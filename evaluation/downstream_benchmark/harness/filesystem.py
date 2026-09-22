"""Binary-safe workspace manifests and protected-item verification."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import tempfile
from typing import Iterable

from .errors import ArtifactCollision, WorkspaceAccessError
from .models import ProtectedItem


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_json(value: object) -> str:
    return sha256_bytes(canonical_json_bytes(value))


@dataclass(frozen=True)
class TreeEntry:
    path: str
    item_type: str
    mode: int
    size: int
    sha256: str
    children_sha256: str | None = None

    def to_dict(self) -> dict[str, object]:
        value: dict[str, object] = {
            "path": self.path,
            "item_type": self.item_type,
            "mode": self.mode,
            "size": self.size,
            "sha256": self.sha256,
        }
        if self.children_sha256 is not None:
            value["children_sha256"] = self.children_sha256
        return value


@dataclass(frozen=True)
class RuntimeProtectedState:
    item: ProtectedItem
    device: int
    inode: int


def _entry_for_path(root: Path, path: Path) -> TreeEntry:
    relative = path.relative_to(root).as_posix()
    info = path.lstat()
    mode = stat.S_IMODE(info.st_mode)
    if stat.S_ISREG(info.st_mode):
        data = path.read_bytes()
        return TreeEntry(relative, "file", mode, len(data), sha256_bytes(data))
    if stat.S_ISDIR(info.st_mode):
        children: list[dict[str, object]] = []
        for directory, dirnames, filenames in os.walk(path, followlinks=False):
            directory_path = Path(directory)
            dirnames.sort()
            filenames.sort()
            for name in dirnames + filenames:
                child = directory_path / name
                child_info = child.lstat()
                child_relative = child.relative_to(path).as_posix()
                child_mode = stat.S_IMODE(child_info.st_mode)
                if stat.S_ISREG(child_info.st_mode):
                    child_data = child.read_bytes()
                    child_identity = {
                        "path": child_relative,
                        "item_type": "file",
                        "mode": child_mode,
                        "size": len(child_data),
                        "sha256": sha256_bytes(child_data),
                    }
                elif stat.S_ISDIR(child_info.st_mode):
                    child_identity = {
                        "path": child_relative,
                        "item_type": "directory",
                        "mode": child_mode,
                        "size": 0,
                    }
                elif stat.S_ISLNK(child_info.st_mode):
                    target = os.readlink(child).encode("utf-8", "surrogateescape")
                    child_identity = {
                        "path": child_relative,
                        "item_type": "symlink",
                        "mode": child_mode,
                        "size": len(target),
                        "sha256": sha256_bytes(target),
                    }
                else:
                    child_identity = {
                        "path": child_relative,
                        "item_type": "other",
                        "mode": child_mode,
                        "size": child_info.st_size,
                    }
                children.append(child_identity)
        children_sha = sha256_json(children)
        identity = sha256_json({"path": relative, "children_sha256": children_sha})
        # Directory allocation size is filesystem-dependent and is not source identity.
        return TreeEntry(relative, "directory", mode, 0, identity, children_sha)
    if stat.S_ISLNK(info.st_mode):
        target = os.readlink(path).encode("utf-8", "surrogateescape")
        return TreeEntry(relative, "symlink", mode, len(target), sha256_bytes(target))
    identity = sha256_json({"path": relative, "mode": info.st_mode, "size": info.st_size})
    return TreeEntry(relative, "other", mode, info.st_size, identity)


def snapshot_tree(root: Path) -> tuple[TreeEntry, ...]:
    root = root.resolve(strict=True)
    entries: list[TreeEntry] = []
    for directory, dirnames, filenames in os.walk(root, followlinks=False):
        directory_path = Path(directory)
        dirnames.sort()
        filenames.sort()
        for name in dirnames + filenames:
            entries.append(_entry_for_path(root, directory_path / name))
    return tuple(sorted(entries, key=lambda entry: entry.path))


def manifest_dict(entries: Iterable[TreeEntry]) -> list[dict[str, object]]:
    return [entry.to_dict() for entry in entries]


def manifest_sha256(entries: Iterable[TreeEntry]) -> str:
    return sha256_json(manifest_dict(entries))


def protected_manifest(root: Path, paths: Iterable[str]) -> tuple[ProtectedItem, ...]:
    root = root.resolve(strict=True)
    result: list[ProtectedItem] = []
    for relative in sorted(set(paths)):
        target = (root / relative).resolve(strict=True)
        if target != root and root not in target.parents:
            raise ValueError(f"protected path leaves workspace: {relative}")
        entry = _entry_for_path(root, target)
        if entry.item_type == "other":
            raise ValueError(f"unsupported protected item type: {relative}")
        result.append(
            ProtectedItem(
                path=entry.path,
                item_type=entry.item_type,
                mode=entry.mode,
                size=entry.size,
                sha256=entry.sha256,
                children_sha256=entry.children_sha256,
            )
        )
    return tuple(result)


def capture_runtime_protected(
    root: Path, expected: Iterable[ProtectedItem]
) -> tuple[RuntimeProtectedState, ...]:
    root = root.resolve(strict=True)
    result: list[RuntimeProtectedState] = []
    for item in expected:
        target = root / item.path
        info = target.lstat()
        result.append(RuntimeProtectedState(item=item, device=info.st_dev, inode=info.st_ino))
    return tuple(result)


def verify_protected(
    root: Path,
    expected: Iterable[ProtectedItem],
    before_runtime: Iterable[RuntimeProtectedState] | None = None,
) -> dict[str, object]:
    root = root.resolve(strict=True)
    before = {state.item.path: state for state in before_runtime or ()}
    issues: list[dict[str, str]] = []
    current_tree = snapshot_tree(root)
    current_by_path = {entry.path: entry for entry in current_tree}
    fingerprints: dict[tuple[str, str], list[str]] = {}
    for entry in current_tree:
        fingerprints.setdefault((entry.item_type, entry.sha256), []).append(entry.path)

    for item in expected:
        entry = current_by_path.get(item.path)
        if entry is None:
            matches = [
                path
                for path in fingerprints.get((item.item_type, item.sha256), [])
                if path != item.path
            ]
            if matches:
                issues.append({"path": item.path, "kind": "rename_or_move", "detail": matches[0]})
            else:
                issues.append({"path": item.path, "kind": "deletion", "detail": "missing"})
            continue
        if entry.item_type != item.item_type:
            issues.append(
                {
                    "path": item.path,
                    "kind": "type_change",
                    "detail": f"{item.item_type}->{entry.item_type}",
                }
            )
        if entry.mode != item.mode:
            issues.append(
                {"path": item.path, "kind": "mode_change", "detail": f"{item.mode}->{entry.mode}"}
            )
        if entry.size != item.size or entry.sha256 != item.sha256:
            issues.append({"path": item.path, "kind": "content_change", "detail": entry.sha256})
        if entry.children_sha256 != item.children_sha256:
            issues.append(
                {
                    "path": item.path,
                    "kind": "child_inventory_change",
                    "detail": entry.children_sha256 or "NA",
                }
            )
        old_runtime = before.get(item.path)
        if old_runtime is not None:
            info = (root / item.path).lstat()
            if info.st_dev != old_runtime.device or info.st_ino != old_runtime.inode:
                issues.append({"path": item.path, "kind": "replacement", "detail": "inode_changed"})
    return {"pass": not issues, "issues": issues}


def diff_manifests(
    before: Iterable[TreeEntry], after: Iterable[TreeEntry]
) -> tuple[dict[str, str], ...]:
    before_map = {entry.path: entry for entry in before}
    after_map = {entry.path: entry for entry in after}
    changes: list[dict[str, str]] = []
    for path in sorted(before_map.keys() | after_map.keys()):
        if path not in before_map:
            changes.append({"path": path, "change": "added"})
        elif path not in after_map:
            changes.append({"path": path, "change": "deleted"})
        elif before_map[path] != after_map[path]:
            changes.append({"path": path, "change": "modified"})
    return tuple(changes)


def copy_fresh_workspace(source_root: Path, destination: Path) -> tuple[TreeEntry, ...]:
    if destination.exists():
        raise ArtifactCollision(f"workspace already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_root, destination, symlinks=True)
    return snapshot_tree(destination)


class WorkspaceView:
    """Ordinary adapter interface constrained to one synthetic workspace.

    This is a harness-level path boundary, not an OS adversarial sandbox.
    """

    def __init__(self, root: Path):
        self.__root = root.resolve(strict=True)

    def _resolve(self, relative_path: str, *, require_exists: bool = False) -> Path:
        if (
            not isinstance(relative_path, str)
            or not relative_path
            or Path(relative_path).is_absolute()
        ):
            raise WorkspaceAccessError("workspace paths must be non-empty and relative")
        candidate = (self.__root / relative_path).resolve(strict=False)
        if candidate != self.__root and self.__root not in candidate.parents:
            raise WorkspaceAccessError("workspace path escape rejected")
        if require_exists and not candidate.exists() and not candidate.is_symlink():
            raise FileNotFoundError(relative_path)
        return candidate

    def read_bytes(self, relative_path: str) -> bytes:
        return self._resolve(relative_path, require_exists=True).read_bytes()

    def write_bytes(self, relative_path: str, data: bytes) -> None:
        target = self._resolve(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    def replace_bytes(self, relative_path: str, data: bytes) -> None:
        target = self._resolve(relative_path, require_exists=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".synthetic-replace-", dir=target.parent
        )
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(data)
            os.chmod(temporary_name, stat.S_IMODE(target.lstat().st_mode))
            os.replace(temporary_name, target)
        finally:
            if os.path.exists(temporary_name):
                os.unlink(temporary_name)

    def delete(self, relative_path: str) -> None:
        target = self._resolve(relative_path, require_exists=True)
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        else:
            target.unlink()

    def rename(self, source: str, destination: str) -> None:
        source_path = self._resolve(source, require_exists=True)
        destination_path = self._resolve(destination)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.rename(destination_path)

    def exists(self, relative_path: str) -> bool:
        return self._resolve(relative_path).exists()

    def list_paths(self) -> tuple[str, ...]:
        return tuple(entry.path for entry in snapshot_tree(self.__root))


def write_new_bytes(path: Path, data: bytes) -> None:
    if path.exists():
        raise ArtifactCollision(f"refusing to overwrite artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_new_json(path: Path, value: object) -> None:
    rendered = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
    write_new_bytes(path, (rendered + "\n").encode("utf-8"))


def artifact_index(root: Path, relative_paths: Iterable[str]) -> dict[str, object]:
    entries: list[dict[str, object]] = []
    for relative in sorted(relative_paths):
        data = (root / relative).read_bytes()
        entries.append({"path": relative, "size": len(data), "sha256": sha256_bytes(data)})
    return {"artifacts": entries}

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SourceContext:
    file: str
    line_start: int
    line_end: int
    focus_line: int
    role: str
    content: str

    def to_dict(self) -> dict[str, object]:
        return {
            "file": self.file,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "focus_line": self.focus_line,
            "role": self.role,
            "content": self.content,
        }


def is_sensitive_path(path: Path) -> bool:
    sensitive_dirs = {".ssh", ".aws", ".gcp"}
    sensitive_files = {"credentials.json", "token.json"}

    for part in path.parts:
        lowered = part.lower()
        if lowered in sensitive_dirs:
            return True
        if "secret" in lowered or "secrets" in lowered:
            return True

    name = path.name.lower()
    return (
        name == ".env"
        or name.startswith(".env.")
        or name.endswith(".pem")
        or name.endswith(".key")
        or name.endswith(".crt")
        or name in sensitive_files
    )


def is_probably_binary(path: Path) -> bool:
    try:
        with path.open("rb") as file:
            return b"\0" in file.read(4096)
    except OSError:
        return True


def is_within_repo(path: Path, repo_root: Path) -> bool:
    resolved_path = path.resolve()
    resolved_root = repo_root.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError:
        return False
    return True


def extract_source_window(
    file_path: str,
    focus_line: int,
    repo_root: Path,
    role: str,
    radius: int = 10,
    max_file_bytes: int = 200_000,
) -> SourceContext | None:
    if focus_line < 1:
        return None

    root = repo_root.resolve()
    candidate = Path(file_path)
    if not candidate.is_absolute():
        candidate = root / candidate

    try:
        resolved = candidate.resolve()
    except OSError:
        return None

    if not is_within_repo(resolved, root):
        return None
    if not resolved.is_file():
        return None
    if is_sensitive_path(resolved):
        return None
    if is_probably_binary(resolved):
        return None

    try:
        if resolved.stat().st_size > max_file_bytes:
            return None
        lines = resolved.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None

    if not lines:
        return None

    line_start = min(len(lines), max(1, focus_line - radius))
    line_end = max(line_start, min(len(lines), focus_line + radius))
    selected = lines[line_start - 1 : line_end]

    return SourceContext(
        file=resolved.relative_to(root).as_posix(),
        line_start=line_start,
        line_end=line_end,
        focus_line=focus_line,
        role=role,
        content="\n".join(selected),
    )


def collect_source_contexts(
    python_traceback: dict[str, object] | None,
    failing_tests: list[dict[str, object]],
    repo_root: Path,
    traceback_radius: int = 10,
    failing_test_radius: int = 20,
) -> list[dict[str, object]]:
    contexts: list[dict[str, object]] = []
    seen: set[tuple[str, int, str]] = set()

    if python_traceback:
        stack_frames = python_traceback.get("stack_frames")
        if isinstance(stack_frames, list):
            for frame in stack_frames:
                if not isinstance(frame, dict):
                    continue
                context = _context_from_entry(
                    frame,
                    repo_root=repo_root,
                    role="traceback_frame",
                    radius=traceback_radius,
                    default_line=None,
                )
                _append_context(contexts, seen, context)

    for failure in failing_tests:
        if not isinstance(failure, dict):
            continue
        context = _context_from_entry(
            failure,
            repo_root=repo_root,
            role="failing_test",
            radius=failing_test_radius,
            default_line=1,
        )
        _append_context(contexts, seen, context)

    return contexts


def _context_from_entry(
    entry: dict[object, object],
    repo_root: Path,
    role: str,
    radius: int,
    default_line: int | None,
) -> SourceContext | None:
    file_path = entry.get("file")
    if not isinstance(file_path, str) or not file_path:
        return None

    raw_line = entry.get("line")
    if isinstance(raw_line, int):
        focus_line = raw_line
    elif default_line is not None:
        focus_line = default_line
    else:
        return None

    return extract_source_window(
        file_path=file_path,
        focus_line=focus_line,
        repo_root=repo_root,
        role=role,
        radius=radius,
    )


def _append_context(
    contexts: list[dict[str, object]],
    seen: set[tuple[str, int, str]],
    context: SourceContext | None,
) -> None:
    if context is None:
        return

    key = (context.file, context.focus_line, context.role)
    if key in seen:
        return

    seen.add(key)
    contexts.append(context.to_dict())

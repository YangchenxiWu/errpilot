"""Block 02 controller V2. Preflight is read-only; dispatch has a separate batch gate."""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import materializer as m
from . import block_03_gitlink_source_export as gitlinks
from .executor import validate_controlling_inputs


BENCHMARK = m.BENCHMARK
REPO = BENCHMARK.parents[1]
WORK = Path("/Users/wuyangchenxi/errpilot-benchmark-work")
PREPARATION = WORK / "expansion_block_02_preparation"
ROOT = WORK / "environment_materialization_expansion_block_02_v2"
BATCH_EXECUTION_TOKEN: str = "BUGSINPY_EXPANSION_BLOCK_02_FIRST_PASS_BATCH_AUTHORIZED_V1"
STATES = {"UNSTARTED", "PREPARED", "DISPATCH_STARTED", "GOVERNED_ATTEMPT_CREATED",
          "CLOSED", "PRE_DISPATCH_REJECTED", "INFRASTRUCTURE_ABORT"}


def _blocked(message: str) -> None:
    raise m.Blocked("BLOCKED_INPUT_IDENTITY", message)


def _run_git(mirror: Path, *args: str) -> bytes:
    result = subprocess.run(["git", "--git-dir", str(mirror), *args],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        _blocked(f"source revision lookup failed: {mirror.name}")
    return result.stdout


def _source_identity(recipe: dict[str, Any], label: str) -> tuple[Path, str]:
    case_id = recipe["canonical_case_id"]
    safe = case_id.replace("::", "__")
    preparation = PREPARATION
    if recipe.get("expansion_block") == 3:
        from .block_03_materializer_bridge import PREPARATION as block_03_preparation

        preparation = block_03_preparation
    identity_path = preparation / safe / "source_identity.json"
    identity = json.loads(identity_path.read_text(encoding="utf-8"))
    mirror = WORK / "subject_repositories" / f"{case_id.split('::')[0]}.git"
    revision = recipe[f"{label.lower()}_source_sha"]
    if (identity.get("canonical_case_id") != case_id
            or identity.get("mirror_path") != str(mirror)
            or identity.get(f"{label.lower()}_commit_full") != revision
            or _run_git(mirror, "cat-file", "-t", revision).strip() != b"commit"):
        _blocked(f"frozen source revision mismatch: {case_id}/{label}")
    return mirror, revision


def source_snapshot_identity(recipe: dict[str, Any], label: str,
                             destination: Path | None = None) -> str:
    """Derive source identity; destination is for separately authorized exports."""
    mirror, revision = _source_identity(recipe, label)
    listing = _run_git(mirror, "ls-tree", "-rz", "--full-tree", revision)
    rows: list[tuple[bytes, bytes, bytes]] = []
    links: list[tuple[bytes, bytes, bytes, bytes]] = []
    forbidden = {os.fsencode(name) for name in m.FORBIDDEN_SNAPSHOT_NAMES}
    for line in listing.split(b"\0"):
        if not line:
            continue
        metadata, path = line.split(b"\t", 1)
        mode, kind, oid = metadata.split(b" ")
        parts = path.split(b"/")
        if any(not part or part in (b".", b"..") or part in forbidden for part in parts):
            _blocked("unsafe tracked source entry")
        path.decode("utf-8", errors="strict")
        if mode == b"160000":
            links.append((path, mode, kind, oid))
            continue
        if kind != b"blob" or mode not in (b"100644", b"100755", b"120000"):
            _blocked("unsafe tracked source entry")
        rows.append((path, mode, oid))
    modules = next((row for row in rows if row[0] == b".gitmodules"), None)
    module_bytes = None
    if links or (recipe.get("expansion_block") == 3
                 and (recipe.get("canonical_case_id"), label) in gitlinks.REVISIONS):
        if modules is not None:
            if modules[1] != b"100644":
                _blocked("gitlink .gitmodules must be a regular non-executable blob")
            module_bytes = _run_git(mirror, "cat-file", "blob", modules[2].decode("ascii"))
    provenance = gitlinks.derive(recipe, label, revision, links, module_bytes)
    if provenance is not None:
        leaf_paths = [path for path, _, _ in rows] + [path for path, _, _, _ in links]
        unique_paths = set(leaf_paths)
        if len(unique_paths) != len(leaf_paths) or any(
                b"/".join(path.split(b"/")[:i]) in unique_paths
                for path in leaf_paths for i in range(1, len(path.split(b"/")))):
            _blocked("ambiguous gitlink source paths or ancestor substitution")
    if not rows:
        _blocked("empty source revision")
    rows.sort(key=lambda row: row[0])
    entries: list[dict[str, Any]] = []
    if destination is not None:
        sidecar = gitlinks.sidecar_path(destination)
        if sidecar.exists() or sidecar.is_symlink():
            _blocked("source provenance sidecar already exists")
        destination.mkdir(parents=True, exist_ok=False)
    process = subprocess.Popen(["git", "--git-dir", str(mirror), "cat-file", "--batch"],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL)
    try:
        assert process.stdin is not None and process.stdout is not None
        for path, mode, oid in rows:
            process.stdin.write(oid + b"\n")
            process.stdin.flush()
            header = process.stdout.readline().split()
            if len(header) != 3 or header[0] != oid or header[1] != b"blob":
                _blocked("source blob identity mismatch")
            content = process.stdout.read(int(header[2]))
            if len(content) != int(header[2]) or process.stdout.read(1) != b"\n":
                _blocked("source blob truncated")
            parent = tuple(path.split(b"/")[:-1])
            name = path.decode("utf-8")
            if mode == b"120000":
                m._safe_link_target(parent, content)
                entries.append({"path": name, "entry_type": "symlink",
                                "target_b64": base64.b64encode(content).decode("ascii"),
                                "target_sha256": m.sha256(content)})
            else:
                entries.append({"path": name, "entry_type": "file",
                                "content_sha256": m.sha256(content),
                                "mode": 0o755 if mode == b"100755" else 0o644})
            if destination is not None:
                target = destination / name
                target.parent.mkdir(parents=True, exist_ok=True)
                if mode == b"120000":
                    os.symlink(content, os.fsencode(target))
                else:
                    with target.open("xb") as stream:
                        stream.write(content)
                    target.chmod(0o755 if mode == b"100755" else 0o644)
    finally:
        if process.stdin is not None:
            process.stdin.close()
        if process.stdout is not None:
            process.stdout.close()
        process.wait()
    if process.returncode:
        _blocked("source blob stream failed")
    manifest = {"schema": "SOURCE_SNAPSHOT_MANIFEST_V2", "entries": entries}
    if provenance is not None:
        manifest["gitlink_provenance"] = provenance
        if destination is not None:
            (destination / gitlinks.PATH).mkdir(parents=True, exist_ok=False)
            with gitlinks.sidecar_path(destination).open("xb") as stream:
                stream.write(m.canonical_json(provenance))
    digest = m.sha256(m.canonical_json(manifest))
    if destination is not None and m.snapshot_manifest(destination)[1] != digest:
        _blocked("staged source snapshot identity mismatch")
    return digest


def _inputs(recipe: dict[str, Any]) -> tuple[dict[str, bytes | None], dict[str, str]]:
    case_id = recipe["canonical_case_id"]
    safe = case_id.replace("::", "__")
    folder = Path("derived_inputs") / "expansion_block_02" / safe
    paths = {
        "raw_requirements": (PREPARATION / safe / "inputs/requirements.raw", Path("raw") / safe / "requirements.raw", "requirements_raw_sha256"),
        "normalized_requirements": (BENCHMARK / folder / "requirements.normalized.txt", folder / "requirements.normalized.txt", "requirements_normalized_sha256"),
        "dependency_input": (BENCHMARK / folder / "requirements.dependencies.txt", folder / "requirements.dependencies.txt", "dependency_input_sha256"),
        "setup_input": (PREPARATION / safe / "inputs/setup.raw", Path("raw") / safe / "setup.raw", "setup_sha256"),
    }
    content: dict[str, bytes | None] = {}
    relative: dict[str, str] = {}
    for field, (source, target, hash_field) in paths.items():
        expected = recipe[hash_field]
        if expected == "ABSENT":
            if source.exists() or source.is_symlink():
                _blocked(f"unexpected input: {field}/{case_id}")
            content[field] = None
        else:
            if not source.is_file() or source.is_symlink():
                _blocked(f"missing input: {field}/{case_id}")
            data = source.read_bytes()
            if m.sha256(data) != expected:
                _blocked(f"frozen input mismatch: {field}/{case_id}")
            content[field] = data
            relative[field] = target.as_posix()
    return content, relative


def derive_requests() -> list[dict[str, Any]]:
    """Phase A: derive and validate all identities with no production writes."""
    if (m.EXPANSION_02_AUTHORITY_TOKEN !=
            "BUGSINPY_EXPANSION_BLOCK_02_MATERIALIZATION_AUTHORIZED_V1"
            or m.EXPANSION_02_AUTHORITY_TOKEN == m.EXPANSION_01_AUTHORITY_TOKEN
            or ROOT != WORK / "environment_materialization_expansion_block_02_v2"):
        _blocked("Block 02 authority or future root namespace mismatch")
    if ROOT.exists() or ROOT.is_symlink():
        _blocked("future V2 production root must be absent")
    validate_controlling_inputs(BENCHMARK)
    if (len(m.read_rows(BENCHMARK / "exclusions.csv")) != 29
            or m.read_rows(BENCHMARK / "cases_manifest.csv")):
        _blocked("V3 exclusions or header-only manifest mismatch")
    recipes = m.check_expansion_block_02_ledger()
    if len(recipes) != 8:
        _blocked("eight Block 02 recipes required")
    self_rows = m.read_rows(BENCHMARK / "expansion_block_02_self_reference_ledger.csv")
    requests: list[dict[str, Any]] = []
    for recipe in recipes:
        case_id = recipe["canonical_case_id"]
        order = recipe["expansion_order"]
        if recipe["expansion_block"] != 2 or not 1 <= order <= 10:
            _blocked("Block 02 recipe namespace/order mismatch")
        mode = recipe["environment_mode_v2"]
        if mode == "SOURCE_INDEPENDENT_ENVIRONMENT":
            labels = ("SOURCE_INDEPENDENT",)
        elif mode == "REVISION_SPECIFIC_BUILD_REQUIRED":
            labels = ("BUGGY", "FIXED")
        else:
            _blocked("unsupported Block 02 mode")
        data, paths = _inputs(recipe)
        ledger = [{k: v for k, v in row.items() if k not in ("expansion_block", "expansion_order")}
                  for row in self_rows if row["canonical_case_id"] == case_id]
        m.verify_inputs(recipe, data["raw_requirements"], data["normalized_requirements"],
                        data["dependency_input"], ledger, data["setup_input"])
        for label in labels:
            if label == "SOURCE_INDEPENDENT":
                revision = {"label": label, "sha": "ABSENT"}
            else:
                revision = {
                    "label": label,
                    "sha": source_snapshot_identity(recipe, label),
                    "source": f"snapshots/{case_id.replace('::', '__')}/{label.lower()}",
                    "source_revision_sha": recipe[f"{label.lower()}_source_sha"],
                }
            request = {
                "canonical_case_id": case_id,
                "expansion_block": recipe["expansion_block"],
                "expansion_order": order,
                "block_identity_sha256": recipe["block_identity_sha256"],
                "build_recipe_sha256": m.recipe_hash(recipe),
                "self_reference_ledger": ledger,
                "revision_label": label,
                "revisions": [revision],
                "network_build": bool(data["dependency_input"] and data["dependency_input"].strip())
                or any(action["requires_network"] for action in recipe["setup_actions"]),
                **paths,
            }
            m.validate_expansion_block_02_request(request)
            requests.append(request)
    if (len(requests) != 12 or len({(r["canonical_case_id"], r["revision_label"])
                                    for r in requests}) != 12):
        _blocked("exactly twelve unique Block 02 identities required")
    return requests


def _stamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic(path: Path, content: bytes) -> None:
    temporary = path.with_name(path.name + ".new")
    with temporary.open("xb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def _json(path: Path, value: Any) -> None:
    _atomic(path, m.canonical_json(value) + b"\n")


def _ledger_entry(request: dict[str, Any]) -> dict[str, Any]:
    return {"key": f'{request["expansion_order"]:02d}_{request["canonical_case_id"].replace("::", "__")}_{request["revision_label"].lower()}',
            "case_id": request["canonical_case_id"], "revision_label": request["revision_label"],
            "request_sha256": m.sha256(m.canonical_json(request) + b"\n"),
            "state": "UNSTARTED", "governed_attempt_consumed": False}


def _save_ledger(ledger: list[dict[str, Any]]) -> None:
    _json(ROOT / "identity_ledger.json", ledger)


def _stage_inputs(requests: list[dict[str, Any]]) -> None:
    recipes = {r["canonical_case_id"]: r for r in m.check_expansion_block_02_ledger()}
    for request in requests:
        recipe = recipes[request["canonical_case_id"]]
        data, paths = _inputs(recipe)
        for field, relative in paths.items():
            target = ROOT / "inputs" / relative
            if target.exists():
                if target.read_bytes() != data[field]:
                    _blocked("staged input changed")
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            _atomic(target, data[field] or b"")
        revision = request["revisions"][0]
        if revision["label"] != "SOURCE_INDEPENDENT":
            target = ROOT / "inputs" / revision["source"]
            if target.exists():
                if m.snapshot_manifest(target)[1] != revision["sha"]:
                    _blocked("staged snapshot changed")
            elif source_snapshot_identity(recipe, revision["label"], target) != revision["sha"]:
                _blocked("staged snapshot changed")


def _dispatch_one(entry: dict[str, Any], request: dict[str, Any],
                  ledger: list[dict[str, Any]]) -> bool:
    if entry["state"] != "UNSTARTED":
        _blocked("identity is not unstarted; Human-PI adjudication required")
    key = entry["key"]
    request_path = ROOT / "requests" / f"{key}.json"
    _json(request_path, request)
    entry["state"] = "PREPARED"
    entry["prepared_at"] = _stamp()
    _save_ledger(ledger)
    entry["state"] = "DISPATCH_STARTED"
    entry["dispatch_at"] = _stamp()
    _save_ledger(ledger)
    command = [sys.executable, "-m", "evaluation.downstream_benchmark.screening.materializer",
               "materialize-expansion-02", "--authority-token", m.EXPANSION_02_AUTHORITY_TOKEN,
               "--request", str(request_path), "--input-root", str(ROOT / "inputs"),
               "--output", str(ROOT / "attempts" / key)]
    try:
        process = subprocess.run(command, cwd=REPO, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, check=False)
    except OSError as exc:
        entry["state"] = "INFRASTRUCTURE_ABORT"
        entry["reason"] = f"subprocess launch: {type(exc).__name__}"
        _save_ledger(ledger)
        return False
    streams = ROOT / "controller_streams"
    _atomic(streams / f"{key}.stdout.raw", process.stdout)
    _atomic(streams / f"{key}.stderr.raw", process.stderr)
    entry["return_code"] = process.returncode
    entry["stdout_sha256"] = m.sha256(process.stdout)
    entry["stderr_sha256"] = m.sha256(process.stderr)
    _save_ledger(ledger)
    attempt = ROOT / "attempts" / key / "attempt.json"
    if not attempt.is_file():
        entry["state"] = ("PRE_DISPATCH_REJECTED" if not attempt.parent.exists()
                          and process.stderr.startswith(b"BLOCKED_INPUT_IDENTITY:")
                          else "INFRASTRUCTURE_ABORT")
        entry["reason"] = "canonical governed attempt evidence absent"
        _save_ledger(ledger)
        return False
    result = json.loads(attempt.read_text(encoding="utf-8"))
    if result.get("attempt_id") != key or result.get("synthetic_only") is not False:
        entry["state"] = "INFRASTRUCTURE_ABORT"
        entry["reason"] = "canonical attempt identity mismatch"
        _save_ledger(ledger)
        return False
    entry["state"] = "GOVERNED_ATTEMPT_CREATED"
    entry["governed_attempt_consumed"] = True
    entry["attempt_json_sha256"] = m.sha256(attempt.read_bytes())
    _save_ledger(ledger)
    if result.get("status") not in ("MATERIALIZED", "BUILD_FAILED"):
        return False
    entry["state"] = "CLOSED"
    entry["outcome"] = result["status"]
    entry["closed_at"] = _stamp()
    _save_ledger(ledger)
    return True


def dispatch(batch_token: str) -> None:
    """Phase B requires the exact batch token before any production write."""
    if batch_token != BATCH_EXECUTION_TOKEN:
        raise m.Blocked("BLOCKED_AUTHORITY", "invalid Block 02 batch token")
    if not m.REAL_MATERIALIZATION_ENABLED or not m.materializer_git_clean():
        raise m.Blocked("BLOCKED_AUTHORITY", "clean committed materializer required")
    requests = derive_requests()
    ROOT.mkdir(mode=0o700, exist_ok=False)
    for name in ("inputs", "requests", "attempts", "controller_streams"):
        (ROOT / name).mkdir()
    ledger = [_ledger_entry(request) for request in requests]
    _save_ledger(ledger)
    _stage_inputs(requests)
    for entry, request in zip(ledger, requests):
        if not _dispatch_one(entry, request, ledger):
            raise m.Blocked("BLOCKED_INPUT_IDENTITY", "batch stopped for Human-PI adjudication")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("preflight", "dispatch"))
    parser.add_argument("--batch-token")
    args = parser.parse_args(argv)
    try:
        if args.phase == "preflight":
            if args.batch_token is not None:
                raise m.Blocked("BLOCKED_AUTHORITY", "preflight accepts no batch token")
            requests = derive_requests()
            for request in requests:
                print(f'{request["expansion_order"]:02d} {request["canonical_case_id"]} '
                      f'{request["revision_label"]}: PREFLIGHT_PASS')
            print("12/12 Block 02 requests valid; zero production attempts")
        else:
            dispatch(args.batch_token or "")
    except (m.Blocked, OSError, ValueError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

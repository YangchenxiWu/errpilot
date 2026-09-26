"""Fail-closed Docker environment materializer with a gated production path.

The shared build engine is exercised only with checked synthetic fixtures in v1.
No import, bare invocation, validate, or plan operation starts Docker builds.
"""

from __future__ import annotations

import argparse
import base64
import csv
import json
import os
import re
import shlex
import shutil
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if __package__:
    from .build_recipes import FROZEN_SHA256, canonical_json, recipe_hash, sha256
    from .executor import ENVIRONMENT_IDENTITY_V1_FIELDS
else:  # Permit the requested bare script invocation as well as python -m.
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from evaluation.downstream_benchmark.screening.build_recipes import (
        FROZEN_SHA256, canonical_json, recipe_hash, sha256,
    )
    from evaluation.downstream_benchmark.screening.executor import ENVIRONMENT_IDENTITY_V1_FIELDS


BENCHMARK = Path(__file__).resolve().parents[1]
FIXTURES = BENCHMARK / "fixtures" / "environment_materializer"
PLATFORM = "linux/amd64"
AUTHORITY_TOKEN = "BUGSINPY_ENVIRONMENT_MATERIALIZATION_AUTHORIZED_V1"
EXPANSION_01_AUTHORITY_TOKEN = "BUGSINPY_EXPANSION_BLOCK_01_MATERIALIZATION_AUTHORIZED_V1"
EXPANSION_01_BLOCK_SHA256 = "8a478d475066ab94afccf80472aa031e141ec8639296487fdd7fa572308ae02c"
EXPANSION_01_RECIPE_SCHEMA = "EXPANSION_BLOCK_01_ENVIRONMENT_BUILD_RECIPE_V1"
EXPANSION_01_FROZEN_SHA256 = {
    "EXPANSION_BLOCK_01.md": "d5ac07dd4d9d2df01af25fa14b4673de6a27ea1f3bee9116f4b5bceca6c234fa",
    "expansion_block_01.csv": "89bd95f71c230dcde90cdb422ea31218bd11e840aebe60641267e36b163f4186",
    "expansion_block_01_environment_build_recipes.csv": "8a9efeb613f6f175322a6c52b899efc30ddb8654b0856e5145ec92c018fc1bf1",
    "expansion_block_01_execution_plan.csv": "6ad8345cc290cfae6b903d9a731f9929722ebf0a7c9a44582b2c70d0501a6359",
    "expansion_block_01_requirements_normalization.csv": "48b90843dbfacabada4804a0dc50aa2a912a8c60a8566653c150c7697fa7e045",
    "expansion_block_01_self_reference_ledger.csv": "42dfe957ca9979586587233cd3395e4a0d87f0c94b3c1fb13e4a2e5fee74986f",
}
REAL_MATERIALIZATION_ENABLED = True  # Each real batch still needs separate Human-PI authority.
MATERIALIZER_VERSION = "ENVIRONMENT_MATERIALIZER_V1_5"
DISTRIBUTION_PROBE_VERSION = "INSTALLED_DISTRIBUTION_MANIFEST_V2"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")
SAFE_NAME = re.compile(r"[A-Za-z0-9_.-]+\Z")
FORBIDDEN_SNAPSHOT_NAMES = {".git", "bug_patch.txt", "screening_evidence", "bug.info", "project.info"}


class Blocked(ValueError):
    def __init__(self, status: str, message: str) -> None:
        super().__init__(message)
        self.status = status


class ProbeBlocked(Blocked):
    def __init__(self, message: str, *, backend: str, command: list[str],
                 stdout: bytes, stderr: bytes, exit_code: int | None) -> None:
        super().__init__("BLOCKED_RUNTIME_IDENTITY", message)
        self.backend = backend
        self.command = command
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def materializer_commit() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=BENCHMARK,
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    return result.stdout.decode("ascii").strip() if result.returncode == 0 else "UNAVAILABLE"


def materializer_git_clean() -> bool:
    result = subprocess.run(["git", "status", "--porcelain=v1"], cwd=BENCHMARK,
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    return result.returncode == 0 and not result.stdout


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def check_frozen_ledger(benchmark: Path = BENCHMARK) -> list[dict[str, Any]]:
    """Read-only authority check; never opens subject source or executes a recipe."""
    for name, expected in FROZEN_SHA256.items():
        if sha256((benchmark / name).read_bytes()) != expected:
            raise Blocked("BLOCKED_INPUT_IDENTITY", f"frozen authority changed: {name}")
    rows = read_rows(benchmark / "environment_build_recipes.csv")
    candidates = [r for r in read_rows(benchmark / "candidate_universe.csv")
                  if r["selected_initial_40"] == "true"]
    plans = read_rows(benchmark / "screening_execution_plan.csv")
    def keys(seq: list[dict[str, str]]) -> list[tuple[str, str]]:
        return [(r["initial_selection_order"], r["canonical_case_id"]) for r in seq]
    if len(rows) != 40 or keys(rows) != keys(candidates) or keys(rows) != keys(plans):
        raise Blocked("BLOCKED_INPUT_IDENTITY", "frozen initial-40 order changed")
    modes: list[str] = []
    recipes: list[dict[str, Any]] = []
    for row in rows:
        recipe = json.loads(row["build_recipe_json"])
        if (row["build_recipe_status"] != "BUILD_RECIPE_READY"
                or recipe_hash(recipe) != row["build_recipe_sha256"]
                or recipe["materialization_identity"] != "UNBUILT"
                or recipe["canonical_case_id"] != row["canonical_case_id"]
                or recipe["runtime_platform"] != PLATFORM
                or recipe["future_network_execution_policy"] != "NONE"):
            raise Blocked("BLOCKED_INPUT_IDENTITY", "recipe identity/status mismatch")
        modes.append(recipe["environment_mode_v2"])
        recipes.append(recipe)
    if modes.count("SOURCE_INDEPENDENT_ENVIRONMENT") != 26 or modes.count(
            "REVISION_SPECIFIC_BUILD_REQUIRED") != 14:
        raise Blocked("BLOCKED_INPUT_IDENTITY", "frozen environment modes changed")
    return recipes


def _check_expansion_block_01_ledger(benchmark: Path) -> list[dict[str, Any]]:
    """Validate only Block 01's frozen ledgers and repository derived inputs."""
    for name, expected in EXPANSION_01_FROZEN_SHA256.items():
        if sha256((benchmark / name).read_bytes()) != expected:
            raise Blocked("BLOCKED_INPUT_IDENTITY", f"frozen Block 01 authority changed: {name}")
    for name, expected in FROZEN_SHA256.items():
        if sha256((benchmark / name).read_bytes()) != expected:
            raise Blocked("BLOCKED_INPUT_IDENTITY", f"frozen authority changed: {name}")
    block = read_rows(benchmark / "expansion_block_01.csv")
    rows = read_rows(benchmark / "expansion_block_01_environment_build_recipes.csv")
    plans = read_rows(benchmark / "expansion_block_01_execution_plan.csv")
    normalizations = read_rows(benchmark / "expansion_block_01_requirements_normalization.csv")
    self_rows = read_rows(benchmark / "expansion_block_01_self_reference_ledger.csv")
    if any(len(items) != 10 for items in (block, rows, plans, normalizations)):
        raise Blocked("BLOCKED_INPUT_IDENTITY", "Block 01 requires exactly ten ordered rows")
    for items in (block, rows, plans, normalizations):
        if [r.get("expansion_order") for r in items] != [str(i) for i in range(1, 11)]:
            raise Blocked("BLOCKED_INPUT_IDENTITY", "Block 01 order must be 1..10")
        if any(r.get("expansion_block") != "1" for r in items):
            raise Blocked("BLOCKED_INPUT_IDENTITY", "Block 01 ledger namespace mismatch")
    text = (benchmark / "EXPANSION_BLOCK_01.md").read_text(encoding="utf-8")
    match = re.search(r"```json\n(.*?)\n```", text, flags=re.DOTALL)
    if match is None:
        raise Blocked("BLOCKED_INPUT_IDENTITY", "Block 01 identity missing")
    try:
        identity = json.loads(match.group(1))
        canonical = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    except (ValueError, TypeError) as exc:
        raise Blocked("BLOCKED_INPUT_IDENTITY", "Block 01 identity invalid") from exc
    if (sha256(canonical) != EXPANSION_01_BLOCK_SHA256
            or identity.get("ordered_10_case_ids") != [r.get("canonical_case_id") for r in block]
            or identity.get("ordered_10_candidate_ranks") != [int(r["candidate_rank"]) for r in block]
            or identity.get("ordered_10_rank_sha256") != [r.get("rank_sha256") for r in block]
            or identity.get("candidate_universe_sha256") != FROZEN_SHA256["candidate_universe.csv"]):
        raise Blocked("BLOCKED_INPUT_IDENTITY", "Block 01 identity mismatch")
    recipes: list[dict[str, Any]] = []
    for order, (member, row, plan, norm) in enumerate(zip(block, rows, plans, normalizations), 1):
        case_id = member["canonical_case_id"]
        if any(item.get("canonical_case_id") != case_id for item in (row, plan, norm)):
            raise Blocked("BLOCKED_INPUT_IDENTITY", "Block 01 membership mismatch")
        try:
            recipe = json.loads(row["build_recipe_json"])
        except (ValueError, TypeError) as exc:
            raise Blocked("BLOCKED_INPUT_IDENTITY", "Block 01 recipe JSON invalid") from exc
        if (recipe.get("recipe_schema_version") != EXPANSION_01_RECIPE_SCHEMA
                or recipe.get("expansion_block") != 1
                or recipe.get("expansion_order") != order
                or recipe.get("canonical_case_id") != case_id
                or recipe.get("block_identity_sha256") != EXPANSION_01_BLOCK_SHA256
                or row.get("build_recipe_status") != "BUILD_RECIPE_READY"
                or recipe_hash(recipe) != row.get("build_recipe_sha256")
                or recipe.get("materialization_identity") != "UNBUILT"
                or recipe.get("runtime_platform") != PLATFORM
                or recipe.get("future_network_execution_policy") != "NONE"
                or recipe.get("execution_plan_sha256") != plan.get("execution_plan_sha256")
                or recipe.get("protected_manifest_sha256") != plan.get("protected_manifest_sha256")
                or not HEX64.fullmatch(plan.get("protected_manifest_sha256", ""))
                or plan.get("protected_manifest_status") != "RESOLVED"
                or plan.get("preparation_status") != "EXPANSION_PREPARATION_READY"):
            raise Blocked("BLOCKED_INPUT_IDENTITY", f"Block 01 recipe/plan mismatch: {case_id}")
        case_ledger = [
            {k: v for k, v in item.items() if k not in ("expansion_block", "expansion_order")}
            for item in self_rows if item.get("canonical_case_id") == case_id
        ]
        if (any(item.get("expansion_block") != "1" or item.get("expansion_order") != str(order)
                for item in self_rows if item.get("canonical_case_id") == case_id)
                or len(case_ledger) != int(row["self_reference_count"])
                or sha256(canonical_json(case_ledger)) != recipe.get("self_reference_ledger_sha256")):
            raise Blocked("BLOCKED_INPUT_IDENTITY", f"Block 01 self-reference mismatch: {case_id}")
        expected_dir = Path("derived_inputs") / "expansion_block_01" / case_id.replace("::", "__")
        for field, path_field, filename in (
            ("requirements_normalized_sha256", "normalized_path", "requirements.normalized.txt"),
            ("dependency_input_sha256", "dependency_input_path", "requirements.dependencies.txt"),
        ):
            expected = expected_dir / filename
            if norm.get(path_field) != expected.as_posix() or sha256(
                    (benchmark / expected).read_bytes()) != recipe.get(field) or norm.get(field) != recipe.get(field):
                raise Blocked("BLOCKED_INPUT_IDENTITY", f"Block 01 derived input mismatch: {case_id}")
        recipes.append(recipe)
    if any(item.get("canonical_case_id") not in {r["canonical_case_id"] for r in block}
           for item in self_rows):
        raise Blocked("BLOCKED_INPUT_IDENTITY", "Block 01 self-reference has unknown case")
    if any(r["environment_mode_v2"] not in (
            "SOURCE_INDEPENDENT_ENVIRONMENT", "REVISION_SPECIFIC_BUILD_REQUIRED")
            for r in recipes):
        raise Blocked("BLOCKED_INPUT_IDENTITY", "Block 01 environment mode invalid")
    return recipes


def check_expansion_block_01_ledger(benchmark: Path = BENCHMARK) -> list[dict[str, Any]]:
    """Fail closed on malformed Block 01 authority without reaching a build."""
    try:
        return _check_expansion_block_01_ledger(benchmark)
    except Blocked:
        raise
    except (OSError, KeyError, TypeError, ValueError) as exc:
        raise Blocked("BLOCKED_INPUT_IDENTITY", "malformed Block 01 ledger") from exc


def verify_inputs(recipe: dict[str, Any], raw: bytes | None, normalized: bytes | None,
                  dependency: bytes | None, ledger: list[dict[str, str]],
                  setup: bytes | None) -> None:
    """Compare the supplied frozen bytes; never recompute normalization policy."""
    identities = (
        ("requirements_raw_sha256", raw),
        ("requirements_normalized_sha256", normalized),
        ("dependency_input_sha256", dependency),
        ("setup_sha256", setup),
    )
    for field, value in identities:
        actual = sha256(value) if value is not None else "ABSENT"
        if actual != recipe[field]:
            raise Blocked("BLOCKED_INPUT_IDENTITY", f"{field} mismatch")
    if sha256(canonical_json(ledger)) != recipe["self_reference_ledger_sha256"]:
        raise Blocked("BLOCKED_INPUT_IDENTITY", "self-reference ledger mismatch")
    if sha256(canonical_json(recipe["setup_actions"])) != recipe["setup_action_ledger_sha256"]:
        raise Blocked("BLOCKED_INPUT_IDENTITY", "setup-action ledger mismatch")
    if setup is None:
        actual_actions: list[tuple[int, str]] = []
    else:
        try:
            lines = setup.decode("utf-8", errors="strict").splitlines()
        except UnicodeError as exc:
            raise Blocked("BLOCKED_INPUT_IDENTITY", "setup UTF-8 decode failed") from exc
        actual_actions = [(ordinal, line) for ordinal, line in enumerate(lines, 1)
                          if line.strip() and not line.lstrip().startswith("#")]
    declared_actions = [(a["source_line_ordinal"], a["exact_source_text"])
                        for a in recipe["setup_actions"]]
    if actual_actions != declared_actions:
        raise Blocked("BLOCKED_INPUT_IDENTITY", "ordered setup text/ordinal mismatch")
    if recipe_hash(recipe) != recipe.get("build_recipe_sha256", recipe_hash(recipe)):
        raise Blocked("BLOCKED_INPUT_IDENTITY", "recipe hash mismatch")


def _safe_link_target(parent: tuple[bytes, ...], target: bytes) -> None:
    """Check raw POSIX link bytes lexically; no target lookup or dereference."""
    if not target or b"\0" in target:
        raise Blocked("BLOCKED_UNSAFE_SYMLINK", "empty or malformed symlink target")
    if target.startswith(b"/"):
        raise Blocked("BLOCKED_UNSAFE_SYMLINK", "absolute symlink target")
    parts = list(parent)
    forbidden = {os.fsencode(name) for name in FORBIDDEN_SNAPSHOT_NAMES}
    for component in target.split(b"/"):
        if component in forbidden:
            raise Blocked("BLOCKED_UNSAFE_SYMLINK", "symlink targets forbidden metadata")
        if component in (b"", b"."):
            continue
        if component == b"..":
            if not parts:
                raise Blocked("BLOCKED_UNSAFE_SYMLINK", "symlink escapes snapshot root")
            parts.pop()
        else:
            parts.append(component)
    if any(component in forbidden for component in parts):
        raise Blocked("BLOCKED_UNSAFE_SYMLINK", "symlink resolves to forbidden metadata")


def _manifest_entries(root: Path) -> list[dict[str, Any]]:
    """Traverse directory descriptors, never following a symlink directory."""
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    try:
        root_fd = os.open(root, flags)
    except OSError as exc:
        raise Blocked("BLOCKED_INPUT_IDENTITY", "explicit non-symlink directory required") from exc
    entries: list[dict[str, Any]] = []
    forbidden = {os.fsencode(name) for name in FORBIDDEN_SNAPSHOT_NAMES}

    def visit(directory_fd: int, parent: tuple[bytes, ...]) -> None:
        with os.scandir(directory_fd) as scan:
            names = sorted(os.fsencode(item.name) for item in scan)
        for name in names:
            relative = (*parent, name)
            if name in forbidden:
                raise Blocked("BLOCKED_INPUT_IDENTITY", "snapshot includes forbidden metadata/history")
            try:
                path = b"/".join(relative).decode("utf-8", errors="strict")
            except UnicodeDecodeError as exc:
                raise Blocked("BLOCKED_INPUT_IDENTITY", "snapshot path is not UTF-8") from exc
            info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            if stat.S_ISLNK(info.st_mode):
                target = os.readlink(name, dir_fd=directory_fd)
                if not isinstance(target, bytes):
                    target = os.fsencode(target)
                _safe_link_target(parent, target)
                entries.append({"path": path, "entry_type": "symlink",
                                "target_b64": base64.b64encode(target).decode("ascii"),
                                "target_sha256": sha256(target)})
            elif stat.S_ISREG(info.st_mode):
                fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory_fd)
                with os.fdopen(fd, "rb") as stream:
                    if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                        raise Blocked("BLOCKED_INPUT_IDENTITY", "snapshot file type changed")
                    content = stream.read()
                entries.append({"path": path, "entry_type": "file",
                                "content_sha256": sha256(content), "mode": info.st_mode & 0o777})
            elif stat.S_ISDIR(info.st_mode):
                child_fd = os.open(name, flags, dir_fd=directory_fd)
                try:
                    visit(child_fd, relative)
                finally:
                    os.close(child_fd)
            else:
                raise Blocked("BLOCKED_INPUT_IDENTITY", "snapshot special file refused")

    try:
        visit(root_fd, ())
    finally:
        os.close(root_fd)
    entries.sort(key=lambda entry: entry["path"])
    return entries


def snapshot_manifest(source: Path) -> tuple[dict[str, Any], str]:
    manifest = {"schema": "SOURCE_SNAPSHOT_MANIFEST_V2", "entries": _manifest_entries(source)}
    return manifest, sha256(canonical_json(manifest))


def context_manifest(context: Path) -> tuple[dict[str, Any], str]:
    manifest = {"schema": "BUILD_CONTEXT_MANIFEST_V2", "entries": _manifest_entries(context)}
    return manifest, sha256(canonical_json(manifest))


def action_argv(action: dict[str, Any], *, source_present: bool) -> list[str]:
    text = action.get("exact_source_text", "")
    if re.search(r"[;&|<>`$\\\n\r]", text):
        raise Blocked("BLOCKED_UNSUPPORTED_ACTION", "shell control/metacharacter refused")
    try:
        args = shlex.split(text)
    except ValueError as exc:
        raise Blocked("BLOCKED_UNSUPPORTED_ACTION", str(exc)) from exc
    if not args:
        raise Blocked("BLOCKED_UNSUPPORTED_ACTION", "empty setup action")
    kind = action.get("classification")
    if args[0] in {"pip", "pip3"} and len(args) >= 3 and args[1] == "install":
        command = ["python", "-m", "pip", "install", *args[2:]]
    elif args[:4] == ["python", "-m", "pip", "install"] and len(args) >= 5:
        command = args
    elif kind == "PROJECT_INSTALL_OR_BUILD" and args[:2] == ["python", "setup.py"]:
        command = args
    elif kind == "FILESYSTEM_PREPARATION" and args[0] == "touch" and len(args) == 2:
        target = args[1]
        if target.startswith("/") and target != "/synthetic-marker":
            raise Blocked("BLOCKED_UNSUPPORTED_ACTION", "absolute touch path refused")
        if ".." in Path(target).parts:
            raise Blocked("BLOCKED_UNSUPPORTED_ACTION", "escaping touch path refused")
        command = args
    else:
        raise Blocked("BLOCKED_UNSUPPORTED_ACTION", "setup action is not in argv allowlist")
    if kind == "DEPENDENCY_INSTALL":
        if command[:4] != ["python", "-m", "pip", "install"]:
            raise Blocked("BLOCKED_UNSUPPORTED_ACTION", "dependency action mismatch")
        if command[4:] == ["-r", "requirements.txt"]:
            if action.get("dependency_input_binding") != "DERIVED_DEPENDENCY_ONLY":
                raise Blocked("BLOCKED_UNSUPPORTED_ACTION", "raw requirements install refused")
            command = ["python", "-m", "pip", "install", "-r", "/__materializer/dependencies.txt"]
        elif any(x == "-r" or x.startswith("-r") or "git+" in x for x in command[4:]):
            raise Blocked("BLOCKED_UNSUPPORTED_ACTION", "unbound requirement/VCS install refused")
        if "." in command[4:] or any(x.startswith(".[") for x in command[4:]):
            if not source_present or not action.get("consumes_subject_source"):
                raise Blocked("BLOCKED_UNSUPPORTED_ACTION", "source install missing source identity")
    elif kind == "PROJECT_INSTALL_OR_BUILD":
        if not source_present or not action.get("consumes_subject_source"):
            raise Blocked("BLOCKED_UNSUPPORTED_ACTION", "project build needs source snapshot")
    elif kind == "FILESYSTEM_PREPARATION":
        if not source_present and command[1] != "/synthetic-marker":
            raise Blocked("BLOCKED_UNSUPPORTED_ACTION", "source file operation without source")
    else:
        raise Blocked("BLOCKED_UNSUPPORTED_ACTION", "unsupported action category")
    return command


def build_definition(recipe: dict[str, Any], *, source_present: bool,
                     dependency_present: bool) -> bytes:
    base = recipe["base_image_reference"]
    if not base.endswith(recipe["base_image_digest"]) or not DIGEST.fullmatch(
            recipe["base_image_digest"]):
        raise Blocked("BLOCKED_RUNTIME_IDENTITY", "immutable base digest mismatch")
    lines = [f"FROM --platform={PLATFORM} {base}", "ENV PYTHONDONTWRITEBYTECODE=1",
             "ENV PIP_DISABLE_PIP_VERSION_CHECK=1"]
    if dependency_present:
        lines += ["COPY dependencies.txt /__materializer/dependencies.txt",
                  'RUN ["python","-m","pip","install","-r","/__materializer/dependencies.txt"]']
    if source_present:
        lines += ["COPY source/ /subject/", "WORKDIR /subject"]
    for action in recipe["setup_actions"]:
        argv = action_argv(action, source_present=source_present)
        lines.append("RUN " + json.dumps(argv, separators=(",", ":")))
    return ("\n".join(lines) + "\n").encode()


def docker(args: list[str], *, timeout: int = 600) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["docker", *args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          check=False, timeout=timeout)


def docker_observation(args: list[str], *, timeout: int = 600) -> subprocess.CompletedProcess[bytes]:
    """Keep probe stdout and stderr as separate raw evidence."""
    return subprocess.run(["docker", *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          check=False, timeout=timeout)


def distribution_backend(version: str) -> str:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version)
    if match is None:
        raise Blocked("BLOCKED_RUNTIME_IDENTITY", "invalid observed Python version")
    major, minor, _ = map(int, match.groups())
    return ("STDLIB_IMPORTLIB_METADATA" if (major, minor) >= (3, 8)
            else "PIP_LIST_JSON")


def canonical_distribution_manifest(raw: bytes, backend: str) -> bytes:
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError("duplicate JSON key")
            value[key] = item
        return value
    try:
        records = json.loads(raw.decode("utf-8", errors="strict"),
                             parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
                             object_pairs_hook=unique_object)
    except (UnicodeError, ValueError) as exc:
        raise Blocked("BLOCKED_RUNTIME_IDENTITY", "distribution probe JSON invalid") from exc
    if not isinstance(records, list):
        raise Blocked("BLOCKED_RUNTIME_IDENTITY", "distribution probe must return a list")
    pairs: list[list[str]] = []
    for record in records:
        if backend == "PIP_LIST_JSON":
            if not isinstance(record, dict):
                raise Blocked("BLOCKED_RUNTIME_IDENTITY", "invalid pip distribution record")
            name, version = record.get("name"), record.get("version")
        elif backend == "STDLIB_IMPORTLIB_METADATA":
            if not isinstance(record, list) or len(record) != 2:
                raise Blocked("BLOCKED_RUNTIME_IDENTITY", "invalid stdlib distribution record")
            name, version = record
        else:
            raise Blocked("BLOCKED_RUNTIME_IDENTITY", "unknown distribution probe backend")
        if (not isinstance(name, str) or not name.strip() or not isinstance(version, str)
                or not version.strip()):
            raise Blocked("BLOCKED_RUNTIME_IDENTITY", "distribution name/version missing")
        pairs.append([name, version])
    pairs.sort(key=lambda pair: (re.sub(r"[-_.]+", "-", pair[0]).casefold(),
                                 pair[1], pair[0]))
    return canonical_json(pairs)


def probe_distributions(image_id: str, python_version: str) -> dict[str, Any]:
    backend = distribution_backend(python_version)
    if backend == "STDLIB_IMPORTLIB_METADATA":
        code = ("import importlib.metadata,json; "
                "print(json.dumps([(d.metadata.get('Name',''),d.version) "
                "for d in importlib.metadata.distributions()]))")
        command = ["python", "-c", code]
    else:
        command = ["python", "-m", "pip", "list", "--format=json"]
    args = ["docker", "run", "--rm", "--pull=never", f"--platform={PLATFORM}",
            "--network=none", "--read-only", "--tmpfs", "/tmp", "-e", "HOME=/tmp",
            image_id, *command]
    try:
        result = docker_observation(args[1:])
    except subprocess.TimeoutExpired as exc:
        raise ProbeBlocked("distribution probe timed out", backend=backend, command=args,
                           stdout=exc.stdout or b"", stderr=exc.stderr or b"",
                           exit_code=None) from exc
    except OSError as exc:
        raise ProbeBlocked("distribution probe unavailable", backend=backend, command=args,
                           stdout=b"", stderr=str(exc).encode(), exit_code=None) from exc
    if result.returncode:
        raise ProbeBlocked("distribution probe failed", backend=backend, command=args,
                           stdout=result.stdout, stderr=result.stderr,
                           exit_code=result.returncode)
    try:
        manifest = canonical_distribution_manifest(result.stdout, backend)
    except Blocked as exc:
        raise ProbeBlocked(str(exc), backend=backend, command=args, stdout=result.stdout,
                           stderr=result.stderr, exit_code=result.returncode) from exc
    return {"backend": backend, "manifest": manifest, "stdout": result.stdout,
            "stderr": result.stderr, "exit_code": result.returncode,
            "command": args}


def probe_python(image: str) -> dict[str, str]:
    code = ("import hashlib,json,platform,sys; p=sys.executable; "
            "print(json.dumps({'version':'.'.join(map(str,sys.version_info[:3])),"
            "'machine':platform.machine(),'executable':p,"
            "'executable_sha256':hashlib.sha256(open(p,'rb').read()).hexdigest()}))")
    result = docker(["run", "--rm", f"--platform={PLATFORM}", "--network=none", "--read-only",
                     "--tmpfs", "/tmp", image, "python", "-c", code])
    if result.returncode:
        raise Blocked("BLOCKED_RUNTIME_IDENTITY", "Python probe failed")
    try:
        return json.loads(result.stdout)
    except (ValueError, UnicodeError) as exc:
        raise Blocked("BLOCKED_RUNTIME_IDENTITY", "Python probe output invalid") from exc


def verify_base(recipe: dict[str, Any]) -> dict[str, str]:
    base = recipe["base_image_reference"]
    digest = recipe["base_image_digest"]
    if not DIGEST.fullmatch(digest) or base != f"docker.io/library/python@{digest}":
        raise Blocked("BLOCKED_RUNTIME_IDENTITY", "base reference/digest mismatch")
    observed = docker(["image", "inspect", base])
    if observed.returncode:
        raise Blocked("BLOCKED_RUNTIME_IDENTITY", "frozen base image unavailable locally")
    image = json.loads(observed.stdout)[0]
    if (image.get("Os"), image.get("Architecture")) != ("linux", "amd64"):
        raise Blocked("BLOCKED_RUNTIME_IDENTITY", "base platform mismatch")
    if digest not in image.get("Id", "") and not any(
            item.endswith(digest) for item in image.get("RepoDigests", [])):
        raise Blocked("BLOCKED_RUNTIME_IDENTITY", "base digest not observed")
    probe = probe_python(base)
    if (probe.get("version") != recipe["python_declared_version"]
            or probe.get("version") != recipe["python_observed_version"]
            or probe.get("machine") != "x86_64"
            or probe.get("executable_sha256") != recipe["python_executable_sha256"]):
        raise Blocked("BLOCKED_RUNTIME_IDENTITY", "observed Python identity mismatch")
    return probe


def inspect_final(image_id: str, recipe: dict[str, Any]) -> dict[str, Any]:
    result = docker(["image", "inspect", image_id])
    if result.returncode:
        raise Blocked("BLOCKED_RUNTIME_IDENTITY", "final image inspect failed")
    observed = json.loads(result.stdout)[0]
    if observed.get("Id") != image_id or (observed.get("Os"), observed.get("Architecture")) != (
            "linux", "amd64") or not DIGEST.fullmatch(image_id):
        raise Blocked("BLOCKED_RUNTIME_IDENTITY", "final image identity mismatch")
    python = probe_python(image_id)
    if (python.get("version") != recipe["python_declared_version"]
            or python.get("executable_sha256") != recipe["python_executable_sha256"]):
        raise Blocked("BLOCKED_RUNTIME_IDENTITY", "final Python identity mismatch")
    distributions = probe_distributions(image_id, python["version"])
    packages = docker_observation(["run", "--rm", "--pull=never", f"--platform={PLATFORM}", "--network=none",
                                   "--read-only", "--tmpfs", "/tmp", image_id,
                                   "dpkg-query", "-W", "-f=${Package} ${Version}\\n"])
    if packages.returncode:
        raise Blocked("BLOCKED_RUNTIME_IDENTITY", "package manifest observation failed")
    layers = observed.get("RootFS", {}).get("Layers")
    if not layers or not all(DIGEST.fullmatch(x) for x in layers):
        raise Blocked("BLOCKED_RUNTIME_IDENTITY", "RootFS layer identity unavailable")
    return {"inspect": observed, "inspect_raw": result.stdout, "python": python,
            "distributions": distributions["manifest"], "distribution_probe": distributions,
            "system_packages": packages.stdout, "system_packages_stderr": packages.stderr,
            "layers": layers}


def complete_existing_identity(image_id: str, original_attempt: dict[str, Any],
                               original_inspect: dict[str, Any],
                               recipe: dict[str, Any]) -> dict[str, Any]:
    """Observe only the exact successful image from one blocked Batch-01 build."""
    revisions = original_attempt.get("revisions", [])
    if (original_attempt.get("status") != "BLOCKED_RUNTIME_IDENTITY"
            or original_attempt.get("attempt_id") != "batch01_10_keras_28"
            or len(revisions) != 1 or revisions[0].get("canonical_case_id") != "keras::28"
            or revisions[0].get("build_exit_code") != 0
            or revisions[0].get("build_command", [])[:2] != ["docker", "build"]
            or recipe.get("canonical_case_id") != "keras::28"
            or original_inspect.get("Id") != image_id or not DIGEST.fullmatch(image_id)):
        raise Blocked("BLOCKED_RUNTIME_IDENTITY", "original build/image evidence mismatch")
    saved_layers = original_inspect.get("RootFS", {}).get("Layers")
    if not saved_layers or not all(DIGEST.fullmatch(layer) for layer in saved_layers):
        raise Blocked("BLOCKED_RUNTIME_IDENTITY", "original RootFS evidence missing")
    current = docker(["image", "inspect", image_id])
    if current.returncode:
        raise Blocked("IDENTITY_COMPLETION_IMAGE_UNAVAILABLE", "original image unavailable")
    try:
        observed = json.loads(current.stdout)[0]
    except (ValueError, IndexError, KeyError) as exc:
        raise Blocked("BLOCKED_RUNTIME_IDENTITY", "current image inspection invalid") from exc
    if (observed.get("Id") != image_id
            or observed.get("RootFS", {}).get("Layers") != saved_layers):
        raise Blocked("BLOCKED_RUNTIME_IDENTITY", "original image/RootFS mismatch")
    result = inspect_final(image_id, recipe)
    if result["layers"] != saved_layers or result["python"]["version"] != "3.7.3":
        raise Blocked("BLOCKED_RUNTIME_IDENTITY", "completed identity differs from original")
    result["network"] = revisions[0]["network_build_policy"] == "NETWORK_ALLOWED_RECORDED"
    return result


def identity(recipe: dict[str, Any], revision_label: str, revision_sha: str,
             evidence: dict[str, Any], packaging_hash: str) -> dict[str, str]:
    image = evidence["inspect"]
    values = {
        "canonical_case_id": recipe["canonical_case_id"], "revision_label": revision_label,
        "revision_sha": revision_sha, "runtime_backend": "docker",
        "runtime_platform": PLATFORM, "base_image_reference": recipe["base_image_reference"],
        "base_image_digest": recipe["base_image_digest"],
        "python_declared_version": recipe["python_declared_version"],
        "python_observed_version": evidence["python"]["version"],
        "python_executable_sha256": evidence["python"]["executable_sha256"],
        "build_recipe_sha256": recipe_hash(recipe),
        "requirements_sha256": recipe["requirements_raw_sha256"],
        "setup_sha256": recipe["setup_sha256"],
        "packaging_metadata_sha256": packaging_hash,
        "system_dependency_manifest_sha256": sha256(evidence["system_packages"]),
        "installed_distribution_manifest_sha256": sha256(evidence["distributions"]),
        # Docker Id is the observed immutable image configuration digest (not a registry manifest).
        "environment_image_digest": image["Id"],
        "environment_tree_or_rootfs_identity": sha256(canonical_json(evidence["layers"])),
        "network_build_policy": "NETWORK_ALLOWED_RECORDED" if evidence["network"] else "NONE",
        "network_execution_policy": "NONE",
        "execution_plan_sha256": recipe["execution_plan_sha256"],
        "screening_runtime_spec_sha256": recipe["screening_runtime_v1_sha256"],
    }
    if tuple(values) != ENVIRONMENT_IDENTITY_V1_FIELDS:
        raise Blocked("BLOCKED_INPUT_IDENTITY", "environment identity schema drift")
    if any(not value or value == "UNBUILT" for value in values.values()):
        raise Blocked("BLOCKED_RUNTIME_IDENTITY", "materialized identity has missing observations")
    return values


def _materialize_checked(fixture: dict[str, Any], *, output: Path, input_root: Path,
                         synthetic_only: bool, single_identity: bool = False) -> dict[str, Any]:
    """Build from already-verified immutable inputs, preserving one attempt's evidence."""
    if not synthetic_only and not REAL_MATERIALIZATION_ENABLED:
        raise Blocked("BLOCKED_AUTHORITY", "production materialization gate disabled")
    output.mkdir(parents=True, exist_ok=False)
    record: dict[str, Any] = {"status": "INTERRUPTED", "started_at": now(),
                              "materializer_version": MATERIALIZER_VERSION,
                              "materializer_source_sha256": sha256(Path(__file__).read_bytes()),
                              "materializer_commit": materializer_commit(),
                              "attempt_id": output.name, "synthetic_only": synthetic_only}
    try:
        recipe = fixture["recipe"]
        if synthetic_only and not recipe["canonical_case_id"].startswith("SYNTHETIC_"):
            raise Blocked("BLOCKED_INPUT_IDENTITY", "only synthetic fixture IDs accepted")
        if synthetic_only and fixture.get("network_build"):
            raise Blocked("BLOCKED_INPUT_IDENTITY", "synthetic builds must have no network")
        if recipe_hash(recipe) != fixture["build_recipe_sha256"]:
            raise Blocked("BLOCKED_INPUT_IDENTITY", "recipe hash mismatch")
        root = input_root.resolve(strict=True)
        if synthetic_only and root != FIXTURES.resolve(strict=True):
            raise Blocked("BLOCKED_INPUT_IDENTITY", "synthetic fixture root mismatch")
        def fixture_bytes(key: str) -> bytes | None:
            relative = fixture.get(key)
            if relative is None:
                return None
            path = (root / relative).resolve(strict=True)
            if not path.is_relative_to(root) or not path.is_file():
                raise Blocked("BLOCKED_INPUT_IDENTITY", "fixture input escapes root")
            return path.read_bytes()
        raw = fixture_bytes("raw_requirements")
        normalized = fixture_bytes("normalized_requirements")
        dependency = fixture_bytes("dependency_input")
        setup = fixture_bytes("setup_input")
        verify_inputs(recipe, raw, normalized, dependency, fixture.get("self_reference_ledger", []),
                      setup)
        mode = recipe["environment_mode_v2"]
        revisions = fixture["revisions"]
        if single_identity and (not isinstance(revisions, list) or len(revisions) != 1
                                or not isinstance(revisions[0], dict)
                                or fixture.get("revision_label") != revisions[0].get("label")):
            raise Blocked("BLOCKED_INPUT_IDENTITY", "exactly one named revision required")
        if mode == "SOURCE_INDEPENDENT_ENVIRONMENT":
            if revisions != [{"label": "SOURCE_INDEPENDENT", "sha": "ABSENT"}]:
                raise Blocked("BLOCKED_INPUT_IDENTITY", "source-independent fixture has source")
        elif mode == "REVISION_SPECIFIC_BUILD_REQUIRED":
            if single_identity:
                label = fixture["revision_label"]
                if label not in ("BUGGY", "FIXED") or revisions[0].get(
                        "source_revision_sha") != recipe[f"{label.lower()}_source_sha"]:
                    raise Blocked("BLOCKED_INPUT_IDENTITY", "frozen single revision mismatch")
            else:
                if [r["label"] for r in revisions] != ["BUGGY", "FIXED"]:
                    raise Blocked("BLOCKED_INPUT_IDENTITY", "two source revisions required")
                if not synthetic_only and [r.get("source_revision_sha") for r in revisions] != [
                        recipe["buggy_source_sha"], recipe["fixed_source_sha"]]:
                    raise Blocked("BLOCKED_INPUT_IDENTITY", "frozen source revisions mismatch")
        else:
            raise Blocked("BLOCKED_INPUT_IDENTITY", "unsupported environment mode")
        if fixture.get("simulate_python_mismatch"):
            raise Blocked("BLOCKED_RUNTIME_IDENTITY", "synthetic base Python mismatch")
        if fixture.get("simulate_interrupt"):
            raise KeyboardInterrupt
        # Validate both snapshots before any Docker probe or first revision build.
        sources: list[tuple[dict[str, Any], Path | None, dict[str, Any] | None]] = []
        for revision in revisions:
            source_name = revision.get("source")
            source = None
            source_manifest = None
            if source_name is not None:
                source = (root / source_name).resolve(strict=True)
                if not source.is_relative_to(root):
                    raise Blocked("BLOCKED_INPUT_IDENTITY", "source escapes synthetic root")
                source_manifest, source_hash = snapshot_manifest(source)
                if source_hash != revision["sha"]:
                    raise Blocked("BLOCKED_INPUT_IDENTITY", "source snapshot identity mismatch")
            elif mode != "SOURCE_INDEPENDENT_ENVIRONMENT":
                raise Blocked("BLOCKED_INPUT_IDENTITY", "source snapshot required")
            sources.append((revision, source, source_manifest))
        base_probe = verify_base(recipe)
        record["base_python_probe"] = base_probe
        record["build_recipe_sha256"] = recipe_hash(recipe)
        record["revisions"] = []
        for revision, source, source_manifest in sources:
            label = revision["label"]
            definition = build_definition(recipe, source_present=source is not None,
                                          dependency_present=dependency is not None)
            # Validate every action before creating a build context or invoking Docker.
            revision_dir = output / label
            revision_dir.mkdir()
            (revision_dir / "Dockerfile").write_bytes(definition)
            context = revision_dir / "context"
            context.mkdir()
            (context / "Dockerfile").write_bytes(definition)
            if dependency is not None:
                (context / "dependencies.txt").write_bytes(dependency)
            if source is not None:
                shutil.copytree(source, context / "source", symlinks=True)
            manifest, context_hash = context_manifest(context)
            (revision_dir / "build_context_manifest.json").write_bytes(canonical_json(manifest))
            if source_manifest is not None:
                (revision_dir / "source_snapshot_manifest.json").write_bytes(
                    canonical_json(source_manifest))
            image_tag = f"errpilot-synthetic-materializer:{output.name.lower()}-{label.lower()}"
            if not SAFE_NAME.fullmatch(output.name):
                raise Blocked("BLOCKED_INPUT_IDENTITY", "unsafe attempt identity")
            network = bool(fixture.get("network_build", False))
            command = ["build", f"--platform={PLATFORM}", "--network=default" if network
                       else "--network=none", "--progress=plain", "--no-cache", "-t", image_tag,
                       "-f", str(context / "Dockerfile"), str(context)]
            started = now()
            try:
                build = docker(command, timeout=1200)
            except subprocess.TimeoutExpired as exc:
                (revision_dir / "build.log").write_bytes(exc.stdout or b"")
                raise Blocked("BUILD_FAILED", "Docker build timed out") from exc
            log = build.stdout
            (revision_dir / "build.log").write_bytes(log)
            entry: dict[str, Any] = {
                "canonical_case_id": recipe["canonical_case_id"],
                "revision_label": label, "source_snapshot_identity": revision["sha"],
                "source_revision_identity": revision.get("source_revision_sha", revision["sha"]),
                "build_recipe_sha256": recipe_hash(recipe), "runtime_platform": PLATFORM,
                "base_image_digest": recipe["base_image_digest"],
                "build_started_at": started, "build_ended_at": now(), "build_command": ["docker", *command],
                "dockerfile_sha256": sha256(definition), "build_context_manifest_sha256": context_hash,
                "build_log_sha256": sha256(log), "build_exit_code": build.returncode,
                "network_build_policy": "NETWORK_ALLOWED_RECORDED" if network else "NONE",
            }
            record["revisions"].append(entry)
            if build.returncode:
                raise Blocked("BUILD_FAILED", "Docker build failed; no retry")
            inspected_tag = docker(["image", "inspect", image_tag])
            if inspected_tag.returncode:
                raise Blocked("BLOCKED_RUNTIME_IDENTITY", "built tag cannot be inspected")
            image_id = json.loads(inspected_tag.stdout)[0]["Id"]
            observations = inspect_final(image_id, recipe)
            observations["network"] = network
            (revision_dir / "image_inspect.json").write_bytes(observations["inspect_raw"])
            (revision_dir / "installed_distributions.json").write_bytes(
                observations["distributions"])
            (revision_dir / "distribution_probe.stdout").write_bytes(
                observations["distribution_probe"]["stdout"])
            (revision_dir / "distribution_probe.stderr").write_bytes(
                observations["distribution_probe"]["stderr"])
            (revision_dir / "system_packages.txt").write_bytes(observations["system_packages"])
            (revision_dir / "system_packages.stderr").write_bytes(
                observations["system_packages_stderr"])
            # Reuse the no-follow context entries even when packaging metadata is a link.
            packaging_entries = [{**entry, "path": entry["path"].removeprefix("source/")}
                                 for entry in manifest["entries"]
                                 if entry["path"] in {"source/setup.py", "source/setup.cfg",
                                                      "source/pyproject.toml"}]
            packaging_hash = (sha256(canonical_json(packaging_entries))
                              if source is not None else "ABSENT")
            ident = identity(recipe, label, revision.get("source_revision_sha", revision["sha"]),
                             observations, packaging_hash)
            identity_bytes = canonical_json(ident)
            (revision_dir / "environment_identity.json").write_bytes(identity_bytes)
            entry.update({
                "status": "MATERIALIZED", "final_image_id": image_id,
                "immutable_final_manifest_digest": observations["inspect"].get("RepoDigests", [])
                or "UNAVAILABLE_LOCAL_ONLY", "rootfs_layers": observations["layers"],
                "observed_python": observations["python"],
                "image_inspect_sha256": sha256(observations["inspect_raw"]),
                "installed_distribution_manifest_sha256": sha256(observations["distributions"]),
                "distribution_probe_version": DISTRIBUTION_PROBE_VERSION,
                "distribution_probe_backend": observations["distribution_probe"]["backend"],
                "distribution_probe_command": observations["distribution_probe"]["command"],
                "distribution_probe_exit_code": observations["distribution_probe"]["exit_code"],
                "distribution_probe_stdout_sha256": sha256(
                    observations["distribution_probe"]["stdout"]),
                "distribution_probe_stderr_sha256": sha256(
                    observations["distribution_probe"]["stderr"]),
                "system_package_manifest_sha256": sha256(observations["system_packages"]),
                "system_package_stderr_sha256": sha256(observations["system_packages_stderr"]),
                "environment_identity_sha256": sha256(identity_bytes),
            })
        record["status"] = "MATERIALIZED"
    except ProbeBlocked as exc:
        if "revision_dir" in locals() and record.get("revisions"):
            (revision_dir / "distribution_probe.stdout").write_bytes(exc.stdout)
            (revision_dir / "distribution_probe.stderr").write_bytes(exc.stderr)
            record["revisions"][-1].update({
                "distribution_probe_version": DISTRIBUTION_PROBE_VERSION,
                "distribution_probe_backend": exc.backend,
                "distribution_probe_command": exc.command,
                "distribution_probe_exit_code": exc.exit_code,
                "distribution_probe_stdout_sha256": sha256(exc.stdout),
                "distribution_probe_stderr_sha256": sha256(exc.stderr),
            })
        record.update(status=exc.status, reason=str(exc))
    except Blocked as exc:
        record.update(status=exc.status, reason=str(exc))
    except KeyboardInterrupt:
        record.update(status="INTERRUPTED", reason="synthetic interruption")
    finally:
        record["ended_at"] = now()
        (output / "attempt.json").write_bytes(canonical_json(record))
    return record


def materialize_synthetic(fixture: dict[str, Any], *, output: Path,
                          fixture_root: Path = FIXTURES) -> dict[str, Any]:
    """Only fixture IDs and paths under the checked synthetic fixture root enter Docker."""
    return _materialize_checked(fixture, output=output, input_root=fixture_root,
                                synthetic_only=True)


def materialize_real_request(request: dict[str, Any], *, authority_token: str,
                             output: Path, input_root: Path) -> dict[str, Any]:
    """Production entrypoint; callers require separate Human-PI case authority."""
    if authority_token != AUTHORITY_TOKEN or not REAL_MATERIALIZATION_ENABLED:
        raise Blocked("BLOCKED_AUTHORITY", "production materialization authority unavailable")
    if materializer_commit() == "UNAVAILABLE" or not materializer_git_clean():
        raise Blocked("BLOCKED_INPUT_IDENTITY", "materializer commit must be clean")
    recipes = {r["canonical_case_id"]: r for r in check_frozen_ledger()}
    case_id = request.get("canonical_case_id")
    if case_id not in recipes:
        raise Blocked("BLOCKED_INPUT_IDENTITY", "case outside frozen initial 40")
    recipe = recipes[case_id]
    if request.get("build_recipe_sha256") != recipe_hash(recipe):
        raise Blocked("BLOCKED_INPUT_IDENTITY", "frozen recipe hash mismatch")
    frozen_ledger = [r for r in read_rows(BENCHMARK / "self_reference_ledger.csv")
                     if r["canonical_case_id"] == case_id]
    if request.get("self_reference_ledger") != frozen_ledger:
        raise Blocked("BLOCKED_INPUT_IDENTITY", "self-reference ledger mismatch")
    request = {**request, "recipe": recipe}
    return _materialize_checked(request, output=output, input_root=input_root,
                                synthetic_only=False)


def materialize_expansion_block_01_request(request: dict[str, Any], *, authority_token: str,
                                           output: Path, input_root: Path) -> dict[str, Any]:
    """Block-01-only capability; a later Human-PI transaction must name the case."""
    if authority_token != EXPANSION_01_AUTHORITY_TOKEN or not REAL_MATERIALIZATION_ENABLED:
        raise Blocked("BLOCKED_AUTHORITY", "Block 01 materialization authority unavailable")
    if materializer_commit() == "UNAVAILABLE" or not materializer_git_clean():
        raise Blocked("BLOCKED_INPUT_IDENTITY", "materializer commit must be clean")
    recipes = {r["canonical_case_id"]: r for r in check_expansion_block_01_ledger()}
    case_id = request.get("canonical_case_id")
    if case_id not in recipes:
        raise Blocked("BLOCKED_INPUT_IDENTITY", "case outside frozen Expansion Block 01")
    recipe = recipes[case_id]
    if (request.get("expansion_block") != 1
            or request.get("expansion_order") != recipe["expansion_order"]
            or request.get("block_identity_sha256") != EXPANSION_01_BLOCK_SHA256
            or request.get("build_recipe_sha256") != recipe_hash(recipe)):
        raise Blocked("BLOCKED_INPUT_IDENTITY", "Block 01 request identity mismatch")
    frozen_ledger = [
        {k: v for k, v in row.items() if k not in ("expansion_block", "expansion_order")}
        for row in read_rows(BENCHMARK / "expansion_block_01_self_reference_ledger.csv")
        if row["canonical_case_id"] == case_id
    ]
    if request.get("self_reference_ledger") != frozen_ledger:
        raise Blocked("BLOCKED_INPUT_IDENTITY", "Block 01 self-reference ledger mismatch")
    namespace = Path("derived_inputs") / "expansion_block_01" / case_id.replace("::", "__")
    if (request.get("normalized_requirements") != (namespace / "requirements.normalized.txt").as_posix()
            or request.get("dependency_input") != (namespace / "requirements.dependencies.txt").as_posix()):
        raise Blocked("BLOCKED_INPUT_IDENTITY", "Block 01 derived-input namespace mismatch")
    label = request.get("revision_label")
    revisions = request.get("revisions")
    if (not isinstance(revisions, list) or len(revisions) != 1
            or not isinstance(revisions[0], dict) or revisions[0].get("label") != label):
        raise Blocked("BLOCKED_INPUT_IDENTITY", "Block 01 requires one named identity")
    revision = revisions[0]
    if recipe["environment_mode_v2"] == "SOURCE_INDEPENDENT_ENVIRONMENT":
        if label != "SOURCE_INDEPENDENT" or revision != {
                "label": "SOURCE_INDEPENDENT", "sha": "ABSENT"}:
            raise Blocked("BLOCKED_INPUT_IDENTITY", "source-independent identity mismatch")
    elif (label not in ("BUGGY", "FIXED")
          or set(revision) != {"label", "sha", "source", "source_revision_sha"}
          or revision["source_revision_sha"] != recipe[f"{label.lower()}_source_sha"]
          or not isinstance(revision["sha"], str)
          or not HEX64.fullmatch(revision["sha"])
          or not isinstance(revision["source"], str)
          or not revision["source"]):
        raise Blocked("BLOCKED_INPUT_IDENTITY", "frozen Block 01 revision mismatch")
    checked = {**request, "recipe": recipe}
    return _materialize_checked(checked, output=output, input_root=input_root,
                                synthetic_only=False, single_identity=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode")
    sub.add_parser("validate", help="verify frozen 40-case recipe ledger without a build")
    sub.add_parser("plan", help="show frozen build modes without a build")
    materialize = sub.add_parser("materialize", help="gated real materialization")
    materialize.add_argument("--authority-token", required=True)
    materialize.add_argument("--request", type=Path)
    materialize.add_argument("--input-root", type=Path)
    materialize.add_argument("--output", type=Path)
    expansion = sub.add_parser("materialize-expansion-01", help="gated Block 01 materialization")
    expansion.add_argument("--authority-token", required=True)
    expansion.add_argument("--request", type=Path)
    expansion.add_argument("--input-root", type=Path)
    expansion.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.mode is None:
        parser.print_help()
        return 2
    try:
        if args.mode == "validate":
            check_frozen_ledger()
            print("40 frozen ready recipes verified; all UNBUILT")
        elif args.mode == "plan":
            recipes = check_frozen_ledger()
            print(json.dumps({"cases": len(recipes), "source_independent": 26,
                              "revision_specific": 14, "materialized": 0}, sort_keys=True))
        elif args.mode == "materialize":
            check_frozen_ledger()
            if args.authority_token != AUTHORITY_TOKEN:
                raise Blocked("BLOCKED_AUTHORITY", "exact future authority token required")
            if not REAL_MATERIALIZATION_ENABLED:
                raise Blocked("BLOCKED_AUTHORITY", "production materialization gate disabled")
            if not all((args.request, args.input_root, args.output)):
                raise Blocked("BLOCKED_INPUT_IDENTITY", "request, input root, and output required")
            request = json.loads(args.request.read_text(encoding="utf-8"))
            result = materialize_real_request(request, authority_token=args.authority_token,
                                              output=args.output,
                                              input_root=args.input_root)
            print(json.dumps({"status": result["status"], "attempt_id": result["attempt_id"]}))
            return 0 if result["status"] == "MATERIALIZED" else 1
        elif args.mode == "materialize-expansion-01":
            if args.authority_token != EXPANSION_01_AUTHORITY_TOKEN:
                raise Blocked("BLOCKED_AUTHORITY", "exact Block 01 authority token required")
            if not all((args.request, args.input_root, args.output)):
                raise Blocked("BLOCKED_INPUT_IDENTITY", "request, input root, and output required")
            request = json.loads(args.request.read_text(encoding="utf-8"))
            result = materialize_expansion_block_01_request(
                request, authority_token=args.authority_token,
                output=args.output, input_root=args.input_root,
            )
            print(json.dumps({"status": result["status"], "attempt_id": result["attempt_id"]}))
            return 0 if result["status"] == "MATERIALIZED" else 1
    except Blocked as exc:
        print(f"{exc.status}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

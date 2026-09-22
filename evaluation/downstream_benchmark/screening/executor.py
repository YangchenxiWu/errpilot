#!/usr/bin/env python3
"""Prepare BugsInPy screening plans and gate any future 3+3 execution.

Preparation reads benchmark metadata and Git object identities.  It never invokes
an oracle.  Execution is a separate subcommand guarded by an exact authority
token and produces a six-entry BUGGY/BUGGY/BUGGY/FIXED/FIXED/FIXED schedule.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shlex
import signal
import stat
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable, Sequence


BUGSINPY_COMMIT = "11c5f1eea954a42132cfd06bf257766a7963e0fd"
BUGSINPY_TREE = "d00ce0495ba73abe50317599f48bced3c9afe4b3"
CANDIDATE_UNIVERSE_SHA256 = "78208adf610a50542be6dfbd03a9b25960ba0b5cfc80768b08ffe7a4c78f3b8c"
PROTOCOL_SHA256 = "34e014a07821dc9dca52178874eef0b847aee7f048071fb4920864ae5d3bee93"
RUN_SPEC_SHA256 = "29ab6f78739d0eeea1c2a774e62e2d133f173e160c3d247407970a80726f4406"
INITIAL_CASE_COUNT = 40
EXECUTION_AUTHORITY_TOKEN = "BUGSINPY_SCREENING_3X3_EXECUTION_AUTHORIZED_V1"
PRE_EXECUTION_TIMEOUT_GATE_REQUIRED = True
PRODUCTION_DOCKER_BACKEND_IMPLEMENTED = False
PRODUCTION_RUNTIME_BACKEND = "docker"
PRODUCTION_RUNTIME_PLATFORM = "linux/amd64"
DOCKER_EXECUTION_NETWORK_MODE = "none"
SUBCOMMAND_TIMEOUT_SECONDS = 300
TRIAL_TIMEOUT_SECONDS = 900

ENVIRONMENT_IDENTITY_V1_FIELDS = (
    "canonical_case_id", "revision_label", "revision_sha", "runtime_backend",
    "runtime_platform", "base_image_reference", "base_image_digest",
    "python_declared_version", "python_observed_version", "python_executable_sha256",
    "build_recipe_sha256", "requirements_sha256", "setup_sha256",
    "packaging_metadata_sha256", "system_dependency_manifest_sha256",
    "installed_distribution_manifest_sha256", "environment_image_digest",
    "environment_tree_or_rootfs_identity", "network_build_policy",
    "network_execution_policy", "execution_plan_sha256", "screening_runtime_spec_sha256",
)

PLAN_FIELDS = (
    "candidate_rank",
    "initial_selection_order",
    "canonical_case_id",
    "project",
    "bugsinpy_bug_id",
    "buggy_revision_metadata",
    "buggy_commit_full",
    "fixed_revision_metadata",
    "fixed_commit_full",
    "python_version",
    "oracle_script_sha256",
    "oracle_command",
    "oracle_commands",
    "oracle_command_count",
    "oracle_cwd",
    "declared_test_file",
    "protected_manifest_status",
    "environment_plan_status",
    "subject_source_url",
    "subject_checkout_identity",
    "screening_ready",
    "pre_execution_timeout_gate",
    "blocking_reason",
    "oracle_plan_status",
    "execution_plan_sha256",
)

_HEX_REVISION = re.compile(r"[0-9a-fA-F]{7,40}")
_SAFE_CASE_ID = re.compile(r"[^A-Za-z0-9._-]+")
_SHELL_CONTROL = re.compile(r"(?:&&|\|\||[;|<>`]|\$\(|\n)")
_UNSAFE_COMMAND_TEXT = re.compile(r'[\\"$\\\\*?{}~]')
_NETWORK_OR_GUI_COMMANDS = {
    "curl",
    "wget",
    "ssh",
    "scp",
    "open",
    "xdg-open",
    "osascript",
}
_TEST_EXECUTABLES = {"pytest", "py.test", "nosetests", "nose"}


class PreparationError(RuntimeError):
    """Raised when preparation cannot freeze an unambiguous plan."""


class RevisionResolutionError(PreparationError):
    """Raised when a declared revision is missing or ambiguous."""


class InfrastructureFailure(RuntimeError):
    """Raised for runner/setup faults distinct from oracle outcomes."""


class OracleTimeout(InfrastructureFailure):
    """A timed-out oracle process group, with any captured partial streams."""

    def __init__(self, subreason: str, stdout: bytes = b"", stderr: bytes = b"") -> None:
        super().__init__(subreason)
        self.subreason = subreason
        self.stdout = stdout
        self.stderr = stderr


def unbuilt_environment_identity() -> dict[str, str]:
    """Never manufacture a materialized identity from planning evidence."""
    return {field: "UNBUILT" for field in ENVIRONMENT_IDENTITY_V1_FIELDS}


def docker_execution_base_argv(image_reference: str) -> tuple[str, ...]:
    """Inert base command for a future digest-pinned, isolated container trial."""
    if not re.fullmatch(r"[A-Za-z0-9./_-]+@sha256:[0-9a-f]{64}", image_reference):
        raise InfrastructureFailure("immutable OCI image reference required")
    return (
        "docker", "run", "--rm", f"--platform={PRODUCTION_RUNTIME_PLATFORM}",
        f"--network={DOCKER_EXECUTION_NETWORK_MODE}", "--read-only", image_reference,
    )


def run_oracle_process(
    argv: Sequence[str], *, cwd: Path, env: dict[str, str], timeout_seconds: float,
    timeout_subreason: str,
) -> subprocess.CompletedProcess[bytes]:
    """Run one command once and kill/reap its process group on timeout."""
    if timeout_seconds <= 0:
        raise OracleTimeout(timeout_subreason)
    deadline = time.monotonic() + timeout_seconds
    process = subprocess.Popen(
        list(argv), cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=max(0.0, deadline - time.monotonic()))
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        stdout, stderr = process.communicate()
        raise OracleTimeout(timeout_subreason, stdout, stderr) from None
    return subprocess.CompletedProcess(list(argv), process.returncode, stdout, stderr)


@dataclass(frozen=True)
class Candidate:
    candidate_rank: int
    selection_order: int
    canonical_case_id: str
    project: str
    bug_id: str
    source_url: str
    python_version: str
    buggy_revision: str
    fixed_revision: str
    declared_test_file: str
    bugsinpy_source_commit: str


@dataclass(frozen=True)
class ScheduledRun:
    revision_label: str
    ordinal: int


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def deterministic_plan_hash(plan: dict[str, Any]) -> str:
    unhashed = {key: value for key, value in plan.items() if key != "execution_plan_sha256"}
    return sha256_bytes(canonical_json_bytes(unhashed))


def _atomic_write_bytes(path: Path, data: bytes, *, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        temporary_path.chmod(mode)
        temporary_path.replace(path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def _atomic_write_json(path: Path, value: Any) -> None:
    _atomic_write_bytes(path, canonical_json_bytes(value))


def _run(
    command: Sequence[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    text: bool = True,
) -> subprocess.CompletedProcess[Any]:
    result = subprocess.run(
        list(command),
        cwd=cwd,
        check=False,
        capture_output=True,
        text=text,
    )
    if check and result.returncode != 0:
        stderr = result.stderr.strip() if text else result.stderr.decode("utf-8", "replace").strip()
        raise PreparationError(
            f"command failed ({result.returncode}): {shlex.join(command)}: {stderr}"
        )
    return result


def _git(repo: Path, *arguments: str, text: bool = True) -> subprocess.CompletedProcess[Any]:
    prohibited = {"log", "show", "diff"}
    if arguments and arguments[0] in prohibited:
        raise PreparationError(f"fix-leakage control rejected git {arguments[0]}")
    return _run(("git", "-C", str(repo), *arguments), text=text)


def _validate_hash(path: Path, expected: str, label: str) -> None:
    actual = sha256_file(path)
    if actual != expected:
        raise PreparationError(f"{label} hash mismatch: expected {expected}, found {actual}")


def validate_controlling_inputs(benchmark_root: Path) -> None:
    _validate_hash(benchmark_root / "PROTOCOL.md", PROTOCOL_SHA256, "PROTOCOL.md")
    _validate_hash(benchmark_root / "RUN_SPEC_V1.md", RUN_SPEC_SHA256, "RUN_SPEC_V1.md")
    _validate_hash(
        benchmark_root / "candidate_universe.csv",
        CANDIDATE_UNIVERSE_SHA256,
        "candidate_universe.csv",
    )
    for name in ("cases_manifest.csv", "exclusions.csv"):
        rows = (benchmark_root / name).read_text(encoding="utf-8").splitlines()
        if len(rows) != 1:
            raise PreparationError(f"{name} must remain header-only")


def validate_bugsinpy_checkout(root: Path) -> None:
    if not root.is_dir():
        raise PreparationError(f"BugsInPy checkout not found: {root}")
    actual_commit = _git(root, "rev-parse", "HEAD").stdout.strip()
    actual_tree = _git(root, "rev-parse", "HEAD^{tree}").stdout.strip()
    branch = _git(root, "branch", "--show-current").stdout.strip()
    status = _git(root, "status", "--porcelain").stdout.strip()
    if actual_commit != BUGSINPY_COMMIT:
        raise PreparationError(
            f"BugsInPy commit mismatch: expected {BUGSINPY_COMMIT}, found {actual_commit}"
        )
    if actual_tree != BUGSINPY_TREE:
        raise PreparationError(
            f"BugsInPy tree mismatch: expected {BUGSINPY_TREE}, found {actual_tree}"
        )
    if branch:
        raise PreparationError(f"BugsInPy checkout must be detached, found branch {branch}")
    if status:
        raise PreparationError("BugsInPy checkout must be clean")


def load_frozen_candidates(benchmark_root: Path) -> list[Candidate]:
    path = benchmark_root / "candidate_universe.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle) if row["selected_initial_40"] == "true"]
    rows.sort(key=lambda row: int(row["initial_selection_order"]))
    if len(rows) != INITIAL_CASE_COUNT:
        raise PreparationError(f"expected 40 frozen candidates, found {len(rows)}")
    orders = [int(row["initial_selection_order"]) for row in rows]
    if orders != list(range(1, INITIAL_CASE_COUNT + 1)):
        raise PreparationError("initial candidate order is not contiguous 1..40")
    candidates = [
        Candidate(
            candidate_rank=int(row["candidate_rank"]),
            selection_order=int(row["initial_selection_order"]),
            canonical_case_id=row["canonical_case_id"],
            project=row["project"],
            bug_id=row["bugsinpy_bug_id"],
            source_url=row["project_source_url"],
            python_version=row["python_version"],
            buggy_revision=row["buggy_commit_id"],
            fixed_revision=row["fixed_commit_id"],
            declared_test_file=row["declared_test_file"],
            bugsinpy_source_commit=row["bugsinpy_source_commit"],
        )
        for row in rows
    ]
    for candidate in candidates:
        if candidate.canonical_case_id != f"{candidate.project}::{candidate.bug_id}":
            raise PreparationError(f"canonical identity mismatch: {candidate.canonical_case_id}")
        if candidate.bugsinpy_source_commit != BUGSINPY_COMMIT:
            raise PreparationError(
                f"candidate {candidate.canonical_case_id} has wrong BugsInPy identity"
            )
    return candidates


def validate_frozen_order_against_spec(
    candidates: Sequence[Candidate], screening_spec_path: Path
) -> None:
    text = screening_spec_path.read_text(encoding="utf-8")
    try:
        block = text.split("In selection order it is:", 1)[1].split("`candidate_universe.csv`", 1)[
            0
        ]
    except IndexError as exc:
        raise PreparationError("could not locate frozen order in SCREENING_SPEC_V1.md") from exc
    expected = re.findall(r"^\d+\. `([^`]+)`$", block, flags=re.MULTILINE)
    actual = [candidate.canonical_case_id for candidate in candidates]
    if expected != actual:
        raise PreparationError("SCREENING_SPEC_V1.md and candidate_universe.csv order differ")


def safe_case_slug(case_id: str) -> str:
    return _SAFE_CASE_ID.sub("-", case_id).strip("-")


def _remote_urls_match(expected: str, actual: str) -> bool:
    return expected.rstrip("/") == actual.rstrip("/")


def acquire_project_mirror(
    project: str,
    source_url: str,
    mirrors_root: Path,
    *,
    allow_network: bool,
) -> Path:
    mirror = mirrors_root / f"{safe_case_slug(project)}.git"
    if not mirror.exists():
        if not allow_network:
            raise PreparationError(f"subject mirror missing and network not authorized: {mirror}")
        mirrors_root.mkdir(parents=True, exist_ok=True)
        _run(("git", "clone", "--mirror", source_url, str(mirror)))
    if _git(mirror, "rev-parse", "--is-bare-repository").stdout.strip() != "true":
        raise PreparationError(f"subject mirror is not bare: {mirror}")
    actual_url = _git(mirror, "remote", "get-url", "origin").stdout.strip()
    if not _remote_urls_match(source_url, actual_url):
        raise PreparationError(
            f"subject remote mismatch for {project}: expected {source_url}, found {actual_url}"
        )
    if allow_network:
        _git(mirror, "remote", "update", "--prune")
    return mirror


def resolve_revision(repo: Path, revision: str) -> str:
    if _HEX_REVISION.fullmatch(revision) is None:
        raise RevisionResolutionError(f"invalid hexadecimal revision metadata: {revision!r}")
    if len(revision) == 40:
        result = _git(repo, "rev-parse", "--verify", f"{revision}^{{commit}}", text=True)
        resolved = result.stdout.strip()
        if resolved != revision.lower():
            raise RevisionResolutionError(f"full revision did not resolve exactly: {revision}")
        return resolved

    result = _git(repo, "rev-parse", f"--disambiguate={revision}")
    objects = sorted(set(line for line in result.stdout.splitlines() if line))
    commits: list[str] = []
    for object_id in objects:
        object_type = _git(repo, "cat-file", "-t", object_id).stdout.strip()
        if object_type == "commit":
            commits.append(object_id)
    if len(commits) != 1:
        detail = ",".join(commits) if commits else "NONE"
        raise RevisionResolutionError(
            f"revision {revision} resolves to {len(commits)} commit objects: {detail}"
        )
    return commits[0]


def _metadata_file(case_metadata_dir: Path, name: str) -> Path:
    path = case_metadata_dir / name
    if not path.is_file():
        raise PreparationError(f"required BugsInPy metadata missing: {path}")
    return path


def analyze_oracle(script_bytes: bytes) -> dict[str, Any]:
    try:
        text = script_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return {
            "status": "UNRESOLVED_NON_UTF8_SCRIPT",
            "commands": [],
            "oracle_command": "",
            "shell_requirement": "UNKNOWN",
            "blocking_reason": "run_test.sh is not UTF-8",
        }
    substantive = [
        line for line in text.split("\n")
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not substantive:
        return {
            "status": "UNRESOLVED_EMPTY_COMMAND",
            "commands": substantive,
            "oracle_command": "",
            "shell_requirement": "UNKNOWN",
            "blocking_reason": "run_test.sh contains no substantive command",
        }
    for ordinal, command in enumerate(substantive, 1):
        try:
            parse_recognized_command(command)
        except PreparationError as exc:
            return {
                "status": "UNRESOLVED_UNSAFE_OR_UNRECOGNIZED_COMMAND_V1_1",
                "commands": substantive,
                "oracle_command": substantive[0] if len(substantive) == 1 else "",
                "shell_requirement": "UNRESOLVED",
                "blocking_reason": f"subcommand {ordinal}: {exc}",
            }
    return {
        "status": "RESOLVED_ORDERED_COMMANDS",
        "commands": substantive,
        "oracle_command": substantive[0] if len(substantive) == 1 else "",
        "shell_requirement": "POSIX_ARGV_IN_CASE_ENVIRONMENT",
        "blocking_reason": "",
    }


def parse_recognized_command(command: str) -> tuple[str, ...]:
    """Accept only literal whitespace-delimited test argv, never shell syntax.

    An apostrophe embedded in a test selector is a literal byte (keras::28).
    Quotes for grouping and shell expansion are deliberately unsupported.
    """
    if not command or any(char in command for char in ("\r", "\n", "\x00")):
        raise PreparationError("empty or multiline command")
    if (_SHELL_CONTROL.search(command) or _UNSAFE_COMMAND_TEXT.search(command)
            or any(char in command for char in "&#()")):
        raise PreparationError("shell syntax or expansion is unsupported")
    tokens = tuple(command.split())
    if not tokens:
        raise PreparationError("empty command")
    executable = tokens[0]
    if executable in _NETWORK_OR_GUI_COMMANDS:
        raise PreparationError(f"prohibited/interactive command {executable}")
    recognized = executable in {"pytest", "py.test"}
    if executable in {"python", "python3"}:
        recognized = (
            len(tokens) >= 3
            and tokens[1] == "-m"
            and tokens[2]
            in {
                "pytest",
                "unittest",
            }
        )
    if not recognized:
        raise PreparationError(f"unrecognized test command {executable}")
    return tokens


def _safe_subject_path(raw_path: str) -> str:
    normalized = raw_path.strip().replace("\\", "/")
    pure = PurePosixPath(normalized)
    if not normalized or pure.is_absolute() or ".." in pure.parts:
        raise PreparationError(f"unsafe protected path: {raw_path!r}")
    return pure.as_posix()


def extract_oracle_test_paths(commands: Iterable[str]) -> list[str]:
    paths: set[str] = set()
    for command in commands:
        try:
            tokens = shlex.split(command, posix=True)
        except ValueError:
            continue
        for token in tokens:
            candidate = token.split("::", 1)[0]
            if candidate.endswith(".py"):
                paths.add(_safe_subject_path(candidate))
    return sorted(paths)


def git_blob_sha256(repo: Path, commit: str, path: str) -> str:
    safe_path = _safe_subject_path(path)
    result = _git(repo, "cat-file", "blob", f"{commit}:{safe_path}", text=False)
    return sha256_bytes(result.stdout)


def build_protected_manifest(
    candidate: Candidate,
    mirror: Path,
    buggy_commit: str,
    fixed_commit: str,
    oracle_commands: Sequence[str],
) -> dict[str, Any]:
    declared_paths = [
        _safe_subject_path(item) for item in candidate.declared_test_file.split(";") if item.strip()
    ]
    command_paths = extract_oracle_test_paths(oracle_commands)
    all_paths = sorted(set(declared_paths) | set(command_paths))
    entries: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in all_paths:
        is_declared = path in declared_paths
        entry: dict[str, Any] = {
            "path": path,
            "sources": sorted(
                source
                for source, source_paths in (
                    ("DECLARED_TEST_FILE", declared_paths),
                    ("ORACLE_COMMAND", command_paths),
                )
                if path in source_paths
            ),
            "buggy_test_injection_from_fixed": False,
        }
        buggy_checkout_sha256 = ""
        fixed_sha256 = ""
        try:
            buggy_checkout_sha256 = git_blob_sha256(mirror, buggy_commit, path)
        except PreparationError as exc:
            if not is_declared:
                errors.append(f"buggy:{path}:{exc}")
        try:
            fixed_sha256 = git_blob_sha256(mirror, fixed_commit, path)
        except PreparationError as exc:
            errors.append(f"fixed:{path}:{exc}")
        entry["buggy_checkout_sha256"] = buggy_checkout_sha256
        entry["fixed_sha256"] = fixed_sha256
        if is_declared and fixed_sha256:
            # bugsinpy-checkout copies every declared test file from the fixed
            # checkout into the buggy checkout before the oracle.  Preserve
            # that benchmark-owned test identity without reading repair files.
            entry["buggy_effective_sha256"] = fixed_sha256
            entry["buggy_test_injection_from_fixed"] = buggy_checkout_sha256 != fixed_sha256
        else:
            entry["buggy_effective_sha256"] = buggy_checkout_sha256
        if not entry["buggy_effective_sha256"]:
            errors.append(f"effective_buggy:{path}:protected content unavailable")
        entries.append(entry)
    status = "RESOLVED" if entries and not errors else "UNRESOLVED"
    manifest = {
        "schema_version": 1,
        "canonical_case_id": candidate.canonical_case_id,
        "buggy_commit_full": buggy_commit,
        "fixed_commit_full": fixed_commit,
        "status": status,
        "entries": entries,
        "errors": errors,
    }
    manifest["manifest_sha256"] = sha256_bytes(canonical_json_bytes(manifest))
    return manifest


def _file_identity(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"present": False, "sha256": "", "size": 0}
    data = path.read_bytes()
    return {"present": True, "sha256": sha256_bytes(data), "size": len(data)}


def _setup_invokes_tests(script_bytes: bytes) -> bool:
    try:
        lines = script_bytes.decode("utf-8").splitlines()
    except UnicodeDecodeError:
        return True
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            tokens = shlex.split(stripped)
        except ValueError:
            return True
        if not tokens:
            continue
        if _SHELL_CONTROL.search(stripped):
            return True
        executable = Path(tokens[0]).name
        if executable in _TEST_EXECUTABLES:
            return True
        if executable in {"tox", "nox"}:
            return True
        if executable == "make" and any(
            "test" in token or "check" in token for token in tokens[1:]
        ):
            return True
        if executable in {"python", "python3"} and len(tokens) >= 3:
            if tokens[1] == "-m" and tokens[2] in {"pytest", "unittest", "nose"}:
                return True
            if tokens[1].endswith("setup.py") and "test" in tokens[2:]:
                return True
        if executable in {"bash", "sh"} and any("run_test" in token for token in tokens[1:]):
            return True
    return False


def build_environment_plan(
    candidate: Candidate,
    case_metadata_dir: Path,
    framework_root: Path,
) -> dict[str, Any]:
    requirements = case_metadata_dir / "requirements.txt"
    setup = case_metadata_dir / "setup.sh"
    bug_info = _metadata_file(case_metadata_dir, "bug.info")
    project_info = _metadata_file(case_metadata_dir.parent.parent, "project.info")
    run_test = _metadata_file(case_metadata_dir, "run_test.sh")
    setup_may_test = setup.is_file() and _setup_invokes_tests(setup.read_bytes())
    status = (
        "UNRESOLVED_SETUP_MAY_EXECUTE_TESTS" if setup_may_test else "PLAN_FROZEN_BUILD_REQUIRED"
    )
    inputs = {
        "bug_info": _file_identity(bug_info),
        "project_info": _file_identity(project_info),
        "run_test_sh": _file_identity(run_test),
        "requirements_txt": _file_identity(requirements),
        "setup_sh": _file_identity(setup),
        "bugsinpy_test": _file_identity(framework_root / "bin" / "bugsinpy-test"),
        "bugsinpy_compile": _file_identity(framework_root / "bin" / "bugsinpy-compile"),
    }
    dependency_input_sha256 = sha256_bytes(canonical_json_bytes(inputs))
    plan = {
        "schema_version": 1,
        "canonical_case_id": candidate.canonical_case_id,
        "status": status,
        "declared_python_version": candidate.python_version,
        "mechanism": {
            "kind": "case-isolated-read-only-content-addressed-environment",
            "steps": [
                "acquire an exact declared-version Python artifact and record its SHA-256",
                "create an external case-isolated environment",
                "install only the hash-recorded dependency inputs into that environment",
                "run the hash-recorded setup procedure only after a separate setup authorization",
                "record installed distributions and system dependencies",
                "hash the complete environment tree and remove all write permission bits",
                "use a fresh HOME, TMPDIR, and cache directory for every oracle ordinal",
            ],
            "shared_across_ordinals_only_when_read_only": True,
        },
        "build_location": "external_case_directory/environment",
        "dependency_and_setup_inputs": inputs,
        "dependency_input_sha256": dependency_input_sha256,
        "setup_execution_authorized_now": False,
        "setup_may_execute_tests": setup_may_test,
        "required_immutable_identity_fields_after_build": [
            "platform_identity",
            "python_artifact_sha256",
            "python_executable_sha256",
            "dependency_input_sha256",
            "installed_distribution_manifest_sha256",
            "system_dependency_manifest_sha256",
            "setup_evidence_sha256",
            "environment_tree_manifest_sha256",
            "environment_root",
            "environment_bin_dir",
            "read_only_content_addressed",
        ],
        "materialized_identity": None,
    }
    plan["environment_plan_sha256"] = sha256_bytes(canonical_json_bytes(plan))
    return plan


def _write_case_marker(case_root: Path, candidate: Candidate) -> None:
    marker = {
        "schema_version": 1,
        "canonical_case_id": candidate.canonical_case_id,
        "purpose": "SCREENING_ONLY",
        "repair_workspace_usable": False,
        "warning": "Never hand this directory or its repositories to a repair agent.",
    }
    _atomic_write_json(case_root / "SCREENING_ONLY_DO_NOT_USE_FOR_REPAIR.json", marker)
    checkout_root = case_root / "screening_checkout"
    checkout_root.mkdir(parents=True, exist_ok=True)
    _atomic_write_json(checkout_root / "SCREENING_ONLY_DO_NOT_USE_FOR_REPAIR.json", marker)


def prepare_case(
    candidate: Candidate,
    *,
    bugsinpy_root: Path,
    external_root: Path,
    mirror: Path,
) -> dict[str, str]:
    case_root = external_root / "screening_workspaces" / safe_case_slug(candidate.canonical_case_id)
    preparation_root = case_root / "preparation"
    metadata_dir = bugsinpy_root / "projects" / candidate.project / "bugs" / candidate.bug_id
    run_test_path = _metadata_file(metadata_dir, "run_test.sh")
    run_test_bytes = run_test_path.read_bytes()
    oracle = analyze_oracle(run_test_bytes)
    buggy_commit = resolve_revision(mirror, candidate.buggy_revision)
    fixed_commit = resolve_revision(mirror, candidate.fixed_revision)
    if buggy_commit == fixed_commit:
        raise RevisionResolutionError(
            f"{candidate.canonical_case_id} resolves buggy and fixed to the same commit"
        )

    protected_manifest = build_protected_manifest(
        candidate,
        mirror,
        buggy_commit,
        fixed_commit,
        oracle["commands"],
    )
    environment_plan = build_environment_plan(candidate, metadata_dir, bugsinpy_root / "framework")
    subject_identity_data = {
        "source_url": candidate.source_url,
        "buggy_commit_full": buggy_commit,
        "fixed_commit_full": fixed_commit,
        "object_format": _git(mirror, "rev-parse", "--show-object-format").stdout.strip(),
    }
    subject_identity = sha256_bytes(canonical_json_bytes(subject_identity_data))
    blocking_reasons = [
        reason
        for reason in (
            oracle["blocking_reason"],
            "" if protected_manifest["status"] == "RESOLVED" else "protected manifest unresolved",
            ""
            if environment_plan["status"] == "PLAN_FROZEN_BUILD_REQUIRED"
            else "environment plan unresolved",
        )
        if reason
    ]
    screening_ready = not blocking_reasons
    plan: dict[str, Any] = {
        "schema_version": "1.1",
        "oracle_representation_version": "COMPOSITE_ORACLE_SEMANTICS_V1",
        "candidate_rank": candidate.candidate_rank,
        "initial_selection_order": candidate.selection_order,
        "canonical_case_id": candidate.canonical_case_id,
        "project": candidate.project,
        "bugsinpy_bug_id": candidate.bug_id,
        "buggy_revision_metadata": candidate.buggy_revision,
        "buggy_commit_full": buggy_commit,
        "fixed_revision_metadata": candidate.fixed_revision,
        "fixed_commit_full": fixed_commit,
        "python_version": candidate.python_version,
        "oracle_script_sha256": sha256_bytes(run_test_bytes),
        "oracle_command": oracle["oracle_command"],
        "oracle_commands": oracle["commands"],
        "oracle_command_count": len(oracle["commands"]),
        "oracle_cwd": "subject repository root",
        "oracle_plan_status": oracle["status"],
        "oracle_shell_requirement": oracle["shell_requirement"],
        "declared_test_file": candidate.declared_test_file,
        "protected_manifest_status": protected_manifest["status"],
        "protected_manifest_sha256": protected_manifest["manifest_sha256"],
        "environment_plan_status": environment_plan["status"],
        "environment_plan_sha256": environment_plan["environment_plan_sha256"],
        "subject_source_url": candidate.source_url,
        "subject_mirror_path": str(mirror),
        "subject_checkout_identity": subject_identity,
        "screening_ready": screening_ready,
        "blocking_reason": "; ".join(blocking_reasons),
        "execution_authorized": False,
        "pre_execution_timeout_gate": "PRE_EXECUTION_TIMEOUT_GATE_REQUIRED",
        "required_execution_authority_token": EXECUTION_AUTHORITY_TOKEN,
        "execution_order": [
            {"revision": item.revision_label, "ordinal": item.ordinal}
            for item in build_execution_schedule()
        ],
        "no_early_stop": True,
        "unrecorded_retry_allowed": False,
        "bugsinpy_source_commit": BUGSINPY_COMMIT,
        "bugsinpy_source_tree": BUGSINPY_TREE,
        "controlling_hashes": {
            "candidate_universe.csv": CANDIDATE_UNIVERSE_SHA256,
            "PROTOCOL.md": PROTOCOL_SHA256,
            "RUN_SPEC_V1.md": RUN_SPEC_SHA256,
        },
    }
    plan["execution_plan_sha256"] = deterministic_plan_hash(plan)

    _write_case_marker(case_root, candidate)
    _atomic_write_bytes(preparation_root / "oracle" / "run_test.sh", run_test_bytes, mode=0o444)
    _atomic_write_json(preparation_root / "protected_manifest.json", protected_manifest)
    _atomic_write_json(preparation_root / "environment_plan.json", environment_plan)
    _atomic_write_json(preparation_root / "execution_plan.json", plan)
    acquisition_evidence = {
        "schema_version": 1,
        "canonical_case_id": candidate.canonical_case_id,
        "source_url": candidate.source_url,
        "mirror_path": str(mirror),
        "subject_checkout_identity": subject_identity,
        "buggy_revision_metadata": candidate.buggy_revision,
        "buggy_commit_full": buggy_commit,
        "fixed_revision_metadata": candidate.fixed_revision,
        "fixed_commit_full": fixed_commit,
        "fix_content_inspected": False,
        "repair_history_inspected": False,
        "oracle_executed": False,
    }
    acquisition_evidence["acquisition_evidence_sha256"] = sha256_bytes(
        canonical_json_bytes(acquisition_evidence)
    )
    _atomic_write_json(preparation_root / "acquisition_evidence.json", acquisition_evidence)
    verified_at = utc_now()
    event_name = re.sub(r"[^0-9A-Za-z]+", "-", verified_at).strip("-") + ".json"
    _atomic_write_json(
        preparation_root / "acquisition_events" / event_name,
        {
            "schema_version": 1,
            "event": "SUBJECT_IDENTITIES_VERIFIED",
            "verified_at_utc": verified_at,
            "acquisition_evidence_sha256": acquisition_evidence["acquisition_evidence_sha256"],
            "oracle_executed": False,
        },
    )
    return {
        field: (
            "true"
            if plan.get(field) is True
            else "false"
            if plan.get(field) is False
            else json.dumps(plan[field], ensure_ascii=False, separators=(",", ":"))
            if field == "oracle_commands"
            else str(plan.get(field, ""))
        )
        for field in PLAN_FIELDS
    }


def write_execution_plan_csv(path: Path, rows: Sequence[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=PLAN_FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        temporary_path.replace(path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def prepare_all(
    *,
    benchmark_root: Path,
    bugsinpy_root: Path,
    external_root: Path,
    output_csv: Path,
    allow_network: bool,
) -> list[dict[str, str]]:
    validate_controlling_inputs(benchmark_root)
    validate_bugsinpy_checkout(bugsinpy_root)
    candidates = load_frozen_candidates(benchmark_root)
    validate_frozen_order_against_spec(candidates, benchmark_root / "SCREENING_SPEC_V1.md")
    external_root.mkdir(parents=True, exist_ok=True)
    project_inputs: dict[str, str] = {}
    for candidate in candidates:
        previous = project_inputs.setdefault(candidate.project, candidate.source_url)
        if not _remote_urls_match(previous, candidate.source_url):
            raise PreparationError(f"multiple source URLs declared for project {candidate.project}")
    mirrors = {
        project: acquire_project_mirror(
            project,
            url,
            external_root / "subject_repositories",
            allow_network=allow_network,
        )
        for project, url in sorted(project_inputs.items())
    }
    rows: list[dict[str, str]] = []
    errors: list[str] = []
    for candidate in candidates:
        try:
            rows.append(
                prepare_case(
                    candidate,
                    bugsinpy_root=bugsinpy_root,
                    external_root=external_root,
                    mirror=mirrors[candidate.project],
                )
            )
        except PreparationError as exc:
            errors.append(f"{candidate.selection_order}:{candidate.canonical_case_id}:{exc}")
    if errors:
        raise PreparationError("preparation blocked:\n" + "\n".join(errors))
    if len(rows) != INITIAL_CASE_COUNT:
        raise PreparationError(f"expected 40 plan rows, built {len(rows)}")
    write_execution_plan_csv(output_csv, rows)
    return rows


def regenerate_csv_from_preserved_preparations(
    benchmark_root: Path, bugsinpy_root: Path, external_root: Path, output_csv: Path
) -> list[dict[str, str]]:
    """Regenerate only the repo CSV from hash-verified existing preparation evidence.

    This transaction does not rewrite external per-case preparation or acquire any
    subject content. A later authorized preparation must issue v1.1 case JSON.
    """
    validate_controlling_inputs(benchmark_root)
    validate_bugsinpy_checkout(bugsinpy_root)
    candidates = load_frozen_candidates(benchmark_root)
    validate_frozen_order_against_spec(candidates, benchmark_root / "SCREENING_SPEC_V1.md")
    rows: list[dict[str, str]] = []
    for candidate in candidates:
        case_root = external_root / "screening_workspaces" / safe_case_slug(
            candidate.canonical_case_id
        )
        plan = _load_json(case_root / "preparation" / "execution_plan.json")
        if deterministic_plan_hash(plan) != plan.get("execution_plan_sha256"):
            raise PreparationError(f"stale plan hash: {candidate.canonical_case_id}")
        if plan.get("canonical_case_id") != candidate.canonical_case_id or plan.get(
            "initial_selection_order"
        ) != candidate.selection_order:
            raise PreparationError(f"frozen candidate mismatch: {candidate.canonical_case_id}")
        preserved = (case_root / "preparation" / "oracle" / "run_test.sh").read_bytes()
        source = (bugsinpy_root / "projects" / candidate.project / "bugs" / candidate.bug_id
                  / "run_test.sh").read_bytes()
        if preserved != source or sha256_bytes(preserved) != plan.get("oracle_script_sha256"):
            raise PreparationError(f"oracle source mismatch: {candidate.canonical_case_id}")
        oracle = analyze_oracle(preserved)
        old_status = plan.get("oracle_plan_status")
        if old_status not in {"RESOLVED_SINGLE_COMMAND", "UNRESOLVED_MULTIPLE_SUBSTANTIVE_COMMANDS"}:
            raise PreparationError(f"unexpected prior oracle status: {candidate.canonical_case_id}")
        if old_status == "RESOLVED_SINGLE_COMMAND" and plan.get("oracle_commands") != oracle[
            "commands"
        ]:
            raise PreparationError(f"single-command drift: {candidate.canonical_case_id}")
        prior_reason = plan.get("blocking_reason", "")
        if old_status == "UNRESOLVED_MULTIPLE_SUBSTANTIVE_COMMANDS":
            expected_reason = f"run_test.sh contains {len(oracle['commands'])} substantive commands"
            if prior_reason != expected_reason:
                raise PreparationError(f"additional old blocker: {candidate.canonical_case_id}")
            prior_reason = ""
        if oracle["blocking_reason"]:
            prior_reason = "; ".join(filter(None, (prior_reason, oracle["blocking_reason"])))
        plan.update({
            "schema_version": "1.1",
            "oracle_representation_version": "COMPOSITE_ORACLE_SEMANTICS_V1",
            "oracle_command": oracle["oracle_command"],
            "oracle_commands": oracle["commands"],
            "oracle_command_count": len(oracle["commands"]),
            "oracle_plan_status": oracle["status"],
            "oracle_shell_requirement": oracle["shell_requirement"],
            "blocking_reason": prior_reason,
            "screening_ready": not prior_reason and plan.get("protected_manifest_status") == "RESOLVED"
            and plan.get("environment_plan_status") == "PLAN_FROZEN_BUILD_REQUIRED",
            "pre_execution_timeout_gate": "PRE_EXECUTION_TIMEOUT_GATE_REQUIRED",
        })
        plan["execution_plan_sha256"] = deterministic_plan_hash(plan)
        rows.append({
            field: json.dumps(plan[field], ensure_ascii=False, separators=(",", ":"))
            if field == "oracle_commands" else "true" if plan.get(field) is True
            else "false" if plan.get(field) is False else str(plan.get(field, ""))
            for field in PLAN_FIELDS
        })
    write_execution_plan_csv(output_csv, rows)
    return rows


def build_execution_schedule() -> tuple[ScheduledRun, ...]:
    return tuple(
        ScheduledRun(revision_label=revision, ordinal=ordinal)
        for revision in ("BUGGY", "FIXED")
        for ordinal in (1, 2, 3)
    )


def deterministic_trial_evidence_hash(evidence: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes({
        key: value for key, value in evidence.items() if key != "trial_evidence_sha256"
    }))


def classify_trial_commands(records: Sequence[dict[str, Any]], command_count: int) -> str:
    if any(record.get("state") == "INTERRUPTED" for record in records):
        return "INTERRUPTED_NOT_ELIGIBILITY"
    if any(record.get("state") == "INFRASTRUCTURE_ERROR" for record in records):
        return "INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY"
    if len(records) != command_count or command_count < 1:
        return "INCOMPLETE_NOT_ELIGIBILITY"
    if [record.get("command_ordinal") for record in records] != list(range(1, command_count + 1)):
        return "CASE_INVALIDATED"
    if any(record.get("state") != "ORACLE_COMPLETED" for record in records):
        return "CASE_INVALIDATED"
    required = {
        "command", "command_sha256", "cwd", "started_at_utc", "ended_at_utc",
        "wall_time_seconds", "stdout_artifact", "stderr_artifact", "stdout_sha256",
        "stderr_sha256", "exit_code", "protected_integrity",
    }
    if any(not required.issubset(record) for record in records):
        return "CASE_INVALIDATED"
    if any(record["command_sha256"] != sha256_bytes(record["command"].encode("utf-8"))
           for record in records):
        return "CASE_INVALIDATED"
    if any(record.get("protected_integrity") is not True for record in records):
        return "CASE_INVALIDATED"
    codes = [record.get("exit_code") for record in records]
    if any(type(code) is not int for code in codes):
        return "CASE_INVALIDATED"
    return "TRIAL_PASS" if all(code == 0 for code in codes) else "TRIAL_FAIL"


def run_ordered_subcommands(
    commands: Sequence[str], runner: Callable[[int, str], dict[str, Any]]
) -> list[dict[str, Any]]:
    """Run every command after nonzero exits; infrastructure faults stop the trial."""
    records: list[dict[str, Any]] = []
    for ordinal, command in enumerate(commands, 1):
        try:
            record = runner(ordinal, command)
        except InfrastructureFailure as exc:
            records.append({
                "command_ordinal": ordinal,
                "command": command,
                "command_sha256": sha256_bytes(command.encode("utf-8")),
                "state": "INFRASTRUCTURE_ERROR",
                "detail": str(exc),
            })
            break
        records.append(record)
        if record.get("state") != "ORACLE_COMPLETED" or record.get("protected_integrity") is not True:
            break
    return records


def classify_execution_records(records: Sequence[dict[str, Any]]) -> str:
    if any(record.get("state") == "INTERRUPTED" for record in records):
        return "INTERRUPTED_NOT_ELIGIBILITY"
    if len(records) != 6:
        return "INCOMPLETE_NOT_ELIGIBILITY"
    if any(record.get("state") == "INFRASTRUCTURE_ERROR" for record in records):
        return "INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY"
    expected = [(item.revision_label, item.ordinal) for item in build_execution_schedule()]
    actual = [(record.get("revision_label"), record.get("ordinal")) for record in records]
    if actual != expected:
        return "CASE_INVALIDATED"
    if any(record.get("trial_result") == "INTERRUPTED_NOT_ELIGIBILITY" for record in records):
        return "INTERRUPTED_NOT_ELIGIBILITY"
    if any(record.get("trial_result") == "INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY"
           for record in records):
        return "INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY"
    if any(record.get("trial_result") not in {"TRIAL_PASS", "TRIAL_FAIL"} for record in records):
        return "CASE_INVALIDATED"
    if all(record["trial_result"] == "TRIAL_FAIL" for record in records[:3]) and all(
        record["trial_result"] == "TRIAL_PASS" for record in records[3:]
    ):
        return "ELIGIBLE"
    return "INELIGIBLE_REPRODUCIBILITY_OUTCOME"


def execute_schedule_without_early_stop(
    runner: Callable[[ScheduledRun], dict[str, Any]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for scheduled in build_execution_schedule():
        try:
            record = runner(scheduled)
        except InfrastructureFailure as exc:
            record = {
                "revision_label": scheduled.revision_label,
                "ordinal": scheduled.ordinal,
                "state": "INFRASTRUCTURE_ERROR",
                "detail": str(exc),
            }
        records.append(record)
    return records


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InfrastructureFailure(f"cannot load JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise InfrastructureFailure(f"expected JSON object: {path}")
    return value


def environment_tree_manifest_sha256(root: Path) -> str:
    if not root.is_dir():
        raise InfrastructureFailure(f"environment root is not a directory: {root}")
    entries: list[dict[str, Any]] = []
    paths = [root, *sorted(root.rglob("*"), key=lambda path: path.relative_to(root).as_posix())]
    for path in paths:
        relative = "." if path == root else path.relative_to(root).as_posix()
        metadata = path.lstat()
        item: dict[str, Any] = {
            "path": relative,
            "mode": f"{stat.S_IMODE(metadata.st_mode):04o}",
        }
        if path.is_symlink():
            item.update({"type": "symlink", "target": os.readlink(path)})
        elif path.is_dir():
            item["type"] = "directory"
        elif path.is_file():
            item.update({"type": "file", "sha256": sha256_file(path)})
        else:
            raise InfrastructureFailure(f"unsupported environment item type: {path}")
        entries.append(item)
    return sha256_bytes(canonical_json_bytes(entries))


def _assert_read_only_tree(root: Path) -> None:
    for path in [root, *root.rglob("*")]:
        if path.is_symlink():
            continue
        if stat.S_IMODE(path.lstat().st_mode) & 0o222:
            raise InfrastructureFailure(f"environment item is writable: {path}")


def _validate_environment_identity(
    identity_path: Path, plan: dict[str, Any], external_root: Path
) -> dict[str, Any]:
    identity = _load_json(identity_path)
    if identity.get("canonical_case_id") != plan["canonical_case_id"]:
        raise InfrastructureFailure("environment identity case mismatch")
    if identity.get("execution_plan_sha256") != plan["execution_plan_sha256"]:
        raise InfrastructureFailure("environment identity plan mismatch")
    required = {
        "platform_identity",
        "python_artifact_sha256",
        "python_executable_sha256",
        "dependency_input_sha256",
        "installed_distribution_manifest_sha256",
        "system_dependency_manifest_sha256",
        "setup_evidence_sha256",
        "environment_tree_manifest_sha256",
        "environment_root",
        "environment_bin_dir",
        "read_only_content_addressed",
    }
    missing = sorted(key for key in required if not identity.get(key))
    if missing:
        raise InfrastructureFailure(f"environment identity fields missing: {','.join(missing)}")
    if identity["read_only_content_addressed"] is not True:
        raise InfrastructureFailure("environment is not declared read-only/content-addressed")
    environment_root = Path(identity["environment_root"]).resolve()
    environment_bin = Path(identity["environment_bin_dir"]).resolve()
    try:
        environment_root.relative_to(external_root.resolve())
        environment_bin.relative_to(environment_root)
    except ValueError as exc:
        raise InfrastructureFailure("environment paths escape the external case root") from exc
    if not environment_root.is_dir():
        raise InfrastructureFailure(f"environment root missing: {environment_root}")
    if not environment_bin.is_dir():
        raise InfrastructureFailure(f"environment bin directory missing: {environment_bin}")
    actual_tree_hash = environment_tree_manifest_sha256(environment_root)
    if actual_tree_hash != identity["environment_tree_manifest_sha256"]:
        raise InfrastructureFailure("environment tree manifest mismatch")
    _assert_read_only_tree(environment_root)
    return identity


def _verify_protected_paths(
    workspace: Path, manifest: dict[str, Any], revision_label: str
) -> tuple[bool, list[str]]:
    failures: list[str] = []
    key = "buggy_effective_sha256" if revision_label == "BUGGY" else "fixed_sha256"
    for entry in manifest.get("entries", []):
        path = workspace / entry["path"]
        expected = entry.get(key, "")
        if not path.is_file():
            failures.append(f"missing:{entry['path']}")
        elif not expected or sha256_file(path) != expected:
            failures.append(f"hash:{entry['path']}")
    return not failures, failures


def _inject_benchmark_owned_tests(
    workspace: Path,
    mirror: Path,
    manifest: dict[str, Any],
    revision_label: str,
    fixed_commit: str,
) -> None:
    if revision_label != "BUGGY":
        return
    for entry in manifest.get("entries", []):
        if not entry.get("buggy_test_injection_from_fixed"):
            continue
        destination = workspace / _safe_subject_path(entry["path"])
        result = _git(
            mirror,
            "cat-file",
            "blob",
            f"{fixed_commit}:{entry['path']}",
            text=False,
        )
        if sha256_bytes(result.stdout) != entry["buggy_effective_sha256"]:
            raise InfrastructureFailure(f"benchmark-owned test identity mismatch: {entry['path']}")
        _atomic_write_bytes(destination, result.stdout)


def _execute_one_run(
    scheduled: ScheduledRun,
    *,
    plan: dict[str, Any],
    manifest: dict[str, Any],
    environment_identity: dict[str, Any],
    run_root: Path,
) -> dict[str, Any]:
    revision_key = f"{scheduled.revision_label.lower()}_commit_full"
    revision_sha = plan[revision_key]
    workspace = run_root / "workspace"
    run_root.mkdir(parents=True, exist_ok=False)
    preparation_started = utc_now()
    trial_monotonic_start: float | None = None
    record: dict[str, Any] = {
        "revision_label": scheduled.revision_label,
        "ordinal": scheduled.ordinal,
        "revision_sha": revision_sha,
        "oracle_commands": plan["oracle_commands"],
        "cwd": str(workspace),
        "environment_identity_sha256": sha256_bytes(canonical_json_bytes(environment_identity)),
        "preparation_started_at_utc": preparation_started,
        "combined_output_available": False,
    }
    try:
        _run(
            (
                "git",
                "clone",
                "--no-checkout",
                "--shared",
                plan["subject_mirror_path"],
                str(workspace),
            )
        )
        _git(workspace, "checkout", "--detach", revision_sha)
        clean = _git(workspace, "status", "--porcelain").stdout.strip()
        if clean:
            raise InfrastructureFailure("fresh screening workspace is not clean")
        _inject_benchmark_owned_tests(
            workspace,
            Path(plan["subject_mirror_path"]),
            manifest,
            scheduled.revision_label,
            plan["fixed_commit_full"],
        )
        pre_ok, pre_failures = _verify_protected_paths(
            workspace, manifest, scheduled.revision_label
        )
        if not pre_ok:
            raise InfrastructureFailure(
                "pre-run protected manifest mismatch: " + ",".join(pre_failures)
            )
        environment = os.environ.copy()
        ephemeral_root = run_root / "ephemeral"
        for name in ("home", "tmp", "cache"):
            (ephemeral_root / name).mkdir(parents=True, exist_ok=True)
        for name in ("PYTHONHOME", "PYTHONPATH", "CONDA_PREFIX", "CONDA_DEFAULT_ENV"):
            environment.pop(name, None)
        environment["PATH"] = os.pathsep.join(
            (str(environment_identity["environment_bin_dir"]), "/usr/bin", "/bin")
        )
        environment["VIRTUAL_ENV"] = str(environment_identity["environment_root"])
        environment["HOME"] = str(ephemeral_root / "home")
        environment["TMPDIR"] = str(ephemeral_root / "tmp")
        environment["XDG_CACHE_HOME"] = str(ephemeral_root / "cache")
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        trial_monotonic_start = time.monotonic()
        trial_deadline = trial_monotonic_start + TRIAL_TIMEOUT_SECONDS
        record["started_at_utc"] = utc_now()
        raw_streams: dict[int, tuple[bytes, bytes]] = {}

        def run_command(command_ordinal: int, command: str) -> dict[str, Any]:
            command_root = run_root / "subcommands" / f"{command_ordinal:02d}"
            started_at = utc_now()
            command_start = time.monotonic()
            subrecord: dict[str, Any] = {
                "command_ordinal": command_ordinal,
                "command": command,
                "command_sha256": sha256_bytes(command.encode("utf-8")),
                "cwd": str(workspace),
                "started_at_utc": started_at,
                "stdout_artifact": str(command_root / "stdout.raw"),
                "stderr_artifact": str(command_root / "stderr.raw"),
            }
            try:
                remaining = trial_deadline - time.monotonic()
                timeout_subreason = (
                    "ORACLE_TRIAL_TIMEOUT" if remaining < SUBCOMMAND_TIMEOUT_SECONDS
                    else "ORACLE_SUBCOMMAND_TIMEOUT"
                )
                completed = run_oracle_process(
                    parse_recognized_command(command),
                    cwd=workspace,
                    env=environment,
                    timeout_seconds=min(SUBCOMMAND_TIMEOUT_SECONDS, remaining),
                    timeout_subreason=timeout_subreason,
                )
                raw_streams[command_ordinal] = (completed.stdout, completed.stderr)
                if time.monotonic() >= trial_deadline:
                    raise OracleTimeout("ORACLE_TRIAL_TIMEOUT", completed.stdout, completed.stderr)
                post_ok, post_failures = _verify_protected_paths(
                    workspace, manifest, scheduled.revision_label
                )
                post_environment_hash = environment_tree_manifest_sha256(
                    Path(environment_identity["environment_root"])
                )
                subrecord.update({
                    "state": "ORACLE_COMPLETED" if completed.returncode >= 0 else "INTERRUPTED",
                    "exit_code": completed.returncode,
                    "protected_integrity": post_ok,
                    "protected_integrity_failures": post_failures,
                })
                if post_environment_hash != environment_identity["environment_tree_manifest_sha256"]:
                    subrecord["state"] = "INFRASTRUCTURE_ERROR"
                    subrecord["detail"] = "oracle mutated the read-only environment identity"
            except OracleTimeout as exc:
                raw_streams[command_ordinal] = (exc.stdout, exc.stderr)
                subrecord.update({
                    "state": "INFRASTRUCTURE_ERROR",
                    "infrastructure_reason": "OTHER_INFRASTRUCTURE_FAILURE",
                    "infrastructure_subreason": exc.subreason,
                    "detail": str(exc),
                })
            except Exception as exc:
                subrecord["state"] = "INFRASTRUCTURE_ERROR"
                subrecord["detail"] = str(exc)
            finally:
                subrecord["ended_at_utc"] = utc_now()
                subrecord["wall_time_seconds"] = round(time.monotonic() - command_start, 9)
            return subrecord

        subcommands = run_ordered_subcommands(plan["oracle_commands"], run_command)
        record["trial_stopped_at_utc"] = utc_now()
        record["trial_wall_time_seconds"] = round(time.monotonic() - trial_monotonic_start, 9)
        if record["trial_wall_time_seconds"] >= TRIAL_TIMEOUT_SECONDS and subcommands:
            last = subcommands[-1]
            if last.get("state") == "ORACLE_COMPLETED":
                last.update({
                    "state": "INFRASTRUCTURE_ERROR",
                    "infrastructure_reason": "OTHER_INFRASTRUCTURE_FAILURE",
                    "infrastructure_subreason": "ORACLE_TRIAL_TIMEOUT",
                })
        for item in subcommands:
            ordinal = item["command_ordinal"]
            if ordinal in raw_streams:
                stdout, stderr = raw_streams[ordinal]
                command_root = run_root / "subcommands" / f"{ordinal:02d}"
                _atomic_write_bytes(command_root / "stdout.raw", stdout)
                _atomic_write_bytes(command_root / "stderr.raw", stderr)
                item["stdout_sha256"] = sha256_bytes(stdout)
                item["stderr_sha256"] = sha256_bytes(stderr)
        trial_result = classify_trial_commands(subcommands, plan["oracle_command_count"])
        trial_evidence = {
            "oracle_commands": plan["oracle_commands"],
            "exit_codes": [item.get("exit_code") for item in subcommands],
            "subcommand_artifacts": [
                {"stdout": item.get("stdout_artifact"), "stderr": item.get("stderr_artifact")}
                for item in subcommands
            ],
            "subcommands": subcommands,
            "trial_result": trial_result,
            "infrastructure_subreason": next(
                (item["infrastructure_subreason"] for item in subcommands
                 if "infrastructure_subreason" in item), None
            ),
        }
        trial_evidence["trial_evidence_sha256"] = deterministic_trial_evidence_hash(trial_evidence)
        _atomic_write_json(run_root / "trial_evidence.json", trial_evidence)
        record.update(
            {
                "state": "ORACLE_COMPLETED" if trial_result in {"TRIAL_PASS", "TRIAL_FAIL"}
                else "INFRASTRUCTURE_ERROR" if trial_result == "INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY"
                else "INTERRUPTED" if trial_result == "INTERRUPTED_NOT_ELIGIBILITY"
                else "CASE_INVALIDATED",
                "trial_result": trial_result,
                "infrastructure_subreason": trial_evidence["infrastructure_subreason"],
                "exit_codes": trial_evidence["exit_codes"],
                "subcommand_artifacts": trial_evidence["subcommand_artifacts"],
                "trial_evidence_sha256": trial_evidence["trial_evidence_sha256"],
            }
        )
    except InfrastructureFailure:
        raise
    except Exception as exc:
        raise InfrastructureFailure(str(exc)) from exc
    finally:
        record["ended_at_utc"] = utc_now()
        if trial_monotonic_start is not None:
            record["wall_time_seconds"] = record.get("trial_wall_time_seconds", round(
                time.monotonic() - trial_monotonic_start, 9
            ))
    return record


def execute_case(
    *,
    case_root: Path,
    external_root: Path,
    execution_id: str,
    authorization: str,
    recorded_rerun_reason: str,
) -> str:
    if authorization != EXECUTION_AUTHORITY_TOKEN:
        raise InfrastructureFailure("exact execution authority token is required")
    if PRE_EXECUTION_TIMEOUT_GATE_REQUIRED:
        raise InfrastructureFailure("PRE_EXECUTION_TIMEOUT_GATE_REQUIRED")
    if not PRODUCTION_DOCKER_BACKEND_IMPLEMENTED:
        raise InfrastructureFailure("PRODUCTION_DOCKER_BACKEND_NOT_IMPLEMENTED")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", execution_id):
        raise InfrastructureFailure(
            "execution id must use only letters, digits, dot, underscore, dash"
        )
    plan_path = case_root / "preparation" / "execution_plan.json"
    manifest_path = case_root / "preparation" / "protected_manifest.json"
    plan = _load_json(plan_path)
    if deterministic_plan_hash(plan) != plan.get("execution_plan_sha256"):
        raise InfrastructureFailure("execution plan hash mismatch")
    if not plan.get("screening_ready"):
        raise InfrastructureFailure(f"case is not screening-ready: {plan.get('blocking_reason')}")
    if plan.get("oracle_plan_status") != "RESOLVED_ORDERED_COMMANDS":
        raise InfrastructureFailure("oracle plan is unresolved")
    script_bytes = (case_root / "preparation" / "oracle" / "run_test.sh").read_bytes()
    if sha256_bytes(script_bytes) != plan.get("oracle_script_sha256"):
        raise InfrastructureFailure("preserved run_test.sh hash mismatch")
    oracle = analyze_oracle(script_bytes)
    if oracle["status"] != "RESOLVED_ORDERED_COMMANDS" or oracle["commands"] != plan.get(
        "oracle_commands"
    ) or len(oracle["commands"]) != plan.get("oracle_command_count"):
        raise InfrastructureFailure("ordered oracle vector does not match preserved run_test.sh")
    manifest = _load_json(manifest_path)
    environment_identity = _validate_environment_identity(
        case_root / "environment" / "environment_identity.json", plan, external_root
    )
    evidence_parent = (
        external_root / "screening_evidence" / safe_case_slug(plan["canonical_case_id"])
    )
    prior_attempts = list(evidence_parent.iterdir()) if evidence_parent.is_dir() else []
    if prior_attempts and not recorded_rerun_reason.strip():
        raise InfrastructureFailure("recorded rerun reason required because prior evidence exists")
    attempt_root = evidence_parent / execution_id
    attempt_root.mkdir(parents=True, exist_ok=False)
    checkpoint_path = attempt_root / "checkpoint.json"
    checkpoint: dict[str, Any] = {
        "schema_version": 1,
        "canonical_case_id": plan["canonical_case_id"],
        "execution_id": execution_id,
        "execution_plan_sha256": plan["execution_plan_sha256"],
        "authority_token_sha256": sha256_bytes(authorization.encode("utf-8")),
        "recorded_rerun_reason": recorded_rerun_reason,
        "state": "STARTED",
        "classification": "INCOMPLETE_NOT_ELIGIBILITY",
        "schedule": [
            {"revision_label": item.revision_label, "ordinal": item.ordinal, "state": "PENDING"}
            for item in build_execution_schedule()
        ],
        "records": [],
        "started_at_utc": utc_now(),
    }
    _atomic_write_json(checkpoint_path, checkpoint)

    def runner(item: ScheduledRun) -> dict[str, Any]:
        index = build_execution_schedule().index(item)
        run_root = (
            attempt_root / "runs" / f"{index + 1:02d}-{item.revision_label.lower()}-{item.ordinal}"
        )
        try:
            record = _execute_one_run(
                item,
                plan=plan,
                manifest=manifest,
                environment_identity=environment_identity,
                run_root=run_root,
            )
        except InfrastructureFailure as exc:
            record = {
                "revision_label": item.revision_label,
                "ordinal": item.ordinal,
                "state": "INFRASTRUCTURE_ERROR",
                "detail": str(exc),
            }
        checkpoint["records"].append(record)
        checkpoint["schedule"][index]["state"] = record["state"]
        checkpoint["classification"] = classify_execution_records(checkpoint["records"])
        _atomic_write_json(checkpoint_path, checkpoint)
        return record

    try:
        records = execute_schedule_without_early_stop(runner)
        checkpoint["records"] = records
        for index, record in enumerate(records):
            checkpoint["schedule"][index]["state"] = record["state"]
        checkpoint["state"] = "COMPLETE"
        checkpoint["classification"] = classify_execution_records(records)
        checkpoint["ended_at_utc"] = utc_now()
        _atomic_write_json(checkpoint_path, checkpoint)
        return checkpoint["classification"]
    except BaseException:
        checkpoint["state"] = "INTERRUPTED"
        checkpoint["classification"] = "INTERRUPTED_NOT_ELIGIBILITY"
        checkpoint["ended_at_utc"] = utc_now()
        _atomic_write_json(checkpoint_path, checkpoint)
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="subcommand")
    prepare_parser = subparsers.add_parser("prepare", help="prepare only; never run an oracle")
    prepare_parser.add_argument("--benchmark-root", type=Path, required=True)
    prepare_parser.add_argument("--bugsinpy-root", type=Path, required=True)
    prepare_parser.add_argument("--external-root", type=Path, required=True)
    prepare_parser.add_argument("--output-csv", type=Path, required=True)
    prepare_parser.add_argument("--allow-network-acquisition", action="store_true")

    execute_parser = subparsers.add_parser(
        "execute", help="future gated oracle execution; not authorized by preparation"
    )
    execute_parser.add_argument("--case-root", type=Path, required=True)
    execute_parser.add_argument("--external-root", type=Path, required=True)
    execute_parser.add_argument("--execution-id", required=True)
    execute_parser.add_argument("--authorization", required=True)
    execute_parser.add_argument("--recorded-rerun-reason", default="")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    if arguments.subcommand is None:
        parser.print_help()
        return 2
    try:
        if arguments.subcommand == "prepare":
            rows = prepare_all(
                benchmark_root=arguments.benchmark_root,
                bugsinpy_root=arguments.bugsinpy_root,
                external_root=arguments.external_root,
                output_csv=arguments.output_csv,
                allow_network=arguments.allow_network_acquisition,
            )
            ready = sum(row["screening_ready"] == "true" for row in rows)
            print(f"prepared {len(rows)} rows; screening_ready={ready}; oracle executions=0")
            return 0
        if arguments.subcommand == "execute":
            classification = execute_case(
                case_root=arguments.case_root,
                external_root=arguments.external_root,
                execution_id=arguments.execution_id,
                authorization=arguments.authorization,
                recorded_rerun_reason=arguments.recorded_rerun_reason,
            )
            print(classification)
            return 0
    except (PreparationError, InfrastructureFailure) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 1
    raise AssertionError(f"unhandled subcommand: {arguments.subcommand}")


if __name__ == "__main__":
    raise SystemExit(main())

"""Fail-closed Docker environment materializer with a gated production path.

The shared build engine is exercised only with checked synthetic fixtures in v1.
No import, bare invocation, validate, or plan operation starts Docker builds.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shlex
import shutil
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
REAL_MATERIALIZATION_ENABLED = True  # Each real batch still needs separate Human-PI authority.
MATERIALIZER_VERSION = "ENVIRONMENT_MATERIALIZER_V1_1"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")
SAFE_NAME = re.compile(r"[A-Za-z0-9_.-]+\Z")
FORBIDDEN_SNAPSHOT_NAMES = {".git", "bug_patch.txt", "screening_evidence", "bug.info", "project.info"}


class Blocked(ValueError):
    def __init__(self, status: str, message: str) -> None:
        super().__init__(message)
        self.status = status


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


def snapshot_manifest(source: Path) -> tuple[dict[str, Any], str]:
    if not source.is_dir() or source.is_symlink():
        raise Blocked("BLOCKED_INPUT_IDENTITY", "explicit source snapshot directory required")
    entries: list[dict[str, Any]] = []
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if any(part in FORBIDDEN_SNAPSHOT_NAMES for part in relative.parts):
            raise Blocked("BLOCKED_INPUT_IDENTITY", "source snapshot includes forbidden metadata/history")
        if path.is_symlink():
            raise Blocked("BLOCKED_INPUT_IDENTITY", "source snapshot symlink refused")
        if path.is_file():
            entries.append({"path": relative.as_posix(), "sha256": sha256(path.read_bytes()),
                            "mode": path.stat().st_mode & 0o777})
        elif not path.is_dir():
            raise Blocked("BLOCKED_INPUT_IDENTITY", "source snapshot special file refused")
    manifest = {"schema": "SOURCE_SNAPSHOT_MANIFEST_V1", "files": entries}
    return manifest, sha256(canonical_json(manifest))


def context_manifest(context: Path) -> tuple[dict[str, Any], str]:
    entries = [{"path": p.relative_to(context).as_posix(), "sha256": sha256(p.read_bytes())}
               for p in sorted(context.rglob("*")) if p.is_file()]
    manifest = {"schema": "BUILD_CONTEXT_MANIFEST_V1", "files": entries}
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
    code = ("import importlib.metadata,json; "
            "print(json.dumps(sorted([(d.metadata.get('Name',''),d.version) "
            "for d in importlib.metadata.distributions()])))")
    distributions = docker(["run", "--rm", f"--platform={PLATFORM}", "--network=none",
                            "--read-only", "--tmpfs", "/tmp", image_id, "python", "-c", code])
    packages = docker(["run", "--rm", f"--platform={PLATFORM}", "--network=none",
                       "--read-only", "--tmpfs", "/tmp", image_id, "dpkg-query", "-W",
                       "-f=${Package} ${Version}\\n"])
    if distributions.returncode or packages.returncode:
        raise Blocked("BLOCKED_RUNTIME_IDENTITY", "package manifest observation failed")
    layers = observed.get("RootFS", {}).get("Layers")
    if not layers or not all(DIGEST.fullmatch(x) for x in layers):
        raise Blocked("BLOCKED_RUNTIME_IDENTITY", "RootFS layer identity unavailable")
    return {"inspect": observed, "inspect_raw": result.stdout, "python": python,
            "distributions": distributions.stdout, "system_packages": packages.stdout,
            "layers": layers}


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
                         synthetic_only: bool) -> dict[str, Any]:
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
        if mode == "SOURCE_INDEPENDENT_ENVIRONMENT":
            if revisions != [{"label": "SOURCE_INDEPENDENT", "sha": "ABSENT"}]:
                raise Blocked("BLOCKED_INPUT_IDENTITY", "source-independent fixture has source")
        elif mode == "REVISION_SPECIFIC_BUILD_REQUIRED":
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
        base_probe = verify_base(recipe)
        record["base_python_probe"] = base_probe
        record["build_recipe_sha256"] = recipe_hash(recipe)
        record["revisions"] = []
        for revision in revisions:
            label, source_name = revision["label"], revision.get("source")
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
                shutil.copytree(source, context / "source")
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
            (revision_dir / "system_packages.txt").write_bytes(observations["system_packages"])
            metadata_files = [p for p in (context / "source" / "setup.py",
                                         context / "source" / "setup.cfg",
                                         context / "source" / "pyproject.toml") if p.is_file()]
            packaging_hash = sha256(canonical_json([
                {"path": p.name, "sha256": sha256(p.read_bytes())} for p in metadata_files
            ])) if source is not None else "ABSENT"
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
                "system_package_manifest_sha256": sha256(observations["system_packages"]),
                "environment_identity_sha256": sha256(identity_bytes),
            })
        record["status"] = "MATERIALIZED"
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
    args = parser.parse_args(argv)
    if args.mode is None:
        parser.print_help()
        return 2
    try:
        recipes = check_frozen_ledger()
        if args.mode == "validate":
            print("40 frozen ready recipes verified; all UNBUILT")
        elif args.mode == "plan":
            print(json.dumps({"cases": len(recipes), "source_independent": 26,
                              "revision_specific": 14, "materialized": 0}, sort_keys=True))
        elif args.mode == "materialize":
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
    except Blocked as exc:
        print(f"{exc.status}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

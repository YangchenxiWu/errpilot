"""Inert, deterministic BugsInPy environment recipe construction.

This module only reads frozen metadata and writes derived data. It has no build,
install, subject import, test, or oracle execution path.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from .audit_environment import classify_setup_line


SCHEMA = "ENVIRONMENT_BUILD_RECIPE_V1"
FROZEN_SHA256 = {
    "PROTOCOL.md": "34e014a07821dc9dca52178874eef0b847aee7f048071fb4920864ae5d3bee93",
    "RUN_SPEC_V1.md": "29ab6f78739d0eeea1c2a774e62e2d133f173e160c3d247407970a80726f4406",
    "SCREENING_SPEC_V1.md": "a7f3cd5e73d6c733f560456d9f3949be18deca9b295ffb4ef2ae087af7e89db3",
    "ORACLE_REPRESENTATION_V1.md": "625b656495b5f1174ea1f4a07f872a42112a0be839b47c3db884dcd103a87f52",
    "SCREENING_RUNTIME_V1.md": "235b404dd32da91f28c303922ce7acfc8f58611cd78f3c365d583cb2572bb41f",
    "candidate_universe.csv": "78208adf610a50542be6dfbd03a9b25960ba0b5cfc80768b08ffe7a4c78f3b8c",
    "screening_execution_plan.csv": "95874a88a7ad54a976ef70db1e4cebc2fe8f9be7f72c7551ce8c00dfa17d25ea",
}
ALLOWED_SETUP = {
    "DEPENDENCY_INSTALL", "PROJECT_INSTALL_OR_BUILD",
    "ENVIRONMENT_CONFIGURATION", "FILESYSTEM_PREPARATION",
}
RECIPE_FIELDS = (
    "initial_selection_order", "canonical_case_id", "python_version",
    "base_image_digest", "base_runtime_probe_status", "python_observed_version",
    "python_executable_sha256", "requirements_raw_sha256", "requirements_encoding",
    "requirements_normalized_sha256", "dependency_input_sha256",
    "self_reference_count", "self_reference_ledger_sha256", "setup_sha256",
    "setup_action_count", "setup_action_ledger_sha256", "environment_mode_v2",
    "build_recipe_sha256", "build_recipe_status", "blocking_reason", "build_recipe_json",
)
NORMALIZATION_FIELDS = (
    "initial_selection_order", "canonical_case_id", "requirements_encoding",
    "requirements_raw_sha256", "requirements_normalized_sha256",
    "dependency_input_sha256", "normalized_path", "dependency_input_path",
    "self_reference_count", "normalization_status",
)
SELF_FIELDS = (
    "canonical_case_id", "original_line_ordinal", "exact_original_text",
    "classification", "evidence", "original_line_sha256",
)


class RecipeError(ValueError):
    """An input cannot be transformed without guessing."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def normalize_requirements(raw: bytes) -> tuple[bytes, str]:
    """Decode strictly and normalize line endings only; preserve the last newline."""
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        text, encoding = raw.decode("utf-16", errors="strict"), "UTF-16_WITH_BOM"
    else:
        text, encoding = raw.decode("utf-8", errors="strict"), "UTF-8"
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"), encoding


def _canonical_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _repository_identity(url: str) -> tuple[str, str]:
    parsed = urlsplit(url)
    path = parsed.path.rstrip("/")
    if path.endswith(".git"):
        path = path[:-4]
    return parsed.netloc.lower(), path.lower()


def _self_classification(line: str, project: str, source_url: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    project_name = _canonical_name(project)
    pin = re.fullmatch(r"([A-Za-z0-9][A-Za-z0-9_.-]*)\s*==\s*[^\s;#]+(?:\s*;[^#]+)?(?:\s*#.*)?", stripped)
    if pin and _canonical_name(pin.group(1)) == project_name:
        return "SELF_PACKAGE_PIN", f"exact normalized distribution name {pin.group(1)!r} equals frozen project {project!r}"
    vcs = re.fullmatch(r"-e\s+git\+(https?://[^@\s]+)@([^#\s]+)#egg=([A-Za-z0-9_.-]+)", stripped)
    if vcs:
        repo_matches = _repository_identity(vcs.group(1)) == _repository_identity(source_url)
        egg_matches = _canonical_name(vcs.group(3)) == project_name
        if repo_matches and egg_matches:
            return "SELF_VCS_REFERENCE", (
                f"VCS repository {vcs.group(1)!r} equals frozen source {source_url!r}; "
                f"egg {vcs.group(3)!r} equals project {project!r}"
            )
        if repo_matches or egg_matches:
            raise RecipeError("ambiguous apparent subject VCS reference")
    apparent_name = re.match(r"([A-Za-z0-9][A-Za-z0-9_.-]*)\b", stripped)
    if apparent_name and _canonical_name(apparent_name.group(1)) == project_name:
        raise RecipeError("unsupported apparent subject package requirement")
    if "git+" in stripped and (
        f"egg={project}".lower() in stripped.lower()
        or source_url.lower().rstrip("/") in stripped.lower()
    ):
        raise RecipeError("unsupported apparent subject VCS requirement")
    return None


def derive_dependency_input(
    normalized: bytes, *, case_id: str, project: str, source_url: str,
) -> tuple[bytes, list[dict[str, str]]]:
    text = normalized.decode("utf-8", errors="strict")
    lines = text.split("\n")
    retained: list[str] = []
    ledger: list[dict[str, str]] = []
    for ordinal, line in enumerate(lines, 1):
        classification = _self_classification(line, project, source_url)
        if classification is None:
            retained.append(line)
        else:
            category, evidence = classification
            ledger.append({
                "canonical_case_id": case_id,
                "original_line_ordinal": str(ordinal),
                "exact_original_text": line,
                "classification": category,
                "evidence": evidence,
                "original_line_sha256": sha256(line.encode("utf-8")),
            })
    return "\n".join(retained).encode("utf-8"), ledger


def setup_actions(raw: bytes | None, frozen_json: str) -> list[dict[str, object]]:
    if raw is None:
        if json.loads(frozen_json) != []:
            raise RecipeError("absent setup disagrees with frozen ledger")
        return []
    lines = raw.decode("utf-8", errors="strict").splitlines()
    frozen = json.loads(frozen_json)
    actions: list[dict[str, object]] = []
    for ordinal, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        category = classify_setup_line(line)
        if category not in ALLOWED_SETUP:
            raise RecipeError(f"unsupported setup action at line {ordinal}: {category}")
        source_action = category in {"PROJECT_INSTALL_OR_BUILD", "FILESYSTEM_PREPARATION"}
        actions.append({
            "source_line_ordinal": ordinal,
            "exact_source_text": line,
            "classification": category,
            "consumes_subject_source": source_action,
            "requires_network": category == "DEPENDENCY_INSTALL",
            "mutates_source_workspace": source_action,
            "future_execution_phase": (
                "PHASE_4_PROJECT_BUILD_OR_INSTALL" if category == "PROJECT_INSTALL_OR_BUILD"
                else "PHASE_3_ORDERED_SETUP"
            ),
            "dependency_input_binding": (
                "DERIVED_DEPENDENCY_ONLY" if re.fullmatch(
                    r"\s*(?:pip|pip3|python\s+-m\s+pip)\s+install\s+-r\s+requirements\.txt\s*", line
                ) else "AS_DECLARED"
            ),
        })
    if [{"line": a["source_line_ordinal"], "category": a["classification"],
         "text": a["exact_source_text"]} for a in actions] != frozen:
        raise RecipeError("setup classification/order differs from frozen ledger")
    return actions


def environment_mode(actions: list[dict[str, object]]) -> str:
    return (
        "REVISION_SPECIFIC_BUILD_REQUIRED"
        if any(action["consumes_subject_source"] for action in actions)
        else "SOURCE_INDEPENDENT_ENVIRONMENT"
    )


def recipe_hash(recipe: dict[str, object]) -> str:
    """A caller's timestamp or already-attached hash is never an identity input."""
    return sha256(canonical_json({k: v for k, v in recipe.items() if k not in {"timestamp", "build_recipe_sha256"}}))


def _csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_data(benchmark: Path, bugsinpy: Path) -> tuple[
    list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], dict[str, tuple[bytes, bytes]]
]:
    for name, expected in FROZEN_SHA256.items():
        if sha256((benchmark / name).read_bytes()) != expected:
            raise RecipeError(f"frozen control drift: {name}")
    plans = _csv_rows(benchmark / "screening_execution_plan.csv")
    audited = _csv_rows(benchmark / "environment_requirements.csv")
    image_rows = _csv_rows(benchmark / "runtime_base_images.csv")
    images = {row["python_version"]: row for row in image_rows}
    candidates = [r for r in _csv_rows(benchmark / "candidate_universe.csv") if r["selected_initial_40"] == "true"]
    def identities(rows: list[dict[str, str]]) -> list[tuple[str, str]]:
        return [(r["initial_selection_order"], r["canonical_case_id"]) for r in rows]
    if len(plans) != 40 or identities(plans) != identities(audited) or identities(plans) != identities(candidates):
        raise RecipeError("frozen initial-40 order mismatch")
    if len(image_rows) != 7 or len(images) != 7 or set(images) != {r["python_version"] for r in plans}:
        raise RecipeError("base-runtime identities do not cover exactly seven declared versions")
    recipes: list[dict[str, str]] = []
    normalized_rows: list[dict[str, str]] = []
    all_self: list[dict[str, str]] = []
    derived_files: dict[str, tuple[bytes, bytes]] = {}
    runtime_hash = sha256((benchmark / "SCREENING_RUNTIME_V1.md").read_bytes())
    for plan, audit in zip(plans, audited, strict=True):
        case_id = plan["canonical_case_id"]
        project, bug_id = case_id.split("::")
        case_dir = bugsinpy / "projects" / project / "bugs" / bug_id
        if sha256((case_dir / "bug.info").read_bytes()) != audit["bug_info_sha256"]:
            raise RecipeError(f"bug metadata drift: {case_id}")
        if sha256((case_dir.parent.parent / "project.info").read_bytes()) != audit["project_info_sha256"]:
            raise RecipeError(f"project metadata drift: {case_id}")
        req_path = case_dir / "requirements.txt"
        setup_path = case_dir / "setup.sh"
        raw = req_path.read_bytes() if req_path.is_file() else None
        setup = setup_path.read_bytes() if setup_path.is_file() else None
        if (sha256(raw) if raw is not None else "ABSENT") != audit["requirements_sha256"]:
            raise RecipeError(f"requirements raw hash drift: {case_id}")
        if (sha256(setup) if setup is not None else "ABSENT") != audit["setup_sha256"]:
            raise RecipeError(f"setup raw hash drift: {case_id}")
        blockers: list[str] = []
        normalized = dependency = b""
        encoding = audit["requirements_encoding"]
        self_rows: list[dict[str, str]] = []
        if raw is not None:
            try:
                normalized, encoding = normalize_requirements(raw)
                second, second_encoding = normalize_requirements(raw)
                if (normalized, encoding) != (second, second_encoding):
                    raise RecipeError("normalization is not byte-deterministic")
                if encoding != audit["requirements_encoding"]:
                    raise RecipeError("requirements encoding drift")
                dependency, self_rows = derive_dependency_input(
                    normalized, case_id=case_id, project=project,
                    source_url=plan["subject_source_url"],
                )
            except (UnicodeError, RecipeError) as exc:
                blockers.append(f"REQUIREMENTS_UNRESOLVED:{exc}")
        try:
            actions = setup_actions(setup, audit["setup_line_classifications"])
        except (UnicodeError, RecipeError) as exc:
            actions = []
            blockers.append(f"SETUP_UNRESOLVED:{exc}")
        image = images[plan["python_version"]]
        exact_probe = (
            image["runtime_probe_status"] == "EXACT_PROBE_PASSED"
            and image["platform"] == "linux/amd64"
            and image["image_source"] == "docker.io/library/python"
            and image["probe_observed_version"] == plan["python_version"]
            and image["probe_platform_machine"] == "x86_64"
            and re.fullmatch(r"[0-9a-f]{64}", image["python_executable_sha256"]) is not None
            and image["probe_exit_code"] == "0"
        )
        if not exact_probe:
            blockers.append("EXACT_BASE_RUNTIME_PROBE_REQUIRED")
        raw_hash = sha256(raw) if raw is not None else "ABSENT"
        normalized_hash = sha256(normalized) if raw is not None and not any(x.startswith("REQUIREMENTS_") for x in blockers) else "UNRESOLVED"
        dependency_hash = sha256(dependency) if normalized_hash != "UNRESOLVED" else "UNRESOLVED"
        if raw is None:
            normalized_hash = dependency_hash = "ABSENT"
        self_hash = sha256(canonical_json(self_rows))
        setup_hash = sha256(setup) if setup is not None else "ABSENT"
        actions_hash = sha256(canonical_json(actions))
        mode = environment_mode(actions) if not any(x.startswith("SETUP_") for x in blockers) else "UNRESOLVED"
        status = "BUILD_RECIPE_BLOCKED" if blockers else "BUILD_RECIPE_READY"
        recipe: dict[str, object] = {
            "recipe_schema_version": SCHEMA,
            "canonical_case_id": case_id,
            "initial_selection_order": int(plan["initial_selection_order"]),
            "buggy_source_sha": plan["buggy_commit_full"],
            "fixed_source_sha": plan["fixed_commit_full"],
            "subject_source_url": plan["subject_source_url"],
            "subject_workspace_role": "FROZEN_REVISION_FRESH_WORKSPACE",
            "future_execution_cwd": plan["oracle_cwd"],
            "source_install_policy": "EXPLICIT_SETUP_ACTIONS_ONLY",
            "python_declared_version": plan["python_version"],
            "base_image_reference": f"docker.io/library/python@{image['immutable_digest']}",
            "base_image_digest": image["immutable_digest"],
            "runtime_platform": "linux/amd64",
            "python_observed_version": image["probe_observed_version"] or "UNBUILT",
            "python_executable_sha256": image["python_executable_sha256"] or "UNBUILT",
            "requirements_raw_sha256": raw_hash,
            "requirements_encoding": encoding,
            "requirements_normalized_sha256": normalized_hash,
            "dependency_input_sha256": dependency_hash,
            "self_reference_ledger_sha256": self_hash,
            "setup_sha256": setup_hash,
            "setup_actions": actions,
            "setup_action_ledger_sha256": actions_hash,
            "pythonpath_metadata": json.loads(audit["pythonpath_metadata"]),
            "environment_mode_v2": mode,
            "system_package_requirements": "UNKNOWN",
            "future_network_build_policy": "DECLARED_DEPENDENCY_SOURCES_ONLY_SEPARATE_AUTHORITY_REQUIRED",
            "future_network_execution_policy": "NONE",
            "execution_plan_sha256": plan["execution_plan_sha256"],
            "screening_runtime_v1_sha256": runtime_hash,
            "materialization_identity": "UNBUILT",
        }
        recipe_digest = recipe_hash(recipe)
        slug = case_id.replace("::", "__")
        normalized_path = f"derived_inputs/{slug}/requirements.normalized.txt" if raw is not None else "ABSENT"
        dependency_path = f"derived_inputs/{slug}/requirements.dependencies.txt" if raw is not None else "ABSENT"
        if raw is not None and normalized_hash != "UNRESOLVED":
            derived_files[slug] = normalized, dependency
        normalized_rows.append({
            "initial_selection_order": plan["initial_selection_order"],
            "canonical_case_id": case_id,
            "requirements_encoding": encoding,
            "requirements_raw_sha256": raw_hash,
            "requirements_normalized_sha256": normalized_hash,
            "dependency_input_sha256": dependency_hash,
            "normalized_path": normalized_path,
            "dependency_input_path": dependency_path,
            "self_reference_count": str(len(self_rows)),
            "normalization_status": "RESOLVED" if normalized_hash not in {"UNRESOLVED"} else "BLOCKED",
        })
        all_self.extend(self_rows)
        recipes.append({
            "initial_selection_order": plan["initial_selection_order"],
            "canonical_case_id": case_id,
            "python_version": plan["python_version"],
            "base_image_digest": image["immutable_digest"],
            "base_runtime_probe_status": image["runtime_probe_status"],
            "python_observed_version": image["probe_observed_version"] or "UNBUILT",
            "python_executable_sha256": image["python_executable_sha256"] or "UNBUILT",
            "requirements_raw_sha256": raw_hash,
            "requirements_encoding": encoding,
            "requirements_normalized_sha256": normalized_hash,
            "dependency_input_sha256": dependency_hash,
            "self_reference_count": str(len(self_rows)),
            "self_reference_ledger_sha256": self_hash,
            "setup_sha256": setup_hash,
            "setup_action_count": str(len(actions)),
            "setup_action_ledger_sha256": actions_hash,
            "environment_mode_v2": mode,
            "build_recipe_sha256": recipe_digest,
            "build_recipe_status": status,
            "blocking_reason": "|".join(blockers) if blockers else "NONE",
            "build_recipe_json": canonical_json(recipe).decode("utf-8").rstrip("\n"),
        })
    return recipes, normalized_rows, all_self, derived_files


def write_data(benchmark: Path, data: tuple[
    list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], dict[str, tuple[bytes, bytes]]
]) -> None:
    recipes, normalized_rows, all_self, derived_files = data
    for slug, (normalized, dependency) in derived_files.items():
        directory = benchmark / "derived_inputs" / slug
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "requirements.normalized.txt").write_bytes(normalized)
        (directory / "requirements.dependencies.txt").write_bytes(dependency)
    _write_csv(benchmark / "environment_build_recipes.csv", RECIPE_FIELDS, recipes)
    _write_csv(benchmark / "requirements_normalization.csv", NORMALIZATION_FIELDS, normalized_rows)
    _write_csv(benchmark / "self_reference_ledger.csv", SELF_FIELDS, all_self)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    source = Path("/Users/wuyangchenxi/errpilot-benchmark-work/bugsinpy")
    write_data(root, build_data(root, source))

"""Prepare the frozen Section-M expansion block without executing subjects.

This module deliberately does not extend the initial-40 loader or its outputs.
It reads pinned metadata, existing bare mirrors, and Git blobs as inert bytes.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path

from . import audit_environment, build_recipes, executor


BLOCK_SHA256 = "8a478d475066ab94afccf80472aa031e141ec8639296487fdd7fa572308ae02c"
FROZEN_LEDGER_SHA256 = {
    "expansion_block_01.csv": "89bd95f71c230dcde90cdb422ea31218bd11e840aebe60641267e36b163f4186",
    "expansion_block_01_traversal.csv": "fa085f820889de2411edbae4e9161e341d5fc508dc64f58004700dc2bd88c55d",
    "runtime_base_images.csv": "abbbe6aef3fafcc5ad62bcb67274ad392f1b3d31d04dc009251f0150495f9e1f",
    "screening_execution_plan.csv": "95874a88a7ad54a976ef70db1e4cebc2fe8f9be7f72c7551ce8c00dfa17d25ea",
    "environment_requirements.csv": "9607c48fb02ba0b5a77be01dc2201e0d3eec7b83ea1ff4e13925b8068353e912",
    "environment_build_recipes.csv": "2addaf1830e61350e46583ec27b1403b43ffb0f8475b48e4bfc7d62b068b663e",
    "requirements_normalization.csv": "86d67df884cf5d46c2e5421bfe477cd3b8c632ba444230f07370f1e415a2af81",
    "self_reference_ledger.csv": "8fefc975111f6ab60db2175c39d6ff8c9b2e7027eb1de7b90209143f24bc615d",
}
BLOCK_FIELDS = (
    "expansion_block", "expansion_order", "candidate_rank", "rank_sha256",
    "canonical_case_id", "project", "bugsinpy_bug_id", "python_version",
    "buggy_commit_id", "fixed_commit_id", "declared_test_file", "metadata_status",
    "initial_40_member", "cumulative_project_count_after_admission", "admission_reason",
)
PLAN_FIELDS = (
    "expansion_block", "expansion_order", "candidate_rank", "canonical_case_id",
    "project", "bugsinpy_bug_id", "python_version", "buggy_revision_metadata",
    "buggy_commit_full", "fixed_revision_metadata", "fixed_commit_full",
    "subject_source_url", "subject_checkout_identity", "oracle_script_sha256",
    "oracle_commands", "oracle_command_count", "oracle_plan_status",
    "declared_test_file", "protected_manifest_sha256", "protected_manifest_status",
    "environment_plan_sha256", "execution_plan_sha256", "preparation_status",
    "blocking_reason", "network_acquisition_occurred",
)
ENV_FIELDS = (
    "expansion_block", "expansion_order", "canonical_case_id", "project",
    "python_version", *audit_environment.FIELDS[4:],
)
NORMALIZATION_FIELDS = (
    "expansion_block", "expansion_order", "canonical_case_id",
    *build_recipes.NORMALIZATION_FIELDS[2:],
)
SELF_FIELDS = ("expansion_block", "expansion_order", *build_recipes.SELF_FIELDS)
RECIPE_FIELDS = (
    "expansion_block", "expansion_order", "canonical_case_id",
    *build_recipes.RECIPE_FIELDS[2:],
)
REPO_OUTPUTS = {
    "plan": "expansion_block_01_execution_plan.csv",
    "environment": "expansion_block_01_environment_requirements.csv",
    "normalization": "expansion_block_01_requirements_normalization.csv",
    "self": "expansion_block_01_self_reference_ledger.csv",
    "recipes": "expansion_block_01_environment_build_recipes.csv",
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json(value: object) -> bytes:
    return build_recipes.canonical_json(value)


def _csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, strict=True)
        rows = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise executor.PreparationError(f"malformed CSV: {path.name}")
    return rows


def _csv_bytes(fields: tuple[str, ...], rows: list[dict[str, str]]) -> bytes:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode("utf-8")


def _identity(benchmark: Path, block: list[dict[str, str]]) -> None:
    text = (benchmark / "EXPANSION_BLOCK_01.md").read_text(encoding="utf-8")
    match = re.search(r"```json\n(.*?)\n```", text, flags=re.DOTALL)
    if match is None:
        raise executor.PreparationError("block identity JSON missing")
    identity = json.loads(match.group(1))
    canonical = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
    if _sha(canonical) != BLOCK_SHA256:
        raise executor.PreparationError("frozen expansion block identity mismatch")
    if (
        identity.get("candidate_universe_sha256") != executor.CANDIDATE_UNIVERSE_SHA256
        or identity.get("bugsinpy_commit") != executor.BUGSINPY_COMMIT
        or identity.get("ordered_10_case_ids") != [r["canonical_case_id"] for r in block]
        or identity.get("ordered_10_candidate_ranks") != [int(r["candidate_rank"]) for r in block]
        or identity.get("ordered_10_rank_sha256") != [r["rank_sha256"] for r in block]
    ):
        raise executor.PreparationError("block ledger differs from frozen identity")


def load_expansion_candidates(benchmark: Path) -> list[executor.Candidate]:
    """Load exactly the frozen ten; never perform candidate selection."""
    executor.validate_controlling_inputs(benchmark)
    for name, expected in FROZEN_LEDGER_SHA256.items():
        if _sha((benchmark / name).read_bytes()) != expected:
            raise executor.PreparationError(f"frozen ledger drift: {name}")
    if _sha((benchmark / "SCREENING_SPEC_V1.md").read_bytes()) != (
        build_recipes.FROZEN_SHA256["SCREENING_SPEC_V1.md"]
    ):
        raise executor.PreparationError("SCREENING_SPEC_V1.md drift")
    block_path = benchmark / "expansion_block_01.csv"
    block = _csv(block_path)
    if not block or tuple(block[0]) != BLOCK_FIELDS or len(block) != 10:
        raise executor.PreparationError("expansion block schema/count mismatch")
    if [r["expansion_order"] for r in block] != [str(i) for i in range(1, 11)]:
        raise executor.PreparationError("expansion order must be 1..10")
    _identity(benchmark, block)
    universe = _csv(benchmark / "candidate_universe.csv")
    by_rank = {int(r["candidate_rank"]): r for r in universe if r["candidate_rank"]}
    if len(by_rank) != 500:
        raise executor.PreparationError("candidate-universe rank identity mismatch")
    initial_ids = {c.canonical_case_id for c in executor.load_frozen_candidates(benchmark)}
    traversal = _csv(benchmark / "expansion_block_01_traversal.csv")
    if [r["candidate_rank"] for r in traversal] != [str(i) for i in range(72, 103)]:
        raise executor.PreparationError("expansion traversal rank mismatch")
    admitted = [r for r in traversal if r["decision"] == "ADMIT"]
    if [r["canonical_case_id"] for r in admitted] != [r["canonical_case_id"] for r in block]:
        raise executor.PreparationError("expansion traversal admission mismatch")
    candidates: list[executor.Candidate] = []
    for row in block:
        case_id = row["canonical_case_id"]
        rank = int(row["candidate_rank"])
        source = by_rank.get(rank)
        if source is None or case_id in initial_ids:
            raise executor.PreparationError(f"unfrozen or initial-40 case: {case_id}")
        for field in (
            "candidate_rank", "rank_sha256", "canonical_case_id", "project",
            "bugsinpy_bug_id", "python_version", "buggy_commit_id",
            "fixed_commit_id", "declared_test_file", "metadata_status",
        ):
            if row[field] != source[field]:
                raise executor.PreparationError(f"expansion metadata drift: {case_id}:{field}")
        if (
            row["expansion_block"] != "1" or row["initial_40_member"] != "false"
            or source["selected_initial_40"] != "false"
            or row["metadata_status"] != "METADATA_ELIGIBLE"
            or case_id != f"{row['project']}::{row['bugsinpy_bug_id']}"
            or source["bugsinpy_source_commit"] != executor.BUGSINPY_COMMIT
            or row["rank_sha256"] != _sha(f"20260922|candidate|{case_id}".encode())
        ):
            raise executor.PreparationError(f"invalid expansion identity: {case_id}")
        candidates.append(executor.Candidate(
            candidate_rank=rank,
            selection_order=int(row["expansion_order"]),
            canonical_case_id=case_id,
            project=row["project"],
            bug_id=row["bugsinpy_bug_id"],
            source_url=source["project_source_url"],
            python_version=row["python_version"],
            buggy_revision=row["buggy_commit_id"],
            fixed_revision=row["fixed_commit_id"],
            declared_test_file=row["declared_test_file"],
            bugsinpy_source_commit=source["bugsinpy_source_commit"],
        ))
    return candidates


def _resolve_pair(
    candidate: executor.Candidate, mirror: Path, *, allow_missing_revision_update: bool,
    updated_projects: set[str],
) -> tuple[str, str, bool]:
    acquired = candidate.project in updated_projects
    try:
        buggy = executor.resolve_revision(mirror, candidate.buggy_revision)
        fixed = executor.resolve_revision(mirror, candidate.fixed_revision)
    except executor.RevisionResolutionError:
        if not allow_missing_revision_update:
            raise
        if candidate.project not in updated_projects:
            # acquire_project_mirror already verified the canonical origin URL.
            executor._git(mirror, "remote", "update", "--prune")
            updated_projects.add(candidate.project)
        acquired = True
        buggy = executor.resolve_revision(mirror, candidate.buggy_revision)
        fixed = executor.resolve_revision(mirror, candidate.fixed_revision)
    if buggy == fixed:
        raise executor.RevisionResolutionError("BUGGY and FIXED resolve to one commit")
    return buggy, fixed, acquired


def _image(benchmark: Path, version: str) -> dict[str, str]:
    matching = [r for r in _csv(benchmark / "runtime_base_images.csv") if r["python_version"] == version]
    if len(matching) != 1:
        raise build_recipes.RecipeError(f"exact base runtime missing: {version}")
    image = matching[0]
    if not (
        image["runtime_probe_status"] == "EXACT_PROBE_PASSED"
        and image["platform"] == "linux/amd64"
        and image["image_source"] == "docker.io/library/python"
        and image["probe_observed_version"] == version
        and image["probe_platform_machine"] == "x86_64"
        and re.fullmatch(r"sha256:[0-9a-f]{64}", image["immutable_digest"])
        and re.fullmatch(r"[0-9a-f]{64}", image["python_executable_sha256"])
        and image["probe_exit_code"] == "0"
    ):
        raise build_recipes.RecipeError(f"exact base runtime probe mismatch: {version}")
    return image


def _case(
    candidate: executor.Candidate, benchmark: Path, bugsinpy: Path, mirror: Path,
    external: Path, *, allow_missing_revision_update: bool, updated_projects: set[str],
) -> tuple[dict[str, str], dict[str, str], dict[str, str], dict[str, str],
           list[dict[str, str]], dict[Path, bytes], dict[Path, bytes]]:
    case_id = candidate.canonical_case_id
    order = str(candidate.selection_order)
    slug = case_id.replace("::", "__")
    case_dir = bugsinpy / "projects" / candidate.project / "bugs" / candidate.bug_id
    project_dir = case_dir.parent.parent
    evidence = external / slug
    repo_files: dict[Path, bytes] = {}
    external_files: dict[Path, bytes] = {}
    reasons: list[str] = []

    bug_info = (case_dir / "bug.info").read_bytes()
    project_info = (project_dir / "project.info").read_bytes()
    script = (case_dir / "run_test.sh").read_bytes()
    raw = (case_dir / "requirements.txt").read_bytes() if (case_dir / "requirements.txt").is_file() else None
    setup = (case_dir / "setup.sh").read_bytes() if (case_dir / "setup.sh").is_file() else None
    oracle = executor.analyze_oracle(script)
    if oracle["status"] != "RESOLVED_ORDERED_COMMANDS":
        reasons.append(f"ORACLE_UNRESOLVED:{oracle['blocking_reason']}")
    external_files[evidence / "oracle" / "run_test.sh"] = script
    external_files[evidence / "oracle_representation.json"] = _json({
        "schema": "COMPOSITE_ORACLE_SEMANTICS_V1", "status": oracle["status"],
        "commands": oracle["commands"], "argv": [
            list(executor.parse_recognized_command(command)) for command in oracle["commands"]
        ] if oracle["status"] == "RESOLVED_ORDERED_COMMANDS" else [],
        "blocking_reason": oracle["blocking_reason"], "script_sha256": _sha(script),
        "executed": False,
    })
    if raw is not None:
        external_files[evidence / "inputs" / "requirements.raw"] = raw
    if setup is not None:
        external_files[evidence / "inputs" / "setup.raw"] = setup

    buggy = fixed = ""
    acquired = False
    try:
        buggy, fixed, acquired = _resolve_pair(
            candidate, mirror, allow_missing_revision_update=allow_missing_revision_update,
            updated_projects=updated_projects,
        )
    except executor.PreparationError as exc:
        reasons.append(f"SOURCE_REVISION_UNRESOLVED:{exc}")
    prior_source_path = evidence / "source_identity.json"
    if prior_source_path.is_file():
        prior_source = json.loads(prior_source_path.read_bytes())
        if (
            prior_source.get("canonical_case_id") == case_id
            and prior_source.get("buggy_commit_full") == buggy
            and prior_source.get("fixed_commit_full") == fixed
        ):
            acquired = acquired or prior_source.get("network_acquisition_occurred") is True
    source_data = {
        "canonical_case_id": case_id, "source_url": candidate.source_url,
        "mirror_path": str(mirror), "object_format": executor._git(
            mirror, "rev-parse", "--show-object-format"
        ).stdout.strip(),
        "buggy_revision_metadata": candidate.buggy_revision,
        "buggy_commit_full": buggy, "fixed_revision_metadata": candidate.fixed_revision,
        "fixed_commit_full": fixed, "network_acquisition_occurred": acquired,
        "fix_content_inspected": False, "repair_history_inspected": False,
    }
    source_hash = _sha(_json({
        "source_url": candidate.source_url, "buggy_commit_full": buggy,
        "fixed_commit_full": fixed, "object_format": source_data["object_format"],
    }))
    external_files[evidence / "source_identity.json"] = _json(source_data)

    protected: dict[str, object] = {"status": "UNRESOLVED", "manifest_sha256": ""}
    if buggy and fixed:
        protected = executor.build_protected_manifest(
            candidate, mirror, buggy, fixed, oracle["commands"]
        )
        if protected["status"] != "RESOLVED":
            reasons.append("PROTECTED_MANIFEST_UNRESOLVED:" + ";".join(protected["errors"]))
        external_files[evidence / "protected_manifest.json"] = executor.canonical_json_bytes(protected)
    else:
        reasons.append("PROTECTED_MANIFEST_UNRESOLVED:source revisions unavailable")

    normalized = dependency = b""
    self_rows: list[dict[str, str]] = []
    encoding = "ABSENT" if raw is None else "UNRESOLVED"
    norm_hash = dep_hash = "ABSENT" if raw is None else "UNRESOLVED"
    if raw is not None:
        try:
            normalized, encoding = build_recipes.normalize_requirements(raw)
            dependency, self_rows = build_recipes.derive_dependency_input(
                normalized, case_id=case_id, project=candidate.project,
                source_url=candidate.source_url,
            )
            norm_hash, dep_hash = _sha(normalized), _sha(dependency)
            derived = benchmark / "derived_inputs" / "expansion_block_01" / slug
            repo_files[derived / "requirements.normalized.txt"] = normalized
            repo_files[derived / "requirements.dependencies.txt"] = dependency
        except (UnicodeError, build_recipes.RecipeError) as exc:
            reasons.append(f"REQUIREMENTS_UNRESOLVED:{exc}")
    setup_lines: list[dict[str, object]] = []
    actions: list[dict[str, object]] = []
    mode = "UNRESOLVED"
    try:
        if setup is not None:
            setup_lines = [
                {"line": n, "category": audit_environment.classify_setup_line(line), "text": line}
                for n, line in enumerate(setup.decode("utf-8").splitlines(), 1)
                if line.strip() and not line.lstrip().startswith("#")
            ]
        actions = build_recipes.setup_actions(
            setup, json.dumps(setup_lines, separators=(",", ":"))
        )
        mode = build_recipes.environment_mode(actions)
    except (UnicodeError, build_recipes.RecipeError) as exc:
        reasons.append(f"SETUP_UNRESOLVED:{exc}")
    if executor._setup_invokes_tests(setup) if setup is not None else False:
        reasons.append("SETUP_CONTAINS_TEST_OR_UNSAFE_ACTION")

    try:
        image = _image(benchmark, candidate.python_version)
    except build_recipes.RecipeError as exc:
        image = None
        reasons.append(f"BASE_RUNTIME_UNRESOLVED:{exc}")
    pythonpaths = (
        audit_environment._literal_pythonpaths(bug_info)
        + audit_environment._literal_pythonpaths(project_info)
    )
    setup_categories = list(dict.fromkeys(str(x["category"]) for x in setup_lines))
    env = {
        "expansion_block": "1", "expansion_order": order, "canonical_case_id": case_id,
        "project": candidate.project, "python_version": candidate.python_version,
        "bug_info_sha256": _sha(bug_info), "project_info_sha256": _sha(project_info),
        "requirements_present": str(raw is not None).lower(),
        "requirements_sha256": _sha(raw) if raw is not None else "ABSENT",
        "requirements_line_count": str(len(normalized.decode("utf-8").splitlines())) if norm_hash not in {"ABSENT", "UNRESOLVED"} else "0",
        "requirements_encoding": encoding, "setup_present": str(setup is not None).lower(),
        "setup_sha256": _sha(setup) if setup is not None else "ABSENT",
        "setup_line_count": str(len(setup_lines)),
        "pythonpath_present": str(bool(pythonpaths)).lower(),
        "pythonpath_metadata": json.dumps(pythonpaths, separators=(",", ":")),
        "setup_classification": "|".join(setup_categories) if setup_categories else "NONE",
        "setup_line_classifications": json.dumps(setup_lines, separators=(",", ":")),
        "source_build_required_or_possible": str(mode == "REVISION_SPECIFIC_BUILD_REQUIRED").lower(),
        "environment_mode": mode,
        "base_runtime_status": image["runtime_probe_status"] if image else "UNRESOLVED",
        "environment_feasibility_status": "UNBUILT",
        "blocking_reason": "|".join(reasons) if reasons else "NONE",
    }
    norm_path = f"derived_inputs/expansion_block_01/{slug}/requirements.normalized.txt" if raw is not None and norm_hash != "UNRESOLVED" else "ABSENT" if raw is None else "UNRESOLVED"
    dep_path = f"derived_inputs/expansion_block_01/{slug}/requirements.dependencies.txt" if raw is not None and dep_hash != "UNRESOLVED" else "ABSENT" if raw is None else "UNRESOLVED"
    normalization = {
        "expansion_block": "1", "expansion_order": order,
        "canonical_case_id": case_id,
        "requirements_encoding": encoding,
        "requirements_raw_sha256": _sha(raw) if raw is not None else "ABSENT",
        "requirements_normalized_sha256": norm_hash, "dependency_input_sha256": dep_hash,
        "normalized_path": norm_path, "dependency_input_path": dep_path,
        "self_reference_count": str(len(self_rows)),
        "normalization_status": "BLOCKED" if norm_hash == "UNRESOLVED" else "RESOLVED",
    }
    external_files[evidence / "environment_inputs.json"] = _json({
        "canonical_case_id": case_id, "bug_info_sha256": _sha(bug_info),
        "project_info_sha256": _sha(project_info), "requirements_raw_sha256": env["requirements_sha256"],
        "requirements_encoding": encoding, "requirements_normalized_sha256": norm_hash,
        "dependency_input_sha256": dep_hash, "setup_sha256": env["setup_sha256"],
        "setup_line_classifications": setup_lines, "setup_actions": actions,
        "pythonpath_metadata": pythonpaths, "environment_mode": mode,
        "self_reference_ledger_sha256": _sha(_json(self_rows)),
        "executed": False,
    })
    plan: dict[str, object] = {
        "schema": "EXPANSION_BLOCK_01_PREPARATION_PLAN_V1",
        "expansion_block": 1, "expansion_order": candidate.selection_order,
        "block_identity_sha256": BLOCK_SHA256, "candidate_rank": candidate.candidate_rank,
        "canonical_case_id": case_id, "project": candidate.project,
        "bugsinpy_bug_id": candidate.bug_id, "python_version": candidate.python_version,
        "buggy_revision_metadata": candidate.buggy_revision, "buggy_commit_full": buggy,
        "fixed_revision_metadata": candidate.fixed_revision, "fixed_commit_full": fixed,
        "subject_source_url": candidate.source_url, "subject_checkout_identity": source_hash,
        "oracle_script_sha256": _sha(script), "oracle_commands": oracle["commands"],
        "oracle_command_count": len(oracle["commands"]), "oracle_plan_status": oracle["status"],
        "declared_test_file": candidate.declared_test_file,
        "protected_manifest_sha256": protected["manifest_sha256"],
        "protected_manifest_status": protected["status"],
        "environment_mode": mode,
        "environment_plan_sha256": _sha(external_files[evidence / "environment_inputs.json"]),
        "pre_execution_timeout_gate": "PRE_EXECUTION_TIMEOUT_GATE_REQUIRED",
        "execution_authorized": False, "subject_materialization": "UNBUILT",
        "network_acquisition_occurred": acquired,
        "preparation_status": "EXPANSION_PREPARATION_BLOCKED" if reasons else "EXPANSION_PREPARATION_READY",
        "blocking_reason": "|".join(reasons) if reasons else "NONE",
    }
    plan_hash = _sha(_json(plan))
    plan["execution_plan_sha256"] = plan_hash
    external_files[evidence / "preparation_plan.json"] = _json(plan)
    csv_plan = {
        field: json.dumps(plan[field], separators=(",", ":")) if field == "oracle_commands"
        else str(plan.get(field, "")).lower() if field == "network_acquisition_occurred"
        else str(plan.get(field, ""))
        for field in PLAN_FIELDS
    }
    for key in ("expansion_block", "expansion_order"):
        csv_plan[key] = str(plan[key])
    self_output = [{"expansion_block": "1", "expansion_order": order, **row} for row in self_rows]

    recipe_body: dict[str, object] | None = None
    if not reasons and image is not None:
        recipe_body = {
            "recipe_schema_version": "EXPANSION_BLOCK_01_ENVIRONMENT_BUILD_RECIPE_V1",
            "expansion_block": 1, "expansion_order": candidate.selection_order,
            "block_identity_sha256": BLOCK_SHA256, "canonical_case_id": case_id,
            "buggy_source_sha": buggy, "fixed_source_sha": fixed,
            "subject_source_url": candidate.source_url,
            "subject_workspace_role": "FROZEN_REVISION_FRESH_WORKSPACE",
            "future_execution_cwd": "subject repository root",
            "source_install_policy": "EXPLICIT_SETUP_ACTIONS_ONLY",
            "python_declared_version": candidate.python_version,
            "base_image_reference": f"docker.io/library/python@{image['immutable_digest']}",
            "base_image_digest": image["immutable_digest"], "runtime_platform": "linux/amd64",
            "python_observed_version": image["probe_observed_version"],
            "python_executable_sha256": image["python_executable_sha256"],
            "requirements_raw_sha256": normalization["requirements_raw_sha256"],
            "requirements_encoding": encoding,
            "requirements_normalized_sha256": norm_hash,
            "dependency_input_sha256": dep_hash,
            "self_reference_ledger_sha256": _sha(_json(self_rows)),
            "setup_sha256": env["setup_sha256"], "setup_actions": actions,
            "setup_action_ledger_sha256": _sha(_json(actions)),
            "pythonpath_metadata": pythonpaths,
            "protected_manifest_sha256": protected["manifest_sha256"],
            "execution_plan_sha256": plan_hash, "environment_mode_v2": mode,
            "system_package_requirements": "UNKNOWN",
            "future_network_build_policy": "DECLARED_DEPENDENCY_SOURCES_ONLY_SEPARATE_AUTHORITY_REQUIRED",
            "future_network_execution_policy": "NONE",
            "screening_runtime_v1_sha256": _sha((benchmark / "SCREENING_RUNTIME_V1.md").read_bytes()),
            "materialization_identity": "UNBUILT",
        }
    recipe = {
        "expansion_block": "1", "expansion_order": order, "canonical_case_id": case_id,
        "python_version": candidate.python_version,
        "base_image_digest": image["immutable_digest"] if image else "UNRESOLVED",
        "base_runtime_probe_status": image["runtime_probe_status"] if image else "UNRESOLVED",
        "python_observed_version": image["probe_observed_version"] if image else "UNRESOLVED",
        "python_executable_sha256": image["python_executable_sha256"] if image else "UNRESOLVED",
        "requirements_raw_sha256": normalization["requirements_raw_sha256"],
        "requirements_encoding": encoding,
        "requirements_normalized_sha256": norm_hash, "dependency_input_sha256": dep_hash,
        "self_reference_count": str(len(self_rows)),
        "self_reference_ledger_sha256": _sha(_json(self_rows)),
        "setup_sha256": env["setup_sha256"], "setup_action_count": str(len(actions)),
        "setup_action_ledger_sha256": _sha(_json(actions)),
        "environment_mode_v2": mode,
        "build_recipe_sha256": build_recipes.recipe_hash(recipe_body) if recipe_body else "",
        "build_recipe_status": "BUILD_RECIPE_READY" if recipe_body else "BUILD_RECIPE_BLOCKED",
        "blocking_reason": "|".join(reasons) if reasons else "NONE",
        "build_recipe_json": _json(recipe_body).decode().rstrip("\n") if recipe_body else "",
    }
    return csv_plan, env, normalization, recipe, self_output, repo_files, external_files


def build_data(
    benchmark: Path, bugsinpy: Path, external: Path, *,
    allow_missing_revision_update: bool = False,
) -> tuple[dict[Path, bytes], dict[Path, bytes], dict[str, object]]:
    candidates = load_expansion_candidates(benchmark)
    executor.validate_bugsinpy_checkout(bugsinpy)
    for name, expected in build_recipes.FROZEN_SHA256.items():
        if _sha((benchmark / name).read_bytes()) != expected:
            raise executor.PreparationError(f"frozen control drift: {name}")
    mirrors = {
        c.project: executor.acquire_project_mirror(
            c.project, c.source_url, external.parent / "subject_repositories", allow_network=False
        ) for c in candidates
    }
    plans: list[dict[str, str]] = []
    environments: list[dict[str, str]] = []
    normalizations: list[dict[str, str]] = []
    recipes: list[dict[str, str]] = []
    self_rows: list[dict[str, str]] = []
    repo_files: dict[Path, bytes] = {}
    external_files: dict[Path, bytes] = {}
    updated_projects: set[str] = set()
    for candidate in candidates:
        plan, env, norm, recipe, self_ref, derived, evidence = _case(
            candidate, benchmark, bugsinpy, mirrors[candidate.project], external,
            allow_missing_revision_update=allow_missing_revision_update,
            updated_projects=updated_projects,
        )
        plans.append(plan)
        environments.append(env)
        normalizations.append(norm)
        recipes.append(recipe)
        self_rows.extend(self_ref)
        repo_files.update(derived)
        external_files.update(evidence)
    repo_files[benchmark / REPO_OUTPUTS["plan"]] = _csv_bytes(PLAN_FIELDS, plans)
    repo_files[benchmark / REPO_OUTPUTS["environment"]] = _csv_bytes(ENV_FIELDS, environments)
    repo_files[benchmark / REPO_OUTPUTS["normalization"]] = _csv_bytes(NORMALIZATION_FIELDS, normalizations)
    repo_files[benchmark / REPO_OUTPUTS["self"]] = _csv_bytes(SELF_FIELDS, self_rows)
    repo_files[benchmark / REPO_OUTPUTS["recipes"]] = _csv_bytes(RECIPE_FIELDS, recipes)
    counts = Counter(p["preparation_status"] for p in plans)
    modes = Counter(r["environment_mode_v2"] for r in recipes)
    return repo_files, external_files, {
        "ready": counts["EXPANSION_PREPARATION_READY"],
        "blocked": counts["EXPANSION_PREPARATION_BLOCKED"],
        "modes": dict(sorted(modes.items())),
        "network_updated_projects": sorted(updated_projects),
    }


def write_new_files(files: dict[Path, bytes]) -> None:
    existing = [str(path) for path in files if path.exists()]
    if existing:
        raise executor.PreparationError("refusing to overwrite existing preparation: " + ", ".join(existing))
    for path, data in sorted(files.items()):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("inspect", "prepare", "verify"))
    parser.add_argument("--allow-missing-revision-update", action="store_true")
    args = parser.parse_args()
    if args.mode != "prepare" and args.allow_missing_revision_update:
        parser.error("remote updates are permitted only during preparation")
    benchmark = Path(__file__).resolve().parents[1]
    work = Path("/Users/wuyangchenxi/errpilot-benchmark-work")
    bugsinpy = work / "bugsinpy"
    external = work / "expansion_block_01_preparation"
    repo_files, external_files, summary = build_data(
        benchmark, bugsinpy, external,
        allow_missing_revision_update=args.allow_missing_revision_update,
    )
    if args.mode == "prepare":
        write_new_files(external_files)
        write_new_files(repo_files)
    elif args.mode == "verify":
        for path, expected in {**repo_files, **external_files}.items():
            if not path.is_file() or path.read_bytes() != expected:
                raise executor.PreparationError(f"regenerated preparation differs: {path}")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()

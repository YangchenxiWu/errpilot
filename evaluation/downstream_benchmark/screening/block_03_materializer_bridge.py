"""Consume accepted Block-03 artifacts without deriving recipes or executing subjects.

The authority record binds Human-PI-accepted preparation, including the two
compatibility overlays. Acceptance grants input capability only. This adapter
has no build, source-export, installation, setup, or oracle execution path.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import executor, materializer as m, prepare_expansion_block_03 as preparation


AUTHORITY_FILE = "block_03_materializer_input_authority_v1.json"
AUTHORITY_SHA256 = "8844f3b9a00e9c8a8d10c32112291d8f68ac883f5cc775425afbc559358b6a9e"
BLOCK_SHA256 = "883628cb72d4ddf56fdfd4a28c4b3c0752b429acf1b6c0abe382bbf7d666e780"
WORK = Path("/Users/wuyangchenxi/errpilot-benchmark-work")
PREPARATION = WORK / "expansion_block_03_preparation"
BUGSINPY = WORK / "bugsinpy"
MEMBERS = ("tqdm::6", "PySnooper::3", "sanic::3", "sanic::5", "PySnooper::2",
           "cookiecutter::2", "cookiecutter::1")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise m.Blocked("BLOCKED_INPUT_IDENTITY", message)


def _read(path: Path) -> bytes:
    _require(path.is_file() and not path.is_symlink(), f"missing/unsafe accepted artifact: {path}")
    return path.read_bytes()


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(_read(path))
    _require(isinstance(value, dict), f"accepted JSON object required: {path.name}")
    return value


def _ordered(rows: list[dict[str, str]], label: str) -> None:
    _require([r["canonical_case_id"] for r in rows] == list(MEMBERS)
             and [r["expansion_order"] for r in rows] == [str(i) for i in range(1, 8)]
             and all(r["expansion_block"] == "3" for r in rows),
             f"exact seven ordered Block 03 {label} required")


def _load(benchmark: Path, evidence: Path, bugsinpy: Path) -> list[dict[str, Any]]:
    authority_bytes = _read(benchmark / AUTHORITY_FILE)
    _require(m.sha256(authority_bytes) == AUTHORITY_SHA256, "Block 03 input authority hash mismatch")
    authority = json.loads(authority_bytes)
    _require(authority["schema"] == "BLOCK_03_MATERIALIZER_INPUT_AUTHORITY_V1"
             and authority["transaction"] == "BLOCK_03_MATERIALIZER_AUTHORITY_BRIDGE_V1"
             and authority["block_status"] == "SECTION_M_EXPANSION_BLOCK_03_FROZEN"
             and authority["block_identity_sha256"] == BLOCK_SHA256
             and authority["preparation_acceptance"] == "HUMAN_PI_ACCEPTED"
             and authority["compatibility_bridge_acceptance"] == "HUMAN_PI_ACCEPTED"
             and authority["bridge_lifecycle"] == "CANDIDATE_ONLY"
             and authority["materialization_authorized"] is False
             and authority["bugsinpy_commit"] == executor.BUGSINPY_COMMIT
             and authority["bugsinpy_tree"] == executor.BUGSINPY_TREE
             and authority["candidate_universe_sha256"] == executor.CANDIDATE_UNIVERSE_SHA256
             and authority["sampling_seed"] == 20260922
             and authority["compatibility_cases"] == list(MEMBERS[-2:]),
             "Block 03 acceptance/provenance mismatch")
    for name, digest in authority["accepted_repository_sha256"].items():
        _require(m.sha256(_read(benchmark / name)) == digest,
                 f"accepted Block 03 preparation hash mismatch: {name}")
    for name, digest in authority["original_preparation_evidence_sha256"].items():
        _require(m.sha256(_read(evidence / name)) == digest,
                 f"accepted Block 03 evidence hash mismatch: {name}")

    # Existing metadata authority includes exact terminal-partial membership,
    # frozen ranks/seed/cap/cursor, V4 exclusions, and a header-only manifest.
    candidates = preparation.load_expansion_candidates(benchmark)
    executor.validate_bugsinpy_checkout(bugsinpy)
    _require([c.canonical_case_id for c in candidates] == list(MEMBERS),
             "Block 03 candidate membership mismatch")
    rows = m.read_rows(benchmark / "expansion_block_03_environment_build_recipes.csv")
    plans = m.read_rows(benchmark / "expansion_block_03_execution_plan.csv")
    environments = m.read_rows(benchmark / "expansion_block_03_environment_requirements.csv")
    norms = m.read_rows(benchmark / "expansion_block_03_requirements_normalization.csv")
    self_rows = m.read_rows(benchmark / "expansion_block_03_self_reference_ledger.csv")
    for items, name in ((rows, "recipes"), (plans, "plans"),
                        (environments, "environments"), (norms, "normalizations")):
        _ordered(items, name)
    _require([r["canonical_case_id"] for r in authority["ordered_recipe_identities"]]
             == list(MEMBERS), "Block 03 authority membership mismatch")
    _require(all(r["canonical_case_id"] in MEMBERS for r in self_rows),
             "unknown Block 03 self-reference case")

    accepted: list[dict[str, Any]] = []
    for candidate, row, csv_plan, env_row, norm, bound in zip(
            candidates, rows, plans, environments, norms, authority["ordered_recipe_identities"]):
        case_id = candidate.canonical_case_id
        slug = case_id.replace("::", "__")
        original = evidence / slug
        # The accepted report establishes these exact overlays. No fallback to
        # historical cookiecutter blocker artifacts is permitted.
        representation = (benchmark / "evidence/block_03_preparation_compatibility_bridge_v1" / slug
                          if case_id in authority["compatibility_cases"] else original)
        plan = _json(representation / "preparation_plan.json")
        environment = _json(representation / "environment_inputs.json")
        oracle = _json(representation / "oracle_representation.json")
        source = _json(original / "source_identity.json")
        recipe = json.loads(row["build_recipe_json"])
        _require(row["build_recipe_status"] == "BUILD_RECIPE_READY"
                 and row["blocking_reason"] == "NONE"
                 and recipe["recipe_schema_version"] == "EXPANSION_BLOCK_03_ENVIRONMENT_BUILD_RECIPE_V1"
                 and recipe["expansion_block"] == 3
                 and recipe["expansion_order"] == candidate.selection_order
                 and recipe["block_identity_sha256"] == BLOCK_SHA256
                 and recipe["canonical_case_id"] == case_id
                 and m.recipe_hash(recipe) == row["build_recipe_sha256"] == bound["build_recipe_sha256"]
                 and recipe["materialization_identity"] == "UNBUILT"
                 and recipe["runtime_platform"] == m.PLATFORM
                 and recipe["environment_mode_v2"] == "REVISION_SPECIFIC_BUILD_REQUIRED"
                 and recipe["future_network_execution_policy"] == "NONE"
                 and recipe["future_execution_cwd"] == "subject repository root",
                 f"accepted Block 03 recipe mismatch: {case_id}")
        plan_body = {k: v for k, v in plan.items() if k != "execution_plan_sha256"}
        _require(m.sha256(m.canonical_json(plan_body)) == plan["execution_plan_sha256"]
                 == recipe["execution_plan_sha256"]
                 and plan["preparation_status"] == "EXPANSION_PREPARATION_READY"
                 and plan["execution_authorized"] is False
                 and plan["subject_materialization"] == "UNBUILT"
                 and plan["pre_execution_timeout_gate"] == "PRE_EXECUTION_TIMEOUT_GATE_REQUIRED"
                 and plan["block_identity_sha256"] == BLOCK_SHA256
                 and plan["protected_manifest_status"] == "RESOLVED"
                 and plan["protected_manifest_sha256"] == recipe["protected_manifest_sha256"],
                 f"accepted Block 03 plan mismatch: {case_id}")
        for field in preparation.PLAN_FIELDS:
            value = (json.dumps(plan[field], separators=(",", ":")) if field == "oracle_commands"
                     else str(plan.get(field, "")).lower() if field == "network_acquisition_occurred"
                     else str(plan.get(field, "")))
            _require(csv_plan[field] == value, f"Block 03 plan CSV mismatch: {case_id}/{field}")
        _require(m.sha256(_read(representation / "environment_inputs.json"))
                 == plan["environment_plan_sha256"]
                 and environment["executed"] is False
                 and environment["setup_actions"] == recipe["setup_actions"]
                 and env_row["setup_sha256"] == recipe["setup_sha256"],
                 f"Block 03 environment binding mismatch: {case_id}")
        commands = json.loads(csv_plan["oracle_commands"])
        _require(oracle["executed"] is False and oracle["status"] == "RESOLVED_ORDERED_COMMANDS"
                 and oracle["commands"] == commands == plan["oracle_commands"]
                 and oracle["argv"] == [command.split() for command in commands]
                 and len(commands) == plan["oracle_command_count"] >= 1
                 and m.sha256(_read(original / "oracle/run_test.sh"))
                 == oracle["script_sha256"] == plan["oracle_script_sha256"],
                 f"Block 03 oracle representation mismatch: {case_id}")
        if case_id in authority["compatibility_cases"]:
            expected_provenance = {
                "representation_authority": "BLOCK_03_PREPARATION_COMPATIBILITY_BRIDGE_V1",
                "bugsinpy_commit": executor.BUGSINPY_COMMIT, "bugsinpy_tree": executor.BUGSINPY_TREE,
                "metadata_directory": f"projects/{candidate.project}/bugs/{candidate.bug_id}",
            }
            _require(oracle["schema"] == "BLOCK_03_PREPARATION_COMPATIBILITY_ORACLE_V1"
                     and oracle["source_provenance"] == expected_provenance
                     and environment["source_provenance"] == expected_provenance
                     and oracle["future_execution_cwd"] == environment["future_execution_cwd"]
                     == "subject repository root", "Block 03 compatibility provenance mismatch")
        source_body = {k: source[k] for k in (
            "source_url", "buggy_commit_full", "fixed_commit_full", "object_format")}
        mirror = WORK / "subject_repositories" / f"{candidate.project}.git"
        _require(source["canonical_case_id"] == case_id and source["source_url"] == candidate.source_url
                 == recipe["subject_source_url"] == plan["subject_source_url"]
                 and source["object_format"] == "sha1" and source["mirror_path"] == str(mirror)
                 and m.sha256(m.canonical_json(source_body)) == plan["subject_checkout_identity"]
                 and executor._git(mirror, "remote", "get-url", "origin").stdout.strip()
                 == candidate.source_url, f"Block 03 source identity mismatch: {case_id}")
        for label in ("buggy", "fixed"):
            revision = getattr(candidate, f"{label}_revision")
            _require(source[f"{label}_commit_full"] == recipe[f"{label}_source_sha"]
                     == plan[f"{label}_commit_full"] == revision
                     and executor._git(mirror, "cat-file", "-t", revision).stdout.strip() == "commit",
                     f"Block 03 {label} source revision mismatch: {case_id}")
        metadata = bugsinpy / "projects" / candidate.project / "bugs" / candidate.bug_id
        _require(m.sha256(_read(metadata / "bug.info")) == environment["bug_info_sha256"]
                 and m.sha256(_read(metadata.parent.parent / "project.info"))
                 == environment["project_info_sha256"], "Block 03 pinned metadata mismatch")
        namespace = Path("derived_inputs/expansion_block_03") / slug
        paths = {"raw_requirements": f"raw/{slug}/requirements.raw",
                 "normalized_requirements": (namespace / "requirements.normalized.txt").as_posix(),
                 "dependency_input": (namespace / "requirements.dependencies.txt").as_posix(),
                 "setup_input": f"raw/{slug}/setup.raw"}
        _require(norm["normalized_path"] == paths["normalized_requirements"]
                 and norm["dependency_input_path"] == paths["dependency_input"]
                 and norm["normalization_status"] == "RESOLVED", "Block 03 derived namespace mismatch")
        data: dict[str, bytes | None] = {}
        for key, file, hash_field in (
            ("raw_requirements", original / "inputs/requirements.raw", "requirements_raw_sha256"),
            ("normalized_requirements", benchmark / paths["normalized_requirements"], "requirements_normalized_sha256"),
            ("dependency_input", benchmark / paths["dependency_input"], "dependency_input_sha256"),
            ("setup_input", original / "inputs/setup.raw", "setup_sha256"),
        ):
            if recipe[hash_field] == "ABSENT":
                _require(not file.exists() and not file.is_symlink(), "unexpected Block 03 raw input")
                data[key] = None
                paths.pop(key)
            else:
                data[key] = _read(file)
                if key in ("raw_requirements", "setup_input"):
                    pinned_name = "requirements.txt" if key == "raw_requirements" else "setup.sh"
                    _require(data[key] == _read(metadata / pinned_name), "Block 03 raw/pinned input mismatch")
        ledger = [{k: v for k, v in item.items() if k not in ("expansion_block", "expansion_order")}
                  for item in self_rows if item["canonical_case_id"] == case_id]
        _require(all(item["expansion_order"] == str(candidate.selection_order)
                     and item["expansion_block"] == "3"
                     for item in self_rows if item["canonical_case_id"] == case_id)
                 and len(ledger) == int(row["self_reference_count"]), "Block 03 self-reference mismatch")
        m.verify_inputs(recipe, data["raw_requirements"], data["normalized_requirements"],
                        data["dependency_input"], ledger, data["setup_input"])
        # Static argv validation only; the existing builder already preserves
        # literal python setup.py develop. No new executable allowlist is added.
        for action in recipe["setup_actions"]:
            m.action_argv(action, source_present=True)
        accepted.append({"recipe": recipe, "execution_plan": plan,
                         "oracle_representation": oracle, "source_identity": source,
                         "input_paths": paths, "self_reference_ledger": ledger})
    return accepted


def load_inputs(benchmark: Path = m.BENCHMARK, evidence: Path = PREPARATION,
                bugsinpy: Path = BUGSINPY) -> list[dict[str, Any]]:
    """Fail closed; perform reads and read-only Git identity checks only."""
    try:
        return _load(benchmark, evidence, bugsinpy)
    except m.Blocked:
        raise
    except (OSError, KeyError, TypeError, ValueError, executor.PreparationError) as exc:
        raise m.Blocked("BLOCKED_INPUT_IDENTITY", "malformed accepted Block 03 input") from exc


def _validate_request(request: dict[str, Any], benchmark: Path) -> dict[str, Any]:
    """Bind one future identity to the accepted inputs; never stage source or build."""
    _require(isinstance(request, dict) and isinstance(request.get("canonical_case_id"), str),
             "Block 03 request object/case identity required")
    accepted = {item["recipe"]["canonical_case_id"]: item for item in load_inputs(benchmark)}
    item = accepted.get(request.get("canonical_case_id"))
    _require(item is not None, "case outside accepted Expansion Block 03")
    recipe = item["recipe"]
    _require(request.get("expansion_block") == 3
             and type(request.get("expansion_block")) is int
             and request.get("expansion_order") == recipe["expansion_order"]
             and type(request.get("expansion_order")) is int
             and request.get("block_identity_sha256") == BLOCK_SHA256
             and request.get("materializer_input_authority_sha256") == AUTHORITY_SHA256
             and request.get("build_recipe_sha256") == m.recipe_hash(recipe)
             and request.get("self_reference_ledger") == item["self_reference_ledger"]
             and all(request.get(key) == item["input_paths"].get(key) for key in (
                 "raw_requirements", "normalized_requirements", "dependency_input", "setup_input")),
             "Block 03 request identity/input mismatch")
    label = request.get("revision_label")
    revisions = request.get("revisions")
    _require(label in ("BUGGY", "FIXED") and isinstance(revisions, list) and len(revisions) == 1
             and isinstance(revisions[0], dict), "Block 03 requires one BUGGY/FIXED identity")
    revision = revisions[0]
    _require(set(revision) == {"label", "sha", "source", "source_revision_sha"}
             and revision["label"] == label
             and revision["source_revision_sha"] == recipe[f"{label.lower()}_source_sha"]
             and isinstance(revision["sha"], str) and bool(m.HEX64.fullmatch(revision["sha"]))
             and revision["source"] == f"snapshots/{recipe['canonical_case_id'].replace('::', '__')}/{label.lower()}",
             "Block 03 source revision/snapshot identity mismatch")
    _require(all(key not in request for key in (
        "recipe", "execution_plan", "oracle_representation", "setup_actions", "oracle_commands")),
        "Block 03 representations must come from accepted artifacts")
    return {**request, "recipe": recipe, "execution_plan": item["execution_plan"],
            "oracle_representation": item["oracle_representation"]}


def validate_request(request: dict[str, Any], benchmark: Path = m.BENCHMARK) -> dict[str, Any]:
    """Reject malformed requests before any runtime path can consume them."""
    try:
        return _validate_request(request, benchmark)
    except m.Blocked:
        raise
    except (OSError, KeyError, TypeError, ValueError) as exc:
        raise m.Blocked("BLOCKED_INPUT_IDENTITY", "malformed Block 03 request") from exc

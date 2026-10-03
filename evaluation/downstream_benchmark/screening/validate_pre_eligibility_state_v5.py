"""Read-only V4 -> V5 persistence validation; never dispatch a subject process.

V4 keeps its original path and validator. Future current-state transactions must
explicitly bind this successor descriptor and validator, under separate authority.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from evaluation.downstream_benchmark.screening import executor


ENTRY_HEAD = "0f996836f2035817a1e9b0347c81bf269f9b36b4"
V4_COMMIT = "fe60347faf7e6f85ee2159ea80e0d0d53be82a9e"
INSTRUCTION_SHA256 = "033b84417d53fbc0f8320b2d483e86e10672b6a7531df26f928ea8254a5c6a41"
PRODUCTION_ROOT = Path(
    "/Users/wuyangchenxi/errpilot-benchmark-work/"
    "environment_materialization_expansion_block_03_v1"
)
EXCLUSIONS = "exclusions_v5.csv"
DISPOSITIONS = "expansion_block_03_build_failure_adjudication_v1.csv"
EVIDENCE = "evidence/block_03_materialization_outcome_v5/first_pass_evidence.json"
STATE = "pre_eligibility_current_state_v5.json"
DOCUMENT = "PRE_ELIGIBILITY_EXCLUSIONS_LEDGER_STATE_V5.md"
RECORD = "BLOCK_03_MATERIALIZATION_OUTCOME_PERSISTENCE_V5.md"
VALIDATOR = "screening/validate_pre_eligibility_state_v5.py"
TESTS = "tests/test_pre_eligibility_state_v5.py"
CREATED_PATHS = (EXCLUSIONS, DISPOSITIONS, EVIDENCE, STATE, DOCUMENT, RECORD, VALIDATOR, TESTS)
PREDECESSOR_HASHES = {
    "exclusions.csv": "e13187b561745222873f6533d7883556b786fcab7f455b5035e664f558654f45",
    "PRE_ELIGIBILITY_EXCLUSIONS_LEDGER_STATE_V4.md":
        "540572c9f81385bd425ebe4c69e31b7a049614ef7be8b76bd0909b8e9b754e6a",
    "screening/executor.py":
        "e16a4e71880ac08e607b2ce43519d7565482c3d3c358ae18c187230a45f5d305",
    "EXPANSION_BLOCK_03_PREPARATION_V1.md":
        "e797ff2ac48b4ac379fb15c25fe805ce1077a06b56a5603082aba48dbcbda829",
    "BLOCK_03_PRE_MATERIALIZATION_LIFECYCLE_CLOSURE_V1.md":
        "8e76134f696f182b8910c0032b24e0027470f4debc375aa85aaa1f5c82a8ca6a",
    "BLOCK_03_MATERIALIZER_AUTHORITY_BRIDGE_V1.md":
        "ebfa53db42d84f0c3b41cd1c49a775343a64b9c72b6c68e1733bd9cf7d8bb65b",
    "block_03_materializer_input_authority_v1.json":
        "8844f3b9a00e9c8a8d10c32112291d8f68ac883f5cc775425afbc559358b6a9e",
    "screening/prepare_expansion_block_03.py":
        "bc3eb4885b0d2dc439953cc72d4ab1e210a5f08ac741e9d0f38b47c0c6f895aa",
    "screening/block_03_materializer_bridge.py":
        "c6212e90ad92fb0be439426549f2f94e6a9790580c6615a2475b7fa95f4f73a5",
    "expansion_block_03.csv":
        "50231362538d477ab262a783da904b51552652dd490267c1c4c84a59db3fcc8b",
    "cases_manifest.csv":
        "c7d423696616ffb7d5dc79fa5bf56294044b3d66c247c744d575617dbb89dac9",
}
SOURCE_HASHES = {
    "first_pass_completion.json":
        "54f598f0cc5df6b8b4cc33416ea517edb90ac5248b25b0b924a16691e32d6832",
    "identity_ledger.json":
        "a867864ce5826520855e321cf52f23ea58663e62a79dbe2aa6c444bf734c2588",
    "materialization_results.csv":
        "b918059ec7746e9c81da1b9cc11e89d1799ac083b57f0d070a57d14750b529e8",
    "post_run_audit.json":
        "2aaca5e11e18832a8eb28e3b4fbf2710245e27c38735b2c984703170c0a8c2f8",
}
# Filled from the entry-gated, read-only extract; not a new materialization.
EVIDENCE_SHA256 = "60a63e81f29bbe7ca885080c788e667d47d63bcc9084e3aad56e15644aacd812"
MEMBERSHIP = (
    ("tqdm::6", 259), ("PySnooper::3", 369), ("sanic::3", 380),
    ("sanic::5", 405), ("PySnooper::2", 431), ("cookiecutter::2", 472),
    ("cookiecutter::1", 485),
)
DELTA = {
    "tqdm::6": "DEPENDENCY_SETUP_FAILURE",
    "sanic::3": "UNSUPPORTED_ENVIRONMENT",
    "sanic::5": "UNSUPPORTED_ENVIRONMENT",
    "cookiecutter::2": "DEPENDENCY_SETUP_FAILURE",
    "cookiecutter::1": "DEPENDENCY_SETUP_FAILURE",
}
READY = ["PySnooper::3", "PySnooper::2"]
DISPOSITION_FIELDS = (
    *executor.EXPANSION_BLOCK_02_BUILD_ADJUDICATION_V1_FIELDS,
    "first_pass_attempt_consumed", "permanent_non_retry", "decision_authority",
)
CAPACITY = {
    "entry_environment_ready": 26,
    "new_complete_materialized_cases": READY,
    "new_environment_ready": 2,
    "resulting_environment_ready": 28,
    "required_slots": 28,
    "capacity_requirement_met": "YES",
}
SCIENTIFIC = {
    "cumulative_metadata_admissions": 67,
    "oracle_outcomes": 0,
    "cases_manifest": "header-only",
    "eligibility_established": "NO",
    "materialized_is_eligible": False,
    "oracle_screening_authorized": False,
    "pilot_final_allocation_performed": False,
}
AUTHORITY = {
    "HUMAN_PI_BLOCK_03_PERSISTENCE_ARCHITECTURE_DECISION_V1": "ADOPTED",
    "BLOCK_03_MATERIALIZATION_OUTCOME_ADJUDICATION_V1": "HUMAN_PI_ACCEPTED",
    "BLOCK_03_MATERIALIZATION_OUTCOME_PERSISTENCE_V5": "AUTHORIZED",
    "authority_source": "HUMAN_PI_CURRENT_TRANSACTION_INSTRUCTION",
    "instruction_sha256": INSTRUCTION_SHA256,
}
LIFECYCLE = {
    "status": "PERSISTED_CANDIDATE", "human_pi_accepted": True,
    "persisted": True, "frozen": False, "committed": False, "remote_published": False,
}


class StateValidationError(RuntimeError):
    """The successor cannot be certified from the supplied persisted evidence."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise StateValidationError(message)


def _same(actual: Any, expected: Any, message: str) -> None:
    # JSON equality also distinguishes booleans from integers.
    _require(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True), message)


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json(path: Path) -> Any:
    def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            _require(key not in result, f"duplicate JSON field: {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def capture_first_pass_evidence(root: Path) -> dict[str, Any]:
    """Extract existing files and verify their hashes; never invoke the materializer."""
    for name, digest in SOURCE_HASHES.items():
        _require(_hash(root / name) == digest, f"production source drift: {name}")
    completion = _json(root / "first_pass_completion.json")
    ledger = _json(root / "identity_ledger.json")
    audit = _json(root / "post_run_audit.json")
    with (root / "materialization_results.csv").open(newline="", encoding="utf-8") as handle:
        results = list(csv.DictReader(handle, strict=True))
    identities = []
    for row, controller in zip(results, ledger, strict=True):
        case, label = row["case_id"], row["revision_label"]
        _same([case, label, row["status"]],
              [controller["case_id"], controller["revision_label"], controller["outcome"]],
              "controller/results identity mismatch")
        _require(controller["attempt_dispatched"] is True
                 and controller["governed_attempt_consumed"] is True,
                 "production attempt not consumed")
        attempt_path, log_path = Path(row["attempt_evidence"]), Path(row["build_log"])
        attempt = _json(attempt_path)
        _require(_hash(attempt_path) == controller["attempt_json_sha256"], "attempt hash drift")
        _require(attempt["synthetic_only"] is False and attempt["materializer_commit"] == ENTRY_HEAD,
                 "attempt is not the governed production first pass")
        _same(attempt["status"], row["status"], "attempt outcome drift")
        _require(len(attempt["revisions"]) == 1, "unexpected identity multiplicity")
        revision = attempt["revisions"][0]
        _same([revision["canonical_case_id"], revision["revision_label"]],
              [case, label], "attempt identity drift")
        _require(_hash(log_path) == revision["build_log_sha256"], "build log drift")
        identities.append({
            "case_id": case, "candidate_rank": int(row["candidate_rank"]),
            "revision_label": label, "status": row["status"], "controller_state": controller["state"],
            "first_pass_attempt_consumed": row["ATTEMPT_CONSUMED"],
            "first_pass_attempt_dispatched": row["ATTEMPT_DISPATCHED"],
            "attempt_path": str(attempt_path.relative_to(root)),
            "attempt_sha256": controller["attempt_json_sha256"],
            "build_log_path": str(log_path.relative_to(root)),
            "build_log_sha256": revision["build_log_sha256"],
            "final_image_id": revision.get("final_image_id", "NA"),
            "environment_identity_sha256": revision.get("environment_identity_sha256", "NA"),
            "installed_distribution_manifest_sha256":
                revision.get("installed_distribution_manifest_sha256", "NA"),
        })
    return {
        "schema": "BLOCK_03_FIRST_PASS_EVIDENCE_EXTRACT_V5",
        "production_root": str(PRODUCTION_ROOT), "source_sha256": SOURCE_HASHES,
        "completion": completion, "identities": identities,
        "post_run_scientific_state": {key: audit[key] for key in (
            "execution_head", "attempts_consumed", "attempts_dispatched", "canonical_runtime_counts",
            "environment_ready_before", "environment_ready_after", "new_factual_environment_ready_cases",
            "oracle_outcomes", "cases_manifest", "eligibility_established",
            "BUGGY_ORACLE_EXECUTED", "FIXED_ORACLE_EXECUTED", "ORACLE_SCREENING_PERFORMED",
            "ORACLE_SCREENING_NOT_AUTHORIZED",
        )},
    }


def validate_first_pass_evidence(evidence: dict[str, Any]) -> None:
    _same(sorted(evidence), sorted(("schema", "production_root", "source_sha256", "completion",
                                   "identities", "post_run_scientific_state")), "evidence schema drift")
    _same(evidence["schema"], "BLOCK_03_FIRST_PASS_EVIDENCE_EXTRACT_V5", "evidence version drift")
    _same(evidence["production_root"], str(PRODUCTION_ROOT), "evidence root drift")
    _same(evidence["source_sha256"], SOURCE_HASHES, "first-pass source identity drift")
    completion = evidence["completion"]
    _same({k: completion[k] for k in (
        "attempts_consumed", "identities", "counts", "oracle_screening_performed", "status",
    )}, {
        "attempts_consumed": 14, "identities": 14,
        "counts": {"BUILD_FAILED": 10, "MATERIALIZED": 4}, "oracle_screening_performed": False,
        "status": "BLOCK_03_FIRST_PASS_MATERIALIZATION_COMPLETE",
    }, "first-pass completion drift")
    identities = evidence["identities"]
    _same([(r["case_id"], r["candidate_rank"], r["revision_label"]) for r in identities],
          [(case, rank, label) for case, rank in MEMBERSHIP for label in ("BUGGY", "FIXED")],
          "first-pass ordered membership/pairs drift")
    for order, (case, _) in enumerate(MEMBERSHIP, 1):
        for row in identities[(order - 1) * 2:order * 2]:
            expected_status = "MATERIALIZED" if case in READY else "BUILD_FAILED"
            _same(row["status"], expected_status, f"first-pass outcome drift: {case}")
            _same([row["controller_state"], row["first_pass_attempt_consumed"],
                   row["first_pass_attempt_dispatched"]], ["CLOSED", "YES", "YES"],
                  f"first-pass attempt state drift: {case}")
            label = row["revision_label"]
            folder = f"attempts/block03_{order:02d}_{case.replace('::', '__')}_{label.lower()}"
            _same([row["attempt_path"], row["build_log_path"]],
                  [folder + "/attempt.json", folder + f"/{label}/build.log"], "evidence path drift")
            for field in ("attempt_sha256", "build_log_sha256"):
                _require(bool(re.fullmatch(r"[0-9a-f]{64}", row[field])), "invalid evidence hash")
            for field in ("environment_identity_sha256", "installed_distribution_manifest_sha256"):
                _require(bool(re.fullmatch(r"[0-9a-f]{64}", row[field])) if case in READY
                         else row[field] == "NA", "incomplete or invented materialized identity")
            _require(bool(re.fullmatch(r"sha256:[0-9a-f]{64}", row["final_image_id"]))
                     if case in READY else row["final_image_id"] == "NA", "final image identity drift")
    _same(dict(Counter(r["status"] for r in identities)),
          {"MATERIALIZED": 4, "BUILD_FAILED": 10}, "first-pass accounting drift")
    _same(evidence["post_run_scientific_state"], {
        "execution_head": ENTRY_HEAD, "attempts_consumed": 14, "attempts_dispatched": 14,
        "canonical_runtime_counts": {"BUILD_FAILED": 10, "MATERIALIZED": 4},
        "environment_ready_before": 26, "environment_ready_after": 28,
        "new_factual_environment_ready_cases": READY, "oracle_outcomes": 0,
        "cases_manifest": "header-only", "eligibility_established": False,
        "BUGGY_ORACLE_EXECUTED": False, "FIXED_ORACLE_EXECUTED": False,
        "ORACLE_SCREENING_PERFORMED": False, "ORACLE_SCREENING_NOT_AUTHORIZED": True,
    }, "first-pass capacity/scientific state drift")


def evidence_reference(evidence: dict[str, Any], case: str) -> str:
    references = [f"evaluation/downstream_benchmark/{EVIDENCE}#case_id={case}"]
    for row in evidence["identities"]:
        if row["case_id"] == case:
            references.extend((
                str(PRODUCTION_ROOT / row["attempt_path"]) + "#sha256=" + row["attempt_sha256"],
                str(PRODUCTION_ROOT / row["build_log_path"]) + "#sha256=" + row["build_log_sha256"],
            ))
    return "; ".join(references)


def expected_state(root: Path) -> dict[str, Any]:
    return {
        "schema": "PRE_ELIGIBILITY_CURRENT_STATE_V5", "version": "V5",
        "authority": AUTHORITY, "entry_head": ENTRY_HEAD,
        "predecessor": {
            "version": "V4", "role": "HISTORICAL_FROZEN_PREDECESSOR", "freeze_commit": V4_COMMIT,
            "accepted_exclusions": 34,
            "reason_counts": {"UNSUPPORTED_ENVIRONMENT": 9, "DEPENDENCY_SETUP_FAILURE": 23,
                              "ORACLE_COMMAND_INVALID": 2},
            "sha256": PREDECESSOR_HASHES,
        },
        "successor": {
            "role": "CURRENT_PRE_ELIGIBILITY_SUCCESSOR", "accepted_exclusions": 39,
            "reason_counts": {"UNSUPPORTED_ENVIRONMENT": 11, "DEPENDENCY_SETUP_FAILURE": 26,
                              "ORACLE_COMMAND_INVALID": 2},
            "exact_block_03_delta": DELTA, "permanent_non_retry_cases": list(DELTA),
            "permanent_non_retry_authority": "HUMAN_PI_ACCEPTED",
            "sha256": {name: _hash(root / name) for name in (EXCLUSIONS, DISPOSITIONS, EVIDENCE)},
        },
        "capacity": CAPACITY, "scientific_state": SCIENTIFIC, "lifecycle": LIFECYCLE,
        "state_document": DOCUMENT, "persistence_record": RECORD, "current_state_validator": VALIDATOR,
        "supersedes_v4_as_current_state_only": True, "mutates_v4_historical_authority": False,
        "next_gate": "HUMAN_PI_REVIEW_OF_BLOCK_03_MATERIALIZATION_OUTCOME_PERSISTENCE_V5",
    }


def validate_successor(root: Path, *, verify_production_evidence: bool = False) -> dict[str, Any]:
    """Validate frozen V4, successor relation, and V5; all operations are reads."""
    try:
        for name, digest in PREDECESSOR_HASHES.items():
            _require(_hash(root / name) == digest, f"frozen predecessor/binding drift: {name}")
        executor.validate_controlling_inputs(root)
        _require(_hash(root / EVIDENCE) == EVIDENCE_SHA256, "persisted first-pass evidence hash drift")
        evidence = _json(root / EVIDENCE)
        validate_first_pass_evidence(evidence)
        if verify_production_evidence:
            _same(capture_first_pass_evidence(PRODUCTION_ROOT), evidence, "live/persisted evidence drift")
            _require(not list((PRODUCTION_ROOT.parent / "screening_evidence").rglob("*.json")),
                     "oracle outcomes exist in screening_evidence")
        old = executor._read_exact_csv(root / "exclusions.csv", executor.EXCLUSION_FIELDS)
        union = executor._read_exact_csv(root / EXCLUSIONS, executor.EXCLUSION_FIELDS)
        _require((root / EXCLUSIONS).read_bytes().startswith((root / "exclusions.csv").read_bytes()),
                 "V4 byte prefix changed in V5")
        _require(len(union) == 39 and len({r["case_id"] for r in union}) == 39,
                 "V5 must contain 39 unique cases")
        _same(union[:34], old, "historical V4 row/reason drift")
        _same([r["case_id"] for r in union[34:]], list(DELTA), "exact ordered Block-03 delta drift")
        _same(dict(Counter(r["exclusion_reason"] for r in union)),
              {"UNSUPPORTED_ENVIRONMENT": 11, "DEPENDENCY_SETUP_FAILURE": 26,
               "ORACLE_COMMAND_INVALID": 2}, "V5 reason split drift")
        disposition = executor._read_exact_csv(root / DISPOSITIONS, DISPOSITION_FIELDS)
        _same([r["canonical_case_id"] for r in disposition], list(DELTA), "NON_RETRY case-set drift")
        timestamps = {r["recorded_at_utc"] for r in union[34:]}
        _require(len(timestamps) == 1 and bool(re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", next(iter(timestamps)))),
            "V5 delta must have one UTC transaction timestamp")
        for norm, row in zip(disposition, union[34:], strict=True):
            case = norm["canonical_case_id"]
            project, bug = case.split("::")
            order = next(i for i, (c, _) in enumerate(MEMBERSHIP, 1) if c == case)
            group = "ARTIFACT_PYWIN32_227" if project == "sanic" else "ARTIFACT_PKG_RESOURCES_0_0_0"
            expected = {
                "expansion_block": "3", "expansion_order": str(order), "canonical_case_id": case,
                "source_project": project, "bugsinpy_bug_id": bug, "required_identity_count": "2",
                "failed_identities": "BUGGY;FIXED", "first_pass_environment_status": "BUILD_FAILED",
                "eligibility_stage": "ENVIRONMENT_MATERIALIZATION",
                "failure_family": "DEPENDENCY_INSTALLATION_FAILURE", "systemic_group": group,
                "final_exclusion_reason": DELTA[case], "retry_policy": "PERMANENT_NON_RETRY",
                "human_pi_adjudication": "ACCEPTED_EXCLUSION",
                "first_pass_evidence_reference": evidence_reference(evidence, case),
                "notes": "Explicit Human-PI adjudication; attempt consumption does not imply "
                         "NON_RETRY; no oracle or eligibility outcome.",
                "first_pass_attempt_consumed": "YES", "permanent_non_retry": "YES",
                "decision_authority": "HUMAN_PI_ACCEPTED",
            }
            _same(norm, expected, f"accepted disposition drift: {case}")
            _same({k: row[k] for k in ("case_id", "source_project", "bugsinpy_bug_id",
                                       "eligibility_stage", "exclusion_reason", "evidence_reference",
                                       "notes")}, {
                "case_id": case, "source_project": project, "bugsinpy_bug_id": bug,
                "eligibility_stage": "ENVIRONMENT_MATERIALIZATION", "exclusion_reason": DELTA[case],
                "evidence_reference": norm["first_pass_evidence_reference"],
                "notes": "BLOCK_03_MATERIALIZATION_OUTCOME_ADJUDICATION_V1; "
                         "PERMANENT_NON_RETRY; HUMAN_PI_ACCEPTED; first-pass BUILD_FAILED; "
                         "no oracle or eligibility outcome.",
            }, f"V5 exclusion disposition drift: {case}")
        _same(_json(root / STATE), expected_state(root), "V5 descriptor/authority/capacity/lifecycle drift")
        admission_counts = [len(executor._read_exact_csv(root / "screening_execution_plan.csv",
                                                        executor.PLAN_FIELDS))]
        for name in ("expansion_block_01.csv", "expansion_block_02.csv", "expansion_block_03.csv"):
            with (root / name).open(newline="", encoding="utf-8") as handle:
                admission_counts.append(len(list(csv.DictReader(handle, strict=True))))
        _same(admission_counts, [40, 10, 10, 7], "metadata admission accounting drift")
        _require(26 + len(READY) == 28 == CAPACITY["required_slots"], "capacity reconciliation failed")
        _require(not [p for p in root.rglob("*") if "block_04" in p.name.lower()], "Block-04 exists")
        document, record = (root / DOCUMENT).read_text(), (root / RECORD).read_text()
        for text in (document, record):
            for marker in ("MATERIALIZED != ELIGIBLE", "ORACLE_SCREENING_NOT_AUTHORIZED",
                           "V5 supersedes V4 AS CURRENT STATE ONLY",
                           "HUMAN_PI_REVIEW_OF_BLOCK_03_MATERIALIZATION_OUTCOME_PERSISTENCE_V5"):
                _require(marker in text, f"missing current-state boundary: {marker}")
        _require(_hash(root / STATE) in document, "state document lacks descriptor identity")
        for name in CREATED_PATHS:
            if name != RECORD:
                _require(f"`{name}` | `{_hash(root / name)}`" in record,
                         f"persistence record lacks exact artifact binding: {name}")
        return {"status": "PRE_ELIGIBILITY_EXCLUSIONS_LEDGER_STATE_V5_VALIDATED",
                "V4_validation": "PASS", "successor_relation": "PASS", "accepted_exclusions": 39,
                "reason_counts": {"UNSUPPORTED_ENVIRONMENT": 11, "DEPENDENCY_SETUP_FAILURE": 26,
                                  "ORACLE_COMMAND_INVALID": 2},
                "capacity": CAPACITY, "scientific_state": SCIENTIFIC, "lifecycle": LIFECYCLE}
    except (OSError, UnicodeError, csv.Error, ValueError, KeyError, TypeError,
            executor.PreparationError) as exc:
        raise StateValidationError(f"V5 validation failed: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--verify-production-evidence", action="store_true",
                        help="read and hash the original governed evidence; execute nothing")
    args = parser.parse_args()
    try:
        print(json.dumps(validate_successor(args.benchmark_root,
                         verify_production_evidence=args.verify_production_evidence), indent=2))
    except StateValidationError as exc:
        parser.exit(1, f"BLOCKED: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Synthetic state mutations only; no production engine, subject, or Git writes."""

from __future__ import annotations

import copy
import csv
import json
import shutil
from pathlib import Path
from unittest import mock

import pytest

from evaluation.downstream_benchmark.screening import validate_pre_eligibility_state_v5 as v5


ROOT = Path(__file__).resolve().parents[1]
V4_INPUTS = (
    "PROTOCOL.md", "RUN_SPEC_V1.md", "candidate_universe.csv",
    "initial_40_build_failure_adjudication_v1.csv", "expansion_block_01.csv",
    "expansion_block_01_environment_materialization.csv",
    "expansion_block_01_build_failure_adjudication_v1.csv", "expansion_block_02.csv",
    "expansion_block_02_execution_plan.csv", "expansion_block_02_environment_build_recipes.csv",
    "expansion_block_02_preparation_blocker_adjudication_v1.csv",
    "expansion_block_02_environment_materialization.csv",
    "expansion_block_02_build_failure_adjudication_v1.csv", "screening_execution_plan.csv",
)


@pytest.fixture
def candidate(tmp_path: Path) -> Path:
    for name in set(V4_INPUTS) | set(v5.PREDECESSOR_HASHES) | set(v5.CREATED_PATHS):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    return tmp_path


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_rows(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def test_persisted_successor_and_predecessor_pass_without_process_or_production_reads() -> None:
    with mock.patch.object(v5.executor.subprocess, "run", side_effect=AssertionError("process")), \
         mock.patch.object(v5, "capture_first_pass_evidence", side_effect=AssertionError("production")):
        v5.executor.validate_controlling_inputs(ROOT)
        result = v5.validate_successor(ROOT)
    assert result["successor_relation"] == "PASS"
    assert result["accepted_exclusions"] == 39
    assert result["capacity"]["resulting_environment_ready"] == 28
    assert result["scientific_state"]["eligibility_established"] == "NO"
    assert result["lifecycle"]["frozen"] is False


def test_frozen_v4_rejects_synthetic_successor_without_modification() -> None:
    read = v5.executor._read_exact_csv
    successor = read(ROOT / v5.EXCLUSIONS, v5.executor.EXCLUSION_FIELDS)
    def substitute(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
        return successor if path == ROOT / "exclusions.csv" else read(path, fields)
    before = (ROOT / "exclusions.csv").read_bytes()
    with mock.patch.object(v5.executor, "_read_exact_csv", side_effect=substitute):
        with pytest.raises(v5.executor.PreparationError, match="adjudicated union"):
            v5.executor.validate_controlling_inputs(ROOT)
    assert (ROOT / "exclusions.csv").read_bytes() == before


@pytest.mark.parametrize("name", list(v5.PREDECESSOR_HASHES))
def test_each_frozen_predecessor_binding_rejects_drift(candidate: Path, name: str) -> None:
    path = candidate / name
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(v5.StateValidationError, match="predecessor/binding drift"):
        v5.validate_successor(candidate)


@pytest.mark.parametrize("mutation", [
    "missing historical", "historical reason", "historical timestamp", "duplicate",
    "missing delta", "extra", "delta order", "delta reason", "reason swap same split",
    "ready case exclusion", "delta identity", "evidence reference", "timestamp", "schema",
])
def test_exact_union_rejects_mutations(candidate: Path, mutation: str) -> None:
    path = candidate / v5.EXCLUSIONS
    fields, rows = read_rows(path)
    if mutation == "missing historical":
        rows.pop(0)
    elif mutation == "historical reason":
        rows[0]["exclusion_reason"] = "ORACLE_COMMAND_INVALID"
    elif mutation == "historical timestamp":
        rows[0]["recorded_at_utc"] = "2026-10-03T00:00:00Z"
    elif mutation == "duplicate":
        rows[-1] = rows[-2].copy()
    elif mutation == "missing delta":
        rows.pop()
    elif mutation == "extra":
        rows.append(dict(rows[-1], case_id="invented::1"))
    elif mutation == "delta order":
        rows[-1], rows[-2] = rows[-2], rows[-1]
    elif mutation == "delta reason":
        rows[-1]["exclusion_reason"] = "UNSUPPORTED_ENVIRONMENT"
    elif mutation == "reason swap same split":
        rows[34]["exclusion_reason"], rows[35]["exclusion_reason"] = (
            rows[35]["exclusion_reason"], rows[34]["exclusion_reason"],
        )
    elif mutation == "ready case exclusion":
        rows[-1]["case_id"] = "PySnooper::3"
    elif mutation == "delta identity":
        rows[-1]["source_project"] = "sanic"
    elif mutation == "evidence reference":
        rows[-1]["evidence_reference"] = "unbound"
    elif mutation == "timestamp":
        rows[-1]["recorded_at_utc"] = "2026-10-03T00:00:00Z"
    else:
        fields.remove("notes")
        rows = [{k: val for k, val in row.items() if k in fields} for row in rows]
    write_rows(path, fields, rows)
    with pytest.raises(v5.StateValidationError):
        v5.validate_successor(candidate)


@pytest.mark.parametrize("field,value", [
    ("retry_policy", "NON_RETRY"), ("retry_policy", "ATTEMPT_CONSUMED"),
    ("permanent_non_retry", "NO"), ("decision_authority", "MECHANICALLY_INFERRED"),
    ("human_pi_adjudication", "PROPOSED_EXCLUSION"), ("first_pass_attempt_consumed", "NO"),
    ("final_exclusion_reason", "UNSUPPORTED_ENVIRONMENT"), ("failed_identities", "BUGGY"),
    ("required_identity_count", "1"), ("first_pass_evidence_reference", "unbound"),
])
def test_disposition_authority_and_attempt_consumption_are_independent(
    candidate: Path, field: str, value: str,
) -> None:
    path = candidate / v5.DISPOSITIONS
    fields, rows = read_rows(path)
    rows[0][field] = value
    write_rows(path, fields, rows)
    with pytest.raises(v5.StateValidationError, match="accepted disposition drift"):
        v5.validate_successor(candidate)


@pytest.mark.parametrize("section,field,value", [
    ("capacity", "entry_environment_ready", 27),
    ("capacity", "new_environment_ready", 3),
    ("capacity", "resulting_environment_ready", 29),
    ("capacity", "required_slots", 24),
    ("capacity", "capacity_requirement_met", "NO"),
    ("capacity", "new_complete_materialized_cases", ["PySnooper::1", "PySnooper::2"]),
    ("scientific_state", "oracle_outcomes", 1),
    ("scientific_state", "oracle_outcomes", False),
    ("scientific_state", "eligibility_established", "YES"),
    ("scientific_state", "oracle_screening_authorized", True),
    ("scientific_state", "pilot_final_allocation_performed", True),
    ("lifecycle", "frozen", True), ("lifecycle", "committed", True),
    ("lifecycle", "remote_published", True),
    ("authority", "HUMAN_PI_BLOCK_03_PERSISTENCE_ARCHITECTURE_DECISION_V1", "PROPOSED"),
    ("authority", "BLOCK_03_MATERIALIZATION_OUTCOME_ADJUDICATION_V1", "PROPOSED"),
    ("successor", "permanent_non_retry_cases", ["tqdm::6"]),
    ("predecessor", "freeze_commit", "0" * 40),
])
def test_current_descriptor_rejects_state_authority_capacity_and_lifecycle_drift(
    candidate: Path, section: str, field: str, value: object,
) -> None:
    path = candidate / v5.STATE
    state = json.loads(path.read_text())
    state[section][field] = value
    path.write_text(json.dumps(state))
    with pytest.raises(v5.StateValidationError, match="descriptor/authority/capacity/lifecycle"):
        v5.validate_successor(candidate)


@pytest.mark.parametrize("mutation", [
    "consumed count", "outcome counts", "missing identity", "duplicate identity", "wrong pair",
    "consumed", "closed", "wrong outcome", "ready evidence incomplete", "capacity pair",
    "oracle", "eligibility", "source hash", "path traversal",
])
def test_first_pass_semantics_fail_closed_independent_of_snapshot_hash(mutation: str) -> None:
    evidence = copy.deepcopy(json.loads((ROOT / v5.EVIDENCE).read_text()))
    identities = evidence["identities"]
    audit = evidence["post_run_scientific_state"]
    if mutation == "consumed count":
        evidence["completion"]["attempts_consumed"] = 13
    elif mutation == "outcome counts":
        evidence["completion"]["counts"] = {"MATERIALIZED": 6, "BUILD_FAILED": 8}
    elif mutation == "missing identity":
        identities.pop()
    elif mutation == "duplicate identity":
        identities[-1] = identities[-2].copy()
    elif mutation == "wrong pair":
        identities[3]["revision_label"] = "BUGGY"
    elif mutation == "consumed":
        identities[0]["first_pass_attempt_consumed"] = "NO"
    elif mutation == "closed":
        identities[0]["controller_state"] = "OPEN"
    elif mutation == "wrong outcome":
        identities[0]["status"] = "MATERIALIZED"
    elif mutation == "ready evidence incomplete":
        identities[2]["environment_identity_sha256"] = "NA"
    elif mutation == "capacity pair":
        audit["new_factual_environment_ready_cases"] = ["PySnooper::3", "PySnooper::1"]
    elif mutation == "oracle":
        audit["oracle_outcomes"] = 1
    elif mutation == "eligibility":
        audit["eligibility_established"] = True
    elif mutation == "source hash":
        evidence["source_sha256"]["identity_ledger.json"] = "0" * 64
    else:
        identities[0]["attempt_path"] = "../attempt.json"
    with pytest.raises(v5.StateValidationError):
        v5.validate_first_pass_evidence(evidence)


def test_persisted_evidence_hash_drift(candidate: Path) -> None:
    path = candidate / v5.EVIDENCE
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(v5.StateValidationError, match="evidence hash drift"):
        v5.validate_successor(candidate)


@pytest.mark.parametrize("name", [v5.DOCUMENT, v5.RECORD])
def test_future_consumer_boundary_cannot_be_removed(candidate: Path, name: str) -> None:
    path = candidate / name
    path.write_text(path.read_text().replace("ORACLE_SCREENING_NOT_AUTHORIZED", ""))
    with pytest.raises(v5.StateValidationError, match="current-state boundary"):
        v5.validate_successor(candidate)


def test_persistence_record_requires_validator_hash_binding(candidate: Path) -> None:
    path = candidate / v5.RECORD
    path.write_text(path.read_text().replace(v5._hash(candidate / v5.VALIDATOR), "0" * 64))
    with pytest.raises(v5.StateValidationError, match="artifact binding"):
        v5.validate_successor(candidate)


def test_duplicate_json_fields_are_rejected(candidate: Path) -> None:
    path = candidate / v5.STATE
    content = path.read_text()
    path.write_text(content.replace('"version": "V5"', '"version": "V5", "version": "V5"'))
    with pytest.raises(v5.StateValidationError, match="duplicate JSON field"):
        v5.validate_successor(candidate)


def test_block_04_is_rejected(candidate: Path) -> None:
    with mock.patch.object(Path, "rglob", return_value=iter([Path("expansion_block_04.csv")])):
        with pytest.raises(v5.StateValidationError, match="Block-04 exists"):
            v5.validate_successor(candidate)

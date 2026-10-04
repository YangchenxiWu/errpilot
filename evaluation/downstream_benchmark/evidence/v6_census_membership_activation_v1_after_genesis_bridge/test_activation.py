"""Candidate-specific rejection coverage; all mutations are in-memory copies."""

import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "activation_candidate_validator", Path(__file__).with_name("validate_activation.py")
)
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


@pytest.fixture(scope="module")
def audited():
    return a.audit()


def test_real_candidate_replays_exactly(audited):
    assert audited["failed"] == 0
    assert audited["positive_count"] >= 20


def test_required_rejection_coverage(audited):
    names = {probe["probe"] for probe in audited["rejection_matrix"]}
    assert {
        "wrong_bridge_hash",
        "unaccepted_bridge",
        "unpublished_bridge",
        "wrong_bridge_closure",
        "wrong_predecessor_descriptor",
        "wrong_raw_projection",
        "wrong_qualified_projection",
        "Q_reapplied_twice",
        "first_sequence_not_1",
        "first_previous_event_non_null",
        "wrong_lifecycle_from",
        "wrong_lifecycle_to",
        "synthetic_backfill",
        "arbitrary_event_id",
        "event_id_mismatch",
        "event_id_self_reference",
        "evidence_reference_drift",
        "wrong_supersession_reference",
        "pool_hash_drift",
        "member_addition",
        "member_omission",
        "member_reorder",
        "preparation_enabled",
        "oracle_enabled",
        "allocation_enabled",
        "scientific_outcome_changed",
        "event_count_not_1",
        "wrong_event_head",
        "candidate_treated_as_canonical",
        "runtime_authority_enabled",
        "auto_promotion_enabled",
        "canonical_v6_current_state_mutation",
    } <= names
    assert all(probe["status"] == "PASS_REJECTED" for probe in audited["rejection_matrix"])


def test_canonical_firewall_after_all_probes(audited):
    predecessor = a.v.loads((a.ROOT / a.v.CURRENT_PATH).read_bytes())
    assert (
        a.v.sha((a.ROOT / a.v.CURRENT_PATH).read_bytes())
        == a.v.IDENTITIES["predecessor_descriptor"][1]
    )
    assert predecessor["event_count"] == 0
    assert predecessor["event_head"] is None
    assert predecessor["projection"]["lifecycle"]["V6_ACTIVATED"] == "NO"
    assert audited["tracked_diff_empty"] and audited["index_empty"]

"""In-memory contract rejection matrix and non-production schema/gate tests.

No reservation algorithm is invoked, and no pilot or final case IDs are computed.
Synthetic accepted gates/outcomes below are fixture values, never authority files.
"""

import copy
import importlib.util
from pathlib import Path

import pytest

_path = Path(__file__).with_name("validate_contract.py")
_spec = importlib.util.spec_from_file_location("v6_contract_auditor", _path)
v = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v)


def event_fixture(data):
    current = copy.deepcopy(data["state"]["projection"])
    initial = copy.deepcopy(current)
    events, authorities, descriptors = [], {}, []
    previous = None
    contract_sha = v.sha(v.B / "v6_capacity_successor_contract.json")
    for index, edge in enumerate(data["lifecycle"]["transitions"][:2], 1):
        # These digests label synthetic old descriptor bytes, not repository current state.
        old_descriptor = v.digest(
            {"namespace": "CANDIDATE_TEST_ONLY", "fixture_index": index, "projection": current}
        )
        descriptors.append(old_descriptor)
        auth = {
            "path": "synthetic-gate-" + str(index),
            "namespace": "CANDIDATE_TEST_ONLY",
            "owner": "HUMAN_PI",
            "gate": edge["gate"],
            "contract_sha256": contract_sha,
            "prior_projection_sha256": v.digest(current),
        }
        auth_sha = v.digest(auth)
        authorities[auth_sha] = auth
        result = v.phase_flags_for_edge(current, edge["to"])
        event = {
            "schema": "V6_CAPACITY_STATE_EVENT_V1",
            "namespace": "CANDIDATE_TEST_ONLY",
            "event_id": "synthetic-event-" + str(index),
            "sequence": index,
            "kind": "STATE_TRANSITION",
            "previous_event_identity": previous,
            "previous_descriptor_sha256": old_descriptor,
            "contract_sha256": contract_sha,
            "predecessor": data["manifest"]["predecessor"],
            "authority_reference": {"path": auth["path"], "sha256": auth_sha},
            "gate": edge["gate"],
            "from_state": edge["from"],
            "to_state": edge["to"],
            "prior_projection_sha256": v.digest(current),
            "result_projection_sha256": v.digest(result),
            "next_projection": result,
            "evidence_references": [],
            "supersession_reference": None,
        }
        events.append(event)
        previous = {
            "event_id": event["event_id"],
            "sequence": index,
            "event_sha256": v.digest(event),
        }
        current = result
    return initial, events, authorities, descriptors, contract_sha


def seven_fixture(data):
    policy = copy.deepcopy(data["run"]["unresolved_seven"])
    head = {"path": "synthetic-seven-track-head", "sha256": "1" * 64}
    identity = {"path": "synthetic-seven-outcome", "sha256": "2" * 64}
    closure = {
        "identity": {"path": "synthetic-accepted-census-closure", "sha256": "3" * 64},
        "fixed_seven_track_head": head,
        "effective_outcomes_at_fixed_head": [identity],
    }
    cutoff = {
        "cutoff": "FIRST_COMBINED_POOL_INPUT_FREEZE",
        "fixed_seven_track_head": head,
        "accepted_census_closure": closure["identity"],
        "late_inclusion": False,
        "cutoff_refresh": False,
    }
    outcomes = [
        {
            "case_id": policy["case_ids"][0],
            "identity": identity,
            "observed_head": head,
            "lifecycle": {k: "YES" for k in policy["required_lifecycle"]},
            "REMOTE_PUBLISHED": "NO",
            "classification": "ELIGIBLE",
            "valid_slots": 6,
            "buggy": ["FAIL"] * 3,
            "fixed": ["PASS"] * 3,
            "new_attempt_id": "synthetic-new",
            "old_attempt_id": "synthetic-old",
            "exact_supersession": True,
            "old_infrastructure_slots_reused": False,
        }
    ]
    return policy, cutoff, closure, outcomes


def rejection_matrix(data=None):
    data = v.bundle() if data is None else data
    results = []

    def rejection(name, action):
        try:
            action()
        except ValueError as exc:
            results.append({"check": name, "status": "PASS_REJECTED", "reason": str(exc)})
        else:
            raise AssertionError("mutation incorrectly accepted: " + name)

    def changed(name, mutation):
        modified = copy.deepcopy(data)
        mutation(modified)
        rejection(name, lambda: v.validate_bundle(modified))

    # Each of the required 28 rejection categories is represented by a named probe.
    mutations = [
        ("01_wrong_predecessor_HEAD", lambda d: d["protocol"]["predecessor"].update(head="0" * 40)),
        (
            "02_wrong_BugsInPy_commit",
            lambda d: d["protocol"]["predecessor"].update(source_commit="0" * 40),
        ),
        (
            "02_wrong_BugsInPy_tree",
            lambda d: d["protocol"]["predecessor"].update(source_tree="0" * 40),
        ),
        (
            "03_wrong_candidate_universe_hash",
            lambda d: d["protocol"]["predecessor"].update(candidate_universe_sha256="0" * 64),
        ),
        ("04_wrong_seed", lambda d: d["run"]["predecessor"].update(seed=1)),
        ("05_pool_count_432", lambda d: d["pool"].pop()),
        ("05_pool_count_434", lambda d: d["pool"].append(copy.deepcopy(d["pool"][-1]))),
        ("06_pool_membership_drift", lambda d: d["pool"][0].update(case_id="pandas::999")),
        ("07_pool_order_drift", lambda d: d["pool"].reverse()),
        ("08_historical_admission_overlap", lambda d: d["pool"][0].update(case_id="pandas::102")),
        ("09_accepted_exclusion_overlap", lambda d: d["pool"][0].update(case_id="scrapy::4")),
        ("10_screened_case_overlap", lambda d: d["pool"][0].update(case_id="youtube-dl::7")),
        (
            "11_wrong_predecessor_disposition",
            lambda d: d["pool"][0].update(predecessor_disposition="ADMIT"),
        ),
        ("12_altered_3x3_rule", lambda d: d["screen"]["screening"].update(majority_vote=True)),
        (
            "13_altered_24_plus_4",
            lambda d: d["run"]["allocation_invariants"].update(final_count=23),
        ),
        (
            "14_altered_final_project_cap",
            lambda d: d["run"]["allocation_invariants"].update(final_sample_project_cap=5),
        ),
        ("15_stop_at_28", lambda d: d["screen"]["census"].update(stop_at_28=True)),
        (
            "16_governed_batch_admission",
            lambda d: d["screen"]["census"].update(batch_admission_authority="TEN_MEMBER_BLOCKS"),
        ),
        (
            "17_new_scientific_failure_reason",
            lambda d: d["screen"]["canonical_failure_reasons"].append("CAPACITY_REJECTION"),
        ),
        (
            "18_competing_current_authority",
            lambda d: d["state"]["authoritative_current_surfaces"].extend(
                ["v6_current_state.json", "csv_current"]
            ),
        ),
        (
            "20_D6_cutoff_refresh",
            lambda d: d["run"]["unresolved_seven"].update(cutoff_refresh=True),
        ),
        (
            "21_late_seven_inclusion_policy",
            lambda d: d["protocol"]["unresolved_seven"].update(late_inclusion=True),
        ),
        (
            "22_pilot_feasibility_lookahead",
            lambda d: d["run"]["pilot"].update(final_feasibility_lookahead="YES"),
        ),
        ("23_pilot_reselection", lambda d: d["run"].update(pilot_reselection="ALLOWED")),
        ("24_pilot_reseed", lambda d: d["run"]["pilot"].update(seed=20260923)),
        (
            "25_pilot_promotion",
            lambda d: d["run"]["pilot"].update(pilot_promotion_to_final="ALLOWED"),
        ),
        (
            "26_changed_final_selection_algorithm",
            lambda d: d["run"]["allocation_invariants"].update(final_algorithm="FIRST_24"),
        ),
        (
            "27_automatic_successor_on_exhaustion",
            lambda d: d["protocol"].update(automatic_successor_on_exhaustion=True),
        ),
        (
            "28_implicit_downstream_authority",
            lambda d: d["lifecycle"]["transitions"][7].update(automatic_next_authority=True),
        ),
        (
            "extra_descriptor_event_disagreement",
            lambda d: d["state"].update(projection_sha256="0" * 64),
        ),
        (
            "extra_candidate_activated",
            lambda d: d["state"]["projection"]["lifecycle"].update(V6_ACTIVATED="YES"),
        ),
        (
            "extra_candidate_preparation_authorized",
            lambda d: d["state"]["projection"]["lifecycle"].update(PREPARATION_AUTHORIZED="YES"),
        ),
        (
            "extra_candidate_oracle_authorized",
            lambda d: d["state"]["projection"]["lifecycle"].update(ORACLE_AUTHORIZED="YES"),
        ),
        (
            "extra_candidate_membership_effective",
            lambda d: d["state"]["projection"]["lifecycle"].update(
                CENSUS_MEMBERSHIP_EFFECTIVE="YES"
            ),
        ),
        (
            "extra_held_unresolved_scientific_failure",
            lambda d: d["screen"]["held_unresolved"].update(scientific_failure="YES"),
        ),
        (
            "extra_held_unresolved_eligible",
            lambda d: d["screen"]["held_unresolved"].update(eligible="YES"),
        ),
        (
            "extra_held_unresolved_automatic_retry",
            lambda d: d["screen"]["held_unresolved"].update(automatic_retry="YES"),
        ),
        (
            "extra_unadjudicated_work_closure",
            lambda d: d["screen"].update(unaccounted_or_unadjudicated_work_blocks_closure=False),
        ),
        ("extra_bridge_evidence_clone", lambda d: d["bridge"].update(raw_evidence_cloned=True)),
        (
            "extra_bridge_closed_rejection_reopened",
            lambda d: d["bridge"]["groups"]["scientific_ineligible"]["cases"][0].update(
                treatment="RETRY"
            ),
        ),
        ("extra_pilot_swap", lambda d: d["run"]["pilot"].update(pilot_swap="ALLOWED")),
        ("extra_pilot_project_cap", lambda d: d["run"]["pilot"].update(pilot_project_cap=4)),
        (
            "extra_minimum_projects_changed",
            lambda d: d["protocol"]["allocation_invariants"].update(minimum_final_projects=5),
        ),
        (
            "extra_fourth_trial",
            lambda d: d["screen"]["screening"]["schedule"].append(
                {"variant": "FIXED", "repetition": 4}
            ),
        ),
        ("extra_missing_trial", lambda d: d["screen"]["screening"]["schedule"].pop()),
        (
            "extra_subcommands_as_repetitions",
            lambda d: d["screen"]["screening"]["composite_trial_semantics"].update(
                subcommands_count_as_extra_repetitions=True
            ),
        ),
        (
            "extra_scientific_rescue",
            lambda d: d["screen"]["screening"].update(scientific_rescue=True),
        ),
        (
            "extra_rank_lineage_changed",
            lambda d: d["pool"][0].update(predecessor_evidence_sha256="0" * 64),
        ),
        (
            "extra_remote_publication_universal",
            lambda d: d["run"]["unresolved_seven"].update(
                remote_published_required_for_integration=True
            ),
        ),
        (
            "extra_applicable_publication_gate_removed",
            lambda d: d["run"]["unresolved_seven"].update(
                applicable_execution_publication_gates="NONE"
            ),
        ),
        (
            "extra_actual_pilot_record_fabricated",
            lambda d: d["state"]["projection"]["allocation"]["pilot_case_ids"].append("fabricated"),
        ),
        (
            "extra_actual_final_record_fabricated",
            lambda d: d["state"]["projection"]["allocation"]["final_case_ids"].append("fabricated"),
        ),
    ]
    for name, mutate in mutations:
        changed(name, mutate)
    changed(
        "extra_competing_manifest_descriptor",
        lambda d: d["manifest"].update(current_descriptor_path="current.csv"),
    )
    # Explicitly reject drift in all 62 accepted semantic fields in the manifest.
    for decision, fields in data["manifest"]["accepted_D1_D8"].items():
        for field in fields:
            changed(
                "accepted_" + decision + "_" + field + "_null_drift",
                lambda d, decision=decision, field=field: d["manifest"]["accepted_D1_D8"][
                    decision
                ].update({field: None}),
            )
    fixture = event_fixture(data)
    event_mutations = [
        (
            "19_broken_event_chain_hash",
            lambda f: f[1][1]["previous_event_identity"].update(event_sha256="0" * 64),
        ),
        (
            "extra_wrong_previous_event_id",
            lambda f: f[1][1]["previous_event_identity"].update(event_id="wrong"),
        ),
        (
            "extra_wrong_previous_sequence",
            lambda f: f[1][1]["previous_event_identity"].update(sequence=3),
        ),
        (
            "extra_wrong_descriptor_predecessor",
            lambda f: f[1][0].update(previous_descriptor_sha256="0" * 64),
        ),
        ("extra_event_sequence_gap", lambda f: f[1][1].update(sequence=3)),
        (
            "extra_unaccepted_event_authority",
            lambda f: f[1][0]["authority_reference"].update(sha256="0" * 64),
        ),
        (
            "extra_event_unauthorized_gate",
            lambda f: f[1][0].update(gate="HUMAN_PI_AUTHORIZE_ORACLE"),
        ),
        ("extra_skip_lifecycle_gate", lambda f: f[1][0].update(to_state="CONTRACT_FROZEN")),
        (
            "extra_event_result_hash_wrong",
            lambda f: f[1][0].update(result_projection_sha256="0" * 64),
        ),
        (
            "extra_event_technical_work_fabricated",
            lambda f: f[1][0]["next_projection"]["case_states"][0].update(attempt_consumed=True),
        ),
        (
            "extra_event_grants_next_authority",
            lambda f: f[1][0]["next_projection"]["lifecycle"].update(ORACLE_AUTHORIZED="YES"),
        ),
        (
            "extra_runtime_event_in_candidate_auditor",
            lambda f: f[1][0].update(namespace="EFFECTIVE_V6"),
        ),
    ]
    for name, mutate in event_mutations:
        modified = copy.deepcopy(fixture)
        mutate(modified)
        rejection(name, lambda modified=modified: v.audit_event_chain(*modified))
    modified = copy.deepcopy(fixture)
    modified[1][1]["event_id"] = modified[1][0]["event_id"]
    rejection("extra_duplicate_event_identity", lambda: v.audit_event_chain(*modified))
    seven = seven_fixture(data)
    seven_mutations = [
        (
            "21_late_seven_outcome_actual_head_mismatch",
            lambda f: f[3][0].update(observed_head={"path": "late-head", "sha256": "4" * 64}),
        ),
        (
            "20_D6_fixed_head_refreshed",
            lambda f: f[1].update(
                fixed_seven_track_head={"path": "refreshed-head", "sha256": "4" * 64}
            ),
        ),
        (
            "extra_seven_late_identity",
            lambda f: f[3][0].update(identity={"path": "late-outcome", "sha256": "5" * 64}),
        ),
        ("extra_seven_duplicate_effective_outcome", lambda f: f[3].append(copy.deepcopy(f[3][0]))),
        (
            "extra_seven_infrastructure_slots_reused",
            lambda f: f[3][0].update(old_infrastructure_slots_reused=True),
        ),
        ("extra_seven_missing_supersession", lambda f: f[3][0].update(exact_supersession=False)),
        ("extra_seven_incomplete_3x3", lambda f: f[3][0].update(valid_slots=5)),
    ]
    for state in seven[0]["required_lifecycle"]:
        seven_mutations.append(
            (
                "extra_seven_missing_" + state,
                lambda f, state=state: f[3][0]["lifecycle"].update({state: "NO"}),
            )
        )
    for name, mutate in seven_mutations:
        modified = copy.deepcopy(seven)
        mutate(modified)
        rejection(name, lambda modified=modified: v.validate_seven_integration(*modified))
    rejection("extra_duplicate_JSON_key", lambda: v.loads('{"a":1,"a":2}'))
    rejection("extra_float_in_hash_payload", lambda: v.canonical({"a": 1.5}))
    return results


def test_candidate_bundle():
    v.validate_bundle(v.bundle())


def test_rejection_matrix():
    results = rejection_matrix()
    assert len(results) >= 28
    assert len({r["check"] for r in results}) == len(results)
    assert all(r["status"] == "PASS_REJECTED" for r in results)
    assert all(any(r["check"].startswith(f"{n:02d}_") for r in results) for n in range(1, 29))


def test_two_authorized_synthetic_events_derive_exact_projection():
    fixture = event_fixture(v.bundle())
    result, head = v.audit_event_chain(*fixture)
    assert result == fixture[1][-1]["next_projection"]
    assert head["event_sha256"] == v.digest(fixture[1][-1])
    assert result["lifecycle"]["CONTRACT_ACCEPTED"] == "YES"
    assert result["lifecycle"]["CONTRACT_FROZEN"] == "YES"
    assert result["lifecycle"]["V6_ACTIVATED"] == "NO"
    assert result["lifecycle"]["ORACLE_AUTHORIZED"] == "NO"
    assert all(value == "NO" for value in result["phase_authorizations"].values())


def test_empty_event_chain_retains_candidate():
    state = v.bundle()["state"]
    result, head = v.audit_event_chain(state["projection"], [], {}, [], state["contract"]["sha256"])
    assert result == state["projection"]
    assert head is None


def test_seven_four_state_integration_without_remote_publication():
    fixture = seven_fixture(v.bundle())
    v.validate_seven_integration(*fixture)
    assert fixture[3][0]["REMOTE_PUBLISHED"] == "NO"


def test_empty_seven_integration_is_valid():
    policy, cutoff, closure, _ = seven_fixture(v.bundle())
    v.validate_seven_integration(policy, cutoff, closure, [])


def terminal_facts():
    return {
        "closure_accepted": True,
        "preparation_accounted": 433,
        "preparation_adjudicated": 433,
        "all_ready_slots_accounted_adjudicated": True,
        "descriptor_event_agree": True,
        "eligible_count": 28,
        "rule_input_resolved": True,
        "prospective_final_feasible": True,
    }


@pytest.mark.parametrize(
    "updates,expected",
    [
        (
            {
                "closure_accepted": False,
                "eligible_count": 0,
                "rule_input_resolved": False,
                "prospective_final_feasible": False,
            },
            "V6_CENSUS_CLOSURE_BLOCKED",
        ),
        ({"preparation_accounted": 432}, "V6_CENSUS_CLOSURE_BLOCKED"),
        ({"preparation_adjudicated": 432}, "V6_CENSUS_CLOSURE_BLOCKED"),
        ({"all_ready_slots_accounted_adjudicated": False}, "V6_CENSUS_CLOSURE_BLOCKED"),
        ({"descriptor_event_agree": False}, "V6_CENSUS_CLOSURE_BLOCKED"),
        (
            {
                "eligible_count": 27,
                "rule_input_resolved": False,
                "prospective_final_feasible": False,
            },
            "V6_CENSUS_EXHAUSTED_INSUFFICIENT_ELIGIBLE_CAPACITY",
        ),
        (
            {"rule_input_resolved": False, "prospective_final_feasible": False},
            "V6_CENSUS_COMPLETE_ALLOCATION_RULE_UNRESOLVED",
        ),
        ({"prospective_final_feasible": False}, "V6_CENSUS_EXHAUSTED_PROJECT_DIVERSITY_INFEASIBLE"),
        ({"prospective_final_feasible": None}, "V6_CENSUS_CLOSURE_BLOCKED"),
        ({}, "V6_CENSUS_COMPLETE_ALLOCATION_AUTHORITY_REQUIRED"),
    ],
)
def test_D8_precedence_without_actual_allocation(updates, expected):
    facts = terminal_facts()
    facts.update(updates)
    assert v.terminal_status(facts) == expected


def test_current_state_schema_rejects_extra_field():
    state = v.bundle()["state"]
    state["csv_is_authority"] = True
    with pytest.raises(ValueError):
        v.validate_schema("V6_CAPACITY_CURRENT_STATE_V1", state)


def test_hash_encoding_is_order_independent_and_UTF8():
    assert v.canonical({"z": "é", "a": 1}) == b'{"a":1,"z":"\xc3\xa9"}'
    assert v.digest({"a": 1, "b": False}) == v.digest({"b": False, "a": 1})


def test_actual_descriptor_has_no_pilots_or_results():
    state = v.bundle()["state"]
    assert state["event_chain"] == []
    assert state["projection"]["allocation"] == {"pilot_case_ids": [], "final_case_ids": []}
    assert not any(c["attempt_consumed"] for c in state["projection"]["case_states"])
    assert not any(
        c["eligible"] or c["scientific_failure"] for c in state["projection"]["case_states"]
    )


def case_schema(case):
    schema = v.load(v.S / "V6_CAPACITY_STATE_EVENT_V1.schema.json")
    validator = v.Draft202012Validator(
        schema["properties"]["next_projection"]["properties"]["case_states"]["items"]
    )
    return list(validator.iter_errors(case))


def scientific_case_fixture():
    case = copy.deepcopy(v.bundle()["state"]["projection"]["case_states"][0])
    case.update(
        phase="ORACLE",
        adjudication_state="HUMAN_PI_ACCEPTED",
        evidence_validity="VALID",
        eligible=True,
        screening_classification="ELIGIBLE",
        authority_reference={"path": "synthetic-gate", "sha256": "a" * 64},
    )
    case["slot_accounting"] = [
        {
            "variant": variant,
            "repetition": repetition,
            "consumed": True,
            "validity": "VALID",
            "scientific_result": "FAIL" if variant == "BUGGY" else "PASS",
            "evidence": {"path": "synthetic-trial", "sha256": "b" * 64},
        }
        for variant in ["BUGGY", "FIXED"]
        for repetition in [1, 2, 3]
    ]
    return case


def test_D4_accepted_held_unresolved_schema_positive():
    case = copy.deepcopy(v.bundle()["state"]["projection"]["case_states"][0])
    case.update(
        phase="PREPARATION",
        technical_status="INTERRUPTED",
        adjudication_state="ACCEPTED_HELD_UNRESOLVED",
        evidence_validity="INCOMPLETE",
        authority_reference={"path": "synthetic-held-adjudication", "sha256": "a" * 64},
    )
    assert case_schema(case) == []
    for field in ["eligible", "scientific_failure", "automatic_retry"]:
        mutated = copy.deepcopy(case)
        mutated[field] = True
        assert case_schema(mutated)


def test_schema_exact_3x3_eligibility_and_nonconforming_science():
    case = scientific_case_fixture()
    assert case_schema(case) == []
    case["slot_accounting"][0]["scientific_result"] = "PASS"
    assert case_schema(case)
    case.update(
        eligible=False,
        scientific_failure=True,
        screening_classification="INELIGIBLE_REPRODUCIBILITY_OUTCOME",
        canonical_exclusion_reasons=["BUGGY_NOT_3_OF_3_FAIL"],
    )
    assert case_schema(case) == []
    case["slot_accounting"][0]["validity"] = "INVALID"
    assert case_schema(case)


def test_missing_slot_or_infrastructure_cannot_be_scientific():
    case = scientific_case_fixture()
    case["slot_accounting"].pop()
    assert case_schema(case)
    case = scientific_case_fixture()
    case["slot_accounting"][0]["scientific_result"] = None
    assert case_schema(case)


def test_runtime_descriptor_profile_requires_explicit_activation():
    state = copy.deepcopy(v.bundle()["state"])
    state.update(
        candidate_only=False,
        runtime_authority=True,
        authoritative_current_surfaces=[state["intended_effective_descriptor_path"]],
        effective_current_descriptor_identity={
            "descriptor_id": "synthetic-runtime-profile",
            "human_pi_transition": {"path": "synthetic-gate", "sha256": "a" * 64},
        },
    )
    with pytest.raises(ValueError):
        v.validate_schema("V6_CAPACITY_CURRENT_STATE_V1", state)

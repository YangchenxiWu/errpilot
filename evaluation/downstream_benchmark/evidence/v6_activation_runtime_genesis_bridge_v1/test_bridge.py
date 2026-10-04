"""Synthetic in-memory bridge probes. No event/post-state artifact is saved.

YES acceptance/installation values below are deliberately synthetic fixture
inputs, never authority. The only canonical projection transformed is abstract Q.
"""

import copy
import importlib.util
import json
from pathlib import Path

import pytest

_spec = importlib.util.spec_from_file_location(
    "genesis_bridge_validator", Path(__file__).with_name("validate_bridge.py")
)
v = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v)


def inputs():
    predecessor = (v.ROOT / v.CURRENT_PATH).read_bytes()
    bridge_bytes = (v.ROOT / v.BRIDGE_PATH).read_bytes()
    bridge = v.loads(bridge_bytes)
    baseline = {
        "baseline_commit": v.BASELINE,
        "published_baseline_commit": v.BASELINE,
        "artifacts": {
            k: (v.B / p).read_bytes()
            for k, (p, _) in v.IDENTITIES.items()
            if k != "predecessor_descriptor"
        },
        "next_sequence": 1,
        "prior_event_count": 0,
        "prior_event_head": None,
    }
    return predecessor, bridge, baseline, bridge_bytes


def synthetic_fixture(namespace="CANDIDATE_TEST_ONLY"):
    predecessor, bridge, baseline, bridge_bytes = inputs()
    old = v.loads(predecessor)
    qualified = v.qualify_runtime_genesis(predecessor, bridge, baseline)
    acceptance = {
        "reference": {"path": v.BRIDGE_PATH, "sha256": v.sha(bridge_bytes)},
        "bytes": bridge_bytes,
        "HUMAN_PI_ACCEPTED": "YES",
        "EFFECTIVE": "YES",
    }
    authority = {
        "path": "synthetic/activation-scope-authority.json",
        "namespace": namespace,
        "owner": "HUMAN_PI",
        "gate": "HUMAN_PI_ACTIVATE_V6_CENSUS_MEMBERSHIP",
        "contract_sha256": v.IDENTITIES["contract_manifest"][1],
        "prior_projection_sha256": v.digest(qualified),
        "previous_descriptor_sha256": v.sha(predecessor),
        "scope": "MEMBERSHIP_ACTIVATION_ONLY",
        "HUMAN_PI_ACCEPTED": "YES",
    }
    projection = copy.deepcopy(qualified)
    projection["state"] = "CENSUS_MEMBERSHIP_ACTIVATED"
    projection["lifecycle"].update(V6_ACTIVATED="YES", CENSUS_MEMBERSHIP_EFFECTIVE="YES")
    refs = [acceptance["reference"]] + [
        bridge["baseline"][k]
        for k in ("lifecycle_closure", "canonical_pool", "predecessor_evidence_bridge")
    ]
    refs.sort(key=lambda r: (r["path"].encode("utf-8"), r["sha256"]))
    core = {
        "schema": "V6_CAPACITY_STATE_EVENT_V1",
        "namespace": namespace,
        "sequence": 1,
        "kind": "STATE_TRANSITION",
        "previous_event_identity": None,
        "previous_descriptor_sha256": v.sha(predecessor),
        "contract_sha256": v.IDENTITIES["contract_manifest"][1],
        "authority_reference": {"path": authority["path"], "sha256": v.digest(authority)},
        "gate": authority["gate"],
        "from_state": qualified["state"],
        "to_state": projection["state"],
        "prior_projection_sha256": v.digest(qualified),
        "result_projection_sha256": v.digest(projection),
        "next_projection": projection,
        "evidence_references": refs,
        "supersession_reference": acceptance["reference"],
        "predecessor": old["predecessor"],
    }
    event = {**core, "event_id": v.derive_event_id(core)}
    event_bytes = (json.dumps(event, ensure_ascii=False, indent=2) + "\n").encode()
    ids = v.validate_event_identity(event, event_bytes)
    head = {"event_id": ids["event_id"], "sequence": 1, "event_sha256": ids["event_sha256"]}
    path = "synthetic/activation-event.json"
    preview = copy.deepcopy(old)
    preview.update(
        candidate_only=False,
        lifecycle_label=projection["state"],
        event_count=1,
        event_head=head,
        event_chain=[{**head, "path": path, "sha256": ids["file_sha256"]}],
        projection=projection,
        projection_sha256=v.digest(projection),
    )
    envelope = {
        **v.ASSERTIONS,
        "post_state_preview": preview,
        "event_preview": event,
        "event_bytes": event_bytes,
        "event_path": path,
    }
    installation_authority = {
        "path": "synthetic/installation-scope-authority.json",
        "owner": "HUMAN_PI",
        "operation": v.OPERATION,
        "canonical_path": v.CURRENT_PATH,
        "expected_predecessor_sha256": v.sha(predecessor),
        "scope": "EXACT_MEMBERSHIP_INSTALLATION_ONLY",
        "HUMAN_PI_ACCEPTED": "YES",
    }
    successor = copy.deepcopy(preview)
    successor.update(
        runtime_authority=True,
        authoritative_current_surfaces=[v.CURRENT_PATH],
        effective_current_descriptor_identity={
            "descriptor_id": "synthetic-installed-descriptor",
            "human_pi_transition": {
                "path": installation_authority["path"],
                "sha256": v.digest(installation_authority),
            },
        },
    )
    successor_bytes = (json.dumps(successor, indent=2, ensure_ascii=False) + "\n").encode()
    proof = {
        "operation": v.OPERATION,
        "path": v.CURRENT_PATH,
        "expected_predecessor_sha256": v.sha(predecessor),
        "observed_predecessor_sha256": v.sha(predecessor),
        "artifact_lifecycle": {k: "YES" for k in v.FOUR},
        "publication": copy.deepcopy(v.PUBLICATION),
        "automatic": False,
        "installation_authorized": True,
        "installed_verified": True,
        "committed_successor_bytes": successor_bytes,
        "observed_installed_bytes": successor_bytes,
        "acceptance_pin": {
            "path": v.CURRENT_PATH,
            "sha256": v.sha(successor_bytes),
            "HUMAN_PI_ACCEPTED": "YES",
        },
        "installation_authority": installation_authority,
        "competing_current_descriptors": [],
    }
    return {
        "predecessor": predecessor,
        "bridge": bridge,
        "baseline": baseline,
        "acceptance": acceptance,
        "authority": authority,
        "qualified": qualified,
        "core": core,
        "event": event,
        "event_bytes": event_bytes,
        "event_path": path,
        "envelope": envelope,
        "successor_bytes": successor_bytes,
        "proof": proof,
    }


def genesis(f):
    return v.validate_genesis_event(
        f["event"], f["predecessor"], f["bridge"], f["baseline"], f["acceptance"], f["authority"]
    )


def candidate(f, as_current=False):
    return v.validate_candidate_envelope(
        f["envelope"],
        f["predecessor"],
        f["bridge"],
        f["baseline"],
        f["acceptance"],
        f["authority"],
        as_current=as_current,
    )


def installation(f):
    return v.validate_installation_semantics(
        f["proof"],
        f["predecessor"],
        f["successor_bytes"],
        f["bridge"],
        f["baseline"],
        f["acceptance"],
        f["event"],
        f["event_bytes"],
        f["event_path"],
        f["authority"],
    )


def positives():
    f = synthetic_fixture()
    results = []

    def check(name, condition):
        assert condition, name
        results.append({"check": name, "status": "PASS"})

    v.validate_bridge(f["bridge"])
    check("exact_bridge_adopted_semantics_and_acyclic_graph", True)
    raw = v.loads(f["predecessor"])["projection"]
    check(
        "Q_deterministic_exact_predecessor",
        f["qualified"] == v.qualify_runtime_genesis(f["predecessor"], f["bridge"], f["baseline"]),
    )
    check(
        "Q_only_five_flags_plus_state",
        {k for k in raw["lifecycle"] if raw["lifecycle"][k] != f["qualified"]["lifecycle"][k]}
        == set(v.FLAGS)
        and all(f["qualified"][k] == raw[k] for k in raw if k not in ("state", "lifecycle")),
    )
    check(
        "Q_membership_and_execution_remain_NO",
        all(f["qualified"]["lifecycle"][k] == "NO" for k in raw["lifecycle"] if k not in v.FLAGS)
        and f["qualified"]["phase_authorizations"] == raw["phase_authorizations"],
    )
    check(
        "Q_does_not_mutate_input_or_create_event",
        v.sha(f["predecessor"]) == v.IDENTITIES["predecessor_descriptor"][1]
        and "event_count" not in f["qualified"]
        and "runtime_authority" not in f["qualified"],
    )
    check(
        "object_field_order_independent",
        v.derive_event_id(dict(reversed(list(f["core"].items())))) == f["event"]["event_id"],
    )
    check(
        "event_id_lowercase_64hex",
        len(f["event"]["event_id"]) == 64
        and all(c in "0123456789abcdef" for c in f["event"]["event_id"]),
    )
    for name, change in [
        ("array_order_sensitive", lambda c: c["next_projection"]["case_states"].reverse()),
        (
            "exact_string_whitespace_sensitive",
            lambda c: c["authority_reference"].update(path=c["authority_reference"]["path"] + " "),
        ),
        ("sequence_sensitive", lambda c: c.update(sequence=2)),
        (
            "evidence_digest_sensitive",
            lambda c: c["evidence_references"][0].update(sha256="a" * 64),
        ),
    ]:
        core = copy.deepcopy(f["core"])
        change(core)
        check(name, v.derive_event_id(core) != f["event"]["event_id"])
    core = copy.deepcopy(f["core"])
    core["authority_reference"]["path"] = "synthetic/é"
    normalized = copy.deepcopy(core)
    normalized["authority_reference"]["path"] = "synthetic/e\u0301"
    check("unicode_not_normalized", v.derive_event_id(core) != v.derive_event_id(normalized))
    identities = v.validate_event_identity(f["event"], f["event_bytes"])
    check("three_distinct_hash_identities", len(set(identities.values())) == 3)
    check(
        "canonical_complete_hash_file_format_independent",
        v.validate_event_identity(f["event"], v.canonical(f["event"]))["event_sha256"]
        == identities["event_sha256"]
        and v.sha(v.canonical(f["event"])) != identities["file_sha256"],
    )
    check("synthetic_genesis_exact_Q_binding", genesis(f) == f["event"]["next_projection"])
    check("synthetic_external_envelope_retains_V1_schemas", candidate(f))
    effective = synthetic_fixture("EFFECTIVE_V6")
    check("EFFECTIVE_namespace_candidate_still_powerless", candidate(effective))
    proof_result = installation(effective)
    check(
        "synthetic_explicit_installation_proof_no_operation",
        proof_result
        == {
            "semantic_proof_valid": True,
            "installation_performed": False,
            "runtime_authority_granted_by_validator": False,
        },
    )
    return results


def rejection_cases():
    cases = []

    def add(name, action):
        cases.append((name, action))

    def mutated_bridge(name, mutate):
        def action():
            bridge = copy.deepcopy(v.bridge_spec())
            mutate(bridge)
            v.validate_bridge(bridge)

        add(name, action)

    mutated_bridge("01_wrong_baseline_commit", lambda b: b.update(baseline_commit="0" * 40))
    for name, role in [
        ("02_wrong_closure_hash", "lifecycle_closure"),
        ("03_wrong_predecessor_descriptor_hash", "predecessor_descriptor"),
        ("05_wrong_contract_manifest", "contract_manifest"),
        ("06_wrong_pool_hash", "canonical_pool"),
        ("07_wrong_predecessor_bridge_hash", "predecessor_evidence_bridge"),
    ]:
        mutated_bridge(name, lambda b, role=role: b["baseline"][role].update(sha256="0" * 64))
    mutated_bridge(
        "04_wrong_raw_projection_hash",
        lambda b: b.update(raw_predecessor_projection_sha256="0" * 64),
    )

    def q_result(name, mutate):
        def action():
            f = synthetic_fixture()
            result = copy.deepcopy(f["qualified"])
            mutate(result)
            v.validate_qualification_result(v.loads(f["predecessor"])["projection"], result)

        add(name, action)

    q_result(
        "08_Q_mutates_membership",
        lambda p: p["lifecycle"].update(CENSUS_MEMBERSHIP_EFFECTIVE="YES"),
    )
    q_result(
        "09_Q_enables_preparation",
        lambda p: p["phase_authorizations"].update(PREPARATION_EXECUTION="YES"),
    )
    q_result("10_Q_enables_oracle", lambda p: p["lifecycle"].update(ORACLE_AUTHORIZED="YES"))
    q_result(
        "11_Q_enables_allocation",
        lambda p: p["allocation"]["pilot_case_ids"].append("synthetic-forbidden"),
    )
    q_result("12_Q_confers_runtime_authority", lambda p: p.update(runtime_authority=True))

    def event_case(name, mutate):
        def action():
            f = synthetic_fixture()
            mutate(f["event"])
            core = {k: x for k, x in f["event"].items() if k != "event_id"}
            f["event"]["event_id"] = v.derive_event_id(core)
            genesis(f)

        add(name, action)

    event_case(
        "13_synthetic_publication_backfill",
        lambda e: e.update(from_state="CONTRACT_CANDIDATE", to_state="HUMAN_PI_CONTRACT_ACCEPTED"),
    )
    event_case("13_synthetic_genesis_kind", lambda e: e.update(kind="GENESIS"))
    event_case("14_first_sequence_not_one", lambda e: e.update(sequence=2))
    event_case(
        "15_non_null_first_predecessor",
        lambda e: e.update(
            previous_event_identity={
                "event_id": "synthetic-prior",
                "sequence": 1,
                "event_sha256": "0" * 64,
            }
        ),
    )

    def core_case(name, mutate):
        def action():
            core = copy.deepcopy(synthetic_fixture()["core"])
            mutate(core)
            v.derive_event_id(core)

        add(name, action)

    def arbitrary():
        f = synthetic_fixture()
        f["event"]["event_id"] = "0" * 64
        v.validate_event_identity(f["event"], v.canonical(f["event"]))

    add("16_arbitrary_event_id", arbitrary)
    core_case("17_event_id_in_core", lambda c: c.update(event_id="0" * 64))
    core_case("18_event_artifact_hash_dependency", lambda c: c.update(event_sha256="0" * 64))
    core_case("18_file_hash_dependency", lambda c: c.update(file_sha256="0" * 64))
    core_case("19_timestamp_introduced", lambda c: c.update(timestamp="synthetic-only"))
    for label, number in [("float", 1.0), ("NaN", float("nan")), ("Infinity", float("inf"))]:
        core_case("20_" + label, lambda c, n=number: c.update(sequence=n))

    def candidate_case(name, mutate=None, as_current=False):
        def action():
            f = synthetic_fixture()
            if mutate:
                mutate(f["envelope"])
            candidate(f, as_current)

        add(name, action)

    candidate_case("21_candidate_as_current", as_current=True)
    candidate_case("22_candidate_auto_promotion", lambda e: e.update(AUTO_PROMOTION="YES"))
    candidate_case(
        "23_current_registration_enabled", lambda e: e.update(CURRENT_REGISTRATION="ALLOWED")
    )

    def install_case(name, mutate):
        def action():
            f = synthetic_fixture("EFFECTIVE_V6")
            mutate(f)
            installation(f)

        add(name, action)

    for flag in v.FOUR:
        install_case(
            "24_missing_" + flag,
            lambda f, k=flag: f["proof"]["artifact_lifecycle"].update({k: "NO"}),
        )
    install_case(
        "25_wrong_effectivity_operation", lambda f: f["proof"].update(operation="SAVE_COPY")
    )
    install_case(
        "26_remote_publication_universal",
        lambda f: f["proof"]["publication"].update(
            MEMBERSHIP_ACTIVATION_ARTIFACT_REMOTE_PUBLICATION="REQUIRED"
        ),
    )
    install_case(
        "27_execution_publication_gates_removed",
        lambda f: f["proof"]["publication"].update(
            REAL_DOWNSTREAM_EXECUTION_PUBLICATION_GATES="NONE"
        ),
    )
    mutated_bridge(
        "28_bridge_future_activation_event", lambda b: b.update(future_event_id="0" * 64)
    )
    mutated_bridge(
        "29_bridge_future_poststate_hash", lambda b: b.update(future_poststate_sha256="0" * 64)
    )
    mutated_bridge(
        "30_hash_dependency_cycle",
        lambda b: b["hash_model"]["edges"].append(["event_sha", "event_core"]),
    )
    mutated_bridge("bridge_self_hash", lambda b: b.update(bridge_sha256="0" * 64))
    mutated_bridge("future_enclosing_commit", lambda b: b.update(enclosing_commit="0" * 40))
    mutated_bridge(
        "boolean_instead_of_integer_genesis_sequence", lambda b: b["genesis"].update(sequence=True)
    )

    def baseline_case(name, mutate):
        def action():
            predecessor, bridge, baseline, _ = inputs()
            mutate(baseline)
            v.qualify_runtime_genesis(predecessor, bridge, baseline)

        add(name, action)

    baseline_case("Q_wrong_external_commit", lambda e: e.update(published_baseline_commit="0" * 40))
    for role in (
        "lifecycle_closure",
        "contract_manifest",
        "canonical_pool",
        "predecessor_evidence_bridge",
    ):
        baseline_case(
            "Q_wrong_" + role + "_bytes",
            lambda e, k=role: e["artifacts"].update({k: e["artifacts"][k] + b" "}),
        )

    def wrong_predecessor():
        predecessor, bridge, baseline, _ = inputs()
        v.qualify_runtime_genesis(predecessor + b" ", bridge, baseline)

    add("Q_wrong_predecessor_bytes", wrong_predecessor)
    baseline_case("Q_sequence_two_forbidden", lambda e: e.update(next_sequence=2))
    baseline_case("Q_reset_after_existing_event_forbidden", lambda e: e.update(prior_event_count=1))
    q_result("Q_changes_consumed_work", lambda p: p["case_states"][0].update(attempt_consumed=True))
    q_result(
        "Q_changes_closure_scientific_outcome",
        lambda p: p.update(terminal_assessment={"primary_status": "synthetic-forbidden"}),
    )
    event_case(
        "raw_projection_used_instead_of_Q", lambda e: e.update(prior_projection_sha256=v.RAW_SHA)
    )
    event_case("wrong_previous_descriptor", lambda e: e.update(previous_descriptor_sha256="0" * 64))
    event_case("missing_genesis_reference", lambda e: e["evidence_references"].pop())
    event_case("wrong_supersession_reference", lambda e: e.update(supersession_reference=None))
    core_case(
        "duplicate_evidence_reference",
        lambda c: c["evidence_references"].append(copy.deepcopy(c["evidence_references"][0])),
    )

    def conflict(c):
        ref = copy.deepcopy(c["evidence_references"][0])
        ref["sha256"] = "0" * 64
        c["evidence_references"].append(ref)

    core_case("conflicting_evidence_reference", conflict)
    core_case("unsorted_evidence_reference", lambda c: c["evidence_references"].reverse())
    core_case("undeclared_previous_event_id", lambda c: c.update(previous_event_id=None))
    core_case("undeclared_previous_event_hash", lambda c: c.update(previous_event_hash=None))
    core_case(
        "invalid_unicode_scalar_value",
        lambda c: c["authority_reference"].update(path="synthetic/\ud800"),
    )
    core_case("invalid_unicode_scalar_key", lambda c: c.update({"\udfff": None}))
    core_case("non_JSON_tuple", lambda c: c.update(evidence_references=()))
    core_case("non_string_key", lambda c: c.update({1: None}))
    add("duplicate_JSON_keys", lambda: v.loads('{"a":1,"a":2}'))
    add("BOM_JSON_rejected", lambda: v.loads(b"\xef\xbb\xbf{}"))
    candidate_case(
        "nested_runtime_authority", lambda e: e["post_state_preview"].update(runtime_authority=True)
    )
    candidate_case(
        "nested_profile_field",
        lambda e: e["post_state_preview"].update(profile="NON_EFFECTIVE_TRANSITION_CANDIDATE"),
    )
    candidate_case(
        "nested_chain_mismatch",
        lambda e: e["post_state_preview"]["event_head"].update(event_sha256="0" * 64),
    )
    candidate_case("namespace_label_promotes_current", lambda e: e.update(RUNTIME_EFFECTIVE="YES"))
    install_case(
        "wrong_compare_predecessor",
        lambda f: f["proof"].update(observed_predecessor_sha256="0" * 64),
    )
    install_case(
        "unaccepted_successor",
        lambda f: f["proof"]["acceptance_pin"].update(HUMAN_PI_ACCEPTED="NO"),
    )
    install_case(
        "wrong_independent_successor_pin",
        lambda f: f["proof"]["acceptance_pin"].update(sha256="0" * 64),
    )
    install_case(
        "missing_accepted_bridge", lambda f: f["acceptance"].update(HUMAN_PI_ACCEPTED="NO")
    )
    install_case("bridge_not_effective", lambda f: f["acceptance"].update(EFFECTIVE="NO"))
    install_case(
        "competing_current_descriptor",
        lambda f: f["proof"]["competing_current_descriptors"].append("synthetic/other.json"),
    )
    install_case("automatic_installation", lambda f: f["proof"].update(automatic=True))
    install_case(
        "installation_not_authorized", lambda f: f["proof"].update(installation_authorized=False)
    )
    install_case("installation_not_verified", lambda f: f["proof"].update(installed_verified=False))
    install_case(
        "committed_bytes_mismatch",
        lambda f: f["proof"].update(committed_successor_bytes=f["successor_bytes"] + b" "),
    )

    def candidate_install(f):
        f["successor_bytes"] = v.canonical(f["envelope"]["post_state_preview"])
        f["proof"].update(
            committed_successor_bytes=f["successor_bytes"],
            observed_installed_bytes=f["successor_bytes"],
        )
        f["proof"]["acceptance_pin"]["sha256"] = v.sha(f["successor_bytes"])

    install_case("candidate_only_installation", candidate_install)

    def bad_successor(f, key, value):
        s = v.loads(f["successor_bytes"])
        s[key] = value
        f["successor_bytes"] = v.canonical(s)
        f["proof"].update(
            committed_successor_bytes=f["successor_bytes"],
            observed_installed_bytes=f["successor_bytes"],
        )
        f["proof"]["acceptance_pin"]["sha256"] = v.sha(f["successor_bytes"])

    install_case(
        "successor_backward_acceptance_pin",
        lambda f: bad_successor(f, "acceptance_pin_reference", f["proof"]["acceptance_pin"]),
    )
    install_case("successor_self_hash", lambda f: bad_successor(f, "file_sha256", "0" * 64))
    install_case(
        "successor_historical_predecessor_repurposed",
        lambda f: bad_successor(f, "predecessor", {"descriptor_sha256": v.sha(f["predecessor"])}),
    )

    def authority_future():
        f = synthetic_fixture()
        f["authority"]["event_id"] = f["event"]["event_id"]
        genesis(f)

    add("event_authority_contains_future_event_id", authority_future)
    install_case(
        "install_authority_contains_future_successor_hash",
        lambda f: f["proof"]["installation_authority"].update(
            successor_sha256=v.sha(f["successor_bytes"])
        ),
    )
    return cases


def rejection_matrix():
    results = []
    for name, action in rejection_cases():
        try:
            action()
        except ValueError as error:
            results.append({"check": name, "status": "PASS_REJECTED", "reason": str(error)})
        else:
            raise AssertionError("incorrectly accepted: " + name)
    return results


def test_positive_suite():
    assert len(positives()) >= 18


@pytest.mark.parametrize("name,action", rejection_cases(), ids=[n for n, _ in rejection_cases()])
def test_rejection(name, action):
    with pytest.raises(ValueError):
        action()

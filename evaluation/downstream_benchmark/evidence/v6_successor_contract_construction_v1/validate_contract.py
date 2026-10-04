"""Read-only V6 contract audit. No production writer, subject or oracle dispatch.

Run with the existing repository .venv Python (jsonschema is already installed).
Mutation probes and event/integration fixtures are in-memory CANDIDATE_TEST_ONLY.
No pilot hashing or selection algorithm is executed by this module.
"""

import contextlib
import copy
import csv
import hashlib
import importlib.util
import io
import json
import os
import re
import subprocess
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator

E = Path(__file__).resolve().parent
B = E.parents[1]
ROOT = B.parents[1]
S = B / "v6_contract_schemas"
HEAD = "26a9264105f303dc0101f74c9315c41ab1c9e265"
DECISION_HASH = "2d30ba01c22a6531ab1480140dbef20d2878ba94c8ac2d7d7aa01cc85514e6f2"
DESIGN_HASH = "f2e17649236d28d1712192146039370a6e0542084a82685d03f2d4d227064163"
POOL_HASH = "cad0889e1a527165fc04663c4bde0b22a8af25cdc07bc8c6426348e5ad1c2669"
DOCS = {
    "protocol": "V6_CAPACITY_SUCCESSOR_PROTOCOL.md",
    "run": "V6_CAPACITY_SUCCESSOR_RUN_SPEC.md",
    "screen": "V6_CENSUS_SCREENING_SPEC.md",
}
NEW_NAMES = list(DOCS.values()) + [
    "v6_reconsideration_pool.csv",
    "v6_predecessor_evidence_bridge.json",
    "v6_current_state.json",
    "v6_capacity_successor_contract.json",
    "v6_census_lifecycle.json",
]
SCHEMA_NAMES = [
    "EP-DBP-6-CAPACITY",
    "EP-DBRS-6-CAPACITY",
    "EP-BIPS-6-CENSUS",
    "V6_RECONSIDERATION_POOL_V1",
    "V6_PREDECESSOR_EVIDENCE_BRIDGE_V1",
    "V6_CAPACITY_CURRENT_STATE_V1",
    "V6_CENSUS_LIFECYCLE_V1",
    "V6_CAPACITY_STATE_EVENT_V1",
]
EVIDENCE_NAMES = [
    "entry_verification.json",
    "validate_contract.py",
    "test_contract.py",
    "validation_results.json",
    "RUN_REPORT.md",
    "artifact_sha256.json",
]
NEW_PATHS = {str((B / n).relative_to(ROOT)) for n in NEW_NAMES}
NEW_PATHS |= {str((S / (n + ".schema.json")).relative_to(ROOT)) for n in SCHEMA_NAMES}
NEW_PATHS |= {str((E / n).relative_to(ROOT)) for n in EVIDENCE_NAMES}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    path = Path(path)
    data = os.readlink(path).encode() if path.is_symlink() else path.read_bytes()
    return hashlib.sha256(data).hexdigest()


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def loads(text):
    return json.loads(text, object_pairs_hook=reject_duplicate_keys)


def load(path):
    return loads(Path(path).read_text(encoding="utf-8"))


def csv_rows(path):
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def canonical(value):
    def inspect(item):
        require(not isinstance(item, float), "floating-point JSON forbidden")
        if isinstance(item, dict):
            require(all(isinstance(k, str) for k in item), "non-string JSON key")
            for v in item.values():
                inspect(v)
        elif isinstance(item, list):
            for v in item:
                inspect(v)
        else:
            require(item is None or isinstance(item, (str, int, bool)), "non-JSON value")

    inspect(value)
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def reference(path):
    path = Path(path)
    return {
        "path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "sha256": sha(path),
    }


def check_ref(ref):
    path = Path(ref["path"])
    require(
        sha(path if path.is_absolute() else ROOT / path) == ref["sha256"],
        "reference digest drift: " + ref["path"],
    )


def embedded(path, label):
    pattern = r"<!-- BEGIN " + label + r" -->\n```json\n(.*?)\n```\n<!-- END " + label + " -->"
    matches = re.findall(pattern, Path(path).read_text(), re.S)
    require(len(matches) == 1, "missing/competing embedded contracts")
    return loads(matches[0])


def module_at(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sources():
    require(
        sha(B / "V6_PROTOCOL_DESIGN_D1_D8_HUMAN_PI_DECISION.md") == DECISION_HASH,
        "wrong accepted decision bytes",
    )
    require(
        sha(B / "V6_FINITE_SAME_UNIVERSE_CENSUS_PROTOCOL_DESIGN_FINALIZED_CANDIDATE.md")
        == DESIGN_HASH,
        "wrong accepted finalized design bytes",
    )
    require(
        sha(B / "v6_reconsideration_pool_proposal.csv") == POOL_HASH,
        "wrong accepted proposal pool bytes",
    )
    design = embedded(
        B / "V6_FINITE_SAME_UNIVERSE_CENSUS_PROTOCOL_DESIGN_FINALIZED_CANDIDATE.md",
        "FINALIZED_DESIGN_JSON",
    )
    proposal = load(B / "v6_capacity_successor_contract_proposal.json")
    predecessor = copy.deepcopy(proposal["predecessor"])
    predecessor.pop("bridge")
    return design, proposal, predecessor


def bundle():
    result = {key: embedded(B / name, "CONTRACT_JSON") for key, name in DOCS.items()}
    result.update(
        pool=csv_rows(B / "v6_reconsideration_pool.csv"),
        bridge=load(B / "v6_predecessor_evidence_bridge.json"),
        state=load(B / "v6_current_state.json"),
        lifecycle=load(B / "v6_census_lifecycle.json"),
        manifest=load(B / "v6_capacity_successor_contract.json"),
    )
    return result


def validate_schema(name, instance):
    schema = load(S / (name + ".schema.json"))
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(instance), key=lambda e: str(e.path))
    require(
        not errors, name + " schema rejection at " + (str(errors[0].json_path) if errors else "")
    )


def expected_pool():
    _, _, pred = sources()
    expected = []
    renames = {
        "proposal_order": "census_order",
        "project": "source_project",
        "design_state": "candidate_state",
    }
    for row in csv_rows(B / "v6_reconsideration_pool_proposal.csv"):
        item = {renames.get(k, k): v for k, v in row.items()}
        item.update(
            candidate_state="CONTRACT_CANDIDATE_ONLY",
            schema_id="V6_RECONSIDERATION_POOL_V1",
            proposal_pool_sha256=POOL_HASH,
            predecessor_head=HEAD,
            predecessor_artifact_inventory_sha256=pred["hash_inventory"]["sha256"],
        )
        expected.append(item)
    return expected


def validate_pool(pool):
    require(len(pool) == 433, "pool count != 433")
    require(len({r["case_id"] for r in pool}) == 433, "duplicate census case")
    old = module_at(
        "historical_pool_replay", B / "evidence/v6_protocol_design_v1/validate_proposal.py"
    )
    _, _, admissions, replay = old.reconstruct()
    exclusions = {r["case_id"] for r in csv_rows(B / "exclusions_v5.csv")}
    prior = load(B / "v6_predecessor_evidence_bridge_proposal.json")
    screened = {
        r["case_id"]
        for g in ["grandfathered_eligible", "scientific_ineligible", "infrastructure_unresolved"]
        for r in prior["groups"][g]["cases"]
    }
    ids = {r["case_id"] for r in pool}
    require(not ids.intersection(admissions), "historical admission overlap")
    require(not ids.intersection(exclusions), "accepted exclusion overlap")
    require(not ids.intersection(screened), "screened-case overlap")
    require(
        [r["case_id"] for r in pool] == [r["canonical_case_id"] for r, _ in replay],
        "pool membership/order drift from mechanical predecessor replay",
    )
    require(pool == expected_pool(), "pool row/lineage/disposition/rank drift")
    validate_schema("V6_RECONSIDERATION_POOL_V1", pool)


def validate_bridge(bridge):
    _, _, pred = sources()
    expected = load(B / "v6_predecessor_evidence_bridge_proposal.json")
    expected["schema"] = "V6_PREDECESSOR_EVIDENCE_BRIDGE_V1"
    expected.pop("design_only")
    expected.update(
        candidate_only=True,
        runtime_authority=False,
        predecessor=pred,
        construction_authority=reference(E / "entry_verification.json"),
        proposal_bridge=reference(B / "v6_predecessor_evidence_bridge_proposal.json"),
    )
    categories = {
        "grandfathered_eligible": "GRANDFATHERED_EVIDENCE",
        "scientific_ineligible": "CLOSED_SCIENTIFIC_REJECTION",
        "infrastructure_unresolved": "INFRASTRUCTURE_UNRESOLVED",
        "accepted_pre_eligibility_exclusions": "CLOSED_PRE_ELIGIBILITY_EXCLUSION",
        "never_admitted_cap_skips": "NEWLY_RECONSIDERABLE_HISTORICAL_CAP_SKIP",
    }
    for key, group in expected["groups"].items():
        group["evidence_category"] = categories[key]
    skips = expected["groups"]["never_admitted_cap_skips"]
    skips.update(
        inventory=reference(B / "v6_reconsideration_pool.csv"),
        proposal_inventory=reference(B / "v6_reconsideration_pool_proposal.csv"),
        treatment="CANDIDATE_ONLY_PROSPECTIVE_RECONSIDERATION",
    )
    require(bridge == expected, "predecessor bridge rewrite, clone or classification drift")
    validate_schema("V6_PREDECESSOR_EVIDENCE_BRIDGE_V1", bridge)


def validate_candidate_state(state, manifest, pool):
    validate_schema("V6_CAPACITY_CURRENT_STATE_V1", state)
    require(
        state["candidate_only"] is True and state["runtime_authority"] is False,
        "candidate gained runtime authority",
    )
    require(
        state["lifecycle_label"] == "CONTRACT_CANDIDATE_ONLY"
        and state["projection"]["state"] == "CONTRACT_CANDIDATE",
        "candidate lifecycle drift",
    )
    require(
        state["effective_current_descriptor_identity"] is None
        and state["authoritative_current_surfaces"] == [],
        "competing/effective candidate authority",
    )
    require(
        state["event_count"] == 0 and state["event_chain"] == [] and state["event_head"] is None,
        "candidate event chain must be empty",
    )
    require(
        state["contract"] == reference(B / "v6_capacity_successor_contract.json"),
        "unbound candidate descriptor",
    )
    require(state["predecessor"] == manifest["predecessor"], "descriptor predecessor drift")
    projection = state["projection"]
    require(
        all(v == "NO" for v in projection["lifecycle"].values())
        and all(v == "NO" for v in projection["phase_authorizations"].values()),
        "implicit downstream authority",
    )
    require(
        projection["combined_pool_input_freeze"] is None
        and projection["allocation"] == {"pilot_case_ids": [], "final_case_ids": []}
        and projection["terminal_assessment"] is None,
        "fabricated freeze/allocation/terminal result",
    )
    require(state["projection_sha256"] == digest(projection), "descriptor projection disagreement")
    require(
        [c["case_id"] for c in projection["case_states"]] == [r["case_id"] for r in pool],
        "descriptor census drift",
    )
    for c, r in zip(projection["case_states"], pool):
        require(
            c["source_project"] == r["source_project"]
            and c["bugsinpy_bug_id"] == r["bugsinpy_bug_id"]
            and c["frozen_rank"] == int(r["frozen_rank"])
            and c["predecessor_evidence"]
            == {"path": r["predecessor_evidence_path"], "sha256": r["predecessor_evidence_sha256"]},
            "descriptor case identity drift",
        )
        expected = dict(
            c,
            phase="NOT_STARTED",
            technical_status=None,
            canonical_exclusion_reasons=[],
            subreasons=[],
            adjudication_state="NOT_ADJUDICATED",
            evidence_validity="NOT_EVALUATED",
            attempt_consumed=False,
            slot_accounting=[],
            eligible=False,
            scientific_failure=False,
            automatic_retry=False,
            supersession_reference=None,
            screening_classification=None,
            authority_reference=None,
            attempt_id=None,
            environment_identity=None,
            oracle_plan_reference=None,
        )
        require(c == expected, "candidate fabricated work/evidence/adjudication")


def validate_bundle(data):
    design, proposal, pred = sources()
    for key in ["protocol", "run", "screen", "lifecycle", "manifest"]:
        c = data[key]
        require(c["predecessor"] == pred, "wrong exact predecessor binding: " + key)
        require(c["accepted_D1_D8"] == design["accepted_D1_D8"], "D1-D8 drift: " + key)
        require(
            c["candidate_only"] is True and c["runtime_authority"] is False,
            "implicit contract authority: " + key,
        )
        require(
            c["construction_authority"] == reference(E / "entry_verification.json"),
            "wrong latest construction authority",
        )
    require(data["protocol"]["architecture"] == design["architecture"], "wrong architecture")
    require(
        data["protocol"]["allocation_invariants"] == design["allocation_invariants"]
        and data["run"]["allocation_invariants"] == design["allocation_invariants"],
        "changed final allocation algorithm/24+4/cap/diversity",
    )
    require(data["screen"]["census"] == design["pool"], "census stopping/batch/membership drift")
    require(data["screen"]["screening"] == design["screening_invariants"], "altered 3x3 rule")
    require(data["screen"]["preparation"] == proposal["preparation"], "preparation/runtime rescue")
    require(
        data["screen"]["canonical_failure_reasons"]
        == design["inherited_canonical_failure_reasons"],
        "new scientific failure reason",
    )
    require(
        data["run"]["pilot"] == design["accepted_D1_D8"]["D7"]
        and data["run"]["pilot_reselection"] == "PROHIBITED"
        and data["run"]["minimum_eligible_before_pilot"] == 28
        and data["run"]["selection_authorized"] is False,
        "pilot algorithm/authority drift",
    )
    for key in ["run", "protocol"]:
        require(
            data[key]["unresolved_seven"] == design["unresolved_seven"],
            "D6 cutoff/integration drift",
        )
        require(data[key]["downstream_authority"] == "NONE", "implicit downstream authority")
    require(
        data["protocol"]["closure"] == design["closure"]
        and data["protocol"]["automatic_successor_on_exhaustion"] is False,
        "terminal precedence/automatic successor drift",
    )
    require(
        data["lifecycle"]["current_state"] == "CONTRACT_CANDIDATE"
        and data["lifecycle"]["completion_grants_next_authority"] is False,
        "state completion granted next authority",
    )
    require(
        len(data["lifecycle"]["states"]) == 16 and len(data["lifecycle"]["transitions"]) == 15,
        "missing lifecycle gate",
    )
    for i, t in enumerate(data["lifecycle"]["transitions"]):
        require(
            t["from"] == data["lifecycle"]["states"][i]
            and t["to"] == data["lifecycle"]["states"][i + 1]
            and t["owner"] == "HUMAN_PI"
            and t["automatic_next_authority"] is False,
            "authority graph drift",
        )
    for key in ["protocol", "run", "screen", "lifecycle"]:
        validate_schema(data[key]["schema"], data[key])
    validate_pool(data["pool"])
    validate_bridge(data["bridge"])
    validate_candidate_state(data["state"], data["manifest"], data["pool"])
    m = data["manifest"]
    require(
        m["lifecycle"] == "CONTRACT_CANDIDATE_ONLY"
        and m["current_descriptor_runtime_authority"] is False
        and m["downstream_authority"] == "NONE",
        "manifest gained state authority",
    )
    require(set(m["schemas"]) == set(SCHEMA_NAMES), "schema identity drift")
    require(
        m["current_descriptor_path"] == "evaluation/downstream_benchmark/v6_current_state.json"
        and m["historical_inputs_sha256"]
        == load(E / "entry_verification.json")["historical_inputs_sha256"]
        and m["accepted_design"]
        == reference(B / "V6_FINITE_SAME_UNIVERSE_CENSUS_PROTOCOL_DESIGN_FINALIZED_CANDIDATE.md")
        and m["decision"] == reference(B / "V6_PROTOCOL_DESIGN_D1_D8_HUMAN_PI_DECISION.md"),
        "competing current descriptor or historical authority identity drift",
    )
    for ref in (
        list(m["schemas"].values())
        + list(m["artifacts"].values())
        + [m["accepted_design"], m["decision"]]
    ):
        check_ref(ref)


def phase_flags_for_edge(projection, target):
    """Pure contract fixture derivation; never writes a current descriptor."""
    result = copy.deepcopy(projection)
    result["state"] = target
    changes = {
        "HUMAN_PI_CONTRACT_ACCEPTED": ["CONTRACT_ACCEPTED"],
        "CONTRACT_FROZEN": ["CONTRACT_FROZEN"],
        "CONTRACT_PERSISTED": ["CONTRACT_PERSISTED"],
        "CONTRACT_COMMITTED": ["CONTRACT_COMMITTED"],
        "CONTRACT_PUBLISHED_WHERE_REQUIRED": ["CONTRACT_PUBLISHED_WHERE_REQUIRED"],
        "CENSUS_MEMBERSHIP_ACTIVATED": ["V6_ACTIVATED", "CENSUS_MEMBERSHIP_EFFECTIVE"],
        "PREPARATION_EXECUTION_AUTHORIZED": ["PREPARATION_AUTHORIZED"],
        "ORACLE_EXECUTION_AUTHORIZED": ["ORACLE_AUTHORIZED"],
        "PILOT_FINAL_ALLOCATION_AUTHORIZED": ["ALLOCATION_AUTHORIZED"],
    }
    for flag in changes.get(target, []):
        result["lifecycle"][flag] = "YES"
    phase = {
        "PREPARATION_PLANNING_AUTHORIZED": "PREPARATION_PLANNING",
        "PREPARATION_EXECUTION_AUTHORIZED": "PREPARATION_EXECUTION",
        "ORACLE_EXECUTION_AUTHORIZED": "ORACLE_EXECUTION",
        "PILOT_FINAL_ALLOCATION_AUTHORIZED": "PILOT_FINAL_ALLOCATION",
    }.get(target)
    if phase:
        result["phase_authorizations"][phase] = "YES"
    return result


def audit_event_chain(initial, events, authorities, descriptor_identities, contract_sha):
    """Audit synthetic lifecycle edges only; production event consumption is not implemented.

    CASE_DISPOSITION and COMBINED_INPUT_FREEZE schemas are checked separately; their
    real evidence/gate enforcement requires a later authorized implementation.
    """
    current = copy.deepcopy(initial)
    prior = None
    event_ids = set()
    lifecycle = load(B / "v6_census_lifecycle.json")
    pred = sources()[2]
    for index, event in enumerate(events, 1):
        validate_schema("V6_CAPACITY_STATE_EVENT_V1", event)
        require(
            event["namespace"] == "CANDIDATE_TEST_ONLY",
            "runtime event use forbidden in contract auditor",
        )
        require(
            event["kind"] == "STATE_TRANSITION",
            "non-fixture event needs later runtime implementation",
        )
        require(
            event["predecessor"] == pred and event["contract_sha256"] == contract_sha,
            "event contract/predecessor identity drift",
        )
        require(
            event["sequence"] == index and event["previous_event_identity"] == prior,
            "broken event-chain identity",
        )
        require(event["event_id"] not in event_ids, "duplicate immutable event identity")
        event_ids.add(event["event_id"])
        require(
            event["previous_descriptor_sha256"] == descriptor_identities[index - 1],
            "wrong exact predecessor descriptor",
        )
        require(
            event["prior_projection_sha256"] == digest(current)
            and event["from_state"] == current["state"],
            "event predecessor projection disagreement",
        )
        auth = authorities.get(event["authority_reference"]["sha256"])
        require(
            auth is not None and digest(auth) == event["authority_reference"]["sha256"],
            "missing exact independent Human-PI authority",
        )
        require(
            event["authority_reference"]["path"] == auth["path"]
            and auth["namespace"] == "CANDIDATE_TEST_ONLY",
            "authority identity/namespace drift",
        )
        edge = next((e for e in lifecycle["transitions"] if e["from"] == current["state"]), None)
        require(
            edge is not None
            and event["to_state"] == edge["to"]
            and event["gate"] == edge["gate"] == auth["gate"]
            and auth["owner"] == "HUMAN_PI"
            and auth["contract_sha256"] == contract_sha
            and auth["prior_projection_sha256"] == digest(current),
            "unauthorized/nonadjacent lifecycle transition",
        )
        require(
            event["next_projection"] == phase_flags_for_edge(current, event["to_state"]),
            "lifecycle event changed technical/scientific work or granted another authority",
        )
        current = copy.deepcopy(event["next_projection"])
        require(
            event["result_projection_sha256"] == digest(current), "event result projection mismatch"
        )
        prior = {"event_id": event["event_id"], "sequence": index, "event_sha256": digest(event)}
    return current, prior


def validate_seven_integration(policy, cutoff, closure, outcomes):
    """Pure synthetic cutoff audit. Never reads, repairs or runs a seven-track subject."""
    expected = sources()[0]["unresolved_seven"]
    require(policy == expected, "D6 policy drift")
    require(
        cutoff["cutoff"] == "FIRST_COMBINED_POOL_INPUT_FREEZE"
        and cutoff["fixed_seven_track_head"] == closure["fixed_seven_track_head"]
        and cutoff["accepted_census_closure"] == closure["identity"]
        and cutoff["late_inclusion"] is False
        and cutoff["cutoff_refresh"] is False,
        "D6 cutoff refresh or late head substitution",
    )
    require(
        len({o["case_id"] for o in outcomes}) == len(outcomes),
        "competing seven-track effective outcomes",
    )
    for outcome in outcomes:
        require(
            outcome["case_id"] in expected["case_ids"]
            and outcome["identity"] in closure["effective_outcomes_at_fixed_head"]
            and outcome["observed_head"] == closure["fixed_seven_track_head"],
            "late seven-track inclusion",
        )
        require(
            all(outcome["lifecycle"].get(k) == "YES" for k in expected["required_lifecycle"]),
            "seven-track missing one of four required lifecycle states",
        )
        require(
            outcome["classification"] == "ELIGIBLE"
            and outcome["valid_slots"] == 6
            and outcome["buggy"] == ["FAIL"] * 3
            and outcome["fixed"] == ["PASS"] * 3
            and outcome["new_attempt_id"] != outcome["old_attempt_id"]
            and outcome["exact_supersession"] is True
            and outcome["old_infrastructure_slots_reused"] is False,
            "seven-track invalid criterion/attempt/supersession",
        )


def terminal_status(facts):
    """Synthetic precedence evaluation, with no allocation or actual pilot computation."""
    if (
        not facts["closure_accepted"]
        or facts["preparation_accounted"] != 433
        or facts["preparation_adjudicated"] != 433
        or not facts["all_ready_slots_accounted_adjudicated"]
        or not facts["descriptor_event_agree"]
    ):
        suffix = "CLOSURE_BLOCKED"
    elif facts["eligible_count"] < 28:
        suffix = "EXHAUSTED_INSUFFICIENT_ELIGIBLE_CAPACITY"
    elif not facts["rule_input_resolved"]:
        suffix = "COMPLETE_ALLOCATION_RULE_UNRESOLVED"
    elif facts["prospective_final_feasible"] is None:
        suffix = "CLOSURE_BLOCKED"
    elif not facts["prospective_final_feasible"]:
        suffix = "EXHAUSTED_PROJECT_DIVERSITY_INFEASIBLE"
    else:
        suffix = "COMPLETE_ALLOCATION_AUTHORITY_REQUIRED"
    return "V6_CENSUS_" + suffix


def main():
    positive = []

    def check(name, fn):
        fn()
        positive.append({"check": name, "status": "PASS"})

    data = bundle()
    historical = load(E / "entry_verification.json")["historical_inputs_sha256"]
    check(
        "exact_19_historical_inputs_preserved",
        lambda: require(
            len(historical) == 19 and all(sha(ROOT / p) == h for p, h in historical.items()),
            "historical drift",
        ),
    )
    check(
        "entry_latest_direct_instruction_bound",
        lambda: check_ref(load(E / "entry_verification.json")["instruction"]),
    )
    check("complete_candidate_bundle_semantics", lambda: validate_bundle(data))
    for name in SCHEMA_NAMES:
        check(
            "schema_meta_valid_" + name,
            lambda name=name: Draft202012Validator.check_schema(load(S / (name + ".schema.json"))),
        )
    check("exact_433_membership_rank_lineage_disjointness", lambda: validate_pool(data["pool"]))
    check("bridge_9_12_7_39_433_reference_only", lambda: validate_bridge(data["bridge"]))
    check(
        "descriptor_candidate_only_no_effective_authority",
        lambda: validate_candidate_state(data["state"], data["manifest"], data["pool"]),
    )
    # Historical semantic auditors retain all scientific checks. Only their process-local
    # path allowlist is extended; no immutable file is edited, and no old main that asserts
    # absence of canonical contracts is incorrectly treated as a successor validator.
    old = module_at(
        "immutable_proposal_audit", B / "evidence/v6_protocol_design_v1/validate_proposal.py"
    )
    old.ALLOW_NEW |= {str((ROOT / p).relative_to(B)) for p in historical.keys() | NEW_PATHS}
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        old.main()
    predecessor_result = loads(output.getvalue())
    check(
        "predecessor_all_29_positive_28_rejections_unchanged",
        lambda: require(
            predecessor_result["counts"]
            == {"positive_passed": 29, "negative_rejected": 28, "failed": 0},
            "predecessor audit failed",
        ),
    )
    final = module_at(
        "immutable_finalized_semantic_audit",
        B / "evidence/v6_protocol_design_finalization_v1/validate_finalization.py",
    )
    decision = embedded(B / "V6_PROTOCOL_DESIGN_D1_D8_HUMAN_PI_DECISION.md", "DECISION_JSON")
    design, proposal, _ = sources()
    _, expected = final.source_semantics(
        load(B / "evidence/v6_protocol_design_finalization_v1/entry_verification.json")[
            "instruction"
        ]
    )
    check(
        "accepted_62_D1_D8_source_fields_and_finalized_invariants",
        lambda: final.validate_semantics(
            decision, design, expected, final.original_hashes(), proposal
        ),
    )
    source = load(E / "entry_verification.json")["source_checkout"]
    for revision, expect in [("HEAD", source["commit"]), ("HEAD^{tree}", source["tree"])]:
        check(
            "live_bugsinpy_" + revision,
            lambda revision=revision, expect=expect: require(
                subprocess.check_output(
                    ["git", "-C", source["path"], "rev-parse", revision], text=True
                ).strip()
                == expect,
                "BugsInPy live drift",
            ),
        )
    check(
        "bugsinpy_clean",
        lambda: require(
            not subprocess.check_output(
                ["git", "-C", source["path"], "status", "--porcelain"], text=True
            ).strip(),
            "dirty BugsInPy source",
        ),
    )
    for args, expect in [
        (["branch", "--show-current"], "main"),
        (["rev-parse", "HEAD"], HEAD),
        (["diff", "--cached", "--name-only"], ""),
        (["diff", "--name-only"], ""),
    ]:
        check(
            "git_" + "_".join(args),
            lambda args=args, expect=expect: require(
                subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()
                == expect,
                "repository/index/tracked drift",
            ),
        )
    actual = set(
        subprocess.check_output(
            ["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT, text=True
        ).splitlines()
    )
    check(
        "exact_bounded_worktree_paths",
        lambda: require(
            set(historical) <= actual and actual <= set(historical) | NEW_PATHS,
            "unrelated path/write scope",
        ),
    )
    check(
        "git_diff_check", lambda: subprocess.run(["git", "diff", "--check"], cwd=ROOT, check=True)
    )
    check(
        "all_new_UTF8_JSON_python_whitespace_static", lambda: static_files(actual - set(historical))
    )
    tests = module_at("v6_candidate_rejection_matrix", E / "test_contract.py")
    matrix = tests.rejection_matrix(data)
    check(
        "rejection_matrix_complete",
        lambda: require(all(r["status"] == "PASS_REJECTED" for r in matrix), "matrix failure"),
    )
    if (E / "artifact_sha256.json").exists():
        inventory = load(E / "artifact_sha256.json")
        require(
            inventory["self_excluded"] is True
            and set(inventory["sha256"])
            == NEW_PATHS - {str((E / "artifact_sha256.json").relative_to(ROOT))},
            "inventory topology drift",
        )
        require(
            all(sha(ROOT / p) == h for p, h in inventory["sha256"].items()),
            "candidate artifact inventory drift",
        )
        require(actual == set(historical) | NEW_PATHS, "final inventory/path population drift")
    result = {
        "schema": "V6_SUCCESSOR_CONTRACT_CONSTRUCTION_VALIDATION_V1",
        "status": "PASS",
        "positive_checks": positive,
        "rejection_matrix": matrix,
        "counts": {"positive_passed": len(positive), "negative_rejected": len(matrix), "failed": 0},
        "predecessor_validation": predecessor_result["counts"],
        "pool_count": 433,
        "pool_sha256": sha(B / "v6_reconsideration_pool.csv"),
        "proposal_pool_sha256": POOL_HASH,
        "project_distribution": dict(
            sorted(Counter(r["source_project"] for r in data["pool"]).items())
        ),
        "new_oracle_repetitions_consumed": 0,
        "production_dispatches": 0,
        "actual_pilot_hashes_computed": 0,
        "actual_pilot_ids_selected": 0,
        "runtime_consumers_implemented": False,
        "schema_validation_engine": "existing .venv jsonschema Draft202012Validator",
        "historical_finalization_main_not_run": "Its absence-of-canonical-contract entry assertions belong to the historical design stage; source semantics and all finalized invariant checks were rerun directly.",
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))


def static_files(paths):
    for name in paths:
        p = ROOT / name
        text = p.read_text(encoding="utf-8")
        require(
            all(line == line.rstrip() for line in text.splitlines()), "trailing whitespace: " + name
        )
        if p.suffix == ".json":
            load(p)
        if p.suffix == ".py":
            compile(text, str(p), "exec")


if __name__ == "__main__":
    main()

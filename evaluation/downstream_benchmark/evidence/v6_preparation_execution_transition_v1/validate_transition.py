"""Read-only V6 event #3 candidate audit; no installer or execution provider.

Reuse the accepted V1 event schema, canonical hashes and pure lifecycle edge.
Mutation probes are in memory and are rehashed to reach semantic checks.
The inherited descriptor-form authority is not runtime effectivity.
"""

import ast
import copy
import hashlib
import importlib.util
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
E = Path(__file__).resolve().parent
ROOT = E.parents[3]
B = ROOT / "evaluation/downstream_benchmark"
PREFIX = str(E.relative_to(ROOT)) + "/"
HEAD = "dded507b6049ad24cdf813590e2d8e8af7e9e241"
CURRENT = "evaluation/downstream_benchmark/v6_current_state.json"
CURRENT_SHA = "6a9028c79aa62f90db2b2d53def32ab23bffcfa3c71d2ec30d7fa64e741e3aae"
REQUEST_SHA = "0146f9568763dcd1f040469c85b7bdbcb93e723a14b27a446fd7a19ec970d3e4"
FROM = "PREPARATION_PLANNING_AUTHORIZED"
TO = "PREPARATION_EXECUTION_AUTHORIZED"
GATE = "HUMAN_PI_AUTHORIZE_V6_PREPARATION_EXECUTION"
AUTHORITY = PREFIX + "execution_authority.json"
EVENT = PREFIX + "preparation_execution_event_candidate.json"
SUCCESSOR = PREFIX + "successor_descriptor_candidate.json"
NATIVE = "evaluation/downstream_benchmark/evidence/v6_native_buildkit_client_compatibility_bridge_v1/"
CLOSURE = "evaluation/downstream_benchmark/V6_PREPARATION_EXECUTION_RUNTIME_AND_EGRESS_QUALIFIED_BASELINE_LIFECYCLE_CLOSURE_V1.md"
CLOSURE_SHA = "a2a2d8f5fef0357fdad7960f45fad8aa74fdc8bf8728472162c1051a96a10949"
PLAN = "evaluation/downstream_benchmark/v6_preparation_plan_manifest_candidate.json"
PLAN_SHA = "3c0a6980360c23f6626863be232fea2878cf13497a74aa2e267594fcf3801b0e"
PLAN_CLOSURE = "evaluation/downstream_benchmark/V6_PREPARATION_PLAN_LIFECYCLE_CLOSURE_V1.md"
PLAN_CLOSURE_SHA = "9e0bbf8db1eaedb344163a98e944915a51e87424d4abf6894545056e73eccfe7"
ENFORCEMENT = "8801637324b2fa32124df8444e88f193a5be3f9c847904f2eebfb92197bc5c10"
SOURCE_SHA = "c83da6f5eb355702f994c28efc6b14bc36988a9cc405ff05a689a9f97128f4b6"
DATA_SHA = "654299e49b0fc8833f093ecc887b4578970895ce28aa5359b4b37246f7b6190e"
PREVIOUS = {
    "sequence": 2,
    "event_id": "007ac4316ab6961c628ddef19202d73a0fd3859db2de30b56f27efd2cae6121c",
    "event_sha256": "27a9778775635db017a5b783c698c86b30f0c49199f6ad96fb5bc4bcfd01b84a",
}
PREVIOUS_FILE_SHA = "b62c5d7b0a256fff1321944364816d67fd9bcb7ae1b7947964662b1fc124af6b"
FILES = {
    "human_pi_request.txt", "entry_verification.json", "execution_authority.json",
    "preparation_execution_event_candidate.json", "projection_delta.json",
    "successor_descriptor_candidate.json", "candidate_envelope.json",
    "validate_transition.py", "validation_results.json", "artifact_sha256.json",
    "RUN_REPORT.md", "commands_run.json",
}
AUTHORIZATION = {
    "transition_candidate_construction": True,
    "canonical_installation": False, "runtime_effectivity": False,
    "preparation_execution": False, "source_acquisition": False,
    "stage": False, "commit": False, "push": False,
}
BOUNDARY = {
    "profile": "NON_EFFECTIVE_TRANSITION_CANDIDATE",
    "CURRENT_AUTHORITY": "UNCHANGED_CANONICAL_PREDECESSOR_DESCRIPTOR",
    "RUNTIME_EFFECTIVE": "NO", "CURRENT_REGISTRATION": "PROHIBITED",
    "AUTO_PROMOTION": "NO", "CANONICAL_INSTALLATION_AUTHORIZED_BY_CANDIDATE": "NO",
    "CANONICAL_EVENT_COUNT": 2, "PROPOSED_EVENT_COUNT": 3,
    "CANONICAL_STATE": FROM, "PROPOSED_STATE": TO,
    "CANONICAL_RUNTIME_AUTHORITY": True, "PROPOSED_RUNTIME_AUTHORITY_FIELD": True,
    "EFFECTIVITY_BINDING_TRANSACTION": "SEPARATE_HUMAN_PI_AUTHORITY_REQUIRED",
    "NEW_DESCRIPTOR_ID": "NOT_CONSTRUCTED",
    "INSTALLATION_AUTHORITY": "NOT_CONSTRUCTED",
    "INDEPENDENT_ACCEPTANCE_PIN": "NOT_CONSTRUCTED",
}
FIREWALL = {
    "EVENT_3_CANDIDATE_CREATED": "YES", "EVENT_3_CANONICAL_EFFECTIVE": "NO",
    "CANONICAL_CURRENT_STATE_MODIFIED": "NO",
    "PREPARATION_EXECUTION_CANONICAL_EFFECTIVE": "NO", "PREPARATION_EXECUTED": "NO",
    "REAL_ATTEMPTS_CONSUMED": 0, "REAL_CLAIMS_CREATED": 0, "REAL_BUILDS_EXECUTED": 0,
    "ENVIRONMENT_READY_CASES_ESTABLISHED": 0, "SOURCE_ACQUISITION_EXECUTED": "NO",
    "ORACLE_EXECUTED": "NO", "ALLOCATION_EXECUTED": "NO",
    "GIT_STAGE": "NO", "GIT_COMMIT": "NO", "GIT_PUSH": "NO",
}


def module_at(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


t = module_at("accepted_planning_transition", B / "evidence/v6_preparation_planning_transition_v1/validate_transition.py")
v, c, a = t.v, t.c, t.a
pretty = t.pretty


def git(*args, input_bytes=None):
    return subprocess.check_output(
        ["git", *args], **({"input": input_bytes} if input_bytes is not None else {}), cwd=ROOT,
        env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
    )


def read_json(path):
    # Qualification observations legitimately contain finite floating timestamps.
    def pairs(items):
        result = {}
        for key, value in items:
            v.require(key not in result, "duplicate JSON key")
            result[key] = value
        return result

    def bad_constant(value):
        raise ValueError("nonfinite JSON value: " + value)

    return json.loads((ROOT / path).read_bytes(), object_pairs_hook=pairs, parse_constant=bad_constant)


def qualified_inventory():
    raw = (ROOT / CLOSURE).read_bytes()
    v.require(v.sha(raw) == CLOSURE_SHA, "wrong runtime closure")
    section = raw.decode().split("## 8. Exact complete accepted repository inventory", 1)[1]
    rows = re.findall(r"^\| `([^`]+)` \| `([0-9a-f]{64})` \|$", section, re.M)
    inventory = dict(rows)
    v.require(len(rows) == len(inventory) == 376, "qualified lineage inventory drift")
    return inventory


def controlling_refs():
    # The accepted closure binds the entire lineage, including historical BLOCKs.
    paths = {
        CLOSURE: CLOSURE_SHA, PLAN: PLAN_SHA, PLAN_CLOSURE: PLAN_CLOSURE_SHA,
        NATIVE + "successor_runtime.py": SOURCE_SHA,
        NATIVE + "successor_runtime_integration_candidate.json": DATA_SHA,
    }
    inventory = qualified_inventory()
    for name in (
        "network_enforcement_identity.json", "population_revalidation.json",
        "once_only_revalidation.json", "validation_results.json",
        "all_base_native_transport_qualification.json", "native_output_parity.json",
        "positive_qualification.json", "negative_qualification.json", "execution_corrections.json",
    ):
        paths[NATIVE + name] = inventory[NATIVE + name]
    for path, digest in inventory.items():
        if path.endswith("/RUN_REPORT.md"):
            paths[path] = digest
    paths["evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/ledger_candidate.json"] = "5d1f10f5fa28860d7eb47a3a56a092c2492e2a90b440904990e44a8cf014d7bc"
    return [{"path": path, "sha256": digest} for path, digest in sorted(paths.items())]


def expected_authority(current):
    return {
        "path": AUTHORITY, "namespace": "EFFECTIVE_V6", "owner": "HUMAN_PI", "gate": GATE,
        "contract_sha256": current["contract"]["sha256"],
        "prior_projection_sha256": v.digest(current["projection"]),
        "previous_descriptor_sha256": CURRENT_SHA,
        "scope": "PREPARATION_EXECUTION_TRANSITION_CANDIDATE_ONLY", "HUMAN_PI_ACCEPTED": "YES",
        "human_pi_instruction": {"path": PREFIX + "human_pi_request.txt", "sha256": REQUEST_SHA},
        "baseline": {"head": HEAD, "live_origin_main": HEAD, "committed_and_published": "YES"},
        "lifecycle_edge": {
            "from": FROM, "gate": GATE, "to": TO, "owner": "HUMAN_PI",
            "automatic_next_authority": False,
            "requires": "Exact accepted plans, separate source acquisition/materialization/build permissions, revalidated implementation; once-only attempts",
        },
        "previous_event_identity": PREVIOUS,
        "previous_event_stored_file_sha256": PREVIOUS_FILE_SHA,
        "runtime_egress_closure": {"path": CLOSURE, "sha256": CLOSURE_SHA},
        "enforcement_identity": ENFORCEMENT,
        "accepted_runtime_source": {"path": NATIVE + "successor_runtime.py", "sha256": SOURCE_SHA},
        "accepted_runtime_data": {"path": NATIVE + "successor_runtime_integration_candidate.json", "sha256": DATA_SHA},
        "accepted_plan": {"path": PLAN, "sha256": PLAN_SHA},
        "population": {"census": 433, "constructible": 431, "total_base_work_items": 641, "restricted": 583, "network_none": 58},
        "once_only": {
            "protocol": "ACCEPT_V6_PREPARATION_ONCE_ONLY_ATTEMPT_PROTOCOL_V1",
            "claim": "exclusive durable claim before work; fsync file and parent",
            "terminal": "one atomic non-overwriting terminal; no retry/reclaim",
            "partial_or_crash": "preserve and block for separate adjudication",
            "attempts_consumed_by_transition": 0,
        },
        "negative_boundaries": {
            "SOURCE_ACQUISITION": "NO", "ENVIRONMENT_MATERIALIZATION": "NO",
            "IMAGE_BUILD": "NO", "ORACLE_EXECUTION": "NO", "PILOT_FINAL_ALLOCATION": "NO",
            "DOWNSTREAM_REPAIR_EXECUTION": "NO", "REAL_DISPATCH": "REJECT",
            "CANONICAL_INSTALLATION_COMPLETE": "NO", "PREPARATION_EXECUTED": "NO",
            "ENVIRONMENT_READY_POPULATION_ESTABLISHED": 0,
        },
        "controlling_evidence": controlling_refs(),
        "candidate_acceptance": "HUMAN_PI_REVIEW_PENDING",
    }


def leaf_delta(before, after, prefix="projection"):
    if isinstance(before, dict) and isinstance(after, dict):
        v.require(before.keys() == after.keys(), "projection key topology changed")
        return [change for key in sorted(before) for change in leaf_delta(before[key], after[key], prefix + "." + key)]
    return [] if before == after else [{"path": prefix, "before": before, "after": after}]


def successor_for_event(current, event, event_raw):
    identities = v.validate_event_identity(event, event_raw)
    head = {"event_id": identities["event_id"], "sequence": event["sequence"], "event_sha256": identities["event_sha256"]}
    result = copy.deepcopy(current)
    result.update(
        lifecycle_label=event["to_state"], event_count=event["sequence"], event_head=head,
        event_chain=current["event_chain"] + [{**head, "path": EVENT, "sha256": identities["file_sha256"]}],
        projection=copy.deepcopy(event["next_projection"]), projection_sha256=event["result_projection_sha256"],
    )
    return result


def envelope_for(event_raw, successor_raw, authority):
    return {
        **BOUNDARY, "firewall": FIREWALL,
        "canonical_predecessor": {"path": CURRENT, "sha256": CURRENT_SHA},
        "event_candidate": {"path": EVENT, "sha256": v.sha(event_raw)},
        "successor_descriptor_candidate": {"path": SUCCESSOR, "sha256": v.sha(successor_raw)},
        "execution_authority": {"path": AUTHORITY, "sha256": v.digest(authority)},
        "controlling_evidence": controlling_refs(),
        "human_pi_instruction": {"path": PREFIX + "human_pi_request.txt", "sha256": REQUEST_SHA},
    }


def derive(current, authority):
    result = c.phase_flags_for_edge(current["projection"], TO)
    core = {
        "schema": "V6_CAPACITY_STATE_EVENT_V1", "namespace": "EFFECTIVE_V6", "sequence": 3,
        "kind": "STATE_TRANSITION", "previous_event_identity": copy.deepcopy(current["event_head"]),
        "previous_descriptor_sha256": CURRENT_SHA, "contract_sha256": current["contract"]["sha256"],
        "authority_reference": {"path": AUTHORITY, "sha256": v.digest(authority)},
        "gate": GATE, "from_state": FROM, "to_state": TO,
        "prior_projection_sha256": v.digest(current["projection"]),
        "result_projection_sha256": v.digest(result), "next_projection": result,
        "evidence_references": controlling_refs(), "supersession_reference": None,
        "predecessor": copy.deepcopy(current["predecessor"]),
    }
    event = {**core, "event_id": v.derive_event_id(core)}
    event_raw = pretty(event)
    successor = successor_for_event(current, event, event_raw)
    successor_raw = pretty(successor)
    return event, event_raw, successor, successor_raw, envelope_for(event_raw, successor_raw, authority)


def prereq_audit(current):
    inventory = qualified_inventory()
    pins = {**inventory, CLOSURE: CLOSURE_SHA, PLAN: PLAN_SHA, PLAN_CLOSURE: PLAN_CLOSURE_SHA,
            CURRENT: CURRENT_SHA, "evaluation/downstream_benchmark/v6_census_lifecycle.json": "7f0313e3f87bfc51e823f4bd627ada0e39a89193dff6ec2dc920e37a72582a92"}
    payload = git("cat-file", "--batch", input_bytes="".join(HEAD + ":" + p + "\n" for p in pins).encode())
    offset = 0
    for path, digest in pins.items():
        end = payload.index(b"\n", offset)
        header = payload[offset:end].split()
        v.require(len(header) == 3 and header[1] == b"blob", "missing committed baseline blob: " + path)
        size = int(header[2])
        raw = payload[end + 1:end + 1 + size]
        offset = end + 2 + size
        v.require(v.sha(raw) == v.sha((ROOT / path).read_bytes()) == digest, "committed byte drift: " + path)
    v.require(offset == len(payload), "unconsumed committed blob output")
    v.require(git("rev-parse", HEAD + "^").decode().strip() == "5c007fbfbfc5b3529105a14f87127f50e1eab6d7", "closure commit parent drift")
    changed = set(git("diff-tree", "--no-commit-id", "--name-only", "-r", HEAD).decode().splitlines())
    v.require(changed == set(inventory) | {CLOSURE}, "closure commit inventory drift")
    t.validate_plan((ROOT / PLAN).read_bytes(), (ROOT / PLAN_CLOSURE).read_bytes(), current)
    config = read_json(NATIVE + "successor_runtime_integration_candidate.json")
    v.require(v.sha((ROOT / (NATIVE + "successor_runtime.py")).read_bytes()) == SOURCE_SHA, "wrong runtime source identity")
    v.require(v.sha((ROOT / (NATIVE + "successor_runtime_integration_candidate.json")).read_bytes()) == DATA_SHA, "wrong runtime data identity")
    v.require(config["real_dispatch"] == "REJECT" and config["runtime_authority"] is False and config["Buildx_solve"] == "PROHIBITED" and config["client"] == "/usr/bin/buildctl", "runtime default deny/solve semantics drift")
    source_ast = ast.parse((ROOT / (NATIVE + "successor_runtime.py")).read_bytes())
    dispatcher = next(node for node in source_ast.body if isinstance(node, ast.FunctionDef) and node.name == "dispatch")
    v.require(len(dispatcher.body) == 2 and isinstance(dispatcher.body[0], ast.Expr) and isinstance(dispatcher.body[1], ast.Raise), "dispatcher is not unconditional default deny")
    receipt = read_json(NATIVE + "network_enforcement_identity.json")
    v.require(v.sha(pretty(receipt["SEMANTIC_ENFORCEMENT_IDENTITY"])) == receipt["semantic_enforcement_sha256"] == receipt["ENFORCEMENT_IDENTITY"] == ENFORCEMENT, "wrong enforcement identity")
    population = read_json(NATIVE + "population_revalidation.json")
    v.require(population["status"] == "PASS" and population["total"] == 641 and population["restricted"] == 583 and population["network_none"] == 58 and population["matplotlib_1_and_8_dispatchable"] is False, "population qualification drift")
    work = read_json("evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/work_items_candidate.json")
    items = work["items"]
    v.require(len(items) == len({p["base_attempt_id"] for p in items}) == 641 and sum(p["build_network_required"] for p in items) == 583, "work item opportunity/split drift")
    v.require(len({p["case_id"] for p in items}) == 431 and not {"matplotlib::1", "matplotlib::8"} & {p["case_id"] for p in items}, "blocker rescue")
    ledger = read_json("evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/ledger_candidate.json")
    v.require(len(ledger["entries"]) == 641 and all(p["state"] == "UNSTARTED" and not p["claimed"] and not p["attempt_consumed"] for p in ledger["entries"]) and not ledger["journal"], "base attempts already consumed")
    v.require([p["base_attempt_id"] for p in ledger["entries"]] == [p["base_attempt_id"] for p in items], "ledger/work order drift")
    facts = read_json(NATIVE + "validation_results.json")
    v.require(facts["all_required_checks"] == facts["all_seven_bases"] == facts["output_parity"] == "PASS" and facts["approved_origins"] == "2/2_PASS" and facts["direct_egress"] == "PROHIBITED_AND_QUALIFIED", "qualified facts missing")
    for name in ("all_base_native_transport_qualification.json", "native_output_parity.json"):
        obj = read_json(NATIVE + name)
        v.require(obj["status"] == "PASS" and obj["passed"] == obj["total"] == 7, "seven-base qualification drift")
    positive = read_json(NATIVE + "positive_qualification.json")
    v.require(positive["status"] == "PASS" and positive["passed"] == positive["total"] == 2 and positive["installs"] == 0 and all(p["TLS_verification"] == "PASS" and p["check_hostname"] and p["verify_mode"] == 2 for p in positive["observations"]), "TLS origins drift")
    negative = read_json(NATIVE + "negative_qualification.json")
    v.require(negative["status"] == "PASS" and all(p["connected"] is False for p in negative["direct_external_only_fixture"]) and negative["network_NONE"]["status"] == "PASS" and all(not p["upstream_dns"] and not p["upstream_connect"] for p in negative["deny_events"]), "egress negative evidence drift")
    once = read_json(NATIVE + "once_only_revalidation.json")
    v.require(once["status"] == "PASS" and once["failures"] == once["errors"] == once["skips"] == 0 and once["real_claims"] == [], "once-only qualification missing")
    return {"status": "PASS", "accepted_lineage_paths": len(inventory), "committed_pins_verified": len(pins), "historical_BLOCK_reports_preserved": True, "all_7_frozen_bases": "QUALIFIED", "output_parity": "PASS", "approved_TLS_origins": "2/2 PASS", "direct_egress": "PROHIBITED_AND_QUALIFIED", "solve_client": "NATIVE_BUILDCTL", "Buildx_solve": "PROHIBITED", "real_dispatch": "REJECT", "population": {"census": 433, "constructible": 431, "total": 641, "restricted": 583, "network_none": 58}, "live_runtime_qualification_rerun": False}


def load_fixture():
    return {
        "entry": v.loads((E / "entry_verification.json").read_bytes()),
        "current_raw": (ROOT / CURRENT).read_bytes(),
        "request_raw": (E / "human_pi_request.txt").read_bytes(),
        "authority": v.loads((E / "execution_authority.json").read_bytes()),
        "authority_raw": (E / "execution_authority.json").read_bytes(),
        "event": v.loads((E / "preparation_execution_event_candidate.json").read_bytes()),
        "event_raw": (E / "preparation_execution_event_candidate.json").read_bytes(),
        "successor": v.loads((E / "successor_descriptor_candidate.json").read_bytes()),
        "successor_raw": (E / "successor_descriptor_candidate.json").read_bytes(),
        "envelope": v.loads((E / "candidate_envelope.json").read_bytes()),
        "delta": v.loads((E / "projection_delta.json").read_bytes()),
    }


def validate_fixture(f, *, as_current=False):
    v.require(not as_current, "candidate claimed effective/current registration prohibited")
    entry = f["entry"]
    v.require(entry["status"] == "ENTRY_GATE_PASS" and entry["head"] == entry["live_origin_main"] == HEAD and entry["branch"] == "main" and entry["authorization"] == AUTHORIZATION and all(entry[k] for k in ("worktree_clean_before_write", "index_clean_before_write", "untracked_clean_before_write")), "entry gate drift")
    v.require(v.sha(f["request_raw"]) == entry["human_pi_request"]["sha256"] == REQUEST_SHA, "Human-PI instruction drift")
    v.require(v.sha(f["current_raw"]) == CURRENT_SHA, "wrong predecessor descriptor")
    current = v.loads(f["current_raw"])
    v.schema("V6_CAPACITY_CURRENT_STATE_V1", current)
    v.require(current["lifecycle_label"] == current["projection"]["state"] == FROM and current["event_count"] == 2 and current["event_head"] == PREVIOUS and current["event_chain"][-1]["sha256"] == PREVIOUS_FILE_SHA, "current chain/state drift")
    v.require(current["projection_sha256"] == v.digest(current["projection"]) == entry["prior_projection_sha256"] and entry["previous_event_identity"] == PREVIOUS and entry["previous_event_stored_file_sha256"] == PREVIOUS_FILE_SHA, "prior projection/event entry drift")
    edge = next(p for p in read_json("evaluation/downstream_benchmark/v6_census_lifecycle.json")["transitions"] if p["from"] == FROM)
    authority = f["authority"]
    v.require(authority["runtime_egress_closure"] == {"path": CLOSURE, "sha256": CLOSURE_SHA}, "wrong runtime closure")
    v.require(authority["enforcement_identity"] == ENFORCEMENT, "wrong enforcement identity")
    v.require(authority["accepted_runtime_source"] == {"path": NATIVE + "successor_runtime.py", "sha256": SOURCE_SHA}, "wrong runtime source identity")
    v.require(authority["accepted_runtime_data"] == {"path": NATIVE + "successor_runtime_integration_candidate.json", "sha256": DATA_SHA}, "wrong runtime data identity")
    v.require(authority["population"]["total_base_work_items"] == 641, "wrong 641 population")
    v.require(authority["population"]["restricted"] == 583 and authority["population"]["network_none"] == 58, "wrong 583/58 split")
    v.require(authority["controlling_evidence"] == controlling_refs(), "historical BLOCK evidence omitted from controlling lineage")
    v.require(authority == expected_authority(current) and authority["lifecycle_edge"] == edge, "authority owner/gate/scope/edge drift")
    v.require(f["authority_raw"] == v.canonical(authority), "authority stored-byte convention drift")
    event = f["event"]
    v.validate_event_identity(event, f["event_raw"])
    v.require(event["sequence"] == 3, "wrong sequence/event #4 creation")
    v.require(event["previous_event_identity"] == PREVIOUS, "wrong prior event")
    v.require(event["previous_descriptor_sha256"] == CURRENT_SHA, "wrong predecessor descriptor")
    v.require(event["prior_projection_sha256"] == current["projection_sha256"], "wrong prior projection")
    v.require(event["gate"] == GATE, "wrong gate")
    v.require(event["from_state"] == FROM and event["to_state"] == TO, "non-adjacent state")
    v.require(event["evidence_references"] == controlling_refs(), "historical BLOCK/controlling evidence omitted")
    prior, result = current["projection"], event["next_projection"]
    v.require(result["case_states"] == prior["case_states"], "case-state mutation/attempt consumption/environment-ready claim/blocker rescue")
    expected_delta = [
        {"path": "projection.lifecycle.PREPARATION_AUTHORIZED", "before": "NO", "after": "YES"},
        {"path": "projection.phase_authorizations.PREPARATION_EXECUTION", "before": "NO", "after": "YES"},
        {"path": "projection.state", "before": FROM, "after": TO},
    ]
    v.require(leaf_delta(prior, result) == expected_delta and result == c.phase_flags_for_edge(prior, TO), "fourth projection change/phase flag mutation")
    expected = derive(current, authority)
    v.require(event == expected[0] and f["event_raw"] == expected[1], "deterministic event or exact payload drift")
    v.schema("V6_CAPACITY_CURRENT_STATE_V1", f["successor"])
    v.require(f["successor"] == expected[2] and f["successor_raw"] == expected[3], "successor descriptor changed beyond transition/inherited effectivity identity")
    v.require(f["envelope"] == expected[4], "candidate claimed effective/automatic canonical promotion/firewall drift")
    v.require(f["delta"] == expected_delta, "projection delta report drift")
    return current, result


def replay(current, candidate, candidate_raw):
    # Reconstruct qualified genesis only for historical event #1 verification.
    old = git("show", a.HEAD + ":" + CURRENT)
    bridge_raw = (ROOT / v.BRIDGE_PATH).read_bytes()
    bridge = v.loads(bridge_raw)
    authority1 = v.loads((a.E / "activation_authority.json").read_bytes())
    _, _, event1, raw1, _, _ = a.derive(old, bridge, a.baseline_evidence(), authority1)
    v.require(raw1 == (a.E / "activation_event_candidate.json").read_bytes(), "event #1 stored replay drift")
    v.validate_genesis_event(event1, old, bridge, a.baseline_evidence(), {"reference": {"path": v.BRIDGE_PATH, "sha256": a.BRIDGE_SHA}, "bytes": bridge_raw, "HUMAN_PI_ACCEPTED": "YES", "EFFECTIVE": "YES"}, authority1)
    census_raw = (B / "evidence/v6_effective_current_descriptor_v1/effective_current_descriptor_candidate.json").read_bytes()
    census = v.loads(census_raw)
    t.historical_replay(census)
    authority2 = v.loads((t.E / "planning_authority.json").read_bytes())
    event2, raw2, planning, _, _ = t.derive(census, authority2)
    v.require(raw2 == (t.E / "planning_transition_event_candidate.json").read_bytes(), "event #2 stored replay drift")
    v.require(planning["projection"] == current["projection"] and planning["event_chain"] == current["event_chain"], "planning installed projection/chain drift")
    pin = read_json("evaluation/downstream_benchmark/V6_PREPARATION_PLANNING_EFFECTIVE_DESCRIPTOR_ACCEPTANCE_PIN_V1.json")
    v.require(pin == {"path": CURRENT, "sha256": CURRENT_SHA, "HUMAN_PI_ACCEPTED": "YES"}, "installed planning acceptance pin drift")
    projection = v.qualify_runtime_genesis(old, bridge, a.baseline_evidence())
    previous = None
    rows = []
    for sequence, event, raw, predecessor_sha in ((1, event1, raw1, v.sha(old)), (2, event2, raw2, v.sha(census_raw)), (3, candidate, candidate_raw, CURRENT_SHA)):
        identities = v.validate_event_identity(event, raw)
        v.require(event["sequence"] == sequence and event["previous_event_identity"] == previous and event["previous_descriptor_sha256"] == predecessor_sha, "full replay predecessor continuity drift")
        authority = read_json(event["authority_reference"]["path"])
        v.require(v.digest(authority) == event["authority_reference"]["sha256"] and authority["gate"] == event["gate"] and authority["owner"] == "HUMAN_PI" and authority["HUMAN_PI_ACCEPTED"] == "YES", "full replay authority drift")
        edge = next(p for p in read_json("evaluation/downstream_benchmark/v6_census_lifecycle.json")["transitions"] if p["from"] == projection["state"])
        v.require((event["from_state"], event["gate"], event["to_state"]) == (edge["from"], edge["gate"], edge["to"]), "full replay adjacent edge drift")
        v.require(event["prior_projection_sha256"] == v.digest(projection) and event["next_projection"] == c.phase_flags_for_edge(projection, event["to_state"]), "full replay projection drift")
        projection = event["next_projection"]
        v.require(event["result_projection_sha256"] == v.digest(projection), "full replay result hash drift")
        previous = {"sequence": sequence, "event_id": identities["event_id"], "event_sha256": identities["event_sha256"]}
        rows.append({"sequence": sequence, **identities, "state": projection["state"], "status": "PASS"})
    return {"status": "PASS", "events": rows, "final_projection_sha256": v.digest(projection), "genesis_qualification": "HISTORICAL_EVENT_1_ONLY; NOT_REAPPLIED_TO_EVENT_3"}


def real_attempt_state():
    root = Path("/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1")
    result = {}
    for name in ("claims", "locks", "terminals"):
        path = root / "ledger" / name
        v.require(path.is_dir() and not path.is_symlink(), "real ledger directory missing or symlink")
        result[name] = sorted(p.name for p in path.iterdir())
        v.require(result[name] == [], "real ledger not empty")
    result["output_paths_present"] = {name: os.path.lexists(root / name) for name in ("attempts", "inputs", "snapshots")}
    v.require(not any(result["output_paths_present"].values()), "real output/attempt path exists")
    return result


def preservation(entry):
    v.require(git("rev-parse", "HEAD").decode().strip() == HEAD and git("branch", "--show-current").decode().strip() == "main", "HEAD/branch changed")
    v.require(git("diff", "--name-only") == git("diff", "--cached", "--name-only") == b"", "tracked/index mutation")
    tracked = {}
    for line in git("ls-files", "--stage", "-z").split(b"\0"):
        if not line:
            continue
        meta, name = line.split(b"\t", 1)
        mode, oid, stage = meta.split()
        v.require(stage == b"0", "unmerged index")
        path = ROOT / name.decode()
        raw = os.readlink(path).encode() if path.is_symlink() else oid if mode == b"160000" else path.read_bytes()
        tracked[name.decode()] = {"mode": mode.decode(), "index_oid": oid.decode(), "sha256": hashlib.sha256(raw).hexdigest()}
    v.require(tracked == entry["tracked_files"] and v.digest(tracked) == entry["tracked_inventory_sha256"], "tracked bytes/index drift")
    untracked = {p.decode() for p in git("ls-files", "--others", "--exclude-standard", "-z").split(b"\0") if p}
    v.require(untracked <= {PREFIX + name for name in FILES} and {p.name for p in E.iterdir()} <= FILES, "unrelated/unexpected artifact or event #4")
    return {"status": "PASS", "tracked_files_byte_and_index_identical": len(tracked), "canonical_sha256": v.sha((ROOT / CURRENT).read_bytes()), "HEAD": HEAD, "tracked_diff": "EMPTY", "index_diff": "EMPTY", "real_attempt_state": real_attempt_state()}


def resign(f):
    f["authority_raw"] = v.canonical(f["authority"])
    f["event"]["authority_reference"] = {"path": AUTHORITY, "sha256": v.digest(f["authority"])}
    f["event"]["result_projection_sha256"] = v.digest(f["event"]["next_projection"])
    f["event"]["event_id"] = v.derive_event_id({k: value for k, value in f["event"].items() if k != "event_id"})
    f["event_raw"] = pretty(f["event"])
    f["successor"] = successor_for_event(v.loads(f["current_raw"]), f["event"], f["event_raw"])
    f["successor_raw"] = pretty(f["successor"])
    f["envelope"] = envelope_for(f["event_raw"], f["successor_raw"], f["authority"])


def rejection_probes(fixture):
    probes = []

    def probe(name, mutate, expected_reason, *, rehash=True, as_current=False):
        f = copy.deepcopy(fixture)
        mutate(f)
        if rehash:
            resign(f)
        try:
            validate_fixture(f, as_current=as_current)
        except ValueError as exc:
            v.require(expected_reason in str(exc), "probe rejected at unintended check: " + name + ": " + str(exc))
            probes.append({"name": name, "status": "PASS_REJECTED", "reason": str(exc), "dependent_hashes_refreshed": rehash})
        else:
            raise ValueError("accepted forbidden probe: " + name)

    def event_field(field, value):
        return lambda f: f["event"].update({field: value})

    probe("wrong_predecessor_descriptor", event_field("previous_descriptor_sha256", "0" * 64), "wrong predecessor descriptor")
    probe("wrong_prior_event", lambda f: f["event"]["previous_event_identity"].update(event_id="wrong-event"), "wrong prior event")
    probe("wrong_sequence", event_field("sequence", 2), "wrong sequence")
    probe("wrong_gate", event_field("gate", "HUMAN_PI_AUTHORIZE_V6_ORACLE_EXECUTION"), "wrong gate")
    probe("non_adjacent_state", event_field("to_state", "ORACLE_EXECUTION_AUTHORIZED"), "non-adjacent state")
    probe("fourth_projection_change", lambda f: f["event"]["next_projection"]["lifecycle"].update(ORACLE_AUTHORIZED="YES"), "fourth projection change")
    for phase in ("PREPARATION_PLANNING", "IMAGE_BUILD", "SOURCE_ACQUISITION", "ORACLE_EXECUTION"):
        value = "NO" if phase == "PREPARATION_PLANNING" else "YES"
        probe(phase + "_flipped", lambda f, p=phase, x=value: f["event"]["next_projection"]["phase_authorizations"].update({p: x}), "fourth projection change")
    for name, field, value in (
        ("case_state_mutation", "frozen_rank", 11),
        ("attempt_consumption", "attempt_consumed", True),
        ("environment_ready_claim", "environment_identity", {"path": "candidate-claimed-environment", "sha256": "0" * 64}),
    ):
        probe(name, lambda f, k=field, x=value: f["event"]["next_projection"]["case_states"][0].update({k: x}), "case-state mutation")
    probe("blocker_rescue", lambda f: next(p for p in f["event"]["next_projection"]["case_states"] if p["case_id"] == "matplotlib::1").update(phase="PREPARATION"), "case-state mutation")
    for name, field, reason in (
        ("wrong_runtime_closure", "runtime_egress_closure", "wrong runtime closure"),
        ("wrong_runtime_source_identity", "accepted_runtime_source", "wrong runtime source identity"),
        ("wrong_runtime_data_identity", "accepted_runtime_data", "wrong runtime data identity"),
    ):
        probe(name, lambda f, k=field: f["authority"][k].update(sha256="0" * 64), reason)
    probe("wrong_enforcement_identity", lambda f: f["authority"].update(enforcement_identity="0" * 64), "wrong enforcement identity")
    probe("wrong_641_population", lambda f: f["authority"]["population"].update(total_base_work_items=640), "wrong 641 population")
    probe("wrong_583_58_split", lambda f: f["authority"]["population"].update(restricted=582, network_none=59), "wrong 583/58 split")
    probe("historical_BLOCK_evidence_omitted", lambda f: f["event"].update(evidence_references=[p for p in f["event"]["evidence_references"] if "v6_buildkit_frozen_base_transport_bridge_v1/RUN_REPORT.md" not in p["path"]]), "historical BLOCK/controlling evidence omitted")
    probe("authority_historical_BLOCK_lineage_omitted", lambda f: f["authority"].update(controlling_evidence=[p for p in f["authority"]["controlling_evidence"] if "v6_buildkit_frozen_base_transport_bridge_v1/RUN_REPORT.md" not in p["path"]]), "historical BLOCK evidence omitted")
    probe("candidate_claimed_effective", lambda f: f["envelope"].update(RUNTIME_EFFECTIVE="YES"), "candidate claimed effective", rehash=False)
    probe("candidate_as_current", lambda f: None, "candidate claimed effective", rehash=False, as_current=True)
    probe("automatic_canonical_promotion", lambda f: f["envelope"].update(AUTO_PROMOTION="YES"), "automatic canonical promotion", rehash=False)
    probe("current_registration", lambda f: f["envelope"].update(CURRENT_REGISTRATION="ALLOWED"), "candidate claimed effective", rehash=False)
    probe("event_4_creation", event_field("sequence", 4), "event #4 creation")
    probe("wrong_prior_projection", event_field("prior_projection_sha256", "0" * 64), "wrong prior projection")
    probe("inherited_effectivity_identity_replaced", lambda f: f["successor"]["effective_current_descriptor_identity"].update(descriptor_id="V6_UNAUTHORIZED_EXECUTION_ID"), "successor descriptor changed", rehash=False)
    probe("arbitrary_event_id", lambda f: f["event"].update(event_id="arbitrary"), "noncanonical event_id", rehash=False)
    return probes


def audit():
    f = load_fixture()
    before = preservation(f["entry"])
    current, result = validate_fixture(f)
    prereqs = prereq_audit(current)
    chain = replay(current, f["event"], f["event_raw"])
    probes = rejection_probes(f)
    after = preservation(f["entry"])
    v.require(before == after, "protected state changed during audit")
    cases = result["case_states"]
    checks = {
        "exact_adjacent_edge_and_Human_PI_gate": True,
        "sequence_3_previous_event_2_exact": True,
        "deterministic_event_id_and_canonical_payload_hash": True,
        "exact_predecessor_and_prior_result_projection_hashes": True,
        "exactly_three_projection_leaves": len(f["delta"]) == 3,
        "lifecycle_label_and_event_head_consistent": f["successor"]["lifecycle_label"] == TO and f["successor"]["event_head"]["sequence"] == 3,
        "event_count_2_to_3": current["event_count"] == 2 and f["successor"]["event_count"] == 3,
        "all_433_case_states_unchanged": len(cases) == 433 and cases == current["projection"]["case_states"],
        "all_cases_NOT_STARTED": all(p["phase"] == "NOT_STARTED" for p in cases),
        "attempts_consumed_zero": sum(p["attempt_consumed"] for p in cases) == 0,
        "environment_identities_and_ready_zero": all(p["environment_identity"] is None for p in cases),
        "slot_outcomes_zero": all(p["slot_accounting"] == [] for p in cases),
        "scientific_classifications_unchanged": cases == current["projection"]["case_states"],
        "PREPARATION_PLANNING_retained_YES": result["phase_authorizations"]["PREPARATION_PLANNING"] == "YES",
        "execution_and_preparation_authorized_candidate_YES": result["phase_authorizations"]["PREPARATION_EXECUTION"] == result["lifecycle"]["PREPARATION_AUTHORIZED"] == "YES",
        "all_five_downstream_phase_boundaries_NO": all(result["phase_authorizations"][k] == "NO" for k in ("SOURCE_ACQUISITION", "IMAGE_BUILD", "ORACLE_EXECUTION", "PILOT_FINAL_ALLOCATION", "DOWNSTREAM_REPAIR_EXECUTION")),
        "641_opportunities_583_58_split_and_blockers_unchanged": prereqs["status"] == "PASS",
        "event_1_2_3_full_replay": chain["status"] == "PASS",
        "runtime_default_deny_preserved": prereqs["real_dispatch"] == "REJECT",
        "inherited_descriptor_authority_form_preserved": f["successor"]["runtime_authority"] is current["runtime_authority"] and f["successor"]["effective_current_descriptor_identity"] == current["effective_current_descriptor_identity"],
        "non_effective_outside_canonical": SUCCESSOR != CURRENT and f["envelope"]["RUNTIME_EFFECTIVE"] == "NO",
        "all_rejection_probes_rejected": all(p["status"] == "PASS_REJECTED" for p in probes),
        "canonical_tracked_index_and_real_ledger_unchanged": after["canonical_sha256"] == CURRENT_SHA,
    }
    v.require(all(checks.values()), "positive check failed")
    return {
        "status": "PASS", "positive_check_count": len(checks), "rejection_probe_count": len(probes), "failed_checks": 0,
        "positive_checks": checks, "rejection_probes": probes, "prerequisites": prereqs,
        "event_identities": v.validate_event_identity(f["event"], f["event_raw"]),
        "successor_descriptor_sha256": v.sha(f["successor_raw"]),
        "prior_projection_sha256": current["projection_sha256"], "result_projection_sha256": v.digest(result),
        "case_states_canonical_sha256_before_and_after": v.digest(cases),
        "event_chain_replay": chain, "preservation": after, "firewall": FIREWALL,
        "qualification": "Candidate transaction and committed-evidence replay only; no live runtime/build/egress/subject execution or scientific validation",
    }


def readonly_guard(event, args):
    if event == "open" and isinstance(args[0], int) and stat.S_ISFIFO(os.fstat(args[0]).st_mode):
        # Anonymous subprocess pipes carry read-only Git blob requests, not files.
        return
    if event == "subprocess.Popen":
        argv = args[1]
        allowed = {"rev-parse", "diff", "ls-files", "show", "log", "diff-tree", "cat-file"}
        branch_read = argv == ["git", "branch", "--show-current"]
        if not isinstance(argv, (list, tuple)) or len(argv) < 2 or argv[0] != "git" or (argv[1] not in allowed and not branch_read):
            raise RuntimeError("read-only audit forbids non-local-Git execution")
    else:
        t.readonly_guard(event, args)


if __name__ == "__main__":
    v.require(sys.argv[1:] in ([], ["--json"]), "expected no argument or --json")
    sys.addaudithook(readonly_guard)
    result = audit()
    recorded = E / "validation_results.json"
    if recorded.exists():
        v.require(recorded.read_bytes() == pretty(result), "stored results differ from fresh audit")
    manifest_path = E / "artifact_sha256.json"
    if manifest_path.exists():
        manifest = v.loads(manifest_path.read_bytes())
        v.require(set(manifest["artifacts"]) == {PREFIX + name for name in FILES - {"artifact_sha256.json"}}, "artifact manifest inventory drift")
        v.require({p.name for p in E.iterdir()} == FILES, "exact artifact inventory drift")
        for path, digest in manifest["artifacts"].items():
            v.require(v.sha((ROOT / path).read_bytes()) == digest, "artifact byte drift: " + path)
    if sys.argv[1:] == ["--json"]:
        sys.stdout.write(pretty(result).decode())
    else:
        print(json.dumps({k: result[k] for k in ("status", "positive_check_count", "rejection_probe_count", "failed_checks", "event_identities", "successor_descriptor_sha256")}, sort_keys=True))

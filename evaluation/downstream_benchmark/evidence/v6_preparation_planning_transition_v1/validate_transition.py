"""Bounded candidate replay and rejection evidence; never installs or executes.

The unchanged frozen V1 schemas, event identity and phase derivation are reused.
This is a transaction audit adapter, not a production event consumer. All
mutation probes are in memory. Running this file writes no files.
"""

import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
E = Path(__file__).resolve().parent
ROOT = E.parents[3]
B = ROOT / "evaluation/downstream_benchmark"
PREFIX = str(E.relative_to(ROOT)) + "/"
HEAD = "ee7ff4672441ddbcfba6dfaca4ed69973331e85d"
CURRENT = "evaluation/downstream_benchmark/v6_current_state.json"
CURRENT_SHA = "9295430e8573474b17bc79339c92f46044e443b9dabfe81280f9fb789d751073"
PLAN = "evaluation/downstream_benchmark/v6_preparation_plan_manifest_candidate.json"
PLAN_SHA = "3c0a6980360c23f6626863be232fea2878cf13497a74aa2e267594fcf3801b0e"
CLOSURE = "evaluation/downstream_benchmark/V6_PREPARATION_PLAN_LIFECYCLE_CLOSURE_V1.md"
CLOSURE_SHA = "9e0bbf8db1eaedb344163a98e944915a51e87424d4abf6894545056e73eccfe7"
REQUEST_SHA = "c0ed2a16ad6965110612151abe201cd55edef3937d90d35179a600a0a74e362a"
GATE = "HUMAN_PI_AUTHORIZE_V6_PREPARATION_PLANNING"
FROM = "CENSUS_MEMBERSHIP_ACTIVATED"
TO = "PREPARATION_PLANNING_AUTHORIZED"
EVENT = PREFIX + "planning_transition_event_candidate.json"
SUCCESSOR = PREFIX + "successor_descriptor_candidate.json"
AUTHORITY = PREFIX + "planning_authority.json"
FILES = {
    "human_pi_request.txt",
    "entry_verification.json",
    "planning_authority.json",
    "planning_transition_event_candidate.json",
    "successor_descriptor_candidate.json",
    "candidate_envelope.json",
    "projection_delta.json",
    "validate_transition.py",
    "validation_results.json",
    "RUN_REPORT.md",
    "artifact_sha256.json",
}
AUTHORIZATION = {
    "transition_candidate_construction": True,
    "successor_descriptor_candidate_construction": True,
    "canonical_installation": False,
    "runtime_effectivity": False,
    "preparation_execution": False,
    "source_acquisition": False,
    "stage": False,
    "commit": False,
    "push": False,
}
BOUNDARY = {
    "profile": "NON_EFFECTIVE_TRANSITION_CANDIDATE",
    "CURRENT_AUTHORITY": "UNCHANGED_CANONICAL_PREDECESSOR_DESCRIPTOR",
    "RUNTIME_EFFECTIVE": "NO",
    "CANONICAL_INSTALLATION_AUTHORIZED_BY_CANDIDATE": "NO",
    "AUTO_PROMOTION": "NO",
    "CURRENT_REGISTRATION": "PROHIBITED",
    "CANONICAL_EVENT_COUNT": 1,
    "PROPOSED_EVENT_COUNT": 2,
    "CANONICAL_STATE": FROM,
    "PROPOSED_STATE": TO,
    "CANONICAL_PREPARATION_PLANNING": "NO",
    "PROPOSED_PREPARATION_PLANNING": "YES",
    "CANONICAL_RUNTIME_AUTHORITY": True,
    "PROPOSED_RUNTIME_AUTHORITY_FIELD": True,
}


def module_at(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


a = module_at(
    "frozen_activation_for_planning",
    B / "evidence/v6_census_membership_activation_v1_after_genesis_bridge/validate_activation.py",
)
v = a.v
c = a.c


def pretty(value):
    v.canonical(value)
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def git(*args):
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"}
    )


def ref(path, raw):
    return {"path": path, "sha256": v.sha(raw)}


def planning_refs():
    return sorted(
        [{"path": PLAN, "sha256": PLAN_SHA}, {"path": CLOSURE, "sha256": CLOSURE_SHA}],
        key=lambda item: (item["path"].encode("utf-8"), item["sha256"]),
    )


def projection_delta(prior, result):
    return [
        {"path": "projection.state", "before": prior["state"], "after": result["state"]},
        {
            "path": "projection.phase_authorizations.PREPARATION_PLANNING",
            "before": prior["phase_authorizations"]["PREPARATION_PLANNING"],
            "after": result["phase_authorizations"]["PREPARATION_PLANNING"],
        },
    ]


def expected_authority(current):
    # The accepted authority-reference shape is retained; no future ID is bound.
    return {
        "path": AUTHORITY,
        "namespace": "EFFECTIVE_V6",
        "owner": "HUMAN_PI",
        "gate": GATE,
        "contract_sha256": current["contract"]["sha256"],
        "prior_projection_sha256": v.digest(current["projection"]),
        "previous_descriptor_sha256": CURRENT_SHA,
        "scope": "PREPARATION_PLANNING_ONLY",
        "HUMAN_PI_ACCEPTED": "YES",
    }


def derive(current, authority):
    """Start at installed projection; do not reapply genesis qualification."""
    result = c.phase_flags_for_edge(current["projection"], TO)
    core = {
        "schema": "V6_CAPACITY_STATE_EVENT_V1",
        "namespace": "EFFECTIVE_V6",
        "sequence": 2,
        "kind": "STATE_TRANSITION",
        "previous_event_identity": copy.deepcopy(current["event_head"]),
        "previous_descriptor_sha256": CURRENT_SHA,
        "contract_sha256": current["contract"]["sha256"],
        "authority_reference": {"path": AUTHORITY, "sha256": v.digest(authority)},
        "gate": GATE,
        "from_state": FROM,
        "to_state": TO,
        "prior_projection_sha256": v.digest(current["projection"]),
        "result_projection_sha256": v.digest(result),
        "next_projection": result,
        "evidence_references": planning_refs(),
        "supersession_reference": None,
        "predecessor": copy.deepcopy(current["predecessor"]),
    }
    event = {**core, "event_id": v.derive_event_id(core)}
    event_raw = pretty(event)
    successor = successor_for_event(current, event, event_raw)
    successor_raw = pretty(successor)
    envelope = envelope_for(event_raw, successor_raw, authority)
    return event, event_raw, successor, successor_raw, envelope


def successor_for_event(current, event, event_raw):
    identities = v.validate_event_identity(event, event_raw)
    head = {
        "event_id": identities["event_id"],
        "sequence": 2,
        "event_sha256": identities["event_sha256"],
    }
    successor = copy.deepcopy(current)
    successor.update(
        lifecycle_label=event["next_projection"]["state"],
        event_count=2,
        event_head=head,
        event_chain=current["event_chain"]
        + [{**head, "path": EVENT, "sha256": identities["file_sha256"]}],
        projection=copy.deepcopy(event["next_projection"]),
        projection_sha256=v.digest(event["next_projection"]),
    )
    return successor


def envelope_for(event_raw, successor_raw, authority):
    # This external profile is audit metadata, not a new V1 event/descriptor schema.
    return {
        **BOUNDARY,
        "canonical_predecessor": {"path": CURRENT, "sha256": CURRENT_SHA},
        "event_candidate": ref(EVENT, event_raw),
        "successor_descriptor_candidate": ref(SUCCESSOR, successor_raw),
        "planning_authority": {"path": AUTHORITY, "sha256": v.digest(authority)},
        "controlling_planning_evidence": planning_refs(),
        "human_pi_instruction": {"path": PREFIX + "human_pi_request.txt", "sha256": REQUEST_SHA},
    }


def load_fixture():
    def raw(name):
        return (E / name).read_bytes()

    return {
        "entry": v.loads(raw("entry_verification.json")),
        "current_raw": (ROOT / CURRENT).read_bytes(),
        "plan_raw": (ROOT / PLAN).read_bytes(),
        "closure_raw": (ROOT / CLOSURE).read_bytes(),
        "request_raw": raw("human_pi_request.txt"),
        "authority": v.loads(raw("planning_authority.json")),
        "authority_raw": raw("planning_authority.json"),
        "event": v.loads(raw("planning_transition_event_candidate.json")),
        "event_raw": raw("planning_transition_event_candidate.json"),
        "successor": v.loads(raw("successor_descriptor_candidate.json")),
        "successor_raw": raw("successor_descriptor_candidate.json"),
        "envelope": v.loads(raw("candidate_envelope.json")),
        "delta": v.loads(raw("projection_delta.json")),
    }


def validate_plan(plan_raw, closure_raw, current):
    v.require(v.sha(plan_raw) == PLAN_SHA, "accepted plan-manifest drift or blocker rescue")
    v.require(v.sha(closure_raw) == CLOSURE_SHA, "accepted plan lifecycle-closure drift")
    plan = v.loads(plan_raw)
    closure = a.closure(closure_raw)
    v.require(
        closure["authority"]["acceptance"] == "ACCEPT_V6_PREPARATION_PLAN",
        "plan acceptance missing",
    )
    v.require(
        closure["lifecycle"]["V6_PREPARATION_PLAN"]
        == ["HUMAN_PI_ACCEPTED", "FROZEN", "PERSISTED", "COMMITTED"]
        and closure["lifecycle"]["COMMITTED"] == closure["lifecycle"]["PERSISTED"] == "YES",
        "plan lifecycle incomplete",
    )
    v.require(
        plan["counts"]
        == {
            "EXPECTED_VARIANT_BINDINGS": 866,
            "ORACLE_REPRESENTATION_BLOCKED": 1,
            "PLAN_CONSTRUCTIBLE": 431,
            "REQUIREMENTS_REPRESENTATION_BLOCKED": 0,
            "RUNTIME_REPRESENTATION_BLOCKED": 0,
            "SETUP_REPRESENTATION_BLOCKED": 1,
            "SOURCE_ACQUISITION_REQUIRED": 0,
            "SOURCE_IDENTITY_BLOCKED": 0,
            "TOTAL_CENSUS_CASES": 433,
            "UNDERDETERMINED": 0,
        },
        "accepted plan count drift",
    )
    cases = current["projection"]["case_states"]
    v.require(len(plan["plans"]) == len(cases) == 433, "population drift")
    v.require(
        [p["case_id"] for p in plan["plans"]] == [p["case_id"] for p in cases],
        "accepted census order drift",
    )
    v.require(
        [p["census_order"] for p in plan["plans"]] == list(range(1, 434)), "plan ordinal drift"
    )
    dispositions = Counter(p["planning_disposition"] for p in plan["plans"])
    v.require(
        dispositions
        == {
            "PREPARATION_PLAN_CONSTRUCTIBLE": 431,
            "PREPARATION_PLAN_BLOCKED_SETUP_REPRESENTATION": 1,
            "PREPARATION_PLAN_BLOCKED_ORACLE_REPRESENTATION": 1,
        },
        "plan disposition drift",
    )
    blockers = {p["case_id"]: p for p in plan["plans"] if p["blockers"]}
    v.require(set(blockers) == {"matplotlib::1", "matplotlib::8"}, "blocker identity drift")
    for block in closure["blockers"]:
        p = blockers[block["case_id"]]
        v.require(
            block["resolved"] is False
            and p["plan_sha256"] == block["plan_sha256"]
            and p["planning_disposition"] == block["planning_disposition"],
            "blocker rescue/reclassification",
        )
    v.require(
        blockers["matplotlib::1"]["blockers"][0]["lines"][1]["text"]
        == "python -mpip install -ve .",
        "setup literal repaired",
    )
    v.require(
        blockers["matplotlib::8"]["oracle"]["commands"]
        == [
            "pytest lib/matplotlib/tests/test_axes.py::test_unautoscaley;pytest lib/matplotlib/tests/test_axes.py::test_unautoscalex"
        ]
        and blockers["matplotlib::8"]["oracle"]["argv"] == [],
        "oracle literal repaired or split",
    )
    return plan, closure


def validate_fixture(f, *, as_current=False):
    v.require(not as_current, "candidate-as-current consumption prohibited")
    entry = f["entry"]
    v.require(
        entry["status"] == "ENTRY_GATE_PASS" and entry["authorization"] == AUTHORIZATION,
        "entry authorization drift",
    )
    v.require(
        entry["head"] == entry["live_origin_main"] == HEAD
        and entry["branch"] == "main"
        and entry["worktree_clean_before_write"]
        and entry["index_clean_before_write"],
        "entry prerequisite drift",
    )
    v.require(
        v.sha(f["request_raw"]) == entry["human_pi_request"]["sha256"] == REQUEST_SHA,
        "direct Human-PI request drift",
    )
    v.require(
        GATE in f["request_raw"].decode() and "Do NOT install" in f["request_raw"].decode(),
        "planning-only direct request missing",
    )
    v.require(v.sha(f["current_raw"]) == CURRENT_SHA, "current canonical descriptor drift")
    current = v.loads(f["current_raw"])
    v.schema("V6_CAPACITY_CURRENT_STATE_V1", current)
    v.require(
        current["lifecycle_label"] == current["projection"]["state"] == FROM
        and current["event_count"] == 1
        and current["runtime_authority"] is True,
        "current entry state drift",
    )
    v.require(
        current["projection_sha256"] == v.digest(current["projection"]),
        "current projection hash mismatch",
    )
    v.require(
        entry["previous_event_identity"] == current["event_head"]
        and entry["prior_projection_sha256"] == current["projection_sha256"],
        "entry chain/projection drift",
    )
    validate_plan(f["plan_raw"], f["closure_raw"], current)
    lifecycle = v.loads((B / "v6_census_lifecycle.json").read_bytes())
    edge = next(e for e in lifecycle["transitions"] if e["from"] == FROM)
    v.require(
        edge
        == {
            "from": FROM,
            "to": TO,
            "gate": GATE,
            "owner": "HUMAN_PI",
            "requires": "Exact activated census and separately authorized planning scope; source acquisition authority remains distinct",
            "automatic_next_authority": False,
        },
        "frozen lifecycle edge drift",
    )
    authority = f["authority"]
    v.require(
        authority == expected_authority(current),
        "planning authority owner/gate/scope/identity drift",
    )
    v.require(f["authority_raw"] == v.canonical(authority), "stored planning authority differs")
    event = f["event"]
    v.validate_event_identity(event, f["event_raw"])
    v.require(
        event["namespace"] == "EFFECTIVE_V6" and event["kind"] == "STATE_TRANSITION",
        "event namespace/kind drift",
    )
    v.require(
        event["sequence"] == 2 and event["previous_event_identity"] == current["event_head"],
        "event-chain sequence/previous head mismatch",
    )
    v.require(
        event["previous_descriptor_sha256"] == CURRENT_SHA
        and event["prior_projection_sha256"] == current["projection_sha256"],
        "event predecessor descriptor/projection mismatch",
    )
    v.require(
        event["from_state"] == FROM and event["to_state"] == TO and event["gate"] == GATE,
        "wrong gate/state or nonadjacent edge",
    )
    v.require(
        event["authority_reference"] == {"path": AUTHORITY, "sha256": v.digest(authority)},
        "event authority-reference mismatch",
    )
    v.require(
        event["evidence_references"] == planning_refs() and event["supersession_reference"] is None,
        "controlling plan evidence/supersession drift",
    )
    result = event["next_projection"]
    prior = current["projection"]
    v.require(
        result["case_states"] == prior["case_states"], "case-state mutation or blocker rescue"
    )
    v.require(
        result["lifecycle"] == prior["lifecycle"]
        and result["lifecycle"]["PREPARATION_AUTHORIZED"] == "NO",
        "execution lifecycle authority leakage",
    )
    expected_phases = {**prior["phase_authorizations"], "PREPARATION_PLANNING": "YES"}
    v.require(
        result["phase_authorizations"] == expected_phases,
        "execution/source/other phase authority leakage",
    )
    v.require(
        result == c.phase_flags_for_edge(prior, TO), "projection changed beyond exact frozen edge"
    )
    v.require(
        event["result_projection_sha256"] == v.digest(result), "result projection hash mismatch"
    )
    expected = derive(current, authority)
    v.require(
        event == expected[0] and f["event_raw"] == expected[1],
        "exact deterministic event replay mismatch",
    )
    v.schema("V6_CAPACITY_CURRENT_STATE_V1", f["successor"])
    v.require(
        f["successor"] == expected[2] and f["successor_raw"] == expected[3],
        "successor descriptor chain/authority/replay mismatch",
    )
    v.require(f["envelope"] == expected[4], "external non-effective candidate boundary drift")
    v.require(f["delta"] == projection_delta(prior, result), "projection delta report drift")
    return current, result, v.validate_event_identity(event, f["event_raw"])


def preservation(entry):
    v.require(git("rev-parse", "HEAD").decode().strip() == HEAD, "HEAD changed")
    v.require(git("branch", "--show-current").decode().strip() == "main", "branch changed")
    v.require(
        git("diff", "--name-only") == b"" and git("diff", "--cached", "--name-only") == b"",
        "tracked worktree/index changed",
    )
    tracked = {}
    for line in git("ls-files", "--stage", "-z").split(b"\0"):
        if not line:
            continue
        meta, name = line.split(b"\t", 1)
        mode, oid, stage = meta.split()
        v.require(stage == b"0", "unmerged tracked path")
        path = ROOT / name.decode()
        raw = (
            os.readlink(path).encode()
            if path.is_symlink()
            else oid
            if mode == b"160000"
            else path.read_bytes()
        )
        tracked[name.decode()] = {
            "mode": mode.decode(),
            "index_oid": oid.decode(),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
    v.require(
        tracked == entry["tracked_files"]
        and v.digest(tracked) == entry["tracked_inventory_sha256"],
        "preexisting tracked bytes/index drift",
    )
    untracked = {
        p.decode()
        for p in git("ls-files", "--others", "--exclude-standard", "-z").split(b"\0")
        if p
    }
    v.require(untracked <= {PREFIX + name for name in FILES}, "unrelated/unexpected new artifact")
    v.require({p.name for p in E.iterdir()} <= FILES, "unexpected evidence artifact")
    return {
        "tracked_files_byte_and_index_identical": len(tracked),
        "canonical_sha256": v.sha((ROOT / CURRENT).read_bytes()),
        "tracked_worktree_diff": "EMPTY",
        "index_diff": "EMPTY",
        "HEAD_unchanged": True,
        "only_authorized_new_paths": True,
    }


def historical_replay(current):
    """Verify event #1 historically; Q is never used for the event #2 derivation."""
    old = git("show", a.HEAD + ":" + CURRENT)
    bridge_raw = (ROOT / v.BRIDGE_PATH).read_bytes()
    bridge = v.loads(bridge_raw)
    authority = v.loads((a.E / "activation_authority.json").read_bytes())
    _, result, event, event_raw, _, _ = a.derive(old, bridge, a.baseline_evidence(), authority)
    v.require(
        event_raw == (a.E / "activation_event_candidate.json").read_bytes(),
        "event #1 stored replay mismatch",
    )
    acceptance = {
        "reference": {"path": v.BRIDGE_PATH, "sha256": a.BRIDGE_SHA},
        "bytes": bridge_raw,
        "HUMAN_PI_ACCEPTED": "YES",
        "EFFECTIVE": "YES",
    }
    v.validate_genesis_event(event, old, bridge, a.baseline_evidence(), acceptance, authority)
    v.validate_bootstrap_descriptor(
        current, event, event_raw, current["event_chain"][0]["path"], result, old
    )
    v.require(
        current
        == v.loads(
            (
                B
                / "evidence/v6_effective_current_descriptor_v1/effective_current_descriptor_candidate.json"
            ).read_bytes()
        ),
        "accepted installed descriptor mismatch",
    )
    pin = v.loads((B / "V6_EFFECTIVE_CURRENT_DESCRIPTOR_ACCEPTANCE_PIN_V1.json").read_bytes())
    v.require(
        pin == {"path": CURRENT, "sha256": CURRENT_SHA, "HUMAN_PI_ACCEPTED": "YES"},
        "current exact acceptance pin drift",
    )
    return True


def validate_plan_commit(closure):
    v.require(
        git("rev-parse", "HEAD^").decode().strip() == closure["parent_commit"],
        "plan enclosing parent mismatch",
    )
    v.require(
        git("log", "-1", "--format=%s").decode().strip()
        == closure["commit_scope"]["required_message"],
        "plan commit message mismatch",
    )
    paths = set(
        git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").decode().splitlines()
    )
    v.require(paths == set(closure["commit_scope"]["paths"]), "plan commit scope mismatch")
    for path, digest in closure["accepted_paths_sha256"].items():
        v.require(
            v.sha((ROOT / path).read_bytes()) == v.sha(git("show", "HEAD:" + path)) == digest,
            "accepted plan input/committed bytes drift: " + path,
        )
    v.require(v.sha(git("show", "HEAD:" + CLOSURE)) == CLOSURE_SHA, "committed plan closure drift")
    return True


def resign(f):
    """Refresh all dependent identities so probes reach semantic checks."""
    core = {k: value for k, value in f["event"].items() if k != "event_id"}
    f["event"]["event_id"] = v.derive_event_id(core)
    f["event_raw"] = pretty(f["event"])
    current = v.loads(f["current_raw"])
    f["successor"] = successor_for_event(current, f["event"], f["event_raw"])
    f["successor_raw"] = pretty(f["successor"])
    f["envelope"] = envelope_for(f["event_raw"], f["successor_raw"], f["authority"])


def rejection_matrix(fixture):
    probes = []

    def reject(name, mutate=None, *, signed=False, as_current=False):
        f = copy.deepcopy(fixture)
        try:
            if mutate:
                mutate(f)
            if signed:
                resign(f)
            validate_fixture(f, as_current=as_current)
        except ValueError as error:
            probes.append({"probe": name, "status": "PASS_REJECTED", "reason": str(error)})
        else:
            raise ValueError("probe was accepted: " + name)

    for name, field, value in [
        ("wrong_gate", "gate", "HUMAN_PI_AUTHORIZE_V6_PREPARATION_EXECUTION"),
        ("wrong_from_state", "from_state", "CONTRACT_PUBLISHED_WHERE_REQUIRED"),
        ("wrong_to_state_nonadjacent", "to_state", "PREPARATION_EXECUTION_AUTHORIZED"),
        ("wrong_kind", "kind", "CASE_DISPOSITION"),
        ("wrong_namespace", "namespace", "CANDIDATE_TEST_ONLY"),
        ("wrong_sequence", "sequence", 3),
        ("genesis_reset", "sequence", 1),
        ("missing_previous_event", "previous_event_identity", None),
        ("wrong_previous_descriptor", "previous_descriptor_sha256", "0" * 64),
        ("wrong_prior_projection_hash", "prior_projection_sha256", "0" * 64),
        ("wrong_result_projection_hash", "result_projection_sha256", "0" * 64),
        ("missing_controlling_plan_evidence", "evidence_references", []),
    ]:
        reject(
            name, lambda f, field=field, value=value: f["event"].update({field: value}), signed=True
        )
    for field in ("event_id", "event_sha256", "sequence"):
        reject(
            "previous_event_" + field + "_mismatch",
            lambda f, field=field: f["event"]["previous_event_identity"].update(
                {field: 9 if field == "sequence" else "0" * 64}
            ),
            signed=True,
        )
    for phase in (
        "SOURCE_ACQUISITION",
        "PREPARATION_EXECUTION",
        "IMAGE_BUILD",
        "ORACLE_EXECUTION",
        "PILOT_FINAL_ALLOCATION",
        "DOWNSTREAM_REPAIR_EXECUTION",
    ):
        reject(
            "authority_leak_" + phase.lower(),
            lambda f, phase=phase: f["event"]["next_projection"]["phase_authorizations"].update(
                {phase: "YES"}
            ),
            signed=True,
        )
    for flag in ("PREPARATION_AUTHORIZED", "ORACLE_AUTHORIZED", "ALLOCATION_AUTHORIZED"):
        reject(
            "lifecycle_leak_" + flag.lower(),
            lambda f, flag=flag: f["event"]["next_projection"]["lifecycle"].update({flag: "YES"}),
            signed=True,
        )
    reject(
        "planning_flag_not_granted",
        lambda f: f["event"]["next_projection"]["phase_authorizations"].update(
            PREPARATION_PLANNING="NO"
        ),
        signed=True,
    )
    for field, value in [
        ("attempt_consumed", True),
        ("phase", "ENVIRONMENT_READY"),
        ("environment_identity", {"fabricated": True}),
        ("oracle_plan_reference", {"path": "fabricated", "sha256": "0" * 64}),
        ("slot_accounting", ["fabricated"]),
        ("eligible", True),
    ]:
        reject(
            "case_mutation_" + field,
            lambda f, field=field, value=value: f["event"]["next_projection"]["case_states"][
                0
            ].update({field: value}),
            signed=True,
        )
    reject(
        "case_order_mutation",
        lambda f: f["event"]["next_projection"]["case_states"].reverse(),
        signed=True,
    )
    reject(
        "case_membership_mutation",
        lambda f: f["event"]["next_projection"]["case_states"].pop(),
        signed=True,
    )
    for case_id in ("matplotlib::1", "matplotlib::8"):

        def rescue(f, case_id=case_id):
            next(
                p for p in f["event"]["next_projection"]["case_states"] if p["case_id"] == case_id
            )["phase"] = "ENVIRONMENT_READY"

        reject("canonical_blocker_rescue_" + case_id, rescue, signed=True)

        def rescue_plan(f, case_id=case_id):
            m = v.loads(f["plan_raw"])
            p = next(p for p in m["plans"] if p["case_id"] == case_id)
            p.update(planning_disposition="PREPARATION_PLAN_CONSTRUCTIBLE", blockers=[])
            f["plan_raw"] = v.canonical(m)

        reject("accepted_plan_blocker_rescue_" + case_id, rescue_plan)
    reject("plan_manifest_byte_drift", lambda f: f.update(plan_raw=f["plan_raw"] + b"\n"))
    reject("plan_closure_byte_drift", lambda f: f.update(closure_raw=f["closure_raw"] + b"\n"))
    reject("direct_request_drift", lambda f: f.update(request_raw=f["request_raw"] + b"\n"))
    reject("arbitrary_event_id", lambda f: f["event"].update(event_id="0" * 64))
    reject("event_stored_bytes_drift", lambda f: f.update(event_raw=f["event_raw"] + b"\n"))
    reject(
        "invented_event_timestamp", lambda f: f["event"].update(timestamp="2026-10-06"), signed=True
    )
    reject("event_self_hash", lambda f: f["event"].update(event_sha256="0" * 64), signed=True)
    for field, value in [
        ("gate", "HUMAN_PI_AUTHORIZE_V6_PREPARATION_EXECUTION"),
        ("owner", "AGENT"),
        ("scope", "PREPARATION_EXECUTION"),
        ("HUMAN_PI_ACCEPTED", "NO"),
    ]:
        reject(
            "planning_authority_" + field.lower() + "_drift",
            lambda f, field=field, value=value: f["authority"].update({field: value}),
        )
    reject(
        "authority_hash_mismatch",
        lambda f: f["event"]["authority_reference"].update(sha256="0" * 64),
        signed=True,
    )
    reject("successor_count_mismatch", lambda f: f["successor"].update(event_count=3))
    reject(
        "successor_chain_prior_entry_mismatch",
        lambda f: f["successor"]["event_chain"][0].update(sha256="0" * 64),
    )
    reject(
        "successor_head_mismatch", lambda f: f["successor"]["event_head"].update(event_id="0" * 64)
    )
    reject(
        "successor_runtime_authority_semantic_drift",
        lambda f: f["successor"].update(runtime_authority=False),
    )
    reject(
        "successor_authoritative_surface_drift",
        lambda f: f["successor"].update(authoritative_current_surfaces=[SUCCESSOR]),
    )
    reject(
        "candidate_marked_runtime_effective",
        lambda f: f["envelope"].update(RUNTIME_EFFECTIVE="YES"),
    )
    reject(
        "candidate_current_registration", lambda f: f["envelope"].update(CURRENT_REGISTRATION="YES")
    )
    reject("candidate_as_current", as_current=True)
    return probes


def audit():
    f = load_fixture()
    protected = preservation(f["entry"])
    current, result, identities = validate_fixture(f)
    checks = []

    def check(name, condition):
        v.require(condition, name)
        checks.append({"check": name, "status": "PASS"})

    check(
        "entry_and_live_ref_observation_bound",
        f["entry"]["head"] == f["entry"]["live_origin_main"] == HEAD,
    )
    check(
        "exact_accepted_plan_manifest_and_lifecycle_closure",
        v.sha(f["plan_raw"]) == PLAN_SHA and v.sha(f["closure_raw"]) == CLOSURE_SHA,
    )
    check(
        "accepted_plan_lifecycle_and_commit_envelope",
        validate_plan_commit(a.closure(f["closure_raw"])),
    )
    check("historical_event_1_and_installed_projection_replay", historical_replay(current))
    check(
        "exact_adjacent_lifecycle_edge_and_gate",
        f["event"]["from_state"] == FROM
        and f["event"]["to_state"] == TO
        and f["event"]["gate"] == GATE,
    )
    check(
        "event_sequence_2_and_exact_previous_head",
        f["event"]["sequence"] == 2
        and f["event"]["previous_event_identity"] == current["event_head"],
    )
    check(
        "exact_previous_descriptor_and_prior_projection_hash",
        f["event"]["previous_descriptor_sha256"] == CURRENT_SHA
        and f["event"]["prior_projection_sha256"] == current["projection_sha256"],
    )
    check(
        "frozen_deterministic_event_core_id",
        identities["event_id"]
        == v.digest({k: value for k, value in f["event"].items() if k != "event_id"}),
    )
    check("distinct_event_core_payload_and_file_hashes", len(set(identities.values())) == 3)
    check(
        "exact_event_successor_and_result_projection_replay",
        f["successor"]["projection"] == result
        and f["successor"]["projection_sha256"] == v.digest(result),
    )
    phases = current["projection"]["phase_authorizations"]
    changed = [k for k in phases if phases[k] != result["phase_authorizations"][k]]
    check(
        "exactly_one_phase_change_planning_no_to_yes",
        changed == ["PREPARATION_PLANNING"]
        and phases[changed[0]] == "NO"
        and result["phase_authorizations"][changed[0]] == "YES",
    )
    check(
        "preparation_authorized_lifecycle_remains_no",
        result["lifecycle"]["PREPARATION_AUTHORIZED"] == "NO",
    )
    check(
        "preparation_execution_remains_no",
        result["phase_authorizations"]["PREPARATION_EXECUTION"] == "NO",
    )
    check(
        "source_acquisition_remains_no",
        result["phase_authorizations"]["SOURCE_ACQUISITION"] == "NO",
    )
    check(
        "image_oracle_allocation_repair_authority_remains_no",
        all(
            result["phase_authorizations"][k] == "NO"
            for k in (
                "IMAGE_BUILD",
                "ORACLE_EXECUTION",
                "PILOT_FINAL_ALLOCATION",
                "DOWNSTREAM_REPAIR_EXECUTION",
            )
        ),
    )
    cases = result["case_states"]
    check(
        "all_433_case_states_and_order_unchanged",
        len(cases) == 433 and cases == current["projection"]["case_states"],
    )
    check("attempt_consumed_count_0", sum(p["attempt_consumed"] for p in cases) == 0)
    check("all_cases_not_started", all(p["phase"] == "NOT_STARTED" for p in cases))
    check("environment_ready_established_0", all(p["environment_identity"] is None for p in cases))
    check(
        "oracle_plan_and_slot_outcomes_0",
        all(p["oracle_plan_reference"] is None and p["slot_accounting"] == [] for p in cases),
    )
    check(
        "matplotlib_1_and_8_blockers_unresolved_and_byte_preserved",
        validate_plan(f["plan_raw"], f["closure_raw"], current)[0]["counts"][
            "SETUP_REPRESENTATION_BLOCKED"
        ]
        == 1,
    )
    check(
        "exact_two_projection_paths_only",
        f["delta"] == projection_delta(current["projection"], result),
    )
    check(
        "successor_appends_only_event_2",
        f["successor"]["event_count"] == 2
        and f["successor"]["event_chain"][:-1] == current["event_chain"],
    )
    preserved_fields = set(current) - {
        "event_count",
        "event_head",
        "event_chain",
        "projection",
        "projection_sha256",
        "lifecycle_label",
    }
    check(
        "frozen_descriptor_authority_and_policy_fields_preserved",
        all(f["successor"][k] == current[k] for k in preserved_fields),
    )
    check(
        "candidate_outside_canonical_and_non_effective",
        SUCCESSOR != CURRENT and f["envelope"]["RUNTIME_EFFECTIVE"] == "NO",
    )
    check(
        "no_new_descriptor_id_or_acceptance_pin_invented",
        f["successor"]["effective_current_descriptor_identity"]
        == current["effective_current_descriptor_identity"],
    )
    probes = rejection_matrix(f)
    check(
        "all_requested_rejection_probes_reject", all(p["status"] == "PASS_REJECTED" for p in probes)
    )
    after = preservation(f["entry"])
    check(
        "canonical_and_593_tracked_files_unchanged_after_all_probes",
        after == protected and after["canonical_sha256"] == CURRENT_SHA,
    )
    return {
        "status": "PASS",
        "positive_check_count": len(checks),
        "rejection_probe_count": len(probes),
        "failed_checks": 0,
        "positive_checks": checks,
        "rejection_probes": probes,
        "event_identities": identities,
        "successor_descriptor_sha256": v.sha(f["successor_raw"]),
        "prior_projection_sha256": current["projection_sha256"],
        "result_projection_sha256": v.digest(result),
        "case_states_canonical_sha256_before_and_after": v.digest(cases),
        "preservation": after,
        "qualification": "Candidate transaction replay only; no runtime consumer, installer, subject test or scientific validation",
    }


def readonly_guard(event, args):
    if event == "open":
        _, mode, flags = args
        if (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
            isinstance(flags, int)
            and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
        ):
            raise RuntimeError("read-only audit forbids filesystem writes")
    if event == "subprocess.Popen":
        argv = args[1]
        allowed = {"rev-parse", "diff", "ls-files", "show", "log", "diff-tree"}
        branch_read = argv == ["git", "branch", "--show-current"]
        if (
            not isinstance(argv, (list, tuple))
            or len(argv) < 2
            or argv[0] != "git"
            or (argv[1] not in allowed and not branch_read)
        ):
            raise RuntimeError("read-only audit forbids non-local-Git execution")
    if event in {
        "os.system",
        "os.posix_spawn",
        "os.remove",
        "os.rename",
        "os.mkdir",
        "os.rmdir",
        "os.chmod",
        "os.link",
        "os.symlink",
        "os.truncate",
        "socket.connect",
        "socket.getaddrinfo",
    }:
        raise RuntimeError("read-only audit forbids mutation/network: " + event)


if __name__ == "__main__":
    sys.addaudithook(readonly_guard)
    result = audit()
    recorded = E / "validation_results.json"
    if recorded.exists():
        v.require(
            recorded.read_bytes() == pretty(result),
            "stored validation evidence differs from fresh audit",
        )
    print(
        json.dumps(
            {
                k: result[k]
                for k in (
                    "status",
                    "positive_check_count",
                    "rejection_probe_count",
                    "failed_checks",
                    "event_identities",
                    "successor_descriptor_sha256",
                )
            },
            sort_keys=True,
        )
    )

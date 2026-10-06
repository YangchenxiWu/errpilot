"""Read-only package audit; construction and every rejection probe stay bounded.

Frozen V1 schemas and accepted transition replay are reused without changes.
This adapter checks the Human-PI's three-leaf effectivity binding; it neither
installs nor asserts candidate runtime effectivity. All mutations are in memory.
"""

import copy
import importlib.util
import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True
E = Path(__file__).resolve().parent
ROOT = E.parents[3]
B = "evaluation/downstream_benchmark/"
PREFIX = str(E.relative_to(ROOT)) + "/"
HEAD = "995dce6f64cebd77e6a28e4aef83e6c35374c7a5"
LIVE = "ee7ff4672441ddbcfba6dfaca4ed69973331e85d"
CURRENT = B + "v6_current_state.json"
CURRENT_SHA = "9295430e8573474b17bc79339c92f46044e443b9dabfe81280f9fb789d751073"
SOURCE = B + "evidence/v6_preparation_planning_transition_v1/successor_descriptor_candidate.json"
SOURCE_SHA = "1ad034c7b49dd243d3e47563fceb53c91da75b9bd1515f2e6a8846cd21396644"
CLOSURE = B + "V6_PREPARATION_PLANNING_TRANSITION_LIFECYCLE_CLOSURE_V1.md"
CLOSURE_SHA = "7a5c6eaa3a54cca26bc040f502044a6784021e23fb75eb3e8b2a253a793cc750"
AUTHORITY = B + "V6_PREPARATION_PLANNING_INSTALLATION_AUTHORITY_V1.json"
DESCRIPTOR = PREFIX + "effective_descriptor_candidate.json"
PIN = B + "V6_PREPARATION_PLANNING_EFFECTIVE_DESCRIPTOR_ACCEPTANCE_PIN_V1.json"
DESCRIPTOR_ID = "V6_EFFECTIVE_CURRENT_DESCRIPTOR_PREPARATION_PLANNING_AUTHORIZED_V1"
EXPECTED_AUTHORITY = {
    "path": AUTHORITY,
    "owner": "HUMAN_PI",
    "operation": "COMPARE_AND_INSTALL_EXACT_ACCEPTED_SUCCESSOR_AT_CANONICAL_PATH",
    "canonical_path": CURRENT,
    "expected_predecessor_sha256": CURRENT_SHA,
    "scope": "EXACT_PREPARATION_PLANNING_TRANSITION_INSTALLATION_ONLY",
    "HUMAN_PI_ACCEPTED": "YES",
}
DECISION = {
    "gate": "HUMAN_PI_DECIDE_V6_PREPARATION_PLANNING_EFFECTIVITY_BINDING",
    "DECISION": "ADOPT_V6_PREPARATION_PLANNING_EFFECTIVITY_BINDING_V1",
    "E1_INSTALLATION_AUTHORITY": "SEPARATE_EXACT_COMPARE_AND_INSTALL_AUTHORITY",
    "E2_DESCRIPTOR_ID": DESCRIPTOR_ID,
    "E3_EFFECTIVITY_REBINDING": "CHANGE_ONLY_EFFECTIVE_CURRENT_DESCRIPTOR_IDENTITY",
    "E4_ACCEPTANCE_PIN": "INDEPENDENT_EXACT_CANONICAL_PATH_AND_FINAL_DESCRIPTOR_SHA256_PIN",
    "E5_EVENT_SEMANTICS": "PRESERVE_EVENT_2_EXACTLY_NO_NEW_EVENT",
    "E6_HASH_GRAPH": "AUTHORITY_TO_DESCRIPTOR_TO_PIN_ACYCLIC",
    "E7_CANONICAL_INSTALLATION": "SEPARATE_LATER_HUMAN_PI_TRANSACTION",
    "transaction": "OPEN_V6_PREPARATION_PLANNING_EFFECTIVITY_BINDING_CONSTRUCTION",
}
EDGES = [["authority", "descriptor"], ["descriptor", "pin"]]
FILES = {
    AUTHORITY,
    DESCRIPTOR,
    PIN,
    *(
        PREFIX + name
        for name in (
            "entry_verification.json",
            "validation_results.json",
            "artifact_sha256.json",
            "RUN_REPORT.md",
            "validate_binding.py",
        )
    ),
}
FIREWALL = dict.fromkeys(
    (
        "CANONICAL_CURRENT_STATE_MODIFIED",
        "INSTALLATION_EXECUTED",
        "EVENT_2_MODIFIED",
        "NEW_EVENT_CREATED",
        "PREPARATION_PLANNING_CANONICAL_EFFECTIVE",
        "PREPARATION_EXECUTION_AUTHORIZED",
        "PREPARATION_EXECUTED",
        "SOURCE_ACQUISITION_AUTHORIZED",
        "MATERIALIZATION_AUTHORIZED",
        "IMAGE_BUILD_AUTHORIZED",
        "ORACLE_AUTHORIZED",
        "ALLOCATION_AUTHORIZED",
        "GIT_STAGE",
        "GIT_COMMIT",
        "GIT_PUSH",
    ),
    "NO",
)

spec = importlib.util.spec_from_file_location(
    "accepted_transition_for_binding",
    ROOT / B / "evidence/v6_preparation_planning_transition_v1/validate_transition.py",
)
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)
v = t.v
pretty = t.pretty


def tracked_inventory():
    tracked = {}
    for line in t.git("ls-files", "--stage", "-z").split(b"\0"):
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
            "sha256": v.sha(raw),
        }
    return tracked


def preservation(entry):
    v.require(t.git("rev-parse", "HEAD").decode().strip() == HEAD, "HEAD drift")
    v.require(t.git("branch", "--show-current").decode().strip() == "main", "branch drift")
    v.require(t.git("diff", "--name-only") == b"", "tracked worktree changed")
    v.require(t.git("diff", "--cached", "--name-only") == b"", "index changed")
    tracked = tracked_inventory()
    v.require(tracked == entry["tracked_files"], "preexisting tracked bytes/index drift")
    v.require(v.digest(tracked) == entry["tracked_inventory_sha256"], "entry inventory drift")
    index = ROOT / t.git("rev-parse", "--git-path", "index").decode().strip()
    v.require(v.sha(index.read_bytes()) == entry["index_file_sha256"], "index bytes drift")
    untracked = {
        p.decode()
        for p in t.git("ls-files", "--others", "--exclude-standard", "-z").split(b"\0")
        if p
    }
    v.require(untracked <= FILES, "unexpected new path")
    v.require({str(p.relative_to(ROOT)) for p in E.iterdir()} <= FILES, "unexpected evidence path")
    for path, digest in entry["required_hashes"].items():
        v.require(v.sha((ROOT / path).read_bytes()) == digest, "protected bytes drift: " + path)
    return {
        "tracked_files_byte_and_index_identical": len(tracked),
        "canonical_sha256": v.sha((ROOT / CURRENT).read_bytes()),
        "tracked_worktree_diff": "EMPTY",
        "index_diff": "EMPTY",
        "index_bytes_identical": True,
        "HEAD_unchanged": True,
        "only_authorized_new_paths": True,
    }


def leaf_delta(before, after, path=""):
    if type(before) is not type(after):
        return [{"path": path, "before": before, "after": after}]
    if isinstance(before, dict):
        v.require(set(before) == set(after), "descriptor field added/removed: " + path)
        return [
            d
            for k in sorted(before)
            for d in leaf_delta(before[k], after[k], (path + "." if path else "") + k)
        ]
    if isinstance(before, list):
        v.require(len(before) == len(after), "descriptor array length changed: " + path)
        return [
            d
            for i, (a, b) in enumerate(zip(before, after))
            for d in leaf_delta(a, b, path + "[" + str(i) + "]")
        ]
    return [] if before == after else [{"path": path, "before": before, "after": after}]


def bound_descriptor(source, authority_raw):
    result = copy.deepcopy(source)
    result["effective_current_descriptor_identity"] = {
        "descriptor_id": DESCRIPTOR_ID,
        "human_pi_transition": {"path": AUTHORITY, "sha256": v.sha(authority_raw)},
    }
    return result


def hash_graph(authority_raw, descriptor_raw, pin_raw):
    raws = {"authority": authority_raw, "descriptor": descriptor_raw, "pin": pin_raw}
    hashes = {key: v.sha(raw) for key, raw in raws.items()}
    for name, raw in raws.items():
        v.require(hashes[name].encode() not in raw, name + " self hash")
    v.require(hashes["descriptor"].encode() not in authority_raw, "backward descriptor hash")
    v.require(hashes["pin"].encode() not in authority_raw, "backward pin hash in authority")
    v.require(hashes["pin"].encode() not in descriptor_raw, "pin hash in descriptor")
    v.require(PIN.encode() not in descriptor_raw, "pin reference in descriptor")
    edges = [
        [upstream, downstream]
        for upstream, digest in hashes.items()
        for downstream, raw in raws.items()
        if upstream != downstream and digest.encode() in raw
    ]
    v.acyclic(edges)
    v.require(sorted(edges) == sorted(EDGES), "incorrect actual hash dependency graph")
    return {"edges": edges, "NO_HASH_CYCLE": "YES"}


def validate_bundle(f, authority_raw, descriptor_raw, pin_raw):
    current, projection, identities = t.validate_fixture(f)
    v.require(v.sha(f["current_raw"]) == CURRENT_SHA, "wrong canonical predecessor")
    v.require(v.sha(f["successor_raw"]) == SOURCE_SHA, "accepted successor bytes drift")
    v.require(
        identities
        == {
            "event_id": "007ac4316ab6961c628ddef19202d73a0fd3859db2de30b56f27efd2cae6121c",
            "event_sha256": "27a9778775635db017a5b783c698c86b30f0c49199f6ad96fb5bc4bcfd01b84a",
            "file_sha256": "b62c5d7b0a256fff1321944364816d67fd9bcb7ae1b7947964662b1fc124af6b",
        },
        "accepted event #2 identity drift",
    )
    authority = v.loads(authority_raw)
    v.require(authority == EXPECTED_AUTHORITY, "exact seven-field installation authority required")
    v.require(authority_raw == v.canonical(authority), "authority stored/canonical byte mismatch")
    descriptor = v.loads(descriptor_raw)
    v.schema("V6_CAPACITY_CURRENT_STATE_V1", descriptor)
    source = f["successor"]
    v.require(f["successor_raw"] == pretty(source), "source serialization convention drift")
    expected = bound_descriptor(source, authority_raw)
    delta = leaf_delta(source, descriptor)
    expected_delta = leaf_delta(source, expected)
    v.require(
        len(delta) == 3 and delta == expected_delta, "not exactly three authorized leaf changes"
    )
    v.require(descriptor_raw == pretty(expected), "exact final descriptor bytes required")
    v.require(descriptor["projection"] == projection, "descriptor projection replay mismatch")
    v.require(descriptor["projection_sha256"] == v.digest(projection), "projection hash mismatch")
    v.require(descriptor["event_chain"] == source["event_chain"], "event chain drift")
    v.require(
        descriptor["event_head"] == source["event_head"] and descriptor["event_count"] == 2,
        "event #2 head/count drift",
    )
    pin = v.loads(pin_raw)
    v.require(
        pin == {"path": CURRENT, "sha256": v.sha(descriptor_raw), "HUMAN_PI_ACCEPTED": "YES"},
        "independent exact canonical-path/final-descriptor pin required",
    )
    v.require(pin_raw == v.canonical(pin), "pin stored/canonical byte mismatch")
    graph = hash_graph(authority_raw, descriptor_raw, pin_raw)
    return current, descriptor, identities, delta, graph


def rejection_probes(fixture, authority_raw, descriptor_raw, pin_raw):
    probes = []

    def reject(name, mutate, layer="exact package validation"):
        f = copy.deepcopy(fixture)
        objects = {
            "authority": v.loads(authority_raw),
            "descriptor": v.loads(descriptor_raw),
            "pin": v.loads(pin_raw),
        }
        mutate(f, objects)
        try:
            validate_bundle(
                f,
                v.canonical(objects["authority"]),
                pretty(objects["descriptor"]),
                v.canonical(objects["pin"]),
            )
        except ValueError as exc:
            probes.append(
                {
                    "probe": name,
                    "status": "PASS_REJECTED",
                    "reason": str(exc),
                    "layer": layer,
                    "fixture": "IN_MEMORY_ONLY",
                }
            )
        else:
            raise ValueError("probe accepted unexpectedly: " + name)

    def change(kind, path, value):
        def mutate(f, objects):
            obj = objects[kind]
            for key in path[:-1]:
                obj = obj[key]
            obj[path[-1]] = value

        return mutate

    identity = ["effective_current_descriptor_identity"]
    transition = identity + ["human_pi_transition"]
    reject("wrong_predecessor", lambda f, o: f.update(current_raw=f["current_raw"] + b"\n"))
    reject(
        "wrong_authority_predecessor",
        change("authority", ["expected_predecessor_sha256"], "0" * 64),
    )
    reject("wrong_authority_scope", change("authority", ["scope"], "PREPARATION_EXECUTION"))
    reject("wrong_descriptor_ID", change("descriptor", identity + ["descriptor_id"], "WRONG"))
    reject(
        "stale_membership_authority_reference",
        change(
            "descriptor",
            transition + ["path"],
            B + "V6_CENSUS_MEMBERSHIP_INSTALLATION_AUTHORITY_V1.json",
        ),
    )
    reject("wrong_authority_SHA", change("descriptor", transition + ["sha256"], "0" * 64))
    reject(
        "fourth_unauthorized_descriptor_change", change("descriptor", ["runtime_authority"], False)
    )

    def event_mutation(f, objects):
        f["event"]["gate"] = "HUMAN_PI_AUTHORIZE_V6_PREPARATION_EXECUTION"
        t.resign(f)  # Rehash dependencies to reach the frozen semantic gate check.

    reject("event_2_mutation_rehashed", event_mutation, "frozen transition semantic validation")
    reject(
        "projection_mutation", change("descriptor", ["projection", "state"], "PREPARATION_COMPLETE")
    )
    reject(
        "execution_authority_leakage",
        change(
            "descriptor", ["projection", "phase_authorizations", "PREPARATION_EXECUTION"], "YES"
        ),
    )

    def rescue(f, objects):
        plan = v.loads(f["plan_raw"])
        for case in plan["plans"]:
            if case["case_id"] == "matplotlib::1":
                case.update(planning_disposition="PREPARATION_PLAN_CONSTRUCTIBLE", blockers=[])
        f["plan_raw"] = pretty(plan)

    reject("blocker_rescue", rescue, "accepted plan hash and frozen blocker validation")
    reject(
        "case_state_blocker_rescue",
        change("descriptor", ["projection", "case_states", 66, "eligible"], True),
    )
    reject("pin_points_to_old_successor_SHA", change("pin", ["sha256"], SOURCE_SHA))
    reject("pin_wrong_canonical_path", change("pin", ["path"], DESCRIPTOR))
    reject(
        "authority_contains_backward_descriptor_hash",
        change("authority", ["descriptor_sha256"], v.sha(descriptor_raw)),
    )
    reject("descriptor_contains_pin_hash", change("descriptor", ["pin_sha256"], v.sha(pin_raw)))
    reject(
        "descriptor_contains_self_hash",
        change("descriptor", ["self_sha256"], v.sha(descriptor_raw)),
    )
    reject(
        "accepted_successor_byte_drift",
        lambda f, o: f.update(successor_raw=f["successor_raw"] + b"\n"),
    )
    try:
        v.acyclic(EDGES + [["pin", "authority"]])
    except ValueError as exc:
        probes.append(
            {
                "probe": "hash_cycle",
                "status": "PASS_REJECTED",
                "reason": str(exc),
                "layer": "unchanged frozen acyclic graph check",
                "fixture": "IN_MEMORY_DEPENDENCY_EDGE_ONLY_NO_HASH_FIXED_POINT",
            }
        )
    else:
        raise ValueError("hash cycle accepted unexpectedly")
    return probes


def audit():
    entry = v.loads((E / "entry_verification.json").read_bytes())
    v.require(
        entry["status"] == "ENTRY_GATE_PASS" and entry["human_pi_decision"] == DECISION,
        "entry decision drift",
    )
    v.require(
        entry["head"] == HEAD
        and entry["live_origin_main"] == LIVE
        and entry["worktree_clean_before_write"]
        and entry["index_clean_before_write"],
        "entry prerequisite drift",
    )
    protected = preservation(entry)
    v.require(v.sha((ROOT / CLOSURE).read_bytes()) == CLOSURE_SHA, "accepted closure drift")
    closure = t.a.closure((ROOT / CLOSURE).read_bytes())
    v.require(
        t.git("rev-parse", "HEAD^").decode().strip() == LIVE, "transition commit parent drift"
    )
    v.require(
        t.git("log", "-1", "--format=%s").decode().strip()
        == closure["commit_scope"]["required_message"],
        "transition commit message drift",
    )
    v.require(
        set(t.git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").decode().splitlines())
        == set(closure["commit_scope"]["paths"]),
        "transition commit scope drift",
    )
    for path, digest in closure["accepted_paths_sha256"].items():
        v.require(
            v.sha((ROOT / path).read_bytes()) == v.sha(t.git("show", "HEAD:" + path)) == digest,
            "accepted transition input/commit drift: " + path,
        )
    f = t.load_fixture()
    authority_raw = (ROOT / AUTHORITY).read_bytes()
    descriptor_raw = (ROOT / DESCRIPTOR).read_bytes()
    pin_raw = (ROOT / PIN).read_bytes()
    current, descriptor, identities, delta, graph = validate_bundle(
        f, authority_raw, descriptor_raw, pin_raw
    )
    v.require(t.historical_replay(current), "historical event #1 replay")
    phases = descriptor["projection"]["phase_authorizations"]
    cases = descriptor["projection"]["case_states"]
    conditions = {
        "canonical_predecessor_unchanged": v.sha(f["current_raw"]) == CURRENT_SHA,
        "accepted_event_2_unchanged_byte_for_byte": identities["file_sha256"]
        == entry["accepted_event_identities"]["file_sha256"],
        "accepted_successor_source_unchanged": v.sha(f["successor_raw"]) == SOURCE_SHA,
        "installation_authority_matches_exact_Human_PI_decision": v.loads(authority_raw)
        == EXPECTED_AUTHORITY,
        "exactly_three_authorized_leaf_changes": len(delta) == 3,
        "descriptor_ID_exact": descriptor["effective_current_descriptor_identity"]["descriptor_id"]
        == DESCRIPTOR_ID,
        "human_pi_transition_path_exact": descriptor["effective_current_descriptor_identity"][
            "human_pi_transition"
        ]["path"]
        == AUTHORITY,
        "human_pi_transition_SHA_equals_authority_SHA": descriptor[
            "effective_current_descriptor_identity"
        ]["human_pi_transition"]["sha256"]
        == v.sha(authority_raw),
        "event_chain_replay_PASS": descriptor["event_chain"] == f["successor"]["event_chain"],
        "frozen_current_state_schema_PASS": descriptor["schema"] == "V6_CAPACITY_CURRENT_STATE_V1",
        "all_433_case_states_and_order_unchanged": len(cases) == 433
        and cases == current["projection"]["case_states"],
        "PREPARATION_PLANNING_YES": phases["PREPARATION_PLANNING"] == "YES",
        "PREPARATION_EXECUTION_NO": phases["PREPARATION_EXECUTION"] == "NO",
        "PREPARATION_AUTHORIZED_NO": descriptor["projection"]["lifecycle"]["PREPARATION_AUTHORIZED"]
        == "NO",
        "SOURCE_ACQUISITION_NO": phases["SOURCE_ACQUISITION"] == "NO",
        "environment_ready_established_0": all(c["environment_identity"] is None for c in cases),
        "acceptance_pin_path_exact": v.loads(pin_raw)["path"] == CURRENT,
        "acceptance_pin_SHA_equals_final_descriptor_SHA": v.loads(pin_raw)["sha256"]
        == v.sha(descriptor_raw),
        "membership_installation_authority_and_pin_untouched": all(
            v.sha((ROOT / p).read_bytes()) == entry["required_hashes"][p]
            for p in (
                B + "V6_CENSUS_MEMBERSHIP_INSTALLATION_AUTHORITY_V1.json",
                B + "V6_EFFECTIVE_CURRENT_DESCRIPTOR_ACCEPTANCE_PIN_V1.json",
            )
        ),
        "no_canonical_replacement": (ROOT / CURRENT).read_bytes() == f["current_raw"]
        and DESCRIPTOR != CURRENT,
        "other_execution_authorizations_NO": all(
            phases[k] == "NO"
            for k in (
                "IMAGE_BUILD",
                "ORACLE_EXECUTION",
                "PILOT_FINAL_ALLOCATION",
                "DOWNSTREAM_REPAIR_EXECUTION",
            )
        ),
        "runtime_authority_and_single_current_surface_preserved": descriptor["runtime_authority"]
        is True
        and descriptor["authoritative_current_surfaces"] == [CURRENT],
        "all_attempts_and_outcomes_unchanged_and_empty": all(
            c["phase"] == "NOT_STARTED"
            and not c["attempt_consumed"]
            and c["slot_accounting"] == []
            and c["oracle_plan_reference"] is None
            for c in cases
        ),
        "both_matplotlib_blockers_preserved": t.validate_plan(
            f["plan_raw"], f["closure_raw"], current
        )[0]["counts"]["PLAN_CONSTRUCTIBLE"]
        == 431,
        "NO_HASH_CYCLE": graph["NO_HASH_CYCLE"] == "YES",
        "authority_and_pin_stored_canonical_hashes_equal": v.sha(authority_raw)
        == v.digest(v.loads(authority_raw))
        and v.sha(pin_raw) == v.digest(v.loads(pin_raw)),
    }
    for name, condition in conditions.items():
        v.require(condition, name)
    probes = rejection_probes(f, authority_raw, descriptor_raw, pin_raw)
    legacy_probes = t.rejection_matrix(f)
    v.require(
        all(p["status"] == "PASS_REJECTED" for p in probes + legacy_probes), "rejection failure"
    )
    after = preservation(entry)
    v.require(after == protected, "mutation during audit")
    return {
        "status": "PASS",
        "positive_check_count": len(conditions),
        "failed_checks": 0,
        "positive_checks": [{"check": k, "status": "PASS"} for k in conditions],
        "binding_rejection_probe_count": len(probes),
        "binding_rejection_probes": probes,
        "frozen_transition_rejection_probe_count": len(legacy_probes),
        "frozen_transition_rejection_probes": legacy_probes,
        "rejection_probe_count": len(probes) + len(legacy_probes),
        "event_identities": identities,
        "exact_authorized_delta": delta,
        "installation_authority": {
            "path": AUTHORITY,
            "sha256": v.sha(authority_raw),
            "canonical_sha256": v.digest(v.loads(authority_raw)),
        },
        "effectivity_bound_descriptor": {
            "path": DESCRIPTOR,
            "sha256": v.sha(descriptor_raw),
            "descriptor_id": DESCRIPTOR_ID,
        },
        "independent_acceptance_pin": {
            "path": PIN,
            "sha256": v.sha(pin_raw),
            "canonical_sha256": v.digest(v.loads(pin_raw)),
        },
        "hash_graph": graph,
        "event_chain_replay": "PASS",
        "frozen_current_state_schema": "PASS",
        "case_states_canonical_sha256_before_and_after": v.digest(cases),
        "members": len(cases),
        "projects": len({c["source_project"] for c in cases}),
        "environment_ready_established": 0,
        "preservation": after,
        "firewall": FIREWALL,
        "qualification": "Bounded package replay/schema/binding audit only; no installer, runtime consumer, subject test or scientific validation",
        "next_gate": "HUMAN_PI_REVIEW_OF_V6_PREPARATION_PLANNING_EFFECTIVITY_BINDING_PACKAGE",
    }


if __name__ == "__main__":
    sys.addaudithook(t.readonly_guard)
    result = audit()
    recorded = E / "validation_results.json"
    if recorded.exists():
        v.require(
            recorded.read_bytes() == pretty(result), "fresh audit differs from stored evidence"
        )
    print(
        json.dumps(
            {
                k: result[k]
                for k in (
                    "status",
                    "positive_check_count",
                    "binding_rejection_probe_count",
                    "frozen_transition_rejection_probe_count",
                    "rejection_probe_count",
                    "failed_checks",
                    "installation_authority",
                    "effectivity_bound_descriptor",
                    "independent_acceptance_pin",
                    "hash_graph",
                    "preservation",
                )
            },
            sort_keys=True,
        )
    )

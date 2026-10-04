"""Read-only evidence of a blocked V6 first-activation transition.

This is a transaction-scoped diagnostic, not a state writer or runtime consumer.
All event-shaped objects below are synthetic in-memory probes. No activation
event, post-state candidate, current selector, or Human-PI authority is emitted.
"""

import copy
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

E = Path(__file__).resolve().parent
B = E.parents[1]
ROOT = B.parents[1]
BASELINE = "d5146d86fc2b36b336d1bdf2657a6cbdfde84f8c"
CLOSURE_HASH = "977ee418f4ac3d84cf66af5943beea75fab3e38ba8c086211f22312c9bd46ac9"
INVENTORY_HASH = "2df23ae13f19055d5998ad84d9eebed16251b551c695ba68bae3d1eb1c5397cf"


def module_at(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    v = module_at(
        "immutable_v6_contract_audit",
        B / "evidence/v6_successor_contract_construction_v1/validate_contract.py",
    )
    t = module_at(
        "immutable_v6_contract_tests",
        B / "evidence/v6_successor_contract_construction_v1/test_contract.py",
    )
    checks = []

    def check(name, condition):
        v.require(condition, name)
        checks.append({"check": name, "status": "PASS"})

    check(
        "exact_main_baseline_and_empty_tracked_diff_index",
        git("branch", "--show-current") == "main"
        and git("rev-parse", "HEAD") == BASELINE
        and git("rev-parse", "refs/remotes/origin/main") == BASELINE
        and not git("diff", "--name-only", "HEAD")
        and not git("diff", "--cached", "--name-only"),
    )
    closure_path = B / "V6_SUCCESSOR_CONTRACT_LIFECYCLE_CLOSURE_V1.md"
    check("accepted_closure_digest", sha(closure_path) == CLOSURE_HASH)
    closure = json.loads(
        re.search(r"```CLOSURE_JSON\n(.*?)\n```", closure_path.read_text(), re.S)[1]
    )
    bindings = closure["historical_inputs_sha256"] | closure["accepted_contract_paths_sha256"]
    bindings[str(closure_path.relative_to(ROOT))] = CLOSURE_HASH
    check(
        "all_42_closure_artifact_bytes_equal_HEAD",
        len(bindings) == 42
        and all(
            sha(ROOT / path) == digest
            and hashlib.sha256(
                subprocess.check_output(["git", "show", f"HEAD:{path}"], cwd=ROOT)
            ).hexdigest()
            == digest
            for path, digest in bindings.items()
        ),
    )
    check(
        "exact_enclosing_commit_parent_message_and_scope",
        git("rev-parse", "HEAD^") == closure["parent_head"]
        and git("log", "-1", "--format=%s") == closure["commit_envelope"]["message"]
        and set(git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").splitlines())
        == set(bindings),
    )
    check(
        "accepted_construction_inventory_seal",
        sha(B / "evidence/v6_successor_contract_construction_v1/artifact_sha256.json")
        == INVENTORY_HASH,
    )
    original = v.load(B / "evidence/v6_protocol_design_v1/predecessor_artifact_sha256.json")
    check(
        "all_201_predecessor_artifact_hashes",
        len(original["artifacts"]) == 201
        and all(
            Path(path).is_file() and sha(Path(path)) == item["sha256"]
            for path, item in original["artifacts"].items()
        ),
    )
    data = v.bundle()
    v.validate_bundle(data)
    check("unchanged_committed_bundle_semantics", True)
    for name in v.SCHEMA_NAMES:
        schema = v.load(v.S / (name + ".schema.json"))
        v.Draft202012Validator.check_schema(schema)
        check("schema_meta_and_identity:" + name, schema["$id"].endswith(":" + name))
    v.static_files(bindings)
    check("all_42_committed_UTF8_JSON_Python_whitespace_checks", True)
    state = data["state"]
    current = state["projection"]
    check(
        "canonical_state_powerless_no_events_no_work_no_allocation",
        state["candidate_only"] is True
        and state["runtime_authority"] is False
        and state["event_chain"] == []
        and state["event_head"] is None
        and state["event_count"] == 0
        and current["state"] == "CONTRACT_CANDIDATE"
        and all(x == "NO" for x in current["lifecycle"].values())
        and all(x == "NO" for x in current["phase_authorizations"].values())
        and current["allocation"] == {"pilot_case_ids": [], "final_case_ids": []}
        and all(
            c["phase"] == "NOT_STARTED" and not c["attempt_consumed"] and c["slot_accounting"] == []
            for c in current["case_states"]
        ),
    )
    check(
        "exact_433_members_15_projects_numeric_rank_order",
        len(data["pool"]) == 433
        and len({r["source_project"] for r in data["pool"]}) == 15
        and [int(r["frozen_rank"]) for r in data["pool"]]
        == sorted(int(r["frozen_rank"]) for r in data["pool"]),
    )
    activation_edge = data["lifecycle"]["transitions"][5]
    check(
        "activation_edge_has_no_candidate_predecessor",
        activation_edge["from"] == "CONTRACT_PUBLISHED_WHERE_REQUIRED"
        and activation_edge["to"] == "CENSUS_MEMBERSHIP_ACTIVATED"
        and activation_edge["gate"] == "HUMAN_PI_ACTIVATE_V6_CENSUS_MEMBERSHIP"
        and activation_edge["from"] != current["state"],
    )

    initial, events, authorities, descriptors, contract = t.event_fixture(data)
    diagnostics = []

    def rejected(name, fn, expected):
        try:
            fn()
        except ValueError as error:
            v.require(expected in str(error), "unexpected diagnostic: " + str(error))
            diagnostics.append({"check": name, "status": "PASS_REJECTED", "reason": str(error)})
        else:
            raise ValueError(name + " unexpectedly accepted")

    first = copy.deepcopy(events[0])
    target = v.phase_flags_for_edge(initial, "CENSUS_MEMBERSHIP_ACTIVATED")
    authority = copy.deepcopy(next(iter(authorities.values())))
    authority["gate"] = activation_edge["gate"]
    authority_hash = v.digest(authority)
    descriptor_hash = sha(B / "v6_current_state.json")
    first.update(
        previous_descriptor_sha256=descriptor_hash,
        authority_reference={"path": authority["path"], "sha256": authority_hash},
        gate=authority["gate"],
        from_state=activation_edge["from"],
        to_state=activation_edge["to"],
        next_projection=target,
        result_projection_sha256=v.digest(target),
    )
    rejected(
        "published_from_state_with_exact_candidate_predecessor",
        lambda: v.audit_event_chain(
            initial, [first], {authority_hash: authority}, [descriptor_hash], contract
        ),
        "event predecessor projection disagreement",
    )
    direct = copy.deepcopy(first)
    direct["from_state"] = current["state"]
    rejected(
        "direct_candidate_to_activation_skips_five_contract_edges",
        lambda: v.audit_event_chain(
            initial, [direct], {authority_hash: authority}, [descriptor_hash], contract
        ),
        "unauthorized/nonadjacent lifecycle transition",
    )
    nonempty = copy.deepcopy(state)
    nonempty["event_count"] = 1
    rejected(
        "candidate_only_profile_with_one_event",
        lambda: v.validate_schema("V6_CAPACITY_CURRENT_STATE_V1", nonempty),
        "schema rejection at $.event_count",
    )
    identities = []
    for label in ["in-memory-identity-A", "in-memory-identity-B"]:
        event = copy.deepcopy(events[0])
        event["event_id"] = label
        derived, head = v.audit_event_chain(
            initial, [event], authorities, descriptors[:1], contract
        )
        v.require(derived == events[0]["next_projection"], "unexpected projection drift")
        identities.append({"event_id": label, "canonical_event_sha256": head["event_sha256"]})
    diagnostics.append(
        {
            "check": "same_transition_accepts_two_arbitrary_event_IDs",
            "status": "CONFIRMED_SEMANTIC_GAP",
            "identities": identities,
        }
    )
    unchanged, head = v.audit_event_chain(initial, [], {}, [], contract)
    check("empty_chain_retains_exact_candidate_projection", unchanged == initial and head is None)
    negative = t.rejection_matrix(data)
    check(
        "all_141_inherited_in_memory_rejections",
        len(negative) == 141 and all(r["status"] == "PASS_REJECTED" for r in negative),
    )
    result = {
        "status": "BLOCKED",
        "next_gate": "HUMAN_PI_V6_ACTIVATION_CONTRACT_SEMANTIC_ADJUDICATION",
        "activation_event_candidate_created": False,
        "post_state_candidate_created": False,
        "positive_count": len(checks),
        "positive_checks": checks,
        "blocked_transition_diagnostics": diagnostics,
        "inherited_rejection_matrix": {"passed": 141, "failed": 0, "probes": negative},
        "phase_F_G_activation_validation": "NOT_RUN_NO_CONTRACT_DERIVABLE_ACTIVATION_CANDIDATE",
        "limits": [
            "Synthetic diagnostic authorities are fixture values, never Human-PI authority.",
            "The inherited helper audits synthetic events only, not production runtime consumption.",
            "Live origin/main is verified separately; this diagnostic performs no network access.",
            "No externally unreferenced V6 storage or subject environment is inspected.",
        ],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

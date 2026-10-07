"""Pure V6 admission/once-only journal candidate, with sentinel-only routes.

This module cannot dispatch a real operation. Its ledger is a proposal and every
claim/terminal mutation is explicitly an in-memory CANDIDATE_TEST_ONLY fixture.
The future durable protocol is specified in ledger_candidate.json.
"""
from __future__ import annotations

import copy
import types
from pathlib import Path

from evaluation.downstream_benchmark.evidence.v6_preparation_execution_activation_v1 import (
    adapter_candidate as a,
)
from evaluation.downstream_benchmark.screening import materialize_expansion_block_02_batch as snapshots

TEST_NAMESPACE = "CANDIDATE_TEST_ONLY"
PERMISSIONS = ("ENVIRONMENT_MATERIALIZATION", "IMAGE_BUILD", "BUILD_NETWORK", "PERSISTENT_EVIDENCE_OUTPUT")
REQUIRED_SUCCESS_EVIDENCE = (
    "dockerfile", "build_context", "source_snapshot_or_absence", "raw_build_log",
    "image_inspection", "python_probe", "installed_distributions", "environment_identity",
)
ROUTE_POLICY = {
    "selection": "EXPLICIT_CENSUS_ORDINAL_CASE_ID_PLAN_SHA",
    "order": "ORIGINAL_FROZEN_RANK_ASCENDING_BUGGY_THEN_FIXED",
    "fallback": "NONE", "stop_at_capacity": False, "automatic_retry": False,
    "automatic_rescue": False, "governed_batches": False,
    "runtime_chunk_scientific_identity": "NONE", "runtime_chunk_membership_authority": "NONE",
    "runtime_chunk_stopping_authority": "NONE", "source_acquisition": False,
    "setup_normalization": False, "recipe_mutation": False, "oracle_execution": False,
    "execution_network": "NONE",
}


def ledger_template(population):
    return {"schema": "V6_ONCE_ONLY_LEDGER_CANDIDATE_V1", "candidate_only": True,
            "runtime_authority": False, "population_sha256": a.identity(population),
            "observation_states": ["UNSTARTED", "MATERIALIZED", "BUILD_FAILED", "BLOCKED_*", "INTERRUPTED"],
            "persistence_protocol": {
                "root": str(a.OUTPUT_ROOT),
                "writer_lock": "Exclusive O_CREAT|O_EXCL lock; existing lock blocks, no automatic reclaim",
                "lock_release": "Only the verified current owner after terminal fsync may release its writer lock; crashed locks need separate adjudication; claim and terminal files are never removed",
                "claim_path": "ledger/claims/<base_attempt_id>.json",
                "terminal_path": "ledger/terminals/<base_attempt_id>.json",
                "write_protocol": "Exclusive complete write, fsync file and parent before work; never replace a claim or terminal",
                "claim_semantics": "Durable claim consumes the base opportunity before any input staging/source export/build; claim survives crash",
                "terminal_semantics": "Exactly one terminal first-pass observation; no result overwrite; status and evidence bound by content SHA",
                "crash_reconciliation": "A prior claimed attempt with no complete terminal blocks dispatch; separate audit may append INTERRUPTED with failure evidence, never run again",
                "partial_record": "Malformed or incomplete claim/terminal blocks; preserve bytes for Human-PI adjudication",
                "retry": "Separate versioned Human-PI authority, new attempt identity and exact prior claim/terminal SHA supersession lineage; unsupported by this base controller",
                "canonical_effect": "NONE; scientific case dispositions require their separate lifecycle authority",
            },
            "entries": [{"base_attempt_id": x["base_attempt_id"], "state": "UNSTARTED",
                         "claimed": False, "attempt_consumed": False} for x in population["items"]],
            "journal": []}


def validate_journal(ledger, population):
    baseline = ledger_template(population)
    require_keys = set(baseline)
    a.require(set(ledger) == require_keys, "ledger schema fields")
    for k in require_keys - {"entries", "journal"}:
        a.require(a.canonical(ledger[k]) == a.canonical(baseline[k]), "ledger policy/population drift")
    expected = {x["base_attempt_id"]: copy.deepcopy(x) for x in baseline["entries"]}
    prior = None
    for sequence, event in enumerate(ledger["journal"], 1):
        a.require(event["namespace"] == TEST_NAMESPACE and event["sequence"] == sequence
                  and event["prior_event_sha256"] == prior, "journal lineage/order")
        body = {k: v for k, v in event.items() if k != "event_sha256"}
        a.require(a.identity(body) == event["event_sha256"], "journal event hash")
        entry = expected.get(event["base_attempt_id"])
        a.require(entry is not None, "unknown ledger attempt")
        if event["operation"] == "CLAIM":
            a.require(set(body) == {"namespace", "sequence", "prior_event_sha256", "base_attempt_id", "operation"},
                      "claim extra fields")
            a.require(not entry["claimed"] and entry["state"] == "UNSTARTED", "repeated base attempt")
            entry.update(claimed=True, attempt_consumed=True)
        elif event["operation"] == "TERMINAL":
            a.require(set(body) == {"namespace", "sequence", "prior_event_sha256", "base_attempt_id",
                                    "operation", "state", "evidence", "reason"}, "terminal extra fields")
            a.require(entry["claimed"] and entry["state"] == "UNSTARTED", "terminal overwrite/unclaimed attempt")
            status = event["state"]
            a.require(status in {"MATERIALIZED", "BUILD_FAILED", "INTERRUPTED"}
                      or (isinstance(status, str) and status.startswith("BLOCKED_") and len(status) > 8),
                      "invalid terminal observation")
            if status == "MATERIALIZED":
                a.require(set(event["evidence"]) == set(REQUIRED_SUCCESS_EVIDENCE)
                          and all(isinstance(v, str) and a.shared.HEX64.fullmatch(v)
                                  for v in event["evidence"].values()), "success evidence missing")
            else:
                a.require(isinstance(event["reason"], str) and bool(event["reason"]), "failure evidence/reason")
            entry["state"] = status
        else:
            raise a.Rejected("unknown journal operation")
        prior = event["event_sha256"]
    a.require(ledger["entries"] == list(expected.values()), "ledger observations/reordering/overwrite")


def append_test_event(ledger, population, item, *, operation, state=None, evidence=None,
                      reason="", namespace=None):
    a.require(namespace == TEST_NAMESPACE, "test-only ledger mutation")
    validate_journal(ledger, population)
    a.require(item in population["items"], "unknown/changed work item")
    result = copy.deepcopy(ledger)
    event = {"namespace": namespace, "sequence": len(result["journal"]) + 1,
             "prior_event_sha256": result["journal"][-1]["event_sha256"] if result["journal"] else None,
             "base_attempt_id": item["base_attempt_id"], "operation": operation}
    if operation == "TERMINAL":
        event.update(state=state, evidence=evidence or {}, reason=reason)
    event["event_sha256"] = a.identity(event)
    result["journal"].append(event)
    entry = next(x for x in result["entries"] if x["base_attempt_id"] == item["base_attempt_id"])
    if operation == "CLAIM":
        entry.update(claimed=True, attempt_consumed=True)
    else:
        entry["state"] = state
    validate_journal(result, population)
    return result


def validate_receipts(receipts, common_binding, *, network_required):
    """Validate exact in-memory acceptance simulations, never authorize runtime."""
    needed = set(PERMISSIONS) if network_required else set(PERMISSIONS) - {"BUILD_NETWORK"}
    a.require(isinstance(receipts, dict) and set(receipts) == needed, "missing/unknown separate authority")
    package = a.loads(Path(__file__).with_name("authority_candidates.json").read_bytes())
    a.require(package["common_binding"] == common_binding, "wrong independent authority common binding")
    for scope in needed:
        record = receipts[scope]
        a.require(record == {"namespace": TEST_NAMESPACE, "scope": scope,
                              "common_binding_sha256": a.identity(common_binding),
                              "authority_candidate_record_sha256": a.identity(package["separate_permissions"][scope]),
                              "HUMAN_PI_ACCEPTED": "YES"}, "unaccepted/wrong authority binding")


def review_route(manifest, population, item, *, receipts, common_binding, policy,
                 runtime_gates, sentinel, snapshot=None, prior_claims=()):
    a.require(a.canonical(policy) == a.canonical(ROUTE_POLICY), "forbidden execution/selection policy")
    a.require(common_binding["entry_current_descriptor"] == {"path": a.CURRENT, "sha256": a.CURRENT_SHA}
              and common_binding["accepted_manifest"] == {"path": a.MANIFEST, "sha256": a.MANIFEST_SHA}
              and common_binding["population_semantic_sha256"] == a.identity(population)
              and common_binding["proposed_v6_output_root"] == str(a.OUTPUT_ROOT), "wrong runtime common binding")
    for ref in common_binding["runtime_input_binding_implementation"].values():
        a.read_exact(ref["path"], ref["sha256"])
    a.require(item in population["items"] and population["candidate_only"] is True, "work item outside population")
    a.require(item["base_attempt_id"] not in prior_claims, "repeated base attempt")
    proposal = a.engine_call_proposal(manifest, item, snapshot=snapshot)
    validate_receipts(receipts, common_binding, network_required=proposal["network_required"])
    a.require(runtime_gates == {
        "namespace": TEST_NAMESPACE, "implementation_accepted_frozen_persisted_committed": True,
        "remote_publication_verified": True, "clean_committed_head": True,
        "exact_execution_descriptor_pin_and_full_chain": True, "source_objects_present": True,
        "base_runtime_verified_without_pull": True,
        "restricted_default_build_network_verified": proposal["network_required"],
        "persistent_output_binding_accepted": True,
    }, "missing lifecycle/publication/source/network/output gate")
    # A callable receives only an inert proposal. The real materializer/exporter
    # cannot be used as a sentinel. Tests additionally prohibit engine entry.
    a.require(isinstance(sentinel, ReviewSentinel), "non-executing review sentinel required")
    return sentinel.capture(proposal)


class ReviewSentinel:
    def __init__(self):
        self.calls = []

    def capture(self, proposal):
        self.calls.append(copy.deepcopy(proposal))
        return {"namespace": TEST_NAMESPACE, "engine_called": False,
                "source_exported": False, "attempt_consumed": False,
                "proposal_sha256": a.identity(proposal)}


def source_function_candidate(manifest, item):
    """Reuse exact shared V2 exporter code with a V6-only immutable resolver.

    Returned function is for future separately authorized integration review;
    never called in this transaction. No predecessor module/global is changed.
    There are no V6 gitlinks and no inherited Block-03 special-case permission.
    """
    plan = a.select(manifest, ordinal=item["census_order"], case_id=item["case_id"], plan_sha=item["plan_sha256"])
    a.require(item["variant"] in {"BUGGY", "FIXED"}, "source-independent export prohibited")
    a.require(item == a.work_item(plan, item["variant"]), "wrong source item/revision")
    a.require(all(not v["source_export_planning"]["tracked_gitlinks"] for v in plan["source_variants"]),
              "unsupported gitlink semantics")
    recipe = a.engine_recipe(plan)
    def resolver(given_recipe, label):
        a.require(given_recipe == recipe and label == item["variant"], "V6 source resolver drift")
        mirror = Path(item["source_mirror"])
        a.require(snapshots._run_git(mirror, "cat-file", "-t", item["source_revision_sha"]).strip()
                  == b"commit", "missing frozen V6 commit")
        return mirror, item["source_revision_sha"]
    original = snapshots.source_snapshot_identity
    bound_globals = {**original.__globals__, "_source_identity": resolver}
    return types.FunctionType(original.__code__, bound_globals, "v6_bound_shared_snapshot",
                              original.__defaults__, original.__closure__)


def real_dispatch(*args, **kwargs):
    raise a.Rejected("CANDIDATE_ONLY: real dispatch has no installed V6 authority/entrypoint")


def request_retry(*args, **kwargs):
    raise a.Rejected("retry requires separate versioned Human-PI successor authority and supersession lineage")

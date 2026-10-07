"""Read-only V6 execution-entry audit; never claims, builds, or repairs."""
from __future__ import annotations

import importlib
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator

from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a
from evaluation.downstream_benchmark.screening import v6_preparation_ledger as ledger
from evaluation.downstream_benchmark.screening import v6_preparation_runtime as runtime

HEAD = "0425059c2c2e306cd48b7739c51dc3cb3688e228"
CURRENT_SHA = "e48580c1f9769d1b93ab995e6dcef3689c6920a9ce7b83f728526e9694dc68fd"
NATIVE = "evaluation/downstream_benchmark/evidence/v6_native_buildkit_client_compatibility_bridge_v1/"
SOURCE_SHA = "c83da6f5eb355702f994c28efc6b14bc36988a9cc405ff05a689a9f97128f4b6"
CONFIG_SHA = "654299e49b0fc8833f093ecc887b4578970895ce28aa5359b4b37246f7b6190e"
ENFORCEMENT_SHA = "8801637324b2fa32124df8444e88f193a5be3f9c847904f2eebfb92197bc5c10"


def git(*args):
    result = subprocess.run(["git", *args], cwd=a.ROOT, capture_output=True, check=True)
    return result.stdout


def tracked_fingerprint():
    inventory = {}
    for raw in git("ls-files", "-z").split(b"\0"):
        if raw:
            relative = raw.decode()
            path = a.ROOT / relative
            a.require(path.is_file() and not path.is_symlink(), "tracked special path")
            inventory[relative] = {"sha256": a.sha(path.read_bytes()),
                                   "mode": path.stat().st_mode & 0o777}
    return {"count": len(inventory), "sha256": a.identity(inventory)}


def journal_observation(items):
    ids = [item["base_attempt_id"] for item in items]
    journal = ledger.Ledger(a.OUTPUT_ROOT, namespace=ledger.REAL, real_ids=ids)
    states = dict(Counter(journal.state(identity) for identity in ids))
    directory_files = {}
    for name in ("claims", "terminals", "locks"):
        root = a.OUTPUT_ROOT / "ledger" / name
        ledger.safe_path(root)
        a.require(root.is_dir(), "persistent ledger directory unavailable")
        directory_files[name] = sorted(str(p.relative_to(a.OUTPUT_ROOT)) for p in root.rglob("*"))
    a.require(states == {"UNSTARTED": 641}, "initial durable ledger differs")
    a.require(all(not paths for paths in directory_files.values()), "ledger is not empty")
    return {"total": len(ids), "unstarted": 641, "claimed": 0, "terminal": 0,
            "active_claims": 0, "orphan_or_unresolved_claims": 0,
            "retries": 0, "state_counts": states, "directory_entries": directory_files}


def main():
    started = datetime.now(timezone.utc).isoformat()
    before = tracked_fingerprint()
    a.require(git("branch", "--show-current").strip().decode() == "main", "branch drift")
    a.require(git("rev-parse", "HEAD").strip().decode() == HEAD, "HEAD drift")
    a.require(git("rev-parse", "origin/main").strip().decode() == HEAD, "local remote ref drift")
    a.require(git("diff", "--name-only") == b"", "tracked worktree dirty")
    a.require(git("diff", "--cached", "--name-only") == b"", "index dirty")
    current = a.loads(a.read_exact(a.CURRENT, CURRENT_SHA))
    Draft202012Validator(a.loads((a.B / "v6_contract_schemas/V6_CAPACITY_CURRENT_STATE_V1.schema.json").read_bytes())).validate(current)
    projection = current["projection"]
    a.require(current["event_count"] == len(current["event_chain"]) == 3, "event count")
    a.require(current["lifecycle_label"] == projection["state"] == "PREPARATION_EXECUTION_AUTHORIZED", "execution state")
    for flag in ("PREPARATION_PLANNING", "PREPARATION_EXECUTION"):
        a.require(projection["phase_authorizations"][flag] == "YES", "preparation authority")
    a.require(projection["lifecycle"]["PREPARATION_AUTHORIZED"] == "YES", "preparation lifecycle")
    for flag in ("SOURCE_ACQUISITION", "ORACLE_EXECUTION", "PILOT_FINAL_ALLOCATION", "DOWNSTREAM_REPAIR_EXECUTION"):
        a.require(projection["phase_authorizations"][flag] == "NO", "phase firewall")
    pin = runtime.read_installed(runtime.EXECUTION_PIN)
    a.require(pin == {"path": a.CURRENT, "sha256": CURRENT_SHA, "HUMAN_PI_ACCEPTED": "YES"}, "canonical pin")
    event_validator = importlib.import_module("evaluation.downstream_benchmark.evidence.v6_activation_runtime_genesis_bridge_v1.validate_bridge")
    for ref in (current["contract"], *current["event_chain"]):
        raw = a.read_exact(ref["path"], ref["sha256"])
        if "event_id" in ref:
            event = a.loads(raw)
            identities = event_validator.validate_event_identity(event, raw)
            a.require(identities["event_sha256"] == ref["event_sha256"] and identities["event_id"] == ref["event_id"], "event identity")
    _, manifest = a.load_inputs()
    population = runtime.population()
    a.require(a.identity(population) == runtime.POPULATION_SHA, "population semantic identity")
    items = population["items"]
    ids = [item["base_attempt_id"] for item in items]
    a.require(len(ids) == len(set(ids)) == 641, "population/duplicate attempts")
    variants = dict(Counter(item["variant"] for item in items))
    a.require(variants == {"BUGGY": 210, "FIXED": 210, "SOURCE_INDEPENDENT": 221}, "type counts")
    network = dict(Counter("RESTRICTED" if item["build_network_required"] else "NONE" for item in items))
    a.require(network == {"RESTRICTED": 583, "NONE": 58}, "network counts")
    for item in items:
        plan = a.select(manifest, ordinal=item["census_order"], case_id=item["case_id"], plan_sha=item["plan_sha256"])
        a.require(item == a.work_item(plan, item["variant"]), "frozen work/recipe identity")
    blockers = population["blocked"]
    a.require({b["case_id"] for b in blockers} == {"matplotlib::1", "matplotlib::8"}, "blocker identity")
    cases = [p["case_id"] for p in manifest["plans"]]
    dispatch_cases = {item["case_id"] for item in items}
    a.require(len(dispatch_cases) == 431 and len(cases) == len(set(cases)) == 433, "case census")
    a.require(set(cases) == dispatch_cases | {b["case_id"] for b in blockers}, "case coverage")
    a.require(not dispatch_cases & {b["case_id"] for b in blockers}, "blocker dispatch")
    a.require(cases == [c["case_id"] for c in projection["case_states"]], "canonical case ordering")
    a.require(all(c["phase"] == "NOT_STARTED" and c["attempt_consumed"] is False and c["environment_identity"] is None for c in projection["case_states"]), "initial canonical case state")
    proposed = a.loads(a.read_exact(runtime.PACKAGE + "ledger_candidate.json", "5d1f10f5fa28860d7eb47a3a56a092c2492e2a90b440904990e44a8cf014d7bc"))
    a.require([e["base_attempt_id"] for e in proposed["entries"]] == ids, "frozen ledger ordering")
    a.require(not proposed["journal"] and all(e["state"] == "UNSTARTED" and not e["claimed"] and not e["attempt_consumed"] for e in proposed["entries"]), "frozen initial ledger")
    ledger_before = journal_observation(items)
    a.read_exact(NATIVE + "successor_runtime.py", SOURCE_SHA)
    a.read_exact(NATIVE + "successor_runtime_integration_candidate.json", CONFIG_SHA)
    enforcement = a.loads((a.ROOT / NATIVE / "network_enforcement_identity.json").read_bytes())
    encoded = (json.dumps(enforcement["SEMANTIC_ENFORCEMENT_IDENTITY"], ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    a.require(a.sha(encoded) == enforcement["semantic_enforcement_sha256"] == ENFORCEMENT_SHA, "enforcement identity")
    semantic = enforcement["SEMANTIC_ENFORCEMENT_IDENTITY"]
    a.require(semantic["restricted_work_item_ids"] == [i["base_attempt_id"] for i in items if i["build_network_required"]], "restricted identities/order")
    a.require(semantic["network_NONE_work_item_ids"] == [i["base_attempt_id"] for i in items if not i["build_network_required"]], "NONE identities/order")
    bases = semantic["seven_base_transport_map"]
    a.require(len(bases) == 7 and {b["scientific_base_authority"] for b in bases} == {i["base_image_reference"] for i in items}, "seven base scientific identities")
    native = importlib.import_module("evaluation.downstream_benchmark.evidence.v6_native_buildkit_client_compatibility_bridge_v1.successor_runtime")
    rejections = {}
    try:
        native.dispatch()
    except a.Rejected as exc:
        rejections["native_dispatch"] = str(exc)
    a.require("native_dispatch" in rejections, "native dispatcher unexpectedly admitted")

    class RealProvider:
        namespace = ledger.REAL

    try:
        native.NativeDockerTransport(compiled=None, binding=None, layout=None,
            artifact_root=a.OUTPUT_ROOT / "production-provider-probe-not-created", runner=RealProvider())
    except a.Rejected as exc:
        rejections["real_provider"] = str(exc)
    a.require("real_provider" in rejections, "real provider unexpectedly admitted")
    installations = {path: (a.ROOT / path).exists() for path in (runtime.INSTALLATION, native.INSTALLATION)}
    ledger_after = journal_observation(items)
    a.require(ledger_before == ledger_after, "ledger mutation by entry probes")
    after = tracked_fingerprint()
    a.require(before == after, "tracked file drift")
    a.require(a.sha((a.ROOT / a.CURRENT).read_bytes()) == CURRENT_SHA, "canonical final drift")
    record = {
        "schema": "V6_PREPARATION_EXECUTION_ENTRY_AUDIT_CANDIDATE_V1", "candidate_only": True,
        "status": "BLOCKED", "reason": "Frozen native runtime has no production dispatch/provider; no real opportunity consumed.",
        "audit_start_utc": started, "audit_end_utc": datetime.now(timezone.utc).isoformat(),
        "execution_start": None, "execution_end": None, "head": HEAD,
        "canonical": {"path": a.CURRENT, "sha256": CURRENT_SHA, "event_count": 3,
                      "event_3": current["event_head"], "pin": pin,
                      "lifecycle_label": current["lifecycle_label"], "phase_authorizations": projection["phase_authorizations"]},
        "population": {"path": runtime.PACKAGE + "work_items_candidate.json", "file_sha256": runtime.WORK_SHA,
                       "semantic_sha256": runtime.POPULATION_SHA, "total": 641, "unique_attempts": 641,
                       "ordered_attempt_ids_sha256": a.identity(ids), "variant_counts": variants,
                       "network_counts": network, "dispatchable_cases": 431, "census_cases": 433,
                       "blockers": blockers, "final_case_reconciliation_constructed": False},
        "runtime": {"source_path": NATIVE + "successor_runtime.py", "source_sha256": SOURCE_SHA,
                    "config_path": NATIVE + "successor_runtime_integration_candidate.json", "config_sha256": CONFIG_SHA,
                    "enforcement_sha256": ENFORCEMENT_SHA, "installation_paths_exist": installations,
                    "read_only_rejection_probes": rejections, "seven_scientific_base_identities": [b["scientific_base_authority"] for b in bases]},
        "persistent_root": str(a.OUTPUT_ROOT), "ledger_before": ledger_before, "ledger_after": ledger_after,
        "ledger_file_inventory_sha256": a.identity({"claims": [], "terminals": [], "locks": []}),
        "namespace_metadata": a.loads((a.OUTPUT_ROOT / "namespace.json").read_bytes()),
        "terminal_outcome_counts": {}, "environment_ready_cases_observed": 0,
        "non_ready_terminal_cases": 0, "dispatchable_cases_still_unstarted": 431,
        "environment_ready_population_candidate": None, "execution_closure_candidate": None,
        "tracked_before": before, "tracked_after": after,
        "firewall": {"source_acquisition": 0, "real_claims": 0, "builds": 0, "oracle": 0,
                     "allocation": 0, "downstream_repair": 0, "git_stage": False, "git_commit": False, "git_push": False},
        "checks": "PASS: exact entry identities, frozen population/recipes/order, ledger, semantic enforcement, and fail-closed rejection probes.",
        "not_checked": ["live seven-base OCI contents", "current source commit/blob presence", "current Docker/daemon/proxy/firewall state", "subject preparation builds", "environment-ready qualification"],
        "completion_review_gate": "HUMAN_PI_REVIEW_OF_V6_PREPARATION_EXECUTION_COMPLETE_BASELINE",
        "completion_review_gate_reached": False,
        "recommended_next_action": "Human-PI resolve the accepted production entrypoint/controller/provider installation gap with a separate bounded authority; preserve frozen attempts and canonical event #3.",
    }
    print(json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

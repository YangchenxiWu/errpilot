"""Finalize only this candidate namespace after actual exact-source qualification."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from . import validate_successor_resume as v

HERE = v.HERE
ROOT = v.ROOT
p = v.p
COMMON = {"candidate_only": True, "HUMAN_PI_ACCEPTED": "NO", "runtime_effective": "NO", "execute_now": False}


def write(name, value):
    (HERE / name).write_bytes(p.pretty(value))


def ref(path):
    return {"path": str(path), **v.identity(path)}


def main():
    results = v.read("synthetic_e2e_results.json")
    v.verify_external_qualification(results)
    matrix = v.read("rejection_matrix.json")
    assert len(matrix["checks"]) == 126 and matrix["mandatory_skipped"] == 0
    source = v.source_delta()
    write("source_semantic_delta.json", source)
    replay = v.replay_scientific()
    write("scientific_projection_revalidation.json", replay)
    preserved = v.preservation()
    write("preservation_verification.json", preserved)
    history = v.read("source_revision_history.json")
    history["revisions"][-1].update(qualification="PASS_126_REJECTIONS", final_source_pair={"controller": v.identity(Path(v.c.__file__)), "provider": v.identity(Path(p.__file__))})
    write("source_revision_history.json", history)
    # A distinct future production schema specification is candidate data, not
    # an issued production receipt or an effective installed contract.
    future = v.read("receipt_schema_v2_candidate.json")
    future["title"] = p.REAL_RECEIPT_SCHEMA
    future["properties"]["schema"]["const"] = p.REAL_RECEIPT_SCHEMA
    future["properties"]["runtime_authority"]["const"] = True
    future["properties"]["candidate_only"]["const"] = False
    future["properties"]["client_authorization_verdict"]["const"] = "REAL_CLIENT_AUTHORIZATION_PASS"
    future["description"] = "Candidate specification of a distinct future production V2 schema. No receipt, acceptance, installation or effectivity is constructed."
    write("future_production_receipt_schema_v2_specification.json", future)
    old = ROOT / "evaluation/downstream_benchmark/evidence/v6_preparation_execution_production_runtime_installation_resume_v1"
    entry = v.read("entry_snapshot.json")
    candidate = {**COMMON, "schema": "V6_TOPOLOGY_STABILITY_SUCCESSOR_INSTALLATION_CANDIDATE_V2",
        "status": "CANDIDATE_ONLY_SYNTHETICALLY_QUALIFIED", "canonical": {"path": p.a.CURRENT, "sha256": p.CANONICAL_SHA}, "event_3_id": p.EVENT_3,
        "old_installation_candidate": ref(old / "production_runtime_installation_candidate.json"),
        "old_installation_plan": ref(old / "installation_plan.json"),
        "old_plan_authorizes_new_sources": False, "enforcement_identity": p.ENFORCEMENT,
        "population_identity": replay["population"], "ledger_binding_identity": p.ledger_identity(),
        "source_pair": {"controller": ref(Path(v.c.__file__)), "provider": ref(Path(p.__file__))},
        "security_contracts": {name: ref(HERE / name) for name in p.SECURITY_CONTRACT_NAMES},
        "receipt_contract": ref(HERE / "receipt_authority_contract_v2_candidate.json"),
        "receipt_schema_candidate": ref(HERE / "receipt_schema_v2_candidate.json"),
        "future_production_schema_specification": ref(HERE / "future_production_receipt_schema_v2_specification.json"),
        "qualification": {name: ref(HERE / name) for name in ("synthetic_e2e_qualifier.py", "synthetic_e2e_results.json", "rejection_matrix.json", "scientific_projection_revalidation.json", "source_semantic_delta.json")},
        "predecessors": {name: {"manifest_self_sha256": package["manifest_self_sha256"], "total_file_count": package["total_file_count"], "identity_basis": package["identity_basis"]} for name, package in entry["predecessors"].items()},
        "proposed_future_targets": {"controller": p.CONTROLLER_TARGET, "provider": p.PROVIDER_TARGET, "receipt_contract": p.CONTRACT_TARGET,
            "effectivity": p.EFFECTIVITY, "acceptance_pin": p.ACCEPTANCE_PIN, "installation_authority": p.INSTALLATION_AUTHORITY,
            "live_evidence_observer": p.LIVE_OBSERVER_TARGET},
        "future_effectivity": "UNCONSTRUCTED_REQUIRES_SEPARATE_HUMAN_PI_ACCEPTANCE_AND_INSTALLATION",
        "accepted_live_projection": "UNCONSTRUCTED", "accepted_client_principals": "UNCONSTRUCTED",
        "independent_live_evidence_observer": "NOT_CONSTRUCTED_NOT_ACCEPTED_NOT_INSTALLED; mandatory separate reviewed C6 equivalent provenance source",
        "REAL_CLIENT_AUTHORIZATION": "BLOCKED_UNTIL_INDEPENDENT_LIVE_EVIDENCE", "historical_clients": "ORIGIN_NOT_ESTABLISHED",
        "PRODUCTION_RUNTIME_INSTALLED": "NO", "REAL_PRODUCTION_ENTRY_EFFECTIVE": "NO", "real_attempt_authorized": False}
    write("successor_installation_candidate.json", candidate)
    plan = {**COMMON, "schema": "V6_TOPOLOGY_STABILITY_SUCCESSOR_INSTALLATION_PLAN_V2_CANDIDATE", "candidate": ref(HERE / "successor_installation_candidate.json"),
        "current_production_installation_authorized": False, "current_real_attempt_authorized": False,
        "transaction_execute_commands": [], "target_files_written": [],
        "dependencies_in_order": ["Human-PI review exact sealed candidate", "Separate acceptance/publication of exact versioned sources/contracts",
            "Separate explicit installation authority for the new pair (old V1 plan insufficient)",
            "Independently accepted authenticated C6 observer source and accepted principal scope, complete fresh live census/boundary",
            "Fresh complete raw security evidence and exact accepted stable projection",
            "Separately constructed, accepted and installed acyclic V2 effectivity descriptor and independent acceptance pin",
            "Compare-install exact accepted sources/contract/schema pins only under later explicit authority",
            "Separate authorized preparation execution; fresh preclaim/provider checks before original exclusive claim/native solve"],
        "unconstructed_future_effectivity": True, "live_client_status": "BLOCKED", "operational_remediation_authorized": False,
        "claim_adapter": "V2 only adds exact raw association SHA to the input binding; original exclusive lock, immutable terminal/one-attempt ownership, no retry semantics remain unchanged",
        "sidecar": "Immutable original bytes/readback before lock; not bearer authority; orphan association blocks future reentry without consuming attempt",
        "supersession": "Historical V1 and all blocked predecessor evidence retained unchanged; no historical BLOCK relabeled",
        "NEXT_GATE": "HUMAN_PI_REVIEW_OF_V6_PRODUCTION_RUNTIME_TOPOLOGY_STABILITY_SUCCESSOR_CANDIDATE"}
    write("successor_installation_plan.json", plan)
    groups = [
        ("historical_frozen_V1_baseline", [ROOT / ref_["path"] for ref_ in entry["controlling_sources"].values()]),
        ("image_corrected_candidate", [ROOT / "evaluation/downstream_benchmark/evidence/v6_production_runtime_image_identity_compatibility_bridge_v1/artifact_sha256.json",
            ROOT / "evaluation/downstream_benchmark/evidence/v6_production_runtime_image_identity_compatibility_bridge_v1/corrected_production_provider_candidate.py"]),
        ("forensic_evidence", [ROOT / "evaluation/downstream_benchmark/evidence/v6_production_runtime_topology_exec_forensics_v1/artifact_sha256.json"]),
        ("partial_successor_BLOCK", [ROOT / "evaluation/downstream_benchmark/evidence/v6_production_runtime_topology_stability_successor_v1/artifact_sha256.json"]),
        ("Human_PI_C1_C16_decision", [HERE / "human_pi_decision.json"]),
        ("topology_client_contracts", [HERE / name for name in ("client_authorization_contract_candidate.json", "topology_stability_contract_candidate.json", "raw_observation_contract_candidate.json", "transient_diagnostics_contract_candidate.json")]),
        ("receipt_sidecar_contract_schema", [HERE / name for name in ("receipt_authority_contract_v2_candidate.json", "receipt_schema_v2_candidate.json", "future_production_receipt_schema_v2_specification.json", "raw_sidecar_contract_candidate.json", "receipt_binding_analysis.json")]),
        ("successor_exact_source_pair", [Path(v.c.__file__), Path(p.__file__)]),
        ("successor_qualification", [HERE / name for name in ("synthetic_e2e_qualifier.py", "synthetic_e2e_results.json", "rejection_matrix.json", "source_semantic_delta.json", "scientific_projection_revalidation.json")]),
        ("successor_installation_candidate", [HERE / "successor_installation_candidate.json"]),
        ("successor_installation_plan", [HERE / "successor_installation_plan.json"]),
    ]
    graph = {**COMMON, "schema": "V6_SUCCESSOR_RESUME_SUPERSESSION_DEPENDENCY_DAG_V2",
        "nodes": [{"id": name, "artifacts": [ref(path) for path in paths]} for name, paths in groups],
        "edges": [[groups[i][0], groups[i + 1][0]] for i in range(len(groups) - 1)],
        "future_effectivity": "SEPARATE_UNCONSTRUCTED_NOT_A_HASH_NODE", "old_plan_not_authoritative_for_new_sources": True,
        "hash_direction": "Contracts contain no new source/receipt/result/install/manifest hashes; sources name contracts without content hash; qualification references sources; candidate references qualification; plan references candidate; graph references all; final inventory references graph. No node hashes itself or a successor.",
        "receipt_hash_direction": ["raw", "security projection", "receipt", "association", "claim"],
        "source_SHA_pins_independent": True, "historical_BLOCK_status_unchanged": True}
    v.acyclic(graph)
    write("supersession_dependency_graph.json", graph)
    # Machine-readable inspection limits: no synthetic pass is a live census.
    write("production_negative_boundary.json", {**COMMON, "schema": "V6_SUCCESSOR_RESUME_PRODUCTION_NEGATIVE_BOUNDARY_V1",
        "REAL_CLIENT_AUTHORIZATION": "BLOCKED", "REAL_CLIENT_AUTHORIZATION_STATUS": "BLOCKED_UNTIL_INDEPENDENT_LIVE_EVIDENCE",
        "PRODUCTION_RUNTIME_INSTALLED": "NO", "REAL_PRODUCTION_ENTRY_EFFECTIVE": "NO", "historical_execs": "ORIGIN_NOT_ESTABLISHED",
        "real_source_export": 0, "real_build": 0, "oracle": 0, "real_receipt": 0, "real_claim": 0, "real_terminal": 0,
        "commit": 0, "push": 0, "Docker_commands": 0, "live_Docker_observations": 0,
        "unavailable_live_evidence_is_never_filled_from_history": True})
    commands = v.read("commands_run.json")
    commands["construction_and_validation_commands"] = [
        {"command": ".venv/bin/python -B -m " + name, "returncode": 0} for name in (
            "evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_resume_v1.construct_resume",
            "evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_resume_v1.construct_sources",
            "evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_resume_v1.construct_qualifier")]
    commands["qualification_runs"] = [{"command": ".venv/bin/python -B -m evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_resume_v1.synthetic_e2e_qualifier",
        "run": i, "returncode": 0, "rejections": count, "Docker_executed": False, "paths_reused": False} for i, count in ((1, 111), (2, 116), (3, 126))]
    commands["independent_audit_commands"] = ["source_delta(): exact AST audit", "replay_scientific(): successor/old/corrected 641 byte-and-command equality", "preservation(): exact tracked/index/predecessor/canonical/real-ledger replay", "git ls-remote origin refs/heads/main (entry and exit, read-only escalation)"]
    write("commands_run.json", commands)
    # Keep all report content upstream of the manifest: its self SHA is returned
    # externally by --verify-seal, never inserted into a payload that it hashes.
    file_count = len([f for f in HERE.rglob("*") if f.is_file()]) + 3  # report, ruff result, validation result; no seal yet
    report = f"""# Run Report — V6 topology-stability successor resume

STATUS: `{v.STATUS}`
NEXT_GATE: `HUMAN_PI_REVIEW_OF_V6_PRODUCTION_RUNTIME_TOPOLOGY_STABILITY_SUCCESSOR_CANDIDATE`

Task: construct one NON-EFFECTIVE successor candidate under the exact direct attached Human-PI contract. No acceptance, installation, effectivity, commit, push or real attempt.

## A. Entry / canonical authority
`main`, local HEAD and live origin/main `{entry['head']}`. Canonical SHA `{p.CANONICAL_SHA}`, PREPARATION_EXECUTION_AUTHORIZED, event_count 3, event #3 `{p.EVENT_3}`. All required entry identities replayed. `.airos/current_state.md` and repo AGENTS files were absent; the direct pasted contract and supplied global AGENTS instructions control.

## B. Three immutable predecessor populations
Image correction: 281 files, manifest `ee8948b829a072ff10e3a41ba086afb4151821010661d89a05ce444ba95369e8`.
Forensics: 220 files, manifest `96b22bb49d14b366d3d6ef7f4d9101b48cae5c6e85112c4798319d4fc7d2c1dd`.
Partial BLOCK: 71 files, entry-measured manifest `def7f4bd8569094ce608dd1ecc8b790c690780ec827dc43c11e2207284f5f21d`; not a previously Human-PI-accepted identity. All 572 relative paths, sizes and hashes, including construction_revision_2, remained exact. Its historical BLOCK was not relabeled. See predecessor_seal_binding.json.

## C. Human-PI C1–C16 implementation
Exact decision text is preserved in raw_human_pi_request.txt and human_pi_decision.json. Every current control-capable session needs independent attribution or independently verified inaccessibility. Current complete census, source authentication, process/endpoint correlation, original provenance-byte SHA, accepted principal scope and control-plane boundary are mandatory. Names, timestamps, ExecIDs, buildctl and a Boolean alone do not authorize. Synthetic data is explicitly confined to candidate source/root. C13 permits candidate construction while real authorization remains blocked.

## D–F. Stable security, raw/transient separation and UNKNOWN behavior
The V2 projection verifies immutable Engine/OCI manifest/config/RootFS, daemon instance/state/argv, worker amd64, exact binaries, endpoint, internal network/participants, exact proxy bindings/source/policy, approved CONNECT origins, no published ports/external/default routes, exact Unix listeners and independently observed ownership/access. Each mandatory field has source/method/type/canonicalization/failure rules in topology_stability_contract_candidate.json. Full raw original bytes, ExecIDs/order, socket rows/addresses/inodes, source metadata and client proofs remain independently hashed. UNKNOWN/unauthorized/incomplete/unverifiable evidence rejects; no historical client exoneration. Authorized transient inode/ExecID turnover passed with equal projection and distinct raw/client evidence hashes.

## G–I. Fresh admission, V2 receipts and raw association
Canonical/event/source/work gates precede fresh security/client/access gates. Mandatory client checks now precede local base probes. Receipt bytes bind the entire unchanged work identity, one exact attempt, canonical/event/effectivity/source/contract/enforcement pins, RESTRICTED_DEFAULT, exact origins and security/client policy/issuance evidence SHA. NONE prohibits receipts and has null claim receipt SHA. A distinct future production schema specification is candidate data; no V1 field is relabeled and no production receipt exists.
Before the original exclusive lock, immutable issuance/current raw plus receipt/association bytes are fsynced and read back. The claim binds exact receipt and association SHA. Sidecars grant no bearer authority and consume no attempt; orphan publication blocks automatic reentry. Providers replay original association/receipt and independently acquire current evidence immediately before solve. Hash direction is raw → security → receipt → association → claim. No circular dependency.

## J–K. Exact source pair and authorized delta
Controller SHA `{candidate['source_pair']['controller']['sha256']}`.
Provider SHA `{candidate['source_pair']['provider']['sha256']}`.
Provider uses the exact image-corrected SHA `82561a9bfe646114e61d00c2c8e01012086a28b15d0bf67488e1d787a6f5371f` as technical predecessor. AST audit declares 15 provider and 5 controller changed function bodies; 23 provider and 6 controller bodies remain identical. Scientific compile, native solve/command/layout paths, original real scientific execute and immutable terminal implementation are preserved. New deltas are V2 authority/client/topology/receipt/association guards and bounded qualification interfaces. Details and complete AST inventory: source_semantic_delta.json.

## L–N. Legitimate hermetic E2E and complete rejection matrix
New exclusive root `{p.QUALIFICATION_ROOT}`. Final run `{results['qualification_run_root']}`; 62 independent fixtures, all synthetic IDs. Own normal constructors, exact source-location/root guards; no object.__new__, __file__ forgery, sys.modules injection or legacy-global mutation. Copied modules were loaded normally with runpy and rejected. Candidate-owned simulated transport executes the original shared scientific `_materialize_checked` code object, including context/build command/probes/identity, through bounded simulated I/O. Its shared checked-path Boolean is false to select the original scientific path, while the owning constructor, namespace, root, transport and candidate_scientific_run.json remain synthetic. No protected production constructor was bypassed and no subprocess Docker/native solve was executed.

Actual restricted and NONE receipt → claim → provider → terminal paths passed, including immutable receipt equality, provider failure exactly one terminal, independently inaccessible sessions, and independent provider revalidation. Both new and inherited A–X (24 each) passed. 126 actual rejection categories passed: all inherited 77 plus 49 V2/client/topology/sidecar/constructor/CLI categories. No mandatory category was skipped. Every rejection records exact source hashes, expected category, observed rejection and ledger byte census before/after. Parser error output in CLI probes is expected rejection evidence. Revisions 1 and 2 (111/116 preliminary rejection passes) remain preserved and superseded by the current exact pair.

## O. Frozen 641 scientific / native replay
Population file `{replay['population']['file_sha256']}`, semantic `{replay['population']['semantic_sha256']}`, ordered IDs `{replay['population']['ordered_attempt_ids_sha256']}`. 641 = 221 SOURCE_INDEPENDENT + 210 BUGGY + 210 FIXED; 583 RESTRICTED / 58 NONE. All successor scientific/execution Dockerfile bytes and native argv projections matched historical and corrected sources, including RUN byte/order/base authority. matplotlib::1 and matplotlib::8 remain blocked. Projection verification is implementation equivalence, not scientific benchmark validation. Real source export/build/oracle: 0. Per-item hashes: scientific_projection_revalidation.json.

## P–Q. Supersession and installation candidate/plan
The exact historical baseline → image correction → forensics → partial BLOCK → C1–C16 → topology/client contracts → receipt/schema → pair → qualification → installation candidate → plan graph is acyclic. Exact file refs/SHAs are in supersession_dependency_graph.json. Graph data is generated after candidate/plan and does not supply authority to them. Future effectivity remains separate and unconstructed. New candidate and plan both have candidate_only=true, HUMAN_PI_ACCEPTED=NO, runtime_effective=NO; plan execute_now=false, current_production_installation_authorized=false and current_real_attempt_authorized=false. Exact candidate/plan SHA identities are bound in the graph and final inventory. Old V1 installation authority does not transfer to these new sources.

## R. Artifact inventory
artifact_sha256.json seals every new payload's relative path, size and exact SHA. It alone is excluded from its own inventory. Its exact self SHA and payload/total counts are computed and returned by the independent `validate_successor_resume --verify-seal` output; the self SHA is not embedded into a payload it hashes, which would introduce a cycle. This report is itself sealed. Planned payload count before seal: {file_count} (the final manifest is authoritative).

## S. Repository / Docker / real ledger preservation
All original 1065 tracked file bytes, Git index, HEAD/live origin, canonical/event #3, frozen runtime/config/ledger/enforcement and all 572 predecessor files were replayed unchanged. Only this new repo namespace is added. Real output/ledger paths, modes and bytes remained exact: 641 UNSTARTED, 0 claims, terminals, retries or orphans. No Docker command, socket/attach operation, mutation, stop/restart, pull or cleanup occurred. No live Docker observation was performed; current infrastructure byte identity/client authorization is not independently certified. Running daemon/proxy/networks/volume were untouched by this agent. No production target was written. See preservation_verification.json.

## T. Production negative boundary / risks / next action
REAL_CLIENT_AUTHORIZATION=BLOCKED_UNTIL_INDEPENDENT_LIVE_EVIDENCE; PRODUCTION_RUNTIME_INSTALLED=NO; REAL_PRODUCTION_ENTRY_EFFECTIVE=NO. Historical execs remain ORIGIN_NOT_ESTABLISHED. The separately reviewed fixed C6 live observer, accepted current principal scope, complete live census/access proof and accepted installed security projection do not exist in this transaction. Future real mode requires their exact independently accepted source/payload pins and rejects missing evidence. Synthetic authentication flags/data cannot enter real constructors. Sequential observation cannot prove continuous atomic security; inaccessible/unobserved surfaces block.

Files changed: only new artifacts under `{HERE.relative_to(ROOT)}` and exclusively new synthetic qualification subtrees. No .airos report, tracked/production or predecessor file changed.
Commands: existing .venv Python -B constructors/qualifier (three distinct source revisions), read-only AST/641/preservation replays, Ruff --no-cache, read-only git ls-remote entry/exit, and independent validator --verify-seal. Full bounded command/result census is in commands_run.json. The initial system Python lacked jsonschema; existing .venv was reused without dependency installation. Initial sandbox DNS lookup failed; the authorized read-only escalation passed. An overbroad AGENTS path search was interrupted and replaced with bounded ancestor/repo reads.
Tests: complete E2E, 126 rejections, both A–X mappings, exact 641 replay, source/contract/schema/graph checks, Ruff and preservation PASS. No native/live/scientific benchmark validation is claimed.
Contract compliance: bounded construction only; no git add/commit/push, real receipt/claim/terminal/materialization/execution, live topology mutation or authority promotion. Recommendation: Human-PI review this exact sealed candidate. Acceptance, installation, execution and remediation remain separate human gates.
"""
    (HERE / "RUN_REPORT.md").write_text(report)
    ruff = subprocess.run([str(ROOT / ".venv/bin/ruff"), "check", "--no-cache", str(HERE)], capture_output=True, check=False)
    write("ruff_results.json", {"command": [str(ROOT / ".venv/bin/ruff"), "check", "--no-cache", str(HERE)], "returncode": ruff.returncode,
                               "stdout": ruff.stdout.decode(), "stderr": ruff.stderr.decode()})
    assert ruff.returncode == 0, ruff.stdout.decode()
    validation = {**COMMON, "schema": "V6_SUCCESSOR_RESUME_VALIDATION_V2", "status": v.STATUS,
        "mandatory_skipped": 0, "entry": "PASS", "predecessor_seals_preservation": "PASS", "tracked_1065_index_HEAD_live_origin": "PASS",
        "canonical_event3_real_ledger": "PASS", "frozen_source_config_ledger_enforcement": "PASS", "contract_schema_canonicalization": "PASS",
        "source_AST_authorized_delta": "PASS", "Ruff": "PASS", "actual_source_pair_full_E2E": "PASS",
        "new_A_X": 24, "inherited_A_X": 24, "inherited_rejections": 77, "total_rejections": 126, "full_rejections": "PASS_REJECTED",
        "scientific_replay_641": "PASS", "acyclic_hash_graph": "PASS", "real_client_authorization": "BLOCKED", "production_runtime_installed": "NO",
        "real_production_entry_effective": "NO", "historical_clients": "ORIGIN_NOT_ESTABLISHED",
        "NEXT_GATE": plan["NEXT_GATE"], "artifact_seal": "Verified independently after seal creation; manifest self SHA external to sealed payload graph"}
    write("validation_results.json", validation)
    # Independent verifier executes all gates; any failure leaves unsealed BLOCK
    # evidence rather than manufacturing a successful inventory.
    result = subprocess.run([str(ROOT / ".venv/bin/python"), "-B", "-m", "evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_resume_v1.validate_successor_resume"], capture_output=True, check=False)
    if result.returncode:
        write("construction_block.json", {**COMMON, "status": "BLOCKED", "validator_exit": result.returncode,
              "stdout": result.stdout.decode(), "stderr": result.stderr.decode(), "remaining_gate": "INDEPENDENT_VALIDATION_FAILED"})
        raise RuntimeError(result.stderr.decode())
    commands = v.read("commands_run.json")
    commands["finalization"] = {"command": ".venv/bin/python -B -m evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_resume_v1.finalize_resume", "independent_validator_returncode": result.returncode, "independent_validator_stdout": result.stdout.decode(), "Ruff_returncode": 0}
    commands["final_external_check"] = {"command": ".venv/bin/python -B -m evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_resume_v1.validate_successor_resume --verify-seal", "result_record": "Returned externally after seal; no post-seal payload write"}
    write("commands_run.json", commands)
    files = {str(f.relative_to(HERE)): v.identity(f) for f in sorted(HERE.rglob("*")) if f.is_file() and f != HERE / "artifact_sha256.json"}
    write("artifact_sha256.json", {**COMMON, "schema": "V6_SUCCESSOR_RESUME_ARTIFACT_SHA256_V1", "excluded": ["artifact_sha256.json"],
        "payload_count": len(files), "total_file_count": len(files) + 1, "files": files, "status": v.STATUS,
        "self_sha256_semantics": "SHA256 exact manifest bytes, independently reported externally; no self-reference"})
    print(json.dumps({"status": v.STATUS, **v.verify_seal(), "controller_sha256": candidate["source_pair"]["controller"]["sha256"], "provider_sha256": candidate["source_pair"]["provider"]["sha256"], "candidate_sha256": v.identity(HERE / "successor_installation_candidate.json")["sha256"], "plan_sha256": v.identity(HERE / "successor_installation_plan.json")["sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()

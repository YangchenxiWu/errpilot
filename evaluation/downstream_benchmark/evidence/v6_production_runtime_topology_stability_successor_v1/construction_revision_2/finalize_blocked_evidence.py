"""Finalize the bounded BLOCK evidence without creating source or authority pins."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone

from . import construct_blocked_candidate as c
from .validate_successor_candidate import validate


def ref(path):
    return {"path": str(path.relative_to(c.ROOT)), **c.file_record(path)}


def main():
    pins = c.read(c.HERE / "historical_predecessor_binding.json")["controlling_file_identities"]
    topology = ["raw_evidence_preservation_contract.json", "security_projection_contract_candidate.json",
                "transient_diagnostic_contract_candidate.json", "unknown_exec_authorization_policy_candidate.json",
                "client_authorization_decision_point.json", "topology_freshness_contract_candidate.json"]
    receipt = ["receipt_authority_contract_v2_candidate.json", "receipt_schema_v2_candidate.json"]
    nodes = [
        {"id": "historical_accepted_baseline", "status": "HISTORICAL_UNCHANGED",
         "artifacts": [{"path": x["path"], "sha256": x["sha256"]} for x in pins.values()]},
        {"id": "image_corrected_non_effective_provider", "status": "PREDECESSOR_NON_EFFECTIVE",
         "artifacts": [ref(c.BRIDGE / "corrected_production_provider_candidate.py")]},
        {"id": "forensics_and_Option_B_decision", "status": "CONSTRUCTION_AUTHORITY_ONLY",
         "artifacts": [ref(c.FORENSICS / "artifact_sha256.json"), ref(c.HERE / "human_pi_decision.json")]},
        {"id": "topology_contract", "status": "PARTIAL_BLOCKED_UNRESOLVED_CLIENT_AUTHORIZATION",
         "artifacts": [ref(c.HERE / x) for x in topology]},
        {"id": "receipt_contract_schema", "status": "CANDIDATE_DESIGN_ONLY_NON_EFFECTIVE",
         "artifacts": [ref(c.HERE / x) for x in receipt]},
        {"id": "successor_source_pair", "status": "NOT_CONSTRUCTED", "missing": "Unique mandatory client authorization rule"},
        {"id": "successor_synthetic_qualification", "status": "NOT_RUN_NO_SUCCESSOR_SOURCE"},
        {"id": "successor_installation_candidate", "status": "NOT_CONSTRUCTED"},
        {"id": "successor_installation_plan", "status": "NOT_CONSTRUCTED"},
        {"id": "future_effectivity", "status": "OUTSIDE_TRANSACTION_NOT_CREATED_NOT_ACCEPTED"},
    ]
    edges = [[nodes[i]["id"], nodes[i + 1]["id"]] for i in range(len(nodes) - 1)]
    c.write("supersession_dependency_graph.json", {**c.COMMON, "schema": "V6_SUCCESSOR_PARTIAL_SUPERSESSION_DAG_V1",
            "status": "BLOCKED", "nodes": nodes, "edges": edges,
            "edge_meaning": "Upstream evidence/acceptance prerequisite for downstream construction or later authority; planned edges do not claim completed nodes",
            "hash_order": "Contracts -> exact source pair -> qualification -> installation candidate -> plan -> later independent installation/effectivity",
            "no_cycle_rule": "Sources may bind upstream contracts and exact paths but never their own file SHA or downstream qualification SHA. Synthetic fixtures bind finalized source SHA. Installation authority must not bind downstream effectivity file SHA.",
            "future_targets": c.read(c.RESUME / "installation_plan.json")["future_targets"],
            "future_effectivity_prerequisites": ["Exact mandatory client authorization rule independently decided",
                "Complete successor contracts/source pair and actual new-source qualification",
                "Exact successful 641 successor projection replay and complete A-X/77/new rejection tests",
                "Separate Human-PI acceptance of exact contracts/source/schema/qualification",
                "Separate authorized versioned installation candidate/plan acceptance and installation transaction",
                "Fresh independently validated complete production topology and accepted stable projection binding",
                "Separate exact installed source and effectivity publication/independent acceptance pin",
                "Separate real preparation attempt authority"],
            "accepted_installation_pin_generated": False, "population_and_order_unchanged": True})
    identities = {"topology_contract": (pins["topology_contract"], ref(c.HERE / "security_projection_contract_candidate.json")),
                  "receipt_contract": (pins["receipt_contract"], ref(c.HERE / "receipt_authority_contract_v2_candidate.json")),
                  "receipt_schema": (pins["receipt_schema"], ref(c.HERE / "receipt_schema_v2_candidate.json"))}
    identity_report = {name: {"old": old, "proposed_new_partial_candidate": new,
                              "new_identity_is_accepted": False} for name, (old, new) in identities.items()}
    for name in ("controller", "provider", "installation_candidate", "installation_plan"):
        identity_report[name] = {"old": pins[name], "proposed_new": {"status": "NOT_CONSTRUCTED"}}
    c.write("candidate_identities.json", {**c.COMMON, "schema": "V6_BLOCKED_SUCCESSOR_IDENTITIES_V1",
            "identities": identity_report, "image_corrected_technical_predecessor": ref(c.BRIDGE / "corrected_production_provider_candidate.py"),
            "additional_candidate_contracts": [ref(c.HERE / x) for x in topology],
            "future_effectivity_pin": {"status": "NOT_CREATED_NO_INDEPENDENT_ACCEPTANCE"},
            "complete_manifest": "artifact_sha256.json (created last; external SHA avoids self-reference)"})
    c.write("construction_revision_and_failure_history.json", {
            "schema": "V6_BLOCKED_SUCCESSOR_CONSTRUCTION_HISTORY_V1",
            "failures": [{"command": ".venv/bin/python -B -m evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_v1.construct_blocked_candidate",
                          "returncode": 1, "stage": "Historical receipt contract path discovery before entry snapshot or contract writes",
                          "exception": "AssertionError: receipt_contract SHA matched both production_receipt_authority_contract.json and receipt_contract.json",
                          "resolution": "Use exact production_receipt_authority_contract.json named by original provider and installation plan; preserve identical duplicate frozen copy",
                          "existing_evidence_modified": False}],
            "successful_retry": {"returncode": 0, "status": "BLOCKED", "predecessor_scientific_replay": 641},
            "initial_network_failure": {"command": "git ls-remote origin refs/heads/main", "returncode": 128,
                                        "reason": "Sandbox DNS could not resolve github.com", "resolution": "Authorized read-only escalation succeeded"}})
    ruff_argv = [str(c.ROOT / ".venv/bin/ruff"), "check", "--no-cache", str(c.HERE)]
    ruff = subprocess.run(ruff_argv, cwd=c.ROOT, capture_output=True, check=False, timeout=60)
    c.write("ruff_results.json", {"schema": "V6_BLOCKED_SUCCESSOR_EVIDENCE_RUFF_V1", "argv": ruff_argv,
            "returncode": ruff.returncode, "stdout": ruff.stdout.decode(), "stderr": ruff.stderr.decode(),
            "scope": "New evidence scripts only; successor production source not constructed"})
    assert ruff.returncode == 0
    preallocation = [
        {"command": "cat /Users/wuyangchenxi/.codex/attachments/c62e1362-5183-4e32-9ccf-da1667105a48/已粘贴的文本.txt", "purpose": "Read direct user request", "returncode": 0},
        {"command": "git status --short --branch", "returncode": 0, "result": "main...origin/main; only two specified predecessor namespaces untracked"},
        {"command": "git rev-parse HEAD", "returncode": 0, "result": c.HEAD},
        {"command": "git ls-files | wc -l", "returncode": 0, "result": 1065},
        {"command": "git ls-files --others --exclude-standard | wc -l", "returncode": 0, "result": 501},
        {"command": "git ls-remote origin refs/heads/main", "returncode": 128, "result": "Sandbox DNS failure; see live_origin_entry.json"},
        {"command": "git ls-remote origin refs/heads/main", "returncode": 0, "result": "Exact required live HEAD; authorized escalation"},
        {"command": "git ls-remote origin refs/heads/main", "returncode": 0, "result": "Final same live HEAD; live_origin_exit.json"},
        {"command": "rg --files / rg -n; sed and cat reads; python3 read-only inspection snippets", "record_kind": "GROUPED_INSPECTION_SUMMARY_NOT_EXACT_ARGV_TRANSCRIPT",
         "scope": ["Instruction file presence", "Original controller/provider source and source-location guards", "Original R1-R22/topology/schema contracts",
                   "Both complete predecessor manifests", "Forensic socket, security and exec-origin assessment", "Historical A-X/77 matrix",
                   "Scientific compilation/guards and ledger implementation"],
         "limitation": "Preallocation inspection snippets were not retained as individually sealed command transcripts; no claim of an exhaustive raw transcript"},
    ]
    c.write("commands_run.json", {"schema": "V6_BLOCKED_SUCCESSOR_COMMANDS_V1",
            "preallocation_and_live_remote_commands": preallocation,
            "construction_exact_script": ref(c.HERE / "construct_blocked_candidate.py"),
            "construction_recorded_commands": c.read(c.HERE / "construction_commands.json"),
            "evidence_validator_script": ref(c.HERE / "validate_successor_candidate.py"),
            "finalizer_script": ref(c.HERE / "finalize_blocked_evidence.py"),
            "primary_module_commands": [
                ".venv/bin/python -B -m evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_v1.construct_blocked_candidate",
                ".venv/bin/python -B -m evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_v1.finalize_blocked_evidence",
                ".venv/bin/python -B -m evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_v1.validate_successor_candidate --verify-seal"],
            "Ruff": ruff_argv,
            "validator_git_reads": [["git", *args] for args in [("ls-files", "-z"), ("diff", "--binary"), ("diff", "--cached", "--binary"),
                ("diff", "--check"), ("rev-parse", "HEAD"), ("branch", "--show-current"), ("ls-files", "--others", "--exclude-standard", "-z")]],
            "Docker_commands_run": [], "dependency_installs": 0, "source_acquisition": 0, "GUI_opened": 0,
            "real_build_receipt_claim_terminal": 0, "git_add_commit_push": 0})
    result = validate(False)
    c.write("validation_results.json", result)
    c.write("preservation_verification.json", {**c.COMMON, "schema": "V6_BLOCKED_SUCCESSOR_PRESERVATION_V1",
            "repository_firewall": "PASS", "all_1065_tracked_file_bytes_unchanged": True,
            "index_unchanged": True, "HEAD_unchanged": True, "tracked_diff_empty": True,
            "complete_predecessor_payloads_280_plus_219_and_two_manifests_unchanged": True,
            "canonical_state_SHA_event_3_unchanged": True, "frozen_runtime_configuration_unchanged": True,
            "641_work_identity_and_order_unchanged": True, "real_ledger_exact_tree_unchanged": True,
            "real_ledger_states": {"UNSTARTED": 641}, "claims": 0, "terminals": 0, "retries": 0, "orphans": 0,
            "production_installation_targets_absent": True,
            "untracked": "Only two sealed predecessors plus new authorized successor namespace",
            "Docker_transaction_actions": [], "Docker_mutations_by_transaction": 0,
            "live_Docker_complete_topology_preservation_comparison": "NOT_PERFORMED_NO_LIVE_DOCKER_OBSERVATION",
            "current_worker_binary_route_socket": "UNVERIFIED", "live_full_inspect_equality": "NOT_TESTED_CURRENT_TRANSACTION",
            "historical_full_inspect_equality": False,
            "no_scientific_downstream_actions": True, "no_installation_activation_real_receipt_claim_terminal": True,
            "no_git_add_commit_push": True})
    checks = result["checks"]["candidate_schema_only_tests"]
    identity_lines = []
    for name in ("topology_contract", "receipt_contract", "receipt_schema"):
        rec = identity_report[name]
        identity_lines.append(f"| {name} | `{rec['old']['sha256']}` | `{rec['proposed_new_partial_candidate']['sha256']}` (partial candidate) |")
    report = f"""# Run Report — V6 topology semantic-stability successor V1

STATUS = **BLOCKED**

PRODUCTION_GATE = **BLOCKED_BY_UNRESOLVED_CLIENT_AUTHORIZATION**

NEXT_MISSING_AUTHORITY = **Unique Human-PI decision on the mandatory active-client authorization rule, its admissible independent evidence and completeness criterion, and treatment of unattributed active clients.**

This package preserves partial, non-effective contract construction and bounded BLOCK evidence under request sections 6, 16 and 17. It is not a complete successor candidate ready for review, an accepted policy, production qualification or scientific validation.

## 1. Task summary

Recorded the direct Option B construction-only decision, replayed every controlling file identity and both complete predecessor seals, and derived separate raw-evidence, stable-security, diagnostic, unknown-exec, freshness and V2 receipt/schema drafts. R1–R22 impact is individually accounted for. The active-client authorization decision remains explicit and unselected in client_authorization_decision_point.json.

The exact supplied decision permits a separate unresolved policy decision point; it does not uniquely decide whether complete authorization of every active client is mandatory or define acceptable attribution evidence. Choosing that requirement or a forensic-only alternative would be an additional decision. No guess was embedded in a source pair. Consequently new controller/provider source, runnable E2E entry, installation candidate/plan and accepted effectivity pin were not constructed. Planned DAG nodes explicitly say NOT_CONSTRUCTED or NOT_RUN.

## 2. Files changed

All new files are beneath `{c.HERE}`. Core outputs: human_pi_decision.json, entry_verification.json, historical_predecessor_binding.json, the six topology/policy contracts and decision point, receipt_contract_impact_analysis.json, receipt_authority_contract_v2_candidate.json, receipt_schema_v2_candidate.json, source_semantic_delta.json, qualification_entry_design_candidate.json, synthetic_e2e_results.json, rejection_matrix.json, scientific_projection_revalidation.json, supersession_dependency_graph.json, candidate_identities.json, construction_block.json, preservation_verification.json, commands_run.json, validation_results.json, three evidence scripts, snapshots, live-origin records, revision history, RUN_REPORT.md and artifact_sha256.json. The manifest is the complete file census. No prior evidence or tracked file changed.

## 3. Commands run

Read-only Git HEAD/branch/status/ls-files/diffs and two successful live `git ls-remote origin refs/heads/main` queries; local Python manifest/size/SHA/AST reads; `rg`, `sed`, `cat` source inspection; `.venv/bin/python -B -m` construction/finalization/verification; `.venv/bin/ruff check --no-cache` on the new evidence scripts. The first sandbox remote query failed DNS and its authorized read-only escalation succeeded. No Docker command, dependency installation or GUI opening occurred.

commands_run.json records primary commands and exact retained on-disk scripts. Preallocation inspection snippets are grouped summaries, not an exhaustive sealed raw command transcript. Live-origin records explicitly disclose that exact start/end timestamps were not captured. No absent timestamp or transcript is fabricated.

## 4. Tests passed/failed

- Entry: local `main` HEAD and freshly queried origin/main equal `{c.HEAD}`. Canonical SHA `{c.STATE_SHA}`, PREPARATION_EXECUTION_AUTHORIZED, 3 events and event #3 `{c.EVENT}` match. Event file SHA identities replayed.
- Both seals: PASS, 280 + 219 payloads plus two manifests = 501 predecessor files, full set/size/SHA replay with no discrepancies.
- Every controlling historical identity, frozen runtime/configuration and semantic enforcement SHA: PASS. The receipt-contract SHA has two identical frozen copies; the provider/plan uniquely names production_receipt_authority_contract.json. The initial discovery assertion was repaired only in the new evidence script; the failure is retained.
- Read-only 641 predecessor scientific/work/native-command replay: PASS_PREDECESSOR_ONLY. Each frozen work item was regenerated, original versus image-corrected pure scientific/transport compilation compared, and native argv validated without execution. 221 SOURCE_INDEPENDENT + 210 BUGGY + 210 FIXED; 583 RESTRICTED / 58 NONE. Both matplotlib blockers preserved. Compilation uses an in-memory synthetic marker, not a receipt.
- Candidate schema/canonicalization checks: {checks['positive']} positive and {checks['negative']} negative PASS, including missing fields, Boolean authority, V1/future-production schema mismatch, malformed security SHA, NONE, extra/raw relabel field, origins, duplicate keys, floats and NaN. These are draft schema/parser tests, not controller/provider authority or E2E tests; no receipt was persisted.
- New evidence scripts: AST parse, Ruff, strict UTF-8/LF/JSON and canonical roundtrip PASS. Source AST inventories include every original/controller and image-corrected provider function; no successor source-equivalence claim is made.
- Full new-source A–X: 0 passed, 0 failed, 24 skipped/NOT_RUN. Inherited 77 rejection categories and 16 new categories: 0 passed, 0 failed, 93 skipped/NOT_RUN. Required source/receipt/claim/terminal and successor scientific replay remain unexecuted. Historical PASS and AST equality are never counted as successor test PASS.
- Partial artifact/hash references and planned dependency DAG: acyclic. Full final seal replay is performed after finalization by `validate_successor_candidate --verify-seal`; exact manifest SHA is reported externally to avoid a self-hash cycle.

## 5. Contract compliance

Transaction remains CANDIDATE_CONSTRUCTION_ONLY. All 1065 tracked files, Git index, HEAD, canonical/event #3, accepted V1 artifacts, frozen runtime/configuration, exact 641 work IDs and ordered population, and real ledger tree are unchanged. Real ledger remains 641 UNSTARTED, 0 claims/terminals/retries/orphans; all six production targets remain absent. Writes are confined to this new namespace. No synthetic output subtree was needed or allocated because source qualification stopped at the unresolved mandatory policy gate.

No original source guard was bypassed, no `__file__`, global or sys.modules substitution, no protected authority constructor workaround, no monkeypatch, no install/activation, no real receipt/claim/terminal/build/solve, no source export/acquisition/materialization, no oracle/allocation/repair, no cleanup, and no Git add/commit/push occurred.

## 6. Risks and unknowns

Unknown exec origin remains ORIGIN_NOT_ESTABLISHED, NOT_PROVEN_BENIGN and NOT_PROVEN_MALICIOUS. The two added historical socket records remain UNRESOLVED. There is no cleanup or exoneration authority. Historical bounded configuration equality does not establish client authorization; historical full Docker inspect equality was FALSE.

Current socket, worker, binaries, routes, complete listener/client census and endpoint ownership/permissions were not freshly observed. No Docker inspection or exec was invoked, so the transaction made no Docker mutation; an actual current live-topology preservation comparison was not performed. `/proc/net/unix` cannot establish endpoint ownership/permissions or initiating host-command authorization. These limitations remain UNVERIFIED and are not promoted to PASS.

The security projection is a typed partial design with unverified mandatory fields and an unresolved policy dependency. No current projection SHA, installed accepted projection SHA or production effectivity SHA exists in this package. V2 receipt/schema and raw-sidecar semantics require independent acceptance and implementation/qualification. Excluding raw diagnostic SHA from immutable receipt bytes is an explicit candidate design to permit transient turnover; separately immutable raw sidecars bind exact receipt SHA/attempt/stage/projection and every original raw SHA. This has not been executed or accepted.

## 7. Recommended next action

Human-PI should decide the exact mandatory active-client authorization rule and admissible complete independent attribution evidence, including treatment of unattributed historic/current clients, and separately authorize any required evidence acquisition. This is the next missing authority, not an acceptance recommendation. Full successor source/qualification construction can resume only after the essential rule is uniquely specified under explicit authority. Installation, acceptance, effectivity, publication and real execution remain separate later gates. STOP at BLOCK.

## Requested A–T evidence

| Item | Outcome / artifact |
| --- | --- |
| A Entry/Human-PI | Exact local/live HEAD and canonical/event verified; direct construction-only decision recorded. |
| B Historical integrity | Every controlling file SHA, 280+219 payload seals and both manifests replayed; preserved. |
| C Stable projection | Typed partial contract; exact image/Engine/OCI/instance/worker/binary/network/proxy/listener invariants; no production projection SHA. |
| D Raw preservation | Complete original raw references plus per-source byte/SHA/method/timestamp rules; missing original metadata stays UNVERIFIABLE. |
| E Diagnostics | Full ExecIDs/order, socket rows/addresses/inodes/turnover retained; listener/security tuples remain mandatory. |
| F Exec authorization | UNKNOWN confers neither authorization nor maliciousness; exact mandatory rule unresolved, production gate BLOCKED. |
| G Freshness | Eleven preclaim steps and independent provider refresh specified as candidate design; no implementation/production claim. |
| H V2 receipts | All R1–R22 reviewed, separate V2 contract/schema, candidate authority false, raw sidecar design, no V1 changes. |
| I Source SHAs | No successor pair constructed; old and corrected predecessor SHAs explicitly bound. |
| J Semantic delta | Full baseline function/AST inventories and corrected seam delta; successor audit NOT_RUN. |
| K Qualification entry | Exact new-path/root mutually exclusive design only; original guards unchanged and no bypass. |
| L A–X | 24/24 accounted for, all NOT_RUN; no full E2E PASS. |
| M Rejections | 77 inherited + 16 new mapped, all NOT_RUN. |
| N 641 replay | Actual precursor comparison/compilation replay PASS; successor projection NOT_RUN. |
| O Installation DAG | Actual partial contracts and planned unconstructed nodes; acyclic, no installation candidate/plan fabricated. |
| P New identities | candidate_identities.json gives actual partial contract/schema SHAs; absent source/installation/pin hashes not invented. |
| Q Seal | artifact_sha256.json full payload paths/sizes/SHAs; external manifest SHA, read-only replay command. |
| R Firewall | All tracked/index/HEAD/predecessor/canonical/ledger/work bytes preserved; targets absent; zero Docker/task mutations; no live topology comparison claimed. |
| S Unknowns | Exact client rule, independent attribution, fresh socket/worker/binary/route/listener/ownership evidence and complete source qualification unresolved. |
| T Next gate | Human-PI exact active-client rule/evidence decision; no review-ready acceptance, install, effectivity, commit/push or real run. |

| Identity | Old | Proposed new |
| --- | --- | --- |
{chr(10).join(identity_lines)}

Recorded at {datetime.now(timezone.utc).isoformat()}. All candidate artifacts remain non-effective.
"""
    (c.HERE / "RUN_REPORT.md").write_text(report, encoding="utf-8")
    # Validate every final report/artifact before writing the manifest last.
    result = validate(False)
    c.write("validation_results.json", result)
    files = {str(path.relative_to(c.HERE)): {"path": str(path), **c.file_record(path)}
             for path in sorted(c.HERE.rglob("*")) if path.is_file() and path.name != "artifact_sha256.json"}
    c.write("artifact_sha256.json", {**c.COMMON, "schema": "V6_BLOCKED_TOPOLOGY_STABILITY_SUCCESSOR_ARTIFACT_SHA256_V1",
            "status": "BLOCKED", "file_count": len(files), "total_payload_size_bytes": sum(x["size_bytes"] for x in files.values()),
            "files": files, "excluded": ["artifact_sha256.json"],
            "self_sha256": "Measured externally by --verify-seal; excluded to avoid self-hash cycle"})
    final = validate(True)
    print(json.dumps({"status": "BLOCKED", "bounded_evidence_validation": final["bounded_evidence_checks"],
                      "file_count": len(files), "manifest_sha256": c.sha((c.HERE / "artifact_sha256.json").read_bytes()),
                      "candidate_schema_tests": {"positive": checks["positive"], "negative": checks["negative"]}}, sort_keys=True))


if __name__ == "__main__":
    main()

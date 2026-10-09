# Run Report — independent exact V6 successor audit

STATUS = `V6_PRODUCTION_RUNTIME_TOPOLOGY_STABILITY_SUCCESSOR_INDEPENDENT_AUDIT_BLOCKED`

The exact sealed candidate is **not eligible for Human-PI acceptance or lifecycle freeze**. Independent review found **2 MATERIAL, 1 MINOR, 0 OPTIONAL** findings. The candidate and all predecessor BLOCK evidence remain unchanged. This audit makes no acceptance, installation, release, scientific-validation or execution decision.

## 1. Task summary and exact identities

Transaction: INDEPENDENT_EXACT_CANDIDATE_AUDIT_ONLY. Current Human-PI review gate: HUMAN_PI_REVIEW_OF_V6_PRODUCTION_RUNTIME_TOPOLOGY_STABILITY_SUCCESSOR_CANDIDATE.

| Artifact | Exact SHA-256 |
|---|---|
| Candidate package manifest, 43 payloads + 1 manifest | `a24c561d6fc68d316908cc62813624f1acb5eff4c93121ae1704938a46a6fec4` |
| Controller | `93696b9a6e6fa7bd3c207c27e0b6c098bd1d68aa8781167edc4c74bc9cc5de41` |
| Provider | `8731a0ab7eb8605201b754c366b601c9f821e5eaa8c2d52204bbcdab8eaf809c` |
| Successor installation candidate | `43cc158cab9d91a50aa8e225e57f74363a0d2f2660c31e1ef00d23ec2485c83d` |
| Successor installation plan | `d4459a2d380ee5cd35107b19b4525750599c850393fbb1002f47014d5323a210` |

Both local HEAD and independently queried live origin/main equal `e492d159daf188323efcfe121aa019d5b098bfb2`. Canonical SHA is `e48580c1f9769d1b93ab995e6dcef3689c6920a9ce7b83f728526e9694dc68fd`, state PREPARATION_EXECUTION_AUTHORIZED, event_count 3. No `.airos/current_state.md` or repository AGENTS.md was present. The attached direct audit request and supplied global rules were applied.

## 2. Files inspected and changed

Read the exact controller/provider/qualifier, V2 security/client/raw/receipt contracts and schemas, original ledger and shared materializer, installation candidate/plan, source deltas, sealed qualification outputs, historical provider/controller references and predecessor manifests. Replayed every payload path, size and SHA for the 44 candidate and 572 predecessor files. Replayed all 613 final external qualification files across 62 fixtures and inspected canonical claim/terminal/receipt/association bytes and artifact hashes. Complete file/AST identities and source diffs are retained in this audit.

All new files are confined to `/Users/wuyangchenxi/errpilot/evaluation/downstream_benchmark/evidence/v6_production_runtime_topology_stability_successor_independent_audit_v1`. Added the requested 15 named outputs plus reproducible audit scripts, exact snapshots, bounded synthetic fixtures, run logs, source diffs and supporting results. No existing candidate/predecessor/tracked file changed. Failed audit-harness revisions and their logs are retained; they are not candidate findings.

## 3. Commands run

Read-only Git HEAD/index/status/diff/file-list checks and `git ls-remote origin refs/heads/main` at entry and exit; bounded file reads, streaming SHA-256 and Python AST comparison. Ran `audit_entry.py`, `audit_checks.py` (three preserved revisions/runs), `audit_additional_checks.py`, `assemble_audit.py`, `audit_receipts.py` and `finalize_audit.py` with `.venv/bin/python -B`. See `commands_run.json` and run logs. No dependency installation, Docker, source acquisition, build, GUI, Git stage/commit/push or topology cleanup was performed.

## 4. Tests and findings

**F01 — MATERIAL: synthetic root confinement fails.** `Authority.__init__/refresh` and downstream guards use lexical `Path.is_relative_to` without rejecting `..`. Normal unchanged candidate constructors accepted an escaped qualification-root spelling resolving inside this audit, outside the mandated qualification root. RESTRICTED/NONE synthetic terminals and failure terminal were durably published there. No module globals, source paths or constructors were forged. This is a filesystem boundary failure; production authorization was not bypassed. Evidence: `isolation_reproduction.json`.

**F02 — MATERIAL: raw socket Path is not bound to attributed endpoint.** `verify_clients` matches connected inode lists but does not reconcile each row's Path with the session/provenance endpoint. Changing connected inode 3697 to `/tmp/unknown-control.sock` while proofs still identify `unix:///run/buildkit/buildkitd.sock` left the accepted security projection unchanged; both controller claim and provider revalidation accepted the contradiction. No unknown listener was added. Evidence: `client_endpoint_correlation_reproduction.json`.

**F03 — MINOR: inherited category semantics are mislabeled.** The `runtime_authority_false` test sets integer `0` in a synthetic V2 receipt which correctly expects Boolean `false`. It therefore tests canonical type distinction rather than the former real-authority Boolean gate. Generic exception capture does not assert the intended reason. Evidence and bounded disposition are in `findings.json`.

Receipt crash-safety disposition: ten requested interruption points and four partial-file write failures retained evidence, rejected reentry and performed no overwrite. Before the lock, a preclaim sidecar directory may coexist with Ledger.state=UNSTARTED, but actual claim reentry rejects. After lock/partial claim or terminal, orphan/parse/partial guards reject. These are bounded code-level injection results; **storage power-loss durability is not established**. The author's sealed qualifier contains no equivalent crash-point injection suite. See `receipt_sidecar_crash_audit.json`.

Receipt checks: canonical original bytes/schema, entire immutable work/attempt/source/effectivity binding, cross-attempt rejection, NONE/null semantics and durable association/claim readback passed; 34 independent negative receipt checks rejected.

Synthetic execution disposition: the original shared `_materialize_checked` code object was traced three times with simulated transport, and legacy globals stayed unchanged. Audit hooks confined resolved writes to this audit and denied all sockets and runtime/source/install subprocesses. Only exact read-only Git queries were allowed. This supports simulated I/O behavior for exercised paths, while **synthetic root isolation fails F01**. These diagnostic E2Es must not be relabeled as successful intended-root isolation qualification.

Both 24-entry A–X mappings and all 126 recorded rejection outcomes (77 inherited + 49 new) were reviewed against actual test source and exact evidence. No mandatory skipped case was observed. Most negative cases have meaningful mutation/rejection/ledger assertions; the complete 126-case author main was not rerun because it writes sealed candidate/external namespaces. The category-name reuse limitation is F03, and F01/F02 are uncovered security cases. Positive retained RESTRICTED/NONE terminals are MATERIALIZED, with 21 artifact hashes each; retained provider failure is INTERRUPTED with `RuntimeError: SYNTHETIC_PROVIDER_FAILURE`. Full qualification acceptance is blocked by material findings.

Independent scientific replay passed all 641 exact work IDs: 221 SOURCE_INDEPENDENT, 210 BUGGY, 210 FIXED; 583 RESTRICTED and 58 NONE. Population file SHA `288eaed9f7e9ff4daf2978e7c41b6c6ead83e9d99b9ddee7801c163153bd63bb`, semantic SHA `f3a719f2a92f1d1ba96baa9dd3936e8bd87d330f048542c9ee5cfce86185a800`, ordered IDs SHA `7a329a4c301e5ddd6bae1047f6bce77430aca5a21d71a7a749dfb3899e4c7a5c`. Full scientific/execution Dockerfile bytes and native argv match historical, corrected and successor implementations for every item. matplotlib::1 and matplotlib::8 remain blocked. No scientific eligibility or environment-ready inference is made.

The 11-node, 10-edge supersession graph and every referenced file identity pass independent acyclic replay. Actual successor controller/provider/candidate/plan pins are exact; historical V1 pins are marked predecessors. candidate_only=true, HUMAN_PI_ACCEPTED=NO, runtime_effective=NO, execute_now=false. Future effectivity remains unconstructed.

## 5. Contract compliance and preservation

All 1065 tracked files, Git index bytes, HEAD, canonical/event chain, exact 572 predecessor files and 44 candidate files are unchanged. Complete persistent output, including the original qualification tree, matches entry: 5059 entries, 3421 files, 20210849828 bytes. All specified production targets are absent. The full persistent ledger remains **641 UNSTARTED, 0 claims, 0 terminals, 0 retries, 0 orphans**. Only synthetic audit-owned attempts exist in the new audit namespace. No real receipt, claim, attempt or execution occurred.

## 6. Risks, assumptions and unknowns

Real-client authorization remains **BLOCKED**. No current Docker topology, live client provenance, live observer or actual host isolation was inspected or certified. Trusted live observer construction and accepted effectivity remain future gates. Fault injection covers selected source-level boundaries, not arbitrary machine power loss. Source/output review establishes the sealed recorded test outcomes; it is not a fresh rerun of every historical rejection. The diagnostic root traversal is an explicit counterexample, never an authorization mechanism for real outputs. Audit harness revisions 1 and 2 failed for fixture ordering and `/dev/null` denial respectively; successful revision 3 and all retained evidence are distinguished.

## 7. Recommended next action

Human-PI should adjudicate F01/F02 and the F03 mapping limitation, then separately authorize a bounded successor remediation/requalification/reseal if desired. Preserve this exact candidate and all predecessor BLOCK packages. No finding was fixed in this transaction. The PASS next gate is not asserted; no acceptance, lifecycle closure, production installation or real execution is authorized by this audit.

`artifact_sha256.json` seals every audit payload path, byte size and SHA, excluding only itself. Its self SHA and exact counts are returned externally after complete replay to avoid a self-reference cycle.

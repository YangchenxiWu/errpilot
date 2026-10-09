# Run Report: exact non-effective acceptance and freeze closure

## 1. Task summary

Human PI directly approved `HUMAN_PI_ACCEPT_V6_REMEDIATED_SUCCESSOR_UNDER_ADOPTED_THREAT_MODEL` with decision `ACCEPT_EXACT_REMEDIATED_SUCCESSOR_FOR_NON_EFFECTIVE_FREEZE`.
The new versioned records accept only the exact existing source/contract baseline
under `CONTROLLED_SINGLE_TRUSTED_OPERATOR`. Source/contract freeze is persisted;
runtime installation and execution effectivity remain NO.

STATUS = V6_REMEDIATED_SUCCESSOR_NON_EFFECTIVE_FREEZE_CLOSURE_READY_FOR_COMMIT
NEXT_GATE = HUMAN_PI_AUTHORIZE_EXACT_FREEZE_COMMIT_AND_PUBLISH

## 2. Files changed

Only new files in `evaluation/downstream_benchmark/evidence/v6_remediated_successor_non_effective_acceptance_freeze_v1/`.
Required outputs: human_pi_acceptance_decision.json, accepted_source_and_contract_pins.json,
accepted_threat_model_binding.json, historical_findings_disposition.json,
non_effective_freeze_record.json, lifecycle_closure.json, predecessor_integrity.json,
preservation_verification.json, closure_validation.json, commands_run.json,
RUN_REPORT.md and artifact_sha256.json.
Additional bounded evidence: raw_user_request.txt, entry_snapshot.json,
entry_verification.json, construct_closure.py, verify_closure.py, draft_readback_verification.json and live_origin_exit.json.
Historical sealed candidate files retain their original candidate_only,
HUMAN_PI_ACCEPTED=NO and execute_now=false snapshots. This subsequent acceptance
record never rewrites or transfers authority to historical snapshots.

Accepted controller SHA-256: `7c097da628d521987dee76dba8689b0dcdd45d286996ce7509c8442bf8f82b10`.
Accepted provider SHA-256: `51f842194fd79bb9519bb6f45281a897c5249bb80558750f4660233c4c0bd438`.
Installation candidate SHA-256: `6f42c9740dea963fb49df7459e7d34c13b8774530c20cf26dd3a9fe7395edb01`.
Installation plan SHA-256: `43fc8823c8c59db7638b873762fde5f47e84aaab140e218a45b259694bfe355e`.
All eight runtime contract identities, capacity contract, threat-model contract,
helper and baseline dependencies are pinned in accepted_source_and_contract_pins.json.
No executable plan was created; the preexisting plan bytes were preserved.

## 3. Commands run

Read-only git status, branch/HEAD, git ls-files, git diff, git check-ignore,
fresh live git ls-remote and Python byte/tree/graph measurements.
Then `python3 -B construct_closure.py prepare`, separate
`python3 -B verify_closure.py --draft`, and `python3 -B construct_closure.py finalize`.
commands_run.json preserves command receipts and exploratory failures.
The final mandatory command is `python3 -B verify_closure.py`: its exact result,
final seal SHA and file count are emitted after sealing, outside the sealed payload
to avoid self-referential evidence. Final user-facing readiness requires its exit 0.

## 4. Tests passed/failed

Entry and preservation: PASS for 1842 physical evidence files (1016 historical,
764 remediated candidate, 38 independent reaudit, 24 threat-model adjudication),
complete manifest path sets/sizes/SHA values, including all 8 ignored .log files.
1065 tracked files and the Git index match the authenticated sealed baseline.
The full external persistent tree (12271 entries / 7510 files), all retained
qualification outputs and canonical state/events are preserved.
Real ledger: 641 UNSTARTED; claims/terminals/locks/retries/orphans all zero.
786 original candidate/plan/version/dependency references were remeasured.
Separate draft readback: PASS (actual receipt in draft_readback_verification.json). All nine final checks are required again by the final sealed verifier.
No new runtime validation, 188 rejection rerun, 641 projection rerun or full E2E
was performed. This evidence packaging does not establish scientific validation.

## 5. Contract compliance

The latest attached Human-PI request is copied byte-for-byte in raw_user_request.txt.
No .airos/current_state.md or separate .airos/contracts/ was present.
Only the exact authorized acceptance closure was constructed. No source edits,
runtime refactoring, security scope expansion, Docker investigation, protocol
changes, production installation, real client authorization, real preparation,
Git staging/commit/push or runtime activation occurred.

## 6. Risks and unknowns

F01 original lexical traversal vulnerability: FIXED, based on preserved scoped evidence.
F02: ACCEPTED_CORRECTED_ENDPOINT_CORRELATION.
F03: ACCEPTED_CORRECTED_BOOLEAN_TYPE_SEMANTICS.
R01: KNOWN_OUT_OF_SCOPE_RESIDUAL_RISK. Precisely excluded: Deliberate adversarial same-UID concurrent directory relocation between successful confinement validation and filesystem operations.
The code is not claimed to prevent that behavior. Ordinary path confinement,
symlink and source-location guards remain in scope and byte-preserved.
R02: ACCEPTED_ADDITIVE_ERRATUM; correct fixture locator `run_4/fixture_76`.
No historical evidence or outcome was rewritten. Historical independent audit
remains BLOCKED; current scoped adjudication remains PASS.
Physical power-loss durability: NOT_ESTABLISHED. Current live production
preconditions were not investigated or established in this closure.

## 7. Recommended next action

Human PI may review the exact final seal and separately authorize
`HUMAN_PI_AUTHORIZE_EXACT_FREEZE_COMMIT_AND_PUBLISH`. This is the next gate, not granted commit/publication authority.
STOP. PRODUCTION_RUNTIME_INSTALLED=NO; RUNTIME_EFFECTIVE=NO;
REAL_CLIENT_AUTHORIZATION=BLOCKED; REAL_PREPARATION_AUTHORIZED=NO.

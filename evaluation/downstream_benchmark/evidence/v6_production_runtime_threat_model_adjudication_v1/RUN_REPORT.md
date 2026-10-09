# Run Report — V6 threat-model adjudication and audit closeout

**CURRENT_SCOPED_ADJUDICATION = PASS**

**STATUS = V6_SUCCESSOR_THREAT_MODEL_ADJUDICATION_READY_FOR_HUMAN_PI_ACCEPTANCE**

This ready status is reportable only after `verify_adjudication.py seal` and a separate `verify` process complete successfully. Their emitted manifest SHA/count identify this exact package without a circular self-hash assertion. Date: 2026-10-08, Europe/Budapest.

The exact existing candidate is eligible for Human-PI acceptance under the expressly adopted threat model. This is an independent recommendation. Candidate acceptance, installation, runtime effectivity and real execution remain separate and unperformed. The historical independent reaudit remains **BLOCKED**.

## 1. Task summary — required A–M results

| Item | Result and evidence |
|---|---|
| A. Human-PI scope decision | Applied `HUMAN_PI_ADJUDICATE_V6_REMEDIATION_REAUDIT_R01_R02` and `ADOPT_CONTROLLED_SINGLE_TRUSTED_OPERATOR_BENCHMARK_THREAT_MODEL_V1`. Exact attached request preserved in `raw_user_request.txt`; authority recorded in `human_pi_threat_model_decision.json`. This accepts a threat-model boundary, not candidate source bytes. |
| B. Exact entry | Local `main`, HEAD and freshly queried live `origin/main` equal `e492d159daf188323efcfe121aa019d5b098bfb2`. Canonical SHA `e48580c1f9769d1b93ab995e6dcef3689c6920a9ce7b83f728526e9694dc68fd`; state `PREPARATION_EXECUTION_AUTHORIZED`; event count 3. Actual event files match their canonical pins. Real ledger: 641 UNSTARTED, zero claims, locks, terminals, retries and orphans. Details: `entry_verification.json`. |
| C. Preservation population | Seven historical packages: **1016 files**; remediated candidate: **764**; independent reaudit: **38**; combined **1818**. Every complete physical path set, file size and SHA matches its seal; modes checked where sealed and fully compared at entry/exit. All eight intentionally ignored historical files included. All **1065 tracked files**, index bytes/mode, HEAD, canonical/events and entire 12,271-entry persistent output tree preserved. See `predecessor_integrity.json`, `entry_snapshot.json`, `preservation_verification.json`. |
| D. R01 | Original severity **MATERIAL** retained. Disposition **OUT_OF_SCOPE_RESIDUAL_RISK** solely for the exact accepted deliberate concurrent relocation scenario. No adversarial-relocation code fix claimed; no historical finding or audit status rewritten. See `R01_scope_adjudication.json`. |
| E. Threat-model boundaries | Controlled single-trusted-operator scientific benchmark of frozen real CLI/Python failure cases. Deliberate adversarial same-UID concurrent directory relocation between successful path validation and subsequent filesystem operations is excluded. This does not require root. Traversal, aliases, symlink manipulation, accidental cross-root writes, wrong-root selection, incorrect writes, identities, once-only semantics, client authorization and network boundaries remain in scope. No general same-UID or host-compromise waiver. See `threat_model_contract.json`. |
| F. In-scope protections | Exact source and sealed independent evidence support original dot-dot rejection, nine lexical/factory rejections, sixteen existing-symlink rejections, three recorded controlled replacements, authorized nested I/O, candidate source/root guards, no-follow traversal and exclusive publication. Receipt/claim/terminal and scientific semantics remain bound. See `in_scope_security_assurance_review.json` and its explicit file/SHA references. |
| G. Future operations | Eight mandatory operational preconditions are documented separately, each explicitly **not currently verified by this transaction**. Any failure blocks production. Historical unknown BuildKit exec origins remain **ORIGIN_NOT_ESTABLISHED**. See `production_operational_preconditions.json`. |
| H. R02 | Additive erratum corrects only `/checks/F01_replace_component_before_open/fixture_root` in the interpretation of the sealed `rejection_matrix.json`: old `run_4`; corrected **`run_4/fixture_76`**. Across all **414** sealed fixture roots, exactly one complete after-inventory matches. Aggregate before/after, raw before/after, trace, original source, all 20 actual fixture entries, absolute symlink target and legitimate nested output agree. Original rejection remains `PASS_REJECTED`, reason `F01 no-follow component refused: mutable`, zero unauthorized claims/builds/artifacts. No rerun or reconstructed result. See `R02_locator_erratum.json`. |
| I. Existing independent qualification | Reused exact independently reviewed F01/F02/F03 and receipt/association evidence; 10 crash + 4 empty-write source-level outcomes; 188 categories (126 inherited + 62 new); both 24-entry A–X maps; 641 independent pure scientific/native projections (221 SOURCE_INDEPENDENT, 210 BUGGY, 210 FIXED; 583 RESTRICTED, 58 NONE). Rechecked all **739** hash references of the **11-node/18-edge** acyclic graph, exact source identities and seven unchanged V2 contracts. No 188-test or 641-projection rerun and no full new E2E execution. See `existing_independent_evidence_review.json`. |
| J. Residual risks | **FULL_ADVERSARIAL_RELOCATION_SAFETY = NOT_ESTABLISHED**. **PHYSICAL_POWER_LOSS_DURABILITY = NOT_ESTABLISHED**. Source-level fault injection does not establish physical power loss, arbitrary prefix persistence or torn-write safety. Live topology, accepted authenticated observer/current clients and future source/receipt/effectivity pins remain separate unverified gates. See `R01_residual_risk_register.json`. |
| K. Recommendation | Exact candidate is eligible for Human-PI acceptance **under the adopted threat model**. `HISTORICAL_INDEPENDENT_AUDIT=BLOCKED`; `CURRENT_SCOPED_ADJUDICATION=PASS`. No automatic acceptance, historical PASS conversion or lifecycle freeze. See `independent_scoped_disposition.json`. |
| L. New seal | `artifact_sha256.json` binds the complete new payload path/size/mode/SHA set, excluding only itself. Its exact self SHA, payload count and physical count are emitted by sealing and independent verification and included in the final handoff. All new text is strict UTF-8/LF; JSON rejects duplicate keys and nonfinite constants. |
| M. Production negative boundary | Candidate-only true; HUMAN_PI_ACCEPTED NO; runtime_effective NO; execute_now false. No Docker command/API/exec/build/cleanup, real ledger write, installation, real attempt, commit or push. Future conditions do not imply current verification. Production execution remains **BLOCKED**. |

Exact candidate identities (unchanged):

| Artifact | SHA256 |
|---|---|
| Controller | `7c097da628d521987dee76dba8689b0dcdd45d286996ce7509c8442bf8f82b10` |
| Provider | `51f842194fd79bb9519bb6f45281a897c5249bb80558750f4660233c4c0bd438` |
| Installation candidate | `6f42c9740dea963fb49df7459e7d34c13b8774530c20cf26dd3a9fe7395edb01` |
| Installation plan | `43fc8823c8c59db7638b873762fde5f47e84aaab140e218a45b259694bfe355e` |
| Candidate manifest | `15161f72e034f4661baa6f2a42dfa649adab4ab33edbb899c3b10d2e3a5a7d15` |
| Independent reaudit manifest | `45c5eafbddb0cebf27b88dbfa86be1085b7f46c76f8d9d5760e53e7dd841f8f8` |

R02's original aggregate file SHA is `2d44550f76223b1878f5d43fbfd60234e74bd1a9ffbac9435390e8fbb003d532`. The raw regression SHA is `25a279507af5542bdc513351bb7cb11933d615735793679a9b6f05387770c357`. The erratum provides all supporting source/output SHAs and complete old/corrected absolute locators.

## 2. Files inspected and changed

Inspected the exact attachment, repository/ancestor governance-file locations, canonical descriptor and event files, nine sealed evidence namespaces, candidate controller/provider/helpers and packaging/regression source, independent R01/R02 findings and primitive probes, raw/aggregated F01 records, all required independent audit results, source/hash graph, candidate/plan, real ledger and sealed persistent/synthetic inventories. No `.airos/current_state.md` or `.airos/contracts/` directory was present.

Only new files under `evaluation/downstream_benchmark/evidence/v6_production_runtime_threat_model_adjudication_v1/` were created. They contain this report, exact request, measurement/reconciliation scripts, entry and exit records, additive decisions/erratum, evidence review, future conditions, command records and seal. The seal is the exact file list. No production, tracked, predecessor, candidate, historical audit or external qualification file was edited. No persistent report was written to `.airos/run_reports/`.

## 3. Commands run

Read-only Git status/branch/HEAD/index/diff/ignore queries; fresh entry/exit `git ls-remote origin refs/heads/main`; bounded source/JSON inspection using `rg`, `sed`, `nl` and Python; `.venv/bin/python -B .../verify_adjudication.py entry`; `.venv/bin/python -B .../adjudicate.py`; final `.../verify_adjudication.py seal` and separate `verify`.

`commands_run.json` records principal tool invocations, failures and scope; `entry_commands.json` and `final_commands.json` record exact Git argv/results generated by the verifier. The initial live query failed due to sandbox DNS, then the explicitly required read-only network retry succeeded. An overbroad read-only governance-file search was interrupted and replaced with exact ancestor/repository locations. No dependencies were installed or GUI opened. No candidate code was imported or executed by the new scripts.

## 4. Tests passed/failed and limitations

New checks passed for complete physical inventories, exact seals, entry baseline, source/input references, graph, R02 unique reconciliation and recorded independent result consistency. Final preservation and seal readback must also pass before this report's ready status is handed off. New Python source is parsed without producing bytecode; new JSON/text receive strict schema-independent parsing and encoding checks.

No runtime suite was newly executed. Historical F01/F02/F03 verifier outcomes, 188-category audit, both A–X mappings, receipt/once-only review, 10 crash/4 partial-write outcomes and 641 independent projections are reused with exact evidence references. Their files, source pins and retained physical outputs were freshly verified. Scientific equivalence is implementation evidence; it is not scientific validation or environment readiness. No mandatory in-scope evidence gap was found in this bounded adjudication.

## 5. Contract compliance

The attached Human-PI request is the controlling bounded contract. This transaction implements only the scope adjudication, independent confirmation and additive locator erratum. All writes stay in the permitted new namespace. No development/remediation cycle, historical revision, candidate acceptance, freeze, commit/publication, installation or real preparation occurred. The older candidate contract's word “privileged” has not been edited or promoted into authority; the latest exact same-UID exclusion governs this scoped assessment.

## 6. Risks and unknowns

R01's kernel/source behavior is preserved: descriptor name verification and a following creation/write/link remain separate. A same-UID process may have sufficient rename permissions; the finding is not disproved. Only the specified deliberate adversarial relocation is excluded. No waiver applies to in-scope accidental path escapes, symlink manipulation, incorrect roots/writes, arbitrary same-UID interference, client authorization or network access.

Future production requires operator ownership, no knowingly untrusted actor manipulating benchmark roots, no concurrent adversarial same-UID directory relocation, exact output-root identity, existing safety checks, accepted source/receipt/effectivity pins, complete C1-C16 current-client authorization and fresh mandatory topology verification. None was certified as a current operational condition here. No live Docker observation was made; zero Docker operations cannot establish that unrelated processes left live Docker state unchanged.

## 7. Recommended next action

**NEXT_GATE = HUMAN_PI_ACCEPT_V6_REMEDIATED_SUCCESSOR_UNDER_ADOPTED_THREAT_MODEL**

Human-PI may review the exact candidate, this additive adjudication and erratum for acceptance under that threat model. This recommendation does not itself accept any candidate or authorize later stages. **STOP after exact sealing and readback.** Historical audit BLOCKED, original R01/R02 findings, candidate-only flags and production boundaries remain intact.

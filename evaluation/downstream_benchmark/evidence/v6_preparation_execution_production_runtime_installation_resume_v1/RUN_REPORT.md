# Run Report — V6 production-runtime installation resume candidate

Date: 2026-10-07 (Europe/Budapest).

`STATUS = V6_PREPARATION_EXECUTION_PRODUCTION_RUNTIME_INSTALLATION_CANDIDATE_READY_FOR_HUMAN_PI_REVIEW`

This transaction constructs a reviewable installation candidate and qualifies its local synthetic controller/provider interfaces. It installs no production source, creates no accepted effectivity pin, consumes no real attempt, and establishes no environment readiness. The prior receipt-contract BLOCK remains preserved as historical evidence.

## Task summary and A–S evidence

| Requirement | Evidence and result |
|---|---|
| A. Entry/predecessors | main, local HEAD and freshly queried live origin/main were exactly `0425059c2c2e306cd48b7739c51dc3cb3688e228`; tracked diff/index clean. Exactly 23 predecessor files (7 run + 16 blocked installation) were enumerated, sized, hashed and their manifests verified before any write. Full inventory follows. No on-disk AGENTS.md or .airos state/contract was found; the supplied global instructions and pasted request govern. |
| B. Human-PI receipt contract | Exact supplied decision text and R1–R22 are retained in human_pi_receipt_authority_decision.json. Adopted semantics grant bounded construction, not production installation or real attempts. production_receipt_authority_contract.json and receipt_contract.json contain identical deterministic bytes because both filenames were explicitly required. |
| C. Canonical receipt | Exact production schema, runtime_authority=true within explicitly isolated synthetic fixtures, full existing work-item record, lexical accepted origins `[files.pythonhosted.org:443,pypi.org:443]`. Existing UTF-8 canonical JSON: sorted keys, compact separators, LF, no floats/NaN/duplicate keys. No token/key/signature/nonce/TTL/expiry. Receipt schema SHA `8a5077220001757af0b4885b9ba5ca23d9bc1adcc7acecb0dc9273647e0ca397`; authority contract SHA `030eebcdfe689cafdb7115a3ec26766c228dd01c4e1bb3ab33f4e9791e96f6d9`. Synthetic receipt SHA in final fixture `8bc7ff4819a7108916f43c2769d93826eea91f4211baef26ed29cf28d37baf27`. No real receipt was issued. |
| D. Live topology contract | Exact daemon runtime, Unix endpoint, container/start/process identity, worker, internal network/participants, proxy instance/network/runtime/source/policy, native/daemon binary identities and local route/socket observations. Deterministic canonical observation hash; local objects must freshly equal the accepted installed payload immediately before claim, and provider reobserves before build. Contract SHA `8ee7bc08d55e8b0c9e628260fed4105e7cd122a9e123f527da37f4776fa96ce4`. No current production topology effectivity claim. |
| E. Architecture/Admission | Committed adapter → Admission → ledger → shared materializer → transport verified. Separate ProductionAdmission inherits the owning Admission interface and revalidates successor authority plus original local source/base checks before the original exclusive claim sequence. No legacy Admission/network guard modified. architecture_resume.md explains the seam. |
| F. Controller | Candidate only under resume namespace; real entry checks exact future installed location and effective independent authority. SHA `bb85d27cd8eefe0a82160657b296d36513ab931cfa97c5954447c0c565c11877`. |
| G. Provider | Separate provider independently verifies durable claim/receipt SHA, exact work semantics and freshly reobserved topology before build; it uses accepted native mechanics and unchanged shared scientific functions. SHA `d466c9310d22754c0c3c9744764bcc402aef988195da7f7aea45b9700eb1de0a`. |
| H. Population | File SHA `288eaed9f7e9ff4daf2978e7c41b6c6ead83e9d99b9ddee7801c163153bd63bb`; semantic SHA `f3a719f2a92f1d1ba96baa9dd3936e8bd87d330f048542c9ee5cfce86185a800`; ordered-ID SHA `7a329a4c301e5ddd6bae1047f6bce77430aca5a21d71a7a749dfb3899e4c7a5c`. 641 = 221 source-independent + 420 revision-specific; 583 restricted + 58 NONE; matplotlib::1 and matplotlib::8 remain outside dispatch. Identity recomputation was only read-only equality verification; no new real identity universe. |
| I. Ledger/receipt claim | Frozen ledger SHA `d64dc5c742d7857e4dcf4f350bc3db4571d679ea9a74a3c4303085ad10bd0dd7`. Embedded ReceiptBoundLedger V1 adds only top-level receipt_sha256 atomically in the original exclusive claim write (also explicit in input_runtime_binding); null on NONE. Original state/immutable terminal methods and fsync/O_EXCL/O_NOFOLLOW helpers inherited. Exact namespace/root/effectivity permit binding tested. Existing real metadata bytes remain exact; the future independent effectivity root is a separate authority. |
| J. Runtime preservation | Frozen runtime SHA `c83da6f5eb355702f994c28efc6b14bc36988a9cc405ff05a689a9f97128f4b6`; config SHA `654299e49b0fc8833f093ecc887b4578970895ce28aa5359b4b37246f7b6190e`; accepted closure SHA `a2a2d8f5fef0357fdad7960f45fad8aa74fdc8bf8728472162c1051a96a10949`. Frozen dispatch/transport/materializer wrapper still reject real use, ONCE_ONLY.real_dispatch remains REJECT. No copied/removed qualification guards and no frozen monkeypatch. All reused helpers are listed and justified in runtime_transport_binding.json. |
| K. Synthetic fixture isolation | Actual fixture lives under `/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1/qualification/production_runtime_installation_resume_v1/run_2/fixture_1/synthetic_effectivity_fixture.json`; SHA `018da591dfaee6d760e10185b34e08d2476702d1c9696bf48a51ea0c1ff4dc22`. It states HUMAN_PI_ACCEPTED=NO and runtime_effective=NO. Only synthetic attempt/case/instance identities are usable. Real CLI exposes no synthetic or injectable provider/authority selector; exact copied source rejects synthetic factories by actual source location. |
| L. Receipt qualification | Deterministic canonical roundtrip/schema/readback passed; issuance left zero claims. Durable restricted claim binds exact bytes SHA; provider exact SHA equality tested using a separately owned corruption fixture. NONE has no receipt and null SHA. Candidate-schema promotion and malformed/duplicate/noncanonical/type-confused receipt bytes reject. |
| M. Controller/provider E2E | All A–X coverage PASS; restricted success, NONE success, one immutable provider-failure terminal, preclaim authority/freshness rejection, duplicate/retry/reuse and isolation checks. 20 rejection cases prove zero preclaim consumption. E2E uses explicit in-process deterministic observation fixtures; no Docker solve was run. Read-only scientific Dockerfile/native argv projection passed for all 641, and six shared scientific code objects remained identical. |
| N. Rejection matrix | 77 PASS_REJECTED. Includes every requested category; operation requests for frozen patch/monkeypatch reject without performing those forbidden mutations. This is not a claim of protection against arbitrary Python process-memory mutation. Command checks are local compiler/validator checks, not public-network probes. |
| O. Installation candidate | candidate_only=true, HUMAN_PI_ACCEPTED=NO, runtime_effective=NO. Exact source/contracts/qualification/transport/population/ledger identities bound. SHA `83ea48b5c4ce7835a46bb6e2207e1893d430b8147b3efa35d4535c0bff08efad`. Candidate excludes downstream plan/report/result hashes to keep the graph acyclic. |
| P. Installation plan | Exact future controller/provider paths match screening conventions; versioned adapter is inside provider, so no additional live ledger file target. Receipt contract, Human-PI authority, final payload and independent accepted pin are separately future-only targets. All 13 requested future steps retained; plan execute_now=false. SHA `de3923da16b4a4ee9b64945baa998a9eba05ca08f0eff92fbe1b2c628a410fbd`. |
| Q. Artifact inventory | 26 new files in this namespace; complete SHA/size seal in artifact_sha256.json (self excluded). External manifest binds 368 qualification files, including both retained runs and source snapshots/copies. Final source bytes are those tested in run_2. |
| R. Preservation/firewall | All 23 predecessors and 1,015 tracked files unchanged; canonical SHA `e48580c1f9769d1b93ab995e6dcef3689c6920a9ce7b83f728526e9694dc68fd`, event_count=3; real tree SHA `d67390175c714245d0f288b9b13c75f2f5082d19182bc45c4b01828800944ec0`. Real ledger remains 641 UNSTARTED, zero claims/terminals/retries/orphans. Every production/execution/publication firewall value is below. |
| S. Next gate | `HUMAN_PI_REVIEW_OF_V6_PREPARATION_EXECUTION_PRODUCTION_RUNTIME_INSTALLATION_CANDIDATE`. Review is a recommendation, not Human-PI acceptance. Stop after construction/seal verification. |

## Exact 23 predecessor files

| Path relative to evidence/ | Bytes | SHA-256 |
|---|---:|---|
| v6_preparation_execution_production_runtime_installation_v1/RUN_REPORT.md | 14999 | `73c4a66ab86a010b3ed144a63317ce1d111915eb5909cf6abadad81bc240b0c5` |
| v6_preparation_execution_production_runtime_installation_v1/architecture_analysis.md | 5493 | `ac44b2394e2216288b22e9e3559fad77504c16fe8c064a3c7761d2a2b148cf17` |
| v6_preparation_execution_production_runtime_installation_v1/artifact_sha256.json | 2486 | `5a1e152f3500c626a72a6ec152571ba5ae65dacc3d2492173dc29db187cb3f2e` |
| v6_preparation_execution_production_runtime_installation_v1/blocked_run_predecessor_binding.json | 1683 | `1c9cd3ee1558ac9254ec67280ffd24fa81099dfe7607393e85f018de955b8d26` |
| v6_preparation_execution_production_runtime_installation_v1/commands_run.json | 2561 | `ac24ffa9728063846ecd4227b8c7b1e9a32db0314c4f7249f8bf392f1a286702` |
| v6_preparation_execution_production_runtime_installation_v1/entry_verification.json | 8969 | `2b53b1d5e3e60ab7c2740382cd52305dedb10fc31afd0a95d3dacecd02339eb4` |
| v6_preparation_execution_production_runtime_installation_v1/human_pi_decision.json | 1024 | `d1c514a61d3b193f31de6e2432f213f865593804279e54dd04773e914720d1e0` |
| v6_preparation_execution_production_runtime_installation_v1/ledger_binding.json | 1789 | `e5766ef872d1720fcc4c5a764deaebe9462dacee40f598e9610750f47dc887e4` |
| v6_preparation_execution_production_runtime_installation_v1/population_binding.json | 1454 | `7d315d8de28c52f1ba27262e38a8857df9bf0edadf298570936f29896a7e3ffd` |
| v6_preparation_execution_production_runtime_installation_v1/preservation_verification.json | 2168 | `e32b7d3e08de5f97366d0f54476cdb5339127f13aa2fb7131eb58cdb8de7b9b7` |
| v6_preparation_execution_production_runtime_installation_v1/receipt_contract_analysis.json | 3019 | `de60ef70745cce5b73ce24b37d4c73b8585f0a264e046ea19668ed712b4f7fe3` |
| v6_preparation_execution_production_runtime_installation_v1/rejection_matrix.json | 13684 | `dabc400459d7faaf7e340b5b49e050d3194c9340bc75ca705c18b6f2e6ffc987` |
| v6_preparation_execution_production_runtime_installation_v1/runtime_transport_binding.json | 2976 | `4a84db13baa92aefc553f890f269d7df1c8b72e9fb92226d0a9cb99492b2499b` |
| v6_preparation_execution_production_runtime_installation_v1/synthetic_qualification_results.json | 635 | `b7e04be406ddc2c49d1e65d3ea504fe93a11ae855723a7e629aba4e92fe8357e` |
| v6_preparation_execution_production_runtime_installation_v1/validate_installation_candidate.py | 13877 | `18294cace1d3d74d1542aadfd986eade6b4ce8cf62926873fda6cc62c95172d3` |
| v6_preparation_execution_production_runtime_installation_v1/validation_results.json | 4239 | `1bf78212b666ef17d995423c1bf2d5a02c7b057f084fb93fb1e5e767d3ec6b6e` |
| v6_preparation_execution_run_v1/RUN_REPORT.md | 11539 | `0cea7f732d8c1b87589442ce3ce320be54715599e2487ce1b44293bda8e10cba` |
| v6_preparation_execution_run_v1/artifact_sha256.json | 757 | `b8415b70ba127849962d4e9a8c6add4342b584d58391b17f087baf2ef10aa722` |
| v6_preparation_execution_run_v1/entry_observations.json | 1466 | `9bf19f68a2b0ef83600a71d337ae568492b4bf00d98ffa673ebafd124a9fce10` |
| v6_preparation_execution_run_v1/entry_validation.json | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| v6_preparation_execution_run_v1/entry_validation_v2.json | 7190 | `b0445f6f86d9315a1de0812c7713db747efc7a75c49bd21830ffb008611c6a03` |
| v6_preparation_execution_run_v1/failed_check_observations.json | 1480 | `40ff5b67a40052e30d0683c96a8df6452f7e78216e53a055d4f3255465f96be9` |
| v6_preparation_execution_run_v1/validate_entry.py | 12577 | `d8401194d80ac0b34b02fd288eed3714090cc9002cd3907ac1cd72e0123b2aed` |

## Files changed

Only the new resume namespace contains repository additions. All are untracked; nothing was staged. The external qualification root contains only this transaction’s synthetic objects/evidence. Bounded construction/output scratch files are under /private/tmp. No preexisting evidence was edited or relocated.

| New artifact | Purpose |
|---|---|
| RUN_REPORT.md | This full run report; bound by the seal |
| architecture_resume.md | Exact candidate/evidence artifact; identity in the seal |
| artifact_sha256.json | Complete package SHA/byte-size seal, excluding itself |
| commands_run.json | Exact candidate/evidence artifact; identity in the seal |
| effectivity_pin_payload_candidate.json | Exact candidate/evidence artifact; identity in the seal |
| external_artifact_sha256.json | Exact candidate/evidence artifact; identity in the seal |
| human_pi_receipt_authority_decision.json | Exact candidate/evidence artifact; identity in the seal |
| installation_plan.json | Exact candidate/evidence artifact; identity in the seal |
| ledger_binding.json | Exact candidate/evidence artifact; identity in the seal |
| population_binding.json | Exact candidate/evidence artifact; identity in the seal |
| predecessor_evidence_binding.json | Exact candidate/evidence artifact; identity in the seal |
| preservation_verification.json | Exact candidate/evidence artifact; identity in the seal |
| production_controller_candidate.py | Exact candidate/evidence artifact; identity in the seal |
| production_provider_candidate.py | Exact candidate/evidence artifact; identity in the seal |
| production_receipt_authority_contract.json | Exact candidate/evidence artifact; identity in the seal |
| production_runtime_installation_candidate.json | Exact candidate/evidence artifact; identity in the seal |
| qualify_resume_candidate.py | Exact candidate/evidence artifact; identity in the seal |
| receipt_contract.json | Exact candidate/evidence artifact; identity in the seal |
| receipt_schema.json | Exact candidate/evidence artifact; identity in the seal |
| rejection_matrix.json | Exact candidate/evidence artifact; identity in the seal |
| runtime_transport_binding.json | Exact candidate/evidence artifact; identity in the seal |
| synthetic_effectivity_fixture.json | Exact candidate/evidence artifact; identity in the seal |
| synthetic_qualification_results.json | Exact candidate/evidence artifact; identity in the seal |
| topology_observation_contract.json | Exact candidate/evidence artifact; identity in the seal |
| validate_resume_candidate.py | Exact candidate/evidence artifact; identity in the seal |
| validation_results.json | Exact candidate/evidence artifact; identity in the seal |

## Commands run and tests

commands_run.json records the inspection/construction/qualification/validation commands and corrected initial failures. Live Git identity used read-only escalation after sandbox DNS failure. External synthetic qualification used scoped escalation because its expressly requested path is outside the workspace sandbox. No dependency was installed.

Passed: existing-venv synthetic qualifier run_2 (8 assertion groups, 77 rejections, A–X coverage, 641 scientific/native projections); AST parsing; receipt JSON schema/readback; Ruff; git diff/index whitespace checks; read-only package/preservation validator. Final --verify-seal checks the exact complete inventory without rerunning or mutating synthetic fixtures. run_1 also passed at its then-tested source bytes (72 rejections); those source copies/results remain preserved rather than being reinterpreted as final-byte qualification.

The initial system Python import, manifest-wrapper parser, sandbox external mkdir, six lint style violations and full-vs-projected semantic-map comparison failed during construction and were corrected. They are not reported as passing commands. Final qualifier, lint and validator succeeded.

## Contract compliance and execution firewall

The supplied R1–R22 and bounded construction request are the authority. No tracked or production target file was changed. No real authority/effectivity was created. No historical BLOCK was rewritten. The sole claim-record extension is receipt SHA binding; inherited once-only durability/terminal semantics remain exact.

| Firewall | Value |
|---|---|
| GIT_STAGE | NO |
| GIT_COMMIT | NO |
| GIT_PUSH | NO |
| PRODUCTION_RUNTIME_INSTALLED | NO |
| REAL_PRODUCTION_ENTRY_EFFECTIVE | NO |
| REAL_PREPARATION_ATTEMPTS_CONSUMED | 0 |
| REAL_CLAIMS_CREATED | 0 |
| REAL_TERMINALS_CREATED | 0 |
| REAL_BUILDS_EXECUTED | 0 |
| REAL_LEDGER_MUTATION | NO |
| ENVIRONMENT_READY_CASES_ESTABLISHED | 0 |
| SOURCE_ACQUISITION_EXECUTED | NO |
| ORACLE_EXECUTED | NO |
| ALLOCATION_EXECUTED | NO |
| DOWNSTREAM_REPAIR_EXECUTED | NO |

## Assumptions, risks and unknowns

- Candidate synthetic interfaces qualify control flow and receipt/durability contracts with deterministic local observations. They do not establish that a production native build currently succeeds.
- No current daemon/proxy/network/firewall, seven OCI contents or source commit/blob presence was operationally qualified. The later installed controller/provider must observe and validate these local identities, and fail closed on mismatch.
- Historical 2/2 TLS qualification remains frozen evidence; no public-network requalification or benchmark dependency installation occurred.
- Future installation must explicitly accept the candidate, installed exact source hashes, new live topology/base bindings, versioned claim contract and independent effectivity pin, and run post-install synthetic qualification. This transaction cannot decide installation, release, merge, readiness or real execution.

Recommended next action: Human-PI review the exact sealed candidate package at the specified next gate. No lifecycle closure, commit, publication or execution follows automatically.

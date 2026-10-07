# Run Report — V6 restricted build-egress compatibility audit

Date: 2026-10-06, Europe/Budapest.

Status: **V6_RESTRICTED_BUILD_EGRESS_SHARED_ENGINE_COMPATIBILITY_BLOCKED**.

## 1. Task summary — entry, accepted decision and compatibility

The accepted Human-PI decision is `ADOPT_V6_INTERNAL_NETWORK_ALLOWLIST_PROXY_EGRESS_V1`, under `HUMAN_PI_DECIDE_V6_RESTRICTED_BUILD_EGRESS_ENFORCEMENT`. Its exact request-file hash and E1–E13 boundaries are recorded in `accepted_decision.json`. This transaction inspected and qualified the existing-engine compatibility prerequisite. The prerequisite failed, so sections 5–14 topology, proxy, connectivity and runtime integration were not executed. No alternate builder was substituted.

Initial and final local HEAD and measured live `origin/main` were `5c007fbfbfc5b3529105a14f87127f50e1eab6d7`, on local branch `main`. Tracked worktree and index were clean at entry and remained clean. The canonical descriptor file SHA remained `6a9028c79aa62f90db2b2d53def32ab23bffcfa3c71d2ec30d7fa64e741e3aae`, with `PREPARATION_PLANNING_AUTHORIZED`, event_count 2, planning YES, preparation execution NO and preparation authorized NO. The canonical 433 cases remained unstarted. `.airos/current_state.md` and repository AGENTS.md were absent; the user-supplied global rules and transaction governed the audit.

The initial untracked population was exactly the saved 14-file activation inventory plus the saved 26-file runtime inventory, including the runtime files outside its evidence directory. All 40 file hashes matched; no unrelated untracked file was present. Activation manifest SHA: `e5470a6dd48350717008350d9bc665f902ad41e747925ec892b3bd86c60466f8`. Runtime manifest SHA: `e1266b88dc5e4fb4f661947b4ad90caed752a440906b0d974384b508c7108025`. All 40 bytes and the Git index bytes were preserved.

The shared production invocation, from `screening/materializer.py:1005`, is:

```text
docker build --platform=linux/amd64 --network=default --progress=plain --no-cache
  -t <frozen-image-tag> -f <accepted-context>/Dockerfile <accepted-context>
```

The 58 network-NONE items instead select `--network=none`. `docker()` calls `subprocess.run` with an inherited environment and no builder override. No DOCKER_BUILDKIT, BUILDX_BUILDER, DOCKER_CONTEXT or DOCKER_HOST override was present. Shared materializer file SHA: `98ba9a45b6b9beaaf00119efe0da07f5513a1d56578d00a5a2dc59cc088dea0c`. The shared Dockerfile generator provides no explicit proxy/application binding.

The installed `docker build --help` identifies the Buildx build frontend. Docker client/server are 29.4.1; Docker Desktop is 4.71.0. The selected `desktop-linux` builder has driver `docker`, BuildKit v0.29.0, containerd executor and daemon-managed worker network `host`. These are measured local observations, not assumptions about classic Docker or another Buildx driver.

A scratch-only parser check used the same installed `docker build` frontend with the required deterministic named network, production platform/progress/no-cache flags and `--call=check`. Its Dockerfile was exactly `FROM scratch` with one LF: no RUN, external source, source export, dependency or image output. It exited 1 with:

```text
ERROR: failed to build: network mode "errpilot-v6-egress-42393faa3385-v1-internal" not supported by buildkit - you can define a custom network for your builder using the network driver-opt in buildx create
```

Classification: **REQUIRES_BUILDER_ARCHITECTURE_CHANGE**. The existing build frontend rejects the required named internal Docker network. A `docker run` client attached to that network would test a different networking mechanism. Creating/selecting a different builder, switching to legacy builder semantics or changing daemon/default-network policy is outside this authority. E9 does not authorize a builder change; E6/E7 prohibit global firewall and daemon-wide changes. Compatibility analysis records the exact source assignment, invocation, binary hash, backend identity and parser stdout/stderr hashes.

## 2. Files changed — topology, identities and inventories

Only this new repository evidence directory was authored. No accepted activation, runtime candidate, shared engine, canonical state or other tracked file was changed. Therefore runtime before/after hashes are identical and are listed in `entry_verification.json`; there is no production integration diff.

| Requested result | Recorded outcome |
| --- | --- |
| Exact Docker topology | NOT_PROVISIONED; internal/external networks, proxy and fixture absent |
| Deterministic stem | `errpilot-v6-egress-42393faa3385-v1` |
| Existing-name inspection | No collisions with planned internal, external, proxy, client, fixture or builder names |
| Internal network / route proof | NOT_RUN; no `Internal=true` object or build-side namespace was provisioned |
| Proxy implementation path / SHA | ABSENT / ABSENT; explicit status file replaces an unimplemented source artifact |
| Allowlist policy file SHA | `f53991bcb3af4005ded1bcd93db1a2f636a588ba2aa007d99160646f20254759` |
| Effective application binding | ABSENT; planned exact pip index/TLS requirements are recorded, not applied |
| Semantic enforcement identity / SHA | ABSENT / ABSENT |
| Blocked qualification observation SHA | `7e5abe84b3dca4c092cc71195ba30dffaac41d0a11fcef6336f2388774656710` |
| Runtime restricted dispatch | REJECT, with no integration changes |

The allowlist file is a planned policy record, not installed enforcement. The observation identity hashes immutable audit records, including a frozen `validation_prepublication.json`; final validation is recorded separately. Transient Docker IDs appear only in operational observations, never in work-item or semantic enforcement identity. No successful enforcement identity was manufactured.

The exact ordered 583 restricted IDs were copied unchanged from the accepted authority candidate's `exact_network_work_item_ids`. Its BUILD_NETWORK semantic SHA revalidated as `42393faa33851396fd70557558fa0e538f817fbee9072d0d56ec9d9323fc21a1`. The current selector's complete 641-item population was compared to the accepted population, without selecting a different subset. The remaining 58 IDs preserve their population order and network NONE status. `work_item_scope.json` binds both lists, the accepted authority bytes and the two non-dispatchable matplotlib blockers. Neither blocker was dispatched.

Repository inventory, including the self-excluded `artifact_sha256.json`, is 29 new files:

| File | Purpose |
| --- | --- |
| `accepted_decision.json` | Exact request/decision and boundaries |
| `entry_verification.json` | Pinned entry, accepted 40-file hashes and canonical gates |
| `compatibility_analysis.json` | Production source, effective argv, backend and parser rejection |
| `audit_compatibility.py` | Reproducible bounded audit source |
| `base_runtime_revalidation.json` | Seven local base and executable identity probes |
| `work_item_scope.json` | Exact accepted 583/58 ordered binding |
| `allowlist_policy.json` | Unimplemented planned allowlist/application policy |
| `proxy_implementation_status.json` | Explicit absent proxy/source/hash |
| `topology_identity.json` | Planned names and absent topology |
| `positive_qualification.json` | Both approved origins explicitly NOT_RUN |
| `negative_qualification.json` | Proxy/fixture/route probes explicitly NOT_RUN |
| `network_enforcement_identity.json` | Absent enforcement and hashed blocked observations |
| `qualification_results.json` | Blocked classification, firewall and next gate |
| `docker_state_before.json` | Before Docker/configuration observations |
| `docker_state_after.json` | After Docker/configuration observations |
| `global_state_preservation.json` | Comparisons and observation limitations |
| `cleanup_verification.json` | Transient client/context cleanup |
| `attempt_state_observations.json` | Empty real claims/terminals and absent attempt artifacts |
| `commands_run.json` | Exact audit subprocess argv/results and stream hashes |
| `focused_tests.txt` | Recorded tool result for six existing runtime tests |
| `rejection_matrix.json` | All 26 requested classes with bounded result labels |
| `validate_evidence.py` | Offline scope, gates, static and artifact validation |
| `validation_prepublication.json` | Frozen observation-bound preliminary validation |
| `validation_results.json` | Final offline validation |
| `persist_external_evidence.py` | Exclusive publication to accepted non-attempt namespace |
| `external_evidence_manifest.json` | Measured external inventory and manifest hash |
| `final_verification.json` | Final entry/artifact/namespace preservation |
| `RUN_REPORT.md` | This report |
| `artifact_sha256.json` | Exact new repository artifact hashes; self hash excluded |

External evidence is stored only at `/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1/qualification/restricted_build_egress_v1`. It contains 22 frozen audit artifacts plus its manifest, 23 files total. The exact filenames, sizes and measured hashes are in `external_evidence_manifest.json`. External manifest SHA: `41583ddf7927d7910259da60313b0440a04601d43fcc1546597cb40ec9e406b9`. Files were created exclusively, flushed/fsynced, and read back; the target directory was fsynced. No real attempt ID is used as this namespace, and no real claim file was created. Final repository validation checks all external bytes against the frozen repository sources. The final report/validation need not be mistaken for the frozen prepublication snapshot.

## 3. Commands run

Principal commands and additional bounded reads:

- Read the exact pasted attachment; inspect required local instruction/state paths, saved artifact manifests, authority, population, runtime/source files and previous qualification conclusions with Python, rg and sed.
- `git status --porcelain=v1 --untracked-files=all`, `git ls-files --others --exclude-standard`, `git rev-parse HEAD`, `git branch --show-current`, tracked/index diffs and `git ls-remote --exit-code origin refs/heads/main`. The required live GitHub origin request is an authorized entry/publication check, separate from egress qualification traffic.
- Read-only Docker version, builder inspection, build help, network/container/image listing/inspection and before/after snapshots. Exact argv and hashes are in `commands_run.json`.
- Seven sequential `docker run --rm --pull=never --name errpilot-v6-egress-42393faa3385-v1-client --platform=linux/amd64 --network=none --read-only --tmpfs /tmp ... python -c ...` executable identity probes, with a deterministic qualification label.
- The single scratch-only `docker build ... --network=errpilot-v6-egress-42393faa3385-v1-internal --call=check ...` parser check. No build output was produced.
- Read-only application firewall state, PF rule query and hashes of known firewall/Docker configuration files. No credentials or unrelated container environment were persisted.
- `.venv/bin/python -B -m unittest evaluation.downstream_benchmark.tests.test_v6_preparation_runtime.RuntimeTests -v`.
- `.venv/bin/python -B` execution of the audit, offline validator, exclusive external publisher, and bounded JSON/report/inventory construction.
- `ruff check --no-cache` on the three existing runtime modules, existing runtime test and all three new evidence scripts; AST parsing, strict JSON/UTF-8 checks; `git diff --check`.

Initial sandboxed live-origin/Docker observations could not access DNS/socket and succeeded with authorized escalated access. Initial system Python lacked jsonschema; the existing `.venv` resolved that without installation. The first offline validator mistakenly classified `docker build --help` as a build probe; its read-only help exception was corrected before final validation. A parent-level AGENTS filename search was interrupted; no unrelated file contents were read from that search. These failed preliminary commands are not reported as passes.

## 4. Tests passed/failed — qualification and rejection matrix

Seven of seven frozen images were LOCAL_PRESENT and matched their saved image ID, digest/platform/layers and exact Python executable probes. Exact image references and Python versions, executable paths and hashes are recorded in `base_runtime_revalidation.json`. No pull or substitution occurred.

Six existing focused RuntimeTests passed: all 641 projected identities, exact selectors and blockers, separate authorities, recipe/revision rejection, guarded no-network/no-pull transport and default-deny dispatch. Saved durable once-only ledger qualification remained hash-bound and PASS; actual-filesystem ledger tests and synthetic materialization were not rerun in this egress transaction.

Additional offline checks passed: 583 restricted items each rejected eight absent/forged receipts, totaling 4,664 rejections; all 58 network-NONE items rejected an enforcement receipt while retaining None; eight forbidden transport forms rejected before Docker. Real dispatch rejected before both Docker and ledger claim. Source-acquisition and oracle policy changes rejected. These establish existing blanket/default-dispatch gates only, not proxy policy parsing, TLS binding, namespace isolation or direct-egress impossibility.

Positive qualification: pypi.org NOT_RUN; files.pythonhosted.org NOT_RUN; 0/2 approved origins demonstrated. Negative qualification: CONNECT parser/denial-before-DNS probes NOT_RUN; external-only local fixture NOT_CREATED; direct fixture connection NOT_RUN; proxy logs ABSENT; route/interface inspection NOT_RUN. No unapproved live destination was contacted. Parser rejection is the expected compatibility-test observation, not a successful enforcement qualification.

All 26 requested rejection classes are present in `rejection_matrix.json`. Unimplemented proxy/application/fixture probes are NOT_RUN; general runtime blanket rejections and prohibited actions not executed have distinct labels. No complete rejection-matrix PASS is claimed. Final Ruff, AST/static checks, strict JSON/UTF-8/LF/BOM/NUL/whitespace checks, artifact/observation/external hash checks and `git diff --check` passed, as recorded by final validation. Initial import/validator errors were corrected as described above.

## 5. Contract compliance — state preservation, cleanup and firewall

The section 4-before-5 prerequisite was enforced. No topology, proxy, synthetic alternate builder or runtime integration was used to bypass it. No scientific recipe/setup semantics, accepted work identity, allowlist or source policy was changed. No dependency/tool installation, host firewall mutation, Docker daemon-wide mutation, default-bridge policy mutation or unrelated object deletion occurred.

Before/after full network observations, unrelated container inspect hashes/selected state, and image inventories matched. Default bridge inspect JSON matched. Readable host PF/Docker settings configuration hashes and application firewall observations matched. Host PF runtime rules could not be read without privileged PF access; Docker's VM daemon configuration was not directly read. Therefore comprehensive global-state proof is limited to observed surfaces and the exact no-mutation command inventory; it is not represented as full enforcement qualification.

Each of the seven named identity clients was removed by `--rm`; the scratch parser context was removed by TemporaryDirectory. No qualification network, proxy, external fixture or builder was created. Final network/container/image inventories showed no remaining transaction Docker resource and no unrelated deletion. Persistent qualification evidence was retained by design.

| Firewall field | Result |
| --- | --- |
| REAL_BENCHMARK_ATTEMPTS_CONSUMED | 0 |
| REAL_BENCHMARK_SOURCE_EXPORTS | 0 |
| SOURCE_ACQUISITION_EXECUTED | NO |
| REAL_BENCHMARK_IMAGE_BUILDS | 0 |
| BENCHMARK_DEPENDENCIES_INSTALLED | 0 |
| UNAPPROVED_LIVE_EGRESS_REQUESTS | 0 |
| ORACLE_EXECUTED | NO |
| EVENT_3_CREATED | NO |
| CANONICAL_CURRENT_STATE_MODIFIED | NO |
| PREPARATION_EXECUTION_CANONICAL_EFFECTIVE | NO |
| GIT_STAGE / GIT_COMMIT / GIT_PUSH | NO / NO / NO |

## 6. Risks and unknowns — unresolved prerequisite

The accepted internal-network/dual-homed-proxy enforcement has not been implemented, provisioned or qualified. The current builder cannot consume the required named network through the existing build frontend. A separate compatibility bridge decision is needed before implementation continues. No builder architecture, legacy-builder mode, daemon-wide policy, application-index override or alternate destination was automatically authorized. A future authorized bridge still requires all topology, CONNECT parser, local negative fixture, approved-origin TLS/HTTP, application binding and no-global-mutation checks.

Actual filesystem ledger tests and source revalidation were bound to the unchanged saved candidate rather than rerun. Complete host PF/daemon VM configuration inspection remains unavailable. No scientific validation, benchmark environment readiness, event #3 readiness, execution effectivity or release decision follows from this audit.

## 7. Recommended next action / next gate

`NEXT_GATE = HUMAN_PI_DECIDE_V6_RESTRICTED_BUILD_EGRESS_COMPATIBILITY_BRIDGE`.

Human-PI should decide an exact bounded production networking/builder compatibility bridge while retaining the internal-network allowlist policy and all other authority boundaries. This is a recommendation and pending gate, not an architecture or research-owner decision. Stop here; real dispatch remains REJECT.

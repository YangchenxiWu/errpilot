# Run Report — V6 dedicated-builder compatibility bridge

Date: 2026-10-06, Europe/Budapest.

Status: **V6_RESTRICTED_BUILD_EGRESS_BRIDGE_BUILDKIT_RUNTIME_MISSING**.

## 1. Task summary — A through R

The accepted Human-PI decision is `ADOPT_V6_DEDICATED_DOCKER_CONTAINER_BUILDER_COMPATIBILITY_BRIDGE_V1`, under `HUMAN_PI_DECIDE_V6_RESTRICTED_BUILD_EGRESS_COMPATIBILITY_BRIDGE`. The exact attachment bytes, SHA-256 and all C1–C17 boundaries are bound in `accepted_decision.json`. This transaction reached the section 3 runtime prerequisite and stopped dependent qualification when the exact runtime image was absent. It completed independent preservation and mechanics checks. It did not qualify a bridge or integrate production changes.

| Requested result | Observed outcome and evidence |
| --- | --- |
| A. Entry | Local `main`, entry and final HEAD/live `origin/main`: `5c007fbfbfc5b3529105a14f87127f50e1eab6d7`. Exactly 14 activation + 26 runtime + 29 prior-audit untracked files; every manifest-bound hash passed before the first new write. Tracked worktree/index clean. Canonical descriptor SHA `6a9028c79aa62f90db2b2d53def32ab23bffcfa3c71d2ec30d7fa64e741e3aae`; planning authorized, event_count 2, preparation execution NO. `.airos/current_state.md`, `.airos/contracts/` and repository AGENTS.md absent. |
| B. Bridge architecture | Dedicated `docker-container` architecture recorded as a plan only. No builder, network, proxy or fixture was provisioned because C11/section 3 failed. Prior `REQUIRES_BUILDER_ARCHITECTURE_CHANGE` finding and shared materializer bytes were revalidated; the rejected named `docker build --network` design was not rerun. |
| C. Exact builder identity/configuration | Planned name `errpilot-v6-builder-42393faa3385-v1`, V6-only scope, `--driver=docker-container`, `--driver-opt=network=errpilot-v6-egress-42393faa3385-v1-internal`, explicit runtime image option below. No `--use`, global selection or bootstrap. Actual container identity, routes, interfaces and driver runtime configuration ABSENT/NOT_RUN. |
| D. Local/no-pull runtime | Installed Buildx `v0.33.0-desktop.1`, commit `7f91f038ac14cbf5c4b2a6b76470860814424da1`. Its binary contains `moby/buildkit:buildx-stable-1` at offsets 24287014 and 24408245; the plan explicitly binds `--driver-opt=image=moby/buildkit:buildx-stable-1`. Local `docker image inspect` returned exit 1, `No such image`. No named BuildKit image appeared in the complete Engine inventory. Runtime image ID and dedicated worker BuildKit version are unobserved. Pulls 0. Existing Desktop worker v0.29.0 was not substituted for a container runtime image. |
| E. Seven frozen bases | All seven exact `docker.io/library/python@sha256:...` references passed fresh Engine image identity and network-NONE Python executable probes (3.6.9, 3.7.0, 3.7.3, 3.7.4, 3.7.7, 3.8.1, 3.8.3). First synthetic bridge build NOT_RUN; 0/7 bridge bases qualified; all-seven offline consumption NOT_DETERMINED. Engine presence does not establish bridge consumption. No registry access, pull, FROM rewrite, registry/OCI/import substitution or retagging was attempted. |
| F. Output/load parity | NOT_RUN: no worker or synthetic bridge output exists. Exact tag visibility, image-ID observation and subsequent frozen identity probe against loaded output are unqualified. No materializer evidence semantics were changed. |
| G. Dockerfile delta | Planned transport-only `ARG PIP_INDEX_URL` recorded separately in `dockerfile_transport_delta.json`; not applied. No execution Dockerfile identities were derived, no frozen recipe bytes/setup order changed, and no byte-identical Dockerfile equivalence is claimed. |
| H. Proxy/application binding | Planned predefined HTTP_PROXY/HTTPS_PROXY args reference `errpilot-v6-egress-42393faa3385-v1-proxy:3128`; planned pip index exactly `https://pypi.org/simple`. Network-NONE args remain empty. No proxy/application binding was implemented or proven inside RUN; no trusted-host, extra index, TLS-disable flag or client-global proxy configuration was introduced. |
| I. Positive/negative networking | Approved origins 0/2 NOT_RUN. CONNECT allowlist/parser, reject-before-DNS, external-only fixture, default RUN proxy access/direct isolation and NONE RUN proxy denial all NOT_RUN. No live qualification origin was contacted. Required GitHub origin reads are separately authorized repository entry/preservation checks. |
| J. Enforcement/bridge identity | Semantic enforcement identity and SHA ABSENT. A distinct hashed **blocked qualification observation** binds five immutable gate records; it is not a qualified enforcement identity. Bridge architecture NOT_QUALIFIED. |
| K. 641/583/58 | Full freshly derived 641-item population equals the accepted runtime population. Exact ordered 583 restricted IDs equal accepted BUILD_NETWORK scope; remaining 58 retain NONE. `matplotlib::1` and `matplotlib::8` blockers remain non-dispatchable. Revisions, recipes, probes and attempt identities remain unchanged. |
| L. Runtime candidate integration | No accepted runtime candidate or shared-engine file changed. Section 10 requires complete bridge qualification first. `runtime_integration_diff.json` records an empty applied diff and preserved 69-file hashes. `real_dispatch` remains REJECT. |
| M. Global preservation | Before/after observations equal: selected `desktop-linux` Docker builder, builder selection/configuration file hashes, 3 networks, 1 unrelated container, 56 image reference rows, 0 volumes, default bridge inspection, readable daemon/Desktop/client/PF configuration hashes and application firewall observation. No daemon restart, install or policy mutation. Observation limitations are listed below. |
| N. Cleanup | Seven transient Engine identity clients removed by `--rm`; no transaction Docker object remains. No builder, proxy, network, bridge volume, external fixture, build output or image was created/deleted. Only required persistent evidence and synthetic filesystem fixtures remain. |
| O. Inventories | New repository evidence directory contains 32 files including its self-excluded hash manifest. Original 69 untracked files are unchanged; final expected untracked total 101. External qualification contains 46 file/symlink artifacts including its manifest; symlink targets are recorded without following them. |
| P. Validation | 11 existing mechanics tests passed, no failures/errors/skips. Fresh source validator: 15 mirrors, 866 commit bindings, 61,333 required leaf blobs, zero missing objects; full event-chain/effectivity replay PASS. Ruff, AST, strict JSON/UTF-8 and `git diff --check` pass. Detailed bridge gates remain NOT_RUN, as recorded in validation and rejection matrices. |
| Q. Firewall | Real attempts/claims/builds/source exports/dependency installs/oracle runs/event #3/canonical mutation: all ZERO/NO. No Git stage, commit or push. No bridge runtime pull or unapproved live qualification request. |
| R. Next gate | Human-PI decision on exact local BuildKit runtime provisioning is required before resuming section 3. Proposed review gate: `HUMAN_PI_DECIDE_V6_LOCAL_BUILDKIT_RUNTIME_PROVISIONING`. No provisioning or acquisition is authorized by this report. |

## 2. Files changed

Only `evaluation/downstream_benchmark/evidence/v6_restricted_build_egress_compatibility_bridge_v1/` was authored in the repository. The 14 requested artifacts are present: decision, entry, runtime/configuration, base/output qualification, proxy/network policy, bridge identity, integration diff, cleanup, validation, inventory and this report. Additional files bind exact population, planned Dockerfile delta, before/after Docker/global observations, source validation, focused/ledger tests, rejection classes, external inventory and final verification. Four evidence scripts make the bounded audit, mechanics testing, offline verification and exclusive publication reviewable.

External writes are confined to `/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1/qualification/restricted_build_egress_compatibility_bridge_v1`. The new ledger fixtures use `SYNTHETIC_QUALIFICATION_ONLY` and synthetic claim IDs, never real attempt claim IDs. The manifest SHA is `f93793d584a8209bc863ff5cb8626567e61e65c034302add07694cf18a2d964a`. The external copy is a frozen prepublication observation snapshot, with `validation_prepublication.json`; final repository validation is recorded separately. Intentional partial records and two symlink targets are negative test evidence, not materializer evidence trees.

The original manifest SHAs remain: activation `e5470a6dd48350717008350d9bc665f902ad41e747925ec892b3bd86c60466f8`, runtime `e1266b88dc5e4fb4f661947b4ad90caed752a440906b0d974384b508c7108025`, prior audit `777f8becd1f112b7651d87c1844c197a847d07e80804e637c2b739fbbc60e200`. No unrelated repository or external file was edited.

## 3. Commands run

Exact audit argv, exit codes and bounded stream hashes are in `commands_run.json` (41 observations). Validation commands are in `validation_results.json`; fresh source command/results are in `source_revalidation.json`; mechanics output is in `focused_tests.txt`.

- Read the attachment and relevant local manifests, canonical descriptor, authority, source/runtime/test code and prior audit evidence using cat, rg, sed and Python.
- Check `git status`, untracked inventory, HEAD/branch, tracked/index diffs and live `git ls-remote origin refs/heads/main` at entry and final preservation.
- Inspect local Buildx version/help/binary constants, selected/dedicated builder, Docker network/container/image/volume inventories and exact image references. No builder create/use/bootstrap command was executed.
- Run seven `docker run --rm --pull=never --network=none --read-only ...` executable identity probes against frozen Engine-store images; no Docker build command was executed.
- Run the unchanged activation package's read-only `revalidate_sources.py`; it uses local Git only and enforces a write/network audit guard. The fresh stdout result is transcribed with explicit provenance in `source_revalidation.json`.
- Run `run_focused_tests.py`: six existing RuntimeTests and five ActualFilesystemTests. Only the latter's setUpClass path is rebound in memory into this transaction's qualification subtree; test bodies and repository source bytes remain unchanged.
- Run `validate_bridge.py`, `publish_observations.py` and final `validate_bridge.py --verify-only`; no dependencies installed. Ruff uses `--no-cache`. AST/strict serialization checks cover new evidence and relevant production/test sources; Git whitespace and clean-index checks pass.

Initial sandboxed Git/Docker reads failed because DNS/socket access was unavailable and succeeded with authorized escalated access. An initial inline inventory assertion ran inside the package loop; it was corrected, and all 69 files passed before writing. Initial Ruff found one unused import in new audit code; it was removed before the audit and final checks. These preliminary errors are not reported as successful checks. The missing-image exit 1 is the expected gate observation.

## 4. Tests passed/failed

All 11 existing focused tests passed: 641 projections, selectors/blockers, acceptance, policy/default dispatch rejection, scientific recipe/revision rejection, no-pull/no-egress transport, exclusive immutable claims/terminals, partial/orphan/symlink denial, crash evidence, two-process once-only race, fsync and fabricated-real-admission rejection. Actual filesystem evidence is retained in the accepted qualification subtree; real ledger claims remain empty.

All 583 restricted items rejected a forged qualified receipt; all 58 NONE items accepted absent binding and rejected a receipt. Real dispatch rejected before Docker or claim. Six forbidden build/pull transport forms rejected with the backend mocked to fail if reached.

All 17 requested rejection classes have explicit records. Fifteen malformed bridge receipts are rejected by the **existing blanket restricted gate**, not by implemented bridge-specific validation. NONE application binding is specifically rejected by the existing NONE receipt rule; scientific mutation is specifically rejected with `hidden plan/recipe mutation`. Bridge-specific negative qualification remains NOT_RUN for every class; no complete bridge rejection-matrix PASS is claimed.

Fresh source-object, frozen Engine-base, population, blocker, artifact and canonical preservation checks pass. Seven-base **bridge** transport, output parity, application RUN binding, approved-origin TLS/HTTP and direct-egress enforcement remain NOT_RUN. The overall bridge did not qualify.

## 5. Contract compliance

C11 and section 3 were enforced before any builder/topology construction. C1–C9 architecture, transport and output requirements are recorded as an unprovisioned plan, not achieved properties. C10 no registry/base mutation and C13–C16 preservation/firewall constraints hold for executed commands. C12 production integration was deferred under section 10. C17 fail-closed behavior holds; the earliest observed failure is the missing runtime, so base-transport/output blockers are not inferred.

Canonical lifecycle and all 433 scientific cases remain unstarted. No research claims, scientific validation, canonical installation, execution effectivity, merge, freeze, release or submission decision follows from mechanics checks.

## 6. Risks and unknowns

The exact container runtime image is missing. No worker can be bootstrapped under the current no-pull policy. Base-image transport behavior and the missing base-transport mechanism are therefore **not determined**; this report does not predict a later successful or blocked base gate. No local registry, OCI layout, import transport or alternate reference is proposed as an implicit workaround.

Output-store parity, proxy parser/TLS/DNS policy, RUN application binding, builder network attachments/routes and direct isolation remain unqualified. PF runtime rules were not readable without privileged PF access; Docker VM daemon configuration was not directly inspected. Global preservation covers measured surfaces and the exact no-mutation command inventory. Binary string evidence locates the installed reference; explicit planned image binding removes reference-selection ambiguity without claiming a dedicated worker version.

## 7. Recommended next action

Human-PI should decide whether and how to provide an exact already-local BuildKit runtime, including its identity/provenance and any separate acquisition authorization. After that decision and local availability, resume the bounded gate order: worker/internal topology, first exact frozen base offline consumption, remaining bases, output/load parity, restricted network qualification, then minimal runtime integration. Every later gate remains necessary. Stop here; real dispatch remains REJECT.

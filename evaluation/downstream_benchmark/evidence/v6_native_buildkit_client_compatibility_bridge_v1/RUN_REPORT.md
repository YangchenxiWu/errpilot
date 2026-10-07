# Run Report — V6 native BuildKit client compatibility bridge

Date: 2026-10-07, Europe/Budapest.

STATUS = **V6_NATIVE_BUILDKIT_CLIENT_COMPATIBILITY_BRIDGE_QUALIFIED_READY_FOR_HUMAN_PI_REVIEW**

NEXT_GATE = **HUMAN_PI_REVIEW_OF_V6_PREPARATION_EXECUTION_RUNTIME_AND_EGRESS_QUALIFIED_BASELINE**

## 1. Task summary / requested A–V

The native same-daemon architecture passed seven-base OCI transport, seven native Docker exports and Engine loads, actual output observations, DEFAULT/NONE network fixtures and both approved TLS origins. The successor is a technically qualified construction candidate with real dispatch rejected. This is infrastructure qualification, not scientific validation or preparation activation.

| Item | Evidence / result |
| --- | --- |
| A. Entry / lineage | main; local HEAD and live origin/main 5c007fbfbfc5b3529105a14f87127f50e1eab6d7 at entry/final; canonical SHA 6a9028c79aa62f90db2b2d53def32ab23bffcfa3c71d2ec30d7fa64e741e3aae; planning authorized, event_count=2; tracked tree/index clean. All 260 prior manifest-bound untracked files and all prior external inventory exact. |
| B. Accepted decision | Human-PI ADOPT_V6_NATIVE_BUILDKIT_CLIENT_COMPATIBILITY_BRIDGE_V1; exact supplied request retained and SHA-bound in accepted_decision.json. |
| C. Client architecture | Host controller copies exact inputs; /usr/bin/buildctl inside the exact dedicated runtime connects through the local daemon Unix socket, registers frozenbase OCI session, invokes dockerfile.v0, exports Docker artifact, copies it out and docker loads it. No host buildctl, TCP daemon or second daemon. |
| D. Same daemon | Same current container/worker/socket for all 9 native solves. This is one new lifecycle instance of the accepted dedicated daemon configuration after the predecessor's verified cleanup; its operational container ID differs from the retired probe instance. Exact image and both binary hashes are retained. Buildx create/inspect/remove only. |
| E. Seven frozen bases | 7/7 PASS: Python 3.6.9, 3.7.0, 3.7.3, 3.7.4, 3.7.7, 3.8.1, 3.8.3; all x86_64, executable bytes exact. Archive config, ordered diffIDs, layer order and linux/amd64 exact; local OCI source consumed without registry requests/pulls observed. |
| F. Transport map | Seven deterministic config/diffID/OCI mappings in seven_base_transport_map.json. Original docker.io/library/python@sha256 authority remains separate from local transport identity. Save archives/layouts retained externally, not in Git. |
| G. Output parity | 7/7 native type=docker,name,dest artifacts SHA-verified before/after copy and docker load. Tag, image ID, RootFS, platform, Python, distributions and system packages observed. Actual shared materializer.identity schema used for all seven synthetic fixture identities. No old-client image byte equality or reproducibility claim. |
| H. Network semantics | Exact 641-item generated definitions audited; 583 DEFAULT and 58 NONE identities/order unchanged. Every scientific RUN byte/order unchanged. NONE uses force-network-mode=none, proven across both ordinary fixture RUNs; no RUN rewrite needed. DEFAULT normal RUN uses the internal-only worker. Internal proxy hostname has a separately recorded native add-hosts transport binding. |
| I. Proxy | Python stdlib CONNECT-only tunnel, exact case-insensitive pypi.org/files.pythonhosted.org:443 allowlist; reject IP/userinfo/malformed/other-port/HTTP requests before DNS. Source/policy hashes bound; end-to-end TLS remains client/origin. |
| J. Positive qualification | 2/2 PASS. pypi.org/simple/: HTTP 200, 256 bytes; files.pythonhosted.org/: HTTP 404, 10 bytes. Both exact hostnames TLS verified with CERT_REQUIRED/check_hostname. No redirects, package installation or dependency resolution. |
| K. Negative/direct path | Local denied.invalid:443, pypi.org:80, 127.0.0.1:443, malformed CONNECT, ordinary forwarding and userinfo all rejected. Logs bind zero upstream DNS/connect for each denial. DEFAULT direct external-only fixture connection failed, internal proxy connection succeeded; both NONE RUNs lacked external routes/proxy connectivity. No unapproved live destination used. |
| L. Identities | ENFORCEMENT_IDENTITY = 8801637324b2fa32124df8444e88f193a5be3f9c847904f2eebfb92197bc5c10; semantic and qualification observation hashes are separate. Qualified candidate receipt carries no installed runtime authority. |
| M. Successor candidate | successor_runtime.py/data provide exact transport compiler, native invocation, copy/readback preserving modes/safe symlinks, Docker export/copy/load, private shared-materializer function rebinding and receipt. Original generator/identity/observation code objects retained. Real dispatch and real materializer entry reject; future accepted controller/provider and all later gates remain required. Full I/O ordering tested offline; no benchmark recipe executed. |
| N. Population | 641/583/58 exact. matplotlib::1 and matplotlib::8 remain non-dispatchable. No governed batches or outcome-dependent stopping. Transport identities do not replace recipe/base-attempt identities. |
| O. Once-only | Unchanged accepted tests exercise exclusive claims, fsync, races, one terminal, non-overwrite, no retry and orphan/crash failure on actual target filesystem in the new synthetic child. All real claims/locks/terminals absent. |
| P. Global preservation | Before/after snapshots and readable config hashes equal for selected builder, client/Desktop config, default bridge, unrelated networks/containers/images and volumes. No daemon restart/global switch/firewall/global proxy mutation. Unreadable PF/VM internals unclaimed. |
| Q. Cleanup | Evidence fsynced/read back first. Owned builder/daemon/state volume/proxy/local fixture/both networks and seven synthetic Engine output images removed. Exact runtime image and seven frozen bases preserved. Layouts, archives, artifacts, logs and ledger fixtures retained externally. |
| R. Inventory | New repo files only in this namespace. New external files only under /Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1/qualification/native_buildkit_client_compatibility_bridge_v1. artifact_sha256.json seals repo bytes; external_evidence_manifest.json binds external inventory/root seal. Historical bytes were never rewritten. |
| S. Validation / rejection | 18 focused methods PASS (17 guard/accepted-mechanics + 1 offline successor I/O model), zero failures/errors/skips. 44 explicit rejection categories PASS. Ruff, AST, strict JSON/UTF-8, whitespace and git diff --check PASS. No benchmark subject tests. |
| T. Firewall | Real attempts/claims/builds/source exports/dependency installs=0; Buildx solves=0; unapproved live egress=0 in recorded scope. Acquisition/oracle/event #3/effective execution descriptor/canonical mutation/stage/commit/push all NO. 9 fixture solves, 10 RUN instructions only. |
| U. Unresolved prerequisite | Technical gates passed. Human-PI integration acceptance, freeze/persist/commit, required publication, event #3, execution effectivity binding, independent acceptance pin and canonical installation remain outstanding. The candidate's real dispatcher stays disabled. |
| V. Next gate | HUMAN_PI_REVIEW_OF_V6_PREPARATION_EXECUTION_RUNTIME_AND_EGRESS_QUALIFIED_BASELINE. Stop; no execution effectivity decision made by this agent. |

## 2. Files inspected / changed

Inspected the supplied request, canonical descriptor and pinned capacity contract, exact manifests and referenced bytes for all eight prior packages, predecessor client/daemon/source/RUN/output/log evidence, shared adapter/runtime/ledger/materializer and accepted tests, seven Engine-local bases and exact runtime, daemon sockets/worker/version/binaries/native help, copied inputs, proxy topology/logs, qualification outputs and global before/after snapshots. No on-disk AGENTS.md or .airos/current_state.md/contracts existed.

Only the new evidence namespace was changed in the repository. It contains the bounded executor, guards, stdlib proxy/fixtures, successor source/data, tests, qualification records, inventories and this report. All older candidate/evidence/source/canonical/index bytes remain exact. External writes were restricted to the authorized qualification child.

## 3. Commands run

Read-only discovery used cat, rg, sed, Git status/HEAD/branch/diffs/untracked inventory, live git ls-remote and filesystem checks. The bounded driver ran phases entry, create, capabilities, base 0, remaining-bases (1–6), network-audit, proxy-create, proxy-observe, egress none, egress restricted, shared-identity, candidate-identity, cleanup and finish. Docker commands covered exact local inspect/save, lifecycle create/start/inspect, native buildctl help/worker/build via docker exec, docker cp/hash, Docker exporter load and qualification-only run probes, logs and owned cleanup. Exact driver argv/timestamps/exit codes/output hashes are in commands_run.json; large raw logs/artifacts are external. The actual-runtime save is also recorded in runtime_identity.json.

Focused test commands were `.venv/bin/python -B .../run_tests.py` and `.venv/bin/python -B .../test_successor_transport.py`; final Ruff and Git whitespace commands are captured. AST/strict decoding/JSON checks ran in the verifier. Existing .venv tooling only; no install/fetch/stage/commit/push. Initial discovery/development checks remain in the chat; evidence-preserving corrections are recorded in execution_corrections.json.

## 4. Tests passed / failed

18/18 focused methods PASS, 0 failed/error/skipped. 44 required rejection categories PASS. Seven actual native base solves/export/load/probes, the two network fixture solves, exact proxy binding, two verified-TLS origins and six local policy denials passed. Offline successor I/O evidence is explicitly synthetic and is not included as an actual Docker export or scientific result.

## 5. Contract compliance

Current Human-PI authority covers construction and fixture qualification only. No prior package rewritten; no Buildx solve or historical syntax/fallback retried; no scientific recipe/work/base-attempt authority changed. Canonical preparation execution remains NO, planning remains YES, event_count remains 2 and attempts/environment-ready remain 0. Once-only mechanics were not altered. The prior disclosed alias-fallback exception remains historical, non-authoritative and unchanged.

## 6. Risks / unknowns

No packet capture, independent global DNS tracing, Docker VM inspection or readable PF-rule audit was performed. Network conclusions bind exact topology, route observations, fixture results and complete retained client/daemon/proxy logs; they do not claim omniscient network visibility. Global equality covers observable entry/final state, not every possible concurrent change between snapshots. No full 641 benchmark build or dependency installation was performed. The successor I/O controller/provider is restricted to construction qualification; real orchestration and acceptance/effectivity installation are later Human-PI gates. Output images are observations with no byte-reproducibility claim. These passes establish infrastructure mechanics, not scientific validation.

## 7. Recommended next action

Human PI should review the frozen source/data, semantic/observation identities, actual 7/7 and 2/2 receipts, network-none and direct-egress results, successor default-deny behavior and cleanup/inventory at HUMAN_PI_REVIEW_OF_V6_PREPARATION_EXECUTION_RUNTIME_AND_EGRESS_QUALIFIED_BASELINE. No execution activation, canonical install or Git publication is performed in this transaction.

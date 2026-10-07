# Run Report — V6 restricted build-egress bridge resume

Date: 2026-10-06, Europe/Budapest.

STATUS = **V6_RESTRICTED_BUILD_EGRESS_BRIDGE_BASE_IMAGE_TRANSPORT_BLOCKED**

NEXT_GATE = **HUMAN_PI_DECIDE_V6_BUILDKIT_FROZEN_BASE_TRANSPORT_BRIDGE**

## 1. Task summary / A–S results

The authorized resume reached the first frozen-base offline-consumption gate and failed there. The dedicated `docker-container` BuildKit runtime was exact and local. Its isolated store did not consume the exact base already present in the Docker Engine store. BuildKit instead attempted to resolve the frozen digest using a Docker Hub manifest HEAD request, which failed at container-local DNS. The fixture `RUN python --version` never executed. Dependent qualification and production integration stopped. Exact observations were durably persisted before transaction-owned resources were removed.

| Requested result | Observed result and evidence |
| --- | --- |
| A. Entry and resume lineage | Branch `main`; local HEAD and queried LIVE `origin/main` both `5c007fbfbfc5b3529105a14f87127f50e1eab6d7`. Exact five manifest inventories: 14 + 26 + 29 + 32 + 23 = 124 prior untracked files; no unrelated paths. Canonical SHA `6a9028c79aa62f90db2b2d53def32ab23bffcfa3c71d2ec30d7fa64e741e3aae`; planning effective, event_count=2, execution/preparation unauthorized. `resume_lineage.json` binds the prior shared-engine finding, runtime-missing bridge report, accepted bridge decision, provisioning report and exact resume request bytes. No architecture adjudication was reopened. |
| B. BuildKit revalidation | Engine/index digest `sha256:cec9f139f45e93c5c69c60f8b07cfad9f43f4ef6b6a6cd917527fea5ff2e3dea`; linux/amd64 manifest `sha256:98cc6a3fc46220d00f8224ae483f3274fc874e9be8d7dd1e2e2c5481209228b5`; locally exported config `sha256:27933730df224df80c41f4e5a9b33fa78831a79fd31903df3bb7deb49363422f`. Exact platform, RepoDigest and RootFS checked before creation and after cleanup. Local save used only to read runtime config bytes; no base export/import, archive extraction, load or registry operation. |
| C. Dedicated builder | `errpilot-v6-builder-42393faa3385-v1`, driver `docker-container`, immutable driver-opt image from `future_builder_binding.json`, driver-opt network `errpilot-v6-egress-42393faa3385-v1-internal`. Network inspect `Internal=true`, ID `b31f31eeb8b89462358e75bde7e9f1ee4e17d02fcfd390ec23bb2bd8c7c59457`; full driver/scope/IPAM/options/labels/inspect identity retained. Runtime container was created with `--pull=never`, then started; Buildx connected to that existing container without acquisition. Container attached only to this network, with no IPv4 default route; DNS forwarding was restricted to `127.0.0.1`. Runtime `buildkitd v0.33.1`, commit `8c91502cf280bd70a0c50912ce251c46a8881d9f`. Global selected builder was unchanged. |
| D. First base offline result | **FAIL**, exit 1, before RUN. Mechanically selected the first accepted seven-base ledger entry: `docker.io/library/python@sha256:036d4ab50fa49df89e746cf1b5369c88db46e8af2fbd08531788e7d920e9a491`, expected Python 3.6.9. Exact Engine-store identity matched. `first_base_transport_qualification.json` and external raw logs retain the failure. |
| E. Seven-base result | 1 attempted, 0 passed; remaining 6 **NOT_RUN** under the first-base hard gate. All seven Engine-local identities were rechecked and preserved during cleanup. Engine presence is not BuildKit consumption proof. |
| F. `--load` / output parity | Explicit `--load` was requested for the fixture. The solve failed before output, so output parity and subsequent probe compatibility remain **NOT_QUALIFIED**. No output image was added; before/after image inventories match. |
| G. Proxy implementation/runtime | **NOT_RUN**. No proxy implementation source, proxy container or proxy runtime identity was created after the hard gate. `proxy_implementation_status.json` and `proxy_runtime_identity.json` explicitly record this unmet dependent deliverable. |
| H. Application binding | **NOT_RUN**. First fixture used network NONE and no proxy/PIP build arguments. No Dockerfile transport ARG, pip index change or recipe/setup mutation was made. |
| I. Positive qualification | **NOT_RUN**, 0 of 2 approved origins attempted. No PyPI request, package install, dependency resolution or TLS/HTTP connectivity qualification occurred. |
| J. Negative/direct-egress qualification | **NOT_RUN**. No proxy parser tests, external-only local fixture, default-RUN reachability proof or network-NONE proxy test was performed. Container isolation observations do not qualify those absent tests. |
| K. Enforcement identities | **ABSENT**. No semantic enforcement identity or completed network qualification observation identity was constructed. Failure evidence is hash-bound by the artifact manifests; it is not an enforcement receipt. |
| L. 641 / 583 / 58 preservation | Exact accepted population rederived against the pinned manifest; full population equality and exact ordered restricted/NONE IDs checked. 641 base attempt identities, 583 restricted and 58 NONE, case order, plan/recipe/revision identities and blocker states are unchanged. |
| M. Production candidate delta | **NONE**. Runtime, adapter, ledger, materializer and tests remain byte-identical to the prior accepted inventories. No builder/proxy integration candidate was applied. |
| N. Focused validation/rejection matrix | The independent evidence verifier passed **27** persisted integrity/preservation checks. The first-base qualification failed. The requested production integration/rejection suite is **NOT_RUN** because the preceding hard gate failed and no integration exists. Event #3 is absent, canonical state remains planning, and execution pin/runtime installation files are absent. `real_dispatch` was not invoked or dynamically retested. |
| O. Global preservation | Networks, containers, volumes, image rows, selected builder, builder selection/configuration hashes and readable host configuration hashes match before/after. 3 original networks, 1 original container, 0 volumes and 57 image rows remain. Application firewall observation is unchanged. PF rules were unreadable; no claim is made about unobserved PF or Docker VM internals. |
| P. Cleanup | Exact observations and precleanup manifest were fsynced and read back first. Only the owned builder, BuildKit container, disposable state volume and internal network were removed. No proxy, client, external fixture/network or output image needed removal. Exact BuildKit runtime and seven frozen Python bases remain. |
| Q. Repository/external inventory | Only this new continuation repository namespace was written: **38 files**, manifest excluding its own hash. New external child: `/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1/qualification/restricted_build_egress_compatibility_bridge_resume_v1`, **67 files**. It retains initial exact observations and a separate `final/` copy, preserving evidence revisions. All 124 prior repository files and 194 prior external file/symlink artifacts remain exact. Final attributable untracked population: 162 files. Manifest equality, rather than these counts alone, is authoritative. |
| R. Firewall | All required real benchmark attempt/claim/source-export/image-build/dependency-install counters are 0. Source acquisition, oracle, event #3, effective execution descriptor, canonical mutation and canonical execution effectivity are NO. Unapproved live egress requests=0: the attempted manifest resolution failed locally without a resolved upstream or registry response; no live request command was run. Runtime pulls=0. Git stage/commit/push=NO. |
| S. Next Human-PI gate | `HUMAN_PI_DECIDE_V6_BUILDKIT_FROZEN_BASE_TRANSPORT_BRIDGE`. A frozen-base transport mechanism is missing under the current accepted restrictions. No import, local registry, OCI substitution, retag, alternate reference or FROM rewrite was invented. |

The exact failing BuildKit observation was:

```text
load metadata for docker.io/library/python@sha256:036d4ab50fa49df89e746cf1b5369c88db46e8af2fbd08531788e7d920e9a491
failed to do request: Head "https://registry-1.docker.io/v2/library/python/manifests/sha256:036d4ab50fa49df89e746cf1b5369c88db46e8af2fbd08531788e7d920e9a491": dial tcp: lookup registry-1.docker.io on 127.0.0.11:53: server misbehaving
```

## 2. Files inspected and changed

Inspected all five prior repository manifests and their exact bytes; prior external manifests and file/symlink hashes; canonical descriptor and pinned contract/event/manifest dependencies through the existing input validator; accepted work-item population and ordered scope; frozen BuildKit binding/config/platform/RootFS; seven base identities; existing runtime authority/preflight code; and observable Docker/global configuration surfaces. No on-disk `.airos/current_state.md`, `.airos/contracts/` or repository AGENTS.md was present; the supplied global rules and explicit request governed this task.

All changes are new evidence files in this continuation directory and its new non-attempt external child. `resume_bridge.py` is a bounded phased evidence executor; `validate_resume.py` is the independent evidence verifier. No tracked or prior candidate file changed. Original precleanup observations remain preserved alongside final corrected configuration metadata.

## 3. Commands run

Executed `resume_bridge.py entry`, `create`, `observe`, `first`, `cleanup`, `finish`, `publish`, and `validate_resume.py --persist`. Used the existing `.venv/bin/python`; no dependencies installed. `commands_run.json` retains exact captured Git/Docker/firewall argv, exit codes, stdout/stderr and hashes. Local runtime `docker image save --platform=linux/amd64` verification is separately bound in `builder_runtime_verification.json`. Preliminary read-only observations and phase failures are described in `execution_corrections.json`.

The only build argv used the explicit dedicated builder, linux/amd64, `--network=none --pull=false --progress=plain --no-cache --load`, a qualification-only tag and the new two-line fixture context. Only `FROM <exact frozen digest>` and `RUN python --version` were present. No benchmark context was opened for a build.

## 4. Tests passed / failed / not run

27 independent evidence integrity/preservation checks passed, zero verifier checks failed. The first frozen-base offline qualification failed with exit 1; this is the authoritative blocked result. The 13 other final gate/preservation classifications passed. Full runtime integration tests, six remaining base builds, output parity, proxy/application binding and network positive/negative tests were not run after the hard stop.

Initial read-only observation issues were corrected: preserved symlink hashes use `target_bytes_sha256`; system Python lacked jsonschema, so the existing project environment was used; Buildx inspect lacked `--format`; BusyBox ip lacked `-j`; and initial immediate bootstrap observation preceded socket readiness. None of these replaced or obscured the actual base failure. Expected nonzero absence probes and unreadable PF observations are distinguished from qualification failures in the command ledger.

## 5. Contract compliance

The accepted dedicated architecture and immutable provisioning binding were retained. No global builder selection, Docker client proxy config, daemon-wide config, host firewall or Docker Desktop setting was changed. No new image was pulled, no daemon restarted, no third-party tool installed and no forbidden transport fallback created. Cleanup was confined to resources absent at entry and proven owned by exact names/IDs/labels. The hard gate prevents any claim that this bridge is qualified or that preparation execution is effective.

## 6. Risks and unknowns

Buildx inspect reports configured daemon flags `--debug --allow-insecure-entitlement=network.host` and a worker network label `host`, while actual Docker container launch args were only `--debug` and Docker NetworkMode was the dedicated internal network. These are separate observed surfaces, reconciled in `builder_metadata_reconciliation.json`; the initial intended-policy field is superseded. No `--network=host` build request was submitted, and no RUN executed. Effective worker entitlement behavior and the 583 default-RUN network paths remain unqualified.

No packet capture or Docker VM/PF internal audit was performed. Egress conclusions are bounded to command records, internal-only attachment, absence of a default route, loopback upstream DNS and the exact locally failed resolution. Snapshot equality cannot rule out concurrent activity between observations. No Python patch execution, output parity, proxy connectivity, benchmark readiness or scientific validation is claimed.

## 7. Recommended next action

Human-PI review of this frozen-base transport block at `HUMAN_PI_DECIDE_V6_BUILDKIT_FROZEN_BASE_TRANSPORT_BRIDGE`. A new explicit decision is needed before attempting a transport mechanism that the current request forbids. This run stops with real attempts=0 and no Git publication.

# Run Report — V6 native BuildKit OCI-session compatibility probe

Date: 2026-10-06, Europe/Budapest.

STATUS = **V6_NATIVE_BUILDKIT_OCI_SESSION_COMPATIBILITY_PROBE_PASS**

NEXT_GATE = **HUMAN_PI_DECIDE_V6_NATIVE_BUILDKIT_CLIENT_COMPATIBILITY_BRIDGE**

## 1. Task summary / requested A–R results

The single native `buildctl` solve connected to the recreated exact containerized daemon, accepted the two-part OCI-session registration, consumed the verified first frozen-base layout, executed the observation RUN, and exported an OCI artifact. Python was 3.6.9 on x86_64, with `/usr/local/bin/python`. No registry request or pull was observed. This establishes first-base native-client/source compatibility only; production migration, all-seven qualification, output parity, egress qualification, real preparation and event #3 remain outside this transaction's authority.

| Item | Evidence and result |
| --- | --- |
| A. Entry / lineage | `main`; LOCAL HEAD and LIVE origin/main at entry and final: `5c007fbfbfc5b3529105a14f87127f50e1eab6d7`. Canonical SHA `6a9028c79aa62f90db2b2d53def32ab23bffcfa3c71d2ec30d7fa64e741e3aae`; state `PREPARATION_PLANNING_AUTHORIZED`, event_count=2, PREPARATION_EXECUTION=NO. All 215 prior untracked files equal the exact seven package manifests; no unrelated untracked paths. |
| B. Exact prior parser block | Prior status remains `V6_BUILDKIT_FROZEN_BASE_TRANSPORT_NAMED_CONTEXT_BLOCKED`. Both retained historical requests failed before RUN: `could not parse oci-layout reference <session-id>:@sha256:<digest>: invalid reference format`. Prior config bytes, ordered nine diffIDs and layout integrity passed. |
| C. Builder / daemon | `errpilot-v6-builder-42393faa3385-v1`, docker-container driver. Runtime, internal network, argv, routes and socket ownership are recorded in `builder_identity.json`. One daemon created; no global `--use`. Operational container ID: `4c38bf6550d91344b596a9c865ab160386aaf70e307c260b4618cb9bd1bf4c15`. |
| D. Native client | `buildctl github.com/moby/buildkit v0.33.1 8c91502cf280bd70a0c50912ce251c46a8881d9f`; same version/commit as `buildkitd`. The first native invocation was exactly `buildctl --version`, inside that container. |
| E. Same-daemon connection | PASS. Actual listening Unix socket and daemon startup message uniquely identify `unix:///run/buildkit/buildkitd.sock`. The one `debug workers` invocation returned exact worker `z2pq19se9on21ttduye8xinwv`, including linux/amd64. No TCP daemon endpoint or listen change. |
| F. Copied OCI layout | PASS. The layout path was recovered from prior manifest-bound evidence. All 13 files, exact index/manifest/config and nine layer hashes match before reuse. After Docker copy, every OCI file plus the sole Dockerfile was independently hashed inside the same container, and the exact file set was checked. |
| G. Native command | One solve, exact two-part `--oci-layout frozenbase=…` plus frontend context mapping, reproduced below and in `buildctl_command.json`. Built-in dockerfile.v0, linux/amd64, no-cache, plain progress, RUN network none, OCI file exporter. Buildx was used for builder metadata/management only. |
| H. Source binding | PASS. Client log explicitly reports `[context errpilot_frozen_base] OCI load from client`, followed by transfer and extraction of all nine exact local uncompressed layer identities. Registration, frontend mapping and frozen-base consumption succeeded. |
| I. Fixture RUN | PASS. `sys.version` output is `3.6.9 (default, Nov 23 2019, 06:41:34)` followed by `[GCC 8.3.0]`; `platform.machine()` is `x86_64`; `sys.executable` is `/usr/local/bin/python`. Complete raw output is retained. |
| J. Output | PASS for qualification artifact existence/integrity. Retained OCI tar is 935645696 bytes; SHA `980a1b2bed92b0c902a621e7619586c674a96fb4388ac8e3a1bd42467bdfb3ac`. Container and copied-file hashes match. Manifest/config/all layer descriptors verified; platform linux/amd64; original nine rootfs diffIDs are the exact prefix. No Engine load or output-parity qualification. |
| K. Registry / network | No registry endpoint, HTTP do-request/fetch-response, pull or other registry resolution attempt in complete retained client/daemon logs. Daemon attached only to the INTERNAL network, with no IPv4 default route, proxy or published port. RUN uses network none. Exact normalized local OCI alias resolve labels and a RUN DNS warning are preserved and explained below. No packet capture performed. |
| L. Historical deviation | The previous alias fallback remains explicitly noncompliant with its triggering condition. Its exact evidence bytes, logs and exception are unchanged; no alias fallback, alternative OCI syntax, alternate frontend or native solve retry occurred here. |
| M. Cleanup | Evidence and precleanup manifests fsynced/read back first. Only owned builder/container/volume/internal network removed. Observable Docker and global selection/configuration snapshots are exactly equal at entry/final: 57 image rows, 3 networks, 1 original container, 0 volumes. Runtime and all seven Python bases preserved. |
| N. Inventory | New repository files only in `evaluation/downstream_benchmark/evidence/v6_native_buildkit_oci_session_probe_v1/`. New external files only under `/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1/qualification/native_buildkit_oci_session_probe_v1/`. Exact final inventories are `artifact_sha256.json` and `external_evidence_manifest.json`; raw logs, fixture, output and final evidence copies remain external qualification evidence. Prior external inventory is exact after cleanup. |
| O. Validation | 23 focused methods passed, 0 failures/errors/skips. All 14 required rejection categories passed offline. Ruff, AST, strict JSON/UTF-8 and git diff --check passed. Required-check receipt records 70 evidence/static checks; final integrity receipt covers the subsequently written report and records. Passing rejection/mechanics tests are not scientific validation. |
| P. Firewall | All seven required real-work/pull/egress counters are 0 within the recorded observation scope. PRODUCTION_CLIENT_SWITCHED, EVENT_3_CREATED, CANONICAL_CURRENT_STATE_MODIFIED, GIT_STAGE, GIT_COMMIT and GIT_PUSH are NO. Exactly one qualification solve, one RUN and one external artifact. |
| Q. Classification | `V6_NATIVE_BUILDKIT_OCI_SESSION_COMPATIBILITY_PROBE_PASS`, restricted to the first verified Python 3.6.9 layout through the native client on this daemon. |
| R. Next gate | `HUMAN_PI_DECIDE_V6_NATIVE_BUILDKIT_CLIENT_COMPATIBILITY_BRIDGE`. A Human-PI decision is required before any production client bridge work. No such decision is made by this report. |

The exact runtime identities are separate:

- Top-level: `sha256:cec9f139f45e93c5c69c60f8b07cfad9f43f4ef6b6a6cd917527fea5ff2e3dea`.
- linux/amd64 manifest: `sha256:98cc6a3fc46220d00f8224ae483f3274fc874e9be8d7dd1e2e2c5481209228b5`.
- Config: `sha256:27933730df224df80c41f4e5a9b33fa78831a79fd31903df3bb7deb49363422f`.

The first base remains scientifically identified by `docker.io/library/python@sha256:036d4ab50fa49df89e746cf1b5369c88db46e8af2fbd08531788e7d920e9a491`. Its config is `sha256:5bf410ee7bb26f8f8fe9d7a2f9e9a05240cce0bc1bdbaee234f74f6b1b25ca94`; local transport is `sha256:9a64909eb826662bbf181357566002a8621652c18e3e24e90bf43f279f97ce8a`. No recipe, revision, work-item or attempt identity was replaced by a transport identity.

Exact Dockerfile bytes, 233 bytes, SHA `af21fac3a3ab13d98306f3423caffbca67fb1a605c072c84a2953ccb7c2f38a0`:

```dockerfile
FROM errpilot_frozen_base
RUN python -c "import sys, platform; print('sys.version=' + sys.version); print('platform.machine()=' + platform.machine()); print('sys.executable=' + sys.executable)"
```

Exact command inside the same daemon container:

```sh
buildctl --addr=unix:///run/buildkit/buildkitd.sock build \
  --oci-layout frozenbase=/tmp/errpilot-v6-native-oci-probe-v1/oci \
  --frontend=dockerfile.v0 \
  --local context=/tmp/errpilot-v6-native-oci-probe-v1/context \
  --local dockerfile=/tmp/errpilot-v6-native-oci-probe-v1/context \
  --opt context:errpilot_frozen_base=oci-layout://frozenbase@sha256:9a64909eb826662bbf181357566002a8621652c18e3e24e90bf43f279f97ce8a \
  --opt platform=linux/amd64 \
  --opt force-network-mode=none \
  --no-cache --progress=plain \
  --output type=oci,dest=/tmp/errpilot-v6-native-oci-probe-v1/output.oci.tar
```

The host invocation was `docker exec <observed owned container ID>` followed by this argv. No registry exporter, push, pull or Buildx solve was submitted.

Output image manifest is `sha256:4ff8761c4fc411c26e3d0684c9a89581bd95494df9d7b363351dc0de78c84794`; output config is `sha256:d59129a0132a48af101e943ca390ad3ec1afeb72ebfd0dbba528c2d450748eb4`. The output includes one fixture layer after the nine unchanged base diffIDs. Its export metadata is an observation, not a determinism or parity qualification.

## 2. Files inspected and changed

Inspected the supplied request, all seven prior package manifests and exact referenced bytes, every manifest-bound external history, canonical descriptor and its contract/event/recipe inputs through the existing input loader, all-641 population and blockers, exact prior parser logs/deviation, OCI files, local runtime and all seven frozen-base inspections, daemon/container/network/socket/worker state, client/daemon logs and the output archive.

No on-disk AGENTS.md, `.airos/current_state.md` or `.airos/contracts/` was found. The supplied global rules and current explicit Human-PI probe contract governed scope; the pinned V6 capacity contract remains unchanged. All new repository files are evidence, bounded executor, tests and verification/report artifacts in the new namespace. No tracked source, production client, adapter, ledger, prior evidence, canonical descriptor or index changed. The output and fixture exist only in the new external qualification child.

## 3. Commands run

Used existing `.venv/bin/python` and `.venv/bin/ruff`; no dependencies installed. Executor phases were `entry`, `create`, `observe-created`, `connect`, `connect-observed`, `copy`, `solve`, `classify-existing-output`, `cleanup`, and `finish`. The observation-only recovery phases never recreated/restarted the daemon or repeated solve. Required validation, final integrity checking and artifact sealing followed.

`commands_run.json` records exact captured Git/Docker/check argv, timestamps, exit codes and stdout/stderr hashes. Runtime identity records also include the exact local save used to verify its config bytes. Read-only LIVE origin checks occurred at entry and final. No fetch, stage, commit or push occurred. The direct development-time test/lint commands and failed local verification traces are available in the chat; durable correction records describe their causes. The final focused tests and required checks have retained raw outputs.

## 4. Tests passed / failed

23 focused methods PASS, no failure/error/skip. Tests cover exact allowed registration, Buildx/old syntax/store/transport/daemon rejection, second daemon, TCP, registry request/pull, real source/dependency work, event #3, canonical mutation, production-switch claim, retry/exporter/network rejection, strict JSON and escaped daemon log messages. The local OCI normalized-label test also proves that actual HTTP registry requests remain rejected even when carrying the same local-source span label.

Ruff, AST, strict JSON/UTF-8, whitespace checks and git diff --check PASS. Native source, RUN and output gates PASS. All-seven consumption, output parity, proxy/egress qualification and real benchmark tests were not run. The required evidence check count and final seals are in the validation/integrity manifests.

## 5. Contract compliance and evidence-preserving corrections

Current transaction stayed within one first-base native probe, one daemon and one solve. Prior 215-file population and external history are byte-exact. 641 total / 583 restricted / 58 network-none items retain exact identities/order; `matplotlib::1` and `matplotlib::8` retain their exact non-dispatchable plans. Canonical case population remains 433, with no consumed attempts or environment-ready cases; real claims/terminals/locks remain empty and real attempts/inputs/snapshots absent.

The previous alias-fallback authority exception is preserved unchanged and is not reused as authority. This transaction made no fallback request or OCI syntax change. `execution_corrections.json` preserves three pre-mutation inventory schema stops (omitted regular-file type, symlink target encoding, separate root-seal versus complete final-inventory schemas), an overly broad all-TCP-sockets check, escaped logfmt endpoint/worker extraction, and the initial local-OCI label classifier result. Actual native worker connection and solve were each invoked once. Initial connection/source/network/output observations are retained separately where final interpretation changed.

The initial all-TCP check encountered a loopback socket at 127.0.0.11. PID 1 socket-inode inspection establishes that the listener is not owned by buildkitd; no nonloopback TCP listener, daemon TCP listener or published port was present. No listen configuration changed.

The source provider displays the exact alias as `docker.io/library/errpilot_frozen_base@sha256:9a64909eb826662bbf181357566002a8621652c18e3e24e90bf43f279f97ce8a`. The client labels that vertex `OCI load from client`, transfers/extracts all nine exact local OCI layers, then completes RUN/export. The three retained resolve/fetch-span label lines contain no network request. The interpretation that these are local-source labels is based on that completed OCI vertex, exact local layer transfer, daemon isolation and full logs; actual HTTP requests/endpoints and every other registry resolve remain rejection conditions. The existing artifact was hashed/copied after correcting this interpretation, without a second solve.

## 6. Risks and unknowns

No packet capture, Docker VM/PF internals audit or independent DNS trace was performed. Network conclusions are bounded to internal-only attachment, no default route/proxy/published port, RUN network none and complete retained logs. BuildKit logged `No non-localhost DNS nameservers are left in resolv.conf. Using default external servers` while preparing RUN; this warning does not establish a DNS request or egress, and no such request was observed. Worker default network is reported as host within the builder container; this fixture explicitly requests RUN network none. That architecture is not qualified for restricted benchmark egress.

Only the first frozen layout was consumed. No production bridge design, all-seven rule, Engine output load/parity, proxy behavior or real preparation is established. Host/global snapshots are observable checks, not proof against all concurrent activity between snapshots. The output archive includes creation metadata and has no claimed byte determinism. The compatibility result is implementation evidence, not scientific validation or readiness for benchmark execution.

## 7. Recommended next action

Review the exact native command, source/RUN/output records, preserved initial classifier records and network interpretation at `HUMAN_PI_DECIDE_V6_NATIVE_BUILDKIT_CLIENT_COMPATIBILITY_BRIDGE`. Human PI may decide whether to authorize a bounded client-compatibility bridge follow-up. No production-client switch, broader qualification, real preparation or event #3 is authorized or performed by this result. Stop at this gate.

# Run Report — exact local BuildKit runtime provisioning

Date: 2026-10-06, Europe/Budapest.

STATUS = V6_EXACT_BUILDKIT_RUNTIME_PROVISIONED_AND_VERIFIED

## 1. Task summary / A–G runtime provenance

Human-PI gate `HUMAN_PI_DECIDE_V6_LOCAL_BUILDKIT_RUNTIME_PROVISIONING` authorized metadata resolution, immutable freezing, one exact-digest linux/amd64 runtime pull, and local verification. The supplied request is bound in accepted_decision.json. No builder was created.

| Identity | Frozen / observed value |
| --- | --- |
| A. Logical tag | `moby/buildkit:buildx-stable-1` |
| Registry / media type | `docker.io` / `application/vnd.oci.image.index.v1+json` |
| B. Top-level digest | `sha256:cec9f139f45e93c5c69c60f8b07cfad9f43f4ef6b6a6cd917527fea5ff2e3dea` |
| C. linux/amd64 manifest | `sha256:98cc6a3fc46220d00f8224ae483f3274fc874e9be8d7dd1e2e2c5481209228b5` |
| D. Registry and verified local config digest | `sha256:27933730df224df80c41f4e5a9b33fa78831a79fd31903df3bb7deb49363422f` |
| D. Engine store/index image ID | `sha256:cec9f139f45e93c5c69c60f8b07cfad9f43f4ef6b6a6cd917527fea5ff2e3dea` |
| D. Engine selected linux/amd64 image ID | `sha256:98cc6a3fc46220d00f8224ae483f3274fc874e9be8d7dd1e2e2c5481209228b5` |
| E. Exact pull reference | `moby/buildkit@sha256:cec9f139f45e93c5c69c60f8b07cfad9f43f4ef6b6a6cd917527fea5ff2e3dea` |
| F. Local verification | RepoDigest and platform match; exported config bytes equal registry config; all 7 exported layers match registry blob or frozen uncompressed diff ID; RootFS matches config. |
| G. Future builder binding | `--driver-opt=image=moby/buildkit@sha256:cec9f139f45e93c5c69c60f8b07cfad9f43f4ef6b6a6cd917527fea5ff2e3dea` |

The immutable identity file was fsynced before the single pull. No tag-only pull or runtime substitution occurred. Registry compressed layer digests and config uncompressed diff IDs remain distinct. This containerd Engine reports the index digest for its store identity and the child manifest digest for a platform-selected inspect; neither is the config digest. local_identity_verification.json retains the platform-selected observation, docker_engine_store_identity.json separately binds the store/index observation, and local archive bytes verify the config independently. Created metadata and RepoTags are observations only. Future create argv is persisted but unexecuted.

## 2. Files inspected and changed / I inventories

Inspected: all 101 files in the four prior inventories (14 activation, 26 runtime implementation, 29 restricted-egress audit, 32 compatibility bridge), their manifest-bound external evidence, canonical current state, seven frozen Python image identities, prior builder configuration, Docker networks/containers/volumes/images/selected builder, host config hashes, and exact registry index/child/config metadata. All prior files remain exact.

Only this new repository directory was written: `evaluation/downstream_benchmark/evidence/v6_local_buildkit_runtime_provisioning_v1`. It contains the requested 11 files plus the phased executor, accepted decision, raw registry metadata, single-pull guard/logs, archive verification, command ledger and external inventory. External copies are confined to `/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1/qualification/local_buildkit_runtime_provisioning_v1` within the existing qualification namespace. No benchmark attempt ID is used. artifact_sha256.json inventories repository bytes and excludes its own hash. external_evidence_manifest.json pins the external manifest and all external copy hashes.

## 3. Commands run

`provision_runtime.py entry`, `resolve`, `acquire`, `verify`, `store`, `finish`, `publish`, `seal` are separate bounded phases. commands_run.json preserves exact Docker/Git argv, exit codes and stdout/stderr hashes for captured commands. The local `docker image save --platform=linux/amd64` command and archive hash are in local_archive_verification.json. Read-only HTTPS metadata GETs for this exact repository are in registry_resolution.json; the short-lived public bearer token was not persisted. Only top index, amd64 manifest and config metadata were requested before pulling; no layer blob was requested in resolution.

The one mutation argv was `['docker', 'image', 'pull', '--platform=linux/amd64', 'moby/buildkit@sha256:cec9f139f45e93c5c69c60f8b07cfad9f43f4ef6b6a6cd917527fea5ff2e3dea']`. Exact stdout/stderr bytes and hashes are retained in pull.stdout.txt, pull.stderr.txt and pull_observation.json. No install, source fetch, base pull, build, run, retag, Docker network/container mutation or daemon restart occurred. Preliminary read-only tool observations verified entry and CLI help; the initial sandbox Docker connection was denied, and the authorized elevated read succeeded.

## 4. Tests / H Docker state delta

16 focused provenance/preservation checks passed, zero failed; no implementation unit suite was needed because only provisioning evidence was added. One runtime image row / one Engine image ID was added; none removed. All prior image identities and seven frozen bases are unchanged. Networks, containers, volumes, default builder selection/configuration and readable host configuration files are unchanged. Exact local exported config and layers were hashed without extracting archive members or starting a container. See validation_results.json and docker_state_before/after.json.

## 5. Contract compliance / J firewall

Required main HEAD and queried LIVE origin/main are both `5c007fbfbfc5b3529105a14f87127f50e1eab6d7` at entry and final verification. Canonical SHA remains `6a9028c79aa62f90db2b2d53def32ab23bffcfa3c71d2ec30d7fa64e741e3aae`, state PREPARATION_PLANNING_AUTHORIZED, event_count=2, PREPARATION_EXECUTION=NO. Index unchanged. No on-disk .airos state/contracts were present. The supplied global instructions and explicit transaction boundary govern this run.

BUILDERS_CREATED=0; BENCHMARK_ATTEMPTS_CONSUMED=0; BENCHMARK_IMAGE_BUILDS=0; BENCHMARK_DEPENDENCIES_INSTALLED=0; SOURCE_ACQUISITION_EXECUTED=NO; EVENT_3_CREATED=NO; CANONICAL_CURRENT_STATE_MODIFIED=NO; GIT_STAGE=NO; GIT_COMMIT=NO; GIT_PUSH=NO. Only one exact runtime pull was executed. Prior evidence was neither modified nor republished.

## 6. Risks and unknowns

Docker Desktop VM daemon config is not directly readable; preservation is established on host configuration hashes and observed Docker/Buildx surfaces. Snapshots do not rule out unrelated concurrent activity between observations. BuildKit process/version, all-seven-base bridge transport, output/load parity and restricted build egress have not been qualified. Runtime provisioning success is not benchmark or scientific validation.

## 7. Recommended next action

NEXT_GATE = RESUME_V6_RESTRICTED_BUILD_EGRESS_COMPATIBILITY_BRIDGE_FROM_RUNTIME_GATE

Resume the existing bridge from its runtime prerequisite using the exact immutable driver option in future_builder_binding.json. This provisioning transaction stops here; no builder creation or bridge qualification is executed.

# Run Report — V6 BuildKit frozen-base local OCI transport bridge

Date: 2026-10-06, Europe/Budapest.

STATUS = **V6_BUILDKIT_FROZEN_BASE_TRANSPORT_NAMED_CONTEXT_BLOCKED**

NEXT_GATE (recommended, not a Human-PI decision) = **HUMAN_PI_REVIEW_OF_V6_BUILDKIT_FROZEN_BASE_TRANSPORT_NAMED_CONTEXT_BLOCK**

## 1. Task summary / requested A–S results

The first frozen Engine base passed config and ordered uncompressed-tar diffID equivalence and produced a separate local OCI transport manifest. The installed Buildx/BuildKit path then rejected the requested OCI source reference before source consumption or RUN. Both the original FROM override and the alias request ended with `could not parse oci-layout reference <session-id>:@sha256:<digest>: invalid reference format`. No output image or qualified transport resulted. The required hard stop leaves all-seven qualification, output parity, restricted-egress resume and production integration incomplete.

One conditional authority exception occurred: the error classifier treated a generic `invalid reference format` as a FROM context-name rejection and invoked the alias fallback. The log actually names the OCI source-reference parser; it does not establish the permitted fallback condition. The second fixture request, exact one-token delta, failed raw logs and exception are explicitly preserved in `execution_corrections.json`. No further syntax variants or retries were executed. The classifier has been narrowed for future execution; this is not evidence that a future fallback condition has been qualified.

| Item | Observed result |
| --- | --- |
| A. Entry / lineage | `main`; local HEAD and LIVE origin/main verified at entry and final as `5c007fbfbfc5b3529105a14f87127f50e1eab6d7`. Canonical SHA `6a9028c79aa62f90db2b2d53def32ab23bffcfa3c71d2ec30d7fa64e741e3aae`, planning effective, event_count=2, PREPARATION_EXECUTION=NO. All 162 prior manifest-bound repository files and all prior external evidence remain exact. Prior blocked mechanism checked against its captured manifest-HEAD failure before RUN. |
| B. Frozen-base identity model | Original frozen registry identities remain scientific/base authorities. Engine inspect IDs, config descriptors and ordered diffIDs are recorded separately. The new OCI manifest is only an execution transport candidate. No recipe/attempt identity changed. |
| C. Engine export | One exact local `docker image save` without pull/network; archive 344779776 bytes, SHA `83580a0fbde0e1fdb9ff5c26fbee44b5ffa168568a5e2f624a81bff90d8161ac`. Stored only in the accepted external qualification child. Exactly one intended image, safe archive members and unique names checked. |
| D. OCI construction / equivalence | Exact config `sha256:5bf410ee7bb26f8f8fe9d7a2f9e9a05240cce0bc1bdbaee234f74f6b1b25ca94`, all 9 ordered rootfs diffIDs PASS. Engine's save contained gzip blobs; stdlib gzip recovered exact tar streams without filesystem unpacking or tar repacking. Config descriptor was recovered from the content-verified frozen manifest in the Engine export; Engine image Id was not mislabeled as a config digest. Local OCI manifest `sha256:9a64909eb826662bbf181357566002a8621652c18e3e24e90bf43f279f97ce8a`; 13 layout files, 935402499 bytes, linux/amd64. Actual layout hashes verified; constructor determinism tested on synthetic fixtures. |
| E. First-base result | Python 3.6.9 base archive equivalence PASS; BuildKit consumption FAIL before RUN. Exact preferred context and alias request each exit 1. No resulting Python/architecture/executable behavior qualification. |
| F. Seven-base results | Seven Engine identities revalidated and preserved. One exported/constructed; 0/7 BuildKit transports qualified. Remaining six not exported or built after the hard stop. |
| G. Production transport map | `seven_base_transport_map.json` records seven authoritative identities and the incomplete first candidate. No qualified seven-base rule, runtime-input installation or regeneration mechanism was constructed. |
| H. Dockerfile/context binding | Original fixture SHA `2529723dc07cd04d57afcd37d5adb560ca2951bd22a9d328d29cfa52445778b8`; alias fixture SHA `00be613df2430bce3e996373416589895e2290e73568a6a2940357cd9e46df09`. Delta replaces only the FROM source with `errpilot_frozen_base`. Neither binding mode qualified. The alias fallback condition was misclassified, as disclosed above. |
| I. Output parity | `--load` requested on both fixture solves, but parser failure prevented output. Tag lookup, image ID/layers and shared identity probes on a new output remain NOT_QUALIFIED. |
| J. Resumed proxy / egress | NOT_RUN: no proxy source/container, external network, local fixture, positive PyPI request, dependency operation, transport ARG or direct/NONE egress proof. |
| K. Enforcement identity | ABSENT; failure evidence hashes are not an enforcement receipt. |
| L. Runtime integration delta | NONE: no runtime/adapter/ledger/materializer/test source changed. No production transport or egress integration candidate was applied. |
| M. 641 / 583 / 58 | Exact rederivation and semantic population hash preserved; work item order, scientific recipes/revisions/attempt IDs unchanged. `matplotlib::1` and `matplotlib::8` remain non-dispatchable. |
| N. Repository / external evidence | All repository changes are in this new evidence directory. Exact artifact inventories are in `artifact_sha256.json` and `external_evidence_manifest.json`. External root: `/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1/qualification/buildkit_frozen_base_transport_bridge_v1`. Initial encoding-check observation and correction, failure logs, precleanup snapshots, final evidence and synthetic ledger fixtures are retained separately. No large archive/layout is in Git. |
| O. Cleanup | Exact observations persisted and fsynced before cleanup. Removed only the labeled builder, runtime container, owned state volume and internal network. Before/after Docker/configuration/selected-builder observations match: 57 image rows, 3 networks, 1 original container, 0 volumes. Exact BuildKit and seven frozen Python bases preserved. Archives/OCI remain qualification evidence, with no accepted production reliance. |
| P. Validation / rejection matrix | 8 bridge methods and 11 unchanged runtime/actual-filesystem methods PASS, 0 failures/errors/skips. 13/18 requested rejection classifications PASS (one uses the unchanged runtime pull guard); 5 dependent production/output classifications NOT_RUN. Ruff, AST, strict repository JSON/UTF-8, whitespace and git diff checks PASS. Independent integrity verifier receipt records its exact check count. Live source-consumption gate FAILED. |
| Q. Firewall | All required real benchmark attempts/claims/builds/dependency installs/source exports and registry pulls/resolution-request counters are 0. Source acquisition, oracle, event #3, canonical mutation, Git stage/commit/push are NO. Two synthetic build requests; zero fixture RUNs and zero output images. |
| R. Unresolved prerequisite | A demonstrated named local OCI source binding accepted by this exact installed Buildx/BuildKit frontend is missing. The observed parser error contains `<session-id>:@sha256:<transport>`; no alternate reference syntax, frontend/runtime or transport path has been verified or adopted. |
| S. Next gate | Human-PI review of the named-context block and conditional fallback exception. No scientific validation, execution effectivity or readiness recommendation is made. |

The seven frozen authorities are:

| Expected Python | Frozen scientific reference | This run |
| --- | --- | --- |
| 3.6.9 | `docker.io/library/python@sha256:036d4ab50fa49df89e746cf1b5369c88db46e8af2fbd08531788e7d920e9a491` | Archive equivalence PASS; BuildKit source parsing FAIL |
| 3.7.0 | `docker.io/library/python@sha256:8c386ccc41ce94c90bce07bae67a06c9d814153e6a9a9094c1257dfcd04c9657` | NOT_RUN first-base gate |
| 3.7.3 | `docker.io/library/python@sha256:e3e087ca7fe013554b3a8b8d4088ab33a9f13af85b5c3f37cd4e69a8e53f14e1` | NOT_RUN first-base gate |
| 3.7.4 | `docker.io/library/python@sha256:5be0532f833568d838b7b2d8726b66d0b8abe26f50a15b566aea4611d5951eac` | NOT_RUN first-base gate |
| 3.7.7 | `docker.io/library/python@sha256:f261d8fbee60f434341b7370fe0e5f3bea0deb0976ad323f0294d7dd694a9426` | NOT_RUN first-base gate |
| 3.8.1 | `docker.io/library/python@sha256:1d24b4656d4df536d8fa690be572774aa84b56c0418266b73886dc8138f047e6` | NOT_RUN first-base gate |
| 3.8.3 | `docker.io/library/python@sha256:ba23c4870854aa0718113e8765e7f46acbf141c6be1e66957ddcf130bd88d59d` | NOT_RUN first-base gate |

The first equivalence binding is:

`docker.io/library/python@sha256:036d4ab50fa49df89e746cf1b5369c88db46e8af2fbd08531788e7d920e9a491` ↔ exact config `sha256:5bf410ee7bb26f8f8fe9d7a2f9e9a05240cce0bc1bdbaee234f74f6b1b25ca94` + exact ordered 9 diffIDs ↔ local transport `sha256:9a64909eb826662bbf181357566002a8621652c18e3e24e90bf43f279f97ce8a`.

The three identities remain separate; full ordered diffIDs and compressed/uncompressed per-layer hashes are in `oci_layout_construction.json`.

## 2. Files inspected and changed

Inspected all six prior repository package manifests and exact referenced files; prior external manifests/inventories; the canonical descriptor and pinned contract, event, manifest and recipe dependencies through `load_inputs`; accepted runtime authority and all-641 population; prior blocked logs and exact immutable BuildKit binding; seven Engine inspections; the one Engine-save archive; local OCI blobs; dedicated builder/network/container and readable host/global configuration observations; unchanged runtime and tests.

No on-disk repository AGENTS.md, `.airos/current_state.md` or `.airos/contracts/` was present. The supplied global rules and explicit Human-PI request governed this task; the pinned V6 successor contract was inspected and validated through the existing input loader. No prior repository/external evidence, tracked source, canonical descriptor or Git index was changed. All changed/new files are evidence/executor/verification files within this new namespace and its accepted external qualification child.

## 3. Commands run

Used existing `.venv/bin/python`; no dependencies installed. Executed `transport_bridge.py` phases: `entry`, `export-first`, `recover-first-encoding-check`, `create-builder`, `first-consume`, `persist-block-and-cleanup`, `finish`; then `run_validation.py`, `seal_evidence.py` and `validate_evidence.py`. `commands_run.json` preserves exact captured Git/Docker/host observation argv, results and stdout/stderr hashes. The image-save argv/archive hash/size are in `archive_export_inventory.json`; runtime/focused/lint/diff argv and raw outputs are in `test_results.json` and accompanying text files.

Both fixture builds used the exact dedicated builder, linux/amd64, network NONE, no-cache, plain progress and explicit load. No benchmark build context or source export was submitted. Read-only LIVE Git identity checks were authorized by the entry/final requirement. All large writes stayed in the accepted external qualification child.

## 4. Tests passed / failed / not run

19 methods PASS: 8 new stdlib archive/layout/firewall methods and 11 unchanged runtime/actual-target-filesystem methods, with the actual filesystem fixture setup redirected in memory to this run's synthetic child. Focused tests exercise compressed/uncompressed exact tar streams, deterministic synthetic manifests, config/diffID/order corruption, blob/manifest/layout corruption, missing layout, unsafe/duplicate/multiple-image archives, nonregeneration, strict JSON, immutable population, event #3 and real-claim rejection. Runtime tests retain exact selection, all-641 identities, no-pull/once-only guards and default-deny dispatch.

Both actual BuildKit solves FAILED at OCI reference parsing before RUN. The 7/7, output parity, proxy positives/negatives and production integration rejection suite were NOT_RUN after that hard gate. Passing synthetic/mechanics tests do not qualify the failed transport or the absent egress bridge.

## 5. Contract compliance

All real-work and scientific-identity firewalls were preserved. Cleanup was limited to objects proven absent at entry and owned by label/name/ID; global selection/configuration and frozen images are exact after cleanup. No image pull, registry, retag, dependency install, real preparation, event #3 or Git publication occurred.

Compliance exception: the alias request was invoked without establishing a FROM context-name failure, owing to an overly broad parser-error classifier. This is recorded honestly rather than described as a contract-compliant fallback. It failed before RUN/output/egress and was followed by the hard stop. The encoding-check correction also retains its initial observation: a compressed distribution hash was initially compared to an uncompressed diffID; the corrected equality uses the exact decoded tar stream. No actual required equality failure was concealed or replaced by changed bytes.

## 6. Risks and unknowns

The requested OCI source syntax remains incompatible in this observed path. No alternative syntax was tried; no successful BuildKit source consumption, Python behavior on a new output, Engine load parity or restricted egress is established. Six other OCI transports are absent. The fallback classifier correction has code inspection and lint/syntax coverage, but no successful live condition qualification.

No packet capture or Docker VM/PF internal audit was performed. Registry conclusions are bounded to the source-parser failure, retained logs, internal-only attachment, absence of a default route and loopback upstream DNS. Readable host configuration hashes and Docker snapshots match; unreadable PF internals and concurrent activity between snapshots remain unknown. Intentionally malformed JSON/symlinks in external negative ledger fixtures are test evidence and are hashed as such; strict JSON validation applies to repository evidence records.

## 7. Recommended next action

Review `first_base_transport_result.json`, the two raw parser errors and `execution_corrections.json` at `HUMAN_PI_REVIEW_OF_V6_BUILDKIT_FROZEN_BASE_TRANSPORT_NAMED_CONTEXT_BLOCK`. Resolve the exact frontend/source-reference prerequisite within an explicit bounded follow-up, then re-establish the first-base gate before all-seven qualification, output parity or egress resume. This report recommends review, not an architecture or readiness decision. Real preparation remains unauthorized.

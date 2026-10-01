STATUS = BLOCK_03_GITLINK_SOURCE_EXPORT_COMPATIBILITY_BRIDGE_V1_CANDIDATE_READY_FOR_HUMAN_PI_ADJUDICATION

# Run Report — candidate only

## A. Authority

`HUMAN_PI_GITLINK_PROTOCOL_DECISION_V1 = ADOPTED` is the explicit authority supplied in the pasted Human-PI request. `BLOCK_03_GITLINK_SOURCE_EXPORT_COMPATIBILITY_BRIDGE_V1` authorizes only this source-representation candidate, repository tests, local Git-object dry exports, deterministic checks, and this report.

No materialization, Docker, subject setup/install/oracle, first-pass attempt, scientific classification, recipe/preparation/membership change, staging, commit, push, or tag is authorized. Live repository ref queries are the explicitly required read-only entry/final checks; they acquire no subject or submodule content.

## B. Entry state

- cwd/root: `/Users/wuyangchenxi/errpilot`
- branch: `main`
- local HEAD and verified LIVE origin/main: `7caa0ecb8d47f81e0a5ecdefcc758da4209b0238`
- historical authority baseline: `314229cc2dc6d4d1e8721a43e5b9189136a64b67`
- entry worktree/index: clean / clean; final index: empty
- attempts: `0 / 14`; production namespace absent
- exact members: `tqdm::6`, `PySnooper::3`, `sanic::3`, `sanic::5`, `PySnooper::2`, `cookiecutter::2`, `cookiecutter::1`
- exact candidate ranks: `259, 369, 380, 405, 431, 472, 485`
- accepted input bridge and controlling scientific inputs validated before writes
- no repository AGENTS.md, `.airos/current_state.md`, or `.airos/` contract found; supplied instructions and transaction control

## C. Implementation root cause

At the required committed HEAD, `screening/materialize_expansion_block_02_batch.py:69-71`, in `source_snapshot_identity`, rejects any entry whose type is not `blob` or whose mode is outside `100644`, `100755`, `120000`. All four exact cookiecutter revisions reproduced `BLOCKED_INPUT_IDENTITY: unsafe tracked source entry` before destination creation.

The missing representation was mode `160000` / type `commit`, not a build/runtime/oracle outcome. Normative classification: `SOURCE_EXPORT_REPRESENTATION_GAP`. No exclusion, NON_RETRY, readiness, or eligibility inference follows.

## D. Representation design

The existing `snapshot_manifest` hash is the canonical identity-bearing mechanism consumed by the request and materializer; the Block-03 request already binds both `sha` and `source_revision_sha`. The candidate uses this same mechanism without a new request field or alternate identity scheme.

- Sidecar: `<source-directory-name>.gitlinks.json`, a sibling outside the superproject source tree.
- Sidecar schema: `BLOCK_03_GITLINK_PROVENANCE_V1` with a deterministic `gitlinks` array.
- Verified sidecar content becomes the separate top-level `gitlink_provenance` field in `SOURCE_SNAPSHOT_MANIFEST_V2`; canonical JSON and its SHA-256 bind the complete record.
- The ordinary V2 `entries` array retains its exact regular-file, executable-mode, and raw-byte symlink semantics. Directories and the external sidecar do not become ordinary entries.
- The gitlink path is an empty real directory. No contents are populated, followed, or acquired.
- Without gitlinks, manifest shape, serialization, and identities remain unchanged. Historical V1/V2 evidence is not rewritten.
- Only the four exact adopted case/label/revision identities are recognized. Unknown historical/future gitlinks, extra/nested mappings, ambiguous paths, transformed entries, and mismatches block.
- Strict mapping and duplicate-field parsing, canonical sidecar bytes, no-follow descriptor traversal, regular-file checks, empty-placeholder checks, and nonblocking special-file rejection are enforced.
- Removing provenance changes the governed snapshot hash; tampering with it blocks. Provenance is identity-bearing, rather than merely a report annotation.

This is a narrowly scoped candidate source-representation amendment. It does not establish a universal submodule policy. Staging/transport must preserve the sibling sidecar with its source directory. The shared engine, dispatch, authority gates, recipes, and controller functions are unchanged; AST comparison to HEAD confirms only `snapshot_manifest`, `_source_identity`, and `source_snapshot_identity` changed.

## E. Files changed

| Absolute path | Purpose | Git state | SHA-256 |
| --- | --- | --- | --- |
| `/Users/wuyangchenxi/errpilot/evaluation/downstream_benchmark/screening/block_03_gitlink_source_export.py` | Scoped adopted identities, strict mapping validation, canonical sidecar and empty-directory verification. | untracked | `26ff2b8ffc6ddb9e36fd727bb5c4a3797d678f59aacf3e94e509b56c797ac200` |
| `/Users/wuyangchenxi/errpilot/evaluation/downstream_benchmark/screening/materialize_expansion_block_02_batch.py` | Recognize and validate the scoped gitlink; export an empty directory and sibling provenance; preserve non-gitlink hashes. | tracked modification | `a195445fddcd5ef9f51481d46611fb28cfe666c335ce7267dab805bc884c542c` |
| `/Users/wuyangchenxi/errpilot/evaluation/downstream_benchmark/screening/materializer.py` | Bind verified separate provenance into snapshot identity; preserve the supported bare-script Blocked exception type. | tracked modification | `d6d91339da310805386bfe20703f1bf3d25801f22b94ae52c6f150059e457f36` |
| `/Users/wuyangchenxi/errpilot/evaluation/downstream_benchmark/tests/test_block_03_gitlink_source_export.py` | 47 local-only tests, including repeated dry exports of the four frozen revisions. | untracked | `98a0dd77cf625fec53cdf2b026e3ce43b456b5963db2d80698e191ee0fcc7b6e` |
| `/Users/wuyangchenxi/errpilot/evaluation/downstream_benchmark/BLOCK_03_GITLINK_SOURCE_EXPORT_COMPATIBILITY_BRIDGE_V1_CANDIDATE_REPORT.md` | Human-PI candidate review report | untracked | Self-hash excluded from report; supplied in final inventory |

Validation artifacts and all temporary exports reside beneath `/private/tmp/errpilot-block03-gitlink-bridge-v1-yzihmlwj`. They are outside the repository and outside the production namespace. Key evidence: `entry_preservation.json`, `source_review_evidence.json`, `four_revision_evidence.json`, `historical_source_evidence.json`, `final_source_test_evidence.json`, `regression_initial_evidence.json`, `regression_cleanup_corrected_evidence.json`, and `post_validation_preservation.json`.

## F. Tests and validation

- Final source selection: **58 passed, 0 failed, 1 deselected, 8 subtests passed**. This comprises 47 new gitlink/source tests and 11 existing V2 manifest tests.
- Existing bounded regression selection: **223 unique tests verified** across the initial 204 passing tests and corrected rerun of the 19 affected tests. Initial run: 204 passed, 19 failed, 2 teardown errors, 2 deselected, 77 subtests passed. Corrected affected selection: 19 passed, 0 failed, 1 deselected, 35 subtests passed. These are multiple runs, not a claimed single clean 223-test run.
- Initial regression failures were reproduced and classified as descriptor-relative temporary cleanup paths incorrectly rejected by the scratch-only transaction runner. Only that scratch runner was corrected, using the actual directory-descriptor path; repository regression tests and production firewalls were unchanged.
- Earlier guard setup also rejected pytest temporary capture/log paths and read-only `git branch --show-current` / `git remote get-url origin`; the runner was constrained to the scratch root, `/dev/null`, and exact read-only metadata operations before successful validation.
- Final source review reproduced and corrected a candidate exception-class mismatch for the supported bare-script snapshot reader; the new regression passes. The sidecar reader also rejects FIFOs without waiting for input.
- Historical read-only comparison: **16/16** Block-01/02 revision identities match both the committed exporter and frozen ledger SHA-256 values.
- Final Ruff: passed. `git diff --check`: passed. Full repository pytest, Docker suites, shared-engine tests, builds, runtime/setup/oracles were not run.
- The two regression deselections invoke the real shared engine: `test_synthetic_entrypoint_rejects_real_case_and_alternate_root` and `test_unsafe_second_revision_blocks_before_any_docker_call`. No production or synthetic engine call was allowed.

Exact final source command:

```sh
TMPDIR=/private/tmp/errpilot-block03-gitlink-bridge-v1-yzihmlwj PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0 python3 /private/tmp/errpilot-block03-gitlink-bridge-v1-yzihmlwj/run_guarded_tests.py \
  evaluation/downstream_benchmark/tests/test_block_03_gitlink_source_export.py \
  evaluation/downstream_benchmark/tests/test_source_snapshot_symlink_v2.py::ManifestV2Tests \
  -k 'not test_unsafe_second_revision_blocks_before_any_docker_call' -q -p no:cacheprovider --tb=short \
  --basetemp=/private/tmp/errpilot-block03-gitlink-bridge-v1-yzihmlwj/final-source-scratch
```

Exact initial bounded regression command:

```sh
TMPDIR=/private/tmp/errpilot-block03-gitlink-bridge-v1-yzihmlwj PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0 python3 /private/tmp/errpilot-block03-gitlink-bridge-v1-yzihmlwj/run_guarded_tests.py \
  evaluation/downstream_benchmark/tests/test_source_snapshot_symlink_v2.py::ManifestV2Tests \
  evaluation/downstream_benchmark/tests/test_expansion_block_02_batch.py \
  evaluation/downstream_benchmark/tests/test_block_03_runtime_activation.py \
  evaluation/downstream_benchmark/tests/test_block_03_materializer_bridge.py \
  evaluation/downstream_benchmark/tests/test_environment_materializer.py::ProductionGateTests \
  evaluation/downstream_benchmark/tests/test_environment_materializer.py::ExpansionBlock01GateTests \
  evaluation/downstream_benchmark/tests/test_environment_materializer.py::ExpansionBlock02GateTests \
  evaluation/downstream_benchmark/tests/test_block_03_preparation_compatibility.py \
  evaluation/downstream_benchmark/tests/test_expansion_block_03_preparation.py \
  evaluation/downstream_benchmark/tests/test_expansion_block_01_preparation.py \
  evaluation/downstream_benchmark/tests/test_expansion_block_02_preparation.py \
  evaluation/downstream_benchmark/tests/test_environment_build_recipes.py \
  evaluation/downstream_benchmark/tests/test_screening_environment_audit.py \
  evaluation/downstream_benchmark/tests/test_screening_executor.py::ScreeningExecutorTests::test_committed_pre_eligibility_ledgers_pass_controlling_validation \
  -k 'not test_synthetic_entrypoint_rejects_real_case_and_alternate_root and not test_unsafe_second_revision_blocks_before_any_docker_call' -q -p no:cacheprovider --tb=short \
  --basetemp=/private/tmp/errpilot-block03-gitlink-bridge-v1-yzihmlwj/regression-scratch
```

Exact corrected affected-selection command:

```sh
TMPDIR=/private/tmp/errpilot-block03-gitlink-bridge-v1-yzihmlwj PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0 python3 /private/tmp/errpilot-block03-gitlink-bridge-v1-yzihmlwj/run_guarded_tests.py \
  evaluation/downstream_benchmark/tests/test_source_snapshot_symlink_v2.py::ManifestV2Tests \
  evaluation/downstream_benchmark/tests/test_environment_materializer.py::ExpansionBlock01GateTests::test_cli_dispatches_one_revision_at_a_time \
  evaluation/downstream_benchmark/tests/test_environment_materializer.py::ExpansionBlock01GateTests::test_ledger_rejects_mutated_count_order_schema_and_hash \
  evaluation/downstream_benchmark/tests/test_environment_materializer.py::ExpansionBlock02GateTests::test_block_01_and_initial_40_ledgers_remain_valid \
  evaluation/downstream_benchmark/tests/test_environment_materializer.py::ExpansionBlock02GateTests::test_blocked_cases_and_wrong_tokens_never_enter_engine \
  evaluation/downstream_benchmark/tests/test_environment_materializer.py::ExpansionBlock02GateTests::test_frozen_ten_cases_return_eight_ready_and_twelve_identities \
  evaluation/downstream_benchmark/tests/test_environment_materializer.py::ExpansionBlock02GateTests::test_mutated_frozen_hash_and_semantics_fail_closed \
  evaluation/downstream_benchmark/tests/test_environment_materializer.py::ExpansionBlock02GateTests::test_request_identity_namespace_and_source_independent_shape \
  evaluation/downstream_benchmark/tests/test_environment_materializer.py::ExpansionBlock02GateTests::test_revision_specific_buggy_and_fixed_dispatch_independently \
  -k 'not test_unsafe_second_revision_blocks_before_any_docker_call' -q -p no:cacheprovider --tb=short \
  --basetemp=/private/tmp/errpilot-block03-gitlink-bridge-v1-yzihmlwj/regression-cleanup-corrected
```

Historical source comparison and static checks:

```sh
TMPDIR=/private/tmp/errpilot-block03-gitlink-bridge-v1-yzihmlwj PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0 python3 /private/tmp/errpilot-block03-gitlink-bridge-v1-yzihmlwj/validate_historical_sources.py
PYTHONDONTWRITEBYTECODE=1 python3 -m ruff check --no-cache evaluation/downstream_benchmark/screening/block_03_gitlink_source_export.py evaluation/downstream_benchmark/screening/materialize_expansion_block_02_batch.py evaluation/downstream_benchmark/screening/materializer.py evaluation/downstream_benchmark/tests/test_block_03_gitlink_source_export.py
git diff --check
git rev-parse --show-toplevel HEAD
git branch --show-current
git status --short
git diff --cached --name-only
git ls-remote --exit-code origin refs/heads/main
```

The first sandbox live-ref query failed DNS resolution; the explicitly authorized elevated read-only query succeeded. Initial local tree audits used `git ls-tree -rz --full-tree`, `git cat-file -t`, and `git cat-file blob` against existing mirrors. Export streaming used only local `git cat-file --batch`. No submodule object lookup/acquisition was required.

Final source guard: 148 actual read-only Git subprocesses; historical comparison guard: 81; initial controller/materializer regression guard: 2047. Successful runs recorded zero real-engine calls, zero Docker calls, and zero forbidden-process attempts. Earlier guarded read-only query rejections executed no forbidden process.

## G. Four-revision result

| Case / label | Superproject revision | Result | Empty / unpopulated / deterministic | Snapshot SHA-256 |
| --- | --- | --- | --- | --- |
| `cookiecutter::2` BUGGY | `d7e7b28811e474e14d1bed747115e47dcdd15ba3` | SOURCE_EXPORT_REPRESENTABLE | PASS / PASS / PASS | `b08bdc5ed2ba1c0ca3e513452134985314dd96cfc0d062158d5f85800c906a8c` |
| `cookiecutter::2` FIXED | `90434ff4ea4477941444f1e83313beb414838535` | SOURCE_EXPORT_REPRESENTABLE | PASS / PASS / PASS | `260eb5fd61b4c2e78eeaefe14eabf08df482a307ad4ed402976333fdc6d2b546` |
| `cookiecutter::1` BUGGY | `c15633745df6abdb24e02746b82aadb20b8cdf8c` | SOURCE_EXPORT_REPRESENTABLE | PASS / PASS / PASS | `865d329c3d4f16350bd3c3446d02729453aa839d1f0d0a7605d6445eeb7d32ce` |
| `cookiecutter::1` FIXED | `7f6804c4953a18386809f11faf4d86898570debc` | SOURCE_EXPORT_REPRESENTABLE | PASS / PASS / PASS | `f58b97db7967697ea66fc00a9bca4aec15dea5b0948021230204281c567614df` |

For each revision, two temporary exports and read-only derivation agree; the real directory contains no submodule files, the ordinary manifest contains no gitlink file entry, and local-only process guards observe no submodule/network/Docker/engine call.

## H. Gitlink provenance

Each row above binds its exact `superproject_revision`. All four bind exactly:

```text
path = docs/HelloCookieCutter1
mode = 160000
object = 239ea692896301eaa280dd407fdd4d5c55cf6998
declared_url = https://github.com/BruceEckel/HelloCookieCutter1
```

| Case / label | Canonical provenance SHA-256 | Ordinary-file manifest SHA-256 |
| --- | --- | --- |
| `cookiecutter::2` BUGGY | `2f51d1713f7b96746ac05446c7c2c4fe9099172039a26d3d6470382dc7fa6ade` | `3cbe95608c173e4ddb36ee31a6dd1dc0c771fb784383aca20da2bd23f84fafb8` |
| `cookiecutter::2` FIXED | `3eb4a3077afe5c637e5bc93a057a4db7680b59a37fb2cc1b69cb7c0984fa00b8` | `42d4b96db33eb479e7b8f5426d9413435b44582db16e75e77c4d32b75f9ba555` |
| `cookiecutter::1` BUGGY | `723779bc83545d17f7e0043bee3770067dc2b69f592ee130cc5b3bc577fab3ef` | `0b24874aa0d4f5e1780adf421f05a1e673e8ab93f842fde9c3ecad22216ecef2` |
| `cookiecutter::1` FIXED | `015141a180af543e2c38c811d241158bc94e97acb897cf46c8b448e5a71f18bf` | `d8ce01aae1fe5acd9538305d34655c62e75ddaca0cc2c2adff3690cd2c9fdfec` |

The export represents the superproject before separately governed BugsInPy fixed-test/helper injection. Complete byte-for-byte equivalence to the entire canonical pre-setup BugsInPy workspace is not claimed.

## I. Fail-closed matrix

```text
MISSING_GITMODULES_REJECTED = PASS
PATH_MISMATCH_REJECTED = PASS
CONFLICTING_MAPPING_REJECTED = PASS
WRONG_OBJECT_REJECTED = PASS
WRONG_URL_REJECTED = PASS
UNSUPPORTED_NESTED_SEMANTICS_REJECTED = PASS
SILENT_GITLINK_DROP_PREVENTED = PASS
NETWORK_ACQUISITION_PREVENTED = PASS
```

Additional passing cases cover malformed/UTF-8/relative mappings, unexpected type/mode/revision/scope, duplicate records, substituted files/symlinks, tampered or removed sidecars, noncanonical provenance, substituted parent directories, missing/populated placeholders, and special sidecar files. Real subprocesses are restricted to read-only Git; no acquisition command is used by the bridge.

## J. Attempt state

```text
FIRST_PASS_PLANNED_GOVERNED_IDENTITIES = 14
FIRST_PASS_ATTEMPTS_CONSUMED_BEFORE = 0
FIRST_PASS_ATTEMPTS_CONSUMED_AFTER = 0
```

The complete external path inventory remains identical to entry; no Block-03 materialization namespace or attempt record exists.

## K. Scientific state

```text
cumulative metadata admissions = 67
accepted exclusions = 34
UNSUPPORTED_ENVIRONMENT = 9
DEPENDENCY_SETUP_FAILURE = 23
ORACLE_COMMAND_INVALID = 2
environment-ready = 26
required slots = 28
oracle outcomes = 0
cases_manifest.csv = header-only
```

Reconciliation: admissions 40 + 10 + 10 + 7; exclusions counted directly; environment-ready cases 19 + 4 + 3, including the existing Batch-01 identity completion. Required slots are the frozen 24 final plus four pilot cases. Header-only manifest and empty screening evidence remain unchanged. No oracle was executed to establish this state.

## L. Firewall attestation

```text
SUBMODULE_INIT_EXECUTED = NO
SUBMODULE_UPDATE_EXECUTED = NO
SUBMODULE_CLONE_EXECUTED = NO
SUBMODULE_FETCH_EXECUTED = NO
SUBMODULE_NETWORK_ACQUISITION_EXECUTED = NO
PRODUCTION_SOURCE_EXPORT_CREATED = NO
FIRST_PASS_ATTEMPT_CONSUMED = NO
DOCKER_BUILD_EXECUTED = NO
DOCKER_CONTAINER_EXECUTED = NO
SUBJECT_DEPENDENCY_INSTALLATION_EXECUTED = NO
SUBJECT_SETUP_EXECUTED = NO
BUGGY_ORACLE_EXECUTED = NO
FIXED_ORACLE_EXECUTED = NO
ELIGIBILITY_CLASSIFICATION_PERFORMED = NO
ACCEPTED_EXCLUSION_ADJUDICATION_PERFORMED = NO
GIT_STAGE_PERFORMED = NO
GIT_COMMIT_PERFORMED = NO
GIT_PUSH_PERFORMED = NO
```

Post-validation preservation verifies 454 unchanged entry tracked files, 56 unchanged external Block-03 preparation files, 112 unchanged historical attempt/identity/ledger JSON records, and 280817 unchanged external paths. Only the two authorized tracked source files differ; the helper, tests, and this report are untracked candidate files. Runtime controller, input bridge, preparation/recipe artifacts, membership, ranking/seed/cursor/caps, and scientific records retain their entry bytes.

## M. Lifecycle state

```text
HUMAN_PI_GITLINK_PROTOCOL_DECISION_V1 = ADOPTED
BLOCK_03_GITLINK_SOURCE_EXPORT_COMPATIBILITY_BRIDGE_V1 = CANDIDATE_ONLY
HUMAN_PI_ACCEPTED = NO
FROZEN = NO
PERSISTED = NO
COMMITTED = NO
REMOTE_PUBLISHED = NO
```

`PERSISTED = NO` denotes absence of an accepted/frozen lifecycle persistence transaction. Working candidate files and this requested report exist locally; no lifecycle closure or adoption artifact was created. No materialization, environment readiness, eligibility, accepted exclusion, or scientific validation is implied.

## N. Next authority gate and risks

```text
NEXT_GATE = HUMAN_PI_REVIEW_OF_BLOCK_03_GITLINK_SOURCE_EXPORT_COMPATIBILITY_BRIDGE_V1
FIRST_PASS_ATTEMPTS_CONSUMED = 0
MATERIALIZATION_EXECUTION_REMAINS_BLOCKED
```

Recommended next action: Human-PI review of the exact candidate diff, sibling-sidecar contract, and source-representability evidence. Acceptance, freeze/persistence, commit/publication, and any first-pass execution require their own authority. Runtime buildability and setup/oracle behavior remain untested. This candidate intentionally rejects all unadopted gitlinks and depends on the existing local accepted evidence for four-revision integration tests.

Contract compliance: source representation and local-only validation only; all negative execution, scientific, Git-write, and scope boundaries preserved. Stop after this report.

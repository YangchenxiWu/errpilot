STATUS = BLOCK_03_GITLINK_SIDECAR_TRANSPORT_COMPATIBILITY_BRIDGE_V1_CANDIDATE_READY_FOR_HUMAN_PI_ADJUDICATION

# Block-03 gitlink sidecar transport compatibility bridge V1 candidate Run Report

## A. Authority and task summary

The pasted Human-PI transaction authorizes only
`BLOCK_03_GITLINK_SIDECAR_TRANSPORT_COMPATIBILITY_BRIDGE_V1`: a minimal transport
change, repository-owned tests, non-materializing temporary staging validation,
and this single candidate report. The adopted gitlink protocol, accepted source
exporter, canonical serialization, provenance fields, snapshot hashes, empty
placeholders, recipes, preparation, membership, and runtime authority remain
unchanged. No real materialization, attempt, Docker, subject setup/dependencies,
oracle, submodule acquisition, eligibility/exclusion adjudication, Git staging,
commit, push, or tag is authorized or performed.

## B. Entry state and inspected evidence

```text
cwd = /Users/wuyangchenxi/errpilot
branch = main
HEAD = 8f60377d809ce4b8e1398cc87a9cf366d50c18c4
LIVE_origin/main = 8f60377d809ce4b8e1398cc87a9cf366d50c18c4
entry_worktree = clean
entry_index = clean
first_pass_attempts = 0 / 14
historical_runtime_authority_baseline = 314229cc2dc6d4d1e8721a43e5b9189136a64b67
```

The first sandbox live-ref query failed DNS; the explicitly required elevated
read-only `git ls-remote origin refs/heads/main` succeeded before edits.
No repository-local AGENTS.md, `.airos/current_state.md`, or `.airos/` contract
was found. The supplied global rules and explicit transaction control this work.
The historical runtime-authority baseline is an ancestor of HEAD.

Committed bytes inspected: `screening/block_03_gitlink_source_export.py`,
`screening/materialize_expansion_block_02_batch.py`, and the shared materializer.
Also inspected: accepted source-export lifecycle closure, runtime-controller
lifecycle closure, Block-03 materializer input authority/adapter, runtime
activation controller, preparation lifecycle record, PROTOCOL, relevant source,
materializer, controller, Block-01/02 tests, and current scientific CSV ledgers.
The accepted input adapter validated all seven ordered recipes. Read-only
source identity derivation passed for all fourteen governed BUGGY/FIXED
identities, including the four cookiecutter revisions, before repository edits.
No production Block-03 materialization namespace or attempt record existed.

Scratch evidence root: `/private/tmp/errpilot-block03-sidecar-transport-v1-scjcm1yh`.
Before implementation, hashes for all 460 tracked files, a materializer
preimage, 280817 external paths/types/modes, and 284 preparation/controller/
attempt-record hashes were preserved. The external root is read-only throughout
validation; temporary exports and staging occur only inside scratch.

## C. Root cause and transport ownership

The committed exporter derives `source.with_name(source.name + ".gitlinks.json")`
in `sidecar_path()`; the sidecar is outside the subject filesystem tree.
`source_snapshot_identity()` writes accepted canonical provenance there and
includes it as top-level `gitlink_provenance` in the V2 snapshot hash.
`gitlinks.read()` validates canonical bytes, all identity fields, `.gitmodules`,
and the empty real placeholder using no-follow descriptor traversal.

The committed omission is `_materialize_checked()` at baseline line 943:
`shutil.copytree(source, context / "source", symlinks=True)` copied only the
directory, omitting its sibling sidecar. Subsequent `context_manifest()` did not
verify a destination source-package identity. `verify_base()` also ran before
context staging. Shared materializer context staging is the established
transport owner for the initial cohort and Blocks 01/02/03. Neither exporter
policy nor controller authority needs a second transport ownership model.

## D. Transport design and contract compliance

`transport_source_package(source, destination, expected_identity)` is a local
filesystem operation with no engine, Git, Docker, network, or attempt path.
It reads the source manifest using the unchanged accepted snapshot validator
and rejects any mismatch with the caller's governed hash. The expected hash
already binds required provenance, including the superproject revision;
a missing required sidecar cannot satisfy it.

When provenance is present, the helper reads its exact existing bytes using
the accepted no-follow regular-file reader, checks them against the already
validated record, copies the source tree with the historical
`copytree(..., symlinks=True)`, and writes those same bytes exclusively to
`sidecar_path(destination)`. It never exports, derives, regenerates, normalizes,
reconstructs, or fetches provenance. It re-reads the destination package and
requires identical manifests, the same governed snapshot hash, and identical
companion bytes. Missing/malformed/substituted/mismatched source or destination
packages raise `BLOCKED_INPUT_IDENTITY`, without scientific exclusion reasons.

For destination `context / "source"`, the unchanged naming function mechanically
derives `context / "source.gitlinks.json"`. This is a helper-derived sibling,
not an invented convention. The sidecar remains outside subject source and is
included by the existing build-context filesystem manifest. Its presence changes
that context's content hash; the governed source snapshot hash is unchanged.
Non-gitlink packages gain no sidecar; regular files, modes, raw symlink targets,
and context content remain identical to historical transport.

The engine's existing staging loop now calls this helper and retains each
revision's own source/context manifest. All contexts are staged and verified
before `verify_base()` or any Docker build. This changes validation order so
transport rejection precedes runtime probes; runtime execution remains untested.
The authority dispatchers, input validators, snapshot functions, recipe and
Dockerfile semantics are unchanged. The staging-only helper is dynamically
tested; the real engine integration order is checked statically under the
no-engine boundary.

## E. Files changed

| Repository-relative path | Purpose | State | SHA-256 |
| --- | --- | --- | --- |
| `evaluation/downstream_benchmark/screening/materializer.py` | Source-package transport and destination verification before runtime probes | tracked, modified, unstaged | `98ba9a45b6b9beaaf00119efe0da07f5513a1d56578d00a5a2dc59cc088dea0c` |
| `evaluation/downstream_benchmark/tests/test_block_03_gitlink_sidecar_transport.py` | Synthetic fail-closed matrix, local four-revision dry transport, historical Block-01/02 transport and integration-order regression | untracked | `81f29020de86c83164dc606508cc7af4ff8ad0bfc3c40ff40f9773446924514d` |
| `evaluation/downstream_benchmark/BLOCK_03_GITLINK_SIDECAR_TRANSPORT_COMPATIBILITY_BRIDGE_V1_CANDIDATE_REPORT.md` | This candidate Run Report | untracked | SELF_HASH_EXCLUDED; exact post-write SHA-256 supplied in final inventory and chat Run Report |

No other repository file is changed. Accepted exporter/helper/test bytes,
preparation, recipe/membership ledgers, input authority and runtime controller
retain their pre-transaction hashes. A saved candidate report does not establish
the governance lifecycle state `PERSISTED`.

## F. Tests, commands and validation

Synthetic transport command:

```sh
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 VALIDATION_RUN=transport-r1 python3 \
  /private/tmp/errpilot-block03-sidecar-transport-v1-scjcm1yh/run_guarded_tests.py \
  evaluation/downstream_benchmark/tests/test_block_03_gitlink_sidecar_transport.py \
  -k 'not frozen_cookiecutter and not historical_block' -q -p no:cacheprovider \
  --tb=short --basetemp=/private/tmp/errpilot-block03-sidecar-transport-v1-scjcm1yh/transport-tests-r1
```

Result: **24 passed, 0 failed, 8 deselected**.

Final bounded regression command:

```sh
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 VALIDATION_RUN=regression-v2 python3 \
  /private/tmp/errpilot-block03-sidecar-transport-v1-scjcm1yh/run_guarded_tests_v2.py \
  evaluation/downstream_benchmark/tests/test_block_03_gitlink_sidecar_transport.py \
  evaluation/downstream_benchmark/tests/test_block_03_gitlink_source_export.py \
  evaluation/downstream_benchmark/tests/test_source_snapshot_symlink_v2.py::ManifestV2Tests \
  evaluation/downstream_benchmark/tests/test_block_03_runtime_activation.py \
  evaluation/downstream_benchmark/tests/test_block_03_materializer_bridge.py \
  evaluation/downstream_benchmark/tests/test_environment_materializer.py::ProductionGateTests \
  evaluation/downstream_benchmark/tests/test_environment_materializer.py::ExpansionBlock01GateTests \
  evaluation/downstream_benchmark/tests/test_environment_materializer.py::ExpansionBlock02GateTests \
  evaluation/downstream_benchmark/tests/test_expansion_block_02_batch.py \
  evaluation/downstream_benchmark/tests/test_block_03_preparation_compatibility.py \
  evaluation/downstream_benchmark/tests/test_expansion_block_03_preparation.py \
  evaluation/downstream_benchmark/tests/test_expansion_block_01_preparation.py \
  evaluation/downstream_benchmark/tests/test_expansion_block_02_preparation.py \
  evaluation/downstream_benchmark/tests/test_environment_build_recipes.py \
  evaluation/downstream_benchmark/tests/test_screening_environment_audit.py \
  evaluation/downstream_benchmark/tests/test_screening_executor.py::ScreeningExecutorTests::test_committed_pre_eligibility_ledgers_pass_controlling_validation \
  -k 'not test_synthetic_entrypoint_rejects_real_case_and_alternate_root and not test_unsafe_second_revision_blocks_before_any_docker_call' \
  -q -p no:cacheprovider --tb=short \
  --basetemp=/private/tmp/errpilot-block03-sidecar-transport-v1-scjcm1yh/regression-tests-v2
```

Result: **302 passed, 0 failed, 77 subtests passed, 2 deselected**, 72.58 seconds.
The two deselected tests invoke the real shared engine; no Docker suites are
collected. This selection includes all new transport tests, the unchanged
47-test gitlink exporter suite, source/symlink regressions, controller/authority
and materializer gates, preparation/recipe/audit regressions, and Block-01/02
checks. Actual local historical transport compares both BUGGY/FIXED revisions
of Block-01 `sanic::2` and Block-02 `PySnooper::1` with historical `copytree`
contexts; both context manifests/hashes match exactly. This is representative
transport coverage, not new materialization evidence for historical blocks.

The guard is installed before collection, permits only local read-only Git
processes, rejects network/alternate subprocesses and real engine/Docker
functions, and limits file mutations to scratch. Successful final run:
**2339 read-only Git processes; 0 forbidden calls**. Test-owned mock dispatches
and status strings are not actual attempts or materialization results.

Initial harness runs are retained: a setup-only guard failure rejected pytest's
`/dev/null` log sink; the first broad run incorrectly resolved descriptor-relative
scratch cleanup as repository paths, yielding **19 failed, 283 passed, 2 errors,
77 subtests passed, 2 deselected**. All failures were inspected and traced to
scratch cleanup in the guard. The V2 guard resolves the descriptor directory
before enforcing the same scratch-only write boundary. No production/test
semantics were changed to make these checks pass. Entry diagnostic scripts also
required correction of a read-only Git allowlist and historical CSV status-column
handling before the successful pre-write entry gate.

Additional commands/checks:

```sh
pwd
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git status --porcelain=v1
git diff --cached --name-only
git rev-list --left-right --count HEAD...origin/main
git ls-remote origin refs/heads/main
git show --stat --oneline HEAD
git merge-base --is-ancestor 314229cc2dc6d4d1e8721a43e5b9189136a64b67 HEAD
PYTHONDONTWRITEBYTECODE=1 python3 -m ruff check --no-cache \
  evaluation/downstream_benchmark/screening/materializer.py \
  evaluation/downstream_benchmark/tests/test_block_03_gitlink_sidecar_transport.py
git diff --check
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0 python3 \
  /private/tmp/errpilot-block03-sidecar-transport-v1-scjcm1yh/check_preservation.py
```

Changed-source Ruff and whitespace checks passed. All changed/created repository
files were re-read. Untracked test/report whitespace is checked separately with
`git diff --no-index --check /dev/null <path>`. The final hash inventory and live
ref verification are performed after this report is saved. Protected function
ASTs compare identically against the preimage: `_safe_link_target`,
`_manifest_entries`, `snapshot_manifest`, `context_manifest`, Block-03 input and
runtime-authority validators, and Block-01/02/03 dispatch functions.

## G. Four-revision temporary dry transport

Each source uses existing local objects and the unchanged accepted exporter.
No production output root is used. The exporter regression also repeats all four
exports and compares canonical bytes/manifests deterministically. All four dry
transports verified source/destination provenance, unchanged source identity,
real empty placeholders, identical bytes, and no submodule contents. No network,
Docker, subject process, engine, or governed attempt occurs.

### cookiecutter::2 BUGGY

```text
STATUS = SOURCE_PACKAGE_TRANSPORT_REPRESENTABLE
superproject_revision = d7e7b28811e474e14d1bed747115e47dcdd15ba3
source_sidecar = /private/tmp/errpilot-block03-sidecar-transport-v1-scjcm1yh/regression-tests-v2/test_frozen_cookiecutter_dry_t0/snapshot.gitlinks.json
destination_sidecar = /private/tmp/errpilot-block03-sidecar-transport-v1-scjcm1yh/regression-tests-v2/test_frozen_cookiecutter_dry_t0/context/source.gitlinks.json
source_and_destination_snapshot_sha256 = b08bdc5ed2ba1c0ca3e513452134985314dd96cfc0d062158d5f85800c906a8c
source_and_destination_sidecar_sha256 = 2f51d1713f7b96746ac05446c7c2c4fe9099172039a26d3d6470382dc7fa6ade
empty_placeholder = PASS
identical_sidecar_bytes = PASS
provenance_identity = PASS
no_submodule_contents = PASS
no_submodule_acquisition = PASS
```

### cookiecutter::2 FIXED

```text
STATUS = SOURCE_PACKAGE_TRANSPORT_REPRESENTABLE
superproject_revision = 90434ff4ea4477941444f1e83313beb414838535
source_sidecar = /private/tmp/errpilot-block03-sidecar-transport-v1-scjcm1yh/regression-tests-v2/test_frozen_cookiecutter_dry_t1/snapshot.gitlinks.json
destination_sidecar = /private/tmp/errpilot-block03-sidecar-transport-v1-scjcm1yh/regression-tests-v2/test_frozen_cookiecutter_dry_t1/context/source.gitlinks.json
source_and_destination_snapshot_sha256 = 260eb5fd61b4c2e78eeaefe14eabf08df482a307ad4ed402976333fdc6d2b546
source_and_destination_sidecar_sha256 = 3eb4a3077afe5c637e5bc93a057a4db7680b59a37fb2cc1b69cb7c0984fa00b8
empty_placeholder = PASS
identical_sidecar_bytes = PASS
provenance_identity = PASS
no_submodule_contents = PASS
no_submodule_acquisition = PASS
```

### cookiecutter::1 BUGGY

```text
STATUS = SOURCE_PACKAGE_TRANSPORT_REPRESENTABLE
superproject_revision = c15633745df6abdb24e02746b82aadb20b8cdf8c
source_sidecar = /private/tmp/errpilot-block03-sidecar-transport-v1-scjcm1yh/regression-tests-v2/test_frozen_cookiecutter_dry_t2/snapshot.gitlinks.json
destination_sidecar = /private/tmp/errpilot-block03-sidecar-transport-v1-scjcm1yh/regression-tests-v2/test_frozen_cookiecutter_dry_t2/context/source.gitlinks.json
source_and_destination_snapshot_sha256 = 865d329c3d4f16350bd3c3446d02729453aa839d1f0d0a7605d6445eeb7d32ce
source_and_destination_sidecar_sha256 = 723779bc83545d17f7e0043bee3770067dc2b69f592ee130cc5b3bc577fab3ef
empty_placeholder = PASS
identical_sidecar_bytes = PASS
provenance_identity = PASS
no_submodule_contents = PASS
no_submodule_acquisition = PASS
```

### cookiecutter::1 FIXED

```text
STATUS = SOURCE_PACKAGE_TRANSPORT_REPRESENTABLE
superproject_revision = 7f6804c4953a18386809f11faf4d86898570debc
source_sidecar = /private/tmp/errpilot-block03-sidecar-transport-v1-scjcm1yh/regression-tests-v2/test_frozen_cookiecutter_dry_t3/snapshot.gitlinks.json
destination_sidecar = /private/tmp/errpilot-block03-sidecar-transport-v1-scjcm1yh/regression-tests-v2/test_frozen_cookiecutter_dry_t3/context/source.gitlinks.json
source_and_destination_snapshot_sha256 = f58b97db7967697ea66fc00a9bca4aec15dea5b0948021230204281c567614df
source_and_destination_sidecar_sha256 = 015141a180af543e2c38c811d241158bc94e97acb897cf46c8b448e5a71f18bf
empty_placeholder = PASS
identical_sidecar_bytes = PASS
provenance_identity = PASS
no_submodule_contents = PASS
no_submodule_acquisition = PASS
```

## H. Transport fail-closed matrix

```text
MISSING_SOURCE_SIDECAR_REJECTED = PASS
MALFORMED_SOURCE_SIDECAR_REJECTED = PASS
WRONG_SUPERPROJECT_BINDING_REJECTED = PASS
WRONG_GITLINK_PATH_REJECTED = PASS
WRONG_GITLINK_MODE_REJECTED = PASS
WRONG_GITLINK_OBJECT_REJECTED = PASS
WRONG_DECLARED_URL_REJECTED = PASS
MISSING_DESTINATION_SIDECAR_REJECTED = PASS
DESTINATION_SIDECAR_TAMPER_REJECTED = PASS
SILENT_SIDECAR_DROP_PREVENTED = PASS
```

Additional passing tests cover noncanonical/duplicate fields, symlink/FIFO
sidecar substitution, populated/missing placeholders, source hash mismatch,
changed destination tree, a different otherwise-valid superproject revision,
final sidecar-byte mismatch, helper-derived renamed destinations, bare-script
exception compatibility, and absence of regeneration/process/attempt paths.

## I. Attempt state

```text
FIRST_PASS_PLANNED_GOVERNED_IDENTITIES = 14
FIRST_PASS_ATTEMPTS_CONSUMED_BEFORE = 0
FIRST_PASS_ATTEMPTS_CONSUMED_AFTER = 0
```

All 75 historical external `attempt.json` paths remain unchanged; none is
Block-03. No Block-03 production namespace or attempt record was created.

## J. Scientific state

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

Admissions are the frozen initial 40 plus 10 + 10 + 7. The normative exclusion
union reproduces 34 and the 9/23/2 split. Historical materialization ledgers and
the accepted Batch-01 completion reproduce 26 ready cases; PROTOCOL requires
24 final slots plus four separate pilot slots. Zero oracle outcomes is the
recorded evidence state; no subject oracle is executed to verify it. Current
controlling-input validation passes and all scientific ledgers retain hashes.

## K. Firewall attestation

```text
SUBMODULE_INIT_EXECUTED = NO
SUBMODULE_UPDATE_EXECUTED = NO
SUBMODULE_CLONE_EXECUTED = NO
SUBMODULE_FETCH_EXECUTED = NO
SUBMODULE_NETWORK_ACQUISITION_EXECUTED = NO
PRODUCTION_SOURCE_EXPORT_CREATED = NO
REAL_MATERIALIZER_ENGINE_INVOKED = NO
DOCKER_BUILD_EXECUTED = NO
DOCKER_CONTAINER_EXECUTED = NO
SUBJECT_DEPENDENCY_INSTALLATION_EXECUTED = NO
SUBJECT_SETUP_EXECUTED = NO
BUGGY_ORACLE_EXECUTED = NO
FIXED_ORACLE_EXECUTED = NO
FIRST_PASS_ATTEMPT_CONSUMED = NO
ELIGIBILITY_CLASSIFICATION_PERFORMED = NO
ACCEPTED_EXCLUSION_ADJUDICATION_PERFORMED = NO
GIT_STAGE_PERFORMED = NO
GIT_COMMIT_PERFORMED = NO
GIT_PUSH_PERFORMED = NO
```

## L. Lifecycle state, risks and unknowns

```text
HUMAN_PI_GITLINK_PROTOCOL_DECISION_V1 = ADOPTED
BLOCK_03_GITLINK_SOURCE_EXPORT_COMPATIBILITY_BRIDGE_V1 = HUMAN_PI_ACCEPTED
BLOCK_03_GITLINK_SOURCE_EXPORT_COMPATIBILITY_BRIDGE_V1 = FROZEN
BLOCK_03_GITLINK_SOURCE_EXPORT_COMPATIBILITY_BRIDGE_V1 = PERSISTED
BLOCK_03_GITLINK_SOURCE_EXPORT_COMPATIBILITY_BRIDGE_V1 = COMMITTED
BLOCK_03_GITLINK_SOURCE_EXPORT_COMPATIBILITY_BRIDGE_V1 = REMOTE_PUBLISHED
BLOCK_03_GITLINK_SIDECAR_TRANSPORT_COMPATIBILITY_BRIDGE_V1 = CANDIDATE_ONLY
HUMAN_PI_ACCEPTED = NO
FROZEN = NO
PERSISTED = NO
COMMITTED = NO
REMOTE_PUBLISHED = NO
GITLINK_SOURCE_PACKAGE_TRANSPORT_REPRESENTABLE
```

The prior accepted source-export bridge's enclosing commit is the verified
local/live remote HEAD. This candidate provides local transport representability
and fail-closed evidence only. Real Docker staging/build/run, actual engine
execution, runtime buildability, environment readiness and scientific validation
remain untested and unauthorized. The full repository test suite was not run.
The required worktree is now intentionally dirty with exactly this candidate's
three paths; the index remains empty, HEAD remains unchanged, and the production
clean-committed-materializer gate continues to reject this unpublished candidate.

## M. Next authority gate and recommended next action

```text
NEXT_GATE = HUMAN_PI_REVIEW_OF_BLOCK_03_GITLINK_SIDECAR_TRANSPORT_COMPATIBILITY_BRIDGE_V1
FIRST_PASS_ATTEMPTS_CONSUMED = 0
MATERIALIZATION_EXECUTION_REMAINS_BLOCKED
```

Recommended next action: Human-PI review of the three-path candidate and its
bounded evidence. Acceptance, lifecycle persistence, freeze, staging, commit,
publication and materialization each remain outside this transaction's authority.

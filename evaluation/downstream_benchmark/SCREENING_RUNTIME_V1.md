# BugsInPy screening runtime v1

- Status: `SCREENING_RUNTIME_V1_FROZEN_WITH_ENVIRONMENT_BLOCKERS`
- Authority: Human PI runtime transaction dated 2026-09-22
- Scope: frozen initial 40 and both declared revisions, before environment materialization or oracle outcomes
- Controlling artifacts: `PROTOCOL.md`, `RUN_SPEC_V1.md`, `SCREENING_SPEC_V1.md`, `ORACLE_REPRESENTATION_V1.md`, and `screening_execution_plan.csv`
- Zero-outcome state: no environment built, subject setup run, subject dependency installed, oracle run, or eligibility result recorded

## A. Authority and current gate

This supplement freezes timeout and environment-construction rules. It does not
amend case membership, candidate order, oracle membership/order, or eligibility
semantics. The mechanical `execute` gate remains closed. A later Human PI
transaction must separately authorize environment materialization, then a still
later explicit transaction must authorize any real 3/3 oracle execution. The
presence of an execution token is never sufficient human authorization.
The older plan ledger still says `PRE_EXECUTION_TIMEOUT_GATE_REQUIRED`; that
mechanical flag remains closed until the case plans are reissued with the
runtime identity and Docker executor in a later transaction. Its retained name
does not mean the timeout values in this document are undecided.

## B. Timeout semantics

`SUBCOMMAND_TIMEOUT_SECONDS = 300` and `TRIAL_TIMEOUT_SECONDS = 900` apply
uniformly to all 40 cases, BUGGY and FIXED. Each subcommand has a hard 300-second
wall-clock limit. Each complete ordered-command trial has one aggregate
900-second wall-clock limit; that clock never resets between subcommands. Both
clocks include process startup and teardown. Environment preparation and fresh
workspace construction occur before the trial clock. Runner-controlled
post-trial evidence hashing occurs after it stops. No automatic retry is allowed.

A subcommand timeout has `infrastructure_subreason=ORACLE_SUBCOMMAND_TIMEOUT`.
An aggregate deadline has `infrastructure_subreason=ORACLE_TRIAL_TIMEOUT`. Both
are `OTHER_INFRASTRUCTURE_FAILURE` at the infrastructure reason layer and
`INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY` at the screening classification layer.
A timed-out trial cannot be `TRIAL_FAIL`, contribute BUGGY FAIL, or produce an
eligibility result. Later commands in that trial do not execute. A timeout
requires termination and reaping of its process group or complete container,
including child processes; abandoning only the parent is insufficient.

## C. Production backend and platform

The frozen production screening backend is Docker/OCI at `linux/amd64`. The host
is Apple Silicon macOS; the subjects declare historical Python 3.6–3.8 patch
versions and may depend on x86-64 Linux binary packages. This is an experiment
runtime identity decision. Native macOS is not a fallback. A case remains
unresolved if Docker cannot provide its exact declared patch version and
complete runtime identity. The present executor's legacy native execution path
is deliberately blocked pending a separately governed Docker implementation.

Docker CLI 29.4.1 and Buildx v0.33.0-desktop.1 were observed. The daemon socket
was absent, so server/engine version, engine architecture, BuildKit daemon, local
pullability, executable Python identity, and actual container operation are
unverified: `DOCKER_DAEMON_REQUIRED`.

## D. Base runtime identity

`runtime_base_images.csv` records one official `docker.io/library/python` tag
and its immutable `linux/amd64` manifest digest for each of the seven declared
patch versions. The registry image config declares the matching
`PYTHON_VERSION`; this is metadata evidence, not an executable probe. No image
was pulled or run. Future acceptance requires pulling by digest, verifying
`linux/amd64`, observing `python --version` in a base image without subject
mounts, and hashing the actual Python executable. A mutable tag alone cannot
identify a production base. Any mismatch blocks the affected version; no
nearby patch substitute is permitted.

## E. Build and execution network

Environment/image construction may use network only under separate authority
and with its exact repositories, immutable artifacts, and hashes recorded.
Real oracle execution must have external network disabled, mechanically
verified with Docker `--network=none` or equivalent before every trial. A
networked build never implies networked execution. No fetched mutable shell
script may run unless its bytes are preserved and content-addressed.

## F. Pinned BugsInPy compile relationship

The pinned `framework/bin/bugsinpy-compile` was read as data. It removes and
creates a virtual environment, installs requirements, executes lines from
`bugsinpy_setup.sh`, installs requirements again, manipulates `PYTHONPATH` and
shell state including `~/.bashrc`, and writes a compile flag. It must not be
used as an opaque production builder. A controlled future builder may reproduce
needed semantics only as explicit, recorded, content-addressed steps; it must
not execute the original script in this transaction.

## G. Static input audit and setup classification

`environment_requirements.csv` preserves the frozen 40-row order and records
raw-byte SHA-256 of each present requirements and setup input, decoded line
counts, Python path metadata, line classifications, environment mode, and
blockers. The audit reads `bug.info` and `project.info` as inert text. Twelve
requirements files are UTF-16 with BOM; their raw hash is authoritative, and
any later UTF-8 conversion requires a frozen recipe and output hash.

Each substantive setup line is classified as exactly one of
`DEPENDENCY_INSTALL`, `PROJECT_INSTALL_OR_BUILD`,
`ENVIRONMENT_CONFIGURATION`, `FILESYSTEM_PREPARATION`, `TEST_INVOCATION`,
`NETWORK_OR_EXTERNAL_SERVICE`, or `UNSUPPORTED_OR_AMBIGUOUS`. Comments and
blank lines are excluded from substantive counts. A test invocation adds
`SETUP_CONTAINS_TEST_INVOCATION` and cannot be admitted to environment building
without adjudication. Unsupported semantics remain unresolved. No setup line
was executed. None of the frozen 40 setup files contains a classified test
invocation; installing a test package is a dependency install, not a test run.

## H. Construction semantics and identity inputs

Every case requires a deterministic recipe identified by SHA-256. It must bind
the immutable base manifest digest; exact observed Python and executable hash;
raw requirements/setup hashes and any normalized derived input hash; relevant
packaging metadata hashes for the revision being built; explicit system-package
manifest; installed-distribution manifest; source revision; and final image
digest/rootfs identity. `UNBUILT` is required for every not-yet-materialized
field. `ABSENT` may be used only for a verified absent input. No materialized
environment identity is claimed by either CSV in this transaction.

The builder must record every package install, source build, filesystem edit,
environment variable, dependency resolver input/output, network source, and
resulting artifact. No subject setup or dependency installation is authorized
by this specification alone.

## I. Source dependence

`environment_mode` is determined per case. `SOURCE_INDEPENDENT_ENVIRONMENT`
means the audited dependency image has no identified source build or self
package pin; it does not assert runtime feasibility. A `setup.py` build/install,
editable local install, or self VCS requirement is
`REVISION_SPECIFIC_BUILD_REQUIRED`. Such a future BUGGY and FIXED image must
use the same frozen recipe, be recorded separately, and differ only by the
frozen source revision. Pinned self VCS references require an explicit rule
before building the FIXED revision; a reference differing even from the BUGGY
revision is `UNRESOLVED`. A self package pin with no source build is also
`UNRESOLVED` until import/source precedence is adjudicated. No one mode is
forced across all projects.

The static audit found 9 source-independent, 19 revision-specific, and 12
unresolved cases. These are construction classifications, not eligibility or
successful-build results.

## J. Read-only execution and freshness

The future environment image/rootfs must be immutable and read-only at trial
execution. Writable state is restricted to a fresh subject workspace, trial
specific `HOME`, `TMPDIR`, cache paths, and runner evidence path. Each of the
six trials gets a fresh source workspace, container/process, and ephemeral
HOME/TMP/cache. No mutable state is reused. Screening images and workspaces
must never be given to a repair agent; fixed source and screening evidence
must never be exposed to one.

## K. Versioned environment identity schema

`SCREENING_ENVIRONMENT_IDENTITY_V1` requires the following keys for each
revision. Values are exact observed values when materialized, otherwise
`UNBUILT`:

```text
canonical_case_id
revision_label
revision_sha
runtime_backend
runtime_platform
base_image_reference
base_image_digest
python_declared_version
python_observed_version
python_executable_sha256
build_recipe_sha256
requirements_sha256
setup_sha256
packaging_metadata_sha256
system_dependency_manifest_sha256
installed_distribution_manifest_sha256
environment_image_digest
environment_tree_or_rootfs_identity
network_build_policy
network_execution_policy
execution_plan_sha256
screening_runtime_spec_sha256
```

For absent requirements/setup, record verified `ABSENT`; for all other
unmaterialized identities, use `UNBUILT`. A future builder must bind this
document's final SHA-256 and the committed execution-plan row hash, and reject
empty, fabricated, mutable-tag-only, or mismatched fields.

## L. Infrastructure classification

The timeout subreasons in section B remain under existing
`OTHER_INFRASTRUCTURE_FAILURE / INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY`.
Infrastructure timeouts do not add an eligibility outcome and do not permit
automatic retries. A later rerun, if ever authorized, needs a separately
recorded reason and a new immutable execution ID.

## M. Zero-oracle boundary

This transaction has no subject dependency installation, setup execution,
subject source execution, oracle command, 3/3 trial, eligibility evidence,
pilot, repair run, or ErrPilot effectiveness result. `cases_manifest.csv` and
`exclusions.csv` remain header-only. No fix patch/diff/history was inspected.

## N. Future materialization authority and blockers

The image metadata confirms seven candidate OCI identities, but the daemon is
unavailable and no Python executable probe or environment build occurred.
`DOCKER_DAEMON_REQUIRED` and `BASE_PYTHON_EXECUTABLE_PROBE_REQUIRED` block every
case. The row ledger additionally freezes UTF-16 conversion, self VCS revision,
and self package source-selection blockers where observed. A separate Human PI
transaction must authorize and specify their resolution before any environment
materialization. A separate explicit authority is still required before real
oracle execution, even after all environment blockers are resolved.

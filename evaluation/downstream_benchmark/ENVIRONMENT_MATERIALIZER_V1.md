# BugsInPy environment materializer v1

- Status candidate: `ENVIRONMENT_MATERIALIZER_V1_SYNTHETICALLY_VALIDATED_AND_FROZEN` only after the listed checks pass and the Human PI publishes the one reviewed commit.
- Scope: deterministic materializer mechanics for the frozen initial 40, validated with synthetic Docker inputs only.
- Controlling inputs: `PROTOCOL.md`, `RUN_SPEC_V1.md`, `ENVIRONMENT_BUILD_SPEC_V1.md`, `environment_build_recipes.csv`, `requirements_normalization.csv`, `self_reference_ledger.csv`, `runtime_base_images.csv`, and `screening_execution_plan.csv`.

This document preserves the synthetic v1 validation record. The global
production gate in v1 is superseded by the production-enabled
`ENVIRONMENT_MATERIALIZER_V1_1` implementation; see `MATERIALIZATION_GATE_V1.md`.
Every real batch still requires separate Human-PI case authority.

## A. Authority and zero-real-build boundary

`screening/materializer.py` has `validate`, `plan`, and `materialize` modes. Bare invocation prints help and exits 2. Import, `validate`, and `plan` do not call Docker. `materialize` requires the exact `BUGSINPY_ENVIRONMENT_MATERIALIZATION_AUTHORIZED_V1` token and a second code gate, `REAL_MATERIALIZATION_ENABLED`, which is **false in v1**. Thus neither the token printed here nor a fabricated request can build one of the real initial 40 in this transaction. A later Human PI transaction must review the production request and open that gate explicitly. No real source, dependency, setup, build, test, oracle, repair, ErrPilot, or model path is exercised here.

## B. Production modes

`SOURCE_INDEPENDENT_ENVIRONMENT` copies the verified derived dependency-only input into the image and does not copy subject source. The source is supplied only to a later fresh screening workspace. `REVISION_SPECIFIC_BUILD_REQUIRED` requires separately identified BUGGY and FIXED source snapshots and emits separate images and identities using the same recipe and ordered action semantics. Each snapshot is a plain directory with a canonical file manifest and an explicit SHA-256. The real request also binds each snapshot to the frozen Git revision SHA. The materializer rejects `.git`, `bug_patch.txt`, BugsInPy metadata, screening evidence, symlinks, and special files in a snapshot. The builder does not access a normal Git working tree or its recoverable history.

## C. Immutable input verification

`validate` checks the controlling hashes, the 40-case order against the selected candidate list and execution plan, the 26/14 mode split, each canonical recipe SHA-256, `BUILD_RECIPE_READY`, and `UNBUILT`. Before any build, the engine compares the supplied raw requirements, normalized requirements, **derived dependency-only** requirements, setup bytes, self-reference ledger, and ordered setup-action ledger with recipe hashes. It never renormalizes requirements or installs raw requirements. A real request must match a frozen case and recipe hash, and its self-reference entries must equal the frozen ledger. Any drift is `BLOCKED_INPUT_IDENTITY`; no best-effort reconstruction occurs.

## D. Structured setup execution

The builder never executes `setup.sh`. It accepts only parsed argv for supported `pip install`, `python setup.py`, and bounded `touch` actions. It rejects shell control and metacharacters, VCS install arguments, unbound `-r` input, and unknown commands as `BLOCKED_UNSUPPORTED_ACTION`. `pip install -r requirements.txt` is rebound to the frozen derived dependency-only file. Actions appear as Dockerfile exec-form `RUN` instructions in frozen order. Source-consuming actions require a revision snapshot. No oracle or test command is supported.

## E. Docker semantics

Every build uses `--platform=linux/amd64`. The Dockerfile starts from the frozen `docker.io/library/python@sha256:...` reference, never a mutable tag. A pre-build image inspection checks the observed image digest and Linux/amd64 platform; a no-network, read-only container probe checks exact Python patch version, x86-64 machine, and Python executable SHA-256. The final image is independently inspected and probed. The Dockerfile bytes and SHA-256 and a canonical build-context manifest are preserved. No timestamp enters the recipe or Dockerfile. Synthetic builds use the already-pulled Python 3.8.3 frozen digest and `--network=none`; no external package is downloaded.

## F. Network policy

The recipe retains its frozen future build policy, `DECLARED_DEPENDENCY_SOURCES_ONLY_SEPARATE_AUTHORITY_REQUIRED`. A separately authorized real build can record `NETWORK_ALLOWED_RECORDED`; synthetic builds use `NONE`. The exact Docker build command and raw log are evidence. Execution policy is always `NONE`, represented by `--network=none` in identity probes and future-style synthetic runs. Build-network permission never changes execution-network policy.

## G. Evidence model

Each attempt directory contains `attempt.json`; each revision directory preserves its Dockerfile, context and manifest, source snapshot manifest if applicable, raw `build.log`, image inspection JSON, installed-distribution JSON, system-package text, and canonical `environment_identity.json` on success. The attempt records case ID, revision/source snapshot identity, frozen source revision when applicable, recipe SHA-256, platform, base digest, materializer version, source-file SHA-256 and Git HEAD, build timestamps, exact Docker argv, Dockerfile/context/log hashes, exit code, observed final image ID, any observed registry manifest digest, RootFS layers, Python probe, and manifest/identity hashes. Docker image `Id` is an observed immutable **configuration digest** and fills `environment_image_digest`; it is not mislabelled as a registry manifest digest. When no registry digest is available, the separate registry field says `UNAVAILABLE_LOCAL_ONLY`.

The attempt directory is screening-only evidence. Its copied source and fixed revision must never be handed to a repair agent. Keep it outside any repair workspace. Synthetic test evidence may be under a local temporary directory; future real evidence needs an explicitly governed persistent destination.

## H. Failure taxonomy

`MATERIALIZED` requires successful build and observed final identity. `BUILD_FAILED` preserves the failing log and represents infrastructure, never oracle failure, case ineligibility, or repair failure. `BLOCKED_INPUT_IDENTITY`, `BLOCKED_RUNTIME_IDENTITY`, and `BLOCKED_UNSUPPORTED_ACTION` stop before a build when detected. `INTERRUPTED` never becomes `MATERIALIZED`. A build is attempted once: no silent retry, source mutation, recipe mutation, or dependency version change follows failure. Any later retry needs a new attempt ID and recorded reason under separate authority.

## I. Cache and tags

Builds currently use `--no-cache` to make synthetic observations easier to inspect. Cache may be enabled later only with recipe identity and final re-observation intact. Mutable local tags are convenience aliases used to locate the just-built image; the identity records observed image ID and RootFS layers, not the tag. A repeated recipe has the same canonical recipe hash even if independent Docker builds yield different image bytes or metadata. This establishes recipe reproducibility, not byte-identical image reproducibility.

## J. Environment identity

The builder fills the existing `SCREENING_ENVIRONMENT_IDENTITY_V1` field order. It takes Python, image ID, RootFS layers, installed distribution manifest, and system-package manifest from Docker observations. It binds the frozen recipe and execution-plan identities and hashes canonical UTF-8 JSON with sorted keys, compact separators, and one LF. Missing observations block success. The frozen 40 recipe rows remain `UNBUILT`; the materializer never writes to them or to screening outcome ledgers.

## K. Screening and repair separation

These images are screening-only. Future execution must use isolated, fresh subject workspaces, disabled network, read-only image rootfs, and only ephemeral writable home/tmp/workspace paths. The synthetic identity command verifies `--network=none`, `--read-only`, and tmp/home mounts. Neither fixed snapshot, official patch, screening evidence, nor image/context containing fixed source may be exposed to a repair agent.

## L. Synthetic validation

Fixtures under `fixtures/environment_materializer/` are not benchmark cases. A is source independent with inert local dependency input and an allowed local file operation. B has distinct A/B snapshot manifests and separate BUGGY/FIXED images. C changes the recipe hash; D simulates a base Python mismatch; E contains an unsupported shell action; F makes a deterministic `--no-index` local package install fail; G simulates interruption. Tests cover the 20 requested authority, input, order, source, Docker, evidence, and outcome properties. No real initial-40 case ID is accepted by the synthetic entrypoint.

## M. Future real-materialization gate

A later Human PI transaction must authorize opening `REAL_MATERIALIZATION_ENABLED`, approve a real request/output location, verify a clean materializer commit and source exports against frozen revisions without repair history, authorize any networked dependency sources and artifact recording, and run a separate real identity gate. The screening oracle and repair gates remain separate and closed. A v1 synthetic pass does not establish that any real subject environment can build or run.

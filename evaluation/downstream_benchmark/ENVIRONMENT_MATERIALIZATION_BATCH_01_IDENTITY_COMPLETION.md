# Batch-01 keras::28 identity completion

Status: `BATCH_01_KERAS28_IDENTITY_COMPLETED`. Classification:
`POST_BUILD_IDENTITY_COMPLETION`. The original Batch-01 ledger and report
remain byte-identical, with keras::28 recorded as `BLOCKED_RUNTIME_IDENTITY`.

The original attempt `batch01_10_keras_28` had one build attempt, exiting 0.
Its installed-distribution probe then failed because Python 3.7.3 lacks
standard-library `importlib.metadata`. The original image ID was
`sha256:f9b214bdeeb7fa29722bdd95226d1aa6600d89f73ca8e6b5627d989f2d7546d3`.
The current local image matched that ID and the preserved RootFS layer list
before any new container probe. Its RootFS layer-list identity is
`566d0031d593efef93e1d19447fd6af841377e855c0994fe4be5bdb3d249869c`.

The V2 probe selected `PIP_LIST_JSON` from the observed Python 3.7.3 version.
It ran `python -m pip list --format=json` against that exact image with no
network, a read-only root filesystem, and ephemeral `/tmp`. The raw stdout and
stderr are preserved separately under
`evidence/batch_01_keras28_identity_completion/`, alongside the canonical
distribution manifest, raw system-package observation, image inspection,
environment identity, and a hash-bearing probe summary. The observed hashes
are:

| Evidence | SHA-256 |
| --- | --- |
| Installed-distribution canonical manifest | `610ea84a2652e16c1a6c373457b7092169c7a3fe3eb196d85fb018d523da4ba5` |
| System-package manifest | `323e5ef08590a7a99dab48cac5046184653aff8f79944bdf6bc4484d727bf00c` |
| Completed `SCREENING_ENVIRONMENT_IDENTITY_V1` | `36070fd6869dac8ef60046ad32ebc1500a4fa190ca0f3f3c83cde2922683a8cf` |

The system-package hash matches the original post-build diagnostic. The
supplemental CSV records `original_status = BLOCKED_RUNTIME_IDENTITY`,
`identity_completion_status = COMPLETED`, and
`effective_environment_status = MATERIALIZED`. No second keras::28 build,
dependency install, setup action, subject import/test, oracle, 3/3 screening,
eligibility decision, repair, ErrPilot call, or model/API call occurred.

Mechanics were also observed on the already-local frozen Python 3.6.9,
3.7.3, and 3.8.3 base images. All three returned exit 0 under a read-only,
network-disabled probe. Backend selection was `PIP_LIST_JSON`,
`PIP_LIST_JSON`, and `STDLIB_IMPORTLIB_METADATA`, respectively. The base-image
manifest hashes were `8379b233098f7ac5efcc4b81b7bf27b6da33ea22488d99ba2a7c4dea5d2b40e2`,
`6d177a0dd082967ffb4a837425656efc465a2324a9e86366b7b8ac2961588939`,
and `a3b5f5e468ec611c8c4875d9d4fcfa3d394c03d0496788f8f1efb2573fb9b7bd`.
These are non-subject probe-mechanics observations, not subject build results.

Repository validation for this amendment: the benchmark-local suite passed
with 95 tests and 42 subtests; the opt-in synthetic Docker build test was
skipped to maintain the zero-installation boundary. The full ErrPilot suite
passed with 89 tests. `ruff check .` and `git diff --check` passed. The frozen
recipes, candidate order, controlling document hashes, original Batch-01
ledger/report, and header-only outcome ledgers remained unchanged. No Batch-02
attempt exists.

# Expansion Block 02 build-failure adjudication V1

Status: `EXPANSION_BLOCK_02_BUILD_FAILURE_ADJUDICATION_V1_FROZEN`.

## Human-PI authority and controlling identity

The Human PI formally accepts all five first-pass build-failed Block 02 cases
as `ACCEPTED_EXCLUSION`, `NON_RETRY`, with final reason
`DEPENDENCY_SETUP_FAILURE`. The explicit five-case instruction controls this
bounded normative transaction. No systemic amendment or retry is accepted.

Entry repository: `/Users/wuyangchenxi/errpilot`, clean `main`, local HEAD and
live `origin/main` `b27f635e8bacbf9dc99b5523a58380e1780e4fe8`, ahead/behind
`0/0`. No `.airos/current_state.md` or repository Research Contract is present.
The committed controlling states are
`EXPANSION_BLOCK_02_MATERIALIZATION_FIRST_PASS_COMPLETE`,
`EXPANSION_BLOCK_02_POST_PRODUCTION_TEST_RECONCILIATION_V1_FROZEN`, and
`PRE_ELIGIBILITY_EXCLUSIONS_LEDGER_STATE_V3_FROZEN`; the entry V3 validator passes
(`PRE_ELIGIBILITY_EXCLUSIONS_LEDGER_STATE_V3_VALIDATED`).

Block 02 identity:
`6d5a8a713ddcb18ea70b8268c72e7aa2d5e1eb44bace81f1bd485c88907c0b95`.
The first-pass materializer/controller commit is
`e148cd8d77e1847d84ab7e9ebd1e9bf5639c67af`, materializer version
`ENVIRONMENT_MATERIALIZER_V1_5`. The committed materialization report and CSV,
with their preserved production attempts, control the observed build outcomes.

## First-pass accounting and exact final dispositions

The first pass contains 12 governed identities: four `MATERIALIZED`, eight
`BUILD_FAILED`, and zero infrastructure/controller blockers. Each of the twelve
durable controller entries is `CLOSED` with its governed attempt consumed.
The three environment-ready Block 02 cases are `fastapi::12`, `httpie::5`, and
`PySnooper::1`. None is appended to `exclusions.csv`.

| Frozen expansion order | Case | Failed identities | Failure family | Final exclusion reason |
| ---: | --- | --- | --- | --- |
| 1 | `tornado::13` | SOURCE_INDEPENDENT | `FROZEN_SETUP_ACTION_FAILURE` | `DEPENDENCY_SETUP_FAILURE` |
| 2 | `tornado::4` | SOURCE_INDEPENDENT | `FROZEN_SETUP_ACTION_FAILURE` | `DEPENDENCY_SETUP_FAILURE` |
| 3 | `spacy::6` | BUGGY; FIXED | `DEPENDENCY_RESOLUTION_FAILURE` | `DEPENDENCY_SETUP_FAILURE` |
| 6 | `tqdm::7` | BUGGY; FIXED | `FROZEN_ARTIFACT_UNAVAILABLE` | `DEPENDENCY_SETUP_FAILURE` |
| 8 | `spacy::7` | BUGGY; FIXED | `DEPENDENCY_RESOLUTION_FAILURE` | `DEPENDENCY_SETUP_FAILURE` |

All five have `ACCEPTED_EXCLUSION`, `NON_RETRY`, and stage
`ENVIRONMENT_MATERIALIZATION`. The companion
`expansion_block_02_build_failure_adjudication_v1.csv` has exactly five data rows
in this order; SHA-256:
`d4dbd49fd835ec75cff33df1d74f45c1de9c7bab09684c1db182c400661e10bd`.
Each row binds the committed report and identity ledger to the exact preserved
`attempt.json` and build-log hashes. Revision-specific rows retain separate
BUGGY and FIXED references.

## Failure-family evidence and non-normative precedent

Both Tornado cases failed at the frozen `pip install unittest` setup action:
the logs report no matching distribution for `unittest`. The recipes and
Dockerfiles are source-independent, and their contexts contain no subject
source; no subject source influenced this blocker. Systemic group:
`SETUP_UNITTEST_INSTALL`. Prior `tornado::6` and `tornado::11` exhibit the same
mechanism. Their historical family labels remain unchanged; precedent is
context only and grants no authority for this adjudication or a retry.

Both `tqdm::7` identities failed on `pkg-resources==0.0.0` in the frozen
dependency input, with no matching distribution. The failing dependency step
precedes subject installation/build in both preserved Dockerfiles. Systemic
group: `ARTIFACT_PKG_RESOURCES_0_0_0`. Historical `tqdm::1` and `tqdm::3`
provide matching-mechanism context only, with no current normative authority.

All four spaCy identities failed during frozen dependency installation along
`preshed -> murmurhash-1.0.15 -> isolated build requirement cython>=3.1`.
The resolver found no matching distribution under the frozen
resolver/index/runtime combination. Systemic group:
`PRESHED_MURMURHASH_CYTHON_GE_3_1`. The evidence does not establish exact causal
pip-version incompatibility, universal Python-3.7 incompatibility, an
equivalent alternative index/artifact, or an exact safe Cython replacement.
This is `DEPENDENCY_RESOLUTION_FAILURE`, normatively mapped to
`DEPENDENCY_SETUP_FAILURE`; it is not classified as universal runtime
incompatibility or `UNSUPPORTED_ENVIRONMENT`.

## NON_RETRY and rejected systemic amendment

`NON_RETRY` closes all five cases under the frozen first-pass benchmark policy
with recovered-case count `r = 0`. No second production build or post-outcome
rescue is authorized. This decision does not assert that another environment
could never build these cases, or infer unobserved later build stages.

For this benchmark state, the Human PI rejects all currently hypothetical
proposals to omit `pip install unittest`, delete `pkg-resources==0.0.0`, alter
direct or transitive Cython constraints, change dependency versions, change
Python runtime, change pip/build toolchain, or change package index/provenance.
None closes all eight required systemic-amendment criteria: mechanical trigger;
exact transformation; general applicability; evidence-grounded transformation;
outcome-independent justification; prospective freezeability; characterized
semantic effect; and non-case-specific application. No systemic recovery rule
is adopted, and no frozen input is amended.

## First-pass evidence preservation

The original scientific evidence, prior adjudications, preparation inputs,
selection order/cursor, production controller/materializer, post-production
reconciliation record, and external production roots remain unchanged.
The separate read-only preservation audit compares entry and final hashes and
modes; ordinary tests do not depend on the external V2 evidence root.

| Preserved evidence | SHA-256 |
| --- | --- |
| `EXPANSION_BLOCK_02_ENVIRONMENT_MATERIALIZATION.md` | `cad9e6189cb87ef45b2db68685ee4a419f80f20eca1a020250d17a23721487ff` |
| `expansion_block_02_environment_materialization.csv` | `06c91e7303749d4e2e5d676aee8455d2371078cf80a8e70521e8f1dbf52ea443` |
| Historical Block 02 root, compact sorted-key 10-file hash map | `1cea074fbac40c465bff0b3a76f1fbfcca8b79da3e0a14d38af47ad44a6a50bb` |
| V2 production root, compact sorted-key 10,197-file hash map | `6a98957c1c7c00d7e0ca19d42a11a400d193a15ac0969b9b41dd1e459bf4430d` |
| V2 `identity_ledger.json` | `c7e64e89c8b331c6499b97d8cfe7171581c113132e0c89005720769dd3db76fa` |

The external roots are
`/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_02`
and
`/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_02_v2`.
Their files and directory identities remain preserved; the historical attempts
directory remains empty. Hash preservation does not imply OS-level write protection.

## Capacity consequence and downstream gates

Initial-40 readiness is 19; Block 01 adds four; Block 02 adds three. Accepted
`NON_RETRY` exclusions recover zero cases, so environment readiness remains
`19 + 4 + 3 + r = 26`, below the required 28 slots (24 final plus four permanently
separate pilots). `BLOCK_03_MATHEMATICALLY_REQUIRED = YES` is now normative
with respect to the closed current recovery policy. This transaction constructs
no Block 03 artifact, traverses no future candidate, and advances no cursor.
Oracle attrition may require still further expansion.

`MATERIALIZED != ELIGIBLE`; environment-ready != eligible.
`cases_manifest.csv` remains header-only, and no case is yet classified
`ELIGIBLE`. Environment/preparation exclusions are not oracle or eligibility
outcomes. No Docker subject build, materialization, retry, dependency/setup
action, subject test, oracle, eligibility, Block-03 traversal, repair, ErrPilot,
or downstream model/API execution occurs in this transaction. Only ordinary
repository tests with existing synthetic fixtures/mocks are permitted.

`PRE_ELIGIBILITY_EXCLUSIONS_LEDGER_STATE_V4.md` records the resulting ledger.
Future ledger transitions, Block 03 construction, acquisition, preparation,
materialization, oracle/eligibility screening, and repair each require separate
Human-PI authority. This freeze grants none of those actions. Publication
requires interactive approval of exactly `git push origin main:main`; the
transaction instruction itself is not push approval. Any automatic existing CI
is only `CI_TRIGGERED_REPOSITORY_VERIFICATION`.

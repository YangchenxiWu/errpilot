# Environment materialization Batch 04

Status: `ENVIRONMENT_MATERIALIZATION_BATCH_04_COMPLETE` and, descriptively, `INITIAL_40_MATERIALIZATION_FIRST_PASS_COMPLETE`. **MATERIALIZED != ELIGIBLE.** No screening, oracle, eligibility, repair, or effectiveness result is asserted.

## A. Authority and entry state

The Human PI authorized real production environment materialization for exactly frozen initial-selection-order cases 31–40: `fastapi::13`, `ansible::4`, `black::16`, `spacy::1`, `httpie::3`, `matplotlib::29`, `tqdm::3`, `fastapi::11`, `ansible::16`, and `httpie::4`. The exact authority token was `BUGSINPY_ENVIRONMENT_MATERIALIZATION_AUTHORIZED_V1`. Networked Docker construction, frozen dependency/setup actions, revision-specific source builds, Source Snapshot Symlink V2, and Distribution Probe V2 were within this authority. Prior-batch retries, subject tests, oracles, eligibility, ErrPilot, repair, and model/API invocation were outside it.

Before any build, the repository was clean on `main` at `ead9f5a87286f4c1c9a388a76ab2620c351f5e6c`; live `origin/main` matched and ahead/behind was `0/0`. The required `PROTOCOL.md` and `RUN_SPEC_V1.md` SHA-256 values were `34e014a07821dc9dca52178874eef0b847aee7f048071fb4920864ae5d3bee93` and `29ab6f78739d0eeea1c2a774e62e2d133f173e160c3d247407970a80726f4406`. The frozen recipe ledger SHA-256 was `2addaf1830e61350e46583ec27b1403b43ffb0f8475b48e4bfc7d62b068b663e`. Its validator confirmed all 40 recipes in the candidate/plan order as `BUILD_RECIPE_READY` and `UNBUILT`; the ten Batch-04 frozen requirements, derived dependency inputs, self-reference ledgers, setup bytes, and source revisions passed input checks. No Batch-04 attempt root or ledger existed beforehand.

The production gate was enabled. The committed materializer was `ENVIRONMENT_MATERIALIZER_V1_3` with source SHA-256 `99c74430f5f270f19624afc7285f8541acce08779a41165e8fb58d351271a211`. Docker was operational. All five required immutable Python base images were locally present as `linux/amd64`, and network-disabled read-only probes matched their frozen Python versions, machine, and executable hashes.

## B–G. Ledger-derived identities and outcomes

The sole identity-count authority, `environment_build_recipes.csv`, assigns five Batch-04 cases to `SOURCE_INDEPENDENT_ENVIRONMENT` and five to `REVISION_SPECIFIC_BUILD_REQUIRED`. Thus Batch 04 required **15 identities**: five source-independent images and BUGGY/FIXED images for each revision-specific case. Every identity received exactly one Docker build command and one independent attempt record.

| Order | Case | Environment mode | Identity outcome and frozen-build observation |
| ---: | --- | --- | --- |
| 31 | `fastapi::13` | Source independent | `MATERIALIZED`. |
| 32 | `ansible::4` | Revision specific | BUGGY and FIXED: `BUILD_FAILED`; frozen `ansible-base==2.10.0.dev0` had no matching distribution. |
| 33 | `black::16` | Revision specific | BUGGY and FIXED: `MATERIALIZED`. |
| 34 | `spacy::1` | Revision specific | BUGGY and FIXED: `BUILD_FAILED`; a frozen dependency's build isolation required `cython>=3.1`, with no matching distribution in this Python 3.7 build. |
| 35 | `httpie::3` | Source independent | `MATERIALIZED`. |
| 36 | `matplotlib::29` | Source independent | `MATERIALIZED`. |
| 37 | `tqdm::3` | Revision specific | BUGGY and FIXED: `BUILD_FAILED`; frozen `pkg-resources==0.0.0` had no matching distribution. |
| 38 | `fastapi::11` | Source independent | `MATERIALIZED`. |
| 39 | `ansible::16` | Revision specific | BUGGY and FIXED: `BUILD_FAILED`; frozen `ansible-base==2.10.0.dev0` had no matching distribution. |
| 40 | `httpie::4` | Source independent | `MATERIALIZED`. |

Totals: **7 `MATERIALIZED`**, **8 `BUILD_FAILED`**, **0 runtime-identity blockers**, **0 input-identity blockers**, and **0 unsafe-symlink blockers**. Each `MATERIALIZED` identity passed the full observed environment identity gate; Docker exit code zero alone was insufficient. Failed builds remain build evidence, not case exclusions or eligibility decisions. The 15-row ledger is `environment_materialization_batch_04.csv` (SHA-256 `250ae3398ab9a59dacd42f24804619c4dc2eace92b82baf2d2c8cda5b6d8792d`).

## H–K. Source, distribution probe, and evidence audit

Ten history-free revision snapshots were exported from exact frozen Git blobs. `SOURCE_SNAPSHOT_MANIFEST_V2` and `BUILD_CONTEXT_MANIFEST_V2` preserved file modes, safe tracked symlinks, and exact symlink target bytes. The BUGGY/FIXED symlink counts were `ansible::4` 69/69, `black::16` 13/13, `spacy::1` 0/0, `tqdm::3` 0/0, and `ansible::16` 166/166. No link escaped the snapshot root or targeted forbidden metadata. Each revision-specific build context held only its own revision; source-independent contexts held no subject source.

Distribution Probe V2 ran only on the seven successfully built images. Python 3.8 images for `fastapi::13`, both `black::16` revisions, `matplotlib::29`, and `fastapi::11` used `STDLIB_IMPORTLIB_METADATA`. Python 3.7 images for `httpie::3` and `httpie::4` used `PIP_LIST_JSON`. Each final-image probe used a network-disabled, read-only container and no subject import or installation. Failed builds never reached the final-image probe; no backend switch occurred.

Large evidence is outside Git under `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_04`. Its `inputs/` tree has the exact frozen input copies, paired revision snapshots and manifests, and requests. Each of the 15 independent attempt directories has `attempt.json`, the exact Dockerfile and build context, V2 context manifest, raw build log, and hashes. Successful attempts also have image inspection, observed Python and RootFS identities, installed-distribution and system-package manifests, probe stdout/stderr, and canonical `SCREENING_ENVIRONMENT_IDENTITY_V1`. A read-only audit reconciled all 15 ledger-required keys to exactly one attempt, rehashed raw logs and manifests, and verified every successful identity and selected probe backend. Unobservable post-failure image fields are `NA` in the CSV; no values were inferred from requirements.

## L–N. One-attempt boundary and prior-batch preservation

The bounded `BATCH04_IDENTITY_CONTROLLER_V1` invoked the committed materializer's frozen input verification, base verification, V2 snapshot/context, Docker build definition, final-image identity, and Distribution Probe V2 routines independently for each required identity. The controller source is preserved in the external evidence root. There was no retry, dependency/version change, Python or base-image change, architecture change, source/symlink or setup change, or recipe change. Build network policy was `NETWORK_ALLOWED_RECORDED`; identity observation and future execution policy were `NONE`.

The controller invoked zero subject pytest/unittest commands, `run_test.sh`, `bugsinpy-test`, functional tests, oracle commands, 3/3 screening, eligibility classifiers, ErrPilot, repair agents, and model/API calls. No subject package import or project CLI was used as a sanity probe. The historical Batch-01, Batch-01 identity-completion, Batch-02, and Batch-03 repository records remained byte-identical to the entry commit; 34 prior external `attempt.json` files matched a pre-completion hash list. Cases 1–30 were not retried or repaired. Frozen authority, candidate order, derived inputs, and self-reference ledger were unchanged. `cases_manifest.csv` and `exclusions.csv` remained header-only.

## O–P. Initial-40 first-pass summary (read-only)

The four frozen batch ledgers, with the Batch-01 `keras::28` identity-completion supplement applied to its effective status, account for **40 initial candidates and 54 required identities**. At the case level, **19** have every required environment identity materialized; **21** have no complete required environment set because of frozen build failure; **0** are blocked for another reason. At the identity level, **25** are effectively `MATERIALIZED`, **29** are `BUILD_FAILED`, and **0** remain blocked. Revision-specific cases count as environment-ready only when both BUGGY and FIXED identities are materialized. These counts describe materialization only; they do not select replacements, adjudicate failures, or declare eligibility.

## Q–V. Validation, publication, and next boundary

Repository-side validation passed: `python3 -m pytest evaluation/downstream_benchmark/tests` reported **107 passed, 2 skipped**; `python3 -m pytest` reported **89 passed**; `ruff check .` and the staged whitespace/diff check passed. The two skipped benchmark tests are opt-in synthetic Docker fixtures. Repository validation did not run subject tests or oracles.

Only `environment_materialization_batch_04.csv` and this report are authorized repository additions for the single commit `evaluation: record environment materialization batch 04`. Commit, push, live ref parity, clean post-push state, and CI status belong to the final run report. A push requires the stated fresh live `origin/main` check and explicit Human-PI approval for one ordinary fast-forward update.

The first-pass materialization record is ready for a **separate** Human-PI adjudication transaction concerning failed environments and any later screening decision. This transaction does not retry, repair, replace, classify eligibility, run an oracle, or claim ErrPilot effectiveness.

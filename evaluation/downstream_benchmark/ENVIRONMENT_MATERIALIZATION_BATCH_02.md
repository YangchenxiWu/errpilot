# Environment materialization Batch 02

Status: `ENVIRONMENT_MATERIALIZATION_BATCH_02_COMPLETE` for the materialization transaction only. **MATERIALIZED != ELIGIBLE.**

## Authority and entry state

The Human PI authorized real production environment materialization for exactly frozen initial-selection-order cases 11–20: `luigi::31`, `youtube-dl::7`, `scrapy::19`, `scrapy::15`, `keras::15`, `black::17`, `scrapy::14`, `thefuck::9`, `httpie::1`, and `ansible::15`. No other case was attempted. The exact token was `BUGSINPY_ENVIRONMENT_MATERIALIZATION_AUTHORIZED_V1`; the production gate was enabled. The committed materializer was `ENVIRONMENT_MATERIALIZER_V1_3` at `5e2ece0c16eab16af19195f316e6de8f35c901ec` (source SHA-256 `99c74430f5f270f19624afc7285f8541acce08779a41165e8fb58d351271a211`).

Before any build, the repository was clean on `main` at that commit; live `origin/main` matched and ahead/behind was `0/0`. The frozen ledger validator reported 40 ready, `UNBUILT` recipes in the unchanged initial-selection order. `PROTOCOL.md` and `RUN_SPEC_V1.md` matched the required SHA-256 hashes. The authoritative `environment_build_recipes.csv` SHA-256 was `2addaf1830e61350e46583ec27b1403b43ffb0f8475b48e4bfc7d62b068b663e`. No prior Batch-02 build attempt or output ledger existed. Docker was operational and all four required immutable base image digests were locally available as `linux/amd64` images.

## Ledger-derived identities and results

The frozen ten ledger rows contain eight `SOURCE_INDEPENDENT_ENVIRONMENT` cases and two `REVISION_SPECIFIC_BUILD_REQUIRED` cases. This mechanically yields **12 required identities**: eight source-independent images, plus BUGGY and FIXED images for each of `black::17` and `ansible::15`. Every identity received exactly one Docker build command. There was no retry, dependency change, Python change, base-image change, architecture change, source change, setup change, or recipe change.

| Order | Case | Environment mode | Identity outcomes and frozen-build observation |
| ---: | --- | --- | --- |
| 11 | `luigi::31` | Source independent | `BUILD_FAILED`: frozen `mysql-connector-python==8.0.20` had no matching distribution in this build. |
| 12 | `youtube-dl::7` | Source independent | `MATERIALIZED`: complete observed environment identity. |
| 13 | `scrapy::19` | Source independent | `BUILD_FAILED`: frozen `pywin32==227` had no matching Linux distribution. |
| 14 | `scrapy::15` | Source independent | `BUILD_FAILED`: frozen `pywin32==227` had no matching Linux distribution. |
| 15 | `keras::15` | Source independent | `BUILD_FAILED`: frozen `numpy==1.19.0rc2` had no matching distribution. |
| 16 | `black::17` | Revision specific | BUGGY: `MATERIALIZED`; FIXED: `MATERIALIZED`. |
| 17 | `scrapy::14` | Source independent | `BUILD_FAILED`: frozen `pywin32==227` had no matching Linux distribution. |
| 18 | `thefuck::9` | Source independent | `BUILD_FAILED`: frozen pip raised `TomlError` parsing a `cryptography` `pyproject.toml`. |
| 19 | `httpie::1` | Source independent | `MATERIALIZED`: complete observed environment identity. |
| 20 | `ansible::15` | Revision specific | BUGGY: `BUILD_FAILED`; FIXED: `BUILD_FAILED`. Both builds lacked a matching distribution for frozen `ansible-base==2.10.0.dev0`. |

Totals: **4 `MATERIALIZED`**, **8 `BUILD_FAILED`**, **0 runtime-identity blockers**, and **0 input-identity blockers**, out of 12 required identities. Failed builds are retained as infrastructure/build observations, not candidate exclusions or eligibility decisions. Build exit 0 was never sufficient by itself: each `MATERIALIZED` row has a complete observed `SCREENING_ENVIRONMENT_IDENTITY_V1` with image ID, RootFS layers, Python version and executable hash, installed distributions, system packages, and canonical identity hash. The CSV records each identity and its exact evidence path.

## V2 representation and observation

`SOURCE_SNAPSHOT_MANIFEST_V2` and `BUILD_CONTEXT_MANIFEST_V2` were used for the four revision-specific identities. The history-free exports came from exact frozen Git blob bytes; tracked symlinks remained symlinks. The black snapshots contain 12 symlinks per revision, and the ansible snapshots contain 354 per revision. Each source/context manifest, its hash, Dockerfile bytes/hash, and the raw build log/hash passed the evidence audit. Each revision's build context contained that revision's source only. No repair patch, opposite revision, or recoverable Git history was placed in a build context.

Distribution Probe V2 selected its backend from the observed Python version: `youtube-dl::7` (3.7.0) and `httpie::1` (3.7.3) used `PIP_LIST_JSON`; black BUGGY and FIXED (3.8.3) used `STDLIB_IMPORTLIB_METADATA`. All four probes succeeded with `--network=none`, `--read-only`, `--pull=never`, and no subject import or installation. Failed builds did not reach the final-image distribution probe. No opportunistic backend switch occurred.

The frozen case-level materializer stopped after the failed ansible BUGGY build. A separate bounded follow-through controller then built only ansible FIXED once, using the same committed materializer's input verification, V2 snapshot/context, build-definition, base-verification, and Docker command semantics. Its independent attempt ID and raw evidence are recorded in the CSV. The original BUGGY attempt remains unchanged; the FIXED attempt was neither a retry nor a recipe repair.

## Evidence, boundaries, and validation

Large evidence remains outside Git under `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_02`. Its case directories retain canonical `attempt.json`, exact requests and frozen inputs, source snapshot manifests where applicable, Dockerfiles, V2 context manifests and contexts, raw build logs, and successful image/probe/identity evidence. The repository CSV SHA-256 is `fe791fc87892cc706bc0e92bdf915f17fed6e0c112fa3f542b2801ad4dfd9a62`. The read-only evidence audit reconciled the 12 ledger-required `(case, revision)` keys exactly once, verified every build command and raw log hash, and verified all successful identity file hashes and probe backends.

Build network policy was `NETWORK_ALLOWED_RECORDED`; identity observation and future execution policy were `NONE`. The controller invoked zero subject pytest/unittest commands, `run_test.sh`, `bugsinpy-test`, functional tests, oracle commands, 3/3 screening, eligibility classifiers, ErrPilot, repair agents, and model/API calls. No subject CLI/import was used as a sanity test. Batch-01 was not retried; Batch-03 and Batch-04 were untouched. `cases_manifest.csv` and `exclusions.csv` remain header-only. The frozen recipes, candidate order, controlling documents, and Batch-01 historical repository artifacts were not modified.

Repository-side validation passed: `python3 -m pytest evaluation/downstream_benchmark/tests` reported 107 passed and 2 skipped; `python3 -m pytest` reported 89 passed; `ruff check .` and `git diff --cached --check` passed. The skipped benchmark tests are opt-in synthetic Docker fixtures; no subject test or oracle was executed.

This transaction establishes only `ENVIRONMENT_MATERIALIZATION_BATCH_02_COMPLETE`. It does not establish candidate eligibility, a screening/oracle outcome, a repair/pilot result, or ErrPilot effectiveness. Any later retry or advancement to eligibility/oracle execution requires separate Human-PI authority.

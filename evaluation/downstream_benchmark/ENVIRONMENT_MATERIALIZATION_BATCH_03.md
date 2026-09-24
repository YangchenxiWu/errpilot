# Environment materialization Batch 03

Status: `ENVIRONMENT_MATERIALIZATION_BATCH_03_COMPLETE` for this materialization transaction. **MATERIALIZED != ELIGIBLE.** No screening, oracle, eligibility, repair, or effectiveness result is asserted.

## A. Authority and entry state

The Human PI authorized real production environment materialization for exactly frozen initial-selection-order cases 21–30: `tornado::6`, `luigi::4`, `fastapi::2`, `youtube-dl::37`, `youtube-dl::18`, `spacy::4`, `ansible::2`, `sanic::1`, `thefuck::26`, and `thefuck::28`. The exact authority token was `BUGSINPY_ENVIRONMENT_MATERIALIZATION_AUTHORIZED_V1`. The production gate, Distribution Probe V2, and Source Snapshot Symlink V2 were active. No Batch-03 attempt or output ledger existed before this transaction.

Before any build, the repository was clean on `main` at `44cead044bb3806e9785c1bc9587e4e7c70f5126`; live `origin/main` matched and ahead/behind was `0/0`. `PROTOCOL.md` and `RUN_SPEC_V1.md` matched their required SHA-256 hashes `34e014a07821dc9dca52178874eef0b847aee7f048071fb4920864ae5d3bee93` and `29ab6f78739d0eeea1c2a774e62e2d133f173e160c3d247407970a80726f4406`. The authoritative `environment_build_recipes.csv` hash was `2addaf1830e61350e46583ec27b1403b43ffb0f8475b48e4bfc7d62b068b663e`. The frozen ledger validator reported 40 ready, `UNBUILT` recipes in the unchanged initial-selection order. The Batch-03 source inputs and derived dependency bytes matched the frozen recipe hashes. Docker was operational; all four immutable Batch-03 base images were locally available as `linux/amd64`. The committed materializer was `ENVIRONMENT_MATERIALIZER_V1_3`, with source SHA-256 `99c74430f5f270f19624afc7285f8541acce08779a41165e8fb58d351271a211`.

## B–G. Ledger-derived identities and outcomes

The sole identity-count authority, `environment_build_recipes.csv`, assigns seven cases to `SOURCE_INDEPENDENT_ENVIRONMENT` and three to `REVISION_SPECIFIC_BUILD_REQUIRED`. This yields **13 required identities**: seven source-independent images and BUGGY/FIXED images for each of `spacy::4`, `ansible::2`, and `sanic::1`. The informational count in the Human-PI request agrees with the frozen ledger. All 13 identities received exactly one Docker build command and one attempt record.

| Order | Case | Mode | Identity outcome and frozen-build observation |
| ---: | --- | --- | --- |
| 21 | `tornado::6` | Source independent | `BUILD_FAILED`: frozen `pip install unittest` found no matching distribution. |
| 22 | `luigi::4` | Source independent | `BUILD_FAILED`: frozen `pywin32==227` had no matching Linux distribution. |
| 23 | `fastapi::2` | Source independent | `MATERIALIZED`: complete observed environment identity. |
| 24 | `youtube-dl::37` | Source independent | `MATERIALIZED`: complete observed environment identity. |
| 25 | `youtube-dl::18` | Source independent | `MATERIALIZED`: complete observed environment identity. |
| 26 | `spacy::4` | Revision specific | BUGGY and FIXED: `BUILD_FAILED`; frozen `python setup.py build_ext --inplace` reported `Running cythonize failed` in each build. |
| 27 | `ansible::2` | Revision specific | BUGGY and FIXED: `BUILD_FAILED`; frozen `ansible-base==2.10.0.dev0` had no matching distribution. |
| 28 | `sanic::1` | Revision specific | BUGGY and FIXED: `BUILD_FAILED`; frozen `pywin32==227` had no matching Linux distribution. |
| 29 | `thefuck::26` | Source independent | `BUILD_FAILED`: frozen pip raised `TomlError` while parsing a `cryptography` `pyproject.toml`. |
| 30 | `thefuck::28` | Source independent | `BUILD_FAILED`: frozen pip raised `TomlError` while parsing a `cryptography` `pyproject.toml`. |

Totals: **3 `MATERIALIZED`**, **10 `BUILD_FAILED`**, **0 runtime-identity blockers**, **0 input-identity blockers**, and **0 unsafe-symlink blockers**. A failed build remains a build observation, not an exclusion or eligibility decision. The CSV has one row per required identity and SHA-256 `2a6eb3abf0b1ef762dcca7273a329119869503d9d1aba5d484556d33afee2ebf`.

## H–K. V2 source, probe, and evidence audit

The six revision-specific source snapshots were exported from exact frozen Git blob bytes without `.git` history, repair patches, or an opposite revision in a build context. `SOURCE_SNAPSHOT_MANIFEST_V2` and `BUILD_CONTEXT_MANIFEST_V2` identities were checked against the raw snapshots and contexts. Tracked symlinks remained symlinks with exact target bytes: `ansible::2` had 69 safe links in each revision; `spacy::4` and `sanic::1` had none. Source-independent contexts contained no subject source.

Distribution Probe V2 ran only for the three successfully built images. `fastapi::2` used `STDLIB_IMPORTLIB_METADATA` under Python 3.8.3; both `youtube-dl` cases used `PIP_LIST_JSON` under Python 3.7.4. Each probe used `--network=none`, `--read-only`, and `--pull=never` with no subject import or installation. Failed builds did not reach the final-image distribution probe. No backend switch occurred.

Large evidence is outside Git under `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_03`. For every identity, the audit reconciled the attempt ID and frozen recipe, exact Docker command, Dockerfile/hash, V2 context manifest/hash, timestamps, raw build log/hash, exit code, source revision/snapshot where applicable, base digest, and network policy. The three `MATERIALIZED` records additionally have observed image ID, RootFS layers, Python version and executable hash, installed-distribution and system-package manifests, image-inspect evidence, and canonical `SCREENING_ENVIRONMENT_IDENTITY_V1` hash. Docker exit code zero alone was never treated as materialization. `NA` in the CSV means the final-image observation was unavailable because the build failed; no such value is fabricated.

## L–N. Attempt and execution boundaries

There was no retry, dependency change, Python change, base-image change, architecture change, source/symlink change, setup change, or frozen-recipe change. The case-level materializer stopped after each failed revision-specific BUGGY build. A separate `BATCH03_FIXED_FOLLOWTHROUGH_V1` controller made exactly one independent FIXED attempt for each of those three cases using the same committed materializer's input verification, base verification, V2 manifests, build definition, Docker command semantics, and final identity probes. It preserved all BUGGY attempt evidence unchanged. Build network policy was `NETWORK_ALLOWED_RECORDED`; identity observation and future execution policy were `NONE`.

The controllers invoked zero subject pytest/unittest commands, `run_test.sh`, `bugsinpy-test`, functional tests, oracle commands, 3/3 screening, eligibility classifiers, ErrPilot, repair agents, and model/API calls. No subject package import or project CLI was used as a post-build sanity test. Batch 01 and Batch 02 failures were not retried or repaired; their repository ledgers and reports remained byte-identical. Batch 04 was untouched. `cases_manifest.csv` and `exclusions.csv` remained header-only. The frozen recipes, candidate order, controlling documents, derived inputs, self-reference ledger, and materializer were unchanged.

## O–R. Repository validation and publication state

Repository-side validation passed: `python3 -m pytest evaluation/downstream_benchmark/tests` reported **107 passed, 2 skipped**; `python3 -m pytest` reported **89 passed**; `ruff check .` passed; and the staged diff whitespace check passed. The two skipped benchmark tests are opt-in synthetic Docker fixtures. No subject test or oracle was executed by repository validation.

Only `environment_materialization_batch_03.csv` and this report are authorized for the single commit `evaluation: record environment materialization batch 03`. The commit and push status are recorded in the transaction's final run report. A push requires a fresh live `origin/main` check and explicit Human-PI approval for the single ordinary fast-forward update. CI has not yet been observed for this Batch-03 commit.

## S–T. Batch 04 and next boundary

Cases 31–40 were not attempted. Any Batch-04 materialization requires separate Human-PI case authority and a fresh entry preflight. Neither this completed materialization nor its repository tests establish candidate eligibility, 3/3 screening, repair performance, or ErrPilot effectiveness.

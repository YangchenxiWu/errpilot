# Environment materialization Batch 01

Status: `ENVIRONMENT_MATERIALIZATION_BATCH_01_COMPLETE`.

## Human PI authority and boundary

The Human PI explicitly authorized real production environment materialization for exactly the frozen initial-selection-order cases 1 through 10: `pandas::102`, `pandas::78`, `pandas::4`, `pandas::45`, `scrapy::4`, `keras::9`, `matplotlib::17`, `keras::18`, `matplotlib::11`, `keras::28`. This transaction used the enabled frozen production materializer `ENVIRONMENT_MATERIALIZER_V1_1` at commit `69c3929143477c5d8fb1649a0614ce5e63288472` with token `BUGSINPY_ENVIRONMENT_MATERIALIZATION_AUTHORIZED_V1`. The authorization covered dependency installation, frozen setup/build actions, revision-specific source builds, Docker/OCI images, and environment identity observation. It did not authorize subject tests, oracles, eligibility, ErrPilot, repair, or model/API calls.

## Required identities and attempts

The frozen ledger yields 14 required identities: four revision-specific pandas cases with BUGGY and FIXED images, plus six source-independent cases. Each of the 14 identities received exactly one governed build attempt under ten case-level materializer attempt IDs; the `(attempt_id, revision_label)` pair identifies each identity. No retry or recipe modification occurred. Build network policy was `NETWORK_ALLOWED_RECORDED`; identity probes and all future environment execution use `NONE`.

| Order | Case | Required revision(s) and result |
| ---: | --- | --- |
| 1 | `pandas::102` | BUGGY: `MATERIALIZED`; FIXED: `MATERIALIZED` |
| 2 | `pandas::78` | BUGGY: `MATERIALIZED`; FIXED: `MATERIALIZED` |
| 3 | `pandas::4` | BUGGY: `MATERIALIZED`; FIXED: `MATERIALIZED` |
| 4 | `pandas::45` | BUGGY: `MATERIALIZED`; FIXED: `MATERIALIZED` |
| 5 | `scrapy::4` | SOURCE_INDEPENDENT: `BUILD_FAILED` |
| 6 | `keras::9` | SOURCE_INDEPENDENT: `BUILD_FAILED` |
| 7 | `matplotlib::17` | SOURCE_INDEPENDENT: `MATERIALIZED` |
| 8 | `keras::18` | SOURCE_INDEPENDENT: `BUILD_FAILED` |
| 9 | `matplotlib::11` | SOURCE_INDEPENDENT: `MATERIALIZED` |
| 10 | `keras::28` | SOURCE_INDEPENDENT: `BLOCKED_RUNTIME_IDENTITY` |

## Outcome and evidence

- Materialized: **10/14**.
- Frozen-recipe build failures: **3/14** (`scrapy::4`, `keras::9`, `keras::18`).
- Runtime identity blockers: **1/14** (`keras::28`).
- `scrapy::4`: the frozen dependency-only input requires `pywin32==227`, for which pip found no distribution on the frozen Linux runtime.
- `keras::9` and `keras::18`: the frozen dependency-only inputs require `numpy==1.19.0rc2`, for which pip found no matching distribution.
- `keras::28`: Docker build exited 0, but the frozen materializer distribution-manifest probe failed because Python 3.7.3 lacks `importlib.metadata`. The supplemental read-only probe records that exception and the observed image ID. This identity remains blocked; Docker exit 0 was not promoted to `MATERIALIZED`.

Large evidence is retained under `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_01`. Each case directory contains `attempt.json`, one revision directory per required identity, the exact Dockerfile, build context and manifest, raw build log and hash, and source snapshot manifest where applicable. Materialized rows also have image inspection, Python/distribution/system-package observations, canonical environment identity, and a network-disabled, read-only `/tmp` and `HOME` compatibility probe. The CSV links each identity to its external evidence. The source snapshots in the external build contexts contain no recoverable Git history, BugsInPy repair metadata, patch file, or screening-result evidence.

## Boundaries

The controller invoked zero subject pytest/unittest commands, `run_test.sh`, `bugsinpy-test`, oracle subcommands, 3/3 trials, eligibility classifiers, ErrPilot runs, repair agents, and model/API calls. Only the frozen build actions and harmless environment identity probes ran. `cases_manifest.csv` and `exclusions.csv` remain header-only. **MATERIALIZED != ELIGIBLE.** No candidate eligibility, screening result, repair result, or ErrPilot effectiveness claim follows from this batch.

## Known limits

The frozen materializer records networked build commands and raw logs but does not emit a standalone immutable download-artifact manifest. The `keras::28` successful Docker build lacks the canonical `SCREENING_ENVIRONMENT_IDENTITY_V1` because the distribution-manifest step failed. Its observed image ID is explicitly ungated. Later work requires separate Human-PI authority for any retry, materializer change, or subject oracle execution.

## Repository validation

Entry was `main` at local and `origin/main` commit `69c3929143477c5d8fb1649a0614ce5e63288472`, ahead/behind `0/0`, with a clean worktree and index. `PROTOCOL.md` and `RUN_SPEC_V1.md` retained their required SHA-256 hashes. The evidence audit verified the frozen initial-40 order, the ten authorized case directories, exactly 14 revision entries, one build command and raw log per identity, unchanged build definitions, source snapshot and context manifests, materialized identity hashes, and header-only `cases_manifest.csv` and `exclusions.csv`.

The benchmark-local suite passed with its opt-in synthetic Docker fixtures: 88 tests and 35 subtests. The full ErrPilot suite passed: 89 tests. `ruff check .` and `git diff --check` passed. An initial `pytest` entry-point invocation failed collection because it omitted the repository root from Python's import path; `python3 -m pytest` corrected that. The first synthetic Docker run from the sandbox could not access the Docker socket; the same synthetic-only suite passed with the authorized Docker access. Neither validation issue executed a real subject oracle.

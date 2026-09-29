# Expansion Block 02 environment materialization

Status: `EXPANSION_BLOCK_02_MATERIALIZATION_FIRST_PASS_COMPLETE`.

This is the first governed environment materialization pass. `MATERIALIZED != ELIGIBLE`. No subject test, oracle, screening, eligibility, repair, or downstream model execution was authorized or run.

## Entry and authority

- The Human PI invoked `EXPANSION_BLOCK_02_FIRST_PASS_BATCH_AUTHORITY_V1_FROZEN` for exactly one governed first-pass attempt per identity. Controller V2 used the outer token `BUGSINPY_EXPANSION_BLOCK_02_FIRST_PASS_BATCH_AUTHORIZED_V1`; each materializer request used the distinct inner token `BUGSINPY_EXPANSION_BLOCK_02_MATERIALIZATION_AUTHORIZED_V1`.
- The entry repository was clean `main` at `e148cd8d77e1847d84ab7e9ebd1e9bf5639c67af`. Live `origin/main` matched, ahead/behind was `0/0`, and no Block 02 result CSV/report or V2 production root existed. The Block 02 identity was `6d5a8a713ddcb18ea70b8268c72e7aa2d5e1eb44bace81f1bd485c88907c0b95`.
- The old incident root `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_02` remained sealed historical evidence. Its ten-file summary SHA-256 was unchanged at `1cea074fbac40c465bff0b3a76f1fbfcca8b79da3e0a14d38af47ad44a6a50bb`. The old `CONTROLLER_PRE_DISPATCH_INVALID_REQUEST` was a `NON_PRODUCTION_ATTEMPT` and consumed no governed attempt.
- The exact zero-production command `python3 -m evaluation.downstream_benchmark.screening.materialize_expansion_block_02_batch preflight` returned `12/12 Block 02 requests valid; zero production attempts`. The V2 root remained absent and the repository clean afterward. Docker was operational; six required frozen `linux/amd64` base images passed digest, architecture, Python-version, and executable-SHA probes. Static Block 02 preparation and the V3 exclusions validator passed; all required frozen source revisions and inputs resolved without a fetch or update.

## Production transaction and ordered outcomes

The one real batch command was:

```text
python3 -m evaluation.downstream_benchmark.screening.materialize_expansion_block_02_batch dispatch --batch-token BUGSINPY_EXPANSION_BLOCK_02_FIRST_PASS_BATCH_AUTHORIZED_V1
```

It was invoked once. All twelve distinct controller entries reached `CLOSED`, each with `governed_attempt_consumed=true`, one request, one canonical `attempt.json`, and one frozen Docker build. No identity was dispatched twice, skipped after its paired revision failed, or rescued. No unauthorized identity was dispatched. The two excluded cookiecutter cases were never requested.

| Order | Case | Identity | Outcome | Docker exit | Final image ID |
| ---: | --- | --- | --- | ---: | --- |
| 1 | `tornado::13` | SOURCE_INDEPENDENT | BUILD_FAILED | 1 | NA |
| 2 | `tornado::4` | SOURCE_INDEPENDENT | BUILD_FAILED | 1 | NA |
| 3 | `spacy::6` | BUGGY | BUILD_FAILED | 1 | NA |
| 3 | `spacy::6` | FIXED | BUILD_FAILED | 1 | NA |
| 4 | `fastapi::12` | SOURCE_INDEPENDENT | MATERIALIZED | 0 | `sha256:b4ff6cd46d6ddbe550d07a7c8c6fc0a979429e779219cc0874931f5fca0611d3` |
| 6 | `tqdm::7` | BUGGY | BUILD_FAILED | 1 | NA |
| 6 | `tqdm::7` | FIXED | BUILD_FAILED | 1 | NA |
| 8 | `spacy::7` | BUGGY | BUILD_FAILED | 1 | NA |
| 8 | `spacy::7` | FIXED | BUILD_FAILED | 1 | NA |
| 9 | `httpie::5` | SOURCE_INDEPENDENT | MATERIALIZED | 0 | `sha256:c8eaac5f6d9477a4d8c29ad0ea4c316f6fe055117cc86b375c5bd19a1c47964c` |
| 10 | `PySnooper::1` | BUGGY | MATERIALIZED | 0 | `sha256:cf8249aab08653c2708da5e0711ac664b4ee13f7f23d2f13f3cba629e10b44cb` |
| 10 | `PySnooper::1` | FIXED | MATERIALIZED | 0 | `sha256:fe5ca7b562e829421a8a45040b7a5ee9b05802c3c5b04f2f7cdc71de2b8366f8` |

There were **4 `MATERIALIZED`**, **8 `BUILD_FAILED`**, and **0 infrastructure/controller blockers**. Both tornado builds failed at their frozen `pip install unittest` setup action. Both tqdm builds failed on frozen `pkg-resources==0.0.0`. The four spacy builds failed during frozen dependency installation when `cython>=3.1` had no matching distribution for that runtime. These are recorded build outcomes, not new exclusion adjudications.

## Case-level readiness and capacity

For a source-independent case, readiness requires its sole identity to materialize. For a revision-specific case, it requires both BUGGY and FIXED to materialize.

| Case | Environment ready? |
| --- | --- |
| `tornado::13` | No |
| `tornado::4` | No |
| `spacy::6` | No |
| `fastapi::12` | Yes |
| `tqdm::7` | No |
| `spacy::7` | No |
| `httpie::5` | Yes |
| `PySnooper::1` | Yes |

The eight authorized cases yield **3** environment-ready cases. The prior ready count was **23**, so the current environment-ready ceiling is **26/28** required slots. `BLOCK_03_MATHEMATICALLY_REQUIRED = YES`. Block 03 was not constructed. The two cookiecutter cases remain excluded under their frozen preparation adjudication. `exclusions.csv` remains at 29 rows and `cases_manifest.csv` remains header-only. No eligibility status was assigned.

## Evidence audit and preservation

- The V2 production evidence root is `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_02_v2`. Its durable ledger SHA-256 is `c7e64e89c8b331c6499b97d8cfe7171581c113132e0c89005720769dd3db76fa`. Its 10,197-file summary SHA-256 is `6a98957c1c7c00d7e0ca19d42a11a400d193a15ac0969b9b41dd1e459bf4430d`, computed by hashing compact sorted-key JSON from relative file paths to SHA-256 values, as for the historical root. No symlinks exist in this V2 root. These hashes anchor later read-only checks; the external directory is not OS-level write-protected.
- The read-only audit checked the exact twelve request SHA-256 values against the controller ledger, exact frozen recipe and block hashes, revision labels and source commits, distinct attempt directories, raw controller stdout/stderr hashes, canonical attempt hashes, frozen inputs, Dockerfiles, context manifests, and raw build-log hashes. All matched. The eight nonzero build logs reached frozen dependency or setup commands; none showed a Docker-host failure.
- All eight revision-specific source snapshots matched their frozen Git blobs and `SOURCE_SNAPSHOT_MANIFEST_V2` identities. The corresponding build-context source trees matched byte-for-byte; their tracked symlink count was **0**. The four source-independent contexts contained no subject source. No source snapshot or evidence was changed during audit.
- All four successful `linux/amd64` image IDs and RootFS layer lists were re-inspected. Fresh network-disabled, read-only Python/distribution/system-package probes reproduced the saved manifests and `environment_identity.json` exactly. Three distribution probes used `STDLIB_IMPORTLIB_METADATA`; the Python 3.7.3 `httpie::5` probe used `PIP_LIST_JSON`. The installed distribution manifests exist for all four successful identities.
- The controller and frozen materializer ran no subject pytest, unittest, `run_test.sh`, tox, BugsInPy oracle, 3/3 screening, eligibility classification, ErrPilot, repair agent, or downstream model/API command. `pip install unittest` was a frozen installation action, not subject unittest execution. Build networking followed each frozen request; inspection probes used `--network=none`. No retry or rescue occurred.

## Repository validation and next Human-PI gate

- `python3 -m evaluation.downstream_benchmark.screening.prepare_expansion_block_02 verify` passed: eight ready and two already excluded preparation cases.
- `screening.executor.validate_controlling_inputs` passed the V3 exclusions union: 29 rows; the manifest has zero data rows.
- The twelve-row result CSV passed field-order, identity-uniqueness, and outcome-count checks.
- `python3 -m pytest evaluation/downstream_benchmark/tests -q` returned **134 passed, 2 skipped, 3 failed, 8 errors**. All 11 nonpassing tests are in `test_expansion_block_02_batch.py` and assume the V2 production root is absent. The required production root now exists, so its pre-dispatch fixture and root-absence assertions no longer apply to this post-dispatch state. No code or test was changed after seeing outcomes.

The Human PI must separately adjudicate any failed-build disposition and authorize any Block 03 construction, oracle screening, eligibility, or repair action. This materialization report grants none of those actions.

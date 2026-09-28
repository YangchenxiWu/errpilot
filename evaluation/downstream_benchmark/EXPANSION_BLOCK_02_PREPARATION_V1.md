# Section-M Expansion Block 02 preparation V1

Status: `EXPANSION_BLOCK_02_PREPARATION_V1_COMPLETE`.

The bounded static preparation transaction closed for all ten frozen candidates. Eight cases are `EXPANSION_PREPARATION_READY`; two are `EXPANSION_PREPARATION_BLOCKED` under the existing oracle and setup semantics. `EXPANSION_BLOCK_02_BUILD_RECIPES_V1_FROZEN` does not apply. All subject environments remain `UNBUILT`, and no eligibility decision was made.

## Authority and identity

Entry was on clean `main` at local and live `origin/main` `ce502a67ec2662ea5a255cdc7fa15bff32678ed0`, ahead/behind `0/0`. The frozen controlling inputs passed `screening.executor.validate_controlling_inputs`; `PROTOCOL.md`, `RUN_SPEC_V1.md`, `SCREENING_SPEC_V1.md`, and `candidate_universe.csv` matched their committed frozen identities. `exclusions.csv` contained exactly 27 rows and `cases_manifest.csv` remained header-only. The pinned BugsInPy checkout was clean and detached at commit `11c5f1eea954a42132cfd06bf257766a7963e0fd`, tree `d00ce0495ba73abe50317599f48bced3c9afe4b3`.

`expansion_block_02.csv` alone supplied the ten case memberships and their order. Every row matched the committed candidate universe for rank, rank hash, case and project identity, Python version, both revision IDs, and declared test path. The 144-row frozen traversal admitted exactly these ten cases in this order. None belonged to the initial 40 or Block 01. Canonical Block 02 identity SHA-256: `6d5a8a713ddcb18ea70b8268c72e7aa2d5e1eb44bace81f1bd485c88907c0b95`.

## Case results

| Order | Case | Oracle | Protected manifest | Environment mode | Recipe | Preparation |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | `tornado::13` | resolved, 1 command | resolved | `SOURCE_INDEPENDENT_ENVIRONMENT` | ready | ready |
| 2 | `tornado::4` | resolved, 2 commands | resolved | `SOURCE_INDEPENDENT_ENVIRONMENT` | ready | ready |
| 3 | `spacy::6` | resolved, 1 command | resolved | `REVISION_SPECIFIC_BUILD_REQUIRED` | ready | ready |
| 4 | `fastapi::12` | resolved, 1 command | resolved | `SOURCE_INDEPENDENT_ENVIRONMENT` | ready | ready |
| 5 | `cookiecutter::3` | unresolved: `tox` | resolved | `UNRESOLVED` | blocked | blocked |
| 6 | `tqdm::7` | resolved, 1 command | resolved | `REVISION_SPECIFIC_BUILD_REQUIRED` | ready | ready |
| 7 | `cookiecutter::4` | unresolved: `tox` | resolved | `UNRESOLVED` | blocked | blocked |
| 8 | `spacy::7` | resolved, 1 command | resolved | `REVISION_SPECIFIC_BUILD_REQUIRED` | ready | ready |
| 9 | `httpie::5` | resolved, 1 command | resolved | `SOURCE_INDEPENDENT_ENVIRONMENT` | ready | ready |
| 10 | `PySnooper::1` | resolved, 1 command | resolved | `REVISION_SPECIFIC_BUILD_REQUIRED` | ready | ready |

The existing bare mirrors for `tornado`, `spacy`, `fastapi`, `tqdm`, and `httpie` matched their frozen canonical source URLs and were used read-only. Exactly two bare mirrors were acquired from frozen URLs: `https://github.com/cookiecutter/cookiecutter` and `https://github.com/cool-RR/PySnooper`. No existing mirror was fetched or updated. All twenty metadata revisions resolved uniquely to distinct full 40-character BUGGY/FIXED commits. No repair diff or history was inspected.

Pinned BugsInPy `run_test.sh` bytes and SHA-256 values are preserved per case. The frozen `COMPOSITE_ORACLE_SEMANTICS_V1` parser resolved nine ordered recognized commands across eight cases. Both `cookiecutter` scripts invoke `tox`, which the frozen semantics do not recognize. This is recorded as `ORACLE_UNRESOLVED:subcommand 1: unrecognized test command tox`, without syntax amendment or execution. All ten protected manifests resolved declared and oracle-referenced test paths, exact BUGGY/FIXED Git blob SHA-256 identities, fixed-test injection, and effective buggy test identities.

## Static environment and recipe results

Nine requirements files were UTF-8 and one was UTF-16 with BOM. Raw, normalized, and dependency-only SHA-256 identities were recorded; five mechanically proven self references were removed only from derived dependency inputs and recorded in the Block 02 self-reference ledger. Setup bytes, hashes, line classifications, possible test invocation, environment modes, and literal `PYTHONPATH` metadata were analyzed as inert input. No case-specific rule was added. The `cookiecutter` setup line `python setup.py develop` is `UNSUPPORTED_OR_AMBIGUOUS` under the frozen setup-action taxonomy, producing `SETUP_UNRESOLVED:unsupported setup action at line 1: UNSUPPORTED_OR_AMBIGUOUS` for both cases. System package requirements remain `UNKNOWN` where the frozen static inputs do not prove them.

The eight ready cases have deterministic `EXPANSION_BLOCK_02_ENVIRONMENT_BUILD_RECIPE_V1` JSON and SHA-256 identities. Each binds the exact case/order and Block 02 identity, both full commits, declared and observed Python/base-image identities, requirements and self-reference hashes, setup ledger, protected manifest, execution plan, environment mode, source install policy, runtime platform, future network policies, and `materialization_identity = UNBUILT`. The two blocked recipe rows retain exact blocker reasons and contain no recipe JSON or recipe hash. All six declared Python versions matched previously frozen exact runtime identities; no Docker runtime probe was repeated.

## Evidence and regeneration

The Block 02 controller is `screening/prepare_expansion_block_02.py`; it binds only Block 02 and reuses the existing frozen environment, oracle, protected-manifest, and recipe helpers. It does not retarget or alter `prepare_expansion_block_01.py`. Its `verify` mode reconstructs candidate identities, all five ledgers, derived files, recipe hashes, and external preparation evidence from pinned inputs and compares every saved byte without mutation. Two in-memory derivations were byte-identical before writing; the saved artifacts passed read-only regeneration afterward.

Repository artifacts are `expansion_block_02_execution_plan.csv` (10 rows), `expansion_block_02_environment_requirements.csv` (10), `expansion_block_02_requirements_normalization.csv` (10), `expansion_block_02_self_reference_ledger.csv` (5), `expansion_block_02_environment_build_recipes.csv` (10), and `derived_inputs/expansion_block_02/`. The 78 external evidence files are isolated under `/Users/wuyangchenxi/errpilot-benchmark-work/expansion_block_02_preparation/` and are not committed. They include source identities, exact commits, oracle bytes and parsed representations, protected manifests, raw environment inputs, and preparation plans.

The Block 01 read-only verifier still passed, its external preparation evidence retained its pre-transaction identity, and no Block 01 or initial-40 tracked artifact changed. The exclusion and manifest boundaries remain unchanged. No subject checkout, Docker subject build, dependency installation, setup action, project build/install, subject import/test, oracle execution, eligibility screening, ErrPilot repair, or downstream model/API call occurred. Static preparation is not materialization or eligibility. Resolving the two `cookiecutter` blockers would require separate Human-PI authority over the frozen oracle/setup semantics; this transaction selected no replacement and triggered no Block 03.

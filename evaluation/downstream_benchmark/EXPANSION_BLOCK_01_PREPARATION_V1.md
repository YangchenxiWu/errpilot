# Section-M Expansion Block 01 preparation V1

Status: `EXPANSION_BLOCK_01_PREPARATION_V1_FROZEN`.

Overall result: `EXPANSION_BLOCK_01_PREPARATION_V1_COMPLETE`. All ten cases are `EXPANSION_PREPARATION_READY`; zero are `EXPANSION_PREPARATION_BLOCKED`. Because every case has a deterministic recipe, `EXPANSION_BLOCK_01_BUILD_RECIPES_V1_FROZEN` also applies. These labels describe static preparation only. All subject environments remain `UNBUILT`.

## Authority and input gate

This transaction follows the Human PI's bounded Expansion Block 01 preparation instruction. The local and live `origin/main` entry ref was `d467d38cbfb7f69753ea4b4f5a71e8f147a24ec9`, with branch `main`, ahead/behind `0/0`, and a clean index/worktree before any write. `PROTOCOL.md`, `RUN_SPEC_V1.md`, `SCREENING_SPEC_V1.md`, and `candidate_universe.csv` matched their frozen SHA-256 values. The exact 21 accepted `NON_RETRY` exclusions matched the normative adjudication CSV; `cases_manifest.csv` was header-only. These checks establish the requested pre-eligibility ledger state without claiming any eligibility outcome.

The sole membership and order input was `expansion_block_01.csv`. All ten rows were checked against the pinned candidate universe, and the frozen traversal and canonical block identity were reproduced. Block SHA-256: `8a478d475066ab94afccf80472aa031e141ec8639296487fdd7fa572308ae02c`. No case belongs to the initial 40. The pinned BugsInPy checkout was `11c5f1eea954a42132cfd06bf257766a7963e0fd` at tree `d00ce0495ba73abe50317599f48bced3c9afe4b3`.

## Prepared cases

| Order | Case | Oracle commands | Environment mode | Self-reference removals | Status |
| ---: | --- | ---: | --- | ---: | --- |
| 1 | `tornado::11` | 1 | `SOURCE_INDEPENDENT_ENVIRONMENT` | 0 | `EXPANSION_PREPARATION_READY` |
| 2 | `matplotlib::21` | 1 | `SOURCE_INDEPENDENT_ENVIRONMENT` | 0 | `EXPANSION_PREPARATION_READY` |
| 3 | `youtube-dl::24` | 1 | `SOURCE_INDEPENDENT_ENVIRONMENT` | 0 | `EXPANSION_PREPARATION_READY` |
| 4 | `tqdm::1` | 1 | `REVISION_SPECIFIC_BUILD_REQUIRED` | 1 | `EXPANSION_PREPARATION_READY` |
| 5 | `black::6` | 2 | `REVISION_SPECIFIC_BUILD_REQUIRED` | 1 | `EXPANSION_PREPARATION_READY` |
| 6 | `luigi::6` | 2 | `SOURCE_INDEPENDENT_ENVIRONMENT` | 1 | `EXPANSION_PREPARATION_READY` |
| 7 | `black::15` | 1 | `REVISION_SPECIFIC_BUILD_REQUIRED` | 1 | `EXPANSION_PREPARATION_READY` |
| 8 | `thefuck::8` | 2 | `SOURCE_INDEPENDENT_ENVIRONMENT` | 1 | `EXPANSION_PREPARATION_READY` |
| 9 | `sanic::2` | 1 | `REVISION_SPECIFIC_BUILD_REQUIRED` | 1 | `EXPANSION_PREPARATION_READY` |
| 10 | `luigi::20` | 1 | `SOURCE_INDEPENDENT_ENVIRONMENT` | 1 | `EXPANSION_PREPARATION_READY` |

All ten existing bare project mirrors matched the canonical source URLs. Both metadata revisions for each case resolved uniquely to full 40-character commits from those mirrors. No mirror update or network acquisition was needed. The preparation read no fix diff or repair history. The pinned `run_test.sh` bytes were preserved under the separate external evidence root. Their 13 substantive commands were parsed as ordered, recognized direct-argv commands under `COMPOSITE_ORACLE_SEMANTICS_V1`; no shell or oracle command was executed. Each protected manifest resolved the declared and oracle-referenced test paths and recorded buggy, fixed, and effective buggy blob SHA-256 identities under the frozen fixed-test injection semantics.

The requirements audit found five UTF-8 and five UTF-16-with-BOM inputs, including any empty raw files as present files. Normalization changed line endings only; seven exact self references were removed from derived dependency-only files and ledgered. The frozen setup taxonomy yielded six source-independent environments and four revision-specific builds. No setup action was executed. The exact previously probed Python base-runtime identities were reused; no Docker runtime probe was repeated. Every recipe binds the case/order, both full commits, Python and immutable base-image identities, raw and derived input hashes, setup actions, protected manifest, execution plan, environment mode, and frozen build/network policies. Recipe hashes use canonical sorted-key UTF-8 JSON with no timestamp.

## Separate artifacts and regeneration

The expansion-only repository ledgers are `expansion_block_01_execution_plan.csv`, `expansion_block_01_environment_requirements.csv`, `expansion_block_01_requirements_normalization.csv`, `expansion_block_01_self_reference_ledger.csv`, and `expansion_block_01_environment_build_recipes.csv`, with row counts 10, 10, 10, 7, and 10. Derived inputs live under `derived_inputs/expansion_block_01/`. External source, oracle, protected-manifest, raw-input, and plan evidence lives under `/Users/wuyangchenxi/errpilot-benchmark-work/expansion_block_01_preparation/` and is not committed.

The preparation implementation is `screening/prepare_expansion_block_01.py`. Its `verify` mode rebuilds all repository and external artifacts from pinned inputs and compares every byte to the saved files without writing. Two independent in-memory builds were byte-identical before publication. The final on-disk verification and repository tests are reported in the transaction run report, not treated as scientific or eligibility validation.

The original initial-40 screening, environment, normalization, self-reference, recipe, exclusion, and manifest artifacts were not edited. Initial-40 loaders still return 40 cases. No subject checkout, dependency installation, setup/project build, Docker subject build, import, subject test, oracle, eligibility run, repair, ErrPilot, or downstream model/API invocation occurred. `MATERIALIZED != ELIGIBLE`; these cases are not materialized. Any real Expansion-01 environment materialization requires a separate Human-PI transaction and its own identity gate.

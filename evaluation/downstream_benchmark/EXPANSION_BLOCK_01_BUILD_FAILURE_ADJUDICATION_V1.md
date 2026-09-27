# Expansion Block 01 build-failure adjudication V1

Status: `EXPANSION_BLOCK_01_BUILD_FAILURE_ADJUDICATION_V1_FROZEN`.

## Authority and entry identity

The Human PI accepts all six Expansion Block 01 first-pass build-failed cases as `ACCEPTED_EXCLUSION` with `NON_RETRY`. This decision applies only to Expansion Block 01. It does not change `INITIAL_40_BUILD_FAILURE_ADJUDICATION_V1.md` or its companion CSV. Entry repository `/Users/wuyangchenxi/errpilot` was clean on `main` at `bb6deb046c4eae4b30933083f66c26927d9ee8a5`; live `origin/main` matched and ahead/behind was `0/0`.

The frozen selection is `expansion_block_01.csv` (SHA-256 `89bd95f71c230dcde90cdb422ea31218bd11e840aebe60641267e36b163f4186`). The committed first-pass report is `EXPANSION_BLOCK_01_ENVIRONMENT_MATERIALIZATION.md` (SHA-256 `d8583cf4546fc50b47c2f8ffd2cca26b7a765d1c5e3f07c1a737db334e4e0304`), and its 14-row identity ledger is `expansion_block_01_environment_materialization.csv` (SHA-256 `a19da1968e75df1745fdc80991ff646e7ea9538205c4cb67bc71272022d600e2`). The external audit JSON SHA-256 is `cd104b6b491b031ecc183f5c87844ae63e1ad0c411fa5e9c6a723690fc703a54`. All 14 saved build logs matched their committed ledger hashes at entry.

## First-pass accounting and dispositions

Ten selected cases required 14 environment identities. All 14 received one governed first-pass attempt: six `MATERIALIZED`, eight `BUILD_FAILED`, and zero other blockers. Four cases have every required identity materialized: `matplotlib::21`, `youtube-dl::24`, `black::6`, and `black::15`. The other six are incomplete because at least one required identity was `BUILD_FAILED`:

| Order | Case | Failed identities | Observed first blocker and failure family | Final exclusion reason |
| ---: | --- | --- | --- | --- |
| 1 | `tornado::11` | SOURCE_INDEPENDENT | Frozen `pip install unittest` found no distribution; `FROZEN_SETUP_ACTION_FAILURE`, `SETUP_UNITTEST_INSTALL` | `DEPENDENCY_SETUP_FAILURE` |
| 4 | `tqdm::1` | BUGGY, FIXED | Frozen `pkg-resources==0.0.0` unavailable in both builds; `FROZEN_ARTIFACT_UNAVAILABLE`, `ARTIFACT_PKG_RESOURCES_0_0_0` | `DEPENDENCY_SETUP_FAILURE` |
| 6 | `luigi::6` | SOURCE_INDEPENDENT | Frozen `pywin32==227` unavailable on linux/amd64; `FROZEN_PLATFORM_INCOMPATIBLE_DEPENDENCY`, `PLATFORM_PYWIN32_227` | `UNSUPPORTED_ENVIRONMENT` |
| 8 | `thefuck::8` | SOURCE_INDEPENDENT | Base pip 18.1 raised `pytoml TomlError` on transitive cryptography metadata; `HISTORICAL_BUILD_TOOLCHAIN_DRIFT`, `TOOLCHAIN_PIP18_CRYPT_TOML` | `DEPENDENCY_SETUP_FAILURE` |
| 9 | `sanic::2` | BUGGY, FIXED | Frozen `pywin32==227` unavailable on linux/amd64 in both builds; `FROZEN_PLATFORM_INCOMPATIBLE_DEPENDENCY`, `PLATFORM_PYWIN32_227` | `UNSUPPORTED_ENVIRONMENT` |
| 10 | `luigi::20` | SOURCE_INDEPENDENT | Frozen `pywin32==227` unavailable on linux/amd64; `FROZEN_PLATFORM_INCOMPATIBLE_DEPENDENCY`, `PLATFORM_PYWIN32_227` | `UNSUPPORTED_ENVIRONMENT` |

The companion `expansion_block_01_build_failure_adjudication_v1.csv` binds each disposition to the committed report, committed identity ledger, and preserved attempt directories. Its frozen SHA-256 is `f3909b354c685391c2279f698835fb17c330ebf2e2b1cd1c7f2c185f8f12284c`. The six rows have a 3/3 split between `UNSUPPORTED_ENVIRONMENT` and `DEPENDENCY_SETUP_FAILURE`.

## Meaning and downstream boundary

`NON_RETRY` means the Human PI will not perform post-outcome recovery or another production build for these six under this benchmark's frozen first-pass environment policy. No dependency, Python, platform, source, recipe, toolchain, or package-index amendment is adopted. Repeated historical symptoms provide context, not a systemic retry rule. The first-pass attempts, build logs, materialization ledger, and audit remain preserved and unchanged. This decision does not claim that another environment could never reproduce a case or that later build stages were observed.

The initial 40 have 19 environment-ready cases. Expansion Block 01 adds four, for 23 total. The benchmark requires at least 28 slots: 24 final and four permanently separate pilots. Since `23 < 28`, a Section-M Expansion Block 02 is mathematically required before any oracle attrition is considered. This transaction does not construct or select Block 02, advance the ranking cursor, or inspect future candidates. `MATERIALIZED != ELIGIBLE`: `cases_manifest.csv` remains header-only, with no 3/3 oracle screening or eligibility decision. Subject acquisition, build or retry, subject import or test, oracle, repair, ErrPilot, and downstream model/API gates remain closed.

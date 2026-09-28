# Expansion Block 02 materializer bridge V1

Status: `EXPANSION_BLOCK_02_MATERIALIZER_BRIDGE_V1_FROZEN`.

## Authority and boundary

The bridge transaction entered on clean `main` at local and live `origin/main` commit `58465e80cf5b4b940e0382c2c88ce5482ffa98c8`, ahead/behind `0/0`. The frozen Block 02 identity is `6d5a8a713ddcb18ea70b8268c72e7aa2d5e1eb44bace81f1bd485c88907c0b95`. `EXPANSION_BLOCK_02_PREPARATION_V1_COMPLETE`, `EXPANSION_BLOCK_02_PREPARATION_BLOCKER_ADJUDICATION_V1_FROZEN`, and `PRE_ELIGIBILITY_EXCLUSIONS_LEDGER_STATE_V3_VALIDATED` were verified from committed inputs before editing. The V3 normative union contains 29 unique exclusions: nine `UNSUPPORTED_ENVIRONMENT`, 18 `DEPENDENCY_SETUP_FAILURE`, and two `ORACLE_COMMAND_INVALID`. `cases_manifest.csv` is header-only.

The bridge establishes capability, not authority to execute it. Real Block 02 materialization requires a separate Human-PI authorization naming each production identity. This transaction executed zero real Block 02 materialization calls, subject Docker builds, dependency or setup actions, subject tests, oracles, eligibility assignments, repairs, or downstream model/API calls. No Block 02 result ledger or production attempt root was created.

## Frozen ten-case state

The committed preparation ledger has ten ordered cases. Eight are both `EXPANSION_PREPARATION_READY` and `BUILD_RECIPE_READY`; two are both `EXPANSION_PREPARATION_BLOCKED` and `BUILD_RECIPE_BLOCKED`. The ready cases and future identity shapes derive from the frozen recipe modes:

| Order | Case | Environment mode | Possible future identities |
| ---: | --- | --- | --- |
| 1 | `tornado::13` | `SOURCE_INDEPENDENT_ENVIRONMENT` | `SOURCE_INDEPENDENT` |
| 2 | `tornado::4` | `SOURCE_INDEPENDENT_ENVIRONMENT` | `SOURCE_INDEPENDENT` |
| 3 | `spacy::6` | `REVISION_SPECIFIC_BUILD_REQUIRED` | `BUGGY`, `FIXED` |
| 4 | `fastapi::12` | `SOURCE_INDEPENDENT_ENVIRONMENT` | `SOURCE_INDEPENDENT` |
| 6 | `tqdm::7` | `REVISION_SPECIFIC_BUILD_REQUIRED` | `BUGGY`, `FIXED` |
| 8 | `spacy::7` | `REVISION_SPECIFIC_BUILD_REQUIRED` | `BUGGY`, `FIXED` |
| 9 | `httpie::5` | `SOURCE_INDEPENDENT_ENVIRONMENT` | `SOURCE_INDEPENDENT` |
| 10 | `PySnooper::1` | `REVISION_SPECIFIC_BUILD_REQUIRED` | `BUGGY`, `FIXED` |

The mode split is exactly four source-independent and four revision-specific cases. It yields 12 possible future production identities, ordered by expansion order and `BUGGY` before `FIXED` within each revision-specific case. This count grants no attempt authority. A future failed `BUGGY` attempt does not suppress a separately authorized `FIXED` attempt.

Orders 5 and 7 are `cookiecutter::3` and `cookiecutter::4`. Both are `NON_RETRY` / `ACCEPTED_EXCLUSION` with final `ORACLE_COMMAND_INVALID` under the Block 02 normative adjudication. Their frozen recipe rows have no recipe JSON or hash and mode `UNRESOLVED`. The validator checks the blocker evidence and their presence in the V3 exclusions; neither case can receive a build capability.

## Materializer authority bridge

`screening/materializer.py` defines a separate `EXPANSION_02_AUTHORITY_TOKEN` with exact value `BUGSINPY_EXPANSION_BLOCK_02_MATERIALIZATION_AUTHORIZED_V1`. Its `check_expansion_block_02_ledger()` checks all ten frozen rows, Block 02 identity and candidate-universe binding, statuses, normative blocked cases, the eight recipe hashes and modes, self-reference rows, and Block 02 derived input paths and bytes. It returns only the eight ready recipes. Hash mismatch or malformed input fails closed.

`materialize_expansion_block_02_request()` requires that exact token, the existing real-materialization gate, and a clean committed materializer. It rejects blocked and out-of-block cases before calling the shared `_materialize_checked()` engine. A request binds expansion block, order, identity, recipe hash, self-reference ledger, and exact `derived_inputs/expansion_block_02/` paths. The separate `materialize-expansion-02` CLI dispatches only to this entrypoint. Block 01's token, validator, entrypoint, and CLI remain separate and unchanged.

Each request names exactly one identity. Source-independent requests require `SOURCE_INDEPENDENT` with the exact `ABSENT` revision object, so no subject source snapshot enters the build context. Revision-specific requests require exactly one `BUGGY` or `FIXED` revision, the frozen source revision SHA, a full snapshot SHA-256, and a nonempty source reference. The shared Source Snapshot V2 path verifies the supplied snapshot against the input tree before Docker work. The bridge reuses the existing symlink preservation, distribution probe, Docker identity, network policy, and restart-safe evidence machinery; it does not fork a Docker builder.

## Frozen materialization input hashes

These SHA-256 values are derived from the clean entry commit and enforced by the Block 02 validator:

| Artifact under `evaluation/downstream_benchmark/` | SHA-256 |
| --- | --- |
| `EXPANSION_BLOCK_02.md` | `9c358171f01e2dd696bdaaeab022c82157c40b4119cf99f20035093e19260584` |
| `expansion_block_02.csv` | `b1d4cc0a8c863535ef881d4c25b4ddd469ab5925cedc36a6e5783c20d01cd6a7` |
| `EXPANSION_BLOCK_02_PREPARATION_V1.md` | `82c3fe89c9bf954502eeaa9b134a9c95371e4d815546af0cc83d3df3bee797c8` |
| `expansion_block_02_execution_plan.csv` | `2c59d144470e4d1f02dcfe582604a5f3d269cb6c26003494be60f90d3b0e166e` |
| `expansion_block_02_requirements_normalization.csv` | `7363a0274865341f32352147a45f6fc150ccefb316ea57597698f444f99f7c5f` |
| `expansion_block_02_self_reference_ledger.csv` | `3d03e4420993097031ea8c0cc5ddbe0e3902dfa1779f4f88484727184f1ef765` |
| `expansion_block_02_environment_build_recipes.csv` | `e22c2ac2e416a2cbf5177d2c3bbf00978f8dbbe2a3815f0a8b7e3398eacec3df` |
| `EXPANSION_BLOCK_02_PREPARATION_BLOCKER_ADJUDICATION_V1.md` | `8c5c1c005acb836051009853809ee9cf8126bd636f98ecadf9105c3b2286b32a` |
| `expansion_block_02_preparation_blocker_adjudication_v1.csv` | `b802fbc633563540dcd3c2567d57ba39520dbc829ca1df60b0f1bd86af2abb45` |
| `PRE_ELIGIBILITY_EXCLUSIONS_LEDGER_STATE_V3.md` | `867855a8a2d2dad02931470f4c10410e6763ad486a87ba49365a0ec9bcd66ad4` |
| `exclusions.csv` | `817ffd6c788f3f757964aa484203842d2db9d18fb46ff220bdb6982b5efb9201` |

The validator also binds `candidate_universe.csv` to its previously frozen SHA-256 `78208adf610a50542be6dfbd03a9b25960ba0b5cfc80768b08ffe7a4c78f3b8c`.

## Next gate

The Human PI must separately authorize any of the 12 real identities before a production request uses this bridge. Materialization remains distinct from oracle screening and eligibility. This freeze does not authorize Block 03 selection or repair execution.

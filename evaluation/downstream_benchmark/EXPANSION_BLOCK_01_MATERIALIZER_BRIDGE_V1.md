# Expansion Block 01 materializer bridge V1

Status: `EXPANSION_BLOCK_01_MATERIALIZER_BRIDGE_V1_FROZEN`.

## Trigger and preserved authority

The committed V1.3 production entrypoint was limited to the frozen initial 40 through `environment_build_recipes.csv` and `self_reference_ledger.csv`. Its `check_frozen_ledger()` still returns exactly those 40 recipes, and `materialize_real_request()` still rejects an Expansion Block 01 case. The initial token, `BUGSINPY_ENVIRONMENT_MATERIALIZATION_AUTHORIZED_V1`, applies only to that existing path. Historical attempts retain their recorded materializer versions and evidence.

## Block 01 authority domain

`check_expansion_block_01_ledger()` is a separate read-only validator. It checks the frozen Block 01 source, recipe, execution-plan, normalization, and self-reference ledger file hashes; exactly ten ordered rows; canonical case and rank membership; recipe schema `EXPANSION_BLOCK_01_ENVIRONMENT_BUILD_RECIPE_V1`; recipe hash and `UNBUILT` state; `linux/amd64`; future execution network policy `NONE`; execution-plan and protected-manifest identities; and every repository-derived normalized/dependency input hash. It derives the mode counts from the recipes: six `SOURCE_INDEPENDENT_ENVIRONMENT` and four `REVISION_SPECIFIC_BUILD_REQUIRED`, or 14 required identities. These counts are observations, not substitute authority for the ledger.

The canonical Block 01 identity is `8a478d475066ab94afccf80472aa031e141ec8639296487fdd7fa572308ae02c`. The frozen `expansion_block_01_environment_build_recipes.csv` SHA-256 is `8a9efeb613f6f175322a6c52b899efc30ddb8654b0856e5145ec92c018fc1bf1`. `expansion_block_01.csv` SHA-256 is `89bd95f71c230dcde90cdb422ea31218bd11e840aebe60641267e36b163f4186`.

The dedicated CLI subcommand is `materialize-expansion-01`. It requires exact token `BUGSINPY_EXPANSION_BLOCK_01_MATERIALIZATION_AUTHORIZED_V1`, a clean committed materializer HEAD, an explicit single-case request, input root, and output path. The request must name a frozen Block 01 case, order, block identity, recipe hash, and exact Block 01 self-reference rows. The request's normalized and dependency input paths must be under `derived_inputs/expansion_block_01/<case>/`; the shared build engine verifies their supplied bytes against the frozen recipe hashes. Initial-40 derived-input and self-reference namespaces cannot satisfy this entrypoint. The expansion token cannot authorize the initial-40 entrypoint, and the initial token cannot authorize this one.

After all authority checks, this entrypoint calls the existing `_materialize_checked()` engine once for the requested case. That engine retains `SOURCE_SNAPSHOT_MANIFEST_V2`, `BUILD_CONTEXT_MANIFEST_V2`, tracked safe-symlink preservation, and `DISTRIBUTION_PROBE_V2`: Python below 3.8 uses `PIP_LIST_JSON`; Python 3.8 and later use `STDLIB_IMPORTLIB_METADATA`. No subject import, test, oracle, eligibility, repair, or model/API path was added. Bare invocation, `validate`, and `plan` remain non-materializing and describe only the original initial-40 domain. No command enumerates and builds Block 01 automatically.

## Validation and execution boundary

Synthetic tests cover token separation, case membership, wrong block/order/schema/hash/ledger/namespace, exact ten-row validation, single-request dispatch, and clean committed HEAD. Existing materializer tests cover the original production rejection, Source Snapshot V2, Distribution Probe V2, and absence of oracle/repair/model execution. Repository validation is recorded in the transaction run report.

This bridge establishes capability only. Zero real Expansion Block 01 environments were built in this transaction; there was no initial-40 retry, subject dependency installation, setup, subject test, oracle, eligibility, repair, or downstream model/API invocation. A later Human-PI transaction must explicitly name Expansion Block 01 and its case(s), pass a fresh identity and clean-HEAD gate, and authorize each real build attempt. `EXPANSION_BLOCK_01_REAL_MATERIALIZATION_PATH_READY` does not itself authorize any attempt. `MATERIALIZED != ELIGIBLE`.

# Expansion Block 02 post-production test reconciliation V1

Status: `EXPANSION_BLOCK_02_POST_PRODUCTION_TEST_RECONCILIATION_V1_FROZEN`.

## Entry and bounded authority

This test-harness transaction entered on clean `main` at local HEAD and live
`origin/main` `97384cce3cdcf309244e4be01eba472b1975dc2a`, ahead/behind `0/0`.
No `.airos/current_state.md` or repository Research Contract was present; the
Human-PI reconciliation instruction controls the two-file write boundary.

Production completed before this transaction, with committed status
`EXPANSION_BLOCK_02_MATERIALIZATION_FIRST_PASS_COMPLETE`: 12 governed identities,
4 `MATERIALIZED`, 8 `BUILD_FAILED`, and zero infrastructure/controller blockers.
The environment-ready cases remain `fastapi::12`, `httpie::5`, and `PySnooper::1`;
the current environment-ready count remains 26. `MATERIALIZED != ELIGIBLE`.

The real Controller V2 root
`/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_02_v2`
legitimately exists. Its existence is preserved production evidence, not a
controller defect. Production `derive_requests()` must still reject an existing
configured root to prevent a second batch.

## Reproduced failures and root-lifecycle cause

Before editing, the benchmark suite reproduced **134 passed, 2 skipped,
3 failed, 8 errors**, with 128 passing subtests. The target module reproduced
**3 passed, 3 failed, 8 errors**. Every nonpassing test was in
`tests/test_expansion_block_02_batch.py`:

| Test | Prior result | Verified cause |
| --- | --- | --- |
| `test_exact_derivation_and_zero_docker_preflight` | Error | B: module request fixture derived against real existing ROOT |
| `test_all_hashes_paths_and_request_shapes` | Error | B: same fixture |
| `test_pure_validator_matches_production_boundary` | Error | B: same fixture |
| `test_preflight_needs_no_batch_token` | Error | B: same fixture |
| `test_valid_batch_token_reaches_only_mocked_dispatch_once_per_identity` | Error | B: same fixture; also retained an obsolete real-root absence assertion |
| `test_pre_dispatch_rejection_preserves_controller_streams` | Error | B: same fixture |
| `test_mock_governed_attempt_transitions_and_restart_safety` | Error | B: same fixture |
| `test_ambiguous_dispatch_without_attempt_blocks` | Error | B: same fixture |
| `test_exact_outer_batch_token_rejects_every_other_authority` | Failure | A/C: rejected-token action succeeded, then asserted real ROOT absent |
| `test_missing_dispatch_token_cli_rejects_before_derivation` | Failure | A/C: missing-token rejection succeeded, then asserted real ROOT absent |
| `test_historical_incident_classification_and_root_remain_frozen` | Failure | C: historical invariants passed, then asserted V2 ROOT absent |

All eight fixture errors were `Blocked: future V2 production root must be absent`.
The three failures were the subsequent root-absence assertions. The report's
causal claim was therefore independently reproduced; no controller/materializer
regression was demonstrated.

## Test isolation and invariant preservation

- The module fixture still calls real deterministic `derive_requests()`, using
  `tmp_path_factory` for an absent V2 test root and its matching WORK namespace.
  WORK also locates frozen source mirrors: a scoped wrapper retains the original
  real source-identity checks and Git-blob hashing without using the production
  evidence root. Docker and the materializer engine remain assertion-guarded.
- A function fixture binds ROOT/WORK to `tmp_path` for root-absence checks,
  preflight CLI, rejected tokens, and valid-token mocked dispatch. All four
  remaining action-level absence assertions refer to temporary paths; the
  module fixture also asserts its derivation root remains absent.
- Exact 12 identities, order, recipe hashes, paths, and Block-02 validator
  behavior remain checked. All twelve canonical request SHA-256 values now also
  match the committed materialization CSV, requiring no external V2 evidence.
- Valid-token mocked dispatch creates only its temporary root and dispatches
  the exact twelve distinct identities once. Its real-root capture/absence
  assertion was removed. Staging, ledger saving, and identity dispatch remain
  mocked; the transition tests retain mocked materializer subprocesses.
- The historical-incident test lost only its final V2-root absence assertion.
  Its three classifications, exact ten-file hash, and empty attempts-directory
  check remain unchanged and pass.
- `test_preflight_refuses_existing_future_root` is unchanged and passes entirely
  in `tmp_path`, proving the production existing-root firewall still fails
  closed. Neither production controller nor materializer changed.

No unit test requires real V2 evidence to exist or disappear, and no unit test
reads its 10,197 files. The before/after external hash audit below was a separate
read-only preservation check, not part of ordinary unit tests or CI.

## Post-reconciliation validation

| Command | Result |
| --- | --- |
| `python3 -m pytest evaluation/downstream_benchmark/tests/test_expansion_block_02_batch.py -q` | 14 passed |
| `python3 -m pytest evaluation/downstream_benchmark/tests -q` | 145 passed, 2 skipped, 128 subtests passed |
| `python3 -m pytest -q` | 89 passed |
| `python3 -m ruff check .` | All checks passed |
| `git diff --check` | Passed |

No test was added, removed, or parametrized differently. The benchmark pass count
increased by exactly eleven because the three failures and eight fixture errors
now pass. The two explicit Docker-validation tests remain skipped. The default
pytest command selects `tests/` via `pyproject.toml`; the separately required
benchmark command covers the benchmark tests.

## Scientific and production evidence preservation

Before/after SHA-256 and mode comparisons preserved 407 of 408 entry tracked
files; only the authorized test module changed. This includes all 306 other
benchmark files.
The compact sorted-key JSON map of those 306 relative repository paths to
SHA-256 values has digest
`ceeb4bcdefc95563f9becae00d0d716ea4f01ce0b6877ac2276b225667e8c3b5`.

| Protected file | Unchanged SHA-256 |
| --- | --- |
| `screening/materialize_expansion_block_02_batch.py` | `5a1f89cdd0ab41c9695d0e10374b9c3a40eb389f1afa54abdcdb356c41da4991` |
| `screening/materializer.py` | `162e09ccee3d4b3e8e19d8d0dd942af551bcada198aea8935b07c025cd5f104f` |
| `EXPANSION_BLOCK_02_ENVIRONMENT_MATERIALIZATION.md` | `cad9e6189cb87ef45b2db68685ee4a419f80f20eca1a020250d17a23721487ff` |
| `expansion_block_02_environment_materialization.csv` | `06c91e7303749d4e2e5d676aee8455d2371078cf80a8e70521e8f1dbf52ea443` |

External file hashes and directory identities were unchanged:

- Historical root: ten files, summary SHA-256
  `1cea074fbac40c465bff0b3a76f1fbfcca8b79da3e0a14d38af47ad44a6a50bb`;
  attempts directory remains empty.
- V2 production root: 10,197 files, summary SHA-256
  `6a98957c1c7c00d7e0ca19d42a11a400d193a15ac0969b9b41dd1e459bf4430d`;
  twelve preserved ledger entries remain CLOSED with governed attempts consumed.

This transaction performed zero real Docker builds, Block-02 production
dispatches, dependency installations, setup actions, subject pytest/unittest,
`run_test.sh`, subject oracles, eligibility, repair, or model/API execution.
The required repository suites exercised their existing temporary synthetic
fixtures and mocks only; they create no scientific execution evidence.

Only this record and the named test module changed. No scientific result,
selection, exclusion, manifest, production semantics, or external evidence
changed. This freeze grants no new execution authority. Any failed-build
disposition, Block 03 work, subject oracle/eligibility screening, or repair
requires a separate Human-PI gate; publication of this transaction additionally
requires interactive approval of exactly `git push origin main:main`.

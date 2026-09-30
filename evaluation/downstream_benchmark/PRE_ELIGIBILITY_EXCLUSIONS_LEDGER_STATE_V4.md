# Pre-eligibility exclusions-ledger state V4

Status: `PRE_ELIGIBILITY_EXCLUSIONS_LEDGER_STATE_V4_FROZEN`.

The Human PI accepts the five Block 02 first-pass build exclusions under
`EXPANSION_BLOCK_02_BUILD_FAILURE_ADJUDICATION_V1_FROZEN`. The controlling entry
is clean `main` at `b27f635e8bacbf9dc99b5523a58380e1780e4fe8`, matching live
`origin/main`. V4 supersedes V3 only as the current pre-eligibility ledger state;
it does not rewrite prior scientific or normative decisions.

| Independent normative authority | Unique exclusions |
| --- | ---: |
| `initial_40_build_failure_adjudication_v1.csv` | 21 |
| `expansion_block_01_build_failure_adjudication_v1.csv` | 6 |
| `expansion_block_02_preparation_blocker_adjudication_v1.csv` | 2 |
| `expansion_block_02_build_failure_adjudication_v1.csv` | 5 |
| Exact authoritative union | 34 |

`exclusions.csv` contains exactly 34 unique case IDs, with nine
`UNSUPPORTED_ENVIRONMENT`, 23 `DEPENDENCY_SETUP_FAILURE`, and two
`ORACLE_COMMAND_INVALID`. Its SHA-256 is
`e13187b561745222873f6533d7883556b786fcab7f455b5035e664f558654f45`.
The complete predecessor header and 29 data rows remain byte-for-byte unchanged,
including timestamps, reasons, evidence references, and notes. Exactly five rows
are appended in frozen Block 02 orders 1, 2, 3, 6, 8: `tornado::13`, `tornado::4`,
`spacy::6`, `tqdm::7`, `spacy::7`. Their one shared transaction timestamp is
`2026-09-30T16:13:52Z`. All five have stage `ENVIRONMENT_MATERIALIZATION`, reason
`DEPENDENCY_SETUP_FAILURE`, `ACCEPTED_EXCLUSION`, and `NON_RETRY` authority.
The three ready Block 02 cases are not exclusions.

The validator checks all four normative sources independently, binds the five
new cases to every required preserved first-pass `BUILD_FAILED` identity, then
checks the exact 34-row union and 9/23/2 reason split. It rejects missing, extra,
duplicate, mutated, proposal-only, environment-ready, and unadjudicated rows.
`PRE_ELIGIBILITY_EXCLUSIONS_LEDGER_STATE_V4_VALIDATED` applies only when the
validator passes against these exact committed files.

`cases_manifest.csv` remains header-only; SHA-256:
`c7d423696616ffb7d5dc79fa5bf56294044b3d66c247c744d575617dbb89dac9`.
Environment/preparation exclusion != eligibility outcome. No case is yet
classified `ELIGIBLE`; `MATERIALIZED != ELIGIBLE`, and environment-ready !=
eligible. No subject/oracle/eligibility execution occurs in this ledger transition.

The accepted current `NON_RETRY` policy fixes recovered-case count `r = 0`.
Environment-ready capacity remains 26 against 28 required slots, so
`BLOCK_03_MATHEMATICALLY_REQUIRED = YES`. Oracle attrition may require further
expansion. This transaction constructs no Block 03 and does not advance the
candidate cursor. Future ledger transitions and all acquisition, preparation,
materialization, oracle, eligibility, allocation, and repair phases require
separate Human-PI authority.

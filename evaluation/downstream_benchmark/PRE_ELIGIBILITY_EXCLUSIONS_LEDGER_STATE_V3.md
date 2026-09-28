# Pre-eligibility exclusions-ledger state V3

Status: `PRE_ELIGIBILITY_EXCLUSIONS_LEDGER_STATE_V3_FROZEN`.

## Authority and transition

The predecessor `PRE_ELIGIBILITY_EXCLUSIONS_LEDGER_STATE_V2.md` recorded 27 exclusions. The current authoritative union consists of 21 accepted initial-40 exclusions in `initial_40_build_failure_adjudication_v1.csv`, six accepted Block 01 exclusions in `expansion_block_01_build_failure_adjudication_v1.csv`, and two accepted Block 02 preparation exclusions in `expansion_block_02_preparation_blocker_adjudication_v1.csv`. The 27 predecessor rows, their timestamps, and their evidence references are unchanged. The two new rows have one transaction timestamp, `2026-09-28T13:04:00Z`.

The union in `exclusions.csv` is exactly 29 unique case IDs. Reason totals are nine `UNSUPPORTED_ENVIRONMENT`, 18 `DEPENDENCY_SETUP_FAILURE`, and two `ORACLE_COMMAND_INVALID`. Current `exclusions.csv` SHA-256: `817ffd6c788f3f757964aa484203842d2db9d18fb46ff220bdb6982b5efb9201`. The committed validator checks each normative source separately and then checks this exact union. `PRE_ELIGIBILITY_EXCLUSIONS_LEDGER_STATE_V3_VALIDATED` applies only when that validator passes against these committed files.

`cases_manifest.csv` remains header-only (SHA-256 `c7d423696616ffb7d5dc79fa5bf56294044b3d66c247c744d575617dbb89dac9`). Environment materialization exclusions and oracle-preparation exclusions are not oracle execution outcomes. No case is yet `ELIGIBLE` on this evidence. V3 supersedes V2 only as the repository's current pre-eligibility ledger state; it does not alter the scientific meaning of prior adjudications. Future ledger transitions require separate Human-PI authority. Materialization, oracle, eligibility, pilot/final allocation, Block 03, and repair gates remain closed.

# Pre-eligibility exclusions-ledger state V2

Status: `PRE_ELIGIBILITY_EXCLUSIONS_LEDGER_STATE_V2_FROZEN`.

## Authority and transition

The predecessor V1 state was the 21 initial-40 accepted exclusions, each governed by `INITIAL_40_BUILD_FAILURE_ADJUDICATION_V1.md` and the frozen `initial_40_build_failure_adjudication_v1.csv` (SHA-256 `74cb6d321e2d2b0225be62b7026f8cd5eb9a113d7e3a13f7506e7fa5b218ae2c`). These 21 rows, including timestamps, evidence references, reasons, and order, are preserved byte-for-byte in the current ledger.

The Human PI's Expansion Block 01 decision is recorded in `EXPANSION_BLOCK_01_BUILD_FAILURE_ADJUDICATION_V1.md` and its six-row CSV (SHA-256 `f3909b354c685391c2279f698835fb17c330ebf2e2b1cd1c7f2c185f8f12284c`). The six `NON_RETRY` exclusions were appended in `expansion_order` 1, 4, 6, 8, 9, 10 with one transaction timestamp, `2026-09-27T12:31:09Z`.

The exact union in `exclusions.csv` is 27 unique cases: 21 initial plus six Expansion Block 01. The initial reason split is six `UNSUPPORTED_ENVIRONMENT` and 15 `DEPENDENCY_SETUP_FAILURE`; the expansion split is three and three; the combined split is **nine** and **18**. Current `exclusions.csv` SHA-256 is `5de4d51a955452ce998a0aab36f2ff88a18cc478f9a63ce5120296d52d08b61c`.

`cases_manifest.csv` remains header-only (SHA-256 `c7d423696616ffb7d5dc79fa5bf56294044b3d66c247c744d575617dbb89dac9`). Environment-ready cases are absent from the exclusions ledger. An environment exclusion is not an oracle or eligibility result, and no case is classified `ELIGIBLE` or oracle-`INELIGIBLE` here.

V2 supersedes only the repository's current pre-eligibility exclusions-ledger state. It does **not** supersede the scientific meaning or normative authority of initial adjudication V1. Any later ledger transition requires separate Human-PI authority and a corresponding validator update. The oracle, eligibility, pilot/final allocation, Block 02 construction, and repair gates remain closed.

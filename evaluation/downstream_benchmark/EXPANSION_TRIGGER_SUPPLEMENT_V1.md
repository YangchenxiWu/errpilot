# Expansion trigger scheduling supplement V1

Status: `EXPANSION_TRIGGER_SUPPLEMENT_V1_FROZEN`.

Authority: the Human PI's 2026-09-26 metadata-only scheduling instruction for Section-M Expansion Block 01. This versioned supplement interprets only the timing of the first block's construction. `SCREENING_SPEC_V1.md` remains byte-identical and controls candidate ranking, traversal, and project-cap semantics.

## A. Original Section-M trigger and accepted state

`SCREENING_SPEC_V1.md` section M states that expansion follows completed 3/3 screening of the initial 40 if too few eligible cases remain to reserve four permanently separate pilot cases and select 24 final cases. Section M also requires blocks of ten, the next frozen global ranking, a cursor after the final global row examined, permanent skips, and a cumulative cap of four admissions per project.

The accepted `INITIAL_40_BUILD_FAILURE_ADJUDICATION_V1.md` and companion CSV classify exactly 21 of the 40 initial candidates as `ACCEPTED_EXCLUSION` with `NON_RETRY`. `exclusions.csv` contains those same 21 case/reason pairs. Exactly 19 initial cases have all required environments materialized. `cases_manifest.csv` is header-only; there are zero initial eligibility outcomes. `MATERIALIZED != ELIGIBLE`.

## B. Mathematical trigger and scheduling interpretation

The initial-40 eligibility ceiling is `40 - 21 = 19`. The benchmark requires at least `24 + 4 = 28` eligible slots, including four permanently separate pilot cases. Since `19 < 28`, at least one expansion block is mathematically unavoidable even if every remaining initial case passes 3/3 screening. This conclusion uses the 21 exclusions only to establish the need for expansion. Exclusion, failure, and environment-feasibility information must never rank or select expansion candidates.

The Human PI therefore authorizes construction and freezing of `SECTION_M_EXPANSION_BLOCK_01` before the remaining initial cases run their oracles. This is a metadata-only, pre-oracle scheduling interpretation of Section M. It does not waive 3/3 screening of the 19 remaining initial cases, establish their eligibility, or allocate pilot or final cases.

## C. Preserved gates

The frozen BugsInPy metadata ranking, sampling seed, permanent skip rule, and cumulative four-candidate-per-project cap remain unchanged. The 40 original admissions all count toward the cap, including the 21 later environment exclusions; no slot is reclaimed. Section M still requires a frozen ten-admission block before any outcome from that block is observed.

This supplement authorizes zero subject acquisition, revision checkout, environment construction, dependency installation, subject import/test, oracle, eligibility execution, pilot/final allocation, repair experiment, ErrPilot invocation, or downstream model/API call. Block 01 must not be executed under this authority. Additional expansion beyond Block 01 remains separately gated by Human-PI authority and the frozen rules. Future acquisition or materialization of any Block-01 case also requires separate explicit authority.

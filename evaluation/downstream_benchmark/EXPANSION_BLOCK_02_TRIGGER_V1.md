# Expansion Block 02 trigger V1

Status: `EXPANSION_BLOCK_02_TRIGGER_V1_FROZEN`.

## A. Current authority state

The Human PI's corrected Block-02 instruction authorizes a metadata-only Section-M Block 02 freeze. The frozen `PRE_ELIGIBILITY_EXCLUSIONS_LEDGER_STATE_V2.md` (SHA-256 `754e8d10bf35fa2b630350755fd43778e5c67cd7f131822a79067a40734008e8`) governs the exact current exclusions ledger. The committed `screening.executor.validate_controlling_inputs` accepted its 27-row union as `PRE_ELIGIBILITY_EXCLUSIONS_LEDGER_STATE_V2_VALIDATED`. The frozen `EXPANSION_BLOCK_01_BUILD_FAILURE_ADJUDICATION_V1.md` (SHA-256 `657cea5539dd016c76c0efb93c14a5468ef5cd5bff8e62b6626b3d52e9416a7f`) governs the capacity calculation. These separate sources jointly establish the trigger; neither source was rewritten.

## B. Accepted exclusions and capacity

`exclusions.csv` (SHA-256 `5de4d51a955452ce998a0aab36f2ff88a18cc478f9a63ce5120296d52d08b61c`) contains 27 unique normative environment exclusions: 21 initial-40 plus six Block-01 cases. The initial 40 have 19 environment-ready cases and Block 01 adds four, for **23** total. The benchmark requires **28** slots: 24 final plus four permanently separate pilot cases. Since **23 < 28**, Block 02 is mathematically required even before any oracle attrition. Environment-ready does not mean eligible; `cases_manifest.csv` remains header-only and records zero oracle or eligibility outcomes.

## C. Scheduling and selection boundary

The frozen `EXPANSION_TRIGGER_SUPPLEMENT_V1.md` established the pre-oracle scheduling interpretation for Block 01. The Human PI's corrected Block-02 instruction separately authorizes this block before oracle screening because the current 23 environment-ready cases cannot fill 28 slots. Exclusion information establishes only the need for this block; it is not a rank, admission, or feasibility input. The frozen Block-01 traversal ended at candidate rank **102** (Block-01 identity SHA-256 `8a478d475066ab94afccf80472aa031e141ec8639296487fdd7fa572308ae02c`); Block 02 begins strictly after it at rank **103**. Initial-40 and Block-01 exclusions do not release cumulative project-cap slots.

This trigger and Block-02 freeze authorize zero subject acquisition, revision checkout, preparation, recipe construction, environment build, dependency installation, subject import or test, oracle, eligibility screening, pilot/final allocation, ErrPilot or other repair execution, or downstream model/API call. Any Block-02 execution requires separate Human-PI authority and controlling identity gates.

# Expansion Block 03 trigger V1

Status: `EXPANSION_BLOCK_03_TRIGGER_V1_FROZEN`.

## A. Current V4 authority and capacity

The Human PI's 2026-09-30 instruction authorizes only terminal Section-M
adjudication and metadata freeze. Entry: clean `main` at local HEAD and live
`origin/main` `fe60347faf7e6f85ee2159ea80e0d0d53be82a9e`, ahead/behind `0/0`.

`PRE_ELIGIBILITY_EXCLUSIONS_LEDGER_STATE_V4.md` is frozen, SHA-256
`540572c9f81385bd425ebe4c69e31b7a049614ef7be8b76bd0909b8e9b754e6a`.
The committed `screening.executor.validate_controlling_inputs` passes:
`PRE_ELIGIBILITY_EXCLUSIONS_LEDGER_STATE_V4_VALIDATED`.

The exact normative union is 21 initial-40, six Block-01, two Block-02
preparation, and five Block-02 build exclusions: **34** unique accepted
`NON_RETRY` exclusions. `exclusions.csv` remains SHA-256
`e13187b561745222873f6533d7883556b786fcab7f455b5035e664f558654f45`.
The prior candidate set has **60** distinct metadata admissions. Recovery is
zero under the accepted policy, leaving **26** environment-ready candidates:
`60 - 34 = 26 = 19 + 4 + 3`.

The required capacity remains **28**: 24 final cases plus four permanently
separate pilots. Since **26 < 28**, `BLOCK_03_MATHEMATICALLY_REQUIRED = YES`,
independently of future oracle attrition. Environment-ready != eligible;
`MATERIALIZED != ELIGIBLE`. `cases_manifest.csv` remains header-only, SHA-256
`c7d423696616ffb7d5dc79fa5bf56294044b3d66c247c744d575617dbb89dac9`, with zero
oracle/eligibility outcomes.

## B. Frozen cursor and terminal-exhaustion adjudication

The authoritative Block-02 traversal and tenth admission terminate at rank
**246**. Its canonical block identity is
`6d5a8a713ddcb18ea70b8268c72e7aa2d5e1eb44bace81f1bd485c88907c0b95`.
Block 03 begins strictly after it at rank **247**. Earlier skips remain skipped;
all 60 admissions count toward the cumulative cap **4**, including exclusions.

`SECTION_M_TERMINAL_EXHAUSTION_ADJUDICATION_V1.md` is
`SECTION_M_TERMINAL_EXHAUSTION_ADJUDICATION_V1_FROZEN`, SHA-256
`bd3d95f56d9aa6332363216b04b91123ac4c0a284076b26504efb399e1daf059`. Its Human-PI rule
`SECTION_M_TERMINAL_PARTIAL_BLOCK_RULE_V1` resolves the unchanged Section-M
terminal BLOCK clause. Two independent traversals exhaust all **254** rows at
ranks **247..500**, finding exactly **7** legal admissions and **247** cap
skips. All 500 ranked eligible identities and their contiguous ranks are checked;
**no rank above 500 exists**. A full ten-case block is impossible. The final
terminal partial block must include **all seven** legal remaining admissions.

## C. Metadata-only selection and next authority gate

The 34 exclusions and 26 environment-ready count establish only the trigger.
Block-03 membership uses only frozen rank, metadata eligibility, prior
membership, cumulative cap, previous cursor, and exhaustion. No Block-03
outcome exists, was inspected, or was used in selection. No environment/build
likelihood, tox or dependency availability, prior cookiecutter blocker,
complexity, patch/difficulty, or desired project mix enters selection.

This trigger authorizes zero subject acquisition, preparation, recipe/build,
dependency/setup install, subject import/test, oracle, eligibility, pilot/final
allocation, ErrPilot/repair, or downstream model/API execution. After freeze,
the next cursor state is `RANKING_EXHAUSTED`; no Block 04 is possible under the
current universe/ranking/cap/prior-skip rules. Any later capacity shortfall
requires another explicit Human-PI protocol adjudication, which is not
pre-authorized. Block-03 acquisition, preparation, and every subsequent phase
remain subject to separate explicit Human-PI authority and identity gates.

# Section-M terminal-exhaustion adjudication V1

Status: `SECTION_M_TERMINAL_EXHAUSTION_ADJUDICATION_V1_FROZEN`.

## A. Human-PI authority and controlling rule

The Human PI's 2026-09-30 terminal-exhaustion transaction explicitly authorizes
this normative metadata-only adjudication and the final terminal Expansion
Block 03. The entry is clean `main` at local HEAD and live `origin/main`
`fe60347faf7e6f85ee2159ea80e0d0d53be82a9e`, ahead/behind `0/0`.
No `.airos/current_state.md` or repository Research Contract is present; the
explicit transaction instruction controls the five-file write boundary.

`SCREENING_SPEC_V1.md` Section M remains frozen and unchanged, SHA-256
`a7f3cd5e73d6c733f560456d9f3949be18deca9b295ffb4ef2ae087af7e89db3`.
Its controlling expansion paragraph is:

> Expansion occurs in blocks of 10 admissions. The cursor begins after the final
> global rank examined to create the current candidate set; previously skipped cases
> remain skipped. Traverse forward, admit only metadata-eligible cases not already in
> the candidate set, and maintain the cumulative four-candidate-per-project cap. A
> block and its identities MUST be frozen before any outcome is observed from that
> block. If a full block cannot be formed under the cap or the ranking is exhausted,
> BLOCK for human-PI adjudication rather than hand-picking, changing the seed, reusing
> an earlier skipped case, or weakening the cap. Pilot and final selection remain
> governed by `PROTOCOL.md` and `RUN_SPEC_V1.md`; screening results cannot alter the
> candidate ranking.

This transaction is the Human-PI adjudication contemplated by that terminal
BLOCK clause. Its purpose is to resolve terminal block size after exhaustive
mechanical traversal, preserving every other frozen selection rule. It changes
only terminal block-size handling; ordinary nonterminal blocks still require
10 admissions. It does not edit Section M, the protocol, or the run specification.

## B. Separately authorized capacity trigger

`PRE_ELIGIBILITY_EXCLUSIONS_LEDGER_STATE_V4.md` is
`PRE_ELIGIBILITY_EXCLUSIONS_LEDGER_STATE_V4_FROZEN`, SHA-256
`540572c9f81385bd425ebe4c69e31b7a049614ef7be8b76bd0909b8e9b754e6a`.
The committed `screening.executor.validate_controlling_inputs` passes against
the current exact 34-case normative union:
`PRE_ELIGIBILITY_EXCLUSIONS_LEDGER_STATE_V4_VALIDATED`.

The frozen initial 40 plus Block 01 and Block 02 contain 60 distinct metadata
admissions. V4 accepts 34 `NON_RETRY` exclusions, with no recovered cases:
`60 - 34 = 26` environment-ready candidates (19 initial + 4 Block 01 + 3
Block 02). The benchmark requires 28 slots: 24 final cases and four permanently
separate pilots. Since `26 < 28`, expansion is mathematically required before
any oracle attrition. The Human PI separately authorizes Block 03 in this
transaction. These capacity facts establish need only and are not selection
inputs. `cases_manifest.csv` remains header-only, with zero oracle/eligibility
outcomes. Environment-ready != eligible; `MATERIALIZED != ELIGIBLE`.

## C. Exhaustive terminal facts established before adjudication

The frozen BugsInPy commit is `11c5f1eea954a42132cfd06bf257766a7963e0fd`, tree
`d00ce0495ba73abe50317599f48bced3c9afe4b3`. `candidate_universe.csv` remains
SHA-256 `78208adf610a50542be6dfbd03a9b25960ba0b5cfc80768b08ffe7a4c78f3b8c`.
Sampling seed remains `20260922`; cumulative project cap remains **4**.

The authoritative Block-02 traversal ends with its tenth admission at rank
**246**. Counts include all 60 prior metadata admissions, including excluded
cases; exclusions release no admission or project-cap slots. The terminal
traversal begins strictly after that cursor at rank **247**, examines every
ranked row exactly once, and continues through rank **500**, without stopping
on the seventh admission at rank 485.

Both independent derivations establish:

- the census has 501 unique cases, 500 metadata-eligible ranked cases and one
  unranked metadata exclusion;
- recomputed seed/case digests sorted by digest and canonical-ID tie-breaker
  reproduce exactly the contiguous ranks **1..500**;
- **no ranked eligible row has rank greater than 500**;
- the terminal range **247..500** contains **254** examined rows;
- decisions are **7 ADMIT** and **247 SKIP_PROJECT_CAP**;
- all other skip categories have count **0**;
- every admission is metadata eligible, previously unselected, unexamined, and
  below the cumulative cap before admission;
- every skipped terminal row has project count **4** before its decision.

Thirteen projects already have four cumulative admissions. The other projects
supply the entire remaining legal capacity:

| Project | Pre-block count | Remaining cap slots | Ranked cases after 246 | Maximum legal admissions |
| --- | ---: | ---: | ---: | ---: |
| `PySnooper` | 1 | 3 | 2 | 2 |
| `cookiecutter` | 2 | 2 | 2 | 2 |
| `sanic` | 2 | 2 | 3 | 2 |
| `tqdm` | 3 | 1 | 6 | 1 |
| Thirteen initially capped projects | 52 | 0 | 241 | 0 |
| **Total** | **60** | **8** | **254** | **7** |

The sum over projects of `min(4 - pre_block_count, remaining_ranked_cases)` is
**7**, and exhaustive traversal admits all seven. Therefore an eighth, ninth,
or tenth legal admission does not exist; a full 10-case block cannot be formed.
The missing fourth PySnooper candidate is not invented: that project has only
three metadata-eligible cases in the entire frozen universe.

The complete mechanically determined admissions, in frozen rank order, are
`tqdm::6` (259), `PySnooper::3` (369), `sanic::3` (380), `sanic::5` (405),
`PySnooper::2` (431), `cookiecutter::2` (472), and `cookiecutter::1` (485).
The complete row-level decisions and every `project_count_before` are retained
in `expansion_block_03_traversal.csv`; exact admitted metadata is retained in
`expansion_block_03.csv`.

Derivation A reconstructs project counts from frozen initial-40 membership and
both admission CSVs, binds the cursor to Block-02's final traversal/admission,
and traverses the frozen numeric rank map. Derivation B recomputes and sorts
all seed/case digests, independently replays initial 40 and both ten-admission
blocks, checks their frozen membership and traversal ledgers, then traverses the
entire remaining ranking. Before this adjudication was written, their complete
terminal results agreed on all 254 identities, every decision/reason/count,
all seven admission identities and metadata/order, both endpoints, exhaustion,
and all post-block project counts. The Human-PI informational cross-check was
compared only after derivation and agreed; it was not used to choose candidates.

## D. Normative Human-PI terminal partial-block rule

Rule identity: `SECTION_M_TERMINAL_PARTIAL_BLOCK_RULE_V1`.

For this benchmark, when all of the following hold:

A. a separately authorized expansion is required;

B. traversal begins at the frozen current cursor;

C. the unchanged frozen ranking and cumulative project cap are preserved;

D. ranking exhaustion occurs before 10 admissions can be collected; and

E. at least one legal admission remains;

then the final terminal expansion block **SHALL consist of ALL remaining legal
admissions encountered before ranking exhaustion**.

No candidate may be omitted. No earlier skipped candidate may be reconsidered.
No project cap may be relaxed. No seed/ranking may be changed. No new candidate
source may be introduced. No target block size may be padded manually.

The established facts satisfy A-E. The Human PI therefore adjudicates the
terminal Section-M condition by freezing the final terminal partial Block 03
as exactly those **seven** admissions. This is normative Human-PI authority,
not an agent recommendation or inferred permission.

## E. Unchanged invariants and prospective timing

The adjudication preserves the frozen candidate ranking, seed, metadata
eligibility criteria, cumulative project cap, prior-skip permanence, cursor
semantics, candidate universe, pilot/final rules, oracle criteria, environment
rules, and repair rules. Ranks at or below 246, including all initial-40,
Block-01, and Block-02 skips, are never revisited. No hand-picking, cap-slot
release after exclusion, ranking change, or desired project mix is permitted.

No Block-03 acquisition, preparation, build, oracle, or eligibility outcome
exists at this boundary. No Block-03 outcome was inspected or used. This rule
is frozen prospectively before all such outcomes. Selection uses only frozen
rank, metadata eligibility, prior selection, cumulative project cap, previous
cursor, and exhaustion. Build likelihood, package/dependency availability, tox,
known prior cookiecutter blockers, environment/oracle complexity, patches,
bug/repair difficulty, and project-mix preference do not enter selection.
`cookiecutter::1` and `cookiecutter::2` receive the same frozen metadata rules
as every other candidate.

## F. Terminal consequence and downstream authority gate

After the Block-03 freeze, `RANKED_CANDIDATE_UNIVERSE_EXHAUSTED` holds and the
next cursor state is `RANKING_EXHAUSTED`. No Block 04 can be constructed under
the current candidate universe, ranking, prior-skip permanence, and cumulative
cap. If later screening/materialization leaves insufficient cases, another
explicit Human-PI protocol adjudication would be required. This transaction
does not pre-authorize that adjudication or a new candidate source.

This freeze authorizes zero subject clone/fetch, environment preparation,
requirements parsing beyond frozen selection metadata, recipe generation,
Docker subject build, dependency/setup install, subject import/test, oracle,
eligibility, pilot/final allocation, ErrPilot/repair, or downstream model/API
execution. Future Block-03 acquisition and preparation each require separate
explicit Human-PI authority and immutable identity gates; later phases remain
separately gated. Ordinary deterministic repository validation is permitted.
No historical evidence or existing frozen artifact is rewritten.

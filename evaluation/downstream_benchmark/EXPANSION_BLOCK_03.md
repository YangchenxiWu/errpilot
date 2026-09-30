# Section-M terminal Expansion Block 03

Status: `SECTION_M_EXPANSION_BLOCK_03_FROZEN`.

## A. Human-PI authority and controlling identities

The Human PI's 2026-09-30 transaction authorizes the Section-M terminal-exhaustion
adjudication and exactly the final mechanically derived terminal partial Block
03. Entry: clean `main` at local HEAD and live `origin/main`
`fe60347faf7e6f85ee2159ea80e0d0d53be82a9e`, ahead/behind `0/0`.
The write boundary contains only the adjudication, trigger, this specification,
admission CSV, and complete traversal CSV. No implementation change is needed.

- Human-PI adjudication: `SECTION_M_TERMINAL_EXHAUSTION_ADJUDICATION_V1.md`,
  status `SECTION_M_TERMINAL_EXHAUSTION_ADJUDICATION_V1_FROZEN`, SHA-256
  `bd3d95f56d9aa6332363216b04b91123ac4c0a284076b26504efb399e1daf059`.
- Rule: `SECTION_M_TERMINAL_PARTIAL_BLOCK_RULE_V1`; the terminal block consists
  of **all** remaining legal admissions before ranking exhaustion.
- Trigger: `EXPANSION_BLOCK_03_TRIGGER_V1.md`, status
  `EXPANSION_BLOCK_03_TRIGGER_V1_FROZEN`, SHA-256
  `9106a9475da1231577b68fdf7ab92087c537a97e709a8c096a4a2833789330e2`; V4 proves 34 accepted exclusions
  and **26 < 28** environment-ready/required slots. These counts establish
  need only and never enter selection.
- Pinned BugsInPy commit: `11c5f1eea954a42132cfd06bf257766a7963e0fd`.
- Pinned BugsInPy tree: `d00ce0495ba73abe50317599f48bced3c9afe4b3`.
- Frozen `candidate_universe.csv` SHA-256:
  `78208adf610a50542be6dfbd03a9b25960ba0b5cfc80768b08ffe7a4c78f3b8c`.
- Sampling seed: **20260922**. Digest: SHA-256 of UTF-8
  `20260922|candidate|<project>::<bug_id>`, ascending digest then canonical ID.
- `PROTOCOL.md` SHA-256:
  `34e014a07821dc9dca52178874eef0b847aee7f048071fb4920864ae5d3bee93`.
- `RUN_SPEC_V1.md` SHA-256:
  `29ab6f78739d0eeea1c2a774e62e2d133f173e160c3d247407970a80726f4406`.
- Unchanged `SCREENING_SPEC_V1.md` SHA-256:
  `a7f3cd5e73d6c733f560456d9f3949be18deca9b295ffb4ef2ae087af7e89db3`.
- Cumulative project cap: **4**, counting every prior admission even after
  exclusion. No cap slots are released, and no prior skip is reconsidered.

## B. Previous cursor and cumulative project counts

The initial 40 end at rank **71**, Block 01 at rank **102**, and Block 02 at
rank **246**. The latter's tenth admission and traversal terminal agree;
Block-02 identity SHA-256 is
`6d5a8a713ddcb18ea70b8268c72e7aa2d5e1eb44bace81f1bd485c88907c0b95`.
The previous cursor is exactly **246**; first examined rank is **247**.
Counts are reconstructed from all 40 initial admissions plus all ten Block-01
and all ten Block-02 admissions, with no environment/exclusion input.

| Project | Before Block 03 | After Block 03 |
| --- | ---: | ---: |
| `PySnooper` | 1 | 3 |
| `ansible` | 4 | 4 |
| `black` | 4 | 4 |
| `cookiecutter` | 2 | 4 |
| `fastapi` | 4 | 4 |
| `httpie` | 4 | 4 |
| `keras` | 4 | 4 |
| `luigi` | 4 | 4 |
| `matplotlib` | 4 | 4 |
| `pandas` | 4 | 4 |
| `sanic` | 2 | 4 |
| `scrapy` | 4 | 4 |
| `spacy` | 4 | 4 |
| `thefuck` | 4 | 4 |
| `tornado` | 4 | 4 |
| `tqdm` | 3 | 4 |
| `youtube-dl` | 4 | 4 |
| **Total** | **60** | **67** |

Every project remains at or below four. PySnooper ends at three; a fourth
case is not fabricated.

## C. Complete exhaustive terminal traversal

`expansion_block_03_traversal.csv`, SHA-256
`ac46a4c73bdef279d615f2eaf706598f2f64e24c68e78b6625b8178307e25968`, records exactly one row for every
rank **247..500**, inclusive: **254** rows. Traversal continues through rank
500 after the seventh admission at rank 485. It never stops merely because
fewer than ten admissions have been found.

Each row preserves frozen rank/digest/case/project/metadata status, all three
prior-membership flags, `project_count_before`, decision/reason, and admitted
order. All examined rows are metadata eligible, previously unselected, and
outside all earlier examined/skipped ranges. Each prior-membership flag is
`false`. Decisions are **ADMIT=7**, **SKIP_PROJECT_CAP=247**; all other skip
categories have count zero. Every capped row has pre-decision count 4 and
reason `CUMULATIVE_PROJECT_CAP_4_REACHED`. Every admission has pre-decision
count below 4 and reason
`SECTION_M_TERMINAL_PARTIAL_BLOCK_NEXT_RANKED_UNDER_PROJECT_CAP`.

The frozen census contains 501 unique cases: 500 eligible ranked rows and
one unranked metadata exclusion (`keras::12`). Recomputed digests and numeric
rank positions agree exactly on contiguous ranks **1..500**. Their maximum
is 500 and **zero** ranked eligible rows lie above it. Exhaustion therefore
covers the entire frozen ranked eligible universe, not a truncated sample.

Thirteen projects have already reached cap 4 and supply 241 terminal rows.
For projects initially below cap, the suffix contains two PySnooper cases
(three available cap slots), three sanic cases (two slots), two cookiecutter
cases (two slots), and six tqdm cases (one slot). Their maximum legal
admissions sum to `min(3,2)+min(2,3)+min(2,2)+min(1,6)=7`.
Exhaustive traversal admits all seven; every other terminal row is capped.
The one later sanic row and five later tqdm rows also skip after those projects
reach cap, giving `241 + 1 + 5 = 247` total cap skips.
No eighth, ninth, or tenth legal admission exists, so a full 10-case block is
impossible under the unchanged ranking/cap/skip rules.

## D. Exact complete terminal admissions

`expansion_block_03.csv`, SHA-256
`50231362538d477ab262a783da904b51552652dd490267c1c4c84a59db3fcc8b`, contains exactly **seven** data rows,
`expansion_block=3`, orders 1..7. It preserves candidate metadata exactly from
`candidate_universe.csv`, including Python versions, buggy/fixed commit IDs,
and declared test files. All rows have `METADATA_ELIGIBLE`, all three
prior-membership flags `false`, and admission reason
`SECTION_M_TERMINAL_PARTIAL_BLOCK_NEXT_RANKED_UNDER_PROJECT_CAP`.

| Order | Rank | Case | Rank SHA-256 | Project count before | Project count after |
| ---: | ---: | --- | --- | ---: | ---: |
| 1 | 259 | `tqdm::6` | `851d768874f0eae83c570076a5879a68fd298f4acb7db0f8d2c5b9ecf7192b82` | 3 | 4 |
| 2 | 369 | `PySnooper::3` | `b5b35c934b0627f46485e59542e6f665cf2f01255c378d24d6859d29f563b721` | 1 | 2 |
| 3 | 380 | `sanic::3` | `bcf12b72645b11e60debf17279bd64e4a37e7c16a216a71ab4504f6bfa2070f2` | 2 | 3 |
| 4 | 405 | `sanic::5` | `ca16c995329f799c4851938f9e8ffe34d3ebcb6bbd45558a3741e4967961d326` | 3 | 4 |
| 5 | 431 | `PySnooper::2` | `d781a79e565be9f24006e19b38061313cb381a350ec5cc5ef5a953096e71a3f2` | 2 | 3 |
| 6 | 472 | `cookiecutter::2` | `ecdcc97568ac8115b419a5f463ec2cdd94568de54f9130d87a9105dd7d5fe47b` | 2 | 3 |
| 7 | 485 | `cookiecutter::1` | `f20623af65022361a9fb23e8d6480837e784e315d7f546bf27a6a680ac78a0cf` | 3 | 4 |

These are all legal remaining candidates. None is omitted, replaced,
hand-picked, manually padded, or admitted by weakening the cap. Prior
cookiecutter exclusions do not affect either remaining cookiecutter admission.
No source beyond the frozen candidate universe is introduced.

## E. Canonical terminal partial-block identity

Schema: `SECTION_M_TERMINAL_PARTIAL_BLOCK_IDENTITY_V1`. The field names do
not require ten admissions. Encoding is UTF-8 JSON, sorted keys and separators
`(',', ':')`, JSON integer counts/ranks/seed, boolean `ranking_exhausted`,
ordered arrays, no timestamp, and **no trailing newline in the hashed bytes**.
The exact canonical JSON bytes decode as:

```json
{"block_admitted_count":7,"block_kind":"TERMINAL_PARTIAL","block_number":3,"block_size":7,"bugsinpy_commit":"11c5f1eea954a42132cfd06bf257766a7963e0fd","candidate_universe_sha256":"78208adf610a50542be6dfbd03a9b25960ba0b5cfc80768b08ffe7a4c78f3b8c","cumulative_admitted_count":67,"first_examined_rank":247,"next_cursor_state":"RANKING_EXHAUSTED","ordered_candidate_ranks":[259,369,380,405,431,472,485],"ordered_case_ids":["tqdm::6","PySnooper::3","sanic::3","sanic::5","PySnooper::2","cookiecutter::2","cookiecutter::1"],"ordered_rank_sha256":["851d768874f0eae83c570076a5879a68fd298f4acb7db0f8d2c5b9ecf7192b82","b5b35c934b0627f46485e59542e6f665cf2f01255c378d24d6859d29f563b721","bcf12b72645b11e60debf17279bd64e4a37e7c16a216a71ab4504f6bfa2070f2","ca16c995329f799c4851938f9e8ffe34d3ebcb6bbd45558a3741e4967961d326","d781a79e565be9f24006e19b38061313cb381a350ec5cc5ef5a953096e71a3f2","ecdcc97568ac8115b419a5f463ec2cdd94568de54f9130d87a9105dd7d5fe47b","f20623af65022361a9fb23e8d6480837e784e315d7f546bf27a6a680ac78a0cf"],"previous_admitted_count":60,"previous_cursor_rank":246,"project_cap":4,"ranking_exhausted":true,"sampling_seed":20260922,"schema":"SECTION_M_TERMINAL_PARTIAL_BLOCK_IDENTITY_V1","terminal_exhaustion_adjudication_sha256":"bd3d95f56d9aa6332363216b04b91123ac4c0a284076b26504efb399e1daf059","traversal_terminal_rank":500}
```

**Block-03 identity SHA-256:** `883628cb72d4ddf56fdfd4a28c4b3c0752b429acf1b6c0abe382bbf7d666e780`.

The identity binds the exact adjudication bytes, frozen source/ranking,
previous cursor, all ordered admissions, cap/counts, traversal terminal,
and exhausted next-cursor state.

## F. Independent reproduction and validation

Derivation A uses the frozen numeric rank map, initial-40 membership flags,
Block-01 and Block-02 admission CSVs, and Block-02's final traversal/admission
cursor. It constructs the complete 60-admission counts before traversing all
remaining rows.

Derivation B independently recomputes seed/case digests and their sorted order,
replays the initial 40 and both ten-admission expansions, compares their
frozen membership and historical traversal ledgers, reconstructs cursor 246,
and traverses the complete suffix afresh. Its initial selection represents
15 projects; the conditional diversity pass is not invoked.

`INDEPENDENT_REPRODUCTION_PASS`: exact equality holds for the first examined
rank, all 254 identities, every decision/reason/`project_count_before`, all
seven admitted rows and their order, terminal rank, absence of ranks above
500, post-block counts, and the canonical identity bytes and SHA-256. A separate
per-project capacity bound also equals seven. The supplied informational
case/rank/digest and count cross-checks agree only after independent derivation.

The two complete pre-identity derivation results are compact sorted-key JSON
maps with SHA-256 `34cc8438368ffb67820a222fd82bca965fcf6d02687bbe6d351e665d89339e93` (including full admission and traversal
rows, counts, endpoints, universe identity, and exhaustion proof). Temporary
verification scripts/evidence are outside the repository; no new execution
capability or persistent implementation artifact is introduced.

The committed V4 validator passes, `exclusions.csv` remains 34 unique rows,
and `cases_manifest.csv` remains header-only. Frozen candidate, protocol,
run/specification and historical artifacts are preserved. Existing narrow
repository ledger-validation tests and final byte/mode/scope checks verify
this metadata transaction; they do not establish subject or scientific validation.

The exact narrow repository command was:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest evaluation/downstream_benchmark/tests/test_screening_executor.py::ScreeningExecutorTests::test_committed_pre_eligibility_ledgers_pass_controlling_validation evaluation/downstream_benchmark/tests/test_screening_executor.py::ScreeningExecutorTests::test_pre_eligibility_ledger_mutations_fail_closed -q -p no:cacheprovider
```

Result: **2 passed, 172 subtests passed**. The mutation checks use temporary
copies and do not modify normative repository inputs. Full pytest and Ruff
were not run for this five-file metadata/docs/CSV transaction. Before commit,
all **412** entry tracked files retain their exact SHA-256, mode and item type;
only the five authorized new files are added. `git diff --check` is required
to pass on the complete staged addition before the single local commit.

## G. Exhausted cursor and future authority gates

Terminal examined rank: **500**. Next cursor state: **RANKING_EXHAUSTED**.
State: `RANKED_CANDIDATE_UNIVERSE_EXHAUSTED`.

No Block 04 can be constructed under the current frozen candidate universe,
ranking, prior-skip permanence, and cumulative project cap. If future
screening/materialization leaves insufficient cases, another explicit Human-PI
protocol adjudication would be required. No such adjudication, new universe,
or further expansion is pre-authorized here.

## H. Prospective zero-outcome and zero-execution boundary

The terminal partial rule and this membership are frozen before any Block-03
acquisition, preparation, build, oracle, or eligibility outcome exists. No
Block-03 outcome was inspected or used. The only selection inputs are frozen
rank, metadata eligibility, prior selection, cumulative cap, previous cursor,
and exhaustion. V4 exclusions/readiness prove need only. Build/dependency/tox
availability, environment/oracle complexity, prior blocker knowledge, patch
characteristics, bug/repair difficulty, and desired project mix are excluded.

This transaction performs zero subject clone/fetch, environment preparation,
requirements parsing beyond frozen candidate metadata, recipe construction,
Docker subject build, dependency/setup installation, subject import/test,
oracle, eligibility, pilot/final allocation, ErrPilot/repair, or downstream
model/API execution. No preparation/build evidence artifact or external
Block-03 root is created, and production evidence is not rewritten.
The 67 cumulative admissions are metadata candidates, not eligible cases.

Future Block-03 source acquisition, immutable revision identity resolution,
and preparation require separate explicit Human-PI authorization and identity
gates. Materialization, oracle/eligibility, allocation, and repair each remain
separately gated. This PASS establishes only the terminal partial-block rule,
exact Block-03 membership, and frozen ranking exhaustion.

Publication requires interactive approval of exactly `git push origin main:main`;
the transaction prompt is not push approval. Only one ordinary fast-forward
push may follow that approval, with no force/amend/rebase/merge/tag/manual CI
rerun. Any automatically triggered existing CI is only
`CI_TRIGGERED_REPOSITORY_VERIFICATION` under its frozen side-effect boundary.

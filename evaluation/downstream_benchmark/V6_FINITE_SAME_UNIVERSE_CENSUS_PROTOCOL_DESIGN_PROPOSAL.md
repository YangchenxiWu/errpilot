# V6 finite same-universe census protocol design proposal

Status: `V6_FINITE_SAME_UNIVERSE_CENSUS_PROTOCOL_DESIGN_CANDIDATE_READY_FOR_HUMAN_PI_REVIEW`.
Lifecycle: `CANDIDATE_ONLY`. This document and every associated CSV/JSON are design evidence,
not an activated protocol, frozen membership, canonical current state, or execution authority.
Date: 2026-10-04 (Europe/Budapest). Exact source identities are in
`evidence/v6_protocol_design_v1/predecessor_artifact_sha256.json`.

## 1. Authority and controlled semantic delta

The current Human-PI instruction accepts `HUMAN_PI_POST_ORACLE_CAPACITY_PROTOCOL_DECISION`
and opens `OPEN_V6_FINITE_SAME_UNIVERSE_CENSUS_PROTOCOL_DESIGN` only. Its exact byte digest
and attachment path are recorded in `evidence/v6_protocol_design_v1/entry_verification.json`.
No inference of execution, acceptance, freeze, staging, commit, or publication is permitted.

| Decision | Accepted value | Effect on this proposal |
| --- | --- | --- |
| J1 ORIGINAL_TARGET_STATUS | RETAIN_28 | Four pilot plus 24 final cases remain required. |
| J2 SUCCESSOR_VERSION_REQUIRED | YES | New successor identities; predecessor bytes remain immutable. |
| J3 EXISTING_9_ELIGIBLE_GRANDFATHERED | YES | Reference existing valid evidence; no capacity rerun. |
| J4 EXISTING_12_INELIGIBLE_FINAL_UNDER_UNCHANGED_ORACLE | YES | No rescue or capacity rerun. |
| J5 UNRESOLVED_7_REQUIRED_BEFORE_EXPANSION | NO | Separate governance track. |
| J6 PRIOR_RANKING_CAN_BE_EXTENDED_WITHOUT_UNIVERSE_CHANGE | NO | Original numeric ranks end at 500. |
| J7 PROJECT_CAP_CHANGE | REQUIRED, CANDIDATE_ADMISSION_CAP_AND_PRIOR_CAP_SKIP_TREATMENT_ONLY | Remove cumulative admission cap for this census; final cap stays four. |
| J8 CANDIDATE_UNIVERSE_EXPANSION_REQUIRED | NO | Same source, metadata census, rank ledger, and seed. |
| J9 SUCCESSOR_STOPPING_RULE_REQUIRED | YES | Exhaust all 433 candidates before feasibility assessment. |
| J10 ORACLE_3X3_RULE_REMAINS_UNCHANGED | YES | Exact BUGGY F/F/F and FIXED P/P/P. |
| J11 PILOT_FINAL_STRUCTURE | RETAIN_24_PLUS_4 | Permanent separation and all existing final constraints. |
| J12 SUCCESSOR_ARCHITECTURE | V6_FINITE_SAME_UNIVERSE_CENSUS_WITH_EVIDENCE_CONTINUITY | One complete scientific census, preserving prior evidence. |

Only the successor candidate-admission/reconsideration policy and its finite stopping
rule change. After later acceptance, the new version would supersede
`SCREENING_SPEC_V1.md` sections D/J/M **only insofar as they impose the initial-40 or
cumulative four-admission cap, forward-only expansion cursor, ten-admission block size,
permanent cap-skip treatment, and outcome-triggered expansion for successor membership**.
It would prospectively supersede the no-prior-skip-reconsideration rule in
`SECTION_M_TERMINAL_EXHAUSTION_ADJUDICATION_V1.md` for exactly the 433 cap skips.
It would not retroactively invalidate those decisions or change any historical row.
All other predecessor scientific, environment, protection, and downstream run requirements
remain controlling by reference. An unlisted conflict blocks the affected later phase.

`PROTOCOL.md` / `RUN_SPEC_V1.md` final-sampling and scientific requirements stay intact.
Proposed successor protocol/run-spec/screening identities must explicitly incorporate their
exact predecessor digests and this narrow change record before activation. The current design
is not an amendment to those canonical files. The model/role heading in the current design
instruction does not amend the frozen downstream repair-agent identity in RUN_SPEC section E.

## 2. Entry identity and predecessor reconstruction

Verified repository `/Users/wuyangchenxi/errpilot`, branch `main`, local HEAD and LIVE
`origin/main`: `26a9264105f303dc0101f74c9315c41ab1c9e265`; entry worktree/index clean.
No repository AGENTS.md, `.airos/current_state.md`, or `.airos/contracts/` exists.
The pasted global rules and current instruction control this design.

- BugsInPy commit: `11c5f1eea954a42132cfd06bf257766a7963e0fd`.
- BugsInPy tree: `d00ce0495ba73abe50317599f48bced3c9afe4b3`; detached, clean local checkout.
- Candidate-universe SHA-256: `78208adf610a50542be6dfbd03a9b25960ba0b5cfc80768b08ffe7a4c78f3b8c`.
- Seed: `20260922`; original rank digest is SHA-256 of UTF-8
  `20260922|candidate|<project>::<bug_id>`; ascending digest then canonical ID.
- 501 census rows; 500 metadata-eligible unique ranks 1..500; unranked `keras::12`
  remains the metadata exclusion and is outside successor membership.
- Historical admissions: initial 40 + 10 + 10 + 7 = 67.
- Those 67 partition into 39 accepted pre-eligibility exclusions and 28 screened cases.
- Those 28 partition into nine eligible, 12 scientific-ineligible, seven infrastructure-unresolved.
- Confirmed eligible capacity nine; even resolving all seven favorably permits only 16,
  below 28. These counts establish need, not candidate selection inputs.

The historical pre-eligibility V5 descriptor intentionally retains its earlier zero-oracle
and candidate-lifecycle fields. Its committed lifecycle closure supplies the effective
pre-eligibility freeze. The later external V5 screening evidence supplies the current
9/12/7 outcomes. No new canonical post-oracle descriptor is invented here. The current
instruction explicitly supplies their evidence-continuity authority. `RUN_REPORT.md` from
that screening transaction reports BLOCKED because infrastructure prevented valid screening
for seven cases; it does not invalidate the other 21 mechanically classified cases.

The old validator passes static V4/V5 reconciliation. Its
`--verify-production-evidence` mode rejects the now-existing oracle evidence because it
also enforces a historical zero-oracle boundary. This rejection is recorded, not repaired
or described as current post-oracle validation. Independent read-only hashing verifies
the 1,737 original screening evidence files and 143 governed external inputs. A future
successor checker must bind both time-specific predecessor layers without changing them.

No V6 successor owner or later allocation was found in the repository, the controlling
manifest/checkpoints/audit, or the external governance top-level namespace. This is the
surveyed local boundary, not a claim about unknown files elsewhere on the computer.

## 3. Exact reconsideration inventory and lineage

`v6_reconsideration_pool_proposal.csv` contains exactly 433 rows in original rank order.
Each row binds canonical ID, project, original numeric rank and digest, universe digest,
source commit/tree, seed, predecessor disposition, source-file digest, record ordinal,
row key, and lineage method. It also binds the rule/implementation for replayed initial skips.
The CSV proposes membership; no row is an admission, preparation attempt, or outcome.

Membership is the conjunction of original ranked-universe membership, never admitted,
terminal predecessor disposition exactly `SKIP_PROJECT_CAP`, no accepted exclusion, no
screened membership, and unique identity. No case is manually added or removed.

| Frozen predecessor segment | Cap skips | Evidence |
| --- | ---: | --- |
| Initial traversal ranks 1..71 | 31 | Unique replay of SCREENING_SPEC section D, frozen universe flags/order, and frozen builder |
| Block 01 ranks 72..102 | 21 | Literal traversal decision rows |
| Block 02 ranks 103..246 | 134 | Literal traversal decision rows |
| Block 03 ranks 247..500 | 247 | Literal exhaustive terminal traversal rows |
| Total | 433 | Complete 500 = 67 + 433 partition |

The initial universe CSV has no literal `decision` column. Its 31 initial skips are
**derived predecessor dispositions**, not invented historical ledger rows: replay yields
the exact stored 40 admissions, all selection ordinals, cursor 71, and 15 projects, so the
conditional diversity pass was not used. Every excluded initial row was capped at four
at its unique visit. The proposal labels this method distinctly from literal traversal
rows. If Human PI requires literal historical decision rows for every case, a separately
accepted reconstruction artifact is needed before successor membership persistence;
the original universe is never edited to add that column.

Rank range is 10..500 with gaps at admissions; successor `proposal_order` 1..433 is
an inventory ordinal, never a replacement scientific rank or rank beyond 500.

| Project | Proposed census count |
| --- | ---: |
| ansible | 14 |
| black | 19 |
| fastapi | 12 |
| httpie | 1 |
| keras | 40 |
| luigi | 29 |
| matplotlib | 26 |
| pandas | 165 |
| sanic | 1 |
| scrapy | 36 |
| spacy | 6 |
| thefuck | 28 |
| tornado | 12 |
| tqdm | 5 |
| youtube-dl | 39 |
| Total | 433 |

Pool intersects prior admissions, exclusions, and screened population in zero cases.
PySnooper and cookiecutter contribute zero reconsideration rows because their ranked
cases were already admitted. Concentration does not authorize a new preparation cap.

## 4. Census and operational scheduling

All 433 rows would belong to the accepted, frozen successor census before any successor
outcome. Every member receives an accountable traversal through the preparation pipeline.
No eligible-count threshold, cost forecast, expected build success, project mix, or early
outcome can remove a member or determine whether later census members exist.

Proposed default: a single logical census, ascending original rank, without prescribed
operational batches. Governance packaging is D2; optional batch boundaries are D3. If
batches are accepted later, define them by exact inventory ordinal intervals and hashes
before the first successor outcome, partition all 433 once, and freeze every boundary
simultaneously. Batch completion never creates, cancels, or changes later membership.
Multiple governance blocks are permissible only if their entire membership is already
frozen as the same complete census. Opening a later phase still requires its own authority.

Preparation for the whole census closes before freezing the environment-ready population;
then screening opens for that frozen population. No stop at 28 eligible, no pass-until-full,
no new rank 501, and no release of historical candidate-cap slots is needed or permitted.

## 5. Preparation pipeline and orthogonal dispositions

Proposed per-candidate flow, effective only under later exact phase authority:
`PROPOSED_V6_CANDIDATE` -> accepted/frozen/persisted census member -> authorized preparation
planning -> `PREPARATION_ATTEMPT` -> `ENVIRONMENT_READY` or a recorded exclusion proposal,
infrastructure-unresolved state, invalid-evidence state, or interruption.
Preparation planning, source acquisition, and real materialization are separately gated.
No source, dependency, runtime, build recipe, or oracle plan for a new subject is created here.

Preserve the mechanically declared BugsInPy fixed-version test injection into the BUGGY
screening workspace: only hash-pinned declared test bytes, with raw/effective identities
and injection recorded. Never copy non-test fixed repair content. Preserve the distinction
between this screening representation and RUN_SPEC section J's full downstream protected-path
requirements; a declared-file heuristic cannot replace that later gate. Case-bound tox/setup
compatibility whitelists remain case-bound; an existing bridge is not blanket authority to
accept an arbitrary new command or setup action for the 433 candidates.

Carry forward inert metadata parsing and full revision resolution; frozen source URL/object
mapping; official-fix leakage separation; strict requirements normalization; proven self-reference
removal only; ordered setup representation; dependency-only input; immutable exact Python patch
and linux/amd64 identity; source-independent versus revision-specific environment modes;
source snapshots and protected-test manifests; bounded symlink handling and explicit gitlink
sidecar transport when its applicable predecessor bridge is needed. Never assume an initial-40
or Block-03 row-bound capability accepts a new candidate. A future implementation bridge
requires separate authority and revalidation of the inherited rules.

Preserve exact normalization and oracle command semantics. No new dependency pin, package
membership, Python/platform substitution, setup reordering, pytest repair, omitted test,
manual command replacement, or environment rescue is an automatic fallback. Build network
requires exact separate authority and recorded artifacts; screening network remains NONE.

Use separate fields for phase, technical status, canonical reason(s), subreason(s), evidence
validity, attempt consumption, retry policy, and Human-PI adjudication. A technical failure
does not by itself create an accepted permanent exclusion or a scientific result.

| Observation | Existing reason layer | Proposed disposition handling |
| --- | --- | --- |
| Changed/missing/invalid metadata | METADATA_INCOMPLETE or PROJECT_STATUS_NOT_OK, retaining original granular metadata code | Block identity contradiction; no silent change to frozen membership |
| Source acquisition, full-object resolution, or export failure | SOURCE_ACQUISITION_FAILURE, with precise subreason | Preserve attempt/evidence; proposed exclusion or infrastructure-unresolved pending adjudication |
| Exact runtime/environment unsupported | UNSUPPORTED_ENVIRONMENT | Preserve blocker and exclusion proposal; no runtime substitution |
| Dependency installation or governed setup/build failure | DEPENDENCY_SETUP_FAILURE | BUILD_FAILED remains technical infrastructure evidence; exclusion requires explicit adjudication |
| Invalid/unrepresentable oracle command | ORACLE_COMMAND_INVALID | No command editing or oracle dispatch; preserve exact metadata and parser evidence |
| Missing protected manifest | PROTECTED_MANIFEST_UNRESOLVED | Block affected candidate; never omit protected paths |
| Required external service, GUI, or outside scope | EXTERNAL_SERVICE_REQUIRED / GUI_INTERACTION_REQUIRED / OUTSIDE_ERRPILOT_SCOPE | Preserve specific canonical reason and evidence |
| Preparation runner/storage/container infrastructure failure | OTHER_INFRASTRUCTURE_FAILURE plus exact phase/subreason | Infrastructure-unresolved; not a scientific FAIL |
| Input/runtime/action gate rejection | Existing BLOCKED_INPUT_IDENTITY / BLOCKED_RUNTIME_IDENTITY / BLOCKED_UNSUPPORTED_ACTION technical status | Preserve distinct status; reason mapping requires evidenced cause, never automatic DEPENDENCY_SETUP_FAILURE |
| Interruption or incomplete attempt | INTERRUPTED / incomplete technical status | Preserve partial evidence and pending/consumed slots; no fabricated completion |

The canonical SCREENING_SPEC reason vocabulary also retains BUGGY_NOT_3_OF_3_FAIL,
FIXED_NOT_3_OF_3_PASS, and NONDETERMINISTIC_ORACLE for valid scientific evidence. Exact
schema fields and preparation mappings are D4/D5 proposal decisions, not new canonical labels.

Every later attempt has a new immutable namespace and authority record. A failed build is
attempted once; preserve all input/output hashes, logs, consumed-attempt fact, and revision
bindings. A later success cannot overwrite the earlier failure. A retry requires a separate
versioned Human-PI authority, exact allowed cases and replacement/supersession relation;
it is not part of the base census authority. Resumption of an interrupted campaign can
dispatch only demonstrably never-consumed pending work under valid separate continuation
authority; it cannot replay consumed work or erase the interruption.

Preparation completion requires all 433 candidate rows accounted for, including each blocked,
excluded, or unresolved row. Accepted exclusions and accepted held-unresolved dispositions
remain distinct. Unadjudicated or unaccounted rows block closure. A Human-PI closure can
retain infrastructure cases unresolved without authorizing retries. Environment-ready freeze
contains only candidates with complete accepted immutable source, dependency, build, oracle,
and protection identities. All census rows remain visible in the reconciliation denominator.

## 6. Oracle-screening contract

Each environment-ready successor case has exactly six slots, in this order:
BUGGY 1, BUGGY 2, BUGGY 3, FIXED 1, FIXED 2, FIXED 3. Use the same preregistered
ordered-command oracle for both variants. Every trial starts with restored source and fresh
ephemeral state; only read-only content-addressed dependencies can be shared.

Preserve SCREENING_RUNTIME's 300-second subcommand and 900-second whole-trial limits,
including startup/teardown; clocks do not reset. Preserve direct argv, subject-root cwd,
immutable environment identity, linux/amd64, network NONE, protected-manifest checks,
command membership/order and exact raw stdout/stderr hashes, timestamps, exit codes,
expected-test-observed evidence where required, trial identity and case classification.

A composite oracle trial is the entire frozen ordered list of N recognized substantive
commands, with N >= 1. Preserve exact script and command bytes, literal argv and order;
never sort, deduplicate, concatenate into a shell, or count N commands as N repetitions.
Every command continues after a valid nonzero exit in the same fresh trial workspace.
TRIAL_PASS requires all N valid commands to exit zero; TRIAL_FAIL requires all N validly
completed and at least one nonzero exit. Missing/invalid/protected-integrity or infrastructure
evidence cannot produce a scientific TRIAL_FAIL. This carries ORACLE_REPRESENTATION_V1
forward unchanged.

Only six valid scientific records with BUGGY = FAIL/FAIL/FAIL and FIXED = PASS/PASS/PASS
can be ELIGIBLE. No majority vote, fourth trial, desirable-outcome retry, or early stop after
a scientific result. All scheduled slots remain accounted for. Infrastructure may stop a
trial's command sequence; it cannot turn a missing executable, timeout, or Docker failure
into scientific FAIL. An externally interrupted campaign preserves missing slots honestly.

Carry forward the exact executor distinction between ELIGIBLE,
INELIGIBLE_REPRODUCIBILITY_OUTCOME, INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY,
INTERRUPTED_NOT_ELIGIBILITY, INCOMPLETE_NOT_ELIGIBILITY, and CASE_INVALIDATED.
The broad RUN_SPEC phrase that invalid/missing execution makes a case ineligible means
it cannot enter the eligible pool; it does not collapse infrastructure into scientific failure.
Six valid nonconforming scientific trials are final scientific-ineligible under the unchanged
rules. Invalid, incomplete, interrupted, and infrastructure evidence remains separately
unresolved/non-eligible. Exact reasons and orthogonal flags are retained.

Screening completion requires a complete scheduled-slot reconciliation for the frozen ready
population, preserved consumed-slot history, and explicit Human-PI closure of any unresolved
or invalid evidence. Missing work cannot be labeled valid scientific completion. Such closure
can retain unresolved cases outside eligibility; it cannot generate results or grant reruns.
No V5 executor or authority token is reused as a V6 execution authorization.

## 7. V5 -> V6 evidence bridge

`v6_predecessor_evidence_bridge_proposal.json` binds the exact committed pre-eligibility
layer, external oracle layer, current Human-PI authority, and all five population classes.

| Class | Count | Successor treatment |
| --- | ---: | --- |
| Existing eligible | 9 | Grandfather the accepted original evidence; no rerun for expansion |
| Existing scientific-ineligible | 12 | Final under unchanged oracle/environment semantics; no rescue |
| Existing infrastructure-unresolved | 7 | Outside V6 execution; separate versioned repair/rerun track |
| Accepted pre-eligibility exclusions | 39 | Preserve all reasons and authority; never reopen |
| Never-admitted cap skips | 433 | Sole prospective successor reconsideration census |

The 500 ranked rows partition as 9 + 12 + 7 + 39 + 433. The extra original unranked
metadata exclusion is outside that partition and stays excluded. Each admitted case has a
rank/universe/admission binding; screened cases additionally bind their original outcome
file and original immutable checkpoint; exclusion cases bind their exact V5 ledger row and
evidence-reference field. The cap-skip class references the exact proposed CSV and its
distinct lineage methods. The bridge is reference metadata, not a clone of raw evidence.
It does not manufacture new execution provenance or replace existing results.

Existing eligible evidence may contribute only through a later accepted/frozen/persisted/
committed successor bridge that references the original artifacts. Their raw evidence can
remain in the governed external store, hash-bound; it need not be copied into Git or rerun.
No absent canonical outcome writer or cases-manifest population is implied by this design.

## 8. Future integration of the unresolved seven

Exact set: matplotlib::17, matplotlib::11, matplotlib::29, matplotlib::21,
PySnooper::1, PySnooper::3, PySnooper::2. Their 42 historical slots were consumed with
infrastructure errors. They receive no V6 preparation/oracle authority from census membership.

Proposed D6 cutoff: the allocation-opening gate is an immutable Human-PI accepted gate
record naming a commit and exact combined eligible-pool snapshot digest. Before that gate
opens, any included repair/rerun outcome must already be Human-PI accepted, frozen,
persisted, and committed, with a versioned authority identifying the seven-track case,
original consumed execution and checkpoint hashes, changed environment/plan identities,
new attempt ID, exact superseded classification, and scope of the supersession. Original
records remain accessible and unmodified. Only one accepted effective outcome per case is
allowed; ambiguity blocks integration.

No scientific-ineligible predecessor case is included in this repair track. A valid new
eligible outcome requires a full six-trial sequence under the same scientific criterion,
plus accepted immutable environment and evidence identities. No old infrastructure slot is
silently reused as scientific evidence. Exact rerun replacement mechanics require their own
versioned decision, not this design's approval.

The combined pool before cutoff consists of the grandfathered nine, accepted eligible V6
outcomes, and only qualifying seven-track outcomes. The cutoff uses committed gate identities,
not an operator-selected date after seeing allocation results. Outcomes accepted later remain
outside that allocation, even if a slot is inconvenient or allocation is unsuccessful. Reopening
the cutoff requires a new protocol adjudication and new allocation version, never silent
substitution. The seven need not finish before census expansion or allocation opens. If none
qualify by the gate, none contribute. This exact cutoff is a recommendation requiring D6
acceptance; predecessor files require frozen eligible inputs but do not uniquely specify the
four-state post-oracle integration cutoff.

## 9. Pilot/final allocation boundary and concentration firewall

Carry forward PROTOCOL Units/Frozen Sampling and RUN_SPEC sections L/M/P/Q unchanged:
exactly four pilot cases, permanently excluded from the final eligible input and final 24;
pilot outcomes cannot affect eligibility, selection, replacement, or frozen inputs; 24 final
eligible non-pilot cases; at least six projects; at most four **final** cases per project.
No combined pilot-plus-final cap or pilot-project cap is invented.

For the eventual final non-pilot snapshot, candidate keys are source_project,
bugsinpy_bug_id, case_id, canonical UTF-8 and unique. Rank final candidates by lowercase
SHA-256 of `20260922|final|<source_project>|<bugsinpy_bug_id>|<case_id>`, then all three
key fields. Accept in that order unless four final cases already represent that project,
until 24; fail closed if impossible. Freeze snapshot bytes/digest before selection.
The robustness six use `20260922|robustness|<case_id>`, digest then case_id. Paired condition
ordering uses low bit of SHA-256's first byte for
`20260922|order|<case_id>|<repetition_index>`: zero RAW first, one ERRPILOT first.
These later algorithms are described, not executed in this transaction.

The predecessor does **not** give a deterministic algorithm choosing which four eligible
cases become pilot, or uniquely fix how pilot reservation interacts with final feasibility.
D7 therefore requires Human PI to supply a prospective outcome-independent pilot rule,
canonical inputs, tie-breaks, reservation order and failure behavior before any selection.
Do not infer a `|pilot|` hash namespace, take the first four ranks, or choose leftovers.
Carry forward known permanent pilot exclusions and final rules exactly.

At full census closure, capacity assessment must distinguish 28 total eligible from valid
allocation. Given an accepted pilot rule and its reservation set P, require |P|=4; freeze
E minus P; let n_j be its eligible counts by project. Feasibility requires
sum_j min(4,n_j) >= 24 and at least six represented projects, plus every other controlling
identity/diversity gate. This is a count criterion, not an allocation performed here. Before
D7 is resolved, report ALLOCATION_RULE_UNRESOLVED rather than assuming feasible pilots.
The current nine span only youtube-dl (4), fastapi (4), and httpie (1); this describes
predecessor evidence, not future final choices or expected successor success.

All 433 may participate even though pandas supplies 165. No cost-saving preparation cap,
expected-success prioritization, or discretionary project quota may reduce the census.
Final cap four and minimum six projects remain the allocation firewall. Downstream pilot
execution, final benchmark execution, RAW, ERRPILOT, robustness and any claim require
separate later authority and all original pre-run gates.

## 10. Proposed identities, ledger, and finite state machine

Proposed identifiers are `EP-DBP-6-CAPACITY`, `EP-DBRS-6-CAPACITY`,
`EP-BIPS-6-CENSUS`, `V6_RECONSIDERATION_POOL_V1`,
`V6_PREDECESSOR_EVIDENCE_BRIDGE_V1`, and `V6_CAPACITY_CURRENT_STATE_V1`.
Exact names and filenames are D1, not active canonical identifiers. The JSON contract
defines the proposed successor run-spec delta, ledger fields, decision surface, and gates.
No canonical V6_CURRENT_STATE file is persisted here.

Proposed future state storage is append-only events plus derived snapshots: case identity,
original rank/universe/source/seed, cohort and original predecessor references; each event's
ID, sequence, previous-event hash, phase/status, authority digest/commit, technical reason,
evidence references, consumed slots, retry policy and explicit supersession; snapshots bind
all input/event hashes, effective state, count reconciliation, lifecycle and separate phase
authorization flags. Unknown outcome/environment fields are null, never fabricated. Event
and snapshot schema D5 needs Human-PI acceptance before persistence. None of these planned
future state events is issued by this proposal.

| From -> to | Required distinct Human-PI gate | Evidence prerequisite |
| --- | --- | --- |
| DESIGN_PROPOSED -> HUMAN_PI_ACCEPTED | HUMAN_PI_ACCEPT_V6_DESIGN | Exact design hashes and resolved required design choices |
| HUMAN_PI_ACCEPTED -> FROZEN | HUMAN_PI_FREEZE_V6_PROTOCOL | Exact successor versions, semantic delta and membership/batch hashes |
| FROZEN -> CENSUS_MEMBERSHIP_PERSISTED | HUMAN_PI_PERSIST_V6_CENSUS | Exact 433 rows, lineage and predecessor bridge; no executed subjects |
| CENSUS_MEMBERSHIP_PERSISTED -> PREPARATION_OPEN | HUMAN_PI_OPEN_V6_PREPARATION | Committed authority/membership and revalidated implementation; exact acquisition/preparation/materialization sub-authorities |
| PREPARATION_OPEN -> PREPARATION_COMPLETE | HUMAN_PI_ACCEPT_V6_PREPARATION_CLOSURE | All 433 accounted, no hidden retries, accepted exclusions/held-unresolved evidence |
| PREPARATION_COMPLETE -> ENVIRONMENT_READY_POPULATION_FROZEN | HUMAN_PI_FREEZE_V6_READY_POPULATION | Immutable ready-case identities and complete census reconciliation |
| ENVIRONMENT_READY_POPULATION_FROZEN -> ORACLE_SCREENING_OPEN | HUMAN_PI_AUTHORIZE_V6_3X3_SCREENING | Exact ready population, six-slot plans, implementation/authority commit and separate execution permission |
| ORACLE_SCREENING_OPEN -> ORACLE_SCREENING_COMPLETE | HUMAN_PI_ACCEPT_V6_SCREENING_CLOSURE | Every planned slot accounted; preserved valid/infrastructure/interrupted/invalid distinctions |
| ORACLE_SCREENING_COMPLETE -> ELIGIBLE_POOL_FROZEN | HUMAN_PI_FREEZE_COMBINED_ELIGIBLE_POOL | Complete census closure, accepted effective outcomes and grandfather bridge; D6 cutoff eligibility |
| ELIGIBLE_POOL_FROZEN -> PILOT_FINAL_ALLOCATION_OPEN | HUMAN_PI_AUTHORIZE_PILOT_FINAL_ALLOCATION | D7 resolved, non-discretionary cutoff commit/snapshot digest, capacity/diversity gates |
| PILOT_FINAL_ALLOCATION_OPEN -> ALLOCATION_COMPLETE | HUMAN_PI_ACCEPT_ALLOCATION | Exact four pilot/24 final, permanent disjointness, final cap/diversity and deterministic outputs |

Every open phase can enter an orthogonal BLOCKED/INTERRUPTED hold, retaining its prior
state and immutable evidence. A separate exact continuation gate can restore that phase
only with valid identities and pending-work accounting; it cannot grant a retry or skip
members. The base state progression and finite per-candidate schedule do not loop retries.
FROZEN and persistence do not grant preparation; ready freeze does not grant screening;
pool freeze does not grant selection; ALLOCATION_COMPLETE grants no repair execution.
Commit/publication are separate lifecycle gates whenever required, never automatic state
transitions. Every authority is data bound to the exact approved phase, not token presence.

## 11. Finite completion and exhaustion

The census is exhausted only when all 433 candidates have governed preparation dispositions
and every ready-case screening slot is accounted for under the accepted pipeline, including
explicit closure of unresolved/invalid states. Do not call pending/unaccounted work exhaustion.
Build failures do not require oracle dispatch; accepted non-ready exclusions remain counted
as census members. Retained infrastructure-unresolved cases remain outside eligibility.

After complete closure, freeze only accepted effective eligible evidence at the accepted
cutoff and assess feasibility under D7 and final cap/diversity. Proposed report statuses:
`V6_CENSUS_COMPLETE_ALLOCATION_AUTHORITY_REQUIRED` if feasible;
`V6_CENSUS_EXHAUSTED_INSUFFICIENT_ELIGIBLE_CAPACITY` if capacity is inadequate;
`V6_CENSUS_EXHAUSTED_PROJECT_DIVERSITY_INFEASIBLE` if final constraints cannot be met;
`V6_CENSUS_COMPLETE_ALLOCATION_RULE_UNRESOLVED` if D7 remains open;
`V6_CENSUS_CLOSURE_BLOCKED` for unaccounted work or unaccepted evidence.
Exact names/precedence are D8; none is a current execution status.

Successful feasibility returns to Human PI for allocation authority. An insufficient or
infeasible complete census fails closed. No automatic snapshot expansion, rank beyond 500,
seed change, scientific rescue, oracle weakening, target reduction, project-cap change,
new successor, or unresolved-seven rerun is permitted. All require a new exact versioned
Human-PI protocol adjudication.

## 12. D1–D8 decision surface

The adopted scientific architecture, full membership obligation, unchanged 3x3, 24+4,
final cap four, evidence continuity, and no universe expansion are uniquely resolved by
the accepted J decisions. The **remaining exact choices** below are not uniquely fixed.

| Decision | Classification | Reviewable proposal / unresolved part |
| --- | --- | --- |
| D1 exact artifact/schema identifiers | REQUIRES_HUMAN_PI_DECISION | Accept or rename the exact identifiers/filenames proposed in section 10 and JSON. |
| D2 census governance packaging | REQUIRES_HUMAN_PI_DECISION | Recommend one logical census with optional operational batching; complete 433 membership is already mandatory under either packaging. |
| D3 operational batch boundaries | REQUIRES_HUMAN_PI_DECISION | Recommend no prescribed batches; if introduced, freeze a complete disjoint ordinal partition before any outcome. |
| D4 preparation failure vocabulary | REQUIRES_HUMAN_PI_DECISION | Retain existing canonical reason/technical layers; accept exact orthogonal mapping, adjudication and held-unresolved closure semantics. |
| D5 V6 current-state ledger | REQUIRES_HUMAN_PI_DECISION | Accept append-only hashed events and derived snapshots; no current-state artifact is activated here. |
| D6 unresolved-seven cutoff | REQUIRES_HUMAN_PI_DECISION | Accept four-state eligibility and immutable allocation-opening commit/snapshot cutoff in section 8. |
| D7 pilot/final semantics | REQUIRES_HUMAN_PI_DECISION | Known final rules retained; missing pilot-selection/reservation algorithm must be supplied prospectively. |
| D8 exhaustion statuses | REQUIRES_HUMAN_PI_DECISION | Accept precise proposed status names and closure/capacity/diversity/rule-unresolved precedence. |

These decisions do not prevent a finite design candidate from being reviewed. Unresolved
required choices prevent acceptance/freeze or the specific dependent later gate. No agent
default supplies missing Human-PI decisions. No additional user response is required to
finish this authorized design transaction.

## 13. Design validation, evidence and firewall

The evidence directory contains entry reconstruction, controlling hashes, a read-only proposal
checker, exact validation results, and the A–T Run Report. The checker verifies membership,
rank/seed/source identities, 67/39/28 and 9/12/7 partitions, unique lineage, bridge equality,
scientific invariants, state/gate coverage, decisions, and original-file preservation.
Mutation probes operate only on in-memory proposal copies and must reject drift. No
production executor is introduced. Actual pass/fail counts and exact commands appear in
`validation_results.json` and `RUN_REPORT.md`; those are design evidence, not subject tests.

All current transaction firewall fields in the contract are NO, including V6 activation/
membership freeze, subject materialization/environment/image work, oracle execution or
consumption, pytest repair, seven reruns, pilot/final selection, predecessor rewriting,
exclusion reopening, scientific rescue, staging, commit and push. Historical 168 consumed
slots are preserved facts; new oracle repetitions consumed by this transaction = zero.

`HUMAN_PI_ACCEPTED = NO`, `FROZEN = NO`, `PERSISTED = NO`, `COMMITTED = NO`,
`REMOTE_PUBLISHED = NO` describe the successor protocol/membership lifecycle. Proposal
files are saved locally for review; that does not constitute canonical successor persistence.
Next gate: `HUMAN_PI_REVIEW_OF_V6_FINITE_SAME_UNIVERSE_CENSUS_PROTOCOL_DESIGN`.
No implementation authority is granted. Stop after the Run Report.

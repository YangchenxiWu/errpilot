# Pre-eligibility exclusions-ledger state V5

Status: `PRE_ELIGIBILITY_EXCLUSIONS_LEDGER_STATE_V5_PERSISTED_CANDIDATE`.

The Human PI adopted `HUMAN_PI_BLOCK_03_PERSISTENCE_ARCHITECTURE_DECISION_V1`,
accepted `BLOCK_03_MATERIALIZATION_OUTCOME_ADJUDICATION_V1`, and authorized
`BLOCK_03_MATERIALIZATION_OUTCOME_PERSISTENCE_V5`. The current transaction
instruction has SHA-256 `033b84417d53fbc0f8320b2d483e86e10672b6a7531df26f928ea8254a5c6a41`. This persists accepted decisions;
it grants no execution, freeze, commit, or publication authority.

The canonical versioned current-state descriptor is `pre_eligibility_current_state_v5.json`; SHA-256:
`6a11d9ac79cb77fbe5e7743799eec3a506b2eaa0ac27a4c36fd850fe124851fd`. Its authority, predecessor, exact delta, evidence identities,
capacity, scientific state, and candidate lifecycle are machine validated by
`screening/validate_pre_eligibility_state_v5.py`. The controlling persistence record is `BLOCK_03_MATERIALIZATION_OUTCOME_PERSISTENCE_V5.md`.

## Frozen predecessor and current successor

V4 = HISTORICAL_FROZEN_PREDECESSOR. Freeze commit: `fe60347faf7e6f85ee2159ea80e0d0d53be82a9e`.
V4 exclusions = 34; V4 split = 9 / 23 / 2, ordered as
UNSUPPORTED_ENVIRONMENT / DEPENDENCY_SETUP_FAILURE / ORACLE_COMMAND_INVALID.
The original `exclusions.csv`, V4 state document, V4 validator, and frozen
Block-03 preparation bindings remain unchanged at their exact predecessor hashes.
`exclusions.csv` is predecessor-bound storage, not the V5 aggregate.

V5 = CURRENT_PRE_ELIGIBILITY_SUCCESSOR.
CURRENT CANONICAL PRE-ELIGIBILITY STATE = V5.
V5 accepted exclusions = 39; V5 split = 11 / 26 / 2.
`exclusions_v5.csv` contains the original V4 header and all 34 historical rows
byte-for-byte, followed by exactly five additions in frozen Block-03 orders
1, 3, 4, 6, 7. No historical case or reason is removed or changed.

V5 supersedes V4 AS CURRENT STATE ONLY.
V5 does NOT invalidate, rewrite, or mutate V4 historical authority.
V4 is validated as V4; the successor relation V4 -> V5 and V5 are validated
separately. V4's expected rejection of a synthetic 39-case union remains correct.

## Accepted exact delta and permanent NON_RETRY

| Case | Final exclusion reason | Decision authority | Retry policy |
| --- | --- | --- | --- |
| tqdm::6 | DEPENDENCY_SETUP_FAILURE | HUMAN_PI_ACCEPTED | PERMANENT_NON_RETRY |
| sanic::3 | UNSUPPORTED_ENVIRONMENT | HUMAN_PI_ACCEPTED | PERMANENT_NON_RETRY |
| sanic::5 | UNSUPPORTED_ENVIRONMENT | HUMAN_PI_ACCEPTED | PERMANENT_NON_RETRY |
| cookiecutter::2 | DEPENDENCY_SETUP_FAILURE | HUMAN_PI_ACCEPTED | PERMANENT_NON_RETRY |
| cookiecutter::1 | DEPENDENCY_SETUP_FAILURE | HUMAN_PI_ACCEPTED | PERMANENT_NON_RETRY |

`expansion_block_03_build_failure_adjudication_v1.csv` extends the historical disposition schema with explicit
`first_pass_attempt_consumed = YES`, `permanent_non_retry = YES`, and
`decision_authority = HUMAN_PI_ACCEPTED`. Its `human_pi_adjudication` retains the
established `ACCEPTED_EXCLUSION` representation; `retry_policy` records
`PERMANENT_NON_RETRY`. All five required BUGGY/FIXED pairs failed at dependency
installation. The failure-family/group columns describe the observed blockers;
the exclusion reasons and NON_RETRY policy come from the Human PI.

Attempt consumption is a first-pass fact. Permanent NON_RETRY is an independent,
explicit Human-PI decision; it is not mechanically inferred from consumed attempts.

## First pass, capacity, and scientific state

`evidence/block_03_materialization_outcome_v5/first_pass_evidence.json` is a hash-bound read-only extract of preserved external first-pass
evidence, not a new attempt or a replacement for the raw files. It binds all four
source summary/ledger identities and each of 14 attempt/build-log pairs. Each
materialized identity retains its final-image, environment, and distribution
manifest identities. Validation can optionally re-read the original evidence;
it never invokes Docker or an oracle.

```text
Block-03 cases = 7
identities = 14
attempts consumed = 14 / 14
MATERIALIZED = 4
BUILD_FAILED = 10
ENTRY_ENVIRONMENT_READY = 26
NEW_COMPLETE_MATERIALIZED_CASES = PySnooper::3; PySnooper::2
NEW_ENVIRONMENT_READY = 2
RESULTING_ENVIRONMENT_READY = 28
REQUIRED_SLOTS = 28
CAPACITY_REQUIREMENT_MET = YES
cumulative metadata admissions = 67
accepted exclusions = 39
UNSUPPORTED_ENVIRONMENT = 11
DEPENDENCY_SETUP_FAILURE = 26
ORACLE_COMMAND_INVALID = 2
oracle outcomes = 0
cases_manifest.csv = header-only
eligibility established = NO
```

The entry capacity of 26 is bound to the frozen V4 predecessor and accepted
Block-02 capacity record (19 + 4 + 3). Complete PySnooper::3 and PySnooper::2
BUGGY/FIXED pairs add two; 26 + 2 = 28. Required slots remain 28. No pilot or
final allocation is made. MATERIALIZED != ELIGIBLE. Capacity satisfaction does
not establish eligibility or guarantee survival through any future oracle gate.

## Future consumers and lifecycle

Every later oracle-screening/current-state transaction must bind the V5
current pre-eligibility descriptor, its artifact hashes, this versioned state
document, the V5 validator, and the controlling V5 persistence record. A pass
from the frozen V4-only validator establishes historical predecessor coherence
only; it cannot establish current V5 successor coherence. No existing oracle,
materializer, or preparation execution semantics are changed by this registration.

```text
HUMAN_PI_ACCEPTED = YES
PERSISTED = YES
FROZEN = NO
COMMITTED = NO
REMOTE_PUBLISHED = NO
NEXT_GATE = HUMAN_PI_REVIEW_OF_BLOCK_03_MATERIALIZATION_OUTCOME_PERSISTENCE_V5
ORACLE_SCREENING_NOT_AUTHORIZED
```

A separate Human-PI lifecycle closure is required. The descriptor is an accepted,
persisted candidate and must not be treated as frozen, committed, or published.

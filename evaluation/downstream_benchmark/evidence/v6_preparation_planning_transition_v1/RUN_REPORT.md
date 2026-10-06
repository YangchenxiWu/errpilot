# V6 Preparation Planning Transition Candidate V1 — Run Report

STATUS = V6_PREPARATION_PLANNING_TRANSITION_CANDIDATE_READY_FOR_HUMAN_PI_REVIEW

2026-10-06, Europe/Budapest. This status requires the saved audit and final
preservation/inventory checks to pass. It describes a review candidate only.
Both entry and closing live-ref queries observed the required exact main commit.

1. Task summary / A. Entry and current state

The direct Human-PI instruction HUMAN_PI_AUTHORIZE_V6_PREPARATION_PLANNING
authorizes construction of exactly one transition candidate from
CENSUS_MEMBERSHIP_ACTIVATED to PREPARATION_PLANNING_AUTHORIZED. It explicitly
prohibits preparation execution and canonical installation. The attached request
is preserved byte-for-byte as human_pi_request.txt, SHA-256
c0ed2a16ad6965110612151abe201cd55edef3937d90d35179a600a0a74e362a.
The source attachment path and construction-only authorization are in
entry_verification.json. HUMAN_PI_ACCEPTED in planning_authority.json records the
direct gate instruction; it does not attest acceptance of this resulting candidate.

At entry, branch main, HEAD and actually queried LIVE origin/main all equalled
ee7ff4672441ddbcfba6dfaca4ed69973331e85d. Worktree and index were clean before
any repository write. Canonical descriptor SHA-256 was and remains
9295430e8573474b17bc79339c92f46044e443b9dabfe81280f9fb789d751073.
Its lifecycle label and projection state are CENSUS_MEMBERSHIP_ACTIVATED,
event_count is 1, runtime_authority is true, and its event head ID is
95e5ab3ca14cf2b5b47f6a1b1614e80f89f7ea8cbaf22e01245c48ed69aca0f3.
Prior projection SHA-256 is
1bb6f6bda409db2b38ecd078d08c3e60582385db172fcaeacd85b7c28d798d38.
The current descriptor matches the previously accepted effective descriptor and
its independent acceptance pin. Historical event #1 and its installed projection
were replayed using the unchanged genesis rules. Genesis qualification is used
only to verify history; event #2 starts at the installed projection without Q.

B. Accepted preparation-plan identity

Controlling evidence is exactly:

| Path under evaluation/downstream_benchmark/ | SHA-256 |
| --- | --- |
| v6_preparation_plan_manifest_candidate.json | 3c0a6980360c23f6626863be232fea2878cf13497a74aa2e267594fcf3801b0e |
| V6_PREPARATION_PLAN_LIFECYCLE_CLOSURE_V1.md | 9e0bbf8db1eaedb344163a98e944915a51e87424d4abf6894545056e73eccfe7 |

The closure records ACCEPT_V6_PREPARATION_PLAN and HUMAN_PI_ACCEPTED, FROZEN,
PERSISTED, COMMITTED. The enclosing HEAD parent, message, exact 13-path commit
scope and all 12 accepted input blobs were checked against local Git and disk.
The exact plan covers 433 cases, 15 projects, 866 source-variant bindings and
ordinals 1–433 in unchanged census order. PLAN_CONSTRUCTIBLE is 431;
SETUP_REPRESENTATION_BLOCKED and ORACLE_REPRESENTATION_BLOCKED are each 1;
SOURCE_ACQUISITION_REQUIRED and all other blocker categories are 0.

C. Event #2

Stored file: planning_transition_event_candidate.json in this evidence directory.
It uses the existing V6_CAPACITY_STATE_EVENT_V1 schema and EFFECTIVE_V6 namespace.
The namespace confers no authority. sequence=2, kind=STATE_TRANSITION, exact
gate=HUMAN_PI_AUTHORIZE_V6_PREPARATION_PLANNING, from_state=
CENSUS_MEMBERSHIP_ACTIVATED, to_state=PREPARATION_PLANNING_AUTHORIZED.
previous_event_identity is the complete unchanged event #1 head, including its
sequence and complete-payload hash. previous_descriptor_sha256 binds the exact
installed descriptor above. Historical predecessor retains its V5 meaning.
The evidence_references bind the exact accepted manifest and lifecycle closure
in frozen reference order. Independent planning authority binds the prior
descriptor, contract and projection, with scope PREPARATION_PLANNING_ONLY.
No timestamp, event self-hash, future descriptor hash or fabricated supersession
is added. supersession_reference is null.

| Identity | SHA-256 |
| --- | --- |
| event_id: frozen canonical core hash, excluding event_id | 007ac4316ab6961c628ddef19202d73a0fd3859db2de30b56f27efd2cae6121c |
| event_sha256: canonical complete payload hash | 27a9778775635db017a5b783c698c86b30f0c49199f6ad96fb5bc4bcfd01b84a |
| Stored event file bytes | b62c5d7b0a256fff1321944364816d67fd9bcb7ae1b7947964662b1fc124af6b |

D. Exact projection delta

The unchanged frozen phase_flags_for_edge() computes only:

| Projection path | Before | Candidate after |
| --- | --- | --- |
| state | CENSUS_MEMBERSHIP_ACTIVATED | PREPARATION_PLANNING_AUTHORIZED |
| phase_authorizations.PREPARATION_PLANNING | NO | YES |

Descriptor lifecycle_label changes consistently. lifecycle.PREPARATION_AUTHORIZED
remains NO. SOURCE_ACQUISITION, PREPARATION_EXECUTION, IMAGE_BUILD,
ORACLE_EXECUTION, PILOT_FINAL_ALLOCATION and DOWNSTREAM_REPAIR_EXECUTION remain NO.
Every other projection value, including all 433 complete case states, their
order, allocation and cutoff/terminal values, is unchanged. Consumed attempts,
environment identities, environment-ready cases, oracle-plan identities and slot
outcomes remain 0. All cases remain NOT_STARTED. No plan disposition is copied
into a canonical case state.

E. Successor descriptor

Path: evaluation/downstream_benchmark/evidence/v6_preparation_planning_transition_v1/successor_descriptor_candidate.json.
SHA-256: 1ad034c7b49dd243d3e47563fceb53c91da75b9bd1515f2e6a8846cd21396644.
event_count=2; event_head is event #2; the unchanged event #1 entry is retained
and exactly one entry is appended. lifecycle_label and projection.state are
PREPARATION_PLANNING_AUTHORIZED. Result projection SHA-256 is
8ef4ec1f4088c2604f72495d40659511ebc7be132f407101ec57149a8dc56458.
All case states have the identical before/after canonical SHA-256
3f5dc8fc843028d2c973d5c082768658a51164fe49874df5fa5b2f4ee576845c.

Only lifecycle_label, event_count, event_head, event_chain, projection and
projection_sha256 differ from the prior descriptor. All other descriptor fields
are retained, including runtime_authority=true, candidate_only=false, the sole
intended canonical surface, consumer policy and existing membership descriptor
identity. These are inherited descriptor-form semantics, not a current-state
registration. The external candidate_envelope.json explicitly records
RUNTIME_EFFECTIVE=NO, CURRENT_REGISTRATION=PROHIBITED, AUTO_PROMOTION=NO and
CURRENT_AUTHORITY=UNCHANGED_CANONICAL_PREDECESSOR_DESCRIPTOR. The exact acceptance
pin still binds the old installed bytes. No successor acceptance pin, descriptor
identity convention or installation authority is invented. This candidate can
never be consumed as current solely because its internal runtime field is true.

2. Files changed / I. New artifact inventory

Only these 11 new, unstaged files are authored in this evidence directory:

- human_pi_request.txt — exact direct instruction bytes.
- entry_verification.json — pre-write entry gate and all 593 tracked path/hash/index identities.
- planning_authority.json — independent planning-only gate authority, frozen canonical JSON serialization.
- planning_transition_event_candidate.json — exactly one stored event #2 candidate.
- successor_descriptor_candidate.json — exact successor descriptor outside canonical.
- candidate_envelope.json — explicit non-effective external profile and file bindings.
- projection_delta.json — the two changed projection paths.
- validate_transition.py — bounded, read-only audit adapter reusing unchanged frozen functions and schemas.
- validation_results.json — fresh positive checks, rejection reasons, replay hashes and preservation evidence.
- RUN_REPORT.md — this review report.
- artifact_sha256.json — exact hashes of the other ten files; its own self-hash is excluded.

No preexisting tracked file changes. No production code, frozen validator,
schema, accepted plan, canonical descriptor or acceptance pin is edited.
The pre-write scratch entry snapshot is in /private/tmp and outside this inventory.

3. Commands run

Read-only cat/rg/sed and bounded Python inspection checked the direct request,
repository/ancestor instruction paths, owning lifecycle/descriptor/event rules,
schemas, accepted plan and closure. No on-disk AGENTS.md, .airos/current_state.md
or .airos/contracts directory was found; the supplied global rules and direct
Human-PI request govern this exact transaction. Principal commands:

```text
git branch --show-current; git rev-parse HEAD origin/main
git status --porcelain=v1 --untracked-files=all
git ls-remote --exit-code origin refs/heads/main
shasum -a 256 <the three required canonical/accepted inputs>
git ls-files --stage -z; git ls-files --others --exclude-standard -z
git show <historical/HEAD blobs>; git log -1 --format=%s
git diff-tree --no-commit-id --name-only -r HEAD
GIT_OPTIONAL_LOCKS=0 .venv/bin/python -B <inline pre-write entry/replay/commit gate>
apply_patch <only new validate_transition.py and RUN_REPORT.md>
.venv/bin/python -B -m ruff format --no-cache <new validator>
.venv/bin/python -B -m ruff check --no-cache <new validator>
.venv/bin/python -B -m ruff format --check --no-cache <new validator>
GIT_OPTIONAL_LOCKS=0 .venv/bin/python -B evaluation/downstream_benchmark/evidence/v6_preparation_planning_transition_v1/validate_transition.py
GIT_OPTIONAL_LOCKS=0 .venv/bin/python -B <guarded candidate-only construction / audit evidence capture>
.venv/bin/python -B <strict JSON/AST/UTF-8/whitespace and exact inventory checks>
git diff --check; git diff --cached --check
```

The initial sandbox live-ref query failed DNS; the authorized elevated read-only
query succeeded, with no fetch. The first construction audit was stopped by an
overly narrow command guard rejecting git branch --show-current. That read-only
query was added to the guard, then the complete audit passed. An intermediate
format check required formatting the new validator; the final check passed.
Neither issue changed controlling bytes or relaxed execution authority.
Construction writes were restricted to the exact new candidate files. Audit
execution rejects filesystem writes, network and non-local-read-only Git
subprocesses. The validation JSON is captured through stdout to its one new file;
the audited process itself remains read-only. Mutation fixtures never write files.

4. Tests passed/failed / F. Replay and rejection validation

Fresh audit: PASS, 28 positive checks, 57 rejection probes, 0 failed checks.
It verifies all 15 requested invariants, exact schema/core ID/payload/file hash
semantics, prior head/descriptor/projection, accepted planning evidence, replay,
the single phase grant, all case states and the canonical firewall.
Signed probes refresh dependent event/descriptor/envelope identities where
applicable, so semantic rejection is checked after coherent identity changes.
Schema-invalid payload mutations also fail closed.

Required rejection classes include wrong gate/from/to state or nonadjacent edge;
sequence/genesis reset and previous-event ID/payload/sequence mismatch;
descriptor/projection chain mismatch; all six forbidden phase grants and three
execution lifecycle grants; case attempt, readiness, environment/oracle/slot,
eligibility, order and membership mutation; rescue of either blocker in a case
or accepted plan; manifest/closure/request drift; arbitrary event ID, timestamp
and self-hash; authority owner/gate/scope/reference drift; successor head/count/
prior-chain/runtime-policy drift; and candidate-as-current or runtime effectivity.
All reject. Final hash/index comparison preserves all 593 preexisting tracked
files, the exact canonical descriptor and accepted plan inputs.
Ruff check and format check, strict JSON, AST, UTF-8/whitespace, exact inventory
and Git whitespace checks pass upon final completion. The authority JSON retains
the accepted canonical serialization without a terminal LF, so its raw file hash
equals the canonical authority-reference hash. Other authored JSON uses terminal
LF; the request copy retains its original bytes.

No full repository pytest, subject test, preparation-plan reconstruction, Docker
operation, runtime qualification or scientific validation was run.

5. Contract compliance / G. Blocker preservation / H. Firewall

matplotlib::1 retains PREPARATION_PLAN_BLOCKED_SETUP_REPRESENTATION, including
literal line 2 python -mpip install -ve ., UNSUPPORTED_OR_AMBIGUOUS classification
and unresolved setup mechanism. matplotlib::8 retains
PREPARATION_PLAN_BLOCKED_ORACLE_REPRESENTATION, its literal semicolon oracle,
empty argv and unresolved parser mechanism. Neither is repaired, split, rescued
or reclassified. Source-acquisition authority remains distinct and NO.

```text
CANONICAL_CURRENT_STATE_MODIFIED = NO
PREPARATION_PLANNING_PROPOSED = YES
PREPARATION_EXECUTION_AUTHORIZED = NO
PREPARATION_EXECUTED = NO
SOURCE_ACQUISITION_AUTHORIZED = NO
SOURCE_ACQUISITION_EXECUTED = NO
MATERIALIZATION_AUTHORIZED = NO
MATERIALIZATION_EXECUTED = NO
IMAGE_BUILD_AUTHORIZED = NO
IMAGE_BUILD_EXECUTED = NO
ORACLE_AUTHORIZED = NO
ORACLE_EXECUTED = NO
ALLOCATION_AUTHORIZED = NO
ALLOCATION_EXECUTED = NO
GIT_STAGE = NO
GIT_COMMIT = NO
GIT_PUSH = NO
```

6. Risks and unknowns

Constructibility establishes no environment readiness or scientific eligibility.
Both accepted blockers remain unresolved. This new adapter is transaction
evidence; no production event consumer/installer is implemented or qualified.
No candidate acceptance, freeze, commit, canonical installation or successor
runtime effectivity is claimed. The inherited descriptor identity/runtime fields
must be read with the non-effective envelope and existing exact-pin policy.
Future installation prerequisites and downstream publication/execution gates
remain separate Human-PI work. Live-ref checks establish observed equality at
their query times and do not lock the remote against later drift.

7. Recommended next action / J. Next gate

HUMAN_PI_REVIEW_OF_V6_PREPARATION_PLANNING_TRANSITION_CANDIDATE.

Stop at that gate. The canonical lifecycle remains CENSUS_MEMBERSHIP_ACTIVATED.

STATUS =
V6_EFFECTIVE_CURRENT_DESCRIPTOR_V1_CANDIDATE_READY_FOR_HUMAN_PI_REVIEW

Run Report — 2026-10-04, Europe/Budapest.

This transaction constructs only an installable effective-current descriptor
candidate from the accepted membership transition. Artifact existence confers no
current authority. Its `runtime_authority=true` describes intended future
canonical bytes; the canonical zero-event predecessor still governs. The
candidate is not Human-PI accepted, frozen, committed, externally pinned, or
installed. The inherited `candidate_only=false` is preserved transition content,
not a new acceptance attestation.

A. Authority / entry

The direct Human-PI request authorizes only
`HUMAN_PI_OPEN_V6_EFFECTIVE_CURRENT_DESCRIPTOR_CONSTRUCTION_V1`.
Repository `/Users/wuyangchenxi/errpilot`, branch `main`, local HEAD
`b83650784bfc6e79ecf11b3a4be2e4e74aac891f`, parent
`b1172b090f68e609fe6d523b9c244391a97566a7`, and live `origin/main`
`1e5f8a3f4bc2e8555619f727ea317b0bd2fdf801` match the exact entry gate.
The local/remote difference is expected. Worktree and index were clean before
the first write. No on-disk AGENTS.md, `.airos/current_state.md`, or
`.airos/contracts/` exists; the supplied global rules and direct request govern.
No existing effective descriptor was found in 103 benchmark JSON artifacts.
Entry checks are recorded in `entry_verification.json`.

B. Source transition candidate

Path: `evaluation/downstream_benchmark/evidence/v6_census_membership_activation_v1_after_genesis_bridge/post_state_candidate.json`.

SHA-256: `bdc7f0d5c7927d7a691fc7a1768e60d4ff82287a1910aa1aac5158ad8a83bf54`.

Projection SHA-256: `1bb6f6bda409db2b38ecd078d08c3e60582385db172fcaeacd85b7c28d798d38`.

Event ID: `95e5ab3ca14cf2b5b47f6a1b1614e80f89f7ea8cbaf22e01245c48ed69aca0f3`.
Event count remains one. The event payload SHA-256 remains
`9183d5b373128bca07018b6524e09bfbfb8cac7e38ccbea28c966f7c018d72cc`.
The accepted activation closure SHA-256 is
`5edf166632d5f847ebb7fa7877ddf88757eff1d73c4025156450ecbda084801b`.
Its lifecycle and all twelve committed transition/closure paths were verified
against the exact parent commit. Q plus the accepted event reproduced the exact
stored source bytes; no new event or transition was created.

C. Installation authority

Path: `evaluation/downstream_benchmark/V6_CENSUS_MEMBERSHIP_INSTALLATION_AUTHORITY_V1.json`.

Stored and semantic SHA-256:
`359be257db9b355222d71d3e72e9234e736331d5e1a6d079f883b572f85a7458`.

Lifecycle closure:
`evaluation/downstream_benchmark/V6_CENSUS_MEMBERSHIP_INSTALLATION_AUTHORITY_V1_LIFECYCLE_CLOSURE.md`.

Closure SHA-256: `f6b2ba7da86feeb29a9308e11f1e8da2d7200a138e6fcf7c403ebb3050fc4212`.

The exact seven fields and values remain unchanged. HUMAN_PI_ACCEPTED, FROZEN,
PERSISTED, and COMMITTED are supported by the accepted closure and exact enclosing
commit parent, message, two-path inventory, and committed blob checks. This prior
authority does not authorize canonical installation in this construction task.

D. Exact three-field effectivity delta

| Top-level field | Accepted transition value | Constructed candidate value |
| --- | --- | --- |
| runtime_authority | false | true |
| authoritative_current_surfaces | empty list | exactly the one canonical path below |
| effective_current_descriptor_identity | null | exactly the schema-supported object below |

```json
{
  "descriptor_id": "V6_EFFECTIVE_CURRENT_DESCRIPTOR_CENSUS_MEMBERSHIP_ACTIVATED_V1",
  "human_pi_transition": {
    "path": "evaluation/downstream_benchmark/V6_CENSUS_MEMBERSHIP_INSTALLATION_AUTHORITY_V1.json",
    "sha256": "359be257db9b355222d71d3e72e9234e736331d5e1a6d079f883b572f85a7458"
  }
}
```

The sole surface is `evaluation/downstream_benchmark/v6_current_state.json`.
No `installation_authority` top-level field was added.

E. Effective descriptor candidate

Path: `evaluation/downstream_benchmark/evidence/v6_effective_current_descriptor_v1/effective_current_descriptor_candidate.json`.

Exact stored SHA-256:
`9295430e8573474b17bc79339c92f46044e443b9dabfe81280f9fb789d751073`.

Stored size: 442041 UTF-8 bytes, including the final newline.

Descriptor ID: `V6_EFFECTIVE_CURRENT_DESCRIPTOR_CENSUS_MEMBERSHIP_ACTIVATED_V1`.

F. Semantic equality proof

All thirteen non-effectivity top-level fields remain semantically equal and
retain exact stored UTF-8 value bytes: candidate_only, consumer_policy, contract,
derived_views_authority, event_chain, event_count, event_head,
intended_effective_descriptor_path, lifecycle_label, predecessor, projection,
projection_sha256, and schema. Value-span comparison preserves nested whitespace,
field order, scalar types, and values. Candidate_only remains false;
lifecycle_label remains CENSUS_MEMBERSHIP_ACTIVATED. The complete event chain,
event head, projection, predecessor, consumer policy, contract reference, and
canonical-path policy are exact. Projection stored-value SHA-256 remains
`b016e542003ebd7df1738543b6bb7976f4dbf09d6bdc726380cf9abef1bab9ce`.

All 433 member identities, numeric ranks, row order, 15 projects, and scientific
case states remain exact. All seven phase authorizations remain NO, and the
PREPARATION_AUTHORIZED, ORACLE_AUTHORIZED, and ALLOCATION_AUTHORIZED lifecycle
flags remain NO. No source acquisition, materialization, build, oracle, repair,
preparation, or allocation authority is gained.

G. Schema / installability proof

The accepted closed V1 schema passed. Its exact SHA-256 is
`cc326c0e8099bc19bf9c002ad48af68cbf488360e4bbb8cb9e0e0266b017b0f9`.
The unmodified frozen `validate_installation_semantics` function passed for the
exact candidate bytes in non-mutating proof mode. The frozen bridge validator
SHA-256 is `5ca9e0f1068b963139c0529f7bbcf142a0728ef61ad9be346e19ac1dae1f2930`.
It returned semantic_proof_valid=true, installation_performed=false, and
runtime_authority_granted_by_validator=false.

The exact candidate and historical inputs are real. Future candidate lifecycle,
committed/installed observations, installation authorization, and exact acceptance
pin were hypothetical in-memory fixtures required by that proof interface. No
proof object or pin was serialized. This establishes structural compatibility,
not fulfillment of future governance or installation prerequisites. Actual
installation remains blocked.

H. Rejection matrix / tests

Thirty descriptor mutations were rejected by the exact construction adapter:
runtime authority false; empty/wrong surfaces; null identity; wrong descriptor
ID; wrong authority path/hash; fourth semantic field delta; altered projection,
event head, membership, or event chain; preparation/oracle/allocation enabled;
self-hash; future pin, installation-record, or enclosing-commit dependency;
empty ID; extra identity hash; reordered membership; candidate_only true; and
each of the seven phase flags individually enabled.

The frozen validator independently rejected 29 of those 30 mutations. It accepts
any nonempty descriptor ID; the wrong nonempty-ID probe is rejected by the
additional exact Human-PI binding in the adapter. This limitation is explicit in
`validation_results.json`; no frozen validator or schema was changed.

Three further frozen-proof checks rejected a missing acceptance pin, incomplete
candidate lifecycle, and absent separate installation authorization. Three
reverse dependency edges were rejected as hash cycles. Total: 36 rejection checks
passed, zero failures. The positive schema, exact delta/equality, accepted-input
replay, and frozen structural proof passed. Ruff check and format check passed.
The historical full pytest suites and subject tests were not run; their earlier
phase-specific entry guards are not repurposed as construction authority.

I. Hash dependency proof

The acyclic order remains accepted installation authority -> effective descriptor
bytes -> exact descriptor SHA-256 -> future independent acceptance pin.
NO_HASH_CYCLE = YES. The exact seven-field prior authority contains no future
descriptor hash. The descriptor has no own SHA, future pin reference, future
installation-record SHA, or future enclosing-commit SHA. Closed schema and exact
three-field preservation checks reject added dependencies; the frozen graph
checker rejects all three tested reverse edges. External evidence inventory hashes
exclude the inventory's own hash and introduce no descriptor back-reference.

J. Future acceptance-pin requirement

After Human-PI review of these exact bytes, separate acceptance/freeze/persistence/
commit must precede a real independent external exact acceptance pin. That future
pin must bind the canonical path and the candidate's exact stored SHA-256, with
Human-PI acceptance. No such pin exists or was created by this transaction.
Separately authorized canonical installation follows that gate.

K. Preservation

The canonical `v6_current_state.json` retains SHA-256
`d17bcd3b7c669227f920671984b502497cdca9d367523548da4130eb8f986670`,
V6_ACTIVATED=NO, MEMBERSHIP_EFFECTIVE=NO, EVENT_COUNT=0, null event head, and empty
event chain. All 465 tracked benchmark files retain their entry byte hashes;
their path-to-SHA mapping digest remains
`e9d25fe8278a1bf08e876e5800bc50d72c086f56c4ae2a32023f924d8042ab3b`.
Accepted artifacts and all production sources are unchanged. HEAD, branch, and
index remain unchanged. Only the six authorized evidence files are new/untracked.

L. New file inventory / commands run

All files below live in `evaluation/downstream_benchmark/evidence/v6_effective_current_descriptor_v1/`:

1. effective_current_descriptor_candidate.json
2. entry_verification.json
3. validate_descriptor.py
4. validation_results.json
5. RUN_REPORT.md
6. artifact_sha256.json

The inventory binds the other five exact stored files and excludes its own hash.
Historical large evidence is referenced and verified without duplication.

Commands run:

```text
cat <attached Human-PI request>; rg --files / rg -n / sed <bounded owning sources>
git rev-parse --show-toplevel; git branch --show-current; git rev-parse HEAD HEAD^
git status --porcelain=v1 --untracked-files=all
git diff --quiet; git diff --cached --quiet; git diff --name-only; git diff --cached --name-only
git ls-remote --exit-code origin refs/heads/main
git show <accepted commit>:<bound path>; git log -1 --format=%s <accepted commit>
git diff-tree --no-commit-id --name-only -r <accepted commit>
git ls-files --stage -z -- evaluation/downstream_benchmark/
git ls-files --others --exclude-standard -z
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B <stdin read-only entry/hash/lifecycle/replay/scan gate>
apply_patch <new entry, validator, validation-results, and report files>
.venv/bin/ruff format --no-cache evaluation/downstream_benchmark/evidence/v6_effective_current_descriptor_v1/validate_descriptor.py
.venv/bin/ruff check --no-cache evaluation/downstream_benchmark/evidence/v6_effective_current_descriptor_v1/validate_descriptor.py
.venv/bin/ruff format --check --no-cache evaluation/downstream_benchmark/evidence/v6_effective_current_descriptor_v1/validate_descriptor.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B <stdin exact candidate construction and positive proof>
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B evaluation/downstream_benchmark/evidence/v6_effective_current_descriptor_v1/validate_descriptor.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B <stdin evidence inventory creation>
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B <stdin final static/inventory/preservation/positive checks>
git diff --check; git diff --cached --check
```

The initial sandboxed remote query could not resolve github.com; the explicitly
requested read-only live query succeeded with network escalation. This was an
environmental entry-query failure, not a validation failure. Two initial source
reads were truncated by output limits; focused function and JSON inspection then
completed the owning checks. No dependency installation or GUI action occurred.

M. Contract compliance / firewall / risks and unknowns

```text
EFFECTIVE_DESCRIPTOR_ACCEPTED = NO
EFFECTIVE_DESCRIPTOR_FROZEN = NO
EFFECTIVE_DESCRIPTOR_COMMITTED = NO
ACCEPTANCE_PIN_CREATED = NO
CANONICAL_INSTALLATION_EXECUTED = NO
V6_CANONICAL_ACTIVATED = NO
PREPARATION_AUTHORIZED = NO
SOURCE_ACQUISITION_AUTHORIZED = NO
MATERIALIZATION_AUTHORIZED = NO
IMAGE_BUILD_AUTHORIZED = NO
ORACLE_AUTHORIZED = NO
ALLOCATION_AUTHORIZED = NO
SUBJECT_DOCKER_EXECUTION = NO
PILOT_IDS_COMPUTED = NO
FINALS_ALLOCATED = NO
GIT_STAGE = NO
GIT_COMMIT = NO
GIT_PUSH = NO
```

Only the bounded candidate and its minimum transaction evidence were constructed.
No canonical write, acceptance pin, stage, commit, push, dependency installation,
source/materialization/build action, subject Docker, oracle, pilot computation,
or final allocation occurred. Scientific validity, production consumer/installer
behavior, runtime qualification, and subject feasibility remain untested. The
frozen validator's nonempty-ID limitation is closed only by this exact construction
adapter; it is not a claim about future production enforcement.

N. Recommended next action / next gate

NEXT_GATE = HUMAN_PI_REVIEW_OF_V6_EFFECTIVE_CURRENT_DESCRIPTOR_V1

Review these exact candidate bytes and their external evidence. No acceptance,
freeze, persistence commit, external pin, canonical installation, or preparation
decision is made here. Stop.

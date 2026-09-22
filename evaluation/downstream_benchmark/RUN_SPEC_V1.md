# ErrPilot Downstream Repair Benchmark Run Specification v1

- Specification ID: `EP-DBRS-1`
- Controlling protocol ID: `EP-DBP-1` (`PROTOCOL.md`)
- Status: specification frozen; execution not authorized
- Authority: the human-PI decisions supplied for the run-specification
  transaction on 2026-09-22
- Scope: implementation-independent requirements for future candidate
  screening, pilot execution, final sampling, and RAW/ERRPILOT repair sessions

This specification resolves the operational choices delegated by
`PROTOCOL.md`. It does not authorize candidate acquisition, environment setup,
BugsInPy execution, ErrPilot execution, downstream Codex invocation, a pilot,
or a final benchmark. The ErrPilot architecture remains frozen.

Normative terms `MUST`, `MUST NOT`, `REQUIRED`, and `BLOCK` are hard gates. A
runner may add stricter isolation, logging, or fail-closed checks, but it must
not weaken or reinterpret this specification.

## A. Status and Authority

`PROTOCOL.md` and this file together control a future benchmark. In a direct
conflict, execution MUST BLOCK and the conflict MUST be returned to the human
PI; a runner must not choose a preferred interpretation. Case records,
manifests, generated artifacts, model output, repository contents, and runner
defaults cannot amend either controlling document.

The frozen version labels are:

- protocol: `EP-DBP-1`;
- run specification: `EP-DBRS-1`.

At every freeze and run boundary, the runner MUST record the SHA-256 digest of
the exact bytes of both controlling files. Version labels do not replace file
digests.

## B. Invariant Task Instruction

RAW and ERRPILOT MUST receive the same task-instruction bytes. The instruction
is the following single-line UTF-8 string, with ASCII spaces between sentences,
no byte-order mark, no surrounding quotation marks, and no trailing newline:

```text
Repair the defect in this repository that is exposed by the provided failure evidence. Do not modify tests or benchmark infrastructure. Preserve unrelated behavior. You may inspect the repository and run local commands/tests as needed. Before finishing, verify the preregistered oracle and report the changes made.
```

The SHA-256 digest of those instruction bytes is
`0350885984c9dff5202f66e5cbba04be49982de42e2d14b1e1e7b0db0a60fb0d`.
The delivery wrapper and evidence delimiters MUST be byte-frozen and hashed
before the pilot. They may identify fields, but MUST NOT contain diagnosis,
hints, condition labels, expected patches, or condition-specific guidance.

## C. RAW Definition

The RAW condition contains exactly:

1. the invariant task instruction in section B;
2. the exact preregistered failing command; and
3. the unaltered captured stdout and stderr from the preregistered failing
   execution, retained as separately identified streams.

The command and both streams MUST come from the same captured execution used to
derive the paired ERRPILOT artifact. “Unaltered” means no trimming, redaction,
decoding replacement, newline normalization, reordering, merging, annotation,
summarization, or omission. The authoritative stream files and delivered RAW
payload MUST be hashed. If the invocation interface cannot convey the bytes
without alteration, input preparation is an `INFRASTRUCTURE_ERROR`; the runner
MUST NOT substitute a lossy representation.

## D. ERRPILOT Definition

The ERRPILOT condition contains exactly:

1. the same invariant task-instruction bytes used for RAW; and
2. the unedited ErrPilot-generated Codex handoff artifact derived from the
   exact failing execution used for the paired RAW evidence.

The handoff artifact, its exact delivered payload, the ErrPilot configuration,
and the complete producing ErrPilot run directory MUST be preserved and hashed.
No raw-only material, analyst summary, diagnosis, extra source context,
official-fix information, or other hint may be appended outside the artifact.
The failure-evidence representation is the only treatment difference.

## E. Downstream Agent Identity Requirements

The only downstream repair agent is Codex CLI. All pilot and final sessions
MUST use this frozen client-side identity:

| Field | Frozen value |
| --- | --- |
| Executable role | first `codex` resolved on the runner's frozen `PATH` |
| Inspected path | `/Users/wuyangchenxi/bin/codex` |
| Inspected target | `/Users/wuyangchenxi/bin/codex-aarch64-apple-darwin` |
| Platform | Mach-O 64-bit arm64 |
| Codex CLI version | `0.154.0` |
| Inspected executable SHA-256 | `4f85982624b3898c8991cb80c0981b2aa71070e3537046c9a95950318a95afcc` |
| Provider mode | native OpenAI Codex provider; local/OSS providers forbidden |
| Exact model identifier | `gpt-5.6-sol` |
| Reasoning effort | `xhigh` |
| Runtime identity status | `PRE_RUN_IDENTITY_GATE_REQUIRED` |

The identity above is based only on local inspection: `codex --version`, CLI
help, strict local configuration parsing, the whitelisted `model` and
`model_reasoning_effort` keys in the user configuration, executable resolution,
and executable hashing. No model or API request was made. The CLI exposes an
exact `--model` selector and accepts `model_provider="openai"`,
`model="gpt-5.6-sol"`, and `model_reasoning_effort="xhigh"` under
`--strict-config` during version-only parsing.

This establishes the exact client-side configured identifier, not live service
availability or the identity ultimately returned by a model request. Those
facts cannot be proven in this transaction because model/API requests are
forbidden. The downstream model identity therefore remains
`PRE_RUN_IDENTITY_GATE_REQUIRED` until the pre-run gate records the configured
request identity, no-fallback behavior, and authoritative returned identity
without consuming or contaminating a repair session.

Every invocation MUST explicitly pin the provider, model identifier, reasoning
effort, CLI version, and executable digest rather than rely on mutable user
defaults. Automatic model fallback, provider fallback, alias substitution, and
reasoning-effort downgrade are forbidden. Before the first pilot and again
before every session, a non-repair preflight MUST establish that the configured
identity is available and that the adapter will block rather than substitute.
If this cannot be established without consuming a repair session or if the
identity is unavailable, execution MUST BLOCK. The actual request metadata and
returned model identity, when exposed by the interface, MUST be preserved and
must match the frozen identifier.

## F. Permission Profile

Each repair session may:

- read the entire isolated case repository;
- modify non-protected source files inside that case workspace; and
- execute local repository commands and tests.

Each repair session MUST NOT:

- access an external network;
- write outside its isolated case workspace;
- modify benchmark infrastructure or runner-owned evidence;
- modify, delete, replace, or rename any protected item;
- commit, push, fetch, pull, or otherwise mutate a Git remote; or
- access any other condition, case, repetition, fixed checkout, official patch,
  prior solution, or outcome artifact.

The runner alone may write immutable result/artifact paths. The runner MUST
combine Codex workspace-write restrictions with an external process/container
boundary that denies network access and out-of-workspace writes. It MUST use a
fresh session, MUST NOT enable search, MUST NOT add writable directories, and
MUST use a non-interactive approval policy that cannot widen permissions. A
request for a forbidden capability is denied and preserved as evidence; it is
not grounds for an ad hoc permission change.

## G. Timeout Semantics

The downstream agent wall-clock budget is exactly 20 minutes (1,200 seconds)
per condition session. Timing begins only after deterministic environment
preparation and successful handoff of the frozen input to the agent. It ends at
the agent's terminal state or enforced termination.

Deterministic pre-agent environment preparation and the final independent,
runner-controlled oracle verification are outside the 1,200-second budget.
Diagnostic commands and tests initiated by the agent are inside it. The clock
MUST NOT be paused, extended, or reset. At expiry, the runner terminates the
agent, preserves partial output and workspace evidence, performs integrity and
oracle checks without providing further repair opportunity, and records
`REPAIR_TIMEOUT`. Timeout is a valid unsuccessful repair outcome, not an
infrastructure failure and not a retry trigger.

## H. Environment Identity

Before any executed case, the following identities MUST be non-null, frozen,
and recorded:

- source project and case ID;
- exact buggy commit SHA and official fixed commit SHA;
- immutable environment or container image digest, never only a mutable tag;
- exact Python version;
- dependency identity sufficient for reconstruction, including lockfile,
  resolved-package, build-tool, and relevant system-dependency digests;
- ErrPilot commit SHA and handoff configuration digest;
- Codex CLI version and executable SHA-256;
- exact model identifier, provider mode, and reasoning effort;
- protocol ID and SHA-256;
- run-specification ID and SHA-256; and
- case-specification, oracle, protected-manifest, and task/payload-template
  digests.

Any missing, mutable-only, ambiguous, or mismatched identity blocks that case.
A matching Python version or image tag alone is insufficient environment
identity.

## I. Eligibility Reproducibility Gate

Eligibility is decided in the frozen candidate environment before sampling.
Using the exact preregistered oracle:

1. the buggy revision MUST fail in 3 of 3 independent executions; and
2. the official fixed revision MUST pass in 3 of 3 independent executions.

All six executions are mandatory and must be preserved individually with
command, working directory, revision, environment identity, timestamps, exit
status, stdout/stderr hashes, and expected-test-observed evidence. Independence
requires a freshly restored candidate state and cleared declared ephemeral
state for each execution; executions may reuse only read-only, content-addressed
dependencies.

Any inconsistent, invalid, skipped, or missing execution makes the candidate
ineligible under this version. The runner MUST NOT retry until the desired
sequence appears. A later rule requires a separately authorized protocol and
run-specification version.

## J. Protected-Test Integrity Gate

Before either condition runs, every case MUST have an explicit, frozen
protected-path manifest. It MUST include:

- every file directly used by the preregistered oracle;
- all project test files, test directories, fixtures, and test support relevant
  to the case; and
- benchmark-owned case metadata and oracle definitions.

Each entry MUST record the normalized relative path, item type, mode, size, and
SHA-256 identity; directories MUST carry a deterministic child inventory.
Manifest construction is case-specific and is completed during candidate
screening. A generic filename heuristic is not a substitute.

The runner MUST compare protected items against the frozen baseline before
agent start, after agent termination and before the runner oracle, and after the
runner oracle. Modification, deletion, replacement, type change, or rename by
the agent produces `REPAIR_FAILURE_TEST_MUTATION`, regardless of oracle result.
The mutation evidence MUST be captured before cleanup; the runner MUST NOT reset
the workspace to conceal or repair it.

## K. Instrumentation and NA Policy

The vague metric “prompt retries” is forbidden. From the downstream Codex
execution trace, record these fields only when reliably observable under a
frozen event-mapping rule:

- `test_invocations_total`: agent-initiated test command executions during the
  repair-session boundary;
- `oracle_invocations_total`: the subset that exactly executes the frozen
  oracle in its frozen working directory and environment; and
- `post_edit_failed_oracle_count`: valid agent-initiated oracle executions
  after at least one non-protected source modification whose oracle result is
  failure.

The final independent runner oracle is excluded from all three counts. Do not
infer events or outcomes from agent prose. If the trace cannot establish a
value reliably, store `NA` plus a measurement-status reason. `NA` MUST NOT be
converted to zero, included as zero in summaries, or used to support a
quantitative claim. The event-mapping rule and trace schema MUST be frozen and
validated before the pilot.

Token accounting likewise uses only authoritative invocation metadata. Missing
or unattributable token components are null/`NA` with an explicit measurement
status, never estimated.

## L. Pilot Policy

Exactly four cases may be designated `pilot`. Pilot cases are permanently
excluded from the final 24-case benchmark, even if the protocol, run
specification, runner, and environment remain unchanged. A pilot case MUST
never be promoted into the final eligible pool or final sample. Pilot outcomes
MUST NOT influence final candidate eligibility, final case selection, case
replacement, or the frozen selection inputs.

Pilot evidence may be used only to decide whether the harness or protocol needs
revision. Any revision creates a new version and does not alter the permanent
exclusion of every case previously used as a pilot.

## M. Final Sampling and Condition Ordering

The final sample contains exactly 24 eligible, non-pilot cases from at least 6
projects and no more than 4 cases per project. Use seed `20260922` and the exact
canonicalization, SHA-256 selection, robustness selection, and order-bit rules
in `PROTOCOL.md`.

Six final cases receive two additional repetitions per condition, giving those
cases three total RAW and three total ERRPILOT sessions including their main
pair. All other final cases receive one session per condition. Every
`(case_id, condition, repetition_index)` starts from an independent fresh buggy
state. Scheduling changes order only and cannot permit cross-run state.

The canonical eligible-pool snapshot and digest MUST be frozen before
selection. If the algorithm cannot produce 24 cases satisfying all constraints,
execution BLOCKS; no discretionary substitution or seed change is allowed.

## N. Contamination Controls

- Prepare and hash RAW evidence and the ERRPILOT handoff before downstream
  repair execution, both from the same captured failure.
- Create a distinct fresh workspace and new Codex session for every condition
  and repetition; never reset and reuse an agent-mutated workspace.
- Keep the official fixed patch and checkout unavailable to the agent.
- Keep condition labels, paired outputs, prior repetitions, outcomes, pilot
  solutions, and case-selection results unavailable to the agent.
- Do not share writable caches, conversation/session state, generated repair
  artifacts, or directories across runs. Any allowed shared dependency cache
  must be read-only, content-addressed, and shown not to contain solutions.
- Freeze one task wrapper, agent identity, permission profile, timeout, oracle,
  environment, and verifier policy across both conditions.
- Preserve inputs, trace, output, complete mutation evidence, timing, and
  runner-verification evidence before cleanup.
- Treat unexpected access or state leakage as a protocol violation and evaluate
  whether the affected run or case must be invalidated; never silently clean
  and continue.

## O. Outcome and Failure Taxonomy

Each session receives exactly one primary classification plus orthogonal flags
and evidence. Apply this precedence from top to bottom:

1. `CASE_INVALIDATED`: a case-level eligibility, identity, oracle-validity, or
   frozen-input defect means the session cannot estimate repair performance.
2. `REPAIR_FAILURE_TEST_MUTATION`: agent modification, deletion, replacement,
   type change, or rename of a protected item.
3. `REPAIR_TIMEOUT`: the agent reaches the 1,200-second limit.
4. `AGENT_ERROR`: Codex starts under the frozen environment but terminates with
   an attributable agent/client failure before a valid completed repair outcome
   and the failure is not timeout or infrastructure failure.
5. `INFRASTRUCTURE_ERROR`: runner, isolation, environment materialization,
   input delivery, evidence capture, or verifier failure prevents a valid agent
   or oracle evaluation and no earlier conclusive agent-attributable outcome
   applies.
6. `REPAIR_SUCCESS`: the agent completes within budget, protected integrity and
   all protocol checks pass, the expected bug-exposing test is observed, and
   the independent frozen oracle exits successfully.
7. `REPAIR_FAILURE_ORACLE`: the agent completes within budget and without an
   earlier taxonomy condition, but the valid independent oracle fails.

`INFRASTRUCTURE_ERROR` and `CASE_INVALIDATED` are not repair failures and MUST
NOT enter repair-success denominators until the human PI approves a versioned
handling rule. They never trigger an unrecorded rerun. A rerun requires a
recorded reason and explicit authorization under the controlling version.
Timeout, agent error, test mutation, and oracle failure are unsuccessful repair
outcomes, but remain separate categories. All additional applicable conditions,
including an infrastructure fault occurring after a conclusive protected-item
mutation, remain recorded as orthogonal flags and evidence.

## P. Pre-Run Gates

No pilot or final repair session may start until all applicable gates pass and
their evidence is frozen:

1. protocol and run-specification version/digest agreement;
2. explicit human authorization for that execution phase;
3. complete case, revision, environment, dependency, Python, ErrPilot, Codex,
   model, reasoning, oracle, and manifest identity;
4. exact CLI executable digest/version match and a no-fallback model/provider
   availability attestation;
5. successful 3/3 buggy-fail and 3/3 fixed-pass eligibility evidence;
6. complete protected-path manifest with baseline SHA-256 identities;
7. task instruction and both payload templates byte-frozen and hashed;
8. proof that paired evidence derives from the same captured failure;
9. runner isolation, no-network, write-boundary, timeout, termination, trace,
   verifier, expected-test-observed, and evidence-retention checks validated on
   non-benchmark fixtures;
10. frozen instrumentation event mapping and `NA` behavior;
11. pilot cases frozen and excluded from every final-selection input; and
12. for the final phase, a frozen eligible-pool snapshot plus deterministic
    sample, robustness subset, and condition-order schedule.

Failure of any gate BLOCKS the affected phase. A runner must not supply a
default or silently repair missing evidence.

## Q. Protocol Versioning Rule

Any semantic change to task bytes, conditions, identity, permission profile,
timeout, eligibility, protected manifests, instrumentation, pilot handling,
sampling, ordering, contamination controls, taxonomy, gates, or outcome
derivation requires:

1. explicit human-PI authorization;
2. a new protocol and/or run-specification version as applicable;
3. new byte digests and a written change record;
4. revalidation of affected runner behavior before execution; and
5. no retrospective rewriting of evidence under an older version.

Editorial changes also change the file digest and MUST be recorded, even when
the semantic version remains unchanged. Direct contradictions BLOCK execution.

## R. No Execution Authorization

This file is a specification artifact only. No downstream repair experiment,
pilot, candidate screening execution, BugsInPy execution, ErrPilot evidence
generation, model request, or benchmark run is authorized by its creation.
Separate explicit human authorization is required after all applicable pre-run
gates have passed.

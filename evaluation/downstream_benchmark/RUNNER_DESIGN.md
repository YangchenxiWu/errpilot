# Future Production Benchmark Runner Design

Status: production-runner design proposal only. A minimal synthetic-only
mechanics harness now exists under `harness/`; it is not a production runner
and cannot invoke a live agent or accept a non-synthetic case. This document
does not authorize execution, BugsInPy acquisition, dependency installation,
Codex invocation, or changes to ErrPilot. A future production implementation
must remain outside `errpilot/` and must follow `PROTOCOL.md` plus a
human-approved, versioned run specification.

## Design Boundary

The runner is an experiment orchestrator around the existing ErrPilot CLI and a
separate downstream Codex interface. It must not add repair behavior to
ErrPilot, alter existing CLI behavior, modify existing ASE evaluation assets,
or use the official fixed patch as agent context. Its phases are candidate
qualification, input preparation, isolated condition execution, independent
verification, and evidence/result finalization.

Execution must fail closed when a pinned input or frozen configuration value is
missing or mismatched.

## Frozen Inputs

The controlling run specification identifies and requires hashing of at least:

- protocol version and case-manifest snapshot;
- source-project snapshot and exact buggy/fixed revisions;
- reproducible environment image or lock identifier;
- failing and oracle commands plus working directory;
- protected test-file manifest;
- common task-instruction bytes;
- ErrPilot revision and handoff configuration;
- Codex agent, exact model/version, configuration, permissions, and invocation
  adapter;
- numeric wall-clock timeout; and
- selection/order seed and repetition plan.

`RUN_SPEC_V1.md` freezes the cross-run values and lists the remaining per-case
gates. The runner must not supply implicit defaults.

## Candidate Qualification and Input Preparation

Qualification occurs before sampling and downstream execution. In a
reproducible candidate environment, run the preregistered oracle on the pinned
buggy revision enough times to establish the stated reproducibility criterion,
then run that exact oracle on the official fixed revision. Preserve commands,
stream bytes, exit codes, timing, environment identity, and revision checks.
Apply all eligibility rules in `PROTOCOL.md` and record every ineligible
candidate in `exclusions.csv`.

For an eligible case, prepare condition inputs before any repair run:

1. Use the frozen existing ErrPilot capture command on the pinned buggy state
   to execute the failing command once and preserve its stdout and stderr as
   separate binary artifacts. Do not trim, redact, reorder, merge, normalize
   newlines, or otherwise rewrite these authoritative streams.
2. Construct the RAW payload from the frozen common task instruction, exact
   failing command, and those unaltered streams. The adapter may add only the
   minimum byte-stable delimiters required to distinguish fields; delimiter
   bytes are part of the frozen prompt template.
3. Continue the frozen ErrPilot bundle, local-triage, and Codex-route pipeline
   on that same captured run to generate the handoff artifact. Preserve the
   full ErrPilot run directory and artifact bytes. Thus RAW and ERRPILOT inputs
   derive from the same captured failure, not two independently varying failure
   executions.
4. Construct the ERRPILOT payload from the identical task-instruction bytes and
   the unedited handoff artifact. Do not append an analyst summary or official
   fix information.
5. Hash the task text, RAW payload, handoff, ERRPILOT payload, raw streams, and
   generating configuration. Record parent/derivation relationships in a
   machine-readable evidence index.

If a text-only Codex interface cannot carry an unaltered stream, input
preparation fails. The implementation must not substitute lossy decoding.

## Fresh-State Isolation and Clean Separation

Maintain a read-only local object/source store for the pinned project and create
a new disposable workspace for every `(case_id, condition, repetition)` tuple.
Materialize the exact buggy revision, build/attach the same frozen environment,
verify a clean baseline and revision hash, and generate a complete baseline file
manifest before agent invocation.

RAW and ERRPILOT must never run sequentially in the same mutable checkout. A
"reset" means destroying or quarantining the completed disposable workspace and
creating a different fresh workspace from the read-only source. Do not rely on
`git reset` to remove untracked files, caches, subprocess state, or leaked
artifacts. Each run receives isolated writable storage and a new Codex session;
shared caches must be read-only and proven not to contain solutions or prior-run
state.

Condition order follows the protocol's deterministic seeded rule. The runner
captures the complete mutated workspace and diff before quarantining it. Cleanup
is allowed only after all configured retention checks succeed.

## Downstream Codex Invocation Boundary

Codex is the only repair agent. The invocation adapter supplies exactly one
condition payload, the frozen workspace root, and the common frozen
model/configuration/permissions/timeout. It must not pass the condition label,
paired result, official patch, fixed checkout, pilot solutions, or prior
repetitions. ErrPilot generates the ERRPILOT artifact but never invokes Codex or
applies a repair.

The adapter records the request and response envelope, process/session
identifier, timestamps, exit reason, stdout/stderr or event stream, tool/action
trace made available by the interface, and authoritative usage metadata. Any
external side effect not permitted by the frozen permission profile is a
protocol violation.

## Timeout

The human-approved run specification fixes the wall-clock timeout at 1,200
seconds, used unchanged for every condition and repetition. Measure it at the
outer orchestrator boundary from successful invocation submission until
terminal agent state. On expiry, terminate through the supported adapter
mechanism, record `agent_status=timeout`, preserve partial artifacts, and
continue to the mutation check and oracle. Do not extend, pause, or retry the
timeout for one condition only.

## Artifact Capture and Immutable Evidence

Write each run to a unique, content-addressed or collision-resistant directory.
Capture, at minimum:

- frozen run specification and environment/revision attestations;
- baseline file and protected-test manifests;
- prompt components and exact delivered payload;
- raw failure stdout/stderr and ErrPilot run artifacts;
- Codex event/response output and usage metadata;
- before/after repository status, binary-safe diff, untracked-file list, and
  post-run file hashes;
- timeout/termination evidence;
- oracle stdout/stderr, exit code, and timing;
- test-mutation report; and
- final machine-readable result plus validation log.

After capture, generate SHA-256 checksums and make the raw evidence tree
read-only or copy it into an append-only artifact store. Later summaries are
derived artifacts and never replace raw files. If immutability cannot be
enforced, record that limitation and do not call the evidence immutable.

## Token Accounting

Use only token counts emitted by the frozen Codex invocation API/adapter. Sum
all Codex calls inside one condition run and retain per-call values for input,
output, cached, reasoning, and total tokens when available. Store both the API's
reported total and a component sum; flag disagreement rather than repairing it.

If the API omits usage, reports incompatible units, or cannot attribute usage
to one condition, set token fields to null and record a specific
`token_measurement_status`. Do not estimate tokens from characters or conflate
ErrPilot's local processing with downstream Codex consumption.

## Test and Oracle Invocation Accounting

The adapter should derive the three metrics frozen by `RUN_SPEC_V1.md` only
from observable, frozen lifecycle events:

- `test_invocations_total`;
- `oracle_invocations_total`; and
- `post_edit_failed_oracle_count`.

The mandatory post-agent oracle run by the independent verifier is recorded
separately and is excluded from all three metrics. If trace events cannot
establish a value without inference, the value is `NA` with a measurement-
status reason, never zero. The exact event mapping must be frozen and exercised
before the pilot.

## Oracle Execution and Success Classification

After Codex reaches a terminal state or timeout, first preserve agent artifacts
and compute the workspace mutation set. Then run the exact preregistered oracle
in a separate verifier process using the same frozen environment and resulting
workspace. The verifier supplies no repair assistance and does not modify the
workspace except for declared ephemeral caches, which must live outside the
tracked tree where possible.

Record exact command bytes, working directory, environment identity, stdout,
stderr, exit code, start/end times, the expected bug-exposing test identity,
and whether that test actually executed. An exit code of zero caused by
collection changes, deselection, or skipping the bug-exposing test is not a
valid oracle pass. Classify `repair_success=true` only when the valid oracle
passes, no protected test changed, no timeout disqualifies the run, and no
protocol violation occurred. Preserve a passing oracle as evidence, not as a
claim of broader scientific or software validation.

## Test-File Mutation Detection

Qualification creates a protected-test manifest from the complete baseline set
of BugsInPy/project test sources and fixtures plus any harness or oracle
definitions designated read-only. The human-approved case specification
resolves project-specific paths before the pilot. A production configuration
file is not automatically classified as a test merely because pytest reads it;
oracle-validity checks separately detect configuration changes that prevent the
expected bug-exposing test from running.

Before and after Codex, compare path, file type, mode, size, and SHA-256 for
every protected item and detect added/deleted/renamed test-like paths using the
full repository diff and untracked-file inventory. Run this check before the
oracle and again afterward to distinguish agent mutation from verifier cache
effects. Any agent-created modification, deletion, replacement, rename, or
equivalent bypass of a protected test is `test_mutation_detected=true`, a
protocol violation, and an unsuccessful repair even if the oracle exits zero.
Preserve the evidence before any cleanup.

## Proposed Result Schema

Use one immutable JSON record per condition run, with a CSV projection for
analysis. Fields should include:

| Group | Fields |
| --- | --- |
| Identity | `schema_version`, `experiment_id`, `case_id`, `source_project`, `bugsinpy_bug_id`, `condition`, `repetition_index`, `sample_role` |
| Pins | `source_revision`, `fixed_revision`, `environment_digest`, `python_version`, `dependency_identity`, `protocol_sha256`, `run_spec_sha256`, `errpilot_revision`, `codex_cli_version`, `codex_executable_sha256`, `codex_provider`, `codex_model`, `codex_reasoning_effort`, `codex_config_sha256` |
| Scheduling | `sample_seed`, `condition_order`, `scheduled_at_utc`, `started_at_utc`, `finished_at_utc` |
| Input | `task_instruction_sha256`, `failing_command`, `raw_stdout_sha256`, `raw_stderr_sha256`, `handoff_sha256`, `delivered_payload_sha256` |
| Agent | `agent_status`, `agent_exit_reason`, `timeout_seconds`, `timed_out`, `agent_duration_ms`, `artifact_directory` |
| Mutation | `workspace_diff_sha256`, `changed_paths`, `test_mutation_detected`, `test_mutation_paths`, `protocol_violation`, `protocol_violation_reason` |
| Oracle | `oracle_command`, `oracle_expected_test`, `oracle_expected_test_observed`, `oracle_exit_code`, `oracle_duration_ms`, `oracle_stdout_sha256`, `oracle_stderr_sha256`, `oracle_valid`, `repair_success` |
| Tokens | `input_tokens`, `output_tokens`, `cached_tokens`, `reasoning_tokens`, `total_tokens`, `token_measurement_status`, `usage_metadata_sha256` |
| Instrumentation | `test_invocations_total`, `oracle_invocations_total`, `post_edit_failed_oracle_count`, `instrumentation_measurement_status` |
| Integrity | `baseline_manifest_sha256`, `protected_tests_manifest_sha256`, `evidence_index_sha256`, `record_created_at_utc`, `notes` |
| Outcome | `outcome_classification`, `repair_success`, `classification_evidence` |

Enums, nullability, clock format, path encoding, success derivation, and checksum
serialization must be defined in a versioned machine-readable schema before the
pilot. Result validation should reject unknown conditions, duplicate run keys,
missing primary evidence, inconsistent totals, and success records with a
timeout, test mutation, failed oracle, or protocol violation.

## Pilot Gate and Future Implementation Sequence

The future implementation should first validate schemas and isolation using
non-benchmark fixtures, then run the 4 designated pilot cases. All pilot cases
remain permanently excluded from the final eligible pool and final sample.
After the pilot, the human researcher decides whether the harness or protocol
changes. Any change requires a new version/hash. Only after that decision, a
frozen eligible-pool snapshot, deterministic final sampling, and explicit
authorization may the final benchmark run.

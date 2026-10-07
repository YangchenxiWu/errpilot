# V6 Preparation Execution Transition Lifecycle Closure V1

Run Report / closure record — 2026-10-07, Europe/Budapest.

## 1. Task summary and Human-PI authority

The latest direct Human-PI instruction accepts only the exact event #3 and
transition-result candidate through
`ACCEPT_V6_PREPARATION_EXECUTION_TRANSITION_CANDIDATE` and opens this transaction
through `OPEN_V6_PREPARATION_EXECUTION_TRANSITION_LIFECYCLE_CLOSURE`.
It authorizes this one closure and one local commit of exactly 13 paths.

V6_PREPARATION_EXECUTION_TRANSITION = HUMAN_PI_ACCEPTED = FROZEN = PERSISTED = COMMITTED.

This lifecycle attestation is fulfilled only after the exact enclosing local
commit and all postconditions are successfully verified. Until then, COMMITTED
is the transaction target. The future enclosing commit SHA and this closure's
own SHA are deliberately omitted. Completion requires the specified parent and
message, exactly the 12 accepted files plus this closure, clean worktree/index,
unchanged controlling bytes, and a final LIVE origin/main observation at the
parent. This record grants no canonical installation, effectivity binding,
preparation execution, source acquisition, build, oracle, allocation, repair,
publication, scientific-validation or paper-readiness authority.

Entry inspection found main, HEAD and independently queried LIVE origin/main at
`dded507b6049ad24cdf813590e2d8e8af7e9e241`, empty tracked diff/index and exactly
12 expected untracked files. artifact_sha256.json and RUN_REPORT.md supplied the
accepted inventory. The manifest binds eleven files and excludes its own hash;
its independently calculated twelfth hash is bound below. All 992 preexisting
tracked byte/index identities match the accepted entry record. No applicable
on-disk AGENTS.md or .airos/current_state.md / contracts directory was found.
The supplied global rules and latest explicit Human-PI request govern this
bounded transaction. The initial sandbox remote query failed DNS; the elevated
read-only ls-remote query succeeded. No fetch, dependency installation or GUI
operation was used.

## 2. Files inspected and changed

Inspected the accepted manifest, RUN_REPORT.md, commands_run.json, entry record,
authority, envelope, projection delta, event, successor, validator and recorded
validation results; the canonical descriptor and its frozen successor contract;
the owning planning validator and read-only guard; the prior planning transition
closure; and the runtime source, data, plan, lifecycle, prerequisite receipts and
historical event/authority inputs traversed by the accepted validator.
The validator verified 376 accepted runtime-lineage files and 381 committed pins.

Only this closure is newly authored. The 12 accepted inputs are persisted
byte-for-byte, retaining their historical HUMAN_PI_REVIEW_PENDING labels and
construction-only GIT_STAGE/GIT_COMMIT=NO statements. Those bytes describe the
prior construction transaction. This closure supplies the later acceptance,
freeze and local persistence authority without rewriting them. The complete
13-path scope and all twelve accepted hashes are bound in section 8.

## 3. Commands run and completion gates

Principal commands actually run before writing this closure:

```text
rg --files --hidden; rg -n; cat; sed
python3 -B <entry, inventory, exact hash and metadata inspection>
git status --porcelain=v1 --untracked-files=all
git branch --show-current
git rev-parse HEAD
git diff --name-only
git diff --cached --name-only
git ls-files --others --exclude-standard -z
git ls-remote --exit-code origin refs/heads/main
.venv/bin/python -B evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/validate_transition.py --json
.venv/bin/ruff check --no-cache evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/validate_transition.py
.venv/bin/python -B <AST/static, strict JSON/UTF-8 and contract identity checks>
git diff --check
git diff --cached --check
git config --get core.hooksPath
rg --files --hidden .git/hooks -g '!*.sample'
```

The original validator ran through its unchanged main entry point, before this
closure existed or any staging occurred. Its audit hook denies filesystem
mutation, network and non-local-read-only-Git subprocesses. Its sealed-preservation
check is specific to the original parent, empty index and 12-file untracked
entry; it is not rewritten to accept the later lifecycle transaction.
Fresh stdout was captured outside the repository and matched the accepted
validation_results.json exactly. No active custom hook path or non-sample
repository hook was found. One discovery rg explicitly named the absent .airos
directory and returned that diagnostic; it did not alter any file.

Required subsequent completion gates:

```text
.venv/bin/python -B /private/tmp/errpilot-v6-transition-lifecycle-closure-gate.py prestage
git add -- <the exact 13 explicit paths in commit_scope.paths>
.venv/bin/python -B /private/tmp/errpilot-v6-transition-lifecycle-closure-gate.py staged
git diff --cached --check
git commit -m "benchmark: freeze V6 preparation execution transition"
.venv/bin/python -B /private/tmp/errpilot-v6-transition-lifecycle-closure-gate.py post
git diff --check
git diff --cached --check
git ls-remote --exit-code origin refs/heads/main
```

These subsequent commands are completion conditions, not a claim that commands
in the future already ran when this file was written. The independent transaction
gate verifies immutable accepted hashes, every preexisting tracked byte/index
identity, staged/committed blobs, exact additions, parent/message, one commit,
canonical semantics, empty real ledger/output paths and clean postconditions.
Its scratch snapshot and captured validation output are outside the repository
inventory. No amend, tag, push or history rewrite is permitted.

## 4. Tests passed / failed and replay

The unchanged accepted validator passed 23 positive checks and all 30 rejection
probes as PASS_REJECTED, with zero failures. Fresh complete result bytes equal
the accepted validation_results.json (SHA bound below). Full event #1 -> event #2
-> event #3 candidate replay passed, including authority references, predecessor
continuity, canonical/stored identities, adjacent frozen edges and projections.
Historical genesis qualification was applied only to event #1.

Ruff check with --no-cache passed on the accepted validator. AST parsing passed
for that validator and the accepted successor runtime. Static inspection checked
the audit guard; the accepted validator checked unconditional runtime dispatch
rejection. Strict JSON checks passed for all nine JSON files, rejecting duplicate
keys and nonfinite constants and enforcing valid UTF-8 strings. All twelve
accepted files passed strict UTF-8, absence of BOM/NUL/CR and trailing-whitespace
checks. Original no-terminal-LF bytes in execution_authority.json and
human_pi_request.txt were retained. git diff --check and cached --check passed.
Ruff format checking, live runtime/build/egress qualification and scientific
benchmark tests were not run or claimed.

## 5. Contract compliance, exact semantics and preservation

Freeze the exact adjacent edge PREPARATION_PLANNING_AUTHORIZED ->
PREPARATION_EXECUTION_AUTHORIZED. The candidate changes only these three leaves:

| Projection leaf | Before | Candidate after |
| --- | --- | --- |
| projection.state | PREPARATION_PLANNING_AUTHORIZED | PREPARATION_EXECUTION_AUTHORIZED |
| projection.lifecycle.PREPARATION_AUTHORIZED | NO | YES |
| projection.phase_authorizations.PREPARATION_EXECUTION | NO | YES |

PREPARATION_PLANNING stays YES. SOURCE_ACQUISITION, IMAGE_BUILD,
ORACLE_EXECUTION, PILOT_FINAL_ALLOCATION and DOWNSTREAM_REPAIR_EXECUTION stay NO.
All 433 ordered case states and scientific classifications are unchanged;
all cases remain NOT_STARTED, attempt_consumed=false, environment_identity=null
and slot_accounting empty. All 641 ordered base-attempt opportunities remain
UNSTARTED, unclaimed and unconsumed, with the 583 restricted / 58 network NONE
split intact. The 431 constructible-case population is unchanged.

matplotlib::1 retains the setup-representation blocker and literal
`python -mpip install -ve .`; matplotlib::8 retains the oracle-representation
blocker and its exact unsplit semicolon-containing oracle command. Both remain
outside the dispatchable work-item population. Their plan IDs, dispositions and
literal blocker evidence are bound below. No blocker is resolved or rescued.
Real claims, locks and terminals remain empty; attempts/inputs/snapshots output
paths remain absent. Real attempts consumed and environment-ready cases are zero.

The canonical v6_current_state.json stays byte-identical, at event_count=2,
PREPARATION_PLANNING_AUTHORIZED, PREPARATION_EXECUTION=NO and
lifecycle.PREPARATION_AUTHORIZED=NO. Candidate event_count=3 and execution flags
exist only in the accepted transition-result artifact. The inherited planning
descriptor ID and installation-authority reference remain unchanged. This
closure is documentary lifecycle evidence, not an event, effectivity binding,
installation authority or current registration. The external envelope remains
RUNTIME_EFFECTIVE=NO, CURRENT_REGISTRATION=PROHIBITED and AUTO_PROMOTION=NO.

## 6. Risks and unknowns

Validation establishes exact transaction/committed-evidence replay and byte
preservation. It does not requalify present-day builder/VM/firewall/network
operation, rehash the large external archive inventory, or establish scientific
results. Those frozen prerequisite limitations remain as recorded in the accepted
runtime/egress closure and historical reports. The original validator's baseline
entry assumptions intentionally remain frozen. Post-commit verification uses the
independent transaction gate without altering accepted candidate code or results.

## 7. Recommended next action

NEXT_GATE = HUMAN_PI_REVIEW_OF_COMMITTED_V6_PREPARATION_EXECUTION_TRANSITION_BASELINE.

Stop after successful post-commit verification. Any effectivity-binding,
canonical-installation or real-execution transaction requires separate Human-PI
authority. This closure recommends no automatic promotion or execution.

## 8. Exact complete accepted inventory and closure binding

The table and machine-readable binding include the manifest's own SHA. The
closure is the thirteenth committed path; its own hash is reported externally
without self-reference.

| Accepted path | SHA-256 |
| --- | --- |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/RUN_REPORT.md` | `68dc1117fd6fcda94eac59da7e471102169e6e7292b680f835c36aa634f9550d` |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/artifact_sha256.json` | `fd4f1306fd65f9f2198582751c64a114842abfd8041f0fe81f692f268d7d6f87` |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/candidate_envelope.json` | `830a411bcd5055a689c6cc374be5327bdd90b4f68a5f5d9ca13db628ae879a1b` |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/commands_run.json` | `a944c0230e8dcb68b4d5269309f471a615888c0502ea531563861be02b493b81` |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/entry_verification.json` | `1f4378012316bd1c34ac56d26f78fbbf1255b8a0e3a814ddee6d27ac4119a1eb` |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/execution_authority.json` | `f1a07a9e4eb26ebe9bd60d6ed84a06fb4f113c7eb471260aa1f0b1fb6dacc41e` |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/human_pi_request.txt` | `0146f9568763dcd1f040469c85b7bdbcb93e723a14b27a446fd7a19ec970d3e4` |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/preparation_execution_event_candidate.json` | `5460983338c0835c4c2ec030d2f58e1314874db50591ae5d0c72780288d81ecb` |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/projection_delta.json` | `221997e179f3a698c804c32699573d06979057c33fcfca6c728477c3f07ea5f2` |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/successor_descriptor_candidate.json` | `6e29d1825bbf3220f58660103761837004fb1265464501638732b9d01e1ce505` |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/validate_transition.py` | `90a37476d10470bfdbcb31f4b367f0e2bd5286ffc4b4e8d70b2df9a8249d7ebf` |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/validation_results.json` | `9ae4814cc7e509f94936a75920e05925abdab912f603985850f909ca9b305572` |

```json
{
  "accepted_event_3": {
    "canonical_payload_sha256": "368aa2581dd7a27dcea6b62a19aad7eb78d5d3ef96866ddfe322ca2dd91a840c",
    "event_id": "237d8020668f338c04065beb8557d8f25263fbfc0282003dcc5b2af67a20a50d",
    "event_sha256": "368aa2581dd7a27dcea6b62a19aad7eb78d5d3ef96866ddfe322ca2dd91a840c",
    "file_sha256": "5460983338c0835c4c2ec030d2f58e1314874db50591ae5d0c72780288d81ecb",
    "path": "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/preparation_execution_event_candidate.json",
    "previous_event_identity": {
      "event_id": "007ac4316ab6961c628ddef19202d73a0fd3859db2de30b56f27efd2cae6121c",
      "event_sha256": "27a9778775635db017a5b783c698c86b30f0c49199f6ad96fb5bc4bcfd01b84a",
      "sequence": 2
    },
    "stored_event_sha256": "5460983338c0835c4c2ec030d2f58e1314874db50591ae5d0c72780288d81ecb"
  },
  "accepted_inventory_sha256": "430718f20e778553526468d51ef9fb2472a5287893f35a2c9cbe2d247db24dd2",
  "accepted_paths_sha256": {
    "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/RUN_REPORT.md": "68dc1117fd6fcda94eac59da7e471102169e6e7292b680f835c36aa634f9550d",
    "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/artifact_sha256.json": "fd4f1306fd65f9f2198582751c64a114842abfd8041f0fe81f692f268d7d6f87",
    "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/candidate_envelope.json": "830a411bcd5055a689c6cc374be5327bdd90b4f68a5f5d9ca13db628ae879a1b",
    "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/commands_run.json": "a944c0230e8dcb68b4d5269309f471a615888c0502ea531563861be02b493b81",
    "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/entry_verification.json": "1f4378012316bd1c34ac56d26f78fbbf1255b8a0e3a814ddee6d27ac4119a1eb",
    "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/execution_authority.json": "f1a07a9e4eb26ebe9bd60d6ed84a06fb4f113c7eb471260aa1f0b1fb6dacc41e",
    "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/human_pi_request.txt": "0146f9568763dcd1f040469c85b7bdbcb93e723a14b27a446fd7a19ec970d3e4",
    "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/preparation_execution_event_candidate.json": "5460983338c0835c4c2ec030d2f58e1314874db50591ae5d0c72780288d81ecb",
    "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/projection_delta.json": "221997e179f3a698c804c32699573d06979057c33fcfca6c728477c3f07ea5f2",
    "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/successor_descriptor_candidate.json": "6e29d1825bbf3220f58660103761837004fb1265464501638732b9d01e1ce505",
    "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/validate_transition.py": "90a37476d10470bfdbcb31f4b367f0e2bd5286ffc4b4e8d70b2df9a8249d7ebf",
    "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/validation_results.json": "9ae4814cc7e509f94936a75920e05925abdab912f603985850f909ca9b305572"
  },
  "accepted_runtime_egress_closure": {
    "path": "evaluation/downstream_benchmark/V6_PREPARATION_EXECUTION_RUNTIME_AND_EGRESS_QUALIFIED_BASELINE_LIFECYCLE_CLOSURE_V1.md",
    "sha256": "a2a2d8f5fef0357fdad7960f45fad8aa74fdc8bf8728472162c1051a96a10949"
  },
  "accepted_successor_descriptor": {
    "form": "TRANSITION_RESULT_CANDIDATE",
    "inherited_effective_current_descriptor_identity": {
      "descriptor_id": "V6_EFFECTIVE_CURRENT_DESCRIPTOR_PREPARATION_PLANNING_AUTHORIZED_V1",
      "human_pi_transition": {
        "path": "evaluation/downstream_benchmark/V6_PREPARATION_PLANNING_INSTALLATION_AUTHORITY_V1.json",
        "sha256": "396db0ffa2d007e44a873b50a9af4436c1bcf1cebb970c09f78173ea6f2a3287"
      }
    },
    "path": "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/successor_descriptor_candidate.json",
    "runtime_effective": false,
    "sha256": "6e29d1825bbf3220f58660103761837004fb1265464501638732b9d01e1ce505"
  },
  "authority": {
    "acceptance": "ACCEPT_V6_PREPARATION_EXECUTION_TRANSITION_CANDIDATE",
    "canonical_installation_authorized": false,
    "effectivity_binding_authorized": false,
    "exact_instruction_sha256": "b1ca8f12247685956cd128fdd2d5b585a031655516a12389b1a3100993c4a037",
    "local_commit_authorized": true,
    "owner": "HUMAN_PI",
    "preparation_execution_authorized": false,
    "remote_publication_authorized": false,
    "scope": "EXACT_ACCEPTED_EVENT_3_AND_TRANSITION_RESULT_CANDIDATE_ONLY",
    "source": "LATEST_DIRECT_HUMAN_PI_INSTRUCTION_IN_THIS_CHAT",
    "transaction": "OPEN_V6_PREPARATION_EXECUTION_TRANSITION_LIFECYCLE_CLOSURE"
  },
  "blockers": [
    {
      "blockers": [
        {
          "category": "SETUP_REPRESENTATION",
          "lines": [
            {
              "category": "DEPENDENCY_INSTALL",
              "line": 1,
              "text": "pip install Cython"
            },
            {
              "category": "UNSUPPORTED_OR_AMBIGUOUS",
              "line": 2,
              "text": "python -mpip install -ve ."
            }
          ],
          "mechanism": "SHARED_SETUP_REPRESENTATION_REJECTS_LITERAL",
          "reason": "unsupported setup action at line 2: UNSUPPORTED_OR_AMBIGUOUS"
        }
      ],
      "case_id": "matplotlib::1",
      "census_order": 67,
      "frozen_rank": 118,
      "plan_sha256": "951d47ffd3c367e9f0a39addbd3e7fea0457e279735e129b5cb83d288ecbf563",
      "planning_disposition": "PREPARATION_PLAN_BLOCKED_SETUP_REPRESENTATION"
    },
    {
      "blockers": [
        {
          "category": "ORACLE_REPRESENTATION",
          "commands": [
            "pytest lib/matplotlib/tests/test_axes.py::test_unautoscaley;pytest lib/matplotlib/tests/test_axes.py::test_unautoscalex"
          ],
          "mechanism": "SHARED_ORACLE_PARSER_REJECTS_LITERAL",
          "reason": "subcommand 1: shell syntax or expansion is unsupported"
        }
      ],
      "case_id": "matplotlib::8",
      "census_order": 121,
      "frozen_rank": 176,
      "plan_sha256": "f820191cadeedee5e33829bc3f72f6244b73633497e214c0c61506ad6f7ac5da",
      "planning_disposition": "PREPARATION_PLAN_BLOCKED_ORACLE_REPRESENTATION"
    }
  ],
  "branch": "main",
  "canonical_predecessor": {
    "PREPARATION_EXECUTION": "NO",
    "PREPARATION_PLANNING": "YES",
    "event_count": 2,
    "path": "evaluation/downstream_benchmark/v6_current_state.json",
    "projection.lifecycle.PREPARATION_AUTHORIZED": "NO",
    "sha256": "6a9028c79aa62f90db2b2d53def32ab23bffcfa3c71d2ec30d7fa64e741e3aae",
    "state": "PREPARATION_PLANNING_AUTHORIZED"
  },
  "commit_scope": {
    "accepted_input_count": 12,
    "amend": false,
    "closure_path": "evaluation/downstream_benchmark/V6_PREPARATION_EXECUTION_TRANSITION_LIFECYCLE_CLOSURE_V1.md",
    "new_local_commit_count": 1,
    "path_count": 13,
    "paths": [
      "evaluation/downstream_benchmark/V6_PREPARATION_EXECUTION_TRANSITION_LIFECYCLE_CLOSURE_V1.md",
      "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/RUN_REPORT.md",
      "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/artifact_sha256.json",
      "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/candidate_envelope.json",
      "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/commands_run.json",
      "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/entry_verification.json",
      "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/execution_authority.json",
      "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/human_pi_request.txt",
      "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/preparation_execution_event_candidate.json",
      "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/projection_delta.json",
      "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/successor_descriptor_candidate.json",
      "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/validate_transition.py",
      "evaluation/downstream_benchmark/evidence/v6_preparation_execution_transition_v1/validation_results.json"
    ],
    "push": false,
    "required_message": "benchmark: freeze V6 preparation execution transition",
    "required_parent": "dded507b6049ad24cdf813590e2d8e8af7e9e241",
    "tag": false
  },
  "completion_status": "V6_PREPARATION_EXECUTION_TRANSITION_BASELINE_COMMITTED",
  "date": "2026-10-07",
  "enforcement_identity": "8801637324b2fa32124df8444e88f193a5be3f9c847904f2eebfb92197bc5c10",
  "entry": {
    "airos_contract_directory_exists": false,
    "airos_current_state_exists": false,
    "branch": "main",
    "exact_accepted_untracked_path_count": 12,
    "head": "dded507b6049ad24cdf813590e2d8e8af7e9e241",
    "index_empty": true,
    "live_origin_main": "dded507b6049ad24cdf813590e2d8e8af7e9e241",
    "live_ref_command": "git ls-remote --exit-code origin refs/heads/main",
    "on_disk_AGENTS_found": false,
    "preexisting_tracked_file_count": 992,
    "preexisting_tracked_inventory_sha256": "24570bbdf4a37f80cc5787422b7035a9c8361f3ef54b7bb51bd083b3c0cc5272",
    "tracked_diff_empty": true
  },
  "firewall": {
    "CANONICAL_CURRENT_STATE_MODIFIED": "NO",
    "DOWNSTREAM_REPAIR_EXECUTION_EXECUTED": "NO",
    "EFFECTIVITY_BINDING_CREATED": "NO",
    "ENVIRONMENT_READY_CASES_ESTABLISHED": 0,
    "EVENT_3_CANONICAL_EFFECTIVE": "NO",
    "GIT_PUSH": "NO",
    "IMAGE_BUILD_EXECUTED": "NO",
    "ORACLE_EXECUTED": "NO",
    "PILOT_FINAL_ALLOCATION_EXECUTED": "NO",
    "PREPARATION_EXECUTED": "NO",
    "PREPARATION_EXECUTION_CANONICAL_EFFECTIVE": "NO",
    "REAL_ATTEMPTS_CONSUMED": 0,
    "SOURCE_ACQUISITION_EXECUTED": "NO"
  },
  "frozen_transition": {
    "automatic_next_authority": false,
    "candidate_runtime_effective": false,
    "from_state": "PREPARATION_PLANNING_AUTHORIZED",
    "gate": "HUMAN_PI_AUTHORIZE_V6_PREPARATION_EXECUTION",
    "kind": "STATE_TRANSITION",
    "prior_projection_sha256": "8ef4ec1f4088c2604f72495d40659511ebc7be132f407101ec57149a8dc56458",
    "projection_delta": [
      {
        "after": "YES",
        "before": "NO",
        "path": "projection.lifecycle.PREPARATION_AUTHORIZED"
      },
      {
        "after": "YES",
        "before": "NO",
        "path": "projection.phase_authorizations.PREPARATION_EXECUTION"
      },
      {
        "after": "PREPARATION_EXECUTION_AUTHORIZED",
        "before": "PREPARATION_PLANNING_AUTHORIZED",
        "path": "projection.state"
      }
    ],
    "result_projection_sha256": "0a805c8a83d5eb2a17883b0b29509aaa29d98c91a2cc6b1a852d8668a90c9c31",
    "sequence": 3,
    "to_state": "PREPARATION_EXECUTION_AUTHORIZED"
  },
  "lifecycle": {
    "COMMITTED": "YES",
    "FROZEN": "YES",
    "HUMAN_PI_ACCEPTED": "YES",
    "PERSISTED": "YES",
    "V6_PREPARATION_EXECUTION_TRANSITION": [
      "HUMAN_PI_ACCEPTED",
      "FROZEN",
      "PERSISTED",
      "COMMITTED"
    ],
    "attestation_condition": "FULFILLED_ONLY_BY_SUCCESSFULLY_VERIFIED_EXACT_ENCLOSING_LOCAL_COMMIT"
  },
  "negative_effectivity": {
    "AUTO_PROMOTION": "NO",
    "CURRENT_REGISTRATION": "PROHIBITED",
    "EFFECTIVITY_BINDING_CREATED": "NO",
    "INDEPENDENT_ACCEPTANCE_PIN": "NOT_CONSTRUCTED",
    "INSTALLATION_AUTHORITY": "NOT_CONSTRUCTED",
    "NEW_DESCRIPTOR_ID": "NOT_CONSTRUCTED",
    "RUNTIME_EFFECTIVE": "NO"
  },
  "next_gate": "HUMAN_PI_REVIEW_OF_COMMITTED_V6_PREPARATION_EXECUTION_TRANSITION_BASELINE",
  "parent_commit": "dded507b6049ad24cdf813590e2d8e8af7e9e241",
  "preservation": {
    "all_433_case_states_unchanged": true,
    "all_641_ledger_entries_UNSTARTED_and_unclaimed": true,
    "all_cases_NOT_STARTED": true,
    "all_preexisting_tracked_bytes_and_index_identities_unchanged": true,
    "attempts_consumed": 0,
    "base_attempt_opportunities": 641,
    "case_states_canonical_sha256_before_and_after": "3f5dc8fc843028d2c973d5c082768658a51164fe49874df5fa5b2f4ee576845c",
    "census_cases": 433,
    "constructible_cases": 431,
    "environment_ready_cases": 0,
    "network_NONE_work_items": 58,
    "real_attempt_state": {
      "claims": [],
      "locks": [],
      "output_paths_present": {
        "attempts": false,
        "inputs": false,
        "snapshots": false
      },
      "terminals": []
    },
    "restricted_network_work_items": 583
  },
  "schema": "V6_PREPARATION_EXECUTION_TRANSITION_LIFECYCLE_CLOSURE_V1",
  "timezone": "Europe/Budapest",
  "unchanged_authorizations": {
    "DOWNSTREAM_REPAIR_EXECUTION": "NO",
    "IMAGE_BUILD": "NO",
    "ORACLE_EXECUTION": "NO",
    "PILOT_FINAL_ALLOCATION": "NO",
    "PREPARATION_PLANNING": "YES",
    "SOURCE_ACQUISITION": "NO"
  },
  "validation": {
    "AST_static": "PASS",
    "BOM_NUL_CR_and_trailing_whitespace": "ABSENT",
    "Ruff_check": "PASS",
    "failed_checks": 0,
    "fresh_readonly_rerun": "PASS",
    "fresh_result_bytes_identical_to_accepted_validation_results": true,
    "fresh_result_sha256": "9ae4814cc7e509f94936a75920e05925abdab912f603985850f909ca9b305572",
    "full_event_chain_replay": {
      "events": [
        {
          "event_id": "95e5ab3ca14cf2b5b47f6a1b1614e80f89f7ea8cbaf22e01245c48ed69aca0f3",
          "event_sha256": "9183d5b373128bca07018b6524e09bfbfb8cac7e38ccbea28c966f7c018d72cc",
          "file_sha256": "4ddc1a67e0ae135269877aa1754d8eeeb3424aab03b6bb38785d769390417734",
          "sequence": 1,
          "state": "CENSUS_MEMBERSHIP_ACTIVATED",
          "status": "PASS"
        },
        {
          "event_id": "007ac4316ab6961c628ddef19202d73a0fd3859db2de30b56f27efd2cae6121c",
          "event_sha256": "27a9778775635db017a5b783c698c86b30f0c49199f6ad96fb5bc4bcfd01b84a",
          "file_sha256": "b62c5d7b0a256fff1321944364816d67fd9bcb7ae1b7947964662b1fc124af6b",
          "sequence": 2,
          "state": "PREPARATION_PLANNING_AUTHORIZED",
          "status": "PASS"
        },
        {
          "event_id": "237d8020668f338c04065beb8557d8f25263fbfc0282003dcc5b2af67a20a50d",
          "event_sha256": "368aa2581dd7a27dcea6b62a19aad7eb78d5d3ef96866ddfe322ca2dd91a840c",
          "file_sha256": "5460983338c0835c4c2ec030d2f58e1314874db50591ae5d0c72780288d81ecb",
          "sequence": 3,
          "state": "PREPARATION_EXECUTION_AUTHORIZED",
          "status": "PASS"
        }
      ],
      "final_projection_sha256": "0a805c8a83d5eb2a17883b0b29509aaa29d98c91a2cc6b1a852d8668a90c9c31",
      "genesis_qualification": "HISTORICAL_EVENT_1_ONLY; NOT_REAPPLIED_TO_EVENT_3",
      "status": "PASS"
    },
    "git_diff_check": "PASS",
    "positive_checks_PASS": 23,
    "qualification": "TRANSACTION_AND_COMMITTED_EVIDENCE_REPLAY_ONLY; NO_LIVE_RUNTIME_OR_SCIENTIFIC_VALIDATION",
    "rejection_probes_PASS_REJECTED": 30,
    "strict_JSON": "PASS",
    "strict_JSON_file_count": 9,
    "strict_UTF8": "PASS",
    "strict_UTF8_file_count": 12,
    "terminal_LF_exceptions_preserved": [
      "execution_authority.json",
      "human_pi_request.txt"
    ]
  }
}
```

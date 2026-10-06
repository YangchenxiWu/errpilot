# V6 Preparation Planning Effectivity-Binding Package Lifecycle Closure V1

2026-10-06, Europe/Budapest.

1. Task summary and Human-PI acceptance

The latest direct Human-PI request accepts the exact effectivity-binding package
through ACCEPT_V6_PREPARATION_PLANNING_EFFECTIVITY_BINDING_PACKAGE and opens only
OPEN_V6_PREPARATION_PLANNING_EFFECTIVITY_BINDING_PACKAGE_LIFECYCLE_CLOSURE.
This closure binds that acceptance to the eight unchanged accepted files, their
exact stored SHA-256 identities, the required parent, and one local commit.
The embedded lifecycle target is fulfilled only after the exact enclosing commit
and all completion gates are verified. No future enclosing commit SHA is included.

The verified entry is main at
995dce6f64cebd77e6a28e4aef83e6c35374c7a5, with an empty index, no tracked changes,
and exactly the eight accepted untracked files. The actual live read-only query
returned origin/main at ee7ff4672441ddbcfba6dfaca4ed69973331e85d. The sandbox query
failed DNS; the authorized elevated read-only query succeeded. No fetch occurred.
No on-disk AGENTS.md or .airos/current_state.md/contracts directory was found in
the inspected repository/ancestor scope. The supplied global rules and attached
Human-PI request govern this transaction.

2. Files changed and accepted identities

The only new authored repository file is this closure. The eight accepted inputs
are preserved byte-for-byte and are added with it. accepted_paths_sha256 below
binds all eight files, including the original inventory's own externally observed
SHA-256. The original inventory binds seven other files and excludes its own
self-hash. commit_scope.paths lists the exact nine enclosing commit paths.
No accepted report, validator, JSON, production code, schema or canonical file is
rewritten. Historical construction-only authorizations in accepted evidence
remain exact; this closure records the new direct acceptance and persistence
transaction without changing those historical bytes.

Installation authority SHA-256:
396db0ffa2d007e44a873b50a9af4436c1bcf1cebb970c09f78173ea6f2a3287.
Effectivity-bound descriptor SHA-256:
6a9028c79aa62f90db2b2d53def32ab23bffcfa3c71d2ec30d7fa64e741e3aae.
Descriptor ID:
V6_EFFECTIVE_CURRENT_DESCRIPTOR_PREPARATION_PLANNING_AUTHORIZED_V1.
Independent acceptance-pin SHA-256:
2bf96a13d13762ab2e30dd8534808df2c2d49fc50a256c7ca272c56aeb89fbfd.
Their full paths and exact authority/pin objects are bound below.

The accepted successor source retains SHA-256
1ad034c7b49dd243d3e47563fceb53c91da75b9bd1515f2e6a8846cd21396644.
Exactly three leaf values differ: effective_current_descriptor_identity.descriptor_id,
effective_current_descriptor_identity.human_pi_transition.path, and
effective_current_descriptor_identity.human_pi_transition.sha256. The complete
before/after values are recorded below. Exactly those three literal substitutions
produce the full accepted bound-descriptor bytes; every other byte remains exact.
The controlling hash graph is authority -> descriptor -> pin, NO_HASH_CYCLE=YES.
No backward pin/descriptor reference or controlling self-hash is introduced.

Event #2 is unchanged: core ID
007ac4316ab6961c628ddef19202d73a0fd3859db2de30b56f27efd2cae6121c,
canonical payload SHA-256
27a9778775635db017a5b783c698c86b30f0c49199f6ad96fb5bc4bcfd01b84a,
stored-file SHA-256
b62c5d7b0a256fff1321944364816d67fd9bcb7ae1b7947964662b1fc124af6b.

3. Commands run and required completion gates

Read-only cat, sed, rg, Git and Python inspected the request, package validator,
accepted inventory/report/entry/results, authority, descriptor, pin, accepted
transition closure, frozen replay/phase/schema implementations and pyproject.toml.
The .airos discovery reported its absence; this was a discovery result, not a
validation failure. Principal commands and bounded operations:

```text
git status --short / --porcelain=v1 --untracked-files=all
git branch --show-current
git rev-parse HEAD
git ls-files --others --exclude-standard / --stage -z
git ls-remote --exit-code origin refs/heads/main
GIT_OPTIONAL_LOCKS=0 .venv/bin/python -B evaluation/downstream_benchmark/evidence/v6_preparation_planning_effectivity_binding_v1/validate_binding.py
.venv/bin/python -B -m ruff check --no-cache evaluation/downstream_benchmark/evidence/v6_preparation_planning_effectivity_binding_v1/validate_binding.py
.venv/bin/python -B -m ruff format --check --no-cache evaluation/downstream_benchmark/evidence/v6_preparation_planning_effectivity_binding_v1/validate_binding.py
GIT_OPTIONAL_LOCKS=0 .venv/bin/python -B <independent accepted inventory/hash/AST/strict JSON/UTF-8/byte delta checks>
git diff --check
git diff --cached --check
.venv/bin/python -B <exclusive creation of this closure only>
GIT_OPTIONAL_LOCKS=0 .venv/bin/python -B /private/tmp/errpilot-v6-binding-closure-20261006-tlgakkve/gate.py prestage
git add -- <the exact nine explicit paths in commit_scope.paths>
GIT_OPTIONAL_LOCKS=0 .venv/bin/python -B /private/tmp/errpilot-v6-binding-closure-20261006-tlgakkve/gate.py staged
git diff --cached --check
git commit -m "benchmark: freeze V6 preparation planning effectivity binding"
GIT_OPTIONAL_LOCKS=0 .venv/bin/python -B /private/tmp/errpilot-v6-binding-closure-20261006-tlgakkve/gate.py post
git ls-remote --exit-code origin refs/heads/main
```

Staged and post-commit commands are required completion gates, not claims that
future commands had run when these closure bytes were created. The independent
gate and immutable input/closure hash captures are scratch evidence outside the
repository inventory. No amend, tag, history rewrite or push is performed.

4. Tests passed / failed

The unchanged accepted package validator was rerun through its original main
entry point before creating this closure or staging. Its original read-only
audit guard forbids filesystem writes, network and non-local-read-only-Git
execution; all rejection fixtures remain in memory. Fresh validation passed all
26 positive checks and all 76 PASS_REJECTED probes (19 binding, 57 frozen
transition), with zero failures. Its complete fresh result serialization matched
the accepted validation_results.json bytes exactly.

Event #1 historical replay and event #2 replay pass. Exact frozen V1 event and
current-state schemas pass without changes. The authority object, descriptor
bytes and pin object/bytes remain exact. The eight accepted hashes, exact
three-leaf delta, acyclic hash graph and canonical preservation pass. Ruff lint
and format checks, AST, six strict duplicate-key/finite-value JSON parses, all
eight accepted UTF-8/BOM/NUL/CR/trailing-whitespace checks, and both initial Git
whitespace checks pass. Canonical compact authority/pin JSON without terminal LF
is preserved without normalization. Independent closure/static, prestage,
staged-blob, exact commit and post-commit checks are completion conditions.

The accepted validator's original main binds the pre-closure parent HEAD and
empty index. It is not rewritten or presented as a post-commit standalone pass.
Post-commit verification checks all accepted and preexisting hashes/identities,
the canonical state, committed blobs and exact commit envelope independently.
No full repository pytest, subject pytest, preparation, runtime qualification,
installer qualification or scientific validation was run.

5. Contract compliance and canonical negative effectivity

The bound descriptor retains event_count=2 and PREPARATION_PLANNING=YES.
PREPARATION_AUTHORIZED, PREPARATION_EXECUTION, SOURCE_ACQUISITION, IMAGE_BUILD,
ORACLE_EXECUTION, PILOT_FINAL_ALLOCATION and DOWNSTREAM_REPAIR_EXECUTION remain NO.
All 433 complete case states and their order remain exact, with every case
NOT_STARTED, zero consumed attempts, environment identities, oracle-plan
identities and slot outcomes. All 605 preexisting tracked file bytes and index
identities remain unchanged. The accepted plan remains 431 constructible and two
blocked; constructibility establishes no environment readiness.

matplotlib::1 retains its unresolved setup blocker, literal setup line 2
python -mpip install -ve ., and UNSUPPORTED_OR_AMBIGUOUS classification.
matplotlib::8 retains its unresolved parser blocker, the literal unsplit
semicolon oracle and empty argv. Exact original blocker identities are recorded
below; no repair, rescue, split or reclassification occurs.

The canonical current state stays at SHA-256
9295430e8573474b17bc79339c92f46044e443b9dabfe81280f9fb789d751073,
event_count=1, CENSUS_MEMBERSHIP_ACTIVATED and PREPARATION_PLANNING=NO.
The candidate's inherited runtime_authority=true and candidate_only=false fields
are preserved prospective descriptor values. The file is outside the canonical
path and is not current. Its independent accepted pin does not install it.
Canonical installation remains NO. This local lifecycle closure grants no
execution, acquisition, image, oracle or allocation authority.

6. Risks and unknowns

Both matplotlib blockers remain unresolved. Bounded replay/schema/binding and
byte-preservation evidence does not establish installer/runtime qualification,
environment readiness, scientific eligibility or a research claim. The live ref
is observed at query time and is not locked against later remote drift.
Acceptance, freezing, persistence and commit here apply only to this exact
package. Canonical installation and publication remain separate Human-PI gates.

7. Recommended next action

NEXT_GATE =
HUMAN_PI_REVIEW_OF_COMMITTED_V6_PREPARATION_PLANNING_EFFECTIVITY_BINDING_BASELINE.

Stop at that gate. The lifecycle target is
V6_PREPARATION_PLANNING_EFFECTIVITY_BINDING_PACKAGE = HUMAN_PI_ACCEPTED = FROZEN
= PERSISTED = COMMITTED, conditioned on the verified exact enclosing local commit.
CANONICAL_CURRENT_STATE_MODIFIED=NO, INSTALLATION_EXECUTED=NO,
PREPARATION_PLANNING_CANONICAL_EFFECTIVE=NO, PREPARATION_EXECUTION_AUTHORIZED=NO,
PREPARATION_EXECUTED=NO, SOURCE_ACQUISITION_AUTHORIZED=NO, ORACLE_AUTHORIZED=NO,
GIT_PUSH=NO. Clean worktree/index and exact live remote equality are required
post-commit completion conditions.

```CLOSURE_JSON
{
  "NEXT_GATE": "HUMAN_PI_REVIEW_OF_COMMITTED_V6_PREPARATION_PLANNING_EFFECTIVITY_BINDING_BASELINE",
  "accepted_identities": {
    "accepted_successor_sha256": "1ad034c7b49dd243d3e47563fceb53c91da75b9bd1515f2e6a8846cd21396644",
    "accepted_transition_closure_sha256": "7a5c6eaa3a54cca26bc040f502044a6784021e23fb75eb3e8b2a253a793cc750",
    "effectivity_bound_descriptor": {
      "descriptor_id": "V6_EFFECTIVE_CURRENT_DESCRIPTOR_PREPARATION_PLANNING_AUTHORIZED_V1",
      "path": "evaluation/downstream_benchmark/evidence/v6_preparation_planning_effectivity_binding_v1/effective_descriptor_candidate.json",
      "sha256": "6a9028c79aa62f90db2b2d53def32ab23bffcfa3c71d2ec30d7fa64e741e3aae"
    },
    "event_2": {
      "event_id": "007ac4316ab6961c628ddef19202d73a0fd3859db2de30b56f27efd2cae6121c",
      "event_sha256": "27a9778775635db017a5b783c698c86b30f0c49199f6ad96fb5bc4bcfd01b84a",
      "file_sha256": "b62c5d7b0a256fff1321944364816d67fd9bcb7ae1b7947964662b1fc124af6b"
    },
    "independent_acceptance_pin": {
      "canonical_sha256": "2bf96a13d13762ab2e30dd8534808df2c2d49fc50a256c7ca272c56aeb89fbfd",
      "path": "evaluation/downstream_benchmark/V6_PREPARATION_PLANNING_EFFECTIVE_DESCRIPTOR_ACCEPTANCE_PIN_V1.json",
      "sha256": "2bf96a13d13762ab2e30dd8534808df2c2d49fc50a256c7ca272c56aeb89fbfd"
    },
    "installation_authority": {
      "canonical_sha256": "396db0ffa2d007e44a873b50a9af4436c1bcf1cebb970c09f78173ea6f2a3287",
      "path": "evaluation/downstream_benchmark/V6_PREPARATION_PLANNING_INSTALLATION_AUTHORITY_V1.json",
      "sha256": "396db0ffa2d007e44a873b50a9af4436c1bcf1cebb970c09f78173ea6f2a3287"
    }
  },
  "accepted_inventory": {
    "accepted_input_count": 8,
    "other_artifacts_bound": 7,
    "path": "evaluation/downstream_benchmark/evidence/v6_preparation_planning_effectivity_binding_v1/artifact_sha256.json",
    "self_hash_excluded_in_original_inventory": true,
    "sha256": "02714e6992ed1acda6a8429cc1a071ce40254dd2c5fc68f19120f8189f0612f0"
  },
  "accepted_paths_sha256": {
    "evaluation/downstream_benchmark/V6_PREPARATION_PLANNING_EFFECTIVE_DESCRIPTOR_ACCEPTANCE_PIN_V1.json": "2bf96a13d13762ab2e30dd8534808df2c2d49fc50a256c7ca272c56aeb89fbfd",
    "evaluation/downstream_benchmark/V6_PREPARATION_PLANNING_INSTALLATION_AUTHORITY_V1.json": "396db0ffa2d007e44a873b50a9af4436c1bcf1cebb970c09f78173ea6f2a3287",
    "evaluation/downstream_benchmark/evidence/v6_preparation_planning_effectivity_binding_v1/RUN_REPORT.md": "f014b01862abefd52df6129615387f0456578d01d3d1746ead7f07a405b4049a",
    "evaluation/downstream_benchmark/evidence/v6_preparation_planning_effectivity_binding_v1/artifact_sha256.json": "02714e6992ed1acda6a8429cc1a071ce40254dd2c5fc68f19120f8189f0612f0",
    "evaluation/downstream_benchmark/evidence/v6_preparation_planning_effectivity_binding_v1/effective_descriptor_candidate.json": "6a9028c79aa62f90db2b2d53def32ab23bffcfa3c71d2ec30d7fa64e741e3aae",
    "evaluation/downstream_benchmark/evidence/v6_preparation_planning_effectivity_binding_v1/entry_verification.json": "0c90cedeec022333d3f5fe5ee086f7bb581c5cc8420c32d54114ff79397a488c",
    "evaluation/downstream_benchmark/evidence/v6_preparation_planning_effectivity_binding_v1/validate_binding.py": "71068378f3ecf156591fe60f7b5d818a6c5a5f61c56a6145c0c3e166cb4d5f18",
    "evaluation/downstream_benchmark/evidence/v6_preparation_planning_effectivity_binding_v1/validation_results.json": "7ba1d8c6982e58a0f1a827702ae1004c1641a956f08411329d4bfab8dc09adb3"
  },
  "authority": {
    "acceptance": "ACCEPT_V6_PREPARATION_PLANNING_EFFECTIVITY_BINDING_PACKAGE",
    "canonical_installation_authorized_by_this_closure": false,
    "event_2_modification_authorized": false,
    "human_pi_request": {
      "path": "/Users/wuyangchenxi/.codex/attachments/eea70ae6-149b-4dea-aa73-a52e4f093094/已粘贴的文本.txt",
      "sha256": "d6e0ae1a604cc6b90dfeef5fe50ec718e31ca6467d6804852551c995fb968c78"
    },
    "owner": "HUMAN_PI",
    "preparation_execution_authorized": false,
    "remote_publication_authorized": false,
    "scope": "EXACT_ACCEPTED_EIGHT_FILE_EFFECTIVITY_BINDING_PACKAGE_AND_ONE_CLOSURE_ONLY",
    "source": "LATEST_DIRECT_ATTACHED_HUMAN_PI_INSTRUCTION_IN_THIS_CHAT",
    "transaction": "OPEN_V6_PREPARATION_PLANNING_EFFECTIVITY_BINDING_PACKAGE_LIFECYCLE_CLOSURE"
  },
  "blockers": [
    {
      "case_id": "matplotlib::1",
      "census_order": 67,
      "frozen_rank": 118,
      "literal_setup_line": "python -mpip install -ve .",
      "mechanism": "SHARED_SETUP_REPRESENTATION_REJECTS_LITERAL",
      "plan_sha256": "951d47ffd3c367e9f0a39addbd3e7fea0457e279735e129b5cb83d288ecbf563",
      "planning_disposition": "PREPARATION_PLAN_BLOCKED_SETUP_REPRESENTATION",
      "preserved_first_setup_line": "pip install Cython",
      "reason": "unsupported setup action at line 2: UNSUPPORTED_OR_AMBIGUOUS",
      "resolved": false,
      "setup_classification": "UNSUPPORTED_OR_AMBIGUOUS",
      "setup_line_number": 2
    },
    {
      "argv": [],
      "case_id": "matplotlib::8",
      "census_order": 121,
      "frozen_rank": 176,
      "literal_oracle_line": "pytest lib/matplotlib/tests/test_axes.py::test_unautoscaley;pytest lib/matplotlib/tests/test_axes.py::test_unautoscalex",
      "mechanism": "SHARED_ORACLE_PARSER_REJECTS_LITERAL",
      "oracle_status": "UNRESOLVED_UNSAFE_OR_UNRECOGNIZED_COMMAND_V1_1",
      "plan_sha256": "f820191cadeedee5e33829bc3f72f6244b73633497e214c0c61506ad6f7ac5da",
      "planning_disposition": "PREPARATION_PLAN_BLOCKED_ORACLE_REPRESENTATION",
      "reason": "subcommand 1: shell syntax or expansion is unsupported",
      "resolved": false
    }
  ],
  "bound_descriptor_semantics": {
    "DOWNSTREAM_REPAIR_EXECUTION": "NO",
    "IMAGE_BUILD": "NO",
    "ORACLE_EXECUTION": "NO",
    "PILOT_FINAL_ALLOCATION": "NO",
    "PREPARATION_AUTHORIZED": "NO",
    "PREPARATION_EXECUTION": "NO",
    "PREPARATION_PLANNING": "YES",
    "SOURCE_ACQUISITION": "NO",
    "candidate_is_canonical_current": false,
    "event_2_unchanged": true,
    "event_count": 2,
    "runtime_authority_field_preserved": true
  },
  "branch": "main",
  "canonical_predecessor": {
    "PREPARATION_PLANNING": "NO",
    "event_count": 1,
    "path": "evaluation/downstream_benchmark/v6_current_state.json",
    "sha256": "9295430e8573474b17bc79339c92f46044e443b9dabfe81280f9fb789d751073",
    "state": "CENSUS_MEMBERSHIP_ACTIVATED"
  },
  "commit_scope": {
    "accepted_input_count": 8,
    "amend": false,
    "closure_path": "evaluation/downstream_benchmark/V6_PREPARATION_PLANNING_EFFECTIVITY_BINDING_PACKAGE_LIFECYCLE_CLOSURE_V1.md",
    "new_local_commit_count": 1,
    "path_count": 9,
    "paths": [
      "evaluation/downstream_benchmark/V6_PREPARATION_PLANNING_EFFECTIVE_DESCRIPTOR_ACCEPTANCE_PIN_V1.json",
      "evaluation/downstream_benchmark/V6_PREPARATION_PLANNING_EFFECTIVITY_BINDING_PACKAGE_LIFECYCLE_CLOSURE_V1.md",
      "evaluation/downstream_benchmark/V6_PREPARATION_PLANNING_INSTALLATION_AUTHORITY_V1.json",
      "evaluation/downstream_benchmark/evidence/v6_preparation_planning_effectivity_binding_v1/RUN_REPORT.md",
      "evaluation/downstream_benchmark/evidence/v6_preparation_planning_effectivity_binding_v1/artifact_sha256.json",
      "evaluation/downstream_benchmark/evidence/v6_preparation_planning_effectivity_binding_v1/effective_descriptor_candidate.json",
      "evaluation/downstream_benchmark/evidence/v6_preparation_planning_effectivity_binding_v1/entry_verification.json",
      "evaluation/downstream_benchmark/evidence/v6_preparation_planning_effectivity_binding_v1/validate_binding.py",
      "evaluation/downstream_benchmark/evidence/v6_preparation_planning_effectivity_binding_v1/validation_results.json"
    ],
    "push": false,
    "required_message": "benchmark: freeze V6 preparation planning effectivity binding",
    "required_parent": "995dce6f64cebd77e6a28e4aef83e6c35374c7a5",
    "tag": false
  },
  "completion_gates": {
    "all_accepted_and_preexisting_bytes_preserved_required": true,
    "exact_nine_path_local_commit_required": true,
    "exact_staged_bytes_required": true,
    "parent_and_message_verification_required": true,
    "post_commit_clean_worktree_and_index_required": true,
    "post_commit_live_origin_main_required": "ee7ff4672441ddbcfba6dfaca4ed69973331e85d"
  },
  "completion_status": "V6_PREPARATION_PLANNING_EFFECTIVITY_BINDING_BASELINE_COMMITTED",
  "date": "2026-10-06",
  "entry": {
    "airos_contract_directory_exists": false,
    "airos_current_state_exists": false,
    "branch": "main",
    "exact_accepted_untracked_path_count": 8,
    "head": "995dce6f64cebd77e6a28e4aef83e6c35374c7a5",
    "index_empty": true,
    "live_origin_main": "ee7ff4672441ddbcfba6dfaca4ed69973331e85d",
    "live_ref_command": "git ls-remote --exit-code origin refs/heads/main",
    "on_disk_AGENTS_found": false,
    "repository": "/Users/wuyangchenxi/errpilot",
    "tracked_diff_empty": true
  },
  "exact_acceptance_pin": {
    "HUMAN_PI_ACCEPTED": "YES",
    "path": "evaluation/downstream_benchmark/v6_current_state.json",
    "sha256": "6a9028c79aa62f90db2b2d53def32ab23bffcfa3c71d2ec30d7fa64e741e3aae"
  },
  "exact_authorized_delta": [
    {
      "after": "V6_EFFECTIVE_CURRENT_DESCRIPTOR_PREPARATION_PLANNING_AUTHORIZED_V1",
      "before": "V6_EFFECTIVE_CURRENT_DESCRIPTOR_CENSUS_MEMBERSHIP_ACTIVATED_V1",
      "path": "effective_current_descriptor_identity.descriptor_id"
    },
    {
      "after": "evaluation/downstream_benchmark/V6_PREPARATION_PLANNING_INSTALLATION_AUTHORITY_V1.json",
      "before": "evaluation/downstream_benchmark/V6_CENSUS_MEMBERSHIP_INSTALLATION_AUTHORITY_V1.json",
      "path": "effective_current_descriptor_identity.human_pi_transition.path"
    },
    {
      "after": "396db0ffa2d007e44a873b50a9af4436c1bcf1cebb970c09f78173ea6f2a3287",
      "before": "359be257db9b355222d71d3e72e9234e736331d5e1a6d079f883b572f85a7458",
      "path": "effective_current_descriptor_identity.human_pi_transition.sha256"
    }
  ],
  "exact_installation_authority": {
    "HUMAN_PI_ACCEPTED": "YES",
    "canonical_path": "evaluation/downstream_benchmark/v6_current_state.json",
    "expected_predecessor_sha256": "9295430e8573474b17bc79339c92f46044e443b9dabfe81280f9fb789d751073",
    "operation": "COMPARE_AND_INSTALL_EXACT_ACCEPTED_SUCCESSOR_AT_CANONICAL_PATH",
    "owner": "HUMAN_PI",
    "path": "evaluation/downstream_benchmark/V6_PREPARATION_PLANNING_INSTALLATION_AUTHORITY_V1.json",
    "scope": "EXACT_PREPARATION_PLANNING_TRANSITION_INSTALLATION_ONLY"
  },
  "firewall": {
    "CANONICAL_CURRENT_STATE_MODIFIED": "NO",
    "CANONICAL_INSTALLATION_AUTHORIZED_BY_THIS_CLOSURE": "NO",
    "DOWNSTREAM_REPAIR_EXECUTION_AUTHORIZED": "NO",
    "DOWNSTREAM_REPAIR_EXECUTION_EXECUTED": "NO",
    "EVENT_2_MODIFIED": "NO",
    "GIT_PUSH": "NO",
    "IMAGE_BUILD_AUTHORIZED": "NO",
    "IMAGE_BUILD_EXECUTED": "NO",
    "INSTALLATION_EXECUTED": "NO",
    "MATERIALIZATION_AUTHORIZED": "NO",
    "MATERIALIZATION_EXECUTED": "NO",
    "NEW_EVENT_CREATED": "NO",
    "ORACLE_AUTHORIZED": "NO",
    "ORACLE_EXECUTED": "NO",
    "PILOT_FINAL_ALLOCATION_AUTHORIZED": "NO",
    "PILOT_FINAL_ALLOCATION_EXECUTED": "NO",
    "PREPARATION_EXECUTED": "NO",
    "PREPARATION_EXECUTION_AUTHORIZED": "NO",
    "PREPARATION_PLANNING_CANONICAL_EFFECTIVE": "NO",
    "SOURCE_ACQUISITION_AUTHORIZED": "NO",
    "SOURCE_ACQUISITION_EXECUTED": "NO"
  },
  "hash_graph": {
    "NO_HASH_CYCLE": "YES",
    "edges": [
      [
        "authority",
        "descriptor"
      ],
      [
        "descriptor",
        "pin"
      ]
    ]
  },
  "lifecycle": {
    "COMMITTED": "YES",
    "FROZEN": "YES",
    "HUMAN_PI_ACCEPTED": "YES",
    "PERSISTED": "YES",
    "V6_PREPARATION_PLANNING_EFFECTIVITY_BINDING_PACKAGE": [
      "HUMAN_PI_ACCEPTED",
      "FROZEN",
      "PERSISTED",
      "COMMITTED"
    ],
    "attestation_condition": "FULFILLED_ONLY_BY_SUCCESSFULLY_VERIFIED_EXACT_ENCLOSING_LOCAL_COMMIT"
  },
  "parent_commit": "995dce6f64cebd77e6a28e4aef83e6c35374c7a5",
  "preservation": {
    "accepted_package_bytes_unchanged": true,
    "all_case_states_and_order_unchanged": true,
    "all_cases_NOT_STARTED": true,
    "all_preexisting_tracked_bytes_and_index_identities_unchanged": true,
    "case_state_count": 433,
    "case_states_canonical_sha256_before_and_after": "3f5dc8fc843028d2c973d5c082768658a51164fe49874df5fa5b2f4ee576845c",
    "consumed_attempts": 0,
    "environment_identities": 0,
    "environment_ready_cases": 0,
    "matplotlib_blockers_unchanged": true,
    "oracle_plan_identities": 0,
    "preexisting_tracked_file_count": 605,
    "preexisting_tracked_inventory_sha256": "0f3912a7fad3924a0c5570828ba91006b65ff61a234603f3291df78d524f405d",
    "slot_outcomes": 0
  },
  "schema": "V6_PREPARATION_PLANNING_EFFECTIVITY_BINDING_PACKAGE_LIFECYCLE_CLOSURE_V1",
  "timezone": "Europe/Budapest",
  "validation": {
    "AST": "PASS",
    "Ruff_check": "PASS",
    "Ruff_format_check": "PASS",
    "UTF8_BOM_NUL_CR_and_trailing_whitespace": "PASS",
    "authority_object_exact": "PASS",
    "binding_rejection_probes_PASS_REJECTED": 19,
    "descriptor_bytes_exact": "PASS",
    "event_chain_replay": "PASS",
    "exact_eight_file_hashes": "PASS",
    "exact_three_literal_byte_substitutions": "PASS",
    "failed_checks": 0,
    "fresh_readonly_original_main_rerun": "PASS",
    "fresh_result_bytes_identical_to_accepted_validation_results": true,
    "frozen_current_state_schema": "PASS",
    "frozen_transition_rejection_probes_PASS_REJECTED": 57,
    "git_cached_diff_check_before_stage": "PASS",
    "git_diff_check": "PASS",
    "pin_object_and_bytes_exact": "PASS",
    "positive_checks_PASS": 26,
    "qualification": "BOUNDED_PACKAGE_REPLAY_SCHEMA_AND_BINDING_AUDIT_ONLY; NO_INSTALLER_RUNTIME_SUBJECT_OR_SCIENTIFIC_VALIDATION",
    "rejection_probes_PASS_REJECTED": 76,
    "strict_JSON": "PASS",
    "strict_JSON_file_count": 6,
    "validator_path": "evaluation/downstream_benchmark/evidence/v6_preparation_planning_effectivity_binding_v1/validate_binding.py"
  }
}
```

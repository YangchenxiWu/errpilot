# V6 capacity successor run specification candidate

Specification ID: `EP-DBRS-6-CAPACITY`.

Status: CONTRACT_CANDIDATE_ONLY. This saved candidate has no runtime authority.
CONTRACT_ACCEPTED = NO; CONTRACT_FROZEN = NO; CONTRACT_PERSISTED = NO; CONTRACT_COMMITTED = NO; CONTRACT_PUBLISHED = NO.
V6_ACTIVATED = NO; CENSUS_MEMBERSHIP_EFFECTIVE = NO; PREPARATION_AUTHORIZED = NO; ORACLE_AUTHORIZED = NO.

The latest direct Human-PI instruction accepts the exact finalized design and opens only
OPEN_V6_SUCCESSOR_CONTRACT_CONSTRUCTION. The bound historical design files retain their earlier
review status. Their bytes are immutable. This transaction does not accept this successor contract.

## Exact predecessor and accepted-design bindings

- `PROTOCOL.md`: `34e014a07821dc9dca52178874eef0b847aee7f048071fb4920864ae5d3bee93`.
- `RUN_SPEC_V1.md`: `29ab6f78739d0eeea1c2a774e62e2d133f173e160c3d247407970a80726f4406`.
- `SCREENING_SPEC_V1.md`: `a7f3cd5e73d6c733f560456d9f3949be18deca9b295ffb4ef2ae087af7e89db3`.
- `D1–D8 decision`: `2d30ba01c22a6531ab1480140dbef20d2878ba94c8ac2d7d7aa01cc85514e6f2`.
- `accepted finalized design`: `f2e17649236d28d1712192146039370a6e0542084a82685d03f2d4d227064163`.
- Predecessor HEAD: `26a9264105f303dc0101f74c9315c41ab1c9e265`.
- BugsInPy commit/tree: `11c5f1eea954a42132cfd06bf257766a7963e0fd` / `d00ce0495ba73abe50317599f48bced3c9afe4b3`.
- Candidate universe: `78208adf610a50542be6dfbd03a9b25960ba0b5cfc80768b08ffe7a4c78f3b8c`; seed `20260922`.
- Full predecessor digest closure: `1afc64237645524ac1954539b1991ba5a8cbdedeebaf19df3c9669551091b622` (201 exact artifact bindings).

## Inherited downstream experiment contract

All non-superseded PROTOCOL.md and RUN_SPEC_V1.md requirements remain mandatory: unchanged
question and Python CLI/pytest scope, identical task bytes, paired RAW/ERRPILOT treatment,
exact frozen downstream Codex identity, no fallback, permission/isolation boundaries,
1,200-second repair budget, immutable environments/protected manifests, objective verifier,
instrumentation and NA policy, contamination controls, failure taxonomy, pre-run gates and
versioning. The architect model in this request does not alter the downstream agent.
The machine section pins every inherited runtime/representation/build/executor specification.
Legacy V5 execution authority cannot authorize V6. No CLI availability or real execution
qualification is asserted here; every inherited pre-run/publication gate still applies.

## D7 exact prospective pilot reservation

Freeze this rule before any V6 outcome under a separate freeze gate. Input is the immutable
combined eligible pool. Reject duplicate canonical keys or case IDs, noncanonical identity
strings, unqualified evidence or ambiguous cutoff. If eligible count is below 28, BLOCK before
pilot selection. For each candidate use its existing canonical source_project, bugsinpy_bug_id
and case_id strings without trimming, case folding or numeric conversion. Encode exactly:

`20260922|pilot|<source_project>|<bugsinpy_bug_id>|<case_id>`

Compute SHA-256 of UTF-8 and sort by lowercase hex digest, then canonical UTF-8 byte sequences
source_project, bugsinpy_bug_id, case_id. Reserve the first four. No pilot project cap or combined
pilot/final cap. No final-feasibility lookahead, swap, reseed, promotion or reselection.
Permanently exclude the four pilots from all final-selection inputs; outcomes cannot affect
selection. This construction specifies the algorithm but computes no pilot digests or IDs.

## Unchanged final, robustness and condition algorithms

Only after separately authorized prospective pilot reservation apply the predecessor final
algorithm to the remaining frozen input: SHA-256 UTF-8 of
`20260922|final|<source_project>|<bugsinpy_bug_id>|<case_id>`, sort by lowercase digest then
canonical UTF-8 key fields, traverse, skip projects already at four, stop at 24. Verify cap four
and at least six projects. After reservation, counts n_j must satisfy sum(min(4,n_j)) >= 24 and
at least six represented projects. Failure is BLOCK_WITHOUT_PILOT_RESELECTION. No changed
seed, replacement, refreshed cutoff or discretionary sample adjustment is allowed.

For the 24 final cases, sort SHA-256 of `20260922|robustness|<case_id>` then case_id, first six.
Those six get two extra repetitions per condition. Paired condition order uses the low bit of
the first byte of SHA-256 of `20260922|order|<case_id>|<repetition_index>`: zero RAW first,
one ERRPILOT first. Every condition/repetition starts independently from fresh buggy state.
These are contract rules, with no actual reservation, allocation or session performed here.

## Normative machine contract

<!-- BEGIN CONTRACT_JSON -->
```json
{
  "accepted_D1_D8": {
    "D1": {
      "bridge": "V6_PREDECESSOR_EVIDENCE_BRIDGE_V1",
      "current_state": "V6_CAPACITY_CURRENT_STATE_V1",
      "decision": "RETAIN_CANDIDATE_IDENTIFIERS_PLUS_EXPLICIT_SCHEMAS",
      "event": "V6_CAPACITY_STATE_EVENT_V1",
      "initial_skip_lineage": "ACCEPT_31_LABELED_REPLAYS_PLUS_402_LITERAL_ROWS",
      "lifecycle": "V6_CENSUS_LIFECYCLE_V1",
      "pool": "V6_RECONSIDERATION_POOL_V1",
      "predecessor_binding": "EXACT_DIGESTS_AND_NARROW_SUPERSESSION_RECORD",
      "protocol": "EP-DBP-6-CAPACITY",
      "run_spec": "EP-DBRS-6-CAPACITY",
      "screening_spec": "EP-BIPS-6-CENSUS"
    },
    "D2": {
      "batch_admission_authority": "NONE",
      "decision": "ONE_LOGICAL_433_MEMBER_CENSUS",
      "later_membership_depends_on_outcomes": "NO",
      "stop_at_28_eligible": "NO"
    },
    "D3": {
      "decision": "NO_GOVERNED_BATCH_SEMANTICS",
      "dispatch_order": "ORIGINAL_FROZEN_RANK_ASCENDING",
      "runtime_chunks_have_scientific_identity": "NO"
    },
    "D4": {
      "ACCEPTED_HELD_UNRESOLVED": "ADMINISTRATIVE_ADJUDICATION_STATE_ONLY",
      "ACCEPTED_HELD_UNRESOLVED_AUTOMATIC_RETRY": "NO",
      "ACCEPTED_HELD_UNRESOLVED_IS_ELIGIBLE": "NO",
      "ACCEPTED_HELD_UNRESOLVED_IS_SCIENTIFIC_FAILURE": "NO",
      "automatic_retry": "NO",
      "decision": "INHERIT_ORTHOGONAL_VOCABULARY_WITH_ACCEPTED_HELD_UNRESOLVED",
      "new_canonical_failure_reasons": "NONE",
      "unaccounted_or_unadjudicated_work_blocks_closure": "YES"
    },
    "D5": {
      "canonical_descriptor": "v6_current_state.json",
      "competing_current_authorities": "NONE",
      "csv_authority": "DERIVED_ONLY",
      "current_descriptor_advances_only_via_authorized_state_transition": "YES",
      "decision": "CANONICAL_JSON_DESCRIPTOR_WITH_APPEND_ONLY_HASH_LINKED_EVENTS",
      "descriptor_event_disagreement": "BLOCK",
      "historical_candidate_or_proposal_descriptor_is_runtime_authority": "NO",
      "runtime_consumers_must_bind_exact_current_descriptor_identity": "YES"
    },
    "D6": {
      "applicable_execution_publication_gates": "RETAIN",
      "combined_pool_input_freeze_is_immutable_for_that_allocation_cycle": "YES",
      "cutoff_refresh": "NO",
      "decision": "FOUR_STATE_INTEGRATION_AT_FIRST_COMBINED_POOL_INPUT_FREEZE",
      "late_inclusion": "NO",
      "remote_published_required_for_integration": "NO",
      "required_lifecycle": [
        "HUMAN_PI_ACCEPTED",
        "FROZEN",
        "PERSISTED",
        "COMMITTED"
      ],
      "seven_track_head": "FIXED_WITH_ACCEPTED_CENSUS_CLOSURE_SNAPSHOT"
    },
    "D7": {
      "decision": "HASH_SEED_PILOT_RESERVATION",
      "digest_input": "20260922|pilot|<source_project>|<bugsinpy_bug_id>|<case_id>",
      "final_algorithm": "UNCHANGED_PREDECESSOR",
      "final_feasibility_lookahead": "NO",
      "infeasible_behavior": "BLOCK_WITHOUT_PILOT_RESELECTION",
      "pilot_count": 4,
      "pilot_exclusion": "PERMANENT",
      "pilot_project_cap": "NONE",
      "pilot_promotion_to_final": "PROHIBITED",
      "pilot_reseed": "PROHIBITED",
      "pilot_swap": "PROHIBITED",
      "reserve": "FIRST_4_FROM_FROZEN_COMBINED_ELIGIBLE_POOL",
      "rule_freeze_before_any_V6_outcome": "YES",
      "seed": 20260922,
      "sort": "LOWERCASE_SHA256_THEN_UTF8_SOURCE_PROJECT_BUG_ID_CASE_ID"
    },
    "D8": {
      "automatic_downstream_authority": "NONE",
      "decision": "PRIMARY_STATUS_PLUS_ORTHOGONAL_RESOLUTION_QUALIFIERS",
      "precedence": [
        "CLOSURE_BLOCKED",
        "INSUFFICIENT_ELIGIBLE_CAPACITY",
        "ALLOCATION_RULE_UNRESOLVED",
        "PROJECT_DIVERSITY_INFEASIBLE",
        "ALLOCATION_AUTHORITY_REQUIRED"
      ],
      "primary_statuses": [
        "V6_CENSUS_COMPLETE_ALLOCATION_AUTHORITY_REQUIRED",
        "V6_CENSUS_EXHAUSTED_INSUFFICIENT_ELIGIBLE_CAPACITY",
        "V6_CENSUS_EXHAUSTED_PROJECT_DIVERSITY_INFEASIBLE",
        "V6_CENSUS_COMPLETE_ALLOCATION_RULE_UNRESOLVED",
        "V6_CENSUS_CLOSURE_BLOCKED"
      ],
      "qualifiers": [
        "V6_CENSUS_COMPLETE_WITH_UNRESOLVED_INFRASTRUCTURE",
        "V6_PREPARATION_EXHAUSTED_WITH_NONSCIENTIFIC_DISPOSITIONS"
      ]
    }
  },
  "allocation_invariants": {
    "condition_order_input": "20260922|order|<case_id>|<repetition_index>",
    "condition_order_rule": "low bit first byte; 0 RAW first, 1 ERRPILOT first",
    "final_algorithm": "traverse frozen eligible non-pilot snapshot; accept unless project already has four; stop at 24; fail closed if impossible",
    "final_count": 24,
    "final_digest_input": "20260922|final|<source_project>|<bugsinpy_bug_id>|<case_id>",
    "final_sample_project_cap": 4,
    "final_seed": 20260922,
    "final_sort": [
      "digest",
      "source_project",
      "bugsinpy_bug_id",
      "case_id"
    ],
    "minimum_final_projects": 6,
    "pilot_count": 4,
    "pilot_outcomes_affect_selection": false,
    "pilot_permanent_final_exclusion": true,
    "required_total": 28,
    "robustness_count": 6,
    "robustness_digest_input": "20260922|robustness|<case_id>",
    "robustness_sort": [
      "digest",
      "case_id"
    ]
  },
  "candidate_only": true,
  "conditions": [
    "RAW",
    "ERRPILOT"
  ],
  "construction_authority": {
    "path": "evaluation/downstream_benchmark/evidence/v6_successor_contract_construction_v1/entry_verification.json",
    "sha256": "6da22cfd90d9ec80044df7c04bcc269984b73d33eb134d147ef584e9c99116d6"
  },
  "downstream_agent": {
    "cli_sha256": "4f85982624b3898c8991cb80c0981b2aa71070e3537046c9a95950318a95afcc",
    "cli_version": "0.154.0",
    "live_identity_gate": "PRE_RUN_IDENTITY_GATE_REQUIRED",
    "model": "gpt-5.6-sol",
    "reasoning_effort": "xhigh"
  },
  "downstream_authority": "NONE",
  "inherit_by_exact_digest": {
    "ENVIRONMENT_BUILD_SPEC_V1.md": {
      "path": "evaluation/downstream_benchmark/ENVIRONMENT_BUILD_SPEC_V1.md",
      "sha256": "570585eb42712936fa67f72f1ae686375c591ffa4dd14e650335d0db614ab7ca"
    },
    "ENVIRONMENT_MATERIALIZER_V1.md": {
      "path": "evaluation/downstream_benchmark/ENVIRONMENT_MATERIALIZER_V1.md",
      "sha256": "7ea6f0f93f8edafdc7fdd534fd74dcee2c6dc7e354ee7d3c0f2495c7d4443196"
    },
    "ORACLE_REPRESENTATION_V1.md": {
      "path": "evaluation/downstream_benchmark/ORACLE_REPRESENTATION_V1.md",
      "sha256": "625b656495b5f1174ea1f4a07f872a42112a0be839b47c3db884dcd103a87f52"
    },
    "PROTOCOL.md": {
      "path": "evaluation/downstream_benchmark/PROTOCOL.md",
      "sha256": "34e014a07821dc9dca52178874eef0b847aee7f048071fb4920864ae5d3bee93"
    },
    "RUN_SPEC_V1.md": {
      "path": "evaluation/downstream_benchmark/RUN_SPEC_V1.md",
      "sha256": "29ab6f78739d0eeea1c2a774e62e2d133f173e160c3d247407970a80726f4406"
    },
    "SCREENING_EXECUTOR_V1.md": {
      "path": "evaluation/downstream_benchmark/SCREENING_EXECUTOR_V1.md",
      "sha256": "eb98361027989dc626360c2d7d1f308df720201c47bd7e579f6d30c2c6353eee"
    },
    "SCREENING_RUNTIME_V1.md": {
      "path": "evaluation/downstream_benchmark/SCREENING_RUNTIME_V1.md",
      "sha256": "235b404dd32da91f28c303922ce7acfc8f58611cd78f3c365d583cb2572bb41f"
    },
    "SCREENING_SPEC_V1.md": {
      "path": "evaluation/downstream_benchmark/SCREENING_SPEC_V1.md",
      "sha256": "a7f3cd5e73d6c733f560456d9f3949be18deca9b295ffb4ef2ae087af7e89db3"
    },
    "SOURCE_SNAPSHOT_SYMLINK_V2.md": {
      "path": "evaluation/downstream_benchmark/SOURCE_SNAPSHOT_SYMLINK_V2.md",
      "sha256": "dc6f065fc04785122e203b71c2805dc5bba94d21a8ee6e19d4c7f110c7288c79"
    }
  },
  "legacy_execution_authority_applies_to_v6": false,
  "minimum_eligible_before_pilot": 28,
  "pilot": {
    "decision": "HASH_SEED_PILOT_RESERVATION",
    "digest_input": "20260922|pilot|<source_project>|<bugsinpy_bug_id>|<case_id>",
    "final_algorithm": "UNCHANGED_PREDECESSOR",
    "final_feasibility_lookahead": "NO",
    "infeasible_behavior": "BLOCK_WITHOUT_PILOT_RESELECTION",
    "pilot_count": 4,
    "pilot_exclusion": "PERMANENT",
    "pilot_project_cap": "NONE",
    "pilot_promotion_to_final": "PROHIBITED",
    "pilot_reseed": "PROHIBITED",
    "pilot_swap": "PROHIBITED",
    "reserve": "FIRST_4_FROM_FROZEN_COMBINED_ELIGIBLE_POOL",
    "rule_freeze_before_any_V6_outcome": "YES",
    "seed": 20260922,
    "sort": "LOWERCASE_SHA256_THEN_UTF8_SOURCE_PROJECT_BUG_ID_CASE_ID"
  },
  "pilot_reselection": "PROHIBITED",
  "predecessor": {
    "accepted_exclusions": 39,
    "admissions": 67,
    "candidate_universe_sha256": "78208adf610a50542be6dfbd03a9b25960ba0b5cfc80768b08ffe7a4c78f3b8c",
    "census_rows": 501,
    "hash_inventory": {
      "path": "/Users/wuyangchenxi/errpilot/evaluation/downstream_benchmark/evidence/v6_protocol_design_v1/predecessor_artifact_sha256.json",
      "sha256": "1afc64237645524ac1954539b1991ba5a8cbdedeebaf19df3c9669551091b622"
    },
    "head": "26a9264105f303dc0101f74c9315c41ab1c9e265",
    "outcome_counts": {
      "eligible": 9,
      "infrastructure_unresolved": 7,
      "scientific_ineligible": 12
    },
    "protocol": {
      "path": "/Users/wuyangchenxi/errpilot/evaluation/downstream_benchmark/PROTOCOL.md",
      "sha256": "34e014a07821dc9dca52178874eef0b847aee7f048071fb4920864ae5d3bee93"
    },
    "ranked_rows": 500,
    "run_spec": {
      "path": "/Users/wuyangchenxi/errpilot/evaluation/downstream_benchmark/RUN_SPEC_V1.md",
      "sha256": "29ab6f78739d0eeea1c2a774e62e2d133f173e160c3d247407970a80726f4406"
    },
    "screened_cases": 28,
    "screening_spec": {
      "path": "/Users/wuyangchenxi/errpilot/evaluation/downstream_benchmark/SCREENING_SPEC_V1.md",
      "sha256": "a7f3cd5e73d6c733f560456d9f3949be18deca9b295ffb4ef2ae087af7e89db3"
    },
    "seed": 20260922,
    "source_commit": "11c5f1eea954a42132cfd06bf257766a7963e0fd",
    "source_tree": "d00ce0495ba73abe50317599f48bced3c9afe4b3"
  },
  "publication_gates": "RETAIN_APPLICABLE_DOWNSTREAM_EXECUTION_GATES",
  "repair_timeout_seconds": 1200,
  "runtime_authority": false,
  "schema": "EP-DBRS-6-CAPACITY",
  "selection_authorized": false,
  "task_instruction_sha256": "0350885984c9dff5202f66e5cbba04be49982de42e2d14b1e1e7b0db0a60fb0d",
  "unresolved_seven": {
    "applicable_execution_publication_gates": "RETAIN",
    "case_ids": [
      "matplotlib::17",
      "matplotlib::11",
      "matplotlib::29",
      "matplotlib::21",
      "PySnooper::1",
      "PySnooper::3",
      "PySnooper::2"
    ],
    "cutoff": "FIRST_COMBINED_POOL_INPUT_FREEZE",
    "cutoff_refresh": false,
    "late_inclusion": false,
    "one_effective_accepted_outcome_per_case": true,
    "prerequisite_to_census": false,
    "remote_published_required_for_integration": false,
    "required_lifecycle": [
      "HUMAN_PI_ACCEPTED",
      "FROZEN",
      "PERSISTED",
      "COMMITTED"
    ],
    "separate_versioned_authority_and_exact_supersession_required": true,
    "seven_track_head": "FIXED_WITH_ACCEPTED_CENSUS_CLOSURE_SNAPSHOT"
  }
}
```
<!-- END CONTRACT_JSON -->

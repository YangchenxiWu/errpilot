# V6 capacity successor protocol candidate

Specification ID: `EP-DBP-6-CAPACITY`.

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

## Prospective architecture and narrow supersession

V6_FINITE_SAME_UNIVERSE_CENSUS_WITH_EVIDENCE_CONTINUITY retains 24 final cases plus
4 permanently separate pilots, final cap 4 and minimum 6 final projects. Only the
original 433 never-admitted historical SKIP_PROJECT_CAP cases become prospective census
members under a later activation gate. Preserve the frozen ranked universe and seed.
One logical census covers all 433; no admission/preparation project cap, governed batch
semantics, outcome-dependent later membership or stopping when 28 become eligible.
Dispatch follows original frozen rank ascending. Runtime chunks carry no scientific identity.

The prospective supersession is limited to legacy SCREENING_SPEC D/J/M admission caps,
forward cursor, ten-admission expansion and the terminal cap-skip rule for these 433.
Historical V1/V5 rows and design/finalization artifacts remain valid under their recorded
versions. Accepted D1–D8 resolves only its named proposal alternatives. All other inherited
requirements remain bound; unlisted contradictions BLOCK and return to Human PI.

## Predecessor continuity

The ranked partition is 9 grandfathered eligible + 12 closed scientific rejections +
7 infrastructure-unresolved + 39 closed accepted pre-eligibility exclusions + 433 prospective
cap skips = 500. Unranked keras::12 remains excluded. The bridge binds original checkpoints,
ledger rows and outcomes by digest and row key. No raw evidence is copied as new V6 evidence.
The nine need no capacity rerun; the twelve receive no rescue; the 39 are never reopened.
The seven remain in a separate versioned repair/rerun track, outside V6 census execution.

## D6 immutable integration

The first immutable combined eligible-pool input freeze is the integration cutoff. An accepted
census-closure snapshot fixes the exact seven-track head, which cannot be refreshed between
closure and freeze. Include only effective eligible outcomes at that head that already satisfy
HUMAN_PI_ACCEPTED, FROZEN, PERSISTED and COMMITTED, independent versioned authority, original
consumed/checkpoint references, new attempt identity and exact supersession. One effective
accepted outcome per case; duplicates or ambiguous supersession BLOCK. Old infrastructure
slots never become scientific trials. The same full six valid 3x3 rule remains required.

The combined input contains the grandfathered nine, accepted eligible V6 outcomes and only
qualifying seven-track outcomes from the fixed head. Seven-track completion is not a census
prerequisite. Bind exact pool bytes/digest, allocation-cycle ID, source identities and accepted
closure/head. A late outcome stays outside this cycle, even after failed allocation. No late
inclusion or cutoff refresh. REMOTE_PUBLISHED is not universally required for integration;
applicable downstream execution publication gates remain mandatory. A new cycle requires a
separate Human-PI adjudication; this contract grants no rerun or new cycle.

## D8 closure and exhaustion

All 433 preparation dispositions and all ready-case scheduled slots must be accounted and
Human-PI adjudicated. Accepted held-unresolved cases remain in denominators, non-scientific
and non-eligible. Unaccepted, unaccounted or contradictory work BLOCKS closure. Precedence:

1. V6_CENSUS_CLOSURE_BLOCKED: any missing adjudication/accounting, unaccepted closure,
   descriptor/event disagreement, competing authority or evidence contradiction.
2. V6_CENSUS_EXHAUSTED_INSUFFICIENT_ELIGIBLE_CAPACITY: accepted complete closure, combined
   eligible count below 28.
3. V6_CENSUS_COMPLETE_ALLOCATION_RULE_UNRESOLVED: complete closure, count at least 28,
   required controlling rule/input identity missing or ambiguous.
4. V6_CENSUS_EXHAUSTED_PROJECT_DIVERSITY_INFEASIBLE: closure/capacity/rules established,
   prescribed prospective pilot reservation leaves final cap/diversity infeasible.
5. V6_CENSUS_COMPLETE_ALLOCATION_AUTHORITY_REQUIRED: closure/capacity/rules/feasibility
   established; separate allocation authority is still required.

Orthogonal qualifiers are V6_CENSUS_COMPLETE_WITH_UNRESOLVED_INFRASTRUCTURE and
V6_PREPARATION_EXHAUSTED_WITH_NONSCIENTIFIC_DISPOSITIONS, only when accepted closure
supports them. They cannot replace a primary status or confer eligibility. No census status
is assigned in this construction. No terminal status authorizes expansion, repair, retry,
allocation, a new successor, changed source/universe/seed/rank, weaker oracle/cap or reduced N.

## Authority graph

v6_census_lifecycle.json defines the 16 explicit states and 15 separate Human-PI gates.
No completed state authorizes the next. Commit and publication remain distinct gates;
publication where inapplicable requires an explicit Human-PI applicability record. Planning,
source acquisition, materialization, image building, oracle and downstream repair retain their
separate subauthorities. BLOCKED/INTERRUPTED holds preserve consumed/partial evidence;
separately authorized continuation may dispatch only demonstrably never-consumed pending work.

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
  "architecture": "V6_FINITE_SAME_UNIVERSE_CENSUS_WITH_EVIDENCE_CONTINUITY",
  "automatic_successor_on_exhaustion": false,
  "bridge": {
    "path": "evaluation/downstream_benchmark/v6_predecessor_evidence_bridge.json",
    "sha256": "768517998be897f3e2a2d250336e1513e0a4ddc2ac6bd590a30ea6935226e222"
  },
  "candidate_only": true,
  "closure": {
    "all_433_preparation_dispositions_accounted_and_adjudicated": true,
    "all_ready_case_screening_slots_accounted_and_adjudicated": true,
    "automatic_downstream_authority": "NONE",
    "automatic_retry": false,
    "held_unresolved": "ADMINISTRATIVE_ADJUDICATION_STATE_ONLY",
    "held_unresolved_eligible": false,
    "held_unresolved_scientific_failure": false,
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
  },
  "construction_authority": {
    "path": "evaluation/downstream_benchmark/evidence/v6_successor_contract_construction_v1/entry_verification.json",
    "sha256": "6da22cfd90d9ec80044df7c04bcc269984b73d33eb134d147ef584e9c99116d6"
  },
  "counts": {
    "accepted_exclusions": 39,
    "cap_skips": 433,
    "eligible": 9,
    "infrastructure_unresolved": 7,
    "scientific_ineligible": 12
  },
  "downstream_authority": "NONE",
  "evidence_continuity": {
    "cap_skips_433": "PROPOSED_PROSPECTIVE_RECONSIDERATION_ONLY",
    "eligible_9": "GRANDFATHER_NO_CAPACITY_RERUN",
    "exclusions_39": "PRESERVED_NOT_REOPENED",
    "ineligible_12": "FINAL_UNCHANGED_ORACLE_NO_RESCUE",
    "predecessor_rewritten": false,
    "raw_evidence_cloned": false,
    "unresolved_7": "SEPARATE_VERSIONED_TRACK_OUTSIDE_V6_EXECUTION"
  },
  "narrow_supersession": {
    "design_decisions": {
      "D1": "Accept exact candidate identifiers, explicit lifecycle/event schemas and 31 labeled replays plus 402 literal rows; resolve proposal section 3 literal-ledger caveat.",
      "D2": "Replace proposal governance packaging and any batch-admission option with one logical 433-member census.",
      "D3": "Replace prescribed/frozen governed batch boundaries and scientific block identity with rank-ascending runtime dispatch chunks of no scientific identity.",
      "D4": "Retain orthogonal vocabulary; explicitly accept held-unresolved administrative closure without scientific failure, eligibility or automatic retry.",
      "D5": "Replace ambiguous derived-current-snapshot interpretation with the sole effective v6_current_state.json descriptor and hash-linked event provenance.",
      "D6": "Replace allocation-opening-gate cutoff in proposal sections 8/10 and unresolved_7_integration with immutable first combined-pool input freeze and fixed accepted-closure seven-track head.",
      "D7": "Replace null/unresolved pilot rule and pilot-project cap with the accepted hash-seed rule and NONE cap; no feasibility lookahead or reselection.",
      "D8": "Replace proposed status precedence with accepted ordered primary statuses plus orthogonal qualifiers."
    },
    "historical_artifacts_modified": false,
    "legacy_sections": "SCREENING_SPEC_V1.md D/J/M: initial-40 and cumulative admission cap, forward cursor, ten-admission outcome-triggered expansion; historical terminal permanent cap-skip disposition only for these exact 433 never-admitted cases",
    "unlisted_conflict": "BLOCK_RETURN_TO_HUMAN_PI"
  },
  "pool": {
    "path": "evaluation/downstream_benchmark/v6_reconsideration_pool.csv",
    "sha256": "42d47f13f39fbdbb335cd741e1c361b2dbf690d5e72382136a61f2608e16fe78"
  },
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
  "runtime_authority": false,
  "schema": "EP-DBP-6-CAPACITY",
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

STATUS =
V6_CENSUS_MEMBERSHIP_ACTIVATION_V1_REAL_TRANSITION_CANDIDATE_READY_FOR_HUMAN_PI_REVIEW

Run Report — 2026-10-04, Europe/Budapest.

A. AUTHORITY / ENTRY STATE

Task summary: reopen only the authorized real membership activation event and exact successor descriptor construction after the published genesis bridge. Transaction `REOPEN_V6_CENSUS_MEMBERSHIP_ACTIVATION_V1_AFTER_GENESIS_BRIDGE` comes from the latest direct Human-PI request, whose exact path/hash is in entry_verification.json. Repository `/Users/wuyangchenxi/errpilot`, branch main; local HEAD, cached origin/main and independently observed LIVE origin/main all equal `1e5f8a3f4bc2e8555619f727ea317b0bd2fdf801`. Initial worktree/index clean. Before the first write, 76 local gate checks passed, including exact contract/bridge enclosing commit parent, message, scope and bytes. Sandbox ls-remote failed DNS; the explicitly authorized read-only escalated retry succeeded. No on-disk AGENTS.md, .airos/current_state.md or .airos/contracts was found; supplied governance instructions and this direct request govern. Candidate namespace was absent at initial entry.

Only event/successor candidate construction is authorized. Installation, runtime effectivity and preparation are not authorized. The closed activation authority record uses HUMAN_PI_ACCEPTED=YES for the already authorized membership-event scope, not acceptance of these candidates. The request identity and construction-only boundary remain external to the unchanged V1 payload schema.

B. PUBLISHED CONTRACT / GENESIS BRIDGE

Contract commit `d5146d86fc2b36b336d1bdf2657a6cbdfde84f8c` is the exact parent of the bridge commit `1e5f8a3f4bc2e8555619f727ea317b0bd2fdf801` and an ancestor of independently observed LIVE origin/main. Exact contract manifest SHA-256 `4401b7c145d8a39c9a33f095f57c13a14bf6887d5848c116fe240631472810a7`; contract closure `977ee418f4ac3d84cf66af5943beea75fab3e38ba8c086211f22312c9bd46ac9`. Genesis bridge SHA-256 `1c4b8890d9e6c102b1be1403f69cf50f3554888c0e251397694e66abc2b0ec10`; bridge lifecycle closure `7e94df7d950dac1465ddf292aa5705a5d6c597915b3310d88642645a948258b5`. Local and committed bytes, exact commit scopes (42 contract paths and 17 bridge paths), messages and parents agree.

Bridge lifecycle: HUMAN_PI_ACCEPTED, FROZEN, PERSISTED, COMMITTED, REMOTE_PUBLISHED, based on the frozen external closure plus actual enclosing commit and independent live publication observation. The historical closure's REMOTE_PUBLISHED=NO and bridge JSON's earlier candidate lifecycle fields retain their historical meaning; neither was rewritten. Bridge EFFECTIVE=YES supplied to the unchanged validator means accepted controlling bridge semantics, not V6 runtime effectivity. The accepted S1–S6 semantics and two V1 payload schemas remain unchanged.

C. PREDECESSOR STATE

Canonical path `evaluation/downstream_benchmark/v6_current_state.json`. Descriptor SHA-256 `d17bcd3b7c669227f920671984b502497cdca9d367523548da4130eb8f986670`; raw projection SHA-256 `f15fd874b21a39d11d9117f6a4aa75b46dde1be4562f35557aa6b60ca08be840`. State CONTRACT_CANDIDATE, candidate_only=true, runtime_authority=false, effective identity=null, authoritative surfaces=[], event_count=0, head=null, chain=[]. V6_ACTIVATED=NO; CENSUS_MEMBERSHIP_EFFECTIVE=NO; all lifecycle and phase authorization flags NO. All 433 case states NOT_STARTED, no consumed attempt or scheduled/consumed slots, no results or allocation. The prewrite scan covered 94 JSON artifacts in the canonical benchmark subtree and found only the raw predecessor as a root V1 state/event artifact. No V6 execution artifact path was found. External storage and live containers/processes were not searched.

Canonical pool SHA-256 `42d47f13f39fbdbb335cd741e1c361b2dbf690d5e72382136a61f2608e16fe78`, exactly 433 members, 15 projects, original frozen numeric rank ascending; mechanical predecessor replay and exact CSV identities/order passed. No copied CSV pool was created. Predecessor bridge SHA-256 `768517998be897f3e2a2d250336e1513e0a4ddc2ac6bd590a30ea6935226e222`. Exact 9 eligible / 12 scientific-ineligible / 7 infrastructure-unresolved / 39 accepted exclusions / 433 reconsideration continuity retained; all 201 predecessor evidence byte pins passed.

D. QUALIFIED GENESIS

Unchanged accepted `qualify_runtime_genesis` produces `9633d99370f49d63e3b1b24e1b49adfbd4550a6aa12439e4f04276f0327638b5`. Q advances only projection.state and the exact five contract lifecycle flags. Every other field remains byte-equivalent under the bridge's canonical JSON definition. Qualification creates no event or canonical descriptor and grants no runtime or downstream authority. Exact changed fields and activation delta:

```json
{
  "Q_changes": [
    {
      "field": "projection.state",
      "from": "CONTRACT_CANDIDATE",
      "to": "CONTRACT_PUBLISHED_WHERE_REQUIRED"
    },
    {
      "field": "projection.lifecycle.CONTRACT_ACCEPTED",
      "from": "NO",
      "to": "YES"
    },
    {
      "field": "projection.lifecycle.CONTRACT_FROZEN",
      "from": "NO",
      "to": "YES"
    },
    {
      "field": "projection.lifecycle.CONTRACT_PERSISTED",
      "from": "NO",
      "to": "YES"
    },
    {
      "field": "projection.lifecycle.CONTRACT_COMMITTED",
      "from": "NO",
      "to": "YES"
    },
    {
      "field": "projection.lifecycle.CONTRACT_PUBLISHED_WHERE_REQUIRED",
      "from": "NO",
      "to": "YES"
    }
  ],
  "activation_changes": [
    {
      "field": "projection.state",
      "from": "CONTRACT_PUBLISHED_WHERE_REQUIRED",
      "to": "CENSUS_MEMBERSHIP_ACTIVATED"
    },
    {
      "field": "projection.lifecycle.V6_ACTIVATED",
      "from": "NO",
      "to": "YES"
    },
    {
      "field": "projection.lifecycle.CENSUS_MEMBERSHIP_EFFECTIVE",
      "from": "NO",
      "to": "YES"
    }
  ]
}
```

E. REAL ACTIVATION EVENT CANDIDATE

Path `evaluation/downstream_benchmark/evidence/v6_census_membership_activation_v1_after_genesis_bridge/activation_event_candidate.json`. Exact schema V6_CAPACITY_STATE_EVENT_V1, namespace EFFECTIVE_V6, kind STATE_TRANSITION, semantic operation CENSUS_MEMBERSHIP_ACTIVATION. One real candidate event only, sequence 1, previous_event_identity=null. No undeclared previous-event field, timestamp, event/file self-hash or future descriptor hash was added. The bridge's derive_event_id computes the core identity; validate_event_identity computes and distinguishes the canonical complete payload and exact stored file identities:

- event_id `95e5ab3ca14cf2b5b47f6a1b1614e80f89f7ea8cbaf22e01245c48ed69aca0f3`
- canonical complete event payload SHA-256 `9183d5b373128bca07018b6524e09bfbfb8cac7e38ccbea28c966f7c018d72cc`
- exact stored event file SHA-256 `4ddc1a67e0ae135269877aa1754d8eeeb3424aab03b6bb38785d769390417734`

Exact non-projection event fields (the historical predecessor field is unchanged):

```json
{
  "authority_reference": {
    "path": "evaluation/downstream_benchmark/evidence/v6_census_membership_activation_v1_after_genesis_bridge/activation_authority.json",
    "sha256": "dde88cf4918c1430f27f177b2cc27e3abef5c4a9570933e7929a8fd8b3592c7a"
  },
  "contract_sha256": "4401b7c145d8a39c9a33f095f57c13a14bf6887d5848c116fe240631472810a7",
  "event_id": "95e5ab3ca14cf2b5b47f6a1b1614e80f89f7ea8cbaf22e01245c48ed69aca0f3",
  "evidence_references": [
    {
      "path": "evaluation/downstream_benchmark/V6_SUCCESSOR_CONTRACT_LIFECYCLE_CLOSURE_V1.md",
      "sha256": "977ee418f4ac3d84cf66af5943beea75fab3e38ba8c086211f22312c9bd46ac9"
    },
    {
      "path": "evaluation/downstream_benchmark/v6_activation_runtime_genesis_bridge_v1.json",
      "sha256": "1c4b8890d9e6c102b1be1403f69cf50f3554888c0e251397694e66abc2b0ec10"
    },
    {
      "path": "evaluation/downstream_benchmark/v6_predecessor_evidence_bridge.json",
      "sha256": "768517998be897f3e2a2d250336e1513e0a4ddc2ac6bd590a30ea6935226e222"
    },
    {
      "path": "evaluation/downstream_benchmark/v6_reconsideration_pool.csv",
      "sha256": "42d47f13f39fbdbb335cd741e1c361b2dbf690d5e72382136a61f2608e16fe78"
    }
  ],
  "from_state": "CONTRACT_PUBLISHED_WHERE_REQUIRED",
  "gate": "HUMAN_PI_ACTIVATE_V6_CENSUS_MEMBERSHIP",
  "kind": "STATE_TRANSITION",
  "namespace": "EFFECTIVE_V6",
  "previous_descriptor_sha256": "d17bcd3b7c669227f920671984b502497cdca9d367523548da4130eb8f986670",
  "previous_event_identity": null,
  "prior_projection_sha256": "9633d99370f49d63e3b1b24e1b49adfbd4550a6aa12439e4f04276f0327638b5",
  "result_projection_sha256": "1bb6f6bda409db2b38ecd078d08c3e60582385db172fcaeacd85b7c28d798d38",
  "schema": "V6_CAPACITY_STATE_EVENT_V1",
  "sequence": 1,
  "supersession_reference": {
    "path": "evaluation/downstream_benchmark/v6_activation_runtime_genesis_bridge_v1.json",
    "sha256": "1c4b8890d9e6c102b1be1403f69cf50f3554888c0e251397694e66abc2b0ec10"
  },
  "to_state": "CENSUS_MEMBERSHIP_ACTIVATED"
}
```

The semantic evidence set is exactly the bridge's four references in UTF-8 path-byte/digest order. Bridge lifecycle proof is independently verified and recorded in entry/lineage, not appended as incidental core evidence. Supersession is the exact accepted genesis bridge, never a future activation closure.

F. REAL SUCCESSOR DESCRIPTOR CANDIDATE

Path `evaluation/downstream_benchmark/evidence/v6_census_membership_activation_v1_after_genesis_bridge/post_state_candidate.json`; exact file SHA-256 `bdc7f0d5c7927d7a691fc7a1768e60d4ff82287a1910aa1aac5158ad8a83bf54`. Schema V6_CAPACITY_CURRENT_STATE_V1; result projection SHA-256 `1bb6f6bda409db2b38ecd078d08c3e60582385db172fcaeacd85b7c28d798d38`. Derived from raw predecessor + one Q + event + exact result; event_count=1. Historical `predecessor` is preserved, V6 transition lineage uses the exact one-entry event_chain with path, file hash, event_id, sequence and canonical event payload hash. Head:

```json
{
  "event_id": "95e5ab3ca14cf2b5b47f6a1b1614e80f89f7ea8cbaf22e01245c48ed69aca0f3",
  "event_sha256": "9183d5b373128bca07018b6524e09bfbfb8cac7e38ccbea28c966f7c018d72cc",
  "sequence": 1
}
```

Proposed V6_ACTIVATED=YES and CENSUS_MEMBERSHIP_EFFECTIVE=YES for the exact 433-member census. The approved preview has candidate_only=false, runtime_authority=false, effective_current_descriptor_identity=null and authoritative_current_surfaces=[]. All three downstream lifecycle authorization flags remain NO; all exact phase flags:

```json
{
  "DOWNSTREAM_REPAIR_EXECUTION": "NO",
  "IMAGE_BUILD": "NO",
  "ORACLE_EXECUTION": "NO",
  "PILOT_FINAL_ALLOCATION": "NO",
  "PREPARATION_EXECUTION": "NO",
  "PREPARATION_PLANNING": "NO",
  "SOURCE_ACQUISITION": "NO"
}
```

Materialization/preparation execution remains unauthorized; oracle not executed, input freeze=null, pilot/final arrays=[], no scientific state or case/work accounting change. Summary firewall names that are absent from V1 are derived assertions only, not new schema fields.

G. NON-EFFECTIVE ENVELOPE

Path `evaluation/downstream_benchmark/evidence/v6_census_membership_activation_v1_after_genesis_bridge/candidate_envelope.json`; file SHA-256 `544b1272e54425892949d7be223e77b8de4e1f992ce273efc83db4a501cc6aec`. Exact bridge assertions:

```json
{
  "profile": "NON_EFFECTIVE_TRANSITION_CANDIDATE",
  "PROPOSED_V6_ACTIVATED": "YES",
  "PROPOSED_MEMBERSHIP_EFFECTIVE": "YES",
  "PROPOSED_EVENT_COUNT": 1,
  "CANONICAL_V6_ACTIVATED": "NO",
  "CANONICAL_MEMBERSHIP_EFFECTIVE": "NO",
  "CANONICAL_EVENT_COUNT": 0,
  "RUNTIME_EFFECTIVE": "NO",
  "CURRENT_AUTHORITY": "UNCHANGED_CANONICAL_PREDECESSOR_DESCRIPTOR",
  "CANONICAL_RUNTIME_AUTHORITY": "NONE",
  "CANONICAL_INSTALLATION_AUTHORIZED_BY_CANDIDATE": "NO",
  "AUTO_PROMOTION": "NO",
  "CURRENT_REGISTRATION": "PROHIBITED"
}
```

The envelope carries the exact event and successor previews. Its event_bytes JSON string losslessly transports exact UTF-8 event file text; the read-only adapter encodes that field to bytes before calling the unchanged bridge API. Neither V1 schema nor bridge is modified. Standalone files and embedded previews must agree exactly. This namespace alone confers no authority; candidate consumption as current is rejected.

H. REPLAY / DERIVATION VALIDATION

The raw descriptor hash, raw projection hash, qualified seed, membership-only delta, closed event core, deterministic event ID, canonical complete payload hash, stored file hash, one-entry head/chain and exact successor all agree with independent mechanical replay. Stored event bytes and post-state payload match derivation exactly. Q is applied once per bootstrap derivation from the exact raw predecessor. Independent verification recomputes from that same raw input; it never composes Q with qualified output or appends another event. Both Q composition and use after sequence 1 are rejected. The accepted bridge hash dependency graph is acyclic; authority is upstream of the core and does not contain future event/successor hashes. Authority storage is canonical JSON without a newline, so its file SHA equals the bridge-required canonical authority digest. Inventory/report hashes are downstream with self-hashes excluded.

I. REJECTION MATRIX

Actual candidate checks: 27 positive checks, 61 rejection probes, 0 failures. Inherited unchanged bridge: 18 positive checks and 85 rejection probes; inherited contract: 141 rejection probes. Rejection probes alter copies in memory and do not write canonical bytes. Probes that violate closed schema/core preconditions may be rejected at that bridge API precondition; legal-shaped mutations are re-signed and audited against the exact expected delta. All required probes are present:

| Probe | Result | Observed rejection reason |
| --- | --- | --- |
| wrong_bridge_hash | PASS_REJECTED | accepted bridge proof drift |
| wrong_bridge_bytes | PASS_REJECTED | wrong exact published bridge hash |
| unaccepted_bridge | PASS_REJECTED | accepted bridge proof drift |
| ineffective_bridge | PASS_REJECTED | accepted bridge proof drift |
| unpublished_bridge | PASS_REJECTED | bridge publication not evidenced |
| wrong_bridge_closure | PASS_REJECTED | wrong exact bridge closure |
| wrong_predecessor_descriptor | PASS_REJECTED | wrong predecessor descriptor bytes |
| wrong_raw_projection | PASS_REJECTED | wrong exact raw projection |
| wrong_qualified_projection | PASS_REJECTED | qualified projection mismatch |
| Q_reapplied_twice | PASS_REJECTED | wrong exact raw projection |
| Q_after_bootstrap | PASS_REJECTED | Q forbidden after genesis |
| first_sequence_not_1 | PASS_REJECTED | first-event predecessor/sequence drift |
| first_previous_event_non_null | PASS_REJECTED | first-event predecessor/sequence drift |
| wrong_lifecycle_from | PASS_REJECTED | nonadjacent lifecycle edge |
| wrong_lifecycle_to | PASS_REJECTED | nonadjacent lifecycle edge |
| synthetic_backfill | PASS_REJECTED | nonadjacent lifecycle edge |
| wrong_previous_descriptor_binding | PASS_REJECTED | raw-descriptor/qualified-projection distinction violated |
| wrong_prior_projection_binding | PASS_REJECTED | raw-descriptor/qualified-projection distinction violated |
| wrong_contract_binding | PASS_REJECTED | historical predecessor/contract changed |
| wrong_supersession_reference | PASS_REJECTED | exact four genesis references/supersession missing |
| wrong_gate | PASS_REJECTED | nonadjacent lifecycle edge |
| arbitrary_event_id | PASS_REJECTED | arbitrary/noncanonical event_id |
| event_id_mismatch | PASS_REJECTED | arbitrary/noncanonical event_id |
| event_id_self_reference | PASS_REJECTED | invalid event core fields (self identity/hash/timestamp prohibited) |
| undeclared_event_field:event_sha256 | PASS_REJECTED | invalid event core fields (self identity/hash/timestamp prohibited) |
| undeclared_event_field:file_sha256 | PASS_REJECTED | invalid event core fields (self identity/hash/timestamp prohibited) |
| undeclared_event_field:successor_sha256 | PASS_REJECTED | invalid event core fields (self identity/hash/timestamp prohibited) |
| undeclared_event_field:timestamp | PASS_REJECTED | invalid event core fields (self identity/hash/timestamp prohibited) |
| undeclared_event_field:previous_event_id | PASS_REJECTED | invalid event core fields (self identity/hash/timestamp prohibited) |
| undeclared_event_field:previous_event_hash | PASS_REJECTED | invalid event core fields (self identity/hash/timestamp prohibited) |
| evidence_reference_drift | PASS_REJECTED | exact four genesis references/supersession missing |
| evidence_reference_order | PASS_REJECTED | evidence reference order drift |
| evidence_reference_duplicate | PASS_REJECTED | duplicate/conflicting evidence reference |
| incidental_evidence_reference | PASS_REJECTED | exact four genesis references/supersession missing |
| pool_hash_drift | PASS_REJECTED | pool byte drift |
| pool_byte_disagreement | PASS_REJECTED | pool byte drift |
| member_addition | PASS_REJECTED | closed V1 schema rejection: $.next_projection.case_states |
| member_omission | PASS_REJECTED | closed V1 schema rejection: $.next_projection.case_states |
| member_reorder | PASS_REJECTED | activation delta changed downstream work/authority |
| preparation_enabled | PASS_REJECTED | activation delta changed downstream work/authority |
| oracle_enabled | PASS_REJECTED | activation delta changed downstream work/authority |
| allocation_enabled | PASS_REJECTED | activation delta changed downstream work/authority |
| source_acquisition_enabled | PASS_REJECTED | activation delta changed downstream work/authority |
| image_build_enabled | PASS_REJECTED | activation delta changed downstream work/authority |
| scientific_outcome_changed | PASS_REJECTED | closed V1 schema rejection: $.next_projection.case_states[0] |
| attempt_consumed | PASS_REJECTED | activation delta changed downstream work/authority |
| actual_pilot_selected | PASS_REJECTED | activation delta changed downstream work/authority |
| event_count_not_1 | PASS_REJECTED | single bootstrap chain mismatch |
| wrong_event_head | PASS_REJECTED | single bootstrap chain mismatch |
| wrong_event_file_binding | PASS_REJECTED | single bootstrap chain mismatch |
| runtime_authority_enabled | PASS_REJECTED | closed V1 schema rejection: $.authoritative_current_surfaces |
| candidate_only_preview_drift | PASS_REJECTED | closed V1 schema rejection: $.event_chain |
| candidate_treated_as_canonical | PASS_REJECTED | candidate-as-current consumption prohibited |
| auto_promotion_enabled | PASS_REJECTED | non-effective assertions drift |
| canonical_registration_enabled | PASS_REJECTED | non-effective assertions drift |
| canonical_activation_asserted | PASS_REJECTED | non-effective assertions drift |
| canonical_v6_current_state_mutation | PASS_REJECTED | wrong predecessor descriptor bytes |
| changed_activation_authority | PASS_REJECTED | independent activation authority mismatch |
| future_authority_identity | PASS_REJECTED | event authority contains undeclared/future identities |
| request_authority_hash_drift | PASS_REJECTED | request identity drift |
| canonical_installation_authorized | PASS_REJECTED | construction-only authorization boundary drift |

J. TESTS / STATIC CHECKS / COMMANDS RUN

Pytest: 112 passed, 0 failed, exit 0. Exact stdout: `112 passed in 181.95s (0:03:01)`. Candidate suite plus both inherited bridge/contract suites were run. Ruff check and format check passed for the two new Python files. All eight unchanged schemas passed draft-2020-12 meta-validation. 67 files in the exact contract/bridge/new-artifact static scope passed UTF-8/no-BOM, strict JSON/duplicate-key/non-JSON/float checks as applicable, Python AST and trailing whitespace checks before the report/inventory; exit checks cover all eleven new files. Git worktree/index whitespace checks passed. A wider read-only historical text scan found pre-existing trailing whitespace in `evaluation/downstream_benchmark/fixtures/environment_materializer/validation_evidence/f/SOURCE_INDEPENDENT/build.log`; that old fixture log was preserved exactly and is outside the changed/contract/bridge static scope.

Principal commands actually run:

```text
git status --porcelain=v1 --untracked-files=all
git branch --show-current
git rev-parse HEAD refs/remotes/origin/main
git log -1 --format=%H%n%s
git ls-remote --exit-code origin refs/heads/main
git diff-tree --no-commit-id --name-only -r <contract-or-bridge-commit>
git show <contract-or-bridge-commit>:<explicitly-pinned-path>
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B <read-only prewrite entry gate>
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B /private/tmp/errpilot_v6_activation_construct.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B evaluation/downstream_benchmark/evidence/v6_census_membership_activation_v1_after_genesis_bridge/validate_activation.py > /private/tmp/errpilot_v6_activation_audit.json
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider evaluation/downstream_benchmark/evidence/v6_census_membership_activation_v1_after_genesis_bridge/test_activation.py evaluation/downstream_benchmark/evidence/v6_activation_runtime_genesis_bridge_v1/test_bridge.py evaluation/downstream_benchmark/evidence/v6_successor_contract_construction_v1/test_contract.py
.venv/bin/ruff check --no-cache <two new Python paths>
.venv/bin/ruff format --check --no-cache <two new Python paths>
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B /private/tmp/errpilot_v6_activation_finish.py
git diff --check
git diff --cached --check
```

Read-only cat/sed/rg, CSV/JSON/hash and AST inspections were also used; a preliminary closure read used an incorrect fenced-block selector, exited without any write, and was corrected to the actual committed delimiter. No dependency installation or GUI action occurred. Scratch helpers/test observation files remain under /private/tmp; they are not semantic evidence or repository candidates.

K. PRESERVATION / CONTRACT COMPLIANCE

All 496 entry byte pins passed throughout executed preservation checks: every tracked benchmark file plus all 201 exact predecessor references. Published contract, schemas, genesis bridge, both closures, canonical descriptor, pool, predecessor bridge, six historical blocker artifacts and existing historical evidence are unchanged. Entire-repository tracked diff and index are empty. HEAD/branch remain the required baseline. Only eleven new untracked activation-candidate/evidence paths are permitted at exit. The direct construction-only contract and supplied governance boundaries are satisfied; no production code or paper-facing claim was modified.

L. NEW FILE INVENTORY

Exact repository paths, purposes and hashes:

| Path | Purpose | Exact file SHA-256 |
| --- | --- | --- |
| `evaluation/downstream_benchmark/evidence/v6_census_membership_activation_v1_after_genesis_bridge/activation_authority.json` | Exact closed bridge authority record; canonical bytes, construction scope only | `dde88cf4918c1430f27f177b2cc27e3abef5c4a9570933e7929a8fd8b3592c7a` |
| `evaluation/downstream_benchmark/evidence/v6_census_membership_activation_v1_after_genesis_bridge/activation_event_candidate.json` | Real sequence-1 V1 membership activation event candidate | `4ddc1a67e0ae135269877aa1754d8eeeb3424aab03b6bb38785d769390417734` |
| `evaluation/downstream_benchmark/evidence/v6_census_membership_activation_v1_after_genesis_bridge/candidate_envelope.json` | NON_EFFECTIVE_TRANSITION_CANDIDATE assertions plus exact previews | `544b1272e54425892949d7be223e77b8de4e1f992ce273efc83db4a501cc6aec` |
| `evaluation/downstream_benchmark/evidence/v6_census_membership_activation_v1_after_genesis_bridge/entry_verification.json` | Independent entry/publication observation and 496 preserved input pins | `92d887e35e03096047c733e1cdc0e0588bf62613c4af1d9107a1a07dd6fdf37c` |
| `evaluation/downstream_benchmark/evidence/v6_census_membership_activation_v1_after_genesis_bridge/lineage.json` | Exact Q/activation deltas, bridge closure/publication proof, hashes, lifecycle | `f749fd2bcbe3eb433654f0790fde6e6e7f08ef4a2efb2895e92f0f5c9f934511` |
| `evaluation/downstream_benchmark/evidence/v6_census_membership_activation_v1_after_genesis_bridge/post_state_candidate.json` | Exact V1 successor preview, powerless and not installed | `bdc7f0d5c7927d7a691fc7a1768e60d4ff82287a1910aa1aac5158ad8a83bf54` |
| `evaluation/downstream_benchmark/evidence/v6_census_membership_activation_v1_after_genesis_bridge/test_activation.py` | Candidate-specific coverage and canonical firewall checks | `2a93a161ff8072c42f28221b85fc1b962ca2ccd93988f8585cb922879d333242` |
| `evaluation/downstream_benchmark/evidence/v6_census_membership_activation_v1_after_genesis_bridge/validate_activation.py` | Read-only transaction adapter invoking unchanged accepted bridge | `35d038988e81806276699bf992669d413a447f3f9097e743eb6af12b463ed907` |
| `evaluation/downstream_benchmark/evidence/v6_census_membership_activation_v1_after_genesis_bridge/validation_results.json` | Positive/rejection/replay evidence and actual test/static results | `5ebe4101798c922ce1b1dd1ca1e01f7656d8e7a682eabbb3d0946d898df1982d` |
| `evaluation/downstream_benchmark/evidence/v6_census_membership_activation_v1_after_genesis_bridge/RUN_REPORT.md` | A–O Run Report; own hash excluded from its text | Bound externally by artifact_sha256.json |
| `evaluation/downstream_benchmark/evidence/v6_census_membership_activation_v1_after_genesis_bridge/artifact_sha256.json` | Inventory of all ten other artifacts; own hash excluded | Independently reported at exit; self-excluded |

No 433-row CSV copy exists. Full required V1 projection case_states are retained in event/descriptor/envelope previews. Formal lifecycle persistence remains NO despite saved review files.

M. FIREWALL

```text
CANONICAL_V6_ACTIVATED = NO
CANONICAL_MEMBERSHIP_EFFECTIVE = NO
CANONICAL_EVENT_COUNT = 0
PROPOSED_V6_ACTIVATED = YES
PROPOSED_MEMBERSHIP_EFFECTIVE = YES
PROPOSED_EVENT_COUNT = 1
CANONICAL_CURRENT_STATE_MODIFIED = NO
PREPARATION_AUTHORIZED = NO
ORACLE_AUTHORIZED = NO
ALLOCATION_AUTHORIZED = NO
SOURCE_ACQUISITION_AUTHORIZED = NO
MATERIALIZATION_AUTHORIZED = NO
IMAGE_BUILD_AUTHORIZED = NO
ORACLE_EXECUTED = NO
COMBINED_ELIGIBLE_POOL_FROZEN = NO
PILOT_FINAL_ALLOCATION_AUTHORIZED = NO
PILOT_SELECTED = NO
FINAL_CASE_SELECTED = NO
PILOT_IDS_COMPUTED = NO
FINALS_ALLOCATED = NO
RUNTIME_EFFECTIVE = NO
CANONICAL_INSTALLATION = NO
GIT_STAGE = NO
GIT_COMMIT = NO
GIT_PUSH = NO
```

N. LIFECYCLE / RISKS AND UNKNOWNS

```text
V6_CENSUS_MEMBERSHIP_ACTIVATION_V1 = TRANSITION_CANDIDATE_ONLY
HUMAN_PI_ACCEPTED = NO
FROZEN = NO
PERSISTED = NO
COMMITTED = NO
REMOTE_PUBLISHED = NO
```

These checks establish exact local construction, bounded semantic rejection behavior and byte preservation. They do not establish scientific validation, subject feasibility, runtime qualification, a working production consumer/installer, downstream execution or allocation feasibility. Initial absence checks cover the canonical benchmark subtree/governed canonical case-work state; other external storage, processes and containers were not inspected. Remote publication was independently observed at entry and rechecked at exit; read-only local validation consumes that observed proof rather than independently querying the network. Future installer/integration work and approval are separate gates. No scientific recommendation is inferred from passing tests.

O. NEXT GATE / RECOMMENDED NEXT ACTION

NEXT_GATE = HUMAN_PI_REVIEW_OF_V6_CENSUS_MEMBERSHIP_ACTIVATION_V1_REAL_TRANSITION_CANDIDATE

Human-PI review of these exact event, successor and envelope bytes is recommended. No acceptance, freeze, formal persistence, commit, publication, installation or preparation authority is granted by this transaction. Stop.

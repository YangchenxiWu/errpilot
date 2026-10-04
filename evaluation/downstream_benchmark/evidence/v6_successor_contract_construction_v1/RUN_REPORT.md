STATUS =
V6_SUCCESSOR_CONTRACT_CANDIDATE_READY_FOR_HUMAN_PI_REVIEW

Run Report — OPEN_V6_SUCCESSOR_CONTRACT_CONSTRUCTION, 2026-10-04, Europe/Budapest.
This is candidate contract construction and internal consistency evidence only.

## A. Authority / entry state

The latest direct Human-PI request accepted the exact finalized V6 design and authorized
contract construction only. It is bound by attachment path and SHA-256 in entry_verification.json.
Historical decision/finalization files retain their earlier acceptance boundary; no bytes were
rewritten to manufacture the later instruction. No successor-contract acceptance is inferred.

Canonical root /Users/wuyangchenxi/errpilot; branch main. HEAD and LIVE origin/main both
26a9264105f303dc0101f74c9315c41ab1c9e265. The live read-only ls-remote succeeded after the sandbox
DNS attempt failed. The entry index was empty, the tracked diff was empty, and exactly 19 expected
historical untracked paths were present. Their identities were recovered from both historical
inventories and checked against finalization lineage, including independently hashed inventory files.
No optional on-disk AGENTS.md, .airos/current_state.md or .airos/contracts was present.
The user-supplied governance instructions and this explicit transaction controlled the work.

## B. Accepted design authority

- D1–D8 decision SHA-256: 2d30ba01c22a6531ab1480140dbef20d2878ba94c8ac2d7d7aa01cc85514e6f2.
- Accepted finalized design SHA-256: f2e17649236d28d1712192146039370a6e0542084a82685d03f2d4d227064163.
- Accepted proposal pool: 433 members, SHA-256 cad0889e1a527165fc04663c4bde0b22a8af25cdc07bc8c6426348e5ad1c2669.
- Original frozen BugsInPy commit 11c5f1eea954a42132cfd06bf257766a7963e0fd and tree
  d00ce0495ba73abe50317599f48bced3c9afe4b3 were rechecked against the clean local source checkout.
- Candidate universe SHA-256 78208adf610a50542be6dfbd03a9b25960ba0b5cfc80768b08ffe7a4c78f3b8c;
  seed 20260922. All 62 accepted D1–D8 fields were independently compared to the bound PI source.

## C. Historical 19-input preservation

All 11 original proposal/evidence paths and 8 finalization paths are byte-identical.
No tracked file, historical V1/V5 artifact, predecessor result or original design input changed.
The inherited audit additionally rechecked 493 tracked inputs, 143 original external inputs,
1737 original evidence files, and the 201 exact predecessor bindings. Hash preservation does
not imply every preserved file was semantically reread in full.

| Historical path | SHA-256 | Preservation |
| --- | --- | --- |
| `evaluation/downstream_benchmark/V6_FINITE_SAME_UNIVERSE_CENSUS_PROTOCOL_DESIGN_FINALIZED_CANDIDATE.md` | `f2e17649236d28d1712192146039370a6e0542084a82685d03f2d4d227064163` | PASS |
| `evaluation/downstream_benchmark/V6_FINITE_SAME_UNIVERSE_CENSUS_PROTOCOL_DESIGN_PROPOSAL.md` | `a406668b6d7761f0d09eab01bd19ac169dccfdaeefc06a1d9cccdea6da7b776b` | PASS |
| `evaluation/downstream_benchmark/V6_PROTOCOL_DESIGN_D1_D8_HUMAN_PI_DECISION.md` | `2d30ba01c22a6531ab1480140dbef20d2878ba94c8ac2d7d7aa01cc85514e6f2` | PASS |
| `evaluation/downstream_benchmark/evidence/v6_protocol_design_finalization_v1/RUN_REPORT.md` | `a361b1eec78e536bb06f08f5ab6ad823af9e8e407f5aa227e641196344900ce3` | PASS |
| `evaluation/downstream_benchmark/evidence/v6_protocol_design_finalization_v1/artifact_sha256.json` | `0482974989df63c40df4ccc0b654040223e92e78f9636c09e7bd2729161f3214` | PASS |
| `evaluation/downstream_benchmark/evidence/v6_protocol_design_finalization_v1/entry_verification.json` | `9fb6b92a8305d33e81915e57019644a20cdfcc1f28010b628aa8ebb9e4499c5f` | PASS |
| `evaluation/downstream_benchmark/evidence/v6_protocol_design_finalization_v1/lineage.json` | `16377282ff47a7870506d642a8b09084055dabd7edcc09ff31c03bdb5168e0b7` | PASS |
| `evaluation/downstream_benchmark/evidence/v6_protocol_design_finalization_v1/validate_finalization.py` | `18cc6217f9c5cbcd397bb62ec1a21bf7ab6465e8c92b7ff62d08f88031e636bd` | PASS |
| `evaluation/downstream_benchmark/evidence/v6_protocol_design_finalization_v1/validation_results.json` | `0e9a30731c78f11f7f548c9a1ee9e1c43d2181330483f797e1965feb35a6a494` | PASS |
| `evaluation/downstream_benchmark/evidence/v6_protocol_design_v1/RUN_REPORT.md` | `0f41bbee5d5755217730032771d4655cc1136b6556178ac0dd40542fa3ba83ba` | PASS |
| `evaluation/downstream_benchmark/evidence/v6_protocol_design_v1/artifact_sha256.json` | `262692d70cf2230d8ce22b2d69a60c13d0ae7952c8a3038bb9d4ccd265574427` | PASS |
| `evaluation/downstream_benchmark/evidence/v6_protocol_design_v1/entry_reconstruction.py` | `c3a708e75dd09ad6c24f71711f1bb97647b474404f54be113cec1637f8866d6e` | PASS |
| `evaluation/downstream_benchmark/evidence/v6_protocol_design_v1/entry_verification.json` | `689ac4d8b04e3d7b34d40dca0facdd9ea353af1e67dc7647a355514edb71aeab` | PASS |
| `evaluation/downstream_benchmark/evidence/v6_protocol_design_v1/predecessor_artifact_sha256.json` | `1afc64237645524ac1954539b1991ba5a8cbdedeebaf19df3c9669551091b622` | PASS |
| `evaluation/downstream_benchmark/evidence/v6_protocol_design_v1/validate_proposal.py` | `e7b3de8671eac44d39f8c9de287dafa6c598aff3ffa45247254fcec9fa11a6b5` | PASS |
| `evaluation/downstream_benchmark/evidence/v6_protocol_design_v1/validation_results.json` | `c85831ef5dcc505a8b8876f30a6ab669e707f3fd0bc2b5b8590d083a7d044636` | PASS |
| `evaluation/downstream_benchmark/v6_capacity_successor_contract_proposal.json` | `85b5e3c4e3fb496257bdcaae27f52b3c3f151e0941b645f36423c3203a8e2684` | PASS |
| `evaluation/downstream_benchmark/v6_predecessor_evidence_bridge_proposal.json` | `f3f80105486f6b95eddcb0cdc5d2c311c90b8989e8b30558662af0d7f7a563e5` | PASS |
| `evaluation/downstream_benchmark/v6_reconsideration_pool_proposal.csv` | `cad0889e1a527165fc04663c4bde0b22a8af25cdc07bc8c6426348e5ad1c2669` | PASS |

## D. Contract artifact inventory

All paths below are new, untracked candidate files. Version labels are not acceptance.
The eight explicit schema IDs use repository JSON Schema draft 2020-12 conventions.
The artifact inventory binds every new file except itself. Its own independent digest is
reported in the final chat; report/inventory self exclusions avoid circular hashes.

| Exact repository-relative path | Contract/schema identity | SHA-256 |
| --- | --- | --- |
| `evaluation/downstream_benchmark/V6_CAPACITY_SUCCESSOR_PROTOCOL.md` | `EP-DBP-6-CAPACITY` | `b11b8247e91b1469a95931bdd6e1acf9600fece339f2e105e5cd54e6bf9d1b60` |
| `evaluation/downstream_benchmark/V6_CAPACITY_SUCCESSOR_RUN_SPEC.md` | `EP-DBRS-6-CAPACITY` | `1bc14f83d23677a0ef16c0ca37e5dfed139af4cfca155dfac6da4296554d8d36` |
| `evaluation/downstream_benchmark/V6_CENSUS_SCREENING_SPEC.md` | `EP-BIPS-6-CENSUS` | `d5d11a7175ff218bc71764a42c382b9c3daf58f456a5cc56df777aa2f3de5d1f` |
| `evaluation/downstream_benchmark/evidence/v6_successor_contract_construction_v1/RUN_REPORT.md` | `construction evidence` | `Self-excluded here; exact SHA-256 in artifact_sha256.json` |
| `evaluation/downstream_benchmark/evidence/v6_successor_contract_construction_v1/artifact_sha256.json` | `construction evidence` | `Self-excluded from hash graph; independently measured seal in final chat` |
| `evaluation/downstream_benchmark/evidence/v6_successor_contract_construction_v1/entry_verification.json` | `V6_SUCCESSOR_CONSTRUCTION_ENTRY_V1` | `6da22cfd90d9ec80044df7c04bcc269984b73d33eb134d147ef584e9c99116d6` |
| `evaluation/downstream_benchmark/evidence/v6_successor_contract_construction_v1/test_contract.py` | `contract validation source` | `3d4190cce6eab5fac08428d43e500f217be3ee75780f4ab38ce2ae86c0aa0a80` |
| `evaluation/downstream_benchmark/evidence/v6_successor_contract_construction_v1/validate_contract.py` | `contract validation source` | `efaee07a08658da8f7b5b3f8fcb2841673c0bd3028c6268a139bf5240459e7da` |
| `evaluation/downstream_benchmark/evidence/v6_successor_contract_construction_v1/validation_results.json` | `V6_SUCCESSOR_CONTRACT_CONSTRUCTION_VALIDATION_V1` | `b8370d72994fa0a758625b513cdef807c679648ee4cb3b1925a2dae62910b05b` |
| `evaluation/downstream_benchmark/v6_capacity_successor_contract.json` | `V6_CAPACITY_SUCCESSOR_CONTRACT_CANDIDATE_V1` | `4401b7c145d8a39c9a33f095f57c13a14bf6887d5848c116fe240631472810a7` |
| `evaluation/downstream_benchmark/v6_census_lifecycle.json` | `V6_CENSUS_LIFECYCLE_V1` | `7f0313e3f87bfc51e823f4bd627ada0e39a89193dff6ec2dc920e37a72582a92` |
| `evaluation/downstream_benchmark/v6_contract_schemas/EP-BIPS-6-CENSUS.schema.json` | `EP-BIPS-6-CENSUS (JSON Schema 2020-12)` | `73bc6dc7772fe9c8615d8ddbe132b5faaf6b20fb5eaadc72e031e4973ade2967` |
| `evaluation/downstream_benchmark/v6_contract_schemas/EP-DBP-6-CAPACITY.schema.json` | `EP-DBP-6-CAPACITY (JSON Schema 2020-12)` | `0381f6f8a314fca2da9673fcce5bed2415494b87ded79fa1330a0d6c998380cc` |
| `evaluation/downstream_benchmark/v6_contract_schemas/EP-DBRS-6-CAPACITY.schema.json` | `EP-DBRS-6-CAPACITY (JSON Schema 2020-12)` | `6639e0a97264ba844922df13f264b0c06d87a0ec200365c61b5badbd69d5e0eb` |
| `evaluation/downstream_benchmark/v6_contract_schemas/V6_CAPACITY_CURRENT_STATE_V1.schema.json` | `V6_CAPACITY_CURRENT_STATE_V1 (JSON Schema 2020-12)` | `cc326c0e8099bc19bf9c002ad48af68cbf488360e4bbb8cb9e0e0266b017b0f9` |
| `evaluation/downstream_benchmark/v6_contract_schemas/V6_CAPACITY_STATE_EVENT_V1.schema.json` | `V6_CAPACITY_STATE_EVENT_V1 (JSON Schema 2020-12)` | `02988699eaf98e042c4798beb3862f9308deba386e6a9c066b365d145f3022b7` |
| `evaluation/downstream_benchmark/v6_contract_schemas/V6_CENSUS_LIFECYCLE_V1.schema.json` | `V6_CENSUS_LIFECYCLE_V1 (JSON Schema 2020-12)` | `4289b56c9bdaf0a798f4008b52356107cfcc3d80ee77e6b0ddca79e7acc8c8f2` |
| `evaluation/downstream_benchmark/v6_contract_schemas/V6_PREDECESSOR_EVIDENCE_BRIDGE_V1.schema.json` | `V6_PREDECESSOR_EVIDENCE_BRIDGE_V1 (JSON Schema 2020-12)` | `371550d60c6267342bf06be5daa6a6ee059750c640599295a5ce3902a5f44d79` |
| `evaluation/downstream_benchmark/v6_contract_schemas/V6_RECONSIDERATION_POOL_V1.schema.json` | `V6_RECONSIDERATION_POOL_V1 (JSON Schema 2020-12)` | `191114f3789d91c80c6e91692ce886636250e346c9496d738cf05204aa1a542e` |
| `evaluation/downstream_benchmark/v6_current_state.json` | `V6_CAPACITY_CURRENT_STATE_V1` | `d17bcd3b7c669227f920671984b502497cdca9d367523548da4130eb8f986670` |
| `evaluation/downstream_benchmark/v6_predecessor_evidence_bridge.json` | `V6_PREDECESSOR_EVIDENCE_BRIDGE_V1` | `768517998be897f3e2a2d250336e1513e0a4ddc2ac6bd590a30ea6935226e222` |
| `evaluation/downstream_benchmark/v6_reconsideration_pool.csv` | `V6_RECONSIDERATION_POOL_V1` | `42d47f13f39fbdbb335cd741e1c361b2dbf690d5e72382136a61f2608e16fe78` |

## E. 433-member canonical pool

The canonical CSV is a candidate transformation of the accepted proposal pool, with explicit
source_project, census order, schema/candidate role labels and predecessor inventory/HEAD bindings.
Every original source value, case key, rank, disposition and evidence-row identity is preserved.
433 unique members, exactly 15 projects, frozen numeric rank ascending, range 10–500 with historical
admission gaps. Independently reconstructed predecessor traversal matches every member in order.
Disjoint from all 67 historical admissions, 39 accepted exclusions and 28 screened cases.
31 initial deterministic replays and 402 literal traversal rows retain distinct lineage labels.
No membership activation or freeze occurred. The candidate CSV has its own digest in section D;
the accepted proposal digest is lineage, not a claim that differently labeled bytes have the same hash.

| Source project | Members |
| --- | ---: |
| ansible | 14 |
| black | 19 |
| fastapi | 12 |
| httpie | 1 |
| keras | 40 |
| luigi | 29 |
| matplotlib | 26 |
| pandas | 165 |
| sanic | 1 |
| scrapy | 36 |
| spacy | 6 |
| thefuck | 28 |
| tornado | 12 |
| tqdm | 5 |
| youtube-dl | 39 |

## F. Predecessor evidence bridge

500 ranked rows partition as 9 GRANDFATHERED_EVIDENCE, 12 CLOSED_SCIENTIFIC_REJECTION,
7 INFRASTRUCTURE_UNRESOLVED, 39 CLOSED_PRE_ELIGIBILITY_EXCLUSION and 433
NEWLY_RECONSIDERABLE_HISTORICAL_CAP_SKIP. The unranked keras::12 metadata exclusion remains
separate and excluded. Original admitted case rows, ledger/evidence identities, checkpoint hashes
and classifications are retained. The bridge references evidence without cloning raw evidence or
presenting old results as new V6 outcomes. Nine require no capacity rerun; twelve receive no rescue;
39 are never reopened; seven stay in their separate versioned track, outside V6 census execution.

## G. Protocol contract

EP-DBP-6-CAPACITY specifies V6_FINITE_SAME_UNIVERSE_CENSUS_WITH_EVIDENCE_CONTINUITY;
24 final + 4 permanently separate pilots; final project cap 4; minimum final coverage 6.
It narrowly supersedes only historical admission/cap-skip and outcome-triggered expansion rules
for the exact 433 never-admitted members and the named D1–D8 proposal alternatives. All other
requirements are inherited by exact digest; unlisted contradictions BLOCK for Human-PI adjudication.
No historical V1/V5 bytes, scientific question, target, oracle or downstream treatment changes.

## H. Run-spec contract

EP-DBRS-6-CAPACITY binds all nine inherited protocol/runtime/representation/build/executor
specifications by exact digest. Task bytes, RAW/ERRPILOT payload rules, Codex gpt-5.6-sol/xhigh
client identity, CLI 0.154.0 digest, no fallback, 1200-second repair budget, isolation/protection,
instrumentation/NA rules, contamination controls, taxonomy and pre-run gates remain inherited.
The architecture model named in this request does not change the frozen downstream agent.
No live downstream identity availability, runtime qualification or real session was tested.

## I. Screening contract

EP-BIPS-6-CENSUS requires one logical 433-member census, complete finite processing, original
frozen rank ascending dispatch, no governed batches, stop-at-28 or outcome-dependent membership.
No census admission/preparation project cap. Preserve BUGGY 1/2/3 then FIXED 1/2/3; six valid
scientific records, F/F/F then P/P/P only. Keep direct argv, frozen composite order, fresh state,
linux/amd64, network NONE, 300-second subcommand/900-second trial clocks, protected integrity,
expected-test observation and immutable raw evidence. No fourth trial, majority, retry or rescue.
Canonical reasons, technical status, adjudication, validity, consumption/slots and supersession
are distinct. ACCEPTED_HELD_UNRESOLVED is administrative only, never scientific failure,
eligible or automatic retry. Schema conditions reject held/scientific/eligibility contradictions.
Unaccounted or unadjudicated work blocks closure. Missing/infrastructure evidence cannot be science.

## J. Current-state / event contract

v6_current_state.json is the sole intended future effective-current path; its construction profile
is CONTRACT_CANDIDATE_ONLY, runtime_authority=false, no effective identity/current surface,
empty event chain/head, 433 NOT_STARTED placeholders, and all lifecycle/phase authority flags NO.
V6_ACTIVATED, CENSUS_MEMBERSHIP_EFFECTIVE, PREPARATION_AUTHORIZED and ORACLE_AUTHORIZED are NO.
The schema also describes a future effective profile, requiring accepted/frozen/persisted/committed
contract and explicitly activated membership. Saving a descriptor never satisfies those gates.

Append-only immutable events bind exact previous event ID/sequence/canonical payload digest,
old exact descriptor digest, contract/predecessor identity, independent Human-PI gate, and
prior/result projection digests. Hashing is canonical UTF-8 compact sorted-key JSON, no floats,
NaN, duplicate keys or self hashes; exact-file hashes are separately retained. The result projection
excludes provenance; the future descriptor binds event head/result projection; consumers pin its
exact accepted file identity externally. This directed graph has no circular hash.

Deterministic authorized event replay and descriptor agreement are mandatory. No event head,
CSV, report or competing snapshot supplies current authority. Any disagreement or unbound identity
BLOCKS. Synthetic two-edge acceptance/freeze fixtures demonstrate exact chain and separate authority
semantics; they are not real acceptance/freeze events. Runtime consumers/state writers and real
CASE_DISPOSITION/COMBINED_INPUT_FREEZE enforcement are not implemented or qualified here.

## K. D6 integration contract

FIRST_COMBINED_POOL_INPUT_FREEZE is the cutoff. The accepted census-closure snapshot fixes the
seven-track head, with no head refresh before first freeze or late inclusion afterwards. Included
superseding outcomes must already be HUMAN_PI_ACCEPTED, FROZEN, PERSISTED and COMMITTED at
that fixed head, with exact supersession, new attempt and unchanged valid six-slot criterion.
One effective outcome per case; original infrastructure slots are never reused as scientific trials.
REMOTE_PUBLISHED is not universally required for integration; applicable downstream real-execution
publication gates are retained. Late outcomes remain outside that allocation cycle, even on failure.
Synthetic tests accept a four-state fixture with REMOTE_PUBLISHED=NO and reject refresh, lateness,
missing lifecycle states, duplicate effective results, missing supersession and slot reuse.
No actual combined pool, cutoff or seven-track result is frozen or integrated in this transaction.

## L. D7 pilot contract

From a later immutable combined eligible pool, BLOCK before pilot selection if eligible count <28.
Use exact canonical strings without numeric coercion or normalization; UTF-8 SHA-256 input:
20260922|pilot|<source_project>|<bugsinpy_bug_id>|<case_id>.
Sort lowercase digest, then canonical UTF-8 source_project, bugsinpy_bug_id and case_id; reserve
first four, no pilot project cap or final-feasibility lookahead. Exclusion is permanent. No swap,
reseed, promotion, reselection or outcome-dependent selection. Then apply the unchanged predecessor
final hash order/cap-four traversal to the remaining frozen pool, selecting 24 with minimum six
projects only under separate authority. Infeasibility is BLOCK_WITHOUT_PILOT_RESELECTION.
Robustness-six and paired-condition order algorithms remain unchanged. Zero actual pilot hashes,
pilot IDs, final cases, robustness cases or condition schedules were computed.

## M. Terminal / exhaustion contract

Precedence is CLOSURE_BLOCKED > INSUFFICIENT_ELIGIBLE_CAPACITY > ALLOCATION_RULE_UNRESOLVED
> PROJECT_DIVERSITY_INFEASIBLE > ALLOCATION_AUTHORITY_REQUIRED. Primary names exactly:

- V6_CENSUS_COMPLETE_ALLOCATION_AUTHORITY_REQUIRED
- V6_CENSUS_EXHAUSTED_INSUFFICIENT_ELIGIBLE_CAPACITY
- V6_CENSUS_EXHAUSTED_PROJECT_DIVERSITY_INFEASIBLE
- V6_CENSUS_COMPLETE_ALLOCATION_RULE_UNRESOLVED
- V6_CENSUS_CLOSURE_BLOCKED

Orthogonal qualifiers are V6_CENSUS_COMPLETE_WITH_UNRESOLVED_INFRASTRUCTURE and
V6_PREPARATION_EXHAUSTED_WITH_NONSCIENTIFIC_DISPOSITIONS. Only accepted/accounted closure
supports qualifiers; no automatic expansion, repair, retry, allocation or successor follows any
status. Ten synthetic precedence tests cover all primary branches and unresolved accounting.
No actual V6 census terminal outcome is asserted by this candidate construction.

## N. State machine / authority graph

Sixteen explicit states, fifteen distinct Human-PI-owned edges. Each edge requires independent
bound authorization and its listed evidence; state completion grants no next authority. Publication
where required is a distinct gate; a not-applicable decision must be explicitly Human-PI bound.
Source acquisition, planning, materialization, builds, oracle and downstream execution retain their
own subauthorities. The current state is CONTRACT_CANDIDATE. No edge was exercised here.

| Transition | Owner | Separate gate |
| --- | --- | --- |
| CONTRACT_CANDIDATE → HUMAN_PI_CONTRACT_ACCEPTED | HUMAN_PI | `HUMAN_PI_ACCEPT_V6_SUCCESSOR_CONTRACT` |
| HUMAN_PI_CONTRACT_ACCEPTED → CONTRACT_FROZEN | HUMAN_PI | `HUMAN_PI_FREEZE_V6_SUCCESSOR_CONTRACT` |
| CONTRACT_FROZEN → CONTRACT_PERSISTED | HUMAN_PI | `HUMAN_PI_PERSIST_V6_SUCCESSOR_CONTRACT` |
| CONTRACT_PERSISTED → CONTRACT_COMMITTED | HUMAN_PI | `HUMAN_PI_AUTHORIZE_CONTRACT_COMMIT` |
| CONTRACT_COMMITTED → CONTRACT_PUBLISHED_WHERE_REQUIRED | HUMAN_PI | `HUMAN_PI_AUTHORIZE_PUBLICATION_WHERE_REQUIRED` |
| CONTRACT_PUBLISHED_WHERE_REQUIRED → CENSUS_MEMBERSHIP_ACTIVATED | HUMAN_PI | `HUMAN_PI_ACTIVATE_V6_CENSUS_MEMBERSHIP` |
| CENSUS_MEMBERSHIP_ACTIVATED → PREPARATION_PLANNING_AUTHORIZED | HUMAN_PI | `HUMAN_PI_AUTHORIZE_V6_PREPARATION_PLANNING` |
| PREPARATION_PLANNING_AUTHORIZED → PREPARATION_EXECUTION_AUTHORIZED | HUMAN_PI | `HUMAN_PI_AUTHORIZE_V6_PREPARATION_EXECUTION` |
| PREPARATION_EXECUTION_AUTHORIZED → PREPARATION_COMPLETE | HUMAN_PI | `HUMAN_PI_ACCEPT_V6_PREPARATION_CLOSURE` |
| PREPARATION_COMPLETE → ENVIRONMENT_READY_POPULATION_FROZEN | HUMAN_PI | `HUMAN_PI_FREEZE_V6_READY_POPULATION` |
| ENVIRONMENT_READY_POPULATION_FROZEN → ORACLE_EXECUTION_AUTHORIZED | HUMAN_PI | `HUMAN_PI_AUTHORIZE_V6_ORACLE_EXECUTION` |
| ORACLE_EXECUTION_AUTHORIZED → ORACLE_COMPLETE | HUMAN_PI | `HUMAN_PI_ACCEPT_V6_ORACLE_CLOSURE` |
| ORACLE_COMPLETE → COMBINED_ELIGIBLE_POOL_FROZEN | HUMAN_PI | `HUMAN_PI_FREEZE_COMBINED_ELIGIBLE_POOL` |
| COMBINED_ELIGIBLE_POOL_FROZEN → PILOT_FINAL_ALLOCATION_AUTHORIZED | HUMAN_PI | `HUMAN_PI_AUTHORIZE_PILOT_FINAL_ALLOCATION` |
| PILOT_FINAL_ALLOCATION_AUTHORIZED → ALLOCATION_COMPLETE | HUMAN_PI | `HUMAN_PI_ACCEPT_ALLOCATION` |

## O. Rejection matrix

141/141 new in-memory rejection probes PASS_REJECTED; 0 accepted bad mutations, 0 failures.
All 28 required categories are explicitly covered (BugsInPy commit and tree, both bad pool sizes,
D6 policy and actual synthetic head refresh/lateness are separate probes). The matrix additionally
rejects every one of the 62 accepted semantic fields changed to null, unbound/duplicate event
identities, candidate authority leaks, bridge clones, trial-rule changes and seven-track lifecycle
or supersession defects. See validation_results.json for every probe and exact rejection reason.
Inherited predecessor matrix: 28/28 rejections passed separately.

## P. Tests / static validation

- Candidate auditor: 27 positive checks PASS, 141 rejections PASS, 0 failed.
- New non-production pytest suite: 23 passed, 0 failed (final run 6.79 seconds).
- Inherited original proposal auditor: 29 positive checks PASS, 28 rejections PASS, 0 failed;
  only its process-local new-file allowlist was extended, not any semantic check or disk file.
- Historical finalized semantic/source checks were rerun directly. Its complete historical main
  was not rerun because it correctly asserts absence of canonical contract files at the earlier
  design stage; those obsolete entry assertions are not successor construction gates.
- Eight schemas passed Draft202012Validator.check_schema; candidate document, pool, bridge,
  lifecycle and descriptor instances passed their contracts; synthetic event cases passed schema
  and chain checks. Real runtime consumers are absent and not claimed as tested.
- Changed-source Ruff check and format --check PASS; source compile and UTF-8/JSON/whitespace
  checks PASS; git diff --check and cached diff --check PASS. The explicit new-file whitespace
  check covers untracked files, which git diff --check alone does not inspect.
- Existing .venv Python/jsonschema/pytest/Ruff were used. No dependency was installed. The
  initial system/bundled runtime probes lacked these tools and were not subject-environment
  modifications. No repository-wide test suite or subject oracle was run.

Commands run (bounded inspection/construction/validation):

```text
cat <bound request>; cat/sed/head/rg local governing designs, specifications and inventories
pwd; git status --short --untracked-files=all; git branch --show-current; git rev-parse HEAD
git diff --cached --name-only; git diff --name-only; git ls-files --others --exclude-standard
git ls-remote --exit-code origin refs/heads/main
git -C /Users/wuyangchenxi/errpilot-benchmark-work/bugsinpy rev-parse HEAD HEAD^{tree}
git -C /Users/wuyangchenxi/errpilot-benchmark-work/bugsinpy status --porcelain
python3 -B <bounded read/hash/runtime availability probes>
.venv/bin/python -B /private/tmp/errpilot_build_v6_candidate.py
.venv/bin/python -B /private/tmp/errpilot_refine_v6_schemas.py
.venv/bin/python -B /private/tmp/errpilot_strengthen_v6_schema.py
.venv/bin/python -B /private/tmp/errpilot_bind_sixslot_schema.py
.venv/bin/python -B /private/tmp/errpilot_guard_runtime_profile.py
.venv/bin/ruff format evaluation/downstream_benchmark/evidence/v6_successor_contract_construction_v1/{validate_contract,test_contract}.py
.venv/bin/ruff check evaluation/downstream_benchmark/evidence/v6_successor_contract_construction_v1/{validate_contract,test_contract}.py
.venv/bin/ruff format --check evaluation/downstream_benchmark/evidence/v6_successor_contract_construction_v1/{validate_contract,test_contract}.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider evaluation/downstream_benchmark/evidence/v6_successor_contract_construction_v1/test_contract.py
.venv/bin/python -B evaluation/downstream_benchmark/evidence/v6_successor_contract_construction_v1/validate_contract.py
git diff --check; git diff --cached --check
.venv/bin/python -B /private/tmp/errpilot_seal_v6_candidate.py
```

The read-only workspace dependency locator was also queried; its bundled runtime was not used
for validation after the existing repository .venv was found. Scratch files are confined to
/private/tmp. Contract sources/evidence are the 22 new repository paths in section D.

## Q. New file inventory

22 new paths = 8 candidate contract/data files + 8 explicit schemas + 6 construction evidence
files (entry, auditor, tests, results, report, hash inventory). Section D names every exact path.
No production package/harness/executor source or .airos state was modified. The inventory binds
21 files, excludes itself, and is independently sealed in the final chat.

## R. Worktree / index

Final expected worktree: exactly 41 untracked paths = 19 preserved historical inputs + 22 new
candidate paths. No tracked diff; index empty. Branch main and HEAD unchanged. Live origin/main
was verified at entry; there was no fetch, stage, commit or push. The closing auditor verifies
exact path population, every historical hash and the complete new inventory after sealing.

## S. Firewall

```text
CONTRACT_ACCEPTED = NO
CONTRACT_FROZEN = NO
CONTRACT_PERSISTED = NO
CONTRACT_COMMITTED = NO
CONTRACT_PUBLISHED = NO
V6_ACTIVATED = NO
MEMBERSHIP_EFFECTIVE = NO
CASE_PREPARED = NO
IMAGE_BUILT = NO
ORACLE_EXECUTED = NO
PILOT_SELECTED = NO
FINAL_CASE_SELECTED = NO
GIT_STAGE = NO
GIT_COMMIT = NO
GIT_PUSH = NO
```

No acquisition/materialization, build, Docker subject command, oracle, unresolved-seven repair
or rerun, pilot/final allocation, model request, V5 rewrite or downstream authority occurred.
Saving candidate files is not canonical accepted persistence, freeze, publication or activation.

## T. Lifecycle / contract compliance / risks and unknowns

V6_SUCCESSOR_CONTRACT = CANDIDATE_ONLY. Construction stayed within the direct authorized scope,
preserved all 19 immutable inputs, and added only candidate contracts/schemas/validators/evidence.
Assumption: the bound latest direct Human-PI instruction is the acceptance/construction authority
for the exact design digests it names; earlier stored status text is historical and remains intact.
Internal contract/test consistency is not scientific validation, execution qualification or a
research claim. Candidate contract acceptance, freeze, canonical persistence, commit/publication,
activation and downstream work remain separate decisions. Real runtime writers/consumers,
preparation/oracle implementations, cutoff evidence, subject environments, live client identity
and allocation feasibility are not implemented or qualified by this transaction. No actual
pilot IDs or capacity/diversity outcome is available yet. No approval question or further
execution is initiated by this report.

## U. Next gate / recommended next action

NEXT_GATE = HUMAN_PI_REVIEW_OF_V6_SUCCESSOR_CONTRACT_CANDIDATE.
Recommend Human-PI review of the exact candidate artifacts, schema/gate contracts, rejection
matrix and hash inventory. This recommendation is not acceptance or activation authority.
No activation authority is granted. Stop.

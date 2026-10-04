# V6 Activation Runtime Genesis Human-PI Semantic Decision

2026-10-04, Europe/Budapest. Direct Human-PI adoption; no agent acceptance decision.

SEMANTICS ADOPTED

BRIDGE NOT YET HUMAN_PI_ACCEPTED

ACTIVATION NOT AUTHORIZED BY THIS RECORD

The established repository convention uses a separate Human-PI decision record.
The following controlling S1–S6 and hash model are copied exactly from this transaction request.

```text
============================================================
ADOPTED SEMANTIC DECISION — CONTROLLING
============================================================

The following Human-PI semantics are now controlling.

------------------------------------------------------------
S1 — RUNTIME GENESIS SOURCE
------------------------------------------------------------

S1 =
    PUBLISHED_CONTRACT_BASELINE_EXTERNAL_QUALIFICATION

Define a qualification function Q.

Q must:

1. consume the exact raw predecessor projection;

2. verify:
       published baseline commit
       lifecycle closure identity
       contract manifest identity
       canonical pool identity
       predecessor evidence bridge identity;

3. set the QUALIFIED REPLAY SEED lifecycle state to:

       CONTRACT_PUBLISHED_WHERE_REQUIRED

4. set ONLY the five contract-lifecycle flags represented by that lifecycle
   advancement to YES;

5. preserve every:
       membership field
       preparation field
       execution-authority field
       case/work accounting field
       allocation field
       closure/scientific field;

6. create:
       NO event
       NO effective descriptor
       NO runtime authority.

The raw predecessor bytes remain immutable.

Raw predecessor projection SHA-256 recovered by adjudication:

    f15fd874b21a39d11d9117f6a4aa75b46dde1be4562f35557aa6b60ca08be840

The future first event must bind:

    previous_descriptor_sha256 =
        raw predecessor descriptor bytes

while:

    prior_projection_sha256 =
        Q(raw predecessor projection)

This distinction MUST be explicitly encoded by the bridge.

------------------------------------------------------------
S2 — FIRST EVENT PREDECESSOR
------------------------------------------------------------

S2 =
    NULL_EVENT_PREDECESSOR_WITH_EXTERNAL_BASELINE_BINDING

For the future first activation event:

    sequence = 1
    previous_event_identity = null

Do NOT invent undeclared fields:

    previous_event_id
    previous_event_hash

The first event may later be:

    CENSUS_MEMBERSHIP_ACTIVATION

only after this bridge itself becomes accepted/effective and separate activation
authority is granted.

No synthetic genesis event.
No publication backfill event.

------------------------------------------------------------
S3 — EVENT IDENTITY
------------------------------------------------------------

S3 =
    SHA256_OF_CANONICAL_EVENT_CORE

event_core is all permitted V1 event fields EXCEPT:

    event_id

Required event-core fields are the existing V1 fields:

    schema
    namespace
    sequence
    kind
    previous_event_identity
    previous_descriptor_sha256
    contract_sha256
    authority_reference
    gate
    from_state
    to_state
    prior_projection_sha256
    result_projection_sha256
    next_projection
    evidence_references
    supersession_reference
    predecessor

Canonicalization:

    UTF-8 JSON
    sort_keys = true
    separators = (",", ":")
    ensure_ascii = false
    allow_nan = false

    no insignificant whitespace
    no trailing newline
    no BOM
    duplicate keys rejected
    floats rejected
    non-JSON values rejected
    invalid Unicode scalar strings rejected
    array order preserved
    exact strings preserved
    no trimming
    no Unicode normalization

Then:

    event_id =
    lowercase_hex(SHA256(canonical_event_core_bytes))

The existing:

    sequence

field belongs in event_core.

No timestamp is added to the V1 event payload.

Exact required future genesis evidence-reference set:

    accepted genesis bridge
    lifecycle closure
    canonical pool
    predecessor evidence bridge

Ordering:

    UTF-8 path bytes
    then digest

Reject duplicate/conflicting references.

Future first-event:

    supersession_reference =
        exact accepted genesis bridge

Keep distinct:

    event_id
    event_sha256
    file_sha256

Definitions:

    event_id =
        SHA256(canonical(core_without_event_id))

    event_sha256 =
        SHA256(canonical(complete_event))

    file_sha256 =
        SHA256(exact_stored_event_bytes)

No event/file self-hash is stored in the event.

------------------------------------------------------------
S4 — NON-EFFECTIVE TRANSITION CANDIDATE
------------------------------------------------------------

S4 =
    NON_EFFECTIVE_TRANSITION_CANDIDATE

Representation:

    external envelope
    +
    existing V1 payload schemas

Do NOT modify the closed V1 schemas to insert a `profile` field.

Required envelope assertions:

    profile =
        NON_EFFECTIVE_TRANSITION_CANDIDATE

    PROPOSED_V6_ACTIVATED = YES
    PROPOSED_MEMBERSHIP_EFFECTIVE = YES
    PROPOSED_EVENT_COUNT = 1

    CANONICAL_V6_ACTIVATED = NO
    CANONICAL_MEMBERSHIP_EFFECTIVE = NO
    CANONICAL_EVENT_COUNT = 0

    RUNTIME_EFFECTIVE = NO

    CURRENT_AUTHORITY =
        UNCHANGED_CANONICAL_PREDECESSOR_DESCRIPTOR

    CANONICAL_RUNTIME_AUTHORITY = NONE

    CANONICAL_INSTALLATION_AUTHORIZED_BY_CANDIDATE = NO

    AUTO_PROMOTION = NO

    CURRENT_REGISTRATION = PROHIBITED

A future nested V1 post-state preview may use:

    candidate_only = false
    runtime_authority = false
    effective_current_descriptor_identity = null
    authoritative_current_surfaces = []

The outer envelope, not an undeclared V1 field, establishes candidate status.

Future proposed event namespace may be:

    EFFECTIVE_V6

but namespace alone MUST confer no authority.

Current-state consumers must never discover candidates via:

    glob
    latest
    mtime
    lexical selection
    namespace label

------------------------------------------------------------
S5 — EFFECTIVITY BOUNDARY
------------------------------------------------------------

S5 =
    FOUR_STATE_PLUS_APPLICABLE_PUBLICATION_AND_EXACT_CANONICAL_INSTALLATION

Required activation-artifact lifecycle before installation:

    HUMAN_PI_ACCEPTED
    FROZEN
    PERSISTED
    COMMITTED

Publication applicability:

    CONTRACT_BASELINE_PUBLICATION =
        REQUIRED_AND_ALREADY_EVIDENCED

    MEMBERSHIP_ACTIVATION_ARTIFACT_REMOTE_PUBLICATION =
        NOT_APPLICABLE_TO_SEMANTIC_MEMBERSHIP_INSTALLATION

    REAL_DOWNSTREAM_EXECUTION_PUBLICATION_GATES =
        RETAIN

The second rule is an explicit Human-PI semantic decision.

Effectivity operation:

    COMPARE_AND_INSTALL_EXACT_ACCEPTED_SUCCESSOR_AT_CANONICAL_PATH

Future installation must:

1. compare expected predecessor identity;

2. install the exact accepted successor at the sole canonical:

       v6_current_state.json

3. verify:
       committed bytes
       independent exact successor acceptance pin
       genesis bridge
       event chain
       applicable publication gates;

4. begin runtime effectivity ONLY after successful installation verification.

The following are insufficient by themselves:

    candidate creation
    Human-PI acceptance
    persistence
    commit
    copy/save

unless the exact authorized installation completes.

------------------------------------------------------------
S6 — EVENT CHAIN BOOTSTRAP
------------------------------------------------------------

S6 =
    SINGLE_ACTIVATION_EVENT_BOOTSTRAP_NO_BACKFILL

After later separately authorized effective installation:

    event_count = 1

and existing V1 representation:

    event_head = {
        event_id: activation_event_id,
        sequence: 1,
        event_sha256: canonical_complete_event_payload_hash
    }

No synthetic genesis event.
No contract-publication event.
No historical backfill.

The sole chain entry must bind:

    event path
    file SHA-256
    event_id
    sequence
    canonical complete payload SHA-256

The descriptor's existing `predecessor` field retains its frozen historical V5
meaning.

Do NOT repurpose it as the V6 predecessor-descriptor pointer.

For event 2+:

    sequence += 1
    previous_event_identity = exact prior event head
    previous_descriptor_sha256 = prior installed descriptor
    prior projection = replayed prior state
    ordinary gate/result/evidence/consumption checks apply

Genesis qualification occurs ONCE and can never be reset/reapplied later.

============================================================
HASH / IDENTITY MODEL — CONTROLLING
============================================================

Bridge construction must enforce an ACYCLIC model.

Required dependency structure:

    immutable predecessor bytes
        -> predecessor descriptor SHA

    raw predecessor projection
        -> raw projection SHA

    contract bytes
        -> contract manifest SHA

    closure bytes
        -> closure SHA

    pool bytes
        -> pool SHA

    exact baseline identities
        -> genesis bridge
        -> bridge SHA

    raw projection + Q
        -> qualified genesis projection
        -> qualified projection SHA

Future-only:

    qualified projection + activation delta
        -> result projection

    fixed references + prior/result identities
        -> event core
        -> event_id

    event core + event_id
        -> complete event
        -> event_sha256 / file_sha256

    event + installation-scope authority + result projection
        -> successor descriptor

Prohibit:

    event_id depending on event/file hash

    event containing successor descriptor hash

    descriptor containing own file hash

    authority referenced by event containing future event ID/hash

    bridge containing future event identity

    bridge containing future successor descriptor identity

    bridge containing its own hash

    bridge containing future enclosing commit identity

    successor descriptor backward-reference to an acceptance pin which itself
    hashes the successor

Require:

    NO_HASH_CYCLE = YES
```

<!-- BEGIN DECISION_JSON -->
```json
{
  "S1_S6": {
    "S1": "PUBLISHED_CONTRACT_BASELINE_EXTERNAL_QUALIFICATION",
    "S2": "NULL_EVENT_PREDECESSOR_WITH_EXTERNAL_BASELINE_BINDING",
    "S3": "SHA256_OF_CANONICAL_EVENT_CORE",
    "S4": "NON_EFFECTIVE_TRANSITION_CANDIDATE",
    "S5": "FOUR_STATE_PLUS_APPLICABLE_PUBLICATION_AND_EXACT_CANONICAL_INSTALLATION",
    "S6": "SINGLE_ACTIVATION_EVENT_BOOTSTRAP_NO_BACKFILL"
  },
  "activation_authorized": "NO",
  "authority": {
    "decision": "HUMAN_PI_V6_ACTIVATION_RUNTIME_GENESIS_SEMANTIC_DECISION",
    "path": "/Users/wuyangchenxi/.codex/attachments/c00459b2-e155-42b7-abb1-b853bfd3f3bf/已粘贴的文本.txt",
    "sha256": "118e831729095ff80d2269dce90848a4d0f975ef248f02045e14a2736a987ba0",
    "transaction": "OPEN_V6_ACTIVATION_RUNTIME_GENESIS_BRIDGE_CONSTRUCTION_V1"
  },
  "baseline_commit": "d5146d86fc2b36b336d1bdf2657a6cbdfde84f8c",
  "baseline_sha256": {
    "canonical_pool": "42d47f13f39fbdbb335cd741e1c361b2dbf690d5e72382136a61f2608e16fe78",
    "closure": "977ee418f4ac3d84cf66af5943beea75fab3e38ba8c086211f22312c9bd46ac9",
    "contract_manifest": "4401b7c145d8a39c9a33f095f57c13a14bf6887d5848c116fe240631472810a7",
    "predecessor_descriptor": "d17bcd3b7c669227f920671984b502497cdca9d367523548da4130eb8f986670",
    "predecessor_evidence_bridge": "768517998be897f3e2a2d250336e1513e0a4ddc2ac6bd590a30ea6935226e222"
  },
  "bridge_human_pi_accepted": "NO",
  "bridge_lifecycle": {
    "COMMITTED": "NO",
    "FROZEN": "NO",
    "HUMAN_PI_ACCEPTED": "NO",
    "PERSISTED": "NO",
    "REMOTE_PUBLISHED": "NO"
  },
  "bridge_required": "V6_ACTIVATION_RUNTIME_GENESIS_BRIDGE_V1",
  "hash_model": "ACYCLIC; immutable inputs -> decision -> bridge; qualified projection is derived evidence; future core -> event_id -> complete event -> successor; independent acceptance pin hashes successor without a successor backward reference",
  "identity": "HUMAN_PI_V6_ACTIVATION_RUNTIME_GENESIS_SEMANTIC_DECISION",
  "negative_authority": "BRIDGE CONSTRUCTION ONLY; no real activation event/post-state/install, canonical change, preparation/acquisition/materialization/build/Docker/oracle/seven repair/rerun/pilot/final allocation/stage/commit/push/tag",
  "payload_schema_policy": "RETAIN_EXISTING_V1_SCHEMAS_WITH_EXTERNAL_CANDIDATE_PROFILE",
  "schema": "V6_ACTIVATION_RUNTIME_GENESIS_HUMAN_PI_SEMANTIC_DECISION_V1",
  "semantic_status": "SEMANTICS ADOPTED",
  "successor_payload_schemas_required": "NO"
}
```
<!-- END DECISION_JSON -->

PERSISTED = NO is the formal bridge lifecycle gate. Saving candidate/decision evidence
locally does not attest formal acceptance, freeze, persistence, commit or publication.

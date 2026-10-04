"""Pure V6 genesis semantics, candidate only; no installer or runtime consumer.

Frozen V1 schemas are loaded and hash-checked once. External evidence is explicit
input. All acceptance/installation examples in test_bridge.py are synthetic.
Nothing in this module grants authority or discovers a current descriptor.
"""

import copy
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator

E = Path(__file__).resolve().parent
B = E.parents[1]
ROOT = B.parents[1]
PREFIX = "evaluation/downstream_benchmark/"
BASELINE = "d5146d86fc2b36b336d1bdf2657a6cbdfde84f8c"
BRIDGE_PATH = PREFIX + "v6_activation_runtime_genesis_bridge_v1.json"
CURRENT_PATH = PREFIX + "v6_current_state.json"
DECISION_PATH = PREFIX + "V6_ACTIVATION_RUNTIME_GENESIS_HUMAN_PI_SEMANTIC_DECISION.md"
DECISION_SHA = "8bbe8de76196a780504362736c9af9a159c29e0ba111b838a5f6dfc2dccf9ab7"
RAW_SHA = "f15fd874b21a39d11d9117f6a4aa75b46dde1be4562f35557aa6b60ca08be840"
IDENTITIES = {
    "predecessor_descriptor": (
        "v6_current_state.json",
        "d17bcd3b7c669227f920671984b502497cdca9d367523548da4130eb8f986670",
    ),
    "lifecycle_closure": (
        "V6_SUCCESSOR_CONTRACT_LIFECYCLE_CLOSURE_V1.md",
        "977ee418f4ac3d84cf66af5943beea75fab3e38ba8c086211f22312c9bd46ac9",
    ),
    "contract_manifest": (
        "v6_capacity_successor_contract.json",
        "4401b7c145d8a39c9a33f095f57c13a14bf6887d5848c116fe240631472810a7",
    ),
    "canonical_pool": (
        "v6_reconsideration_pool.csv",
        "42d47f13f39fbdbb335cd741e1c361b2dbf690d5e72382136a61f2608e16fe78",
    ),
    "predecessor_evidence_bridge": (
        "v6_predecessor_evidence_bridge.json",
        "768517998be897f3e2a2d250336e1513e0a4ddc2ac6bd590a30ea6935226e222",
    ),
}
FLAGS = [
    "CONTRACT_ACCEPTED",
    "CONTRACT_FROZEN",
    "CONTRACT_PERSISTED",
    "CONTRACT_COMMITTED",
    "CONTRACT_PUBLISHED_WHERE_REQUIRED",
]
SEMANTICS = {
    "S1": "PUBLISHED_CONTRACT_BASELINE_EXTERNAL_QUALIFICATION",
    "S2": "NULL_EVENT_PREDECESSOR_WITH_EXTERNAL_BASELINE_BINDING",
    "S3": "SHA256_OF_CANONICAL_EVENT_CORE",
    "S4": "NON_EFFECTIVE_TRANSITION_CANDIDATE",
    "S5": "FOUR_STATE_PLUS_APPLICABLE_PUBLICATION_AND_EXACT_CANONICAL_INSTALLATION",
    "S6": "SINGLE_ACTIVATION_EVENT_BOOTSTRAP_NO_BACKFILL",
}
CORE_FIELDS = [
    "schema",
    "namespace",
    "sequence",
    "kind",
    "previous_event_identity",
    "previous_descriptor_sha256",
    "contract_sha256",
    "authority_reference",
    "gate",
    "from_state",
    "to_state",
    "prior_projection_sha256",
    "result_projection_sha256",
    "next_projection",
    "evidence_references",
    "supersession_reference",
    "predecessor",
]
ASSERTIONS = {
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
    "CURRENT_REGISTRATION": "PROHIBITED",
}
PUBLICATION = {
    "CONTRACT_BASELINE_PUBLICATION": "REQUIRED_AND_ALREADY_EVIDENCED",
    "MEMBERSHIP_ACTIVATION_ARTIFACT_REMOTE_PUBLICATION": "NOT_APPLICABLE_TO_SEMANTIC_MEMBERSHIP_INSTALLATION",
    "REAL_DOWNSTREAM_EXECUTION_PUBLICATION_GATES": "RETAIN",
}
FOUR = ["HUMAN_PI_ACCEPTED", "FROZEN", "PERSISTED", "COMMITTED"]
OPERATION = "COMPARE_AND_INSTALL_EXACT_ACCEPTED_SUCCESSOR_AT_CANONICAL_PATH"
EDGES = [
    ["predecessor_bytes", "predecessor_sha"],
    ["raw_projection", "raw_sha"],
    ["contract_bytes", "contract_sha"],
    ["closure_bytes", "closure_sha"],
    ["pool_bytes", "pool_sha"],
    ["predecessor_bridge_bytes", "predecessor_bridge_sha"],
    ["decision_bytes", "decision_sha"],
    *[
        [n, "genesis_bridge"]
        for n in [
            "predecessor_sha",
            "raw_sha",
            "contract_sha",
            "closure_sha",
            "pool_sha",
            "predecessor_bridge_sha",
            "baseline_commit",
            "decision_sha",
        ]
    ],
    ["genesis_bridge", "bridge_sha"],
    ["raw_projection", "qualified_projection"],
    ["genesis_bridge", "qualified_projection"],
    ["qualified_projection", "qualified_sha"],
    ["qualified_projection", "result_projection"],
    ["activation_delta", "result_projection"],
    ["result_projection", "result_sha"],
    ["qualified_sha", "event_core"],
    ["result_sha", "event_core"],
    ["bridge_sha", "event_core"],
    ["predecessor_sha", "event_core"],
    ["event_scope_authority", "event_core"],
    ["fixed_evidence", "event_core"],
    ["event_core", "event_id"],
    ["event_core", "complete_event"],
    ["event_id", "complete_event"],
    ["complete_event", "event_sha"],
    ["stored_event_bytes", "file_sha"],
    ["complete_event", "stored_event_bytes"],
    ["event_sha", "successor_descriptor"],
    ["file_sha", "successor_descriptor"],
    ["result_projection", "successor_descriptor"],
    ["installation_scope_authority", "successor_descriptor"],
    ["successor_descriptor", "successor_sha"],
    ["successor_sha", "independent_acceptance_pin"],
]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    require(type(data) is bytes, "exact bytes required")
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    def inspect(item):
        require(type(item) in (dict, list, str, int, bool, type(None)), "non-JSON or float value")
        if type(item) is str:
            require(not any(0xD800 <= ord(c) <= 0xDFFF for c in item), "invalid Unicode scalar")
        elif type(item) is dict:
            for key, child in item.items():
                require(type(key) is str, "non-string JSON key")
                inspect(key)
                inspect(child)
        elif type(item) is list:
            for child in item:
                inspect(child)

    inspect(value)
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")


def digest(value):
    return sha(canonical(value))


def loads(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result

    if type(raw) is bytes:
        raw = raw.decode("utf-8")
    require(type(raw) is str and not raw.startswith("\ufeff"), "BOM/non-text JSON")
    result = json.loads(raw, object_pairs_hook=pairs)
    canonical(result)
    return result


def acyclic(edges):
    graph = {}
    for parent, child in edges:
        graph.setdefault(parent, []).append(child)
    seen, active = set(), set()

    def visit(node):
        require(node not in active, "hash dependency cycle")
        if node in seen:
            return
        active.add(node)
        for child in graph.get(node, []):
            visit(child)
        active.remove(node)
        seen.add(node)

    for node in graph:
        visit(node)


def bridge_spec():
    spec = {
        "schema": "V6_ACTIVATION_RUNTIME_GENESIS_BRIDGE_V1",
        "identifier": "V6_ACTIVATION_RUNTIME_GENESIS_BRIDGE_V1",
        "status": "CANDIDATE_ONLY",
        "runtime_authority": False,
        "lifecycle": {k: "NO" for k in FOUR + ["REMOTE_PUBLISHED"]},
        "authority": {"path": DECISION_PATH, "sha256": DECISION_SHA},
        "baseline_commit": BASELINE,
        "baseline": {k: {"path": PREFIX + p, "sha256": h} for k, (p, h) in IDENTITIES.items()},
        "raw_predecessor_projection_sha256": RAW_SHA,
        "adopted_semantics": SEMANTICS,
        "payload_schema_policy": "RETAIN_EXISTING_V1_SCHEMAS_WITH_EXTERNAL_CANDIDATE_PROFILE",
        "successor_payload_schemas_required": "NO",
        "bridge_aware_semantic_validation": "REQUIRED",
        "supersedes_only": [
            "initial replay-seed interpretation",
            "first-event genesis qualification",
            "deterministic event_id rule",
            "non-effective candidate-envelope semantics",
            "activation effectivity/install applicability",
            "one-event bootstrap semantics",
        ],
        "does_not_supersede": [
            "V6 candidate universe",
            "433-member pool",
            "ranking",
            "seed",
            "preparation semantics",
            "oracle semantics",
            "3x3 eligibility",
            "pilot rule",
            "final allocation rule",
            "predecessor scientific outcomes",
            "exclusions",
            "unresolved-seven repair policy",
        ],
        "qualification": {
            "input": "EXACT_RAW_PREDECESSOR_DESCRIPTOR_BYTES_AND_ITS_EXACT_RAW_PROJECTION",
            "verify": list(IDENTITIES)
            + ["published_baseline_commit", "closure_four_state_lifecycle"],
            "state": "CONTRACT_PUBLISHED_WHERE_REQUIRED",
            "only_flags_set_yes": FLAGS,
            "all_other_projection_fields": "PRESERVE_EXACTLY",
            "event_created": "NO",
            "effective_descriptor_created": "NO",
            "runtime_authority": "NONE",
            "only_sequence": 1,
            "existing_event_count": 0,
            "existing_event_head": None,
            "reapply_after_bootstrap": "PROHIBITED",
            "previous_descriptor_sha256": "SHA256_OF_RAW_PREDECESSOR_DESCRIPTOR_BYTES",
            "prior_projection_sha256": "SHA256_OF_CANONICAL_Q_RAW_PROJECTION",
            "qualified_projection_identity_location": "DERIVED_EVIDENCE_ONLY_NOT_CANONICAL_CURRENT",
        },
        "genesis": {
            "sequence": 1,
            "previous_event_identity": None,
            "undeclared_predecessor_fields": "PROHIBITED",
            "semantic_operation": "CENSUS_MEMBERSHIP_ACTIVATION",
            "v1_kind": "STATE_TRANSITION",
            "from_state": "CONTRACT_PUBLISHED_WHERE_REQUIRED",
            "to_state": "CENSUS_MEMBERSHIP_ACTIVATED",
            "gate": "HUMAN_PI_ACTIVATE_V6_CENSUS_MEMBERSHIP",
            "authority": "SEPARATE_AFTER_EXACT_BRIDGE_ACCEPTANCE_AND_EFFECTIVITY",
            "no_synthetic_genesis_or_publication_backfill": True,
            "evidence_reference_set": [
                "exact accepted genesis bridge",
                "lifecycle_closure",
                "canonical_pool",
                "predecessor_evidence_bridge",
            ],
            "evidence_reference_order": "UTF8_PATH_BYTES_THEN_DIGEST",
            "duplicate_conflicting_references": "REJECT",
            "supersession_reference": "EXACT_ACCEPTED_GENESIS_BRIDGE",
        },
        "event_identity": {
            "core_fields": CORE_FIELDS,
            "excluded_field": "event_id",
            "timestamp_added": "NO",
            "encoding": "UTF-8",
            "sort_keys": True,
            "separators": [",", ":"],
            "ensure_ascii": False,
            "allow_nan": False,
            "insignificant_whitespace": "NONE",
            "trailing_newline": "NONE",
            "BOM": "NONE",
            "duplicate_keys": "REJECT",
            "floats": "REJECT",
            "non_JSON": "REJECT",
            "invalid_Unicode_scalars": "REJECT",
            "array_order": "PRESERVE",
            "strings": "EXACT_NO_TRIM_NO_UNICODE_NORMALIZATION",
            "event_id": "LOWERCASE_HEX_SHA256_CANONICAL_CORE_WITHOUT_EVENT_ID",
            "event_sha256": "SHA256_CANONICAL_COMPLETE_EVENT",
            "file_sha256": "SHA256_EXACT_STORED_EVENT_BYTES",
            "event_or_file_self_hash_stored_in_event": "NO",
        },
        "candidate_envelope": {
            "assertions": ASSERTIONS,
            "representation": "EXTERNAL_ENVELOPE_PLUS_EXISTING_V1_PAYLOADS",
            "nested_preview": {
                "candidate_only": False,
                "runtime_authority": False,
                "effective_current_descriptor_identity": None,
                "authoritative_current_surfaces": [],
            },
            "proposed_namespace": "EFFECTIVE_V6",
            "namespace_alone_confers_authority": "NO",
            "current_discovery_by": {
                k: "PROHIBITED"
                for k in ["glob", "latest", "mtime", "lexical_selection", "namespace_label"]
            },
        },
        "effectivity": {
            "required_artifact_lifecycle": FOUR,
            "publication": PUBLICATION,
            "operation": OPERATION,
            "sole_canonical_path": CURRENT_PATH,
            "checks": [
                "compare expected predecessor identity",
                "exact committed successor bytes",
                "independent exact acceptance pin with no descriptor back-reference",
                "exact accepted effective genesis bridge",
                "full event chain",
                "applicable publication gates",
                "exact authorized installation",
                "post-install byte verification",
            ],
            "runtime_begins": "ONLY_AFTER_SUCCESSFUL_INSTALLATION_VERIFICATION",
            "alone_insufficient": [
                "candidate creation",
                "Human-PI acceptance",
                "persistence",
                "commit",
                "copy/save",
            ],
            "installation_implemented": "NO",
            "real_downstream_execution_authorized": "NO",
        },
        "bootstrap": {
            "event_count": 1,
            "event_head_fields": ["event_id", "sequence", "event_sha256"],
            "sole_entry_fields": ["path", "sha256", "event_id", "sequence", "event_sha256"],
            "descriptor_predecessor": "RETAIN_FROZEN_HISTORICAL_V5_MEANING",
            "event_2_plus": "INCREMENT_SEQUENCE; EXACT_PRIOR_HEAD; PRIOR_INSTALLED_DESCRIPTOR; REPLAYED_PRIOR_PROJECTION; ORDINARY_GATE_RESULT_EVIDENCE_CONSUMPTION_CHECKS",
            "genesis_qualification": "ONCE_AT_SEQUENCE_1_NEVER_RESET_OR_REAPPLIED",
        },
        "hash_model": {
            "NO_HASH_CYCLE": "YES",
            "edges": EDGES,
            "prohibited": [
                "event_id depending on event/file hash",
                "event containing successor descriptor hash",
                "descriptor containing own file hash",
                "event authority containing future event identity",
                "bridge containing future event identity",
                "bridge containing future successor descriptor identity",
                "bridge containing own hash",
                "bridge containing future enclosing commit identity",
                "descriptor backward-reference to acceptance pin hashing successor",
            ],
        },
        "negative_authority": "NO_REAL_EVENT_POST_STATE_INSTALL_ACTIVATION_PREPARATION_ACQUISITION_MATERIALIZATION_BUILD_DOCKER_ORACLE_SEVEN_REPAIR_RERUN_PILOT_FINALS_STAGE_COMMIT_PUSH_TAG",
    }
    return copy.deepcopy(spec)


def validate_bridge(bridge):
    canonical(bridge)
    acyclic(bridge.get("hash_model", {}).get("edges", []))
    require(
        canonical(bridge) == canonical(bridge_spec()),
        "bridge identity or closed adopted semantics drift",
    )


SCHEMAS = {}
for _name, _hash in {
    "V6_CAPACITY_STATE_EVENT_V1": "02988699eaf98e042c4798beb3862f9308deba386e6a9c066b365d145f3022b7",
    "V6_CAPACITY_CURRENT_STATE_V1": "cc326c0e8099bc19bf9c002ad48af68cbf488360e4bbb8cb9e0e0266b017b0f9",
}.items():
    _raw = (B / "v6_contract_schemas" / (_name + ".schema.json")).read_bytes()
    require(sha(_raw) == _hash, "frozen V1 schema drift")
    SCHEMAS[_name] = Draft202012Validator(loads(_raw))


def schema(name, value):
    canonical(value)
    errors = list(SCHEMAS[name].iter_errors(value))
    require(
        not errors, "closed V1 schema rejection" + (": " + errors[0].json_path if errors else "")
    )


def qualify_runtime_genesis(predecessor, bridge, external_baseline_evidence):
    validate_bridge(bridge)
    evidence = external_baseline_evidence
    require(
        set(evidence)
        == {
            "baseline_commit",
            "published_baseline_commit",
            "artifacts",
            "next_sequence",
            "prior_event_count",
            "prior_event_head",
        },
        "baseline evidence fields drift",
    )
    require(
        evidence["baseline_commit"] == evidence["published_baseline_commit"] == BASELINE,
        "wrong published baseline commit",
    )
    require(
        type(evidence["next_sequence"]) is int
        and evidence["next_sequence"] == 1
        and type(evidence["prior_event_count"]) is int
        and evidence["prior_event_count"] == 0
        and evidence["prior_event_head"] is None,
        "Q forbidden after genesis",
    )
    require(
        set(evidence["artifacts"]) == set(IDENTITIES) - {"predecessor_descriptor"},
        "missing/extra baseline artifact",
    )
    require(
        sha(predecessor) == IDENTITIES["predecessor_descriptor"][1],
        "wrong predecessor descriptor bytes",
    )
    for role, raw in evidence["artifacts"].items():
        require(sha(raw) == IDENTITIES[role][1], "wrong " + role + " bytes")
    closure = evidence["artifacts"]["lifecycle_closure"].decode("utf-8")
    record = loads(re.search(r"```CLOSURE_JSON\n(.*?)\n```", closure, re.S)[1])
    require(
        record["contract_lifecycle"]["V6_SUCCESSOR_CONTRACT"] == ["HUMAN_PI_ACCEPTED", "FROZEN"]
        and record["contract_lifecycle"]["PERSISTED"]
        == record["contract_lifecycle"]["COMMITTED"]
        == "YES",
        "contract closure incomplete",
    )
    descriptor = loads(predecessor)
    schema("V6_CAPACITY_CURRENT_STATE_V1", descriptor)
    require(
        descriptor["event_count"] == 0
        and descriptor["event_chain"] == []
        and descriptor["event_head"] is None
        and descriptor["runtime_authority"] is False,
        "not raw powerless predecessor",
    )
    raw_projection = descriptor["projection"]
    require(digest(raw_projection) == RAW_SHA, "wrong raw projection hash")
    result = copy.deepcopy(raw_projection)
    result["state"] = "CONTRACT_PUBLISHED_WHERE_REQUIRED"
    for flag in FLAGS:
        result["lifecycle"][flag] = "YES"
    validate_qualification_result(raw_projection, result)
    return result


def validate_qualification_result(raw, qualified):
    require(digest(raw) == RAW_SHA, "wrong exact raw projection")
    expected = copy.deepcopy(raw)
    expected["state"] = "CONTRACT_PUBLISHED_WHERE_REQUIRED"
    for flag in FLAGS:
        expected["lifecycle"][flag] = "YES"
    require(canonical(qualified) == canonical(expected), "Q mutated a preserved field or authority")


def refs_valid(refs):
    canonical(refs)
    require(type(refs) is list, "reference list required")
    paths = set()
    for ref in refs:
        require(
            type(ref) is dict
            and set(ref) == {"path", "sha256"}
            and type(ref["path"]) is str
            and ref["path"]
            and type(ref["sha256"]) is str
            and re.fullmatch(r"[0-9a-f]{64}", ref["sha256"]),
            "invalid evidence reference",
        )
        require(ref["path"] not in paths, "duplicate/conflicting evidence reference")
        paths.add(ref["path"])
    require(
        refs == sorted(refs, key=lambda r: (r["path"].encode("utf-8"), r["sha256"])),
        "evidence reference order drift",
    )


def derive_event_id(event_without_event_id):
    core = event_without_event_id
    canonical(core)
    require(
        type(core) is dict and set(core) == set(CORE_FIELDS),
        "invalid event core fields (self identity/hash/timestamp prohibited)",
    )
    schema("V6_CAPACITY_STATE_EVENT_V1", {**core, "event_id": "schema-probe-only"})
    refs_valid(core["evidence_references"])
    return digest(core)


def validate_event_identity(event, stored_bytes):
    schema("V6_CAPACITY_STATE_EVENT_V1", event)
    core = {k: v for k, v in event.items() if k != "event_id"}
    require(event["event_id"] == derive_event_id(core), "arbitrary/noncanonical event_id")
    require(canonical(loads(stored_bytes)) == canonical(event), "stored event payload differs")
    return {
        "event_id": event["event_id"],
        "event_sha256": digest(event),
        "file_sha256": sha(stored_bytes),
    }


def accepted_bridge(bridge, acceptance):
    validate_bridge(bridge)
    require(
        set(acceptance) == {"reference", "bytes", "HUMAN_PI_ACCEPTED", "EFFECTIVE"},
        "invalid bridge acceptance evidence",
    )
    require(
        acceptance["HUMAN_PI_ACCEPTED"] == acceptance["EFFECTIVE"] == "YES",
        "bridge not accepted/effective",
    )
    ref = acceptance["reference"]
    refs_valid([ref])
    require(
        ref["path"] == BRIDGE_PATH
        and sha(acceptance["bytes"]) == ref["sha256"]
        and canonical(loads(acceptance["bytes"])) == canonical(bridge),
        "wrong accepted bridge bytes",
    )
    return ref


def validate_genesis_event(event, predecessor, bridge, baseline, acceptance, authority):
    qualified = qualify_runtime_genesis(predecessor, bridge, baseline)
    bridge_ref = accepted_bridge(bridge, acceptance)
    validate_event_identity(event, canonical(event))
    require(
        event["sequence"] == 1 and event["previous_event_identity"] is None,
        "first-event predecessor/sequence drift",
    )
    require(
        event["kind"] == "STATE_TRANSITION"
        and event["from_state"] == qualified["state"]
        and event["to_state"] == "CENSUS_MEMBERSHIP_ACTIVATED"
        and event["gate"] == "HUMAN_PI_ACTIVATE_V6_CENSUS_MEMBERSHIP",
        "genesis/backfill or wrong activation edge",
    )
    old = loads(predecessor)
    require(
        event["previous_descriptor_sha256"] == sha(predecessor)
        and event["prior_projection_sha256"] == digest(qualified),
        "raw-descriptor/qualified-projection distinction violated",
    )
    require(
        event["contract_sha256"] == IDENTITIES["contract_manifest"][1]
        and event["predecessor"] == old["predecessor"],
        "historical predecessor/contract changed",
    )
    expected = copy.deepcopy(qualified)
    expected["state"] = "CENSUS_MEMBERSHIP_ACTIVATED"
    expected["lifecycle"].update(V6_ACTIVATED="YES", CENSUS_MEMBERSHIP_EFFECTIVE="YES")
    require(
        canonical(event["next_projection"]) == canonical(expected)
        and event["result_projection_sha256"] == digest(expected),
        "activation delta changed downstream work/authority",
    )
    required_refs = [bridge_ref] + [
        bridge["baseline"][k]
        for k in ("lifecycle_closure", "canonical_pool", "predecessor_evidence_bridge")
    ]
    required_refs.sort(key=lambda r: (r["path"].encode("utf-8"), r["sha256"]))
    require(
        event["evidence_references"] == required_refs
        and event["supersession_reference"] == bridge_ref,
        "exact four genesis references/supersession missing",
    )
    require(
        set(authority)
        == {
            "path",
            "namespace",
            "owner",
            "gate",
            "contract_sha256",
            "prior_projection_sha256",
            "previous_descriptor_sha256",
            "scope",
            "HUMAN_PI_ACCEPTED",
        },
        "event authority contains undeclared/future identities",
    )
    require(
        event["authority_reference"] == {"path": authority["path"], "sha256": digest(authority)}
        and authority["owner"] == "HUMAN_PI"
        and authority["HUMAN_PI_ACCEPTED"] == "YES"
        and authority["namespace"] == event["namespace"]
        and authority["scope"] == "MEMBERSHIP_ACTIVATION_ONLY"
        and authority["gate"] == event["gate"]
        and authority["contract_sha256"] == event["contract_sha256"]
        and authority["prior_projection_sha256"] == digest(qualified)
        and authority["previous_descriptor_sha256"] == sha(predecessor),
        "independent activation authority mismatch",
    )
    return expected


def validate_bootstrap_descriptor(
    descriptor, event, event_bytes, event_path, projection, predecessor
):
    schema("V6_CAPACITY_CURRENT_STATE_V1", descriptor)
    identities = validate_event_identity(event, event_bytes)
    head = {
        "event_id": identities["event_id"],
        "sequence": 1,
        "event_sha256": identities["event_sha256"],
    }
    entry = {**head, "path": event_path, "sha256": identities["file_sha256"]}
    old = loads(predecessor)
    require(
        descriptor["event_count"] == 1
        and descriptor["event_head"] == head
        and descriptor["event_chain"] == [entry],
        "single bootstrap chain mismatch",
    )
    require(
        descriptor["predecessor"] == old["predecessor"]
        and descriptor["contract"] == old["contract"]
        and descriptor["intended_effective_descriptor_path"] == CURRENT_PATH
        and descriptor["derived_views_authority"] == "NONE"
        and descriptor["consumer_policy"] == old["consumer_policy"],
        "descriptor canonical policy/historical predecessor drift",
    )
    require(
        descriptor["projection"] == projection
        and descriptor["projection_sha256"] == digest(projection)
        and descriptor["lifecycle_label"] == projection["state"],
        "descriptor replay disagreement",
    )


def validate_candidate_envelope(
    envelope, predecessor, bridge, baseline, acceptance, authority, *, as_current=False
):
    canonical({k: v for k, v in envelope.items() if k != "event_bytes"})
    require(not as_current, "candidate-as-current consumption prohibited")
    require(
        set(envelope)
        == set(ASSERTIONS) | {"post_state_preview", "event_preview", "event_bytes", "event_path"},
        "external candidate fields drift",
    )
    require(
        all(type(envelope[k]) is type(v) and envelope[k] == v for k, v in ASSERTIONS.items()),
        "non-effective assertions drift",
    )
    old = loads(predecessor)
    require(
        old["event_count"] == 0
        and old["projection"]["lifecycle"]["V6_ACTIVATED"]
        == old["projection"]["lifecycle"]["CENSUS_MEMBERSHIP_EFFECTIVE"]
        == "NO",
        "canonical predecessor changed",
    )
    event, preview = envelope["event_preview"], envelope["post_state_preview"]
    projection = validate_genesis_event(event, predecessor, bridge, baseline, acceptance, authority)
    validate_bootstrap_descriptor(
        preview, event, envelope["event_bytes"], envelope["event_path"], projection, predecessor
    )
    require(
        preview["candidate_only"] is False
        and preview["runtime_authority"] is False
        and preview["effective_current_descriptor_identity"] is None
        and preview["authoritative_current_surfaces"] == [],
        "nested preview has runtime authority",
    )
    return True


def validate_installation_semantics(
    proof,
    predecessor,
    successor_bytes,
    bridge,
    baseline,
    acceptance,
    event,
    event_bytes,
    event_path,
    authority,
):
    """Non-mutating proof check only. A successful result installs NOTHING."""
    require(
        set(proof)
        == {
            "operation",
            "path",
            "expected_predecessor_sha256",
            "observed_predecessor_sha256",
            "artifact_lifecycle",
            "publication",
            "automatic",
            "installation_authorized",
            "installed_verified",
            "committed_successor_bytes",
            "observed_installed_bytes",
            "acceptance_pin",
            "installation_authority",
            "competing_current_descriptors",
        },
        "installation proof fields drift",
    )
    require(
        proof["operation"] == OPERATION and proof["path"] == CURRENT_PATH,
        "wrong effectivity operation/path",
    )
    require(
        proof["expected_predecessor_sha256"]
        == proof["observed_predecessor_sha256"]
        == sha(predecessor),
        "compare predecessor mismatch",
    )
    require(
        proof["artifact_lifecycle"] == {k: "YES" for k in FOUR},
        "missing artifact lifecycle prerequisite",
    )
    require(proof["publication"] == PUBLICATION, "publication applicability/execution gates drift")
    require(
        proof["automatic"] is False
        and proof["installation_authorized"] is True
        and proof["installed_verified"] is True
        and proof["competing_current_descriptors"] == [],
        "exact explicit installation incomplete/competing",
    )
    require(
        proof["committed_successor_bytes"] == proof["observed_installed_bytes"] == successor_bytes,
        "committed/installed successor byte mismatch",
    )
    successor = loads(successor_bytes)
    require(
        proof["acceptance_pin"]
        == {"path": CURRENT_PATH, "sha256": sha(successor_bytes), "HUMAN_PI_ACCEPTED": "YES"},
        "missing independent exact successor acceptance pin",
    )
    install_authority = proof["installation_authority"]
    require(
        set(install_authority)
        == {
            "path",
            "owner",
            "operation",
            "canonical_path",
            "expected_predecessor_sha256",
            "scope",
            "HUMAN_PI_ACCEPTED",
        },
        "installation authority contains future/hash-cycle identity",
    )
    require(
        install_authority["owner"] == "HUMAN_PI"
        and install_authority["operation"] == OPERATION
        and install_authority["canonical_path"] == CURRENT_PATH
        and install_authority["expected_predecessor_sha256"] == sha(predecessor)
        and install_authority["scope"] == "EXACT_MEMBERSHIP_INSTALLATION_ONLY"
        and install_authority["HUMAN_PI_ACCEPTED"] == "YES",
        "installation scope authority mismatch",
    )
    projection = validate_genesis_event(event, predecessor, bridge, baseline, acceptance, authority)
    validate_bootstrap_descriptor(
        successor, event, event_bytes, event_path, projection, predecessor
    )
    require(
        event["namespace"] == "EFFECTIVE_V6"
        and successor["candidate_only"] is False
        and successor["runtime_authority"] is True
        and successor["authoritative_current_surfaces"] == [CURRENT_PATH],
        "candidate-only installation forbidden",
    )
    require(
        successor["effective_current_descriptor_identity"]["human_pi_transition"]
        == {"path": install_authority["path"], "sha256": digest(install_authority)},
        "descriptor installation authority mismatch",
    )
    return {
        "semantic_proof_valid": True,
        "installation_performed": False,
        "runtime_authority_granted_by_validator": False,
    }


def main():
    """Read-only audit to stdout; preserves every canonical/historical input."""

    def module_at(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def git(*args):
        return subprocess.check_output(["git", *args], cwd=ROOT).decode().strip()

    entry = loads((E / "entry_verification.json").read_bytes())
    require(
        git("rev-parse", "--show-toplevel") == str(ROOT)
        and git("branch", "--show-current") == "main"
        and git("rev-parse", "HEAD") == BASELINE,
        "repository/HEAD drift",
    )
    require(
        not git("diff", "--name-only", "HEAD") and not git("diff", "--cached", "--name-only"),
        "tracked/index change",
    )
    for path, expected in (entry["baseline_42_sha256"] | entry["blocker_6_sha256"]).items():
        require(sha((ROOT / path).read_bytes()) == expected, "preservation failure: " + path)
        if path in entry["baseline_42_sha256"]:
            require(
                sha(subprocess.check_output(["git", "show", "HEAD:" + path], cwd=ROOT)) == expected,
                "committed baseline drift",
            )
    require(
        sha((ROOT / DECISION_PATH).read_bytes()) == DECISION_SHA, "adopted decision record drift"
    )
    bridge = loads((ROOT / BRIDGE_PATH).read_bytes())
    validate_bridge(bridge)
    baseline = {
        "baseline_commit": entry["local_head"],
        "published_baseline_commit": entry["live_origin_main"],
        "artifacts": {
            k: (B / p).read_bytes()
            for k, (p, _) in IDENTITIES.items()
            if k != "predecessor_descriptor"
        },
        "next_sequence": 1,
        "prior_event_count": 0,
        "prior_event_head": None,
    }
    qualified = qualify_runtime_genesis((ROOT / CURRENT_PATH).read_bytes(), bridge, baseline)
    tests = module_at("genesis_bridge_synthetic_tests", E / "test_bridge.py")
    positive, rejected = tests.positives(), tests.rejection_matrix()
    inherited_dir = B / "evidence/v6_successor_contract_construction_v1"
    inherited = module_at("frozen_contract_audit", inherited_dir / "validate_contract.py")
    inherited_tests = module_at("frozen_contract_tests", inherited_dir / "test_contract.py")
    data = inherited.bundle()
    inherited.validate_bundle(data)
    old_rejections = inherited_tests.rejection_matrix(data)
    require(len(old_rejections) == 141, "inherited rejection inventory drift")
    new_paths = {DECISION_PATH, BRIDGE_PATH} | {
        str((E / n).relative_to(ROOT))
        for n in [
            "validate_bridge.py",
            "test_bridge.py",
            "entry_verification.json",
            "qualification_evidence.json",
            "lineage.json",
            "validation_results.json",
            "RUN_REPORT.md",
            "artifact_sha256.json",
        ]
    }
    untracked = set(git("ls-files", "--others", "--exclude-standard").splitlines())
    require(
        set(entry["blocker_6_sha256"]) <= untracked
        and untracked <= new_paths | set(entry["blocker_6_sha256"]),
        "unrelated/new activation artifact",
    )
    print(
        json.dumps(
            {
                "schema": "V6_GENESIS_BRIDGE_VALIDATION_RESULTS_V1",
                "status": "CANDIDATE_READY_FOR_HUMAN_PI_REVIEW",
                "qualified_projection_sha256": digest(qualified),
                "positive_count": len(positive),
                "positive_checks": positive,
                "rejection_count": len(rejected),
                "rejection_matrix": rejected,
                "failed": 0,
                "inherited_contract_bundle": "PASS",
                "inherited_rejection_count": len(old_rejections),
                "inherited_rejections": old_rejections,
                "preserved_baseline_paths": 42,
                "preserved_blocker_paths": 6,
                "tracked_diff_empty": True,
                "index_empty": True,
                "limits": [
                    "Pure semantic checks; passed external publication/acceptance/commit/install evidence is not independently recovered by these functions.",
                    "Entry LIVE origin/main was independently checked by read-only ls-remote; this local audit does not access the network.",
                    "All activation-shaped events, descriptors, acceptance and installation proofs are synthetic in-memory fixtures only; none is serialized or installed.",
                    "No production runtime consumer/installer, real execution, scientific validation, or Human-PI acceptance is asserted.",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

"""Read-only construction evidence; synthetic installation proofs stay in memory.

This adapter binds the Human PI's exact descriptor identity and three-field delta.
The accepted bridge validator remains unchanged. No installer, runtime consumer,
acceptance-pin writer, subject execution, or scientific validation runs here.
"""

import copy
import hashlib
import importlib.util
import json
import os
import subprocess
from pathlib import Path

E = Path(__file__).resolve().parent
ROOT = E.parents[3]
PREFIX = "evaluation/downstream_benchmark/"
B = ROOT / PREFIX
HEAD = "b83650784bfc6e79ecf11b3a4be2e4e74aac891f"
PARENT = "b1172b090f68e609fe6d523b9c244391a97566a7"
LIVE = "1e5f8a3f4bc2e8555619f727ea317b0bd2fdf801"
SOURCE = (
    PREFIX
    + "evidence/v6_census_membership_activation_v1_after_genesis_bridge/post_state_candidate.json"
)
AUTHORITY = PREFIX + "V6_CENSUS_MEMBERSHIP_INSTALLATION_AUTHORITY_V1.json"
AUTHORITY_SHA = "359be257db9b355222d71d3e72e9234e736331d5e1a6d079f883b572f85a7458"
AUTHORITY_CLOSURE = PREFIX + "V6_CENSUS_MEMBERSHIP_INSTALLATION_AUTHORITY_V1_LIFECYCLE_CLOSURE.md"
TRANSITION_CLOSURE = PREFIX + "V6_CENSUS_MEMBERSHIP_ACTIVATION_V1_LIFECYCLE_CLOSURE.md"
DESCRIPTOR_ID = "V6_EFFECTIVE_CURRENT_DESCRIPTOR_CENSUS_MEMBERSHIP_ACTIVATED_V1"
CANDIDATE = E / "effective_current_descriptor_candidate.json"
DELTA = {
    "runtime_authority",
    "authoritative_current_surfaces",
    "effective_current_descriptor_identity",
}
FILES = {
    "effective_current_descriptor_candidate.json",
    "entry_verification.json",
    "validate_descriptor.py",
    "validation_results.json",
    "RUN_REPORT.md",
    "artifact_sha256.json",
}
EDGES = [
    ["accepted_installation_authority", "effective_descriptor_bytes"],
    ["effective_descriptor_bytes", "exact_descriptor_sha256"],
    ["exact_descriptor_sha256", "future_independent_acceptance_pin"],
]


def module_at(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


a = module_at(
    "accepted_v6_activation",
    B / "evidence/v6_census_membership_activation_v1_after_genesis_bridge/validate_activation.py",
)
v = a.v


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def top_values(raw):
    """Extract exact UTF-8 value spans, retaining nested whitespace and order."""
    text = raw.decode("utf-8")
    decoder = json.JSONDecoder()

    def skip(i):
        while i < len(text) and text[i].isspace():
            i += 1
        return i

    i = skip(0)
    v.require(text[i] == "{", "top-level JSON object required")
    i = skip(i + 1)
    result = {}
    while text[i] != "}":
        key, i = decoder.raw_decode(text, i)
        i = skip(i)
        v.require(text[i] == ":", "JSON field separator required")
        start = skip(i + 1)
        _, end = decoder.raw_decode(text, start)
        result[key] = text[start:end].encode("utf-8")
        i = skip(end)
        if text[i] == ",":
            i = skip(i + 1)
        else:
            v.require(text[i] == "}", "JSON object terminator required")
    return result


def protected_hashes():
    result = {}
    for line in git("ls-files", "--stage", "-z", "--", PREFIX).split(b"\0"):
        if not line:
            continue
        meta, name = line.split(b"\t", 1)
        mode, oid, stage = meta.split()
        v.require(stage == b"0", "unmerged protected path")
        path = ROOT / name.decode()
        raw = (
            os.readlink(path).encode()
            if path.is_symlink()
            else (oid if mode == b"160000" else path.read_bytes())
        )
        result[name.decode()] = hashlib.sha256(raw).hexdigest()
    return result


def preservation():
    entry = v.loads((E / "entry_verification.json").read_bytes())
    v.require(entry["status"] == "ENTRY_GATE_PASS", "entry gate required")
    v.require(git("rev-parse", "HEAD").decode().strip() == HEAD, "HEAD drift")
    v.require(git("rev-parse", "HEAD^").decode().strip() == PARENT, "parent drift")
    v.require(git("branch", "--show-current").decode().strip() == "main", "branch drift")
    v.require(git("diff", "--name-only") == b"", "tracked worktree changed")
    v.require(git("diff", "--cached", "--name-only") == b"", "index changed")
    expected = {str((E / name).relative_to(ROOT)) for name in FILES}
    untracked = {
        p.decode()
        for p in git("ls-files", "--others", "--exclude-standard", "-z").split(b"\0")
        if p
    }
    v.require(untracked <= expected, "unrelated untracked paths")
    hashes = protected_hashes()
    v.require(
        len(hashes) == entry["protected_tracked_benchmark_files"], "protected inventory drift"
    )
    v.require(
        v.digest(hashes) == entry["protected_path_hash_mapping_sha256"], "protected byte drift"
    )
    for path, sha in entry["required_hashes"].items():
        v.require(v.sha((ROOT / path).read_bytes()) == sha, "accepted artifact drift: " + path)
    return {
        "tracked_files_unchanged": len(hashes),
        "protected_path_hash_mapping_sha256": v.digest(hashes),
        "canonical_sha256": entry["required_hashes"][v.CURRENT_PATH],
        "tracked_worktree_diff": "EMPTY",
        "index_diff": "EMPTY",
        "HEAD_unchanged": True,
        "only_authorized_new_paths": True,
    }


def inputs():
    entry = v.loads((E / "entry_verification.json").read_bytes())
    source_raw = (ROOT / SOURCE).read_bytes()
    source = v.loads(source_raw)
    predecessor = (ROOT / v.CURRENT_PATH).read_bytes()
    install_authority = v.loads((ROOT / AUTHORITY).read_bytes())
    v.require(
        install_authority
        == {
            "path": AUTHORITY,
            "owner": "HUMAN_PI",
            "operation": v.OPERATION,
            "canonical_path": v.CURRENT_PATH,
            "expected_predecessor_sha256": v.sha(predecessor),
            "scope": "EXACT_MEMBERSHIP_INSTALLATION_ONLY",
            "HUMAN_PI_ACCEPTED": "YES",
        },
        "exact seven-field installation authority required",
    )
    v.require(v.digest(install_authority) == AUTHORITY_SHA, "authority semantic hash mismatch")
    transition = a.closure((ROOT / TRANSITION_CLOSURE).read_bytes())
    installation = a.closure((ROOT / AUTHORITY_CLOSURE).read_bytes())
    for record, lifecycle_key, identity, commit, scope in [
        (
            transition,
            "transition_lifecycle",
            "V6_CENSUS_MEMBERSHIP_ACTIVATION_V1",
            PARENT,
            transition["accepted_activation_paths_sha256"]
            | {TRANSITION_CLOSURE: entry["required_hashes"][TRANSITION_CLOSURE]},
        ),
        (
            installation,
            "lifecycle",
            "V6_CENSUS_MEMBERSHIP_INSTALLATION_AUTHORITY_V1",
            HEAD,
            {
                AUTHORITY: AUTHORITY_SHA,
                AUTHORITY_CLOSURE: entry["required_hashes"][AUTHORITY_CLOSURE],
            },
        ),
    ]:
        life = record[lifecycle_key]
        v.require(
            life[identity] == ["HUMAN_PI_ACCEPTED", "FROZEN"]
            and life["PERSISTED"] == life["COMMITTED"] == "YES",
            "accepted lifecycle incomplete",
        )
        v.require(
            git("rev-parse", commit + "^").decode().strip()
            == record["commit_envelope"]["required_parent"],
            "closure commit parent drift",
        )
        v.require(
            git("log", "-1", "--format=%s", commit).decode().strip()
            == record["commit_envelope"]["message"],
            "closure commit message drift",
        )
        v.require(
            set(
                git("diff-tree", "--no-commit-id", "--name-only", "-r", commit)
                .decode()
                .splitlines()
            )
            == set(scope),
            "closure commit paths drift",
        )
        for path, sha in scope.items():
            v.require(
                v.sha((ROOT / path).read_bytes()) == v.sha(git("show", commit + ":" + path)) == sha,
                "accepted/committed byte drift: " + path,
            )
    bridge_raw = (ROOT / v.BRIDGE_PATH).read_bytes()
    bridge = v.loads(bridge_raw)
    baseline = a.baseline_evidence()
    acceptance = a.verify_bridge_governance(
        bridge_raw, (ROOT / a.BRIDGE_CLOSURE).read_bytes(), LIVE
    )
    event_raw = (a.E / "activation_event_candidate.json").read_bytes()
    event = v.loads(event_raw)
    activation_authority = v.loads((a.E / "activation_authority.json").read_bytes())
    _, projection, derived_event, derived_raw, derived_source, _ = a.derive(
        predecessor, bridge, baseline, activation_authority
    )
    v.require(
        source == derived_source and source_raw == a.pretty(derived_source),
        "exact source replay drift",
    )
    v.require(event == derived_event and event_raw == derived_raw, "exact event replay drift")
    v.validate_candidate_envelope(
        a.decode_envelope(v.loads((a.E / "candidate_envelope.json").read_bytes())),
        predecessor,
        bridge,
        baseline,
        acceptance,
        activation_authority,
    )
    return {
        "source": source,
        "source_raw": source_raw,
        "predecessor": predecessor,
        "install_authority": install_authority,
        "bridge": bridge,
        "baseline": baseline,
        "acceptance": acceptance,
        "event": event,
        "event_raw": event_raw,
        "event_path": SOURCE.rsplit("/", 1)[0] + "/activation_event_candidate.json",
        "activation_authority": activation_authority,
        "projection": projection,
    }


def synthetic_proof(raw, f):
    """Every future lifecycle/commit/install assertion here is hypothetical."""
    return {
        "operation": v.OPERATION,
        "path": v.CURRENT_PATH,
        "expected_predecessor_sha256": v.sha(f["predecessor"]),
        "observed_predecessor_sha256": v.sha(f["predecessor"]),
        "artifact_lifecycle": {key: "YES" for key in v.FOUR},
        "publication": copy.deepcopy(v.PUBLICATION),
        "automatic": False,
        "installation_authorized": True,
        "installed_verified": True,
        "committed_successor_bytes": raw,
        "observed_installed_bytes": raw,
        "acceptance_pin": {
            "path": v.CURRENT_PATH,
            "sha256": v.sha(raw),
            "HUMAN_PI_ACCEPTED": "YES",
        },
        "installation_authority": copy.deepcopy(f["install_authority"]),
        "competing_current_descriptors": [],
    }


def frozen_proof(raw, f, proof=None):
    return v.validate_installation_semantics(
        synthetic_proof(raw, f) if proof is None else proof,
        f["predecessor"],
        raw,
        f["bridge"],
        f["baseline"],
        f["acceptance"],
        f["event"],
        f["event_raw"],
        f["event_path"],
        f["activation_authority"],
    )


def validate_exact(raw, f):
    descriptor = v.loads(raw)
    v.schema("V6_CAPACITY_CURRENT_STATE_V1", descriptor)
    expected = {
        "runtime_authority": True,
        "authoritative_current_surfaces": [v.CURRENT_PATH],
        "effective_current_descriptor_identity": {
            "descriptor_id": DESCRIPTOR_ID,
            "human_pi_transition": {"path": AUTHORITY, "sha256": AUTHORITY_SHA},
        },
    }
    v.require(set(descriptor) == set(f["source"]), "top-level fields added/removed")
    changed = {
        key for key in descriptor if v.canonical(descriptor[key]) != v.canonical(f["source"][key])
    }
    v.require(changed == DELTA, "exact three-field effectivity delta required")
    v.require(
        all(v.canonical(descriptor[key]) == v.canonical(value) for key, value in expected.items()),
        "Human-PI exact effectivity values/descriptor_id required",
    )
    original_values, new_values = top_values(f["source_raw"]), top_values(raw)
    unchanged = sorted(set(descriptor) - DELTA)
    v.require(
        all(new_values[key] == original_values[key] for key in unchanged),
        "non-effectivity stored UTF-8 value bytes changed",
    )
    v.require(
        descriptor["event_chain"] == f["source"]["event_chain"]
        and descriptor["event_head"] == f["source"]["event_head"],
        "event chain/head drift",
    )
    v.require(
        descriptor["projection"] == f["projection"] == f["source"]["projection"], "projection drift"
    )
    v.require(
        descriptor["projection_sha256"]
        == v.digest(descriptor["projection"])
        == "1bb6f6bda409db2b38ecd078d08c3e60582385db172fcaeacd85b7c28d798d38",
        "projection hash drift",
    )
    phases = descriptor["projection"]["phase_authorizations"]
    v.require(len(phases) == 7 and set(phases.values()) == {"NO"}, "phase authority enabled")
    v.require(
        all(
            descriptor["projection"]["lifecycle"][key] == "NO"
            for key in ["PREPARATION_AUTHORIZED", "ORACLE_AUTHORIZED", "ALLOCATION_AUTHORIZED"]
        ),
        "downstream lifecycle authority enabled",
    )
    cases = descriptor["projection"]["case_states"]
    pool = a.c.csv_rows(B / "v6_reconsideration_pool.csv")
    v.require(
        len(cases) == 433
        and len({c["case_id"] for c in cases}) == 433
        and len({c["source_project"] for c in cases}) == 15,
        "membership cardinality drift",
    )
    v.require(
        [(c["case_id"], c["source_project"], c["frozen_rank"]) for c in cases]
        == [(c["case_id"], c["source_project"], int(c["frozen_rank"])) for c in pool],
        "membership identity/order drift",
    )
    v.require(v.sha(raw).encode() not in v.canonical(descriptor), "descriptor self-hash")
    v.acyclic(EDGES)
    proof_result = frozen_proof(raw, f)
    return {
        "schema": "PASS",
        "exact_effectivity_delta": sorted(changed),
        "unchanged_semantic_and_stored_UTF8_value_fields": unchanged,
        "unchanged_field_count": len(unchanged),
        "projection_stored_value_sha256": v.sha(new_values["projection"]),
        "projection_semantic_sha256": descriptor["projection_sha256"],
        "event_chain_semantic_sha256": v.digest(descriptor["event_chain"]),
        "membership_semantic_sha256": v.digest(cases),
        "members": len(cases),
        "projects": 15,
        "phase_authorizations": phases,
        "frozen_installability_proof": proof_result,
        "NO_HASH_CYCLE": "YES",
    }


def rejected(call):
    try:
        call()
    except ValueError as error:
        return {"result": "PASS_REJECTED", "reason": str(error)}
    return {"result": "ACCEPTED"}


def audit():
    before = preservation()
    f = inputs()
    raw = CANDIDATE.read_bytes()
    descriptor = v.loads(raw)
    positive = validate_exact(raw, f)
    mutations = [
        ("runtime_authority_false", lambda d: d.update(runtime_authority=False)),
        ("empty_current_surfaces", lambda d: d.update(authoritative_current_surfaces=[])),
        (
            "wrong_canonical_surface",
            lambda d: d.update(authoritative_current_surfaces=["wrong/current.json"]),
        ),
        ("null_effective_identity", lambda d: d.update(effective_current_descriptor_identity=None)),
        (
            "wrong_descriptor_id",
            lambda d: d["effective_current_descriptor_identity"].update(
                descriptor_id="wrong-nonempty-id"
            ),
        ),
        (
            "wrong_authority_path",
            lambda d: d["effective_current_descriptor_identity"]["human_pi_transition"].update(
                path="wrong/authority.json"
            ),
        ),
        (
            "wrong_authority_sha",
            lambda d: d["effective_current_descriptor_identity"]["human_pi_transition"].update(
                sha256="0" * 64
            ),
        ),
        ("fourth_semantic_field_delta", lambda d: d["predecessor"].update(seed=20260923)),
        (
            "altered_projection",
            lambda d: d["projection"]["allocation"].update(final_case_ids=["pandas::116"]),
        ),
        ("altered_event_head", lambda d: d["event_head"].update(event_id="0" * 64)),
        (
            "altered_membership",
            lambda d: d["projection"]["case_states"][0].update(case_id="wrong::1"),
        ),
        (
            "preparation_enabled",
            lambda d: d["projection"]["lifecycle"].update(PREPARATION_AUTHORIZED="YES"),
        ),
        ("oracle_enabled", lambda d: d["projection"]["lifecycle"].update(ORACLE_AUTHORIZED="YES")),
        (
            "allocation_enabled",
            lambda d: d["projection"]["lifecycle"].update(ALLOCATION_AUTHORIZED="YES"),
        ),
        ("descriptor_self_hash", lambda d: d.update(descriptor_sha256=v.sha(raw))),
        (
            "future_pin_dependency",
            lambda d: d.update(
                acceptance_pin_reference={"path": "future/pin.json", "sha256": "0" * 64}
            ),
        ),
        (
            "future_installation_record_sha",
            lambda d: d.update(future_installation_record_sha256="0" * 64),
        ),
        ("future_enclosing_commit_sha", lambda d: d.update(future_enclosing_commit_sha="0" * 40)),
        (
            "empty_descriptor_id",
            lambda d: d["effective_current_descriptor_identity"].update(descriptor_id=""),
        ),
        (
            "identity_self_hash_field",
            lambda d: d["effective_current_descriptor_identity"].update(sha256=v.sha(raw)),
        ),
        ("altered_event_chain", lambda d: d["event_chain"][0].update(path="wrong/event.json")),
        ("reordered_membership", lambda d: d["projection"]["case_states"].reverse()),
        ("candidate_only_true", lambda d: d.update(candidate_only=True)),
    ]
    for key in descriptor["projection"]["phase_authorizations"]:
        mutations.append(
            (
                "phase_enabled:" + key,
                lambda d, key=key: d["projection"]["phase_authorizations"].update({key: "YES"}),
            )
        )
    matrix = []
    for name, mutate in mutations:
        changed = copy.deepcopy(descriptor)
        mutate(changed)
        changed_raw = a.pretty(changed)
        exact = rejected(lambda: validate_exact(changed_raw, f))
        frozen = rejected(lambda: frozen_proof(changed_raw, f))
        v.require(exact["result"] == "PASS_REJECTED", "required rejection escaped: " + name)
        matrix.append(
            {
                "check": name,
                "exact_construction_adapter": exact,
                "unchanged_frozen_validator": frozen,
                "acceptance_pin_for_mutated_bytes": "SYNTHETIC_IN_MEMORY_ONLY",
            }
        )
    prerequisite_rejections = []
    for name, mutate in [
        ("missing_real_acceptance_pin", lambda p: p.update(acceptance_pin={})),
        (
            "descriptor_not_accepted_frozen_persisted_committed",
            lambda p: p.update(artifact_lifecycle={k: "NO" for k in v.FOUR}),
        ),
        (
            "installation_not_separately_authorized",
            lambda p: p.update(installation_authorized=False),
        ),
    ]:
        proof = synthetic_proof(raw, f)
        mutate(proof)
        result = rejected(lambda: frozen_proof(raw, f, proof))
        v.require(result["result"] == "PASS_REJECTED", "missing future prerequisite accepted")
        prerequisite_rejections.append({"check": name, **result})
    cycle_rejections = []
    for node in [
        "effective_descriptor_bytes",
        "exact_descriptor_sha256",
        "future_independent_acceptance_pin",
    ]:
        edges = EDGES + [[node, "accepted_installation_authority"]]
        result = rejected(lambda: v.acyclic(edges))
        v.require(result["result"] == "PASS_REJECTED", "hash cycle accepted")
        cycle_rejections.append({"check": "reverse_dependency:" + node, **result})
    after = preservation()
    v.require(before == after, "audit changed protected inputs")
    return {
        "status": "PASS",
        "date": "2026-10-04",
        "timezone": "Europe/Budapest",
        "authority_transaction": "HUMAN_PI_OPEN_V6_EFFECTIVE_CURRENT_DESCRIPTOR_CONSTRUCTION_V1",
        "candidate": {
            "path": str(CANDIDATE.relative_to(ROOT)),
            "sha256": v.sha(raw),
            "byte_count": len(raw),
            "descriptor_id": DESCRIPTOR_ID,
        },
        "source": {"path": SOURCE, "sha256": v.sha(f["source_raw"])},
        "installation_authority": {
            "path": AUTHORITY,
            "sha256": AUTHORITY_SHA,
            "lifecycle": ["HUMAN_PI_ACCEPTED", "FROZEN", "PERSISTED", "COMMITTED"],
        },
        "positive": positive,
        "rejection_matrix": matrix,
        "descriptor_rejection_count": len(matrix),
        "future_prerequisite_rejections": prerequisite_rejections,
        "hash_cycle_rejections": cycle_rejections,
        "total_rejection_count": len(matrix) + len(prerequisite_rejections) + len(cycle_rejections),
        "failures": 0,
        "hash_dependency_edges": EDGES,
        "validators": {
            "construction_adapter": {
                "path": str(Path(__file__).relative_to(ROOT)),
                "sha256": v.sha(Path(__file__).read_bytes()),
            },
            "frozen_bridge": {
                "path": str(Path(v.__file__).relative_to(ROOT)),
                "sha256": v.sha(Path(v.__file__).read_bytes()),
            },
        },
        "preservation": after,
        "synthetic_proof_scope": "Only structural compatibility is tested. The exact candidate and accepted historical inputs are real; the future candidate lifecycle, committed/installed observations, installation authorization, and acceptance pin are hypothetical in-memory fixtures. No proof or pin object is serialized.",
        "frozen_validator_limitation": "The frozen validator accepts any nonempty descriptor_id. wrong_descriptor_id is rejected by the exact Human-PI binding in the construction adapter, not by the frozen validator.",
        "canonical_installation_status": "BLOCKED_PENDING_REAL_HUMAN_PI_ACCEPTANCE_FREEZE_PERSISTENCE_COMMIT_EXTERNAL_EXACT_PIN_AND_SEPARATE_INSTALLATION_AUTHORIZATION",
        "firewall": {
            key: "NO"
            for key in [
                "EFFECTIVE_DESCRIPTOR_ACCEPTED",
                "EFFECTIVE_DESCRIPTOR_FROZEN",
                "EFFECTIVE_DESCRIPTOR_COMMITTED",
                "ACCEPTANCE_PIN_CREATED",
                "CANONICAL_INSTALLATION_EXECUTED",
                "V6_CANONICAL_ACTIVATED",
                "PREPARATION_AUTHORIZED",
                "SOURCE_ACQUISITION_AUTHORIZED",
                "MATERIALIZATION_AUTHORIZED",
                "IMAGE_BUILD_AUTHORIZED",
                "ORACLE_AUTHORIZED",
                "ALLOCATION_AUTHORIZED",
                "SUBJECT_DOCKER_EXECUTION",
                "PILOT_IDS_COMPUTED",
                "FINALS_ALLOCATED",
                "GIT_STAGE",
                "GIT_COMMIT",
                "GIT_PUSH",
            ]
        },
        "next_gate": "HUMAN_PI_REVIEW_OF_V6_EFFECTIVE_CURRENT_DESCRIPTOR_V1",
        "limits": "No production consumer/installer execution, scientific validation, subject feasibility, runtime qualification, or downstream execution was tested.",
    }


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True, ensure_ascii=False, indent=2))

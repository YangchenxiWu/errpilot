"""Transaction-scoped, read-only audit of a non-effective V6 activation candidate.

The accepted bridge performs Q, identity derivation and V1 semantic validation.
This adapter independently verifies its actual governance/publication inputs.
It is neither a runtime consumer nor an installer. All rejection probes are
in memory, and this module never writes a canonical or candidate artifact.
"""

import copy
import csv
import importlib.util
import io
import json
import re
import subprocess
from pathlib import Path

E = Path(__file__).resolve().parent
ROOT = E.parents[3]
PREFIX = "evaluation/downstream_benchmark/"
B = ROOT / PREFIX
NAMESPACE = str(E.relative_to(ROOT)) + "/"
HEAD = "1e5f8a3f4bc2e8555619f727ea317b0bd2fdf801"
BRIDGE_SHA = "1c4b8890d9e6c102b1be1403f69cf50f3554888c0e251397694e66abc2b0ec10"
BRIDGE_CLOSURE = PREFIX + "V6_ACTIVATION_RUNTIME_GENESIS_BRIDGE_LIFECYCLE_CLOSURE_V1.md"
BRIDGE_CLOSURE_SHA = "7e94df7d950dac1465ddf292aa5705a5d6c597915b3310d88642645a948258b5"
QUALIFIED_SHA = "9633d99370f49d63e3b1b24e1b49adfbd4550a6aa12439e4f04276f0327638b5"
REQUEST = Path(
    "/Users/wuyangchenxi/.codex/attachments/391f60cc-0bdb-4ae5-8e80-3c5b84bb49d7/已粘贴的文本.txt"
)
TRANSACTION = "REOPEN_V6_CENSUS_MEMBERSHIP_ACTIVATION_V1_AFTER_GENESIS_BRIDGE"
FILES = {
    "validate_activation.py",
    "test_activation.py",
    "activation_authority.json",
    "activation_event_candidate.json",
    "post_state_candidate.json",
    "candidate_envelope.json",
    "entry_verification.json",
    "validation_results.json",
    "lineage.json",
    "RUN_REPORT.md",
    "artifact_sha256.json",
}


def module_at(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


v = module_at(
    "frozen_v6_genesis_bridge",
    B / "evidence/v6_activation_runtime_genesis_bridge_v1/validate_bridge.py",
)
c = module_at(
    "frozen_v6_contract", B / "evidence/v6_successor_contract_construction_v1/validate_contract.py"
)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def pretty(value):
    v.canonical(value)
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def closure(raw):
    match = re.search(r"```(?:CLOSURE_JSON|json)\n(.*?)\n```", raw.decode("utf-8"), re.S)
    v.require(match is not None, "missing lifecycle closure record")
    return v.loads(match[1])


def baseline_evidence():
    return {
        "baseline_commit": v.BASELINE,
        "published_baseline_commit": v.BASELINE,
        "artifacts": {
            role: (B / path).read_bytes()
            for role, (path, _) in v.IDENTITIES.items()
            if role != "predecessor_descriptor"
        },
        "next_sequence": 1,
        "prior_event_count": 0,
        "prior_event_head": None,
    }


def verify_bridge_governance(bridge_bytes, closure_bytes, published_head):
    v.require(v.sha(bridge_bytes) == BRIDGE_SHA, "wrong exact published bridge hash")
    v.require(v.sha(closure_bytes) == BRIDGE_CLOSURE_SHA, "wrong exact bridge closure")
    v.require(published_head == HEAD, "bridge publication not evidenced")
    record = closure(closure_bytes)
    life = record["bridge_lifecycle"]
    v.require(
        record["authority"]["acceptance"] == "ACCEPTED"
        and life["V6_ACTIVATION_RUNTIME_GENESIS_BRIDGE_V1"] == ["HUMAN_PI_ACCEPTED", "FROZEN"]
        and life["PERSISTED"] == life["COMMITTED"] == "YES",
        "bridge governance lifecycle incomplete",
    )
    scope = record["historical_blocker_paths_sha256"] | record["accepted_bridge_paths_sha256"]
    scope = {**scope, BRIDGE_CLOSURE: BRIDGE_CLOSURE_SHA}
    v.require(
        git("rev-parse", HEAD + "^") == record["commit_envelope"]["required_parent"]
        and git("log", "-1", "--format=%s", HEAD) == record["commit_envelope"]["message"]
        and set(git("diff-tree", "--no-commit-id", "--name-only", "-r", HEAD).splitlines())
        == set(scope),
        "bridge enclosing commit parent/message/scope drift",
    )
    for path, digest in scope.items():
        v.require(v.sha((ROOT / path).read_bytes()) == digest, "bridge input drift: " + path)
        committed = subprocess.check_output(["git", "show", HEAD + ":" + path], cwd=ROOT)
        v.require(v.sha(committed) == digest, "bridge committed identity drift: " + path)
    return {
        "reference": {"path": v.BRIDGE_PATH, "sha256": BRIDGE_SHA},
        "bytes": bridge_bytes,
        "HUMAN_PI_ACCEPTED": "YES",
        # Effective accepted *bridge semantics*, not membership/runtime effectivity.
        "EFFECTIVE": "YES",
    }


def validate_authority_source(authority, entry, request_bytes):
    v.require(v.sha(request_bytes) == entry["human_pi_request"]["sha256"], "request identity drift")
    v.require(
        entry["human_pi_request"]["path"] == str(REQUEST)
        and entry["transaction"] == TRANSACTION
        and TRANSACTION in request_bytes.decode("utf-8"),
        "direct Human-PI construction authority missing",
    )
    v.require(
        authority["path"] == NAMESPACE + "activation_authority.json"
        and authority["namespace"] == "EFFECTIVE_V6",
        "transaction authority path/namespace drift",
    )
    v.require(
        entry["authorization"]
        == {
            "activation_event_candidate_construction": True,
            "successor_descriptor_candidate_construction": True,
            "canonical_installation": False,
            "runtime_effectivity": False,
            "preparation": False,
        },
        "construction-only authorization boundary drift",
    )


def derive(predecessor, bridge, baseline, authority):
    """One Q application at bootstrap, then the exact membership-only delta."""
    old = v.loads(predecessor)
    qualified = v.qualify_runtime_genesis(predecessor, bridge, baseline)
    v.require(v.digest(qualified) == QUALIFIED_SHA, "qualified seed identity drift")
    result = c.phase_flags_for_edge(qualified, "CENSUS_MEMBERSHIP_ACTIVATED")
    refs = [{"path": v.BRIDGE_PATH, "sha256": BRIDGE_SHA}] + [
        bridge["baseline"][role]
        for role in ("lifecycle_closure", "canonical_pool", "predecessor_evidence_bridge")
    ]
    refs.sort(key=lambda ref: (ref["path"].encode("utf-8"), ref["sha256"]))
    core = {
        "schema": "V6_CAPACITY_STATE_EVENT_V1",
        "namespace": "EFFECTIVE_V6",
        "sequence": 1,
        "kind": "STATE_TRANSITION",
        "previous_event_identity": None,
        "previous_descriptor_sha256": v.sha(predecessor),
        "contract_sha256": v.IDENTITIES["contract_manifest"][1],
        "authority_reference": {"path": authority["path"], "sha256": v.digest(authority)},
        "gate": "HUMAN_PI_ACTIVATE_V6_CENSUS_MEMBERSHIP",
        "from_state": qualified["state"],
        "to_state": result["state"],
        "prior_projection_sha256": v.digest(qualified),
        "result_projection_sha256": v.digest(result),
        "next_projection": result,
        "evidence_references": refs,
        "supersession_reference": {"path": v.BRIDGE_PATH, "sha256": BRIDGE_SHA},
        "predecessor": old["predecessor"],
    }
    event = {**core, "event_id": v.derive_event_id(core)}
    event_bytes = pretty(event)
    identities = v.validate_event_identity(event, event_bytes)
    head = {
        "event_id": identities["event_id"],
        "sequence": 1,
        "event_sha256": identities["event_sha256"],
    }
    event_path = NAMESPACE + "activation_event_candidate.json"
    successor = copy.deepcopy(old)
    successor.update(
        candidate_only=False,
        runtime_authority=False,
        lifecycle_label=result["state"],
        effective_current_descriptor_identity=None,
        authoritative_current_surfaces=[],
        event_count=1,
        event_head=head,
        event_chain=[{**head, "path": event_path, "sha256": identities["file_sha256"]}],
        projection=result,
        projection_sha256=v.digest(result),
    )
    envelope = {
        **v.ASSERTIONS,
        "event_preview": event,
        "post_state_preview": successor,
        # Lossless JSON transport for the API's exact bytes input; no V1 change.
        "event_bytes": event_bytes.decode("utf-8"),
        "event_path": event_path,
    }
    return qualified, result, event, event_bytes, successor, envelope


def decode_envelope(envelope):
    decoded = copy.deepcopy(envelope)
    v.require(type(decoded["event_bytes"]) is str, "event byte transport must be UTF-8 text")
    decoded["event_bytes"] = decoded["event_bytes"].encode("utf-8")
    return decoded


def validate_transition(fixture, *, as_current=False):
    """Pinned real-input adapter around the unchanged bridge-aware validator."""
    f = fixture
    expected_acceptance = verify_bridge_governance(
        f["bridge_bytes"], f["bridge_closure_bytes"], f["published_head"]
    )
    v.require(f["acceptance"] == expected_acceptance, "accepted bridge proof drift")
    validate_authority_source(f["authority"], f["entry"], f["request_bytes"])
    v.require(f["pool_bytes"] == f["baseline"]["artifacts"]["canonical_pool"], "pool byte drift")
    v.require(
        v.canonical(f["qualified"])
        == v.canonical(v.qualify_runtime_genesis(f["predecessor"], f["bridge"], f["baseline"])),
        "qualified projection mismatch",
    )
    v.require(v.digest(f["qualified"]) == QUALIFIED_SHA, "qualified projection identity mismatch")
    edge = c.load(B / "v6_census_lifecycle.json")["transitions"][5]
    v.require(
        (f["event"]["from_state"], f["event"]["to_state"], f["event"]["gate"])
        == (edge["from"], edge["to"], edge["gate"]),
        "nonadjacent lifecycle edge",
    )
    envelope = decode_envelope(f["envelope"])
    v.require(
        envelope["event_preview"] == f["event"]
        and envelope["post_state_preview"] == f["successor"]
        and envelope["event_bytes"] == f["event_bytes"]
        and envelope["event_path"] == NAMESPACE + "activation_event_candidate.json",
        "standalone/enclosed candidate or event path disagreement",
    )
    v.validate_candidate_envelope(
        envelope,
        f["predecessor"],
        f["bridge"],
        f["baseline"],
        f["acceptance"],
        f["authority"],
        as_current=as_current,
    )
    identities = v.validate_event_identity(f["event"], f["event_bytes"])
    v.require(
        identities["event_id"] != identities["event_sha256"], "event identity/payload conflation"
    )
    v.require(
        identities["event_sha256"] != identities["file_sha256"], "event payload/file conflation"
    )
    replay = derive(f["predecessor"], f["bridge"], f["baseline"], f["authority"])
    v.require(
        f["event"] == replay[2]
        and f["event_bytes"] == replay[3]
        and f["successor"] == replay[4]
        and f["envelope"] == replay[5],
        "exact deterministic replay mismatch",
    )
    return identities


def inputs():
    entry = v.loads((E / "entry_verification.json").read_bytes())
    bridge_bytes = (ROOT / v.BRIDGE_PATH).read_bytes()
    bridge_closure_bytes = (ROOT / BRIDGE_CLOSURE).read_bytes()
    predecessor = (ROOT / v.CURRENT_PATH).read_bytes()
    baseline = baseline_evidence()
    bridge = v.loads(bridge_bytes)
    acceptance = verify_bridge_governance(
        bridge_bytes, bridge_closure_bytes, entry["live_origin_main"]
    )
    return {
        "entry": entry,
        "request_bytes": REQUEST.read_bytes(),
        "predecessor": predecessor,
        "bridge": bridge,
        "bridge_bytes": bridge_bytes,
        "bridge_closure_bytes": bridge_closure_bytes,
        "published_head": entry["live_origin_main"],
        "baseline": baseline,
        "pool_bytes": baseline["artifacts"]["canonical_pool"],
        "acceptance": acceptance,
        "authority": v.loads((E / "activation_authority.json").read_bytes()),
        "qualified": v.qualify_runtime_genesis(predecessor, bridge, baseline),
        "event": v.loads((E / "activation_event_candidate.json").read_bytes()),
        "event_bytes": (E / "activation_event_candidate.json").read_bytes(),
        "successor": v.loads((E / "post_state_candidate.json").read_bytes()),
        "envelope": v.loads((E / "candidate_envelope.json").read_bytes()),
    }


def preservation(entry):
    v.require(
        git("rev-parse", "--show-toplevel") == str(ROOT)
        and git("branch", "--show-current") == "main"
        and git("rev-parse", "HEAD") == HEAD
        and git("rev-parse", "refs/remotes/origin/main") == HEAD,
        "repository baseline drift",
    )
    v.require(
        not git("diff", "--name-only", "HEAD") and not git("diff", "--cached", "--name-only"),
        "tracked canonical diff or index mutation",
    )
    for path, digest in entry["preserved_inputs_sha256"].items():
        v.require(v.sha(Path(path).read_bytes()) == digest, "preservation failure: " + path)
    untracked = set(git("ls-files", "--others", "--exclude-standard").splitlines())
    v.require(untracked <= {NAMESPACE + name for name in FILES}, "unexpected untracked path")
    v.require({p.name for p in E.iterdir() if p.is_file()} <= FILES, "unexpected candidate file")


def rejection_matrix(fixture):
    probes = []

    def reject(name, mutate=None, action=None):
        f = copy.deepcopy(fixture)
        try:
            if mutate:
                mutate(f)
            if action:
                action(f)
            else:
                validate_transition(f)
        except ValueError as error:
            probes.append({"probe": name, "status": "PASS_REJECTED", "reason": str(error)})
        else:
            raise ValueError("unexpected acceptance: " + name)

    def set_event(f, key, value):
        f["event"][key] = value
        f["event_bytes"] = pretty(f["event"])
        f["envelope"]["event_preview"] = copy.deepcopy(f["event"])
        f["envelope"]["event_bytes"] = f["event_bytes"].decode("utf-8")

    def resign(f):
        core = {k: value for k, value in f["event"].items() if k != "event_id"}
        f["event"]["event_id"] = v.derive_event_id(core)
        set_event(f, "event_id", f["event"]["event_id"])
        ids = v.validate_event_identity(f["event"], f["event_bytes"])
        head = {"event_id": ids["event_id"], "sequence": 1, "event_sha256": ids["event_sha256"]}
        f["successor"].update(
            event_head=head,
            event_chain=[
                {
                    **head,
                    "path": NAMESPACE + "activation_event_candidate.json",
                    "sha256": ids["file_sha256"],
                }
            ],
            projection=copy.deepcopy(f["event"]["next_projection"]),
            projection_sha256=f["event"]["result_projection_sha256"],
        )
        f["envelope"]["post_state_preview"] = copy.deepcopy(f["successor"])

    def edit_event(f, key, value):
        set_event(f, key, value)
        resign(f)

    def edit_result(f, change):
        change(f["event"]["next_projection"])
        set_event(f, "result_projection_sha256", v.digest(f["event"]["next_projection"]))
        resign(f)

    def edit_successor(f, key, value):
        f["successor"][key] = value
        f["envelope"]["post_state_preview"] = copy.deepcopy(f["successor"])

    reject("wrong_bridge_hash", lambda f: f["acceptance"]["reference"].update(sha256="0" * 64))
    reject("wrong_bridge_bytes", lambda f: f.update(bridge_bytes=f["bridge_bytes"] + b"\n"))
    reject("unaccepted_bridge", lambda f: f["acceptance"].update(HUMAN_PI_ACCEPTED="NO"))
    reject("ineffective_bridge", lambda f: f["acceptance"].update(EFFECTIVE="NO"))
    reject("unpublished_bridge", lambda f: f.update(published_head=v.BASELINE))
    reject(
        "wrong_bridge_closure",
        lambda f: f.update(bridge_closure_bytes=f["bridge_closure_bytes"] + b"\n"),
    )
    reject("wrong_predecessor_descriptor", lambda f: f.update(predecessor=f["predecessor"] + b"\n"))
    reject(
        "wrong_raw_projection", action=lambda f: v.validate_qualification_result({}, f["qualified"])
    )
    reject(
        "wrong_qualified_projection", lambda f: f["qualified"].update(state="CONTRACT_CANDIDATE")
    )
    reject(
        "Q_reapplied_twice",
        action=lambda f: v.validate_qualification_result(f["qualified"], f["qualified"]),
    )
    reject(
        "Q_after_bootstrap", lambda f: f["baseline"].update(next_sequence=2, prior_event_count=1)
    )
    for name, key, value in [
        ("first_sequence_not_1", "sequence", 2),
        (
            "first_previous_event_non_null",
            "previous_event_identity",
            {"event_id": "prior", "sequence": 1, "event_sha256": "0" * 64},
        ),
        ("wrong_lifecycle_from", "from_state", "CONTRACT_COMMITTED"),
        ("wrong_lifecycle_to", "to_state", "PREPARATION_PLANNING_AUTHORIZED"),
        ("synthetic_backfill", "to_state", "CONTRACT_PUBLISHED_WHERE_REQUIRED"),
        ("wrong_previous_descriptor_binding", "previous_descriptor_sha256", "0" * 64),
        ("wrong_prior_projection_binding", "prior_projection_sha256", v.RAW_SHA),
        ("wrong_contract_binding", "contract_sha256", "0" * 64),
        (
            "wrong_supersession_reference",
            "supersession_reference",
            {"path": BRIDGE_CLOSURE, "sha256": BRIDGE_CLOSURE_SHA},
        ),
        ("wrong_gate", "gate", "HUMAN_PI_PREPARATION_EXECUTION"),
    ]:
        reject(name, lambda f, key=key, value=value: edit_event(f, key, value))
    reject("arbitrary_event_id", lambda f: set_event(f, "event_id", "arbitrary"))
    reject("event_id_mismatch", lambda f: set_event(f, "event_id", "0" * 64))
    reject("event_id_self_reference", action=lambda f: v.derive_event_id(f["event"]))
    for field in [
        "event_sha256",
        "file_sha256",
        "successor_sha256",
        "timestamp",
        "previous_event_id",
        "previous_event_hash",
    ]:
        reject(
            "undeclared_event_field:" + field,
            action=lambda f, field=field: v.derive_event_id(
                {
                    **{k: value for k, value in f["event"].items() if k != "event_id"},
                    field: "0" * 64,
                }
            ),
        )
    reject(
        "evidence_reference_drift",
        lambda f: edit_event(f, "evidence_references", f["event"]["evidence_references"][:-1]),
    )
    reject(
        "evidence_reference_order",
        action=lambda f: v.refs_valid(list(reversed(f["event"]["evidence_references"]))),
    )
    reject(
        "evidence_reference_duplicate",
        action=lambda f: v.refs_valid(
            f["event"]["evidence_references"] + [f["event"]["evidence_references"][0]]
        ),
    )
    reject(
        "incidental_evidence_reference",
        lambda f: edit_event(
            f,
            "evidence_references",
            sorted(
                f["event"]["evidence_references"]
                + [{"path": NAMESPACE + "RUN_REPORT.md", "sha256": "0" * 64}],
                key=lambda r: (r["path"].encode(), r["sha256"]),
            ),
        ),
    )
    reject(
        "pool_hash_drift",
        lambda f: f["baseline"]["artifacts"].update(canonical_pool=f["pool_bytes"] + b"\n"),
    )
    reject("pool_byte_disagreement", lambda f: f.update(pool_bytes=f["pool_bytes"] + b"\n"))
    for name, change in [
        ("member_addition", lambda p: p["case_states"].append(copy.deepcopy(p["case_states"][0]))),
        ("member_omission", lambda p: p["case_states"].pop()),
        ("member_reorder", lambda p: p["case_states"].reverse()),
        ("preparation_enabled", lambda p: p["lifecycle"].update(PREPARATION_AUTHORIZED="YES")),
        ("oracle_enabled", lambda p: p["lifecycle"].update(ORACLE_AUTHORIZED="YES")),
        ("allocation_enabled", lambda p: p["lifecycle"].update(ALLOCATION_AUTHORIZED="YES")),
        (
            "source_acquisition_enabled",
            lambda p: p["phase_authorizations"].update(SOURCE_ACQUISITION="YES"),
        ),
        ("image_build_enabled", lambda p: p["phase_authorizations"].update(IMAGE_BUILD="YES")),
        (
            "scientific_outcome_changed",
            lambda p: p["case_states"][0].update(scientific_failure=True),
        ),
        ("attempt_consumed", lambda p: p["case_states"][0].update(attempt_consumed=True)),
        ("actual_pilot_selected", lambda p: p["allocation"].update(pilot_case_ids=["pandas::116"])),
    ]:
        reject(name, lambda f, change=change: edit_result(f, change))
    for name, key, value in [
        ("event_count_not_1", "event_count", 2),
        ("wrong_event_head", "event_head", None),
        ("wrong_event_file_binding", "event_chain", []),
        ("runtime_authority_enabled", "runtime_authority", True),
        ("candidate_only_preview_drift", "candidate_only", True),
    ]:
        reject(name, lambda f, key=key, value=value: edit_successor(f, key, value))
    reject(
        "candidate_treated_as_canonical", action=lambda f: validate_transition(f, as_current=True)
    )
    reject("auto_promotion_enabled", lambda f: f["envelope"].update(AUTO_PROMOTION="YES"))
    reject(
        "canonical_registration_enabled",
        lambda f: f["envelope"].update(CURRENT_REGISTRATION="ALLOWED"),
    )
    reject(
        "canonical_activation_asserted",
        lambda f: f["envelope"].update(CANONICAL_V6_ACTIVATED="YES"),
    )
    reject(
        "canonical_v6_current_state_mutation",
        action=lambda f: v.qualify_runtime_genesis(
            pretty(f["successor"]), f["bridge"], f["baseline"]
        ),
    )
    reject(
        "changed_activation_authority",
        lambda f: f["authority"].update(scope="PREPARATION_EXECUTION"),
    )
    reject(
        "future_authority_identity",
        lambda f: f["authority"].update(event_id=f["event"]["event_id"]),
    )
    reject(
        "request_authority_hash_drift", lambda f: f.update(request_bytes=f["request_bytes"] + b"\n")
    )
    reject(
        "canonical_installation_authorized",
        lambda f: f["entry"]["authorization"].update(canonical_installation=True),
    )
    return probes


def audit():
    f = inputs()
    preservation(f["entry"])
    identities = validate_transition(f)
    positive = []

    def check(name, ok):
        v.require(ok, name)
        positive.append({"check": name, "status": "PASS"})

    old = v.loads(f["predecessor"])
    result = f["successor"]["projection"]
    check("exact_qualified_genesis_seed", v.digest(f["qualified"]) == QUALIFIED_SHA)
    check(
        "exact_legal_lifecycle_adjacency",
        f["event"]["from_state"] == "CONTRACT_PUBLISHED_WHERE_REQUIRED"
        and f["event"]["to_state"] == "CENSUS_MEMBERSHIP_ACTIVATED",
    )
    check("first_sequence_1", f["event"]["sequence"] == 1)
    check("null_previous_event", f["event"]["previous_event_identity"] is None)
    check(
        "deterministic_event_id",
        identities["event_id"]
        == v.derive_event_id({k: value for k, value in f["event"].items() if k != "event_id"}),
    )
    v.schema("V6_CAPACITY_STATE_EVENT_V1", f["event"])
    check("V1_event_schema", True)
    projection_schema = v.SCHEMAS["V6_CAPACITY_CURRENT_STATE_V1"].schema["properties"]["projection"]
    v.Draft202012Validator(projection_schema).validate(result)
    check("result_projection_schema", True)
    v.schema("V6_CAPACITY_CURRENT_STATE_V1", f["successor"])
    check("post_state_V1_schema", True)
    check("event_count_1", f["successor"]["event_count"] == 1)
    check(
        "exact_event_head",
        f["successor"]["event_head"]
        == {
            "event_id": identities["event_id"],
            "sequence": 1,
            "event_sha256": identities["event_sha256"],
        },
    )
    check("canonical_pool_identity", v.sha(f["pool_bytes"]) == v.IDENTITIES["canonical_pool"][1])
    pool = list(csv.DictReader(io.StringIO(f["pool_bytes"].decode("utf-8"))))
    c.validate_pool(pool)
    check(
        "unchanged_433_members_15_projects_exact_order",
        len(pool) == 433
        and len({r["source_project"] for r in pool}) == 15
        and [s["case_id"] for s in result["case_states"]] == [r["case_id"] for r in pool],
    )
    check("preparation_unauthorized", result["lifecycle"]["PREPARATION_AUTHORIZED"] == "NO")
    check("oracle_unauthorized", result["lifecycle"]["ORACLE_AUTHORIZED"] == "NO")
    check("allocation_unauthorized", result["lifecycle"]["ALLOCATION_AUTHORIZED"] == "NO")
    check(
        "candidate_non_effective",
        not f["successor"]["runtime_authority"] and f["envelope"]["RUNTIME_EFFECTIVE"] == "NO",
    )
    check(
        "canonical_descriptor_unchanged",
        v.sha((ROOT / v.CURRENT_PATH).read_bytes()) == v.IDENTITIES["predecessor_descriptor"][1],
    )
    v.acyclic(f["bridge"]["hash_model"]["edges"])
    check(
        "no_hash_cycle",
        set(f["event"]) == set(v.CORE_FIELDS) | {"event_id"} and "sha256" not in f["successor"],
    )
    check(
        "exact_replay_agreement",
        f["successor"] == derive(f["predecessor"], f["bridge"], f["baseline"], f["authority"])[4],
    )
    check(
        "bridge_once_in_bootstrap_no_backfill",
        f["baseline"]["next_sequence"] == 1
        and f["baseline"]["prior_event_count"] == 0
        and len(f["successor"]["event_chain"]) == 1,
    )
    check(
        "scientific_and_work_state_unchanged",
        result["case_states"] == old["projection"]["case_states"],
    )
    check(
        "all_phase_subauthorities_NO",
        all(value == "NO" for value in result["phase_authorizations"].values()),
    )
    check(
        "allocation_and_input_freeze_unchanged",
        result["allocation"] == old["projection"]["allocation"]
        and result["combined_pool_input_freeze"] is None
        and result["terminal_assessment"] is None,
    )
    check("historical_predecessor_retained", f["successor"]["predecessor"] == old["predecessor"])
    check(
        "exact_stored_authority_identity",
        (E / "activation_authority.json").read_bytes() == v.canonical(f["authority"]),
    )
    check("three_hash_identities_distinct", len(set(identities.values())) == 3)
    inherited = c.bundle()
    c.validate_bundle(inherited)
    check("frozen_contract_bundle_valid", True)
    inherited_tests = module_at(
        "inherited_contract_tests",
        B / "evidence/v6_successor_contract_construction_v1/test_contract.py",
    )
    bridge_tests = module_at(
        "inherited_bridge_tests",
        B / "evidence/v6_activation_runtime_genesis_bridge_v1/test_bridge.py",
    )
    rejected = rejection_matrix(f)
    inherited_rejections = inherited_tests.rejection_matrix(inherited)
    bridge_positive = bridge_tests.positives()
    bridge_rejections = bridge_tests.rejection_matrix()
    preservation(f["entry"])
    return {
        "schema": "V6_ACTIVATION_CANDIDATE_VALIDATION_RESULTS_V1",
        "status": "REAL_TRANSITION_CANDIDATE_READY_FOR_HUMAN_PI_REVIEW",
        "positive_count": len(positive),
        "positive_checks": positive,
        "rejection_count": len(rejected),
        "rejection_matrix": rejected,
        "failed": 0,
        "identities": identities,
        "qualified_projection_sha256": v.digest(f["qualified"]),
        "result_projection_sha256": v.digest(result),
        "successor_file_sha256": v.sha((E / "post_state_candidate.json").read_bytes()),
        "bridge_inherited_positive_count": len(bridge_positive),
        "bridge_inherited_rejection_count": len(bridge_rejections),
        "contract_inherited_rejection_count": len(inherited_rejections),
        "preserved_input_count": len(f["entry"]["preserved_inputs_sha256"]),
        "tracked_diff_empty": True,
        "index_empty": True,
        "limits": [
            "Candidate construction and deterministic semantic checks only; no runtime consumer or installer is implemented or invoked.",
            "Publication is independently observed with read-only live ls-remote; pure bridge functions alone do not recover external governance proof.",
            "Negative probes mutate copies in memory, never the canonical file.",
            "Q is used once per independent bootstrap derivation from raw predecessor bytes; repeated verification is not Q composition or a second chain event.",
            "No subject feasibility, scientific validation, preparation, oracle execution or allocation is established.",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, ensure_ascii=False))

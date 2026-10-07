"""Read-only effectivity-binding package audit; no construction or installer.

Reuse frozen schemas and accepted event replay without changing historical
entry assumptions. Rejection probes mutate only in-memory fixture copies.
"""

import copy
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True
E = Path(__file__).resolve().parent
ROOT = E.parents[3]
B = "evaluation/downstream_benchmark/"
PREFIX = str(E.relative_to(ROOT)) + "/"
HEAD = "914a25283c3ec12079a80fa722e3adb2b9c4c188"
PARENT = "dded507b6049ad24cdf813590e2d8e8af7e9e241"
CURRENT = B + "v6_current_state.json"
CURRENT_SHA = "6a9028c79aa62f90db2b2d53def32ab23bffcfa3c71d2ec30d7fa64e741e3aae"
TRANSITION = B + "evidence/v6_preparation_execution_transition_v1/"
SOURCE = TRANSITION + "successor_descriptor_candidate.json"
SOURCE_SHA = "6e29d1825bbf3220f58660103761837004fb1265464501638732b9d01e1ce505"
CLOSURE = B + "V6_PREPARATION_EXECUTION_TRANSITION_LIFECYCLE_CLOSURE_V1.md"
CLOSURE_SHA = "6342142a1115e01f96ad8ce24e53ab1bcc93f88c8500caee305067a68e4e465d"
AUTHORITY = B + "V6_PREPARATION_EXECUTION_INSTALLATION_AUTHORITY_V1.json"
DESCRIPTOR = PREFIX + "effective_descriptor_candidate.json"
PIN = B + "V6_PREPARATION_EXECUTION_EFFECTIVE_DESCRIPTOR_ACCEPTANCE_PIN_V1.json"
DESCRIPTOR_ID = "V6_EFFECTIVE_CURRENT_DESCRIPTOR_PREPARATION_EXECUTION_AUTHORIZED_V1"
EVENT_SHA = "5460983338c0835c4c2ec030d2f58e1314874db50591ae5d0c72780288d81ecb"
EVENT_ID = "237d8020668f338c04065beb8557d8f25263fbfc0282003dcc5b2af67a20a50d"
PAYLOAD_SHA = "368aa2581dd7a27dcea6b62a19aad7eb78d5d3ef96866ddfe322ca2dd91a840c"
WORK = B + "evidence/v6_preparation_execution_activation_v1/work_items_candidate.json"
LEDGER = B + "evidence/v6_preparation_execution_activation_v1/ledger_candidate.json"
PLAN = B + "v6_preparation_plan_manifest_candidate.json"
FILES = {
    AUTHORITY, DESCRIPTOR, PIN, PREFIX + "entry_verification.json",
    PREFIX + "validation_results.json", PREFIX + "artifact_sha256.json",
    PREFIX + "RUN_REPORT.md", PREFIX + "validate_binding.py",
}
FIREWALL = {
    "CANONICAL_CURRENT_STATE_MODIFIED": "NO", "INSTALLATION_EXECUTED": "NO",
    "EVENT_3_MODIFIED": "NO", "NEW_EVENT_CREATED": "NO",
    "PREPARATION_EXECUTION_CANONICAL_EFFECTIVE": "NO", "PREPARATION_EXECUTED": "NO",
    "REAL_ATTEMPTS_CONSUMED": 0, "REAL_CLAIMS_CREATED": 0, "REAL_BUILDS_EXECUTED": 0,
    "ENVIRONMENT_READY_CASES_ESTABLISHED": 0, "SOURCE_ACQUISITION_EXECUTED": "NO",
    "ORACLE_EXECUTED": "NO", "ALLOCATION_EXECUTED": "NO",
    "GIT_STAGE": "NO", "GIT_COMMIT": "NO", "GIT_PUSH": "NO",
}

spec = importlib.util.spec_from_file_location("accepted_execution_transition", ROOT / (TRANSITION + "validate_transition.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
v = m.v
pretty = m.pretty


def expected_authority():
    return {
        "path": AUTHORITY, "owner": "HUMAN_PI",
        "operation": "COMPARE_AND_INSTALL_EXACT_ACCEPTED_SUCCESSOR_AT_CANONICAL_PATH",
        "canonical_path": CURRENT, "expected_predecessor_sha256": CURRENT_SHA,
        "scope": "EXACT_PREPARATION_EXECUTION_TRANSITION_INSTALLATION_ONLY",
        "HUMAN_PI_ACCEPTED": "YES",
    }


def rebind(source, authority_sha):
    result = copy.deepcopy(source)
    identity = result["effective_current_descriptor_identity"]
    identity["descriptor_id"] = DESCRIPTOR_ID
    identity["human_pi_transition"] = {"path": AUTHORITY, "sha256": authority_sha}
    return result


def leaves(before, after, prefix=""):
    v.require(type(before) is type(after), "leaf type changed: " + prefix)
    if isinstance(before, dict):
        v.require(before.keys() == after.keys(), "object topology changed: " + prefix)
        return [row for key in sorted(before) for row in leaves(before[key], after[key], prefix + ("." if prefix else "") + key)]
    if isinstance(before, list):
        v.require(len(before) == len(after), "array topology changed: " + prefix)
        return [row for i, (left, right) in enumerate(zip(before, after)) for row in leaves(left, right, prefix + "[" + str(i) + "]")]
    return [] if before == after else [{"path": prefix, "before": before, "after": after}]


def hash_graph(f):
    authority, descriptor, pin = f["authority"], f["descriptor"], f["pin"]
    hashes = {"authority": v.sha(f["authority_raw"]), "descriptor": v.sha(f["descriptor_raw"]), "pin": v.sha(f["pin_raw"])}
    # Edges run from hashed artifact to the artifact that consumes its hash.
    edges = [("authority", "descriptor"), ("descriptor", "pin")]
    for consumer, obj in (("authority", authority), ("descriptor", descriptor), ("pin", pin)):
        for producer in hashes:
            if producer + "_sha256" in obj or (producer == consumer and "self_hash" in obj):
                edges.append((producer, consumer))
    visiting, visited = set(), set()

    def visit(node):
        v.require(node not in visiting, "hash cycle or self dependency")
        if node in visited:
            return
        visiting.add(node)
        for producer, consumer in edges:
            if producer == node:
                visit(consumer)
        visiting.remove(node)
        visited.add(node)

    for node in hashes:
        visit(node)
    v.require(edges == [("authority", "descriptor"), ("descriptor", "pin")], "backward or extra hash dependency")
    identity = descriptor["effective_current_descriptor_identity"]["human_pi_transition"]
    v.require(identity == {"path": AUTHORITY, "sha256": hashes["authority"]}, "wrong authority path or SHA")
    v.require(pin["sha256"] == hashes["descriptor"], "pin does not consume final descriptor SHA")
    for consumer, obj in (("authority", authority), ("descriptor", descriptor), ("pin", pin)):
        raw = v.canonical(obj)
        forbidden = {"authority": ("authority", "descriptor", "pin"), "descriptor": ("descriptor", "pin"), "pin": ("pin",)}[consumer]
        v.require(all(hashes[node].encode() not in raw for node in forbidden), "self or backward hash value")
    return {"edges": [list(edge) for edge in edges], "artifact_sha256": hashes, "NO_HASH_CYCLE": "YES"}


def fixture():
    f = {"canonical_raw": (ROOT / CURRENT).read_bytes(), "event_raw": (ROOT / m.EVENT).read_bytes(), "installation_requested": False, "new_events": []}
    for key, path in (("authority", AUTHORITY), ("descriptor", DESCRIPTOR), ("pin", PIN), ("work", WORK), ("ledger", LEDGER), ("plan", PLAN)):
        raw = (ROOT / path).read_bytes()
        f[key], f[key + "_raw"] = v.loads(raw), raw
    return f


def validate(f, source, accepted):
    v.require(not f["installation_requested"], "automatic installation prohibited")
    v.require(f["new_events"] == [], "event #4 or any new event prohibited")
    v.require(v.sha(f["canonical_raw"]) == CURRENT_SHA, "canonical current-state replacement prohibited")
    v.require(f["event_raw"] == accepted["event_raw"] and v.sha(f["event_raw"]) == EVENT_SHA, "event #3 mutation")
    authority = f["authority"]
    graph = hash_graph(f)
    v.require(authority["expected_predecessor_sha256"] == CURRENT_SHA, "wrong predecessor SHA")
    v.require(authority["path"] == AUTHORITY and authority["canonical_path"] == CURRENT, "wrong authority path")
    v.require(authority["scope"] == expected_authority()["scope"], "wrong authority scope")
    v.require(authority["operation"] == expected_authority()["operation"], "wrong operation")
    v.require(authority == expected_authority() and f["authority_raw"] == v.canonical(authority), "authority exact semantic object or canonical bytes drift")
    descriptor = f["descriptor"]
    v.schema("V6_CAPACITY_CURRENT_STATE_V1", descriptor)
    v.require(descriptor["effective_current_descriptor_identity"]["descriptor_id"] == DESCRIPTOR_ID, "wrong descriptor ID")
    expected = rebind(source, v.sha(f["authority_raw"]))
    delta = leaves(source, descriptor)
    v.require(delta == leaves(source, expected) and len(delta) == 3 and descriptor == expected, "fourth descriptor leaf, event, projection or population change")
    v.require(f["descriptor_raw"] == pretty(descriptor), "descriptor stored-byte convention drift")
    v.require(descriptor["event_count"] == 3 and descriptor["event_head"] == source["event_head"] and descriptor["event_chain"] == source["event_chain"], "event chain/count/head drift")
    projection = descriptor["projection"]
    v.require(descriptor["lifecycle_label"] == projection["state"] == "PREPARATION_EXECUTION_AUTHORIZED", "execution state drift")
    v.require(projection == accepted["event"]["next_projection"] and descriptor["projection_sha256"] == v.digest(projection), "projection replay/hash drift")
    phases = projection["phase_authorizations"]
    v.require(phases["PREPARATION_PLANNING"] == phases["PREPARATION_EXECUTION"] == projection["lifecycle"]["PREPARATION_AUTHORIZED"] == "YES", "execution/preparation authorization drift")
    v.require(all(phases[key] == "NO" for key in ("SOURCE_ACQUISITION", "IMAGE_BUILD", "ORACLE_EXECUTION", "PILOT_FINAL_ALLOCATION", "DOWNSTREAM_REPAIR_EXECUTION")), "downstream authorization flipped")
    v.require(descriptor["runtime_authority"] is True and descriptor["authoritative_current_surfaces"] == [CURRENT], "descriptor-form semantics drift")
    cases = projection["case_states"]
    v.require(len(cases) == 433 and cases == source["projection"]["case_states"], "433 case-state drift")
    v.require(all(row["phase"] == "NOT_STARTED" and row["attempt_consumed"] is False and row["environment_identity"] is None and row["slot_accounting"] == [] for row in cases), "attempt consumption or environment-ready claim")
    items = f["work"]["items"]
    v.require(len(items) == len({row["base_attempt_id"] for row in items}) == 641, "wrong 641 opportunities")
    v.require(sum(row["build_network_required"] for row in items) == 583 and sum(not row["build_network_required"] for row in items) == 58, "wrong 583/58 identities")
    v.require(len({row["case_id"] for row in items}) == 431 and not {"matplotlib::1", "matplotlib::8"} & {row["case_id"] for row in items}, "blocker rescue")
    v.require(f["work_raw"] == (ROOT / WORK).read_bytes() and f["work"] == v.loads(f["work_raw"]), "work-item identity/order drift")
    v.require(f["plan_raw"] == (ROOT / PLAN).read_bytes() and f["plan"] == v.loads(f["plan_raw"]), "blocker disposition/plan drift")
    entries = f["ledger"]["entries"]
    v.require(len(entries) == 641 and not f["ledger"]["journal"] and all(row["state"] == "UNSTARTED" and row["claimed"] is False and row["attempt_consumed"] is False for row in entries), "attempt or claim consumption")
    v.require([row["base_attempt_id"] for row in entries] == [row["base_attempt_id"] for row in items], "ledger opportunity identity drift")
    v.require(f["ledger_raw"] == (ROOT / LEDGER).read_bytes() and f["ledger"] == v.loads(f["ledger_raw"]), "ledger bytes drift")
    expected_pin = {"path": CURRENT, "sha256": v.sha(f["descriptor_raw"]), "HUMAN_PI_ACCEPTED": "YES"}
    v.require(f["pin"] == expected_pin and f["pin_raw"] == v.canonical(expected_pin), "wrong canonical pin path, acceptance or bytes")
    v.require(f["pin"]["sha256"] != SOURCE_SHA, "old transition-result SHA pinned")
    return delta, graph


def snapshot():
    stage = m.git("ls-files", "--stage", "-z")
    rows = {}
    for row in stage.split(b"\0"):
        if not row:
            continue
        meta, name = row.split(b"\t", 1)
        mode, oid, index_stage = meta.split()
        v.require(index_stage == b"0", "unmerged index")
        path = ROOT / name.decode()
        raw = os.readlink(path).encode() if path.is_symlink() else oid if mode == b"160000" else path.read_bytes()
        rows[name.decode()] = {"mode": mode.decode(), "index_oid": oid.decode(), "sha256": hashlib.sha256(raw).hexdigest()}
    return {"tracked_files_count": len(rows), "tracked_inventory_sha256": v.digest(rows), "index_entries_sha256": v.sha(stage), "index_file_sha256": v.sha((ROOT / ".git/index").read_bytes())}


def preserve(entry):
    v.require(m.git("rev-parse", "HEAD").decode().strip() == HEAD and m.git("rev-parse", "HEAD^").decode().strip() == PARENT and m.git("branch", "--show-current").decode().strip() == "main", "branch/HEAD/parent drift")
    v.require(m.git("diff", "--name-only") == m.git("diff", "--cached", "--name-only") == b"", "tracked/index mutation")
    result = snapshot()
    v.require(all(result[key] == entry[key] for key in result), "tracked bytes/index drift")
    untracked = {row.decode() for row in m.git("ls-files", "--others", "--exclude-standard", "-z").split(b"\0") if row}
    v.require(untracked <= FILES and {str(row.relative_to(ROOT)) for row in E.iterdir()} <= FILES, "unexpected new file, closure, installer or event")
    v.require(v.sha((ROOT / CURRENT).read_bytes()) == CURRENT_SHA and v.sha((ROOT / m.EVENT).read_bytes()) == EVENT_SHA, "canonical/event bytes changed")
    result.update(status="PASS", untracked_paths=sorted(untracked), real_attempt_state=m.real_attempt_state())
    return result


def probes(base, source, accepted):
    results = []

    def reject(name, mutate, target=None):
        f = copy.deepcopy(base)
        mutate(f)
        # Rehash altered objects so probes reach semantic checks.
        if target:
            f[target + "_raw"] = pretty(f[target]) if target in ("descriptor", "work", "plan", "ledger") else v.canonical(f[target])
        if target == "authority":
            f["descriptor"]["effective_current_descriptor_identity"]["human_pi_transition"]["sha256"] = v.sha(f["authority_raw"])
            f["descriptor_raw"] = pretty(f["descriptor"])
        if target in ("authority", "descriptor"):
            f["pin"]["sha256"] = v.sha(f["descriptor_raw"])
            f["pin_raw"] = v.canonical(f["pin"])
        try:
            validate(f, source, accepted)
        except ValueError as error:
            results.append({"probe": name, "status": "PASS_REJECTED", "reason": str(error), "mutation": "IN_MEMORY_ONLY"})
        else:
            raise ValueError("probe accepted: " + name)

    for key, value, name in (
        ("expected_predecessor_sha256", "0" * 64, "wrong predecessor SHA"),
        ("path", B + "wrong_authority.json", "wrong authority path"),
        ("scope", "EXACT_PREPARATION_PLANNING_TRANSITION_INSTALLATION_ONLY", "wrong authority scope"),
        ("operation", "INSTALL_AUTOMATICALLY", "wrong operation"),
    ):
        reject(name, lambda f, key=key, value=value: f["authority"].update({key: value}), "authority")
    reject("wrong descriptor ID", lambda f: f["descriptor"]["effective_current_descriptor_identity"].update(descriptor_id="WRONG"), "descriptor")
    reject("stale planning installation authority", lambda f: f["descriptor"]["effective_current_descriptor_identity"].update(human_pi_transition=copy.deepcopy(source["effective_current_descriptor_identity"]["human_pi_transition"])), "descriptor")
    reject("wrong authority SHA", lambda f: f["descriptor"]["effective_current_descriptor_identity"]["human_pi_transition"].update(sha256="0" * 64), "descriptor")
    reject("fourth descriptor leaf change", lambda f: f["descriptor"]["projection"]["lifecycle"].update(ORACLE_AUTHORIZED="YES"), "descriptor")
    reject("event_count mutation", lambda f: f["descriptor"].update(event_count=4), "descriptor")
    reject("event #3 mutation", lambda f: f.update(event_raw=f["event_raw"] + b"\n"))
    reject("event_head mutation", lambda f: f["descriptor"]["event_head"].update(event_id="0" * 64), "descriptor")
    reject("projection mutation", lambda f: f["descriptor"]["projection"].update(state="PREPARATION_PLANNING_AUTHORIZED"), "descriptor")
    for key, value, name in (
        ("PREPARATION_EXECUTION", "NO", "PREPARATION_EXECUTION flipped"),
        ("SOURCE_ACQUISITION", "YES", "SOURCE_ACQUISITION flipped"),
        ("IMAGE_BUILD", "YES", "IMAGE_BUILD flipped"),
        ("ORACLE_EXECUTION", "YES", "ORACLE flipped"),
        ("PILOT_FINAL_ALLOCATION", "YES", "ALLOCATION flipped"),
        ("DOWNSTREAM_REPAIR_EXECUTION", "YES", "DOWNSTREAM_REPAIR flipped"),
    ):
        reject(name, lambda f, key=key, value=value: f["descriptor"]["projection"]["phase_authorizations"].update({key: value}), "descriptor")
    reject("PREPARATION_AUTHORIZED flipped", lambda f: f["descriptor"]["projection"]["lifecycle"].update(PREPARATION_AUTHORIZED="NO"), "descriptor")
    for key, value, name in (
        ("scientific_failure", True, "case-state mutation"),
        ("attempt_consumed", True, "attempt consumption"),
        ("environment_identity", {"image": "CLAIM"}, "environment-ready claim"),
    ):
        reject(name, lambda f, key=key, value=value: f["descriptor"]["projection"]["case_states"][0].update({key: value}), "descriptor")
    reject("blocker rescue", lambda f: f["work"]["items"][0].update(case_id="matplotlib::1"), "work")
    reject("blocker disposition mutation", lambda f: next(row for row in f["plan"]["plans"] if row["case_id"] == "matplotlib::8").update(planning_disposition="PREPARATION_PLAN_CONSTRUCTIBLE"), "plan")
    reject("wrong 641", lambda f: f["work"]["items"].pop(), "work")
    reject("wrong 583/58", lambda f: f["work"]["items"][0].update(build_network_required=False), "work")
    reject("ledger attempt consumption", lambda f: f["ledger"]["entries"][0].update(attempt_consumed=True), "ledger")
    for key, value, name in (
        ("sha256", SOURCE_SHA, "pin old transition-result SHA"),
        ("sha256", "0" * 64, "pin wrong descriptor SHA"),
        ("path", DESCRIPTOR, "pin wrong canonical path"),
        ("HUMAN_PI_ACCEPTED", "NO", "pin HUMAN_PI_ACCEPTED != YES"),
    ):
        reject(name, lambda f, key=key, value=value: f["pin"].update({key: value}), "pin")
    reject("backward hash dependency", lambda f: f["authority"].update(descriptor_sha256=v.sha(f["descriptor_raw"])), "authority")
    reject("hash cycle", lambda f: f["authority"].update(pin_sha256=v.sha(f["pin_raw"])), "authority")
    reject("self hash", lambda f: f["authority"].update(self_hash=v.sha(f["authority_raw"])), "authority")
    reject("canonical current-state replacement", lambda f: f.update(canonical_raw=f["descriptor_raw"]))
    reject("automatic installation", lambda f: f.update(installation_requested=True))
    reject("event #4 creation", lambda f: f.update(new_events=[{"sequence": 4}]))
    return results


def guard_probes():
    # Exercise the audit hook directly; do not invoke any prohibited OS action.
    results = []
    for name, event, args in (
        ("guard rejects canonical file write", "open", (str(ROOT / CURRENT), "w", os.O_WRONLY | os.O_TRUNC)),
        ("guard rejects canonical atomic replacement", "os.rename", (str(ROOT / DESCRIPTOR), str(ROOT / CURRENT))),
        ("guard rejects event #4 file creation", "open", (str(E / "event_4.json"), "x", os.O_WRONLY | os.O_CREAT)),
        ("guard rejects git staging", "subprocess.Popen", (None, ["git", "add", AUTHORITY])),
        ("guard rejects build execution", "subprocess.Popen", (None, ["docker", "build", "."])),
        ("guard rejects network connection", "socket.connect", (None, ("example.invalid", 443))),
    ):
        try:
            m.readonly_guard(event, args)
        except RuntimeError as error:
            results.append({"probe": name, "status": "PASS_REJECTED", "reason": str(error), "mutation": "DIRECT_GUARD_CALL_ONLY; NO_OS_ACTION"})
        else:
            raise ValueError("guard probe accepted: " + name)
    return results


def audit():
    entry = v.loads((E / "entry_verification.json").read_bytes())
    v.require(entry["status"] == "ENTRY_GATE_PASS" and entry["branch"] == "main" and entry["head"] == HEAD and entry["parent"] == entry["live_origin_main"] == PARENT and all(entry[key] is True for key in ("worktree_clean_before_write", "index_clean_before_write", "untracked_clean_before_write")), "entry gate drift")
    before = preserve(entry)
    v.require(v.sha((ROOT / CLOSURE).read_bytes()) == CLOSURE_SHA, "wrong transition closure")
    source_raw = (ROOT / SOURCE).read_bytes()
    v.require(v.sha(source_raw) == SOURCE_SHA, "wrong accepted successor bytes")
    source = v.loads(source_raw)
    accepted = m.load_fixture()
    current, _ = m.validate_fixture(accepted)
    prereqs = m.prereq_audit(current)
    chain = m.replay(current, accepted["event"], accepted["event_raw"])
    identities = v.validate_event_identity(accepted["event"], accepted["event_raw"])
    v.require(identities == {"event_id": EVENT_ID, "event_sha256": PAYLOAD_SHA, "file_sha256": EVENT_SHA}, "event #3 identities drift")
    f = fixture()
    delta, graph = validate(f, source, accepted)
    v.require(chain["final_projection_sha256"] == f["descriptor"]["projection_sha256"], "bound descriptor replay mismatch")
    rejection = probes(f, source, accepted) + guard_probes()
    after = preserve(entry)
    v.require(before == after, "protected state changed during audit")
    cases = source["projection"]["case_states"]
    blockers = [{key: row[key] for key in ("case_id", "planning_disposition", "plan_sha256", "blockers")} for row in f["plan"]["plans"] if row["case_id"] in ("matplotlib::1", "matplotlib::8")]
    controls = {}
    for key in ("authority", "descriptor", "pin"):
        raw = f[key + "_raw"]
        controls[key] = {"path": {"authority": AUTHORITY, "descriptor": DESCRIPTOR, "pin": PIN}[key], "stored_sha256": v.sha(raw), "canonical_semantic_sha256": v.digest(f[key]), "size_bytes": len(raw), "semantic_object": f[key] if key != "descriptor" else f[key]["effective_current_descriptor_identity"]}
    return {
        "status": "PASS", "failed_checks": 0, "schema": "V6_CAPACITY_CURRENT_STATE_V1",
        "schema_validation": "PASS", "three_leaf_delta": delta, "controls": controls,
        "hash_graph": graph, "event_3_identities": identities, "event_chain_replay": chain,
        "frozen_current_state_schema_sha256": "cc326c0e8099bc19bf9c002ad48af68cbf488360e4bbb8cb9e0e0266b017b0f9",
        "accepted_runtime_bindings": {"runtime_egress_closure": {"path": m.CLOSURE, "sha256": m.CLOSURE_SHA}, "enforcement_identity": m.ENFORCEMENT, "runtime_source_sha256": m.SOURCE_SHA, "runtime_configuration_data_sha256": m.DATA_SHA, "semantics_changed": False, "live_qualification_rerun": False},
        "prerequisites": prereqs, "rejection_probe_count": len(rejection), "rejection_probes": rejection,
        "population_preservation": {"case_states": 433, "case_states_canonical_sha256_before_and_after": v.digest(cases), "opportunities": 641, "restricted": 583, "network_NONE": 58, "constructible_cases": 431, "attempts_consumed": 0, "environment_ready_cases": 0, "work_items_stored_sha256": v.sha(f["work_raw"]), "restricted_identity_sha256": v.digest([row["base_attempt_id"] for row in f["work"]["items"] if row["build_network_required"]]), "network_NONE_identity_sha256": v.digest([row["base_attempt_id"] for row in f["work"]["items"] if not row["build_network_required"]]), "blockers": blockers},
        "preservation": after, "firewall": FIREWALL,
        "qualification": "Package byte/semantic validation and accepted committed-evidence replay only; live runtime/egress/build qualification and scientific validation were not run.",
    }


if __name__ == "__main__":
    v.require(sys.argv[1:] in ([], ["--json"]), "expected no argument or --json")
    sys.addaudithook(m.readonly_guard)
    result = audit()
    recorded = E / "validation_results.json"
    if recorded.exists():
        v.require(recorded.read_bytes() == pretty(result), "stored results differ from fresh audit")
    manifest_path = E / "artifact_sha256.json"
    if manifest_path.exists():
        manifest = v.loads(manifest_path.read_bytes())
        v.require(set(manifest["artifacts"]) == FILES - {PREFIX + "artifact_sha256.json"}, "manifest scope drift")
        v.require(set(result["preservation"]["untracked_paths"]) == FILES, "final exact inventory drift")
        for path, item in manifest["artifacts"].items():
            raw = (ROOT / path).read_bytes()
            v.require(item == {"sha256": v.sha(raw), "size_bytes": len(raw)}, "artifact byte drift: " + path)
    if sys.argv[1:] == ["--json"]:
        sys.stdout.write(pretty(result).decode())
    else:
        print(json.dumps({"status": result["status"], "rejection_probe_count": result["rejection_probe_count"], "failed_checks": result["failed_checks"], "NO_HASH_CYCLE": result["hash_graph"]["NO_HASH_CYCLE"], "descriptor_sha256": result["controls"]["descriptor"]["stored_sha256"]}, sort_keys=True))

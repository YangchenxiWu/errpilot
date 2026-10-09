"""Derive partial candidate contracts; unresolved client authority stops sources/E2E.

All writes are confined to this new evidence namespace. Imported predecessors
are used only for pure compilation and read-only identity inspection.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import importlib
import json
import os
import stat
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
EVIDENCE = ROOT / "evaluation/downstream_benchmark/evidence"
RESUME = EVIDENCE / "v6_preparation_execution_production_runtime_installation_resume_v1"
BRIDGE = EVIDENCE / "v6_production_runtime_image_identity_compatibility_bridge_v1"
FORENSICS = EVIDENCE / "v6_production_runtime_topology_exec_forensics_v1"
REQUEST = Path("/Users/wuyangchenxi/.codex/attachments/c62e1362-5183-4e32-9ccf-da1667105a48/已粘贴的文本.txt")
HEAD = "e492d159daf188323efcfe121aa019d5b098bfb2"
STATE_SHA = "e48580c1f9769d1b93ab995e6dcef3689c6920a9ce7b83f728526e9694dc68fd"
EVENT = "237d8020668f338c04065beb8557d8f25263fbfc0282003dcc5b2af67a20a50d"
BLOCK = "BLOCKED_BY_UNRESOLVED_CLIENT_AUTHORIZATION"
COMMON = {"candidate_only": True, "HUMAN_PI_ACCEPTED": "NO", "runtime_effective": "NO",
          "execute_now": False, "production_gate": BLOCK}
PIN_VALUES = {
    "controller": "bb85d27cd8eefe0a82160657b296d36513ab931cfa97c5954447c0c565c11877",
    "provider": "d466c9310d22754c0c3c9744764bcc402aef988195da7f7aea45b9700eb1de0a",
    "installation_candidate": "83ea48b5c4ce7835a46bb6e2207e1893d430b8147b3efa35d4535c0bff08efad",
    "installation_plan": "de3923da16b4a4ee9b64945baa998a9eba05ca08f0eff92fbe1b2c628a410fbd",
    "installation_closure": "a764800f1a2bb8745ded16dca8452b4ca50e368dcefa630ee7784776103870f9",
    "topology_contract": "8ee7bc08d55e8b0c9e628260fed4105e7cd122a9e123f527da37f4776fa96ce4",
    "receipt_contract": "030eebcdfe689cafdb7115a3ec26766c228dd01c4e1bb3ab33f4e9791e96f6d9",
    "receipt_schema": "8a5077220001757af0b4885b9ba5ca23d9bc1adcc7acecb0dc9273647e0ca397",
    "runtime_source": "c83da6f5eb355702f994c28efc6b14bc36988a9cc405ff05a689a9f97128f4b6",
    "runtime_configuration": "654299e49b0fc8833f093ecc887b4578970895ce28aa5359b4b37246f7b6190e",
}
COMMANDS = []


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pretty(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                       allow_nan=False) + "\n").encode("utf-8")


def write(name, value):
    target = HERE / name
    assert target.parent.resolve().is_relative_to(HERE)
    target.write_bytes(pretty(value))


def read(path):
    return json.loads(path.read_bytes())


def run(argv):
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, check=False,
                            env={**os.environ, "GIT_OPTIONAL_LOCKS": "0",
                                 "PYTHONDONTWRITEBYTECODE": "1"}, timeout=60)
    COMMANDS.append({"argv": argv, "returncode": result.returncode,
                     "stdout": result.stdout.decode("utf-8"),
                     "stderr": result.stderr.decode("utf-8")})
    assert result.returncode == 0, (argv, result.stderr)
    return result.stdout


def file_record(path):
    return {"sha256": sha(path.read_bytes()), "size_bytes": path.stat().st_size}


def snapshot_tree(root):
    result = {}
    for path in [root, *sorted(root.rglob("*"))]:
        assert not path.is_symlink()
        rec = {"type": "directory" if path.is_dir() else "file",
               "mode": stat.S_IMODE(path.lstat().st_mode)}
        if path.is_file():
            rec.update(file_record(path))
        result[str(path.relative_to(root))] = rec
    return result


def replay_predecessor(root, expected_sha, expected_count):
    manifest = root / "artifact_sha256.json"
    assert sha(manifest.read_bytes()) == expected_sha
    data = read(manifest)
    assert len(data["files"]) == data["file_count"] == expected_count
    expected = set(data["files"]) | {"artifact_sha256.json"}
    actual = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}
    assert actual == expected
    records = {}
    for name, rec in data["files"].items():
        path = root / name
        assert not path.is_symlink()
        observed = file_record(path)
        assert observed == {k: rec[k] for k in observed}
        records[name] = observed
    records["artifact_sha256.json"] = file_record(manifest)
    return {"path": str(root.relative_to(ROOT)), "manifest_sha256": expected_sha,
            "payload_count": expected_count, "total_files": expected_count + 1,
            "complete_set_size_sha_replay": "PASS", "files": records}


def functions(path):
    tree = ast.parse(path.read_bytes())
    result = {}

    def visit(nodes, prefix=""):
        for node in nodes:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                name = prefix + node.name
                result[name] = {"ast_sha256": sha(ast.dump(node, include_attributes=False).encode()),
                                "line": node.lineno, "end_line": node.end_lineno}
                visit(node.body, name + ".")
    visit(tree.body)
    return result


def main():
    assert ROOT == Path("/Users/wuyangchenxi/errpilot")
    assert not (HERE / "entry_snapshot.json").exists(), "single allocation only"
    assert run(["git", "rev-parse", "HEAD"]).decode().strip() == HEAD
    assert run(["git", "branch", "--show-current"]).decode().strip() == "main"
    assert run(["git", "diff", "--binary"]) == run(["git", "diff", "--cached", "--binary"]) == b""
    paths = [x for x in run(["git", "ls-files", "-z"]).decode().split("\0") if x]
    assert len(paths) == 1065
    tracked = {name: file_record(ROOT / name) for name in paths}
    untracked = [x for x in run(["git", "ls-files", "--others", "--exclude-standard", "-z"]).decode().split("\0") if x]
    predecessors = [replay_predecessor(BRIDGE, "ee8948b829a072ff10e3a41ba086afb4151821010661d89a05ce444ba95369e8", 280),
                    replay_predecessor(FORENSICS, "96b22bb49d14b366d3d6ef7f4d9101b48cae5c6e85112c4798319d4fc7d2c1dd", 219)]
    expected_untracked = {str(Path(p["path"]) / name) for p in predecessors for name in p["files"]}
    own = {x for x in untracked if x.startswith(str(HERE.relative_to(ROOT)) + "/")}
    assert set(untracked) - own == expected_untracked and len(expected_untracked) == 501
    pins = {}
    for role, digest in PIN_VALUES.items():
        matches = [name for name, record in tracked.items() if record["sha256"] == digest]
        if role == "receipt_contract":
            # The authoritative provider/plan names this exact file. An identical
            # frozen receipt_contract.json copy is preserved, not competing authority.
            controlling = str((RESUME / "production_receipt_authority_contract.json").relative_to(ROOT))
            assert controlling in matches
            matches = [controlling]
        assert len(matches) == 1, (role, matches)
        pins[role] = {"path": matches[0], "sha256": digest, "status": "PASS"}
    corrected = BRIDGE / "corrected_production_provider_candidate.py"
    assert sha(corrected.read_bytes()) == "82561a9bfe646114e61d00c2c8e01012086a28b15d0bf67488e1d787a6f5371f"
    state_path = ROOT / "evaluation/downstream_benchmark/v6_current_state.json"
    assert sha(state_path.read_bytes()) == STATE_SHA
    state = read(state_path)
    assert state["lifecycle_label"] == "PREPARATION_EXECUTION_AUTHORIZED"
    assert state["event_count"] == 3 and state["event_head"]["event_id"] == EVENT
    for event in state["event_chain"]:
        assert sha((ROOT / event["path"]).read_bytes()) == event["sha256"]
    for ref in (state["contract"], state["effective_current_descriptor_identity"]["human_pi_transition"]):
        assert sha((ROOT / ref["path"]).read_bytes()) == ref["sha256"]
    p = importlib.import_module("evaluation.downstream_benchmark.evidence.v6_production_runtime_image_identity_compatibility_bridge_v1.corrected_production_provider_candidate")
    old = importlib.import_module("evaluation.downstream_benchmark.evidence.v6_preparation_execution_production_runtime_installation_resume_v1.production_provider_candidate")
    config = p.frozen_inputs()
    population = p.legacy.population()
    ids = [x["base_attempt_id"] for x in population["items"]]
    assert p.population_identity(population, (ROOT / p.legacy.PACKAGE / "work_items_candidate.json").read_bytes()) == p.expected_population_identity()
    journal = p.ledger.Ledger(p.a.OUTPUT_ROOT, namespace=p.ledger.REAL, real_ids=ids)
    counts = dict(Counter(journal.state(x) for x in ids))
    assert counts == {"UNSTARTED": 641}
    ledger_tree = snapshot_tree(p.a.OUTPUT_ROOT / "ledger")
    assert not any(path.startswith(("claims/", "terminals/", "locks/")) and rec["type"] == "file"
                   for path, rec in ledger_tree.items())
    targets = read(RESUME / "installation_plan.json")["future_targets"]
    assert all(not (ROOT / path).exists() for path in targets.values())
    original_observation = p.a.OUTPUT_ROOT / "qualification/production_runtime_topology_provisioning_v1/live_topology_observation.json"
    corrected_observation = BRIDGE / "corrected_topology_observation.json"
    assert sha(original_observation.read_bytes()) == "3a9166d306fee282279702312d6e170cad6f3a1f60b8ce70bb6e3e579af746ea"
    assert sha(corrected_observation.read_bytes()) == "f7dcd64c808aae7b8e9db4e0835594b1f7a488ec52b186686a9f362a84aa65ac"
    historical = read(original_observation)
    later = read(corrected_observation)
    assert set(historical) == set(later)
    differences = [k for k in historical if historical[k] != later[k]]
    assert differences == ["daemon_socket_observation"]
    write("entry_snapshot.json", {"tracked": tracked, "index_sha256": sha((ROOT / ".git/index").read_bytes()),
          "ledger_root": str(p.a.OUTPUT_ROOT / "ledger"), "ledger_tree": ledger_tree,
          "namespace": {"path": str(p.a.OUTPUT_ROOT / "namespace.json"), **file_record(p.a.OUTPUT_ROOT / "namespace.json")},
          "predecessors": predecessors, "head": HEAD, "ordered_attempt_ids": ids,
          "production_targets": targets, "current_state_sha256": STATE_SHA})
    raw_request = REQUEST.read_bytes()
    (HERE / "raw_human_pi_request.txt").write_bytes(raw_request)
    write("human_pi_decision.json", {**COMMON, "schema": "V6_TOPOLOGY_STABILITY_SUCCESSOR_HUMAN_PI_DECISION_RECORD_V1",
          "authority": "HUMAN_PI_ADJUDICATE_V6_PRODUCTION_RUNTIME_TOPOLOGY_STABILITY_AND_EXEC_ORIGIN",
          "decision": "ADOPT_OPTION_B_VERSIONED_TOPOLOGY_SEMANTIC_STABILITY_SUCCESSOR_V1",
          "authorization": "BOUNDED_SUCCESSOR_CONTRACT_AND_QUALIFICATION_CANDIDATE_CONSTRUCTION_ONLY",
          "exec_origin": "ORIGIN_NOT_ESTABLISHED", "benign": "NOT_PROVEN", "malicious": "NOT_PROVEN",
          "cleanup_or_exoneration_authority": False, "request_sha256": sha(raw_request),
          "request_copy": "raw_human_pi_request.txt", "source": "Direct user-supplied request",
          "successor_accepted": False})
    write("entry_verification.json", {**COMMON, "schema": "V6_TOPOLOGY_STABILITY_SUCCESSOR_ENTRY_V1", "status": "PASS",
          "branch": "main", "local_head": HEAD, "live_origin_main": HEAD,
          "live_origin_evidence": "live_origin_entry.json", "canonical_sha256": STATE_SHA,
          "lifecycle": state["lifecycle_label"], "event_count": 3, "event_3_id": EVENT,
          "tracked_count": 1065, "predecessor_untracked_count": 501, "other_preexisting_untracked": [],
          "real_ledger_states": counts, "claims": 0, "terminals": 0, "retries": 0, "orphans": 0,
          "production_targets_absent": targets, "tracked_diff_empty": True, "index_diff_empty": True,
          "repository_AGENTS_present": (ROOT / "AGENTS.md").exists(),
          "airos_current_state_present": (ROOT / ".airos/current_state.md").exists(),
          "new_namespace_preexisted": False, "contract": "Direct attached Human-PI request"})
    write("historical_predecessor_binding.json", {**COMMON, "schema": "V6_TOPOLOGY_STABILITY_PREDECESSOR_BINDING_V1",
          "status": "PASS", "controlling_file_identities": pins, "predecessor_seals": predecessors,
          "corrected_provider": {"path": str(corrected.relative_to(ROOT)), **file_record(corrected)},
          "enforcement_semantic_identity": p.ENFORCEMENT, "enforcement_identity_check": "p.frozen_inputs exact pretty-serialization SHA replay",
          "historical_accepted_status_preserved": True, "successor_installation_authorized": False,
          "original_topology": {"path": str(original_observation), **file_record(original_observation)},
          "image_corrected_topology": {"path": str(corrected_observation.relative_to(ROOT)), **file_record(corrected_observation)},
          "exact_observation_field_difference": differences,
          "source_authority_ambiguous": False})
    serialization = copy.deepcopy(read(RESUME / "topology_observation_contract.json")["canonical_serialization"])
    write("raw_evidence_preservation_contract.json", {**COMMON, "schema": "V6_FULL_RAW_TOPOLOGY_EVIDENCE_PRESERVATION_V2_CANDIDATE",
          "representation": "FULL_RAW_OBSERVATION", "raw_bytes": "Never normalize, drop, reorder, rewrite or relabel source bytes",
          "required_sources": ["full Docker daemon/proxy/network/image inspect bytes", "original Unix socket table bytes",
                               "ExecIDs including original ordering", "raw worker/platform output", "raw route tables",
                               "raw binary hash output", "proxy source and policy bytes", "independent image content-chain evidence"],
          "per_source_binding": ["source identity", "observation method and argv/API", "start and end timestamp",
                                 "exact original byte length", "SHA256 of full original bytes", "success/failure status"],
          "missing_original_timestamp": "UNVERIFIABLE; do not synthesize a per-source timestamp",
          "unknown_exec_evidence": "All historical and new records retained; no cleanup or authorization inference",
          "historical_raw_references": [{"path": str(path.relative_to(ROOT)), **file_record(path)} for path in
              [FORENSICS / "raw_original_daemon_inspect.stdout", FORENSICS / "raw_correction_daemon_inspect.stdout",
               FORENSICS / "raw_original_socket_table.txt", FORENSICS / "raw_correction_socket_table.txt",
               FORENSICS / "exec_process_attribution.json", FORENSICS / "exec_inspect_observations.json"]],
          "raw_bundle_identity": "SHA256 canonical manifest of exact per-source records; separately preserve each original SHA",
          "current_observation_status": "NOT_REOBSERVED_BY_CONSTRUCTION_SCRIPT",
          "raw_identity_is_security_projection_identity": False})
    instance = {"daemon_instance_identity", "proxy_instance_identity", "worker_identity"}
    transient = {"daemon_socket_observation"}
    field_specs = []
    for field in historical:
        classification = "INSTANCE_IDENTITY" if field in instance else "TRANSIENT_DIAGNOSTIC" if field in transient else "STABLE_SECURITY_INVARIANT"
        if field == "daemon_socket_observation":
            typed = "string"
            meaning = "Full raw socket table; split listeners from diagnostics in new projection, never erase raw table"
        else:
            typed = "object" if isinstance(historical[field], dict) else "array" if isinstance(historical[field], list) else "string"
            meaning = "Exact historical value is a candidate baseline reference, requiring fresh independent verification and later acceptance"
        field_specs.append({"field": field, "type": typed, "classification": classification,
                            "historical_reference_value": historical[field], "meaning": meaning,
                            "production_acceptance": "NONE"})
    added = [
        ("daemon_engine_image_id", "string", "STABLE_SECURITY_INVARIANT", "Independent container/store identity plus OCI content chain"),
        ("proxy_engine_image_id", "string", "STABLE_SECURITY_INVARIANT", "Independent container/store identity plus OCI content chain"),
        ("daemon_platform_manifest_identity", "object", "STABLE_SECURITY_INVARIANT", "Exact running/selected manifest digest, size, mediaType, linux/amd64"),
        ("proxy_platform_manifest_identity", "object", "STABLE_SECURITY_INVARIANT", "Exact running/selected manifest digest, size, mediaType, linux/amd64"),
        ("daemon_rootfs_identity", "object", "STABLE_SECURITY_INVARIANT", "Exact ordered RootFS diff_ids, configuration and platform chain"),
        ("proxy_rootfs_identity", "object", "STABLE_SECURITY_INVARIANT", "Exact ordered RootFS diff_ids, configuration and platform chain"),
        ("daemon_running", "boolean", "STABLE_SECURITY_INVARIANT", "Must independently equal true"),
        ("proxy_running", "boolean", "STABLE_SECURITY_INVARIANT", "Must independently equal true"),
        ("unix_listeners", "array", "STABLE_SECURITY_INVARIANT", "Exact listener path, Protocol, Type, St, Flags; no extra or duplicate endpoint"),
        ("unix_endpoint_ownership_permissions", "object", "UNVERIFIABLE", "Independent stat/ownership evidence required where observable; proc/net/unix does not establish it"),
        ("tcp_udp_listener_inventory", "array", "UNVERIFIABLE", "Independent complete listener inventory; Docker PortBindings absence alone insufficient"),
        ("active_client_authorization", "object", "UNVERIFIABLE", "Mandatory rule and admissible independent attribution are unresolved; no default"),
    ]
    field_specs.extend({"field": name, "type": typed, "classification": classification,
                        "mandatory": "UNDECIDED_BY_HUMAN_PI" if name == "active_client_authorization" else True,
                        "evidence_requirement": meaning}
                       for name, typed, classification, meaning in added)
    listener_fields = ["Path", "Protocol", "Type", "St", "Flags"]
    socket = read(FORENSICS / "socket_diff_analysis.json")
    listeners = [{k: row[k] for k in listener_fields} for row in socket["original_records"]
                 if row["record_kind_inference"] == "LISTENER"]
    write("security_projection_contract_candidate.json", {**COMMON,
          "schema": "V6_LIVE_DAEMON_TOPOLOGY_SEMANTIC_STABILITY_V2_CANDIDATE",
          "construction_status": "PARTIAL_BLOCKED", "uniquely_executable_production_contract": False,
          "representation": "STABLE_SECURITY_PROJECTION", "canonical_serialization": serialization,
          "fields": field_specs, "historical_listener_configuration_reference": listeners,
          "listener_order": "Sort by Path, Protocol, Type, St, Flags; reject duplicates and unauthorized endpoints",
          "mandatory_invariants": ["immutable BuildKit reference plus independent Engine/OCI identity",
              "exact daemon/proxy instance and running state", "exact worker and ordered platforms", "native/daemon binary hashes",
              "Unix BuildKit endpoint", "exact daemon argv/DNS", "daemon internal-only network and exact semantics/participants",
              "proxy exactly dual-homed with exact existing network bindings", "exact proxy image/source/policy",
              "only files.pythonhosted.org:443 and pypi.org:443 CONNECT origins", "no published ports",
              "no default or unauthorized external daemon route", "exact approved Unix listener tuples",
              "independent endpoint ownership/permissions where observable", "no unauthorized Unix/TCP listeners",
              "no independently established unauthorized clients", "exact enforcement identity"],
          "unverified_mandatory_field": "BLOCK; no omit/null/empty-list success substitution",
          "missing_client_rule": "client_authorization_decision_point.json",
          "instance_replacement": "Changes projection; never diagnostic-only",
          "diagnostic_only": ["ExecIDs and their ordering", "socket Num/Inode/RefCount", "connection turnover", "observation timestamps"],
          "stable_projection_not_sufficient_for_authorization": True,
          "installed_accepted_projection": "NOT_CREATED_NOT_ACCEPTED",
          "security_projection_sha256": "NOT_COMPUTED; no complete independently authorized gate/field specification"})
    write("transient_diagnostic_contract_candidate.json", {**COMMON,
          "schema": "V6_TRANSIENT_TOPOLOGY_DIAGNOSTICS_V2_CANDIDATE", "representation": "TRANSIENT_DIAGNOSTICS",
          "preserve_exact": ["ExecIDs and ordering", "socket Num/Inode/RefCount", "connected Path/Protocol/Type/St/Flags",
                             "every raw line", "observation method and timestamps", "diagnostic connection lifecycle"],
          "configuration_projection_excludes": ["ExecIDs", "incidental socket addresses/inodes", "timestamps", "connected record multiplicity"],
          "connected_records": "Preserved and evaluated in separate client-authorization gate; never generically authorized",
          "turnover_alone_means": "NEITHER_AUTHORIZED_NOR_MALICIOUS",
          "listener_type_state_flags_path": "Mandatory security invariant, never removed as transient",
          "historical_new_socket_records": [row for row in socket["correction_records"]
              if row["raw_line"] not in {x["raw_line"] for x in socket["original_records"]}],
          "historical_two_record_disposition": "UNRESOLVED", "current_socket_table": "UNVERIFIED"})
    write("client_authorization_decision_point.json", {**COMMON,
          "schema": "V6_SUCCESSOR_CLIENT_AUTHORIZATION_HUMAN_PI_DECISION_POINT_V1", "status": BLOCK,
          "why_not_unique": "Option B authorizes semantic-stability design but does not decide whether every active client must be independently authorized, or define admissible complete attribution evidence. Section 6 explicitly requires a separate decision point when the rule is not unique.",
          "unresolved_fields": {"active_client_authorization_mandatory": "UNDECIDED_BY_HUMAN_PI",
              "independent_attribution_source_and_coverage": "NOT_DEFINED",
              "unattributed_client_effect_on_admission": "NO_PRODUCTION_ADMISSION_UNTIL_EXACT_RULE_ACCEPTED"},
          "not_an_adopted_policy": [
              {"option": "Require complete independent authorization of every active client",
               "condition": "Define exact approved host/client identity, scope, evidence source, completeness and relation to socket/exec/attempt"},
              {"option": "Treat historic unknown execs as unresolved forensic evidence outside a universal active-client gate",
               "condition": "Explicitly decide mandatory fields, continuing unknown disposition, and exact handling of new active clients; never infer authorization"}],
          "decision_requested": ["Choose the mandatory active-client authorization rule explicitly",
              "Define admissible independent evidence and complete coverage criterion",
              "Decide how unattributed historical/current active clients affect the production gate without exoneration",
              "Authorize any additional evidence acquisition separately if necessary"],
          "not_selected_by_agent": True, "source_E2E_construction_stopped_at_this_gate": True})
    write("unknown_exec_authorization_policy_candidate.json", {**COMMON,
          "schema": "V6_UNKNOWN_EXEC_AUTHORIZATION_POLICY_V2_CANDIDATE", "status": "PARTIAL_BLOCKED",
          "rules": ["UNKNOWN is never AUTHORIZED", "UNKNOWN is never automatically MALICIOUS",
              "Unexplained new listener or externally reachable endpoint BLOCKS", "Unverified mandatory security invariant BLOCKS",
              "If active client authorization is mandatory, unattributed client BLOCKS pending independent authority",
              "No generic buildctl allowlist", "No arbitrary dial-stdio authorization from BuildKit binary identity",
              "Never remove unknown-exec evidence"],
          "separate_assessments": ["CONFIGURATION_VALIDATION", "CLIENT_AUTHORIZATION_EVIDENCE", "FORENSIC_DIAGNOSTICS"],
          "exact_active_client_rule": "UNRESOLVED_SEPARATE_HUMAN_PI_DECISION_REQUIRED",
          "exec_A_B_C_D_initiating_host_commands": "ORIGIN_NOT_ESTABLISHED",
          "configuration_no_observed_drift_is_client_authorization": False,
          "current_active_client_census": "UNVERIFIED", "decision_point": "client_authorization_decision_point.json"})
    order = ["verify exact canonical descriptor, full event chain and event #3 authority",
             "verify independently Human-PI accepted successor effectivity pin",
             "verify exact installed controller/provider/contracts/shared source bytes and committed publication",
             "verify exact immutable work membership and 641/583/58 population",
             "acquire new complete raw topology evidence with original-byte preservation",
             "independently validate every mandatory security invariant",
             "compute canonical STABLE_SECURITY_PROJECTION SHA",
             "compare to independently installed accepted security projection binding",
             "apply exact accepted unknown-exec/client-authorization rule; unresolved policy BLOCKS",
             "issue, canonicalize, read back and verify distinct production V2 receipt for RESTRICTED_DEFAULT; NONE has null receipt",
             "only then exclusive durable claim with exact immutable receipt SHA"]
    write("topology_freshness_contract_candidate.json", {**COMMON, "schema": "V6_TOPOLOGY_FRESHNESS_V2_CANDIDATE",
          "controller_preclaim_order": order, "provider": "Independently repeat canonical/source/work/mandatory-security/client checks with newly acquired raw evidence immediately before every build; never trust controller observation alone",
          "identities": {"CURRENT_RAW_OBSERVATION_SHA": "Full original-byte current raw bundle evidence manifest",
              "CURRENT_SECURITY_PROJECTION_SHA": "Canonical typed current stable security fields only",
              "INSTALLED_ACCEPTED_SECURITY_PROJECTION_SHA": "Separate later Human-PI accepted installed comparison authority",
              "PRODUCTION_EFFECTIVITY_PIN_SHA": "Exact separately accepted effective descriptor bytes; no candidate pin"},
          "identities_interchangeable": False, "rejection_before_claim_consumption": 0,
          "provider_rejection_after_claim": "Exactly one immutable failure terminal, consumed attempt, no retry",
          "receipt_revalidation": "Stable security binding must match; new raw observations are retained in independent sidecars without changing already issued receipt bytes solely for transient turnover",
          "TOCTOU_limit": "Sequential observations do not prove continuous topology stability; do not claim atomic observation or absence of unobservable clients",
          "new_TTL_nonce_bearer_credential": False, "production_execution_implemented": False})
    v1 = read(RESUME / "production_receipt_authority_contract.json")
    impacts = {}
    changed = {"R1_SCHEMA", "R7_REQUIRED_RECEIPT_BINDINGS", "R9_RUNTIME_AUTHORITY", "R10_FRESHNESS", "R11_PRECLAIM_ORDER", "R15_QUALIFICATION_RECEIPT", "R16_PRODUCTION_RECEIPT", "R17_LIVE_TOPOLOGY_MINIMUM_BINDINGS", "R18_PUBLIC_NETWORK_REQUALIFICATION"}
    explanations = {
        "R1_SCHEMA": "Distinct V2 candidate and future distinct production V2 schema; V1 never reinterpreted",
        "R7_REQUIRED_RECEIPT_BINDINGS": "Replace equality binding with explicitly named security_projection_sha256; exact raw SHA remains separately verifiable mandatory sidecar evidence",
        "R9_RUNTIME_AUTHORITY": "Candidate/schema runtime_authority=false; future production V2 requires independent new effectivity acceptance",
        "R10_FRESHNESS": "Fresh full raw evidence plus identical accepted security projection and independent mandatory client gate; no equality of incidental raw socket inodes",
        "R11_PRECLAIM_ORDER": "Versioned order separately validates security projection, raw preservation and exact client policy before receipt and durable claim",
        "R15_QUALIFICATION_RECEIPT": "V2_CANDIDATE is never production authority; no boolean/schema promotion",
        "R16_PRODUCTION_RECEIPT": "Future V2 production receipt is separately accepted and installed; not constructed here",
        "R17_LIVE_TOPOLOGY_MINIMUM_BINDINGS": "Existing exact mandatory image/instance/network/source fields retained, with explicit listener and independent client gates",
        "R18_PUBLIC_NETWORK_REQUALIFICATION": "Frozen 2/2 remains controlling; fresh local provider/controller security and client checks mandatory, no public probe"}
    for name, values in v1["human_pi_decision"]["rules"].items():
        impacts[name] = {"frozen_V1": values, "candidate_impact": "VERSIONED_CHANGE" if name in changed else "PRESERVE",
                         "analysis": explanations.get(name, "Preserve exact once-only, origin, receipt SHA, no-reuse, NONE or separate-authority rule as stated")}
    write("receipt_contract_impact_analysis.json", {**COMMON, "schema": "V6_RECEIPT_V1_TO_V2_IMPACT_V1",
          "v1_receipt_contract": pins["receipt_contract"], "v1_receipt_schema": pins["receipt_schema"],
          "all_R1_R22": impacts, "replacing_raw_SHA_changes_meaning": True, "distinct_contract_and_schema_required": True,
          "raw_sha_in_receipt_bytes": "Excluded from candidate stable identity design; bind mandatory immutable sidecar by exact receipt SHA, attempt, stage and fresh raw evidence SHA",
          "sidecar_design_acceptance": "CANDIDATE_ONLY; requires independent Human-PI acceptance",
          "V1_live_daemon_topology_observation_sha256": "Frozen raw-observation meaning; never relabeled"})
    schema = copy.deepcopy(read(RESUME / "receipt_schema.json"))
    old_field = "live_daemon_topology_observation_sha256"
    schema["title"] = "V6_RESTRICTED_BUILD_EGRESS_ENFORCEMENT_RECEIPT_V2_CANDIDATE"
    schema["required"] = ["security_projection_sha256" if x == old_field else x for x in schema["required"]]
    schema["properties"]["security_projection_sha256"] = schema["properties"].pop(old_field)
    schema["properties"]["schema"]["const"] = schema["title"]
    schema["properties"]["runtime_authority"]["const"] = False
    schema["properties"]["runtime_authority"]["type"] = "boolean"
    for name, value in [("candidate_only", True), ("provider_independent_freshness_required", True)]:
        schema["required"].append(name)
        schema["properties"][name] = {"type": "boolean", "const": value}
    schema["description"] = "Non-effective candidate schema only. No production receipt or accepted pin is generated. Raw observation evidence is an independent mandatory immutable sidecar."
    write("receipt_schema_v2_candidate.json", schema)
    write("receipt_authority_contract_v2_candidate.json", {**COMMON,
          "schema": "V6_PRODUCTION_RECEIPT_AUTHORITY_CONTRACT_V2_CANDIDATE",
          "receipt_schema": schema["title"], "candidate_runtime_authority": False,
          "required_receipt_fields": schema["required"], "canonical_serialization": serialization,
          "allowed_origins": p.ORIGINS, "work_item_identity": "Exact unchanged entire frozen item and one exact base_attempt_id",
          "raw_evidence_sidecar": {"mandatory": True, "bound_by": ["exact receipt SHA", "one exact attempt ID", "verification stage", "raw bundle SHA", "each original source SHA", "current stable projection SHA"],
              "stages": ["issuance", "immediately before exclusive claim", "independently before provider build"],
              "immutable": True, "not_authority": True, "raw_original_bytes_verifiable": True,
              "connected_turnover": "New immutable sidecar; receipt bytes unchanged if mandatory security and exact client checks all pass"},
          "durable_claim_binding": "Exact canonical immutable receipt SHA; provider requires equality to durable claim SHA",
          "NONE": {"receipt": "PROHIBITED", "claim_receipt_sha256": None},
          "once_only": ["one attempt one immutable terminal", "no retry", "no receipt reuse across IDs or after terminal"],
          "preclaim_failure": "Zero claims/terminals/attempt consumption", "new_bearer_TTL_nonce": False,
          "candidate_schema_accepted_by_production": False,
          "future_production_schema": "V6_RESTRICTED_BUILD_EGRESS_ENFORCEMENT_RECEIPT_V2 (requires separate exact acceptance; not created)",
          "effectivity_pin": "NOT_CREATED", "source_pair": "NOT_CONSTRUCTED_PENDING_CLIENT_POLICY"})
    inventories = {"accepted_controller": functions(ROOT / pins["controller"]["path"]),
                   "accepted_provider": functions(ROOT / pins["provider"]["path"]),
                   "image_corrected_provider": functions(corrected)}
    differences = {name: {"accepted": inventories["accepted_provider"].get(name),
                           "image_corrected": inventories["image_corrected_provider"].get(name)}
                   for name in sorted(set(inventories["accepted_provider"]) | set(inventories["image_corrected_provider"]))
                   if inventories["accepted_provider"].get(name, {}).get("ast_sha256") != inventories["image_corrected_provider"].get(name, {}).get("ast_sha256")}
    write("source_semantic_delta.json", {**COMMON, "schema": "V6_SUCCESSOR_SOURCE_SEMANTIC_DELTA_BLOCKED_V1",
          "status": "NOT_CONSTRUCTED", "successor_controller_sha256": None, "successor_provider_sha256": None,
          "new_source_equivalence_audit": "NOT_RUN_NO_SUCCESSOR_SOURCE", "baseline_function_AST_inventories": inventories,
          "replayed_original_to_image_corrected_provider_function_deltas": differences,
          "declared_future_successor_semantics": ["explicit new candidate path/root constructors, excluding installed source",
              "exact successor provider import", "versioned projection and independent raw preservation", "V2 receipt plus immutable raw sidecars",
              "accepted mandatory unknown-exec/client policy", "independent preclaim/provider freshness", "new separate effectivity/source pin contract"],
          "unchanged_scientific_transport_functions": [name for name in inventories["accepted_provider"]
              if name in inventories["image_corrected_provider"] and inventories["accepted_provider"][name]["ast_sha256"] == inventories["image_corrected_provider"][name]["ast_sha256"]],
          "production_synthetic_bypass": False, "reason": BLOCK})
    write("qualification_entry_design_candidate.json", {**COMMON, "schema": "V6_SUCCESSOR_QUALIFICATION_ENTRY_DESIGN_V1",
          "status": "DESIGN_ONLY_NOT_IMPLEMENTED", "new_candidate_path": str(HERE.relative_to(ROOT)),
          "new_qualification_root": str(HERE / "qualification/synthetic_topology_stability_v1"),
          "root_created": False,
          "candidate_constructor": "Explicit newly versioned authorized synthetic constructor gated by exact new module paths and qualification root; normal initialization, no protected real constructor bypass",
          "production_constructor": "No arguments; exact future screening source path, exact independent installed successor effectivity and source bytes; no synthetic fixtures/providers/root/selectors",
          "mutual_exclusion": "Installed source must reject all synthetic interfaces and qualification CLI options; qualification cannot call real runner",
          "old_V1_guards": "Byte-preserved, never bypassed or modified; do not use original synthetic constructor for moved source",
          "prohibited": ["__file__ substitution", "runtime globals replacement", "monkeypatch", "sys.modules identity substitution",
              "arbitrary injectable production factory", "object.__new__ protected real authority workaround"],
          "legitimate_source_E2E": "NOT_RUN; exact successor source pair not constructed"})
    inherited = read(RESUME / "rejection_matrix.json")
    mapped = {letter: {"predecessor_checks": rec["evidence_checks"], "status": "NOT_RUN",
                       "reason": BLOCK, "historical_PASS_is_successor_PASS": False}
              for letter, rec in inherited["required_A_X_coverage"].items()}
    new_tests = ["stale_security_projection_preclaim", "unknown_mandatory_client_authorization", "unresolved_client_policy",
                 "image_manifest_config_independent_identity", "wrong_worker_or_binary", "external_daemon_network",
                 "proxy_source_policy_drift", "unauthorized_Unix_listener", "missing_owner_permission_evidence",
                 "unverified_complete_listener_inventory", "authorized_transient_inode_ExecID_turnover",
                 "provider_independent_freshness", "receipt_raw_sidecar_separate_identity", "candidate_V2_schema_real_authority_rejection",
                 "fixture_production_path_rejection", "production_CLI_synthetic_root_provider_rejection"]
    write("synthetic_e2e_results.json", {**COMMON, "schema": "V6_SUCCESSOR_SYNTHETIC_E2E_BLOCKED_V1",
          "status": "NOT_RUN", "full_A_X": mapped, "A_X_totals": {"passed": 0, "failed": 0, "skipped": 24},
          "reason": "Cannot choose mandatory client authorization semantics or qualify a guessed source pair under this decision",
          "required_successor_additional_tests": {name: "NOT_RUN" for name in new_tests},
          "real_receipts": 0, "real_claims": 0, "real_terminals": 0, "real_builds": 0,
          "synthetic_claims": 0, "synthetic_terminals": 0, "successor_E2E_PASS": False})
    write("rejection_matrix.json", {**COMMON, "schema": "V6_SUCCESSOR_REJECTION_MATRIX_BLOCKED_V1",
          "inherited_77": {name: {"status": "NOT_RUN", "reason": BLOCK} for name in inherited["checks"]},
          "new_categories": {name: {"status": "NOT_RUN", "reason": BLOCK} for name in new_tests},
          "totals": {"passed": 0, "failed": 0, "skipped": 77 + len(new_tests), "inherited": 77, "new": len(new_tests)},
          "AST_equivalence_counted_as_test_pass": False})
    # Read-only scientific/native command replay is predecessor evidence only.
    _, manifest = p.a.load_inputs()
    p.a.validate_population(manifest, population)
    maps = p.exact_json(p.a.ROOT / p.NATIVE / "seven_base_transport_map.json")["mapping"]
    replay = []
    for item in population["items"]:
        plan = p.a.select(manifest, ordinal=item["census_order"], case_id=item["case_id"], plan_sha=item["plan_sha256"])
        assert item == p.a.work_item(plan, item["variant"])
        marker = b"SYNTHETIC_COMPILE_ONLY_NO_RECEIPT_AUTHORITY\n" if item["build_network_required"] else None
        compiled = p.compile_production_transport(item, plan, historical, receipt_raw=marker)
        predecessor = old.compile_production_transport(item, plan, historical, receipt_raw=marker)
        assert compiled == predecessor
        assert compiled["scientific_dockerfile"] == p.a.shared.build_definition(p.a.engine_recipe(plan),
            source_present=item["variant"] != "SOURCE_INDEPENDENT",
            dependency_present=plan["recipe_candidate"]["requirements"]["dependency_bytes_b64"] is not None)
        base = next(x for x in maps if x["scientific_base_authority"] == item["base_image_reference"])
        binding = {**base, "endpoint": config["endpoint"], "native_binary_sha256": config["client_binary_sha256"],
            "same_daemon": True, "daemon_count": 1, "runtime_reference": config["runtime_image"]["immutable_reference"],
            "frontend_alias": "errpilot_frozen_base", "container_id": sha(b"SYNTHETIC_DAEMON"),
            "container_root": "/tmp/errpilot-v6-synthetic-compile-only", "tag": "errpilot-synthetic-compile-only",
            "proxy_internal_host_binding": "add-hosts=errpilot-v6-egress-42393faa3385-v1-proxy=172.28.0.3", "compiled": compiled}
        argv = p.native.native_argv(binding, binding["container_root"], binding["tag"], compiled)
        old_argv = old.native.native_argv(binding, binding["container_root"], binding["tag"], predecessor)
        assert argv == old_argv
        p.validate_command(["docker", "exec", binding["container_id"], *argv], binding)
        replay.append({"base_attempt_id": item["base_attempt_id"], "work_item_sha256": p.a.identity(item),
            "variant": item["variant"], "network": "RESTRICTED_DEFAULT" if item["build_network_required"] else "NONE",
            "scientific_dockerfile_sha256": sha(compiled["scientific_dockerfile"]),
            "execution_dockerfile_sha256": sha(compiled["execution_dockerfile"]), "native_argv_sha256": p.a.identity(argv),
            "same_predecessor_scientific_and_transport": True})
    variants = dict(Counter(item["variant"] for item in population["items"]))
    assert variants.get("SOURCE_INDEPENDENT") == 221 and sum(v for k, v in variants.items() if k != "SOURCE_INDEPENDENT") == 420
    write("scientific_projection_revalidation.json", {**COMMON, "schema": "V6_SCIENTIFIC_PREDECESSOR_REPLAY_BLOCKED_SUCCESSOR_V1",
          "status": "PASS_PREDECESSOR_REPLAY_ONLY", "successor_641_scientific_projection": "NOT_RUN_NO_SUCCESSOR_SOURCE",
          "population": p.population_identity(population, (ROOT / p.legacy.PACKAGE / "work_items_candidate.json").read_bytes()),
          "variants": variants, "blocked_cases": ["matplotlib::1", "matplotlib::8"], "per_item_replay": replay,
          "compiled_count": 641, "commands_executed": 0, "builds": 0, "source_export": 0,
          "compile_marker_is_receipt": False, "current_topology_validation": False,
          "scientific_validation_established": False})
    write("construction_block.json", {**COMMON, "schema": "V6_TOPOLOGY_STABILITY_SUCCESSOR_CONSTRUCTION_BLOCK_V1",
          "status": "BLOCKED", "primary_blocker": BLOCK,
          "contract_sections": [6, 16, 17], "exact_missing_authority": "Unique mandatory active-client authorization rule and admissible complete independent attribution evidence, including treatment of unattributed active clients",
          "current_observation_limitations": ["raw socket table UNVERIFIED", "worker/binary/routes not freshly reobserved",
              "endpoint ownership/permissions not established by proc/net/unix", "complete unauthorized listener/client absence unverified"],
          "not_constructed": ["production_controller_successor_candidate.py", "production_provider_successor_candidate.py",
              "synthetic_e2e_qualification.py", "successor_installation_candidate.json", "successor_installation_plan.json"],
          "no_next_review_ready_claim": True,
          "next_legal_gate": "HUMAN_PI_DECIDE_EXACT_V6_SUCCESSOR_ACTIVE_CLIENT_AUTHORIZATION_RULE_AND_INDEPENDENT_EVIDENCE_REQUIREMENTS",
          "no_auto_promotion_or_fallback": True})
    write("construction_commands.json", COMMANDS)
    print(json.dumps({"status": "BLOCKED", "primary_blocker": BLOCK,
                      "entry_and_seals": "PASS", "predecessor_scientific_replay": len(replay),
                      "variants": variants, "time_utc": datetime.now(timezone.utc).isoformat()}))


if __name__ == "__main__":
    main()

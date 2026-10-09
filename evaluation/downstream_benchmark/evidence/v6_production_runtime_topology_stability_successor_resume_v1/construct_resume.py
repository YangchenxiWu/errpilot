"""Bounded candidate construction; no Docker, Git mutation or real output writes."""
from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OLD = ROOT / "evaluation/downstream_benchmark/evidence/v6_preparation_execution_production_runtime_installation_resume_v1"
CORRECTED = ROOT / "evaluation/downstream_benchmark/evidence/v6_production_runtime_image_identity_compatibility_bridge_v1"
PARTIAL = ROOT / "evaluation/downstream_benchmark/evidence/v6_production_runtime_topology_stability_successor_v1"
PREFIX = str(HERE.relative_to(ROOT)) + "/"
COMMON = {"candidate_only": True, "HUMAN_PI_ACCEPTED": "NO", "runtime_effective": "NO",
          "execute_now": False, "real_client_authorization_status": "BLOCKED_UNTIL_INDEPENDENT_LIVE_EVIDENCE"}


def write(name, value):
    path = HERE / name
    path.write_bytes((json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode())


def replace_functions(source, changes):
    tree = ast.parse(source)
    spans = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for child in node.body:
                key = node.name + "." + getattr(child, "name", "")
                if key in changes:
                    spans.append((min([child.lineno] + [x.lineno for x in child.decorator_list]), child.end_lineno,
                                  "\n".join("    " + s if s else "" for s in changes.pop(key).strip().splitlines())))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in changes:
            spans.append((node.lineno, node.end_lineno, changes.pop(node.name).strip()))
    assert not changes, changes
    lines = source.splitlines()
    for start, end, text in sorted(spans, reverse=True):
        lines[start - 1:end] = text.splitlines()
    return "\n".join(lines) + "\n"


def main():
    raw = (HERE / "raw_human_pi_request.txt").read_text()
    rules = {}
    for i in range(1, 17):
        start = raw.index(f"C{i}:\n") + len(f"C{i}:\n")
        end = raw.index(f"\nC{i+1}:\n", start) if i < 16 else raw.index("\nConstruct a deterministic", start)
        rules[f"C{i}"] = raw[start:end].strip()
    write("human_pi_decision.json", {**COMMON, "schema": "V6_CLIENT_POLICY_HUMAN_PI_DECISION_CAPTURE_V1",
        "owner": "HUMAN_PI", "decision": "ADOPT_V6_ACTIVE_CLIENT_AUTHORIZATION_POLICY_V1",
        "authority": "HUMAN_PI_DECIDE_V6_ACTIVE_BUILDKIT_CLIENT_AUTHORIZATION_V1",
        "authorization": "RESUME_BOUNDED_SUCCESSOR_CANDIDATE_CONSTRUCTION_ONLY", "exact_C1_C16": rules,
        "historical_execs": "ORIGIN_NOT_ESTABLISHED", "installation_authorized": False})
    serialization = json.loads((PARTIAL / "security_projection_contract_candidate.json").read_bytes())["canonical_serialization"]
    client = {**COMMON, "schema": "V6_ACTIVE_BUILDKIT_CLIENT_AUTHORIZATION_POLICY_V1_CANDIDATE",
        "C1_C16": rules, "canonical_serialization": serialization,
        "scope": "Every active session capable of accessing BuildKit control plane, including host, Engine exec/attach, container processes, Unix/TCP endpoints and unobserved access surfaces",
        "classification_order": ["Reject malformed/duplicate/missing evidence", "UNAUTHORIZED evidence rejects",
            "Unattributed or inadmissible evidence is UNKNOWN", "Independently established inaccessible sessions are UNABLE_TO_ACCESS_CONTROL_PLANE",
            "Independently established permitted principal and correlated access is AUTHORIZED",
            "Any UNKNOWN, incomplete census or unverifiable boundary blocks"],
        "admissible_kinds": ["AUTHENTICATED_HOST_LAUNCH_PROVENANCE", "CORRELATED_ENGINE_EXEC_METADATA",
            "INDEPENDENT_SOCKET_ACCESS_RESTRICTIONS", "VERIFIED_CONTAINER_PROCESS_ENDPOINT_RELATIONSHIP",
            "SEPARATELY_REVIEWED_EQUIVALENT"],
        "insufficient_alone": ["process name", "buildctl binary", "timestamps", "ExecID", "incomplete log absence", "matching network"],
        "correlation": "Every session ID occurs exactly once in observed census and exactly once in independently authenticated evidence; process/session/endpoint IDs, source hashes and stage acquisition agree",
        "completeness": "Exact observed session set, connected socket/process correlation and all independently accepted access surfaces; unobserved surfaces or incomplete coverage block",
        "production_evidence_origin": "Fixed separately reviewed installed observer source, exact SHA bound by new independently accepted effectivity and installation authority; no caller data or authorized Boolean",
        "production_live_observer": "Not installed or accepted; absent observer/authenticated provenance is BLOCKED",
        "synthetic": "Only candidate-owned exact path constructor reads synthetic evidence, explicitly labeled synthetic; never real authorization",
        "historical_clients": "ORIGIN_NOT_ESTABLISHED; no retrospective authorization, exoneration or malicious classification",
        "failure": "BLOCK before claim / one failure terminal if changed after claim; no build, no retry"}
    write("client_authorization_contract_candidate.json", client)
    write("raw_observation_contract_candidate.json", {**COMMON, "schema": "V6_FULL_RAW_OBSERVATION_CONTRACT_V2_CANDIDATE",
        "V1_unchanged": {"path": str((OLD / "topology_observation_contract.json").relative_to(ROOT)),
            "sha256": "8ee7bc08d55e8b0c9e628260fed4105e7cd122a9e123f527da37f4776fa96ce4"},
        "representation": "Exact UTF-8 source bytes in individually hashed entries, stage, method, source, timestamps, missing/unverifiable fields; no raw normalization",
        "required_sources": ["daemon", "proxy", "network", "worker", "images", "proxy_source", "proxy_policy",
            "unix_sockets", "routes", "socket_access", "listener_inventory", "client_census", "client_evidence"],
        "FULL_RAW_OBSERVATION": ["complete Docker inspect (including ExecIDs and order)", "complete Unix socket table Num/address/inode/record bytes",
            "process/worker/routes/native and daemon binary observations", "Engine/manifest/config/RootFS source bytes",
            "authenticated launch/process/endpoint relationships", "source timestamps/method/hash/missing/unverifiable"],
        "raw_observation_sha256": "SHA256 exact canonical raw source envelope, each source hash independently replayed",
        "source_completeness": "Authenticated observer acquisition covers full inspect and namespaces; unavailable sources block; historical sources cannot fill a live gap",
        "synthetic_raw": "Synthetic envelopes explicitly marked, no live proof"})
    mandatory = {
        "image_identity": ("Docker container/store/selected inspect + retained OCI index/manifest/config bytes", "verify_image_identity exact accepted independent content chain", "object"),
        "daemon_identity_state_argv": ("Full fresh inspect plus authenticated process observation", "exact Id/Pid/StartedAt/Running/Path/Args; no name attribution", "object"),
        "worker_platform": ("Fresh buildctl debug workers via independently accepted observer", "one exact worker; linux/amd64 required; full worker compared to accepted projection", "array"),
        "native_daemon_binaries": ("Fresh in-container sha256sum via independent observer", "exact frozen binary SHAs", "object"),
        "endpoint": ("Fresh Unix listener inventory and worker connection endpoint", "unix:///run/buildkit/buildkitd.sock; required listener path", "string"),
        "internal_daemon_network": ("Full container + internal network inspect", "only exact internal network, participants exactly daemon/proxy", "object"),
        "proxy_two_network_binding": ("Full proxy/network inspect", "two exact accepted networks, one internal and one external; no published ports", "object"),
        "proxy_image_source_policy": ("Independent image chain + exact fresh source/policy bytes", "exact config/source/policy SHAs and approved CONNECT origins only", "object"),
        "no_published_ports": ("Full daemon/proxy HostConfig and NetworkSettings", "empty PortBindings and no non-null published Ports", "object"),
        "no_external_default_route": ("Full fresh /proc/net/route, route6 and authenticated complete namespace route inventory", "no default/gateway/external route; IPv4 parsed, IPv6 absence independently verified", "array"),
        "unix_listeners": ("Full /proc/net/unix + independent complete listener namespace inventory", "exact path/Protocol/Type/St/Flags; unknown or duplicate listeners reject", "array"),
        "socket_access": ("Independent lstat/ACL/mount/user-namespace/access-control observations", "socket owner/group/mode/type and complete access restrictions; unverifiable blocks", "object"),
        "listener_inventory": ("Independent full Unix/TCP/UDP/network namespace inventory", "no external control listener; unknown surfaces block", "object"),
        "enforcement_identity": ("Exact frozen network enforcement source/config pins", "8801637324b2fa32124df8444e88f193a5be3f9c847904f2eebfb92197bc5c10", "string"),
    }
    fields = {k: {"authoritative_source": s, "exact_observation_method": method, "representation": typ,
                  "canonicalization": "adapter canonical JSON; original source bytes retained distinctly",
                  "verification_rule": method, "failure_or_unknown": "PRODUCTION_GATE=BLOCKED; independently unauthorized path=REJECT"}
              for k, (s, method, typ) in mandatory.items()}
    write("topology_stability_contract_candidate.json", {**COMMON,
        "schema": "V6_STABLE_SECURITY_PROJECTION_CONTRACT_V2_CANDIDATE", "fields": fields,
        "projection_schema": "V6_STABLE_SECURITY_PROJECTION_V2", "canonical_serialization": serialization,
        "accepted_live_projection": "NOT_CONSTRUCTED_NOT_ACCEPTED",
        "historical_drafting_input_sha256": "def7f4bd8569094ce608dd1ecc8b790c690780ec827dc43c11e2207284f5f21d",
        "identities_distinct": ["RAW_OBSERVATION_SHA256", "SECURITY_PROJECTION_SHA256", "CLIENT_AUTHORIZATION_EVIDENCE_SHA256", "EFFECTIVITY_PIN_SHA256"],
        "diagnostic_exclusions": ["ExecIDs/order", "socket Num/RefCount/Inode", "connected socket turnover", "observation timing"],
        "exclusion_precondition": "Complete current independently verified client census and endpoint access; connected rows still correlated, unknown listeners never dropped",
        "admission_order": list(range(1, 14)),
        "preclaim_order": ["canonical/event3", "independent successor effectivity pin", "installed source/contract pins", "exact work/population",
            "fresh full raw", "mandatory invariants", "projection", "accepted installed projection binding", "complete client authorization",
            "fresh access boundary", "RESTRICTED V2 receipt", "immutable raw association publication/readback", "original exclusive claim"],
        "provider": "Repeat all authority/security/client/access checks with independently acquired raw before native solve",
        "TOCTOU_limit": "Sequential checks do not prove continuous atomic security; fresh stage evidence mandatory; no TTL/bearer authority"})
    write("transient_diagnostics_contract_candidate.json", {**COMMON, "schema": "V6_TRANSIENT_DIAGNOSTICS_CONTRACT_V2_CANDIDATE",
        "preserved": ["ExecIDs/order", "socket inode/Num/RefCount", "connected row bytes", "timestamps", "diagnostic turnover"],
        "projection_exclusion": "Only non-listening rows with independently correlated authorized/inaccessible sessions; all original bytes remain in raw envelope",
        "unknown_is_not_transient_authorization": True})
    schema = copy.deepcopy(json.loads((PARTIAL / "receipt_schema_v2_candidate.json").read_bytes()))
    schema["title"] = "V6_RESTRICTED_BUILD_EGRESS_ENFORCEMENT_RECEIPT_V2_CANDIDATE"
    props = schema["properties"]
    props["runtime_authority"] = {"type": "boolean", "const": False}
    props["schema"]["const"] = schema["title"]
    props["client_authorization_verdict"] = {"type": "string", "const": "SYNTHETIC_CLIENT_AUTHORIZATION_PASS"}
    props["client_authorization_evidence_sha256"] = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
    props["client_authorization_policy_sha256"] = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
    schema["required"] = sorted(props)
    write("receipt_schema_v2_candidate.json", schema)
    write("receipt_authority_contract_v2_candidate.json", {**COMMON, "schema": "V6_PRODUCTION_RECEIPT_AUTHORITY_CONTRACT_V2_CANDIDATE",
        "receipt_schema": schema["title"], "future_production_schema": "V6_RESTRICTED_BUILD_EGRESS_ENFORCEMENT_RECEIPT_V2",
        "allowed_origins": ["files.pythonhosted.org:443", "pypi.org:443"], "required_receipt_fields": sorted(props),
        "canonical_serialization": serialization, "NONE": {"receipt": "PROHIBITED", "claim_receipt_sha256": None},
        "future_real_pin": "Exact separately Human-PI accepted successor effectivity bytes; not created by this package",
        "synthetic_receipt": "runtime_authority=false, candidate_only=true, SYNTHETIC_CLIENT_AUTHORIZATION_PASS; rejects in production",
        "future_production_receipt": "runtime_authority=true, candidate_only=false, REAL_CLIENT_AUTHORIZATION_PASS only after independent accepted live observer; separate schema, no V1/V2-candidate promotion",
        "security_binding": "Fresh accepted projection hash; exact entire frozen item, single base_attempt_id and all canonical/event/pin/source/contract/enforcement pins",
        "client_evidence_binding": "Receipt binds exact issuance client-evidence SHA; immutable preclaim association retains issuance raw plus freshly independent current raw; provider verifies both and acquires fresh client evidence",
        "raw_identity": "Distinct immutable sidecar; raw SHA never substituted for security projection SHA",
        "freshness": "Immediately before claim and provider solve; changes in security reject, authorized transient changes retain receipt bytes",
        "once_only": ["receipt byte SHA equals exclusive durable claim receipt SHA", "provider claim/receipt equality", "one attempt/one immutable terminal",
            "no retry", "no cross-attempt reuse", "no receipt after terminal"], "V1_live_daemon_topology_observation_sha256": "Frozen unchanged V1 meaning"})
    write("raw_sidecar_contract_candidate.json", {**COMMON, "schema": "V6_IMMUTABLE_RAW_ASSOCIATION_CONTRACT_V2_CANDIDATE",
        "graph": ["raw envelope", "security projection", "V2 receipt", "immutable evidence association", "exclusive durable claim"],
        "association_fields": ["schema", "stage", "attempt_id", "receipt_sha256", "security_projection_sha256", "raw_observation_sha256",
            "issuance_raw_observation_sha256", "client_authorization_evidence_sha256", "issuance_client_authorization_evidence_sha256"],
        "path": "<accepted root>/raw-evidence/<exact attempt>/preclaim or provider/<association SHA>.json",
        "ownership": "Same verified controller/provider authority/root and exact attempt; exclusive directories/files, no caller-selected path, no symlink",
        "durability": "fsynced exact raw bytes, source manifest, receipt and association; readback before original exclusive lock; claim input binding adds exact association SHA",
        "failure_before_claim": "No ledger lock/claim/terminal before full sidecar publication/readback; orphan sidecar blocks reentry pending separate adjudication, no attempt consumption",
        "provider": "Read back exact association/raw/receipt bound by durable claim; independently collect fresh raw, verify security/client/access, persist separate provider association before solve",
        "not_bearer_authority": True, "real_sidecar_writes_this_transaction": 0,
        "acyclic": "Association hashes raw and receipt, never claim; receipt hashes sources/contracts/projection/issuance evidence, never association"})
    write("receipt_binding_analysis.json", {**COMMON, "schema": "V6_RECEIPT_V2_BINDING_ANALYSIS_V1",
        "V1_contract_sha256": "030eebcdfe689cafdb7115a3ec26766c228dd01c4e1bb3ab33f4e9791e96f6d9",
        "V1_schema_sha256": "8a5077220001757af0b4885b9ba5ca23d9bc1adcc7acecb0dc9273647e0ca397",
        "partial_draft_reviewed": True, "separate_V2_required": True,
        "cycle_prevention": "Sources contain contract filenames, no receipt/installation/result hash; contract has no new source hash; receipt/association/claim point only backward",
        "raw_not_in_receipt_equality": True, "issuance_client_evidence_replayed_from_sidecar": True,
        "preclaim_revalidation": "Compare stable binding, preserve original receipt and issuance raw; fresh raw may differ only after mandatory security and C1-C16 PASS"})


if __name__ == "__main__":
    main()

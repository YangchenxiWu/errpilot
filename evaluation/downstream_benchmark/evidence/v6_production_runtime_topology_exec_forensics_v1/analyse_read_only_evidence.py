"""Offline forensic comparisons. Parses sources with AST; executes no provider code."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CORRECTION = HERE.parent / "v6_production_runtime_image_identity_compatibility_bridge_v1"
RESUME = HERE.parent / "v6_preparation_execution_production_runtime_installation_resume_v1"
PROVISION = Path("/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1/qualification/production_runtime_topology_provisioning_v1")
A = "3cb528138771884a52fa9bd01e5d5458ca4ffbd41c949282328d08b2dc0286bf"
B = "fe36c6b84e7ab5a74fbfe441848c95fa4fab65fe5db8cfba3477d0fdb0960e73"
SOURCES = {}
MISSING = {"FIELD_NOT_EXPOSED": True}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    raw = path.read_bytes()
    SOURCES[str(path)] = {"sha256": sha(raw), "size_bytes": len(raw)}
    return raw


def load(path):
    return json.loads(read(path))


def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def diff(left, right, path=""):
    if type(left) is not type(right):
        return [{"field": path, "expected": left, "observed": right}]
    if isinstance(left, dict):
        result = []
        for key in sorted(left.keys() | right.keys()):
            result += diff(left.get(key, MISSING), right.get(key, MISSING), path + "/" + key)
        return result
    return [{"field": path, "expected": left, "observed": right}] if left != right else []


def field(value, path):
    for key in path.split("/"):
        if not isinstance(value, dict) or key not in value:
            return MISSING
        value = value[key]
    return value


def nodes(source):
    result = {}
    def visit(body, prefix=""):
        for node in body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                key = prefix + node.name
                result[key] = node
                visit(node.body, key + ".")
    visit(ast.parse(source).body)
    return result


def main():
    accepted = load(PROVISION / "live_topology_observation.json")
    corrected = load(CORRECTION / "corrected_topology_observation.json")
    contract = load(RESUME / "topology_observation_contract.json")
    original_raw = read(PROVISION / "raw/093_fresh_daemon_inspect.stdout")
    correction_raw = read(CORRECTION / "live_observation/run_2/raw/001.stdout")
    original = json.loads(original_raw)[0]
    correction = json.loads(correction_raw)[0]
    observations = {name: load(HERE / ("exec_inspect_observations_" + name + ".json"))
                    for name in ("before", "before_authorized", "detail", "security", "after")
                    if (HERE / ("exec_inspect_observations_" + name + ".json")).exists()}
    phase = "after" if "after" in observations else "security"
    current_obs = observations[phase]
    current_cmd = current_obs["full_daemon_cli_inspect"]["command"]
    current_raw = read(HERE / current_cmd["stdout_path"])
    current = json.loads(current_raw)[0]
    raw_copies = {"raw_original_daemon_inspect.stdout": original_raw,
                  "raw_correction_daemon_inspect.stdout": correction_raw,
                  "raw_original_socket_table.txt": read(PROVISION / "raw/106_daemon_unix_sockets.stdout"),
                  "raw_correction_socket_table.txt": read(CORRECTION / "live_observation/run_2/raw/008.stdout")}
    # Bind socket copies to the controlling full observations, without reserialization.
    assert raw_copies["raw_original_socket_table.txt"].decode() == accepted["daemon_socket_observation"]
    assert raw_copies["raw_correction_socket_table.txt"].decode() == corrected["daemon_socket_observation"]
    for name, raw in raw_copies.items():
        (HERE / name).write_bytes(raw)
    config_fields = ["Config", "Image", "ImageManifestDescriptor", "HostConfig", "NetworkSettings",
                     "Path", "Args", "Mounts", "AppArmorProfile", "ProcessLabel", "MountLabel"]
    requested = ["Id", "State/StartedAt", "State/Pid", "State/Running", "Config/Image", "Image",
                 "ImageManifestDescriptor", "HostConfig/NetworkMode", "HostConfig/Dns", "HostConfig/PortBindings",
                 "NetworkSettings/Networks", "Path", "Args", "Mounts", "ExecIDs"]
    original_proxy_raw = read(PROVISION / "raw/094_fresh_proxy_inspect.stdout")
    correction_proxy_raw = read(CORRECTION / "live_observation/run_2/raw/002.stdout")
    current_proxy_cmd = current_obs["full_proxy_cli_inspect"]["command"]
    current_proxy_raw = read(HERE / current_proxy_cmd["stdout_path"])
    proxy_sequence = [json.loads(raw)[0] for raw in (original_proxy_raw, correction_proxy_raw, current_proxy_raw)]
    comparisons = []
    for label, left, right, lr, rr in [
        ("original_to_correction_daemon", original, correction, original_raw, correction_raw),
        ("correction_to_current_daemon", correction, current, correction_raw, current_raw),
        ("original_to_current_daemon", original, current, original_raw, current_raw),
        ("original_to_correction_proxy", proxy_sequence[0], proxy_sequence[1], original_proxy_raw, correction_proxy_raw),
        ("correction_to_current_proxy", proxy_sequence[1], proxy_sequence[2], correction_proxy_raw, current_proxy_raw),
    ]:
        critical = [{"field": f, "left": field(left, f), "right": field(right, f),
                     "equality": "UNKNOWN" if MISSING in (field(left, f), field(right, f)) else field(left, f) == field(right, f)}
                    for f in config_fields]
        delta = diff(left, right)
        for row in delta:
            top = row["field"].split("/")[1]
            row["category"] = ("A_SECURITY_CRITICAL_CONFIGURATION" if top in config_fields else
                               "B_LIFECYCLE_INSTANCE_IDENTITY" if top in ("Id", "Name", "Created", "State") else
                               "C_DIAGNOSTIC_RUNTIME_BOOKKEEPING" if top in ("ExecIDs", "RestartCount", "LogPath") else
                               "D_UNKNOWN_OR_UNOBSERVABLE")
            row["provenance"] = {"left_raw_sha256": sha(lr), "right_raw_sha256": sha(rr)}
        sec = "UNKNOWN" if any(x["equality"] == "UNKNOWN" for x in critical) else all(x["equality"] for x in critical)
        comparisons.append({"comparison": label, "FULL_DOCKER_INSPECT_BYTE_EQUALITY": lr == rr,
                            "full_parsed_field_equality": not delta, "SECURITY_CRITICAL_FIELD_EQUALITY": sec,
                            "SECURITY_CONFIG_DRIFT": "UNKNOWN" if sec == "UNKNOWN" else "NO" if sec else "YES",
                            "security_field_checks": critical, "differences": delta,
                            "requested_field_checks": [{"field": f, "left": field(left, f), "right": field(right, f),
                                "equal": "UNKNOWN" if MISSING in (field(left, f), field(right, f)) else field(left, f) == field(right, f)}
                                for f in requested], "left_raw_sha256": sha(lr), "right_raw_sha256": sha(rr)})
    intra_phase = []
    for name, obs in observations.items():
        if "full_daemon_cli_inspect" in obs:
            observed_inventory = load(HERE / ("raw_docker_inventory_" + name + ".json"))
            api_daemon = next(x["parsed"] for x in observed_inventory["containers"] if x["parsed"]["Id"] == original["Id"])
            intra_phase.append({"phase": name, "API_to_CLI_full_field_differences": diff(api_daemon, obs["full_daemon_cli_inspect"]["parsed"][0]),
                "interpretation": "Separate read timestamps and exact array ordering retained; any ExecID list ordering drift is diagnostic and is not silently sorted away."})
    write("docker_inspect_field_diff.json", {"schema": "V6_TOPOLOGY_FULL_INSPECT_FORENSICS_V1", "current_phase": phase,
        "comparisons": comparisons, "SECURITY_CONFIG_DRIFT": "NO" if all(x["SECURITY_CONFIG_DRIFT"] == "NO" for x in comparisons) else "UNKNOWN",
        "scope": "Complete preserved daemon/proxy inspect configuration fields; does not prove current in-container route, socket, worker or binary bytes.",
        "ExecIDs_not_excluded": True, "strict_topology_gate_replaced": False, "intra_phase_API_to_CLI_comparisons": intra_phase})

    def sockets(text):
        result = []
        for raw in text.splitlines()[1:]:
            parts = raw.split(maxsplit=7)
            row = dict(zip(["Num", "RefCount", "Protocol", "Flags", "Type", "St", "Inode", "Path"], parts))
            row.setdefault("Path", "")
            row["raw_line"] = raw
            row["record_kind_inference"] = "LISTENER" if row["Flags"] == "00010000" and row["St"] == "01" else "CONNECTED_RUNTIME_RECORD" if row["St"] == "03" else "UNKNOWN"
            result.append(row)
        return result
    osockets, csockets = sockets(accepted["daemon_socket_observation"]), sockets(corrected["daemon_socket_observation"])
    old_by_inode = {x["Inode"]: x for x in osockets}
    changes = []
    for row in csockets:
        if row["Inode"] not in old_by_inode or row != old_by_inode[row["Inode"]]:
            changes.append({"record": row, "change": "ADDED" if row["Inode"] not in old_by_inode else "CHANGED",
                "classification": "UNRESOLVED", "evidence": "State 03, stream type 0001, zero listen flags identify connected bookkeeping, not a new listener. Actual lifetime, client authorization, PID and initiating host command are not established.",
                "security_relevant_config_change_observed": False, "measured_transient_lifetime": "UNKNOWN",
                "exec_inode_causal_binding": "NOT_ESTABLISHED", "provenance": [str(PROVISION / "raw/106_daemon_unix_sockets.stdout"), str(CORRECTION / "live_observation/run_2/raw/008.stdout")]})
    for row in osockets:
        if row["Inode"] not in {x["Inode"] for x in csockets}:
            changes.append({"record": row, "change": "REMOVED", "classification": "UNRESOLVED"})
    listener = lambda rows: [x for x in rows if x["record_kind_inference"] == "LISTENER"]
    summary = lambda rows: {"records": len(rows), "path_bearing": sum(bool(x["Path"]) for x in rows),
                           "unnamed": sum(not x["Path"] for x in rows), "listeners": len(listener(rows))}
    write("socket_diff_analysis.json", {"schema": "V6_RAW_SOCKET_FORENSICS_V1", "original_records": osockets,
        "correction_records": csockets, "original_counts": summary(osockets), "correction_counts": summary(csockets),
        "FULL_RAW_TEXT_EQUALITY": accepted["daemon_socket_observation"] == corrected["daemon_socket_observation"],
        "full_raw_text_sha256": {"original": sha(accepted["daemon_socket_observation"].encode()), "correction": sha(corrected["daemon_socket_observation"].encode())},
        "listener_record_exact_equality": listener(osockets) == listener(csockets), "differences": changes,
        "retained_inodes": sorted(set(old_by_inode) & {x["Inode"] for x in csockets}),
        "added_inodes": [x["record"]["Inode"] for x in changes if x["change"] == "ADDED"],
        "inode_renumbering_observed": False, "current_socket_table": "CURRENT_SOCKET_TABLE_NOT_REOBSERVED",
        "interpretation": "Two records were added; the four original records, including both listeners, remain exact. No replacement of inode 340 or 344 is shown. Socket lifetimes and exec-to-inode causality remain unresolved.",
        "kernel_field_semantics": "Flags/state interpretation is an analyst inference from the preserved Linux table; no new kernel/source/network query was made."})

    historical_commands = []
    log_sources = sorted(set(list(PROVISION.rglob("*commands*.json")) + list(CORRECTION.rglob("*commands*.json"))))
    def walk(value, source, pointer=""):
        if isinstance(value, dict):
            if isinstance(value.get("argv"), list):
                historical_commands.append({"source": str(source), "pointer": pointer,
                    **{k: v for k, v in value.items() if k in ("argv", "name", "started_at", "finished_at", "exit_code", "returncode", "stdout_path", "stderr_path", "stdout_sha256", "stderr_sha256")}})
            for key, val in value.items():
                walk(val, source, pointer + "/" + key)
        elif isinstance(value, list):
            for index, val in enumerate(value):
                walk(val, source, pointer + "/" + str(index))
    for path in log_sources:
        walk(load(path), path)
    candidate_commands = [x for x in historical_commands if x["argv"][:2] == ["docker", "buildx"] or "dial-stdio" in x["argv"]]
    write("raw_historical_command_inventory.json", {"all_recorded_argv": historical_commands,
          "potential_relevance_only": candidate_commands, "not_executed_in_this_transaction": True})
    history = load(CORRECTION / "docker_exec_drift_details.json")
    exec_ids = sorted({k for obs in observations.values() for k in obs if len(k) == 64})
    attribution = []
    for eid in exec_ids:
        live = [{"phase": name, **obs[eid]} for name, obs in observations.items() if eid in obs]
        available = [x for x in live if x["available"]]
        latest = available[-1]["parsed"] if available else None
        hist = next((x["response"] for x in history["metadata"] if x["response"]["ID"] == eid), None)
        top_evidence = [{"phase": name, "docker_top": obs["docker_top"], "engine_top": obs["engine_top"]}
                        for name, obs in observations.items() if obs.get("docker_top", {}).get("command", {}).get("returncode") == 0]
        temporal = ("PID 807 has container-side ps start time 2026-10-07 19:19:10, the same one-second bucket as the recorded builder bootstrap (19:19:10.457129-19:19:10.735332 UTC). This is TEMPORAL_CORRELATION only; no exec-ID-to-host-command audit binding exists."
                    if eid == A else "No retained creation/start timestamp uniquely binds this exact ExecID to a host command. Historical Exec B inspect exposes no creation or start time. Current 404 does not expose its final exit status or termination cause.")
        attribution.append({"exec_id": eid, "historical_metadata": hist, "live_observations": live,
            "OBSERVED_EXECUTABLE": (latest or hist or {}).get("ProcessConfig", MISSING),
            "OBSERVED_CONTAINER_AND_PROCESS": {k: (latest or hist or {}).get(k, MISSING) for k in ("ContainerID", "Pid", "Running", "ExitCode")},
            "live_metadata_status": "OBSERVED_DURING_TRANSACTION" if latest else "UNKNOWN",
            "observed_process_metadata_provenance": "Latest successful exact GET during transaction" if latest else "Predecessor metadata only; current exact GET unavailable",
            "last_successful_metadata": latest,
            "last_inspect_metadata": live[-1]["parsed"], "last_inspect_timestamp": live[-1]["command"]["started_at"],
            "last_inspect_http_status": live[-1]["http_status"],
            "final_snapshot_membership": eid in current["ExecIDs"],
            "final_snapshot_exact_inspect_metadata": observations.get("after", {}).get(eid, {}).get("parsed"),
            "final_snapshot_metadata_status": "OBSERVED" if observations.get("after", {}).get(eid, {}).get("available") else "UNKNOWN_OR_NOT_QUERIED_AT_FINAL_SAMPLE",
            "TEMPORAL_CORRELATION": temporal,
            "ATTRIBUTED_INITIATING_COMMAND": None, "UNRESOLVED_ORIGIN": "ORIGIN_NOT_ESTABLISHED",
            "host_initiator_inferred_from_argv": False, "creation_timestamp": "NOT_EXPOSED_BY_EXEC_INSPECT",
            "top_crosscheck": top_evidence, "causal_evidence_required": "A retained Engine audit event, unique host process trace, or client log binding the exact ExecID to its initiating invocation. ps timestamps and argv alone do not establish that binding."})
    inventories = {name: load(HERE / ("raw_docker_inventory_" + name + ".json")) for name in ("before_authorized", "detail", "security", "after") if (HERE / ("raw_docker_inventory_" + name + ".json")).exists()}
    timeline = [{"phase": name, "daemon_exec_ids": next(x["parsed"]["ExecIDs"] for x in inv["containers"] if x["parsed"]["Id"] == original["Id"]),
                 "command": inv["containers_list"]["command"]} for name, inv in inventories.items()]
    write("exec_inspect_observations.json", {"exact_targets": [A, B], "phases": observations,
        "historical_original_exec_ids": original["ExecIDs"], "historical_correction_exec_ids": correction["ExecIDs"],
        "current_exec_ids": current["ExecIDs"], "live_exec_ids_timeline": timeline,
        "initial_sandbox_failure_preserved": True, "current_socket_table": "CURRENT_SOCKET_TABLE_NOT_REOBSERVED"})
    write("exec_process_attribution.json", {"schema": "V6_EXEC_PROCESS_ATTRIBUTION_V1", "execs": attribution,
        "source_command_logs": [str(x) for x in log_sources], "historical_recorded_command_count": len(historical_commands),
        "unique_initiating_command_attribution_count": 0, "daemon_logs": observations["before_authorized"]["daemon_logs"],
        "daemon_log_assessment": "Startup-only daemon logs show worker and Unix server startup, with no ExecID or initiating host PID/command. The worker host-network warning describes the worker mode at startup, not a new Docker HostConfig.NetworkMode change; container external attachment and route invariants remain independently necessary.",
        "correction_buildx_or_explicit_dial_stdio_commands": [x for x in candidate_commands if str(CORRECTION) in x["source"]],
        "absence_of_logged_command_does_not_prove_absence_of_concurrent_client": True})

    inv = inventories[phase]
    networks = {x["parsed"]["Name"]: x["parsed"] for x in inv["network_details"]}
    d, p = current, proxy_sequence[2]
    internal_name = accepted["internal_builder_network"]["Name"]
    internal = networks[internal_name]
    proxy_source = ROOT / "evaluation/downstream_benchmark/evidence/v6_native_buildkit_client_compatibility_bridge_v1/proxy.py"
    source_sha = sha(read(proxy_source))
    categories = {
        "schema": "STABLE_SECURITY_INVARIANT", "BuildKit_runtime_reference": "STABLE_SECURITY_INVARIANT",
        "daemon_endpoint": "STABLE_SECURITY_INVARIANT", "daemon_instance_identity": "INSTANCE_IDENTITY",
        "worker_identity": "INSTANCE_IDENTITY", "internal_builder_network": "STABLE_SECURITY_INVARIANT",
        "proxy_instance_identity": "INSTANCE_IDENTITY", "proxy_network_binding": "STABLE_SECURITY_INVARIANT",
        "proxy_policy_sha256": "STABLE_SECURITY_INVARIANT", "enforcement_identity": "STABLE_SECURITY_INVARIANT",
        "native_binary_sha256": "STABLE_SECURITY_INVARIANT", "daemon_binary_sha256": "STABLE_SECURITY_INVARIANT",
        "daemon_image_config_digest": "STABLE_SECURITY_INVARIANT", "daemon_network_attachments": "STABLE_SECURITY_INVARIANT",
        "daemon_argv": "STABLE_SECURITY_INVARIANT", "daemon_dns": "STABLE_SECURITY_INVARIANT",
        "daemon_port_bindings": "STABLE_SECURITY_INVARIANT", "daemon_routes": "STABLE_SECURITY_INVARIANT",
        "daemon_socket_observation": "TRANSIENT_DIAGNOSTIC", "proxy_image_config_digest": "STABLE_SECURITY_INVARIANT",
        "proxy_argv": "STABLE_SECURITY_INVARIANT", "proxy_source_sha256": "STABLE_SECURITY_INVARIANT",
        "proxy_policy_bytes_sha256": "STABLE_SECURITY_INVARIANT"}
    invariants = [{"field": f, "classification": categories[f], "frozen_exact_value": accepted[f],
                   "original_to_correction_equal": accepted[f] == corrected[f],
                   "provenance": [str(PROVISION / "live_topology_observation.json"), str(CORRECTION / "corrected_topology_observation.json")],
                   "current_full_field_status": "NOT_REOBSERVED_IN_THIS_TRANSACTION"}
                  for f in contract["required_fields"]]
    checks = {
        "daemon_exact_image_reference": d["Config"]["Image"] == accepted["BuildKit_runtime_reference"],
        "daemon_dedicated_container_identity": d["Id"] == accepted["daemon_instance_identity"]["container_id"],
        "daemon_started_at_pid_running": {k: d["State"][k] for k in ("Pid", "StartedAt")} == {k: accepted["daemon_instance_identity"][k] for k in ("Pid", "StartedAt")} and d["State"]["Running"],
        "daemon_only_internal_network": set(d["NetworkSettings"]["Networks"]) == {internal_name},
        "daemon_network_mode_exact": d["HostConfig"]["NetworkMode"] == original["HostConfig"]["NetworkMode"],
        "internal_network_Internal_true": internal["Internal"] is True,
        "internal_network_exact_identity": internal["Id"] == accepted["internal_builder_network"]["Id"],
        "internal_network_exact_two_participants": set(internal["Containers"]) == {d["Id"], p["Id"]},
        "proxy_exactly_dual_homed": p["NetworkSettings"]["Networks"] == accepted["proxy_network_binding"] and len(p["NetworkSettings"]["Networks"]) == 2,
        "external_network_only_proxy": all(set(n["Containers"]) == {p["Id"]} for name, n in networks.items() if name in p["NetworkSettings"]["Networks"] and name != internal_name),
        "no_published_ports_daemon_proxy": d["HostConfig"]["PortBindings"] == {} and p["HostConfig"]["PortBindings"] == {} and not d["NetworkSettings"]["Ports"] and not p["NetworkSettings"]["Ports"],
        "no_daemon_gateway_in_inspect": d["NetworkSettings"]["Networks"][internal_name]["Gateway"] == "",
        "daemon_dns_exact": d["HostConfig"]["Dns"] == accepted["daemon_dns"],
        "daemon_argv_exact": {"Path": d["Path"], "Args": d["Args"]} == accepted["daemon_argv"],
        "proxy_argv_exact": {"Path": p["Path"], "Args": p["Args"]} == accepted["proxy_argv"],
        "proxy_host_bind_source_sha_exact": source_sha == accepted["proxy_source_sha256"],
        "proxy_source_mount_exact_read_only": any(x.get("Source") == str(proxy_source) and x["Destination"] == "/qualification_proxy.py" and x["RW"] is False for x in p["Mounts"]),
        "current_daemon_in_container_no_default_route": "UNKNOWN",
        "current_worker_identity_and_platform": "NOT_REOBSERVED; startup logs agree with accepted worker, but are historical startup evidence",
        "current_exact_native_and_daemon_binary_bytes": "NOT_REOBSERVED",
        "current_unix_listener_endpoint": "CURRENT_SOCKET_TABLE_NOT_REOBSERVED",
        "current_full_topology_exact_sha": "NOT_REOBSERVED; historical corrected raw topology already differs"}
    write("topology_security_invariants.json", {"schema": "V6_TOPOLOGY_SECURITY_INVARIANT_ASSESSMENT_V1",
        "contract_path": str(RESUME / "topology_observation_contract.json"), "contract_sha256": sha(read(RESUME / "topology_observation_contract.json")),
        "contract_authoritative_unchanged": True, "field_assessments": invariants, "current_inspect_checks": checks,
        "worker_split": {"worker_ID": "INSTANCE_IDENTITY", "worker_platform_and_executor_constraints": "STABLE_SECURITY_INVARIANT"},
        "socket_split": {"entire_raw_table": "TRANSIENT_DIAGNOSTIC", "approved_endpoint_listener_path_type_state_flags_owner_and_no_unapproved_listener": "STABLE_SECURITY_INVARIANT", "two_added_record_lifetimes_and_clients": "UNKNOWN"},
        "network_split": {"Internal_flag_membership_dual_homing_no_ports_route_DNS": "STABLE_SECURITY_INVARIANT", "network_EndpointID_IP_MAC_identity": "INSTANCE_IDENTITY; frozen V1 still requires exact bytes"},
        "receipt_freshness": {"classification": "STABLE_SECURITY_INVARIANT", "requirements": contract["freshness"],
            "bind": "Exact canonical/event3/effectivity/source/contract/enforcement/work-item/network-mode/origins and live topology SHA in receipt; independent provider prebuild reobservation, before claim and build.",
            "V1_exact_byte_gate_retained": True, "semantic_freshness_not_substituted": True},
        "essential_checks_may_not_be_removed": True, "new_V2_contract_constructed": False})

    original_source = read(RESUME / "production_provider_candidate.py").decode()
    corrected_source = read(CORRECTION / "corrected_production_provider_candidate.py").decode()
    on, cn = nodes(original_source), nodes(corrected_source)
    retained = ["Authority.__init__", "Authority.synthetic", "Authority.refresh", "receipt_value", "verify_receipt", "verify_claim", "ReceiptBoundLedger.claim", "ProductionProvider.execute", "ProductionProvider.execute_synthetic"]
    ast_checks = {n: {"equal": ast.dump(on[n], include_attributes=False) == ast.dump(cn[n], include_attributes=False),
                      "original_ast_sha256": sha(ast.dump(on[n], include_attributes=False).encode()),
                      "corrected_ast_sha256": sha(ast.dump(cn[n], include_attributes=False).encode()),
                      "corrected_lines": [cn[n].lineno, cn[n].end_lineno]} for n in retained}
    qualification = load(CORRECTION / "synthetic_qualification_results.json")
    rejection = load(CORRECTION / "rejection_matrix.json")
    seam = read(CORRECTION / "candidate_only_identity_observer.py").decode()
    qual_source = read(CORRECTION / "qualify_bridge_candidate.py").decode()
    delta = load(CORRECTION / "source_semantic_delta.json")
    direct_functions = sorted({node.func.attr for source in (seam, qual_source) for node in ast.walk(ast.parse(source))
                               if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "p"})
    guards = [{"name": name, "lines": [cn[name].lineno, cn[name].end_lineno],
               "exact_source": ast.get_source_segment(corrected_source, cn[name]), "AST_unchanged": ast_checks[name]["equal"]}
              for name in ("Authority.__init__", "Authority.synthetic")]
    coverage = [
        {"path": "verify_image_identity / image_identity_pins / normalize_topology", "evidence": "3 positive pure checks and 52 retained rejection checks; exact correction seal verified", "coverage": "PURE_SCOPE_QUALIFIED_HISTORICALLY", "gap": "Does not instantiate receipt authority or traverse controller/provider claim/build/terminal path"},
        {"path": "observe_image_config / retained_image_content / parse_workers", "evidence": "Historical live correction collector calls; current transaction reads code only", "coverage": "HISTORICAL_LIVE_COMPONENT_OBSERVATION_ONLY", "gap": "Not independently qualified by the three pure positives; real-observer orchestration and corrected receipt binding remain E2E gaps"},
        {"path": "Authority.synthetic exact source/root/fixture pins", "evidence": "Guard rejection retained; AST unchanged", "coverage": "REJECTION_COVERED", "gap": "Corrected candidate lives at a different path from the exact permitted RESUME/production_provider_candidate.py"},
        {"path": "Authority.observe synthetic to corrected normalization", "evidence": "Full corrected Authority was not instantiated", "coverage": "NOT_RUN", "gap": "No corrected-byte full synthetic observation/authority E2E"},
        {"path": "receipt construction, serialization, stale topology/enforcement rejection", "evidence": "Receipt AST independently equal; pure wrong-topology/enforcement comparison only", "coverage": "UNCHANGED_SOURCE_SEMANTICS_ONLY", "gap": "No issued receipt binds corrected provider source SHA and full freshness path"},
        {"path": "controller preclaim -> receipt-bound claim -> provider -> durable terminal / A-through-X", "evidence": "Controller source pinned unchanged; provider and ledger AST unchanged", "coverage": "NOT_RUN_FOR_CORRECTED_BYTES", "gap": "Historical original E2E is predecessor evidence only; corrected provider integration is unqualified"},
        {"path": "real production guards/live observer/real ledger", "evidence": "Production targets absent, full observer prohibited here", "coverage": "NOT_RUN_AND_NOT_AUTHORIZED", "gap": "No production installation, real receipt/claim/terminal or scientific validation"}]
    proposal = {
        "status": "DESIGN_OPTION_ONLY_NOT_CONSTRUCTED_NOT_EXECUTED",
        "exact_byte_candidate_design": "A separately versioned, hermetic filesystem namespace containing a full isolated checkout. Materialize exact corrected SHA 82561a9... at the guard's actual permitted repo-relative RESUME/production_provider_candidate.py inside that namespace, never replacing host accepted evidence. Resolve a.ROOT naturally from the isolated checkout and isolate the hard-coded benchmark output root at the OS filesystem boundary. Keep production target/pin paths absent and deny host Docker/network access. Invoke the unchanged guard normally with correctly hash-bound synthetic-only fixtures and IDs. No __file__ rebinding, object construction bypass, monkeypatch or production guard relaxation. This is an untested feasibility proposal requiring explicit Human-PI approval of placement and isolation.",
        "required_tests": "Re-run complete original A-through-X synthetic controller/provider E2E with receipt SHA bound to exact corrected provider bytes, stale topology between preclaim/build, wrong image/config/platform/enforcement, wrong root/namespace and production entry rejections, interruption/duplicate claim/terminal checks; verify real host ledger and frozen sources preserved.",
        "remaining_real_observer_gap": "Synthetic Authority.observe does not call the real observe_image_config collector. A separately authorized qualification design must cover recorded Engine/image-content failures and exact corrected observer orchestration without a production connection; pure content verification is insufficient for full real-observer coverage.",
        "alternative_successor_guard_design": "If the isolated exact-path design cannot satisfy all unchanged guards, request a new explicitly versioned qualification/source-location contract and candidate guard before construction. Bind new SHA separately; do not call the changed candidate exact original corrected-byte E2E.",
        "Human_PI_decisions_required": ["Authorize bounded isolated synthetic E2E construction/execution and namespace placement with no host evidence replacement", "Accept the isolation and exact-source fixture hash graph independently", "If a guard change is needed, authorize and review a versioned successor guard contract; frozen host guards remain unchanged", "Independently decide topology V1 retention or future semantic contract; E2E alone grants no installation/effectivity"]}
    write("synthetic_e2e_coverage_gap.json", {"schema": "V6_SYNTHETIC_E2E_COVERAGE_GAP_V1", "COVERAGE_GAP_MATRIX": coverage,
        "historical_positive_checks": qualification["tests"], "historical_rejection_count": len(rejection["checks"]),
        "all_historical_rejections_PASS_REJECTED": all(x["status"] == "PASS_REJECTED" for x in rejection["checks"].values()),
        "full_corrected_E2E": "NOT_RUN", "current_E2E_execution": "NOT_AUTHORIZED_NOT_RUN",
        "direct_p_functions_found_in_pure_test_sources": direct_functions, "exact_source_location_guards": guards,
        "independent_AST_checks": ast_checks, "retained_semantic_delta_is_predecessor": delta,
        "unchanged_AST_does_not_establish_corrected_byte_E2E": True, "future_versioned_qualification_design": proposal,
        "sources_imported_or_executed": False})
    write("raw_source_hashes.json", {"schema": "V6_FORENSIC_READ_SOURCE_HASHES_V1", "files": SOURCES})
    print(json.dumps({"full_inspect_drift": [x["differences"] for x in comparisons],
          "security_config_drift": "NO" if all(x["SECURITY_CONFIG_DRIFT"] == "NO" for x in comparisons) else "UNKNOWN",
          "socket_counts": [summary(osockets), summary(csockets)], "exec_origins_attributed": 0,
          "current_exec_ids": current["ExecIDs"], "coverage_AST_equal": all(x["equal"] for x in ast_checks.values())}))


if __name__ == "__main__":
    main()

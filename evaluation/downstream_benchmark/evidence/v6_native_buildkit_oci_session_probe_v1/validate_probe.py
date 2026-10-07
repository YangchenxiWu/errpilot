"""Local evidence verification, required checks, and acyclic artifact sealing."""
from __future__ import annotations

import ast
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("native_probe_validation_subject", Path(__file__).with_name("native_probe.py"))
n = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n)


def evidence_checks():
    checks = {}
    def check(name, condition):
        checks[name] = bool(condition)
        n.require(condition, name)
    entry, final = n.load("entry_verification.json"), n.load("final_verification.json")
    check("all_215_prior_repo_bytes_exact", len(entry["prior_file_hashes"]) == 215 and all(
        n.digest(n.ROOT / rel) == expected for rel, expected in entry["prior_file_hashes"].items()))
    check("canonical_bytes_exact", n.digest(n.ROOT / "evaluation/downstream_benchmark/v6_current_state.json") == n.h.CANONICAL)
    check("index_bytes_exact", n.digest(n.ROOT / ".git/index") == entry["index_sha256"] == final["index_sha256"])
    check("HEAD_live_origin_at_entry_and_final", all(row["head"] == row["live_origin_main"] == n.h.HEAD and row["branch"] == "main" for row in [entry, final]))
    check("population_and_blockers_preserved", all(entry[k] == final[k] for k in ["total", "restricted", "network_none", "population_sha256", "blocker_plans", "attempt_state"]))
    check("prior_external_bytes_and_path_set_exact", n.inventory(n.EXTERNAL, exclude=n.Q) == n.load("prior_external_inventory.json"))
    lineage = n.load("lineage.json")
    check("actual_prior_OCI_layout_exact", n.verify_layout(Path(lineage["layout_path"]), lineage["layout_inventory"]) == lineage["layout_inventory"])
    check("historical_alias_exception_preserved", lineage["historical_deviation"]["fallback_condition_classification_deviation"]["contract_compliance_exception"] is True
          and lineage["historical_deviation_is_authority"] is False)
    runtime = n.load("runtime_identity.json")
    check("runtime_exact_three_identities", runtime["engine_store_id"] == n.IMAGE.split("@")[1]
          and runtime["platform_manifest_id"] == "sha256:98cc6a3fc46220d00f8224ae483f3274fc874e9be8d7dd1e2e2c5481209228b5"
          and runtime["verified_config_digest"] == "sha256:27933730df224df80c41f4e5a9b33fa78831a79fd31903df3bb7deb49363422f")
    builder, native = n.load("builder_identity.json"), n.load("native_client_identity.json")
    connection, copied = n.load("daemon_connection.json"), n.load("copied_input_manifest.json")
    command = n.load("buildctl_command.json")
    owned = n.load("owned_objects.json")
    check("same_daemon_connection_exact_worker", connection["status"] == "PASS"
          and connection["same_container_id"] == owned["container_id"] == builder["container_id_operational_only"] == native["inside_same_container"]
          and connection["expected_worker_id_from_daemon_logs"] in connection["worker_stdout"]
          and connection["linux_amd64_available"])
    check("endpoint_actual_unique_unix", len(set(connection["observed_socket_paths"])) == 1
          and connection["observed_server_endpoints"] == connection["observed_socket_paths"]
          and connection["endpoint_selected"] == "unix://" + connection["observed_socket_paths"][0])
    check("native_client_same_runtime_version", native["version"].split()[1:] == builder["BuildKit_version"].split()[1:])
    n.validate_command(command["argv_inside_container"], connection["endpoint_selected"])
    check("exact_native_command_same_container", command["host_argv"] == ["docker", "exec", owned["container_id"]] + command["argv_inside_container"])
    check("copied_layout_and_one_Dockerfile_exact", copied["status"] == "PASS" and copied["OCI_file_count"] == 13 and len(copied["files"]) == 14
          and copied["context_files"] == ["Dockerfile"] and n.digest(n.Q / "context/Dockerfile") == n.sha(n.DOCKERFILE.encode()))
    expected_copied = {n.CPATH + "/oci/" + rel: item["sha256"] for rel, item in lineage["layout_inventory"].items()}
    expected_copied[n.CPATH + "/context/Dockerfile"] = n.sha(n.DOCKERFILE.encode())
    observed_copied = {line.split(None, 1)[1].strip(): line.split(None, 1)[0] for line in copied["observed_sha256sum"].splitlines()}
    check("persisted_inside_container_hashes_match_prior_exact_bytes", expected_copied == copied["files"] == observed_copied
          and set(copied["actual_file_paths"]) == set(expected_copied))
    check("Dockerfile_exact_qualification_only", n.load("probe_dockerfile.json")["bytes_utf8"] == n.DOCKERFILE
          and n.load("probe_dockerfile.json")["sha256"] == n.sha(n.DOCKERFILE.encode()))
    rows = n.load("commands_run.json")
    create_rows = [r for r in rows if r["argv"][:2] == ["docker", "create"]]
    solves = [r for r in rows if r["name"] == "single_native_oci_session_solve"]
    version_rows = [r for r in rows if r["name"] == "native_client_version"]
    workers_rows = [r for r in rows if r["name"] == "native_same_daemon_workers"]
    check("one_daemon_one_version_one_workers_one_solve", len(create_rows) == len(solves) == len(version_rows) == len(workers_rows) == 1)
    check("no_Buildx_solve_pull_or_global_use", not any(r["argv"][1:3] == ["buildx", "build"] or "pull" in r["argv"] or "--use" in r["argv"] for r in rows)
          and "--pull=never" in create_rows[0]["argv"])
    check("no_external_TCP_exposure", not builder["PortBindings"] and not builder["TCP_daemon_listener"])
    check("internal_no_default_route_no_proxy", builder["internal"] and set(builder["network_attachments"]) == {n.INTERNAL}
          and not any(line.startswith("default ") for line in builder["routes"].splitlines()) and not builder["proxy_env_keys"])
    logpaths = [n.Q / name for name in ["buildctl.stdout.log", "buildctl.stderr.log", "daemon_precleanup.stdout.log", "daemon_precleanup.stderr.log"]]
    registry_lines = n.registry_lines("\n".join(p.read_text(errors="strict") for p in logpaths))
    check("complete_client_and_daemon_logs_no_registry_attempt", not registry_lines)
    source, run, output = n.load("source_binding_result.json"), n.load("run_observation.json"), n.load("output_observation.json")
    check("raw_solve_logs_match_record", n.digest(n.Q / "buildctl.stdout.log") == source["command"]["stdout_sha256"]
          and n.digest(n.Q / "buildctl.stderr.log") == source["command"]["stderr_sha256"])
    facts = {"same_daemon": command["same_container_id"] == connection["same_container_id"] == owned["container_id"],
        "daemon_count_created": len(create_rows), "external_TCP_listener": builder["TCP_daemon_listener"],
        "registry_attempts": len(registry_lines), "registry_pulls": sum("pull" in r["argv"] for r in rows),
        "benchmark_source_copied": copied["benchmark_source_copied"], "benchmark_dependency_installs": n.load("firewall.json")["BENCHMARK_DEPENDENCY_INSTALLS"],
        "event_count": final["attempt_state"]["event_count"], "canonical_modified": n.digest(n.ROOT / "evaluation/downstream_benchmark/v6_current_state.json") != n.h.CANONICAL,
        "production_client_switch_claim": n.load("firewall.json")["PRODUCTION_CLIENT_SWITCHED"] != "NO", "native_solve_count": len(solves)}
    n.validate_execution_facts(facts)
    check("rejection_policy_on_actual_execution_facts", True)
    if final["classification"] == n.PASS:
        check("source_registration_mapping_consumption_pass", source["source_binding"] == "PASS" and source["exit_code"] == 0
              and source["OCI_registration_accepted"] and source["frontend_mapping_accepted"] and source["frozen_base_consumed"])
        check("fixture_RUN_Python_3_6_9_x86_64_executable_pass", run["RUN_pass"] and run["actual_observation"]["platform.machine()"] == "x86_64"
              and run["actual_observation"]["sys.executable"] == "/usr/local/bin/python")
        independent = n.inspect_output(Path(output["retained_output"]))
        check("actual_output_archive_layers_platform_and_frozen_prefix_exact", independent == output and output["frozen_nine_rootfs_prefix_exact"])
    check("Docker_state_exact_restoration", n.load("docker_state_before.json") == n.load("docker_state_after.json")
          and n.load("cleanup_verification.json")["status"] == "PASS")
    check("evidence_persisted_before_cleanup", n.digest(n.Q / "precleanup_external_manifest.json") == n.load("precleanup_evidence_receipt.json")["external_manifest_sha256"]
          and n.load("precleanup_evidence_receipt.json")["evidence_persisted_before_cleanup"])
    firewall = n.load("firewall.json")
    check("all_real_work_counters_zero", all(firewall[k] == 0 for k in ["REAL_BENCHMARK_ATTEMPTS", "REAL_BENCHMARK_CLAIMS", "REAL_BENCHMARK_BUILDS",
        "BENCHMARK_DEPENDENCY_INSTALLS", "BENCHMARK_SOURCE_EXPORTS", "REGISTRY_PULLS", "UNAPPROVED_EGRESS"]))
    check("all_required_NO_flags", all(firewall[k] == "NO" for k in ["PRODUCTION_CLIENT_SWITCHED", "EVENT_3_CREATED", "CANONICAL_CURRENT_STATE_MODIFIED", "GIT_STAGE", "GIT_COMMIT", "GIT_PUSH"]))
    for path in n.OUT.iterdir():
        if path.is_file():
            raw = path.read_bytes()
            raw.decode("utf-8", errors="strict")
            if path.suffix == ".json":
                n.strict_json(raw)
            if path.suffix == ".py":
                ast.parse(raw.decode("utf-8"), filename=str(path))
            check("no_trailing_whitespace:" + path.name, all(line == line.rstrip(b" \t") for line in raw.splitlines()))
    check("strict_JSON_UTF8_AST", True)
    return checks


def validate():
    outcomes = {}
    for label, argv in [
        ("focused_tests", [str(n.ROOT / ".venv/bin/python"), "-B", str(n.OUT / "test_native_probe.py")]),
        ("ruff", [str(n.ROOT / ".venv/bin/ruff"), "check", str(n.OUT)]),
        ("git_diff_check", ["git", "diff", "--check"]),
    ]:
        result, rec = n.command(label, argv, check=False)
        n.durable(n.OUT / (label + ".stdout.txt"), result.stdout)
        n.durable(n.OUT / (label + ".stderr.txt"), result.stderr)
        outcomes[label] = rec
        n.require(result.returncode == 0, label + " failed")
    checks = evidence_checks()
    required_rejections = {
        "Buildx_invocation_used": "test_reject_buildx_solve", "old_Buildx_OCI_syntax_used": "test_reject_old_buildx_oci_syntax",
        "wrong_OCI_store_name": "test_reject_wrong_store_registration", "wrong_transport_manifest": "test_reject_wrong_transport_manifest",
        "wrong_daemon": "test_reject_wrong_daemon_command", "second_daemon_created": "test_reject_second_daemon",
        "external_TCP_daemon_exposure": "test_reject_external_tcp_endpoint", "registry_access": "test_reject_registry_attempt",
        "pull": "test_reject_pull", "benchmark_source_copy": "test_reject_benchmark_source_copy",
        "benchmark_dependency_install": "test_reject_benchmark_dependency_install", "event_3": "test_reject_event_three",
        "canonical_mutation": "test_reject_canonical_mutation", "production_client_switch_claim": "test_reject_production_client_switch_claim",
    }
    log = outcomes["focused_tests"]["stderr"]
    n.require("Ran 23 tests" in log and log.rstrip().endswith("OK"), "focused test count/result mismatch")
    for method in required_rejections.values():
        n.require(any(line.startswith(method + " ") and line.endswith(" ... ok") for line in log.splitlines()), "missing rejection test")
    n.save("rejection_matrix.json", {"status": "PASS_OFFLINE_REJECTIONS", "rejections": {k: {"test": v, "result": "PASS"} for k, v in required_rejections.items()},
        "methods_passed": 23, "scientific_validation": False, "live_probe_classification": n.load("final_verification.json")["classification"]})
    n.save("validation_results.json", {"status": "PASS_EVIDENCE_AND_REQUIRED_CHECKS", "classification": n.load("final_verification.json")["classification"],
        "focused_tests": {"passed": 23, "failed": 0, "errors": 0, "skipped": 0}, "commands": outcomes,
        "ruff": "PASS", "AST": "PASS", "strict_JSON_UTF8": "PASS", "git_diff_check": "PASS", "checks": checks,
        "checks_passed": len(checks), "checks_failed": 0, "next_gate": n.load("final_verification.json")["next_gate"],
        "scientific_validation": False, "scope": "first-base native OCI-session compatibility only"})
    print(f"VALIDATION PASS: 23 tests; Ruff/AST/strict JSON UTF8/diff; {len(checks)} evidence checks")


def seal():
    n.require((n.OUT / "RUN_REPORT.md").exists(), "report missing")
    # Fresh final checks cover the report and validation records before sealing.
    checks = evidence_checks()
    n.save("final_integrity_receipt.json", {"status": "PASS_EVIDENCE_INTEGRITY_ONLY", "checks_passed": len(checks), "checks_failed": 0,
        "checks": checks, "scientific_validation": False})
    dest = n.Q / "final"
    dest.mkdir()
    for p in sorted(n.OUT.iterdir()):
        if p.is_file() and p.name not in {"artifact_sha256.json", "external_evidence_manifest.json"}:
            n.durable(dest / p.name, p.read_bytes())
    items = n.inventory(n.Q)
    n.save("external_evidence_manifest.json", {"root": str(n.Q), "artifact_inventory": items, "file_count": len(items),
        "all_bytes_verified": True, "benchmark_attempt_id": None, "qualification_only": True, "prior_external_preserved": True,
        "publication_model": "complete external inventory; external final copies precede repo manifest to avoid circular hashes"})
    artifacts = {str(p.relative_to(n.ROOT)): n.digest(p) for p in sorted(n.OUT.iterdir()) if p.is_file() and p.name != "artifact_sha256.json"}
    n.save("artifact_sha256.json", {"artifacts": artifacts, "file_count_including_manifest": len(artifacts) + 1,
        "self_hash_excluded": True, "status": n.load("final_verification.json")["classification"],
        "prior_files_preserved": 215, "real_attempts": 0, "next_gate": n.load("final_verification.json")["next_gate"]})
    verify_seal()


def verify_seal():
    manifest = n.load("artifact_sha256.json")
    actual = {str(p.relative_to(n.ROOT)): n.digest(p) for p in n.OUT.iterdir() if p.is_file() and p.name != "artifact_sha256.json"}
    n.require(actual == manifest["artifacts"] and len(actual) + 1 == manifest["file_count_including_manifest"], "repository seal differs")
    external = n.load("external_evidence_manifest.json")
    n.require(n.inventory(n.Q) == external["artifact_inventory"], "external seal differs")
    n.require(n.inventory(n.EXTERNAL, exclude=n.Q) == n.load("prior_external_inventory.json"), "prior external changed after sealing")
    print(json.dumps({"status": "PASS_SEALED_INVENTORIES", "repository_files": len(actual) + 1,
        "external_files": external["file_count"], "prior_repository_files": 215, "classification": manifest["status"]}))


if __name__ == "__main__":
    n.require(len(sys.argv) == 2 and sys.argv[1] in {"validate", "seal", "verify-seal"}, "explicit validation phase required")
    {"validate": validate, "seal": seal, "verify-seal": verify_seal}[sys.argv[1]]()

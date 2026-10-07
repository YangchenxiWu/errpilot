"""Independent read-only evidence/preservation verifier; --persist adds receipt."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
spec = importlib.util.spec_from_file_location("transport_evidence_subject", OUT / "transport_bridge.py")
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    checks = {}
    def check(name, condition):
        checks[name] = bool(condition)
        if not condition:
            raise AssertionError(name)
    entry, final = t.load("entry_verification.json"), t.load("final_verification.json")
    first, construction = t.load("first_base_transport_result.json"), t.load("oci_layout_construction.json")
    check("162_prior_repo_files_exact", len(entry["prior_file_hashes"]) == 162 and all(
        digest(ROOT / rel) == expected for rel, expected in entry["prior_file_hashes"].items()))
    check("canonical_and_index_exact", digest(ROOT / "evaluation/downstream_benchmark/v6_current_state.json") == entry["canonical_sha256"]
          and digest(ROOT / ".git/index") == entry["index_sha256"])
    check("HEAD_live_origin_required_at_entry_and_final", all(d["head"] == d["live_origin_main"] == t.prior.HEAD for d in [entry, final]))
    check("planning_event_count_two_execution_no", entry["event_count"] == 2 and entry["phase_authorizations"]["PREPARATION_EXECUTION"] == "NO")
    runtime = t.load("builder_runtime_verification.json")
    check("runtime_exact", runtime["engine_store_id"] == "sha256:cec9f139f45e93c5c69c60f8b07cfad9f43f4ef6b6a6cd917527fea5ff2e3dea"
          and runtime["platform_manifest_id"] == "sha256:98cc6a3fc46220d00f8224ae483f3274fc874e9be8d7dd1e2e2c5481209228b5"
          and runtime["verified_config_digest"] == "sha256:27933730df224df80c41f4e5a9b33fa78831a79fd31903df3bb7deb49363422f")
    export = t.load("archive_export_inventory.json")["exports"][0]
    check("single_exact_Engine_save", export["argv"] == ["docker", "image", "save", first["frozen_registry_identity"]]
          and export["exit_code"] == 0 and digest(Path(export["archive_path"])) == export["archive_sha256"]
          and Path(export["archive_path"]).stat().st_size == export["archive_size"])
    base = t.load("frozen_base_authorities.json")["bases"][0]
    independent_archive_observation = {}
    t.inspect_archive(Path(export["archive_path"]), base, independent_archive_observation)
    check("config_and_all_nine_tar_diffIDs_exact", independent_archive_observation["engine_config_identity"] == construction["engine_config_identity"]
          and independent_archive_observation["config_rootfs_diff_ids"] == construction["config_rootfs_diff_ids"]
          and len(independent_archive_observation["layers_checked"]) == 9
          and all(x["uncompressed_tar_sha256"] == x["expected_rootfs_diff_id"] for x in independent_archive_observation["layers_checked"]))
    inventory = t.validate_layout(Path(construction["local_oci_path"]), construction)
    check("actual_OCI_exact_and_content_addressed", inventory == first["layout_inventory"] and len(inventory) == 13)
    check("scientific_and_transport_identity_separate", first["frozen_registry_identity"].split("@", 1)[1] != construction["transport_manifest_identity"]
          and t.load("seven_base_transport_map.json")["transport_identity_in_base_attempt_identity"] is False)
    attempts = first["attempts"]
    check("two_failed_source_parser_requests_before_RUN", len(attempts) == 2 and all(
        x["exit_code"] == 1 and "could not parse oci-layout reference" in x["stderr"]
        and "invalid reference format" in x["stderr"] and "RUN python --version" in x["stderr"] for x in attempts))
    for index, stem in enumerate(["first_exact_reference", "first_alias"]):
        check(stem + "_raw_logs_exact", digest(t.Q / (stem + ".stdout.txt")) == attempts[index]["stdout_sha256"]
              and digest(t.Q / (stem + ".stderr.txt")) == attempts[index]["stderr_sha256"])
    check("no_registry_endpoint_in_build_logs", not any(token in row["stdout"] + row["stderr"] for row in attempts
          for token in ["registry-1.docker.io", "auth.docker.io", "https://registry"]))
    delta = t.load("dockerfile_transport_delta.json")
    check("preferred_original_bytes_and_single_alias_delta", delta["original_bytes"] == "FROM " + first["frozen_registry_identity"] + "\nRUN python --version\n"
          and delta["execution_bytes"] == delta["original_bytes"].replace(first["frozen_registry_identity"], "errpilot_frozen_base", 1)
          and t.sha(delta["original_bytes"].encode()) == delta["original_Dockerfile_sha256"]
          and t.sha(delta["execution_bytes"].encode()) == delta["execution_Dockerfile_sha256"])
    check("fallback_condition_deviation_disclosed", t.load("execution_corrections.json")["fallback_condition_classification_deviation"]["contract_compliance_exception"] is True
          and t.load("validation_results.json")["contract_compliance"] == "EXCEPTION_ALIAS_FALLBACK_CONDITION_MISCLASSIFIED")
    check("hard_stop_all_dependent_gates", all(t.load(name)["status"] == "NOT_RUN_FIRST_BASE_HARD_GATE" for name in [
        "all_base_transport_results.json", "output_parity_qualification.json", "downstream_egress_resume.json", "runtime_integration_diff.json"]))
    check("no_production_transport_rule_or_enforcement", t.load("seven_base_transport_map.json")["production_transport_rule_constructed"] is False
          and t.load("network_enforcement_identity.json")["semantic_enforcement_identity"] is None)
    check("641_583_58_blockers_and_attempt_ids_exact", (final["total"], final["restricted"], final["network_none"]) == (641, 583, 58)
          and final["blockers_non_dispatchable"] == ["matplotlib::1", "matplotlib::8"]
          and final["all_recipe_revision_plan_case_attempt_identities_preserved"] is True)
    check("precleanup_receipt_exact", digest(t.Q / "precleanup_evidence_manifest.json") == t.load("precleanup_evidence_receipt.json")["manifest_sha256"])
    check("Docker_global_surfaces_restored", t.load("docker_state_before.json") == t.load("docker_state_after.json"))
    cleanup = t.load("cleanup_verification.json")
    check("owned_cleanup_and_frozen_images_preserved", cleanup["status"] == "PASS" and cleanup["runtime_preserved"]
          and cleanup["seven_frozen_bases_preserved"] and cleanup["qualification_output_images_created"] == 0)
    check("prior_external_history_exact", t.prior.inventory(t.EXTERNAL, exclude=t.Q) == t.load("prior_external_inventory.json"))
    tests = t.load("test_results.json")
    check("19_methods_passed_no_skips", tests["status"] == "PASS" and tests["runtime_tests"]["run"] == 11
          and tests["runtime_tests"]["skipped"] == 0 and tests["focused_bridge_tests"]["test_methods"] == 8)
    firewall = t.load("firewall.json")
    check("required_zero_counters", all(firewall[k] == 0 for k in ["REAL_BENCHMARK_ATTEMPTS", "REAL_BENCHMARK_CLAIMS",
        "REAL_BENCHMARK_BUILDS", "BENCHMARK_DEPENDENCIES_INSTALLED", "REAL_BENCHMARK_SOURCE_EXPORTS", "REGISTRY_PULLS",
        "REGISTRY_BASE_RESOLUTION_REQUESTS_DURING_LOCAL_OCI_BUILDS"]))
    check("required_NO_flags", all(firewall[k] == "NO" for k in ["SOURCE_ACQUISITION_EXECUTED", "ORACLE_EXECUTED",
        "EVENT_3_CREATED", "CANONICAL_CURRENT_STATE_MODIFIED", "GIT_STAGE", "GIT_COMMIT", "GIT_PUSH"]))
    check("correct_blocked_status", t.load("validation_results.json")["status"] == t.NAMED_BLOCK)
    for path in OUT.glob("*.json"):
        t.strict_json(path.read_bytes())
    check("all_current_repo_JSON_strict_UTF8", True)
    if (OUT / "artifact_sha256.json").exists():
        seal = t.load("artifact_sha256.json")
        actual = {str(p.relative_to(ROOT)): digest(p) for p in OUT.iterdir() if p.is_file() and p.name != "artifact_sha256.json"}
        check("repository_seal_exact", actual == seal["artifacts"] and len(actual) + 1 == seal["file_count_including_manifest"])
        external = t.load("external_evidence_manifest.json")
        check("external_seal_exact", t.prior.inventory(t.Q) == external["artifact_inventory"])
    report = {"status": "PASS_EVIDENCE_INTEGRITY_ONLY", "checks_passed": len(checks), "checks_failed": 0,
              "checks": checks, "live_transport_qualification": "FAILED_NAMED_CONTEXT_GATE",
              "contract_compliance_exception_disclosed": True, "scientific_validation": False}
    if sys.argv[1:] == ["--persist"]:
        t.save("evidence_validation.json", report)
    elif sys.argv[1:]:
        raise ValueError("only --persist is supported")
    print(json.dumps({k: v for k, v in report.items() if k != "checks"}, sort_keys=True))


if __name__ == "__main__":
    main()

"""Independent read-only verification of the stopped resume evidence.

--persist exclusively writes a verification receipt in this new namespace.
Once sealed, the default mode also checks repository/external manifest equality.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
BLOCK = "V6_RESTRICTED_BUILD_EGRESS_BRIDGE_BASE_IMAGE_TRANSPORT_BLOCKED"
checks = {}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(name):
    return json.loads((OUT / name).read_bytes())


def check(name, condition):
    checks[name] = bool(condition)
    if not condition:
        raise AssertionError(name)


entry = load("entry_verification.json")
first = load("first_base_transport_qualification.json")
runtime = load("builder_runtime_verification.json")
builder = load("builder_creation_observation.json")
scope = load("work_item_scope.json")
cmds = load("commands_run.json")
external = Path(load("precleanup_evidence_receipt.json")["root"])

check("124_prior_files_exact", len(entry["prior_file_hashes"]) == 124 and all(
    sha((ROOT / rel).read_bytes()) == digest for rel, digest in entry["prior_file_hashes"].items()))
check("canonical_descriptor_exact", sha((ROOT / "evaluation/downstream_benchmark/v6_current_state.json").read_bytes())
      == entry["canonical_sha256"])
check("index_exact", sha((ROOT / ".git/index").read_bytes()) == entry["index_sha256"])
check("event_count_two_execution_no", entry["event_count"] == 2 and
      entry["phase_authorizations"]["PREPARATION_EXECUTION"] == "NO")
check("runtime_exact_digests_platform", runtime["engine_store_id"] ==
      "sha256:cec9f139f45e93c5c69c60f8b07cfad9f43f4ef6b6a6cd917527fea5ff2e3dea" and
      runtime["platform_manifest_id"] == "sha256:98cc6a3fc46220d00f8224ae483f3274fc874e9be8d7dd1e2e2c5481209228b5" and
      runtime["verified_config_digest"] == "sha256:27933730df224df80c41f4e5a9b33fa78831a79fd31903df3bb7deb49363422f" and
      runtime["platform"] == "linux/amd64")
check("immutable_driver_opt", runtime["immutable_reference"] in builder["builder"])
check("dedicated_driver", re.search(r"^Driver:\s+docker-container$", builder["builder"], re.M))
check("internal_only_attachment", list(builder["network_attachments"]) ==
      ["errpilot-v6-egress-42393faa3385-v1-internal"])
check("internal_network_true", load("internal_network_verification.json")["Internal"] is True)
check("no_default_route", not re.search(r"^default\s", builder["routes_interfaces"], re.M))
check("DNS_forwarding_loopback_only", builder["container_inspect"]["HostConfig"]["Dns"] == ["127.0.0.1"] and
      "# ExtServers: [127.0.0.1]" in builder["routes_interfaces"])
check("no_pull_or_global_selection_command", all("pull" not in r["argv"] and "--use" not in r["argv"] for r in cmds))
check("runtime_create_pull_never", all("--pull=never" in r["argv"] for r in cmds if r["argv"][:2] == ["docker", "create"]))
check("one_fixture_build_none_pull_false_load", len([r for r in cmds if r["argv"][:3] == ["docker", "buildx", "build"]]) == 1 and
      all(x in first["argv"] for x in ["--network=none", "--pull=false", "--load", "--no-cache", "--platform=linux/amd64"]))
check("first_base_mechanical_exact", first["selected_base_rule"] == "FIRST_IN_ACCEPTED_ORDERED_SEVEN_BASE_LEDGER" and
      first["exact_reference"] == "docker.io/library/python@sha256:036d4ab50fa49df89e746cf1b5369c88db46e8af2fbd08531788e7d920e9a491")
check("first_base_failed_at_registry_DNS", first["status"] == BLOCK and first["exit_code"] == 1 and
      'Head "https://registry-1.docker.io/' in first["stderr"] and
      "lookup registry-1.docker.io on 127.0.0.11:53: server misbehaving" in first["stderr"])
check("exact_fixture_only_Dockerfile", first["Dockerfile"] == "FROM " + first["exact_reference"] + "\nRUN python --version\n" and
      sha((external / "first-base-context/Dockerfile").read_bytes()) == first["Dockerfile_sha256"])
check("external_raw_failure_logs_exact", sha((external / "first_base.stdout.txt").read_bytes()) == first["stdout_sha256"] and
      sha((external / "first_base.stderr.txt").read_bytes()) == first["stderr_sha256"])
check("precleanup_receipt_exact", sha((external / "precleanup_evidence_manifest.json").read_bytes()) ==
      load("precleanup_evidence_receipt.json")["manifest_sha256"])
check("all_dependent_qualification_not_run", all(load(name)["status"] == "NOT_RUN_BASE_TRANSPORT_HARD_GATE" for name in [
      "all_base_transport_qualification.json", "output_parity_qualification.json", "proxy_runtime_identity.json",
      "application_binding.json", "positive_qualification.json", "negative_qualification.json",
      "network_enforcement_identity.json", "runtime_integration_diff.json", "rejection_matrix.json"]))
check("no_effective_enforcement_or_runtime_delta", load("network_enforcement_identity.json")["semantic_enforcement_identity"] is None and
      load("runtime_integration_diff.json")["files_changed"] == [])
check("641_583_58_preserved", (scope["total"], scope["restricted"], scope["network_none"]) == (641, 583, 58) and
      load("final_verification.json")["all_work_item_case_plan_recipe_revision_blocker_identities_preserved"] is True)
check("observable_global_state_exact", load("docker_state_before.json") == load("docker_state_after.json"))
check("owned_cleanup_and_frozen_images_preserved", load("cleanup_verification.json")["status"] == "PASS" and
      load("cleanup_verification.json")["runtime_preserved"] and load("cleanup_verification.json")["seven_frozen_bases_preserved"])
check("zero_real_attempts_claims_exports_builds", all(load("firewall.json")[k] == 0 for k in [
      "REAL_BENCHMARK_ATTEMPTS_CONSUMED", "REAL_BENCHMARK_CLAIMS_CREATED", "REAL_BENCHMARK_SOURCE_EXPORTS",
      "REAL_BENCHMARK_IMAGE_BUILDS", "BENCHMARK_DEPENDENCIES_INSTALLED", "UNAPPROVED_LIVE_EGRESS_REQUESTS"]))
check("exact_next_gate", load("validation_results.json")["next_gate"] ==
      "HUMAN_PI_DECIDE_V6_BUILDKIT_FROZEN_BASE_TRANSPORT_BRIDGE")
check("metadata_network_observation_reconciled", load("builder_metadata_reconciliation.json")["build_network_host_requested"] is False and
      load("builder_metadata_reconciliation.json")["worker_network_qualified_for_restricted_RUN"] is False)

if (OUT / "artifact_sha256.json").exists():
    d = load("artifact_sha256.json")
    actual = {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in OUT.iterdir()
              if p.is_file() and p.name != "artifact_sha256.json"}
    check("repository_manifest_exact", actual == d["artifacts"] and len(actual) + 1 == d["file_count_including_manifest"])
    d = load("external_evidence_manifest.json")
    actual = {str(p.relative_to(external)): {"type": "file", "bytes": p.stat().st_size, "sha256": sha(p.read_bytes())}
              for p in external.rglob("*") if p.is_file()}
    check("external_manifest_exact", actual == d["artifact_inventory"])

report = {"status": "PASS", "checks_passed": len(checks), "checks_failed": 0, "checks": checks,
          "first_base_qualification": "FAIL_EXPECTED_BLOCK_CLASSIFICATION", "runtime_suite": "NOT_RUN_HARD_GATE",
          "scientific_validation": False}
if sys.argv[1:] == ["--persist"]:
    path = OUT / "evidence_validation.json"
    with path.open("x") as stream:
        stream.write(json.dumps(report, sort_keys=True, indent=2) + "\n")
elif sys.argv[1:]:
    raise RuntimeError("only --persist is supported")
print(json.dumps(report, sort_keys=True))

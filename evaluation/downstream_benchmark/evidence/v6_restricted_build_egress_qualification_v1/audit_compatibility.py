"""Bounded existing-builder audit. Never provisions networks or dispatches work."""
from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a  # noqa: E402
from evaluation.downstream_benchmark.screening import v6_preparation_runtime as r  # noqa: E402

HEAD = "5c007fbfbfc5b3529105a14f87127f50e1eab6d7"
NETWORK_SHA = "42393faa33851396fd70557558fa0e538f817fbee9072d0d56ec9d9323fc21a1"
STEM = "errpilot-v6-egress-42393faa3385-v1"
COMMANDS = []


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     indent=2, allow_nan=False) + "\n", encoding="utf-8")


def command(name, argv, *, raw=True, timeout=60):
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=timeout, check=False)
    record = {"name": name, "argv": argv, "exit_code": result.returncode,
              "stdout_sha256": digest(result.stdout), "stderr_sha256": digest(result.stderr)}
    if raw:
        record.update(stdout=result.stdout.decode("utf-8"), stderr=result.stderr.decode("utf-8"))
    COMMANDS.append(record)
    return result


def checked(name, argv, *, raw=True):
    result = command(name, argv, raw=raw)
    a.require(result.returncode == 0, "audit observation failed: " + name)
    return result.stdout


def preserved_files():
    files = {}
    for package in ("v6_preparation_execution_activation_v1",
                    "v6_preparation_execution_runtime_implementation_v1"):
        path = a.B / "evidence" / package / "artifact_sha256.json"
        inventory = a.loads(path.read_bytes())
        for relative, expected in inventory["artifacts"].items():
            observed = digest((ROOT / relative).read_bytes())
            a.require(observed == expected, "accepted artifact changed: " + relative)
            files[relative] = observed
        files[str(path.relative_to(ROOT))] = digest(path.read_bytes())
    a.require(len(files) == 40, "accepted inventory must have exactly 40 files")
    return files


def config_hashes():
    paths = [Path("/etc/pf.conf"), Path("/etc/docker/daemon.json"),
             Path("/Users/wuyangchenxi/.docker/daemon.json"),
             Path("/Users/wuyangchenxi/Library/Group Containers/group.com.docker/settings-store.json")]
    result = {}
    for path in paths:
        try:
            result[str(path)] = {"status": "READABLE", "sha256": digest(path.read_bytes())}
        except FileNotFoundError:
            result[str(path)] = {"status": "ABSENT"}
        except PermissionError:
            result[str(path)] = {"status": "UNREADABLE"}
    return result


def snapshot(label):
    network_list = checked(label + "_network_ids", ["docker", "network", "ls", "-q"])
    ids = network_list.decode().split()
    networks = a.loads(checked(label + "_network_inspect",
                              ["docker", "network", "inspect", *ids]))
    container_list = checked(label + "_container_ids", ["docker", "ps", "-aq", "--no-trunc"])
    containers = []
    for container_id in container_list.decode().split():
        raw = checked(label + "_container_inspect", ["docker", "inspect", container_id], raw=False)
        item = a.loads(raw)[0]
        containers.append({"Id": item["Id"], "Name": item["Name"], "Image": item["Image"],
                           "State": item["State"], "NetworkSettings": item["NetworkSettings"],
                           "inspect_sha256": digest(raw)})
    images = checked(label + "_images", ["docker", "image", "ls", "--no-trunc", "--digests",
                                        "--format", "{{json .}}"])
    image_rows = sorted(images.decode().splitlines())
    application_firewall = command(label + "_application_firewall", [
        "/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"])
    pf = command(label + "_pf_rules", ["/sbin/pfctl", "-sr"])
    builder = checked(label + "_builder", ["docker", "buildx", "inspect", "desktop-linux"])
    return {"networks": networks, "containers": containers, "images": image_rows,
            "configuration_file_hashes": config_hashes(),
            "application_firewall": {"exit_code": application_firewall.returncode,
                                     "stdout_sha256": digest(application_firewall.stdout)},
            "host_pf_rules": {"exit_code": pf.returncode, "stdout_sha256": digest(pf.stdout),
                              "stderr_sha256": digest(pf.stderr)},
            "builder_stdout_sha256": digest(builder), "builder": builder.decode()}


def main():
    original = preserved_files()
    untracked = checked("entry_untracked", ["git", "ls-files", "--others", "--exclude-standard"])
    observed = set(untracked.decode().splitlines())
    own = str(OUT.relative_to(ROOT)) + "/"
    a.require({x for x in observed if not x.startswith(own)} == set(original),
              "unrelated or missing untracked file")
    head = checked("entry_head", ["git", "rev-parse", "HEAD"]).decode().strip()
    branch = checked("entry_branch", ["git", "branch", "--show-current"]).decode().strip()
    a.require((head, branch) == (HEAD, "main"), "local entry identity")
    checked("entry_tracked_clean", ["git", "diff", "--exit-code"])
    checked("entry_index_clean", ["git", "diff", "--cached", "--exit-code"])
    index_hash = digest((ROOT / ".git/index").read_bytes())
    live = checked("entry_live_origin", ["git", "ls-remote", "--exit-code", "origin", "refs/heads/main"])
    a.require(live.decode().split()[0] == HEAD, "live origin drift")
    descriptor, manifest = a.load_inputs()
    a.require(digest((a.B / "v6_current_state.json").read_bytes()) == a.CURRENT_SHA,
              "live canonical descriptor changed")
    authority = a.loads((a.B / "evidence/v6_preparation_execution_activation_v1/authority_candidates.json").read_bytes())
    acceptance = a.loads(a.read_exact(r.AUTHORITY, r.AUTHORITY_SHA))
    r.validate_acceptance(acceptance, network_required=True)
    network = authority["separate_permissions"]["BUILD_NETWORK"]
    a.require(a.identity(network) == NETWORK_SHA, "BUILD_NETWORK semantic identity changed")
    population = r.population()
    a.require(a.derive_population(manifest) == population, "production selector population changed")
    allowed_ids = network["exact_scope"]["exact_network_work_item_ids"]
    all_ids = [x["base_attempt_id"] for x in population["items"]]
    flagged = [x["base_attempt_id"] for x in population["items"] if x["build_network_required"]]
    a.require(allowed_ids == flagged and len(allowed_ids) == 583 and len(all_ids) == 641,
              "exact ordered accepted scope mismatch")
    none_ids = [x for x in all_ids if x not in set(allowed_ids)]
    a.require(len(none_ids) == 58 and len(set(all_ids)) == 641, "NONE scope changed")
    scope = {"schema": "V6_RESTRICTED_BUILD_EGRESS_EXACT_SCOPE_V1", "BUILD_NETWORK_semantic_sha256": NETWORK_SHA,
             "authority_path": str((a.B / "evidence/v6_preparation_execution_activation_v1/authority_candidates.json").relative_to(ROOT)),
             "authority_file_sha256": r.AUTH_CANDIDATE_SHA,
             "restricted_ids_source": "exact_network_work_item_ids copied unchanged from accepted authority",
             "restricted_work_item_ids": allowed_ids, "network_none_work_item_ids": none_ids,
             "total": 641, "restricted": 583, "network_none": 58, "blocked_cases": population["blocked"]}
    save("work_item_scope.json", scope)
    saved = a.loads((a.B / "evidence/v6_preparation_execution_runtime_implementation_v1/qualification_results.json").read_bytes())
    a.require(saved["default_deny_dispatch"] == "REJECT" and saved["real_preparation_attempts"] == 0
              and saved["ledger"] == "PASS" and saved["base_runtime_pass"] == 7,
              "saved runtime conclusions changed")
    save("entry_verification.json", {"schema": "V6_RESTRICTED_EGRESS_ENTRY_VERIFICATION_V1", "status": "PASS",
         "head": head, "branch": branch, "live_origin_main": live.decode().split()[0],
         "canonical_descriptor_sha256": a.CURRENT_SHA, "event_count": descriptor["event_count"],
         "phase_authorizations": descriptor["projection"]["phase_authorizations"],
         "PREPARATION_AUTHORIZED": descriptor["projection"]["lifecycle"]["PREPARATION_AUTHORIZED"],
         "accepted_file_count": 40, "accepted_file_hashes": original,
         "index_sha256": index_hash, "unrelated_untracked": [],
         "saved_runtime_conclusions": saved, "own_transaction_paths_excluded_from_entry_inventory": own,
         "airos_current_state": "ABSENT", "repository_AGENTS": "ABSENT"})
    before = snapshot("before")
    save("docker_state_before.json", before)
    forbidden_names = {STEM + suffix for suffix in ("-internal", "-external", "-proxy", "-client", "-fixture", "-builder")}
    collisions = [n["Name"] for n in before["networks"] if n["Name"] in forbidden_names]
    collisions += [c["Name"].lstrip("/") for c in before["containers"] if c["Name"].lstrip("/") in forbidden_names]
    a.require(not collisions, "pre-existing qualification name collision; no object will be deleted")
    version = a.loads(checked("docker_version", ["docker", "version", "--format", "{{json .}}"] ))
    help_text = checked("docker_build_help", ["docker", "build", "--help"]).decode()
    docker_path = checked("docker_binary_path", ["/usr/bin/which", "docker"]).decode().strip()
    backend_environment = {k: os.environ.get(k) for k in ("DOCKER_BUILDKIT", "BUILDX_BUILDER", "DOCKER_CONTEXT", "DOCKER_HOST")}
    # Credentials/proxy environment and unrelated container environment are never persisted.
    source = (a.B / "screening/materializer.py").read_bytes()
    tree = ast.parse(source)
    function = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == "_materialize_checked")
    assignment = next(x for x in ast.walk(function) if isinstance(x, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == "command" for t in x.targets)
                      and isinstance(x.value, ast.List) and x.value.elts
                      and isinstance(x.value.elts[0], ast.Constant) and x.value.elts[0].value == "build")
    effective = ["docker", "build", "--platform=linux/amd64", "--network=default", "--progress=plain", "--no-cache",
                 "-t", "<frozen-image-tag>", "-f", "<accepted-context>/Dockerfile", "<accepted-context>"]
    bases = a.loads((a.B / "evidence/v6_preparation_execution_runtime_implementation_v1/base_runtime_local_status.json").read_bytes())
    base_results = []
    code = ("import hashlib,json,platform,sys; p=sys.executable; "
            "print(json.dumps({'version':'.'.join(map(str,sys.version_info[:3])),"
            "'machine':platform.machine(),'executable':p,"
            "'executable_sha256':hashlib.sha256(open(p,'rb').read()).hexdigest()}))")
    for base in bases["bases"]:
        raw = checked("base_inspect_" + base["python_version"], ["docker", "image", "inspect", base["reference"]], raw=False)
        image = a.loads(raw)[0]
        identity = {k: image[k] for k in ("Id", "Architecture", "Os", "RepoDigests", "RootFS")}
        a.require(identity == base["image_identity"], "local frozen base identity drift")
        probe = a.loads(checked("base_probe_" + base["python_version"], ["docker", "run", "--rm", "--pull=never",
            "--name", STEM + "-client", "--label", "errpilot.qualification=" + STEM,
            "--platform=linux/amd64", "--network=none", "--read-only", "--tmpfs", "/tmp",
            base["reference"], "python", "-c", code]))
        a.require(probe == base["python_probe"], "frozen Python executable probe drift")
        base_results.append({"reference": base["reference"], "image_identity": identity,
                             "python_probe": probe, "local_status": "LOCAL_PRESENT", "qualification": "PASS"})
    save("base_runtime_revalidation.json", {"status": "PASS", "bases": base_results, "pass": 7, "pulls": 0})
    # A scratch-only check invokes the installed production docker-build frontend.
    # --call=check stops before image output; there are no RUNs, external sources or dependencies.
    with tempfile.TemporaryDirectory(prefix=STEM + "-parser-", dir="/private/tmp") as directory:
        context = Path(directory)
        (context / "Dockerfile").write_text("FROM scratch\n", encoding="utf-8")
        argv = ["docker", "build", "--platform=linux/amd64", "--network=" + STEM + "-internal",
                "--progress=plain", "--no-cache", "--call=check", "-t", STEM + "-client",
                "-f", str(context / "Dockerfile"), str(context)]
        parser = command("existing_builder_custom_network_parser_probe", argv)
    output = (parser.stdout + parser.stderr).decode()
    rejection = parser.returncode != 0 and "not supported by buildkit" in output.lower() and "network mode" in output.lower()
    docker_driver = "Driver:        docker" in before["builder"]
    frontend = "Usage:  docker buildx build" in help_text
    proven = rejection and docker_driver and frontend and not backend_environment["DOCKER_BUILDKIT"] == "0"
    classification = "REQUIRES_BUILDER_ARCHITECTURE_CHANGE" if proven else "UNDERDETERMINED"
    status = "V6_RESTRICTED_BUILD_EGRESS_SHARED_ENGINE_COMPATIBILITY_BLOCKED" if proven else "BLOCKED"
    save("compatibility_analysis.json", {"schema": "V6_RESTRICTED_BUILD_EGRESS_COMPATIBILITY_ANALYSIS_V1",
         "classification": classification, "status": status, "production_path": "evaluation/downstream_benchmark/screening/materializer.py",
         "production_file_sha256": digest(source), "command_assignment_line": assignment.lineno,
         "command_assignment_source": ast.get_source_segment(source.decode(), assignment),
         "effective_restricted_build_argv_template": effective,
         "network_none_argv_difference": "--network=none", "subprocess_environment": "inherited; no env override in shared docker()",
         "observed_backend_environment": backend_environment, "docker_binary_sha256": digest(Path(docker_path).read_bytes()),
         "docker_version": version, "production_frontend_is_buildx": frontend,
         "selected_builder": "desktop-linux", "selected_builder_driver": "docker" if docker_driver else "UNDETERMINED",
         "builder_inspection": before["builder"], "named_network_rejected": rejection,
         "parser_probe": COMMANDS[-1], "parser_probe_dockerfile": "FROM scratch\n",
         "parser_probe_has_no_RUN_no_dependency_no_source_no_output": True,
         "qualification_only_builder_created": False,
         "exact_incompatibility": "The existing docker-build BuildKit frontend rejects the required named internal network. Shared production code selects default/none only, provides no proxy build arguments, and the existing docker-driver worker is daemon-managed. A named-network docker-run client would not test production build networking. Changing builders or daemon/default-network policy is outside E9/E7.",
         "prohibited_workarounds": ["switch to legacy builder", "create/select docker-container builder", "change Docker daemon/default bridge policy", "machine-global firewall"],
         "compatibility_proven": False, "topology_provisioning_authorized_under_section_5": False})
    after = snapshot("after")
    save("docker_state_after.json", after)
    a.require(before["networks"] == after["networks"], "unrelated network state drift")
    a.require(before["containers"] == after["containers"], "unrelated container state drift")
    a.require(before["images"] == after["images"], "image inventory drift")
    a.require(before["configuration_file_hashes"] == after["configuration_file_hashes"], "global configuration drift")
    a.require(preserved_files() == original, "accepted packages changed during audit")
    a.require(digest((ROOT / ".git/index").read_bytes()) == index_hash, "index bytes changed")
    checked("final_tracked_clean", ["git", "diff", "--exit-code"])
    checked("final_index_clean", ["git", "diff", "--cached", "--exit-code"])
    save("global_state_preservation.json", {"status": "PASS_FOR_OBSERVED_SURFACES",
         "networks_inspect_identical": True, "containers_inspect_identical": True, "image_inventory_identical": True,
         "readable_configuration_hashes_identical": True, "default_bridge_inspect_identical": True,
         "application_firewall_observation_identical": before["application_firewall"] == after["application_firewall"],
         "host_pf_runtime_rules": "NOT_READABLE_WITHOUT_PRIVILEGED_PF_ACCESS" if before["host_pf_rules"]["exit_code"] else "COMPARED",
         "host_pf_runtime_rules_observation_identical": before["host_pf_rules"] == after["host_pf_rules"],
         "docker_vm_daemon_config_directly_read": False,
         "limitations": "Host PF runtime rules and daemon VM config are not directly proven. Readable config hashes, exact command inventory, unchanged network/container/image observations and no mutation commands support no-agent-global-mutation attestation.",
         "agent_firewall_mutation_commands": 0, "agent_daemon_mutation_commands": 0,
         "agent_default_bridge_mutation_commands": 0, "third_party_software_installs": 0,
         "unrelated_resource_deletions": 0, "accepted_40_files_preserved": True, "index_bytes_preserved": True})
    save("topology_identity.json", {"status": "NOT_PROVISIONED_COMPATIBILITY_GATE_BLOCKED", "namespace": STEM,
         "planned_internal_network": STEM + "-internal", "planned_external_network": STEM + "-external",
         "planned_proxy": STEM + "-proxy", "preexisting_name_collisions": collisions,
         "actual_internal_network": None, "actual_external_network": None, "actual_proxy": None,
         "Internal_true_inspection": "NOT_RUN", "build_client_route_inspection": "NOT_RUN",
         "extra_external_interface_probe": "NOT_RUN", "direct_egress_qualified": False})
    save("cleanup_verification.json", {"status": "PASS_NO_REMAINING_TRANSACTION_RESOURCES",
         "seven_network_none_identity_probe_clients": "REMOVED_BY_DOCKER_RUN_RM",
         "scratch_parser_context": "REMOVED_BY_TEMPORARYDIRECTORY", "topology_networks_created": 0,
         "proxy_created": False, "fixture_created": False, "builder_created": False,
         "networks_unchanged": True, "containers_unchanged": True, "images_unchanged": True,
         "unrelated_objects_deleted": 0})
    save("commands_run.json", {"scope": "read-only entry/builder inspections, seven no-network identity probes, scratch-only existing-builder parser check", "commands": COMMANDS})
    print(json.dumps({"status": status, "classification": classification, "base_runtime_pass": 7,
                      "parser_exit_code": parser.returncode, "parser_output": output, "accepted_files_preserved": 40}))


if __name__ == "__main__":
    main()

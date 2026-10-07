"""Read-only Docker audit of the missing-runtime bridge gate; never bootstraps."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a  # noqa: E402
from evaluation.downstream_benchmark.screening import v6_preparation_runtime as r  # noqa: E402

HEAD = "5c007fbfbfc5b3529105a14f87127f50e1eab6d7"
RUNTIME = "moby/buildkit:buildx-stable-1"
BUILDER = "errpilot-v6-builder-42393faa3385-v1"
STEM = "errpilot-v6-egress-42393faa3385-v1"
STATUS = "V6_RESTRICTED_BUILD_EGRESS_BRIDGE_BUILDKIT_RUNTIME_MISSING"
REQUEST = Path("/Users/wuyangchenxi/.codex/attachments/defff922-013a-4d9d-b3e6-71d41ba65162/已粘贴的文本.txt")
COMMANDS = []


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     indent=2, allow_nan=False) + "\n", encoding="utf-8")


def command(name, argv, *, raw=True, timeout=60):
    if argv[0] == "docker":
        permitted = argv[1:3] in (["buildx", "version"], ["buildx", "inspect"],
            ["image", "ls"], ["image", "inspect"], ["network", "ls"],
            ["network", "inspect"], ["volume", "ls"], ["volume", "inspect"])
        permitted |= argv[1] in {"version", "ps", "inspect"}
        if argv[1] == "run":
            permitted = (name.startswith("engine_base_probe_") and "--pull=never" in argv
                and "--network=none" in argv and "--rm" in argv and "--read-only" in argv
                and argv[argv.index("--name") + 1] == STEM + "-bridge-base-probe")
        a.require(permitted, "audit forbids builder creation, bootstrap, builds and pulls")
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=timeout, check=False)
    record = {"name": name, "argv": argv, "exit_code": result.returncode,
              "stdout_sha256": sha(result.stdout), "stderr_sha256": sha(result.stderr)}
    if raw:
        record.update(stdout=result.stdout.decode("utf-8"), stderr=result.stderr.decode("utf-8"))
    COMMANDS.append(record)
    return result


def checked(name, argv, *, raw=True):
    result = command(name, argv, raw=raw)
    a.require(result.returncode == 0, "observation failed: " + name)
    return result.stdout


def preserved_files():
    files = {}
    packages = []
    for package, count in (("v6_preparation_execution_activation_v1", 14),
                           ("v6_preparation_execution_runtime_implementation_v1", 26),
                           ("v6_restricted_build_egress_qualification_v1", 29)):
        path = a.B / "evidence" / package / "artifact_sha256.json"
        inventory = a.loads(path.read_bytes())
        local = {}
        for relative, expected in inventory["artifacts"].items():
            actual = sha((ROOT / relative).read_bytes())
            a.require(actual == expected, "accepted artifact changed: " + relative)
            local[relative] = actual
        relative = str(path.relative_to(ROOT))
        local[relative] = sha(path.read_bytes())
        a.require(len(local) == count, "accepted inventory cardinality: " + package)
        files.update(local)
        packages.append({"package": package, "file_count": count, "manifest_sha256": local[relative]})
    a.require(len(files) == 69, "exact 69-file entry population required")
    return files, packages


def config_hashes():
    paths = [Path("/etc/pf.conf"), Path("/etc/docker/daemon.json"),
        Path("/Users/wuyangchenxi/.docker/daemon.json"),
        Path("/Users/wuyangchenxi/.docker/config.json"),
        Path("/Users/wuyangchenxi/Library/Group Containers/group.com.docker/settings-store.json")]
    result = {}
    for path in paths:
        try:
            result[str(path)] = {"status": "READABLE", "sha256": sha(path.read_bytes())}
        except FileNotFoundError:
            result[str(path)] = {"status": "ABSENT"}
        except PermissionError:
            result[str(path)] = {"status": "UNREADABLE"}
    return result


def snapshot(label):
    ids = checked(label + "_network_ids", ["docker", "network", "ls", "-q"]).decode().split()
    networks = a.loads(checked(label + "_networks", ["docker", "network", "inspect", *ids])) if ids else []
    ids = checked(label + "_container_ids", ["docker", "ps", "-aq", "--no-trunc"]).decode().split()
    containers = []
    for value in ids:
        raw = checked(label + "_container", ["docker", "inspect", value], raw=False)
        item = a.loads(raw)[0]
        containers.append({"Id": item["Id"], "Name": item["Name"], "Image": item["Image"],
            "State": item["State"], "NetworkSettings": item["NetworkSettings"], "inspect_sha256": sha(raw)})
    images = checked(label + "_images", ["docker", "image", "ls", "-a", "--no-trunc", "--digests",
        "--format", "{{.ID}}|{{.Repository}}|{{.Tag}}|{{.Digest}}"])
    ids = checked(label + "_volume_names", ["docker", "volume", "ls", "-q"]).decode().split()
    volumes = a.loads(checked(label + "_volumes", ["docker", "volume", "inspect", *ids])) if ids else []
    selected = checked(label + "_selected_builder", ["docker", "buildx", "inspect"])
    app_fw = command(label + "_application_firewall", [
        "/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"])
    pf = command(label + "_pf_rules", ["/sbin/pfctl", "-sr"])
    buildx = Path("/Users/wuyangchenxi/.docker/buildx")
    buildx_files = {str(p.relative_to(buildx)): sha(p.read_bytes())
        for p in sorted(buildx.rglob("*")) if p.is_file() and not p.is_symlink()
        and (p.name in {"current", "defaults"} or "instances" in p.relative_to(buildx).parts)}
    return {"networks": networks, "containers": containers,
        "images": sorted(images.decode().splitlines()), "volumes": volumes,
        "configuration_file_hashes": config_hashes(), "buildx_selection_configuration_hashes": buildx_files,
        "selected_builder": selected.decode(), "selected_builder_sha256": sha(selected),
        "application_firewall": {"exit_code": app_fw.returncode, "stdout_sha256": sha(app_fw.stdout)},
        "host_pf_rules": {"exit_code": pf.returncode, "stdout_sha256": sha(pf.stdout),
                          "stderr_sha256": sha(pf.stderr)}}


def main():
    original, packages = preserved_files()
    own = str(OUT.relative_to(ROOT)) + "/"
    untracked = checked("entry_untracked", ["git", "ls-files", "--others", "--exclude-standard"])
    a.require({x for x in untracked.decode().splitlines() if not x.startswith(own)} == set(original),
              "unrelated or missing untracked file")
    head = checked("entry_head", ["git", "rev-parse", "HEAD"]).decode().strip()
    branch = checked("entry_branch", ["git", "branch", "--show-current"]).decode().strip()
    a.require((head, branch) == (HEAD, "main"), "entry identity")
    checked("entry_tracked_clean", ["git", "diff", "--exit-code"])
    checked("entry_index_clean", ["git", "diff", "--cached", "--exit-code"])
    index_sha = sha((ROOT / ".git/index").read_bytes())
    live = checked("entry_live_origin", ["git", "ls-remote", "--exit-code", "origin", "refs/heads/main"])
    a.require(live.decode().split()[0] == HEAD, "live origin drift")
    descriptor, manifest = a.load_inputs()
    population = r.population()
    a.require(a.derive_population(manifest) == population, "641 identity preservation")
    authority = a.loads(a.read_exact(r.PACKAGE + "authority_candidates.json", r.AUTH_CANDIDATE_SHA))
    network = authority["separate_permissions"]["BUILD_NETWORK"]
    restricted = [x["base_attempt_id"] for x in population["items"] if x["build_network_required"]]
    none = [x["base_attempt_id"] for x in population["items"] if not x["build_network_required"]]
    a.require(network["exact_scope"]["exact_network_work_item_ids"] == restricted
              and len(restricted) == 583 and len(none) == 58, "exact network scopes")
    previous = a.loads((a.B / "evidence/v6_restricted_build_egress_qualification_v1/compatibility_analysis.json").read_bytes())
    a.require(previous["classification"] == "REQUIRES_BUILDER_ARCHITECTURE_CHANGE"
              and previous["named_network_rejected"] is True, "prior finding")
    a.require(sha((ROOT / previous["production_path"]).read_bytes()) == previous["production_file_sha256"],
              "shared materializer drift")
    save("entry_verification.json", {"status": "PASS", "head": head, "branch": branch,
        "live_origin_main": live.decode().split()[0], "canonical_descriptor_sha256": a.CURRENT_SHA,
        "event_count": descriptor["event_count"], "lifecycle": descriptor["lifecycle_label"],
        "phase_authorizations": descriptor["projection"]["phase_authorizations"],
        "accepted_packages": packages, "accepted_file_hashes": original, "index_sha256": index_sha,
        "unrelated_untracked": [], "initial_prewrite_69_file_verification": "PASS_BEFORE_FIRST_NEW_WRITE",
        "airos_current_state": "ABSENT", "repository_AGENTS": "ABSENT", "previous_finding": previous,
        "failed_preliminary_inventory_check": "Inline assertion was placed within the package loop; corrected and all 69 hashes verified before writing."})
    raw_request = REQUEST.read_bytes()
    save("accepted_decision.json", {"authority": "HUMAN_PI_DECIDE_V6_RESTRICTED_BUILD_EGRESS_COMPATIBILITY_BRIDGE",
        "decision": "ADOPT_V6_DEDICATED_DOCKER_CONTAINER_BUILDER_COMPATIBILITY_BRIDGE_V1",
        "request_path": str(REQUEST), "request_sha256": sha(raw_request),
        "exact_request": raw_request.decode("utf-8"), "scope": "BRIDGE_CONSTRUCTION_AND_QUALIFICATION_ONLY",
        "canonical_execution_authority": "NO", "event_3_authorized": False})
    save("work_item_scope.json", {"status": "PASS", "total": 641, "restricted": 583, "network_none": 58,
        "population_sha256": a.identity(population), "BUILD_NETWORK_semantic_sha256": a.identity(network),
        "restricted_work_item_ids": restricted, "network_none_work_item_ids": none,
        "blocked_cases": population["blocked"], "all_items_unchanged": True})
    before = snapshot("before")
    save("docker_state_before.json", before)
    names = {STEM + x for x in ("-internal", "-external", "-proxy", "-fixture", "-bridge-base-probe")}
    names |= {"buildx_buildkit_" + BUILDER + "0"}
    a.require(not any(x["Name"] in names for x in before["networks"]), "network collision")
    a.require(not any(x["Name"].lstrip("/") in names for x in before["containers"]), "container collision")
    absent_builder = command("dedicated_builder_absent", ["docker", "buildx", "inspect", BUILDER])
    a.require(absent_builder.returncode != 0 and "no builder" in absent_builder.stderr.decode().lower(),
              "dedicated builder already exists or absence underdetermined")
    version = checked("buildx_version", ["docker", "buildx", "version"]).decode().strip()
    binary_path = Path("/Applications/Docker.app/Contents/Resources/cli-plugins/docker-buildx")
    binary = binary_path.read_bytes()
    offsets = [m.start() for m in re.finditer(re.escape(RUNTIME.encode()), binary)]
    a.require(offsets, "installed Buildx does not contain expected runtime reference")
    runtime = command("exact_buildkit_image_inspect", ["docker", "image", "inspect", RUNTIME])
    a.require(runtime.returncode != 0 and "No such image" in runtime.stderr.decode(),
              "missing-runtime-only audit cannot handle a present or uncertain runtime")
    runtime_rows = [x for x in before["images"] if "buildkit" in x.lower()]
    a.require(not runtime_rows, "other named BuildKit images require separate exact-reference assessment")
    save("builder_runtime_identity.json", {"status": STATUS, "exact_runtime_reference": RUNTIME,
        "reference_selection": "Explicit planned --driver-opt=image=" + RUNTIME,
        "installed_binary_reference_offsets": offsets, "installed_buildx_binary": str(binary_path),
        "installed_buildx_binary_sha256": sha(binary), "buildx_version": version,
        "local_image_inspect": COMMANDS[-1], "local_buildkit_named_image_rows": runtime_rows,
        "local_image_present": False, "runtime_image_id": None, "runtime_buildkit_version": None,
        "pulls": 0, "builder_created": False,
        "desktop_builtin_buildkit": "Existing daemon worker is not an Engine-store docker-container runtime image; not substituted."})
    save("builder_configuration.json", {"status": "PLANNED_NOT_PROVISIONED_RUNTIME_GATE_BLOCKED",
        "name": BUILDER, "driver": "docker-container", "scope": "DEDICATED_ERRPILOT_V6_ONLY",
        "driver_options": {"network": STEM + "-internal", "image": RUNTIME},
        "planned_create_argv": ["docker", "buildx", "create", "--name", BUILDER,
            "--driver=docker-container", "--driver-opt=network=" + STEM + "-internal",
            "--driver-opt=image=" + RUNTIME],
        "default_builder_selection_mutation": False, "global_use": False,
        "actual_container_id": None, "actual_container_networks": None, "routes_interfaces": "NOT_RUN",
        "driver_runtime_configuration": "NOT_RUN", "buildkit_version": "NOT_OBSERVED"})
    bases = a.loads((a.B / "evidence/v6_preparation_execution_runtime_implementation_v1/base_runtime_local_status.json").read_bytes())
    base_results = []
    code = ("import hashlib,json,platform,sys; p=sys.executable; "
        "print(json.dumps({'version':'.'.join(map(str,sys.version_info[:3])),"
        "'machine':platform.machine(),'executable':p,"
        "'executable_sha256':hashlib.sha256(open(p,'rb').read()).hexdigest()}))")
    for base in bases["bases"]:
        raw = checked("engine_base_inspect_" + base["python_version"],
            ["docker", "image", "inspect", base["reference"]], raw=False)
        image = a.loads(raw)[0]
        identity = {k: image[k] for k in ("Id", "Architecture", "Os", "RepoDigests", "RootFS")}
        a.require(identity == base["image_identity"], "Engine-store frozen base drift")
        probe = a.loads(checked("engine_base_probe_" + base["python_version"], ["docker", "run", "--rm",
            "--pull=never", "--name", STEM + "-bridge-base-probe", "--label", "errpilot.qualification=" + BUILDER,
            "--platform=linux/amd64", "--network=none", "--read-only", "--tmpfs", "/tmp",
            base["reference"], "python", "-c", code]))
        a.require(probe == base["python_probe"], "Engine-store executable identity drift")
        base_results.append({"reference": base["reference"], "image_identity": identity,
            "python_probe": probe, "engine_store_revalidation": "PASS", "bridge_offline_consumption": "NOT_RUN"})
    save("base_transport_qualification.json", {"status": "NOT_RUN_BUILDKIT_RUNTIME_GATE_BLOCKED",
        "first_base_synthetic_build": "NOT_RUN", "all_7_bases_offline_consumable": "NOT_DETERMINED",
        "bridge_bases_qualified": 0, "engine_store_bases_revalidated": 7, "bases": base_results,
        "registry_requests": 0, "pulls": 0, "FROM_changes": 0,
        "missing_base_transport_mechanism": "NOT_DETERMINED: no docker-container BuildKit worker exists to test exact frozen references.",
        "prohibited_substitutions_used": []})
    save("output_parity_qualification.json", {"status": "NOT_RUN_BUILDKIT_RUNTIME_GATE_BLOCKED",
        "load_image_visible": "NOT_DETERMINED", "exact_tag_lookup": "NOT_RUN", "image_id_probe": "NOT_RUN",
        "frozen_identity_probe": "NOT_RUN_ON_BRIDGE_OUTPUT", "materializer_semantic_redesign": False})
    old_policy = a.loads((a.B / "evidence/v6_restricted_build_egress_qualification_v1/allowlist_policy.json").read_bytes())
    save("proxy_policy.json", {"status": "PLANNED_NOT_IMPLEMENTED_RUNTIME_GATE_BLOCKED",
        "accepted_policy": old_policy, "proxy": STEM + "-proxy", "port": 3128,
        "proxy_build_args_for_583": {"HTTP_PROXY": "http://" + STEM + "-proxy:3128",
                                    "HTTPS_PROXY": "http://" + STEM + "-proxy:3128"},
        "PIP_INDEX_URL": "https://pypi.org/simple", "network_none_build_args": [],
        "implementation_identity": None, "application_binding_qualified": False})
    save("dockerfile_transport_delta.json", {"status": "NOT_APPLIED_RUNTIME_GATE_BLOCKED",
        "planned_transport_only_line": "ARG PIP_INDEX_URL", "PIP_INDEX_URL": "https://pypi.org/simple",
        "derived_execution_dockerfile_identities": "NOT_CREATED", "frozen_recipe_bytes_changed": False,
        "execution_dockerfiles_changed": False, "byte_identical_equivalence_claimed": False,
        "setup_action_order_changed": False, "synthetic_RUN_application_proof": "NOT_RUN"})
    save("network_qualification.json", {"status": "NOT_RUN_BUILDKIT_RUNTIME_GATE_BLOCKED",
        "approved_origins": {"pypi.org:443": "NOT_RUN", "files.pythonhosted.org:443": "NOT_RUN"},
        "approved_origins_pass": 0, "positive": "0/2_NOT_RUN", "live_qualification_requests": 0,
        "CONNECT_parser_rejections": "NOT_RUN", "deny_before_DNS": "NOT_RUN",
        "external_only_fixture_direct_access": "NOT_RUN", "RUN_default_reaches_proxy": "NOT_RUN",
        "RUN_none_proxy_unreachable": "NOT_RUN", "direct_egress": "NOT_QUALIFIED", "proxy_logs": None})
    save("runtime_integration_diff.json", {"status": "NOT_APPLIED_FULL_QUALIFICATION_REQUIRED",
        "files_changed": [], "accepted_69_file_hashes_before": original,
        "allowed_future_delta": ["explicit dedicated builder", "buildx build", "--load",
            "HTTP_PROXY and HTTPS_PROXY predefined args for 583", "exact PIP_INDEX_URL ARG binding",
            "enforcement identity check"], "real_dispatch": "REJECT", "shared_materializer_modified": False})
    after = snapshot("after")
    save("docker_state_after.json", after)
    a.require(before == after, "observed Docker/global state drift")
    a.require(preserved_files()[0] == original, "accepted package drift")
    a.require(sha((ROOT / ".git/index").read_bytes()) == index_sha, "Git index bytes drift")
    for key in ("claims", "terminals", "locks"):
        path = a.OUTPUT_ROOT / "ledger" / key
        a.require(path.is_dir() and not list(path.iterdir()), "real ledger not empty: " + key)
    real_paths = {name: (a.OUTPUT_ROOT / name).exists() for name in ("attempts", "snapshots")}
    a.require(not any(real_paths.values()), "real attempt output appeared")
    save("attempt_state_observations.json", {"real_ledger_claims": [], "real_ledger_terminals": [],
        "real_ledger_locks": [], "real_output_paths_present": real_paths,
        "case_count": 433, "all_cases_unstarted": all(x["phase"] == "NOT_STARTED"
            and x["attempt_consumed"] is False for x in descriptor["projection"]["case_states"]),
        "event_count": descriptor["event_count"], "event_3_created": False,
        "canonical_descriptor_sha256": sha((a.B / "v6_current_state.json").read_bytes())})
    save("global_state_preservation.json", {"observed_surfaces_unchanged": True,
        "default_builder_unchanged": True, "buildx_selection_configuration_hashes_unchanged": True,
        "networks_containers_images_volumes_unchanged": True, "default_bridge_inspect_unchanged": True,
        "readable_config_hashes_unchanged": True, "application_firewall_observation_unchanged": True,
        "limitations": ["PF runtime rules unreadable without privileged PF access",
            "Docker VM daemon configuration not directly readable", "Hash/snapshot comparison covers observed surfaces only"],
        "daemon_restart": False, "third_party_install": False, "host_firewall_mutation": False})
    save("cleanup_verification.json", {"status": "PASS", "builder_created": False,
        "networks_proxy_external_fixture_created": False, "qualification_builds_or_images_created": False,
        "base_identity_probe_containers": {"created": 7, "removed_by_rm": 7},
        "owned_transient_objects_remaining": [], "unrelated_objects_removed": [],
        "before_after_state_equal": True, "persistent_evidence_retained": True})
    bindings = {name: sha((OUT / name).read_bytes()) for name in (
        "builder_runtime_identity.json", "builder_configuration.json", "base_transport_qualification.json",
        "output_parity_qualification.json", "network_qualification.json")}
    save("bridge_identity.json", {"status": STATUS, "bridge_architecture": "NOT_QUALIFIED",
        "semantic_enforcement_identity": None, "semantic_enforcement_sha256": None,
        "operational_builder_identity": None, "qualification_observation_identity": bindings,
        "qualification_observation_sha256": a.identity(bindings), "real_attempts": 0,
        "next_gate": "HUMAN_PI_DECIDE_V6_LOCAL_BUILDKIT_RUNTIME_PROVISIONING"})
    save("commands_run.json", {"scope": "NO_BUILD_NO_BOOTSTRAP_NO_PULL; seven Engine-store identity containers only",
        "commands": COMMANDS, "secrets_persisted": False})
    print(json.dumps({"status": STATUS, "accepted_files": 69, "scope": "641/583/58",
        "engine_bases": 7, "bridge_bases_qualified": 0, "builder_created": False, "real_attempts": 0}))


if __name__ == "__main__":
    main()

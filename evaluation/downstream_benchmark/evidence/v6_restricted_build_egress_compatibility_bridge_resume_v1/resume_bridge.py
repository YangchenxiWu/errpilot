"""Phased fixture-only bridge resume; fail closed at the first base gate.

No acquisition, benchmark dispatch, scientific identity change or Git mutation.
The running driver container is created with --pull=never so Buildx bootstrap
does not enter its image-acquisition path. This is runtime startup only, never
an Engine-to-BuildKit base import mechanism.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
B = ROOT / "evaluation/downstream_benchmark"
E = B / "evidence"
EXTERNAL = Path("/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1")
Q = EXTERNAL / "qualification/restricted_build_egress_compatibility_bridge_resume_v1"
HEAD = "5c007fbfbfc5b3529105a14f87127f50e1eab6d7"
CANONICAL = "6a9028c79aa62f90db2b2d53def32ab23bffcfa3c71d2ec30d7fa64e741e3aae"
BUILDER = "errpilot-v6-builder-42393faa3385-v1"
STEM = "errpilot-v6-egress-42393faa3385-v1"
INTERNAL = STEM + "-internal"
CONTAINER = "buildx_buildkit_" + BUILDER + "0"
VOLUME = CONTAINER + "_state"
OWNER = "errpilot.v6.qualification=restricted_build_egress_compatibility_bridge_resume_v1"
REQUEST = Path("/Users/wuyangchenxi/.codex/attachments/d1505d47-6152-4eac-8942-2271df06d201/已粘贴的文本.txt")
BLOCK = "V6_RESTRICTED_BUILD_EGRESS_BRIDGE_BASE_IMAGE_TRANSPORT_BLOCKED"
NEXT = "HUMAN_PI_DECIDE_V6_BUILDKIT_FROZEN_BASE_TRANSPORT_BRIDGE"
PACKAGES = [("v6_preparation_execution_activation_v1", 14),
            ("v6_preparation_execution_runtime_implementation_v1", 26),
            ("v6_restricted_build_egress_qualification_v1", 29),
            ("v6_restricted_build_egress_compatibility_bridge_v1", 32),
            ("v6_local_buildkit_runtime_provisioning_v1", 23)]
sys.path.insert(0, str(ROOT))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2,
                       allow_nan=False) + "\n").encode()


def now():
    return datetime.now(timezone.utc).isoformat()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def durable(path, raw, *, update=False):
    require(not path.is_symlink(), "symlink output forbidden")
    with path.open("wb" if update else "xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    require(path.read_bytes() == raw, "write readback failed")


def save(name, value):
    durable(OUT / name, encoded(value))


def load(name):
    return json.loads((OUT / name).read_bytes())


def command(name, argv, *, check=True, raw=True, timeout=55):
    if argv[0] == "git":
        require(argv[1] in {"rev-parse", "branch", "diff", "ls-files", "ls-remote"},
                "Git mutation forbidden")
    if argv[0] == "docker":
        require("pull" not in argv and "--use" not in argv and "--network=host" not in argv,
                "pull/global builder/host network forbidden")
        require(argv[1] not in {"system", "builder"}, "global Docker mutation forbidden")
    started = now()
    try:
        result = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=timeout,
                                check=False)
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        result = subprocess.CompletedProcess(argv, 124, exc.stdout or b"", exc.stderr or b"")
        timed_out = True
    rec = {"name": name, "argv": argv, "started_at_utc": started,
           "finished_at_utc": now(), "exit_code": result.returncode,
           "timed_out": timed_out, "stdout_sha256": sha(result.stdout),
           "stderr_sha256": sha(result.stderr)}
    if raw:
        rec.update(stdout=result.stdout.decode(errors="replace"),
                   stderr=result.stderr.decode(errors="replace"))
    path = OUT / "commands_run.json"
    prior = json.loads(path.read_bytes()) if path.exists() else []
    durable(path, encoded(prior + [rec]), update=path.exists())
    if check:
        require(result.returncode == 0, "command failed: " + name)
    return result, rec


def checked(name, argv, **kwargs):
    return command(name, argv, **kwargs)[0].stdout


def inventory(root, *, exclude=None):
    require(root.is_dir() and not root.is_symlink(), "inventory root unavailable")
    result = {}
    for directory, dirs, names in os.walk(root, followlinks=False):
        if exclude and Path(directory) == exclude.parent:
            dirs[:] = [d for d in dirs if Path(directory) / d != exclude]
        for name in sorted(dirs + names):
            p = Path(directory) / name
            rel = str(p.relative_to(root))
            if p.is_symlink():
                target = os.readlink(os.fsencode(p))
                result[rel] = {"type": "symlink", "target_b64": base64.b64encode(target).decode(),
                               "sha256": sha(target)}
            elif p.is_file():
                raw = p.read_bytes()
                result[rel] = {"type": "file", "bytes": len(raw), "sha256": sha(raw)}
    return result


def preserved():
    files, packages = {}, []
    for package, count in PACKAGES:
        path = E / package / "artifact_sha256.json"
        d = json.loads(path.read_bytes())
        require(len(d["artifacts"]) + 1 == count, "prior manifest count drift")
        for rel, expected in d["artifacts"].items():
            require(sha((ROOT / rel).read_bytes()) == expected, "prior bytes drift: " + rel)
            files[rel] = expected
        rel = str(path.relative_to(ROOT))
        files[rel] = sha(path.read_bytes())
        packages.append({"package": package, "files": count, "manifest_sha256": files[rel]})
    require(len(files) == 124, "combined prior manifest drift")
    return files, packages


def prior_external_checks():
    checks = []
    path = E / PACKAGES[1][0] / "external_artifact_sha256.json"
    d = json.loads(path.read_bytes())
    all_external = inventory(EXTERNAL)
    for item in d["artifacts"]:
        require(all_external[item["relative_path"]]["sha256"] ==
                item.get("sha256", item.get("target_bytes_sha256")),
                "runtime external artifact drift")
    checks.append({"manifest": str(path.relative_to(ROOT)), "checked": len(d["artifacts"])})
    for package, _ in PACKAGES[2:]:
        path = E / package / "external_evidence_manifest.json"
        d = json.loads(path.read_bytes())
        root = Path(d["root"])
        items = d.get("artifact_inventory", d.get("artifacts"))
        actual = inventory(root)
        require(set(actual) == set(items) | {"artifact_sha256.json"}, "prior external inventory drift")
        for rel, item in items.items():
            require(actual[rel]["sha256"] == item["sha256"], "prior external bytes drift")
        expected = d.get("manifest_sha256", d.get("external_manifest_sha256"))
        require(sha((root / "artifact_sha256.json").read_bytes()) == expected,
                "prior external manifest drift")
        checks.append({"manifest": str(path.relative_to(ROOT)), "checked": len(actual)})
    return checks


def config_hashes():
    result = {}
    for name in ["/etc/pf.conf", "/etc/docker/daemon.json", "/Users/wuyangchenxi/.docker/daemon.json",
                 "/Users/wuyangchenxi/.docker/config.json",
                 "/Users/wuyangchenxi/Library/Group Containers/group.com.docker/settings-store.json"]:
        try:
            result[name] = {"status": "READABLE", "sha256": sha(Path(name).read_bytes())}
        except FileNotFoundError:
            result[name] = {"status": "ABSENT"}
        except PermissionError:
            result[name] = {"status": "UNREADABLE"}
    return result


def snapshot(label):
    result = {"configuration_file_hashes": config_hashes()}
    for kind, listing, inspect in [
        ("networks", ["docker", "network", "ls", "-q"], ["docker", "network", "inspect"]),
        ("containers", ["docker", "ps", "-aq", "--no-trunc"], ["docker", "inspect"]),
        ("volumes", ["docker", "volume", "ls", "-q"], ["docker", "volume", "inspect"])]:
        ids = sorted(checked(label + "_" + kind + "_ids", listing).decode().split())
        rows = json.loads(checked(label + "_" + kind, inspect + ids, raw=False)) if ids else []
        if kind == "containers":
            rows = [{k: row.get(k) for k in ["Id", "Name", "Image", "State", "NetworkSettings"]}
                    for row in rows]
        result[kind] = rows
    result["images"] = sorted(checked(label + "_images", ["docker", "image", "ls", "-a",
        "--no-trunc", "--digests", "--format", "{{.ID}}|{{.Repository}}|{{.Tag}}|{{.Digest}}"]
        ).decode().splitlines())
    result["selected_builder"] = checked(label + "_selected", ["docker", "buildx", "inspect"]).decode()
    base = Path("/Users/wuyangchenxi/.docker/buildx")
    result["buildx_selection_configuration_hashes"] = {str(p.relative_to(base)): sha(p.read_bytes())
        for p in sorted(base.rglob("*")) if p.is_file() and not p.is_symlink()
        and (p.name in {"current", "defaults"} or "instances" in p.relative_to(base).parts)}
    for key, argv in [
        ("application_firewall", ["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"]),
        ("pf_rules", ["/sbin/pfctl", "-sr"])]:
        _, rec = command(label + "_" + key, argv, check=False)
        result[key] = {k: rec[k] for k in ["exit_code", "stdout_sha256", "stderr_sha256"]}
    return result


def attempt_state():
    d = json.loads((B / "v6_current_state.json").read_bytes())
    rows = d["projection"]["case_states"]
    result = {"canonical_sha256": sha((B / "v6_current_state.json").read_bytes()),
        "event_count": d["event_count"], "case_count": len(rows),
        "real_attempts_consumed": sum(bool(x["attempt_consumed"]) for x in rows),
        "environment_ready_cases": sum(x["environment_identity"] is not None for x in rows)}
    for name in ["claims", "terminals", "locks"]:
        path = EXTERNAL / "ledger" / name
        result["real_ledger_" + name] = sorted(p.name for p in path.iterdir()) if path.exists() else []
    result["real_output_paths_present"] = {n: (EXTERNAL / n).exists()
        for n in ["attempts", "snapshots", "inputs"]}
    require(result["real_attempts_consumed"] == result["environment_ready_cases"] == 0 and
            not any(result["real_ledger_" + n] for n in ["claims", "terminals", "locks"]) and
            not any(result["real_output_paths_present"].values()), "real attempt/output appeared")
    return result


def git_state(label):
    head = checked(label + "_head", ["git", "rev-parse", "HEAD"]).decode().strip()
    branch = checked(label + "_branch", ["git", "branch", "--show-current"]).decode().strip()
    require((head, branch) == (HEAD, "main"), "HEAD/branch drift")
    checked(label + "_tracked", ["git", "diff", "--exit-code"])
    checked(label + "_index", ["git", "diff", "--cached", "--exit-code"])
    live = checked(label + "_live", ["git", "ls-remote", "--exit-code", "origin", "refs/heads/main"])
    require(live.decode().split() == [HEAD, "refs/heads/main"], "LIVE origin drift")
    require(sha((B / "v6_current_state.json").read_bytes()) == CANONICAL, "canonical drift")
    return {"head": head, "branch": branch, "live_origin_main": HEAD,
            "canonical_sha256": CANONICAL, "index_sha256": sha((ROOT / ".git/index").read_bytes()),
            "tracked_worktree": "CLEAN", "tracked_index": "CLEAN"}


def runtime_verify(label):
    binding = json.loads((E / PACKAGES[4][0] / "future_builder_binding.json").read_bytes())
    frozen = json.loads((E / PACKAGES[4][0] / "immutable_runtime_identity.json").read_bytes())
    ref = binding["driver_options"]["image"]
    require(ref == frozen["immutable_pull_reference"] and "@sha256:" in ref,
            "immutable future binding mismatch")
    row = json.loads(checked(label + "_runtime_platform", ["docker", "image", "inspect",
        "--platform=linux/amd64", ref], raw=False))[0]
    store = json.loads(checked(label + "_runtime_store", ["docker", "image", "inspect", ref], raw=False))[0]
    require(row["Id"] == frozen["linux_amd64_manifest_digest"] and
        (row["Os"], row["Architecture"]) == ("linux", "amd64") and
        store["Id"] == frozen["top_level_digest"] and ref in row["RepoDigests"] and
        row["RootFS"]["Layers"] == frozen["rootfs_diff_ids"], "runtime digest/platform drift")
    # Local export only. No extract, load, import, registry or base transport.
    with tempfile.TemporaryFile() as stream:
        argv = ["docker", "image", "save", "--platform=linux/amd64", ref]
        proc = subprocess.run(argv, cwd=ROOT, stdout=stream, stderr=subprocess.PIPE, timeout=55)
        require(proc.returncode == 0, "local runtime config export failed")
        stream.seek(0)
        archive_sha = hashlib.file_digest(stream, "sha256").hexdigest()
        stream.seek(0)
        with tarfile.open(fileobj=stream, mode="r") as archive:
            member = "blobs/sha256/" + frozen["config_digest"].split(":")[1]
            config = archive.extractfile(member).read()
        require("sha256:" + sha(config) == frozen["config_digest"], "local config mismatch")
    return {"status": "EXACT_AND_LOCAL", "LOCAL_PRESENT": "YES", "no_additional_pull_required": True,
        "immutable_reference": ref, "platform": "linux/amd64", "engine_store_id": store["Id"],
        "platform_manifest_id": row["Id"], "verified_config_digest": "sha256:" + sha(config),
        "RootFS": row["RootFS"], "local_save_argv": argv, "archive_sha256": archive_sha,
        "save_stderr_sha256": sha(proc.stderr), "archive_retained": False,
        "local_export_is_not_a_base_import": True}


def entry():
    require(not (OUT / "entry_verification.json").exists(), "entry already executed")
    files, packages = preserved()
    own = str(OUT.relative_to(ROOT)) + "/"
    untracked = set(checked("entry_untracked", ["git", "ls-files", "--others", "--exclude-standard"])
                    .decode().splitlines())
    require({x for x in untracked if not x.startswith(own)} == set(files), "unrelated untracked paths")
    external_checks = prior_external_checks()
    require(not Q.exists() and not Q.is_symlink(), "continuation external namespace collision")
    g = git_state("entry")
    from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a
    from evaluation.downstream_benchmark.screening import v6_preparation_runtime as r
    descriptor, manifest = a.load_inputs()
    population = r.population()
    require(a.derive_population(manifest) == population, "frozen population mismatch")
    scope = json.loads((E / PACKAGES[3][0] / "work_item_scope.json").read_bytes())
    restricted = [x["base_attempt_id"] for x in population["items"] if x["build_network_required"]]
    none = [x["base_attempt_id"] for x in population["items"] if not x["build_network_required"]]
    require(restricted == scope["restricted_work_item_ids"] and none == scope["network_none_work_item_ids"]
            and (len(population["items"]), len(restricted), len(none)) == (641, 583, 58), "scope drift")
    save("entry_verification.json", {"status": "PASS", **g, "packages": packages,
        "prior_file_hashes": files, "combined_prior_untracked_count": 124,
        "exact_prior_manifest_equality": True, "unrelated_untracked_paths": [],
        "airos_current_state": "ABSENT", "airos_contracts": "ABSENT",
        "prewrite_manifest_verification": "PASS_INLINE_BEFORE_EXECUTOR_CREATION",
        "lifecycle_label": descriptor["lifecycle_label"], "event_count": descriptor["event_count"],
        "phase_authorizations": descriptor["projection"]["phase_authorizations"],
        "PREPARATION_AUTHORIZED": descriptor["projection"]["lifecycle"]["PREPARATION_AUTHORIZED"],
        "attempt_state": attempt_state(), "prior_external_manifest_checks": external_checks,
        "observed_at_utc": now()})
    save("work_item_scope.json", scope)
    save("prior_external_inventory.json", inventory(EXTERNAL))
    raw = REQUEST.read_bytes()
    lineage = {}
    for pkg, names in [(PACKAGES[2][0], ["RUN_REPORT.md", "compatibility_analysis.json"]),
                       (PACKAGES[3][0], ["RUN_REPORT.md", "accepted_decision.json"]),
                       (PACKAGES[4][0], ["RUN_REPORT.md", "future_builder_binding.json"] )]:
        for name in names:
            p = E / pkg / name
            lineage[str(p.relative_to(ROOT))] = sha(p.read_bytes())
    save("resume_lineage.json", {"authority": "RESUME_V6_RESTRICTED_BUILD_EGRESS_COMPATIBILITY_BRIDGE_FROM_RUNTIME_GATE",
        "accepted_bridge_decision": "ADOPT_V6_DEDICATED_DOCKER_CONTAINER_BUILDER_COMPATIBILITY_BRIDGE_V1",
        "architecture_adjudication_reopened": False, "lineage": lineage,
        "request_path": str(REQUEST), "request_sha256": sha(raw), "exact_request": raw.decode(),
        "real_benchmark_preparation_authorized": False})
    runtime = runtime_verify("entry")
    save("builder_runtime_verification.json", runtime)
    before = snapshot("before")
    save("docker_state_before.json", before)
    names = {INTERNAL, STEM + "-external", STEM + "-proxy", STEM + "-fixture", CONTAINER, VOLUME}
    require(not any(x["Name"] in names for x in before["networks"] + before["volumes"]),
            "matching network/volume collision")
    require(not any(x["Name"].lstrip("/") in names for x in before["containers"]), "matching container collision")
    absent, _ = command("dedicated_builder_absence", ["docker", "buildx", "inspect", BUILDER], check=False)
    require(absent.returncode != 0 and b"no builder" in absent.stderr.lower(), "builder absence underdetermined")
    save("builder_configuration.json", {"name": BUILDER, "driver": "docker-container",
        "scope": "DEDICATED_ERRPILOT_V6_ONLY", "driver_options": {"network": INTERNAL,
            "image": runtime["immutable_reference"]}, "buildkitd_flags": ["--debug"],
        "global_use": False, "explicit_load": True, "RUN_network_semantics": {"restricted": "default", "none": "none"},
        "container": CONTAINER, "state_volume": VOLUME, "ownership_label": OWNER,
        "startup": "EXACT_LOCAL_DOCKER_CREATE_PULL_NEVER_THEN_BUILDX_BOOTSTRAP_EXISTING_RUNNING_CONTAINER",
        "DNS": "127.0.0.1; prevents Docker embedded DNS forwarding live registry lookups",
        "network_host_entitlement_requested_by_executor": False,
        "effective_worker_network_and_entitlements": "REQUIRE_OBSERVATION; NOT_ASSUMED_FROM_DRIVER_METADATA"})
    print("ENTRY PASS: 124 exact prior files, 641/583/58, exact local BuildKit config/platform", flush=True)


def create():
    require(load("entry_verification.json")["status"] == "PASS", "entry gate missing")
    cfg = load("builder_configuration.json")
    # Revalidate immediately before the first Docker mutation.
    require(runtime_verify("precreate") == load("builder_runtime_verification.json"), "runtime changed before create")
    netid = checked("create_internal", ["docker", "network", "create", "--internal", "--driver=bridge",
        "--label", OWNER, INTERNAL]).decode().strip()
    row = json.loads(checked("inspect_internal", ["docker", "network", "inspect", netid]))[0]
    require(row["Internal"] is True and row["Name"] == INTERNAL and row["Labels"].get(OWNER.split("=")[0]) == OWNER.split("=")[1],
            "internal network semantics/ownership mismatch")
    save("internal_network_verification.json", {"network_id": netid, "driver": row["Driver"],
        "scope": row["Scope"], "IPAM": row["IPAM"], "options": row["Options"], "labels": row["Labels"],
        "Internal": row["Internal"], "inspect_json_sha256": sha(encoded(row)), "inspect": row})
    binding = json.loads((E / PACKAGES[4][0] / "future_builder_binding.json").read_bytes())
    checked("create_dedicated_builder", binding["future_create_argv_not_executed"] + ["--buildkitd-flags=--debug"])
    checked("create_owned_state_volume", ["docker", "volume", "create", "--label", OWNER, VOLUME])
    checked("create_runtime_without_pull", ["docker", "create", "--pull=never", "--platform=linux/amd64",
        "--name", CONTAINER, "--privileged", "--network=" + INTERNAL, "--dns=127.0.0.1",
        "--label", OWNER, "--mount", "type=volume,src=" + VOLUME + ",dst=/var/lib/buildkit",
        cfg["driver_options"]["image"], "--debug"])
    checked("start_exact_runtime", ["docker", "start", CONTAINER])
    observe()


def observe():
    cfg = load("builder_configuration.json")
    netid = load("internal_network_verification.json")["network_id"]
    result, rec = command("bootstrap_existing_runtime", ["docker", "buildx", "inspect", "--bootstrap", BUILDER])
    require("pulling image" not in (rec["stdout"] + rec["stderr"]).lower(), "bootstrap entered image acquisition")
    inspect_raw = checked("builder_container_inspect", ["docker", "inspect", CONTAINER])
    row = json.loads(inspect_raw)[0]
    networks = row["NetworkSettings"]["Networks"]
    runtime = load("builder_runtime_verification.json")
    require(set(networks) == {INTERNAL} and networks[INTERNAL]["NetworkID"] == netid,
            "builder attached to wrong/extra network")
    require(row["Config"]["Image"] == runtime["immutable_reference"] and row["Image"] in
        {runtime["platform_manifest_id"], runtime["engine_store_id"], runtime["verified_config_digest"]}, "wrong runtime image")
    info = checked("builder_buildx_inspect", ["docker", "buildx", "inspect", BUILDER]).decode()
    require(re.search(r"^Driver:\s+docker-container$", info, re.M), "wrong builder driver")
    require(re.search(r"^Status:\s+running$", info, re.M) and
            not re.search(r"^Error:", info, re.M), "builder workers not ready")
    version = checked("runtime_buildkit_version", ["docker", "exec", CONTAINER, "buildkitd", "--version"]).decode().strip()
    routes = checked("builder_routes_interfaces", ["docker", "exec", CONTAINER, "sh", "-c",
        "ip addr; ip route; cat /proc/net/route; cat /etc/resolv.conf"]).decode()
    routes4 = checked("builder_ipv4_routes", ["docker", "exec", CONTAINER, "ip", "route"]).decode()
    require(not re.search(r"^default\s", routes4, re.M), "builder has default Internet route")
    save("builder_creation_observation.json", {"status": "PASS_DRIVER_RUNTIME_INTERNAL_NETWORK",
        "builder": info, "container_inspect": row, "container_inspect_stdout_sha256": sha(inspect_raw),
        "runtime_version": version, "routes_interfaces": routes, "network_attachments": networks,
        "ordinary_ipv4_default_route": False, "runtime_pull": False, "bootstrap_observation": rec})
    save("docker_versions.json", {"docker": checked("docker_version", ["docker", "version"]).decode(),
        "buildx": checked("buildx_version", ["docker", "buildx", "version"]).decode()})
    print("BUILDER PASS: exact immutable runtime, internal-only network, no default route, no pull", flush=True)


def first():
    require(load("builder_creation_observation.json")["status"] == "PASS_DRIVER_RUNTIME_INTERNAL_NETWORK",
            "builder gate missing")
    require(not Q.exists() and not Q.is_symlink(), "external qualification namespace already exists")
    Q.mkdir()
    context = Q / "first-base-context"
    context.mkdir()
    bases = json.loads((E / PACKAGES[1][0] / "base_runtime_local_status.json").read_bytes())["bases"]
    base = bases[0]  # Mechanical: first entry in the accepted ordered seven-base ledger.
    row = json.loads(checked("first_base_engine_store", ["docker", "image", "inspect", base["reference"]]))[0]
    require({k: row[k] for k in base["image_identity"]} == base["image_identity"], "first frozen base drift")
    dockerfile = ("FROM " + base["reference"] + "\nRUN python --version\n").encode()
    durable(context / "Dockerfile", dockerfile)
    tag = STEM + "-resume-first-base:qualification"
    absent, _ = command("qualification_output_tag_absent", ["docker", "image", "inspect", tag], check=False)
    require(absent.returncode != 0 and b"No such image" in absent.stderr, "output tag collision")
    started = now()
    argv = ["docker", "buildx", "build", "--builder=" + BUILDER, "--platform=linux/amd64",
            "--network=none", "--pull=false", "--progress=plain", "--no-cache", "--load",
            "-t", tag, "-f", str(context / "Dockerfile"), str(context)]
    result, rec = command("first_frozen_base_offline_build", argv, check=False, timeout=45)
    durable(Q / "first_base.stdout.txt", result.stdout)
    durable(Q / "first_base.stderr.txt", result.stderr)
    log = checked("builder_logs_after_first_base", ["docker", "logs", "--timestamps", CONTAINER])
    # Docker logs writes BuildKit stderr to the client's stderr; retain both.
    logrec = load("commands_run.json")[-1]
    durable(Q / "builder.stdout.log", log)
    durable(Q / "builder.stderr.log", logrec["stderr"].encode())
    finished = now()
    events, eventrec = command("first_base_docker_events", ["docker", "events", "--since", started,
        "--until", finished, "--format={{json .}}"], check=False)
    durable(Q / "docker_events.jsonl", events.stdout)
    text = (result.stdout + result.stderr).decode(errors="replace")
    status = "PASS" if result.returncode == 0 else BLOCK
    record = {"status": status, "selected_base_rule": "FIRST_IN_ACCEPTED_ORDERED_SEVEN_BASE_LEDGER",
        "accepted_base_ledger_sha256": sha((E / PACKAGES[1][0] / "base_runtime_local_status.json").read_bytes()),
        "exact_reference": base["reference"], "expected_python_patch": base["python_version"],
        "engine_store_identity": base["image_identity"], "engine_store_present": True,
        "BuildKit_consumption": "PASS" if result.returncode == 0 else "FAILED_BEFORE_RUN",
        "resulting_qualification_image_identity": None, "Dockerfile": dockerfile.decode(),
        "Dockerfile_sha256": sha(dockerfile), "context": str(context), "benchmark_context": False,
        "argv": argv, "exit_code": result.returncode, "timed_out": rec["timed_out"],
        "stdout_sha256": sha(result.stdout), "stderr_sha256": sha(result.stderr),
        "stdout": rec["stdout"], "stderr": rec["stderr"], "builder_log_binding": {
            "stdout_sha256": sha(log), "stderr_sha256": logrec["stderr_sha256"]},
        "network_observation": {"builder_internal_only": True, "default_route": False,
            "RUN_network": "none", "upstream_DNS": "CONTAINER_LOOPBACK_ONLY",
            "proxy_present": False, "event_command_exit_code": eventrec["exit_code"]},
        "registry_resolution_attempted_by_BuildKit": "registry-1.docker.io" in text or "auth.docker.io" in text,
        "registry_response_or_base_layer_download_observed": False,
        "FROM_rewrite": False, "retagging": False, "local_registry": False,
        "OCI_layout_import": False, "alternate_reference": False,
        "missing_transport": "No demonstrated path from Engine-local frozen base to the isolated docker-container BuildKit content store",
        "next_gate": NEXT if status == BLOCK else "ALL_SEVEN_BASE_GATE"}
    save("first_base_transport_qualification.json", record)
    print(json.dumps({k: record[k] for k in ["status", "exact_reference", "exit_code", "stderr", "next_gate"]}), flush=True)
    if result.returncode == 0:
        raise RuntimeError("FIRST_BASE_PASSED: continue authorized all-seven gate; blocked finalizer is not applicable")
    require(record["registry_resolution_attempted_by_BuildKit"], "unexpected first-base failure requires generic BLOCKED adjudication")
    for name, details in {
        "all_base_transport_qualification.json": {"required_bases": 7, "attempted": 1, "passed": 0,
            "remaining_six": "NOT_RUN_FIRST_BASE_HARD_GATE", "all_seven_offline_consumable": "NO"},
        "output_parity_qualification.json": {"explicit_load_requested": True, "output_parity": "NOT_QUALIFIED"},
        "proxy_implementation_status.json": {"implementation_written": False, "proxy_created": False},
        "proxy_runtime_identity.json": {"runtime_identity": None, "proxy_created": False},
        "application_binding.json": {"binding": "NOT_RUN", "Dockerfile_transport_delta": None},
        "positive_qualification.json": {"approved_origins_passed": 0, "executed": False},
        "negative_qualification.json": {"direct_egress_local_fixture": "NOT_RUN", "executed": False},
        "network_enforcement_identity.json": {"semantic_enforcement_identity": None,
            "qualification_observation_identity": None, "ENFORCEMENT_IDENTITY": "ABSENT"},
        "runtime_integration_diff.json": {"files_changed": [], "production_runtime_delta": "NONE",
            "integration_executed": False},
        "rejection_matrix.json": {"focused_runtime_integration_tests": "NOT_RUN",
            "reason": "First-base failure requires immediate stop; no integration candidate exists"},
    }.items():
        save(name, {"status": "NOT_RUN_BASE_TRANSPORT_HARD_GATE", **details})
    # Durably preserve exact qualification observations before any cleanup.
    copied = {}
    for p in sorted(OUT.iterdir()):
        if p.is_file():
            durable(Q / p.name, p.read_bytes())
            copied[p.name] = {"sha256": sha(p.read_bytes()), "bytes": p.stat().st_size}
    durable(Q / "precleanup_evidence_manifest.json", encoded({"repository_copies": copied,
        "qualification_files": inventory(Q), "persisted_before_cleanup": True,
        "status": BLOCK, "benchmark_attempt_id": None}))
    save("precleanup_evidence_receipt.json", {"root": str(Q), "durable": True,
        "manifest_sha256": sha((Q / "precleanup_evidence_manifest.json").read_bytes()),
        "first_base_status": BLOCK, "no_dependent_qualification_executed": True})


def cleanup():
    require(load("first_base_transport_qualification.json")["status"] == BLOCK and
        load("precleanup_evidence_receipt.json")["durable"], "blocked evidence not yet persisted")
    before = load("docker_state_before.json")
    require(CONTAINER not in {x["Name"].lstrip("/") for x in before["containers"]}, "container not owned")
    row = json.loads(checked("cleanup_owned_container", ["docker", "inspect", CONTAINER]))[0]
    key, value = OWNER.split("=", 1)
    require(row["Config"]["Labels"].get(key) == value, "container ownership mismatch")
    volume = json.loads(checked("cleanup_owned_volume", ["docker", "volume", "inspect", VOLUME]))[0]
    net = json.loads(checked("cleanup_owned_network", ["docker", "network", "inspect", INTERNAL]))[0]
    require(volume["Labels"].get(key) == net["Labels"].get(key) == value,
            "network/volume ownership mismatch")
    require(net["Id"] == load("internal_network_verification.json")["network_id"], "network ID drift")
    require(set(net["Containers"]) == {row["Id"]}, "unrelated container on dedicated network")
    checked("remove_owned_builder", ["docker", "buildx", "rm", "--force", BUILDER])
    remains, _ = command("owned_container_remaining", ["docker", "inspect", CONTAINER], check=False)
    if remains.returncode == 0:
        checked("remove_owned_container", ["docker", "rm", "--force", CONTAINER])
    remains, _ = command("owned_volume_remaining", ["docker", "volume", "inspect", VOLUME], check=False)
    if remains.returncode == 0:
        checked("remove_owned_volume", ["docker", "volume", "rm", VOLUME])
    checked("remove_owned_internal_network", ["docker", "network", "rm", INTERNAL])
    after = snapshot("after")
    save("docker_state_after.json", after)
    checks = {key + "_unchanged": before[key] == after[key] for key in before}
    require(all(checks.values()), "observable global state delta after cleanup: " + str(checks))
    save("global_state_preservation.json", {"status": "PASS_OBSERVABLE_SURFACES", **checks,
        "daemon_restart": False, "third_party_install": False, "host_firewall_mutation": False,
        "limitations": ["PF rules may be unreadable; no claim about unobserved PF runtime internals",
            "Docker VM daemon configuration not directly readable", "Snapshot comparison does not rule out concurrent activity"]})
    remaining_builder, _ = command("cleanup_builder_absence", ["docker", "buildx", "inspect", BUILDER], check=False)
    require(remaining_builder.returncode != 0 and b"no builder" in remaining_builder.stderr.lower(), "builder remains")
    verify = runtime_verify("after_cleanup")
    require(verify == load("builder_runtime_verification.json"), "runtime changed during cleanup")
    bases = json.loads((E / PACKAGES[1][0] / "base_runtime_local_status.json").read_bytes())["bases"]
    for base in bases:
        row = json.loads(checked("cleanup_base_" + base["python_version"],
            ["docker", "image", "inspect", base["reference"]], raw=False))[0]
        require({k: row[k] for k in base["image_identity"]} == base["image_identity"], "frozen base changed")
    save("cleanup_verification.json", {"status": "PASS", "evidence_persisted_before_cleanup": True,
        "removed_transaction_owned": [BUILDER, CONTAINER, VOLUME, INTERNAL],
        "proxy_fixture_clients_external_network_created": False, "qualification_output_images_created": 0,
        "runtime_preserved": True, "seven_frozen_bases_preserved": True,
        "docker_inventory_equals_before": True, "production_must_reproduce_frozen_configuration": True})
    print("CLEANUP PASS: builder/container/state volume/internal network removed; original Docker surfaces restored", flush=True)


def finish():
    require(load("cleanup_verification.json")["status"] == "PASS", "cleanup missing")
    files, _ = preserved()
    require(files == load("entry_verification.json")["prior_file_hashes"], "prior inventory changed")
    g = git_state("final")
    require(g["index_sha256"] == load("entry_verification.json")["index_sha256"], "index changed")
    require(inventory(EXTERNAL, exclude=Q) == load("prior_external_inventory.json"), "prior external inventory changed")
    require(attempt_state() == load("entry_verification.json")["attempt_state"], "real attempt state changed")
    scope = load("work_item_scope.json")
    own = str(OUT.relative_to(ROOT)) + "/"
    untracked = set(checked("final_untracked", ["git", "ls-files", "--others", "--exclude-standard"])
        .decode().splitlines())
    require({x for x in untracked if not x.startswith(own)} == set(files), "unrelated untracked file appeared")
    save("final_verification.json", {"status": "PASS", **g, "prior_124_repository_files_exact": True,
        "prior_external_inventory_exact": True, "attempt_state": attempt_state(),
        "population_sha256": scope["population_sha256"], "total": 641, "restricted": 583, "network_none": 58,
        "all_work_item_case_plan_recipe_revision_blocker_identities_preserved": True})
    firewall = {"REAL_BENCHMARK_ATTEMPTS_CONSUMED": 0, "REAL_BENCHMARK_CLAIMS_CREATED": 0,
        "REAL_BENCHMARK_SOURCE_EXPORTS": 0, "REAL_BENCHMARK_IMAGE_BUILDS": 0,
        "BENCHMARK_DEPENDENCIES_INSTALLED": 0, "SOURCE_ACQUISITION_EXECUTED": "NO",
        "UNAPPROVED_LIVE_EGRESS_REQUESTS": 0, "ORACLE_EXECUTED": "NO", "EVENT_3_CREATED": "NO",
        "EFFECTIVE_EXECUTION_DESCRIPTOR_CREATED": "NO", "CANONICAL_CURRENT_STATE_MODIFIED": "NO",
        "PREPARATION_EXECUTION_CANONICAL_EFFECTIVE": "NO", "GIT_STAGE": "NO", "GIT_COMMIT": "NO", "GIT_PUSH": "NO",
        "fixture_only_build_invocations": 1, "runtime_pulls": 0,
        "egress_basis": "No live request command; isolated internal-only builder with no default route and loopback upstream DNS; failed local registry-resolution attempt retained"}
    save("firewall.json", firewall)
    results = {"status": BLOCK, "next_gate": NEXT, "checks": {
        "entry_124_manifest_equality": "PASS", "HEAD_live_origin_canonical_index": "PASS",
        "exact_runtime_config_platform": "PASS", "dedicated_driver_and_immutable_runtime": "PASS",
        "internal_only_builder_no_default_route": "PASS", "no_runtime_pull": "PASS",
        "first_base_offline_consumption": "FAIL", "hard_stop_dependent_gates": "PASS",
        "641_583_58_exact_identity_preservation": "PASS", "prior_evidence_unchanged": "PASS",
        "precleanup_durable_evidence": "PASS", "owned_resource_cleanup": "PASS",
        "global_observable_preservation": "PASS", "real_attempts_claims_sources_builds_zero": "PASS"},
        "runtime_integration_test_suite": "NOT_RUN_NO_INTEGRATION_AFTER_HARD_GATE",
        "no_scientific_validation_claim": True}
    save("validation_results.json", results)
    print(json.dumps({"status": BLOCK, "next_gate": NEXT, "checks": results["checks"]}), flush=True)


def publish():
    require(load("validation_results.json")["status"] == BLOCK, "final validation missing")
    final = Q / "final"
    final.mkdir()
    files = {}
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.name not in {"artifact_sha256.json", "external_evidence_manifest.json"}:
            durable(final / p.name, p.read_bytes())
            files[p.name] = {"bytes": p.stat().st_size, "sha256": sha(p.read_bytes())}
    durable(final / "artifact_sha256.json", encoded({"artifacts": files, "self_hash_excluded": True,
        "status": BLOCK, "namespace": "QUALIFICATION_ONLY_NOT_ATTEMPT"}))
    entire = inventory(Q)
    save("external_evidence_manifest.json", {"root": str(Q), "artifact_inventory": entire,
        "file_count": len(entire), "all_bytes_verified": True, "prior_external_unchanged": True,
        "benchmark_attempt_id": None, "exclusive_creation_fsync_readback": True,
        "precleanup_manifest_sha256": sha((Q / "precleanup_evidence_manifest.json").read_bytes()),
        "final_manifest_sha256": sha((final / "artifact_sha256.json").read_bytes())})
    files = {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in sorted(OUT.iterdir())
             if p.is_file() and p.name != "artifact_sha256.json"}
    save("artifact_sha256.json", {"artifacts": files, "file_count_including_manifest": len(files) + 1,
        "self_hash_excluded": True, "status": BLOCK, "prior_files_preserved": 124,
        "real_attempts": 0, "semantic_enforcement_identity": None, "next_gate": NEXT})
    print(json.dumps({"repository_files": len(files) + 1, "external_files": len(entire), "status": BLOCK}), flush=True)


if __name__ == "__main__":
    require(len(sys.argv) == 2 and sys.argv[1] in {"entry", "create", "observe", "first", "cleanup", "finish", "publish"}, "invalid phase")
    globals()[sys.argv[1]]()

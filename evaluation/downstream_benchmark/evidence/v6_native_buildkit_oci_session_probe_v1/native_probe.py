"""Single native OCI-session qualification probe; no production dispatch."""
from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import os
import re
import sys
import tarfile
from pathlib import Path, PurePosixPath

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
E = OUT.parent
PRIOR = E / "v6_buildkit_frozen_base_transport_bridge_v1"
EXTERNAL = Path("/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1")
Q = EXTERNAL / "qualification/native_buildkit_oci_session_probe_v1"
REQUEST = Path("/Users/wuyangchenxi/.codex/attachments/d3a8f330-b3c8-45c4-955e-b971d3051f0a/已粘贴的文本.txt")
spec = importlib.util.spec_from_file_location("native_probe_read_helpers", E / "v6_restricted_build_egress_compatibility_bridge_resume_v1/resume_bridge.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
h.OUT, h.Q = OUT, Q
sha, require, durable, encoded = h.sha, h.require, h.durable, h.encoded
save, load, checked, command = h.save, h.load, h.checked, h.command
BUILDER, CONTAINER, VOLUME, INTERNAL = h.BUILDER, h.CONTAINER, h.VOLUME, h.INTERNAL
OWNER = "errpilot.v6.qualification=native_buildkit_oci_session_probe_v1"
IMAGE = "moby/buildkit@sha256:cec9f139f45e93c5c69c60f8b07cfad9f43f4ef6b6a6cd917527fea5ff2e3dea"
TRANSPORT = "sha256:9a64909eb826662bbf181357566002a8621652c18e3e24e90bf43f279f97ce8a"
CONFIG = "sha256:5bf410ee7bb26f8f8fe9d7a2f9e9a05240cce0bc1bdbaee234f74f6b1b25ca94"
CPATH = "/tmp/errpilot-v6-native-oci-probe-v1"
PASS = "V6_NATIVE_BUILDKIT_OCI_SESSION_COMPATIBILITY_PROBE_PASS"
SOURCE_BLOCK = "V6_NATIVE_BUILDKIT_OCI_SESSION_SOURCE_BINDING_BLOCKED"
CONNECTION_BLOCK = "V6_NATIVE_BUILDKIT_CLIENT_SAME_DAEMON_CONNECTION_BLOCKED"
REGISTRY_BLOCK = "V6_NATIVE_BUILDKIT_OCI_SESSION_REGISTRY_DEPENDENCY_BLOCKED"
POST_BLOCK = "V6_NATIVE_BUILDKIT_OCI_SESSION_POST_SOURCE_BLOCKED"
DOCKERFILE = ('FROM errpilot_frozen_base\n'
              'RUN python -c "import sys, platform; print(\'sys.version=\' + sys.version); '
              'print(\'platform.machine()=\' + platform.machine()); '
              'print(\'sys.executable=\' + sys.executable)"\n')


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    def invalid(value):
        raise ValueError("nonfinite JSON: " + value)
    return json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=pairs, parse_constant=invalid)


def inventory(root, exclude=None):
    require(root.is_dir() and not root.is_symlink(), "inventory root absent/unsafe")
    result = {}
    for directory, dirs, names in os.walk(root, followlinks=False):
        if exclude and Path(directory) == exclude.parent:
            dirs[:] = [d for d in dirs if Path(directory) / d != exclude]
        for name in sorted(dirs + names):
            p = Path(directory) / name
            rel = str(p.relative_to(root))
            if p.is_symlink():
                target = os.readlink(os.fsencode(p))
                result[rel] = {"type": "symlink", "target_b64": base64.b64encode(target).decode(), "sha256": sha(target)}
            elif p.is_file():
                result[rel] = {"type": "file", "bytes": p.stat().st_size, "sha256": digest(p)}
    return result


def preserve_prior():
    files, packages = {}, []
    for package, count in h.PACKAGES + [("v6_restricted_build_egress_compatibility_bridge_resume_v1", 38), (PRIOR.name, 53)]:
        path = E / package / "artifact_sha256.json"
        manifest = strict_json(path.read_bytes())
        require(len(manifest["artifacts"]) + 1 == count, "prior manifest count drift")
        for rel, expected in manifest["artifacts"].items():
            require(digest(ROOT / rel) == expected, "prior bytes drift: " + rel)
            files[rel] = expected
        rel = str(path.relative_to(ROOT))
        files[rel] = digest(path)
        actual = {str(p.relative_to(ROOT)) for p in path.parent.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
        within = {x for x in manifest["artifacts"] if x.startswith(str(path.parent.relative_to(ROOT)) + "/")}
        require(actual == within | {rel}, "prior namespace inventory drift")
        packages.append({"package": package, "files": count, "manifest_sha256": files[rel]})
    require(len(files) == 215, "prior combined population drift")
    actual = checked("prior_untracked", ["git", "ls-files", "--others", "--exclude-standard"]).decode().splitlines()
    own = str(OUT.relative_to(ROOT)) + "/"
    require({p for p in actual if not p.startswith(own)} == set(files), "unrelated untracked paths")
    return files, packages


def population_state():
    from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a
    from evaluation.downstream_benchmark.screening import v6_preparation_runtime as r
    descriptor, plans = a.load_inputs()
    population = r.population()
    require(a.derive_population(plans) == population, "population derivation drift")
    scope = strict_json((PRIOR / "work_item_scope.json").read_bytes())
    restricted = [x["base_attempt_id"] for x in population["items"] if x["build_network_required"]]
    none = [x["base_attempt_id"] for x in population["items"] if not x["build_network_required"]]
    require((len(population["items"]), len(restricted), len(none)) == (641, 583, 58), "population counts drift")
    require(restricted == scope["restricted_work_item_ids"] and none == scope["network_none_work_item_ids"], "population identity/order drift")
    blockers = [p for p in plans["plans"] if p["case_id"] in {"matplotlib::1", "matplotlib::8"}]
    require(blockers == strict_json((PRIOR / "entry_verification.json").read_bytes())["blocker_plans"], "blocker bytes/semantics drift")
    require(not any(x["case_id"] in {"matplotlib::1", "matplotlib::8"} for x in population["items"]), "blocker dispatch")
    require(descriptor["projection"]["state"] == "PREPARATION_PLANNING_AUTHORIZED" and descriptor["event_count"] == 2
            and descriptor["projection"]["phase_authorizations"]["PREPARATION_EXECUTION"] == "NO", "canonical authority drift")
    return {"total": 641, "restricted": 583, "network_none": 58, "population_sha256": sha(encoded(population)),
            "blocker_plans": blockers, "attempt_state": h.attempt_state()}


def verify_layout(path, expected):
    actual = inventory(path)
    require(actual == expected and len(actual) == 13, "exact prior OCI file inventory drift")
    require(strict_json((path / "oci-layout").read_bytes()) == {"imageLayoutVersion": "1.0.0"}, "OCI layout marker")
    index = strict_json((path / "index.json").read_bytes())
    require(len(index["manifests"]) == 1 and index["manifests"][0]["digest"] == TRANSPORT, "wrong transport")
    manifest = strict_json((path / "blobs/sha256" / TRANSPORT.split(":")[1]).read_bytes())
    require(manifest["config"]["digest"] == CONFIG, "wrong config")
    for desc in [manifest["config"]] + manifest["layers"]:
        p = path / "blobs/sha256" / desc["digest"].split(":")[1]
        require("sha256:" + digest(p) == desc["digest"] and p.stat().st_size == desc["size"], "OCI descriptor drift")
    config = strict_json((path / "blobs/sha256" / CONFIG.split(":")[1]).read_bytes())
    diffids = strict_json((PRIOR / "first_base_transport_result.json").read_bytes())["rootfs_diff_ids"]
    require(config["rootfs"]["diff_ids"] == diffids == [d["digest"] for d in manifest["layers"]] and len(diffids) == 9,
            "ordered 9 rootfs diffIDs drift")
    return actual


def entry():
    require(not Q.exists() and not Q.is_symlink(), "new external namespace already exists")
    require(not (ROOT / ".airos/current_state.md").exists() and not (ROOT / ".airos/contracts").exists(), "new AIROS scope requires reading")
    files, packages = preserve_prior()
    git = h.git_state("entry")
    state = population_state()
    external = inventory(EXTERNAL)
    # Bind every prior external manifest, including historical malformed fixtures.
    extchecks = []
    for package, _ in h.PACKAGES[2:] + [("v6_restricted_build_egress_compatibility_bridge_resume_v1", 38), (PRIOR.name, 53)]:
        d = strict_json((E / package / "external_evidence_manifest.json").read_bytes())
        prefix = str(Path(d["root"]).relative_to(EXTERNAL)) + "/"
        actual = {k[len(prefix):]: v for k, v in external.items() if k.startswith(prefix)}
        expected = d.get("artifact_inventory", d.get("artifacts"))
        for rel, item in expected.items():
            normalized = {"type": "file", **item}
            if normalized["type"] == "symlink" and "target" in normalized:
                normalized["target_b64"] = base64.b64encode(os.fsencode(normalized.pop("target"))).decode()
            require(actual.get(rel) == normalized, "prior external bytes drift: " + rel)
        if "manifest_sha256" in d or "external_manifest_sha256" in d:
            require(set(actual) == set(expected) | {"artifact_sha256.json"}, "prior external set drift")
            require(actual["artifact_sha256.json"]["sha256"] == d.get("manifest_sha256", d.get("external_manifest_sha256")), "prior external seal drift")
        else:
            require(set(actual) == set(expected), "prior external exact inventory drift")
        extchecks.append({"package": package, "verified_files": len(actual)})
    d = strict_json((E / h.PACKAGES[1][0] / "external_artifact_sha256.json").read_bytes())
    for item in d["artifacts"]:
        require(external[item["relative_path"]]["sha256"] == item.get("sha256", item.get("target_bytes_sha256")), "runtime external drift")
    first = strict_json((PRIOR / "first_base_transport_result.json").read_bytes())
    construction = strict_json((PRIOR / "oci_layout_construction.json").read_bytes())
    deviation = strict_json((PRIOR / "execution_corrections.json").read_bytes())
    require(first["status"] == "V6_BUILDKIT_FROZEN_BASE_TRANSPORT_NAMED_CONTEXT_BLOCKED"
            and construction["config_bytes_exact"] and construction["rootfs_diff_ids_exact"]
            and first["archive_equivalence"] == "PASS" and deviation["fallback_condition_classification_deviation"]["contract_compliance_exception"], "prior result mismatch")
    for attempt in first["attempts"]:
        require(attempt["exit_code"] == 1 and "could not parse oci-layout reference" in attempt["stderr"]
                and "invalid reference format" in attempt["stderr"], "prior parser block mismatch")
    layout = Path(construction["local_oci_path"])
    prior_ext = strict_json((PRIOR / "external_evidence_manifest.json").read_bytes())
    prefix = str(layout.relative_to(Path(prior_ext["root"]))) + "/"
    expected_layout = {k[len(prefix):]: v for k, v in prior_ext["artifact_inventory"].items() if k.startswith(prefix)}
    require(expected_layout == first["layout_inventory"], "layout manifests disagree")
    verify_layout(layout, expected_layout)
    runtime = h.runtime_verify("entry")
    bases = strict_json((PRIOR / "frozen_base_authorities.json").read_bytes())["bases"]
    for i, base in enumerate(bases):
        row = strict_json(checked("entry_base_" + str(i), ["docker", "image", "inspect", base["reference"]], raw=False))[0]
        require({k: row[k] for k in base["image_identity"]} == base["image_identity"], "frozen base drift")
    before = h.snapshot("before")
    require(not any(x["Name"] == "/" + CONTAINER for x in before["containers"])
            and not any(x["Name"] == INTERNAL for x in before["networks"])
            and not any(x["Name"] == VOLUME for x in before["volumes"]), "owned Docker name collision")
    save("entry_verification.json", {"status": "PASS", **git, **state, "prior_file_count": len(files),
        "prior_file_hashes": files, "prior_packages": packages, "prior_external_checks": extchecks,
        "state": "PREPARATION_PLANNING_AUTHORIZED", "event_count": 2, "PREPARATION_EXECUTION": "NO",
        "airos_current_state": "ABSENT", "airos_contracts": "ABSENT", "observed_at_utc": h.now()})
    save("lineage.json", {"authority": "OPEN_V6_NATIVE_BUILDKIT_OCI_SESSION_COMPATIBILITY_PROBE", "request_path": str(REQUEST),
        "request_sha256": digest(REQUEST), "prior_status": first["status"], "prior_namespace": str(PRIOR.relative_to(ROOT)),
        "prior_manifest_sha256": digest(PRIOR / "artifact_sha256.json"), "historical_deviation": deviation,
        "historical_deviation_is_authority": False, "exact_prior_parser_error": "could not parse oci-layout reference <session-id>:@sha256:<digest>: invalid reference format",
        "layout_path": str(layout), "layout_inventory": expected_layout, "layout_manifest_origin": str(PRIOR / "external_evidence_manifest.json"),
        "transport_manifest": TRANSPORT, "config": CONFIG, "rootfs_diff_ids": first["rootfs_diff_ids"],
        "frozen_scientific_reference": first["frozen_registry_identity"]})
    save("prior_external_inventory.json", external)
    save("runtime_identity.json", runtime)
    save("docker_state_before.json", before)
    print("ENTRY PASS: 215 exact prior files; live HEAD, OCI 13 files/9 diffIDs, runtime and 7 bases verified", flush=True)


def create():
    require(load("entry_verification.json")["status"] == "PASS", "entry missing")
    require(not Q.exists(), "external namespace collision")
    Q.mkdir()
    durable(Q / "request.txt", REQUEST.read_bytes())
    netid = checked("create_internal", ["docker", "network", "create", "--internal", "--driver=bridge", "--label", OWNER, INTERNAL]).decode().strip()
    net = strict_json(checked("inspect_internal", ["docker", "network", "inspect", netid]))[0]
    require(net["Internal"] and net["Name"] == INTERNAL, "network not internal")
    save("internal_network.json", net)
    binding = strict_json((E / "v6_local_buildkit_runtime_provisioning_v1/future_builder_binding.json").read_bytes())
    checked("create_builder_metadata", binding["future_create_argv_not_executed"] + ["--buildkitd-flags=--debug"])
    checked("create_owned_volume", ["docker", "volume", "create", "--label", OWNER, VOLUME])
    cid = checked("create_exact_daemon", ["docker", "create", "--pull=never", "--platform=linux/amd64", "--name", CONTAINER,
        "--privileged", "--network=" + INTERNAL, "--dns=127.0.0.1", "--label", OWNER,
        "--mount", "type=volume,src=" + VOLUME + ",dst=/var/lib/buildkit", IMAGE, "--debug"]).decode().strip()
    save("owned_objects.json", {"container_id": cid, "container_name": CONTAINER, "volume": VOLUME, "network_id": netid, "builder": BUILDER, "label": OWNER})
    checked("start_exact_daemon", ["docker", "start", cid])
    command("bootstrap_existing_daemon", ["docker", "buildx", "inspect", "--bootstrap", BUILDER])
    observe_created()


def observe_created():
    """Read existing owned runtime only; never create a second daemon."""
    owned = load("owned_objects.json")
    cid, netid = owned["container_id"], owned["network_id"]
    net = load("internal_network.json")
    bootstrap = [r for r in load("commands_run.json") if r["name"] == "bootstrap_existing_daemon"][-1]
    require("pulling image" not in (bootstrap["stdout"] + bootstrap["stderr"]).lower(), "unexpected pull")
    row = strict_json(checked("daemon_inspect", ["docker", "inspect", cid], raw=False))[0]
    require(row["Config"]["Image"] == IMAGE and set(row["NetworkSettings"]["Networks"]) == {INTERNAL}
            and row["NetworkSettings"]["Networks"][INTERNAL]["NetworkID"] == netid, "wrong daemon runtime/network")
    require(not row["HostConfig"]["PortBindings"] and not row["NetworkSettings"]["Ports"], "external TCP exposure")
    proxy_keys = [k.split("=", 1)[0] for k in row["Config"]["Env"] if k.split("=", 1)[0].lower().endswith("proxy")]
    require(not proxy_keys, "proxy env present")
    routes = checked("daemon_routes", ["docker", "exec", cid, "ip", "route"]).decode()
    require(not re.search(r"^default\s", routes, re.M), "external default route")
    version = checked("daemon_version", ["docker", "exec", cid, "buildkitd", "--version"]).decode().strip()
    argv = checked("daemon_argv", ["docker", "exec", cid, "cat", "/proc/1/cmdline"]).decode().strip("\0").split("\0")
    unix = checked("observed_unix_sockets", ["docker", "exec", cid, "cat", "/proc/net/unix"]).decode()
    tcp = checked("observed_tcp_sockets", ["docker", "exec", cid, "cat", "/proc/net/tcp", "/proc/net/tcp6"]).decode()
    fds = checked("daemon_fd_socket_ownership", ["docker", "exec", cid, "ls", "-l", "/proc/1/fd"]).decode()
    daemon_inodes = set(re.findall(r"socket:\[(\d+)\]", fds))
    listeners = [line.split() for line in tcp.splitlines() if len(line.split()) > 9 and line.split()[3] == "0A"]
    require(not any(row[9] in daemon_inodes for row in listeners), "TCP daemon listener forbidden")
    require(all(row[1].split(":")[0] in {"0100007F", "0B00007F", "00000000000000000000000001000000"}
                for row in listeners), "nonloopback TCP listener forbidden")
    _, logs = command("daemon_startup_logs", ["docker", "logs", cid])
    durable(Q / "daemon_startup.stdout.log", logs["stdout"].encode())
    durable(Q / "daemon_startup.stderr.log", logs["stderr"].encode())
    save("builder_identity.json", {"builder": BUILDER, "driver": "docker-container", "container_id_operational_only": cid,
        "image_reference": IMAGE, "image_id": row["Image"], "network": INTERNAL, "network_id": netid,
        "internal": net["Internal"], "network_attachments": row["NetworkSettings"]["Networks"], "daemon_argv": argv,
        "BuildKit_version": version, "routes": routes, "proxy_env_keys": proxy_keys, "PortBindings": row["HostConfig"]["PortBindings"],
        "unix_socket_observation": unix, "tcp_socket_observation": tcp, "bootstrap": bootstrap,
        "daemon_fd_observation": fds, "daemon_socket_inodes": sorted(daemon_inodes),
        "TCP_listener_rows": listeners, "TCP_daemon_listener": False,
        "no_use": True, "daemon_count_created": 1})
    print("BUILDER CREATED; socket/worker state recorded for exact endpoint selection", flush=True)


def connect():
    identity = load("builder_identity.json")
    cid = identity["container_id_operational_only"]
    version, rec = command("native_client_version", ["docker", "exec", cid, "buildctl", "--version"], check=False)
    save("native_client_identity.json", {"command": rec, "version": version.stdout.decode().strip(), "inside_same_container": cid,
        "exists": version.returncode == 0, "client_location": "buildctl executable resolved inside exact daemon container"})
    connect_observed()


def daemon_log_messages(text):
    messages = []
    for line in text.splitlines():
        match = re.search(r'msg=("(?:\\.|[^"\\])*")', line)
        messages.append(json.loads(match.group(1)) if match else line)
    return "\n".join(messages)


def connect_observed():
    identity = load("builder_identity.json")
    cid = identity["container_id_operational_only"]
    native = load("native_client_identity.json")
    sockets = [line.split()[-1] for line in identity["unix_socket_observation"].splitlines()[1:]
               if len(line.split()) >= 8 and line.split()[3] == "00010000" and line.split()[-1].endswith("buildkitd.sock")]
    _, logs = command("daemon_connection_logs", ["docker", "logs", cid])
    logtext = daemon_log_messages(logs["stdout"] + logs["stderr"])
    observed = re.findall(r"running server on (\S+)", logtext)
    workers = re.findall(r'found worker "([^"]+)"', logtext)
    candidates = sorted(set(sockets) & set(observed))
    if not native["exists"] or len(candidates) != 1 or len(set(workers)) != 1:
        save("daemon_connection.json", {"status": CONNECTION_BLOCK, "socket_candidates": sockets, "observed_server_endpoints": observed,
            "observed_worker_ids": workers, "endpoint_selected": None, "reason": "client unavailable or actual local endpoint/worker not unique"})
        print(CONNECTION_BLOCK, flush=True)
        return
    endpoint = "unix://" + candidates[0]
    result, rec = command("native_same_daemon_workers", ["docker", "exec", cid, "buildctl", "--addr=" + endpoint, "debug", "workers"], check=False)
    text = result.stdout.decode()
    passed = result.returncode == 0 and workers[0] in text and "linux/amd64" in text
    connection = {"status": "PASS" if passed else CONNECTION_BLOCK, "endpoint_selected": endpoint,
        "observed_socket_paths": sockets, "observed_server_endpoints": observed, "expected_worker_id_from_daemon_logs": workers[0],
        "worker_stdout": text, "linux_amd64_available": "linux/amd64" in text, "same_container_id": cid, "command": rec}
    if (OUT / "daemon_connection.json").exists():
        durable(OUT / "daemon_connection_initial_observation.json", (OUT / "daemon_connection.json").read_bytes())
        durable(OUT / "daemon_connection.json", encoded(connection), update=True)
    else:
        save("daemon_connection.json", connection)
    print("SAME DAEMON CONNECTION " + ("PASS" if passed else "BLOCKED"), flush=True)


def copy():
    require(load("daemon_connection.json")["status"] == "PASS", "connection blocked; no input copy")
    lineage = load("lineage.json")
    verify_layout(Path(lineage["layout_path"]), lineage["layout_inventory"])
    cid = load("owned_objects.json")["container_id"]
    context = Q / "context"
    context.mkdir()
    durable(context / "Dockerfile", DOCKERFILE.encode())
    save("probe_dockerfile.json", {"bytes_utf8": DOCKERFILE, "sha256": sha(DOCKERFILE.encode()), "base_token": "errpilot_frozen_base",
        "observation_fields_only": ["sys.version", "platform.machine()", "sys.executable"], "network_dependent_operations": 0})
    checked("create_container_input_root", ["docker", "exec", cid, "mkdir", CPATH])
    checked("copy_exact_prior_oci", ["docker", "cp", lineage["layout_path"], cid + ":" + CPATH + "/oci"], timeout=300)
    checked("copy_fixture_context", ["docker", "cp", str(context), cid + ":" + CPATH + "/context"])
    paths = sorted(CPATH + "/oci/" + rel for rel in lineage["layout_inventory"]) + [CPATH + "/context/Dockerfile"]
    inside_hashes = checked("independent_container_input_hashes", ["docker", "exec", cid, "sha256sum"] + paths, timeout=300).decode()
    inside_files = checked("independent_container_input_files", ["docker", "exec", cid, "find", CPATH, "-type", "f"]).decode().splitlines()
    observed = {line.split(None, 1)[1].strip(): line.split(None, 1)[0] for line in inside_hashes.splitlines()}
    expected = {CPATH + "/oci/" + rel: item["sha256"] for rel, item in lineage["layout_inventory"].items()}
    expected[CPATH + "/context/Dockerfile"] = sha(DOCKERFILE.encode())
    require(set(inside_files) == set(expected) and observed == expected, "copied files/hash drift")
    save("copied_input_manifest.json", {"status": "PASS", "container_root": CPATH, "files": expected,
        "observed_sha256sum": inside_hashes, "actual_file_paths": sorted(inside_files), "OCI_file_count": 13,
        "context_files": ["Dockerfile"], "benchmark_source_copied": False, "dependency_files_copied": False})
    print("COPY PASS: 13 OCI files plus one Dockerfile independently hashed inside container", flush=True)


def native_argv(endpoint):
    require(endpoint.startswith("unix:///"), "nonlocal daemon endpoint forbidden")
    return ["buildctl", "--addr=" + endpoint, "build", "--oci-layout", "frozenbase=" + CPATH + "/oci",
        "--frontend=dockerfile.v0", "--local", "context=" + CPATH + "/context", "--local", "dockerfile=" + CPATH + "/context",
        "--opt", "context:errpilot_frozen_base=oci-layout://frozenbase@" + TRANSPORT, "--opt", "platform=linux/amd64",
        "--opt", "force-network-mode=none", "--no-cache", "--progress=plain", "--output", "type=oci,dest=" + CPATH + "/output.oci.tar"]


def validate_command(argv, endpoint):
    require(argv == native_argv(endpoint), "native command differs from single allowed command")
    require("oci-layout:///" not in " ".join(argv) and "buildx" not in argv, "old/Buildx syntax forbidden")
    return True


def validate_execution_facts(facts):
    """Reject prohibited execution evidence independently of success labels."""
    for key, expected in {
        "same_daemon": True, "daemon_count_created": 1, "external_TCP_listener": False,
        "registry_attempts": 0, "registry_pulls": 0, "benchmark_source_copied": False,
        "benchmark_dependency_installs": 0, "event_count": 2, "canonical_modified": False,
        "production_client_switch_claim": False, "native_solve_count": 1,
    }.items():
        require(facts.get(key) == expected, "prohibited execution fact: " + key)
    return True


def registry_lines(text):
    # The OCI provider normalizes the local alias as an image-reference label.
    # Preserve this label separately; only these exact local-source label lines
    # are excluded, never HTTP requests, registry endpoints, or other resolves.
    local_ref = "docker.io/library/errpilot_frozen_base@" + TRANSPORT
    result = []
    for line in text.splitlines():
        local_label = (bool(re.fullmatch(r"#\d+ resolve " + re.escape(local_ref) + r" done", line))
            or bool(re.search(r'msg=fetch span="resolving ' + re.escape(local_ref) + r'"', line)))
        request = re.search(r"registry-1\.docker\.io|auth\.docker\.io|https?://[^\s]+/v2/|\bdo request\b|\bfetch response\b|\bpulling image\b", line, re.I)
        resolution = re.search(r"\bresolv(e|ing)\b.*(docker\.io|registry)", line, re.I)
        if request or (resolution and not local_label):
            result.append(line)
    return result


def classify_existing_output():
    """Inspect the already completed single solve; no build or syntax retry."""
    source = load("source_binding_result.json")
    require(source["exit_code"] == 0 and source["frozen_base_consumed"] and load("run_observation.json")["RUN_pass"], "completed source/RUN gate absent")
    require(len([r for r in load("commands_run.json") if r["name"] == "single_native_oci_session_solve"]) == 1, "solve count drift")
    client = (Q / "buildctl.stdout.log").read_text() + (Q / "buildctl.stderr.log").read_text()
    daemon = (Q / "daemon_after_solve.stdout.log").read_text() + (Q / "daemon_after_solve.stderr.log").read_text()
    require("OCI load from client" in client and not registry_lines(client + daemon), "actual registry dependency or OCI consumption absent")
    builder = load("builder_identity.json")
    require(builder["internal"] and not re.search(r"^default\s", builder["routes"], re.M) and not builder["proxy_env_keys"], "isolation drift")
    for name in ["source_binding_result.json", "network_observation.json", "output_observation.json"]:
        durable(OUT / name.replace(".json", "_initial_observation.json"), (OUT / name).read_bytes())
    local_labels = source["registry_resolution_attempt_lines"]
    require(all(not registry_lines(line) for line in local_labels), "not solely local OCI label evidence")
    cid = load("owned_objects.json")["container_id"]
    inside = checked("existing_output_container_hash", ["docker", "exec", cid, "sha256sum", CPATH + "/output.oci.tar"]).decode().split()[0]
    checked("copy_existing_output_evidence", ["docker", "cp", cid + ":" + CPATH + "/output.oci.tar", str(Q / "output.oci.tar")], timeout=300)
    require(digest(Q / "output.oci.tar") == inside, "output copy hash mismatch")
    output = inspect_output(Q / "output.oci.tar")
    source["status"] = PASS
    source["registry_resolution_attempt_lines"] = []
    source["local_OCI_normalized_reference_label_lines"] = local_labels
    durable(OUT / "source_binding_result.json", encoded(source), update=True)
    network = load("network_observation.json")
    network.update(registry_attempt_lines=[], registry_attempts_observed=0,
        local_OCI_normalized_reference_label_lines=local_labels,
        interpretation="Exact normalized alias label inside successful OCI load from client, not an HTTP registry request. Complete logs contain no registry endpoint, do-request, fetch-response, pull, or other resolve attempt.",
        RUN_DNS_warning_observed="No non-localhost DNS nameservers are left in resolv.conf. Using default external servers",
        RUN_DNS_warning_boundary="RUN network mode none; no DNS or HTTP request observed; no packet capture performed")
    durable(OUT / "network_observation.json", encoded(network), update=True)
    durable(OUT / "output_observation.json", encoded(output), update=True)
    save("output_copy_verification.json", {"status": "PASS", "container_SHA256": inside, "retained_SHA256": output["sha256"],
        "solve_repeated": False, "OCI_syntax_changed": False, "inspection_of_existing_output_only": True})
    print(PASS + ": existing artifact copied and verified; single solve only", flush=True)


def solve():
    require(load("copied_input_manifest.json")["status"] == "PASS", "copied inputs missing")
    require(not (OUT / "source_binding_result.json").exists(), "second probe/retry forbidden")
    cid = load("owned_objects.json")["container_id"]
    endpoint = load("daemon_connection.json")["endpoint_selected"]
    argv = native_argv(endpoint)
    validate_command(argv, endpoint)
    full = ["docker", "exec", cid] + argv
    save("buildctl_command.json", {"argv_inside_container": argv, "host_argv": full, "endpoint": endpoint,
        "same_container_id": cid, "registration": "frozenbase=" + CPATH + "/oci", "mapping": "context:errpilot_frozen_base=oci-layout://frozenbase@" + TRANSPORT,
        "solve_count_authorized": 1, "Buildx_solve": False, "output": CPATH + "/output.oci.tar", "fixture_RUN_network": "none"})
    result, rec = command("single_native_oci_session_solve", full, check=False, timeout=300)
    durable(Q / "buildctl.stdout.log", result.stdout)
    durable(Q / "buildctl.stderr.log", result.stderr)
    _, daemon = command("daemon_after_solve", ["docker", "logs", cid])
    durable(Q / "daemon_after_solve.stdout.log", daemon["stdout"].encode())
    durable(Q / "daemon_after_solve.stderr.log", daemon["stderr"].encode())
    text = result.stdout.decode(errors="replace") + result.stderr.decode(errors="replace")
    registries = registry_lines(text + daemon["stdout"] + daemon["stderr"])
    # A completed OCI source vertex and RUN output establish actual consumption.
    source_lines = [line for line in text.splitlines() if "OCI" in line or "oci-layout" in line or "frozenbase" in line]
    observation = {"sys.version": re.findall(r"sys\.version=(3\.6\.9[^\r\n]*)", text),
        "platform.machine()": re.findall(r"platform\.machine\(\)=([^\r\n]+)", text),
        "sys.executable": re.findall(r"sys\.executable=([^\r\n]+)", text)}
    # Progress repeats the command text; only emitted '#N elapsed field=value' lines count.
    actual = {}
    for field, pattern in [("sys.version", r"^#\d+\s+[\d.]+\s+sys\.version=(.+)$"),
                           ("platform.machine()", r"^#\d+\s+[\d.]+\s+platform\.machine\(\)=([^\r\n]+)$"),
                           ("sys.executable", r"^#\d+\s+[\d.]+\s+sys\.executable=([^\r\n]+)$")]:
        matches = re.findall(pattern, text, re.M)
        actual[field] = matches[0] if len(matches) == 1 else None
    run_pass = bool(actual["sys.version"] and actual["sys.version"].startswith("3.6.9 ")
                    and actual["platform.machine()"] == "x86_64" and actual["sys.executable"] == "/usr/local/bin/python")
    source_pass = run_pass or bool(re.search(r"^#\d+.*(?:FROM|load).*oci-layout://frozenbase", text, re.M) and "extracting sha256:" in text)
    status = REGISTRY_BLOCK if registries else PASS if result.returncode == 0 and run_pass else POST_BLOCK if source_pass else SOURCE_BLOCK
    save("source_binding_result.json", {"status": status, "exit_code": result.returncode, "timed_out": rec["timed_out"],
        "source_binding": "PASS" if source_pass else "BLOCKED", "OCI_registration_accepted": source_pass,
        "frontend_mapping_accepted": source_pass, "frozen_base_consumed": source_pass, "source_log_lines": source_lines,
        "registry_resolution_attempt_lines": registries, "raw_logs": [str(Q / "buildctl.stdout.log"), str(Q / "buildctl.stderr.log")], "command": rec})
    save("run_observation.json", {"status": "PASS" if run_pass else "NOT_PASSED", "actual_observation": actual,
        "raw_matching_observations": observation, "Python_expected": "3.6.9", "platform_expected": "linux/amd64 (x86_64)",
        "sys_executable_expected": "/usr/local/bin/python", "RUN_pass": run_pass})
    save("network_observation.json", {"registry_attempt_lines": registries, "registry_attempts_observed": len(registries),
        "internal_only": True, "proxy": False, "fixture_RUN_network": "none", "packet_capture_performed": False,
        "observation_scope": "complete retained daemon/client logs; internal network attachment; no IPv4 default route; no proxy; loopback DNS; no registry exporter"})
    if registries or result.returncode:
        save("output_observation.json", {"status": "NOT_PRODUCED_OR_NOT_QUALIFIED", "solve_exit_code": result.returncode,
            "retained_output": None, "reason": "hard stop after failed solve or registry dependency"})
    else:
        checked("copy_output_evidence", ["docker", "cp", cid + ":" + CPATH + "/output.oci.tar", str(Q / "output.oci.tar")], timeout=300)
        output = inspect_output(Q / "output.oci.tar")
        save("output_observation.json", output)
    print(status, flush=True)


def inspect_output(path):
    with tarfile.open(path, "r") as archive:
        members = archive.getmembers()
        require(len({m.name for m in members}) == len(members) and all(not PurePosixPath(m.name).is_absolute()
            and ".." not in PurePosixPath(m.name).parts and (m.isfile() or m.isdir()) for m in members), "unsafe output archive")
        files = {m.name: m for m in members if m.isfile()}
        def read(name):
            require(name in files, "output member absent")
            return archive.extractfile(files[name]).read()
        index = strict_json(read("index.json"))
        descriptors = index["manifests"]
        # OCI exporter may wrap the image in an OCI index; follow observed descriptors only.
        def blob(desc):
            raw = read("blobs/sha256/" + desc["digest"].split(":")[1])
            require("sha256:" + sha(raw) == desc["digest"] and len(raw) == desc["size"], "output descriptor drift")
            return strict_json(raw)
        images = []
        for desc in descriptors:
            obj = blob(desc)
            for child in obj.get("manifests", [desc]):
                image = blob(child) if "manifests" in obj else obj
                if "layers" in image:
                    config = blob(image["config"])
                    if config.get("os") == "linux" and config.get("architecture") == "amd64":
                        images.append((child, image, config))
        require(len(images) == 1, "output linux/amd64 image not unique")
        desc, image, config = images[0]
        expected = load("lineage.json")["rootfs_diff_ids"]
        require(config["rootfs"]["diff_ids"][:9] == expected, "output lost frozen rootfs prefix")
        layer_hashes = []
        for layer in image["layers"]:
            name = "blobs/sha256/" + layer["digest"].split(":")[1]
            require(name in files and files[name].size == layer["size"], "output layer absent/size drift")
            value = hashlib.file_digest(archive.extractfile(files[name]), "sha256").hexdigest()
            require("sha256:" + value == layer["digest"], "output layer drift")
            layer_hashes.append(value)
    return {"status": "PASS_QUALIFICATION_OUTPUT_ONLY", "retained_output": str(path), "bytes": path.stat().st_size,
        "sha256": digest(path), "image_manifest": desc, "config_digest": image["config"]["digest"],
        "rootfs_diff_ids": config["rootfs"]["diff_ids"], "frozen_nine_rootfs_prefix_exact": True,
        "platform": "linux/amd64", "layer_sha256": layer_hashes, "loaded_to_Engine": False, "output_parity_qualified": False}


def cleanup():
    owned = load("owned_objects.json")
    cid = owned["container_id"]
    _, logs = command("daemon_precleanup", ["docker", "logs", cid], check=False)
    durable(Q / "daemon_precleanup.stdout.log", logs["stdout"].encode())
    durable(Q / "daemon_precleanup.stderr.log", logs["stderr"].encode())
    save("docker_state_precleanup.json", h.snapshot("precleanup"))
    pre = {p.name: {"sha256": digest(p), "bytes": p.stat().st_size} for p in OUT.iterdir() if p.is_file()}
    durable(Q / "precleanup_repository_evidence.json", encoded(pre))
    durable(Q / "precleanup_external_manifest.json", encoded(inventory(Q)))
    save("precleanup_evidence_receipt.json", {"status": "PERSISTED_FSYNC_READBACK", "external_manifest_sha256": digest(Q / "precleanup_external_manifest.json"),
        "repository_evidence_sha256": digest(Q / "precleanup_repository_evidence.json"), "evidence_persisted_before_cleanup": True})
    row = strict_json(checked("cleanup_owned_container_check", ["docker", "inspect", cid], raw=False))[0]
    require(row["Name"] == "/" + CONTAINER and row["Config"]["Labels"].get(OWNER.split("=")[0]) == OWNER.split("=")[1], "cleanup container ownership")
    # Builder metadata removal and owned container/state removal follow the prior architecture.
    checked("remove_owned_builder", ["docker", "buildx", "rm", BUILDER])
    remaining = checked("remaining_container_ids", ["docker", "ps", "-aq", "--no-trunc"]).decode().split()
    if cid in remaining:
        checked("remove_owned_container", ["docker", "rm", "-f", cid])
    volumes = checked("remaining_volume_names", ["docker", "volume", "ls", "-q"]).decode().split()
    if VOLUME in volumes:
        vol = strict_json(checked("cleanup_owned_volume_check", ["docker", "volume", "inspect", VOLUME]))[0]
        require(vol["Labels"].get(OWNER.split("=")[0]) == OWNER.split("=")[1], "cleanup volume ownership")
        checked("remove_owned_volume", ["docker", "volume", "rm", VOLUME])
    net = strict_json(checked("cleanup_owned_network_check", ["docker", "network", "inspect", owned["network_id"]]))[0]
    require(net["Labels"].get(OWNER.split("=")[0]) == OWNER.split("=")[1] and not net["Containers"], "cleanup network ownership/attachment")
    checked("remove_owned_internal", ["docker", "network", "rm", owned["network_id"]])
    after = h.snapshot("after")
    save("docker_state_after.json", after)
    before = load("docker_state_before.json")
    save("cleanup_verification.json", {"status": "PASS" if after == before else "STATE_DRIFT", "Docker_observable_state_exact": after == before,
        "runtime_image_preserved": after["images"] == before["images"], "seven_frozen_bases_preserved": after["images"] == before["images"],
        "owned_builder_container_volume_network_removed": True, "container_copied_inputs_removed_with_container": True,
        "qualification_output_retained_outside_Docker": (Q / "output.oci.tar").exists(), "prior_evidence_modified": False,
        "no_global_builder_use": True})
    require(after == before, "observable Docker state did not return to entry")
    print("CLEANUP PASS: observable Docker/global selection/config state exact", flush=True)


def finish():
    entry = load("entry_verification.json")
    files, packages = preserve_prior()
    require(files == entry["prior_file_hashes"], "prior 215 files changed")
    git = h.git_state("final")
    require(git["index_sha256"] == entry["index_sha256"], "index bytes changed")
    state = population_state()
    require(all(state[k] == entry[k] for k in state), "canonical/population/ledgers changed")
    require(inventory(EXTERNAL, exclude=Q) == load("prior_external_inventory.json"), "prior external evidence changed")
    connection = load("daemon_connection.json")
    status = connection["status"] if connection["status"] != "PASS" else load("source_binding_result.json")["status"]
    if status == PASS and load("output_observation.json")["status"] != "PASS_QUALIFICATION_OUTPUT_ONLY":
        status = POST_BLOCK
    next_gate = ("HUMAN_PI_DECIDE_V6_NATIVE_BUILDKIT_CLIENT_COMPATIBILITY_BRIDGE" if status == PASS else
        "HUMAN_PI_REVIEW_V6_NATIVE_BUILDKIT_OCI_SESSION_SOURCE_BLOCK" if status == SOURCE_BLOCK else
        "HUMAN_PI_REVIEW_" + status.removeprefix("V6_"))
    save("final_verification.json", {"status": "PASS_PRESERVATION", **git, **state, "prior_file_count": len(files),
        "prior_manifest_population_exact": True, "prior_external_exact": True, "classification": status, "next_gate": next_gate,
        "new_repository_inventory_before_validation": sorted(str(p.relative_to(ROOT)) for p in OUT.iterdir() if p.is_file()), "external_root": str(Q)})
    save("firewall.json", {"REAL_BENCHMARK_ATTEMPTS": 0, "REAL_BENCHMARK_CLAIMS": 0, "REAL_BENCHMARK_BUILDS": 0,
        "BENCHMARK_DEPENDENCY_INSTALLS": 0, "BENCHMARK_SOURCE_EXPORTS": 0, "REGISTRY_PULLS": 0,
        "UNAPPROVED_EGRESS": 0, "unapproved_egress_scope": "no egress observed; network isolation and retained logs; no packet capture",
        "PRODUCTION_CLIENT_SWITCHED": "NO", "EVENT_3_CREATED": "NO", "CANONICAL_CURRENT_STATE_MODIFIED": "NO",
        "GIT_STAGE": "NO", "GIT_COMMIT": "NO", "GIT_PUSH": "NO", "native_fixture_solves": int((OUT / "buildctl_command.json").exists()),
        "daemon_count_created": 1, "qualification_only": True})
    print(status + "\nNEXT_GATE=" + next_gate, flush=True)


if __name__ == "__main__":
    phases = {"entry": entry, "create": create, "observe-created": observe_created, "connect": connect,
        "connect-observed": connect_observed, "copy": copy, "solve": solve, "classify-existing-output": classify_existing_output,
        "cleanup": cleanup, "finish": finish}
    require(len(sys.argv) == 2 and sys.argv[1] in phases, "single explicit phase required")
    phases[sys.argv[1]]()

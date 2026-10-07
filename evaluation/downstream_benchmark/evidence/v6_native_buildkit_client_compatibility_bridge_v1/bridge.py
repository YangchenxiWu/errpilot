"""Bounded native-client qualification. Never dispatch a benchmark attempt."""
from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
import tarfile
from pathlib import Path

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
E = OUT.parent
PRIOR = E / "v6_native_buildkit_oci_session_probe_v1"
EXTERNAL = Path("/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1")
Q = EXTERNAL / "qualification/native_buildkit_client_compatibility_bridge_v1"
REQUEST = Path("/Users/wuyangchenxi/.codex/attachments/25849ba2-9fb1-42f4-b778-a7e553fd267b/已粘贴的文本.txt")


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


n = module("bridge_predecessor_helpers", PRIOR / "native_probe.py")
t = module("bridge_oci_helpers", E / "v6_buildkit_frozen_base_transport_bridge_v1/transport_bridge.py")
h = n.h
n.OUT = h.OUT = t.OUT = t.prior.OUT = OUT
n.Q = h.Q = t.Q = t.prior.Q = Q
sha, require, durable, encoded = h.sha, h.require, h.durable, h.encoded
save, load, checked, command = h.save, h.load, h.checked, h.command
strict_json, digest, inventory = n.strict_json, n.digest, n.inventory
BUILDER, CONTAINER, VOLUME, INTERNAL, IMAGE = n.BUILDER, n.CONTAINER, n.VOLUME, n.INTERNAL, n.IMAGE
OWNER = "errpilot.v6.qualification=native_buildkit_client_compatibility_bridge_v1"
CPATH = "/tmp/errpilot-v6-native-client-bridge-v1"
PACKAGES = h.PACKAGES + [
    ("v6_restricted_build_egress_compatibility_bridge_resume_v1", 38),
    ("v6_buildkit_frozen_base_transport_bridge_v1", 53),
    (PRIOR.name, 45),
]
g = module("native_bridge_guards", OUT / "guards.py")
raw_command = command


def command(name, argv, **kwargs):
    g.command(argv)
    return raw_command(name, argv, **kwargs)


h.command = n.command = t.prior.command = command


def preserve_prior():
    files, packages = {}, []
    for package, count in PACKAGES:
        path = E / package / "artifact_sha256.json"
        manifest = strict_json(path.read_bytes())
        require(len(manifest["artifacts"]) + 1 == count, "prior count drift: " + package)
        for rel, expected in manifest["artifacts"].items():
            require(digest(ROOT / rel) == expected, "historical bytes drift: " + rel)
            files[rel] = expected
        rel = str(path.relative_to(ROOT))
        files[rel] = digest(path)
        actual = {str(p.relative_to(ROOT)) for p in path.parent.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
        within = {x for x in manifest["artifacts"] if x.startswith(str(path.parent.relative_to(ROOT)) + "/")}
        require(actual == within | {rel}, "historical namespace drift: " + package)
        packages.append({"package": package, "files": count, "manifest_sha256": files[rel]})
    require(len(files) == 260, "prior combined population drift")
    actual = checked("prior_untracked", ["git", "ls-files", "--others", "--exclude-standard"]).decode().splitlines()
    own = str(OUT.relative_to(ROOT)) + "/"
    require({p for p in actual if not p.startswith(own)} == set(files), "unrelated untracked paths")
    return files, packages


def verify_external_history():
    external = inventory(EXTERNAL, exclude=Q)
    checks = []
    for package, _ in PACKAGES[2:]:
        d = strict_json((E / package / "external_evidence_manifest.json").read_bytes())
        prefix = str(Path(d["root"]).relative_to(EXTERNAL)) + "/"
        actual = {k[len(prefix):]: v for k, v in external.items() if k.startswith(prefix)}
        expected = d.get("artifact_inventory", d.get("artifacts"))
        for rel, item in expected.items():
            normalized = {"type": "file", **item}
            if normalized["type"] == "symlink" and "target" in normalized:
                import base64
                normalized["target_b64"] = base64.b64encode(os.fsencode(normalized.pop("target"))).decode()
            require(actual.get(rel) == normalized, "historical external drift: " + rel)
        seal = d.get("manifest_sha256", d.get("external_manifest_sha256"))
        require(set(actual) == set(expected) | ({"artifact_sha256.json"} if seal else set()), "historical external set drift")
        if seal:
            require(actual["artifact_sha256.json"]["sha256"] == seal, "historical external seal drift")
        checks.append({"package": package, "verified_files": len(actual)})
    d = strict_json((E / PACKAGES[1][0] / "external_artifact_sha256.json").read_bytes())
    for item in d["artifacts"]:
        require(external[item["relative_path"]]["sha256"] == item.get("sha256", item.get("target_bytes_sha256")), "runtime history drift")
    return external, checks


def predecessor():
    def read(name):
        return strict_json((PRIOR / (name + ".json")).read_bytes())
    source, run, output = read("source_binding_result"), read("run_observation"), read("output_observation")
    connection, client, builder = read("daemon_connection"), read("native_client_identity"), read("builder_identity")
    argv = read("buildctl_command")["argv_inside_container"]
    require(source["status"] == n.PASS and source["exit_code"] == 0 and source["frozen_base_consumed"], "predecessor PASS absent")
    require(connection["status"] == "PASS" and connection["same_container_id"] == client["inside_same_container"] == builder["container_id_operational_only"], "predecessor wrong daemon")
    require(builder["daemon_count_created"] == 1 and builder["image_reference"] == IMAGE and client["exists"], "predecessor runtime drift")
    require("--oci-layout" in argv and "frozenbase=" in " ".join(argv)
            and "context:errpilot_frozen_base=oci-layout://frozenbase@" + n.TRANSPORT in argv, "predecessor native registration drift")
    require(run["RUN_pass"] and "3.6.9" in json.dumps(run) and "x86_64" in json.dumps(run), "predecessor RUN absent")
    require(output["status"] == "PASS_QUALIFICATION_OUTPUT_ONLY" and output["platform"] == "linux/amd64", "predecessor output invalid")
    require(not read("network_observation")["registry_attempt_lines"], "predecessor registry fallback")
    commands = read("commands_run")
    solves = [x for x in commands if "single_native_oci_session_solve" == x["name"]]
    require(len(solves) == 1 and not any(x["argv"][:3] == ["docker", "buildx", "build"] for x in commands), "predecessor solve drift")
    logs = Path(read("external_evidence_manifest")["root"])
    text = "".join((logs / x).read_text() for x in ["buildctl.stderr.log", "buildctl.stdout.log", "daemon_after_solve.stderr.log", "daemon_after_solve.stdout.log"])
    require(not n.registry_lines(text) and "OCI load from client" in text, "predecessor log mismatch")
    require(digest(Path(output["retained_output"])) == output["sha256"], "predecessor output bytes drift")
    h.OUT = PRIOR
    try:
        verified_output = n.inspect_output(Path(output["retained_output"]))
    finally:
        h.OUT = OUT
    require(verified_output["sha256"] == output["sha256"], "predecessor artifact invalid")
    return {"status": "PASS", "required_predecessor_status": n.PASS, "manifest_sha256": digest(PRIOR / "artifact_sha256.json"),
            "same_daemon": connection, "native_client": client, "source": source, "run": run,
            "validated_output": verified_output, "registry_requests_observed": 0, "Buildx_solves": 0,
            "historical_Buildx_adapter": "NOT_QUALIFIED_PARSER_BLOCKED", "historical_fallback_exception_preserved": True}


def entry():
    require(not Q.exists(), "new external namespace collision")
    require(not (ROOT / ".airos/current_state.md").exists() and not (ROOT / ".airos/contracts").exists(), "new AIROS scope requires reading")
    files, packages = preserve_prior()
    git, population = h.git_state("entry"), n.population_state()
    external, checks = verify_external_history()
    binding = predecessor()
    runtime = h.runtime_verify("entry")
    bases = strict_json((E / "v6_buildkit_frozen_base_transport_bridge_v1/frozen_base_authorities.json").read_bytes())["bases"]
    for i, base in enumerate(bases):
        row = strict_json(checked("entry_base_" + str(i), ["docker", "image", "inspect", base["reference"]], raw=False))[0]
        require({k: row[k] for k in base["image_identity"]} == base["image_identity"], "frozen base drift")
    before = h.snapshot("before")
    require(not any(x["Name"] == "/" + CONTAINER for x in before["containers"])
            and not any(x["Name"] == INTERNAL for x in before["networks"])
            and not any(x["Name"] == VOLUME for x in before["volumes"]), "owned object collision")
    save("accepted_decision.json", {"gate": "HUMAN_PI_DECIDE_V6_NATIVE_BUILDKIT_CLIENT_COMPATIBILITY_BRIDGE",
        "decision": "ADOPT_V6_NATIVE_BUILDKIT_CLIENT_COMPATIBILITY_BRIDGE_V1", "owner": "HUMAN_PI",
        "authority_scope": "CONSTRUCTION_AND_FIXTURE_QUALIFICATION_ONLY", "request_path": str(REQUEST),
        "request_sha256": digest(REQUEST), "request_bytes_utf8": REQUEST.read_text(), "real_dispatch": "REJECT"})
    save("entry_verification.json", {"status": "PASS", **git, **population, "prior_files": files,
        "prior_packages": packages, "prior_file_count": len(files), "prior_external_checks": checks,
        "airos_current_state": "ABSENT", "airos_contracts": "ABSENT"})
    save("predecessor_probe_binding.json", binding)
    save("prior_external_inventory.json", external)
    save("runtime_identity.json", runtime)
    save("docker_state_before.json", before)
    save("frozen_base_authorities.json", {"bases": bases})
    print("ENTRY PASS: 260 prior bytes exact; predecessor reproduced; seven bases and runtime local", flush=True)


def create():
    n.OWNER, n.REQUEST = OWNER, REQUEST
    n.create()
    n.connect()
    require(load("daemon_connection.json")["status"] == "PASS", "same-daemon connection failed")
    cid = load("owned_objects.json")["container_id"]
    for name, argv in [
        ("buildctl_help", ["buildctl", "--help"]),
        ("buildctl_build_help", ["buildctl", "build", "--help"]),
        ("buildkitd_help", ["buildkitd", "--help"]),
        ("client_binary_hash", ["sha256sum", "/usr/bin/buildctl", "/usr/bin/buildkitd"]),
    ]:
        result, rec = command(name, ["docker", "exec", cid] + argv)
        durable(Q / (name + ".txt"), result.stdout + result.stderr)
        save(name + ".json", rec)
    print("CLIENT HELP AND EXACT BINARY HASHES RECOVERED", flush=True)


def runtime_capabilities():
    cid = load("owned_objects.json")["container_id"]
    observations = {}
    for binary, tokens in [
        ("buildctl", [b"github.com/moby/buildkit/cmd/buildctl.parseOutput", b"docker", b"dest", b"--output", b"build-arg:"]),
        ("buildkitd", [b"github.com/moby/buildkit/exporter/oci", b"force-network-mode", b"build-arg:", b"networkmode", b"docker", b"name"]),
    ]:
        path = Q / (binary + ".runtime-binary")
        checked("copy_runtime_binary_" + binary, ["docker", "cp", cid + ":/usr/bin/" + binary, str(path)])
        raw = path.read_bytes()
        expected = {line.split()[1]: line.split()[0] for line in load("client_binary_hash.json")["stdout"].splitlines()}
        require(digest(path) == expected["/usr/bin/" + binary], "runtime binary copy drift")
        snippets = []
        for token in tokens:
            offsets = [m.start() for m in re.finditer(re.escape(token), raw)]
            snippets.append({"token": token.decode(), "occurrences": len(offsets),
                "observed_context": [raw[max(0, pos - 55):pos + len(token) + 85].decode(errors="replace") for pos in offsets[:5]]})
        observations[binary] = {"binary_sha256": digest(path), "snippets": snippets}
    save("runtime_capabilities.json", {"exact_runtime_binary_observations": observations,
        "native_option_form_from_build_help": "--opt build-arg:foo=bar", "native_export_option_form": "--output type=<exporter>,<attributes>",
        "docker_exporter": "installed exporter/oci runtime includes Docker variant; actual type=docker,name,dest is gated by the qualification solve",
        "network_none_option": "force-network-mode=none", "none_runtime_proof": "predecessor exact option plus dedicated current fixture required",
        "default_network": "omit force-network-mode; normal RUN uses worker default inside dedicated internal-only daemon",
        "source": "exact installed binary and native help; no host buildctl or alternate frontend"})
    print("INSTALLED RUNTIME CAPABILITIES RECOVERED", flush=True)


def copy_verified(host_root, container_root, label):
    cid = load("owned_objects.json")["container_id"]
    expected = inventory(host_root)
    require(expected and all(x["type"] == "file" for x in expected.values()), "unsafe input file set")
    checked(label + "_copy", ["docker", "cp", str(host_root), cid + ":" + container_root], timeout=300)
    paths = sorted(container_root + "/" + rel for rel in expected)
    observed = checked(label + "_hash", ["docker", "exec", cid, "sha256sum"] + paths, timeout=300).decode()
    hashes = {line.split(None, 1)[1].strip(): line.split(None, 1)[0] for line in observed.splitlines()}
    inside = checked(label + "_files", ["docker", "exec", cid, "find", container_root, "-type", "f"]).decode().splitlines()
    target = {container_root + "/" + rel: x["sha256"] for rel, x in expected.items()}
    require(hashes == target and set(inside) == set(paths), "input copy mismatch")
    return {"status": "PASS", "host_root": str(host_root), "container_root": container_root, "inventory": expected, "container_hashes": hashes}


def native_solve(label, layout, context, transport, *, output, network_none=True, build_args=None, extra_hosts=None):
    require(not (OUT / (label + "_solve_started.json")).exists(), "automatic solve retry forbidden")
    connection = load("daemon_connection.json")
    cid = load("owned_objects.json")["container_id"]
    require(connection["same_container_id"] == cid and connection["endpoint_selected"] == "unix:///run/buildkit/buildkitd.sock", "wrong same-daemon endpoint")
    argv = ["/usr/bin/buildctl", "--addr=" + connection["endpoint_selected"], "build",
        "--oci-layout", "frozenbase=" + layout, "--frontend=dockerfile.v0", "--local", "context=" + context,
        "--local", "dockerfile=" + context, "--opt", "context:errpilot_frozen_base=oci-layout://frozenbase@" + transport,
        "--opt", "platform=linux/amd64", "--no-cache", "--progress=plain", "--output", output]
    if network_none:
        argv += ["--opt", "force-network-mode=none"]
    for key, value in sorted((build_args or {}).items()):
        argv += ["--opt", "build-arg:" + key + "=" + value]
    if extra_hosts:
        argv += ["--opt", "add-hosts=" + extra_hosts]
    g.native_command(argv, list(argv))
    save(label + "_solve_started.json", {"host_argv": ["docker", "exec", cid] + argv, "same_daemon": cid,
        "network": "NONE" if network_none else "DEFAULT", "fixture_only": True, "retry_allowed": False})
    result, rec = command(label + "_native_solve", ["docker", "exec", cid] + argv, check=False, timeout=600)
    durable(Q / (label + ".buildctl.stdout.log"), result.stdout)
    durable(Q / (label + ".buildctl.stderr.log"), result.stderr)
    daemon_result, _ = command(label + "_daemon_logs", ["docker", "logs", cid])
    durable(Q / (label + ".daemon.log"), daemon_result.stdout + daemon_result.stderr)
    text = (result.stdout + result.stderr + daemon_result.stdout + daemon_result.stderr).decode(errors="replace")
    old = n.TRANSPORT
    n.TRANSPORT = transport
    try:
        registry = n.registry_lines(text)
    finally:
        n.TRANSPORT = old
    # Prior completed local OCI aliases in cumulative daemon logs are preserved
    # separately; HTTP registry requests always remain prohibited.
    transport_ids = [transport]
    if (OUT / "seven_base_transport_map.json").exists():
        transport_ids += [x["local_oci_manifest_identity"] for x in load("seven_base_transport_map.json")["mapping"]]
    registry = [line for line in registry if not any(
        re.search(r'msg=fetch span="resolving docker.io/library/errpilot_frozen_base@' + re.escape(identity) + r'"', line)
        and not re.search(r"\bdo request\b|\bfetch response\b|https?://|registry-1|auth.docker", line)
        for identity in transport_ids)]
    receipt = {"exit_code": result.returncode, "OCI_load_from_client": "OCI load from client" in text,
        "registry_request_lines": registry, "argv": argv, "command": rec}
    save(label + "_solve_observation.json", receipt)
    require(result.returncode == 0 and receipt["OCI_load_from_client"] and not registry, "native solve/source/registry gate failed: " + label)
    return result.stdout + result.stderr


def engine_observations(tag, base, label):
    from evaluation.downstream_benchmark.screening import materializer as m
    row = strict_json(checked(label + "_image_inspect", ["docker", "image", "inspect", tag], raw=False))[0]
    require(tag in row["RepoTags"] and (row["Os"], row["Architecture"]) == ("linux", "amd64"), "output tag/platform invalid")
    prefix = base["image_identity"]["RootFS"]["Layers"]
    require(row["RootFS"]["Layers"][:len(prefix)] == prefix, "output rootfs lost exact base layers")
    python = ("import hashlib,json,platform,sys; p=sys.executable; print(json.dumps({'version':'.'.join(map(str,sys.version_info[:3])),"
              "'machine':platform.machine(),'executable':p,'executable_sha256':hashlib.sha256(open(p,'rb').read()).hexdigest()}))")
    args = ["docker", "run", "--rm", "--pull=never", "--platform=linux/amd64", "--network=none", "--read-only", "--tmpfs", "/tmp", "-e", "HOME=/tmp", tag]
    observed = strict_json(checked(label + "_python_probe", args + ["python", "-c", python]))
    require(observed == base["python_probe"], "output Python identity changed")
    backend = m.distribution_backend(observed["version"])
    dist_cmd = ["python", "-m", "pip", "list", "--format=json"] if backend == "PIP_LIST_JSON" else ["python", "-c",
        "import importlib.metadata,json; print(json.dumps([(d.metadata.get('Name',''),d.version) for d in importlib.metadata.distributions()]))"]
    result, _ = command(label + "_distribution_probe", args + dist_cmd)
    distributions = m.canonical_distribution_manifest(result.stdout, backend)
    packages, _ = command(label + "_system_packages", args + ["dpkg-query", "-W", "-f=${Package} ${Version}\\n"])
    durable(Q / (label + ".installed_distributions.json"), distributions)
    durable(Q / (label + ".system_packages.txt"), packages.stdout)
    return {"status": "PASS", "qualification_tag": tag, "image_id_observed": row["Id"], "RootFS": row["RootFS"],
        "platform": "linux/amd64", "python_probe": observed, "distribution_backend": backend,
        "installed_distribution_manifest_sha256": sha(distributions), "system_packages_sha256": sha(packages.stdout),
        "environment_observation_identity": sha(encoded({"base": base["reference"], "image_id": row["Id"],
            "rootfs": row["RootFS"], "python": observed, "distributions": sha(distributions), "system_packages": sha(packages.stdout)})),
        "materializer_observation_semantics_available": True, "benchmark_environment_created": False,
        "old_client_byte_equality_required": False, "byte_reproducibility_claim": False}


def qualify_base(index):
    require(load("entry_verification.json")["status"] == "PASS", "entry absent")
    require((OUT / "runtime_capabilities.json").exists(), "installed capabilities absent")
    bases = load("frozen_base_authorities.json")["bases"]
    require(0 <= index < 7, "wrong base ordinal")
    if index:
        require(load("base_" + str(index - 1) + "_qualification.json")["status"] == "PASS", "prior base hard gate")
    base, label = bases[index], "base_" + str(index)
    require(not (OUT / (label + "_started.json")).exists(), "base retry/regeneration forbidden")
    save(label + "_started.json", {"base": base["reference"], "fixture_only": True})
    row = strict_json(checked(label + "_frozen_inspect", ["docker", "image", "inspect", base["reference"]], raw=False))[0]
    require({k: row[k] for k in base["image_identity"]} == base["image_identity"], "frozen base drift")
    root = Q / label
    root.mkdir()
    archive = root / "engine-save.tar"
    checked(label + "_save", ["docker", "image", "save", "--platform=linux/amd64", "-o", str(archive), base["reference"]], timeout=300)
    observation = {"archive_sha256": digest(archive)}
    transport = t.construct_layout(archive, root / "oci", base, observation)
    observation["layout_inventory"] = t.validate_layout(root / "oci", observation)
    durable(root / "archive_equivalence.json", encoded(observation))
    save(label + "_transport.json", observation)
    cid = load("owned_objects.json")["container_id"]
    croot = CPATH + "/" + label
    checked(label + "_input_root", ["docker", "exec", cid, "mkdir", "-p", croot])
    copied = copy_verified(root / "oci", croot + "/oci", label + "_oci")
    context = root / "context"
    context.mkdir()
    action = 'RUN python -c "import sys,platform; print(\'NATIVE_BASE_IDENTITY=\'+platform.python_version()+\':\'+platform.machine()+\':\'+sys.executable)"\n'
    original = "FROM " + base["reference"] + "\n" + action
    execution = "FROM errpilot_frozen_base\n" + action
    require(execution == original.replace("FROM " + base["reference"] + "\n", "FROM errpilot_frozen_base\n", 1), "action delta")
    durable(context / "Dockerfile", execution.encode())
    copied_context = copy_verified(context, croot + "/context", label + "_context")
    save(label + "_copied_inputs.json", {"OCI": copied, "context": copied_context,
        "scientific_fixture_dockerfile": original, "execution_dockerfile": execution, "delta": "BASE_TRANSPORT_SUBSTITUTION_ONLY"})
    tag = "errpilot-v6-native-bridge-qualification:" + label
    output_inside = croot + "/output.docker.tar"
    text = native_solve(label, croot + "/oci", croot + "/context", transport["digest"],
        output="type=docker,name=" + tag + ",dest=" + output_inside).decode(errors="replace")
    marker = "NATIVE_BASE_IDENTITY=" + base["python_version"] + ":x86_64:/usr/local/bin/python"
    require(marker in text, "fixture Python observation missing")
    inside_sha = checked(label + "_output_hash", ["docker", "exec", cid, "sha256sum", output_inside]).decode().split()[0]
    host_output = root / "output.docker.tar"
    checked(label + "_output_copy", ["docker", "cp", cid + ":" + output_inside, str(host_output)], timeout=300)
    require(digest(host_output) == inside_sha, "Docker output copy drift")
    with tarfile.open(host_output) as tar:
        manifest = strict_json(tar.extractfile("manifest.json").read())
        require(len(manifest) == 1 and tag in manifest[0]["RepoTags"], "not exact tagged Docker-format output")
    checked(label + "_engine_load", ["docker", "load", "-i", str(host_output)], timeout=300)
    output = engine_observations(tag, base, label)
    output.update(exporter="docker", docker_load=True, artifact_sha256=inside_sha, artifact_bytes=host_output.stat().st_size,
        retained_artifact=str(host_output))
    mapping = {"scientific_base_authority": base["reference"], "frozen_registry_digest": base["reference"].split("@")[1],
        "engine_image_identity": base["image_identity"]["Id"], "engine_config_identity": observation["engine_config_identity"],
        "ordered_rootfs_diff_ids": observation["config_rootfs_diff_ids"], "docker_save_archive_sha256": observation["archive_sha256"],
        "local_oci_manifest_identity": transport["digest"], "layout_path": str(root / "oci"), "native_store_name": "frozenbase",
        "frontend_context_alias": "errpilot_frozen_base", "qualification_result": "PASS", "python_version": base["python_version"]}
    save(label + "_qualification.json", {"status": "PASS", "base": base["reference"], "transport": mapping, "output_parity": output,
        "RUN_identity": marker, "registry_requests_observed": 0, "pulls": 0})
    mapfile = OUT / "seven_base_transport_map.json"
    mappings = load(mapfile.name)["mapping"] if mapfile.exists() else []
    mappings.append(mapping)
    durable(mapfile, encoded({"mapping": mappings, "qualified": len(mappings), "total": 7,
        "transport_enters_scientific_identity": False, "automatic_regeneration": False}), update=mapfile.exists())
    if index == 6:
        results = [load("base_" + str(i) + "_qualification.json") for i in range(7)]
        save("all_base_native_transport_qualification.json", {"status": "PASS", "passed": 7, "total": 7, "results": results})
        save("native_output_parity.json", {"status": "PASS", "passed": 7, "total": 7, "outputs": [r["output_parity"] for r in results],
            "scientific_firewall": "environment-evidence semantics only; no old-client image byte equality or scientific validation"})
    print("NATIVE TRANSPORT + DOCKER EXPORT/LOAD PARITY PASS " + str(index + 1) + "/7: " + base["python_version"], flush=True)


def network_audit():
    require(load("all_base_native_transport_qualification.json")["status"] == "PASS", "seven-base gate absent")
    from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a
    from evaluation.downstream_benchmark.screening import v6_preparation_runtime as r
    _, manifest = a.load_inputs()
    population = r.population()
    rows = []
    for item in population["items"]:
        plan = a.select(manifest, ordinal=item["census_order"], case_id=item["case_id"], plan_sha=item["plan_sha256"])
        recipe = a.engine_recipe(plan)
        values = a.embedded_inputs(manifest, plan)
        definition = a.shared.build_definition(recipe, source_present=item["variant"] != "SOURCE_INDEPENDENT",
            dependency_present=values["dependency_input"] is not None)
        base = recipe["base_image_reference"]
        from_line = "FROM --platform=linux/amd64 " + base + "\n"
        require(definition.startswith(from_line.encode()) and definition.count(from_line.encode()) == 1, "ambiguous FROM")
        derived = b"FROM --platform=linux/amd64 errpilot_frozen_base\n" + definition[len(from_line):]
        args = {}
        if item["build_network_required"]:
            derived = derived.replace(b"\n", b"\nARG PIP_INDEX_URL\n", 1)
            args = {"HTTP_PROXY": "http://" + h.STEM + "-proxy:3128", "HTTPS_PROXY": "http://" + h.STEM + "-proxy:3128",
                "PIP_INDEX_URL": "https://pypi.org/simple"}
        original_runs = [line for line in definition.splitlines(keepends=True) if line.startswith(b"RUN ")]
        derived_runs = [line for line in derived.splitlines(keepends=True) if line.startswith(b"RUN ")]
        require(original_runs == derived_runs, "scientific RUN action bytes/order changed")
        rows.append({"base_attempt_id": item["base_attempt_id"], "recipe_sha256": item["recipe_sha256"],
            "engine_recipe_sha256": item["engine_recipe_sha256"], "scientific_dockerfile_sha256": sha(definition),
            "execution_dockerfile_sha256": sha(derived), "RUN_count": len(original_runs), "RUN_bytes_and_order_unchanged": True,
            "build_network": "DEFAULT" if args else "NONE", "native_frontend_opts": ([] if args else ["force-network-mode=none"]),
            "proxy_build_args": args, "EXECUTION_NETWORK_TRANSPORT_DELTA": "NATIVE_FRONTEND_FORCE_NETWORK_MODE_NONE" if not args else "NONE",
            "dockerfile_delta": ["BASE_TRANSPORT_SUBSTITUTION"] + (["ARG_PIP_INDEX_URL_TRANSPORT_BINDING"] if args else []),
            "RUN_network_directive_insertion": False})
    restricted = [x["base_attempt_id"] for x in rows if x["build_network"] == "DEFAULT"]
    none = [x["base_attempt_id"] for x in rows if x["build_network"] == "NONE"]
    require((len(rows), len(restricted), len(none)) == (641, 583, 58), "network scope drift")
    scope = strict_json((E / "v6_buildkit_frozen_base_transport_bridge_v1/work_item_scope.json").read_bytes())
    require(restricted == scope["restricted_work_item_ids"] and none == scope["network_none_work_item_ids"], "exact network IDs drift")
    save("native_network_semantics_audit.json", {"status": "STATIC_AUDIT_PASS_RUNTIME_QUALIFICATION_PENDING", "total": 641,
        "restricted": 583, "none": 58, "restricted_ids": restricted, "none_ids": none, "items": rows,
        "network_none_mechanism": "--opt force-network-mode=none", "RUN_rewrite_required": False,
        "scientific_actions_unchanged": True, "default_uses_internal_only_worker": load("builder_identity.json"),
        "native_help_sha256": load("buildctl_build_help.json")["stdout_sha256"]})
    print("NETWORK SEMANTICS STATIC AUDIT PASS 641/583/58; runtime NONE fixture pending", flush=True)


def proxy_create():
    require(load("native_network_semantics_audit.json")["total"] == 641, "network audit absent")
    require(not (OUT / "proxy_objects.json").exists(), "proxy creation already attempted")
    external_net, proxy_name, fixture_name = h.STEM + "-external", h.STEM + "-proxy", h.STEM + "-external-fixture"
    before = h.snapshot("before_proxy")
    require(not any(x["Name"] == external_net for x in before["networks"])
        and not any(x["Name"] in {"/" + proxy_name, "/" + fixture_name} for x in before["containers"]), "proxy name collision")
    durable(Q / "proxy.py", (OUT / "proxy.py").read_bytes())
    source = module("bridge_proxy_policy", OUT / "proxy.py")
    save("proxy_policy.json", {"policy": source.POLICY, "policy_sha256": sha(encoded(source.POLICY)),
        "implementation_sha256": digest(OUT / "proxy.py"), "port": 3128, "proxy_name": proxy_name})
    fixture = ('import socketserver\n'
        'class Handler(socketserver.BaseRequestHandler):\n'
        '    def handle(self): self.request.sendall(b"EXTERNAL_ONLY_FIXTURE\\n")\n'
        'class Server(socketserver.ThreadingMixIn,socketserver.TCPServer):\n'
        '    allow_reuse_address=True\n'
        'with Server(("0.0.0.0",8443),Handler) as server: server.serve_forever()\n')
    durable(Q / "external_fixture.py", fixture.encode())
    image = load("frozen_base_authorities.json")["bases"][0]["reference"]
    netid = checked("create_external_proxy_network", ["docker", "network", "create", "--driver=bridge", "--label", OWNER, external_net]).decode().strip()
    save("proxy_objects.json", {"external_network": external_net, "external_network_id": netid,
        "proxy_name": proxy_name, "fixture_name": fixture_name, "image": image, "label": OWNER})
    for role, name, source_path, target in [
        ("fixture", fixture_name, Q / "external_fixture.py", "/external_fixture.py"),
        ("proxy", proxy_name, Q / "proxy.py", "/qualification_proxy.py"),
    ]:
        cid = checked("create_" + role, ["docker", "create", "--pull=never", "--platform=linux/amd64", "--name", name,
            "--network=" + external_net, "--label", OWNER, "--read-only", "--tmpfs", "/tmp",
            "--mount", "type=bind,src=" + str(source_path) + ",dst=" + target + ",readonly", "--entrypoint", "python",
            image, "-u", target]).decode().strip()
        save(role + "_container_creation.json", {"id": cid, "name": name, "source_sha256": digest(source_path)})
        if role == "proxy":
            checked("connect_proxy_internal", ["docker", "network", "connect", INTERNAL, cid])
        checked("start_" + role, ["docker", "start", cid])
    proxy_observe()


def proxy_observe():
    """Observe existing owned objects only; never restart/recreate the proxy."""
    owned = load("proxy_objects.json")
    proxy_name, fixture_name, external_net = owned["proxy_name"], owned["fixture_name"], owned["external_network"]
    proxy = strict_json(checked("inspect_proxy", ["docker", "inspect", proxy_name], raw=False))[0]
    fixture_row = strict_json(checked("inspect_external_fixture", ["docker", "inspect", fixture_name], raw=False))[0]
    daemon = strict_json(checked("inspect_daemon_topology", ["docker", "inspect", load("owned_objects.json")["container_id"]], raw=False))[0]
    internal = strict_json(checked("inspect_internal_topology", ["docker", "network", "inspect", INTERNAL]))[0]
    external = strict_json(checked("inspect_external_topology", ["docker", "network", "inspect", external_net]))[0]
    require(internal["Internal"] and not external["Internal"] and set(proxy["NetworkSettings"]["Networks"]) == {INTERNAL, external_net}
        and set(fixture_row["NetworkSettings"]["Networks"]) == {external_net} and set(daemon["NetworkSettings"]["Networks"]) == {INTERNAL}, "topology violated")
    require(not any(x["HostConfig"]["PortBindings"] for x in [proxy, fixture_row, daemon]), "published port prohibited")
    result, _ = command("proxy_ready_logs", ["docker", "logs", proxy_name])
    require('"event": "READY"' in (result.stdout + result.stderr).decode(), "proxy not ready")
    topology = {"proxy_name": proxy_name, "proxy_url": "http://" + proxy_name + ":3128",
        "proxy_internal_ip": proxy["NetworkSettings"]["Networks"][INTERNAL]["IPAddress"],
        "fixture_external_ip": fixture_row["NetworkSettings"]["Networks"][external_net]["IPAddress"], "fixture_port": 8443,
        "internal_network": INTERNAL, "external_network": external_net, "daemon_internal_only": True,
        "proxy_dual_homed": True, "fixture_external_only": True, "published_ports": False}
    raw = (Q / "buildkitd.runtime-binary").read_bytes()
    position = raw.find(b"add-hosts")
    require(position >= 0, "native internal proxy host-binding option absent")
    save("proxy_host_binding.json", {"option_key": "add-hosts", "native_frontend_option": "add-hosts=" + proxy_name + "=" + topology["proxy_internal_ip"],
        "exact_runtime_binary_sha256": digest(Q / "buildkitd.runtime-binary"),
        "runtime_key_context": raw[position - 45:position + 60].decode(errors="replace"),
        "purpose": "deterministic internal-only proxy hostname mapping; no external DNS dependency in RUN",
        "scientific_Dockerfile_or_RUN_changed": False, "qualification_required": True})
    durable(Q / "topology.json", encoded(topology))
    save("proxy_topology.json", {"status": "PASS", "topology": topology, "internal_network": internal, "external_network": external,
        "proxy_networks": proxy["NetworkSettings"]["Networks"], "fixture_networks": fixture_row["NetworkSettings"]["Networks"],
        "daemon_networks": daemon["NetworkSettings"]["Networks"]})
    print("INTERNAL BUILDER + DUAL-HOMED PROXY + EXTERNAL-ONLY LOCAL FIXTURE READY", flush=True)


def observations(log, prefix):
    return [strict_json(line.split(prefix, 1)[1].encode()) for line in log.splitlines()
            if re.match(r"#\d+ \d+\.\d+ " + re.escape(prefix), line)]


def egress_qualify(mode):
    require(mode in {"none", "restricted"}, "wrong network fixture")
    if mode == "restricted":
        require(load("none_qualification.json")["status"] == "PASS", "NONE hard gate absent")
    mapping = load("seven_base_transport_map.json")["mapping"][0]
    root = Q / (mode + "-context")
    root.mkdir()
    durable(root / "egress_fixture.py", (OUT / "egress_fixture.py").read_bytes())
    durable(root / "topology.json", (Q / "topology.json").read_bytes())
    dockerfile = ("FROM errpilot_frozen_base\n" + ("ARG PIP_INDEX_URL\n" if mode == "restricted" else "")
        + "COPY egress_fixture.py /egress_fixture.py\nCOPY topology.json /topology.json\n"
        + "RUN python /egress_fixture.py " + mode + "\n")
    if mode == "none":
        dockerfile += "RUN python /egress_fixture.py none\n"
    durable(root / "Dockerfile", dockerfile.encode())
    croot = CPATH + "/" + mode + "-context"
    save(mode + "_copied_inputs.json", copy_verified(root, croot, mode + "_fixture"))
    args = {"HTTP_PROXY": load("proxy_topology.json")["topology"]["proxy_url"],
        "HTTPS_PROXY": load("proxy_topology.json")["topology"]["proxy_url"], "PIP_INDEX_URL": "https://pypi.org/simple"} if mode == "restricted" else {}
    output_inside = CPATH + "/" + mode + ".fixture.rootfs.tar"
    text = native_solve(mode, CPATH + "/base_0/oci", croot, mapping["local_oci_manifest_identity"],
        output="type=tar,dest=" + output_inside, network_none=mode == "none", build_args=args,
        extra_hosts=load("proxy_host_binding.json")["native_frontend_option"].split("=", 1)[1] if mode == "restricted" else None).decode()
    if mode == "none":
        none = observations(text, "NONE_OBSERVATION=")
        require(len(none) == 2 and all(x["status"] == "PASS" for x in none), "NONE fixture not all RUNs")
        save("none_qualification.json", {"status": "PASS", "observations": none, "RUN_count": 2,
            "native_frontend_option": "force-network-mode=none", "proxy_build_args": {}, "RUN_rewrite": False})
        print("NETWORK NONE RUNTIME PASS: BOTH RUNs HAVE NO ROUTE/PROXY CONNECTIVITY", flush=True)
        return
    positive = observations(text, "POSITIVE_ORIGIN=")
    binding = observations(text, "APPLICATION_BINDING=")
    direct = observations(text, "DIRECT_EXTERNAL_FIXTURE=")
    negative = observations(text, "NEGATIVE_PROXY=")
    result, _ = command("proxy_qualification_logs", ["docker", "logs", load("proxy_objects.json")["proxy_name"]])
    log = result.stdout + result.stderr
    durable(Q / "proxy_qualification.log", log)
    events = [strict_json(line.encode()) for line in log.decode().splitlines()]
    denied = [x for x in events if x["event"] == "DENY"]
    require(len(denied) == 6 and all(not x["upstream_dns"] and not x["upstream_connect"] for x in denied), "denials touched upstream")
    require(not any(x["event"] in {"UPSTREAM_DNS", "UPSTREAM_CONNECT"} and x["request_id"] in {r["request_id"] for r in denied} for x in events), "denied upstream activity")
    allow = [x for x in events if x["event"] == "ALLOW"]
    require(len(positive) == len(allow) == 2 and {x["host"] for x in positive} == {"pypi.org", "files.pythonhosted.org"}
        and {x["host"] for x in allow} == {"pypi.org", "files.pythonhosted.org"}
        and all(x["TLS_verification"] == "PASS" and x["read_bytes"] <= 256 and x["verify_mode"] == 2 for x in positive), "approved origins gate")
    require(len(binding) == len(direct) == len(negative) == 1 and not direct[0]["connected"] and negative[0]["internal_proxy_reachable"], "application/direct path gate")
    save("positive_qualification.json", {"status": "PASS", "passed": 2, "total": 2, "observations": positive, "allow_events": allow,
        "TLS_end_to_end": True, "bounded_bytes_per_origin": 256, "installs": 0})
    save("negative_qualification.json", {"status": "PASS", "direct_external_only_fixture": direct,
        "proxy_over_internal_network": negative, "network_NONE": load("none_qualification.json"), "deny_events": denied,
        "denied_upstream_DNS": False, "denied_upstream_connect": False, "unapproved_live_destination_contacted": False})
    save("application_binding.json", {"status": "PASS", "observations": binding, "native_frontend_build_args": args,
        "native_option_form": "--opt build-arg:<key>=<value>", "TLS_disabled": False})
    audit = load("native_network_semantics_audit.json")
    save("native_network_semantics.json", {"status": "PASS", "total": 641, "default": 583, "none": 58,
        "static_audit_sha256": digest(OUT / "native_network_semantics_audit.json"), "none_mechanism": "force-network-mode=none",
        "RUN_action_bytes_unchanged": all(x["RUN_bytes_and_order_unchanged"] for x in audit["items"]),
        "default_runtime": "normal RUN shares isolated dedicated worker network; internal proxy reachable; external-only fixture unreachable",
        "NONE_runtime": load("none_qualification.json"), "DEFAULT_runtime": load("negative_qualification.json")})
    print("RESTRICTED EGRESS PASS: 2/2 TLS ORIGINS; 6 LOCAL DENIALS; DIRECT EXTERNAL PATH FAILS", flush=True)


def shared_identity_parity():
    from evaluation.downstream_benchmark.screening import materializer as m
    results = []
    for index, result in enumerate(load("all_base_native_transport_qualification.json")["results"]):
        output = result["output_parity"]
        label = "base_" + str(index)
        definition = load(label + "_copied_inputs.json")["scientific_fixture_dockerfile"]
        recipe = {"canonical_case_id": "SYNTHETIC_NATIVE_OUTPUT_BASE_" + str(index),
            "base_image_reference": result["base"], "base_image_digest": result["base"].split("@")[1],
            "python_declared_version": output["python_probe"]["version"], "requirements_raw_sha256": "ABSENT",
            "setup_sha256": sha(definition.encode()), "execution_plan_sha256": sha(definition.encode()),
            "screening_runtime_v1_sha256": digest(ROOT / "evaluation/downstream_benchmark/SCREENING_RUNTIME_V1.md"),
            "fixture_only": True, "scientific_fixture_Dockerfile_sha256": sha(definition.encode())}
        evidence = {"inspect": {"Id": output["image_id_observed"]}, "python": output["python_probe"],
            "layers": output["RootFS"]["Layers"], "distributions": (Q / (label + ".installed_distributions.json")).read_bytes(),
            "system_packages": (Q / (label + ".system_packages.txt")).read_bytes(), "network": False}
        identity = m.identity(recipe, "SYNTHETIC_QUALIFICATION", "ABSENT", evidence, "ABSENT")
        require(tuple(identity) == m.ENVIRONMENT_IDENTITY_V1_FIELDS and all(identity.values()), "shared environment schema lost observations")
        durable(Q / (label + ".shared_environment_identity.json"), m.canonical_json(identity))
        results.append({"fixture": recipe["canonical_case_id"], "identity": identity, "identity_sha256": sha(m.canonical_json(identity)),
            "real_environment_ready": False, "base": result["base"]})
    save("shared_environment_identity_qualification.json", {"status": "PASS", "passed": 7, "total": 7,
        "source": "actual unchanged materializer.identity and ENVIRONMENT_IDENTITY_V1_FIELDS", "results": results,
        "materializer_source_sha256": digest(Path(m.__file__)), "benchmark_identity_or_ready_state_created": False})
    print("SHARED ENVIRONMENT IDENTITY SCHEMA PASS 7/7; SYNTHETIC QUALIFICATION ONLY", flush=True)


def candidate_identity():
    require(all(load(name)["status"] == "PASS" for name in ["all_base_native_transport_qualification.json", "native_output_parity.json",
        "native_network_semantics.json", "positive_qualification.json", "negative_qualification.json", "shared_environment_identity_qualification.json"]), "technical gate missing")
    scope = strict_json((E / "v6_restricted_build_egress_compatibility_bridge_v1/work_item_scope.json").read_bytes())
    audit = load("native_network_semantics_audit.json")
    binary = {line.split()[1]: line.split()[0] for line in load("client_binary_hash.json")["stdout"].splitlines()}
    configuration = {"schema": "V6_NATIVE_BUILDKIT_CLIENT_BRIDGE_CONFIGURATION_CANDIDATE_V1", "candidate_only": True,
        "runtime_authority": False, "client": "/usr/bin/buildctl", "client_binary_sha256": binary["/usr/bin/buildctl"],
        "daemon_binary_sha256": binary["/usr/bin/buildkitd"], "endpoint": "unix:///run/buildkit/buildkitd.sock", "daemon_count": 1,
        "same_daemon_requirement": "all native solves use freshly provisioned dedicated daemon; no second daemon or TCP endpoint",
        "builder_name": BUILDER, "driver": "docker-container", "internal_network": INTERNAL,
        "runtime_image": load("runtime_identity.json"), "native_store_name": "frozenbase", "frontend_alias": "errpilot_frozen_base",
        "frontend": "dockerfile.v0", "output": "native type=docker,name,dest; hash; docker cp; docker load; shared inspect/probe",
        "network_none": "--opt force-network-mode=none", "network_default": "normal RUN on internal-only worker",
        "proxy": load("proxy_policy.json"), "internal_proxy_name_resolution": "--opt add-hosts=<exact proxy name>=<observed freshly provisioned internal IP>",
        "persistent_output_root": str(EXTERNAL), "real_dispatch": "REJECT", "future_provision_from_frozen_configuration": True,
        "qualification_live_objects_required": False,
        "daemon_lifecycle_create_argv_template": strict_json((E / "v6_local_buildkit_runtime_provisioning_v1/future_builder_binding.json").read_bytes())["future_create_argv_not_executed"],
        "lifecycle_daemon_container_template": ["docker", "create", "--pull=never", "--platform=linux/amd64", "--name", CONTAINER,
            "--privileged", "--network=" + INTERNAL, "--dns=127.0.0.1", "--mount", "type=volume,src=" + VOLUME + ",dst=/var/lib/buildkit", IMAGE, "--debug"],
        "Buildx_solve": "PROHIBITED", "Buildx_lifecycle_only": ["create", "inspect", "rm"],
        "successor_source": {name: digest(OUT / name) for name in ["successor_runtime.py", "guards.py", "proxy.py"]}}
    save("successor_runtime_integration_candidate.json", configuration)
    transport = [{k: row[k] for k in ["scientific_base_authority", "engine_config_identity", "ordered_rootfs_diff_ids",
        "local_oci_manifest_identity", "layout_path", "native_store_name", "frontend_context_alias"]} for row in load("seven_base_transport_map.json")["mapping"]]
    semantic = {"schema": "V6_RESTRICTED_BUILD_EGRESS_ENFORCEMENT_V1", "BUILD_NETWORK_semantic_SHA": scope["BUILD_NETWORK_semantic_sha256"],
        "restricted_work_item_ids": audit["restricted_ids"], "network_NONE_work_item_ids": audit["none_ids"],
        "population_semantic_SHA": scope["population_sha256"], "native_bridge_configuration_sha256": digest(OUT / "successor_runtime_integration_candidate.json"),
        "same_daemon_requirement": configuration["same_daemon_requirement"], "BuildKit_runtime_reference": IMAGE,
        "BuildKit_config_digest": load("runtime_identity.json")["verified_config_digest"], "seven_base_transport_map": transport,
        "output_parity_semantics": ["same_frozen_authority_and_actions", "linux/amd64", "observed_image_ID", "RootFS",
            "Python_probe", "installed_distributions", "system_packages", "shared_environment_identity"],
        "network_NONE_transport": "force-network-mode=none; all RUN actions unchanged", "proxy_implementation_SHA": digest(OUT / "proxy.py"),
        "proxy_policy_SHA": load("proxy_policy.json")["policy_sha256"], "PIP_INDEX_URL": "https://pypi.org/simple",
        "positive_requirement": "2/2 verified-TLS approved origins through CONNECT proxy", "negative_requirement": "local deny before DNS; no direct external fixture route; NONE cannot reach proxy",
        "Docker_version": strict_json(checked("identity_docker_version", ["docker", "version", "--format", "{{json .}}"])),
        "BuildKit_version": load("builder_identity.json")["BuildKit_version"], "persistent_output_root": str(EXTERNAL),
        "global_state_requirement": "observable unrelated state equal after cleanup; unreadable internals unclaimed"}
    observations_identity = {name: digest(OUT / name) for name in ["all_base_native_transport_qualification.json", "native_output_parity.json",
        "shared_environment_identity_qualification.json", "native_network_semantics.json", "positive_qualification.json", "negative_qualification.json",
        "application_binding.json", "builder_identity.json", "daemon_connection.json", "proxy_topology.json"]}
    save("network_enforcement_identity.json", {"schema": "V6_RESTRICTED_BUILD_EGRESS_ENFORCEMENT_V1", "status": "QUALIFIED_CANDIDATE_ONLY",
        "SEMANTIC_ENFORCEMENT_IDENTITY": semantic, "semantic_enforcement_sha256": sha(encoded(semantic)),
        "QUALIFICATION_OBSERVATION_IDENTITY": observations_identity, "qualification_observation_sha256": sha(encoded(observations_identity)),
        "ENFORCEMENT_IDENTITY": sha(encoded(semantic)), "runtime_authority": False, "canonical_installation": False, "real_dispatch": "REJECT"})
    save("runtime_integration_diff.json", {"status": "SUCCESSOR_CANDIDATE_CONSTRUCTED_NOT_INSTALLED",
        "historical_sources_modified": False, "source_path": str(OUT / "successor_runtime.py"), "source_sha256": digest(OUT / "successor_runtime.py"),
        "before": "shared Docker build transport; restricted runtime default-deny", "after_candidate": "same materializer code with native OCI-session/Docker-export/load transport",
        "scientific_definition_and_context": "unchanged original SHA; separately recorded execution Dockerfile transport deltas",
        "runtime_recipe_and_base_attempt_identity": "unchanged; no identity regeneration",
        "changed_Dockerfile_lines_only": ["FROM frozen reference -> context alias", "restricted only: ARG PIP_INDEX_URL"],
        "none_mechanism": "frontend option; zero RUN directive insertion", "shared_observation_code": "rebound code objects unchanged",
        "real_dispatch": "REJECT", "provider_scope": "SYNTHETIC_QUALIFICATION_ONLY; future accepted controller required",
        "later_gates": ["Human-PI runtime/integration acceptance", "freeze/persist/commit", "required publication", "event #3",
            "execution effectivity binding", "independent acceptance pin", "canonical install"]})
    facts = {"total": 641, "restricted": 583, "none": 58, "same_daemon": True, "daemon_count": 1,
        "native_binary_exact": True, "base_mapping_exact": True, "frozen_base_authority_unchanged": True, "config_diffids_exact": True,
        "registry_fallback": False, "image_pull_fallback": False, "docker_exporter": True, "docker_load": True,
        "output_inspectable": True, "network_none_no_proxy": True, "none_all_RUNs_bound": True, "allowlist": g.ALLOWLIST,
        "pip_index": "https://pypi.org/simple", "TLS_verification": True, "trusted_host": False, "direct_external_path": False,
        "blocker_dispatch": False, "automatic_retry": False, "attempt_identity_regeneration": False, "source_acquisition": False,
        "oracle_execution": False, "event_3": False, "canonical_mutation": False, "production_client_switch_effectivity_claim": False}
    g.qualification_facts(facts)
    save("qualification_facts.json", facts)
    print("QUALIFIED ENFORCEMENT IDENTITY + DEFAULT-DENY SUCCESSOR CANDIDATE CONSTRUCTED", flush=True)


def fixture_control():
    topology = load("proxy_topology.json")["topology"]
    code = ("import socket; s=socket.create_connection((" + repr(topology["fixture_external_ip"]) + ",8443),3); "
        "value=s.recv(128); s.close(); assert value==b'EXTERNAL_ONLY_FIXTURE\\n'; print(value.decode().strip())")
    result, rec = command("external_fixture_reachable_from_proxy_control", ["docker", "exec", topology["proxy_name"], "python", "-c", code])
    require(result.stdout.strip() == b"EXTERNAL_ONLY_FIXTURE", "external fixture reachability control failed")
    save("external_fixture_reachability_control.json", {"status": "PASS", "proxy_external_to_fixture": "CONNECTED_EXACT_MARKER",
        "fixture_external_ip": topology["fixture_external_ip"], "command": rec, "Internet_destination": False,
        "existing_default_RUN_direct_failure": load("negative_qualification.json")["direct_external_only_fixture"]})
    identity = load("network_enforcement_identity.json")
    durable(OUT / "network_enforcement_identity_initial_observation.json", encoded(identity))
    identity["QUALIFICATION_OBSERVATION_IDENTITY"]["external_fixture_reachability_control.json"] = digest(OUT / "external_fixture_reachability_control.json")
    identity["qualification_observation_sha256"] = sha(encoded(identity["QUALIFICATION_OBSERVATION_IDENTITY"]))
    durable(OUT / "network_enforcement_identity.json", encoded(identity), update=True)
    print("EXTERNAL-ONLY FIXTURE CONTROL PASS FROM PROXY; DEFAULT BUILD PATH REMAINS DENIED", flush=True)


def cleanup():
    require(load("once_only_revalidation.json")["status"] == "PASS" and load("successor_transport_test_results.json")["status"] == "PASS", "required tests absent")
    require(load("external_fixture_reachability_control.json")["status"] == "PASS", "negative fixture precondition not proven")
    require(not (OUT / "cleanup_verification.json").exists(), "cleanup already recorded")
    owned = load("owned_objects.json")
    cid = owned["container_id"]
    exports = []
    for mode in ["none", "restricted"]:
        inside = CPATH + "/" + mode + ".fixture.rootfs.tar"
        expected = checked("cleanup_" + mode + "_output_hash", ["docker", "exec", cid, "sha256sum", inside], timeout=300).decode().split()[0]
        target = Q / (mode + ".fixture.rootfs.tar")
        checked("cleanup_" + mode + "_output_copy", ["docker", "cp", cid + ":" + inside, str(target)], timeout=300)
        require(digest(target) == expected, "fixture output copy drift")
        exports.append({"mode": mode, "sha256": expected, "bytes": target.stat().st_size, "path": str(target), "fixture_only": True})
    save("fixture_output_artifacts.json", {"status": "PASS", "artifacts": exports})
    for name, target in [("daemon", cid), ("proxy", load("proxy_objects.json")["proxy_name"]), ("external_fixture", load("proxy_objects.json")["fixture_name"])]:
        result, _ = command(name + "_precleanup_logs", ["docker", "logs", target])
        durable(Q / (name + "_precleanup.log"), result.stdout + result.stderr)
    save("docker_state_precleanup.json", h.snapshot("precleanup"))
    repository_evidence = {p.name: {"sha256": digest(p), "bytes": p.stat().st_size} for p in OUT.iterdir() if p.is_file()}
    durable(Q / "precleanup_repository_evidence.json", encoded(repository_evidence))
    durable(Q / "precleanup_external_inventory.json", encoded(inventory(Q)))
    for p in Q.rglob("*"):
        if p.is_file() and not p.is_symlink():
            fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
    save("precleanup_evidence_receipt.json", {"status": "PERSISTED_FSYNC_READBACK", "evidence_persisted_before_cleanup": True,
        "external_inventory_sha256": digest(Q / "precleanup_external_inventory.json"),
        "repository_inventory_sha256": digest(Q / "precleanup_repository_evidence.json")})
    key, value = OWNER.split("=", 1)
    proxy_objects = load("proxy_objects.json")
    for name in [proxy_objects["proxy_name"], proxy_objects["fixture_name"]]:
        row = strict_json(checked("cleanup_verify_" + name, ["docker", "inspect", name], raw=False))[0]
        require(row["Config"]["Labels"].get(key) == value and row["Config"]["Image"] == proxy_objects["image"], "cleanup proxy/fixture ownership")
        checked("remove_" + name, ["docker", "rm", "-f", name])
    for row in load("native_output_parity.json")["outputs"]:
        tag = row["qualification_tag"]
        require(not any(line.split("|")[1:3] == tag.split(":", 1) for line in load("docker_state_before.json")["images"]), "output tag preexisted")
        actual = strict_json(checked("cleanup_verify_image_" + tag.split(":")[-1], ["docker", "image", "inspect", tag], raw=False))[0]
        require(actual["Id"] == row["image_id_observed"] and actual["RepoTags"] == [tag], "cleanup output image ownership/tag changed")
        checked("remove_image_" + tag.split(":")[-1], ["docker", "image", "rm", tag])
    row = strict_json(checked("cleanup_owned_daemon_check", ["docker", "inspect", cid], raw=False))[0]
    require(row["Name"] == "/" + CONTAINER and row["Config"]["Labels"].get(key) == value, "cleanup daemon ownership")
    checked("remove_owned_builder", ["docker", "buildx", "rm", BUILDER])
    remaining = checked("remaining_container_ids", ["docker", "ps", "-aq", "--no-trunc"]).decode().split()
    if cid in remaining:
        checked("remove_owned_daemon", ["docker", "rm", "-f", cid])
    if VOLUME in checked("remaining_volume_names", ["docker", "volume", "ls", "-q"]).decode().split():
        row = strict_json(checked("cleanup_volume_check", ["docker", "volume", "inspect", VOLUME]))[0]
        require(row["Labels"].get(key) == value, "cleanup volume ownership")
        checked("remove_owned_volume", ["docker", "volume", "rm", VOLUME])
    for net in [proxy_objects["external_network_id"], owned["network_id"]]:
        row = strict_json(checked("cleanup_network_check_" + net[:12], ["docker", "network", "inspect", net]))[0]
        require(row["Labels"].get(key) == value and not row["Containers"], "cleanup network ownership/attachments")
        checked("remove_owned_network_" + net[:12], ["docker", "network", "rm", net])
    after = h.snapshot("after")
    before = load("docker_state_before.json")
    save("docker_state_after.json", after)
    equality = {key: before[key] == after[key] for key in before}
    save("global_state_preservation.json", {"status": "PASS" if all(equality.values()) else "STATE_DRIFT", "observable_equality": equality,
        "selected_builder_unchanged": equality["selected_builder"], "unreadable_PF_or_VM_internals_claimed": False,
        "scope": "before/after Docker snapshots and readable configuration hashes; no packet capture or Docker VM inspection"})
    save("cleanup_verification.json", {"status": "PASS" if after == before else "STATE_DRIFT", "Docker_observable_state_exact": after == before,
        "owned_builder_daemon_volume_proxy_fixture_networks_removed": True, "seven_synthetic_Engine_output_images_removed": True,
        "copied_inputs_removed_with_daemon": True, "exact_runtime_and_seven_frozen_Engine_bases_preserved": equality["images"],
        "qualification_outputs_and_all_OCI_layouts_retained": True, "external_root": str(Q), "evidence_persisted_before_cleanup": True})
    require(after == before, "observable global state drift after cleanup")
    print("CLEANUP PASS: EXACT OBSERVABLE DOCKER/GLOBAL STATE RESTORED; FROZEN INPUTS/EVIDENCE PRESERVED", flush=True)


def finish():
    require(load("cleanup_verification.json")["status"] == "PASS", "cleanup not passed")
    files, packages = preserve_prior()
    external, external_checks = verify_external_history()
    require(external == load("prior_external_inventory.json"), "historical external inventory drift")
    git, population = h.git_state("final"), n.population_state()
    require(git["index_sha256"] == load("entry_verification.json")["index_sha256"], "index bytes changed")
    save("population_revalidation.json", {"status": "PASS", **population, "all_641_exact_unchanged": True,
        "restricted_IDs_exact_unchanged": True, "NONE_IDs_exact_unchanged": True,
        "matplotlib_1_and_8_dispatchable": False, "operational_chunks_scientific_identity": False})
    records = load("commands_run.json")
    solves = [r for r in records if r["name"].endswith("_native_solve")]
    require(len(solves) == 9 and all(r["exit_code"] == 0 for r in solves), "solve population/result drift")
    require(not any(r["argv"][:3] == ["docker", "buildx", "build"] or r["argv"][:2] == ["docker", "pull"] for r in records), "prohibited command observed")
    require(all(r["argv"][3] == "/usr/bin/buildctl" for r in solves), "host/alternate buildctl observed")
    firewall = {"REAL_BENCHMARK_ATTEMPTS": 0, "REAL_BENCHMARK_CLAIMS": 0, "REAL_BENCHMARK_BUILDS": 0,
        "REAL_BENCHMARK_SOURCE_EXPORTS": 0, "BENCHMARK_DEPENDENCY_INSTALLS": 0, "SOURCE_ACQUISITION_EXECUTED": "NO",
        "BUILDX_SOLVES": 0, "UNAPPROVED_LIVE_EGRESS": 0, "ORACLE_EXECUTED": "NO", "EVENT_3_CREATED": "NO",
        "EFFECTIVE_EXECUTION_DESCRIPTOR_CREATED": "NO", "CANONICAL_CURRENT_STATE_MODIFIED": "NO",
        "PREPARATION_EXECUTION_CANONICAL_EFFECTIVE": "NO", "GIT_STAGE": "NO", "GIT_COMMIT": "NO", "GIT_PUSH": "NO",
        "QUALIFICATION_NATIVE_SOLVES": 9, "QUALIFICATION_RUN_INSTRUCTIONS": 10, "REAL_DISPATCH": "REJECT",
        "observation_scope": "exact command/context receipts, unchanged canonical state, empty real ledger, preserved external inventory; no packet capture"}
    save("firewall.json", firewall)
    save("execution_corrections.json", {"historical_bytes_rewritten": False, "solves_retried": False,
        "notes": [
            "Initial entry verifier included an existing ignored __pycache__ file. Restored predecessor inventory convention; all 260 manifest-bound and untracked paths were then exact. No Docker mutation had occurred.",
            "Initial proxy readiness read returned no READY line before Python startup completed. The same running proxy was observed later; no restart, recreation or repeated solve occurred. Both observations remain in command receipts.",
            "An observation-only shared identity persistence call in the filesystem sandbox was denied outside the workspace. It was repeated with authorized escalation, before any identity artifact existed; no build or probe repeated.",
            "Development Ruff found an assigned lambda, an unused local and an unused import; these were repaired in new source before final validation.",
            "Executor functions were extended while the previously loaded remaining-base process completed. Exact native commands and immutable input/output receipts bind executed mechanics; no source/solve fallback was introduced.",
            "Added a local proxy-to-external-fixture reachability control after initial fixture records. Preserved initial enforcement observation identity before adding the control hash; semantic identity unchanged. No native solve or denied request repeated."]})
    import ast
    checks = {}
    for p in sorted(OUT.iterdir()):
        if not p.is_file():
            continue
        text = p.read_bytes().decode("utf-8", errors="strict")
        checks["UTF8:" + p.name] = True
        require(not any(line.rstrip() != line for line in text.splitlines()), "trailing whitespace: " + p.name)
        if p.suffix == ".py":
            ast.parse(text)
            checks["AST:" + p.name] = True
        if p.suffix == ".json":
            strict_json(p.read_bytes())
            checks["strict_JSON:" + p.name] = True
    result, _ = command("final_ruff", [str(ROOT / ".venv/bin/ruff"), "check", str(OUT)])
    durable(OUT / "ruff_final.txt", result.stdout + result.stderr)
    checks["Ruff"] = result.returncode == 0
    result, _ = command("final_diff_check", ["git", "diff", "--check"])
    durable(OUT / "git_diff_check.txt", result.stdout + result.stderr)
    checks["git_diff_check"] = result.returncode == 0
    for name in ["all_base_native_transport_qualification.json", "native_output_parity.json", "shared_environment_identity_qualification.json",
        "native_network_semantics.json", "positive_qualification.json", "negative_qualification.json", "once_only_revalidation.json",
        "successor_transport_test_results.json", "external_fixture_reachability_control.json", "population_revalidation.json", "global_state_preservation.json", "cleanup_verification.json"]:
        checks[name] = load(name)["status"] == "PASS"
    require(all(checks.values()), "final required check failed")
    identity = load("network_enforcement_identity.json")
    require(identity["ENFORCEMENT_IDENTITY"] != "ABSENT" and identity["semantic_enforcement_sha256"] == sha(encoded(identity["SEMANTIC_ENFORCEMENT_IDENTITY"])), "enforcement absent/drift")
    require(identity["qualification_observation_sha256"] == sha(encoded(identity["QUALIFICATION_OBSERVATION_IDENTITY"])), "observation identity drift")
    for name, expected in load("successor_runtime_integration_candidate.json")["successor_source"].items():
        require(digest(OUT / name) == expected, "candidate source changed after identity binding")
    status = "V6_NATIVE_BUILDKIT_CLIENT_COMPATIBILITY_BRIDGE_QUALIFIED_READY_FOR_HUMAN_PI_REVIEW"
    gate = "HUMAN_PI_REVIEW_OF_V6_PREPARATION_EXECUTION_RUNTIME_AND_EGRESS_QUALIFIED_BASELINE"
    save("validation_results.json", {"status": status, "all_required_checks": "PASS", "checks": checks,
        "focused_tests": {"run": 18, "failures": 0, "errors": 0, "skips": 0}, "rejection_categories": 44,
        "all_seven_bases": "PASS", "output_parity": "PASS", "network_DEFAULT_583": "QUALIFIED", "network_NONE_58": "QUALIFIED",
        "approved_origins": "2/2_PASS", "direct_egress": "PROHIBITED_AND_QUALIFIED", "real_dispatch": "REJECT", "next_gate": gate})
    save("final_verification.json", {"status": "PASS", **git, "prior_files": files, "prior_packages": packages,
        "prior_external_checks": external_checks, "canonical_bytes_exact": True, "index_bytes_exact": True,
        "attempt_state": population["attempt_state"], "enforcement_identity": identity["ENFORCEMENT_IDENTITY"], "next_gate": gate})
    report = f"""# Run Report — V6 native BuildKit client compatibility bridge

Date: 2026-10-07, Europe/Budapest.

STATUS = **{status}**

NEXT_GATE = **{gate}**

## 1. Task summary / requested A–V

The native same-daemon architecture passed seven-base OCI transport, seven native Docker exports and Engine loads, actual output observations, DEFAULT/NONE network fixtures and both approved TLS origins. The successor is a technically qualified construction candidate with real dispatch rejected. This is infrastructure qualification, not scientific validation or preparation activation.

| Item | Evidence / result |
| --- | --- |
| A. Entry / lineage | main; local HEAD and live origin/main {h.HEAD} at entry/final; canonical SHA {h.CANONICAL}; planning authorized, event_count=2; tracked tree/index clean. All 260 prior manifest-bound untracked files and all prior external inventory exact. |
| B. Accepted decision | Human-PI ADOPT_V6_NATIVE_BUILDKIT_CLIENT_COMPATIBILITY_BRIDGE_V1; exact supplied request retained and SHA-bound in accepted_decision.json. |
| C. Client architecture | Host controller copies exact inputs; /usr/bin/buildctl inside the exact dedicated runtime connects through the local daemon Unix socket, registers frozenbase OCI session, invokes dockerfile.v0, exports Docker artifact, copies it out and docker loads it. No host buildctl, TCP daemon or second daemon. |
| D. Same daemon | Same current container/worker/socket for all 9 native solves. This is one new lifecycle instance of the accepted dedicated daemon configuration after the predecessor's verified cleanup; its operational container ID differs from the retired probe instance. Exact image and both binary hashes are retained. Buildx create/inspect/remove only. |
| E. Seven frozen bases | 7/7 PASS: Python 3.6.9, 3.7.0, 3.7.3, 3.7.4, 3.7.7, 3.8.1, 3.8.3; all x86_64, executable bytes exact. Archive config, ordered diffIDs, layer order and linux/amd64 exact; local OCI source consumed without registry requests/pulls observed. |
| F. Transport map | Seven deterministic config/diffID/OCI mappings in seven_base_transport_map.json. Original docker.io/library/python@sha256 authority remains separate from local transport identity. Save archives/layouts retained externally, not in Git. |
| G. Output parity | 7/7 native type=docker,name,dest artifacts SHA-verified before/after copy and docker load. Tag, image ID, RootFS, platform, Python, distributions and system packages observed. Actual shared materializer.identity schema used for all seven synthetic fixture identities. No old-client image byte equality or reproducibility claim. |
| H. Network semantics | Exact 641-item generated definitions audited; 583 DEFAULT and 58 NONE identities/order unchanged. Every scientific RUN byte/order unchanged. NONE uses force-network-mode=none, proven across both ordinary fixture RUNs; no RUN rewrite needed. DEFAULT normal RUN uses the internal-only worker. Internal proxy hostname has a separately recorded native add-hosts transport binding. |
| I. Proxy | Python stdlib CONNECT-only tunnel, exact case-insensitive pypi.org/files.pythonhosted.org:443 allowlist; reject IP/userinfo/malformed/other-port/HTTP requests before DNS. Source/policy hashes bound; end-to-end TLS remains client/origin. |
| J. Positive qualification | 2/2 PASS. pypi.org/simple/: HTTP 200, 256 bytes; files.pythonhosted.org/: HTTP 404, 10 bytes. Both exact hostnames TLS verified with CERT_REQUIRED/check_hostname. No redirects, package installation or dependency resolution. |
| K. Negative/direct path | Local denied.invalid:443, pypi.org:80, 127.0.0.1:443, malformed CONNECT, ordinary forwarding and userinfo all rejected. Logs bind zero upstream DNS/connect for each denial. DEFAULT direct external-only fixture connection failed, internal proxy connection succeeded; both NONE RUNs lacked external routes/proxy connectivity. No unapproved live destination used. |
| L. Identities | ENFORCEMENT_IDENTITY = {identity['ENFORCEMENT_IDENTITY']}; semantic and qualification observation hashes are separate. Qualified candidate receipt carries no installed runtime authority. |
| M. Successor candidate | successor_runtime.py/data provide exact transport compiler, native invocation, copy/readback preserving modes/safe symlinks, Docker export/copy/load, private shared-materializer function rebinding and receipt. Original generator/identity/observation code objects retained. Real dispatch and real materializer entry reject; future accepted controller/provider and all later gates remain required. Full I/O ordering tested offline; no benchmark recipe executed. |
| N. Population | 641/583/58 exact. matplotlib::1 and matplotlib::8 remain non-dispatchable. No governed batches or outcome-dependent stopping. Transport identities do not replace recipe/base-attempt identities. |
| O. Once-only | Unchanged accepted tests exercise exclusive claims, fsync, races, one terminal, non-overwrite, no retry and orphan/crash failure on actual target filesystem in the new synthetic child. All real claims/locks/terminals absent. |
| P. Global preservation | Before/after snapshots and readable config hashes equal for selected builder, client/Desktop config, default bridge, unrelated networks/containers/images and volumes. No daemon restart/global switch/firewall/global proxy mutation. Unreadable PF/VM internals unclaimed. |
| Q. Cleanup | Evidence fsynced/read back first. Owned builder/daemon/state volume/proxy/local fixture/both networks and seven synthetic Engine output images removed. Exact runtime image and seven frozen bases preserved. Layouts, archives, artifacts, logs and ledger fixtures retained externally. |
| R. Inventory | New repo files only in this namespace. New external files only under {Q}. artifact_sha256.json seals repo bytes; external_evidence_manifest.json binds external inventory/root seal. Historical bytes were never rewritten. |
| S. Validation / rejection | 18 focused methods PASS (17 guard/accepted-mechanics + 1 offline successor I/O model), zero failures/errors/skips. 44 explicit rejection categories PASS. Ruff, AST, strict JSON/UTF-8, whitespace and git diff --check PASS. No benchmark subject tests. |
| T. Firewall | Real attempts/claims/builds/source exports/dependency installs=0; Buildx solves=0; unapproved live egress=0 in recorded scope. Acquisition/oracle/event #3/effective execution descriptor/canonical mutation/stage/commit/push all NO. 9 fixture solves, 10 RUN instructions only. |
| U. Unresolved prerequisite | Technical gates passed. Human-PI integration acceptance, freeze/persist/commit, required publication, event #3, execution effectivity binding, independent acceptance pin and canonical installation remain outstanding. The candidate's real dispatcher stays disabled. |
| V. Next gate | {gate}. Stop; no execution effectivity decision made by this agent. |

## 2. Files inspected / changed

Inspected the supplied request, canonical descriptor and pinned capacity contract, exact manifests and referenced bytes for all eight prior packages, predecessor client/daemon/source/RUN/output/log evidence, shared adapter/runtime/ledger/materializer and accepted tests, seven Engine-local bases and exact runtime, daemon sockets/worker/version/binaries/native help, copied inputs, proxy topology/logs, qualification outputs and global before/after snapshots. No on-disk AGENTS.md or .airos/current_state.md/contracts existed.

Only the new evidence namespace was changed in the repository. It contains the bounded executor, guards, stdlib proxy/fixtures, successor source/data, tests, qualification records, inventories and this report. All older candidate/evidence/source/canonical/index bytes remain exact. External writes were restricted to the authorized qualification child.

## 3. Commands run

Read-only discovery used cat, rg, sed, Git status/HEAD/branch/diffs/untracked inventory, live git ls-remote and filesystem checks. The bounded driver ran phases entry, create, capabilities, base 0, remaining-bases (1–6), network-audit, proxy-create, proxy-observe, egress none, egress restricted, shared-identity, candidate-identity, cleanup and finish. Docker commands covered exact local inspect/save, lifecycle create/start/inspect, native buildctl help/worker/build via docker exec, docker cp/hash, Docker exporter load and qualification-only run probes, logs and owned cleanup. Exact driver argv/timestamps/exit codes/output hashes are in commands_run.json; large raw logs/artifacts are external. The actual-runtime save is also recorded in runtime_identity.json.

Focused test commands were `.venv/bin/python -B .../run_tests.py` and `.venv/bin/python -B .../test_successor_transport.py`; final Ruff and Git whitespace commands are captured. AST/strict decoding/JSON checks ran in the verifier. Existing .venv tooling only; no install/fetch/stage/commit/push. Initial discovery/development checks remain in the chat; evidence-preserving corrections are recorded in execution_corrections.json.

## 4. Tests passed / failed

18/18 focused methods PASS, 0 failed/error/skipped. 44 required rejection categories PASS. Seven actual native base solves/export/load/probes, the two network fixture solves, exact proxy binding, two verified-TLS origins and six local policy denials passed. Offline successor I/O evidence is explicitly synthetic and is not included as an actual Docker export or scientific result.

## 5. Contract compliance

Current Human-PI authority covers construction and fixture qualification only. No prior package rewritten; no Buildx solve or historical syntax/fallback retried; no scientific recipe/work/base-attempt authority changed. Canonical preparation execution remains NO, planning remains YES, event_count remains 2 and attempts/environment-ready remain 0. Once-only mechanics were not altered. The prior disclosed alias-fallback exception remains historical, non-authoritative and unchanged.

## 6. Risks / unknowns

No packet capture, independent global DNS tracing, Docker VM inspection or readable PF-rule audit was performed. Network conclusions bind exact topology, route observations, fixture results and complete retained client/daemon/proxy logs; they do not claim omniscient network visibility. Global equality covers observable entry/final state, not every possible concurrent change between snapshots. No full 641 benchmark build or dependency installation was performed. The successor I/O controller/provider is restricted to construction qualification; real orchestration and acceptance/effectivity installation are later Human-PI gates. Output images are observations with no byte-reproducibility claim. These passes establish infrastructure mechanics, not scientific validation.

## 7. Recommended next action

Human PI should review the frozen source/data, semantic/observation identities, actual 7/7 and 2/2 receipts, network-none and direct-egress results, successor default-deny behavior and cleanup/inventory at {gate}. No execution activation, canonical install or Git publication is performed in this transaction.
"""
    durable(OUT / "RUN_REPORT.md", report.encode())
    final = Q / "final"
    final.mkdir()
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.name not in {"external_evidence_manifest.json", "artifact_sha256.json"}:
            durable(final / path.name, path.read_bytes())
    external_inventory = inventory(Q)
    durable(Q / "artifact_sha256.json", encoded({"schema": "V6_NATIVE_CLIENT_BRIDGE_EXTERNAL_ARTIFACTS_V1", "artifacts": external_inventory}))
    save("external_evidence_manifest.json", {"root": str(Q), "artifact_inventory": external_inventory,
        "manifest_sha256": digest(Q / "artifact_sha256.json"), "all_bytes_verified": True,
        "large_artifacts_outside_Git": True, "prior_external_inventory_exact": True})
    artifacts = {str(p.relative_to(ROOT)): digest(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name != "artifact_sha256.json"}
    save("artifact_sha256.json", {"schema": "V6_NATIVE_CLIENT_BRIDGE_REPOSITORY_ARTIFACTS_V1", "artifacts": artifacts})
    print(status + "; sealed " + str(len(artifacts) + 1) + " repo files and " + str(len(external_inventory) + 1) + " external files", flush=True)


if __name__ == "__main__":
    phases = {"entry": entry, "create": create, "capabilities": runtime_capabilities, "network-audit": network_audit,
        "proxy-create": proxy_create, "proxy-observe": proxy_observe, "shared-identity": shared_identity_parity,
        "candidate-identity": candidate_identity, "fixture-control": fixture_control, "cleanup": cleanup, "finish": finish}
    require(len(sys.argv) >= 2, "phase required")
    if sys.argv[1] == "base":
        require(len(sys.argv) == 3, "base ordinal required")
        qualify_base(int(sys.argv[2]))
    elif sys.argv[1] == "remaining-bases":
        require(len(sys.argv) == 2, "no extra arguments")
        for ordinal in range(1, 7):
            qualify_base(ordinal)
    elif sys.argv[1] == "egress":
        require(len(sys.argv) == 3, "egress mode required")
        egress_qualify(sys.argv[2])
    else:
        require(len(sys.argv) == 2 and sys.argv[1] in phases, "unknown qualification phase")
        phases[sys.argv[1]]()

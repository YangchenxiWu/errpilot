"""Bounded, phased exact-digest provisioning; no builder or benchmark execution."""
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
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
B = ROOT / "evaluation/downstream_benchmark"
EXTERNAL = Path("/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1")
Q = EXTERNAL / "qualification/local_buildkit_runtime_provisioning_v1"
HEAD = "5c007fbfbfc5b3529105a14f87127f50e1eab6d7"
CANONICAL_SHA = "6a9028c79aa62f90db2b2d53def32ab23bffcfa3c71d2ec30d7fa64e741e3aae"
TAG = "moby/buildkit:buildx-stable-1"
REGISTRY = "https://registry-1.docker.io"
REQUEST = Path("/Users/wuyangchenxi/.codex/attachments/88053db4-ae54-4de6-9536-8131055382c2/已粘贴的文本.txt")
PACKAGES = [("v6_preparation_execution_activation_v1", 14),
            ("v6_preparation_execution_runtime_implementation_v1", 26),
            ("v6_restricted_build_egress_qualification_v1", 29),
            ("v6_restricted_build_egress_compatibility_bridge_v1", 32)]
SUCCESS = "V6_EXACT_BUILDKIT_RUNTIME_PROVISIONED_AND_VERIFIED"
NEXT_GATE = "RESUME_V6_RESTRICTED_BUILD_EGRESS_COMPATIBILITY_BRIDGE_FROM_RUNTIME_GATE"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def encoded(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2,
                       allow_nan=False) + "\n").encode()


def durable(path, raw, *, exclusive=True):
    require(not path.is_symlink(), "refuse symlink output")
    with path.open("xb" if exclusive else "wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def save(name, value):
    durable(OUT / name, encoded(value))


def load(name):
    return json.loads((OUT / name).read_bytes())


def command(name, argv, *, raw=True, timeout=60, check=True):
    if argv[0] == "docker":
        readonly = (argv[1:3] in (["image", "ls"], ["image", "inspect"],
            ["network", "ls"], ["network", "inspect"], ["volume", "ls"],
            ["volume", "inspect"], ["buildx", "inspect"], ["buildx", "version"])
            or argv[1] in {"version", "ps", "inspect"})
        if not readonly:
            identity = load("immutable_runtime_identity.json")
            require(name == "exact_digest_single_pull" and argv == identity["pull_argv"],
                    "Docker mutation forbidden except the frozen single pull")
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=timeout, check=False)
    record = {"name": name, "argv": argv, "exit_code": result.returncode,
              "observed_at_utc": now(), "stdout_sha256": sha(result.stdout),
              "stderr_sha256": sha(result.stderr)}
    if raw:
        record.update(stdout=result.stdout.decode(errors="replace"),
                      stderr=result.stderr.decode(errors="replace"))
    p = OUT / "commands_run.json"
    records = json.loads(p.read_bytes()) if p.exists() else []
    records.append(record)
    durable(p, encoded(records), exclusive=not p.exists())
    if check:
        require(result.returncode == 0, "command failed: " + name)
    return result, record


def checked(name, argv, *, raw=True):
    return command(name, argv, raw=raw)[0].stdout


def preserved():
    files, packages = {}, []
    for package, count in PACKAGES:
        p = B / "evidence" / package / "artifact_sha256.json"
        manifest = json.loads(p.read_bytes())
        require(len(manifest["artifacts"]) + 1 == count, "prior count drift")
        for rel, expected in manifest["artifacts"].items():
            require(sha((ROOT / rel).read_bytes()) == expected, "prior artifact drift: " + rel)
            files[rel] = expected
        rel = str(p.relative_to(ROOT))
        files[rel] = sha(p.read_bytes())
        packages.append({"package": package, "files": count, "manifest_sha256": files[rel]})
    require(len(files) == 101, "prior 101-file inventory")
    return {"files": files, "packages": packages}


def namespace_inventory(root):
    result = {}
    require(root.is_dir() and not root.is_symlink(), "external root unavailable")
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in sorted(dirs + files):
            p = Path(directory) / name
            rel = str(p.relative_to(root))
            if p.is_symlink():
                target = os.readlink(os.fsencode(p))
                result[rel] = {"type": "symlink", "target_b64": base64.b64encode(target).decode(),
                               "sha256": sha(target)}
            elif p.is_file():
                result[rel] = {"type": "file", "bytes": p.stat().st_size,
                               "sha256": sha(p.read_bytes())}
    return result


def check_prior_external():
    observations = []
    p = B / "evidence/v6_preparation_execution_runtime_implementation_v1/external_artifact_sha256.json"
    v = json.loads(p.read_bytes())
    for item in v["artifacts"]:
        q = Path(item["path"])
        if item["entry_type"] == "symlink":
            require(q.is_symlink() and sha(os.readlink(os.fsencode(q))) == item["target_bytes_sha256"],
                    "prior external symlink drift")
        else:
            require(not q.is_symlink() and sha(q.read_bytes()) == item["sha256"],
                    "prior external file drift")
    observations.append({"manifest": str(p.relative_to(ROOT)), "checked": len(v["artifacts"])})
    for package in ["v6_restricted_build_egress_qualification_v1",
                    "v6_restricted_build_egress_compatibility_bridge_v1"]:
        p = B / "evidence" / package / "external_evidence_manifest.json"
        v = json.loads(p.read_bytes())
        root = Path(v["root"])
        items = v.get("artifacts", v.get("artifact_inventory"))
        actual = namespace_inventory(root)
        require(set(actual) == set(items) | {"artifact_sha256.json"}, "prior external inventory drift")
        for rel, item in items.items():
            require(actual[rel]["sha256"] == item["sha256"], "prior external bytes drift")
        expected = v.get("external_manifest_sha256", v.get("manifest_sha256"))
        require(sha((root / "artifact_sha256.json").read_bytes()) == expected, "external manifest drift")
        observations.append({"manifest": str(p.relative_to(ROOT)), "checked": len(actual)})
    return observations


def config_hashes():
    paths = ["/etc/pf.conf", "/etc/docker/daemon.json", "/Users/wuyangchenxi/.docker/daemon.json",
             "/Users/wuyangchenxi/.docker/config.json",
             "/Users/wuyangchenxi/Library/Group Containers/group.com.docker/settings-store.json"]
    result = {}
    for name in paths:
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
        raw = checked(label + "_" + kind + "_inspect", inspect + ids, raw=False) if ids else b"[]"
        rows = json.loads(raw)
        if kind == "containers":
            rows = [{"Id": x["Id"], "Name": x["Name"], "Image": x["Image"], "State": x["State"],
                     "NetworkSettings": x["NetworkSettings"], "inspect_sha256": sha(encoded(x))} for x in rows]
        result[kind] = rows
    lines = sorted(checked(label + "_images", ["docker", "image", "ls", "-a", "--no-trunc",
        "--digests", "--format", "{{.ID}}|{{.Repository}}|{{.Tag}}|{{.Digest}}"]
        ).decode().splitlines())
    result["images"] = lines
    ids = sorted({line.split("|")[0] for line in lines})
    rows = json.loads(checked(label + "_image_inspections", ["docker", "image", "inspect", *ids], raw=False))
    result["image_identities"] = {x["Id"]: {k: x.get(k) for k in
        ["Id", "RepoDigests", "RepoTags", "Architecture", "Os", "RootFS", "Created"]} for x in rows}
    result["selected_builder"] = checked(label + "_selected_builder", ["docker", "buildx", "inspect"]).decode()
    buildx = Path("/Users/wuyangchenxi/.docker/buildx")
    result["buildx_selection_configuration_hashes"] = {str(p.relative_to(buildx)): sha(p.read_bytes())
        for p in sorted(buildx.rglob("*")) if p.is_file() and not p.is_symlink()
        and (p.name in {"current", "defaults"} or "instances" in p.relative_to(buildx).parts)}
    bases = json.loads((B / "evidence/v6_preparation_execution_runtime_implementation_v1/base_runtime_local_status.json").read_bytes())
    result["frozen_python_bases"] = []
    for item in bases["bases"]:
        row = json.loads(checked(label + "_python_" + item["python_version"],
            ["docker", "image", "inspect", item["reference"]], raw=False))[0]
        identity = {k: row[k] for k in item["image_identity"]}
        require(identity == item["image_identity"], "frozen Python image drift")
        result["frozen_python_bases"].append({"reference": item["reference"], "image_identity": identity})
    require(len(result["frozen_python_bases"]) == 7, "seven bases required")
    return result


def git_state(label):
    head = checked(label + "_head", ["git", "rev-parse", "HEAD"]).decode().strip()
    branch = checked(label + "_branch", ["git", "branch", "--show-current"]).decode().strip()
    require((head, branch) == (HEAD, "main"), "HEAD/branch drift")
    checked(label + "_tracked_clean", ["git", "diff", "--exit-code"])
    checked(label + "_index_clean", ["git", "diff", "--cached", "--exit-code"])
    live = checked(label + "_live_origin", ["git", "ls-remote", "--exit-code", "origin", "refs/heads/main"]).decode().strip()
    require(live.split() == [HEAD, "refs/heads/main"], "live origin drift")
    canonical = (B / "v6_current_state.json").read_bytes()
    v = json.loads(canonical)
    require(sha(canonical) == CANONICAL_SHA and v["event_count"] == 2 and
        v["lifecycle_label"] == "PREPARATION_PLANNING_AUTHORIZED" and
        v["projection"]["phase_authorizations"]["PREPARATION_EXECUTION"] == "NO", "canonical drift")
    require(all(not x["attempt_consumed"] and x["phase"] == "NOT_STARTED" and
                x["environment_identity"] is None for x in v["projection"]["case_states"]), "attempt drift")
    return {"head": head, "branch": branch, "live_origin_main": HEAD,
            "canonical_sha256": sha(canonical), "event_count": 2, "preparation_execution": "NO",
            "git_index_sha256": sha((ROOT / ".git/index").read_bytes())}


def entry():
    original = preserved()
    untracked = checked("entry_untracked", ["git", "ls-files", "--others", "--exclude-standard"]).decode().splitlines()
    own = str(OUT.relative_to(ROOT)) + "/"
    require({x for x in untracked if not x.startswith(own)} == set(original["files"]), "untracked inventory drift")
    state = git_state("entry")
    external_checks = check_prior_external()
    external = namespace_inventory(EXTERNAL)
    require(not Q.exists(), "new qualification namespace must be absent")
    require(all(x == "namespace.json" or x.startswith("qualification/") for x in external),
            "unexpected real output/attempt evidence")
    result, observation = command("entry_missing_runtime", ["docker", "image", "inspect", TAG], check=False)
    require(result.returncode != 0 and b"No such image" in result.stderr, "runtime missing prerequisite failed")
    before = snapshot("before")
    require(not any("buildkit" in x.lower() for x in before["images"]), "unexpected local BuildKit image")
    save("docker_state_before.json", before)
    save("accepted_decision.json", {"gate": "HUMAN_PI_DECIDE_V6_LOCAL_BUILDKIT_RUNTIME_PROVISIONING",
        "decision": "AUTHORIZE_V6_EXACT_BUILDKIT_RUNTIME_RESOLUTION_AND_ACQUISITION_V1",
        "request_path": str(REQUEST), "request_sha256": sha(REQUEST.read_bytes()),
        "request_text": REQUEST.read_text(), "scope": "ONE_EXACT_RUNTIME_ONLY_NO_BUILDER_NO_ATTEMPTS"})
    save("entry_verification.json", {**state, "observed_at_utc": now(), "prior_repository_inventory": original,
        "prior_external_inventory": external, "prior_external_manifest_checks": external_checks,
        "missing_runtime_observation": observation, "local_present": False,
        "airos_current_state_exists": (ROOT / ".airos/current_state.md").exists(),
        "airos_contracts_exists": (ROOT / ".airos/contracts").exists(),
        "runtime_execution_or_integration_authorized": False,
        "external_qualification_root": str(Q), "entry_untracked_prior_files": 101})
    print(json.dumps({"phase": "entry", "status": "PASS", "prior_files": 101,
                      "external_artifacts": len(external), "frozen_python_bases": 7}), flush=True)


def resolve():
    require(not (OUT / "pull_attempt_guard.json").exists(), "resolution must precede acquisition")
    load("entry_verification.json")
    observations = []
    token_url = "https://auth.docker.io/token?service=registry.docker.io&scope=repository%3Amoby%2Fbuildkit%3Apull"
    with urlopen(Request(token_url), timeout=60) as response:
        auth = json.load(response)
        observations.append({"method": "GET", "url": token_url, "status": response.status,
                             "bearer_token": "EPHEMERAL_NOT_PERSISTED"})
    token = auth.get("token", auth.get("access_token"))
    require(isinstance(token, str), "public registry authorization unavailable")
    accept = ", ".join(["application/vnd.oci.image.index.v1+json",
        "application/vnd.docker.distribution.manifest.list.v2+json", "application/vnd.oci.image.manifest.v1+json",
        "application/vnd.docker.distribution.manifest.v2+json"])

    def metadata(path, filename, expected=None):
        url = REGISTRY + "/v2/moby/buildkit/" + path
        with urlopen(Request(url, headers={"Accept": accept, "Authorization": "Bearer " + token}), timeout=60) as response:
            raw = response.read(4 * 1024 * 1024 + 1)
            require(len(raw) <= 4 * 1024 * 1024, "oversized metadata")
            digest = "sha256:" + sha(raw)
            header = response.headers.get("Docker-Content-Digest")
            require(header is None or header == digest, "registry header/body digest disagreement")
            require(expected is None or digest == expected, "registry expected digest disagreement")
            observations.append({"method": "GET", "url": url, "status": response.status,
                "content_type": response.headers.get("Content-Type"), "docker_content_digest": header,
                "body_sha256": sha(raw), "bytes": len(raw), "persisted_raw_metadata": filename})
        durable(OUT / filename, raw)
        return json.loads(raw), digest, raw

    top, top_digest, top_raw = metadata("manifests/buildx-stable-1", "registry_index.raw.json")
    require(top["schemaVersion"] == 2, "unsupported schema")
    if "manifests" in top:
        candidates = [x for x in top["manifests"] if x.get("platform", {}).get("os") == "linux"
            and x.get("platform", {}).get("architecture") == "amd64"
            and x.get("platform", {}).get("variant", "") in {"", "v1"}]
        require(len(candidates) == 1, "linux/amd64 absent or ambiguous")
        child_descriptor = candidates[0]
        child, child_digest, child_raw = metadata("manifests/" + child_descriptor["digest"],
            "registry_amd64_manifest.raw.json", child_descriptor["digest"])
        require(len(child_raw) == child_descriptor["size"], "child size mismatch")
    else:
        child, child_digest, child_raw = top, top_digest, top_raw
        child_descriptor = {"digest": child_digest, "mediaType": child["mediaType"], "size": len(child_raw)}
        durable(OUT / "registry_amd64_manifest.raw.json", child_raw)
    config_digest = child["config"]["digest"]
    config, observed_config_digest, config_raw = metadata("blobs/" + config_digest,
        "registry_config.raw.json", config_digest)
    require(len(config_raw) == child["config"]["size"], "config size mismatch")
    require(config["os"] == "linux" and config["architecture"] == "amd64", "config platform mismatch")
    require(config["rootfs"]["type"] == "layers" and
            len(config["rootfs"]["diff_ids"]) == len(child["layers"]), "config/layer cardinality")
    pull_reference = "moby/buildkit@" + top_digest
    resolution = {"status": "PASS_UNAMBIGUOUS_METADATA_ONLY", "logical_tag": TAG,
        "registry": "docker.io", "registry_endpoint": REGISTRY, "resolved_at_utc": now(),
        "top_level_digest": top_digest, "top_level_media_type": top["mediaType"],
        "linux_amd64_manifest_digest": child_digest, "child_manifest_media_type": child["mediaType"],
        "child_descriptor": child_descriptor, "config_digest": observed_config_digest,
        "layers": child["layers"], "http_metadata_observations": observations,
        "layer_blob_requests": 0, "image_pulls": 0, "immutable_pull_reference": pull_reference}
    save("registry_resolution.json", resolution)
    identity = {"status": "FROZEN_BEFORE_ACQUISITION", "logical_tag": TAG, "platform": "linux/amd64",
        "frozen_at_utc": now(), "registry": "docker.io", "top_level_digest": top_digest,
        "top_level_media_type": top["mediaType"], "linux_amd64_manifest_digest": child_digest,
        "config_digest": config_digest, "registry_layer_digests": [x["digest"] for x in child["layers"]],
        "rootfs_diff_ids": config["rootfs"]["diff_ids"], "immutable_pull_reference": pull_reference,
        "pull_argv": ["docker", "image", "pull", "--platform=linux/amd64", pull_reference],
        "registry_resolution_sha256": sha((OUT / "registry_resolution.json").read_bytes()),
        "raw_metadata_sha256": {name: sha((OUT / name).read_bytes()) for name in
            ["registry_index.raw.json", "registry_amd64_manifest.raw.json", "registry_config.raw.json"]}}
    save("immutable_runtime_identity.json", identity)
    print(json.dumps({"phase": "resolve", "status": identity["status"],
        "top_level_digest": top_digest, "amd64_manifest_digest": child_digest,
        "config_digest": config_digest, "pull_reference": pull_reference}), flush=True)


def acquire():
    identity = load("immutable_runtime_identity.json")
    entry_record = load("entry_verification.json")
    require(preserved() == entry_record["prior_repository_inventory"], "prior repository drift")
    require(namespace_inventory(EXTERNAL) == entry_record["prior_external_inventory"], "prior external drift")
    require(snapshot("prepull") == load("docker_state_before.json"), "prepull Docker state drift")
    require(identity["status"] == "FROZEN_BEFORE_ACQUISITION", "identity not frozen")
    for name, digest in identity["raw_metadata_sha256"].items():
        require(sha((OUT / name).read_bytes()) == digest, "frozen metadata drift")
    require(sha((OUT / "registry_resolution.json").read_bytes()) == identity["registry_resolution_sha256"],
            "frozen resolution drift")
    require(re.fullmatch(r"moby/buildkit@sha256:[0-9a-f]{64}", identity["immutable_pull_reference"]), "not exact digest")
    save("pull_attempt_guard.json", {"immutable_identity_sha256": sha((OUT / "immutable_runtime_identity.json").read_bytes()),
        "started_at_utc": now(), "argv": identity["pull_argv"], "maximum_pull_invocations": 1,
        "automatic_retry": False})
    print("Executing the one frozen linux/amd64 digest pull.", flush=True)
    result, observation = command("exact_digest_single_pull", identity["pull_argv"], timeout=1800, check=False)
    durable(OUT / "pull.stdout.txt", result.stdout)
    durable(OUT / "pull.stderr.txt", result.stderr)
    save("pull_observation.json", {**observation, "status": "PASS" if result.returncode == 0 else "BLOCKED_PULL_FAILED",
        "pull_invocations": 1, "immutable_identity_sha256": sha((OUT / "immutable_runtime_identity.json").read_bytes()),
        "argv_sha256": sha(encoded(identity["pull_argv"])), "stdout_path": "pull.stdout.txt",
        "stderr_path": "pull.stderr.txt", "tag_only_pull": False, "other_image_pulls": 0})
    require(result.returncode == 0, "single pull failed; no automatic retry")
    print(json.dumps({"phase": "acquire", "status": "PASS", "pull_reference": identity["immutable_pull_reference"]}), flush=True)


def verify():
    identity = load("immutable_runtime_identity.json")
    pull = load("pull_observation.json")
    require(pull["exit_code"] == 0 and pull["pull_invocations"] == 1, "pull incomplete")
    ref = identity["immutable_pull_reference"]
    raw = checked("local_exact_runtime_inspect", ["docker", "image", "inspect", "--platform=linux/amd64", ref], raw=False)
    rows = json.loads(raw)
    require(len(rows) == 1, "local runtime identity ambiguous")
    image = rows[0]
    require(image["Os"] == "linux" and image["Architecture"] == "amd64", "local platform mismatch")
    require(any(x.split("@")[-1] == identity["top_level_digest"] and
        x.split("@")[0] in {"moby/buildkit", "docker.io/moby/buildkit"} for x in image["RepoDigests"]),
        "RepoDigest mismatch")
    require(image["RootFS"]["Type"] == "layers" and image["RootFS"]["Layers"] == identity["rootfs_diff_ids"],
        "RootFS diff-ID mismatch")
    archive_argv = ["docker", "image", "save", "--platform=linux/amd64", ref]
    with tempfile.TemporaryFile(dir="/private/tmp") as archive:
        process = subprocess.run(archive_argv, cwd=ROOT, stdout=archive, stderr=subprocess.PIPE, timeout=600)
        require(process.returncode == 0, "local archive export failed")
        archive.seek(0)
        archive_hash = hashlib.sha256()
        for block in iter(lambda: archive.read(1024 * 1024), b""):
            archive_hash.update(block)
        archive.seek(0)
        members, documents = {}, {}
        with tarfile.open(fileobj=archive, mode="r|") as tar:
            for member in tar:
                if not member.isfile():
                    continue
                stream = tar.extractfile(member)
                h = hashlib.sha256()
                small = bytearray() if member.size <= 4 * 1024 * 1024 else None
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    h.update(block)
                    if small is not None:
                        small.extend(block)
                members[member.name] = {"size": member.size, "sha256": h.hexdigest()}
                if small is not None:
                    try:
                        documents[member.name] = (json.loads(small), bytes(small))
                    except (ValueError, UnicodeDecodeError):
                        pass
        config_matches = [name for name, item in members.items() if "sha256:" + item["sha256"] == identity["config_digest"]]
        require(len(config_matches) == 1, "exact local config bytes missing/ambiguous")
        local_config, config_raw = documents[config_matches[0]]
        require(config_raw == (OUT / "registry_config.raw.json").read_bytes(), "local config byte mismatch")
        require(local_config["rootfs"]["diff_ids"] == image["RootFS"]["Layers"], "local config RootFS mismatch")
        require("manifest.json" in documents, "local archive Docker manifest unavailable")
        manifest = documents["manifest.json"][0]
        require(len(manifest) == 1 and manifest[0]["Config"] == config_matches[0], "archive config binding")
        layers = manifest[0]["Layers"]
        require(len(layers) == len(identity["registry_layer_digests"]), "archive layer count mismatch")
        layer_evidence = []
        for i, name in enumerate(layers):
            actual = "sha256:" + members[name]["sha256"]
            registry_digest = identity["registry_layer_digests"][i]
            diff_id = identity["rootfs_diff_ids"][i]
            require(actual in {registry_digest, diff_id}, "exported layer bytes mismatch")
            layer_evidence.append({"archive_member": name, "actual_digest": actual,
                "registry_compressed_layer_digest": registry_digest, "uncompressed_diff_id": diff_id,
                "match": "REGISTRY_BLOB" if actual == registry_digest else "ROOTFS_DIFF_ID"})
    archive_observation = {"argv": archive_argv, "exit_code": process.returncode,
        "stdout_archive_sha256": archive_hash.hexdigest(), "stderr_sha256": sha(process.stderr),
        "archive_members": members, "local_config_member": config_matches[0],
        "local_config_sha256": sha(config_raw), "layer_verification": layer_evidence,
        "extract_to_filesystem": False, "archive_retained": False, "image_pull_or_run": False}
    save("local_archive_verification.json", archive_observation)
    save("local_identity_verification.json", {"status": "PASS_EXACT_LOCAL_BYTES",
        "registry_top_level_digest": identity["top_level_digest"],
        "registry_linux_amd64_manifest_digest": identity["linux_amd64_manifest_digest"],
        "registry_config_digest": identity["config_digest"], "verified_local_config_digest": "sha256:" + sha(config_raw),
        "engine_image_id": image["Id"], "engine_id_is_config_digest": image["Id"] == identity["config_digest"],
        "engine_id_semantics": "OBSERVED_SEPARATELY_FROM_VERIFIED_CONFIG_BYTES",
        "RepoDigests": image["RepoDigests"], "RepoTags_observation_only": image.get("RepoTags"),
        "Architecture": image["Architecture"], "Os": image["Os"], "RootFS": image["RootFS"],
        "Created_observation_only": image.get("Created"), "inspect_stdout_sha256": sha(raw),
        "config_bytes_equal_registry": True, "all_local_layers_verified": True,
        "archive_verification_sha256": sha((OUT / "local_archive_verification.json").read_bytes())})
    previous = json.loads((B / "evidence/v6_restricted_build_egress_compatibility_bridge_v1/builder_configuration.json").read_bytes())
    planned = [x if x != "--driver-opt=image=" + TAG else "--driver-opt=image=" + ref for x in previous["planned_create_argv"]]
    save("future_builder_binding.json", {"status": "FROZEN_REFERENCE_ONLY_BUILDER_NOT_CREATED",
        "builder_name": previous["name"], "driver": "docker-container",
        "driver_options": {**previous["driver_options"], "image": ref},
        "exact_driver_opt": "--driver-opt=image=" + ref, "future_create_argv_not_executed": planned,
        "builder_creation_executed": False, "bootstrap_executed": False, "use_executed": False,
        "immutable_runtime_identity_sha256": sha((OUT / "immutable_runtime_identity.json").read_bytes()),
        "prior_builder_configuration_sha256": sha((B / "evidence/v6_restricted_build_egress_compatibility_bridge_v1/builder_configuration.json").read_bytes())})
    print(json.dumps({"phase": "verify", "status": "PASS_EXACT_LOCAL_BYTES", "engine_image_id": image["Id"],
        "config_digest": identity["config_digest"], "layers_verified": len(layer_evidence)}), flush=True)


def finish():
    identity, local, entry_record = load("immutable_runtime_identity.json"), load("local_identity_verification.json"), load("entry_verification.json")
    store = load("docker_engine_store_identity.json")
    before = load("docker_state_before.json")
    after = snapshot("after")
    save("docker_state_after.json", after)
    checks = {key + "_unchanged": before[key] == after[key] for key in before if key not in {"images", "image_identities"}}
    checks["old_image_identities_unchanged"] = all(after["image_identities"].get(k) == v for k,v in before["image_identities"].items())
    added = sorted(set(after["images"]) - set(before["images"]))
    removed = sorted(set(before["images"]) - set(after["images"]))
    new_ids = sorted(set(after["image_identities"]) - set(before["image_identities"]))
    checks["only_exact_runtime_image_added"] = (not removed and len(added) == 1 and
        added[0].split("|") == [store["engine_store_image_id"], "moby/buildkit", "<none>", identity["top_level_digest"]]
        and new_ids == [store["engine_store_image_id"]])
    final_git = git_state("final")
    checks["git_index_unchanged"] = final_git["git_index_sha256"] == entry_record["git_index_sha256"]
    checks["prior_101_repository_files_unchanged"] = preserved() == entry_record["prior_repository_inventory"]
    checks["prior_external_namespace_exact"] = namespace_inventory(EXTERNAL) == entry_record["prior_external_inventory"]
    checks["canonical_state_unchanged"] = final_git["canonical_sha256"] == entry_record["canonical_sha256"]
    checks["single_exact_digest_pull"] = sum(x["name"] == "exact_digest_single_pull" for x in load("commands_run.json")) == 1
    checks["exact_local_bytes"] = local["status"] == "PASS_EXACT_LOCAL_BYTES"
    checks["immutable_freeze_precedes_pull"] = identity["frozen_at_utc"] < load("pull_attempt_guard.json")["started_at_utc"]
    require(all(checks.values()), "preservation checks failed: " + repr(checks))
    firewall = {"BUILDERS_CREATED": 0, "BENCHMARK_ATTEMPTS_CONSUMED": 0,
        "BENCHMARK_IMAGE_BUILDS": 0, "BENCHMARK_DEPENDENCIES_INSTALLED": 0,
        "SOURCE_ACQUISITION_EXECUTED": "NO", "EVENT_3_CREATED": "NO",
        "CANONICAL_CURRENT_STATE_MODIFIED": "NO", "GIT_STAGE": "NO", "GIT_COMMIT": "NO", "GIT_PUSH": "NO",
        "RUNTIME_IMAGE_PULL_INVOCATIONS": 1, "OTHER_IMAGE_PULLS": 0,
        "BUILDER_BOOTSTRAP_EXECUTED": "NO", "BRIDGE_QUALIFICATION_EXECUTED": "NO"}
    save("validation_results.json", {"status": SUCCESS, "checks": checks, "checks_passed": len(checks),
        "checks_failed": 0, "final_git": final_git, "docker_state_delta": {"added_image_rows": added,
        "removed_image_rows": removed, "added_engine_image_ids": new_ids}, "firewall": firewall,
        "scientific_validation_claimed": False, "next_gate": NEXT_GATE,
        "limitations": ["Docker Desktop VM daemon config is not directly readable; host config hashes and observed Engine/builder surfaces compared.",
            "No BuildKit process was started; worker version, frozen-base bridge transport, output parity and restricted egress remain unqualified.",
            "Before/after snapshots establish observed state preservation, not concurrent host activity between snapshots."]})
    report = f"""# Run Report — exact local BuildKit runtime provisioning

Date: 2026-10-06, Europe/Budapest.

STATUS = {SUCCESS}

## 1. Task summary / A–G runtime provenance

Human-PI gate `HUMAN_PI_DECIDE_V6_LOCAL_BUILDKIT_RUNTIME_PROVISIONING` authorized metadata resolution, immutable freezing, one exact-digest linux/amd64 runtime pull, and local verification. The supplied request is bound in accepted_decision.json. No builder was created.

| Identity | Frozen / observed value |
| --- | --- |
| A. Logical tag | `{TAG}` |
| Registry / media type | `docker.io` / `{identity['top_level_media_type']}` |
| B. Top-level digest | `{identity['top_level_digest']}` |
| C. linux/amd64 manifest | `{identity['linux_amd64_manifest_digest']}` |
| D. Registry and verified local config digest | `{identity['config_digest']}` |
| D. Engine store/index image ID | `{store['engine_store_image_id']}` |
| D. Engine selected linux/amd64 image ID | `{local['engine_image_id']}` |
| E. Exact pull reference | `{identity['immutable_pull_reference']}` |
| F. Local verification | RepoDigest and platform match; exported config bytes equal registry config; all {len(identity['rootfs_diff_ids'])} exported layers match registry blob or frozen uncompressed diff ID; RootFS matches config. |
| G. Future builder binding | `--driver-opt=image={identity['immutable_pull_reference']}` |

The immutable identity file was fsynced before the single pull. No tag-only pull or runtime substitution occurred. Registry compressed layer digests and config uncompressed diff IDs remain distinct. This containerd Engine reports the index digest for its store identity and the child manifest digest for a platform-selected inspect; neither is the config digest. local_identity_verification.json retains the platform-selected observation, docker_engine_store_identity.json separately binds the store/index observation, and local archive bytes verify the config independently. Created metadata and RepoTags are observations only. Future create argv is persisted but unexecuted.

## 2. Files inspected and changed / I inventories

Inspected: all 101 files in the four prior inventories (14 activation, 26 runtime implementation, 29 restricted-egress audit, 32 compatibility bridge), their manifest-bound external evidence, canonical current state, seven frozen Python image identities, prior builder configuration, Docker networks/containers/volumes/images/selected builder, host config hashes, and exact registry index/child/config metadata. All prior files remain exact.

Only this new repository directory was written: `{OUT.relative_to(ROOT)}`. It contains the requested 11 files plus the phased executor, accepted decision, raw registry metadata, single-pull guard/logs, archive verification, command ledger and external inventory. External copies are confined to `{Q}` within the existing qualification namespace. No benchmark attempt ID is used. artifact_sha256.json inventories repository bytes and excludes its own hash. external_evidence_manifest.json pins the external manifest and all external copy hashes.

## 3. Commands run

`provision_runtime.py entry`, `resolve`, `acquire`, `verify`, `store`, `finish`, `publish`, `seal` are separate bounded phases. commands_run.json preserves exact Docker/Git argv, exit codes and stdout/stderr hashes for captured commands. The local `docker image save --platform=linux/amd64` command and archive hash are in local_archive_verification.json. Read-only HTTPS metadata GETs for this exact repository are in registry_resolution.json; the short-lived public bearer token was not persisted. Only top index, amd64 manifest and config metadata were requested before pulling; no layer blob was requested in resolution.

The one mutation argv was `{identity['pull_argv']}`. Exact stdout/stderr bytes and hashes are retained in pull.stdout.txt, pull.stderr.txt and pull_observation.json. No install, source fetch, base pull, build, run, retag, Docker network/container mutation or daemon restart occurred. Preliminary read-only tool observations verified entry and CLI help; the initial sandbox Docker connection was denied, and the authorized elevated read succeeded.

## 4. Tests / H Docker state delta

{len(checks)} focused provenance/preservation checks passed, zero failed; no implementation unit suite was needed because only provisioning evidence was added. One runtime image row / one Engine image ID was added; none removed. All prior image identities and seven frozen bases are unchanged. Networks, containers, volumes, default builder selection/configuration and readable host configuration files are unchanged. Exact local exported config and layers were hashed without extracting archive members or starting a container. See validation_results.json and docker_state_before/after.json.

## 5. Contract compliance / J firewall

Required main HEAD and queried LIVE origin/main are both `{HEAD}` at entry and final verification. Canonical SHA remains `{CANONICAL_SHA}`, state PREPARATION_PLANNING_AUTHORIZED, event_count=2, PREPARATION_EXECUTION=NO. Index unchanged. No on-disk .airos state/contracts were present. The supplied global instructions and explicit transaction boundary govern this run.

BUILDERS_CREATED=0; BENCHMARK_ATTEMPTS_CONSUMED=0; BENCHMARK_IMAGE_BUILDS=0; BENCHMARK_DEPENDENCIES_INSTALLED=0; SOURCE_ACQUISITION_EXECUTED=NO; EVENT_3_CREATED=NO; CANONICAL_CURRENT_STATE_MODIFIED=NO; GIT_STAGE=NO; GIT_COMMIT=NO; GIT_PUSH=NO. Only one exact runtime pull was executed. Prior evidence was neither modified nor republished.

## 6. Risks and unknowns

Docker Desktop VM daemon config is not directly readable; preservation is established on host configuration hashes and observed Docker/Buildx surfaces. Snapshots do not rule out unrelated concurrent activity between observations. BuildKit process/version, all-seven-base bridge transport, output/load parity and restricted build egress have not been qualified. Runtime provisioning success is not benchmark or scientific validation.

## 7. Recommended next action

NEXT_GATE = {NEXT_GATE}

Resume the existing bridge from its runtime prerequisite using the exact immutable driver option in future_builder_binding.json. This provisioning transaction stops here; no builder creation or bridge qualification is executed.
"""
    durable(OUT / "RUN_REPORT.md", report.encode())
    print(json.dumps({"phase": "finish", "status": SUCCESS, "checks_passed": len(checks),
                      "docker_added_image_rows": len(added), "firewall": firewall}), flush=True)


def store():
    identity, local = load("immutable_runtime_identity.json"), load("local_identity_verification.json")
    raw = checked("local_engine_store_inspect", ["docker", "image", "inspect", identity["immutable_pull_reference"]], raw=False)
    rows = json.loads(raw)
    require(len(rows) == 1, "store identity ambiguous")
    image = rows[0]
    require(image["Id"] == identity["top_level_digest"], "Engine store identity drift")
    require(image["Descriptor"]["digest"] == identity["top_level_digest"] and
        image["Descriptor"]["mediaType"] == identity["top_level_media_type"], "Engine index descriptor mismatch")
    require(local["engine_image_id"] == identity["linux_amd64_manifest_digest"], "Engine platform identity mismatch")
    save("docker_engine_store_identity.json", {"status": "PASS_SEPARATE_INDEX_PLATFORM_AND_CONFIG_IDENTITIES",
        "engine_store_image_id": image["Id"], "engine_platform_selected_image_id": local["engine_image_id"],
        "verified_config_digest": identity["config_digest"], "RepoDigests": image["RepoDigests"],
        "Descriptor": image["Descriptor"], "inspect_stdout_sha256": sha(raw),
        "local_platform_verification_sha256": sha((OUT / "local_identity_verification.json").read_bytes()),
        "note": "Containerd store/index Id and platform-selected inspect Id are distinct; config bytes are independently verified. Earlier platform observation retained unchanged."})
    print(json.dumps({"phase": "store", "status": "PASS", "engine_store_image_id": image["Id"]}), flush=True)


def publish():
    entry_record = load("entry_verification.json")
    require(namespace_inventory(EXTERNAL) == entry_record["prior_external_inventory"], "external baseline drift before publication")
    require(load("validation_results.json")["status"] == SUCCESS, "provisioning not verified")
    require(not Q.exists(), "qualification output already exists")
    Q.mkdir()
    sources = [p for p in sorted(OUT.iterdir()) if p.is_file() and p.name not in
        {"external_evidence_manifest.json", "artifact_sha256.json"}]
    for source in sources:
        durable(Q / source.name, source.read_bytes())
        require((Q / source.name).read_bytes() == source.read_bytes(), "external copy mismatch")
    artifacts = namespace_inventory(Q)
    manifest = {"schema": "V6_LOCAL_BUILDKIT_RUNTIME_EXTERNAL_ARTIFACTS_V1", "status": SUCCESS,
                "root": str(Q), "qualification_only": True, "real_attempts": 0,
                "artifacts": artifacts, "self_hash_excluded": True, "file_count_including_manifest": len(artifacts)+1}
    durable(Q / "artifact_sha256.json", encoded(manifest))
    save("external_evidence_manifest.json", {"root": str(Q), "namespace": "qualification",
        "status": "PASS_EXCLUSIVE_DURABLE_COPY", "artifact_inventory": artifacts,
        "manifest_sha256": sha((Q / "artifact_sha256.json").read_bytes()),
        "file_count_including_manifest": len(artifacts)+1, "benchmark_attempt_id": None,
        "all_copy_bytes_verified": True, "prior_external_artifacts_unchanged": True})
    after = namespace_inventory(EXTERNAL)
    prior = {k: v for k, v in after.items() if not k.startswith("qualification/local_buildkit_runtime_provisioning_v1/")}
    require(prior == entry_record["prior_external_inventory"], "prior external preservation failed")
    print(json.dumps({"phase": "publish", "external_artifacts": len(artifacts)+1, "status": "PASS"}), flush=True)


def seal():
    entry_record = load("entry_verification.json")
    require(preserved() == entry_record["prior_repository_inventory"], "prior repo preservation failed")
    record = load("external_evidence_manifest.json")
    require(sha((Q / "artifact_sha256.json").read_bytes()) == record["manifest_sha256"], "external manifest drift")
    external = namespace_inventory(Q)
    require({k:v for k,v in external.items() if k != "artifact_sha256.json"} == record["artifact_inventory"], "external inventory mismatch")
    for rel in record["artifact_inventory"]:
        require((Q / rel).read_bytes() == (OUT / rel).read_bytes(), "repository/external byte mismatch")
    own = str(OUT.relative_to(ROOT)) + "/"
    all_untracked = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT).decode().splitlines()
    require({x for x in all_untracked if not x.startswith(own)} == set(entry_record["prior_repository_inventory"]["files"]),
            "unrelated untracked drift")
    require(sha((ROOT / ".git/index").read_bytes()) == entry_record["git_index_sha256"], "index drift at seal")
    artifacts = {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in sorted(OUT.iterdir())
                 if p.is_file() and p.name != "artifact_sha256.json"}
    save("artifact_sha256.json", {"schema": "V6_LOCAL_BUILDKIT_RUNTIME_ARTIFACT_SHA256_V1", "status": SUCCESS,
        "artifacts": artifacts, "file_count_including_manifest": len(artifacts)+1, "self_hash_excluded": True,
        "external_manifest_sha256": record["manifest_sha256"], "external_artifacts": len(external),
        "prior_repository_files_preserved": 101, "git_stage_commit_push": False, "real_attempts": 0})
    require(all(sha((ROOT / rel).read_bytes()) == digest for rel,digest in artifacts.items()), "sealed bytes mismatch")
    print(json.dumps({"phase": "seal", "status": SUCCESS, "repository_files": len(artifacts)+1,
                      "external_artifacts": len(external), "next_gate": NEXT_GATE}), flush=True)


if __name__ == "__main__":
    require(len(sys.argv) == 2 and sys.argv[1] in {"entry", "resolve", "acquire", "verify", "store", "finish", "publish", "seal"}, "phase required")
    try:
        globals()[sys.argv[1]]()
    except Exception as error:
        p = OUT / ("blocked_" + sys.argv[1] + ".json")
        if not p.exists():
            durable(p, encoded({"status": "BLOCKED", "phase": sys.argv[1], "error_type": type(error).__name__,
                               "error": str(error), "observed_at_utc": now(), "automatic_retry": False}))
        raise

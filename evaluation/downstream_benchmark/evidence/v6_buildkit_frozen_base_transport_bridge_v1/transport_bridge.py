"""Offline, qualification-only Engine archive equivalence and OCI transport gate.

Exact config and uncompressed tar-stream bytes are used. Gzip decoding changes
only the encoding; no filesystem extraction, tar repacking, registry fallback,
image pull, real attempt, or canonical write is performed.
Dependent phases may be added only after this first archive gate passes.
"""
from __future__ import annotations

import hashlib
import gzip
import importlib.util
import json
import os
import re
import subprocess
import sys
import tarfile
from pathlib import Path, PurePosixPath

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
E = OUT.parent
PRIOR = E / "v6_restricted_build_egress_compatibility_bridge_resume_v1"
EXTERNAL = Path("/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1")
Q = EXTERNAL / "qualification/buildkit_frozen_base_transport_bridge_v1"
REQUEST = Path("/Users/wuyangchenxi/.codex/attachments/eca44c60-f949-44e2-8711-a4d59c5803ab/已粘贴的文本.txt")
ARCHIVE_BLOCK = "V6_BUILDKIT_FROZEN_BASE_TRANSPORT_ARCHIVE_EQUIVALENCE_BLOCKED"
NAMED_BLOCK = "V6_BUILDKIT_FROZEN_BASE_TRANSPORT_NAMED_CONTEXT_BLOCKED"
NEXT = "HUMAN_PI_REVIEW_OF_V6_BUILDKIT_FROZEN_BASE_TRANSPORT_NAMED_CONTEXT_BLOCK"
spec = importlib.util.spec_from_file_location("prior_resume_read_helpers", PRIOR / "resume_bridge.py")
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
prior.OUT = OUT  # Helper observations write exclusively to the NEW namespace.
prior.Q = Q
sha, require, durable, encoded = prior.sha, prior.require, prior.durable, prior.encoded
save, load, checked, command = prior.save, prior.load, prior.checked, prior.command


class ArchiveRejected(ValueError):
    """A strict pre-construction equality or archive safety condition failed."""

def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ArchiveRejected("duplicate JSON key: " + key)
            result[key] = value
        return result
    def invalid(value):
        raise ArchiveRejected("nonfinite JSON: " + value)
    return json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=pairs,
                      parse_constant=invalid)


def file_sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def digest_path(digest):
    if not isinstance(digest, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise ArchiveRejected("invalid SHA256 identity")
    return "blobs/sha256/" + digest.split(":")[1]


def inspect_archive(path, expected, observation):
    """Validate exact config and raw ordered layer bytes before any layout write.

    The exact frozen manifest retained by Engine's save binds its observed
    config descriptor. Containerd image inspect's Id is the registry manifest,
    so it must never be mislabeled as the config digest.
    """
    def check(name, condition):
        observation.setdefault("checks", {})[name] = bool(condition)
        if not condition:
            raise ArchiveRejected(name)
    with tarfile.open(path, mode="r:") as archive:
        members = archive.getmembers()
        names = [m.name for m in members]
        check("unique_archive_member_names", len(names) == len(set(names)))
        check("safe_regular_files_and_directories", all(
            not PurePosixPath(m.name).is_absolute() and ".." not in PurePosixPath(m.name).parts
            and (m.isfile() or m.isdir()) for m in members))
        lookup = {m.name: m for m in members}
        observation["archive_members"] = [
            {"name": m.name, "size": m.size, "type": "file" if m.isfile() else "directory"}
            for m in members]
        def read(name):
            check("regular_member:" + name, name in lookup and lookup[name].isfile())
            return archive.extractfile(lookup[name]).read()
        manifest = strict_json(read("manifest.json"))
        check("exactly_one_intended_image", isinstance(manifest, list) and len(manifest) == 1)
        entry = manifest[0]
        frozen = expected["reference"].split("@", 1)[1]
        frozen_raw = read(digest_path(frozen))
        check("frozen_registry_manifest_bytes_exact", "sha256:" + sha(frozen_raw) == frozen)
        frozen_manifest = strict_json(frozen_raw)
        check("image_manifest_schema", frozen_manifest.get("schemaVersion") == 2
              and isinstance(frozen_manifest.get("layers"), list))
        config_digest = frozen_manifest["config"]["digest"]
        check("legacy_config_matches_frozen_manifest", entry["Config"] == digest_path(config_digest))
        config_raw = read(entry["Config"])
        check("config_bytes_exact", "sha256:" + sha(config_raw) == config_digest
              and len(config_raw) == frozen_manifest["config"]["size"])
        config = strict_json(config_raw)
        check("linux_amd64", (config.get("os"), config.get("architecture")) == ("linux", "amd64"))
        diff_ids = config["rootfs"]["diff_ids"]
        check("rootfs_diff_ids_exact", diff_ids == expected["image_identity"]["RootFS"]["Layers"])
        check("rootfs_type_layers", config["rootfs"]["type"] == "layers")
        layers = entry["Layers"]
        frozen_layers = frozen_manifest["layers"]
        check("layer_count_exact", len(layers) == len(diff_ids) == len(frozen_layers))
        check("layer_order_frozen_manifest_exact", layers == [digest_path(x["digest"]) for x in frozen_layers])
        observation.update(frozen_registry_identity=expected["reference"],
            engine_config_identity=config_digest, engine_config_observation_source=
            "EXACT_ENGINE_SAVE_FROZEN_MANIFEST_CONFIG_DESCRIPTOR_VERIFIED_BY_MANIFEST_SHA256",
            config_bytes_sha256=sha(config_raw), config_bytes_size=len(config_raw),
            config_rootfs_diff_ids=diff_ids, engine_rootfs_diff_ids=expected["image_identity"]["RootFS"]["Layers"],
            ordered_archive_layer_members=layers, ordered_registry_layer_descriptors=frozen_layers,
            layer_count=len(layers), layers_checked=[])
        for i, (name, diff_id, descriptor) in enumerate(zip(layers, diff_ids, frozen_layers)):
            payload = read(name)
            actual = "sha256:" + sha(payload)
            is_gzip = descriptor["mediaType"] == "application/vnd.docker.image.rootfs.diff.tar.gzip"
            check("supported_layer_encoding:" + str(i), is_gzip or descriptor["mediaType"] in {
                "application/vnd.oci.image.layer.v1.tar", "application/vnd.docker.image.rootfs.diff.tar"})
            detail = {"ordinal": i, "member": name, "size": len(payload),
                "saved_payload_sha256": actual, "expected_rootfs_diff_id": diff_id,
                "registry_layer_digest": descriptor["digest"],
                "registry_media_type": descriptor["mediaType"],
                "gzip_header_observed": payload[:2] == b"\x1f\x8b",
                "raw_saved_bytes_equal_diff_id": actual == diff_id,
                "encoding": "gzip" if is_gzip else "uncompressed_tar"}
            observation["layers_checked"].append(detail)
            check("saved_layer_descriptor_exact:" + str(i),
                  actual == descriptor["digest"] and len(payload) == descriptor["size"])
            # DiffIDs hash the exact UNCOMPRESSED tar stream. Gzip decoding
            # neither unpacks files nor changes any tar header/content byte.
            stream = archive.extractfile(lookup[name])
            if is_gzip:
                stream = gzip.GzipFile(fileobj=stream, mode="rb")
            hasher = hashlib.sha256()
            uncompressed_size = 0
            with stream:
                while chunk := stream.read(1024 * 1024):
                    hasher.update(chunk)
                    uncompressed_size += len(chunk)
            detail.update(uncompressed_tar_sha256="sha256:" + hasher.hexdigest(),
                          uncompressed_tar_size=uncompressed_size,
                          gzip_decoded_without_filesystem_unpack=is_gzip)
            check("uncompressed_tar_bytes_equal_rootfs_diff_id:" + str(i),
                  "sha256:" + hasher.hexdigest() == diff_id)
        observation["status"] = "PASS_ARCHIVE_EQUIVALENCE"
        return config_raw, layers, diff_ids


def construct_layout(archive_path, destination, expected, observation):
    """Deterministic stdlib-only OCI layout; never write before all equalities."""
    config_raw, layers, diff_ids = inspect_archive(archive_path, expected, observation)
    require(not destination.exists(), "no overwrite/automatic regeneration")
    destination.mkdir()
    (destination / "blobs/sha256").mkdir(parents=True)
    def blob(raw):
        digest = "sha256:" + sha(raw)
        path = destination / digest_path(digest)
        if path.exists():
            require(path.read_bytes() == raw, "content address collision")
        else:
            durable(path, raw)
        return {"digest": digest, "size": len(raw)}
    config_descriptor = {"mediaType": "application/vnd.oci.image.config.v1+json", **blob(config_raw)}
    layer_descriptors = []
    with tarfile.open(archive_path, mode="r:") as archive:
        for name, diff_id, detail in zip(layers, diff_ids, observation["layers_checked"]):
            stream = archive.extractfile(name)
            if detail["encoding"] == "gzip":
                stream = gzip.GzipFile(fileobj=stream, mode="rb")
            path = destination / digest_path(diff_id)
            hasher, size = hashlib.sha256(), 0
            with stream, path.open("xb") as output:
                while chunk := stream.read(1024 * 1024):
                    output.write(chunk)
                    hasher.update(chunk)
                    size += len(chunk)
                output.flush()
                os.fsync(output.fileno())
            require("sha256:" + hasher.hexdigest() == diff_id
                    and size == detail["uncompressed_tar_size"]
                    and file_sha(path) == diff_id.split(":")[1], "archive changed after verification")
            layer_descriptors.append({"mediaType": "application/vnd.oci.image.layer.v1.tar",
                                      "digest": diff_id, "size": size})
    manifest = {"schemaVersion": 2, "mediaType": "application/vnd.oci.image.manifest.v1+json",
                "config": config_descriptor, "layers": layer_descriptors}
    transport = {"mediaType": manifest["mediaType"], **blob(encoded(manifest)),
                 "platform": {"os": "linux", "architecture": "amd64"}}
    durable(destination / "oci-layout", encoded({"imageLayoutVersion": "1.0.0"}))
    durable(destination / "index.json", encoded({"schemaVersion": 2, "manifests": [transport]}))
    observation.update(local_oci_path=str(destination), transport_manifest_identity=transport["digest"],
                       transport_identity_is_scientific_base_identity=False)
    return transport


def validate_layout(destination, observation):
    """Read-only integrity check of an already constructed candidate layout."""
    if not destination.is_dir() or destination.is_symlink():
        raise ArchiveRejected("missing local OCI layout")
    inventory = prior.inventory(destination)
    if any(row["type"] != "file" for row in inventory.values()):
        raise ArchiveRejected("OCI symlink forbidden")
    expected_manifest = observation["transport_manifest_identity"]
    expected_config = observation["engine_config_identity"]
    for digest in [expected_manifest, expected_config, *observation["config_rootfs_diff_ids"]]:
        path = destination / digest_path(digest)
        if not path.is_file() or path.is_symlink() or file_sha(path) != digest.split(":")[1]:
            raise ArchiveRejected("OCI blob mutation or missing blob: " + digest)
    layout = strict_json((destination / "oci-layout").read_bytes())
    index = strict_json((destination / "index.json").read_bytes())
    if layout != {"imageLayoutVersion": "1.0.0"} or index.get("schemaVersion") != 2 or len(index["manifests"]) != 1:
        raise ArchiveRejected("OCI layout/index mismatch")
    desc = index["manifests"][0]
    if desc["digest"] != expected_manifest or desc["platform"] != {"os": "linux", "architecture": "amd64"}:
        raise ArchiveRejected("wrong OCI manifest or platform")
    manifest_raw = (destination / digest_path(expected_manifest)).read_bytes()
    manifest = strict_json(manifest_raw)
    if desc["size"] != len(manifest_raw) or manifest["config"]["digest"] != expected_config:
        raise ArchiveRejected("OCI config descriptor mismatch")
    if [x["digest"] for x in manifest["layers"]] != observation["config_rootfs_diff_ids"]:
        raise ArchiveRejected("OCI layer order mismatch")
    for layer in manifest["layers"]:
        if layer["mediaType"] != "application/vnd.oci.image.layer.v1.tar" or \
                (destination / digest_path(layer["digest"])).stat().st_size != layer["size"]:
            raise ArchiveRejected("OCI layer media type/size mismatch")
    if strict_json((destination / digest_path(expected_config)).read_bytes())["rootfs"]["diff_ids"] != observation["config_rootfs_diff_ids"]:
        raise ArchiveRejected("OCI rootfs diffID mismatch")
    expected_files = {"oci-layout", "index.json", digest_path(expected_manifest), digest_path(expected_config),
                      *(digest_path(x) for x in observation["config_rootfs_diff_ids"])}
    if set(inventory) != expected_files:
        raise ArchiveRejected("OCI file population drift")
    return inventory


def validate_qualification_firewall(descriptor_raw, population, real_claims):
    """Exact accepted population and planning-only state; no new identities."""
    from evaluation.downstream_benchmark.screening import v6_preparation_runtime as r
    if sha(descriptor_raw) != prior.CANONICAL:
        raise ArchiveRejected("canonical descriptor changed/event #3/real attempt claim")
    descriptor = strict_json(descriptor_raw)
    if descriptor["event_count"] != 2 or descriptor["projection"]["phase_authorizations"]["PREPARATION_EXECUTION"] != "NO":
        raise ArchiveRejected("event #3 or execution effectivity")
    if population != r.population():
        raise ArchiveRejected("641/583/58 or blocker/attempt identity drift")
    if real_claims or any(row["attempt_consumed"] for row in descriptor["projection"]["case_states"]):
        raise ArchiveRejected("real attempt claim")


def entry():
    files, packages = prior.preserved()
    manifest = strict_json((PRIOR / "artifact_sha256.json").read_bytes())
    for rel, digest in manifest["artifacts"].items():
        require(sha((ROOT / rel).read_bytes()) == digest, "prior resume bytes drift: " + rel)
        files[rel] = digest
    rel = str((PRIOR / "artifact_sha256.json").relative_to(ROOT))
    files[rel] = sha((ROOT / rel).read_bytes())
    actual = {str(p.relative_to(ROOT)) for p in PRIOR.iterdir() if p.is_file()}
    require(actual == set(manifest["artifacts"]) | {rel}, "prior resume population drift")
    require(len(files) == 162, "prior file population drift")
    own = str(OUT.relative_to(ROOT)) + "/"
    untracked = checked("entry_untracked", ["git", "ls-files", "--others", "--exclude-standard"]).decode().splitlines()
    require({x for x in untracked if not x.startswith(own)} == set(files), "unrelated dirty paths")
    g = prior.git_state("entry")
    external_checks = prior.prior_external_checks()
    resume_external = strict_json((PRIOR / "external_evidence_manifest.json").read_bytes())
    require(prior.inventory(Path(resume_external["root"])) == resume_external["artifact_inventory"],
            "prior resume external bytes drift")
    require(not Q.exists() and not Q.is_symlink(), "external namespace collision")
    require(not (ROOT / ".airos/current_state.md").exists(), "new AIROS state needs review")
    require(not (ROOT / ".airos/contracts").exists(), "new AIROS contracts need review")
    sys.path.insert(0, str(ROOT))
    from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a
    from evaluation.downstream_benchmark.screening import v6_preparation_runtime as r
    descriptor, plans = a.load_inputs()
    population = r.population()
    validate_qualification_firewall((ROOT / a.CURRENT).read_bytes(), population, prior.attempt_state()["real_ledger_claims"])
    require(a.derive_population(plans) == population, "work item identity drift")
    scope = strict_json((PRIOR / "work_item_scope.json").read_bytes())
    restricted = [x["base_attempt_id"] for x in population["items"] if x["build_network_required"]]
    none = [x["base_attempt_id"] for x in population["items"] if not x["build_network_required"]]
    require((len(population["items"]), len(restricted), len(none)) == (641, 583, 58)
            and restricted == scope["restricted_work_item_ids"]
            and none == scope["network_none_work_item_ids"], "641/583/58 drift")
    blockers = [p for p in plans["plans"] if p["case_id"] in {"matplotlib::1", "matplotlib::8"}]
    # The accepted input validator binds both blocker states, plus the full
    # derive_population equality excludes them from dispatchable work items.
    require(not any(x["case_id"] in {"matplotlib::1", "matplotlib::8"}
                    for x in population["items"]), "blocker dispatch")
    first_prior = strict_json((PRIOR / "first_base_transport_qualification.json").read_bytes())
    require(first_prior["status"] == "V6_RESTRICTED_BUILD_EGRESS_BRIDGE_BASE_IMAGE_TRANSPORT_BLOCKED"
            and first_prior["BuildKit_consumption"] == "FAILED_BEFORE_RUN"
            and 'Head "https://registry-1.docker.io/' in first_prior["stderr"], "prior mechanism mismatch")
    save("accepted_decision.json", {"owner": "HUMAN_PI", "gate": "HUMAN_PI_DECIDE_V6_BUILDKIT_FROZEN_BASE_TRANSPORT_BRIDGE",
        "decision": "ADOPT_V6_ENGINE_IMAGE_TO_LOCAL_OCI_CONTEXT_TRANSPORT_V1",
        "action": "OPEN_V6_BUILDKIT_FROZEN_BASE_TRANSPORT_BRIDGE_AND_RESUME",
        "request_path": str(REQUEST), "request_sha256": sha(REQUEST.read_bytes()),
        "exact_request": REQUEST.read_text(), "scope": "LOCAL_TRANSPORT_AND_SYNTHETIC_QUALIFICATION_ONLY",
        "real_preparation_authorized": False, "stage_commit_push_authorized": False})
    save("entry_verification.json", {"status": "PASS", **g, "prior_file_hashes": files,
        "prior_packages": packages, "prior_file_count": len(files), "prior_external_checks": external_checks,
        "resume_external_count": len(resume_external["artifact_inventory"]),
        "lifecycle_label": descriptor["lifecycle_label"], "event_count": descriptor["event_count"],
        "phase_authorizations": descriptor["projection"]["phase_authorizations"],
        "blocker_plans": blockers, "attempt_state": prior.attempt_state(),
        "airos_current_state": "ABSENT", "airos_contracts": "ABSENT", "observed_at_utc": prior.now()})
    save("prior_external_inventory.json", prior.inventory(EXTERNAL))
    save("work_item_scope.json", scope)
    save("builder_runtime_verification.json", prior.runtime_verify("entry"))
    bases = strict_json((E / "v6_preparation_execution_runtime_implementation_v1/base_runtime_local_status.json").read_bytes())["bases"]
    for i, base in enumerate(bases):
        row = strict_json(checked("base_" + str(i) + "_inspect", ["docker", "image", "inspect", base["reference"]]))[0]
        require({k: row[k] for k in base["image_identity"]} == base["image_identity"], "frozen base changed")
        base["engine_inspect_observation"] = row
    save("frozen_base_authorities.json", {"bases": bases, "count": len(bases),
        "scientific_base_identity_policy": "ORIGINAL_FROZEN_REGISTRY_DIGEST_ONLY",
        "OCI_transport_identity": "NOT_YET_ESTABLISHED"})
    save("docker_state_before.json", prior.snapshot("before"))
    print("ENTRY PASS: exact 162 prior files, runtime and 7 bases; 641/583/58 preserved", flush=True)


def export_first():
    require(load("entry_verification.json")["status"] == "PASS", "entry gate")
    base = load("frozen_base_authorities.json")["bases"][0]
    row = strict_json(checked("first_base_preexport", ["docker", "image", "inspect", base["reference"]]))[0]
    require({k: row[k] for k in base["image_identity"]} == base["image_identity"], "preexport base drift")
    require(not Q.exists(), "no external overwrite")
    Q.mkdir()
    archive_path = Q / "first_base.docker-save.tar"
    argv = ["docker", "image", "save", base["reference"]]
    started = prior.now()
    with archive_path.open("xb") as stream:
        result = subprocess.run(argv, cwd=ROOT, stdout=stream, stderr=subprocess.PIPE, timeout=55, check=False)
        stream.flush()
        os.fsync(stream.fileno())
    durable(Q / "docker-save.stderr.txt", result.stderr)
    rec = {"argv": argv, "started_at_utc": started, "finished_at_utc": prior.now(),
           "exit_code": result.returncode, "archive_path": str(archive_path),
           "archive_size": archive_path.stat().st_size, "archive_sha256": file_sha(archive_path),
           "stderr_sha256": sha(result.stderr), "exact_frozen_reference": base["reference"],
           "network": "NONE_LOCAL_ENGINE_SAVE", "intended_images": 1,
           "selected_base_rule": "FIRST_IN_ACCEPTED_ORDERED_SEVEN_BASE_LEDGER"}
    save("archive_export_inventory.json", {"exports": [rec], "large_artifacts_in_git": False})
    require(result.returncode == 0, "Docker image save failed")
    observation = {"status": "NOT_YET_ESTABLISHED", "archive_path": str(archive_path),
        "archive_sha256": rec["archive_sha256"], "filesystem_unpack_repack": False,
        "layer_mutation": False, "gzip_decoding": "ENCODING_ONLY_EXACT_TAR_STREAM",
        "tar_repack": False, "OCI_layout_written": False}
    try:
        construct_layout(archive_path, Q / "first_base.oci", base, observation)
    except (ArchiveRejected, KeyError, ValueError, tarfile.TarError) as exc:
        observation.update(status=ARCHIVE_BLOCK, failed_condition=str(exc),
                           transport_manifest_identity=None, OCI_layout_written=False)
        save("oci_layout_construction.json", observation)
        save("first_base_transport_result.json", {"status": ARCHIVE_BLOCK,
            "frozen_registry_identity": base["reference"], "archive_equivalence": "FAIL",
            "BuildKit_consumption": "NOT_RUN_ARCHIVE_HARD_GATE", "expected_python_patch": base["python_version"],
            "failed_condition": str(exc), "registry_requests_during_local_OCI_builds": 0,
            "qualification_Docker_objects_created": 0})
        print(json.dumps({"status": ARCHIVE_BLOCK, "failed_condition": str(exc),
                          "first_layer": observation.get("layers_checked", [])[:1]}), flush=True)
        return
    observation["OCI_layout_written"] = True
    save("oci_layout_construction.json", observation)
    print("ARCHIVE PASS: continue authorized first BuildKit consumption gate", flush=True)


def recover_first_encoding_check():
    """Preserve and correct the compressed-digest versus diffID check error."""
    old = load("oci_layout_construction.json")
    require(old["failed_condition"] == "raw_saved_layer_bytes_equal_rootfs_diff_id:0"
            and old["layers_checked"][0]["gzip_header_observed"], "not the identified encoding check error")
    for source, target in [("oci_layout_construction.json", "archive_encoding_initial_observation.json"),
                           ("first_base_transport_result.json", "first_base_initial_encoding_check.json")]:
        require(not (OUT / target).exists(), "revision evidence collision")
        (OUT / source).rename(OUT / target)
    save("execution_corrections.json", {"initial_check_error": "COMPRESSED_DISTRIBUTION_DIGEST_COMPARED_TO_UNCOMPRESSED_DIFF_ID",
        "initial_observations_preserved": True, "replacement_rule":
        "SHA256_OF_GZIP_DECODED_EXACT_TAR_STREAM_EQUALS_DIFF_ID; NO_FILESYSTEM_UNPACK_OR_TAR_REPACK",
        "actual_required_equality_failure_observed_before_correction": False,
        "archive_reexported": False, "archive_bytes_changed": False})
    base = load("frozen_base_authorities.json")["bases"][0]
    export = load("archive_export_inventory.json")["exports"][0]
    path = Path(export["archive_path"])
    require(file_sha(path) == export["archive_sha256"], "export drift")
    observation = {"archive_path": str(path), "archive_sha256": export["archive_sha256"],
        "filesystem_unpack_repack": False, "tar_repack": False, "layer_mutation": False,
        "gzip_decoding": "ENCODING_ONLY_EXACT_TAR_STREAM", "OCI_layout_written": False}
    try:
        transport = construct_layout(path, Q / "first_base.oci", base, observation)
    except (ArchiveRejected, KeyError, ValueError, tarfile.TarError) as exc:
        observation.update(status=ARCHIVE_BLOCK, failed_condition=str(exc),
                           transport_manifest_identity=None)
        save("oci_layout_construction.json", observation)
        save("first_base_transport_result.json", {"status": ARCHIVE_BLOCK, "archive_equivalence": "FAIL",
             "BuildKit_consumption": "NOT_RUN_ARCHIVE_HARD_GATE", "failed_condition": str(exc)})
        print(ARCHIVE_BLOCK + ": " + str(exc), flush=True)
        return
    observation.update(OCI_layout_written=True, status="PASS_ARCHIVE_EQUIVALENCE",
                       config_bytes_exact=True, rootfs_diff_ids_exact=True, layer_order_exact=True,
                       gzip_decoding_does_not_mutate_tar_stream=True)
    save("oci_layout_construction.json", observation)
    print("ARCHIVE PASS: exact config and all 9 uncompressed tar diffIDs; local OCI " + transport["digest"], flush=True)


def create_builder():
    require(load("oci_layout_construction.json")["status"] == "PASS_ARCHIVE_EQUIVALENCE", "archive gate")
    cfg = strict_json((PRIOR / "builder_configuration.json").read_bytes())
    cfg["ownership_label"] = "errpilot.v6.qualification=buildkit_frozen_base_transport_bridge_v1"
    prior.OWNER = cfg["ownership_label"]
    save("builder_configuration.json", cfg)
    require(not any(x["Name"] == prior.INTERNAL for x in load("docker_state_before.json")["networks"]),
            "network collision")
    absent, _ = command("builder_absence", ["docker", "buildx", "inspect", prior.BUILDER], check=False)
    require(absent.returncode != 0 and b"no builder" in absent.stderr.lower(), "builder collision")
    prior.create()


def observe_builder():
    prior.OWNER = load("builder_configuration.json")["ownership_label"]
    prior.observe()


def first_consume():
    require(load("builder_creation_observation.json")["status"] == "PASS_DRIVER_RUNTIME_INTERNAL_NETWORK", "builder gate")
    construction = load("oci_layout_construction.json")
    require(construction["status"] == "PASS_ARCHIVE_EQUIVALENCE", "archive gate")
    base = load("frozen_base_authorities.json")["bases"][0]
    layout = Path(construction["local_oci_path"])
    layout_inventory = validate_layout(layout, construction)
    require(all(row["sha256"] == name.split("/")[-1] for name, row in layout_inventory.items()
                if name.startswith("blobs/sha256/")), "OCI blob drift")
    manifest = construction["transport_manifest_identity"]
    original = ("FROM " + base["reference"] + "\nRUN python --version\n").encode()
    context = Q / "first-base-context"
    context.mkdir()
    durable(context / "Dockerfile", original)
    tag = "errpilot-v6-frozen-transport-first:qualification"
    result, _ = command("output_tag_absent", ["docker", "image", "inspect", tag], check=False)
    require(result.returncode != 0 and b"No such image" in result.stderr, "output tag collision")
    common = ["docker", "buildx", "build", "--builder=" + prior.BUILDER, "--platform=linux/amd64",
        "--network=none", "--no-cache", "--progress=plain", "--load"]
    source = "oci-layout://" + str(layout) + "@" + manifest
    argv = common + ["--build-context", base["reference"] + "=" + source,
                    "-t", tag, "-f", str(context / "Dockerfile"), str(context)]
    result, exact_rec = command("first_exact_reference_context", argv, check=False, timeout=55)
    durable(Q / "first_exact_reference.stdout.txt", result.stdout)
    durable(Q / "first_exact_reference.stderr.txt", result.stderr)
    combined = (result.stdout + result.stderr).decode(errors="replace")
    mode, execution = "EXACT_REFERENCE_CONTEXT_OVERRIDE", original
    attempts = [exact_rec]
    if result.returncode != 0:
        require(not any(x in combined for x in ["registry-1.docker.io", "auth.docker.io", "https://registry"]),
                "V6_BUILDKIT_FROZEN_BASE_TRANSPORT_REGISTRY_DEPENDENCY_BLOCKED")
        # Fallback only for a CLI/frontend named-context NAME parsing failure.
        name_failure = bool(re.search(r"(?i)(invalid context name|context.*invalid.*name)", combined))
        if not name_failure:
            save("first_base_transport_result.json", {"status": "V6_BUILDKIT_FROZEN_BASE_TRANSPORT_NAMED_CONTEXT_BLOCKED",
                "exact_reference_attempt": exact_rec, "fallback_authorized_for_observed_failure": False,
                "frozen_registry_identity": base["reference"], "archive_equivalence": "PASS"})
            print("NAMED CONTEXT BLOCKED: " + combined, flush=True)
            return
        execution = original.replace(base["reference"].encode(), b"errpilot_frozen_base", 1)
        durable(context / "Dockerfile.transport", execution)
        mode = "SINGLE_TRANSPORT_ALIAS_SUBSTITUTION"
        argv = common + ["--build-context", "errpilot_frozen_base=" + source,
            "-t", tag, "-f", str(context / "Dockerfile.transport"), str(context)]
        result, fallback = command("first_authorized_alias_context", argv, check=False, timeout=55)
        attempts.append(fallback)
        durable(Q / "first_alias.stdout.txt", result.stdout)
        durable(Q / "first_alias.stderr.txt", result.stderr)
        combined = (result.stdout + result.stderr).decode(errors="replace")
    logs, logrec = command("builder_logs_after_transport", ["docker", "logs", "--timestamps", prior.CONTAINER])
    durable(Q / "builder_after_first.stdout.log", logs.stdout)
    durable(Q / "builder_after_first.stderr.log", logs.stderr)
    registry = any(x in combined + logrec["stdout"] + logrec["stderr"]
                   for x in ["registry-1.docker.io", "auth.docker.io", "https://registry"])
    delta = {"mode": mode, "original_Dockerfile_sha256": sha(original),
        "execution_Dockerfile_sha256": sha(execution), "original_bytes": original.decode(),
        "execution_bytes": execution.decode(), "original_FROM_source": base["reference"],
        "execution_FROM_source": "errpilot_frozen_base" if mode != "EXACT_REFERENCE_CONTEXT_OVERRIDE" else base["reference"],
        "exact_one_token_delta": mode != "EXACT_REFERENCE_CONTEXT_OVERRIDE",
        "other_delta": False, "SCIENTIFIC_RECIPE_IDENTITY": "UNCHANGED", "FROZEN_BASE_IDENTITY": "UNCHANGED",
        "EXECUTION_TRANSPORT_IDENTITY": "NEW_AND_SEPARATE"}
    save("dockerfile_transport_delta.json", delta)
    record = {"status": "PASS" if result.returncode == 0 and not registry else
        "V6_BUILDKIT_FROZEN_BASE_TRANSPORT_REGISTRY_DEPENDENCY_BLOCKED" if registry else
        "V6_BUILDKIT_FROZEN_BASE_TRANSPORT_NAMED_CONTEXT_BLOCKED",
        "archive_equivalence": "PASS", "FROM_TRANSPORT_MODE": mode, "attempts": attempts,
        "frozen_registry_identity": base["reference"], "transport_manifest_identity": manifest,
        "engine_config_identity": construction["engine_config_identity"], "rootfs_diff_ids": construction["config_rootfs_diff_ids"],
        "named_context_binding": (base["reference"] if mode == "EXACT_REFERENCE_CONTEXT_OVERRIDE" else "errpilot_frozen_base") + "=" + source,
        "layout_inventory": layout_inventory, "tag": tag, "exit_code": result.returncode,
        "registry_resolution_requests_observed": int(registry)}
    if record["status"] == "PASS":
        row = strict_json(checked("first_output_inspect", ["docker", "image", "inspect", tag]))[0]
        require((row["Os"], row["Architecture"]) == ("linux", "amd64"), "output platform")
        require(row["RootFS"]["Layers"][:len(record["rootfs_diff_ids"])] == record["rootfs_diff_ids"], "output rootfs prefix")
        # Use precisely the pre-existing shared Engine observation/probe path.
        from evaluation.downstream_benchmark.screening import v6_preparation_runtime as r
        engine = r.shared_engine()
        probe = engine.probe_python(row["Id"])
        require(probe == base["python_probe"], "Python patch/executable/architecture identity")
        record.update(image_identity={k: row[k] for k in ["Id", "Os", "Architecture", "RootFS", "RepoTags"]},
                      python_probe=probe, python_identity="PASS", shared_identity_probe_mechanics="PASS")
    save("first_base_transport_result.json", record)
    print(json.dumps({k: record[k] for k in ["status", "FROM_TRANSPORT_MODE", "exit_code", "registry_resolution_requests_observed"]}), flush=True)


def persist_block_and_cleanup():
    first = load("first_base_transport_result.json")
    require(first["status"] == NAMED_BLOCK, "named-context hard stop required")
    require(len(first["attempts"]) == 2 and all(x["exit_code"] == 1 for x in first["attempts"]), "attempt evidence")
    observations = load("execution_corrections.json")
    observations["fallback_condition_classification_deviation"] = {
        "observed_error": "could not parse oci-layout reference <session-id>:@sha256:<digest>: invalid reference format",
        "failed_surface": "OCI_SOURCE_REFERENCE_PARSER",
        "FROM_context_name_failure_established": False,
        "alias_fallback_was_invoked": True, "classification_was_too_broad": True,
        "contract_compliance_exception": True,
        "consequence": "SECOND_SYNTHETIC_BUILD_REQUEST_BEFORE_RUN; NO_OUTPUT_NO_EGRESS_NO_ATTEMPT",
        "classifier_corrected_for_future_execution": True,
        "further_retries_or_source_syntax_variants_executed": False}
    durable(OUT / "execution_corrections.json", encoded(observations), update=True)
    construction = load("oci_layout_construction.json")
    bases = load("frozen_base_authorities.json")["bases"]
    rows, mapping = [], []
    for i, base in enumerate(bases):
        rows.append({"frozen_registry_identity": base["reference"], "expected_python_patch": base["python_version"],
            "archive_equivalence": "PASS" if i == 0 else "NOT_RUN_FIRST_BASE_HARD_GATE",
            "BuildKit_consumption": "FAIL_BEFORE_RUN" if i == 0 else "NOT_RUN_FIRST_BASE_HARD_GATE",
            "python_identity": "NOT_QUALIFIED"})
        mapping.append({"frozen_registry_digest": base["reference"].split("@", 1)[1],
            "scientific_base_reference": base["reference"], "engine_image_identity": base["image_identity"]["Id"],
            "engine_config_identity": construction["engine_config_identity"] if i == 0 else None,
            "rootfs_diff_ids": base["image_identity"]["RootFS"]["Layers"],
            "docker_archive_sha": construction["archive_sha256"] if i == 0 else None,
            "local_oci_manifest_sha": construction["transport_manifest_identity"] if i == 0 else None,
            "named_context_binding": first["named_context_binding"] if i == 0 else None,
            "qualification_result": NAMED_BLOCK if i == 0 else "NOT_RUN_FIRST_BASE_HARD_GATE",
            "production_transport_binding_accepted": False})
    save("all_base_transport_results.json", {"status": "NOT_RUN_FIRST_BASE_HARD_GATE", "required": 7,
        "exported": 1, "archive_equivalence_passed": 1, "BuildKit_consumption_passed": 0, "results": rows})
    save("seven_base_transport_map.json", {"status": "INCOMPLETE_UNQUALIFIED_NOT_PRODUCTION_RULE",
        "mapping": mapping, "production_transport_rule_constructed": False,
        "transport_identity_in_base_attempt_identity": False, "automatic_regeneration": False,
        "registry_fallback": False, "pull_fallback": False})
    save("output_parity_qualification.json", {"status": "NOT_RUN_FIRST_BASE_HARD_GATE", "output_parity": "NOT_QUALIFIED",
        "explicit_load_requested": True, "output_images_created": 0,
        "existing_identity_probe_executed_on_new_output": False})
    save("downstream_egress_resume.json", {"status": "NOT_RUN_FIRST_BASE_HARD_GATE", "proxy_implementation_created": False,
        "internal_plus_external_proxy_topology_created": False, "positive_origins_attempted": 0,
        "negative_connect_direct_egress_and_network_none_proofs": "NOT_RUN", "benchmark_dependency_installs": 0})
    save("network_enforcement_identity.json", {"status": "ABSENT", "semantic_enforcement_identity": None,
        "qualification_observation_identity": None, "restricted_egress_qualified": False})
    save("runtime_integration_diff.json", {"status": "NOT_RUN_FIRST_BASE_HARD_GATE", "files_changed": [],
        "production_runtime_delta": "NONE", "runtime_candidate_installed": False})
    copied = {}
    for p in sorted(OUT.iterdir()):
        if p.is_file():
            durable(Q / p.name, p.read_bytes())
            copied[p.name] = {"sha256": sha(p.read_bytes()), "bytes": p.stat().st_size}
    durable(Q / "precleanup_evidence_manifest.json", encoded({"repository_copies": copied,
        "qualification_files": prior.inventory(Q), "persisted_before_cleanup": True,
        "status": NAMED_BLOCK, "benchmark_attempt_id": None}))
    save("precleanup_evidence_receipt.json", {"root": str(Q), "durable": True,
        "manifest_sha256": file_sha(Q / "precleanup_evidence_manifest.json"),
        "first_base_status": NAMED_BLOCK, "no_dependent_qualification_executed": True})
    # Reuse the exact prior owned-object cleanup mechanics with this run's
    # outcome filename and label; no prior evidence file is edited.
    prior.BLOCK = NAMED_BLOCK
    prior.OWNER = load("builder_configuration.json")["ownership_label"]
    def alias_load(name):
        return load("first_base_transport_result.json" if name == "first_base_transport_qualification.json" else name)
    prior.load = alias_load
    prior.cleanup()


def finish():
    require(load("cleanup_verification.json")["status"] == "PASS", "cleanup gate")
    entry = load("entry_verification.json")
    require(all(sha((ROOT / rel).read_bytes()) == digest for rel, digest in entry["prior_file_hashes"].items()),
            "prior repository file changed")
    require(prior.inventory(EXTERNAL, exclude=Q) == load("prior_external_inventory.json"), "prior external delta")
    require(prior.attempt_state() == entry["attempt_state"], "attempt state changed")
    g = prior.git_state("final")
    require(g["index_sha256"] == entry["index_sha256"], "index changed")
    from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a
    from evaluation.downstream_benchmark.screening import v6_preparation_runtime as r
    _, manifest = a.load_inputs()
    validate_qualification_firewall((ROOT / a.CURRENT).read_bytes(), r.population(), prior.attempt_state()["real_ledger_claims"])
    require(a.derive_population(manifest) == r.population(), "population changed")
    own = str(OUT.relative_to(ROOT)) + "/"
    untracked = checked("final_untracked", ["git", "ls-files", "--others", "--exclude-standard"]).decode().splitlines()
    require({x for x in untracked if not x.startswith(own)} == set(entry["prior_file_hashes"]), "unrelated dirty delta")
    save("final_verification.json", {"status": "PASS", **g, "prior_162_repository_files_exact": True,
        "prior_external_inventory_exact": True, "attempt_state": prior.attempt_state(),
        "total": 641, "restricted": 583, "network_none": 58,
        "population_semantic_sha256": r.POPULATION_SHA, "blockers_non_dispatchable": ["matplotlib::1", "matplotlib::8"],
        "all_recipe_revision_plan_case_attempt_identities_preserved": True,
        "transport_identity_in_attempt_identity": False})
    save("firewall.json", {"REAL_BENCHMARK_ATTEMPTS": 0, "REAL_BENCHMARK_CLAIMS": 0,
        "REAL_BENCHMARK_BUILDS": 0, "BENCHMARK_DEPENDENCIES_INSTALLED": 0,
        "REAL_BENCHMARK_SOURCE_EXPORTS": 0, "REGISTRY_PULLS": 0,
        "REGISTRY_BASE_RESOLUTION_REQUESTS_DURING_LOCAL_OCI_BUILDS": 0,
        "SOURCE_ACQUISITION_EXECUTED": "NO", "ORACLE_EXECUTED": "NO", "EVENT_3_CREATED": "NO",
        "CANONICAL_CURRENT_STATE_MODIFIED": "NO", "GIT_STAGE": "NO", "GIT_COMMIT": "NO", "GIT_PUSH": "NO",
        "fixture_only_build_requests": 2, "fixture_RUNs_executed": 0, "fixture_output_images_created": 0,
        "network_basis": "internal-only builder, no default route, loopback upstream DNS, parser failure before source consumption/RUN; captured logs contain no registry endpoint request",
        "packet_capture": "NOT_PERFORMED", "scientific_validation": False})
    print("FINAL PRESERVATION PASS: 162 prior files, canonical/index, external history and 641/583/58 exact", flush=True)


if __name__ == "__main__":
    {"entry": entry, "export-first": export_first,
     "recover-first-encoding-check": recover_first_encoding_check,
     "create-builder": create_builder, "observe-builder": observe_builder,
     "first-consume": first_consume, "persist-block-and-cleanup": persist_block_and_cleanup,
     "finish": finish}[sys.argv[1]]()

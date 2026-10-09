"""Construct the non-effective image observation correction, exclusively in this package."""
from __future__ import annotations

import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parent / "v6_preparation_execution_production_runtime_installation_resume_v1" / "production_provider_candidate.py"
ORIGINAL_SHA = "d466c9310d22754c0c3c9744764bcc402aef988195da7f7aea45b9700eb1de0a"

HELPERS = '''
def image_identity_pins(config, role):
    """Only the accepted configuration/map supply image pins; no source fallback."""
    a.require(role in {"daemon", "proxy"}, "unknown image identity role")
    if role == "daemon":
        rt = config["runtime_image"]
        return {"engine": rt["engine_store_id"], "manifest": rt["platform_manifest_id"],
                "config": rt["verified_config_digest"], "reference": rt["immutable_reference"],
                "platform": rt["platform"], "diff_ids": rt["RootFS"]["Layers"], "indexed": True}
    row = a.loads(a.read_exact(NATIVE + "seven_base_transport_map.json",
        "e1decc99328c414a136456d74cc70f410219aa8c0ad4c17e96397676240a25db"))["mapping"][0]
    return {"engine": row["engine_image_identity"], "manifest": row["frozen_registry_digest"],
            "config": row["engine_config_identity"], "reference": row["scientific_base_authority"],
            "platform": "linux/amd64", "diff_ids": row["ordered_rootfs_diff_ids"], "indexed": False}


def verify_image_identity(container, store, selected, index_raw, manifest_raw, config_raw, pins):
    """Pure content-chain verification; returns observations, never production authority."""
    a.require(isinstance(container, dict) and isinstance(store, dict) and isinstance(selected, dict),
              "malformed image identity observation")
    a.require(container.get("Image") == store.get("Id") == pins["engine"]
              and container.get("Config", {}).get("Image") == pins["reference"],
              "Engine image ID/reference mismatch")
    a.require(all(isinstance(raw, bytes) for raw in (index_raw, manifest_raw, config_raw)),
              "missing identity content bytes")
    a.require(bool(manifest_raw) and bool(config_raw), "missing manifest/config identity bytes")
    a.require((selected.get("Os"), selected.get("Architecture")) == tuple(pins["platform"].split("/")),
              "wrong selected image platform")
    manifest = a.loads(manifest_raw)
    oci_config = a.loads(config_raw)
    a.require(isinstance(manifest, dict) and isinstance(oci_config, dict), "malformed OCI identity")
    a.require("sha256:" + a.sha(manifest_raw) == pins["manifest"]
              and selected.get("Id") == pins["manifest"]
              and selected.get("Descriptor", {}).get("digest") == pins["manifest"]
              and selected["Descriptor"].get("size") == len(manifest_raw),
              "wrong platform manifest provenance")
    a.require(manifest.get("schemaVersion") == 2
              and manifest.get("mediaType") == selected["Descriptor"].get("mediaType"),
              "wrong manifest representation")
    descriptor = manifest.get("config", {})
    running = container.get("ImageManifestDescriptor", {})
    a.require(isinstance(running, dict) and running.get("digest") == pins["manifest"]
              and running.get("size") == len(manifest_raw)
              and running.get("mediaType") == manifest.get("mediaType")
              and running.get("platform") == {"os": "linux", "architecture": "amd64"}
              and container.get("Platform") == "linux", "wrong running container platform/manifest")
    a.require("sha256:" + a.sha(config_raw) == descriptor.get("digest") == pins["config"]
              and descriptor.get("size") == len(config_raw), "wrong OCI config provenance")
    a.require((oci_config.get("os"), oci_config.get("architecture")) == tuple(pins["platform"].split("/")),
              "wrong OCI config platform")
    if pins["indexed"]:
        a.require("sha256:" + a.sha(index_raw) == pins["engine"]
                  and store.get("Descriptor", {}).get("digest") == pins["engine"]
                  and store["Descriptor"].get("size") == len(index_raw), "wrong OCI index provenance")
        index = a.loads(index_raw)
        a.require(index.get("schemaVersion") == 2
                  and index.get("mediaType") == store["Descriptor"].get("mediaType"),
                  "wrong index representation")
        matches = [x for x in index.get("manifests", [])
                   if x.get("platform") == {"os": "linux", "architecture": "amd64"}]
        a.require(len(matches) == 1 and matches[0]["digest"] == pins["manifest"]
                  and matches[0]["size"] == len(manifest_raw)
                  and matches[0]["mediaType"] == manifest["mediaType"],
                  "ambiguous/wrong index platform lineage")
    else:
        a.require(index_raw == b"" and store.get("Descriptor") == selected.get("Descriptor"),
                  "unexpected proxy index/manifest lineage")
    rootfs, fields = oci_config.get("rootfs", {}), oci_config.get("config", {})
    a.require(rootfs.get("type") == "layers" and rootfs.get("diff_ids") == pins["diff_ids"]
              and selected.get("RootFS") == {"Type": "layers", "Layers": pins["diff_ids"]},
              "wrong image RootFS content lineage")
    a.require(isinstance(fields, dict) and isinstance(selected.get("Config"), dict)
              and bool(selected["Config"])
              and all(k in fields and fields[k] == v for k, v in selected["Config"].items()),
              "wrong live Engine config fields")
    omitted = {k: v for k, v in fields.items() if k not in selected["Config"]}
    a.require(not omitted if pins["indexed"] else
              all(v in [None, False, "", {}, []] or k == "Image" for k, v in omitted.items()),
              "unreported non-default Engine config fields")
    return {"ENGINE_IMAGE_ID": store["Id"], "OCI_INDEX_OR_MANIFEST_DIGEST": pins["manifest"],
            "OCI_CONFIG_DIGEST": "sha256:" + a.sha(config_raw), "PLATFORM_IDENTITY": pins["platform"]}


def retained_image_content(config, role):
    """Read the exact retained content sources, without acquisition or alternate paths."""
    pins = image_identity_pins(config, role)
    if role == "daemon":
        root = a.OUTPUT_ROOT / "qualification/local_buildkit_runtime_provisioning_v1"
        paths = [root / name for name in
                 ("registry_index.raw.json", "registry_amd64_manifest.raw.json", "registry_config.raw.json")]
        for path in paths:
            ledger.safe_path(path)
        return tuple(path.read_bytes() for path in paths)
    row = a.loads(a.read_exact(NATIVE + "seven_base_transport_map.json",
        "e1decc99328c414a136456d74cc70f410219aa8c0ad4c17e96397676240a25db"))["mapping"][0]
    archive = Path(row["layout_path"]).parent / "engine-save.tar"
    ledger.safe_path(archive)
    with tarfile.open(archive, "r") as source:
        result = []
        for digest in (pins["manifest"], pins["config"]):
            name = "blobs/sha256/" + digest.split(":")[1]
            matches = [m for m in source.getmembers() if m.name == name]
            a.require(len(matches) == 1 and matches[0].isfile(), "ambiguous/missing retained identity member")
            with source.extractfile(matches[0]) as member:
                result.append(member.read())
    return b"", result[0], result[1]


def observe_image_config(container, config, role, read_only_run):
    """Image observation seam only; no receipt, ledger, dispatch or authority construction."""
    pins = image_identity_pins(config, role)
    store = a.loads(read_only_run(["docker", "image", "inspect", container["Image"]]))[0]
    selected = a.loads(read_only_run(["docker", "image", "inspect", "--platform", pins["platform"],
                                    container["Image"]]))[0]
    identity = verify_image_identity(container, store, selected, *retained_image_content(config, role), pins)
    return identity["OCI_CONFIG_DIGEST"]


'''


def main():
    raw = ORIGINAL.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == ORIGINAL_SHA
    source = raw.decode("utf-8")
    corrected = source.replace("import subprocess\n", "import subprocess\nimport tarfile\n", 1)
    old = '''            daemon["image_config_digest"] = a.loads(run(["docker", "image", "inspect", daemon["Image"]]))[0]["Id"]
            proxy["image_config_digest"] = a.loads(run(["docker", "image", "inspect", proxy["Image"]]))[0]["Id"]'''
    new = '''            daemon["image_config_digest"] = observe_image_config(daemon, self.config, "daemon", run)
            proxy["image_config_digest"] = observe_image_config(proxy, self.config, "proxy", run)'''
    assert corrected.count(old) == 1
    corrected = corrected.replace(old, new, 1)
    marker = "def normalize_topology(objects, proxy_code, policy_raw, config):\n"
    assert corrected.count(marker) == 1
    corrected = corrected.replace(marker, HELPERS + marker, 1)
    marker = '''    a.require(d["State"]["Running"] is True and p["State"]["Running"] is True, "daemon/proxy stopped")'''
    corrected = corrected.replace(marker, marker + '''
    a.require(d["Image"] == image_identity_pins(config, "daemon")["engine"], "wrong BuildKit Engine image ID")
    a.require(p["Image"] == image_identity_pins(config, "proxy")["engine"], "wrong proxy Engine image ID")''', 1)
    ast.parse(corrected)
    candidate = HERE / "corrected_production_provider_candidate.py"
    with candidate.open("xb") as stream:
        stream.write(corrected.encode())
    diff = "".join(difflib.unified_diff(source.splitlines(True), corrected.splitlines(True),
                                    fromfile=str(ORIGINAL), tofile=str(candidate)))
    with (HERE / "provider_identity_correction.patch").open("xb") as stream:
        stream.write(diff.encode())
    print(json.dumps({"provider_sha256": hashlib.sha256(corrected.encode()).hexdigest(),
                      "patch_sha256": hashlib.sha256(diff.encode()).hexdigest()}))


if __name__ == "__main__":
    main()

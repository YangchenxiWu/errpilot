"""Separate production provider candidate. No installed authority exists here.

Receipt, topology and versioned claim binding are shared with the controller.
The frozen qualification dispatcher/transport/materializer wrapper are never used.
"""
from __future__ import annotations

import copy
import importlib
import ipaddress
import json
import re
import shutil
import subprocess
import tarfile
import types
import uuid
from pathlib import Path

from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a
from evaluation.downstream_benchmark.screening import v6_preparation_ledger as ledger
from evaluation.downstream_benchmark.screening import v6_preparation_runtime as legacy

NATIVE_PACKAGE = "evaluation.downstream_benchmark.evidence.v6_native_buildkit_client_compatibility_bridge_v1"
native = importlib.import_module(NATIVE_PACKAGE + ".successor_runtime")
guards = importlib.import_module(NATIVE_PACKAGE + ".guards")
NATIVE = "evaluation/downstream_benchmark/evidence/v6_native_buildkit_client_compatibility_bridge_v1/"
RESUME = "evaluation/downstream_benchmark/evidence/v6_production_runtime_topology_stability_successor_resume_v1/"
SCREENING = "evaluation/downstream_benchmark/screening/"
CONTROLLER_TARGET = SCREENING + "v6_preparation_production_controller_v2.py"
PROVIDER_TARGET = SCREENING + "v6_preparation_production_provider_v2.py"
EFFECTIVITY = "evaluation/downstream_benchmark/V6_PREPARATION_PRODUCTION_RUNTIME_EFFECTIVITY_V2.json"
ACCEPTANCE_PIN = "evaluation/downstream_benchmark/V6_PREPARATION_PRODUCTION_RUNTIME_EFFECTIVITY_ACCEPTANCE_PIN_V2.json"
INSTALLATION_AUTHORITY = "evaluation/downstream_benchmark/V6_PREPARATION_PRODUCTION_RUNTIME_INSTALLATION_AUTHORITY_V2.json"
CONTRACT_TARGET = "evaluation/downstream_benchmark/V6_PREPARATION_PRODUCTION_RECEIPT_AUTHORITY_CONTRACT_V2.json"
QUALIFICATION_ROOT = a.OUTPUT_ROOT / "qualification/production_runtime_topology_stability_successor_resume_v1"
SYNTHETIC = "SYNTHETIC_TOPOLOGY_STABILITY_SUCCESSOR_V2_QUALIFICATION"
REAL = ledger.REAL
RECEIPT_SCHEMA = "V6_RESTRICTED_BUILD_EGRESS_ENFORCEMENT_RECEIPT_V2_CANDIDATE"
OBSERVATION_SCHEMA = "V6_LIVE_DAEMON_TOPOLOGY_OBSERVATION_V1"
CANONICAL_SHA = "e48580c1f9769d1b93ab995e6dcef3689c6920a9ce7b83f728526e9694dc68fd"
EVENT_3 = "237d8020668f338c04065beb8557d8f25263fbfc0282003dcc5b2af67a20a50d"
ENFORCEMENT = "8801637324b2fa32124df8444e88f193a5be3f9c847904f2eebfb92197bc5c10"
FROZEN_SOURCE_SHA = "c83da6f5eb355702f994c28efc6b14bc36988a9cc405ff05a689a9f97128f4b6"
FROZEN_CONFIG_SHA = "654299e49b0fc8833f093ecc887b4578970895ce28aa5359b4b37246f7b6190e"
LEDGER_SHA = "d64dc5c742d7857e4dcf4f350bc3db4571d679ea9a74a3c4303085ad10bd0dd7"
ORDER_SHA = "7a329a4c301e5ddd6bae1047f6bce77430aca5a21d71a7a749dfb3899e4c7a5c"
CLOSURE = "evaluation/downstream_benchmark/V6_PREPARATION_EXECUTION_RUNTIME_AND_EGRESS_QUALIFIED_BASELINE_LIFECYCLE_CLOSURE_V1.md"
CLOSURE_SHA = "a2a2d8f5fef0357fdad7960f45fad8aa74fdc8bf8728472162c1051a96a10949"
ORIGINS = ["files.pythonhosted.org:443", "pypi.org:443"]
RECEIPT_FIELDS = {"schema", "runtime_authority", "canonical_state_sha256", "event_3_id",
    "production_runtime_effectivity_pin_sha256", "controller_source_sha256",
    "provider_source_sha256", "receipt_contract_sha256", "enforcement_identity",
    "base_attempt_id", "work_item_identity", "network_mode", "allowed_origins",
    "security_projection_sha256", "candidate_only", "provider_independent_freshness_required",
    "client_authorization_verdict", "client_authorization_evidence_sha256", "client_authorization_policy_sha256"}


def exact_json(path):
    ledger.safe_path(path)
    return a.loads(path.read_bytes())


def pretty(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def frozen_inputs():
    a.read_exact(NATIVE + "successor_runtime.py", FROZEN_SOURCE_SHA)
    config = a.loads(a.read_exact(NATIVE + "successor_runtime_integration_candidate.json", FROZEN_CONFIG_SHA))
    a.read_exact(SCREENING + "v6_preparation_ledger.py", LEDGER_SHA)
    a.read_exact(CLOSURE, CLOSURE_SHA)
    for name, digest in config["successor_source"].items():
        a.read_exact(NATIVE + name, digest)
    enforcement = exact_json(a.ROOT / NATIVE / "network_enforcement_identity.json")
    a.require(a.sha(pretty(enforcement["SEMANTIC_ENFORCEMENT_IDENTITY"])) == ENFORCEMENT,
              "frozen semantic enforcement identity drift")
    mapping = a.loads(a.read_exact(NATIVE + "seven_base_transport_map.json",
        "e1decc99328c414a136456d74cc70f410219aa8c0ad4c17e96397676240a25db"))
    semantic_map = enforcement["SEMANTIC_ENFORCEMENT_IDENTITY"]["seven_base_transport_map"]
    a.require(len(mapping["mapping"]) == len(semantic_map) == 7
              and [{k: row[k] for k in semantic_map[i]} for i, row in enumerate(mapping["mapping"])] == semantic_map,
              "frozen seven-base transport map drift")
    return config


def population_identity(population, raw):
    ids = [x["base_attempt_id"] for x in population["items"]]
    return {"file_sha256": a.sha(raw), "semantic_sha256": a.identity(population),
            "ordered_attempt_ids_sha256": a.identity(ids), "total": len(ids),
            "restricted": sum(x["build_network_required"] for x in population["items"]),
            "none": sum(not x["build_network_required"] for x in population["items"])}


def expected_population_identity():
    return {"file_sha256": legacy.WORK_SHA, "semantic_sha256": legacy.POPULATION_SHA,
            "ordered_attempt_ids_sha256": ORDER_SHA, "total": 641, "restricted": 583, "none": 58}


def ledger_identity():
    return {"implementation_path": SCREENING + "v6_preparation_ledger.py",
            "implementation_sha256": LEDGER_SHA, "claim_binding_schema": "V6_RECEIPT_BOUND_CLAIM_ADAPTER_V2",
            "root": str(a.OUTPUT_ROOT / "ledger"), "record_extension": ["receipt_sha256", "input_runtime_binding.raw_evidence_association_sha256"],
            "existing_namespace_sha256": "7570569f68a9babf36d408f8c59cc17879c0ef23262d6178ffc9d50bbc06c67e"}


def validate_effectivity_status(p):
    a.require(p["schema"] == "V6_PREPARATION_PRODUCTION_RUNTIME_EFFECTIVITY_V2"
              and p["candidate_only"] is False and p["HUMAN_PI_ACCEPTED"] == "YES"
              and p["runtime_effective"] == "YES", "non-effective/candidate installation")
    a.require(p["canonical"] == {"path": a.CURRENT, "sha256": CANONICAL_SHA}
              and p["event_3_id"] == EVENT_3, "wrong canonical/event #3 pin")


def validate_real_population(p):
    a.require(p == expected_population_identity(), "wrong exact 641/583/58 population")


class Authority:
    """Real entry has no injectable pin, observer, root, or runner argument."""
    def __init__(self, *, _qualification_fixture=None):
        a.require(type(self) is Authority, "authority subtype forbidden")
        if _qualification_fixture is None:
            a.require(Path(__file__).resolve() == a.ROOT / PROVIDER_TARGET,
                      "candidate source is not installed production provider")
            self.mode, self.root = REAL, a.OUTPUT_ROOT
        else:
            a.require(Path(__file__).resolve() == a.ROOT / RESUME / "production_provider_successor_candidate.py",
                      "synthetic interface unavailable from installed/copied production source")
            ledger.safe_path(_qualification_fixture)
            a.require(_qualification_fixture.is_relative_to(QUALIFICATION_ROOT), "synthetic authority outside qualification")
            self.mode, self.fixture_path = SYNTHETIC, _qualification_fixture
        self.refresh()

    @classmethod
    def synthetic(cls, fixture_path):
        a.require(cls is Authority, "synthetic authority subtype forbidden")
        return cls(_qualification_fixture=fixture_path)

    def refresh(self):
        if self.mode == REAL:
            # Verify canonical authority first; loading a later pin cannot replace it.
            canonical_raw = a.read_exact(a.CURRENT, CANONICAL_SHA)
            current = a.loads(canonical_raw)
            canonical_pin = legacy.read_installed(legacy.EXECUTION_PIN)
            a.require(canonical_pin == {"path": a.CURRENT, "sha256": CANONICAL_SHA, "HUMAN_PI_ACCEPTED": "YES"},
                      "canonical descriptor independent acceptance pin")
            event = a.loads(a.read_exact(current["event_chain"][2]["path"], current["event_chain"][2]["sha256"]))
            legacy.validate_execution_descriptor(canonical_raw, canonical_pin,
                {"execution_descriptor": canonical_pin, "event_3_authority": event["authority_reference"],
                 "effective_descriptor_identity": current["effective_current_descriptor_identity"]})
            pin = exact_json(a.ROOT / ACCEPTANCE_PIN)
            a.require(set(pin) == {"path", "sha256", "HUMAN_PI_ACCEPTED"}
                      and pin["path"] == EFFECTIVITY and pin["HUMAN_PI_ACCEPTED"] == "YES",
                      "missing exact Human-PI accepted effectivity pin")
            raw = a.read_exact(EFFECTIVITY, pin["sha256"])
            p = a.loads(raw)
            validate_effectivity_status(p)
            a.require(p["controller"]["path"] == CONTROLLER_TARGET
                      and p["provider"]["path"] == PROVIDER_TARGET
                      and p["receipt_contract"]["path"] == CONTRACT_TARGET,
                      "wrong installed source/contract path")
            authority_ref = p["installation_authority"]
            a.require(authority_ref["path"] == INSTALLATION_AUTHORITY, "installation authority path")
            installed = a.loads(a.read_exact(authority_ref["path"], authority_ref["sha256"]))
            a.require(installed["schema"] == "V6_PREPARATION_PRODUCTION_RUNTIME_INSTALLATION_AUTHORITY_V2"
                      and installed["owner"] == "HUMAN_PI" and installed["HUMAN_PI_ACCEPTED"] == "YES"
                      and installed["gate"] == "HUMAN_PI_INSTALL_V6_PREPARATION_PRODUCTION_RUNTIME_V2",
                      "unaccepted installation authority")
            a.require(installed["accepted_installation_payload"] == {k: p[k] for k in
                      ("canonical", "event_3_id", "controller", "provider", "receipt_contract",
                       "receipt_schema", "enforcement_identity", "population_identity", "ledger_binding_identity",
                       "frozen_sources", "live_topology", "base_layouts", "security_contracts", "live_evidence_observer", "accepted_client_principals")}, "installation authority/pin disagreement")
            for ref in (p["controller"], p["provider"], p["receipt_contract"]):
                a.read_exact(ref["path"], ref["sha256"])
            self.config = frozen_inputs()
            a.require(p["frozen_sources"] == installed["accepted_installation_payload"]["frozen_sources"],
                      "frozen helper binding")
            for path, digest in p["frozen_sources"].items():
                a.read_exact(path, digest)
            required_sources = {SCREENING + name for name in (
                "v6_preparation_adapter.py", "v6_preparation_runtime.py", "v6_preparation_ledger.py",
                "materializer.py", "materialize_expansion_block_02_batch.py")}
            a.require(required_sources <= set(p["frozen_sources"]), "shared implementation pins missing")
            head = legacy._git("rev-parse", "HEAD").decode().strip()
            a.require(legacy._git("status", "--porcelain=v1", "--untracked-files=all") == b"",
                      "production requires clean committed sources")
            a.require(legacy._git("ls-remote", "origin", "refs/heads/main").decode().split()
                      == [head, "refs/heads/main"], "production exact live publication")
            for ref in (p["controller"], p["provider"]):
                a.require(a.sha(legacy._git("cat-file", "blob", head + ":" + ref["path"])) == ref["sha256"],
                          "source not exact committed installation")
            self.root, self.pin_sha = a.OUTPUT_ROOT, a.sha(raw)
            self.population = legacy.population()
            validate_real_population(p["population_identity"])
            a.require(population_identity(self.population, a.read_exact(legacy.PACKAGE + "work_items_candidate.json", legacy.WORK_SHA))
                      == p["population_identity"] == expected_population_identity(), "wrong exact 641/583/58 population")
            legacy.validate_acceptance(a.loads(a.read_exact(legacy.AUTHORITY, legacy.AUTHORITY_SHA)), network_required=True)
            _, self.manifest = a.load_inputs()
            a.validate_population(self.manifest, self.population)
            namespace = exact_json(self.root / "namespace.json")
            a.require(namespace["namespace"] == "IMPLEMENTATION_AND_SYNTHETIC_QUALIFICATION_ONLY"
                      and namespace["runtime_acceptance_sha256"] == legacy.AUTHORITY_SHA,
                      "existing ledger root identity changed")
            a.require(a.sha((self.root / "namespace.json").read_bytes()) == ledger_identity()["existing_namespace_sha256"],
                      "exact existing namespace identity changed")
            a.require(p["ledger_binding_identity"] == ledger_identity(), "ledger binding identity")
        else:
            self.config = frozen_inputs()
            a.require(self.mode == SYNTHETIC, "fake qualification namespace")
            raw = self.fixture_path.read_bytes()
            p = a.loads(raw)
            a.require(p["schema"] == "V6_SYNTHETIC_SUCCESSOR_EFFECTIVITY_FIXTURE_V2"
                      and p["namespace"] == SYNTHETIC and p["HUMAN_PI_ACCEPTED"] == "NO"
                      and p["runtime_effective"] == "NO" and p["synthetic_only"] is True,
                      "synthetic fixture cannot assert Human-PI production effectivity")
            self.root = Path(p["qualification_root"])
            ledger.safe_path(self.root)
            a.require(self.root.is_relative_to(QUALIFICATION_ROOT), "real ledger root forbidden in synthetic mode")
            self.pin_sha = a.sha(raw)
            self.population = exact_json(self.root / "population.json")
            raw_population = (self.root / "population.json").read_bytes()
            a.require(p["population_identity"] == population_identity(self.population, raw_population), "synthetic population identity")
            a.require(all(x["base_attempt_id"].startswith("SYNTHETIC_QUALIFICATION_")
                          and x["case_id"].startswith("SYNTHETIC_") for x in self.population["items"]),
                      "real attempt identity in synthetic fixture")
            a.require(p["canonical"] == {"path": str(self.root / "canonical.json"),
                                        "sha256": a.sha((self.root / "canonical.json").read_bytes())}, "synthetic canonical pin")
            current = exact_json(self.root / "canonical.json")
            a.require(current == {"namespace": SYNTHETIC, "state": "PREPARATION_EXECUTION_AUTHORIZED",
                                  "event_3_id": p["event_3_id"]}, "wrong synthetic canonical state")
            a.require(p["event_3_id"] == a.sha(b"SYNTHETIC_EVENT_3\n"), "wrong synthetic event #3")
            for ref, name in ((p["controller"], "production_controller_successor_candidate.py"),
                              (p["provider"], "production_provider_successor_candidate.py"),
                              (p["receipt_contract"], "receipt_authority_contract_v2_candidate.json")):
                a.require(ref["path"] == RESUME + name, "wrong synthetic source path")
                a.read_exact(ref["path"], ref["sha256"])
            a.require(p["ledger_binding_identity"] == {**ledger_identity(), "root": str(self.root / "ledger")},
                      "synthetic ledger binding")
            self.manifest = exact_json(self.root / "scientific_manifest.json")
        self.payload = p
        a.require(p["receipt_schema"] == (REAL_RECEIPT_SCHEMA if self.mode == REAL else RECEIPT_SCHEMA) and p["enforcement_identity"] == ENFORCEMENT,
                  "wrong receipt schema/enforcement identity")
        contract = a.loads(a.read_exact(p["receipt_contract"]["path"], p["receipt_contract"]["sha256"]))
        a.require(contract["receipt_schema"] == RECEIPT_SCHEMA and contract["future_production_schema"] == REAL_RECEIPT_SCHEMA and contract["allowed_origins"] == ORIGINS,
                  "wrong receipt contract/allowlist")
        for n in ("claims", "terminals", "locks"):
            ledger.safe_path(self.root / "ledger" / n)
            a.require((self.root / "ledger" / n).is_dir(), "existing ledger required before admission")
        verify_security_contracts(self)
        return self

    def journal(self):
        return ReceiptBoundLedger(self)

    def select(self, item):
        a.require(item["case_id"] not in {"matplotlib::1", "matplotlib::8"}, "blocker dispatch")
        matches = [x for x in self.population["items"] if x["base_attempt_id"] == item["base_attempt_id"]]
        a.require(len(matches) == 1 and a.canonical(matches[0]) == a.canonical(item), "unknown/stale/mutated work binding")
        if self.mode == REAL:
            plan = a.select(self.manifest, ordinal=item["census_order"], case_id=item["case_id"], plan_sha=item["plan_sha256"])
            a.require(item == a.work_item(plan, item["variant"]), "regenerated work identity")
            return plan
        return synthetic_plan(self, item)

    def observe(self, stage="ISSUANCE"):
        if self.mode == SYNTHETIC:
            a.require(Path(__file__).resolve() == a.ROOT / RESUME / "production_provider_successor_candidate.py",
                      "synthetic observation forbidden outside exact candidate source")
            bundle = exact_json(self.root / "raw_fixture.json")
            a.require(bundle["namespace"] == SYNTHETIC and bundle["synthetic_only"] is True,
                      "synthetic raw cannot assert live evidence")
        else:
            bundle = collect_live_raw(self, stage)
        result = verify_raw_security(bundle, self.config, stage=stage, synthetic=self.mode == SYNTHETIC,
                                     accepted_principals=self.payload["accepted_client_principals"])
        a.require(a.canonical(result["security_projection"]) == a.canonical(self.payload["live_topology"]),
                  "stale or mismatched live topology/security projection")
        return result



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


def normalize_topology(objects, proxy_code, policy_raw, config):
    d, p, n, worker = (objects[k] for k in ("daemon", "proxy", "network", "worker"))
    a.require(d["State"]["Running"] is True and p["State"]["Running"] is True, "daemon/proxy stopped")
    a.require(d["Image"] == image_identity_pins(config, "daemon")["engine"], "wrong BuildKit Engine image ID")
    a.require(p["Image"] == image_identity_pins(config, "proxy")["engine"], "wrong proxy Engine image ID")
    a.require(d["Config"]["Image"] == config["runtime_image"]["immutable_reference"]
              and d["image_config_digest"] == config["runtime_image"]["verified_config_digest"], "wrong BuildKit runtime digest")
    a.require(n["Internal"] is True and n["Name"] == config["internal_network"], "builder network not exact internal-only")
    dn, pn = d["NetworkSettings"]["Networks"], p["NetworkSettings"]["Networks"]
    a.require(set(dn) == {n["Name"]} and dn[n["Name"]]["NetworkID"] == n["Id"], "daemon has external network")
    a.require(n["Name"] in pn and pn[n["Name"]]["NetworkID"] == n["Id"]
              and len(pn) == 2 and dn[n["Name"]].get("Gateway", "") == "", "proxy topology binding")
    a.require(d["HostConfig"]["Dns"] == ["127.0.0.1"] and not d["HostConfig"]["PortBindings"], "daemon DNS/port exposure")
    a.require(d["native_binary_sha256"] == config["client_binary_sha256"]
              and d["daemon_binary_sha256"] == config["daemon_binary_sha256"], "wrong native/daemon binaries")
    a.require(d["Path"] == "/usr/bin/buildkitd" and d["Args"] == ["--debug"], "daemon argv/entitlement drift")
    a.require(p["Path"] == "python" and p["Args"] == ["-u", "/qualification_proxy.py"]
              and not p["HostConfig"]["PortBindings"], "proxy process/port drift")
    proxy_base = exact_json(a.ROOT / NATIVE / "seven_base_transport_map.json")["mapping"][0]
    a.require(p["image_config_digest"] == proxy_base["engine_config_identity"]
              and p["Config"]["Image"] == proxy_base["scientific_base_authority"], "accepted proxy runtime digest drift")
    a.require(set(n["Containers"]) == {d["Id"], p["Id"]}, "unexpected internal network participant")
    a.require(a.sha(proxy_code) == config["proxy"]["implementation_sha256"], "wrong proxy source")
    policy = a.loads(policy_raw)
    a.require(policy == config["proxy"]["policy"] and a.sha(pretty(policy)) == config["proxy"]["policy_sha256"],
              "wrong proxy policy/broader allowlist")
    a.require(isinstance(worker, list) and len(worker) == 1 and isinstance(worker[0], dict)
              and "linux/amd64" in worker[0]["PLATFORMS"], "exact one amd64-capable worker required")
    return {"schema": OBSERVATION_SCHEMA, "BuildKit_runtime_reference": d["Config"]["Image"],
        "daemon_endpoint": config["endpoint"],
        "daemon_instance_identity": {"container_id": d["Id"], "StartedAt": d["State"]["StartedAt"], "Pid": d["State"]["Pid"]},
        "worker_identity": worker[0], "internal_builder_network": {k: n[k] for k in ("Id", "Name", "Internal", "Driver", "IPAM", "Options", "Containers")},
        "proxy_instance_identity": {"container_id": p["Id"], "StartedAt": p["State"]["StartedAt"], "Pid": p["State"]["Pid"]},
        "proxy_network_binding": pn, "proxy_policy_sha256": a.sha(pretty(policy)), "enforcement_identity": ENFORCEMENT,
        "native_binary_sha256": d["native_binary_sha256"], "daemon_binary_sha256": d["daemon_binary_sha256"],
        "daemon_image_config_digest": d["image_config_digest"], "daemon_network_attachments": dn,
        "daemon_argv": {"Path": d["Path"], "Args": d["Args"]}, "daemon_dns": d["HostConfig"]["Dns"],
        "daemon_port_bindings": d["HostConfig"]["PortBindings"], "daemon_routes": d["routes"],
        "daemon_socket_observation": d["sockets"], "proxy_image_config_digest": p["image_config_digest"],
        "proxy_argv": {"Path": p["Path"], "Args": p["Args"]}, "proxy_source_sha256": a.sha(proxy_code),
        "proxy_policy_bytes_sha256": a.sha(policy_raw)}


def parse_workers(raw):
    rows = raw.decode("utf-8").strip().splitlines()
    a.require(len(rows) == 2 and rows[0].split() == ["ID", "PLATFORMS"], "ambiguous native worker observation")
    parts = rows[1].split()
    a.require(len(parts) == 2, "native worker identity row")
    return [{"ID": parts[0], "PLATFORMS": parts[1].split(",")}]


def receipt_value(authority, item, observation):
    a.require(item["build_network_required"] is True, "receipt prohibited for NONE")
    p = authority.payload
    synthetic = authority.mode == SYNTHETIC
    return {"schema": RECEIPT_SCHEMA if synthetic else REAL_RECEIPT_SCHEMA, "runtime_authority": not synthetic,
        "candidate_only": synthetic, "provider_independent_freshness_required": True,
        "canonical_state_sha256": p["canonical"]["sha256"], "event_3_id": p["event_3_id"],
        "production_runtime_effectivity_pin_sha256": authority.pin_sha,
        "controller_source_sha256": p["controller"]["sha256"], "provider_source_sha256": p["provider"]["sha256"],
        "receipt_contract_sha256": p["receipt_contract"]["sha256"], "enforcement_identity": p["enforcement_identity"],
        "base_attempt_id": item["base_attempt_id"], "work_item_identity": copy.deepcopy(item),
        "network_mode": "RESTRICTED_DEFAULT", "allowed_origins": list(ORIGINS),
        "security_projection_sha256": observation["security_projection_sha256"],
        "client_authorization_verdict": observation["client_verdict"],
        "client_authorization_evidence_sha256": observation["client_evidence_sha256"],
        "client_authorization_policy_sha256": p["security_contracts"]["client_authorization_contract_candidate.json"]["sha256"]}


def verify_receipt(authority, item, raw, observation, *, issuance=None):
    if not item["build_network_required"]:
        a.require(raw is None, "NONE receipt present")
        return None
    a.require(isinstance(raw, bytes), "restricted receipt null/missing")
    value = a.loads(raw)
    a.require(set(value) == RECEIPT_FIELDS and raw == a.canonical(value), "wrong/noncanonical receipt bytes/schema fields")
    expected = receipt_value(authority, item, observation)
    if issuance is not None:
        a.require(issuance["security_projection_sha256"] == observation["security_projection_sha256"]
                  and issuance["client_verdict"] == observation["client_verdict"], "fresh issuance/projection/client mismatch")
        expected["client_authorization_evidence_sha256"] = issuance["client_evidence_sha256"]
    a.require(a.canonical(value) == a.canonical(expected), "receipt semantic binding/schema/reuse/freshness mismatch")
    return a.sha(raw)


class ReceiptBoundLedger(ledger.Ledger):
    """V1 adds receipt_sha256 atomically; all durable filesystem helpers are inherited."""
    def __init__(self, authority):
        a.require(type(authority) is Authority, "unrecognized ledger authority")
        ledger.safe_path(authority.root)
        a.require(authority.mode in (REAL, SYNTHETIC), "claim namespace")
        if authority.mode == REAL:
            a.require(authority.root == a.OUTPUT_ROOT, "wrong real ledger root")
        else:
            a.require(authority.root.is_relative_to(QUALIFICATION_ROOT), "synthetic real ledger forbidden")
        self.root, self.namespace = authority.root, authority.mode
        self.real_ids = frozenset(x["base_attempt_id"] for x in authority.population["items"])
        self.authority = authority

    def _path(self, name, attempt):
        a.require(name in {"claims", "terminals", "locks"}, "ledger path kind")
        a.require(isinstance(attempt, str) and re.fullmatch(r"[A-Za-z0-9_-]+", attempt)
                  and attempt in self.real_ids, "unknown/unsafe attempt identity")
        if self.namespace == SYNTHETIC:
            a.require(attempt.startswith("SYNTHETIC_QUALIFICATION_"), "real identity forbidden in synthetic ledger")
        path = self.root / "ledger" / name / (attempt + ".json")
        ledger.safe_path(path)
        return path

    def claim(self, attempt, binding, *, permit=None):
        a.require(isinstance(permit, legacy.Admission) and type(permit).__name__ == "ProductionAdmission"
                  and permit.item["base_attempt_id"] == attempt and permit.binding == binding,
                  "versioned real/synthetic claim requires production Admission")
        a.require(permit.controller.authority.mode == self.namespace
                  and permit.controller.authority.root == self.root
                  and binding["effectivity_pin_sha256"] == self.authority.pin_sha,
                  "permit namespace/root/effectivity does not belong to ledger")
        fresh = permit.revalidate()
        digest = binding["receipt_sha256"]
        a.require(digest is None if not permit.item["build_network_required"] else
                  isinstance(digest, str) and a.shared.HEX64.fullmatch(digest), "claim receipt binding")
        a.require(digest == (a.sha(permit.receipt_raw) if permit.receipt_raw is not None else None), "claim receipt SHA mismatch")
        a.require(self.state(attempt) == "UNSTARTED", "duplicate claim/no automatic retry")
        # The new immutable association is fully durable/read back before the original lock.
        association = publish_raw_association(self.authority, permit.item, permit.receipt_raw, fresh,
                                              permit.issuance_observation, stage="PRECLAIM")
        owner = uuid.uuid4().hex
        body = {"namespace": self.namespace, "attempt_id": attempt, "owner": owner}
        ledger.exclusive_write(self._path("locks", attempt), a.canonical(body))
        a.require(not self._path("terminals", attempt).exists(), "terminal before claim")
        record = {**body, "operation": "CLAIM", "input_runtime_binding": {**binding, "raw_evidence_association_sha256": association},
                  "state": "CLAIMED_NO_TERMINAL", "attempt_consumed": True, "receipt_sha256": digest}
        ledger.exclusive_write(self._path("claims", attempt), a.canonical(record))
        return record


def verify_claim(authority, item, claim, raw):
    a.require(type(authority) is Authority, "unrecognized provider authority")
    authority.refresh()
    authority.select(item)
    journal = authority.journal()
    a.require(a.canonical(journal._read(journal._path("claims", item["base_attempt_id"]))) == a.canonical(claim),
              "durable claim differs from supplied claim")
    a.require(journal.state(item["base_attempt_id"]) == "CLAIMED_NO_TERMINAL", "receipt after terminal/reuse")
    issuance = read_claim_association(authority, item, claim, raw)
    observation = authority.observe("PROVIDER_PREBUILD")
    digest = verify_receipt(authority, item, raw, observation, issuance=issuance)
    a.require(claim["attempt_id"] == item["base_attempt_id"]
              and claim["receipt_sha256"] == claim["input_runtime_binding"]["receipt_sha256"] == digest,
              "provider receipt SHA must equal exact durable claim SHA")
    expected = {"item": item, "effectivity_pin_sha256": authority.pin_sha,
                "receipt_sha256": digest, "security_projection_sha256": observation["security_projection_sha256"]}
    a.require(all(a.canonical(claim["input_runtime_binding"].get(k)) == a.canonical(v) for k, v in expected.items()), "claim work/runtime binding")
    publish_raw_association(authority, item, raw, observation, issuance, stage="PROVIDER_PREBUILD")
    return observation["security_projection"]


def compile_production_transport(item, plan, topology, *, receipt_raw):
    a.require(item == a.work_item(plan, item["variant"]), "scientific work binding")
    recipe = a.engine_recipe(plan)
    scientific = a.shared.build_definition(recipe, source_present=item["variant"] != "SOURCE_INDEPENDENT",
        dependency_present=plan["recipe_candidate"]["requirements"]["dependency_bytes_b64"] is not None)
    required = item["build_network_required"]
    a.require(isinstance(receipt_raw, bytes) if required else receipt_raw is None, "transport receipt/NONE binding")
    proxy_name = frozen_inputs()["proxy"]["proxy_name"]
    proxy_url = "http://" + proxy_name + ":3128"
    args = {"HTTP_PROXY": proxy_url, "HTTPS_PROXY": proxy_url, "PIP_INDEX_URL": "https://pypi.org/simple"} if required else {}
    options = [] if required else ["force-network-mode=none"]
    guards.network_binding(required=required, options=options, build_args=args, proxy_url=proxy_url, receipt=receipt_raw)
    return {"base_attempt_id": item["base_attempt_id"], "scientific_base_authority": item["base_image_reference"],
        "scientific_dockerfile": scientific,
        "execution_dockerfile": guards.execution_dockerfile(scientific, frozen_base=item["base_image_reference"], restricted=required),
        "build_args": args, "frontend_options": options, "execution_network": "NONE"}


class NativeProductionTransport:
    """One solve on the independently verified exact daemon; no implicit acquisition."""
    def __init__(self, provider, compiled, binding, layout, artifact_root):
        a.require(type(provider) is ProductionProvider and type(provider.authority) is Authority
                  and provider.authority.mode == REAL and Path(__file__).resolve() == a.ROOT / PROVIDER_TARGET,
                  "native production transport requires exact installed provider and real authority")
        self.provider, self.compiled, self.binding = provider, compiled, binding
        self.layout, self.root, self.used = layout, artifact_root, False

    def invoke(self, argv, *, timeout=600):
        validate_command(argv, self.binding)
        result = subprocess.run(argv, capture_output=True, check=False, timeout=timeout)
        self.provider.persist_command(argv, result)
        return result

    def check(self, argv, *, timeout=600):
        r = self.invoke(argv, timeout=timeout)
        a.require(r.returncode == 0, "native production phase failed; no retry")
        return r

    def build(self, args, *, timeout=1200):
        a.require(not self.used, "native solve retry prohibited")
        network = "--network=default" if self.compiled["build_args"] else "--network=none"
        a.require(args[:5] == ["build", "--platform=linux/amd64", network, "--progress=plain", "--no-cache"]
                  and len(args) == 10 and args[5] == "-t" and args[7] == "-f", "unexpected scientific build command")
        context, tag = Path(args[9]), args[6]
        a.require(Path(args[8]) == context / "Dockerfile"
                  and (context / "Dockerfile").read_bytes() == self.compiled["scientific_dockerfile"], "scientific recipe mutation")
        a.shared.context_manifest(context)
        verify_layout(self.layout, self.binding)
        verify_claim(self.provider.authority, self.provider.item, self.provider.claim, self.provider.receipt_raw)
        self.used = True
        ledger.mkdir_durable(self.root.parent)
        a.require(not self.root.exists(), "transport evidence overwrite")
        self.root.mkdir(mode=0o700)
        staged = self.root / "execution-context"
        shutil.copytree(context, staged, symlinks=True)
        (staged / "Dockerfile").write_bytes(self.compiled["execution_dockerfile"])
        expected = a.shared.context_manifest(staged)
        cid, croot = self.binding["container_id"], self.binding["container_root"]
        self.check(["docker", "exec", cid, "mkdir", "-p", croot])
        self.check(["docker", "cp", str(self.layout), cid + ":" + croot + "/oci"])
        self.check(["docker", "cp", str(staged), cid + ":" + croot + "/context"])
        readback = self.root / "readback-context"
        self.check(["docker", "cp", cid + ":" + croot + "/context", str(readback)])
        a.require(a.shared.context_manifest(readback) == expected, "context copy/readback identity drift")
        returned_layout = self.root / "readback-oci"
        self.check(["docker", "cp", cid + ":" + croot + "/oci", str(returned_layout)])
        verify_layout(returned_layout, self.binding)
        argv = native.native_argv(self.binding, croot, tag, self.compiled)
        result = self.invoke(["docker", "exec", cid] + argv, timeout=timeout)
        ledger.exclusive_write(self.root / "native-build.log", result.stdout + result.stderr)
        if result.returncode:
            return subprocess.CompletedProcess(args, result.returncode, result.stdout + result.stderr)
        a.require(not re.search(rb"(docker\.io|registry-1\.docker\.io|auth\.docker\.io)", result.stdout + result.stderr), "registry fallback observed")
        expected_sha = self.check(["docker", "exec", cid, "sha256sum", croot + "/output.docker.tar"]).stdout.decode().split()[0]
        artifact = self.root / "output.docker.tar"
        self.check(["docker", "cp", cid + ":" + croot + "/output.docker.tar", str(artifact)])
        a.require(native.file_sha(artifact) == expected_sha, "native Docker exporter copy/hash mismatch")
        loaded = self.check(["docker", "load", "-i", str(artifact)])
        image = a.loads(self.check(["docker", "image", "inspect", tag]).stdout)[0]
        layers = self.binding["ordered_rootfs_diff_ids"]
        a.require(tag in image["RepoTags"] and (image["Os"], image["Architecture"]) == ("linux", "amd64")
                  and image["RootFS"]["Layers"][:len(layers)] == layers, "output platform/base RootFS mismatch")
        ledger.exclusive_write(self.root / "native-transport-receipt.json", a.canonical({
            "artifact_sha256": expected_sha, "image_id": image["Id"], "RootFS": image["RootFS"],
            "scientific_base_authority": self.compiled["scientific_base_authority"],
            "base_attempt_id": self.compiled["base_attempt_id"], "receipt_sha256": self.provider.claim["receipt_sha256"]}))
        return subprocess.CompletedProcess(args, 0, result.stdout + result.stderr + loaded.stdout)


def verify_layout(layout, binding):
    ledger.safe_path(layout)
    a.require(layout.is_dir(), "missing local OCI frozen base; no pull/fallback")
    blobs = layout / "blobs/sha256"
    manifest_id = binding["local_oci_manifest_identity"].removeprefix("sha256:")
    index = exact_json(layout / "index.json")
    a.require(len(index["manifests"]) == 1 and index["manifests"][0]["digest"] == "sha256:" + manifest_id,
              "local OCI manifest identity")
    def blob(ref):
        path = blobs / ref["digest"].removeprefix("sha256:")
        ledger.safe_path(path)
        raw = path.read_bytes()
        a.require(len(raw) == ref["size"] and "sha256:" + a.sha(raw) == ref["digest"], "OCI blob digest/size")
        return raw
    manifest = a.loads(blob(index["manifests"][0]))
    config = a.loads(blob(manifest["config"]))
    a.require(manifest["config"]["digest"] == binding["engine_config_identity"]
              and config["rootfs"]["diff_ids"] == binding["ordered_rootfs_diff_ids"]
              and (config["os"], config["architecture"]) == ("linux", "amd64"), "OCI frozen config/diffID/platform")
    for ref in manifest["layers"]:
        blob(ref)


def validate_command(argv, binding):
    a.require(isinstance(argv, list) and argv and all(isinstance(x, str) for x in argv), "command shape")
    a.require(argv[0] == "docker" and len(argv) > 1, "host buildctl/source fetch forbidden")
    a.require(not any(x in {"pull", "fetch", "clone", "buildx", "--pull", "--network=host"} for x in argv), "acquisition/Buildx solve forbidden")
    if argv[1] == "exec":
        a.require(argv[2] == binding["container_id"], "wrong daemon instance")
        cmd = argv[3:]
        if cmd[:1] == ["/usr/bin/buildctl"]:
            expected = native.native_argv(binding, binding["container_root"], binding["tag"], binding["compiled"])
            guards.native_command(cmd, expected)
        elif cmd[:3] == ["mkdir", "-p", binding["container_root"]]:
            a.require(len(cmd) == 3, "mkdir command scope")
        else:
            a.require(cmd == ["sha256sum", binding["container_root"] + "/output.docker.tar"], "daemon exec scope")
    elif argv[1] == "cp":
        a.require(len(argv) == 4, "copy scope")
        a.require(any(x.startswith(binding["container_id"] + ":" + binding["container_root"] + "/") for x in argv[2:]), "copy daemon/root scope")
    elif argv[1] == "load":
        a.require(len(argv) == 4 and argv[2] == "-i", "Docker load scope")
    elif argv[1:3] == ["image", "inspect"]:
        a.require(len(argv) == 4, "inspection scope")
    elif argv[1] == "run":
        a.require([x for x in argv if x.startswith("--network")] == ["--network=none"]
                  and "--pull=never" in argv and not any(x.startswith("--pull=") and x != "--pull=never" for x in argv), "network on probe/NONE or pull")
    else:
        raise a.Rejected("unapproved native provider command")


def shared_scientific_engine(transport):
    """Private binding of shared scientific functions; no frozen qualification code copied."""
    a.require(type(transport) in (NativeProductionTransport, SyntheticScientificTransport), "accepted native transport required")
    bound = dict(a.shared.__dict__)
    for name, value in a.shared.__dict__.items():
        if isinstance(value, types.FunctionType) and value.__globals__ is a.shared.__dict__:
            function = types.FunctionType(value.__code__, bound, value.__name__, value.__defaults__, value.__closure__)
            function.__kwdefaults__ = value.__kwdefaults__
            bound[name] = function
    def docker(args, *, timeout=600):
        args = list(args)
        if args[:1] == ["build"]:
            return transport.build(args, timeout=timeout)
        if args[:1] == ["run"] and "--pull=never" not in args:
            args.insert(1, "--pull=never")
        return transport.invoke(["docker", *args], timeout=timeout)
    bound["docker"], bound["docker_observation"] = docker, docker
    return types.SimpleNamespace(**bound)


class ProductionProvider:
    def __init__(self, authority, item, claim, receipt_raw):
        a.require(type(authority) is Authority, "unrecognized provider authority")
        self.authority, self.item, self.claim, self.receipt_raw = authority, item, claim, receipt_raw
        self.topology = verify_claim(authority, item, claim, receipt_raw)
        self.command_number = 0

    def persist_command(self, argv, result):
        self.command_number += 1
        path = self.authority.root / "attempts" / self.item["base_attempt_id"] / "transport-commands"
        ledger.mkdir_durable(path)
        ledger.exclusive_write(path / (str(self.command_number) + ".json"), a.canonical({"argv": argv,
            "returncode": result.returncode, "stdout_sha256": a.sha(result.stdout), "stderr_sha256": a.sha(result.stderr)}))

    def execute(self):
        a.require(self.authority.mode == REAL, "synthetic provider must use explicit candidate-only fixture interface")
        verify_claim(self.authority, self.item, self.claim, self.receipt_raw)
        plan = self.authority.select(self.item)
        values = a.embedded_inputs(self.authority.manifest, plan)
        for key, relative in a.input_paths(self.item).items():
            if values[key] is not None:
                path = self.authority.root / relative
                ledger.mkdir_durable(path.parent)
                ledger.exclusive_write(path, values[key])
        snapshot = None
        if self.item["variant"] != "SOURCE_INDEPENDENT":
            source = "snapshots/" + self.item["base_attempt_id"]
            ledger.mkdir_durable(self.authority.root / "snapshots")
            digest = legacy.source_function(plan, self.item)(a.engine_recipe(plan), self.item["variant"], self.authority.root / source)
            ledger.persist_tree(self.authority.root / source)
            snapshot = {"sha256": digest, "source_revision_sha": self.item["source_revision_sha"], "source": source}
        proposal = a.engine_call_proposal(self.authority.manifest, self.item, snapshot=snapshot)
        compiled = compile_production_transport(self.item, plan, self.topology, receipt_raw=self.receipt_raw)
        maps = exact_json(a.ROOT / NATIVE / "seven_base_transport_map.json")
        matches = [x for x in maps["mapping"] if x["scientific_base_authority"] == self.item["base_image_reference"]]
        a.require(len(matches) == 1, "unique scientific base transport required")
        base = matches[0]
        layouts = self.authority.payload["base_layouts"]
        layout = Path(layouts[self.item["base_image_reference"]])
        # Installation may name durable exact local layouts, never registry fallback.
        a.require(layout.is_relative_to(a.OUTPUT_ROOT), "local base layout outside accepted persistent root")
        proxy_network = self.topology["proxy_network_binding"][self.authority.config["internal_network"]]
        ipaddress.ip_address(proxy_network["IPAddress"])
        binding = {**base, "endpoint": self.authority.config["endpoint"],
            "native_binary_sha256": self.authority.config["client_binary_sha256"], "same_daemon": True,
            "daemon_count": 1, "runtime_reference": self.authority.config["runtime_image"]["immutable_reference"],
            "frontend_alias": "errpilot_frozen_base", "container_id": self.topology["daemon_instance_identity"]["container_id"],
            "container_root": "/tmp/errpilot-v6-" + self.item["base_attempt_id"],
            "proxy_internal_host_binding": "add-hosts=" + self.authority.config["proxy"]["proxy_name"] + "=" + proxy_network["IPAddress"],
            "tag": "errpilot-synthetic-materializer:" + self.item["base_attempt_id"].lower() + "-" + self.item["variant"].lower(),
            "compiled": compiled}
        output = Path(proposal["output"])
        ledger.mkdir_durable(output.parent)
        transport = NativeProductionTransport(self, compiled, binding, layout, self.authority.root / "transport" / self.item["base_attempt_id"])
        result = shared_scientific_engine(transport)._materialize_checked(proposal["fixture"], output=output,
                    input_root=self.authority.root, synthetic_only=False, single_identity=True)
        hashes = ledger.persist_tree(output)
        transport_hashes = ledger.persist_tree(transport.root) if transport.root.exists() else {}
        evidence = {"artifact_sha256": hashes, "transport_artifact_sha256": transport_hashes,
                    "input_runtime_binding": self.claim["input_runtime_binding"], "receipt_sha256": self.claim["receipt_sha256"]}
        if result["status"] == "MATERIALIZED":
            r = result["revisions"][0]
            evidence.update(dict(zip(ledger.SUCCESS, (r["dockerfile_sha256"], r["build_context_manifest_sha256"],
                a.sha(b"ABSENT\n") if snapshot is None else snapshot["sha256"], r["build_log_sha256"],
                r["image_inspect_sha256"], a.identity(r["observed_python"]), r["installed_distribution_manifest_sha256"],
                r["environment_identity_sha256"]))))
        return result["status"], evidence, result.get("reason", "")

    def execute_synthetic(self, scenario):
        a.require(self.authority.mode == SYNTHETIC
                  and Path(__file__).resolve() == a.ROOT / RESUME / "production_provider_successor_candidate.py"
                  and type(scenario) is SyntheticScenario, "synthetic test provider unavailable from installed real entry")
        verify_claim(self.authority, self.item, self.claim, self.receipt_raw)
        plan = self.authority.select(self.item)
        normalized_item = a.work_item(plan, self.item["variant"])
        values = a.embedded_inputs(self.authority.manifest, plan)
        for key, relative in a.input_paths(self.item).items():
            if values[key] is not None:
                path = self.authority.root / relative
                ledger.mkdir_durable(path.parent)
                ledger.exclusive_write(path, values[key])
        proposal = a.engine_call_proposal(self.authority.manifest, normalized_item)
        fixture = copy.deepcopy(proposal["fixture"])
        for key, relative in a.input_paths(self.item).items():
            if key in fixture:
                fixture[key] = relative
        compiled = compile_production_transport(normalized_item, plan, self.topology, receipt_raw=self.receipt_raw)
        compiled["base_attempt_id"] = self.item["base_attempt_id"]
        output = self.authority.root / "attempts" / self.item["base_attempt_id"]
        transport = SyntheticScientificTransport(self, compiled, a.engine_recipe(plan), scenario)
        # The accepted shared scientific code object is invoked through our bounded
        # transport. False selects the original checked scientific path, not real I/O:
        # the owning transport, IDs, root, and constructor all remain synthetic.
        result = shared_scientific_engine(transport)._materialize_checked(fixture, output=output,
                    input_root=self.authority.root, synthetic_only=False, single_identity=True)
        ledger.exclusive_write(output / "candidate_scientific_run.json", a.canonical({
            "schema": "V6_CANDIDATE_HERMETIC_SCIENTIFIC_RUN_V2", "synthetic_only": True,
            "real_build": False, "real_authorization": False,
            "shared_checked_path_argument": False, "meaning": "Original checked scientific path through bounded simulated I/O; no real materialization"}))
        hashes = ledger.persist_tree(output)
        evidence = {"artifact_sha256": hashes, "synthetic_only": True, "real_build": False,
                    "shared_scientific_code_sha256": a.sha(a.shared._materialize_checked.__code__.co_code),
                    "receipt_sha256": self.claim["receipt_sha256"], "synthetic_transport_calls": transport.calls}
        if result["status"] == "MATERIALIZED":
            r = result["revisions"][0]
            evidence.update(dict(zip(ledger.SUCCESS, (r["dockerfile_sha256"], r["build_context_manifest_sha256"],
                a.sha(b"ABSENT\n"), r["build_log_sha256"], r["image_inspect_sha256"], a.identity(r["observed_python"]),
                r["installed_distribution_manifest_sha256"], r["environment_identity_sha256"]))))
        return result["status"], evidence, result.get("reason", "")


# V2 authority and security interfaces. The frozen native/scientific functions
# above retain their original bodies; all new evidence is versioned separately.
REAL_RECEIPT_SCHEMA = "V6_RESTRICTED_BUILD_EGRESS_ENFORCEMENT_RECEIPT_V2"
SECURITY_CONTRACT_NAMES = (
    "client_authorization_contract_candidate.json", "topology_stability_contract_candidate.json",
    "raw_observation_contract_candidate.json", "transient_diagnostics_contract_candidate.json",
    "receipt_schema_v2_candidate.json", "raw_sidecar_contract_candidate.json",
)
LIVE_OBSERVER_TARGET = SCREENING + "v6_preparation_live_security_observer_v2.py"
RAW_SOURCES = ("daemon", "proxy", "network", "worker", "images", "proxy_source", "proxy_policy",
               "unix_sockets", "routes", "socket_access", "listener_inventory", "client_census", "client_evidence")
ADMISSIBLE_CLIENT_SOURCES = {"AUTHENTICATED_HOST_LAUNCH_PROVENANCE", "CORRELATED_ENGINE_EXEC_METADATA",
    "INDEPENDENT_SOCKET_ACCESS_RESTRICTIONS", "VERIFIED_CONTAINER_PROCESS_ENDPOINT_RELATIONSHIP",
    "SEPARATELY_REVIEWED_EQUIVALENT"}
LISTENER_PATHS = ["/run/buildkit/buildkitd.sock", "/run/buildkit/otel-grpc.sock"]


def verify_security_contracts(authority):
    refs = authority.payload["security_contracts"]
    a.require(set(refs) == set(SECURITY_CONTRACT_NAMES), "missing/versioned security contracts")
    for name in SECURITY_CONTRACT_NAMES:
        expected = RESUME + name if authority.mode == SYNTHETIC else SCREENING + name.replace("_candidate", "_installed_v2")
        a.require(refs[name]["path"] == expected, "wrong security contract source location")
        raw = a.read_exact(expected, refs[name]["sha256"])
        a.loads(raw)
    policy = a.loads(a.read_exact(refs[SECURITY_CONTRACT_NAMES[0]]["path"], refs[SECURITY_CONTRACT_NAMES[0]]["sha256"]))
    a.require(set(policy["C1_C16"]) == {"C" + str(i) for i in range(1, 17)}
              and set(policy["admissible_kinds"]) == ADMISSIBLE_CLIENT_SOURCES,
              "client policy incomplete/drift")


def synthetic_plan(authority, item):
    a.require(authority.mode == SYNTHETIC, "synthetic plan in production")
    plan = a.select(authority.manifest, ordinal=item["census_order"], case_id=item["case_id"], plan_sha=item["plan_sha256"])
    normalized = a.work_item(plan, item["variant"])
    expected = {**normalized, "base_attempt_id": "SYNTHETIC_QUALIFICATION_" + item["case_id"].removeprefix("SYNTHETIC_")}
    a.require(a.canonical(item) == a.canonical(expected), "synthetic scientific work identity drift")
    a.require(item["variant"] == "SOURCE_INDEPENDENT", "candidate fixture source export prohibited")
    return plan


def collect_live_raw(authority, stage):
    """Only a separately reviewed fixed source may acquire authenticated live data.

    No observer/provider/topology/census/root object or fixture is accepted from
    callers. The absent live observer is a hard production prerequisite, not a
    value populated from historical observations or candidate fixtures.
    """
    a.require(authority.mode == REAL and Path(__file__).resolve() == a.ROOT / PROVIDER_TARGET,
              "live observer requires installed real source")
    ref = authority.payload["live_evidence_observer"]
    a.require(set(ref) == {"path", "sha256", "HUMAN_PI_ACCEPTED", "C6_equivalent_source_reviewed"}
              and ref["path"] == LIVE_OBSERVER_TARGET and ref["HUMAN_PI_ACCEPTED"] == "YES"
              and ref["C6_equivalent_source_reviewed"] is True,
              "BLOCKED_UNTIL_INDEPENDENT_LIVE_EVIDENCE: separately reviewed C6 observer absent")
    a.read_exact(LIVE_OBSERVER_TARGET, ref["sha256"])
    # This challenge identifies one acquisition, never a bearer claim credential.
    acquisition = uuid.uuid4().hex
    import sys
    result = subprocess.run([sys.executable, "-B", str(a.ROOT / LIVE_OBSERVER_TARGET),
        "--stage", stage, "--acquisition-id", acquisition], capture_output=True, check=False, timeout=60)
    a.require(result.returncode == 0, "independent authenticated live observation unavailable")
    bundle = a.loads(result.stdout)
    a.require(bundle.get("namespace") == REAL and bundle.get("synthetic_only") is False
              and bundle.get("acquisition_id") == acquisition and bundle.get("stage") == stage
              and bundle.get("authenticated_observer_source_sha256") == ref["sha256"],
              "live source/authentication/fresh acquisition mismatch")
    return bundle


def source_value(bundle, name):
    source = bundle["sources"][name]
    a.require(set(source) == {"raw_utf8", "sha256", "source", "method", "timestamp", "missing", "unverifiable"},
              "raw source metadata completeness")
    raw = source["raw_utf8"].encode("utf-8")
    a.require(source["sha256"] == a.sha(raw) and all(isinstance(source[k], str) and source[k] for k in
              ("source", "method", "timestamp")) and source["missing"] == [] and source["unverifiable"] == [],
              "raw original source SHA/missing/unverifiable evidence")
    return raw


def parse_socket_rows(raw):
    rows = raw.decode().splitlines()
    a.require(rows and rows[0].split() == ["Num", "RefCount", "Protocol", "Flags", "Type", "St", "Inode", "Path"],
              "Unix socket table unavailable/malformed")
    result = []
    for line in rows[1:]:
        p = line.split()
        a.require(len(p) in (7, 8) and all(re.fullmatch(r"[0-9a-fA-F]+", x.rstrip(":")) for x in p[:7]),
                  "unparseable Unix record blocks")
        result.append(dict(zip(("Num", "RefCount", "Protocol", "Flags", "Type", "St", "Inode", "Path"), p + ([""] if len(p) == 7 else []))))
    return result


def verify_routes(raw, inventory):
    rows = raw.decode().splitlines()
    a.require(rows and rows[0].split()[:4] == ["Iface", "Destination", "Gateway", "Flags"], "route table missing")
    routes = []
    for line in rows[1:]:
        parts = line.split()
        a.require(len(parts) == 11 and re.fullmatch(r"[0-9A-Fa-f]{8}", parts[1])
                  and parts[1] != "00000000" and parts[2] == "00000000"
                  and parts[0] == "eth0" and not int(parts[3], 16) & 2,
                  "external/default daemon route")
        routes.append({"interface": parts[0], "destination": parts[1], "gateway": parts[2], "flags": parts[3], "mask": parts[7]})
    a.require(routes and inventory["ipv6_route_inventory"] == [] and inventory["ipv6_complete"] is True,
              "IPv6 routes unverifiable/external")
    return sorted(routes, key=a.canonical)


def verify_clients(census, evidence, socket_rows, *, synthetic, accepted_principals):
    a.require(set(census) == {"sessions", "observed_session_ids", "covered_surfaces", "unobserved_surfaces", "complete"}, "client census schema")
    a.require(census["complete"] is True and census["unobserved_surfaces"] == []
              and sorted(census["covered_surfaces"]) == ["CONTAINER_PROCESS", "ENGINE_EXEC_ATTACH", "HOST_LAUNCH", "NETWORK_ENDPOINT", "UNIX_ACCESS"],
              "incomplete active client census/unobserved surfaces")
    a.require(set(evidence) == {"namespace", "sessions", "boundary", "approved_principals"}
              and evidence["namespace"] == (SYNTHETIC if synthetic else REAL), "client authentication namespace")
    a.require(isinstance(accepted_principals, list) and bool(accepted_principals)
              and all(isinstance(x, str) and x and x != "UNKNOWN" for x in accepted_principals)
              and evidence["approved_principals"] == accepted_principals,
              "client principals not independently accepted by effectivity authority")
    boundary = evidence["boundary"]
    a.require(boundary["verified_access_restrictions"] is True and boundary["complete"] is True
              and boundary["source_kind"] == "INDEPENDENT_SOCKET_ACCESS_RESTRICTIONS"
              and boundary["unverifiable_surfaces"] == [] and a.shared.HEX64.fullmatch(boundary["source_sha256"])
              and boundary["source_sha256"] == a.sha(boundary["original_source_utf8"].encode()),
              "unverifiable control-plane access boundary")
    sessions = census["sessions"]
    ids = [s["session_id"] for s in sessions]
    proofs = evidence["sessions"]
    a.require(len(ids) == len(set(ids)) and sorted(ids) == sorted(census["observed_session_ids"])
              and sorted(ids) == sorted(s["session_id"] for s in proofs) and len(ids) == len(proofs),
              "incomplete/duplicate active session attribution")
    classified = []
    for session in sessions:
        proof = next(s for s in proofs if s["session_id"] == session["session_id"])
        a.require(proof["source_kind"] in ADMISSIBLE_CLIENT_SOURCES
                  and proof["authenticated_source"] is True and proof["correlation_complete"] is True
                  and proof["session_endpoint"] == session["endpoint"]
                  and proof["process_identity"] == session["process_identity"]
                  and a.shared.HEX64.fullmatch(proof["source_sha256"])
                  and proof["source_sha256"] == a.sha(proof["original_source_utf8"].encode()), "UNKNOWN client: insufficient independent attribution")
        verdict = proof["classification"]
        a.require(verdict in {"AUTHORIZED", "UNABLE_TO_ACCESS_CONTROL_PLANE"}, "UNKNOWN/UNAUTHORIZED active client blocks")
        if verdict == "AUTHORIZED":
            a.require(proof["principal"] in evidence["approved_principals"] and proof["principal"] != "UNKNOWN"
                      and session["control_capable"] is True, "client principal/access not independently authorized")
        else:
            a.require(proof["independent_inaccessibility"] is True and session["control_capable"] is False,
                      "unverified client inaccessibility")
            a.require(session["socket_inodes"] == [], "inaccessible client has control connection")
        classified.append({"session_id": session["session_id"], "classification": verdict})
    connected = sorted(r["Inode"] for r in socket_rows if r["St"] == "03")
    covered = sorted(i for s in sessions for i in s["socket_inodes"])
    a.require(connected == covered, "unattributed connected Unix socket/client")
    return {"verdict": "SYNTHETIC_CLIENT_AUTHORIZATION_PASS" if synthetic else "REAL_CLIENT_AUTHORIZATION_PASS",
            "classified": sorted(classified, key=lambda x: x["session_id"])}


def verify_raw_security(bundle, config, *, stage, synthetic, accepted_principals=None):
    a.require(bundle["schema"] == "V6_FULL_RAW_OBSERVATION_ENVELOPE_V2"
              and bundle["synthetic_only"] is synthetic and set(bundle["sources"]) == set(RAW_SOURCES),
              "raw observation namespace/schema/source completeness")
    raw = {n: source_value(bundle, n) for n in RAW_SOURCES}
    objects = {n: a.loads(raw[n]) for n in ("daemon", "proxy", "network", "worker")}
    images = a.loads(raw["images"])
    identities = {}
    for role in ("daemon", "proxy"):
        entry = images[role]
        identity = verify_image_identity(objects[role], entry["store"], entry["selected"],
            entry["index_raw"].encode(), entry["manifest_raw"].encode(), entry["config_raw"].encode(), image_identity_pins(config, role))
        identities[role] = {**identity, "RootFS": entry["selected"]["RootFS"]}
        a.require(objects[role]["image_config_digest"] == identity["OCI_CONFIG_DIGEST"], "wrong independently verified config digest")
    sockets = parse_socket_rows(raw["unix_sockets"])
    a.require(objects["daemon"]["sockets"] == raw["unix_sockets"].decode()
              and objects["daemon"]["routes"] == raw["routes"].decode(), "raw/inspect socket/route evidence mismatch")
    listeners = [{k: r[k] for k in ("Path", "Protocol", "Flags", "Type", "St")} for r in sockets if int(r["Flags"], 16) & 65536]
    listeners.sort(key=lambda x: x["Path"])
    expected = [{"Path": path, "Protocol": "00000000", "Flags": "00010000", "Type": "0001", "St": "01"} for path in LISTENER_PATHS]
    a.require(listeners == expected, "unexpected/duplicate Unix listener")
    a.require(all(r["St"] == "03" or int(r["Flags"], 16) & 65536 for r in sockets), "unclassified Unix socket entry")
    inventory = a.loads(raw["listener_inventory"])
    a.require(inventory["complete"] is True and inventory["unverifiable_surfaces"] == []
              and inventory["tcp"] == [] and inventory["udp"] == []
              and sorted(inventory["unix_listener_paths"]) == LISTENER_PATHS,
              "external/unverifiable listener inventory")
    routes = verify_routes(raw["routes"], inventory)
    access = a.loads(raw["socket_access"])
    a.require(access["complete"] is True and access["unverifiable"] == [] and access["ownership_observation"] == "INDEPENDENT_LSTAT_ACL_MOUNT_USER_NAMESPACE",
              "unverifiable socket ownership/access restrictions")
    a.require(sorted(x["path"] for x in access["endpoints"]) == LISTENER_PATHS and len(access["endpoints"]) == 2,
              "endpoint access inventory")
    for endpoint in access["endpoints"]:
        a.require(endpoint["type"] == "SOCKET" and type(endpoint["uid"]) is int and type(endpoint["gid"]) is int
                  and type(endpoint["mode"]) is int and endpoint["mode"] & 7 == 0
                  and endpoint["unauthorized_access"] is False and endpoint["acl_complete"] is True,
                  "unauthorized/unverifiable endpoint permissions")
    if synthetic and accepted_principals is None:
        accepted_principals = ["SYNTHETIC_HUMAN_PI_APPROVED_PRINCIPAL"]
    result = verify_clients(a.loads(raw["client_census"]), a.loads(raw["client_evidence"]), sockets,
                            synthetic=synthetic, accepted_principals=accepted_principals)
    observed = normalize_topology(objects, raw["proxy_source"], raw["proxy_policy"], config)
    for role in ("daemon", "proxy"):
        ports = objects[role]["NetworkSettings"].get("Ports", {})
        a.require(isinstance(ports, dict) and all(v is None for v in ports.values()), "published port/external control path")
    observed.pop("daemon_socket_observation")
    observed["daemon_routes"] = routes
    observed["schema"] = "V6_STABLE_SECURITY_PROJECTION_V2"
    observed.update(independent_image_identities=identities, unix_listeners=listeners,
                    socket_access=access, listener_inventory=inventory)
    # Client identity/evidence changes remain separately gated and retained; no
    # unknown session can reach a projection PASS by diagnostic exclusion.
    return {"raw_bundle": copy.deepcopy(bundle), "raw_observation_sha256": a.identity(bundle),
        "security_projection": observed, "security_projection_sha256": a.identity(observed),
        "client_evidence_sha256": a.sha(raw["client_evidence"]), "client_verdict": result["verdict"],
        "client_classifications": result["classified"], "observation_stage": stage}


def association_value(item, raw, observation, issuance, stage):
    return {"schema": "V6_IMMUTABLE_RAW_EVIDENCE_ASSOCIATION_V2", "stage": stage,
        "attempt_id": item["base_attempt_id"], "receipt_sha256": a.sha(raw) if raw is not None else None,
        "security_projection_sha256": observation["security_projection_sha256"],
        "raw_observation_sha256": observation["raw_observation_sha256"],
        "issuance_raw_observation_sha256": issuance["raw_observation_sha256"],
        "client_authorization_evidence_sha256": observation["client_evidence_sha256"],
        "issuance_client_authorization_evidence_sha256": issuance["client_evidence_sha256"]}


def publish_raw_association(authority, item, raw, observation, issuance, *, stage):
    authority.select(item)
    if authority.mode == SYNTHETIC:
        a.require(Path(__file__).resolve() == a.ROOT / RESUME / "production_provider_successor_candidate.py"
                  and authority.root.is_relative_to(QUALIFICATION_ROOT), "raw synthetic ownership")
    else:
        a.require(Path(__file__).resolve() == a.ROOT / PROVIDER_TARGET and authority.root == a.OUTPUT_ROOT,
                  "raw real ownership")
    parent = authority.root / "raw-evidence" / item["base_attempt_id"]
    ledger.mkdir_durable(parent)
    path = parent / ("preclaim" if stage == "PRECLAIM" else "provider")
    ledger.safe_path(path)
    if stage == "PRECLAIM":
        a.require(not path.exists(), "orphan/preexisting raw sidecar blocks automatic reentry")
        path.mkdir(mode=0o700)
        ledger.fsync_dir(parent)
    else:
        ledger.mkdir_durable(path)
    for value in (observation["raw_bundle"], issuance["raw_bundle"]):
        payload = a.canonical(value)
        name = path / (a.sha(payload) + ".raw.json")
        if name.exists():
            a.require(name.read_bytes() == payload, "raw immutable readback differs")
        else:
            ledger.exclusive_write(name, payload)
    if raw is not None:
        name = path / (a.sha(raw) + ".receipt.json")
        if name.exists():
            a.require(name.read_bytes() == raw, "receipt immutable readback differs")
        else:
            ledger.exclusive_write(name, raw)
    value = association_value(item, raw, observation, issuance, stage)
    payload = a.canonical(value)
    digest = a.sha(payload)
    name = path / (digest + ".json")
    if name.exists():
        a.require(name.read_bytes() == payload, "association immutable readback differs")
    else:
        ledger.exclusive_write(name, payload)
    ledger.persist_tree(path)
    a.require(name.read_bytes() == payload and all((path / (obs["raw_observation_sha256"] + ".raw.json")).read_bytes()
              == a.canonical(obs["raw_bundle"]) for obs in (observation, issuance)), "raw sidecar durable readback failed before claim")
    return digest


def read_claim_association(authority, item, claim, raw):
    digest = claim["input_runtime_binding"]["raw_evidence_association_sha256"]
    a.require(isinstance(digest, str) and a.shared.HEX64.fullmatch(digest), "claim raw association SHA")
    root = authority.root / "raw-evidence" / item["base_attempt_id"] / "preclaim"
    path = root / (digest + ".json")
    value = exact_json(path)
    a.require(a.sha(path.read_bytes()) == digest and path.read_bytes() == a.canonical(value)
              and value["stage"] == "PRECLAIM" and value["attempt_id"] == item["base_attempt_id"]
              and value["receipt_sha256"] == (a.sha(raw) if raw is not None else None), "raw association receipt/attempt/readback binding")
    observations = []
    for key in ("issuance_raw_observation_sha256", "raw_observation_sha256"):
        source = root / (value[key] + ".raw.json")
        bundle = exact_json(source)
        a.require(source.read_bytes() == a.canonical(bundle) and a.sha(source.read_bytes()) == value[key], "immutable original raw SHA")
        observations.append(verify_raw_security(bundle, authority.config, stage="RETAINED_" + key, synthetic=authority.mode == SYNTHETIC,
                                               accepted_principals=authority.payload["accepted_client_principals"]))
    issuance, preclaim = observations
    a.require(value == association_value(item, raw, preclaim, issuance, "PRECLAIM"), "raw association semantic binding")
    if raw is not None:
        receipt = root / (a.sha(raw) + ".receipt.json")
        ledger.safe_path(receipt)
        a.require(receipt.read_bytes() == raw, "immutable receipt readback")
    verify_receipt(authority, item, raw, preclaim, issuance=issuance)
    return issuance


class SyntheticScenario:
    """Candidate-owned deterministic scientific I/O fixture; no caller callable."""
    def __init__(self, outcome="PASS"):
        a.require(Path(__file__).resolve() == a.ROOT / RESUME / "production_provider_successor_candidate.py"
                  and outcome in {"PASS", "RAISE", "BUILD_FAILED"}, "synthetic scenario unavailable")
        self.outcome = outcome


class SyntheticScientificTransport:
    """Normal candidate-only initialization. Never invokes Docker/subprocess."""
    def __init__(self, provider, compiled, recipe, scenario):
        a.require(Path(__file__).resolve() == a.ROOT / RESUME / "production_provider_successor_candidate.py"
                  and provider.authority.mode == SYNTHETIC and type(scenario) is SyntheticScenario
                  and provider.authority.root.is_relative_to(QUALIFICATION_ROOT), "synthetic scientific transport forbidden in production")
        self.provider, self.compiled, self.recipe, self.scenario = provider, compiled, recipe, scenario
        self.used, self.calls = False, []
        self.image = {"Id": "sha256:" + a.identity({"synthetic_compiled": compiled["scientific_dockerfile"].decode()}),
            "Os": "linux", "Architecture": "amd64", "RootFS": {"Layers": ["sha256:" + a.sha(b"SYNTHETIC_LAYER")]},
            "RepoDigests": [recipe["base_image_reference"]]}

    def build(self, args, *, timeout=1200):
        a.require(not self.used, "synthetic native solve retry prohibited")
        a.require(len(args) == 10 and args[:5] == ["build", "--platform=linux/amd64",
                  "--network=default" if self.compiled["build_args"] else "--network=none", "--progress=plain", "--no-cache"],
                  "synthetic native scientific build command mismatch")
        path = Path(args[9])
        ledger.safe_path(path)
        a.require(path.is_relative_to(self.provider.authority.root) and (path / "Dockerfile").read_bytes() == self.compiled["scientific_dockerfile"],
                  "synthetic scientific recipe/root changed")
        a.shared.context_manifest(path)
        verify_claim(self.provider.authority, self.provider.item, self.provider.claim, self.provider.receipt_raw)
        self.used = True
        maps = exact_json(a.ROOT / NATIVE / "seven_base_transport_map.json")["mapping"]
        base = next(x for x in maps if x["scientific_base_authority"] == self.compiled["scientific_base_authority"])
        cfg = self.provider.authority.config
        binding = {**base, "endpoint": cfg["endpoint"], "native_binary_sha256": cfg["client_binary_sha256"],
            "same_daemon": True, "daemon_count": 1, "runtime_reference": cfg["runtime_image"]["immutable_reference"],
            "frontend_alias": "errpilot_frozen_base", "container_id": "SYNTHETIC_DAEMON",
            "container_root": "/tmp/errpilot-v6-" + self.provider.item["base_attempt_id"], "tag": args[6],
            "proxy_internal_host_binding": "add-hosts=" + cfg["proxy"]["proxy_name"] + "=172.28.0.3", "compiled": self.compiled}
        argv = ["docker", "exec", binding["container_id"], *native.native_argv(binding, binding["container_root"], binding["tag"], self.compiled)]
        validate_command(argv, binding)
        self.calls.append({"synthetic_only": True, "native_argv": argv, "executed": False})
        if self.scenario.outcome == "RAISE":
            raise RuntimeError("SYNTHETIC_PROVIDER_FAILURE")
        return subprocess.CompletedProcess(args, 1 if self.scenario.outcome == "BUILD_FAILED" else 0,
            b"SYNTHETIC_NATIVE_SOLVE_OBSERVATION_ONLY\n", b"")

    def invoke(self, argv, *, timeout=600):
        a.require(argv[:1] == ["docker"], "synthetic command shape")
        args = argv[1:]
        self.calls.append({"argv": argv, "executed": False, "synthetic_only": True})
        if args[:2] == ["image", "inspect"]:
            a.require(len(args) == 3, "synthetic inspect command")
            stdout = a.canonical([self.image])
        elif args[:1] == ["run"]:
            a.require([x for x in args if x.startswith("--network")] == ["--network=none"] and "--pull=never" in args,
                      "synthetic observation egress/pull")
            if "dpkg-query" in args:
                stdout = b"SYNTHETIC_PACKAGE 1\n"
            elif "--format=json" in args:
                stdout = b"[]\n"
            elif args[-1].startswith("import importlib.metadata"):
                stdout = b"[]\n"
            else:
                a.require(args[-2] == "-c" and "executable_sha256" in args[-1], "unexpected synthetic Python probe")
                stdout = a.canonical({"version": self.recipe["python_declared_version"], "machine": "x86_64",
                    "executable": "/usr/local/bin/python", "executable_sha256": self.recipe["python_executable_sha256"]})
        else:
            raise a.Rejected("unapproved synthetic observation command")
        result = subprocess.CompletedProcess(argv, 0, stdout, b"")
        self.provider.persist_command(argv, result)
        return result

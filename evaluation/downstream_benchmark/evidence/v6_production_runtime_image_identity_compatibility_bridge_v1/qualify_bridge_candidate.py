"""Affected pure observation/rejection checks; full controller/provider E2E is NOT_RUN."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from . import candidate_only_identity_observer as seam
from . import corrected_production_provider_candidate as p

HERE = Path(__file__).resolve().parent


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(p.pretty(value))


def main():
    root = seam.QUALIFICATION / (sys.argv[1] if len(sys.argv) == 2 else "run_2")
    root.mkdir(parents=True, exist_ok=False)
    raw = p.exact_json(HERE / "live_image_identity_observations.json")
    provenance = p.exact_json(HERE / "config_digest_provenance.json")
    config = p.frozen_inputs()
    daemon, proxy = copy.deepcopy(raw["daemon"]), copy.deepcopy(raw["proxy"])
    nid, cid, pid = "SYNTHETIC_INTERNAL_NETWORK", "SYNTHETIC_DAEMON", "SYNTHETIC_PROXY"
    daemon.update(Id=cid, State={"Running": True, "StartedAt": "SYNTHETIC_START", "Pid": 101},
                  native_binary_sha256=config["client_binary_sha256"],
                  daemon_binary_sha256=config["daemon_binary_sha256"],
                  routes="SYNTHETIC_INTERNAL_ROUTE", sockets="SYNTHETIC_UNIX_SOCKET")
    proxy.update(Id=pid, State={"Running": True, "StartedAt": "SYNTHETIC_START", "Pid": 102})
    internal = config["internal_network"]
    daemon["NetworkSettings"]["Networks"] = {internal: {"NetworkID": nid, "Gateway": "", "IPAddress": "172.28.0.2"}}
    proxy["NetworkSettings"]["Networks"] = {
        internal: {"NetworkID": nid, "Gateway": "", "IPAddress": "172.28.0.3"},
        "SYNTHETIC_EXTERNAL": {"NetworkID": "SYNTHETIC_EXTERNAL_NETWORK", "IPAddress": "172.29.0.2"}}
    network = {"Id": nid, "Name": internal, "Internal": True, "Driver": "bridge", "IPAM": {},
               "Options": {}, "Containers": {cid: {"Name": cid}, pid: {"Name": pid}}}
    identities = {}
    for role, name in (("daemon", "BuildKit"), ("proxy", "proxy")):
        content = provenance["mapping"][name]
        identities[role] = {"store": raw["engine_store_inspect"] if role == "daemon" else raw["proxy_platform_inspect"],
                            "selected": raw["buildkit_platform_inspect"] if role == "daemon" else raw["proxy_platform_inspect"],
                            "index_raw": provenance["buildkit_index"]["index_raw"] if role == "daemon" else "",
                            "manifest_raw": content["manifest_raw"], "config_raw": content["config_raw"]}
    fixture = {"namespace": seam.NAMESPACE, "runtime_authority": False, "config": config,
               "objects": {"daemon": daemon, "proxy": proxy, "network": network,
                           "worker": [{"ID": "SYNTHETIC_WORKER", "PLATFORMS": ["linux/amd64"]}]},
               "identities": identities, "proxy_source": (p.a.ROOT / p.NATIVE / "proxy.py").read_text(),
               "policy_raw": p.pretty(config["proxy"]["policy"]).decode()}
    write(root / "baseline_fixture.json", fixture)
    fixture = seam.read_fixture(root / "baseline_fixture.json")
    expected = seam.observe_fixture(fixture)
    write(root / "expected_observation.json", expected)
    results, rejections = {}, {}
    results["BuildKit_correct_Engine_and_config"] = {"status": "PASS", "observed": expected["daemon_image_config_digest"]}
    results["proxy_correct_Engine_and_config"] = {"status": "PASS", "observed": expected["proxy_image_config_digest"]}
    assert seam.observe_fixture(fixture, expected) == expected
    results["exact_synthetic_observation_recomparison"] = {"status": "PASS", "sha256": p.a.identity(expected)}

    def reject(name, mutate=None, call=None):
        case = copy.deepcopy(fixture)
        if mutate:
            mutate(case)
            path = root / name / "fixture.json"
            write(path, case)
            case = seam.read_fixture(path)
        try:
            if call:
                call(case)
            else:
                seam.observe_fixture(case, expected)
        except p.a.Rejected as exc:
            rejections[name] = {"status": "PASS_REJECTED", "reason": str(exc),
                                "candidate_logic_exercised": True, "real_ledger_access": False}
        else:
            raise AssertionError("not rejected: " + name)

    for role in ("daemon", "proxy"):
        prefix = "BuildKit" if role == "daemon" else "proxy"
        reject(prefix + "_incorrect_Engine_ID", lambda x, r=role: x["objects"][r].update(Image="sha256:" + "0" * 64))
        reject(prefix + "_incorrect_store_ID", lambda x, r=role: x["identities"][r]["store"].update(Id="sha256:" + "0" * 64))
        reject(prefix + "_incorrect_config_bytes", lambda x, r=role: x["identities"][r].update(config_raw=x["identities"][r]["config_raw"] + " "))
        reject(prefix + "_wrong_platform", lambda x, r=role: x["identities"][r]["selected"].update(Architecture="arm64"))
        reject(prefix + "_wrong_running_manifest", lambda x, r=role: x["objects"][r]["ImageManifestDescriptor"].update(digest="sha256:" + "0" * 64))
        reject(prefix + "_wrong_running_platform", lambda x, r=role: x["objects"][r]["ImageManifestDescriptor"].update(platform={"os": "linux", "architecture": "arm64"}))
        reject(prefix + "_wrong_manifest_provenance", lambda x, r=role: x["identities"][r]["selected"].update(Descriptor={"digest": "sha256:" + "0" * 64}))
        reject(prefix + "_swapped_manifest_config", lambda x, r=role: x["identities"][r].update(
            manifest_raw=x["identities"][r]["config_raw"], config_raw=x["identities"][r]["manifest_raw"]))
        reject(prefix + "_wrong_Config_reference", lambda x, r=role: x["objects"][r]["Config"].update(Image="SYNTHETIC_WRONG_REFERENCE"))
        reject(prefix + "_wrong_RootFS", lambda x, r=role: x["identities"][r]["selected"].update(RootFS={"Type": "layers", "Layers": []}))
        reject(prefix + "_wrong_Engine_config_fields", lambda x, r=role: x["identities"][r]["selected"].update(Config={"Env": ["SYNTHETIC_MUTATION"]}))
        reject(prefix + "_missing_Engine_ID", lambda x, r=role: x["objects"][r].pop("Image"))
        reject(prefix + "_malformed_Engine_ID", lambda x, r=role: x["objects"][r].update(Image={"not": "a digest"}))
        reject(prefix + "_missing_platform", lambda x, r=role: x["identities"][r]["selected"].pop("Os"))
        # Independent OCI-config gate in actual normalize_topology, after content verification.
        def bad_normalized_config(case, r=role):
            objects = copy.deepcopy(case["objects"])
            for n in ("daemon", "proxy"):
                objects[n]["image_config_digest"] = p.image_identity_pins(config, n)["config"]
            objects[r]["image_config_digest"] = "sha256:" + "0" * 64
            p.normalize_topology(objects, case["proxy_source"].encode(), case["policy_raw"].encode(), config)
        reject(prefix + "_incorrect_config_digest", call=bad_normalized_config)
    reject("swapped_index_config_identities", lambda x: x["identities"]["daemon"].update(
        index_raw=x["identities"]["daemon"]["config_raw"], config_raw=x["identities"]["daemon"]["index_raw"]))
    reject("wrong_index_provenance", lambda x: x["identities"]["daemon"].update(index_raw="{}"))
    reject("stale_container_topology", lambda x: x["objects"]["daemon"]["State"].update(StartedAt="SYNTHETIC_STALE_START"))
    reject("stale_topology_preclaim_pure_observation", lambda x: x["objects"]["daemon"]["State"].update(Pid=999))
    reject("extra_daemon_network_attachment", lambda x: x["objects"]["daemon"]["NetworkSettings"]["Networks"].update(EXTRA={"NetworkID": "EXTRA"}))
    reject("changed_internal_network", lambda x: x["objects"]["network"].update(Internal=False))
    reject("changed_internal_network_identity", lambda x: x["objects"]["network"].update(Id="SYNTHETIC_OTHER_NETWORK"))
    reject("changed_worker", lambda x: x["objects"]["worker"][0].update(ID="SYNTHETIC_OTHER_WORKER"))
    reject("wrong_worker_platform", lambda x: x["objects"]["worker"][0].update(PLATFORMS=["linux/arm64"]))
    reject("changed_proxy_source", lambda x: x.update(proxy_source=x["proxy_source"] + "\n# mutation\n"))
    reject("changed_proxy_policy", lambda x: x.update(policy_raw=p.pretty({"SYNTHETIC_POLICY": "MUTATED"}).decode()))
    changed_enforcement = copy.deepcopy(expected)
    changed_enforcement["enforcement_identity"] = "0" * 64
    reject("altered_network_enforcement_observation", call=lambda x: seam.observe_fixture(x, changed_enforcement))
    reject("missing_manifest_digest", lambda x: x["identities"]["daemon"]["selected"]["Descriptor"].pop("digest"))
    reject("missing_config_bytes", lambda x: x["identities"]["proxy"].update(config_raw=""))
    reject("daemon_stopped", lambda x: x["objects"]["daemon"]["State"].update(Running=False))
    reject("proxy_stopped", lambda x: x["objects"]["proxy"]["State"].update(Running=False))
    reject("daemon_DNS_drift", lambda x: x["objects"]["daemon"]["HostConfig"].update(Dns=["8.8.8.8"]))
    reject("daemon_binary_drift", lambda x: x["objects"]["daemon"].update(daemon_binary_sha256="0" * 64))
    reject("proxy_argv_drift", lambda x: x["objects"]["proxy"].update(Args=["WRONG"]))
    reject("candidate_real_Authority_firewall", call=lambda x: p.Authority())
    reject("candidate_synthetic_Authority_firewall", call=lambda x: p.Authority.synthetic(root / "baseline_fixture.json"))
    reject("helper_cannot_assert_production_authority", lambda x: x.update(runtime_authority=True))
    prior = p.exact_json(HERE.parent / "v6_preparation_execution_production_runtime_installation_resume_v1" / "rejection_matrix.json")
    coverage = {"wrong_topology_fields": "changed_worker", "stale_topology_preclaim": "stale_topology_preclaim_pure_observation"}
    not_run = {
        "full_corrected_controller_provider_A_through_X": "NOT_RUN: exact original Authority.synthetic source-location guard rejects this new candidate path. No source guard patch, rebinding, object.__new__, monkeypatch or installed controller invocation was used.",
        "original_preclaim_ledger_E2E": "NOT_RUN: original fixture/source/root firewall retained exactly; pure fresh normalization/equality rejection exercised instead.",
        "receipt_stale_enforcement": "NOT_RUN: receipt logic AST preserved; no receipt authority instantiated.",
        "stale_topology_sha": "NOT_RUN: receipt serialization/hash rejection AST preserved; no receipt issued.",
        "wrong_enforcement_identity": "NOT_RUN: Authority.refresh acceptance gate AST unchanged; altered observation enforcement rejected at pure comparison.",
    }
    write(HERE / "synthetic_qualification_results.json", {
        "schema": "V6_IMAGE_IDENTITY_BRIDGE_PURE_QUALIFICATION_V1", "status": "PASS_AFFECTED_PURE_SCOPE",
        "candidate_provider_sha256": p.a.sha(Path(p.__file__).read_bytes()),
        "qualification_code_sha256": p.a.sha(Path(__file__).read_bytes()),
        "pure_seam_sha256": p.a.sha(Path(seam.__file__).read_bytes()),
        "namespace": seam.NAMESPACE, "qualification_root": str(root), "tests": results,
        "rejection_count": len(rejections), "full_A_through_X_claimed": False, "NOT_RUN": not_run,
        "previous_affected_checks": {name: {"previous_status": prior["checks"][name]["status"],
                                          "corrected_pure_check": check, "status": rejections[check]["status"]}
                                     for name, check in coverage.items()},
        "Docker_used": False, "public_network_used": False, "real_receipts": 0, "real_claims": 0,
        "real_terminals": 0, "scientific_validation_claimed": False})
    write(HERE / "rejection_matrix.json", {"schema": "V6_IMAGE_IDENTITY_BRIDGE_REJECTIONS_V1", "checks": rejections,
                                           "status": "PASS_REJECTED", "count": len(rejections), "NOT_RUN": not_run})
    print(json.dumps({"positive_checks": len(results), "rejections": len(rejections), "status": "PASS_AFFECTED_PURE_SCOPE"}))


if __name__ == "__main__":
    main()

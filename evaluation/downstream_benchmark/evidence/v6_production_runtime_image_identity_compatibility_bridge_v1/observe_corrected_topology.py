"""Read-only collector for the candidate's actual image verifier and topology normalizer.

No Authority is constructed. Authority.observe and full production E2E remain NOT_RUN.
The read argv/order follows the preserved accepted observer; it invokes no solve.
"""
from __future__ import annotations

import datetime
import json
import subprocess
import sys
from pathlib import Path

from . import corrected_production_provider_candidate as p

HERE = Path(__file__).resolve().parent
PROVISION = p.a.OUTPUT_ROOT / "qualification/production_runtime_topology_provisioning_v1"
EXPECTED_SHA = "3a9166d306fee282279702312d6e170cad6f3a1f60b8ce70bb6e3e579af746ea"


def differences(left, right, path=""):
    if type(left) is not type(right):
        return [{"field": path, "expected": left, "observed": right}]
    if isinstance(left, dict):
        result = []
        for key in sorted(set(left) | set(right)):
            name = path + "/" + key
            if key not in left or key not in right:
                result.append({"field": name, "expected": left.get(key), "observed": right.get(key)})
            else:
                result.extend(differences(left[key], right[key], name))
        return result
    if left != right:
        return [{"field": path, "expected": left, "observed": right}]
    return []


def main():
    raw_relative = "live_observation/" + (sys.argv[1] if len(sys.argv) == 2 else "run_2") + "/raw"
    raw_root = HERE / raw_relative
    raw_root.mkdir(parents=True, exist_ok=False)
    commands = []

    def run(argv):
        allowed = (argv[:2] == ["docker", "inspect"] or argv[:3] in
                   (["docker", "image", "inspect"], ["docker", "network", "inspect"]))
        if argv[:2] == ["docker", "exec"]:
            tail = argv[3:]
            allowed = (tail[:1] == ["/usr/bin/buildctl"] and tail[-2:] == ["debug", "workers"]
                       or tail[:1] == ["sha256sum"] and tail[1:] in (["/usr/bin/buildctl"], ["/usr/bin/buildkitd"])
                       or tail[:1] == ["cat"] and tail[1:] in
                       (["/proc/net/route"], ["/proc/net/unix"], ["/qualification_proxy.py"]))
        p.a.require(allowed, "collector command outside read-only allowlist")
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        result = subprocess.run(argv, capture_output=True, check=False, timeout=30)
        stem = f"{len(commands) + 1:03d}"
        for extension, raw in (("stdout", result.stdout), ("stderr", result.stderr)):
            (raw_root / (stem + "." + extension)).write_bytes(raw)
        commands.append({"argv": argv, "started_at": started, "returncode": result.returncode,
                         "stdout_path": raw_relative + "/" + stem + ".stdout", "stdout_sha256": p.a.sha(result.stdout),
                         "stderr_path": raw_relative + "/" + stem + ".stderr", "stderr_sha256": p.a.sha(result.stderr)})
        (HERE / "fresh_live_commands.json").write_bytes(p.pretty(commands))
        p.a.require(result.returncode == 0, "live topology observation unavailable")
        return result.stdout

    config = p.frozen_inputs()
    expected_raw = (PROVISION / "live_topology_observation.json").read_bytes()
    p.a.require(p.a.sha(expected_raw) == EXPECTED_SHA, "provisioned topology bytes drift")
    expected = p.a.loads(expected_raw)
    daemon = p.a.loads(run(["docker", "inspect", "buildx_buildkit_" + config["builder_name"] + "0"]))[0]
    proxy = p.a.loads(run(["docker", "inspect", config["proxy"]["proxy_name"]]))[0]
    p.a.require(daemon["Id"] == expected["daemon_instance_identity"]["container_id"]
                and proxy["Id"] == expected["proxy_instance_identity"]["container_id"],
                "LIVE_TOPOLOGY_DRIFT: provisioned instance identity changed")
    cid, pid = daemon["Id"], proxy["Id"]
    worker = p.parse_workers(run(["docker", "exec", cid, "/usr/bin/buildctl", "--addr=" + config["endpoint"],
                                  "debug", "workers"]))
    network = p.a.loads(run(["docker", "network", "inspect", config["internal_network"]]))[0]
    for key, binary in (("native_binary_sha256", "/usr/bin/buildctl"), ("daemon_binary_sha256", "/usr/bin/buildkitd")):
        daemon[key] = run(["docker", "exec", cid, "sha256sum", binary]).decode().split()[0]
    daemon["routes"] = run(["docker", "exec", cid, "cat", "/proc/net/route"]).decode()
    daemon["sockets"] = run(["docker", "exec", cid, "cat", "/proc/net/unix"]).decode()
    daemon["image_config_digest"] = p.observe_image_config(daemon, config, "daemon", run)
    proxy["image_config_digest"] = p.observe_image_config(proxy, config, "proxy", run)
    code = run(["docker", "exec", pid, "cat", "/qualification_proxy.py"])
    policy = p.pretty(config["proxy"]["policy"])
    objects = {"daemon": daemon, "proxy": proxy, "worker": worker, "network": network}
    (HERE / "fresh_live_raw_objects.json").write_bytes(p.pretty(objects))
    observed = p.normalize_topology(objects, code, policy, config)
    raw = p.a.canonical(observed)
    (HERE / "corrected_topology_observation.json").write_bytes(raw)
    contract = p.exact_json(p.a.ROOT / p.RESUME / "topology_observation_contract.json")
    delta = differences(expected, observed)
    comparison = {"schema": "V6_IMAGE_IDENTITY_BRIDGE_TOPOLOGY_COMPARISON_V1",
                  "corrected_provider_sha256": p.a.sha(Path(p.__file__).read_bytes()),
                  "status": "PASS_EXACT" if raw == expected_raw else "BLOCKED",
                  "reason": None if raw == expected_raw else "LIVE_TOPOLOGY_DRIFT",
                  "expected_sha256": EXPECTED_SHA, "observed_sha256": p.a.sha(raw),
                  "canonical_bytes_equal": raw == expected_raw,
                  "same_schema": observed["schema"] == contract["observation_schema"],
                  "same_field_names": set(observed) == set(contract["required_fields"]),
                  "differences": delta, "artificial_expected_hash_construction": False,
                  "actual_candidate_functions": ["observe_image_config", "verify_image_identity", "parse_workers", "normalize_topology"],
                  "Authority_observe_E2E": "NOT_RUN: source-location firewall retained; no Authority constructed"}
    (HERE / "topology_comparison.json").write_bytes(p.pretty(comparison))
    print(json.dumps({k: v for k, v in comparison.items() if k != "differences"}))
    print(json.dumps(delta))


if __name__ == "__main__":
    main()

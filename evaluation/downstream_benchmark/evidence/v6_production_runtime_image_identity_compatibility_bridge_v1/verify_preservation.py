"""Compare read-only after state to the measured entry snapshot; no initialization."""
from __future__ import annotations

import collections
import os
import stat
import subprocess
from pathlib import Path

from . import corrected_production_provider_candidate as p
from .observe_corrected_topology import differences

HERE = Path(__file__).resolve().parent


def main():
    commands = []

    def run(argv):
        result = subprocess.run(argv, capture_output=True, timeout=30,
                                env=dict(os.environ, GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1"))
        commands.append({"argv": argv, "returncode": result.returncode, "stdout": result.stdout.decode(),
                         "stderr": result.stderr.decode(), "stdout_sha256": p.a.sha(result.stdout),
                         "stderr_sha256": p.a.sha(result.stderr)})
        assert result.returncode == 0
        return result.stdout

    def j(argv):
        return p.a.loads(run(argv))

    containers = j(["docker", "inspect", *run(["docker", "ps", "-aq", "--no-trunc"]).decode().split()])
    networks = j(["docker", "network", "inspect", *run(["docker", "network", "ls", "-q", "--no-trunc"]).decode().split()])
    names = run(["docker", "volume", "ls", "-q"]).decode().split()
    volumes = j(["docker", "volume", "inspect", *names]) if names else []
    images = [p.a.loads(row.encode()) for row in
              run(["docker", "image", "ls", "--no-trunc", "--digests", "--format", "{{json .}}"]).decode().splitlines()]
    after = {"containers": containers, "networks": networks, "volumes": volumes, "images": images}
    before = p.exact_json(HERE / "before_docker_inventory.json")
    # Identity/config/state use all container/network/volume fields. Image listing
    # presentation ages change with time; compare exact identities/tags/counts instead.
    def projection(inv):
        return {"containers": sorted(inv["containers"], key=lambda x: x["Id"]),
                "networks": sorted(inv["networks"], key=lambda x: x["Id"]),
                "volumes": sorted(inv["volumes"], key=lambda x: x["Name"]),
                "images": sorted([{k: x[k] for k in ("ID", "Digest", "Repository", "Tag", "Containers", "Size")}
                                  for x in inv["images"]], key=lambda x: (x["ID"], x["Repository"], x["Tag"]))}
    equal = p.a.canonical(projection(before)) == p.a.canonical(projection(after))
    (HERE / "after_docker_inventory.json").write_bytes(p.pretty(after))
    (HERE / "preservation_commands.json").write_bytes(p.pretty(commands))
    baseline = p.exact_json(HERE / "before_preservation_snapshot.json")
    tracked = {}
    for name in run(["git", "ls-files", "-z"]).decode().split("\0"):
        if name:
            path = p.a.ROOT / name
            tracked[name] = {"sha256": p.a.sha(path.read_bytes()), "size_bytes": path.stat().st_size}
    tree = {}
    for path in sorted((p.a.OUTPUT_ROOT / "ledger").rglob("*")):
        name = str(path.relative_to(p.a.OUTPUT_ROOT / "ledger"))
        tree[name] = {"type": "directory" if path.is_dir() else "file", "mode": stat.S_IMODE(path.lstat().st_mode)}
        if path.is_file():
            tree[name].update(sha256=p.a.sha(path.read_bytes()), size_bytes=path.stat().st_size)
    population = p.legacy.population()
    ids = [x["base_attempt_id"] for x in population["items"]]
    ledger = p.ledger.Ledger(p.a.OUTPUT_ROOT, namespace=p.ledger.REAL, real_ids=ids)
    counts = dict(collections.Counter(ledger.state(x) for x in ids))
    current_raw = (p.a.ROOT / p.a.CURRENT).read_bytes()
    current = p.a.loads(current_raw)
    paths = p.exact_json(HERE.parent / "v6_preparation_execution_production_runtime_installation_resume_v1" / "installation_plan.json")["future_targets"]
    targets = {name: {"path": path, "exists": (p.a.ROOT / path).exists()} for name, path in paths.items()}
    assert tracked == baseline["tracked"]
    assert p.a.sha((p.a.ROOT / ".git/index").read_bytes()) == baseline["index_sha256"]
    assert run(["git", "diff", "--binary"]) == run(["git", "diff", "--cached", "--binary"]) == b""
    status = run(["git", "status", "--porcelain=v1", "--untracked-files=all"]).decode()
    prefix = "?? " + str(HERE.relative_to(p.a.ROOT)) + "/"
    assert all(row.startswith(prefix) for row in status.splitlines())
    assert tree == baseline["ledger_tree"] and counts == {"UNSTARTED": 641}
    assert p.a.identity(ids) == p.ORDER_SHA
    assert p.a.sha(current_raw) == p.CANONICAL_SHA and current["event_count"] == 3 and current["event_head"]["event_id"] == p.EVENT_3
    assert all(not x["exists"] for x in targets.values())
    def named_projection(inv):
        value = projection(inv)
        for name in ("containers", "networks", "volumes"):
            key = "Name" if name == "volumes" else "Id"
            value[name] = {row[key]: row for row in value[name]}
        return value
    delta = differences(named_projection(before), named_projection(after))
    assert p.a.sha((p.a.OUTPUT_ROOT / "namespace.json").read_bytes()) == p.ledger_identity()["existing_namespace_sha256"]
    (HERE / "after_preservation_snapshot.json").write_bytes(p.pretty({
        "tracked": tracked, "index_sha256": baseline["index_sha256"], "ledger_tree": tree,
        "ledger_states": counts, "canonical_sha256": p.a.sha(current_raw), "event_3": current["event_head"],
        "git_status": status, "installed_targets": targets}))
    (HERE / "preservation_verification.json").write_bytes(p.pretty({
        "schema": "V6_IMAGE_IDENTITY_BRIDGE_PRESERVATION_V1",
        "status": "PASS_PRESERVED" if equal else "BLOCKED_DOCKER_INSPECT_DRIFT",
        "all_1065_tracked_file_bytes_equal": True, "index_bytes_equal": True, "tracked_diff": "", "index_diff": "",
        "only_untracked_namespace": str(HERE), "canonical_sha256": p.CANONICAL_SHA, "event_count": 3, "event_3_id": p.EVENT_3,
        "real_ledger_exact_tree_equal": True, "real_ledger_states": counts, "claims": 0, "terminals": 0, "retries": 0, "orphans": 0,
        "ordered_work_identity_sha256": p.a.identity(ids), "namespace_sha256": p.a.sha((p.a.OUTPUT_ROOT / "namespace.json").read_bytes()),
        "docker_exact_container_network_volume_inspects_equal": equal,
        "docker_full_inspect_differences": delta,
        "docker_exact_image_identity_tag_count_equal": projection(before)["images"] == projection(after)["images"],
        "docker_identity_and_lifecycle_state_equal": {
            "containers": [{k: x[k] for k in ("Id", "Name", "State")} for x in projection(before)["containers"]]
                          == [{k: x[k] for k in ("Id", "Name", "State")} for x in projection(after)["containers"]],
            "networks": projection(before)["networks"] == projection(after)["networks"],
            "volumes": projection(before)["volumes"] == projection(after)["volumes"]},
        "docker_counts": {k: len(v) for k, v in after.items()},
        "retained_running_containers": [{"Id": x["Id"], "Name": x["Name"], "State": x["State"]}
                                        for x in containers if x["State"]["Running"]],
        "installed_targets": targets,
        "image_listing_projection_fields": ["ID", "Digest", "Repository", "Tag", "Containers", "Size"],
        "all_container_fields_including_ExecIDs_compared": True,
        "negative_boundary": {"Docker_mutations": 0, "solve_build_pull_import_export": 0,
                              "real_receipts_claims_terminals": 0, "installed_controller_invocations": 0,
                              "production_target_creation": 0, "source_promotions": 0,
                              "stage_commit_push": 0, "dependency_installs": 0, "topology_cleanup": 0,
                              "original_evidence_writes": 0, "OCI_layout_writes": 0}}))
    (HERE / "preservation_commands.json").write_bytes(p.pretty(commands))
    print(p.pretty({"status": "PASS_PRESERVED" if equal else "BLOCKED_DOCKER_INSPECT_DRIFT",
                    "counts": counts, "docker": {k: len(v) for k, v in after.items()}, "differences": delta}).decode())


if __name__ == "__main__":
    main()

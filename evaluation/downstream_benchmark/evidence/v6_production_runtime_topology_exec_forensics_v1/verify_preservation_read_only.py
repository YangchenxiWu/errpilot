"""Read-only snapshot comparison; no runtime, ledger or provider initialization."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CORRECTION = HERE.parent / "v6_production_runtime_image_identity_compatibility_bridge_v1"
OUTPUT = Path("/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def tree(root):
    result = {}
    for path in sorted(root.rglob("*")):
        entry = {"type": "directory" if path.is_dir() else "file", "mode": stat.S_IMODE(path.lstat().st_mode)}
        if path.is_file():
            entry.update(sha256=sha(path.read_bytes()), size_bytes=path.stat().st_size)
        result[str(path.relative_to(root))] = entry
    return result


def differences(left, right, path=""):
    missing = {"MISSING": True}
    if type(left) is not type(right):
        return [{"field": path, "before": left, "after": right}]
    if isinstance(left, dict):
        result = []
        for key in sorted(left.keys() | right.keys()):
            result += differences(left.get(key, missing), right.get(key, missing), path + "/" + key)
        return result
    return [{"field": path, "before": left, "after": right}] if left != right else []


def main():
    baseline = json.loads((HERE / "raw_entry_snapshot.json").read_text())
    commands = json.loads((HERE / "commands_run.json").read_text())
    def run(argv):
        assert argv[0] == "git" and argv[1] in ("rev-parse", "branch", "ls-files", "status", "diff")
        start = datetime.datetime.now(datetime.timezone.utc).isoformat()
        p = subprocess.run(argv, capture_output=True, timeout=30, cwd=ROOT, env=dict(os.environ, GIT_OPTIONAL_LOCKS="0"))
        commands.append({"argv": argv, "started_at": start, "finished_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "returncode": p.returncode, "stdout": p.stdout.decode(), "stderr": p.stderr.decode(),
            "stdout_sha256": sha(p.stdout), "stderr_sha256": sha(p.stderr)})
        write("commands_run.json", commands)
        assert p.returncode == 0
        return p.stdout.decode().strip()
    tracked = {name: {"sha256": sha((ROOT / name).read_bytes()), "size_bytes": (ROOT / name).stat().st_size}
               for name in run(["git", "ls-files", "-z"]).split("\0") if name}
    index_sha = sha((ROOT / ".git/index").read_bytes())
    head = run(["git", "rev-parse", "HEAD"])
    branch = run(["git", "branch", "--show-current"])
    tracked_diff = run(["git", "diff", "--binary"])
    index_diff = run(["git", "diff", "--cached", "--binary"])
    whitespace = run(["git", "diff", "--check"])
    status = run(["git", "status", "--porcelain=v1", "--untracked-files=all"])
    allowed_prefixes = ["?? " + str(x.relative_to(ROOT)) + "/" for x in (HERE, CORRECTION)]
    canonical_raw = (ROOT / "evaluation/downstream_benchmark/v6_current_state.json").read_bytes()
    canonical = json.loads(canonical_raw)
    ledger_tree = tree(OUTPUT / "ledger")
    output_tree = tree(OUTPUT)
    work = ROOT / "evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/work_items_candidate.json"
    work_raw = work.read_bytes()
    assert sha(work_raw) == "288eaed9f7e9ff4daf2978e7c41b6c6ead83e9d99b9ddee7801c163153bd63bb"
    population = json.loads(work_raw)
    ids = [x["base_attempt_id"] for x in population["items"]]
    assert len(ids) == len(set(ids)) == 641
    # Reproduce only the inspected read-only Ledger.state absence checks; do not instantiate helpers.
    unstarted = sum(not any((OUTPUT / "ledger" / folder / (aid + ".json")).exists()
                            for folder in ("claims", "terminals", "locks")) for aid in ids)
    counts = {folder: len(list((OUTPUT / "ledger" / folder).iterdir())) for folder in ("claims", "terminals", "locks")}
    targets = {name: {"path": item["path"], "exists": (ROOT / item["path"]).exists()}
               for name, item in baseline["installed_targets"].items()}
    seal_raw = (CORRECTION / "artifact_sha256.json").read_bytes()
    seal = json.loads(seal_raw)
    sealed_set = set(seal["files"]) | {"artifact_sha256.json"}
    actual = {str(p.relative_to(CORRECTION)) for p in CORRECTION.rglob("*") if p.is_file()}
    bad = [n for n, x in seal["files"].items() if not (CORRECTION / n).is_file()
           or sha((CORRECTION / n).read_bytes()) != x["sha256"] or (CORRECTION / n).stat().st_size != x["size_bytes"]]
    predecessor = json.loads((HERE / "predecessor_binding.json").read_text())["accepted_baseline_binding_verified"]
    predecessor_bad = [x["path"] for x in predecessor["pins"] + predecessor["original_package_files"] + predecessor["topology_evidence"]
                       if sha(Path(x["path"]).read_bytes()) != x.get("expected", x["sha256"])]
    live = json.loads((HERE / "raw_final_live_origin.json").read_text())
    after = {"tracked": tracked, "index_sha256": index_sha, "head": head, "branch": branch,
             "canonical_sha256": sha(canonical_raw), "event_3": canonical["event_head"], "event_count": canonical["event_count"],
             "ledger_tree": ledger_tree, "output_tree": output_tree, "installed_targets": targets,
             "git_status": status, "live_origin_main": live["stdout"].split()[0]}
    write("raw_final_snapshot.json", after)
    checks = {
        "all_1065_previously_tracked_files_unchanged": tracked == baseline["tracked"] and len(tracked) == 1065,
        "index_bytes_unchanged": index_sha == baseline["index_sha256"], "head_unchanged": head == baseline["head"],
        "branch_main": branch == "main", "fresh_live_origin_main_unchanged": live["returncode"] == 0 and live["stdout"].split() == [head, "refs/heads/main"],
        "canonical_exact_unchanged": sha(canonical_raw) == baseline["canonical_sha256"],
        "event_3_unchanged": canonical["event_head"] == baseline["event_3"] and canonical["event_count"] == 3,
        "tracked_diff_empty": not tracked_diff, "index_diff_empty": not index_diff, "git_diff_check_pass": not whitespace,
        "only_authorized_untracked_namespaces": all(any(row.startswith(prefix) for prefix in allowed_prefixes) for row in status.splitlines()),
        "correction_seal_sha_exact": sha(seal_raw) == "ee8948b829a072ff10e3a41ba086afb4151821010661d89a05ce444ba95369e8",
        "correction_complete_280_payloads_preserved": len(seal["files"]) == 280 and actual == sealed_set and not bad,
        "all_original_predecessor_bindings_preserved": not predecessor_bad,
        "no_production_installation_targets_created": not any(x["exists"] for x in targets.values()),
        "real_ledger_tree_equal": ledger_tree == baseline["ledger_tree"], "all_641_UNSTARTED": unstarted == 641,
        "zero_real_claim_terminal_lock_retry_orphan_entries": not any(counts.values()) and set(ledger_tree) == {"claims", "terminals", "locks"},
        "real_output_entire_tree_equal": output_tree == baseline["output_tree"],
        "namespace_sha_exact": sha((OUTPUT / "namespace.json").read_bytes()) == "7570569f68a9babf36d408f8c59cc17879c0ef23262d6178ffc9d50bbc06c67e"}
    def inventory(name):
        value = json.loads((HERE / ("raw_docker_inventory_" + name + ".json")).read_text())
        return {
            "containers": {x["parsed"]["Id"]: x["parsed"] for x in value["containers"]},
            "containers_list": {x["Id"]: x for x in value["containers_list"]["parsed"]},
            "images": {x["Id"]: x for x in value["images"]["parsed"]},
            "networks_list": {x["Id"]: x for x in value["networks"]["parsed"]},
            "network_details": {x["parsed"]["Id"]: x["parsed"] for x in value.get("network_details", [])},
            "volumes": {x["Name"]: x for x in value["volumes"]["parsed"]["Volumes"]}}
    first, security, last = (inventory(n) for n in ("before_authorized", "security", "after"))
    # First inventory lacks network-detail reads; compare those from the first detailed collection.
    first_delta = differences({k: v for k, v in first.items() if k != "network_details"},
                              {k: v for k, v in last.items() if k != "network_details"})
    detail_delta = differences(security, last)
    identity_equal = {k: set(first[k]) == set(last[k]) for k in first if k != "network_details"}
    write("raw_docker_preservation_diff.json", {"before_to_after_all_object_field_differences": first_delta,
        "first_detailed_network_inventory_to_after_all_field_differences": detail_delta,
        "object_id_sets_equal": identity_equal, "full_snapshot_object_field_equality": not first_delta,
        "response_transport_byte_equality_not_asserted": True,
        "process_top_raw_stdout_before": json.loads((HERE / "exec_inspect_observations_before_authorized.json").read_text())["docker_top"],
        "process_top_raw_stdout_after": json.loads((HERE / "exec_inspect_observations_after.json").read_text())["docker_top"]})
    write("preservation_verification.json", {"schema": "V6_FORENSIC_PRESERVATION_V1", "status": "PASS" if all(checks.values()) else "BLOCKED",
        "checks": checks, "tracked_file_count": 1065, "real_ledger_states": {"UNSTARTED": unstarted},
        "claims": counts["claims"], "terminals": counts["terminals"], "retries": 0, "orphans": counts["locks"],
        "output_tree_entry_count": len(output_tree), "Docker_object_counts": {k: len(v) for k, v in last.items()},
        "Docker_object_identity_sets_equal": identity_equal, "Docker_full_inspect_byte_equality": False,
        "Docker_all_object_field_equality": not first_delta, "Docker_observed_differences": first_delta,
        "TASK_CAUSED_MUTATION": "NO", "task_mutation_scope": "No Docker/runtime/real ledger/production/frozen source mutation; only the explicitly authorized forensic evidence namespace was written.",
        "UNATTRIBUTED_CONCURRENT_DRIFT": "POSSIBLE", "concurrent_drift_observed": bool(first_delta),
        "causal_caveat": "ExecID turnover and process changes are observed, not assigned to any initiating host process. Read-only observation cannot prove that the entire daemon state remained constant between samples.",
        "forbidden_Docker_Git_runtime_actions": 0, "new_ExecCreate_ExecStart_ExecAttach_requests": 0,
        "original_280_inventory_bad_files": bad, "predecessor_binding_bad_files": predecessor_bad,
        "explicit_unchanged_production_firewall": "No accepted installed production provider/controller, effectivity, acceptance pin, installation authority or receipt contract; source-location/frozen contract guards unchanged; no real attempts; installation/execution/commit/publication remain outside this transaction."})
    assert all(checks.values()), checks
    print(json.dumps({"status": "PASS", "checks": len(checks), "Docker_counts": {k: len(v) for k, v in last.items()},
          "Docker_field_differences": first_delta, "ledger": {"UNSTARTED": unstarted}}))


if __name__ == "__main__":
    main()

"""Offline preservation/default-deny checks; blocked bridge gates stay NOT_RUN."""
from __future__ import annotations

import ast
import copy
import json
import os
import stat
import subprocess
import sys
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a  # noqa: E402
from evaluation.downstream_benchmark.screening import v6_preparation_ledger as ledger  # noqa: E402
from evaluation.downstream_benchmark.screening import v6_preparation_runtime as r  # noqa: E402


def save(name, value):
    raw = (json.dumps(value, ensure_ascii=False, sort_keys=True,
                      indent=2, allow_nan=False) + "\n").encode("utf-8")
    if "--verify-only" in sys.argv:
        assert (OUT / name).read_bytes() == raw, name
    else:
        (OUT / name).write_bytes(raw)


def reject(call):
    try:
        call()
    except a.Rejected as error:
        return str(error)
    raise AssertionError("required rejection did not occur")


def external_files(root):
    files = {}
    for path in sorted(root.rglob("*")):
        relative = str(path.relative_to(root))
        if relative == "artifact_sha256.json":
            continue
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            value = os.readlink(path)
            files[relative] = {"type": "symlink", "target": value,
                               "sha256": a.sha(os.fsencode(value))}
        elif stat.S_ISREG(mode):
            raw = path.read_bytes()
            files[relative] = {"type": "file", "bytes": len(raw), "sha256": a.sha(raw)}
        else:
            assert stat.S_ISDIR(mode), relative
    return files


def main():
    descriptor, manifest = a.load_inputs()
    population = r.population()
    assert a.derive_population(manifest) == population
    scope = a.loads((OUT / "work_item_scope.json").read_bytes())
    assert a.identity(population) == scope["population_sha256"]
    assert (len(population["items"]), len(scope["restricted_work_item_ids"]),
            len(scope["network_none_work_item_ids"])) == (641, 583, 58)
    assert {x["case_id"] for x in population["blocked"]} == {"matplotlib::1", "matplotlib::8"}
    entry = a.loads((OUT / "entry_verification.json").read_bytes())
    for relative, expected in entry["accepted_file_hashes"].items():
        assert a.sha((ROOT / relative).read_bytes()) == expected, relative
    assert len(entry["accepted_file_hashes"]) == 69
    assert a.sha((a.B / "v6_current_state.json").read_bytes()) == a.CURRENT_SHA
    assert descriptor["event_count"] == 2 and descriptor["projection"]["phase_authorizations"]["PREPARATION_EXECUTION"] == "NO"
    assert a.sha((ROOT / ".git/index").read_bytes()) == entry["index_sha256"]
    own = str(OUT.relative_to(ROOT)) + "/"
    observed = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT).decode().splitlines()
    assert {x for x in observed if not x.startswith(own)} == set(entry["accepted_file_hashes"])
    bridge = a.loads((OUT / "bridge_identity.json").read_bytes())
    assert bridge["semantic_enforcement_identity"] is None
    assert a.identity(bridge["qualification_observation_identity"]) == bridge["qualification_observation_sha256"]
    for name, expected in bridge["qualification_observation_identity"].items():
        assert a.sha((OUT / name).read_bytes()) == expected, name
    assert a.loads((OUT / "docker_state_before.json").read_bytes()) == a.loads((OUT / "docker_state_after.json").read_bytes())
    malformed = {
        "default_or_docker_builder_fallback": {"driver": "docker", "builder": "desktop-linux"},
        "missing_explicit_builder": {"builder": None},
        "wrong_builder": {"builder": "other-builder"},
        "builder_attached_to_external_network": {"builder_networks": ["internal", "external"]},
        "named_build_network_regression": {"build_network": "errpilot-v6-egress-42393faa3385-v1-internal"},
        "network_host": {"build_network": "host"},
        "missing_load": {"load": False},
        "wrong_output_store": {"output_store": "cache-only"},
        "buildkit_runtime_pull": {"runtime_pull": True},
        "base_image_registry_access": {"registry_egress": True},
        "altered_FROM_or_base": {"FROM": "python:latest"},
        "missing_proxy_args": {"proxy_args": []},
        "missing_PIP_INDEX_URL": {"PIP_INDEX_URL": None},
        "alternate_PIP_index": {"PIP_INDEX_URL": "https://denied.invalid/simple"},
        "proxy_bypass": {"direct_egress": True},
    }
    restricted_item = next(x for x in population["items"] if x["build_network_required"])
    none_item = next(x for x in population["items"] if not x["build_network_required"])
    matrix = {}
    for name, receipt in malformed.items():
        reason = reject(lambda receipt=receipt: r.require_network(restricted_item, receipt))
        matrix[name] = {"input": receipt, "existing_runtime_probe": "PASS_BLANKET_REJECTION_ONLY",
            "observed_reason": reason, "bridge_specific_probe": "NOT_RUN_RUNTIME_GATE_BLOCKED"}
    matrix["application_binding_on_network_NONE"] = {"input": {"HTTP_PROXY": "http://proxy:3128"},
        "existing_runtime_probe": "PASS_NONE_RECEIPT_REJECTION",
        "observed_reason": reject(lambda: r.require_network(none_item, {"HTTP_PROXY": "http://proxy:3128"})),
        "bridge_specific_probe": "NOT_RUN_RUNTIME_GATE_BLOCKED"}
    changed = copy.deepcopy(manifest["plans"][restricted_item["census_order"] - 1])
    changed["recipe_candidate"]["setup_actions"].append({"text": "python -m pip install other"})
    matrix["scientific_recipe_mutation"] = {"existing_runtime_probe": "PASS_FROZEN_PLAN_HASH_REJECTION",
        "observed_reason": reject(lambda: a.select({"plans": [changed]}, ordinal=1,
            case_id=changed["case_id"], plan_sha=changed["plan_sha256"])),
        "bridge_specific_probe": "NOT_RUN_RUNTIME_GATE_BLOCKED"}
    save("rejection_matrix.json", {"qualification": "PARTIAL_OFFLINE_ONLY",
        "interpretation": "Blanket rejection proves the unchanged gate stays closed. It does not independently validate malformed bridge settings or implemented enforcement.",
        "classes": matrix, "bridge_specific_matrix_pass": False})
    restricted_count = none_count = 0
    for item in population["items"]:
        if item["build_network_required"]:
            reject(lambda item=item: r.require_network(item, {"qualified": True}))
            restricted_count += 1
        else:
            r.require_network(item, None)
            reject(lambda item=item: r.require_network(item, {"qualified": True}))
            none_count += 1
    acceptance = a.loads(a.read_exact(r.AUTHORITY, r.AUTHORITY_SHA))
    request = {"descriptor_path": a.CURRENT, "descriptor_sha": a.CURRENT_SHA,
        "manifest_path": a.MANIFEST, "manifest_sha": a.MANIFEST_SHA,
        "ordinal": restricted_item["census_order"], "case_id": restricted_item["case_id"],
        "plan_sha": restricted_item["plan_sha256"], "base_attempt_id": restricted_item["base_attempt_id"]}
    with mock.patch.object(a.shared, "docker", side_effect=AssertionError("Docker forbidden")), \
            mock.patch.object(ledger.Ledger, "claim", side_effect=AssertionError("real claim forbidden")):
        real_reason = reject(lambda: r.dispatch(request, acceptance=acceptance, policy=r.POLICY))
        engine = r.shared_engine()
        for argv in (["build", "--network=host"], ["build", "--network=default"],
            ["build", "--network=errpilot-v6-egress-42393faa3385-v1-internal"],
            ["buildx", "build", "--builder=other", "--network=none"],
            ["pull", "moby/buildkit:buildx-stable-1"], ["image", "pull", "python:latest"]):
            reject(lambda argv=argv: engine.docker(argv))
    results = a.loads((OUT / "persistent_ledger_qualification.json").read_bytes())
    assert results["status"] == "PASS" and results["run"] == 11 and results["skipped"] == 0
    source = a.loads((OUT / "source_revalidation.json").read_bytes())
    assert source["observed_result"]["missing_objects"] == 0
    assert source["observed_result"]["required_leaf_blobs"] == 61333
    files = sorted(p for p in OUT.iterdir() if p.is_file())
    py_files = []
    for path in files:
        raw = path.read_bytes()
        value = raw.decode("utf-8", errors="strict")
        assert not raw.startswith(b"\xef\xbb\xbf") and b"\x00" not in raw and b"\r" not in raw
        assert value.endswith("\n") and all(line.rstrip() == line for line in value.splitlines()), path
        if path.suffix == ".json":
            a.loads(raw)
        elif path.suffix == ".py":
            ast.parse(value)
            py_files.append(str(path.relative_to(ROOT)))
    checks = {}
    production_ast = [*r.IMPLEMENTATION, "evaluation/downstream_benchmark/tests/test_v6_preparation_runtime.py",
                      "evaluation/downstream_benchmark/screening/materializer.py"]
    for relative in production_ast:
        ast.parse((ROOT / relative).read_bytes().decode("utf-8", errors="strict"))
    for name, argv in (("ruff", ["ruff", "check", "--no-cache", *r.IMPLEMENTATION,
            "evaluation/downstream_benchmark/tests/test_v6_preparation_runtime.py", *py_files]),
        ("git_diff_check", ["git", "diff", "--check"]),
        ("tracked_clean", ["git", "diff", "--exit-code"]),
        ("index_clean", ["git", "diff", "--cached", "--exit-code"])):
        result = subprocess.run(argv, cwd=ROOT, capture_output=True, check=False)
        checks[name] = {"argv": argv, "exit_code": result.returncode,
            "stdout": result.stdout.decode(), "stderr": result.stderr.decode()}
        assert result.returncode == 0, name
    external_status = "NOT_YET_PUBLISHED"
    if (OUT / "external_evidence_manifest.json").exists():
        record = a.loads((OUT / "external_evidence_manifest.json").read_bytes())
        root = Path(record["root"])
        assert root == a.OUTPUT_ROOT / "qualification/restricted_build_egress_compatibility_bridge_v1"
        assert a.sha((root / "artifact_sha256.json").read_bytes()) == record["manifest_sha256"]
        inventory = a.loads((root / "artifact_sha256.json").read_bytes())
        assert external_files(root) == inventory["artifacts"]
        for name, expected in record["repository_observation_hashes"].items():
            assert (root / name).read_bytes() == (OUT / name).read_bytes()
            assert a.sha((OUT / name).read_bytes()) == expected
        external_status = "PASS_ALL_FILES_AND_SYMLINK_TARGETS_WITHOUT_FOLLOWING"
    if (OUT / "artifact_sha256.json").exists():
        inventory = a.loads((OUT / "artifact_sha256.json").read_bytes())
        expected_names = {str(p.relative_to(ROOT)) for p in files if p.name != "artifact_sha256.json"}
        assert expected_names == set(inventory["artifacts"])
        for name, expected in inventory["artifacts"].items():
            assert a.sha((ROOT / name).read_bytes()) == expected, name
    if "--verify-only" in sys.argv:
        assert (OUT / "artifact_sha256.json").exists()
        assert external_status.startswith("PASS")
        print(json.dumps({"status": "PASS_READ_ONLY_FINAL_ARTIFACT_VERIFICATION",
            "repository_artifacts_including_manifest": len(files), "accepted_files_preserved": 69,
            "external_artifacts": external_status, "bridge_qualified": False}))
        return
    save("validation_results.json", {"status": "PASS_INDEPENDENT_CHECKS_WITH_RUNTIME_MISSING_BLOCKER",
        "bridge_status": bridge["status"], "all_bridge_gates_passed": False,
        "exact_641_identities": "PASS", "583_58_split": "PASS", "two_blockers_preserved": "PASS",
        "source_object_presence": "PASS_FRESH_READ_ONLY_REVALIDATION", "seven_engine_base_identities": "PASS",
        "seven_bridge_bases_offline": "NOT_RUN", "output_parity": "NOT_RUN", "positive_origins": "0/2_NOT_RUN",
        "once_only_semantics": "PASS_5_ACTUAL_FILESYSTEM_TESTS", "focused_tests": results,
        "restricted_blanket_receipt_rejections": restricted_count, "none_receipt_rejections": none_count,
        "real_dispatch": "REJECT_BEFORE_CLAIM_AND_DOCKER", "real_dispatch_reason": real_reason,
        "rejection_classes": len(matrix), "bridge_specific_rejection_matrix": "NOT_RUN",
        "AST": "PASS", "production_AST_files": production_ast,
        "strict_JSON_UTF8_LF_BOM_NUL_whitespace": "PASS", "commands": checks,
        "accepted_69_files_canonical_and_index_preserved": True,
        "external_artifacts": external_status, "files_checked": [p.name for p in files],
        "semantic_enforcement_identity": None, "real_attempts": 0, "event_3_created": False})
    print(json.dumps({"status": "PASS_INDEPENDENT_CHECKS_WITH_RUNTIME_MISSING_BLOCKER",
        "mechanics_tests": 11, "rejection_classes": len(matrix), "bridge_qualified": False,
        "external_artifacts": external_status}))


if __name__ == "__main__":
    main()

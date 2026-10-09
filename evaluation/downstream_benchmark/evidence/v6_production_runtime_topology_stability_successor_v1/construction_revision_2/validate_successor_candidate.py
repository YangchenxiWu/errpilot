"""Read-only verification of a BLOCKED partial candidate; never promote it."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import stat
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator

from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def record(path):
    return {"sha256": sha(path.read_bytes()), "size_bytes": path.stat().st_size}


def strict(raw):
    assert raw.endswith(b"\n") and b"\r" not in raw and not raw.startswith(b"\xef\xbb\xbf")
    raw.decode("utf-8", "strict")
    return a.loads(raw)


def read(name):
    return strict((HERE / name).read_bytes())


def git(*args):
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=False,
                            env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"}, timeout=30)
    assert result.returncode == 0
    return result.stdout


def tree(root):
    result = {}
    for path in [root, *sorted(root.rglob("*"))]:
        assert not path.is_symlink()
        rec = {"type": "directory" if path.is_dir() else "file",
               "mode": stat.S_IMODE(path.lstat().st_mode)}
        if path.is_file():
            rec.update(record(path))
        result[str(path.relative_to(root))] = rec
    return result


def validate(require_seal):
    snapshot = read("entry_snapshot.json")
    checks = {}
    actual_tracked = [x for x in git("ls-files", "-z").decode().split("\0") if x]
    assert len(actual_tracked) == 1065 and set(actual_tracked) == set(snapshot["tracked"])
    assert {name: record(ROOT / name) for name in actual_tracked} == snapshot["tracked"]
    checks["all_1065_tracked_exact_bytes"] = "PASS"
    assert sha((ROOT / ".git/index").read_bytes()) == snapshot["index_sha256"]
    assert git("diff", "--binary") == git("diff", "--cached", "--binary") == b""
    assert git("diff", "--check") == b""
    assert git("rev-parse", "HEAD").decode().strip() == snapshot["head"]
    assert git("branch", "--show-current").decode().strip() == "main"
    checks["index_HEAD_and_tracked_diffs"] = "PASS"
    expected_untracked = set()
    payload_count = 0
    for predecessor in snapshot["predecessors"]:
        root = ROOT / predecessor["path"]
        files = {str(path.relative_to(root)) for path in root.rglob("*") if path.is_file()}
        assert files == set(predecessor["files"])
        for name, rec in predecessor["files"].items():
            assert record(root / name) == rec
            expected_untracked.add(str(Path(predecessor["path"]) / name))
        assert sha((root / "artifact_sha256.json").read_bytes()) == predecessor["manifest_sha256"]
        payload_count += predecessor["payload_count"]
    assert payload_count == 499 and len(expected_untracked) == 501
    own_files = {str(path.relative_to(ROOT)) for path in HERE.rglob("*") if path.is_file()}
    untracked = {x for x in git("ls-files", "--others", "--exclude-standard", "-z").decode().split("\0") if x}
    assert untracked == expected_untracked | own_files
    checks["complete_280_and_219_payload_preservation"] = "PASS"
    checks["only_two_predecessors_plus_new_namespace_untracked"] = "PASS"
    assert tree(Path(snapshot["ledger_root"])) == snapshot["ledger_tree"]
    assert record(Path(snapshot["namespace"]["path"])) == {k: snapshot["namespace"][k] for k in ("sha256", "size_bytes")}
    assert all(not (ROOT / path).exists() for path in snapshot["production_targets"].values())
    checks["real_ledger_exact_tree_and_namespace"] = "PASS"
    checks["all_six_production_targets_absent"] = "PASS"
    current = ROOT / "evaluation/downstream_benchmark/v6_current_state.json"
    assert sha(current.read_bytes()) == snapshot["current_state_sha256"]
    state = a.loads(current.read_bytes())
    assert state["event_count"] == 3
    assert state["event_head"]["event_id"] == "237d8020668f338c04065beb8557d8f25263fbfc0282003dcc5b2af67a20a50d"
    for event in state["event_chain"]:
        assert sha((ROOT / event["path"]).read_bytes()) == event["sha256"]
    checks["canonical_full_event_files_preserved"] = "PASS"
    json_count = 0
    python_count = 0
    for path in sorted(HERE.rglob("*")):
        assert not path.is_symlink()
        if not path.is_file():
            continue
        raw = path.read_bytes()
        if path.suffix == ".json":
            value = strict(raw)
            assert raw == (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                                      allow_nan=False) + "\n").encode()
            assert a.loads(a.canonical(value)) == value
            json_count += 1
        elif path.suffix == ".py":
            assert raw.endswith(b"\n") and b"\r" not in raw
            ast.parse(raw)
            python_count += 1
        elif path.suffix in {".md", ".txt"}:
            raw.decode("utf-8", "strict")
            assert b"\r" not in raw
    checks["strict_JSON_UTF8_LF_and_canonical_roundtrip"] = {"status": "PASS", "JSON_files": json_count}
    checks["new_evidence_script_AST_parse"] = {"status": "PASS", "Python_files": python_count}
    projection = read("security_projection_contract_candidate.json")
    assert projection["uniquely_executable_production_contract"] is False
    assert projection["production_gate"] == "BLOCKED_BY_UNRESOLVED_CLIENT_AUTHORIZATION"
    assert projection["security_projection_sha256"].startswith("NOT_COMPUTED")
    assert read("unknown_exec_authorization_policy_candidate.json")["exact_active_client_rule"].startswith("UNRESOLVED")
    assert read("source_semantic_delta.json")["status"] == "NOT_CONSTRUCTED"
    assert read("synthetic_e2e_results.json")["status"] == "NOT_RUN"
    assert read("synthetic_e2e_results.json")["A_X_totals"] == {"passed": 0, "failed": 0, "skipped": 24}
    assert len(read("rejection_matrix.json")["inherited_77"]) == 77
    assert read("construction_block.json")["status"] == "BLOCKED"
    checks["no_unknown_authorization_or_E2E_PASS_promotion"] = "PASS"
    for absent in read("construction_block.json")["not_constructed"]:
        assert not (HERE / absent).exists()
    checks["missing_source_installation_E2E_artifacts_not_fabricated"] = "PASS"
    schema = read("receipt_schema_v2_candidate.json")
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    example = {name: "a" * 64 for name in schema["required"]}
    example.update({"schema": schema["title"], "runtime_authority": False,
                    "candidate_only": True, "provider_independent_freshness_required": True,
                    "base_attempt_id": "SYNTHETIC_QUALIFICATION_SCHEMA_ONLY",
                    "work_item_identity": {"base_attempt_id": "SYNTHETIC_QUALIFICATION_SCHEMA_ONLY"},
                    "network_mode": "RESTRICTED_DEFAULT", "allowed_origins": ["files.pythonhosted.org:443", "pypi.org:443"]})
    assert validator.is_valid(example)
    assert a.loads(a.canonical(example)) == example
    positive = 2
    negatives = []
    for name in schema["required"]:
        value = dict(example)
        del value[name]
        assert not validator.is_valid(value)
        negatives.append("missing_" + name)
    for name, replacement in [
        ("runtime_authority", True), ("runtime_authority", 0), ("runtime_authority", "false"),
        ("candidate_only", False), ("provider_independent_freshness_required", False),
        ("schema", "V6_RESTRICTED_BUILD_EGRESS_ENFORCEMENT_RECEIPT_V1"),
        ("schema", "V6_RESTRICTED_BUILD_EGRESS_ENFORCEMENT_RECEIPT_V2"),
        ("network_mode", "NONE"), ("network_mode", "UNRESTRICTED"),
        ("allowed_origins", ["pypi.org:443"]),
        ("allowed_origins", ["files.pythonhosted.org:443", "pypi.org:443", "example.org:443"]),
        ("security_projection_sha256", "G" * 64), ("security_projection_sha256", None),
    ]:
        assert not validator.is_valid({**example, name: replacement})
        negatives.append("wrong_" + name + "_" + str(replacement))
    assert not validator.is_valid({**example, "live_daemon_topology_observation_sha256": "b" * 64})
    negatives.append("raw_SHA_relabel_or_extra_field")
    v1_schema = a.loads((ROOT / "evaluation/downstream_benchmark/evidence/v6_preparation_execution_production_runtime_installation_resume_v1/receipt_schema.json").read_bytes())
    assert not Draft202012Validator(v1_schema).is_valid(example)
    negatives.append("V2_candidate_does_not_validate_as_V1_schema")
    for raw in [b'{"x":1,"x":2}\n', b'{"x":NaN}\n', b'{"x":1.5}\n']:
        try:
            a.loads(raw)
        except (ValueError, a.Rejected):
            negatives.append("canonical_parser_rejected_" + raw.decode().strip())
        else:
            raise AssertionError("noncanonical scalar or duplicate accepted")
    checks["candidate_schema_only_tests"] = {"status": "PASS", "positive": positive, "negative": len(negatives),
                                              "negative_checks": negatives, "persisted_receipts": 0,
                                              "production_authority_validation": "NOT_RUN"}
    replay = read("scientific_projection_revalidation.json")
    assert replay["compiled_count"] == len(replay["per_item_replay"]) == 641
    assert replay["population"]["ordered_attempt_ids_sha256"] == a.identity(snapshot["ordered_attempt_ids"])
    assert [row["base_attempt_id"] for row in replay["per_item_replay"]] == snapshot["ordered_attempt_ids"]
    assert replay["successor_641_scientific_projection"] == "NOT_RUN_NO_SUCCESSOR_SOURCE"
    checks["predecessor_641_replay_record_integrity"] = "PASS_PREDECESSOR_ONLY"
    graph = read("supersession_dependency_graph.json")
    nodes = {node["id"] for node in graph["nodes"]}
    visiting, visited = set(), set()

    def visit(node):
        assert node not in visiting, "cyclic dependency graph"
        if node in visited:
            return
        visiting.add(node)
        for upstream, downstream in graph["edges"]:
            assert upstream in nodes and downstream in nodes
            if upstream == node:
                visit(downstream)
        visiting.remove(node)
        visited.add(node)
    for node in nodes:
        visit(node)
    for node in graph["nodes"]:
        for ref in node.get("artifacts", []):
            assert sha((ROOT / ref["path"]).read_bytes()) == ref["sha256"]
    checks["actual_partial_hash_references_and_planned_DAG_acyclic"] = "PASS"
    assert not (HERE / "qualification").exists()
    checks["no_synthetic_output_or_predecessor_qualification_writes"] = "PASS"
    checks["live_Docker_observation_and_complete_topology_validation"] = "NOT_RUN"
    checks["full_successor_source_AST_equivalence_Ruff_E2E_rejections"] = "NOT_RUN_NO_SUCCESSOR_SOURCE"
    if require_seal:
        seal = read("artifact_sha256.json")
        expected = set(seal["files"]) | {"artifact_sha256.json"}
        actual = {str(path.relative_to(HERE)) for path in HERE.rglob("*") if path.is_file()}
        assert actual == expected
        for name, rec in seal["files"].items():
            assert record(HERE / name) == {k: rec[k] for k in ("sha256", "size_bytes")}
        assert len(seal["files"]) == seal["file_count"]
        assert sum(rec["size_bytes"] for rec in seal["files"].values()) == seal["total_payload_size_bytes"]
        checks["full_artifact_path_size_SHA_seal_replay"] = "PASS"
        checks["manifest_file_SHA_external"] = sha((HERE / "artifact_sha256.json").read_bytes())
    else:
        checks["full_artifact_path_size_SHA_seal_replay"] = "NOT_REQUESTED_PRESEAL"
    return {"schema": "V6_BLOCKED_SUCCESSOR_EVIDENCE_VALIDATION_V1", "status": "BLOCKED",
            "bounded_evidence_checks": "PASS", "candidate_review_ready": False,
            "production_gate": "BLOCKED_BY_UNRESOLVED_CLIENT_AUTHORIZATION", "checks": checks,
            "claims": 0, "terminals": 0, "real_attempt_consumption": 0,
            "evidence_validation_is_successor_qualification": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-seal", action="store_true")
    args = parser.parse_args()
    print(json.dumps(validate(args.verify_seal), ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

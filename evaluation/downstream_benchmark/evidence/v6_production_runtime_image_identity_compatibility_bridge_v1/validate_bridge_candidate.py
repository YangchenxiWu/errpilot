"""Validate a bounded non-effective candidate and its immutable evidence graph.

--verify-seal is read-only. The construction result can be BLOCKED even when
evidence integrity/static/pure gates pass; live byte equality remains mandatory.
"""
from __future__ import annotations

import ast
import copy
import difflib
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from . import corrected_production_provider_candidate as p

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parent / "v6_preparation_execution_production_runtime_installation_resume_v1" / "production_provider_candidate.py"
HELPERS = {"image_identity_pins", "verify_image_identity", "retained_image_content", "observe_image_config"}


def dump(value):
    return ast.dump(value, include_attributes=False)


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def git(*args):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    return subprocess.check_output(["git", *args], cwd=p.a.ROOT, env=env)


def function_inventory(tree):
    result = {}

    def visit(node, prefix=""):
        for child in getattr(node, "body", []):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = prefix + child.name
                result[name] = hashlib.sha256(dump(child).encode()).hexdigest()
                visit(child, name + ".")
    visit(tree)
    return result


def semantic_delta():
    old_raw, new_raw = ORIGINAL.read_bytes(), (HERE / "corrected_production_provider_candidate.py").read_bytes()
    assert p.a.sha(old_raw) == "d466c9310d22754c0c3c9744764bcc402aef988195da7f7aea45b9700eb1de0a"
    old, new = ast.parse(old_raw), ast.parse(new_raw)
    old_functions, new_functions = function_inventory(old), function_inventory(new)
    changed = [n for n in old_functions if old_functions[n] != new_functions.get(n)]
    assert set(changed) == {"Authority", "Authority.observe", "normalize_topology"}
    authority_old = next(x for x in old.body if isinstance(x, ast.ClassDef) and x.name == "Authority")
    authority_new = next(x for x in new.body if isinstance(x, ast.ClassDef) and x.name == "Authority")
    observe_old = next(x for x in authority_old.body if isinstance(x, ast.FunctionDef) and x.name == "observe")
    observe_new = next(x for x in authority_new.body if isinstance(x, ast.FunctionDef) and x.name == "observe")
    expected_observe = copy.deepcopy(observe_old)
    assignments = []
    for node in ast.walk(expected_observe):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Subscript):
            target = node.targets[0]
            if isinstance(target.slice, ast.Constant) and target.slice.value == "image_config_digest":
                role = target.value.id
                assert role in ("daemon", "proxy")
                node.value = ast.parse(f'observe_image_config({role}, self.config, "{role}", run)', mode="eval").body
                assignments.append(role)
    assert assignments == ["daemon", "proxy"] and dump(expected_observe) == dump(observe_new)
    normalize_old = next(x for x in old.body if isinstance(x, ast.FunctionDef) and x.name == "normalize_topology")
    normalize_new = next(x for x in new.body if isinstance(x, ast.FunctionDef) and x.name == "normalize_topology")
    expected_normalize = copy.deepcopy(normalize_old)
    gates = ast.parse('''a.require(d["Image"] == image_identity_pins(config, "daemon")["engine"], "wrong BuildKit Engine image ID")
a.require(p["Image"] == image_identity_pins(config, "proxy")["engine"], "wrong proxy Engine image ID")''').body
    expected_normalize.body[2:2] = gates
    assert dump(expected_normalize) == dump(normalize_new)
    # Remove only proven changes; the complete remaining module must equal frozen AST.
    reverted = copy.deepcopy(new)
    reverted.body = [x for x in reverted.body if not
                     (isinstance(x, ast.FunctionDef) and x.name in HELPERS)
                     and not (isinstance(x, ast.Import) and [y.name for y in x.names] == ["tarfile"])]
    for i, node in enumerate(reverted.body):
        if isinstance(node, ast.FunctionDef) and node.name == "normalize_topology":
            reverted.body[i] = copy.deepcopy(normalize_old)
        elif isinstance(node, ast.ClassDef) and node.name == "Authority":
            for j, method in enumerate(node.body):
                if isinstance(method, ast.FunctionDef) and method.name == "observe":
                    node.body[j] = copy.deepcopy(observe_old)
    assert dump(reverted) == dump(old)
    pure = next(x for x in new.body if isinstance(x, ast.FunctionDef) and x.name == "verify_image_identity")
    forbidden = {"Authority", "ReceiptBoundLedger", "ProductionProvider", "subprocess", "eval", "exec",
                 "__import__", "setattr", "delattr", "object", "receipt_value", "verify_receipt"}
    assert not any(isinstance(x, ast.Name) and x.id in forbidden for x in ast.walk(pure))
    assert not any(isinstance(x, (ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal)) for x in ast.walk(pure))
    seam_tree = ast.parse((HERE / "candidate_only_identity_observer.py").read_bytes())
    assert not any(isinstance(x, ast.Attribute) and x.attr in
                   {"Authority", "synthetic", "claim", "terminal", "refresh", "receipt_value", "__new__"}
                   for x in ast.walk(seam_tree))
    patch = "".join(difflib.unified_diff(old_raw.decode().splitlines(True), new_raw.decode().splitlines(True),
                                    fromfile=str(ORIGINAL), tofile=str(HERE / "corrected_production_provider_candidate.py")))
    assert (HERE / "provider_identity_correction.patch").read_bytes() == patch.encode()
    return {"schema": "V6_IMAGE_IDENTITY_BRIDGE_SOURCE_SEMANTIC_DELTA_V1", "status": "PASS",
            "original_provider_sha256": p.a.sha(old_raw), "corrected_provider_sha256": p.a.sha(new_raw),
            "changed_existing_methods": ["Authority.observe: two image assignments only", "normalize_topology: two additional exact Engine ID gates only"],
            "added_helpers": sorted(HELPERS), "added_imports": ["tarfile"],
            "original_functions": old_functions, "corrected_functions": new_functions,
            "complete_module_AST_equivalent_after_reverting_verified_seam": True,
            "Authority_refresh_unchanged": True, "source_location_and_synthetic_guards_unchanged": True,
            "controller_changed": False, "receipt_serialization_fields_unchanged": True,
            "ReceiptBoundLedger_claim_terminal_unchanged": True, "ProductionProvider_behavior_unchanged": True,
            "scientific_source_export_recipe_transport_unchanged": True,
            "pure_helper_cannot_create_production_authority": True,
            "NOTE": "Code evidence and pure qualification only. No runtime installation/effectivity or scientific validation."}


def validate():
    baseline = p.exact_json(HERE / "accepted_baseline_binding.json")
    for ref in baseline["pins"]:
        assert digest(Path(ref["path"])) == ref["sha256"], ref["path"]
    for ref in baseline["original_package_files"] + baseline["topology_evidence"]:
        path = Path(ref["path"])
        assert digest(path) == ref["sha256"] and path.stat().st_size == ref["size_bytes"], str(path)
    delta = semantic_delta()
    for path in HERE.rglob("*"):
        assert not path.is_symlink()
        if path.is_file() and path.suffix in {".json", ".py", ".md", ".patch"}:
            raw = path.read_bytes()
            raw.decode("utf-8", errors="strict")
            assert b"\r" not in raw and raw.endswith(b"\n"), str(path)
            if path.suffix == ".json":
                value = p.a.loads(raw)
                assert raw == p.pretty(value) or raw == p.a.canonical(value), str(path)
            if path.suffix == ".py":
                ast.parse(raw)
    before = p.exact_json(HERE / "before_preservation_snapshot.json")
    for name, ref in before["tracked"].items():
        assert digest(p.a.ROOT / name) == ref["sha256"]
    assert digest(p.a.ROOT / ".git/index") == before["index_sha256"]
    assert git("diff", "--binary") == git("diff", "--cached", "--binary") == b""
    assert git("rev-parse", "HEAD").decode().strip() == "e492d159daf188323efcfe121aa019d5b098bfb2"
    assert git("branch", "--show-current").decode().strip() == "main"
    status = git("status", "--porcelain=v1", "--untracked-files=all").decode().splitlines()
    relative = str(HERE.relative_to(p.a.ROOT)) + "/"
    assert status and all(row.startswith("?? " + relative) for row in status), status
    tests = p.exact_json(HERE / "synthetic_qualification_results.json")
    rejects = p.exact_json(HERE / "rejection_matrix.json")
    assert all(x["status"] == "PASS" for x in tests["tests"].values())
    assert tests["candidate_provider_sha256"] == delta["corrected_provider_sha256"]
    assert tests["qualification_code_sha256"] == digest(HERE / "qualify_bridge_candidate.py")
    assert tests["pure_seam_sha256"] == digest(HERE / "candidate_only_identity_observer.py")
    assert rejects["count"] == tests["rejection_count"] == len(rejects["checks"])
    assert all(x["status"] == "PASS_REJECTED" for x in rejects["checks"].values())
    topology = p.exact_json(HERE / "topology_comparison.json")
    assert topology["corrected_provider_sha256"] == delta["corrected_provider_sha256"]
    raw = (HERE / "corrected_topology_observation.json").read_bytes()
    assert p.a.sha(raw) == topology["observed_sha256"] and raw == p.a.canonical(p.a.loads(raw))
    assert topology["same_schema"] and topology["same_field_names"]
    expected_raw = (p.a.OUTPUT_ROOT / "qualification/production_runtime_topology_provisioning_v1/live_topology_observation.json").read_bytes()
    assert (raw == expected_raw) == topology["canonical_bytes_equal"]
    if not topology["canonical_bytes_equal"]:
        assert topology["status"] == "BLOCKED" and topology["differences"]
    if (HERE / "supersession_dependency_report.json").exists():
        report = p.exact_json(HERE / "supersession_dependency_report.json")
        assert report["old_accepted_provider_sha256"] == delta["original_provider_sha256"]
        assert report["corrected_proposed_provider_sha256"] == delta["corrected_provider_sha256"]
        assert report["old_plan_authorizes_new_provider"] is False
        assert report["accepted_or_effective_replacement_plan_created"] is False
    preservation = p.exact_json(HERE / "preservation_verification.json")
    assert preservation["status"] in {"PASS_PRESERVED", "BLOCKED_DOCKER_INSPECT_DRIFT"}
    assert preservation["all_1065_tracked_file_bytes_equal"] and preservation["index_bytes_equal"]
    assert preservation["real_ledger_exact_tree_equal"] and preservation["real_ledger_states"] == {"UNSTARTED": 641}
    if preservation["status"] != "PASS_PRESERVED":
        assert preservation["docker_full_inspect_differences"]
    commands = p.exact_json(HERE / "fresh_live_commands.json")
    for command in commands:
        assert command["returncode"] == 0
        for name in ("stdout", "stderr"):
            assert digest(HERE / command[name + "_path"]) == command[name + "_sha256"]
    return delta, {"schema": "V6_IMAGE_IDENTITY_BRIDGE_VALIDATION_V1",
                   "status": "BLOCKED" if not topology["canonical_bytes_equal"] or preservation["status"] != "PASS_PRESERVED" else
                   "V6_PRODUCTION_RUNTIME_IMAGE_IDENTITY_COMPATIBILITY_CANDIDATE_READY_FOR_HUMAN_PI_REVIEW",
                   "blocking_reasons": ([topology["reason"]] if topology["reason"] else [])
                       + ([preservation["status"]] if preservation["status"] != "PASS_PRESERVED" else []),
                   "artifact_integrity": "PASS", "frozen_sources": "PASS",
                   "strict_JSON_UTF8_LF": "PASS", "hash_graph": "PASS", "AST_scope": "PASS", "source_parse": "PASS",
                   "affected_pure_tests": "PASS", "rejection_checks": "PASS_REJECTED",
                   "topology_exact_bytes": "PASS" if topology["canonical_bytes_equal"] else "BLOCKED",
                   "preservation": preservation["status"], "full_controller_provider_E2E": "NOT_RUN",
                   "full_A_through_X_qualification_claimed": False, "candidate_only": True,
                   "runtime_effective": "NO", "installation_authority": "NO", "real_attempt_authority": "NO"}


def verify_seal():
    manifest = p.exact_json(HERE / "artifact_sha256.json")
    paths = {str(x.relative_to(HERE)) for x in HERE.rglob("*") if x.is_file() and x.name != "artifact_sha256.json"}
    assert paths == set(manifest["files"])
    for name, ref in manifest["files"].items():
        path = HERE / name
        assert ref["path"] == str(path) and digest(path) == ref["sha256"] and path.stat().st_size == ref["size_bytes"]
    return {"status": "PASS_SEAL", "files": len(paths), "manifest_sha256": digest(HERE / "artifact_sha256.json")}


def main():
    delta, result = validate()
    if "--verify-seal" in sys.argv:
        assert p.a.canonical(delta) == p.a.canonical(p.exact_json(HERE / "source_semantic_delta.json"))
        stored = p.exact_json(HERE / "validation_results.json")
        assert all(stored[k] == v for k, v in result.items())
        print(json.dumps({"validation": result, "seal": verify_seal()}))
    else:
        (HERE / "source_semantic_delta.json").write_bytes(p.pretty(delta))
        (HERE / "validation_results.json").write_bytes(p.pretty(result))
        print(json.dumps(result))


if __name__ == "__main__":
    main()

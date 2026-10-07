"""Guarded static/schema/unit validation and end-state preservation audit.

Run with the existing .venv Python -B. Only validation_results.json is written.
Real engines, source exports, Docker, network and non-Git processes are denied.
"""
import ast
import importlib.util
import io
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
E = Path(__file__).resolve().parent
ROOT = E.parents[3]
sys.path.insert(0, str(ROOT))

from evaluation.downstream_benchmark.evidence.v6_preparation_execution_activation_v1 import (  # noqa: E402
    adapter_candidate as a, controller_candidate as c, test_candidates as tests,
)

COUNTS = {"read_only_git_processes": 0, "forbidden_process_attempts": 0,
          "real_engine_calls": 0, "real_source_exports": 0, "docker_calls": 0,
          "network_attempts": 0}


def audit(event, args):
    if event == "subprocess.Popen":
        argv = args[1]
        allowed = isinstance(argv, (list, tuple)) and argv[0] == "git" and len(argv) > 1 and argv[1] in {
            "ls-files", "status", "diff", "rev-parse", "branch", "cat-file", "ls-tree", "log", "diff-tree"}
        if not allowed:
            COUNTS["forbidden_process_attempts"] += 1
            raise RuntimeError("non-read-only-Git subprocess forbidden")
        COUNTS["read_only_git_processes"] += 1
    elif event == "open":
        path, mode, flags = args
        writing = (isinstance(mode, str) and any(x in mode for x in "wax+")) or (
            flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        if writing and not isinstance(path, int):
            a.require(Path(os.fsdecode(path)).absolute() == E / "validation_results.json",
                      "validation writes outside its result forbidden")
    elif event.startswith("socket."):
        COUNTS["network_attempts"] += 1
        raise RuntimeError("network forbidden")
    elif event in {"os.system", "os.posix_spawn", "os.fork", "os.mkdir", "os.remove", "os.rmdir", "os.rename", "os.symlink"}:
        raise RuntimeError("alternate execution/filesystem mutation forbidden")


FORBIDDEN_CODES = {
    a.shared._materialize_checked.__code__: "real_engine_calls",
    a.shared.docker.__code__: "docker_calls",
    a.shared.docker_observation.__code__: "docker_calls",
    c.snapshots.source_snapshot_identity.__code__: "real_source_exports",
    a.shared.transport_source_package.__code__: "real_source_exports",
}


def profile(frame, event, arg):
    if event == "call" and frame.f_code in FORBIDDEN_CODES:
        COUNTS[FORBIDDEN_CODES[frame.f_code]] += 1
        raise RuntimeError("real engine/source/Docker invocation forbidden")


sys.addaudithook(audit)
sys.setprofile(profile)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT,
                                   env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"})


def preservation(entry):
    a.require(git("rev-parse", "HEAD").decode().strip() == entry["head"], "HEAD changed")
    a.require(git("branch", "--show-current").decode().strip() == "main", "branch changed")
    a.require(git("diff", "--name-only") == git("diff", "--cached", "--name-only") == b"", "tracked/index modification")
    tracked = {}
    for line in git("ls-files", "--stage", "-z").split(b"\0"):
        if not line:
            continue
        meta, name = line.split(b"\t", 1)
        mode, oid, stage = meta.split()
        a.require(stage == b"0", "unmerged index")
        path = ROOT / name.decode()
        raw = os.readlink(path).encode() if path.is_symlink() else path.read_bytes()
        tracked[name.decode()] = {"mode": mode.decode(), "index_oid": oid.decode(), "sha256": a.sha(raw)}
    a.require(tracked == entry["tracked_files"], "preexisting tracked bytes/index drift")
    external, paths = {}, {}
    for root in a.WORK_ROOT.iterdir():
        if root.name in {"bugsinpy", "subject_repositories", "caches"}:
            continue
        for base, dirs, files in os.walk(root):
            dirs[:] = [x for x in dirs if x not in {"source", "context", "workspace", ".git", "BUGGY", "FIXED", "SOURCE_INDEPENDENT"}]
            for name in files:
                path = Path(base) / name
                paths[str(path)] = path.is_symlink()
                if name in {"attempt.json", "preparation_plan.json", "source_identity.json"} or name.endswith("_plan.json"):
                    external[str(path)] = a.sha(path.read_bytes())
    a.require(external == entry["external_metadata"], "historical attempt/preparation metadata drift")
    path_hash = a.sha((json.dumps(paths, sort_keys=True, separators=(",", ":")) + "\n").encode())
    a.require(path_hash == entry["external_evidence_path_inventory"]["sha256"]
              and len(paths) == entry["external_evidence_path_inventory"]["count"], "new/missing production evidence path")
    a.require(sorted(x.name for x in a.WORK_ROOT.iterdir()) == entry["entry_work_root_children"], "new production root")
    a.require(not a.OUTPUT_ROOT.exists() and not a.OUTPUT_ROOT.is_symlink(), "real V6 output root exists")
    return {"tracked_files_unchanged": len(tracked), "historical_metadata_unchanged": len(external),
            "historical_evidence_path_count_unchanged": len(paths), "new_real_attempt_directories": 0}


def check_candidate_data():
    descriptor, manifest = a.load_inputs()
    pop = a.loads((E / "work_items_candidate.json").read_bytes())
    a.validate_population(manifest, pop)
    ledger = a.loads((E / "ledger_candidate.json").read_bytes())
    a.require(a.canonical(ledger) == a.canonical(c.ledger_template(pop)), "ledger template modified/consumed")
    c.validate_journal(ledger, pop)
    auth = a.loads((E / "authority_candidates.json").read_bytes())
    a.require(set(auth["separate_permissions"]) == set(c.PERMISSIONS), "separate authority surface")
    common = auth["common_binding"]
    a.require(auth["common_binding_sha256"] == a.identity(common), "common binding SHA")
    for record in auth["separate_permissions"].values():
        a.require(record["HUMAN_PI_ACCEPTED"] == "NO" and record["lifecycle"] == "CANDIDATE_ONLY"
                  and record["runtime_authority"] is False
                  and record["common_binding_sha256"] == a.identity(common), "authority inferred/fabricated")
    a.require(auth["candidate_only"] is True and auth["runtime_authority"] is False
              and auth["event_3_constructed"] is False
              and auth["effective_current_descriptor_constructed"] is False, "candidate effectivity")
    for ref in [*common["runtime_input_binding_implementation"].values(), *common["shared_mechanics"].values(),
                common["ordered_work_items"], common["once_only_ledger"],
                common["entry_current_descriptor"], common["accepted_manifest"], common["accepted_plan_closure"]]:
        a.read_exact(ref["path"], ref["sha256"])
    a.require(common["population_semantic_sha256"] == a.identity(pop)
              and common["population_counts"] == pop["counts"] and common["runtime_policy"] == c.ROUTE_POLICY,
              "population/permission scope")
    a.require(common["proposed_v6_output_root"] == str(a.OUTPUT_ROOT), "output root binding")
    network = auth["separate_permissions"]["BUILD_NETWORK"]["exact_scope"]
    a.require(network["exact_network_work_item_ids"] == [x["base_attempt_id"] for x in pop["items"] if x["build_network_required"]]
              and network["network_required_work_items"] == 583 and network["network_none_work_items"] == 58
              and network["execution_network"] == "NONE" and network["policy"] == a.NETWORK_POLICY,
              "build-network scope widened")
    # Published owning schemas and frozen phase semantics; no event is created.
    spec = importlib.util.spec_from_file_location("frozen_v6_schema_audit",
        a.B / "evidence/v6_successor_contract_construction_v1/validate_contract.py")
    frozen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(frozen)
    frozen.validate_schema("V6_CAPACITY_CURRENT_STATE_V1", descriptor)
    for ref in descriptor["event_chain"]:
        frozen.validate_schema("V6_CAPACITY_STATE_EVENT_V1", a.loads(a.read_exact(ref["path"], ref["sha256"])))
    lifecycle = a.loads((a.B / "v6_census_lifecycle.json").read_bytes())
    frozen.validate_schema("V6_CENSUS_LIFECYCLE_V1", lifecycle)
    edge = next(x for x in lifecycle["transitions"] if x["from"] == "PREPARATION_PLANNING_AUTHORIZED"
                and x["to"] == "PREPARATION_EXECUTION_AUTHORIZED")
    a.require(edge["gate"] == "HUMAN_PI_AUTHORIZE_V6_PREPARATION_EXECUTION"
              and edge["requires"] == "Exact accepted plans, separate source acquisition/materialization/build permissions, revalidated implementation; once-only attempts",
              "frozen edge reinterpreted")
    future = frozen.phase_flags_for_edge(descriptor["projection"], edge["to"])
    a.require(future["case_states"] == descriptor["projection"]["case_states"], "activation scientific delta")
    a.require(future["phase_authorizations"]["PREPARATION_PLANNING"] == "YES"
              and future["phase_authorizations"]["PREPARATION_EXECUTION"] == "YES"
              and future["lifecycle"]["PREPARATION_AUTHORIZED"] == "YES", "future phase delta")
    return {"current_schema": "PASS", "two_existing_event_schemas": "PASS",
            "frozen_lifecycle_schema_and_edge": "PASS", "candidate_exact_structure_and_hashes": "PASS",
            "authority_acceptance": "NO", "future_event_3_created": False, "counts": pop["counts"]}


def text_and_ast():
    python, json_count = 0, 0
    for path in E.iterdir():
        if not path.is_file():
            continue
        raw = path.read_bytes()
        text = raw.decode("utf-8", errors="strict")
        a.require(raw.endswith(b"\n") and not raw.startswith(b"\xef\xbb\xbf") and b"\0" not in raw,
                  "UTF-8/LF/BOM/NUL")
        a.require(all(line == line.rstrip() for line in text.splitlines()), "trailing whitespace")
        if path.suffix == ".py":
            ast.parse(text)
            python += 1
        elif path.suffix == ".json":
            a.loads(raw)
            json_count += 1
    return {"python_ast_files": python, "strict_json_files": json_count, "text_integrity": "PASS"}


def main():
    entry = a.loads((E / "entry_verification.json").read_bytes())
    before = preservation(entry)
    data = check_candidate_data()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(tests.CandidateTests)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    a.require(result.wasSuccessful(), stream.getvalue())
    after = preservation(entry)
    text_result = text_and_ast()
    evidence = {"schema": "V6_PREPARATION_PACKAGE_VALIDATION_RESULTS_V1", "status": "PASS",
                "unit_tests_run": result.testsRun, "failed": len(result.failures), "errors": len(result.errors),
                "positive_checks": tests.POSITIVE, "rejection_checks": tests.REJECTIONS,
                "rejection_count": len(tests.REJECTIONS), "schema_and_binding_checks": data,
                "before_preservation": before, "after_preservation": after,
                "static_checks": text_result, "guard_counts": COUNTS,
                "test_log": stream.getvalue(),
                "qualification": "Non-executing candidate tests only; no runtime/build/source-export/scientific qualification"}
    (E / "validation_results.json").write_text(json.dumps(evidence, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": evidence["status"], "tests": result.testsRun,
                      "rejections": evidence["rejection_count"], "guards": COUNTS}, sort_keys=True))


if __name__ == "__main__":
    main()

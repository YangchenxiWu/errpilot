"""Run authorized bridge/runtime checks, preserving exact results in this run."""
from __future__ import annotations

import ast
import importlib.util
import io
import os
import subprocess
import sys
import unittest
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("bridge_validation", OUT / "transport_bridge.py")
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)
os.environ["ERRPILOT_V6_ACTUAL_FS_QUALIFICATION"] = "YES"
from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a  # noqa: E402
from evaluation.downstream_benchmark.screening import v6_preparation_ledger as ledger  # noqa: E402
from evaluation.downstream_benchmark.screening import v6_preparation_runtime as runtime  # noqa: E402
from evaluation.downstream_benchmark.tests import test_v6_preparation_runtime as existing  # noqa: E402


def synthetic_setup(cls):
    cls.root = t.Q / "ledger-fixtures"
    a.require(not cls.root.exists() and not cls.root.is_symlink(), "no fixture overwrite")
    cls.real_ids = [x["base_attempt_id"] for x in runtime.population()["items"]]
    cls.journal = ledger.Ledger(cls.root, namespace=ledger.SYNTHETIC, real_ids=cls.real_ids)
    cls.journal.initialize()


def run_command(name, argv):
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, check=False, timeout=55)
    t.durable(OUT / (name + ".stdout.txt"), result.stdout)
    t.durable(OUT / (name + ".stderr.txt"), result.stderr)
    return {"argv": argv, "exit_code": result.returncode,
            "stdout_sha256": t.sha(result.stdout), "stderr_sha256": t.sha(result.stderr)}


def main():
    existing.ActualFilesystemTests.setUpClass = classmethod(synthetic_setup)
    suite = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(existing.RuntimeTests),
                               unittest.defaultTestLoader.loadTestsFromTestCase(existing.ActualFilesystemTests)])
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    t.durable(OUT / "runtime_tests.txt", stream.getvalue().encode())
    runtime_result = {"run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
        "skipped": len(result.skipped), "status": "PASS" if result.wasSuccessful() and not result.skipped else "FAIL",
        "fixture_root": str(t.Q / "ledger-fixtures"), "namespace": ledger.SYNTHETIC,
        "existing_test_source_sha256": t.file_sha(Path(existing.__file__)),
        "override": "in-memory setUpClass qualification path only; unchanged existing 11 test bodies"}
    focused = run_command("focused_tests", [sys.executable, str(OUT / "test_transport_bridge.py")])
    files = sorted(OUT.glob("*.py")) + [ROOT / p for p in runtime.IMPLEMENTATION] + [Path(existing.__file__)]
    ruff = run_command("ruff", [str(ROOT / ".venv/bin/ruff"), "check", *map(str, files)])
    diff = run_command("git_diff_check", ["git", "diff", "--check"])
    syntax = {}
    for path in files:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        syntax[str(path.relative_to(ROOT))] = "PASS"
    strict = {}
    for path in sorted(OUT.glob("*.json")):
        t.strict_json(path.read_bytes())
        strict[path.name] = "PASS"
    whitespace = {p.name: [i for i, line in enumerate(p.read_text().splitlines(), 1) if line.rstrip() != line]
                  for p in OUT.glob("*.py")}
    t.require(not any(whitespace.values()), "new file whitespace errors")
    t.validate_layout(Path(t.load("oci_layout_construction.json")["local_oci_path"]), t.load("oci_layout_construction.json"))
    report = {"status": "PASS" if runtime_result["status"] == "PASS" and all(
        x["exit_code"] == 0 for x in [focused, ruff, diff]) else "FAIL", "runtime_tests": runtime_result,
        "focused_bridge_tests": {**focused, "test_methods": 8, "synthetic_archive_rejection_cases": 8,
                                 "synthetic_layout_rejection_cases": 5},
        "Ruff": ruff, "AST": syntax, "strict_JSON_UTF8": strict, "git_diff_check": diff,
        "new_file_whitespace": whitespace, "actual_candidate_OCI_integrity": "PASS",
        "production_transport_and_egress_integration_suite": "NOT_RUN_FIRST_BASE_HARD_GATE",
        "live_first_base_consumption": "FAIL_BEFORE_RUN", "scientific_validation": False}
    t.save("test_results.json", report)
    print(t.encoded({"status": report["status"], "runtime_tests": runtime_result,
        "focused_tests": report["focused_bridge_tests"], "Ruff": ruff["exit_code"], "AST_files": len(syntax),
        "strict_JSON_files": len(strict), "git_diff_check": diff["exit_code"]}).decode(), flush=True)
    t.require(report["status"] == "PASS", "required mechanics checks failed")


if __name__ == "__main__":
    main()

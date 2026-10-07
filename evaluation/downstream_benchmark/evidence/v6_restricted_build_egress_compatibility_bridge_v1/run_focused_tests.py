"""Rerun existing mechanics tests in this transaction's synthetic namespace."""
from __future__ import annotations

import io
import json
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.environ["ERRPILOT_V6_ACTUAL_FS_QUALIFICATION"] = "YES"
from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a  # noqa: E402
from evaluation.downstream_benchmark.screening import v6_preparation_ledger as ledger  # noqa: E402
from evaluation.downstream_benchmark.screening import v6_preparation_runtime as runtime  # noqa: E402
from evaluation.downstream_benchmark.tests import test_v6_preparation_runtime as tests  # noqa: E402

Q = a.OUTPUT_ROOT / "qualification/restricted_build_egress_compatibility_bridge_v1"


def setup_synthetic(cls):
    cls.root = Q / "ledger-fixtures"
    a.require(not cls.root.exists() and not cls.root.is_symlink(), "fixture already exists; no overwrite")
    cls.real_ids = [x["base_attempt_id"] for x in runtime.population()["items"]]
    cls.journal = ledger.Ledger(cls.root, namespace=ledger.SYNTHETIC, real_ids=cls.real_ids)
    cls.journal.initialize()


def main():
    tests.ActualFilesystemTests.setUpClass = classmethod(setup_synthetic)
    stream = io.StringIO()
    suite = unittest.TestSuite([
        unittest.defaultTestLoader.loadTestsFromTestCase(tests.RuntimeTests),
        unittest.defaultTestLoader.loadTestsFromTestCase(tests.ActualFilesystemTests),
    ])
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    (OUT / "focused_tests.txt").write_text(stream.getvalue(), encoding="utf-8")
    report = {"status": "PASS" if result.wasSuccessful() else "FAILED",
        "run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
        "skipped": len(result.skipped), "runtime_tests": 6, "actual_filesystem_tests": 5,
        "filesystem_root": str(Q / "ledger-fixtures"), "namespace": ledger.SYNTHETIC,
        "fixture_setup_override": "In-memory setUpClass path only; existing five test bodies unchanged",
        "test_source_sha256": a.sha(Path(tests.__file__).read_bytes()),
        "real_ledger_claim_count_after": len(list((a.OUTPUT_ROOT / "ledger/claims").iterdir())),
        "real_claims_created": 0, "qualification_is_bridge_network_or_output_proof": False}
    a.require(report["real_ledger_claim_count_after"] == 0, "real claim appeared")
    (OUT / "persistent_ledger_qualification.json").write_text(
        json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    a.require(result.wasSuccessful() and result.testsRun == 11 and not result.skipped,
              "required existing mechanics tests failed or skipped")


if __name__ == "__main__":
    main()

"""Transaction-owned synthetic qualification; no real attempt identity can run."""
from __future__ import annotations

import csv
import io
import json
import os
import subprocess
import unittest
from collections import Counter
from pathlib import Path

from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a
from evaluation.downstream_benchmark.screening import v6_preparation_ledger as l
from evaluation.downstream_benchmark.screening import v6_preparation_runtime as r
from evaluation.downstream_benchmark.tests import test_v6_preparation_runtime as tests
from evaluation.downstream_benchmark.tests.test_environment_materializer import fixture as load_fixture

E = Path(__file__).resolve().parent
Q = a.OUTPUT_ROOT / "qualification" / "runtime-implementation-v1"


def save(name, value):
    (E / name).write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def docker(*args):
    result = subprocess.run(["docker", *args], capture_output=True, check=False, timeout=60)
    return result


def bases():
    counts = Counter(x["base_image_reference"] for x in r.population()["items"])
    rows = list(csv.DictReader((a.B / "runtime_base_images.csv").open()))
    observations = []
    engine = r.shared_engine()
    for row in rows:
        ref = row["image_source"] + "@" + row["immutable_digest"]
        inspected = docker("image", "inspect", ref)
        observed = {"reference": ref, "python_version": row["python_version"],
                    "affected_work_items": counts[ref], "inspect_exit_code": inspected.returncode,
                    "inspect_stdout_sha256": a.sha(inspected.stdout),
                    "inspect_stderr_sha256": a.sha(inspected.stderr)}
        if inspected.returncode:
            observed.update(local_status="LOCAL_MISSING" if b"No such image" in inspected.stderr
                            else "LOCAL_STATUS_UNVERIFIED", qualification="BLOCKED")
        else:
            observed["local_status"] = "LOCAL_PRESENT"
            try:
                probe = engine.verify_base({"base_image_reference": ref,
                    "base_image_digest": row["immutable_digest"],
                    "python_declared_version": row["python_version"],
                    "python_observed_version": row["observed_python_version"],
                    "python_executable_sha256": row["python_executable_sha256"]})
                observed.update(qualification="PASS", python_probe=probe)
                image = json.loads(inspected.stdout)[0]
                observed["image_identity"] = {k: image[k] for k in
                                               ("Id", "Os", "Architecture", "RepoDigests", "RootFS")}
            except (a.shared.Blocked, a.Rejected) as exc:
                observed.update(qualification="BLOCKED", reason=str(exc))
        observations.append(observed)
    save("base_runtime_local_status.json", {"schema": "V6_BASE_RUNTIME_LOCAL_STATUS_V1",
         "bases": observations, "pulls": 0, "substitutions": 0,
         "affected_work_items_total": sum(x["affected_work_items"] for x in observations)})
    return observations


def network():
    inspection = {}
    for name, args in (("default_bridge", ("network", "inspect", "bridge")),
                       ("builder", ("buildx", "inspect", "desktop-linux")),
                       ("networks", ("network", "ls", "--format", "{{json .}}"))):
        result = docker(*args)
        inspection[name] = {"argv": ["docker", *args], "exit_code": result.returncode,
                            "stdout": result.stdout.decode(), "stderr": result.stderr.decode(),
                            "stdout_sha256": a.sha(result.stdout)}
    policy = {"scope": "EXACT_583_ACCEPTED_WORK_ITEMS", "default_action": "DENY",
              "allowed_origins": ["https://pypi.org/simple/", "https://files.pythonhosted.org/"],
              "execution_network": "NONE", "registry_egress": "NONE",
              "implementation": "UNPROVISIONED_SHARED_DEFAULT_NETWORK"}
    result = {"schema": "V6_NETWORK_ENFORCEMENT_QUALIFICATION_V1",
        "status": "RESTRICTED_BUILD_NETWORK_ENFORCEMENT_BLOCKED", "affected_work_items": 583,
        "policy": policy, "policy_semantic_sha256": a.identity(policy),
        "installed_enforcement_identity": "ABSENT", "inspection": inspection,
        "reason": "Only built-in docker-driver builders and ordinary bridge/host/none networks "
                  "are installed. Shared builds use --network=default. An environment proxy "
                  "does not prevent direct egress; network=none prevents permitted dependency "
                  "traffic. The accepted shared-default-network path would need daemon/default "
                  "network restriction or a separately authorized isolated enforcement integration.",
        "qualified": False, "machine_global_mutations": 0, "daemon_global_mutations": 0,
        "third_party_installs": 0, "qualification_live_network_requests": 0,
        "allow_probe": "NOT_RUN_UNPROVISIONED", "negative_probe": "TRANSPORT_REJECTION_UNIT_TEST_ONLY",
        "request_provenance": [], "scope_weakened": False}
    save("network_enforcement_qualification.json", result)
    return result


def initialize():
    a.require(not a.OUTPUT_ROOT.exists() and not a.OUTPUT_ROOT.is_symlink(),
              "new namespace must be absent; no silent reuse")
    l.mkdir_durable(a.OUTPUT_ROOT)
    metadata = {"schema": "V6_PERSISTENT_NAMESPACE_V1", "runtime_acceptance_sha256": r.AUTHORITY_SHA,
                "namespace": "IMPLEMENTATION_AND_SYNTHETIC_QUALIFICATION_ONLY",
                "real_attempt_claims": 0, "real_dispatch_authorized": False}
    l.exclusive_write(a.OUTPUT_ROOT / "namespace.json", a.canonical(metadata))
    l.mkdir_durable(Q)
    l.exclusive_write(Q / "namespace.json", a.canonical({"namespace": l.SYNTHETIC}))
    # Empty production ledger directories are namespace structure, never attempt records.
    l.Ledger(a.OUTPUT_ROOT, namespace=l.REAL,
             real_ids=[x["base_attempt_id"] for x in r.population()["items"]]).initialize()


def focused_tests():
    os.environ["ERRPILOT_V6_ACTUAL_FS_QUALIFICATION"] = "YES"
    # unittest's skip flag was set at import time; activate only this explicitly
    # authorized qualification run, never during ordinary tests/import.
    tests.ActualFilesystemTests.__unittest_skip__ = False
    suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    log = stream.getvalue()
    (E / "focused_tests.txt").write_text(log)
    value = {"namespace": l.SYNTHETIC, "tests_run": result.testsRun,
             "failures": len(result.failures), "errors": len(result.errors),
             "skipped": len(result.skipped), "status": "PASS" if result.wasSuccessful() else "FAIL",
             "actual_target_filesystem_root": str(tests.ActualFilesystemTests.root),
             "filesystem_device": a.OUTPUT_ROOT.stat().st_dev,
             "semantics": ["O_EXCL", "file fsync", "parent directory fsync",
                "same-filesystem exclusive hard-link atomic publication", "two-process claim race",
                "partial/orphan/crash preserved", "no automatic reclaim", "no terminal overwrite"]}
    save("persistent_ledger_qualification.json", value)
    return value


def synthetic(base_status, *, fixture_names=("a", "b", "f", "g"), run_label="V1",
              prior_observations=()):
    a.require(all(x["qualification"] == "PASS" for x in base_status), "frozen base qualification required")
    journal = l.Ledger(Q, namespace=l.SYNTHETIC,
                       real_ids=[x["base_attempt_id"] for x in r.population()["items"]])
    journal.initialize()
    observations = list(prior_observations)
    for index, fixture_name in enumerate(fixture_names, 1):
        attempt = f"SYNTHETIC_QUALIFICATION_V6_{run_label}_{index:02d}_{fixture_name.upper()}"
        fixture = load_fixture(fixture_name)
        claim = journal.claim(attempt, {"namespace": l.SYNTHETIC,
              "fixture_sha256": a.identity(fixture), "runtime_acceptance_sha256": r.AUTHORITY_SHA,
              "controller_sha256": a.sha((a.ROOT / r.IMPLEMENTATION[1]).read_bytes())})
        output = Q / "attempts" / attempt
        l.mkdir_durable(output.parent)
        result = r.shared_engine().materialize_synthetic(fixture, output=output)
        hashes = l.persist_tree(output)
        evidence = {"artifact_sha256": hashes, "network_provenance": "NONE",
                    "input_runtime_binding": claim["input_runtime_binding"]}
        if result["status"] == "MATERIALIZED":
            rows = result["revisions"]
            # Synthetic B records both explicitly distinct fixture revisions.
            for key, field in (("dockerfile", "dockerfile_sha256"),
                    ("build_context", "build_context_manifest_sha256"),
                    ("raw_build_log", "build_log_sha256"), ("image_inspection", "image_inspect_sha256"),
                    ("installed_distributions", "installed_distribution_manifest_sha256"),
                    ("environment_identity", "environment_identity_sha256")):
                evidence[key] = a.identity([row[field] for row in rows])
            evidence["source_snapshot_or_absence"] = a.identity([row["source_snapshot_identity"] for row in rows])
            evidence["python_probe"] = a.identity([row["observed_python"] for row in rows])
        terminal = journal.terminal(claim, state=result["status"], evidence=evidence,
                    reason=result.get("reason", ""))
        expected = {"a": "MATERIALIZED", "b": "MATERIALIZED", "f": "BUILD_FAILED", "g": "INTERRUPTED"}[fixture_name]
        observations.append({"namespace": l.SYNTHETIC, "attempt_id": attempt,
             "status": result["status"], "expected": expected, "pass": result["status"] == expected,
             "claim_sha256": a.identity(claim), "terminal_sha256": a.identity(terminal),
             "artifact_sha256": hashes, "revisions": result.get("revisions", [])})
    save("synthetic_materializer_qualification.json", {"namespace": l.SYNTHETIC,
        "status": "PASS" if all(x["pass"] for x in observations) else "FAIL",
        "observations": observations, "restricted_network_build": "NOT_RUN_ENFORCEMENT_BLOCKED",
        "real_image_builds": 0, "real_source_exports": 0, "oracle_runs": 0})
    return observations


def main():
    initialize()
    base_status = bases()
    network_status = network()
    test_status = focused_tests()
    if test_status["status"] == "PASS" and all(x["qualification"] == "PASS" for x in base_status):
        synthetic(base_status)
    save("qualification_results.json", {"status":
        "V6_PREPARATION_EXECUTION_RUNTIME_IMPLEMENTATION_READY_QUALIFICATION_BLOCKED"
        if test_status["status"] == "PASS" else "BLOCKED",
        "ledger": test_status["status"], "network": network_status["status"],
        "base_runtime_pass": sum(x["qualification"] == "PASS" for x in base_status),
        "real_preparation_attempts": 0, "event_3_created": False})
    print(json.dumps({"ledger": test_status, "bases": [
        {k: x[k] for k in ("python_version", "local_status", "qualification", "affected_work_items")}
        for x in base_status], "network": network_status["status"]}))


if __name__ == "__main__":
    main()

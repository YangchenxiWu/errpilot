"""Focused V6 mechanics/rejections; benchmark operations are never invoked."""
from __future__ import annotations

import copy
import os
import subprocess
import sys
import unittest
import uuid
from unittest import mock

from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a
from evaluation.downstream_benchmark.screening import v6_preparation_ledger as l
from evaluation.downstream_benchmark.screening import v6_preparation_runtime as r


class RuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.descriptor, cls.manifest = a.load_inputs()
        cls.population = r.population()
        cls.item = cls.population["items"][0]
        cls.acceptance = a.loads(a.read_exact(r.AUTHORITY, r.AUTHORITY_SHA))
        cls.request = dict(descriptor_path=a.CURRENT, descriptor_sha=a.CURRENT_SHA,
            manifest_path=a.MANIFEST, manifest_sha=a.MANIFEST_SHA,
            ordinal=cls.item["census_order"], case_id=cls.item["case_id"],
            plan_sha=cls.item["plan_sha256"], base_attempt_id=cls.item["base_attempt_id"])

    def test_all_641_projection_identities(self):
        derived = a.derive_population(self.manifest)
        self.assertEqual(derived, self.population)
        self.assertEqual(a.identity(derived), r.POPULATION_SHA)
        for item in derived["items"]:
            a.select(self.manifest, ordinal=item["census_order"],
                     case_id=item["case_id"], plan_sha=item["plan_sha256"])
            snapshot = None if item["variant"] == "SOURCE_INDEPENDENT" else {
                "sha256": "a" * 64, "source_revision_sha": item["source_revision_sha"],
                "source": f"snapshots/{item['base_attempt_id']}"}
            proposal = a.engine_call_proposal(self.manifest, item, snapshot=snapshot)
            self.assertEqual(proposal["fixture"]["revision_label"], item["variant"])
            self.assertEqual(proposal["fixture"]["build_recipe_sha256"], item["engine_recipe_sha256"])
            self.assertEqual(proposal["execution_network"], "NONE")

    def test_exact_selector_rejections(self):
        changes = {"descriptor_path": "latest", "descriptor_sha": "0" * 64,
                   "manifest_path": "scan", "manifest_sha": "0" * 64, "ordinal": True,
                   "case_id": "pandas::0", "plan_sha": "0" * 64,
                   "base_attempt_id": "predecessor-token"}
        for key, value in changes.items():
            with self.subTest(key=key), self.assertRaises(a.Rejected):
                r.select(**{**self.request, key: value})
        for blocked in self.population["blocked"]:
            with self.subTest(case=blocked["case_id"]), self.assertRaises(a.Rejected):
                r.select(**{**self.request, "ordinal": blocked["census_order"],
                    "case_id": blocked["case_id"], "plan_sha": blocked["plan_sha256"]})

    def test_authority_rejections(self):
        r.validate_acceptance(self.acceptance, network_required=True)
        with self.assertRaises(a.Rejected):
            r.validate_acceptance(None, network_required=True)
        for scope in self.acceptance["separate_permissions"]:
            record = copy.deepcopy(self.acceptance)
            del record["separate_permissions"][scope]
            with self.subTest(scope=scope), self.assertRaises(a.Rejected):
                r.validate_acceptance(record, network_required=True)

    def test_policy_and_real_dispatch_default_deny(self):
        for key, value in r.POLICY.items():
            changed = {**r.POLICY, key: "forbidden" if value is None else
                       True if value is False else "latest"}
            with self.subTest(key=key), self.assertRaises(a.Rejected):
                r.preflight(self.request, acceptance=self.acceptance, policy=changed)
        with mock.patch.object(a.shared, "docker", side_effect=AssertionError("Docker forbidden")), \
             mock.patch.object(l.Ledger, "claim", side_effect=AssertionError("real claim forbidden")):
            with self.assertRaises(a.Rejected):
                r.dispatch(self.request, acceptance=self.acceptance, policy=r.POLICY)
        raw = (a.ROOT / a.CURRENT).read_bytes()
        pin = {"path": a.CURRENT, "sha256": a.sha(raw), "HUMAN_PI_ACCEPTED": "YES"}
        with self.assertRaises(a.Rejected):
            r.validate_execution_descriptor(raw, pin, {})
        with self.assertRaises(a.Rejected):
            r.validate_installation({"schema": "BLOCK_03_RUNTIME_ACTIVATION_AUTHORITY_V1"})
        with self.assertRaises(a.Rejected):
            r.request_retry()

    def test_recipe_setup_and_opposite_revision_rejections(self):
        plan = copy.deepcopy(self.manifest["plans"][self.item["census_order"] - 1])
        plan["recipe_candidate"]["setup_actions"].append({"text": "pytest"})
        with self.assertRaises(a.Rejected):
            a.select({"plans": [plan]}, ordinal=1, case_id=plan["case_id"],
                     plan_sha=plan["plan_sha256"])
        plan = self.manifest["plans"][self.item["census_order"] - 1]
        projected = copy.deepcopy(plan)
        projected["recipe_candidate"]["setup_actions"][0]["text"] = "python -m pip install other"
        with self.assertRaises((a.Rejected, a.shared.Blocked)):
            a.engine_recipe(projected)
        resolver = r.source_function(plan, self.item)
        with self.assertRaises(a.Rejected):
            resolver(a.engine_recipe(plan), "FIXED")
        with mock.patch.object(r.snapshots, "_run_git", side_effect=a.Rejected("missing local source")):
            resolver = r.source_function(plan, self.item)
            with self.assertRaises(a.Rejected):
                resolver(a.engine_recipe(plan), self.item["variant"])

    def test_network_and_no_pull_transport(self):
        with self.assertRaises(a.Rejected):
            r.require_network(self.item, {"qualified": True})
        captures = []
        def capture(args, *, timeout=600):
            captures.append(args)
            return subprocess.CompletedProcess(args, 1 if args[0] == "image" else 0, b"[]")
        with mock.patch.object(a.shared, "docker", capture):
            engine = r.shared_engine()
            engine.docker(["run", "--rm", "--network=none", "synthetic-image"])
            self.assertIn("--pull=never", captures[0])
            self.assertIs(engine._materialize_checked.__code__, a.shared._materialize_checked.__code__)
            for argv in (["pull", "image"], ["image", "pull", "image"],
                         ["build", "--network=default"], ["run", "--network=default"],
                         ["run", "--network=none", "--pull=always"],
                         ["build", "--network=none", "--network=host"],
                         ["run", "--network=none", "--network", "default"]):
                with self.subTest(argv=argv), self.assertRaises(a.Rejected):
                    engine.docker(argv)
            with self.assertRaises(a.shared.Blocked):
                engine.verify_base({"base_image_reference": self.item["base_image_reference"],
                    "base_image_digest": self.item["base_image_reference"].split("@", 1)[1]})


@unittest.skipUnless(os.environ.get("ERRPILOT_V6_ACTUAL_FS_QUALIFICATION") == "YES",
                     "requires explicitly authorized actual target filesystem qualification")
class ActualFilesystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = a.OUTPUT_ROOT / "qualification" / ("ledger-" + uuid.uuid4().hex)
        cls.real_ids = [x["base_attempt_id"] for x in r.population()["items"]]
        cls.journal = l.Ledger(cls.root, namespace=l.SYNTHETIC, real_ids=cls.real_ids)
        cls.journal.initialize()

    def attempt(self):
        return "SYNTHETIC_QUALIFICATION_" + uuid.uuid4().hex

    def test_exclusive_claim_terminal_and_immutable_results(self):
        for state in ("MATERIALIZED", "BUILD_FAILED", "BLOCKED_INPUT_IDENTITY", "INTERRUPTED"):
            attempt = self.attempt()
            self.assertEqual(self.journal.state(attempt), "UNSTARTED")
            claim = self.journal.claim(attempt, {"namespace": l.SYNTHETIC})
            with self.assertRaises(a.Rejected):
                self.journal.claim(attempt, {})
            evidence = {k: "a" * 64 for k in l.SUCCESS}
            self.journal.terminal(claim, state=state, evidence=evidence, reason="synthetic observation")
            path = self.journal._path("terminals", attempt)
            raw = path.read_bytes()
            with self.assertRaises(a.Rejected):
                self.journal.terminal(claim, state="MATERIALIZED", evidence=evidence)
            with self.assertRaises(a.Rejected):
                self.journal.claim(attempt, {})
            self.assertEqual(path.read_bytes(), raw)
            self.assertEqual(self.journal.state(attempt), state)

    def test_no_claim_partial_claim_orphan_and_symlink(self):
        with self.assertRaises(a.Rejected):
            self.journal.terminal({"attempt_id": self.attempt()}, state="INTERRUPTED",
                                  evidence={"failure": "synthetic"}, reason="synthetic")
        attempt = self.attempt()
        l.exclusive_write(self.journal._path("claims", attempt), b'{"partial":')
        with self.assertRaises((ValueError, a.Rejected)):
            self.journal.claim(attempt, {})
        attempt = self.attempt()
        l.exclusive_write(self.journal._path("locks", attempt), b"partial lock")
        with self.assertRaises(a.Rejected):
            self.journal.claim(attempt, {})
        attempt = self.attempt()
        path = self.journal._path("claims", attempt)
        path.symlink_to(self.root / "nonexistent")
        with self.assertRaises(a.Rejected):
            self.journal.claim(attempt, {})
        with self.assertRaises(a.Rejected):
            self.journal.claim(self.real_ids[0], {})

    def test_crash_orphan_partial_terminal_and_atomic_nonoverwrite(self):
        attempt = self.attempt()
        claim = self.journal.claim(attempt, {})
        partial = self.journal._path("terminals", attempt).with_suffix(".json.partial.crash")
        l.exclusive_write(partial, b"partial terminal")
        with self.assertRaises(a.Rejected):
            self.journal.claim(attempt, {})
        with self.assertRaises(a.Rejected):
            self.journal.terminal(claim, state="INTERRUPTED", evidence={"crash": "synthetic"},
                                  reason="synthetic crash")
        path = self.root / "atomic-negative.json"
        l.atomic_publish(path, b"first\n")
        with self.assertRaises(FileExistsError):
            l.atomic_publish(path, b"second\n")
        self.assertEqual(path.read_bytes(), b"first\n")

    def test_two_process_claim_race_and_actual_fsync(self):
        attempt = self.attempt()
        code = (
            "import sys; from pathlib import Path; "
            "from evaluation.downstream_benchmark.screening import v6_preparation_ledger as l; "
            "j=l.Ledger(Path(sys.argv[1]),namespace=l.SYNTHETIC); "
            "j.claim(sys.argv[2],{'namespace':l.SYNTHETIC}); print('CLAIMED')"
        )
        children = [subprocess.Popen([sys.executable, "-B", "-c", code, str(self.root), attempt],
                    cwd=a.ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(2)]
        results = [child.communicate() + (child.returncode,) for child in children]
        self.assertEqual(sum(result[2] == 0 for result in results), 1)
        self.assertEqual(self.journal.state(attempt), "CLAIMED_NO_TERMINAL")
        l.fsync_dir(self.root)
        path = self.root / "exclusive-behavior.json"
        l.exclusive_write(path, a.canonical({"namespace": l.SYNTHETIC}))
        with self.assertRaises(FileExistsError):
            l.exclusive_write(path, b"overwrite")

    def test_preserved_safe_symlink_and_fabricated_real_admission(self):
        path = self.root / "synthetic-evidence"
        l.mkdir_durable(path)
        l.exclusive_write(path / "payload", b"fixture-only\n")
        (path / "link").symlink_to("payload")
        hashes = l.persist_tree(path)
        self.assertEqual(set(hashes), {"link", "payload"})
        (path / "escape").symlink_to("../../outside")
        with self.assertRaises(a.shared.Blocked):
            l.persist_tree(path)
        real = l.Ledger(a.OUTPUT_ROOT, namespace=l.REAL, real_ids=self.real_ids)
        item = r.population()["items"][0]
        fabricated = r.Admission({}, {}, item, {})
        before = list((a.OUTPUT_ROOT / "ledger/claims").iterdir())
        with self.assertRaises((a.Rejected, OSError)):
            real.claim(item["base_attempt_id"], {}, permit=fabricated)
        self.assertEqual(list((a.OUTPUT_ROOT / "ledger/claims").iterdir()), before)


if __name__ == "__main__":
    unittest.main()

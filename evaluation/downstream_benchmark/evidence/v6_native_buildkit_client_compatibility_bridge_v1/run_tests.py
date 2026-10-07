"""Focused offline rejection tests and accepted once-only filesystem tests."""
from __future__ import annotations

import copy
import io
import json
import os
import socket
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(OUT))
os.environ["ERRPILOT_V6_ACTUAL_FS_QUALIFICATION"] = "YES"
import bridge as b  # noqa: E402
import guards as g  # noqa: E402
import proxy as p  # noqa: E402
import successor_runtime as successor  # noqa: E402
from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a  # noqa: E402
from evaluation.downstream_benchmark.screening import v6_preparation_ledger as ledger  # noqa: E402
from evaluation.downstream_benchmark.screening import v6_preparation_runtime as runtime  # noqa: E402
from evaluation.downstream_benchmark.tests import test_v6_preparation_runtime as accepted  # noqa: E402

MATRIX = {}


def rejected(name, callback):
    try:
        callback()
    except (ValueError, RuntimeError, a.Rejected):
        MATRIX[name] = "PASS"
        return
    raise AssertionError("not rejected: " + name)


class GuardTests(unittest.TestCase):
    def test_client_and_transport_rejections(self):
        argv = b.load("base_0_solve_observation.json")["argv"]
        g.native_command(argv, argv)
        for name, replace, value in [
            ("wrong_native_buildctl_binary", "/usr/bin/buildctl", "/host/buildctl"),
            ("wrong_daemon", "--addr=unix:///run/buildkit/buildkitd.sock", "--addr=unix:///wrong.sock"),
            ("second_daemon", "--addr=unix:///run/buildkit/buildkitd.sock", "--addr=tcp://second:1234"),
            ("wrong_OCI_store", next(x for x in argv if x.startswith("frozenbase=")), "wrongstore=/tmp/oci"),
            ("wrong_base_transport_mapping", next(x for x in argv if x.startswith("context:")), "context:errpilot_frozen_base=oci-layout://wrong@sha256:" + "0" * 64),
            ("missing_Docker_exporter", next(x for x in argv if x.startswith("type=docker,")), "type=oci,dest=/tmp/wrong.tar"),
        ]:
            changed = [value if x == replace else x for x in argv]
            rejected(name, lambda: g.native_command(changed, argv))
        rejected("Buildx_solve_invocation", lambda: g.command(["docker", "buildx", "build", "."]))
        rejected("old_Buildx_OCI_layout_syntax", lambda: g.command(["docker", "exec", "c", "buildctl", "oci-layout:///tmp/oci"]))
        rejected("network_host", lambda: g.command(["docker", "run", "--network=host", "x"]))

    def test_facts_fail_closed(self):
        facts = b.load("qualification_facts.json")
        g.qualification_facts(facts)
        mapping = {
            "wrong_641_population": ("total", 640), "wrong_583_58_split": ("restricted", 582),
            "config_diffID_drift": ("config_diffids_exact", False),
            "changed_frozen_base_authority": ("frozen_base_authority_unchanged", False),
            "registry_fallback": ("registry_fallback", True), "image_pull_fallback": ("image_pull_fallback", True),
            "missing_docker_load": ("docker_load", False), "output_not_inspectable": ("output_inspectable", False),
            "network_NONE_effective_proxy": ("network_none_no_proxy", False),
            "incomplete_NONE_RUN_binding": ("none_all_RUNs_bound", False),
            "changed_allowlist": ("allowlist", g.ALLOWLIST + ["denied.invalid"]),
            "alternate_pip_index": ("pip_index", "https://denied.invalid/simple"),
            "trusted_host": ("trusted_host", True), "TLS_disabled": ("TLS_verification", False),
            "direct_external_path": ("direct_external_path", True), "blocker_dispatch": ("blocker_dispatch", True),
            "automatic_retry": ("automatic_retry", True), "attempt_identity_regeneration": ("attempt_identity_regeneration", True),
            "source_acquisition": ("source_acquisition", True), "oracle_execution": ("oracle_execution", True),
            "event_3": ("event_3", True), "canonical_mutation": ("canonical_mutation", True),
            "production_client_switch_effectivity_claim": ("production_client_switch_effectivity_claim", True),
        }
        for name, (key, value) in mapping.items():
            with self.subTest(name=name):
                changed = copy.deepcopy(facts)
                changed[key] = value
                rejected(name, lambda: g.qualification_facts(changed))

    def test_network_receipts(self):
        url = b.load("proxy_topology.json")["topology"]["proxy_url"]
        args = {"HTTP_PROXY": url, "HTTPS_PROXY": url, "PIP_INDEX_URL": "https://pypi.org/simple"}
        g.network_binding(required=True, options=[], build_args=args, proxy_url=url, receipt={"fixture": True})
        g.network_binding(required=False, options=["force-network-mode=none"], build_args={}, proxy_url=url, receipt=None)
        rejected("missing_receipt_on_restricted_item", lambda: g.network_binding(required=True, options=[], build_args=args, proxy_url=url, receipt=None))
        rejected("enforcement_receipt_on_NONE_item", lambda: g.network_binding(required=False, options=["force-network-mode=none"], build_args={}, proxy_url=url, receipt={}))
        rejected("wrong_proxy", lambda: g.network_binding(required=True, options=[], build_args={**args, "HTTPS_PROXY": "http://wrong:3128"}, proxy_url=url, receipt={}))

    def test_Dockerfile_transport_only(self):
        _, manifest = a.load_inputs()
        audit = {row["base_attempt_id"]: row for row in b.load("native_network_semantics_audit.json")["items"]}
        identity = b.load("network_enforcement_identity.json")
        proxy_url = b.load("proxy_topology.json")["topology"]["proxy_url"]
        for item in runtime.population()["items"]:
            plan = a.select(manifest, ordinal=item["census_order"], case_id=item["case_id"], plan_sha=item["plan_sha256"])
            recipe = a.engine_recipe(plan)
            original = a.shared.build_definition(recipe, source_present=item["variant"] != "SOURCE_INDEPENDENT",
                dependency_present=a.embedded_inputs(manifest, plan)["dependency_input"] is not None)
            actual = g.execution_dockerfile(original, frozen_base=item["base_image_reference"], restricted=item["build_network_required"])
            row = audit[item["base_attempt_id"]]
            self.assertEqual(a.sha(actual), row["execution_dockerfile_sha256"])
            receipt = {"schema": "V6_RESTRICTED_BUILD_EGRESS_ENFORCEMENT_RECEIPT_CANDIDATE_V1",
                "semantic_enforcement_sha256": identity["semantic_enforcement_sha256"], "base_attempt_id": item["base_attempt_id"],
                "runtime_authority": False} if item["build_network_required"] else None
            compiled = successor.compile_transport(item, plan, proxy_url=proxy_url, enforcement_receipt=receipt)
            self.assertEqual(compiled["execution_dockerfile"], actual)
            self.assertEqual(compiled["base_attempt_id"], item["base_attempt_id"])
            self.assertEqual(compiled["recipe_sha256"], item["recipe_sha256"])
        rejected("incomplete_RUN_network_none_transformation", lambda: g.network_binding(required=False,
            options=[], build_args={}, proxy_url="unused", receipt=None))

    def test_successor_default_deny_and_shared_code(self):
        rejected("successor_real_dispatch", lambda: successor.dispatch({"accepted": True}))
        fake = types.SimpleNamespace(namespace="SYNTHETIC_QUALIFICATION_ONLY", run=mock.Mock())
        transport = successor.NativeDockerTransport(compiled={}, binding={}, layout=b.Q / "base_0/oci",
            artifact_root=b.Q / "candidate-transport-test-unused", runner=fake)
        engine = successor.shared_engine(transport)
        self.assertIs(engine.shared_materializer_code_object, a.shared._materialize_checked.__code__)
        self.assertIs(engine.shared_identity_code_object, a.shared.identity.__code__)
        engine.docker(["run", "--network=none", "synthetic-image"])
        self.assertIn("--pull=never", fake.run.call_args.args[0])
        rejected("successor_real_materializer", lambda: engine._materialize_checked({}, output=a.OUTPUT_ROOT / "attempts/x",
            input_root=a.OUTPUT_ROOT, synthetic_only=False))
        self.assertFalse((b.Q / "candidate-transport-test-unused").exists())

    def test_proxy_authority_before_DNS(self):
        for name, method, authority in [
            ("unapproved_host", "CONNECT", "denied.invalid:443"),
            ("IP_literal", "CONNECT", "127.0.0.1:443"),
            ("alternate_port", "CONNECT", "pypi.org:80"),
            ("userinfo_authority", "CONNECT", "user@pypi.org:443"),
            ("malformed_CONNECT", "CONNECT", "broken"),
            ("ordinary_HTTP_forwarding", "GET", "http://denied.invalid/"),
        ]:
            self.assertIsNone(p.authorize(method, authority, "HTTP/1.1")[0])
            left, right = socket.socketpair()
            try:
                right.sendall((method + " " + authority + " HTTP/1.1\r\n\r\n").encode())
                with mock.patch.object(socket, "getaddrinfo", side_effect=AssertionError("DNS before DENY")), \
                     mock.patch.object(socket.socket, "connect", side_effect=AssertionError("upstream before DENY")), \
                     mock.patch.object(p, "emit") as emit:
                    p.Handler(left, ("local", 0), None)
                self.assertIn(b"403 Forbidden", right.recv(1024))
                self.assertEqual(emit.call_args.args[:1], ("DENY",))
                self.assertFalse(emit.call_args.kwargs["upstream_dns"])
                self.assertFalse(emit.call_args.kwargs["upstream_connect"])
                MATRIX[name] = "PASS"
            finally:
                left.close()
                right.close()
        self.assertEqual(p.authorize("CONNECT", "PYPI.ORG:443", "HTTP/1.1"), ("pypi.org", "ALLOW"))


def setup_synthetic(cls):
    cls.root = b.Q / "ledger-fixtures"
    a.require(not cls.root.exists(), "synthetic ledger no overwrite")
    cls.real_ids = [x["base_attempt_id"] for x in runtime.population()["items"]]
    cls.journal = ledger.Ledger(cls.root, namespace=ledger.SYNTHETIC, real_ids=cls.real_ids)
    cls.journal.initialize()


def main():
    accepted.ActualFilesystemTests.setUpClass = classmethod(setup_synthetic)
    suite = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(cls)
        for cls in [GuardTests, accepted.RuntimeTests, accepted.ActualFilesystemTests]])
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    b.durable(OUT / "focused_tests.txt", stream.getvalue().encode())
    report = {"status": "PASS" if result.wasSuccessful() else "FAIL", "tests_run": result.testsRun,
        "failures": len(result.failures), "errors": len(result.errors), "skips": len(result.skipped),
        "rejection_categories": len(MATRIX), "namespace": ledger.SYNTHETIC, "root": str(b.Q / "ledger-fixtures"),
        "test_source_sha256": b.digest(Path(accepted.__file__)), "real_claims": b.h.attempt_state()["real_ledger_claims"]}
    b.save("rejection_matrix.json", {"status": report["status"], "matrix": MATRIX,
        "scope": "offline guards + real local proxy parser; live fixture rejections recorded separately"})
    b.save("once_only_revalidation.json", report)
    print(json.dumps(report, sort_keys=True))
    a.require(result.wasSuccessful() and not result.skipped, "focused tests failed/skipped")


if __name__ == "__main__":
    main()

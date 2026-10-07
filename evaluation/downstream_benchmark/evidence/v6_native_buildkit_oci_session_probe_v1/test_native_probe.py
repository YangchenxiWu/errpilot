"""Offline rejection tests for the bounded native probe evidence contract."""
from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("native_probe_test_subject", Path(__file__).with_name("native_probe.py"))
n = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n)


class NativeProbeRejections(unittest.TestCase):
    def setUp(self):
        self.endpoint = "unix:///run/buildkit/buildkitd.sock"
        self.argv = n.native_argv(self.endpoint)
        self.facts = {"same_daemon": True, "daemon_count_created": 1, "external_TCP_listener": False,
            "registry_attempts": 0, "registry_pulls": 0, "benchmark_source_copied": False,
            "benchmark_dependency_installs": 0, "event_count": 2, "canonical_modified": False,
            "production_client_switch_claim": False, "native_solve_count": 1}

    def reject_argv(self, token, replacement):
        argv = self.argv.copy()
        argv[argv.index(token)] = replacement
        with self.assertRaises(RuntimeError):
            n.validate_command(argv, self.endpoint)

    def reject_fact(self, key, value):
        facts = copy.deepcopy(self.facts)
        facts[key] = value
        with self.assertRaises(RuntimeError):
            n.validate_execution_facts(facts)

    def test_allowed_native_two_part_registration(self):
        self.assertTrue(n.validate_command(self.argv, self.endpoint))
        self.assertTrue(n.validate_execution_facts(self.facts))

    def test_reject_buildx_solve(self):
        self.reject_argv("buildctl", "buildx")

    def test_reject_old_buildx_oci_syntax(self):
        mapping = "context:errpilot_frozen_base=oci-layout://frozenbase@" + n.TRANSPORT
        self.reject_argv(mapping, "context:errpilot_frozen_base=oci-layout:///absolute/path@" + n.TRANSPORT)

    def test_reject_wrong_store_registration(self):
        self.reject_argv("frozenbase=" + n.CPATH + "/oci", "wrongstore=" + n.CPATH + "/oci")

    def test_reject_wrong_store_mapping(self):
        self.reject_argv("context:errpilot_frozen_base=oci-layout://frozenbase@" + n.TRANSPORT,
                         "context:errpilot_frozen_base=oci-layout://wrongstore@" + n.TRANSPORT)

    def test_reject_wrong_transport_manifest(self):
        self.reject_argv("context:errpilot_frozen_base=oci-layout://frozenbase@" + n.TRANSPORT,
                         "context:errpilot_frozen_base=oci-layout://frozenbase@sha256:" + "0" * 64)

    def test_reject_wrong_daemon_command(self):
        self.reject_argv("--addr=" + self.endpoint, "--addr=unix:///another-daemon.sock")

    def test_reject_wrong_daemon_observation(self):
        self.reject_fact("same_daemon", False)

    def test_reject_second_daemon(self):
        self.reject_fact("daemon_count_created", 2)

    def test_reject_external_tcp_endpoint(self):
        with self.assertRaises(RuntimeError):
            n.native_argv("tcp://0.0.0.0:1234")
        self.reject_fact("external_TCP_listener", True)

    def test_reject_registry_attempt(self):
        self.reject_fact("registry_attempts", 1)
        self.assertTrue(n.registry_lines('do request request.method=HEAD url="https://registry-1.docker.io/v2/library/python/manifests/sha256:123"'))
        self.assertFalse(n.registry_lines('load metadata for oci-layout://frozenbase@sha256:123'))

    def test_reject_pull(self):
        self.reject_fact("registry_pulls", 1)
        self.assertTrue(n.registry_lines("pulling image moby/buildkit"))

    def test_local_OCI_normalized_label_is_distinct_from_registry_request(self):
        ref = "docker.io/library/errpilot_frozen_base@" + n.TRANSPORT
        self.assertFalse(n.registry_lines("#4 resolve " + ref + " done"))
        self.assertFalse(n.registry_lines('level=debug msg=fetch span="resolving ' + ref + '"'))
        self.assertTrue(n.registry_lines("#4 resolve docker.io/library/python@sha256:" + "0" * 64 + " done"))
        self.assertTrue(n.registry_lines('msg="do request" url="https://registry-1.docker.io/v2/" span="resolving ' + ref + '"'))

    def test_reject_benchmark_source_copy(self):
        self.reject_fact("benchmark_source_copied", True)

    def test_reject_benchmark_dependency_install(self):
        self.reject_fact("benchmark_dependency_installs", 1)

    def test_reject_event_three(self):
        self.reject_fact("event_count", 3)

    def test_reject_canonical_mutation(self):
        self.reject_fact("canonical_modified", True)

    def test_reject_production_client_switch_claim(self):
        self.reject_fact("production_client_switch_claim", True)

    def test_reject_fallback_retry(self):
        self.reject_fact("native_solve_count", 2)

    def test_reject_registry_exporter(self):
        self.reject_argv("type=oci,dest=" + n.CPATH + "/output.oci.tar", "type=image,name=example/push,push=true")

    def test_reject_implicit_fixture_network(self):
        self.reject_argv("force-network-mode=none", "force-network-mode=host")

    def test_strict_json_rejects_ambiguous_records(self):
        for raw in [b'{"event_count":2,"event_count":3}', b'{"value":NaN}', b'{"value":"\xff"}']:
            with self.subTest(raw=raw), self.assertRaises((ValueError, UnicodeDecodeError)):
                n.strict_json(raw)

    def test_daemon_logfmt_escaped_quotes_are_decoded(self):
        raw = 'level=info msg="found worker \\"unique-worker\\", platforms=[linux/amd64]"\nlevel=info msg="running server on /run/buildkit/buildkitd.sock"'
        decoded = n.daemon_log_messages(raw)
        self.assertIn('found worker "unique-worker"', decoded)
        self.assertTrue(decoded.endswith("running server on /run/buildkit/buildkitd.sock"))


if __name__ == "__main__":
    unittest.main(verbosity=2)

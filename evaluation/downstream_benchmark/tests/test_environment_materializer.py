"""Synthetic-only authority, identity, and Docker checks for materializer v1."""

from __future__ import annotations

import ast
import inspect
import json
import os
import runpy
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evaluation.downstream_benchmark.screening import materializer as m


def fixture(name: str) -> dict:
    data = json.loads((m.FIXTURES / f"fixture_{name.lower()}.json").read_text())
    if "extends" in data:
        base = json.loads((m.FIXTURES / data.pop("extends")).read_text())
        base.update(data)
        if base.pop("mutate", None) == "recipe_hash":
            base["build_recipe_sha256"] = "0" * 64
        elif name == "e":
            base["setup_input"] = "setup_e.txt"
            base["recipe"]["setup_sha256"] = m.sha256((m.FIXTURES / "setup_e.txt").read_bytes())
            base["recipe"]["setup_actions"][0]["exact_source_text"] = "touch x; echo unsafe"
            base["recipe"]["setup_action_ledger_sha256"] = m.sha256(
                m.canonical_json(base["recipe"]["setup_actions"]))
            base["build_recipe_sha256"] = m.recipe_hash(base["recipe"])
        return base
    return data


class AuthorityTests(unittest.TestCase):
    def test_bare_invocation_prints_help_and_fails(self) -> None:
        self.assertEqual(m.main([]), 2)

    def test_plan_and_validate_have_no_docker_path(self) -> None:
        with patch.object(m, "docker", side_effect=AssertionError("Docker was called")):
            self.assertEqual(m.main(["validate"]), 0)
            self.assertEqual(m.main(["plan"]), 0)

    def test_real_materialize_requires_exact_token_and_explicit_inputs(self) -> None:
        with patch.object(m, "docker", side_effect=AssertionError("Docker was called")):
            self.assertEqual(m.main(["materialize", "--authority-token", "wrong"]), 1)
            self.assertEqual(m.main(["materialize", "--authority-token", m.AUTHORITY_TOKEN]), 1)
        self.assertTrue(m.REAL_MATERIALIZATION_ENABLED)
        self.assertEqual(m.MATERIALIZER_VERSION, "ENVIRONMENT_MATERIALIZER_V1_3")

    def test_frozen_ledger_is_ready_and_unbuilt(self) -> None:
        self.assertEqual(len(m.check_frozen_ledger()), 40)

    def test_recipe_hash_mismatch_blocks_before_docker(self) -> None:
        with tempfile.TemporaryDirectory() as temp, patch.object(
                m, "docker", side_effect=AssertionError("Docker was called")):
            result = m.materialize_synthetic(fixture("c"), output=Path(temp) / "c")
        self.assertEqual(result["status"], "BLOCKED_INPUT_IDENTITY")

    def test_dependency_hash_mismatch_blocks(self) -> None:
        data = fixture("a")
        data["recipe"]["dependency_input_sha256"] = "0" * 64
        data["build_recipe_sha256"] = m.recipe_hash(data["recipe"])
        with tempfile.TemporaryDirectory() as temp, patch.object(
                m, "docker", side_effect=AssertionError("Docker was called")):
            result = m.materialize_synthetic(data, output=Path(temp) / "hash")
        self.assertEqual(result["status"], "BLOCKED_INPUT_IDENTITY")

    def test_base_digest_mismatch_blocks(self) -> None:
        data = fixture("a")
        data["recipe"]["base_image_digest"] = "sha256:" + "0" * 64
        data["build_recipe_sha256"] = m.recipe_hash(data["recipe"])
        with tempfile.TemporaryDirectory() as temp, patch.object(
                m, "docker", side_effect=AssertionError("Docker was called")):
            result = m.materialize_synthetic(data, output=Path(temp) / "digest")
        self.assertEqual(result["status"], "BLOCKED_RUNTIME_IDENTITY")

    def test_python_mismatch_simulation_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp, patch.object(
                m, "docker", side_effect=AssertionError("Docker was called")):
            result = m.materialize_synthetic(fixture("d"), output=Path(temp) / "python")
        self.assertEqual(result["status"], "BLOCKED_RUNTIME_IDENTITY")

    def test_setup_action_order_preserved(self) -> None:
        data = fixture("a")["recipe"]
        data["setup_actions"] = [
            {"classification": "DEPENDENCY_INSTALL", "exact_source_text": "pip install alpha"},
            {"classification": "DEPENDENCY_INSTALL", "exact_source_text": "pip install beta"},
        ]
        definition = m.build_definition(data, source_present=False, dependency_present=True)
        self.assertLess(definition.index(b"alpha"), definition.index(b"beta"))

    def test_unsupported_action_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp, patch.object(m, "verify_base", return_value={}):
            result = m.materialize_synthetic(fixture("e"), output=Path(temp) / "unsupported")
        self.assertEqual(result["status"], "BLOCKED_UNSUPPORTED_ACTION")

    def test_source_independent_build_excludes_subject_source(self) -> None:
        data = fixture("a")["recipe"]
        definition = m.build_definition(data, source_present=False, dependency_present=True)
        self.assertNotIn(b"COPY source", definition)
        self.assertNotIn(b"WORKDIR /subject", definition)

    def test_revision_specific_requires_explicit_snapshot(self) -> None:
        data = fixture("b")
        data["revisions"][0].pop("source")
        with tempfile.TemporaryDirectory() as temp, patch.object(m, "verify_base", return_value={}):
            result = m.materialize_synthetic(data, output=Path(temp) / "missing")
        self.assertEqual(result["status"], "BLOCKED_INPUT_IDENTITY")

    def test_buggy_and_fixed_snapshot_hashes_differ(self) -> None:
        data = fixture("b")
        self.assertNotEqual(data["revisions"][0]["sha"], data["revisions"][1]["sha"])
        self.assertEqual([r["label"] for r in data["revisions"]], ["BUGGY", "FIXED"])

    def test_identity_uses_observed_values_and_canonical_hash(self) -> None:
        recipe = fixture("a")["recipe"]
        image_id = "sha256:" + "a" * 64
        evidence = {"inspect": {"Id": image_id}, "python": {
            "version": "3.8.3", "executable_sha256": "b" * 64},
            "distributions": b"[]\n", "distribution_probe": {"backend":
                "STDLIB_IMPORTLIB_METADATA"}, "system_packages": b"package 1\n",
            "layers": ["sha256:" + "c" * 64], "network": False}
        identity = m.identity(recipe, "SOURCE_INDEPENDENT", "ABSENT", evidence, "ABSENT")
        self.assertEqual(identity["environment_image_digest"], image_id)
        self.assertEqual(identity["python_executable_sha256"], "b" * 64)
        self.assertNotIn("UNBUILT", identity.values())
        self.assertEqual(len(m.sha256(m.canonical_json(identity))), 64)

    def test_build_failure_is_infrastructure_and_no_retry(self) -> None:
        calls: list[list[str]] = []
        def fake_docker(args: list[str], **_: object) -> subprocess.CompletedProcess[bytes]:
            calls.append(args)
            return subprocess.CompletedProcess(args, 1, b"deterministic build failure")
        with tempfile.TemporaryDirectory() as temp, patch.object(m, "verify_base", return_value={}), \
                patch.object(m, "docker", side_effect=fake_docker):
            result = m.materialize_synthetic(fixture("a"), output=Path(temp) / "failed")
            self.assertTrue((Path(temp) / "failed" / "SOURCE_INDEPENDENT" / "build.log").exists())
        self.assertEqual(result["status"], "BUILD_FAILED")
        self.assertEqual(len([c for c in calls if c[0] == "build"]), 1)
        self.assertNotIn("eligibility", result)

    def test_interruption_never_materialized(self) -> None:
        with tempfile.TemporaryDirectory() as temp, patch.object(
                m, "docker", side_effect=AssertionError("Docker was called")):
            result = m.materialize_synthetic(fixture("g"), output=Path(temp) / "interrupted")
        self.assertEqual(result["status"], "INTERRUPTED")

    def test_execution_network_none_and_mutable_tag_not_identity(self) -> None:
        data = fixture("a")["recipe"]
        self.assertEqual(data["future_network_execution_policy"], "NONE")
        self.assertNotIn("tag", m.ENVIRONMENT_IDENTITY_V1_FIELDS)
        self.assertEqual(m.PLATFORM, "linux/amd64")

    def test_no_oracle_repair_or_model_invocation(self) -> None:
        tree = ast.parse(Path(m.__file__).read_text())
        imported = {alias.name for node in ast.walk(tree) if isinstance(node, (ast.Import,
                    ast.ImportFrom)) for alias in node.names}
        self.assertFalse({"openai", "anthropic", "errpilot"} & imported)
        self.assertNotIn("run_oracle_process", Path(m.__file__).read_text())


class DistributionProbeV2Tests(unittest.TestCase):
    def test_backend_selection_for_36_37_38(self) -> None:
        self.assertEqual(m.distribution_backend("3.6.9"), "PIP_LIST_JSON")
        self.assertEqual(m.distribution_backend("3.7.3"), "PIP_LIST_JSON")
        self.assertEqual(m.distribution_backend("3.8.3"), "STDLIB_IMPORTLIB_METADATA")

    def test_pip_canonicalization_ignores_input_order(self) -> None:
        a = b'[{"name":"Zoo_Pkg","version":"2"},{"name":"alpha.pkg","version":"1"}]'
        b = b'[{"version":"1","name":"alpha.pkg"},{"version":"2","name":"Zoo_Pkg"}]'
        expected = [["alpha.pkg", "1"], ["Zoo_Pkg", "2"]]
        self.assertEqual(m.canonical_distribution_manifest(a, "PIP_LIST_JSON"),
                         m.canonical_json(expected))
        self.assertEqual(m.canonical_distribution_manifest(a, "PIP_LIST_JSON"),
                         m.canonical_distribution_manifest(b, "PIP_LIST_JSON"))

    def test_bad_json_or_missing_fields_blocks(self) -> None:
        for raw in (b"{", b"{}", b'[{"name":"a"}]', b'[{"version":"1"}]',
                    b'[{"name":"","version":"1"}]',
                    b'[{"name":"a","version":""}]',
                    b'[{"name":"a","name":"b","version":"1"}]'):
            with self.subTest(raw=raw), self.assertRaises(m.Blocked):
                m.canonical_distribution_manifest(raw, "PIP_LIST_JSON")

    def test_probe_failure_blocks_without_fallback(self) -> None:
        calls: list[list[str]] = []
        def fail(args: list[str], **_: object) -> subprocess.CompletedProcess[bytes]:
            calls.append(args)
            return subprocess.CompletedProcess(args, 1, b"", b"pip unavailable")
        with patch.object(m, "docker_observation", side_effect=fail):
            with self.assertRaises(m.Blocked) as result:
                m.probe_distributions("sha256:" + "a" * 64, "3.7.3")
        self.assertEqual(result.exception.status, "BLOCKED_RUNTIME_IDENTITY")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][-4:], ["-m", "pip", "list", "--format=json"])

    def test_failed_probe_preserves_raw_streams_and_backend(self) -> None:
        image_id = "sha256:" + "a" * 64
        def fake_docker(args: list[str], **_: object) -> subprocess.CompletedProcess[bytes]:
            if args[0] == "build":
                return subprocess.CompletedProcess(args, 0, b"build succeeded")
            if args[:2] == ["image", "inspect"]:
                return subprocess.CompletedProcess(args, 0,
                    json.dumps([{"Id": image_id}]).encode())
            raise AssertionError("unexpected Docker operation")
        failure = m.ProbeBlocked("pip unavailable", backend="PIP_LIST_JSON",
            command=["docker", "run"], stdout=b"raw out", stderr=b"raw err", exit_code=1)
        with tempfile.TemporaryDirectory() as temp, \
                patch.object(m, "verify_base", return_value={}), \
                patch.object(m, "docker", side_effect=fake_docker), \
                patch.object(m, "inspect_final", side_effect=failure):
            root = Path(temp) / "probe-failure"
            record = m.materialize_synthetic(fixture("a"), output=root)
            revision = root / "SOURCE_INDEPENDENT"
            self.assertEqual((revision / "distribution_probe.stdout").read_bytes(), b"raw out")
            self.assertEqual((revision / "distribution_probe.stderr").read_bytes(), b"raw err")
        self.assertEqual(record["status"], "BLOCKED_RUNTIME_IDENTITY")
        self.assertEqual(record["revisions"][0]["distribution_probe_backend"], "PIP_LIST_JSON")
        self.assertEqual(record["revisions"][0]["distribution_probe_stdout_sha256"],
                         m.sha256(b"raw out"))

    def test_probe_evidence_and_nonmutating_commands(self) -> None:
        calls: list[list[str]] = []
        def observe(args: list[str], **_: object) -> subprocess.CompletedProcess[bytes]:
            calls.append(args)
            return subprocess.CompletedProcess(args, 0,
                                               b'[{"name":"example","version":"1"}]', b"notice")
        with patch.object(m, "docker_observation", side_effect=observe):
            result = m.probe_distributions("sha256:" + "a" * 64, "3.7.3")
        self.assertEqual(result["backend"], "PIP_LIST_JSON")
        self.assertEqual(result["stderr"], b"notice")
        self.assertEqual(result["manifest"], b'[["example","1"]]\n')
        self.assertIn("--network=none", calls[0])
        self.assertIn("--read-only", calls[0])
        self.assertNotIn("install", calls[0])
        self.assertNotIn("subject", inspect.getsource(m.probe_distributions).lower())

    def test_historical_batch_01_unchanged(self) -> None:
        benchmark = m.BENCHMARK
        self.assertEqual(m.sha256((benchmark / "environment_materialization_batch_01.csv").read_bytes()),
                         "d898ee0bb6d26f6b46ad387292a39df93d438e683947ff6500229b0922a1088b")
        self.assertEqual(m.sha256((benchmark / "ENVIRONMENT_MATERIALIZATION_BATCH_01.md").read_bytes()),
                         "184fa568a6cb59685047f868799fcd012869d53d5a7409cbc8d3af68fc665f13")

    def test_completion_rejects_mismatched_image_without_build(self) -> None:
        attempt = {"status": "BLOCKED_RUNTIME_IDENTITY", "attempt_id": "batch01_10_keras_28",
                   "revisions": [{"canonical_case_id": "keras::28", "build_exit_code": 0,
                                  "build_command": ["docker", "build"]}]}
        with patch.object(m, "docker", side_effect=AssertionError("Docker called")):
            with self.assertRaises(m.Blocked):
                m.complete_existing_identity("sha256:" + "a" * 64, attempt,
                                             {"Id": "sha256:" + "b" * 64},
                                             {"canonical_case_id": "keras::28"})
        source = inspect.getsource(m.complete_existing_identity)
        self.assertNotIn('docker(["build"', source)


class ProductionGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.docker_guard = patch.object(m, "docker", side_effect=AssertionError("Docker was called"))
        self.docker_guard.start()
        self.addCleanup(self.docker_guard.stop)
        recipe = m.check_frozen_ledger()[0]
        case_id = recipe["canonical_case_id"]
        ledger = [row for row in m.read_rows(m.BENCHMARK / "self_reference_ledger.csv")
                  if row["canonical_case_id"] == case_id]
        self.request = {"canonical_case_id": case_id,
                        "build_recipe_sha256": m.recipe_hash(recipe),
                        "self_reference_ledger": ledger}

    def invoke(self, request: dict, *, clean: bool = True) -> dict:
        with patch.object(m, "materializer_commit", return_value="a" * 40), \
                patch.object(m, "materializer_git_clean", return_value=clean), \
                patch.object(m, "_materialize_checked",
                             side_effect=AssertionError("Build engine was entered")):
            return m.materialize_real_request(request, authority_token=m.AUTHORITY_TOKEN,
                                              output=Path("unused-output"),
                                              input_root=Path("unused-input"))

    def test_import_and_token_constant_have_no_execution_side_effect(self) -> None:
        with patch("subprocess.run", side_effect=AssertionError("Subprocess was called")):
            runpy.run_path(str(Path(m.__file__)), run_name="materializer_import_probe")
        self.assertEqual(m.AUTHORITY_TOKEN,
                         "BUGSINPY_ENVIRONMENT_MATERIALIZATION_AUTHORIZED_V1")

    def test_missing_or_wrong_token_blocks(self) -> None:
        for token in ("", "wrong"):
            with self.subTest(token=token), patch.object(
                    m, "_materialize_checked", side_effect=AssertionError("Build engine was entered")):
                with self.assertRaises(m.Blocked) as blocked:
                    m.materialize_real_request(self.request, authority_token=token,
                                               output=Path("unused-output"),
                                               input_root=Path("unused-input"))
                self.assertEqual(blocked.exception.status, "BLOCKED_AUTHORITY")

    def test_missing_request_input_or_output_blocks_at_cli(self) -> None:
        full = ["--request", "unused-request", "--input-root", "unused-input",
                "--output", "unused-output"]
        for omitted in ("--request", "--input-root", "--output"):
            with self.subTest(omitted=omitted):
                args = full.copy()
                index = args.index(omitted)
                del args[index:index + 2]
                self.assertEqual(m.main(["materialize", "--authority-token",
                                         m.AUTHORITY_TOKEN, *args]), 1)

    def test_case_outside_frozen_initial_40_blocks(self) -> None:
        request = {**self.request, "canonical_case_id": "OUTSIDE_FROZEN_40"}
        with self.assertRaises(m.Blocked) as blocked:
            self.invoke(request)
        self.assertEqual(blocked.exception.status, "BLOCKED_INPUT_IDENTITY")

    def test_frozen_recipe_hash_mismatch_blocks(self) -> None:
        request = {**self.request, "build_recipe_sha256": "0" * 64}
        with self.assertRaises(m.Blocked) as blocked:
            self.invoke(request)
        self.assertEqual(blocked.exception.status, "BLOCKED_INPUT_IDENTITY")

    def test_self_reference_ledger_mismatch_blocks(self) -> None:
        request = {**self.request, "self_reference_ledger": [{"changed": "true"}]}
        with self.assertRaises(m.Blocked) as blocked:
            self.invoke(request)
        self.assertEqual(blocked.exception.status, "BLOCKED_INPUT_IDENTITY")

    def test_dirty_materializer_checkout_blocks(self) -> None:
        with self.assertRaises(m.Blocked) as blocked:
            self.invoke(self.request, clean=False)
        self.assertEqual(blocked.exception.status, "BLOCKED_INPUT_IDENTITY")

    def test_one_explicit_request_does_not_enumerate_batch(self) -> None:
        with patch.object(m, "materializer_commit", return_value="a" * 40), \
                patch.object(m, "materializer_git_clean", return_value=True), \
                patch.object(m, "_materialize_checked",
                             return_value={"status": "MATERIALIZED"}) as build:
            m.materialize_real_request(self.request, authority_token=m.AUTHORITY_TOKEN,
                                       output=Path("unused-output"),
                                       input_root=Path("unused-input"))
        build.assert_called_once()
        self.assertEqual(build.call_args.args[0]["canonical_case_id"],
                         self.request["canonical_case_id"])

    def test_synthetic_entrypoint_rejects_real_case_and_alternate_root(self) -> None:
        data = fixture("a")
        data["recipe"]["canonical_case_id"] = self.request["canonical_case_id"]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            result = m.materialize_synthetic(data, output=root / "real-case")
            self.assertEqual(result["status"], "BLOCKED_INPUT_IDENTITY")
            result = m.materialize_synthetic(fixture("a"), output=root / "wrong-root",
                                             fixture_root=root)
            self.assertEqual(result["status"], "BLOCKED_INPUT_IDENTITY")


@unittest.skipUnless(os.environ.get("MATERIALIZER_DOCKER_TESTS") == "1", "explicit Docker validation")
class SyntheticDockerTests(unittest.TestCase):
    def test_a_b_f_and_repeat_a(self) -> None:
        with tempfile.TemporaryDirectory(prefix="errpilot-materializer-test-") as temp:
            root = Path(temp)
            results = {name: m.materialize_synthetic(fixture(name), output=root / name)
                       for name in ("a", "b", "f", "a_repeat") if name != "a_repeat"}
            results["a_repeat"] = m.materialize_synthetic(fixture("a"),
                                                             output=root / "a_repeat")
            self.assertEqual(results["a"]["status"], "MATERIALIZED")
            self.assertEqual(results["b"]["status"], "MATERIALIZED")
            self.assertEqual(results["f"]["status"], "BUILD_FAILED")
            self.assertEqual(results["a"]["build_recipe_sha256"],
                             results["a_repeat"]["build_recipe_sha256"])
            self.assertNotEqual(results["b"]["revisions"][0]["final_image_id"],
                                results["b"]["revisions"][1]["final_image_id"])
            for name, label in (("a", "SOURCE_INDEPENDENT"), ("b", "BUGGY"), ("b", "FIXED")):
                entry = results[name]["revisions"][0 if label != "FIXED" else 1]
                ident = json.loads((root / name / label / "environment_identity.json").read_text())
                self.assertEqual(ident["environment_image_digest"], entry["final_image_id"])
                run = m.docker(["run", "--rm", "--platform=linux/amd64", "--network=none",
                                "--read-only", "--tmpfs", "/tmp", "--tmpfs", "/home",
                                "-e", "HOME=/home", entry["final_image_id"], "python", "-c",
                                "print('synthetic-identity-ok')"])
                self.assertEqual(run.returncode, 0)
                self.assertIn(b"synthetic-identity-ok", run.stdout)

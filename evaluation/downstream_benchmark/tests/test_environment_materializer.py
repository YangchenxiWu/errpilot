"""Synthetic-only authority, identity, and Docker checks for materializer v1."""

from __future__ import annotations

import ast
import json
import os
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

    def test_real_materialize_requires_exact_token_and_remains_closed(self) -> None:
        with patch.object(m, "docker", side_effect=AssertionError("Docker was called")):
            self.assertEqual(m.main(["materialize", "--authority-token", "wrong"]), 1)
            self.assertEqual(m.main(["materialize", "--authority-token", m.AUTHORITY_TOKEN]), 1)
        self.assertFalse(m.REAL_MATERIALIZATION_ENABLED)

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
            "distributions": b"[]\n", "system_packages": b"package 1\n",
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

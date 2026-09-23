"""Synthetic and ledger checks for the data-only build recipe transaction."""

from __future__ import annotations

import ast
import csv
import json
import unittest
from pathlib import Path

from evaluation.downstream_benchmark.screening import build_recipes as recipes
from evaluation.downstream_benchmark.screening import probe_base_runtimes


BENCHMARK = Path(__file__).resolve().parents[1]


class RequirementsTests(unittest.TestCase):
    def test_utf8_normalization_is_deterministic(self) -> None:
        raw = b"alpha==1\r\nbeta==2\r"
        self.assertEqual(recipes.normalize_requirements(raw), (b"alpha==1\nbeta==2\n", "UTF-8"))
        self.assertEqual(recipes.normalize_requirements(raw), recipes.normalize_requirements(raw))

    def test_utf16_le_bom(self) -> None:
        self.assertEqual(recipes.normalize_requirements(b"\xff\xfe" + "a==1\r\n".encode("utf-16-le")),
                         (b"a==1\n", "UTF-16_WITH_BOM"))

    def test_utf16_be_bom(self) -> None:
        self.assertEqual(recipes.normalize_requirements(b"\xfe\xff" + "a==1\r".encode("utf-16-be")),
                         (b"a==1\n", "UTF-16_WITH_BOM"))

    def test_malformed_utf16_blocks(self) -> None:
        with self.assertRaises(UnicodeError):
            recipes.normalize_requirements(b"\xff\xfea")

    def test_no_replacement_character(self) -> None:
        with self.assertRaises(UnicodeError):
            recipes.normalize_requirements(b"\xffbroken")

    def test_only_line_endings_change(self) -> None:
        raw = b"  a==1  \r\n# keep comment\r\r\n\tb==2"
        self.assertEqual(recipes.normalize_requirements(raw)[0], b"  a==1  \n# keep comment\n\n\tb==2")

    def test_self_vcs_is_omitted(self) -> None:
        raw = b"-e git+https://github.com/org/demo.git@abcdef#egg=demo\nother==1\n"
        derived, ledger = recipes.derive_dependency_input(
            raw, case_id="demo::1", project="demo", source_url="https://github.com/org/demo")
        self.assertEqual(derived, b"other==1\n")
        self.assertEqual(ledger[0]["classification"], "SELF_VCS_REFERENCE")
        self.assertEqual(ledger[0]["original_line_ordinal"], "1")

    def test_self_package_pin_is_omitted(self) -> None:
        derived, ledger = recipes.derive_dependency_input(
            b"Demo==1.0\nother==2", case_id="demo::1", project="demo",
            source_url="https://github.com/org/demo")
        self.assertEqual(derived, b"other==2")
        self.assertEqual(ledger[0]["classification"], "SELF_PACKAGE_PIN")

    def test_unrelated_dependency_unchanged(self) -> None:
        raw = b"demo-tools==1\n # a comment\n  other==2  \n"
        derived, ledger = recipes.derive_dependency_input(
            raw, case_id="demo::1", project="demo", source_url="https://github.com/org/demo")
        self.assertEqual((derived, ledger), (raw, []))

    def test_ambiguous_apparent_self_blocks(self) -> None:
        with self.assertRaises(recipes.RecipeError):
            recipes.derive_dependency_input(
                b"-e git+https://github.com/org/demo@abc#egg=other\n",
                case_id="demo::1", project="demo", source_url="https://github.com/org/demo")


class RecipeTests(unittest.TestCase):
    def test_self_omission_can_be_source_independent(self) -> None:
        derived, ledger = recipes.derive_dependency_input(
            b"demo==1\n", case_id="demo::1", project="demo",
            source_url="https://github.com/org/demo")
        self.assertEqual((derived, len(ledger), recipes.environment_mode([])),
                         (b"", 1, "SOURCE_INDEPENDENT_ENVIRONMENT"))

    def test_project_install_is_revision_specific(self) -> None:
        actions = recipes.setup_actions(b"python setup.py install\n", '[{"line":1,"category":"PROJECT_INSTALL_OR_BUILD","text":"python setup.py install"}]')
        self.assertEqual(recipes.environment_mode(actions), "REVISION_SPECIFIC_BUILD_REQUIRED")
        self.assertTrue(actions[0]["consumes_subject_source"])

    def test_recipe_hash_is_deterministic(self) -> None:
        recipe = {"case": "demo::1", "base": "sha256:a"}
        self.assertEqual(recipes.recipe_hash(recipe), recipes.recipe_hash(dict(reversed(list(recipe.items())))))

    def test_timestamp_does_not_enter_recipe_hash(self) -> None:
        base = {"case": "demo::1"}
        self.assertEqual(recipes.recipe_hash(base), recipes.recipe_hash({**base, "timestamp": "any time"}))

    def test_no_materialization_identity_is_fabricated(self) -> None:
        with (BENCHMARK / "environment_build_recipes.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 40)
        for row in rows:
            recipe = json.loads(row["build_recipe_json"])
            self.assertEqual(recipe["materialization_identity"], "UNBUILT")
            self.assertNotIn("environment_image_digest", recipe)
            self.assertEqual(row["build_recipe_sha256"], recipes.recipe_hash(recipe))

    def test_new_helpers_have_no_subject_execution_path(self) -> None:
        source = (BENCHMARK / "screening" / "build_recipes.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = {alias.name for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))
                    for alias in node.names}
        self.assertFalse({"subprocess", "docker", "pytest"} & imported)
        called = {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call)
                  and isinstance(node.func, ast.Name)}
        self.assertFalse({"exec", "eval", "system", "run_test", "run_oracle_process"} & called)
        probe_source = (BENCHMARK / "screening" / "probe_base_runtimes.py").read_text(encoding="utf-8")
        self.assertNotIn("run_test.sh", probe_source)
        self.assertNotIn("--mount", probe_source)
        self.assertNotIn("--volume", probe_source)
        self.assertEqual(probe_source.count("subprocess.run("), 2)
        self.assertEqual(
            {name for name in ("hashlib", "json", "platform", "sys") if name in probe_base_runtimes.PROBE_CODE},
            {"hashlib", "json", "platform", "sys"},
        )


if __name__ == "__main__":
    unittest.main()

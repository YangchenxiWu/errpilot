from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from evaluation.downstream_benchmark.screening import executor


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ("git", "-C", str(repo), *args),
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def commit_file(repo: Path, path: str, content: str, message: str) -> str:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    git(repo, "add", path)
    git(
        repo,
        "-c",
        "user.name=Screening Test",
        "-c",
        "user.email=screening@example.invalid",
        "commit",
        "-m",
        message,
    )
    return git(repo, "rev-parse", "HEAD")


class ScreeningExecutorTests(unittest.TestCase):
    def make_repo(self, root: Path) -> tuple[Path, str, str]:
        repo = root / "subject"
        repo.mkdir()
        subprocess.run(("git", "init", "-q", str(repo)), check=True)
        buggy = commit_file(repo, "tests/test_subject.py", "VALUE = 1\n", "first")
        fixed = commit_file(repo, "subject.py", "VALUE = 2\n", "second")
        return repo, buggy, fixed

    def test_bare_default_cannot_run_oracle(self) -> None:
        with mock.patch.object(executor, "execute_case") as execute:
            self.assertEqual(executor.main([]), 2)
        execute.assert_not_called()

    def test_preparation_resolves_full_and_abbreviated_identities(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo, buggy, fixed = self.make_repo(Path(temporary))
            self.assertEqual(executor.resolve_revision(repo, buggy[:10]), buggy)
            self.assertEqual(executor.resolve_revision(repo, fixed), fixed)

    def test_case_preparation_is_static_and_writes_resolved_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo, buggy, fixed = self.make_repo(root)
            bugsinpy = root / "bugsinpy"
            metadata = bugsinpy / "projects" / "demo" / "bugs" / "1"
            metadata.mkdir(parents=True)
            (metadata.parent.parent / "project.info").write_text(
                'github_url="local"\nstatus="OK"\n', encoding="utf-8"
            )
            (metadata / "bug.info").write_text(
                'python_version="3.11"\n'
                f'buggy_commit_id="{buggy[:12]}"\n'
                f'fixed_commit_id="{fixed}"\n'
                'test_file="tests/test_subject.py"\n',
                encoding="utf-8",
            )
            oracle_bytes = b"pytest tests/test_subject.py::test_value\n"
            (metadata / "run_test.sh").write_bytes(oracle_bytes)
            (metadata / "requirements.txt").write_bytes(b"")
            framework_bin = bugsinpy / "framework" / "bin"
            framework_bin.mkdir(parents=True)
            (framework_bin / "bugsinpy-test").write_text("framework data\n", encoding="utf-8")
            (framework_bin / "bugsinpy-compile").write_text("framework data\n", encoding="utf-8")
            candidate = executor.Candidate(
                candidate_rank=1,
                selection_order=1,
                canonical_case_id="demo::1",
                project="demo",
                bug_id="1",
                source_url="local",
                python_version="3.11",
                buggy_revision=buggy[:12],
                fixed_revision=fixed,
                declared_test_file="tests/test_subject.py",
                bugsinpy_source_commit=executor.BUGSINPY_COMMIT,
            )
            with mock.patch("subprocess.run", wraps=subprocess.run) as run:
                row = executor.prepare_case(
                    candidate,
                    bugsinpy_root=bugsinpy,
                    external_root=root / "external",
                    mirror=repo,
                )
            invoked = [call.args[0] for call in run.call_args_list]
            self.assertFalse(
                any(command and command[0] in {"pytest", "py.test"} for command in invoked)
            )
            self.assertEqual(row["buggy_commit_full"], buggy)
            self.assertEqual(row["fixed_commit_full"], fixed)
            self.assertEqual(row["screening_ready"], "true")
            saved = (
                root
                / "external"
                / "screening_workspaces"
                / "demo-1"
                / "preparation"
                / "oracle"
                / "run_test.sh"
            )
            self.assertEqual(saved.read_bytes(), oracle_bytes)

    def test_abbreviated_resolution_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo, buggy, _ = self.make_repo(Path(temporary))
            values = [executor.resolve_revision(repo, buggy[:12]) for _ in range(3)]
            self.assertEqual(values, [buggy, buggy, buggy])

    def test_ambiguous_revision_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo, _, _ = self.make_repo(Path(temporary))
            with mock.patch.object(
                executor,
                "_git",
                side_effect=[
                    subprocess.CompletedProcess([], 0, "a" * 40 + "\n" + "b" * 40 + "\n", ""),
                    subprocess.CompletedProcess([], 0, "commit\n", ""),
                    subprocess.CompletedProcess([], 0, "commit\n", ""),
                ],
            ):
                with self.assertRaises(executor.RevisionResolutionError):
                    executor.resolve_revision(repo, "abcdef0")

    def test_protected_manifest_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo, buggy, fixed = self.make_repo(Path(temporary))
            candidate = executor.Candidate(
                candidate_rank=1,
                selection_order=1,
                canonical_case_id="demo::1",
                project="demo",
                bug_id="1",
                source_url="local",
                python_version="3.11",
                buggy_revision=buggy,
                fixed_revision=fixed,
                declared_test_file="tests/test_subject.py",
                bugsinpy_source_commit=executor.BUGSINPY_COMMIT,
            )
            command = ["pytest tests/test_subject.py::test_value"]
            first = executor.build_protected_manifest(candidate, repo, buggy, fixed, command)
            second = executor.build_protected_manifest(candidate, repo, buggy, fixed, command)
            self.assertEqual(first, second)
            self.assertEqual(first["status"], "RESOLVED")
            self.assertEqual(len(first["entries"]), 1)

    def test_missing_buggy_test_uses_frozen_fixed_test_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "subject"
            repo.mkdir()
            subprocess.run(("git", "init", "-q", str(repo)), check=True)
            buggy = commit_file(repo, "subject.py", "VALUE = 1\n", "first")
            fixed = commit_file(repo, "tests/test_subject.py", "def test_value(): pass\n", "second")
            candidate = executor.Candidate(
                candidate_rank=1,
                selection_order=1,
                canonical_case_id="demo::1",
                project="demo",
                bug_id="1",
                source_url="local",
                python_version="3.11",
                buggy_revision=buggy,
                fixed_revision=fixed,
                declared_test_file="tests/test_subject.py",
                bugsinpy_source_commit=executor.BUGSINPY_COMMIT,
            )
            manifest = executor.build_protected_manifest(
                candidate,
                repo,
                buggy,
                fixed,
                ["pytest tests/test_subject.py::test_value"],
            )
            entry = manifest["entries"][0]
            self.assertEqual(manifest["status"], "RESOLVED")
            self.assertEqual(entry["buggy_checkout_sha256"], "")
            self.assertEqual(entry["buggy_effective_sha256"], entry["fixed_sha256"])
            self.assertTrue(entry["buggy_test_injection_from_fixed"])

    def test_execution_plan_hash_is_deterministic(self) -> None:
        first = {"b": [2, 1], "a": "value"}
        second = {"a": "value", "b": [2, 1]}
        self.assertEqual(
            executor.deterministic_plan_hash(first), executor.deterministic_plan_hash(second)
        )

    def test_environment_tree_hash_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "environment"
            (root / "bin").mkdir(parents=True)
            executable = root / "bin" / "python"
            executable.write_bytes(b"synthetic interpreter\n")
            try:
                executable.chmod(0o555)
                (root / "bin").chmod(0o555)
                root.chmod(0o555)
                first = executor.environment_tree_manifest_sha256(root)
                second = executor.environment_tree_manifest_sha256(root)
                self.assertEqual(first, second)
                executor._assert_read_only_tree(root)
            finally:
                root.chmod(0o755)
                (root / "bin").chmod(0o755)
                executable.chmod(0o644)

    def test_execution_requires_exact_authority_input(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaises(executor.InfrastructureFailure):
                executor.execute_case(
                    case_root=root / "case",
                    external_root=root,
                    execution_id="attempt-1",
                    authorization="not-authorized",
                    recorded_rerun_reason="",
                )

    def test_schedule_is_fixed_three_buggy_then_three_fixed(self) -> None:
        self.assertEqual(
            [(item.revision_label, item.ordinal) for item in executor.build_execution_schedule()],
            [
                ("BUGGY", 1),
                ("BUGGY", 2),
                ("BUGGY", 3),
                ("FIXED", 1),
                ("FIXED", 2),
                ("FIXED", 3),
            ],
        )

    def test_no_early_stop_after_outcomes_or_infrastructure_error(self) -> None:
        calls: list[tuple[str, int]] = []

        def runner(item: executor.ScheduledRun) -> dict[str, object]:
            calls.append((item.revision_label, item.ordinal))
            if len(calls) == 2:
                raise executor.InfrastructureFailure("synthetic setup fault")
            return {
                "revision_label": item.revision_label,
                "ordinal": item.ordinal,
                "state": "ORACLE_COMPLETED",
                "exit_code": 1,
                "protected_integrity": True,
            }

        records = executor.execute_schedule_without_early_stop(runner)
        self.assertEqual(len(calls), 6)
        self.assertEqual(len(records), 6)
        self.assertEqual(records[1]["state"], "INFRASTRUCTURE_ERROR")

    def test_infrastructure_and_reproducibility_outcomes_are_distinct(self) -> None:
        schedule = executor.build_execution_schedule()
        records = [
            {
                "revision_label": item.revision_label,
                "ordinal": item.ordinal,
                "state": "ORACLE_COMPLETED",
                "exit_code": 1,
                "protected_integrity": True,
            }
            for item in schedule
        ]
        self.assertEqual(
            executor.classify_execution_records(records),
            "INELIGIBLE_REPRODUCIBILITY_OUTCOME",
        )
        records[0]["state"] = "INFRASTRUCTURE_ERROR"
        self.assertEqual(
            executor.classify_execution_records(records),
            "INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY",
        )

    def test_interruption_or_incomplete_checkpoint_is_not_eligibility(self) -> None:
        self.assertEqual(
            executor.classify_execution_records([{"state": "INTERRUPTED"}]),
            "INTERRUPTED_NOT_ELIGIBILITY",
        )
        self.assertEqual(executor.classify_execution_records([]), "INCOMPLETE_NOT_ELIGIBILITY")

    def test_screening_checkout_marker_forbids_repair_reuse(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            candidate = executor.Candidate(
                candidate_rank=1,
                selection_order=1,
                canonical_case_id="demo::1",
                project="demo",
                bug_id="1",
                source_url="local",
                python_version="3.11",
                buggy_revision="a" * 40,
                fixed_revision="b" * 40,
                declared_test_file="tests/test_subject.py",
                bugsinpy_source_commit=executor.BUGSINPY_COMMIT,
            )
            executor._write_case_marker(root, candidate)
            marker_path = root / "screening_checkout" / "SCREENING_ONLY_DO_NOT_USE_FOR_REPAIR.json"
            marker = json.loads(marker_path.read_text(encoding="utf-8"))
            self.assertFalse(marker["repair_workspace_usable"])
            self.assertEqual(marker["purpose"], "SCREENING_ONLY")

    def test_oracle_preservation_and_multi_command_refusal(self) -> None:
        single = executor.analyze_oracle(b"pytest tests/test_x.py::test_x\n")
        self.assertEqual(single["status"], "RESOLVED_SINGLE_COMMAND")
        multiple = executor.analyze_oracle(b"pytest tests/test_x.py\npytest tests/test_y.py\n")
        self.assertEqual(multiple["status"], "UNRESOLVED_MULTIPLE_SUBSTANTIVE_COMMANDS")

    def test_csv_writer_preserves_supplied_order(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "plan.csv"
            rows = []
            for rank in (4, 2):
                row = {field: "" for field in executor.PLAN_FIELDS}
                row["candidate_rank"] = str(rank)
                rows.append(row)
            executor.write_execution_plan_csv(path, rows)
            with path.open(newline="", encoding="utf-8") as handle:
                actual = list(csv.DictReader(handle))
            self.assertEqual([row["candidate_rank"] for row in actual], ["4", "2"])
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                hashlib.sha256(path.read_bytes()).hexdigest(),
            )


if __name__ == "__main__":
    unittest.main()

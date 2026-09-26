from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
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
    def test_committed_pre_eligibility_ledgers_pass_controlling_validation(self) -> None:
        benchmark_root = Path(__file__).resolve().parents[1]
        executor.validate_controlling_inputs(benchmark_root)
        with (benchmark_root / "exclusions.csv").open(newline="", encoding="utf-8") as handle:
            self.assertEqual(len(list(csv.DictReader(handle))), 21)

    def test_pre_eligibility_ledger_mutations_fail_closed(self) -> None:
        benchmark_root = Path(__file__).resolve().parents[1]
        controlling = (
            "PROTOCOL.md", "RUN_SPEC_V1.md", "candidate_universe.csv",
            "cases_manifest.csv", "initial_40_build_failure_adjudication_v1.csv",
            "exclusions.csv",
        )
        with tempfile.TemporaryDirectory() as temporary:
            test_root = Path(temporary)
            for name in controlling:
                shutil.copyfile(benchmark_root / name, test_root / name)
            path = test_root / "exclusions.csv"
            original = path.read_text(encoding="utf-8")
            with path.open(newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                fields = reader.fieldnames
                rows = list(reader)
            self.assertIsNotNone(fields)

            def check_rows(label: str, changed: list[dict[str, str]]) -> None:
                with self.subTest(label=label):
                    with path.open("w", newline="", encoding="utf-8") as handle:
                        writer = csv.DictWriter(handle, fieldnames=fields)
                        writer.writeheader()
                        writer.writerows(changed)
                    with self.assertRaises(executor.PreparationError):
                        executor.validate_controlling_inputs(test_root)

            check_rows("deleted normative exclusion", rows[:-1])
            changed = [row.copy() for row in rows]
            changed[0]["exclusion_reason"] = "DEPENDENCY_SETUP_FAILURE"
            check_rows("reason mutation", changed)
            changed = [row.copy() for row in rows]
            changed[-1] = changed[0].copy()
            check_rows("duplicate case", changed)
            check_rows("unexpected extra case", rows + [dict(rows[0], case_id="unknown::1")])
            changed = [row.copy() for row in rows]
            changed[0]["eligibility_stage"] = "ORACLE_SCREENING"
            check_rows("wrong stage", changed)
            changed = [row.copy() for row in rows]
            changed[0].update(case_id="black::17", source_project="black", bugsinpy_bug_id="17")
            check_rows("environment-ready case inserted", changed)
            changed = [row.copy() for row in rows]
            changed[0]["source_project"] = "other"
            check_rows("wrong source project", changed)
            changed = [row.copy() for row in rows]
            changed[0]["evidence_reference"] = ""
            check_rows("missing evidence reference", changed)
            changed = [row.copy() for row in rows]
            changed[0]["notes"] = "proposal-only"
            check_rows("missing normative markers", changed)
            changed = [row.copy() for row in rows]
            next(row for row in changed if row["case_id"] == "thefuck::9")[
                "exclusion_reason"
            ] = "NEEDS_HUMAN_PI_ADJUDICATION"
            check_rows("proposal-only disposition", changed)

            path.write_text(original, encoding="utf-8")
            manifest = test_root / "cases_manifest.csv"
            manifest.write_text(manifest.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            with self.assertRaises(executor.PreparationError):
                executor.validate_controlling_inputs(test_root)
            shutil.copyfile(benchmark_root / "cases_manifest.csv", manifest)
            path.write_text(original.replace("eligibility_stage", "stage", 1), encoding="utf-8")
            with self.assertRaises(executor.PreparationError):
                executor.validate_controlling_inputs(test_root)
            path.write_text(original, encoding="utf-8")
            adjudication = test_root / "initial_40_build_failure_adjudication_v1.csv"
            adjudication.write_bytes(
                (benchmark_root / "initial_40_build_failure_adjudication_proposal.csv").read_bytes()
            )
            with self.assertRaises(executor.PreparationError):
                executor.validate_controlling_inputs(test_root)

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
            self.assertEqual(row["oracle_commands"], json.dumps([oracle_bytes.decode().strip()]))
            self.assertEqual(row["oracle_command_count"], "1")
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

    def test_timeout_gate_blocks_even_with_exact_authority_before_any_execution(self) -> None:
        with mock.patch.object(executor, "_load_json") as load, mock.patch.object(
            executor.subprocess, "run"
        ) as run:
            with self.assertRaisesRegex(
                executor.InfrastructureFailure, "PRE_EXECUTION_TIMEOUT_GATE_REQUIRED"
            ):
                executor.execute_case(
                    case_root=Path("/nonexistent/case"),
                    external_root=Path("/nonexistent"),
                    execution_id="attempt-1",
                    authorization=executor.EXECUTION_AUTHORITY_TOKEN,
                    recorded_rerun_reason="",
                )
        load.assert_not_called()
        run.assert_not_called()

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
                "trial_result": "TRIAL_FAIL",
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
                "trial_result": "TRIAL_FAIL",
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

    def test_oracle_preservation_and_ordered_commands(self) -> None:
        single = executor.analyze_oracle(b"pytest tests/test_x.py::test_x\n")
        self.assertEqual(single["status"], "RESOLVED_ORDERED_COMMANDS")
        self.assertEqual(single["commands"], ["pytest tests/test_x.py::test_x"])
        source = b"pytest tests/test_y.py  \npytest tests/test_x.py\n"
        multiple = executor.analyze_oracle(source)
        self.assertEqual(multiple["status"], "RESOLVED_ORDERED_COMMANDS")
        self.assertEqual(multiple["commands"], ["pytest tests/test_y.py  ", "pytest tests/test_x.py"])
        six = executor.analyze_oracle(b"pytest tests/test_x.py\n" * 6)
        self.assertEqual(len(six["commands"]), 6)
        self.assertEqual(six["status"], "RESOLVED_ORDERED_COMMANDS")
        self.assertEqual(executor.sha256_bytes(source), hashlib.sha256(source).hexdigest())

    def test_any_unsafe_line_leaves_oracle_unresolved(self) -> None:
        for unsafe in (
            "pytest tests/test_y.py | cat",
            "pytest tests/test_y.py > output",
            "curl https://example.invalid",
            "MODE=1 pytest tests/test_y.py",
            "pytest tests/test_y.py && echo done",
            "pytest tests/test_y.py &",
            "/tmp/pytest tests/test_y.py",
            'pytest "tests/test_y.py"',
        ):
            with self.subTest(unsafe=unsafe):
                parsed = executor.analyze_oracle(
                    ("pytest tests/test_x.py\n" + unsafe + "\n").encode()
                )
                self.assertNotEqual(parsed["status"], "RESOLVED_ORDERED_COMMANDS")

    def test_composite_trial_outcomes_and_no_early_stop(self) -> None:
        for codes, expected in (([1, 0], "TRIAL_FAIL"), ([0, 1], "TRIAL_FAIL"),
                                ([0, 0], "TRIAL_PASS")):
            calls: list[int] = []

            def runner(ordinal: int, command: str) -> dict[str, object]:
                calls.append(ordinal)
                return {"command_ordinal": ordinal, "command": command,
                        "command_sha256": executor.sha256_bytes(command.encode()),
                        "cwd": "/synthetic", "started_at_utc": "T0", "ended_at_utc": "T1",
                        "wall_time_seconds": 1.0, "stdout_artifact": "stdout.raw",
                        "stderr_artifact": "stderr.raw",
                        "stdout_sha256": executor.sha256_bytes(b""),
                        "stderr_sha256": executor.sha256_bytes(b""),
                        "state": "ORACLE_COMPLETED", "exit_code": codes[ordinal - 1],
                        "protected_integrity": True}

            records = executor.run_ordered_subcommands(["pytest x", "pytest y"], runner)
            self.assertEqual(calls, [1, 2])
            self.assertEqual(executor.classify_trial_commands(records, 2), expected)
        infrastructure = [records[0], {"command_ordinal": 2,
                                       "state": "INFRASTRUCTURE_ERROR"}]
        self.assertNotEqual(executor.classify_trial_commands(infrastructure, 2), "TRIAL_FAIL")
        missing_evidence = [dict(records[0]), dict(records[1])]
        del missing_evidence[1]["stderr_sha256"]
        self.assertEqual(executor.classify_trial_commands(missing_evidence, 2),
                         "CASE_INVALIDATED")
        interrupted = [dict(records[0]), dict(records[1])]
        interrupted[1]["state"] = "INTERRUPTED"
        self.assertEqual(executor.classify_trial_commands(interrupted, 2),
                         "INTERRUPTED_NOT_ELIGIBILITY")

    def test_synthetic_future_trial_uses_one_workspace_and_runs_after_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            environment_root = root / "environment"
            (environment_root / "bin").mkdir(parents=True)
            identity = {
                "environment_root": str(environment_root),
                "environment_bin_dir": str(environment_root / "bin"),
                "environment_tree_manifest_sha256":
                    executor.environment_tree_manifest_sha256(environment_root),
            }
            plan = {
                "buggy_commit_full": "a" * 40,
                "fixed_commit_full": "b" * 40,
                "subject_mirror_path": str(root / "subject.git"),
                "oracle_commands": ["pytest tests/x.py", "pytest tests/y.py"],
                "oracle_command_count": 2,
            }
            completed = [
                subprocess.CompletedProcess([], 1, b"first", b"failure"),
                subprocess.CompletedProcess([], 0, b"second", b""),
            ]
            with mock.patch.object(executor, "_run"), mock.patch.object(
                executor, "_git", return_value=subprocess.CompletedProcess([], 0, "", "")
            ), mock.patch.object(executor, "_inject_benchmark_owned_tests"), mock.patch.object(
                executor, "_verify_protected_paths", return_value=(True, [])
            ), mock.patch.object(executor, "run_oracle_process", side_effect=completed) as run:
                record = executor._execute_one_run(
                    executor.ScheduledRun("BUGGY", 1), plan=plan, manifest={},
                    environment_identity=identity, run_root=root / "trial"
                )
            self.assertEqual(run.call_count, 2)
            self.assertEqual([call.args[0] for call in run.call_args_list],
                             [("pytest", "tests/x.py"), ("pytest", "tests/y.py")])
            self.assertEqual(run.call_args_list[0].kwargs["cwd"],
                             run.call_args_list[1].kwargs["cwd"])
            self.assertEqual(record["trial_result"], "TRIAL_FAIL")
            self.assertEqual(record["exit_codes"], [1, 0])
            evidence = json.loads((root / "trial" / "trial_evidence.json").read_text())
            self.assertEqual(evidence["trial_result"], "TRIAL_FAIL")
            self.assertEqual((root / "trial" / "subcommands" / "01" / "stdout.raw").read_bytes(),
                             b"first")

    def test_production_timeout_and_network_defaults(self) -> None:
        self.assertEqual(executor.SUBCOMMAND_TIMEOUT_SECONDS, 300)
        self.assertEqual(executor.TRIAL_TIMEOUT_SECONDS, 900)
        self.assertEqual(executor.PRODUCTION_RUNTIME_BACKEND, "docker")
        self.assertEqual(executor.PRODUCTION_RUNTIME_PLATFORM, "linux/amd64")
        self.assertEqual(executor.DOCKER_EXECUTION_NETWORK_MODE, "none")
        self.assertTrue(executor.PRE_EXECUTION_TIMEOUT_GATE_REQUIRED)
        self.assertFalse(executor.PRODUCTION_DOCKER_BACKEND_IMPLEMENTED)
        image = "docker.io/library/python@sha256:" + "a" * 64
        argv = executor.docker_execution_base_argv(image)
        self.assertIn("--network=none", argv)
        self.assertIn("--platform=linux/amd64", argv)
        self.assertIn("--read-only", argv)
        self.assertEqual(argv[-1], image)
        with self.assertRaises(executor.InfrastructureFailure):
            executor.docker_execution_base_argv("docker.io/library/python:3.8.3")

    def test_unbuilt_identity_fields_are_not_fabricated(self) -> None:
        identity = executor.unbuilt_environment_identity()
        self.assertEqual(set(identity), set(executor.ENVIRONMENT_IDENTITY_V1_FIELDS))
        self.assertEqual(set(identity.values()), {"UNBUILT"})

    def _synthetic_timeout_trial(
        self, root: Path, completed: object, *, trial_timeout: float,
        subcommand_timeout: float = 1.0,
    ) -> tuple[dict[str, object], object]:
        environment_root = root / "environment"
        (environment_root / "bin").mkdir(parents=True)
        identity = {
            "environment_root": str(environment_root),
            "environment_bin_dir": str(environment_root / "bin"),
            "environment_tree_manifest_sha256":
                executor.environment_tree_manifest_sha256(environment_root),
        }
        plan = {
            "buggy_commit_full": "a" * 40,
            "fixed_commit_full": "b" * 40,
            "subject_mirror_path": str(root / "subject.git"),
            "oracle_commands": ["pytest synthetic_a", "pytest synthetic_b"],
            "oracle_command_count": 2,
        }
        with mock.patch.object(executor, "_run"), mock.patch.object(
            executor, "_git", return_value=subprocess.CompletedProcess([], 0, "", "")
        ), mock.patch.object(executor, "_inject_benchmark_owned_tests"), mock.patch.object(
            executor, "_verify_protected_paths", return_value=(True, [])
        ), mock.patch.object(executor, "TRIAL_TIMEOUT_SECONDS", trial_timeout), mock.patch.object(
            executor, "SUBCOMMAND_TIMEOUT_SECONDS", subcommand_timeout
        ), mock.patch.object(executor, "run_oracle_process", side_effect=completed) as run:
            record = executor._execute_one_run(
                executor.ScheduledRun("BUGGY", 1), plan=plan, manifest={},
                environment_identity=identity, run_root=root / "trial"
            )
        return record, run

    def test_subcommand_timeout_is_infrastructure_and_stops_trial_without_retry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            record, run = self._synthetic_timeout_trial(
                root, executor.OracleTimeout("ORACLE_SUBCOMMAND_TIMEOUT", b"partial", b""),
                trial_timeout=2.0, subcommand_timeout=0.01,
            )
            self.assertEqual(run.call_count, 1)
            self.assertEqual(record["trial_result"], "INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY")
            self.assertEqual(record["state"], "INFRASTRUCTURE_ERROR")
            self.assertEqual(record["infrastructure_subreason"], "ORACLE_SUBCOMMAND_TIMEOUT")
            schedule = executor.build_execution_schedule()
            six_records = [
                {
                    "revision_label": item.revision_label,
                    "ordinal": item.ordinal,
                    "state": "ORACLE_COMPLETED",
                    "trial_result": "TRIAL_FAIL" if item.revision_label == "BUGGY" else "TRIAL_PASS",
                }
                for item in schedule
            ]
            six_records[0] = record
            self.assertEqual(executor.classify_execution_records(six_records),
                             "INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY")
            evidence = json.loads((root / "trial" / "trial_evidence.json").read_text())
            self.assertEqual(len(evidence["subcommands"]), 1)
            self.assertNotEqual(evidence["trial_result"], "TRIAL_FAIL")
            self.assertEqual(evidence["subcommands"][0]["infrastructure_reason"],
                             "OTHER_INFRASTRUCTURE_FAILURE")
            self.assertEqual((root / "trial" / "subcommands" / "01" / "stdout.raw").read_bytes(),
                             b"partial")

    def test_aggregate_trial_timeout_is_infrastructure_and_stops_later_command(self) -> None:
        def slow_completed(*args: object, **kwargs: object) -> subprocess.CompletedProcess[bytes]:
            time.sleep(0.03)
            return subprocess.CompletedProcess([], 1, b"", b"")

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            record, run = self._synthetic_timeout_trial(
                root, slow_completed, trial_timeout=0.01, subcommand_timeout=1.0
            )
            self.assertEqual(run.call_count, 1)
            self.assertLess(run.call_args.kwargs["timeout_seconds"], 1.0)
            self.assertEqual(run.call_args.kwargs["timeout_subreason"],
                             "ORACLE_TRIAL_TIMEOUT")
            self.assertEqual(record["infrastructure_subreason"], "ORACLE_TRIAL_TIMEOUT")
            self.assertEqual(record["trial_result"], "INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY")
            self.assertNotEqual(record["trial_result"], "TRIAL_FAIL")

    def test_timeout_kills_spawned_process_group(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sentinel = root / "child_survived"
            child = "import pathlib,time; time.sleep(0.4); pathlib.Path(%r).write_text('bad')" % str(sentinel)
            parent = (
                "import subprocess,sys,time; "
                f"subprocess.Popen([sys.executable,'-c',{child!r}]); "
                "print('spawned',flush=True); time.sleep(3)"
            )
            with self.assertRaises(executor.OracleTimeout) as caught:
                executor.run_oracle_process(
                    [sys.executable, "-c", parent], cwd=root, env=os.environ.copy(),
                    timeout_seconds=0.1, timeout_subreason="ORACLE_SUBCOMMAND_TIMEOUT",
                )
            self.assertEqual(caught.exception.subreason, "ORACLE_SUBCOMMAND_TIMEOUT")
            self.assertIn(b"spawned", caught.exception.stdout)
            time.sleep(0.5)
            self.assertFalse(sentinel.exists())

    def test_composite_eligibility_is_six_trial_results(self) -> None:
        schedule = executor.build_execution_schedule()
        records = [
            {"revision_label": item.revision_label, "ordinal": item.ordinal,
             "state": "ORACLE_COMPLETED",
             "trial_result": "TRIAL_FAIL" if item.revision_label == "BUGGY" else "TRIAL_PASS"}
            for item in schedule
        ]
        self.assertEqual(executor.classify_execution_records(records), "ELIGIBLE")
        self.assertEqual(executor.classify_execution_records(records[:5]),
                         "INCOMPLETE_NOT_ELIGIBILITY")
        records[0]["trial_result"] = "TRIAL_PASS"
        self.assertEqual(executor.classify_execution_records(records),
                         "INELIGIBLE_REPRODUCIBILITY_OUTCOME")

    def test_trial_evidence_hash_is_deterministic(self) -> None:
        first = {"exit_codes": [1, 0], "oracle_commands": ["pytest x", "pytest y"]}
        second = {"oracle_commands": ["pytest x", "pytest y"], "exit_codes": [1, 0]}
        digest = executor.deterministic_trial_evidence_hash(first)
        self.assertEqual(digest, executor.deterministic_trial_evidence_hash(second))
        first["trial_evidence_sha256"] = digest
        self.assertEqual(digest, executor.deterministic_trial_evidence_hash(first))

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

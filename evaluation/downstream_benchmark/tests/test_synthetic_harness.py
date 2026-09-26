from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

from evaluation.downstream_benchmark.harness import (
    Action,
    BenchmarkRunner,
    CASE_SCHEMA_VERSION,
    CapturedFailure,
    CaseSpec,
    CaseSpecError,
    DEFAULT_REPAIR_TIMEOUT_SECONDS,
    ErrPilotHandoff,
    IsolationProbeAdapter,
    OUTCOMES,
    PROTOCOL_SHA256,
    PROTOCOL_VERSION,
    ProvenanceMismatch,
    RUN_SPEC_SHA256,
    RUN_SPEC_VERSION,
    ScriptedAdapter,
    TASK_INSTRUCTION,
    TASK_INSTRUCTION_SHA256,
    build_payload_pair,
    decode_frame,
    manifest_sha256,
    protected_manifest,
    result_record_sha256,
    snapshot_tree,
    validate_result_record,
)


BENCHMARK_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = BENCHMARK_ROOT / "fixtures" / "synthetic_case" / "source"
FIXED_TIME = "2026-09-22T12:00:00.000000Z"
SUCCESSFUL_SUBJECT = b"def answer() -> int:\n    return 2\n"
PASSING_ORACLE = b'print("SYNTHETIC_EXPECTED_TEST_OBSERVED")\nraise SystemExit(0)\n'


def case_mapping(*, workspace_identity: str | None = None, missing_oracle: bool = False):
    identity = workspace_identity or manifest_sha256(snapshot_tree(SOURCE_ROOT))
    oracle = [sys.executable, "missing_oracle.py" if missing_oracle else "oracle.py"]
    return {
        "schema_version": CASE_SCHEMA_VERSION,
        "execution_mode": "synthetic_validation",
        "case_id": "SYNTHETIC_CASE_A",
        "source_project": "synthetic-local-fixture",
        "source_revision": "synthetic:buggy:v1",
        "fixed_revision": "synthetic:fixed:v1",
        "failing_command": "python oracle.py",
        "oracle_command": oracle,
        "oracle_expected_marker": "SYNTHETIC_EXPECTED_TEST_OBSERVED",
        "workspace_identity": identity,
        "protected_items": [
            item.to_dict() for item in protected_manifest(SOURCE_ROOT, ["oracle.py", "protected"])
        ],
        "environment_identity": {
            "immutable_id": "synthetic-local-stdlib-environment-v1",
            "python_version": sys.version.split()[0],
            "dependency_identity": "python-standard-library-only",
        },
        "sample_role": "synthetic_fixture",
        "protocol_version": PROTOCOL_VERSION,
        "protocol_sha256": PROTOCOL_SHA256,
        "run_spec_version": RUN_SPEC_VERSION,
        "run_spec_sha256": RUN_SPEC_SHA256,
        "errpilot_revision": "synthetic-handoff-fixture-v1",
        "errpilot_configuration_sha256": hashlib.sha256(b"synthetic-config-v1").hexdigest(),
    }


def case_spec(**kwargs) -> CaseSpec:
    return CaseSpec.from_mapping(case_mapping(**kwargs))


def evidence(case: CaseSpec, *, handoff_execution_id: str = "capture-001"):
    failure = CapturedFailure(
        source_execution_id="capture-001",
        source_state_sha256=case.workspace_identity,
        failing_command=case.failing_command,
        stdout=b"synthetic failure stdout\xff\r\n",
        stderr=b"synthetic failure stderr\x00\n",
    )
    handoff = ErrPilotHandoff(
        source_execution_id=handoff_execution_id,
        source_state_sha256=case.workspace_identity,
        artifact=b"SYNTHETIC HANDOFF\nobserved: answer was 1\n",
        producing_run_identity="synthetic-errpilot-run-001",
    )
    return failure, handoff


def success_adapter(identity: str) -> ScriptedAdapter:
    return ScriptedAdapter(identity, [Action("write", "subject.py", SUCCESSFUL_SUBJECT)])


def noop_adapters(prefix: str = "noop"):
    return {
        "RAW": ScriptedAdapter(f"{prefix}-raw"),
        "ERRPILOT": ScriptedAdapter(f"{prefix}-errpilot"),
    }


class SyntheticHarnessTests(unittest.TestCase):
    def run_pair(
        self,
        case: CaseSpec,
        adapters,
        *,
        timeout_seconds: float = DEFAULT_REPAIR_TIMEOUT_SECONDS,
        repetition: int = 1,
        order=("RAW", "ERRPILOT"),
        temp: tempfile.TemporaryDirectory | None = None,
        handoff_execution_id: str = "capture-001",
    ):
        owned = temp or tempfile.TemporaryDirectory()
        self.addCleanup(owned.cleanup)
        failure, handoff = evidence(case, handoff_execution_id=handoff_execution_id)
        run_root = Path(owned.name) / "run"
        runner = BenchmarkRunner(SOURCE_ROOT, run_root, now=lambda: FIXED_TIME)
        results = runner.run_pair(
            case,
            failure,
            handoff,
            adapters,
            repetition=repetition,
            condition_order=order,
            timeout_seconds=timeout_seconds,
        )
        return results, run_root

    def test_authoritative_entry_hashes_and_task_bytes_match(self):
        protocol = (BENCHMARK_ROOT / "PROTOCOL.md").read_bytes()
        run_spec = (BENCHMARK_ROOT / "RUN_SPEC_V1.md").read_bytes()
        self.assertEqual(hashlib.sha256(protocol).hexdigest(), PROTOCOL_SHA256)
        self.assertEqual(hashlib.sha256(run_spec).hexdigest(), RUN_SPEC_SHA256)
        self.assertEqual(hashlib.sha256(TASK_INSTRUCTION).hexdigest(), TASK_INSTRUCTION_SHA256)

    def test_case_schema_rejects_incomplete_or_non_synthetic_identity(self):
        mapping = case_mapping()
        del mapping["source_revision"]
        with self.assertRaisesRegex(CaseSpecError, "missing required case identities"):
            CaseSpec.from_mapping(mapping)

        mapping = case_mapping()
        mapping["execution_mode"] = "benchmark"
        with self.assertRaisesRegex(CaseSpecError, "refuses non-synthetic"):
            CaseSpec.from_mapping(mapping)

    def test_payloads_are_deterministic_binary_exact_and_share_provenance(self):
        case = case_spec()
        failure, handoff = evidence(case)
        first = build_payload_pair(case, failure, handoff)
        second = build_payload_pair(case, failure, handoff)
        self.assertEqual(first, second)
        self.assertEqual(first.raw.source_execution_sha256, first.errpilot.source_execution_sha256)

        raw_fields = dict(decode_frame(first.raw.bytes_value))
        errpilot_fields = dict(decode_frame(first.errpilot.bytes_value))
        self.assertEqual(raw_fields["TASK"], TASK_INSTRUCTION)
        self.assertEqual(errpilot_fields["TASK"], TASK_INSTRUCTION)
        self.assertEqual(raw_fields["FAILING_COMMAND"], failure.failing_command.encode())
        self.assertEqual(raw_fields["STDOUT"], failure.stdout)
        self.assertEqual(raw_fields["STDERR"], failure.stderr)
        self.assertEqual(errpilot_fields["HANDOFF"], handoff.artifact)
        self.assertNotIn("HANDOFF", raw_fields)
        self.assertNotIn("STDOUT", errpilot_fields)
        self.assertNotIn("STDERR", errpilot_fields)

    def test_same_execution_mismatch_blocks_before_workspace_or_adapter(self):
        case = case_spec()
        adapters = noop_adapters()
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        failure, handoff = evidence(case, handoff_execution_id="different-capture")
        run_root = Path(temporary.name) / "run"
        runner = BenchmarkRunner(SOURCE_ROOT, run_root)
        with self.assertRaisesRegex(ProvenanceMismatch, "source execution IDs differ"):
            runner.run_pair(
                case,
                failure,
                handoff,
                adapters,
                repetition=1,
                condition_order=("RAW", "ERRPILOT"),
            )
        self.assertFalse(run_root.exists())
        self.assertEqual(adapters["RAW"].call_count, 0)
        self.assertEqual(adapters["ERRPILOT"].call_count, 0)

    def test_fixture_matrix_exercises_every_frozen_outcome_without_retry(self):
        observed: set[str] = set()

        scenarios = []
        scenarios.append(
            (
                case_spec(),
                {"RAW": success_adapter("success-raw"), "ERRPILOT": success_adapter("success-ep")},
                DEFAULT_REPAIR_TIMEOUT_SECONDS,
                "REPAIR_SUCCESS",
            )
        )
        scenarios.append(
            (case_spec(), noop_adapters("oracle-fail"), 1200.0, "REPAIR_FAILURE_ORACLE")
        )
        mutation_actions = [
            Action("write", "subject.py", SUCCESSFUL_SUBJECT),
            Action("write", "oracle.py", PASSING_ORACLE),
        ]
        scenarios.append(
            (
                case_spec(),
                {
                    "RAW": ScriptedAdapter("mutation-raw", mutation_actions),
                    "ERRPILOT": ScriptedAdapter("mutation-ep", mutation_actions),
                },
                1200.0,
                "REPAIR_FAILURE_TEST_MUTATION",
            )
        )
        scenarios.append(
            (
                case_spec(),
                {
                    "RAW": ScriptedAdapter("timeout-raw", wall_time_seconds=0.05),
                    "ERRPILOT": ScriptedAdapter("timeout-ep", wall_time_seconds=0.05),
                },
                0.01,
                "REPAIR_TIMEOUT",
            )
        )
        scenarios.append(
            (
                case_spec(),
                {
                    "RAW": ScriptedAdapter("agent-error-raw", raise_agent_failure=True),
                    "ERRPILOT": ScriptedAdapter("agent-error-ep", raise_agent_failure=True),
                },
                1200.0,
                "AGENT_ERROR",
            )
        )
        scenarios.append(
            (
                case_spec(missing_oracle=True),
                noop_adapters("infra"),
                1200.0,
                "INFRASTRUCTURE_ERROR",
            )
        )
        wrong_identity = "0" * 64
        scenarios.append(
            (
                case_spec(workspace_identity=wrong_identity),
                noop_adapters("invalid"),
                1200.0,
                "CASE_INVALIDATED",
            )
        )

        for index, (case, adapters, timeout, expected) in enumerate(scenarios, start=1):
            with self.subTest(expected=expected):
                results, _ = self.run_pair(
                    case,
                    adapters,
                    timeout_seconds=timeout,
                    repetition=index,
                )
                for condition in ("RAW", "ERRPILOT"):
                    self.assertEqual(results[condition]["repair_outcome"], expected)
                    validate_result_record(results[condition])
                    observed.add(results[condition]["repair_outcome"])
                expected_calls = 0 if expected == "CASE_INVALIDATED" else 1
                self.assertEqual(adapters["RAW"].call_count, expected_calls)
                self.assertEqual(adapters["ERRPILOT"].call_count, expected_calls)
        self.assertEqual(observed, set(OUTCOMES))

    def test_protected_mutation_overrides_passing_oracle(self):
        case = case_spec()
        actions = [
            Action("write", "subject.py", SUCCESSFUL_SUBJECT),
            Action("write", "oracle.py", PASSING_ORACLE),
        ]
        results, _ = self.run_pair(
            case,
            {
                "RAW": ScriptedAdapter("mutation-pass-raw", actions),
                "ERRPILOT": ScriptedAdapter("mutation-pass-ep", actions),
            },
        )
        for result in results.values():
            self.assertEqual(result["oracle_exit_code"], 0)
            self.assertFalse(result["protected_integrity_pass"])
            self.assertEqual(result["repair_outcome"], "REPAIR_FAILURE_TEST_MUTATION")

    def test_protected_content_deletion_replacement_and_rename_are_detected(self):
        original_oracle = (SOURCE_ROOT / "oracle.py").read_bytes()
        actions_by_kind = {
            "content": Action("write", "oracle.py", PASSING_ORACLE),
            "deletion": Action("delete", "oracle.py"),
            "replacement": Action("replace", "oracle.py", original_oracle),
            "rename": Action("rename", "oracle.py", destination="moved_oracle.py"),
            "directory_child": Action(
                "write", "protected/oracle_data.txt", b"changed protected child\n"
            ),
        }
        for index, (kind, action) in enumerate(actions_by_kind.items(), start=20):
            with self.subTest(kind=kind):
                adapters = {
                    "RAW": ScriptedAdapter(f"{kind}-raw", [action]),
                    "ERRPILOT": ScriptedAdapter(f"{kind}-ep", [action]),
                }
                results, _ = self.run_pair(case_spec(), adapters, repetition=index)
                for result in results.values():
                    self.assertEqual(result["repair_outcome"], "REPAIR_FAILURE_TEST_MUTATION")

    def test_fresh_state_and_ordinary_workspace_isolation(self):
        case = case_spec()
        probes = (
            "raw_only_marker.txt",
            "../errpilot/raw/errpilot_handoff.bin",
            "../../../artifacts",
            "/tmp/outside-workspace",
        )
        raw = ScriptedAdapter(
            "raw-writes-private-marker", [Action("write", "raw_only_marker.txt", b"raw only")]
        )
        errpilot = IsolationProbeAdapter("errpilot-probe", probes)
        results, run_root = self.run_pair(case, {"RAW": raw, "ERRPILOT": errpilot})

        self.assertEqual(errpilot.probe_blocked, [True, True, True, True])
        self.assertNotIn("raw_only_marker.txt", results["ERRPILOT"]["changed_paths"])
        self.assertFalse(
            (
                run_root
                / "workspaces"
                / case.case_id
                / "repetition-1"
                / "errpilot"
                / "raw_only_marker.txt"
            ).exists()
        )

        raw_artifacts = run_root / "artifacts" / case.case_id / "repetition-1" / "raw" / "raw"
        errpilot_artifacts = (
            run_root / "artifacts" / case.case_id / "repetition-1" / "errpilot" / "raw"
        )
        self.assertFalse((raw_artifacts / "errpilot_handoff.bin").exists())
        self.assertFalse((errpilot_artifacts / "failure_stdout.bin").exists())
        self.assertFalse((errpilot_artifacts / "failure_stderr.bin").exists())

    def test_result_artifacts_are_separate_hashed_and_unknown_metrics_are_na(self):
        case = case_spec()
        results, run_root = self.run_pair(
            case,
            {"RAW": success_adapter("artifact-raw"), "ERRPILOT": success_adapter("artifact-ep")},
        )
        for condition, result in results.items():
            self.assertEqual(result["test_invocations_total"], "NA")
            self.assertEqual(result["oracle_invocations_total"], "NA")
            self.assertEqual(result["post_edit_failed_oracle_count"], "NA")
            self.assertEqual(result["codex_cli_version"], "NA")
            self.assertEqual(result["model_identifier"], "NA")
            self.assertEqual(result["reasoning_effort"], "NA")
            self.assertEqual(result["result_sha256"], result_record_sha256(result))

            artifact_root = (
                run_root / "artifacts" / case.case_id / "repetition-1" / condition.lower()
            )
            stored = json.loads((artifact_root / "result.json").read_text())
            self.assertEqual(stored, result)
            index = json.loads((artifact_root / "evidence_index.json").read_text())
            indexed_paths = {entry["path"] for entry in index["artifacts"]}
            self.assertIn("raw/payload.bin", indexed_paths)
            self.assertIn("raw/adapter_stdout.bin", indexed_paths)
            self.assertIn("raw/oracle_stdout.bin", indexed_paths)
            self.assertIn("derived/workspace_diff.json", indexed_paths)
            self.assertIn("derived/protected_before_oracle.json", indexed_paths)

    def test_result_hash_is_deterministic_for_identical_synthetic_inputs(self):
        case = case_spec()
        first, _ = self.run_pair(
            case,
            {"RAW": success_adapter("stable-raw"), "ERRPILOT": success_adapter("stable-ep")},
        )
        second, _ = self.run_pair(
            case,
            {"RAW": success_adapter("stable-raw"), "ERRPILOT": success_adapter("stable-ep")},
        )
        self.assertEqual(first["RAW"]["result_sha256"], second["RAW"]["result_sha256"])
        self.assertEqual(first["ERRPILOT"]["result_sha256"], second["ERRPILOT"]["result_sha256"])

    def test_default_timeout_is_exactly_1200_and_test_override_does_not_change_it(self):
        self.assertEqual(DEFAULT_REPAIR_TIMEOUT_SECONDS, 1200.0)
        adapters = {
            "RAW": ScriptedAdapter("short-timeout-raw", wall_time_seconds=0.05),
            "ERRPILOT": ScriptedAdapter("short-timeout-ep", wall_time_seconds=0.05),
        }
        results, _ = self.run_pair(case_spec(), adapters, timeout_seconds=0.01)
        self.assertEqual(DEFAULT_REPAIR_TIMEOUT_SECONDS, 1200.0)
        self.assertEqual(results["RAW"]["timeout_seconds"], 0.01)
        self.assertEqual(results["RAW"]["repair_outcome"], "REPAIR_TIMEOUT")

    def test_harness_path_makes_no_network_request(self):
        adapters = noop_adapters("offline")
        with mock.patch(
            "socket.create_connection", side_effect=AssertionError("network forbidden")
        ):
            results, _ = self.run_pair(case_spec(), adapters)
        self.assertEqual(results["RAW"]["repair_outcome"], "REPAIR_FAILURE_ORACLE")

    def test_machine_readable_schema_files_are_valid_json(self):
        schema_root = BENCHMARK_ROOT / "harness" / "schemas"
        case_schema = json.loads((schema_root / "case_spec.schema.json").read_text())
        result_schema = json.loads((schema_root / "result.schema.json").read_text())
        self.assertEqual(
            case_schema["properties"]["execution_mode"]["const"], "synthetic_validation"
        )
        self.assertEqual(result_schema["properties"]["repair_outcome"]["enum"], list(OUTCOMES))

    def test_cases_manifest_remains_header_only(self):
        lines = (BENCHMARK_ROOT / "cases_manifest.csv").read_text().splitlines()
        self.assertEqual(len(lines), 1)


if __name__ == "__main__":
    unittest.main()

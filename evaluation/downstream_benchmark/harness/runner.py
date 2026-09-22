"""Synthetic-only benchmark runner and evidence recorder."""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from typing import Callable, Mapping

from .adapters import SyntheticAgentAdapter
from .constants import (
    CONDITIONS,
    DEFAULT_REPAIR_TIMEOUT_SECONDS,
    OUTCOMES,
    RESULT_SCHEMA_VERSION,
    TASK_INSTRUCTION_SHA256,
)
from .errors import AgentFailure, ArtifactCollision, CaseSpecError
from .filesystem import (
    artifact_index,
    canonical_json_bytes,
    capture_runtime_protected,
    copy_fresh_workspace,
    diff_manifests,
    manifest_dict,
    manifest_sha256,
    sha256_bytes,
    snapshot_tree,
    verify_protected,
    WorkspaceView,
    write_new_bytes,
    write_new_json,
)
from .models import (
    AdapterResult,
    CapturedFailure,
    CaseSpec,
    ConditionPayload,
    ErrPilotHandoff,
)
from .payloads import PayloadPair, build_payload_pair


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _safe_component(value: str) -> str:
    return "".join(
        character if character.isalnum() or character in "-_." else "_" for character in value
    )


class _RepairBudgetExpired(Exception):
    """Internal signal used to stop a synthetic adapter at the outer boundary."""


def _invoke_with_timeout(
    adapter: SyntheticAgentAdapter,
    workspace: WorkspaceView,
    payload: ConditionPayload,
    timeout_seconds: float,
) -> AdapterResult:
    if not hasattr(signal, "setitimer"):
        raise RuntimeError("wall-clock adapter enforcement requires POSIX setitimer")

    def expire(_signum, _frame):
        raise _RepairBudgetExpired

    previous_handler = signal.getsignal(signal.SIGALRM)
    signal.signal(signal.SIGALRM, expire)
    previous_timer = signal.setitimer(signal.ITIMER_REAL, timeout_seconds)
    try:
        return adapter.run(workspace, payload, timeout_seconds)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)
        if previous_timer != (0.0, 0.0):
            signal.setitimer(signal.ITIMER_REAL, *previous_timer)


class BenchmarkRunner:
    """Execute deterministic fixture pairs without any live agent or benchmark case."""

    def __init__(
        self,
        source_root: Path,
        run_root: Path,
        *,
        oracle_timeout_seconds: float = 10.0,
        now: Callable[[], str] = _utc_now,
    ):
        self.source_root = source_root.resolve(strict=True)
        self.run_root = run_root.resolve(strict=False)
        self.oracle_timeout_seconds = oracle_timeout_seconds
        self.now = now
        if self.oracle_timeout_seconds <= 0:
            raise ValueError("oracle timeout must be positive")
        fixture_root = (Path(__file__).resolve().parents[1] / "fixtures").resolve(strict=True)
        if self.source_root != fixture_root and fixture_root not in self.source_root.parents:
            raise ValueError("synthetic source_root must be inside benchmark-local fixtures")

    def run_pair(
        self,
        case: CaseSpec,
        failure: CapturedFailure,
        handoff: ErrPilotHandoff,
        adapters: Mapping[str, SyntheticAgentAdapter],
        *,
        repetition: int,
        condition_order: tuple[str, str],
        timeout_seconds: float = DEFAULT_REPAIR_TIMEOUT_SECONDS,
    ) -> dict[str, dict[str, object]]:
        case.validate_authority()
        if repetition < 1:
            raise CaseSpecError("repetition must be at least 1")
        if tuple(sorted(condition_order)) != tuple(sorted(CONDITIONS)):
            raise CaseSpecError("condition_order must contain RAW and ERRPILOT exactly once")
        if timeout_seconds <= 0:
            raise CaseSpecError("timeout_seconds must be positive")
        if len(case.oracle_command) != 2:
            raise CaseSpecError("synthetic oracle command must contain interpreter and script only")
        if Path(case.oracle_command[0]).resolve(strict=True) != Path(sys.executable).resolve(
            strict=True
        ):
            raise CaseSpecError("synthetic oracle must use the current Python interpreter")
        oracle_script = Path(case.oracle_command[1])
        if (
            oracle_script.is_absolute()
            or ".." in oracle_script.parts
            or oracle_script.suffix != ".py"
        ):
            raise CaseSpecError("synthetic oracle script must be a relative Python fixture path")
        if set(adapters) != set(CONDITIONS):
            raise CaseSpecError("one synthetic adapter is required for each condition")
        for condition, adapter in adapters.items():
            if getattr(adapter, "synthetic_only", False) is not True:
                raise CaseSpecError(f"{condition} adapter is not explicitly synthetic-only")
            if not getattr(adapter, "identity", ""):
                raise CaseSpecError(f"{condition} adapter identity is missing")
            if getattr(adapter, "call_count", 0) != 0:
                raise CaseSpecError(f"{condition} adapter is not a fresh synthetic session")
        if adapters["RAW"] is adapters["ERRPILOT"]:
            raise CaseSpecError("paired conditions require distinct synthetic adapter sessions")

        # This gate precedes all workspace creation and adapter execution.
        payloads = build_payload_pair(case, failure, handoff)

        namespace = Path(_safe_component(case.case_id)) / f"repetition-{repetition}"
        workspace_parent = self.run_root / "workspaces" / namespace
        artifact_parent = self.run_root / "artifacts" / namespace
        if workspace_parent.exists() or artifact_parent.exists():
            raise ArtifactCollision("a synthetic pair may not be silently rerun or overwritten")

        source_manifest = snapshot_tree(self.source_root)
        source_identity = manifest_sha256(source_manifest)
        workspaces: dict[str, Path] = {}
        workspace_manifests: dict[str, tuple] = {}
        for condition in CONDITIONS:
            workspace = workspace_parent / condition.lower()
            workspaces[condition] = workspace
            workspace_manifests[condition] = copy_fresh_workspace(self.source_root, workspace)

        invalid_reasons: list[str] = []
        if source_identity != case.workspace_identity:
            invalid_reasons.append("source_workspace_identity_mismatch")
        if manifest_sha256(workspace_manifests["RAW"]) != source_identity:
            invalid_reasons.append("raw_fresh_copy_mismatch")
        if manifest_sha256(workspace_manifests["ERRPILOT"]) != source_identity:
            invalid_reasons.append("errpilot_fresh_copy_mismatch")
        if workspace_manifests["RAW"] != workspace_manifests["ERRPILOT"]:
            invalid_reasons.append("condition_pre_run_state_mismatch")
        for condition in CONDITIONS:
            report = verify_protected(workspaces[condition], case.protected_items)
            if not report["pass"]:
                invalid_reasons.append(f"{condition.lower()}_protected_baseline_mismatch")

        results: dict[str, dict[str, object]] = {}
        if invalid_reasons:
            for condition in condition_order:
                results[condition] = self._record_invalidated(
                    case=case,
                    condition=condition,
                    condition_order=condition_order,
                    repetition=repetition,
                    payload=payloads.for_condition(condition),
                    payloads=payloads,
                    failure=failure,
                    handoff=handoff,
                    workspace=workspaces[condition],
                    artifact_root=artifact_parent / condition.lower(),
                    source_identity=source_identity,
                    invalid_reasons=invalid_reasons,
                    adapter_identity=adapters[condition].identity,
                    timeout_seconds=timeout_seconds,
                )
            return results

        # Both independent workspaces exist and match before either adapter starts.
        for condition in condition_order:
            results[condition] = self._run_session(
                case=case,
                condition=condition,
                condition_order=condition_order,
                repetition=repetition,
                payload=payloads.for_condition(condition),
                payloads=payloads,
                failure=failure,
                handoff=handoff,
                workspace=workspaces[condition],
                artifact_root=artifact_parent / condition.lower(),
                source_identity=source_identity,
                adapter=adapters[condition],
                timeout_seconds=timeout_seconds,
            )
        return results

    def _write_input_artifacts(
        self,
        *,
        case: CaseSpec,
        condition: str,
        payload: ConditionPayload,
        payloads: PayloadPair,
        failure: CapturedFailure,
        handoff: ErrPilotHandoff,
        baseline_manifest: tuple,
        artifact_root: Path,
        source_identity: str,
    ) -> list[str]:
        if artifact_root.exists():
            raise ArtifactCollision(f"artifact root already exists: {artifact_root}")
        artifact_root.mkdir(parents=True)
        written: list[str] = []

        def write_bytes(relative: str, data: bytes) -> None:
            write_new_bytes(artifact_root / relative, data)
            written.append(relative)

        def write_json(relative: str, value: object) -> None:
            write_new_json(artifact_root / relative, value)
            written.append(relative)

        write_bytes("raw/payload.bin", payload.bytes_value)
        if condition == "RAW":
            write_bytes("raw/failure_stdout.bin", failure.stdout)
            write_bytes("raw/failure_stderr.bin", failure.stderr)
        else:
            write_bytes("raw/errpilot_handoff.bin", handoff.artifact)
        write_json("derived/case_spec.json", case.to_dict())
        write_json("derived/baseline_manifest.json", manifest_dict(baseline_manifest))
        write_json(
            "derived/payload_metadata.json",
            {
                "condition": condition,
                "payload_sha256": payload.sha256,
                "task_instruction_sha256": TASK_INSTRUCTION_SHA256,
                "source_execution_id": payload.source_execution_id,
                "source_execution_sha256": payload.source_execution_sha256,
                "source_state_identity": source_identity,
                "paired_raw_payload_sha256": payloads.raw.sha256,
                "paired_errpilot_payload_sha256": payloads.errpilot.sha256,
                "errpilot_producing_run_identity": handoff.producing_run_identity,
            },
        )
        return written

    def _record_invalidated(
        self,
        *,
        case: CaseSpec,
        condition: str,
        condition_order: tuple[str, str],
        repetition: int,
        payload: ConditionPayload,
        payloads: PayloadPair,
        failure: CapturedFailure,
        handoff: ErrPilotHandoff,
        workspace: Path,
        artifact_root: Path,
        source_identity: str,
        invalid_reasons: list[str],
        adapter_identity: str,
        timeout_seconds: float,
    ) -> dict[str, object]:
        baseline = snapshot_tree(workspace)
        written = self._write_input_artifacts(
            case=case,
            condition=condition,
            payload=payload,
            payloads=payloads,
            failure=failure,
            handoff=handoff,
            baseline_manifest=baseline,
            artifact_root=artifact_root,
            source_identity=source_identity,
        )
        write_new_json(
            artifact_root / "derived/pre_run_validation.json",
            {"pass": False, "reasons": invalid_reasons},
        )
        written.append("derived/pre_run_validation.json")
        timestamp = self.now()
        record = self._base_record(
            case=case,
            condition=condition,
            condition_order=condition_order,
            repetition=repetition,
            payload=payload,
            source_identity=source_identity,
            adapter_identity=adapter_identity,
            timeout_seconds=timeout_seconds,
            start_time=timestamp,
            end_time=timestamp,
            elapsed_seconds=0.0,
            termination_reason="pre_run_case_identity_gate_failed",
            oracle_exit_code="NA",
            protected_integrity_pass="NA",
            changed_paths=[],
            repair_outcome="CASE_INVALIDATED",
            instrumentation=("NA", "NA", "NA", "NA_PRE_RUN_BLOCK"),
            flags={"case_invalid_reasons": list(invalid_reasons)},
            oracle_valid=False,
            oracle_expected_test_observed=False,
        )
        return self._finalize_record(artifact_root, written, record)

    def _run_session(
        self,
        *,
        case: CaseSpec,
        condition: str,
        condition_order: tuple[str, str],
        repetition: int,
        payload: ConditionPayload,
        payloads: PayloadPair,
        failure: CapturedFailure,
        handoff: ErrPilotHandoff,
        workspace: Path,
        artifact_root: Path,
        source_identity: str,
        adapter: SyntheticAgentAdapter,
        timeout_seconds: float,
    ) -> dict[str, object]:
        baseline = snapshot_tree(workspace)
        runtime_protected = capture_runtime_protected(workspace, case.protected_items)
        written = self._write_input_artifacts(
            case=case,
            condition=condition,
            payload=payload,
            payloads=payloads,
            failure=failure,
            handoff=handoff,
            baseline_manifest=baseline,
            artifact_root=artifact_root,
            source_identity=source_identity,
        )

        start_time = self.now()
        actual_start = time.monotonic()
        infrastructure_error: str | None = None
        agent_error = False
        try:
            adapter_result = _invoke_with_timeout(
                adapter, WorkspaceView(workspace), payload, timeout_seconds
            )
            adapter_result.validate()
        except _RepairBudgetExpired:
            adapter_result = AdapterResult(
                status="timeout",
                termination_reason="repair_budget_expired",
                stderr=b"synthetic adapter terminated at runner wall-clock boundary\n",
                duration_seconds=max(0.0, time.monotonic() - actual_start),
            )
        except AgentFailure as exc:
            agent_error = True
            adapter_result = AdapterResult(
                status="agent_error",
                termination_reason="synthetic_agent_failure",
                stderr=str(exc).encode("utf-8"),
                duration_seconds=max(0.0, time.monotonic() - actual_start),
            )
        except Exception as exc:  # noqa: BLE001 - boundary failures are evidence, not crashes.
            infrastructure_error = f"adapter_boundary_exception:{type(exc).__name__}"
            adapter_result = AdapterResult(
                status="completed",
                termination_reason="adapter_boundary_exception",
                stderr=str(exc).encode("utf-8", "backslashreplace"),
                duration_seconds=max(0.0, time.monotonic() - actual_start),
            )
        end_time = self.now()

        write_new_bytes(artifact_root / "raw/adapter_stdout.bin", adapter_result.stdout)
        write_new_bytes(artifact_root / "raw/adapter_stderr.bin", adapter_result.stderr)
        write_new_json(artifact_root / "raw/adapter_trace.json", list(adapter_result.trace))
        written.extend(
            ["raw/adapter_stdout.bin", "raw/adapter_stderr.bin", "raw/adapter_trace.json"]
        )

        after_agent = snapshot_tree(workspace)
        changes = diff_manifests(baseline, after_agent)
        changed_paths = [change["path"] for change in changes]
        write_new_json(artifact_root / "derived/workspace_diff.json", list(changes))
        written.append("derived/workspace_diff.json")

        integrity_before_oracle = verify_protected(
            workspace, case.protected_items, runtime_protected
        )
        write_new_json(
            artifact_root / "derived/protected_before_oracle.json", integrity_before_oracle
        )
        written.append("derived/protected_before_oracle.json")

        oracle_exit_code: int | str = "NA"
        oracle_stdout = b""
        oracle_stderr = b""
        oracle_expected_observed = False
        oracle_valid = False
        try:
            completed = subprocess.run(
                case.oracle_command,
                cwd=workspace,
                check=False,
                capture_output=True,
                timeout=self.oracle_timeout_seconds,
                env={
                    "PATH": os.environ.get("PATH", ""),
                    "LANG": "C",
                    "LC_ALL": "C",
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "PYTHONPATH": "",
                },
            )
            oracle_exit_code = completed.returncode
            oracle_stdout = completed.stdout
            oracle_stderr = completed.stderr
            marker = case.oracle_expected_marker.encode("utf-8")
            oracle_expected_observed = marker in oracle_stdout or marker in oracle_stderr
            oracle_valid = oracle_expected_observed
            if not oracle_valid:
                infrastructure_error = infrastructure_error or "oracle_expected_marker_not_observed"
        except (OSError, subprocess.SubprocessError) as exc:
            infrastructure_error = infrastructure_error or f"oracle_execution:{type(exc).__name__}"
            oracle_stderr = str(exc).encode("utf-8", "backslashreplace")

        write_new_bytes(artifact_root / "raw/oracle_stdout.bin", oracle_stdout)
        write_new_bytes(artifact_root / "raw/oracle_stderr.bin", oracle_stderr)
        write_new_json(
            artifact_root / "derived/oracle_result.json",
            {
                "command": list(case.oracle_command),
                "exit_code": oracle_exit_code,
                "expected_marker": case.oracle_expected_marker,
                "expected_test_observed": oracle_expected_observed,
                "oracle_valid": oracle_valid,
            },
        )
        written.extend(
            ["raw/oracle_stdout.bin", "raw/oracle_stderr.bin", "derived/oracle_result.json"]
        )

        integrity_after_oracle = verify_protected(
            workspace, case.protected_items, runtime_protected
        )
        write_new_json(
            artifact_root / "derived/protected_after_oracle.json", integrity_after_oracle
        )
        written.append("derived/protected_after_oracle.json")

        protected_pass = bool(integrity_before_oracle["pass"] and integrity_after_oracle["pass"])
        if integrity_before_oracle["pass"] and not integrity_after_oracle["pass"]:
            infrastructure_error = infrastructure_error or "verifier_changed_protected_item"
        timed_out = (
            adapter_result.status == "timeout" or adapter_result.duration_seconds >= timeout_seconds
        )
        agent_error = agent_error or adapter_result.status == "agent_error"

        if not integrity_before_oracle["pass"]:
            outcome = "REPAIR_FAILURE_TEST_MUTATION"
        elif timed_out:
            outcome = "REPAIR_TIMEOUT"
        elif agent_error:
            outcome = "AGENT_ERROR"
        elif infrastructure_error is not None:
            outcome = "INFRASTRUCTURE_ERROR"
        elif oracle_valid and oracle_exit_code == 0:
            outcome = "REPAIR_SUCCESS"
        else:
            outcome = "REPAIR_FAILURE_ORACLE"

        flags = {
            "timed_out": timed_out,
            "agent_error": agent_error,
            "infrastructure_error": infrastructure_error or "NA",
            "protected_before_oracle_issues": integrity_before_oracle["issues"],
            "protected_after_oracle_issues": integrity_after_oracle["issues"],
        }
        record = self._base_record(
            case=case,
            condition=condition,
            condition_order=condition_order,
            repetition=repetition,
            payload=payload,
            source_identity=source_identity,
            adapter_identity=adapter.identity,
            timeout_seconds=timeout_seconds,
            start_time=start_time,
            end_time=end_time,
            elapsed_seconds=adapter_result.duration_seconds,
            termination_reason=adapter_result.termination_reason,
            oracle_exit_code=oracle_exit_code,
            protected_integrity_pass=protected_pass,
            changed_paths=changed_paths,
            repair_outcome=outcome,
            instrumentation=(
                adapter_result.test_invocations_total,
                adapter_result.oracle_invocations_total,
                adapter_result.post_edit_failed_oracle_count,
                adapter_result.instrumentation_status,
            ),
            flags=flags,
            oracle_valid=oracle_valid,
            oracle_expected_test_observed=oracle_expected_observed,
        )
        return self._finalize_record(artifact_root, written, record)

    def _base_record(
        self,
        *,
        case: CaseSpec,
        condition: str,
        condition_order: tuple[str, str],
        repetition: int,
        payload: ConditionPayload,
        source_identity: str,
        adapter_identity: str,
        timeout_seconds: float,
        start_time: str,
        end_time: str,
        elapsed_seconds: float,
        termination_reason: str,
        oracle_exit_code: int | str,
        protected_integrity_pass: bool | str,
        changed_paths: list[str],
        repair_outcome: str,
        instrumentation: tuple[int | str, int | str, int | str, str],
        flags: dict[str, object],
        oracle_valid: bool,
        oracle_expected_test_observed: bool,
    ) -> dict[str, object]:
        return {
            "schema_version": RESULT_SCHEMA_VERSION,
            "case_id": case.case_id,
            "condition": condition,
            "repetition": repetition,
            "condition_order": list(condition_order),
            "protocol_version": case.protocol_version,
            "protocol_sha256": case.protocol_sha256,
            "run_spec_version": case.run_spec_version,
            "run_spec_sha256": case.run_spec_sha256,
            "source_revision": case.source_revision,
            "fixed_revision": case.fixed_revision,
            "source_state_identity": source_identity,
            "environment_identity": case.environment_identity.to_dict(),
            "errpilot_revision": case.errpilot_revision,
            "codex_cli_version": "NA",
            "model_identifier": "NA",
            "reasoning_effort": "NA",
            "agent_adapter_identity": adapter_identity,
            "payload_sha256": payload.sha256,
            "source_execution_id": payload.source_execution_id,
            "source_execution_sha256": payload.source_execution_sha256,
            "start_time": start_time,
            "end_time": end_time,
            "elapsed_seconds": elapsed_seconds,
            "timeout_seconds": timeout_seconds,
            "termination_reason": termination_reason,
            "oracle_exit_code": oracle_exit_code,
            "oracle_valid": oracle_valid,
            "oracle_expected_test_observed": oracle_expected_test_observed,
            "protected_integrity_pass": protected_integrity_pass,
            "changed_paths": changed_paths,
            "repair_outcome": repair_outcome,
            "test_invocations_total": instrumentation[0],
            "oracle_invocations_total": instrumentation[1],
            "post_edit_failed_oracle_count": instrumentation[2],
            "instrumentation_status": instrumentation[3],
            "flags": flags,
            "artifact_references": {},
        }

    def _finalize_record(
        self,
        artifact_root: Path,
        written: list[str],
        record: dict[str, object],
    ) -> dict[str, object]:
        index = artifact_index(artifact_root, written)
        write_new_json(artifact_root / "evidence_index.json", index)
        evidence_index_sha256 = sha256_bytes((artifact_root / "evidence_index.json").read_bytes())
        record["artifact_references"] = {
            "artifact_root": ".",
            "evidence_index": "evidence_index.json",
            "evidence_index_sha256": evidence_index_sha256,
            "raw_payload": "raw/payload.bin",
        }
        record["result_sha256"] = result_record_sha256(record)
        validate_result_record(record)
        write_new_json(artifact_root / "result.json", record)
        return record


def result_record_sha256(record: Mapping[str, object]) -> str:
    unhashed = dict(record)
    unhashed.pop("result_sha256", None)
    return sha256_bytes(canonical_json_bytes(unhashed))


def validate_result_record(record: Mapping[str, object]) -> None:
    required = {
        "schema_version",
        "case_id",
        "condition",
        "repetition",
        "condition_order",
        "protocol_version",
        "source_revision",
        "environment_identity",
        "errpilot_revision",
        "codex_cli_version",
        "model_identifier",
        "reasoning_effort",
        "payload_sha256",
        "start_time",
        "end_time",
        "elapsed_seconds",
        "termination_reason",
        "oracle_exit_code",
        "protected_integrity_pass",
        "changed_paths",
        "repair_outcome",
        "test_invocations_total",
        "oracle_invocations_total",
        "post_edit_failed_oracle_count",
        "instrumentation_status",
        "artifact_references",
        "result_sha256",
    }
    missing = sorted(required - set(record))
    if missing:
        raise ValueError(f"result record is missing fields: {', '.join(missing)}")
    if record["schema_version"] != RESULT_SCHEMA_VERSION:
        raise ValueError("unsupported result schema version")
    if record["condition"] not in CONDITIONS:
        raise ValueError("unknown result condition")
    if record["repair_outcome"] not in OUTCOMES:
        raise ValueError("unknown repair outcome")
    if record["result_sha256"] != result_record_sha256(record):
        raise ValueError("result_sha256 does not match canonical record bytes")
    if record["repair_outcome"] == "REPAIR_SUCCESS":
        if record["oracle_exit_code"] != 0 or not record["oracle_valid"]:
            raise ValueError("success requires a valid passing runner oracle")
        if record["protected_integrity_pass"] is not True:
            raise ValueError("success requires protected integrity")
        if record["flags"].get("timed_out"):
            raise ValueError("success cannot also be a timeout")
    for field in (
        "test_invocations_total",
        "oracle_invocations_total",
        "post_edit_failed_oracle_count",
    ):
        value = record[field]
        if value != "NA" and (not isinstance(value, int) or value < 0):
            raise ValueError(f"{field} must be a non-negative integer or NA")

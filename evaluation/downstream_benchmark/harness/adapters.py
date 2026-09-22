"""Small, deterministic synthetic-agent boundary; no live adapter exists."""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Protocol, Sequence

from .errors import AgentFailure, WorkspaceAccessError
from .models import AdapterResult, ConditionPayload
from .filesystem import WorkspaceView


class SyntheticAgentAdapter(Protocol):
    """Future live adapters may implement a similar boundary in another transaction.

    This harness accepts only objects explicitly marked ``synthetic_only``.
    """

    identity: str
    synthetic_only: bool

    def run(
        self,
        workspace: WorkspaceView,
        payload: ConditionPayload,
        timeout_seconds: float,
    ) -> AdapterResult: ...


@dataclass(frozen=True)
class Action:
    operation: str
    path: str
    data: bytes = b""
    destination: str | None = None


class ScriptedAdapter:
    synthetic_only = True

    def __init__(
        self,
        identity: str,
        actions: Sequence[Action] = (),
        *,
        status: str = "completed",
        duration_seconds: float = 0.001,
        wall_time_seconds: float = 0.0,
        raise_agent_failure: bool = False,
        instrumentation_known: bool = False,
    ):
        self.identity = identity
        self.actions = tuple(actions)
        self.status = status
        self.duration_seconds = duration_seconds
        self.wall_time_seconds = wall_time_seconds
        self.raise_agent_failure = raise_agent_failure
        self.instrumentation_known = instrumentation_known
        self.call_count = 0

    def run(
        self,
        workspace: WorkspaceView,
        payload: ConditionPayload,
        timeout_seconds: float,
    ) -> AdapterResult:
        self.call_count += 1
        if self.raise_agent_failure:
            raise AgentFailure("synthetic attributable adapter failure")
        trace: list[dict[str, object]] = []
        for action in self.actions:
            if action.operation == "write":
                workspace.write_bytes(action.path, action.data)
            elif action.operation == "replace":
                workspace.replace_bytes(action.path, action.data)
            elif action.operation == "delete":
                workspace.delete(action.path)
            elif action.operation == "rename" and action.destination is not None:
                workspace.rename(action.path, action.destination)
            else:
                raise ValueError(f"unsupported synthetic action: {action.operation}")
            trace.append({"operation": action.operation, "path": action.path})
        if self.wall_time_seconds:
            time.sleep(self.wall_time_seconds)
        if self.instrumentation_known:
            instrumentation = (0, 0, 0, "SYNTHETIC_EXPLICIT_ZERO_EVENTS")
        else:
            instrumentation = ("NA", "NA", "NA", "NA_SYNTHETIC_TRACE_NOT_AUTHORITATIVE")
        return AdapterResult(
            status=self.status,
            termination_reason=self.status,
            stdout=f"synthetic adapter {self.identity}\n".encode("utf-8"),
            stderr=b"",
            trace=tuple(trace),
            duration_seconds=self.duration_seconds,
            test_invocations_total=instrumentation[0],
            oracle_invocations_total=instrumentation[1],
            post_edit_failed_oracle_count=instrumentation[2],
            instrumentation_status=instrumentation[3],
        )


class IsolationProbeAdapter(ScriptedAdapter):
    """Synthetic adapter that records ordinary-interface escape attempts."""

    def __init__(self, identity: str, probes: Sequence[str]):
        super().__init__(identity)
        self.probes = tuple(probes)
        self.probe_blocked: list[bool] = []

    def run(
        self,
        workspace: WorkspaceView,
        payload: ConditionPayload,
        timeout_seconds: float,
    ) -> AdapterResult:
        self.call_count += 1
        for path in self.probes:
            try:
                workspace.read_bytes(path)
            except (WorkspaceAccessError, FileNotFoundError, IsADirectoryError):
                self.probe_blocked.append(True)
            else:
                self.probe_blocked.append(False)
        return AdapterResult(
            status="completed",
            termination_reason="completed",
            stdout=b"synthetic isolation probes complete\n",
            duration_seconds=0.001,
        )

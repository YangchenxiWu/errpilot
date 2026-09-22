"""Synthetic-only validation harness for the frozen downstream benchmark."""

from .adapters import Action, IsolationProbeAdapter, ScriptedAdapter, SyntheticAgentAdapter
from .constants import (
    CASE_SCHEMA_VERSION,
    CONDITIONS,
    DEFAULT_REPAIR_TIMEOUT_SECONDS,
    OUTCOMES,
    PROTOCOL_SHA256,
    PROTOCOL_VERSION,
    RESULT_SCHEMA_VERSION,
    RUN_SPEC_SHA256,
    RUN_SPEC_VERSION,
    TASK_INSTRUCTION,
    TASK_INSTRUCTION_SHA256,
)
from .errors import (
    AgentFailure,
    ArtifactCollision,
    CaseSpecError,
    HarnessError,
    ProvenanceMismatch,
    WorkspaceAccessError,
)
from .filesystem import (
    manifest_sha256,
    protected_manifest,
    snapshot_tree,
)
from .models import (
    AdapterResult,
    CapturedFailure,
    CaseSpec,
    ConditionPayload,
    EnvironmentIdentity,
    ErrPilotHandoff,
    ProtectedItem,
)
from .payloads import PayloadPair, build_payload_pair, decode_frame
from .runner import BenchmarkRunner, result_record_sha256, validate_result_record

__all__ = [
    "Action",
    "AdapterResult",
    "AgentFailure",
    "ArtifactCollision",
    "BenchmarkRunner",
    "CASE_SCHEMA_VERSION",
    "CONDITIONS",
    "CapturedFailure",
    "CaseSpec",
    "CaseSpecError",
    "ConditionPayload",
    "DEFAULT_REPAIR_TIMEOUT_SECONDS",
    "EnvironmentIdentity",
    "ErrPilotHandoff",
    "HarnessError",
    "IsolationProbeAdapter",
    "OUTCOMES",
    "PROTOCOL_SHA256",
    "PROTOCOL_VERSION",
    "PayloadPair",
    "ProtectedItem",
    "ProvenanceMismatch",
    "RESULT_SCHEMA_VERSION",
    "RUN_SPEC_SHA256",
    "RUN_SPEC_VERSION",
    "ScriptedAdapter",
    "SyntheticAgentAdapter",
    "TASK_INSTRUCTION",
    "TASK_INSTRUCTION_SHA256",
    "WorkspaceAccessError",
    "build_payload_pair",
    "decode_frame",
    "manifest_sha256",
    "protected_manifest",
    "result_record_sha256",
    "snapshot_tree",
    "validate_result_record",
]

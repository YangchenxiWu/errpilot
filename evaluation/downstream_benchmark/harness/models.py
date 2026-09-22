"""Machine-readable identities and records for the synthetic harness."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any, Mapping, Sequence

from .constants import (
    CASE_SCHEMA_VERSION,
    PROTOCOL_SHA256,
    PROTOCOL_VERSION,
    RUN_SPEC_SHA256,
    RUN_SPEC_VERSION,
)
from .errors import CaseSpecError

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$")


def _require_text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CaseSpecError(f"{name} must be a non-empty string")
    return value


def _require_safe_id(name: str, value: object) -> str:
    text = _require_text(name, value)
    if not _SAFE_ID_RE.fullmatch(text):
        raise CaseSpecError(f"{name} contains unsupported characters")
    return text


def _require_sha256(name: str, value: object) -> str:
    text = _require_text(name, value)
    if not _SHA256_RE.fullmatch(text):
        raise CaseSpecError(f"{name} must be a lowercase SHA-256 digest")
    return text


@dataclass(frozen=True)
class EnvironmentIdentity:
    immutable_id: str
    python_version: str
    dependency_identity: str

    @classmethod
    def from_mapping(cls, value: object) -> "EnvironmentIdentity":
        if not isinstance(value, Mapping):
            raise CaseSpecError("environment_identity must be an object")
        return cls(
            immutable_id=_require_text(
                "environment_identity.immutable_id", value.get("immutable_id")
            ),
            python_version=_require_text(
                "environment_identity.python_version", value.get("python_version")
            ),
            dependency_identity=_require_text(
                "environment_identity.dependency_identity", value.get("dependency_identity")
            ),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "immutable_id": self.immutable_id,
            "python_version": self.python_version,
            "dependency_identity": self.dependency_identity,
        }


@dataclass(frozen=True)
class ProtectedItem:
    path: str
    item_type: str
    mode: int
    size: int
    sha256: str
    children_sha256: str | None = None

    @classmethod
    def from_mapping(cls, value: object) -> "ProtectedItem":
        if not isinstance(value, Mapping):
            raise CaseSpecError("each protected item must be an object")
        path = _require_text("protected_items.path", value.get("path"))
        if path.startswith("/") or ".." in path.split("/"):
            raise CaseSpecError("protected item paths must be normalized relative paths")
        item_type = value.get("item_type")
        if item_type not in {"file", "directory", "symlink"}:
            raise CaseSpecError("protected_items.item_type is invalid")
        mode = value.get("mode")
        size = value.get("size")
        if not isinstance(mode, int) or mode < 0:
            raise CaseSpecError("protected_items.mode must be a non-negative integer")
        if not isinstance(size, int) or size < 0:
            raise CaseSpecError("protected_items.size must be a non-negative integer")
        children = value.get("children_sha256")
        if children is not None:
            children = _require_sha256("protected_items.children_sha256", children)
        if item_type == "directory" and children is None:
            raise CaseSpecError("protected directories require children_sha256")
        return cls(
            path=path,
            item_type=item_type,
            mode=mode,
            size=size,
            sha256=_require_sha256("protected_items.sha256", value.get("sha256")),
            children_sha256=children,
        )

    def to_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "path": self.path,
            "item_type": self.item_type,
            "mode": self.mode,
            "size": self.size,
            "sha256": self.sha256,
        }
        if self.children_sha256 is not None:
            result["children_sha256"] = self.children_sha256
        return result


@dataclass(frozen=True)
class CaseSpec:
    schema_version: str
    execution_mode: str
    case_id: str
    source_project: str
    source_revision: str
    fixed_revision: str
    failing_command: str
    oracle_command: tuple[str, ...]
    oracle_expected_marker: str
    workspace_identity: str
    protected_items: tuple[ProtectedItem, ...]
    environment_identity: EnvironmentIdentity
    sample_role: str
    protocol_version: str
    protocol_sha256: str
    run_spec_version: str
    run_spec_sha256: str
    errpilot_revision: str
    errpilot_configuration_sha256: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> "CaseSpec":
        if not isinstance(value, Mapping):
            raise CaseSpecError("case specification must be an object")
        required = {
            "schema_version",
            "execution_mode",
            "case_id",
            "source_project",
            "source_revision",
            "fixed_revision",
            "failing_command",
            "oracle_command",
            "oracle_expected_marker",
            "workspace_identity",
            "protected_items",
            "environment_identity",
            "sample_role",
            "protocol_version",
            "protocol_sha256",
            "run_spec_version",
            "run_spec_sha256",
            "errpilot_revision",
            "errpilot_configuration_sha256",
        }
        missing = sorted(required - set(value))
        if missing:
            raise CaseSpecError(f"missing required case identities: {', '.join(missing)}")
        unknown = sorted(set(value) - required)
        if unknown:
            raise CaseSpecError(f"unknown case-specification fields: {', '.join(unknown)}")

        oracle_command = value.get("oracle_command")
        if (
            not isinstance(oracle_command, Sequence)
            or isinstance(oracle_command, (str, bytes))
            or not oracle_command
            or any(not isinstance(part, str) or not part for part in oracle_command)
        ):
            raise CaseSpecError("oracle_command must be a non-empty array of non-empty strings")

        protected_value = value.get("protected_items")
        if (
            not isinstance(protected_value, Sequence)
            or isinstance(protected_value, (str, bytes))
            or not protected_value
        ):
            raise CaseSpecError("protected_items must be a non-empty array")
        protected = tuple(ProtectedItem.from_mapping(item) for item in protected_value)
        paths = [item.path for item in protected]
        if len(paths) != len(set(paths)):
            raise CaseSpecError("protected item paths must be unique")

        result = cls(
            schema_version=_require_text("schema_version", value.get("schema_version")),
            execution_mode=_require_text("execution_mode", value.get("execution_mode")),
            case_id=_require_safe_id("case_id", value.get("case_id")),
            source_project=_require_safe_id("source_project", value.get("source_project")),
            source_revision=_require_text("source_revision", value.get("source_revision")),
            fixed_revision=_require_text("fixed_revision", value.get("fixed_revision")),
            failing_command=_require_text("failing_command", value.get("failing_command")),
            oracle_command=tuple(oracle_command),
            oracle_expected_marker=_require_text(
                "oracle_expected_marker", value.get("oracle_expected_marker")
            ),
            workspace_identity=_require_sha256(
                "workspace_identity", value.get("workspace_identity")
            ),
            protected_items=protected,
            environment_identity=EnvironmentIdentity.from_mapping(
                value.get("environment_identity")
            ),
            sample_role=_require_text("sample_role", value.get("sample_role")),
            protocol_version=_require_text("protocol_version", value.get("protocol_version")),
            protocol_sha256=_require_sha256("protocol_sha256", value.get("protocol_sha256")),
            run_spec_version=_require_text("run_spec_version", value.get("run_spec_version")),
            run_spec_sha256=_require_sha256("run_spec_sha256", value.get("run_spec_sha256")),
            errpilot_revision=_require_text("errpilot_revision", value.get("errpilot_revision")),
            errpilot_configuration_sha256=_require_sha256(
                "errpilot_configuration_sha256", value.get("errpilot_configuration_sha256")
            ),
        )
        result.validate_authority()
        return result

    @classmethod
    def from_json_bytes(cls, data: bytes) -> "CaseSpec":
        try:
            value = json.loads(data)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CaseSpecError("case specification is not valid UTF-8 JSON") from exc
        return cls.from_mapping(value)

    def validate_authority(self) -> None:
        if self.schema_version != CASE_SCHEMA_VERSION:
            raise CaseSpecError("unsupported case schema version")
        if self.execution_mode != "synthetic_validation":
            raise CaseSpecError("this harness refuses non-synthetic execution")
        if self.sample_role != "synthetic_fixture":
            raise CaseSpecError("synthetic cases must use sample_role=synthetic_fixture")
        if self.protocol_version != PROTOCOL_VERSION or self.protocol_sha256 != PROTOCOL_SHA256:
            raise CaseSpecError("protocol identity does not match the frozen authority")
        if self.run_spec_version != RUN_SPEC_VERSION or self.run_spec_sha256 != RUN_SPEC_SHA256:
            raise CaseSpecError("run-specification identity does not match the frozen authority")

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "execution_mode": self.execution_mode,
            "case_id": self.case_id,
            "source_project": self.source_project,
            "source_revision": self.source_revision,
            "fixed_revision": self.fixed_revision,
            "failing_command": self.failing_command,
            "oracle_command": list(self.oracle_command),
            "oracle_expected_marker": self.oracle_expected_marker,
            "workspace_identity": self.workspace_identity,
            "protected_items": [item.to_dict() for item in self.protected_items],
            "environment_identity": self.environment_identity.to_dict(),
            "sample_role": self.sample_role,
            "protocol_version": self.protocol_version,
            "protocol_sha256": self.protocol_sha256,
            "run_spec_version": self.run_spec_version,
            "run_spec_sha256": self.run_spec_sha256,
            "errpilot_revision": self.errpilot_revision,
            "errpilot_configuration_sha256": self.errpilot_configuration_sha256,
        }


@dataclass(frozen=True)
class CapturedFailure:
    source_execution_id: str
    source_state_sha256: str
    failing_command: str
    stdout: bytes
    stderr: bytes


@dataclass(frozen=True)
class ErrPilotHandoff:
    source_execution_id: str
    source_state_sha256: str
    artifact: bytes
    producing_run_identity: str


@dataclass(frozen=True)
class ConditionPayload:
    condition: str
    bytes_value: bytes
    sha256: str
    source_execution_id: str
    source_execution_sha256: str


@dataclass(frozen=True)
class AdapterResult:
    status: str
    termination_reason: str
    stdout: bytes = b""
    stderr: bytes = b""
    trace: tuple[Mapping[str, Any], ...] = ()
    duration_seconds: float = 0.0
    test_invocations_total: int | str = "NA"
    oracle_invocations_total: int | str = "NA"
    post_edit_failed_oracle_count: int | str = "NA"
    instrumentation_status: str = "NA_SYNTHETIC_TRACE_NOT_AUTHORITATIVE"

    def validate(self) -> None:
        if self.status not in {"completed", "timeout", "agent_error"}:
            raise ValueError("unsupported synthetic adapter status")
        if self.duration_seconds < 0:
            raise ValueError("adapter duration cannot be negative")
        for name in (
            "test_invocations_total",
            "oracle_invocations_total",
            "post_edit_failed_oracle_count",
        ):
            value = getattr(self, name)
            if value != "NA" and (not isinstance(value, int) or value < 0):
                raise ValueError(f"{name} must be a non-negative integer or NA")

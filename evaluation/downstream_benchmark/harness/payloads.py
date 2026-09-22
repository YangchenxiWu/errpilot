"""Deterministic RAW and ERRPILOT payload construction."""

from __future__ import annotations

from dataclasses import dataclass

from .constants import CONDITIONS, PAYLOAD_MAGIC, TASK_INSTRUCTION
from .errors import ProvenanceMismatch
from .filesystem import sha256_bytes, sha256_json
from .models import CapturedFailure, CaseSpec, ConditionPayload, ErrPilotHandoff


def _frame(fields: tuple[tuple[bytes, bytes], ...]) -> bytes:
    payload = bytearray(PAYLOAD_MAGIC)
    for name, value in fields:
        if not name.isascii() or b"\n" in name or b":" in name:
            raise ValueError("payload field names must be simple ASCII")
        payload.extend(name)
        payload.extend(b":")
        payload.extend(str(len(value)).encode("ascii"))
        payload.extend(b"\n")
        payload.extend(value)
    return bytes(payload)


def decode_frame(payload: bytes) -> tuple[tuple[str, bytes], ...]:
    """Decode the length-framed format for validation; no text normalization occurs."""
    if not payload.startswith(PAYLOAD_MAGIC):
        raise ValueError("invalid payload magic")
    position = len(PAYLOAD_MAGIC)
    fields: list[tuple[str, bytes]] = []
    while position < len(payload):
        newline = payload.find(b"\n", position)
        if newline < 0:
            raise ValueError("truncated field header")
        header = payload[position:newline]
        try:
            name_bytes, size_bytes = header.split(b":", 1)
            size = int(size_bytes.decode("ascii"))
            name = name_bytes.decode("ascii")
        except (ValueError, UnicodeDecodeError) as exc:
            raise ValueError("invalid field header") from exc
        start = newline + 1
        end = start + size
        if size < 0 or end > len(payload):
            raise ValueError("truncated field value")
        fields.append((name, payload[start:end]))
        position = end
    return tuple(fields)


@dataclass(frozen=True)
class PayloadPair:
    raw: ConditionPayload
    errpilot: ConditionPayload

    def for_condition(self, condition: str) -> ConditionPayload:
        if condition == CONDITIONS[0]:
            return self.raw
        if condition == CONDITIONS[1]:
            return self.errpilot
        raise KeyError(condition)


def build_payload_pair(
    case: CaseSpec,
    failure: CapturedFailure,
    handoff: ErrPilotHandoff,
) -> PayloadPair:
    if failure.source_execution_id != handoff.source_execution_id:
        raise ProvenanceMismatch("source execution IDs differ")
    if failure.source_state_sha256 != handoff.source_state_sha256:
        raise ProvenanceMismatch("source-state identities differ")
    if failure.source_state_sha256 != case.workspace_identity:
        raise ProvenanceMismatch("captured failure does not match the case source state")
    if failure.failing_command != case.failing_command:
        raise ProvenanceMismatch("captured failing command differs from the case specification")
    if not failure.stdout and not failure.stderr:
        raise ProvenanceMismatch("captured failure must preserve at least one non-empty stream")
    if not handoff.artifact:
        raise ProvenanceMismatch("ErrPilot handoff artifact is empty")

    source_execution_sha256 = sha256_json(
        {
            "source_execution_id": failure.source_execution_id,
            "source_state_sha256": failure.source_state_sha256,
            "failing_command_sha256": sha256_bytes(failure.failing_command.encode("utf-8")),
            "stdout_sha256": sha256_bytes(failure.stdout),
            "stderr_sha256": sha256_bytes(failure.stderr),
        }
    )
    raw_bytes = _frame(
        (
            (b"TASK", TASK_INSTRUCTION),
            (b"FAILING_COMMAND", failure.failing_command.encode("utf-8")),
            (b"STDOUT", failure.stdout),
            (b"STDERR", failure.stderr),
        )
    )
    errpilot_bytes = _frame(((b"TASK", TASK_INSTRUCTION), (b"HANDOFF", handoff.artifact)))
    return PayloadPair(
        raw=ConditionPayload(
            condition="RAW",
            bytes_value=raw_bytes,
            sha256=sha256_bytes(raw_bytes),
            source_execution_id=failure.source_execution_id,
            source_execution_sha256=source_execution_sha256,
        ),
        errpilot=ConditionPayload(
            condition="ERRPILOT",
            bytes_value=errpilot_bytes,
            sha256=sha256_bytes(errpilot_bytes),
            source_execution_id=failure.source_execution_id,
            source_execution_sha256=source_execution_sha256,
        ),
    )

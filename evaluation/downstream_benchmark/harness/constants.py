"""Frozen values used by the synthetic downstream-benchmark harness."""

from __future__ import annotations

import hashlib

PROTOCOL_VERSION = "EP-DBP-1"
RUN_SPEC_VERSION = "EP-DBRS-1"
PROTOCOL_SHA256 = "34e014a07821dc9dca52178874eef0b847aee7f048071fb4920864ae5d3bee93"
RUN_SPEC_SHA256 = "29ab6f78739d0eeea1c2a774e62e2d133f173e160c3d247407970a80726f4406"

TASK_INSTRUCTION = (
    b"Repair the defect in this repository that is exposed by the provided failure evidence. "
    b"Do not modify tests or benchmark infrastructure. Preserve unrelated behavior. You may "
    b"inspect the repository and run local commands/tests as needed. Before finishing, verify "
    b"the preregistered oracle and report the changes made."
)
TASK_INSTRUCTION_SHA256 = "0350885984c9dff5202f66e5cbba04be49982de42e2d14b1e1e7b0db0a60fb0d"

DEFAULT_REPAIR_TIMEOUT_SECONDS = 1200.0
PAYLOAD_FORMAT_VERSION = "EP-DBPAYLOAD-1"
PAYLOAD_MAGIC = PAYLOAD_FORMAT_VERSION.encode("ascii") + b"\x00"
CASE_SCHEMA_VERSION = "EP-DB-CASE-1"
RESULT_SCHEMA_VERSION = "EP-DB-RESULT-1"

CONDITIONS = ("RAW", "ERRPILOT")
OUTCOMES = (
    "REPAIR_SUCCESS",
    "REPAIR_FAILURE_ORACLE",
    "REPAIR_FAILURE_TEST_MUTATION",
    "REPAIR_TIMEOUT",
    "AGENT_ERROR",
    "INFRASTRUCTURE_ERROR",
    "CASE_INVALIDATED",
)


def _assert_frozen_instruction() -> None:
    actual = hashlib.sha256(TASK_INSTRUCTION).hexdigest()
    if actual != TASK_INSTRUCTION_SHA256:
        raise RuntimeError("frozen task-instruction bytes do not match RUN_SPEC_V1")


_assert_frozen_instruction()

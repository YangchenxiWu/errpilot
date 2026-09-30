"""Explicit first-pass governance binding; validation performs no runtime work.

The existing command token is required separately. This unsigned envelope is
inspectable benchmark authority, not authentication or an attempt/retry ledger.
No authority is inferred from accepted preparation or created on import.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from . import block_03_materializer_bridge as bridge, materializer as m


SCHEMA = "BLOCK_03_RUNTIME_ACTIVATION_AUTHORITY_V1"
TRANSACTION = "BLOCK_03_FIRST_PASS_MATERIALIZATION"
BASELINE_COMMIT = "314229cc2dc6d4d1e8721a43e5b9189136a64b67"
LIFECYCLE_FILE = "BLOCK_03_PRE_MATERIALIZATION_LIFECYCLE_CLOSURE_V1.md"
LIFECYCLE_SHA256 = "8e76134f696f182b8910c0032b24e0027470f4debc375aa85aaa1f5c82a8ca6a"
MEMBER_RANKS = (259, 369, 380, 405, 431, 472, 485)


def _deny(message: str) -> None:
    raise m.Blocked("BLOCKED_AUTHORITY", message)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _deny("duplicate runtime authority field")
        result[key] = value
    return result


def read_authority(path: Path | None) -> dict[str, Any]:
    """Read an explicitly supplied JSON object, rejecting ambiguity and symlinks."""
    try:
        if path is None or path.is_symlink() or not path.is_file():
            _deny("Block 03 explicit runtime authority required")
        value = json.loads(path.read_bytes(), object_pairs_hook=_unique_object)
        if not isinstance(value, dict):
            _deny("Block 03 runtime authority object required")
        return value
    except (OSError, TypeError, ValueError, RecursionError) as exc:
        if isinstance(exc, m.Blocked):
            raise
        raise m.Blocked("BLOCKED_AUTHORITY", "malformed Block 03 runtime authority") from exc


def validate_authority(authority: dict[str, Any] | None) -> None:
    """Require the exact envelope and accepted historical baseline, without writes.

    The baseline names immutable input authority, not the future controller
    commit. A clean committed materializer is still required by the dispatcher.
    Accepted recipes and external evidence remain checked by the input bridge.
    """
    expected = {
        "schema": SCHEMA,
        "transaction": TRANSACTION,
        "baseline_commit": BASELINE_COMMIT,
        "block_identity_sha256": bridge.BLOCK_SHA256,
        "ordered_case_ids": list(bridge.MEMBERS),
        "ordered_candidate_ranks": list(MEMBER_RANKS),
        "materializer_input_authority_sha256": bridge.AUTHORITY_SHA256,
        "lifecycle_record_sha256": LIFECYCLE_SHA256,
        "authority_decision": "HUMAN_PI_AUTHORIZED",
    }
    try:
        # Serialized comparison distinguishes JSON integers from bools/floats,
        # rejects unknown/missing fields, and makes membership order normative.
        if not isinstance(authority, dict) or m.canonical_json(authority) != m.canonical_json(expected):
            _deny("Block 03 first-pass materialization not authorized: exact runtime binding required")
        for name, digest in ((LIFECYCLE_FILE, LIFECYCLE_SHA256),
                             (bridge.AUTHORITY_FILE, bridge.AUTHORITY_SHA256)):
            path = m.BENCHMARK / name
            if path.is_symlink() or not path.is_file() or m.sha256(path.read_bytes()) != digest:
                _deny("Block 03 accepted authority changed")
            relative = path.relative_to(m.BENCHMARK.parents[1]).as_posix()
            result = subprocess.run(
                ["git", "cat-file", "blob", f"{BASELINE_COMMIT}:{relative}"],
                cwd=m.BENCHMARK, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
            )
            if result.returncode or m.sha256(result.stdout) != digest:
                _deny("Block 03 committed baseline authority unavailable or mismatched")
    except (OSError, TypeError, ValueError, RecursionError) as exc:
        if isinstance(exc, m.Blocked):
            raise
        raise m.Blocked("BLOCKED_AUTHORITY", "malformed Block 03 runtime authority") from exc

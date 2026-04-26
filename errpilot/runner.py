"""Command execution and run artifact capture."""

from __future__ import annotations

import json
import shlex
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from errpilot.storage import ensure_run_dir, update_latest_pointer


@dataclass(frozen=True)
class CapturedRun:
    """Summary of a captured command run."""

    run_id: str
    run_dir: Path
    exit_code: int


def capture_command(command: tuple[str, ...], cwd: Path | None = None) -> CapturedRun:
    """Execute a command and persist the Day 2 run artifacts."""
    if not command:
        raise ValueError("command must not be empty")

    working_dir = cwd or Path.cwd()
    run_id = _new_run_id()
    run_dir = ensure_run_dir(run_id, working_dir)

    started = time.monotonic()
    started_at = datetime.now(timezone.utc)
    completed = _run_command(command, working_dir)
    finished_at = datetime.now(timezone.utc)
    duration_ms = int((time.monotonic() - started) * 1000)

    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    metadata = {
        "schema_version": "0.1",
        "run_id": run_id,
        "command": list(command),
        "command_display": _display_command(command),
        "cwd": str(working_dir),
        "execution_mode": _execution_mode(command),
        "exit_code": completed.returncode,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "duration_ms": duration_ms,
    }

    (run_dir / "stdout.log").write_text(stdout, encoding="utf-8")
    (run_dir / "stderr.log").write_text(stderr, encoding="utf-8")
    (run_dir / "combined.log").write_text(_combined_log(stdout, stderr), encoding="utf-8")
    (run_dir / "command.txt").write_text(f"{metadata['command_display']}\n", encoding="utf-8")
    (run_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    update_latest_pointer(run_id, working_dir)

    return CapturedRun(run_id=run_id, run_dir=run_dir, exit_code=completed.returncode)


def _run_command(command: tuple[str, ...], cwd: Path) -> subprocess.CompletedProcess[str]:
    try:
        if len(command) == 1:
            return subprocess.run(command[0], cwd=cwd, shell=True, capture_output=True, text=True)
        return subprocess.run(command, cwd=cwd, shell=False, capture_output=True, text=True)
    except FileNotFoundError as exc:
        return subprocess.CompletedProcess(command, 127, stdout="", stderr=f"{exc}\n")


def _display_command(command: tuple[str, ...]) -> str:
    if len(command) == 1:
        return command[0]
    return shlex.join(command)


def _execution_mode(command: tuple[str, ...]) -> str:
    if len(command) == 1:
        return "shell"
    return "exec"


def _combined_log(stdout: str, stderr: str) -> str:
    parts: list[str] = []
    if stdout:
        parts.append(stdout)
    if stderr:
        if parts and not parts[-1].endswith("\n"):
            parts[-1] += "\n"
        parts.append(stderr)
    return "".join(parts)


def _new_run_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{timestamp}-{uuid4().hex[:8]}"

"""Filesystem storage helpers for ErrPilot runs."""

from __future__ import annotations

import os
from pathlib import Path


RUNS_DIR = Path(".errpilot") / "runs"
LATEST_POINTER = Path(".errpilot") / "latest"


def ensure_run_dir(run_id: str, cwd: Path | None = None) -> Path:
    """Create and return the storage directory for a run."""
    root = cwd or Path.cwd()
    run_dir = root / RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def update_latest_pointer(run_id: str, cwd: Path | None = None) -> None:
    """Point ErrPilot's latest run marker at the given run id."""
    root = cwd or Path.cwd()
    errpilot_dir = root / ".errpilot"
    errpilot_dir.mkdir(parents=True, exist_ok=True)
    (root / LATEST_POINTER).write_text(f"{run_id}\n", encoding="utf-8")

    latest_link = root / RUNS_DIR / "latest"
    if latest_link.exists() or latest_link.is_symlink():
        if latest_link.is_dir() and not latest_link.is_symlink():
            return
        latest_link.unlink()

    try:
        os.symlink(run_id, latest_link)
    except OSError:
        pass

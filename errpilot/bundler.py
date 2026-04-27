"""Build portable error bundles from captured ErrPilot runs."""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict
from pathlib import Path
from typing import Any

from errpilot.parsers.python_traceback import parse_python_traceback
from errpilot.storage import LATEST_POINTER, RUNS_DIR


SCHEMA_VERSION = "0.1"
DEFAULT_TAIL_LINES = 80


def tail_text(text: str, max_lines: int = DEFAULT_TAIL_LINES) -> str:
    """Return the last max_lines of text, preserving a trailing newline when present."""
    if max_lines <= 0:
        return ""

    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text

    excerpt = "\n".join(lines[-max_lines:])
    if text.endswith(("\n", "\r")):
        excerpt += "\n"
    return excerpt


def build_error_bundle(run_id: str = "latest") -> tuple[Path, Path]:
    """Build markdown and JSON error bundle artifacts for a captured run."""
    root = Path.cwd()
    selected_run_id = _resolve_run_id(run_id, root)
    run_dir = root / RUNS_DIR / selected_run_id
    if not run_dir.is_dir():
        raise FileNotFoundError(f"run directory not found: {run_dir}")

    metadata = _read_json(run_dir / "metadata.json")
    command = _read_text(run_dir / "command.txt").strip()
    stdout = _read_text(run_dir / "stdout.log")
    stderr = _read_text(run_dir / "stderr.log")
    combined = _read_text(run_dir / "combined.log")
    python_traceback = _load_or_parse_python_traceback(run_dir, stderr)

    bundle = {
        "schema_version": SCHEMA_VERSION,
        "run_id": selected_run_id,
        "command": command,
        "cwd": metadata.get("cwd"),
        "exit_code": metadata.get("exit_code"),
        "metadata": metadata,
        "logs": {
            "stdout_path": str(run_dir / "stdout.log"),
            "stderr_path": str(run_dir / "stderr.log"),
            "combined_path": str(run_dir / "combined.log"),
            "stdout_excerpt": tail_text(stdout),
            "stderr_excerpt": tail_text(stderr),
            "combined_excerpt": tail_text(combined),
        },
        "python_traceback": python_traceback,
        "git": _git_state(root),
    }

    json_path = run_dir / "error_bundle.json"
    md_path = run_dir / "error_bundle.md"
    json_path.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(_render_markdown(bundle), encoding="utf-8")

    return md_path, json_path


def _resolve_run_id(run_id: str, root: Path) -> str:
    if run_id != "latest":
        return run_id

    latest_path = root / LATEST_POINTER
    if not latest_path.exists():
        raise FileNotFoundError(".errpilot/latest not found")

    latest_run_id = latest_path.read_text(encoding="utf-8").strip()
    if not latest_run_id:
        raise ValueError(".errpilot/latest is empty")
    return latest_run_id


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_or_parse_python_traceback(run_dir: Path, stderr: str) -> dict[str, Any] | None:
    traceback_path = run_dir / "python_traceback.json"
    if traceback_path.exists():
        return _read_json(traceback_path)

    traceback = parse_python_traceback(stderr)
    if traceback is None:
        return None

    traceback_data = asdict(traceback)
    traceback_path.write_text(
        json.dumps(traceback_data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return traceback_data


def _git_state(root: Path) -> dict[str, str | bool | None]:
    branch = _git_output(root, "rev-parse", "--abbrev-ref", "HEAD")
    commit = _git_output(root, "rev-parse", "HEAD")
    status = _git_output(root, "status", "--porcelain")

    return {
        "branch": branch,
        "commit": commit,
        "dirty": bool(status) if status is not None else False,
    }


def _git_output(root: Path, *args: str) -> str | None:
    try:
        completed = subprocess.run(
            ("git", *args),
            cwd=root,
            capture_output=True,
            check=False,
            text=True,
        )
    except FileNotFoundError:
        return None

    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def _render_markdown(bundle: dict[str, Any]) -> str:
    traceback = bundle["python_traceback"]
    git = bundle["git"]
    logs = bundle["logs"]
    lines = [
        "# ErrPilot Error Bundle",
        "",
        "## Run Summary",
        "",
        f"- Run ID: `{bundle['run_id']}`",
        f"- Command: `{bundle['command']}`",
        f"- CWD: `{bundle['cwd']}`",
        f"- Exit code: `{bundle['exit_code']}`",
        "",
        "## Git State",
        "",
        f"- Branch: `{git['branch']}`",
        f"- Commit: `{git['commit']}`",
        f"- Dirty: `{git['dirty']}`",
        "",
        "## Python Traceback",
        "",
    ]

    if traceback is None:
        lines.append("No Python traceback detected.")
    else:
        top_frame = _top_frame(traceback)
        lines.extend(
            [
                f"- Error class: `{traceback.get('error_class')}`",
                f"- Error message: `{traceback.get('error_message')}`",
                f"- Top frame: `{_format_frame(top_frame)}`",
                "",
                "| File | Line | Function |",
                "| --- | ---: | --- |",
            ]
        )
        for frame in traceback.get("stack_frames", []):
            lines.append(
                "| "
                f"{_escape_table_cell(str(frame.get('file')))} | "
                f"{frame.get('line')} | "
                f"{_escape_table_cell(str(frame.get('function')))} |"
            )

    lines.extend(
        [
            "",
            "## stderr excerpt",
            "",
            "```text",
            logs["stderr_excerpt"].rstrip(),
            "```",
            "",
            "## stdout excerpt",
            "",
            "```text",
            logs["stdout_excerpt"].rstrip(),
            "```",
            "",
            "## Next Step",
            "",
            "Inspect the traceback and captured logs before choosing a fix path.",
            "",
        ]
    )
    return "\n".join(lines)


def _top_frame(traceback: dict[str, Any]) -> dict[str, Any] | None:
    stack_frames = traceback.get("stack_frames", [])
    if not stack_frames:
        return None
    return stack_frames[-1]


def _format_frame(frame: dict[str, Any] | None) -> str:
    if frame is None:
        return "unknown"
    return f"{frame.get('file')}:{frame.get('line')} in {frame.get('function')}"


def _escape_table_cell(value: str) -> str:
    return value.replace("|", "\\|")

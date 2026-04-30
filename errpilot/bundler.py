"""Build portable error bundles from captured ErrPilot runs."""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict
from pathlib import Path
from typing import Any

from errpilot.parsers.pytest import parse_pytest_failures
from errpilot.parsers.python_traceback import parse_python_traceback
from errpilot.source_context import collect_source_contexts
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
    pytest_report = parse_pytest_failures(combined)
    failing_tests = (
        [failure.to_dict() for failure in pytest_report.failing_tests]
        if pytest_report is not None
        else []
    )
    signature = _failure_signature(python_traceback)
    log_window = _log_window(stderr)
    source_contexts = collect_source_contexts(
        python_traceback=python_traceback,
        failing_tests=failing_tests,
        repo_root=root,
    )

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
            "log_window": log_window,
        },
        "python_traceback": python_traceback,
        "failing_tests": failing_tests,
        "pytest": pytest_report.to_dict() if pytest_report is not None else None,
        "signature": signature,
        "source_contexts": source_contexts,
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
    diff = _git_output(root, "diff", "--quiet", "--")

    return {
        "branch": branch,
        "commit": commit,
        "dirty": bool(status) if status is not None else False,
        "status": status,
        "diff": None,
        "diff_omitted": True,
        "diff_available": diff is not None,
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

    if args[:2] == ("diff", "--quiet"):
        return "" if completed.returncode == 1 else None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def _failure_signature(traceback: dict[str, Any] | None) -> dict[str, Any] | None:
    if traceback is None:
        return None

    top_frame = _top_frame(traceback)
    error_class = traceback.get("error_class")
    error_message = traceback.get("error_message")
    frame_text = _format_frame(top_frame)
    summary_parts = [part for part in (error_class, error_message) if part is not None]
    summary = ": ".join(summary_parts)
    if frame_text != "unknown":
        summary = f"{summary} @ {frame_text}" if summary else frame_text

    return {
        "kind": "python_traceback",
        "error_class": error_class,
        "error_message": error_message,
        "top_frame": top_frame,
        "summary": summary,
    }


def _log_window(text: str, max_lines: int = DEFAULT_TAIL_LINES) -> dict[str, Any]:
    lines = text.splitlines()
    marker_index = next(
        (index for index, line in enumerate(lines) if "Traceback (most recent call last):" in line),
        None,
    )
    if marker_index is None:
        excerpt = tail_text(text, max_lines)
        total_lines = len(lines)
        start_line = max(total_lines - len(excerpt.splitlines()) + 1, 1) if total_lines else None
        return {
            "source": "stderr.log",
            "reason": "stderr_tail",
            "start_line": start_line,
            "end_line": total_lines or None,
            "excerpt": excerpt,
        }

    end_index = min(len(lines), marker_index + max_lines)
    excerpt = "\n".join(lines[marker_index:end_index])
    if text.endswith(("\n", "\r")) and end_index == len(lines):
        excerpt += "\n"
    return {
        "source": "stderr.log",
        "reason": "python_traceback",
        "start_line": marker_index + 1,
        "end_line": end_index,
        "excerpt": excerpt,
    }


def _render_markdown(bundle: dict[str, Any]) -> str:
    traceback = bundle["python_traceback"]
    git = bundle["git"]
    logs = bundle["logs"]
    signature = bundle["signature"]
    source_contexts = bundle["source_contexts"]
    failing_tests = bundle["failing_tests"]
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
        "### git status",
        "",
        "```text",
        git.get("status") or "",
        "```",
        "",
        "### git diff",
        "",
        "Diff content omitted from error bundles to keep failure searches focused.",
        "",
        "## Signature",
        "",
        signature.get("summary") if signature is not None else "No failure signature detected.",
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

    lines.extend(["", "## Pytest Failures", ""])
    if not failing_tests:
        lines.append("No pytest failures detected.")
    else:
        lines.extend(
            [
                "| # | Node ID | File | Test | Error |",
                "|---|--------|------|------|-------|",
            ]
        )
        for index, failure in enumerate(failing_tests, start=1):
            lines.append(
                "| "
                f"{index} | "
                f"{_escape_table_cell(str(failure.get('nodeid') or ''))} | "
                f"{_escape_table_cell(str(failure.get('file') or ''))} | "
                f"{_escape_table_cell(str(failure.get('test_name') or ''))} | "
                f"{_escape_table_cell(str(failure.get('error_class') or ''))} |"
            )

    lines.extend(["", "## Source Contexts", ""])
    if not source_contexts:
        lines.append("No source contexts available.")
    else:
        for context in source_contexts:
            lines.extend(
                [
                    f"### {context['file']}:{context['focus_line']} ({context['role']})",
                    "",
                    f"Lines {context['line_start']}-{context['line_end']}",
                    "",
                    "```text",
                    str(context["content"]),
                    "```",
                    "",
                ]
            )

    lines.extend(
        [
            "",
            "## Log Window",
            "",
            "```text",
            logs["log_window"]["excerpt"].rstrip(),
            "```",
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
            "Inspect the traceback and captured logs before choosing a triage or handoff path.",
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

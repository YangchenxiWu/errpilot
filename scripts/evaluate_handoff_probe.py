"""Compare raw failure prompts with ErrPilot handoff prompts.

This is a deterministic handoff-quality probe, not a repair benchmark. It checks
whether an input artifact explicitly carries the evidence and guardrails a
downstream debugging workflow would need.
"""

from __future__ import annotations

import csv
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "evaluation" / "handoff_probe"
PROMPTS_DIR = OUTPUT_DIR / "prompts"
RESULTS_PATH = OUTPUT_DIR / "results.csv"


@dataclass(frozen=True)
class ProbeCase:
    case_id: str
    command: list[str]
    expected_error: str
    expected_file: str


CASES = [
    ProbeCase(
        case_id="python_assertion_failure",
        command=["pytest", "examples/python_assertion_failure"],
        expected_error="AssertionError",
        expected_file="examples/python_assertion_failure/test_example.py",
    ),
    ProbeCase(
        case_id="pytest_fixture_failure",
        command=["pytest", "examples/pytest_fixture_failure"],
        expected_error="fixture",
        expected_file="examples/pytest_fixture_failure/test_fixture.py",
    ),
    ProbeCase(
        case_id="python_import_failure",
        command=["pytest", "examples/python_import_failure"],
        expected_error="ModuleNotFoundError",
        expected_file="examples/python_import_failure/test_import_failure.py",
    ),
    ProbeCase(
        case_id="pytest_multi_failure",
        command=["pytest", "examples/pytest_multi_failure"],
        expected_error="AssertionError",
        expected_file="examples/pytest_multi_failure/test_multi_failure.py",
    ),
    ProbeCase(
        case_id="missing_config_failure",
        command=["pytest", "examples/missing_config_failure"],
        expected_error="FileNotFoundError",
        expected_file="examples/missing_config_failure/test_missing_config.py",
    ),
    ProbeCase(
        case_id="python_type_error_failure",
        command=["pytest", "examples/python_type_error_failure"],
        expected_error="TypeError",
        expected_file="examples/python_type_error_failure/test_type_error.py",
    ),
    ProbeCase(
        case_id="python_traceback_failure",
        command=["python3", "examples/python_traceback_failure/fail.py"],
        expected_error="ValueError",
        expected_file="examples/python_traceback_failure/fail.py",
    ),
]

RESULT_COLUMNS = [
    "case_id",
    "input_mode",
    "input_lines",
    "input_chars",
    "contains_expected_error",
    "contains_relevant_file",
    "explicit_verification_command",
    "contains_source_context",
    "contains_triage_route",
    "contains_human_approval_gate",
    "contains_safety_constraints",
    "handoff_completeness_score",
    "prompt_path",
]


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []

    for case in CASES:
        run_id = f"handoff-probe-{case.case_id}"
        run_dir = REPO_ROOT / ".errpilot" / "runs" / run_id
        if run_dir.exists():
            shutil.rmtree(run_dir)

        _run_errpilot_pipeline(run_id, case.command)

        raw_prompt_path = _write_raw_prompt(case, run_dir)
        handoff_prompt_path = run_dir / "codex_prompt.md"
        copied_handoff_path = PROMPTS_DIR / f"{case.case_id}.errpilot_handoff.md"
        copied_handoff_path.write_text(
            handoff_prompt_path.read_text(encoding="utf-8"),
            encoding="utf-8",
        )

        rows.append(_score_prompt(case, "raw_log", raw_prompt_path))
        rows.append(_score_prompt(case, "errpilot_handoff", copied_handoff_path))

    _write_results(rows)
    _print_summary(rows)
    return 0


def _run_errpilot_pipeline(run_id: str, command: list[str]) -> None:
    _run_cli(["run", "--run-id", run_id, "--", *command], check=False)
    _run_cli(["bundle", run_id], check=True)
    _run_cli(["triage", run_id, "--local"], check=True)
    _run_cli(["route", run_id, "--target", "codex"], check=True)


def _run_cli(args: list[str], check: bool) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [sys.executable, "-m", "errpilot.cli", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if check and completed.returncode != 0:
        raise RuntimeError(
            f"errpilot {' '.join(args)} failed with exit_code={completed.returncode}: "
            f"{completed.stderr or completed.stdout}"
        )
    return completed


def _write_raw_prompt(case: ProbeCase, run_dir: Path) -> Path:
    command = " ".join(case.command)
    combined = (run_dir / "combined.log").read_text(encoding="utf-8").rstrip()
    content = "\n".join(
        [
            "# Raw Failure Prompt",
            "",
            "The following command failed. Diagnose the root cause and propose a minimal fix.",
            "",
            "## Command",
            "",
            f"`{command}`",
            "",
            "## Raw Output",
            "",
            "```text",
            combined,
            "```",
            "",
        ]
    )
    path = PROMPTS_DIR / f"{case.case_id}.raw_log.md"
    path.write_text(content, encoding="utf-8")
    return path


def _score_prompt(case: ProbeCase, input_mode: str, path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    checks = {
        "contains_expected_error": case.expected_error in text,
        "contains_relevant_file": case.expected_file in text,
        "explicit_verification_command": "## Verification Command" in text,
        "contains_source_context": "## Source Contexts" in text or "source_contexts" in text,
        "contains_triage_route": "recommended_route" in text or "triage_recommended_route" in text,
        "contains_human_approval_gate": "requires_human_approval" in text
        or "human approval" in text.lower(),
        "contains_safety_constraints": "## Constraints" in text and "## Do Not Do" in text,
    }
    score = sum(1 for value in checks.values() if value)
    return {
        "case_id": case.case_id,
        "input_mode": input_mode,
        "input_lines": str(len(text.splitlines())),
        "input_chars": str(len(text)),
        **{key: _bool_string(value) for key, value in checks.items()},
        "handoff_completeness_score": f"{score}/{len(checks)}",
        "prompt_path": str(path.relative_to(REPO_ROOT)),
    }


def _write_results(rows: list[dict[str, str]]) -> None:
    with RESULTS_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _print_summary(rows: list[dict[str, str]]) -> None:
    print(f"cases={len(CASES)}")
    print(f"prompt_pairs={len(rows) // 2}")
    print(f"results={RESULTS_PATH}")
    for mode in ("raw_log", "errpilot_handoff"):
        mode_rows = [row for row in rows if row["input_mode"] == mode]
        scores = [_score_value(row["handoff_completeness_score"]) for row in mode_rows]
        average = sum(scores) / len(scores)
        print(f"{mode}_average_score={average:.2f}/7")


def _score_value(score: str) -> int:
    return int(score.split("/", 1)[0])


def _bool_string(value: bool) -> str:
    return "true" if value else "false"


if __name__ == "__main__":
    raise SystemExit(main())

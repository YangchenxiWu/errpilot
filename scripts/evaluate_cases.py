"""Generate evaluation results for ErrPilot case-study rows."""

from __future__ import annotations

import csv
import json
import shlex
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = REPO_ROOT / "evaluation" / "cases.csv"
RESULTS_PATH = REPO_ROOT / "evaluation" / "results.csv"

RESULT_COLUMNS = [
    "case_id",
    "source_project",
    "source_type",
    "command",
    "executed",
    "exit_code",
    "error_class",
    "failing_tests_count",
    "source_contexts_count",
    "severity",
    "expected_severity",
    "severity_match",
    "route",
    "expected_route",
    "route_compatible",
    "raw_log_lines",
    "bundle_md_lines",
    "handoff_artifacts_count",
    "notes",
]

ACTUAL_ROUTES = {
    "local_suggestion",
    "codex_or_aider_prompt",
    "stronger_coding_agent_prompt",
    "manual_plus_agent_investigation",
    "manual_review",
}


def main() -> None:
    cases = _read_cases()
    rows = [_evaluate_case(case) for case in cases]
    _write_results(rows)

    executed_count = sum(row["executed"] == "true" for row in rows)
    print(f"cases={len(rows)}")
    print(f"executed={executed_count}")
    print(f"documented_only={len(rows) - executed_count}")
    print(f"results={RESULTS_PATH}")


def _read_cases() -> list[dict[str, str]]:
    with CASES_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_results(rows: list[dict[str, str]]) -> None:
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _evaluate_case(case: dict[str, str]) -> dict[str, str]:
    if not _is_auto_runnable(case):
        return _documented_only_row(case)

    row = _base_row(case)
    row["executed"] = "true"
    try:
        run_id = _run_errpilot_pipeline(case["command"])
        bundle_path = REPO_ROOT / ".errpilot" / "runs" / run_id / "error_bundle.json"
        bundle_md_path = REPO_ROOT / ".errpilot" / "runs" / run_id / "error_bundle.md"
        combined_log_path = REPO_ROOT / ".errpilot" / "runs" / run_id / "combined.log"
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))

        severity = _triage_value(bundle, "severity")
        route = _triage_value(bundle, "recommended_route")

        row.update(
            {
                "exit_code": _stringify(_exit_code(bundle)),
                "error_class": _error_class(bundle),
                "failing_tests_count": str(len(_list_value(bundle.get("failing_tests")))),
                "source_contexts_count": str(len(_list_value(bundle.get("source_contexts")))),
                "severity": _stringify(severity),
                "severity_match": _severity_match(severity, case.get("expected_severity", "")),
                "route": _stringify(route),
                "route_compatible": route_compatible(route, case.get("expected_route", "")),
                "raw_log_lines": str(_line_count(combined_log_path)),
                "bundle_md_lines": str(_line_count(bundle_md_path)),
                "handoff_artifacts_count": str(
                    len(_list_value(bundle.get("handoff_artifacts")))
                ),
                "notes": _append_note(case.get("notes", ""), "auto_runnable_local_example"),
            }
        )
    except Exception as exc:
        row["notes"] = _append_note(case.get("notes", ""), f"pipeline_error={exc}")
    return row


def _base_row(case: dict[str, str]) -> dict[str, str]:
    return {
        "case_id": case.get("case_id", ""),
        "source_project": case.get("source_project", ""),
        "source_type": case.get("source_type", ""),
        "command": case.get("command", ""),
        "executed": "false",
        "exit_code": "",
        "error_class": "",
        "failing_tests_count": "",
        "source_contexts_count": "",
        "severity": "",
        "expected_severity": case.get("expected_severity", ""),
        "severity_match": "",
        "route": "",
        "expected_route": case.get("expected_route", ""),
        "route_compatible": "",
        "raw_log_lines": "",
        "bundle_md_lines": "",
        "handoff_artifacts_count": "",
        "notes": case.get("notes", ""),
    }


def _documented_only_row(case: dict[str, str]) -> dict[str, str]:
    row = _base_row(case)
    row["notes"] = _append_note(case.get("notes", ""), "documented_only_external_case")
    return row


def _is_auto_runnable(case: dict[str, str]) -> bool:
    if case.get("source_project", "").lower() != "errpilot":
        return False
    if case.get("source_type", "").lower() != "local_example":
        return False

    command = case.get("command", "")
    if not command.startswith("pytest examples/"):
        return False

    parts = shlex.split(command)
    if len(parts) < 2 or parts[0] != "pytest":
        return False

    example_path = REPO_ROOT / parts[1]
    try:
        example_path.relative_to(REPO_ROOT / "examples")
    except ValueError:
        return False
    return example_path.exists()


def _run_errpilot_pipeline(command: str) -> str:
    command_parts = shlex.split(command)
    _run_cli(["run", "--", *command_parts], check=False)
    _run_cli(["bundle", "latest"], check=True)
    _run_cli(["triage", "latest", "--local"], check=True)
    _run_cli(["route", "latest", "--target", "codex"], check=True)
    return (REPO_ROOT / ".errpilot" / "latest").read_text(encoding="utf-8").strip()


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


def normalize_expected_severity(value: object) -> int | None:
    text = _stringify(value).strip().upper()
    if not text or text == "UNKNOWN":
        return None
    if text.startswith("S") and text[1:].isdigit():
        return int(text[1:])
    if text.isdigit():
        return int(text)
    return None


def route_compatible(actual_route: object, expected_route: object) -> str:
    actual = _stringify(actual_route).strip()
    expected = _stringify(expected_route).strip()
    if not actual:
        return ""
    if actual == expected:
        return "true"
    if expected == "codex_prompt":
        return _bool_string(actual in {"codex_or_aider_prompt", "stronger_coding_agent_prompt"})
    if expected == "aider_prompt":
        return _bool_string(actual in {"codex_or_aider_prompt", "stronger_coding_agent_prompt"})
    if expected == "manual_or_aider_prompt":
        return _bool_string(
            actual
            in {
                "manual_plus_agent_investigation",
                "codex_or_aider_prompt",
                "stronger_coding_agent_prompt",
            }
        )
    if expected == "manual_review":
        return _bool_string(actual in {"manual_review", "manual_plus_agent_investigation"})
    if expected == "local_suggestion":
        return _bool_string(actual == "local_suggestion")
    if expected == "gemini_summary":
        return _bool_string(actual == "gemini_summary")
    return _bool_string(actual in ACTUAL_ROUTES and actual == expected)


def _severity_match(actual_severity: object, expected_severity: object) -> str:
    actual = _to_int(actual_severity)
    expected = normalize_expected_severity(expected_severity)
    if actual is None:
        return ""
    return _bool_string(expected is not None and actual == expected)


def _exit_code(bundle: dict[str, object]) -> object:
    run = _dict_value(bundle.get("run"))
    if "exit_code" in run:
        return run["exit_code"]
    return bundle.get("exit_code", "")


def _error_class(bundle: dict[str, object]) -> str:
    traceback = _dict_value(bundle.get("python_traceback"))
    error_class = _stringify(traceback.get("error_class"))
    if error_class:
        return error_class

    failing_tests = _list_value(bundle.get("failing_tests"))
    if not failing_tests:
        return ""
    first_failure = _dict_value(failing_tests[0])
    return _stringify(first_failure.get("error_class"))


def _triage_value(bundle: dict[str, object], key: str) -> object:
    triage = _dict_value(bundle.get("triage"))
    return triage.get(key, "")


def _line_count(path: Path) -> int:
    if not path.exists():
        return 0
    return len(path.read_text(encoding="utf-8").splitlines())


def _append_note(notes: str, extra: str) -> str:
    if notes:
        return f"{notes}; {extra}"
    return extra


def _dict_value(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _list_value(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def _stringify(value: object) -> str:
    if value is None:
        return ""
    return str(value)


def _to_int(value: object) -> int | None:
    if isinstance(value, int):
        return value
    text = _stringify(value).strip()
    if text.isdigit():
        return int(text)
    return None


def _bool_string(value: bool) -> str:
    return "true" if value else "false"


if __name__ == "__main__":
    main()

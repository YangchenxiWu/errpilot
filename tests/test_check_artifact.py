from pathlib import Path

from scripts.check_artifact import CHECK_STEPS, latest_codex_prompt_path


def test_check_artifact_defines_expected_steps() -> None:
    commands = [step.display_command for step in CHECK_STEPS]

    assert commands == [
        "python3 -m pytest",
        "python3 -m ruff check errpilot tests",
        "python3 scripts/evaluate_cases.py",
        "errpilot run -- pytest examples/python_assertion_failure",
        "errpilot bundle latest",
        "errpilot triage latest --local",
        "errpilot route latest --target codex",
    ]


def test_demo_run_capture_expects_failing_example_exit_code() -> None:
    demo_run = next(step for step in CHECK_STEPS if step.name == "demo run capture")

    assert demo_run.expected_returncode == 1


def test_latest_codex_prompt_path_uses_latest_run_id(tmp_path: Path) -> None:
    latest_path = tmp_path / ".errpilot" / "latest"
    latest_path.parent.mkdir()
    latest_path.write_text("run-123\n", encoding="utf-8")

    assert latest_codex_prompt_path(tmp_path) == (
        tmp_path / ".errpilot" / "runs" / "run-123" / "codex_prompt.md"
    )

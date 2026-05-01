import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from errpilot.cli import main
from errpilot.router.handoff import HandoffPrompt, build_handoff_prompt


def test_codex_prompt_contains_required_sections() -> None:
    prompt = build_handoff_prompt(_bundle(), "codex")

    assert isinstance(prompt, HandoffPrompt)
    assert prompt.target == "codex"
    assert prompt.filename == "codex_prompt.md"
    assert "# ErrPilot Handoff: codex" in prompt.content
    assert "## Failure Summary" in prompt.content
    assert "## Triage Result" in prompt.content
    assert "## Failing Tests" in prompt.content
    assert "## Source Contexts" in prompt.content
    assert "## Verification Command" in prompt.content
    assert "## Constraints" in prompt.content
    assert "## Do Not Do" in prompt.content


def test_codex_prompt_uses_structured_fields() -> None:
    prompt = build_handoff_prompt(_bundle(), "codex")

    assert "test_addition" in prompt.content
    assert "AssertionError" in prompt.content
    assert "def test_addition():" in prompt.content
    assert "codex_or_aider_prompt" in prompt.content
    assert "pytest examples/python_assertion_failure" in prompt.content


def test_manual_target_returns_manual_review_prompt() -> None:
    prompt = build_handoff_prompt(_bundle(), "manual")

    assert prompt.filename == "manual_review.md"
    assert "# ErrPilot Handoff: manual" in prompt.content
    assert "Human review checklist" in prompt.content
    assert "Do not run destructive commands." in prompt.content


def test_unsupported_target_raises_value_error() -> None:
    with pytest.raises(ValueError, match="unsupported handoff target"):
        build_handoff_prompt(_bundle(), "openhands")


def test_prompt_does_not_include_full_raw_combined_log() -> None:
    bundle = _bundle()
    logs = bundle["logs"]
    assert isinstance(logs, dict)
    logs["combined_excerpt"] = "FAILED tests/test_example.py::test_addition"
    logs["combined_log"] = "FULL RAW COMBINED LOG SHOULD NOT BE INCLUDED"

    prompt = build_handoff_prompt(bundle, "codex")

    assert "FAILED tests/test_example.py::test_addition" in prompt.content
    assert "FULL RAW COMBINED LOG SHOULD NOT BE INCLUDED" not in prompt.content


def test_cli_route_latest_codex_writes_codex_prompt() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        run_dir = _write_fake_error_bundle()

        result = runner.invoke(main, ["route", "latest", "--target", "codex"])

        assert result.exit_code == 0
        prompt_path = run_dir / "codex_prompt.md"
        assert prompt_path.exists()
        assert f"handoff_prompt={Path.cwd() / prompt_path}" in result.output


def test_cli_route_latest_manual_writes_manual_review() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        run_dir = _write_fake_error_bundle()

        result = runner.invoke(main, ["route", "latest", "--target", "manual"])

        assert result.exit_code == 0
        prompt_path = run_dir / "manual_review.md"
        assert prompt_path.exists()
        assert "Human review checklist" in prompt_path.read_text(encoding="utf-8")


def test_cli_route_fails_when_error_bundle_is_missing() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        run_dir = Path(".errpilot/runs/run-001")
        run_dir.mkdir(parents=True)
        Path(".errpilot/latest").write_text("run-001\n", encoding="utf-8")

        result = runner.invoke(main, ["route", "latest", "--target", "codex"])

        assert result.exit_code != 0
        assert "error_bundle.json not found for run_id=run-001" in result.output
        assert "errpilot bundle run-001" in result.output
        assert not (run_dir / "codex_prompt.md").exists()


def test_cli_route_prompt_contains_structured_fields_from_bundle() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        run_dir = _write_fake_error_bundle()

        result = runner.invoke(main, ["route", "latest", "--target", "codex"])

        assert result.exit_code == 0
        prompt = (run_dir / "codex_prompt.md").read_text(encoding="utf-8")
        assert "test_addition" in prompt
        assert "AssertionError" in prompt
        assert "def test_addition():" in prompt
        assert "codex_or_aider_prompt" in prompt


def test_cli_route_codex_updates_handoff_artifacts() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        run_dir = _write_fake_error_bundle()

        result = runner.invoke(main, ["route", "latest", "--target", "codex"])

        assert result.exit_code == 0
        bundle = _read_bundle(run_dir)
        assert bundle["handoff_artifacts"] == [
            {
                "target": "codex",
                "path": "codex_prompt.md",
                "kind": "prompt",
                "generated_by": "errpilot route",
                "executes_downstream_tool": False,
            }
        ]


def test_cli_route_codex_twice_does_not_duplicate_artifact() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        run_dir = _write_fake_error_bundle()

        first = runner.invoke(main, ["route", "latest", "--target", "codex"])
        second = runner.invoke(main, ["route", "latest", "--target", "codex"])

        assert first.exit_code == 0
        assert second.exit_code == 0
        artifacts = _read_bundle(run_dir)["handoff_artifacts"]
        assert [artifact["target"] for artifact in artifacts].count("codex") == 1


def test_cli_route_codex_and_manual_create_two_artifacts() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        run_dir = _write_fake_error_bundle()

        codex = runner.invoke(main, ["route", "latest", "--target", "codex"])
        manual = runner.invoke(main, ["route", "latest", "--target", "manual"])

        assert codex.exit_code == 0
        assert manual.exit_code == 0
        artifacts = _read_bundle(run_dir)["handoff_artifacts"]
        assert {artifact["target"] for artifact in artifacts} == {"codex", "manual"}


def test_cli_route_artifact_entry_does_not_execute_downstream_tool() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        run_dir = _write_fake_error_bundle()

        result = runner.invoke(main, ["route", "latest", "--target", "codex"])

        assert result.exit_code == 0
        artifact = _read_bundle(run_dir)["handoff_artifacts"][0]
        assert artifact["executes_downstream_tool"] is False


def _bundle() -> dict[str, object]:
    return {
        "command": "pytest examples/python_assertion_failure",
        "run": {"run_id": "run-001", "exit_code": 1},
        "exit_code": 1,
        "python_traceback": None,
        "logs": {
            "stderr_excerpt": "AssertionError: assert 3 == 4",
            "stdout_excerpt": "",
            "combined_excerpt": "FAILED examples/python_assertion_failure/test_example.py::test_addition",
        },
        "failing_tests": [
            {
                "nodeid": "examples/python_assertion_failure/test_example.py::test_addition",
                "file": "examples/python_assertion_failure/test_example.py",
                "test_name": "test_addition",
                "error_class": "AssertionError",
            }
        ],
        "source_contexts": [
            {
                "file": "examples/python_assertion_failure/test_example.py",
                "focus_line": 2,
                "role": "failing_test",
                "line_start": 1,
                "line_end": 2,
                "content": "def test_addition():\n    assert 3 == 4\n",
            }
        ],
        "triage": {
            "severity": 2,
            "confidence": 0.78,
            "recommended_route": "codex_or_aider_prompt",
            "requires_human_approval": True,
            "reason": "Single pytest AssertionError with localized failure context.",
        },
        "handoff_artifacts": [],
    }


def _write_fake_error_bundle() -> Path:
    run_dir = Path(".errpilot/runs/run-001")
    run_dir.mkdir(parents=True)
    Path(".errpilot/latest").write_text("run-001\n", encoding="utf-8")
    (run_dir / "error_bundle.json").write_text(
        json.dumps(_bundle(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return run_dir


def _read_bundle(run_dir: Path) -> dict[str, object]:
    return json.loads((run_dir / "error_bundle.json").read_text(encoding="utf-8"))

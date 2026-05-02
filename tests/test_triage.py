import json
from pathlib import Path

from click.testing import CliRunner

from errpilot.cli import main
from errpilot.triage.local import LocalTriageResult, classify_bundle


def test_single_pytest_assertion_is_severity_2() -> None:
    result = classify_bundle(
        {
            "command": "pytest tests/test_example.py",
            "exit_code": 1,
            "failing_tests": [
                {
                    "nodeid": "tests/test_example.py::test_addition",
                    "error_class": "AssertionError",
                    "summary": "AssertionError: assert 3 == 4",
                }
            ],
            "source_contexts": [
                {
                    "file": "tests/test_example.py",
                    "content": "def test_addition():\n    assert 3 == 4\n",
                }
            ],
        }
    )

    assert result.severity == 2
    assert result.recommended_route == "codex_or_aider_prompt"
    assert result.requires_human_approval is True
    assert result.to_dict()["confidence"] == result.confidence


def test_single_pytest_type_error_is_severity_2() -> None:
    result = classify_bundle(
        {
            "command": "pytest examples/python_type_error_failure",
            "exit_code": 1,
            "failing_tests": [
                {
                    "nodeid": (
                        "examples/python_type_error_failure/"
                        "test_type_error.py::test_increment_rejects_wrong_type"
                    ),
                    "error_class": "TypeError",
                    "summary": "TypeError: can only concatenate str (not \"int\") to str",
                }
            ],
            "source_contexts": [
                {
                    "file": "examples/python_type_error_failure/test_type_error.py",
                    "content": "def increment(value: int) -> int:\n    return value + 1\n",
                }
            ],
        }
    )

    assert result.severity == 2
    assert result.recommended_route == "codex_or_aider_prompt"


def test_multiple_failing_tests_are_severity_3() -> None:
    result = classify_bundle(
        {
            "command": "pytest",
            "exit_code": 1,
            "failing_tests": [
                {"nodeid": "tests/test_a.py::test_one", "error_class": "AssertionError"},
                {"nodeid": "tests/test_a.py::test_two", "error_class": "AssertionError"},
            ],
        }
    )

    assert result.severity == 3
    assert result.recommended_route == "stronger_coding_agent_prompt"


def test_module_not_found_is_severity_4() -> None:
    result = classify_bundle(
        {
            "command": "python app.py",
            "exit_code": 1,
            "python_traceback": {
                "error_class": "ModuleNotFoundError",
                "error_message": "No module named 'requests'",
            },
        }
    )

    assert result.severity == 4
    assert result.recommended_route == "manual_plus_agent_investigation"
    assert result.requires_human_approval is True


def test_pytest_missing_fixture_is_severity_4() -> None:
    result = classify_bundle(
        {
            "command": "pytest examples/pytest_fixture_failure",
            "exit_code": 1,
            "logs": {
                "stderr_excerpt": "fixture 'missing_fixture' not found",
                "combined_excerpt": "ERROR examples/pytest_fixture_failure/test_fixture.py",
            },
            "failing_tests": [
                {
                    "nodeid": (
                        "examples/pytest_fixture_failure/"
                        "test_fixture.py::test_needs_missing_fixture"
                    ),
                    "file": "examples/pytest_fixture_failure/test_fixture.py",
                    "test_name": "test_needs_missing_fixture",
                    "error_class": "FixtureError",
                    "summary": (
                        "ERROR examples/pytest_fixture_failure/"
                        "test_fixture.py::test_needs_missing_fixture"
                    ),
                }
            ],
        }
    )

    assert result.severity == 4
    assert result.recommended_route == "manual_plus_agent_investigation"
    assert result.requires_human_approval is True
    assert "fixture" in result.reason.lower() or "setup/configuration" in result.reason.lower()


def test_secret_signal_is_severity_5_manual_review() -> None:
    result = classify_bundle(
        {
            "command": "pytest",
            "exit_code": 1,
            "logs": {
                "stderr_excerpt": "AssertionError: expected password token to be redacted",
            },
            "failing_tests": [
                {"nodeid": "tests/test_auth.py::test_redaction", "error_class": "AssertionError"}
            ],
        }
    )

    assert result.severity == 5
    assert result.recommended_route == "manual_review"
    assert result.requires_human_approval is True


def test_unknown_nonzero_failure_is_severity_1_local_suggestion() -> None:
    result = classify_bundle(
        {
            "command": "custom-tool --check",
            "exit_code": 2,
            "logs": {"stderr_excerpt": "failed without structured parser output"},
        }
    )

    assert result.severity == 1
    assert result.recommended_route == "local_suggestion"
    assert result.requires_human_approval is False


def test_missing_fields_do_not_crash() -> None:
    result = classify_bundle({})

    assert isinstance(result, LocalTriageResult)
    assert result.severity == 1
    assert result.recommended_route == "local_suggestion"


def test_cli_local_triage_writes_local_triage_json() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        run_dir = _write_fake_error_bundle()

        result = runner.invoke(main, ["triage", "latest", "--local"])

        assert result.exit_code == 0
        triage_path = run_dir / "local_triage.json"
        assert triage_path.exists()
        triage = json.loads(triage_path.read_text(encoding="utf-8"))
        assert triage["severity"] == 2
        assert triage["recommended_route"] == "codex_or_aider_prompt"
        assert triage["requires_human_approval"] is True


def test_cli_local_triage_updates_error_bundle_triage_field() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        run_dir = _write_fake_error_bundle()

        result = runner.invoke(main, ["triage", "latest", "--local"])

        assert result.exit_code == 0
        triage = json.loads((run_dir / "local_triage.json").read_text(encoding="utf-8"))
        bundle = json.loads((run_dir / "error_bundle.json").read_text(encoding="utf-8"))
        assert bundle["triage"] == triage


def test_cli_local_triage_prints_severity() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        _write_fake_error_bundle()

        result = runner.invoke(main, ["triage", "run-001", "--local"])

        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["severity"] == 2


def test_cli_local_triage_fails_when_error_bundle_is_missing() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        run_dir = Path(".errpilot/runs/run-001")
        run_dir.mkdir(parents=True)
        Path(".errpilot/latest").write_text("run-001\n", encoding="utf-8")

        result = runner.invoke(main, ["triage", "latest", "--local"])

        assert result.exit_code != 0
        assert "error_bundle.json not found for run_id=run-001" in result.output
        assert "errpilot bundle run-001" in result.output
        assert not (run_dir / "local_triage.json").exists()


def test_cli_model_backed_triage_is_unimplemented() -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["triage", "latest", "--model", "small-local-model"])

    assert result.exit_code != 0
    assert "model-backed triage is not implemented yet" in result.output


def _write_fake_error_bundle() -> Path:
    run_dir = Path(".errpilot/runs/run-001")
    run_dir.mkdir(parents=True)
    Path(".errpilot/latest").write_text("run-001\n", encoding="utf-8")
    bundle = {
        "command": "pytest tests/test_example.py",
        "exit_code": 1,
        "logs": {
            "stderr_excerpt": "AssertionError: assert 3 == 4",
            "combined_excerpt": "FAILED tests/test_example.py::test_addition",
        },
        "failing_tests": [
            {
                "nodeid": "tests/test_example.py::test_addition",
                "error_class": "AssertionError",
                "summary": "AssertionError: assert 3 == 4",
            }
        ],
        "source_contexts": [
            {
                "file": "tests/test_example.py",
                "content": "def test_addition():\n    assert 3 == 4\n",
            }
        ],
    }
    (run_dir / "error_bundle.json").write_text(
        json.dumps(bundle, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return run_dir

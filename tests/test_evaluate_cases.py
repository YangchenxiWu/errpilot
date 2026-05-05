from scripts.evaluate_cases import (
    _is_auto_runnable,
    _without_section,
    normalize_expected_severity,
    route_compatible,
)


def test_normalize_expected_severity_s_notation() -> None:
    assert normalize_expected_severity("S4") == 4
    assert normalize_expected_severity("2") == 2
    assert normalize_expected_severity("") is None


def test_manual_or_aider_prompt_compatible_with_manual_plus_agent_investigation() -> None:
    assert route_compatible("manual_plus_agent_investigation", "manual_or_aider_prompt") == "true"


def test_errpilot_pytest_example_is_auto_runnable_when_path_exists() -> None:
    assert _is_auto_runnable(
        {
            "source_project": "ErrPilot",
            "source_type": "local_example",
            "command": "pytest examples/python_assertion_failure",
        }
    )


def test_errpilot_python_traceback_example_is_auto_runnable() -> None:
    assert _is_auto_runnable(
        {
            "source_project": "ErrPilot",
            "source_type": "local_example",
            "command": "python3 examples/python_traceback_failure/fail.py",
        }
    )


def test_other_python_examples_are_not_auto_runnable() -> None:
    assert not _is_auto_runnable(
        {
            "source_project": "ErrPilot",
            "source_type": "local_example",
            "command": "python3 examples/python_traceback_failure/other.py",
        }
    )


def test_external_cases_are_not_auto_runnable() -> None:
    assert not _is_auto_runnable(
        {
            "source_project": "skiloadlab",
            "source_type": "local_cli",
            "command": "pytest examples/python_assertion_failure",
        }
    )
    assert not _is_auto_runnable(
        {
            "source_project": "slsa_verifier",
            "source_type": "local_shell",
            "command": "pytest examples/python_assertion_failure",
        }
    )


def test_without_section_removes_only_named_markdown_section() -> None:
    lines = [
        "# Bundle",
        "",
        "## Run Summary",
        "run",
        "## Git State",
        "volatile",
        "## Signature",
        "stable",
    ]

    assert _without_section(lines, "## Git State") == [
        "# Bundle",
        "",
        "## Run Summary",
        "run",
        "## Signature",
        "stable",
    ]

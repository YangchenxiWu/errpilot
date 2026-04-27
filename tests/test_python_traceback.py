import json
from pathlib import Path

from click.testing import CliRunner

from errpilot.cli import main
from errpilot.parsers.python_traceback import parse_python_traceback


def test_parse_basic_value_error() -> None:
    text = """Traceback (most recent call last):
  File "demo.py", line 3, in <module>
    main()
  File "demo.py", line 2, in main
    raise ValueError("demo")
ValueError: demo
"""

    traceback = parse_python_traceback(text)

    assert traceback is not None
    assert traceback.error_class == "ValueError"
    assert traceback.error_message == "demo"
    assert len(traceback.stack_frames) == 2
    assert traceback.top_frame is not None
    assert traceback.top_frame.file == "demo.py"
    assert traceback.top_frame.line == 2
    assert traceback.top_frame.function == "main"


def test_parse_absolute_path_frame() -> None:
    text = """Traceback (most recent call last):
  File "/Users/x/project/src/foo.py", line 42, in compute
    compute()
RuntimeError: failed
"""

    traceback = parse_python_traceback(text)

    assert traceback is not None
    assert traceback.stack_frames[0].file == "/Users/x/project/src/foo.py"


def test_parse_module_not_found_error() -> None:
    text = """Traceback (most recent call last):
  File "demo.py", line 1, in <module>
    import errpilot
ModuleNotFoundError: No module named 'errpilot'
"""

    traceback = parse_python_traceback(text)

    assert traceback is not None
    assert traceback.error_class == "ModuleNotFoundError"
    assert traceback.error_message == "No module named 'errpilot'"


def test_parse_assertion_error_without_message() -> None:
    text = """Traceback (most recent call last):
  File "test_demo.py", line 10, in test_demo
    assert False
AssertionError
"""

    traceback = parse_python_traceback(text)

    assert traceback is not None
    assert traceback.error_class == "AssertionError"
    assert traceback.error_message == ""


def test_parse_non_traceback_returns_none() -> None:
    text = """hello world
everything is fine
"""

    assert parse_python_traceback(text) is None


def test_parse_string_file_and_module_function() -> None:
    text = """Traceback (most recent call last):
  File "<string>", line 1, in <module>
NameError: name 'x' is not defined
"""

    traceback = parse_python_traceback(text)

    assert traceback is not None
    assert traceback.top_frame is not None
    assert traceback.top_frame.file == "<string>"
    assert traceback.top_frame.function == "<module>"


def test_cli_parse_latest_outputs_json_and_writes_artifact() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        run_dir = Path(".errpilot/runs/run-001")
        run_dir.mkdir(parents=True)
        Path(".errpilot/latest").write_text("run-001\n", encoding="utf-8")
        (run_dir / "stderr.log").write_text(
            """Traceback (most recent call last):
  File "demo.py", line 3, in <module>
    main()
  File "demo.py", line 2, in main
    raise ValueError("demo")
ValueError: demo
""",
            encoding="utf-8",
        )

        result = runner.invoke(main, ["parse", "latest"])

        assert result.exit_code == 0
        assert "ValueError" in result.output
        output_path = run_dir / "python_traceback.json"
        assert output_path.exists()
        parsed = json.loads(output_path.read_text(encoding="utf-8"))
        assert parsed["error_class"] == "ValueError"
        assert parsed["stack_frames"][-1]["function"] == "main"

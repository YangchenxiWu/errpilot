import json
from pathlib import Path

from click.testing import CliRunner

from errpilot.bundler import build_error_bundle, tail_text
from errpilot.cli import main


TRACEBACK_TEXT = """Traceback (most recent call last):
  File "demo.py", line 5, in <module>
    f()
  File "demo.py", line 2, in f
    raise ValueError("bundle-demo")
ValueError: bundle-demo
"""


def test_tail_text_returns_last_lines() -> None:
    assert tail_text("one\ntwo\nthree\n", max_lines=2) == "two\nthree\n"
    assert tail_text("one\ntwo", max_lines=5) == "one\ntwo"
    assert tail_text("one\ntwo", max_lines=0) == ""


def test_build_error_bundle_writes_files_from_fake_run() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        run_dir = _write_fake_run()

        md_path, json_path = build_error_bundle("latest")

        assert md_path == Path.cwd() / run_dir / "error_bundle.md"
        assert json_path == Path.cwd() / run_dir / "error_bundle.json"
        assert md_path.exists()
        assert json_path.exists()
        assert (run_dir / "python_traceback.json").exists()


def test_build_error_bundle_json_contains_expected_fields() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        run_dir = _write_fake_run()

        _, json_path = build_error_bundle("run-001")

        bundle = json.loads(json_path.read_text(encoding="utf-8"))
        assert bundle["run_id"] == "run-001"
        assert bundle["command"] == "python demo.py"
        assert bundle["exit_code"] == 1
        assert "ValueError: bundle-demo" in bundle["logs"]["stderr_excerpt"]
        assert "ValueError: bundle-demo" in bundle["logs"]["log_window"]["excerpt"]
        assert bundle["python_traceback"]["error_class"] == "ValueError"
        assert bundle["failing_tests"][0]["error_class"] == "AssertionError"
        assert bundle["failing_tests"][0]["test_name"] == "test_addition"
        assert bundle["pytest"]["framework"] == "pytest"
        assert bundle["signature"]["summary"] == "ValueError: bundle-demo @ demo.py:2 in f"
        assert bundle["source_context"][0]["available"] is True
        assert bundle["source_context"][0]["line"] == 2
        assert bundle["source_context"][0]["start_line"] == 1
        assert bundle["git"]["status"] is None
        assert bundle["git"]["diff"] is None

        parsed = json.loads((run_dir / "python_traceback.json").read_text(encoding="utf-8"))
        assert parsed["error_message"] == "bundle-demo"


def test_build_error_bundle_omits_git_diff_content(monkeypatch) -> None:
    runner = CliRunner()
    noisy_diff = (
        "diff --git a/tests/test_example.py b/tests/test_example.py\n"
        "+failing_tests test_addition AssertionError\n"
    )

    def fake_git_output(root: Path, *args: str) -> str | None:
        if args == ("rev-parse", "--abbrev-ref", "HEAD"):
            return "main"
        if args == ("rev-parse", "HEAD"):
            return "abc123"
        if args == ("status", "--porcelain"):
            return " M tests/test_example.py"
        if args == ("diff", "--quiet", "--"):
            return ""
        if args == ("diff", "--"):
            return noisy_diff
        return None

    monkeypatch.setattr("errpilot.bundler._git_output", fake_git_output)

    with runner.isolated_filesystem():
        run_dir = _write_fake_run()

        md_path, json_path = build_error_bundle("latest")

        bundle_json = json_path.read_text(encoding="utf-8")
        markdown = md_path.read_text(encoding="utf-8")
        assert "diff --git" not in bundle_json
        assert "+failing_tests test_addition AssertionError" not in bundle_json
        assert noisy_diff not in bundle_json
        assert "diff --git" not in markdown
        assert "+failing_tests test_addition AssertionError" not in markdown
        assert noisy_diff not in markdown
        bundle = json.loads(bundle_json)
        assert bundle["git"]["dirty"] is True
        assert bundle["git"]["diff"] is None
        assert bundle["git"]["diff_omitted"] is True
        assert bundle["git"]["diff_available"] is True
        assert run_dir.exists()


def test_build_error_bundle_markdown_contains_required_headings() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        _write_fake_run()

        md_path, _ = build_error_bundle("latest")

        markdown = md_path.read_text(encoding="utf-8")
        assert "# ErrPilot Error Bundle" in markdown
        assert "## Run Summary" in markdown
        assert "## Git State" in markdown
        assert "## Signature" in markdown
        assert "## Python Traceback" in markdown
        assert "## Pytest Failures" in markdown
        assert "test_addition" in markdown
        assert "AssertionError" in markdown
        assert "## Source Context" in markdown
        assert "## Log Window" in markdown
        assert "## stderr excerpt" in markdown
        assert "## stdout excerpt" in markdown
        assert "## Next Step" in markdown


def test_cli_bundle_latest() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        run_dir = _write_fake_run()

        result = runner.invoke(main, ["bundle", "latest"])

        assert result.exit_code == 0
        assert "error_bundle_md=" in result.output
        assert "error_bundle_json=" in result.output
        assert (run_dir / "error_bundle.md").exists()
        assert (run_dir / "error_bundle.json").exists()


def _write_fake_run() -> Path:
    run_dir = Path(".errpilot/runs/run-001")
    run_dir.mkdir(parents=True)
    Path(".errpilot/latest").write_text("run-001\n", encoding="utf-8")
    metadata = {
        "schema_version": "0.1",
        "run_id": "run-001",
        "command": ["python", "demo.py"],
        "command_display": "python demo.py",
        "cwd": str(Path.cwd()),
        "execution_mode": "exec",
        "exit_code": 1,
        "started_at": "2026-04-27T00:00:00+00:00",
        "finished_at": "2026-04-27T00:00:01+00:00",
        "duration_ms": 1000,
    }
    (run_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (run_dir / "command.txt").write_text("python demo.py\n", encoding="utf-8")
    Path("demo.py").write_text(
        """def f():
    raise ValueError("bundle-demo")


f()
""",
        encoding="utf-8",
    )
    (run_dir / "stdout.log").write_text("before failure\n", encoding="utf-8")
    (run_dir / "stderr.log").write_text(TRACEBACK_TEXT, encoding="utf-8")
    (run_dir / "combined.log").write_text(
        "before failure\n"
        f"{TRACEBACK_TEXT}"
        "FAILED examples/python_assertion_failure/test_example.py::test_addition - "
        "AssertionError: assert 3 == 4\n",
        encoding="utf-8",
    )
    return run_dir

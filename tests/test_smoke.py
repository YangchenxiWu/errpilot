import json
import sys
from pathlib import Path

from click.testing import CliRunner

from errpilot.cli import main


def test_help_works() -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "ErrPilot" in result.output


def test_run_captures_command_artifacts() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(
            main,
            ["run", sys.executable, "-c", "print('hello from errpilot')"],
        )

        assert result.exit_code == 0
        assert "run_id=" in result.output
        assert "exit_code=0" in result.output

        latest_run_id = Path(".errpilot/latest").read_text(encoding="utf-8").strip()
        run_dir = Path(".errpilot/runs") / latest_run_id
        assert (run_dir / "stdout.log").read_text(encoding="utf-8") == "hello from errpilot\n"
        assert (run_dir / "stderr.log").read_text(encoding="utf-8") == ""
        assert "hello from errpilot" in (run_dir / "combined.log").read_text(encoding="utf-8")

        metadata = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))
        assert metadata["run_id"] == latest_run_id
        assert metadata["exit_code"] == 0
        assert metadata["execution_mode"] == "exec"
        assert metadata["command"][:2] == [sys.executable, "-c"]


def test_run_captures_failed_command_metadata() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(
            main,
            [
                "run",
                sys.executable,
                "-c",
                "import sys; print('bad', file=sys.stderr); raise SystemExit(7)",
            ],
        )

        assert result.exit_code == 7
        assert "exit_code=7" in result.output

        latest_run_id = Path(".errpilot/latest").read_text(encoding="utf-8").strip()
        run_dir = Path(".errpilot/runs") / latest_run_id
        assert (run_dir / "stderr.log").read_text(encoding="utf-8") == "bad\n"

        metadata = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))
        assert metadata["exit_code"] == 7
        assert metadata["execution_mode"] == "exec"


def test_run_captures_missing_command_as_127() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(main, ["run", "definitely-not-an-errpilot-command"])

        assert result.exit_code == 127
        assert "exit_code=127" in result.output

        latest_run_id = Path(".errpilot/latest").read_text(encoding="utf-8").strip()
        run_dir = Path(".errpilot/runs") / latest_run_id
        assert "definitely-not-an-errpilot-command" in (
            run_dir / "stderr.log"
        ).read_text(encoding="utf-8")

        metadata = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))
        assert metadata["execution_mode"] == "shell"


def test_route_latest_to_codex_works() -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["route", "latest", "--target", "codex"])

    assert result.exit_code == 0
    assert "run_id=latest" in result.output
    assert "target=codex" in result.output

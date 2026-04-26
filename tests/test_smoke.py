from click.testing import CliRunner

from errpilot.cli import main


def test_help_works() -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "ErrPilot" in result.output


def test_run_prints_received_command() -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["run", "pytest"])

    assert result.exit_code == 0
    assert "received command: pytest" in result.output


def test_route_latest_to_codex_works() -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["route", "latest", "--target", "codex"])

    assert result.exit_code == 0
    assert "run_id=latest" in result.output
    assert "target=codex" in result.output

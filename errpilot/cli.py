"""Placeholder command line interface for ErrPilot."""

from __future__ import annotations

import click


@click.group()
def main() -> None:
    """ErrPilot failure triage router."""


@main.command(
    context_settings={
        "allow_extra_args": True,
        "ignore_unknown_options": True,
    }
)
@click.argument("command", nargs=-1, required=True, type=click.UNPROCESSED)
def run(command: tuple[str, ...]) -> None:
    """Record a command that would be run by ErrPilot."""
    click.echo(f"placeholder: received command: {' '.join(command)}")


@main.command()
@click.argument("run_id", required=False)
def bundle(run_id: str | None) -> None:
    """Build a placeholder error bundle."""
    selected_run = run_id or "latest"
    click.echo(f"placeholder: would build bundle for run_id={selected_run}")


@main.command()
@click.argument("run_id", required=False)
@click.option("--local", "use_local", is_flag=True, help="Use local-only placeholder triage.")
@click.option("--model", "model_name", required=True, help="Model name to display.")
def triage(run_id: str | None, use_local: bool, model_name: str) -> None:
    """Run placeholder severity triage."""
    selected_run = run_id or "latest"
    mode = "local" if use_local else "remote"
    click.echo(
        f"placeholder: would triage run_id={selected_run} mode={mode} model={model_name}"
    )


@main.command()
@click.argument("run_id", required=False)
@click.option(
    "--target",
    required=True,
    type=click.Choice(["codex", "aider", "gemini", "openhands"]),
    help="Target backend to display.",
)
def route(run_id: str | None, target: str) -> None:
    """Route a placeholder failure to an AI coding backend."""
    selected_run = run_id or "latest"
    click.echo(f"placeholder: would route run_id={selected_run} target={target}")


if __name__ == "__main__":
    main()

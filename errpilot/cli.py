"""Command line interface for ErrPilot."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import click

from errpilot.bundler import build_error_bundle
from errpilot.parsers.python_traceback import parse_python_traceback
from errpilot.router.handoff import build_handoff_prompt
from errpilot.runner import capture_command
from errpilot.storage import LATEST_POINTER, RUNS_DIR
from errpilot.triage.local import classify_bundle


@click.group()
def main() -> None:
    """ErrPilot failure intake and triage CLI."""


@main.command(
    context_settings={
        "allow_extra_args": True,
        "ignore_unknown_options": True,
    }
)
@click.argument("command", nargs=-1, required=True, type=click.UNPROCESSED)
def run(command: tuple[str, ...]) -> None:
    """Run a command and capture its output."""
    captured = capture_command(command)
    click.echo(f"run_id={captured.run_id}")
    click.echo(f"run_dir={captured.run_dir}")
    click.echo(f"exit_code={captured.exit_code}")
    raise click.exceptions.Exit(captured.exit_code)


@main.command()
@click.argument("run_id", required=False)
def bundle(run_id: str | None) -> None:
    """Build markdown and JSON error bundle artifacts."""
    try:
        md_path, json_path = build_error_bundle(run_id or "latest")
    except (FileNotFoundError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"error_bundle_md={md_path}")
    click.echo(f"error_bundle_json={json_path}")


@main.command()
@click.argument("run_id", required=False)
def parse(run_id: str | None) -> None:
    """Parse captured failure output."""
    selected_run = _resolve_run_id(run_id or "latest")
    run_dir = Path.cwd() / RUNS_DIR / selected_run
    stderr_path = run_dir / "stderr.log"

    if not stderr_path.exists():
        raise click.ClickException(f"stderr.log not found for run_id={selected_run}")

    traceback = parse_python_traceback(stderr_path.read_text(encoding="utf-8"))
    if traceback is None:
        click.echo("No Python traceback detected.")
        return

    output = json.dumps(asdict(traceback), indent=2, sort_keys=True)
    click.echo(output)
    (run_dir / "python_traceback.json").write_text(f"{output}\n", encoding="utf-8")


@main.command()
@click.argument("run_id", required=False)
@click.option("--local", "use_local", is_flag=True, help="Use local-only deterministic triage.")
@click.option("--model", "model_name", help="Model-backed triage is not implemented yet.")
def triage(run_id: str | None, use_local: bool, model_name: str | None) -> None:
    """Run severity triage for an error bundle."""
    if model_name is not None:
        raise click.ClickException(
            "model-backed triage is not implemented yet; use --local for deterministic triage"
        )
    if not use_local:
        raise click.ClickException("only local triage is implemented; rerun with --local")

    selected_run = _resolve_run_id(run_id or "latest")
    run_dir = Path.cwd() / RUNS_DIR / selected_run
    bundle_path = run_dir / "error_bundle.json"
    if not bundle_path.exists():
        raise click.ClickException(
            f"error_bundle.json not found for run_id={selected_run}; "
            f"run `errpilot bundle {selected_run}` first"
        )

    bundle_data = json.loads(bundle_path.read_text(encoding="utf-8"))
    result = classify_bundle(bundle_data).to_dict()
    bundle_data["triage"] = result
    output = json.dumps(result, indent=2, sort_keys=True)
    (run_dir / "local_triage.json").write_text(f"{output}\n", encoding="utf-8")
    bundle_path.write_text(
        json.dumps(bundle_data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    click.echo(output)


@main.command()
@click.argument("run_id", required=False)
@click.option(
    "--target",
    required=True,
    type=click.Choice(["codex", "aider", "gemini", "manual"]),
    help="Prompt target to generate.",
)
def route(run_id: str | None, target: str) -> None:
    """Generate a handoff prompt artifact for a run."""
    selected_run = _resolve_run_id(run_id or "latest")
    run_dir = Path.cwd() / RUNS_DIR / selected_run
    bundle_path = run_dir / "error_bundle.json"
    if not bundle_path.exists():
        raise click.ClickException(
            f"error_bundle.json not found for run_id={selected_run}; "
            f"run `errpilot bundle {selected_run}` first"
        )

    bundle_data = json.loads(bundle_path.read_text(encoding="utf-8"))
    prompt = build_handoff_prompt(bundle_data, target)
    prompt_path = run_dir / prompt.filename
    prompt_path.write_text(prompt.content, encoding="utf-8")
    bundle_data["handoff_artifacts"] = _upsert_handoff_artifact(
        bundle_data.get("handoff_artifacts"),
        target=target,
        filename=prompt.filename,
    )
    bundle_path.write_text(
        json.dumps(bundle_data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    click.echo(f"handoff_prompt={prompt_path}")


def _resolve_run_id(run_id: str) -> str:
    if run_id != "latest":
        return run_id

    latest_path = Path.cwd() / LATEST_POINTER
    if not latest_path.exists():
        raise click.ClickException(".errpilot/latest not found")

    latest_run_id = latest_path.read_text(encoding="utf-8").strip()
    if not latest_run_id:
        raise click.ClickException(".errpilot/latest is empty")
    return latest_run_id


def _upsert_handoff_artifact(
    existing_artifacts: object, target: str, filename: str
) -> list[dict[str, object]]:
    artifact = {
        "target": target,
        "path": filename,
        "kind": "prompt",
        "generated_by": "errpilot route",
        "executes_downstream_tool": False,
    }
    artifacts = [
        item
        for item in existing_artifacts
        if isinstance(item, dict) and item.get("target") != target
    ] if isinstance(existing_artifacts, list) else []
    artifacts.append(artifact)
    return artifacts


if __name__ == "__main__":
    main()

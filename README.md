# ErrPilot

ErrPilot turns failed command executions into structured, auditable failure
bundles for humans and AI coding agents.

ErrPilot is a CLI-first failure intake and triage desk for AI-assisted
debugging. It is not a self-directed coding agent. It does not silently modify
source code, apply patches, or make repository changes on behalf of a downstream
tool. Codex, Aider, Gemini CLI, OpenHands, SWE-agent, and Copilot remain
downstream repair or investigation backends; ErrPilot standardizes the intake
and handoff layer before failures are passed to humans or AI agents.

## Problem

Modern development workflows increasingly hand failing commands to humans and AI
coding agents, but the intake is usually ad hoc. A failed test run, traceback,
or build log may be too large for one prompt, too small to explain the real
context, or missing the audit trail needed to understand what was captured.

ErrPilot is intended to sit between the failed command and any downstream repair
backend. It turns noisy failure output into a structured failure bundle, keeps
the raw evidence auditable, and reserves explicit handoff artifacts for later
workflow stages. Human approval remains part of the workflow before any action
that could affect source code or external systems.

## Current Scope

This repository currently contains the intake and bundle construction core:

- Python package metadata.
- Click CLI commands.
- Run capture through `errpilot run`.
- Python traceback and pytest failure parsing.
- Source context extraction with repository-bound safety checks.
- `error_bundle.md` and `error_bundle.json` generation.
- Smoke tests for the CLI and captured run artifacts.
- Initial architecture, schema, severity, and security documentation.

Planned work includes local triage, handoff prompt generation, and case-study
evaluation. Direct repair execution is intentionally outside the current
implementation.

## CLI Preview

```bash
errpilot run pytest
errpilot bundle latest
errpilot triage latest --local --model small-local-model
errpilot route latest --target codex
```

`errpilot run` executes the command and stores run artifacts under
`.errpilot/runs/<run_id>/`:

- `stdout.log`
- `stderr.log`
- `combined.log`
- `command.txt`
- `metadata.json`

The latest run id is also written to `.errpilot/latest`, with
`.errpilot/runs/latest` used as a best-effort symlink when supported.

The triage and route commands still print placeholder messages only.

## Development

```bash
python -m pytest
```

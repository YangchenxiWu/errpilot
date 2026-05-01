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
- Deterministic local triage through `errpilot triage latest --local`.
- Handoff prompt artifact generation through `errpilot route`.
- Smoke tests for the CLI and captured run artifacts.
- Initial architecture, schema, severity, and security documentation.

Planned work includes case-study evaluation. Direct repair execution is
intentionally outside the current implementation.

## CLI Preview

```bash
errpilot run pytest
errpilot bundle latest
errpilot triage latest --local
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

## Local Triage

`errpilot triage latest --local` reads the latest run's `error_bundle.json`,
classifies it with deterministic local rules, writes
`.errpilot/runs/<run_id>/local_triage.json`, and updates the bundle's top-level
`triage` field with the same result. This mode is local and rule-based; it is
not model-backed and does not call external services.

## Handoff Prompts

`errpilot route latest --target codex` reads the latest run's
`error_bundle.json` and writes a reviewable handoff prompt artifact into the run
directory. Supported targets are `codex`, `aider`, `gemini`, and `manual`.

Generated files:

- `codex_prompt.md`
- `aider_prompt.md`
- `gemini_prompt.md`
- `manual_review.md`

Route only generates prompt artifacts. It does not execute downstream tools and
does not apply patches.

## Development

```bash
python -m pytest
```

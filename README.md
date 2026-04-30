# ErrPilot

ErrPilot is a CLI-first failure intake and triage tool for AI-assisted debugging.

It is not a coding agent. ErrPilot must not silently modify source code, apply
patches, or make repository changes on behalf of a downstream tool. Its job is
to capture failed command executions, build structured and auditable failure
bundles, classify failure complexity, and prepare an explicit handoff to human
reviewers or downstream coding agents such as Codex, Aider, Gemini CLI,
OpenHands, SWE-agent, or Copilot.

## Problem

Modern development workflows increasingly hand failing commands to humans and AI
coding agents, but the intake is usually ad hoc. A failed test run, traceback,
or build log may be too large for one prompt, too small to explain the real
context, or missing the audit trail needed to understand what was captured.

ErrPilot is intended to sit between the failed command and any downstream
investigation tool or coding agent. It turns noisy failure output into a
structured failure bundle, estimates severity, and prepares an explicit handoff.
Human approval remains part of the workflow before any action that could affect
source code or external systems.

## Current Scope

This repository currently contains the Day 1-5 intake and bundle construction
work:

- Python package metadata.
- Click CLI commands.
- `errpilot run` command execution and artifact capture.
- Python traceback and pytest failure parsing.
- Error bundle construction with compact source and log context.
- Smoke tests for the CLI and captured run artifacts.
- Initial architecture, schema, severity, and security documentation.

Gemini integration, MCP, caching, patch application, GitHub Actions automation,
and direct agent execution are intentionally not implemented.

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

The remaining commands still print placeholder messages only.

## Development

```bash
python -m pytest
```

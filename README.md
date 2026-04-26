# ErrPilot

ErrPilot is a CLI-first failure triage router for AI-assisted debugging.

It is not an autonomous coding agent. ErrPilot must not silently modify source
code, apply patches, or make repository changes on behalf of a backend. Its job
is to capture failed command executions, extract compact debugging context,
classify failure complexity, and route the failure to a suitable AI coding
backend such as Gemini, Codex CLI, Aider, or OpenHands.

## Problem

Modern development workflows increasingly hand failing commands to AI tools, but
the handoff is usually ad hoc. A failed test run, traceback, or build log may be
too large for one prompt, too small to explain the real context, or routed to a
backend that is a poor fit for the problem.

ErrPilot is intended to sit between the failed command and the coding backend. It
will turn noisy failure output into a compact error bundle, estimate severity,
and recommend or prepare an explicit handoff. Human approval remains part of the
workflow before any action that could affect source code or external systems.

## Current Scope

This repository currently contains the Day 1 project skeleton plus the first
Day 2 runtime step:

- Python package metadata.
- Click CLI commands.
- `errpilot run` command execution and artifact capture.
- Smoke tests for the CLI and captured run artifacts.
- Initial architecture, schema, severity, and security documentation.

Traceback parsing, pytest failure parsing, bundle construction, Gemini
integration, MCP, caching, patch application, and real debugging logic are
intentionally not implemented yet.

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

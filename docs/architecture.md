# Architecture

ErrPilot is designed as a CLI-first failure triage router. It is not a coding
agent and does not silently modify source code.

## Pipeline

The intended pipeline is:

```text
command runner
  -> log capture
  -> error parser
  -> source context extractor
  -> error bundle builder
  -> severity triage
  -> agent router
  -> approval gate
```

## Components

The command runner will execute the user-requested command and preserve command
metadata, exit status, stdout, stderr, duration, and working directory.

The log capture step will normalize command output and keep enough context to
explain the failure without sending entire repositories or excessive logs.

The error parser will identify structured failure signals such as Python
tracebacks, test failures, build errors, and tool diagnostics.

The source context extractor will collect a small amount of relevant local
context, such as nearby source lines and project metadata, while respecting the
security model.

The error bundle builder will produce a portable JSON object that can be shown to
humans or passed to an approved backend.

Severity triage will classify failures by complexity and risk. The first
implementation should support a local heuristic mode before any external model
integration.

The agent router will select or recommend a backend such as Codex CLI, Aider,
Gemini, or OpenHands based on severity, context size, and user preference.

The approval gate is mandatory before source changes, patch application,
external service calls, or other sensitive actions.

## Day 1 Status

Only the placeholder CLI and documentation are present in the Day 1 skeleton.
The runtime pipeline above is a design target, not an implemented system.

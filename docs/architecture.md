# Architecture

ErrPilot is designed as a CLI-first failure intake and triage desk. It produces
structured failure bundles for humans and downstream repair backends. It is not
a coding agent and does not silently modify source code.

## Pipeline

The intended pipeline is:

```text
failed command
  -> run capture
  -> traceback / pytest parsing
  -> source context construction
  -> error bundle generation
  -> local triage
  -> handoff artifact generation
  -> human or downstream agent
```

## Components

Run capture executes the user-requested command and preserves command metadata,
exit status, stdout, stderr, duration, and working directory.

Traceback and pytest parsing identify structured failure signals from Python
tracebacks and pytest failure summaries.

Source context construction collects bounded local source windows while
respecting repository boundaries and the security model.

Error bundle generation produces `error_bundle.json` and `error_bundle.md` for
humans or downstream repair backends.

Local triage reads `error_bundle.json`, produces `local_triage.json`, and writes
the result back into the bundle's `triage` field.

Handoff artifact generation is the step after local triage. It reads structured
bundle fields such as the failure summary, failing tests, source contexts, and
triage result, then writes target-specific prompt files for downstream review.
Generated prompts are based on structured bundle fields and bounded excerpts,
not full raw logs.

Downstream tools remain replaceable. The handoff artifacts describe the failure
and suggested constraints, but ErrPilot does not execute those tools.

Any future source changes, patch application, external service calls, or other
sensitive actions must remain behind explicit approval.

## Current Status

The current implementation captures failed command executions, parses Python and
pytest failures, extracts source context, and builds markdown and JSON failure
bundles. It can also run deterministic local triage and generate reviewable
handoff prompt artifacts.

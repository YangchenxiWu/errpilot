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

Local triage is planned. The current JSON schema reserves a `triage` field, but
the field is not populated by a real triage implementation yet.

Handoff artifact generation is planned. The current JSON schema reserves
`handoff_artifacts`, but ErrPilot does not generate repair prompts or perform
repairs yet.

Any future source changes, patch application, external service calls, or other
sensitive actions must remain behind explicit approval.

## Current Status

The current implementation captures failed command executions, parses Python and
pytest failures, extracts source context, and builds markdown and JSON failure
bundles. Local triage and handoff artifact generation remain planned workflow
stages.

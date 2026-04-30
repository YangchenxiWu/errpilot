# Error Bundle Schema

An error bundle is a structured, auditable failure intake artifact for humans
and AI coding agents.

The bundle is produced from a captured failed command. It keeps raw evidence in
separate files, adds compact structured diagnosis fields, and reserves space for
future handoff data without making any downstream tool mandatory.

## Evidence Model

ErrPilot separates three kinds of data:

- Raw evidence: `stdout.log`, `stderr.log`, `combined.log`, `command.txt`, and
  `metadata.json` remain separate files in the run directory.
- Structured diagnosis: traceback fields, pytest `failing_tests`,
  `source_contexts`, and git state are compact machine-readable summaries.
- Future handoff data: `triage` and `handoff_artifacts` are reserved fields for
  later pipeline stages.

## Stable Fields

Recommended stable top-level fields:

- `schema_version`
- `run`
- `command`
- `logs`
- `git`
- `python_traceback`
- `pytest`
- `failing_tests`
- `source_contexts`
- `risk_flags`
- `triage`
- `handoff_artifacts`

Compatibility fields currently present:

- `run_id`
- `cwd`
- `exit_code`
- `metadata`
- `signature`

Consumers should prefer the structured `run` object and other stable top-level
fields where possible. Compatibility fields remain available for existing
consumers.

## JSON Sketch

```json
{
  "schema_version": "0.1",
  "run": {
    "run_id": "20260430T192250Z-0cb13ffb",
    "cwd": "/path/to/repo",
    "exit_code": 1,
    "started_at": "...",
    "finished_at": "...",
    "duration_ms": 120
  },
  "command": "pytest examples/python_assertion_failure",
  "logs": {
    "stdout_path": "stdout.log",
    "stderr_path": "stderr.log",
    "combined_path": "combined.log",
    "stdout_excerpt": "...",
    "stderr_excerpt": "...",
    "combined_excerpt": "..."
  },
  "git": {
    "branch": "main",
    "commit": "...",
    "dirty": true,
    "status": "M errpilot/bundler.py",
    "diff_available": true,
    "diff_omitted": true,
    "diff_path": null
  },
  "python_traceback": null,
  "pytest": {
    "framework": "pytest",
    "failing_tests": []
  },
  "failing_tests": [],
  "source_contexts": [],
  "risk_flags": [],
  "triage": null,
  "handoff_artifacts": [],
  "metadata": {},
  "signature": {}
}
```

## Field Notes

`run` contains the structured run identity and timing fields currently emitted by
the bundler: `run_id`, `cwd`, `exit_code`, `started_at`, `finished_at`, and
`duration_ms` when available.

`logs` points to raw log files and includes bounded excerpts for quick review.
The raw log files remain the source of truth for full command output.

`git` captures repository state without embedding full patch text. Dirty state
may be recorded through `dirty`, `status`, `diff_available`, `diff_omitted`, and
optional `diff_path`, but the JSON bundle must not inline the full git diff.

`source_contexts` contains bounded source windows. Each item includes `file`,
`line_start`, `line_end`, `focus_line`, `role`, and `content`.

`risk_flags`, `triage`, and `handoff_artifacts` are reserved fields. They are
currently emitted as `[]`, `null`, and `[]`.

## Design Principles

- Preserve raw evidence as separate files.
- Keep machine-readable fields compact and noise-controlled.
- Do not inline full git diffs in JSON.
- Include bounded source windows only through `source_contexts`.
- Do not include sensitive files such as `.env`, credentials, tokens, private
  keys, or certificates in source contexts.
- Keep downstream agents replaceable; the bundle is agent-agnostic.

## Consumer Guidance

- Use `schema_version` to check compatibility.
- Prefer `run` over legacy `run_id`, `cwd`, and `exit_code`.
- Use `failing_tests` for test-level failures.
- Use `source_contexts` for bounded code evidence.
- Treat `risk_flags`, `triage`, and `handoff_artifacts` as reserved fields until
  later pipeline stages populate them.

# ErrPilot

[![CI](https://github.com/YangchenxiWu/errpilot/actions/workflows/ci.yml/badge.svg)](https://github.com/YangchenxiWu/errpilot/actions/workflows/ci.yml)
[![DOI](https://zenodo.org/badge/1221643785.svg)](https://doi.org/10.5281/zenodo.20053340)

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

Direct repair execution is intentionally outside the current implementation.

## CLI Preview

```bash
errpilot run -- pytest examples/python_assertion_failure
errpilot bundle latest
errpilot triage latest --local
errpilot route latest --target codex
```

`errpilot run` executes the command and stores run artifacts under
`.errpilot/runs/<run_id>/`:

ErrPilot executes only the user-supplied command explicitly passed to
`errpilot run --`; it does not sandbox that command.

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

## Case-Study Evaluation

```bash
python3 scripts/evaluate_cases.py
```

The runner writes `evaluation/results.csv`. The default artifact reports 12
case entries: 7 executable open-source, repository-local failure cases and 5
documented-only external design probes used as context for additional failure
categories. The executable local cases are the primary reproducible evidence.
An optional cross-project vignette using the public SkiLoadLab Python CLI is
recorded under
[`evaluation/cross_project_vignette/`](evaluation/cross_project_vignette/).
See [docs/evaluation.md](docs/evaluation.md) for the case policy and output
fields.

The repository also includes a deterministic handoff-quality probe:

```bash
python3 scripts/evaluate_handoff_probe.py
```

It compares raw failure prompts with ErrPilot-generated handoff prompts on all
seven executable failures. The probe measures explicit handoff completeness, not
repair success: raw prompts average `2.0/7` checked fields, while ErrPilot
handoff artifacts average `7.0/7`.
For a clean-clone reviewer path, see
[docs/artifact_reproduction.md](docs/artifact_reproduction.md).
For an optional Docker path, see
[docs/container_reproduction.md](docs/container_reproduction.md).

## Artifact Check

```bash
python3 scripts/check_artifact.py
```

This runs tests, lint, the case-study evaluation, and the minimal ErrPilot demo
path through `codex_prompt.md` generation.

## Citation And Archived Artifact

The DOI badge points to the Zenodo all-versions record. The release used for the
ASE Tools and Datasets artifact snapshot is archived at
https://doi.org/10.5281/zenodo.20053341.

The ASE demonstration screencast is available at
https://youtu.be/-cGRD9A6AXo.

## Development

```bash
python -m pytest
```

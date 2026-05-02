# Local Development Workflow

ErrPilot is designed as a local development failure intake tool. The intended
workflow is explicit:

```bash
cd any-local-project
errpilot run -- pytest
errpilot bundle latest
errpilot triage latest --local
errpilot route latest --target codex
```

## Explicit CLI Wrapper

ErrPilot is currently an explicit CLI wrapper. Users wrap commands with
`errpilot run --`, and ErrPilot captures that command's stdout, stderr, exit
code, metadata, and git state.

Prefer argv-style invocation:

```bash
errpilot run -- <command> <arg1> <arg2>
```

ErrPilot does not silently monitor all terminal activity. It does not scan the
user's filesystem for failures. It does not apply patches.

This explicit wrapper mode is intentional:

- clear user consent
- reproducible failure record
- bounded project root
- safer source context extraction
- reduced risk of collecting secrets or unrelated projects
- easier artifact review

## Optional Shell Helpers

Users can add a small alias for repeated local use:

```bash
alias ep='errpilot run --'
ep pytest
ep python scripts/make_figures.py
ep bash scripts/verify-artifact.sh
```

## Optional Project Workflows

A project can call ErrPilot from a `Makefile` target:

```makefile
test:
	errpilot run -- pytest
```

Or the user can wrap an existing target:

```bash
errpilot run -- make test
```

## Project Roots

ErrPilot can be installed once and then used from any project root, including:

- SkiLoadLab
- slsa-verifier
- ErrPilot itself
- other Python or CLI projects

Running from the target project root keeps captured paths, git state, source
contexts, and generated artifacts tied to the intended repository.

## Relationship To Evaluation

The evaluation runner only auto-runs in-repository examples for reproducibility.
Real local usage is broader: run ErrPilot from the target project's own root
directory.

Documented external cases exist to motivate later case studies without making
the artifact depend on the author's machine paths. The evaluation runner does
not execute external repositories by default.

## Future Work

Possible future additions include:

- optional project config file
- optional shell integration
- optional watch mode
- optional external case execution with explicit project-root mapping

ErrPilot should not add silent global monitoring. Local development use should
remain explicit and reviewable.

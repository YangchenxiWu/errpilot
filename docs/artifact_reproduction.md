# Artifact Reproduction

This path is intended for reviewers starting from a clean clone. It verifies
that ErrPilot can be installed, tested, evaluated, and used for the minimal
failure-intake demo without relying on the author's local paths.

ErrPilot captures explicitly wrapped commands through `errpilot run -- ...`.
It does not silently monitor the system. It also does not execute downstream
repair tools; `errpilot route` only writes reviewable handoff prompt artifacts.

## Clean Clone Setup

```bash
cd /tmp
rm -rf errpilot-clean
git clone https://github.com/YangchenxiWu/errpilot errpilot-clean
cd errpilot-clean

python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

## Test And Lint

```bash
python3 -m pytest
python3 -m ruff check errpilot tests
```

Expected result:

- `pytest` passes.
- `ruff` reports no lint violations.

## One-Command Artifact Check

```bash
python3 scripts/check_artifact.py
```

Expected result:

- The script reports `artifact check: PASS`.
- It runs tests, lint, case-study evaluation, the minimal demo path, and verifies
  that `.errpilot/runs/<run_id>/codex_prompt.md` exists.

## Case-Study Evaluation

```bash
python3 scripts/evaluate_cases.py
cat evaluation/results.csv
```

Expected result:

- `scripts/evaluate_cases.py` reports `cases=12`.
- It reports `executed=7`.
- It reports `documented_only=5`.
- `evaluation/results.csv` contains 12 rows after the header.
- The 7 executable rows are local ErrPilot examples: pytest examples plus one
  standalone Python traceback example.
- The 5 SkiLoadLab / slsa-verifier rows are documented-only by default.

External SkiLoadLab and slsa-verifier cases motivate real-world CI, CLI, shell,
and supply-chain failure categories. They are documented-only and are not
executed by the default evaluation runner because they depend on external
repository paths, archived CI state, tools, runtime paths, or archived logs. The
default artifact path avoids network calls and external repository mutation, so
these rows should not be interpreted as reproduced real-world executions.

## Minimal Demo

```bash
errpilot run -- pytest examples/python_assertion_failure
errpilot bundle latest
errpilot triage latest --local
errpilot route latest --target codex
```

Expected result:

- `errpilot run -- pytest examples/python_assertion_failure` returns the failed
  command's exit code and prints a `run_id` plus `.errpilot/runs/<run_id>/`.
- `errpilot bundle latest` writes `error_bundle.md` and `error_bundle.json`.
- `errpilot triage latest --local` writes deterministic local triage into the
  bundle and prints a severity and route.
- `errpilot route latest --target codex` writes
  `.errpilot/runs/<run_id>/codex_prompt.md`.

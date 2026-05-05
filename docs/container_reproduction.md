# Container Reproduction

Docker is an optional artifact reproduction path. The primary reproduction path
remains a clean clone with a local virtual environment, as documented in
[`docs/artifact_reproduction.md`](artifact_reproduction.md).

External SkiLoadLab and slsa-verifier cases remain documented-only by default.
The container path runs the same in-repository executable checks and does not
execute external repositories.

## Build

```bash
docker build -t errpilot-artifact:local .
```

## Run Artifact Check

```bash
docker run --rm errpilot-artifact:local
```

Expected result:

- `scripts/check_artifact.py` reports `artifact check: PASS`.
- The check runs tests, lint, case-study evaluation, and the minimal ErrPilot
  CLI demo through `codex_prompt.md` generation.

## Summarize Evaluation

```bash
docker run --rm errpilot-artifact:local python scripts/summarize_evaluation.py
```

Expected result:

- `total cases: 12`
- `executable: 7`
- `documented-only: 5`
- `severity matches among executable: 7/7`
- `route compatible among executable: 7/7`

## Image Sanity Check

```bash
docker run --rm errpilot-artifact:local sh -lc 'errpilot --help && python -m pytest && python scripts/evaluate_cases.py'
```

Expected result:

- The `errpilot` CLI is installed and prints help.
- The test suite passes.
- Evaluation reports `cases=12`, `executed=7`, and `documented_only=5`.

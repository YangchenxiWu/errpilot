# Case-Study Evaluation

ErrPilot's case-study evaluation does not measure whether ErrPilot fixes bugs.
It measures whether ErrPilot can generate stable failure records, triage
records, handoff prompt artifacts, and evaluation rows for known failure cases.
The capability mapping for paper-ready evidence is maintained in
[`docs/evaluation_matrix.md`](evaluation_matrix.md).

The current `evaluation/cases.csv` includes both executable local ErrPilot
examples and documented external cases from SkiLoadLab / slsa-verifier.
`evaluation/results.csv` therefore contains two kinds of rows:

- auto-run local examples from this repository
- documented-only external cases from SkiLoadLab / slsa-verifier

External cases are documented-only and are not executed by default because they
depend on external repository paths, archived CI state, dependencies,
command-line tools, and runtime state. The default runner is metadata-safe: it
only executes local ErrPilot examples under `pytest examples/` plus the exact
standalone Python traceback example command listed in `cases.csv`.

Current baseline targets are `cases >= 12`, `executed >= 7`, and
`documented_only = 5`.

The executable local cases provide the primary reproducible evidence for parser
extraction, bounded source context collection, deterministic triage, and
handoff artifact generation. The documented-only external cases motivate
real-world CI, CLI, shell, and supply-chain failure categories without requiring
author-specific paths, archived CI state, external repository state, network
calls, mutation, or downstream repair tools. They should not be interpreted as
reproduced real-world executions.

## Running

```bash
python3 scripts/evaluate_cases.py
cat evaluation/results.csv
```

For a compact paper-notes summary, run:

```bash
python3 scripts/summarize_evaluation.py
```

Local examples should produce `executed=true` rows. External SkiLoadLab and
slsa-verifier cases should remain documented-only by default with
`executed=false` and `documented_only_external_case` in `notes`.

## Output Fields

- `executed`: whether the runner executed the case command.
- `exit_code`: captured exit code for executed cases.
- `error_class`: traceback error class, or the first failing test error class.
- `failing_tests_count`: number of parsed failing tests.
- `source_contexts_count`: number of bounded source contexts.
- `severity`: actual local triage severity.
- `expected_severity`: expected severity from `cases.csv`.
- `severity_match`: whether actual severity matches the normalized expectation.
- `route`: actual local triage recommended route.
- `expected_route`: expected route from `cases.csv`.
- `route_compatible`: whether actual and expected routes are compatible.
- `raw_log_lines`: number of lines in the captured combined log.
- `bundle_md_lines`: stable line count for `error_bundle.md`, excluding the
  volatile Git State section so local dirty worktrees do not change the
  evaluation row.
- `handoff_artifacts_count`: number of generated handoff artifact records.
- `notes`: case notes plus runner status details.

Bundle and prompt artifacts use bounded or compact excerpts for review. Very
small logs may fit entirely inside those excerpts; the goal is bounded evidence,
not a guarantee that no complete small log appears.

## Normalization

Expected severities are normalized before comparison. For example, `S2` and `2`
both compare as severity `2`.

Expected routes are also compared through compatibility rules. For example,
`codex_prompt` is compatible with `codex_or_aider_prompt`, and
`manual_or_aider_prompt` is compatible with `manual_plus_agent_investigation`.

A mismatch is useful. It can reveal a classifier gap, an expectation gap, or a
case whose failure mode needs more precise documentation. The pytest fixture
example is treated as a test setup/configuration failure and may route to
`manual_plus_agent_investigation` while remaining compatible with the
`manual_or_aider_prompt` expectation.

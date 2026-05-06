# Paper Claims Map

This map keeps ErrPilot's paper claims aligned with artifact evidence. ErrPilot
is a failure intake and handoff layer; these claims do not measure or assert bug
repair success.

| Intended claim | Artifact evidence | Command | Output file | Paper/demo placement |
| --- | --- | --- | --- | --- |
| ErrPilot constructs structured failure intake artifacts. | A wrapped failed command creates raw logs, command metadata, and structured bundle files. The JSON bundle separates run metadata, logs, parsed diagnostics, triage, and handoff artifact records. | `errpilot run -- pytest examples/python_assertion_failure` followed by `errpilot bundle latest` | `.errpilot/runs/<run_id>/combined.log`, `.errpilot/runs/<run_id>/metadata.json`, `.errpilot/runs/<run_id>/error_bundle.json`, `.errpilot/runs/<run_id>/error_bundle.md` | Paper system overview; artifact walkthrough; screencast bundle-generation segment. |
| ErrPilot extracts bounded source contexts. | The bundle includes `source_contexts` entries with file paths, focus lines, roles, and bounded line windows for the failing local code. | `errpilot bundle latest` after the wrapped pytest example | `.errpilot/runs/<run_id>/error_bundle.json`, `.errpilot/runs/<run_id>/error_bundle.md` | Paper design section on source-context construction; evaluation capability matrix; screencast source-context segment. |
| ErrPilot provides deterministic local triage. | Local triage records severity, confidence, recommended route, human-approval requirement, and reason using local rules rather than external model calls. | `errpilot triage latest --local` | `.errpilot/runs/<run_id>/local_triage.json`, top-level `triage` field in `.errpilot/runs/<run_id>/error_bundle.json` | Paper workflow section; severity/route discussion; screencast triage segment. |
| ErrPilot generates reviewable handoff prompts. | Route generation writes a prompt artifact that summarizes command evidence, triage, failing tests, source contexts, log excerpts, and constraints without executing downstream repair tools. | `errpilot route latest --target codex` | `.errpilot/runs/<run_id>/codex_prompt.md`, `handoff_artifacts` in `.errpilot/runs/<run_id>/error_bundle.json` | Paper handoff section; demo handoff segment; artifact reproduction notes. |
| ErrPilot is evaluated on executable local cases plus documented external candidates. | The evaluation runner reports 12 total case entries: 7 executable in-repository failure cases and 5 documented-only external SkiLoadLab / slsa-verifier candidates. The executable rows provide the primary artifact evidence; the external rows are context and should not be interpreted as reproduced real-world executions. The summary script reports severity and route agreement for executable rows. | `python3 scripts/evaluate_cases.py` and `python3 scripts/summarize_evaluation.py` | `evaluation/results.csv`; terminal summary from `scripts/summarize_evaluation.py`; `docs/evaluation_matrix.md` | Paper evaluation section; case-study table; reviewer artifact checklist; screencast evaluation segment. |

## Claim Boundaries

- ErrPilot captures commands only when explicitly invoked with
  `errpilot run -- ...`; it does not sandbox those user-supplied commands.
- ErrPilot preserves raw evidence while adding structured diagnostic fields.
- ErrPilot uses bounded source excerpts for handoff artifacts instead of
  treating full logs or whole files as the primary summary.
- ErrPilot's local triage is deterministic and auditable, not a final diagnosis.
- ErrPilot generates handoff artifacts for humans or downstream tools; it does
  not execute repair tools.
- The evaluation measures failure-record generation, structured extraction,
  deterministic triage, and handoff artifact generation. It does not measure
  bug-fixing success.

## Abstract Candidate

ErrPilot is a CLI-first tool for turning explicitly wrapped failing commands
into structured, auditable failure bundles for AI-assisted debugging workflows.
Rather than acting as a repair agent, ErrPilot standardizes the intake layer
before a human or downstream coding tool investigates a failure. It captures
command metadata, raw stdout/stderr logs, parsed Python traceback and pytest
failure signals, bounded source contexts, deterministic local triage, and
reviewable handoff prompts for tools such as Codex, Aider, Gemini CLI, or manual
review. The artifact is designed to be local-first and reproducible: it requires
no external service calls, does not silently monitor terminal activity, and does
not execute downstream repair tools. We evaluate ErrPilot with 7 executable
in-repository failure cases covering pytest assertions, fixture/setup failures,
imports, multi-test failures, missing configuration, type errors, and standalone
tracebacks, plus 5 documented-only external candidates used to motivate
additional CI, CLI, shell, and supply-chain failure categories.

## Data Availability Statement

ErrPilot, its documentation, executable examples, evaluation case metadata,
generated evaluation results, artifact reproduction scripts, CI workflow, and
optional Docker reproduction path are available in the public repository. The
default artifact evaluation uses only in-repository examples and does not
require external repositories, external APIs, secrets, or downstream repair
tools. External SkiLoadLab and slsa-verifier cases are included as
documented-only metadata for context and are not executed by default.

## Limitations

ErrPilot does not repair bugs, rank patches, or measure downstream agent
success. The evaluation is a small artifact case study, not a broad empirical
benchmark. The external SkiLoadLab and slsa-verifier cases are documented-only
and are not reproduced by the default evaluation. Local triage is deterministic
and intentionally simple. ErrPilot executes user-supplied commands explicitly
passed to `errpilot run --`; it does not sandbox those commands.

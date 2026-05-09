# Paper Claims Map

This map keeps ErrPilot's paper claims aligned with artifact evidence. ErrPilot
is a failure provenance and handoff layer; these claims do not measure or assert
bug repair success.

| Intended claim | Artifact evidence | Command | Output file | Paper/demo placement |
| --- | --- | --- | --- | --- |
| ErrPilot constructs structured failure provenance artifacts. | A wrapped failed command creates raw logs, command metadata, and structured bundle files. The JSON bundle separates run metadata, logs, parsed diagnostics, triage, and handoff artifact records. | `errpilot run -- pytest examples/python_assertion_failure` followed by `errpilot bundle latest` | `.errpilot/runs/<run_id>/combined.log`, `.errpilot/runs/<run_id>/metadata.json`, `.errpilot/runs/<run_id>/error_bundle.json`, `.errpilot/runs/<run_id>/error_bundle.md` | Paper system overview; artifact walkthrough; screencast bundle-generation segment. |
| ErrPilot extracts bounded source contexts. | The bundle includes `source_contexts` entries with file paths, focus lines, roles, and bounded line windows for the failing local code. | `errpilot bundle latest` after the wrapped pytest example | `.errpilot/runs/<run_id>/error_bundle.json`, `.errpilot/runs/<run_id>/error_bundle.md` | Paper design section on source-context construction; evaluation capability matrix; screencast source-context segment. |
| ErrPilot provides deterministic local triage. | Local triage records severity, confidence, recommended route, human-approval requirement, and reason using local rules rather than external model calls. | `errpilot triage latest --local` | `.errpilot/runs/<run_id>/local_triage.json`, top-level `triage` field in `.errpilot/runs/<run_id>/error_bundle.json` | Paper workflow section; severity/route discussion; screencast triage segment. |
| ErrPilot generates reviewable handoff prompts. | Route generation writes a prompt artifact that summarizes command evidence, triage, failing tests, source contexts, log excerpts, and constraints without executing downstream repair tools. | `errpilot route latest --target codex` | `.errpilot/runs/<run_id>/codex_prompt.md`, `handoff_artifacts` in `.errpilot/runs/<run_id>/error_bundle.json` | Paper handoff section; demo handoff segment; artifact reproduction notes. |
| ErrPilot handoff artifacts are more complete than raw failure prompts under a deterministic checklist. | The handoff-quality probe compares raw failure prompts with generated Codex handoff artifacts on all 7 executable cases. Raw prompts average 2.0/7 checked fields; ErrPilot handoff artifacts average 7.0/7. This is not a repair-success benchmark. | `python3 scripts/evaluate_handoff_probe.py` | `evaluation/handoff_probe/results.csv`; `evaluation/handoff_probe/prompts/` | Paper evaluation section; handoff-quality probe table; reviewer artifact checklist. |
| ErrPilot is evaluated on executable local cases plus documented design probes. | The evaluation runner reports 12 default case entries: 7 executable open-source, repository-local failure cases and 5 documented-only external SkiLoadLab / slsa-verifier design probes. The executable rows provide the primary artifact evidence; the external rows are context and should not be interpreted as benchmark executions. An optional SkiLoadLab cross-project vignette records one reproduced public Python CLI failure. | `python3 scripts/evaluate_cases.py` and `python3 scripts/summarize_evaluation.py`; optional SkiLoadLab vignette run | `evaluation/results.csv`; terminal summary from `scripts/summarize_evaluation.py`; `docs/evaluation_matrix.md`; `evaluation/cross_project_vignette/skiloadlab_missing_input/` | Paper evaluation section; artifact-readiness table; reviewer artifact checklist; screencast evaluation segment. |

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
into auditable failure provenance for AI-assisted debugging workflows. Rather
than acting as a repair agent, ErrPilot standardizes the intake layer before a
human or downstream coding tool investigates a failure: what command failed,
what raw evidence was captured, what source context was selected, what local
routing decision was made, and what verification contract accompanies a handoff.
The artifact is local-first and reproducible, requiring no external service
calls and executing no downstream repair tools. We evaluate ErrPilot with 7
open-source, repository-local executable failure cases. A deterministic
handoff-quality probe on all 7 executable cases shows raw failure prompts
average 2/7 checked handoff fields, while ErrPilot artifacts average 7/7. We also report one
optional SkiLoadLab cross-project vignette.

## Data Availability Statement

ErrPilot, its documentation, executable examples, evaluation case metadata,
generated evaluation results, artifact reproduction scripts, CI workflow, and
optional Docker reproduction path are available in the public repository at
https://github.com/YangchenxiWu/errpilot and archived on Zenodo at
https://doi.org/10.5281/zenodo.20053341. The default artifact evaluation uses
only in-repository examples and does not require external repositories, external
APIs, secrets, or downstream repair tools. The SkiLoadLab vignette is provided
as an optional cross-project check, while other external cases are included as
documented-only metadata for context and are not executed by default.

## Limitations

ErrPilot does not repair bugs, rank patches, or measure downstream agent
success. The evaluation is an artifact-readiness study, not a broad empirical
benchmark or downstream-agent comparison. The SkiLoadLab vignette is a single
optional cross-project check; slsa-verifier entries are documented-only design
probes and are not reproduced by the default evaluation. Local triage is
deterministic and intentionally simple. ErrPilot executes user-supplied commands
explicitly passed to
`errpilot run --`; it does not sandbox those commands.

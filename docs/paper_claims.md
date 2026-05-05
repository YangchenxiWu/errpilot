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
| ErrPilot is evaluated on executable local cases plus documented external candidates. | The evaluation runner reports 12 total cases: 7 executable in-repository examples and 5 documented-only external SkiLoadLab / slsa-verifier candidates. The summary script reports severity and route agreement for executable rows. | `python3 scripts/evaluate_cases.py` and `python3 scripts/summarize_evaluation.py` | `evaluation/results.csv`; terminal summary from `scripts/summarize_evaluation.py`; `docs/evaluation_matrix.md` | Paper evaluation section; case-study table; reviewer artifact checklist; screencast evaluation segment. |

## Claim Boundaries

- ErrPilot captures commands only when explicitly invoked with
  `errpilot run -- ...`.
- ErrPilot preserves raw evidence while adding structured diagnostic fields.
- ErrPilot uses bounded source excerpts for handoff artifacts instead of
  treating full logs or whole files as the primary summary.
- ErrPilot's local triage is deterministic and auditable, not a final diagnosis.
- ErrPilot generates handoff artifacts for humans or downstream tools; it does
  not execute repair tools.
- The evaluation measures failure-record generation, structured extraction,
  deterministic triage, and handoff artifact generation. It does not measure
  bug-fixing success.

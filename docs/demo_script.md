# ErrPilot 5-Minute Screencast Script

## Demo Goal

Show how ErrPilot turns an explicitly wrapped local failure into a structured,
auditable failure bundle with source context, deterministic local triage, and a
handoff prompt for a downstream human or AI coding tool.

The demo positions ErrPilot as the intake layer before repair. It captures,
structures, explains, and routes failure evidence; it does not execute
downstream repair tools.

## Demo Environment Assumptions

- Start from a clean clone of the ErrPilot repository.
- Install locally with `pip install -e ".[dev]"`.
- Use only in-repository examples.
- No external repository is required.
- No external API is required.

## 5-Minute Timeline

| Time | Segment | Commands | What to show |
| --- | --- | --- | --- |
| 0:00-0:30 | Problem: raw failure output is noisy and ad hoc | None | Briefly show the repository and explain that raw test output alone is hard to audit, summarize, and hand off consistently. |
| 0:30-1:10 | Run capture | `errpilot run -- pytest examples/python_assertion_failure` | Show the printed `run_id`, `run_dir`, and failed command exit code. Open `.errpilot/runs/<run_id>/` to show captured `stdout.log`, `stderr.log`, `combined.log`, `command.txt`, and `metadata.json`. |
| 1:10-1:50 | Bundle generation | `errpilot bundle latest` | Show that `error_bundle.md` and `error_bundle.json` exist. Open both files briefly: Markdown for review, JSON for machine-readable structure. |
| 1:50-2:30 | Source contexts and failing tests | Viewer command or editor search in `error_bundle.json` | Show `failing_tests` with the pytest node and error class. Show `source_contexts` with bounded code windows rather than full-file dumps. |
| 2:30-3:10 | Local triage | `errpilot triage latest --local` | Show the terminal output, then open `local_triage.json` and the bundle's top-level `triage` field. Point out severity, route, confidence, reason, and human approval. |
| 3:10-3:50 | Handoff prompt | `errpilot route latest --target codex` | Show `codex_prompt.md`. Highlight structured sections such as task, command, triage, failing tests, source contexts, and constraints. |
| 3:50-4:30 | Evaluation | `python3 scripts/evaluate_cases.py` | Show the summary output as 12 total case entries: 7 executable in-repository failure cases and 5 documented-only external candidates. Open `evaluation/results.csv` and point to local executable examples versus documented external cases. |
| 4:30-5:00 | Conclusion | None | Summarize ErrPilot as a reproducible failure-intake layer before repair. Downstream tools remain replaceable; ErrPilot provides auditable evidence and handoff artifacts. |

## Commands To Copy-Paste

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

```bash
errpilot run -- pytest examples/python_assertion_failure
errpilot bundle latest
errpilot triage latest --local
errpilot route latest --target codex
```

Inspect the single-case demo artifacts before running the evaluation step.
`.errpilot/latest` always points to the most recent ErrPilot run, and
`python3 scripts/evaluate_cases.py` creates additional runs for the executable
evaluation cases. After running the evaluation script, `.errpilot/latest` points
to the last evaluation case. Keep the earlier `run_id` if you need to revisit
the single-case demo artifacts later.

```bash
python3 scripts/evaluate_cases.py
cat evaluation/results.csv
```

Optional inspection commands:

```bash
cat .errpilot/latest
ls -la .errpilot/runs/$(cat .errpilot/latest)
sed -n '1,160p' .errpilot/runs/$(cat .errpilot/latest)/error_bundle.md
sed -n '1,220p' .errpilot/runs/$(cat .errpilot/latest)/codex_prompt.md
```

## What To Show On Screen

1. Terminal command:
   `errpilot run -- pytest examples/python_assertion_failure`

   Show that ErrPilot only captures the command explicitly wrapped after
   `errpilot run --`.

2. Run artifact directory:
   `.errpilot/runs/<run_id>/`

   Show raw logs, command metadata, and the latest run pointer.

3. Bundle artifacts:
   `error_bundle.md` and `error_bundle.json`

   Show that the Markdown file is readable by humans and the JSON file has
   structured fields for tools.

4. Failure extraction:
   `failing_tests` and `source_contexts`

   Show the pytest node, error class, and bounded source window around the
   relevant local code.

5. Local triage:
   `local_triage.json` and `error_bundle.json`

   Show severity, recommended route, confidence, reason, and
   `requires_human_approval`.

6. Handoff prompt:
   `codex_prompt.md`

   Show that the prompt is generated as an artifact. It is not executed by
   ErrPilot.

7. Evaluation output:
   `evaluation/results.csv`

   Show reproducible local examples and documented-only external cases in one
   auditable table.

## Expected Output Highlights

- `error_bundle.md` exists after `errpilot bundle latest`.
- `error_bundle.json` contains structured failure evidence.
- `source_contexts` include bounded code windows.
- `failing_tests` includes the pytest test node and error class.
- `errpilot triage latest --local` prints triage severity and route.
- `local_triage.json` records the same deterministic triage result.
- `codex_prompt.md` contains structured handoff sections.
- `python3 scripts/evaluate_cases.py` reports 12 total case entries:
  7 executable in-repository failure cases and 5 documented-only external
  candidates.
- `evaluation/results.csv` shows 7 executable in-repository cases and 5
  documented-only SkiLoadLab / slsa-verifier cases. The external rows are
  context only and should not be interpreted as reproduced real-world
  executions.

## Speaker Notes

- Emphasize the explicit wrapper: ErrPilot captures commands only when the user
  runs `errpilot run -- ...`; it is not background monitoring.
- Emphasize bounded excerpts: ErrPilot preserves raw logs but handoff artifacts
  use compact evidence and bounded source windows.
- Emphasize replaceable downstream tools: Codex, Aider, Gemini CLI, manual
  review, or other repair workflows can consume the same bundle.
- Emphasize human approval for risky changes: triage records
  `requires_human_approval`, and route generation writes prompts rather than
  changing code.
- Emphasize reproducibility: the main demo uses only a clean clone and local
  examples, while external cases remain documented-only by default.

## Backup Path

If live command output is too verbose, use the generated artifacts as the main
visual path before running the evaluation step:

```bash
cat .errpilot/latest
ls -la .errpilot/runs/$(cat .errpilot/latest)
sed -n '1,120p' .errpilot/runs/$(cat .errpilot/latest)/error_bundle.md
sed -n '1,160p' .errpilot/runs/$(cat .errpilot/latest)/local_triage.json
sed -n '1,180p' .errpilot/runs/$(cat .errpilot/latest)/codex_prompt.md
python3 scripts/evaluate_cases.py
```

Narrate from the files rather than scrolling through raw pytest output. The
core story remains the same: explicit capture, structured bundle, bounded
source evidence, deterministic triage, handoff artifact, and reproducible
evaluation summary.

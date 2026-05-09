# Cross-Project Vignette: SkiLoadLab

This directory records a small cross-project ErrPilot vignette using the public
SkiLoadLab repository:

- Repository: https://github.com/YangchenxiWu/SkiLoadLab
- Local source used for the run: `<SKILOADLAB_ROOT>`
- Run ID: `ase26-skiloadlab-missing-input`
- Failure command:

```bash
<SKILOADLAB_ROOT>/.venv/bin/python -m skiloadlab.cli.combine \
  --in /tmp/skiloadlab_missing_input.csv \
  --out /tmp/skiloadlab_probe/out.csv \
  --report /tmp/skiloadlab_probe/report.json \
  --alpha 0.5
```

The command exercises a real SkiLoadLab package CLI on a deterministic missing
input path. ErrPilot captured the failure, generated a structured bundle,
classified it with local triage, and produced a target-specific handoff record.

Observed artifact facts:

| Field | Value |
|---|---|
| Exit code | `1` |
| Error class | `FileNotFoundError` |
| Missing path | `/tmp/skiloadlab_missing_input.csv` |
| Repo-local source contexts | `skiloadlab/cli/combine.py`, `skiloadlab/core_model.py` |
| Triage severity | `4` |
| Triage route | `manual_plus_agent_investigation` |
| Human approval gate | `true` |
| Handoff artifact | `codex_prompt.md` |

The copied raw artifacts intentionally preserve ErrPilot's recorded command
context. Before including these artifacts in a public archive, consider
regenerating them from a neutral temporary checkout so that absolute local paths
do not appear in the archived files.

# ASE 2026 Terminal Demo Workflow

This workflow is optimized for a 4-5 minute Tools & Datasets screencast.
It presents ErrPilot as a deterministic failure-intake and handoff layer, not
as an autonomous repair agent.

## Positioning

Use this sentence early:

> ErrPilot turns an explicitly wrapped failed command into structured,
> auditable, and reproducible failure artifacts for human or agent handoff.

Avoid these claims:

- ErrPilot fixes bugs automatically.
- ErrPilot is an AI coding assistant wrapper.
- ErrPilot executes downstream repair tools.

Emphasize these claims:

- Raw evidence is preserved in run artifacts.
- Failure evidence is normalized into Markdown and JSON bundles.
- Local triage is deterministic and rule-based.
- Handoff prompts are generated as reviewable artifacts.
- Downstream tools remain replaceable.

## Fresh Clone Setup

Record from a clean clone so the bundle does not show unrelated dirty files.

```bash
mkdir -p ~/ase26-demo
cd ~/ase26-demo
git clone <ERRPILOT_REPO_URL> errpilot
cd errpilot
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
python3 -m pytest
```

For the local working copy in this repository, the deterministic CLI option is:

```bash
errpilot run --run-id ase26-missing-config -- pytest examples/missing_config_failure
```

If recording from another clone, make sure the clone includes the `--run-id`
change before recording.

## One-Command Trial Run

The scripted path pauses between sections so you can record one segment at a
time:

```bash
bash scripts/ase26_terminal_demo.sh
```

The script uses only local examples and no external API.

## Manual Recording Commands

Use these commands if you prefer typing manually.

### 1. Raw Failure

```bash
pytest -q examples/missing_config_failure
```

Highlight:

- `FAILED examples/missing_config_failure/test_missing_config.py::test_required_config_exists`
- `FileNotFoundError`

Do not dwell on the full pytest banner.

### 2. Explicit Capture

```bash
errpilot run --run-id ase26-missing-config -- pytest examples/missing_config_failure
```

Expected shape:

```text
run_id=ase26-missing-config
run_dir=/.../.errpilot/runs/ase26-missing-config
exit_code=1
```

Say:

> ErrPilot captures only the command explicitly passed after `errpilot run --`.

### 3. Raw Artifacts

```bash
ls -1 .errpilot/runs/ase26-missing-config
```

Before bundling, highlight:

- `combined.log`
- `command.txt`
- `metadata.json`
- `stdout.log`
- `stderr.log`

Do not open the full logs unless you need a backup visual.

### 4. Structured Bundle

```bash
errpilot bundle latest
sed -n '1,8p' .errpilot/runs/ase26-missing-config/error_bundle.md
sed -n '/## Pytest Failures/,/## Log Window/p' .errpilot/runs/ase26-missing-config/error_bundle.md
```

Highlight:

- `Run Summary`
- `Pytest Failures`
- `Source Contexts`

Say:

> The Markdown bundle is the reviewer-facing view; the JSON bundle is the
> machine-readable representation.

### 5. Normalized JSON View

```bash
python3 - <<'PY'
import json
from pathlib import Path

run_id = Path(".errpilot/latest").read_text(encoding="utf-8").strip()
bundle = json.loads((Path(".errpilot") / "runs" / run_id / "error_bundle.json").read_text())
view = {
    "schema_version": bundle["schema_version"],
    "command": bundle["command"],
    "exit_code": bundle["run"]["exit_code"],
    "failing_tests": bundle["failing_tests"],
    "source_contexts": bundle["source_contexts"],
}
print(json.dumps(view, indent=2, sort_keys=True))
PY
```

Highlight:

- `schema_version`
- `failing_tests[].error_class`
- `source_contexts[].file`
- `source_contexts[].focus_line`
- bounded `source_contexts[].content`

Avoid showing full `logs.combined_excerpt`; it is too noisy for the main demo.

### 6. Deterministic Local Triage

```bash
errpilot triage latest --local
```

Highlight:

- `severity`
- `recommended_route`
- `requires_human_approval`
- `reason`

Say:

> This is local deterministic triage, not a model call.

### 7. Persisted Triage

```bash
python3 -m json.tool .errpilot/runs/ase26-missing-config/local_triage.json
```

Say:

> The triage result is persisted as an auditable artifact.

### 8. Handoff Prompt Artifact

```bash
errpilot route latest --target codex
sed -n '1,/## Relevant Log Excerpts/p' .errpilot/runs/ase26-missing-config/codex_prompt.md
sed -n '/## Verification Command/,$p' .errpilot/runs/ase26-missing-config/codex_prompt.md
```

Highlight:

- `Failure Summary`
- `Triage Result`
- `Failing Tests`
- `Source Contexts`
- `Verification Command`
- `Constraints`
- `Do Not Do`

Say:

> Route generates a prompt artifact. ErrPilot does not execute Codex or apply a
> patch.

## Pacing

- 0:00-0:25 raw pytest failure
- 0:25-1:05 explicit capture and run directory
- 1:05-2:00 Markdown and JSON bundle
- 2:00-2:45 deterministic local triage
- 2:45-3:45 handoff prompt artifact
- 3:45-4:30 reproducibility and auditability recap

## Terminal Layout

- Use terminal only.
- Use a large font, roughly 18-20 pt.
- Keep terminal width near 100-110 columns.
- Do not use VSCode or an agent UI in the main recording.
- Clear the terminal before starting the real take.

## Known Weaknesses And Fixes

### Weakness: time-based run ids make recordings non-deterministic

Fix:

```bash
errpilot run --run-id ase26-missing-config -- pytest examples/missing_config_failure
```

### Weakness: unrelated dirty git state distracts reviewers

Fix: record from a clean clone. Do not record from an active paper-editing
workspace.

### Weakness: raw pytest logs are visually noisy

Fix: show raw output briefly, then switch to `error_bundle.md`, selected JSON
fields, and `local_triage.json`.

### Weakness: `codex_prompt.md` can look like an agent wrapper

Fix: explicitly say the file is a handoff artifact. Highlight that route does
not execute downstream tools.

### Weakness: plain JSON triage output looks abrupt

Fix for future CLI polish: add a compact human summary such as:

```text
ErrPilot local triage
severity: 4
route: manual_plus_agent_investigation
confidence: 0.70
requires_human_approval: true
artifact: .errpilot/runs/ase26-missing-config/local_triage.json
```

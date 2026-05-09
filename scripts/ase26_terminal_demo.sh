#!/usr/bin/env bash
set -euo pipefail

EP_RUN="ase26-missing-config"
EP_CASE="examples/missing_config_failure"
OPEN_VSCODE="${OPEN_VSCODE:-0}"
EP_RUN_DIR=".errpilot/runs/$EP_RUN"
EP_DEMO_LOG="$EP_RUN_DIR/demo_walkthrough.md"

pause() {
  printf "\n[press Enter to continue] "
  IFS= read -r _ || true
  printf "\n"
}

section() {
  printf "\n"
  printf "========================================================================\n"
  printf "%s\n" "$1"
  printf "========================================================================\n"
}

intent() {
  printf "Purpose: %s\n\n" "$1"
}

checkpoint() {
  printf "Review checkpoint: %s\n" "$1"
}

summary() {
  printf "\033[1m%s\033[0m\n" "$1"
}

field() {
  printf "  \033[36m%-24s\033[0m %s\n" "$1" "$2"
}

run_cmd() {
  printf "$ %s\n" "$*"
  "$@"
}

write_demo_log() {
  python3 scripts/demo_walkthrough_view.py --write "$EP_RUN" "$EP_CASE"
}

show_demo_log() {
  if command -v bat >/dev/null 2>&1; then
    printf "$ %s\n" "bat --style=plain --paging=never $EP_DEMO_LOG"
    bat --style=plain --paging=never "$EP_DEMO_LOG"
    return
  fi

  printf "$ %s\n" "sed -n '1,160p' $EP_DEMO_LOG"
  sed -n '1,160p' "$EP_DEMO_LOG"
}

open_artifact() {
  local path="$1"
  local line="${2:-1}"
  local label="${3:-artifact}"

  checkpoint "$label"

  if [[ "$OPEN_VSCODE" != "1" ]]; then
    printf "[editor checkpoint] %s:%s\n" "$path" "$line"
    return
  fi

  if command -v code >/dev/null 2>&1; then
    printf "$ code -r -g %s:%s\n" "$path" "$line"
    code -r -g "$path:$line"
    return
  fi

  printf "[VS Code unavailable] Open manually: %s:%s\n" "$path" "$line"
}

section "0. Reproducible Setup"
intent "Reset the demo run so every recording starts from the same evidence state."
python3 - <<'PY'
from pathlib import Path
import shutil

run_id = "ase26-missing-config"
run_dir = Path(".errpilot") / "runs" / run_id
latest = Path(".errpilot") / "latest"
latest_link = Path(".errpilot") / "runs" / "latest"

if run_dir.exists():
    shutil.rmtree(run_dir)
if latest.exists() and latest.read_text(encoding="utf-8").strip() == run_id:
    latest.unlink()
if latest_link.is_symlink():
    latest_link.unlink()

print(f"demo_run_id={run_id}")
print("demo_state=clean")
PY
pause

section "1. Baseline Failure Signal"
intent "Show a noisy configuration failure as a reviewer would first encounter it."
printf "Bounded excerpt only; the capture step preserves the full stdout/stderr logs.\n\n"
printf "$ pytest -q %s | sed -n '1,24p'\n" "$EP_CASE"
set +e
pytest -q "$EP_CASE" 2>&1 | sed -n '1,24p'
RAW_EXIT=${PIPESTATUS[0]}
set -e
printf "\n[excerpt truncated; raw failure remains reproducible]\n"
printf "raw_exit_code=%s\n" "$RAW_EXIT"
summary "Raw failure signal"
field "failure mode" "configuration traceback"
field "raw exit code" "$RAW_EXIT"
field "full log preserved in" "$EP_RUN_DIR/combined.log"
pause

section "2. Capture Command Evidence"
intent "Convert an ephemeral failing command into an auditable run record."
printf "$ errpilot run --run-id %s -- pytest %s\n" "$EP_RUN" "$EP_CASE"
printf "capture.metadata=recorded\n"
printf "capture.streams=stdout,stderr,combined\n"
printf "capture.command_context=preserved\n"
set +e
errpilot run --run-id "$EP_RUN" -- pytest "$EP_CASE"
CAPTURE_EXIT=$?
set -e
printf "capture.status=stored\n"
printf "capture_command_exit_code=%s\n" "$CAPTURE_EXIT"
summary "Capture summary"
field "run id" "$EP_RUN"
field "run directory" "$EP_RUN_DIR"
field "stored streams" "stdout.log, stderr.log, combined.log"
pause

section "3. Inspect Immutable Run Record"
intent "Verify the raw evidence files before any parsing or triage is introduced."
run_cmd ls -1 "$EP_RUN_DIR"
checkpoint "raw evidence inventory: logs, command text, metadata"
summary "Immutable evidence layer"
field "metadata" "$EP_RUN_DIR/metadata.json"
field "command text" "$EP_RUN_DIR/command.txt"
field "combined log" "$EP_RUN_DIR/combined.log"
pause

section "4. Build Structured Failure Bundle"
intent "Transform raw logs into a reviewable failure representation with source context."
run_cmd errpilot bundle latest
write_demo_log
open_artifact "$EP_RUN_DIR/error_bundle.md" 1 "human-readable failure bundle"
printf "\n$ sed -n '1,8p' .errpilot/runs/%s/error_bundle.md\n" "$EP_RUN"
sed -n '1,8p' ".errpilot/runs/$EP_RUN/error_bundle.md"
printf "\n$ sed -n '/## Pytest Failures/,/## Log Window/p' .errpilot/runs/%s/error_bundle.md\n" "$EP_RUN"
sed -n '/## Pytest Failures/,/## Log Window/p' ".errpilot/runs/$EP_RUN/error_bundle.md"
pause

section "5. Inspect Normalized Schema Fields"
intent "Show the machine-readable fields that downstream tools can consume deterministically."
run_cmd python3 scripts/demo_bundle_view.py
checkpoint "normalized JSON schema is available without reopening the full log"
summary "Schema fields for downstream consumers"
field "artifact" "$EP_RUN_DIR/error_bundle.json"
field "stable fields" "failing_tests, source_contexts, schema_version"
pause

section "6. Deterministic Triage Classification"
intent "Classify the failure with local rules; no model or repair backend is invoked."
run_cmd errpilot triage latest --local
write_demo_log
summary "ErrPilot local triage"
python3 scripts/demo_triage_summary.py
pause

section "7. Persist Triage Decision Record"
intent "Make the routing decision auditable as data, not terminal-only narration."
open_artifact "$EP_RUN_DIR/local_triage.json" 1 "persisted triage decision record"
run_cmd python3 scripts/demo_triage_view.py
pause

section "8. Generate Reviewable Handoff Record"
intent "Package the evidence, constraints, and verification command for a controlled debugging handoff."
run_cmd errpilot route latest --target codex
write_demo_log
open_artifact "$EP_RUN_DIR/codex_prompt.md" 1 "target-specific handoff record"
printf "\n$ sed -n '1,/## Failing Tests/p' .errpilot/runs/%s/codex_prompt.md\n" "$EP_RUN"
sed -n '1,/## Failing Tests/p' ".errpilot/runs/$EP_RUN/codex_prompt.md"
printf "\n$ sed -n '/## Verification Command/,\$p' .errpilot/runs/%s/codex_prompt.md\n" "$EP_RUN"
sed -n '/## Verification Command/,$p' ".errpilot/runs/$EP_RUN/codex_prompt.md"
pause

section "9. Audit Artifact Inventory"
intent "Confirm the final run directory contains raw evidence, structured bundles, triage, and handoff records."
write_demo_log
run_cmd ls -1 "$EP_RUN_DIR"
pause

section "10. Walkthrough Recap"
intent "Review the generated demo log as a compact, reproducible artifact trail."
show_demo_log
pause

section "11. Artifact Readiness Check"
intent "Keep the recording short here; run the full reproducibility check before submission."
if [[ "${RUN_ARTIFACT_CHECK:-0}" == "1" ]]; then
  run_cmd python3 scripts/check_artifact.py
else
  printf "Full artifact check is available but skipped for pacing.\n"
  printf "Run it before the final recording with:\n"
  printf "$ RUN_ARTIFACT_CHECK=1 bash scripts/ase26_terminal_demo.sh\n"
  printf "\nOr run directly:\n"
  printf "$ python3 scripts/check_artifact.py\n"
fi

printf "\nDemo complete. Evidence capture, structuring, triage, and handoff were demonstrated.\n"
printf "No autonomous repair backend or external model was executed.\n"

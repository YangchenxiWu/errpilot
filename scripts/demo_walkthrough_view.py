"""Write a compact Markdown walkthrough for the latest ASE demo run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("run_id")
    parser.add_argument("case")
    args = parser.parse_args()

    run_dir = Path(".errpilot") / "runs" / args.run_id
    content = build_walkthrough(run_dir, args.run_id, args.case)
    if args.write:
        (run_dir / "demo_walkthrough.md").write_text(content, encoding="utf-8")
    else:
        print(content, end="")
    return 0


def build_walkthrough(run_dir: Path, run_id: str, case: str) -> str:
    lines = [
        "# ASE Demo Artifact Trail",
        "",
        f"- run_id: `{run_id}`",
        f"- command: `pytest {case}`",
        f"- run_dir: `{run_dir}`",
        "",
        "## Evidence Layers",
        "",
        "- raw logs: `stdout.log`, `stderr.log`, `combined.log`",
        "- command context: `command.txt`, `metadata.json`",
    ]

    bundle_path = run_dir / "error_bundle.json"
    if bundle_path.exists():
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        lines.extend(
            [
                "- structured bundle: `error_bundle.md`, `error_bundle.json`",
                "",
                "## Normalized Failure Signal",
                "",
                f"- schema_version: `{bundle.get('schema_version')}`",
                f"- failing_tests: `{len(_list(bundle.get('failing_tests')))}`",
                f"- source_contexts: `{len(_list(bundle.get('source_contexts')))}`",
            ]
        )

    triage_path = run_dir / "local_triage.json"
    if triage_path.exists():
        triage = json.loads(triage_path.read_text(encoding="utf-8"))
        lines.extend(
            [
                "",
                "## Routing Decision",
                "",
                f"- severity: `S{triage.get('severity')}`",
                f"- confidence: `{triage.get('confidence')}`",
                f"- route: `{triage.get('recommended_route')}`",
                f"- requires_human_approval: `{triage.get('requires_human_approval')}`",
                f"- reason: {triage.get('reason')}",
            ]
        )

    handoff_path = run_dir / "codex_prompt.md"
    if handoff_path.exists():
        lines.extend(
            [
                "",
                "## Controlled Handoff",
                "",
                "- artifact: `codex_prompt.md`",
                "- downstream execution: `not executed by ErrPilot`",
                "- verification command is included in the handoff record",
            ]
        )

    lines.extend(
        [
            "",
            "## Review Claim",
            "",
            "ErrPilot converts a noisy failed command into auditable raw evidence,",
            "a normalized failure schema, a deterministic routing decision, and a",
            "reviewable handoff artifact without executing an autonomous repair backend.",
            "",
        ]
    )
    return "\n".join(lines)


def _list(value: object) -> list[object]:
    return value if isinstance(value, list) else []


if __name__ == "__main__":
    raise SystemExit(main())

"""Print a compact terminal summary of the latest ErrPilot triage record."""

from __future__ import annotations

import json
from pathlib import Path


def _cyan(label: str) -> str:
    return f"\033[36m{label}\033[0m"


def _bold(value: object) -> str:
    return f"\033[1m{value}\033[0m"


def main() -> int:
    run_id = Path(".errpilot/latest").read_text(encoding="utf-8").strip()
    run_dir = Path(".errpilot") / "runs" / run_id
    triage = json.loads((run_dir / "local_triage.json").read_text(encoding="utf-8"))
    confidence = float(triage["confidence"])
    print(
        f"  {_cyan('severity')} {_bold(triage['severity'])}   "
        f"{_cyan('route')} {_bold(triage['recommended_route'])}   "
        f"{_cyan('confidence')} {_bold(f'{confidence:.2f}')}"
    )
    print(f"  {_cyan('requires_human_approval')} {_bold(str(triage['requires_human_approval']).lower())}")
    print(f"  {_cyan('reason')} {triage['reason']}")
    print(f"  {_cyan('artifact')} {run_dir / 'local_triage.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

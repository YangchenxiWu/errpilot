"""Print a compact JSON view of the latest ErrPilot triage record for demos."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    run_id = Path(".errpilot/latest").read_text(encoding="utf-8").strip()
    triage_path = Path(".errpilot") / "runs" / run_id / "local_triage.json"
    triage = json.loads(triage_path.read_text(encoding="utf-8"))
    view = {
        "severity": f"S{triage['severity']}",
        "recommended_route": triage["recommended_route"],
        "requires_human_approval": triage["requires_human_approval"],
        "reason": triage["reason"],
    }
    print(json.dumps(view, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

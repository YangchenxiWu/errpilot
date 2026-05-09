"""Print a compact JSON view of the latest ErrPilot error bundle for demos."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    run_id = Path(".errpilot/latest").read_text(encoding="utf-8").strip()
    bundle_path = Path(".errpilot") / "runs" / run_id / "error_bundle.json"
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    view = {
        "schema_version": bundle["schema_version"],
        "failing_tests": [
            {
                "nodeid": failure["nodeid"],
                "file": failure["file"],
                "test_name": failure["test_name"],
                "error_class": failure["error_class"],
            }
            for failure in bundle["failing_tests"]
        ],
        "source_contexts": [
            {
                "file": context["file"],
                "focus_line": context["focus_line"],
                "line_start": context["line_start"],
                "line_end": context["line_end"],
                "role": context["role"],
            }
            for context in bundle["source_contexts"]
        ],
    }
    print(json.dumps(view, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

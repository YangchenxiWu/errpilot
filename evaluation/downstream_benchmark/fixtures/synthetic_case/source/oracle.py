"""Deterministic synthetic oracle; not scientific benchmark evidence."""

from __future__ import annotations

import sys

from subject import answer

print("SYNTHETIC_EXPECTED_TEST_OBSERVED")
if answer() != 2:
    print("expected answer() == 2", file=sys.stderr)
    raise SystemExit(1)

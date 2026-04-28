"""Parser for pytest failure summary text."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass


FAILED_RE = re.compile(r"^FAILED\s+(\S+)(?:\s+-\s+(.*))?\s*$")
ERROR_RE = re.compile(r"^ERROR\s+(\S+).*$")
ERROR_CLASS_RE = re.compile(r"^((?:[A-Za-z_][A-Za-z0-9_]*\.)*[A-Z][A-Za-z0-9_]*(?:Error|Exception)?)\b")


@dataclass
class PytestFailure:
    nodeid: str
    file: str | None
    test_name: str | None
    error_class: str | None
    summary: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class PytestReport:
    framework: str
    failing_tests: list[PytestFailure]

    def to_dict(self) -> dict[str, object]:
        return {
            "framework": self.framework,
            "failing_tests": [failure.to_dict() for failure in self.failing_tests],
        }


def parse_pytest_failures(text: str) -> PytestReport | None:
    """Parse pytest FAILED and ERROR summary lines from raw pytest output."""
    failures: list[PytestFailure] = []
    seen_nodeids: set[str] = set()
    has_missing_fixture = "fixture" in text and "not found" in text

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        failure = _parse_failed_line(stripped, text)
        if failure is None:
            failure = _parse_error_line(stripped, has_missing_fixture)
        if failure is None or failure.nodeid in seen_nodeids:
            continue

        seen_nodeids.add(failure.nodeid)
        failures.append(failure)

    if not failures:
        return None
    return PytestReport(framework="pytest", failing_tests=failures)


def _parse_failed_line(line: str, text: str) -> PytestFailure | None:
    match = FAILED_RE.match(line)
    if match is None:
        return None

    nodeid, reason = match.groups()
    file, test_name = _split_nodeid(nodeid)
    return PytestFailure(
        nodeid=nodeid,
        file=file,
        test_name=test_name,
        error_class=_extract_error_class(reason or "") or _extract_error_class_from_text(text),
        summary=line,
    )


def _parse_error_line(line: str, has_missing_fixture: bool) -> PytestFailure | None:
    match = ERROR_RE.match(line)
    if match is None:
        return None

    nodeid = match.group(1)
    file, test_name = _split_nodeid(nodeid)
    return PytestFailure(
        nodeid=nodeid,
        file=file,
        test_name=test_name,
        error_class="FixtureError" if has_missing_fixture else None,
        summary=line,
    )


def _split_nodeid(nodeid: str) -> tuple[str | None, str | None]:
    parts = nodeid.split("::")
    file = parts[0] or None
    test_name = parts[-1] if len(parts) > 1 else None
    return file, test_name


def _extract_error_class(reason: str) -> str | None:
    match = ERROR_CLASS_RE.match(reason.strip())
    if match is None:
        return None
    return match.group(1)


def _extract_error_class_from_text(text: str) -> str | None:
    if "AssertionError" in text:
        return "AssertionError"
    return None

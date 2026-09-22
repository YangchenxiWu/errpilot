"""Inert, reproducible audit of the frozen BugsInPy environment inputs.

This module reads only the pinned BugsInPy metadata and the committed screening
ledger. It never imports, sources, installs, or executes a subject input.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

from . import executor


FIELDS = (
    "initial_selection_order", "canonical_case_id", "project", "python_version",
    "bug_info_sha256", "project_info_sha256",
    "requirements_present", "requirements_sha256", "requirements_line_count",
    "requirements_encoding", "setup_present", "setup_sha256", "setup_line_count",
    "pythonpath_present", "pythonpath_metadata", "setup_classification",
    "setup_line_classifications", "source_build_required_or_possible",
    "environment_mode", "base_runtime_status", "environment_feasibility_status",
    "blocking_reason",
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _decode_requirements(data: bytes) -> tuple[str, str]:
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16"), "UTF-16_WITH_BOM"
    return data.decode("utf-8"), "UTF-8"


def classify_setup_line(line: str) -> str:
    """Conservatively classify one literal substantive setup line."""
    stripped = line.strip()
    if re.match(r"^(?:python\s+setup\.py\s+test\b|make\s+test\b|tox(?:\s|$))", stripped):
        return "TEST_INVOCATION"
    if re.search(r"(?:^|\s)(?:pytest|py\.test|nosetests|unittest)(?:\s|$)", stripped):
        if not re.match(r"^(?:pip|pip3|python\s+-m\s+pip)\s+install\b", stripped):
            return "TEST_INVOCATION"
    if re.match(r"^(?:pip|pip3|python\s+-m\s+pip)\s+install\s+-e\s+\.", stripped):
        return "PROJECT_INSTALL_OR_BUILD"
    if re.match(r"^python\s+setup\.py\s+(?:install|build|build_ext)\b", stripped):
        return "PROJECT_INSTALL_OR_BUILD"
    if re.match(r"^(?:pip|pip3|python\s+-m\s+pip)\s+install\b", stripped):
        return "DEPENDENCY_INSTALL"
    if re.match(r"^(?:mkdir|touch|cp|mv|ln)\s+", stripped):
        return "FILESYSTEM_PREPARATION"
    if re.match(r"^(?:export|set)\s+", stripped):
        return "ENVIRONMENT_CONFIGURATION"
    if re.match(r"^(?:curl|wget|ssh|scp)\s+", stripped):
        return "NETWORK_OR_EXTERNAL_SERVICE"
    return "UNSUPPORTED_OR_AMBIGUOUS"


def _literal_pythonpaths(data: bytes) -> list[str]:
    text = data.decode("utf-8", errors="replace")
    values = []
    for line in text.splitlines():
        match = re.fullmatch(r'\s*(?:pythonpath|PYTHONPATH)\s*=\s*"([^"]*)"\s*', line)
        if match and match.group(1):
            values.append(match.group(1))
    return values


def audit_rows(benchmark_root: Path, bugsinpy_root: Path) -> list[dict[str, str]]:
    executor.validate_controlling_inputs(benchmark_root)
    executor.validate_bugsinpy_checkout(bugsinpy_root)
    candidates = executor.load_frozen_candidates(benchmark_root)
    executor.validate_frozen_order_against_spec(candidates, benchmark_root / "SCREENING_SPEC_V1.md")
    with (benchmark_root / "screening_execution_plan.csv").open(newline="", encoding="utf-8") as handle:
        plans = list(csv.DictReader(handle))
    if len(plans) != executor.INITIAL_CASE_COUNT:
        raise executor.PreparationError("execution plan is not 40 rows")
    if [(int(p["initial_selection_order"]), p["canonical_case_id"]) for p in plans] != [
        (c.selection_order, c.canonical_case_id) for c in candidates
    ]:
        raise executor.PreparationError("execution plan order does not match frozen candidates")
    if any(p["screening_ready"] != "true" or p["oracle_plan_status"] != "RESOLVED_ORDERED_COMMANDS"
           for p in plans):
        raise executor.PreparationError("a frozen candidate is not preparation-ready")

    rows: list[dict[str, str]] = []
    for candidate, plan in zip(candidates, plans, strict=True):
        case_dir = bugsinpy_root / "projects" / candidate.project / "bugs" / candidate.bug_id
        project_dir = case_dir.parent.parent
        bug_info = (case_dir / "bug.info").read_bytes()
        project_info = (project_dir / "project.info").read_bytes()
        version_match = re.search(
            rb'^\s*python_version\s*=\s*"([^"]+)"', bug_info, re.MULTILINE
        )
        if version_match is None or version_match.group(1).decode("ascii") != candidate.python_version:
            raise executor.PreparationError(
                f"declared Python version drift: {candidate.canonical_case_id}"
            )
        requirement_path = case_dir / "requirements.txt"
        setup_path = case_dir / "setup.sh"
        requirements = requirement_path.read_bytes() if requirement_path.is_file() else None
        setup = setup_path.read_bytes() if setup_path.is_file() else None
        requirement_text, encoding = _decode_requirements(requirements) if requirements is not None else ("", "ABSENT")
        setup_text = setup.decode("utf-8") if setup is not None else ""
        setup_lines = [line for line in setup_text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
        classified = [
            {"line": number, "category": classify_setup_line(line), "text": line}
            for number, line in enumerate(setup_text.splitlines(), 1)
            if line.strip() and not line.lstrip().startswith("#")
        ]
        categories = list(dict.fromkeys(item["category"] for item in classified))
        pythonpaths = _literal_pythonpaths(bug_info) + _literal_pythonpaths(project_info)
        normalized_project = re.sub(r"[-_.]+", "", candidate.project).lower()
        self_vcs = []
        self_package = []
        for line in requirement_text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("-e git+") and f"#egg={candidate.project}".lower() in line.lower():
                self_vcs.append(line)
            name = re.match(r"([A-Za-z0-9_.-]+)\s*(?:==|>=|<=|~=|!=|>|<)", line)
            if name and re.sub(r"[-_.]+", "", name.group(1)).lower() == normalized_project:
                self_package.append(line)
        source_build = "PROJECT_INSTALL_OR_BUILD" in categories or bool(self_vcs)
        if source_build:
            mode = "REVISION_SPECIFIC_BUILD_REQUIRED"
        elif self_package:
            mode = "UNRESOLVED"
        else:
            mode = "SOURCE_INDEPENDENT_ENVIRONMENT"
        blockers = ["DOCKER_DAEMON_REQUIRED", "BASE_PYTHON_EXECUTABLE_PROBE_REQUIRED"]
        if encoding == "UTF-16_WITH_BOM":
            blockers.append("UTF16_REQUIREMENTS_CONVERSION_RECIPE_REQUIRED")
        if self_vcs:
            blockers.append("SELF_VCS_REQUIREMENT_REVISION_RULE_REQUIRED")
            if any(f"@{plan['buggy_commit_full']}" not in line for line in self_vcs):
                blockers.append("SELF_VCS_REFERENCE_DIFFERS_FROM_BUGGY_REVISION")
                mode = "UNRESOLVED"
        if self_package and not source_build:
            blockers.append("SELF_PACKAGE_PIN_SOURCE_SELECTION_UNRESOLVED")
        if "TEST_INVOCATION" in categories:
            blockers.append("SETUP_CONTAINS_TEST_INVOCATION")
        if "UNSUPPORTED_OR_AMBIGUOUS" in categories:
            blockers.append("SETUP_SEMANTICS_UNRESOLVED")
            mode = "UNRESOLVED"
        rows.append({
            "initial_selection_order": str(candidate.selection_order),
            "canonical_case_id": candidate.canonical_case_id,
            "project": candidate.project,
            "python_version": candidate.python_version,
            "bug_info_sha256": _sha256(bug_info),
            "project_info_sha256": _sha256(project_info),
            "requirements_present": str(requirements is not None).lower(),
            "requirements_sha256": _sha256(requirements) if requirements is not None else "ABSENT",
            "requirements_line_count": str(len(requirement_text.splitlines())),
            "requirements_encoding": encoding,
            "setup_present": str(setup is not None).lower(),
            "setup_sha256": _sha256(setup) if setup is not None else "ABSENT",
            "setup_line_count": str(len(setup_lines)),
            "pythonpath_present": str(bool(pythonpaths)).lower(),
            "pythonpath_metadata": json.dumps(pythonpaths, separators=(",", ":")),
            "setup_classification": "|".join(categories) if categories else "NONE",
            "setup_line_classifications": json.dumps(classified, separators=(",", ":")),
            "source_build_required_or_possible": str(source_build).lower(),
            "environment_mode": mode,
            "base_runtime_status": "METADATA_IDENTIFIED_PROBE_PENDING",
            "environment_feasibility_status": "UNRESOLVED_NOT_BUILT",
            "blocking_reason": "|".join(blockers),
        })
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    benchmark = Path(__file__).resolve().parents[1]
    bugsinpy = Path("/Users/wuyangchenxi/errpilot-benchmark-work/bugsinpy")
    write_csv(benchmark / "environment_requirements.csv", audit_rows(benchmark, bugsinpy))

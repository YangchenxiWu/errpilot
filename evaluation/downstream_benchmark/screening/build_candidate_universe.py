#!/usr/bin/env python3
"""Build the metadata-only BugsInPy screening census and frozen candidate order."""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path


SEED = "20260922"
INITIAL_TARGET = 40
MINIMUM_PROJECTS = 10
MAXIMUM_PER_PROJECT = 4
SOURCE_COMMIT = "11c5f1eea954a42132cfd06bf257766a7963e0fd"
COMMIT_RE = re.compile(r"[0-9a-fA-F]{7,40}")
ASSIGNMENT_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$")
UNQUOTED_VALUE_RE = re.compile(r"[A-Za-z0-9._:/+@-]+")

UNIVERSE_FIELDS = (
    "candidate_rank",
    "initial_selection_order",
    "selected_initial_40",
    "project",
    "project_source_url",
    "bugsinpy_bug_id",
    "canonical_case_id",
    "rank_sha256",
    "project_status",
    "python_version",
    "buggy_commit_id",
    "fixed_commit_id",
    "declared_test_file",
    "run_test_exists",
    "setup_exists",
    "requirements_exists",
    "metadata_status",
    "metadata_exclusion_reason",
    "bugsinpy_source_commit",
)

EXCLUSION_FIELDS = (
    "project",
    "bugsinpy_bug_id",
    "canonical_case_id",
    "metadata_exclusion_reason",
    "detail",
    "bugsinpy_source_commit",
)


class MetadataParseError(ValueError):
    """Raised when an info file is not a sequence of literal assignments."""


@dataclass
class CaseRecord:
    project: str
    bug_id: str
    project_source_url: str = ""
    project_status: str = ""
    python_version: str = ""
    buggy_commit_id: str = ""
    fixed_commit_id: str = ""
    declared_test_file: str = ""
    run_test_exists: bool = False
    setup_exists: bool = False
    requirements_exists: bool = False
    exclusion_details: list[tuple[str, str]] = field(default_factory=list)
    candidate_rank: int | None = None
    rank_sha256: str = ""
    initial_selection_order: int | None = None

    @property
    def canonical_case_id(self) -> str:
        return f"{self.project}::{self.bug_id}"

    @property
    def is_eligible(self) -> bool:
        return not self.exclusion_details

    def exclude(self, reason: str, detail: str) -> None:
        item = (reason, detail)
        if item not in self.exclusion_details:
            self.exclusion_details.append(item)


def parse_literal_assignments(path: Path) -> dict[str, str]:
    """Parse inert scalar assignments without sourcing or executing the file."""
    values: dict[str, str] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = ASSIGNMENT_RE.fullmatch(line)
        if match is None:
            raise MetadataParseError(f"line {line_number}: not a scalar assignment")
        key, raw_value = match.groups()
        if key in values:
            raise MetadataParseError(f"line {line_number}: duplicate key {key}")
        if not raw_value:
            value = ""
        elif raw_value[0] in {'\"', "'"}:
            try:
                parsed = ast.literal_eval(raw_value)
            except (SyntaxError, ValueError) as exc:
                raise MetadataParseError(
                    f"line {line_number}: invalid quoted value for {key}"
                ) from exc
            if not isinstance(parsed, str):
                raise MetadataParseError(f"line {line_number}: non-string value for {key}")
            value = parsed
        elif UNQUOTED_VALUE_RE.fullmatch(raw_value):
            value = raw_value
        else:
            raise MetadataParseError(f"line {line_number}: unsafe unquoted value for {key}")
        values[key] = value.strip()
    return values


def validate_source_checkout(root: Path, expected_commit: str) -> None:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    actual_commit = result.stdout.strip()
    if actual_commit != expected_commit:
        raise RuntimeError(
            f"BugsInPy source mismatch: expected {expected_commit}, found {actual_commit}"
        )


def census_case(project_dir: Path, bug_dir: Path) -> CaseRecord:
    record = CaseRecord(project=project_dir.name, bug_id=bug_dir.name)
    project_info_path = project_dir / "project.info"
    bug_info_path = bug_dir / "bug.info"

    project_info: dict[str, str] = {}
    if not project_info_path.is_file():
        record.exclude("PROJECT_INFO_MISSING", "project.info does not exist")
    else:
        try:
            project_info = parse_literal_assignments(project_info_path)
        except (MetadataParseError, UnicodeDecodeError) as exc:
            record.exclude("PROJECT_INFO_UNPARSEABLE", str(exc))

    record.project_source_url = project_info.get("github_url", "")
    record.project_status = project_info.get("status", "")
    if project_info_path.is_file() and record.project_status != "OK":
        record.exclude(
            "PROJECT_STATUS_NOT_OK",
            f"normalized project status is {record.project_status!r}",
        )

    bug_info: dict[str, str] = {}
    if not bug_info_path.is_file():
        record.exclude("BUG_INFO_MISSING", "bug.info does not exist")
    else:
        try:
            bug_info = parse_literal_assignments(bug_info_path)
        except (MetadataParseError, UnicodeDecodeError) as exc:
            record.exclude("BUG_INFO_UNPARSEABLE", str(exc))

    record.python_version = bug_info.get("python_version", "")
    record.buggy_commit_id = bug_info.get("buggy_commit_id", "")
    record.fixed_commit_id = bug_info.get("fixed_commit_id", "")
    record.declared_test_file = bug_info.get("test_file", "")

    required_fields = (
        ("python_version", record.python_version, "PYTHON_VERSION_MISSING"),
        ("buggy_commit_id", record.buggy_commit_id, "BUGGY_COMMIT_ID_MISSING"),
        ("fixed_commit_id", record.fixed_commit_id, "FIXED_COMMIT_ID_MISSING"),
        ("test_file", record.declared_test_file, "DECLARED_TEST_FILE_MISSING"),
    )
    for field_name, value, reason in required_fields:
        if not value:
            record.exclude(reason, f"{field_name} is absent or empty")

    if record.buggy_commit_id and COMMIT_RE.fullmatch(record.buggy_commit_id) is None:
        record.exclude("BUGGY_COMMIT_ID_INVALID", "buggy_commit_id is not a 7-40 hex Git ID")
    if record.fixed_commit_id and COMMIT_RE.fullmatch(record.fixed_commit_id) is None:
        record.exclude("FIXED_COMMIT_ID_INVALID", "fixed_commit_id is not a 7-40 hex Git ID")
    if record.buggy_commit_id and record.buggy_commit_id == record.fixed_commit_id:
        record.exclude(
            "BUGGY_FIXED_COMMIT_IDS_IDENTICAL",
            "buggy_commit_id and fixed_commit_id are identical",
        )

    run_test_path = bug_dir / "run_test.sh"
    record.run_test_exists = run_test_path.is_file()
    if not record.run_test_exists:
        record.exclude("RUN_TEST_MISSING", "run_test.sh does not exist")
    elif run_test_path.stat().st_size == 0:
        record.exclude("RUN_TEST_EMPTY", "run_test.sh is empty")

    record.setup_exists = (bug_dir / "setup.sh").is_file()
    record.requirements_exists = (bug_dir / "requirements.txt").is_file()
    return record


def census(root: Path) -> list[CaseRecord]:
    projects_root = root / "projects"
    if not projects_root.is_dir():
        raise RuntimeError(f"projects directory not found under {root}")
    records: list[CaseRecord] = []
    for project_dir in sorted(path for path in projects_root.iterdir() if path.is_dir()):
        bugs_dir = project_dir / "bugs"
        if not bugs_dir.is_dir():
            continue
        for bug_dir in sorted(path for path in bugs_dir.iterdir() if path.is_dir()):
            records.append(census_case(project_dir, bug_dir))
    return records


def rank_and_select(records: list[CaseRecord]) -> tuple[list[CaseRecord], bool]:
    eligible = [record for record in records if record.is_eligible]
    for record in eligible:
        rank_input = f"{SEED}|candidate|{record.canonical_case_id}".encode()
        record.rank_sha256 = hashlib.sha256(rank_input).hexdigest()
    eligible.sort(key=lambda record: (record.rank_sha256, record.canonical_case_id))
    for candidate_rank, record in enumerate(eligible, 1):
        record.candidate_rank = candidate_rank

    target = min(INITIAL_TARGET, len(eligible))
    selected: list[CaseRecord] = []
    project_counts: Counter[str] = Counter()
    for record in eligible:
        if project_counts[record.project] >= MAXIMUM_PER_PROJECT:
            continue
        selected.append(record)
        project_counts[record.project] += 1
        if len(selected) == target:
            break

    used_diversity_pass = False
    eligible_projects = sorted({record.project for record in eligible})
    if len({record.project for record in selected}) < MINIMUM_PROJECTS and len(
        eligible_projects
    ) >= MINIMUM_PROJECTS:
        used_diversity_pass = True
        selected = []
        project_counts.clear()
        project_order = sorted(
            eligible_projects,
            key=lambda project: (
                hashlib.sha256(f"{SEED}|project|{project}".encode()).hexdigest(),
                project,
            ),
        )
        by_project = {
            project: [record for record in eligible if record.project == project]
            for project in project_order[:MINIMUM_PROJECTS]
        }
        for project in project_order[:MINIMUM_PROJECTS]:
            record = by_project[project][0]
            selected.append(record)
            project_counts[project] += 1
        for record in eligible:
            if record in selected or project_counts[record.project] >= MAXIMUM_PER_PROJECT:
                continue
            selected.append(record)
            project_counts[record.project] += 1
            if len(selected) == target:
                break

    for selection_order, record in enumerate(selected, 1):
        record.initial_selection_order = selection_order

    if len(selected) != target:
        raise RuntimeError(
            f"candidate constraints yield {len(selected)} selections for target {target}"
        )
    if len(eligible) >= INITIAL_TARGET and len(selected) != INITIAL_TARGET:
        raise RuntimeError("metadata universe cannot yield exactly 40 initial candidates")
    if len(eligible_projects) >= MINIMUM_PROJECTS and len(
        {record.project for record in selected}
    ) < MINIMUM_PROJECTS:
        raise RuntimeError("candidate set cannot yield 10 represented projects")
    if any(count > MAXIMUM_PER_PROJECT for count in project_counts.values()):
        raise RuntimeError("candidate set exceeds the four-case project cap")
    return selected, used_diversity_pass


def write_universe(path: Path, records: list[CaseRecord], source_commit: str) -> None:
    ordered = sorted(
        records,
        key=lambda record: (
            record.candidate_rank is None,
            record.candidate_rank or 0,
            record.canonical_case_id,
        ),
    )
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=UNIVERSE_FIELDS, lineterminator="\n")
        writer.writeheader()
        for record in ordered:
            writer.writerow(
                {
                    "candidate_rank": record.candidate_rank or "",
                    "initial_selection_order": record.initial_selection_order or "",
                    "selected_initial_40": str(record.initial_selection_order is not None).lower(),
                    "project": record.project,
                    "project_source_url": record.project_source_url,
                    "bugsinpy_bug_id": record.bug_id,
                    "canonical_case_id": record.canonical_case_id,
                    "rank_sha256": record.rank_sha256,
                    "project_status": record.project_status,
                    "python_version": record.python_version,
                    "buggy_commit_id": record.buggy_commit_id,
                    "fixed_commit_id": record.fixed_commit_id,
                    "declared_test_file": record.declared_test_file,
                    "run_test_exists": str(record.run_test_exists).lower(),
                    "setup_exists": str(record.setup_exists).lower(),
                    "requirements_exists": str(record.requirements_exists).lower(),
                    "metadata_status": (
                        "METADATA_ELIGIBLE" if record.is_eligible else "METADATA_EXCLUDED"
                    ),
                    "metadata_exclusion_reason": "|".join(
                        reason for reason, _detail in record.exclusion_details
                    ),
                    "bugsinpy_source_commit": source_commit,
                }
            )


def write_exclusions(path: Path, records: list[CaseRecord], source_commit: str) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXCLUSION_FIELDS, lineterminator="\n")
        writer.writeheader()
        for record in sorted(records, key=lambda item: item.canonical_case_id):
            for reason, detail in sorted(record.exclusion_details):
                writer.writerow(
                    {
                        "project": record.project,
                        "bugsinpy_bug_id": record.bug_id,
                        "canonical_case_id": record.canonical_case_id,
                        "metadata_exclusion_reason": reason,
                        "detail": detail,
                        "bugsinpy_source_commit": source_commit,
                    }
                )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bugsinpy-root", type=Path, required=True)
    parser.add_argument("--candidate-output", type=Path, required=True)
    parser.add_argument("--exclusions-output", type=Path, required=True)
    parser.add_argument("--source-commit", default=SOURCE_COMMIT)
    args = parser.parse_args()

    root = args.bugsinpy_root.resolve(strict=True)
    validate_source_checkout(root, args.source_commit)
    records = census(root)
    selected, used_diversity_pass = rank_and_select(records)
    write_universe(args.candidate_output, records, args.source_commit)
    write_exclusions(args.exclusions_output, records, args.source_commit)

    eligible = [record for record in records if record.is_eligible]
    selected_counts = Counter(record.project for record in selected)
    summary = {
        "source_commit": args.source_commit,
        "census_cases": len(records),
        "metadata_eligible": len(eligible),
        "metadata_excluded": len(records) - len(eligible),
        "eligible_projects": len({record.project for record in eligible}),
        "selected_initial": len(selected),
        "selected_projects": len(selected_counts),
        "maximum_selected_per_project": max(selected_counts.values(), default=0),
        "used_diversity_pass": used_diversity_pass,
    }
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()

"""Summarize ErrPilot evaluation results without modifying them."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_PATH = REPO_ROOT / "evaluation" / "results.csv"
GROUP_COLUMNS = ("failure_type", "source_type", "severity", "route")


def main() -> None:
    rows = read_results(RESULTS_PATH)
    summary = summarize_rows(rows)

    print(f"total cases: {summary['total_cases']}")
    print(f"executable: {summary['executable_count']}")
    print(f"documented-only: {summary['documented_only_count']}")
    print(
        "severity matches among executable: "
        f"{summary['severity_match_count']}/{summary['executable_count']}"
    )
    print(
        "route compatible among executable: "
        f"{summary['route_compatible_count']}/{summary['executable_count']}"
    )

    print("\nCounts")
    print("------")
    for column in GROUP_COLUMNS:
        if column not in summary["counts_by"]:
            print(f"{column}: column not present")
            continue
        print_counts(column, summary["counts_by"][column])

    print("\nMarkdown table")
    print("--------------")
    print(markdown_table(rows))


def read_results(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def summarize_rows(rows: list[dict[str, str]]) -> dict[str, object]:
    executable_rows = [row for row in rows if is_executable(row)]
    documented_only_count = len(rows) - len(executable_rows)

    columns = set().union(*(row.keys() for row in rows)) if rows else set()
    counts_by = {
        column: count_values(rows, column)
        for column in GROUP_COLUMNS
        if column in columns
    }

    return {
        "total_cases": len(rows),
        "executable_count": len(executable_rows),
        "documented_only_count": documented_only_count,
        "severity_match_count": count_true(executable_rows, "severity_match"),
        "route_compatible_count": count_true(executable_rows, "route_compatible"),
        "counts_by": counts_by,
    }


def is_executable(row: dict[str, str]) -> bool:
    return row.get("executed", "").strip().lower() == "true"


def count_true(rows: list[dict[str, str]], column: str) -> int:
    return sum(row.get(column, "").strip().lower() == "true" for row in rows)


def count_values(rows: list[dict[str, str]], column: str) -> Counter[str]:
    values = (row.get(column, "").strip() or "(blank)" for row in rows)
    return Counter(values)


def print_counts(column: str, counts: Counter[str]) -> None:
    print(f"{column}:")
    for value, count in sorted(counts.items()):
        print(f"  {value}: {count}")


def markdown_table(rows: list[dict[str, str]]) -> str:
    columns = [
        "case_id",
        "source_type",
        "executed",
        "error_class",
        "severity",
        "severity_match",
        "route",
        "route_compatible",
    ]
    lines = [
        "| case_id | source_type | executed | error_class | severity | "
        "severity_match | route | route_compatible |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        values = [escape_markdown_cell(row.get(column, "")) for column in columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def escape_markdown_cell(value: str) -> str:
    return (value or "").replace("|", "\\|")


if __name__ == "__main__":
    main()

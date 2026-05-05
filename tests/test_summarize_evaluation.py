from collections import Counter

from scripts.summarize_evaluation import (
    count_values,
    markdown_table,
    summarize_rows,
)


def test_summarize_rows_counts_executable_matches() -> None:
    rows = [
        {
            "case_id": "local_pass",
            "source_type": "local_example",
            "executed": "true",
            "severity_match": "true",
            "route_compatible": "true",
            "severity": "2",
            "route": "codex_or_aider_prompt",
        },
        {
            "case_id": "local_route_mismatch",
            "source_type": "local_example",
            "executed": "true",
            "severity_match": "true",
            "route_compatible": "false",
            "severity": "3",
            "route": "manual_review",
        },
        {
            "case_id": "external_doc",
            "source_type": "github_actions",
            "executed": "false",
            "severity_match": "",
            "route_compatible": "",
            "severity": "",
            "route": "",
        },
    ]

    summary = summarize_rows(rows)

    assert summary["total_cases"] == 3
    assert summary["executable_count"] == 2
    assert summary["documented_only_count"] == 1
    assert summary["severity_match_count"] == 2
    assert summary["route_compatible_count"] == 1
    assert summary["counts_by"]["source_type"] == Counter(
        {"local_example": 2, "github_actions": 1}
    )


def test_count_values_uses_blank_placeholder() -> None:
    assert count_values([{"severity": ""}, {"severity": "2"}], "severity") == Counter(
        {"(blank)": 1, "2": 1}
    )


def test_markdown_table_escapes_pipe_characters() -> None:
    table = markdown_table(
        [
            {
                "case_id": "case|one",
                "source_type": "local_example",
                "executed": "true",
                "error_class": "AssertionError",
                "severity": "2",
                "severity_match": "true",
                "route": "codex_or_aider_prompt",
                "route_compatible": "true",
            }
        ]
    )

    assert "case\\|one" in table
    assert "| case_id | source_type | executed |" in table

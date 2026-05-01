"""Deterministic handoff prompt rendering from ErrPilot error bundles."""

from __future__ import annotations

from dataclasses import dataclass


SUPPORTED_TARGETS = {
    "codex": "codex_prompt.md",
    "aider": "aider_prompt.md",
    "gemini": "gemini_prompt.md",
    "manual": "manual_review.md",
}

TARGET_GUIDANCE = {
    "codex": (
        "Use this as a focused debugging task. Produce a minimal patch and report "
        "verification results."
    ),
    "aider": "Prefer editing the smallest relevant file set and ask before broad changes.",
    "gemini": (
        "Use the large context window for analysis and produce a concise repair plan before "
        "code changes."
    ),
    "manual": "Human review checklist: confirm scope, inspect evidence, decide owner, and verify.",
}


@dataclass(frozen=True)
class HandoffPrompt:
    """Rendered handoff prompt artifact metadata."""

    target: str
    filename: str
    content: str

    def to_dict(self) -> dict[str, object]:
        return {
            "target": self.target,
            "filename": self.filename,
            "content": self.content,
        }


def build_handoff_prompt(bundle: dict[str, object], target: str) -> HandoffPrompt:
    """Build a markdown handoff prompt for a supported target."""
    if target not in SUPPORTED_TARGETS:
        raise ValueError(f"unsupported handoff target: {target}")

    content = "\n".join(
        [
            f"# ErrPilot Handoff: {target}",
            "",
            "## Failure Summary",
            "",
            *_failure_summary_lines(bundle),
            "",
            "## Triage Result",
            "",
            *_triage_lines(bundle),
            "",
            "## Failing Tests",
            "",
            *_failing_test_lines(bundle),
            "",
            "## Source Contexts",
            "",
            *_source_context_lines(bundle),
            "",
            "## Relevant Log Excerpts",
            "",
            *_log_excerpt_lines(bundle),
            "",
            "## Verification Command",
            "",
            _verification_command(bundle),
            "",
            "## Constraints",
            "",
            "- Keep changes minimal.",
            "- Do not modify unrelated files.",
            "- Preserve public behavior unless the failure requires changing it.",
            "- Use the source contexts and failing tests as primary evidence.",
            "- Ask for human approval before any risky or broad change.",
            "",
            "## Do Not Do",
            "",
            "- Do not run destructive commands.",
            (
                "- Do not read or expose secrets, tokens, credentials, .env files, private keys, "
                "or certificates."
            ),
            "- Do not claim success without running the verification command.",
            "- Do not replace this with a broad rewrite.",
            "",
            "## Target Guidance",
            "",
            TARGET_GUIDANCE[target],
            "",
        ]
    )
    return HandoffPrompt(
        target=target,
        filename=SUPPORTED_TARGETS[target],
        content=content,
    )


def _failure_summary_lines(bundle: dict[str, object]) -> list[str]:
    lines = [
        f"- command: `{_string_or_default(bundle.get('command'), 'unknown')}`",
        f"- exit_code: `{_exit_code(bundle)}`",
    ]

    traceback = _as_dict(bundle.get("python_traceback"))
    error_class = _string_or_empty(traceback.get("error_class"))
    error_message = _string_or_empty(traceback.get("error_message"))
    if error_class or error_message:
        lines.append(f"- python_traceback: `{_join_error(error_class, error_message)}`")

    failing_tests = _as_list(bundle.get("failing_tests"))
    if failing_tests:
        lines.append(f"- failing_tests: `{len(failing_tests)}`")

    triage = _as_dict(bundle.get("triage"))
    if triage:
        lines.append(f"- triage_severity: `{triage.get('severity')}`")
        lines.append(f"- triage_recommended_route: `{triage.get('recommended_route')}`")

    return lines


def _triage_lines(bundle: dict[str, object]) -> list[str]:
    triage = _as_dict(bundle.get("triage"))
    if not triage:
        return ["No triage result available."]
    return [
        f"- severity: `{triage.get('severity')}`",
        f"- confidence: `{triage.get('confidence')}`",
        f"- recommended_route: `{triage.get('recommended_route')}`",
        f"- requires_human_approval: `{triage.get('requires_human_approval')}`",
        f"- reason: {triage.get('reason')}",
    ]


def _failing_test_lines(bundle: dict[str, object]) -> list[str]:
    failing_tests = _as_list(bundle.get("failing_tests"))
    if not failing_tests:
        return ["No failing tests detected."]

    lines: list[str] = []
    for index, failure_value in enumerate(failing_tests, start=1):
        failure = _as_dict(failure_value)
        lines.extend(
            [
                f"### Failing Test {index}",
                "",
                f"- nodeid: `{_string_or_default(failure.get('nodeid'), 'unknown')}`",
                f"- file: `{_string_or_default(failure.get('file'), 'unknown')}`",
                f"- test_name: `{_string_or_default(failure.get('test_name'), 'unknown')}`",
                f"- error_class: `{_string_or_default(failure.get('error_class'), 'unknown')}`",
                "",
            ]
        )
    return lines


def _source_context_lines(bundle: dict[str, object]) -> list[str]:
    source_contexts = _as_list(bundle.get("source_contexts"))
    if not source_contexts:
        return ["No source contexts available."]

    lines: list[str] = []
    for index, context_value in enumerate(source_contexts, start=1):
        context = _as_dict(context_value)
        lines.extend(
            [
                f"### Source Context {index}",
                "",
                f"- file: `{_string_or_default(context.get('file'), 'unknown')}`",
                f"- focus_line: `{_string_or_default(context.get('focus_line'), 'unknown')}`",
                f"- role: `{_string_or_default(context.get('role'), 'unknown')}`",
                (
                    "- lines: "
                    f"`{_string_or_default(context.get('line_start'), 'unknown')}-"
                    f"{_string_or_default(context.get('line_end'), 'unknown')}`"
                ),
                "",
                "```text",
                _string_or_empty(context.get("content")).rstrip(),
                "```",
                "",
            ]
        )
    return lines


def _log_excerpt_lines(bundle: dict[str, object]) -> list[str]:
    logs = _as_dict(bundle.get("logs"))
    lines: list[str] = []
    stderr_excerpt = _string_or_empty(logs.get("stderr_excerpt")).strip()
    stdout_excerpt = _string_or_empty(logs.get("stdout_excerpt")).strip()
    combined_excerpt = _string_or_empty(logs.get("combined_excerpt")).strip()

    if stderr_excerpt:
        lines.extend(["### stderr_excerpt", "", "```text", stderr_excerpt, "```", ""])
    if stdout_excerpt:
        lines.extend(["### stdout_excerpt", "", "```text", stdout_excerpt, "```", ""])
    if combined_excerpt and combined_excerpt not in {stderr_excerpt, stdout_excerpt}:
        lines.extend(["### combined_excerpt", "", "```text", combined_excerpt, "```", ""])

    return lines if lines else ["No relevant log excerpts available."]


def _verification_command(bundle: dict[str, object]) -> str:
    command = _string_or_empty(bundle.get("command")).strip()
    if not command:
        return "No verification command available."
    return f"`{command}`"


def _exit_code(bundle: dict[str, object]) -> object:
    run = _as_dict(bundle.get("run"))
    if "exit_code" in run:
        return run["exit_code"]
    if "exit_code" in bundle:
        return bundle["exit_code"]
    return "unknown"


def _join_error(error_class: str, error_message: str) -> str:
    return ": ".join(part for part in (error_class, error_message) if part)


def _as_dict(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _as_list(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def _string_or_empty(value: object) -> str:
    return value if isinstance(value, str) else ""


def _string_or_default(value: object, default: str) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, int | float | bool):
        return str(value)
    return default

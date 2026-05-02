"""Deterministic local triage classification for ErrPilot bundles."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LocalTriageResult:
    """Local-only triage result suitable for JSON serialization."""

    severity: int
    confidence: float
    reason: str
    recommended_route: str
    requires_human_approval: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "severity": self.severity,
            "confidence": self.confidence,
            "reason": self.reason,
            "recommended_route": self.recommended_route,
            "requires_human_approval": self.requires_human_approval,
        }


HIGH_RISK_SIGNALS = (
    "secret",
    "token",
    "credential",
    "password",
    "private key",
    ".env",
    "rm -rf",
    "delete production",
    "destructive",
)

SECURITY_CONTEXT_SIGNALS = (
    "auth",
    "authentication",
    "authorization",
    "security",
    "permission",
    "credential",
    "token",
    "secret",
)

DEPENDENCY_CONFIG_BUILD_SIGNALS = (
    "modulenotfounderror",
    "importerror",
    "missing dependency",
    "dependency resolver",
    "pip install",
    "npm install",
    "build failed",
    "config error",
    "ci",
    "workflow",
    "shell command not found",
    "command not found",
)

REQUIRED_ARTIFACT_SIGNALS = (
    "required artifact",
    "required config",
    "configuration file",
    "config file",
)

LOCAL_ERROR_CLASSES = {"ValueError", "TypeError", "AssertionError"}


def classify_bundle(bundle: dict[str, object]) -> LocalTriageResult:
    """Classify an error bundle using deterministic local rules."""
    text = _combined_searchable_text(bundle)
    lowered = text.lower()
    python_traceback = _as_dict(bundle.get("python_traceback"))
    failing_tests = _as_list(bundle.get("failing_tests"))
    source_contexts = _as_list(bundle.get("source_contexts"))

    if _has_high_risk_signal(lowered):
        return LocalTriageResult(
            severity=5,
            confidence=0.85,
            reason="High-risk or security-sensitive signal detected in the failure bundle.",
            recommended_route="manual_review",
            requires_human_approval=True,
        )

    if _has_pytest_fixture_failure(lowered, failing_tests):
        return LocalTriageResult(
            severity=4,
            confidence=0.75,
            reason=(
                "Missing pytest fixture or test setup/configuration failure detected."
            ),
            recommended_route="manual_plus_agent_investigation",
            requires_human_approval=True,
        )

    if _has_dependency_config_build_signal(lowered, python_traceback):
        return LocalTriageResult(
            severity=4,
            confidence=0.70,
            reason="Dependency, configuration, build, CI, or external-tool failure detected.",
            recommended_route="manual_plus_agent_investigation",
            requires_human_approval=True,
        )

    if len(failing_tests) >= 2:
        return LocalTriageResult(
            severity=3,
            confidence=0.75,
            reason="Multiple failing tests indicate a broader behavior failure.",
            recommended_route="stronger_coding_agent_prompt",
            requires_human_approval=True,
        )

    if _has_multiple_source_files(source_contexts):
        return LocalTriageResult(
            severity=3,
            confidence=0.75,
            reason="Failure context spans multiple source files.",
            recommended_route="stronger_coding_agent_prompt",
            requires_human_approval=True,
        )

    if _is_single_local_pytest_error(failing_tests):
        return LocalTriageResult(
            severity=2,
            confidence=0.78,
            reason="Single local pytest failure with localized failure context.",
            recommended_route="codex_or_aider_prompt",
            requires_human_approval=True,
        )

    error_class = _string_or_empty(python_traceback.get("error_class"))
    if error_class in LOCAL_ERROR_CLASSES:
        return LocalTriageResult(
            severity=2,
            confidence=0.78,
            reason=f"Local Python traceback with {error_class}.",
            recommended_route="codex_or_aider_prompt",
            requires_human_approval=True,
        )

    if _has_trivial_local_signal(lowered, python_traceback, bundle):
        return LocalTriageResult(
            severity=1,
            confidence=0.65,
            reason="Trivial local invocation, syntax, path, or unstructured nonzero failure.",
            recommended_route="local_suggestion",
            requires_human_approval=False,
        )

    return LocalTriageResult(
        severity=1,
        confidence=0.55,
        reason="No structured high-confidence failure pattern detected.",
        recommended_route="local_suggestion",
        requires_human_approval=True,
    )


def _combined_searchable_text(bundle: dict[str, object]) -> str:
    parts: list[str] = []
    _append_value(parts, bundle.get("command"))

    logs = _as_dict(bundle.get("logs"))
    for key in ("stdout_excerpt", "stderr_excerpt", "combined_excerpt"):
        _append_value(parts, logs.get(key))
    log_window = _as_dict(logs.get("log_window"))
    _append_value(parts, log_window.get("excerpt"))

    traceback = _as_dict(bundle.get("python_traceback"))
    _append_value(parts, traceback.get("error_class"))
    _append_value(parts, traceback.get("error_message"))

    for failure in _as_list(bundle.get("failing_tests")):
        _append_value(parts, failure)

    for context in _as_list(bundle.get("source_contexts")):
        context_dict = _as_dict(context)
        _append_value(parts, context_dict.get("file"))
        _append_value(parts, context_dict.get("content"))

    _append_value(parts, bundle.get("risk_flags"))
    return "\n".join(parts)


def _append_value(parts: list[str], value: object) -> None:
    if value is None:
        return
    if isinstance(value, str):
        parts.append(value)
        return
    if isinstance(value, dict):
        for item in value.values():
            _append_value(parts, item)
        return
    if isinstance(value, (list, tuple, set)):
        for item in value:
            _append_value(parts, item)
        return
    parts.append(str(value))


def _has_high_risk_signal(text: str) -> bool:
    if any(signal in text for signal in HIGH_RISK_SIGNALS):
        return True
    return "permission denied" in text and any(
        signal in text for signal in SECURITY_CONTEXT_SIGNALS
    )


def _has_dependency_config_build_signal(
    text: str, python_traceback: dict[str, object]
) -> bool:
    error_class = _string_or_empty(python_traceback.get("error_class"))
    if error_class in {"ModuleNotFoundError", "ImportError"}:
        return True
    if any(signal in text for signal in DEPENDENCY_CONFIG_BUILD_SIGNALS):
        return True
    return "no such file or directory" in text and any(
        signal in text for signal in REQUIRED_ARTIFACT_SIGNALS
    )


def _has_pytest_fixture_failure(text: str, failing_tests: list[object]) -> bool:
    if "fixtureerror" in text:
        return True
    if "fixture" in text and "not found" in text:
        return True
    return any(
        _string_or_empty(_as_dict(failure).get("error_class")) == "FixtureError"
        for failure in failing_tests
    )


def _has_multiple_source_files(source_contexts: list[object]) -> bool:
    files = {
        file_name
        for context in source_contexts
        if (file_name := _string_or_empty(_as_dict(context).get("file")))
    }
    return len(files) >= 2


def _is_single_local_pytest_error(failing_tests: list[object]) -> bool:
    if len(failing_tests) != 1:
        return False
    failure = _as_dict(failing_tests[0])
    return _string_or_empty(failure.get("error_class")) in {"AssertionError", "TypeError"}


def _has_trivial_local_signal(
    text: str, python_traceback: dict[str, object], bundle: dict[str, object]
) -> bool:
    if _string_or_empty(python_traceback.get("error_class")) == "SyntaxError":
        return True
    if "no such file or directory" in text or "file not found" in text:
        return True
    if "command not found" in text or "not recognized as" in text:
        return True
    exit_code = bundle.get("exit_code")
    return isinstance(exit_code, int) and exit_code != 0


def _as_dict(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _as_list(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def _string_or_empty(value: object) -> str:
    return value if isinstance(value, str) else ""

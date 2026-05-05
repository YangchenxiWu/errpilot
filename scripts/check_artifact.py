"""Run the ErrPilot artifact readiness checks."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class CheckStep:
    name: str
    display_command: str
    command: list[str]
    expected_returncode: int = 0


@dataclass(frozen=True)
class CheckResult:
    name: str
    display_command: str
    returncode: int
    expected_returncode: int
    stdout: str
    stderr: str

    @property
    def passed(self) -> bool:
        return self.returncode == self.expected_returncode


CHECK_STEPS = [
    CheckStep(
        name="pytest",
        display_command="python3 -m pytest",
        command=[sys.executable, "-m", "pytest"],
    ),
    CheckStep(
        name="ruff",
        display_command="python3 -m ruff check errpilot tests",
        command=[sys.executable, "-m", "ruff", "check", "errpilot", "tests"],
    ),
    CheckStep(
        name="evaluation",
        display_command="python3 scripts/evaluate_cases.py",
        command=[sys.executable, "scripts/evaluate_cases.py"],
    ),
    CheckStep(
        name="demo run capture",
        display_command="errpilot run -- pytest examples/python_assertion_failure",
        command=["errpilot", "run", "--", "pytest", "examples/python_assertion_failure"],
        expected_returncode=1,
    ),
    CheckStep(
        name="demo bundle",
        display_command="errpilot bundle latest",
        command=["errpilot", "bundle", "latest"],
    ),
    CheckStep(
        name="demo triage",
        display_command="errpilot triage latest --local",
        command=["errpilot", "triage", "latest", "--local"],
    ),
    CheckStep(
        name="demo route",
        display_command="errpilot route latest --target codex",
        command=["errpilot", "route", "latest", "--target", "codex"],
    ),
]


def main() -> int:
    results = [run_step(step) for step in CHECK_STEPS]
    prompt_path = latest_codex_prompt_path(REPO_ROOT)
    prompt_exists = prompt_path.exists()

    print("\nArtifact check summary")
    print("======================")
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"{status} {result.name}: {result.display_command}")
        if not result.passed:
            print(f"  expected exit code: {result.expected_returncode}")
            print(f"  actual exit code: {result.returncode}")
            print_excerpt("stdout", result.stdout)
            print_excerpt("stderr", result.stderr)

    prompt_status = "PASS" if prompt_exists else "FAIL"
    print(f"{prompt_status} codex prompt exists: {prompt_path}")

    if all(result.passed for result in results) and prompt_exists:
        print("artifact check: PASS")
        return 0

    print("artifact check: FAIL")
    return 1


def run_step(step: CheckStep) -> CheckResult:
    completed = subprocess.run(
        step.command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return CheckResult(
        name=step.name,
        display_command=step.display_command,
        returncode=completed.returncode,
        expected_returncode=step.expected_returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def latest_codex_prompt_path(repo_root: Path) -> Path:
    latest_path = repo_root / ".errpilot" / "latest"
    if not latest_path.exists():
        return repo_root / ".errpilot" / "runs" / "<missing-latest>" / "codex_prompt.md"
    run_id = latest_path.read_text(encoding="utf-8").strip()
    return repo_root / ".errpilot" / "runs" / run_id / "codex_prompt.md"


def print_excerpt(label: str, text: str, max_lines: int = 20) -> None:
    if not text.strip():
        return
    print(f"  {label}:")
    for line in text.splitlines()[:max_lines]:
        print(f"    {line}")


if __name__ == "__main__":
    raise SystemExit(main())

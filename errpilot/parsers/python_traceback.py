"""Parser for Python traceback text."""

from __future__ import annotations

import re
from dataclasses import dataclass


TRACEBACK_MARKER = "Traceback (most recent call last):"
FRAME_RE = re.compile(r'^\s*File "(.+?)", line (\d+), in (.+?)\s*$')
ERROR_LINE_RE = re.compile(
    r"^((?:[A-Za-z_][A-Za-z0-9_]*\.)*[A-Z][A-Za-z0-9_]*)(?::\s*(.*))?$"
)


@dataclass
class StackFrame:
    file: str
    line: int
    function: str


@dataclass
class PythonTraceback:
    language: str
    error_class: str | None
    error_message: str | None
    stack_frames: list[StackFrame]

    @property
    def top_frame(self) -> StackFrame | None:
        """Return the frame closest to the exception site."""
        if not self.stack_frames:
            return None
        return self.stack_frames[-1]


def parse_python_traceback(text: str) -> PythonTraceback | None:
    """Parse Python traceback text into structured fields."""
    if TRACEBACK_MARKER not in text:
        return None

    stack_frames = [_parse_frame(line) for line in text.splitlines()]
    stack_frames = [frame for frame in stack_frames if frame is not None]
    error_class, error_message = _parse_error_line(text)

    return PythonTraceback(
        language="python",
        error_class=error_class,
        error_message=error_message,
        stack_frames=stack_frames,
    )


def _parse_frame(line: str) -> StackFrame | None:
    match = FRAME_RE.match(line)
    if match is None:
        return None

    file, line_number, function = match.groups()
    return StackFrame(file=file, line=int(line_number), function=function)


def _parse_error_line(text: str) -> tuple[str | None, str | None]:
    for line in reversed(text.splitlines()):
        stripped = line.strip()
        if not stripped:
            continue

        match = ERROR_LINE_RE.match(stripped)
        if match is None:
            continue

        error_class, error_message = match.groups()
        return error_class, error_message if error_message is not None else ""

    return None, None

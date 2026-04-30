from pathlib import Path

from errpilot.source_context import SourceContext, collect_source_contexts, extract_source_window


def test_extracts_window_around_line_from_repo_local_file(tmp_path: Path) -> None:
    source = tmp_path / "pkg" / "demo.py"
    source.parent.mkdir()
    source.write_text("one\ntwo\nthree\nfour\nfive\n", encoding="utf-8")

    context = extract_source_window("pkg/demo.py", 3, tmp_path, "traceback", radius=1)

    assert context is not None
    assert context.file == "pkg/demo.py"
    assert context.line_start == 2
    assert context.line_end == 4
    assert context.focus_line == 3
    assert context.role == "traceback"
    assert context.content == "two\nthree\nfour"


def test_clamps_line_start_at_one(tmp_path: Path) -> None:
    source = tmp_path / "demo.py"
    source.write_text("one\ntwo\nthree\n", encoding="utf-8")

    context = extract_source_window("demo.py", 1, tmp_path, "traceback", radius=10)

    assert context is not None
    assert context.line_start == 1
    assert context.line_end == 3
    assert context.content == "one\ntwo\nthree"


def test_clamps_line_window_to_file_end(tmp_path: Path) -> None:
    source = tmp_path / "demo.py"
    source.write_text("one\ntwo\nthree\n", encoding="utf-8")

    context = extract_source_window("demo.py", 100, tmp_path, "traceback", radius=1)

    assert context is not None
    assert context.line_start == 3
    assert context.line_end == 3
    assert context.content == "three"


def test_rejects_absolute_path_outside_repo_root(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    outside = tmp_path / "outside.py"
    outside.write_text("print('outside')\n", encoding="utf-8")

    assert extract_source_window(str(outside), 1, repo_root, "traceback") is None


def test_rejects_sensitive_env_file(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("TOKEN=secret\n", encoding="utf-8")

    assert extract_source_window(".env", 1, tmp_path, "config") is None


def test_rejects_binary_file_containing_null_byte(tmp_path: Path) -> None:
    binary = tmp_path / "data.bin"
    binary.write_bytes(b"abc\0def")

    assert extract_source_window("data.bin", 1, tmp_path, "traceback") is None


def test_rejects_missing_file(tmp_path: Path) -> None:
    assert extract_source_window("missing.py", 1, tmp_path, "traceback") is None


def test_to_dict_includes_all_fields() -> None:
    context = SourceContext(
        file="demo.py",
        line_start=1,
        line_end=3,
        focus_line=2,
        role="traceback",
        content="one\ntwo\nthree",
    )

    assert context.to_dict() == {
        "file": "demo.py",
        "line_start": 1,
        "line_end": 3,
        "focus_line": 2,
        "role": "traceback",
        "content": "one\ntwo\nthree",
    }


def test_collects_context_from_traceback_stack_frame(tmp_path: Path) -> None:
    source = tmp_path / "app.py"
    source.write_text("one\ntwo\nthree\n", encoding="utf-8")
    traceback = {"stack_frames": [{"file": "app.py", "line": 2}]}

    contexts = collect_source_contexts(traceback, [], tmp_path, traceback_radius=1)

    assert contexts == [
        {
            "file": "app.py",
            "line_start": 1,
            "line_end": 3,
            "focus_line": 2,
            "role": "traceback_frame",
            "content": "one\ntwo\nthree",
        }
    ]


def test_collects_context_from_failing_tests_file(tmp_path: Path) -> None:
    test_file = tmp_path / "tests" / "test_demo.py"
    test_file.parent.mkdir()
    test_file.write_text("def test_one():\n    assert False\n", encoding="utf-8")
    failing_tests = [{"file": "tests/test_demo.py"}]

    contexts = collect_source_contexts(None, failing_tests, tmp_path, failing_test_radius=1)

    assert contexts == [
        {
            "file": "tests/test_demo.py",
            "line_start": 1,
            "line_end": 2,
            "focus_line": 1,
            "role": "failing_test",
            "content": "def test_one():\n    assert False",
        }
    ]


def test_collect_skips_outside_repo_traceback_frame(tmp_path: Path) -> None:
    outside = tmp_path / "outside.py"
    outside.write_text("print('outside')\n", encoding="utf-8")
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    traceback = {"stack_frames": [{"file": str(outside), "line": 1}]}

    assert collect_source_contexts(traceback, [], repo_root) == []


def test_collect_deduplicates_same_file_focus_line_and_role(tmp_path: Path) -> None:
    source = tmp_path / "app.py"
    source.write_text("one\ntwo\nthree\n", encoding="utf-8")
    traceback = {
        "stack_frames": [
            {"file": "app.py", "line": 2},
            {"file": "app.py", "line": 2},
        ]
    }

    contexts = collect_source_contexts(traceback, [], tmp_path, traceback_radius=1)

    assert len(contexts) == 1
    assert contexts[0]["file"] == "app.py"
    assert contexts[0]["focus_line"] == 2
    assert contexts[0]["role"] == "traceback_frame"


def test_collect_malformed_entries_do_not_crash(tmp_path: Path) -> None:
    source = tmp_path / "tests" / "test_demo.py"
    source.parent.mkdir()
    source.write_text("def test_one():\n    assert False\n", encoding="utf-8")
    traceback = {
        "stack_frames": [
            {"file": "app.py"},
            {"file": 123, "line": 1},
            "not-a-frame",
        ]
    }
    failing_tests = [
        {"file": ""},
        {"line": 1},
        "not-a-failure",
        {"file": "tests/test_demo.py", "line": "not-numeric"},
    ]

    contexts = collect_source_contexts(traceback, failing_tests, tmp_path, failing_test_radius=1)

    assert contexts == [
        {
            "file": "tests/test_demo.py",
            "line_start": 1,
            "line_end": 2,
            "focus_line": 1,
            "role": "failing_test",
            "content": "def test_one():\n    assert False",
        }
    ]

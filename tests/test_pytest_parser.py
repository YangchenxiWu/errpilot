from errpilot.parsers.pytest import parse_pytest_failures


def test_failed_assertion_error_parsing() -> None:
    report = parse_pytest_failures(
        "FAILED examples/python_assertion_failure/test_example.py::test_addition - "
        "AssertionError: assert 3 == 4\n"
    )

    assert report is not None
    assert len(report.failing_tests) == 1
    failure = report.failing_tests[0]
    assert failure.nodeid == "examples/python_assertion_failure/test_example.py::test_addition"
    assert failure.file == "examples/python_assertion_failure/test_example.py"
    assert failure.test_name == "test_addition"
    assert failure.error_class == "AssertionError"


def test_failed_assertion_error_parsing_from_assert_evidence() -> None:
    report = parse_pytest_failures(
        "\n".join(
            [
                "FAILED examples/python_assertion_failure/test_example.py::test_addition",
                "E       assert 3 == 4",
            ]
        )
    )

    assert report is not None
    failure = report.failing_tests[0]
    assert failure.error_class == "AssertionError"


def test_error_fixture_parsing() -> None:
    report = parse_pytest_failures(
        "\n".join(
            [
                "ERROR examples/pytest_fixture_failure/test_fixture.py::test_needs_missing_fixture",
                "E       fixture 'missing_fixture' not found",
            ]
        )
    )

    assert report is not None
    failure = report.failing_tests[0]
    assert failure.error_class == "FixtureError"
    assert failure.test_name == "test_needs_missing_fixture"


def test_failed_type_error_parsing_from_failure_body() -> None:
    report = parse_pytest_failures(
        "\n".join(
            [
                "FAILED examples/python_type_error_failure/test_type_error.py::test_increment",
                'E       TypeError: can only concatenate str (not "int") to str',
            ]
        )
    )

    assert report is not None
    failure = report.failing_tests[0]
    assert failure.error_class == "TypeError"


def test_error_module_not_found_parsing_from_failure_body() -> None:
    report = parse_pytest_failures(
        "\n".join(
            [
                "ERROR examples/python_import_failure/test_import_failure.py",
                "E   ModuleNotFoundError: No module named 'definitely_missing_errpilot_dependency'",
            ]
        )
    )

    assert report is not None
    failure = report.failing_tests[0]
    assert failure.error_class == "ModuleNotFoundError"


def test_multiple_failed_lines_preserve_order() -> None:
    report = parse_pytest_failures(
        "\n".join(
            [
                "FAILED tests/test_one.py::test_alpha - AssertionError: assert False",
                "FAILED tests/test_two.py::test_beta - ValueError: bad value",
            ]
        )
    )

    assert report is not None
    assert len(report.failing_tests) == 2
    assert report.failing_tests[0].nodeid == "tests/test_one.py::test_alpha"
    assert report.failing_tests[1].nodeid == "tests/test_two.py::test_beta"


def test_duplicate_nodeids_returned_once() -> None:
    line = "FAILED tests/test_one.py::test_alpha - AssertionError: assert False"

    report = parse_pytest_failures(f"{line}\n{line}\n")

    assert report is not None
    assert len(report.failing_tests) == 1


def test_non_pytest_text_returns_none() -> None:
    report = parse_pytest_failures(
        """hello world
everything is fine
"""
    )

    assert report is None

import definitely_missing_errpilot_dependency


def test_imported_dependency_available() -> None:
    assert definitely_missing_errpilot_dependency is not None

# Raw Failure Prompt

The following command failed. Diagnose the root cause and propose a minimal fix.

## Command

`pytest examples/pytest_fixture_failure`

## Raw Output

```text
============================= test session starts ==============================
platform darwin -- Python 3.13.1, pytest-9.0.3, pluggy-1.6.0
rootdir: <ERRPILOT_ROOT>
configfile: pyproject.toml
collected 1 item

examples/pytest_fixture_failure/test_fixture.py E                        [100%]

==================================== ERRORS ====================================
_________________ ERROR at setup of test_needs_missing_fixture _________________
file <ERRPILOT_ROOT>/examples/pytest_fixture_failure/test_fixture.py, line 1
  def test_needs_missing_fixture(missing_fixture) -> None:
E       fixture 'missing_fixture' not found
>       available fixtures: cache, capfd, capfdbinary, caplog, capsys, capsysbinary, capteesys, doctest_namespace, monkeypatch, pytestconfig, record_property, record_testsuite_property, record_xml_attribute, recwarn, subtests, tmp_path, tmp_path_factory, tmpdir, tmpdir_factory
>       use 'pytest --fixtures [testpath]' for help on them.

<ERRPILOT_ROOT>/examples/pytest_fixture_failure/test_fixture.py:1
=========================== short test summary info ============================
ERROR examples/pytest_fixture_failure/test_fixture.py::test_needs_missing_fixture
=============================== 1 error in 0.00s ===============================
```

# Raw Failure Prompt

The following command failed. Diagnose the root cause and propose a minimal fix.

## Command

`pytest examples/python_assertion_failure`

## Raw Output

```text
============================= test session starts ==============================
platform darwin -- Python 3.13.1, pytest-9.0.3, pluggy-1.6.0
rootdir: <ERRPILOT_ROOT>
configfile: pyproject.toml
collected 1 item

examples/python_assertion_failure/test_example.py F                      [100%]

=================================== FAILURES ===================================
________________________________ test_addition _________________________________

    def test_addition() -> None:
>       assert add(1, 2) == 4
E       assert 3 == 4
E        +  where 3 = add(1, 2)

examples/python_assertion_failure/test_example.py:6: AssertionError
=========================== short test summary info ============================
FAILED examples/python_assertion_failure/test_example.py::test_addition - ass...
============================== 1 failed in 0.01s ===============================
```

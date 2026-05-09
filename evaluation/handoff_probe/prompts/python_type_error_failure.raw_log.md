# Raw Failure Prompt

The following command failed. Diagnose the root cause and propose a minimal fix.

## Command

`pytest examples/python_type_error_failure`

## Raw Output

```text
============================= test session starts ==============================
platform darwin -- Python 3.13.1, pytest-9.0.3, pluggy-1.6.0
rootdir: <ERRPILOT_ROOT>
configfile: pyproject.toml
collected 1 item

examples/python_type_error_failure/test_type_error.py F                  [100%]

=================================== FAILURES ===================================
______________________ test_increment_rejects_wrong_type _______________________

    def test_increment_rejects_wrong_type() -> None:
>       increment("1")

examples/python_type_error_failure/test_type_error.py:6: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

value = '1'

    def increment(value: int) -> int:
>       return value + 1
               ^^^^^^^^^
E       TypeError: can only concatenate str (not "int") to str

examples/python_type_error_failure/test_type_error.py:2: TypeError
=========================== short test summary info ============================
FAILED examples/python_type_error_failure/test_type_error.py::test_increment_rejects_wrong_type
============================== 1 failed in 0.01s ===============================
```

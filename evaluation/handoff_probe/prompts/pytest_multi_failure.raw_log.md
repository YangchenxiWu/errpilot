# Raw Failure Prompt

The following command failed. Diagnose the root cause and propose a minimal fix.

## Command

`pytest examples/pytest_multi_failure`

## Raw Output

```text
============================= test session starts ==============================
platform darwin -- Python 3.13.1, pytest-9.0.3, pluggy-1.6.0
rootdir: <ERRPILOT_ROOT>
configfile: pyproject.toml
collected 2 items

examples/pytest_multi_failure/test_multi_failure.py FF                   [100%]

=================================== FAILURES ===================================
____________________________ test_addition_contract ____________________________

    def test_addition_contract() -> None:
>       assert 1 + 1 == 3
E       assert (1 + 1) == 3

examples/pytest_multi_failure/test_multi_failure.py:2: AssertionError
_____________________________ test_string_contract _____________________________

    def test_string_contract() -> None:
>       assert "errpilot".upper() == "ERR-PILOT"
E       AssertionError: assert 'ERRPILOT' == 'ERR-PILOT'
E         
E         - ERR-PILOT
E         ?    -
E         + ERRPILOT

examples/pytest_multi_failure/test_multi_failure.py:6: AssertionError
=========================== short test summary info ============================
FAILED examples/pytest_multi_failure/test_multi_failure.py::test_addition_contract
FAILED examples/pytest_multi_failure/test_multi_failure.py::test_string_contract
============================== 2 failed in 0.01s ===============================
```

# Raw Failure Prompt

The following command failed. Diagnose the root cause and propose a minimal fix.

## Command

`pytest examples/python_import_failure`

## Raw Output

```text
============================= test session starts ==============================
platform darwin -- Python 3.13.1, pytest-9.0.3, pluggy-1.6.0
rootdir: <ERRPILOT_ROOT>
configfile: pyproject.toml
collected 0 items / 1 error

==================================== ERRORS ====================================
____ ERROR collecting examples/python_import_failure/test_import_failure.py ____
ImportError while importing test module '<ERRPILOT_ROOT>/examples/python_import_failure/test_import_failure.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
examples/python_import_failure/test_import_failure.py:1: in <module>
    import definitely_missing_errpilot_dependency
E   ModuleNotFoundError: No module named 'definitely_missing_errpilot_dependency'
=========================== short test summary info ============================
ERROR examples/python_import_failure/test_import_failure.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.05s ===============================
```

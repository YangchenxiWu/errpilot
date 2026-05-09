# Raw Failure Prompt

The following command failed. Diagnose the root cause and propose a minimal fix.

## Command

`python3 examples/python_traceback_failure/fail.py`

## Raw Output

```text
Traceback (most recent call last):
  File "<ERRPILOT_ROOT>/examples/python_traceback_failure/fail.py", line 13, in <module>
    main()
    ~~~~^^
  File "<ERRPILOT_ROOT>/examples/python_traceback_failure/fail.py", line 9, in main
    parse_retry_count("-1")
    ~~~~~~~~~~~~~~~~~^^^^^^
  File "<ERRPILOT_ROOT>/examples/python_traceback_failure/fail.py", line 4, in parse_retry_count
    raise ValueError("retry count must be non-negative")
ValueError: retry count must be non-negative
```

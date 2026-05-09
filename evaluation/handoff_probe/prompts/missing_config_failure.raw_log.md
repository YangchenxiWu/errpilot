# Raw Failure Prompt

The following command failed. Diagnose the root cause and propose a minimal fix.

## Command

`pytest examples/missing_config_failure`

## Raw Output

```text
============================= test session starts ==============================
platform darwin -- Python 3.13.1, pytest-9.0.3, pluggy-1.6.0
rootdir: <ERRPILOT_ROOT>
configfile: pyproject.toml
collected 1 item

examples/missing_config_failure/test_missing_config.py F                 [100%]

=================================== FAILURES ===================================
_________________________ test_required_config_exists __________________________

    def read_required_config() -> str:
        config_path = Path(__file__).with_name("required_config.toml")
        try:
>           return config_path.read_text(encoding="utf-8")
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

examples/missing_config_failure/test_missing_config.py:7: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/pathlib/_local.py:546: in read_text
    return PathBase.read_text(self, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/pathlib/_abc.py:632: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors, newline=newline) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = PosixPath('<ERRPILOT_ROOT>/examples/missing_config_failure/required_config.toml')
mode = 'r', buffering = -1, encoding = 'utf-8', errors = None, newline = None

    def open(self, mode='r', buffering=-1, encoding=None,
             errors=None, newline=None):
        """
        Open the file pointed to by this path and return a file object, as
        the built-in open() function does.
        """
        if "b" not in mode:
            encoding = io.text_encoding(encoding)
>       return io.open(self, mode, buffering, encoding, errors, newline)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       FileNotFoundError: [Errno 2] No such file or directory: '<ERRPILOT_ROOT>/examples/missing_config_failure/required_config.toml'

/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/pathlib/_local.py:537: FileNotFoundError

The above exception was the direct cause of the following exception:

    def test_required_config_exists() -> None:
>       assert read_required_config()
               ^^^^^^^^^^^^^^^^^^^^^^

examples/missing_config_failure/test_missing_config.py:13: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    def read_required_config() -> str:
        config_path = Path(__file__).with_name("required_config.toml")
        try:
            return config_path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
>           raise FileNotFoundError("required config file not found: required_config.toml") from exc
E           FileNotFoundError: required config file not found: required_config.toml

examples/missing_config_failure/test_missing_config.py:9: FileNotFoundError
=========================== short test summary info ============================
FAILED examples/missing_config_failure/test_missing_config.py::test_required_config_exists
============================== 1 failed in 0.02s ===============================
```

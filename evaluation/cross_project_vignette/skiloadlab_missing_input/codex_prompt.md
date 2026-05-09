# ErrPilot Handoff: codex

## Failure Summary

- command: `<SKILOADLAB_ROOT>/.venv/bin/python -m skiloadlab.cli.combine --in /tmp/skiloadlab_missing_input.csv --out /tmp/skiloadlab_probe/out.csv --report /tmp/skiloadlab_probe/report.json --alpha 0.5`
- exit_code: `1`
- python_traceback: `FileNotFoundError: [Errno 2] No such file or directory: '/tmp/skiloadlab_missing_input.csv'`
- triage_severity: `4`
- triage_recommended_route: `manual_plus_agent_investigation`

## Triage Result

- severity: `4`
- confidence: `0.7`
- recommended_route: `manual_plus_agent_investigation`
- requires_human_approval: `True`
- reason: Dependency, configuration, build, CI, or external-tool failure detected.

## Failing Tests

No failing tests detected.

## Source Contexts

### Source Context 1

- file: `skiloadlab/cli/combine.py`
- focus_line: `6`
- role: `traceback_frame`
- lines: `1-6`

```text
from skiloadlab.core_model import main

__all__ = ["main"]

if __name__ == "__main__":
    main()
```

### Source Context 2

- file: `skiloadlab/core_model.py`
- focus_line: `91`
- role: `traceback_frame`
- lines: `81-101`

```text
    ap.add_argument("--out", required=True, help="Output CSV")
    ap.add_argument("--report", required=True, help="Output report JSON")
    ap.add_argument(
        "--alpha",
        type=float,
        default=0.5,
        help="Weight for internal component (0..1)",
    )
    args = ap.parse_args()

    report = run_combined_load(
        inp=Path(args.inp),
        outp=Path(args.out),
        rep=Path(args.report),
        alpha=float(args.alpha),
    )

    print(f"[OK] Saved: {report['output_csv']}")
    print(f"[OK] Report: {report['output_report']}")
    print(f"internal_used_for_combined = {report['internal_used_for_combined']}")
    print(f"corr(combined, z_internal) = {report['corr_comb_internal']}")
```

### Source Context 3

- file: `skiloadlab/core_model.py`
- focus_line: `37`
- role: `traceback_frame`
- lines: `27-47`

```text
    m = a.notna() & b.notna()
    if m.sum() < 3:
        return float("nan")
    return float(np.corrcoef(a[m], b[m])[0, 1])


def run_combined_load(inp: Path, outp: Path, rep: Path, alpha: float) -> dict:
    if not (0.0 <= alpha <= 1.0):
        raise ValueError("alpha must be within [0, 1].")

    df = pd.read_csv(inp)

    # Demo / public run-level mode
    if ("z_mech" in df.columns) and ("z_internal" in df.columns):
        df["z_mech"] = pd.to_numeric(df["z_mech"], errors="coerce")
        df["z_internal"] = pd.to_numeric(df["z_internal"], errors="coerce")

        df["combined_load_v2"] = alpha * df["z_internal"] + (1.0 - alpha) * df["z_mech"]

        corr_comb_internal = corr_safe(df["combined_load_v2"], df["z_internal"])
        corr_comb_mech = corr_safe(df["combined_load_v2"], df["z_mech"])
```

### Source Context 4

- file: `.venv/lib/python3.13/site-packages/pandas/io/parsers/readers.py`
- focus_line: `873`
- role: `traceback_frame`
- lines: `863-883`

```text
        delimiter,
        engine,
        sep,
        on_bad_lines,
        names,
        defaults={"delimiter": ","},
        dtype_backend=dtype_backend,
    )
    kwds.update(kwds_defaults)

    return _read(filepath_or_buffer, kwds)


@overload
def read_table(
    filepath_or_buffer: FilePath | ReadCsvBuffer[bytes] | ReadCsvBuffer[str],
    *,
    iterator: Literal[True],
    chunksize: int | None = ...,
    **kwds: Unpack[_read_shared[HashableT]],
) -> TextFileReader: ...
```

### Source Context 5

- file: `.venv/lib/python3.13/site-packages/pandas/io/parsers/readers.py`
- focus_line: `300`
- role: `traceback_frame`
- lines: `290-310`

```text
            )
    else:
        chunksize = validate_integer("chunksize", chunksize, 1)

    nrows = kwds.get("nrows", None)

    # Check for duplicates in names.
    _validate_names(kwds.get("names", None))

    # Create the parser.
    parser = TextFileReader(filepath_or_buffer, **kwds)

    if chunksize or iterator:
        return parser

    with parser:
        return parser.read(nrows)


@overload
def read_csv(
```

### Source Context 6

- file: `.venv/lib/python3.13/site-packages/pandas/io/parsers/readers.py`
- focus_line: `1645`
- role: `traceback_frame`
- lines: `1635-1655`

```text
        self.chunksize = options.pop("chunksize", None)
        self.nrows = options.pop("nrows", None)

        self._check_file_or_buffer(f, engine)
        self.options, self.engine = self._clean_options(options, engine)

        if "has_index_names" in kwds:
            self.options["has_index_names"] = kwds["has_index_names"]

        self.handles: IOHandles | None = None
        self._engine = self._make_engine(f, self.engine)

    def close(self) -> None:
        if self.handles is not None:
            self.handles.close()
        self._engine.close()

    def _get_options_with_defaults(self, engine: CSVEngine) -> dict[str, Any]:
        kwds = self.orig_options

        options = {}
```

### Source Context 7

- file: `.venv/lib/python3.13/site-packages/pandas/io/parsers/readers.py`
- focus_line: `1904`
- role: `traceback_frame`
- lines: `1894-1914`

```text
            elif (
                engine == "c"
                and self.options.get("encoding", "utf-8") == "utf-8"
                and isinstance(stringify_path(f), str)
            ):
                # c engine can decode utf-8 bytes, adding TextIOWrapper makes
                # the c-engine especially for memory_map=True far slower
                is_text = False
                if "b" not in mode:
                    mode += "b"
            self.handles = get_handle(
                f,
                mode,
                encoding=self.options.get("encoding", None),
                compression=self.options.get("compression", None),
                memory_map=self.options.get("memory_map", False),
                is_text=is_text,
                errors=self.options.get("encoding_errors", "strict"),
                storage_options=self.options.get("storage_options", None),
            )
            assert self.handles is not None
```

### Source Context 8

- file: `.venv/lib/python3.13/site-packages/pandas/io/common.py`
- focus_line: `926`
- role: `traceback_frame`
- lines: `916-936`

```text
            raise ValueError(msg)

        assert not isinstance(handle, str)
        handles.append(handle)

    elif isinstance(handle, str):
        # Check whether the filename is to be opened in binary mode.
        # Binary mode does not support 'encoding' and 'newline'.
        if ioargs.encoding and "b" not in ioargs.mode:
            # Encoding
            handle = open(
                handle,
                ioargs.mode,
                encoding=ioargs.encoding,
                errors=errors,
                newline="",
            )
        else:
            # Binary mode
            handle = open(handle, ioargs.mode)
        handles.append(handle)
```


## Relevant Log Excerpts

### stderr_excerpt

```text
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "<SKILOADLAB_ROOT>/skiloadlab/cli/combine.py", line 6, in <module>
    main()
    ~~~~^^
  File "<SKILOADLAB_ROOT>/skiloadlab/core_model.py", line 91, in main
    report = run_combined_load(
        inp=Path(args.inp),
    ...<2 lines>...
        alpha=float(args.alpha),
    )
  File "<SKILOADLAB_ROOT>/skiloadlab/core_model.py", line 37, in run_combined_load
    df = pd.read_csv(inp)
  File "<SKILOADLAB_ROOT>/.venv/lib/python3.13/site-packages/pandas/io/parsers/readers.py", line 873, in read_csv
    return _read(filepath_or_buffer, kwds)
  File "<SKILOADLAB_ROOT>/.venv/lib/python3.13/site-packages/pandas/io/parsers/readers.py", line 300, in _read
    parser = TextFileReader(filepath_or_buffer, **kwds)
  File "<SKILOADLAB_ROOT>/.venv/lib/python3.13/site-packages/pandas/io/parsers/readers.py", line 1645, in __init__
    self._engine = self._make_engine(f, self.engine)
                   ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^
  File "<SKILOADLAB_ROOT>/.venv/lib/python3.13/site-packages/pandas/io/parsers/readers.py", line 1904, in _make_engine
    self.handles = get_handle(
                   ~~~~~~~~~~^
        f,
        ^^
    ...<6 lines>...
        storage_options=self.options.get("storage_options", None),
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "<SKILOADLAB_ROOT>/.venv/lib/python3.13/site-packages/pandas/io/common.py", line 926, in get_handle
    handle = open(
        handle,
    ...<3 lines>...
        newline="",
    )
FileNotFoundError: [Errno 2] No such file or directory: '/tmp/skiloadlab_missing_input.csv'
```


## Verification Command

`<SKILOADLAB_ROOT>/.venv/bin/python -m skiloadlab.cli.combine --in /tmp/skiloadlab_missing_input.csv --out /tmp/skiloadlab_probe/out.csv --report /tmp/skiloadlab_probe/report.json --alpha 0.5`

## Constraints

- Keep changes minimal.
- Do not modify unrelated files.
- Preserve public behavior unless the failure requires changing it.
- Use the source contexts and failing tests as primary evidence.
- Ask for human approval before any risky or broad change.

## Do Not Do

- Do not run destructive commands.
- Do not read or expose secrets, tokens, credentials, .env files, private keys, or certificates.
- Do not claim success without running the verification command.
- Do not replace this with a broad rewrite.

## Target Guidance

Use this as a focused debugging task. Produce a minimal patch and report verification results.

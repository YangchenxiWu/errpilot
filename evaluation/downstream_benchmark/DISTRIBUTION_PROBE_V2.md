# Installed distribution probe V2

Status: `DISTRIBUTION_PROBE_V2_FROZEN` after the validation recorded in the
Batch-01 identity-completion supplement. Scope: installed-distribution
observation only; frozen build recipes and screening policy are unchanged.

## A. Root cause

`importlib.metadata` entered the Python standard library in Python 3.8.
The V1.1 materializer's unconditional import cannot run under the frozen
Python 3.6/3.7 population. The observed keras::28 Python 3.7.3 exception is
a probe implementation limitation, not a dependency recipe, subject source,
oracle, or eligibility result.

## B. Observed semantic object

The manifest is the installed environment's ordered canonical list of
`[name, version]` distribution pairs. The strings are observed values. The
manifest is neither inferred from requirements nor a comparison metric across
cases; its SHA-256 identifies one environment's observed inventory.

## C-E. Deterministic backend selection

The observed Python patch version selects exactly one backend:

| Python version | Backend | In-container command |
| --- | --- | --- |
| >= 3.8 | `STDLIB_IMPORTLIB_METADATA` | `python -c` using `importlib.metadata.distributions()` |
| < 3.8 | `PIP_LIST_JSON` | `python -m pip list --format=json` |

No alternate backend is tried after failure or an inconvenient inventory.
The Python >=3.8 implementation enumerates distribution metadata, then sends
the JSON list to the host for validation and canonicalization. The Python
<3.8 implementation sends pip's JSON list to that same host-side path. Neither
backend imports subject code. `importlib_metadata` is not installed as a
compatibility workaround.

## F. Canonical manifest

Probe stdout must be valid UTF-8 JSON with a top-level list, no duplicate
object keys, and no non-JSON constants. Each record must contain non-empty
string `name` and `version` values. Host-side code orders pairs by distribution
name after case folding and normalizing runs of `-`, `_`, or `.` to `-`, then
by observed version, then by observed name to settle exact ties. The output
retains the observed name and version strings. The benchmark's canonical JSON
serializer emits sorted keys, compact separators, UTF-8, and one final LF;
SHA-256 is calculated over those exact bytes.

## G-H. Probe isolation and failure classification

Each distribution probe uses the immutable image ID with `docker run --rm`,
`--pull=never`, `--platform=linux/amd64`, `--network=none`, `--read-only`,
and an ephemeral `/tmp` mount. It performs no installation or image mutation.
Exit code 0 and a valid manifest are required. A failing, malformed, or
incomplete required backend yields `BLOCKED_RUNTIME_IDENTITY`. The materializer
stores raw distribution stdout and stderr separately, their hashes, the backend,
the V2 probe version, and the canonical manifest. System-package observation
remains an independent gate.

## I. Relation to environment identity V1

`SCREENING_ENVIRONMENT_IDENTITY_V1` field order remains frozen. The
`installed_distribution_manifest_sha256` field now hashes the V2 canonical
manifest for future materializations. Backend and raw-probe evidence live in
the materializer attempt record and probe files, outside that V1 identity
object. Previous successful Batch-01 identity bytes and hashes are unchanged.

## J-K. Batch-01 history and identity completion

The original Batch-01 CSV and report are historical evidence. keras::28's
original status remains `BLOCKED_RUNTIME_IDENTITY`. A separate supplement can
record `POST_BUILD_IDENTITY_COMPLETION` only after the exact original image ID
and saved RootFS layers match, the original single build exited 0, Python is
still 3.7.3, and every identity observation passes. This operation reuses the
original immutable image; it cannot invoke `docker build`, install packages,
or edit the external original attempt. Its successful status is expressed as
`identity_completion_status = COMPLETED` and
`effective_environment_status = MATERIALIZED`, without retroactively changing
the original transaction. A missing exact image is
`IDENTITY_COMPLETION_IMAGE_UNAVAILABLE` and leaves the environment blocked.

## L. Zero-oracle boundary

This probe and its completion do not execute subject imports, tests, oracles,
3/3 screening, eligibility, repair, ErrPilot, or a model/API. A materialized
environment alone is not an eligible case.

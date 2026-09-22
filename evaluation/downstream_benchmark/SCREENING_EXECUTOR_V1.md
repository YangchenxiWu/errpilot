# BugsInPy Production Screening Executor v1

- Implementation status: `BUGSINPY_SCREENING_EXECUTOR_V1_FROZEN`
- Preparation result: 40/40 full buggy and fixed commit identities resolved
- Screening readiness: 34 plan-ready, 6 oracle-plan unresolved
- Eligibility executions performed: 0
- Eligibility conclusions: none

This document describes the benchmark-local screening executor implemented in
`screening/executor.py`.  It implements preparation and the mechanically gated
future 3/3 runner.  It does not authorize screening and does not change the
semantics of `PROTOCOL.md`, `RUN_SPEC_V1.md`, or `SCREENING_SPEC_V1.md`.

## 1. Architecture

The executor has six bounded components:

1. **Authority and input validation.** It verifies the frozen protocol, run-spec,
   and candidate-universe hashes; requires header-only `cases_manifest.csv` and
   `exclusions.csv`; verifies the pinned, detached, clean BugsInPy checkout; and
   checks the 40-row order against `SCREENING_SPEC_V1.md`.
2. **Acquisition and identity resolution.** It maintains one external bare mirror
   per subject project and resolves every declared revision against the complete
   local object set. Short identifiers must resolve to exactly one commit object.
3. **Oracle preservation and analysis.** It stores the exact `run_test.sh` bytes,
   hashes them, and statically derives the command only when the script contains
   exactly one recognized, non-control-flow test command.
4. **Protected-manifest preparation.** It combines the declared test file with
   directly identifiable test paths from the oracle. It records raw and effective
   SHA-256 identities for buggy and fixed states.
5. **Environment planning.** It hashes BugsInPy metadata, requirements, setup, and
   relevant framework inputs and records every immutable field that a later
   environment build must supply. It does not build or validate an environment.
6. **Gated execution and evidence.** A separately authorized execution creates a
   fresh checkout for each ordinal, follows the fixed 3+3 schedule, writes raw
   evidence and checkpoints, and classifies infrastructure, interruption, and
   reproducibility states separately.

There is no repair-agent adapter, ErrPilot invocation, model/API client, pilot
entry point, or path for populating final repair results.

## 2. Preparation and execution modes

The CLI has two subcommands:

- `prepare` performs static validation, acquisition, identity resolution, and
  plan/evidence generation. It cannot run an oracle.
- `execute` is the future oracle path. It is not entered by a bare invocation or
  by `prepare`.

A bare invocation prints help and exits nonzero. The preparation transaction used
`prepare`; it did not use `execute`.

## 3. Exact authority gate for future oracle execution

Execution requires all of the following:

1. the explicit `execute` subcommand;
2. the exact authority value
   `BUGSINPY_SCREENING_3X3_EXECUTION_AUTHORIZED_V1` supplied through the required
   `--authorization` argument;
3. a unique, syntactically valid execution ID;
4. a screening-ready case plan with a valid deterministic plan hash;
5. a resolved single-command oracle plan;
6. a complete external `environment_identity.json` bound to the case and plan;
7. an explicit recorded rerun reason if any prior attempt evidence exists.

This token is a mechanical guard, not human authorization by itself. A future
human-PI transaction must still authorize real oracle execution. The present
transaction provides no such authorization.

## 4. External state and evidence layout

All large or mutable screening state remains outside the ErrPilot repository:

```text
/Users/wuyangchenxi/errpilot-benchmark-work/
  bugsinpy/                         pinned framework and metadata
  subject_repositories/<project>.git
  screening_workspaces/<case>/
    SCREENING_ONLY_DO_NOT_USE_FOR_REPAIR.json
    screening_checkout/
      SCREENING_ONLY_DO_NOT_USE_FOR_REPAIR.json
    preparation/
      acquisition_evidence.json
      acquisition_events/<timestamp>.json
      environment_plan.json
      execution_plan.json
      protected_manifest.json
      oracle/run_test.sh
    environment/                    absent until a separately governed build
  screening_evidence/<case>/<execution-id>/
    checkpoint.json
    runs/<ordinal>/                 future execution only
      stdout.raw
      stderr.raw
      workspace/
```

The content-addressed acquisition identity is deterministic; timestamped
verification events are append-only. Acquisition/setup preparation evidence and
future oracle evidence are separate.
The only committed row-level output is the compact
`screening_execution_plan.csv` ledger.

## 5. Subject isolation and fix-leakage controls

The 15 project repositories are external bare mirrors. Per-case directories carry
an explicit marker declaring them screening-only and unusable as repair
workspaces. A future execution creates a new checkout for every one of the six
ordinals; a screening checkout is never handed to a repair agent.

The implementation permits only object identity and blob-hash operations needed
for preparation. Its Git wrapper rejects `git log`, `git show`, and `git diff`.
Preparation does not read `bug_patch.txt`, an official fix diff, a fix-revealing
commit message, or a human repair explanation. Fixed subject blobs are accessed
only for mechanically declared protected-test identities.

BugsInPy's checkout framework copies each declared fixed-version test file into
the buggy checkout before running the oracle. The protected manifest records this
as `buggy_test_injection_from_fixed`; a future runner injects only those declared,
hash-pinned benchmark-owned test bytes. It does not copy non-test repair content.

## 6. Oracle preservation and current unresolved cases

Every candidate's exact `run_test.sh` bytes are stored read-only in its external
preparation directory and identified by SHA-256. The original command text is not
normalized. The oracle working directory is the subject repository root.

Six cases contain multiple substantive commands and are therefore intentionally
unresolved rather than combined or simplified:

| Initial order | Case | Substantive commands |
| ---: | --- | ---: |
| 10 | `keras::28` | 2 |
| 13 | `scrapy::19` | 4 |
| 17 | `scrapy::14` | 2 |
| 21 | `tornado::6` | 2 |
| 27 | `ansible::2` | 2 |
| 38 | `fastapi::11` | 6 |

These rows have `screening_ready=false`. Resolving them requires a separately
approved, versioned rule for representing a multi-command oracle; this executor
does not invent one.

## 7. Protected manifests

Protected paths are the union of:

- semicolon-separated paths in the declared BugsInPy `test_file`; and
- `.py` test paths mechanically parsed from the preserved oracle command(s).

Paths are canonicalized as safe repository-relative POSIX paths and sorted. Each
manifest records its source, the raw buggy-checkout hash when present, the fixed
hash, the effective buggy hash after BugsInPy-declared test injection, and whether
injection is required. All 40 protected manifests are resolved. No broader
subjective test-path guesses are included.

## 8. Environment identity and preparation status

All 40 rows have `environment_plan_status=PLAN_FROZEN_BUILD_REQUIRED`. Each plan
records the declared Python version and identities for `requirements.txt`,
`setup.sh`, `bug.info`, `project.info`, `run_test.sh`, `bugsinpy-test`, and
`bugsinpy-compile`. Setup scripts are scanned as data for direct test invocation;
none was executed.

Before a case can execute, a separately governed build must populate and bind:

- platform identity;
- Python artifact and executable SHA-256;
- dependency-input identity;
- installed-distribution manifest identity;
- system-dependency manifest identity;
- setup-evidence identity;
- environment-tree manifest identity; and
- the case-isolated environment root;
- the case-isolated environment binary directory.

The materialized environment must be marked content-addressed and have no write
permission bits. Each ordinal receives fresh `HOME`, `TMPDIR`, and
`XDG_CACHE_HOME` directories, and bytecode writes are disabled. The environment
tree hash is checked before execution and again after every oracle ordinal.

Metadata existence is not claimed as a reproducible environment. No dependency
was installed and no environment was constructed in this transaction.

## 9. Fixed ordering, evidence, and no-retry semantics

The future schedule is immutable:

```text
BUGGY 1, BUGGY 2, BUGGY 3, FIXED 1, FIXED 2, FIXED 3
```

There is no early-stop branch. Oracle exit codes do not alter the remaining
schedule. Every completed run records the exact command, cwd, bound environment
identity, timestamps, wall time, exit code, revision SHA, ordinal, raw stdout and
stderr, their hashes, and protected-integrity result. Combined stream ordering is
marked unavailable rather than fabricated.

An existing execution ID is never overwritten. If prior evidence exists, a later
attempt requires an explicit recorded rerun reason. Infrastructure failures remain
`INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY`; they are not converted into oracle failure
or silently retried.

## 10. Checkpoint and interruption semantics

The executor writes a checkpoint before the first run with all six schedule slots
pending. It updates the checkpoint after each recorded ordinal. A normal finish is
classified only after all six records exist in exact order.

An interruption writes `state=INTERRUPTED` and
`classification=INTERRUPTED_NOT_ELIGIBILITY`. Missing records produce
`INCOMPLETE_NOT_ELIGIBILITY`. Neither state can be interpreted as eligibility.
Raw artifacts and the last checkpoint remain in the unique evidence directory for
human inspection; the executor does not synthesize missing outcomes.

## 11. Meaning of the committed readiness ledger

`screening_ready=true` means only that immutable subject identities, the static
oracle plan, protected manifest, and environment-construction plan are resolved
well enough to attempt a later environment build and screening transaction. It
does not mean the environment has been built, any oracle has run, or the case is
eligible.

This freeze establishes production screening machinery and preparation evidence
only. It does not establish any candidate eligibility, pilot result, repair
result, ErrPilot effectiveness result, or scientific validation claim.

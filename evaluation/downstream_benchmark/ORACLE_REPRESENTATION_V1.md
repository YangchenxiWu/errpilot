# BugsInPy ordered oracle representation v1

- Status: `COMPOSITE_ORACLE_SEMANTICS_V1_FROZEN`
- Implementation target: `SCREENING_EXECUTOR_V1_1`
- Executor status on validated commit: `BUGSINPY_SCREENING_EXECUTOR_V1_1_FROZEN`
- Authority: Human PI transaction instruction dated 2026-09-22
- Scope: versioned supplement to `SCREENING_SPEC_V1.md`; no rewrite of that specification
- Execution state: no real oracle execution authorized or performed
- Gate: `PRE_EXECUTION_TIMEOUT_GATE_REQUIRED`

This supplement changes only static oracle representation and the mechanics of a
future screening trial. `PROTOCOL.md`, `RUN_SPEC_V1.md`, candidate selection,
eligibility, fix-leakage, sampling, pilot, and final rules retain their authority.
It supersedes `SCREENING_EXECUTOR_V1` only for composite-oracle representation
and future execution mechanics.
The frozen `run_test.sh` bytes and SHA-256 are the source for command membership
and order. A trial is the entire ordered list of its recognized substantive test
commands. N=1 is the single-command case of the same model. The authoritative
plan field is `oracle_commands`; `oracle_command_count` MUST equal its length and
be at least one. `oracle_command` is readability-only and MUST NOT drive execution.
`screening_ready` denotes static preparation readiness, not execution authority;
the CSV separately records `PRE_EXECUTION_TIMEOUT_GATE_REQUIRED` for every row.

## Static resolution

Each substantive line MUST independently pass the versioned recognized test
command parser. The parser accepts literal whitespace-delimited `pytest`,
`py.test`, `python -m pytest`, `python3 -m pytest`, `python -m unittest`, or
`python3 -m unittest` argument vectors. The executor runs the parsed argv
directly; it never invokes a shell for an oracle. Embedded apostrophes in literal
test selectors remain literal. It preserves each accepted line's UTF-8 bytes as
command text, including trailing spaces, and its exact position. It MUST NOT
sort, combine, deduplicate, normalize, or reorder commands. The original whole
script bytes and hash remain preserved independently.

Any substantive line with shell control flow, pipe, redirection, environment
assignment, expansion, unsupported executable, interactive or network/GUI
command, or ambiguous syntax leaves the entire oracle unresolved. No arbitrary
shell script is admitted. A safe N-command plan has status
`RESOLVED_ORDERED_COMMANDS`; an unsafe one has
`UNRESOLVED_UNSAFE_OR_UNRECOGNIZED_COMMAND_V1_1` with its blocking reason.

## Trial and evidence

Each of the six BUGGY 1–3, then FIXED 1–3 trials starts with a freshly restored
revision workspace. All subcommands within one trial use that same workspace,
frozen environment identity, oracle cwd, and trial-owned HOME, TMPDIR, and cache.
No mutable state may carry between trials. Every subcommand executes exactly once
in script order after an earlier nonzero exit. Infrastructure failure that makes
continuation impossible is recorded as infrastructure failure, never oracle FAIL.

For each subcommand the executor records a stable one-based ordinal, exact text,
command SHA-256, cwd, start/end timestamps, elapsed time, exit code, raw stdout
and stderr artifacts and SHA-256 hashes, and protected-integrity status. The
trial records the ordered command vector, ordered exit-code vector, ordered
subcommand artifact references, composite classification, and SHA-256 of
canonical JSON trial evidence without the hash field. Missing evidence or failed
protected integrity invalidates the trial. Output prose never determines result.

`COMMAND_PASS` means exit code 0; `COMMAND_FAIL` means a nonzero exit code.
`TRIAL_PASS` means every one of N valid completed commands passed. `TRIAL_FAIL`
means all N completed as valid oracle executions and at least one failed. An
interrupted, invalid, or infrastructure-failed command cannot create `TRIAL_FAIL`.
The six-trial eligibility pattern remains BUGGY = FAIL/FAIL/FAIL and FIXED =
PASS/PASS/PASS. N subcommands still contribute exactly one observation per trial.
For illustration only, `[1, 0, 0, 0]` is one FAIL trial and `[0, 0, 0, 0]` one
PASS trial; neither vector is benchmark outcome evidence.

## BugsInPy provenance and boundaries

Pinned BugsInPy commit `11c5f1eea954a42132cfd06bf257766a7963e0fd`
`framework/bin/bugsinpy-test` reads `run_test.sh` into an ordered command array
and iterates over every entry. Its recorded SHA-256 is
`439edaa83ee1f518d70d7c5f195568e0217860e7be38a062188b5cf991078696`.
ErrPilot instead classifies from process exit codes; BugsInPy's output-text
heuristics and `bugsinpy-test` are not used for eligibility classification.

This amendment authorizes no `bug_patch.txt`, fixed repair diff, repair-revealing
history, repair explanation, model, ErrPilot, or repair-agent exposure or run.
It authorizes no subject dependency installation, environment materialization,
or oracle execution. Timeout semantics remain undecided. Even an otherwise
complete plan MUST be blocked by `PRE_EXECUTION_TIMEOUT_GATE_REQUIRED` until a
later Human-PI-authorized transaction freezes timeout semantics and explicitly
authorizes execution.

The committed CSV is deterministically regenerated from hash-verified preserved
v1 preparation evidence and pinned `run_test.sh` bytes. The external per-case
preparation JSON is not rewritten in this transaction. It must be reissued as
v1.1 and bound to a future immutable environment identity before any future
execution, in addition to resolving the timeout and authorization gates.

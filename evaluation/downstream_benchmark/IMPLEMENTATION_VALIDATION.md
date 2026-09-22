# Synthetic Harness Implementation and Validation

Status: `BENCHMARK_HARNESS_SYNTHETICALLY_VALIDATED` only.

The implementation in `harness/` exercises the frozen benchmark mechanics with
deterministic local fixtures and Python standard-library code. The case loader
requires `execution_mode=synthetic_validation` and
`sample_role=synthetic_fixture`; the runner rejects any adapter not explicitly
marked synthetic-only. There is no live Codex adapter, ErrPilot invocation,
BugsInPy integration, network client, container provisioner, or production
benchmark entry point.

Implemented mechanics:

- strict machine-readable case and result identities, with JSON schemas;
- byte-preserving length-framed RAW and ERRPILOT payloads containing the same
  frozen task-instruction bytes;
- paired source-execution provenance validation before workspace creation;
- independent fresh workspace copies prepared before either condition starts;
- harness-level workspace path isolation for deterministic fake adapters;
- a default repair timeout constant of exactly 1,200 seconds, with shorter
  injected values accepted only by this synthetic-only runner;
- protected path, content, type, mode, recursive directory-inventory, runtime
  replacement, deletion, and observable rename checks;
- runner-controlled subprocess execution of a local synthetic oracle;
- the seven frozen outcome classes and their precedence;
- separate raw and derived evidence, canonical result hashing, and artifact
  checksums; and
- explicit `NA` values when synthetic traces cannot establish instrumentation
  or live Codex/model identity.

Validation command:

```text
python3 -m unittest discover -s evaluation/downstream_benchmark/tests -v
```

The tests cover success, oracle failure, protected-test mutation overriding a
passing oracle, timeout without retry, agent error, infrastructure error,
pre-run case invalidation, same-execution mismatch rejection, and ordinary
workspace-interface contamination attempts. The path boundary is a harness
interface control, not an OS-level adversarial sandbox. A POSIX wall-clock alarm
interrupts an over-budget synthetic adapter callback. Live Codex process-tree
termination remains intentionally unimplemented.

No BugsInPy repair result exists. No live Codex result exists. No candidate,
pilot, or final benchmark session has run. A synthetic PASS does not establish
ErrPilot effectiveness, benchmark readiness, scientific validity, or completed
evaluation. Every non-synthetic pre-run gate in `RUN_SPEC_V1.md` remains open
and requires a separately authorized transaction.

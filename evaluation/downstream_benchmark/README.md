# Downstream Repair Benchmark

This directory is scaffolding for a paired BugsInPy benchmark that will test
whether an ErrPilot-generated structured handoff improves a downstream Codex
agent's objective repair success relative to raw failure output. The planned
benchmark is limited to Python-centric CLI/pytest failures, 24 eligible final
cases, one repair agent, and the frozen protocol in `PROTOCOL.md`.

This is not the existing handoff-completeness evaluation. The existing
`evaluation/handoff_probe/` and `scripts/evaluate_handoff_probe.py` score whether
RAW and ErrPilot artifacts contain specified evidence and guardrails; they do
not execute repairs or measure bug-fixing success. This directory instead
defines a future downstream repair experiment whose primary outcome is passage
of a preregistered bug-exposing test after Codex attempts a repair.

It is also not an ErrPilot autonomous-repair feature, an architectural
extension, a multi-model comparison, a general-language benchmark, or a
CI/supply-chain evaluation. Nothing here authorizes changing ErrPilot, tests,
existing evaluation artifacts, README/paper claims, or running BugsInPy or
Codex experiments.

Contents:

- `PROTOCOL.md`: frozen scientific and operational constraints.
- `RUN_SPEC_V1.md`: versioned, human-authorized operational decisions and
  pre-run gates; it does not authorize execution.
- `cases_manifest.csv`: header-only case registry awaiting eligibility work.
- `exclusions.csv`: header-only exclusion ledger awaiting eligibility work.
- `RUNNER_DESIGN.md`: production-runner design; no production runner is implemented.
- `harness/`: standard-library, synthetic-only mechanics and machine-readable
  case/result schemas. It refuses non-synthetic cases and has no live adapter.
- `fixtures/`: deterministic local fixture content that is not a benchmark case.
- `tests/`: synthetic validation of payload, provenance, isolation, timeout,
  protected-integrity, oracle, evidence, and taxonomy mechanics.
- `IMPLEMENTATION_VALIDATION.md`: implemented boundary, validation command, and
  unresolved non-synthetic gates.

Before any pilot, all incomplete per-case and runner gates in `RUN_SPEC_V1.md`
require evidence, and the human PI must provide separate execution
authorization.

# Positioning Vs Existing Tools

ErrPilot is not a repair backend. It is a failure intake and handoff layer
before human or downstream AI-assisted debugging. It captures explicitly
wrapped failed commands and transforms them into structured, auditable failure
bundles with bounded source contexts, deterministic local triage, and
reviewable handoff prompts.

## Comparison

| Workflow or tool | Captures command metadata | Preserves raw evidence | Produces structured JSON | Extracts failing tests | Extracts bounded source contexts | Provides local deterministic triage | Generates agent-agnostic handoff artifact | Executes repairs | Auditability |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Plain terminal output | No | No | No | Sometimes, as text | No | No | No | No | Low: transient output, little structure |
| Saved raw logs | Partial, if manually recorded | Yes | No | Sometimes, as text | No | No | No | No | Medium: evidence exists, but diagnosis is manual |
| pytest output | Partial test invocation context | Partial terminal evidence | No | Yes, as pytest text | No | No | No | No | Medium: strong test signal, weak cross-tool structure |
| GitHub Actions logs | Partial CI metadata | Yes | No | Sometimes, as text | No | No | No | No | Medium: durable logs, CI-specific context |
| Issue templates | Manual | Optional manual excerpts | No | Manual | Manual | No | No | No | Medium: structured by humans, inconsistent evidence |
| Direct copy-paste into a coding assistant | Manual | No durable local evidence by default | No | Depends on pasted content | Depends on pasted content | No | No | Maybe, depending on the assistant | Low to medium: prompt contents may be incomplete or hard to reproduce |
| Coding agents / repair backends | Depends on backend | Depends on backend | Depends on backend | Depends on backend | Depends on backend | Depends on backend | No, usually backend-specific | Yes | Varies: often optimized for action rather than intake audit |
| ErrPilot | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No | High: raw logs, metadata, diagnostic fields, triage, and prompts are stored as artifacts |

## Explicit Distinctions

- ErrPilot complements coding agents and repair backends by standardizing the
  failure intake before a human or tool decides what to do next.
- ErrPilot avoids downstream tool lock-in by producing reviewable prompt
  artifacts rather than invoking a specific backend.
- ErrPilot does not execute repair tools.
- ErrPilot does not silently monitor the system; it captures commands only when
  they are explicitly wrapped with `errpilot run -- ...`.
- ErrPilot does not rely on CI-only logs. Its reproducible examples run locally,
  while CI and external cases are represented as documented evaluation context.
- ErrPilot separates raw evidence files from structured diagnostic fields, so a
  reviewer can audit both the original failure output and the derived summary.

## Reviewer Objection Responses

### "This is just a log wrapper."

ErrPilot preserves raw logs, but the contribution is the structured intake layer
around those logs: command metadata, parsed pytest failures, Python traceback
fields, bounded source contexts, deterministic triage, and handoff artifacts.
The raw evidence remains auditable while the diagnostic fields make the failure
portable across reviewers and downstream tools.

### "Only a small evaluation set."

The evaluation is a case-study artifact evaluation, not a benchmark of repair
success. The 6 executable in-repository cases cover distinct parser, triage,
source-context, and handoff behaviors. The 5 documented-only external cases
extend the taxonomy to CI, CLI, shell, and supply-chain failures without making
the default run depend on external repositories or author-specific paths.

### "External cases are documented-only."

That is intentional for reproducibility. External SkiLoadLab and slsa-verifier
cases motivate real-world failure categories, but executing them would require
external repository state, dependencies, CI history, or local path assumptions.
ErrPilot's default evaluation keeps the executable artifact self-contained.

### "The triage rules are simple."

The local triage is deliberately deterministic and auditable. For an artifact
submission, simple transparent rules are easier to inspect than opaque model
calls, and they establish the handoff route without contacting external
services. The goal is stable failure intake, not final diagnosis.

### "Prompt generation is template-based."

Template-based prompt artifacts are a design choice for reproducibility and
review. The generated prompt records the command, failure evidence, source
contexts, triage result, and constraints in a predictable format that can be
used by different downstream tools or a human reviewer.

### "No user study."

The current contribution is an artifact and workflow demonstration. It focuses
on whether a clean clone can reproduce failure capture, bundle generation,
structured extraction, local triage, prompt generation, and evaluation rows.
A user study would measure adoption or task performance, which is separate from
the artifact-readiness claim.

## Paper-Ready Contribution Language

- A failure bundle schema that separates raw command evidence from structured
  diagnostic fields, triage records, and handoff artifacts.
- A bounded source-context construction workflow that attaches relevant code
  windows to parsed failures while avoiding full-file dumping.
- A deterministic local triage and handoff workflow that assigns severity,
  recommends a route, records human-approval requirements, and emits reviewable
  prompt artifacts.
- A reproducible case-study evaluation with 6 executable in-repository cases and
  5 documented-only external cases that motivate broader failure categories.

# Severity Rubric

ErrPilot severity describes debugging complexity and operational risk, not user
importance. The score is intended to guide triage, bundle detail, and approval
prompts.

Local triage is deterministic and rule-based. When rules overlap, ErrPilot uses
the highest matching severity.

## Level 1: Local Environment, Path, Import, or Syntax Issue

Simple failures with obvious, local causes. Examples include syntax errors,
simple path issues, missing commands, empty or unstructured nonzero exits, and
small local invocation problems. The recommended route is `local_suggestion`.

## Level 2: Single Local Test or Traceback Failure

Failures that look localized to one failing pytest assertion or one local Python
traceback such as `ValueError`, `TypeError`, or `AssertionError`. The
recommended route is `codex_or_aider_prompt`.

## Level 3: Cross-File Behavior Failure

Failures involving multiple failing tests or source context from multiple files.
These can indicate shared behavior, interfaces, or state that need a stronger
repository-aware investigation. The recommended route is
`stronger_coding_agent_prompt`.

## Level 4: Dependency, Configuration, CI, Build, or External-Tool Failure

Failures tied to dependency resolution, missing packages, configuration files,
CI or workflow behavior, build failures, shell command availability, required
artifacts, or external tools. The recommended route is
`manual_plus_agent_investigation`.

## Level 5: Secret, Auth, Destructive, or Security-Sensitive Failure

Failures containing secret, token, credential, password, private key, `.env`,
authorization, authentication, destructive command, production deletion, or
security-sensitive signals. The recommended route is `manual_review`.

## Precedence

- S5 overrides all other severities.
- S4 overrides S3, S2, and S1.
- S3 overrides S2 and S1.
- S2 overrides S1.
- When uncertain between two categories, choose the higher severity.

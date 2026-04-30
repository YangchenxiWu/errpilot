# Severity Rubric

ErrPilot severity describes debugging complexity and operational risk, not user
importance. The score is intended to guide triage, bundle detail, and approval
prompts.

## Level 1: Local Syntax or Invocation Issue

Simple failures with obvious, local causes. Examples include missing CLI flags,
syntax errors in recently edited files, import typos, or formatting failures.
These should usually be handled with compact local context.

## Level 2: Small Test or Type Failure

Failures that affect a small number of tests, functions, or type checks. The
investigation scope is still local, but a downstream coding agent may need nearby
source context and the test assertion.

## Level 3: Cross-File Behavior Failure

Failures involving several files, shared interfaces, configuration, or stateful
behavior. The handoff should include a richer bundle and may need a downstream
coding agent that can inspect the repository interactively.

## Level 4: Systemic or Environment-Sensitive Failure

Failures tied to integration behavior, dependency versions, build tooling,
platform differences, networked services, or flaky execution. These require
careful approval before external calls or broad repository inspection.

## Level 5: High-Risk or Ambiguous Failure

Failures with unclear cause, security implications, production data exposure,
large blast radius, or suggested changes that could alter infrastructure,
secrets, authentication, authorization, or persistence. ErrPilot should prepare
handoffs conservatively and require explicit human review.

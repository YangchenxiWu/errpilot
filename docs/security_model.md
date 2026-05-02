# Security Model

ErrPilot is approval-gated by design. It may prepare context and package a
handoff for a downstream coding agent, but it must not silently modify source
code, apply patches, run destructive commands, upload sensitive files, or call
external services without clear user approval.

ErrPilot only executes commands that the user explicitly passes to
`errpilot run -- <argv...>`. It does not run as a background listener, monitor
terminal activity, or scan the system for failures.

## Approval-Gated Actions

The following actions require explicit approval:

- Applying or writing source code changes.
- Running commands that can modify files, services, databases, or remote state.
- Sending error bundles, logs, source excerpts, or repository metadata to
  external AI providers.
- Reading or including files that match sensitive patterns.
- Expanding context beyond the minimal files needed to explain a failure.
- Persisting caches that may contain logs, source excerpts, or environment data.

## Sensitive File Patterns

ErrPilot should treat these patterns as sensitive by default:

```text
.env
.env.*
*.pem
*.key
*.crt
*.p12
*.pfx
id_rsa
id_ed25519
*.kubeconfig
.npmrc
.pypirc
pip.conf
netrc
.netrc
*secret*
*secrets*
*token*
*credential*
credentials.json
service-account*.json
```

Sensitive matches should be excluded, redacted, or shown for explicit approval
before use in an error bundle.

## Prompt Artifacts

Generated handoff prompts are reviewable artifacts. They should use structured
bundle fields, bounded source contexts, failing test summaries, triage results,
and compact log excerpts.

Prompt artifacts should not include secrets, tokens, credentials, `.env` files,
private keys, or certificates. Source contexts are bounded, and sensitive paths
are skipped by the source context collection step.

Human approval is still required before risky changes, broad edits, external
service calls, or any action that can modify source code or remote state.

## Default Posture

The default posture is local-first and read-minimal. ErrPilot should collect the
smallest useful context, prefer local triage where possible, and preserve a
human approval step before any downstream tool receives code, logs, or metadata.

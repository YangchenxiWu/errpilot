# CI side-effect boundary V1

Status: `CI_SIDE_EFFECT_BOUNDARY_V1_FROZEN`.

## Triggering contradiction and interpretation

The initial-40 adjudication transaction prohibited every Docker build and every
ErrPilot invocation while also requiring a push and post-push CI verification.
The repository already had a push-triggered `.github/workflows/ci.yml` that
builds and runs a repository artifact Docker image, runs repository tests and
evaluation scripts, and performs a minimal ErrPilot CLI artifact demo. The
literal prohibition therefore conflicted with the required publication step.

The Human PI accepts the normative initial-40 adjudication and interprets its
execution boundary as `ZERO_BENCHMARK_RESEARCH_EXECUTION`. Automatic runs of the
pre-existing workflow after a push are classified as
`CI_TRIGGERED_REPOSITORY_VERIFICATION` only when all of these conditions hold:

1. Publication or push automatically triggers the existing repository CI.
2. CI executes only that pre-existing workflow.
3. CI does not access the external BugsInPy subject or evidence workspace.
4. CI does not build a BugsInPy subject environment.
5. CI does not execute a BugsInPy subject test or oracle.
6. CI does not perform eligibility screening.
7. CI does not run the RAW-vs-ERRPILOT downstream repair experiment.
8. CI does not mutate benchmark evidence or authoritative candidate outcomes.

Repository artifact checks satisfying these conditions are distinct from
benchmark research execution. A report covering a push must disclose whether
the automatic repository CI ran Docker and the minimal ErrPilot artifact demo,
and must report its result. This interpretation applies prospectively and
retrospectively only to the already disclosed CI side effect of adjudication
commit `46951423f73e19685f54fc858ba405fe75127181`.

This boundary does not authorize manually triggering additional Docker builds
or ErrPilot runs in a bounded benchmark transaction. BugsInPy subject builds,
imports, tests, oracles, 3/3 screening, eligibility classification, candidate
expansion, repair experiments, and downstream model/API calls remain closed
without their own authority. It changes no candidate disposition, eligibility
outcome, benchmark result, or scientific claim.

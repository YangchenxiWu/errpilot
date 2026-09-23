# BugsInPy production materialization gate v1

## Entry state and prior block

The frozen `ENVIRONMENT_MATERIALIZER_V1` implementation had
`REAL_MATERIALIZATION_ENABLED = False`. This second code gate allowed synthetic
fixture validation while preventing a real initial-40 build, even with the
authority token. The Human PI reports that the first real Batch 01 transaction
was blocked at this gate before any build; that block is accepted behavior.
The v1 code confirms the blocking mechanism. This repository contains no
independent execution log of that prior attempt.

## Production activation

Version `ENVIRONMENT_MATERIALIZER_V1_1` changes the global code gate to
`REAL_MATERIALIZATION_ENABLED = True`. It is a common executor for future
materialization batches. It contains no Batch 01 case list and does not
enumerate or launch a batch. This transaction performs zero real environment
materializations and changes no frozen recipe, source, candidate order, or
screening outcome ledger.

The enabled code path is a capability, not Human-PI transaction authority.
Every future real materialization requires a separately issued Human-PI
transaction naming its exact authorized case set. Batch 01 still needs that
separate authority. The exact token
`BUGSINPY_ENVIRONMENT_MATERIALIZATION_AUTHORIZED_V1` is required but is not,
by itself, Human-PI authorization.

## Entry controls for a future authorized batch

The caller must explicitly select `materialize` and supply the exact token,
request file, input root, and output location. The request must name one case
in the frozen initial 40, match its frozen build-recipe SHA-256, and match its
frozen self-reference ledger. The materializer implementation must be
committed at HEAD and the repository clean before a real request. Each case
invocation must fall within the exact case set named by that batch's Human-PI
transaction; this human authority boundary is outside the materializer's
global code gate.

The existing immutable base-image and platform checks, Python identity
checks, source-snapshot history exclusion, setup-action allowlist, no-retry
build behavior, synthetic/real separation, and environment identity
observations remain required. Any failed identity or authority check blocks
the request. A real build, dependency install, setup action, subject test,
oracle, eligibility result, repair run, or ErrPilot/model invocation requires
its own later authorized transaction and is not part of this activation.

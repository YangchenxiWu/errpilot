# Expansion Block 02 pre-dispatch incident V1

Status: `EXPANSION_BLOCK_02_PRE_DISPATCH_INCIDENT_V1_FROZEN`.

## Entry and authority

This adjudication entered on clean `main` at local HEAD and live `origin/main`
`8d176e14617c59e44c515cf687feb8329527c850`, ahead/behind `0/0`.
The frozen bridge status is `EXPANSION_BLOCK_02_MATERIALIZER_BRIDGE_V1_FROZEN`;
Block 02 identity is
`6d5a8a713ddcb18ea70b8268c72e7aa2d5e1eb44bace81f1bd485c88907c0b95`.
The V3 exclusions validator passed with 29 unique cases; `cases_manifest.csv` is
header-only. The Block 02 validator returned eight ready recipes, four per
environment mode, which derive 12 ordered production identities. No repository
Block 02 materialization result CSV or report existed at entry.

The original Human-PI materialization authority named the 12 identities under
the Block 02 bridge. It did not authorize a Block 01 request. This incident
adjudication is authority to preserve and classify the failed controller
transaction and to preflight a correction. It grants no new production run.

## Preserved event and causal boundary

The old controller created the external root below. Its durable identity ledger
recorded `tornado::13 / SOURCE_INDEPENDENT` as the first and only dispatched
identity. The one preserved request has `expansion_block=1`; the frozen Block 02
bridge requires `expansion_block=2`. Its request SHA-256 is
`7478212bf403afd81e264c60404ab70c32c4baafdfb8b28cb17f49214675cefd`.
The committed Block 02 entrypoint validates that field before calling
`_materialize_checked()`. The invalid request therefore rejected at the frozen
request-identity gate. The governed engine was not entered; no Docker subject
build, dependency install, or setup action began. The governed attempt
directory is absent. The controller then tried to write subprocess streams
inside that absent directory and failed with `FileNotFoundError`. Its blocker
record says the return code and raw stdout/stderr were lost. Those bytes are
unavailable and have not been reconstructed. The remaining 11 ledger entries
are `UNSTARTED`; no subject outcome was observed.

The controller dispatch record is **not** a governed production materialization
attempt. The Human PI classifies the event as
`CONTROLLER_PRE_DISPATCH_INVALID_REQUEST`, the invocation as
`NON_PRODUCTION_ATTEMPT`, and the prior batch as
`ABORTED_BEFORE_FIRST_PRODUCTION_ATTEMPT`. It is neither `MATERIALIZED` nor
`BUILD_FAILED`, nor a subject infrastructure, environment, oracle, or
eligibility outcome. The invalid invocation remains part of the historical
record. The Human PI determined that it did not consume the first-pass budget
for `tornado::13`; all 12 identities are
`UNATTEMPTED_AT_GOVERNED_BUILD_LAYER` and retain first-pass eligibility.

## Old evidence root seal

The historical root is
`/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_02`.
It is sealed as read-only incident evidence: never overwrite, truncate, delete,
reuse its ledger, manufacture an attempt directory, change its
`ATTEMPTED`/`UNSTARTED` records, or add reconstructed streams. The seal is a
governance rule; this transaction made no filesystem change to that root.

At adjudication, the root had ten files and an empty `attempts/` directory.
The following deterministic summary hashes sorted relative file paths to their
SHA-256 values, encoded the map as compact sorted-key UTF-8 JSON, and hashed
those bytes: `1cea074fbac40c465bff0b3a76f1fbfcca8b79da3e0a14d38af47ad44a6a50bb`.
The six controller/ledger/request files and their SHA-256 values are:

| Relative path | SHA-256 |
| --- | --- |
| `controller.py` | `6a5cb79fb737fac4e9b6d401dfbc3aa2e8fc66a370bd55278740dda3f5edf0c0` |
| `controller_blocker.json` | `07c086d786b7267b8cf28ed98fe9443b2fba9487c4b84c56b0e44fb273f42544` |
| `controller_identity.json` | `0cf1f6ea004a4ab1144361f69337c271db31f53195468eafffcb207fd8ecc253` |
| `identity_ledger.json` | `c46473c1e2a62a31fde31170845e28f2d3b343a3ffba74a3edf92a0809a044e7` |
| `preexisting_evidence_manifest.json` | `26b109ce46b3d6fddd0d2fe761df5262669a9da21242b5eb05677b36c8a1dde2` |
| `requests/01_tornado__13_source_independent.json` | `7478212bf403afd81e264c60404ab70c32c4baafdfb8b28cb17f49214675cefd` |

The four staged input hashes are: `requirements.dependencies.txt`,
`requirements.normalized.txt`, and `requirements.raw` each
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`;
`setup.raw` is `eda9238dce9ee9d86f2024e4723c24b9f566a2ef4e763ac92b6018e3c3244a7b`.
All four live under `inputs/` for `tornado__13`. The preexisting-evidence
manifest contains 198,335 entries and remained byte-for-byte unchanged.

## Future root and execution boundary

The corrected repository controller has status
`EXPANSION_BLOCK_02_PRODUCTION_CONTROLLER_V2_FROZEN` after 12/12 read-only
preflight and the stated test gates pass. This status describes controller
readiness only; it does not confer production execution authority.

The reserved future root is
`/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_02_v2`.
`v2` means controller transaction V2, not a second scientific attempt. It was
absent at entry and must remain absent in this transaction. A future approved
identity executed there would still be its first governed production
materialization attempt. The new controller's separate batch token is
unconfigured; preflight creates no production attempt record. A later exact
Human-PI execution authorization, with a new batch token and repository
transaction, is required before any real dispatch. Materialization does not
establish oracle or eligibility status.

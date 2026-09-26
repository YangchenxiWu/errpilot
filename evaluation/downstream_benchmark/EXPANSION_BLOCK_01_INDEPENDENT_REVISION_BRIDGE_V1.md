# Expansion Block 01 independent-revision bridge V1

Status: `EXPANSION_BLOCK_01_INDEPENDENT_REVISION_BRIDGE_V1_LOCAL_ONLY`.

## Authority and scope

The Human PI authorized a bounded capability correction to the committed Block 01
`materialize-expansion-01` path. This amendment changes no frozen Block 01
candidate, recipe, source commit, base image, dependency input, setup action,
or self-reference ledger. The initial-40 `materialize` path retains its existing
two-revision request semantics. This transaction authorizes synthetic and mock
validation only; it authorizes no real subject build or production attempt.

## One identity per Block 01 request

Every Block 01 request now requires an explicit `revision_label` and a
`revisions` array of exactly one object. For a source-independent recipe, the
only accepted identity is `SOURCE_INDEPENDENT` with
`{"label":"SOURCE_INDEPENDENT","sha":"ABSENT"}` and no source snapshot. For
a revision-specific recipe, the label must be `BUGGY` or `FIXED`; its single
revision object must bind the frozen corresponding source commit, a snapshot
manifest SHA-256, and an explicit source snapshot path. A paired BUGGY/FIXED
request, a missing selector, a mismatched label or commit, and any source in a
source-independent request fail before the build engine is called.

The dedicated entrypoint still verifies the Block 01 token, clean committed
materializer, frozen ledger, case and order, block identity, recipe hash,
self-reference rows, and expansion-only derived-input namespace. The shared
engine still verifies supplied input bytes and the actual source snapshot;
preserves `SOURCE_SNAPSHOT_MANIFEST_V2` and `BUILD_CONTEXT_MANIFEST_V2` with
safe tracked symlinks; checks the immutable linux/amd64 base identity; and uses
Distribution Probe V2 after successful final-image construction. Runtime
observation remains network-disabled and read-only.

The engine processes only the selected revision in a Block 01 request and
creates its attempt record under an exclusive output directory. A future BUGGY
`BUILD_FAILED` result does not dispatch FIXED implicitly and cannot prevent a
separately authorized FIXED request. No controller or automatic batch dispatch
is added here. A future production controller must enforce the one-attempt
budget across separate requests, name the new committed HEAD, and separately
authorize every required identity before any Docker subject build.

`MATERIALIZED != ELIGIBLE`. This bridge does not authorize a subject test,
oracle, eligibility run, repair, ErrPilot run, or downstream model/API call.

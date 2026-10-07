# V6 Preparation Execution Run — BLOCKED Entry Report

Run Report, 2026-10-07, Europe/Budapest. Candidate execution evidence; uncommitted.

## 1. Task summary

**STATUS = BLOCKED. No real preparation attempt was consumed.** The direct
Human-PI instruction authorizes execution of the exact frozen 641-opportunity
population. Canonical authority, local/live publication, population identities,
runtime source/configuration hashes, and the initial durable ledger match.
Execution cannot begin through the exact frozen runtime: its native `dispatch`
unconditionally raises `Rejected`; `NativeDockerTransport` accepts only a
`SYNTHETIC_QUALIFICATION_ONLY` provider and a qualification output subtree; its
materializer wrapper also requires `synthetic_only=True`. The two runtime
installation paths named by the accepted sources do not exist.

This is a global production-entry/runtime condition, not an ordinary build
failure or a per-opportunity terminal classification. None of the 641 items was
claimed, skipped, terminalized, retried, repaired, rescued, or substituted.
Bypassing these guards or supplying a new real provider would exceed the
instruction to use the exact frozen runtime without redesign or source/config
changes. This transaction stops at the entry gate.

The exact owning evidence is `successor_runtime.py:32` (unconditional dispatch
rejection), `:100` (real provider refusal), and `:195` (qualification-only
materializer). The canonical installation closure independently records the
unchanged unconditional production default deny at lines 80–83. These source
facts were checked locally rather than inferred from memory.

## 2. Final requested accounting (A–P)

| Item | Observed result |
|---|---|
| A. Canonical entry authority | `HUMAN_PI_AUTHORIZE_V6_PREPARATION_EXECUTION_RUN`; `main`; initial worktree/index clean and untracked empty. Local HEAD, local origin/main, and independently queried live origin/main all `0425059c2c2e306cd48b7739c51dc3cb3688e228`. Canonical lifecycle/projection `PREPARATION_EXECUTION_AUTHORIZED`; preparation planning/execution/authorized YES; source acquisition, oracle, allocation, downstream repair NO. |
| B. Exact population | 641 distinct ordered base-attempt identities; 431 dispatchable cases; frozen manifest and each work-item/recipe relationship verified with accepted adapter functions. Frozen population file SHA `288eaed9f7e9ff4daf2978e7c41b6c6ead83e9d99b9ddee7801c163153bd63bb`; semantic SHA `f3a719f2a92f1d1ba96baa9dd3936e8bd87d330f048542c9ee5cfce86185a800`. No population reconstruction or expansion. |
| C. Execution start/end | Execution did not start; both execution timestamps null. Completed final bounded entry audit: `2026-10-07T14:37:53.044365Z` to `2026-10-07T14:37:54.987681Z` (16:37:53–16:37:54 Europe/Budapest). |
| D. Durable ledger | Total 641; UNSTARTED 641; claimed 0; terminal 0; active claims 0; orphan/unresolved claims 0; retries 0. Actual claims/terminals/locks directories empty before and after read-only rejection probes. |
| E. Terminal outcome counts | Empty; no terminal outcomes observed or invented. |
| F. Environment-ready count | 0 established by this transaction; no environment-ready qualification occurred. |
| G. Non-ready terminal cases | 0. All 431 dispatchable cases remain unstarted; they are not reclassified as terminal non-ready. |
| H. Preserved blockers | `matplotlib::1`: `PREPARATION_PLAN_BLOCKED_SETUP_REPRESENTATION`, plan SHA `951d47ffd3c367e9f0a39addbd3e7fea0457e279735e129b5cb83d288ecbf563`. `matplotlib::8`: `PREPARATION_PLAN_BLOCKED_ORACLE_REPRESENTATION`, plan SHA `f820191cadeedee5e33829bc3f73f6244b73633497e214c0c61506ad6f7ac5da`. Both outside the 641-item dispatch population, consuming no attempts. |
| I. Network accounting | Frozen opportunity identities/order match enforcement: restricted 583 + NONE 58 = 641. Real execution counts are 0/0. Current network enforcement was not exercised. |
| J. Preparation types | Source-independent 221 + revision-specific 420 = 641; BUGGY 210 and FIXED 210 preserved. |
| K. Persistent identities | Accepted external root `/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1`; authoritative ledger under `ledger/{claims,terminals,locks}`. This transaction leaves the external root unchanged. Candidate entry evidence root is this repository directory. Empty ledger-file inventory SHA `3bd960131d32405d67df4b9348b00ec871864b2536499a7ae48f860c3a7cb24e` is an entry inventory, not a completed-execution ledger seal. |
| L. Environment-ready population candidate | Not constructed; path/count/SHA not applicable. The prerequisite 641 terminal opportunities is not met. |
| M. Execution closure candidate | Not constructed; path/SHA not applicable. This BLOCKED entry report does not represent execution completion. |
| N. Canonical preservation | SHA remains `e48580c1f9769d1b93ab995e6dcef3689c6920a9ce7b83f728526e9694dc68fd`; event count remains 3. Event #3 ID `237d8020668f338c04065beb8557d8f25263fbfc0282003dcc5b2af67a20a50d`, semantic SHA `368aa2581dd7a27dcea6b62a19aad7eb78d5d3ef96866ddfe322ca2dd91a840c`. No event #4. |
| O. Firewall | Source acquisition 0; builds 0; oracle 0; allocation 0; downstream repair 0; git stage/commit/push NO. |
| P. Completion review gate | `HUMAN_PI_REVIEW_OF_V6_PREPARATION_EXECUTION_COMPLETE_BASELINE` remains pending and **not reached**. Immediate Human-PI decision concerns the production entrypoint/controller/provider installation gap. |

All 433 census identities are covered exactly once by the initial census:
431 dispatchable cases plus the two accepted blockers. A final preparation
partition is not fabricated for unexecuted cases.

## 3. Files inspected and changed

Inspected canonical descriptor, independent pin, canonical installation
authority/closure, frozen successor contract and schema, all three event
references, frozen preparation manifest, work-item population, ledger proposal,
runtime authority acceptance, preparation adapter/runtime/ledger sources,
candidate controller, native runtime/config/enforcement identity, and owning
lifecycle event identity validator. Read actual external namespace metadata and
all ledger states/directories. No on-disk AGENTS.md or .airos contract/state was
found; the supplied user instructions govern.

Seven new files are bounded to this candidate evidence directory:

- `validate_entry.py`: read-only integrity and rejection audit.
- `entry_observations.json`: direct authority, initial clean state and live remote receipt.
- `entry_validation.json`: preserved empty stdout from the first audit's failed event-hash check.
- `entry_validation_v2.json`: completed entry audit; SHA `b0445f6f86d9315a1de0812c7713db747efc7a75c49bd21830ffb008611c6a03`.
- `failed_check_observations.json`: failed checks, causes and corrections.
- `RUN_REPORT.md`: this report.
- `artifact_sha256.json`: byte inventory of the six other candidate files; excludes itself.

The 1015 preexisting tracked file byte/mode identities have the same aggregate
fingerprint before and after the audit:
`1db4d925d48fc1b8cc853893c138e46050b6e9cdebfb5efd0b902b500a0fac17`.
No accepted runtime, frozen plan/recipe, event, effectivity package, canonical
descriptor, or preexisting tracked file was edited. No external write occurred.

## 4. Commands run

Read-only shell inspection used `pwd`, `rg --files`, `rg -n`, `cat`, `sed`,
`nl -ba`, `wc -l`, `ls -la`, and `shasum -a 256` on the stated local paths.
Git commands: `status --porcelain=v1 --untracked-files=all`,
`branch --show-current`, `rev-parse HEAD`, `rev-parse origin/main`,
`ls-remote origin refs/heads/main`, `ls-files -z`, `cat-file blob` for the accepted
historical planning descriptor, `diff --name-only`, `diff --cached --name-only`,
`diff --check`, and `diff --cached --check`. No fetch or Git mutation was used.

Python read-only inline inspections and rejection probes ran with `python3 -B`
and the existing `.venv/bin/python -B`. The completed reproducible audit command:

```text
.venv/bin/python -B -m evaluation.downstream_benchmark.evidence.v6_preparation_execution_run_v1.validate_entry
```

Its stdout was saved exclusively as `entry_validation_v2.json`. Writing these
new candidate files used `apply_patch` and exclusive stdout/manifest creation.
No production dispatcher was invoked with a real work item, and no Docker,
Buildx, buildctl, source-export, benchmark oracle, subject test, dependency
installation, or network-qualification command ran.

## 5. Tests passed/failed

PASS: exact canonical SHA/schema/state/phase firewall and independent pin;
event file/semantic identities through the unchanged owning validator;
frozen manifest/plan/work-item/recipe identities; 641 unique attempts and frozen
ordering; 583/58 network identity/order reconciliation; 221/420 preparation
type counts; seven scientific base identity coverage; 433 census identity
coverage and blocker exclusion; initial durable ledger accounting; unchanged
ledger after expected native dispatch and real-provider rejections; tracked
byte/mode and canonical preservation. Completed audit exited 0. Git worktree
and cached whitespace checks pass.

Failed preliminary checks are preserved in `failed_check_observations.json`:
sandboxed live Git DNS access failed before the authorized escalated read
succeeded; system `python3` lacked `jsonschema`, resolved by the existing venv
without installation; the first new audit used the preparation adapter's
compact encoding for lifecycle event hashes, corrected only in this new audit
by calling the accepted owning `validate_event_identity` function. These are
inspection/audit failures, not subject preparation outcomes or retries.

No scientific validation or preparation success is claimed. No completion
gate check can pass while all 641 opportunities remain unstarted.

## 6. Contract compliance, risks and unknowns

Accepted runtime source SHA is exactly
`c83da6f5eb355702f994c28efc6b14bc36988a9cc405ff05a689a9f97128f4b6`;
configuration/data SHA is exactly
`654299e49b0fc8833f093ecc887b4578970895ce28aa5359b4b37246f7b6190e`;
semantic enforcement identity independently recomputes to
`8801637324b2fa32124df8444e88f193a5be3f9c847904f2eebfb92197bc5c10`.
The native dispatcher/provider rejection is reproducible and not changed by
the caller's new execution authority. Runtime installation files
`V6_NATIVE_BUILDKIT_CLIENT_RUNTIME_INSTALLATION_V1.json` and
`V6_PREPARATION_EXECUTION_RUNTIME_INSTALLATION_V1.json` are both absent.
The external namespace metadata still identifies an
implementation/synthetic-qualification-only namespace; it was preserved.

After this global entry block, current source commits/blobs, live OCI layout
contents, Docker/daemon/proxy/firewall state, output materialization, and
environment-ready qualification were not checked. Historical frozen
qualification records do not prove these current operational states. No
assumptions about their readiness are made.

## 7. Recommended next action

Human-PI should resolve the accepted production entrypoint/controller/provider
installation gap under a separate bounded authority that states whether and
how production activation may change or extend the frozen runtime lineage.
Preserve all 641 unstarted opportunities and canonical event #3. Do not infer
permission to implement that change from this execution transaction. Once
the gap is resolved, entry authority and the durable ledger require exact
revalidation before any real attempt. The requested complete-baseline review
gate is not yet available. Stop.

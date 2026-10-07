# V6 Preparation Execution Activation Package — Run Report

Date: 2026-10-06, Europe/Budapest.

STATUS = V6_PREPARATION_EXECUTION_ACTIVATION_PACKAGE_READY_FOR_HUMAN_PI_REVIEW

## A. Task summary, entry and canonical state

The supplied direct Human-PI gate HUMAN_PI_AUTHORIZE_V6_PREPARATION_EXECUTION
authorizes this bounded activation-package construction. It does not accept the
independent permissions. This report, six Python files and seven JSON files are
review candidates only. All 14 new paths stay in this one evidence directory;
no existing repository file, shared implementation or scientific claim is edited.
Local saving is not Human-PI lifecycle acceptance, freeze, committed persistence
or publication.

Repository `/Users/wuyangchenxi/errpilot`, branch `main`. Entry LOCAL HEAD and
actually queried LIVE origin/main equal `5c007fbfbfc5b3529105a14f87127f50e1eab6d7`.
Entry tracked worktree and index were clean, with no untracked files. The final
live query returned the same ref. The sandbox first query failed DNS; the
explicitly required elevated read-only query succeeded. No fetch/clone occurred.
The remote-ref metadata read is distinct from build/source-acquisition traffic.
No on-disk AGENTS.md or `.airos/current_state.md` / Research Contract was found
in bounded repository/ancestor locations; the supplied global instructions and
the pasted request govern this transaction.

Canonical `evaluation/downstream_benchmark/v6_current_state.json` SHA-256 is
`6a9028c79aa62f90db2b2d53def32ab23bffcfa3c71d2ec30d7fa64e741e3aae`.
Lifecycle label and projection state remain PREPARATION_PLANNING_AUTHORIZED,
event count 2. PREPARATION_PLANNING=YES; PREPARATION_EXECUTION=NO;
PREPARATION_AUTHORIZED=NO. SOURCE_ACQUISITION, IMAGE_BUILD, ORACLE_EXECUTION,
PILOT_FINAL_ALLOCATION and DOWNSTREAM_REPAIR_EXECUTION remain NO.
All 433 canonical cases remain NOT_STARTED, attempt_consumed=false and without
environment identity. Canonical environment-ready count is 0.

## B. Exact frozen lifecycle requirement

The unchanged lifecycle requires this exact edge:

```text
PREPARATION_PLANNING_AUTHORIZED
  -- HUMAN_PI_AUTHORIZE_V6_PREPARATION_EXECUTION -->
PREPARATION_EXECUTION_AUTHORIZED
requires = Exact accepted plans, separate source acquisition/materialization/build permissions, revalidated implementation; once-only attempts
```

This transaction constructs no event #3 and no effective-current descriptor.
The gate itself does not grant separate source, materialization, build, network
or persistent-output acceptance. No already accepted exact V6 execution
subauthority was identified in the inspected controlling V6 authorities;
historical predecessor authorities remain confined to their own membership.

## C. Accepted-plan revalidation

Manifest `evaluation/downstream_benchmark/v6_preparation_plan_manifest_candidate.json`:
SHA-256 `3c0a6980360c23f6626863be232fea2878cf13497a74aa2e267594fcf3801b0e`.
Closure `evaluation/downstream_benchmark/V6_PREPARATION_PLAN_LIFECYCLE_CLOSURE_V1.md`:
SHA-256 `9e0bbf8db1eaedb344163a98e944915a51e87424d4abf6894545056e73eccfe7`.

The full accepted external semantic validator was rerun read-only, preserving
all accepted bytes. Its historical descriptor reference was resolved to the
immutable planning-baseline Git blob at
`3939dfca7f25d3c1d4cd97c76b3676694cda84be`, SHA
`9295430e8573474b17bc79339c92f46044e443b9dabfe81280f9fb789d751073`.
Only its file_ref resolution was adapted in memory. The installed current
descriptor was independently compared to the accepted effectivity package and
exact pin, with accepted event #1/#2 and effectivity replay passing.

The full 433-member/15-project census, original frozen ranks, 1..433 ordinals,
866 variant commit bindings, metadata literal bytes, derived requirements,
setup actions, protected manifests and blocker reconciliation passed.
Constructible=431, setup blocker=1, oracle blocker=1, source-acquisition-required=0.

matplotlib::1 at census ordinal 67/rank 118 retains literal
`python -mpip install -ve .` and PREPARATION_PLAN_BLOCKED_SETUP_REPRESENTATION.
matplotlib::8 at ordinal 121/rank 176 retains its semicolon-composed literal
pytest line and PREPARATION_PLAN_BLOCKED_ORACLE_REPRESENTATION. Neither is
rescued, normalized, reclassified, marked successful or dispatched.
Machine evidence: `evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/revalidation.json` — SHA-256 `fd260c14dff347de4577b253037e4a528691fa3dc4286de5ad49a174d342d3e9`.

## D. Implementation reuse / gap matrix

| Component | Classification | Evidence / consequence |
| --- | --- | --- |
| Shared input byte/hash and setup ledger verification | EXACTLY_REUSABLE | verify_inputs is invoked with accepted embedded bytes; no renormalization |
| Supported setup argv and ordered Dockerfile definition | EXACTLY_REUSABLE | action_argv/build_definition stay unchanged; all 641 definitions derive through them |
| Shared single-identity materializer, probes and identity observations | EXACTLY_REUSABLE | Existing _materialize_checked(single_identity=True) is the future route; never invoked here |
| V6 accepted-plan to shared engine fields | V6_BINDING_REQUIRED | adapter_candidate.py projects fields and binds both accepted recipe SHA and projected engine-input SHA |
| Source V2 exporter algorithm | EXACTLY_REUSABLE | Original source_snapshot_identity code object retained; no duplicate exporter algorithm |
| Historical source resolver | V6_BINDING_REQUIRED | Scoped copied function globals provide immutable V6 mirror/revision resolver; predecessor globals unchanged |
| V2 safe symlink, source transport and context manifests | EXACTLY_REUSABLE | Existing materializer safety/copy/hash mechanics; actual source transport/export remains unexecuted |
| Installed distribution V2 and environment identity field order | EXACTLY_REUSABLE | Existing seven-runtime backend selection/observations; no installed manifest or final identity is fabricated |
| Old membership loaders, block identity records and tokens | SEMANTICALLY_INCOMPATIBLE | Initial-40 and Block-01/02/03 membership cannot admit V6; Block-03 token is rejected |
| Historical runtime authority structural pattern | V6_BINDING_REQUIRED | Strict independent envelopes and hash bindings adapted; historical accepted envelope is not V6 authority |
| Timestamp attempt names and mutable whole-table controller ledger | SEMANTICALLY_INCOMPATIBLE | Stable SHA identities and immutable claim/terminal protocol replace this design in the candidate only |
| Shared network_build boolean as a declared-origin restriction | SEMANTICALLY_INCOMPATIBLE | Default network needs externally enforced deny-by-default egress, accepted policy and evidence before use |
| Cookiecutter Block-03 gitlink exception | NOT_APPLICABLE | No V6 plan has a gitlink; no special permission or member is inherited |
| Frozen V6 schemas and phase_flags_for_edge | EXACTLY_REUSABLE | Existing descriptor/event schemas pass; pure future phase delta has exactly three changed leaves |
| matplotlib::1 and matplotlib::8 | BLOCKED | Exact setup and oracle representation blockers remain; neither is a base work item |
| Current local Docker-base presence / restricted egress deployment | BLOCKED | Future dispatch prerequisite until separately authorized probes/provisioning; not checked or qualified in this transaction |

The exact inspected/shared identities are bound in authority_candidates.json:

| Shared path below evaluation/downstream_benchmark | SHA-256 |
| --- | --- |
| `DISTRIBUTION_PROBE_V2.md` | `4748af02119304ca754e2d4b972d3894278ba5cdd8516064fece96e69f69e7f4` |
| `ENVIRONMENT_BUILD_SPEC_V1.md` | `570585eb42712936fa67f72f1ae686375c591ffa4dd14e650335d0db614ab7ca` |
| `ENVIRONMENT_MATERIALIZER_V1.md` | `7ea6f0f93f8edafdc7fdd534fd74dcee2c6dc7e354ee7d3c0f2495c7d4443196` |
| `MATERIALIZATION_GATE_V1.md` | `58e65f24b12d6a6b767a49352f3e9daf6e4b64d426bb9af8d30de4bf7596f4ed` |
| `SOURCE_SNAPSHOT_SYMLINK_V2.md` | `dc6f065fc04785122e203b71c2805dc5bba94d21a8ee6e19d4c7f110c7288c79` |
| `screening/block_03_gitlink_source_export.py` | `26ff2b8ffc6ddb9e36fd727bb5c4a3797d678f59aacf3e94e509b56c797ac200` |
| `screening/build_recipes.py` | `96fd5f432474c76c25aaccc5cce5ac588d76cdaace269a7b9c7fd9356c3b2aba` |
| `screening/materialize_expansion_block_02_batch.py` | `a195445fddcd5ef9f51481d46611fb28cfe666c335ce7267dab805bc884c542c` |
| `screening/materializer.py` | `98ba9a45b6b9beaaf00119efe0da07f5513a1d56578d00a5a2dc59cc088dea0c` |

## E. V6 input/runtime binding candidate

`evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/adapter_candidate.py` — SHA-256 `0246d455fee259486640fd0d10451af864532a6b22131a73c40eac157da04808`.

Selection requires exact manifest path/SHA, integer census ordinal, case ID and
plan SHA. The population follows frozen rank order and BUGGY before FIXED for
revision-specific cases. There is no alternate scientific subset, latest/mtime/
lexical/directory fallback, capacity stop or governed batch.

The adapter projects the accepted embedded recipe into the shared engine field
shape. It preserves the accepted recipe SHA separately from the new projected
engine-input SHA. Accepted future_argv annotations are omitted only from the
legacy engine's setup-action representation; the original action text, order,
ledger hash and shared computed argv must match exactly. No frozen recipe bytes
or parser/allowlist are changed. The legacy execution_plan_sha256 identity field
binds the whole accepted preparation plan SHA in this proposed V6 representation;
it does not establish an oracle six-slot execution plan.

The source candidate reuses the original exporter code object with scoped V6
resolver globals and exact mirror/commit binding. Predecessor module globals
and membership are unchanged. The function is never invoked. No snapshot SHA is
claimed for a real source export; zeros used in tests are explicit mock fixtures.
All real source snapshot identities and environment identities remain unknown.

`evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/controller_candidate.py` — SHA-256 `3f7086db4ac791ecc81b3032f9844f909fd8baad1835f3bf60ee93cbd52879dc`.
Its review_route reaches only a ReviewSentinel. real_dispatch always rejects
CANDIDATE_ONLY. This is not an installed production runtime consumer.

## F. Exact preparation work-item model and counts

`evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/work_items_candidate.json` — SHA-256 `288eaed9f7e9ff4daf2978e7c41b6c6ead83e9d99b9ddee7801c163153bd63bb`.
Population semantic SHA-256: `f3a719f2a92f1d1ba96baa9dd3936e8bd87d330f048542c9ee5cfce86185a800`.

| Population | Count |
| --- | ---: |
| Source-independent cases / SOURCE_INDEPENDENT work items | 221 |
| Revision-specific cases | 210 |
| Revision-specific BUGGY work items | 210 |
| Revision-specific FIXED work items | 210 |
| Dispatchable cases | 431 |
| Blocked/non-dispatchable cases | 2 |
| Total base preparation attempt opportunities, if independently authorized | 641 |
| Work items needing narrowly scoped build-network permission | 583 |
| Work items retaining build network NONE | 58 |

The count is derived as 221 + (210 x 2)=641. Source-independent images can serve
both later source variants; they create one environment opportunity per case.
The 866 revision bindings are source availability evidence and are not a build
attempt count. One durable base opportunity covers input/snapshot/context/build
and observation. At most 641 Docker build invocations could follow; prebuild
blocking or interruption can yield fewer. No success/readiness count is predicted.
BUGGY failure does not consume/suppress the distinct FIXED base identity.

Every item binds case, ordinal, frozen rank, plan SHA, mode, applicability,
source revision/tree where relevant, exact recipe/input/runtime identities,
protected manifest and derived network requirement. Operational scheduling
chunks, if later used, have scientific/membership/stopping authority NONE.

## G. Once-only attempt accounting candidate

`evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/ledger_candidate.json` — SHA-256 `5d1f10f5fa28860d7eb47a3a56a092c2492e2a90b440904990e44a8cf014d7bc`.
Controller identity is given in E. Every proposed base ID is
`v6-prep-base-` plus SHA-256 of its complete frozen binding body, excluding only
the already derived base_attempt_id. Canonical serialization uses sorted keys,
compact UTF-8 JSON, ensure_ascii=false and one LF. Timestamp/randomness do not
participate. The identity anchors the current accepted planning descriptor SHA;
the later execution descriptor must have a separately accepted exact pin and
lineage to this anchor. Event activation cannot create a fresh base opportunity.

All 641 saved candidate ledger entries are UNSTARTED/unclaimed/unconsumed.
The proposal uses exclusive durable claim and unique terminal records rather
than overwriting a status table. Claim fsync precedes every operation; a surviving
claim blocks another dispatch. Exactly one terminal first-pass observation is
permitted. BUILD_FAILED, BLOCKED_* and INTERRUPTED cannot be overwritten by
success. Crash/partial record or orphaned lock blocks; separate evidence audit
may append INTERRUPTED without rerunning the build. Retry needs separately
versioned Human-PI authority, a new identity and exact supersession lineage;
this base controller supports no retry.

Journal logic is tested only in CANDIDATE_TEST_ONLY memory. The durable O_EXCL /
fsync / lock protocol is a proposal-level design, explicitly allowed by G.
Actual persistent I/O and real runtime-entry installation require separately
accepted implementation closure and revalidation; they are not tested/installed
or claimed complete as production capability here.

## H. Source-acquisition applicability

Fresh read-only verification passed 15 mirrors, all 866 commit bindings and
61,333 unique required leaf blobs across project repositories, missing objects=0.
SOURCE_ACQUISITION_CURRENTLY_REQUIRED=NO; SOURCE_ACQUISITION_AUTHORIZED=NO.
This is a current applicability observation. Any later missing required object
blocks and returns to separate Human-PI source-acquisition authority. No fetch,
clone, source export or real snapshot staging was performed.

## I. Materialization authority candidate

All four independent records are in `evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/authority_candidates.json` — SHA-256 `13c4c6753263b0657bca1c49122f4f73e27254c5c5d30e7d4c158f9782cf6360`.
Each record has its own canonical semantic SHA and the exact common binding:
`68e9335a77d7b1f86ea1cfa2341cf44a9a1c716b1938f52806b151de2218b80d`. They can be separately adjudicated; acceptance
is not inferred from their shared file or the received lifecycle gate.

| Independent permission | Acceptance / lifecycle | Candidate record semantic SHA-256 |
| --- | --- | --- |
| BUILD_NETWORK | NO / CANDIDATE_ONLY | `42393faa33851396fd70557558fa0e538f817fbee9072d0d56ec9d9323fc21a1` |
| ENVIRONMENT_MATERIALIZATION | NO / CANDIDATE_ONLY | `9d26db1b5b8c2651677f65c2d5e8fa6aa1b1aea46b3fdf2e7eb3e7bf87011c34` |
| IMAGE_BUILD | NO / CANDIDATE_ONLY | `a95e1615a4a757da70dd968cc15541dadc056a402ce3f0474aaad02adc96820b` |
| PERSISTENT_EVIDENCE_OUTPUT | NO / CANDIDATE_ONLY | `101db1b51f5cd6699a892f763ed56353f514345af287a6840fbbf8b6cf70214d` |

ENVIRONMENT_MATERIALIZATION scope is the exact 641-item population, accepted
input persistence and 420 exact revision-specific source snapshots using shared
V2 mechanics. Source-independent contexts contain no subject source. No history,
official patch, metadata, opposite revision, acquisition or oracle is permitted.
Every record binds current descriptor, accepted manifest/closure, full ordered
population, exact adapter/controller, ledger, output root, shared mechanics and
no-retry rules. HUMAN_PI_ACCEPTED=NO.

## J. Image-build authority candidate

IMAGE_BUILD independently covers at most one shared-engine build opportunity
per work item (maximum 641), exact projected Dockerfile/context/input identity,
seven frozen linux/amd64 base runtime references and required shared probes /
installed-distribution / environment observations. No base substitution,
pull, recipe/source/version repair, subject import/test or oracle is authorized.
Current local base availability was not probed; unavailable bases block and
need separate runtime acquisition authority. HUMAN_PI_ACCEPTED=NO.

## K. Build-network authority candidate

Frozen policy is exactly
DECLARED_DEPENDENCY_SOURCES_ONLY_SEPARATE_AUTHORITY_REQUIRED.
Real execution network remains NONE, including future identity probes.

The minimum declared-consumer scope is 583 work items in 373 cases: substantive
non-comment dependency input or a frozen setup action with requires_network=true.
Empty/comment-only files alone do not supply permission; the remaining 58
source-independent work items stay network=none. The exact ordered 583 IDs are
bound in the network record. This is a permission applicability derivation,
not an observation that any package installation succeeds or contacts a source.

Proposed package origins are `https://pypi.org/simple/` and
`https://files.pythonhosted.org/`, with declared transitive/build requirements
only and provenance. These are candidate defaults, not a finding about current
base-image pip configuration. Future read-only installer-source verification
must match; a different or undeclared source blocks for a separate exact Human-PI
decision. No configuration/source/version is replaced. Registry egress/pulls,
VCS acquisition, arbitrary Internet and undeclared setup downloads are excluded.

The shared engine's --network=default Boolean cannot enforce origins. Future
permission additionally requires accepted, provisioned, deny-by-default Docker
build/daemon egress, implementation identity, allow/deny evidence, exact argv,
destination/request/package/artifact provenance, raw installer/build logs and
denial/failure evidence. Unrestricted default networking cannot satisfy it.
This infrastructure is not provisioned or qualified here. HUMAN_PI_ACCEPTED=NO.

## L. Persistent evidence/output binding

The existing governed parent convention is
`/Users/wuyangchenxi/errpilot-benchmark-work`. Historical materialization and
preparation children were inspected through the exact predecessor controllers
and preservation census. No existing accepted V6 attempt namespace applies.
Proposed child `/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1` requires
explicit Human-PI output acceptance; it is not created. This is an explicit
output-root decision requirement, not a claim of current output authority.

Future outputs include exclusive claim/terminal records, exact input/controller
identities, Dockerfile/context identity, source snapshot identity or ABSENT,
raw build log, image inspection/Python probe, installed distributions,
environment identity, failure/interruption evidence and network provenance.
FIXED source/context and evidence stay outside repair workspaces.
PERSISTENT_EVIDENCE_OUTPUT HUMAN_PI_ACCEPTED=NO.

## M. Publication and runtime entry gates

The accepted plan and canonical planning baseline are already committed and
present at the required live main ref. New candidates remain untracked and
unaccepted/unfrozen/uncommitted/unpublished.

Before any real preparation dispatch, close the exact gates recorded in the
authority package:

1. Human-PI accepts the exact V6 adapter/source resolver/runtime binding,
   ordered work population, once-only protocol and independent permissions;
   freeze/persist/commit the accepted identities.
2. Complete and separately revalidate the real runtime integration and durable
   exclusive/fsync ledger I/O; candidate sentinel-only routes are not executable
   authority. Preserve the source resolver, recipe and no-retry semantics.
3. Explicitly accept the proposed V6 output namespace and exact restricted
   build-network source/enforcement/evidence scope, provision enforcement and
   verify its identity. Provisioning itself is not authorized by this transaction.
4. Publish the reviewed runtime implementation and authority closure as required
   by retained materialization/publication gates, then verify exact clean
   committed local/live identities. No publication waiver is inferred; any
   not-applicable decision would need explicit exact Human-PI binding.
5. Separately accept/close event #3, successor effectivity binding, canonical
   compare/install authority and independent final descriptor SHA acceptance pin.
   Verify the full chain and the exact execution descriptor before runtime use.
6. Recheck all local source objects and exact base runtime identity without
   acquisition; absent source/base objects block. Bind operation-level permissions
   explicitly in the accepted V6 consumer. Frozen event #3 itself does not flip
   IMAGE_BUILD/SOURCE_ACQUISITION flags or supply independent permission acceptance.
7. Verify the durable claim/terminal census before each once-only dispatch;
   no claim/terminal/evidence path may be overwritten or used for automatic retry.

## N. Event #3 readiness

Event #3 is not constructible/effective in this transaction: separate candidate
acceptance, implementation/durable-runtime closure and applicable publication /
effectivity/installation gates are unclosed. Merely changing NO to YES in a
candidate record is not closure. After those exact prerequisite closures,
the frozen edge is deterministic and needs no scientific state reinterpretation.

The pure unchanged phase_flags_for_edge calculation has exactly this delta:

| Leaf | Before | After |
| --- | --- | --- |
| projection.state | PREPARATION_PLANNING_AUTHORIZED | PREPARATION_EXECUTION_AUTHORIZED |
| projection.lifecycle.PREPARATION_AUTHORIZED | NO | YES |
| projection.phase_authorizations.PREPARATION_EXECUTION | NO | YES |

PREPARATION_PLANNING stays YES. Every case scientific state, attempt field,
readiness identity, allocation and other phase flag stays unchanged at activation.
No event bytes, successor descriptor or installation file is fabricated here.

## O. Validation, commands and rejection matrix

Final guarded validation: 4 unit tests passed; 0 failed,
0 errors; 57 rejection probes passed. Every one of 641
adapter/controller proposals reached only a non-executing sentinel; 420
source bindings reused the exact shared source-exporter code object without
calling it. All shared Dockerfile definitions derive from accepted inputs;
the ordered list SHA is
`c79e0230b42ea6e10bfead66c4977114f4461c8de139e1f463ccb1b34ace729a`.
Owning descriptor/two event/lifecycle schemas and exact candidate structures /
hashes passed. Ruff, AST, strict JSON, UTF-8/LF/BOM/NUL/trailing whitespace and
git diff --check passed. Final whole-file/inventory checks cover new report and
inventory as well; validation_results records its own preceding guard scope.

Guard counters: real_engine_calls=0, real_source_exports=0, docker_calls=0,
network_attempts=0, forbidden_process_attempts=0. Test-guard read-only Git
processes=10; full accepted source /
replay revalidation recorded 2851
read-only Git calls. No full repository pytest, real source-export test,
Docker/container probe, subject installation/import/test, oracle, runtime
qualification or scientific validation was run. None is claimed.

Principal commands actually run (plus bounded cat/rg/sed/inline Python reads):

```text
cat /Users/wuyangchenxi/.codex/attachments/51587d63-b1a2-421e-ad7c-be2f34baa67e/已粘贴的文本.txt
git rev-parse HEAD
git branch --show-current
git status --porcelain=v1 --untracked-files=all
git ls-remote --heads origin main
.venv/bin/python -B /private/tmp/errpilot_v6_package_revalidate.py > evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/revalidation.json
PYTHONPATH=. .venv/bin/python -B evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/construct_package.py
PYTHONPATH=. .venv/bin/python -B evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/validate_package.py
PYTHONPATH=. .venv/bin/python -B -m ruff check --no-cache evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/*.py
git diff --check
.venv/bin/python -B /private/tmp/errpilot_v6_package_report.py
```

Recoverable tooling corrections: an initial manifest lookup used `cases` rather
than the actual `plans` key and was corrected read-only. A constructor reference
used a nonexistent gitlink helper filename, then was corrected to the actual
shared module. The first guarded validator stopped before unit tests on a path
inventory serialization mismatch (ASCII escapes vs UTF-8); original count/hash
matched under the original serialization and the checker was corrected. An
existing planning-only delta-display helper was replaced with a generic pure
leaf diff, yielding the required three-leaf delta without changing source checks.
The initial candidate network predicate was then narrowed from file-presence
to explicit declared consumers, and validation rerun. No failure ran a forbidden
operation, consumed an attempt or changed accepted files. Final results supersede
these tooling attempts; original scientific blockers remain unresolved.

Machine evidence: `evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/validation_results.json` — SHA-256 `b9226116bb4320c7e35221691ffbb20bf3034e2d0498f29995b8c57b4c49294c`.

| Rejection check | Result |
| --- | --- |
| missing_environment_materialization_authority | PASS |
| missing_image_build_authority | PASS |
| missing_build_network_authority | PASS |
| missing_persistent_evidence_output_authority | PASS |
| predecessor_block_03_token | PASS |
| unaccepted_candidate_permission | PASS |
| wrong_runtime_descriptor_binding | PASS |
| wrong_independent_authority_scope_sha | PASS |
| source_acquisition_attempt | PASS |
| oracle_execution | PASS |
| stop_at_capacity_behavior | PASS |
| governed_chunk_batch_semantics | PASS |
| chunk_membership_authority | PASS |
| chunk_stopping_authority | PASS |
| latest_selector | PASS |
| mtime_selector | PASS |
| lexical_selector | PASS |
| directory_scan_selector | PASS |
| automatic_retry | PASS |
| silent_rescue | PASS |
| missing_remote_publication_verified | PASS |
| missing_clean_committed_head | PASS |
| missing_source_objects_present | PASS |
| missing_base_runtime_verified_without_pull | PASS |
| missing_restricted_default_build_network_verified | PASS |
| missing_exact_execution_descriptor_pin_and_full_chain | PASS |
| repeated_base_attempt_at_dispatch | PASS |
| real_engine_as_sentinel | PASS |
| wrong_current_descriptor | PASS |
| wrong_manifest_sha | PASS |
| wrong_manifest_path_latest_fallback | PASS |
| blocked_case_matplotlib::1 | PASS |
| blocked_case_matplotlib::8 | PASS |
| wrong_ordinal | PASS |
| ordinal_bool_type | PASS |
| wrong_plan_sha | PASS |
| reordered_case | PASS |
| stale_recipe | PASS |
| hidden_recipe_mutation | PASS |
| setup_normalization | PASS |
| wrong_revision | PASS |
| wrong_variant | PASS |
| duplicate_work_item | PASS |
| real_dispatch_candidate_only | PASS |
| retry_without_authority | PASS |
| repeated_base_attempt_claim | PASS |
| terminal_without_claim | PASS |
| materialized_without_evidence | PASS |
| successful_overwrite_BUILD_FAILED | PASS |
| retry_claim_after_BUILD_FAILED | PASS |
| successful_overwrite_BLOCKED_INPUT_IDENTITY | PASS |
| retry_claim_after_BLOCKED_INPUT_IDENTITY | PASS |
| successful_overwrite_INTERRUPTED | PASS |
| retry_claim_after_INTERRUPTED | PASS |
| successful_overwrite_MATERIALIZED | PASS |
| retry_claim_after_MATERIALIZED | PASS |
| ledger_lineage_drift | PASS |

## P. Exact new file inventory and files changed

Exactly 14 new untracked files in `evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/`. No tracked diff or index change.
Below are 12 supporting code/data/evidence SHA identities; RUN_REPORT.md has
no self-hash and artifact_sha256.json binds all 13 other files, including this
report. Its own independent SHA is observed after finalization to avoid a cycle.

| File | SHA-256 |
| --- | --- |
| `adapter_candidate.py` | `0246d455fee259486640fd0d10451af864532a6b22131a73c40eac157da04808` |
| `authority_candidates.json` | `13c4c6753263b0657bca1c49122f4f73e27254c5c5d30e7d4c158f9782cf6360` |
| `construct_package.py` | `ebfbc3094bdf614d8694533b839167df066e1a10e3f0580372f7493db7776676` |
| `controller_candidate.py` | `3f7086db4ac791ecc81b3032f9844f909fd8baad1835f3bf60ee93cbd52879dc` |
| `entry_verification.json` | `833591f35c5ee49ba287a9282e57b51fd6ac0fa1d24966d035f1952831772e72` |
| `ledger_candidate.json` | `5d1f10f5fa28860d7eb47a3a56a092c2492e2a90b440904990e44a8cf014d7bc` |
| `revalidate_sources.py` | `c1e3cd31607de167eaf0109aa0859312b480ee8c4d8dc79f85d1c8b0c6ebf30a` |
| `revalidation.json` | `fd260c14dff347de4577b253037e4a528691fa3dc4286de5ad49a174d342d3e9` |
| `test_candidates.py` | `255296243650e63d14b87c58f6d4c543fbfc88ce637482d8698768a779d9e9e5` |
| `validate_package.py` | `d8dbb9f61516d68d9a3df9309888efb554e9e648776b32065d5c3a0497049d74` |
| `validation_results.json` | `b9226116bb4320c7e35221691ffbb20bf3034e2d0498f29995b8c57b4c49294c` |
| `work_items_candidate.json` | `288eaed9f7e9ff4daf2978e7c41b6c6ead83e9d99b9ddee7801c163153bd63bb` |
| RUN_REPORT.md | SELF_HASH_EXCLUDED; bound by artifact_sha256.json |
| artifact_sha256.json | SELF_HASH_EXCLUDED |

## Q. Contract compliance, preservation and firewall

The explicit candidate-only scope is satisfied. Entry identity was unique;
accepted plans and shared scientific mechanics stayed exact. Only the bounded
package is authored. All 615 preexisting tracked byte/index identities and
242 historical preparation/attempt metadata hashes match entry. The bounded
historical evidence path map (101,284 file paths, excluding subject source,
contexts/workspaces and caches) retains its original count and full-map SHA.
No production child/root or attempt directory is created. Repository candidate
evidence saving does not grant persistent real-attempt output authority.

```text
PREPARATION_EXECUTION_CANONICAL_EFFECTIVE = NO
PREPARATION_EXECUTED = NO
ATTEMPTS_CONSUMED = 0
ENVIRONMENT_READY_CASES_ESTABLISHED = 0
SOURCE_ACQUISITION_EXECUTED = NO
SOURCE_ACQUISITION_AUTHORIZED = NO
REAL_MATERIALIZATION_EXECUTED = NO
REAL_IMAGE_BUILD_EXECUTED = NO
REAL_BUILD_NETWORK_USED = NO
ORACLE_EXECUTED = NO
ALLOCATION_EXECUTED = NO
CANONICAL_CURRENT_STATE_MODIFIED = NO
EVENT_3_CREATED = NO
EFFECTIVE_CURRENT_DESCRIPTOR_CREATED = NO
GIT_STAGE = NO
GIT_COMMIT = NO
GIT_PUSH = NO
```

## R. Risks/unknowns and next exact Human-PI decisions

Real environment buildability, installed dependency/system-package adequacy,
current Docker/base-image presence, network enforcement, durable filesystem
behavior, production integration, environment readiness, oracle compatibility,
scientific eligibility and capacity are unestablished. The ledger/controller is
proposal-level and source-function rebinding is tested without invoking export.
No candidate-only evidence is promoted to runtime or scientific qualification.
The two literal matplotlib blockers remain unchanged and require their own
later exact Human-PI supersession if any executable operation is desired.

Recommended next action is Human-PI review of this exact file/hash package,
with separate decisions on (1) runtime/input-binding and once-only protocol,
(2) ENVIRONMENT_MATERIALIZATION record, (3) IMAGE_BUILD record,
(4) BUILD_NETWORK exact 583-item/source/enforcement/evidence record and
(5) PERSISTENT_EVIDENCE_OUTPUT proposed root/paths. All acceptance fields are NO.
Any accepted decisions must be bound to these exact record/file/population SHAs.
Then separately authorize the implementation/durable-runtime closure, freeze /
commit/publication steps and event/effectivity/install sequence described in M/N.
The current lifecycle gate does not grant those actions, and this run stops here.

Missing Human-PI acceptance of finite new candidate permissions is not classified
as a technical package BLOCK. The package is ready for review; preparation
execution and transition construction remain unactivated.

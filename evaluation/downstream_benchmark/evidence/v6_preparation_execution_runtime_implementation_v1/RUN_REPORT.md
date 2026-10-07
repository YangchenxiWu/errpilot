# Run Report — V6 preparation runtime implementation and qualification candidate

Date: 2026-10-06 (Europe/Budapest). Status: **V6_PREPARATION_EXECUTION_RUNTIME_IMPLEMENTATION_READY_QUALIFICATION_BLOCKED**.

Task summary: integrated exact accepted V6 input selection, single-item shared-engine transport, authority/default-deny checks and durable once-only claim/terminal I/O. Source, local-base, synthetic engine and target-filesystem checks passed. Restricted default-network enforcement remains unprovisioned and unqualified for 583 work items; that subtask stopped within the explicit boundary. This is an implementation candidate, with no real preparation or event #3 authority.

## A. Entry / authority

Repository `/Users/wuyangchenxi/errpilot`, branch `main`; initial and final local HEAD and measured live origin/main were `5c007fbfbfc5b3529105a14f87127f50e1eab6d7`. Initial tracked worktree/index were clean. The requested planning descriptor SHA is `6a9028c79aa62f90db2b2d53def32ab23bffcfa3c71d2ec30d7fa64e741e3aae`; state PREPARATION_PLANNING_AUTHORIZED, event_count 2, 433 unstarted cases, zero attempts and environment identities. Planning is YES; execution, materialization lifecycle, acquisition, image build and oracle flags remain NO.

Entry initially contained the accepted 14 files plus `.RUN_REPORT.md.swp`. The user explicitly authorized moving that editor artifact to `/private/tmp/errpilot-v6-runtime-swap-backup-20261006-01a1119d/.RUN_REPORT.md.swp` and continuing. SHA at both sides of the move: `ac1b06578303e6b9b05fa2a96f0515c456b19b98ccb0923667a082db62f0fc29`. Vim PID 90367 had it open; it was not terminated. After the move, exactly the accepted 14 untracked files remained before transaction authoring. All accepted file hashes were rechecked, including the report. No unrelated path was removed or overwritten. `.airos/current_state.md` and repository AGENTS.md were absent; the user-supplied global rules and pasted transaction governed this run.

## B. Accepted package bindings

All provided file identities, all 13 inventory-bound artifacts and the inventory itself match. Canonical semantic identities use sorted compact UTF-8 JSON with one LF, exactly as the accepted adapter specifies. Common binding `68e9335a77d7b1f86ea1cfa2341cf44a9a1c716b1938f52806b151de2218b80d`; population `f3a719f2a92f1d1ba96baa9dd3936e8bd87d330f048542c9ee5cfce86185a800`. Candidate authority bytes stayed unchanged.

| Accepted package path | SHA-256 |
| --- | --- |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/RUN_REPORT.md` | `41e7499ad88d78611a1f3859ad20c2dff6a951859bb4cc021c61b3e686ee48e2` |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/adapter_candidate.py` | `0246d455fee259486640fd0d10451af864532a6b22131a73c40eac157da04808` |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/artifact_sha256.json` | `e5470a6dd48350717008350d9bc665f902ad41e747925ec892b3bd86c60466f8` |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/authority_candidates.json` | `13c4c6753263b0657bca1c49122f4f73e27254c5c5d30e7d4c158f9782cf6360` |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/construct_package.py` | `ebfbc3094bdf614d8694533b839167df066e1a10e3f0580372f7493db7776676` |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/controller_candidate.py` | `3f7086db4ac791ecc81b3032f9844f909fd8baad1835f3bf60ee93cbd52879dc` |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/entry_verification.json` | `833591f35c5ee49ba287a9282e57b51fd6ac0fa1d24966d035f1952831772e72` |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/ledger_candidate.json` | `5d1f10f5fa28860d7eb47a3a56a092c2492e2a90b440904990e44a8cf014d7bc` |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/revalidate_sources.py` | `c1e3cd31607de167eaf0109aa0859312b480ee8c4d8dc79f85d1c8b0c6ebf30a` |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/revalidation.json` | `fd260c14dff347de4577b253037e4a528691fa3dc4286de5ad49a174d342d3e9` |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/test_candidates.py` | `255296243650e63d14b87c58f6d4c543fbfc88ce637482d8698768a779d9e9e5` |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/validate_package.py` | `d8dbb9f61516d68d9a3df9309888efb554e9e648776b32065d5c3a0497049d74` |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/validation_results.json` | `b9226116bb4320c7e35221691ffbb20bf3034e2d0498f29995b8c57b4c49294c` |
| `evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/work_items_candidate.json` | `288eaed9f7e9ff4daf2978e7c41b6c6ead83e9d99b9ddee7801c163153bd63bb` |

## C. Human-PI acceptance record

Created `evaluation/downstream_benchmark/V6_PREPARATION_EXECUTION_RUNTIME_AUTHORITY_ACCEPTANCE_V1.json`. SHA-256: `5bff21c82ad11a80882a160c4dfb79e06bd4c249f769424d5047493fdf442861`. It binds the exact request file/hash, full accepted package, common/population identities, runtime input binding and once-only protocol, four independently accepted permission semantic hashes, exact output root, SOURCE_ACQUISITION_AUTHORIZED=NO and conditional network effectivity. It explicitly retains canonical execution effectivity NO, no event #3 grant, no real preparation in this transaction and no commit authority.

The independently accepted semantic hashes are ENVIRONMENT_MATERIALIZATION `9d26db1b5b8c2651677f65c2d5e8fa6aa1b1aea46b3fdf2e7eb3e7bf87011c34`; IMAGE_BUILD `a95e1615a4a757da70dd968cc15541dadc056a402ce3f0474aaad02adc96820b`; BUILD_NETWORK `42393faa33851396fd70557558fa0e538f817fbee9072d0d56ec9d9323fc21a1`; PERSISTENT_EVIDENCE_OUTPUT `101db1b51f5cd6699a892f763ed56353f514345af287a6840fbbf8b6cf70214d`.

## D. Production runtime implementation / files changed

Three isolated V6 modules were added. The adapter projects accepted bytes and retains stable attempt identities from the exact immutable planning descriptor in Git. The runtime requires every selector identity, a separately installed execution descriptor/pin and runtime installation, exact acceptance and permission scopes, unchanged shared mechanics, clean committed implementation bytes and exact live publication. It checks local sources/base before claims; claims are revalidated immediately before persistence. Its CLI requires an explicit request. The ledger writes immutable records and never automatically reclaims or retries.

| New production path | SHA-256 |
| --- | --- |
| `evaluation/downstream_benchmark/screening/v6_preparation_adapter.py` | `9cab10b07922492bb4401b4e245d1a47034041bd5e018c88eaa2960b4b4c2402` |
| `evaluation/downstream_benchmark/screening/v6_preparation_ledger.py` | `d64dc5c742d7857e4dcf4f350bc3db4571d679ea9a74a3c4303085ad10bd0dd7` |
| `evaluation/downstream_benchmark/screening/v6_preparation_runtime.py` | `70afd185d8e6dc6083fdec0580e1ef7a0ff1098841d9ad02192df937a76e2355` |

No preexisting tracked file ended with a diff. The shared materializer and source exporter were preserved byte-for-byte. V6 binds the same shared code objects into a private function namespace, adding a Docker transport guard for exact network=none and pull=never probes. It does not install another builder or change shared globals, Dockerfiles, recipe/setup bytes, blockers or predecessor authorities. Restricted default-network dispatch has an unconditional rejection until a separately authorized scoped enforcement integration exists. A new focused test file and bounded evidence/qualification scripts accompany the modules; complete paths/hashes are in `implementation_inventory.json` and `artifact_sha256.json`.

## E. Exact work population

All 641 work items were mechanically rederived and their ordered complete semantic identity matched: 221 SOURCE_INDEPENDENT, 210 BUGGY and 210 FIXED, from 431 dispatchable cases. All 641 field projections/proposals were checked without invoking benchmark operations. Exactly 583 require restricted build-network permission; 58 stay NONE. Both `matplotlib::1` and `matplotlib::8` reject. Their blockers and the full 433-case scientific state remain exact.

## F. Durable once-only ledger

UNSTARTED → exclusive writer lock and durable claim → one durable terminal. Lock/claim creation uses O_CREAT|O_EXCL|O_NOFOLLOW, full writes, file fsync and parent-directory fsync. Terminal publication fsyncs a new partial inode, atomically links it to the final name with exclusive no-overwrite semantics, fsyncs the directory, then removes only the temporary link and verified current writer lock. Claims/terminals are never removed or replaced. A claim, lock, malformed record or orphan partial blocks another dispatch. A crash after terminal publication cannot enable another dispatch.

Final actual-target qualification: 11 focused tests, zero failures/errors/skips. It exercised two-process claim contention, terminal without claim, duplicate claim/terminal, success/failure/interruption overwrite rejection, partial/orphan states, no reclaim/retry, fsync and hard-link atomic nonreplacement. It also verified safe V2 symlink preservation, rejected an escaping negative fixture and rejected a fabricated real admission before any real claim. These are synthetic filesystem/mechanics observations, not a physical power-loss experiment.

## G. Persistent output root

Initialized only `/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1`. Left namespace metadata, empty real ledger directories, and explicitly synthetic qualification subtrees. No real attempt, input or snapshot directory was created. Actual external artifact hashes were measured separately in `external_artifact_sha256.json` (103 files/symlinks). Deliberately malformed/orphan/unsafe-link records are preserved as negative fixtures under qualification and labelled in that inventory.

`persistent_output_qualification.json` binds concrete synthetic claim/terminal, input/controller binding, Dockerfile/context, source manifest or ABSENT, raw build log, image inspection/Python probe, installed distributions, environment identity, failure/interruption and network NONE provenance to exact external paths/hashes. Restricted-egress request/provenance outputs remain unqualified.

## H. Seven frozen local base runtimes

No pull or substitution command was issued. All seven already-local immutable references were independently inspected and probed with network=none/pull=never for exact Python patch, x86_64 platform and executable SHA. All passed; zero missing-base work items. Read-only installed-pip configuration/default probes matched the accepted PyPI index scope in all seven, without outputting credentials. This does not qualify actual dependency installs or egress confinement.

| Python | Frozen reference | Local status / identity probe | Affected items |
| --- | --- | --- | --- |
| 3.6.9 | `docker.io/library/python@sha256:036d4ab50fa49df89e746cf1b5369c88db46e8af2fbd08531788e7d920e9a491` | LOCAL_PRESENT / PASS | 38 |
| 3.7.0 | `docker.io/library/python@sha256:8c386ccc41ce94c90bce07bae67a06c9d814153e6a9a9094c1257dfcd04c9657` | LOCAL_PRESENT / PASS | 49 |
| 3.7.3 | `docker.io/library/python@sha256:e3e087ca7fe013554b3a8b8d4088ab33a9f13af85b5c3f37cd4e69a8e53f14e1` | LOCAL_PRESENT / PASS | 41 |
| 3.7.4 | `docker.io/library/python@sha256:5be0532f833568d838b7b2d8726b66d0b8abe26f50a15b566aea4611d5951eac` | LOCAL_PRESENT / PASS | 30 |
| 3.7.7 | `docker.io/library/python@sha256:f261d8fbee60f434341b7370fe0e5f3bea0deb0976ad323f0294d7dd694a9426` | LOCAL_PRESENT / PASS | 12 |
| 3.8.1 | `docker.io/library/python@sha256:1d24b4656d4df536d8fa690be572774aa84b56c0418266b73886dc8138f047e6` | LOCAL_PRESENT / PASS | 24 |
| 3.8.3 | `docker.io/library/python@sha256:ba23c4870854aa0718113e8765e7f46acbf141c6be1e66957ddcf130bd88d59d` | LOCAL_PRESENT / PASS | 447 |

## I. Restricted build-network enforcement

**RESTRICTED_BUILD_NETWORK_ENFORCEMENT_BLOCKED — 583 exact items.** Installed Docker Desktop has only docker-driver default/desktop-linux builders and ordinary bridge/host/none networks. The accepted shared engine emits `--network=default` for network-required items. Neither that mode nor a proxy environment variable enforces origin restrictions; NONE cannot supply allowed dependency traffic. No qualified scoped mechanism is installed. The accepted default-network path would require daemon/default-network policy mutation, or a separately reviewed scoped integration/tooling authority; the prohibited broader mechanisms were not attempted.

Accepted policy identity (declarative, not enforcement): `0a49cbc497d36683b9fe197c341e0ade6cf8a5cb446a7ac99fe74f5b55808c58`. Installed/qualified enforcement identity: **ABSENT**. Allowed origins remain exactly `https://pypi.org/simple/` and `https://files.pythonhosted.org/`; execution/oracle network stays NONE; registry acquisition is not authorized. This run performed zero network/host firewall/daemon policy mutations, third-party installs, or bounded live allow/deny requests. Controlled transport-negative fixtures passed; they establish rejection by the V6 transport, not real restricted-egress confinement. Exact builder/network inspection bytes and hashes are in `network_enforcement_qualification.json`.

## J. Synthetic materializer/image qualification

The guarded shared engine built only existing SYNTHETIC_A/B/F fixture inputs, with RUN network NONE and already-local bases. A materialized one source-independent image; B materialized distinct BUGGY/FIXED images and source/context identities; F made one expected no-index build fail, retaining its raw log; G exercised interruption before build. Total synthetic Docker build calls: four; successful fixture image identities: three. Distribution/environment observations use the shared mechanics. No subject/oracle test or real benchmark dependency/source operation ran. `external_docker_changes.json` records the new synthetic image IDs and exact build argv.

One qualifier defect loaded G's extension JSON without resolving its base, causing KeyError before Docker for G. The surviving synthetic claim and partial output were preserved, then explicitly observed as INTERRUPTED. A new synthetic G identity exercised the corrected loader and shared interruption; the original identity was not rerun. An initial reconciliation address incorrectly named already-terminal F and was rejected without overwrite, then the surviving G was resolved by exact records. Initial Ruff unused-name issues and a mocked missing-image response error were corrected. `qualification_corrections.json` preserves these facts. Completed A/B/F terminals were not changed or rebuilt.

## K. Production default-deny result

Real dispatch was tested with the exact accepted item and runtime acceptance while claim/Docker entry were forbidden by test guards: REJECT. The installed event #2 planning descriptor rejects as an execution descriptor. Future installation and independent execution pin are absent and were not created. Dirty/uncommitted candidate state cannot satisfy runtime admission. Even a fabricated Admission object cannot produce a real claim because authority is revalidated from installed files. All 583 restricted-network items independently reject regardless of a caller's claimed qualification. There is no retry, predecessor-token, fallback or governed-batch entry.

## L. Validation / rejection matrix

Final focused tests: 11 passed, zero failures/errors/skips. Ruff, AST/static checks, strict duplicate-key/canonical JSON, UTF-8/LF/no BOM/no NUL/trailing whitespace and git diff --check passed. Bare CLI invocation returned expected exit 2 without a request. Exact source revalidation passed for 15 mirrors, 866 revision bindings and 61,333 required leaf blobs, with zero missing objects/acquisition/exports; full planning event/effectivity replay passed. It used only local read-only Git commands (2,851 counted source/replay calls).

`validation_results.json` maps every requested rejection class to the focused tests. Missing source/base coverage uses controlled negative fixtures and the local-base inventory; it does not pretend a missing real object was repaired. No full repository suite, benchmark subject/oracle suite, real dispatch, restricted-network live qualification or scientific validation was performed.

## M. Exact repository inventory

The accepted 14 untracked activation files stayed exact. All 615 preexisting tracked byte identities and raw index SHA stayed exact. New transaction paths consist only of the acceptance record, three V6 modules, focused tests and the bounded requested evidence subtree. `artifact_sha256.json` lists every new repository file, including this report, with exact hashes; its own self-hash is excluded to avoid a cycle. The final artifact inventory hash is observed separately after finalization. Nothing was staged, committed or pushed.

## N. External changes

The accepted persistent root contains only documented namespace structure and qualification evidence. Full no-follow file/link hashes and zero real claims/terminals/attempts/inputs/snapshots are recorded separately. Three fixture-only images were retained; probes used transient --rm containers. The explicitly authorized swap backup remains under /private/tmp; it was measured separately and has no repository hash claim. No source mirror, predecessor output root, repair workspace, host firewall or daemon policy was changed. External negative fixtures intentionally preserve incomplete records rather than cleaning them.

## O. Risks and unknowns

Restricted egress for 583 work items is unimplemented/unqualified under existing authorized tooling. Denial-of-arbitrary-egress, allowed live-origin connectivity and package/request provenance therefore remain unestablished. The 58 NONE items are mechanically supported but still cannot dispatch before review, commit/publication and exact event #3/effectivity/install closure. Future event #3 admission is checked against the pinned baseline and deterministic three-leaf delta; a positive real successor/installation was not fabricated or executed here. Fresh local sources/bases must be rechecked at future admission. Successful synthetic mechanics/fsync calls do not establish real case buildability, physical power-loss durability, environment readiness, oracle compatibility, scientific eligibility or capacity.

## P. Firewall

```json
{
  "REAL_PREPARATION_ATTEMPTS_CONSUMED": 0,
  "PREPARATION_EXECUTED": "NO",
  "ENVIRONMENT_READY_CASES_ESTABLISHED": 0,
  "REAL_BENCHMARK_SOURCE_EXPORTS": 0,
  "SOURCE_ACQUISITION_EXECUTED": "NO",
  "REAL_BENCHMARK_IMAGE_BUILDS": 0,
  "ORACLE_EXECUTED": "NO",
  "EVENT_3_CREATED": "NO",
  "CANONICAL_CURRENT_STATE_MODIFIED": "NO",
  "PREPARATION_EXECUTION_CANONICAL_EFFECTIVE": "NO",
  "GIT_STAGE": "NO",
  "GIT_COMMIT": "NO",
  "GIT_PUSH": "NO"
}
```

## Q. Event #3 readiness

**NO.** No event #3 or successor descriptor was constructed; canonical bytes are unchanged. The retained future delta is only projection.state planning→execution, projection.lifecycle.PREPARATION_AUTHORIZED NO→YES and projection.phase_authorizations.PREPARATION_EXECUTION NO→YES. No case state changes are permitted at activation. Qualification, review, implementation persistence/publication and separate event/effectivity/install/pin gates remain open.

## R. Recommended next Human-PI action / contract compliance

Review this exact uncommitted implementation/evidence package and decide the separately scoped deny-by-default enforcement mechanism and any new tooling/policy authority needed to implement it. Then qualify that mechanism and the 583-item restricted path before accepting full runtime readiness. Commit/publication, event #3 construction, effectivity binding, canonical compare/install, final independent descriptor pin and real dispatch each require their separate later authority. No new gate name, acceptance, merge or scientific decision is inferred by this recommendation.

The transaction complied with its implementation/synthetic-only write scope and no-commit/event firewall. The network subtask stopped at the explicit external-prerequisite boundary without weakening the policy. This run stops after delivering the candidate and qualification blocker.

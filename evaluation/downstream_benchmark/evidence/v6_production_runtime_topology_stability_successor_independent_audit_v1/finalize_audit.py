"""Final exact preservation replay, report, and non-self-referential audit seal."""
import ast
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('audit_entry',HERE/'audit_entry.py')
e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
ROOT=e.ROOT;CAND=e.CAND
entry=json.loads((HERE/'entry_snapshot.json').read_bytes())
assert e.git('rev-parse','HEAD').strip()==e.EXPECTED_HEAD
assert e.git('branch','--show-current').strip()=='main'
assert e.git('diff','--name-only')==e.git('diff','--cached','--name-only')==''
tracked=e.git('ls-files','-z').split('\0')[:-1]
assert {p:e.identity(ROOT/p) for p in tracked}==entry['tracked']
assert e.identity(ROOT/'.git/index')==entry['index']
for package,old in entry['packages'].items():
    root=HERE.parent/package
    current={str(f.relative_to(root)):e.identity(f) for f in sorted(root.rglob('*')) if f.is_file()}
    assert current==old['files']
remaining=[p for p in e.git('ls-files','--others','--exclude-standard','-z').split('\0')[:-1]
           if not p.startswith(str(HERE.relative_to(ROOT))+'/')]
assert remaining==entry['preexisting_untracked']
print('Hashing all persistent output for final equality',flush=True)
after=e.tree(Path(entry['persistent_root']))
assert after==entry['persistent_tree']
targets=json.loads((HERE/'entry_verification.json').read_bytes())['production_targets_absent']
assert all(not (ROOT/p).exists() for p in targets)
for path in HERE.rglob('*.py'):
    ast.parse(path.read_text())
assert not any(p.is_symlink() for p in HERE.rglob('*'))
preservation={'status':'PASS_EXACT_BYTES_PATHS_TYPES_MODES','tracked_files_exact':1065,
    'Git_index_bytes_exact':True,'local_HEAD':e.EXPECTED_HEAD,'live_origin_main_exit':e.EXPECTED_HEAD,
    'live_remote_evidence':'Independent read-only git ls-remote origin refs/heads/main, successful exit 0 at entry and exit; no fetch/push.',
    'predecessor_files_exact':572,'candidate_files_exact':44,'preexisting_untracked_files_exact':616,
    'canonical_sha256':'e48580c1f9769d1b93ab995e6dcef3689c6920a9ce7b83f728526e9694dc68fd',
    'state':'PREPARATION_EXECUTION_AUTHORIZED','event_count':3,
    'real_ledger':{'UNSTARTED':641,'claims':0,'terminals':0,'retries':0,'orphans':0},
    'complete_persistent_output_including_qualification_exact':True,
    'persistent_entries':len(after),'persistent_files':sum(v['type']=='file' for v in after.values()),
    'persistent_file_bytes':sum(v.get('size_bytes',0) for v in after.values()),
    'production_targets_absent':targets,'only_new_write_namespace':str(HERE),
    'Docker_operations':0,'network_in_test_processes':0,'real_source_acquisitions':0,'real_receipts_claims_attempts':0,
    'topology_cleanup':0,'Git_stage_commit_push':0,'real_client_authorization':'BLOCKED',
    'live_Docker_topology_certified':False}
e.write('preservation_verification.json',preservation)

def update(name,values):
    p=HERE/name;x=json.loads(p.read_bytes());x.update(values)
    p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')

receipt=json.loads((HERE/'receipt_independent_replay.json').read_bytes())
update('receipt_sidecar_crash_audit.json',{'additional_receipt_replay':{'path':str(HERE/'receipt_independent_replay.json'),
    'sha256':e.sha(HERE/'receipt_independent_replay.json'),'independent_rejection_count':len(receipt['rejections'])}})
update('validation_results.json',{'preservation':'PASS_EXACT_BYTES_PATHS_TYPES_MODES','receipt_independent_negative_checks':len(receipt['rejections']),
    'audit_source_AST_parse':'PASS','final_status':'V6_PRODUCTION_RUNTIME_TOPOLOGY_STABILITY_SUCCESSOR_INDEPENDENT_AUDIT_BLOCKED'})
e.write('commands_run.json',{
    'read_only_inventory':['pwd','rg --files / rg -n for repository instructions, source functions and constraints',
        'cat/sed/nl for attached request, exact candidate/controller/provider/qualifier/contracts, ledger and shared materializer',
        'git status --short','git rev-parse HEAD','git rev-parse origin/main','git ls-files (tracked/untracked)',
        'git diff --quiet / git diff --cached --quiet','git remote get-url origin',
        'git ls-remote origin refs/heads/main (initial sandbox DNS failure; then read-only escalation succeeded; exit verification succeeded)'],
    'audit_namespace_writes':['mkdir exact new audit namespace','apply_patch audit-owned Python helpers only',
        'cp audit_checks.py audit_checks_revision_1.py and audit_checks_revision_2.py to preserve diagnostic revisions'],
    'executed_python_commands':['.venv/bin/python -B '+str(HERE/filename) for filename in (
        'audit_entry.py','audit_checks.py','audit_additional_checks.py','assemble_audit.py','audit_receipts.py','finalize_audit.py')],
    'checks_runs':[{'run':1,'result':'HARNESS_ERROR after successful complete external/scientific replay: security fixture referenced before construction; traceback and exact script preserved'},
        {'run':2,'result':'HARNESS_ERROR: /dev/null diagnostic sink denied by audit guard, producing INTERRUPTED synthetic terminals; exact artifacts/log/script retained; not counted as candidate failure'},
        {'run':3,'result':'COMPLETED; root confinement counterexample, three expected E2E results, 23 security rejection probes plus correlation counterexample, ten injected crash boundaries'}],
    'additional_checks':'COMPLETED: full preclaim/provider endpoint contradiction; four partial-publication failures retained and blocked',
    'receipt_checks':f'PASS retained RESTRICTED/NONE associations and {len(receipt["rejections"])} rejections',
    'no_author_main_execution':'Original qualifier main/finalizer/constructors which write sealed outputs were not run. Exact candidate library constructors/functions were invoked with bounded synthetic fixtures; no candidate source was edited.',
    'safety':'No dependencies installed, no GUI, no Docker. Test subprocess allowlist contained only exact local git cat-file planning blob and git rev-parse HEAD.'})

ids=json.loads((HERE/'candidate_identities.json').read_bytes())
report=f'''# Run Report — independent exact V6 successor audit

STATUS = `V6_PRODUCTION_RUNTIME_TOPOLOGY_STABILITY_SUCCESSOR_INDEPENDENT_AUDIT_BLOCKED`

The exact sealed candidate is **not eligible for Human-PI acceptance or lifecycle freeze**. Independent review found **2 MATERIAL, 1 MINOR, 0 OPTIONAL** findings. The candidate and all predecessor BLOCK evidence remain unchanged. This audit makes no acceptance, installation, release, scientific-validation or execution decision.

## 1. Task summary and exact identities

Transaction: INDEPENDENT_EXACT_CANDIDATE_AUDIT_ONLY. Current Human-PI review gate: HUMAN_PI_REVIEW_OF_V6_PRODUCTION_RUNTIME_TOPOLOGY_STABILITY_SUCCESSOR_CANDIDATE.

| Artifact | Exact SHA-256 |
|---|---|
| Candidate package manifest, 43 payloads + 1 manifest | `{ids['candidate_manifest']['sha256']}` |
| Controller | `{ids['controller']['sha256']}` |
| Provider | `{ids['provider']['sha256']}` |
| Successor installation candidate | `{ids['installation_candidate']['sha256']}` |
| Successor installation plan | `{ids['installation_plan']['sha256']}` |

Both local HEAD and independently queried live origin/main equal `{e.EXPECTED_HEAD}`. Canonical SHA is `{preservation['canonical_sha256']}`, state PREPARATION_EXECUTION_AUTHORIZED, event_count 3. No `.airos/current_state.md` or repository AGENTS.md was present. The attached direct audit request and supplied global rules were applied.

## 2. Files inspected and changed

Read the exact controller/provider/qualifier, V2 security/client/raw/receipt contracts and schemas, original ledger and shared materializer, installation candidate/plan, source deltas, sealed qualification outputs, historical provider/controller references and predecessor manifests. Replayed every payload path, size and SHA for the 44 candidate and 572 predecessor files. Replayed all 613 final external qualification files across 62 fixtures and inspected canonical claim/terminal/receipt/association bytes and artifact hashes. Complete file/AST identities and source diffs are retained in this audit.

All new files are confined to `{HERE}`. Added the requested 15 named outputs plus reproducible audit scripts, exact snapshots, bounded synthetic fixtures, run logs, source diffs and supporting results. No existing candidate/predecessor/tracked file changed. Failed audit-harness revisions and their logs are retained; they are not candidate findings.

## 3. Commands run

Read-only Git HEAD/index/status/diff/file-list checks and `git ls-remote origin refs/heads/main` at entry and exit; bounded file reads, streaming SHA-256 and Python AST comparison. Ran `audit_entry.py`, `audit_checks.py` (three preserved revisions/runs), `audit_additional_checks.py`, `assemble_audit.py`, `audit_receipts.py` and `finalize_audit.py` with `.venv/bin/python -B`. See `commands_run.json` and run logs. No dependency installation, Docker, source acquisition, build, GUI, Git stage/commit/push or topology cleanup was performed.

## 4. Tests and findings

**F01 — MATERIAL: synthetic root confinement fails.** `Authority.__init__/refresh` and downstream guards use lexical `Path.is_relative_to` without rejecting `..`. Normal unchanged candidate constructors accepted an escaped qualification-root spelling resolving inside this audit, outside the mandated qualification root. RESTRICTED/NONE synthetic terminals and failure terminal were durably published there. No module globals, source paths or constructors were forged. This is a filesystem boundary failure; production authorization was not bypassed. Evidence: `isolation_reproduction.json`.

**F02 — MATERIAL: raw socket Path is not bound to attributed endpoint.** `verify_clients` matches connected inode lists but does not reconcile each row's Path with the session/provenance endpoint. Changing connected inode 3697 to `/tmp/unknown-control.sock` while proofs still identify `unix:///run/buildkit/buildkitd.sock` left the accepted security projection unchanged; both controller claim and provider revalidation accepted the contradiction. No unknown listener was added. Evidence: `client_endpoint_correlation_reproduction.json`.

**F03 — MINOR: inherited category semantics are mislabeled.** The `runtime_authority_false` test sets integer `0` in a synthetic V2 receipt which correctly expects Boolean `false`. It therefore tests canonical type distinction rather than the former real-authority Boolean gate. Generic exception capture does not assert the intended reason. Evidence and bounded disposition are in `findings.json`.

Receipt crash-safety disposition: ten requested interruption points and four partial-file write failures retained evidence, rejected reentry and performed no overwrite. Before the lock, a preclaim sidecar directory may coexist with Ledger.state=UNSTARTED, but actual claim reentry rejects. After lock/partial claim or terminal, orphan/parse/partial guards reject. These are bounded code-level injection results; **storage power-loss durability is not established**. The author's sealed qualifier contains no equivalent crash-point injection suite. See `receipt_sidecar_crash_audit.json`.

Receipt checks: canonical original bytes/schema, entire immutable work/attempt/source/effectivity binding, cross-attempt rejection, NONE/null semantics and durable association/claim readback passed; {len(receipt['rejections'])} independent negative receipt checks rejected.

Synthetic execution disposition: the original shared `_materialize_checked` code object was traced three times with simulated transport, and legacy globals stayed unchanged. Audit hooks confined resolved writes to this audit and denied all sockets and runtime/source/install subprocesses. Only exact read-only Git queries were allowed. This supports simulated I/O behavior for exercised paths, while **synthetic root isolation fails F01**. These diagnostic E2Es must not be relabeled as successful intended-root isolation qualification.

Both 24-entry A–X mappings and all 126 recorded rejection outcomes (77 inherited + 49 new) were reviewed against actual test source and exact evidence. No mandatory skipped case was observed. Most negative cases have meaningful mutation/rejection/ledger assertions; the complete 126-case author main was not rerun because it writes sealed candidate/external namespaces. The category-name reuse limitation is F03, and F01/F02 are uncovered security cases. Positive retained RESTRICTED/NONE terminals are MATERIALIZED, with 21 artifact hashes each; retained provider failure is INTERRUPTED with `RuntimeError: SYNTHETIC_PROVIDER_FAILURE`. Full qualification acceptance is blocked by material findings.

Independent scientific replay passed all 641 exact work IDs: 221 SOURCE_INDEPENDENT, 210 BUGGY, 210 FIXED; 583 RESTRICTED and 58 NONE. Population file SHA `288eaed9f7e9ff4daf2978e7c41b6c6ead83e9d99b9ddee7801c163153bd63bb`, semantic SHA `f3a719f2a92f1d1ba96baa9dd3936e8bd87d330f048542c9ee5cfce86185a800`, ordered IDs SHA `7a329a4c301e5ddd6bae1047f6bce77430aca5a21d71a7a749dfb3899e4c7a5c`. Full scientific/execution Dockerfile bytes and native argv match historical, corrected and successor implementations for every item. matplotlib::1 and matplotlib::8 remain blocked. No scientific eligibility or environment-ready inference is made.

The 11-node, 10-edge supersession graph and every referenced file identity pass independent acyclic replay. Actual successor controller/provider/candidate/plan pins are exact; historical V1 pins are marked predecessors. candidate_only=true, HUMAN_PI_ACCEPTED=NO, runtime_effective=NO, execute_now=false. Future effectivity remains unconstructed.

## 5. Contract compliance and preservation

All 1065 tracked files, Git index bytes, HEAD, canonical/event chain, exact 572 predecessor files and 44 candidate files are unchanged. Complete persistent output, including the original qualification tree, matches entry: {preservation['persistent_entries']} entries, {preservation['persistent_files']} files, {preservation['persistent_file_bytes']} bytes. All specified production targets are absent. The full persistent ledger remains **641 UNSTARTED, 0 claims, 0 terminals, 0 retries, 0 orphans**. Only synthetic audit-owned attempts exist in the new audit namespace. No real receipt, claim, attempt or execution occurred.

## 6. Risks, assumptions and unknowns

Real-client authorization remains **BLOCKED**. No current Docker topology, live client provenance, live observer or actual host isolation was inspected or certified. Trusted live observer construction and accepted effectivity remain future gates. Fault injection covers selected source-level boundaries, not arbitrary machine power loss. Source/output review establishes the sealed recorded test outcomes; it is not a fresh rerun of every historical rejection. The diagnostic root traversal is an explicit counterexample, never an authorization mechanism for real outputs. Audit harness revisions 1 and 2 failed for fixture ordering and `/dev/null` denial respectively; successful revision 3 and all retained evidence are distinguished.

## 7. Recommended next action

Human-PI should adjudicate F01/F02 and the F03 mapping limitation, then separately authorize a bounded successor remediation/requalification/reseal if desired. Preserve this exact candidate and all predecessor BLOCK packages. No finding was fixed in this transaction. The PASS next gate is not asserted; no acceptance, lifecycle closure, production installation or real execution is authorized by this audit.

`artifact_sha256.json` seals every audit payload path, byte size and SHA, excluding only itself. Its self SHA and exact counts are returned externally after complete replay to avoid a self-reference cycle.
'''
(HERE/'RUN_REPORT.md').write_text(report)
required=['entry_verification.json','exact_candidate_inventory.json','security_audit.json','client_authorization_audit.json',
    'receipt_sidecar_crash_audit.json','source_delta_audit.json','synthetic_isolation_audit.json','qualification_coverage_audit.json',
    'scientific_integrity_audit.json','supersession_graph_audit.json','preservation_verification.json','findings.json','validation_results.json','RUN_REPORT.md']
assert all((HERE/name).is_file() for name in required)
files={str(f.relative_to(HERE)):{'size_bytes':f.stat().st_size,'sha256':e.sha(f)} for f in sorted(HERE.rglob('*')) if f.is_file() and f!=HERE/'artifact_sha256.json'}
seal={'schema':'V6_SUCCESSOR_INDEPENDENT_AUDIT_ARTIFACT_SHA256_V1','status':'V6_PRODUCTION_RUNTIME_TOPOLOGY_STABILITY_SUCCESSOR_INDEPENDENT_AUDIT_BLOCKED',
    'candidate_only':True,'HUMAN_PI_ACCEPTED':'NO','runtime_effective':'NO','execute_now':False,
    'payload_count':len(files),'total_file_count':len(files)+1,'excluded':['artifact_sha256.json'],'files':files,
    'self_sha256_semantics':'SHA256 exact manifest bytes, reported externally; no self-reference'}
e.write('artifact_sha256.json',seal)
current={str(f.relative_to(HERE)):{'size_bytes':f.stat().st_size,'sha256':e.sha(f)} for f in HERE.rglob('*') if f.is_file() and f!=HERE/'artifact_sha256.json'}
assert current==files
assert len([f for f in HERE.rglob('*') if f.is_file()])==len(files)+1
print(json.dumps({'status':seal['status'],'payload_count':len(files),'total_file_count':len(files)+1,
    'audit_manifest_sha256':e.sha(HERE/'artifact_sha256.json'),'preservation':'PASS','findings':{'MATERIAL':2,'MINOR':1,'OPTIONAL':0},
    'real_ledger':preservation['real_ledger'],'report':str(HERE/'RUN_REPORT.md')},sort_keys=True))

"""Assemble independent findings and reproducible structural audit evidence."""
import ast
import difflib
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CAND = HERE.parent / 'v6_production_runtime_topology_stability_successor_resume_v1'
OLD = HERE.parent / 'v6_preparation_execution_production_runtime_installation_resume_v1'
CORRECTED = HERE.parent / 'v6_production_runtime_image_identity_compatibility_bridge_v1/corrected_production_provider_candidate.py'
STATUS = 'V6_PRODUCTION_RUNTIME_TOPOLOGY_STABILITY_SUCCESSOR_INDEPENDENT_AUDIT_BLOCKED'

def read(path):
    return json.loads(path.read_bytes())

def ref(path):
    raw = path.read_bytes()
    return {'path': str(path), 'sha256': hashlib.sha256(raw).hexdigest(), 'size_bytes': len(raw)}

def write(name, obj):
    with (HERE / name).open('x') as f:
        json.dump(obj, f, sort_keys=True, indent=2); f.write('\n')

def funcs(path):
    result = {}
    for n in ast.parse(path.read_text()).body:
        entries = [(n.name, n)] if isinstance(n, ast.FunctionDef) else (
            [(n.name + '.' + f.name, f) for f in n.body if isinstance(f, ast.FunctionDef)] if isinstance(n, ast.ClassDef) else [])
        for name, node in entries:
            result[name] = {'line': node.lineno, 'end_line': node.end_lineno,
                            'ast_sha256': hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest()}
    return result

sources = {'controller': CAND/'production_controller_successor_candidate.py',
           'provider': CAND/'production_provider_successor_candidate.py',
           'qualifier': CAND/'synthetic_e2e_qualifier.py',
           'installation_candidate': CAND/'successor_installation_candidate.json',
           'installation_plan': CAND/'successor_installation_plan.json',
           'candidate_manifest': CAND/'artifact_sha256.json'}
identities = {k:ref(v) for k,v in sources.items()}
write('candidate_identities.json', identities)
delta = {}
for role, base in [('provider',CORRECTED),('controller',OLD/'production_controller_candidate.py')]:
    before, after = funcs(base), funcs(sources[role])
    changed = sorted(k for k in before if before[k]['ast_sha256'] != after.get(k,{}).get('ast_sha256'))
    delta[role] = {'baseline':ref(base), 'successor':ref(sources[role]), 'before':before, 'after':after,
        'changed':changed,'added':sorted(set(after)-set(before)),'removed':sorted(set(before)-set(after)),
        'preserved':sorted(k for k in before if k not in changed)}
    (HERE/(role+'_independent_source_delta.diff')).write_text(''.join(difflib.unified_diff(
        base.read_text().splitlines(True),sources[role].read_text().splitlines(True),fromfile=str(base),tofile=str(sources[role]))))
assert len(delta['provider']['changed'])==15 and len(delta['controller']['changed'])==5
assert len(delta['provider']['preserved'])==23 and len(delta['controller']['preserved'])==6
assert not delta['provider']['removed'] and not delta['controller']['removed']
write('source_delta_audit.json', {'status':'PASS_EXACT_AST_INVENTORY_WITH_SECURITY_FINDINGS','deltas':delta,
    'inspected_sources':[ref(p) for p in sources.values()],
    'historical_shared_guards_unchanged':'Verified by 1065-file entry and final preservation, plus frozen_inputs SHA guards.',
    'top_level_review':'Imports remain fixed module names. V2 paths/schema/root constants and receipt fields are explicit. No caller-selected import, root or network fallback on production CLI.',
    'production_native_and_scientific_functions':'compile_production_transport, frozen_inputs, image identity functions, normalize_topology, native build/invoke/check, command/layout checks and ProductionProvider.execute AST unchanged from corrected provider.',
    'legacy_monkeypatch':'No object.__new__, __file__ forgery or sys.modules injection in candidate/qualifier. Private shared function binding keeps original code objects; independent trace and shared-global census confirmed.',
    'root_guard_disposition':'FAIL_F01', 'client_correlation_disposition':'FAIL_F02'})

graph = read(CAND/'supersession_dependency_graph.json')
nodes = {n['id']:n for n in graph['nodes']}; indegree={n:0 for n in nodes}; outgoing={n:[] for n in nodes}
for start,end in graph['edges']:
    assert start in nodes and end in nodes and start != end
    indegree[end]+=1;outgoing[start].append(end)
ready=[n for n in nodes if indegree[n]==0]; ordered=[]
while ready:
    n=ready.pop();ordered.append(n)
    for child in outgoing[n]:
        indegree[child]-=1
        if not indegree[child]:ready.append(child)
assert len(ordered)==len(nodes)==11
references=[]
for node in graph['nodes']:
    for r in node['artifacts']:
        actual=ref(Path(r['path']));assert all(actual[k]==r[k] for k in ('sha256','size_bytes'))
        references.append({'node':node['id'],**actual})
candidate=read(sources['installation_candidate']);plan=read(sources['installation_plan'])
for x in (candidate,plan):
    assert x['candidate_only'] is True and x['HUMAN_PI_ACCEPTED']=='NO' and x['runtime_effective']=='NO' and x['execute_now'] is False
assert candidate['source_pair']['controller']==ref(sources['controller'])
assert candidate['source_pair']['provider']==ref(sources['provider'])
assert plan['candidate']==ref(sources['installation_candidate'])
assert plan['unconstructed_future_effectivity'] is True
assert candidate['old_plan_authorizes_new_sources'] is False
write('supersession_graph_audit.json', {'status':'PASS_EXACT_ACYCLIC_BINDINGS','nodes':11,'edges':10,
    'topological_order':ordered,'references':references,'candidate':ref(sources['installation_candidate']),
    'plan':ref(sources['installation_plan']),'stale_V1_source_masquerade':False,
    'historical_V1_refs':'Explicit predecessor references only; new source_pair pins match exact successor bytes.',
    'content_hash_direction':'Contracts do not bind downstream source/result/candidate/plan hashes; source names contracts; qualification pins sources; candidate pins qualification; plan pins candidate; DAG pins nodes; manifest pins all payloads.',
    'future_effectivity':'UNCONSTRUCTED','candidate_only':True,'HUMAN_PI_ACCEPTED':'NO','runtime_effective':'NO','execute_now':False,
    'interpretation':'Acyclic identity graph establishes provenance, not acceptance or security correctness.'})

policy=read(CAND/'client_authorization_contract_candidate.json')
decision=read(CAND/'human_pi_decision.json')
assert policy['C1_C16']==decision['exact_C1_C16']
request=' '.join((CAND/'raw_human_pi_request.txt').read_text().split())
assert all(' '.join(v.split()) in request for v in policy['C1_C16'].values())
control_review={
    'C1':('CONDITIONAL_FAIL_F02','verify_clients covers named surfaces but does not bind each socket row Path to its attributed session endpoint.'),
    'C2':('PASS','Historical clients remain ORIGIN_NOT_ESTABLISHED in decision/contracts; no retrospective attribution.'),
    'C3':('FAIL_F02','Claim and provider accepted contradictory connected-path versus attributed endpoint evidence.'),
    'C4':('PASS_EXPLICIT_UNKNOWN_REJECTION','UNKNOWN and UNAUTHORIZED verdicts reject; independent negative probes confirmed.'),
    'C5':('PASS_EXPLICIT_GATES_WITH_F02_LIMIT','Incomplete census/boundary reject, but contradictory endpoint correlation is not rejected.'),
    'C6':('CONDITIONAL_F02','Production fixed separately reviewed SHA-pinned observer is mandatory; evidence labels alone not externally accepted. Correlation between its raw/provenance outputs remains unchecked for socket Path.'),
    'C7':('PASS','Process-name-only and ExecID-only source kinds rejected in independent checks.'),
    'C8':('FAIL_F02','Session IDs and inode lists are checked; path/endpoint relation is not. Connected Path is dropped from stable projection.'),
    'C9':('PASS_CALL_ORDER_WITH_F02_LIMIT','ProductionAdmission.revalidate before sidecar/lock; verify_claim at provider construction/execution/build. Both call the affected verifier.'),
    'C10':('PASS','Raw source UTF-8, SHA/source/method/timestamp fields retained; claim association replays them.'),
    'C11':('PASS','Distinct raw, stable projection, client-evidence and effectivity identities; V1 schema not relabeled.'),
    'C12':('FAIL_F01_ISOLATION','Synthetic outputs remain labeled synthetic, but ../ escapes qualification root through normal constructor.'),
    'C13':('PASS','Candidate-only package and current real authorization remain BLOCKED.'),
    'C14':('PASS','No accepted/effective V2 descriptor or installed runtime target exists.'),
    'C15':('PASS','No historical client exoneration or cleanup performed or authorized.'),
    'C16':('PASS','No operational remediation performed; separate authority retained.'),
}
write('client_authorization_audit.json',{'status':'BLOCKED_F02','policy':ref(CAND/'client_authorization_contract_candidate.json'),
    'C1_C16':{k:{'requirement':policy['C1_C16'][k],'disposition':v[0],'evidence':v[1]} for k,v in control_review.items()},
    'reproductions':[ref(HERE/'security_check_reproduction.json'),ref(HERE/'client_endpoint_correlation_reproduction.json')],
    'real_client_authorization':'BLOCKED','live_observer_reviewed_or_installed':False})
write('security_audit.json',{'status':'BLOCKED','material_findings':['F01','F02'],
    'code_locations':{'constructor':'Authority.__init__/refresh, lines 121-134, 206-229','clients':'verify_clients lines 938-984',
                      'raw_verification':'verify_raw_security lines 987-1043','controller_preclaim':'ProductionAdmission.revalidate; ReceiptBoundLedger.claim',
                      'provider_prebuild':'verify_claim; NativeProductionTransport.build'},
    'security_positive_evidence':'Explicit UNKNOWN/incomplete boundary/name-only/ExecID-only/missing mandatory source gates reject. Unknown listeners checked before projection; no arbitrary production CLI selector; fixed unconstructed observer prerequisite.',
    'independent_checks':ref(HERE/'security_check_reproduction.json'),'current_real_authorization':'BLOCKED',
    'production_constructor_injectable_authority_or_root':False,'synthetic_reachable_from_production_CLI':False,
    'qualification_root_confinement':False,'raw_connected_path_correlation_complete':False,
    'no_live_security_attestation':'No Docker or live topology observation was performed.'})

crashes=read(HERE/'crash_reproduction.json');partial=read(HERE/'partial_publication_reproduction.json')
write('receipt_sidecar_crash_audit.json',{'status':'PASS_BOUNDED_FAILURE_POINTS_NOT_FULL_STORAGE_CRASH_PROOF',
    'receipt_contract':ref(CAND/'receipt_authority_contract_v2_candidate.json'),'schema':ref(CAND/'receipt_schema_v2_candidate.json'),
    'future_schema':ref(CAND/'future_production_receipt_schema_v2_specification.json'),
    'V1_semantics':'Frozen V1 sources/contracts unchanged; V2 candidate and future real schema are distinct.',
    'receipt_binding':'Exact field set and canonical bytes; base_attempt_id and entire work item; canonical/event/effectivity/controller/provider/contract/enforcement/client policy/issuance evidence pins.',
    'NONE':'verify_receipt requires raw is None; independent E2E inspected null durable claim receipt SHA.',
    'durable_operations_before_exclusive_claim':['mkdir_durable(raw-evidence/attempt) with parent fsync','exclusive preclaim directory mkdir and parent fsync',
        'exclusive current and issuance raw files with file/parent fsync','exclusive receipt file with file/parent fsync for RESTRICTED',
        'exclusive association file with file/parent fsync','persist_tree and original raw/association readback','exclusive writer lock','exclusive claim'],
    'orphan_policy':'Preclaim directory existing blocks all reentry, including empty/partial artifacts. Before the writer lock ledger.state may still report UNSTARTED; actual claim blocks through sidecar guard. After lock without claim orphan lock blocks; malformed claim parse blocks; terminal partial blocks.',
    'original_candidate_crash_qualification':'No crash/partial-write fault injection in sealed synthetic_e2e_qualifier.py. It tests missing/corrupt association after successful claim and provider failure.',
    'independent_points':[{k:v for k,v in x.items() if k!='retained_files'} for x in crashes['cases']],
    'partial_writes':partial['cases'],'once_only_observed':True,'overwrites_observed':False,'automatic_reentry_accepted':False,
    'limits':['Line-event interruption and local write-error injection are not power-loss tests.','No durable recovery/cleanup authority constructed.','Diagnostics use F01 traversal solely to confine actual writes to audit namespace; do not certify root isolation.'],
    'evidence':[ref(HERE/'crash_reproduction.json'),ref(HERE/'partial_publication_reproduction.json')]})
write('synthetic_isolation_audit.json',{'status':'FAIL_F01','evidence':ref(HERE/'isolation_reproduction.json'),
    'root_guard_failure':'Path.is_relative_to is lexical; safe_path prohibits symlinks but not ..; both fixture_path and payload qualification_root pass using .. and resolve outside QUALIFICATION_ROOT.',
    'reproduced_actions':'Normal exact candidate constructors, RESTRICTED and NONE synthetic MATERIALIZED terminals, failure INTERRUPTED terminal, all outside declared qualification root and inside exclusive audit namespace.',
    'no_candidate_mutation':True,'no_legacy_global_mutation':True,'same_materialize_checked_code_object_traced':True,
    'simulated_IO_review':'SyntheticScientificTransport has no subprocess.run; simulated build validates command/context and returns CompletedProcess; SOURCE_INDEPENDENT only; Docker wrapper binds original shared functions to simulated transport. Original materializer_commit invokes local read-only git.',
    'audit_enforcement':'Python audit hook resolved every write path against this audit directory, denied sockets/Docker/native/install/source subprocesses, and allowed only two exact read-only git forms. /dev/null used only to discard Git diagnostics.',
    'production_entry':'Exact installed source paths required; production CLI has only --request; no synthetic CLI or arbitrary provider accepted.',
    'interpretation':'No demonstrated Docker/network or real authority bypass. Demonstrated filesystem confinement bypass is independently material.'})

matrix=read(CAND/'rejection_matrix.json');results=read(CAND/'synthetic_e2e_results.json');inherited=read(OLD/'rejection_matrix.json')
assert len(matrix['checks'])==126 and len(inherited['checks'])==77 and set(inherited['checks'])<=set(matrix['checks'])
assert len(results['required_A_through_X'])==len(results['required_inherited_A_X'])==24
assert matrix['mandatory_skipped']==0
for name,row in matrix['checks'].items():
    assert row['status']=='PASS_REJECTED' and row['ledger_before']==row['ledger_after']
    assert row['exact_tested_sources']=={str(sources[k].relative_to(ROOT)):identities[k]['sha256'] for k in ('controller','provider')}
qualifier=sources['qualifier'].read_text()
def gate(name):
    if name.startswith('production_CLI'):return 'controller.main argparse'
    if name.startswith('old_frozen_'):return 'historical successor_runtime frozen guard (deliberately unchanged)'
    if name in {'source_acquisition','oracle','allocation','repair','patch_frozen_runtime','monkeypatch_frozen_runtime','retry'}:return 'controller.request_operation/request_retry'
    if name in {'source_fetch','base_pull','registry_fallback','Buildx_solve','host_buildctl','network_on_NONE'}:return 'provider.validate_command'
    if name.startswith('effectivity_'):return 'provider.validate_effectivity_status'
    if name.startswith('wrong_real_population'):return 'provider.validate_real_population'
    if name in {'terminal_overwrite'}:return 'inherited Ledger.terminal ownership/state guard'
    if name.startswith('copied_installed') or name.startswith('candidate_real') or name.startswith('real_constructor') or name=='real_controller_authority_injection':return 'exact source constructor/signature guard'
    if name.startswith('provider_') or 'claim_raw_association' in name:return 'ProductionProvider/verify_claim/read_claim_association/execute_synthetic'
    if name.startswith('receipt_') or name in {'NONE_issuance','NONE_receipt_present','restricted_receipt_null','wrong_production_schema','qualification_receipt_promoted','runtime_authority_false','wrong_allowed_origins','broader_allowlist','stale_topology_sha','noncanonical_receipt_bytes','duplicate_receipt_keys'}:return 'receipt_value/verify_receipt or ledger revalidation for reuse'
    return 'controller.prepare/claim -> Authority.refresh/select/observe, verify_raw_security/verify_clients, or explicit constructor/transport guard'
coverage=[]
for name,row in matrix['checks'].items():
    coverage.append({'name':name,'inherited':name in inherited['checks'],'source_gate_family':gate(name),
        'observed_exception':row['observed_rejection'],'observed_reason':row['reason'],
        'unchanged_ledger_bytes':True,'qualification':'READ_SOURCE_AND_SEALED_OUTPUT',
        'disposition':'MINOR_MAPPING_LIMIT_F03' if name=='runtime_authority_false' else 'SUPPORTED_REJECTION_OUTCOME'})
write('qualification_coverage_audit.json',{'status':'REJECTION_OUTCOMES_SUBSTANTIATED_WITH_MAPPING_LIMIT_AND_MATERIAL_GAPS',
    'source':ref(sources['qualifier']),'output':ref(CAND/'synthetic_e2e_results.json'),'matrix':ref(CAND/'rejection_matrix.json'),
    'successor_A_X':results['required_A_through_X'],'inherited_A_X':results['required_inherited_A_X'],
    'rejection_count':126,'inherited_count':77,'new_count':49,'mandatory_skipped_reported_and_seen':0,'coverage':coverage,
    'fixture_review':'62 exact separate fixture roots, 613 exact external files verified. Several read-only negative probes intentionally share a primary ledger; before/after hashes show no mutation. Mutation cases use fresh fixture calls, with intentional paired probes documented in source.',
    'positive_evidence':'Read actual RESTRICTED/NONE MATERIALIZED terminal/claim canonical bytes and 21 artifact hashes each; failure INTERRUPTED terminal and transient-turnover terminal inspected.',
    'independent_execution':'641 projection replay; 23 explicit fail-closed security probes plus one contradictory endpoint counterexample; three exact shared-code E2E traces under audit containment; ten crash boundaries plus four partial-write faults.',
    'not_independently_rerun':'The entire author 126-case main was not executed, because it writes sealed candidate outputs and the external original qualification tree. Review used actual source, exact sealed rejection output and preserved fixture bytes.',
    'qualification_gaps':['F01 traversal not covered','F02 contradictory raw socket Path not covered','F03 runtime_authority_false is integer zero in a synthetic receipt, not the former real-authority Boolean gate'],
    'crash_source_test_gap':'Author qualifier has no preclaim crash injection; independent bounded probes supplied separately with explicit limits.'})
science=read(HERE/'scientific_independent_replay.json')
write('scientific_integrity_audit.json',{'status':'PASS_EXACT_641_PROJECTION','evidence':ref(HERE/'scientific_independent_replay.json'),
    'population':science['population'],'variants':science['variants'],'blocked_cases':science['blocked_cases'],
    'scientific_Dockerfile_RUN_bytes_order':'Exact full scientific Dockerfile equality old/corrected/successor for all 641; full byte equality implies RUN byte/order equality.',
    'native_command_projection':'Exact old/corrected/successor equality for all 641; native commands not executed.',
    'scientific_eligibility_inferred':False,'environment_ready_inferred':False,'real_builds':0,'source_exports':0})

findings=[
 {'id':'F01','severity':'MATERIAL','title':'Synthetic root confinement bypass through dot-dot paths',
  'source_path':str(sources['provider']),'source_functions':['Authority.__init__','Authority.refresh','ReceiptBoundLedger.__init__','publish_raw_association','SyntheticScientificTransport.__init__'],
  'source_lines':[131,132,212,213,494,1060,1140], 'source_sha256':identities['provider']['sha256'],
  'evidence_identity':[ref(HERE/'isolation_reproduction.json'),ref(HERE/'audit_io_events.json')],
  'observed':'Direct outside-root constructor rejects; same outside audit directory expressed as QUALIFICATION_ROOT/../../../../errpilot/... is accepted. Normal constructors publish claims, raw sidecars and terminals outside the exclusive qualification root.',
  'consequence':'Candidate-only synthetic API can write outside its mandated qualification namespace; real-output/sibling filesystem contamination is possible where caller can prepare synthetic fixture files. No real ledger or production authority bypass was exercised.',
  'proposed_bounded_disposition':'Separate authorized successor revision must reject traversal/non-normalized inputs or verify canonical resolved fixture/root confinement before any I/O; add negative constructor, ledger, sidecar and transport tests without modifying frozen historical guards. Re-audit and reseal; do not fix this sealed package.'},
 {'id':'F02','severity':'MATERIAL','title':'Connected Unix socket path is not correlated to the attributed client endpoint',
  'source_path':str(sources['provider']),'source_functions':['verify_clients','verify_raw_security'],
  'source_lines':[961,962,981,982,983,1003,1034,1043], 'source_sha256':identities['provider']['sha256'],
  'evidence_identity':[ref(HERE/'client_endpoint_correlation_reproduction.json'),ref(HERE/'security_check_reproduction.json')],
  'observed':'For connected inode 3697, changing the independently retained socket Path to /tmp/unknown-control.sock while census/provenance still assert unix:///run/buildkit/buildkitd.sock preserves the accepted projection. Original controller publishes claim and provider revalidation accepts.',
  'consequence':'Contradictory raw endpoint/client provenance can satisfy the authorization gate because only inode multiset membership is checked; stable diagnostic exclusion hides the discrepancy. Violates complete process/endpoint correlation. Real observer remains absent and real authorization remains BLOCKED.',
  'proposed_bounded_disposition':'Separate successor revision must define and verify the socket inode/path/process/session relation (or an explicit independently authenticated peer mapping where pathless sockets are legitimate), fail closed on contradictions, and add preclaim/provider counterexample tests. Keep existing unknown-listener checks.'},
 {'id':'F03','severity':'MINOR','title':'Inherited authority rejection label changed meaning without an explicit mapping',
  'source_path':str(sources['qualifier']),'source_functions':['main.rejected','main receipt mutations'],
  'source_lines':[163,224,226,244], 'source_sha256':identities['qualifier']['sha256'],
  'evidence_identity':[ref(CAND/'rejection_matrix.json'),ref(CAND/'synthetic_e2e_results.json')],
  'observed':'runtime_authority_false mutates the synthetic receipt field to integer 0. V2 synthetic receipts correctly expect Boolean false, so this probes type/canonical-byte mismatch, not rejection of Boolean false as a real production authority value. The catch helper accepts any listed exception without asserting the gate reason.',
  'consequence':'All 126 rejection outcomes are recorded, but an unchanged inherited category name overstates semantic equivalence of this one authority test. Other production entry guards remain closed.',
  'proposed_bounded_disposition':'In a separately authorized candidate revision, document the V1-to-V2 category mapping, retain the type-confusion check under an accurate name, and assert intended exception/reason for authority-specific tests.'}
]
write('findings.json',{'status':STATUS,'findings':findings,'counts':{'MATERIAL':2,'MINOR':1,'OPTIONAL':0},'fixes_performed':False})
write('validation_results.json',{'status':STATUS,'candidate_exact_seal':'PASS','entry':'PASS','security':'BLOCKED_F01_F02',
    'receipt_crash_safety':'PASS_10_BOUNDARIES_PLUS_4_PARTIAL_WRITE_PROBES_WITH_LIMITS','synthetic_isolation':'FAIL_F01',
    'source_delta':'PASS_EXACT_AST_WITH_FINDINGS','A_X_126':'SOURCE_OUTPUT_REVIEW_COMPLETED_WITH_F03_MAPPING_LIMIT',
    'scientific_641':'PASS_EXACT_PROJECTION','supersession_graph':'PASS','preservation':'See preservation_verification.json; required final exact replay',
    'findings':{'MATERIAL':2,'MINOR':1,'OPTIONAL':0},'real_client_authorization':'BLOCKED',
    'candidate_acceptance_eligible':False,'lifecycle_freeze_eligible':False,
    'NEXT_GATE':'NOT_ADVANCED_TO_PASS_GATE; Human-PI disposition of independent audit findings required',
    'transaction':'INDEPENDENT_EXACT_CANDIDATE_AUDIT_ONLY'})
print('Assembled required audit analyses: BLOCKED, 2 MATERIAL / 1 MINOR / 0 OPTIONAL')

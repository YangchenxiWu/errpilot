"""Independent offline probes of exact imported bytes; candidate outputs read only."""
import copy
import importlib
import os
import sys
from collections import Counter
from pathlib import Path
from .audit_inventory import HERE,C,QUAL,REPO,read,write as new_write,sha,ident

def write(name,value):
 if (HERE/name).exists():
  assert read(HERE/name)==value,'prior audit result drift: '+name
 else:new_write(name,value)

def guard(event,args):
 if event=='subprocess.Popen' and args[1]==['git','cat-file','blob','5c007fbfbfc5b3529105a14f87127f50e1eab6d7:evaluation/downstream_benchmark/v6_current_state.json']:
  return
 if event in ('subprocess.Popen','os.system','socket.connect','socket.bind'):
  raise RuntimeError('AUDIT forbids process/network operation: '+event)
 if event=='open':
  path,mode,flags=args
  writing=(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)) if isinstance(flags,int) else bool(mode and any(c in mode for c in 'wax+'))
  if writing and (isinstance(path,int) or not Path(path).absolute().is_relative_to(HERE)):
   raise RuntimeError('AUDIT forbids external write: '+str(path))
 if event in ('os.mkdir','os.rename','os.remove','os.rmdir','os.symlink','os.link','os.chmod','os.truncate'):
  raise RuntimeError('AUDIT forbids filesystem mutation: '+event)
sys.addaudithook(guard)
PKG='evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_remediation_final_resume_v1'
p=importlib.import_module(PKG+'.production_provider_remediated_candidate')
c=importlib.import_module(PKG+'.production_controller_remediated_candidate')
q=importlib.import_module(PKG+'.qualification_io')
source={str(Path(m.__file__).relative_to(REPO)):ident(Path(m.__file__)) for m in (p,c,q,p.endpoint_binding)}
assert sha(Path(p.__file__).read_bytes())=='51f842194fd79bb9519bb6f45281a897c5249bb80558750f4660233c4c0bd438'
assert sha(Path(c.__file__).read_bytes())=='7c097da628d521987dee76dba8689b0dcdd45d286996ce7509c8442bf8f82b10'
shared_before={k:id(v) for k,v in p.a.shared.__dict__.items()}

def reject(call,reason):
 try:call()
 except Exception as e:
  assert type(e).__name__=='Rejected' and str(e)==reason,(type(e).__name__,str(e),reason)
  return {'status':'PASS_REJECTED','exception':type(e).__name__,'reason':str(e)}
 raise AssertionError('unexpected acceptance')

f01={}
for label,value in {
 'original_exploit_retargeted':str(QUAL)+'/../../../../errpilot/'+str(HERE.relative_to(REPO))+'/not-created',
 'direct_parent':str(QUAL)+'/../escape', 'nested_parent':str(QUAL)+'/a/../../escape',
 'dot_alias':str(QUAL)+'/./fixture_1','double_separator':str(QUAL)+'//fixture_1',
 'relative_alias':'qualification/fake','absolute_outside':str(HERE/'not-created'),
 'real_root':str(p.a.OUTPUT_ROOT/'namespace.json')}.items():
 reason='F01 outside exact qualification root' if label in ('absolute_outside','real_root') else 'F01 absolute canonical spelling required; traversal/alias rejected'
 f01[label]={'input':value,**reject(lambda v=value:p.Authority.synthetic(v),reason)}
f01['audit_owned_constructor_guard']=reject(lambda:c.ProductionController.synthetic(HERE/'not-created.json'),'F01 outside exact qualification root')
sealed=read(C/'synthetic_output_inventory.json')['files']
io=q.QualificationIO()
symlinks=[]
for rel,row in sealed.items():
 if row['type']=='symlink' and rel.startswith('run_4/'):
  symlinks.append({'path':str(QUAL/rel),'target':row['target'],**reject(lambda rel=rel:io.path(QUAL/rel),'F01 symlink/resolved alias rejected')})
legit=QUAL/'run_4/fixture_76/legitimate/nested/receipt.json'
assert io.read(legit)==b'LEGITIMATE_OWNED_FIXTURE\n'
write('independent_F01_probes.json',{'sources':source,'lexical_and_constructor':f01,'existing_symlinks_read_only':symlinks,'legitimate_nested_read':{'path':str(legit),'status':'PASS'},'new_nested_write_executed':False,'actual_path_replacement_executed':False,'reason':'Exact source/root guards prevent writing under the audit namespace; existing qualification output must stay unchanged. No guard bypass or root substitution performed.'})

config=p.frozen_inputs();matrix=read(C/'rejection_matrix.json')['checks']
base=read(QUAL/'run_4/fixture_1/raw_fixture.json')
baseline=p.verify_raw_security(base,config,stage='AUDIT_BASELINE',synthetic=True)
assert baseline['client_verdict']=='SYNTHETIC_CLIENT_AUTHORIZATION_PASS'
f02=[];f03=[]
for name,row in matrix.items():
 if not name.startswith('F02_') and name not in ('runtime_authority_false','runtime_authority_integer_zero'):continue
 bundle=read(Path(row['fixture_root'])/'raw_fixture.json')
 reason=row['intended_gate']['reason']
 for stage in ('PRECLAIM','PROVIDER_PREBUILD'):
  result=reject(lambda:p.verify_raw_security(bundle,config,stage=stage,synthetic=True),reason)
  entry={'category':name,'stage_argument':stage,'input_file':str(Path(row['fixture_root'])/'raw_fixture.json'),'input_sha256':sha((Path(row['fixture_root'])/'raw_fixture.json').read_bytes()),'execution':'EXACT_FINAL_PURE_VERIFIER; not full constructor/claim/build execution',**result}
  (f03 if name.startswith('runtime_authority_') else f02).append(entry)
# Independently reconstruct the original contradiction from the passing fixture.
mut=copy.deepcopy(base)
sockets=mut['sources']['unix_sockets']['raw_utf8'].replace('3697 /run/buildkit/buildkitd.sock','3697 /tmp/unknown-control.sock')
daemon=p.a.loads(mut['sources']['daemon']['raw_utf8'].encode());daemon['sockets']=sockets
for name,raw in [('unix_sockets',sockets.encode()),('daemon',p.a.canonical(daemon))]:
 mut['sources'][name].update(raw_utf8=raw.decode(),sha256=p.a.sha(raw))
original=[]
for stage in ('PRECLAIM','PROVIDER_PREBUILD'):
 original.append({'stage':stage,**reject(lambda:p.verify_raw_security(mut,config,stage=stage,synthetic=True),'F02 actual socket Path/endpoint conflict')})
pathless=[]
for rel,row in sealed.items():
 if rel.startswith('run_4/') and rel.endswith('/raw_fixture.json') and row['type']=='file':
  b=read(QUAL/rel);e=p.a.loads(b['sources']['client_evidence']['raw_utf8'].encode())
  if any(x.get('pathless_independent_association') is True for x in e['sessions']):
   result=p.verify_raw_security(b,config,stage='AUDIT_PATHLESS',synthetic=True)
   paths=[x['Path'] for x in p.parse_socket_rows(b['sources']['unix_sockets']['raw_utf8'].encode()) if x['St']=='03']
   assert paths==[''];pathless.append({'file':str(QUAL/rel),'actual_Path':paths,'verdict':result['client_verdict']})
write('independent_F02_probes.json',{'sources':source,'baseline':'PASS','original_contradiction_reconstruction':original,'recorded_negative_inputs_independently_executed':f02,'pathless_positive':pathless,'real_claims':0,'builds':0,'executed_route_limit':'Pure shared gate independently executed; complete source-level preclaim/prebuild calls reviewed in sealed run_4 evidence.'})
write('independent_F03_probes.json',{'sources':source,'field':'client_evidence.sessions[0].authenticated_source','checks':f03,'false_and_zero_distinct':True})

authority=p.Authority.synthetic(QUAL/'run_4/fixture_1/synthetic_effectivity_fixture.json')
ctrl=c.ProductionController.synthetic(QUAL/'run_4/fixture_1/synthetic_effectivity_fixture.json')
terminal_checks=[]
for item in authority.population['items']:
 root=Path(authority.root);aid=item['base_attempt_id'];claim_path=root/'ledger/claims'/(aid+'.json');term_path=root/'ledger/terminals'/(aid+'.json')
 if not term_path.exists():continue
 claim=read(claim_path);terminal=read(term_path)
 assert claim_path.read_bytes()==p.a.canonical(claim) and term_path.read_bytes()==p.a.canonical(terminal)
 assert terminal['claim_sha256']==p.a.sha(claim_path.read_bytes())
 receipt=None if claim['receipt_sha256'] is None else (root/'raw-evidence'/aid/'preclaim'/(claim['receipt_sha256']+'.receipt.json')).read_bytes()
 issuance=p.read_claim_association(authority,item,claim,receipt)
 assert p.verify_receipt(authority,item,receipt,authority.observe('AUDIT_READ_ONLY'),issuance=issuance)==claim['receipt_sha256']
 after_terminal=reject(lambda:ctrl.prepare(item),'receipt after claim/terminal; no retry/reuse')
 provider_reentry=reject(lambda:p.verify_claim(authority,item,claim,receipt),'receipt after terminal/reuse')
 terminal_checks.append({'attempt_id':aid,'state':terminal['state'],'claim_sha256':sha(claim_path.read_bytes()),'terminal_sha256':sha(term_path.read_bytes()),'receipt_sha256':claim['receipt_sha256'],'association_sha256':claim['input_runtime_binding']['raw_evidence_association_sha256'],'NONE_null':receipt is None,'controller_reentry':after_terminal,'provider_reentry':provider_reentry,'retained_association_verified_by_final_source':True})
write('independent_receipt_probes.json',{'sources':source,'terminals':terminal_checks,'writes_to_existing_output':0})

old=importlib.import_module('evaluation.downstream_benchmark.evidence.v6_preparation_execution_production_runtime_installation_resume_v1.production_provider_candidate')
prior=importlib.import_module('evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_resume_v1.production_provider_successor_candidate')
_,manifest=p.a.load_inputs();popraw=p.a.read_exact(p.legacy.PACKAGE+'work_items_candidate.json',p.legacy.WORK_SHA);population=p.a.loads(popraw)
p.a.validate_population(manifest,population)
mapping=p.exact_json(REPO/p.NATIVE/'seven_base_transport_map.json')['mapping']
rows=[]
for item in population['items']:
 plan=p.a.select(manifest,ordinal=item['census_order'],case_id=item['case_id'],plan_sha=item['plan_sha256'])
 assert item==p.a.work_item(plan,item['variant'])
 marker=b'AUDIT_COMPILE_ONLY_NO_AUTHORITY\n' if item['build_network_required'] else None
 compiled=p.compile_production_transport(item,plan,{},receipt_raw=marker)
 previous=prior.compile_production_transport(item,plan,{},receipt_raw=marker)
 original=old.compile_production_transport(item,plan,{},receipt_raw=marker)
 assert compiled==previous==original
 recipe=p.a.engine_recipe(plan)
 expected=p.a.shared.build_definition(recipe,source_present=item['variant']!='SOURCE_INDEPENDENT',dependency_present=plan['recipe_candidate']['requirements']['dependency_bytes_b64'] is not None)
 assert compiled['scientific_dockerfile']==expected
 base_row=next(x for x in mapping if x['scientific_base_authority']==item['base_image_reference'])
 binding={**base_row,'endpoint':config['endpoint'],'native_binary_sha256':config['client_binary_sha256'],'same_daemon':True,'daemon_count':1,'runtime_reference':config['runtime_image']['immutable_reference'],'frontend_alias':'errpilot_frozen_base','container_id':'SYNTHETIC_DAEMON','container_root':'/tmp/errpilot-v6-compile-only','tag':'errpilot-synthetic-compile-only','proxy_internal_host_binding':'add-hosts='+config['proxy']['proxy_name']+'=172.28.0.3','compiled':compiled}
 argv=p.native.native_argv(binding,binding['container_root'],binding['tag'],compiled)
 assert argv==old.native.native_argv(binding,binding['container_root'],binding['tag'],original)==prior.native.native_argv(binding,binding['container_root'],binding['tag'],previous)
 p.validate_command(['docker','exec',binding['container_id'],*argv],binding)
 if not item['build_network_required']:assert compiled['build_args']=={} and compiled['frontend_options']==['force-network-mode=none']
 rows.append({'attempt_id':item['base_attempt_id'],'variant':item['variant'],'work_identity':p.a.identity(item),'recipe_sha256':p.a.identity(recipe),'scientific_dockerfile_sha256':sha(expected),'ordered_RUN': [x.decode() for x in expected.splitlines() if x.startswith(b'RUN ')],'execution_dockerfile_sha256':sha(compiled['execution_dockerfile']),'native_argv_sha256':p.a.identity(argv),'base_authority':item['base_image_reference'],'required_network':item['build_network_required'],'status':'PASS_EXACT_PURE_PROJECTION'})
assert shared_before=={k:id(v) for k,v in p.a.shared.__dict__.items()}
write('scientific_integrity_audit.json',{'status':'PASS_IMPLEMENTATION_EQUIVALENCE_ONLY','independently_executed':True,'sources':source,'population':p.population_identity(population,popraw),'variants':dict(Counter(x['variant'] for x in population['items'])),'blocked':[x['case_id'] for x in population['blocked']],'replayed':len(rows),'rows':rows,'shared_module_bindings_unchanged':True,'native_commands_executed':0,'environment_readiness_claimed':False,'scientific_validation_claimed':False})
print({'F01_lexical':len(f01),'F01_existing_symlinks':len(symlinks),'F02_negative_gate_calls':len(f02),'F03_gate_calls':len(f03),'terminal_associations':len(terminal_checks),'scientific_replay':len(rows)})

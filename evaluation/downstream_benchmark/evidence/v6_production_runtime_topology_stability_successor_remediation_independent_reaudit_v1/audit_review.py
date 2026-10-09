"""Independent structural and sealed-evidence cross-checks; no qualification rerun."""
import ast
import collections
import os
from pathlib import Path
from .audit_inventory import HERE,C,QUAL,REPO,E,read,write,ident,sha,tree

def digest_value(value):
 import json
 return sha((json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode())
def source_pins(refs):
 return all(sha((REPO/p).read_bytes())==h for p,h in refs.items())
def functions(path):
 result={}
 def walk(nodes,prefix=''):
  for n in nodes:
   if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
    result[prefix+n.name]={'ast':ast.dump(n,include_attributes=False),'line':n.lineno,'end':n.end_lineno};walk(n.body,prefix+n.name+'.')
   elif isinstance(n,ast.ClassDef):walk(n.body,prefix+n.name+'.')
 walk(ast.parse(path.read_bytes()).body);return result

# Strict independent seal shape and text validation.
m=read(C/'artifact_sha256.json')
assert set(m)=={'HUMAN_PI_ACCEPTED','candidate_only','construction_history_included','excluded','execute_now','files','payload_count','qualified_runtime_source_pair','runtime_effective','schema','self_sha256_semantics','strict_text_semantics','synthetic_outputs_bound_by','total_file_count'}
assert m['schema']=='V6_REMEDIATED_SUCCESSOR_FINAL_CANDIDATE_SEAL_V1' and m['excluded']==['artifact_sha256.json'] and m['payload_count']==763 and m['total_file_count']==764
json_count=0;python_count=0
for rel,row in m['files'].items():
 assert set(row)=={'mode','sha256','size_bytes','type'} and row['type']=='file'
 raw=(C/rel).read_bytes();raw.decode('utf-8');assert b'\r' not in raw
 if rel.endswith('.json'):read(C/rel);json_count+=1
 if rel.endswith('.py'):ast.parse(raw);python_count+=1
write('seal_schema_validation.json',{'status':'PASS','schema':m['schema'],'payload_rows':763,'strict_JSON_files':json_count,'AST_parsed_python_files':python_count,'all_payload_UTF8_LF':True})

graph=read(C/'supersession_dependency_graph.json');nodes={n['id']:n for n in graph['nodes']};assert len(nodes)==11 and len(graph['edges'])==18
visited=set();stack=set()
def visit(n):
 assert n not in stack,'cycle';
 if n in visited:return
 stack.add(n)
 for src,dst in graph['edges']:
  assert src in nodes and dst in nodes
  if src==n:visit(dst)
 stack.remove(n);visited.add(n)
for n in nodes:visit(n)
references=[]
for n in graph['nodes']:
 for ref in n['references']:
  path=REPO/ref['path'];actual=ident(path)
  assert actual['type']=='file' and all(actual.get(k)==v for k,v in ref.items() if k!='path'),ref
  references.append({'node':n['id'],'path':str(path),**actual})
assert len(references)==739
old=E/'v6_production_runtime_topology_stability_successor_resume_v1'
contracts=['receipt_authority_contract_v2_candidate.json','receipt_schema_v2_candidate.json','client_authorization_contract_candidate.json','topology_stability_contract_candidate.json','raw_observation_contract_candidate.json','transient_diagnostics_contract_candidate.json','raw_sidecar_contract_candidate.json']
assert all((C/n).read_bytes()==(old/n).read_bytes() for n in contracts)
write('contract_supersession_audit.json',{'status':'PASS_HASH_GRAPH_WITH_F01_AUTHORITY_FINDING','nodes':11,'edges':18,'acyclic':True,'exact_hash_references':739,'references':references,'preserved_V2_contracts':contracts,'V3_endpoint_supplement_mandatory':True,'V3_F01_exclusion_accepted':False,'historical_acceptance_transferred':False,'effectivity_pin_created':False})

matrix=read(C/'rejection_matrix.json');checks=matrix['checks'];gold=read(old/'rejection_matrix.json')['checks']
assert len(checks)==188 and len(gold)==126 and not set(gold)-set(checks) and len(set(checks)-set(gold))==62
assert matrix['mandatory_skipped']==0
results=read(C/'synthetic_e2e_results.json')['tests']
evidence_summary=[];counter=collections.Counter();locators=[]
harnesses={n:(C/n).read_text().splitlines() for n in ('synthetic_e2e_qualifier.py','remediation_regressions.py','additional_security_regressions.py','package_final_candidate.py')}
for name,row in checks.items():
 assert row['expected_category']==name and row['status']=='PASS_REJECTED' and source_pins(row['exact_tested_sources'])
 assert row['ledger_before']==row['ledger_after'] and row['attempts_consumed_by_rejection']==0
 controlled=row.get('controlled_harness_mutation_during_call',False)
 if not controlled:assert row['evidence_before']==row['evidence_after']
 assert digest_value(row['evidence_before'])==row['fixture_identity']
 expected=row.get('intended_gate',{'reason':row.get('expected_specific_rejection'),'classification':'Rejected'})
 assert expected['classification']==row['observed_rejection']
 reason_exact=expected['reason']==row['reason']
 if not reason_exact:
  assert name in ('missing_effectivity_pin','missing_claim_raw_association')
  assert row['observed_rejection']=='FileNotFoundError' and row['reason'].startswith('[Errno 2]')
  expected_leaf='absent_effectivity.json' if name=='missing_effectivity_pin' else read(Path(row['fixture_root'])/'ledger/claims/SYNTHETIC_QUALIFICATION_RESTRICTED_A.json')['input_runtime_binding']['raw_evidence_association_sha256']+'.json'
  assert expected_leaf in row['reason']
 if name.startswith('production_CLI_'):assert 'unrecognized arguments: --'+name.removeprefix('production_CLI_') in row['stderr']
 counter[row['observed_rejection']]+=1
 tokens=[name]
 if name.startswith('F02_'):tokens.append(name.split('_',3)[-1])
 if name.startswith('F01_'):tokens.append(name.removeprefix('F01_'))
 if name.startswith('effectivity_'):tokens.append(name.removeprefix('effectivity_'))
 if name.startswith('wrong_real_population_'):tokens.append(name.removeprefix('wrong_real_population_'))
 if name.startswith('production_CLI_'):tokens.append('--'+name.removeprefix('production_CLI_'))
 tokens.append(name.upper())
 refs=[]
 for file,lines in harnesses.items():
  for number,line in enumerate(lines,1):
   if any(('"'+t+'"' in line or "'"+t+"'" in line) for t in tokens):refs.append({'path':str(C/file),'line':number,'source':line.strip()})
 if not refs:
  # Dynamic loop labels have explicit operation selectors in these exact sources.
  if name.startswith('F01_'):
   file='additional_security_regressions.py' if 'outbound' in name else 'remediation_regressions.py'
   refs=[{'path':str(C/file),'line':96 if 'outbound' in name else 189,'source':'Dynamic F01 label: loop selector and actual fixture inventory must be read together.'}]
  elif name.startswith('F02_'):
   refs=[{'path':str(C/'additional_security_regressions.py'),'line':36,'source':'Socket attribute Protocol/Type/Flags loop; exact row mutation before each route.'}]
  elif name.startswith('copied_installed_'):
   refs=[{'path':str(C/'synthetic_e2e_qualifier.py'),'line':319,'source':'Dynamic copied source class factory guard.'}]
  else:locators.append(name)
 fixture=Path(row['fixture_root']);direct_path=C/'construction_history/qualification_run_4/executed_rejections'/(name+'.json')
 direct_equal=read(direct_path)==row if direct_path.exists() else None
 if not controlled:assert direct_equal
 identities=[k for k in row['ledger_before'].get('claims',{})]
 input_ref=row['evidence_before'].get('raw_fixture.json')
 evidence_summary.append({'category':name,'inherited':name in gold,'source_pins':row['exact_tested_sources'],'fixture_root':str(fixture),'fixture_identity':row['fixture_identity'],'record_path':str(direct_path) if direct_equal else str(C/'rejection_matrix.json'),'expected_gate':expected,'actual_reason':row['reason'],'exception':row['observed_rejection'],'reason_exact':reason_exact,'missing_file_reason_normalization_verified':not reason_exact,'mutation_or_input_source':refs,'raw_fixture_identity':input_ref,'input_ledger_claim_identities':identities,'ledger_before_after_equal':True,'evidence_before_after_equal':row['evidence_before']==row['evidence_after'],'controlled_mutation':controlled,'mandatory_skip':False})
assert not locators,locators
mappings={}
for key in ('required_A_X_coverage','inherited_A_X_coverage'):
 mapping=matrix[key];assert set(mapping)==set('ABCDEFGHIJKLMNOPQRSTUVWX')
 for value in mapping.values():
  assert value['checks'] and all(x in checks or x in results for x in value['checks'])
 mappings[key]=mapping
write('qualification_coverage_audit.json',{'status':'PASS_188_RECORDED_REJECTIONS_WITH_MINOR_LOCATOR_DEFECT','inherited':126,'new':62,'total':188,'mandatory_skips':0,'exception_counts':dict(counter),'all_final_source_pins_verified':True,'both_A_X_mappings':mappings,'categories':evidence_summary,'independent_execution_scope':'76 final pure F02 calls + 4 F03 calls, F01 read-only probes, receipt/association readbacks and 641 replay. Remaining calls inspected against sealed final harness, records and physical inventory.','semantic_notes':['terminal_overwrite correctly rejects at missing writer lock after a completed terminal; this is an ownership gate, not the later duplicate-terminal branch. Exclusive publication also reviewed.','Missing-file cases intentionally normalize changing path/digest; audit verifies exact missing association digest from the durable claim.','Pure/no-write categories reuse fixture_1; mutating security fixtures use separate roots. Independent per-category records do not mean 188 fresh ledgers.','F01_replace_component_before_open fixture_root incorrectly names run_4; actual trace and inventories resolve fixture_76.']})

# Fault traces must identify exact code object source, line and retained result.
faults=[]
for name in ('crash_boundary_revalidation.json','partial_write_revalidation.json'):
 document=read(C/name);assert source_pins(document['exact_tested_sources'])
 for row in document['checks']:
  hit=row['trace_hit'];assert len(hit)==1;hit=hit[0]
  path=Path(hit['source']);assert sha(path.read_bytes())==hit['source_sha256']
  fs=functions(path);assert hit['function'] in fs and fs[hit['function']]['line']<=hit['line']<=fs[hit['function']]['end']
  code=path.read_text().splitlines()[hit['line']-1].strip()
  root=Path(row['fixture']) if 'fixture' in row else Path(read(C/'construction_history/qualification_run_4/rejection_matrix.json')['checks']['runtime_authority_false']['fixture_root']).parent/('fixture_'+str(121+len([x for x in faults if x['suite']==name])))
  # Infer partial fixtures by exact after-inventory identity, never guessed population authority.
  if 'fixture' not in row:
   inventory=read(C/'synthetic_output_inventory.json')['files'];candidates=sorted({Path(k).parts[1] for k in inventory if k.startswith('run_4/fixture_') and len(Path(k).parts)>1})
   found=[]
   for label in candidates:
    prefix='run_4/'+label+'/'
    entries={k[len(prefix):]:v for k,v in inventory.items() if k.startswith(prefix)}
    if entries==row['after']:found.append(QUAL/'run_4'/label)
   assert len(found)==1,found;root=found[0]
  measured=tree(root);measured.pop('.');assert measured==row['after']
  claims=[k for k,v in measured.items() if k.startswith('ledger/claims/') and v['type']=='file' and v['size_bytes']>0]
  terminals=[k for k,v in measured.items() if k.startswith('ledger/terminals/') and k.endswith('.json') and v['type']=='file']
  assert len(claims)<=1 and len(terminals)<=1 and row['reentry']['automatic_retry'] is False and row['reentry']['evidence_bytes_paths_modes_unchanged']
  if 'empty_retained_file' in row:assert measured[row['empty_retained_file']]['size_bytes']==0 and 'os.write(fd, view)' in code
  faults.append({'suite':name,'point':row.get('point',row.get('kind')),'trace':hit,'source_line':code,'fixture_root':str(root),'retained_after_inventory_matches':True,'nonempty_claims':len(claims),'terminal_count':len(terminals),'reentry':row['reentry'],'empty_retained_file':row.get('empty_retained_file'),'independently_injected':False})
assert len(faults)==14
write('crash_partial_write_audit.json',{'status':'SOURCE_LEVEL_FAULT_INJECTION_PASS_REVIEWED_SEALED_EVIDENCE','crash_boundaries':10,'partial_write_classes':4,'PHYSICAL_POWER_LOSS_DURABILITY_NOT_ESTABLISHED':True,'actual_final_source_and_lines_verified':True,'checks':faults,'limitations':['Four partial-write classes inject before the first os.write and retain empty reserved files; they do not establish arbitrary prefix/torn-write or power-loss behavior.','The actual final synthetic I/O methods are reached. Production ledger I/O and real power loss were not independently executed.','Crash before sidecar/lock/claim reserves evidence and fails reentry visibly; a malformed/empty claim does not imply a successfully durable consumed attempt.']})

protected=['compile_production_transport','validate_command','verify_layout','NativeProductionTransport.invoke','NativeProductionTransport.check','NativeProductionTransport.build','image_identity_pins','verify_image_identity','normalize_topology','verify_routes']
current=functions(C/'production_provider_remediated_candidate.py');before=functions(old/'production_provider_successor_candidate.py')
assert all(current[n]['ast']==before[n]['ast'] for n in protected)
changes={role:[n for n in sorted(set(functions(old/f'production_{role}_successor_candidate.py'))|set(functions(C/f'production_{role}_remediated_candidate.py'))) if functions(old/f'production_{role}_successor_candidate.py').get(n,{}).get('ast')!=functions(C/f'production_{role}_remediated_candidate.py').get(n,{}).get('ast')] for role in ('controller','provider')}
history=[]
for i in range(1,5):
 root=QUAL/f'run_{i}/input-source'
 pair={role:ident(root/f'production_{role}_remediated_candidate.py') for role in ('controller','provider')}
 result_file=C/f'construction_history/qualification_run_{i}'/('qualification_failure.json' if i==1 else 'synthetic_e2e_results.json')
 result=read(result_file)
 history.append({'run':i,'pair':pair,'controller_matches_final':pair['controller']['sha256']==sha((C/'production_controller_remediated_candidate.py').read_bytes()),'provider_matches_final':pair['provider']['sha256']==sha((C/'production_provider_remediated_candidate.py').read_bytes()),'recorded_status':result['status'],'failure_reason':result.get('reason'),'result_path':str(result_file)})
assert history[-1]['controller_matches_final'] and history[-1]['provider_matches_final'] and history[0]['recorded_status']=='BLOCKED'
write('synthetic_source_isolation_audit.json',{'status':'PASS_REVIEW_WITH_F01_LIMITATION','protected_function_AST_exact':protected,'changed_functions':changes,'history':history,'source_location_checks':'Exact candidate __file__ gates synthetic constructors; exact future installed paths gate real constructors. CLI only accepts --request.','shared_scientific_binding':'Private copied globals dictionary with original code objects; frozen module bindings not mutated. Synthetic transport implements deterministic CompletedProcess objects without subprocess invocation.','constructors_independently_called':'Normal synthetic constructors read fixture_1; wrong audit namespace and real-root constructors reject. No __file__ or globals patched; no __new__ bypass.','full_E2E_independently_rerun':False,'reason':'Preserving the exact hard-coded qualification population and source guards prevents a fresh write-capable E2E under the audit namespace.'})
print({'graph_references':len(references),'categories':len(evidence_summary),'fault_boundaries':len(faults),'source_history':history})

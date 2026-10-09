"""Compare the exit firewall, seal only this audit, and read the seal back."""
import ast
import json
import os
from pathlib import Path
from .audit_inventory import HERE,C,REPO,OUT,HEAD,read,write,sha,tree,snapshot,ident,git

entry=read(HERE/'entry_snapshot.json')
after=snapshot()
checks={key:entry[key]==after[key] for key in ('tracked','index','packages','persistent_tree','head','branch','tracked_diff','staged_diff')}
assert all(checks.values()),checks
assert len(after['tracked'])==1065 and after['head']==HEAD and after['branch']=='main'
assert after['tracked_diff']==after['staged_diff']==''
start=read(HERE/'entry_verification.json')
assert start['tracked_matches_preconstruction'] and start['index_matches_preconstruction']
assert start['existing_evidence_physical_files']==1780
assert start['canonical_sha256']=='e48580c1f9769d1b93ab995e6dcef3689c6920a9ce7b83f728526e9694dc68fd'
assert start['canonical_state']=='PREPARATION_EXECUTION_AUTHORIZED' and start['event_count']==3 and start['event_3_id']=='237d8020668f338c04065beb8557d8f25263fbfc0282003dcc5b2af67a20a50d'
for pins in start['source_and_descriptor_pins'].values():assert pins['expected']==pins['measured']
current=read(REPO/'evaluation/downstream_benchmark/v6_current_state.json')
assert all(ident(REPO/r['path'])['sha256']==r['sha256'] for r in current['event_chain'])
assert all(not list((OUT/'ledger'/n).iterdir()) for n in ('claims','terminals','locks'))
assert set(os.listdir(OUT))=={'ledger','namespace.json','qualification'}
candidate=read(C/'remediated_installation_candidate.json');plan=read(C/'remediated_installation_plan.json')
for value in (candidate,plan):
 assert value['candidate_only'] is True and value['HUMAN_PI_ACCEPTED']=='NO' and value['runtime_effective']=='NO' and value['execute_now'] is False
targets=set(start['production_target_exists'])|set(plan['proposed_helper_targets'].values())
targets|={'evaluation/downstream_benchmark/screening/'+n.replace('_candidate','_installed_v2') for n in candidate['security_contracts']}
absent={p:not os.path.lexists(REPO/p) for p in sorted(targets)}
assert all(absent.values()),absent
standard={p for p in git('ls-files','--others','--exclude-standard','-z').split('\0') if p}
existing={str((HERE.parent/n/p).relative_to(REPO)) for n,inventory in entry['packages'].items() for p,v in inventory.items() if v['type']=='file'}
unexpected=sorted(p for p in standard-existing if not p.startswith(str(HERE.relative_to(REPO))+'/'))
assert unexpected==[],unexpected
write('preservation_verification.json',{'status':'PASS_EXACT_EXIT_FIREWALL','checks':checks,'tracked_file_count':1065,'index_before':entry['index'],'index_after':after['index'],'existing_evidence_files':1780,'predecessor_files':1016,'candidate_files':764,'persistent_entries':len(after['persistent_tree']),'persistent_file_count':sum(v['type']=='file' for v in after['persistent_tree'].values()),'head':HEAD,'branch':'main','live_origin_exit':{'command':'git ls-remote --exit-code origin refs/heads/main','observed':HEAD,'exit_code':0,'method':'Actual read-only escalated tool call immediately before finalization'},'canonical':ident(REPO/'evaluation/downstream_benchmark/v6_current_state.json'),'event_count':3,'event_3_id':current['event_head']['event_id'],'real_ledger':{'UNSTARTED':641,'claims':0,'terminals':0,'retries':0,'orphans':0,'locks':0},'production_targets_absent':absent,'unexpected_standard_untracked':unexpected,'Docker_operations':0,'live_Docker_recertification':False,'Docker_preservation_basis':'No Docker command/API/native solve/topology operation was issued by the auditor. Unrelated concurrent Docker state changes were not measured.','writes_only_under':str(HERE),'candidate_or_historical_source_changes':False,'native_commands_executed':0,'acceptance_commit_publication_or_installation':False})
validation=read(HERE/'validation_results.json')
validation['gates']['P_preservation']='PASS_EXACT_EXIT_FIREWALL'
validation['gates']['O_audit_seal']='MANIFEST_CREATED_AND_INDEPENDENTLY_READ_BACK_AFTER_THIS_PAYLOAD; exact result emitted by finalizer'
with (HERE/'validation_results.json').open('w') as f:f.write(json.dumps(validation,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
commands=read(HERE/'commands_run.json')
commands['commands'] += [
 {'command':'git ls-remote --exit-code origin refs/heads/main','kind':'exit live check','context':'authorized read-only network escalation','exit_code':0,'result':HEAD+' refs/heads/main'},
 {'command':'.venv/bin/python -B -m evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_remediation_independent_reaudit_v1.finalize_audit','kind':'final preservation and seal','result_record':'preservation_verification.json and independently measured seal readback emitted on stdout'},
]
commands['finalization']='Exact exit comparison stored in preservation_verification.json. Manifest excludes only itself. Final self SHA, count and readback result are emitted on stdout after all writes; no circular post-seal payload is appended.'
with (HERE/'commands_run.json').open('w') as f:f.write(json.dumps(commands,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
for path in HERE.glob('*.py'):ast.parse(path.read_bytes())
for path in HERE.glob('*.json'):read(path)
assert read(HERE/'findings.json')['counts']=={'MATERIAL':1,'MINOR':1,'OPTIONAL':0}
assert read(HERE/'scientific_integrity_audit.json')['replayed']==641
assert read(HERE/'candidate_inventory.json')['status']=='PASS'
assert all(x['status']=='PASS' for x in read(HERE/'predecessor_integrity.json').values())
inventory=tree(HERE);files={k:v for k,v in inventory.items() if v['type']=='file'}
assert 'artifact_sha256.json' not in files
seal={'schema':'V6_SUCCESSOR_REMEDIATION_INDEPENDENT_REAUDIT_SEAL_V1','status':'V6_SUCCESSOR_REMEDIATION_INDEPENDENT_REAUDIT_BLOCKED','HUMAN_PI_ACCEPTED':'NO','runtime_effective':'NO','execute_now':False,'excluded':['artifact_sha256.json'],'payload_count':len(files),'total_file_count':len(files)+1,'files':files,'directories':{k:v for k,v in inventory.items() if v['type']=='directory'},'symlinks':{k:v for k,v in inventory.items() if v['type']=='symlink'},'self_sha256_semantics':'Exact independent byte hash emitted after publication; no circular self reference.','raw_probe_note':'owned_syscall_sandbox/exclusive_creation_retained/empty_reserved.json intentionally contains zero bytes; it is retained syscall evidence, not a JSON document.'}
write('artifact_sha256.json',seal)
actual=tree(HERE);actualfiles={k:v for k,v in actual.items() if v['type']=='file'}
readback=read(HERE/'artifact_sha256.json')
assert readback==seal
assert set(actualfiles)==set(seal['files'])|{'artifact_sha256.json'}
assert all(actualfiles[k]==v for k,v in seal['files'].items())
assert {k:v for k,v in actual.items() if v['type']=='directory'}==seal['directories']
assert {k:v for k,v in actual.items() if v['type']=='symlink'}==seal['symlinks']
print(json.dumps({'STATUS':seal['status'],'preservation':'PASS_EXACT_EXIT_FIREWALL','seal_readback':'PASS_EXACT_PATH_SIZE_MODE_SHA','physical_file_count':len(actualfiles),'payload_count':len(files),'artifact_sha256_self':sha((HERE/'artifact_sha256.json').read_bytes()),'real_ledger':{'UNSTARTED':641,'claims':0,'terminals':0,'retries':0,'orphans':0},'findings':{'MATERIAL':1,'MINOR':1,'OPTIONAL':0}},sort_keys=True))

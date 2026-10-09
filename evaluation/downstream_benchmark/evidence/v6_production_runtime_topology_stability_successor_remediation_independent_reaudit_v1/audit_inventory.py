"""Independent read-only measurement; writes only this new audit namespace."""
import collections
import hashlib
import json
import os
import stat
import subprocess
from pathlib import Path

REPO = Path('/Users/wuyangchenxi/errpilot')
HERE = Path(__file__).resolve().parent
E = HERE.parent
C = E / 'v6_production_runtime_topology_stability_successor_remediation_final_resume_v1'
OUT = Path('/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1')
QUAL = OUT / 'qualification/production_runtime_topology_stability_successor_remediation_final_resume_v1'
HEAD = 'e492d159daf188323efcfe121aa019d5b098bfb2'
PACKAGES = {
 'v6_production_runtime_image_identity_compatibility_bridge_v1': (281, 'ee8948b829a072ff10e3a41ba086afb4151821010661d89a05ce444ba95369e8'),
 'v6_production_runtime_topology_exec_forensics_v1': (220, '96b22bb49d14b366d3d6ef7f4d9101b48cae5c6e85112c4798319d4fc7d2c1dd'),
 'v6_production_runtime_topology_stability_successor_v1': (71, 'def7f4bd8569094ce608dd1ecc8b790c690780ec827dc43c11e2207284f5f21d'),
 'v6_production_runtime_topology_stability_successor_resume_v1': (44, 'a24c561d6fc68d316908cc62813624f1acb5eff4c93121ae1704938a46a6fec4'),
 'v6_production_runtime_topology_stability_successor_independent_audit_v1': (339, 'c077bca8014466ec10adac46470671f5039da1ceed9a43b1daa372bd77337771'),
 'v6_production_runtime_topology_stability_successor_remediation_v1': (14, '5985cbfca51bdff9a146562bc064ebbe97ef16dcb77f39c587a45cff6e0e4be6'),
 'v6_production_runtime_topology_stability_successor_remediation_resume_v1': (47, 'a266e734b8d97b1205affab0e252e4d85363b9dd404cbeb424cd7c7c6f3ab3f3'),
 C.name: (764, '15161f72e034f4661baa6f2a42dfa649adab4ab33edbb899c3b10d2e3a5a7d15'),
}
PINS = {
 'production_controller_remediated_candidate.py': '7c097da628d521987dee76dba8689b0dcdd45d286996ce7509c8442bf8f82b10',
 'production_provider_remediated_candidate.py': '51f842194fd79bb9519bb6f45281a897c5249bb80558750f4660233c4c0bd438',
 'remediated_installation_candidate.json': '6f42c9740dea963fb49df7459e7d34c13b8774530c20cf26dd3a9fe7395edb01',
 'remediated_installation_plan.json': '43fc8823c8c59db7638b873762fde5f47e84aaab140e218a45b259694bfe355e',
}

def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()
def pairs(xs):
 d = {}
 for k,v in xs:
  if k in d: raise ValueError('duplicate JSON key: '+k)
  d[k] = v
 return d
def read(p): return json.loads(Path(p).read_bytes(), object_pairs_hook=pairs, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
def write(name, value):
 p = HERE / name
 assert p.parent == HERE
 with p.open('x', encoding='utf-8') as f: f.write(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)+'\n')
def ident(p):
 s = p.lstat(); d = {'mode': stat.S_IMODE(s.st_mode)}
 if stat.S_ISLNK(s.st_mode): return dict(d, type='symlink', target=os.readlink(p))
 if stat.S_ISDIR(s.st_mode): return dict(d, type='directory')
 assert stat.S_ISREG(s.st_mode), str(p)
 fd=os.open(p, os.O_RDONLY|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb') as f: h=hashlib.file_digest(f,'sha256').hexdigest()
 return dict(d,type='file',size_bytes=s.st_size,sha256=h)
def tree(root):
 result={'.':ident(root)}
 def visit(p):
  for entry in sorted(os.scandir(p),key=lambda e:e.name):
   q=Path(entry.path); d=ident(q); result[str(q.relative_to(root))]=d
   if d['type']=='directory': visit(q)
 visit(root); return result
def git(*args):
 return subprocess.check_output(['git',*args],cwd=REPO,env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'}).decode()
def snapshot():
 tracked={p:ident(REPO/p) for p in git('ls-files','-z').split('\0') if p}
 packages={k:tree(E/k) for k in PACKAGES}
 return {'tracked':tracked,'index':ident(REPO/'.git/index'),'packages':packages,'persistent_tree':tree(OUT),
         'head':git('rev-parse','HEAD').strip(),'branch':git('branch','--show-current').strip(),
         'tracked_diff':git('diff','--name-only','HEAD'),'staged_diff':git('diff','--cached','--name-only')}
def entry():
 snap=snapshot();write('entry_snapshot.json',snap)
 baseline=read(C/'entry_snapshot.json')
 pk={}
 for name,(count,pin) in PACKAGES.items():
  allpaths=snap['packages'][name]
  files={k:v for k,v in allpaths.items() if v['type']=='file'}
  m=read(E/name/'artifact_sha256.json')
  errors=[]
  if len(files)!=count:errors.append('physical count')
  if files['artifact_sha256.json']['sha256']!=pin:errors.append('self SHA')
  if set(files)!=set(m['files'])|{'artifact_sha256.json'}:errors.append('complete relative path set')
  for path,ref in m['files'].items():
   if Path(path).is_absolute() or any(x in ('.','..','') for x in path.split('/')):errors.append('invalid path '+path)
   if not {'sha256','size_bytes'}<=ref.keys():errors.append('invalid row '+path)
   for key in ('sha256','size_bytes','mode','type'):
    if key in ref and files.get(path,{}).get(key)!=ref[key]:errors.append(path+':'+key)
  if any(v['type']=='symlink' for v in allpaths.values()):errors.append('package symlink')
  pk[name]={'status':'PASS' if not errors else 'FAIL','errors':errors,'schema':m.get('schema'),'physical_files':len(files),'manifest_self_sha256':files['artifact_sha256.json']['sha256'],'files':files}
 write('candidate_inventory.json',pk.pop(C.name));write('predecessor_integrity.json',pk)
 inv=read(C/'synthetic_output_inventory.json')
 actual=tree(QUAL);actual.pop('.')
 errors=[p for p in set(actual)|set(inv['files']) if actual.get(p)!=inv['files'].get(p)]
 historical={k:v for k,v in snap['persistent_tree'].items() if k!='qualification/'+QUAL.name and not k.startswith('qualification/'+QUAL.name+'/')}
 old_errors=[p for p in set(historical)|set(baseline['persistent_tree']) if historical.get(p)!=baseline['persistent_tree'].get(p)]
 write('synthetic_output_verification.json',{'status':'PASS' if not errors and not old_errors else 'FAIL','root':str(QUAL),'measured_types':dict(collections.Counter(x['type'] for x in actual.values())),'exact_inventory_differences':errors,'historical_persistent_differences':old_errors,'historical_file_count':sum(x['type']=='file' for x in historical.values()),'followed_symlinks':False,'actual_entries':actual})
 can=read(REPO/'evaluation/downstream_benchmark/v6_current_state.json')
 work=read(REPO/'evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/work_items_candidate.json')
 ledger={n:sorted(os.listdir(OUT/'ledger'/n)) for n in ('claims','terminals','locks')}
 candidate=read(C/'remediated_installation_candidate.json');plan=read(C/'remediated_installation_plan.json')
 targets=sorted(set(baseline['production_targets_absent'])|set(candidate['proposed_future_targets'].values()))
 exists={p:os.path.lexists(REPO/p) for p in targets}
 checks={'tracked_count':len(snap['tracked']),'tracked_matches_preconstruction':snap['tracked']==baseline['tracked'],
 'index_matches_preconstruction':snap['index']==baseline['index'],'head':snap['head'],'branch':snap['branch'],
 'canonical_sha256':sha((REPO/'evaluation/downstream_benchmark/v6_current_state.json').read_bytes()),
 'canonical_state':can['projection']['state'],'event_count':can['event_count'],'event_3_id':can['event_head']['event_id'],
 'event_files':{x['path']:ident(REPO/x['path']) for x in can['event_chain']},
 'ledger_directory_entries':ledger,'real_ledger':{'UNSTARTED':len(work['items']),'claims':0 if not ledger['claims'] else len(ledger['claims']),'terminals':len(ledger['terminals']),'locks':len(ledger['locks']),'retries':0,'orphans':0},
 'ledger_method':'read-only inventory; no Ledger constructor called','airos_current_state_present':(REPO/'.airos/current_state.md').exists(),
 'source_and_descriptor_pins':{n:{'expected':h,'measured':sha((C/n).read_bytes())} for n,h in PINS.items()},
 'candidate_flags':{k:candidate[k] for k in ('candidate_only','HUMAN_PI_ACCEPTED','runtime_effective','execute_now')},
 'plan_flags':{k:plan[k] for k in ('candidate_only','HUMAN_PI_ACCEPTED','runtime_effective','execute_now')},
 'production_target_exists':exists,'live_origin_query':{'command':'git ls-remote --exit-code origin refs/heads/main','exit_code':0,'observed':HEAD,'initial_sandbox_attempt':'DNS failure; separately authorized read-only network retry succeeded'},
 'tracked_diff':snap['tracked_diff'],'staged_diff':snap['staged_diff']}
 standard=set(git('ls-files','--others','--exclude-standard','-z').split('\0'))
 allsealed={str((E/n/p).relative_to(REPO)) for n in PACKAGES for p,v in snap['packages'][n].items() if v['type']=='file'}
 checks['existing_evidence_physical_files']=len(allsealed);checks['ignored_sealed_paths']=sorted(allsealed-standard)
 write('entry_verification.json',checks)
 print(json.dumps({'packages':{k:{a:v[a] for a in ('status','physical_files','errors')} for k,v in pk.items()},'candidate_files':len(snap['packages'][C.name]),'synthetic_differences':len(errors),'old_output_differences':len(old_errors),'tracked':len(snap['tracked']),'tracked_unchanged':checks['tracked_matches_preconstruction'],'index_unchanged':checks['index_matches_preconstruction']}))

if __name__=='__main__':entry()

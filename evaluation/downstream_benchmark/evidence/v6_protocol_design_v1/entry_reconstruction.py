"""Read-only reconstruction; writes scratch evidence only, never dispatches subjects."""
import csv, hashlib, io, json, os, stat, subprocess, sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path('/Users/wuyangchenxi/errpilot'); B=ROOT/'evaluation/downstream_benchmark'
EXT=Path('/Users/wuyangchenxi/errpilot-benchmark-work'); O=EXT/'v5_3x3_buggy_fixed_oracle_screening_v1'
HEAD='26a9264105f303dc0101f74c9315c41ab1c9e265'
SOURCE='11c5f1eea954a42132cfd06bf257766a7963e0fd'; TREE='d00ce0495ba73abe50317599f48bced3c9afe4b3'
UH='78208adf610a50542be6dfbd03a9b25960ba0b5cfc80768b08ffe7a4c78f3b8c'
sys.path.insert(0,str(ROOT))
from evaluation.downstream_benchmark.screening import build_candidate_universe as builder
from evaluation.downstream_benchmark.screening.executor import classify_execution_records
from evaluation.downstream_benchmark.screening.validate_pre_eligibility_state_v5 import validate_successor
checks=[]
def check(name, condition, details=None):
    checks.append({'check':name,'status':'PASS' if condition else 'FAIL','details':details})
    if not condition: raise RuntimeError(name)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csvrows(p): return list(csv.DictReader(Path(p).open(newline='',encoding='utf-8')))
def j(p):return json.loads(Path(p).read_text())
def git(*args,root=ROOT):return subprocess.check_output(['git','-C',str(root),*args],text=True).strip()
def identity(p):
    p=Path(p);s=p.lstat();symlink=stat.S_ISLNK(s.st_mode)
    return {'sha256':hashlib.sha256(os.readlink(p).encode()).hexdigest() if symlink else sha(p),'mode':stat.S_IMODE(s.st_mode),'type':'symlink' if symlink else 'file'}
check('repo_root',git('rev-parse','--show-toplevel')==str(ROOT))
check('branch',git('branch','--show-current')=='main')
check('local_HEAD',git('rev-parse','HEAD')==HEAD)
check('entry_clean',git('status','--porcelain=v1','--untracked-files=all')=='')
check('index_clean',git('diff','--cached','--name-only')=='')
# Live network result was independently obtained by the approved read-only tool call.
live={'command':'git ls-remote origin refs/heads/main','observed_oid':HEAD,'observation':'successful elevated network query in this transaction; sandbox DNS failed first','remote_ref':'refs/heads/main'}
check('live_origin_main',live['observed_oid']==HEAD,live)
check('source_commit_tree',git('rev-parse','HEAD',root=EXT/'bugsinpy')==SOURCE and git('rev-parse','HEAD^{tree}',root=EXT/'bugsinpy')==TREE)
check('source_clean_detached',git('status','--porcelain=v1','--untracked-files=all',root=EXT/'bugsinpy')=='' and git('rev-parse','--abbrev-ref','HEAD',root=EXT/'bugsinpy')=='HEAD')
check('universe_hash',sha(B/'candidate_universe.csv')==UH)
u=csvrows(B/'candidate_universe.csv'); ranked=sorted((r for r in u if r['metadata_status']=='METADATA_ELIGIBLE'),key=lambda r:int(r['candidate_rank']))
check('501_census_500_unique_ranked',len(u)==501 and len(ranked)==500 and len({r['canonical_case_id'] for r in u})==501 and [int(r['candidate_rank']) for r in ranked]==list(range(1,501)))
check('seed_rank_digest_order',str(builder.SEED)=="20260922" and all(r['rank_sha256']==hashlib.sha256(f"20260922|candidate|{r['canonical_case_id']}".encode()).hexdigest() for r in ranked) and ranked==sorted(ranked,key=lambda r:(r['rank_sha256'],r['canonical_case_id'])))
check('all_source_identities',all(r['bugsinpy_source_commit']==SOURCE for r in u))
records=builder.census(EXT/'bugsinpy');selected,diversity=builder.rank_and_select(records)
builder.write_universe(Path('/private/tmp/errpilot_v6_reproduced_universe.csv'),records,SOURCE)
check('metadata_census_byte_reproduction',sha('/private/tmp/errpilot_v6_reproduced_universe.csv')==UH and not diversity)
counts=Counter(); dispositions={}; admissions=[]; initial_skips=[]; lineage=[]
# Initial skips have no literal decision column; their disposition is uniquely replayed.
for r in ranked:
    capped=counts[r['project']]>=4; decision='SKIP_PROJECT_CAP' if capped else 'ADMIT'
    ref={'path':str(B/'candidate_universe.csv'),'sha256':UH,'row_key':r['canonical_case_id'],'csv_record_ordinal':u.index(r)+1,'lineage_mode':'DETERMINISTIC_INITIAL_TRAVERSAL_REPLAY','rule_path':str(B/'SCREENING_SPEC_V1.md'),'rule_sha256':sha(B/'SCREENING_SPEC_V1.md'),'rule_section':'D','implementation_path':str(B/'screening/build_candidate_universe.py'),'implementation_sha256':sha(B/'screening/build_candidate_universe.py')}
    item={'case_id':r['canonical_case_id'],'project':r['project'],'candidate_rank':int(r['candidate_rank']),'rank_sha256':r['rank_sha256'],'predecessor_disposition':decision,'predecessor_evidence':ref}
    dispositions[item['case_id']]=item
    if not capped:counts[r['project']]+=1;admissions.append(item['case_id'])
    else:initial_skips.append(item['case_id'])
    if len(admissions)==40:break
initial=sorted((r for r in u if r['selected_initial_40']=='true'),key=lambda r:int(r['initial_selection_order']))
check('initial_40_exact_rank71_31_skips',admissions==[r['canonical_case_id'] for r in initial] and int(r['candidate_rank'])==71 and len(initial_skips)==31)
cursor=71;skip_counts={'initial':31}
for n,end,added in [(1,102,10),(2,246,10),(3,500,7)]:
    path=B/f'expansion_block_{n:02d}_traversal.csv'; rows=csvrows(path); admitted=[]
    check(f'block_{n}_complete_rank_range',[int(r['candidate_rank']) for r in rows]==list(range(cursor+1,end+1)))
    for idx,t in enumerate(rows,1):
        r=ranked[int(t['candidate_rank'])-1];decision='SKIP_PROJECT_CAP' if counts[r['project']]>=4 else 'ADMIT'
        check_name=f'block_{n}_exact_traversal'
        if not (t['canonical_case_id']==r['canonical_case_id'] and t['project']==r['project'] and t['rank_sha256']==r['rank_sha256'] and t['metadata_status']==r['metadata_status'] and int(t['project_count_before'])==counts[r['project']] and t['decision']==decision and r['canonical_case_id'] not in dispositions):raise RuntimeError(check_name)
        expected_reason='CUMULATIVE_PROJECT_CAP_4_REACHED' if decision=='SKIP_PROJECT_CAP' else ('SECTION_M_TERMINAL_PARTIAL_BLOCK_NEXT_RANKED_UNDER_PROJECT_CAP' if n==3 else 'SECTION_M_NEXT_RANKED_UNDER_PROJECT_CAP')
        if t['decision_reason']!=expected_reason:raise RuntimeError(check_name+' reason')
        dispositions[r['canonical_case_id']]={'case_id':r['canonical_case_id'],'project':r['project'],'candidate_rank':int(r['candidate_rank']),'rank_sha256':r['rank_sha256'],'predecessor_disposition':decision,'predecessor_evidence':{'path':str(path),'sha256':sha(path),'row_key':r['canonical_case_id'],'csv_record_ordinal':idx,'lineage_mode':'LITERAL_FROZEN_TRAVERSAL_ROW'}}
        if decision=='ADMIT':
            counts[r['project']]+=1;admitted.append(r['canonical_case_id']);admissions.append(r['canonical_case_id'])
            if int(t['expansion_order_if_admitted'])!=len(admitted):raise RuntimeError('admission order')
        elif t['expansion_order_if_admitted']:raise RuntimeError('skip order')
    stored=sorted(csvrows(B/f'expansion_block_{n:02d}.csv'),key=lambda r:int(r['expansion_order']))
    check(f'block_{n}_admissions_exact',len(admitted)==added and admitted==[r['canonical_case_id'] for r in stored])
    skip_counts[f'block_{n:02d}']=len(rows)-added;cursor=end
check('67_admissions_433_skips_500_partition',len(admissions)==67 and len(set(admissions))==67 and len(dispositions)==500 and Counter(x['predecessor_disposition'] for x in dispositions.values())=={'ADMIT':67,'SKIP_PROJECT_CAP':433})
pool=[dispositions[r['canonical_case_id']] for r in ranked if dispositions[r['canonical_case_id']]['predecessor_disposition']=='SKIP_PROJECT_CAP']
ex=csvrows(B/'exclusions_v5.csv'); exids={r['case_id'] for r in ex}; outcomes=j(O/'case_outcomes.json'); screened={r['case_id'] for r in outcomes}
check('39_exclusions_exact_split',len(ex)==len(exids)==39 and Counter(r['exclusion_reason'] for r in ex)=={'UNSUPPORTED_ENVIRONMENT':11,'DEPENDENCY_SETUP_FAILURE':26,'ORACLE_COMMAND_INVALID':2})
check('static_v4_v5_validation',validate_successor(B)['accepted_exclusions']==39)
check('28_screened_partition_admissions',len(screened)==len(outcomes)==28 and not(exids & screened) and exids|screened==set(admissions))
check('9_12_7_scientific_partition',Counter(r['case_status'] for r in outcomes)=={'ELIGIBLE':9,'INELIGIBLE_REPRODUCIBILITY_OUTCOME':12,'INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY':7})
cc=j(O/'controller_checkpoint.json')
check('oracle_same_HEAD_28_invocations',cc['execution_head']==HEAD and len(cc['case_invocations'])==28 and {x['case_id'] for x in cc['case_invocations']}==screened)
byout={x['case_id']:x for x in outcomes}; checkpoint_refs={}
for inv in cc['case_invocations']:
    cp=Path(inv['checkpoint_path']); ck=j(cp)
    if sha(cp)!=inv['checkpoint_sha256'] or classify_execution_records(ck['records'])!=byout[inv['case_id']]['case_status'] or ck['classification']!=byout[inv['case_id']]['case_status']:raise RuntimeError('checkpoint lineage/classifier')
    for label in ('BUGGY','FIXED'):
        if [r['trial_result'] for r in ck['records'] if r['revision_label']==label]!=byout[inv['case_id']][label]:raise RuntimeError('repetition lineage')
    checkpoint_refs[inv['case_id']]={'path':str(cp),'sha256':sha(cp)}
check('28_checkpoint_hashes_and_classifiers',True)
account=j(O/'execution_accounting.json');check('168_historical_consumed_no_new_execution',len(account)==168 and all(r['consumed'] and r['dispatched'] for r in account) and sum(r['completed'] for r in account)==126)
fh=j(O/'final_hashes.json');check('external_final_hashes',all(sha(O/n)==h for n,h in fh.items() if n!='evidence_files'))
ev=j(O/'evidence_sha256.json');check('1737_original_evidence_hashes',len(ev)==fh['evidence_files']==1737 and len({r['path'] for r in ev})==1737 and all(Path(r['path']).stat().st_size==r['bytes'] and sha(r['path'])==r['sha256'] for r in ev))
inputs=j(O/'external_input_inventory.json');check('143_original_external_inputs',len(inputs)==143 and all(identity(p)['sha256']==d['sha256'] and identity(p)['mode']==d['mode'] for p,d in inputs.items()))
oldrepo=j(O/'repository_input_inventory.json');tracked={p:identity(ROOT/p) for p in git('ls-files').splitlines()}
check('493_repository_input_preservation',len(oldrepo)==len(tracked)==493 and all(tracked[p]['sha256']==d['sha256'] and tracked[p]['mode']==d['mode'] for p,d in oldrepo.items()))
check('pool_disjoint_unique_lineage',len(pool)==433 and len({r['case_id'] for r in pool})==433 and not ({r['case_id'] for r in pool}&(set(admissions)|exids|screened)))
check('no_allocation_in_controlling_records',not csvrows(B/'cases_manifest.csv') and j(O/'post_run_audit.json')['allocation_performed'] is False)
repo_v6=[str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if '.git' not in p.parts and any('v6' in s.lower() for s in p.relative_to(ROOT).parts)]
external_v6=[p.name for p in EXT.iterdir() if 'v6' in p.name.lower()]
check('no_successor_owner',not repo_v6 and not external_v6,{'repository_names':repo_v6,'external_governance_top_level':external_v6})
check('no_later_allocation_artifact',not [str(p) for p in B.rglob('*') if p.is_file() and any(s in p.name.lower() for s in ('allocation','pilot_selection','final_selection','eligible_pool'))] and not [p.name for p in EXT.iterdir() if any(s in p.name.lower() for s in ('allocation','pilot','final_selection','eligible_pool'))])
request=Path('/Users/wuyangchenxi/.codex/attachments/94b454a0-d0f6-42ec-8af0-d5aa1449fbbb/已粘贴的文本.txt')
result={'schema':'V6_DESIGN_ENTRY_VERIFICATION_PROPOSAL_V1','status':'PASS','verified_at_utc':datetime.now(timezone.utc).isoformat(),'repository':str(ROOT),'branch':'main','entry_head':HEAD,'live_origin_main':live,'instruction':{'path':str(request),'sha256':sha(request)},'missing_optional_repo_instructions':['AGENTS.md','.airos/current_state.md','.airos/contracts/'],'checks':checks,'tracked_entry_inventory':tracked,'external_original_input_inventory':inputs,'source':{'path':str(EXT/'bugsinpy'),'commit':SOURCE,'tree':TREE},'universe_sha256':UH,'seed':20260922,'admissions':admissions,'pool':pool,'outcomes':outcomes,'exclusions':ex,'checkpoint_references':checkpoint_refs,'skip_origin_counts':skip_counts,'pool_summary':{'count':433,'min_rank':pool[0]['candidate_rank'],'max_rank':pool[-1]['candidate_rank'],'project_counts':dict(sorted(Counter(r['project'] for r in pool).items()))},'historical_validator_compatibility':{'command':'python3 -B -m evaluation.downstream_benchmark.screening.validate_pre_eligibility_state_v5 --verify-production-evidence','exit_code':1,'message':'BLOCKED: oracle outcomes exist in screening_evidence','interpretation':'historical zero-oracle boundary; static validation passes; original post-oracle evidence independently hashed'}}
Path('/private/tmp/errpilot_v6_design_entry.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'status':'PASS','checks':len(checks),'tracked_files':len(tracked),'external_evidence_files':len(ev),'external_inputs':len(inputs),'pool':result['pool_summary'],'skip_origins':skip_counts},indent=2))

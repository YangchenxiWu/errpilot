"""Read-only design checker. No subject, Docker, network, oracle or production dispatch.

Run from any cwd: python3 -B /absolute/path/to/validate_proposal.py
Checks proposal data and preserved original evidence; negative probes mutate in-memory copies.
This is not V6 execution machinery or a canonical successor-state writer.
"""
import copy
import csv
import hashlib
import json
import os
import stat
import subprocess
from collections import Counter
from pathlib import Path

BENCHMARK = Path(__file__).resolve().parents[2]
ROOT = BENCHMARK.parents[1]
EVIDENCE = Path(__file__).resolve().parent
EXPECTED_HEAD = '26a9264105f303dc0101f74c9315c41ab1c9e265'
SOURCE = '11c5f1eea954a42132cfd06bf257766a7963e0fd'
TREE = 'd00ce0495ba73abe50317599f48bced3c9afe4b3'
UNIVERSE = '78208adf610a50542be6dfbd03a9b25960ba0b5cfc80768b08ffe7a4c78f3b8c'
EXTERNAL = Path('/Users/wuyangchenxi/errpilot-benchmark-work/v5_3x3_buggy_fixed_oracle_screening_v1')
FIREWALL = {'V6_PROTOCOL_ACTIVATED','V6_MEMBERSHIP_FROZEN','NEW_SUBJECT_MATERIALIZED',
            'ENVIRONMENT_PREPARED','IMAGE_BUILT','ORACLE_REPETITION_EXECUTED',
            'ORACLE_REPETITION_CONSUMED','PYTEST_REPAIR_PERFORMED','UNRESOLVED_7_RERUN_EXECUTED',
            'PILOT_SELECTED','FINAL_CASE_SELECTED','V5_ARTIFACT_REWRITTEN','PRIOR_EXCLUSION_REOPENED',
            'SCIENTIFIC_FAILURE_RESCUED','GIT_STAGE_PERFORMED','GIT_COMMIT_PERFORMED','GIT_PUSH_PERFORMED'}
STATE_NAMES = ['DESIGN_PROPOSED','HUMAN_PI_ACCEPTED','FROZEN','CENSUS_MEMBERSHIP_PERSISTED',
               'PREPARATION_OPEN','PREPARATION_COMPLETE','ENVIRONMENT_READY_POPULATION_FROZEN',
               'ORACLE_SCREENING_OPEN','ORACLE_SCREENING_COMPLETE','ELIGIBLE_POOL_FROZEN',
               'PILOT_FINAL_ALLOCATION_OPEN','ALLOCATION_COMPLETE']
ALLOW_NEW = {'V6_FINITE_SAME_UNIVERSE_CENSUS_PROTOCOL_DESIGN_PROPOSAL.md',
             'v6_reconsideration_pool_proposal.csv','v6_predecessor_evidence_bridge_proposal.json',
             'v6_capacity_successor_contract_proposal.json'} | {
             'evidence/v6_protocol_design_v1/'+n for n in ['entry_verification.json','entry_reconstruction.py',
             'predecessor_artifact_sha256.json','validate_proposal.py','validation_results.json',
             'RUN_REPORT.md','artifact_sha256.json']}


def sha(path):
    path = Path(path)
    return hashlib.sha256(os.readlink(path).encode() if path.is_symlink() else path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def read_csv(path):
    with Path(path).open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_reference(item):
    require(sha(item['path']) == item['sha256'], 'reference digest drift: '+item['path'])


def reconstruct():
    """Independent replay from original universe and literal traversal CSVs."""
    rows = read_csv(BENCHMARK/'candidate_universe.csv')
    ranked = sorted((r for r in rows if r['candidate_rank']), key=lambda r:int(r['candidate_rank']))
    counts = Counter()
    result = []
    admitted = []
    cursor = 0
    for r in ranked:
        capped = counts[r['project']] == 4
        result.append((r, 'SKIP_PROJECT_CAP' if capped else 'ADMIT', {
            'path':str(BENCHMARK/'candidate_universe.csv'),'sha256':UNIVERSE,
            'csv_record_ordinal':rows.index(r)+1,'row_key':r['canonical_case_id'],
            'lineage_mode':'DETERMINISTIC_INITIAL_TRAVERSAL_REPLAY'}))
        if not capped:
            counts[r['project']] += 1
            admitted.append(r['canonical_case_id'])
        cursor = int(r['candidate_rank'])
        if len(admitted) == 40:
            break
    actual_initial = sorted((r for r in rows if r['selected_initial_40']=='true'), key=lambda r:int(r['initial_selection_order']))
    require(admitted == [r['canonical_case_id'] for r in actual_initial] and cursor == 71, 'initial replay drift')
    require(len({r['project'] for r in actual_initial}) == 15, 'initial diversity replay drift')
    for n, endpoint, target in [(1,102,10),(2,246,10),(3,500,7)]:
        path = BENCHMARK/f'expansion_block_{n:02d}_traversal.csv'
        traversed = read_csv(path)
        require([int(t['candidate_rank']) for t in traversed] == list(range(cursor+1,endpoint+1)), 'incomplete traversal')
        block_admissions = []
        for ordinal, t in enumerate(traversed,1):
            r = ranked[int(t['candidate_rank'])-1]
            decision = 'SKIP_PROJECT_CAP' if counts[r['project']] == 4 else 'ADMIT'
            require(t['canonical_case_id']==r['canonical_case_id'] and t['project']==r['project']
                    and t['rank_sha256']==r['rank_sha256'] and t['decision']==decision
                    and int(t['project_count_before'])==counts[r['project']], 'literal traversal mismatch')
            result.append((r,decision,{'path':str(path),'sha256':sha(path),'csv_record_ordinal':ordinal,
                                      'row_key':r['canonical_case_id'],'lineage_mode':'LITERAL_FROZEN_TRAVERSAL_ROW'}))
            if decision == 'ADMIT':
                counts[r['project']] += 1
                admitted.append(r['canonical_case_id'])
                block_admissions.append(r['canonical_case_id'])
        block = sorted(read_csv(BENCHMARK/f'expansion_block_{n:02d}.csv'), key=lambda r:int(r['expansion_order']))
        require(len(block_admissions)==target and block_admissions==[r['canonical_case_id'] for r in block], 'block admission drift')
        cursor = endpoint
    require(len(result)==500 and len(admitted)==len(set(admitted))==67, 'historical partition drift')
    return rows, ranked, admitted, [(r,e) for r,d,e in result if d=='SKIP_PROJECT_CAP']


def validate_pool(pool, expected, admissions, exclusions, screened):
    require(len(pool)==433, 'count must be exactly 433')
    ids = [r['case_id'] for r in pool]
    require(len(set(ids))==433, 'duplicate identity')
    require(not set(ids).intersection(set(admissions)|set(exclusions)|set(screened)), 'historical overlap')
    require(ids==[r['canonical_case_id'] for r,_ in expected], 'exact mechanical pool/order mismatch')
    for ordinal, (p,(u,e)) in enumerate(zip(pool,expected),1):
        require(p['proposal_order']==str(ordinal), 'inventory order drift')
        require(p['project']==u['project'] and p['bugsinpy_bug_id']==u['bugsinpy_bug_id'], 'project/key drift')
        require(p['frozen_rank']==u['candidate_rank'] and p['rank_sha256']==u['rank_sha256'], 'rank drift')
        require(p['candidate_universe_sha256']==UNIVERSE and p['seed']=='20260922', 'universe/seed drift')
        require(p['bugsinpy_commit']==SOURCE and p['bugsinpy_tree']==TREE, 'source identity drift')
        require(p['predecessor_disposition']=='SKIP_PROJECT_CAP', 'reopened other disposition')
        require(p['design_state']=='PROPOSED_V6_CANDIDATE', 'activation disguised as proposal')
        for key, field in [('path','predecessor_evidence_path'),('sha256','predecessor_evidence_sha256'),
                           ('csv_record_ordinal','predecessor_csv_record_ordinal'),('row_key','predecessor_row_key'),
                           ('lineage_mode','lineage_mode')]:
            require(str(e[key])==p[field], 'nonunique/wrong lineage: '+field)
        if e['lineage_mode']=='DETERMINISTIC_INITIAL_TRAVERSAL_REPLAY':
            require(p['predecessor_rule_path']==str(BENCHMARK/'SCREENING_SPEC_V1.md') and
                    p['predecessor_rule_sha256']==sha(BENCHMARK/'SCREENING_SPEC_V1.md') and
                    p['predecessor_rule_section']=='D' and
                    p['predecessor_implementation_path']==str(BENCHMARK/'screening/build_candidate_universe.py') and
                    p['predecessor_implementation_sha256']==sha(BENCHMARK/'screening/build_candidate_universe.py'), 'initial replay rule identity missing')
        else:
            require(all(p[k]=='' for k in ['predecessor_rule_path','predecessor_rule_sha256','predecessor_rule_section',
                                           'predecessor_implementation_path','predecessor_implementation_sha256']), 'literal lineage confused with replay')


def validate_contract(c):
    require(c['candidate_only'] is True and c['design_status']=='DESIGN_PROPOSED', 'candidate lifecycle drift')
    require(c['authority']['design_only'] is True and c['authority']['execution_authorized'] is False, 'execution authority drift')
    require(c['lifecycle']=={k:'NO' for k in ['HUMAN_PI_ACCEPTED','FROZEN','PERSISTED','COMMITTED','REMOTE_PUBLISHED']}, 'lifecycle grant')
    require(c['firewall']=={k:'NO' for k in FIREWALL}, 'firewall grant/missing field')
    p=c['predecessor'];require(p['head']==EXPECTED_HEAD and p['source_commit']==SOURCE and p['source_tree']==TREE and p['candidate_universe_sha256']==UNIVERSE and p['seed']==20260922, 'predecessor identity drift')
    require([p['census_rows'],p['ranked_rows'],p['admissions'],p['accepted_exclusions'],p['screened_cases']]==[501,500,67,39,28] and p['outcome_counts']=={'eligible':9,'scientific_ineligible':12,'infrastructure_unresolved':7}, 'predecessor count drift')
    j=c['authority']['accepted_decisions'];require(j=={'J1':'RETAIN_28','J2':'YES','J3':'YES','J4':'YES','J5':'NO','J6':'NO','J7':{'change':'REQUIRED','scope':'CANDIDATE_ADMISSION_CAP_AND_PRIOR_CAP_SKIP_TREATMENT_ONLY','final_sample_project_cap':4},'J8':'NO','J9':'YES','J10':'YES','J11':'RETAIN_24_PLUS_4','J12':'V6_FINITE_SAME_UNIVERSE_CENSUS_WITH_EVIDENCE_CONTINUITY'}, 'accepted decision drift')
    census=c['census'];require(census['expected_count']==census['actual_count']==433 and census['candidate_admission_project_cap'] is None and census['preparation_project_cap'] is None and census['must_process_all_members'] is True and census['stop_when_28_eligible'] is False and census['logical_membership_complete_before_outcomes'] is True and census['outcome_conditioned_later_membership'] is False and census['order']=='ORIGINAL_FROZEN_RANK_ASCENDING' and census['batch_partition_full_pool_before_outcomes'] is True, 'census optional stopping/cap drift')
    prep=c['preparation'];require(prep['execution_authorized'] is False and prep['attempt_policy']=='ONCE_NO_AUTOMATIC_RETRY' and prep['later_success_overwrites_failure'] is False, 'preparation authority/retry drift')
    s=c['screening'];require(s['schedule']==[{'variant':v,'repetition':i} for v in ['BUGGY','FIXED'] for i in [1,2,3]] and s['eligible_buggy']==['FAIL']*3 and s['eligible_fixed']==['PASS']*3 and s['all_six_required'] is True and s['majority_vote'] is False and s['fourth_repetition'] is False and s['scientific_rescue'] is False, 'oracle criterion drift')
    require(s['execution_authorized'] is False and s['subcommand_timeout_seconds']==300 and s['trial_timeout_seconds']==900 and s['platform']=='linux/amd64' and s['network']=='NONE' and s['fresh_state_every_trial'] is True and s['raw_evidence_immutable'] is True, 'runtime drift')
    require(s['classifications']==['ELIGIBLE','INELIGIBLE_REPRODUCIBILITY_OUTCOME','INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY','INTERRUPTED_NOT_ELIGIBILITY','INCOMPLETE_NOT_ELIGIBILITY','CASE_INVALIDATED'], 'scientific/infrastructure distinction drift')
    require(s['composite_trial_semantics']=={'commands_per_trial':'N>=1 frozen recognized commands in original script order','command_order_preserved':True,'direct_argv_shell':False,'continue_after_valid_nonzero':True,'trial_pass':'all N valid completed commands exit zero','trial_fail':'all N valid completed commands and at least one nonzero','subcommands_count_as_extra_repetitions':False}, 'composite oracle semantics drift')
    require(c['evidence_continuity']=={'eligible_9':'GRANDFATHER_NO_CAPACITY_RERUN','ineligible_12':'FINAL_UNCHANGED_ORACLE_NO_RESCUE','unresolved_7':'SEPARATE_VERSIONED_TRACK_OUTSIDE_V6_EXECUTION','exclusions_39':'PRESERVED_NOT_REOPENED','cap_skips_433':'PROPOSED_PROSPECTIVE_RECONSIDERATION_ONLY','predecessor_rewritten':False,'raw_evidence_cloned':False}, 'predecessor evidence continuity drift')
    a=c['allocation'];require([a['required_total'],a['pilot_count'],a['final_count'],a['final_sample_project_cap'],a['minimum_final_projects']]==[28,4,24,4,6] and a['pilot_permanent_final_exclusion'] is True and a['pilot_outcomes_affect_selection'] is False and a['selection_authorized'] is False, 'allocation invariant drift')
    require(a['pilot_selection_rule'] is None and a['pilot_rule_status']=='REQUIRES_HUMAN_PI_DECISION_D7' and a['pilot_project_cap'] is None and a['combined_pilot_final_project_cap'] is None, 'invented pilot rule/cap')
    require(a['final_seed']==20260922 and a['final_digest_input']=='20260922|final|<source_project>|<bugsinpy_bug_id>|<case_id>' and a['final_sort']==['digest','source_project','bugsinpy_bug_id','case_id'] and a['robustness_count']==6 and a['robustness_digest_input']=='20260922|robustness|<case_id>' and a['condition_order_input']=='20260922|order|<case_id>|<repetition_index>', 'allocation algorithm drift')
    u=c['unresolved_7_integration'];require(u['execution_authorized'] is False and u['prerequisite_to_expansion'] is False and u['required_before_inclusion']==['HUMAN_PI_ACCEPTED','FROZEN','PERSISTED','COMMITTED'] and u['own_versioned_authority_required'] is True and u['exact_supersession_required'] is True and u['late_outcome_inclusion'] is False and u['cutoff']=='BEFORE_IMMUTABLE_ALLOCATION_OPEN_GATE_COMMIT_AND_POOL_SNAPSHOT_DIGEST' and u['cutoff_status']=='PROPOSED_D6', 'unresolved-seven boundary drift')
    machine=c['state_machine'];require(machine['states']==STATE_NAMES and machine['current_state']=='DESIGN_PROPOSED' and len(machine['transitions'])==11, 'state coverage drift')
    for i,t in enumerate(machine['transitions']):require(t['from']==STATE_NAMES[i] and t['to']==STATE_NAMES[i+1] and t['human_pi_gate'].startswith('HUMAN_PI_') and bool(t['requires']) and t['grants_downstream_execution_automatically'] is False, 'automatic state authority')
    require(len({t['human_pi_gate'] for t in machine['transitions']})==11 and machine['commit_and_publication_separate_gates'] is True, 'gate collapse')
    exhaustion=c['exhaustion'];require(exhaustion['complete_census_required'] is True and exhaustion['all_ready_screening_slots_accounted'] is True and exhaustion['stop_when_28_eligible'] is False and exhaustion['infeasible_behavior']=='FAIL_CLOSED_NEW_HUMAN_PI_PROTOCOL_ADJUDICATION_REQUIRED', 'exhaustion drift')
    require(set(exhaustion['automatic_changes_forbidden'])=={'source_snapshot','candidate_universe','rank_above_500','seed','reopen_scientific_failures','oracle_rule','target_N','final_project_cap','new_successor','unresolved_7_rerun'}, 'exhaustion loophole')
    require(set(c['decision_surface'])=={f'D{i}' for i in range(1,9)} and all(d['classification']=='REQUIRES_HUMAN_PI_DECISION' for d in c['decision_surface'].values()), 'manufactured exact-decision uniqueness')
    require(c['current_state_ledger_proposal']['not_instantiated'] is True and c['current_state_ledger_proposal']['new_scientific_results_assigned']==0 and c['proposed_successor_identifiers']['canonical_files_created'] is False, 'canonical state activation')
    require(c['next_gate']=='HUMAN_PI_REVIEW_OF_V6_FINITE_SAME_UNIVERSE_CENSUS_PROTOCOL_DESIGN', 'next gate drift')


def main():
    entry=read_json(EVIDENCE/'entry_verification.json')
    universe,ranked,admissions,expected=reconstruct()
    pool=read_csv(BENCHMARK/'v6_reconsideration_pool_proposal.csv')
    exclusions=read_csv(BENCHMARK/'exclusions_v5.csv')
    outcomes=read_json(EXTERNAL/'case_outcomes.json')
    screened=[o['case_id'] for o in outcomes]
    exids=[o['case_id'] for o in exclusions]
    contract=read_json(BENCHMARK/'v6_capacity_successor_contract_proposal.json')
    bridge=read_json(BENCHMARK/'v6_predecessor_evidence_bridge_proposal.json')
    positive=[];negative=[]
    def check(name, fn):
        fn();positive.append({'check':name,'status':'PASS'})
    def yes(name, condition):
        check(name,lambda:require(condition,name))
    yes('entry_36_checks_all_pass',len(entry['checks'])==36 and all(x['status']=='PASS' for x in entry['checks']))
    yes('source_universe_immutable',sha(BENCHMARK/'candidate_universe.csv')==UNIVERSE and len(universe)==501 and len(ranked)==500)
    yes('numeric_ranks_1_through_500',[int(r['candidate_rank']) for r in ranked]==list(range(1,501)))
    yes('seed_digest_rank_order',all(r['rank_sha256']==hashlib.sha256(f"20260922|candidate|{r['canonical_case_id']}".encode()).hexdigest() for r in ranked) and ranked==sorted(ranked,key=lambda r:(r['rank_sha256'],r['canonical_case_id'])))
    check('exact_pool_lineage_replay',lambda:validate_pool(pool,expected,admissions,exids,screened))
    yes('433_unique_proposed_rows',len(pool)==len({r['case_id'] for r in pool})==433)
    yes('67_prior_admissions_exact',len(admissions)==len(set(admissions))==67 and admissions==entry['admissions'])
    yes('39_exclusion_split',len(exids)==len(set(exids))==39 and Counter(r['exclusion_reason'] for r in exclusions)=={'UNSUPPORTED_ENVIRONMENT':11,'DEPENDENCY_SETUP_FAILURE':26,'ORACLE_COMMAND_INVALID':2})
    yes('28_screened_partition',len(screened)==len(set(screened))==28 and set(exids).isdisjoint(screened) and set(exids)|set(screened)==set(admissions))
    yes('9_12_7_outcomes',Counter(r['case_status'] for r in outcomes)=={'ELIGIBLE':9,'INELIGIBLE_REPRODUCIBILITY_OUTCOME':12,'INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY':7})
    for group,status,count in [('grandfathered_eligible','ELIGIBLE',9),('scientific_ineligible','INELIGIBLE_REPRODUCIBILITY_OUTCOME',12),('infrastructure_unresolved','INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY',7)]:
        rows=bridge['groups'][group]['cases']
        yes(group+'_bridge_identity',bridge['groups'][group]['count']==len(rows)==count and [r['case_id'] for r in rows]==[r['case_id'] for r in outcomes if r['case_status']==status] and all(r['predecessor_status']==status for r in rows))
        for row in rows:
            check_reference(row['checkpoint_reference']);check_reference(row['outcome_reference']);check_reference(row['admission'])
            require(row['outcome_reference']['row_key']==row['case_id'] and row['checkpoint_reference']==entry['checkpoint_references'][row['case_id']], 'bridge misbound checkpoint')
            case=next(r for r in ranked if r['canonical_case_id']==row['case_id'])
            require(row['frozen_rank']==int(case['candidate_rank']) and row['project']==case['project'] and row['candidate_universe_sha256']==UNIVERSE and row['admission']['row_key']==row['case_id'], 'bridge identity/rank mismatch')
            treatment={'ELIGIBLE':'PRESERVED_NO_CAPACITY_RERUN','INELIGIBLE_REPRODUCIBILITY_OUTCOME':'FINAL_UNDER_UNCHANGED_ORACLE_NO_RESCUE','INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY':'SEPARATE_VERSIONED_GOVERNANCE_OUTSIDE_V6_EXECUTION'}[status]
            require(row['treatment']==treatment, 'bridge treatment drift')
    yes('39_exclusion_bridge_identity',[r['case_id'] for r in bridge['groups']['accepted_pre_eligibility_exclusions']['cases']]==exids)
    for row,old in zip(bridge['groups']['accepted_pre_eligibility_exclusions']['cases'],exclusions):
        check_reference(row['ledger_reference']);check_reference(row['admission'])
        require(row['exclusion_reason']==old['exclusion_reason'] and row['original_evidence_reference']==old['evidence_reference'] and row['treatment']=='PRESERVED_NOT_REOPENED', 'exclusion reinterpretation')
    yes('bridge_reference_only',bridge['raw_evidence_cloned'] is False and bridge['design_only'] is True and all(v is False for v in bridge['lifecycle'].values()))
    check('bridge_433_inventory_reference',lambda:check_reference(bridge['groups']['never_admitted_cap_skips']['inventory']))
    cap_skips=bridge['groups']['never_admitted_cap_skips']
    yes('bridge_cap_skip_lineage_policy',cap_skips['count']==433 and cap_skips['predecessor_disposition']=='SKIP_PROJECT_CAP' and cap_skips['lineage_modes']=={'DETERMINISTIC_INITIAL_TRAVERSAL_REPLAY':31,'LITERAL_FROZEN_TRAVERSAL_ROW':402} and cap_skips['skip_origin_counts']=={'initial':31,'block_01':21,'block_02':134,'block_03':247} and cap_skips['treatment']=='PROPOSED_ONLY_PROSPECTIVE_RECONSIDERATION')
    yes('complete_ranked_partition_bridge',bridge['ranked_partition_count']==500 and sum(g['count'] for g in bridge['groups'].values())==500 and bridge['unranked_metadata_exclusion']['case_id']=='keras::12')
    yes('skip_origins_31_21_134_247',entry['skip_origin_counts']=={'initial':31,'block_01':21,'block_02':134,'block_03':247})
    yes('pool_rank_project_distribution',contract['census']['project_counts']==dict(Counter(r['project'] for r in pool)) and contract['census']['rank_range']==[10,500] and contract['census']['rank_distribution']=={f'{lo}..{lo+99}':sum(lo<=int(r['frozen_rank'])<=lo+99 for r in pool) for lo in [1,101,201,301,401]})
    check('successor_contract_invariants',lambda:validate_contract(contract))
    yes('seven_track_exact_set',contract['unresolved_7_integration']['case_ids']==[r['case_id'] for r in outcomes if r['case_status']=='INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY'])
    yes('no_allocation',read_csv(BENCHMARK/'cases_manifest.csv')==[] and read_json(EXTERNAL/'post_run_audit.json')['allocation_performed'] is False)
    def original_preservation():
        for path,d in entry['tracked_entry_inventory'].items():
            p=ROOT/path;s=p.lstat()
            require(sha(p)==d['sha256'] and stat.S_IMODE(s.st_mode)==d['mode'] and ('symlink' if p.is_symlink() else 'file')==d['type'],'tracked change: '+path)
        for path,d in entry['external_original_input_inventory'].items():
            require(sha(path)==d['sha256'] and stat.S_IMODE(Path(path).lstat().st_mode)==d['mode'],'external input change')
    check('493_tracked_and_143_external_inputs_preserved',original_preservation)
    def external_evidence():
        manifest=read_json(EXTERNAL/'evidence_sha256.json')
        require(len(manifest)==1737,'evidence count drift')
        for row in manifest:require(sha(row['path'])==row['sha256'] and Path(row['path']).stat().st_size==row['bytes'],'original evidence changed')
        for name,digest in read_json(EXTERNAL/'final_hashes.json').items():
            if name!='evidence_files':require(sha(EXTERNAL/name)==digest,'final predecessor digest changed')
    check('1737_original_evidence_hashes_preserved',external_evidence)
    inventory=read_json(EVIDENCE/'predecessor_artifact_sha256.json')
    check('201_predecessor_bindings',lambda:require(len(inventory['artifacts'])==201 and all(sha(p)==d['sha256'] for p,d in inventory['artifacts'].items()),'predecessor binding drift'))
    for ref in [contract['predecessor'][k] for k in ['hash_inventory','bridge','protocol','run_spec','screening_spec']]+[contract['census']['membership'],entry['instruction']]:check_reference(ref)
    yes('referential_hash_closure',True)
    head=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
    branch=subprocess.check_output(['git','-C',str(ROOT),'branch','--show-current'],text=True).strip()
    index=subprocess.check_output(['git','-C',str(ROOT),'diff','--cached','--name-only'],text=True).strip()
    tracked_diff=subprocess.check_output(['git','-C',str(ROOT),'diff','--name-only'],text=True).strip()
    yes('HEAD_main_and_index_unchanged',head==EXPECTED_HEAD and branch=='main' and index==tracked_diff=='')
    new_files=subprocess.check_output(['git','-C',str(ROOT),'ls-files','--others','--exclude-standard'],text=True).splitlines()
    yes('proposal_only_write_scope',all(p.startswith('evaluation/downstream_benchmark/') and p.removeprefix('evaluation/downstream_benchmark/') in ALLOW_NEW for p in new_files))
    # Reject membership/lineage mutations without touching files or invoking any executor.
    pool_mutations=[('432_rows',lambda x:x.pop()),('434_rows',lambda x:x.append(copy.deepcopy(x[-1]))),
                    ('duplicate_case',lambda x:x[1].update(case_id=x[0]['case_id'])),
                    ('admitted_case_reopened',lambda x:x[0].update(case_id=admissions[0])),
                    ('scientific_failure_reopened',lambda x:x[0].update(case_id=next(r['case_id'] for r in outcomes if r['case_status']=='INELIGIBLE_REPRODUCIBILITY_OUTCOME'))),
                    ('other_disposition',lambda x:x[0].update(predecessor_disposition='ADMIT')),
                    ('rank_order_changed',lambda x:x.reverse()),('lineage_hash_changed',lambda x:x[0].update(predecessor_evidence_sha256='0'*64)),
                    ('source_changed',lambda x:x[0].update(bugsinpy_commit='0'*40)),('seed_changed',lambda x:x[0].update(seed='1')),
                    ('universe_changed',lambda x:x[0].update(candidate_universe_sha256='0'*64))]
    contract_mutations=[('admission_cap_reintroduced',lambda x:x['census'].update(candidate_admission_project_cap=4)),
                        ('preparation_cap_added',lambda x:x['census'].update(preparation_project_cap=4)),
                        ('optional_stopping_at_28',lambda x:x['census'].update(stop_when_28_eligible=True)),
                        ('majority_vote',lambda x:x['screening'].update(majority_vote=True)),
                        ('fourth_repetition',lambda x:x['screening']['schedule'].append({'variant':'FIXED','repetition':4})),
                        ('final_project_cap_weakened',lambda x:x['allocation'].update(final_sample_project_cap=5)),
                        ('24_plus_4_changed',lambda x:x['allocation'].update(final_count=23)),
                        ('invented_pilot_rule',lambda x:x['allocation'].update(pilot_selection_rule='first four')),
                        ('seven_required_before_expansion',lambda x:x['unresolved_7_integration'].update(prerequisite_to_expansion=True)),
                        ('late_seven_integrated',lambda x:x['unresolved_7_integration'].update(late_outcome_inclusion=True)),
                        ('automatic_downstream_authority',lambda x:x['state_machine']['transitions'][3].update(grants_downstream_execution_automatically=True)),
                        ('protocol_activated',lambda x:x['firewall'].update(V6_PROTOCOL_ACTIVATED='YES')),
                        ('canonical_state_persisted',lambda x:x['lifecycle'].update(PERSISTED='YES')),
                        ('automatic_successor_at_exhaustion',lambda x:x['exhaustion']['automatic_changes_forbidden'].remove('new_successor')),
                        ('preparation_rescue',lambda x:x['preparation'].update(later_success_overwrites_failure=True)),
                        ('missing_oracle_slot',lambda x:x['screening']['schedule'].pop())]
    contract_mutations.append(('subcommands_counted_as_repetitions',lambda x:x['screening']['composite_trial_semantics'].update(subcommands_count_as_extra_repetitions=True)))
    for name,mutator in pool_mutations:
        modified=copy.deepcopy(pool);mutator(modified)
        try:validate_pool(modified,expected,admissions,exids,screened)
        except ValueError as exc:negative.append({'check':name,'status':'PASS_REJECTED','reason':str(exc)})
        else:raise ValueError('mutation accepted: '+name)
    for name,mutator in contract_mutations:
        modified=copy.deepcopy(contract);mutator(modified)
        try:validate_contract(modified)
        except ValueError as exc:negative.append({'check':name,'status':'PASS_REJECTED','reason':str(exc)})
        else:raise ValueError('mutation accepted: '+name)
    artifact_integrity=None
    if (EVIDENCE/'artifact_sha256.json').exists():
        registry=read_json(EVIDENCE/'artifact_sha256.json')
        require(all(sha(ROOT/p)==digest for p,digest in registry['sha256'].items()),'proposal artifact hash drift')
        artifact_integrity={'status':'PASS','bound_files':len(registry['sha256']),'registry_sha256':sha(EVIDENCE/'artifact_sha256.json')}
    print(json.dumps({'schema':'V6_DESIGN_VALIDATION_RESULTS_PROPOSAL_V1','status':'PASS',
                      'positive_checks':positive,'negative_mutation_checks':negative,
                      'counts':{'positive_passed':len(positive),'negative_rejected':len(negative),'failed':0},
                      'proposal_pool_sha256':sha(BENCHMARK/'v6_reconsideration_pool_proposal.csv'),
                      'proposal_contract_sha256':sha(BENCHMARK/'v6_capacity_successor_contract_proposal.json'),
                      'artifact_integrity_if_inventory_present':artifact_integrity,
                      'execution_dispatches':0,'new_oracle_repetitions_consumed':0,
                      'historical_compatibility_probe':entry['historical_validator_compatibility']},indent=2,sort_keys=True))


if __name__ == '__main__':
    main()

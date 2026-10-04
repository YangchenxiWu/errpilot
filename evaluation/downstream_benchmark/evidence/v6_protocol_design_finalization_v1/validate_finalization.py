"""Read-only design/evidence validator; no runtime, subject, network or state writer.

Run: python3 -B /absolute/path/to/validate_finalization.py
The predecessor checker is unchanged on disk. Its process-local write allowlist
is extended only by the eight authorized finalization paths. All other original
positive checks and in-memory probes run unchanged, including historical hashes.
"""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import re
import subprocess
from pathlib import Path

E = Path(__file__).resolve().parent
B = E.parents[1]
ROOT = B.parents[1]
OLD = B / 'evidence/v6_protocol_design_v1'
HEAD = '26a9264105f303dc0101f74c9315c41ab1c9e265'
POOL = 'cad0889e1a527165fc04663c4bde0b22a8af25cdc07bc8c6426348e5ad1c2669'
ORIGINAL_REGISTRY = '262692d70cf2230d8ce22b2d69a60c13d0ae7952c8a3038bb9d4ccd265574427'
DECISION = B / 'V6_PROTOCOL_DESIGN_D1_D8_HUMAN_PI_DECISION.md'
CANDIDATE = B / 'V6_FINITE_SAME_UNIVERSE_CENSUS_PROTOCOL_DESIGN_FINALIZED_CANDIDATE.md'
NEW = [DECISION, CANDIDATE] + [E / n for n in [
    'entry_verification.json', 'lineage.json', 'validate_finalization.py',
    'validation_results.json', 'RUN_REPORT.md', 'artifact_sha256.json',
]]
EXPECTED_DECISIONS = [
    'RETAIN_CANDIDATE_IDENTIFIERS_PLUS_EXPLICIT_SCHEMAS',
    'ONE_LOGICAL_433_MEMBER_CENSUS',
    'NO_GOVERNED_BATCH_SEMANTICS',
    'INHERIT_ORTHOGONAL_VOCABULARY_WITH_ACCEPTED_HELD_UNRESOLVED',
    'CANONICAL_JSON_DESCRIPTOR_WITH_APPEND_ONLY_HASH_LINKED_EVENTS',
    'FOUR_STATE_INTEGRATION_AT_FIRST_COMBINED_POOL_INPUT_FREEZE',
    'HASH_SEED_PILOT_RESERVATION',
    'PRIMARY_STATUS_PLUS_ORTHOGONAL_RESOLUTION_QUALIFIERS',
]
EXPECTED_KEYS = [
    'decision protocol run_spec screening_spec pool bridge current_state lifecycle event predecessor_binding initial_skip_lineage',
    'decision batch_admission_authority later_membership_depends_on_outcomes stop_at_28_eligible',
    'decision dispatch_order runtime_chunks_have_scientific_identity',
    'decision new_canonical_failure_reasons automatic_retry unaccounted_or_unadjudicated_work_blocks_closure ACCEPTED_HELD_UNRESOLVED ACCEPTED_HELD_UNRESOLVED_IS_SCIENTIFIC_FAILURE ACCEPTED_HELD_UNRESOLVED_IS_ELIGIBLE ACCEPTED_HELD_UNRESOLVED_AUTOMATIC_RETRY',
    'decision canonical_descriptor csv_authority descriptor_event_disagreement competing_current_authorities current_descriptor_advances_only_via_authorized_state_transition historical_candidate_or_proposal_descriptor_is_runtime_authority runtime_consumers_must_bind_exact_current_descriptor_identity',
    'decision required_lifecycle seven_track_head remote_published_required_for_integration applicable_execution_publication_gates late_inclusion cutoff_refresh combined_pool_input_freeze_is_immutable_for_that_allocation_cycle',
    'decision seed digest_input sort pilot_count reserve pilot_project_cap final_feasibility_lookahead pilot_exclusion final_algorithm infeasible_behavior rule_freeze_before_any_V6_outcome pilot_swap pilot_reseed pilot_promotion_to_final',
    'decision automatic_downstream_authority primary_statuses qualifiers precedence',
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def embedded(p, label):
    text = Path(p).read_text(encoding='utf-8')
    pattern = r'<!-- BEGIN ' + label + r' -->\n```json\n(.*?)\n```\n<!-- END ' + label + r' -->'
    matches = re.findall(pattern, text, re.S)
    require(len(matches) == 1, 'missing/competing embedded semantic records')
    return json.loads(matches[0])


def source_semantics(request):
    """Independently read every named accepted field from the bound PI text."""
    source = Path(request['path']).read_text(encoding='utf-8')
    require(sha(request['path']) == request['sha256'], 'Human-PI instruction identity drift')
    require('ACCEPTED HUMAN_PI_V6_PROTOCOL_DESIGN_D1_D8_DECISION' in source and
            'OPEN_V6_PROTOCOL_DESIGN_DECISION_PERSISTENCE_AND_FINALIZATION' in source,
            'instruction lacks accepted decision/transaction')
    raw = source.split('ACCEPTED HUMAN-PI D1–D8 DECISION\n', 1)[1].split(
        '\n============================================================\nPRE-EXISTING ACCEPTED', 1)[0]
    expected = {}
    for number, keys in enumerate(EXPECTED_KEYS, 1):
        name = f'D{number}'
        body = raw.split('\n' + name + '\n' + '-' * 60 + '\n', 1)[1]
        if number < 8:
            body = body.split('\n' + '-' * 60 + '\nD' + str(number + 1) + '\n', 1)[0]
        record = {}
        for key in keys.split():
            if key == 'decision':
                value = re.search(r'^' + name + r' =\n([^\n]+)', body, re.M)[1].strip()
                require(value == EXPECTED_DECISIONS[number - 1], 'PI decision marker drift')
            elif key in {'primary_statuses', 'qualifiers', 'precedence'}:
                label = {'primary_statuses': 'Primary statuses', 'qualifiers': 'Qualifiers', 'precedence': 'Precedence'}[key]
                lines = re.search(r'^' + label + r':\n((?:\n|    [^\n]+\n)+)', body + '\n', re.M)[1].splitlines()
                value = [s.strip() for s in lines if s.strip() and s.strip() != '>']
            elif key == 'required_lifecycle':
                lines = re.search(r'^required_lifecycle =\n((?:\n|    [^\n]+\n)+)', body + '\n', re.M)[1].splitlines()
                value = [s.strip() for s in lines if s.strip()]
            else:
                value = re.search(r'^' + re.escape(key) + r' =\n    ([^\n]+)', body, re.M)[1].strip()
                if value.isdecimal():
                    value = int(value)
            record[key] = value
        expected[name] = record
    require(sum(len(v) for v in expected.values()) == 62, 'incomplete source semantic map')
    return raw, expected


def original_hashes():
    require(sha(OLD / 'artifact_sha256.json') == ORIGINAL_REGISTRY, 'original inventory byte drift')
    inventory = load(OLD / 'artifact_sha256.json')
    require(inventory['self_excluded'] is True and len(inventory['sha256']) == 10, 'inventory topology drift')
    result = dict(inventory['sha256'])
    result[str((OLD / 'artifact_sha256.json').relative_to(ROOT))] = ORIGINAL_REGISTRY
    require(len(result) == 11 and all(sha(ROOT / p) == h for p, h in result.items()), 'original 11 byte drift')
    return result


def check_ref(r):
    require(sha(ROOT / r['path']) == r['sha256'], 'reference digest drift: ' + r['path'])


def validate_semantics(d, m, expected, originals, proposal):
    require(set(d['accepted_D1_D8']) == set(expected) and d['accepted_D1_D8'] == expected, 'decision disagrees with PI fields')
    require(m['accepted_D1_D8'] == expected, 'candidate disagrees with PI fields')
    require(all(set(expected[f'D{i}']) == set(EXPECTED_KEYS[i - 1].split()) for i in range(1, 9)), 'unknown/missing semantic keys')
    require('null' not in json.dumps(d['accepted_D1_D8']) and 'REQUIRES_HUMAN_PI_DECISION' not in json.dumps(m['accepted_D1_D8']), 'null/unresolved decision field')
    require(d['human_pi_status'] == 'ACCEPTED' and d['semantic_status'] == 'PERSISTED_AS_DESIGN_AUTHORITY' and
            d['decision_identity'] == 'HUMAN_PI_V6_PROTOCOL_DESIGN_D1_D8_DECISION' and
            d['transaction'] == 'OPEN_V6_PROTOCOL_DESIGN_DECISION_PERSISTENCE_AND_FINALIZATION', 'decision status/authority drift')
    require(d['finalized_design_accepted'] is False and d['contract_construction_authorized'] is False and d['execution_authorized'] is False, 'decision grants unauthorized next gate')
    require(d['predecessor_head'] == m['predecessor_head'] == HEAD and
            d['original_candidate_sha256'] == m['original_candidate_sha256'] == originals, 'proposal lineage identities drift')
    expected_capacity = {'identity': proposal['authority']['accepted_capacity_decision'],
                         'original_instruction': proposal['authority']['instruction'],
                         'accepted_decisions': proposal['authority']['accepted_decisions']}
    require(d['accepted_capacity_context'] == m['accepted_capacity_context'] == expected_capacity, 'accepted capacity decision drift')
    require(m['architecture'] == 'V6_FINITE_SAME_UNIVERSE_CENSUS_WITH_EVIDENCE_CONTINUITY' and
            m['design_status'] == 'FINALIZED_CANDIDATE_ONLY' and
            m['readiness'] == 'FINALIZED_CANDIDATE_READY_FOR_HUMAN_PI_ACCEPTANCE', 'candidate identity/status drift')
    require(m['lifecycle'] == {k: 'NO' for k in ['HUMAN_PI_ACCEPTED', 'FROZEN', 'PERSISTED_CANONICAL', 'COMMITTED', 'REMOTE_PUBLISHED']}, 'design lifecycle upgraded')
    p = m['pool']
    require(p['count'] == 433 and p['project_count'] == 15 and p['logical_census_count'] == 1 and
            p['governed_batches'] == p['batch_admission_authority'] == 'NONE' and
            p['outcome_dependent_membership'] is False and p['stop_at_28'] is False and
            p['order'] == 'ORIGINAL_FROZEN_RANK_ASCENDING' and p['rank_range'] == [10, 500] and
            p['candidate_admission_project_cap'] == p['preparation_project_cap'] == 'NONE' and
            (p['initial_replay_rows'], p['literal_rows']) == (31, 402), 'census/lineage/stop/order/cap drift')
    require(p['reference'] == {'path': str((B / 'v6_reconsideration_pool_proposal.csv').relative_to(ROOT)), 'sha256': POOL}, 'pool identity drift')
    require(m['counts'] == {'eligible': 9, 'scientific_ineligible': 12, 'infrastructure_unresolved': 7, 'accepted_exclusions': 39, 'cap_skips': 433} and
            m['continuity'] == proposal['evidence_continuity'], 'predecessor class preservation drift')
    require(m['predecessor_identity'] == {k: proposal['predecessor'][k] for k in m['predecessor_identity']} and
            set(m['predecessor_identity']) == {'candidate_universe_sha256', 'source_commit', 'source_tree', 'seed', 'census_rows', 'ranked_rows'}, 'universe/source/seed drift')
    require(m['inherited_canonical_failure_reasons'] == proposal['preparation']['canonical_reason_vocabulary'], 'new scientific failure vocabulary')
    require(m['screening_invariants'] == proposal['screening'], '3x3/oracle/runtime/integrity semantics changed')
    a = m['allocation_invariants']
    require(a == {k: proposal['allocation'][k] for k in a} and len(a) == 16 and
            [a[k] for k in ['required_total', 'pilot_count', 'final_count', 'final_sample_project_cap', 'minimum_final_projects']] == [28, 4, 24, 4, 6], 'final allocation invariant/algorithm drift')
    u = m['unresolved_seven']
    require(u['case_ids'] == proposal['unresolved_7_integration']['case_ids'] and u['prerequisite_to_census'] is False and
            u['cutoff'] == 'FIRST_COMBINED_POOL_INPUT_FREEZE' and u['seven_track_head'] == expected['D6']['seven_track_head'] and
            u['required_lifecycle'] == ['HUMAN_PI_ACCEPTED', 'FROZEN', 'PERSISTED', 'COMMITTED'] and
            u['one_effective_accepted_outcome_per_case'] is True and u['separate_versioned_authority_and_exact_supersession_required'] is True and
            u['late_inclusion'] is False and u['cutoff_refresh'] is False and u['remote_published_required_for_integration'] is False and
            u['applicable_execution_publication_gates'] == 'RETAIN', 'seven-track cutoff/integration/publication drift')
    state = m['current_state_authority']
    require(state['effective_descriptor_count'] == 1 and state['canonical_descriptor'] == 'v6_current_state.json' and
            state['storage'] == expected['D5']['decision'] and state['event_relation'] == 'HASH_BOUND_TRANSITION_PROVENANCE_NOT_COMPETING_CURRENT_AUTHORITY' and
            state['csv_authority'] == 'DERIVED_ONLY' and state['disagreement'] == 'BLOCK' and
            state['advance'] == 'AUTHORIZED_STATE_TRANSITION_ONLY' and state['consumer_binding'] == 'EXACT_EFFECTIVE_CURRENT_DESCRIPTOR_IDENTITY' and
            state['historical_descriptor_runtime_authority'] is False and state['instantiated'] is False, 'current descriptor/event authority drift')
    c = m['closure']
    require(c['all_433_preparation_dispositions_accounted_and_adjudicated'] is True and c['all_ready_case_screening_slots_accounted_and_adjudicated'] is True and
            c['held_unresolved'] == 'ADMINISTRATIVE_ADJUDICATION_STATE_ONLY' and c['held_unresolved_scientific_failure'] is False and
            c['held_unresolved_eligible'] is False and c['automatic_retry'] is False, 'D4 closure/adjudication/eligibility drift')
    require(c['primary_statuses'] == expected['D8']['primary_statuses'] and c['qualifiers'] == expected['D8']['qualifiers'] and
            c['precedence'] == ['CLOSURE_BLOCKED', 'INSUFFICIENT_ELIGIBLE_CAPACITY', 'ALLOCATION_RULE_UNRESOLVED', 'PROJECT_DIVERSITY_INFEASIBLE', 'ALLOCATION_AUTHORITY_REQUIRED'] and
            c['automatic_downstream_authority'] == 'NONE', 'D8 precedence/status/authority drift')
    require(set(m['narrow_supersession']) == set(expected) and all(m['narrow_supersession'].values()), 'missing narrow override')
    require(m['downstream_authority'] == 'NONE' and m['production_contract_constructed'] is False and
            m['runtime_state_created'] is False and m['new_oracle_repetitions_consumed'] == 0 and
            m['next_gate'] == 'HUMAN_PI_ACCEPTANCE_OF_FINALIZED_V6_FINITE_SAME_UNIVERSE_CENSUS_PROTOCOL_DESIGN', 'next gate/runtime/authority leak')
    firewall_keys = 'ORIGINAL_11_MODIFIED V6_PROTOCOL_ACTIVATED V6_MEMBERSHIP_FROZEN PRODUCTION_CONTRACT_CONSTRUCTED CASE_PREPARED IMAGE_BUILT ORACLE_EXECUTED UNRESOLVED_7_RERUN PILOT_SELECTED FINAL_CASE_SELECTED GIT_STAGE GIT_COMMIT GIT_PUSH GIT_TAG'.split()
    require(m['firewall'] == {k: 'NO' for k in firewall_keys}, 'firewall drift')


def main():
    positive = []
    negative = []
    def check(name, fn):
        fn()
        positive.append({'check': name, 'status': 'PASS'})
    def yes(name, condition):
        check(name, lambda: require(condition, name))
    originals = original_hashes()
    yes('all_original_11_exact_hashes_unchanged', len(originals) == 11)
    entry = load(E / 'entry_verification.json')
    yes('entry_18_checks_pass_before_writes', len(entry['checks']) == 18 and all(c['status'] == 'PASS' for c in entry['checks']) and entry['status'] == 'PASS')
    yes('entry_required_live_oid_recorded', entry['head'] == entry['live_origin_main']['observed_oid'] == HEAD)
    d = embedded(DECISION, 'DECISION_JSON')
    m = embedded(CANDIDATE, 'FINALIZED_DESIGN_JSON')
    raw, expected = source_semantics(entry['instruction'])
    yes('decision_exact_semantic_text_preserved', '```text\n' + raw.rstrip() + '\n```' in DECISION.read_text())
    yes('62_decision_fields_match_PI_source', d['accepted_D1_D8'] == expected)
    yes('62_finalized_fields_match_PI_source', m['accepted_D1_D8'] == expected)
    yes('decision_instruction_identity_bound', d['instruction'] == entry['instruction'])
    proposal = load(B / 'v6_capacity_successor_contract_proposal.json')
    check('all_finalized_semantic_invariants', lambda: validate_semantics(d, m, expected, originals, proposal))
    check('decision_reference_identity', lambda: check_ref(m['decision']))
    yes('decision_reference_is_new_decision', m['decision']['path'] == str(DECISION.relative_to(ROOT)))
    lineage = load(E / 'lineage.json')
    yes('lineage_original_11_head_pool_source_seed', lineage['original_candidate_sha256'] == originals and
        lineage['predecessor_head'] == HEAD and lineage['pool_sha256'] == POOL and
        lineage['bugsinpy_commit'] == proposal['predecessor']['source_commit'] and
        lineage['bugsinpy_tree'] == proposal['predecessor']['source_tree'] and lineage['seed'] == 20260922)
    for key in ['decision', 'finalized_design_candidate', 'entry_verification', 'candidate_universe']:
        check('lineage_' + key + '_hash', lambda key=key: check_ref(lineage[key]))
    yes('lineage_paths_authorities_design_only', lineage['decision']['path'] == str(DECISION.relative_to(ROOT)) and
        lineage['finalized_design_candidate']['path'] == str(CANDIDATE.relative_to(ROOT)) and
        lineage['entry_verification']['path'] == str((E / 'entry_verification.json').relative_to(ROOT)) and
        lineage['candidate_universe']['path'] == str((B / 'candidate_universe.csv').relative_to(ROOT)) and
        lineage['transaction'] == d['transaction'] and lineage['accepted_capacity_context'] == d['accepted_capacity_context'] and
        lineage['design_only'] is True and lineage['runtime_authority'] is False)
    prose = CANDIDATE.read_text().split('<!-- BEGIN FINALIZED_DESIGN_JSON -->')[0]
    decision_prose = DECISION.read_text().split('<!-- BEGIN DECISION_JSON -->')[0]
    yes('explicit_decision_negative_authority', all(t in decision_prose for t in [
        'THIS DECISION ACCEPTS D1–D8 SEMANTICS', 'DOES NOT YET ACCEPT THE FINALIZED V6 DESIGN AS A WHOLE',
        'DOES NOT AUTHORIZE CONTRACT CONSTRUCTION OR EXECUTION']))
    yes('prose_cutoff_and_pilot_boundaries_explicit', all(t in prose for t in [
        'FIRST_COMBINED_POOL_INPUT_FREEZE', 'No late inclusion, cutoff refresh',
        '20260922|pilot|<source_project>|<bugsinpy_bug_id>|<case_id>',
        'No pilot project cap and no final-feasibility lookahead', 'No pilot swap, reseed, promotion or reselection']))
    yes('prose_authority_graph_retains_separate_gates', all(t in prose for t in [
        'Separate contract-construction authority', 'HUMAN_PI_FREEZE_V6_PROTOCOL',
        'HUMAN_PI_PERSIST_V6_CENSUS', 'HUMAN_PI_OPEN_V6_PREPARATION',
        'HUMAN_PI_ACCEPT_V6_PREPARATION_CLOSURE', 'HUMAN_PI_FREEZE_V6_READY_POPULATION',
        'HUMAN_PI_AUTHORIZE_V6_3X3_SCREENING', 'HUMAN_PI_ACCEPT_V6_SCREENING_CLOSURE',
        'HUMAN_PI_FREEZE_COMBINED_ELIGIBLE_POOL', 'HUMAN_PI_AUTHORIZE_PILOT_FINAL_ALLOCATION',
        'HUMAN_PI_ACCEPT_ALLOCATION']))
    # Re-run every original validator check and probe unchanged except its local
    # write scope. No disk edit or monkeypatch to semantic validation occurs.
    spec = importlib.util.spec_from_file_location('immutable_v6_proposal_checker', OLD / 'validate_proposal.py')
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    old.ALLOW_NEW |= {str(p.relative_to(B)) for p in NEW}
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        old.main()
    predecessor_result = json.loads(output.getvalue())
    yes('predecessor_validator_all_29_and_28_pass', predecessor_result['status'] == 'PASS' and
        predecessor_result['counts'] == {'positive_passed': 29, 'negative_rejected': 28, 'failed': 0})
    yes('canonical_root_main_head_index_tracked_unchanged', subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', '--show-toplevel'], text=True).strip() == str(ROOT) and
        subprocess.check_output(['git', '-C', str(ROOT), 'branch', '--show-current'], text=True).strip() == 'main' and
        subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip() == HEAD and
        subprocess.check_output(['git', '-C', str(ROOT), 'diff', '--cached', '--name-only'], text=True).strip() == '' and
        subprocess.check_output(['git', '-C', str(ROOT), 'diff', '--name-only'], text=True).strip() == '')
    actual = set(subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '--others', '--exclude-standard'], text=True).splitlines())
    new_paths = {str(p.relative_to(ROOT)) for p in NEW}
    yes('exact_original_plus_finalization_worktree_scope', entry['allowed_new_paths'] == [str(p.relative_to(ROOT)) for p in NEW] and
        actual == set(originals) | {p for p in new_paths if (ROOT / p).exists()} and not (actual - set(originals) - new_paths))
    yes('no_canonical_V6_contract_or_runtime_state_created', not any((B / name).exists() for name in [
        'V6_CAPACITY_SUCCESSOR_PROTOCOL.md', 'V6_CAPACITY_SUCCESSOR_RUN_SPEC.md', 'V6_CENSUS_SCREENING_SPEC.md',
        'v6_reconsideration_pool.csv', 'v6_predecessor_evidence_bridge.json', 'v6_current_state.json']))
    yes('no_V6_execution_namespaces', set(str(p.relative_to(ROOT)) for p in B.rglob('*') if p.is_file() and 'v6' in str(p.relative_to(B)).lower()) == actual.intersection(set(originals) | new_paths))
    external = Path('/Users/wuyangchenxi/errpilot-benchmark-work')
    yes('external_no_V6_governance_or_screening_runs', not any('v6' in p.name.lower() for p in external.iterdir()) and
        not any('v6' in run.name.lower() for case in (external / 'screening_evidence').iterdir() if case.is_dir() for run in case.iterdir()))
    for command in [['git', '-C', str(ROOT), 'diff', '--check'], ['git', '-C', str(ROOT), 'diff', '--cached', '--check']]:
        check(' '.join(command[3:]) + '_pass', lambda command=command: subprocess.run(command, check=True, capture_output=True))
    yes('new_files_UTF8_JSON_python_and_whitespace_valid', all(
        all(line == line.rstrip() for line in p.read_text(encoding='utf-8').splitlines()) for p in NEW if p.exists()))
    for p in NEW:
        if p.exists() and p.suffix == '.json':
            load(p)
        if p.exists() and p.suffix == '.py':
            compile(p.read_text(), str(p), 'exec')
    # Check the inventory if present, without emitting its hash in results
    # (the inventory binds results; a reverse hash would form a cycle).
    if (E / 'artifact_sha256.json').exists():
        registry = load(E / 'artifact_sha256.json')
        require(registry['self_excluded'] is True and registry['sha256'].keys() == (new_paths - {str((E / 'artifact_sha256.json').relative_to(ROOT))}), 'new inventory topology drift')
        for p, h in registry['sha256'].items():
            require(sha(ROOT / p) == h, 'new inventory hash drift: ' + p)
        require(actual == set(originals) | new_paths and len(actual) == 19, 'final exact 19 path population')
    # Each accepted semantic field must reject null drift in either artifact.
    for owner in ['decision', 'candidate']:
        for name, fields in expected.items():
            for key in fields:
                dc, mc = copy.deepcopy(d), copy.deepcopy(m)
                (dc if owner == 'decision' else mc)['accepted_D1_D8'][name][key] = None
                try:
                    validate_semantics(dc, mc, expected, originals, proposal)
                except ValueError as exc:
                    negative.append({'check': f'{owner}_{name}_{key}_null_drift', 'status': 'PASS_REJECTED', 'reason': str(exc)})
                else:
                    raise ValueError('accepted PI field drift: ' + name + '.' + key)
    probes = [
        ('outcome_dependent_continuation', 'pool', 'outcome_dependent_membership', True),
        ('governed_batches', 'pool', 'governed_batches', 'BLOCKS'),
        ('stop_at_28', 'pool', 'stop_at_28', True),
        ('wrong_pool_digest', 'pool', 'reference', {'path': m['pool']['reference']['path'], 'sha256': '0' * 64}),
        ('wrong_pool_count', 'pool', 'count', 432),
        ('rank_501', 'pool', 'rank_range', [10, 501]),
        ('reintroduce_admission_cap', 'pool', 'candidate_admission_project_cap', 4),
        ('held_is_scientific_failure', 'closure', 'held_unresolved_scientific_failure', True),
        ('held_is_eligible', 'closure', 'held_unresolved_eligible', True),
        ('automatic_retry', 'closure', 'automatic_retry', True),
        ('unadjudicated_closure', 'closure', 'all_433_preparation_dispositions_accounted_and_adjudicated', False),
        ('competing_descriptor', 'current_state_authority', 'effective_descriptor_count', 2),
        ('ignore_event_disagreement', 'current_state_authority', 'disagreement', 'PREFER_DESCRIPTOR'),
        ('csv_authority', 'current_state_authority', 'csv_authority', 'CANONICAL'),
        ('stale_proposal_runtime_authority', 'current_state_authority', 'historical_descriptor_runtime_authority', True),
        ('unbound_consumer', 'current_state_authority', 'consumer_binding', 'LATEST_FILENAME'),
        ('late_seven_inclusion', 'unresolved_seven', 'late_inclusion', True),
        ('refresh_seven_cutoff', 'unresolved_seven', 'cutoff_refresh', True),
        ('old_allocation_open_cutoff', 'unresolved_seven', 'cutoff', 'ALLOCATION_OPEN'),
        ('require_remote_publication_for_integration', 'unresolved_seven', 'remote_published_required_for_integration', True),
        ('drop_execution_publication_gate', 'unresolved_seven', 'applicable_execution_publication_gates', 'NONE'),
        ('scientific_rescue', 'screening_invariants', 'scientific_rescue', True),
        ('majority_vote', 'screening_invariants', 'majority_vote', True),
        ('change_final_cap', 'allocation_invariants', 'final_sample_project_cap', 5),
        ('change_final_24', 'allocation_invariants', 'final_count', 23),
        ('weaken_minimum_projects', 'allocation_invariants', 'minimum_final_projects', 5),
        ('wrong_terminal_precedence', 'closure', 'precedence', list(reversed(m['closure']['precedence']))),
        ('automatic_allocation', 'closure', 'automatic_downstream_authority', 'GRANTED'),
        ('design_accepted', 'lifecycle', 'HUMAN_PI_ACCEPTED', 'YES'),
        ('v6_activated', 'firewall', 'V6_PROTOCOL_ACTIVATED', 'YES'),
        ('production_contract_constructed', 'firewall', 'PRODUCTION_CONTRACT_CONSTRUCTED', 'YES'),
        ('pilot_selected', 'firewall', 'PILOT_SELECTED', 'YES'),
        ('git_staged', 'firewall', 'GIT_STAGE', 'YES'),
    ]
    for name, section, key, value in probes:
        mutated = copy.deepcopy(m)
        mutated[section][key] = value
        try:
            validate_semantics(d, mutated, expected, originals, proposal)
        except ValueError as exc:
            negative.append({'check': name, 'status': 'PASS_REJECTED', 'reason': str(exc)})
        else:
            raise ValueError('semantic drift accepted: ' + name)
    result = {
        'schema': 'V6_PROTOCOL_DESIGN_FINALIZATION_VALIDATION_V1', 'status': 'PASS',
        'positive_checks': positive, 'negative_mutation_checks': negative,
        'counts': {'positive_passed': len(positive), 'negative_rejected': len(negative), 'failed': 0},
        'original_proposal_validator': {'mode': 'UNCHANGED_CHECKER_WITH_PROCESS_LOCAL_EIGHT_PATH_ALLOWLIST_EXTENSION', 'counts': predecessor_result['counts'], 'all_original_493_tracked_143_external_1737_evidence_and_201_bindings': 'PASS'},
        'decision_sha256': sha(DECISION), 'finalized_candidate_sha256': sha(CANDIDATE),
        'lineage_sha256': sha(E / 'lineage.json'), 'pool_sha256': POOL,
        'execution_dispatches': 0, 'new_oracle_repetitions_consumed': 0,
        'design_consistency_only': True,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()

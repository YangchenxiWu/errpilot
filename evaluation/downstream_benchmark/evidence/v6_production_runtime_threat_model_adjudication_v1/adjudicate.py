"""Apply the explicit Human-PI scope decision to exact sealed evidence.

This script validates records and references, never imports candidate code.
"""
from pathlib import Path
import json

from verify_adjudication import A, C, HERE, REPO, PINS, identity, read, ref, save, sha, tree

STATUS = 'V6_SUCCESSOR_THREAT_MODEL_ADJUDICATION_READY_FOR_HUMAN_PI_ACCEPTANCE'
NEXT = 'HUMAN_PI_ACCEPT_V6_REMEDIATED_SUCCESSOR_UNDER_ADOPTED_THREAT_MODEL'
EXCLUSION = ('An adversarial process operating under the same macOS UID that deliberately races '
             'the benchmark writer by relocating authorized qualification/output directories '
             'between successful path validation and subsequent filesystem operations.')
IN_SCOPE = [
    'Path traversal using "." / ".." and path aliases.',
    'Unauthorized symlink traversal.',
    'Incorrect or unauthorized output paths.',
    'Accidental cross-root writes.',
    'Incorrect qualification-root selection.',
    'Receipt/association/claim/terminal identity violations.',
    'Unauthorized BuildKit clients under C1-C16.',
    'Unknown active control-capable clients: production BLOCK.',
    'Scientific/work identity drift.',
    'Once-only claim/terminal violations.',
    'Unintended overwrite or automatic retry.',
]


def refs(*names):
    return [ref(p) for p in names]


def verify_ref(row):
    path = Path(row['path'])
    if not path.is_absolute():
        path = REPO / path
    got = identity(path)
    for key in ('sha256', 'size_bytes', 'mode', 'type'):
        if key in row:
            assert got[key] == row[key], (path, key)


def source_ref(name, first, last):
    path = C / name
    return dict(ref(path), first_line=first, last_line=last,
                excerpt='\n'.join(path.read_text().splitlines()[first-1:last]))


def semantic(value):
    return sha((json.dumps(value, sort_keys=True, ensure_ascii=False,
                           separators=(',', ':'), allow_nan=False)+'\n').encode())


def reconcile_r02():
    matrix = read(C / 'rejection_matrix.json')
    record = matrix['checks']['F01_replace_component_before_open']
    raw_path = C / 'construction_history/qualification_run_4/root_confinement_regressions.json'
    raw = read(raw_path)['replaceable_component']
    assert record['evidence_before'] == raw['before']
    assert record['evidence_after'] == raw['after']
    assert record['trace_evidence'] == raw['trace_hit']
    assert record['status'] == raw['status'] == 'PASS_REJECTED'
    assert record['reason'] == raw['reason'] == 'F01 no-follow component refused: mutable'
    assert record['fixture_identity'] == semantic(raw['before'])
    inv = read(C / 'synthetic_output_inventory.json')
    root = Path(inv['root'])
    fixture_roots = [k for k, v in inv['files'].items()
                     if v['type'] == 'directory' and k.count('/') == 1]
    matches = []
    for fixture in fixture_roots:
        entries = {k[len(fixture)+1:]: v for k, v in inv['files'].items() if k.startswith(fixture+'/')}
        if entries == raw['after']:
            matches.append(fixture)
    assert matches == ['run_4/fixture_76']
    corrected = root / matches[0]
    actual = tree(corrected)
    actual.pop('.')
    assert actual == raw['after']
    assert record['fixture_root'] == str(root / 'run_4')
    assert raw['after']['mutable']['target'] == str(corrected / 'owned_redirect')
    nested = corrected / 'legitimate/nested/receipt.json'
    assert nested.read_bytes() == b'LEGITIMATE_OWNED_FIXTURE\n'
    assert raw['after']['legitimate/nested/receipt.json'] == identity(nested)
    assert not (corrected / 'owned_redirect/nested/association.json').exists()
    assert raw['redirected_artifacts'] == record['unauthorized_candidate_artifacts'] == 0
    assert record['unauthorized_claims'] == record['unauthorized_builds'] == 0
    qio = (C / 'qualification_io.py').read_text().splitlines()
    assert raw['trace_hit'] == [{'operation': 'replace directory with symlink before actual open', 'source_line': 83}]
    assert qio[82].strip() == 'child = os.open(component, FLAGS, dir_fd=fd)'
    assert 'str(Path(result[\'qualification_run_root\']))' in (C / 'package_final_candidate.py').read_text().splitlines()[82]
    erratum = {
        'status': 'PASS_UNIQUE_LOCATOR_RECONCILIATION', 'finding': 'R02', 'severity': 'MINOR',
        'disposition': 'MINOR_EVIDENCE_LOCATOR_ERRATUM_ONLY',
        'original_file': str(C / 'rejection_matrix.json'),
        'original_file_SHA256': identity(C / 'rejection_matrix.json')['sha256'],
        'field': '/checks/F01_replace_component_before_open/fixture_root',
        'old_locator': record['fixture_root'], 'corrected_locator': str(corrected),
        'supporting_evidence_SHAs': refs(raw_path, C / 'root_confinement_regressions.json',
             C / 'package_final_candidate.py', C / 'remediation_regressions.py', C / 'qualification_io.py',
             C / 'synthetic_output_inventory.json', A / 'findings.json', A / 'independent_F01_probes.json', nested),
        'unique_reconciliation': {'searched_fixture_roots': len(fixture_roots), 'exact_inventory_matches': matches,
             'aggregate_before_equals_raw_before': True, 'aggregate_after_equals_raw_after': True,
             'aggregate_trace_equals_raw_trace': True, 'fixture_identity_matches_before_semantic_SHA256': True,
             'all_20_actual_entries_equal_sealed_after_inventory': True,
             'symlink_target': raw['after']['mutable'], 'retained_fixture_inventory': actual},
        'source_trace': [source_ref('package_final_candidate.py', 76, 83),
                         source_ref('remediation_regressions.py', 253, 293),
                         source_ref('qualification_io.py', 75, 93)],
        'semantic_effect': 'Only the base path used to locate this category evidence is corrected. No test outcome, input, trace, source, claim, or security semantics changes; no full-race safety claim.',
        'unchanged_test_result': {k: record[k] for k in ('status', 'reason', 'observed_rejection',
             'attempts_consumed_by_rejection', 'unauthorized_claims', 'unauthorized_builds', 'unauthorized_candidate_artifacts')},
        'historical_record_preserved': True, 'test_result_reconstructed': False, 'test_rerun': False,
    }
    return erratum


def review_records():
    assert read(HERE / 'entry_verification.json')['status'] == 'PASS'
    f1 = read(A / 'independent_F01_probes.json')
    assert len(f1['lexical_and_constructor']) == 9
    assert all(v['status'] == 'PASS_REJECTED' for v in f1['lexical_and_constructor'].values())
    assert len(f1['existing_symlinks_read_only']) == 16
    assert all(v['status'] == 'PASS_REJECTED' for v in f1['existing_symlinks_read_only'])
    assert f1['legitimate_nested_read']['status'] == 'PASS'
    f2 = read(A / 'independent_F02_probes.json')
    assert len(f2['original_contradiction_reconstruction']) == 2
    assert all(x['status'] == 'PASS_REJECTED' and x['reason'] == 'F02 actual socket Path/endpoint conflict'
               for x in f2['original_contradiction_reconstruction'])
    assert len(f2['recorded_negative_inputs_independently_executed']) == 76
    f3 = read(A / 'independent_F03_probes.json')
    assert len(f3['checks']) == 4 and f3['false_and_zero_distinct'] is True
    for row in f2['recorded_negative_inputs_independently_executed'] + f3['checks']:
        assert row['status'] == 'PASS_REJECTED'
        assert identity(Path(row['input_file']))['sha256'] == row['input_sha256']
    for data in (f1, f2, f3, read(A / 'independent_receipt_probes.json')):
        for path, row in data['sources'].items():
            verify_ref(dict(row, path=path))
    rc = read(A / 'independent_receipt_probes.json')
    assert len(rc['terminals']) == 3
    for terminal in rc['terminals']:
        assert terminal['retained_association_verified_by_final_source'] is True
        assert terminal['controller_reentry']['status'] == terminal['provider_reentry']['status'] == 'PASS_REJECTED'
    assert sorted(x['state'] for x in rc['terminals']) == ['INTERRUPTED', 'MATERIALIZED', 'MATERIALIZED']
    assert next(x for x in rc['terminals'] if x['NONE_null'])['receipt_sha256'] is None
    cover = read(A / 'qualification_coverage_audit.json')
    matrix = read(C / 'rejection_matrix.json')
    assert cover['total'] == len(cover['categories']) == len(matrix['checks']) == 188
    assert cover['inherited'] == 126 and cover['new'] == 62 and cover['mandatory_skips'] == 0
    assert {x['category'] for x in cover['categories']} == set(matrix['checks'])
    assert all(x['status'] == 'PASS_REJECTED' and x['attempts_consumed_by_rejection'] == 0 for x in matrix['checks'].values())
    for mapping in cover['both_A_X_mappings'].values():
        assert set(mapping) == set('ABCDEFGHIJKLMNOPQRSTUVWX')
        assert all(v['status'] == 'PASS' for v in mapping.values())
    for row in matrix['checks'].values():
        for path, digest in row['exact_tested_sources'].items():
            verify_ref({'path': path, 'sha256': digest})
    faults = read(A / 'crash_partial_write_audit.json')
    assert faults['crash_boundaries'] == 10 and faults['partial_write_classes'] == 4
    assert len(faults['checks']) == 14 and faults['PHYSICAL_POWER_LOSS_DURABILITY_NOT_ESTABLISHED'] is True
    for row in faults['checks']:
        trace = row['trace']
        assert identity(Path(trace['source']))['sha256'] == trace['source_sha256']
        assert Path(trace['source']).read_text().splitlines()[trace['line']-1].strip() == row['source_line']
        assert row['retained_after_inventory_matches'] is True
        assert row['nonempty_claims'] <= 1 and row['terminal_count'] <= 1
        assert row['reentry']['automatic_retry'] is False
        assert row['reentry']['evidence_bytes_paths_modes_unchanged'] is True
        if row['empty_retained_file']:
            assert identity(Path(row['fixture_root']) / row['empty_retained_file'])['size_bytes'] == 0
    science = read(A / 'scientific_integrity_audit.json')
    assert science['replayed'] == len(science['rows']) == 641 and science['independently_executed'] is True
    assert all(x['status'] == 'PASS_EXACT_PURE_PROJECTION' for x in science['rows'])
    assert science['variants'] == {'BUGGY': 210, 'FIXED': 210, 'SOURCE_INDEPENDENT': 221}
    assert science['population']['restricted'] == 583 and science['population']['none'] == 58
    assert science['native_commands_executed'] == 0 and science['scientific_validation_claimed'] is False
    graph = read(C / 'supersession_dependency_graph.json')
    reviewed = read(A / 'contract_supersession_audit.json')
    assert len(graph['nodes']) == reviewed['nodes'] == 11
    assert len(graph['edges']) == reviewed['edges'] == 18
    assert len(reviewed['references']) == reviewed['exact_hash_references'] == 739
    for r in reviewed['references']:
        verify_ref(r)
    adj = {n['id']: [] for n in graph['nodes']}
    for src, dst in graph['edges']:
        assert src in adj and dst in adj
        adj[src].append(dst)
    done = set()
    def visit(node, active):
        assert node not in active
        if node not in done:
            for other in adj[node]:
                visit(other, active | {node})
            done.add(node)
    for node in adj:
        visit(node, set())
    for name in reviewed['preserved_V2_contracts']:
        old = C.parent / 'v6_production_runtime_topology_stability_successor_resume_v1' / name
        assert (C / name).read_bytes() == old.read_bytes()
    assert read(A / 'findings.json')['counts'] == {'MATERIAL': 1, 'MINOR': 1, 'OPTIONAL': 0}
    qio = (C / 'qualification_io.py').read_text()
    for line in ['os.O_DIRECTORY | os.O_NOFOLLOW', "part not in {'.', '..', ''}",
                 'if (info.st_dev, info.st_ino) != self.anchor:', 'os.O_EXCL | os.O_NOFOLLOW',
                 'follow_symlinks=False', 'fcntl.F_GETPATH']:
        assert line in qio
    assert read(A / 'validation_results.json')['STATUS'] == 'V6_SUCCESSOR_REMEDIATION_INDEPENDENT_REAUDIT_BLOCKED'
    return {
        'status': 'PASS_EXISTING_EXACT_IN_SCOPE_EVIDENCE',
        'method': 'Fresh read-only byte/reference and record-consistency checks plus independent source review. Existing sealed independent executions are reused; no candidate tests or native operations run now.',
        'F01': {'lexical_constructor_rejections': 9, 'existing_symlink_rejections': 16,
               'original_dotdot_rejected': True, 'adversarial_relocation_safety_claimed': False},
        'F02': {'original_counterexample_stages': 2, 'recorded_independent_pure_gate_calls': 76,
               'real_client_authorization': 'BLOCKED'},
        'F03': {'recorded_independent_calls': 4, 'Boolean_false_distinct_from_integer_zero': True},
        'receipt_once_only': {'recorded_terminals': 3, 'restricted_NONE_failure_covered': True,
               'immutable_claim_receipt_association_bindings': True, 'automatic_retry': False},
        'fault_evidence': {'crash': 10, 'partial_write': 4, 'scope': 'SOURCE_LEVEL_FAULT_INJECTION_PASS',
               'partial_write_detail': 'Injected before first os.write; empty reserved files retained. Arbitrary prefix/torn-write and physical power-loss behavior not established.'},
        'coverage': {'negative_categories': 188, 'inherited': 126, 'new': 62, 'A_X_mappings': 2,
               'mandatory_skips': 0, 'R02_locator_resolved_by_additive_erratum': True},
        'scientific_native': {'recorded_independent_pure_replays': 641, 'variants': science['variants'],
               'population': science['population'], 'native_commands_executed_now': 0,
               'scientific_validation_claimed': False, 'environment_readiness_claimed': False},
        'graph': {'nodes': 11, 'edges': 18, 'exact_hash_references_rechecked': 739, 'acyclic': True,
               'V2_contracts_byte_exact': 7, 'historical_acceptance_transferred': False},
        'evidence': refs(*[A / name for name in (
            'F01_root_confinement_reaudit.json', 'independent_F01_probes.json',
            'F02_endpoint_correlation_reaudit.json', 'independent_F02_probes.json',
            'F03_test_semantics_reaudit.json', 'independent_F03_probes.json',
            'receipt_association_audit.json', 'independent_receipt_probes.json',
            'crash_partial_write_audit.json', 'qualification_coverage_audit.json',
            'scientific_integrity_audit.json', 'contract_supersession_audit.json',
            'synthetic_source_isolation_audit.json')]),
    }


def main():
    erratum = reconcile_r02()
    review = review_records()
    request = Path('/Users/wuyangchenxi/.codex/attachments/02c54131-2265-4673-9853-2a11d3b0ddf9/已粘贴的文本.txt')
    raw = request.read_bytes()
    assert b'\r' not in raw and raw.endswith(b'\n')
    raw.decode('utf-8')
    with (HERE / 'raw_user_request.txt').open('xb') as stream:
        stream.write(raw)
    save('human_pi_threat_model_decision.json', {
        'authority': 'HUMAN_PI_ADJUDICATE_V6_REMEDIATION_REAUDIT_R01_R02',
        'decision': 'ADOPT_CONTROLLED_SINGLE_TRUSTED_OPERATOR_BENCHMARK_THREAT_MODEL_V1',
        'HUMAN_PI_EXPLICIT_DECISION': 'EXCLUDE_ADVERSARIAL_CONCURRENT_DIRECTORY_RELOCATION_BY_SAME_UID',
        'authorization': 'BOUNDED_THREAT_MODEL_ADJUDICATION_AND_INDEPENDENT_CONFIRMATION',
        'source': ref(HERE / 'raw_user_request.txt'), 'authority_origin': 'Latest explicit user instruction',
        'R01_DISPOSITION': ['KNOWN_RESIDUAL_RISK', 'OUT_OF_SCOPE_UNDER_ACCEPTED_BENCHMARK_THREAT_MODEL',
                           'NOT_FIXED_AGAINST_ADVERSARIAL_CONCURRENT_RELOCATION', 'NOT_RETROACTIVELY_AUDIT_PASS'],
        'R02_DISPOSITION': 'MINOR_EVIDENCE_LOCATOR_ERRATUM_ONLY',
        'source_candidate_acceptance': False, 'production_authorization': False})
    save('threat_model_contract.json', {
        'schema': 'CONTROLLED_SINGLE_TRUSTED_OPERATOR_BENCHMARK_THREAT_MODEL_V1',
        'purpose': 'A controlled, single-trusted-operator scientific benchmark executing frozen real CLI/Python failure cases.',
        'multi_tenant_adversarial_security_platform': False, 'in_scope': IN_SCOPE, 'out_of_scope': EXCLUSION,
        'same_UID_may_have_sufficient_filesystem_permissions': True, 'root_privilege_required_claimed': False,
        'exclusion_limit': 'Only deliberate adversarial concurrent directory relocation. Accidental path escapes, symlink manipulation, wrong-root selection and incorrect writes remain in scope.',
        'not_excluded': ['Arbitrary same-UID interference', 'Host compromise as a blanket waiver',
                         'BuildKit client authorization', 'Network access'],
        'mandatory_in_scope_evidence_failure': 'BLOCK',
        'historical_candidate_V3_word_privileged_is_not_the_accepted_boundary': True,
        'authority': ref(HERE / 'human_pi_threat_model_decision.json')})
    save('R02_locator_erratum.json', erratum)
    save('existing_independent_evidence_review.json', review)
    save('R01_scope_adjudication.json', {
        'finding': 'R01', 'R01_ORIGINAL_AUDIT_SEVERITY': 'MATERIAL',
        'R01_ACCEPTED_SCOPE_DISPOSITION': 'OUT_OF_SCOPE_RESIDUAL_RISK',
        'R01_CODE_FIX_FOR_ADVERSARIAL_RELOCATION': 'NOT_CLAIMED',
        'R01_HISTORICAL_FINDING_PRESERVED': 'YES', 'known_residual_risk': True,
        'FULL_ADVERSARIAL_RELOCATION_SAFETY': 'NOT_ESTABLISHED',
        'PHYSICAL_POWER_LOSS_DURABILITY': 'NOT_ESTABLISHED',
        'retained_finding': 'On macOS an open directory descriptor continues to refer to a directory relocated after verification. F_GETPATH does not atomically bind a later open/write/link to the verified name.',
        'source_intervals': [source_ref('qualification_io.py', 150, 167), source_ref('qualification_io.py', 171, 184)],
        'effects': ['A rename after parent verification can cause exclusive leaf creation under the relocated directory before detection.',
                   'Relocation after leaf verification can precede the following write.',
                   'Parent verification followed by os.link is not an atomic confinement guarantee.'],
        'exact_accepted_exclusion': EXCLUSION,
        'historical_probe_scope': 'Two sealed Darwin syscall mechanism probes, not an exact candidate-constructor race reproduction; no new race was executed here.',
        'decision_effect': 'Resolves the authority/scope ambiguity for the excluded deliberate relocation scenario. It neither repairs the mechanism nor rewrites the historical blocked audit.',
        'evidence': refs(A / 'findings.json', A / 'F01_root_confinement_reaudit.json', A / 'relocation_primitive_probe.json',
                         HERE / 'threat_model_contract.json', HERE / 'existing_independent_evidence_review.json')})
    save('R01_residual_risk_register.json', {
        'risks': [
            {'id': 'R01', 'severity_in_original_audit': 'MATERIAL', 'disposition': 'KNOWN_OUT_OF_SCOPE_RESIDUAL_RISK',
             'scenario': EXCLUSION, 'code_fix': 'NOT_CLAIMED', 'safety': 'NOT_ESTABLISHED',
             'scope_expansion_response': 'If deliberate concurrent relocation enters scope, this scoped PASS is insufficient; separate Human-PI work authorization and evidence required.'},
            {'id': 'DURABILITY', 'scenario': 'Physical power loss, arbitrary torn writes or partial-prefix persistence',
             'disposition': 'NOT_ESTABLISHED', 'evidence_limit': '10 crash + 4 empty-write source-level outcomes only.'},
            {'id': 'LIVE_PRODUCTION', 'scenario': 'Unknown control-capable clients, incomplete census, missing accepted observer, missing source/receipt/effectivity pins or stale topology',
             'disposition': 'PRODUCTION_BLOCKED', 'historical_exec_origins': 'ORIGIN_NOT_ESTABLISHED'}],
        'accidental_path_escapes_or_symlink_manipulation_waived': False,
        'historical_audit': ref(A / 'findings.json')})
    rows = [
        ('Lexical traversal, aliases, unauthorized root and accidental cross-root path selection',
         '9 independent lexical/factory rejections plus exact candidate-owned root/source guards and recorded wrong-root cases.',
         [A / 'independent_F01_probes.json', A / 'synthetic_source_isolation_audit.json', C / 'root_confinement_regressions.json']),
        ('Symlink manipulation and incorrect writes',
         '16 independent existing-symlink rejections; componentwise O_NOFOLLOW, scope inode and descriptor checks; 3 recorded controlled replacements and legitimate nested read/write.',
         [A / 'F01_root_confinement_reaudit.json', C / 'additional_security_regressions.json', HERE / 'R02_locator_erratum.json']),
        ('Receipt, association, claim, terminal and once-only identity',
         'Sealed exact-byte readback and source review preserve ownership, NONE/null receipt semantics, one claim/terminal, exclusive publication and no automatic retry.',
         [A / 'receipt_association_audit.json', A / 'independent_receipt_probes.json']),
        ('Unauthorized/unknown clients and network authority',
         'C1-C16 remain mandatory. F02 independently rejects contradictory endpoints; F03 distinguishes bool from int. Production remains BLOCKED pending complete current evidence.',
         [C / 'client_authorization_contract_candidate.json', A / 'F02_endpoint_correlation_reaudit.json', A / 'F03_test_semantics_reaudit.json']),
        ('Scientific/work identity and coverage',
         '188 recorded categories, both 24-entry A-X maps, independent 641 pure projections and exact source/hash graph support implementation equivalence only.',
         [A / 'qualification_coverage_audit.json', A / 'scientific_integrity_audit.json', A / 'contract_supersession_audit.json']),
        ('No overwrite/retry after source-level interruptions',
         '10 crash and 4 empty-write records preserve orphan evidence and reject reentry; physical power-loss durability remains unestablished.',
         [A / 'crash_partial_write_audit.json']),
    ]
    save('in_scope_security_assurance_review.json', {
        'status': 'PASS_UNDER_ADOPTED_THREAT_MODEL', 'mandatory_in_scope_property_unestablished': [],
        'assurance_basis': 'Exact sealed evidence and source mechanisms; no universal adversarial or physical durability guarantee.',
        'properties': [{'property': p, 'assessment': s, 'status': 'SUPPORTED_WITH_STATED_EVIDENCE_SCOPE', 'evidence': refs(*e)} for p, s, e in rows],
        'deliberate_relocation_exclusion': EXCLUSION,
        'accidental_path_escapes_wrong_roots_symlinks_incorrect_writes_remain_in_scope': True,
        'arbitrary_same_UID_interference_excluded': False,
        'full_new_E2E_execution': False, 'source_level_faults_are_physical_durability': False})
    conditions = [
        'Benchmark directories owned by the intended trusted operator.',
        'No knowingly untrusted actor permitted to manipulate those roots.',
        'No concurrent adversarial same-UID directory relocation.',
        'Exact authorized output-root identity.',
        'Existing in-scope filesystem safety checks.',
        'Accepted source/receipt/effectivity pins.',
        'Complete C1-C16 current-client authorization.',
        'Fresh mandatory topology security verification.',
    ]
    save('production_operational_preconditions.json', {
        'scope': 'FUTURE_PRODUCTION_OPERATIONAL_CONDITIONS',
        'conditions': [{'condition': c, 'mandatory': True, 'currently_verified_by_this_transaction': False} for c in conditions],
        'if_any_mandatory_precondition_fails': 'PRODUCTION_EXECUTION_BLOCKED',
        'PRODUCTION_EXECUTION': 'BLOCKED', 'unknown_BuildKit_exec_origins': 'ORIGIN_NOT_ESTABLISHED',
        'present_adjudication_authorizes_unknown_clients': False,
        'current_topology_or_client_census_performed': False,
        'C1_C16_reference': ref(C / 'client_authorization_contract_candidate.json'),
        'separate_acceptance_installation_effectivity_execution_authority_required': True})
    save('independent_scoped_disposition.json', {
        'STATUS': STATUS, 'HISTORICAL_INDEPENDENT_AUDIT': 'BLOCKED',
        'historical_exact_status': 'V6_SUCCESSOR_REMEDIATION_INDEPENDENT_REAUDIT_BLOCKED',
        'CURRENT_SCOPED_ADJUDICATION': 'PASS',
        'recommendation': 'Exact existing candidate is eligible for Human-PI acceptance under the adopted threat model, with R01 retained as known out-of-scope residual risk and additive R02 locator erratum.',
        'exact_candidate_pins': {n: ref(C / n) for n in PINS},
        'decision_basis': refs(HERE / 'human_pi_threat_model_decision.json', HERE / 'R01_scope_adjudication.json',
                              HERE / 'R02_locator_erratum.json', HERE / 'in_scope_security_assurance_review.json'),
        'candidate_only': True, 'HUMAN_PI_ACCEPTED': 'NO', 'runtime_effective': 'NO', 'execute_now': False,
        'automatic_candidate_acceptance': False, 'historical_audit_retroactively_passed': False,
        'lifecycle_freeze': False, 'commit_or_publication': False, 'production_installation': False,
        'real_attempt': False, 'NEXT_GATE': NEXT, 'STOP': True})
    save('validation_results.json', {
        'STATUS': STATUS, 'CURRENT_SCOPED_ADJUDICATION': 'PASS',
        'checks_completed': ['1818 complete physical paths/sizes/SHAs including 8 ignored files',
              '1065 tracked files and index matched sealed historical baseline',
              'Exact HEAD, canonical, events, candidate pins and negative flags',
              'Entire 12271-entry persistent tree and empty real ledger matched sealed audit snapshot',
              'R02 single match among 414 fixtures, aggregate/raw/source/actual-output correspondence',
              'Existing independent evidence record checks and 739 actual hash references',
              'Exact narrow Human-PI scope; future preconditions explicitly not currently verified'],
        'checks_to_complete_before_reporting_final_status': 'verify_adjudication.py seal and separate verify must succeed; seal does fresh preservation and strict JSON/UTF-8/LF checks.',
        'candidate_tests_rerun': False, 'full_new_E2E': False, '641_projections_rerun': False,
        'physical_power_loss_durability': 'NOT_ESTABLISHED', 'adversarial_relocation_safety': 'NOT_ESTABLISHED',
        'historical_audit_rewritten': False, 'production_authorization_inferred': False})
    print(json.dumps({'status': 'PASS_SCOPED_REVIEW', 'R02_unique_fixture': 'run_4/fixture_76',
                      'fixture_roots_searched': 414, 'graph_hash_references': 739,
                      'final_ready_status_requires': 'exit preservation, seal and separate readback'}))


if __name__ == '__main__':
    main()

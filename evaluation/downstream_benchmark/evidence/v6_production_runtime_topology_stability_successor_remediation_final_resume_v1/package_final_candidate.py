"""Bind completed qualification to a non-effective supersession candidate."""
from __future__ import annotations

import json
from pathlib import Path

from . import production_provider_remediated_candidate as p
from . import remediation_regressions as r
from . import verify_firewall as v

OUT = Path(__file__).resolve().parent
RUN = OUT / 'construction_history/qualification_run_4'
STATUS = 'REMEDIATED_SUCCESSOR_CANDIDATE_READY_FOR_INDEPENDENT_REAUDIT'


def read(path):
    return v.read_json(path)


def ref(path):
    return {'path': str(path), **v.identity(path)}


def save(name, value):
    with (OUT / name).open('xb') as stream:
        stream.write(p.pretty(value))


def sources():
    return {str(OUT / name): v.identity(OUT / name)['sha256'] for name in (
        'production_controller_remediated_candidate.py', 'production_provider_remediated_candidate.py',
        'qualification_io.py', 'socket_endpoint_binding.py')}


def ledger_view(inventory):
    return {key: value for key, value in inventory.items()
            if key.startswith('ledger/') and value['type'] == 'file'}


def direct_record(name, before, after, reason, mutation, fixture, trace):
    v.require(ledger_view(before) == ledger_view(after) == {}, 'direct negative ledger mutated')
    return {'status': 'PASS_REJECTED', 'reason': reason, 'expected_category': name,
        'observed_rejection': 'Rejected', 'expected_specific_rejection': reason,
        'actual_rejection_reason': reason, 'ledger_before': {}, 'ledger_after': {},
        'evidence_before': before, 'evidence_after': after,
        'fixture_identity': v.semantic(before), 'fixture_root': fixture,
        'mutation': mutation, 'mutation_identity': v.semantic(mutation),
        'controlled_harness_mutation_during_call': True,
        'exact_tested_sources': sources(), 'trace_evidence': trace,
        'attempts_consumed_by_rejection': 0, 'unauthorized_claims': 0,
        'unauthorized_builds': 0, 'unauthorized_candidate_artifacts': 0}


def qualification():
    result = read(RUN / 'synthetic_e2e_results.json')
    matrix = read(RUN / 'rejection_matrix.json')
    v.require(result['status'] == 'PASS' and result['inherited_126_count'] == 126,
              'full final runtime suite incomplete')
    v.require(result['new_rejection_count'] == 59 and matrix['mandatory_skipped'] == 0,
              'final rejection suite incomplete')
    for record in matrix['checks'].values():
        v.require(record['status'] == 'PASS_REJECTED'
                  and record['reason'] == record['intended_gate']['reason']
                  or record['status'] == 'PASS_REJECTED'
                  and record['observed_rejection'] in {'FileNotFoundError', 'SystemExit'},
                  'negative gate did not assert intended reason')
        v.require(record['ledger_before'] == record['ledger_after']
                  and record['evidence_before'] == record['evidence_after'],
                  'regular rejection mutated evidence')
        v.require(record['attempts_consumed_by_rejection'] == 0, 'negative consumed new attempt')
        for path, sha in record['exact_tested_sources'].items():
            v.require(v.identity(v.ROOT / path)['sha256'] == sha, 'qualification source identity drift')
    for field in ('required_A_through_X', 'required_inherited_A_X'):
        v.require(set(result[field]) == set('ABCDEFGHIJKLMNOPQRSTUVWX'), 'A-X incomplete')
        v.require(all(x['status'] == 'PASS' for x in result[field].values()), 'A-X gate failed')
    root = read(RUN / 'root_confinement_regressions.json')
    extra = read(RUN / 'additional_security_regressions.json')
    race = root['replaceable_component']
    checks = matrix['checks']
    checks['F01_replace_component_before_open'] = direct_record(
        'F01_replace_component_before_open', race['before'], race['after'], race['reason'],
        {'operation': 'Replace mutable component with symlink immediately before no-follow open'},
        str(Path(result['qualification_run_root'])), race['trace_hit'])
    for record in extra['checks']:
        name = 'F01_' + record['name']
        v.require(record['reason'] == record['expected_reason']
                  and record['candidate_artifacts_created'] == 0, 'direct F01 gate failed')
        checks[name] = direct_record(name, record['filesystem_before'], record['filesystem_after'],
            record['reason'], {'operation': record['harness_mutation']}, record['fixture_root'],
            record.get('hits', []))
        if name.endswith('namespace_inode_replacement'):
            v.require(record['filesystem_before'] == record['filesystem_after']
                      and record['replacement_namespace_after'] == {}, 'namespace replacement wrote artifact')
    v.require(len(checks) == 188, 'complete negative population')
    matrix.update(total_count=188, inherited_count=126, new_count=62,
        regular_dispatcher_rejections=185, direct_controlled_path_replacements=3,
        qualification_source_run=ref(RUN / 'rejection_matrix.json'),
        exact_tested_sources=sources(), no_historical_PASS_promoted=True)
    save('rejection_matrix.json', matrix)
    result.update(final_source_pair=sources(), complete_negative_category_count=188,
                  aggregate_matrix=ref(OUT / 'rejection_matrix.json'),
                  raw_final_qualification_result=ref(RUN / 'synthetic_e2e_results.json'))
    save('synthetic_e2e_results.json', result)
    for name in ('root_confinement_regressions.json', 'socket_endpoint_regressions.json',
                 'runtime_authority_test_mapping.json', 'crash_boundary_revalidation.json',
                 'partial_write_revalidation.json', 'additional_security_regressions.json'):
        value = read(RUN / name)
        value.update(exact_tested_sources=sources(), raw_qualification_result=ref(RUN / name))
        save(name, value)
    receipt_keys = ('restricted_route', 'NONE_route', 'receipt_issuance_no_consumption_and_deterministic_sha',
                    'receipt_contract_schema', 'independent_provider_revalidation',
                    'provider_failure_one_immutable_terminal')
    save('receipt_association_revalidation.json', {'status': 'PASS', 'source_pair': sources(),
        'checks': {key: result['tests'][key] for key in receipt_keys},
        'qualification': ref(RUN / 'synthetic_e2e_results.json'),
        'raw_association_corruption_missing_rejected': {name: checks[name] for name in (
            'missing_claim_raw_association', 'corrupt_claim_raw_association')},
        'real_receipts': 0, 'real_claims': 0, 'real_terminals': 0})
    for name, count in [('crash_boundary_revalidation.json', 10), ('partial_write_revalidation.json', 4)]:
        value = read(OUT / name)
        v.require(value['count'] == count and value['status'] == 'SOURCE_LEVEL_FAULT_INJECTION_PASS',
                  'fault suite incomplete')
        for check in value['checks']:
            after = check['after']
            claims = [key for key, item in after.items() if key.startswith('ledger/claims/')
                      and item['type'] == 'file' and item['size_bytes'] > 0]
            terminals = [key for key, item in after.items() if key.startswith('ledger/terminals/')
                         and key.endswith('.json') and item['type'] == 'file']
            v.require(len(claims) <= 1 and len(terminals) <= 1, 'fault duplicate claim/terminal')
            v.require(check['reentry']['automatic_retry'] is False
                      and check['reentry']['evidence_bytes_paths_modes_unchanged'], 'fault retry/overwrite')
        save(name.removesuffix('.json') + '_attempt_boundary_analysis.json', {'status': 'PASS',
             'evidence': ref(OUT / name), 'valid_claim_consumption': 'Only durable nonempty CLAIM record',
             'incomplete_record_or_orphan': 'Reserved partial/lock/sidecar blocks automatic reentry',
             'at_most_one_terminal': True, 'PHYSICAL_POWER_LOSS_DURABILITY_NOT_ESTABLISHED': True})
    external = r.inventory(v.QUALIFICATION)
    save('synthetic_output_inventory.json', {'root': str(v.QUALIFICATION), 'files': external,
         'status': 'PASS_EXACT_SYNTHETIC_OUTPUT_INVENTORY',
         'all_failed_and_successful_runs_retained': True, 'root_alias_or_symlink': False})


def history():
    records = []
    for path in sorted((OUT / 'construction_history').glob('revision_*')):
        record = read(path / 'revision.json')
        checks = {name: ref(path / name) for name in ('ruff_result.json', 'ast_result.json')
                  if (path / name).exists()}
        records.append({'revision': record['revision'], 'record': ref(path / 'revision.json'),
                        'checks': checks, 'historical_result_unchanged': True})
    save('construction_revision_ledger.json', {'status': 'FINAL_RUNTIME_PAIR_QUALIFIED',
        'entries': records, 'exact_final_pair': sources(),
        'historical_failed_G_pair': {
            'controller': 'b8b89f7be85c3709007a4813e9dcd7be6e99c0e438511bf672a742ae8080c523',
            'provider': '03933c18e9e471f06232cbc319fe0cd082829d68ac3f9867090165486a37936f'},
        'historical_G_status': 'FAIL_UNQUALIFIED_NEVER_PROMOTED',
        'failed_qualification_run_1': ref(OUT / 'construction_history/qualification_run_1/qualification_failure.json'),
        'final_full_runtime_qualification': ref(RUN / 'synthetic_e2e_results.json'),
        'execution_semantics': 'Checkpoint affected-tests lists describe the intended checks. Actual execution is established only by retained Ruff/AST/results/diagnostic files. Final run 4 retests all mandatory runtime categories against exact final bytes.',
        'candidate_effective': False})


def package():
    original = v.EVIDENCE / v.RESUME
    failed = v.EVIDENCE / 'v6_production_runtime_topology_stability_successor_remediation_resume_v1'
    finding = read(v.EVIDENCE / v.AUDIT / 'findings.json')
    save('finding_dispositions.json', {'status': 'CANDIDATE_REMEDIATED_PENDING_INDEPENDENT_REAUDIT',
        'findings': [{**x, 'candidate_disposition': 'Remediated and hermetically qualified; not accepted',
                      'current_source_pair': sources(), 'evidence': ref(OUT / ({
                          'F01': 'root_confinement_regressions.json', 'F02': 'socket_endpoint_regressions.json',
                          'F03': 'runtime_authority_test_mapping.json'}[x['id']]))} for x in finding['findings']],
        'historical_audit_findings_unchanged': True, 'HUMAN_PI_ACCEPTED': 'NO'})
    candidate = read(original / 'successor_installation_candidate.json')
    candidate.update(schema='V6_REMEDIATED_SUCCESSOR_INSTALLATION_CANDIDATE_V3',
        status='CANDIDATE_ONLY_FULL_FINAL_HERMETIC_QUALIFICATION_PASS',
        candidate_only=True, HUMAN_PI_ACCEPTED='NO', runtime_effective='NO', execute_now=False,
        current_production_installation_authorized=False, current_real_attempt_authorized=False,
        original_successor_candidate=ref(original / 'successor_installation_candidate.json'),
        original_successor_plan=ref(original / 'successor_installation_plan.json'),
        original_independent_audit_findings=ref(v.EVIDENCE / v.AUDIT / 'findings.json'),
        prior_blocked_remediation_manifests={name: ref(v.EVIDENCE / name / 'artifact_sha256.json')
            for name in ('v6_production_runtime_topology_stability_successor_remediation_v1', failed.name)},
        human_pi_construction_authority=ref(OUT / 'human_pi_decision.json'),
        construction_history=ref(OUT / 'construction_revision_ledger.json'),
        source_pair={role: ref(OUT / ('production_' + role + '_remediated_candidate.py'))
                     for role in ('controller', 'provider')},
        candidate_helpers={name: ref(OUT / name) for name in p.HELPER_SHA256},
        receipt_contract=ref(OUT / 'receipt_authority_contract_v2_candidate.json'),
        receipt_schema_candidate=ref(OUT / 'receipt_schema_v2_candidate.json'),
        security_contracts={name: ref(OUT / name) for name in p.SECURITY_CONTRACT_NAMES},
        contract_version_disposition=ref(OUT / 'contract_version_disposition.json'),
        qualification={name: ref(OUT / name) for name in (
            'synthetic_e2e_results.json', 'rejection_matrix.json', 'root_confinement_regressions.json',
            'socket_endpoint_regressions.json', 'runtime_authority_test_mapping.json',
            'receipt_association_revalidation.json', 'crash_boundary_revalidation.json',
            'partial_write_revalidation.json', 'scientific_projection_revalidation.json',
            'source_semantic_delta.json', 'additional_security_regressions.json')},
        immutable_predecessor_lineage=ref(OUT / 'predecessor_inventory.json'),
        synthetic_output_inventory=ref(OUT / 'synthetic_output_inventory.json'),
        no_historical_acceptance_promoted=True)
    save('remediated_installation_candidate.json', candidate)
    plan = read(original / 'successor_installation_plan.json')
    plan.update(schema='V6_REMEDIATED_SUCCESSOR_INSTALLATION_PLAN_V3_CANDIDATE',
        candidate=ref(OUT / 'remediated_installation_candidate.json'),
        NEXT_GATE='HUMAN_PI_REVIEW_OF_V6_SUCCESSOR_REMEDIATION_CANDIDATE',
        current_production_installation_authorized=False, current_real_attempt_authorized=False,
        execute_now=False, candidate_only=True, HUMAN_PI_ACCEPTED='NO', runtime_effective='NO',
        dependencies_in_order=['Independent reaudit of exact sealed candidate', *plan['dependencies_in_order']],
        final_source_pair=sources(), proposed_helper_targets={
            'qualification_io.py': 'evaluation/downstream_benchmark/screening/v6_preparation_qualification_io_v3.py',
            'socket_endpoint_binding.py': 'evaluation/downstream_benchmark/screening/v6_preparation_socket_endpoint_binding_v3.py'},
        future_effectivity_pin_created=False)
    save('remediated_installation_plan.json', plan)
    # Hash-bearing edges point from a dependent node to immutable prerequisites.
    groups = {
        'accepted_baseline': [v.ROOT / v.CANONICAL, v.ROOT / p.CLOSURE,
                              v.EVIDENCE / 'v6_production_runtime_image_identity_compatibility_bridge_v1/accepted_baseline_binding.json'],
        'predecessor_lineage': [v.EVIDENCE / name / 'artifact_sha256.json' for name in v.PACKAGES],
        'independent_findings': [v.EVIDENCE / v.AUDIT / 'findings.json'],
        'human_pi_authority': [OUT / 'human_pi_decision.json', OUT / 'raw_human_pi_request.txt'],
        'failed_and_iterated_construction': [OUT / 'construction_revision_ledger.json',
            *sorted(path for path in (OUT / 'construction_history').rglob('*') if path.is_file())],
        'source_pair': [OUT / name for name in ('production_controller_remediated_candidate.py',
            'production_provider_remediated_candidate.py', *p.HELPER_SHA256)],
        'versioned_contracts': [OUT / name for name in ('receipt_authority_contract_v2_candidate.json', *p.SECURITY_CONTRACT_NAMES)],
        'final_qualification': [OUT / name for name in candidate['qualification']],
        'scientific_replay': [OUT / 'scientific_projection_revalidation.json'],
        'installation_candidate': [OUT / 'remediated_installation_candidate.json'],
        'installation_plan': [OUT / 'remediated_installation_plan.json'],
    }
    graph = {'schema': 'V6_REMEDIATED_SUCCESSOR_SUPERSESSION_HASH_DAG_V1', 'candidate_only': True,
        'HUMAN_PI_ACCEPTED': 'NO', 'runtime_effective': 'NO', 'execute_now': False,
        'nodes': [{'id': key, 'references': [ref(path) for path in paths]} for key, paths in groups.items()],
        'edges': [[key, dependency] for key, dependencies in {
            'predecessor_lineage': ['accepted_baseline'], 'independent_findings': ['predecessor_lineage'],
            'human_pi_authority': ['independent_findings'],
            'failed_and_iterated_construction': ['human_pi_authority', 'predecessor_lineage'],
            'source_pair': ['failed_and_iterated_construction'],
            'versioned_contracts': ['predecessor_lineage', 'human_pi_authority'],
            'final_qualification': ['source_pair', 'versioned_contracts'],
            'scientific_replay': ['source_pair', 'accepted_baseline'],
            'installation_candidate': ['final_qualification', 'scientific_replay', 'human_pi_authority',
                                       'independent_findings', 'predecessor_lineage'],
            'installation_plan': ['installation_candidate']}.items() for dependency in dependencies],
        'future_effectivity_pin': 'NOT_CREATED', 'historical_acceptance_transfer': False}
    save('supersession_dependency_graph.json', graph)


if __name__ == '__main__':
    qualification()
    history()
    package()
    print(json.dumps({'candidate': ref(OUT / 'remediated_installation_candidate.json'),
                      'plan': ref(OUT / 'remediated_installation_plan.json'),
                      'negative_categories': 188, 'candidate_only': True}))

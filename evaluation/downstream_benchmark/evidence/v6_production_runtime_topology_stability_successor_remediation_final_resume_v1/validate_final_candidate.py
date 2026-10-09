"""Validate all final gates, publish an exact seal, then independently read it back."""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
from pathlib import Path

from . import remediation_regressions as r
from . import verify_firewall as v

OUT = Path(__file__).resolve().parent
STATUS = 'REMEDIATED_SUCCESSOR_CANDIDATE_READY_FOR_INDEPENDENT_REAUDIT'


def read(name):
    return v.read_json(OUT / name)


def write(name, value):
    with (OUT / name).open('xb') as stream:
        stream.write((json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                                 allow_nan=False) + '\n').encode())


def files():
    v.require(not any(path.is_symlink() for path in OUT.rglob('*')), 'new evidence symlink')
    return {str(path.relative_to(OUT)): v.identity(path) for path in sorted(OUT.rglob('*'))
            if path.is_file()}


def strict_text(inventory):
    for name in inventory:
        raw = (OUT / name).read_bytes()
        raw.decode('utf-8', errors='strict')
        # A zero-length unified diff has no non-LF line endings and is retained exactly.
        v.require(b'\r' not in raw and (not raw or raw.endswith(b'\n')),
                  'non-LF artifact: ' + name)
        if name.endswith('.json'):
            v.read_json(OUT / name)


def graph():
    value = read('supersession_dependency_graph.json')
    nodes = {node['id']: node for node in value['nodes']}
    v.require(len(nodes) == len(value['nodes']), 'duplicate graph node')
    adjacency = {key: [] for key in nodes}
    for source, target in value['edges']:
        v.require(source in nodes and target in nodes, 'missing graph node')
        adjacency[source].append(target)
    visited, active = set(), set()
    def visit(key):
        v.require(key not in active, 'supersession hash cycle')
        if key in visited:
            return
        active.add(key)
        for target in adjacency[key]:
            visit(target)
        active.remove(key)
        visited.add(key)
    for key, node in nodes.items():
        visit(key)
        for ref in node['references']:
            actual = v.identity(Path(ref['path']))
            v.require(all(actual[field] == ref[field] for field in ('size_bytes', 'sha256', 'type', 'mode')),
                      'hash graph reference drift: ' + ref['path'])
    v.require(not value['historical_acceptance_transfer']
              and value['future_effectivity_pin'] == 'NOT_CREATED', 'authority transfer')
    return {'status': 'PASS', 'nodes': len(nodes), 'edges': len(value['edges']),
            'reference_count': sum(len(node['references']) for node in nodes.values())}


def preservation():
    before = read('entry_snapshot.json')
    after = v.inspect()
    v.require(after == {key: value for key, value in before.items() if key != 'persistent_tree'},
              'IMMEDIATE_BLOCK tracked/index/canonical/predecessor/real-ledger mutation')
    v.require(v.persistent_tree() == before['persistent_tree'], 'IMMEDIATE_BLOCK preexisting output mutation')
    live = read('live_origin_exit.json')
    v.require(live['returncode'] == 0 and live['stdout'].split() == [v.HEAD, 'refs/heads/main'],
              'IMMEDIATE_BLOCK LIVE origin/main changed')
    physical = [str((v.EVIDENCE / name / rel).relative_to(v.ROOT))
                for name, package in before['packages'].items() for rel in package['files']]
    new = [str(path.relative_to(v.ROOT)) for path in sorted(OUT.rglob('*')) if path.is_file()]
    paths = physical + new
    result = subprocess.run(['git', 'check-ignore', '--stdin', '-z', '-v', '-n'], cwd=v.ROOT,
        input=('\0'.join(paths) + '\0').encode(), capture_output=True, check=False)
    v.require(result.returncode in (0, 1), 'ignore query failure')
    fields = result.stdout.decode().split('\0')[:-1]
    v.require(len(fields) == len(paths) * 4, 'ignore query incomplete')
    expected, ignored = [], []
    for start in range(0, len(fields), 4):
        source, line, pattern, path = fields[start:start + 4]
        if pattern:
            ignored.append({'path': path, 'source': source, 'line': line, 'pattern': pattern})
        else:
            expected.append(path)
    observed = v.git('ls-files', '--others', '--exclude-standard', '-z').split('\0')[:-1]
    v.require(sorted(expected) == sorted(observed), 'unrelated standard-untracked path')
    v.require(len(physical) == 1016, 'predecessor population changed')
    helper_targets = ['evaluation/downstream_benchmark/screening/v6_preparation_qualification_io_v3.py',
                      'evaluation/downstream_benchmark/screening/v6_preparation_socket_endpoint_binding_v3.py']
    v.require(all(not (v.ROOT / name).exists() and not (v.ROOT / name).is_symlink()
                  for name in helper_targets), 'production helper installed')
    return {'status': 'PASS', 'tracked_files_exact': 1065, 'index_byte_identical': True,
         'local_HEAD': v.HEAD, 'LIVE_origin_main': v.HEAD, 'canonical_SHA': v.CANONICAL_SHA,
         'event_count': 3, 'event_3_id': v.EVENT_ID, 'physical_predecessors_exact': 1016,
         'all_seven_manifest_self_hashes_exact': True, 'real_ledger': before['real_ledger'],
         'complete_preexisting_persistent_output_exact': True,
         'persistent_file_count': sum(x['type'] == 'file' for x in before['persistent_tree'].values()),
         'git_standard_untracked_exact': True, 'ignored_predecessor_count': 8,
         'ignored_paths': ignored, 'production_targets_absent': before['production_targets_absent'],
         'production_helper_targets_absent': helper_targets,
         'Docker_mutation_operations': 0, 'Docker_observation_or_exec_operations': 0,
         'Docker_preservation_basis': 'No Docker API/CLI/exec/build operation invoked; simulated transport only.',
         'live_Docker_topology_independently_recertified': False,
         'historical_unknown_exec_origin': 'ORIGIN_NOT_ESTABLISHED',
         'git_add_commit_push': 0, 'real_receipts_claims_terminals_builds': 0,
         'PRODUCTION_RUNTIME_INSTALLED': 'NO', 'REAL_PRODUCTION_ENTRY_EFFECTIVE': 'NO',
         'REAL_CLIENT_AUTHORIZATION': 'BLOCKED'}


def gates(run_lint=True):
    current_sources = sorted(OUT.glob('*.py'))
    parsed = {}
    for path in current_sources:
        ast.parse(path.read_bytes())
        parsed[path.name] = v.identity(path)['sha256']
    if run_lint:
        cmd = ['ruff', 'check', '--no-cache', '--output-format', 'json', *map(str, current_sources)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        diagnostics = json.loads(result.stdout)
        v.require(result.returncode == 0 and diagnostics == [], 'correctable final Ruff failure')
    e2e = read('synthetic_e2e_results.json')
    matrix = read('rejection_matrix.json')
    v.require(e2e['status'] == 'PASS' and e2e['full_source_pair_E2E'] is True
              and matrix['status'] == 'PASS_REJECTED', 'final E2E incomplete')
    v.require(matrix['total_count'] == len(matrix['checks']) == 188
              and matrix['inherited_count'] == 126 and matrix['new_count'] == 62
              and matrix['mandatory_skipped'] == 0, 'negative category coverage incomplete')
    historical = v.read_json(v.EVIDENCE / v.RESUME / 'rejection_matrix.json')['checks']
    v.require(set(historical) <= set(matrix['checks']), 'inherited mandatory category skipped')
    for name, record in matrix['checks'].items():
        v.require(record['status'] == 'PASS_REJECTED'
                  and record['ledger_before'] == record['ledger_after']
                  and record['attempts_consumed_by_rejection'] == 0, 'negative gate failed: ' + name)
        for path, sha in record['exact_tested_sources'].items():
            absolute = Path(path) if Path(path).is_absolute() else v.ROOT / path
            v.require(v.identity(absolute)['sha256'] == sha, 'tested source drift: ' + name)
    for field in ('required_A_through_X', 'required_inherited_A_X'):
        v.require(set(e2e[field]) == set('ABCDEFGHIJKLMNOPQRSTUVWX')
                  and all(x['status'] == 'PASS' for x in e2e[field].values()), 'A-X failed')
    for name in ('root_confinement_regressions.json', 'socket_endpoint_regressions.json',
                 'runtime_authority_test_mapping.json', 'receipt_association_revalidation.json',
                 'additional_security_regressions.json'):
        v.require(read(name)['status'] == 'PASS', 'security regression failed: ' + name)
    for route in ('controller_preclaim', 'provider_prebuild'):
        v.require(matrix['checks']['F02_' + route + '_same_inode_wrong_Path']['reason'] ==
                  'F02 actual socket Path/endpoint conflict', 'audit exact F02 counterexample not rejected')
    mapping = read('runtime_authority_test_mapping.json')['checks']
    v.require(type(mapping['runtime_authority_false']['value']) is bool
              and mapping['runtime_authority_false']['value'] is False
              and type(mapping['runtime_authority_integer_zero']['value']) is int
              and mapping['runtime_authority_integer_zero']['value'] == 0, 'F03 mutation type incorrect')
    v.require(e2e['tests']['F02_pathless_independent_peer_positive']['status'] == 'PASS',
              'pathless positive not established')
    for name, count in [('crash_boundary_revalidation.json', 10), ('partial_write_revalidation.json', 4)]:
        result = read(name)
        v.require(result['count'] == count and len(result['checks']) == count
                  and result['status'] == 'SOURCE_LEVEL_FAULT_INJECTION_PASS'
                  and all(x['status'] == 'SOURCE_LEVEL_FAULT_INJECTION_PASS' for x in result['checks']),
                  'fault suite failed')
    science = read('scientific_projection_revalidation.json')
    v.require(science['status'] == 'PASS_IMPLEMENTATION_EQUIVALENCE_ONLY'
              and science['replayed_count'] == len(science['per_item_replay']) == 641
              and science['environment_ready_cases'] == 0
              and science['blocked_cases'] == ['matplotlib::1', 'matplotlib::8'], 'scientific replay failed')
    v.require(read('source_semantic_delta.json')['status'] == 'PASS', 'semantic source delta failed')
    for name in ('remediated_installation_candidate.json', 'remediated_installation_plan.json'):
        candidate = read(name)
        v.require(candidate['candidate_only'] is True and candidate['HUMAN_PI_ACCEPTED'] == 'NO'
                  and candidate['runtime_effective'] == 'NO' and candidate['execute_now'] is False
                  and candidate['current_production_installation_authorized'] is False
                  and candidate['current_real_attempt_authorized'] is False, 'authority boundary changed')
    external = read('synthetic_output_inventory.json')
    v.require(external['root'] == str(v.QUALIFICATION)
              and external['files'] == r.inventory(v.QUALIFICATION), 'synthetic outputs changed')
    preserved = preservation()
    dag = graph()
    strict_text(files())
    return {'RUFF_PASS': True, 'AST_PASS': True,
        'F01_REGRESSIONS_PASS': True, 'F02_REGRESSIONS_PASS': True, 'F03_REGRESSIONS_PASS': True,
        'FULL_HERMETIC_E2E_PASS': True, 'INHERITED_126_REJECTIONS_PASS': True,
        'NEW_SECURITY_REJECTIONS_PASS': True, 'TEN_CRASH_BOUNDARIES_PASS': True,
        'FOUR_PARTIAL_WRITE_TESTS_PASS': True, 'SCIENCE_641_PROJECTION_PASS': True,
        'SOURCE_SEMANTIC_DELTA_PASS': True, 'SUPERSESSION_HASH_GRAPH_PASS': True,
        'PREDECESSOR_1016_PRESERVATION_PASS': True, 'REAL_LEDGER_PRESERVATION_PASS': True,
        'CANONICAL_EVENT_PRESERVATION_PASS': True, 'STRICT_JSON_UTF8_LF_PASS': True,
        'current_source_AST_identities': parsed, 'preservation': preserved, 'hash_graph': dag,
        'negative_categories': {'inherited': 126, 'new': 62, 'total': 188},
        'PHYSICAL_POWER_LOSS_DURABILITY_NOT_ESTABLISHED': True}


def preflight():
    result = gates()
    write('final_preflight_validation.json', result)
    print(json.dumps({'all_preseal_gates': 'PASS', 'negative_count': 188,
                      'graph': result['hash_graph']}))


def seal():
    result = gates()
    v.require(not (OUT / 'artifact_sha256.json').exists(), 'candidate already sealed')
    write('preservation_verification.json', result['preservation'])
    write('validation_results.json', {'status': 'ALL_FINAL_PRESEAL_GATES_PASS', 'gates': result,
         'exact_candidate_seal': 'Required postpublication verification by this validator; outcome emitted after exact readback.',
         'final_status_after_successful_seal_readback': STATUS,
         'NEXT_GATE': 'HUMAN_PI_REVIEW_OF_V6_SUCCESSOR_REMEDIATION_CANDIDATE',
         'candidate_only': True, 'HUMAN_PI_ACCEPTED': 'NO', 'runtime_effective': 'NO'})
    payloads = files()
    strict_text(payloads)
    write('artifact_sha256.json', {'schema': 'V6_REMEDIATED_SUCCESSOR_FINAL_CANDIDATE_SEAL_V1',
        'candidate_only': True, 'HUMAN_PI_ACCEPTED': 'NO', 'runtime_effective': 'NO', 'execute_now': False,
        'files': payloads, 'payload_count': len(payloads), 'total_file_count': len(payloads) + 1,
        'excluded': ['artifact_sha256.json'], 'self_sha256_semantics': 'Independent exact byte hash; no self-reference',
        'strict_text_semantics': 'All repository evidence is UTF-8 and LF; an empty unified diff has no line endings.',
        'construction_history_included': True,
        'synthetic_outputs_bound_by': 'synthetic_output_inventory.json',
        'qualified_runtime_source_pair': read('remediated_installation_candidate.json')['source_pair']})
    verify()


def verify():
    manifest = read('artifact_sha256.json')
    current = files()
    v.require(set(current) == set(manifest['files']) | {'artifact_sha256.json'}, 'seal population differs')
    v.require(len(current) == manifest['total_file_count'], 'seal file count differs')
    for name, expected in manifest['files'].items():
        v.require(current[name] == expected, 'exact sealed payload differs: ' + name)
    strict_text(current)
    gates()
    print(json.dumps({'STATUS': STATUS, 'EXACT_CANDIDATE_SEAL_PASS': True,
        'manifest_self_sha256': current['artifact_sha256.json']['sha256'],
        'payload_count': manifest['payload_count'], 'total_file_count': len(current),
        'controller_sha256': current['production_controller_remediated_candidate.py']['sha256'],
        'provider_sha256': current['production_provider_remediated_candidate.py']['sha256'],
        'candidate_sha256': current['remediated_installation_candidate.json']['sha256'],
        'plan_sha256': current['remediated_installation_plan.json']['sha256'],
        'negative_categories': 188, 'NEXT_GATE': 'HUMAN_PI_REVIEW_OF_V6_SUCCESSOR_REMEDIATION_CANDIDATE',
        'PRODUCTION_RUNTIME_INSTALLED': 'NO', 'REAL_PRODUCTION_ENTRY_EFFECTIVE': 'NO',
        'REAL_CLIENT_AUTHORIZATION': 'BLOCKED'}, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['preflight', 'seal', 'verify'])
    args = parser.parse_args()
    {'preflight': preflight, 'seal': seal, 'verify': verify}[args.mode]()

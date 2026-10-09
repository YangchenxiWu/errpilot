"""Independent deterministic readback. Read-only; no constructor imports.

Exit 0 and JSON PASS are required. --draft checks the provisional sealed payload;
default checks the final exact seal. No runtime, Docker or ledger APIs are used.
"""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

ROOT = Path('/Users/wuyangchenxi/errpilot')
PACKAGE = Path(__file__).resolve().parent
EVIDENCE = ROOT / 'evaluation/downstream_benchmark/evidence'
CANDIDATE = EVIDENCE / 'v6_production_runtime_topology_stability_successor_remediation_final_resume_v1'
REAUDIT = EVIDENCE / 'v6_production_runtime_topology_stability_successor_remediation_independent_reaudit_v1'
ADJUDICATION = EVIDENCE / 'v6_production_runtime_threat_model_adjudication_v1'
OUTPUT = Path('/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1')
EXPECTED_HEAD = 'e492d159daf188323efcfe121aa019d5b098bfb2'
EXPECTED_CANONICAL = 'e48580c1f9769d1b93ab995e6dcef3689c6920a9ce7b83f728526e9694dc68fd'
EXPECTED_SOURCES = {
    'controller': ('production_controller_remediated_candidate.py', '7c097da628d521987dee76dba8689b0dcdd45d286996ce7509c8442bf8f82b10'),
    'provider': ('production_provider_remediated_candidate.py', '51f842194fd79bb9519bb6f45281a897c5249bb80558750f4660233c4c0bd438'),
}
EXPECTED_DESCRIPTORS = {
    'remediated_installation_candidate.json': '6f42c9740dea963fb49df7459e7d34c13b8774530c20cf26dd3a9fe7395edb01',
    'remediated_installation_plan.json': '43fc8823c8c59db7638b873762fde5f47e84aaab140e218a45b259694bfe355e',
}
EXPECTED_MANIFESTS = {
    CANDIDATE.name: (764, '15161f72e034f4661baa6f2a42dfa649adab4ab33edbb899c3b10d2e3a5a7d15'),
    REAUDIT.name: (38, '45c5eafbddb0cebf27b88dbfa86be1085b7f46c76f8d9d5760e53e7dd841f8f8'),
    ADJUDICATION.name: (24, 'fd714b537b34bf693740a6b34971db4eec65aea02dcc21a8c383b6ba27c7e225'),
}
EXPECTED_CONTRACTS = {
    'client_authorization_contract_candidate.json': '792f21cfa8aa24fd3211cd06c3e9dfe9190e5740796975354923a4a5beff04b1',
    'client_socket_endpoint_binding_contract_v3_candidate.json': 'd003df304951eec524d28ab9cd43d3e15f47fa5242afdd6d109db5d42dd9b149',
    'raw_observation_contract_candidate.json': 'cc74cc482258556da63a23a328d960f4c9aa8e8fda8a8175d985dafc883d352b',
    'raw_sidecar_contract_candidate.json': '08308644b3e3a5c04ef23b4998b7745fb7d9f45aff3c51b33e8db96fa647707e',
    'receipt_authority_contract_v2_candidate.json': '03ac2cb65e4a6122fdf89bd9fdc423fec386331eea8e243a7d728a13815b3c80',
    'receipt_schema_v2_candidate.json': '8927298f08c2882e5d72c095f0781a9421bd32f84f34fac041a33a0253c4f877',
    'topology_stability_contract_candidate.json': 'ec1ba27287ac82d0aac888888ddc58b7c91646d77db8ddeae07807ab5d859a50',
    'transient_diagnostics_contract_candidate.json': 'b64a430540b56c86dfae52632e04e6052d12a0276bb89caf4ad4a74d01edd97d',
}
BOUNDARY = {
    'HUMAN_PI_ACCEPTANCE': 'YES', 'SOURCE_PAIR_ACCEPTED': 'YES',
    'CONTRACT_BASELINE_ACCEPTED': 'YES', 'ACCEPTED_THREAT_MODEL': 'CONTROLLED_SINGLE_TRUSTED_OPERATOR',
    'FREEZE_SCOPE': 'NON_EFFECTIVE_SOURCE_AND_CONTRACT_BASELINE',
    'PRODUCTION_RUNTIME_INSTALLED': 'NO', 'RUNTIME_EFFECTIVE': 'NO',
    'REAL_CLIENT_AUTHORIZATION': 'BLOCKED', 'REAL_PREPARATION_AUTHORIZED': 'NO', 'execute_now': False,
}
CHECK_NAMES = ['ACCEPTANCE_AUTHORITY_EXACT', 'ALL_PREDECESSOR_IDENTITIES',
               'SOURCE_AND_CONTRACT_PINS', 'R01_R02_DISPOSITIONS', 'NON_EFFECTIVE_BOUNDARY',
               'REAL_LEDGER_PRESERVATION', 'CANONICAL_EVENT_PRESERVATION',
               'SOURCE_FREEZE_CLOSURE', 'EXACT_EVIDENCE_SEAL']
REQUIRED = {
    'human_pi_acceptance_decision.json', 'accepted_source_and_contract_pins.json',
    'accepted_threat_model_binding.json', 'historical_findings_disposition.json',
    'non_effective_freeze_record.json', 'lifecycle_closure.json', 'predecessor_integrity.json',
    'preservation_verification.json', 'closure_validation.json', 'commands_run.json',
    'RUN_REPORT.md', 'artifact_sha256.json', 'raw_user_request.txt', 'entry_snapshot.json',
    'entry_verification.json', 'construct_closure.py', 'verify_closure.py',
}


def require(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def load(path):
    def unique(rows):
        result = {}
        for key, value in rows:
            require(key not in result, 'duplicate JSON key: ' + key)
            result[key] = value
        return result
    def finite(value):
        raise RuntimeError('nonfinite JSON constant: ' + value)
    return json.loads(Path(path).read_bytes().decode('utf-8'), object_pairs_hook=unique,
                      parse_constant=finite)


def measure(path):
    path = Path(path)
    metadata = path.lstat()
    mode = stat.S_IMODE(metadata.st_mode)
    if stat.S_ISLNK(metadata.st_mode):
        return {'type': 'symlink', 'mode': mode, 'target': os.readlink(path)}
    if stat.S_ISDIR(metadata.st_mode):
        return {'type': 'directory', 'mode': mode}
    require(stat.S_ISREG(metadata.st_mode), 'unexpected filesystem object: ' + str(path))
    hasher = hashlib.sha256()
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), 'rb') as stream:
        while True:
            raw = stream.read(1024 * 1024)
            if not raw:
                break
            hasher.update(raw)
    return {'type': 'file', 'mode': mode, 'size_bytes': metadata.st_size, 'sha256': hasher.hexdigest()}


def inventory(root):
    result = {'.': measure(root)}
    pending = [Path(root)]
    while pending:
        parent = pending.pop()
        with os.scandir(parent) as entries:
            for entry in entries:
                path = Path(entry.path)
                measured = measure(path)
                result[str(path.relative_to(root))] = measured
                if measured['type'] == 'directory':
                    pending.append(path)
    return result


def git_read(*args):
    p = subprocess.run(['git', *args], cwd=ROOT, capture_output=True,
                       env={**os.environ, 'GIT_OPTIONAL_LOCKS': '0'})
    require(p.returncode == 0, 'read-only Git command failed: ' + repr(args))
    return p.stdout.decode('utf-8')


def references(value):
    found = []
    pending = [value]
    while pending:
        value = pending.pop()
        if isinstance(value, dict):
            if isinstance(value.get('path'), str) and isinstance(value.get('sha256'), str):
                path = Path(value['path'])
                path = path if path.is_absolute() else ROOT / path
                row = measure(path)
                require(row['type'] == 'file' and row['sha256'] == value['sha256'],
                        'reference SHA drift: ' + str(path))
                if 'size_bytes' in value:
                    require(row['size_bytes'] == value['size_bytes'], 'reference size drift: ' + str(path))
                found.append(str(path))
            pending.extend(value.values())
        elif isinstance(value, list):
            pending.extend(value)
    return found


def dag(nodes, edges):
    require(len(edges) == len(set(tuple(e) for e in edges)), 'duplicate graph edges')
    require(all(a in nodes and b in nodes and a != b for a, b in edges), 'bad graph endpoint')
    children = {n: set() for n in nodes}
    for a, b in edges:
        children[a].add(b)
    active = set()
    finished = set()
    def visit(n):
        require(n not in active, 'dependency cycle: ' + n)
        if n in finished:
            return
        active.add(n)
        for child in children[n]:
            visit(child)
        active.remove(n)
        finished.add(n)
    for n in nodes:
        visit(n)


def verify(draft):
    phase = 'DRAFT' if draft else 'FINAL'
    required = REQUIRED if draft else REQUIRED | {'draft_readback_verification.json', 'live_origin_exit.json'}
    require(PACKAGE == EVIDENCE / 'v6_remediated_successor_non_effective_acceptance_freeze_v1', 'wrong package')
    require(set(p.name for p in PACKAGE.iterdir()) == required, 'unexpected closure path population')
    manifest = load(PACKAGE / 'artifact_sha256.json')
    require(manifest['phase'] == phase, 'wrong seal phase')
    require(manifest['total_file_count'] == len(required) and manifest['payload_count'] == len(required) - 1,
            'closure file count mismatch')
    require(set(manifest['files']) == required - {'artifact_sha256.json'}, 'seal path set mismatch')
    require(manifest['excluded'] == ['artifact_sha256.json'], 'unexpected seal exclusions')
    for name, expected in manifest['files'].items():
        require(measure(PACKAGE / name) == expected, 'closure seal byte/metadata mismatch: ' + name)
        raw = (PACKAGE / name).read_bytes()
        raw.decode('utf-8')
        require(b'\r' not in raw and raw.endswith(b'\n'), 'closure LF/text mismatch: ' + name)
    docs = {p.name: load(p) for p in PACKAGE.glob('*.json')}
    decision = docs['human_pi_acceptance_decision.json']
    raw_request = (PACKAGE / 'raw_user_request.txt').read_bytes()
    attachment = Path('/Users/wuyangchenxi/.codex/attachments/780ffd42-d81b-4061-8530-41c990b22a3e/已粘贴的文本.txt')
    require(raw_request == attachment.read_bytes(), 'direct Human-PI request copy mismatch')
    request = raw_request.decode('utf-8')
    require(decision['AUTHORITY'] == 'HUMAN_PI_ACCEPT_V6_REMEDIATED_SUCCESSOR_UNDER_ADOPTED_THREAT_MODEL', 'authority mismatch')
    require(decision['DECISION'] == 'ACCEPT_EXACT_REMEDIATED_SUCCESSOR_FOR_NON_EFFECTIVE_FREEZE', 'decision mismatch')
    require(decision['AUTHORIZATION'] == 'CONSTRUCT_AND_VERIFY_EXACT_NON_EFFECTIVE_ACCEPTANCE_FREEZE_CLOSURE', 'authorization mismatch')
    for phrase in (decision['AUTHORITY'], decision['DECISION'], decision['AUTHORIZATION'],
                   'HUMAN_PI_ACCEPTANCE = YES', EXPECTED_HEAD, EXPECTED_CANONICAL,
                   *(v[1] for v in EXPECTED_SOURCES.values()), *EXPECTED_DESCRIPTORS.values(),
                   *(v[1] for v in EXPECTED_MANIFESTS.values())):
        require(phrase in request, 'authority request omits exact pin/decision: ' + phrase)
    require(decision['record_version'] == 1 and decision['Git_commit_publish_authorized'] is False,
            'wrong acceptance version/authority scope')
    for name in ('human_pi_acceptance_decision.json', 'accepted_source_and_contract_pins.json',
                 'accepted_threat_model_binding.json', 'non_effective_freeze_record.json',
                 'lifecycle_closure.json', 'artifact_sha256.json'):
        require(all(docs[name][k] == v and type(docs[name][k]) is type(v) for k, v in BOUNDARY.items()),
                'non-effective authority boundary mismatch: ' + name)

    # Authenticate all 10 packages before trusting any of their inventory data.
    for n, (_, pin) in EXPECTED_MANIFESTS.items():
        require(measure(EVIDENCE / n / 'artifact_sha256.json')['sha256'] == pin, 'required manifest drift: ' + n)
    old_inv = load(CANDIDATE / 'predecessor_inventory.json')
    require(old_inv['count'] == 1016 and len(old_inv['packages']) == 7, 'historical population drift')
    spec = dict(EXPECTED_MANIFESTS)
    spec.update({n: (v['count'], v['manifest_self_sha256_measured']) for n, v in old_inv['packages'].items()})
    actual_packages = {}
    total = 0
    integrity = docs['predecessor_integrity.json']
    require(set(integrity['packages']) == set(spec), 'predecessor package graph population mismatch')
    for name, (expected_count, expected_pin) in spec.items():
        base = EVIDENCE / name
        actual = inventory(base)
        actual_packages[name] = actual
        regular = {n: v for n, v in actual.items() if v['type'] == 'file'}
        require(not any(v['type'] == 'symlink' for v in actual.values()), 'evidence package symlink: ' + name)
        require(len(regular) == expected_count and regular['artifact_sha256.json']['sha256'] == expected_pin,
                'predecessor manifest identity/count drift: ' + name)
        frozen = load(base / 'artifact_sha256.json')
        require(set(regular) == set(frozen['files']) | {'artifact_sha256.json'}, 'predecessor exact path drift: ' + name)
        for n, row in frozen['files'].items():
            require(not Path(n).is_absolute() and all(p not in ('', '.', '..') for p in n.split('/')),
                    'unsafe manifest relative path')
            require({'size_bytes', 'sha256'} <= row.keys(), 'incomplete predecessor pin')
            require(all(regular[n][k] == v for k, v in row.items() if k in ('size_bytes', 'sha256', 'mode', 'type')),
                    'FROZEN_BYTE_OR_METADATA_DRIFT: ' + name + '/' + n)
        require(integrity['packages'][name]['files'] == regular, 'new integrity inventory mismatch: ' + name)
        total += len(regular)
    require(total == integrity['total_physical_files'] == 1842, '1842 physical evidence population mismatch')
    require((integrity['historical_predecessors'], integrity['remediated_candidate'],
             integrity['independent_reaudit'], integrity['threat_model_adjudication']) == (1016, 764, 38, 24),
            'predecessor population partition mismatch')
    entry = docs['entry_snapshot.json']
    historical_entry = load(ADJUDICATION / 'entry_snapshot.json')
    require(actual_packages == entry['packages'], 'predecessor trees changed during closure')

    # Compare actual tracked/index/persistent bytes both with transaction entry
    # and with the authenticated historical snapshot. No ledger construction.
    names = [n for n in git_read('ls-files', '-z').split('\0') if n]
    tracked = {n: measure(ROOT / n) for n in names}
    require(len(tracked) == 1065 and tracked == entry['tracked'] == historical_entry['tracked'], 'tracked source drift')
    idx = measure(ROOT / git_read('rev-parse', '--git-path', 'index').strip())
    require(idx == entry['index'] == historical_entry['index'], 'Git index drift')
    require(measure(ROOT / git_read('rev-parse', '--git-path', 'HEAD').strip()) == entry['git_HEAD_file'], 'HEAD file drift')
    require(git_read('rev-parse', 'HEAD').strip() == EXPECTED_HEAD == entry['head'], 'local HEAD drift')
    require(git_read('branch', '--show-current').strip() == entry['branch'] == 'main', 'branch drift')
    require(git_read('rev-parse', 'refs/remotes/origin/main').strip() == entry['cached_origin_main'] == EXPECTED_HEAD,
            'cached origin/main drift')
    require(git_read('diff', '--no-ext-diff', '--binary', 'HEAD') == '', 'tracked diff introduced')
    require(git_read('diff', '--no-ext-diff', '--cached', '--binary') == '', 'staged diff introduced')
    untracked = sorted(n for n in git_read('ls-files', '--others', '--exclude-standard', '-z').split('\0')
                       if n and not n.startswith(str(PACKAGE.relative_to(ROOT)) + '/'))
    require(untracked == entry['untracked_outside_write_set'], 'untracked files introduced outside closure')
    persistent = inventory(OUTPUT)
    require(persistent == entry['persistent_tree'] == historical_entry['persistent_tree'], 'REAL_LEDGER_OR_PERSISTENT_OUTPUT_DRIFT')
    require(set(os.listdir(OUTPUT / 'ledger')) == {'claims', 'terminals', 'locks'}, 'unexpected real ledger namespace')
    require(all(not os.listdir(OUTPUT / 'ledger' / n) for n in ('claims', 'terminals', 'locks')), 'real ledger modified')
    work = load(ROOT / 'evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/work_items_candidate.json')
    require(len(work['items']) == 641, 'work population drift')
    ledger = {'UNSTARTED': 641, 'claims': 0, 'terminals': 0, 'locks': 0, 'retries': 0, 'orphans': 0}
    preserved = docs['preservation_verification.json']
    require(preserved['real_ledger'] == ledger and preserved['index'] == idx, 'preservation ledger/index record mismatch')
    require(preserved['persistent_entries'] == len(persistent) == 12271, 'persistent population mismatch')
    require(preserved['persistent_files'] == sum(v['type'] == 'file' for v in persistent.values()) == 7510,
            'persistent file population mismatch')
    inv = load(CANDIDATE / 'synthetic_output_inventory.json')
    prefix = str(Path(inv['root']).relative_to(OUTPUT)) + '/'
    retained = {n[len(prefix):]: v for n, v in persistent.items() if n.startswith(prefix)}
    require(retained == inv['files'] and len(retained) == preserved['qualification_entries'] == 7210,
            'qualification output inventory drift')
    require(all(not os.path.lexists(ROOT / p) for p in preserved['production_targets_absent']), 'production target installed')
    require(preserved['production_targets_absent'] == load(ADJUDICATION / 'entry_verification.json')['production_targets_absent'],
            'production absence boundary narrowed')
    paths = sorted(str((EVIDENCE / n / f).relative_to(ROOT)) for n, tr in actual_packages.items()
                   for f, v in tr.items() if v['type'] == 'file')
    ip = subprocess.run(['git', 'check-ignore', '--stdin'], cwd=ROOT,
                        input=('\n'.join(paths) + '\n').encode(), capture_output=True)
    require(ip.returncode in (0, 1), 'git check-ignore failed')
    ignored = ip.stdout.decode().splitlines()
    require(len(ignored) == 8 and set(ignored) == set(integrity['ignored_files_included']), 'ignored .log coverage drift')

    can_path = ROOT / 'evaluation/downstream_benchmark/v6_current_state.json'
    require(measure(can_path)['sha256'] == EXPECTED_CANONICAL, 'canonical SHA drift')
    can = load(can_path)
    require(can['projection']['state'] == 'PREPARATION_EXECUTION_AUTHORIZED', 'canonical state drift')
    require(can['event_count'] == len(can['event_chain']) == 3, 'canonical event count drift')
    closure = docs['lifecycle_closure.json']
    require(closure['event_chain'] == can['event_chain'] and closure['event_count'] == 3, 'closure event bindings drift')
    for event in can['event_chain']:
        require(measure(ROOT / event['path'])['sha256'] == event['sha256'], 'event exact-byte drift')
    pins = docs['accepted_source_and_contract_pins.json']
    candidate = load(CANDIDATE / 'remediated_installation_candidate.json')
    require(pins['accepted_source_pair'] == candidate['source_pair'], 'accepted source pair changed')
    for role, (name, expected) in EXPECTED_SOURCES.items():
        require(pins['accepted_source_pair'][role]['sha256'] == measure(CANDIDATE / name)['sha256'] == expected,
                'source identity drift: ' + role)
        require(pins['accepted_source_pair'][role]['path'] == str(CANDIDATE / name), 'accepted source path drift')
    for name, expected in EXPECTED_DESCRIPTORS.items():
        require(measure(CANDIDATE / name)['sha256'] == expected, 'installation snapshot drift')
        d = load(CANDIDATE / name)
        require(d['candidate_only'] is True and d['HUMAN_PI_ACCEPTED'] == 'NO' and d['execute_now'] is False
                and d['runtime_effective'] == 'NO' and d['current_production_installation_authorized'] is False
                and d['current_real_attempt_authorized'] is False, 'historical candidate flags changed')
    require(pins['accepted_helper_sources'] == candidate['candidate_helpers'], 'helper dependency population drift')
    require({n: r['sha256'] for n, r in pins['accepted_runtime_contracts'].items()} == EXPECTED_CONTRACTS,
            'contract identity/population mismatch')
    for n, h in EXPECTED_CONTRACTS.items():
        require(measure(CANDIDATE / n)['sha256'] == h, 'runtime contract drift: ' + n)
    require(pins['accepted_capacity_contract']['sha256'] == can['contract']['sha256'], 'capacity contract binding drift')
    require(pins['source_bytes_copied_or_changed'] is False and pins['executable_plan_created'] is False, 'scope expansion')

    findings = docs['historical_findings_disposition.json']
    require(findings['F01']['disposition'] == 'FIXED' and findings['F01']['scope'] == 'Original lexical traversal vulnerability only',
            'F01 disposition changed')
    require(findings['F02']['disposition'] == 'ACCEPTED_CORRECTED_ENDPOINT_CORRELATION', 'F02 disposition changed')
    require(findings['F03']['disposition'] == 'ACCEPTED_CORRECTED_BOOLEAN_TYPE_SEMANTICS', 'F03 disposition changed')
    precise = 'Deliberate adversarial same-UID concurrent directory relocation between successful confinement validation and filesystem operations.'
    require(findings['R01']['disposition'] == 'KNOWN_OUT_OF_SCOPE_RESIDUAL_RISK'
            and findings['R01']['precisely_excluded'] == precise
            and findings['R01']['code_prevents_behavior_claimed'] is False, 'R01 overclaim or exclusion drift')
    threat = docs['accepted_threat_model_binding.json']
    require(threat['precise_exclusion'] == precise and threat['adversarial_relocation_prevented_claimed'] is False
            and threat['ordinary_path_symlink_source_location_guards_retained'] is True
            and threat['arbitrary_same_UID_interference_excluded'] is False
            and threat['BuildKit_client_authorization_or_network_access_waived'] is False, 'threat scope drift')
    require(findings['R02']['disposition'] == 'ACCEPTED_ADDITIVE_ERRATUM'
            and findings['R02']['corrected_locator'] == 'run_4/fixture_76', 'R02 disposition/locator drift')
    erratum = load(ADJUDICATION / 'R02_locator_erratum.json')
    require(findings['R02']['corrected_absolute_locator'] == erratum['corrected_locator'], 'R02 absolute locator mismatch')
    fixture_prefix = str(Path(erratum['corrected_locator']).relative_to(OUTPUT)) + '/'
    actual_fixture = {n[len(fixture_prefix):]: v for n, v in persistent.items() if n.startswith(fixture_prefix)}
    require(actual_fixture == erratum['unique_reconciliation']['retained_fixture_inventory'], 'R02 retained fixture bytes drift')
    require(findings['HISTORICAL_INDEPENDENT_AUDIT'] == 'BLOCKED'
            and load(REAUDIT / 'artifact_sha256.json')['status'] == 'V6_SUCCESSOR_REMEDIATION_INDEPENDENT_REAUDIT_BLOCKED',
            'historical BLOCKED rewritten')
    require(findings['CURRENT_SCOPED_ADJUDICATION'] == 'PASS'
            and load(ADJUDICATION / 'independent_scoped_disposition.json')['CURRENT_SCOPED_ADJUDICATION'] == 'PASS',
            'current scoped disposition drift')
    require(findings['historical_audit_retroactively_passed'] is False
            and findings['physical_power_loss_durability'] == threat['physical_power_loss_durability'] == 'NOT_ESTABLISHED',
            'historical/durability overclaim')

    # All actual reference occurrences, then graph topology and reference coverage.
    new_references = sum(len(references(d)) for n, d in docs.items() if n != 'draft_readback_verification.json')
    original_count = sum(len(references(load(CANDIDATE / n))) for n in (
        'remediated_installation_candidate.json', 'remediated_installation_plan.json',
        'supersession_dependency_graph.json', 'contract_version_disposition.json'))
    require(original_count == closure['historical_graph_reference_occurrences_verified'] == 786, 'historical graph coverage drift')
    graph = load(CANDIDATE / 'supersession_dependency_graph.json')
    dag({n['id'] for n in graph['nodes']}, graph['edges'])
    nodes = closure['nodes']
    edges = closure['edges_dependent_to_dependency']
    require(set(nodes) == set(spec) | {
        'human_pi_acceptance_decision', 'accepted_source_and_contract_pins', 'accepted_threat_model_binding',
        'historical_findings_disposition', 'non_effective_freeze_record', 'predecessor_integrity',
        'preservation_verification', 'entry_verification'}, 'lifecycle graph node coverage mismatch')
    dag(set(nodes), edges)
    paths_to_nodes = {pin['path']: n for n, pin in nodes.items()}
    expected_edges = set()
    for n, pin in nodes.items():
        if pin['path'].startswith(str(PACKAGE) + '/'):
            for path in references(load(pin['path'])):
                if path in paths_to_nodes and paths_to_nodes[path] != n:
                    expected_edges.add((n, paths_to_nodes[path]))
    require(set(tuple(e) for e in edges) == expected_edges, 'lifecycle edges do not match exact dependencies')
    require(closure['lifecycle']['CLOSURE_COMMITTED'] == closure['lifecycle']['CLOSURE_PUBLISHED'] == 'NO', 'commit/publication overclaim')
    require(closure['STATUS'] == 'V6_REMEDIATED_SUCCESSOR_NON_EFFECTIVE_FREEZE_CLOSURE_READY_FOR_COMMIT'
            and closure['NEXT_GATE'] == decision['NEXT_GATE'] == 'HUMAN_PI_AUTHORIZE_EXACT_FREEZE_COMMIT_AND_PUBLISH'
            and closure['STOP'] is True, 'wrong completion gate')
    freeze = docs['non_effective_freeze_record.json']
    require(freeze['SOURCE_AND_CONTRACT_FROZEN'] == 'YES' and freeze['prior_installation_plan_amended'] is False
            and freeze['executable_plan_created'] is False and freeze['canonical_transition_created'] is False
            and freeze['event_4_created'] is False and freeze['installation_effectivity_created'] is False,
            'freeze/effectivity boundary changed')
    require(all(n not in required for n in ('production_controller.py', 'production_provider.py')), 'unexpected runtime copy')
    entry_check = docs['entry_verification.json']
    origin = entry_check['fresh_live_origin_entry']
    require(origin['exit_code'] == 0 and origin['stdout'] == EXPECTED_HEAD + '\trefs/heads/main\n', 'fresh entry origin mismatch')
    validation = docs['closure_validation.json']
    expected_checks = {k: ('PENDING' if draft and k == 'EXACT_EVIDENCE_SEAL' else 'PASS') for k in CHECK_NAMES}
    require(validation['checks'] == expected_checks, 'persisted validation check mismatch')
    require(validation['ordinary_closure_code_failures'] == docs['commands_run.json']['closure_code_failures'], 'failure receipts disagree')
    if not draft:
        receipt = docs['draft_readback_verification.json']
        require(receipt['status'] == 'PASS' and receipt['phase'] == 'DRAFT'
                and receipt['checks'] == {k: 'PASS' for k in CHECK_NAMES}, 'missing successful actual draft readback')
        origin = docs['live_origin_exit.json']
        require(origin['exit_code'] == 0 and origin['stdout'] == EXPECTED_HEAD + '\trefs/heads/main\n', 'fresh exit origin mismatch')
        require(validation['status'] == 'PASS', 'closure validation incomplete')
    return {
        'status': 'PASS', 'phase': phase, 'checks': {k: 'PASS' for k in CHECK_NAMES},
        'seal_sha256': measure(PACKAGE / 'artifact_sha256.json')['sha256'],
        'payload_count': manifest['payload_count'], 'total_file_count': manifest['total_file_count'],
        'physical_predecessor_files': total, 'ignored_log_files': len(ignored),
        'tracked_files': len(tracked), 'index_sha256': idx['sha256'],
        'persistent_entries': len(persistent), 'persistent_files': preserved['persistent_files'],
        'qualification_entries': len(retained), 'real_ledger': ledger,
        'canonical_sha256': EXPECTED_CANONICAL, 'event_count': 3, 'HEAD': EXPECTED_HEAD,
        'original_graph_reference_occurrences': original_count,
        'new_record_reference_occurrences': new_references,
        'lifecycle_nodes': len(nodes), 'lifecycle_edges': len(edges), 'acyclic': True,
        'source_pair': {n: h for n, (_, h) in EXPECTED_SOURCES.items()},
        'accepted_runtime_contract_sha256': EXPECTED_CONTRACTS,
        'R01': 'KNOWN_OUT_OF_SCOPE_RESIDUAL_RISK', 'R02': 'ACCEPTED_ADDITIVE_ERRATUM',
        'fixture_locator': 'run_4/fixture_76', 'HISTORICAL_INDEPENDENT_AUDIT': 'BLOCKED',
        'CURRENT_SCOPED_ADJUDICATION': 'PASS', 'physical_power_loss_durability': 'NOT_ESTABLISHED',
        'production_boundary': {k: BOUNDARY[k] for k in ('PRODUCTION_RUNTIME_INSTALLED', 'RUNTIME_EFFECTIVE',
                                                       'REAL_CLIENT_AUTHORIZATION', 'REAL_PREPARATION_AUTHORIZED')},
        'candidate_tests_executed': False, 'Docker_operations': 0, 'file_writes': 0,
        'STATUS': closure['STATUS'] if not draft else 'DRAFT_READBACK_PASS', 'NEXT_GATE': closure['NEXT_GATE'],
    }


if __name__ == '__main__':
    require(sys.argv[1:] in ([], ['--draft']), 'unsupported verifier arguments')
    try:
        print(json.dumps(verify(bool(sys.argv[1:])), sort_keys=True))
    except Exception as exc:
        print(json.dumps({'status': 'BLOCKED', 'error_type': type(exc).__name__, 'reason': str(exc)}, sort_keys=True))
        raise

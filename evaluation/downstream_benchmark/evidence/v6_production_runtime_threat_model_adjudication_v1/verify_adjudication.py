"""Read-only evidence measurement; exclusive output only in this adjudication package.

No candidate imports, test execution, Docker operations, or ledger constructors.
"""
import ast
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

REPO = Path('/Users/wuyangchenxi/errpilot')
HERE = Path(__file__).resolve().parent
E = HERE.parent
C = E / 'v6_production_runtime_topology_stability_successor_remediation_final_resume_v1'
A = E / 'v6_production_runtime_topology_stability_successor_remediation_independent_reaudit_v1'
OUT = Path('/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1')
HEAD = 'e492d159daf188323efcfe121aa019d5b098bfb2'
CANON_SHA = 'e48580c1f9769d1b93ab995e6dcef3689c6920a9ce7b83f728526e9694dc68fd'
C_SHA = '15161f72e034f4661baa6f2a42dfa649adab4ab33edbb899c3b10d2e3a5a7d15'
A_SHA = '45c5eafbddb0cebf27b88dbfa86be1085b7f46c76f8d9d5760e53e7dd841f8f8'
PINS = {
    'production_controller_remediated_candidate.py': '7c097da628d521987dee76dba8689b0dcdd45d286996ce7509c8442bf8f82b10',
    'production_provider_remediated_candidate.py': '51f842194fd79bb9519bb6f45281a897c5249bb80558750f4660233c4c0bd438',
    'remediated_installation_candidate.json': '6f42c9740dea963fb49df7459e7d34c13b8774530c20cf26dd3a9fe7395edb01',
    'remediated_installation_plan.json': '43fc8823c8c59db7638b873762fde5f47e84aaab140e218a45b259694bfe355e',
}
COMMANDS = []


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pairs(items):
    result = {}
    for k, v in items:
        assert k not in result, ('duplicate JSON key', k)
        result[k] = v
    return result


def reject_constant(value):
    raise ValueError(value)


def read(path):
    return json.loads(Path(path).read_bytes().decode('utf-8'),
                      object_pairs_hook=pairs, parse_constant=reject_constant)


def save(name, value):
    path = HERE / name
    assert path.parent == HERE
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                indent=2, allow_nan=False) + '\n')


def identity(path):
    s = path.lstat()
    result = {'mode': stat.S_IMODE(s.st_mode)}
    if stat.S_ISLNK(s.st_mode):
        return dict(result, type='symlink', target=os.readlink(path))
    if stat.S_ISDIR(s.st_mode):
        return dict(result, type='directory')
    assert stat.S_ISREG(s.st_mode), path
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    return dict(result, type='file', size_bytes=s.st_size, sha256=digest)


def ref(path, **extra):
    return dict(identity(path), path=str(path), **extra)


def tree(root):
    result = {'.': identity(root)}
    def visit(parent):
        for entry in sorted(os.scandir(parent), key=lambda x: x.name):
            path = Path(entry.path)
            info = identity(path)
            result[str(path.relative_to(root))] = info
            if info['type'] == 'directory':
                visit(path)
    visit(root)
    return result


def git(*args):
    argv = ['git', *args]
    p = subprocess.run(argv, cwd=REPO, env={**os.environ, 'GIT_OPTIONAL_LOCKS': '0'},
                       capture_output=True, check=False)
    COMMANDS.append({'argv': argv, 'exit_code': p.returncode,
                     'stdout_sha256': sha(p.stdout), 'stderr': p.stderr.decode()})
    assert p.returncode == 0, COMMANDS[-1]
    return p.stdout.decode()


def package_specs():
    # Authenticate the candidate before using its pinned predecessor inventory.
    assert identity(C / 'artifact_sha256.json')['sha256'] == C_SHA
    inv = read(C / 'predecessor_inventory.json')
    row = read(C / 'artifact_sha256.json')['files']['predecessor_inventory.json']
    assert identity(C / 'predecessor_inventory.json')['sha256'] == row['sha256']
    assert len(inv['packages']) == 7 and inv['count'] == 1016
    specs = {name: (v['count'], v['manifest_self_sha256_measured'])
             for name, v in inv['packages'].items()}
    specs[C.name] = (764, C_SHA)
    specs[A.name] = (38, A_SHA)
    return specs


def snapshot():
    names = [x for x in git('ls-files', '-z').split('\0') if x]
    return {
        'head': git('rev-parse', 'HEAD').strip(),
        'branch': git('branch', '--show-current').strip(),
        'cached_origin_main': git('rev-parse', 'refs/remotes/origin/main').strip(),
        'tracked_diff': git('diff', '--no-ext-diff', '--binary', 'HEAD'),
        'staged_diff': git('diff', '--no-ext-diff', '--cached', '--binary'),
        'tracked': {n: identity(REPO / n) for n in names},
        'index': identity(REPO / git('rev-parse', '--git-path', 'index').strip()),
        'packages': {n: tree(E / n) for n in package_specs()},
        'persistent_tree': tree(OUT),
    }


def check_seals(snap):
    result = {}
    for name, (count, pin) in package_specs().items():
        entries = snap['packages'][name]
        files = {k: v for k, v in entries.items() if v['type'] == 'file'}
        m = read(E / name / 'artifact_sha256.json')
        assert len(files) == count, name
        assert files['artifact_sha256.json']['sha256'] == pin, name
        assert set(files) == set(m['files']) | {'artifact_sha256.json'}, name
        assert not any(v['type'] == 'symlink' for v in entries.values()), name
        for path, expected in m['files'].items():
            assert not Path(path).is_absolute()
            assert all(part not in {'', '.', '..'} for part in path.split('/'))
            assert {'size_bytes', 'sha256'} <= expected.keys()
            for key in ('size_bytes', 'sha256', 'mode', 'type'):
                if key in expected:
                    assert files[path][key] == expected[key], (name, path, key)
        result[name] = {'status': 'PASS', 'physical_files': count,
                        'manifest_self_sha256': pin, 'files': files,
                        'complete_path_set_verified': True, 'ignored_files_included': True}
    assert sum(x['physical_files'] for x in result.values()) == 1818
    return result


def entry():
    snap = snapshot()
    seals = check_seals(snap)
    old = read(A / 'entry_snapshot.json')
    assert snap['tracked'] == old['tracked'] and len(snap['tracked']) == 1065
    assert snap['index'] == old['index']
    assert snap['persistent_tree'] == old['persistent_tree']
    assert snap['branch'] == 'main' and snap['head'] == snap['cached_origin_main'] == HEAD
    assert snap['tracked_diff'] == snap['staged_diff'] == ''
    can_path = REPO / 'evaluation/downstream_benchmark/v6_current_state.json'
    can = read(can_path)
    assert identity(can_path)['sha256'] == CANON_SHA
    assert can['projection']['state'] == 'PREPARATION_EXECUTION_AUTHORIZED'
    assert can['event_count'] == len(can['event_chain']) == 3
    events = []
    for event in can['event_chain']:
        r = ref(REPO / event['path'])
        assert r['sha256'] == event['sha256']
        events.append(dict(event, measured=r))
    source_pins = {n: ref(C / n) for n in PINS}
    assert all(source_pins[n]['sha256'] == h for n, h in PINS.items())
    flags = {}
    for name in ('remediated_installation_candidate.json', 'remediated_installation_plan.json'):
        v = read(C / name)
        flags[name] = {k: v[k] for k in ('candidate_only', 'HUMAN_PI_ACCEPTED', 'runtime_effective', 'execute_now')}
        assert flags[name] == {'candidate_only': True, 'HUMAN_PI_ACCEPTED': 'NO', 'runtime_effective': 'NO', 'execute_now': False}
        assert v['current_production_installation_authorized'] is False
        assert v['current_real_attempt_authorized'] is False
    ledger = {k: sorted(os.listdir(OUT / 'ledger' / k)) for k in ('claims', 'terminals', 'locks')}
    assert all(not v for v in ledger.values())
    assert set(os.listdir(OUT / 'ledger')) == set(ledger)
    work = read(REPO / 'evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/work_items_candidate.json')
    assert len(work['items']) == 641
    targets = read(A / 'preservation_verification.json')['production_targets_absent']
    assert all(not os.path.lexists(REPO / p) for p in targets)
    allsealed = sorted(str((E / n / p).relative_to(REPO)) for n, v in seals.items() for p in v['files'])
    ignored_raw = subprocess.run(['git', 'check-ignore', '--stdin'], input=('\n'.join(allsealed)+'\n').encode(),
                                 cwd=REPO, capture_output=True, check=False)
    assert ignored_raw.returncode in (0, 1)
    ignored = ignored_raw.stdout.decode().splitlines()
    assert len(ignored) == 8
    COMMANDS.append({'argv': ['git', 'check-ignore', '--stdin'], 'input': '1818 measured package file paths',
                     'exit_code': ignored_raw.returncode, 'stdout': ignored})
    inv = read(C / 'synthetic_output_inventory.json')
    qual = Path(inv['root'])
    actual = tree(qual)
    actual.pop('.')
    assert actual == inv['files']
    summary = {'status': 'PASS', 'measured_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'head': snap['head'], 'branch': snap['branch'], 'cached_origin_main': snap['cached_origin_main'],
               'fresh_live_origin_entry': {'command': ['git', 'ls-remote', 'origin', 'refs/heads/main'],
                    'tool_chunk_id': '0f1c12', 'exit_code': 0, 'stdout': HEAD+'\trefs/heads/main\n'},
               'canonical': ref(can_path), 'state': can['projection']['state'], 'event_count': 3,
               'events': events, 'source_and_descriptor_pins': source_pins, 'flags': flags,
               'tracked_count': 1065, 'tracked_diff': '', 'staged_diff': '', 'index': snap['index'],
               'real_ledger': {'UNSTARTED': 641, 'claims': 0, 'terminals': 0, 'locks': 0, 'retries': 0, 'orphans': 0},
               'ledger_method': 'Read-only entire persistent tree and empty ledger namespace comparison to sealed audit snapshot; no constructor.',
               'production_targets_absent': targets, 'ignored_sealed_paths': ignored,
               'airos_current_state_present': (REPO / '.airos/current_state.md').exists(),
               'separate_airos_contract_present': (REPO / '.airos/contracts').exists(),
               'governing_request': 'Latest attached Human-PI adjudication request; exact copy in raw_user_request.txt'}
    save('entry_snapshot.json', snap)
    save('predecessor_integrity.json', {'status': 'PASS', 'total_physical_files': 1818,
         'historical_predecessors': 1016, 'candidate': 764, 'independent_reaudit': 38, 'packages': seals})
    save('entry_verification.json', summary)
    save('synthetic_output_readback.json', {'status': 'PASS', 'root': str(qual),
         'inventory_reference': ref(C / 'synthetic_output_inventory.json'),
         'types': dict(collections.Counter(x['type'] for x in actual.values())),
         'followed_symlinks': False, 'new_test_execution': False,
         'entire_persistent_tree_matches_sealed_reaudit_snapshot': True,
         'persistent_entries': len(snap['persistent_tree']),
         'persistent_files': sum(v['type'] == 'file' for v in snap['persistent_tree'].values())})
    save('entry_commands.json', COMMANDS)
    print(json.dumps({'status': 'PASS', 'physical_files': 1818, 'tracked': 1065,
                      'ignored_files': len(ignored), 'persistent_entries': len(snap['persistent_tree'])}))


def final_verify():
    snap = snapshot()
    baseline = read(HERE / 'entry_snapshot.json')
    assert snap == baseline, 'entry/exit snapshot mismatch'
    check_seals(snap)
    entry_data = read(HERE / 'entry_verification.json')
    assert all(not os.path.lexists(REPO / p) for p in entry_data['production_targets_absent'])
    assert read(A / 'validation_results.json')['STATUS'] == 'V6_SUCCESSOR_REMEDIATION_INDEPENDENT_REAUDIT_BLOCKED'
    exit_live = read(HERE / 'live_origin_exit.json')
    assert exit_live['exit_code'] == 0 and exit_live['stdout'] == HEAD+'\trefs/heads/main\n'
    standard = [p for p in git('ls-files', '--others', '--exclude-standard', '-z').split('\0') if p]
    allowed = [str((E / n).relative_to(REPO))+'/' for n in package_specs()]
    allowed.append(str(HERE.relative_to(REPO))+'/')
    assert all(any(p.startswith(prefix) for prefix in allowed) for p in standard), 'unexpected untracked path'
    scope = read(HERE / 'threat_model_contract.json')
    disposition = read(HERE / 'independent_scoped_disposition.json')
    r01 = read(HERE / 'R01_scope_adjudication.json')
    assert disposition['CURRENT_SCOPED_ADJUDICATION'] == 'PASS'
    assert disposition['HISTORICAL_INDEPENDENT_AUDIT'] == 'BLOCKED'
    assert disposition['HUMAN_PI_ACCEPTED'] == 'NO' and disposition['execute_now'] is False
    assert disposition['runtime_effective'] == 'NO' and disposition['candidate_only'] is True
    assert len(scope['in_scope']) == 11
    assert scope['out_of_scope'] == r01['exact_accepted_exclusion']
    assert r01['R01_ORIGINAL_AUDIT_SEVERITY'] == 'MATERIAL'
    assert r01['R01_ACCEPTED_SCOPE_DISPOSITION'] == 'OUT_OF_SCOPE_RESIDUAL_RISK'
    assert r01['R01_CODE_FIX_FOR_ADVERSARIAL_RELOCATION'] == 'NOT_CLAIMED'
    assert r01['FULL_ADVERSARIAL_RELOCATION_SAFETY'] == r01['PHYSICAL_POWER_LOSS_DURABILITY'] == 'NOT_ESTABLISHED'
    future = read(HERE / 'production_operational_preconditions.json')
    assert len(future['conditions']) == 8
    assert all(c['currently_verified_by_this_transaction'] is False for c in future['conditions'])
    assert future['PRODUCTION_EXECUTION'] == 'BLOCKED'
    assert read(HERE / 'R02_locator_erratum.json')['historical_record_preserved'] is True
    return snap


def seal():
    snap = final_verify()
    save('preservation_verification.json', {
        'status': 'PASS', 'all_snapshot_fields_equal': True,
        'preserved_physical_files': 1818, 'preserved_tracked_files': 1065,
        'index': snap['index'], 'head': HEAD, 'branch': 'main', 'live_origin_exit': read(HERE / 'live_origin_exit.json'),
        'canonical_SHA256': CANON_SHA, 'event_count': 3,
        'real_ledger': read(HERE / 'entry_verification.json')['real_ledger'],
        'persistent_tree_unchanged': True, 'candidate_and_audit_bytes_unchanged': True,
        'historical_audit_status_unchanged': 'V6_SUCCESSOR_REMEDIATION_INDEPENDENT_REAUDIT_BLOCKED',
        'Docker_operations': 0, 'candidate_test_execution': 0, 'ledger_writes': 0,
        'production_preconditions_currently_verified': False,
        'commit_push_installation_or_acceptance': False,
        'write_boundary': str(HERE), 'snapshot_reference': ref(HERE / 'entry_snapshot.json')})
    save('final_commands.json', COMMANDS)
    files = {k: v for k, v in tree(HERE).items() if v['type'] == 'file'}
    assert 'artifact_sha256.json' not in files
    for name in files:
        raw = (HERE / name).read_bytes()
        raw.decode('utf-8')
        assert b'\r' not in raw and raw.endswith(b'\n'), name
        if name.endswith('.json'):
            read(HERE / name)
        elif name.endswith('.py'):
            ast.parse(raw.decode('utf-8'), filename=name)
    save('artifact_sha256.json', {'schema': 'V6_THREAT_MODEL_ADJUDICATION_SEAL_V1',
        'files': files, 'payload_count': len(files), 'total_file_count': len(files)+1,
        'excluded': ['artifact_sha256.json'], 'self_sha256_semantics': 'Exact byte SHA emitted after independent readback; no circular self-reference.',
        'HUMAN_PI_ACCEPTED': 'NO', 'runtime_effective': 'NO', 'execute_now': False,
        'status': read(HERE / 'independent_scoped_disposition.json')['STATUS']})
    verify()


def verify():
    final_verify()
    m = read(HERE / 'artifact_sha256.json')
    entries = tree(HERE)
    files = {k: v for k, v in entries.items() if v['type'] == 'file'}
    assert set(files) == set(m['files']) | {'artifact_sha256.json'}
    assert len(files) == m['total_file_count'] == m['payload_count']+1
    assert all(files[k] == v for k, v in m['files'].items())
    assert all(v['type'] == 'file' for k, v in entries.items() if k != '.')
    for name in files:
        raw = (HERE / name).read_bytes()
        raw.decode('utf-8')
        assert b'\r' not in raw and raw.endswith(b'\n'), name
        if name.endswith('.json'):
            read(HERE / name)
        elif name.endswith('.py'):
            ast.parse(raw.decode('utf-8'), filename=name)
    print(json.dumps({'status': 'PASS_EXACT_SEAL_READBACK', 'manifest_sha256': files['artifact_sha256.json']['sha256'],
                      'payload_count': m['payload_count'], 'physical_count': m['total_file_count'],
                      'preserved_physical_files': 1818, 'preserved_tracked_files': 1065}))


if __name__ == '__main__':
    {'entry': entry, 'seal': seal, 'verify': verify}[sys.argv[1]]()

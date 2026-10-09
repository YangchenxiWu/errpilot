"""New scoped physical-inventory verifier under the Human-PI resume decision."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path('/Users/wuyangchenxi/errpilot')
HERE = ROOT / ('evaluation/downstream_benchmark/evidence/'
               'v6_production_runtime_topology_stability_successor_remediation_final_resume_v1')
EVIDENCE = HERE.parent
OUTPUT = Path('/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1')
QUALIFICATION = OUTPUT / ('qualification/'
                          'production_runtime_topology_stability_successor_remediation_final_resume_v1')
REQUEST = Path('/Users/wuyangchenxi/.codex/attachments/'
               '18878d3a-1b4a-4dbb-adaa-56c3f87fb616/已粘贴的文本.txt')
HEAD = 'e492d159daf188323efcfe121aa019d5b098bfb2'
CANONICAL = 'evaluation/downstream_benchmark/v6_current_state.json'
CANONICAL_SHA = 'e48580c1f9769d1b93ab995e6dcef3689c6920a9ce7b83f728526e9694dc68fd'
EVENT_ID = '237d8020668f338c04065beb8557d8f25263fbfc0282003dcc5b2af67a20a50d'
AUDIT = 'v6_production_runtime_topology_stability_successor_independent_audit_v1'
RESUME = 'v6_production_runtime_topology_stability_successor_resume_v1'
PACKAGES = {
    'v6_production_runtime_image_identity_compatibility_bridge_v1':
        (281, 'ee8948b829a072ff10e3a41ba086afb4151821010661d89a05ce444ba95369e8'),
    'v6_production_runtime_topology_exec_forensics_v1':
        (220, '96b22bb49d14b366d3d6ef7f4d9101b48cae5c6e85112c4798319d4fc7d2c1dd'),
    'v6_production_runtime_topology_stability_successor_v1':
        (71, 'def7f4bd8569094ce608dd1ecc8b790c690780ec827dc43c11e2207284f5f21d'),
    RESUME: (44, 'a24c561d6fc68d316908cc62813624f1acb5eff4c93121ae1704938a46a6fec4'),
    AUDIT: (339, 'c077bca8014466ec10adac46470671f5039da1ceed9a43b1daa372bd77337771'),
}
CONTROLLING = {
    'production_controller_successor_candidate.py':
        '93696b9a6e6fa7bd3c207c27e0b6c098bd1d68aa8781167edc4c74bc9cc5de41',
    'production_provider_successor_candidate.py':
        '8731a0ab7eb8605201b754c366b601c9f821e5eaa8c2d52204bbcdab8eaf809c',
    'successor_installation_candidate.json':
        '43cc158cab9d91a50aa8e225e57f74363a0d2f2660c31e1ef00d23ec2485c83d',
    'successor_installation_plan.json':
        'd4459a2d380ee5cd35107b19b4525750599c850393fbb1002f47014d5323a210',
}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def semantic(value):
    return digest((json.dumps(value, ensure_ascii=False, sort_keys=True,
                              separators=(',', ':'), allow_nan=False) + '\n').encode())


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f'duplicate JSON key: {path}: {key}')
            result[key] = value
        return result

    def invalid(value):
        raise ValueError(f'nonfinite JSON: {path}: {value}')

    return json.loads(path.read_bytes().decode('utf-8'), object_pairs_hook=unique,
                      parse_constant=invalid)


def identity(path):
    st = path.lstat()
    value = {'mode': stat.S_IMODE(st.st_mode)}
    if path.is_symlink():
        return {**value, 'type': 'symlink', 'target': os.readlink(path)}
    if stat.S_ISDIR(st.st_mode):
        return {**value, 'type': 'directory'}
    require(stat.S_ISREG(st.st_mode), f'special file refused: {path}')
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(chunk)
    return {**value, 'type': 'file', 'size_bytes': st.st_size, 'sha256': h.hexdigest()}


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT).decode('utf-8')


def write(name, value):
    path = HERE / name
    require(path.parent == HERE and not path.is_symlink(), 'output outside new namespace')
    raw = value if isinstance(value, bytes) else (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                   allow_nan=False) + '\n').encode('utf-8')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
    except BaseException:
        raise


def inspect():
    packages = {}
    expected_paths = set()
    for name, (count, manifest_sha) in PACKAGES.items():
        root = EVIDENCE / name
        require(not any(p.is_symlink() for p in root.rglob('*')), 'predecessor symlink')
        files = {str(p.relative_to(root)): identity(p)
                 for p in sorted(root.rglob('*')) if p.is_file()}
        manifest = read_json(root / 'artifact_sha256.json')
        require(len(files) == count, f'predecessor count: {name}')
        require(files['artifact_sha256.json']['sha256'] == manifest_sha,
                f'predecessor manifest SHA: {name}')
        require(set(files) == set(manifest['files']) | {'artifact_sha256.json'},
                f'predecessor exact manifest population: {name}')
        for rel, ref in manifest['files'].items():
            require(all(files[rel][k] == ref[k] for k in ('size_bytes', 'sha256')),
                    f'predecessor payload size/SHA: {name}/{rel}')
        packages[name] = {'status': 'PASS_EXACT_PATH_SIZE_SHA', 'count': count,
                          'manifest_self_sha256_measured': manifest_sha,
                          'payload_count': len(manifest['files']), 'files': files}
        expected_paths.update(str((root / rel).relative_to(ROOT)) for rel in files)
    tracked_paths = git('ls-files', '-z').split('\0')[:-1]
    tracked = {rel: identity(ROOT / rel) for rel in tracked_paths}
    prior = read_json(EVIDENCE / AUDIT / 'entry_snapshot.json')
    require(len(tracked) == 1065 and tracked == prior['tracked'], 'tracked byte/mode drift')
    index = identity(ROOT / '.git/index')
    require(index == prior['index'], 'index byte/mode drift')
    require(git('diff', '--name-only', 'HEAD') == '', 'tracked diff')
    require(git('diff', '--cached', '--name-only') == '', 'staged diff')
    require(git('branch', '--show-current').strip() == 'main', 'wrong branch')
    require(git('rev-parse', 'HEAD').strip() == HEAD, 'local HEAD drift')
    require(git('rev-parse', 'refs/remotes/origin/main').strip() == HEAD,
            'local origin/main drift')
    prefix = str(HERE.relative_to(ROOT)) + '/'
    standard = {rel for rel in git('ls-files', '--others', '--exclude-standard', '-z')
                .split('\0')[:-1] if not rel.startswith(prefix)}
    all_others = {rel for rel in git('ls-files', '--others', '-z').split('\0')[:-1]
                  if not rel.startswith(prefix)}
    require(expected_paths <= all_others, 'a predecessor file is tracked or missing')
    ignored_expected = sorted(expected_paths - standard)
    ignore_rules = {}
    for rel in ignored_expected:
        ignore_rules[rel] = git('check-ignore', '-v', rel).strip()
    canonical = identity(ROOT / CANONICAL)
    current = read_json(ROOT / CANONICAL)
    require(canonical['sha256'] == CANONICAL_SHA, 'canonical byte drift')
    require(current['projection']['state'] == 'PREPARATION_EXECUTION_AUTHORIZED'
            and current['event_count'] == 3 and current['event_head']['event_id'] == EVENT_ID,
            'canonical/event #3 drift')
    event_files = {ref['path']: identity(ROOT / ref['path']) for ref in current['event_chain']}
    require(all(event_files[ref['path']]['sha256'] == ref['sha256']
                for ref in current['event_chain']), 'event file drift')
    sources = {rel: identity(EVIDENCE / RESUME / rel) for rel in CONTROLLING}
    require(all(sources[rel]['sha256'] == expected for rel, expected in CONTROLLING.items()),
            'controlling predecessor source/candidate/plan drift')
    require(not QUALIFICATION.is_symlink(), 'qualification root symlink')
    require({p.name for p in OUTPUT.iterdir()} == {'ledger', 'namespace.json', 'qualification'},
            'unexpected real output top-level entry')
    real_paths = [OUTPUT, OUTPUT / 'namespace.json', OUTPUT / 'ledger',
                  *sorted((OUTPUT / 'ledger').rglob('*'))]
    real_tree = {str(p.relative_to(OUTPUT)): identity(p) for p in real_paths}
    require({p.name for p in (OUTPUT / 'ledger').iterdir()} == {'claims', 'terminals', 'locks'},
            'real ledger namespace drift')
    require(all(not list((OUTPUT / 'ledger' / n).iterdir())
                for n in ('claims', 'terminals', 'locks')), 'real ledger nonempty')
    work_path = ROOT / ('evaluation/downstream_benchmark/evidence/'
                        'v6_preparation_execution_activation_v1/work_items_candidate.json')
    population = read_json(work_path)
    ids = [x['base_attempt_id'] for x in population['items']]
    population_ref = {'path': str(work_path), 'file_sha256': digest(work_path.read_bytes()),
                      'semantic_sha256': semantic(population),
                      'ordered_id_sha256': semantic(ids), 'count': len(ids),
                      'variants': dict(Counter(x['variant'] for x in population['items'])),
                      'restricted': sum(x['build_network_required'] for x in population['items']),
                      'none': sum(not x['build_network_required'] for x in population['items']),
                      'blocked': [x['case_id'] for x in population['blocked']]}
    require(population_ref['file_sha256'] ==
            '288eaed9f7e9ff4daf2978e7c41b6c6ead83e9d99b9ddee7801c163153bd63bb',
            'population file drift')
    require(population_ref['semantic_sha256'] ==
            'f3a719f2a92f1d1ba96baa9dd3936e8bd87d330f048542c9ee5cfce86185a800',
            'population semantic drift')
    require(population_ref['ordered_id_sha256'] ==
            '7a329a4c301e5ddd6bae1047f6bce77430aca5a21d71a7a749dfb3899e4c7a5c',
            'ordered ID drift')
    require(len(set(ids)) == len(ids) == 641 and population_ref['restricted'] == 583
            and population_ref['none'] == 58 and population_ref['variants'] ==
            {'SOURCE_INDEPENDENT': 221, 'BUGGY': 210, 'FIXED': 210}
            and population_ref['blocked'] == ['matplotlib::1', 'matplotlib::8'],
            'population counts drift')
    targets = read_json(EVIDENCE / AUDIT / 'preservation_verification.json')[
        'production_targets_absent']
    require(all(not (ROOT / p).exists() and not (ROOT / p).is_symlink() for p in targets),
            'production target present')
    return {'packages': packages, 'tracked': tracked, 'index': index,
            'canonical': canonical, 'event_files': event_files,
            'event_count': 3, 'event_id': EVENT_ID, 'head': HEAD, 'branch': 'main',
            'state': current['projection']['state'], 'predecessor_sources': sources,
            'standard_untracked_paths': sorted(standard),
            'standard_untracked_count': len(standard),
            'expected_physical_evidence_count': len(expected_paths),
            'ignored_expected_paths': ignored_expected, 'ignore_rules': ignore_rules,
            'standard_untracked_outside_expected': sorted(standard - expected_paths),
            'all_untracked_including_ignored_count': len(all_others),
            'real_output_tree_excluding_historical_qualification': real_tree,
            'population': population_ref,
            'real_ledger': {'UNSTARTED': 641, 'claims': 0, 'terminals': 0,
                            'retries': 0, 'orphans': 0},
            'real_ledger_observation_method':
                'Exact population plus empty claims/terminals/locks directories; '
                'matches frozen Ledger.state UNSTARTED branch; Ledger not invoked.',
            'production_targets_absent': targets,
            'new_qualification_child_absent': str(QUALIFICATION),
            'airos_current_state_present': (ROOT / '.airos/current_state.md').exists()}



PACKAGES['v6_production_runtime_topology_stability_successor_remediation_v1'] = (
    14, '5985cbfca51bdff9a146562bc064ebbe97ef16dcb77f39c587a45cff6e0e4be6')


PACKAGES['v6_production_runtime_topology_stability_successor_remediation_resume_v1'] = (
    47, 'a266e734b8d97b1205affab0e252e4d85363b9dd404cbeb424cd7c7c6f3ab3f3')


def persistent_tree():
    return {str(path.relative_to(OUTPUT)): identity(path)
            for path in [OUTPUT, *sorted(OUTPUT.rglob('*'))]
            if path != QUALIFICATION and not path.is_relative_to(QUALIFICATION)}


def reconcile(snapshot):
    physical = [str((EVIDENCE / name / rel).relative_to(ROOT))
                for name, package in snapshot['packages'].items() for rel in package['files']]
    result = subprocess.run(['git', 'check-ignore', '--stdin', '-z', '-v', '-n'],
                            cwd=ROOT, input=('\0'.join(physical) + '\0').encode(),
                            capture_output=True, check=False)
    require(result.returncode in (0, 1), 'ignore query failed')
    fields = result.stdout.decode().split('\0')[:-1]
    require(len(fields) == 4 * len(physical), 'ignore result incomplete')
    statuses = {}
    for start in range(0, len(fields), 4):
        source, line, pattern, path = fields[start:start + 4]
        statuses[path] = {'ignored': bool(pattern), 'source': source, 'line': line, 'pattern': pattern}
    expected = sorted(path for path, value in statuses.items() if not value['ignored'])
    require(expected == snapshot['standard_untracked_paths'], 'unrelated standard-untracked paths')
    require(len(physical) == 1016, 'predecessor count')
    return {'status': 'PASS', 'physical_count': 1016, 'visible_count': len(expected),
            'ignored_count': 1016 - len(expected), 'path_status': statuses,
            'expected_standard_untracked': expected, 'observed_standard_untracked': expected,
            'unexpected_standard_untracked': [], 'ignore_rules_changed': False}


def capture():
    require(not QUALIFICATION.exists(), 'qualification child already exists')
    snapshot = inspect()
    reconciliation = reconcile(snapshot)
    live = read_json(HERE / 'live_origin_entry.json')
    require(live['returncode'] == 0 and live['stdout'].split() == [HEAD, 'refs/heads/main'],
            'LIVE origin mismatch')
    snapshot['persistent_tree'] = persistent_tree()
    write('entry_snapshot.json', snapshot)
    write('predecessor_inventory.json', {'status': 'PASS', 'count': 1016, 'packages': snapshot['packages']})
    write('git_population_reconciliation.json', reconciliation)
    write('entry_verification.json', {'status': 'PASS', 'head': HEAD, 'live_origin_main': HEAD,
        'canonical_sha256': CANONICAL_SHA, 'state': snapshot['state'], 'event_count': 3,
        'event_3_id': EVENT_ID, 'tracked_count': 1065, 'index_exact': True,
        'physical_predecessor_count': 1016, 'visible_count': reconciliation['visible_count'],
        'ignored_count': reconciliation['ignored_count'], 'real_ledger': snapshot['real_ledger'],
        'production_installed': 'NO', 'runtime_effective': 'NO', 'REAL_CLIENT_AUTHORIZATION': 'BLOCKED',
        'exclusive_qualification_child_unused': True})
    request = REQUEST.read_bytes()
    write('raw_human_pi_request.txt', request)
    write('human_pi_decision.json', {
        'authority': 'HUMAN_PI_ADJUDICATE_V6_SUCCESSOR_REMEDIATION_CONSTRUCTION_FAILURE_POLICY',
        'decision': 'ADOPT_CONSTRUCTION_ITERATION_AND_FINAL_GATE_SEPARATION_V1',
        'authorization': 'RESUME_BOUNDED_F01_F02_F03_REMEDIATION_WITH_CONSTRUCTION_FIX_LOOP',
        'open': 'OPEN_V6_SUCCESSOR_REMEDIATION_FINAL_CONSTRUCTION_RESUME',
        'request_sha256': digest(request), 'candidate_only': True, 'HUMAN_PI_ACCEPTED': 'NO',
        'runtime_effective': 'NO', 'execute_now': False})
    print(json.dumps(read_json(HERE / 'entry_verification.json'), sort_keys=True))


if __name__ == '__main__':
    capture()

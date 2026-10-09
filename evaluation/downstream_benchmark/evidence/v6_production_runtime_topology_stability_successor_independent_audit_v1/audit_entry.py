"""Independent read-only entry inventories; output confined to this audit."""
import hashlib
import json
import os
import stat
import subprocess
from pathlib import Path

ROOT = Path('/Users/wuyangchenxi/errpilot')
HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
CAND = EVIDENCE / 'v6_production_runtime_topology_stability_successor_resume_v1'
EXPECTED_HEAD = 'e492d159daf188323efcfe121aa019d5b098bfb2'
PACKAGES = {
    'v6_production_runtime_image_identity_compatibility_bridge_v1': (281, 'ee8948b829a072ff10e3a41ba086afb4151821010661d89a05ce444ba95369e8'),
    'v6_production_runtime_topology_exec_forensics_v1': (220, '96b22bb49d14b366d3d6ef7f4d9101b48cae5c6e85112c4798319d4fc7d2c1dd'),
    'v6_production_runtime_topology_stability_successor_v1': (71, 'def7f4bd8569094ce608dd1ecc8b790c690780ec827dc43c11e2207284f5f21d'),
    CAND.name: (44, 'a24c561d6fc68d316908cc62813624f1acb5eff4c93121ae1704938a46a6fec4'),
}

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def identity(path):
    s = path.lstat()
    value = {'mode': stat.S_IMODE(s.st_mode)}
    if stat.S_ISLNK(s.st_mode):
        return {**value, 'type': 'symlink', 'target': os.readlink(path)}
    if stat.S_ISDIR(s.st_mode):
        return {**value, 'type': 'directory'}
    assert stat.S_ISREG(s.st_mode), str(path)
    return {**value, 'type': 'file', 'size_bytes': s.st_size, 'sha256': sha(path)}

def tree(root):
    return {str(p.relative_to(root)): identity(p) for p in sorted(root.rglob('*'))}

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT).decode()

def write(name, value):
    p = HERE / name
    with p.open('x') as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write('\n')

def main():
    assert git('rev-parse', 'HEAD').strip() == EXPECTED_HEAD
    assert git('diff', '--name-only') == git('diff', '--cached', '--name-only') == ''
    tracked = git('ls-files', '-z').split('\0')[:-1]
    assert len(tracked) == 1065
    preexisting = [p for p in git('ls-files', '--others', '--exclude-standard', '-z').split('\0')[:-1]
                   if not p.startswith(str(HERE.relative_to(ROOT)) + '/')]
    assert len(preexisting) == 616
    packages = {}
    for name, (count, digest) in PACKAGES.items():
        root = EVIDENCE / name
        files = {str(p.relative_to(root)): identity(p) for p in sorted(root.rglob('*')) if p.is_file()}
        assert len(files) == count and sha(root / 'artifact_sha256.json') == digest
        manifest = json.loads((root / 'artifact_sha256.json').read_bytes())
        assert set(files) == set(manifest['files']) | {'artifact_sha256.json'}
        for rel, ref in manifest['files'].items():
            assert files[rel]['sha256'] == ref['sha256']
            assert files[rel]['size_bytes'] == ref['size_bytes']
        assert not any(p.is_symlink() for p in root.rglob('*'))
        packages[name] = {'manifest_sha256': digest, 'count': count, 'files': files,
                          'status': 'PASS_EXACT_PATH_SIZE_SHA_REPLAY'}
    output = Path('/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1')
    print('Hashing complete persistent output', flush=True)
    snapshot = {'tracked': {p: identity(ROOT / p) for p in tracked},
                'index': identity(ROOT / '.git/index'), 'preexisting_untracked': preexisting,
                'packages': packages, 'persistent_root': str(output), 'persistent_tree': tree(output)}
    current = json.loads((ROOT / 'evaluation/downstream_benchmark/v6_current_state.json').read_bytes())
    canonical = identity(ROOT / 'evaluation/downstream_benchmark/v6_current_state.json')
    assert canonical['sha256'] == 'e48580c1f9769d1b93ab995e6dcef3689c6920a9ce7b83f728526e9694dc68fd'
    assert current['event_count'] == 3 and current['projection']['state'] == 'PREPARATION_EXECUTION_AUTHORIZED'
    assert not list((output / 'ledger/claims').iterdir())
    assert not list((output / 'ledger/terminals').iterdir())
    assert not list((output / 'ledger/locks').iterdir())
    targets = json.loads((CAND / 'preservation_verification.json').read_bytes())['production_targets_absent']
    assert all(not (ROOT / p).exists() for p in targets)
    write('entry_snapshot.json', snapshot)
    write('exact_candidate_inventory.json', packages)
    write('entry_verification.json', {'status': 'PASS', 'head': EXPECTED_HEAD,
          'live_origin_main': EXPECTED_HEAD, 'live_origin_verification': 'git ls-remote origin refs/heads/main; read-only escalation exit 0',
          'initial_sandbox_network_result': 'exit 128: DNS unavailable; successful escalated read followed',
          'tracked': 1065, 'preexisting_untracked': 616, 'canonical': canonical,
          'state': current['projection']['state'], 'event_count': 3, 'event_head': current['event_head'],
          'real_ledger': {'UNSTARTED': 641, 'claims': 0, 'terminals': 0, 'retries': 0, 'orphans': 0},
          'production_targets_absent': targets, 'airos_current_state_present': (ROOT / '.airos/current_state.md').exists(),
          'persistent_output_scope': 'All entries including qualification, file SHA256, path, type and mode',
          'persistent_entry_count': len(snapshot['persistent_tree']),
          'audit_scope': 'INDEPENDENT_EXACT_CANDIDATE_AUDIT_ONLY', 'real_client_authorization': 'BLOCKED'})
    print('PASS entry and complete inventories', flush=True)

if __name__ == '__main__':
    main()

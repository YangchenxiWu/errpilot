"""Capture and verify an ENTRY BLOCK only; this never qualifies remediation.

Only the new evidence namespace is writable. No predecessor candidate is
imported or executed, and no ledger, qualification fixture or runtime is written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/Users/wuyangchenxi/errpilot')
HERE = ROOT / ('evaluation/downstream_benchmark/evidence/'
               'v6_production_runtime_topology_stability_successor_remediation_v1')
EVIDENCE = HERE.parent
OUTPUT = Path('/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1')
QUALIFICATION = OUTPUT / ('qualification/'
                          'production_runtime_topology_stability_successor_remediation_v1')
REQUEST = Path('/Users/wuyangchenxi/.codex/attachments/'
               '1d320043-1a13-4811-bb3d-2cd46486913e/已粘贴的文本.txt')
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
    require(not path.is_symlink(), f'symlink refused: {path}')
    value = {'mode': stat.S_IMODE(st.st_mode)}
    if stat.S_ISDIR(st.st_mode):
        return {**value, 'type': 'directory'}
    require(stat.S_ISREG(st.st_mode), f'special file refused: {path}')
    raw = path.read_bytes()
    return {**value, 'type': 'file', 'size_bytes': len(raw), 'sha256': digest(raw)}


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
    require(not QUALIFICATION.exists() and not QUALIFICATION.is_symlink(),
            'new qualification child occupied')
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


def capture():
    snapshot = inspect()
    require(snapshot['standard_untracked_count'] == 947
            and len(snapshot['ignored_expected_paths']) == 8
            and snapshot['expected_physical_evidence_count'] == 955
            and snapshot['standard_untracked_outside_expected'] == [],
            'different entry condition; do not construct this BLOCK automatically')
    live = read_json(HERE / 'live_origin_entry.json')
    require(live['returncode'] == 0 and live['stdout'].split() == [HEAD, 'refs/heads/main'],
            'live remote unavailable or wrong')
    raw = REQUEST.read_bytes()
    write('raw_human_pi_request.txt', raw)
    write('human_pi_decision.json', {
        'schema': 'V6_SUCCESSOR_REMEDIATION_HUMAN_PI_DECISION_V1',
        'authority': 'HUMAN_PI_ADJUDICATE_V6_PRODUCTION_RUNTIME_TOPOLOGY_STABILITY_SUCCESSOR_AUDIT_FINDINGS',
        'decision': 'ACCEPT_INDEPENDENT_AUDIT_FINDINGS_FOR_BOUNDED_REMEDIATION',
        'authorization': 'BOUNDED_VERSIONED_SUCCESSOR_REMEDIATION_AND_REQUALIFICATION_ONLY',
        'transaction_type': 'CANDIDATE_REMEDIATION_ONLY', 'request_sha256': digest(raw),
        'request_source': str(REQUEST), 'entry_gate_satisfied': False,
        'candidate_only': True, 'HUMAN_PI_ACCEPTED': 'NO', 'runtime_effective': 'NO',
        'execute_now': False, 'production_installation_authorized': False,
        'current_real_attempt_authorized': False})
    write('entry_snapshot.json', snapshot)
    write('predecessor_integrity.json', {
        'status': 'PASS_EXACT_955_PHYSICAL_FILES', 'packages': snapshot['packages'],
        'file_count': 955, 'payload_count_excluding_five_manifests': 950,
        'individual_size_sha_verified': True, 'all_manifest_self_sha_measured': True,
        'tracked_or_symlinked_predecessor_files': 0,
        'standard_untracked_files': 947, 'ignored_untracked_evidence_files': 8,
        'ignored_paths': snapshot['ignored_expected_paths'],
        'integrity_pass_does_not_waive_entry_population_gate': True})
    write('entry_verification.json', {
        'schema': 'V6_SUCCESSOR_REMEDIATION_ENTRY_V1', 'status': 'BLOCKED',
        'block_code': 'ENTRY_UNTRACKED_POPULATION_GATE_UNRESOLVED',
        'required_standard_untracked_count': 955, 'observed_standard_untracked_count': 947,
        'request_does_not_define_ignore_handling': True,
        'physical_predecessor_count': 955, 'physical_integrity': 'PASS',
        'ignored_evidence_count': 8, 'ignored_evidence_paths': snapshot['ignored_expected_paths'],
        'ignore_rules': snapshot['ignore_rules'],
        'all_untracked_including_ignored_count': snapshot['all_untracked_including_ignored_count'],
        'standard_untracked_outside_five_namespaces': [],
        'explanation': 'The exact five physical evidence populations match. The request '
                       'requires exact entry untracked population 955 without defining '
                       'ignore handling. The inherited gate uses git ls-files --others '
                       '--exclude-standard; its actual result is 947. Eight sealed audit '
                       'logs are ignored by unchanged .gitignore:26:*.log. Neither '
                       'silently changing the gate nor editing ignore rules is authorized.',
        'entry_gate_semantics_reference': str(EVIDENCE / AUDIT / 'audit_entry.py'),
        'required_human_adjudication': 'Explicitly define the admissible entry population '
                                      'as 955 physical untracked evidence files including '
                                      'eight ignored logs, with 947 standard Git-visible '
                                      'untracked files, or provide another exact gate. '
                                      'Do not edit/stage/delete any predecessor to reconcile it.',
        'local_HEAD': HEAD, 'live_origin_main': HEAD, 'branch': 'main',
        'live_origin_observed_utc': live['observed_at_utc'],
        'canonical_sha256': CANONICAL_SHA, 'state': snapshot['state'],
        'event_count': 3, 'event_3_id': EVENT_ID,
        'tracked_exact': 1065, 'index_exact': True,
        'real_ledger': snapshot['real_ledger'], 'production_installed': 'NO',
        'production_effectivity': 'NO', 'real_client_authorization': 'BLOCKED',
        'historical_exec_origin': 'ORIGIN_NOT_ESTABLISHED',
        'new_qualification_child_absent': True, 'remediation_started': False,
        'no_candidate_or_plan_constructed': True})
    findings = read_json(EVIDENCE / AUDIT / 'findings.json')
    write('audit_finding_dispositions.json', {
        'status': 'BLOCKED_BEFORE_REMEDIATION',
        'audit_findings_identity': identity(EVIDENCE / AUDIT / 'findings.json'),
        'findings': [{'id': f['id'], 'severity': f['severity'], 'title': f['title'],
                      'disposition': 'NOT_STARTED_ENTRY_GATE_BLOCKED',
                      'failure_mechanism_uniquely_reviewed_in_this_run': False,
                      'fix_constructed': False, 'regression_executed': False}
                     for f in findings['findings']],
        'old_candidates_accepted_or_modified': False})
    print('BLOCKED: 947 standard untracked; 955 exact physical predecessor files; 8 ignored logs')


def preservation():
    before = read_json(HERE / 'entry_snapshot.json')
    after = inspect()
    require(after == before, 'entry-preserved sources/files/ledger changed')
    return {'schema': 'V6_SUCCESSOR_REMEDIATION_BLOCK_PRESERVATION_V1',
            'status': 'PASS_BOUNDED_BLOCK_PRESERVATION', 'tracked_files_exact': 1065,
            'predecessor_files_exact': 955, 'five_manifests_exact': True,
            'index_bytes_modes_exact': True, 'HEAD': HEAD, 'canonical_sha256': CANONICAL_SHA,
            'event_count': 3, 'event_3_id': EVENT_ID,
            'real_output_ledger_tree_exact': True, 'real_ledger': before['real_ledger'],
            'qualification_child_created': False,
            'historical_qualification_tree_independently_rehashed': False,
            'Docker_operations': 0, 'Docker_topology_independently_certified': False,
            'Docker_preservation_basis': 'No Docker operation or runtime/config mutation by agent',
            'production_targets_absent': before['production_targets_absent'],
            'only_new_repo_write_namespace': str(HERE), 'staging_commits_pushes': 0}


def seal():
    require(read_json(HERE / 'ruff_results.json')['returncode'] == 0, 'Ruff failed')
    write('preservation_verification.json', preservation())
    write('validation_results.json', {
        'status': 'BLOCKED', 'evidence_validation_status': 'PASS_BOUNDED_BLOCK_EVIDENCE',
        'mandatory_entry_gate': 'BLOCKED_UNRESOLVED_955_VS_947_IGNORE_SEMANTICS',
        'passed': ['955 predecessor file sizes/SHA and exact populations',
                   'five exact manifest self SHA256', 'four controlling predecessor identities',
                   '1065 tracked file size/SHA/mode and exact index',
                   'local HEAD, cached origin/main and live origin entry identity',
                   'canonical and three event file identities',
                   '641 exact population identity and unchanged empty real ledger',
                   'production targets absent', 'Ruff --no-cache'],
        'not_run_due_to_entry_block': ['F01/F02/F03 remediation and new source AST/text deltas',
                                    'V2 contract preservation/versioning qualification',
                                    'root/socket/authority regressions',
                                    'receipt/association revalidation',
                                    '10 crash boundaries and 4 partial-write categories',
                                    'hermetic E2E and inherited 126 rejection categories',
                                    '641 scientific/native Dockerfile/command projection replay',
                                    'new candidate/plan construction and supersession DAG'],
        'scientific_validation_claimed': False, 'physical_power_loss_durability_established': False,
        'source_level_fault_injection_executed': False, 'no_mandatory_qualification_skip_on_PASS':
            'No qualification PASS asserted; this is an early BLOCK',
        'runtime_effective': 'NO', 'REAL_CLIENT_AUTHORIZATION': 'BLOCKED',
        'next_gate': 'HUMAN_PI_ADJUDICATE_V6_SUCCESSOR_REMEDIATION_ENTRY_POPULATION'})
    files = {str(p.relative_to(HERE)): identity(p)
             for p in sorted(HERE.rglob('*')) if p.is_file()}
    require('artifact_sha256.json' not in files, 'manifest already exists')
    for rel in files:
        raw = (HERE / rel).read_bytes()
        raw.decode('utf-8')
        require(b'\r' not in raw and raw.endswith(b'\n'), f'UTF-8/LF check: {rel}')
        if rel.endswith('.json'):
            read_json(HERE / rel)
    write('artifact_sha256.json', {
        'schema': 'V6_SUCCESSOR_REMEDIATION_ENTRY_BLOCK_ARTIFACT_SHA256_V1',
        'status': 'BLOCKED', 'candidate_only': True, 'HUMAN_PI_ACCEPTED': 'NO',
        'runtime_effective': 'NO', 'execute_now': False, 'files': files,
        'payload_count': len(files), 'total_file_count': len(files) + 1,
        'excluded': ['artifact_sha256.json'],
        'self_sha256_semantics': 'Exact manifest byte SHA256 measured separately at verification; '
                                 'no self-reference and no external acceptance authority'})
    verify()


def verify():
    require(preservation()['status'] == 'PASS_BOUNDED_BLOCK_PRESERVATION', 'preservation')
    manifest = read_json(HERE / 'artifact_sha256.json')
    files = {str(p.relative_to(HERE)): identity(p)
             for p in sorted(HERE.rglob('*')) if p.is_file()}
    require(set(files) == set(manifest['files']) | {'artifact_sha256.json'}, 'new inventory drift')
    require(len(files) == manifest['total_file_count'], 'new manifest count')
    for rel, ref in manifest['files'].items():
        require(files[rel] == ref, f'new manifest size/SHA/mode: {rel}')
        raw = (HERE / rel).read_bytes()
        raw.decode('utf-8')
        require(b'\r' not in raw and raw.endswith(b'\n'), f'UTF-8/LF: {rel}')
        if rel.endswith('.json'):
            read_json(HERE / rel)
    require(read_json(HERE / 'entry_verification.json')['status'] == 'BLOCKED', 'entry status')
    require(read_json(HERE / 'validation_results.json')['status'] == 'BLOCKED', 'overall status')
    print(json.dumps({'status': 'BLOCKED', 'bounded_block_evidence_seal': 'PASS',
                      'total_files': len(files), 'payload_files': manifest['payload_count'],
                      'manifest_self_sha256': files['artifact_sha256.json']['sha256'],
                      'remediation_requalification_executed': False}, sort_keys=True))


def main():
    require(Path(__file__).absolute() == HERE / 'validate_remediation.py', 'wrong evidence source path')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['capture-entry-block', 'seal-entry-block', 'verify-seal'])
    args = parser.parse_args()
    print('Observation UTC:', datetime.now(timezone.utc).isoformat())
    {'capture-entry-block': capture, 'seal-entry-block': seal, 'verify-seal': verify}[args.mode]()


if __name__ == '__main__':
    main()

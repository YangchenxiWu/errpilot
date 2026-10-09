"""Bounded evidence authoring only. Never import or execute runtime candidates.

prepare: remeasure authenticated predecessors and construct draft records/seal.
finalize: consume an actual separate draft readback, remeasure preservation,
and seal final records. Final verification is a separate read-only process.
"""
import collections
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

R = Path('/Users/wuyangchenxi/errpilot')
HERE = Path(__file__).resolve().parent
E = R / 'evaluation/downstream_benchmark/evidence'
C = E / 'v6_production_runtime_topology_stability_successor_remediation_final_resume_v1'
A = E / 'v6_production_runtime_topology_stability_successor_remediation_independent_reaudit_v1'
T = E / 'v6_production_runtime_threat_model_adjudication_v1'
OUT = Path('/Users/wuyangchenxi/errpilot-benchmark-work/v6_preparation_execution_v1')
ATTACHMENT = Path('/Users/wuyangchenxi/.codex/attachments/780ffd42-d81b-4061-8530-41c990b22a3e/已粘贴的文本.txt')
HEAD = 'e492d159daf188323efcfe121aa019d5b098bfb2'
CANON = 'e48580c1f9769d1b93ab995e6dcef3689c6920a9ce7b83f728526e9694dc68fd'
PINS = {
    'production_controller_remediated_candidate.py': '7c097da628d521987dee76dba8689b0dcdd45d286996ce7509c8442bf8f82b10',
    'production_provider_remediated_candidate.py': '51f842194fd79bb9519bb6f45281a897c5249bb80558750f4660233c4c0bd438',
    'remediated_installation_candidate.json': '6f42c9740dea963fb49df7459e7d34c13b8774530c20cf26dd3a9fe7395edb01',
    'remediated_installation_plan.json': '43fc8823c8c59db7638b873762fde5f47e84aaab140e218a45b259694bfe355e',
}
MANIFESTS = {
    C.name: (764, '15161f72e034f4661baa6f2a42dfa649adab4ab33edbb899c3b10d2e3a5a7d15'),
    A.name: (38, '45c5eafbddb0cebf27b88dbfa86be1085b7f46c76f8d9d5760e53e7dd841f8f8'),
    T.name: (24, 'fd714b537b34bf693740a6b34971db4eec65aea02dcc21a8c383b6ba27c7e225'),
}
READY = 'V6_REMEDIATED_SUCCESSOR_NON_EFFECTIVE_FREEZE_CLOSURE_READY_FOR_COMMIT'
NEXT = 'HUMAN_PI_AUTHORIZE_EXACT_FREEZE_COMMIT_AND_PUBLISH'
AUTH = 'HUMAN_PI_ACCEPT_V6_REMEDIATED_SUCCESSOR_UNDER_ADOPTED_THREAT_MODEL'
DECISION = 'ACCEPT_EXACT_REMEDIATED_SUCCESSOR_FOR_NON_EFFECTIVE_FREEZE'
BOUNDARY = {
    'HUMAN_PI_ACCEPTANCE': 'YES', 'SOURCE_PAIR_ACCEPTED': 'YES',
    'CONTRACT_BASELINE_ACCEPTED': 'YES',
    'ACCEPTED_THREAT_MODEL': 'CONTROLLED_SINGLE_TRUSTED_OPERATOR',
    'FREEZE_SCOPE': 'NON_EFFECTIVE_SOURCE_AND_CONTRACT_BASELINE',
    'PRODUCTION_RUNTIME_INSTALLED': 'NO', 'RUNTIME_EFFECTIVE': 'NO',
    'REAL_CLIENT_AUTHORIZATION': 'BLOCKED', 'REAL_PREPARATION_AUTHORIZED': 'NO',
    'execute_now': False,
}
CHECKS = ['ACCEPTANCE_AUTHORITY_EXACT', 'ALL_PREDECESSOR_IDENTITIES',
          'SOURCE_AND_CONTRACT_PINS', 'R01_R02_DISPOSITIONS', 'NON_EFFECTIVE_BOUNDARY',
          'REAL_LEDGER_PRESERVATION', 'CANONICAL_EVENT_PRESERVATION',
          'SOURCE_FREEZE_CLOSURE', 'EXACT_EVIDENCE_SEAL']
R01_SCENARIO = ('Deliberate adversarial same-UID concurrent directory relocation '
                'between successful confinement validation and filesystem operations.')
COMMANDS = []


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def pairs(items):
    d = {}
    for k, v in items:
        assert k not in d, ('duplicate key', k)
        d[k] = v
    return d


def read(p):
    def bad(v):
        raise ValueError(v)
    return json.loads(Path(p).read_bytes().decode('utf-8'), object_pairs_hook=pairs,
                      parse_constant=bad)


def identity(p):
    p = Path(p)
    s = p.lstat()
    d = {'mode': stat.S_IMODE(s.st_mode)}
    if stat.S_ISLNK(s.st_mode):
        return dict(d, type='symlink', target=os.readlink(p))
    if stat.S_ISDIR(s.st_mode):
        return dict(d, type='directory')
    assert stat.S_ISREG(s.st_mode), str(p)
    with os.fdopen(os.open(p, os.O_RDONLY | os.O_NOFOLLOW), 'rb') as f:
        h = hashlib.file_digest(f, 'sha256').hexdigest()
    return dict(d, type='file', size_bytes=s.st_size, sha256=h)


def ref(p):
    return dict(identity(p), path=str(p))


def tree(p):
    result = {'.': identity(p)}
    def visit(parent):
        for e in sorted(os.scandir(parent), key=lambda e: e.name):
            child = Path(e.path)
            row = identity(child)
            result[str(child.relative_to(p))] = row
            if row['type'] == 'directory':
                visit(child)
    visit(p)
    return result


def save(name, d, replace=False):
    p = HERE / name
    assert p.parent == HERE and not p.is_symlink()
    raw = json.dumps(d, sort_keys=True, ensure_ascii=False, indent=2,
                     allow_nan=False) + '\n'
    with p.open('w' if replace else 'x', encoding='utf-8', newline='\n') as f:
        f.write(raw)


def git(*args):
    p = subprocess.run(['git', *args], cwd=R, capture_output=True,
                       env={**os.environ, 'GIT_OPTIONAL_LOCKS': '0'}, check=False)
    COMMANDS.append({'argv': ['git', *args], 'exit_code': p.returncode,
                     'stdout_sha256': digest(p.stdout),
                     'stderr': p.stderr.decode('utf-8')})
    assert p.returncode == 0, COMMANDS[-1]
    return p.stdout.decode('utf-8')


def specs():
    for name, (count, pin) in MANIFESTS.items():
        assert identity(E / name / 'artifact_sha256.json')['sha256'] == pin
    inv = read(C / 'predecessor_inventory.json')
    expected = read(C / 'artifact_sha256.json')['files']['predecessor_inventory.json']
    assert identity(C / 'predecessor_inventory.json')['sha256'] == expected['sha256']
    assert inv['count'] == 1016 and len(inv['packages']) == 7
    return dict(MANIFESTS, **{n: (v['count'], v['manifest_self_sha256_measured'])
                             for n, v in inv['packages'].items()})


def snapshot():
    names = [n for n in git('ls-files', '-z').split('\0') if n]
    return {
        'head': git('rev-parse', 'HEAD').strip(),
        'branch': git('branch', '--show-current').strip(),
        'cached_origin_main': git('rev-parse', 'refs/remotes/origin/main').strip(),
        'tracked_diff': git('diff', '--no-ext-diff', '--binary', 'HEAD'),
        'staged_diff': git('diff', '--no-ext-diff', '--cached', '--binary'),
        'tracked': {n: identity(R / n) for n in names},
        'index': identity(R / git('rev-parse', '--git-path', 'index').strip()),
        'git_HEAD_file': identity(R / git('rev-parse', '--git-path', 'HEAD').strip()),
        'packages': {n: tree(E / n) for n in specs()},
        'persistent_tree': tree(OUT),
        'untracked_outside_write_set': sorted(
            n for n in git('ls-files', '--others', '--exclude-standard', '-z').split('\0')
            if n and not n.startswith(str(HERE.relative_to(R)) + '/')),
    }


def seals(snap):
    out = {}
    for name, (count, pin) in specs().items():
        tr = snap['packages'][name]
        files = {k: v for k, v in tr.items() if v['type'] == 'file'}
        manifest = read(E / name / 'artifact_sha256.json')
        assert len(files) == count and files['artifact_sha256.json']['sha256'] == pin
        assert set(files) == set(manifest['files']) | {'artifact_sha256.json'}
        assert not any(v['type'] == 'symlink' for v in tr.values())
        for n, row in manifest['files'].items():
            assert not Path(n).is_absolute() and all(x not in {'', '.', '..'} for x in n.split('/'))
            assert {'size_bytes', 'sha256'} <= row.keys()
            for k in ('size_bytes', 'sha256', 'type', 'mode'):
                if k in row:
                    assert files[n][k] == row[k], (name, n, k)
        out[name] = {'status': 'PASS', 'physical_file_count': count,
                     'manifest': ref(E / name / 'artifact_sha256.json'),
                     'complete_path_set_verified': True, 'files': files}
    assert sum(v['physical_file_count'] for v in out.values()) == 1842
    return out


def reference_count(value):
    count = 0
    if isinstance(value, dict):
        if isinstance(value.get('path'), str) and isinstance(value.get('sha256'), str):
            p = Path(value['path'])
            p = p if p.is_absolute() else R / p
            row = identity(p)
            assert row['type'] == 'file' and row['sha256'] == value['sha256'], str(p)
            if 'size_bytes' in value:
                assert row['size_bytes'] == value['size_bytes'], str(p)
            count += 1
        count += sum(reference_count(v) for v in value.values())
    elif isinstance(value, list):
        count += sum(reference_count(v) for v in value)
    return count


def baseline_check(snap):
    old = read(T / 'entry_snapshot.json')
    for field in ('tracked', 'index', 'persistent_tree'):
        assert snap[field] == old[field], ('FROZEN_BASELINE_DRIFT', field)
    assert len(snap['tracked']) == 1065
    assert snap['head'] == snap['cached_origin_main'] == HEAD and snap['branch'] == 'main'
    assert snap['tracked_diff'] == snap['staged_diff'] == ''
    can_path = R / 'evaluation/downstream_benchmark/v6_current_state.json'
    can = read(can_path)
    assert identity(can_path)['sha256'] == CANON
    assert can['projection']['state'] == 'PREPARATION_EXECUTION_AUTHORIZED'
    assert can['event_count'] == len(can['event_chain']) == 3
    for event in can['event_chain']:
        assert identity(R / event['path'])['sha256'] == event['sha256']
    for name, pin in PINS.items():
        assert identity(C / name)['sha256'] == pin
    for name in ('remediated_installation_candidate.json', 'remediated_installation_plan.json'):
        d = read(C / name)
        assert d['candidate_only'] is True and d['HUMAN_PI_ACCEPTED'] == 'NO'
        assert d['execute_now'] is False and d['runtime_effective'] == 'NO'
        assert d['current_production_installation_authorized'] is False
        assert d['current_real_attempt_authorized'] is False
    assert set(os.listdir(OUT / 'ledger')) == {'claims', 'terminals', 'locks'}
    assert all(not os.listdir(OUT / 'ledger' / k) for k in ('claims', 'terminals', 'locks'))
    work = read(R / 'evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/work_items_candidate.json')
    assert len(work['items']) == 641
    targets = read(T / 'entry_verification.json')['production_targets_absent']
    assert all(not os.path.lexists(R / p) for p in targets)
    inv = read(C / 'synthetic_output_inventory.json')
    actual = tree(Path(inv['root']))
    actual.pop('.')
    assert actual == inv['files']
    assert read(T / 'independent_scoped_disposition.json')['CURRENT_SCOPED_ADJUDICATION'] == 'PASS'
    assert read(A / 'artifact_sha256.json')['status'] == 'V6_SUCCESSOR_REMEDIATION_INDEPENDENT_REAUDIT_BLOCKED'
    return can, targets, len(actual)


def authority_check():
    text = ATTACHMENT.read_text()
    for phrase in (AUTH, DECISION, 'HUMAN_PI_ACCEPTANCE = YES',
                   'CONSTRUCT_AND_VERIFY_EXACT_NON_EFFECTIVE_ACCEPTANCE_FREEZE_CLOSURE',
                   HEAD, CANON, *PINS.values(), *(v[1] for v in MANIFESTS.values()),
                   'NO Git stage/commit/push.', 'run_4/fixture_76'):
        assert phrase in text, ('AUTHORITY_MISMATCH', phrase)


def preservation(snap, targets, qualification_count):
    entry = read(HERE / 'entry_snapshot.json')
    assert snap == entry, 'PRESERVATION_DRIFT'
    return {
        'schema': 'V6_NON_EFFECTIVE_FREEZE_PRESERVATION_V1', 'status': 'PASS',
        'entry_snapshot': ref(HERE / 'entry_snapshot.json'),
        'authenticated_historical_snapshot': ref(T / 'entry_snapshot.json'),
        'all_snapshot_fields_equal': True, 'tracked_files_preserved': 1065,
        'index': snap['index'], 'HEAD': snap['head'], 'branch': snap['branch'],
        'canonical_sha256': CANON, 'event_count': 3,
        'persistent_root': str(OUT), 'persistent_entries': len(snap['persistent_tree']),
        'persistent_files': sum(v['type'] == 'file' for v in snap['persistent_tree'].values()),
        'persistent_tree_unchanged': True, 'qualification_entries': qualification_count,
        'qualification_inventory': ref(C / 'synthetic_output_inventory.json'),
        'qualification_tree_unchanged': True,
        'real_ledger': {'UNSTARTED': 641, 'claims': 0, 'terminals': 0,
                        'locks': 0, 'retries': 0, 'orphans': 0},
        'ledger_method': 'Read-only full tree comparison and empty claim/terminal/lock namespaces; no ledger constructor or candidate imports.',
        'production_targets_absent': targets, 'writes_outside_closure': 0,
        'Git_stage_commit_push': False, 'Docker_operations': 0,
        'runtime_tests_executed': 0, 'scientific_validation_claimed': False,
    }


def seal(phase):
    files = {}
    for p in sorted(HERE.iterdir()):
        assert p.is_file() and not p.is_symlink(), p.name
        if p.name == 'artifact_sha256.json':
            continue
        raw = p.read_bytes()
        raw.decode('utf-8')
        assert b'\r' not in raw and raw.endswith(b'\n'), p.name
        if p.suffix == '.json':
            read(p)
        files[p.name] = identity(p)
    save('artifact_sha256.json', {
        'schema': 'V6_NON_EFFECTIVE_ACCEPTANCE_FREEZE_SEAL_V1', 'phase': phase,
        **BOUNDARY, 'files': files, 'payload_count': len(files),
        'total_file_count': len(files) + 1, 'excluded': ['artifact_sha256.json'],
        'self_sha256_semantics': 'Exact independent file-byte SHA-256 emitted by separate final readback; no circular self-reference.',
        'freeze_preserves_all_predecessor_bytes': True,
    }, replace=(HERE / 'artifact_sha256.json').exists())
    m = read(HERE / 'artifact_sha256.json')
    assert set(p.name for p in HERE.iterdir()) == set(m['files']) | {'artifact_sha256.json'}
    assert all(identity(HERE / n) == d for n, d in m['files'].items())
    return ref(HERE / 'artifact_sha256.json')


def report(final=False):
    p = HERE / 'RUN_REPORT.md'
    text = f'''# Run Report: exact non-effective acceptance and freeze closure

## 1. Task summary

Human PI directly approved `{AUTH}` with decision `{DECISION}`.
The new versioned records accept only the exact existing source/contract baseline
under `CONTROLLED_SINGLE_TRUSTED_OPERATOR`. Source/contract freeze is persisted;
runtime installation and execution effectivity remain NO.

STATUS = {READY if final else 'DRAFT_SEALED_AWAITING_SEPARATE_READBACK'}
NEXT_GATE = {NEXT}

## 2. Files changed

Only new files in `{HERE.relative_to(R)}/`.
Required outputs: human_pi_acceptance_decision.json, accepted_source_and_contract_pins.json,
accepted_threat_model_binding.json, historical_findings_disposition.json,
non_effective_freeze_record.json, lifecycle_closure.json, predecessor_integrity.json,
preservation_verification.json, closure_validation.json, commands_run.json,
RUN_REPORT.md and artifact_sha256.json.
Additional bounded evidence: raw_user_request.txt, entry_snapshot.json,
entry_verification.json, construct_closure.py, verify_closure.py{', draft_readback_verification.json and live_origin_exit.json' if final else ''}.
Historical sealed candidate files retain their original candidate_only,
HUMAN_PI_ACCEPTED=NO and execute_now=false snapshots. This subsequent acceptance
record never rewrites or transfers authority to historical snapshots.

Accepted controller SHA-256: `{PINS['production_controller_remediated_candidate.py']}`.
Accepted provider SHA-256: `{PINS['production_provider_remediated_candidate.py']}`.
Installation candidate SHA-256: `{PINS['remediated_installation_candidate.json']}`.
Installation plan SHA-256: `{PINS['remediated_installation_plan.json']}`.
All eight runtime contract identities, capacity contract, threat-model contract,
helper and baseline dependencies are pinned in accepted_source_and_contract_pins.json.
No executable plan was created; the preexisting plan bytes were preserved.

## 3. Commands run

Read-only git status, branch/HEAD, git ls-files, git diff, git check-ignore,
fresh live git ls-remote and Python byte/tree/graph measurements.
Then `python3 -B construct_closure.py prepare`, separate
`python3 -B verify_closure.py --draft`{', and `python3 -B construct_closure.py finalize`' if final else ' (mandatory next construction check)'}.
commands_run.json preserves command receipts and exploratory failures.
The final mandatory command is `python3 -B verify_closure.py`: its exact result,
final seal SHA and file count are emitted after sealing, outside the sealed payload
to avoid self-referential evidence. Final user-facing readiness requires its exit 0.

## 4. Tests passed/failed

Entry and preservation: PASS for 1842 physical evidence files (1016 historical,
764 remediated candidate, 38 independent reaudit, 24 threat-model adjudication),
complete manifest path sets/sizes/SHA values, including all 8 ignored .log files.
1065 tracked files and the Git index match the authenticated sealed baseline.
The full external persistent tree (12271 entries / 7510 files), all retained
qualification outputs and canonical state/events are preserved.
Real ledger: 641 UNSTARTED; claims/terminals/locks/retries/orphans all zero.
786 original candidate/plan/version/dependency references were remeasured.
{'Separate draft readback: PASS (actual receipt in draft_readback_verification.json). All nine final checks are required again by the final sealed verifier.' if final else 'Separate draft and final sealed readback are mandatory completion gates.'}
No new runtime validation, 188 rejection rerun, 641 projection rerun or full E2E
was performed. This evidence packaging does not establish scientific validation.

## 5. Contract compliance

The latest attached Human-PI request is copied byte-for-byte in raw_user_request.txt.
No .airos/current_state.md or separate .airos/contracts/ was present.
Only the exact authorized acceptance closure was constructed. No source edits,
runtime refactoring, security scope expansion, Docker investigation, protocol
changes, production installation, real client authorization, real preparation,
Git staging/commit/push or runtime activation occurred.

## 6. Risks and unknowns

F01 original lexical traversal vulnerability: FIXED, based on preserved scoped evidence.
F02: ACCEPTED_CORRECTED_ENDPOINT_CORRELATION.
F03: ACCEPTED_CORRECTED_BOOLEAN_TYPE_SEMANTICS.
R01: KNOWN_OUT_OF_SCOPE_RESIDUAL_RISK. Precisely excluded: {R01_SCENARIO}
The code is not claimed to prevent that behavior. Ordinary path confinement,
symlink and source-location guards remain in scope and byte-preserved.
R02: ACCEPTED_ADDITIVE_ERRATUM; correct fixture locator `run_4/fixture_76`.
No historical evidence or outcome was rewritten. Historical independent audit
remains BLOCKED; current scoped adjudication remains PASS.
Physical power-loss durability: NOT_ESTABLISHED. Current live production
preconditions were not investigated or established in this closure.

## 7. Recommended next action

Human PI may review the exact final seal and separately authorize
`{NEXT}`. This is the next gate, not granted commit/publication authority.
STOP. PRODUCTION_RUNTIME_INSTALLED=NO; RUNTIME_EFFECTIVE=NO;
REAL_CLIENT_AUTHORIZATION=BLOCKED; REAL_PREPARATION_AUTHORIZED=NO.
'''
    with p.open('w' if p.exists() else 'x', encoding='utf-8', newline='\n') as f:
        f.write(text)


def prepare():
    assert not (HERE / 'human_pi_acceptance_decision.json').exists()
    authority_check()
    snap = snapshot()
    integrity = seals(snap)
    can, targets, qualification_count = baseline_check(snap)
    candidate = read(C / 'remediated_installation_candidate.json')
    count = sum(reference_count(read(C / n)) for n in (
        'remediated_installation_candidate.json', 'remediated_installation_plan.json',
        'supersession_dependency_graph.json', 'contract_version_disposition.json'))
    assert count == 786
    raw = ATTACHMENT.read_bytes()
    with (HERE / 'raw_user_request.txt').open('xb') as f:
        f.write(raw)
    save('entry_snapshot.json', snap)
    package_paths = sorted(str((E / n / p).relative_to(R)) for n, v in integrity.items() for p in v['files'])
    ip = subprocess.run(['git', 'check-ignore', '--stdin'], cwd=R,
                        input=('\n'.join(package_paths) + '\n').encode(), capture_output=True)
    assert ip.returncode in (0, 1)
    ignored = ip.stdout.decode().splitlines()
    assert len(ignored) == 8 and all(p.endswith('.log') for p in ignored)
    COMMANDS.append({'argv': ['git', 'check-ignore', '--stdin'], 'input_count': 1842,
                     'exit_code': ip.returncode, 'stdout': ignored})
    save('entry_verification.json', {
        'status': 'PASS', 'local_date': '2026-10-08', 'timezone': 'Europe/Budapest',
        'all_required_identities_verified_before_first_write': True,
        'prewrite_readonly_measurement_receipt': {'tool_chunk_id': '326753', 'exit_code': 0, 'status': 'ENTRY_PASS'},
        'fresh_live_origin_entry': {'argv': ['git', 'ls-remote', '--exit-code', 'origin', 'refs/heads/main'],
            'stdout': HEAD + '\trefs/heads/main\n', 'exit_code': 0, 'tool_chunk_id': 'e87df9',
            'basis': 'Actual fresh network tool result; cached tracking ref is separately measured.'},
        'canonical': ref(R / 'evaluation/downstream_benchmark/v6_current_state.json'),
        'state': can['projection']['state'], 'event_count': 3,
        'event_chain': can['event_chain'], 'exact_source_descriptor_pins': {n: ref(C / n) for n in PINS},
        'required_manifest_pins': {n: ref(E / n / 'artifact_sha256.json') for n in MANIFESTS},
        'ignored_evidence_paths': ignored, 'airos_current_state_present': False,
        'separate_airos_contracts_present': False,
        'existing_candidate_graph_reference_count': count,
    })
    save('predecessor_integrity.json', {
        'schema': 'V6_ACCEPTANCE_FREEZE_PREDECESSOR_INTEGRITY_V1', 'status': 'PASS',
        'total_physical_files': 1842, 'historical_predecessors': 1016,
        'remediated_candidate': 764, 'independent_reaudit': 38,
        'threat_model_adjudication': 24, 'packages': integrity,
        'ignored_files_included': ignored, 'followed_symlinks': False,
    })
    save('human_pi_acceptance_decision.json', {
        'schema': 'V6_REMEDIATED_SUCCESSOR_NON_EFFECTIVE_HUMAN_PI_ACCEPTANCE_V1',
        'record_version': 1, 'AUTHORITY': AUTH, 'DECISION': DECISION,
        'AUTHORIZATION': 'CONSTRUCT_AND_VERIFY_EXACT_NON_EFFECTIVE_ACCEPTANCE_FREEZE_CLOSURE',
        **BOUNDARY, 'authority_source': ref(HERE / 'raw_user_request.txt'),
        'human_instruction_origin': 'Direct user attachment in this chat; byte-preserved copy, not inferred from predecessor records.',
        'accepted_exact_source_and_installation_snapshots': {n: ref(C / n) for n in PINS},
        'candidate_manifest': ref(C / 'artifact_sha256.json'),
        'independent_reaudit_manifest': ref(A / 'artifact_sha256.json'),
        'threat_model_adjudication_manifest': ref(T / 'artifact_sha256.json'),
        'canonical': ref(R / 'evaluation/downstream_benchmark/v6_current_state.json'),
        'HEAD': HEAD, 'branch': 'main', 'event_count': 3,
        'authority_effect': 'Subsequent versioned acceptance for exact non-effective source and contract freeze only.',
        'historical_preacceptance_flags_rewritten': False,
        'production_installation_authorized': False, 'Git_commit_publish_authorized': False,
        'NEXT_GATE': NEXT,
    })
    decision = ref(HERE / 'human_pi_acceptance_decision.json')
    contracts = dict(candidate['security_contracts'])
    contracts['receipt_authority_contract_v2_candidate.json'] = candidate['receipt_contract']
    assert len(contracts) == 8
    save('accepted_source_and_contract_pins.json', {
        'schema': 'V6_ACCEPTED_EXACT_SOURCE_AND_CONTRACT_PINS_V1', **BOUNDARY,
        'acceptance_authority': decision, 'accepted_source_pair': candidate['source_pair'],
        'accepted_helper_sources': candidate['candidate_helpers'], 'accepted_runtime_contracts': contracts,
        'accepted_capacity_contract': ref(R / can['contract']['path']),
        'accepted_threat_model_contract': ref(T / 'threat_model_contract.json'),
        'installation_candidate_snapshot': ref(C / 'remediated_installation_candidate.json'),
        'installation_plan_snapshot': ref(C / 'remediated_installation_plan.json'),
        'contract_version_disposition': ref(C / 'contract_version_disposition.json'),
        'V2_contract_preservation': ref(C / 'v2_contract_preservation.json'),
        'historical_candidate_dependency_graph': ref(C / 'supersession_dependency_graph.json'),
        'future_receipt_schema_specification_snapshot': candidate['future_production_schema_specification'],
        'baseline_ledger_implementation': ref(R / candidate['ledger_binding_identity']['implementation_path']),
        'baseline_ledger_namespace': ref(OUT / 'namespace.json'),
        'historical_preacceptance_flags': {'candidate_only': True, 'HUMAN_PI_ACCEPTED': 'NO',
            'execute_now': False, 'runtime_effective': 'NO'},
        'source_bytes_copied_or_changed': False, 'executable_plan_created': False,
    })
    save('accepted_threat_model_binding.json', {
        'schema': 'V6_ACCEPTED_THREAT_MODEL_BINDING_V1', **BOUNDARY,
        'acceptance_authority': decision, 'adopted_threat_model_contract': ref(T / 'threat_model_contract.json'),
        'adoption_authority': ref(T / 'human_pi_threat_model_decision.json'),
        'scoped_adjudication': ref(T / 'independent_scoped_disposition.json'),
        'in_scope_assurance_review': ref(T / 'in_scope_security_assurance_review.json'),
        'precise_exclusion': R01_SCENARIO,
        'R01_disposition': 'KNOWN_OUT_OF_SCOPE_RESIDUAL_RISK',
        'adversarial_relocation_prevented_claimed': False,
        'ordinary_path_symlink_source_location_guards_retained': True,
        'arbitrary_same_UID_interference_excluded': False,
        'BuildKit_client_authorization_or_network_access_waived': False,
        'physical_power_loss_durability': 'NOT_ESTABLISHED',
        'new_security_scope_or_runtime_features': False,
    })
    save('historical_findings_disposition.json', {
        'schema': 'V6_ACCEPTED_HISTORICAL_FINDINGS_DISPOSITION_V1',
        'acceptance_authority': decision,
        'F01': {'disposition': 'FIXED', 'scope': 'Original lexical traversal vulnerability only',
                'evidence': ref(A / 'F01_root_confinement_reaudit.json')},
        'F02': {'disposition': 'ACCEPTED_CORRECTED_ENDPOINT_CORRELATION',
                'evidence': ref(A / 'F02_endpoint_correlation_reaudit.json')},
        'F03': {'disposition': 'ACCEPTED_CORRECTED_BOOLEAN_TYPE_SEMANTICS',
                'evidence': ref(A / 'F03_test_semantics_reaudit.json')},
        'R01': {'disposition': 'KNOWN_OUT_OF_SCOPE_RESIDUAL_RISK', 'precisely_excluded': R01_SCENARIO,
                'code_prevents_behavior_claimed': False, 'safety': 'NOT_ESTABLISHED',
                'risk_register': ref(T / 'R01_residual_risk_register.json'),
                'scope_adjudication': ref(T / 'R01_scope_adjudication.json')},
        'R02': {'disposition': 'ACCEPTED_ADDITIVE_ERRATUM', 'corrected_locator': 'run_4/fixture_76',
                'corrected_absolute_locator': read(T / 'R02_locator_erratum.json')['corrected_locator'],
                'erratum': ref(T / 'R02_locator_erratum.json'), 'historical_record_rewritten': False,
                'test_outcome_or_source_changed': False},
        'HISTORICAL_INDEPENDENT_AUDIT': 'BLOCKED',
        'historical_audit': ref(A / 'findings.json'),
        'CURRENT_SCOPED_ADJUDICATION': 'PASS',
        'scoped_adjudication': ref(T / 'independent_scoped_disposition.json'),
        'historical_audit_retroactively_passed': False,
        'physical_power_loss_durability': 'NOT_ESTABLISHED',
    })
    save('non_effective_freeze_record.json', {
        'schema': 'V6_NON_EFFECTIVE_SOURCE_AND_CONTRACT_FREEZE_V1', 'record_version': 1,
        **BOUNDARY, 'SOURCE_AND_CONTRACT_FROZEN': 'YES',
        'acceptance_authority': decision,
        'accepted_pins': ref(HERE / 'accepted_source_and_contract_pins.json'),
        'threat_model_binding': ref(HERE / 'accepted_threat_model_binding.json'),
        'findings_disposition': ref(HERE / 'historical_findings_disposition.json'),
        'predecessor_integrity': ref(HERE / 'predecessor_integrity.json'),
        'immutability': 'All predecessor bytes remain unchanged. Freeze is exact byte identities, not filesystem chmod or historical snapshot edits.',
        'candidate_manifest': ref(C / 'artifact_sha256.json'),
        'historical_flags_are_preacceptance_snapshots': True,
        'prior_installation_plan_amended': False, 'executable_plan_created': False,
        'canonical_transition_created': False, 'event_4_created': False,
        'installation_effectivity_created': False, 'STOP': True, 'NEXT_GATE': NEXT,
    })
    save('preservation_verification.json', preservation(snap, targets, qualification_count))
    nodes = {n: ref(HERE / (n + '.json')) for n in (
        'human_pi_acceptance_decision', 'accepted_source_and_contract_pins',
        'accepted_threat_model_binding', 'historical_findings_disposition',
        'non_effective_freeze_record', 'predecessor_integrity', 'preservation_verification',
        'entry_verification')}
    nodes.update({n: ref(E / n / 'artifact_sha256.json') for n in specs()})
    edges = []
    bypath = {v['path']: n for n, v in nodes.items()}
    def collect(d, n):
        if isinstance(d, dict):
            if d.get('path') in bypath:
                dep = bypath[d['path']]
                if dep != n and [n, dep] not in edges:
                    edges.append([n, dep])
            for v in d.values():
                collect(v, n)
        elif isinstance(d, list):
            for v in d:
                collect(v, n)
    for n, pin in nodes.items():
        if pin['path'].startswith(str(HERE) + '/'):
            collect(read(pin['path']), n)
    save('lifecycle_closure.json', {
        'schema': 'V6_NON_EFFECTIVE_ACCEPTANCE_FREEZE_LIFECYCLE_CLOSURE_V1',
        **BOUNDARY, 'STATUS': READY, 'NEXT_GATE': NEXT, 'STOP': True,
        'lifecycle': {'SOURCE_AND_CONTRACT_PERSISTED': 'YES', 'SOURCE_AND_CONTRACT_ACCEPTED': 'YES',
            'SOURCE_AND_CONTRACT_FROZEN': 'YES', 'CLOSURE_COMMITTED': 'NO', 'CLOSURE_PUBLISHED': 'NO',
            'PRODUCTION_RUNTIME_INSTALLED': 'NO', 'RUNTIME_EFFECTIVE': 'NO',
            'REAL_CLIENT_AUTHORIZATION': 'BLOCKED', 'REAL_PREPARATION_AUTHORIZED': 'NO'},
        'canonical': ref(R / 'evaluation/downstream_benchmark/v6_current_state.json'),
        'canonical_state': can['projection']['state'], 'event_count': 3, 'event_chain': can['event_chain'],
        'nodes': nodes, 'edges_dependent_to_dependency': sorted(edges),
        'historical_candidate_graph': ref(C / 'supersession_dependency_graph.json'),
        'historical_graph_reference_occurrences_verified': count,
        'closure_authority_over_historical_snapshots': 'Subsequent exact source/contract acceptance only; all historical preacceptance bytes and BLOCKED statuses retained.',
        'production_operations_authorized': False,
    })
    new_refs = sum(reference_count(read(p)) for p in HERE.glob('*.json'))
    save('closure_validation.json', {
        'schema': 'V6_NON_EFFECTIVE_FREEZE_CLOSURE_VALIDATION_V1',
        'status': 'DRAFT_REQUIRES_SEPARATE_SEALED_READBACK',
        'checks': {k: ('PENDING' if k == 'EXACT_EVIDENCE_SEAL' else 'PASS') for k in CHECKS},
        'lifecycle_closure': ref(HERE / 'lifecycle_closure.json'),
        'historical_graph_reference_occurrences_verified': count,
        'new_record_reference_occurrences_verified_at_construction': new_refs,
        'rejection_tests_rerun': False, '641_projections_rerun': False, 'full_E2E_rerun': False,
        'physical_power_loss_durability': 'NOT_ESTABLISHED',
        'ordinary_closure_code_failures': [],
    })
    save('commands_run.json', {
        'schema': 'V6_NON_EFFECTIVE_FREEZE_COMMAND_RECEIPTS_V1',
        'prewrite_inspection': [
            {'commands': ['cat exact user attachment', 'rg instructions/contracts/manifests',
                          'git status --short', 'git branch --show-current', 'git rev-parse HEAD'],
             'tool_chunk_ids': ['b1fd1e', 'af2ac7', '2bad77'],
             'nonfatal_result': 'rg command exit 2 because absent .airos path; no governing repo AGENTS or separate .airos contract found.'},
            {'argv': ['git', 'ls-remote', '--exit-code', 'origin', 'refs/heads/main'],
             'tool_chunk_id': 'd30f2c', 'exit_code': 128, 'stderr': 'Could not resolve host: github.com',
             'scope': 'Sandbox network attempt; no identity mismatch.'},
            {'argv': ['git', 'ls-remote', '--exit-code', 'origin', 'refs/heads/main'],
             'tool_chunk_id': 'e87df9', 'exit_code': 0, 'stdout': HEAD + '\trefs/heads/main\n'},
            {'commands': ['Python exact manifest/tree/source/canonical measurements',
                          'sed read-only prior verifier', 'cat prior threat/scope/preservation records',
                          'Python candidate/contract/graph/disposition inspection'],
             'tool_chunk_ids': ['bbe1db', 'ceddcc', '035645', '0208f9', '68ae01', 'cb2188', '4ee73e', '4b34d9'],
             'nonfatal_result': 'One exploratory cat locator filename absent; corrected to actual R02_locator_erratum.json. Oversized exploratory output was truncated; targeted follow-ups and full deterministic byte measurements supplied evidence.'},
            {'command': 'Read-only Python authenticated 1842-file/tree/ledger entry measurement',
             'tool_chunk_ids': ['7957bc', '326753'], 'exit_code': 0, 'result': 'ENTRY_PASS'},
            {'command': 'Read-only Python candidate/plan/dependency/version graph byte references',
             'tool_chunk_id': '4ee73e', 'exit_code': 0, 'references': 786, 'mismatches': []},
        ],
        'constructor_commands': COMMANDS,
        'constructor_invocation': ['python3', '-B', str(HERE / 'construct_closure.py'), 'prepare'],
        'execution_boundary': 'Read-only measurements and new closure files only. No runtime candidate imported or executed.',
        'closure_code_failures': [],
    })
    report()
    pin = seal('DRAFT')
    print(json.dumps({'status': 'DRAFT_SEALED', 'manifest': pin,
                      'total_file_count': read(HERE / 'artifact_sha256.json')['total_file_count']}))


def finalize():
    # The orchestration layer writes actual separate readback and fresh origin receipts.
    result = read(HERE / 'draft_readback_verification.json')
    assert result['status'] == 'PASS' and result['phase'] == 'DRAFT'
    assert result['checks'] == {k: 'PASS' for k in CHECKS}
    assert identity(HERE / 'artifact_sha256.json')['sha256'] == result['seal_sha256']
    live = read(HERE / 'live_origin_exit.json')
    assert live['exit_code'] == 0 and live['stdout'] == HEAD + '\trefs/heads/main\n'
    authority_check()
    snap = snapshot()
    seals(snap)
    _, targets, qual_count = baseline_check(snap)
    assert snap == read(HERE / 'entry_snapshot.json')
    assert preservation(snap, targets, qual_count) == read(HERE / 'preservation_verification.json')
    validation = read(HERE / 'closure_validation.json')
    validation['status'] = 'PASS'
    validation['checks'] = {k: 'PASS' for k in CHECKS}
    validation['actual_separate_draft_readback'] = ref(HERE / 'draft_readback_verification.json')
    validation['final_readback_required_before_reporting_ready'] = True
    validation['seal_semantics'] = 'Actual separate draft sealed readback passed. Final metadata and receipt additions must pass separate final readback after final sealing.'
    validation['fresh_live_origin_exit'] = ref(HERE / 'live_origin_exit.json')
    save('closure_validation.json', validation, replace=True)
    commands = read(HERE / 'commands_run.json')
    commands['finalize_measurement_commands'] = COMMANDS
    commands['separate_draft_readback'] = {
        'argv': ['python3', '-B', str(HERE / 'verify_closure.py'), '--draft'],
        'exit_code': 0, 'receipt': ref(HERE / 'draft_readback_verification.json')}
    commands['fresh_live_origin_exit'] = live
    commands['finalize_invocation'] = ['python3', '-B', str(HERE / 'construct_closure.py'), 'finalize']
    commands['final_readback_gate'] = {
        'argv': ['python3', '-B', str(HERE / 'verify_closure.py')],
        'receipt_location': 'Actual tool output after final seal; no circular result inside its own sealed payload.',
        'required_exit_code': 0, 'no_file_writes': True}
    save('commands_run.json', commands, replace=True)
    report(final=True)
    for p in HERE.glob('*.json'):
        if p.name not in ('artifact_sha256.json', 'draft_readback_verification.json'):
            reference_count(read(p))
    pin = seal('FINAL')
    assert read(HERE / 'artifact_sha256.json')['total_file_count'] == 19
    print(json.dumps({'status': 'FINAL_SEALED_REQUIRES_SEPARATE_READBACK', 'manifest': pin,
                      'total_file_count': 19}))


if __name__ == '__main__':
    assert HERE == E / 'v6_remediated_successor_non_effective_acceptance_freeze_v1'
    assert sys.argv[1:] in (['prepare'], ['finalize'])
    (prepare if sys.argv[1] == 'prepare' else finalize)()

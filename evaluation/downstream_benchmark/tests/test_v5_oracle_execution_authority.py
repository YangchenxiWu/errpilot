"""Successor authority tests. Every actual process boundary is a tripwire."""

from __future__ import annotations

import copy
import json
import shutil
import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest

from evaluation.downstream_benchmark.screening import executor as legacy
from evaluation.downstream_benchmark.screening import v5_oracle_executor as v


@pytest.fixture(autouse=True)
def no_process(monkeypatch):
    deny = Mock(side_effect=AssertionError('REAL PROCESS/ORACLE FORBIDDEN'))
    for name in ('Popen', 'run', 'check_output'):
        monkeypatch.setattr(subprocess, name, deny)
    monkeypatch.setattr(v.docker, 'DockerProcessRunner', deny)
    monkeypatch.setattr(legacy, '_run', deny)
    monkeypatch.setattr(legacy, '_git', deny)
    yield deny
    assert deny.call_count == 0


@pytest.fixture(scope='module')
def current():
    return v.resolve_current_population()


@pytest.fixture
def authority(tmp_path):
    path = tmp_path / 'successor.json'
    shutil.copyfile(v.AUTHORITY, path)
    return path


def save(path, value):
    path.write_bytes(legacy.canonical_json_bytes(value))


def admit(current, path, token=legacy.EXECUTION_AUTHORITY_TOKEN):
    return v.require_execution_authority(token, path, current=current)


@pytest.mark.parametrize('token', ('', 'HUMAN_PI_AUTHORIZED', 'force'))
def test_token_alone_cannot_authorize(current, authority, token):
    with pytest.raises(legacy.InfrastructureFailure, match='BLOCKED_AUTHORITY'):
        admit(current, authority, token)


def test_no_successor_rejected(current, tmp_path):
    with pytest.raises(legacy.InfrastructureFailure, match='BLOCKED_AUTHORITY'):
        admit(current, tmp_path / 'absent.json')


def test_exact_valid_successor_accepted_with_false_historical_booleans(current, authority):
    before = v.READINESS.read_bytes()
    historical = v.read_json(v.READINESS)
    assert historical['real_oracle_execution_authorized'] is False
    assert set(historical['lifecycle'].values()) == {False}
    assert admit(current, authority)['production_gate'] == 'ACCEPTED'
    assert v.READINESS.read_bytes() == before
    assert legacy.sha256_bytes(before) == v.READINESS_FILES[v.READINESS.name]


MUTATIONS = (
    ('WRONG_TRANSACTION_REJECTED', ('transaction',), 'V4_ORACLE_SCREENING'),
    ('WRONG_READINESS_BASELINE_REJECTED', ('readiness_baseline_commit',), v.BASELINE),
    ('WRONG_CANDIDATE_HASH_REJECTED',
     ('readiness_evidence', v.READINESS.name, 'sha256'), 'a' * 64),
    ('WRONG_LIFECYCLE_HASH_REJECTED',
     ('readiness_evidence', 'V5_ORACLE_EXECUTION_READINESS_LIFECYCLE_CLOSURE_V1.md', 'sha256'),
     'a' * 64),
    ('WRONG_V5_STATE_REJECTED', ('v5_current_state_authority', v.v5.STATE, 'sha256'), 'a' * 64),
    ('WRONG_MANIFEST_REJECTED', ('current_plan_manifest', 'sha256'), 'a' * 64),
    ('WRONG_POPULATION_REJECTED', ('population', 'case_ids'), list(reversed(v.INITIAL + v.NEWER))),
    ('WRONG_ENVIRONMENT_BINDING_REJECTED', ('environment_bindings', 'sha256'), 'a' * 64),
    ('WRONG_REPETITION_NAMESPACE_REJECTED', ('repetition_namespace', 'planned_repetitions'), 167),
    ('STALE_AUTHORITY_REJECTED', ('activation_transaction',), 'V4_ORACLE_EXECUTION_AUTHORITY_V1'),
    ('WRONG_SCHEMA_REJECTED', ('schema',), 'V5_ORACLE_EXECUTION_READINESS_BRIDGE_V1'),
    ('WRONG_VERSION_REJECTED', ('schema_version',), 2),
    ('WRONG_PLAN_BASELINE_REJECTED', ('plan_population_baseline_commit',), v.READINESS_BASELINE),
    ('WRONG_CANDIDATE_PATH_REJECTED', ('readiness_evidence', v.READINESS.name, 'path'), '/tmp/other'),
    ('WRONG_MANIFEST_PATH_REJECTED', ('current_plan_manifest', 'path'), '/tmp/latest.json'),
    ('WRONG_CASE_COUNT_REJECTED', ('population', 'case_count'), 27),
    ('WRONG_POPULATION_DIGEST_REJECTED', ('population', 'sha256'), 'a' * 64),
    ('WRONG_VARIANT_COUNT_REJECTED', ('environment_bindings', 'variant_count'), 55),
    ('WRONG_REPETITION_ORDER_REJECTED', ('repetition_namespace', 'slots_sha256'), 'a' * 64),
    ('WRONG_3X3_REJECTED', ('repetition_namespace', 'repetitions_per_variant'), 2),
    ('WRONG_EXECUTION_ID_REJECTED', ('repetition_namespace', 'execution_id'), 'retry-v2'),
    ('WRONG_EVIDENCE_ROOT_REJECTED', ('repetition_namespace', 'evidence_root'), '/tmp/other'),
    ('WRONG_TIMEOUT_REJECTED', ('timeout', 'trial_timeout_seconds'), 901),
    ('WRONG_DECISION_REJECTED', ('authority_decision',), 'CANDIDATE_ONLY'),
    ('NOT_AUTHORIZED_REJECTED', ('real_oracle_execution_authorized',), False),
    ('WRONG_HUMAN_AUTHORITY_REJECTED', ('human_pi_authorized',), False),
    ('BOOL_AS_INTEGER_REJECTED', ('schema_version',), True),
    ('INTEGER_AS_BOOL_REJECTED', ('real_oracle_execution_authorized',), 1),
    ('FLOAT_AS_COUNT_REJECTED', ('repetition_namespace', 'planned_repetitions'), 168.0),
)


@pytest.mark.parametrize('label,keys,value', MUTATIONS, ids=[m[0] for m in MUTATIONS])
def test_authority_matrix(current, authority, label, keys, value):
    candidate = v.read_json(authority)
    target = candidate
    for key in keys[:-1]:
        target = target[key]
    assert target[keys[-1]] != value or type(target[keys[-1]]) is not type(value)
    target[keys[-1]] = value
    save(authority, candidate)
    with pytest.raises(legacy.InfrastructureFailure, match='BLOCKED_AUTHORITY'):
        admit(current, authority)


@pytest.mark.parametrize('key', (
    'schema', 'schema_version', 'activation_transaction', 'transaction', 'readiness_baseline_commit',
    'plan_population_baseline_commit', 'readiness_evidence', 'v5_current_state_authority',
    'current_plan_manifest', 'population', 'environment_bindings', 'repetition_namespace',
    'timeout', 'authority_decision', 'human_pi_authorized', 'real_oracle_execution_authorized',
))
def test_missing_required_field_rejected(current, authority, key):
    candidate = v.read_json(authority)
    del candidate[key]
    save(authority, candidate)
    with pytest.raises(legacy.InfrastructureFailure, match='BLOCKED_AUTHORITY'):
        admit(current, authority)


@pytest.mark.parametrize('data', (
    b'not-json', b'[]', b'null', b'{"transaction":"one","transaction":"two"}',
    b'{"schema_version":NaN}', b'\xff',
))
def test_malformed_authority_rejected(current, authority, data):
    authority.write_bytes(data)
    with pytest.raises(legacy.InfrastructureFailure, match='BLOCKED_AUTHORITY'):
        admit(current, authority)


def test_unknown_fields_rejected(current, authority):
    save(authority, dict(v.read_json(authority), force=True))
    with pytest.raises(legacy.InfrastructureFailure, match='BLOCKED_AUTHORITY'):
        admit(current, authority)


def test_historical_artifact_is_stale_authority(current):
    with pytest.raises(legacy.InfrastructureFailure, match='BLOCKED_AUTHORITY'):
        admit(current, v.READINESS)


def test_symlink_authority_rejected(current, tmp_path):
    path = tmp_path / 'link.json'
    path.symlink_to(v.AUTHORITY)
    with pytest.raises(legacy.InfrastructureFailure, match='BLOCKED_AUTHORITY'):
        admit(current, path)


@pytest.mark.parametrize('name', tuple(v.READINESS_FILES | v.V5_AUTHORITY_FILES))
def test_referenced_frozen_bytes_drift_rejected(current, authority, tmp_path, monkeypatch, name):
    for source in v.READINESS_FILES | v.V5_AUTHORITY_FILES:
        target = tmp_path / 'benchmark' / source
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(v.BENCHMARK / source, target)
    (tmp_path / 'benchmark' / name).write_bytes(b'changed frozen evidence')
    monkeypatch.setattr(v, 'BENCHMARK', tmp_path / 'benchmark')
    with pytest.raises(legacy.InfrastructureFailure, match='BLOCKED_AUTHORITY'):
        admit(current, authority)


@pytest.mark.parametrize('field,value', (('manifest_sha256', 'a' * 64),
                                      ('manifest_path', Path('/tmp/stale.json'))))
def test_stale_resolved_manifest_rejected(current, authority, field, value):
    fields = dict(manifest_path=current.manifest_path, manifest_sha256=current.manifest_sha256,
                  cases=current.cases)
    fields[field] = value
    with pytest.raises(legacy.InfrastructureFailure, match='BLOCKED_AUTHORITY'):
        admit(v.CurrentPopulation(**fields), authority)


def test_binding_drift_after_resolution_rejected(current, authority):
    cases = copy.deepcopy(current.cases)
    cases['pandas::102']['selected']['environment_bindings']['BUGGY']['environment_image_id'] = (
        'sha256:' + 'a' * 64)
    with pytest.raises(legacy.InfrastructureFailure, match='BLOCKED_AUTHORITY'):
        admit(v.CurrentPopulation(current.manifest_path, current.manifest_sha256, cases), authority)


def test_authority_changed_during_admission_rejected(current, authority, monkeypatch):
    expected = v.expected_execution_authority
    def change_after_read(resolved):
        result = expected(resolved)
        authority.write_bytes(b'changed during admission')
        return result
    monkeypatch.setattr(v, 'expected_execution_authority', change_after_read)
    with pytest.raises(legacy.InfrastructureFailure, match='BLOCKED_AUTHORITY.*changed during admission'):
        admit(current, authority)


def historical_images():
    images = {}
    for item in v.load_population():
        for binding in item['bindings'].values():
            path = Path(binding['environment_identity_path']).parent / 'image_inspect.json'
            saved = json.loads(path.read_bytes())
            saved = saved[0] if isinstance(saved, list) else saved
            images[saved['Id']] = {k: saved[k] for k in ('Id', 'Os', 'Architecture', 'RootFS')}
    return images


def test_all_168_shared_production_authority_gates_reach_dispatch_sentinel(monkeypatch, no_process):
    admission = Mock(wraps=v.require_execution_authority)
    dispatch = Mock(wraps=v.docker.dispatch)
    monkeypatch.setattr(v, 'require_execution_authority', admission)
    monkeypatch.setattr(v.docker, 'dispatch', dispatch)
    before = v.READINESS.read_bytes()
    report = v.authority_dry_validate(images=historical_images())
    assert admission.call_count == 28 + 168 and dispatch.call_count == 168
    assert report['planned_repetitions'] == report['authority_dry_validated_repetitions'] == 168
    assert report['executed_repetitions'] == report['consumed_repetitions'] == no_process.call_count == 0
    records = report['records']
    assert len({(r['case_id'], r['revision_label'], r['ordinal']) for r in records}) == 168
    assert len({r['evidence_path'] for r in records}) == 168
    assert all(call.kwargs['dry_run'] is True and 'runner' not in call.kwargs
               for call in dispatch.call_args_list)
    for record in records:
        assert record['execution_authority']['production_gate'] == 'ACCEPTED'
        assert record['execution_authority']['sha256'] == report['authority_sha256']
        assert record['timeout'] == v.TIMEOUT
        assert record['environment_image_id'] in record['docker_invocation']
        assert record['execution_id'] == v.AUTHORITY_EXECUTION_ID
        assert record['selected_plan_sha256'] == legacy.sha256_file(Path(record['selected_plan_path']))
        assert record['executed'] is record['consumed'] is False
        assert not Path(record['evidence_path']).exists()
    assert not list((v.WORK / 'screening_evidence').rglob('*.json'))
    assert v.READINESS.read_bytes() == before


def test_authority_drift_between_slots_stops_before_second_dispatch(authority, monkeypatch):
    dispatch = v.docker.dispatch
    count = 0
    def change_after_first(*args, **kwargs):
        nonlocal count
        count += 1
        result = dispatch(*args, **kwargs)
        authority.write_bytes(b'stale')
        return result
    monkeypatch.setattr(v.docker, 'dispatch', change_after_first)
    with pytest.raises(legacy.InfrastructureFailure, match='BLOCKED_AUTHORITY'):
        v.authority_dry_validate(images=historical_images(), authority_path=authority)
    assert count == 1
    assert not list((v.WORK / 'screening_evidence').rglob('*.json'))


def test_wrong_runtime_namespace_rejected_before_image_or_dispatch(monkeypatch):
    images, sentinel = Mock(), Mock()
    with pytest.raises(legacy.InfrastructureFailure, match='BLOCKED_AUTHORITY'):
        v.execute_case(case='pandas::102', execution_id='retry-other',
                       authorization=legacy.EXECUTION_AUTHORITY_TOKEN,
                       image_inspector=images, sentinel=sentinel)
    images.assert_not_called()
    sentinel.assert_not_called()


def publication_git(mutation=''):
    """Emulate only readonly Git responses; no actual process can be created."""
    def read(argv, **kwargs):
        assert argv[0] == 'git'
        if argv[1:3] == ['cat-file', 'blob']:
            revision, relative = argv[3].split(':', 1)
            path = v.BENCHMARK.parents[1] / relative
            if mutation == 'missing_authority' and path == v.AUTHORITY:
                raise subprocess.CalledProcessError(128, argv)
            if (mutation == 'uncommitted_executor' and path.name == 'v5_oracle_executor.py'
                    or mutation == 'wrong_baseline_bytes' and revision == v.READINESS_BASELINE):
                return b'wrong committed bytes'
            return path.read_bytes()
        if argv[1:3] == ['merge-base', '--is-ancestor']:
            if mutation == 'wrong_ancestry':
                raise subprocess.CalledProcessError(1, argv)
            assert argv[3:] == [v.READINESS_BASELINE, 'HEAD']
            return b''
        if argv[1:3] == ['rev-parse', 'HEAD']:
            return b'a' * 40 + b'\n'
        if argv[1] == 'ls-remote':
            if mutation == 'remote_unavailable':
                raise subprocess.CalledProcessError(128, argv)
            if mutation == 'empty_remote':
                return b''
            return (b'b' if mutation == 'wrong_remote' else b'a') * 40 + b'\trefs/heads/main\n'
        raise AssertionError(f'unexpected Git operation: {argv}')
    return read


def test_exact_committed_published_successor_gate_accepts_readonly_git_fixture(monkeypatch):
    query = Mock(side_effect=publication_git())
    monkeypatch.setattr(subprocess, 'check_output', query)
    v.require_execution_publication()
    assert any(call.args[0][1] == 'ls-remote' for call in query.call_args_list)


@pytest.mark.parametrize('mutation', ('missing_authority', 'uncommitted_executor', 'wrong_ancestry',
                                     'wrong_baseline_bytes', 'wrong_remote', 'remote_unavailable',
                                     'empty_remote'))
def test_real_publication_default_deny(monkeypatch, mutation):
    monkeypatch.setattr(subprocess, 'check_output', publication_git(mutation))
    with pytest.raises(legacy.InfrastructureFailure, match='BLOCKED_AUTHORITY'):
        v.require_execution_publication()


def test_production_authority_override_rejected_before_query(tmp_path):
    with pytest.raises(legacy.InfrastructureFailure, match='BLOCKED_AUTHORITY'):
        v.require_execution_publication(tmp_path / 'other.json')


def test_real_candidate_blocked_before_image_workspace_or_oracle(monkeypatch):
    monkeypatch.setattr(subprocess, 'check_output', publication_git('missing_authority'))
    inspector = Mock(side_effect=AssertionError('real image probe forbidden'))
    monkeypatch.setattr(v.docker, 'inspect_images', inspector)
    with pytest.raises(legacy.InfrastructureFailure, match='BLOCKED_AUTHORITY'):
        v.execute_case(case='pandas::102', execution_id=v.AUTHORITY_EXECUTION_ID,
                       dry_run=False, authorization=legacy.EXECUTION_AUTHORITY_TOKEN)
    inspector.assert_not_called()
    assert not list((v.WORK / 'screening_evidence').rglob('*.json'))

"""Non-executing V5 plan/backend tests; real process creation is a tripwire."""

from __future__ import annotations

import copy
import json
import shutil
import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest

from evaluation.downstream_benchmark.screening import docker_oracle_backend_v1 as backend
from evaluation.downstream_benchmark.screening import executor as legacy
from evaluation.downstream_benchmark.screening import oracle_trial_driver_v1 as driver
from evaluation.downstream_benchmark.screening import v5_oracle_executor as v


@pytest.fixture(autouse=True)
def no_real_process(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError('REAL PROCESS CREATION FORBIDDEN IN BRIDGE TESTS')
    monkeypatch.setattr(subprocess, 'Popen', deny)
    monkeypatch.setattr(subprocess, 'run', deny)
    monkeypatch.setattr(subprocess, 'check_output', deny)


@pytest.fixture(scope='module')
def authentic_population():
    # Only inert frozen ledgers and files are read; no Docker/subject process.
    return v.load_population()


@pytest.fixture
def context(tmp_path, authentic_population):
    population = copy.deepcopy(authentic_population)
    images = {}
    for item in population:
        case = item['case_id']
        root = tmp_path / 'historical' / legacy.safe_case_slug(case)
        root.mkdir(parents=True)
        for key in ('plan_path', 'script_path', 'protected_manifest_path'):
            original = Path(item[key])
            target = root / (key + '.json' if key != 'script_path' else 'run_test.sh')
            shutil.copyfile(original, target)
            item[key] = str(target)
        for variant, binding in item['bindings'].items():
            original = Path(binding['environment_identity_path'])
            saved = json.loads((original.parent / 'image_inspect.json').read_bytes())
            saved = saved[0] if isinstance(saved, list) else saved
            images[saved['Id']] = {k: saved[k] for k in ('Id', 'Os', 'Architecture', 'RootFS')}
            target = root / (variant + '_environment_identity.json')
            shutil.copyfile(original, target)
            binding['environment_identity_path'] = str(target)
    namespace = tmp_path / 'oracle_plans/v1_1'
    files = v.derive_bundle(population, namespace)
    v.write_exclusive_bundle(files, namespace)
    manifest = namespace / 'current_plan_manifest_v1.json'
    return {'population': population, 'images': images, 'manifest': manifest,
            'namespace': namespace, 'work': tmp_path / 'work', 'files': files}


def resolve(context):
    return v.resolve_current_population(manifest_path=context['manifest'],
                                        population=context['population'])


def save(path, value):
    path.write_bytes(legacy.canonical_json_bytes(value))


def slot(context, **overrides):
    args = dict(case='pandas::102', variant='BUGGY', ordinal=1, execution_id='synthetic',
                images=context['images'], work=context['work'])
    args.update(overrides)
    return v.preflight_slot(resolve(context), **args)


def test_exact_plan_and_invocation_accepted(context):
    invocation, binding = slot(context)
    assert binding['environment_image_id'] in invocation.argv
    assert '--network=none' in invocation.argv and '--read-only' in invocation.argv
    assert invocation.argv[invocation.argv.index('--platform') + 1] == 'linux/amd64'
    assert invocation.argv[invocation.argv.index('--workdir') + 1] == '/subject'
    assert '--entrypoint' in invocation.argv
    assert invocation.request['cwd'] == '/subject'
    assert invocation.request['commands'][0]['argv'] == list(legacy.parse_recognized_command(
        invocation.request['commands'][0]['text']))
    assert not invocation.evidence.exists()
    assert 'eligibility' not in binding


@pytest.mark.parametrize('mutation', (
    'missing_case', 'duplicate_case', 'unexpected_case', 'wrong_hash', 'wrong_baseline',
    'missing_timeout', 'wrong_300', 'wrong_900', 'wrong_timeout_authority',
    'stale_initial_selected', 'predecessor_masquerade', 'wrong_lineage', 'wrong_environment',
    'wrong_selected_version', 'ambiguous_path',
))
def test_manifest_fail_closed(context, mutation):
    path = context['manifest']
    manifest = v.read_json(path)
    first = manifest['cases'][0]
    if mutation == 'missing_case':
        manifest['cases'].pop()
    elif mutation == 'duplicate_case':
        manifest['cases'][-1] = copy.deepcopy(first)
    elif mutation == 'unexpected_case':
        first['case_id'] = 'excluded::1'
    elif mutation == 'wrong_hash':
        first['selected_plan_sha256'] = 'a' * 64
    elif mutation == 'wrong_baseline':
        manifest['v5_baseline_commit'] = 'b' * 40
    elif mutation == 'missing_timeout':
        del manifest['timeout']
    elif mutation in ('wrong_300', 'wrong_900'):
        manifest['timeout']['subcommand_timeout_seconds' if mutation == 'wrong_300'
                            else 'trial_timeout_seconds'] -= 1
    elif mutation == 'wrong_timeout_authority':
        manifest['timeout']['authority_sha256'] = 'c' * 64
    elif mutation in ('stale_initial_selected', 'predecessor_masquerade'):
        first['selected_plan_path'] = first['predecessor']['path']
        first['selected_plan_sha256'] = first['predecessor']['sha256']
        if mutation == 'predecessor_masquerade':
            first['selected_version'] = '1.1'
    elif mutation == 'wrong_lineage':
        first['predecessor']['sha256'] = 'd' * 64
    elif mutation == 'wrong_environment':
        first['environment_bindings']['BUGGY']['environment_image_id'] = 'sha256:' + 'e' * 64
    elif mutation == 'wrong_selected_version':
        first['selected_version'] = '1'
    elif mutation == 'ambiguous_path':
        first['selected_plan_path'] = str(Path(first['selected_plan_path']).parent / '..'
                                          / 'execution_plan.json')
    save(path, manifest)
    with pytest.raises(legacy.InfrastructureFailure):
        resolve(context)


@pytest.mark.parametrize('mutation', ('malformed', 'wrong_command', 'wrong_cwd', 'wrong_plan_hash'))
def test_selected_plan_fail_closed(context, mutation):
    manifest = v.read_json(context['manifest'])
    path = Path(manifest['cases'][0]['selected_plan_path'])
    if mutation == 'malformed':
        path.write_text('{')
    else:
        plan = v.read_json(path)
        if mutation == 'wrong_command':
            plan['oracle_commands'][0] += ' other_test'
        elif mutation == 'wrong_cwd':
            plan['oracle_cwd'] = '/tmp'
        else:
            plan['execution_plan_sha256'] = '0' * 64
        save(path, plan)
    with pytest.raises(legacy.InfrastructureFailure):
        resolve(context)


@pytest.mark.parametrize('variant', ('BUGGY', 'FIXED'))
def test_wrong_image_identity_rejected(context, variant):
    image = context['population'][0]['bindings'][variant]['environment_image_id']
    context['images'][image]['Id'] = 'sha256:' + 'f' * 64
    with pytest.raises(legacy.InfrastructureFailure, match='Docker image identity'):
        slot(context, variant=variant)


def test_missing_image_rejected(context):
    with pytest.raises(legacy.InfrastructureFailure, match='missing/nonimmutable'):
        slot(context, images={})


@pytest.mark.parametrize('fields', ({'case': 'tqdm::6'}, {'variant': 'OTHER'}, {'ordinal': 0},
                                  {'ordinal': 4}, {'ordinal': True}, {'execution_id': '../unsafe'}))
def test_wrong_screening_unit_rejected(context, fields):
    with pytest.raises(legacy.InfrastructureFailure):
        slot(context, **fields)


def test_duplicate_repetition_rejected(context):
    seen = set()
    slot(context, seen=seen)
    with pytest.raises(legacy.InfrastructureFailure, match='duplicate repetition'):
        slot(context, seen=seen)


def test_evidence_collision_rejected(context):
    invocation, _ = slot(context)
    invocation.evidence.mkdir(parents=True)
    with pytest.raises(legacy.InfrastructureFailure, match='evidence collision'):
        slot(context)


def test_existing_different_attempt_rejected(context):
    root = context['work'] / 'screening_evidence/pandas-102/older_attempt'
    root.mkdir(parents=True)
    with pytest.raises(legacy.InfrastructureFailure, match='prior oracle attempt'):
        slot(context)


def test_environment_file_drift_rejected(context):
    path = Path(context['population'][0]['bindings']['BUGGY']['environment_identity_path'])
    identity = v.read_json(path)
    identity['revision_sha'] = '0' * 40
    save(path, identity)
    with pytest.raises(legacy.InfrastructureFailure, match='environment hash'):
        slot(context)


@pytest.mark.parametrize('timeout', ({}, dict(v.TIMEOUT, subcommand_timeout_seconds=300.0),
                                  dict(v.TIMEOUT, trial_timeout_seconds=True)))
def test_timeout_default_deny(timeout):
    with pytest.raises(legacy.InfrastructureFailure):
        v.validate_timeout(timeout)


def test_gate_is_satisfied_without_flag_flip():
    assert v.PRE_EXECUTION_TIMEOUT_GATE_REQUIRED is legacy.PRE_EXECUTION_TIMEOUT_GATE_REQUIRED is True
    v.validate_timeout(v.TIMEOUT)


def test_bundle_collision_never_overwrites(context):
    path = next(p for p in context['files'] if p.name == 'execution_plan.json')
    path.write_bytes(b'conflicting governed content')
    with pytest.raises(legacy.InfrastructureFailure, match='conflicting existing successor'):
        v.write_exclusive_bundle(context['files'], context['namespace'])
    assert path.read_bytes() == b'conflicting governed content'


def test_unselected_extra_is_not_selected(context):
    (context['namespace'] / 'zzz-latest.json').write_bytes(b'not current authority')
    current = resolve(context)
    assert len(current.cases) == 28 and all('zzz-latest' not in i['selected']['selected_plan_path']
                                          for i in current.cases.values())


def test_all_168_reach_actual_case_dispatch_sentinel_without_process_or_evidence(context):
    records, names, destinations = [], set(), set()
    def sentinel(invocation, binding):
        assert invocation.container_name not in names
        assert str(invocation.evidence) not in destinations
        names.add(invocation.container_name)
        destinations.add(str(invocation.evidence))
        assert not invocation.evidence.exists()
        return dict(binding, executed=False)
    for case in v.INITIAL + v.NEWER:
        records.extend(v.execute_case(case=case, execution_id='synthetic-dry',
                                      manifest_path=context['manifest'], work=context['work'],
                                      population=context['population'], sentinel=sentinel,
                                      image_inspector=lambda _: context['images']))
    assert len(records) == len(names) == len(destinations) == 168
    assert not context['work'].exists()
    assert [r['revision_label'] for r in records[:6]] == ['BUGGY'] * 3 + ['FIXED'] * 3


def test_default_dry_requires_nonexecuting_sentinel(context):
    with pytest.raises(legacy.InfrastructureFailure, match='sentinel'):
        v.execute_case(case='pandas::102', execution_id='synthetic',
                       manifest_path=context['manifest'], work=context['work'],
                       population=context['population'], image_inspector=lambda _: context['images'])
    assert not context['work'].exists()


@pytest.mark.parametrize('authorization', ('', legacy.EXECUTION_AUTHORITY_TOKEN))
def test_real_execution_stays_blocked_before_any_process_or_evidence(authorization):
    with pytest.raises(legacy.InfrastructureFailure):
        v.execute_case(case='pandas::102', execution_id='must-not-execute', dry_run=False,
                       authorization=authorization)


class FakeClock:
    def __init__(self):
        self.now = 0.0
    def __call__(self):
        return self.now


def synthetic_trial(tmp_path, codes, durations=None, *, startup=0, launch_error=False):
    invocation = backend.construct_invocation(case='SYNTHETIC', variant='BUGGY', ordinal=1,
                                              execution_id='fake', image='sha256:' + 'a' * 64,
                                              evidence=tmp_path / 'trial',
                                              commands=['pytest -q test_sample.py  '] * len(codes),
                                              protected=[])
    invocation.evidence.mkdir()
    capture = invocation.evidence / 'capture'
    capture.mkdir()
    clock, killed, waits = FakeClock(), [], []
    pending = list(zip(codes, durations or [1] * len(codes)))
    def factory(argv, **kwargs):
        assert kwargs['shell'] is False and kwargs['cwd'] == '/subject'
        if launch_error:
            raise OSError('synthetic launch failure')
        code, duration = pending.pop(0)
        kwargs['stdout'].write(b'raw\x00stdout\xff\n')
        kwargs['stderr'].write(b'raw\r\nstderr\xfe')
        clock.now += startup
        process = Mock(pid=777)
        def wait(timeout=None):
            waits.append(timeout)
            if timeout is None:
                return -9
            clock.now += min(duration, timeout)
            if duration > timeout:
                raise subprocess.TimeoutExpired(argv, timeout)
            return code
        process.wait.side_effect = wait
        return process
    records = driver.run_trial(invocation.request, capture, process_factory=factory, clock=clock,
                               kill_group=lambda *args: killed.append(args), stamp=lambda: 'synthetic')
    launch = {'state': 'COMPLETED', 'exit_code': 0, 'stdout': b'docker\x00out', 'stderr': b'docker\xfferr'}
    result = backend.capture_result(invocation, launch, clock=clock, started=0)
    return invocation, result, records, killed, waits


@pytest.mark.parametrize('codes,expected', (([0, 0], 'TRIAL_PASS'), ([1, 0], 'TRIAL_FAIL'),
                                         ([0, 1], 'TRIAL_FAIL'), ([-9, 0], 'INTERRUPTED_NOT_ELIGIBILITY')))
def test_synthetic_subject_results_are_exit_based_and_ordered(tmp_path, codes, expected):
    invocation, result, records, killed, waits = synthetic_trial(tmp_path, codes)
    assert result['trial_result'] == expected
    assert result['exit_codes'] == (codes[:1] if codes[0] < 0 else codes)
    assert all(r['command'] == 'pytest -q test_sample.py  ' for r in records)
    assert not killed and all(v == 300 for v in waits)
    assert 'eligibility' not in result and 'classification' not in result
    assert invocation.request['commands'][0]['argv'] == ['pytest', '-q', 'test_sample.py']


def test_synthetic_launch_error_remains_infrastructure(tmp_path):
    _, result, _, _, _ = synthetic_trial(tmp_path, [0, 0], launch_error=True)
    assert result['trial_result'] == 'INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY'
    assert len(result['subcommands']) == 1


@pytest.mark.parametrize('durations,reason,count', (([301, 1], 'ORACLE_SUBCOMMAND_TIMEOUT', 1),
                                                   ([290, 290, 290, 50], 'ORACLE_TRIAL_TIMEOUT', 4)))
def test_synthetic_timeouts_terminate_reap_stop_and_do_not_become_fail(tmp_path, durations, reason, count):
    _, result, records, killed, waits = synthetic_trial(tmp_path, [0] * len(durations), durations)
    assert result['trial_result'] == 'INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY'
    assert result['infrastructure_subreason'] == reason
    assert records[-1]['infrastructure_subreason'] == reason and len(records) == count
    assert len(killed) == 1 and waits[-1] is None
    if reason == 'ORACLE_TRIAL_TIMEOUT':
        assert waits[-2] == 30


def test_subcommand_clock_includes_startup(tmp_path):
    _, result, _, killed, waits = synthetic_trial(tmp_path, [0], [291], startup=10)
    assert waits[0] == 290 and killed
    assert result['infrastructure_subreason'] == 'ORACLE_SUBCOMMAND_TIMEOUT'


def test_stdout_stderr_preserved_as_raw_bytes_and_hashes(tmp_path):
    invocation, result, records, _, _ = synthetic_trial(tmp_path, [1, 0])
    for record in result['subcommands']:
        for stream, expected in [('stdout', b'raw\x00stdout\xff\n'), ('stderr', b'raw\r\nstderr\xfe')]:
            path = Path(record[stream + '_artifact'])
            assert path.read_bytes() == expected
            assert record[stream + '_sha256'] == legacy.sha256_bytes(expected)
    assert (invocation.evidence / 'docker_stdout.raw').read_bytes() == b'docker\x00out'
    assert result['combined_output_available'] is False


def test_missing_evidence_never_passes(tmp_path):
    invocation, _, _, _, _ = synthetic_trial(tmp_path, [0])
    for stream in ('stdout', 'stderr'):
        (invocation.evidence / f'docker_{stream}.raw').unlink()
    (invocation.evidence / 'capture/subcommands/01/stdout.raw').unlink()
    with pytest.raises(legacy.InfrastructureFailure, match='missing raw'):
        backend.capture_result(invocation, {'state': 'COMPLETED', 'exit_code': 0},
                               clock=lambda: 1, started=0)


@pytest.mark.parametrize('state,exit_code,expected', (
    ('COMPLETED', 125, 'INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY'),
    ('INFRASTRUCTURE_ERROR', None, 'INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY'),
    ('INTERRUPTED', None, 'INTERRUPTED_NOT_ELIGIBILITY'),
))
def test_docker_failure_never_becomes_scientific_result(tmp_path, state, exit_code, expected):
    invocation, _, _, _, _ = synthetic_trial(tmp_path, [0])
    for stream in ('stdout', 'stderr'):
        (invocation.evidence / f'docker_{stream}.raw').unlink()
    result = backend.capture_result(invocation, {'state': state, 'exit_code': exit_code},
                                    clock=lambda: 1, started=0)
    assert result['trial_result'] == expected


def test_host_aggregate_timeout_invokes_container_termination(monkeypatch, tmp_path):
    process = Mock(pid=999, returncode=-9)
    process.communicate.side_effect = [subprocess.TimeoutExpired('fake', 900), (b'partial', b'error')]
    popen = Mock(return_value=process)
    monkeypatch.setattr(subprocess, 'Popen', popen)
    invocation = backend.construct_invocation(case='SYNTHETIC', variant='FIXED', ordinal=3,
                                              execution_id='fake', image='sha256:' + 'a' * 64,
                                              evidence=tmp_path, commands=['pytest -q'], protected=[])
    runner = backend.DockerProcessRunner()
    runner.terminate_and_reap = Mock()
    result = runner(invocation, lambda: 900)
    runner.terminate_and_reap.assert_called_once_with(invocation, process)
    assert result['infrastructure_subreason'] == 'ORACLE_TRIAL_TIMEOUT'
    assert result['state'] == 'INFRASTRUCTURE_ERROR' and result['stdout'] == b'partial'
    assert popen.call_args.kwargs['shell'] is False


def test_container_termination_targets_daemon_owned_container_and_reaps(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(subprocess, 'run', lambda args, **kwargs: calls.append(args)
                        or subprocess.CompletedProcess(args, 0, b'', b''))
    killed = Mock()
    monkeypatch.setattr(backend.os, 'killpg', killed)
    process = Mock(pid=999)
    invocation = backend.construct_invocation(case='SYNTHETIC', variant='BUGGY', ordinal=1,
                                              execution_id='fake', image='sha256:' + 'a' * 64,
                                              evidence=tmp_path, commands=['pytest'], protected=[])
    backend.DockerProcessRunner().terminate_and_reap(invocation, process)
    assert calls == [['docker', 'kill', invocation.container_name],
                     ['docker', 'rm', '--force', invocation.container_name]]
    killed.assert_called_once()
    process.wait.assert_called_once()


def test_expired_complete_trial_never_launches_process(tmp_path):
    invocation = backend.construct_invocation(case='SYNTHETIC', variant='BUGGY', ordinal=1,
                                              execution_id='fake', image='sha256:' + 'a' * 64,
                                              evidence=tmp_path, commands=['pytest'], protected=[])
    result = backend.DockerProcessRunner()(invocation, lambda: 0)
    assert result['infrastructure_subreason'] == 'ORACLE_TRIAL_TIMEOUT'


def test_mutable_image_and_shell_command_not_constructible(tmp_path):
    for image, command in [('python:latest', 'pytest'), ('sha256:' + 'a' * 64, 'pytest | cat')]:
        with pytest.raises((legacy.InfrastructureFailure, legacy.PreparationError)):
            backend.construct_invocation(case='SYNTHETIC', variant='BUGGY', ordinal=1,
                                          execution_id='fake', image=image, evidence=tmp_path,
                                          commands=[command], protected=[])


def test_readonly_image_metadata_adapter_uses_only_image_inspect(monkeypatch):
    image = 'sha256:' + 'a' * 64
    output = ' '.join(json.dumps(v) for v in (image, 'linux', 'amd64', {'Layers': ['layer']})) + '\n'
    called = []
    def run(argv, **kwargs):
        called.append(argv)
        return subprocess.CompletedProcess(argv, 0, output.encode(), b'')
    monkeypatch.setattr(subprocess, 'run', run)
    assert backend.inspect_images([image])[image]['Architecture'] == 'amd64'
    assert called[0][:3] == ['docker', 'image', 'inspect']


def test_driver_protected_failure_stops_without_scientific_fail(monkeypatch, tmp_path):
    monkeypatch.setattr(driver, 'protected_integrity', lambda *args: (False, ['mutated']))
    _, result, records, _, _ = synthetic_trial(tmp_path, [1, 0])
    # Preserve the predecessor classifier's incomplete-vector precedence.
    assert result['trial_result'] == 'INCOMPLETE_NOT_ELIGIBILITY' and len(records) == 1
    assert records[0]['protected_integrity'] is False


def test_capture_collision_preserves_existing_raw_streams(tmp_path):
    invocation, _, _, _, _ = synthetic_trial(tmp_path, [0])
    with pytest.raises(legacy.InfrastructureFailure, match='capture evidence collision'):
        backend.capture_result(invocation, {'state': 'COMPLETED', 'exit_code': 0,
                                           'stdout': b'would overwrite'}, clock=lambda: 1, started=0)
    assert (invocation.evidence / 'docker_stdout.raw').read_bytes() == b'docker\x00out'


def test_partial_aggregate_timeout_preserves_stream_hashes_without_fabricated_completion(tmp_path):
    invocation, _, _, _, _ = synthetic_trial(tmp_path, [0])
    for stream in ('stdout', 'stderr'):
        (invocation.evidence / f'docker_{stream}.raw').unlink()
    (invocation.evidence / 'capture/subcommands/01/result.json').unlink()
    result = backend.capture_result(invocation, {'state': 'INFRASTRUCTURE_ERROR', 'exit_code': -9,
                                                'infrastructure_subreason': 'ORACLE_TRIAL_TIMEOUT'},
                                    clock=lambda: 900, started=0)
    assert result['trial_result'] == 'INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY'
    assert result['subcommands'][0]['completion_evidence'] == 'MISSING'
    assert result['subcommands'][0]['stdout_sha256'] == legacy.sha256_bytes(b'raw\x00stdout\xff\n')
    assert 'started_at_utc' not in result['subcommands'][0]


def test_common_dry_launch_boundary_cannot_select_real_runner(tmp_path):
    invocation = backend.construct_invocation(case='SYNTHETIC', variant='BUGGY', ordinal=1,
                                              execution_id='fake', image='sha256:' + 'a' * 64,
                                              evidence=tmp_path, commands=['pytest'], protected=[])
    sentinel = Mock(return_value='sentinel')
    assert backend.dispatch(invocation, dry_run=True, binding={}, sentinel=sentinel) == 'sentinel'
    with pytest.raises(legacy.InfrastructureFailure):
        backend.dispatch(invocation, dry_run=True, binding={}, sentinel=sentinel, runner=Mock())


def test_production_trial_preparation_and_evidence_capture_with_fake_git_and_process(monkeypatch, tmp_path):
    data = b'benchmark-owned synthetic protected bytes'
    digest = legacy.sha256_bytes(data)
    manifest_path = tmp_path / 'protected.json'
    save(manifest_path, {'entries': [{'path': 'test_sample.py', 'buggy_effective_sha256': digest,
                                     'fixed_sha256': digest, 'buggy_test_injection_from_fixed': False}]})
    root = tmp_path / 'synthetic-trial'
    invocation = backend.construct_invocation(
        case='SYNTHETIC', variant='BUGGY', ordinal=1, execution_id='fake',
        image='sha256:' + 'a' * 64, evidence=root,
        commands=['pytest -q test_sample.py'], protected=[{'path': 'test_sample.py', 'sha256': digest}])
    git_calls = []
    def fake_clone(argv):
        git_calls.append(argv)
        workspace = Path(argv[-1])
        workspace.mkdir()
        (workspace / 'test_sample.py').write_bytes(data)
    monkeypatch.setattr(legacy, '_run', fake_clone)
    monkeypatch.setattr(legacy, '_git', lambda *args, **kwargs: Mock(stdout=''))
    monkeypatch.setattr(driver, 'protected_integrity', lambda *args: (True, []))
    def runner(inv, remaining):
        assert remaining() > 0
        def process(argv, **kwargs):
            kwargs['stdout'].write(b'raw synthetic stdout')
            kwargs['stderr'].write(b'raw synthetic stderr')
            return Mock(wait=Mock(return_value=0))
        driver.run_trial(inv.request, root / 'capture', process_factory=process)
        return {'state': 'COMPLETED', 'exit_code': 0, 'stdout': b'container out', 'stderr': b''}
    binding = {'case_id': 'SYNTHETIC', 'revision_label': 'BUGGY', 'ordinal': 1,
               'revision_sha': 'b' * 40}
    item = {'current_plan': {'project': 'SYNTHETIC', 'subject_mirror_path': str(tmp_path / 'fake.git'),
                             'fixed_commit_full': 'c' * 40},
            'protected_manifest_path': str(manifest_path)}
    record = v.execute_trial(invocation, binding, item, runner=runner)
    assert git_calls[0][:4] == ('git', 'clone', '--no-checkout', '--shared')
    assert record['state'] == 'ORACLE_COMPLETED' and record['trial_result'] == 'TRIAL_PASS'
    assert record['trial_evidence_sha256'] == legacy.deterministic_trial_evidence_hash(record)
    assert (root / 'input.json').is_file() and (root / 'trial_evidence.json').is_file()
    assert Path(record['subcommands'][0]['stdout_artifact']).read_bytes() == b'raw synthetic stdout'

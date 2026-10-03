"""Docker process boundary for the V5 executor. No eligibility aggregation.

Constructing an invocation is pure. The production subprocess adapter is never
selected by dry validation; real execution additionally requires the V5 executor
lifecycle gate. Subject commands run as direct argv in one fresh trial container.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import signal
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from . import executor as legacy


DRIVER = Path(__file__).with_name('oracle_trial_driver_v1.py')


@dataclass(frozen=True)
class Invocation:
    argv: tuple[str, ...]
    container_name: str
    evidence: Path
    request: dict[str, Any]


def construct_invocation(*, case: str, variant: str, ordinal: int, execution_id: str,
                         image: str, evidence: Path, commands: list[str],
                         protected: list[dict[str, str]]) -> Invocation:
    if re.fullmatch('sha256:[a-f0-9]{64}', image) is None:
        raise legacy.InfrastructureFailure('immutable governed Docker image ID required')
    name = 'ep-oracle-' + hashlib.sha256(
        f'{case}|{variant}|{ordinal}|{execution_id}'.encode()
    ).hexdigest()[:32]
    request = {
        'commands': [{'text': text, 'argv': list(legacy.parse_recognized_command(text))}
                     for text in commands],
        'cwd': '/subject', 'protected': protected,
        'subcommand_timeout_seconds': legacy.SUBCOMMAND_TIMEOUT_SECONDS,
        'trial_timeout_seconds': legacy.TRIAL_TIMEOUT_SECONDS,
    }
    argv = (
        'docker', 'run', '--rm', '--name', name, '--cidfile', str(evidence / 'container.id'),
        '--platform', 'linux/amd64', '--network=none', '--read-only',
        '--mount', f'type=bind,src={evidence / "workspace"},dst=/subject',
        '--mount', f'type=bind,src={DRIVER},dst=/__oracle/driver.py,readonly',
        '--mount', f'type=bind,src={evidence / "input.json"},dst=/__oracle/input.json,readonly',
        '--mount', f'type=bind,src={evidence / "capture"},dst=/__oracle/evidence',
        '--tmpfs', '/__oracle/ephemeral:rw,mode=1777',
        '--env', 'HOME=/__oracle/ephemeral/home', '--env', 'TMPDIR=/__oracle/ephemeral/tmp',
        '--env', 'XDG_CACHE_HOME=/__oracle/ephemeral/cache',
        '--env', 'PYTHONDONTWRITEBYTECODE=1', '--workdir', '/subject',
        '--entrypoint', 'python', image, '/__oracle/driver.py',
    )
    return Invocation(argv, name, evidence, request)


def inspect_images(images: list[str]) -> dict[str, dict[str, Any]]:
    """Read-only metadata; no pull/run/create fallback."""
    result = subprocess.run(
        ['docker', 'image', 'inspect', '--format',
         '{{json .Id}} {{json .Os}} {{json .Architecture}} {{json .RootFS}}', *images],
        capture_output=True, check=False, timeout=60,
    )
    if result.returncode:
        raise legacy.InfrastructureFailure('governed Docker image missing/inspect failed')
    decoder = json.JSONDecoder()
    observations = {}
    for line in result.stdout.decode('utf-8').splitlines():
        fields, rest = [], line
        while rest.strip():
            rest = rest.lstrip()
            value, end = decoder.raw_decode(rest)
            fields.append(value)
            rest = rest[end:]
        image, system, arch, rootfs = fields
        if image in observations:
            raise legacy.InfrastructureFailure('duplicate Docker image observation')
        observations[image] = {'Id': image, 'Os': system, 'Architecture': arch, 'RootFS': rootfs}
    if set(observations) != set(images):
        raise legacy.InfrastructureFailure('Docker image observation population mismatch')
    return observations


class DockerProcessRunner:
    """The only real Docker launch adapter; used only after explicit lifecycle authority."""

    def __call__(self, invocation: Invocation, remaining: Callable[[], float]) -> dict[str, Any]:
        process = None
        try:
            if remaining() <= 0:
                return {'state': 'INFRASTRUCTURE_ERROR', 'exit_code': None,
                        'stdout': b'', 'stderr': b'',
                        'infrastructure_subreason': 'ORACLE_TRIAL_TIMEOUT'}
            process = subprocess.Popen(invocation.argv, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, start_new_session=True, shell=False)
            stdout, stderr = process.communicate(timeout=max(0, remaining()))
            return {'state': 'COMPLETED', 'exit_code': process.returncode,
                    'stdout': stdout, 'stderr': stderr}
        except subprocess.TimeoutExpired:
            self.terminate_and_reap(invocation, process)
            stdout, stderr = process.communicate()
            return {'state': 'INFRASTRUCTURE_ERROR', 'exit_code': process.returncode,
                    'stdout': stdout, 'stderr': stderr,
                    'infrastructure_subreason': 'ORACLE_TRIAL_TIMEOUT'}
        except BaseException as exc:
            if process is not None:
                self.terminate_and_reap(invocation, process)
                stdout, stderr = process.communicate()
            else:
                stdout, stderr = b'', b''
            return {'state': 'INTERRUPTED' if isinstance(exc, KeyboardInterrupt)
                    else 'INFRASTRUCTURE_ERROR', 'stdout': stdout, 'stderr': stderr,
                    'exit_code': None, 'detail': str(exc)}

    def terminate_and_reap(self, invocation: Invocation, process: Any) -> None:
        # CLI process-group termination alone does not terminate daemon-owned children.
        killed = subprocess.run(['docker', 'kill', invocation.container_name],
                                capture_output=True, check=False, timeout=30)
        removed = subprocess.run(['docker', 'rm', '--force', invocation.container_name],
                                 capture_output=True, check=False, timeout=30)
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
        if killed.returncode and removed.returncode:
            raise legacy.InfrastructureFailure('container termination/reaping not confirmed')


def dispatch(invocation: Invocation, *, dry_run: bool, binding: dict[str, Any],
             sentinel: Callable[..., Any] | None = None,
             remaining: Callable[[], float] | None = None,
             runner: Callable[..., dict[str, Any]] | None = None) -> Any:
    """Common production launch boundary. Dry mode cannot construct a process runner."""
    if dry_run:
        if sentinel is None or runner is not None:
            raise legacy.InfrastructureFailure('non-executing launch sentinel required')
        return sentinel(invocation, binding)
    if remaining is None or sentinel is not None:
        raise legacy.InfrastructureFailure('invalid production launch boundary')
    return (runner or DockerProcessRunner())(invocation, remaining)


def capture_result(invocation: Invocation, launch: dict[str, Any], *,
                   clock: Callable[[], float], started: float) -> dict[str, Any]:
    """Hash raw streams after the trial clock stops; never derive results from prose."""
    elapsed = clock() - started
    root = invocation.evidence
    if any((root / f'docker_{stream}.raw').exists() for stream in ('stdout', 'stderr')):
        raise legacy.InfrastructureFailure('result capture evidence collision')
    for stream in ('stdout', 'stderr'):
        data = launch.get(stream, b'')
        if not isinstance(data, bytes):
            raise legacy.InfrastructureFailure('raw Docker stream must be bytes')
        with (root / f'docker_{stream}.raw').open('xb') as handle:
            handle.write(data)
    capture = root / 'capture'
    records = []
    for ordinal, command in enumerate(invocation.request['commands'], 1):
        subroot = capture / 'subcommands' / f'{ordinal:02d}'
        if not (subroot / 'result.json').exists():
            if subroot.exists():
                partial = {'command_ordinal': ordinal, 'command': command['text'],
                           'command_sha256': legacy.sha256_bytes(command['text'].encode()),
                           'argv': command['argv'], 'cwd': '/subject',
                           'state': 'INTERRUPTED' if launch['state'] == 'INTERRUPTED'
                           else 'INFRASTRUCTURE_ERROR',
                           'infrastructure_reason': 'OTHER_INFRASTRUCTURE_FAILURE',
                           'infrastructure_subreason': 'ORACLE_TRIAL_TIMEOUT' if elapsed >= 900
                           else launch.get('infrastructure_subreason'),
                           'completion_evidence': 'MISSING', 'exit_code': None}
                for stream in ('stdout', 'stderr'):
                    path = subroot / f'{stream}.raw'
                    if path.is_file() and not path.is_symlink():
                        partial[f'{stream}_artifact'] = str(path)
                        partial[f'{stream}_sha256'] = legacy.sha256_file(path)
                records.append(partial)
            break
        if (subroot / 'result.json').is_symlink():
            raise legacy.InfrastructureFailure('ambiguous subcommand evidence')
        record = json.loads((subroot / 'result.json').read_bytes())
        if (record.get('command_ordinal') != ordinal or record.get('command') != command['text']
                or record.get('argv') != command['argv'] or record.get('cwd') != '/subject'
                or record.get('command_sha256') != legacy.sha256_bytes(command['text'].encode())):
            raise legacy.InfrastructureFailure('container subcommand evidence identity mismatch')
        for stream in ('stdout', 'stderr'):
            path = subroot / f'{stream}.raw'
            if not path.is_file() or path.is_symlink():
                raise legacy.InfrastructureFailure('missing raw subcommand evidence')
            record[f'{stream}_artifact'] = str(path)
            record[f'{stream}_sha256'] = legacy.sha256_file(path)
        records.append(record)
        if record['state'] != 'ORACLE_COMPLETED' or not record.get('protected_integrity'):
            break
    result = legacy.classify_trial_commands(records, len(invocation.request['commands']))
    if launch['state'] != 'COMPLETED' or launch.get('exit_code') != 0 or elapsed >= 900:
        result = ('INTERRUPTED_NOT_ELIGIBILITY' if launch['state'] == 'INTERRUPTED'
                  else 'INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY')
    return {
        'trial_result': result, 'subcommands': records,
        'oracle_commands': [c['text'] for c in invocation.request['commands']],
        'exit_codes': [r.get('exit_code') for r in records],
        'subcommand_artifacts': [{'stdout': r.get('stdout_artifact'),
                                 'stderr': r.get('stderr_artifact')} for r in records],
        'infrastructure_subreason': ('ORACLE_TRIAL_TIMEOUT' if elapsed >= 900 else
                                    launch.get('infrastructure_subreason') or next(
                                        (r.get('infrastructure_subreason') for r in records
                                         if r.get('infrastructure_subreason')), None)),
        'docker_invocation': list(invocation.argv),
        'docker_exit_code': launch.get('exit_code'),
        'docker_stdout_sha256': legacy.sha256_file(root / 'docker_stdout.raw'),
        'docker_stderr_sha256': legacy.sha256_file(root / 'docker_stderr.raw'),
        'executor_interrupted': launch['state'] == 'INTERRUPTED',
        'timeout_state': elapsed >= 900 or launch.get('infrastructure_subreason') in (
            'ORACLE_TRIAL_TIMEOUT', 'ORACLE_SUBCOMMAND_TIMEOUT') or any(
                r.get('infrastructure_subreason') in ('ORACLE_TRIAL_TIMEOUT', 'ORACLE_SUBCOMMAND_TIMEOUT')
                for r in records),
        'combined_output_available': False, 'wall_time_seconds': elapsed,
    }

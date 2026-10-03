"""Container-side ordered direct-argv runner; compatible with governed Python 3.6.

Imported by synthetic tests without executing anything. Only the explicitly
launched container entry point calls main. The host owns the complete 900 s
startup/teardown deadline; this driver additionally bounds each command/process
group and never resets its own remaining trial budget.
"""

import hashlib
import json
import os
import signal
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def protected_integrity(workspace, entries):
    failures = []
    for entry in entries:
        path = Path(workspace) / entry['path']
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
            failures.append(entry['path'])
    return not failures, failures


def run_trial(request, evidence, *, process_factory=subprocess.Popen,
              clock=time.monotonic, kill_group=os.killpg, stamp=utc_now):
    """No shell, retries, eligibility aggregation, or continuation after faults."""
    evidence = Path(evidence)
    deadline = clock() + request['trial_timeout_seconds']
    records = []
    for ordinal, command in enumerate(request['commands'], 1):
        root = evidence / 'subcommands' / ('%02d' % ordinal)
        root.mkdir(parents=True, exist_ok=False)
        started = clock()
        record = {
            'command_ordinal': ordinal, 'command': command['text'],
            'command_sha256': hashlib.sha256(command['text'].encode('utf-8')).hexdigest(),
            'argv': command['argv'], 'cwd': request['cwd'],
            'started_at_utc': stamp(), 'exit_code': None,
        }
        remaining = deadline - started
        command_deadline = started + request['subcommand_timeout_seconds']
        reason = ('ORACLE_TRIAL_TIMEOUT' if deadline <= command_deadline
                  else 'ORACLE_SUBCOMMAND_TIMEOUT')
        process = None
        with (root / 'stdout.raw').open('xb') as stdout, (root / 'stderr.raw').open('xb') as stderr:
            try:
                if remaining <= 0:
                    raise subprocess.TimeoutExpired(command['argv'], 0)
                process = process_factory(command['argv'], cwd=request['cwd'],
                                          stdout=stdout, stderr=stderr,
                                          start_new_session=True, shell=False)
                code = process.wait(timeout=max(0, min(command_deadline, deadline) - clock()))
                record['exit_code'] = code
                if clock() >= deadline:
                    reason = 'ORACLE_TRIAL_TIMEOUT'
                    raise subprocess.TimeoutExpired(command['argv'], 0)
                if clock() >= command_deadline:
                    raise subprocess.TimeoutExpired(command['argv'], 0)
                intact, failures = protected_integrity(request['cwd'], request['protected'])
                record.update(state='ORACLE_COMPLETED' if code >= 0 else 'INTERRUPTED',
                              protected_integrity=intact, protected_integrity_failures=failures)
                if clock() >= min(command_deadline, deadline):
                    raise subprocess.TimeoutExpired(command['argv'], 0)
            except subprocess.TimeoutExpired:
                if process is not None:
                    try:
                        kill_group(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    record['exit_code'] = process.wait()
                record.update(state='INFRASTRUCTURE_ERROR',
                              infrastructure_reason='OTHER_INFRASTRUCTURE_FAILURE',
                              infrastructure_subreason=reason)
            except BaseException as exc:
                if process is not None:
                    try:
                        kill_group(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    record['exit_code'] = process.wait()
                record.update(state='INTERRUPTED' if isinstance(exc, KeyboardInterrupt)
                              else 'INFRASTRUCTURE_ERROR', detail=str(exc))
        record.update(ended_at_utc=stamp(), wall_time_seconds=clock() - started)
        records.append(record)
        # Append-only per-command completion survives interruption of the trial.
        with (root / 'result.json').open('x') as handle:
            json.dump(record, handle, sort_keys=True, separators=(',', ':'))
            handle.write('\n')
        if record['state'] != 'ORACLE_COMPLETED' or not record.get('protected_integrity'):
            break
    return records


def main():
    request = json.loads(Path('/__oracle/input.json').read_text())
    for name in ('home', 'tmp', 'cache'):
        Path('/__oracle/ephemeral', name).mkdir(parents=True, exist_ok=False)
    records = run_trial(request, '/__oracle/evidence')
    with Path('/__oracle/evidence/driver_result.json').open('x') as handle:
        json.dump({'subcommands': records}, handle, sort_keys=True, separators=(',', ':'))
        handle.write('\n')


if __name__ == '__main__':
    main()

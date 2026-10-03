"""Versioned V5 extension at the frozen execute_case boundary.

The predecessor executor/materializer bytes remain frozen. This extension reuses
their fixed schedule, command parser, integrity checks and classifiers, while V5
plan selection is exclusively the explicit Human-PI current-plan manifest.
Preparation and dry validation never select the production process runner.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from . import docker_oracle_backend_v1 as docker
from . import executor as legacy
from . import validate_pre_eligibility_state_v5 as v5


BASELINE = '86fb1021e2504f00fa2a9dfcdc25ab95a307e41c'
WORK = Path('/Users/wuyangchenxi/errpilot-benchmark-work')
BENCHMARK = Path(__file__).resolve().parents[1]
NAMESPACE = WORK / 'oracle_plans/v1_1'
MANIFEST = NAMESPACE / 'current_plan_manifest_v1.json'
AUTHORITY = BENCHMARK / 'v5_oracle_execution_readiness_bridge_v1.json'
INITIAL = (
    'pandas::102', 'pandas::78', 'pandas::4', 'pandas::45', 'matplotlib::17',
    'matplotlib::11', 'keras::28', 'youtube-dl::7', 'black::17', 'httpie::1',
    'fastapi::2', 'youtube-dl::37', 'youtube-dl::18', 'fastapi::13', 'black::16',
    'httpie::3', 'matplotlib::29', 'fastapi::11', 'httpie::4',
)
NEWER = ('matplotlib::21', 'youtube-dl::24', 'black::6', 'black::15', 'fastapi::12',
         'httpie::5', 'PySnooper::1', 'PySnooper::3', 'PySnooper::2')
CONTRACTS = {
    'PROTOCOL.md': legacy.PROTOCOL_SHA256,
    'RUN_SPEC_V1.md': legacy.RUN_SPEC_SHA256,
    'SCREENING_SPEC_V1.md': 'a7f3cd5e73d6c733f560456d9f3949be18deca9b295ffb4ef2ae087af7e89db3',
    'ORACLE_REPRESENTATION_V1.md': '625b656495b5f1174ea1f4a07f872a42112a0be839b47c3db884dcd103a87f52',
    'SCREENING_RUNTIME_V1.md': '235b404dd32da91f28c303922ce7acfc8f58611cd78f3c365d583cb2572bb41f',
}
TIMEOUT = {
    'subcommand_timeout_seconds': 300, 'trial_timeout_seconds': 900,
    'authority': 'SCREENING_RUNTIME_V1.md#B',
    'authority_sha256': CONTRACTS['SCREENING_RUNTIME_V1.md'],
    'scope': 'subcommand and complete trial including startup/teardown; no clock reset',
    'termination': 'terminate and reap process group or complete container',
}
PRE_EXECUTION_TIMEOUT_GATE_REQUIRED = legacy.PRE_EXECUTION_TIMEOUT_GATE_REQUIRED
PRODUCTION_DOCKER_BACKEND_IMPLEMENTED = True


def require(condition: bool, message: str) -> None:
    if not condition:
        raise legacy.InfrastructureFailure(message)


def read_bytes(path: Path) -> bytes:
    require(path.is_file() and not path.is_symlink(), f'missing/ambiguous artifact: {path}')
    require(path.resolve() == path.absolute(), f'symlinked artifact path: {path}')
    return path.read_bytes()


def read_json(path: Path) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result = {}
        for key, value in pairs:
            require(key not in result, f'duplicate JSON key: {key}')
            result[key] = value
        return result
    try:
        value = json.loads(read_bytes(path), object_pairs_hook=unique)
    except (ValueError, OSError) as exc:
        raise legacy.InfrastructureFailure(f'malformed JSON: {path}') from exc
    require(isinstance(value, dict), f'JSON object required: {path}')
    return value


def rows(benchmark: Path, name: str) -> list[dict[str, str]]:
    with (benchmark / name).open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def load_population(benchmark: Path = BENCHMARK, work: Path = WORK) -> list[dict[str, Any]]:
    """Reconstruct frozen admissions minus V5 exclusions and materialization ledgers."""
    for name, digest in CONTRACTS.items():
        require(legacy.sha256_bytes(read_bytes(benchmark / name)) == digest,
                f'frozen contract identity mismatch: {name}')
    v5.validate_successor(benchmark)
    plans, groups, admitted = {}, {}, []
    for group, name in enumerate(('screening_execution_plan.csv',
                                  'expansion_block_01_execution_plan.csv',
                                  'expansion_block_02_execution_plan.csv',
                                  'expansion_block_03_execution_plan.csv')):
        for row in rows(benchmark, name):
            case = row['canonical_case_id']
            require(case not in plans, 'duplicate admission')
            plans[case], groups[case] = row, group
            admitted.append(case)
    excluded = {row['case_id'] for row in rows(benchmark, 'exclusions_v5.csv')}
    ready = [case for case in admitted if case not in excluded]
    require(len(admitted) == 67 and len(excluded) == 39 and ready == list(INITIAL + NEWER),
            'V5 population/order mismatch')
    environments = {}

    def add(case: str, label: str, path: Path, digest: str) -> None:
        require((case, label) not in environments, 'duplicate governed environment')
        require(legacy.sha256_bytes(read_bytes(path)) == digest, 'environment hash mismatch')
        identity = read_json(path)
        require(all(identity.get(k) not in (None, '', 'UNBUILT')
                    for k in legacy.ENVIRONMENT_IDENTITY_V1_FIELDS), 'incomplete environment')
        require(identity['canonical_case_id'] == case and identity['revision_label'] == label
                and identity['runtime_backend'] == 'docker'
                and identity['runtime_platform'] == 'linux/amd64'
                and identity['network_execution_policy'] == 'NONE'
                and identity['screening_runtime_spec_sha256'] == CONTRACTS['SCREENING_RUNTIME_V1.md']
                and identity['execution_plan_sha256'] == plans[case]['execution_plan_sha256'],
                'governed environment binding mismatch')
        environments[case, label] = {
            'path': str(path), 'sha256': digest, 'identity': identity,
        }

    for batch in range(1, 5):
        for row in rows(benchmark, f'environment_materialization_batch_0{batch}.csv'):
            if row['materialization_status'] == 'MATERIALIZED':
                add(row['canonical_case_id'], row['revision_label'],
                    Path(row['external_evidence_reference']) / 'environment_identity.json',
                    row['environment_identity_sha256'])
    completion = rows(benchmark, 'environment_materialization_batch_01_identity_completion.csv')[0]
    require(completion['effective_environment_status'] == 'MATERIALIZED', 'keras completion mismatch')
    add('keras::28', 'SOURCE_INDEPENDENT',
        benchmark / 'evidence/batch_01_keras28_identity_completion/environment_identity.json',
        completion['screening_environment_identity_v1_sha256'])
    for block in (1, 2):
        for row in rows(benchmark, f'expansion_block_0{block}_environment_materialization.csv'):
            if row['status'] == 'MATERIALIZED':
                add(row['canonical_case_id'], row['revision_label'],
                    Path(row['evidence_path']) / row['revision_label'] / 'environment_identity.json',
                    row['environment_identity_sha256'])
    first_pass = read_json(benchmark / 'evidence/block_03_materialization_outcome_v5/first_pass_evidence.json')
    for row in first_pass['identities']:
        if row['status'] == 'MATERIALIZED':
            add(row['case_id'], row['revision_label'],
                Path(first_pass['production_root']) / Path(row['attempt_path']).parent
                / row['revision_label'] / 'environment_identity.json', row['environment_identity_sha256'])
    require({c for c, _ in environments} == set(ready), 'environment-ready population mismatch')
    population = []
    for case in ready:
        row, group = plans[case], groups[case]
        preparation = (work / f'expansion_block_0{group}_preparation' / case.replace('::', '__')
                       if group else work / 'screening_workspaces' / legacy.safe_case_slug(case)
                       / 'preparation')
        plan_path = preparation / ('preparation_plan.json' if group else 'execution_plan.json')
        plan = read_json(plan_path)
        require(plan.get('execution_plan_sha256') == legacy.deterministic_plan_hash(plan),
                'predecessor/preparation plan identity mismatch')
        script_path = preparation / 'oracle/run_test.sh'
        script = read_bytes(script_path)
        oracle = legacy.analyze_oracle(script)
        commands = json.loads(row['oracle_commands'])
        require(legacy.sha256_bytes(script) == row['oracle_script_sha256']
                and oracle['status'] == 'RESOLVED_ORDERED_COMMANDS'
                and oracle['commands'] == commands
                and len(commands) == int(row['oracle_command_count']), 'frozen oracle mismatch')
        manifest_path = preparation / 'protected_manifest.json'
        protected = read_json(manifest_path)
        require(protected['status'] == 'RESOLVED'
                and protected['canonical_case_id'] == case
                and protected['manifest_sha256'] == plan['protected_manifest_sha256'],
                'protected manifest mismatch')
        if group:
            require(plan['execution_plan_sha256'] == row['execution_plan_sha256']
                    and plan['oracle_plan_status'] == 'RESOLVED_ORDERED_COMMANDS'
                    and plan['oracle_commands'] == commands, 'newer plan actually stale')
        else:
            require(plan['schema_version'] == 1, 'unexpected initial predecessor version')
        labels = {label for c, label in environments if c == case}
        require(labels in ({'SOURCE_INDEPENDENT'}, {'BUGGY', 'FIXED'}), 'incomplete variant pair')
        bindings = {}
        for variant in ('BUGGY', 'FIXED'):
            source = row[variant.lower() + '_commit_full']
            require(re.fullmatch('[a-f0-9]{40}', source) is not None
                    and plan[variant.lower() + '_commit_full'] == source, 'source binding mismatch')
            label = 'SOURCE_INDEPENDENT' if labels == {'SOURCE_INDEPENDENT'} else variant
            env = environments[case, label]
            require(env['identity']['revision_sha'] == ('ABSENT' if label == 'SOURCE_INDEPENDENT'
                                                       else source), 'environment/source mismatch')
            bindings[variant] = {'source_revision': source,
                                 'environment_identity_path': env['path'],
                                 'environment_identity_sha256': env['sha256'],
                                 'environment_image_id': env['identity']['environment_image_digest'],
                                 'materialized_environment_label': label}
        population.append({'case_id': case, 'group': group, 'row': row, 'plan': plan,
                           'plan_path': str(plan_path), 'plan_sha256': legacy.sha256_file(plan_path),
                           'script_path': str(script_path), 'protected_manifest_path': str(manifest_path),
                           'protected_manifest_file_sha256': legacy.sha256_file(manifest_path),
                           'bindings': bindings, 'oracle': oracle})
    return population


def derive_bundle(population: list[dict[str, Any]], namespace: Path = NAMESPACE
                  ) -> dict[Path, bytes]:
    """Pure mechanical per-case successor derivation; never rewrites a predecessor."""
    require([p['case_id'] for p in population] == list(INITIAL + NEWER), 'exact V5 population required')
    files, entries = {}, []
    for item in population:
        case, original = item['case_id'], item['plan']
        predecessor = None
        if case in INITIAL:
            plan = dict(original)
            oracle = item['oracle']
            require(original['oracle_plan_status'] in (
                'RESOLVED_SINGLE_COMMAND', 'UNRESOLVED_MULTIPLE_SUBSTANTIVE_COMMANDS'),
                'unexpected historical representation')
            reason = original.get('blocking_reason', '')
            if original['oracle_plan_status'] == 'UNRESOLVED_MULTIPLE_SUBSTANTIVE_COMMANDS':
                require(reason == f"run_test.sh contains {len(oracle['commands'])} substantive commands",
                        'historical additional blocker')
                reason = ''
            plan.update(schema_version='1.1',
                        oracle_representation_version='COMPOSITE_ORACLE_SEMANTICS_V1',
                        oracle_command=oracle['oracle_command'], oracle_commands=oracle['commands'],
                        oracle_command_count=len(oracle['commands']), oracle_plan_status=oracle['status'],
                        oracle_shell_requirement=oracle['shell_requirement'], blocking_reason=reason,
                        screening_ready=not reason and original['protected_manifest_status'] == 'RESOLVED'
                        and original['environment_plan_status'] == 'PLAN_FROZEN_BUILD_REQUIRED',
                        pre_execution_timeout_gate='PRE_EXECUTION_TIMEOUT_GATE_REQUIRED')
            require(legacy.deterministic_plan_hash(plan) == item['row']['execution_plan_sha256'],
                    'mechanically reissued composite core differs from committed plan')
            predecessor = {'path': item['plan_path'], 'sha256': item['plan_sha256'],
                           'execution_plan_sha256': original['execution_plan_sha256']}
            plan['readiness_binding'] = {
                'v5_baseline_commit': BASELINE, 'predecessor': predecessor,
                'frozen_execution_plan_sha256': item['row']['execution_plan_sha256'],
                'environment_bindings': item['bindings'], 'timeout': TIMEOUT,
                'frozen_contract_sha256': CONTRACTS,
            }
            plan['execution_plan_sha256'] = legacy.deterministic_plan_hash(plan)
            selected = namespace / legacy.safe_case_slug(case) / 'execution_plan.json'
            data = legacy.canonical_json_bytes(plan)
            files[selected] = data
            version = '1.1'
        else:
            plan, selected = original, Path(item['plan_path'])
            data = read_bytes(selected)
            version = plan['schema']
        entries.append({
            'case_id': case, 'selected_plan_path': str(selected),
            'selected_plan_sha256': legacy.sha256_bytes(data), 'selected_version': version,
            'execution_plan_sha256': plan['execution_plan_sha256'], 'predecessor': predecessor,
            'environment_bindings': item['bindings'],
        })
    manifest = {
        'schema': 'V5_CURRENT_ORACLE_PLAN_MANIFEST_V1',
        'storage_decision': 'HUMAN_PI_V5_ORACLE_PLAN_STORAGE_DECISION_V1',
        'v5_baseline_commit': BASELINE, 'frozen_contract_sha256': CONTRACTS, 'timeout': TIMEOUT,
        'execution_order': [{'revision': s.revision_label, 'ordinal': s.ordinal}
                            for s in legacy.build_execution_schedule()],
        'execution_authorized': False, 'cases': entries,
    }
    files[namespace / 'current_plan_manifest_v1.json'] = legacy.canonical_json_bytes(manifest)
    return files


def write_exclusive_bundle(files: dict[Path, bytes], namespace: Path = NAMESPACE) -> None:
    # Check every collision before the first write; compatible files may be reused.
    require(namespace.resolve() == namespace.absolute(), 'ambiguous successor namespace')
    for path, data in files.items():
        require(path.is_relative_to(namespace), 'successor outside authorized namespace')
        require(path.resolve() == path.absolute(), 'ambiguous successor path')
        if path.exists():
            require(read_bytes(path) == data, f'conflicting existing successor artifact: {path}')
    for path, data in files.items():
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as handle:
                handle.write(data)


@dataclass(frozen=True)
class CurrentPopulation:
    manifest_path: Path
    manifest_sha256: str
    cases: dict[str, dict[str, Any]]


def resolve_current_population(*, benchmark: Path = BENCHMARK, work: Path = WORK,
                               manifest_path: Path = MANIFEST,
                               population: list[dict[str, Any]] | None = None) -> CurrentPopulation:
    """No latest/mtime/lexical selection or fallback. Revalidate every selected byte."""
    inputs = load_population(benchmark, work) if population is None else population
    expected_files = derive_bundle(inputs, manifest_path.parent)
    expected_manifest = json.loads(expected_files[manifest_path])
    manifest = read_json(manifest_path)
    require(manifest == expected_manifest, 'V5 manifest selection/timeout/population mismatch')
    resolved = {}
    for entry, item in zip(manifest['cases'], inputs):
        path = Path(entry['selected_plan_path'])
        data = read_bytes(path)
        require(legacy.sha256_bytes(data) == entry['selected_plan_sha256'], 'selected plan hash mismatch')
        if item['case_id'] in INITIAL:
            require(data == expected_files[path], 'successor/lineage/core mismatch')
        plan = read_json(path)
        require(legacy.deterministic_plan_hash(plan) == entry['execution_plan_sha256'],
                'selected plan deterministic identity mismatch')
        resolved[entry['case_id']] = dict(item, selected=entry, current_plan=plan)
    return CurrentPopulation(manifest_path, legacy.sha256_file(manifest_path), resolved)


def validate_timeout(timeout: dict[str, Any]) -> None:
    require(PRE_EXECUTION_TIMEOUT_GATE_REQUIRED is True, 'frozen timeout gate was weakened')
    require(timeout == TIMEOUT
            and type(timeout.get('subcommand_timeout_seconds')) is int
            and type(timeout.get('trial_timeout_seconds')) is int, 'missing/mismatched timeout authority')


def preflight_slot(current: CurrentPopulation, *, case: str, variant: str, ordinal: int,
                   execution_id: str, images: dict[str, dict[str, Any]],
                   work: Path = WORK, seen: set[tuple[str, str, int]] | None = None
                   ) -> tuple[docker.Invocation, dict[str, Any]]:
    require(case in current.cases, 'case outside current V5 population')
    require(variant in ('BUGGY', 'FIXED') and type(ordinal) is int and ordinal in (1, 2, 3),
            'wrong variant/repetition')
    require(re.fullmatch('[A-Za-z0-9][A-Za-z0-9._-]{0,127}', execution_id) is not None,
            'unsafe execution identity')
    require(legacy.sha256_file(current.manifest_path) == current.manifest_sha256,
            'manifest changed after resolution')
    item = current.cases[case]
    entry, plan, row = item['selected'], item['current_plan'], item['row']
    path = Path(entry['selected_plan_path'])
    require(legacy.sha256_bytes(read_bytes(path)) == entry['selected_plan_sha256']
            and read_json(path) == plan, 'selected plan changed/wrong identity')
    commands = json.loads(row['oracle_commands'])
    require(plan['canonical_case_id'] == case and plan['oracle_commands'] == commands
            and plan['oracle_command_count'] == len(commands)
            and plan['oracle_plan_status'] == 'RESOLVED_ORDERED_COMMANDS', 'oracle representation mismatch')
    require(plan.get('oracle_cwd', 'subject repository root') == 'subject repository root',
            'wrong oracle cwd')
    script = read_bytes(Path(item['script_path']))
    require(legacy.sha256_bytes(script) == row['oracle_script_sha256']
            and legacy.analyze_oracle(script)['commands'] == commands, 'oracle source drift')
    manifest = read_json(current.manifest_path)
    require(manifest['v5_baseline_commit'] == BASELINE
            and manifest['frozen_contract_sha256'] == CONTRACTS
            and entry == next(e for e in manifest['cases'] if e['case_id'] == case),
            'V5 selected plan/environment authority changed')
    validate_timeout(manifest.get('timeout', {}))
    binding = entry['environment_bindings'][variant]
    environment_path = Path(binding['environment_identity_path'])
    require(legacy.sha256_bytes(read_bytes(environment_path)) == binding['environment_identity_sha256'],
            'environment hash mismatch')
    identity = read_json(environment_path)
    require(identity['canonical_case_id'] == case
            and identity['revision_label'] == binding['materialized_environment_label']
            and identity['revision_sha'] == ('ABSENT' if identity['revision_label'] == 'SOURCE_INDEPENDENT'
                                             else binding['source_revision'])
            and identity['execution_plan_sha256'] == row['execution_plan_sha256']
            and identity['environment_image_digest'] == binding['environment_image_id']
            and identity['runtime_backend'] == 'docker' and identity['runtime_platform'] == 'linux/amd64'
            and identity['network_execution_policy'] == 'NONE'
            and identity['screening_runtime_spec_sha256'] == TIMEOUT['authority_sha256'],
            'environment/variant/plan authority mismatch')
    image = binding['environment_image_id']
    require(re.fullmatch('sha256:[a-f0-9]{64}', image) is not None and image in images,
            'missing/nonimmutable Docker image')
    observed = images[image]
    require(observed['Id'] == image and observed['Os'] == 'linux' and observed['Architecture'] == 'amd64'
            and legacy.sha256_bytes(legacy.canonical_json_bytes(observed['RootFS']['Layers']))
            == identity['environment_tree_or_rootfs_identity'], 'Docker image identity mismatch')
    key = case, variant, ordinal
    require(seen is None or key not in seen, 'duplicate repetition')
    case_evidence = work / 'screening_evidence' / legacy.safe_case_slug(case)
    attempt = case_evidence / execution_id
    # This bridge provides no retry path. Any different prior attempt blocks as well.
    require(not case_evidence.exists() or all(p == attempt for p in case_evidence.iterdir()),
            'prior oracle attempt: new Human-PI authority required')
    schedule_index = list(legacy.build_execution_schedule()).index(legacy.ScheduledRun(variant, ordinal)) + 1
    evidence = attempt / 'runs' / f'{schedule_index:02d}-{variant.lower()}-{ordinal}'
    require(evidence.resolve() == evidence.absolute() and not evidence.exists(),
            'evidence collision/ambiguous destination')
    require(',' not in str(evidence) and ',' not in str(docker.DRIVER), 'unsafe Docker mount encoding')
    protected_path = Path(item['protected_manifest_path'])
    require(legacy.sha256_bytes(read_bytes(protected_path)) == item['protected_manifest_file_sha256'],
            'protected manifest drift')
    protected = read_json(protected_path)
    protected_key = 'buggy_effective_sha256' if variant == 'BUGGY' else 'fixed_sha256'
    entries = [{'path': str(legacy._safe_subject_path(e['path'])), 'sha256': e[protected_key]}
               for e in protected['entries']]
    invocation = docker.construct_invocation(case=case, variant=variant, ordinal=ordinal,
                                             execution_id=execution_id, image=image,
                                             evidence=evidence, commands=commands, protected=entries)
    if seen is not None:
        seen.add(key)
    return invocation, {
        'case_id': case, 'revision_label': variant, 'ordinal': ordinal,
        'execution_id': execution_id,
        'revision_sha': binding['source_revision'], 'environment_identity_sha256': binding[
            'environment_identity_sha256'], 'environment_image_id': image,
        'execution_plan_sha256': entry['execution_plan_sha256'],
        'selected_plan_path': entry['selected_plan_path'], 'selected_version': entry['selected_version'],
        'environment_identity_path': binding['environment_identity_path'],
        'selected_plan_sha256': entry['selected_plan_sha256'], 'manifest_sha256': current.manifest_sha256,
        'timeout': TIMEOUT, 'evidence_path': str(evidence),
    }


def require_execution_authority(authorization: str, authority_path: Path = AUTHORITY) -> None:
    require(authorization == legacy.EXECUTION_AUTHORITY_TOKEN, 'exact execution authority required')
    authority = read_json(authority_path)
    require(authority.get('real_oracle_execution_authorized') is True
            and all(authority.get('lifecycle', {}).get(k) is True for k in (
                'human_pi_accepted', 'frozen', 'persisted', 'committed', 'remote_published')),
            'readiness bridge candidate: real oracle execution remains blocked')
    require(authority['v5_baseline_commit'] == BASELINE
            and authority['manifest_path'] == str(MANIFEST)
            and authority['manifest_sha256'] == legacy.sha256_file(MANIFEST),
            'execution authority/current manifest mismatch')
    repository = BENCHMARK.parents[1]
    relative = authority_path.relative_to(repository).as_posix()
    committed = subprocess.check_output(['git', 'cat-file', 'blob', f'HEAD:{relative}'], cwd=repository)
    require(committed == read_bytes(authority_path), 'execution authority is not committed')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repository).decode().strip()
    remote = subprocess.check_output(['git', 'ls-remote', '--exit-code', 'origin', 'refs/heads/main'],
                                     cwd=repository).decode().split()[0]
    require(head == remote, 'execution authority is not remotely published')
    for name, digest in authority['implementation_sha256'].items():
        path = BENCHMARK / name
        require(legacy.sha256_file(path) == digest, 'accepted implementation changed')
        require(subprocess.check_output(['git', 'cat-file', 'blob',
                                         'HEAD:evaluation/downstream_benchmark/' + name], cwd=repository)
                == read_bytes(path), 'implementation is not committed')


def execute_case(*, case: str, execution_id: str, manifest_path: Path = MANIFEST,
                 dry_run: bool = True, authorization: str = '',
                 sentinel: Callable[[docker.Invocation, dict[str, Any]], Any] | None = None,
                 image_inspector: Callable[[list[str]], dict[str, dict[str, Any]]] = docker.inspect_images,
                 benchmark: Path = BENCHMARK, work: Path = WORK,
                 population: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Versioned canonical case dispatch; default dry, real gate before any write."""
    if not dry_run:
        require_execution_authority(authorization)
        require(population is None and benchmark == BENCHMARK and work == WORK
                and manifest_path == MANIFEST and image_inspector is docker.inspect_images
                and sentinel is None, 'production authority/adapter overrides prohibited')
    current = resolve_current_population(benchmark=benchmark, work=work,
                                         manifest_path=manifest_path, population=population)
    require(case in current.cases, 'case outside V5 population')
    images = image_inspector(sorted({b['environment_image_id'] for b in
                                    current.cases[case]['bindings'].values()}))
    slots, seen = [], set()
    for scheduled in legacy.build_execution_schedule():
        invocation, binding = preflight_slot(current, case=case, variant=scheduled.revision_label,
                                              ordinal=scheduled.ordinal, execution_id=execution_id,
                                              images=images, work=work, seen=seen)
        slots.append((invocation, binding))
    if dry_run:
        require(sentinel is not None, 'non-executing process-boundary sentinel required')
        return [docker.dispatch(invocation, dry_run=True, binding=binding, sentinel=sentinel)
                for invocation, binding in slots]
    attempt_root = slots[0][0].evidence.parent.parent
    attempt_root.mkdir(parents=True, exist_ok=False)
    checkpoint = {'canonical_case_id': case, 'execution_id': execution_id,
                  'state': 'STARTED', 'classification': 'INCOMPLETE_NOT_ELIGIBILITY',
                  'manifest_sha256': current.manifest_sha256, 'started_at_utc': legacy.utc_now(),
                  'schedule': [{'revision_label': s.revision_label, 'ordinal': s.ordinal,
                                'state': 'PENDING'} for s in legacy.build_execution_schedule()],
                  'records': []}
    legacy._atomic_write_json(attempt_root / 'checkpoint.json', checkpoint)
    try:
        for index, (invocation, binding) in enumerate(slots):
            try:
                # Reconcile selected artifacts/images again immediately before each launch.
                refreshed = resolve_current_population(benchmark=benchmark, work=work,
                                                       manifest_path=manifest_path)
                invocation, binding = preflight_slot(
                    refreshed, case=case, variant=binding['revision_label'], ordinal=binding['ordinal'],
                    execution_id=execution_id, images=image_inspector([binding['environment_image_id']]),
                    work=work)
                record = execute_trial(invocation, binding, refreshed.cases[case],
                                       authorization=authorization)
            except Exception as exc:
                record = dict(binding, state='INFRASTRUCTURE_ERROR', detail=str(exc))
            checkpoint['records'].append(record)
            checkpoint['schedule'][index]['state'] = record['state']
            legacy._atomic_write_json(attempt_root / 'checkpoint.json', checkpoint)
            if record.get('executor_interrupted'):
                raise KeyboardInterrupt('executor interrupted; evidence/checkpoint preserved')
        checkpoint.update(state='COMPLETE', ended_at_utc=legacy.utc_now(),
                          classification=legacy.classify_execution_records(checkpoint['records']))
        legacy._atomic_write_json(attempt_root / 'checkpoint.json', checkpoint)
        return checkpoint['records']
    except BaseException:
        checkpoint.update(state='INTERRUPTED', classification='INTERRUPTED_NOT_ELIGIBILITY')
        legacy._atomic_write_json(attempt_root / 'checkpoint.json', checkpoint)
        raise


def execute_trial(invocation: docker.Invocation, binding: dict[str, Any], item: dict[str, Any], *,
                  runner: Callable[..., dict[str, Any]] | None = None,
                  authorization: str = '') -> dict[str, Any]:
    """Fresh workspace preparation is outside the clock; no installation/setup."""
    if runner is None:
        require_execution_authority(authorization)
    root = invocation.evidence
    root.mkdir(parents=True, exist_ok=False)
    workspace = root / 'workspace'
    plan = item['current_plan']
    mirror = Path(plan.get('subject_mirror_path', str(WORK / 'subject_repositories'
                                                   / (plan['project'] + '.git'))))
    legacy._run(('git', 'clone', '--no-checkout', '--shared', str(mirror), str(workspace)))
    legacy._git(workspace, 'checkout', '--detach', binding['revision_sha'])
    require(not legacy._git(workspace, 'status', '--porcelain').stdout.strip(), 'fresh source is dirty')
    protected = read_json(Path(item['protected_manifest_path']))
    legacy._inject_benchmark_owned_tests(workspace, mirror, protected,
                                        binding['revision_label'], plan['fixed_commit_full'])
    intact, failures = legacy._verify_protected_paths(workspace, protected, binding['revision_label'])
    require(intact, f'pre-run protected integrity failure: {failures}')
    (root / 'capture').mkdir()
    with (root / 'input.json').open('xb') as handle:
        handle.write(legacy.canonical_json_bytes(invocation.request))
    record = dict(binding, started_at_utc=legacy.utc_now(), cwd='/subject',
                  fresh_workspace=str(workspace), ephemeral_state='fresh container tmpfs')
    started = time.monotonic()
    launch = docker.dispatch(invocation, dry_run=False, binding=binding, runner=runner,
                             remaining=lambda: 900 - (time.monotonic() - started))
    stopped = time.monotonic()
    record['ended_at_utc'] = legacy.utc_now()
    record.update(docker.capture_result(invocation, launch, clock=lambda: stopped, started=started))
    record['state'] = ('ORACLE_COMPLETED' if record['trial_result'] in ('TRIAL_PASS', 'TRIAL_FAIL')
                       else 'INTERRUPTED' if record['trial_result'] == 'INTERRUPTED_NOT_ELIGIBILITY'
                       else 'INFRASTRUCTURE_ERROR' if record['trial_result']
                       == 'INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY' else 'CASE_INVALIDATED')
    record['trial_evidence_sha256'] = legacy.deterministic_trial_evidence_hash(record)
    legacy._atomic_write_json(root / 'trial_evidence.json', record)
    return record


def dry_validate(*, manifest_path: Path = MANIFEST, benchmark: Path = BENCHMARK,
                 work: Path = WORK, images: dict[str, dict[str, Any]] | None = None
                 ) -> dict[str, Any]:
    population = load_population(benchmark, work)
    required = sorted({b['environment_image_id'] for p in population for b in p['bindings'].values()})
    observed = docker.inspect_images(required) if images is None else images
    seen, paths, records = set(), set(), []

    def sentinel(invocation: docker.Invocation, binding: dict[str, Any]) -> dict[str, Any]:
        key = binding['case_id'], binding['revision_label'], binding['ordinal']
        require(key not in seen and binding['evidence_path'] not in paths, 'duplicate dry namespace')
        seen.add(key)
        paths.add(binding['evidence_path'])
        return dict(binding, docker_invocation=list(invocation.argv),
                    oracle_argv=[c['argv'] for c in invocation.request['commands']],
                    boundary='NON_EXECUTING_SENTINEL', executed=False)

    for item in population:
        records.extend(execute_case(case=item['case_id'], execution_id='v5-readiness-dry-v1',
                                    manifest_path=manifest_path, sentinel=sentinel,
                                    image_inspector=lambda _: observed, benchmark=benchmark,
                                    work=work, population=population))
    require(len(records) == len(seen) == len(paths) == 168, 'incomplete dry repetition namespace')
    return {'schema': 'V5_ORACLE_READINESS_DRY_VALIDATION_V1', 'v5_baseline_commit': BASELINE,
            'manifest_sha256': legacy.sha256_file(manifest_path), 'cases': 28, 'variants': 56,
            'planned_repetitions': 168, 'dry_validated_repetitions': 168, 'executed_repetitions': 0,
            'planned_command_invocations': 210, 'records': records}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('reissue', 'dry-validate', 'execute'))
    parser.add_argument('--case')
    parser.add_argument('--execution-id', default='')
    parser.add_argument('--authorization', default='')
    args = parser.parse_args()
    if args.mode == 'reissue':
        files = derive_bundle(load_population())
        write_exclusive_bundle(files)
        print(json.dumps({'successors': 19, 'manifest': str(MANIFEST), 'executed': 0}))
    elif args.mode == 'dry-validate':
        report = dry_validate()
        print(json.dumps({k: v for k, v in report.items() if k != 'records'}, indent=2))
    else:
        execute_case(case=args.case or '', execution_id=args.execution_id, dry_run=False,
                     authorization=args.authorization)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

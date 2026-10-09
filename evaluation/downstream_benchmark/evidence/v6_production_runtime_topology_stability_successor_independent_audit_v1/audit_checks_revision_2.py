"""Bounded independent checks on unchanged candidate code. No production I/O.

Traversal fixtures intentionally reproduce a confinement defect. Their resolved
locations are exclusively inside this audit, not the advertised qualification
root. Passing diagnostics here is NOT proof that the root guard is sound.
"""
import ast
import copy
import hashlib
import importlib
import json
import os
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True
WORK = HERE / 'synthetic_run_2'
WORK.mkdir(exist_ok=False)
io_events = []

def owned(path):
    if isinstance(path, int):
        return
    p = Path(os.fsdecode(path)).resolve()
    if not p.is_relative_to(HERE):
        raise RuntimeError('AUDIT_WRITE_BOUNDARY: ' + str(p))

def hook(event, args):
    if event == 'open':
        path, mode, flags = args
        if (flags or 0) & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
            owned(path)
    elif event in {'os.mkdir', 'os.remove', 'os.rmdir', 'os.chmod', 'os.utime'}:
        owned(args[0])
    elif event in {'os.rename', 'os.link', 'os.symlink'}:
        owned(args[0]); owned(args[1])
    elif event == 'subprocess.Popen':
        executable, argv, cwd, env = args
        allowed = (argv == ['git', 'rev-parse', 'HEAD'] or argv == ['git', 'cat-file', 'blob',
            '5c007fbfbfc5b3529105a14f87127f50e1eab6d7:evaluation/downstream_benchmark/v6_current_state.json'])
        io_events.append({'event': event, 'argv': argv, 'cwd': str(cwd), 'allowed_read_only': allowed})
        if not allowed or not Path(cwd).resolve().is_relative_to(ROOT):
            raise RuntimeError('AUDIT_SUBPROCESS_DENIED')
    elif event.startswith('socket.') or event in {'os.system', 'os.posix_spawn', 'os.exec', 'os.fork', 'os.chdir'}:
        io_events.append({'event': event, 'denied': True})
        raise RuntimeError('AUDIT_EXTERNAL_IO_DENIED: ' + event)

sys.addaudithook(hook)
PACKAGE = 'evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_resume_v1'
p = importlib.import_module(PACKAGE + '.production_provider_successor_candidate')
c = importlib.import_module(PACKAGE + '.production_controller_successor_candidate')
q = importlib.import_module(PACKAGE + '.synthetic_e2e_qualifier')
a, ledger = p.a, p.ledger
CAND = Path(p.__file__).parent

def write(name, value):
    with (HERE / name).open('x') as f:
        json.dump(value, f, sort_keys=True, indent=2)
        f.write('\n')

def ident(path):
    raw = path.read_bytes()
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'size_bytes': len(raw)}

def snapshot(root):
    return {str(x.relative_to(root)): ident(x) for x in sorted(root.rglob('*')) if x.is_file()}

def rejected(call):
    try:
        call()
    except (a.Rejected, ValueError, TypeError, KeyError, OSError, SystemExit) as exc:
        return {'rejected': True, 'exception': type(exc).__name__, 'reason': str(exc)}
    return {'rejected': False}

def lexical(actual):
    value = p.QUALIFICATION_ROOT / os.path.relpath(actual, p.QUALIFICATION_ROOT)
    assert value.is_relative_to(p.QUALIFICATION_ROOT)
    assert value.resolve() == actual and not actual.is_relative_to(p.QUALIFICATION_ROOT)
    return value

def fixture(label):
    actual = WORK / label
    path, items = q.fixture(lexical(actual))
    controller = c.ProductionController.synthetic(path)
    assert controller.authority.root.resolve() == actual
    return controller, items, actual

def isolation():
    direct, _ = q.fixture(WORK / 'direct_root_reject')
    direct_reject = rejected(lambda: c.ProductionController.synthetic(direct))
    assert direct_reject['rejected']
    controller, items, actual = fixture('traversal_e2e')
    before = {k: id(v) for k, v in a.shared.__dict__.items()}
    traces = []
    def trace(frame, event, arg):
        if event == 'call' and frame.f_code is a.shared._materialize_checked.__code__:
            traces.append({'same_original_code_object': True, 'synthetic_only_argument': frame.f_locals['synthetic_only'],
                           'output': str(frame.f_locals['output']), 'input_root': str(frame.f_locals['input_root'])})
        return trace
    sys.settrace(trace)
    try:
        terminals = {items[i]['variant'] + '_' + str(i): controller.run_synthetic(items[i], p.SyntheticScenario(outcome))
                     for i, outcome in ((0, 'PASS'), (2, 'PASS'), (3, 'RAISE'))}
    finally:
        sys.settrace(None)
    assert {k: id(v) for k, v in a.shared.__dict__.items()} == before
    assert [v['state'] for v in terminals.values()] == ['MATERIALIZED', 'MATERIALIZED', 'INTERRUPTED']
    assert len(traces) == 3
    for item in (items[0], items[2], items[3]):
        claim_raw = (actual / 'ledger/claims' / (item['base_attempt_id'] + '.json')).read_bytes()
        term_raw = (actual / 'ledger/terminals' / (item['base_attempt_id'] + '.json')).read_bytes()
        claim, terminal = a.loads(claim_raw), a.loads(term_raw)
        assert claim_raw == a.canonical(claim) and term_raw == a.canonical(terminal)
        assert terminal['claim_sha256'] == a.sha(claim_raw)
        assert claim['attempt_id'].startswith('SYNTHETIC_QUALIFICATION_')
        assert claim['receipt_sha256'] is None if not item['build_network_required'] else claim['receipt_sha256']
    root_result = {'status': 'FAIL_CONFINEMENT', 'direct_root_rejection': direct_reject,
        'declared_qualification_root': str(p.QUALIFICATION_ROOT), 'accepted_lexical_root': str(controller.authority.root),
        'actual_resolved_root': str(actual), 'candidate_sources_modified': False,
        'candidate_or_legacy_globals_patched': False, 'normal_candidate_constructors_used': True,
        'actual_outside_declared_root': not actual.is_relative_to(p.QUALIFICATION_ROOT),
        'original_checked_function_calls': traces, 'terminals': terminals,
        'interpretation': 'Counterexample to synthetic root confinement; E2E diagnostics do not validate the advertised isolation guard.'}
    write('isolation_reproduction.json', root_result)
    return root_result

class InjectedCrash(BaseException):
    pass

def crashes():
    # Source line events interrupt unchanged code; no module/global monkeypatch.
    cases = [('before_raw_publication', 'publish_raw_association', 1080),
             ('after_raw_publication', 'publish_raw_association', 1081),
             ('before_receipt_publication', 'publish_raw_association', 1086),
             ('after_receipt_publication', 'publish_raw_association', 1087),
             ('before_association_publication', 'publish_raw_association', 1094),
             ('after_association_publication', 'publish_raw_association', 1095),
             ('immediately_before_exclusive_lock', 'claim', 528),
             ('after_lock_before_claim', 'claim', 529),
             ('claim_publication_failure', 'claim', 532)]
    results = []
    for label, fn, line in cases:
        ctrl, items, actual = fixture('crash_' + label)
        admission = ctrl.prepare(items[0])
        hit = []
        def trace(frame, event, arg):
            if event == 'line' and frame.f_code.co_filename == p.__file__ and frame.f_code.co_name == fn and frame.f_lineno == line:
                hit.append(line)
                raise InjectedCrash(label)
            return trace
        sys.settrace(trace)
        try:
            ctrl.claim(admission)
            raise AssertionError('crash point not reached')
        except InjectedCrash:
            pass
        finally:
            sys.settrace(None)
        assert hit == [line]
        before = snapshot(actual)
        state = rejected(lambda: ctrl.authority.journal().state(items[0]['base_attempt_id']))
        if not state['rejected']:
            state['value'] = ctrl.authority.journal().state(items[0]['base_attempt_id'])
        reentry = rejected(lambda: ctrl.claim(admission))
        assert reentry['rejected'] and before == snapshot(actual)
        assert not list((actual / 'ledger/claims').iterdir())
        results.append({'point': label, 'source_line': line, 'source_function': fn, 'trace_hit': hit,
            'state': state, 'reentry': reentry, 'bytes_unchanged_on_reentry': True,
            'claims': 0, 'locks': len(list((actual / 'ledger/locks').iterdir())),
            'retained_files': before})
    ctrl, items, actual = fixture('crash_terminal_publication')
    admission = ctrl.prepare(items[0]); claim = ctrl.claim(admission)
    hit = []
    # Interruption after the fsynced partial inode, immediately before final link.
    atomic = ledger.atomic_publish
    link_line = next(n.lineno for n in ast.walk(ast.parse(Path(ledger.__file__).read_text()))
                     if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'link')
    def trace(frame, event, arg):
        if event == 'line' and frame.f_code is atomic.__code__ and frame.f_lineno == link_line:
            hit.append(link_line); raise InjectedCrash('terminal_publication_failure')
        return trace
    sys.settrace(trace)
    try:
        ctrl.authority.journal().terminal(claim, state='INTERRUPTED', evidence={'audit_crash': True}, reason='audit injected crash')
        raise AssertionError('terminal crash not reached')
    except InjectedCrash:
        pass
    finally:
        sys.settrace(None)
    before = snapshot(actual)
    reentry = rejected(lambda: ctrl.claim(admission))
    second_terminal = rejected(lambda: ctrl.authority.journal().terminal(claim, state='INTERRUPTED', evidence={'audit_crash': True}, reason='retry probe'))
    assert hit and reentry['rejected'] and second_terminal['rejected'] and before == snapshot(actual)
    results.append({'point': 'terminal_publication_failure', 'source_path': ledger.__file__, 'source_line': link_line,
        'source_function': 'atomic_publish', 'trace_hit': hit, 'reentry': reentry, 'second_terminal': second_terminal,
        'bytes_unchanged_on_reentry': True, 'claims': 1, 'terminals': 0, 'partial_terminals': 1, 'retained_files': before})
    write('crash_reproduction.json', {'status': 'PASS_BOUNDED_INJECTED_POINTS', 'cases': results,
          'scope': 'Original code objects with line-event crash injection in audit-confined traversal fixtures; not a hardware power-loss/fsync durability proof.'})

def security_checks():
    baseline = a.loads((WORK / 'direct_root_reject/raw_fixture.json').read_bytes())
    config = p.frozen_inputs()
    first = p.verify_raw_security(baseline, config, stage='AUDIT', synthetic=True)
    rows = []
    def check(label, mutation, expected=None):
        b = copy.deepcopy(baseline); mutation(b)
        result = rejected(lambda: p.verify_raw_security(b, config, stage='AUDIT', synthetic=True))
        if expected:
            assert result['rejected'] and expected in result['reason'], (label, result)
        rows.append({'name': label, **result})
    def object_change(bundle, source, fn):
        value = a.loads(bundle['sources'][source]['raw_utf8'].encode()); fn(value)
        raw = a.canonical(value); bundle['sources'][source].update(raw_utf8=raw.decode(), sha256=a.sha(raw))
    for source in p.RAW_SOURCES:
        check('mandatory_missing_' + source, lambda b, source=source: b['sources'].pop(source), 'source completeness')
    for verdict in ('UNKNOWN', 'UNAUTHORIZED'):
        check('client_' + verdict, lambda b, verdict=verdict: object_change(b, 'client_evidence', lambda v: v['sessions'][0].update(classification=verdict)), 'active client blocks')
    for label, source, fn, reason in [
        ('incomplete_census', 'client_census', lambda v: v.update(complete=False), 'incomplete active client census'),
        ('unobserved_surface', 'client_census', lambda v: v.update(unobserved_surfaces=['UNKNOWN']), 'incomplete active client census'),
        ('name_alone', 'client_evidence', lambda v: v['sessions'][0].update(source_kind='PROCESS_NAME_BUILDCTL'), 'insufficient independent attribution'),
        ('ExecID_alone', 'client_evidence', lambda v: v['sessions'][0].update(source_kind='EXEC_ID_ONLY'), 'insufficient independent attribution'),
        ('missing_boundary', 'client_evidence', lambda v: v['boundary'].update(complete=False), 'access boundary'),
        ('unknown_listener', 'listener_inventory', lambda v: v.update(tcp=[{'address':'0.0.0.0','port':1234}]), 'listener inventory'),
        ('unattributed_socket', 'client_census', lambda v: v['sessions'][0].update(socket_inodes=[]), 'unattributed connected'),
        ('missing_socket_access', 'socket_access', lambda v: v.update(complete=False), 'socket ownership/access'),
    ]:
        check(label, lambda b, source=source, fn=fn: object_change(b, source, fn), reason)
    # Raw connected peer path is excluded from projection yet is not checked
    # against the session endpoint. Keep the full raw inspect internally equal.
    b = copy.deepcopy(baseline)
    raw = b['sources']['unix_sockets']['raw_utf8'].replace('3697 /run/buildkit/buildkitd.sock', '3697 /tmp/unknown-control.sock')
    b['sources']['unix_sockets'].update(raw_utf8=raw, sha256=a.sha(raw.encode()))
    object_change(b, 'daemon', lambda v: v.update(sockets=raw))
    try:
        alt = p.verify_raw_security(b, config, stage='AUDIT', synthetic=True)
        rows.append({'name':'connected_socket_path_unbound', 'rejected':False,
                     'stable_projection_unchanged': alt['security_projection_sha256'] == first['security_projection_sha256'],
                     'raw_changed': alt['raw_observation_sha256'] != first['raw_observation_sha256']})
    except Exception as exc:
        rows.append({'name':'connected_socket_path_unbound','rejected':True,'reason':str(exc)})
    write('security_check_reproduction.json', {'checks':rows, 'baseline_security_sha':first['security_projection_sha256']})

def evidence_and_science():
    sealed = a.loads((CAND / 'synthetic_e2e_results.json').read_bytes())
    base = p.QUALIFICATION_ROOT
    mismatches = []
    for rel, ref in sealed['external_inventory'].items():
        actual = ident(base / rel)
        if actual != ref:
            mismatches.append({'path':rel,'expected':ref,'actual':actual})
    runroot = Path(sealed['qualification_run_root'])
    observed_paths = {str(f.relative_to(base)) for f in runroot.rglob('*') if f.is_file()}
    assert observed_paths == set(sealed['external_inventory']) and not mismatches
    original_records = []
    for path in sorted(runroot.glob('fixture_*/ledger/terminals/*.json')):
        raw = path.read_bytes(); t = a.loads(raw)
        claim_path = path.parent.parent / 'claims' / path.name
        claim_raw = claim_path.read_bytes(); cl = a.loads(claim_raw)
        assert raw == a.canonical(t) and claim_raw == a.canonical(cl)
        assert t['claim_sha256'] == a.sha(claim_raw)
        artifacts = t['evidence'].get('artifact_sha256', {})
        for name, digest in artifacts.items():
            assert a.sha((path.parents[2] / 'attempts' / t['attempt_id'] / name).read_bytes()) == digest
        original_records.append({'path':str(path),'state':t['state'],'terminal_sha':a.sha(raw),'claim_sha':a.sha(claim_raw),
                                 'artifact_count':len(artifacts),'receipt_sha':cl['receipt_sha256']})
    write('qualification_external_replay.json', {'status':'PASS_EXACT_EXTERNAL_BYTES', 'file_count':len(observed_paths),
          'fixture_count':len(list(runroot.glob('fixture_*'))),'terminals':original_records,
          'limitations':'No source modification or replay in the preexisting qualification namespace; historical execution order is assessed from source plus sealed results.'})
    old = importlib.import_module('evaluation.downstream_benchmark.evidence.v6_preparation_execution_production_runtime_installation_resume_v1.production_provider_candidate')
    corrected = importlib.import_module('evaluation.downstream_benchmark.evidence.v6_production_runtime_image_identity_compatibility_bridge_v1.corrected_production_provider_candidate')
    population_raw = (ROOT / p.legacy.PACKAGE / 'work_items_candidate.json').read_bytes()
    population = a.loads(population_raw)
    identity = p.population_identity(population,population_raw)
    assert identity == p.expected_population_identity()
    assert identity['file_sha256'] == '288eaed9f7e9ff4daf2978e7c41b6c6ead83e9d99b9ddee7801c163153bd63bb'
    assert identity['semantic_sha256'] == 'f3a719f2a92f1d1ba96baa9dd3936e8bd87d330f048542c9ee5cfce86185a800'
    assert len({x['base_attempt_id'] for x in population['items']}) == 641
    _, manifest = a.load_inputs(); cfg = p.frozen_inputs()
    maps = p.exact_json(ROOT / p.NATIVE / 'seven_base_transport_map.json')['mapping']
    results = []
    for item in population['items']:
        plan = a.select(manifest,ordinal=item['census_order'],case_id=item['case_id'],plan_sha=item['plan_sha256'])
        assert a.work_item(plan,item['variant']) == item
        receipt = b'AUDIT_COMPILE_ONLY_NO_AUTHORITY\n' if item['build_network_required'] else None
        compiled = [m.compile_production_transport(item,plan,{},receipt_raw=receipt) for m in (old,corrected,p)]
        assert compiled[0] == compiled[1] == compiled[2]
        expected = a.shared.build_definition(a.engine_recipe(plan),source_present=item['variant'] != 'SOURCE_INDEPENDENT',dependency_present=plan['recipe_candidate']['requirements']['dependency_bytes_b64'] is not None)
        assert compiled[2]['scientific_dockerfile'] == expected
        m = next(x for x in maps if x['scientific_base_authority'] == item['base_image_reference'])
        binding = {**m,'endpoint':cfg['endpoint'],'native_binary_sha256':cfg['client_binary_sha256'],
            'same_daemon':True,'daemon_count':1,'runtime_reference':cfg['runtime_image']['immutable_reference'],
            'frontend_alias':'errpilot_frozen_base','container_id':'SYNTHETIC_AUDIT_DAEMON',
            'container_root':'/tmp/errpilot-v6-audit-compile-only','tag':'errpilot-synthetic-audit-compile-only',
            'proxy_internal_host_binding':'add-hosts='+cfg['proxy']['proxy_name']+'=172.28.0.3','compiled':compiled[2]}
        argv=[m.native.native_argv(binding,binding['container_root'],binding['tag'],co) for m,co in zip((old,corrected,p),compiled)]
        assert argv[0] == argv[1] == argv[2]
        p.validate_command(['docker','exec',binding['container_id'],*argv[2]],binding)
        results.append({'base_attempt_id':item['base_attempt_id'],'item_sha':a.identity(item),
            'scientific_dockerfile_sha':a.sha(expected),'execution_dockerfile_sha':a.sha(compiled[2]['execution_dockerfile']),
            'native_argv_sha':a.identity(argv[2]),'exact_equal':True})
    blocked = [x['case_id'] for x in population['blocked']]
    assert blocked == ['matplotlib::1','matplotlib::8']
    counts = dict(Counter(x['variant'] for x in population['items']))
    assert counts == {'SOURCE_INDEPENDENT':221,'BUGGY':210,'FIXED':210}
    write('scientific_independent_replay.json', {'status':'PASS_EXACT_PROJECTION','population':identity,
        'variants':counts,'blocked_cases':blocked,'per_item':results,'real_commands_executed':0,
        'scientific_eligibility_or_environment_readiness_inferred':False})

def main():
    assert (HERE / 'scientific_independent_replay.json').is_file()
    assert (HERE / 'qualification_external_replay.json').is_file()
    print('Original-constructor traversal counterexample and bounded E2E',flush=True)
    isolation()
    print('Independent pure security gates',flush=True)
    security_checks()
    print('Ten exact-code crash points',flush=True)
    crashes()
    write('audit_io_events.json',{'events':io_events,'write_root':str(HERE),'network_allowed':False,
        'subprocess_policy':'Only two exact read-only Git argv forms; all Docker, native, source acquisition and dependency subprocesses denied',
        'bytecode_writes_disabled':True})
    print('Completed independent bounded checks',flush=True)

if __name__ == '__main__':
    main()

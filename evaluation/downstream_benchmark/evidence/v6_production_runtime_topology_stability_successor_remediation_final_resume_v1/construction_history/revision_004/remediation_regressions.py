"""Finding-specific and source-level interruption regressions; no frozen patching."""
from __future__ import annotations

import ast
import hashlib
import json
import os
import stat
import sys
from pathlib import Path

from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a

from . import production_provider_remediated_candidate as p
from . import qualification_io as qio


def inventory(root):
    if root is None:
        return {}
    root = Path(root)
    result = {}
    for current, directories, files in os.walk(root, followlinks=False):
        for name in sorted(directories + files):
            path = Path(current) / name
            info = path.lstat()
            value = {'mode': stat.S_IMODE(info.st_mode)}
            if path.is_symlink():
                value.update(type='symlink', target=os.readlink(path))
            elif path.is_dir():
                value.update(type='directory')
            else:
                raw = path.read_bytes()
                value.update(type='file', size_bytes=len(raw), sha256=a.sha(raw))
            result[str(path.relative_to(root))] = value
    return result


def save(out, name, value):
    with (out / name).open('xb') as stream:
        stream.write(p.pretty(value))


def reason_spec(name, golden, reason, classification):
    if reason is not None:
        return {'reason': reason, 'classification': classification or 'Rejected',
                'mapping': 'Explicit finding-specific candidate gate'}
    record = golden[name]
    expected = record['reason'].replace('v6_production_runtime_topology_stability_successor_resume_v1',
                                      'v6_production_runtime_topology_stability_successor_remediation_final_resume_v1')
    expected = expected.replace('production_controller_successor_candidate', 'production_controller_remediated_candidate')
    expected = expected.replace('production_provider_successor_candidate', 'production_provider_remediated_candidate')
    changed = {'synthetic_real_ledger_path': 'F01 outside exact qualification root',
               'wrong_endpoint_owner': 'F02 independent endpoint access proof mismatch'}
    return {'reason': changed.get(name, expected), 'classification': record['observed_rejection'],
            'mapping': 'Inherited exact reason, with explicit F01/F02 source-location/security mapping'}


def assert_reason(name, exc, expected, stderr):
    a.require(type(exc).__name__ == expected['classification'],
              'wrong exception classification for ' + name + ': ' + type(exc).__name__)
    if name in {'missing_claim_raw_association', 'missing_effectivity_pin'}:
        a.require(isinstance(exc, FileNotFoundError) and exc.errno == 2,
                  'missing input gate not exercised')
        if name == 'missing_effectivity_pin':
            a.require(Path(exc.filename).name == 'absent_effectivity.json', 'wrong missing effectivity input')
        else:
            a.require(Path(exc.filename).suffix == '.json' and len(Path(exc.filename).stem) == 64,
                      'wrong missing association input')
    else:
        a.require(str(exc) == expected['reason'], 'unrelated rejection for ' + name + ': ' + str(exc))
    if name.startswith('production_CLI_'):
        option = '--' + name.removeprefix('production_CLI_')
        a.require('unrecognized arguments: ' + option in stderr, 'wrong CLI option rejection')


def raw_values(root):
    bundle = p.exact_json(root / 'raw_fixture.json')
    values = {name: a.loads(bundle['sources'][name]['raw_utf8'].encode()) for name in
              ('client_census', 'client_evidence', 'socket_access', 'listener_inventory')}
    return bundle, values


def rewrite(root, bundle, values):
    for name, value in values.items():
        raw = value.encode() if isinstance(value, str) else a.canonical(value)
        bundle['sources'][name].update(raw_utf8=raw.decode(), sha256=a.sha(raw))
    Path(root / 'raw_fixture.json').write_bytes(p.pretty(bundle))


def socket_change(root, change):
    bundle, values = raw_values(root)
    original = bundle['sources']['unix_sockets']['raw_utf8']
    changed = change(original)
    daemon = a.loads(bundle['sources']['daemon']['raw_utf8'].encode())
    daemon['sockets'] = changed
    values.update(unix_sockets=changed, daemon=daemon)
    rewrite(root, bundle, values)


def run_f03(fresh, rejected, out):
    records = {}
    for name, value, reason in [
        ('runtime_authority_false', False, 'F03 client authenticated_source authority false'),
        ('runtime_authority_integer_zero', 0, 'F03 client authenticated_source exact Boolean type required')]:
        ctrl, items, _ = fresh()
        admission = ctrl.prepare(items[0])
        bundle, values = raw_values(ctrl.authority.root)
        values['client_evidence']['sessions'][0]['authenticated_source'] = value
        rewrite(ctrl.authority.root, bundle, values)
        rejected(name, lambda: ctrl.claim(admission), ctrl.authority.root, True, reason=reason)
        records[name] = {'old_V1_name': name, 'V2_field': 'client_evidence.sessions[0].authenticated_source',
                         'value': value, 'JSON_type': 'boolean' if type(value) is bool else 'integer',
                         'function': 'verify_clients -> verify_authority_leaf', 'intended_reason': reason,
                         'deprecated_receipt_field_reintroduced': False, 'status': 'PASS_REJECTED'}
    save(out, 'runtime_authority_test_mapping.json', {'status': 'PASS', 'checks': records,
        'synthetic_receipt_runtime_authority_false_is_valid_and_unchanged': True,
        'rationale': 'The genuine V2 independent client authorization Boolean must be true. '
                     'The synthetic receipt runtime_authority false remains correct and is never rejected as real authority.'})


def run_f02(fresh, rejected, out):
    def mutate_source(name, mutation):
        def action(root):
            bundle, values = raw_values(root)
            mutation(values[name])
            rewrite(root, bundle, values)
        return action
    def endpoint(root):
        bundle, values = raw_values(root)
        values['client_census']['sessions'][0]['endpoint'] = 'unix:///tmp/unknown-control.sock'
        rewrite(root, bundle, values)
    def duplicate(root):
        bundle, values = raw_values(root)
        sockets = bundle['sources']['unix_sockets']['raw_utf8']
        sockets += sockets.splitlines()[-1].replace('0000000000000003', '0000000000000004') + '\n'
        daemon = a.loads(bundle['sources']['daemon']['raw_utf8'].encode())
        daemon['sockets'] = sockets
        values['client_census']['sessions'][0]['socket_inodes'].append('3697')
        values.update(unix_sockets=sockets, daemon=daemon)
        rewrite(root, bundle, values)
    def forged(root):
        bundle, values = raw_values(root)
        proof = values['client_evidence']['sessions'][0]
        body = a.loads(proof['original_source_utf8'].encode())
        body['process_identity'] = 'FORGED_PROCESS'
        proof['original_source_utf8'] = a.canonical(body).decode()
        proof['source_sha256'] = a.sha(proof['original_source_utf8'].encode())
        rewrite(root, bundle, values)
    def normalization(root):
        bundle, values = raw_values(root)
        wrong = 'unix:///run/buildkit/../buildkit/buildkitd.sock'
        values['client_census']['sessions'][0]['endpoint'] = wrong
        values['client_evidence']['sessions'][0]['session_endpoint'] = wrong
        rewrite(root, bundle, values)
    cases = [
        ('same_inode_wrong_Path', lambda root: socket_change(root, lambda s: s.replace('3697 /run/buildkit/buildkitd.sock', '3697 /tmp/unknown-control.sock')), 'F02 actual socket Path/endpoint conflict'),
        ('wrong_endpoint_unchanged_proof', endpoint, 'UNKNOWN client: insufficient independent attribution'),
        ('matching_Path_wrong_client', mutate_source('client_census', lambda x: x['sessions'][0].update(process_identity='WRONG_CLIENT')), 'UNKNOWN client: insufficient independent attribution'),
        ('forged_independent_provenance', forged, 'F02 independent session/socket provenance binding mismatch'),
        ('pathless_without_independent_association', lambda root: socket_change(root, lambda s: s.replace('3697 /run/buildkit/buildkitd.sock', '3697')), 'F02 pathless independent session association unavailable'),
        ('ambiguous_duplicate_inode', duplicate, 'F02 ambiguous duplicate connected inode'),
        ('inconsistent_socket_namespace', mutate_source('client_census', lambda x: x['sessions'][0].update(socket_namespace='WRONG_NAMESPACE')), 'F02 inconsistent socket/client namespace'),
        ('unverifiable_socket_namespace', mutate_source('listener_inventory', lambda x: x.pop('socket_namespace')), 'F02 unverifiable socket namespace'),
        ('unknown_control_capable', mutate_source('client_evidence', lambda x: x['sessions'][0].update(classification='UNKNOWN')), 'UNKNOWN/UNAUTHORIZED active client blocks'),
        ('incomplete_census', mutate_source('client_census', lambda x: x.update(complete=False)), 'incomplete active client census/unobserved surfaces'),
        ('unauthorized_client', mutate_source('client_evidence', lambda x: x['sessions'][0].update(classification='UNAUTHORIZED')), 'UNKNOWN/UNAUTHORIZED active client blocks'),
        ('new_unauthorized_listener', lambda root: socket_change(root, lambda s: s + '0000000000000004: 00000002 00000000 00010000 0001 01 777 /tmp/unauthorized.sock\n'), 'unexpected/duplicate Unix listener'),
        ('wrong_socket_permission', mutate_source('socket_access', lambda x: x['endpoints'][0].update(mode=438)), 'unauthorized/unverifiable endpoint permissions'),
        ('wrong_endpoint_access_proof', mutate_source('socket_access', lambda x: x['endpoints'][0].update(uid=999)), 'F02 independent endpoint access proof mismatch'),
        ('invalid_endpoint_normalization', normalization, 'F02 invalid endpoint normalization'),
        ('missing_mandatory_permission_evidence', mutate_source('socket_access', lambda x: x.update(endpoints=[])), 'endpoint access inventory'),
    ]
    executed = []
    for label, mutate, reason in cases:
        for route in ('controller_preclaim', 'provider_prebuild'):
            ctrl, items, _ = fresh()
            admission = ctrl.prepare(items[0])
            if route == 'provider_prebuild':
                claim = ctrl.claim(admission)
                impl = p.ProductionProvider(ctrl.authority, items[0], claim, admission.receipt_raw)
            mutate(ctrl.authority.root)
            call = (lambda: ctrl.claim(admission)) if route == 'controller_preclaim' else (
                lambda: impl.execute_synthetic(p.SyntheticScenario()))
            name = 'F02_' + route + '_' + label
            rejected(name, call, ctrl.authority.root, route == 'controller_preclaim', reason=reason)
            a.require(not (ctrl.authority.root / 'attempts').exists(), 'F02 rejection reached build')
            executed.append({'name': name, 'route': route, 'reason': reason, 'status': 'PASS_REJECTED',
                             'builds': 0, 'new_claims': 0, 'new_terminals': 0, 'automatic_retry': False})
    save(out, 'socket_endpoint_regressions.json', {'status': 'PASS', 'checks': executed,
        'negative_count': len(executed), 'correctly_correlated_authorized_client': 'Inherited full E2E and authorization tests',
        'transient_turnover': 'Inherited authorized_transient_turnover_preserves_projection with complete new proof',
        'actual_Path_never_filled_or_ignored': True, 'real_client_authorization': 'BLOCKED'})


def run_f01(fresh, rejected, out):
    checks = []
    root = p.QUALIFICATION_ROOT
    lexical = [('direct_parent', str(root / '../escape/effectivity.json')),
               ('nested_parent', str(root / 'a/../../escape/effectivity.json')),
               ('outside_absolute', str(a.OUTPUT_ROOT / 'namespace.json')),
               ('relative_alias', 'qualification/alias/effectivity.json'),
               ('dot_spelling_alias', str(root) + '/./fixture/effectivity.json')]
    for label, spelling in lexical:
        ctrl, _, _ = fresh()
        reason = ('F01 outside exact qualification root' if label == 'outside_absolute' else
                  'F01 absolute canonical spelling required; traversal/alias rejected')
        rejected('F01_' + label, lambda spelling=spelling: p.Authority.synthetic(spelling),
                 ctrl.authority.root, True, reason=reason)
        checks.append(label)
    for label in ('intermediate_symlink', 'outbound_symlink', 'dangling_symlink'):
        ctrl, items, path = fresh()
        base = Path(ctrl.authority.root)
        link = base / 'fixture_alias'
        target = base / ('absent_owned_target' if label == 'dangling_symlink' else 'owned_target')
        if label != 'dangling_symlink':
            target.mkdir()
        link.symlink_to(target, target_is_directory=True)
        spelling = link / 'synthetic_effectivity_fixture.json'
        rejected('F01_' + label, lambda: p.Authority.synthetic(spelling), base, True,
                 reason='F01 symlink/resolved alias rejected')
        a.require(not (target / spelling.name).exists(), 'F01 escape artifact created')
        checks.append(label)
    for label, kind in [('receipt_sidecar_escape', 'raw-evidence'), ('claim_escape', 'claims'),
                        ('terminal_escape', 'terminals'), ('lock_escape', 'locks')]:
        ctrl, items, _ = fresh()
        admission = ctrl.prepare(items[0])
        claim = ctrl.claim(admission) if kind == 'terminals' else None
        base = Path(ctrl.authority.root)
        target = base / 'test_owned_redirect_target'
        target.mkdir()
        component = base / kind if kind == 'raw-evidence' else base / 'ledger' / kind
        if component.exists():
            component.rename(component.with_name(kind + '_retained_original'))
        component.symlink_to(target, target_is_directory=True)
        if kind == 'terminals':
            def call():
                return ctrl.authority.journal().terminal(claim, state='INTERRUPTED', evidence={'synthetic': True}, reason='OWNED_NEGATIVE')
        else:
            def call():
                return ctrl.claim(admission)
        reason = 'F01 symlink/resolved alias rejected' if kind == 'raw-evidence' else 'symlink ledger path'
        rejected('F01_' + label, call, base, kind != 'terminals', reason=reason)
        a.require(not list(target.iterdir()), 'F01 redirected artifact created')
        checks.append(label)
    ctrl, _, path = fresh()
    data = p.exact_json(path)
    data['qualification_root'] = str(root / 'other_caller_selected_namespace')
    Path(path).write_bytes(p.pretty(data))
    rejected('F01_caller_selected_root', lambda: p.Authority.synthetic(path), ctrl.authority.root, True,
             reason='F01 fixture/root namespace alias')
    checks.append('caller_selected_root')
    # Direct descriptor primitive and exact candidate source, legitimate nested write.
    ctrl, _, _ = fresh()
    nested = ctrl.authority.root / 'legitimate' / 'nested'
    ctrl.authority.io.mkdir_durable(nested)
    ctrl.authority.io.exclusive_write(nested / 'receipt.json', b'LEGITIMATE_OWNED_FIXTURE\n')
    a.require(ctrl.authority.io.read(nested / 'receipt.json') == b'LEGITIMATE_OWNED_FIXTURE\n', 'F01 nested readback')
    # The single planned replacement happens after resolve but before component open.
    base = Path(ctrl.authority.root)
    mutable, redirect = base / 'mutable', base / 'owned_redirect'
    (mutable / 'nested').mkdir(parents=True)
    (redirect / 'nested').mkdir(parents=True)
    target = mutable / 'nested' / 'association.json'
    source = Path(qio.__file__).read_text().splitlines()
    line = next(i + 1 for i, text in enumerate(source) if 'child = os.open(component, FLAGS, dir_fd=fd)' in text)
    hits = []
    def trace(frame, event, arg):
        if event == 'line' and frame.f_code is qio.QualificationIO.directory.__code__ \
                and frame.f_lineno == line and frame.f_locals.get('component') == 'mutable' and not hits:
            mutable.rename(base / 'retained_mutable')
            mutable.symlink_to(redirect, target_is_directory=True)
            hits.append({'source_line': line, 'operation': 'replace directory with symlink before actual open'})
        return trace
    before = inventory(base)
    sys.settrace(trace)
    try:
        try:
            ctrl.authority.io.exclusive_write(target, b'MUST_NOT_ESCAPE\n')
        except a.Rejected as exc:
            a.require(str(exc) == 'F01 no-follow component refused: mutable', 'wrong F01 race gate')
            race_reason = str(exc)
        else:
            raise AssertionError('F01 symlink replacement accepted')
    finally:
        sys.settrace(None)
    a.require(len(hits) == 1 and not (redirect / 'nested' / 'association.json').exists(), 'F01 race containment failed')
    save(out, 'root_confinement_regressions.json', {'status': 'PASS', 'negative_checks': checks,
        'legitimate_nested_write': 'PASS', 'replaceable_component': {'status': 'PASS_REJECTED',
        'reason': race_reason, 'trace_hit': hits, 'before': before, 'after': inventory(base),
        'redirected_artifacts': 0}, 'source': p.RESUME + 'qualification_io.py',
        'no_unauthorized_outside_root_artifact_created': True,
        'scope_limit': 'No privileged relocation of an already-open directory outside the authorized tree tested'})


class InjectedCrash(BaseException):
    pass


def function_line(function, fragment, occurrence=0):
    lines = Path(function.__code__.co_filename).read_text().splitlines()
    tree = ast.parse('\n'.join(lines))
    node = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                and n.lineno == function.__code__.co_firstlineno)
    matches = [i + 1 for i in range(node.lineno - 1, node.end_lineno) if fragment in lines[i]]
    return matches[occurrence]


def injected(call, function, line, exception, predicate=lambda frame: True):
    hits = []
    def trace(frame, event, arg):
        if event == 'line' and frame.f_code is function.__code__ and frame.f_lineno == line and predicate(frame):
            hits.append({'function': function.__qualname__, 'source': frame.f_code.co_filename,
                         'source_sha256': hashlib.sha256(Path(frame.f_code.co_filename).read_bytes()).hexdigest(),
                         'line': line})
            raise exception
        return trace
    sys.settrace(trace)
    try:
        try:
            call()
        except BaseException as exc:
            a.require(type(exc) is type(exception) and str(exc) == str(exception), 'unrelated fault injection failure')
        else:
            raise AssertionError('fault point did not interrupt actual candidate function')
    finally:
        sys.settrace(None)
    a.require(len(hits) == 1, 'exact fault boundary not hit')
    return hits


def reentry(ctrl, item, before):
    try:
        ctrl.claim(ctrl.prepare(item))
    except (a.Rejected, ValueError) as exc:
        reason = str(exc)
        observed_exception = type(exc).__name__
        if isinstance(exc, json.JSONDecodeError):
            a.require(reason == 'Expecting value: line 1 column 1 (char 0)', 'wrong partial claim parse gate')
        else:
            a.require(reason in {'orphan/preexisting raw sidecar blocks automatic reentry',
                                'orphan writer lock blocks', 'orphan/partial terminal blocks',
                                'receipt after claim/terminal; no retry/reuse'}, 'unrelated reentry gate')
    else:
        raise AssertionError('automatic reentry accepted after injected interruption')
    a.require(before == inventory(ctrl.authority.root), 'reentry overwrote retained fault evidence')
    return {'reason': reason, 'classification': observed_exception,
            'evidence_bytes_paths_modes_unchanged': True, 'automatic_retry': False}


def run_crash(fresh, out):
    publish = p.publish_raw_association
    claim = p.ReceiptBoundLedger.claim
    points = [
        ('before_raw_publication', publish, function_line(publish, '.exclusive_write(name, payload)', 0)),
        ('after_raw_publication', publish, function_line(publish, '    if raw is not None:')),
        ('before_receipt_publication', publish, function_line(publish, '.exclusive_write(name, raw)')),
        ('after_receipt_publication', publish, function_line(publish, '    value = association_value')),
        ('before_association_publication', publish, function_line(publish, '.exclusive_write(name, payload)', 1)),
        ('after_association_publication', publish, function_line(publish, '.persist_tree(path)')),
        ('before_exclusive_lock', claim, function_line(claim, '.exclusive_write(self._path("locks"')),
        ('after_lock_before_claim', claim, function_line(claim, 'terminal before claim')),
        ('claim_publication_failure', claim, function_line(claim, '.exclusive_write(self._path("claims"')),
        ('terminal_publication_failure', qio.QualificationIO.atomic_publish,
         function_line(qio.QualificationIO.atomic_publish, 'os.link(partial.name')),
    ]
    checks = []
    for label, function, line in points:
        ctrl, items, _ = fresh()
        admission = ctrl.prepare(items[0])
        durable_claim = ctrl.claim(admission) if label == 'terminal_publication_failure' else None
        before = inventory(ctrl.authority.root)
        call = (lambda: ctrl.authority.journal().terminal(durable_claim, state='INTERRUPTED', evidence={'fault': label}, reason='SYNTHETIC_FAULT')) \
            if durable_claim is not None else (lambda: ctrl.claim(admission))
        hits = injected(call, function, line, InjectedCrash(label))
        after = inventory(ctrl.authority.root)
        retry = reentry(ctrl, items[0], after)
        checks.append({'point': label, 'status': 'SOURCE_LEVEL_FAULT_INJECTION_PASS',
                       'trace_hit': hits, 'fixture': str(ctrl.authority.root),
                       'before': before, 'after': after, 'reentry': retry,
                       'durable_readback': inventory(ctrl.authority.root) == after,
                       'physical_power_loss': 'PHYSICAL_POWER_LOSS_DURABILITY_NOT_ESTABLISHED'})
    save(out, 'crash_boundary_revalidation.json', {'status': 'SOURCE_LEVEL_FAULT_INJECTION_PASS',
         'count': 10, 'checks': checks, 'PHYSICAL_POWER_LOSS_DURABILITY': 'NOT_ESTABLISHED'})
    partials = []
    line = function_line(qio.QualificationIO.exclusive_write, 'count = os.write(fd, view)')
    for kind in ('raw', 'receipt', 'association', 'claim'):
        ctrl, items, _ = fresh()
        admission = ctrl.prepare(items[0])
        def match(frame):
            path = frame.f_locals['path']
            if kind == 'claim':
                return path.parent.name == 'claims'
            if path.parent.name != 'preclaim':
                return False
            return path.name.endswith('.raw.json') if kind == 'raw' else (
                path.name.endswith('.receipt.json') if kind == 'receipt' else
                path.suffix == '.json' and not path.name.endswith(('.raw.json', '.receipt.json')))
        before = inventory(ctrl.authority.root)
        hits = injected(lambda: ctrl.claim(admission), qio.QualificationIO.exclusive_write,
                        line, OSError('SYNTHETIC_EMPTY_' + kind), match)
        after = inventory(ctrl.authority.root)
        empty = [rel for rel, value in after.items() if value.get('type') == 'file'
                 and value.get('size_bytes') == 0 and rel not in before]
        a.require(len(empty) == 1, 'partial write did not retain one exact empty file')
        retry = reentry(ctrl, items[0], after)
        partials.append({'kind': kind, 'status': 'SOURCE_LEVEL_FAULT_INJECTION_PASS',
                         'trace_hit': hits, 'empty_retained_file': empty[0], 'before': before,
                         'after': after, 'reentry': retry, 'physical_power_loss': 'NOT_ESTABLISHED'})
    save(out, 'partial_write_revalidation.json', {'status': 'SOURCE_LEVEL_FAULT_INJECTION_PASS',
         'count': 4, 'checks': partials, 'PHYSICAL_POWER_LOSS_DURABILITY': 'NOT_ESTABLISHED'})


def run(fresh, rejected, results, rejects, out, bind_fixture_provenance):
    run_f01(fresh, rejected, out)
    run_f02(fresh, rejected, out)
    run_f03(fresh, rejected, out)
    run_crash(fresh, out)
    results['F01_complete_regressions'] = {'status': 'PASS'}
    results['F02_complete_regressions'] = {'status': 'PASS'}
    results['F03_exact_authority_mapping'] = {'status': 'PASS'}
    results['10_crash_4_partial_write'] = {'status': 'SOURCE_LEVEL_FAULT_INJECTION_PASS'}

"""Additional bounded counterexample and partial-publication diagnostics."""
import ast
import copy
import importlib
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True
io_events = []
# Reuse only the independently written I/O guard definitions, not candidate code
# or any guard override. No module main or fixture creation is evaluated here.
source = ast.parse((HERE / 'audit_checks.py').read_text())
definitions = [n for n in source.body if isinstance(n, ast.FunctionDef) and n.name in {'owned', 'hook'}]
exec(compile(ast.Module(body=definitions, type_ignores=[]), str(HERE / 'audit_checks.py'), 'exec'))
sys.addaudithook(hook)
pkg = 'evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_resume_v1'
p = importlib.import_module(pkg + '.production_provider_successor_candidate')
c = importlib.import_module(pkg + '.production_controller_successor_candidate')
q = importlib.import_module(pkg + '.synthetic_e2e_qualifier')
a, ledger = p.a, p.ledger
WORK = HERE / 'additional_synthetic'
WORK.mkdir(exist_ok=False)

def fixture(label):
    actual = WORK / label
    lexical = p.QUALIFICATION_ROOT / os.path.relpath(actual, p.QUALIFICATION_ROOT)
    assert lexical.resolve() == actual
    path, items = q.fixture(lexical)
    return c.ProductionController.synthetic(path), items, actual

def snap(root):
    return {str(f.relative_to(root)): a.sha(f.read_bytes()) for f in root.rglob('*') if f.is_file()}

def reject(call):
    try:
        call()
    except (ValueError, KeyError, OSError) as exc:
        return {'rejected': True, 'exception': type(exc).__name__, 'reason': str(exc)}
    return {'rejected': False}

def write(name, data):
    with (HERE / name).open('x') as f:
        json.dump(data, f, sort_keys=True, indent=2); f.write('\n')

ctrl, items, root = fixture('connected_path_correlation')
admission = ctrl.prepare(items[0])
bundle = p.exact_json(ctrl.authority.root / 'raw_fixture.json')
original_sockets = bundle['sources']['unix_sockets']['raw_utf8']
changed = original_sockets.replace('3697 /run/buildkit/buildkitd.sock', '3697 /tmp/unknown-control.sock')
assert changed != original_sockets
q.rewrite_raw_object(ctrl.authority.root, 'unix_sockets', changed)
d = a.loads(bundle['sources']['daemon']['raw_utf8'].encode()); d['sockets'] = changed
q.rewrite_raw_object(ctrl.authority.root, 'daemon', d)
fresh = ctrl.authority.observe('PRECLAIM')
assert fresh['security_projection_sha256'] == admission.issuance_observation['security_projection_sha256']
claim = ctrl.claim(admission)
provider = p.ProductionProvider(ctrl.authority, items[0], claim, admission.receipt_raw)
write('client_endpoint_correlation_reproduction.json', {
    'status':'FAIL_INCONSISTENT_RAW_ENDPOINT_ACCEPTED', 'unchanged_candidate_normal_constructors':True,
    'claim_durable': (root / 'ledger/claims' / (items[0]['base_attempt_id'] + '.json')).is_file(),
    'provider_constructor_independent_verification_also_accepted':True,
    'socket_inode':'3697','observed_connected_path':'/tmp/unknown-control.sock',
    'census_and_proof_endpoint':a.loads(bundle['sources']['client_census']['raw_utf8'].encode())['sessions'][0]['endpoint'],
    'security_projection_unchanged':True,'raw_hash_changed':fresh['raw_observation_sha256'] != admission.issuance_observation['raw_observation_sha256'],
    'unknown_listeners_added':False,'client_proof_changed':False,'real_authorization_claimed':False,
    'fixture_root':str(root),'claim_sha256':a.identity(claim),
    'scope':'Synthetic internally contradictory raw/provenance evidence accepted; no live observer or real client authorization exercised.'})

results=[]
for kind in ('raw','receipt','association','claim'):
    ctrl, items, root=fixture('empty_file_' + kind)
    admission=ctrl.prepare(items[0]); hit=[]
    def trace(frame,event,arg):
        if event == 'line' and frame.f_code is ledger.exclusive_write.__code__ and frame.f_lineno == 55:
            path=frame.f_locals['path']
            match = ((kind=='raw' and path.name.endswith('.raw.json')) or
                     (kind=='receipt' and path.name.endswith('.receipt.json')) or
                     (kind=='association' and path.parent.name=='preclaim' and not path.name.endswith(('.raw.json','.receipt.json'))) or
                     (kind=='claim' and path.parent.name=='claims'))
            if match:
                hit.append(str(path));raise OSError('AUDIT_INJECTED_WRITE_FAILURE_AFTER_EXCLUSIVE_CREATE')
        return trace
    sys.settrace(trace)
    try:
        ctrl.claim(admission)
        raise AssertionError('partial-write injection missed')
    except OSError as exc:
        assert str(exc)=='AUDIT_INJECTED_WRITE_FAILURE_AFTER_EXCLUSIVE_CREATE'
    finally:
        sys.settrace(None)
    assert len(hit)==1 and Path(hit[0]).stat().st_size==0
    before=snap(root); retry=reject(lambda:ctrl.claim(admission))
    assert retry['rejected'] and before==snap(root)
    results.append({'operation':kind,'empty_retained_file':hit[0],'retry':retry,'no_overwrite':True,
                    'claims':len(list((root/'ledger/claims').iterdir())),'locks':len(list((root/'ledger/locks').iterdir()))})
write('partial_publication_reproduction.json',{'status':'PASS_FAIL_CLOSED_FOR_INJECTED_PARTIAL_WRITES','cases':results,
    'limitation':'Injected local write exceptions, not storage power-loss behavior; diagnostic roots exploit F01 and remain inside audit.'})
write('additional_io_events.json',{'events':io_events,'write_root':str(HERE),'network':False})
print('PASS additional diagnostics; connected path contradiction reproduced; four partial writes retained and blocked')

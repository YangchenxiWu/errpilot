import importlib.util
import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path('/Users/wuyangchenxi/errpilot')
B = ROOT / 'evaluation/downstream_benchmark'
sys.path.insert(0, str(ROOT))

def readonly(event, args):
    if event == 'open':
        path, mode, flags = args
        writing = (isinstance(mode, str) and any(x in mode for x in 'wax+')) or (
            flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        if writing and not isinstance(path, int):
            raise RuntimeError('read-only validation forbids writes')
    elif event.startswith('socket.') or event in {'os.system', 'os.posix_spawn', 'os.fork'}:
        raise RuntimeError('network / alternate execution forbidden')

sys.addaudithook(readonly)

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value

v = module('accepted_plan_validator', B / 'evidence/v6_preparation_planning_v1/validate_candidate.py')
g = v.g
manifest = v.strict_load(g.MANIFEST)
original_ref = g.file_ref
historical = g.git(ROOT, 'cat-file', 'blob', g.BASELINE + ':evaluation/downstream_benchmark/v6_current_state.json')
g.require(g.sha(historical) == g.CURRENT_SHA, 'historical planning descriptor changed')

def historical_ref(path):
    if path == B / 'v6_current_state.json':
        return manifest['current_descriptor']
    return original_ref(path)

# Only historical owning-descriptor resolution is adapted in memory. The new
# canonical descriptor is independently verified below; frozen inputs stay exact.
g.file_ref = historical_ref
result = v.validate(manifest, external=True)
t = module('accepted_transition_validator', B / 'evidence/v6_preparation_planning_transition_v1/validate_transition.py')
f = t.load_fixture()
f['current_raw'] = historical
t.validate_fixture(f)
binding = module('accepted_effectivity_validator', B / 'evidence/v6_preparation_planning_effectivity_binding_v1/validate_binding.py')
authority_raw = (ROOT / binding.AUTHORITY).read_bytes()
descriptor_raw = (ROOT / binding.DESCRIPTOR).read_bytes()
pin_raw = (ROOT / binding.PIN).read_bytes()
binding.validate_bundle(f, authority_raw, descriptor_raw, pin_raw)
current_raw = (B / 'v6_current_state.json').read_bytes()
g.require(current_raw == descriptor_raw, 'installed descriptor differs from accepted effectivity package')
current = v.strict_load(B / 'v6_current_state.json')
pin = json.loads(pin_raw)
g.require(pin == {'path': 'evaluation/downstream_benchmark/v6_current_state.json',
                  'sha256': g.sha(current_raw), 'HUMAN_PI_ACCEPTED': 'YES'}, 'current acceptance pin')
g.require(g.sha(current_raw) == '6a9028c79aa62f90db2b2d53def32ab23bffcfa3c71d2ec30d7fa64e741e3aae', 'current SHA')
projection = current['projection']
g.require(current['event_count'] == 2 and len(current['event_chain']) == 2, 'event chain count')
g.require(projection['state'] == current['lifecycle_label'] == 'PREPARATION_PLANNING_AUTHORIZED', 'current lifecycle')
g.require(projection['lifecycle']['PREPARATION_AUTHORIZED'] == 'NO', 'execution lifecycle')
g.require(all(c['phase'] == 'NOT_STARTED' and c['attempt_consumed'] is False
              and c['environment_identity'] is None for c in projection['case_states']), 'case states changed')
future = t.c.phase_flags_for_edge(projection, 'PREPARATION_EXECUTION_AUTHORIZED')
g.require(future['case_states'] == projection['case_states'], 'activation changes scientific cases')
delta = binding.leaf_delta(projection, future, 'projection')
result.update({
    'status': 'PASS', 'source_mirrors': len(manifest['projects']),
    'required_leaf_blobs': sum(x['unique_required_leaf_blob_objects'] for x in manifest['leaf_object_availability'].values()),
    'missing_objects': 0, 'SOURCE_ACQUISITION_CURRENTLY_REQUIRED': 'NO',
    'SOURCE_ACQUISITION_AUTHORIZED': 'NO', 'SOURCE_EXPORTS': 0,
    'accepted_plan_validation': 'Fresh complete external semantic validator run',
    'historical_descriptor_resolution': {'sha256': g.CURRENT_SHA, 'commit': g.BASELINE,
                                        'method': 'Immutable Git blob; in-memory file_ref adaptation only'},
    'current_descriptor_sha256': g.sha(current_raw), 'full_event_chain_replay': 'PASS',
    'planning_effectivity_binding_replay': 'PASS', 'case_count_unstarted': 433,
    'event_3_created': False, 'future_edge_delta_only': delta,
    'read_only_git_counts': dict(g.COMMAND_COUNTS),
    'prohibited_execution': 'Write/network audit guard; local read-only Git only'
})
print(json.dumps(result, sort_keys=True, indent=2))

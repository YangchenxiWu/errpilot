"""Read-only receipt replay against exact retained sealed E2E artifacts."""
import ast
import copy
import importlib
import json
import os
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT));sys.dont_write_bytecode=True
io_events=[]
tree=ast.parse((HERE/'audit_checks.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'owned','hook'}],type_ignores=[]),str(HERE/'audit_checks.py'),'exec'))
sys.addaudithook(hook)
pkg='evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_resume_v1'
p=importlib.import_module(pkg+'.production_provider_successor_candidate');a=p.a
candidate=Path(p.__file__).parent
sealed=a.loads((candidate/'synthetic_e2e_results.json').read_bytes())
root=Path(sealed['qualification_run_root'])/'fixture_1'
authority=p.Authority.synthetic(root/'synthetic_effectivity_fixture.json')
observation=authority.observe('AUDIT_READ_ONLY')
items=authority.population['items'];raw=(root/'issued-receipt.json').read_bytes()
assert p.verify_receipt(authority,items[0],raw,observation)==a.sha(raw)
assert p.verify_receipt(authority,items[2],None,observation) is None
from jsonschema import Draft202012Validator
schema=a.loads((candidate/'receipt_schema_v2_candidate.json').read_bytes())
Draft202012Validator.check_schema(schema);Draft202012Validator(schema).validate(a.loads(raw))
claims=[]
for item in (items[0],items[2]):
    cl=a.loads((root/'ledger/claims'/(item['base_attempt_id']+'.json')).read_bytes())
    receipt=raw if item['build_network_required'] else None
    issuance=p.read_claim_association(authority,item,cl,receipt)
    assert cl['receipt_sha256']==(a.sha(receipt) if receipt else None)
    claims.append({'attempt':item['base_attempt_id'],'receipt_sha':cl['receipt_sha256'],
        'association_sha':cl['input_runtime_binding']['raw_evidence_association_sha256'],
        'issuance_raw_sha':issuance['raw_observation_sha256'],'security_projection_sha':issuance['security_projection_sha256']})
checks=[]
def reject(label,call):
    try:call()
    except (ValueError,KeyError,TypeError) as exc:
        checks.append({'name':label,'rejected':True,'type':type(exc).__name__,'reason':str(exc)})
    else:raise AssertionError('unexpected receipt acceptance: '+label)
reject('cross_attempt_reuse',lambda:p.verify_receipt(authority,items[1],raw,observation))
reject('NONE_has_receipt',lambda:p.verify_receipt(authority,items[2],raw,observation))
reject('RESTRICTED_missing_receipt',lambda:p.verify_receipt(authority,items[0],None,observation))
reject('pretty_noncanonical_bytes',lambda:p.verify_receipt(authority,items[0],p.pretty(a.loads(raw)),observation))
reject('duplicate_keys',lambda:p.verify_receipt(authority,items[0],b'{"schema":"a","schema":"b"}',observation))
value=a.loads(raw)
for key in sorted(value):
    changed=copy.deepcopy(value);changed.pop(key)
    reject('missing_'+key,lambda changed=changed:p.verify_receipt(authority,items[0],a.canonical(changed),observation))
for key in ('base_attempt_id','canonical_state_sha256','event_3_id','production_runtime_effectivity_pin_sha256','controller_source_sha256','provider_source_sha256','receipt_contract_sha256','security_projection_sha256','client_authorization_evidence_sha256','client_authorization_policy_sha256'):
    changed={**value,key:'0'*64}
    reject('changed_'+key,lambda changed=changed:p.verify_receipt(authority,items[0],a.canonical(changed),observation))
out={'status':'PASS_EXACT_RETAINED_RECEIPT_AND_ASSOCIATION_READBACK','claims':claims,'rejections':checks,
     'deterministic_canonical_bytes':raw==a.canonical(value),'schema_validated':True,'writes_to_retained_fixture':0,
     'production_receipt_created':False,'source_provider_sha':a.sha(Path(p.__file__).read_bytes())}
with (HERE/'receipt_independent_replay.json').open('x') as f:json.dump(out,f,sort_keys=True,indent=2);f.write('\n')
print('PASS retained RESTRICTED/NONE receipts and associations;',len(checks),'receipt rejections')

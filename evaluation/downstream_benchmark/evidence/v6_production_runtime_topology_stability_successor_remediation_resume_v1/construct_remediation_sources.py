"""Construct one new versioned pair from exact immutable predecessor bytes."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path('/Users/wuyangchenxi/errpilot')
OLD_NAME = 'v6_production_runtime_topology_stability_successor_resume_v1'
NEW_NAME = 'v6_production_runtime_topology_stability_successor_remediation_resume_v1'
BASE = ROOT / 'evaluation/downstream_benchmark/evidence' / OLD_NAME
OUT = BASE.parent / NEW_NAME


def change(text, old, new, count=1):
    assert text.count(old) == count, old
    return text.replace(old, new)


def write(name, raw):
    with (OUT / name).open('xb') as stream:
        stream.write(raw.encode() if isinstance(raw, str) else raw)


def main():
    original = {}
    for role, sha in [('controller', '93696b9a6e6fa7bd3c207c27e0b6c098bd1d68aa8781167edc4c74bc9cc5de41'),
                      ('provider', '8731a0ab7eb8605201b754c366b601c9f821e5eaa8c2d52204bbcdab8eaf809c')]:
        raw = (BASE / ('production_' + role + '_successor_candidate.py')).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == sha
        original[role] = raw.decode()
    controller = original['controller'].replace(OLD_NAME, NEW_NAME)
    provider = original['provider'].replace(OLD_NAME, NEW_NAME)
    for role in ('controller', 'provider'):
        old = 'production_' + role + '_successor_candidate'
        new = 'production_' + role + '_remediated_candidate'
        controller = controller.replace(old, new)
        provider = provider.replace(old, new)
    provider = change(provider, 'from pathlib import Path\n',
                      'from pathlib import Path\n\nfrom evaluation.downstream_benchmark.evidence.'
                      + NEW_NAME + '.qualification_io import (\n'
                      '    ConfinedPath, QualificationIO, anchored_manifest_entries, checked,\n)\n'
                      'from evaluation.downstream_benchmark.evidence.' + NEW_NAME
                      + ' import socket_endpoint_binding as endpoint_binding\n')
    provider = change(provider,
                      '            ledger.safe_path(_qualification_fixture)\n'
                      '            a.require(_qualification_fixture.is_relative_to(QUALIFICATION_ROOT), "synthetic authority outside qualification")\n'
                      '            self.mode, self.fixture_path = SYNTHETIC, _qualification_fixture',
                      '            fixture = checked(_qualification_fixture)\n'
                      '            self.io = QualificationIO(fixture.parent).bind()\n'
                      '            self.mode, self.fixture_path = SYNTHETIC, ConfinedPath(fixture, io=self.io)')
    provider = change(provider,
                      '            self.root = Path(p["qualification_root"])\n'
                      '            ledger.safe_path(self.root)\n'
                      '            a.require(self.root.is_relative_to(QUALIFICATION_ROOT), "real ledger root forbidden in synthetic mode")',
                      '            self.root = ConfinedPath(checked(p["qualification_root"]), io=self.io)\n'
                      '            a.require(self.root == self.fixture_path.parent, "F01 fixture/root namespace alias")\n'
                      '            self.io.path(self.root)')
    provider = change(provider,
                      '            a.require(authority.root.is_relative_to(QUALIFICATION_ROOT), "synthetic real ledger forbidden")',
                      '            authority.io.path(authority.root)\n'
                      '            a.require(authority.root == authority.fixture_path.parent, "F01 ledger namespace alias")')
    provider = change(provider, 'class ReceiptBoundLedger(ledger.Ledger):',
                      'def fs(authority):\n'
                      '    a.require(type(authority) is Authority, "unrecognized filesystem authority")\n'
                      '    return ledger if authority.mode == REAL else authority.io\n\n\n'
                      'class ReceiptBoundLedger(ledger.Ledger):')
    provider = change(provider,
                      '"""V1 adds receipt_sha256 atomically; all durable filesystem helpers are inherited."""',
                      '"""Same once-only records; synthetic syscall boundaries are descriptor-confined."""')
    # Only candidate-owned functions that can write synthetic artifacts are changed.
    for name in ('ReceiptBoundLedger', 'ProductionProvider', 'publish_raw_association'):
        tree = ast.parse(provider)
        node = next(n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name == name) if name != 'ReceiptBoundLedger' else next(
            n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name)
        lines = provider.splitlines(keepends=True)
        body = ''.join(lines[node.lineno - 1:node.end_lineno])
        authority = 'self.authority' if name != 'publish_raw_association' else 'authority'
        for method in ('exclusive_write', 'mkdir_durable', 'persist_tree', 'fsync_dir'):
            body = body.replace('ledger.' + method + '(', 'fs(' + authority + ').' + method + '(')
        provider = ''.join(lines[:node.lineno - 1]) + body + ''.join(lines[node.end_lineno:])
    # Preserve the exact frozen terminal record logic, changing only I/O dispatch.
    frozen = (ROOT / 'evaluation/downstream_benchmark/screening/v6_preparation_ledger.py').read_text()
    cls = next(n for n in ast.parse(frozen).body if isinstance(n, ast.ClassDef) and n.name == 'Ledger')
    terminal = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'terminal')
    body = '\n'.join(frozen.splitlines()[terminal.lineno - 1:terminal.end_lineno])
    body = body.replace('atomic_publish(', 'fs(self.authority).atomic_publish(')
    body = body.replace('        lock.unlink()\n        fsync_dir(lock.parent)',
                        '        if self.namespace == SYNTHETIC:\n'
                        '            self.authority.io.unlink(lock)\n'
                        '        else:\n            lock.unlink()\n            ledger.fsync_dir(lock.parent)')
    provider = change(provider, '\n\ndef verify_claim(', '\n\n' + body + '\n\n\ndef verify_claim(')
    provider = change(provider,
                      '    bound["docker"], bound["docker_observation"] = docker, docker',
                      '    bound["docker"], bound["docker_observation"] = docker, docker\n'
                      '    if transport.provider.authority.mode == SYNTHETIC:\n'
                      '        bound["_manifest_entries"] = anchored_manifest_entries')
    provider = change(provider, '        path = Path(args[9])\n        ledger.safe_path(path)',
                      '        path = ConfinedPath(checked(args[9]), io=self.provider.authority.io)\n'
                      '        self.provider.authority.io.path(path)')
    provider = change(provider,
                      '        proof = next(s for s in proofs if s["session_id"] == session["session_id"])',
                      '        proof = next(s for s in proofs if s["session_id"] == session["session_id"])\n'
                      '        endpoint_binding.verify_authority_leaf(proof)')
    provider = change(provider,
                      'def verify_clients(census, evidence, socket_rows, *, synthetic, accepted_principals):',
                      'def verify_clients(census, evidence, socket_rows, *, synthetic, accepted_principals,\n'
                      '                   socket_access, listener_inventory):')
    provider = change(provider, '    a.require(connected == covered, "unattributed connected Unix socket/client")',
                      '    a.require(connected == covered, "unattributed connected Unix socket/client")\n'
                      '    endpoint_binding.verify_endpoint_binding(census, evidence, socket_rows, socket_access, listener_inventory)')
    provider = change(provider, '                            synthetic=synthetic, accepted_principals=accepted_principals)',
                      '                            synthetic=synthetic, accepted_principals=accepted_principals,\n'
                      '                            socket_access=access, listener_inventory=inventory)')
    provider = change(provider, '    "receipt_schema_v2_candidate.json", "raw_sidecar_contract_candidate.json",',
                      '    "receipt_schema_v2_candidate.json", "raw_sidecar_contract_candidate.json",\n'
                      '    "client_socket_endpoint_binding_contract_v3_candidate.json",')
    controller = change(controller, 'ledger.persist_tree(path)', 'provider.fs(self.authority).persist_tree(path)')
    for role, value in [('controller', controller), ('provider', provider)]:
        ast.parse(value)
        write('production_' + role + '_remediated_candidate.py', value)
    contract_names = ['receipt_authority_contract_v2_candidate.json', 'receipt_schema_v2_candidate.json',
                      'client_authorization_contract_candidate.json', 'topology_stability_contract_candidate.json',
                      'raw_observation_contract_candidate.json', 'transient_diagnostics_contract_candidate.json',
                      'raw_sidecar_contract_candidate.json']
    for name in contract_names:
        write(name, (BASE / name).read_bytes())
    old_ref = {'path': str((BASE / 'client_authorization_contract_candidate.json').relative_to(ROOT)),
               'sha256': hashlib.sha256((BASE / 'client_authorization_contract_candidate.json').read_bytes()).hexdigest()}
    write('client_socket_endpoint_binding_contract_v3_candidate.json', json.dumps({
        'schema': 'V6_CLIENT_SOCKET_ENDPOINT_BINDING_CONTRACT_V3_CANDIDATE',
        'candidate_only': True, 'HUMAN_PI_ACCEPTED': 'NO', 'runtime_effective': 'NO',
        'execute_now': False, 'supplements_without_editing': old_ref,
        'supersedes_incomplete_socket_correlation': 'Original V2 inode-list-only verification',
        'receipt_scope_schema_unchanged': True,
        'named_socket': 'Actual Path equals normalized proven unix control endpoint; contradiction rejects',
        'anonymous_socket': 'Independently authenticated exact peer/session endpoint association required; never fill Path',
        'proof_body_schema': 'V6_INDEPENDENT_SESSION_SOCKET_ASSOCIATION_V3',
        'proof_bindings': ['session_id', 'process_identity', 'endpoint', 'principal', 'classification',
                          'socket_namespace', 'user_namespace', 'complete actual socket rows and attributes',
                          'exact observed socket access identity', 'pathless independent peer association'],
        'boundary_body_schema': 'V6_INDEPENDENT_ENDPOINT_ACCESS_BOUNDARY_V3',
        'real_observer_dependency': 'Existing separately accepted authenticated fixed observer; absent, real BLOCKED',
        'C1_C16': 'Inherited unchanged, no origin or authorization inferred from matching metadata',
        'F03_mapping': 'runtime_authority_false => actual V2 client proof authenticated_source Boolean authority leaf',
        'F01_limit': 'Descriptor-relative no-follow operations and namespace inode pins; privileged directory relocation excluded'
    }, indent=2, sort_keys=True) + '\n')
    print('Constructed new candidate sources and supplementary V3 contract; none effective')


if __name__ == '__main__':
    main()

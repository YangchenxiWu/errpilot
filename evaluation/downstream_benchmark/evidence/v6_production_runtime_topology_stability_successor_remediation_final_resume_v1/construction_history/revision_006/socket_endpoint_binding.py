"""V3 supplementary independent session/socket evidence binding for F02/F03."""
from __future__ import annotations

import copy
from pathlib import PurePosixPath
from urllib.parse import urlsplit

from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a


def endpoint_path(endpoint):
    a.require(type(endpoint) is str, 'F02 invalid endpoint normalization')
    parsed = urlsplit(endpoint)
    parts = parsed.path.split('/')[1:]
    a.require(parsed.scheme == 'unix' and parsed.netloc == '' and parsed.query == ''
              and parsed.fragment == '' and parsed.path.startswith('/')
              and all(part not in {'', '.', '..'} for part in parts)
              and '%' not in endpoint and '\\' not in endpoint
              and endpoint == 'unix://' + str(PurePosixPath(parsed.path)),
              'F02 invalid endpoint normalization')
    return parsed.path


def independent_body(session, proof, rows, access, inventory):
    """Exact structure used by hermetic fixtures and independently parsed by verifier.

    This constructor never creates authorization or fills missing socket Path.
    Real evidence must originate from the separately accepted authenticated observer.
    """
    return {'schema': 'V6_INDEPENDENT_SESSION_SOCKET_ASSOCIATION_V3',
            'session_id': session['session_id'], 'process_identity': session['process_identity'],
            'endpoint': session['endpoint'], 'principal': proof['principal'],
            'classification': proof['classification'],
            'socket_namespace': session.get('socket_namespace'),
            'observed_socket_namespace': inventory.get('socket_namespace'),
            'user_namespace': session.get('user_namespace'),
            'observed_user_namespace': inventory.get('user_namespace'),
            'socket_rows': copy.deepcopy(rows), 'socket_access_sha256': a.identity(access),
            'independent_inaccessibility': proof['independent_inaccessibility'],
            'pathless_independent_association': proof.get('pathless_independent_association', False),
            'independent_peer_endpoint': proof.get('independent_peer_endpoint')}


def verify_authority_leaf(proof):
    a.require(type(proof['authenticated_source']) is bool,
              'F03 client authenticated_source exact Boolean type required')
    a.require(proof['authenticated_source'] is True,
              'F03 client authenticated_source authority false')


def verify_endpoint_binding(census, evidence, rows, access, inventory):
    connected = [row for row in rows if row['St'] == '03']
    inodes = [row['Inode'] for row in connected]
    a.require(len(inodes) == len(set(inodes)), 'F02 ambiguous duplicate connected inode')
    a.require(type(inventory.get('socket_namespace')) is str
              and bool(inventory['socket_namespace'])
              and type(inventory.get('user_namespace')) is str
              and bool(inventory['user_namespace']), 'F02 unverifiable socket namespace')
    by_inode = {row['Inode']: row for row in connected}
    boundary = evidence['boundary']
    body = a.loads(boundary['original_source_utf8'].encode())
    a.require(body == {'schema': 'V6_INDEPENDENT_ENDPOINT_ACCESS_BOUNDARY_V3',
                      'socket_access_sha256': a.identity(access),
                      'socket_namespace': inventory['socket_namespace'],
                      'user_namespace': inventory['user_namespace']},
              'F02 independent endpoint access proof mismatch')
    for session in census['sessions']:
        proof = next(p for p in evidence['sessions'] if p['session_id'] == session['session_id'])
        associated = []
        if proof['classification'] == 'AUTHORIZED':
            path = endpoint_path(session['endpoint'])
            a.require(path == '/run/buildkit/buildkitd.sock', 'F02 wrong control-plane endpoint')
            a.require(session.get('socket_namespace') == inventory['socket_namespace']
                      and session.get('user_namespace') == inventory['user_namespace'],
                      'F02 inconsistent socket/client namespace')
            access_matches = [x for x in access['endpoints'] if x['path'] == path]
            a.require(len(access_matches) == 1
                      and access_matches[0]['mount_namespace'] == inventory['socket_namespace']
                      and access_matches[0]['user_namespace'] == inventory['user_namespace'],
                      'F02 endpoint access namespace mismatch')
            for inode in session['socket_inodes']:
                a.require(inode in by_inode, 'F02 session inode not independently observed')
                row = by_inode[inode]
                a.require(row['Protocol'] == '00000000' and row['Type'] == '0001'
                          and row['Flags'] == '00000000' and row['St'] == '03',
                          'F02 inconsistent connected socket attributes')
                if row['Path']:
                    a.require(row['Path'] == path, 'F02 actual socket Path/endpoint conflict')
                else:
                    a.require(proof.get('pathless_independent_association') is True
                              and proof.get('independent_peer_endpoint') == session['endpoint'],
                              'F02 pathless independent session association unavailable')
                associated.append(row)
        else:
            a.require(proof['independent_inaccessibility'] is True
                      and session['control_capable'] is False and session['socket_inodes'] == [],
                      'F02 independent inaccessibility not established')
        body = a.loads(proof['original_source_utf8'].encode())
        a.require(body == independent_body(session, proof, associated, access, inventory),
                  'F02 independent session/socket provenance binding mismatch')

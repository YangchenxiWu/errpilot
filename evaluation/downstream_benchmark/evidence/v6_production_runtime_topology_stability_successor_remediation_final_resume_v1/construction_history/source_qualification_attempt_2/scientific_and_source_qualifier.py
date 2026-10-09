"""Read-only scientific replay and source delta for a lint-BLOCKED construction.
No qualification, constructor, receipt, ledger or native command is invoked.
"""
from __future__ import annotations

import ast
import difflib
import hashlib
import json
from collections import Counter
from pathlib import Path

from evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_remediation_final_resume_v1 import production_provider_remediated_candidate as p

ROOT = p.a.ROOT
OUT = ROOT / p.RESUME
PREDECESSOR = OUT.parent / "v6_production_runtime_topology_stability_successor_resume_v1"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(path):
    raw = path.read_bytes()
    return {"path": str(path), "size_bytes": len(raw), "sha256": sha(raw)}


def write(name, value):
    with (OUT / name).open("xb") as stream:
        stream.write((json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode())


def replay_scientific():
    from evaluation.downstream_benchmark.evidence.v6_preparation_execution_production_runtime_installation_resume_v1 import production_provider_candidate as old
    from evaluation.downstream_benchmark.evidence.v6_production_runtime_image_identity_compatibility_bridge_v1 import corrected_production_provider_candidate as corrected
    p.frozen_inputs()
    from evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_resume_v1 import production_provider_successor_candidate as predecessor
    _, manifest = p.a.load_inputs()
    raw = p.a.read_exact(p.legacy.PACKAGE + "work_items_candidate.json", p.legacy.WORK_SHA)
    population = p.a.loads(raw)
    p.validate_real_population(p.population_identity(population, raw))
    p.a.validate_population(manifest, population)
    maps = p.exact_json(ROOT / p.NATIVE / "seven_base_transport_map.json")["mapping"]
    replay = []
    config = p.frozen_inputs()
    for item in population["items"]:
        plan = p.a.select(manifest, ordinal=item["census_order"], case_id=item["case_id"], plan_sha=item["plan_sha256"])
        p.a.require(item == p.a.work_item(plan, item["variant"]), "frozen work item drift")
        marker = b"SYNTHETIC_COMPILE_ONLY_NO_RECEIPT_AUTHORITY\n" if item["build_network_required"] else None
        compiled = p.compile_production_transport(item, plan, {}, receipt_raw=marker)
        prior = old.compile_production_transport(item, plan, {}, receipt_raw=marker)
        correction = corrected.compile_production_transport(item, plan, {}, receipt_raw=marker)
        p.a.require(compiled == prior == correction == predecessor.compile_production_transport(item, plan, {}, receipt_raw=marker), "scientific/native transport projection drift")
        expected = p.a.shared.build_definition(p.a.engine_recipe(plan), source_present=item["variant"] != "SOURCE_INDEPENDENT",
            dependency_present=plan["recipe_candidate"]["requirements"]["dependency_bytes_b64"] is not None)
        p.a.require(compiled["scientific_dockerfile"] == expected, "Dockerfile/RUN byte/order drift")
        base = next(x for x in maps if x["scientific_base_authority"] == item["base_image_reference"])
        binding = {**base, "endpoint": config["endpoint"], "native_binary_sha256": config["client_binary_sha256"],
            "same_daemon": True, "daemon_count": 1, "runtime_reference": config["runtime_image"]["immutable_reference"],
            "frontend_alias": "errpilot_frozen_base", "container_id": "SYNTHETIC_DAEMON", "container_root": "/tmp/errpilot-v6-compile-only",
            "tag": "errpilot-synthetic-compile-only", "proxy_internal_host_binding": "add-hosts=" + config["proxy"]["proxy_name"] + "=172.28.0.3", "compiled": compiled}
        argv = p.native.native_argv(binding, binding["container_root"], binding["tag"], compiled)
        p.a.require(argv == old.native.native_argv(binding, binding["container_root"], binding["tag"], prior)
                    == corrected.native.native_argv(binding, binding["container_root"], binding["tag"], correction), "native argv drift")
        p.validate_command(["docker", "exec", binding["container_id"], *argv], binding)
        replay.append({"base_attempt_id": item["base_attempt_id"], "work_item_sha256": p.a.identity(item), "case_id": item["case_id"],
            "variant": item["variant"], "network": "RESTRICTED_DEFAULT" if item["build_network_required"] else "NONE",
            "scientific_dockerfile_sha256": sha(compiled["scientific_dockerfile"]), "execution_dockerfile_sha256": sha(compiled["execution_dockerfile"]),
            "native_argv_sha256": p.a.identity(argv), "base_authority": item["base_image_reference"], "status": "PASS_EXACT_BYTES_COMMAND_PROJECTION"})
    counts = dict(Counter(x["variant"] for x in population["items"]))
    p.a.require(counts == {"SOURCE_INDEPENDENT": 221, "BUGGY": 210, "FIXED": 210}, "variant population drift")
    p.a.require([x["case_id"] for x in population["blocked"]] == ["matplotlib::1", "matplotlib::8"], "blocked case drift")
    return {"schema": "V6_SUCCESSOR_641_EXACT_SCIENTIFIC_NATIVE_REPLAY_V2", "status": "PASS", "population": p.population_identity(population, raw),
        "variants": counts, "blocked_cases": ["matplotlib::1", "matplotlib::8"], "per_item_replay": replay, "replayed_count": 641,
        "exact_tested_provider": identity(Path(p.__file__)), "RUN_bytes_and_order_equal": True, "native_commands_executed": 0,
        "real_builds": 0, "real_source_export": 0, "oracle": 0, "scientific_validation_claimed": False}


def function_inventory(path):
    raw = path.read_text()
    tree = ast.parse(raw)
    result = {}
    def visit(nodes, prefix=""):
        for node in nodes:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = prefix + node.name
                text = "\n".join(raw.splitlines()[node.lineno - 1:node.end_lineno])
                result[name] = {"ast_sha256": sha(ast.dump(node, include_attributes=False).encode()),
                                "text_sha256": sha(text.encode()), "line": node.lineno,
                                "end_line": node.end_lineno}
                visit(node.body, name + ".")
            elif isinstance(node, ast.ClassDef):
                visit(node.body, prefix + node.name + ".")
    visit(tree.body)
    return result



def deltas():
    comparisons = {}
    categories = {
        'verify_clients': 'F02 endpoint/socket/session provenance; F03 exact Boolean authority',
        'verify_raw_security': 'F02 required endpoint access/inventory interface',
        'shared_scientific_engine': 'F01 confined descriptor-root manifest adapter; frozen code objects preserved',
        'fs': 'F01 explicit descriptor-relative synthetic filesystem dispatch',
        'ReceiptBoundLedger.terminal': 'F01 no-follow durable publication; qualify frozen ledger.SUCCESS references',
    }
    for label, directory, suffix in [
        ('original_V2', PREDECESSOR, 'successor'),
        ('failed_remediation', OUT.parent / 'v6_production_runtime_topology_stability_successor_remediation_resume_v1', 'remediated')]:
        comparisons[label] = {}
        for role in ('controller', 'provider'):
            old_path = directory / ('production_' + role + '_' + suffix + '_candidate.py')
            new_path = OUT / ('production_' + role + '_remediated_candidate.py')
            old, new = function_inventory(old_path), function_inventory(new_path)
            changes = []
            for name in sorted(set(old) | set(new)):
                if old.get(name, {}).get('ast_sha256') == new.get(name, {}).get('ast_sha256'):
                    continue
                permitted = (name in categories or name.startswith(('Authority.', 'ReceiptBoundLedger.',
                              'ProductionController.', 'SyntheticScientificTransport.', 'SyntheticScenario.'))
                              or name in {'publish_raw_association', 'ProductionProvider.persist_command',
                                          'ProductionProvider.execute', 'ProductionProvider.execute_synthetic'})
                p.a.require(permitted, 'unauthorized function semantic delta: ' + name)
                changes.append({'function': name, 'before': old.get(name), 'after': new.get(name),
                    'authorized_finding_or_dependency': categories.get(name,
                        'F01 exact source/root/helper binding and descriptor-confined I/O'),
                    'qualification_basis': 'Actual final source-pair full E2E and security/fault regressions'})
            diff = ''.join(difflib.unified_diff(old_path.read_text().splitlines(keepends=True),
                                              new_path.read_text().splitlines(keepends=True),
                                              fromfile=str(old_path), tofile=str(new_path)))
            with (OUT / (label + '_' + role + '_source_delta.diff')).open('x') as stream:
                stream.write(diff)
            comparisons[label][role] = {'before': identity(old_path), 'after': identity(new_path),
                 'changed_functions': changes,
                 'unchanged_functions': sorted(name for name in old if name in new
                    and old[name]['ast_sha256'] == new[name]['ast_sha256'])}
            for path, tag in [(old_path, label), (new_path, 'final')]:
                output = OUT / (tag + '_' + role + '_source.ast.txt')
                if not output.exists():
                    with output.open('x') as stream:
                        stream.write(ast.dump(ast.parse(path.read_bytes()), include_attributes=False, indent=2) + '\n')
    scientific = ['compile_production_transport', 'validate_command', 'verify_layout',
                  'NativeProductionTransport.invoke', 'NativeProductionTransport.check',
                  'NativeProductionTransport.build', 'image_identity_pins', 'verify_image_identity',
                  'normalize_topology', 'verify_routes']
    current = function_inventory(Path(p.__file__))
    for name in scientific:
        for directory, suffix in [(PREDECESSOR, 'successor'),
            (OUT.parent / 'v6_production_runtime_topology_stability_successor_remediation_resume_v1', 'remediated')]:
            previous = function_inventory(directory / ('production_provider_' + suffix + '_candidate.py'))
            p.a.require(current[name]['ast_sha256'] == previous[name]['ast_sha256'],
                        'protected scientific/security function drift: ' + name)
    helpers = {name: {'source': identity(OUT / name), 'functions': function_inventory(OUT / name),
                     'finding': 'F01' if name == 'qualification_io.py' else 'F02/F03'}
               for name in p.HELPER_SHA256}
    p.a.require(all(identity(OUT / name)['sha256'] == digest for name, digest in p.HELPER_SHA256.items()),
                'helper pin drift')
    contracts = ['receipt_authority_contract_v2_candidate.json', 'receipt_schema_v2_candidate.json',
                 'client_authorization_contract_candidate.json', 'topology_stability_contract_candidate.json',
                 'raw_observation_contract_candidate.json', 'transient_diagnostics_contract_candidate.json',
                 'raw_sidecar_contract_candidate.json']
    p.a.require(all((OUT / name).read_bytes() == (PREDECESSOR / name).read_bytes() for name in contracts),
                'historical V2 contract changed')
    write('contract_version_disposition.json', {'status': 'PASS',
          'V2_contracts_byte_exact': {name: identity(OUT / name) for name in contracts},
          'C1_C16_byte_exact': True, 'V1_preserved_by_tracked_and_predecessor_firewall': True,
          'V3_required': True, 'reason': 'Independent full socket-row/session/access-boundary correlation is absent from V2 inode-list-only contract.',
          'V3_candidate': identity(OUT / 'client_socket_endpoint_binding_contract_v3_candidate.json'),
          'historical_failed_V3_preserved': True, 'HUMAN_PI_ACCEPTED': 'NO',
          'no_old_V2_schema_amended': True, 'real_observer_dependency': 'Absent; real authorization BLOCKED'})
    return {'status': 'PASS', 'comparisons': comparisons, 'new_internal_helpers': helpers,
            'scientific_compiler_function_AST_exact': True,
            'protected_functions_AST_exact': scientific, 'frozen_sources_modified': False,
            'module_level_delta_scope': 'Candidate imports, exact source location, exact qualification root and helper hashes only',
            'V1_V2_contracts_preserved': True, 'C1_C16_unchanged': True}


def main():
    before = {name: id(value) for name, value in p.a.shared.__dict__.items()}
    write('source_semantic_delta.json', deltas())
    result = replay_scientific()
    p.a.require(before == {name: id(value) for name, value in p.a.shared.__dict__.items()},
                'frozen scientific globals changed')
    result.update(status='PASS_IMPLEMENTATION_EQUIVALENCE_ONLY', environment_ready_cases=0,
                  inherited_shared_function_code_objects_unchanged=True,
                  scientific_validation_claimed=False, tested_helper_pins=p.HELPER_SHA256)
    write('scientific_projection_revalidation.json', result)
    print(json.dumps({'status': result['status'], 'count': result['replayed_count'],
                      'source_delta': 'PASS', 'native_commands_executed': 0}))


if __name__ == '__main__':
    main()

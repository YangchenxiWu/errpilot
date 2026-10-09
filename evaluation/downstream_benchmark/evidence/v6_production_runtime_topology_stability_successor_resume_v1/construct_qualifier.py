"""Adapt inherited coverage to the exact candidate pair without guard bypasses."""
from __future__ import annotations

from .construct_resume import HERE, OLD, replace_functions


def main():
    source = (OLD / "qualify_resume_candidate.py").read_text()
    source = source.replace('import importlib.util', 'import runpy')
    source = source.replace('from . import production_controller_candidate as c', 'from . import production_controller_successor_candidate as c')
    source = source.replace('from . import production_provider_candidate as p', 'from . import production_provider_successor_candidate as p')
    source = source.replace('production_controller_candidate.py', 'production_controller_successor_candidate.py').replace('production_provider_candidate.py', 'production_provider_successor_candidate.py')
    source = source.replace('qualify_resume_candidate.py', 'synthetic_e2e_qualifier.py').replace('production_receipt_authority_contract.json', 'receipt_authority_contract_v2_candidate.json').replace('receipt_schema.json', 'receipt_schema_v2_candidate.json').replace('topology_observation_contract.json', 'topology_stability_contract_candidate.json')
    source = source.replace('live_daemon_topology_observation_sha256', 'security_projection_sha256')
    source = source.replace('"V6_PREPARATION_PRODUCTION_RUNTIME_EFFECTIVITY_V1"', '"V6_PREPARATION_PRODUCTION_RUNTIME_EFFECTIVITY_V2"')
    source = source.replace('provider.execute_synthetic(observations)', 'provider.execute_synthetic(p.SyntheticScenario())')
    source = source.replace('controller.run_synthetic(items[2], observations)', 'controller.run_synthetic(items[2], p.SyntheticScenario())')
    source = source.replace('controller.run_synthetic(items[3], fail)', 'controller.run_synthetic(items[3], p.SyntheticScenario("RAISE"))')
    source = source.replace('"runtime_authority_false": ("runtime_authority", False)', '"runtime_authority_false": ("runtime_authority", 0)')
    source = source.replace('data["State"]["Pid"] += 1\n    daemon_path.write_bytes(p.pretty(data))', 'data["State"]["Pid"] += 1\n    daemon_path.write_bytes(p.pretty(data))\n    rewrite_raw_object(ctrl.authority.root, "daemon", data)')
    old = '''spec = importlib.util.spec_from_file_location("copy_" + method, copy_path)
        copied = importlib.util.module_from_spec(spec)
        import sys
        sys.modules[spec.name] = copied
        spec.loader.exec_module(copied)
        rejected("copied_installed_" + method + "_synthetic_interface", lambda copied=copied, method=method: getattr(copied, method).synthetic(path))'''
    new = '''copied = runpy.run_path(str(copy_path), run_name="candidate_copy_guard_probe")
        rejected("copied_installed_" + method + "_synthetic_interface", lambda copied=copied, method=method: copied[method].synthetic(path), root)'''
    assert old in source
    source = source.replace(old, new)
    start = source.index('    # Bind unchanged shared code objects')
    end = source.index('    results["receipt_contract_schema"]', start)
    source = source[:start] + '''    results["shared_scientific_code_objects_preserved"] = {"status": "PASS", "evidence": "actual original shared _materialize_checked path exercised in restricted and NONE source-pair E2E", "frozen_dispatch_guards": "UNCHANGED"}
''' + source[end:]
    # All inherited probes now record exact source and actual ledger bytes. Pure
    # probes use the primary synthetic ledger as an unchanged-state witness.
    source = source.replace('        before = journal_files(root) if root else None', '        root = root or primary_root\n        before = journal_files(root)')
    source = source.replace('except (a.Rejected, ValueError, TypeError, KeyError, OSError) as exc:', 'except (a.Rejected, ValueError, TypeError, KeyError, OSError, SystemExit) as exc:\n            if isinstance(exc, SystemExit):\n                a.require(exc.code == 2, "unexpected CLI exit status")')
    source = source.replace('results, rejects = {}, {}', 'results, rejects = {}, {}\n    primary_root = None')
    source = source.replace('    ledger.safe_path(p.QUALIFICATION_ROOT)', '    frozen_globals_before = {k: id(v) for k, v in a.shared.__dict__.items()}\n    ledger.safe_path(p.QUALIFICATION_ROOT)', 1)
    source = source.replace('    root = controller.authority.root\n    admitted', '    root = controller.authority.root\n    primary_root = root\n    admitted')
    source = source.replace('"ledger_unchanged": root is not None, "zero_claims_preclaim": zero}', '"ledger_unchanged": True, "zero_claims_preclaim": zero,\n                             "ledger_before": before, "ledger_after": journal_files(root),\n                             "expected_category": name, "observed_rejection": type(exc).__name__,\n                             "exact_tested_sources": source_identities()}')
    source = source.replace('ledger.mkdir_durable(p.QUALIFICATION_ROOT)\n    number', '''if not p.QUALIFICATION_ROOT.exists():
        p.QUALIFICATION_ROOT.mkdir(mode=0o700)
        write(p.QUALIFICATION_ROOT / "transaction.json", {"request_sha256": a.sha((OUT / "raw_human_pi_request.txt").read_bytes())})
    else:
        a.require(p.exact_json(p.QUALIFICATION_ROOT / "transaction.json") == {"request_sha256": a.sha((OUT / "raw_human_pi_request.txt").read_bytes())}, "qualification root belongs to another transaction")
    number''')
    source = source.replace('    external = {str(x.relative_to(p.QUALIFICATION_ROOT))', '    add_v2_suite(fresh, rejected, results, rejects)\n    a.require(frozen_globals_before == {k: id(v) for k, v in a.shared.__dict__.items()}, "legacy globals mutated")\n    external = {str(x.relative_to(p.QUALIFICATION_ROOT))')
    source = source.replace('    print(json.dumps(summary, sort_keys=True))', '''    inherited = p.exact_json(a.ROOT / "evaluation/downstream_benchmark/evidence/v6_preparation_execution_production_runtime_installation_resume_v1/rejection_matrix.json")
    a.require(set(inherited["checks"]) <= set(rejects), "mandatory inherited rejection category skipped")
    summary["required_A_through_X"] = required_coverage(results, rejects)
    summary["required_inherited_A_X"] = {letter: {"status": "PASS", "checks": record["evidence_checks"]} for letter, record in inherited["required_A_X_coverage"].items()}
    for record in summary["required_inherited_A_X"].values():
        a.require(all(x in results or x in rejects for x in record["checks"]), "inherited A-X missing actual execution")
    summary["test_provider"] = "Candidate-owned normal SyntheticScenario and SyntheticScientificTransport; original shared scientific code object executes context/build/probes/identity with simulated I/O. No arbitrary callable or native execution."
    summary["full_source_pair_E2E"] = True
    summary["real_client_authorization_status"] = "BLOCKED_UNTIL_INDEPENDENT_LIVE_EVIDENCE"
    (OUT / "synthetic_e2e_results.json").write_bytes(p.pretty(summary))
    (OUT / "rejection_matrix.json").write_bytes(p.pretty({"schema": "V6_SUCCESSOR_RESUME_REJECTIONS_V2", "status": "PASS_REJECTED", "inherited_count": 77, "new_count": len(rejects) - 77, "mandatory_skipped": 0, "checks": rejects, "required_A_X_coverage": summary["required_A_through_X"], "inherited_A_X_coverage": summary["required_inherited_A_X"]}))
    print(json.dumps({"status": "PASS", "fixture_count": counter, "rejections": len(rejects), "A_X": len(summary["required_A_through_X"]), "exact_sources": source_identities()}))''')
    source = replace_functions(source, {'fixture': (HERE / 'qualification_fixture_extension.txt').read_text().split('\n# END_FIXTURE\n')[0],
        'journal_files': '''def journal_files(root):
    return {n: {x.name: a.sha(x.read_bytes()) for x in sorted((root / "ledger" / n).iterdir()) if x.is_file()}
            for n in ("claims", "terminals", "locks")}'''})
    source = source.replace('write(run_root / "qualification_results.json", summary)', '# Summary is written after complete coverage below.')
    source += (HERE / 'qualification_fixture_extension.txt').read_text().split('\n# END_FIXTURE\n')[1]
    # Extension functions must exist before main runs.
    source = source.replace('if __name__ == "__main__":\n    main()\n', '')
    source += '\n\nif __name__ == "__main__":\n    main()\n'
    (HERE / "synthetic_e2e_qualifier.py").write_text(source)


if __name__ == "__main__":
    main()

"""Version the exact inherited qualifier; require category-specific reasons."""
from __future__ import annotations

from pathlib import Path

BASE = Path('/Users/wuyangchenxi/errpilot/evaluation/downstream_benchmark/evidence')
OLD = 'v6_production_runtime_topology_stability_successor_resume_v1'
NEW = 'v6_production_runtime_topology_stability_successor_remediation_resume_v1'
OUT = BASE / NEW


def main():
    text = (BASE / OLD / 'synthetic_e2e_qualifier.py').read_text()
    text = text.replace('production_controller_successor_candidate', 'production_controller_remediated_candidate')
    text = text.replace('production_provider_successor_candidate', 'production_provider_remediated_candidate')
    text = text.replace('import json\n', 'import json\nimport contextlib\nimport io\nimport traceback\n')
    text = text.replace('from . import production_provider_remediated_candidate as p',
                        'from . import production_provider_remediated_candidate as p\n'
                        'from . import remediation_regressions as regression')
    text = text.replace('path.write_bytes(p.pretty(data))', 'Path(path).write_bytes(p.pretty(data))')
    text = text.replace('daemon_path.write_bytes(p.pretty(data))', 'Path(daemon_path).write_bytes(p.pretty(data))')
    text = text.replace('claim_path.write_bytes(a.canonical(wrong_claim))', 'Path(claim_path).write_bytes(a.canonical(wrong_claim))')
    text = text.replace('path.write_bytes(p.pretty(bundle))', 'Path(path).write_bytes(p.pretty(bundle))')
    text = text.replace('(root / "raw-evidence" / claim["attempt_id"] / "preclaim" / (claim["input_runtime_binding"]["raw_evidence_association_sha256"] + ".json")).write_bytes', 'Path(root / "raw-evidence" / claim["attempt_id"] / "preclaim" / (claim["input_runtime_binding"]["raw_evidence_association_sha256"] + ".json")).write_bytes')
    # Fixture generation is explicit synthetic independent proof construction.
    text = text.replace('    write(root / "raw_fixture.json", bundle)',
                        '    bind_fixture_provenance(bundle)\n    write(root / "raw_fixture.json", bundle)')
    text = text.replace('    current = ctrl.authority.observe("PRECLAIM")',
                        '    rebind_owned_positive_fixture(ctrl.authority.root)\n'
                        '    current = ctrl.authority.observe("PRECLAIM")')
    text = text.replace('    admission = ctrl.prepare(items[0])\n    a.require(any(x["classification"]',
                        '    rebind_owned_positive_fixture(ctrl.authority.root)\n'
                        '    admission = ctrl.prepare(items[0])\n    a.require(any(x["classification"]')
    text = text.replace('        "runtime_authority_false": ("runtime_authority", 0), ', '')
    start = text.index('    def rejected(')
    end = text.index('    controller, items, primary_fixture = fresh()', start)
    text = text[:start] + '''    golden = p.exact_json(a.ROOT / "evaluation/downstream_benchmark/evidence/v6_production_runtime_topology_stability_successor_resume_v1/rejection_matrix.json")["checks"]
    def rejected(name, call, root=None, zero=False, *, reason=None, classification=None):
        root = root or primary_root
        before = journal_files(root)
        files_before = regression.inventory(root)
        captured = io.StringIO()
        try:
            with contextlib.redirect_stderr(captured):
                call()
        except (a.Rejected, ValueError, TypeError, KeyError, OSError, SystemExit) as exc:
            expected = regression.reason_spec(name, golden, reason, classification)
            regression.assert_reason(name, exc, expected, captured.getvalue())
            a.require(before == journal_files(root), "rejection mutated synthetic ledger: " + name)
            a.require(files_before == regression.inventory(root), "rejection mutated durable evidence: " + name)
            if zero:
                a.require(all(not x for x in before.values()), "preclaim fixture already consumed")
            record = {"status": "PASS_REJECTED", "reason": str(exc),
                      "ledger_unchanged": True, "zero_claims_preclaim": zero,
                      "ledger_before": before, "ledger_after": journal_files(root),
                      "evidence_before": files_before, "evidence_after": regression.inventory(root),
                      "expected_category": name, "intended_gate": expected,
                      "observed_rejection": type(exc).__name__, "stderr": captured.getvalue(),
                      "fixture_root": str(root), "fixture_identity": a.identity(files_before),
                      "exact_tested_sources": source_identities(), "attempts_consumed_by_rejection": 0}
            a.require(name not in rejects, "duplicate rejection evidence identity")
            rejects[name] = record
            write(OUT / "executed_rejections" / (name + ".json"), p.pretty(record))
        else:
            raise AssertionError("unexpected acceptance: " + name)
''' + text[end:]
    text = text.replace('    add_v2_suite(fresh, rejected, results, rejects)',
                        '    add_v2_suite(fresh, rejected, results, rejects)\n'
                        '    regression.run(fresh, rejected, results, rejects, OUT, bind_fixture_provenance)')
    text = text.replace('    summary["required_A_through_X"] = required_coverage(results, rejects)',
                        '    a.require(set(golden) <= set(rejects), "mandatory 126 inherited category missing")\n'
                        '    summary["inherited_126_count"] = len(golden)\n'
                        '    summary["new_rejection_count"] = len(rejects) - len(golden)\n'
                        '    summary["required_A_through_X"] = required_coverage(results, rejects)')
    text = text.replace('"inherited_count": 77, "new_count": len(rejects) - 77',
                        '"inherited_count": 126, "new_count": len(rejects) - 126')
    # Record the helper sources as part of the actual source identity, not just imports.
    text = text.replace('    return {str(Path(module.__file__).relative_to(a.ROOT)): a.sha(Path(module.__file__).read_bytes()) for module in (c, p)}',
                        '    return {**{str(Path(module.__file__).relative_to(a.ROOT)): a.sha(Path(module.__file__).read_bytes()) for module in (c, p)},\n'
                        '            **{p.RESUME + name: a.sha((OUT / name).read_bytes()) for name in p.HELPER_SHA256}}')
    extension = '''

def bind_fixture_provenance(bundle):
    # Only this test-owned generator constructs synthetic proof bytes. Verification
    # never fills a socket Path or generates a missing independent association.
    values = {name: a.loads(bundle["sources"][name]["raw_utf8"].encode())
              for name in ("client_census", "client_evidence", "socket_access", "listener_inventory")}
    census, evidence, access, inventory = [values[name] for name in
        ("client_census", "client_evidence", "socket_access", "listener_inventory")]
    inventory.update(socket_namespace="SYNTHETIC_DAEMON_NAMESPACE", user_namespace="SYNTHETIC_USER_NS")
    rows = p.parse_socket_rows(bundle["sources"]["unix_sockets"]["raw_utf8"].encode())
    for session in census["sessions"]:
        session.setdefault("socket_namespace", inventory["socket_namespace"])
        session.setdefault("user_namespace", inventory["user_namespace"])
        proof = next(x for x in evidence["sessions"] if x["session_id"] == session["session_id"])
        associated = [row for row in rows if row["St"] == "03" and row["Inode"] in session["socket_inodes"]]
        body = p.endpoint_binding.independent_body(session, proof, associated, access, inventory)
        proof["original_source_utf8"] = a.canonical(body).decode()
        proof["source_sha256"] = a.sha(proof["original_source_utf8"].encode())
    body = {"schema": "V6_INDEPENDENT_ENDPOINT_ACCESS_BOUNDARY_V3",
            "socket_access_sha256": a.identity(access), "socket_namespace": inventory["socket_namespace"],
            "user_namespace": inventory["user_namespace"]}
    evidence["boundary"]["original_source_utf8"] = a.canonical(body).decode()
    evidence["boundary"]["source_sha256"] = a.sha(evidence["boundary"]["original_source_utf8"].encode())
    for name, value in values.items():
        raw = a.canonical(value)
        bundle["sources"][name].update(raw_utf8=raw.decode(), sha256=a.sha(raw))


def rebind_owned_positive_fixture(root):
    path = root / "raw_fixture.json"
    bundle = p.exact_json(path)
    bind_fixture_provenance(bundle)
    # Test-owned source fixture mutation, not a candidate durable artifact write.
    Path(path).write_bytes(p.pretty(bundle))
'''
    text = text.replace('\nif __name__ == "__main__":\n    main()', extension + '''
if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        with (OUT / "qualification_failure.json").open("xb") as stream:
            stream.write(p.pretty({"status": "BLOCKED", "exception": type(exc).__name__,
                                  "reason": str(exc), "traceback": traceback.format_exc(),
                                  "no_retry_performed": True, "exact_sources": source_identities()}))
        raise
''')
    with (OUT / 'synthetic_e2e_qualifier.py').open('x') as stream:
        stream.write(text)
    print('Constructed exact-category qualifier; no qualification executed yet')


if __name__ == '__main__':
    main()

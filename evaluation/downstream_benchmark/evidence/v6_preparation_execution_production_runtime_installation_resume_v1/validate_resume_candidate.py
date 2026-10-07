"""Read-only package/preservation validator. --verify-seal never reruns fixtures."""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
from collections import Counter
from pathlib import Path

from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a
from evaluation.downstream_benchmark.screening import v6_preparation_ledger as ledger
from evaluation.downstream_benchmark.screening import v6_preparation_runtime as legacy

from . import production_controller_candidate as c
from . import production_provider_candidate as p

OUT = a.ROOT / p.RESUME
READY = "V6_PREPARATION_EXECUTION_PRODUCTION_RUNTIME_INSTALLATION_CANDIDATE_READY_FOR_HUMAN_PI_REVIEW"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=a.ROOT)


def load(name):
    return a.loads((OUT / name).read_bytes())


def tracked():
    files = {x.decode(): {"sha256": a.sha((a.ROOT / x.decode()).read_bytes()),
                         "mode": (a.ROOT / x.decode()).stat().st_mode & 0o777}
             for x in git("ls-files", "-z").split(b"\0") if x}
    return len(files), a.identity(files)


def real_tree():
    tree = {}
    for n in ("namespace.json", "ledger", "attempts", "inputs", "snapshots"):
        path = a.OUTPUT_ROOT / n
        ledger.safe_path(path)
        for f in ([path, *sorted(path.rglob("*"))] if path.is_dir() else [path]):
            ledger.safe_path(f)
            tree[str(f.relative_to(a.OUTPUT_ROOT))] = {"type": "ABSENT"} if not f.exists() else {
                "type": "directory", "mode": f.stat().st_mode & 0o777} if f.is_dir() else {
                "type": "file", "mode": f.stat().st_mode & 0o777, "size": f.stat().st_size,
                "sha256": a.sha(f.read_bytes())}
    return tree


def validate(*, verify_seal=False):
    pre = load("predecessor_evidence_binding.json")
    a.require(git("branch", "--show-current").strip() == b"main", "branch drift")
    for ref in ("HEAD", "origin/main"):
        a.require(git("rev-parse", ref).strip().decode() == pre["head"], "entry Git ref drift")
    a.require(git("diff", "--name-only") == git("diff", "--cached", "--name-only") == b"", "tracked/index changed")
    a.require(tracked() == (pre["tracked_count"], pre["tracked_fingerprint_sha256"]), "tracked bytes/modes changed")
    for path, identity in pre["predecessor_files"].items():
        raw = (a.ROOT / path).read_bytes()
        a.require(len(raw) == identity["size_bytes"] and a.sha(raw) == identity["sha256"], "predecessor changed: " + path)
    new_files = {str(x.relative_to(a.ROOT)) for x in OUT.rglob("*") if x.is_file()}
    actual = {x.decode() for x in git("ls-files", "--others", "--exclude-standard", "-z").split(b"\0") if x}
    a.require(actual == set(pre["predecessor_files"]) | new_files, "other untracked path or predecessor population drift")
    current = a.loads(a.read_exact(a.CURRENT, p.CANONICAL_SHA))
    projection = current["projection"]
    a.require(current["event_count"] == len(current["event_chain"]) == 3
              and current["event_head"]["event_id"] == p.EVENT_3
              and current["lifecycle_label"] == projection["state"] == "PREPARATION_EXECUTION_AUTHORIZED"
              and projection["lifecycle"]["PREPARATION_AUTHORIZED"] == "YES"
              and projection["phase_authorizations"]["PREPARATION_EXECUTION"] == "YES", "canonical authority")
    a.require(all(projection["phase_authorizations"][x] == "NO" for x in
                  ("SOURCE_ACQUISITION", "ORACLE_EXECUTION", "PILOT_FINAL_ALLOCATION", "DOWNSTREAM_REPAIR_EXECUTION")), "phase firewall")
    p.frozen_inputs()
    a.require(p.native.ONCE_ONLY["real_dispatch"] == "REJECT", "frozen guard drift")
    a.require(real_tree() == pre["real_tree"] and a.identity(real_tree()) == pre["real_tree_sha256"], "real ledger/output tree mutation")
    pop = legacy.population()
    _, manifest = a.load_inputs()
    a.validate_population(manifest, pop)
    identities = p.population_identity(pop, a.read_exact(legacy.PACKAGE + "work_items_candidate.json", legacy.WORK_SHA))
    p.validate_real_population(identities)
    a.require(Counter(x["variant"] for x in pop["items"]) == {"SOURCE_INDEPENDENT": 221, "BUGGY": 210, "FIXED": 210}, "variant counts")
    a.require({x["case_id"] for x in pop["blocked"]} == {"matplotlib::1", "matplotlib::8"}, "blockers")
    journal = ledger.Ledger(a.OUTPUT_ROOT, namespace=ledger.REAL, real_ids=[x["base_attempt_id"] for x in pop["items"]])
    a.require(all(journal.state(x["base_attempt_id"]) == "UNSTARTED" for x in pop["items"]), "real attempt state changed")
    for name in ("claims", "terminals", "locks"):
        a.require(not list((a.OUTPUT_ROOT / "ledger" / name).iterdir()), "real orphan/claim/terminal")
    for path in (p.CONTROLLER_TARGET, p.PROVIDER_TARGET, p.EFFECTIVITY, p.ACCEPTANCE_PIN, p.INSTALLATION_AUTHORITY, p.CONTRACT_TARGET):
        a.require(not (a.ROOT / path).exists(), "production installation/effectivity path exists")
    decision = load("human_pi_receipt_authority_decision.json")
    a.require(len(decision["rules"]) == 22 and {int(x.split("_")[0][1:]) for x in decision["rules"]} == set(range(1, 23)), "R1-R22 missing")
    contract = load("production_receipt_authority_contract.json")
    a.require((OUT / "production_receipt_authority_contract.json").read_bytes() == (OUT / "receipt_contract.json").read_bytes(), "contract aliases disagree")
    a.require(contract["human_pi_decision"] == decision and contract["allowed_origins"] == p.ORIGINS
              and set(contract["required_receipt_fields"]) == p.RECEIPT_FIELDS, "receipt decided semantics")
    for source in OUT.glob("*.py"):
        ast.parse(source.read_bytes())
    for artifact in OUT.glob("*.json"):
        a.loads(artifact.read_bytes())
    a.require(issubclass(c.ProductionAdmission, legacy.Admission), "Admission seam")
    a.require(p.ReceiptBoundLedger.terminal is ledger.Ledger.terminal
              and p.ReceiptBoundLedger.state is ledger.Ledger.state, "once-only terminal/state implementation changed")
    source = (OUT / "production_provider_candidate.py").read_text()
    a.require(all(token not in source for token in ("native.dispatch(", "native.NativeDockerTransport(", "native.shared_engine(")), "qualification guard bypass")
    qualification = load("synthetic_qualification_results.json")
    a.require(qualification["status"] == "PASS" and qualification["namespace"] == p.SYNTHETIC
              and all(v["status"] == "PASS" for v in qualification["tests"].values()), "synthetic qualification did not pass")
    matrix = load("rejection_matrix.json")
    a.require(matrix["status"] == "PASS" and all(v["status"] == "PASS_REJECTED" for v in matrix["checks"].values()), "rejection matrix failure")
    a.require(set(matrix["checks"]) == set(qualification["rejections"]), "matrix/qualification disagreement")
    a.require(all(v["status"] == "PASS" for v in qualification["required_A_through_X"].values()), "A-X coverage gap")
    external = load("external_artifact_sha256.json")
    external_actual = {str(x.relative_to(p.QUALIFICATION_ROOT)) for x in p.QUALIFICATION_ROOT.rglob("*") if x.is_file()}
    a.require(external_actual == set(external["files"]), "external qualification inventory population drift")
    for relative, identity in external["files"].items():
        path = p.QUALIFICATION_ROOT / relative
        ledger.safe_path(path)
        raw = path.read_bytes()
        a.require(len(raw) == identity["size_bytes"] and a.sha(raw) == identity["sha256"], "external evidence changed")
    fixture_ref = qualification["primary_effectivity_fixture"]
    raw_fixture = Path(fixture_ref["path"]).read_bytes()
    a.require(a.sha(raw_fixture) == fixture_ref["sha256"], "synthetic fixture source binding")
    fixture = a.loads(raw_fixture)
    for key, filename in (("controller", "production_controller_candidate.py"), ("provider", "production_provider_candidate.py")):
        a.require(fixture[key]["sha256"] == a.sha((OUT / filename).read_bytes()), "qualification did not test final candidate bytes")
    candidate = load("production_runtime_installation_candidate.json")
    a.require(candidate["status"] == READY and candidate["candidate_only"] is True
              and candidate["HUMAN_PI_ACCEPTED"] == candidate["runtime_effective"] == "NO", "candidate promoted")
    for relative, identity in candidate["package_bindings"].items():
        a.require(a.sha((OUT / relative).read_bytes()) == identity, "candidate bound artifact changed: " + relative)
    a.require(candidate["population_identity"] == identities and candidate["ledger_binding_identity"] == p.ledger_identity(), "population/ledger installation binding")
    plan = load("installation_plan.json")
    a.require(plan["installation_candidate_sha256"] == a.sha((OUT / "production_runtime_installation_candidate.json").read_bytes())
              and plan["execute_now"] is False and plan["future_targets"] == candidate["future_targets"], "installation plan binding/effectivity")
    graph = candidate["hash_graph"]
    visiting, visited = set(), set()
    def visit(node):
        a.require(node not in visiting, "hash cycle")
        if node in visited:
            return
        visiting.add(node)
        for dep in graph.get(node, []):
            visit(dep)
        visiting.remove(node)
        visited.add(node)
    for node in graph:
        visit(node)
    for name in ("production_controller_candidate.py", "production_provider_candidate.py"):
        raw = (OUT / name).read_bytes()
        a.require(a.sha(raw).encode() not in raw, "self hash embedded")
    if verify_seal:
        seal = load("artifact_sha256.json")
        expected = {str(x.relative_to(OUT)) for x in OUT.rglob("*") if x.is_file() and x.name != "artifact_sha256.json"}
        a.require(set(seal["files"]) == expected, "new artifact seal population")
        for relative, identity in seal["files"].items():
            raw = (OUT / relative).read_bytes()
            a.require(len(raw) == identity["size_bytes"] and a.sha(raw) == identity["sha256"], "sealed artifact changed")
    return {"schema": "V6_PRODUCTION_RUNTIME_RESUME_VALIDATION_RESULTS_V1", "status": "PASS", "candidate_status": READY,
        "checks": {"predecessor_23_exact": "PASS", "tracked_1015_exact": "PASS", "canonical_event_3_exact": "PASS",
                   "real_ledger_641_UNSTARTED_zero_claims_terminals_retries_orphans": "PASS", "frozen_runtime_config_exact": "PASS",
                   "population_641_221_420_583_58_exact": "PASS", "Admission_seam": "PASS", "versioned_receipt_claim_binding": "PASS",
                   "synthetic_E2E_A_X": "PASS", "all_rejections": "PASS", "final_sources_qualified": "PASS",
                   "external_evidence_exact": "PASS", "acyclic_hash_graph": "PASS", "production_targets_absent": "PASS"},
        "rejections_passed": len(matrix["checks"]), "artifact_seal_checked": verify_seal,
        "installation_candidate_sha256": a.sha((OUT / "production_runtime_installation_candidate.json").read_bytes()),
        "preservation": {"tracked_count": pre["tracked_count"], "tracked_sha256": pre["tracked_fingerprint_sha256"],
                         "canonical_sha256": p.CANONICAL_SHA, "real_tree_sha256": pre["real_tree_sha256"]},
        "limitations": ["Synthetic provider uses explicit local deterministic observations; no actual native Docker solve executed",
                        "Current production daemon/network/OCI/source-presence operational state not qualified",
                        "No real environment readiness or scientific validation established"],
        "next_gate": "HUMAN_PI_REVIEW_OF_V6_PREPARATION_EXECUTION_PRODUCTION_RUNTIME_INSTALLATION_CANDIDATE"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-seal", action="store_true")
    args = parser.parse_args()
    print(json.dumps(validate(verify_seal=args.verify_seal), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

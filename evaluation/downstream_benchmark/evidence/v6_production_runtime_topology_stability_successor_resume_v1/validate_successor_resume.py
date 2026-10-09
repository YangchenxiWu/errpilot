"""Independent read-only replay, exact preservation and acyclic artifact seal."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import stat
import subprocess
from collections import Counter
from pathlib import Path

from . import production_controller_successor_candidate as c
from . import production_provider_successor_candidate as p

HERE = Path(__file__).resolve().parent
ROOT = p.a.ROOT
STATUS = "V6_PRODUCTION_RUNTIME_TOPOLOGY_STABILITY_SUCCESSOR_CANDIDATE_READY_FOR_HUMAN_PI_REVIEW"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(path):
    return {"sha256": sha(path.read_bytes()), "size_bytes": path.stat().st_size}


def read(name):
    return p.a.loads((HERE / name).read_bytes())


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def function_inventory(path):
    tree = ast.parse(path.read_text())
    inventory = {}
    for node in tree.body:
        children = [(node.name, node)] if isinstance(node, ast.FunctionDef) else (
            [(node.name + "." + child.name, child) for child in node.body if isinstance(child, ast.FunctionDef)]
            if isinstance(node, ast.ClassDef) else [])
        for key, child in children:
            inventory[key] = {"ast_sha256": sha(ast.dump(child, include_attributes=False).encode()),
                              "line": child.lineno, "end_line": child.end_lineno}
    return inventory


def source_delta():
    old = ROOT / "evaluation/downstream_benchmark/evidence/v6_preparation_execution_production_runtime_installation_resume_v1"
    corrected = ROOT / "evaluation/downstream_benchmark/evidence/v6_production_runtime_image_identity_compatibility_bridge_v1/corrected_production_provider_candidate.py"
    baseline = {"historical_controller": old / "production_controller_candidate.py",
        "historical_provider": old / "production_provider_candidate.py", "corrected_provider": corrected,
        "successor_controller": Path(c.__file__), "successor_provider": Path(p.__file__)}
    inventories = {name: function_inventory(path) for name, path in baseline.items()}
    permitted = {
        "provider": {"validate_effectivity_status", "ledger_identity", "Authority.__init__", "Authority.synthetic", "Authority.refresh", "Authority.select", "Authority.observe",
            "receipt_value", "verify_receipt", "ReceiptBoundLedger.__init__", "ReceiptBoundLedger.claim", "verify_claim", "NativeProductionTransport.__init__",
            "shared_scientific_engine", "ProductionProvider.execute_synthetic"},
        "controller": {"ProductionAdmission.revalidate", "ProductionController.__init__", "ProductionController.synthetic", "ProductionController.prepare", "ProductionController.run_synthetic"},
    }
    changes = {}
    for role, predecessor in (("provider", "corrected_provider"), ("controller", "historical_controller")):
        before, after = inventories[predecessor], inventories["successor_" + role]
        changed = {k for k in before if before[k]["ast_sha256"] != after.get(k, {}).get("ast_sha256")}
        p.a.require(changed == permitted[role], "undeclared/missing authorized source body delta: " + role)
        changes[role] = {"changed": sorted(changed), "new": sorted(set(after) - set(before)),
            "preserved": sorted(k for k in before if k not in changed),
            "reasons": {k: ("New V2 topology/client/receipt/association or bounded qualification/source guard interface; scientific inputs, once-only lock/terminal and real native solve preserved") for k in sorted(changed)}}
    immutable = ("compile_production_transport", "frozen_inputs", "image_identity_pins", "verify_image_identity", "retained_image_content", "observe_image_config",
        "normalize_topology", "parse_workers", "NativeProductionTransport.build", "NativeProductionTransport.invoke", "NativeProductionTransport.check",
        "verify_layout", "validate_command", "ProductionProvider.execute", "ProductionProvider.persist_command", "ProductionProvider.__init__", "ReceiptBoundLedger._path")
    for name in immutable:
        p.a.require(inventories["corrected_provider"][name]["ast_sha256"] == inventories["successor_provider"][name]["ast_sha256"], "scientific/native/frozen function changed: " + name)
    for path in (Path(c.__file__), Path(p.__file__), HERE / "synthetic_e2e_qualifier.py"):
        text = path.read_text()
        p.a.require("object.__new__" not in text and "sys.modules[" not in text and "__file__ =" not in text, "forbidden synthetic bypass")
    return {"schema": "V6_SUCCESSOR_EXACT_SOURCE_DELTA_V2", "status": "PASS",
        "sources": {name: {"path": str(path.relative_to(ROOT)), **identity(path)} for name, path in baseline.items()},
        "function_AST_inventories": inventories, "authorized_deltas": changes,
        "unchanged_scientific_native_functions": list(immutable),
        "shared_scientific_code": "Original _materialize_checked/build_definition/context/probe/identity code objects, cloned only to bind transport; original module globals unchanged",
        "qualification_design": "Own normal constructors, exact candidate path/root, no object.__new__/forged file/sys.modules injection; actual shared scientific engine via deterministic simulated I/O",
        "production_authentication": "Fixed SHA-pinned separately Human-PI reviewed C6 observer + accepted principal set; no installed observer currently exists, so real entry stays blocked",
        "non_function_deltas": ["exact candidate imports/source paths", "distinct V2 future target/effectivity/contract names", "distinct synthetic namespace/root", "new receipt fields", "new protected evidence/transport interfaces"],
        "scientific_validation_claimed": False}


def replay_scientific():
    from evaluation.downstream_benchmark.evidence.v6_preparation_execution_production_runtime_installation_resume_v1 import production_provider_candidate as old
    from evaluation.downstream_benchmark.evidence.v6_production_runtime_image_identity_compatibility_bridge_v1 import corrected_production_provider_candidate as corrected
    p.frozen_inputs()
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
        p.a.require(compiled == prior == correction, "scientific/native transport projection drift")
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


def preservation():
    entry = read("entry_snapshot.json")
    p.a.require(git("rev-parse", "HEAD").decode().strip() == entry["head"] and git("branch", "--show-current").decode().strip() == "main", "HEAD/branch drift")
    p.a.require(sha((ROOT / ".git/index").read_bytes()) == entry["index_sha256"], "index bytes drift")
    tracked = git("ls-files", "-z").decode().split("\0")[:-1]
    p.a.require(set(tracked) == set(entry["tracked"]) and len(tracked) == 1065
                and all(identity(ROOT / path) == value for path, value in entry["tracked"].items()), "tracked set/bytes drift")
    p.a.require(git("diff", "--name-only") == b"" and git("diff", "--cached", "--name-only") == b"", "tracked/index diff")
    for package in entry["predecessors"].values():
        root = Path(package["path"])
        files = {str(f.relative_to(root)): identity(f) for f in root.rglob("*") if f.is_file()}
        p.a.require(files == package["files"] and not any(f.is_symlink() for f in root.rglob("*")), "predecessor set/byte drift")
    untracked = set(git("ls-files", "--others", "--exclude-standard", "-z").decode().split("\0")[:-1])
    prefix = str(HERE.relative_to(ROOT)) + "/"
    p.a.require({x for x in untracked if not x.startswith(prefix)} == set(entry["untracked_paths"]), "unexpected untracked path")
    p.a.require(identity(ROOT / p.a.CURRENT) == entry["canonical"], "canonical byte drift")
    current = p.a.loads((ROOT / p.a.CURRENT).read_bytes())
    p.a.require(current["projection"]["state"] == "PREPARATION_EXECUTION_AUTHORIZED" and current["event_count"] == 3
                and current["event_head"]["event_id"] == p.EVENT_3, "canonical/event3 drift")
    for ref in entry["controlling_sources"].values():
        p.a.require(sha((ROOT / ref["path"]).read_bytes()) == ref["sha256"], "controlling source drift")
    p.frozen_inputs()
    root = p.a.OUTPUT_ROOT
    p.a.require(set(f.name for f in root.iterdir()) == {"namespace.json", "ledger", "qualification"}, "real output namespace changed")
    tree = {}
    for f in [root / "namespace.json", root / "ledger", *sorted((root / "ledger").rglob("*"))]:
        tree[str(f.relative_to(root))] = {"mode": stat.S_IMODE(f.stat().st_mode), "type": "file" if f.is_file() else "directory",
                                        **(identity(f) if f.is_file() else {})}
    p.a.require(tree == entry["real_output_tree"], "real output/ledger tree mode/byte drift")
    population = p.legacy.population()
    journal = p.ledger.Ledger(root, namespace=p.REAL, real_ids=[x["base_attempt_id"] for x in population["items"]])
    states = dict(Counter(journal.state(x["base_attempt_id"]) for x in population["items"]))
    p.a.require(states == {"UNSTARTED": 641}, "real ledger consumption/orphan")
    targets = [*entry["production_targets"].values(), p.CONTROLLER_TARGET, p.PROVIDER_TARGET, p.EFFECTIVITY, p.ACCEPTANCE_PIN,
               p.INSTALLATION_AUTHORITY, p.CONTRACT_TARGET, p.LIVE_OBSERVER_TARGET]
    p.a.require(all(not (ROOT / target).exists() for target in targets), "production target appeared")
    live = read("live_origin_exit.json")
    p.a.require(live["returncode"] == 0 and live["stdout"].split() == [entry["head"], "refs/heads/main"], "live origin unavailable/drift")
    return {"schema": "V6_SUCCESSOR_RESUME_PRESERVATION_V1", "status": "PASS", "tracked_files_exact": 1065,
        "predecessor_files_exact": 572, "partial_files_exact": 71, "index_exact": True, "HEAD_live_origin_exact": entry["head"],
        "canonical_sha256": p.CANONICAL_SHA, "event_3_id": p.EVENT_3, "real_ledger_states": states,
        "claims": 0, "terminals": 0, "retries": 0, "orphans": 0, "real_output_bytes_modes_paths_exact": True,
        "production_targets_absent": targets, "only_new_repo_namespace": prefix,
        "Docker_commands_executed": 0, "Docker_mutations_by_agent": 0, "live_Docker_state_independently_observed": False,
        "Docker_preservation_evidence": "No Docker process/socket/attach/exec/build/network/image/volume operation executed; no current live topology certification"}


def acyclic(graph):
    nodes = {n["id"] for n in graph["nodes"]}
    p.a.require(len(nodes) == len(graph["nodes"]), "duplicate DAG node")
    incoming = {n: 0 for n in nodes}
    outgoing = {n: [] for n in nodes}
    for edge in graph["edges"]:
        a, b = edge
        p.a.require(a in nodes and b in nodes and a != b, "invalid DAG edge")
        incoming[b] += 1
        outgoing[a].append(b)
    ready = [n for n, count in incoming.items() if count == 0]
    ordered = []
    while ready:
        node = ready.pop()
        ordered.append(node)
        for child in outgoing[node]:
            incoming[child] -= 1
            if incoming[child] == 0:
                ready.append(child)
    p.a.require(len(ordered) == len(nodes), "cyclic dependency graph")
    for node in graph["nodes"]:
        for ref in node.get("artifacts", []):
            p.a.require(identity(Path(ref["path"])) == {k: ref[k] for k in ("sha256", "size_bytes")}, "DAG file hash drift")
    return ordered


def verify_external_qualification(results):
    root = p.QUALIFICATION_ROOT
    for relative, value in results["external_inventory"].items():
        p.a.require(identity(root / relative) == value, "qualification source/fixture/ledger/evidence byte drift")
    run = Path(results["qualification_run_root"])
    for module, name in ((c, "production_controller_successor_candidate.py"), (p, "production_provider_successor_candidate.py")):
        p.a.require((run / "input-source" / name).read_bytes() == Path(module.__file__).read_bytes(), "tested source pair differs from final source")
    p.a.require((run / "input-source/synthetic_e2e_qualifier.py").read_bytes() == (HERE / "synthetic_e2e_qualifier.py").read_bytes(), "tested qualifier source differs")
    p.a.require(results["status"] == "PASS" and results["full_source_pair_E2E"] is True
                and all(v["status"] == "PASS" for v in results["required_A_through_X"].values())
                and len(results["required_A_through_X"]) == 24 and len(results["required_inherited_A_X"]) == 24,
                "complete source-pair E2E required")


def verify_seal():
    manifest = read("artifact_sha256.json")
    files = {str(f.relative_to(HERE)): identity(f) for f in HERE.rglob("*") if f.is_file() and f.name != "artifact_sha256.json"}
    # Only the root manifest is excluded; any nested seals are payloads.
    files = {str(f.relative_to(HERE)): identity(f) for f in HERE.rglob("*") if f.is_file() and f != HERE / "artifact_sha256.json"}
    p.a.require(files == manifest["files"] and len(files) == manifest["payload_count"], "artifact set/size/SHA seal mismatch")
    p.a.require(not any(f.is_symlink() for f in HERE.rglob("*")), "artifact symlink")
    return {"manifest_self_sha256": sha((HERE / "artifact_sha256.json").read_bytes()), "payload_count": len(files), "total_file_count": len(files) + 1}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-seal", action="store_true")
    args = parser.parse_args(argv)
    preservation()
    source_delta()
    results = read("synthetic_e2e_results.json")
    verify_external_qualification(results)
    matrix = read("rejection_matrix.json")
    inherited = p.exact_json(ROOT / "evaluation/downstream_benchmark/evidence/v6_preparation_execution_production_runtime_installation_resume_v1/rejection_matrix.json")
    p.a.require(set(inherited["checks"]) <= set(matrix["checks"]) and matrix["inherited_count"] == 77
                and matrix["mandatory_skipped"] == 0 and all(x["status"] == "PASS_REJECTED" and x["ledger_before"] == x["ledger_after"] for x in matrix["checks"].values()), "rejection coverage incomplete")
    replay = replay_scientific()
    p.a.require(replay == read("scientific_projection_revalidation.json"), "641 successor replay drift")
    acyclic(read("supersession_dependency_graph.json"))
    plan, candidate = read("successor_installation_plan.json"), read("successor_installation_candidate.json")
    p.a.require(candidate["candidate_only"] is True and candidate["HUMAN_PI_ACCEPTED"] == "NO" and candidate["runtime_effective"] == "NO"
                and plan["execute_now"] is False and plan["current_production_installation_authorized"] is False
                and plan["current_real_attempt_authorized"] is False, "production authority/installation claim")
    for name in [*p.SECURITY_CONTRACT_NAMES, "receipt_authority_contract_v2_candidate.json"]:
        raw = (HERE / name).read_bytes()
        value = p.a.loads(raw)
        p.a.require(raw == p.pretty(value), "versioned contract/schema deterministic serialization")
        p.a.require(p.a.loads(p.a.canonical(value)) == value, "contract/schema canonical roundtrip")
    from jsonschema import Draft202012Validator
    Draft202012Validator.check_schema(read("receipt_schema_v2_candidate.json"))
    ruff = read("ruff_results.json")
    p.a.require(ruff["returncode"] == 0, "Ruff failed/not run")
    validations = read("validation_results.json")
    p.a.require(validations["status"] == STATUS and validations["mandatory_skipped"] == 0, "validation result incomplete")
    result = {"status": STATUS, "inherited_rejections": 77, "total_rejections": len(matrix["checks"]), "scientific_replays": 641,
              "real_client_authorization": "BLOCKED", "production_runtime_installed": "NO", "real_production_entry_effective": "NO"}
    if args.verify_seal:
        result.update(verify_seal())
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

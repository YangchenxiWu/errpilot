"""Read-only semantic checks and in-memory candidate rejection probes.

Only validation_results.json is written. No subject tests or runtime actions.
"""
from __future__ import annotations

import base64
import collections
import copy
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
E = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("candidate_planning", E / "construct_candidate.py")
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
B = g.B
ROOT = g.ROOT
PLAN_KEYS = {
    "schema", "candidate_only", "baseline", "current_descriptor_sha256", "pool_sha256",
    "case_id", "census_order", "frozen_rank", "source_project", "bugsinpy_bug_id",
    "source_repository", "source_variants", "input_bindings", "input_paths", "recipe_candidate",
    "oracle", "applicable_case_specific_bridges", "downstream_authority", "blockers",
    "planning_disposition", "plan_sha256",
}
FORBIDDEN_KEYS = {
    "environment_ready", "environment_ready_cases", "eligible", "scientific_failure",
    "screening_classification", "attempt_id", "attempt_consumed", "build_result",
    "oracle_result", "environment_identity", "installed_distributions", "final_image_id",
    "retry", "rescue", "latest", "mtime", "directory_scan_selector", "outcomes",
}
RECIPE_KEYS = {
    "schema", "python_declared_version", "base_runtime", "runtime_platform", "requirements",
    "setup_sha256", "setup_lines", "setup_actions", "setup_action_ledger_sha256",
    "environment_mode_v2", "pythonpath_metadata", "source_install_policy",
    "system_package_requirements", "future_network_build_policy", "future_network_execution_policy",
    "protected_manifest", "source_preparation",
}
PROTECTED_CACHE = {}
TREE_CACHE = {}
REPO_CACHE = set()


def strict_load(path):
    def unique(pairs):
        obj = {}
        for key, value in pairs:
            g.require(key not in obj, "duplicate JSON key")
            obj[key] = value
        return obj
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def no_execution_fields(item):
    if isinstance(item, dict):
        g.require(not FORBIDDEN_KEYS & set(item), "outcome/selection/execution claim")
        for value in item.values():
            no_execution_fields(value)
    elif isinstance(item, list):
        for value in item:
            no_execution_fields(value)


def validate(manifest, *, external=True):
    g.require(manifest["schema"] == "V6_PREPARATION_PLAN_MANIFEST_CANDIDATE_V1", "manifest schema")
    g.require(manifest["candidate_only"] is True and manifest["runtime_authority"] is False
              and manifest["lifecycle"] == "CANDIDATE_ONLY", "candidate lifecycle")
    g.require(manifest["baseline"] == g.BASELINE, "wrong baseline")
    g.require(manifest["current_descriptor"] == g.file_ref(B / "v6_current_state.json")
              and manifest["current_descriptor"]["sha256"] == g.CURRENT_SHA, "wrong descriptor")
    g.require(manifest["canonical_pool"] == g.file_ref(B / "v6_reconsideration_pool.csv")
              and manifest["canonical_pool"]["sha256"] == g.POOL_SHA, "wrong pool")
    g.require(manifest["selection"] == {
        "method": "EXPLICIT_MANIFEST_SHA256_AND_CASE_ORDINAL", "dispatch_order": "ORIGINAL_FROZEN_RANK_ASCENDING",
        "governed_batches": False, "runtime_chunk_scientific_identity": "NONE",
        "runtime_chunk_admission_authority": "NONE", "fallback": "NONE", "stop_at_capacity": False,
        "automatic_retry": False, "automatic_rescue": False}, "fallback/batch/retry/capacity policy")
    g.require(manifest["downstream_authority"] == g.NEGATIVE, "downstream authority")
    pool = g.rows(B / "v6_reconsideration_pool.csv")
    plans = manifest["plans"]
    g.require(len(plans) == len({p["case_id"] for p in plans}) == 433, "missing/duplicate census case")
    g.require([(p["case_id"], p["source_project"], p["bugsinpy_bug_id"], p["frozen_rank"], p["census_order"]) for p in plans]
              == [(p["case_id"], p["source_project"], p["bugsinpy_bug_id"], int(p["frozen_rank"]), int(p["census_order"])) for p in pool], "wrong case/order/project")
    g.require(len({p["plan_sha256"] for p in plans}) == 433, "ambiguous plan identity")
    g.require(manifest["planning_vocabulary"] == {
        "authority": "PROPOSAL_LEVEL_ONLY_NO_CANONICAL_EFFECT", "statuses": g.VOCABULARY,
        "primary_priority": g.PRIORITY, "blocker_incidence_is_overlapping": True}, "planning vocabulary")
    no_execution_fields(plans)
    g.require(manifest["bugsinpy"] == {"path": str(g.META), "commit": g.ex.BUGSINPY_COMMIT, "tree": g.ex.BUGSINPY_TREE}, "metadata baseline")
    counts = collections.Counter()
    incidence = collections.Counter()
    revision_bindings = 0
    all_full = 0
    constructed = 0
    for p in plans:
        g.require(set(p) == PLAN_KEYS, "unknown/missing plan field")
        g.require(p["schema"] == "V6_PREPARATION_CASE_PLAN_CANDIDATE_V1" and p["candidate_only"] is True, "plan lifecycle")
        g.require(p["baseline"] == g.BASELINE and p["pool_sha256"] == g.POOL_SHA
                  and p["current_descriptor_sha256"] == g.CURRENT_SHA, "plan controlling identity")
        g.require(p["downstream_authority"] == g.NEGATIVE and not p["applicable_case_specific_bridges"], "authority/bridge generalization")
        body = {k: v for k, v in p.items() if k != "plan_sha256"}
        g.require(g.identity(body) == p["plan_sha256"], "plan hash mismatch")
        g.require(p["planning_disposition"] == g.disposition(p["blockers"]), "wrong primary disposition")
        counts[p["planning_disposition"]] += 1
        incidence.update({b["category"] for b in p["blockers"]})
        variants = p["source_variants"]
        g.require(len(variants) == 2 and [v["label"] for v in variants] == ["BUGGY", "FIXED"], "variant identity")
        revision_bindings += len(variants)
        paths = p["input_paths"]
        prefix = f"projects/{p['source_project']}/bugs/{p['bugsinpy_bug_id']}"
        expected_paths = [f"projects/{p['source_project']}/project.info", *[f"{prefix}/{n}" for n in ("bug.info", "run_test.sh", "setup.sh", "requirements.txt")]]
        g.require(paths == expected_paths, "input path mutation")
        g.require(p["input_bindings"] == [manifest["metadata_inputs"][x]["sha256"] for x in paths], "input identity mismatch")
        input_raw = []
        for path in paths:
            record = manifest["metadata_inputs"][path]
            raw = base64.b64decode(record["bytes_b64"], validate=True) if record["present"] else None
            g.require(record["sha256"] == (g.sha(raw) if raw is not None else "ABSENT"), "metadata embedded-byte identity")
            if external:
                local = g.META / path
                g.require((local.read_bytes() if local.is_file() else None) == raw, "metadata literal mutation")
            input_raw.append(raw)
        project_raw, bug_raw, script, setup, raw = input_raw
        bi = g.metadata.parse_literal_assignments(g.META / paths[1])
        pi = g.metadata.parse_literal_assignments(g.META / paths[0])
        universe = {r["canonical_case_id"]: r for r in g.rows(B / "candidate_universe.csv")}
        g.require(bi["test_file"] == universe[p["case_id"]]["declared_test_file"] and pi["status"] == "OK", "declared test/project status drift")
        repo = p["source_repository"]
        g.require(repo == manifest["projects"][p["source_project"]] and repo["expected_url"] == pi["github_url"], "wrong source repository")
        if external and p["source_project"] not in REPO_CACHE:
            mirror = Path(repo["mirror_path"])
            g.require(mirror == g.WORK / "subject_repositories" / (g.ex.safe_case_slug(p["source_project"]) + ".git"), "mirror selector mutation")
            g.require(repo["locally_present"] is True and repo["bare"] is True
                      and g.git(mirror, "rev-parse", "--is-bare-repository").strip() == b"true"
                      and g.git(mirror, "remote", "get-url", "origin").decode().strip() == repo["observed_origin"]
                      and g.ex._remote_urls_match(pi["github_url"], repo["observed_origin"]), "mirror identity drift")
            REPO_CACHE.add(p["source_project"])
        for variant, field in zip(variants, ["buggy_commit_id", "fixed_commit_id"]):
            g.require(variant["revision_metadata"] == bi[field], "wrong declared revision")
            if external:
                full = g.ex.resolve_revision(Path(repo["mirror_path"]), bi[field])
                g.require(full == variant["commit_oid"] and variant["object_locally_present"] == "YES", "wrong resolved revision/local presence")
            if variant["commit_oid"] is not None:
                all_full += 1
            export = variant["source_export_planning"]
            g.require(export["source_export_executed"] is False and export["snapshot_sha256"] is None, "source export claimed")
            if external:
                key = (p["source_project"], variant["commit_oid"])
                if key not in TREE_CACHE:
                    raw_tree = g.git(Path(repo["mirror_path"]), "ls-tree", "-r", "-z", variant["commit_oid"])
                    parsed = []
                    for record in raw_tree.split(b"\0"):
                        if record:
                            header, path = record.split(b"\t", 1)
                            mode, kind, oid = header.split()
                            parsed.append((path, mode, kind, oid))
                    TREE_CACHE[key] = (g.sha(raw_tree), parsed)
                tree_sha, parsed = TREE_CACHE[key]
                links = [{"path": path.decode(), "object_id": oid.decode(), "mode": "160000"}
                         for path, mode, kind, oid in parsed if mode == b"160000"]
                g.require(export["tree_metadata_sha256"] == tree_sha and export["tracked_entry_count"] == len(parsed)
                          and export["tracked_symlink_count"] == sum(mode == b"120000" for path, mode, kind, oid in parsed)
                          and export["tracked_gitlinks"] == links and export["tree_metadata_status"] == "RESOLVED",
                          "source tree representation mutation")
        recipe = p["recipe_candidate"]
        g.require(set(recipe) == RECIPE_KEYS and recipe["schema"] == "V6_PREPARATION_RECIPE_PROPOSAL_V1", "hidden recipe field/schema mutation")
        req = recipe["requirements"]
        g.require(req["raw_sha256"] == (g.sha(raw) if raw is not None else "ABSENT"), "raw requirements mutated")
        normalized = dependency = None
        ledger = []
        encoding = "ABSENT"
        failed = False
        if raw is not None:
            try:
                normalized, encoding = g.br.normalize_requirements(raw)
                dependency, ledger = g.br.derive_dependency_input(normalized, case_id=p["case_id"], project=p["source_project"], source_url=pi["github_url"])
            except (UnicodeError, g.br.RecipeError):
                failed = True
        g.require(any(b["category"] == "REQUIREMENTS_REPRESENTATION" for b in p["blockers"]) == failed, "requirements blocker missing")
        for name, data in [("normalized", normalized), ("dependency", dependency)]:
            expected = base64.b64encode(data).decode() if data is not None else None
            key = "normalized_bytes_b64" if name == "normalized" else "dependency_bytes_b64"
            hash_key = "normalized_sha256" if name == "normalized" else "dependency_input_sha256"
            g.require(req[key] == expected, "unsupported silent normalization")
            g.require(req[hash_key] == (g.sha(data) if data is not None else "ABSENT" if raw is None else "UNRESOLVED"), "derived dependency hash")
        g.require(req["encoding"] == encoding and req["self_reference_ledger"] == ledger
                  and req["self_reference_ledger_sha256"] == g.identity(ledger), "self-reference ledger drift")
        g.require(recipe["setup_sha256"] == (g.sha(setup) if setup is not None else "ABSENT"), "setup bytes mutation")
        lines = [{"line": n, "category": g.ae.classify_setup_line(line), "text": line}
                 for n, line in enumerate(setup.decode().splitlines(), 1) if line.strip() and not line.lstrip().startswith("#")] if setup is not None else []
        g.require(recipe["setup_lines"] == lines, "setup line/order mutation")
        actions = []
        setup_blocked = False
        try:
            actions = g.br.setup_actions(setup, json.dumps(lines))
            g.require(recipe["environment_mode_v2"] == g.br.environment_mode(actions), "mode mutation")
            for action in actions:
                try:
                    action["future_argv"] = g.mat.action_argv(action, source_present=action["consumes_subject_source"])
                except g.mat.Blocked:
                    setup_blocked = True
        except (UnicodeError, g.br.RecipeError):
            setup_blocked = True
        if setup is not None and g.ex._setup_invokes_tests(setup):
            setup_blocked = True
        g.require(recipe["setup_actions"] == actions, "hidden setup/recipe mutation")
        g.require(any(b["category"] == "SETUP_REPRESENTATION" for b in p["blockers"]) == setup_blocked, "setup blocker missing")
        g.require(recipe["setup_action_ledger_sha256"] == g.identity([{k: v for k, v in a.items() if k != "future_argv"} for a in actions]), "setup ledger hash")
        expected_oracle = g.ex.analyze_oracle(script)
        expected_oracle["argv"] = ([list(g.ex.parse_recognized_command(c)) for c in expected_oracle["commands"]]
                                   if expected_oracle["status"] == "RESOLVED_ORDERED_COMMANDS" else [])
        expected_oracle.update({"script_sha256": g.sha(script), "representation": "COMPOSITE_ORACLE_SEMANTICS_V1", "executed": False, "future_cwd": "subject repository root"})
        g.require(p["oracle"] == expected_oracle, "oracle literal mutation")
        g.require(any(b["category"] == "ORACLE_REPRESENTATION" for b in p["blockers"])
                  == (expected_oracle["status"] != "RESOLVED_ORDERED_COMMANDS"), "oracle blocker missing")
        g.require(recipe["python_declared_version"] == bi["python_version"] and recipe["runtime_platform"] == "linux/amd64", "runtime mutation")
        g.require(recipe["base_runtime"] == g.p3._image(B, bi["python_version"]), "base runtime mutation")
        g.require(recipe["future_network_execution_policy"] == "NONE"
                  and recipe["future_network_build_policy"] == "DECLARED_DEPENDENCY_SOURCES_ONLY_SEPARATE_AUTHORITY_REQUIRED"
                  and recipe["source_install_policy"] == "EXPLICIT_SETUP_ACTIONS_ONLY", "network/install policy mutation")
        if external and all(v["object_locally_present"] == "YES" for v in variants):
            cid = p["case_id"]
            if cid not in PROTECTED_CACHE:
                u = universe[cid]
                candidate = g.ex.Candidate(p["frozen_rank"], p["census_order"], cid, p["source_project"],
                                           p["bugsinpy_bug_id"], pi["github_url"], bi["python_version"],
                                           bi["buggy_commit_id"], bi["fixed_commit_id"], u["declared_test_file"],
                                           g.ex.BUGSINPY_COMMIT)
                PROTECTED_CACHE[cid] = g.ex.build_protected_manifest(candidate, Path(repo["mirror_path"]),
                    variants[0]["commit_oid"], variants[1]["commit_oid"], expected_oracle["commands"])
            g.require(recipe["protected_manifest"] == PROTECTED_CACHE[cid], "protected test input mutation")
        if p["planning_disposition"] == g.VOCABULARY[0]:
            g.require(not p["blockers"] and recipe["protected_manifest"]["status"] == "RESOLVED", "constructible with unresolved inputs")
            constructed += 1
    expected_counts = {g.COUNTER_KEYS[key]: counts[key] for key in g.VOCABULARY}
    expected_counts.update({"TOTAL_CENSUS_CASES": 433, "EXPECTED_VARIANT_BINDINGS": revision_bindings})
    g.require(manifest["counts"] == expected_counts and sum(counts.values()) == 433, "disposition reconciliation")
    g.require(manifest["blocker_incidence_case_counts"] == dict(sorted(incidence.items())), "blocker incidence reconciliation")
    g.require(revision_bindings == 866, "variant count")
    if external:
        for project, repo in manifest["projects"].items():
            oids = sorted({oid.decode() for (name, _), (_, parsed) in TREE_CACHE.items() if name == project
                           for path, mode, kind, oid in parsed if kind == b"blob"})
            raw_check = g.git(Path(repo["mirror_path"]), "cat-file", "--batch-check",
                              input=("\n".join(oids) + "\n").encode())
            missing = sorted(line.split()[0].decode() for line in raw_check.splitlines() if line.endswith(b" missing"))
            g.require(manifest["leaf_object_availability"][project]
                      == {"unique_required_leaf_blob_objects": len(oids), "missing": missing}, "leaf object availability mutation")
    return {"case_count": 433, "variant_count": revision_bindings, "full_commit_identity_bindings": all_full,
            "constructible": constructed, "counts": expected_counts}


def rehash(manifest):
    for p in manifest["plans"]:
        p["plan_sha256"] = g.identity({k: v for k, v in p.items() if k != "plan_sha256"})


def main():
    manifest = strict_load(g.MANIFEST)
    result = validate(manifest)
    table = g.rows(g.TABLE)
    g.require([(int(x["census_order"]), x["case_id"], x["plan_sha256"], x["planning_disposition"]) for x in table]
              == [(x["census_order"], x["case_id"], x["plan_sha256"], x["planning_disposition"]) for x in manifest["plans"]], "CSV plan resolution")
    for row, plan in zip(table, manifest["plans"]):
        buggy, fixed = plan["source_variants"]
        expected = {k: str(plan[k]) for k in ["census_order", "case_id", "source_project", "bugsinpy_bug_id", "frozen_rank", "plan_sha256", "planning_disposition"]}
        expected.update({"buggy_revision_metadata": buggy["revision_metadata"], "buggy_commit_oid": buggy["commit_oid"],
            "buggy_object_locally_present": buggy["object_locally_present"], "fixed_revision_metadata": fixed["revision_metadata"],
            "fixed_commit_oid": fixed["commit_oid"], "fixed_object_locally_present": fixed["object_locally_present"],
            "requires_source_acquisition": str(any(b["category"] == "SOURCE_ACQUISITION" for b in plan["blockers"])),
            "blocker_categories": "|".join(sorted({b["category"] for b in plan["blockers"]})),
            "blocker_mechanisms": "|".join(sorted({b["mechanism"] for b in plan["blockers"]})),
            "oracle_status": plan["oracle"]["status"], "python_version": plan["recipe_candidate"]["python_declared_version"],
            "environment_mode": plan["recipe_candidate"]["environment_mode_v2"]})
        g.require(row == expected, "derived CSV field disagreement")
    gate = strict_load(E / "entry_verification.json")
    g.require(all(g.sha((ROOT / path).read_bytes()) == value for path, value in gate["tracked_sha256"].items()), "tracked byte preservation")
    g.require(g.snapshot_external() == gate["external_metadata_sha256"], "external evidence preservation")
    g.require(not g.git(ROOT, "diff", "--cached", "--name-only") and not g.git(ROOT, "diff", "--name-only"), "index/tracked modification")
    # Mutations deliberately recompute plan hashes; semantic checks must still reject.
    probes = {
        "missing_case": lambda m: m["plans"].pop(),
        "duplicate_case": lambda m: m["plans"].__setitem__(1, copy.deepcopy(m["plans"][0])),
        "reordered_case": lambda m: m["plans"].reverse(),
        "wrong_revision": lambda m: m["plans"][0]["source_variants"][0].__setitem__("commit_oid", "0" * 40),
        "wrong_revision_metadata": lambda m: m["plans"][0]["source_variants"][0].__setitem__("revision_metadata", "0" * 40),
        "wrong_project": lambda m: m["plans"][0].__setitem__("source_project", "wrong-project"),
        "wrong_pool_hash": lambda m: m["canonical_pool"].__setitem__("sha256", "0" * 64),
        "wrong_baseline": lambda m: m.__setitem__("baseline", "0" * 40),
        "plan_ambiguity": lambda m: m["plans"][0].__setitem__("alternate_plan_sha256", "0" * 64),
        "fallback_latest_resolution": lambda m: m["selection"].__setitem__("fallback", "latest"),
        "mtime_resolution": lambda m: m["selection"].__setitem__("method", "MTIME"),
        "hidden_recipe_mutation": lambda m: m["plans"][0]["recipe_candidate"]["setup_actions"].append({"exact_source_text": "pip install rescue"}),
        "unsupported_silent_normalization": lambda m: m["plans"][0]["recipe_candidate"]["requirements"].__setitem__("dependency_bytes_b64", base64.b64encode(b"repaired==1\n").decode()),
        "execution_state_claims": lambda m: m["plans"][0].__setitem__("attempt_consumed", True),
        "environment_ready_claims": lambda m: m["plans"][0].__setitem__("environment_ready", True),
        "automatic_retry": lambda m: m["selection"].__setitem__("automatic_retry", True),
        "automatic_rescue": lambda m: m["selection"].__setitem__("automatic_rescue", True),
        "stop_at_capacity": lambda m: m["selection"].__setitem__("stop_at_capacity", True),
        "governed_batches": lambda m: m["selection"].__setitem__("governed_batches", True),
        "execution_authority": lambda m: m["downstream_authority"].__setitem__("PREPARATION_AUTHORIZED", "YES"),
        "oracle_command_substitution": lambda m: m["plans"][0]["oracle"]["commands"].__setitem__(0, "python -m pytest"),
        "case_specific_bridge_generalization": lambda m: m["plans"][0]["applicable_case_specific_bridges"].append("cookiecutter"),
        "hidden_recipe_field": lambda m: m["plans"][0]["recipe_candidate"].__setitem__("repair_allowed", True),
        "protected_manifest_mutation": lambda m: m["plans"][0]["recipe_candidate"]["protected_manifest"].__setitem__("manifest_sha256", "0" * 64),
        "source_presence_mutation": lambda m: m["plans"][0]["source_variants"][0].__setitem__("object_locally_present", "NO"),
        "source_tree_representation_mutation": lambda m: m["plans"][0]["source_variants"][0]["source_export_planning"].__setitem__("tracked_entry_count", 0),
    }
    rejection = {}
    for name, mutate in probes.items():
        fixture = copy.deepcopy(manifest)
        mutate(fixture)
        rehash(fixture)
        try:
            validate(fixture, external=True)
        except (ValueError, KeyError, TypeError) as exc:
            rejection[name] = {"result": "REJECTED", "reason": str(exc)}
        else:
            raise ValueError("mutation accepted: " + name)
    firewall = {key: "NO" for key in (
        "PREPARATION_EXECUTED", "SOURCE_ACQUISITION_EXECUTED", "MATERIALIZATION_EXECUTED",
        "IMAGE_BUILD_EXECUTED", "ORACLE_EXECUTED", "V6_MEMBERSHIP_CHANGED", "CENSUS_ORDER_CHANGED",
        "PILOT_SELECTED", "FINAL_SELECTED", "GIT_STAGE", "GIT_COMMIT", "GIT_PUSH")}
    firewall["ENVIRONMENT_READY_CASES_ESTABLISHED"] = 0
    saved = {"status": "PASS", "coverage": result, "manifest_sha256": g.sha(g.MANIFEST.read_bytes()),
             "positive_checks": {name: "PASS" for name in (
                 "exact_433_case_coverage", "no_duplicates", "frozen_rank_order", "866_buggy_fixed_bindings",
                 "deterministic_revision_identity", "no_predecessor_overlap_entry", "exact_metadata_bytes",
                 "requirements_represented_without_silent_repair", "exact_ordered_setup", "exact_oracle_representation",
                 "one_disposition_per_case", "counts_reconcile", "explicit_manifest_plan_resolution",
                 "no_outcome_fields", "no_governed_batches", "downstream_negative_authority",
                 "tracked_files_preserved", "242_external_metadata_files_preserved", "index_empty")},
             "rejection_matrix": rejection, "rejection_count": len(rejection), "failed_checks": 0,
             "firewall": firewall, "read_only_git_command_counts": dict(g.COMMAND_COUNTS),
             "tests_executed": "Candidate semantic validator and in-memory mutations only",
             "subject_tests_or_oracles_executed": 0}
    g.save(E / "validation_results.json", saved)
    print(json.dumps({"status": "PASS", "coverage": result, "rejections": len(rejection),
                      "manifest_sha256": saved["manifest_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()

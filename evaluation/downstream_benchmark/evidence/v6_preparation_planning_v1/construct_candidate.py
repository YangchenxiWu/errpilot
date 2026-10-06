"""Candidate-only census planning. Only local read-only Git and inert parsers run.

This is evidence tooling, not a V6 executor or an authority writer. It has no
source export, subject import, setup, install, Docker, retry or oracle path.
"""
from __future__ import annotations

import base64
import collections
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
B = ROOT / "evaluation/downstream_benchmark"
E = Path(__file__).resolve().parent
WORK = Path("/Users/wuyangchenxi/errpilot-benchmark-work")
META = WORK / "bugsinpy"
BASELINE = "3939dfca7f25d3c1d4cd97c76b3676694cda84be"
POOL_SHA = "42d47f13f39fbdbb335cd741e1c361b2dbf690d5e72382136a61f2608e16fe78"
CURRENT_SHA = "9295430e8573474b17bc79339c92f46044e443b9dabfe81280f9fb789d751073"
MANIFEST = B / "v6_preparation_plan_manifest_candidate.json"
TABLE = B / "v6_preparation_planning_cases_candidate.csv"
NEGATIVE = {k: "NO" for k in (
    "PREPARATION_AUTHORIZED", "SOURCE_ACQUISITION_AUTHORIZED",
    "MATERIALIZATION_AUTHORIZED", "IMAGE_BUILD_AUTHORIZED", "ORACLE_AUTHORIZED",
    "ALLOCATION_AUTHORIZED")}
VOCABULARY = [
    "PREPARATION_PLAN_CONSTRUCTIBLE",
    "PREPARATION_PLAN_BLOCKED_SOURCE_IDENTITY",
    "PREPARATION_PLAN_REQUIRES_SOURCE_ACQUISITION",
    "PREPARATION_PLAN_BLOCKED_REQUIREMENTS_REPRESENTATION",
    "PREPARATION_PLAN_BLOCKED_SETUP_REPRESENTATION",
    "PREPARATION_PLAN_BLOCKED_ORACLE_REPRESENTATION",
    "PREPARATION_PLAN_BLOCKED_RUNTIME_REPRESENTATION",
    "PREPARATION_PLAN_UNDERDETERMINED",
]
PRIORITY = ["SOURCE_IDENTITY", "REQUIREMENTS_REPRESENTATION", "SETUP_REPRESENTATION",
            "ORACLE_REPRESENTATION", "RUNTIME_REPRESENTATION", "UNDERDETERMINED",
            "SOURCE_ACQUISITION"]
COUNTER_KEYS = dict(zip(VOCABULARY, [
    "PLAN_CONSTRUCTIBLE", "SOURCE_IDENTITY_BLOCKED", "SOURCE_ACQUISITION_REQUIRED",
    "REQUIREMENTS_REPRESENTATION_BLOCKED", "SETUP_REPRESENTATION_BLOCKED",
    "ORACLE_REPRESENTATION_BLOCKED", "RUNTIME_REPRESENTATION_BLOCKED", "UNDERDETERMINED"]))
STATUS_FOR = dict(zip(PRIORITY, [VOCABULARY[1], VOCABULARY[3], VOCABULARY[4],
                              VOCABULARY[5], VOCABULARY[6], VOCABULARY[7], VOCABULARY[2]]))
COMMAND_COUNTS = collections.Counter()
WRITES = set()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":"), allow_nan=False) + "\n").encode()


def identity(value):
    return sha(canonical(value))


def require(ok, why):
    if not ok:
        raise ValueError(why)


def audit(event, args):
    if event == "subprocess.Popen":
        argv = args[1]
        require(isinstance(argv, (tuple, list)) and argv[0] == "git", "non-Git process forbidden")
        index = 3 if len(argv) > 2 and argv[1] == "-C" else 1
        verb = argv[index]
        require(verb in {"rev-parse", "status", "branch", "diff", "ls-files", "ls-tree",
                         "show", "cat-file", "remote", "log", "diff-tree", "merge-base"},
                "mutating or network Git forbidden")
        require(verb != "remote" or argv[index + 1] == "get-url", "mutating remote command")
        COMMAND_COUNTS[verb] += 1
    elif event == "open":
        path, mode, flags = args
        writing = (isinstance(mode, str) and any(x in mode for x in "wax+")) or (
            flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        if writing and isinstance(path, (str, bytes, os.PathLike)):
            target = Path(os.fsdecode(path)).absolute()
            require(target == MANIFEST or target == TABLE or target.parent == E,
                    "write outside candidate evidence: " + str(target))
            WRITES.add(str(target.relative_to(ROOT)))
    elif event.startswith("socket.") or event in {"os.system", "os.posix_spawn", "os.fork"}:
        raise ValueError("network or alternate execution forbidden")


sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))
sys.addaudithook(audit)
from evaluation.downstream_benchmark.screening import (  # noqa: E402
    audit_environment as ae, build_recipes as br, build_candidate_universe as metadata,
    executor as ex, materializer as mat, prepare_expansion_block_03 as p3,
)


def git(repo, *args, input=None, check=True):
    r = subprocess.run(["git", "-C", str(repo), *args], input=input,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
                       env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"})
    if check:
        require(r.returncode == 0, "local Git failed: " + " ".join(args) + ": " + r.stderr.decode(errors="replace"))
    return r.stdout if check else r


def rows(path):
    return list(csv.DictReader(path.open(newline="", encoding="utf-8")))


def file_ref(path):
    return {"path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
            "sha256": sha(path.read_bytes())}


def save(path, value):
    path.write_bytes(canonical(value))


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def snapshot_external():
    found = {}
    for root in WORK.iterdir():
        if root.name in {"bugsinpy", "subject_repositories", "caches"}:
            continue
        for base, dirs, files in os.walk(root):
            dirs[:] = [x for x in dirs if x not in {"source", "context", "workspace", ".git",
                                                  "BUGGY", "FIXED", "SOURCE_INDEPENDENT"}]
            for name in files:
                if name in {"attempt.json", "preparation_plan.json", "source_identity.json"} or name.endswith("_plan.json"):
                    path = Path(base) / name
                    found[str(path)] = sha(path.read_bytes())
    return found


def entry():
    require(git(ROOT, "rev-parse", "HEAD").decode().strip() == BASELINE, "baseline drift")
    require(git(ROOT, "branch", "--show-current").decode().strip() == "main", "branch drift")
    require(not git(ROOT, "diff", "--cached", "--name-only"), "index not clean")
    tracked = {name: sha((ROOT / name).read_bytes()) for name in
               git(ROOT, "ls-files").decode().splitlines() if (ROOT / name).is_file()}
    require(not git(ROOT, "diff", "--name-only"), "tracked worktree drift")
    pool = rows(B / "v6_reconsideration_pool.csv")
    require(sha((B / "v6_reconsideration_pool.csv").read_bytes()) == POOL_SHA, "pool hash")
    require(sha((B / "v6_current_state.json").read_bytes()) == CURRENT_SHA, "descriptor hash")
    a = module("v6_planning_frozen_activation", B / "evidence/v6_census_membership_activation_v1_after_genesis_bridge/validate_activation.py")
    d = json.loads((B / "v6_current_state.json").read_bytes())
    a.c.validate_schema("V6_CAPACITY_CURRENT_STATE_V1", d)
    prior = git(ROOT, "show", a.HEAD + ":evaluation/downstream_benchmark/v6_current_state.json")
    bridge_bytes = (ROOT / a.v.BRIDGE_PATH).read_bytes()
    baseline = a.baseline_evidence()
    a.verify_bridge_governance(bridge_bytes, (ROOT / a.BRIDGE_CLOSURE).read_bytes(), a.HEAD)
    _, projection, event, event_raw, source, _ = a.derive(
        prior, json.loads(bridge_bytes), baseline,
        json.loads((a.E / "activation_authority.json").read_bytes()))
    require(event_raw == (a.E / "activation_event_candidate.json").read_bytes(), "event replay")
    require(d["projection"] == projection and d["event_chain"] == source["event_chain"], "chain replay")
    require(d["event_count"] == 1 and d["runtime_authority"] is True, "current authority")
    require(set(d["projection"]["phase_authorizations"].values()) == {"NO"}, "phase authority")
    pb = json.loads((B / "v6_predecessor_evidence_bridge.json").read_bytes())
    historical = set()
    continuity = {}
    for key, expected in [("grandfathered_eligible", 9), ("scientific_ineligible", 12),
                          ("infrastructure_unresolved", 7), ("accepted_pre_eligibility_exclusions", 39)]:
        group = pb["groups"][key]
        ids = {x["case_id"] for x in group["cases"]}
        require(group["count"] == len(ids) == expected and not ids & historical, "predecessor partition")
        continuity[key] = expected
        historical |= ids
    require(not historical & {x["case_id"] for x in pool}, "predecessor overlap")
    for key in ["pre_eligibility_state", "oracle_outcomes", "predecessor_artifact_inventory"]:
        a.c.check_ref(pb[key])
    contract = json.loads((B / "v6_capacity_successor_contract.json").read_bytes())
    for group in ["artifacts", "schemas"]:
        for ref in contract[group].values():
            a.c.check_ref(ref)
    run = a.c.embedded(B / "V6_CAPACITY_SUCCESSOR_RUN_SPEC.md", "CONTRACT_JSON")
    for ref in run["inherit_by_exact_digest"].values():
        a.c.check_ref(ref)
    external = snapshot_external()
    for name in external:
        obj = json.loads(Path(name).read_bytes())
        require(obj.get("canonical_case_id", obj.get("case_id")) not in {x["case_id"] for x in pool}, "prior census execution evidence")
        require("V6" not in str(obj.get("schema", "")), "prior V6 artifact")
    ex.validate_bugsinpy_checkout(META)
    result = {
        "status": "ENTRY_PASS", "authority": "OPEN_V6_PREPARATION_PLANNING",
        "authority_source": file_ref(Path("/Users/wuyangchenxi/.codex/attachments/4b1e5489-e177-4597-8300-ceb0c6763a14/已粘贴的文本.txt")),
        "repo": str(ROOT), "branch": "main", "local_head": BASELINE, "live_origin_main": BASELINE,
        "live_ref_evidence": "Read-only git ls-remote --exit-code origin refs/heads/main succeeded; sandbox DNS query failed, elevated read-only query matched.",
        "clean_worktree_before_any_write": True, "clean_index_before_any_write": True,
        "entry_gate_before_write": "Full inline read-only entry validator exited 0 before construct_candidate.py was created; 242 external metadata files checked.",
        "current_descriptor": file_ref(B / "v6_current_state.json"), "pool": file_ref(B / "v6_reconsideration_pool.csv"),
        "event_count": 1, "full_event_replay": "PASS", "predecessor_counts": continuity,
        "canonical_planning_flag": "NO", "direct_request_planning_scope": "Candidate-only; no state transition or canonical authorization write.",
        "downstream_authority": NEGATIVE, "no_prior_v6_plan_or_execution_found": True,
        "external_metadata_sha256": external, "tracked_sha256": tracked,
        "root_airos_present": (ROOT / ".airos").exists(),
    }
    return result, pool, run


def pinned_inputs(pool):
    tree = git(META, "ls-tree", "-r", "-z", ex.BUGSINPY_COMMIT, "projects")
    objects = {}
    for record in tree.split(b"\0"):
        if record:
            header, path = record.split(b"\t", 1)
            mode, kind, oid = header.split()
            objects[path.decode()] = (mode.decode(), kind.decode(), oid.decode())
    registry = {}
    for row in pool:
        project, bug = row["source_project"], row["bugsinpy_bug_id"]
        prefix = f"projects/{project}/bugs/{bug}"
        for relative in [f"projects/{project}/project.info", *[f"{prefix}/{n}" for n in
                         ("bug.info", "run_test.sh", "setup.sh", "requirements.txt")]]:
            if relative in registry:
                continue
            path = META / relative
            if relative not in objects:
                require(not path.exists(), "unpinned metadata input " + relative)
                registry[relative] = {"path": relative, "present": False, "sha256": "ABSENT"}
                continue
            mode, kind, oid = objects[relative]
            require(kind == "blob" and mode in {"100644", "100755"}, "unsafe metadata input")
            raw = path.read_bytes()
            require(raw == git(META, "cat-file", "blob", oid), "metadata checkout drift " + relative)
            registry[relative] = {"path": relative, "present": True, "git_blob": oid,
                                  "sha256": sha(raw), "bytes_b64": base64.b64encode(raw).decode()}
    return registry


def disposition(blockers):
    for category in PRIORITY:
        if any(x["category"] == category for x in blockers):
            return STATUS_FOR[category]
    return VOCABULARY[0]


def construct(pool, inputs):
    universe = {r["canonical_case_id"]: r for r in rows(B / "candidate_universe.csv")}
    projects = {}
    plans = []
    trees = {}
    blob_availability = {}
    for row in pool:
        cid, project, bug = row["case_id"], row["source_project"], row["bugsinpy_bug_id"]
        u = universe[cid]
        prefix = f"projects/{project}/bugs/{bug}"
        case_dir = META / prefix
        pi = metadata.parse_literal_assignments(META / f"projects/{project}/project.info")
        bi = metadata.parse_literal_assignments(case_dir / "bug.info")
        require(u["project"] == project and u["bugsinpy_bug_id"] == bug and int(u["candidate_rank"]) == int(row["frozen_rank"]), "case metadata identity")
        for field in ["buggy_commit_id", "fixed_commit_id", "python_version"]:
            require(bi[field] == u[field], "pinned metadata mismatch " + cid + ":" + field)
        require(pi["github_url"] == u["project_source_url"], "repository metadata drift")
        require(bi["test_file"] == u["declared_test_file"] and pi["status"] == "OK", "declared test/project status drift")
        mirror = WORK / "subject_repositories" / (ex.safe_case_slug(project) + ".git")
        blockers = []

        def block(category, mechanism, **details):
            blockers.append({"category": category, "mechanism": mechanism, **details})

        if project not in projects:
            present = mirror.is_dir()
            actual_url = git(mirror, "remote", "get-url", "origin").decode().strip() if present else None
            bare = git(mirror, "rev-parse", "--is-bare-repository").decode().strip() == "true" if present else None
            fmt = git(mirror, "rev-parse", "--show-object-format").decode().strip() if present else None
            projects[project] = {"source_project": project, "expected_url": pi["github_url"],
                                 "mirror_path": str(mirror), "locally_present": present,
                                 "observed_origin": actual_url, "bare": bare, "object_format": fmt}
        repo = projects[project]
        good_mirror = repo["locally_present"] and repo["bare"] and ex._remote_urls_match(pi["github_url"], repo["observed_origin"])
        if repo["locally_present"] and not good_mirror:
            block("SOURCE_IDENTITY", "MIRROR_IDENTITY_MISMATCH")
        variants = []
        for label, field in [("BUGGY", "buggy_commit_id"), ("FIXED", "fixed_commit_id")]:
            revision = bi[field]
            full = revision.lower() if re.fullmatch(r"[0-9a-fA-F]{40}", revision) else None
            available = "UNKNOWN"
            if good_mirror:
                try:
                    full = ex.resolve_revision(mirror, revision)
                    available = "YES"
                except ex.PreparationError:
                    available = "NO"
            elif not repo["locally_present"]:
                available = "NO"
            if full is None:
                block("SOURCE_IDENTITY", "ABBREVIATED_REVISION_NOT_UNIQUELY_RESOLVED", variant=label, declared_revision=revision)
            elif available == "NO":
                block("SOURCE_ACQUISITION", "REQUIRED_COMMIT_NOT_LOCAL", variant=label, commit=full)
            export = {"schema": "SOURCE_SNAPSHOT_MANIFEST_V2", "source_export_executed": False,
                      "snapshot_sha256": None, "tracked_gitlinks": [], "tracked_symlink_count": None,
                      "tree_metadata_status": "NOT_AVAILABLE"}
            if available == "YES":
                key = (project, full)
                if key not in trees:
                    result = git(mirror, "ls-tree", "-r", "-z", full, check=False)
                    entries = []
                    if result.returncode == 0:
                        for record in result.stdout.split(b"\0"):
                            if record:
                                header, path = record.split(b"\t", 1)
                                mode, kind, oid = header.split()
                                entries.append((path, mode, kind, oid))
                    trees[key] = (result.returncode, sha(result.stdout), entries)
                rc, tree_sha, entries = trees[key]
                export.update({"tree_metadata_sha256": tree_sha, "tracked_entry_count": len(entries),
                               "tree_metadata_status": "RESOLVED" if rc == 0 else "UNAVAILABLE",
                               "tracked_symlink_count": 0})
                if rc:
                    block("SOURCE_ACQUISITION", "REQUIRED_TREE_NOT_LOCAL", variant=label, commit=full)
                for path, mode, kind, oid in entries:
                    try:
                        name = path.decode("utf-8", errors="strict")
                    except UnicodeError:
                        block("UNDERDETERMINED", "SOURCE_PATH_NOT_UTF8", variant=label, path_b64=base64.b64encode(path).decode())
                        continue
                    if any(x in mat.FORBIDDEN_SNAPSHOT_NAMES for x in name.split("/")):
                        block("UNDERDETERMINED", "FORBIDDEN_SOURCE_METADATA_PATH", variant=label, path=name)
                    if mode == b"160000":
                        export["tracked_gitlinks"].append({"path": name, "object_id": oid.decode(), "mode": "160000"})
                        block("UNDERDETERMINED", "GITLINK_OUTSIDE_FROZEN_COOKIECUTTER_SCOPE", variant=label, path=name, object_id=oid.decode())
                    elif mode == b"120000":
                        export["tracked_symlink_count"] += 1
                        target = git(mirror, "cat-file", "blob", oid.decode(), check=False)
                        if target.returncode:
                            block("SOURCE_ACQUISITION", "REQUIRED_SYMLINK_BLOB_NOT_LOCAL", variant=label, object_id=oid.decode())
                        else:
                            try:
                                mat._safe_link_target(tuple(path.split(b"/")[:-1]), target.stdout)
                            except mat.Blocked as exc:
                                block("UNDERDETERMINED", "UNSAFE_TRACKED_SYMLINK", variant=label, path=name, reason=str(exc))
                    elif mode not in {b"100644", b"100755"} or kind != b"blob":
                        block("UNDERDETERMINED", "UNSUPPORTED_GIT_TREE_ENTRY", variant=label, path=name, mode=mode.decode())
            variants.append({"label": label, "revision_metadata": revision, "commit_oid": full,
                             "object_locally_present": available, "source_export_planning": export})
        if variants[0]["commit_oid"] and variants[0]["commit_oid"] == variants[1]["commit_oid"]:
            block("SOURCE_IDENTITY", "BUGGY_FIXED_IDENTITY_COLLISION")
        script = (case_dir / "run_test.sh").read_bytes()
        oracle = ex.analyze_oracle(script)
        oracle["argv"] = ([list(ex.parse_recognized_command(x)) for x in oracle["commands"]]
                          if oracle["status"] == "RESOLVED_ORDERED_COMMANDS" else [])
        oracle.update({"script_sha256": sha(script), "representation": "COMPOSITE_ORACLE_SEMANTICS_V1",
                       "executed": False, "future_cwd": "subject repository root"})
        if oracle["status"] != "RESOLVED_ORDERED_COMMANDS":
            block("ORACLE_REPRESENTATION", "SHARED_ORACLE_PARSER_REJECTS_LITERAL", reason=oracle["blocking_reason"], commands=oracle["commands"])
        raw = (case_dir / "requirements.txt").read_bytes() if (case_dir / "requirements.txt").is_file() else None
        normalized = dependency = None
        ledger = []
        encoding = "ABSENT"
        if raw is not None:
            try:
                normalized, encoding = br.normalize_requirements(raw)
                require((normalized, encoding) == br.normalize_requirements(raw), "requirements nondeterministic")
                dependency, ledger = br.derive_dependency_input(normalized, case_id=cid, project=project, source_url=pi["github_url"])
            except (UnicodeError, br.RecipeError) as exc:
                block("REQUIREMENTS_REPRESENTATION", "INHERITED_REQUIREMENTS_REPRESENTATION_REJECTS_LITERAL", reason=str(exc))
        setup = (case_dir / "setup.sh").read_bytes() if (case_dir / "setup.sh").is_file() else None
        setup_lines = []
        actions = []
        mode = "UNRESOLVED"
        try:
            if setup is not None:
                setup_lines = [{"line": n, "category": ae.classify_setup_line(line), "text": line}
                               for n, line in enumerate(setup.decode("utf-8", errors="strict").splitlines(), 1)
                               if line.strip() and not line.lstrip().startswith("#")]
            actions = br.setup_actions(setup, json.dumps(setup_lines))
            mode = br.environment_mode(actions)
            for action in actions:
                try:
                    action["future_argv"] = mat.action_argv(action, source_present=action["consumes_subject_source"])
                except mat.Blocked as exc:
                    block("SETUP_REPRESENTATION", "MATERIALIZER_ARGV_REJECTS_ACTION", line=action["source_line_ordinal"], text=action["exact_source_text"], reason=str(exc))
        except (UnicodeError, br.RecipeError) as exc:
            block("SETUP_REPRESENTATION", "SHARED_SETUP_REPRESENTATION_REJECTS_LITERAL", reason=str(exc), lines=setup_lines)
        if setup is not None and ex._setup_invokes_tests(setup):
            block("SETUP_REPRESENTATION", "SETUP_CONTAINS_TEST_OR_UNSAFE_ACTION", lines=setup_lines)
        runtime = None
        try:
            runtime = p3._image(B, bi["python_version"])
        except br.RecipeError as exc:
            block("RUNTIME_REPRESENTATION", "EXACT_BASE_RUNTIME_BINDING_UNRESOLVED", reason=str(exc))
        c = ex.Candidate(int(row["frozen_rank"]), int(row["census_order"]), cid, project, bug,
                         pi["github_url"], bi["python_version"], bi["buggy_commit_id"], bi["fixed_commit_id"],
                         u["declared_test_file"], ex.BUGSINPY_COMMIT)
        protected = {"status": "PENDING_SOURCE_OBJECTS", "rule": "Only declared fixed test bytes injected into BUGGY; preserve raw and effective manifests", "manifest_sha256": None}
        if all(v["object_locally_present"] == "YES" for v in variants):
            protected = ex.build_protected_manifest(c, mirror, variants[0]["commit_oid"], variants[1]["commit_oid"], oracle["commands"])
            if protected["status"] != "RESOLVED":
                block("UNDERDETERMINED", "PROTECTED_MANIFEST_UNRESOLVED", errors=protected["errors"])
        req = {"raw_sha256": sha(raw) if raw is not None else "ABSENT", "encoding": encoding,
               "normalized_sha256": sha(normalized) if normalized is not None else "ABSENT" if raw is None else "UNRESOLVED",
               "dependency_input_sha256": sha(dependency) if dependency is not None else "ABSENT" if raw is None else "UNRESOLVED",
               "normalized_bytes_b64": base64.b64encode(normalized).decode() if normalized is not None else None,
               "dependency_bytes_b64": base64.b64encode(dependency).decode() if dependency is not None else None,
               "self_reference_ledger": ledger, "self_reference_ledger_sha256": identity(ledger),
               "policy": "Inherited ENVIRONMENT_BUILD_SPEC_V1 C/E only; strict decoding/newline representation and proven self-reference omissions; no version/marker/comment/order repairs"}
        semantic_actions = [{k: v for k, v in x.items() if k != "future_argv"} for x in actions]
        recipe = {"schema": "V6_PREPARATION_RECIPE_PROPOSAL_V1", "python_declared_version": bi["python_version"],
                  "base_runtime": runtime, "runtime_platform": "linux/amd64", "requirements": req,
                  "setup_sha256": sha(setup) if setup is not None else "ABSENT", "setup_lines": setup_lines,
                  "setup_actions": actions, "setup_action_ledger_sha256": identity(semantic_actions),
                  "environment_mode_v2": mode,
                  "pythonpath_metadata": ae._literal_pythonpaths((case_dir / "bug.info").read_bytes()) + ae._literal_pythonpaths((META / f"projects/{project}/project.info").read_bytes()),
                  "source_install_policy": "EXPLICIT_SETUP_ACTIONS_ONLY", "system_package_requirements": "UNKNOWN",
                  "future_network_build_policy": "DECLARED_DEPENDENCY_SOURCES_ONLY_SEPARATE_AUTHORITY_REQUIRED",
                  "future_network_execution_policy": "NONE", "protected_manifest": protected,
                  "source_preparation": "Frozen revision; preserve file modes and safe symlinks; hash-pinned declared-test injection only; no source export in this transaction"}
        plan = {"schema": "V6_PREPARATION_CASE_PLAN_CANDIDATE_V1", "candidate_only": True,
                "baseline": BASELINE, "current_descriptor_sha256": CURRENT_SHA, "pool_sha256": POOL_SHA,
                "case_id": cid, "census_order": int(row["census_order"]), "frozen_rank": int(row["frozen_rank"]),
                "source_project": project, "bugsinpy_bug_id": bug, "source_repository": repo,
                "source_variants": variants, "input_bindings": [inputs[f"projects/{project}/project.info"]["sha256"], *[inputs[f"{prefix}/{n}"]["sha256"] for n in ("bug.info", "run_test.sh", "setup.sh", "requirements.txt")]],
                "input_paths": [f"projects/{project}/project.info", *[f"{prefix}/{n}" for n in ("bug.info", "run_test.sh", "setup.sh", "requirements.txt")]],
                "recipe_candidate": recipe, "oracle": oracle, "applicable_case_specific_bridges": [],
                "downstream_authority": NEGATIVE, "blockers": blockers, "planning_disposition": disposition(blockers)}
        plan["plan_sha256"] = identity(plan)
        plans.append(plan)
        if len(plans) % 50 == 0:
            print(f"Planned {len(plans)}/433", flush=True)
    # Verify leaf-object availability in one read-only batch per project. No blob bytes are exported.
    missing_by_project = {}
    for project in projects:
        oids = sorted({oid.decode() for (p, _), (_, _, entries) in trees.items() if p == project
                       for _, mode, kind, oid in entries if kind == b"blob"})
        if not oids:
            continue
        output = git(Path(projects[project]["mirror_path"]), "cat-file", "--batch-check", input=("\n".join(oids) + "\n").encode())
        missing = {line.split()[0].decode() for line in output.splitlines() if line.endswith(b" missing")}
        missing_by_project[project] = missing
        blob_availability[project] = {"unique_required_leaf_blob_objects": len(oids), "missing": sorted(missing)}
    for plan in plans:
        missing = missing_by_project.get(plan["source_project"], set())
        for variant in plan["source_variants"]:
            key = (plan["source_project"], variant["commit_oid"])
            if key in trees:
                required_missing = sorted({oid.decode() for _, _, kind, oid in trees[key][2] if kind == b"blob" and oid.decode() in missing})
                variant["source_export_planning"]["missing_required_blob_objects"] = required_missing
                if required_missing:
                    plan["blockers"].append({"category": "SOURCE_ACQUISITION", "mechanism": "REQUIRED_SOURCE_BLOB_NOT_LOCAL", "variant": variant["label"], "objects": required_missing})
        plan["planning_disposition"] = disposition(plan["blockers"])
        plan.pop("plan_sha256")
        plan["plan_sha256"] = identity(plan)
    return plans, projects, blob_availability


def build():
    gate, pool, run = entry()
    save(E / "entry_verification.json", gate)
    inputs = pinned_inputs(pool)
    plans, projects, blobs = construct(pool, inputs)
    tally = collections.Counter(p["planning_disposition"] for p in plans)
    counts = {COUNTER_KEYS[key]: tally[key] for key in VOCABULARY}
    counts.update({"TOTAL_CENSUS_CASES": len(plans), "EXPECTED_VARIANT_BINDINGS": sum(len(p["source_variants"]) for p in plans)})
    incidence = collections.Counter()
    for p in plans:
        incidence.update({b["category"] for b in p["blockers"]})
    manifest = {
        "schema": "V6_PREPARATION_PLAN_MANIFEST_CANDIDATE_V1", "candidate_only": True,
        "runtime_authority": False, "lifecycle": "CANDIDATE_ONLY", "baseline": BASELINE,
        "current_descriptor": file_ref(B / "v6_current_state.json"), "canonical_pool": file_ref(B / "v6_reconsideration_pool.csv"),
        "bugsinpy": {"path": str(META), "commit": ex.BUGSINPY_COMMIT, "tree": ex.BUGSINPY_TREE},
        "selection": {"method": "EXPLICIT_MANIFEST_SHA256_AND_CASE_ORDINAL", "dispatch_order": "ORIGINAL_FROZEN_RANK_ASCENDING",
                      "governed_batches": False, "runtime_chunk_scientific_identity": "NONE", "runtime_chunk_admission_authority": "NONE",
                      "fallback": "NONE", "stop_at_capacity": False, "automatic_retry": False, "automatic_rescue": False},
        "identity_convention": {"canonical_json": "UTF-8, sorted keys, compact separators, ensure_ascii=false, one final LF",
                                "plan_sha256": "SHA-256 of complete plan excluding only plan_sha256; follows executor.deterministic_plan_hash serialization",
                                "new_plan_and_manifest_schemas": "PROPOSAL_LEVEL_HUMAN_PI_REVIEW_REQUIRED"},
        "planning_vocabulary": {"authority": "PROPOSAL_LEVEL_ONLY_NO_CANONICAL_EFFECT", "statuses": VOCABULARY,
                                "primary_priority": PRIORITY, "blocker_incidence_is_overlapping": True},
        "downstream_authority": NEGATIVE, "inherited_contracts": run["inherit_by_exact_digest"],
        "metadata_inputs": inputs, "projects": projects, "leaf_object_availability": blobs,
        "counts": counts, "blocker_incidence_case_counts": dict(sorted(incidence.items())), "plans": plans,
        "future_authority": {"existing_lifecycle": file_ref(B / "v6_census_lifecycle.json"),
                             "next_review": "HUMAN_PI_REVIEW_OF_V6_PREPARATION_PLAN",
                             "edges": [
                                 ["CENSUS_MEMBERSHIP_ACTIVATED", "PREPARATION_PLANNING_AUTHORIZED", "HUMAN_PI_AUTHORIZE_V6_PREPARATION_PLANNING"],
                                 ["PREPARATION_PLANNING_AUTHORIZED", "PREPARATION_EXECUTION_AUTHORIZED", "HUMAN_PI_AUTHORIZE_V6_PREPARATION_EXECUTION"],
                                 ["PREPARATION_EXECUTION_AUTHORIZED", "PREPARATION_COMPLETE", "HUMAN_PI_ACCEPT_V6_PREPARATION_CLOSURE"]],
                             "separate_subauthorities": ["SOURCE_ACQUISITION", "ENVIRONMENT_MATERIALIZATION", "IMAGE_BUILD"],
                             "execution_prerequisites": "Exact accepted plans, revalidated implementation with V6 input/runtime bindings, once-only attempts, explicit output namespaces and applicable publication/network permissions; old V5 tokens/adapters confer no V6 authority",
                             "new_bridge_if_required": "Separate Human-PI successor adjudication for exact cases and literal mechanisms; no bridge created here"},
    }
    save(MANIFEST, manifest)
    fields = ["census_order", "case_id", "source_project", "bugsinpy_bug_id", "frozen_rank", "plan_sha256",
              "planning_disposition", "buggy_revision_metadata", "buggy_commit_oid", "buggy_object_locally_present",
              "fixed_revision_metadata", "fixed_commit_oid", "fixed_object_locally_present", "requires_source_acquisition",
              "blocker_categories", "blocker_mechanisms", "oracle_status", "python_version", "environment_mode"]
    with TABLE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for p in plans:
            buggy, fixed = p["source_variants"]
            writer.writerow({**{k: p[k] for k in fields[:7]},
                             "buggy_revision_metadata": buggy["revision_metadata"], "buggy_commit_oid": buggy["commit_oid"],
                             "buggy_object_locally_present": buggy["object_locally_present"],
                             "fixed_revision_metadata": fixed["revision_metadata"], "fixed_commit_oid": fixed["commit_oid"],
                             "fixed_object_locally_present": fixed["object_locally_present"],
                             "requires_source_acquisition": any(b["category"] == "SOURCE_ACQUISITION" for b in p["blockers"]),
                             "blocker_categories": "|".join(sorted({b["category"] for b in p["blockers"]})),
                             "blocker_mechanisms": "|".join(sorted({b["mechanism"] for b in p["blockers"]})),
                             "oracle_status": p["oracle"]["status"], "python_version": p["recipe_candidate"]["python_declared_version"],
                             "environment_mode": p["recipe_candidate"]["environment_mode_v2"]})
    save(E / "lineage.json", {"baseline": BASELINE, "current_descriptor": manifest["current_descriptor"],
                              "canonical_pool": manifest["canonical_pool"], "inherited_contracts": manifest["inherited_contracts"],
                              "builder": file_ref(Path(__file__)), "authority_source": gate["authority_source"],
                              "candidate_artifacts": [file_ref(MANIFEST), file_ref(TABLE)],
                              "predecessor_counts_preserved": gate["predecessor_counts"], "canonical_state_written": False})
    save(E / "construction_observations.json", {
        "read_only_git_command_counts": dict(COMMAND_COUNTS), "writes": sorted(WRITES),
        "non_git_processes": 0, "network_calls": 0, "source_exports": 0, "setup_or_oracle_calls": 0,
        "unique_project_count": len(projects), "local_mirror_count": sum(p["locally_present"] for p in projects.values()),
        "variant_commit_bindings": sum(v["commit_oid"] is not None for p in plans for v in p["source_variants"]),
        "local_variant_commits": sum(v["object_locally_present"] == "YES" for p in plans for v in p["source_variants"]),
        "unique_commit_objects_by_repository": len({(p["source_project"], v["commit_oid"]) for p in plans for v in p["source_variants"] if v["commit_oid"]}),
        "unique_recipe_families": len({identity({k: p["recipe_candidate"][k] for k in ["python_declared_version", "requirements", "setup_sha256", "setup_actions", "pythonpath_metadata", "environment_mode_v2"]}) for p in plans}),
        "base_runtime_families": dict(collections.Counter(p["recipe_candidate"]["python_declared_version"] for p in plans)),
        "counts": counts, "blocker_incidence_case_counts": manifest["blocker_incidence_case_counts"],
        "full_source_export_representations": "Only tree modes/paths and symlink/test blob hashes checked; no snapshot identity fabricated",
    })
    require(snapshot_external() == gate["external_metadata_sha256"], "external evidence changed")
    require(all(sha((ROOT / name).read_bytes()) == value for name, value in gate["tracked_sha256"].items()), "pre-existing tracked files changed")
    print(json.dumps({"manifest_sha256": sha(MANIFEST.read_bytes()), "counts": counts,
                      "blocker_incidence": manifest["blocker_incidence_case_counts"], "projects": len(projects)}, sort_keys=True), flush=True)


if __name__ == "__main__":
    require(sys.argv[1:] == ["construct-candidate"], "explicit construct-candidate mode required")
    build()

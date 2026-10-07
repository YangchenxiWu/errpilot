"""Exact V6 input projection adapted from the Human-PI accepted candidate.

Selection/projection are read-only. Execution authority is checked separately.
The planning descriptor identity is retained in stable base attempt identities.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

from evaluation.downstream_benchmark.screening import materializer as shared

ROOT = Path(__file__).resolve().parents[3]
B = ROOT / "evaluation/downstream_benchmark"
CURRENT = "evaluation/downstream_benchmark/v6_current_state.json"
CURRENT_SHA = "6a9028c79aa62f90db2b2d53def32ab23bffcfa3c71d2ec30d7fa64e741e3aae"
MANIFEST = "evaluation/downstream_benchmark/v6_preparation_plan_manifest_candidate.json"
MANIFEST_SHA = "3c0a6980360c23f6626863be232fea2878cf13497a74aa2e267594fcf3801b0e"
CLOSURE = "evaluation/downstream_benchmark/V6_PREPARATION_PLAN_LIFECYCLE_CLOSURE_V1.md"
CLOSURE_SHA = "9e0bbf8db1eaedb344163a98e944915a51e87424d4abf6894545056e73eccfe7"
WORK_ROOT = Path("/Users/wuyangchenxi/errpilot-benchmark-work")
OUTPUT_ROOT = WORK_ROOT / "v6_preparation_execution_v1"
CONSTRUCTIBLE = "PREPARATION_PLAN_CONSTRUCTIBLE"
NETWORK_POLICY = "DECLARED_DEPENDENCY_SOURCES_ONLY_SEPARATE_AUTHORITY_REQUIRED"
SCHEMA = "V6_PREPARATION_RUNTIME_INPUT_BINDING_CANDIDATE_V1"


class Rejected(ValueError):
    """A candidate binding is ambiguous, changed or unauthorized."""


def require(condition, message):
    if not condition:
        raise Rejected(message)


def canonical(value):
    def check(x):
        if isinstance(x, dict):
            require(all(isinstance(k, str) for k in x), "non-string JSON key")
            for v in x.values():
                check(v)
        elif isinstance(x, list):
            for v in x:
                check(v)
        else:
            require(x is None or type(x) in (str, int, bool), "non-canonical JSON value")
    check(value)
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(value):
    return sha(canonical(value))


def loads(raw):
    def unique(pairs):
        result = {}
        for k, v in pairs:
            require(k not in result, "duplicate JSON key")
            result[k] = v
        return result
    value = json.loads(raw, object_pairs_hook=unique)
    canonical(value)
    return value


def read_exact(relative, digest):
    path = ROOT / relative
    require(not path.is_symlink() and path.is_file(), "missing/symlink exact input")
    require(all(not p.is_symlink() for p in path.parents if p.is_relative_to(ROOT)),
            "symlink input ancestor")
    if relative == CURRENT and digest == CURRENT_SHA:
        result = subprocess.run(["git", "cat-file", "blob",
            "5c007fbfbfc5b3529105a14f87127f50e1eab6d7:" + CURRENT],
            cwd=ROOT, capture_output=True, check=False)
        require(result.returncode == 0, "accepted planning baseline unavailable")
        raw = result.stdout
    else:
        raw = path.read_bytes()
    require(sha(raw) == digest, "exact input SHA mismatch: " + relative)
    return raw


def load_inputs(*, current_path=CURRENT, current_sha=CURRENT_SHA,
                manifest_path=MANIFEST, manifest_sha=MANIFEST_SHA):
    require((current_path, current_sha) == (CURRENT, CURRENT_SHA), "wrong current descriptor")
    require((manifest_path, manifest_sha) == (MANIFEST, MANIFEST_SHA), "wrong manifest SHA/path")
    descriptor = loads(read_exact(CURRENT, CURRENT_SHA))
    manifest = loads(read_exact(MANIFEST, MANIFEST_SHA))
    read_exact(CLOSURE, CLOSURE_SHA)
    require(descriptor["candidate_only"] is False and descriptor["event_count"] == 2,
            "current descriptor effectivity/count")
    projection = descriptor["projection"]
    require(descriptor["lifecycle_label"] == projection["state"]
            == "PREPARATION_PLANNING_AUTHORIZED", "planning current required")
    require(projection["lifecycle"]["PREPARATION_AUTHORIZED"] == "NO", "execution effective")
    expected = {k: "NO" for k in projection["phase_authorizations"]}
    expected["PREPARATION_PLANNING"] = "YES"
    require(projection["phase_authorizations"] == expected, "phase firewall")
    require(len(projection["case_states"]) == 433 and all(
        c["phase"] == "NOT_STARTED" and c["attempt_consumed"] is False
        and c["environment_identity"] is None for c in projection["case_states"]),
        "canonical cases/attempts/readiness")
    for ref in [descriptor["contract"], *descriptor["event_chain"]]:
        read_exact(ref["path"], ref["sha256"])
    for ref in manifest["inherited_contracts"].values():
        read_exact(ref["path"], ref["sha256"])
    require(manifest["counts"]["TOTAL_CENSUS_CASES"] == 433
            and manifest["counts"]["PLAN_CONSTRUCTIBLE"] == 431
            and manifest["counts"]["SOURCE_ACQUISITION_REQUIRED"] == 0, "plan counts")
    require([(c["case_id"], c["frozen_rank"]) for c in projection["case_states"]]
            == [(p["case_id"], p["frozen_rank"]) for p in manifest["plans"]], "census order")
    require([p["census_order"] for p in manifest["plans"]] == list(range(1, 434)), "ordinals")
    require([p["frozen_rank"] for p in manifest["plans"]]
            == sorted(p["frozen_rank"] for p in manifest["plans"]), "frozen rank order")
    require({p["case_id"]: p["planning_disposition"] for p in manifest["plans"]
             if p["planning_disposition"] != CONSTRUCTIBLE} == {
        "matplotlib::1": "PREPARATION_PLAN_BLOCKED_SETUP_REPRESENTATION",
        "matplotlib::8": "PREPARATION_PLAN_BLOCKED_ORACLE_REPRESENTATION"}, "blocker drift")
    for p in manifest["plans"]:
        require(identity({k: v for k, v in p.items() if k != "plan_sha256"})
                == p["plan_sha256"], "plan identity")
    return descriptor, manifest


def validate_manifest(manifest):
    _, expected = load_inputs()
    require(canonical(manifest) == canonical(expected), "manifest/order/recipe mutation")


def select(manifest, *, ordinal, case_id, plan_sha):
    require(type(ordinal) is int and 1 <= ordinal <= len(manifest["plans"]), "wrong ordinal")
    p = manifest["plans"][ordinal - 1]
    require((p["census_order"], p["case_id"], p["plan_sha256"])
            == (ordinal, case_id, plan_sha), "wrong ordinal/case/plan SHA")
    require(identity({k: v for k, v in p.items() if k != "plan_sha256"}) == plan_sha,
            "hidden plan/recipe mutation")
    require(p["planning_disposition"] == CONSTRUCTIBLE and not p["blockers"],
            "blocked case dispatch")
    return copy.deepcopy(p)


def engine_recipe(plan):
    """Field projection only: accepted recipe bytes remain unchanged and bound."""
    r = plan["recipe_candidate"]
    base = r["base_runtime"]
    q = r["requirements"]
    # future_argv is an accepted inert annotation. Shared argv parsing consumes
    # the unchanged source text; its existing ledger hashes exclude annotation.
    actions = [{k: copy.deepcopy(v) for k, v in a.items() if k != "future_argv"}
               for a in r["setup_actions"]]
    projected = {
        "schema": "V6_SHARED_ENGINE_RECIPE_BINDING_CANDIDATE_V1",
        "canonical_case_id": plan["case_id"], "census_order": plan["census_order"],
        "frozen_rank": plan["frozen_rank"], "accepted_plan_sha256": plan["plan_sha256"],
        "accepted_recipe_sha256": identity(r),
        "python_declared_version": r["python_declared_version"],
        "python_observed_version": base["observed_python_version"],
        "base_image_reference": base["image_source"] + "@" + base["immutable_digest"],
        "base_image_digest": base["immutable_digest"],
        "python_executable_sha256": base["python_executable_sha256"],
        "runtime_platform": r["runtime_platform"], "environment_mode_v2": r["environment_mode_v2"],
        "buggy_source_sha": plan["source_variants"][0]["commit_oid"],
        "fixed_source_sha": plan["source_variants"][1]["commit_oid"],
        "requirements_raw_sha256": q["raw_sha256"],
        "requirements_normalized_sha256": q["normalized_sha256"],
        "dependency_input_sha256": q["dependency_input_sha256"],
        "self_reference_ledger_sha256": q["self_reference_ledger_sha256"],
        "setup_sha256": r["setup_sha256"], "setup_actions": actions,
        "setup_action_ledger_sha256": r["setup_action_ledger_sha256"],
        "future_network_build_policy": r["future_network_build_policy"],
        "future_network_execution_policy": r["future_network_execution_policy"],
        # This legacy engine field binds the whole accepted preparation plan,
        # not a six-slot oracle execution plan, which remains unauthorized.
        "execution_plan_sha256": plan["plan_sha256"],
        "screening_runtime_v1_sha256": shared.FROZEN_SHA256["SCREENING_RUNTIME_V1.md"],
    }
    require(identity(actions) == r["setup_action_ledger_sha256"], "setup ledger drift")
    for accepted, action in zip(r["setup_actions"], actions):
        require(shared.action_argv(action, source_present=r["environment_mode_v2"]
                                   == "REVISION_SPECIFIC_BUILD_REQUIRED")
                == accepted["future_argv"], "setup normalization/semantics drift")
    return projected


def embedded_inputs(manifest, plan):
    r = plan["recipe_candidate"]
    def metadata(index):
        row = manifest["metadata_inputs"][plan["input_paths"][index]]
        raw = base64.b64decode(row["bytes_b64"], validate=True) if row["present"] else None
        require((sha(raw) if raw is not None else "ABSENT") == row["sha256"], "raw input SHA")
        return raw
    def derived(key):
        encoded = r["requirements"][key]
        return base64.b64decode(encoded, validate=True) if encoded is not None else None
    values = {"raw_requirements": metadata(4), "setup_input": metadata(3),
              "normalized_requirements": derived("normalized_bytes_b64"),
              "dependency_input": derived("dependency_bytes_b64")}
    shared.verify_inputs(engine_recipe(plan), values["raw_requirements"],
                         values["normalized_requirements"], values["dependency_input"],
                         r["requirements"]["self_reference_ledger"], values["setup_input"])
    return values


def needs_build_network(plan):
    encoded = plan["recipe_candidate"]["requirements"]["dependency_bytes_b64"]
    dependency = base64.b64decode(encoded, validate=True) if encoded is not None else b""
    declared = any(line.strip() and not line.lstrip().startswith(b"#") for line in dependency.splitlines())
    return bool(declared or any(a["requires_network"] for a in plan["recipe_candidate"]["setup_actions"]))


def work_item(plan, variant):
    r = plan["recipe_candidate"]
    mode = r["environment_mode_v2"]
    labels = ["SOURCE_INDEPENDENT"] if mode == "SOURCE_INDEPENDENT_ENVIRONMENT" else ["BUGGY", "FIXED"]
    require(variant in labels, "wrong variant applicability")
    source = None if variant == "SOURCE_INDEPENDENT" else next(
        x for x in plan["source_variants"] if x["label"] == variant)
    recipe = engine_recipe(plan)
    bound = {
        "schema": "V6_BASE_PREPARATION_ATTEMPT_IDENTITY_V1",
        "current_descriptor": {"path": CURRENT, "sha256": CURRENT_SHA},
        "preparation_manifest": {"path": MANIFEST, "sha256": MANIFEST_SHA},
        "case_id": plan["case_id"], "census_order": plan["census_order"],
        "frozen_rank": plan["frozen_rank"], "plan_sha256": plan["plan_sha256"],
        "environment_mode": mode, "variant": variant,
        "source_revision_sha": source["commit_oid"] if source else "ABSENT",
        "source_tree_metadata_sha256": source["source_export_planning"]["tree_metadata_sha256"] if source else "ABSENT",
        "source_mirror": plan["source_repository"]["mirror_path"] if source else "ABSENT",
        "recipe_sha256": identity(r), "engine_recipe_sha256": shared.recipe_hash(recipe),
        "input_bindings": dict(zip(plan["input_paths"], plan["input_bindings"])),
        "derived_dependency_sha256": r["requirements"]["dependency_input_sha256"],
        "base_runtime_sha256": identity(r["base_runtime"]),
        "base_image_reference": recipe["base_image_reference"],
        "python_declared_version": r["python_declared_version"],
        "protected_manifest_sha256": r["protected_manifest"]["manifest_sha256"],
        "variant_applicability": labels,
        "build_network_required": needs_build_network(plan),
    }
    return {**bound, "base_attempt_id": "v6-prep-base-" + identity(bound)}


def derive_population(manifest):
    validate_manifest(manifest)
    items, blocked = [], []
    for p in manifest["plans"]:
        if p["planning_disposition"] != CONSTRUCTIBLE:
            blocked.append({k: p[k] for k in ("case_id", "census_order", "frozen_rank", "plan_sha256", "planning_disposition")})
            continue
        p = select(manifest, ordinal=p["census_order"], case_id=p["case_id"], plan_sha=p["plan_sha256"])
        embedded_inputs(manifest, p)
        mode = p["recipe_candidate"]["environment_mode_v2"]
        labels = ["SOURCE_INDEPENDENT"] if mode == "SOURCE_INDEPENDENT_ENVIRONMENT" else ["BUGGY", "FIXED"]
        for label in labels:
            items.append(work_item(p, label))
    require(len({x["base_attempt_id"] for x in items}) == len(items), "duplicate work item")
    return {"schema": "V6_PREPARATION_WORK_ITEMS_CANDIDATE_V1", "candidate_only": True,
            "runtime_authority": False, "manifest_sha256": MANIFEST_SHA,
            "counts": {**dict(Counter(x["variant"] for x in items)),
                       "dispatchable_cases": len(manifest["plans"]) - len(blocked),
                       "blocked_cases": len(blocked), "total_base_attempts": len(items)},
            "items": items, "blocked": blocked}


def validate_population(manifest, population):
    require(canonical(population) == canonical(derive_population(manifest)),
            "population duplicate/order/identity drift")


def input_paths(item):
    return {key: f"inputs/{item['base_attempt_id']}/{name}" for key, name in (
        ("raw_requirements", "requirements.raw"), ("normalized_requirements", "requirements.normalized"),
        ("dependency_input", "requirements.dependencies"), ("setup_input", "setup.raw"))}


def engine_call_proposal(manifest, item, *, snapshot=None):
    """Build a future shared-engine call, never create input/attempt directories."""
    p = select(manifest, ordinal=item["census_order"], case_id=item["case_id"], plan_sha=item["plan_sha256"])
    require(canonical(item) == canonical(work_item(p, item["variant"])), "work item binding drift")
    values = embedded_inputs(manifest, p)
    paths = {k: v for k, v in input_paths(item).items() if values[k] is not None}
    source_present = item["variant"] != "SOURCE_INDEPENDENT"
    if source_present:
        require(isinstance(snapshot, dict) and set(snapshot) == {"sha256", "source_revision_sha", "source"},
                "explicit snapshot observation required")
        require(snapshot["source_revision_sha"] == item["source_revision_sha"]
                and isinstance(snapshot["sha256"], str) and bool(shared.HEX64.fullmatch(snapshot["sha256"]))
                and snapshot["source"] == f"snapshots/{item['base_attempt_id']}", "wrong snapshot/revision")
        revisions = [{"label": item["variant"], "sha": snapshot["sha256"],
                      "source": snapshot["source"], "source_revision_sha": item["source_revision_sha"]}]
    else:
        require(snapshot is None, "source-independent snapshot refused")
        revisions = [{"label": "SOURCE_INDEPENDENT", "sha": "ABSENT"}]
    recipe = engine_recipe(p)
    network_required = needs_build_network(p)
    fixture = {"recipe": recipe, "build_recipe_sha256": shared.recipe_hash(recipe),
               **paths, "self_reference_ledger": p["recipe_candidate"]["requirements"]["self_reference_ledger"],
               "revision_label": item["variant"], "revisions": revisions, "network_build": network_required}
    definition = shared.build_definition(recipe, source_present=source_present,
                                         dependency_present=values["dependency_input"] is not None)
    return {"schema": "V6_SHARED_ENGINE_CALL_PROPOSAL_V1", "candidate_only": True,
            "entrypoint": "evaluation.downstream_benchmark.screening.materializer._materialize_checked",
            "fixture": fixture, "input_root": str(OUTPUT_ROOT),
            "output": str(OUTPUT_ROOT / "attempts" / item["base_attempt_id"]),
            "synthetic_only": False, "single_identity": True,
            "dockerfile_sha256": sha(definition), "network_required": network_required,
            "execution_network": "NONE", "attempt_consumed": False}

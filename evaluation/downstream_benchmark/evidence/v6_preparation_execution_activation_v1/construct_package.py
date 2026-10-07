"""Construct three review-only data artifacts; no runtime operations."""
import json
from pathlib import Path

from evaluation.downstream_benchmark.evidence.v6_preparation_execution_activation_v1 import (
    adapter_candidate as a, controller_candidate as c,
)

E = Path(__file__).resolve().parent


def ref(path):
    return {"path": str(path.relative_to(a.ROOT)), "sha256": a.sha(path.read_bytes())}


def save(name, value):
    (E / name).write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def construct():
    _, manifest = a.load_inputs()
    population = a.derive_population(manifest)
    save("work_items_candidate.json", population)
    ledger = c.ledger_template(population)
    save("ledger_candidate.json", ledger)
    code = {name: ref(E / name) for name in ("adapter_candidate.py", "controller_candidate.py")}
    mechanics = {name: ref(a.B / name) for name in (
        "screening/materializer.py", "screening/materialize_expansion_block_02_batch.py",
        "screening/build_recipes.py", "screening/block_03_gitlink_source_export.py",
        "ENVIRONMENT_MATERIALIZER_V1.md", "MATERIALIZATION_GATE_V1.md",
        "ENVIRONMENT_BUILD_SPEC_V1.md", "SOURCE_SNAPSHOT_SYMLINK_V2.md", "DISTRIBUTION_PROBE_V2.md")}
    common = {
        "entry_current_descriptor": {"path": a.CURRENT, "sha256": a.CURRENT_SHA},
        "accepted_manifest": {"path": a.MANIFEST, "sha256": a.MANIFEST_SHA},
        "accepted_plan_closure": {"path": a.CLOSURE, "sha256": a.CLOSURE_SHA},
        "ordered_work_items": ref(E / "work_items_candidate.json"),
        "population_semantic_sha256": a.identity(population), "population_counts": population["counts"],
        "runtime_input_binding_implementation": code,
        "implementation_semantic_sha256": a.identity(code),
        "once_only_ledger": ref(E / "ledger_candidate.json"), "shared_mechanics": mechanics,
        "persistent_work_root": str(a.WORK_ROOT), "proposed_v6_output_root": str(a.OUTPUT_ROOT),
        "no_retry_semantics": "One durable claim and terminal per stable base attempt; no overwrite or automatic retry",
        "runtime_policy": c.ROUTE_POLICY,
    }
    records = {}
    scopes = {
        "ENVIRONMENT_MATERIALIZATION": {
            "population": "Exactly the 641 bound base work items; two frozen blockers cannot dispatch",
            "operations": ["Persist exact raw/derived inputs", "420 exact revision-specific source snapshots using shared V2 mechanics",
                           "No subject source in 221 source-independent image contexts", "Shared source/context verification"],
            "source_revision_policy": "Exact manifest mirror and full commit; no Git history/patch/metadata leakage; no acquisition; no test injection during image snapshot export",
        },
        "IMAGE_BUILD": {
            "population": "At most one shared-engine image-build opportunity per bound work item, maximum 641; prebuild blocking may yield fewer Docker build calls",
            "entrypoint": "screening.materializer._materialize_checked(single_identity=True, synthetic_only=False)",
            "frozen_recipe": "Exact source recipe SHA plus projected engine-input SHA and derived Dockerfile SHA; no input/command repair",
            "base_runtime": "Seven exact immutable linux/amd64 Python references and executable identities from manifest; verify locally; absent base BLOCKS; no pull authority",
            "probes": "Shared no-network/read-only Python and installed-distribution observations; no subject import/test/oracle",
        },
        "BUILD_NETWORK": {
            "policy": a.NETWORK_POLICY,
            "exact_network_work_item_ids": [x["base_attempt_id"] for x in population["items"] if x["build_network_required"]],
            "network_required_work_items": sum(x["build_network_required"] for x in population["items"]),
            "network_none_work_items": sum(not x["build_network_required"] for x in population["items"]),
            "network_scope_derivation": "Substantive non-comment frozen dependency lines or frozen setup action requires_network=true; empty/comment-only dependency files alone confer no permission; no undeclared setup egress",
            "allowed_candidate_origins": ["https://pypi.org/simple/", "https://files.pythonhosted.org/"],
            "origin_status": "CANDIDATE_ONLY default package-source proposal; verify existing frozen-base pip configuration matches, otherwise BLOCK for separate Human-PI exact-source decision; do not alter sources",
            "literal_dependency_scope": "Only exact derived dependency-input bytes and frozen network-requiring setup argv, in original order; transitive dependencies and build requirements declared by those exact installs, with observed provenance",
            "network_for_unlisted_source": "BLOCK; no arbitrary internet, VCS acquisition, package/version/source substitutions or undeclared setup downloads",
            "enforcement": "DENY_BY_DEFAULT_ON_SHARED_ENGINE_DEFAULT_NETWORK; external Docker-daemon/default-build-network egress restriction required because the shared boolean is not an origin allowlist",
            "required_future_evidence": ["Exact Human-PI accepted egress policy/provisioning identity", "Deny/allow probes without subject installation", "Observed immutable-base installer-source configuration",
                                         "Exact Docker argv", "Destination/request evidence with origin and package/artifact hashes", "Raw installer/build logs", "Denials and failures"],
            "registry_egress": "NONE; unavailable frozen base returns to separate Human-PI runtime acquisition authority",
            "execution_network": "NONE",
        },
        "PERSISTENT_EVIDENCE_OUTPUT": {
            "root_authority": "Existing errpilot-benchmark-work parent convention reused; this V6 child is a proposed namespace requiring explicit Human-PI acceptance",
            "root": str(a.OUTPUT_ROOT), "create_now": False,
            "required_outputs": ["Exclusive durable claim and unique terminal journal records", "Exact input and controller identities",
                                 "Dockerfile/context identity", "Source snapshot identity or explicit ABSENT", "Raw build log",
                                 "Image inspection and Python probe", "Installed-distribution observation", "Environment identity", "Failure/interruption evidence", "Network provenance and denials"],
            "paths": {"claims": "ledger/claims/<base_attempt_id>.json", "terminals": "ledger/terminals/<base_attempt_id>.json",
                      "inputs": "inputs/<base_attempt_id>/", "snapshots": "snapshots/<base_attempt_id>/",
                      "attempts": "attempts/<base_attempt_id>/"},
            "repair_boundary": "Evidence and FIXED source/context remain outside any repair workspace",
        },
    }
    for name, scope in scopes.items():
        records[name] = {"schema": "V6_SEPARATE_PREPARATION_PERMISSION_CANDIDATE_V1", "scope": name,
                         "lifecycle": "CANDIDATE_ONLY", "HUMAN_PI_ACCEPTED": "NO",
                         "runtime_authority": False, "common_binding_sha256": a.identity(common),
                         "exact_scope": scope}
    save("authority_candidates.json", {
        "schema": "V6_PREPARATION_EXECUTION_AUTHORITY_PACKAGE_CANDIDATE_V1",
        "candidate_only": True, "runtime_authority": False, "common_binding": common,
        "common_binding_sha256": a.identity(common), "separate_permissions": records,
        "source_acquisition": {"CURRENTLY_REQUIRED": "NO", "HUMAN_PI_ACCEPTED": "NO",
                               "AUTHORIZED": "NO", "missing_object_policy": "BLOCK and request separate versioned source-acquisition authority"},
        "lifecycle_gate_received": "HUMAN_PI_AUTHORIZE_V6_PREPARATION_EXECUTION",
        "gate_implies_separate_permission_acceptance": False,
        "event_3_constructed": False, "effective_current_descriptor_constructed": False,
        "future_runtime_entry_gates": [
            "Exact adapter, controller, source resolver binding, work-item population and ledger protocol HUMAN_PI_ACCEPTED/FROZEN/PERSISTED/COMMITTED",
            "Four exact independent permissions HUMAN_PI_ACCEPTED and frozen/persisted/committed",
            "Remote publication of runtime implementation and authorities, then clean committed exact local/live ref verification",
            "Provision and independently verify accepted restricted build egress and persistent output binding",
            "Local immutable base availability/probes and fresh source-object presence; absence blocks, no implicit pull/fetch",
            "Separately accepted event #3 plus successor effectivity binding, canonical compare/install authority and exact acceptance pin",
            "Revalidate full event chain/current execution flags and exact permission/implementation/population bindings",
            "Install separately reviewed real runtime entrypoint and durable exclusive/fsync ledger I/O before dispatch; this package exposes sentinel-only routes",
        ],
    })
    return population["counts"]


if __name__ == "__main__":
    print(json.dumps(construct(), sort_keys=True))

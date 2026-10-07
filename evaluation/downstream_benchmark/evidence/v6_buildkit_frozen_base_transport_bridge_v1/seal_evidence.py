"""Finalize blocked evidence, verify it, and seal repository/external manifests."""
from __future__ import annotations

import ast
import importlib.util
import subprocess
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
spec = importlib.util.spec_from_file_location("transport_sealing", OUT / "transport_bridge.py")
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)


def main():
    t.require(t.load("final_verification.json")["status"] == "PASS", "final preservation missing")
    matrix = {
        "config_mismatch": ("PASS", "focused archive config mutation"),
        "rootfs_diffID_mismatch": ("PASS", "focused rootfs mutation"),
        "layer_reorder": ("PASS", "focused archive/OCI layer-order mutations"),
        "OCI_blob_mutation": ("PASS", "focused layout blob mutation"),
        "wrong_OCI_manifest": ("PASS", "focused index manifest mutation"),
        "wrong_base_mapping": ("NOT_RUN", "production seven-base mapping gate not reached"),
        "wrong_named_context": ("NOT_RUN", "production transport integration gate not reached"),
        "extra_Dockerfile_delta": ("NOT_RUN", "production transport integration gate not reached"),
        "registry_fallback": ("NOT_RUN", "no production OCI transport rule constructed"),
        "pull_fallback": ("PASS_EXISTING_RUNTIME_GUARD", "unchanged RuntimeTests.test_network_and_no_pull_transport"),
        "wrong_scientific_base_identity": ("PASS", "focused archive scientific-base mutation"),
        "transport_identity_inserted_into_attempt_identity": ("PASS", "focused immutable population mutation"),
        "missing_local_OCI_layout": ("PASS", "focused absent-layout probe"),
        "output_parity_failure": ("NOT_RUN", "source parser failed before output; parity gate not reached"),
        "641_583_58_drift": ("PASS", "focused count/split mutation and unchanged runtime all-641 selectors"),
        "blocker_dispatch": ("PASS", "focused population mutation and unchanged runtime both-blocker selector rejection"),
        "event_3_creation": ("PASS", "focused descriptor mutation and unchanged runtime execution gate rejection"),
        "real_attempt_claim": ("PASS", "focused real-claim observation rejection and unchanged runtime default-deny dispatch"),
    }
    t.save("rejection_matrix.json", {"probes": {k: {"status": status, "evidence": evidence} for k, (status, evidence) in matrix.items()},
        "passed": 13, "not_run": 5, "failed": 0,
        "unrun_reason": "First-base hard stop forbids dependent production transport, output and egress qualification",
        "posthoc_error_recognition_is_not_a_passed_fallback_condition_guard_test": True})
    t.save("validation_results.json", {"status": t.NAMED_BLOCK, "next_gate": t.NEXT,
        "next_gate_kind": "RECOMMENDED_HUMAN_PI_REVIEW; NOT_AN_ACCEPTED_DECISION",
        "mechanics_test_status": "PASS", "tests_passed": 19,
        "first_base_archive_equivalence": "PASS", "first_base_BuildKit_consumption": "FAIL_BEFORE_RUN",
        "all_seven_base_qualification": "NOT_RUN_FIRST_BASE_HARD_GATE", "output_parity": "NOT_QUALIFIED",
        "downstream_restricted_egress": "NOT_RUN_FIRST_BASE_HARD_GATE", "enforcement_identity": "ABSENT",
        "contract_compliance": "EXCEPTION_ALIAS_FALLBACK_CONDITION_MISCLASSIFIED",
        "canonical_execution_effective": False, "real_attempts": 0, "scientific_validation": False})
    result = subprocess.run([sys.executable, str(OUT / "validate_evidence.py"), "--persist"], cwd=ROOT,
                            capture_output=True, check=False, timeout=55)
    t.durable(OUT / "evidence_verifier.stdout.txt", result.stdout)
    t.durable(OUT / "evidence_verifier.stderr.txt", result.stderr)
    t.require(result.returncode == 0, "independent verifier failed: " + result.stderr.decode())
    c, f = t.load("oci_layout_construction.json"), t.load("first_base_transport_result.json")
    archive = t.load("archive_export_inventory.json")["exports"][0]
    delta = t.load("dockerfile_transport_delta.json")
    base_table = "\n".join("| " + b["python_version"] + " | `" + b["reference"] + "` | "
        + ("Archive equivalence PASS; BuildKit source parsing FAIL" if i == 0 else "NOT_RUN first-base gate") + " |"
        for i, b in enumerate(t.load("frozen_base_authorities.json")["bases"]))
    report = f"""# Run Report — V6 BuildKit frozen-base local OCI transport bridge

Date: 2026-10-06, Europe/Budapest.

STATUS = **{t.NAMED_BLOCK}**

NEXT_GATE (recommended, not a Human-PI decision) = **{t.NEXT}**

## 1. Task summary / requested A–S results

The first frozen Engine base passed config and ordered uncompressed-tar diffID equivalence and produced a separate local OCI transport manifest. The installed Buildx/BuildKit path then rejected the requested OCI source reference before source consumption or RUN. Both the original FROM override and the alias request ended with `could not parse oci-layout reference <session-id>:@sha256:<digest>: invalid reference format`. No output image or qualified transport resulted. The required hard stop leaves all-seven qualification, output parity, restricted-egress resume and production integration incomplete.

One conditional authority exception occurred: the error classifier treated a generic `invalid reference format` as a FROM context-name rejection and invoked the alias fallback. The log actually names the OCI source-reference parser; it does not establish the permitted fallback condition. The second fixture request, exact one-token delta, failed raw logs and exception are explicitly preserved in `execution_corrections.json`. No further syntax variants or retries were executed. The classifier has been narrowed for future execution; this is not evidence that a future fallback condition has been qualified.

| Item | Observed result |
| --- | --- |
| A. Entry / lineage | `main`; local HEAD and LIVE origin/main verified at entry and final as `5c007fbfbfc5b3529105a14f87127f50e1eab6d7`. Canonical SHA `6a9028c79aa62f90db2b2d53def32ab23bffcfa3c71d2ec30d7fa64e741e3aae`, planning effective, event_count=2, PREPARATION_EXECUTION=NO. All 162 prior manifest-bound repository files and all prior external evidence remain exact. Prior blocked mechanism checked against its captured manifest-HEAD failure before RUN. |
| B. Frozen-base identity model | Original frozen registry identities remain scientific/base authorities. Engine inspect IDs, config descriptors and ordered diffIDs are recorded separately. The new OCI manifest is only an execution transport candidate. No recipe/attempt identity changed. |
| C. Engine export | One exact local `docker image save` without pull/network; archive {archive['archive_size']} bytes, SHA `{archive['archive_sha256']}`. Stored only in the accepted external qualification child. Exactly one intended image, safe archive members and unique names checked. |
| D. OCI construction / equivalence | Exact config `{c['engine_config_identity']}`, all 9 ordered rootfs diffIDs PASS. Engine's save contained gzip blobs; stdlib gzip recovered exact tar streams without filesystem unpacking or tar repacking. Config descriptor was recovered from the content-verified frozen manifest in the Engine export; Engine image Id was not mislabeled as a config digest. Local OCI manifest `{c['transport_manifest_identity']}`; 13 layout files, 935402499 bytes, linux/amd64. Actual layout hashes verified; constructor determinism tested on synthetic fixtures. |
| E. First-base result | Python 3.6.9 base archive equivalence PASS; BuildKit consumption FAIL before RUN. Exact preferred context and alias request each exit 1. No resulting Python/architecture/executable behavior qualification. |
| F. Seven-base results | Seven Engine identities revalidated and preserved. One exported/constructed; 0/7 BuildKit transports qualified. Remaining six not exported or built after the hard stop. |
| G. Production transport map | `seven_base_transport_map.json` records seven authoritative identities and the incomplete first candidate. No qualified seven-base rule, runtime-input installation or regeneration mechanism was constructed. |
| H. Dockerfile/context binding | Original fixture SHA `{delta['original_Dockerfile_sha256']}`; alias fixture SHA `{delta['execution_Dockerfile_sha256']}`. Delta replaces only the FROM source with `errpilot_frozen_base`. Neither binding mode qualified. The alias fallback condition was misclassified, as disclosed above. |
| I. Output parity | `--load` requested on both fixture solves, but parser failure prevented output. Tag lookup, image ID/layers and shared identity probes on a new output remain NOT_QUALIFIED. |
| J. Resumed proxy / egress | NOT_RUN: no proxy source/container, external network, local fixture, positive PyPI request, dependency operation, transport ARG or direct/NONE egress proof. |
| K. Enforcement identity | ABSENT; failure evidence hashes are not an enforcement receipt. |
| L. Runtime integration delta | NONE: no runtime/adapter/ledger/materializer/test source changed. No production transport or egress integration candidate was applied. |
| M. 641 / 583 / 58 | Exact rederivation and semantic population hash preserved; work item order, scientific recipes/revisions/attempt IDs unchanged. `matplotlib::1` and `matplotlib::8` remain non-dispatchable. |
| N. Repository / external evidence | All repository changes are in this new evidence directory. Exact artifact inventories are in `artifact_sha256.json` and `external_evidence_manifest.json`. External root: `{t.Q}`. Initial encoding-check observation and correction, failure logs, precleanup snapshots, final evidence and synthetic ledger fixtures are retained separately. No large archive/layout is in Git. |
| O. Cleanup | Exact observations persisted and fsynced before cleanup. Removed only the labeled builder, runtime container, owned state volume and internal network. Before/after Docker/configuration/selected-builder observations match: 57 image rows, 3 networks, 1 original container, 0 volumes. Exact BuildKit and seven frozen Python bases preserved. Archives/OCI remain qualification evidence, with no accepted production reliance. |
| P. Validation / rejection matrix | 8 bridge methods and 11 unchanged runtime/actual-filesystem methods PASS, 0 failures/errors/skips. 13/18 requested rejection classifications PASS (one uses the unchanged runtime pull guard); 5 dependent production/output classifications NOT_RUN. Ruff, AST, strict repository JSON/UTF-8, whitespace and git diff checks PASS. Independent integrity verifier receipt records its exact check count. Live source-consumption gate FAILED. |
| Q. Firewall | All required real benchmark attempts/claims/builds/dependency installs/source exports and registry pulls/resolution-request counters are 0. Source acquisition, oracle, event #3, canonical mutation, Git stage/commit/push are NO. Two synthetic build requests; zero fixture RUNs and zero output images. |
| R. Unresolved prerequisite | A demonstrated named local OCI source binding accepted by this exact installed Buildx/BuildKit frontend is missing. The observed parser error contains `<session-id>:@sha256:<transport>`; no alternate reference syntax, frontend/runtime or transport path has been verified or adopted. |
| S. Next gate | Human-PI review of the named-context block and conditional fallback exception. No scientific validation, execution effectivity or readiness recommendation is made. |

The seven frozen authorities are:

| Expected Python | Frozen scientific reference | This run |
| --- | --- | --- |
{base_table}

The first equivalence binding is:

`{f['frozen_registry_identity']}` ↔ exact config `{c['engine_config_identity']}` + exact ordered 9 diffIDs ↔ local transport `{c['transport_manifest_identity']}`.

The three identities remain separate; full ordered diffIDs and compressed/uncompressed per-layer hashes are in `oci_layout_construction.json`.

## 2. Files inspected and changed

Inspected all six prior repository package manifests and exact referenced files; prior external manifests/inventories; the canonical descriptor and pinned contract, event, manifest and recipe dependencies through `load_inputs`; accepted runtime authority and all-641 population; prior blocked logs and exact immutable BuildKit binding; seven Engine inspections; the one Engine-save archive; local OCI blobs; dedicated builder/network/container and readable host/global configuration observations; unchanged runtime and tests.

No on-disk repository AGENTS.md, `.airos/current_state.md` or `.airos/contracts/` was present. The supplied global rules and explicit Human-PI request governed this task; the pinned V6 successor contract was inspected and validated through the existing input loader. No prior repository/external evidence, tracked source, canonical descriptor or Git index was changed. All changed/new files are evidence/executor/verification files within this new namespace and its accepted external qualification child.

## 3. Commands run

Used existing `.venv/bin/python`; no dependencies installed. Executed `transport_bridge.py` phases: `entry`, `export-first`, `recover-first-encoding-check`, `create-builder`, `first-consume`, `persist-block-and-cleanup`, `finish`; then `run_validation.py`, `seal_evidence.py` and `validate_evidence.py`. `commands_run.json` preserves exact captured Git/Docker/host observation argv, results and stdout/stderr hashes. The image-save argv/archive hash/size are in `archive_export_inventory.json`; runtime/focused/lint/diff argv and raw outputs are in `test_results.json` and accompanying text files.

Both fixture builds used the exact dedicated builder, linux/amd64, network NONE, no-cache, plain progress and explicit load. No benchmark build context or source export was submitted. Read-only LIVE Git identity checks were authorized by the entry/final requirement. All large writes stayed in the accepted external qualification child.

## 4. Tests passed / failed / not run

19 methods PASS: 8 new stdlib archive/layout/firewall methods and 11 unchanged runtime/actual-target-filesystem methods, with the actual filesystem fixture setup redirected in memory to this run's synthetic child. Focused tests exercise compressed/uncompressed exact tar streams, deterministic synthetic manifests, config/diffID/order corruption, blob/manifest/layout corruption, missing layout, unsafe/duplicate/multiple-image archives, nonregeneration, strict JSON, immutable population, event #3 and real-claim rejection. Runtime tests retain exact selection, all-641 identities, no-pull/once-only guards and default-deny dispatch.

Both actual BuildKit solves FAILED at OCI reference parsing before RUN. The 7/7, output parity, proxy positives/negatives and production integration rejection suite were NOT_RUN after that hard gate. Passing synthetic/mechanics tests do not qualify the failed transport or the absent egress bridge.

## 5. Contract compliance

All real-work and scientific-identity firewalls were preserved. Cleanup was limited to objects proven absent at entry and owned by label/name/ID; global selection/configuration and frozen images are exact after cleanup. No image pull, registry, retag, dependency install, real preparation, event #3 or Git publication occurred.

Compliance exception: the alias request was invoked without establishing a FROM context-name failure, owing to an overly broad parser-error classifier. This is recorded honestly rather than described as a contract-compliant fallback. It failed before RUN/output/egress and was followed by the hard stop. The encoding-check correction also retains its initial observation: a compressed distribution hash was initially compared to an uncompressed diffID; the corrected equality uses the exact decoded tar stream. No actual required equality failure was concealed or replaced by changed bytes.

## 6. Risks and unknowns

The requested OCI source syntax remains incompatible in this observed path. No alternative syntax was tried; no successful BuildKit source consumption, Python behavior on a new output, Engine load parity or restricted egress is established. Six other OCI transports are absent. The fallback classifier correction has code inspection and lint/syntax coverage, but no successful live condition qualification.

No packet capture or Docker VM/PF internal audit was performed. Registry conclusions are bounded to the source-parser failure, retained logs, internal-only attachment, absence of a default route and loopback upstream DNS. Readable host configuration hashes and Docker snapshots match; unreadable PF internals and concurrent activity between snapshots remain unknown. Intentionally malformed JSON/symlinks in external negative ledger fixtures are test evidence and are hashed as such; strict JSON validation applies to repository evidence records.

## 7. Recommended next action

Review `first_base_transport_result.json`, the two raw parser errors and `execution_corrections.json` at `{t.NEXT}`. Resolve the exact frontend/source-reference prerequisite within an explicit bounded follow-up, then re-establish the first-base gate before all-seven qualification, output parity or egress resume. This report recommends review, not an architecture or readiness decision. Real preparation remains unauthorized.
"""
    t.durable(OUT / "RUN_REPORT.md", report.encode())
    from evaluation.downstream_benchmark.screening import v6_preparation_runtime as runtime
    python_files = sorted(OUT.glob("*.py")) + [ROOT / rel for rel in runtime.IMPLEMENTATION]
    _, rec = t.command("final_Ruff", [str(ROOT / ".venv/bin/ruff"), "check", *map(str, python_files)])
    t.command("final_git_diff_check", ["git", "diff", "--check"])
    for path in python_files:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for path in OUT.iterdir():
        if path.is_file():
            path.read_text(encoding="utf-8", errors="strict")
        if path.suffix == ".json":
            t.strict_json(path.read_bytes())
    t.save("final_static_checks.json", {"Ruff": rec, "AST_files": len(python_files),
        "strict_JSON_UTF8": "PASS", "git_diff_check": "PASS", "repository_all_file_UTF8": "PASS"})
    final = t.Q / "final"
    t.require(not final.exists(), "no final evidence overwrite")
    final.mkdir()
    copies = {}
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.name not in {"artifact_sha256.json", "external_evidence_manifest.json"}:
            raw = path.read_bytes()
            t.durable(final / path.name, raw)
            copies[path.name] = {"bytes": len(raw), "sha256": t.sha(raw)}
    t.durable(final / "artifact_sha256.json", t.encoded({"artifacts": copies, "self_hash_excluded": True,
        "namespace": "QUALIFICATION_ONLY_NOT_ATTEMPT", "status": t.NAMED_BLOCK}))
    entire = t.prior.inventory(t.Q)
    t.save("external_evidence_manifest.json", {"root": str(t.Q), "artifact_inventory": entire,
        "file_count": len(entire), "all_bytes_verified": True, "prior_external_unchanged": True,
        "benchmark_attempt_id": None, "large_archive_and_OCI_qualification_only": True,
        "runtime_input_namespace_installed": False,
        "precleanup_manifest_sha256": t.file_sha(t.Q / "precleanup_evidence_manifest.json"),
        "final_manifest_sha256": t.file_sha(final / "artifact_sha256.json")})
    artifacts = {str(path.relative_to(ROOT)): t.file_sha(path) for path in sorted(OUT.iterdir())
                 if path.is_file() and path.name != "artifact_sha256.json"}
    t.save("artifact_sha256.json", {"artifacts": artifacts, "file_count_including_manifest": len(artifacts) + 1,
        "self_hash_excluded": True, "prior_files_preserved": 162, "status": t.NAMED_BLOCK,
        "real_attempts": 0, "next_gate": t.NEXT, "contract_compliance_exception_disclosed": True})
    print(t.encoded({"status": t.NAMED_BLOCK, "repository_files": len(artifacts) + 1,
        "external_file_symlink_artifacts": len(entire), "next_gate": t.NEXT}).decode(), flush=True)


if __name__ == "__main__":
    main()

"""Prepare the bounded BLOCK report, run local validation, and seal all new evidence."""
from __future__ import annotations

import datetime
import json
import subprocess
from pathlib import Path

from . import corrected_production_provider_candidate as p

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / "v6_preparation_execution_production_runtime_installation_resume_v1"


def write(name, value):
    (HERE / name).write_bytes(p.pretty(value))


def main():
    provider_sha = p.a.sha((HERE / "corrected_production_provider_candidate.py").read_bytes())
    old_sha = "d466c9310d22754c0c3c9744764bcc402aef988195da7f7aea45b9700eb1de0a"
    plan = p.exact_json(OLD / "installation_plan.json")
    old_candidate = p.exact_json(OLD / "production_runtime_installation_candidate.json")
    write("supersession_dependency_report.json", {
        "schema": "V6_PRODUCTION_RUNTIME_IMAGE_IDENTITY_BRIDGE_SUPERSESSION_DEPENDENCIES_V1",
        "candidate_only": True, "HUMAN_PI_ACCEPTED": "NO", "runtime_effective": "NO",
        "old_accepted_provider_sha256": old_sha, "corrected_proposed_provider_sha256": provider_sha,
        "affected_installation_plan": {"path": str(OLD / "installation_plan.json"),
                                      "sha256": p.a.sha((OLD / "installation_plan.json").read_bytes()),
                                      "source_pin_field": "exact_copy_sources.provider", "source_pin": plan["exact_copy_sources"]["provider"]},
        "affected_installation_candidate": {"path": str(OLD / "production_runtime_installation_candidate.json"),
                                           "sha256": p.a.sha((OLD / "production_runtime_installation_candidate.json").read_bytes()),
                                           "source_binding_fields": ["provider", "package_bindings.production_provider_candidate.py"],
                                           "provider_binding": old_candidate["provider"],
                                           "package_binding": old_candidate["package_bindings"]["production_provider_candidate.py"]},
        "accepted_candidate_closure_sha256": "a764800f1a2bb8745ded16dca8452b4ca50e368dcefa630ee7784776103870f9",
        "original_package_manifest_sha256": "99588f947554c2f9d25c2884d0ceba7b939b4d04ccb4a857bc7a21070c8f3ce5",
        "prospective_installation_effectivity_binding": {
            "required_later_versioned_candidate_and_plan": True,
            "provider_candidate_source": {"path": str(HERE / "corrected_production_provider_candidate.py"), "sha256": provider_sha},
            "installed_provider_target": plan["future_targets"]["provider"],
            "prospective_provider_source_sha256": provider_sha,
            "prospective_plan_candidate_authority_effectivity_acceptance_pin_sha256": None,
            "not_constructed_not_accepted_not_effective": True,
            "dependencies": ["Human-PI acceptance of exact corrected bytes and qualified bounded evidence",
                             "Resolve/adjudicate fresh topology and full Docker inspect drift without this transaction changing the contract",
                             "Separately authorize versioned installation candidate/plan supersession and exact source/package bindings",
                             "Separately authorize exact installation authority, installed source SHA, fresh accepted topology",
                             "Separately create effectivity payload and independent exact Human-PI acceptance pin",
                             "Separately authorize any real preparation attempt"]},
        "unchanged_receipt_contract": old_candidate["receipt_authority_contract"],
        "receipt_fields_and_canonical_serialization_unchanged": True,
        "ledger_claim_terminal_once_only_semantics_unchanged": True,
        "scientific_functions_recipes_work_population_network_commands_unchanged": True,
        "future_receipt_provider_source_value": "Would reflect separately accepted new source/effectivity binding; no receipt exists in this transaction",
        "controller_sha256_unchanged": old_candidate["controller"]["sha256"],
        "old_plan_authorizes_new_provider": False, "accepted_or_effective_replacement_plan_created": False,
        "no_implicit_acceptance_or_source_promotion": True})
    drift_ids = ["fe36c6b84e7ab5a74fbfe441848c95fa4fab65fe5db8cfba3477d0fdb0960e73",
                 "3cb528138771884a52fa9bd01e5d5458ca4ffbd41c949282328d08b2dc0286bf"]
    responses = []
    for ident, pid in zip(drift_ids, [1314, 807], strict=True):
        responses.append({"source": "read-only local Docker Engine GET via curl Unix socket; tool output",
                          "argv": ["curl", "--silent", "--show-error", "--unix-socket",
                                   "/Users/wuyangchenxi/.docker/run/docker.sock", "http://localhost/exec/" + ident + "/json"],
                          "response": {"ID": ident, "Running": True, "ExitCode": None,
                                       "ProcessConfig": {"tty": False, "entrypoint": "buildctl", "arguments": ["dial-stdio"], "privileged": False},
                                       "OpenStdin": True, "OpenStderr": True, "OpenStdout": True, "CanRemove": False,
                                       "ContainerID": "165fb59b3d43bd73a48072e6c283d338e9140b700f3e3f3bd0b3bc3602b06402", "DetachKeys": "", "Pid": pid}})
    write("docker_exec_drift_details.json", {
        "schema": "V6_IMAGE_IDENTITY_BRIDGE_DOCKER_EXEC_DRIFT_V1", "status": "OBSERVED_UNRESOLVED",
        "new_exec_id": drift_ids[0], "previous_retained_exec_id": drift_ids[1], "metadata": responses,
        "origin": "NOT_ESTABLISHED: this task's logged commands contain no buildctl dial-stdio or Buildx invocation",
        "socket_drift_causality": "NOT_ESTABLISHED; both observations are preserved without causal assertion",
        "stopped_or_removed": False})
    write("construction_revision_and_failure_history.json", {
        "schema": "V6_IMAGE_IDENTITY_BRIDGE_CONSTRUCTION_HISTORY_V1",
        "final_provider_sha256": provider_sha,
        "events": [
            {"status": "READ_ONLY_FAILURE", "command": "system python3 inline Ledger-state/import check", "reason": "ModuleNotFoundError: jsonschema", "resolution": "Used existing .venv; no dependency install"},
            {"status": "PARTIAL_SYNTHETIC_RUN_FAILED", "namespace": str(HERE / "qualification/synthetic_identity_v1"), "reason": "missing_config_bytes reached JSONDecodeError before explicit rejection", "resolution": "Added nonempty manifest/config byte gate within pure identity helper; failed fixtures retained"},
            {"status": "PASS_AFFECTED_PURE_SCOPE", "namespace": "qualification/synthetic_identity_v1/run_2", "checks": 3, "rejections": 48},
            {"status": "EVIDENCE_VALIDATOR_FAILURE", "reason": "New JSON evidence from construction was valid but not canonically key-sorted", "resolution": "Normalized only unsealed new correction JSON to accepted canonical/pretty UTF-8 LF representation; original evidence unchanged"},
            {"status": "READ_ONLY_FAILURE", "reason": "Relative path rejected by existing absolute persistent path guard in local diff diagnostic", "resolution": "Used absolute path; original guard unchanged"},
            {"status": "PRESERVATION_BLOCKED", "reason": "Full Docker inspect comparison found new ExecIDs; first raw after snapshot and commands retained under preservation_attempt_1"},
            {"status": "PASS_AFFECTED_PURE_SCOPE", "namespace": "qualification/synthetic_identity_v1/run_3", "checks": 3, "rejections": 48},
            {"status": "BOUNDED_IDENTITY_HELPER_REFINEMENT", "reason": "Independently verify running container ImageManifestDescriptor and platform against selected frozen content, in addition to local selected image view"},
            {"status": "PASS_AFFECTED_PURE_SCOPE", "namespace": "qualification/synthetic_identity_v1/run_4", "checks": 3, "rejections": 52},
            {"status": "BLOCKED", "reason": "Final fresh candidate observation retains exact daemon_socket_observation contradiction; full inspect retains ExecIDs drift"}],
        "no_original_or_frozen_qualification_module_patch_or_monkeypatch": True,
        "earlier_observation_and_preservation_evidence_retained": True})
    provenance = p.exact_json(HERE / "config_digest_provenance.json")
    raw_images = p.exact_json(HERE / "live_image_identity_observations.json")
    provenance["mapping"]["BuildKit"]["OCI_INDEX_DIGEST"] = raw_images["engine_store_inspect"]["Descriptor"]["digest"]
    provenance["mapping"]["BuildKit"]["PLATFORM_ENGINE_INSPECT_ID"] = raw_images["buildkit_platform_inspect"]["Id"]
    provenance["mapping"]["BuildKit"]["OCI_PLATFORM_MANIFEST_DIGEST"] = raw_images["buildkit_platform_inspect"]["Descriptor"]["digest"]
    provenance["mapping"]["proxy"]["PLATFORM_ENGINE_INSPECT_ID"] = raw_images["proxy_platform_inspect"]["Id"]
    write("config_digest_provenance.json", provenance)
    commands = p.exact_json(HERE / "commands_run.json")
    commands["new_commands"] = [
        {"argv": [".venv/bin/python", "-B", str(HERE / "construct_provider_candidate.py")], "result": "constructed new candidate, subsequently revised only within identity helper"},
        {"argv": [".venv/bin/python", "-B", "-m", "evaluation.downstream_benchmark.evidence.v6_production_runtime_image_identity_compatibility_bridge_v1.qualify_bridge_candidate"], "result": "initial missing-config rejection failure; retained"},
        *[{"argv": [".venv/bin/python", "-B", "-m", "evaluation.downstream_benchmark.evidence.v6_production_runtime_image_identity_compatibility_bridge_v1.qualify_bridge_candidate", name], "result": "PASS_AFFECTED_PURE_SCOPE"} for name in ("run_2", "run_3", "run_4")],
        {"argv": [".venv/bin/python", "-B", "-m", "evaluation.downstream_benchmark.evidence.v6_production_runtime_image_identity_compatibility_bridge_v1.observe_corrected_topology"], "result": "BLOCKED exact socket drift; earlier evidence retained"},
        {"argv": [".venv/bin/python", "-B", "-m", "evaluation.downstream_benchmark.evidence.v6_production_runtime_image_identity_compatibility_bridge_v1.observe_corrected_topology", "run_2"], "result": "BLOCKED on final candidate bytes; raw argv/stdout/stderr hashes in fresh_live_commands.json"},
        {"argv": [".venv/bin/python", "-B", "-m", "evaluation.downstream_benchmark.evidence.v6_production_runtime_image_identity_compatibility_bridge_v1.verify_preservation"], "runs": 3, "result": "initial fail-closed assertion, then explicit BLOCKED drift evidence with all tracked/index/ledger and lifecycle state preserved"},
        {"command": "Inline local SHA/AST/patch generation, copying only new attempt evidence and sorting only unsealed new JSON", "write_scope": str(HERE)},
        {"argv": [".venv/bin/python", "-B", "-m", "evaluation.downstream_benchmark.evidence.v6_production_runtime_image_identity_compatibility_bridge_v1.validate_bridge_candidate"], "result": "initial canonical serialization failure then evidence/static qualification passes with construction BLOCKED"},
        {"argv": [".venv/bin/ruff", "check", "--no-cache", str(HERE)], "result": "PASS on all final new Python"}]
    commands["fresh_live_read_only_inspections"] = p.exact_json(HERE / "fresh_live_commands.json")
    commands["after_preservation_read_only_commands"] = p.exact_json(HERE / "preservation_commands.json")
    commands["exec_metadata_read_only_GETs"] = responses
    commands["tools_write_scope"] = str(HERE)
    commands["earlier_raw_command_evidence"] = ["live_raw", "live_observation_attempt_1/fresh_live_commands.json", "preservation_attempt_1/preservation_commands.json", "preservation_attempt_2/preservation_commands.json"]
    write("commands_run.json", commands)
    ruff_argv = [str(p.a.ROOT / ".venv/bin/ruff"), "check", "--no-cache", str(HERE)]
    ruff = subprocess.run(ruff_argv, cwd=p.a.ROOT, capture_output=True, check=False)
    write("ruff_results.json", {"argv": ruff_argv, "returncode": ruff.returncode,
                               "stdout": ruff.stdout.decode(), "stderr": ruff.stderr.decode(),
                               "stdout_sha256": p.a.sha(ruff.stdout), "stderr_sha256": p.a.sha(ruff.stderr),
                               "status": "PASS" if ruff.returncode == 0 else "FAIL"})
    assert ruff.returncode == 0
    validation_argv = [str(p.a.ROOT / ".venv/bin/python"), "-B", "-m",
                       "evaluation.downstream_benchmark.evidence.v6_production_runtime_image_identity_compatibility_bridge_v1.validate_bridge_candidate"]
    checked = subprocess.run(validation_argv, cwd=p.a.ROOT, capture_output=True, check=False)
    write("validation_command_result.json", {"argv": validation_argv, "returncode": checked.returncode,
                                             "stdout": checked.stdout.decode(), "stderr": checked.stderr.decode()})
    assert checked.returncode == 0, checked.stderr.decode()
    validation = p.exact_json(HERE / "validation_results.json")
    validation["Ruff"] = "PASS"
    validation["next_gate"] = None
    validation["recommendation"] = "Human-PI adjudicate the preserved live topology/ExecIDs drift and unresolved E2E coverage under a separately bounded transaction; no source promotion or installation"
    write("validation_results.json", validation)
    topology = p.exact_json(HERE / "topology_comparison.json")
    report = f'''# Run Report — V6 Production Runtime Image Identity Compatibility Bridge V1

STATUS: **BLOCKED**. Candidate construction and affected pure requalification are complete; exact live topology and complete Docker inspect preservation gates do not pass. No Human-PI review-ready, acceptance, installation, effectivity or scientific qualification claim is made. NEXT_GATE is unset.

## 1. Task summary

Constructed a versioned non-effective provider correction for Engine store ID versus OCI config digest. Fresh independently verified local content provenance passed for both images. The corrected candidate keeps the accepted observation schema and field semantics, and independently validates Engine store ID, running container platform manifest, selected Engine platform view, retained content hashes, OCI config and RootFS. Production authority firewalls are unchanged.

The sole exact topology field difference is `/daemon_socket_observation`: the current raw `/proc/net/unix` contains two additional records (socket addresses `00000000319c26ff` / `000000002eda958e`, inodes `18643` / `14575`). It is genuine observed runtime socket drift; no representation normalization or expected-byte synthesis was applied. Exact comparator and old evidence remain intact.

## 2. Files changed

All writes are new files beneath `{HERE}`. No tracked file, index byte, accepted/frozen source, original evidence package, previous qualification namespace, OCI layout or production target changed. The new pure qualification namespace is `{HERE / 'qualification/synthetic_identity_v1'}`; no external qualification child was necessary. Partial and successful rounds are retained.

Core outputs: corrected_production_provider_candidate.py, provider_identity_correction.patch, source_semantic_delta.json, human_pi_decision.json, entry_verification.json, accepted_baseline_binding.json, live_image_identity_observations.json, config_digest_provenance.json, corrected_topology_observation.json, topology_comparison.json, synthetic_qualification_results.json, rejection_matrix.json, preservation_verification.json, validate_bridge_candidate.py, validation_results.json, commands_run.json, supersession_dependency_report.json, RUN_REPORT.md and artifact_sha256.json. Additional raw outputs, fixtures, scripts, snapshots, failure/revision history and Ruff results are included in the complete path/size/SHA seal.

## 3. Commands run

Git read-only HEAD/branch/status/diffs/ls-files and live `git ls-remote origin refs/heads/main`; streaming exact local SHA and package checks; Docker inspect/image inspect with `--platform=linux/amd64`, network/volume/image/container inventories; read-only native worker metadata, binary hashes, routes/socket bytes and proxy source; two read-only local Docker Engine exec-metadata GETs. `.venv/bin/python -B` constructed/requalified/observed/validated the new candidate. `.venv/bin/ruff check --no-cache` passed. Exact primary argv, raw outputs, hashes and earlier failures are retained in commands_run.json and the linked raw command records. No dependency installation occurred.

## 4. Tests passed/failed

- Entry and all frozen exact pins: PASS; original 26-file manifest verified (25 listed payload files plus manifest); all 512 sealed provisioning evidence payload files verified.
- Independent Engine/index/platform-manifest/config/RootFS lineage: PASS for both running images; no acquisition/export.
- Final candidate source parses, AST/function equivalence and source delta gate: PASS; Ruff: PASS.
- 3 positive pure checks: PASS. 52 negative checks: PASS_REJECTED using actual corrected candidate functions, including independent Engine/config errors, selected and running platform/manifest errors, swapped identities, stale topology, daemon external attachment, internal network/worker changes, policy/source changes, enforcement comparison and missing/malformed fields.
- Full corrected controller/provider E2E and full A–X: NOT_RUN. Exact original Authority.synthetic source-location guard rejects the new candidate path. No guard patch, `object.__new__`, global rebinding or monkeypatch bypass was used. Receipt/claim/preclaim E2E-dependent coverage remains NOT_RUN; unchanged AST is separate evidence, not qualification.
- First synthetic round failed on missing config bytes before an explicit JSON rejection; the candidate-only image helper was tightened and later rounds passed. Early system Python lacked jsonschema; existing .venv was used. Initial new-evidence key sorting and a relative-path diagnostic were corrected only within the new namespace. Failure evidence is retained.
- Final live exact-byte topology gate: BLOCKED (LIVE_TOPOLOGY_DRIFT).
- Complete Docker inspect byte comparison: BLOCKED_DOCKER_INSPECT_DRIFT (`ExecIDs` changed). Container identities, configurations except diagnostic ExecIDs, lifecycle State, network/volume inspect and exact image identities/tags/counts remain equal. The complete comparator still includes ExecIDs and is not weakened.

## 5. Contract compliance

Transaction remains CANDIDATE_CONSTRUCTION_ONLY. Repository root writes are confined to the new correction namespace. No original provider/controller mutation, accepted contract mutation, production installation, runtime effectivity, installed controller invocation, real receipt, real claim/terminal, build/solve/pull/import/export, dependency install, topology lifecycle/network mutation, cleanup, stage/commit/push or automatic source promotion occurred. Both provisioned containers and both observed dial-stdio execs were retained. No scientific function, recipe, population, command compiler, receipt/claim/terminal or source-location guard changed.

## 6. Risks and unknowns

The exact accepted raw socket observation is not stable against the observed added connections. This transaction has no authority to alter that contract, remove the connections, rewrite old evidence or bind the new hash as accepted. Full inspect additionally found a newly retained running `buildctl dial-stdio` exec `fe36c6b84e7ab5a74fbfe441848c95fa4fab65fe5db8cfba3477d0fdb0960e73` (PID 1314) alongside prior exec `3cb528138771884a52fa9bd01e5d5458ca4ffbd41c949282328d08b2dc0286bf` (PID 807). No dial-stdio/Buildx invocation appears in this task's command records. Its origin and causal relationship to socket drift are NOT_ESTABLISHED. Nothing was stopped or removed.

The corrected provider has a new SHA. Old accepted plan/candidate source pins cannot authorize it. Original synthetic source/root firewalls prevent legitimate full E2E at this new path; that coverage is explicitly unresolved. Retained local metadata is required by the image seam; no alternate source or acquisition fallback is introduced.

## 7. Recommended next action

Human-PI review/adjudicate the preserved live socket/ExecIDs drift and unresolved qualification coverage under a new explicit bounded transaction. Any eventual source acceptance requires a versioned installation candidate/plan supersession and later exact installation/effectivity authority. Do not install this source under the old plan. Recommendation only; no research or acceptance decision is made.

## Requested A–N evidence

| Item | Measured outcome / evidence |
| --- | --- |
| A Entry/authority | main, local HEAD and live origin/main `e492d159daf188323efcfe121aa019d5b098bfb2`; entry clean; canonical `e48580c1f9769d1b93ab995e6dcef3689c6920a9ce7b83f728526e9694dc68fd`, PREPARATION_EXECUTION_AUTHORIZED, 3 events; event #3 `{p.EVENT_3}`. Direct Human-PI candidate construction authority only. |
| B Frozen provenance | Every requested file/semantic pin and original package/provisioning seals verified in accepted_baseline_binding.json; all original bytes preserved. Network `880163…5c10` is the accepted semantic identity; raw enforcement file SHA is separately recorded. |
| C Current Engine IDs | BuildKit `sha256:cec9f139f45e93c5c69c60f8b07cfad9f43f4ef6b6a6cd917527fea5ff2e3dea`; proxy `sha256:036d4ab50fa49df89e746cf1b5369c88db46e8af2fbd08531788e7d920e9a491`. |
| D OCI config identities | BuildKit `sha256:27933730df224df80c41f4e5a9b33fa78831a79fd31903df3bb7deb49363422f`; proxy `sha256:5bf410ee7bb26f8f8fe9d7a2f9e9a05240cce0bc1bdbaee234f74f6b1b25ca94`. Raw retained config bytes hashed; linux/amd64 manifests and live Config/RootFS correspondence independently checked. BuildKit platform manifest `sha256:98cc6a3fc46220d00f8224ae483f3274fc874e9be8d7dd1e2e2c5481209228b5`. |
| E Discrepancy/correction | Original real observer used Engine `.Id` as config digest. Two assignments now call verified content-chain observation; two extra Engine-ID gates added; original config comparisons remain exact. Field semantics and serialization unchanged. |
| F Corrected provider SHA | `{provider_sha}`; NON-EFFECTIVE, uninstalled. |
| G Minimal delta | Authority.observe changes only the two image assignments; normalize_topology adds only two exact Engine checks; four associated image helpers plus tarfile import. Full AST equivalent after reverting those proven changes; all other functions/constants/guards unchanged. |
| H Topology SHA/comparison | Fresh corrected `{topology['observed_sha256']}` versus accepted `{topology['expected_sha256']}`. Same schema/23 field names; one differing field `/daemon_socket_observation`; BLOCKED. Raw observations generated using actual final candidate identity/normalization functions. |
| I Affected synthetic | 3 pure positives PASS; 52 negatives PASS_REJECTED. Original stale-topology/worker pure checks requalified; full preclaim/receipt/controller E2E NOT_RUN. |
| J Rejection matrix | rejection_matrix.json binds explicit tested reasons; all 52 exercised candidate logic. No historical rejection evidence changed or full A–X claim made. |
| K Supersession dependencies | supersession_dependency_report.json binds old provider/plan/candidate and proposed new source. Old source `{old_sha}` remains pinned; no accepted/effective replacement plan created. |
| L Evidence seal | artifact_sha256.json includes every new file's absolute path, byte size and SHA except itself; its own SHA is printed by final verification and reported in chat, avoiding a hash cycle. |
| M Preservation | All 1065 tracked files/index/canonical/event/ordered 641 work IDs and exact real ledger tree preserved; 641 UNSTARTED, 0 claims/terminals/retries/orphans. 3 containers (2 running), 5 networks, 1 volume, 57 image listing rows unchanged. Full daemon inspect differs only in ExecIDs; this mandatory contradiction is retained and blocks exact preservation. |
| N Negative boundaries | All six production targets remain absent; runtime/install/real attempt authority NO. No forbidden task action, no source promotion, no topology cleanup, no stage/commit/push. |

Report generated at {datetime.datetime.now(datetime.timezone.utc).isoformat()}. Evidence is implementation/observation material for bounded Human-PI adjudication, not a scientific validation or acceptance decision.
'''
    (HERE / "RUN_REPORT.md").write_text(report, encoding="utf-8")
    commands["finalization"] = {"argv": [str(p.a.ROOT / ".venv/bin/python"), "-B", "-m",
                                           "evaluation.downstream_benchmark.evidence.v6_production_runtime_image_identity_compatibility_bridge_v1.finalize_evidence"],
                                "ruff_argv": ruff_argv, "validation_argv": validation_argv,
                                "final_read_only_verification_argv": validation_argv + ["--verify-seal"]}
    write("commands_run.json", commands)
    # Revalidate completed JSON/report graph before sealing, without changing sources.
    from .validate_bridge_candidate import validate
    _, result = validate()
    assert result["status"] == validation["status"] == "BLOCKED"
    files = {}
    for path in sorted(HERE.rglob("*")):
        if path.is_file() and path.name != "artifact_sha256.json":
            files[str(path.relative_to(HERE))] = {"path": str(path), "size_bytes": path.stat().st_size,
                                                "sha256": p.a.sha(path.read_bytes())}
    write("artifact_sha256.json", {"schema": "V6_PRODUCTION_RUNTIME_IMAGE_IDENTITY_BRIDGE_ARTIFACT_SHA256_V1",
                                  "status": "BLOCKED", "candidate_only": True, "HUMAN_PI_ACCEPTED": "NO",
                                  "runtime_effective": "NO", "files": files, "excluded": ["artifact_sha256.json"],
                                  "file_count": len(files), "total_payload_size_bytes": sum(x["size_bytes"] for x in files.values()),
                                  "candidate_provider_sha256": provider_sha,
                                  "self_sha256": "Measured externally by --verify-seal; excluded to avoid self-hash cycle"})
    print(json.dumps({"status": "BLOCKED", "provider_sha256": provider_sha,
                      "manifest_sha256": p.a.sha((HERE / "artifact_sha256.json").read_bytes()),
                      "sealed_files": len(files)}))


if __name__ == "__main__":
    main()

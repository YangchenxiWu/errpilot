"""Offline validation of the blocked audit and current runtime's closed gates."""
from __future__ import annotations

import ast
import copy
import json
import subprocess
import sys
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a  # noqa: E402
from evaluation.downstream_benchmark.screening import v6_preparation_ledger as ledger  # noqa: E402
from evaluation.downstream_benchmark.screening import v6_preparation_runtime as r  # noqa: E402


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     indent=2, allow_nan=False) + "\n", encoding="utf-8")


def reject(call):
    try:
        call()
    except a.Rejected:
        return
    raise AssertionError("required rejection did not occur")


def main():
    descriptor, manifest = a.load_inputs()
    population = r.population()
    scope = a.loads((OUT / "work_item_scope.json").read_bytes())
    authority = a.loads(a.read_exact(r.PACKAGE + "authority_candidates.json", r.AUTH_CANDIDATE_SHA))
    network = authority["separate_permissions"]["BUILD_NETWORK"]
    assert a.identity(network) == scope["BUILD_NETWORK_semantic_sha256"]
    assert network["exact_scope"]["exact_network_work_item_ids"] == scope["restricted_work_item_ids"]
    assert a.derive_population(manifest) == population
    assert len(scope["restricted_work_item_ids"]) == 583
    assert len(scope["network_none_work_item_ids"]) == 58
    assert {x["case_id"] for x in population["items"]}.isdisjoint({"matplotlib::1", "matplotlib::8"})
    receipts = [None, {}, {"qualified": True}, {"proxy_identity": "wrong"},
                {"allowed_destinations": ["denied.invalid:443"]},
                {"scope": "wrong-583-work-items"},
                {"PIP_INDEX_URL": "https://denied.invalid/simple", "PIP_TRUSTED_HOST": "pypi.org"},
                {"tls_verify": False, "network": "default"}]
    restricted_rejections = 0
    none_rejections = 0
    for item in population["items"]:
        if item["build_network_required"]:
            for receipt in receipts:
                reject(lambda item=item, receipt=receipt: r.require_network(item, receipt))
                restricted_rejections += 1
        else:
            r.require_network(item, None)
            reject(lambda item=item: r.require_network(item, {"qualified": True}))
            none_rejections += 1
    transports = [
        ["build", "--network=default"], ["build", "--network=wrong-internal"],
        ["build", "--network=none", "--network=host"],
        ["run", "--network=none", "--network=external"],
        ["network", "rm", "unrelated"], ["network", "create", "anything"],
        ["container", "rm", "unrelated"], ["pull", "image"],
    ]
    with mock.patch.object(a.shared, "docker", side_effect=AssertionError("Docker forbidden")):
        engine = r.shared_engine()
        for argv in transports:
            reject(lambda argv=argv: engine.docker(argv))
    acceptance = a.loads(a.read_exact(r.AUTHORITY, r.AUTHORITY_SHA))
    item = population["items"][0]
    request = {"descriptor_path": a.CURRENT, "descriptor_sha": a.CURRENT_SHA,
               "manifest_path": a.MANIFEST, "manifest_sha": a.MANIFEST_SHA,
               "ordinal": item["census_order"], "case_id": item["case_id"],
               "plan_sha": item["plan_sha256"], "base_attempt_id": item["base_attempt_id"]}
    with mock.patch.object(a.shared, "docker", side_effect=AssertionError("real build forbidden")), \
            mock.patch.object(ledger.Ledger, "claim", side_effect=AssertionError("real claim forbidden")):
        reject(lambda: r.dispatch(request, acceptance=acceptance, policy=r.POLICY))
        for name in ("source_acquisition", "oracle_execution"):
            policy = copy.deepcopy(r.POLICY)
            policy[name] = True
            reject(lambda policy=policy: r.preflight(request, acceptance=acceptance, policy=policy))
    entry = a.loads((OUT / "entry_verification.json").read_bytes())
    for relative, expected in entry["accepted_file_hashes"].items():
        assert a.sha((ROOT / relative).read_bytes()) == expected, relative
    assert a.sha((a.B / "v6_current_state.json").read_bytes()) == a.CURRENT_SHA
    assert descriptor["event_count"] == 2
    assert a.sha((ROOT / ".git/index").read_bytes()) == entry["index_sha256"]
    enforcement = a.loads((OUT / "network_enforcement_identity.json").read_bytes()) \
        if (OUT / "network_enforcement_identity.json").is_file() else None
    if enforcement:
        observation = enforcement["QUALIFICATION_OBSERVATION_IDENTITY"]
        assert a.identity(observation) == enforcement["QUALIFICATION_OBSERVATION_SHA256"]
        assert enforcement["SEMANTIC_ENFORCEMENT_IDENTITY"] is None
        for name, expected in observation["observations"].items():
            assert a.sha((OUT / name).read_bytes()) == expected, name
    external = None
    if (OUT / "external_evidence_manifest.json").is_file():
        external = a.loads((OUT / "external_evidence_manifest.json").read_bytes())
        target = a.OUTPUT_ROOT / "qualification/restricted_build_egress_v1"
        assert external["root"] == str(target) and not target.is_symlink()
        assert a.sha((target / "artifact_sha256.json").read_bytes()) == external["external_manifest_sha256"]
        assert set(p.name for p in target.iterdir()) == {*external["artifacts"], "artifact_sha256.json"}
        for name, measured in external["artifacts"].items():
            assert a.sha((target / name).read_bytes()) == measured["sha256"]
            assert (target / name).stat().st_size == measured["bytes"]
            assert (target / name).read_bytes() == (OUT / name).read_bytes()
        assert external["real_attempt_claim_files_created"] == 0
    commands = a.loads((OUT / "commands_run.json").read_bytes())["commands"]
    for record in commands:
        argv = record["argv"]
        if argv[0] == "docker":
            assert argv[1] in {"version", "buildx", "network", "ps", "inspect", "image", "run", "build"}
            if argv[1] == "network":
                assert argv[2] in {"ls", "inspect"}
            if argv[1] == "image":
                assert argv[2] in {"ls", "inspect"}
            if argv[1] == "run":
                assert "--network=none" in argv and "--pull=never" in argv and "--rm" in argv
                assert record["name"].startswith("base_probe_")
            if argv[1] == "build":
                if record["name"] == "docker_build_help":
                    assert argv == ["docker", "build", "--help"]
                else:
                    assert record["name"] == "existing_builder_custom_network_parser_probe"
                    assert "--call=check" in argv and record["exit_code"] == 1
            if argv[1] == "buildx":
                assert argv[2] == "inspect"
    files = [p for p in OUT.iterdir() if p.is_file() and p.suffix in {".json", ".py", ".md", ".txt"}]
    ast_files = []
    for path in files:
        raw = path.read_bytes()
        text = raw.decode("utf-8", errors="strict")
        assert not raw.startswith(b"\xef\xbb\xbf") and b"\x00" not in raw and b"\r" not in raw
        assert text.endswith("\n")
        assert all(line.rstrip() == line for line in text.splitlines()), path
        if path.suffix == ".json":
            a.loads(raw)
        if path.suffix == ".py":
            ast.parse(text)
            ast_files.append(str(path.relative_to(ROOT)))
    production = [*r.IMPLEMENTATION, "evaluation/downstream_benchmark/tests/test_v6_preparation_runtime.py"]
    checked = {}
    for name, argv in [
        ("ruff", ["ruff", "check", "--no-cache", *production, *ast_files]),
        ("git_diff_check", ["git", "diff", "--check"]),
        ("tracked_worktree_clean", ["git", "diff", "--exit-code"]),
        ("index_clean", ["git", "diff", "--cached", "--exit-code"]),
    ]:
        result = subprocess.run(argv, cwd=ROOT, capture_output=True, check=False)
        checked[name] = {"argv": argv, "exit_code": result.returncode,
                         "stdout": result.stdout.decode(), "stderr": result.stderr.decode()}
        assert result.returncode == 0, name
    offline = {"restricted_items": 583, "restricted_blanket_rejections": restricted_rejections,
               "network_none_items": 58, "none_receipt_rejections": none_rejections,
               "transport_rejections": len(transports), "real_dispatch": "REJECT_BEFORE_CLAIM_OR_DOCKER",
               "enforcement_qualified_by_these_checks": False,
               "interpretation": "Existing runtime blanket default-deny only. These probes do not qualify a proxy, application environment or routing."}
    save("validation_results.json", {"status": "PASS_OFFLINE_WITH_COMPATIBILITY_BLOCKER",
         "AST_static": "PASS", "strict_JSON_UTF8_LF_BOM_NUL_whitespace": "PASS",
         "files_validated": sorted(str(p.relative_to(ROOT)) for p in files),
         "accepted_40_artifact_bytes_preserved": True, "canonical_descriptor_bytes_preserved": True,
         "index_bytes_preserved": True, "exact_scope": "641/583/58_PASS",
         "offline_rejection_probes": offline, "commands": checked,
         "existing_runtime_focused_tests": {"run": 6, "failed": 0, "errors": 0,
                                            "actual_target_filesystem_tests_rerun": False},
         "initial_system_python_attempt": "FAILED_BEFORE_AUDIT: ModuleNotFoundError jsonschema; recovered using existing .venv; no installation",
         "initial_validator_attempt": "FAILED: docker build --help observation initially treated as a build probe; read-only help exception corrected; final validation passes",
         "qualification_observation_identity": "PASS" if enforcement else "NOT_YET_AUTHORED",
         "external_manifest_and_all_23_external_files": "PASS" if external else "NOT_YET_PUBLISHED",
         "live_proxy_integration_tests": "NOT_RUN_COMPATIBILITY_GATE_BLOCKED",
         "positive_allowed_origins": "0/2_NOT_RUN", "negative_external_only_fixture": "NOT_RUN"})
    print(json.dumps({"status": "PASS_OFFLINE_WITH_COMPATIBILITY_BLOCKER", "offline": offline,
                      "ruff_exit_code": checked["ruff"]["exit_code"], "strict_files": len(files)}))


if __name__ == "__main__":
    main()

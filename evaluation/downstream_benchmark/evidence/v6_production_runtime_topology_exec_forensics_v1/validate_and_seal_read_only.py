"""Bounded evidence-only validator/sealer. Verification mode performs no writes."""
import ast
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REQUIRED = ["human_pi_authority.json", "entry_verification.json", "predecessor_binding.json", "exec_inspect_observations.json",
    "exec_process_attribution.json", "socket_diff_analysis.json", "docker_inspect_field_diff.json", "topology_security_invariants.json",
    "raw_socket_volatility_analysis.md", "synthetic_e2e_coverage_gap.json", "adjudication_options.md",
    "preservation_verification.json", "commands_run.json", "RUN_REPORT.md"]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pairs(items):
    result = {}
    for key, val in items:
        assert key not in result, "duplicate JSON key: " + key
        result[key] = val
    return result


def strict(raw):
    return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                      parse_constant=lambda val: (_ for _ in ()).throw(AssertionError("non-finite JSON " + val)))


def write(name, obj):
    (HERE / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def validate():
    files = [p for p in sorted(HERE.rglob("*")) if p.is_file()]
    checks, raw_exemptions = {}, []
    assert all((HERE / name).is_file() for name in REQUIRED)
    json_count = 0
    for p in files:
        raw = p.read_bytes()
        raw.decode("utf-8")
        if p.suffix == ".json":
            strict(raw)
            assert b"\r" not in raw and raw.endswith(b"\n"), str(p)
            json_count += 1
        elif p.suffix in (".py", ".md"):
            assert b"\r" not in raw and raw.endswith(b"\n"), str(p)
            assert all(line == line.rstrip() for line in raw.decode().splitlines()), str(p)
            if p.suffix == ".py":
                ast.parse(raw)
        else:
            raw_exemptions.append({"path": str(p.relative_to(HERE)), "sha256": sha(raw),
                "contains_CR": b"\r" in raw, "reason": "Exact raw observation/request bytes retained; HTTP CRLF and source formatting are not normalized."})
    checks["strict_JSON_UTF8_authored_LF_and_python_AST_syntax"] = True
    commands = strict((HERE / "commands_run.json").read_bytes())
    api_commands = []
    for item in commands:
        argv = item["argv"]
        assert isinstance(argv, list) and all(isinstance(x, str) for x in argv)
        if argv[0] == "git":
            assert argv[1] in ("rev-parse", "branch", "ls-files", "status", "diff", "ls-remote")
            assert "--output" not in argv and "-D" not in argv and "-d" not in argv
        elif argv[0] == "docker":
            assert argv[:3] in (["docker", "context", "show"], ["docker", "context", "inspect"]) or argv[:2] in (["docker", "inspect"], ["docker", "top"], ["docker", "logs"])
        elif argv[0] == "curl":
            assert argv[argv.index("--request") + 1] == "GET" and "--unix-socket" in argv
            assert argv[argv.index("--unix-socket") + 1] == "/Users/wuyangchenxi/.docker/run/docker.sock"
            assert argv[-1] == "http://localhost" + item["api_path"]
            assert re.fullmatch(r"/(containers/json\?all=1|images/json\?all=1|networks|volumes|networks/[a-f0-9]{64}|exec/[a-f0-9]{64}/json|containers/[a-f0-9]{64}/(json|top\?ps_args=-eo%20pid%2Cppid%2Clstart%2Cetime%2Cargs))", item["api_path"])
            api_commands.append(item)
        elif argv[0] == "python3":
            assert len(argv) == 2 and (ROOT / argv[1]).resolve().parent == HERE
            assert Path(argv[1]).name in ("analyse_read_only_evidence.py", "verify_preservation_read_only.py")
        else:
            raise AssertionError("unreviewed argv: " + str(argv))
        for stream in ("stdout", "stderr"):
            if stream + "_path" in item:
                actual = (HERE / item[stream + "_path"]).read_bytes()
            else:
                actual = item[stream].encode()
            assert sha(actual) == item[stream + "_sha256"], argv
        assert "started_at" in item and "finished_at" in item
    checks["exact_current_command_raw_hashes_timestamps_and_GET_only_allowlist"] = True
    source_hashes = strict((HERE / "raw_source_hashes.json").read_bytes())["files"]
    for name, entry in source_hashes.items():
        raw = Path(name).read_bytes()
        assert sha(raw) == entry["sha256"] and len(raw) == entry["size_bytes"], name
    checks["all_analysis_source_hashes_exact"] = True
    predecessor = strict((HERE / "predecessor_binding.json").read_bytes())
    correction = HERE.parent / "v6_production_runtime_image_identity_compatibility_bridge_v1"
    seal_raw = (correction / "artifact_sha256.json").read_bytes()
    assert sha(seal_raw) == predecessor["correction_seal_sha256"] == "ee8948b829a072ff10e3a41ba086afb4151821010661d89a05ce444ba95369e8"
    inventory = strict(seal_raw)["files"]
    assert len(inventory) == 280 and set(inventory) | {"artifact_sha256.json"} == {str(p.relative_to(correction)) for p in correction.rglob("*") if p.is_file()}
    for name, row in inventory.items():
        raw = (correction / name).read_bytes()
        assert sha(raw) == row["sha256"] and len(raw) == row["size_bytes"]
    checks["complete_predecessor_280_payloads_plus_manifest_preserved"] = True
    preservation = strict((HERE / "preservation_verification.json").read_bytes())
    assert preservation["status"] == "PASS" and all(preservation["checks"].values())
    assert preservation["real_ledger_states"] == {"UNSTARTED": 641}
    assert preservation["claims"] == preservation["terminals"] == preservation["retries"] == preservation["orphans"] == 0
    checks["all_20_repo_ledger_output_preservation_checks_and_git_diff_check"] = True
    socket = strict((HERE / "socket_diff_analysis.json").read_bytes())
    assert socket["added_inodes"] == ["18643", "14575"]
    assert {x["record"]["Num"] for x in socket["differences"]} == {"00000000319c26ff:", "000000002eda958e:"}
    assert all(x["classification"] == "UNRESOLVED" and x["exec_inode_causal_binding"] == "NOT_ESTABLISHED" for x in socket["differences"])
    assert socket["listener_record_exact_equality"] and not socket["FULL_RAW_TEXT_EQUALITY"]
    assert socket["current_socket_table"] == "CURRENT_SOCKET_TABLE_NOT_REOBSERVED"
    checks["socket_classification_bound_to_exact_historical_raw_evidence"] = True
    attribution = strict((HERE / "exec_process_attribution.json").read_bytes())
    assert attribution["unique_initiating_command_attribution_count"] == 0
    assert all(x["ATTRIBUTED_INITIATING_COMMAND"] is None and x["UNRESOLVED_ORIGIN"] == "ORIGIN_NOT_ESTABLISHED" for x in attribution["execs"])
    for row in attribution["execs"]:
        for obs in row["live_observations"]:
            if obs["available"]:
                assert obs["parsed"]["ID"] == row["exec_id"]
                assert obs["parsed"]["ContainerID"] == "165fb59b3d43bd73a48072e6c283d338e9140b700f3e3f3bd0b3bc3602b06402"
            else:
                assert obs["parsed"] is None
    checks["no_fabricated_exec_metadata_or_causal_attribution"] = True
    coverage = strict((HERE / "synthetic_e2e_coverage_gap.json").read_bytes())
    assert coverage["historical_rejection_count"] == 52 and len(coverage["historical_positive_checks"]) == 3
    assert all(x["equal"] for x in coverage["independent_AST_checks"].values())
    assert coverage["full_corrected_E2E"] == "NOT_RUN" and coverage["sources_imported_or_executed"] is False
    checks["coverage_gap_AST_provenance_and_no_E2E_claim"] = True
    failed = [{"argv": x["argv"], "returncode": x["returncode"], "http_status": x.get("http_status"),
               "stdout_path": x.get("stdout_path"), "stderr_path": x.get("stderr_path")}
              for x in commands if x["returncode"] not in (0,) or x.get("http_status") not in (None, 200)]
    return {"schema": "V6_FORENSIC_BOUNDED_EVIDENCE_VALIDATION_V1", "status": "PASS", "checks": checks,
        "strict_JSON_file_count_before_seal": json_count, "source_hash_count": len(source_hashes),
        "command_count": len(commands), "Engine_GET_count": len(api_commands), "forbidden_command_category_count": 0,
        "observed_failures": failed, "failures_are_preserved_not_claimed_PASS": True,
        "raw_exact_byte_LF_exemptions": raw_exemptions, "production_or_synthetic_E2E_tests_run": False,
        "scope": "Evidence consistency/preservation validation only; not scientific validation or production qualification."}


def main():
    assert sys.argv[1:] in (["--seal"], ["--verify-seal"])
    results = validate()
    if sys.argv[1] == "--seal":
        write("validation_results.json", results)
        files = {str(p.relative_to(HERE)): {"sha256": sha(p.read_bytes()), "size_bytes": p.stat().st_size}
                 for p in sorted(HERE.rglob("*")) if p.is_file() and p.name != "artifact_sha256.json"}
        write("artifact_sha256.json", {"schema": "V6_PRODUCTION_RUNTIME_TOPOLOGY_EXEC_FORENSICS_ARTIFACT_SHA256_V1",
            "status": "V6_PRODUCTION_RUNTIME_TOPOLOGY_EXEC_FORENSICS_READY_FOR_HUMAN_PI_ADJUDICATION",
            "next_gate": "HUMAN_PI_ADJUDICATE_V6_PRODUCTION_RUNTIME_TOPOLOGY_STABILITY_AND_EXEC_ORIGIN",
            "HUMAN_PI_ACCEPTED": "NO", "runtime_effective": "NO", "candidate_only": True,
            "file_count": len(files), "total_payload_size_bytes": sum(x["size_bytes"] for x in files.values()),
            "files": files, "excluded": ["artifact_sha256.json"],
            "self_sha256": "Measured externally; manifest excluded to avoid a self-hash cycle"})
    seal_raw = (HERE / "artifact_sha256.json").read_bytes()
    seal = strict(seal_raw)
    expected = set(seal["files"]) | {"artifact_sha256.json"}
    assert expected == {str(p.relative_to(HERE)) for p in HERE.rglob("*") if p.is_file()}
    for name, row in seal["files"].items():
        raw = (HERE / name).read_bytes()
        assert sha(raw) == row["sha256"] and len(raw) == row["size_bytes"], name
    print(json.dumps({"status": seal["status"], "bounded_checks": len(results["checks"]),
        "seal_sha256": sha(seal_raw), "payload_file_count": seal["file_count"], "total_files_including_manifest": len(expected),
        "payload_size_bytes": seal["total_payload_size_bytes"], "sealed_inventory_verification": "PASS"}))


if __name__ == "__main__":
    main()

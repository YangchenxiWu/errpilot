"""Exclusively publish frozen blocked-audit evidence in a non-attempt namespace."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a  # noqa: E402

TARGET = a.OUTPUT_ROOT / "qualification/restricted_build_egress_v1"
NAMES = (
    "accepted_decision.json", "entry_verification.json", "compatibility_analysis.json",
    "base_runtime_revalidation.json", "docker_state_before.json", "docker_state_after.json",
    "commands_run.json", "global_state_preservation.json", "cleanup_verification.json",
    "work_item_scope.json", "allowlist_policy.json", "positive_qualification.json",
    "negative_qualification.json", "rejection_matrix.json", "qualification_results.json",
    "validation_prepublication.json", "attempt_state_observations.json", "topology_identity.json",
    "proxy_implementation_status.json", "network_enforcement_identity.json", "focused_tests.txt",
    "audit_compatibility.py",
)


def publish(path, raw):
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    assert path.read_bytes() == raw


def main():
    for parent in (TARGET, *TARGET.parents):
        a.require(not parent.is_symlink(), "symlink publication path")
    a.require(TARGET.parent.is_dir() and not TARGET.exists(), "publication collision or missing accepted parent")
    entry = a.loads((OUT / "entry_verification.json").read_bytes())
    for name, expected in entry["accepted_file_hashes"].items():
        a.require(a.sha((ROOT / name).read_bytes()) == expected, "accepted artifact drift")
    a.require(a.sha((ROOT / a.CURRENT).read_bytes()) == a.CURRENT_SHA, "canonical drift")
    identity = a.loads((OUT / "network_enforcement_identity.json").read_bytes())
    observation = identity["QUALIFICATION_OBSERVATION_IDENTITY"]
    a.require(a.identity(observation) == identity["QUALIFICATION_OBSERVATION_SHA256"], "observation identity drift")
    for name, expected in observation["observations"].items():
        a.require(a.sha((OUT / name).read_bytes()) == expected, "observation source drift")
    TARGET.mkdir(mode=0o700)
    entries = {}
    for name in NAMES:
        source = OUT / name
        a.require(source.is_file() and not source.is_symlink(), "missing/symlink evidence source")
        raw = source.read_bytes()
        publish(TARGET / name, raw)
        entries[name] = {"sha256": a.sha((TARGET / name).read_bytes()), "bytes": len(raw)}
    manifest = {"schema": "V6_RESTRICTED_BUILD_EGRESS_EXTERNAL_EVIDENCE_SHA256_V1",
                "namespace": "QUALIFICATION_ONLY_NOT_BASE_ATTEMPT", "root": str(TARGET),
                "accepted_output_root": str(a.OUTPUT_ROOT), "artifacts": entries,
                "file_count_including_manifest": len(entries) + 1, "self_hash_excluded": True,
                "qualification_observation_sha256": identity["QUALIFICATION_OBSERVATION_SHA256"],
                "real_attempt_claim_files_created": 0}
    raw = (json.dumps(manifest, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")
    publish(TARGET / "artifact_sha256.json", raw)
    directory = os.open(TARGET, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    result = {**manifest, "external_manifest_path": str(TARGET / "artifact_sha256.json"),
              "external_manifest_sha256": a.sha((TARGET / "artifact_sha256.json").read_bytes()),
              "read_after_write_verified": True, "exclusive_file_creation": True,
              "file_and_target_directory_fsync": True}
    (OUT / "external_evidence_manifest.json").write_text(
        json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"root": str(TARGET), "files": len(entries) + 1,
                      "manifest_sha256": result["external_manifest_sha256"]}))


if __name__ == "__main__":
    main()

"""Exclusively publish frozen observations beside owned synthetic ledger fixtures."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(OUT))
from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a  # noqa: E402
from evaluation.downstream_benchmark.screening import v6_preparation_ledger as ledger  # noqa: E402
from validate_bridge import external_files  # noqa: E402

Q = a.OUTPUT_ROOT / "qualification/restricted_build_egress_compatibility_bridge_v1"


def main():
    ledger.safe_path(Q)
    a.require(Q.is_dir() and {p.name for p in Q.iterdir()} == {"ledger-fixtures"},
              "publication requires only this transaction's existing ledger fixtures; no overwrite")
    fixture_result = a.loads((OUT / "persistent_ledger_qualification.json").read_bytes())
    a.require(fixture_result["filesystem_root"] == str(Q / "ledger-fixtures")
              and fixture_result["status"] == "PASS", "owned fixture provenance")
    prepublication = (OUT / "validation_results.json").read_bytes()
    ledger.exclusive_write(OUT / "validation_prepublication.json", prepublication)
    selected = sorted(p for p in OUT.iterdir() if p.is_file() and p.suffix in {".json", ".txt"}
                      and p.name not in {"validation_results.json", "artifact_sha256.json",
                                         "external_evidence_manifest.json"})
    bindings = {}
    for source in selected:
        raw = source.read_bytes()
        ledger.exclusive_write(Q / source.name, raw)
        a.require((Q / source.name).read_bytes() == raw, "external publication mismatch")
        bindings[source.name] = a.sha(raw)
    # Preserve intentional malformed/symlink fixtures as no-follow observations.
    # They are negative test evidence, not valid materializer evidence trees.
    artifacts = external_files(Q)
    for path in sorted(Q.rglob("*"), reverse=True):
        if path.is_symlink():
            continue
        if path.is_file():
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
        elif path.is_dir():
            ledger.fsync_dir(path)
    manifest = {"schema": "V6_BRIDGE_BLOCKED_QUALIFICATION_EXTERNAL_ARTIFACTS_V1",
        "namespace": ledger.SYNTHETIC, "status": "BUILDKIT_RUNTIME_MISSING",
        "artifacts": artifacts, "repository_observation_hashes": bindings,
        "intentional_negative_fixtures": "Partial records and symlink targets are recorded without following links",
        "real_attempt_ids_used_as_claims": [], "real_attempts": 0}
    raw = json.dumps(manifest, sort_keys=True, indent=2, allow_nan=False).encode() + b"\n"
    ledger.exclusive_write(Q / "artifact_sha256.json", raw)
    a.require(external_files(Q) == artifacts, "external inventory changed")
    record = {"root": str(Q), "manifest_sha256": a.sha(raw),
        "file_or_symlink_count_including_manifest": len(artifacts) + 1,
        "repository_observation_hashes": bindings, "artifact_inventory": artifacts,
        "publication": "EXCLUSIVE_O_NOFOLLOW_FSYNC_READBACK; symlink targets never followed",
        "real_claim_files_created": 0}
    ledger.exclusive_write(OUT / "external_evidence_manifest.json",
        json.dumps(record, sort_keys=True, indent=2, allow_nan=False).encode() + b"\n")
    print(json.dumps({"status": "PUBLISHED_BLOCKED_OBSERVATIONS", "root": str(Q),
        "artifacts_including_manifest": len(artifacts) + 1, "real_attempts": 0}))


if __name__ == "__main__":
    main()

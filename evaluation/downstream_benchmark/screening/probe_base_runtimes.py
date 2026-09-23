"""Probe only recorded immutable base Python images, without subject mounts."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path


PROBE_CODE = (
    "import hashlib,json,platform,sys\n"
    "p=sys.executable\n"
    "with open(p,'rb') as f: digest=hashlib.sha256(f.read()).hexdigest()\n"
    "print(json.dumps({'sys_version':sys.version,'version':'.'.join(map(str,sys.version_info[:3])),"
    "'machine':platform.machine(),'executable':p,'executable_sha256':digest},sort_keys=True))\n"
)
EVIDENCE_FIELDS = (
    "probe_observed_version", "probe_sys_version", "probe_platform_machine",
    "python_executable", "python_executable_sha256", "probe_stdout_sha256",
    "probe_stderr_sha256", "probe_exit_code",
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def probe_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    if len(rows) != 7 or {row["python_version"] for row in rows} != {
        "3.6.9", "3.7.0", "3.7.3", "3.7.4", "3.7.7", "3.8.1", "3.8.3"
    }:
        raise ValueError("unexpected base-runtime inventory")
    for field in EVIDENCE_FIELDS:
        if field not in fields:
            fields.append(field)
    for row in rows:
        digest = row["immutable_digest"]
        if (row["platform"] != "linux/amd64" or row["image_source"] != "docker.io/library/python"
                or not re.fullmatch(r"sha256:[0-9a-f]{64}", digest)):
            raise ValueError("unexpected base-runtime identity")
        reference = f"docker.io/library/python@{digest}"
        pull = subprocess.run(
            ["docker", "pull", "--platform=linux/amd64", reference],
            capture_output=True, check=False,
        )
        if pull.returncode != 0:
            row.update({field: "" for field in EVIDENCE_FIELDS})
            row["probe_exit_code"] = "NOT_RUN"
            row["runtime_probe_status"] = "EXACT_PROBE_FAILED"
            row["blocking_reason"] = "EXACT_IMAGE_PULL_FAILED"
            continue
        result = subprocess.run(
            ["docker", "run", "--rm", "--platform=linux/amd64", "--network=none",
             "--pull=never", "--entrypoint=python", reference, "-c", PROBE_CODE],
            capture_output=True, check=False,
        )
        row["probe_stdout_sha256"] = _sha256(result.stdout)
        row["probe_stderr_sha256"] = _sha256(result.stderr)
        row["probe_exit_code"] = str(result.returncode)
        try:
            observed = json.loads(result.stdout.decode("utf-8", errors="strict"))
        except (UnicodeError, json.JSONDecodeError):
            observed = {}
        row["probe_observed_version"] = observed.get("version", "")
        # JSON escaping keeps the exact multiline sys.version as one CSV field.
        row["probe_sys_version"] = json.dumps(observed.get("sys_version", ""), ensure_ascii=False)
        row["probe_platform_machine"] = observed.get("machine", "")
        row["python_executable"] = observed.get("executable", "")
        row["python_executable_sha256"] = observed.get("executable_sha256", "")
        valid = (
            result.returncode == 0
            and observed.get("version") == row["python_version"]
            and observed.get("machine") == "x86_64"
            and isinstance(observed.get("executable"), str)
            and observed["executable"].startswith("/")
            and re.fullmatch(r"[0-9a-f]{64}", observed.get("executable_sha256", "")) is not None
        )
        row["runtime_probe_status"] = "EXACT_PROBE_PASSED" if valid else "EXACT_PROBE_FAILED"
        row["blocking_reason"] = "NONE" if valid else "EXACT_PYTHON_IDENTITY_MISMATCH_OR_PROBE_FAILED"
    return fields, rows


def write_rows(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    target = Path(__file__).resolve().parents[1] / "runtime_base_images.csv"
    write_rows(target, *probe_rows(target))

"""Read-only BLOCKED-package integrity audit and frozen-runtime regression.

No production installation candidate exists: section 11 required a hard stop.
This verifier does not construct a controller/provider, claim, build or write.
"""
from __future__ import annotations

import ast
import importlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from evaluation.downstream_benchmark.evidence.v6_preparation_execution_run_v1 import validate_entry as previous
from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a
from evaluation.downstream_benchmark.screening import v6_preparation_ledger as ledger
from evaluation.downstream_benchmark.screening import v6_preparation_runtime as legacy

OUT = Path(__file__).resolve().parent
NATIVE = "evaluation.downstream_benchmark.evidence.v6_native_buildkit_client_compatibility_bridge_v1.successor_runtime"
STATUS = "V6_PREPARATION_EXECUTION_PRODUCTION_RUNTIME_RECEIPT_CONTRACT_BLOCKED"
NOT_CONSTRUCTED = (
    "production_controller_candidate.py", "production_provider_candidate.py",
    "production_runtime_installation_candidate.json", "installation_plan.json",
)


def audit(event, args):
    if event == "open":
        mode, flags = args[1:3]
        a.require(not (isinstance(mode, str) and any(c in mode for c in "wax+")), "audit: write open refused")
        a.require(not (isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)), "audit: write flags refused")
    if event.startswith("socket.") or event in {
        "os.mkdir", "os.remove", "os.rmdir", "os.rename", "os.link", "os.symlink",
        "os.chmod", "os.chown", "os.truncate", "os.system", "os.posix_spawn",
    }:
        raise a.Rejected("audit: filesystem/network mutation refused: " + event)
    if event == "subprocess.Popen":
        argv = args[1]
        a.require(isinstance(argv, (list, tuple)) and len(argv) > 1 and argv[0] == "git"
                  and argv[1] in {"ls-files", "diff", "rev-parse", "branch", "cat-file"},
                  "audit: only local read-only Git allowed")


def load(name):
    return a.loads((OUT / name).read_bytes())


def real_tree():
    result = {}
    for name in ("namespace.json", "ledger", "attempts", "inputs", "snapshots"):
        root = a.OUTPUT_ROOT / name
        if not root.exists():
            result[name] = {"type": "ABSENT"}
            continue
        for path in [root, *sorted(root.rglob("*"))] if root.is_dir() else [root]:
            ledger.safe_path(path)
            row = {"type": "directory" if path.is_dir() else "file", "mode": path.stat().st_mode & 0o777}
            if path.is_file():
                row.update(size=path.stat().st_size, sha256=a.sha(path.read_bytes()))
            result[str(path.relative_to(a.OUTPUT_ROOT))] = row
    return result


def receipt_scan():
    binding = load("receipt_contract_analysis.json")["accepted_inventory_scan"]
    closure = a.ROOT / binding["closure_path"]
    a.require(a.sha(closure.read_bytes()) == binding["closure_sha256"], "closure SHA drift")
    section = closure.read_text().split("## 8. Exact complete accepted repository inventory", 1)[1]
    refs = {m.group(1): m.group(2) for m in re.finditer(r"^\| `([^`]+)` \| `([a-f0-9]{64})` \|$", section, re.M)}
    a.require(len(refs) == 376 and a.identity(refs) == binding["inventory_sha256"], "accepted inventory drift")
    schemas, production_hits = {}, []
    for relative, digest in refs.items():
        raw = a.read_exact(relative, digest)
        if Path(relative).suffix in {".py", ".json", ".md"}:
            text = raw.decode("utf-8")
            for schema in sorted(set(re.findall(r"V6_[A-Z0-9_]*RECEIPT[A-Z0-9_]*", text))):
                schemas.setdefault(schema, []).append(relative)
            for n, line in enumerate(text.splitlines(), 1):
                if re.search(r"production.{0,100}receipt|receipt.{0,100}production", line, re.I):
                    production_hits.append({"path": relative, "line": n, "text": line[:400]})
    a.require(schemas == binding["receipt_schemas"] and production_hits == binding["production_receipt_text_hits"] == [], "receipt scan differs")
    a.require(set(schemas) == {"V6_RESTRICTED_BUILD_EGRESS_ENFORCEMENT_RECEIPT_CANDIDATE_V1"}, "unexpected receipt contract")
    return binding


def regressions():
    native = importlib.import_module(NATIVE)
    original_dispatch = native.dispatch
    original_transport = native.NativeDockerTransport
    original_namespace = dict(native.__dict__)
    rows = []

    def reject(name, call):
        try:
            call()
        except a.Rejected as exc:
            rows.append({"check": name, "result": "PASS_EXPECTED_REJECTION", "reason": str(exc), "scope": "FROZEN_RUNTIME_READ_ONLY"})
        else:
            raise AssertionError("expected rejection absent: " + name)

    reject("old_frozen_dispatch_real_execution", lambda: native.dispatch(runtime_authority=True))

    class RealRunner:
        namespace = ledger.REAL

    class NewQualificationRunner:
        namespace = "SYNTHETIC_PRODUCTION_RUNTIME_QUALIFICATION"

    class QualificationRunner:
        namespace = ledger.SYNTHETIC

    kwargs = dict(compiled={}, binding={}, layout=None, artifact_root=a.OUTPUT_ROOT / "attempts/PROBE_NOT_CREATED")
    reject("qualification_transport_rejects_real_provider_namespace", lambda: native.NativeDockerTransport(**kwargs, runner=RealRunner()))
    reject("qualification_transport_rejects_new_controller_namespace", lambda: native.NativeDockerTransport(**kwargs, runner=NewQualificationRunner()))
    reject("fake_qualification_namespace_at_real_output_root", lambda: native.NativeDockerTransport(**kwargs, runner=QualificationRunner()))
    transport = native.NativeDockerTransport(compiled={}, binding={}, layout=None,
        artifact_root=a.OUTPUT_ROOT / "qualification/production_runtime_installation_v1/PROBE_NOT_CREATED", runner=QualificationRunner())
    engine = native.shared_engine(transport)
    reject("frozen_shared_engine_real_materialization", lambda: engine._materialize_checked({},
        output=a.OUTPUT_ROOT / "qualification/production_runtime_installation_v1/PROBE_NOT_CREATED",
        input_root=a.OUTPUT_ROOT, synthetic_only=False))
    reject("frozen_shared_engine_wrong_output_root", lambda: engine._materialize_checked({},
        output=a.OUTPUT_ROOT / "attempts/PROBE_NOT_CREATED", input_root=a.OUTPUT_ROOT, synthetic_only=True))
    a.require(native.ONCE_ONLY["real_dispatch"] == "REJECT", "frozen ONCE_ONLY changed")

    _, manifest = a.load_inputs()
    items = legacy.population()["items"]
    restricted = next(item for item in items if item["build_network_required"])
    plan = a.select(manifest, ordinal=restricted["census_order"], case_id=restricted["case_id"], plan_sha=restricted["plan_sha256"])
    receipt = {"schema": "V6_RESTRICTED_BUILD_EGRESS_ENFORCEMENT_RECEIPT_CANDIDATE_V1",
        "semantic_enforcement_sha256": previous.ENFORCEMENT_SHA,
        "base_attempt_id": restricted["base_attempt_id"], "runtime_authority": False}
    proxy = "http://errpilot-v6-egress-42393faa3385-v1-proxy:3128"
    compiled = native.compile_transport(restricted, plan, proxy_url=proxy, enforcement_receipt=receipt)
    a.require(compiled["real_dispatch"] == "REJECT", "candidate receipt upgraded")
    reject("qualification_receipt_forged_runtime_authority", lambda: native.compile_transport(restricted, plan,
        proxy_url=proxy, enforcement_receipt={**receipt, "runtime_authority": True}))
    reject("wrong_enforcement_identity_frozen_compiler", lambda: native.compile_transport(restricted, plan,
        proxy_url=proxy, enforcement_receipt={**receipt, "semantic_enforcement_sha256": "0" * 64}))
    none = next(item for item in items if not item["build_network_required"])
    none_plan = a.select(manifest, ordinal=none["census_order"], case_id=none["case_id"], plan_sha=none["plan_sha256"])
    reject("enforcement_receipt_on_network_none", lambda: native.compile_transport(none, none_plan, proxy_url=proxy, enforcement_receipt=receipt))
    none_compiled = native.compile_transport(none, none_plan, proxy_url="unused", enforcement_receipt=None)
    a.require(none_compiled["frontend_options"] == ["force-network-mode=none"] and none_compiled["build_args"] == {}, "NONE binding drift")
    # Guard-only probes; these call no executable and do not mutate runtime code.
    for name, argv in (("Buildx_solve", ["docker", "buildx", "build"]),
                       ("base_pull", ["docker", "pull", "python"]),
                       ("source_fetch", ["git", "fetch", "origin"])):
        try:
            native.guards.command(argv)
        except ValueError as exc:
            rows.append({"check": name, "result": "PASS_EXPECTED_REJECTION", "reason": str(exc), "scope": "FROZEN_COMMAND_GUARD_ONLY"})
        else:
            raise AssertionError("guard accepted: " + name)
    a.require(native.dispatch is original_dispatch and native.NativeDockerTransport is original_transport
              and native.__dict__ == original_namespace, "frozen namespace/function replacement")
    a.read_exact(previous.NATIVE + "successor_runtime.py", previous.SOURCE_SHA)
    a.read_exact(previous.NATIVE + "successor_runtime_integration_candidate.json", previous.CONFIG_SHA)
    tree = ast.parse((a.ROOT / previous.NATIVE / "successor_runtime.py").read_text())
    dispatch = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "dispatch")
    a.require(len(dispatch.body) == 2 and isinstance(dispatch.body[0], ast.Expr)
              and isinstance(dispatch.body[1], ast.Raise), "dispatch is no longer unconditional raise")
    return rows


def main():
    sys.dont_write_bytecode = True
    sys.addaudithook(audit)
    entry = load("entry_verification.json")
    baseline = entry["before_new_write_audit"]
    before = previous.tracked_fingerprint()
    a.require(before == baseline["tracked_before"], "tracked byte/mode fingerprint changed")
    a.require(previous.git("rev-parse", "HEAD").strip().decode() == previous.HEAD, "HEAD drift")
    a.require(previous.git("branch", "--show-current").strip() == b"main", "branch drift")
    a.require(previous.git("diff", "--name-only") == previous.git("diff", "--cached", "--name-only") == b"", "tracked/index mutation")
    predecessor = load("blocked_run_predecessor_binding.json")["files"]
    for relative, row in predecessor.items():
        path = a.ROOT / relative
        a.require(not path.is_symlink() and path.stat().st_size == row["size"] and a.sha(path.read_bytes()) == row["sha256"], "predecessor bytes changed")
    untracked = {raw.decode() for raw in previous.git("ls-files", "--others", "--exclude-standard", "-z").split(b"\0") if raw}
    namespace = str(OUT.relative_to(a.ROOT)) + "/"
    a.require({p for p in untracked if not p.startswith(namespace)} == set(predecessor), "unrelated untracked path")
    a.require(a.sha((a.ROOT / a.CURRENT).read_bytes()) == previous.CURRENT_SHA, "canonical drift")
    a.require(real_tree() == entry["real_tree"], "real persistent tree mutation")
    scan = receipt_scan()
    for name in NOT_CONSTRUCTED:
        a.require(not (OUT / name).exists(), "artifact constructed after mandatory stop")
    for relative in ("evaluation/downstream_benchmark/screening/v6_preparation_production_controller.py",
                     "evaluation/downstream_benchmark/screening/v6_preparation_production_provider.py",
                     legacy.INSTALLATION, "evaluation/downstream_benchmark/V6_NATIVE_BUILDKIT_CLIENT_RUNTIME_INSTALLATION_V1.json"):
        a.require(not (a.ROOT / relative).exists(), "production source/authority installed")
    rows = regressions()
    states = previous.journal_observation(legacy.population()["items"])
    a.require(states == baseline["ledger_after"], "real ledger drift")
    a.require(real_tree() == entry["real_tree"] and previous.tracked_fingerprint() == before, "regression mutation")
    seal_verified = False
    if "--verify-seal" in sys.argv:
        inventory = load("artifact_sha256.json")
        actual = {p.name: {"size": p.stat().st_size, "sha256": a.sha(p.read_bytes())}
                  for p in sorted(OUT.iterdir()) if p.name != "artifact_sha256.json"}
        a.require(all(p.is_file() and not p.is_symlink() for p in OUT.iterdir()), "special artifact")
        a.require(actual == inventory["files"], "artifact inventory drift")
        a.require(untracked == set(predecessor) | {namespace + p.name for p in OUT.iterdir()}, "untracked exact inventory drift")
        seal_verified = True
    print(json.dumps({"schema": "V6_PRODUCTION_RUNTIME_BLOCKED_PACKAGE_VALIDATION_V1",
        "audit_end_utc": datetime.now(timezone.utc).isoformat(), "status": STATUS,
        "integrity_validation": "PASS", "frozen_regression": rows,
        "frozen_regression_count": len(rows), "production_controller_provider_qualification": "NOT_RUN",
        "accepted_inventory_count": scan["inventory_count"], "accepted_inventory_sha256": scan["inventory_sha256"],
        "ledger_after": states, "real_tree_sha256": a.identity(real_tree()),
        "tracked_after": before, "predecessor_count": len(predecessor), "artifact_seal_verified": seal_verified,
        "PRODUCTION_RUNTIME_INSTALLED": "NO", "REAL_PRODUCTION_ENTRY_EFFECTIVE": "NO",
        "REAL_PREPARATION_ATTEMPTS_CONSUMED": 0, "REAL_CLAIMS_CREATED": 0,
        "REAL_TERMINALS_CREATED": 0, "REAL_BUILDS_EXECUTED": 0,
        "REAL_LEDGER_MUTATION": "NO", "ENVIRONMENT_READY_CASES_ESTABLISHED": 0,
        "SOURCE_ACQUISITION_EXECUTED": "NO", "ORACLE_EXECUTED": "NO",
        "ALLOCATION_EXECUTED": "NO", "DOWNSTREAM_REPAIR_EXECUTED": "NO",
        "GIT_STAGE": "NO", "GIT_COMMIT": "NO", "GIT_PUSH": "NO"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

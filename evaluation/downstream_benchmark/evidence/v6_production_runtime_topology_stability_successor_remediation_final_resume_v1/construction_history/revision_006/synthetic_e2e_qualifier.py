"""Deterministic local synthetic qualification; no Docker/network/real ledger writes.

Every mutation case owns a different synthetic ledger under the requested external
qualification root. Provider fixtures supply local observations, not benchmark
builds. Real transport compilation/commands and scientific code preservation are
checked separately against the exact accepted work, without dispatching it.
"""
from __future__ import annotations

import copy
import runpy
import json
import contextlib
import io
import traceback
from dataclasses import replace
from pathlib import Path

from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a
from evaluation.downstream_benchmark.screening import v6_preparation_ledger as ledger
from evaluation.downstream_benchmark.screening import v6_preparation_runtime as legacy

from . import production_controller_remediated_candidate as c
from . import production_provider_remediated_candidate as p
from . import remediation_regressions as regression
from . import additional_security_regressions as additional

OUT = a.ROOT / p.RESUME
RUN_EVIDENCE = None
STATUS = "V6_PREPARATION_EXECUTION_PRODUCTION_RUNTIME_INSTALLATION_CANDIDATE_READY_FOR_HUMAN_PI_REVIEW"


def write(path, value):
    ledger.mkdir_durable(path.parent)
    ledger.exclusive_write(path, p.pretty(value) if not isinstance(value, bytes) else value)


def digest(label):
    return a.sha(("SYNTHETIC_" + label + "\n").encode())


def synthetic_item(label, required):
    # Preserve the existing record topology and schema; synthesize only fixtures.
    template = next(x for x in legacy.population()["items"] if x["variant"] == "SOURCE_INDEPENDENT")
    item = copy.deepcopy(template)
    def synthetic_values(value):
        if isinstance(value, dict):
            return {k: synthetic_values(v) for k, v in value.items()}
        if isinstance(value, list):
            return [synthetic_values(v) for v in value]
        if isinstance(value, str) and a.shared.HEX64.fullmatch(value):
            return digest(label + value)
        return value
    item = synthetic_values(item)
    item.update(case_id="SYNTHETIC_" + label, base_attempt_id="SYNTHETIC_QUALIFICATION_" + label,
                build_network_required=required, census_order=1, frozen_rank=1)
    item["current_descriptor"]["path"] = "SYNTHETIC_CANONICAL"
    item["preparation_manifest"]["path"] = "SYNTHETIC_MANIFEST"
    item["input_bindings"] = {"SYNTHETIC_INPUT_" + str(i): digest(label + str(i)) for i in range(len(item["input_bindings"]))}
    return item


def fixture(root):
    ledger.mkdir_durable(root)
    for name in ("claims", "terminals", "locks"):
        ledger.mkdir_durable(root / "ledger" / name)
    _, accepted = a.load_inputs()
    templates = legacy.population()["items"]
    selected = []
    for label, required in (("RESTRICTED_A", True), ("RESTRICTED_B", True), ("NONE", False), ("FAILURE", True)):
        old_item = next(x for x in templates if x["variant"] == "SOURCE_INDEPENDENT" and x["build_network_required"] is required)
        plan = a.select(accepted, ordinal=old_item["census_order"], case_id=old_item["case_id"], plan_sha=old_item["plan_sha256"])
        plan.update(case_id="SYNTHETIC_" + label, census_order=len(selected) + 1)
        plan["plan_sha256"] = a.identity({k: v for k, v in plan.items() if k != "plan_sha256"})
        selected.append(plan)
    manifest = {**accepted, "plans": selected}
    write(root / "scientific_manifest.json", manifest)
    items = [{**a.work_item(plan, "SOURCE_INDEPENDENT"), "base_attempt_id": "SYNTHETIC_QUALIFICATION_" + plan["case_id"].removeprefix("SYNTHETIC_")} for plan in selected]
    population = {"schema": "V6_SYNTHETIC_WORK_POPULATION_V2", "namespace": p.SYNTHETIC, "items": items}
    write(root / "population.json", population)
    seed = p.exact_json(a.ROOT / "evaluation/downstream_benchmark/evidence/v6_production_runtime_image_identity_compatibility_bridge_v1/qualification/synthetic_identity_v1/run_4/baseline_fixture.json")
    config = p.frozen_inputs()
    objects = copy.deepcopy(seed["objects"])
    sockets = "Num RefCount Protocol Flags Type St Inode Path\n0000000000000001: 00000002 00000000 00010000 0001 01 340 /run/buildkit/buildkitd.sock\n0000000000000002: 00000002 00000000 00010000 0001 01 344 /run/buildkit/otel-grpc.sock\n0000000000000003: 00000003 00000000 00000000 0001 03 3697 /run/buildkit/buildkitd.sock\n"
    routes = "Iface Destination Gateway Flags RefCnt Use Metric Mask MTU Window IRTT\neth0 00001CAC 00000000 0001 0 0 0 0000FFFF 0 0 0\n"
    objects["daemon"].update(sockets=sockets, routes=routes, native_binary_sha256=config["client_binary_sha256"], daemon_binary_sha256=config["daemon_binary_sha256"])
    for role in ("daemon", "proxy"):
        objects[role]["image_config_digest"] = p.image_identity_pins(config, role)["config"]
        write(root / "topology" / (role + ".json"), objects[role])
    access = {"complete": True, "unverifiable": [], "ownership_observation": "INDEPENDENT_LSTAT_ACL_MOUNT_USER_NAMESPACE",
        "endpoints": [{"path": path, "type": "SOCKET", "uid": 0, "gid": 0, "mode": 432, "unauthorized_access": False,
            "acl_complete": True, "acl": [], "mount_namespace": "SYNTHETIC_DAEMON_NAMESPACE", "user_namespace": "SYNTHETIC_USER_NS"} for path in p.LISTENER_PATHS]}
    inventory = {"complete": True, "unverifiable_surfaces": [], "tcp": [], "udp": [], "unix_listener_paths": p.LISTENER_PATHS,
                 "ipv6_complete": True, "ipv6_route_inventory": []}
    census = {"sessions": [{"session_id": "SYNTHETIC_SESSION_A", "endpoint": config["endpoint"], "process_identity": "SYNTHETIC_HOST_PROCESS_A",
        "control_capable": True, "socket_inodes": ["3697"]}], "observed_session_ids": ["SYNTHETIC_SESSION_A"],
        "covered_surfaces": ["HOST_LAUNCH", "ENGINE_EXEC_ATTACH", "CONTAINER_PROCESS", "UNIX_ACCESS", "NETWORK_ENDPOINT"], "unobserved_surfaces": [], "complete": True}
    evidence = {"namespace": p.SYNTHETIC, "approved_principals": ["SYNTHETIC_HUMAN_PI_APPROVED_PRINCIPAL"],
        "sessions": [{"session_id": "SYNTHETIC_SESSION_A", "session_endpoint": config["endpoint"], "process_identity": "SYNTHETIC_HOST_PROCESS_A",
            "source_kind": "AUTHENTICATED_HOST_LAUNCH_PROVENANCE", "authenticated_source": True, "correlation_complete": True,
            "source_sha256": digest("SYNTHETIC_PROVENANCE"), "classification": "AUTHORIZED", "principal": "SYNTHETIC_HUMAN_PI_APPROVED_PRINCIPAL",
            "independent_inaccessibility": False, "original_source_utf8": "SYNTHETIC_HOST_PROVENANCE_ORIGINAL_BYTES"}],
        "boundary": {"source_kind": "INDEPENDENT_SOCKET_ACCESS_RESTRICTIONS", "source_sha256": digest("SYNTHETIC_ACCESS_BOUNDARY"),
            "verified_access_restrictions": True, "complete": True, "unverifiable_surfaces": [], "original_source_utf8": "SYNTHETIC_BOUNDARY_ORIGINAL_BYTES"}}
    evidence["sessions"][0]["source_sha256"] = a.sha(evidence["sessions"][0]["original_source_utf8"].encode())
    evidence["boundary"]["source_sha256"] = a.sha(evidence["boundary"]["original_source_utf8"].encode())
    values = {**objects, "images": seed["identities"], "proxy_source": seed["proxy_source"], "proxy_policy": seed["policy_raw"],
        "unix_sockets": sockets, "routes": routes, "socket_access": access, "listener_inventory": inventory, "client_census": census, "client_evidence": evidence}
    sources = {}
    for name, value in values.items():
        raw = value.encode() if isinstance(value, str) else a.canonical(value)
        sources[name] = {"raw_utf8": raw.decode(), "sha256": a.sha(raw), "source": "SYNTHETIC_RAW_" + name,
            "method": "CANDIDATE_OWNED_HERMETIC_FIXTURE", "timestamp": "SYNTHETIC_ACQUISITION_1", "missing": [], "unverifiable": []}
    bundle = {"schema": "V6_FULL_RAW_OBSERVATION_ENVELOPE_V2", "namespace": p.SYNTHETIC, "synthetic_only": True, "sources": sources,
        "historical_execs": "ORIGIN_NOT_ESTABLISHED", "acquisition_id": "SYNTHETIC_ACQUISITION_1", "stage": "SYNTHETIC_FIXTURE"}
    bind_fixture_provenance(bundle)
    write(root / "raw_fixture.json", bundle)
    observation = p.verify_raw_security(bundle, config, stage="ISSUANCE", synthetic=True)
    canonical = {"namespace": p.SYNTHETIC, "state": "PREPARATION_EXECUTION_AUTHORIZED", "event_3_id": a.sha(b"SYNTHETIC_EVENT_3\n")}
    write(root / "canonical.json", canonical)
    refs = {key: {"path": p.RESUME + name, "sha256": a.sha((OUT / name).read_bytes())} for key, name in (
        ("controller", "production_controller_remediated_candidate.py"), ("provider", "production_provider_remediated_candidate.py"),
        ("receipt_contract", "receipt_authority_contract_v2_candidate.json"))}
    security_contracts = {name: {"path": p.RESUME + name, "sha256": a.sha((OUT / name).read_bytes())} for name in p.SECURITY_CONTRACT_NAMES}
    payload = {"schema": "V6_SYNTHETIC_SUCCESSOR_EFFECTIVITY_FIXTURE_V2", "namespace": p.SYNTHETIC, "synthetic_only": True,
        "HUMAN_PI_ACCEPTED": "NO", "runtime_effective": "NO", "qualification_root": str(root),
        "canonical": {"path": str(root / "canonical.json"), "sha256": a.sha((root / "canonical.json").read_bytes())},
        "event_3_id": canonical["event_3_id"], **refs, "receipt_schema": p.RECEIPT_SCHEMA, "enforcement_identity": p.ENFORCEMENT,
        "population_identity": p.population_identity(population, (root / "population.json").read_bytes()),
        "ledger_binding_identity": {**p.ledger_identity(), "root": str(root / "ledger")}, "live_topology": observation["security_projection"],
        "security_contracts": security_contracts, "accepted_client_principals": evidence["approved_principals"]}
    path = root / "synthetic_effectivity_fixture.json"
    write(path, payload)
    return path, items


def observations(item, receipt_raw):
    return "MATERIALIZED", {name: digest(item["base_attempt_id"] + name) for name in ledger.SUCCESS}, ""


def journal_files(root):
    return {n: {x.name: a.sha(x.read_bytes()) for x in sorted((root / "ledger" / n).iterdir()) if x.is_file()}
            for n in ("claims", "terminals", "locks")}


def main():
    global RUN_EVIDENCE
    frozen_globals_before = {k: id(v) for k, v in a.shared.__dict__.items()}
    ledger.safe_path(p.QUALIFICATION_ROOT)
    if not p.QUALIFICATION_ROOT.exists():
        p.QUALIFICATION_ROOT.mkdir(mode=0o700)
        write(p.QUALIFICATION_ROOT / "transaction.json", {"request_sha256": a.sha((OUT / "raw_human_pi_request.txt").read_bytes())})
    else:
        a.require(p.exact_json(p.QUALIFICATION_ROOT / "transaction.json") == {"request_sha256": a.sha((OUT / "raw_human_pi_request.txt").read_bytes())}, "qualification root belongs to another transaction")
    number = 1
    while (p.QUALIFICATION_ROOT / ("run_" + str(number))).exists():
        number += 1
    run_root = p.QUALIFICATION_ROOT / ("run_" + str(number))
    RUN_EVIDENCE = OUT / "construction_history" / ("qualification_run_" + str(number))
    RUN_EVIDENCE.mkdir(exist_ok=False)
    ledger.mkdir_durable(run_root)
    for name in ("production_controller_remediated_candidate.py", "production_provider_remediated_candidate.py", "synthetic_e2e_qualifier.py",
                 "receipt_authority_contract_v2_candidate.json", "receipt_schema_v2_candidate.json", "topology_stability_contract_candidate.json"):
        write(run_root / "input-source" / name, (OUT / name).read_bytes())
    results, rejects = {}, {}
    primary_root = None
    counter = 0
    def fresh():
        nonlocal counter
        counter += 1
        path, items = fixture(run_root / ("fixture_" + str(counter)))
        return c.ProductionController.synthetic(path), items, path
    golden = p.exact_json(a.ROOT / "evaluation/downstream_benchmark/evidence/v6_production_runtime_topology_stability_successor_resume_v1/rejection_matrix.json")["checks"]
    def rejected(name, call, root=None, zero=False, *, reason=None, classification=None):
        root = root or primary_root
        before = journal_files(root)
        files_before = regression.inventory(root)
        captured = io.StringIO()
        try:
            with contextlib.redirect_stderr(captured):
                call()
        except (a.Rejected, ValueError, TypeError, KeyError, OSError, SystemExit) as exc:
            expected = regression.reason_spec(name, golden, reason, classification)
            regression.assert_reason(name, exc, expected, captured.getvalue())
            a.require(before == journal_files(root), "rejection mutated synthetic ledger: " + name)
            a.require(files_before == regression.inventory(root), "rejection mutated durable evidence: " + name)
            if zero:
                a.require(all(not x for x in before.values()), "preclaim fixture already consumed")
            record = {"status": "PASS_REJECTED", "reason": str(exc),
                      "ledger_unchanged": True, "zero_claims_preclaim": zero,
                      "ledger_before": before, "ledger_after": journal_files(root),
                      "evidence_before": files_before, "evidence_after": regression.inventory(root),
                      "expected_category": name, "intended_gate": expected,
                      "observed_rejection": type(exc).__name__, "stderr": captured.getvalue(),
                      "fixture_root": str(root), "fixture_identity": a.identity(files_before),
                      "exact_tested_sources": source_identities(), "attempts_consumed_by_rejection": 0}
            a.require(name not in rejects, "duplicate rejection evidence identity")
            rejects[name] = record
            write(RUN_EVIDENCE / "executed_rejections" / (name + ".json"), p.pretty(record))
        else:
            raise AssertionError("unexpected acceptance: " + name)
    controller, items, primary_fixture = fresh()
    root = controller.authority.root
    primary_root = root
    admitted = controller.prepare(items[0])
    write(root / "issued-receipt.json", admitted.receipt_raw)
    a.require((root / "issued-receipt.json").read_bytes() == admitted.receipt_raw, "receipt canonical readback")
    from jsonschema import Draft202012Validator
    Draft202012Validator(p.exact_json(OUT / "receipt_schema_v2_candidate.json")).validate(a.loads(admitted.receipt_raw))
    a.require(all(not x for x in journal_files(root).values()), "issuance consumed attempt")
    a.require(admitted.receipt_raw == controller.prepare(items[0]).receipt_raw, "receipt SHA nondeterministic")
    results["receipt_issuance_no_consumption_and_deterministic_sha"] = {"status": "PASS", "receipt_sha256": a.sha(admitted.receipt_raw)}
    claim = controller.claim(admitted)
    a.require(claim["receipt_sha256"] == a.sha(admitted.receipt_raw), "durable receipt SHA missing")
    provider = p.ProductionProvider(controller.authority, items[0], claim, admitted.receipt_raw)
    state, evidence, reason = provider.execute_synthetic(p.SyntheticScenario())
    terminal = controller.authority.journal().terminal(claim, state=state, evidence=evidence, reason=reason)
    results["restricted_route"] = {"status": "PASS", "claim_sha256": a.identity(claim), "terminal_sha256": a.identity(terminal)}
    rejected("receipt_post_terminal", lambda: p.ProductionProvider(controller.authority, items[0], claim, admitted.receipt_raw), root)
    rejected("terminal_overwrite", lambda: controller.authority.journal().terminal(claim, state=state, evidence=evidence), root)
    rejected("receipt_reuse", lambda: controller.claim(admitted), root)
    rejected("duplicate_claim", lambda: controller.claim(admitted), root)
    rejected("retry", lambda: c.request_retry(), root)
    none_admission = controller.prepare(items[2])
    a.require(none_admission.receipt_raw is None and none_admission.binding["receipt_sha256"] is None, "NONE semantics")
    none_terminal = controller.run_synthetic(items[2], p.SyntheticScenario())
    none_claim = controller.authority.journal()._read(controller.authority.journal()._path("claims", items[2]["base_attempt_id"]))
    a.require(none_claim["receipt_sha256"] is None and none_terminal["state"] == "MATERIALIZED", "NONE successful route")
    results["NONE_route"] = {"status": "PASS", "receipt_sha256": None}
    def fail(item, raw):
        raise RuntimeError("SYNTHETIC_PROVIDER_FAILURE")
    failure = controller.run_synthetic(items[3], p.SyntheticScenario("RAISE"))
    a.require(failure["state"] == "INTERRUPTED", "provider failure terminal")
    a.require(len(list((root / "ledger/terminals").glob(items[3]["base_attempt_id"] + ".json"))) == 1, "failure terminal count")
    results["provider_failure_one_immutable_terminal"] = {"status": "PASS", "state": failure["state"]}
    topo = controller.authority.observe()
    pending = items[1]
    raw = controller.prepare(pending).receipt_raw
    rejected("NONE_receipt_present", lambda: p.verify_receipt(controller.authority, items[2], raw, topo))
    rejected("NONE_issuance", lambda: p.receipt_value(controller.authority, items[2], topo))
    rejected("restricted_receipt_null", lambda: p.verify_receipt(controller.authority, pending, None, topo))
    value = a.loads(raw)
    changed_work = copy.deepcopy(value)
    changed_work["work_item_identity"]["census_order"] = True
    rejected("receipt_work_bool_integer_confusion", lambda: p.verify_receipt(controller.authority, pending, a.canonical(changed_work), topo))
    mutations = {"wrong_production_schema": ("schema", "WRONG"),
        "qualification_receipt_promoted": ("schema", "V6_RESTRICTED_BUILD_EGRESS_ENFORCEMENT_RECEIPT_CANDIDATE_V1"),
"wrong_allowed_origins": ("allowed_origins", ["pypi.org:443"]),
        "broader_allowlist": ("allowed_origins", p.ORIGINS + ["example.org:443"]),
        "stale_topology_sha": ("security_projection_sha256", "0" * 64),
        "receipt_other_attempt": ("base_attempt_id", items[0]["base_attempt_id"]),
        "receipt_wrong_work_identity": ("work_item_identity", items[0]),
        "receipt_stale_effectivity": ("production_runtime_effectivity_pin_sha256", "0" * 64),
        "receipt_stale_canonical": ("canonical_state_sha256", "0" * 64),
        "receipt_stale_event_3": ("event_3_id", "0" * 64),
        "receipt_stale_controller": ("controller_source_sha256", "0" * 64),
        "receipt_stale_provider": ("provider_source_sha256", "0" * 64),
        "receipt_stale_contract": ("receipt_contract_sha256", "0" * 64),
        "receipt_stale_enforcement": ("enforcement_identity", "0" * 64)}
    for name, (key, wrong) in mutations.items():
        changed = {**value, key: wrong}
        rejected(name, lambda changed=changed: p.verify_receipt(controller.authority, pending, a.canonical(changed), topo))
    rejected("noncanonical_receipt_bytes", lambda: p.verify_receipt(controller.authority, pending, p.pretty(value), topo))
    rejected("duplicate_receipt_keys", lambda: p.verify_receipt(controller.authority, pending, b'{"schema":"x","schema":"y"}\n', topo))
    for name, mutate in (
        ("wrong_controller_sha", lambda x: x["controller"].update(sha256="0" * 64)),
        ("wrong_provider_sha", lambda x: x["provider"].update(sha256="0" * 64)),
        ("wrong_receipt_contract_sha", lambda x: x["receipt_contract"].update(sha256="0" * 64)),
        ("wrong_population_identity", lambda x: x["population_identity"].update(total=641)),
        ("wrong_enforcement_identity", lambda x: x.update(enforcement_identity="0" * 64)),
        ("wrong_event_3", lambda x: x.update(event_3_id="0" * 64)),
        ("wrong_canonical_SHA", lambda x: x["canonical"].update(sha256="0" * 64)),
        ("wrong_topology_fields", lambda x: x["live_topology"]["worker_identity"].update(ID="STALE_WORKER")),
        ("fake_qualification_namespace", lambda x: x.update(namespace="SYNTHETIC_QUALIFICATION_ONLY")),
        ("synthetic_fixture_asserts_production_acceptance", lambda x: x.update(HUMAN_PI_ACCEPTED="YES")),
        ("synthetic_fixture_asserts_production_effectivity", lambda x: x.update(runtime_effective="YES"))):
        ctrl, xs, path = fresh()
        data = a.loads(path.read_bytes())
        mutate(data)
        Path(path).write_bytes(p.pretty(data))
        rejected(name, lambda ctrl=ctrl, xs=xs: ctrl.prepare(xs[0]), ctrl.authority.root, True)
    ctrl, xs, path = fresh()
    absent = path.parent / "absent_effectivity.json"
    rejected("missing_effectivity_pin", lambda: c.ProductionController.synthetic(absent), ctrl.authority.root, True)
    ctrl, xs, path = fresh()
    admission = ctrl.prepare(xs[0])
    daemon_path = ctrl.authority.root / "topology/daemon.json"
    data = a.loads(daemon_path.read_bytes())
    data["State"]["Pid"] += 1
    Path(daemon_path).write_bytes(p.pretty(data))
    rewrite_raw_object(ctrl.authority.root, "daemon", data)
    rejected("stale_topology_preclaim", lambda: ctrl.claim(admission), ctrl.authority.root, True)
    results["live_local_topology_reobserved_immediately_preclaim"] = {"status": "PASS", "test": "stale_topology_preclaim", "Docker_used": False}
    ctrl, xs, path = fresh()
    admission = ctrl.prepare(xs[0])
    changed = replace(admission, binding={**admission.binding, "receipt_sha256": "0" * 64})
    rejected("claim_receipt_SHA_mismatch", lambda: ctrl.claim(changed), ctrl.authority.root, True)
    ctrl, xs, path = fresh()
    admission = ctrl.prepare(xs[0])
    claim = ctrl.claim(admission)
    wrong_claim = copy.deepcopy(claim)
    wrong_claim["receipt_sha256"] = "0" * 64
    wrong_claim["input_runtime_binding"]["receipt_sha256"] = "0" * 64
    claim_path = ctrl.authority.journal()._path("claims", xs[0]["base_attempt_id"])
    Path(claim_path).write_bytes(a.canonical(wrong_claim))  # Owned corruption fixture, never real ledger.
    rejected("provider_receipt_SHA_mismatch", lambda: p.ProductionProvider(ctrl.authority, xs[0], wrong_claim, admission.receipt_raw), ctrl.authority.root)
    ctrl, xs, path = fresh()
    admission = ctrl.prepare(xs[0])
    claim = ctrl.claim(admission)
    rejected("provider_restricted_null_before_build", lambda: p.ProductionProvider(ctrl.authority, xs[0], claim, None), ctrl.authority.root)
    none_admission = ctrl.prepare(xs[2])
    none_claim = ctrl.claim(none_admission)
    rejected("provider_NONE_receipt_before_build", lambda: p.ProductionProvider(ctrl.authority, xs[2], none_claim, admission.receipt_raw), ctrl.authority.root)
    another_admission = ctrl.prepare(xs[1])
    another_claim = ctrl.claim(another_admission)
    rejected("provider_other_attempt_receipt_before_build", lambda: p.ProductionProvider(ctrl.authority, xs[1], another_claim, admission.receipt_raw), ctrl.authority.root)
    ctrl, xs, path = fresh()
    admission = ctrl.prepare(xs[0])
    other_ctrl, _, _ = fresh()
    rejected("permit_other_ledger_root", lambda: other_ctrl.authority.journal().claim(xs[0]["base_attempt_id"], admission.binding, permit=admission), other_ctrl.authority.root, True)
    ctrl, xs, path = fresh()
    rejected("unknown_attempt", lambda: ctrl.prepare({**xs[0], "base_attempt_id": "SYNTHETIC_QUALIFICATION_UNKNOWN"}), ctrl.authority.root, True)
    rejected("regenerated_attempt_ID", lambda: ctrl.prepare({**xs[0], "base_attempt_id": "v6-prep-base-" + "0" * 64}), ctrl.authority.root, True)
    rejected("blocker_dispatch", lambda: ctrl.prepare({**xs[0], "case_id": "matplotlib::1"}), ctrl.authority.root, True)
    rejected("mutated_work_binding", lambda: ctrl.prepare({**xs[0], "recipe_sha256": "0" * 64}), ctrl.authority.root, True)
    rejected("synthetic_authority_usable_by_real_entry", lambda: ctrl.run(xs[0]), ctrl.authority.root, True)
    rejected("candidate_real_controller", c.ProductionController)
    rejected("candidate_real_provider", p.Authority)
    rejected("synthetic_real_ledger_path", lambda: p.Authority.synthetic(a.OUTPUT_ROOT / "namespace.json"))
    # Copy source under the qualification root and prove its synthetic factory
    # rejects by actual __file__; never install a live target or mutate globals.
    for module, name, method in ((c, "production_controller_remediated_candidate.py", "ProductionController"),
                                 (p, "production_provider_remediated_candidate.py", "Authority")):
        copy_path = run_root / "copied-production-entry" / name
        write(copy_path, Path(module.__file__).read_bytes())
        copied = runpy.run_path(str(copy_path), run_name="candidate_copy_guard_probe")
        rejected("copied_installed_" + method + "_synthetic_interface", lambda copied=copied, method=method: copied[method].synthetic(path), root)
    # Pure production status validator is shared with the real installed loader;
    # these dictionaries are never persisted as accepted production authority.
    status = {"schema": "V6_PREPARATION_PRODUCTION_RUNTIME_EFFECTIVITY_V2", "candidate_only": False,
              "HUMAN_PI_ACCEPTED": "YES", "runtime_effective": "YES",
              "canonical": {"path": a.CURRENT, "sha256": p.CANONICAL_SHA}, "event_3_id": p.EVENT_3}
    for key, value in (("candidate_only", True), ("HUMAN_PI_ACCEPTED", "NO"), ("runtime_effective", "NO")):
        rejected("effectivity_" + key, lambda key=key, value=value: p.validate_effectivity_status({**status, key: value}))
    for key, value in (("total", 640), ("restricted", 582), ("none", 59), ("ordered_attempt_ids_sha256", "0" * 64)):
        rejected("wrong_real_population_" + key, lambda key=key, value=value: p.validate_real_population({**p.expected_population_identity(), key: value}))
    # Scientific compilation is read-only across all exact frozen work items.
    _, manifest = a.load_inputs()
    population = legacy.population()
    maps = p.exact_json(a.ROOT / p.NATIVE / "seven_base_transport_map.json")["mapping"]
    compiled_count = 0
    for item in population["items"]:
        plan = a.select(manifest, ordinal=item["census_order"], case_id=item["case_id"], plan_sha=item["plan_sha256"])
        compiled = p.compile_production_transport(item, plan, topo, receipt_raw=raw if item["build_network_required"] else None)
        a.require(compiled["scientific_dockerfile"] == a.shared.build_definition(a.engine_recipe(plan),
            source_present=item["variant"] != "SOURCE_INDEPENDENT",
            dependency_present=plan["recipe_candidate"]["requirements"]["dependency_bytes_b64"] is not None), "scientific Dockerfile changed")
        base = next(x for x in maps if x["scientific_base_authority"] == item["base_image_reference"])
        binding = {**base, "endpoint": p.frozen_inputs()["endpoint"], "native_binary_sha256": p.frozen_inputs()["client_binary_sha256"],
            "same_daemon": True, "daemon_count": 1, "runtime_reference": p.frozen_inputs()["runtime_image"]["immutable_reference"],
            "frontend_alias": "errpilot_frozen_base", "container_id": digest("DAEMON"), "container_root": "/tmp/errpilot-v6-test",
            "proxy_internal_host_binding": "add-hosts=errpilot-v6-egress-42393faa3385-v1-proxy=172.28.0.3",
            "tag": "errpilot-synthetic-test", "compiled": compiled}
        argv = p.native.native_argv(binding, binding["container_root"], binding["tag"], compiled)
        p.validate_command(["docker", "exec", binding["container_id"], *argv], binding)
        compiled_count += 1
    results["all_641_scientific_recipe_and_native_command_projection"] = {"status": "PASS", "count": compiled_count, "restricted": 583, "NONE": 58, "builds": 0}
    for name, argv in {"source_fetch": ["git", "fetch"], "base_pull": ["docker", "pull", "python"],
        "registry_fallback": ["docker", "build", "."], "Buildx_solve": ["docker", "buildx", "build", "."],
        "host_buildctl": ["/usr/bin/buildctl", "build"],
        "network_on_NONE": ["docker", "run", "--network=default", "--pull=never", "synthetic"]}.items():
        rejected(name, lambda argv=argv: p.validate_command(argv, binding))
    for op in ("SOURCE_ACQUISITION", "ORACLE", "ALLOCATION", "REPAIR", "PATCH_FROZEN_RUNTIME", "MONKEYPATCH_FROZEN_RUNTIME"):
        rejected(op.lower(), lambda op=op: c.request_operation(op))
    rejected("old_frozen_dispatch_as_production", p.native.dispatch)
    class RealRunner:
        namespace = p.REAL
    rejected("old_frozen_transport_as_production", lambda: p.native.NativeDockerTransport(compiled=None,
        binding=None, layout=None, artifact_root=a.OUTPUT_ROOT / "never-created", runner=RealRunner()))
    class QualificationRunner:
        namespace = "SYNTHETIC_QUALIFICATION_ONLY"
    frozen_transport = p.native.NativeDockerTransport(compiled=None, binding=None, layout=None,
        artifact_root=run_root / "frozen-wrapper-probe", runner=QualificationRunner())
    rejected("old_frozen_materializer_as_production", lambda: p.native.shared_engine(frozen_transport)._materialize_checked({},
        output=run_root / "never-created-materializer", input_root=run_root, synthetic_only=False))
    a.require(p.native.ONCE_ONLY["real_dispatch"] == "REJECT", "frozen ONCE_ONLY real dispatch changed")
    results["shared_scientific_code_objects_preserved"] = {"status": "PASS", "evidence": "actual original shared _materialize_checked path exercised in restricted and NONE source-pair E2E", "frozen_dispatch_guards": "UNCHANGED"}
    results["receipt_contract_schema"] = {"status": "PASS", "canonical_roundtrip": True, "byte_sha_binding": True, "NONE_receipt": "PROHIBITED"}
    add_v2_suite(fresh, rejected, results, rejects)
    regression.run(fresh, rejected, results, rejects, RUN_EVIDENCE, bind_fixture_provenance)
    additional.run(fresh, rejected, results, RUN_EVIDENCE, bind_fixture_provenance)
    a.require(frozen_globals_before == {k: id(v) for k, v in a.shared.__dict__.items()}, "legacy globals mutated")
    external = {str(x.relative_to(p.QUALIFICATION_ROOT)): {"sha256": a.sha(x.read_bytes()), "size_bytes": x.stat().st_size}
                for x in sorted(run_root.rglob("*")) if x.is_file()}
    summary = {"schema": "V6_PRODUCTION_RUNTIME_RESUME_SYNTHETIC_QUALIFICATION_V1", "status": "PASS",
        "namespace": p.SYNTHETIC, "qualification_run_root": str(run_root), "fixture_count": counter,
        "test_provider": "Explicit candidate-only in-process provider of deterministic local observations; no native solve executed",
        "tests": results, "rejection_count": len(rejects), "rejections": rejects,
        "primary_effectivity_fixture": {"path": str(primary_fixture), "sha256": a.sha(primary_fixture.read_bytes())},
        "external_inventory": external, "Docker_used": False, "public_network_used": False,
        "real_claims": 0, "real_terminals": 0, "real_builds": 0,
        "production_topology_effective_claimed": False, "environment_ready_cases_established": 0}
    # Summary is written after complete coverage below.
    inherited = p.exact_json(a.ROOT / "evaluation/downstream_benchmark/evidence/v6_preparation_execution_production_runtime_installation_resume_v1/rejection_matrix.json")
    a.require(set(inherited["checks"]) <= set(rejects), "mandatory inherited rejection category skipped")
    a.require(set(golden) <= set(rejects), "mandatory 126 inherited category missing")
    summary["inherited_126_count"] = len(golden)
    summary["new_rejection_count"] = len(rejects) - len(golden)
    summary["required_A_through_X"] = required_coverage(results, rejects)
    summary["required_inherited_A_X"] = {letter: {"status": "PASS", "checks": record["evidence_checks"]} for letter, record in inherited["required_A_X_coverage"].items()}
    for record in summary["required_inherited_A_X"].values():
        a.require(all(x in results or x in rejects for x in record["checks"]), "inherited A-X missing actual execution")
    summary["test_provider"] = "Candidate-owned normal SyntheticScenario and SyntheticScientificTransport; original shared scientific code object executes context/build/probes/identity with simulated I/O. No arbitrary callable or native execution."
    summary["full_source_pair_E2E"] = True
    summary["real_client_authorization_status"] = "BLOCKED_UNTIL_INDEPENDENT_LIVE_EVIDENCE"
    write(RUN_EVIDENCE / "synthetic_e2e_results.json", summary)
    write(RUN_EVIDENCE / "rejection_matrix.json", p.pretty({"schema": "V6_SUCCESSOR_RESUME_REJECTIONS_V2", "status": "PASS_REJECTED", "inherited_count": 126, "new_count": len(rejects) - 126, "mandatory_skipped": 0, "checks": rejects, "required_A_X_coverage": summary["required_A_through_X"], "inherited_A_X_coverage": summary["required_inherited_A_X"]}))
    print(json.dumps({"status": "PASS", "fixture_count": counter, "rejections": len(rejects), "A_X": len(summary["required_A_through_X"]), "exact_sources": source_identities()}))




def source_identities():
    return {**{str(Path(module.__file__).relative_to(a.ROOT)): a.sha(Path(module.__file__).read_bytes()) for module in (c, p)},
            **{p.RESUME + name: a.sha((OUT / name).read_bytes()) for name in p.HELPER_SHA256}}


def rewrite_raw_object(root, name, value):
    path = root / "raw_fixture.json"
    bundle = p.exact_json(path)
    raw = value.encode() if isinstance(value, str) else a.canonical(value)
    bundle["sources"][name].update(raw_utf8=raw.decode(), sha256=a.sha(raw))
    Path(path).write_bytes(p.pretty(bundle))


def mutate_raw(root, name, mutate):
    bundle = p.exact_json(root / "raw_fixture.json")
    value = a.loads(bundle["sources"][name]["raw_utf8"].encode())
    mutate(value)
    rewrite_raw_object(root, name, value)


def add_v2_suite(fresh, rejected, results, rejects):
    # Actual preclaim source-pair gates for C1-C16 and mandatory V2 invariants.
    cases = {
        "unknown_active_client": ("client_evidence", lambda x: x["sessions"][0].update(classification="UNKNOWN")),
        "unauthorized_active_client": ("client_evidence", lambda x: x["sessions"][0].update(classification="UNAUTHORIZED")),
        "incomplete_client_census": ("client_census", lambda x: x.update(complete=False)),
        "unobserved_control_surface": ("client_census", lambda x: x.update(unobserved_surfaces=["UNKNOWN_HOST_ENDPOINT"])),
        "unverifiable_socket_access": ("socket_access", lambda x: x.update(complete=False)),
        "unverifiable_access_boundary": ("client_evidence", lambda x: x["boundary"].update(verified_access_restrictions=False)),
        "authorized_boolean_alone": ("client_evidence", lambda x: x["sessions"][0].update(source_kind="PROCESS_NAME_BUILDCTL", authorized=True)),
        "unknown_principal": ("client_evidence", lambda x: x["sessions"][0].update(principal="UNKNOWN")),
        "uncorrelated_Engine_exec_metadata": ("client_evidence", lambda x: x["sessions"][0].update(correlation_complete=False)),
        "duplicate_client_attribution": ("client_evidence", lambda x: x["sessions"].append(copy.deepcopy(x["sessions"][0]))),
        "missing_client_attribution": ("client_evidence", lambda x: x.update(sessions=[])),
        "unattributed_connected_socket": ("client_census", lambda x: x["sessions"][0].update(socket_inodes=[])),
        "wrong_daemon_image": ("daemon", lambda x: x.update(Image="sha256:" + "0" * 64)),
        "wrong_daemon_image_config": ("images", lambda x: x["daemon"].update(config_raw=x["daemon"]["config_raw"] + " ")),
        "wrong_daemon_platform": ("images", lambda x: x["daemon"]["selected"].update(Architecture="arm64")),
        "wrong_proxy_image": ("proxy", lambda x: x.update(Image="sha256:" + "0" * 64)),
        "wrong_native_binary": ("daemon", lambda x: x.update(native_binary_sha256="0" * 64)),
        "wrong_daemon_binary": ("daemon", lambda x: x.update(daemon_binary_sha256="0" * 64)),
        "wrong_worker": ("worker", lambda x: x[0].update(ID="SYNTHETIC_WRONG_WORKER")),
        "wrong_worker_platform": ("worker", lambda x: x[0].update(PLATFORMS=["linux/arm64"])),
        "external_daemon_attachment": ("daemon", lambda x: x["NetworkSettings"]["Networks"].update(EXTERNAL={"NetworkID": "WRONG"})),
        "unauthorized_internal_participant": ("network", lambda x: x["Containers"].update(UNAUTHORIZED={"Name": "UNAUTHORIZED"})),
        "wrong_proxy_policy": ("proxy_policy", lambda x: x.update(allowed_port=80)),
        "external_control_listener": ("listener_inventory", lambda x: x.update(tcp=[{"address": "0.0.0.0", "port": 1234}])),
        "incomplete_listener_inventory": ("listener_inventory", lambda x: x.update(complete=False)),
        "unverifiable_IPv6_route": ("listener_inventory", lambda x: x.update(ipv6_complete=False)),
        "world_accessible_control_socket": ("socket_access", lambda x: x["endpoints"][0].update(mode=438)),
        "wrong_endpoint_owner": ("socket_access", lambda x: x["endpoints"][0].update(uid=999)),
        "unaccepted_client_principal_set": ("client_evidence", lambda x: x.update(approved_principals=["UNREVIEWED_PRINCIPAL"])),
        "missing_original_provenance_bytes": ("client_evidence", lambda x: x["sessions"][0].pop("original_source_utf8")),
        "wrong_original_provenance_sha": ("client_evidence", lambda x: x["sessions"][0].update(source_sha256="0" * 64)),
    }
    for name, (source, mutation) in cases.items():
        ctrl, items, _ = fresh()
        admission = ctrl.prepare(items[0])
        mutate_raw(ctrl.authority.root, source, mutation)
        rejected(name, lambda ctrl=ctrl, admission=admission: ctrl.claim(admission), ctrl.authority.root, True)
    for name, source, raw_change in (
        ("wrong_proxy_source", "proxy_source", lambda raw: raw + "\n# changed\n"),
        ("unexpected_Unix_listener", "unix_sockets", lambda raw: raw + "0000000000000004: 00000002 00000000 00010000 0001 01 777 /tmp/unauthorized.sock\n"),
        ("default_external_route", "routes", lambda raw: raw + "eth0 00000000 01121CAC 0003 0 0 0 00000000 0 0 0\n")):
        ctrl, items, _ = fresh()
        admission = ctrl.prepare(items[0])
        bundle = p.exact_json(ctrl.authority.root / "raw_fixture.json")
        changed = raw_change(bundle["sources"][source]["raw_utf8"])
        rewrite_raw_object(ctrl.authority.root, source, changed)
        if source in ("routes", "unix_sockets"):
            d = a.loads(bundle["sources"]["daemon"]["raw_utf8"].encode())
            d["routes" if source == "routes" else "sockets"] = changed
            rewrite_raw_object(ctrl.authority.root, "daemon", d)
        rejected(name, lambda ctrl=ctrl, admission=admission: ctrl.claim(admission), ctrl.authority.root, True)
    ctrl, items, _ = fresh()
    admission = ctrl.prepare(items[0])
    original = admission.issuance_observation
    bundle = p.exact_json(ctrl.authority.root / "raw_fixture.json")
    sockets = bundle["sources"]["unix_sockets"]["raw_utf8"].replace("3697", "4001").replace("0000000000000003", "0000000000000099")
    rewrite_raw_object(ctrl.authority.root, "unix_sockets", sockets)
    d = a.loads(bundle["sources"]["daemon"]["raw_utf8"].encode())
    d.update(sockets=sockets, ExecIDs=["SYNTHETIC_NEW_EXEC_ID"])
    rewrite_raw_object(ctrl.authority.root, "daemon", d)
    mutate_raw(ctrl.authority.root, "client_census", lambda x: x["sessions"][0].update(socket_inodes=["4001"]))
    mutate_raw(ctrl.authority.root, "client_evidence", lambda x: x["sessions"][0].update(
        original_source_utf8="FRESH_SYNTHETIC_PROVENANCE_BYTES", source_sha256=a.sha(b"FRESH_SYNTHETIC_PROVENANCE_BYTES")))
    rebind_owned_positive_fixture(ctrl.authority.root)
    current = ctrl.authority.observe("PRECLAIM")
    a.require(current["raw_observation_sha256"] != original["raw_observation_sha256"]
              and current["client_evidence_sha256"] != original["client_evidence_sha256"]
              and current["security_projection_sha256"] == original["security_projection_sha256"], "transient turnover identity split")
    claim = ctrl.claim(admission)
    implementation = p.ProductionProvider(ctrl.authority, items[0], claim, admission.receipt_raw)
    state, evidence, reason = implementation.execute_synthetic(p.SyntheticScenario())
    terminal = ctrl.authority.journal().terminal(claim, state=state, evidence=evidence, reason=reason)
    a.require(terminal["state"] == "MATERIALIZED" and claim["receipt_sha256"] == a.sha(admission.receipt_raw), "transient source-pair E2E")
    results["authorized_transient_turnover_preserves_projection"] = {"status": "PASS", "before_raw": original["raw_observation_sha256"], "after_raw": current["raw_observation_sha256"],
        "projection_sha256": current["security_projection_sha256"], "receipt_sha256": claim["receipt_sha256"]}
    results["distinct_raw_security_client_pin_identities"] = {"status": "PASS", "raw": original["raw_observation_sha256"], "security": original["security_projection_sha256"], "client": original["client_evidence_sha256"], "pin": ctrl.authority.pin_sha}
    results["authorized_synthetic_client_census"] = {"status": "PASS", "real_authorization_claimed": False}
    results["independent_provider_revalidation"] = {"status": "PASS", "stages": ["constructor", "execution", "immediately before simulated native solve"], "raw_evidence_files": len(list((ctrl.authority.root / "raw-evidence" / items[0]["base_attempt_id"] / "provider").glob("*.json")))}
    for name, source, mutation in (
        ("provider_topology_mismatch_before_build", "worker", lambda x: x[0].update(ID="WRONG")),
        ("provider_client_mismatch_before_build", "client_evidence", lambda x: x["sessions"][0].update(classification="UNKNOWN"))):
        ctrl, items, _ = fresh()
        admission = ctrl.prepare(items[0])
        claim = ctrl.claim(admission)
        implementation = p.ProductionProvider(ctrl.authority, items[0], claim, admission.receipt_raw)
        mutate_raw(ctrl.authority.root, source, mutation)
        rejected(name, lambda impl=implementation: impl.execute_synthetic(p.SyntheticScenario()), ctrl.authority.root)
        a.require(not (ctrl.authority.root / "attempts").exists(), "provider mismatched gate reached build")
    ctrl, items, _ = fresh()
    admission = ctrl.prepare(items[0])
    claim = ctrl.claim(admission)
    impl = p.ProductionProvider(ctrl.authority, items[0], claim, admission.receipt_raw)
    rejected("arbitrary_callable_synthetic_provider", lambda: impl.execute_synthetic(observations), ctrl.authority.root)
    for name, mutate in (
        ("missing_claim_raw_association", lambda root, claim: (root / "raw-evidence" / claim["attempt_id"] / "preclaim" / (claim["input_runtime_binding"]["raw_evidence_association_sha256"] + ".json")).rename(root / "withheld_raw_association.json")),
        ("corrupt_claim_raw_association", lambda root, claim: Path(root / "raw-evidence" / claim["attempt_id"] / "preclaim" / (claim["input_runtime_binding"]["raw_evidence_association_sha256"] + ".json")).write_bytes(b"{}\n"))):
        ctrl, items, _ = fresh()
        admission = ctrl.prepare(items[0])
        claim = ctrl.claim(admission)
        mutate(ctrl.authority.root, claim)
        rejected(name, lambda ctrl=ctrl, items=items, claim=claim, admission=admission: p.ProductionProvider(ctrl.authority, items[0], claim, admission.receipt_raw), ctrl.authority.root)
    ctrl, items, _ = fresh()
    extra = {"session_id": "SYNTHETIC_INACCESSIBLE_SESSION", "endpoint": "SYNTHETIC_ISOLATED_NAMESPACE",
             "process_identity": "SYNTHETIC_ISOLATED_PROCESS", "control_capable": False, "socket_inodes": []}
    mutate_raw(ctrl.authority.root, "client_census", lambda x: (x["sessions"].append(extra), x["observed_session_ids"].append(extra["session_id"])))
    proof = {"session_id": extra["session_id"], "session_endpoint": extra["endpoint"], "process_identity": extra["process_identity"],
             "source_kind": "INDEPENDENT_SOCKET_ACCESS_RESTRICTIONS", "authenticated_source": True, "correlation_complete": True,
             "classification": "UNABLE_TO_ACCESS_CONTROL_PLANE", "principal": "UNKNOWN", "independent_inaccessibility": True,
             "original_source_utf8": "SYNTHETIC_INDEPENDENT_ISOLATION_BYTES", "source_sha256": a.sha(b"SYNTHETIC_INDEPENDENT_ISOLATION_BYTES")}
    mutate_raw(ctrl.authority.root, "client_evidence", lambda x: x["sessions"].append(proof))
    rebind_owned_positive_fixture(ctrl.authority.root)
    admission = ctrl.prepare(items[0])
    a.require(any(x["classification"] == "UNABLE_TO_ACCESS_CONTROL_PLANE" for x in admission.issuance_observation["client_classifications"]), "inaccessibility not independently established")
    results["independently_inaccessible_synthetic_session"] = {"status": "PASS", "real_authorization_claimed": False}
    ctrl, items, path = fresh()
    rejected("real_constructor_root_injection", lambda: p.Authority(root=ctrl.authority.root), ctrl.authority.root, True)
    rejected("real_constructor_topology_injection", lambda: p.Authority(topology={"authorized": True}), ctrl.authority.root, True)
    rejected("real_controller_authority_injection", lambda: c.ProductionController(authority=ctrl.authority), ctrl.authority.root, True)
    rejected("synthetic_authority_to_live_collector", lambda: p.collect_live_raw(ctrl.authority, "PRECLAIM"), ctrl.authority.root, True)
    class FakeRealProvider:
        class authority:
            mode = p.REAL
    rejected("fake_provider_native_transport_injection", lambda: p.NativeProductionTransport(FakeRealProvider(), None, None, None, ctrl.authority.root / "never-created"), ctrl.authority.root, True)
    for option in ("--synthetic", "--root", "--provider", "--topology", "--effectivity-pin"):
        args = ["--request", str(path), option]
        if option != "--synthetic":
            args.append("UNAUTHORIZED_SELECTOR")
        rejected("production_CLI_" + option.removeprefix("--"), lambda args=args: c.main(args), ctrl.authority.root, True)


def required_coverage(results, rejects):
    obligations = {
        "A": ["restricted_route"], "B": ["NONE_route"], "C": ["receipt_issuance_no_consumption_and_deterministic_sha"],
        "D": ["receipt_contract_schema"], "E": ["distinct_raw_security_client_pin_identities"], "F": ["authorized_synthetic_client_census"],
        "G": ["unknown_active_client"], "H": ["incomplete_client_census"], "I": ["unverifiable_socket_access"],
        "J": ["wrong_enforcement_identity", "stale_topology_sha"], "K": ["wrong_controller_sha", "wrong_provider_sha"],
        "L": ["wrong_canonical_SHA", "wrong_event_3", "missing_effectivity_pin"],
        "M": ["wrong_daemon_image", "wrong_daemon_image_config", "wrong_daemon_platform"],
        "N": ["wrong_worker", "wrong_native_binary"], "O": ["external_daemon_attachment"],
        "P": ["wrong_proxy_source", "wrong_proxy_policy"], "Q": ["unexpected_Unix_listener"],
        "R": ["authorized_transient_turnover_preserves_projection"], "S": ["independent_provider_revalidation"],
        "T": ["provider_topology_mismatch_before_build", "provider_client_mismatch_before_build"],
        "U": ["restricted_route"], "V": ["duplicate_claim", "receipt_reuse", "receipt_post_terminal"],
        "W": ["provider_failure_one_immutable_terminal"],
        "X": ["synthetic_authority_usable_by_real_entry", "copied_installed_Authority_synthetic_interface", "copied_installed_ProductionController_synthetic_interface"],
    }
    for checks in obligations.values():
        a.require(all(results.get(name, rejects.get(name, {})).get("status") in ("PASS", "PASS_REJECTED") for name in checks), "mandatory successor A-X not passed")
    return {letter: {"status": "PASS", "checks": checks, "exact_tested_sources": source_identities()} for letter, checks in obligations.items()}



def bind_fixture_provenance(bundle):
    # Only this test-owned generator constructs synthetic proof bytes. Verification
    # never fills a socket Path or generates a missing independent association.
    values = {name: a.loads(bundle["sources"][name]["raw_utf8"].encode())
              for name in ("client_census", "client_evidence", "socket_access", "listener_inventory")}
    census, evidence, access, inventory = [values[name] for name in
        ("client_census", "client_evidence", "socket_access", "listener_inventory")]
    inventory.update(socket_namespace="SYNTHETIC_DAEMON_NAMESPACE", user_namespace="SYNTHETIC_USER_NS")
    rows = p.parse_socket_rows(bundle["sources"]["unix_sockets"]["raw_utf8"].encode())
    for session in census["sessions"]:
        session.setdefault("socket_namespace", inventory["socket_namespace"])
        session.setdefault("user_namespace", inventory["user_namespace"])
        proof = next(x for x in evidence["sessions"] if x["session_id"] == session["session_id"])
        associated = [row for row in rows if row["St"] == "03" and row["Inode"] in session["socket_inodes"]]
        body = p.endpoint_binding.independent_body(session, proof, associated, access, inventory)
        proof["original_source_utf8"] = a.canonical(body).decode()
        proof["source_sha256"] = a.sha(proof["original_source_utf8"].encode())
    body = {"schema": "V6_INDEPENDENT_ENDPOINT_ACCESS_BOUNDARY_V3",
            "socket_access_sha256": a.identity(access), "socket_namespace": inventory["socket_namespace"],
            "user_namespace": inventory["user_namespace"]}
    evidence["boundary"]["original_source_utf8"] = a.canonical(body).decode()
    evidence["boundary"]["source_sha256"] = a.sha(evidence["boundary"]["original_source_utf8"].encode())
    for name, value in values.items():
        raw = a.canonical(value)
        bundle["sources"][name].update(raw_utf8=raw.decode(), sha256=a.sha(raw))


def rebind_owned_positive_fixture(root):
    path = root / "raw_fixture.json"
    bundle = p.exact_json(path)
    bind_fixture_provenance(bundle)
    # Test-owned source fixture mutation, not a candidate durable artifact write.
    Path(path).write_bytes(p.pretty(bundle))

if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        with (RUN_EVIDENCE / "qualification_failure.json").open("xb") as stream:
            stream.write(p.pretty({"status": "BLOCKED", "exception": type(exc).__name__,
                                  "reason": str(exc), "traceback": traceback.format_exc(),
                                  "no_retry_performed": True, "exact_sources": source_identities()}))
        raise


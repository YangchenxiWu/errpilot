"""Deterministic local synthetic qualification; no Docker/network/real ledger writes.

Every mutation case owns a different synthetic ledger under the requested external
qualification root. Provider fixtures supply local observations, not benchmark
builds. Real transport compilation/commands and scientific code preservation are
checked separately against the exact accepted work, without dispatching it.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from dataclasses import replace
from pathlib import Path

from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a
from evaluation.downstream_benchmark.screening import v6_preparation_ledger as ledger
from evaluation.downstream_benchmark.screening import v6_preparation_runtime as legacy

from . import production_controller_candidate as c
from . import production_provider_candidate as p

OUT = a.ROOT / p.RESUME
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
    items = [synthetic_item("RESTRICTED_A", True), synthetic_item("RESTRICTED_B", True),
             synthetic_item("NONE", False), synthetic_item("FAILURE", True)]
    population = {"schema": "V6_SYNTHETIC_WORK_POPULATION_V1", "namespace": p.SYNTHETIC, "items": items}
    write(root / "population.json", population)
    config = p.frozen_inputs()
    internal = config["internal_network"]
    nid, cid, pid = digest("NETWORK"), digest("DAEMON"), digest("PROXY")
    networks = {internal: {"NetworkID": nid, "IPAddress": "172.28.0.2", "Gateway": ""}}
    daemon = {"Id": cid, "State": {"Running": True, "StartedAt": "SYNTHETIC_INSTANCE_START", "Pid": 101},
        "Config": {"Image": config["runtime_image"]["immutable_reference"]},
        "NetworkSettings": {"Networks": networks}, "HostConfig": {"Dns": ["127.0.0.1"], "PortBindings": {}},
        "Path": "/usr/bin/buildkitd", "Args": ["--debug"],
        "native_binary_sha256": config["client_binary_sha256"], "daemon_binary_sha256": config["daemon_binary_sha256"],
        "image_config_digest": config["runtime_image"]["verified_config_digest"],
        "routes": "SYNTHETIC_INTERNAL_ROUTE_ONLY", "sockets": "SYNTHETIC_UNIX_BUILDKit_SOCKET"}
    proxy = {"Id": pid, "State": {"Running": True, "StartedAt": "SYNTHETIC_INSTANCE_START", "Pid": 102},
        "NetworkSettings": {"Networks": {internal: {"NetworkID": nid, "IPAddress": "172.28.0.3", "Gateway": ""},
            "SYNTHETIC_EXTERNAL": {"NetworkID": digest("EXTERNAL_NETWORK"), "IPAddress": "172.29.0.2"}}},
        "Path": "python", "Args": ["-u", "/qualification_proxy.py"], "HostConfig": {"PortBindings": {}},
        "image_config_digest": p.exact_json(a.ROOT / p.NATIVE / "seven_base_transport_map.json")["mapping"][0]["engine_config_identity"],
        "Config": {"Image": p.exact_json(a.ROOT / p.NATIVE / "seven_base_transport_map.json")["mapping"][0]["scientific_base_authority"]}}
    network = {"Id": nid, "Name": internal, "Internal": True, "Driver": "bridge", "IPAM": {"Config": []},
               "Options": {}, "Containers": {cid: {"Name": "SYNTHETIC_DAEMON"}, pid: {"Name": "SYNTHETIC_PROXY"}}}
    objects = {"daemon": daemon, "proxy": proxy, "network": network,
               "worker": [{"ID": "SYNTHETIC_WORKER", "PLATFORMS": ["linux/amd64"]}]}
    code = (a.ROOT / p.NATIVE / "proxy.py").read_bytes()
    policy_raw = p.pretty(config["proxy"]["policy"])
    for name, value in objects.items():
        write(root / "topology" / (name + ".json"), value)
    write(root / "topology/proxy.py", code)
    write(root / "topology/policy.json", policy_raw)
    observation = p.normalize_topology(objects, code, policy_raw, config)
    canonical = {"namespace": p.SYNTHETIC, "state": "PREPARATION_EXECUTION_AUTHORIZED", "event_3_id": a.sha(b"SYNTHETIC_EVENT_3\n")}
    write(root / "canonical.json", canonical)
    refs = {key: {"path": p.RESUME + name, "sha256": a.sha((OUT / name).read_bytes())} for key, name in (
        ("controller", "production_controller_candidate.py"), ("provider", "production_provider_candidate.py"),
        ("receipt_contract", "production_receipt_authority_contract.json"))}
    payload = {"schema": "V6_SYNTHETIC_PRODUCTION_EFFECTIVITY_FIXTURE_V1", "namespace": p.SYNTHETIC,
        "synthetic_only": True, "HUMAN_PI_ACCEPTED": "NO", "runtime_effective": "NO", "qualification_root": str(root),
        "canonical": {"path": str(root / "canonical.json"), "sha256": a.sha((root / "canonical.json").read_bytes())},
        "event_3_id": canonical["event_3_id"], **refs, "receipt_schema": p.RECEIPT_SCHEMA,
        "enforcement_identity": p.ENFORCEMENT, "population_identity": p.population_identity(population, (root / "population.json").read_bytes()),
        "ledger_binding_identity": {**p.ledger_identity(), "root": str(root / "ledger")}, "live_topology": observation}
    path = root / "synthetic_effectivity_fixture.json"
    write(path, payload)
    return path, items


def observations(item, receipt_raw):
    return "MATERIALIZED", {name: digest(item["base_attempt_id"] + name) for name in ledger.SUCCESS}, ""


def journal_files(root):
    return {n: sorted(x.name for x in (root / "ledger" / n).iterdir()) for n in ("claims", "terminals", "locks")}


def main():
    ledger.safe_path(p.QUALIFICATION_ROOT)
    ledger.mkdir_durable(p.QUALIFICATION_ROOT)
    number = 1
    while (p.QUALIFICATION_ROOT / ("run_" + str(number))).exists():
        number += 1
    run_root = p.QUALIFICATION_ROOT / ("run_" + str(number))
    ledger.mkdir_durable(run_root)
    for name in ("production_controller_candidate.py", "production_provider_candidate.py", "qualify_resume_candidate.py",
                 "production_receipt_authority_contract.json", "receipt_schema.json", "topology_observation_contract.json"):
        write(run_root / "input-source" / name, (OUT / name).read_bytes())
    results, rejects = {}, {}
    counter = 0
    def fresh():
        nonlocal counter
        counter += 1
        path, items = fixture(run_root / ("fixture_" + str(counter)))
        return c.ProductionController.synthetic(path), items, path
    def rejected(name, call, root=None, zero=False):
        before = journal_files(root) if root else None
        try:
            call()
        except (a.Rejected, ValueError, TypeError, KeyError, OSError) as exc:
            if root:
                a.require(before == journal_files(root), "rejection mutated synthetic ledger: " + name)
                if zero:
                    a.require(all(not x for x in before.values()), "preclaim fixture already consumed")
            rejects[name] = {"status": "PASS_REJECTED", "reason": str(exc),
                             "ledger_unchanged": root is not None, "zero_claims_preclaim": zero}
        else:
            raise AssertionError("unexpected acceptance: " + name)
    controller, items, primary_fixture = fresh()
    root = controller.authority.root
    admitted = controller.prepare(items[0])
    write(root / "issued-receipt.json", admitted.receipt_raw)
    a.require((root / "issued-receipt.json").read_bytes() == admitted.receipt_raw, "receipt canonical readback")
    from jsonschema import Draft202012Validator
    Draft202012Validator(p.exact_json(OUT / "receipt_schema.json")).validate(a.loads(admitted.receipt_raw))
    a.require(all(not x for x in journal_files(root).values()), "issuance consumed attempt")
    a.require(admitted.receipt_raw == controller.prepare(items[0]).receipt_raw, "receipt SHA nondeterministic")
    results["receipt_issuance_no_consumption_and_deterministic_sha"] = {"status": "PASS", "receipt_sha256": a.sha(admitted.receipt_raw)}
    claim = controller.claim(admitted)
    a.require(claim["receipt_sha256"] == a.sha(admitted.receipt_raw), "durable receipt SHA missing")
    provider = p.ProductionProvider(controller.authority, items[0], claim, admitted.receipt_raw)
    state, evidence, reason = provider.execute_synthetic(observations)
    terminal = controller.authority.journal().terminal(claim, state=state, evidence=evidence, reason=reason)
    results["restricted_route"] = {"status": "PASS", "claim_sha256": a.identity(claim), "terminal_sha256": a.identity(terminal)}
    rejected("receipt_post_terminal", lambda: p.ProductionProvider(controller.authority, items[0], claim, admitted.receipt_raw), root)
    rejected("terminal_overwrite", lambda: controller.authority.journal().terminal(claim, state=state, evidence=evidence), root)
    rejected("receipt_reuse", lambda: controller.claim(admitted), root)
    rejected("duplicate_claim", lambda: controller.claim(admitted), root)
    rejected("retry", lambda: c.request_retry(), root)
    none_admission = controller.prepare(items[2])
    a.require(none_admission.receipt_raw is None and none_admission.binding["receipt_sha256"] is None, "NONE semantics")
    none_terminal = controller.run_synthetic(items[2], observations)
    none_claim = controller.authority.journal()._read(controller.authority.journal()._path("claims", items[2]["base_attempt_id"]))
    a.require(none_claim["receipt_sha256"] is None and none_terminal["state"] == "MATERIALIZED", "NONE successful route")
    results["NONE_route"] = {"status": "PASS", "receipt_sha256": None}
    def fail(item, raw):
        raise RuntimeError("SYNTHETIC_PROVIDER_FAILURE")
    failure = controller.run_synthetic(items[3], fail)
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
        "runtime_authority_false": ("runtime_authority", False), "wrong_allowed_origins": ("allowed_origins", ["pypi.org:443"]),
        "broader_allowlist": ("allowed_origins", p.ORIGINS + ["example.org:443"]),
        "stale_topology_sha": ("live_daemon_topology_observation_sha256", "0" * 64),
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
        path.write_bytes(p.pretty(data))
        rejected(name, lambda ctrl=ctrl, xs=xs: ctrl.prepare(xs[0]), ctrl.authority.root, True)
    ctrl, xs, path = fresh()
    absent = path.parent / "absent_effectivity.json"
    rejected("missing_effectivity_pin", lambda: c.ProductionController.synthetic(absent), ctrl.authority.root, True)
    ctrl, xs, path = fresh()
    admission = ctrl.prepare(xs[0])
    daemon_path = ctrl.authority.root / "topology/daemon.json"
    data = a.loads(daemon_path.read_bytes())
    data["State"]["Pid"] += 1
    daemon_path.write_bytes(p.pretty(data))
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
    claim_path.write_bytes(a.canonical(wrong_claim))  # Owned corruption fixture, never real ledger.
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
    for module, name, method in ((c, "production_controller_candidate.py", "ProductionController"),
                                 (p, "production_provider_candidate.py", "Authority")):
        copy_path = run_root / "copied-production-entry" / name
        write(copy_path, Path(module.__file__).read_bytes())
        spec = importlib.util.spec_from_file_location("copy_" + method, copy_path)
        copied = importlib.util.module_from_spec(spec)
        import sys
        sys.modules[spec.name] = copied
        spec.loader.exec_module(copied)
        rejected("copied_installed_" + method + "_synthetic_interface", lambda copied=copied, method=method: getattr(copied, method).synthetic(path))
    # Pure production status validator is shared with the real installed loader;
    # these dictionaries are never persisted as accepted production authority.
    status = {"schema": "V6_PREPARATION_PRODUCTION_RUNTIME_EFFECTIVITY_V1", "candidate_only": False,
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
    # Bind unchanged shared code objects through the new seam without I/O.
    transport = object.__new__(p.NativeProductionTransport)
    engine = p.shared_scientific_engine(transport)
    for name in ("_materialize_checked", "build_definition", "context_manifest", "identity", "transport_source_package", "inspect_final"):
        a.require(getattr(engine, name).__code__ is getattr(a.shared, name).__code__, "shared scientific code object drift")
    results["shared_scientific_code_objects_preserved"] = {"status": "PASS", "frozen_dispatch_guards": "UNCHANGED"}
    results["receipt_contract_schema"] = {"status": "PASS", "canonical_roundtrip": True, "byte_sha_binding": True, "NONE_receipt": "PROHIBITED"}
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
    write(run_root / "qualification_results.json", summary)
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()

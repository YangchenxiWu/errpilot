"""Produce the exact source pair from byte-preserved technical predecessors."""
from __future__ import annotations

from .construct_resume import CORRECTED, HERE, OLD, PREFIX, replace_functions


def main():
    source = (CORRECTED / "corrected_production_provider_candidate.py").read_text()
    source = source.replace('RESUME = "evaluation/downstream_benchmark/evidence/v6_preparation_execution_production_runtime_installation_resume_v1/"', f'RESUME = "{PREFIX}"')
    source = source.replace('production_runtime_installation_resume_v1"', 'production_runtime_topology_stability_successor_resume_v1"')
    source = source.replace('v6_preparation_production_controller.py', 'v6_preparation_production_controller_v2.py')
    source = source.replace('v6_preparation_production_provider.py', 'v6_preparation_production_provider_v2.py')
    source = source.replace('RUNTIME_EFFECTIVITY_V1', 'RUNTIME_EFFECTIVITY_V2').replace('RUNTIME_EFFECTIVITY_ACCEPTANCE_PIN_V1', 'RUNTIME_EFFECTIVITY_ACCEPTANCE_PIN_V2')
    source = source.replace('RUNTIME_INSTALLATION_AUTHORITY_V1', 'RUNTIME_INSTALLATION_AUTHORITY_V2').replace('RUNTIME_V1"', 'RUNTIME_V2"')
    source = source.replace('RECEIPT_AUTHORITY_CONTRACT_V1', 'RECEIPT_AUTHORITY_CONTRACT_V2')
    source = source.replace('RECEIPT_SCHEMA = "V6_RESTRICTED_BUILD_EGRESS_ENFORCEMENT_RECEIPT_V1"', 'RECEIPT_SCHEMA = "V6_RESTRICTED_BUILD_EGRESS_ENFORCEMENT_RECEIPT_V2_CANDIDATE"')
    source = source.replace('SYNTHETIC = "SYNTHETIC_PRODUCTION_RUNTIME_QUALIFICATION"', 'SYNTHETIC = "SYNTHETIC_TOPOLOGY_STABILITY_SUCCESSOR_V2_QUALIFICATION"')
    source = source.replace('"live_daemon_topology_observation_sha256"}', '"security_projection_sha256", "candidate_only", "provider_independent_freshness_required",\n    "client_authorization_verdict", "client_authorization_evidence_sha256", "client_authorization_policy_sha256"}')
    source = source.replace('"production_controller_candidate.py"', '"production_controller_successor_candidate.py"').replace('"production_provider_candidate.py"', '"production_provider_successor_candidate.py"')
    source = source.replace('"production_receipt_authority_contract.json"', '"receipt_authority_contract_v2_candidate.json"')
    source = source.replace('"V6_SYNTHETIC_PRODUCTION_EFFECTIVITY_FIXTURE_V1"', '"V6_SYNTHETIC_SUCCESSOR_EFFECTIVITY_FIXTURE_V2"')
    source = source.replace('"live_topology", "base_layouts")', '"live_topology", "base_layouts", "security_contracts", "live_evidence_observer", "accepted_client_principals")')
    source = source.replace('"V6_RECEIPT_BOUND_CLAIM_ADAPTER_V1"', '"V6_RECEIPT_BOUND_CLAIM_ADAPTER_V2"')
    source = source.replace('"record_extension": ["receipt_sha256"]', '"record_extension": ["receipt_sha256", "input_runtime_binding.raw_evidence_association_sha256"]')
    source = source.replace('a.require(p["receipt_schema"] == RECEIPT_SCHEMA and p["enforcement_identity"] == ENFORCEMENT,', 'a.require(p["receipt_schema"] == (REAL_RECEIPT_SCHEMA if self.mode == REAL else RECEIPT_SCHEMA) and p["enforcement_identity"] == ENFORCEMENT,')
    source = source.replace('a.require(contract["receipt_schema"] == RECEIPT_SCHEMA and contract["allowed_origins"] == ORIGINS,', 'a.require(contract["receipt_schema"] == RECEIPT_SCHEMA and contract["future_production_schema"] == REAL_RECEIPT_SCHEMA and contract["allowed_origins"] == ORIGINS,')
    source = source.replace('        return self\n\n    def journal', '        verify_security_contracts(self)\n        return self\n\n    def journal')
    source = source.replace('        self.manifest = {}', '        self.manifest = exact_json(self.root / "scientific_manifest.json")')
    source = source.replace('        return {}\n\n    def observe', '        return synthetic_plan(self, item)\n\n    def observe')
    source = replace_functions(source, {
        'Authority.__init__': '''def __init__(self, *, _qualification_fixture=None):
    a.require(type(self) is Authority, "authority subtype forbidden")
    if _qualification_fixture is None:
        a.require(Path(__file__).resolve() == a.ROOT / PROVIDER_TARGET,
                  "candidate source is not installed production provider")
        self.mode, self.root = REAL, a.OUTPUT_ROOT
    else:
        a.require(Path(__file__).resolve() == a.ROOT / RESUME / "production_provider_successor_candidate.py",
                  "synthetic interface unavailable from installed/copied production source")
        ledger.safe_path(_qualification_fixture)
        a.require(_qualification_fixture.is_relative_to(QUALIFICATION_ROOT), "synthetic authority outside qualification")
        self.mode, self.fixture_path = SYNTHETIC, _qualification_fixture
    self.refresh()''',
        'Authority.synthetic': '''@classmethod
def synthetic(cls, fixture_path):
    a.require(cls is Authority, "synthetic authority subtype forbidden")
    return cls(_qualification_fixture=fixture_path)''',
        'Authority.observe': '''def observe(self, stage="ISSUANCE"):
    if self.mode == SYNTHETIC:
        a.require(Path(__file__).resolve() == a.ROOT / RESUME / "production_provider_successor_candidate.py",
                  "synthetic observation forbidden outside exact candidate source")
        bundle = exact_json(self.root / "raw_fixture.json")
        a.require(bundle["namespace"] == SYNTHETIC and bundle["synthetic_only"] is True,
                  "synthetic raw cannot assert live evidence")
    else:
        bundle = collect_live_raw(self, stage)
    result = verify_raw_security(bundle, self.config, stage=stage, synthetic=self.mode == SYNTHETIC,
                                 accepted_principals=self.payload["accepted_client_principals"])
    a.require(a.canonical(result["security_projection"]) == a.canonical(self.payload["live_topology"]),
              "stale or mismatched live topology/security projection")
    return result''',
        'receipt_value': '''def receipt_value(authority, item, observation):
    a.require(item["build_network_required"] is True, "receipt prohibited for NONE")
    p = authority.payload
    synthetic = authority.mode == SYNTHETIC
    return {"schema": RECEIPT_SCHEMA if synthetic else REAL_RECEIPT_SCHEMA, "runtime_authority": not synthetic,
        "candidate_only": synthetic, "provider_independent_freshness_required": True,
        "canonical_state_sha256": p["canonical"]["sha256"], "event_3_id": p["event_3_id"],
        "production_runtime_effectivity_pin_sha256": authority.pin_sha,
        "controller_source_sha256": p["controller"]["sha256"], "provider_source_sha256": p["provider"]["sha256"],
        "receipt_contract_sha256": p["receipt_contract"]["sha256"], "enforcement_identity": p["enforcement_identity"],
        "base_attempt_id": item["base_attempt_id"], "work_item_identity": copy.deepcopy(item),
        "network_mode": "RESTRICTED_DEFAULT", "allowed_origins": list(ORIGINS),
        "security_projection_sha256": observation["security_projection_sha256"],
        "client_authorization_verdict": observation["client_verdict"],
        "client_authorization_evidence_sha256": observation["client_evidence_sha256"],
        "client_authorization_policy_sha256": p["security_contracts"]["client_authorization_contract_candidate.json"]["sha256"]}''',
        'verify_receipt': '''def verify_receipt(authority, item, raw, observation, *, issuance=None):
    if not item["build_network_required"]:
        a.require(raw is None, "NONE receipt present")
        return None
    a.require(isinstance(raw, bytes), "restricted receipt null/missing")
    value = a.loads(raw)
    a.require(set(value) == RECEIPT_FIELDS and raw == a.canonical(value), "wrong/noncanonical receipt bytes/schema fields")
    expected = receipt_value(authority, item, observation)
    if issuance is not None:
        a.require(issuance["security_projection_sha256"] == observation["security_projection_sha256"]
                  and issuance["client_verdict"] == observation["client_verdict"], "fresh issuance/projection/client mismatch")
        expected["client_authorization_evidence_sha256"] = issuance["client_evidence_sha256"]
    a.require(a.canonical(value) == a.canonical(expected), "receipt semantic binding/schema/reuse/freshness mismatch")
    return a.sha(raw)''',
        'ReceiptBoundLedger.claim': '''def claim(self, attempt, binding, *, permit=None):
    a.require(isinstance(permit, legacy.Admission) and type(permit).__name__ == "ProductionAdmission"
              and permit.item["base_attempt_id"] == attempt and permit.binding == binding,
              "versioned real/synthetic claim requires production Admission")
    a.require(permit.controller.authority.mode == self.namespace
              and permit.controller.authority.root == self.root
              and binding["effectivity_pin_sha256"] == self.authority.pin_sha,
              "permit namespace/root/effectivity does not belong to ledger")
    fresh = permit.revalidate()
    digest = binding["receipt_sha256"]
    a.require(digest is None if not permit.item["build_network_required"] else
              isinstance(digest, str) and a.shared.HEX64.fullmatch(digest), "claim receipt binding")
    a.require(digest == (a.sha(permit.receipt_raw) if permit.receipt_raw is not None else None), "claim receipt SHA mismatch")
    a.require(self.state(attempt) == "UNSTARTED", "duplicate claim/no automatic retry")
    # The new immutable association is fully durable/read back before the original lock.
    association = publish_raw_association(self.authority, permit.item, permit.receipt_raw, fresh,
                                          permit.issuance_observation, stage="PRECLAIM")
    owner = uuid.uuid4().hex
    body = {"namespace": self.namespace, "attempt_id": attempt, "owner": owner}
    ledger.exclusive_write(self._path("locks", attempt), a.canonical(body))
    a.require(not self._path("terminals", attempt).exists(), "terminal before claim")
    record = {**body, "operation": "CLAIM", "input_runtime_binding": {**binding, "raw_evidence_association_sha256": association},
              "state": "CLAIMED_NO_TERMINAL", "attempt_consumed": True, "receipt_sha256": digest}
    ledger.exclusive_write(self._path("claims", attempt), a.canonical(record))
    return record''',
        'verify_claim': '''def verify_claim(authority, item, claim, raw):
    a.require(type(authority) is Authority, "unrecognized provider authority")
    authority.refresh()
    authority.select(item)
    journal = authority.journal()
    a.require(a.canonical(journal._read(journal._path("claims", item["base_attempt_id"]))) == a.canonical(claim),
              "durable claim differs from supplied claim")
    a.require(journal.state(item["base_attempt_id"]) == "CLAIMED_NO_TERMINAL", "receipt after terminal/reuse")
    issuance = read_claim_association(authority, item, claim, raw)
    observation = authority.observe("PROVIDER_PREBUILD")
    digest = verify_receipt(authority, item, raw, observation, issuance=issuance)
    a.require(claim["attempt_id"] == item["base_attempt_id"]
              and claim["receipt_sha256"] == claim["input_runtime_binding"]["receipt_sha256"] == digest,
              "provider receipt SHA must equal exact durable claim SHA")
    expected = {"item": item, "effectivity_pin_sha256": authority.pin_sha,
                "receipt_sha256": digest, "security_projection_sha256": observation["security_projection_sha256"]}
    a.require(all(a.canonical(claim["input_runtime_binding"].get(k)) == a.canonical(v) for k, v in expected.items()), "claim work/runtime binding")
    publish_raw_association(authority, item, raw, observation, issuance, stage="PROVIDER_PREBUILD")
    return observation["security_projection"]''',
        'NativeProductionTransport.__init__': '''def __init__(self, provider, compiled, binding, layout, artifact_root):
    a.require(type(provider) is ProductionProvider and type(provider.authority) is Authority
              and provider.authority.mode == REAL and Path(__file__).resolve() == a.ROOT / PROVIDER_TARGET,
              "native production transport requires exact installed provider and real authority")
    self.provider, self.compiled, self.binding = provider, compiled, binding
    self.layout, self.root, self.used = layout, artifact_root, False''',
        'ProductionProvider.execute_synthetic': '''def execute_synthetic(self, scenario):
    a.require(self.authority.mode == SYNTHETIC
              and Path(__file__).resolve() == a.ROOT / RESUME / "production_provider_successor_candidate.py"
              and type(scenario) is SyntheticScenario, "synthetic test provider unavailable from installed real entry")
    verify_claim(self.authority, self.item, self.claim, self.receipt_raw)
    plan = self.authority.select(self.item)
    normalized_item = a.work_item(plan, self.item["variant"])
    values = a.embedded_inputs(self.authority.manifest, plan)
    for key, relative in a.input_paths(self.item).items():
        if values[key] is not None:
            path = self.authority.root / relative
            ledger.mkdir_durable(path.parent)
            ledger.exclusive_write(path, values[key])
    proposal = a.engine_call_proposal(self.authority.manifest, normalized_item)
    fixture = copy.deepcopy(proposal["fixture"])
    for key, relative in a.input_paths(self.item).items():
        if key in fixture:
            fixture[key] = relative
    compiled = compile_production_transport(normalized_item, plan, self.topology, receipt_raw=self.receipt_raw)
    compiled["base_attempt_id"] = self.item["base_attempt_id"]
    output = self.authority.root / "attempts" / self.item["base_attempt_id"]
    transport = SyntheticScientificTransport(self, compiled, a.engine_recipe(plan), scenario)
    # The accepted shared scientific code object is invoked through our bounded
    # transport. False selects the original checked scientific path, not real I/O:
    # the owning transport, IDs, root, and constructor all remain synthetic.
    result = shared_scientific_engine(transport)._materialize_checked(fixture, output=output,
                input_root=self.authority.root, synthetic_only=False, single_identity=True)
    ledger.exclusive_write(output / "candidate_scientific_run.json", a.canonical({
        "schema": "V6_CANDIDATE_HERMETIC_SCIENTIFIC_RUN_V2", "synthetic_only": True,
        "real_build": False, "real_authorization": False,
        "shared_checked_path_argument": False, "meaning": "Original checked scientific path through bounded simulated I/O; no real materialization"}))
    hashes = ledger.persist_tree(output)
    evidence = {"artifact_sha256": hashes, "synthetic_only": True, "real_build": False,
                "shared_scientific_code_sha256": a.sha(a.shared._materialize_checked.__code__.co_code),
                "receipt_sha256": self.claim["receipt_sha256"], "synthetic_transport_calls": transport.calls}
    if result["status"] == "MATERIALIZED":
        r = result["revisions"][0]
        evidence.update(dict(zip(ledger.SUCCESS, (r["dockerfile_sha256"], r["build_context_manifest_sha256"],
            a.sha(b"ABSENT\\n"), r["build_log_sha256"], r["image_inspect_sha256"], a.identity(r["observed_python"]),
            r["installed_distribution_manifest_sha256"], r["environment_identity_sha256"]))))
    return result["status"], evidence, result.get("reason", "")''',
    })
    source = source.replace('a.require(isinstance(transport, NativeProductionTransport), "accepted native transport required")',
                            'a.require(type(transport) in (NativeProductionTransport, SyntheticScientificTransport), "accepted native transport required")')
    source = source.replace('        ledger.safe_path(authority.root)\n        a.require(authority.mode', '        a.require(type(authority) is Authority, "unrecognized ledger authority")\n        ledger.safe_path(authority.root)\n        a.require(authority.mode')
    source += (HERE / "provider_v2_extension.txt").read_text()
    (HERE / "production_provider_successor_candidate.py").write_text(source)
    source = (OLD / "production_controller_candidate.py").read_text()
    source = source.replace('evaluation/downstream_benchmark/evidence/v6_preparation_execution_production_runtime_installation_resume_v1/', PREFIX)
    source = source.replace('v6_preparation_execution_production_runtime_installation_resume_v1.production_provider_candidate',
                            'v6_production_runtime_topology_stability_successor_resume_v1.production_provider_successor_candidate')
    source = source.replace('v6_preparation_production_controller.py', 'v6_preparation_production_controller_v2.py').replace('v6_preparation_production_provider"', 'v6_preparation_production_provider_v2"')
    source = source.replace('production_controller_candidate.py', 'production_controller_successor_candidate.py')
    source = source.replace('    receipt_raw: bytes | None', '    receipt_raw: bytes | None\n    issuance_observation: dict = field(compare=False, repr=False)')
    source = replace_functions(source, {
        'ProductionController.__init__': '''def __init__(self, *, _qualification_fixture=None):
    a.require(type(self) is ProductionController, "controller subtype forbidden")
    if _qualification_fixture is None:
        a.require(Path(__file__).resolve() == a.ROOT / CONTROLLER_TARGET,
                  "candidate controller is not an installed real production entry")
        self.authority = provider.Authority()
    else:
        a.require(Path(__file__).resolve() == a.ROOT / RESUME / "production_controller_successor_candidate.py",
                  "synthetic authority cannot enter installed/copied production controller")
        self.authority = provider.Authority.synthetic(_qualification_fixture)''',
        'ProductionController.synthetic': '''@classmethod
def synthetic(cls, fixture_path):
    a.require(cls is ProductionController, "synthetic controller subtype forbidden")
    return cls(_qualification_fixture=fixture_path)''',
        'ProductionAdmission.revalidate': '''def revalidate(self):
    a.require(type(self.controller) is ProductionController, "unbound production permit")
    observed = self.controller.prepare(self.item, _retained_receipt=self.receipt_raw,
                                       _issuance=self.issuance_observation, _stage="PRECLAIM")
    a.require(a.canonical(observed.manifest) == a.canonical(self.manifest)
              and a.canonical(observed.plan) == a.canonical(self.plan)
              and a.canonical(observed.item) == a.canonical(self.item)
              and a.canonical(observed.binding) == a.canonical(self.binding)
              and observed.receipt_raw == self.receipt_raw, "admission/receipt changed before durable claim")
    return observed.issuance_observation''',
        'ProductionController.prepare': '''def prepare(self, item, *, _retained_receipt=None, _issuance=None, _stage="ISSUANCE"):
    """Fresh read-only admission; receipt issuance consumes no attempts."""
    authority = self.authority.refresh()
    plan = authority.select(item)
    journal = authority.journal()
    a.require(journal.state(item["base_attempt_id"]) == "UNSTARTED", "receipt after claim/terminal; no retry/reuse")
    observation = authority.observe(_stage)
    source_presence, base_probe = {}, {}
    if authority.mode == provider.REAL:
        a.embedded_inputs(authority.manifest, plan)
        exporter = legacy.source_function(plan, item)
        labels = ("BUGGY", "FIXED") if item["variant"] == "SOURCE_INDEPENDENT" else (item["variant"],)
        source_presence = {label: exporter(a.engine_recipe(plan), label) for label in labels}
        base_probe = legacy.shared_engine().verify_base(a.engine_recipe(plan))
    raw = _retained_receipt if _issuance is not None else (
        a.canonical(provider.receipt_value(authority, item, observation)) if item["build_network_required"] else None)
    digest = provider.verify_receipt(authority, item, raw, observation, issuance=_issuance)
    binding = {"item": copy.deepcopy(item), "effectivity_pin_sha256": authority.pin_sha,
        "receipt_sha256": digest, "security_projection_sha256": observation["security_projection_sha256"],
        "source_presence_identities": source_presence, "base_probe": base_probe}
    return ProductionAdmission(authority.manifest, plan, copy.deepcopy(item), binding, self, raw, observation)''',
    })
    (HERE / "production_controller_successor_candidate.py").write_text(source)


if __name__ == "__main__":
    main()

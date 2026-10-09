"""Candidate controller: real entry requires exact future installation/effectivity.

ProductionAdmission preserves the owning Admission interface and revalidates the
independent successor authority, sources, work, local inputs and topology before
the versioned exclusive durable claim. No real work is enabled by this artifact.
"""
from __future__ import annotations

import argparse
import copy
import importlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a
from evaluation.downstream_benchmark.screening import v6_preparation_ledger as ledger
from evaluation.downstream_benchmark.screening import v6_preparation_runtime as legacy

RESUME = "evaluation/downstream_benchmark/evidence/v6_production_runtime_topology_stability_successor_resume_v1/"
CONTROLLER_TARGET = "evaluation/downstream_benchmark/screening/v6_preparation_production_controller_v2.py"
if Path(__file__).resolve() == a.ROOT / CONTROLLER_TARGET:
    provider = importlib.import_module("evaluation.downstream_benchmark.screening.v6_preparation_production_provider_v2")
else:
    provider = importlib.import_module("evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_resume_v1.production_provider_successor_candidate")


@dataclass(frozen=True)
class ProductionAdmission(legacy.Admission):
    controller: object = field(compare=False, repr=False)
    receipt_raw: bytes | None
    issuance_observation: dict = field(compare=False, repr=False)

    def revalidate(self):
        a.require(type(self.controller) is ProductionController, "unbound production permit")
        observed = self.controller.prepare(self.item, _retained_receipt=self.receipt_raw,
                                           _issuance=self.issuance_observation, _stage="PRECLAIM")
        a.require(a.canonical(observed.manifest) == a.canonical(self.manifest)
                  and a.canonical(observed.plan) == a.canonical(self.plan)
                  and a.canonical(observed.item) == a.canonical(self.item)
                  and a.canonical(observed.binding) == a.canonical(self.binding)
                  and observed.receipt_raw == self.receipt_raw, "admission/receipt changed before durable claim")
        return observed.issuance_observation
        # No network/authority provider is called between this check and exclusive lock.


class ProductionController:
    def __init__(self, *, _qualification_fixture=None):
        a.require(type(self) is ProductionController, "controller subtype forbidden")
        if _qualification_fixture is None:
            a.require(Path(__file__).resolve() == a.ROOT / CONTROLLER_TARGET,
                      "candidate controller is not an installed real production entry")
            self.authority = provider.Authority()
        else:
            a.require(Path(__file__).resolve() == a.ROOT / RESUME / "production_controller_successor_candidate.py",
                      "synthetic authority cannot enter installed/copied production controller")
            self.authority = provider.Authority.synthetic(_qualification_fixture)

    @classmethod
    def synthetic(cls, fixture_path):
        a.require(cls is ProductionController, "synthetic controller subtype forbidden")
        return cls(_qualification_fixture=fixture_path)

    def prepare(self, item, *, _retained_receipt=None, _issuance=None, _stage="ISSUANCE"):
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
        return ProductionAdmission(authority.manifest, plan, copy.deepcopy(item), binding, self, raw, observation)

    def claim(self, admission):
        a.require(type(admission) is ProductionAdmission and admission.controller is self,
                  "foreign production Admission")
        return self.authority.journal().claim(admission.item["base_attempt_id"], admission.binding, permit=admission)

    def run(self, item):
        a.require(self.authority.mode == provider.REAL, "synthetic authority usable by real production entry forbidden")
        a.require(Path(__file__).resolve() == a.ROOT / CONTROLLER_TARGET, "real production source path")
        admission = self.prepare(item)
        claim = self.claim(admission)
        return self._after_claim(admission, claim)

    def run_synthetic(self, item, fixture_provider):
        a.require(self.authority.mode == provider.SYNTHETIC
                  and Path(__file__).resolve() == a.ROOT / RESUME / "production_controller_successor_candidate.py",
                  "installed production entry cannot invoke synthetic interface")
        admission = self.prepare(item)
        claim = self.claim(admission)
        return self._after_claim(admission, claim, fixture_provider=fixture_provider)

    def _after_claim(self, admission, claim, *, fixture_provider=None):
        journal = self.authority.journal()
        try:
            implementation = provider.ProductionProvider(self.authority, admission.item, claim, admission.receipt_raw)
            if self.authority.mode == provider.SYNTHETIC:
                state, evidence, reason = implementation.execute_synthetic(fixture_provider)
            else:
                a.require(fixture_provider is None, "test interface forbidden in production")
                state, evidence, reason = implementation.execute()
            evidence = {**evidence, "receipt_sha256": claim["receipt_sha256"]}
        except (Exception, KeyboardInterrupt) as exc:
            state, reason = "INTERRUPTED", "provider interrupted; no automatic retry"
            evidence = {"failure_type": type(exc).__name__, "detail": str(exc), "receipt_sha256": claim["receipt_sha256"]}
            for relative in ("attempts", "transport", "inputs", "snapshots"):
                path = self.authority.root / relative / admission.item["base_attempt_id"]
                if path.is_dir():
                    evidence[relative + "_artifact_sha256"] = ledger.persist_tree(path)
        # Publication failure is outside the catch: never try a second terminal.
        return journal.terminal(claim, state=state, evidence=evidence, reason=reason)


def request_operation(operation):
    a.require(operation == "PREPARATION", "source acquisition/oracle/allocation/repair/frozen mutation/retry forbidden")


def request_retry(*args, **kwargs):
    raise a.Rejected("retry prohibited; separate later Human-PI authority required")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        # CLI never accepts a synthetic mode, authority object, fixture provider,
        # effectivity SHA, root, topology object, namespace or transport selector.
        controller = ProductionController()
        result = controller.run(a.loads(args.request.read_bytes()))
    except (a.Rejected, OSError, KeyError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "REJECT", "reason": str(exc)}))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0 if result["state"] == "MATERIALIZED" else 1


if __name__ == "__main__":
    raise SystemExit(main())

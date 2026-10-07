"""Explicit single-item V6 dispatch; import, selection and preflight never claim.

The runtime acceptance authorizes implementation/qualification only. Dispatch
also requires a separately installed execution descriptor, independent pin,
reviewed runtime installation and clean committed local/live identities.
Restricted default-network builds remain blocked until an authorized scoped
enforcement integration is installed; a self-asserted qualification cannot open it.
"""
from __future__ import annotations

import argparse
import copy
import json
import subprocess
import types
from dataclasses import dataclass
from pathlib import Path

from jsonschema import Draft202012Validator

from . import materialize_expansion_block_02_batch as snapshots
from . import v6_preparation_adapter as a
from . import v6_preparation_ledger as ledger

PACKAGE = "evaluation/downstream_benchmark/evidence/v6_preparation_execution_activation_v1/"
AUTHORITY = "evaluation/downstream_benchmark/V6_PREPARATION_EXECUTION_RUNTIME_AUTHORITY_ACCEPTANCE_V1.json"
AUTHORITY_SHA = "5bff21c82ad11a80882a160c4dfb79e06bd4c249f769424d5047493fdf442861"
INSTALLATION = "evaluation/downstream_benchmark/V6_PREPARATION_EXECUTION_RUNTIME_INSTALLATION_V1.json"
EXECUTION_PIN = "evaluation/downstream_benchmark/V6_PREPARATION_EXECUTION_EFFECTIVE_DESCRIPTOR_ACCEPTANCE_PIN_V1.json"
WORK_SHA = "288eaed9f7e9ff4daf2978e7c41b6c6ead83e9d99b9ddee7801c163153bd63bb"
AUTH_CANDIDATE_SHA = "13c4c6753263b0657bca1c49122f4f73e27254c5c5d30e7d4c158f9782cf6360"
POPULATION_SHA = "f3a719f2a92f1d1ba96baa9dd3936e8bd87d330f048542c9ee5cfce86185a800"
POLICY = {
    "fallback": "NONE", "stop_at_capacity": False, "automatic_retry": False,
    "automatic_rescue": False, "governed_batches": False,
    "source_acquisition": False, "setup_normalization": False,
    "recipe_mutation": False, "oracle_execution": False, "execution_network": "NONE",
    "predecessor_token": None,
}
IMPLEMENTATION = (
    "evaluation/downstream_benchmark/screening/v6_preparation_adapter.py",
    "evaluation/downstream_benchmark/screening/v6_preparation_runtime.py",
    "evaluation/downstream_benchmark/screening/v6_preparation_ledger.py",
)


def population():
    return a.loads(a.read_exact(PACKAGE + "work_items_candidate.json", WORK_SHA))


def select(*, descriptor_path, descriptor_sha, manifest_path, manifest_sha,
           ordinal, case_id, plan_sha, base_attempt_id):
    """Require every accepted identity; no directory, latest or capacity selection."""
    _, manifest = a.load_inputs(current_path=descriptor_path, current_sha=descriptor_sha,
                                manifest_path=manifest_path, manifest_sha=manifest_sha)
    plan = a.select(manifest, ordinal=ordinal, case_id=case_id, plan_sha=plan_sha)
    items = [x for x in population()["items"] if x["base_attempt_id"] == base_attempt_id]
    a.require(len(items) == 1, "wrong base attempt ID")
    item = items[0]
    a.require((item["census_order"], item["case_id"], item["plan_sha256"])
              == (ordinal, case_id, plan_sha), "wrong ordinal/case/plan/attempt binding")
    a.require(item == a.work_item(plan, item["variant"]), "frozen recipe/work identity changed")
    return manifest, plan, copy.deepcopy(item)


def validate_acceptance(record, *, network_required):
    expected = a.loads(a.read_exact(AUTHORITY, AUTHORITY_SHA))
    a.require(a.canonical(record) == a.canonical(expected), "missing/wrong runtime acceptance")
    candidates = a.loads(a.read_exact(PACKAGE + "authority_candidates.json", AUTH_CANDIDATE_SHA))
    a.require(record["common_binding_sha256"] == candidates["common_binding_sha256"]
              and record["population_semantic_sha256"] == POPULATION_SHA,
              "runtime common binding mismatch")
    for scope, candidate in candidates["separate_permissions"].items():
        a.require(record["separate_permissions"].get(scope) == {
            "HUMAN_PI_ACCEPTED": "YES", "candidate_semantic_sha256": a.identity(candidate)},
            "missing/wrong " + scope + " authority")
    for ref in candidates["common_binding"]["shared_mechanics"].values():
        a.read_exact(ref["path"], ref["sha256"])
    a.require(record["persistent_output_root"] == str(a.OUTPUT_ROOT)
              and record["SOURCE_ACQUISITION_AUTHORIZED"] == "NO", "output/source authority")
    a.require(record["BUILD_NETWORK_EFFECTIVITY"] ==
              "REQUIRES_DENY_BY_DEFAULT_EGRESS_PROVISIONING_AND_QUALIFICATION",
              "network condition changed")
    return candidates


def _git(*args):
    result = subprocess.run(["git", *args], cwd=a.ROOT, capture_output=True, check=False)
    a.require(result.returncode == 0, "required read-only Git identity unavailable")
    return result.stdout


def validate_execution_descriptor(raw, pin, installation):
    """Consume only the exact future three-leaf transition from the accepted baseline."""
    baseline, _ = a.load_inputs()
    d = a.loads(raw)
    schema = a.loads((a.B / "v6_contract_schemas/V6_CAPACITY_CURRENT_STATE_V1.schema.json").read_bytes())
    a.require(not list(Draft202012Validator(schema).iter_errors(d)), "descriptor schema")
    a.require(pin == {"path": a.CURRENT, "sha256": a.sha(raw), "HUMAN_PI_ACCEPTED": "YES"},
              "independent execution descriptor pin missing/wrong")
    a.require(d["candidate_only"] is False and d["runtime_authority"] is True
              and d["event_count"] == 3 and len(d["event_chain"]) == 3
              and d["lifecycle_label"] == "PREPARATION_EXECUTION_AUTHORIZED",
              "dispatch before event #3/effectivity")
    expected = copy.deepcopy(baseline["projection"])
    expected["state"] = "PREPARATION_EXECUTION_AUTHORIZED"
    expected["lifecycle"]["PREPARATION_AUTHORIZED"] = "YES"
    expected["phase_authorizations"]["PREPARATION_EXECUTION"] = "YES"
    a.require(d["projection"] == expected, "event #3 changed scientific states/other flags")
    a.require(d["event_chain"][:2] == baseline["event_chain"], "predecessor event chain changed")
    # All baseline surfaces except the explicit installation/effectivity leaves persist.
    allowed = {"projection", "projection_sha256", "event_chain", "event_count", "event_head",
               "lifecycle_label", "effective_current_descriptor_identity"}
    a.require(set(d) == set(baseline), "descriptor schema topology changed")
    a.require(all(d[k] == baseline[k] for k in baseline if k not in allowed),
              "descriptor contract/membership/authority drift")
    for ref in [d["contract"], *d["event_chain"]]:
        a.read_exact(ref["path"], ref["sha256"])
    ref = d["event_chain"][2]
    event = a.loads(a.read_exact(ref["path"], ref["sha256"]))
    schema = a.loads((a.B / "v6_contract_schemas/V6_CAPACITY_STATE_EVENT_V1.schema.json").read_bytes())
    a.require(not list(Draft202012Validator(schema).iter_errors(event)), "event schema")
    prior = baseline["event_head"]
    a.require(ref["sequence"] == 3 and event["sequence"] == 3
              and event["kind"] == "STATE_TRANSITION"
              and event["namespace"] == "EFFECTIVE_V6"
              and event["from_state"] == "PREPARATION_PLANNING_AUTHORIZED"
              and event["to_state"] == "PREPARATION_EXECUTION_AUTHORIZED"
              and event["gate"] == "HUMAN_PI_AUTHORIZE_V6_PREPARATION_EXECUTION"
              and event["previous_descriptor_sha256"] == a.CURRENT_SHA
              and event["previous_event_identity"] == prior
              and event["prior_projection_sha256"] == a.identity(baseline["projection"])
              and event["result_projection_sha256"] == d["projection_sha256"] == a.identity(expected)
              and event["next_projection"] == expected
              and event["contract_sha256"] == baseline["contract"]["sha256"]
              and event["predecessor"] == baseline["predecessor"], "event #3 semantic identity")
    event_core = {k: v for k, v in event.items() if k != "event_id"}
    a.require(event["event_id"] == a.identity(event_core) == ref["event_id"]
              and a.identity(event) == ref["event_sha256"]
              and d["event_head"] == {"sequence": 3, "event_id": ref["event_id"],
                                      "event_sha256": ref["event_sha256"]}, "event #3 hash chain")
    auth_ref = event["authority_reference"]
    auth = a.loads(a.read_exact(auth_ref["path"], auth_ref["sha256"]))
    a.require(auth["owner"] == "HUMAN_PI" and auth["gate"] == event["gate"]
              and auth["HUMAN_PI_ACCEPTED"] == "YES" and auth["namespace"] == "EFFECTIVE_V6"
              and auth["path"] == auth_ref["path"]
              and auth["contract_sha256"] == baseline["contract"]["sha256"]
              and auth["previous_descriptor_sha256"] == a.CURRENT_SHA
              and auth["prior_projection_sha256"] == a.identity(baseline["projection"]),
              "event #3 Human-PI authority")
    for ref in event["evidence_references"]:
        a.read_exact(ref["path"], ref["sha256"])
    a.require(installation["execution_descriptor"] == pin
              and installation["event_3_authority"] == auth_ref
              and installation["effective_descriptor_identity"] ==
              d["effective_current_descriptor_identity"], "installation/effectivity binding")
    # Future installation binds every previously reviewed descriptor/event byte;
    # no unpinned historical projection is substituted during execution.
    return d


def validate_installation(record):
    a.require(record["schema"] == "V6_PREPARATION_EXECUTION_RUNTIME_INSTALLATION_V1"
              and record["HUMAN_PI_ACCEPTED"] == "YES"
              and record["runtime_acceptance"] == {"path": AUTHORITY, "sha256": AUTHORITY_SHA}
              and set(record["implementation"]) == set(IMPLEMENTATION),
              "reviewed runtime installation missing/wrong")
    a.require(_git("status", "--porcelain=v1", "--untracked-files=all") == b"",
              "clean committed implementation required")
    head = _git("rev-parse", "HEAD").decode().strip()
    for path, digest in record["implementation"].items():
        a.read_exact(path, digest)
        a.require(a.sha(_git("cat-file", "blob", head + ":" + path)) == digest,
                  "uncommitted implementation identity")
    live = _git("ls-remote", "origin", "refs/heads/main").decode().split()
    a.require(live == [head, "refs/heads/main"], "exact live publication required")
    return head


def source_function(plan, item):
    """Bind the shared V2 exporter code object without predecessor membership/tokens."""
    recipe = a.engine_recipe(plan)
    def resolver(given_recipe, label):
        a.require(given_recipe == recipe and label in ("BUGGY", "FIXED"), "source resolver")
        a.require(not any(v["source_export_planning"]["tracked_gitlinks"]
                          for v in plan["source_variants"]), "unaccepted gitlink semantics")
        mirror = Path(plan["source_repository"]["mirror_path"])
        revision = next(v["commit_oid"] for v in plan["source_variants"] if v["label"] == label)
        a.require(snapshots._run_git(mirror, "cat-file", "-t", revision).strip() == b"commit",
                  "missing local source commit; SOURCE_ACQUISITION_BLOCKED")
        if item["variant"] != "SOURCE_INDEPENDENT":
            a.require(label == item["variant"] and revision == item["source_revision_sha"],
                      "opposite revision refused")
        return mirror, revision
    original = snapshots.source_snapshot_identity
    return types.FunctionType(original.__code__, {**original.__globals__, "_source_identity": resolver},
                              "v6_bound_shared_snapshot", original.__defaults__, original.__closure__)


def require_network(item, qualification):
    if item["build_network_required"]:
        # No accepted scoped implementation is installed for the shared default
        # build network. Neither a receipt nor a caller Boolean can bypass this.
        raise a.Rejected("RESTRICTED_BUILD_NETWORK_ENFORCEMENT_BLOCKED: "
                         "qualified scoped enforcement integration required for 583 items")
    a.require(qualification is None, "network authority for NONE item refused")


def shared_engine():
    """Reuse shared engine code, binding only V6's no-pull/no-egress transport.

    No shared global is modified. All Dockerfile, context, build and observation
    code objects stay identical to the accepted shared engine.
    """
    bound = dict(a.shared.__dict__)
    def guarded(original):
        def call(args, *, timeout=600):
            args = list(args)
            a.require(bool(args) and args[0] in ("image", "run", "build"), "Docker operation scope")
            if args[0] == "image":
                a.require(args[1] == "inspect", "Docker image acquisition/mutation refused")
            elif args[0] == "run":
                a.require([x for x in args if x.startswith("--network")] == ["--network=none"],
                          "execution network must be exactly NONE")
                a.require(not any(x.startswith("--pull=") and x != "--pull=never" for x in args),
                          "Docker pull forbidden")
                if "--pull=never" not in args:
                    args.insert(1, "--pull=never")
            else:
                a.require([x for x in args if x.startswith("--network")] == ["--network=none"]
                          and not any(x == "--pull" or x.startswith("--pull=") for x in args),
                          "unrestricted build/pull forbidden")
            return original(args, timeout=timeout)
        return call
    for name, value in a.shared.__dict__.items():
        if isinstance(value, types.FunctionType) and value.__globals__ is a.shared.__dict__:
            bound[name] = types.FunctionType(value.__code__, bound, value.__name__,
                                             value.__defaults__, value.__closure__)
            bound[name].__kwdefaults__ = value.__kwdefaults__
    bound["docker"] = guarded(a.shared.docker)
    bound["docker_observation"] = guarded(a.shared.docker_observation)
    return types.SimpleNamespace(**bound)


@dataclass(frozen=True)
class Admission:
    manifest: dict
    plan: dict
    item: dict
    binding: dict

    def revalidate(self):
        """An import caller cannot turn a fabricated admission into a real claim."""
        item = self.item
        request = {"descriptor_path": a.CURRENT, "descriptor_sha": a.CURRENT_SHA,
                   "manifest_path": a.MANIFEST, "manifest_sha": a.MANIFEST_SHA,
                   "ordinal": item["census_order"], "case_id": item["case_id"],
                   "plan_sha": item["plan_sha256"], "base_attempt_id": item["base_attempt_id"]}
        observed = preflight(request, acceptance=a.loads(a.read_exact(AUTHORITY, AUTHORITY_SHA)),
            installation=read_installed(INSTALLATION), pin=read_installed(EXECUTION_PIN), policy=POLICY)
        a.require(observed == self, "admission changed before durable claim")


def read_installed(relative):
    a.require(relative in (INSTALLATION, EXECUTION_PIN), "unapproved authority path")
    path = a.ROOT / relative
    ledger.safe_path(path)
    return a.loads(path.read_bytes())


def preflight(request, *, acceptance=None, installation=None, pin=None,
              network_qualification=None, policy=None):
    a.require(a.canonical(policy) == a.canonical(POLICY), "forbidden policy/token/selector")
    manifest, plan, item = select(**request)
    validate_acceptance(acceptance, network_required=item["build_network_required"])
    a.require(installation is not None and pin is not None, "future installation/pin required")
    # Read the independently installed canonical pin; caller-supplied objects
    # cannot be treated as accepted descriptor authority.
    a.require(pin == read_installed(EXECUTION_PIN), "installed pin mismatch")
    a.require(installation == read_installed(INSTALLATION),
              "installed runtime authority mismatch")
    validate_execution_descriptor((a.ROOT / a.CURRENT).read_bytes(), pin, installation)
    head = validate_installation(installation)
    require_network(item, network_qualification)
    export = source_function(plan, item)
    labels = ("BUGGY", "FIXED") if item["variant"] == "SOURCE_INDEPENDENT" else (item["variant"],)
    source_identities = {label: export(a.engine_recipe(plan), label) for label in labels}
    base_probe = shared_engine().verify_base(a.engine_recipe(plan))
    journal = ledger.Ledger(a.OUTPUT_ROOT, namespace=ledger.REAL,
                            real_ids=[x["base_attempt_id"] for x in population()["items"]])
    a.require(journal.state(item["base_attempt_id"]) == "UNSTARTED", "repeat attempt/no retry")
    binding = {"item": item, "runtime_acceptance_sha256": AUTHORITY_SHA,
               "implementation_commit": head, "implementation": installation["implementation"],
               "execution_descriptor": pin, "source_presence_identities": source_identities,
               "base_probe": base_probe, "network": "NONE"}
    return Admission(manifest, plan, item, binding)


def dispatch(request, **authority):
    admission = preflight(request, **authority)
    item, plan = admission.item, admission.plan
    journal = ledger.Ledger(a.OUTPUT_ROOT, namespace=ledger.REAL,
                            real_ids=[x["base_attempt_id"] for x in population()["items"]])
    journal.initialize()
    claim = journal.claim(item["base_attempt_id"], admission.binding, permit=admission)
    try:
        values = a.embedded_inputs(admission.manifest, plan)
        for key, relative in a.input_paths(item).items():
            if values[key] is not None:
                path = a.OUTPUT_ROOT / relative
                ledger.mkdir_durable(path.parent)
                ledger.exclusive_write(path, values[key])
        snapshot = None
        if item["variant"] != "SOURCE_INDEPENDENT":
            source = f"snapshots/{item['base_attempt_id']}"
            ledger.mkdir_durable(a.OUTPUT_ROOT / "snapshots")
            digest = source_function(plan, item)(a.engine_recipe(plan), item["variant"],
                                                a.OUTPUT_ROOT / source)
            ledger.persist_tree(a.OUTPUT_ROOT / source)
            snapshot = {"sha256": digest, "source_revision_sha": item["source_revision_sha"],
                        "source": source}
        proposal = a.engine_call_proposal(admission.manifest, item, snapshot=snapshot)
        a.require(proposal["network_required"] is False, "unrestricted default build denied")
        output = Path(proposal["output"])
        ledger.mkdir_durable(output.parent)
        result = shared_engine()._materialize_checked(proposal["fixture"], output=output,
                    input_root=a.OUTPUT_ROOT, synthetic_only=False, single_identity=True)
        hashes = ledger.persist_tree(output)
        evidence = {"artifact_sha256": hashes, "input_runtime_binding": admission.binding,
                    "network_provenance": {"build": "NONE", "execution": "NONE"}}
        if result["status"] == "MATERIALIZED":
            r = result["revisions"][0]
            evidence.update(dict(zip(ledger.SUCCESS, (
                r["dockerfile_sha256"], r["build_context_manifest_sha256"],
                a.sha(b"ABSENT\n") if snapshot is None else snapshot["sha256"],
                r["build_log_sha256"], r["image_inspect_sha256"], a.identity(r["observed_python"]),
                r["installed_distribution_manifest_sha256"], r["environment_identity_sha256"]))))
    except (Exception, KeyboardInterrupt) as exc:
        # Preserve any partially staged/built artifacts and consume no new identity.
        evidence = {"failure_type": type(exc).__name__, "detail": str(exc),
                    "input_runtime_binding": admission.binding, "network_provenance": "NONE"}
        if "output" in locals() and output.is_dir():
            evidence["artifact_sha256"] = ledger.persist_tree(output)
        return journal.terminal(claim, state="INTERRUPTED", evidence=evidence,
                                reason="operation interrupted; no automatic retry")
    # A terminal publication failure retains the claim/lock for adjudication;
    # it must never trigger a second terminal publication attempt.
    return journal.terminal(claim, state=result["status"], evidence=evidence,
                            reason=result.get("reason", ""))


def request_retry(*args, **kwargs):
    raise a.Rejected("retry requires later separate Human-PI authority and a new identity")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    # CLI is explicit real dispatch only; bare invocation does not select anything.
    args = parser.parse_args(argv)
    try:
        result = dispatch(a.loads(args.request.read_bytes()),
            acceptance=a.loads((a.ROOT / AUTHORITY).read_bytes()),
            installation=read_installed(INSTALLATION),
            pin=read_installed(EXECUTION_PIN), policy=POLICY)
    except (a.Rejected, OSError, KeyError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "REJECT", "reason": str(exc)}))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0 if result["state"] == "MATERIALIZED" else 1


if __name__ == "__main__":
    raise SystemExit(main())

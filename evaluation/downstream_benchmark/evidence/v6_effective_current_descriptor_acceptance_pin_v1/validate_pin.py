"""Read-only acceptance-pin audit; all rejection fixtures stay in memory.

The frozen installation validator is unchanged. Its exact pin statement is
executed separately because its full proof requires completed installation.
No installer, canonical writer, lifecycle closure, or downstream execution runs.
"""

import ast
import copy
import importlib.util
import json
import re
from pathlib import Path

E = Path(__file__).resolve().parent
ROOT = E.parents[3]
PREFIX = "evaluation/downstream_benchmark/"
B = ROOT / PREFIX
HEAD = "2df946a0aa04d82831240e2c9b6a7cd789e7685d"
PARENT = "b83650784bfc6e79ecf11b3a4be2e4e74aac891f"
LIVE = "1e5f8a3f4bc2e8555619f727ea317b0bd2fdf801"
PIN_PATH = PREFIX + "V6_EFFECTIVE_CURRENT_DESCRIPTOR_ACCEPTANCE_PIN_V1.json"
PIN_ID = "V6_EFFECTIVE_CURRENT_DESCRIPTOR_ACCEPTANCE_PIN_V1"
DESCRIPTOR_PATH = (
    PREFIX
    + "evidence/v6_effective_current_descriptor_v1/effective_current_descriptor_candidate.json"
)
DESCRIPTOR_SHA = "9295430e8573474b17bc79339c92f46044e443b9dabfe81280f9fb789d751073"
DESCRIPTOR_CLOSURE = PREFIX + "V6_EFFECTIVE_CURRENT_DESCRIPTOR_V1_LIFECYCLE_CLOSURE.md"
AUTHORITY_PATH = PREFIX + "V6_CENSUS_MEMBERSHIP_INSTALLATION_AUTHORITY_V1.json"
AUTHORITY_CLOSURE = PREFIX + "V6_CENSUS_MEMBERSHIP_INSTALLATION_AUTHORITY_V1_LIFECYCLE_CLOSURE.md"
REQUIRED_HASHES = {
    DESCRIPTOR_PATH: DESCRIPTOR_SHA,
    DESCRIPTOR_CLOSURE: "de1d122d752c29ee7fc6dde854603cfe1121bf0b4a370ec32fe6543cff514fe8",
    AUTHORITY_PATH: "359be257db9b355222d71d3e72e9234e736331d5e1a6d079f883b572f85a7458",
    AUTHORITY_CLOSURE: "f6b2ba7da86feeb29a9308e11f1e8da2d7200a138e6fcf7c403ebb3050fc4212",
    PREFIX + "v6_current_state.json": (
        "d17bcd3b7c669227f920671984b502497cdca9d367523548da4130eb8f986670"
    ),
}
FILES = {
    PIN_PATH,
    *(
        str((E / name).relative_to(ROOT))
        for name in (
            "entry_verification.json",
            "validate_pin.py",
            "validation_results.json",
            "RUN_REPORT.md",
        )
    ),
}
EDGES = [
    ["accepted_installation_authority", "effective_descriptor_bytes"],
    ["effective_descriptor_bytes", "exact_descriptor_sha256"],
    ["exact_descriptor_sha256", "external_acceptance_pin"],
]

spec = importlib.util.spec_from_file_location(
    "accepted_v6_effective_descriptor",
    B / "evidence/v6_effective_current_descriptor_v1/validate_descriptor.py",
)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
v = d.v
EXPECTED = {"path": v.CURRENT_PATH, "sha256": DESCRIPTOR_SHA, "HUMAN_PI_ACCEPTED": "YES"}


def frozen_pin_statement():
    source = Path(v.__file__).read_bytes()
    tree = ast.parse(source)
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "validate_installation_semantics"
    )
    nodes = [
        node
        for node in function.body
        if isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Call)
        and node.value.args
        and isinstance(node.value.args[-1], ast.Constant)
        and node.value.args[-1].value == "missing independent exact successor acceptance pin"
    ]
    v.require(len(nodes) == 1, "frozen pin predicate missing/ambiguous")
    node = nodes[0]
    return compile(ast.Module(body=[node], type_ignores=[]), v.__file__, "exec"), {
        "path": str(Path(v.__file__).relative_to(ROOT)),
        "sha256": v.sha(source),
        "start_line": node.lineno,
        "end_line": node.end_lineno,
        "statement_AST_sha256": v.sha(ast.dump(node, include_attributes=False).encode()),
        "method": "Execute the unchanged frozen acceptance-pin require statement; no installation assertion supplied.",
    }


PIN_CHECK, PIN_CHECK_SOURCE = frozen_pin_statement()


def frozen_pin_check(pin, descriptor_bytes):
    exec(
        PIN_CHECK,
        dict(v.__dict__),
        {
            "proof": {"acceptance_pin": pin},
            "successor_bytes": descriptor_bytes,
        },
    )


def governance(path, identity, commit):
    record = d.a.closure((ROOT / path).read_bytes())
    lifecycle = record["lifecycle"]
    v.require(lifecycle[identity] == ["HUMAN_PI_ACCEPTED", "FROZEN"], "acceptance/freeze missing")
    v.require(
        lifecycle["PERSISTED"] == lifecycle["COMMITTED"] == "YES", "persistence/commit missing"
    )
    envelope = record["commit_envelope"]
    v.require(
        d.git("rev-parse", commit + "^").decode().strip() == envelope["required_parent"],
        "lifecycle commit parent drift",
    )
    v.require(
        d.git("log", "-1", "--format=%s", commit).decode().strip() == envelope["message"],
        "lifecycle commit message drift",
    )
    v.require(
        set(d.git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).decode().splitlines())
        == set(envelope["exact_paths"]),
        "lifecycle commit envelope drift",
    )
    for name in envelope["exact_paths"]:
        v.require(
            d.git("show", commit + ":" + name) == (ROOT / name).read_bytes(),
            "lifecycle committed bytes drift: " + name,
        )
    if identity == "V6_EFFECTIVE_CURRENT_DESCRIPTOR_V1":
        for name, sha in record["accepted_candidate_evidence_paths_sha256"].items():
            v.require(v.sha((ROOT / name).read_bytes()) == sha, "accepted evidence drift")
    return {key: "YES" for key in v.FOUR}


def scan_artifacts():
    pins, installations, count = [], [], 0
    for path in B.rglob("*.json"):
        count += 1
        name = str(path.relative_to(ROOT))
        if name in FILES and name != PIN_PATH:
            continue  # Separate audit metadata is not an acceptance-pin artifact.
        obj = json.loads(path.read_bytes())

        def visit(value):
            if isinstance(value, dict):
                if (
                    value.get("path") == v.CURRENT_PATH
                    and value.get("sha256") == DESCRIPTOR_SHA
                    and "HUMAN_PI_ACCEPTED" in value
                ):
                    pins.append(str(path.relative_to(ROOT)))
                if (
                    "INSTALLATION_RECORD" in str(value.get("schema", "")).upper()
                    or value.get("installed_verified") is True
                    or value.get("observed_installed_bytes") is not None
                ):
                    installations.append(str(path.relative_to(ROOT)))
                for child in value.values():
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)

        visit(obj)
    record_paths = [
        str(path.relative_to(ROOT))
        for path in B.rglob("*")
        if path.is_file() and "installation" in path.name.lower() and "record" in path.name.lower()
    ]
    return {
        "JSON_artifacts_scanned": count,
        "exact_pin_hits": pins,
        "installation_record_hits": installations,
        "installation_record_paths": record_paths,
    }


def preservation():
    entry = v.loads((E / "entry_verification.json").read_bytes())
    v.require(
        entry["status"] == "ENTRY_GATE_PASS" and entry["live_origin_main"] == LIVE,
        "entry/live-ref evidence missing",
    )
    v.require(
        d.git("rev-parse", "--show-toplevel").decode().strip() == str(ROOT), "wrong repository"
    )
    v.require(d.git("branch", "--show-current").decode().strip() == "main", "branch drift")
    v.require(d.git("rev-parse", "HEAD").decode().strip() == HEAD, "HEAD drift")
    v.require(d.git("rev-parse", "HEAD^").decode().strip() == PARENT, "parent drift")
    v.require(d.git("diff", "--name-only") == b"", "tracked worktree changed")
    v.require(d.git("diff", "--cached", "--name-only") == b"", "index changed")
    untracked = {
        p.decode()
        for p in d.git("ls-files", "--others", "--exclude-standard", "-z").split(b"\0")
        if p
    }
    v.require(untracked <= FILES, "unrelated untracked paths")
    hashes = d.protected_hashes()
    v.require(
        len(hashes) == entry["protected_tracked_benchmark_files"]
        and v.digest(hashes) == entry["protected_path_hash_mapping_sha256"],
        "protected bytes drift",
    )
    for name, sha in REQUIRED_HASHES.items():
        v.require(v.sha((ROOT / name).read_bytes()) == sha, "controlling identity drift: " + name)
    scan = scan_artifacts()
    v.require(scan["exact_pin_hits"] == [PIN_PATH], "unexpected existing/duplicate pin artifact")
    v.require(
        not scan["installation_record_hits"] and not scan["installation_record_paths"],
        "installation record exists",
    )
    return {
        "tracked_benchmark_files_unchanged": len(hashes),
        "protected_path_hash_mapping_sha256": v.digest(hashes),
        "canonical_sha256": REQUIRED_HASHES[v.CURRENT_PATH],
        "tracked_worktree_diff": "EMPTY",
        "index_diff": "EMPTY",
        "HEAD_unchanged": True,
        "only_authorized_untracked_paths": True,
        "installation_record_absent": True,
    }


def validate_pin(raw, descriptor_bytes, lifecycle, predecessor):
    pin = v.loads(raw)
    v.require(
        type(pin) is dict and set(pin) == set(EXPECTED), "exact three semantic fields required"
    )
    v.require(
        type(pin["sha256"]) is str and re.fullmatch(r"[0-9a-f]{64}", pin["sha256"]),
        "malformed SHA-256",
    )
    v.require(pin == EXPECTED, "exact Human-PI pin values/canonical target required")
    v.require(lifecycle == {key: "YES" for key in v.FOUR}, "descriptor lifecycle incomplete")
    descriptor = v.loads(descriptor_bytes)
    v.require(
        descriptor["effective_current_descriptor_identity"]["descriptor_id"] == d.DESCRIPTOR_ID,
        "wrong exact descriptor_id",
    )
    v.require(
        descriptor["effective_current_descriptor_identity"]["human_pi_transition"]
        == {"path": AUTHORITY_PATH, "sha256": REQUIRED_HASHES[AUTHORITY_PATH]},
        "wrong installation-authority reference",
    )
    serialized = v.canonical(descriptor)
    v.require(
        all(
            token not in serialized
            for token in (
                PIN_PATH.encode(),
                PIN_ID.encode(),
                b"acceptance_pin",
                b"installation_record",
            )
        ),
        "descriptor depends on pin/future installation record",
    )
    v.require(
        v.sha(descriptor_bytes) == pin["sha256"] == DESCRIPTOR_SHA,
        "pinned descriptor bytes mismatch",
    )
    v.require(v.sha(raw) != pin["sha256"], "pin self-hash dependency")
    v.require(
        v.sha(predecessor) == REQUIRED_HASHES[v.CURRENT_PATH],
        "canonical predecessor changed unexpectedly",
    )
    current = v.loads(predecessor)
    v.require(
        current["projection"]["lifecycle"]["V6_ACTIVATED"] == "NO"
        and current["projection"]["lifecycle"]["CENSUS_MEMBERSHIP_EFFECTIVE"] == "NO"
        and current["event_count"] == 0
        and current["event_head"] is None
        and current["runtime_authority"] is False,
        "canonical installation already occurred",
    )
    frozen_pin_check(pin, descriptor_bytes)
    v.acyclic(EDGES)
    return pin


def rejection(name, call, layer):
    try:
        call()
    except ValueError as error:
        return {"check": name, "layer": layer, "result": "PASS_REJECTED", "reason": str(error)}
    raise ValueError("required rejection escaped: " + name)


def audit():
    before = preservation()
    lifecycle = governance(DESCRIPTOR_CLOSURE, "V6_EFFECTIVE_CURRENT_DESCRIPTOR_V1", HEAD)
    authority_lifecycle = governance(
        AUTHORITY_CLOSURE, "V6_CENSUS_MEMBERSHIP_INSTALLATION_AUTHORITY_V1", PARENT
    )
    f = d.inputs()
    descriptor_bytes = (ROOT / DESCRIPTOR_PATH).read_bytes()
    raw = (ROOT / PIN_PATH).read_bytes()
    pin = validate_pin(raw, descriptor_bytes, lifecycle, f["predecessor"])
    v.require(raw == v.canonical(pin), "pin stored bytes must be exact canonical JSON")
    descriptor = v.loads(descriptor_bytes)
    v.schema("V6_CAPACITY_CURRENT_STATE_V1", descriptor)
    projection = v.validate_genesis_event(
        f["event"],
        f["predecessor"],
        f["bridge"],
        f["baseline"],
        f["acceptance"],
        f["activation_authority"],
    )
    v.validate_bootstrap_descriptor(
        descriptor, f["event"], f["event_raw"], f["event_path"], projection, f["predecessor"]
    )
    matrix = []
    mutations = [
        ("missing_path", lambda p: p.pop("path")),
        ("extra_field", lambda p: p.update(metadata="forbidden")),
        ("wrong_canonical_path", lambda p: p.update(path="wrong/current.json")),
        ("artifact_path_substituted", lambda p: p.update(path=PIN_PATH)),
        ("wrong_descriptor_SHA", lambda p: p.update(sha256="0" * 64)),
        ("transition_candidate_SHA", lambda p: p.update(sha256=v.sha(f["source_raw"]))),
        ("HUMAN_PI_ACCEPTED_NO", lambda p: p.update(HUMAN_PI_ACCEPTED="NO")),
        ("HUMAN_PI_ACCEPTED_boolean", lambda p: p.update(HUMAN_PI_ACCEPTED=True)),
        ("pin_self_hash", lambda p: p.update(own_sha256=v.sha(raw))),
        (
            "future_installation_record_dependency",
            lambda p: p.update(future_installation_record_sha256="0" * 64),
        ),
        ("future_commit_dependency", lambda p: p.update(future_commit_sha="0" * 40)),
        (
            "future_installed_file_observation",
            lambda p: p.update(observed_installed_sha256=DESCRIPTOR_SHA),
        ),
        ("malformed_SHA", lambda p: p.update(sha256="not-a-sha")),
        ("uppercase_SHA", lambda p: p.update(sha256=DESCRIPTOR_SHA.upper())),
        ("missing_sha256", lambda p: p.pop("sha256")),
        ("missing_acceptance", lambda p: p.pop("HUMAN_PI_ACCEPTED")),
        ("wrong_field_name", lambda p: p.update(SHA256=p.pop("sha256"))),
    ]
    for name, mutate in mutations:
        changed = copy.deepcopy(pin)
        mutate(changed)
        matrix.append(
            rejection(
                name,
                lambda: validate_pin(
                    v.canonical(changed), descriptor_bytes, lifecycle, f["predecessor"]
                ),
                "exact pin adapter",
            )
        )
        matrix.append(
            rejection(
                "frozen_pin:" + name,
                lambda: frozen_pin_check(changed, descriptor_bytes),
                "unchanged frozen pin statement",
            )
        )
    for key in v.FOUR:
        changed_lifecycle = dict(lifecycle, **{key: "NO"})
        matrix.append(
            rejection(
                "descriptor_lifecycle:" + key,
                lambda: validate_pin(raw, descriptor_bytes, changed_lifecycle, f["predecessor"]),
                "real-lifecycle adapter; synthetic mutation",
            )
        )
    for name, mutate in [
        (
            "wrong_descriptor_id",
            lambda o: o["effective_current_descriptor_identity"].update(descriptor_id="wrong-id"),
        ),
        (
            "wrong_authority_path",
            lambda o: o["effective_current_descriptor_identity"]["human_pi_transition"].update(
                path="wrong/authority.json"
            ),
        ),
        (
            "wrong_authority_SHA",
            lambda o: o["effective_current_descriptor_identity"]["human_pi_transition"].update(
                sha256="0" * 64
            ),
        ),
        (
            "descriptor_depends_on_pin_path",
            lambda o: o.update(acceptance_pin_reference={"path": PIN_PATH}),
        ),
        ("descriptor_depends_on_pin_SHA", lambda o: o.update(acceptance_pin_sha256=v.sha(raw))),
        ("descriptor_depends_on_pin_identity", lambda o: o.update(pin_identity=PIN_ID)),
    ]:
        changed = copy.deepcopy(descriptor)
        mutate(changed)
        matrix.append(
            rejection(
                name,
                lambda: validate_pin(
                    raw,
                    descriptor_bytes=d.a.pretty(changed),
                    lifecycle=lifecycle,
                    predecessor=f["predecessor"],
                ),
                "exact descriptor binding; synthetic mutation",
            )
        )
    matrix.append(
        rejection(
            "descriptor_byte_drift",
            lambda: validate_pin(raw, descriptor_bytes + b"\n", lifecycle, f["predecessor"]),
            "exact stored SHA",
        )
    )
    for name, changed_raw in [
        ("canonical_changed_unexpectedly", f["predecessor"] + b"\n"),
        ("canonical_already_installed", descriptor_bytes),
    ]:
        matrix.append(
            rejection(
                name,
                lambda: validate_pin(raw, descriptor_bytes, lifecycle, changed_raw),
                "canonical predecessor guard; synthetic bytes",
            )
        )
    for name, malformed in [
        ("duplicate_key", raw[:-1] + b',"path":"duplicate"}'),
        ("BOM", b"\xef\xbb\xbf" + raw),
        ("float", b'{"path":1.0}'),
        ("invalid_unicode_scalar", b'{"path":"\\ud800"}'),
    ]:
        matrix.append(
            rejection(
                name,
                lambda: validate_pin(malformed, descriptor_bytes, lifecycle, f["predecessor"]),
                "frozen strict JSON",
            )
        )
    for node in [
        "effective_descriptor_bytes",
        "exact_descriptor_sha256",
        "external_acceptance_pin",
    ]:
        matrix.append(
            rejection(
                "hash_cycle:" + node,
                lambda: v.acyclic(EDGES + [[node, "accepted_installation_authority"]]),
                "frozen acyclic checker",
            )
        )
    proof = {
        "operation": v.OPERATION,
        "path": v.CURRENT_PATH,
        "expected_predecessor_sha256": v.sha(f["predecessor"]),
        "observed_predecessor_sha256": v.sha((ROOT / v.CURRENT_PATH).read_bytes()),
        "artifact_lifecycle": lifecycle,
        "publication": copy.deepcopy(v.PUBLICATION),
        "automatic": False,
        "installation_authorized": False,
        "installed_verified": False,
        "committed_successor_bytes": d.git("show", HEAD + ":" + DESCRIPTOR_PATH),
        "observed_installed_bytes": None,
        "acceptance_pin": pin,
        "installation_authority": copy.deepcopy(f["install_authority"]),
        "competing_current_descriptors": [],
    }
    full = rejection(
        "real_full_installation_proof_without_installation",
        lambda: d.frozen_proof(descriptor_bytes, f, proof),
        "unchanged full frozen installation validator",
    )
    v.require(
        full["reason"] == "exact explicit installation incomplete/competing",
        "unexpected full-proof failure",
    )
    after = preservation()
    v.require(before == after, "audit changed protected inputs")
    canonical_sha, stored_sha = v.digest(pin), v.sha(raw)
    return {
        "status": "PASS",
        "date": "2026-10-05",
        "timezone": "Europe/Budapest",
        "authority_transaction": "HUMAN_PI_OPEN_V6_EFFECTIVE_CURRENT_DESCRIPTOR_ACCEPTANCE_PIN_CONSTRUCTION_V1",
        "pin_object": pin,
        "pin_artifact_path": PIN_PATH,
        "ACCEPTANCE_PIN_CANONICAL_OBJECT_SHA256": canonical_sha,
        "ACCEPTANCE_PIN_STORED_FILE_SHA256": stored_sha,
        "canonical_and_stored_hash_equality_verified": canonical_sha == stored_sha,
        "stored_byte_count": len(raw),
        "stored_format": "exact frozen canonical UTF-8 JSON; no trailing newline",
        "descriptor": {
            "path": DESCRIPTOR_PATH,
            "sha256": DESCRIPTOR_SHA,
            "descriptor_id": d.DESCRIPTOR_ID,
            "lifecycle": lifecycle,
            "closure_path": DESCRIPTOR_CLOSURE,
            "closure_sha256": REQUIRED_HASHES[DESCRIPTOR_CLOSURE],
            "commit": HEAD,
        },
        "installation_authority": {
            "path": AUTHORITY_PATH,
            "sha256": REQUIRED_HASHES[AUTHORITY_PATH],
            "lifecycle": authority_lifecycle,
            "closure_path": AUTHORITY_CLOSURE,
            "closure_sha256": REQUIRED_HASHES[AUTHORITY_CLOSURE],
            "commit": PARENT,
        },
        "positive": {
            "exact_three_fields": "PASS",
            "exact_descriptor_identity": "PASS",
            "actual_committed_descriptor_bytes": "PASS",
            "schema": "PASS",
            "frozen_event_replay_and_bootstrap_descriptor": "PASS",
            "frozen_acceptance_pin_requirement": "SATISFIED",
            "NO_HASH_CYCLE": "YES",
        },
        "rejection_matrix": matrix,
        "rejection_count": len(matrix),
        "failures": 0,
        "hash_dependency_edges": EDGES,
        "frozen_pin_predicate": PIN_CHECK_SOURCE,
        "non_mutating_installation_proof": {
            "acceptance_pin_requirement": "SATISFIED",
            "full_validator_result": "EXPECTED_REJECTION_INSTALLATION_NOT_EXECUTED",
            "full_validator_observation": full,
            "installed_verified": False,
            "observed_installed_bytes": None,
            "canonical_replacement_observed": False,
            "installation_authorized_by_this_transaction": False,
            "synthetic_successful_installation_fixture_used": False,
            "installation_performed": False,
            "runtime_authority_granted_by_validator": False,
        },
        "preservation": after,
        "firewall": {
            key: "NO"
            for key in [
                "ACCEPTANCE_PIN_HUMAN_PI_LIFECYCLE_CLOSED",
                "CANONICAL_CURRENT_STATE_MODIFIED",
                "INSTALLATION_EXECUTED",
                "V6_CANONICAL_ACTIVATED",
                "PREPARATION_AUTHORIZED",
                "ORACLE_AUTHORIZED",
                "SOURCE_ACQUISITION",
                "MATERIALIZATION",
                "IMAGE_BUILD",
                "SUBJECT_DOCKER_EXECUTION",
                "PILOT_IDS_COMPUTED",
                "FINALS_ALLOCATED",
                "GIT_STAGE",
                "GIT_COMMIT",
                "GIT_PUSH",
            ]
        },
        "next_gate": "HUMAN_PI_REVIEW_OF_V6_EFFECTIVE_CURRENT_DESCRIPTOR_ACCEPTANCE_PIN_V1",
        "limits": "Pin semantics only. Full proof deliberately rejects absent installation; no runtime qualification or scientific validation. Negative fixtures are in memory. This candidate pin has no Human-PI lifecycle closure.",
    }


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True, ensure_ascii=False, indent=2))

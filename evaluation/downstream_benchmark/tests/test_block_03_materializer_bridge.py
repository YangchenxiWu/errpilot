"""Accepted-input and production-boundary checks with an enforced runtime firewall."""

from __future__ import annotations

import copy
import csv
import io
import json
import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from evaluation.downstream_benchmark.screening import block_03_materializer_bridge as bridge
from evaluation.downstream_benchmark.screening import materializer as m


@pytest.fixture(scope="module", autouse=True)
def runtime_firewall():
    original = subprocess.run
    original_popen = subprocess.Popen

    def check_git(args, kwargs):
        assert isinstance(args, list) and args[:1] == ["git"] and not kwargs.get("shell")
        command = args[3] if args[1:2] in (["-C"], ["--git-dir"]) else args[1]
        assert command in {"status", "rev-parse", "remote", "cat-file", "branch"}
        if command == "branch":
            assert args[-1:] == ["--show-current"]
        if command == "remote":
            assert args[-3:-1] == ["remote", "get-url"]
        if command == "cat-file":
            assert "-t" in args

    def readonly_git(args, *positional, **kwargs):
        check_git(args, kwargs)
        return original(args, *positional, **kwargs)

    def readonly_popen(args, *positional, **kwargs):
        check_git(args, kwargs)
        return original_popen(args, *positional, **kwargs)

    def forbidden(*args, **kwargs):
        raise AssertionError("materialization/subject execution crossed runtime firewall")

    with patch.object(subprocess, "run", side_effect=readonly_git), \
            patch.object(subprocess, "Popen", side_effect=readonly_popen), \
            patch.object(m, "docker", side_effect=forbidden), \
            patch.object(m, "docker_observation", side_effect=forbidden), \
            patch.object(m, "_materialize_checked", side_effect=forbidden):
        yield


@pytest.fixture(scope="module")
def accepted():
    return bridge.load_inputs()


@pytest.fixture
def mutable_inputs(tmp_path: Path):
    # Copies inert artifacts only, never a subject checkout or environment.
    benchmark = tmp_path / "benchmark"
    shutil.copytree(m.BENCHMARK, benchmark, ignore=shutil.ignore_patterns("__pycache__"))
    evidence = tmp_path / "preparation_evidence"
    shutil.copytree(bridge.PREPARATION, evidence)
    return benchmark, evidence


def rebind_fixture(benchmark: Path, monkeypatch, changed: Path, *, external=False, evidence=None):
    """Rebind a synthetic fixture to exercise semantic checks beyond byte guards."""
    authority_path = benchmark / bridge.AUTHORITY_FILE
    authority = json.loads(authority_path.read_text())
    mapping = ("original_preparation_evidence_sha256" if external else "accepted_repository_sha256")
    authority[mapping][str(changed.relative_to(evidence if external else benchmark))] = m.sha256(changed.read_bytes())
    authority_path.write_text(json.dumps(authority, indent=2, sort_keys=True) + "\n")
    monkeypatch.setattr(bridge, "AUTHORITY_SHA256", m.sha256(authority_path.read_bytes()))


def request_for(item, label="BUGGY"):
    recipe = item["recipe"]
    return {"canonical_case_id": recipe["canonical_case_id"], "expansion_block": 3,
            "expansion_order": recipe["expansion_order"], "block_identity_sha256": bridge.BLOCK_SHA256,
            "materializer_input_authority_sha256": bridge.AUTHORITY_SHA256,
            "build_recipe_sha256": m.recipe_hash(recipe),
            "self_reference_ledger": item["self_reference_ledger"], **item["input_paths"],
            "revision_label": label, "revisions": [{"label": label, "sha": "0" * 64,
                "source": f"snapshots/{recipe['canonical_case_id'].replace('::', '__')}/{label.lower()}",
                "source_revision_sha": recipe[f"{label.lower()}_source_sha"]}]}


def test_exact_seven_and_deterministic_order(accepted):
    first = bridge.load_inputs()
    second = bridge.load_inputs()
    assert first == second == accepted
    assert tuple(item["recipe"]["canonical_case_id"] for item in first) == bridge.MEMBERS
    assert [item["recipe"]["expansion_order"] for item in first] == list(range(1, 8))
    assert all(item["recipe"]["materialization_identity"] == "UNBUILT" for item in first)
    assert m.check_expansion_block_03_ledger() == [item["recipe"] for item in first]


@pytest.mark.parametrize("mutation", ["missing", "eighth", "duplicate", "reorder"])
def test_membership_rejected_independently_of_file_hash(mutable_inputs, monkeypatch, mutation):
    benchmark, evidence = mutable_inputs
    path = benchmark / "expansion_block_03_environment_build_recipes.csv"
    rows = m.read_rows(path)
    fields = list(rows[0])
    if mutation == "missing":
        rows.pop()
    elif mutation == "eighth":
        rows.append({**rows[-1], "canonical_case_id": "unknown::8", "expansion_order": "8"})
    elif mutation == "duplicate":
        rows[-1]["canonical_case_id"] = rows[0]["canonical_case_id"]
    else:
        rows[0], rows[1] = rows[1], rows[0]
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    path.write_text(stream.getvalue())
    rebind_fixture(benchmark, monkeypatch, path)
    with pytest.raises(m.Blocked, match="exact seven ordered Block 03 recipes required"):
        bridge.load_inputs(benchmark, evidence)


@pytest.mark.parametrize("name", [bridge.AUTHORITY_FILE,
    "EXPANSION_BLOCK_03_PREPARATION_V1.md", "BLOCK_03_PREPARATION_COMPATIBILITY_BRIDGE_V1.md",
    "expansion_block_03_execution_plan.csv", "expansion_block_03_environment_requirements.csv",
    "expansion_block_03_environment_build_recipes.csv",
    "evidence/block_03_preparation_compatibility_bridge_v1/cookiecutter__2/oracle_representation.json"])
def test_missing_artifact_rejected(mutable_inputs, name):
    benchmark, evidence = mutable_inputs
    (benchmark / name).unlink()
    with pytest.raises(m.Blocked):
        bridge.load_inputs(benchmark, evidence)


@pytest.mark.parametrize("name", [bridge.AUTHORITY_FILE,
    "EXPANSION_BLOCK_03_PREPARATION_V1.md", "BLOCK_03_PREPARATION_COMPATIBILITY_BRIDGE_V1.md",
    "expansion_block_03_environment_build_recipes.csv", "expansion_block_03_execution_plan.csv",
    "expansion_block_03_environment_requirements.csv",
    "derived_inputs/expansion_block_03/cookiecutter__1/requirements.dependencies.txt"])
def test_wrong_accepted_artifact_hash_rejected(mutable_inputs, name):
    benchmark, evidence = mutable_inputs
    path = benchmark / name
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(m.Blocked, match="hash mismatch"):
        bridge.load_inputs(benchmark, evidence)


@pytest.mark.parametrize("key,value", [
    ("block_identity_sha256", "0" * 64), ("preparation_acceptance", "PREPARED"),
    ("compatibility_bridge_acceptance", "CANDIDATE_ONLY"),
    ("materialization_authorized", True), ("bugsinpy_commit", "0" * 40),
    ("bugsinpy_tree", "0" * 40), ("sampling_seed", 1), ("bridge_lifecycle", "FROZEN")])
def test_authority_semantics_fail_closed(mutable_inputs, monkeypatch, key, value):
    benchmark, evidence = mutable_inputs
    path = benchmark / bridge.AUTHORITY_FILE
    authority = json.loads(path.read_text())
    authority[key] = value
    path.write_text(json.dumps(authority))
    monkeypatch.setattr(bridge, "AUTHORITY_SHA256", m.sha256(path.read_bytes()))
    with pytest.raises(m.Blocked, match="acceptance/provenance mismatch"):
        bridge.load_inputs(benchmark, evidence)


def test_wrong_recipe_identity_rejected(mutable_inputs, monkeypatch):
    benchmark, evidence = mutable_inputs
    path = benchmark / bridge.AUTHORITY_FILE
    authority = json.loads(path.read_text())
    authority["ordered_recipe_identities"][0]["build_recipe_sha256"] = "0" * 64
    path.write_text(json.dumps(authority))
    monkeypatch.setattr(bridge, "AUTHORITY_SHA256", m.sha256(path.read_bytes()))
    with pytest.raises(m.Blocked, match="recipe mismatch"):
        bridge.load_inputs(benchmark, evidence)


def test_preparation_state_other_than_ready_is_rejected(mutable_inputs):
    benchmark, evidence = mutable_inputs
    path = benchmark / "evidence/block_03_preparation_compatibility_bridge_v1/cookiecutter__2/preparation_plan.json"
    plan = json.loads(path.read_text())
    plan["preparation_status"] = "EXPANSION_PREPARATION_BLOCKED"
    path.write_text(json.dumps(plan))
    with pytest.raises(m.Blocked, match="preparation hash mismatch"):
        bridge.load_inputs(benchmark, evidence)


@pytest.mark.parametrize("key,value", [("source_url", "https://example.invalid/other"),
    ("buggy_commit_full", "0" * 40), ("fixed_commit_full", "0" * 40),
    ("mirror_path", "/unused/other.git")])
def test_wrong_source_identity_rejected(mutable_inputs, monkeypatch, key, value):
    benchmark, evidence = mutable_inputs
    path = evidence / "tqdm__6/source_identity.json"
    source = json.loads(path.read_text())
    source[key] = value
    path.write_text(json.dumps(source))
    rebind_fixture(benchmark, monkeypatch, path, external=True, evidence=evidence)
    with pytest.raises(m.Blocked, match="source identity mismatch"):
        bridge.load_inputs(benchmark, evidence)


def test_cookiecutter_commands_pass_through_unchanged(accepted):
    expected = [
        ["tox tests/test_hooks.py::TestFindHooks::test_find_hook",
         "tox tests/test_hooks.py::TestExternalHooks::test_run_hook"],
        ["tox tests/test_generate_context.py::test_generate_context_decodes_non_ascii_chars"],
    ]
    for item, commands in zip(accepted[-2:], expected):
        assert item["execution_plan"]["oracle_commands"] == commands
        assert item["oracle_representation"]["commands"] == commands
        assert item["oracle_representation"]["argv"] == [command.split() for command in commands]
        action = item["recipe"]["setup_actions"][0]
        assert action["exact_source_text"] == "python setup.py develop"
        assert m.action_argv(action, source_present=True) == ["python", "setup.py", "develop"]
        for label in ("BUGGY", "FIXED"):
            checked = m.validate_expansion_block_03_request(request_for(item, label))
            assert checked["recipe"] == item["recipe"]
            assert checked["oracle_representation"] == item["oracle_representation"]


@pytest.mark.parametrize("filename,key,value", [
    ("oracle_representation.json", "commands", ["pytest tests/test_hooks.py"]),
    ("environment_inputs.json", "setup_actions", [{"exact_source_text": "python setup.py install"}]),
])
def test_command_mutation_rejected(mutable_inputs, filename, key, value):
    benchmark, evidence = mutable_inputs
    path = benchmark / "evidence/block_03_preparation_compatibility_bridge_v1/cookiecutter__2" / filename
    content = json.loads(path.read_text())
    content[key] = value
    path.write_text(json.dumps(content))
    with pytest.raises(m.Blocked, match="preparation hash mismatch"):
        bridge.load_inputs(benchmark, evidence)


@pytest.mark.parametrize("key,value", [("canonical_case_id", "unknown::8"), ("expansion_block", 4),
    ("expansion_order", 8), ("block_identity_sha256", "0" * 64),
    ("build_recipe_sha256", "0" * 64), ("materializer_input_authority_sha256", "0" * 64),
    ("normalized_requirements", "derived_inputs/expansion_block_02/other"),
    ("oracle_commands", ["tox"]), ("revision_label", "SOURCE_INDEPENDENT")])
def test_future_request_identity_rejections(accepted, key, value):
    request = request_for(accepted[0])
    request[key] = value
    with pytest.raises(m.Blocked):
        m.validate_expansion_block_03_request(request)


@pytest.mark.parametrize("value", [None, [], {"canonical_case_id": []}])
def test_malformed_request_fails_closed(value):
    with pytest.raises(m.Blocked, match="request object/case identity required"):
        m.validate_expansion_block_03_request(value)


def test_buggy_fixed_separation_and_no_multiple_identities(accepted):
    for item in accepted:
        for label in ("BUGGY", "FIXED"):
            request = request_for(item, label)
            checked = m.validate_expansion_block_03_request(request)
            assert checked["recipe"] == item["recipe"]
            request["revisions"][0]["source_revision_sha"] = item["recipe"][
                "fixed_source_sha" if label == "BUGGY" else "buggy_source_sha"]
            with pytest.raises(m.Blocked, match="source revision/snapshot identity mismatch"):
                m.validate_expansion_block_03_request(request)
    request = request_for(accepted[0])
    request["revisions"].append(copy.deepcopy(request["revisions"][0]))
    with pytest.raises(m.Blocked, match="one BUGGY/FIXED identity"):
        m.validate_expansion_block_03_request(request)


def test_disabled_dispatch_rejects_all_tokens_before_input_or_output(tmp_path):
    output = tmp_path / "attempt"
    for token in ("", "wrong", m.AUTHORITY_TOKEN, m.EXPANSION_01_AUTHORITY_TOKEN,
                  m.EXPANSION_02_AUTHORITY_TOKEN, m.EXPANSION_03_AUTHORITY_TOKEN):
        with patch.object(m, "validate_expansion_block_03_request",
                          side_effect=AssertionError("validated after disabled dispatch")):
            with pytest.raises(m.Blocked, match="first-pass materialization not authorized"):
                m.materialize_expansion_block_03_request(
                    {}, authority_token=token, output=output, input_root=tmp_path)
            assert m.main(["materialize-expansion-03", "--authority-token", token]) == 1
    assert not output.exists()


def test_input_acceptance_does_not_supply_runtime_authority(accepted, tmp_path):
    # Accepted inputs and the command token alone still cannot enter the engine.
    request = request_for(accepted[0])
    with patch.object(m, "materializer_commit", return_value="a" * 40), \
            patch.object(m, "materializer_git_clean", return_value=True), \
            patch.object(m, "_materialize_checked", side_effect=AssertionError("entered engine")) as engine:
        with pytest.raises(m.Blocked) as rejection:
            m.materialize_expansion_block_03_request(
                request, authority_token=m.EXPANSION_03_AUTHORITY_TOKEN,
                output=tmp_path / "attempt", input_root=tmp_path)
        assert rejection.value.status == "BLOCKED_AUTHORITY"
        engine.assert_not_called()
    assert not (tmp_path / "attempt").exists()


def test_validate_and_plan_cli_only_accept_input(accepted, capsys):
    assert m.main(["validate-expansion-03"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result == {"status": "BLOCK_03_MATERIALIZER_INPUT_ACCEPTED", "cases": 7,
                      "materialization_authorized": False}
    assert m.main(["plan-expansion-03"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["materialization_authorized"] is False
    assert [(r["canonical_case_id"], r["revision_label"]) for r in result["ordered_future_identities"]] == [
        (case_id, label) for case_id in bridge.MEMBERS for label in ("BUGGY", "FIXED")]


def test_scientific_ledgers_unchanged_by_consumption():
    names = ["exclusions.csv", "cases_manifest.csv", "candidate_universe.csv",
             "expansion_block_03.csv", "expansion_block_03_traversal.csv",
             "expansion_block_02_environment_materialization.csv"]
    before = {name: (m.BENCHMARK / name).read_bytes() for name in names}
    bridge.load_inputs()
    assert {name: (m.BENCHMARK / name).read_bytes() for name in names} == before
    assert len(m.read_rows(m.BENCHMARK / "exclusions.csv")) == 34
    assert not m.read_rows(m.BENCHMARK / "cases_manifest.csv")

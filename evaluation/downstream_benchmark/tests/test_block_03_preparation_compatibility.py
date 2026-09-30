"""Preparation-only literal parsing, source binding, and deterministic regression."""

import csv
import io
import json
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest

from evaluation.downstream_benchmark.screening import (
    audit_environment, block_03_preparation_compatibility as bridge,
    build_recipes, executor, prepare_expansion_block_03 as preparation,
)


BENCHMARK = Path(__file__).resolve().parents[1]
WORK = Path("/Users/wuyangchenxi/errpilot-benchmark-work")
EXTERNAL = WORK / "expansion_block_03_preparation"


def _rows(data: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(data.decode("utf-8"))))


@pytest.mark.parametrize("argv", sorted(bridge.TOX_ARGV))
def test_literal_tox_argv_serializes_without_translation(argv: tuple[str, ...]) -> None:
    command = "  " + "\t".join(argv) + "  "
    result = bridge.analyze_oracle(command.encode())
    assert result["status"] == "RESOLVED_ORDERED_COMMANDS"
    assert result["commands"] == [command]
    assert bridge.parse_command(command) == argv
    data = {"commands": result["commands"], "argv": [list(bridge.parse_command(command))]}
    serialized = build_recipes.canonical_json(data)
    assert serialized == build_recipes.canonical_json(json.loads(serialized))
    assert build_recipes.sha256(serialized) == build_recipes.sha256(build_recipes.canonical_json(data))
    with pytest.raises(executor.PreparationError, match="unrecognized test command tox"):
        executor.parse_recognized_command(command)


@pytest.mark.parametrize("command", [
    "tox -e py36", "tox --", "tox tests/unobserved.py", "python -m tox", "tox4",
    "tox; pytest", "tox && pytest", "tox > output", "tox | cat", "tox $(id)",
    "TOXENV=py36 tox", "'tox'", "tox\r", "tox\n", "tox\x00", "/usr/bin/tox",
])
def test_nearby_or_unsafe_tox_forms_stay_unsupported(command: str) -> None:
    with pytest.raises(executor.PreparationError):
        bridge.parse_command(command)


def test_oracle_subcommand_order_duplicates_and_whole_script_bytes_are_preserved() -> None:
    command = "tox tests/test_hooks.py::TestExternalHooks::test_run_hook"
    script = ("# provenance\n\ntox\n" + command + "  \n" + command).encode()
    before = bytes(script)
    result = bridge.analyze_oracle(script)
    assert result["commands"] == ["tox", command + "  ", command]
    assert script == before
    assert result["oracle_command"] == ""
    blocked = bridge.analyze_oracle(script + b"\ntox -e guessed")
    assert blocked["status"] == "UNRESOLVED_UNSAFE_OR_UNRECOGNIZED_COMMAND_V1_1"
    assert blocked["blocking_reason"] == "subcommand 4: unrecognized test command tox"


def _setup_ledger(raw: bytes) -> str:
    return json.dumps([{"line": n, "category": bridge.classify_setup_line(line), "text": line}
                       for n, line in enumerate(raw.decode().splitlines(), 1)
                       if line.strip() and not line.lstrip().startswith("#")])


def test_develop_preserves_literal_text_source_ordinal_phase_and_deterministic_hash() -> None:
    raw = b"# first\n\npip install -r requirements.txt\npython setup.py develop\n"
    actions = bridge.setup_actions(raw, _setup_ledger(raw))
    assert [a["source_line_ordinal"] for a in actions] == [3, 4]
    assert [a["exact_source_text"] for a in actions] == [
        "pip install -r requirements.txt", "python setup.py develop",
    ]
    develop = actions[1]
    assert develop["classification"] == "PROJECT_INSTALL_OR_BUILD"
    assert develop["consumes_subject_source"] is True
    assert develop["mutates_source_workspace"] is True
    assert develop["dependency_input_binding"] == "AS_DECLARED"
    assert develop["future_execution_phase"] == "PHASE_4_PROJECT_BUILD_OR_INSTALL"
    assert build_recipes.environment_mode(actions) == "REVISION_SPECIFIC_BUILD_REQUIRED"
    assert build_recipes.canonical_json(actions) == build_recipes.canonical_json(
        bridge.setup_actions(raw, _setup_ledger(raw)))
    assert audit_environment.classify_setup_line("python setup.py develop") == "UNSUPPORTED_OR_AMBIGUOUS"
    with pytest.raises(build_recipes.RecipeError):
        bridge.setup_actions(raw, "[]")
    with pytest.raises(build_recipes.RecipeError):
        bridge.setup_actions(raw, json.dumps(list(reversed(json.loads(_setup_ledger(raw))))))


@pytest.mark.parametrize("command", [
    "python3 setup.py develop", "python setup.py develop --user",
    "python setup.py develop && pytest", "python setup.py develop # comment",
    "python setup.py develop_extra", "python ./setup.py develop", "python -m setup develop",
])
def test_nearby_develop_forms_stay_unsupported(command: str) -> None:
    assert bridge.classify_setup_line(command) == audit_environment.classify_setup_line(command)
    assert bridge.classify_setup_line(command) not in build_recipes.ALLOWED_SETUP
    with pytest.raises(build_recipes.RecipeError):
        bridge.setup_actions(command.encode(), _setup_ledger(command.encode()))


@pytest.mark.parametrize("command", [
    "pytest tests/test_x.py", "py.test -q", "python -m unittest test_x",
    "python3 -m pytest test_x", "pytest tests/test_x.py::literal'apostrophe",
])
def test_existing_oracle_commands_delegate_unchanged(command: str) -> None:
    assert bridge.parse_command(command) == executor.parse_recognized_command(command)
    assert bridge.analyze_oracle(command.encode()) == executor.analyze_oracle(command.encode())


def test_existing_setup_categories_and_absent_setup_delegate_unchanged() -> None:
    raw = b"# prior forms\npip install -e .\npython setup.py install\nmkdir fixture\n"
    assert bridge.setup_actions(raw, _setup_ledger(raw)) == build_recipes.setup_actions(raw, _setup_ledger(raw))
    assert bridge.setup_actions(None, "[]") == build_recipes.setup_actions(None, "[]")
    for command in ["", "# comment", "pytest tests/x.py", "nox", "python -m tox"]:
        assert bridge.analyze_oracle(command.encode()) == executor.analyze_oracle(command.encode())


def test_bridge_rejects_other_cases_or_drifted_frozen_sources() -> None:
    candidates = preparation.load_expansion_candidates(BENCHMARK)
    c = candidates[-2]
    case = WORK / "bugsinpy/projects/cookiecutter/bugs/2"
    script, setup = (case / "run_test.sh").read_bytes(), (case / "setup.sh").read_bytes()
    bridge.validate_case_sources(c, script, setup)
    for changed, oracle, install in [
        (candidates[0], script, setup), (replace(c, candidate_rank=471), script, setup),
        (replace(c, fixed_revision=c.buggy_revision), script, setup),
        (c, script + b"\n", setup), (c, script, b"pip install -e ."), (c, script, None),
    ]:
        with pytest.raises(executor.PreparationError, match="two frozen source identities"):
            bridge.validate_case_sources(changed, oracle, install)


def test_two_case_derivation_is_inert_exact_and_five_case_bytes_are_unchanged(monkeypatch) -> None:
    commands = []
    reprepared = []
    original_run = subprocess.run
    original_case = preparation._case

    def record_case(candidate, *args, **kwargs):
        if kwargs.get("compatibility_bridge"):
            reprepared.append(candidate.canonical_case_id)
        return original_case(candidate, *args, **kwargs)

    def read_only_git(argv, **kwargs):
        assert list(argv[:2]) == ["git", "-C"]
        assert argv[3] in {"rev-parse", "branch", "status", "remote", "cat-file"}
        if argv[3] == "remote":
            assert list(argv[4:]) == ["get-url", "origin"]
        if argv[3] == "cat-file":
            assert argv[4] == "blob"
        commands.append(list(argv))
        return original_run(argv, **kwargs)

    monkeypatch.setattr(subprocess, "run", read_only_git)
    monkeypatch.setattr(preparation, "_case", record_case)
    legacy, historical, _ = preparation.build_data(BENCHMARK, WORK / "bugsinpy", EXTERNAL)
    first = bridge.build_data(BENCHMARK, WORK / "bugsinpy", EXTERNAL)
    assert first == bridge.build_data(BENCHMARK, WORK / "bugsinpy", EXTERNAL)
    assert reprepared == ["cookiecutter::2", "cookiecutter::1"] * 2
    files, evidence, summary = first
    assert (summary["ready"], summary["blocked"]) == (7, 0)
    assert summary["reprepared_case_ids"] == ["cookiecutter::2", "cookiecutter::1"]
    assert summary["materialization_authorized"] is False
    assert len(evidence) == 6
    for key in ("plan", "environment", "recipes"):
        path = BENCHMARK / preparation.REPO_OUTPUTS[key]
        assert _rows(legacy[path])[:5] == _rows(files[path])[:5]
    for path, data in legacy.items():
        if path.name not in {preparation.REPO_OUTPUTS[k] for k in ("plan", "environment", "recipes")}:
            assert files[path] == data == path.read_bytes()
    for path, data in historical.items():
        assert path.read_bytes() == data
    for c in preparation.load_expansion_candidates(BENCHMARK)[-2:]:
        slug = c.canonical_case_id.replace("::", "__")
        case = WORK / "bugsinpy/projects" / c.project / "bugs" / c.bug_id
        prefix = BENCHMARK / bridge.EVIDENCE_ROOT / slug
        oracle = json.loads(evidence[prefix / "oracle_representation.json"])
        plan = json.loads(evidence[prefix / "preparation_plan.json"])
        env = json.loads(evidence[prefix / "environment_inputs.json"])
        assert oracle["commands"] == (case / "run_test.sh").read_text().splitlines()
        assert oracle["argv"] == [list(bridge.parse_command(x)) for x in oracle["commands"]]
        assert oracle["script_sha256"] == build_recipes.sha256((case / "run_test.sh").read_bytes())
        assert oracle["future_execution_cwd"] == env["future_execution_cwd"] == "subject repository root"
        assert oracle["source_provenance"] == env["source_provenance"] == bridge.source_provenance(c)
        assert oracle["executed"] is False and env["executed"] is False
        assert plan["execution_authorized"] is False and plan["subject_materialization"] == "UNBUILT"
        assert plan["buggy_commit_full"] == c.buggy_revision
        assert plan["fixed_commit_full"] == c.fixed_revision
        plan_hash = plan.pop("execution_plan_sha256")
        assert build_recipes.sha256(build_recipes.canonical_json(plan)) == plan_hash
        assert env["setup_actions"][0]["exact_source_text"] == "python setup.py develop"
        recipe = next(r for r in _rows(files[BENCHMARK / preparation.REPO_OUTPUTS["recipes"]])
                      if r["canonical_case_id"] == c.canonical_case_id)
        body = json.loads(recipe["build_recipe_json"])
        assert build_recipes.recipe_hash(body) == recipe["build_recipe_sha256"]
        assert body["setup_actions"] == env["setup_actions"]
        assert body["future_execution_cwd"] == "subject repository root"
        assert body["execution_plan_sha256"] == plan_hash
        assert body["materialization_identity"] == "UNBUILT"
    assert commands and all(argv[0] == "git" for argv in commands)

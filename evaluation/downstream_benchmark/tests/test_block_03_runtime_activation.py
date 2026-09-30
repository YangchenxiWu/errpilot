"""First-pass authority matrix with the real engine and processes firewalled."""

from __future__ import annotations

import json
import subprocess
from unittest.mock import patch

import pytest

from evaluation.downstream_benchmark.screening import block_03_materializer_bridge as bridge
from evaluation.downstream_benchmark.screening import block_03_runtime_activation as controller
from evaluation.downstream_benchmark.screening import materializer as m


@pytest.fixture(scope="module", autouse=True)
def runtime_firewall():
    run, popen = subprocess.run, subprocess.Popen

    def check_git(args, kwargs):
        assert isinstance(args, list) and args[0] == "git" and not kwargs.get("shell")
        pos = 3 if args[1] in ("-C", "--git-dir") else 1
        assert args[pos] in {"status", "rev-parse", "remote", "cat-file", "branch"}
        if args[pos] == "remote":
            assert args[pos + 1] == "get-url"
        if args[pos] == "branch":
            assert args[pos + 1:] == ["--show-current"]
        if args[pos] == "cat-file":
            assert args[pos + 1] == "-t" or (
                args[pos + 1] == "blob" and args[pos + 2] in {
                    f"{controller.BASELINE_COMMIT}:evaluation/downstream_benchmark/{name}"
                    for name in (controller.LIFECYCLE_FILE, bridge.AUTHORITY_FILE)
                })

    def readonly_run(args, *rest, **kwargs):
        check_git(args, kwargs)
        return run(args, *rest, **kwargs)

    def readonly_popen(args, *rest, **kwargs):
        check_git(args, kwargs)
        return popen(args, *rest, **kwargs)

    def forbidden(*args, **kwargs):
        raise AssertionError("real runtime crossed non-executing validation firewall")

    with patch.object(subprocess, "run", side_effect=readonly_run), \
            patch.object(subprocess, "Popen", side_effect=readonly_popen), \
            patch.object(m, "docker", side_effect=forbidden), \
            patch.object(m, "docker_observation", side_effect=forbidden), \
            patch.object(m, "_materialize_checked", side_effect=forbidden):
        yield


@pytest.fixture
def authority():
    # Explicit synthetic Human-PI invocation; no runnable authority file is saved
    # in the repository or the production work directory.
    return {
        "schema": "BLOCK_03_RUNTIME_ACTIVATION_AUTHORITY_V1",
        "transaction": "BLOCK_03_FIRST_PASS_MATERIALIZATION",
        "baseline_commit": "314229cc2dc6d4d1e8721a43e5b9189136a64b67",
        "block_identity_sha256": "883628cb72d4ddf56fdfd4a28c4b3c0752b429acf1b6c0abe382bbf7d666e780",
        "ordered_case_ids": ["tqdm::6", "PySnooper::3", "sanic::3", "sanic::5", "PySnooper::2",
                             "cookiecutter::2", "cookiecutter::1"],
        "ordered_candidate_ranks": [259, 369, 380, 405, 431, 472, 485],
        "materializer_input_authority_sha256": "8844f3b9a00e9c8a8d10c32112291d8f68ac883f5cc775425afbc559358b6a9e",
        "lifecycle_record_sha256": "8e76134f696f182b8910c0032b24e0027470f4debc375aa85aaa1f5c82a8ca6a",
        "authority_decision": "HUMAN_PI_AUTHORIZED",
    }


@pytest.fixture(scope="module")
def accepted():
    return bridge.load_inputs()


def request_for(item, label="BUGGY"):
    recipe = item["recipe"]
    return {
        "canonical_case_id": recipe["canonical_case_id"], "expansion_block": 3,
        "expansion_order": recipe["expansion_order"], "block_identity_sha256": bridge.BLOCK_SHA256,
        "materializer_input_authority_sha256": bridge.AUTHORITY_SHA256,
        "build_recipe_sha256": m.recipe_hash(recipe),
        "self_reference_ledger": item["self_reference_ledger"], **item["input_paths"],
        "revision_label": label, "revisions": [{"label": label, "sha": "0" * 64,
            "source": f"snapshots/{recipe['canonical_case_id'].replace('::', '__')}/{label.lower()}",
            "source_revision_sha": recipe[f"{label.lower()}_source_sha"]}],
    }


def invoke(authority, tmp_path, request=None, token=m.EXPANSION_03_AUTHORITY_TOKEN):
    return m.materialize_expansion_block_03_request(
        request or {}, authority_token=token, runtime_authority=authority,
        output=tmp_path / "attempt", input_root=tmp_path / "absent-inputs")


@pytest.mark.parametrize("value", [None, {}, [], "authorized", True])
def test_no_or_malformed_authority_rejected_before_input(value, tmp_path):
    with patch.object(m, "validate_expansion_block_03_request",
                      side_effect=AssertionError("input validation before authority")):
        with pytest.raises(m.Blocked) as result:
            invoke(value, tmp_path)
    assert result.value.status == "BLOCKED_AUTHORITY"
    assert not (tmp_path / "attempt").exists()


@pytest.mark.parametrize("field,value", [
    ("schema", "BLOCK_03_RUNTIME_ACTIVATION_AUTHORITY_V0"),
    ("transaction", "BLOCK_03_PREPARATION"),
    ("baseline_commit", "7b612f96a6715bb8b109d1152b2b1ac5e4b1bcf7"),
    ("block_identity_sha256", m.EXPANSION_02_BLOCK_SHA256),
    ("materializer_input_authority_sha256", "0" * 64),
    ("lifecycle_record_sha256", "0" * 64),
    ("authority_decision", "DENY"), ("authority_decision", True),
    ("ordered_candidate_ranks", [259.0, 369, 380, 405, 431, 472, 485]),
    ("ordered_candidate_ranks", [260, 369, 380, 405, 431, 472, 485]),
    ("build_recipe_sha256", "0" * 64),
])
def test_wrong_or_stale_binding_rejected(authority, tmp_path, field, value):
    authority[field] = value
    with pytest.raises(m.Blocked) as result:
        invoke(authority, tmp_path)
    assert result.value.status == "BLOCKED_AUTHORITY"
    assert not (tmp_path / "attempt").exists()


@pytest.mark.parametrize("mutation", ["missing", "extra", "duplicate", "reordered"])
def test_exact_ordered_membership_required(authority, tmp_path, mutation):
    members = authority["ordered_case_ids"]
    if mutation == "missing":
        members.pop()
    elif mutation == "extra":
        members.append("unknown::8")
    elif mutation == "duplicate":
        members[-1] = members[0]
    else:
        members[0], members[1] = members[1], members[0]
    with pytest.raises(m.Blocked) as result:
        invoke(authority, tmp_path)
    assert result.value.status == "BLOCKED_AUTHORITY"


@pytest.mark.parametrize("field", [
    "schema", "transaction", "baseline_commit", "ordered_case_ids", "ordered_candidate_ranks",
    "block_identity_sha256", "materializer_input_authority_sha256", "lifecycle_record_sha256",
    "authority_decision",
])
def test_missing_binding_field_denied(authority, tmp_path, field):
    authority.pop(field)
    with pytest.raises(m.Blocked) as result:
        invoke(authority, tmp_path)
    assert result.value.status == "BLOCKED_AUTHORITY"


@pytest.mark.parametrize("token", ["", "wrong", m.AUTHORITY_TOKEN,
    m.EXPANSION_01_AUTHORITY_TOKEN, m.EXPANSION_02_AUTHORITY_TOKEN])
def test_invalid_or_cross_block_token_denied(authority, tmp_path, token):
    with pytest.raises(m.Blocked) as result:
        invoke(authority, tmp_path, token=token)
    assert result.value.status == "BLOCKED_AUTHORITY"


def test_validation_is_inert_and_does_not_open_input_or_engine(authority):
    with patch.object(m, "validate_expansion_block_03_request",
                      side_effect=AssertionError("authority validation consumed input")):
        assert controller.validate_authority(authority) is None
        assert m.validate_expansion_block_03_runtime_authority(
            authority_token=m.EXPANSION_03_AUTHORITY_TOKEN, runtime_authority=authority) is None


@pytest.mark.parametrize("code,content", [(1, b""), (0, b"wrong committed identity")])
def test_missing_or_mismatched_committed_baseline_denied(authority, code, content):
    with patch.object(controller.subprocess, "run", return_value=subprocess.CompletedProcess(
            [], code, content, b"")):
        with pytest.raises(m.Blocked) as result:
            controller.validate_authority(authority)
    assert result.value.status == "BLOCKED_AUTHORITY"


def test_changed_local_accepted_authority_denied(authority, tmp_path, monkeypatch):
    monkeypatch.setattr(m, "BENCHMARK", tmp_path)
    (tmp_path / controller.LIFECYCLE_FILE).write_bytes(b"changed lifecycle")
    with pytest.raises(m.Blocked) as result:
        controller.validate_authority(authority)
    assert result.value.status == "BLOCKED_AUTHORITY"


@pytest.mark.parametrize("commit,clean", [(controller.BASELINE_COMMIT, False), ("UNAVAILABLE", True)])
def test_clean_committed_dispatch_remains_required(authority, tmp_path, commit, clean):
    with patch.object(m, "materializer_commit", return_value=commit), \
            patch.object(m, "materializer_git_clean", return_value=clean):
        with pytest.raises(m.Blocked) as result:
            invoke(authority, tmp_path)
    assert result.value.status == "BLOCKED_INPUT_IDENTITY"
    assert not (tmp_path / "attempt").exists()


def test_all_fourteen_exact_authorities_reach_only_nonexecuting_sentinel(authority, accepted, tmp_path):
    seen = []

    def sentinel(checked, **kwargs):
        assert kwargs == {"output": tmp_path / "attempt", "input_root": tmp_path / "absent-inputs",
                          "synthetic_only": False, "single_identity": True}
        seen.append((checked["canonical_case_id"], checked["revision_label"]))
        assert checked["recipe"]["materialization_identity"] == "UNBUILT"
        return {"status": "AUTHORITY_ACCEPTED"}

    with patch.object(m, "materializer_git_clean", return_value=True), \
            patch.object(m, "_materialize_checked", side_effect=sentinel) as engine:
        for item in accepted:
            for label in ("BUGGY", "FIXED"):
                assert invoke(authority, tmp_path, request_for(item, label)) == {"status": "AUTHORITY_ACCEPTED"}
        assert engine.call_count == 14
    assert seen == [(case, label) for case in bridge.MEMBERS for label in ("BUGGY", "FIXED")]
    assert not (tmp_path / "attempt").exists() and not (tmp_path / "absent-inputs").exists()


@pytest.mark.parametrize("field,value", [("build_recipe_sha256", "0" * 64),
    ("materializer_input_authority_sha256", "0" * 64), ("expansion_block", 2)])
def test_valid_authority_still_requires_accepted_request(authority, accepted, tmp_path, field, value):
    request = request_for(accepted[0])
    request[field] = value
    with patch.object(m, "materializer_git_clean", return_value=True):
        with pytest.raises(m.Blocked) as result:
            invoke(authority, tmp_path, request)
    assert result.value.status == "BLOCKED_INPUT_IDENTITY"


@pytest.mark.parametrize("dispatch", [m.materialize_expansion_block_01_request,
                                     m.materialize_expansion_block_02_request])
def test_block03_authority_cannot_authorize_other_dispatchers(authority, tmp_path, dispatch):
    with pytest.raises(m.Blocked) as result:
        dispatch({"runtime_authority": authority}, authority_token=m.EXPANSION_03_AUTHORITY_TOKEN,
                 output=tmp_path / "attempt", input_root=tmp_path)
    assert result.value.status == "BLOCKED_AUTHORITY"


@pytest.mark.parametrize("raw", [b"{", b"null", b"[]", b'{"schema":"a","schema":"b"}'])
def test_cli_malformed_authority_is_blocked_authority(raw, tmp_path, capsys):
    path = tmp_path / "authority.json"
    path.write_bytes(raw)
    assert m.main(["materialize-expansion-03", "--authority-token", m.EXPANSION_03_AUTHORITY_TOKEN,
                   "--runtime-authority", str(path)]) == 1
    assert capsys.readouterr().err.startswith("BLOCKED_AUTHORITY:")


def test_cli_absent_missing_and_symlink_authority_denied(tmp_path, capsys):
    base = ["materialize-expansion-03", "--authority-token", m.EXPANSION_03_AUTHORITY_TOKEN]
    assert m.main(base) == 1
    assert capsys.readouterr().err.startswith("BLOCKED_AUTHORITY:")
    missing = tmp_path / "absent.json"
    assert m.main(base + ["--runtime-authority", str(missing)]) == 1
    assert capsys.readouterr().err.startswith("BLOCKED_AUTHORITY:")
    link = tmp_path / "link.json"
    link.symlink_to(missing)
    assert m.main(base + ["--runtime-authority", str(link)]) == 1
    assert capsys.readouterr().err.startswith("BLOCKED_AUTHORITY:")


def test_cli_exact_authority_reaches_only_sentinel(authority, accepted, tmp_path, capsys):
    auth_path, request_path = tmp_path / "authority.json", tmp_path / "request.json"
    auth_path.write_text(json.dumps(authority))
    request_path.write_text(json.dumps(request_for(accepted[0])))
    with patch.object(m, "materializer_git_clean", return_value=True), \
            patch.object(m, "_materialize_checked", return_value={
                "status": "AUTHORITY_ACCEPTED", "attempt_id": "NON_EXECUTING_SENTINEL"}) as engine:
        assert m.main(["materialize-expansion-03", "--authority-token", m.EXPANSION_03_AUTHORITY_TOKEN,
                       "--runtime-authority", str(auth_path), "--request", str(request_path),
                       "--input-root", str(tmp_path / "absent-inputs"),
                       "--output", str(tmp_path / "attempt")]) == 1
        assert json.loads(capsys.readouterr().out)["status"] == "AUTHORITY_ACCEPTED"
        engine.assert_called_once()
    assert not (tmp_path / "attempt").exists() and not (tmp_path / "absent-inputs").exists()


def test_global_kill_switch_still_denies(authority, tmp_path, monkeypatch):
    monkeypatch.setattr(m, "REAL_MATERIALIZATION_ENABLED", False)
    with pytest.raises(m.Blocked) as result:
        invoke(authority, tmp_path)
    assert result.value.status == "BLOCKED_AUTHORITY"


def test_authority_and_sentinel_leave_scientific_state_and_attempts_unchanged(authority, accepted, tmp_path):
    names = ["candidate_universe.csv", "exclusions.csv", "cases_manifest.csv", "expansion_block_03.csv",
             "expansion_block_03_traversal.csv", bridge.AUTHORITY_FILE,
             "expansion_block_03_environment_build_recipes.csv", "expansion_block_03_execution_plan.csv"]
    before = {name: (m.BENCHMARK / name).read_bytes() for name in names}
    controller.validate_authority(authority)
    with patch.object(m, "materializer_git_clean", return_value=True), \
            patch.object(m, "_materialize_checked", return_value={"status": "AUTHORITY_ACCEPTED"}):
        invoke(authority, tmp_path, request_for(accepted[0]))
    assert {name: (m.BENCHMARK / name).read_bytes() for name in names} == before
    assert len(m.read_rows(m.BENCHMARK / "exclusions.csv")) == 34
    assert not m.read_rows(m.BENCHMARK / "cases_manifest.csv")
    assert not (tmp_path / "attempt").exists()

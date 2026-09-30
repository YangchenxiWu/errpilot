"""Zero-Docker checks for the Block 02 controller and pre-dispatch boundary."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from evaluation.downstream_benchmark.screening import materializer as m
from evaluation.downstream_benchmark.screening import materialize_expansion_block_02_batch as batch
from evaluation.downstream_benchmark.screening import executor


EXPECTED = [
    ("tornado::13", "SOURCE_INDEPENDENT", 1),
    ("tornado::4", "SOURCE_INDEPENDENT", 2),
    ("spacy::6", "BUGGY", 3),
    ("spacy::6", "FIXED", 3),
    ("fastapi::12", "SOURCE_INDEPENDENT", 4),
    ("tqdm::7", "BUGGY", 6),
    ("tqdm::7", "FIXED", 6),
    ("spacy::7", "BUGGY", 8),
    ("spacy::7", "FIXED", 8),
    ("httpie::5", "SOURCE_INDEPENDENT", 9),
    ("PySnooper::1", "BUGGY", 10),
    ("PySnooper::1", "FIXED", 10),
]


@pytest.fixture(scope="module", autouse=True)
def historical_v3_benchmark(tmp_path_factory: pytest.TempPathFactory):
    # Production remains pinned to V3; replay only its read-only checks in a fixture.
    benchmark = tmp_path_factory.mktemp("block-02-v3-ledger")
    for name in set(m.EXPANSION_02_FROZEN_SHA256) | {"candidate_universe.csv", "cases_manifest.csv"}:
        shutil.copy2(m.BENCHMARK / name, benchmark / name)
    shutil.copytree(m.BENCHMARK / "derived_inputs/expansion_block_02",
                    benchmark / "derived_inputs/expansion_block_02")
    predecessor = b"".join((m.BENCHMARK / "exclusions.csv").read_bytes().splitlines(
        keepends=True)[:30])
    assert m.sha256(predecessor) == m.EXPANSION_02_FROZEN_SHA256["exclusions.csv"]
    (benchmark / "exclusions.csv").write_bytes(predecessor)
    assert len(m.read_rows(benchmark / "exclusions.csv")) == 29
    check_ledger = m.check_expansion_block_02_ledger

    def validate_historical(path: Path) -> None:
        assert path == benchmark
        executor.validate_controlling_inputs(m.BENCHMARK)  # Current V4 authority remains checked.
        check_ledger(path)  # Exact V3 hashes and semantics remain checked independently.
        assert (path / "cases_manifest.csv").read_bytes() == (m.BENCHMARK / "cases_manifest.csv").read_bytes()

    with patch.object(batch, "BENCHMARK", benchmark), \
            patch.object(batch, "validate_controlling_inputs", side_effect=validate_historical), \
            patch.object(m, "check_expansion_block_02_ledger",
                         side_effect=lambda root=benchmark: check_ledger(root)):
        yield benchmark


@pytest.fixture(scope="module")
def requests(tmp_path_factory: pytest.TempPathFactory,
             historical_v3_benchmark: Path) -> list[dict]:
    work = tmp_path_factory.mktemp("block-02-derivation")
    root = work / "environment_materialization_expansion_block_02_v2"
    source_work = batch.WORK
    source_identity = batch._source_identity

    def frozen_source_identity(recipe: dict, label: str) -> tuple[Path, str]:
        # WORK also locates frozen source mirrors; retain their real read-only checks.
        with patch.object(batch, "WORK", source_work):
            return source_identity(recipe, label)

    with patch.object(batch, "WORK", work), patch.object(batch, "ROOT", root), \
            patch.object(batch, "_source_identity", side_effect=frozen_source_identity), \
            patch.object(m, "docker", side_effect=AssertionError("Docker called")), \
            patch.object(m, "_materialize_checked", side_effect=AssertionError("engine called")):
        derived = batch.derive_requests()
    assert not root.exists()
    return derived


@pytest.fixture
def isolated_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "environment_materialization_expansion_block_02_v2"
    monkeypatch.setattr(batch, "WORK", tmp_path)
    monkeypatch.setattr(batch, "ROOT", root)
    return root


def test_exact_derivation_and_zero_docker_preflight(requests: list[dict],
                                                  isolated_root: Path) -> None:
    assert [(r["canonical_case_id"], r["revision_label"], r["expansion_order"])
            for r in requests] == EXPECTED
    assert len(requests) == 12
    assert all(r["expansion_block"] == 2 for r in requests)
    assert not any(r["expansion_block"] == 1 for r in requests)
    assert not any(r["canonical_case_id"].startswith("cookiecutter::") for r in requests)
    assert not isolated_root.exists()


def test_all_hashes_paths_and_request_shapes(requests: list[dict]) -> None:
    recipes = {r["canonical_case_id"]: r for r in m.check_expansion_block_02_ledger()}
    self_rows = m.read_rows(m.BENCHMARK / "expansion_block_02_self_reference_ledger.csv")
    request_hashes = {(r["canonical_case_id"], r["revision_label"]): r["request_sha256"]
                      for r in m.read_rows(
                          m.BENCHMARK / "expansion_block_02_environment_materialization.csv")}
    for request in requests:
        case_id = request["canonical_case_id"]
        recipe = recipes[case_id]
        assert m.sha256(m.canonical_json(request) + b"\n") == request_hashes[
            case_id, request["revision_label"]]
        expected_ledger = [{k: v for k, v in row.items()
                            if k not in ("expansion_block", "expansion_order")}
                           for row in self_rows if row["canonical_case_id"] == case_id]
        assert request["expansion_order"] == recipe["expansion_order"]
        assert request["build_recipe_sha256"] == m.recipe_hash(recipe)
        assert request["block_identity_sha256"] == recipe["block_identity_sha256"]
        assert request["self_reference_ledger"] == expected_ledger
        namespace = f'derived_inputs/expansion_block_02/{case_id.replace("::", "__")}'
        assert request["normalized_requirements"] == f"{namespace}/requirements.normalized.txt"
        assert request["dependency_input"] == f"{namespace}/requirements.dependencies.txt"
        assert len(request["revisions"]) == 1
        revision = request["revisions"][0]
        if request["revision_label"] == "SOURCE_INDEPENDENT":
            assert revision == {"label": "SOURCE_INDEPENDENT", "sha": "ABSENT"}
        else:
            label = request["revision_label"]
            assert set(revision) == {"label", "sha", "source", "source_revision_sha"}
            assert revision["label"] == label
            assert revision["source_revision_sha"] == recipe[f"{label.lower()}_source_sha"]
            assert revision["source"] == f'snapshots/{case_id.replace("::", "__")}/{label.lower()}'
            assert m.HEX64.fullmatch(revision["sha"])
        assert m.validate_expansion_block_02_request(request)["recipe"] == recipe


def test_read_only_revision_hash_matches_staged_snapshot(tmp_path: Path) -> None:
    recipe = next(r for r in m.check_expansion_block_02_ledger()
                  if r["canonical_case_id"] == "PySnooper::1")
    expected = batch.source_snapshot_identity(recipe, "BUGGY")
    staged = tmp_path / "snapshot"
    assert batch.source_snapshot_identity(recipe, "BUGGY", staged) == expected
    assert m.snapshot_manifest(staged)[1] == expected


def test_pure_validator_matches_production_boundary(requests: list[dict]) -> None:
    request = requests[0]
    checked = m.validate_expansion_block_02_request(request)
    with patch.object(m, "materializer_commit", return_value="a" * 40), \
            patch.object(m, "materializer_git_clean", return_value=True), \
            patch.object(m, "_materialize_checked", return_value={"status": "MATERIALIZED"}) as engine:
        result = m.materialize_expansion_block_02_request(
            request, authority_token=m.EXPANSION_02_AUTHORITY_TOKEN,
            output=Path("unused"), input_root=Path("unused"),
        )
        assert result["status"] == "MATERIALIZED"
        assert engine.call_args.args[0] == checked
        engine.reset_mock()
        for token in (batch.BATCH_EXECUTION_TOKEN, m.EXPANSION_01_AUTHORITY_TOKEN):
            with pytest.raises(m.Blocked, match="Block 02 materialization authority unavailable"):
                m.materialize_expansion_block_02_request(
                    request, authority_token=token,
                    output=Path("unused"), input_root=Path("unused"),
                )
        engine.assert_not_called()
        with pytest.raises(m.Blocked, match="Block 02 request identity mismatch"):
            m.materialize_expansion_block_02_request(
                {**request, "expansion_block": 1},
                authority_token=m.EXPANSION_02_AUTHORITY_TOKEN,
                output=Path("unused"), input_root=Path("unused"),
            )
        engine.assert_not_called()


def test_exact_outer_batch_token_rejects_every_other_authority(isolated_root: Path) -> None:
    assert batch.BATCH_EXECUTION_TOKEN == (
        "BUGSINPY_EXPANSION_BLOCK_02_FIRST_PASS_BATCH_AUTHORIZED_V1"
    )
    assert batch.BATCH_EXECUTION_TOKEN != m.EXPANSION_02_AUTHORITY_TOKEN
    for token in ("", "wrong", m.EXPANSION_01_AUTHORITY_TOKEN,
                  m.EXPANSION_02_AUTHORITY_TOKEN):
        with patch.object(batch, "derive_requests",
                          side_effect=AssertionError("derived after rejected gate")), \
                patch.object(m, "materializer_git_clean",
                             side_effect=AssertionError("checked after rejected gate")):
            with pytest.raises(m.Blocked, match="invalid Block 02 batch token"):
                batch.dispatch(token)
        assert not isolated_root.exists()


def test_preflight_needs_no_batch_token(requests: list[dict],
                                       isolated_root: Path,
                                       capsys: pytest.CaptureFixture[str]) -> None:
    with patch.object(batch, "derive_requests", return_value=requests) as derive:
        assert batch.main(["preflight"]) == 0
        assert "12/12 Block 02 requests valid; zero production attempts" in capsys.readouterr().out
        assert batch.main(["preflight", "--batch-token", batch.BATCH_EXECUTION_TOKEN]) == 2
        assert "preflight accepts no batch token" in capsys.readouterr().err
        derive.assert_called_once_with()
    assert not isolated_root.exists()


def test_missing_dispatch_token_cli_rejects_before_derivation(
        isolated_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    with patch.object(batch, "derive_requests",
                      side_effect=AssertionError("derived after rejected gate")):
        assert batch.main(["dispatch"]) == 2
    assert "invalid Block 02 batch token" in capsys.readouterr().err
    assert not isolated_root.exists()


def test_valid_batch_token_reaches_only_mocked_dispatch_once_per_identity(
        requests: list[dict], isolated_root: Path) -> None:
    with patch.object(m, "materializer_git_clean", return_value=True), \
            patch.object(batch, "derive_requests", return_value=requests), \
            patch.object(batch, "_stage_inputs") as stage, \
            patch.object(batch, "_save_ledger") as save, \
            patch.object(batch, "_dispatch_one", return_value=True) as mocked_dispatch:
        batch.dispatch(batch.BATCH_EXECUTION_TOKEN)
    assert isolated_root.is_dir()
    assert mocked_dispatch.call_count == 12
    assert stage.call_count == save.call_count == 1
    dispatched = [(call.args[1]["canonical_case_id"], call.args[1]["revision_label"],
                   call.args[1]["expansion_order"]) for call in mocked_dispatch.call_args_list]
    assert dispatched == EXPECTED
    assert len(set(dispatched)) == 12
    assert all(not case.startswith("cookiecutter::") for case, _, _ in dispatched)


def test_preflight_refuses_existing_future_root(tmp_path: Path,
                                                monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(batch, "WORK", tmp_path)
    root = tmp_path / "environment_materialization_expansion_block_02_v2"
    root.mkdir()
    monkeypatch.setattr(batch, "ROOT", root)
    with pytest.raises(m.Blocked, match="must be absent"):
        batch.derive_requests()


def _fixture_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "fixture"
    root.mkdir()
    for name in ("requests", "controller_streams", "attempts"):
        (root / name).mkdir()
    monkeypatch.setattr(batch, "ROOT", root)
    return root


def test_pre_dispatch_rejection_preserves_controller_streams(
        requests: list[dict], tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _fixture_root(tmp_path, monkeypatch)
    request = requests[0]
    entry = batch._ledger_entry(request)
    ledger = [entry]
    completed = subprocess.CompletedProcess([], 1, b"raw stdout\n",
                                            b"BLOCKED_INPUT_IDENTITY: bad request\n")
    with patch.object(batch.subprocess, "run", return_value=completed) as invoked:
        assert not batch._dispatch_one(entry, request, ledger)
    invoked.assert_called_once()
    key = entry["key"]
    assert (root / "controller_streams" / f"{key}.stdout.raw").read_bytes() == completed.stdout
    assert (root / "controller_streams" / f"{key}.stderr.raw").read_bytes() == completed.stderr
    assert entry["return_code"] == 1
    assert entry["state"] == "PRE_DISPATCH_REJECTED"
    assert entry["governed_attempt_consumed"] is False
    assert "outcome" not in entry
    assert not (root / "attempts" / key).exists()
    assert json.loads((root / "identity_ledger.json").read_text())[0]["state"] == entry["state"]


def test_mock_governed_attempt_transitions_and_restart_safety(
        requests: list[dict], tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _fixture_root(tmp_path, monkeypatch)
    request = requests[0]
    entry = batch._ledger_entry(request)
    ledger = [entry]
    states: list[str] = []
    original_save = batch._save_ledger

    def record(rows: list[dict]) -> None:
        states.append(rows[0]["state"])
        original_save(rows)

    def fake_run(*_: object, **__: object) -> subprocess.CompletedProcess:
        attempt = root / "attempts" / entry["key"]
        attempt.mkdir()
        (attempt / "attempt.json").write_text(json.dumps({
            "attempt_id": entry["key"], "synthetic_only": False, "status": "MATERIALIZED",
        }))
        return subprocess.CompletedProcess([], 0, b"ok\n", b"")

    with patch.object(batch, "_save_ledger", side_effect=record), \
            patch.object(batch.subprocess, "run", side_effect=fake_run) as invoked:
        assert batch._dispatch_one(entry, request, ledger)
        assert states == ["PREPARED", "DISPATCH_STARTED", "DISPATCH_STARTED",
                          "GOVERNED_ATTEMPT_CREATED", "CLOSED"]
        assert entry["governed_attempt_consumed"] is True
        assert entry["outcome"] == "MATERIALIZED"
        with pytest.raises(m.Blocked, match="not unstarted"):
            batch._dispatch_one(entry, request, ledger)
        entry["state"] = "DISPATCH_STARTED"
        with pytest.raises(m.Blocked, match="not unstarted"):
            batch._dispatch_one(entry, request, ledger)
        entry["state"] = "GOVERNED_ATTEMPT_CREATED"
        with pytest.raises(m.Blocked, match="not unstarted"):
            batch._dispatch_one(entry, request, ledger)
        entry["state"] = "PRE_DISPATCH_REJECTED"
        with pytest.raises(m.Blocked, match="not unstarted"):
            batch._dispatch_one(entry, request, ledger)
        invoked.assert_called_once()
        command = invoked.call_args.args[0]
        assert command[command.index("--authority-token") + 1] == m.EXPANSION_02_AUTHORITY_TOKEN
        assert batch.BATCH_EXECUTION_TOKEN not in command
        assert m.EXPANSION_01_AUTHORITY_TOKEN not in command


def test_ambiguous_dispatch_without_attempt_blocks(
        requests: list[dict], tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _fixture_root(tmp_path, monkeypatch)
    request = requests[0]
    entry = batch._ledger_entry(request)
    completed = subprocess.CompletedProcess([], 1, b"partial", b"unknown failure")
    with patch.object(batch.subprocess, "run", return_value=completed):
        assert not batch._dispatch_one(entry, request, [entry])
    assert entry["state"] == "INFRASTRUCTURE_ABORT"
    assert entry["governed_attempt_consumed"] is False
    assert "outcome" not in entry


def test_block_01_and_initial_ledgers_still_validate() -> None:
    assert len(m.check_expansion_block_01_ledger()) == 10
    assert len(m.check_frozen_ledger()) == 40


def test_historical_incident_classification_and_root_remain_frozen() -> None:
    incident = (m.BENCHMARK / "EXPANSION_BLOCK_02_PRE_DISPATCH_INCIDENT_V1.md").read_text()
    for classification in ("CONTROLLER_PRE_DISPATCH_INVALID_REQUEST",
                           "NON_PRODUCTION_ATTEMPT",
                           "ABORTED_BEFORE_FIRST_PRODUCTION_ATTEMPT"):
        assert classification in incident
    old_root = batch.WORK / "environment_materialization_expansion_block_02"
    files = {path.relative_to(old_root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
             for path in old_root.rglob("*") if path.is_file()}
    digest = hashlib.sha256(json.dumps(files, sort_keys=True,
                                       separators=(",", ":")).encode()).hexdigest()
    assert len(files) == 10
    assert digest == "1cea074fbac40c465bff0b3a76f1fbfcca8b79da3e0a14d38af47ad44a6a50bb"
    assert not any((old_root / "attempts").iterdir())

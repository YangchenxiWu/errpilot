"""Zero-Docker checks for the Block 02 controller and pre-dispatch boundary."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from evaluation.downstream_benchmark.screening import materializer as m
from evaluation.downstream_benchmark.screening import materialize_expansion_block_02_batch as batch


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


@pytest.fixture(scope="module")
def requests() -> list[dict]:
    with patch.object(m, "docker", side_effect=AssertionError("Docker called")), \
            patch.object(m, "_materialize_checked", side_effect=AssertionError("engine called")):
        return batch.derive_requests()


def test_exact_derivation_and_zero_docker_preflight(requests: list[dict]) -> None:
    assert [(r["canonical_case_id"], r["revision_label"], r["expansion_order"])
            for r in requests] == EXPECTED
    assert len(requests) == 12
    assert all(r["expansion_block"] == 2 for r in requests)
    assert not any(r["expansion_block"] == 1 for r in requests)
    assert not any(r["canonical_case_id"].startswith("cookiecutter::") for r in requests)
    assert not batch.ROOT.exists()


def test_all_hashes_paths_and_request_shapes(requests: list[dict]) -> None:
    recipes = {r["canonical_case_id"]: r for r in m.check_expansion_block_02_ledger()}
    self_rows = m.read_rows(m.BENCHMARK / "expansion_block_02_self_reference_ledger.csv")
    for request in requests:
        case_id = request["canonical_case_id"]
        recipe = recipes[case_id]
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
        with pytest.raises(m.Blocked, match="Block 02 request identity mismatch"):
            m.materialize_expansion_block_02_request(
                {**request, "expansion_block": 1},
                authority_token=m.EXPANSION_02_AUTHORITY_TOKEN,
                output=Path("unused"), input_root=Path("unused"),
            )
        engine.assert_not_called()


def test_current_batch_execution_gate_is_unusable(requests: list[dict]) -> None:
    assert batch.BATCH_EXECUTION_TOKEN is None
    with patch.object(batch, "derive_requests", side_effect=AssertionError("derived after gate")):
        with pytest.raises(m.Blocked, match="batch token not configured"):
            batch.dispatch("arbitrary")
    assert not batch.ROOT.exists()


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

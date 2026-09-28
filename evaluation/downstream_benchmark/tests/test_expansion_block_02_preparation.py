"""Frozen Block 02 membership and fail-closed metadata loading."""

from pathlib import Path

import pytest

from evaluation.downstream_benchmark.screening import executor
from evaluation.downstream_benchmark.screening.prepare_expansion_block_02 import (
    FROZEN_LEDGER_SHA256,
    load_expansion_candidates,
)


BENCHMARK = Path(__file__).resolve().parents[1]
INPUTS = (
    "PROTOCOL.md", "RUN_SPEC_V1.md", "SCREENING_SPEC_V1.md",
    "candidate_universe.csv", "cases_manifest.csv", "exclusions.csv",
    "initial_40_build_failure_adjudication_v1.csv", "expansion_block_01.csv",
    "expansion_block_01_build_failure_adjudication_v1.csv",
    "expansion_block_01_environment_materialization.csv",
    "expansion_block_02_traversal.csv", "EXPANSION_BLOCK_02.md",
)


def test_loads_exact_frozen_block_02_without_prior_membership() -> None:
    candidates = load_expansion_candidates(BENCHMARK)
    assert [c.canonical_case_id for c in candidates] == [
        "tornado::13", "tornado::4", "spacy::6", "fastapi::12",
        "cookiecutter::3", "tqdm::7", "cookiecutter::4", "spacy::7",
        "httpie::5", "PySnooper::1",
    ]
    assert [c.selection_order for c in candidates] == list(range(1, 11))
    assert len(executor.load_frozen_candidates(BENCHMARK)) == 40


def test_rejects_block_02_metadata_drift(tmp_path: Path) -> None:
    for name in set(INPUTS) | set(FROZEN_LEDGER_SHA256):
        (tmp_path / name).write_bytes((BENCHMARK / name).read_bytes())
    block = tmp_path / "expansion_block_02.csv"
    block.write_text(
        block.read_text().replace("tornado::13", "tornado::12", 1),
        encoding="utf-8",
    )
    with pytest.raises(executor.PreparationError, match="expansion_block_02.csv"):
        load_expansion_candidates(tmp_path)

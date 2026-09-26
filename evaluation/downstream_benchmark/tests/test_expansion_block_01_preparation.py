"""Frozen expansion membership and fail-closed metadata loading."""

from pathlib import Path

import pytest

from evaluation.downstream_benchmark.screening import executor
from evaluation.downstream_benchmark.screening.prepare_expansion_block_01 import (
    FROZEN_LEDGER_SHA256,
    load_expansion_candidates,
)


BENCHMARK = Path(__file__).resolve().parents[1]
INPUTS = (
    "PROTOCOL.md", "RUN_SPEC_V1.md", "SCREENING_SPEC_V1.md",
    "candidate_universe.csv", "cases_manifest.csv", "exclusions.csv",
    "initial_40_build_failure_adjudication_v1.csv", "expansion_block_01.csv",
    "expansion_block_01_traversal.csv", "EXPANSION_BLOCK_01.md",
)


def test_loads_exact_frozen_expansion_without_extending_initial_40() -> None:
    expansion = load_expansion_candidates(BENCHMARK)
    assert [c.canonical_case_id for c in expansion] == [
        "tornado::11", "matplotlib::21", "youtube-dl::24", "tqdm::1",
        "black::6", "luigi::6", "black::15", "thefuck::8", "sanic::2",
        "luigi::20",
    ]
    assert [c.selection_order for c in expansion] == list(range(1, 11))
    assert len(executor.load_frozen_candidates(BENCHMARK)) == 40


def test_rejects_block_metadata_drift(tmp_path: Path) -> None:
    for name in set(INPUTS) | set(FROZEN_LEDGER_SHA256):
        (tmp_path / name).write_bytes((BENCHMARK / name).read_bytes())
    block = tmp_path / "expansion_block_01.csv"
    block.write_text(
        block.read_text().replace("tornado::11", "tornado::12", 1),
        encoding="utf-8",
    )
    with pytest.raises(executor.PreparationError, match="frozen ledger drift"):
        load_expansion_candidates(tmp_path)

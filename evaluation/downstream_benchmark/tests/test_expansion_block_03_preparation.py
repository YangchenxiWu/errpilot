"""Preparation-only terminal membership and frozen-input rejection checks."""

from pathlib import Path

import pytest

from evaluation.downstream_benchmark.screening import executor
from evaluation.downstream_benchmark.screening.prepare_expansion_block_03 import (
    FROZEN_LEDGER_SHA256,
    load_expansion_candidates,
    write_new_files,
)


BENCHMARK = Path(__file__).resolve().parents[1]


def _copy_inputs(destination: Path) -> None:
    # Include current normative sources rather than a predecessor's ledger set.
    inputs = set(BENCHMARK.glob("*.csv")) | set(BENCHMARK.glob("*.md"))
    inputs.update(BENCHMARK / name for name in FROZEN_LEDGER_SHA256)
    for source in inputs:
        target = destination / source.relative_to(BENCHMARK)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())


def test_loads_exact_terminal_seven_without_extending_prior_blocks() -> None:
    candidates = load_expansion_candidates(BENCHMARK)
    assert [(c.candidate_rank, c.canonical_case_id) for c in candidates] == [
        (259, "tqdm::6"), (369, "PySnooper::3"), (380, "sanic::3"),
        (405, "sanic::5"), (431, "PySnooper::2"),
        (472, "cookiecutter::2"), (485, "cookiecutter::1"),
    ]
    assert [c.selection_order for c in candidates] == list(range(1, 8))
    assert len(executor.load_frozen_candidates(BENCHMARK)) == 40


@pytest.mark.parametrize(
    ("name", "before", "after"),
    [
        ("expansion_block_03.csv", "tqdm::6", "tqdm::7"),
        ("EXPANSION_BLOCK_03.md", '"block_size":7', '"block_size":8'),
        ("expansion_block_03_traversal.csv", "SKIP_PROJECT_CAP", "ADMIT"),
        ("exclusions.csv", "DEPENDENCY_SETUP_FAILURE", "ORACLE_COMMAND_INVALID"),
        ("screening/build_recipes.py", "EXPLICIT_SETUP_ACTIONS_ONLY", "IMPLICIT_INSTALL"),
    ],
)
def test_rejects_frozen_input_drift(
    tmp_path: Path, name: str, before: str, after: str,
) -> None:
    _copy_inputs(tmp_path)
    assert len(load_expansion_candidates(tmp_path)) == 7
    target = tmp_path / name
    original = target.read_text()
    assert before in original
    target.write_text(original.replace(before, after, 1), encoding="utf-8")
    with pytest.raises(executor.PreparationError):
        load_expansion_candidates(tmp_path)


def test_write_preflight_preserves_existing_files(tmp_path: Path) -> None:
    existing = tmp_path / "existing.json"
    new = tmp_path / "new.json"
    existing.write_bytes(b"preserved evidence\n")
    with pytest.raises(executor.PreparationError, match="refusing to overwrite"):
        write_new_files({new: b"new\n", existing: b"replacement\n"})
    assert existing.read_bytes() == b"preserved evidence\n"
    assert not new.exists()

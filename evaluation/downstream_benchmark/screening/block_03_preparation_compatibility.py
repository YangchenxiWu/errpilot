"""Inert Block-03-only literal representation bridge; no execution authority.

The shared frozen parsers stay unchanged. Only bare tox and the three observed
tox argv forms are added, together with exactly python setup.py develop.
Historical external evidence is read-only; changed JSON is saved in the repo.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path

from . import audit_environment, build_recipes, executor


AUTHORITY = "BLOCK_03_PREPARATION_COMPATIBILITY_BRIDGE_V1"
PREVIOUS_REPORT_SHA256 = "e797ff2ac48b4ac379fb15c25fe805ce1077a06b56a5603082aba48dbcbda829"
SETUP_SHA256 = "3d7b5491b985872ef7604a0c7730a7cd6a9a20371b3697e5dff279588c2324b3"
SOURCE_IDENTITIES = {
    "cookiecutter::2": (472, 6, "d7e7b28811e474e14d1bed747115e47dcdd15ba3",
                        "90434ff4ea4477941444f1e83313beb414838535",
                        "d1afcc0a9c7c285eba2cd8697752e3d4ce55e5dc2710606c18a43817ef360cc0"),
    "cookiecutter::1": (485, 7, "c15633745df6abdb24e02746b82aadb20b8cdf8c",
                        "7f6804c4953a18386809f11faf4d86898570debc",
                        "8fa48fdd88c886fbdf244124c952d919743b1c4ca407a0b4d50d091d9fab4b34"),
}
TOX_ARGV = frozenset({
    ("tox",),
    ("tox", "tests/test_hooks.py::TestFindHooks::test_find_hook"),
    ("tox", "tests/test_hooks.py::TestExternalHooks::test_run_hook"),
    ("tox", "tests/test_generate_context.py::test_generate_context_decodes_non_ascii_chars"),
})
EVIDENCE_ROOT = "evidence/block_03_preparation_compatibility_bridge_v1"


def validate_case_sources(candidate: executor.Candidate, script: bytes, setup: bytes | None) -> None:
    observed = (candidate.candidate_rank, candidate.selection_order,
                candidate.buggy_revision, candidate.fixed_revision, build_recipes.sha256(script))
    if (SOURCE_IDENTITIES.get(candidate.canonical_case_id) != observed
            or setup is None or build_recipes.sha256(setup) != SETUP_SHA256):
        raise executor.PreparationError("compatibility bridge is limited to the two frozen source identities")


def source_provenance(candidate: executor.Candidate) -> dict[str, str]:
    return {"representation_authority": AUTHORITY, "bugsinpy_commit": executor.BUGSINPY_COMMIT,
            "bugsinpy_tree": executor.BUGSINPY_TREE,
            "metadata_directory": f"projects/{candidate.project}/bugs/{candidate.bug_id}"}


def parse_command(command: str) -> tuple[str, ...]:
    tokens = tuple(command.split())
    if tokens not in TOX_ARGV:
        return executor.parse_recognized_command(command)
    # Retain the shared no-shell boundary even for the finite literal whitelist.
    if (any(c in command for c in ("\r", "\n", "\x00"))
            or executor._SHELL_CONTROL.search(command)
            or executor._UNSAFE_COMMAND_TEXT.search(command)
            or any(c in command for c in "&#()")):
        raise executor.PreparationError("shell syntax or expansion is unsupported")
    return tokens


def analyze_oracle(script: bytes) -> dict[str, object]:
    original = executor.analyze_oracle(script)
    if original["status"] != "UNRESOLVED_UNSAFE_OR_UNRECOGNIZED_COMMAND_V1_1":
        return original
    for ordinal, command in enumerate(original["commands"], 1):
        try:
            parse_command(command)
        except executor.PreparationError as exc:
            return {**original, "blocking_reason": f"subcommand {ordinal}: {exc}"}
    return {**original, "status": "RESOLVED_ORDERED_COMMANDS",
            "shell_requirement": "POSIX_ARGV_IN_CASE_ENVIRONMENT", "blocking_reason": ""}


def classify_setup_line(line: str) -> str:
    if line.strip() == "python setup.py develop":
        return "PROJECT_INSTALL_OR_BUILD"
    return audit_environment.classify_setup_line(line)


def setup_actions(raw: bytes | None, frozen_json: str) -> list[dict[str, object]]:
    if raw is None:
        return build_recipes.setup_actions(raw, frozen_json)
    actions = []
    for ordinal, line in enumerate(raw.decode("utf-8", errors="strict").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        category = classify_setup_line(line)
        if line.strip() == "python setup.py develop":
            action = {"source_line_ordinal": ordinal, "exact_source_text": line,
                      "classification": category, "consumes_subject_source": True,
                      "requires_network": False, "mutates_source_workspace": True,
                      "future_execution_phase": "PHASE_4_PROJECT_BUILD_OR_INSTALL",
                      "dependency_input_binding": "AS_DECLARED"}
        else:
            ledger = json.dumps([{"line": 1, "category": category, "text": line}])
            action = build_recipes.setup_actions(line.encode("utf-8"), ledger)[0]
            action["source_line_ordinal"] = ordinal
        actions.append(action)
    if [{"line": a["source_line_ordinal"], "category": a["classification"],
         "text": a["exact_source_text"]} for a in actions] != json.loads(frozen_json):
        raise build_recipes.RecipeError("setup classification/order differs from frozen ledger")
    return actions


def build_data(benchmark: Path, bugsinpy: Path, external: Path) -> tuple[
    dict[Path, bytes], dict[Path, bytes], dict[str, object]
]:
    """Regenerate the two cases in memory and retain all five prior rows exactly."""
    from . import prepare_expansion_block_03 as preparation

    report = benchmark / "EXPANSION_BLOCK_03_PREPARATION_V1.md"
    if build_recipes.sha256(report.read_bytes()) != PREVIOUS_REPORT_SHA256:
        raise executor.PreparationError("previous preparation report drift")
    original, historical, old_summary = preparation.build_data(benchmark, bugsinpy, external)
    if (old_summary["ready"], old_summary["blocked"]) != (5, 2):
        raise executor.PreparationError("previous five-ready/two-blocked representation drift")
    for path, data in historical.items():
        if not path.is_file() or path.read_bytes() != data:
            raise executor.PreparationError(f"historical evidence drift: {path}")
    updated = dict(original)
    evidence_files: dict[Path, bytes] = {}
    changed_rows = {}
    for candidate in preparation.load_expansion_candidates(benchmark):
        if candidate.canonical_case_id not in SOURCE_IDENTITIES:
            continue
        mirror = executor.acquire_project_mirror(
            candidate.project, candidate.source_url, external.parent / "subject_repositories",
            allow_network=False,
        )
        plan, env, norm, recipe, self_rows, derived, evidence = preparation._case(
            candidate, benchmark, bugsinpy, mirror, external, compatibility_bridge=True,
        )
        for path, data in derived.items():
            if data != original[path] or path.read_bytes() != data:
                raise executor.PreparationError(f"derived input drift: {path}")
        slug = candidate.canonical_case_id.replace("::", "__")
        for path, data in evidence.items():
            if data != historical[path]:
                relative = path.relative_to(external)
                evidence_files[benchmark / EVIDENCE_ROOT / relative] = data
        changed_rows[candidate.canonical_case_id] = (plan, env, recipe)
        # Normalization and self-reference handling are outside this bridge.
        old_norm = next(r for r in preparation._csv(benchmark / preparation.REPO_OUTPUTS["normalization"])
                        if r["canonical_case_id"] == candidate.canonical_case_id)
        old_self = [r for r in preparation._csv(benchmark / preparation.REPO_OUTPUTS["self"])
                    if r["canonical_case_id"] == candidate.canonical_case_id]
        if norm != old_norm or self_rows != old_self:
            raise executor.PreparationError(f"normalization/self-reference drift: {slug}")
    for index, (key, fields) in enumerate((
        ("plan", preparation.PLAN_FIELDS), ("environment", preparation.ENV_FIELDS),
        ("recipes", preparation.RECIPE_FIELDS),
    )):
        path = benchmark / preparation.REPO_OUTPUTS[key]
        rows = preparation._csv(path)
        baseline_rows = list(csv.DictReader(io.StringIO(original[path].decode())))
        expected = [changed_rows[r["canonical_case_id"]][index]
                    if r["canonical_case_id"] in changed_rows else r for r in baseline_rows]
        if rows != baseline_rows and rows != expected:
            raise executor.PreparationError(f"candidate ledger differs from prior or bridge representation: {path}")
        updated[path] = preparation._csv_bytes(fields, expected)
    # Every other generated repository byte is immutable in this transaction.
    for path, data in updated.items():
        if data == original[path] and path.read_bytes() != data:
            raise executor.PreparationError(f"unchanged preparation artifact drift: {path}")
    return updated, evidence_files, {
        "ready": 5 + sum(r[0]["preparation_status"] == "EXPANSION_PREPARATION_READY" for r in changed_rows.values()),
        "blocked": sum(r[0]["preparation_status"] == "EXPANSION_PREPARATION_BLOCKED" for r in changed_rows.values()),
        "reprepared_case_ids": list(changed_rows), "historical_evidence_rewritten": False,
        "materialization_authorized": False,
    }


def main() -> None:
    from . import prepare_expansion_block_03 as preparation

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("inspect", "prepare", "verify"))
    args = parser.parse_args()
    benchmark = Path(__file__).resolve().parents[1]
    work = Path("/Users/wuyangchenxi/errpilot-benchmark-work")
    repo_files, evidence, summary = build_data(
        benchmark, work / "bugsinpy", work / "expansion_block_03_preparation",
    )
    if args.mode == "prepare":
        # Fail before any write on an existing versioned evidence file.
        preparation.write_new_files(evidence)
        for path, data in repo_files.items():
            if path.read_bytes() != data:
                path.write_bytes(data)
    elif args.mode == "verify":
        for path, data in {**repo_files, **evidence}.items():
            if not path.is_file() or path.read_bytes() != data:
                raise executor.PreparationError(f"bridge regeneration differs: {path}")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()

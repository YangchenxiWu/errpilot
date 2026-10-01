"""Local-only gitlink export, provenance identity, and fail-closed regressions."""

from __future__ import annotations

import base64
import io
import os
import runpy
from pathlib import Path
from unittest.mock import patch

import pytest

from evaluation.downstream_benchmark.screening import block_03_gitlink_source_export as g
from evaluation.downstream_benchmark.screening import block_03_materializer_bridge as bridge
from evaluation.downstream_benchmark.screening import materialize_expansion_block_02_batch as batch
from evaluation.downstream_benchmark.screening import materializer as m


REVISION = g.REVISIONS[("cookiecutter::2", "BUGGY")]
RECIPE = {"canonical_case_id": "cookiecutter::2", "expansion_block": 3}
MODULES = (f'[submodule "{g.PATH}"]\n\tpath = {g.PATH}\n\turl = {g.URL}\n').encode()
LINK = (g.PATH.encode(), b"160000", b"commit", g.OBJECT.encode())


class BlobProcess:
    """In-memory cat-file stream; no Git process or subject code is executed."""

    def __init__(self, blobs: dict[bytes, bytes]) -> None:
        self.blobs = blobs
        self.stdout = io.BytesIO()
        self.stdin = self
        self.returncode = 0

    def write(self, query: bytes) -> None:
        oid = query.strip()
        content = self.blobs[oid]
        self.stdout = io.BytesIO(oid + b" blob " + str(len(content)).encode()
                                + b"\n" + content + b"\n")

    def flush(self) -> None:
        pass

    def close(self) -> None:
        pass

    def wait(self) -> None:
        pass


def export_fixture(tmp_path: Path, *, recipe: dict | None = None,
                   links: list | None = None, modules: bytes | None = MODULES,
                   module_mode: bytes = b"100644") -> tuple[Path, str]:
    blobs = {b"a" * 40: b"plain\x00bytes\n", b"b" * 40: b"#!/bin/sh\n",
             b"c" * 40: b"missing-\xff"}
    rows = [(b"plain.txt", b"100644", b"a" * 40),
            (b"run.sh", b"100755", b"b" * 40), (b"link", b"120000", b"c" * 40)]
    if modules is not None:
        blobs[b"d" * 40] = modules
        rows.append((b".gitmodules", module_mode, b"d" * 40))
    listing = b"".join(mode + b" blob " + oid + b"\t" + path + b"\0"
                       for path, mode, oid in rows)
    for path, mode, kind, oid in [LINK] if links is None else links:
        listing += mode + b" " + kind + b" " + oid + b"\t" + path + b"\0"

    def git(_mirror, *args):
        if args == ("ls-tree", "-rz", "--full-tree", REVISION):
            return listing
        if args[:2] == ("cat-file", "blob"):
            return blobs[args[2].encode()]
        raise AssertionError(f"unapproved Git operation: {args}")

    destination = tmp_path / "source"
    with patch.object(batch, "_source_identity", return_value=(tmp_path / "mirror", REVISION)), \
            patch.object(batch, "_run_git", side_effect=git), \
            patch.object(batch.subprocess, "Popen", return_value=BlobProcess(blobs)) as popen:
        digest = batch.source_snapshot_identity(RECIPE if recipe is None else recipe,
                                               "BUGGY", destination)
    assert popen.call_args.args[0] == ["git", "--git-dir", str(tmp_path / "mirror"),
                                     "cat-file", "--batch"]
    return destination, digest


def test_export_empty_directory_and_identity_bearing_provenance(tmp_path: Path) -> None:
    source, digest = export_fixture(tmp_path)
    placeholder = source / g.PATH
    assert placeholder.is_dir() and not placeholder.is_symlink()
    assert list(placeholder.iterdir()) == []
    manifest, actual = m.snapshot_manifest(source)
    assert actual == digest
    assert manifest["gitlink_provenance"] == g.provenance(REVISION)
    assert g.sidecar_path(source).read_bytes() == m.canonical_json(g.provenance(REVISION))
    assert all(entry["path"] != g.PATH for entry in manifest["entries"])
    assert not any(entry["path"].endswith(".gitlinks.json") for entry in manifest["entries"])
    ordinary = {k: v for k, v in manifest.items() if k != "gitlink_provenance"}
    assert m.sha256(m.canonical_json(ordinary)) != digest


def test_regular_executable_symlink_bytes_and_old_identity_unchanged(tmp_path: Path) -> None:
    source, digest = export_fixture(tmp_path, recipe={"canonical_case_id": "fixture"},
                                    links=[], modules=None)
    expected = {"schema": "SOURCE_SNAPSHOT_MANIFEST_V2", "entries": [
        {"path": "link", "entry_type": "symlink",
         "target_b64": base64.b64encode(b"missing-\xff").decode(),
         "target_sha256": m.sha256(b"missing-\xff")},
        {"path": "plain.txt", "entry_type": "file",
         "content_sha256": m.sha256(b"plain\x00bytes\n"), "mode": 0o644},
        {"path": "run.sh", "entry_type": "file",
         "content_sha256": m.sha256(b"#!/bin/sh\n"), "mode": 0o755},
    ]}
    assert m.snapshot_manifest(source) == (expected, m.sha256(m.canonical_json(expected)))
    assert digest == m.sha256(m.canonical_json(expected))
    assert (source / "plain.txt").read_bytes() == b"plain\x00bytes\n"
    assert (source / "run.sh").stat().st_mode & 0o777 == 0o755
    assert os.readlink(os.fsencode(source / "link")) == b"missing-\xff"
    assert not g.sidecar_path(source).exists()


def test_repeated_export_bytes_manifests_and_provenance_are_deterministic(tmp_path: Path) -> None:
    first, digest = export_fixture(tmp_path / "first")
    second, again = export_fixture(tmp_path / "second")
    assert digest == again
    assert m.canonical_json(m.snapshot_manifest(first)[0]) == m.canonical_json(
        m.snapshot_manifest(second)[0])
    assert g.sidecar_path(first).read_bytes() == g.sidecar_path(second).read_bytes()


@pytest.mark.parametrize("modules", [
    None, b"", b"malformed", MODULES.replace(g.PATH.encode(), b"wrong/path"),
    MODULES.replace(g.URL.encode(), b"https://example.org/wrong"),
    MODULES.replace(g.URL.encode(), b"../relative"),
    MODULES + b"\tpath = wrong/path\n",
    MODULES + b'[submodule "other"]\npath = docs/HelloCookieCutter1\nurl = wrong\n',
    MODULES + b'[submodule "nested"]\npath = docs/HelloCookieCutter1/nested\nurl = wrong\n',
    MODULES + b"\tupdate = checkout\n", MODULES + b"[DEFAULT]\nurl = wrong\n",
    MODULES + b"\xff",
], ids=["missing", "empty", "malformed", "wrong-path", "wrong-url", "relative-url",
        "duplicate-key", "conflicting-section", "nested-mapping", "extra-options",
        "defaults", "invalid-utf8"])
def test_bad_gitmodules_blocks_before_export(tmp_path: Path, modules: bytes | None) -> None:
    with pytest.raises(m.Blocked):
        export_fixture(tmp_path, modules=modules)
    assert not (tmp_path / "source").exists()


@pytest.mark.parametrize("links", [
    [], [(LINK[0], b"160000", b"commit", b"e" * 40)],
    [(LINK[0], b"160000", b"blob", LINK[3])],
    [(b"wrong/path", *LINK[1:])], [LINK, (b"docs/HelloCookieCutter1/nested", *LINK[1:])],
    [(LINK[0], b"100644", b"blob", b"a" * 40)],
    [(LINK[0], b"120000", b"blob", b"c" * 40)], [LINK, LINK],
    [(LINK[0], b"160001", b"commit", LINK[3])],
], ids=["silently-dropped", "wrong-object", "wrong-kind", "wrong-path", "nested",
        "regular-file-substitution", "symlink-substitution", "duplicate", "wrong-mode"])
def test_unrepresentable_tree_blocks_before_export(tmp_path: Path, links: list) -> None:
    with pytest.raises(m.Blocked):
        export_fixture(tmp_path, links=links)
    assert not (tmp_path / "source").exists()


@pytest.mark.parametrize("recipe", [
    {**RECIPE, "expansion_block": 2}, {**RECIPE, "canonical_case_id": "cookiecutter::3"},
    {**RECIPE, "expansion_block": 3.0},
])
def test_no_future_or_historical_gitlink_policy(tmp_path: Path, recipe: dict) -> None:
    with pytest.raises(m.Blocked):
        export_fixture(tmp_path, recipe=recipe)


def test_wrong_superproject_revision_blocks() -> None:
    with pytest.raises(m.Blocked):
        g.derive(RECIPE, "BUGGY", "f" * 40, [LINK], MODULES)


@pytest.mark.parametrize("mode", [b"100755", b"120000"])
def test_gitmodules_must_be_plain_regular_file(tmp_path: Path, mode: bytes) -> None:
    with pytest.raises(m.Blocked):
        export_fixture(tmp_path, module_mode=mode)


@pytest.mark.parametrize("change", ["populate", "file", "symlink", "parent-symlink",
                                   "sidecar-symlink", "sidecar-tamper", "duplicate-field",
                                   "mapping-tamper", "drop-placeholder", "sidecar-fifo"])
def test_staged_provenance_and_empty_directory_fail_closed(tmp_path: Path, change: str) -> None:
    source, _ = export_fixture(tmp_path)
    placeholder = source / g.PATH
    sidecar = g.sidecar_path(source)
    if change == "populate":
        (placeholder / "unexpected.txt").write_bytes(b"populated")
    elif change in ("file", "symlink", "drop-placeholder"):
        placeholder.rmdir()
        if change == "file":
            placeholder.write_bytes(b"substitute")
        elif change == "symlink":
            placeholder.symlink_to("../missing")
    elif change == "parent-symlink":
        (source / "docs").rename(source / "other-docs")
        (source / "docs").symlink_to("other-docs")
    elif change == "sidecar-symlink":
        saved = tmp_path / "saved.json"
        sidecar.rename(saved)
        sidecar.symlink_to(saved)
    elif change == "sidecar-tamper":
        sidecar.write_bytes(sidecar.read_bytes().replace(g.OBJECT.encode(), b"e" * 40))
    elif change == "duplicate-field":
        sidecar.write_bytes(b'{"schema":"duplicate",' + sidecar.read_bytes()[1:])
    elif change == "mapping-tamper":
        (source / ".gitmodules").write_bytes(MODULES.replace(g.URL.encode(), b"wrong"))
    elif change == "sidecar-fifo":
        sidecar.unlink()
        os.mkfifo(sidecar)
    with pytest.raises(m.Blocked):
        m.snapshot_manifest(source)


def test_sidecar_drop_cannot_match_governed_identity(tmp_path: Path) -> None:
    source, governed = export_fixture(tmp_path)
    g.sidecar_path(source).unlink()
    assert m.snapshot_manifest(source)[1] != governed


def test_provenance_revision_participates_in_identity() -> None:
    manifests = [{"schema": "SOURCE_SNAPSHOT_MANIFEST_V2", "entries": [],
                  "gitlink_provenance": g.provenance(revision)} for revision in g.REVISIONS.values()]
    assert len({m.sha256(m.canonical_json(manifest)) for manifest in manifests}) == 4


@pytest.mark.parametrize("case_id,label", list(g.REVISIONS))
def test_frozen_four_revisions_local_dry_export(tmp_path: Path, case_id: str, label: str) -> None:
    recipe = next(item["recipe"] for item in bridge.load_inputs()
                  if item["recipe"]["canonical_case_id"] == case_id)
    expected = batch.source_snapshot_identity(recipe, label)
    first, second = tmp_path / "first", tmp_path / "second"
    assert batch.source_snapshot_identity(recipe, label, first) == expected
    assert batch.source_snapshot_identity(recipe, label, second) == expected
    manifest, digest = m.snapshot_manifest(first)
    assert m.snapshot_manifest(second) == (manifest, digest)
    assert digest == expected
    assert manifest["gitlink_provenance"] == g.provenance(g.REVISIONS[(case_id, label)])
    assert list((first / g.PATH).iterdir()) == list((second / g.PATH).iterdir()) == []
    assert g.sidecar_path(first).read_bytes() == g.sidecar_path(second).read_bytes()
    assert g.PATH not in {entry["path"] for entry in manifest["entries"]}
    assert not (bridge.WORK / "environment_materialization_expansion_block_03_v1").exists()


def test_bare_script_snapshot_reader_preserves_blocked_type(tmp_path: Path) -> None:
    source, _ = export_fixture(tmp_path)
    sidecar = g.sidecar_path(source)
    sidecar.write_bytes(sidecar.read_bytes().replace(g.OBJECT.encode(), b"e" * 40))
    namespace = runpy.run_path(m.__file__, run_name="materializer_bare_source_test")
    with pytest.raises(namespace["Blocked"]):
        namespace["snapshot_manifest"](source)

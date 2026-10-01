"""Non-materializing source-package staging and historical transport regressions."""

from __future__ import annotations

import ast
import json
import os
import runpy
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from evaluation.downstream_benchmark.screening import block_03_gitlink_source_export as g
from evaluation.downstream_benchmark.screening import block_03_materializer_bridge as bridge
from evaluation.downstream_benchmark.screening import materialize_expansion_block_02_batch as batch
from evaluation.downstream_benchmark.screening import materializer as m
from evaluation.downstream_benchmark.tests.test_block_03_gitlink_source_export import export_fixture


@pytest.fixture(autouse=True)
def no_runtime():
    def forbidden(*args, **kwargs):
        raise AssertionError("runtime/attempt boundary crossed")

    with patch.object(m, "_materialize_checked", side_effect=forbidden), \
            patch.object(m, "docker", side_effect=forbidden), \
            patch.object(m, "docker_observation", side_effect=forbidden), \
            patch.object(m, "verify_base", side_effect=forbidden), \
            patch.object(m, "inspect_final", side_effect=forbidden):
        yield


@pytest.fixture
def package(tmp_path):
    source, identity = export_fixture(tmp_path / "input")
    # Export above uses only in-memory Git mocks. Transport needs no processes.
    with patch.object(batch.subprocess, "Popen", side_effect=AssertionError("process")), \
            patch.object(batch, "source_snapshot_identity", side_effect=AssertionError("export")), \
            patch.object(g, "derive", side_effect=AssertionError("regenerated provenance")):
        yield source, identity


def destination(tmp_path: Path) -> Path:
    context = tmp_path / "context"
    context.mkdir()
    return context / "source"


def test_valid_transport_preserves_bytes_placeholder_and_identity(package, tmp_path):
    source, identity = package
    target = destination(tmp_path)
    before = g.sidecar_path(source).read_bytes()
    manifest = m.transport_source_package(source, target, identity)
    assert manifest == m.snapshot_manifest(source)[0]
    assert m.snapshot_manifest(target) == (manifest, identity)
    assert g.sidecar_path(target) == target.with_name(target.name + ".gitlinks.json")
    assert g.sidecar_path(target).read_bytes() == before == g.sidecar_path(source).read_bytes()
    assert g.read(target) == manifest["gitlink_provenance"]
    assert (target / g.PATH).is_dir() and not (target / g.PATH).is_symlink()
    assert list((target / g.PATH).iterdir()) == []
    assert (target / "run.sh").stat().st_mode & 0o777 == 0o755
    assert os.readlink(os.fsencode(target / "link")) == b"missing-\xff"
    assert not list(tmp_path.rglob("attempt.json"))


def test_companion_names_follow_helper_for_renamed_destination(package, tmp_path):
    source, identity = package
    target = tmp_path / "renamed-snapshot"
    m.transport_source_package(source, target, identity)
    assert g.sidecar_path(target).name == "renamed-snapshot.gitlinks.json"
    assert g.sidecar_path(target).read_bytes() == g.sidecar_path(source).read_bytes()


@pytest.mark.parametrize("change", [
    "missing", "malformed", "identity", "superproject", "path", "mode", "object", "url",
    "noncanonical", "duplicate-field", "sidecar-symlink", "sidecar-fifo", "populated",
])
def test_source_failure_blocks_before_destination_copy(package, tmp_path, change):
    source, identity = package
    sidecar = g.sidecar_path(source)
    value = json.loads(sidecar.read_bytes())
    if change == "missing":
        sidecar.unlink()
    elif change == "malformed":
        sidecar.write_bytes(b"{malformed")
    elif change == "identity":
        identity = "0" * 64
    elif change == "noncanonical":
        sidecar.write_bytes(sidecar.read_bytes() + b"\n")
    elif change == "duplicate-field":
        sidecar.write_bytes(b'{"schema":"duplicate",' + sidecar.read_bytes()[1:])
    elif change in ("sidecar-symlink", "sidecar-fifo"):
        data = sidecar.read_bytes()
        sidecar.unlink()
        if change == "sidecar-symlink":
            saved = tmp_path / "saved.json"
            saved.write_bytes(data)
            sidecar.symlink_to(saved)
        else:
            os.mkfifo(sidecar)
    elif change == "populated":
        (source / g.PATH / "unexpected").write_bytes(b"submodule contents")
    else:
        field, replacement = {
            "superproject": ("superproject_revision", g.REVISIONS[("cookiecutter::2", "FIXED")]),
            "path": ("path", "wrong/path"), "mode": ("mode", "100644"),
            "object": ("object", "e" * 40), "url": ("declared_url", "https://example.org/wrong"),
        }[change]
        value["gitlinks"][0][field] = replacement
        sidecar.write_bytes(m.canonical_json(value))
    target = destination(tmp_path)
    with patch.object(m.shutil, "copytree", side_effect=AssertionError("copied invalid source")):
        with pytest.raises(m.Blocked) as blocked:
            m.transport_source_package(source, target, identity)
    assert blocked.value.status == "BLOCKED_INPUT_IDENTITY"
    assert not target.exists() and not g.sidecar_path(target).exists()


@pytest.mark.parametrize("change", ["missing", "bytes", "superproject", "tree", "placeholder"])
def test_destination_drop_or_tampering_blocks(package, tmp_path, monkeypatch, change):
    source, identity = package
    target = destination(tmp_path)
    snapshot = m.snapshot_manifest

    def damaged(path):
        if path == target:
            sidecar = g.sidecar_path(path)
            if change == "missing":
                sidecar.unlink()
            elif change == "bytes":
                sidecar.write_bytes(sidecar.read_bytes() + b"\n")
            elif change == "superproject":
                value = json.loads(sidecar.read_bytes())
                value["gitlinks"][0]["superproject_revision"] = g.REVISIONS[("cookiecutter::2", "FIXED")]
                sidecar.write_bytes(m.canonical_json(value))
            elif change == "tree":
                (path / "plain.txt").write_bytes(b"wrong source tree")
            else:
                (path / g.PATH).rmdir()
        return snapshot(path)

    monkeypatch.setattr(m, "snapshot_manifest", damaged)
    with pytest.raises(m.Blocked) as blocked:
        m.transport_source_package(source, target, identity)
    assert blocked.value.status == "BLOCKED_INPUT_IDENTITY"


def test_destination_companion_final_byte_check_blocks(package, tmp_path):
    source, identity = package
    target = destination(tmp_path)
    reader = g._read_at

    def changed(directory, name):
        data = reader(directory, name)
        if name.endswith(".gitlinks.json"):
            changed.calls += 1
            if changed.calls == 4:
                return data + b"\n"
        return data

    changed.calls = 0
    with patch.object(g, "_read_at", side_effect=changed):
        with pytest.raises(m.Blocked, match="destination companion bytes changed"):
            m.transport_source_package(source, target, identity)


def test_non_gitlink_transport_matches_historical_copytree(tmp_path):
    source, identity = export_fixture(tmp_path / "input", recipe={"canonical_case_id": "fixture"},
                                      links=[], modules=None)
    target = destination(tmp_path)
    old = tmp_path / "historical"
    shutil.copytree(source, old, symlinks=True)
    assert m.transport_source_package(source, target, identity) == m.snapshot_manifest(old)[0]
    assert m.snapshot_manifest(target) == m.snapshot_manifest(old)
    assert not g.sidecar_path(target).exists()
    assert os.readlink(os.fsencode(target / "link")) == os.readlink(os.fsencode(old / "link"))


def test_production_transport_precedes_base_probe_and_build():
    # Inspect the actual integration without entering the real engine/attempt path.
    tree = ast.parse(Path(m.__file__).read_text())
    engine = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                  and node.name == "_materialize_checked")
    body = next(node for node in engine.body if isinstance(node, ast.Try)).body
    stage = next(i for i, node in enumerate(body) if isinstance(node, ast.For)
                 and isinstance(node.iter, ast.Name) and node.iter.id == "sources")
    probe = next(i for i, node in enumerate(body) if isinstance(node, ast.Assign)
                 and isinstance(node.value, ast.Call)
                 and isinstance(node.value.func, ast.Name) and node.value.func.id == "verify_base")
    build = next(i for i, node in enumerate(body) if isinstance(node, ast.For)
                 and isinstance(node.iter, ast.Name) and node.iter.id == "contexts")
    assert stage < probe < build
    calls = [node for node in ast.walk(body[stage]) if isinstance(node, ast.Call)]
    assert any(isinstance(node.func, ast.Name) and node.func.id == "transport_source_package"
               for node in calls)
    assert not any(isinstance(node.func, ast.Attribute) and node.func.attr == "copytree"
                   for node in calls)
    # Each staged context carries its own source and manifest into the build loop.
    assert [name.id for name in body[build].target.elts] == [
        "revision", "source", "manifest", "context", "definition", "context_hash"]


def test_bare_script_transport_preserves_blocked_type(package, tmp_path):
    source, identity = package
    g.sidecar_path(source).unlink()
    namespace = runpy.run_path(m.__file__, run_name="materializer_bare_transport_test")
    with pytest.raises(namespace["Blocked"]):
        namespace["transport_source_package"](source, destination(tmp_path), identity)


@pytest.mark.parametrize("case_id,label", list(g.REVISIONS))
def test_frozen_cookiecutter_dry_transport(tmp_path, case_id, label):
    recipe = next(item["recipe"] for item in bridge.load_inputs()
                  if item["recipe"]["canonical_case_id"] == case_id)
    identity = batch.source_snapshot_identity(recipe, label)
    source, target = tmp_path / "snapshot", destination(tmp_path)
    assert batch.source_snapshot_identity(recipe, label, source) == identity
    manifest = m.transport_source_package(source, target, identity)
    assert manifest["gitlink_provenance"] == g.provenance(g.REVISIONS[(case_id, label)])
    assert m.snapshot_manifest(target)[1] == identity
    assert g.sidecar_path(source).read_bytes() == g.sidecar_path(target).read_bytes()
    assert list((source / g.PATH).iterdir()) == list((target / g.PATH).iterdir()) == []
    assert not list(tmp_path.rglob("attempt.json"))
    assert not (bridge.WORK / "environment_materialization_expansion_block_03_v1").exists()


@pytest.mark.parametrize("block,case_id", [(1, "sanic::2"), (2, "PySnooper::1")])
@pytest.mark.parametrize("label", ["BUGGY", "FIXED"])
def test_historical_block_transport_matches_old_context(tmp_path, block, case_id, label):
    row = next(r for r in m.read_rows(m.BENCHMARK / f"expansion_block_0{block}_environment_build_recipes.csv")
               if r["canonical_case_id"] == case_id)
    recipe = json.loads(row["build_recipe_json"])
    source, old, target = tmp_path / "snapshot", tmp_path / "old-context", tmp_path / "new-context"
    old.mkdir()
    target.mkdir()
    if block == 1:
        with patch.object(batch, "PREPARATION", batch.WORK / "expansion_block_01_preparation"):
            identity = batch.source_snapshot_identity(recipe, label, source)
    else:
        identity = batch.source_snapshot_identity(recipe, label, source)
    assert not g.sidecar_path(source).exists()
    shutil.copytree(source, old / "source", symlinks=True)
    m.transport_source_package(source, target / "source", identity)
    assert m.context_manifest(old) == m.context_manifest(target)
    assert not g.sidecar_path(target / "source").exists()

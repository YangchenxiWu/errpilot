"""Synthetic, history-free source and Docker-context symlink checks."""

from __future__ import annotations

import base64
import json
import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evaluation.downstream_benchmark.screening import materializer as m


def link(target: bytes, path: Path) -> None:
    os.symlink(target, os.fsencode(path))


class ManifestV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="snapshot-symlink-v2-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "source"
        self.root.mkdir()

    def entries(self) -> tuple[list[dict], str]:
        manifest, digest = m.snapshot_manifest(self.root)
        self.assertEqual(manifest["schema"], "SOURCE_SNAPSHOT_MANIFEST_V2")
        self.assertEqual(digest, m.sha256(m.canonical_json(manifest)))
        return manifest["entries"], digest

    def test_regular_file_identity_is_deterministic_and_ordered(self) -> None:
        (self.root / "z.txt").write_bytes(b"z")
        (self.root / "a.txt").write_bytes(b"a")
        first, digest = self.entries()
        second, again = self.entries()
        self.assertEqual((first, digest), (second, again))
        self.assertEqual([item["path"] for item in first], ["a.txt", "z.txt"])
        self.assertEqual(first[0]["entry_type"], "file")
        self.assertEqual(first[0]["content_sha256"], m.sha256(b"a"))
        self.assertIn("mode", first[0])

    def test_safe_file_and_directory_links_are_preserved_not_traversed(self) -> None:
        (self.root / "real.txt").write_bytes(b"content")
        (self.root / "real-dir").mkdir()
        (self.root / "real-dir" / "child.txt").write_bytes(b"child")
        link(b"real.txt", self.root / "link.txt")
        link(b"real-dir", self.root / "dir-link")
        entries, _ = self.entries()
        by_path = {item["path"]: item for item in entries}
        self.assertEqual(by_path["link.txt"]["entry_type"], "symlink")
        self.assertEqual(by_path["dir-link"]["entry_type"], "symlink")
        self.assertEqual(by_path["link.txt"]["target_b64"], base64.b64encode(b"real.txt").decode())
        self.assertEqual(by_path["link.txt"]["target_sha256"], m.sha256(b"real.txt"))
        self.assertNotIn("dir-link/child.txt", by_path)
        self.assertIn("real-dir/child.txt", by_path)

    def test_exact_target_bytes_control_link_identity(self) -> None:
        link(b"nonexistent-\xff", self.root / "link")
        first, digest = self.entries()
        self.assertEqual(base64.b64decode(first[0]["target_b64"]), b"nonexistent-\xff")
        self.assertEqual(first[0]["target_sha256"], m.sha256(b"nonexistent-\xff"))
        (self.root / "link").unlink()
        link(b"nonexistent-\xfe", self.root / "link")
        second, other_digest = self.entries()
        self.assertNotEqual(first[0], second[0])
        self.assertNotEqual(digest, other_digest)

    def test_target_file_content_change_does_not_change_link_entry(self) -> None:
        target = self.root / "real.txt"
        target.write_bytes(b"first")
        link(b"real.txt", self.root / "link")
        first, digest = self.entries()
        target.write_bytes(b"second")
        second, new_digest = self.entries()
        self.assertEqual(first[0], second[0])
        self.assertNotEqual(digest, new_digest)

    def test_relative_dotdot_inside_root_and_dangling_target(self) -> None:
        (self.root / "nested").mkdir()
        link(b"../missing.txt", self.root / "nested" / "link")
        entries, _ = self.entries()
        self.assertEqual(entries[0]["path"], "nested/link")
        self.assertEqual(entries[0]["entry_type"], "symlink")

    def test_absolute_and_lexical_escape_block(self) -> None:
        (self.root / "nested").mkdir()
        for target, location in ((b"/tmp/outside", self.root / "link"),
                                 (b"../outside", self.root / "link"),
                                 (b"../../outside", self.root / "nested" / "link")):
            with self.subTest(target=target):
                link(target, location)
                with self.assertRaises(m.Blocked) as blocked:
                    self.entries()
                self.assertEqual(blocked.exception.status, "BLOCKED_UNSAFE_SYMLINK")
                location.unlink()

    def test_forbidden_paths_and_targets_block(self) -> None:
        for name in m.FORBIDDEN_SNAPSHOT_NAMES:
            with self.subTest(name=name):
                (self.root / name).write_bytes(b"forbidden")
                with self.assertRaises(m.Blocked):
                    self.entries()
                (self.root / name).unlink()
                link(os.fsencode(name), self.root / "link")
                with self.assertRaises(m.Blocked) as blocked:
                    self.entries()
                self.assertEqual(blocked.exception.status, "BLOCKED_UNSAFE_SYMLINK")
                (self.root / "link").unlink()

    def test_special_file_blocks(self) -> None:
        fifo = self.root / "fifo"
        os.mkfifo(fifo)
        with self.assertRaises(m.Blocked) as blocked:
            self.entries()
        self.assertEqual(blocked.exception.status, "BLOCKED_INPUT_IDENTITY")

    def test_context_manifest_and_copy_preserve_links(self) -> None:
        (self.root / "real.txt").write_bytes(b"data")
        link(b"real.txt", self.root / "link.txt")
        (self.root / "nested").mkdir()
        link(b"../real.txt", self.root / "nested" / "inner-link")
        context = Path(self.temp.name) / "context"
        context.mkdir()
        shutil.copytree(self.root, context / "source", symlinks=True)
        manifest, digest = m.context_manifest(context)
        self.assertEqual(manifest["schema"], "BUILD_CONTEXT_MANIFEST_V2")
        self.assertEqual(digest, m.sha256(m.canonical_json(manifest)))
        by_path = {item["path"]: item for item in manifest["entries"]}
        for path, target in (("source/link.txt", b"real.txt"),
                             ("source/nested/inner-link", b"../real.txt")):
            copied = context / path
            self.assertTrue(stat.S_ISLNK(os.lstat(copied).st_mode))
            self.assertEqual(os.readlink(os.fsencode(copied)), target)
            self.assertEqual(by_path[path]["entry_type"], "symlink")
            self.assertEqual(by_path[path]["target_sha256"], m.sha256(target))
            self.assertNotIn("content_sha256", by_path[path])

    def test_no_traversal_outside_root_through_directory_link(self) -> None:
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (outside / "secret.txt").write_bytes(b"outside")
        link(b"../outside", self.root / "external-dir")
        with self.assertRaises(m.Blocked) as blocked:
            self.entries()
        self.assertEqual(blocked.exception.status, "BLOCKED_UNSAFE_SYMLINK")

    def test_unsafe_second_revision_blocks_before_any_docker_call(self) -> None:
        fixture = json.loads((m.FIXTURES / "fixture_b.json").read_bytes())
        first_hash = fixture["revisions"][0]["sha"]
        with patch.object(m, "snapshot_manifest", side_effect=[
                ({}, first_hash), m.Blocked("BLOCKED_UNSAFE_SYMLINK", "unsafe FIXED link")]), \
                patch.object(m, "verify_base", side_effect=AssertionError("Docker probe")), \
                patch.object(m, "docker", side_effect=AssertionError("Docker build")):
            result = m.materialize_synthetic(fixture, output=Path(self.temp.name) / "attempt")
        self.assertEqual(result["status"], "BLOCKED_UNSAFE_SYMLINK")
        self.assertFalse((Path(self.temp.name) / "attempt" / "BUGGY").exists())

    def test_historical_ledgers_stay_byte_identical(self) -> None:
        expected = {
            "environment_materialization_batch_01.csv":
                "d898ee0bb6d26f6b46ad387292a39df93d438e683947ff6500229b0922a1088b",
            "ENVIRONMENT_MATERIALIZATION_BATCH_01.md":
                "184fa568a6cb59685047f868799fcd012869d53d5a7409cbc8d3af68fc665f13",
            "environment_materialization_batch_01_identity_completion.csv":
                "bd17f23a0cf59167a96aab91b064f00bed8f0d2c3048fa2da493332128478f47",
        }
        for name, digest in expected.items():
            self.assertEqual(m.sha256((m.BENCHMARK / name).read_bytes()), digest)


@unittest.skipUnless(os.environ.get("MATERIALIZER_SYMLINK_DOCKER_TESTS") == "1",
                     "explicit synthetic Docker validation")
class SyntheticSymlinkDockerTests(unittest.TestCase):
    def test_image_keeps_exact_symlinks(self) -> None:
        base = "docker.io/library/python@sha256:ba23c4870854aa0718113e8765e7f46acbf141c6be1e66957ddcf130bd88d59d"
        inspect = subprocess.run(["docker", "image", "inspect", base], capture_output=True)
        self.assertEqual(inspect.returncode, 0, "frozen synthetic base must already be local")
        with tempfile.TemporaryDirectory(prefix="snapshot-symlink-docker-") as temp:
            root = Path(temp)
            source = root / "source"
            source.mkdir()
            (source / "real.txt").write_bytes(b"synthetic")
            (source / "nested").mkdir()
            link(b"real.txt", source / "link.txt")
            link(b"../real.txt", source / "nested" / "inner-link")
            snapshot, _ = m.snapshot_manifest(source)
            self.assertEqual(sum(item["entry_type"] == "symlink"
                                 for item in snapshot["entries"]), 2)
            context = root / "context"
            context.mkdir()
            shutil.copytree(source, context / "source", symlinks=True)
            (context / "Dockerfile").write_text(
                f"FROM --platform=linux/amd64 {base}\nCOPY source/ /subject/\n")
            context_manifest, _ = m.context_manifest(context)
            self.assertEqual(sum(item["entry_type"] == "symlink"
                                 for item in context_manifest["entries"]), 2)
            tag = "errpilot-synthetic-symlink-v2:local"
            build = subprocess.run(["docker", "build", "--platform=linux/amd64",
                                    "--network=none", "--pull=false", "--no-cache",
                                    "-t", tag, str(context)], capture_output=True)
            self.assertEqual(build.returncode, 0, build.stdout[-1000:] + build.stderr[-1000:])
            probe = ("import base64,json,os,stat;"
                     "p=['/subject/link.txt','/subject/nested/inner-link'];"
                     "print(json.dumps([{'link':stat.S_ISLNK(os.lstat(x).st_mode),"
                     "'target_b64':base64.b64encode(os.readlink(os.fsencode(x))).decode()}"
                     " for x in p]))")
            run = subprocess.run(["docker", "run", "--rm", "--platform=linux/amd64",
                                  "--network=none", "--read-only", tag,
                                  "python", "-c", probe], capture_output=True)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            observed = json.loads(run.stdout)
            self.assertEqual(observed, [
                {"link": True, "target_b64": base64.b64encode(target).decode()}
                for target in (b"real.txt", b"../real.txt")])

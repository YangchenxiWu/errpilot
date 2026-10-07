"""Synthetic stdlib archive/layout tests. No Docker or real source operations."""
from __future__ import annotations

import copy
import gzip
import importlib.util
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("transport_test_subject", HERE / "transport_bridge.py")
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)


def fixture(path, *, compressed=True, mutation=None):
    layers = []
    for i in range(2):
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w") as archive:
            payload = ("SYNTHETIC_LAYER_" + str(i)).encode()
            member = tarfile.TarInfo("synthetic-" + str(i))
            member.size = len(payload)
            archive.addfile(member, io.BytesIO(payload))
        layers.append(buf.getvalue())
    diff_ids = ["sha256:" + t.sha(x) for x in layers]
    config = {"architecture": "amd64", "os": "linux", "rootfs": {"type": "layers", "diff_ids": diff_ids}}
    if mutation == "rootfs":
        config["rootfs"]["diff_ids"] = list(reversed(diff_ids))
    config_raw = t.encoded(config)
    config_digest = "sha256:" + t.sha(config_raw)
    stored = [gzip.compress(x, mtime=0) if compressed else x for x in layers]
    descriptors = [{"digest": "sha256:" + t.sha(x), "size": len(x), "mediaType":
        "application/vnd.docker.image.rootfs.diff.tar.gzip" if compressed else
        "application/vnd.oci.image.layer.v1.tar"} for x in stored]
    source_manifest = {"schemaVersion": 2, "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
        "config": {"digest": config_digest, "size": len(config_raw), "mediaType": "application/vnd.docker.container.image.v1+json"},
        "layers": descriptors}
    source_raw = t.encoded(source_manifest)
    source_digest = "sha256:" + t.sha(source_raw)
    legacy = {"Config": t.digest_path(config_digest), "Layers": [t.digest_path(x["digest"]) for x in descriptors],
              "RepoTags": []}
    if mutation == "order":
        legacy["Layers"].reverse()
    expected = {"reference": "docker.io/library/python@" + source_digest,
                "image_identity": {"RootFS": {"Layers": diff_ids}}}
    if mutation == "scientific_base":
        expected["reference"] = "docker.io/library/python@sha256:" + "0" * 64
    items = [("manifest.json", t.encoded([legacy, legacy] if mutation == "multi" else [legacy])),
             (t.digest_path(source_digest), source_raw), (t.digest_path(config_digest),
                config_raw + b" " if mutation == "config" else config_raw)]
    items += [(t.digest_path(d["digest"]), x + b"mutation" if mutation == "layer" and i == 0 else x)
              for i, (d, x) in enumerate(zip(descriptors, stored))]
    if mutation == "duplicate":
        items.append(items[0])
    if mutation == "unsafe":
        items.append(("../outside", b"forbidden"))
    with tarfile.open(path, "w") as archive:
        for name, payload in items:
            member = tarfile.TarInfo(name)
            member.size = len(payload)
            archive.addfile(member, io.BytesIO(payload))
    return expected


class TransportTests(unittest.TestCase):
    def test_compressed_exact_tar_stream_and_determinism(self):
        with tempfile.TemporaryDirectory(prefix="errpilot-oci-synthetic-") as tmp:
            root = Path(tmp)
            archive = root / "source.tar"
            expected = fixture(archive)
            observations = []
            for name in ["a", "b"]:
                observation = {}
                t.construct_layout(archive, root / name, expected, observation)
                t.validate_layout(root / name, observation)
                self.assertTrue(all(x["uncompressed_tar_sha256"] == x["expected_rootfs_diff_id"]
                                    and not x["raw_saved_bytes_equal_diff_id"] for x in observation["layers_checked"]))
                observations.append(observation)
            self.assertEqual(observations[0]["transport_manifest_identity"], observations[1]["transport_manifest_identity"])
            self.assertEqual(t.prior.inventory(root / "a"), t.prior.inventory(root / "b"))

    def test_uncompressed_archive_exact_bytes(self):
        with tempfile.TemporaryDirectory(prefix="errpilot-oci-synthetic-") as tmp:
            root = Path(tmp)
            archive = root / "source.tar"
            expected = fixture(archive, compressed=False)
            observation = {}
            t.construct_layout(archive, root / "layout", expected, observation)
            self.assertTrue(all(x["raw_saved_bytes_equal_diff_id"] for x in observation["layers_checked"]))
            t.validate_layout(root / "layout", observation)

    def test_archive_rejections_write_no_layout(self):
        for mutation in ["config", "rootfs", "order", "layer", "scientific_base", "multi", "duplicate", "unsafe"]:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory(prefix="errpilot-oci-synthetic-") as tmp:
                root = Path(tmp)
                archive = root / "source.tar"
                expected = fixture(archive, mutation=mutation)
                with self.assertRaises(t.ArchiveRejected):
                    t.construct_layout(archive, root / "layout", expected, {})
                self.assertFalse((root / "layout").exists())

    def test_layout_rejections_and_nonregeneration(self):
        for mutation in ["blob", "manifest", "absent", "rootfs", "extra"]:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory(prefix="errpilot-oci-synthetic-") as tmp:
                root = Path(tmp)
                archive = root / "source.tar"
                expected = fixture(archive)
                observation = {}
                layout = root / "layout"
                t.construct_layout(archive, layout, expected, observation)
                if mutation == "blob":
                    (layout / t.digest_path(observation["config_rootfs_diff_ids"][0])).write_bytes(b"mutated")
                elif mutation == "manifest":
                    index = json.loads((layout / "index.json").read_bytes())
                    index["manifests"][0]["digest"] = "sha256:" + "0" * 64
                    (layout / "index.json").write_bytes(t.encoded(index))
                elif mutation == "absent":
                    layout = root / "missing"
                elif mutation == "rootfs":
                    observation = copy.deepcopy(observation)
                    observation["config_rootfs_diff_ids"].reverse()
                else:
                    (layout / "extra").write_bytes(b"extra")
                with self.assertRaises(t.ArchiveRejected):
                    t.validate_layout(layout, observation)
                self.assertFalse((root / "missing").exists())

    def test_no_overwrite_after_verified_layout(self):
        with tempfile.TemporaryDirectory(prefix="errpilot-oci-synthetic-") as tmp:
            root = Path(tmp)
            archive = root / "source.tar"
            expected = fixture(archive)
            layout = root / "layout"
            observation = {}
            t.construct_layout(archive, layout, expected, observation)
            before = t.prior.inventory(layout)
            with self.assertRaises(RuntimeError):
                t.construct_layout(archive, layout, expected, {})
            self.assertEqual(t.prior.inventory(layout), before)

    def test_strict_json_rejections(self):
        for raw in [b'{"a":1,"a":2}', b'{"x":NaN}', b'"\xff"']:
            with self.subTest(raw=raw), self.assertRaises((t.ArchiveRejected, UnicodeError)):
                t.strict_json(raw)

    def test_population_and_blocker_rejection_probes(self):
        from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a
        from evaluation.downstream_benchmark.screening import v6_preparation_runtime as r
        raw, population = (a.ROOT / a.CURRENT).read_bytes(), r.population()
        t.validate_qualification_firewall(raw, population, [])
        for mutation in ["total", "split", "blocker", "transport_identity"]:
            changed = copy.deepcopy(population)
            if mutation == "total":
                changed["items"].pop()
            elif mutation == "split":
                changed["items"][0]["build_network_required"] = not changed["items"][0]["build_network_required"]
            elif mutation == "blocker":
                changed["items"][0]["case_id"] = "matplotlib::1"
            else:
                changed["items"][0]["base_attempt_id"] = "sha256:" + "a" * 64
            with self.subTest(mutation=mutation), self.assertRaises(t.ArchiveRejected):
                t.validate_qualification_firewall(raw, changed, [])

    def test_event_three_and_real_claim_rejection_probes(self):
        from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a
        from evaluation.downstream_benchmark.screening import v6_preparation_runtime as r
        raw, population = (a.ROOT / a.CURRENT).read_bytes(), r.population()
        changed = json.loads(raw)
        changed["event_count"] = 3
        with self.assertRaises(t.ArchiveRejected):
            t.validate_qualification_firewall(t.encoded(changed), population, [])
        with self.assertRaises(t.ArchiveRejected):
            t.validate_qualification_firewall(raw, population, ["FORBIDDEN_REAL_CLAIM"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

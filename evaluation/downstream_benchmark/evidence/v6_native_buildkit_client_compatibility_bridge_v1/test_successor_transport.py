"""Exercise candidate I/O ordering and context preservation without Docker."""
from __future__ import annotations

import io
import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT.parents[3]))
sys.path.insert(0, str(OUT))
import bridge as b  # noqa: E402
import successor_runtime as s  # noqa: E402
from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a  # noqa: E402
from evaluation.downstream_benchmark.screening import v6_preparation_runtime as runtime  # noqa: E402


class TransportTests(unittest.TestCase):
    def test_native_sequence_preserves_context_and_refuses_second_invocation(self):
        root = b.Q / "successor-io-fixture"
        a.require(not root.exists(), "fixture no overwrite")
        root.mkdir()
        _, manifest = a.load_inputs()
        item = next(x for x in runtime.population()["items"] if not x["build_network_required"])
        plan = a.select(manifest, ordinal=item["census_order"], case_id=item["case_id"], plan_sha=item["plan_sha256"])
        compiled = s.compile_transport(item, plan, proxy_url="unused", enforcement_receipt=None)
        context = root / "scientific-context"
        context.mkdir()
        (context / "Dockerfile").write_bytes(compiled["scientific_dockerfile"])
        marker = context / "marker"
        marker.write_bytes(b"synthetic only\n")
        marker.chmod(0o755)
        (context / "safe-link").symlink_to("marker")
        original = a.shared.context_manifest(context)
        binding = {"endpoint": "unix:///run/buildkit/buildkitd.sock", "native_binary_sha256": "7809f0f3e4a85c880b929fa618668048a48bb23d251799f9960150ce9a8d5017",
            "same_daemon": True, "daemon_count": 1, "runtime_reference": b.IMAGE,
            "scientific_base_authority": item["base_image_reference"], "native_store_name": "frozenbase", "frontend_alias": "errpilot_frozen_base",
            "local_oci_manifest_identity": "sha256:" + "a" * 64, "ordered_rootfs_diff_ids": ["sha256:" + "b" * 64],
            "container_id": "SYNTHETIC_CONTAINER_IO_MODEL", "container_root": "/tmp/errpilot-v6-synthetic-io-model"}
        tag = "errpilot-synthetic-native-io-model:qualification"
        payload = b"SYNTHETIC_IO_MODEL_ONLY_NOT_A_DOCKER_ARTIFACT\n"
        copied = {}
        calls = []
        class Runner:
            namespace = "SYNTHETIC_QUALIFICATION_ONLY"
            def verify_layout(self, layout, given):
                self.layout_checked = layout == root / "layout-model" and given == binding
            def verify_container_layout(self, cid, path, given):
                a.require(self.layout_checked and cid == binding["container_id"] and given == binding, "layout order")
            def require_no_registry_request(self, cid, result):
                a.require(cid == binding["container_id"] and b"registry" not in result.stdout, "registry fallback")
            def persist(self, name, raw):
                b.durable(root / (name + ".evidence"), raw)
            def run(self, argv, *, timeout):
                calls.append(list(argv))
                output = b""
                if argv[:2] == ["docker", "cp"]:
                    source, target = argv[2:4]
                    if target.endswith(":/tmp/errpilot-v6-synthetic-io-model/context"):
                        staged = root / "container-context-model"
                        shutil.copytree(source, staged, symlinks=True)
                        copied["context"] = staged
                    elif source.endswith(":/tmp/errpilot-v6-synthetic-io-model/context"):
                        shutil.copytree(copied["context"], target, symlinks=True)
                    elif source.endswith(":/tmp/errpilot-v6-synthetic-io-model/output.docker.tar"):
                        Path(target).write_bytes(payload)
                elif argv[0:2] == ["docker", "exec"] and argv[3:4] == ["sha256sum"]:
                    output = (a.sha(payload) + "  " + argv[4] + "\n").encode()
                elif argv[:3] == ["docker", "image", "inspect"]:
                    output = json.dumps([{"Id": "sha256:" + "c" * 64, "RepoTags": [tag], "Os": "linux", "Architecture": "amd64",
                        "RootFS": {"Layers": binding["ordered_rootfs_diff_ids"]}}]).encode()
                elif argv[:2] == ["docker", "exec"] and argv[3:4] == ["/usr/bin/buildctl"]:
                    output = b"SYNTHETIC_NATIVE_IO_MODEL\n"
                return subprocess.CompletedProcess(argv, 0, output, b"")
        transport = s.NativeDockerTransport(compiled=compiled, binding=binding, layout=root / "layout-model",
            artifact_root=root / "transport-output-model", runner=Runner())
        args = ["build", "--platform=linux/amd64", "--network=none", "--progress=plain", "--no-cache", "-t", tag, "-f", str(context / "Dockerfile"), str(context)]
        result = transport.build(args)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(a.shared.context_manifest(context), original)
        native_index = next(i for i, argv in enumerate(calls) if argv[:2] == ["docker", "exec"] and argv[3:4] == ["/usr/bin/buildctl"])
        load_index = next(i for i, argv in enumerate(calls) if argv[:2] == ["docker", "load"])
        inspect_index = next(i for i, argv in enumerate(calls) if argv[:3] == ["docker", "image", "inspect"])
        self.assertLess(native_index, load_index)
        self.assertLess(load_index, inspect_index)
        native = calls[native_index]
        self.assertIn("force-network-mode=none", native)
        self.assertIn("frozenbase=" + binding["container_root"] + "/oci", native)
        count = len(calls)
        with self.assertRaises(a.Rejected):
            transport.build(args)
        self.assertEqual(len(calls), count)


if __name__ == "__main__":
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(TransportTests))
    b.durable(OUT / "successor_transport_tests.txt", stream.getvalue().encode())
    b.save("successor_transport_test_results.json", {"status": "PASS" if result.wasSuccessful() else "FAIL", "tests_run": result.testsRun,
        "failures": len(result.failures), "errors": len(result.errors), "skips": len(result.skipped),
        "scope": "offline explicit I/O model; native solve/load ordering, context modes/symlinks, no retry; no Docker or scientific action executes"})
    a.require(result.wasSuccessful(), "successor I/O mechanics failed")

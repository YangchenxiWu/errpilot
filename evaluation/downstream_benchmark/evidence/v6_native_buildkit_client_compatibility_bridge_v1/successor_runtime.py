"""Native Docker transport integration candidate. Real dispatch stays rejected.

The shared materializer keeps its scientific generator, packaging, inspection,
probe and environment-identity code. Only its build transport is replaced.
Acceptance, publication, event #3 and canonical installation are future gates.
"""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import types
from pathlib import Path

from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a
from evaluation.downstream_benchmark.screening import v6_preparation_runtime as legacy

try:
    from . import guards
except ImportError:
    import guards

OUT = Path(__file__).resolve().parent
INSTALLATION = "evaluation/downstream_benchmark/V6_NATIVE_BUILDKIT_CLIENT_RUNTIME_INSTALLATION_V1.json"
LATER_GATES = (
    "runtime_integration_HUMAN_PI_ACCEPTED", "frozen", "persisted", "committed",
    "required_publication", "event_3", "execution_effectivity_binding",
    "independent_acceptance_pin", "canonical_install",
)


def dispatch(*args, **kwargs):
    """No import, candidate receipt or caller Boolean can claim a real attempt."""
    raise a.Rejected("real_dispatch=REJECT; successor candidate is not installed; later Human-PI gates required")


def compile_transport(item, plan, *, proxy_url, enforcement_receipt):
    a.require(item == a.work_item(plan, item["variant"]), "work/attempt identity changed")
    a.require(item["case_id"] not in {"matplotlib::1", "matplotlib::8"}, "blocker dispatch")
    recipe = a.engine_recipe(plan)
    original = a.shared.build_definition(recipe, source_present=item["variant"] != "SOURCE_INDEPENDENT",
        dependency_present=plan["recipe_candidate"]["requirements"]["dependency_bytes_b64"] is not None)
    required = item["build_network_required"]
    identity = a.loads((OUT / "network_enforcement_identity.json").read_bytes())
    expected_receipt = {"schema": "V6_RESTRICTED_BUILD_EGRESS_ENFORCEMENT_RECEIPT_CANDIDATE_V1",
        "semantic_enforcement_sha256": identity["semantic_enforcement_sha256"], "base_attempt_id": item["base_attempt_id"],
        "runtime_authority": False}
    a.require(enforcement_receipt == expected_receipt if required else enforcement_receipt is None,
        "wrong/missing candidate receipt; qualification receipt grants no runtime authority")
    execution = guards.execution_dockerfile(original, frozen_base=item["base_image_reference"], restricted=required)
    options = [] if required else ["force-network-mode=none"]
    args = {"HTTP_PROXY": proxy_url, "HTTPS_PROXY": proxy_url, "PIP_INDEX_URL": "https://pypi.org/simple"} if required else {}
    guards.network_binding(required=required, options=options, build_args=args, proxy_url=proxy_url, receipt=enforcement_receipt)
    return {"base_attempt_id": item["base_attempt_id"], "item": item, "recipe": recipe,
        "scientific_dockerfile": original, "execution_dockerfile": execution,
        "frontend_options": options, "build_args": args,
        "scientific_base_authority": item["base_image_reference"], "recipe_sha256": item["recipe_sha256"],
        "execution_network": "NONE", "real_dispatch": "REJECT"}


def native_argv(binding, root, tag, compiled):
    a.require(binding["endpoint"] == "unix:///run/buildkit/buildkitd.sock", "wrong daemon")
    a.require(binding["native_binary_sha256"] == "7809f0f3e4a85c880b929fa618668048a48bb23d251799f9960150ce9a8d5017", "wrong binary")
    a.require(binding["same_daemon"] and binding["daemon_count"] == 1, "second/wrong daemon")
    a.require(binding["runtime_reference"] == "moby/buildkit@sha256:cec9f139f45e93c5c69c60f8b07cfad9f43f4ef6b6a6cd917527fea5ff2e3dea", "runtime substitution")
    a.require(binding["scientific_base_authority"] == compiled["scientific_base_authority"], "base authority changed")
    a.require(binding["native_store_name"] == "frozenbase" and binding["frontend_alias"] == "errpilot_frozen_base", "wrong store")
    a.require(root.startswith("/tmp/errpilot-v6-") and ".." not in Path(root).parts, "unsafe builder input path")
    a.require(tag.startswith("errpilot-") and "," not in tag, "unsafe exporter tag")
    argv = ["/usr/bin/buildctl", "--addr=" + binding["endpoint"], "build",
        "--oci-layout", "frozenbase=" + root + "/oci", "--frontend=dockerfile.v0",
        "--local", "context=" + root + "/context", "--local", "dockerfile=" + root + "/context",
        "--opt", "context:errpilot_frozen_base=oci-layout://frozenbase@" + binding["local_oci_manifest_identity"],
        "--opt", "platform=linux/amd64", "--no-cache", "--progress=plain", "--output",
        "type=docker,name=" + tag + ",dest=" + root + "/output.docker.tar"]
    for option in compiled["frontend_options"]:
        argv += ["--opt", option]
    for key, value in sorted(compiled["build_args"].items()):
        argv += ["--opt", "build-arg:" + key + "=" + value]
    if compiled["build_args"]:
        a.require(binding["proxy_internal_host_binding"].startswith("add-hosts=errpilot-v6-egress-42393faa3385-v1-proxy="), "wrong proxy host binding")
        argv += ["--opt", binding["proxy_internal_host_binding"]]
    guards.native_command(argv, list(argv))
    return argv


def file_sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


class NativeDockerTransport:
    """Explicit I/O provider; no daemon or host buildctl is implicitly selected.

    A future accepted controller supplies a freshly provisioned daemon binding,
    exact immutable transport map and append-only command/evidence provider.
    This candidate only permits a construction/qualification provider.
    """
    def __init__(self, *, compiled, binding, layout, artifact_root, runner):
        a.require(runner.namespace == "SYNTHETIC_QUALIFICATION_ONLY", "real runtime provider unavailable in candidate")
        a.require(artifact_root.is_relative_to(a.OUTPUT_ROOT / "qualification"), "wrong output root")
        self.compiled, self.binding, self.layout = compiled, binding, layout
        self.root, self.runner = artifact_root, runner
        self.used = False

    def invoke(self, argv, *, timeout=600):
        guards.command(argv)
        return self.runner.run(argv, timeout=timeout)

    def check(self, argv, *, timeout=600):
        result = self.invoke(argv, timeout=timeout)
        a.require(result.returncode == 0, "native bridge phase failed; no retry")
        return result

    def build(self, args, *, timeout=1200):
        a.require(not self.used, "automatic retry refused")
        expected_network = "--network=default" if self.compiled["build_args"] else "--network=none"
        a.require(args[:3] == ["build", "--platform=linux/amd64", expected_network], "network/command mismatch")
        a.require(args[3:5] == ["--progress=plain", "--no-cache"] and args[5] == "-t" and args[7] == "-f" and len(args) == 10,
            "unexpected build flags")
        tag, context = args[6], Path(args[9])
        a.require(Path(args[8]) == context / "Dockerfile", "wrong Dockerfile/context")
        a.require((context / "Dockerfile").read_bytes() == self.compiled["scientific_dockerfile"], "scientific generator changed")
        # Full no-follow manifest also binds safe symlinks and file modes.
        a.shared.context_manifest(context)
        self.runner.verify_layout(self.layout, self.binding)
        self.used = True
        a.require(not self.root.exists(), "output already exists; no overwrite")
        self.root.mkdir()
        staged = self.root / "execution-context"
        shutil.copytree(context, staged, symlinks=True)
        (staged / "Dockerfile").write_bytes(self.compiled["execution_dockerfile"])
        expected_manifest = a.shared.context_manifest(staged)
        cid, croot = self.binding["container_id"], self.binding["container_root"]
        self.check(["docker", "exec", cid, "mkdir", "-p", croot])
        self.check(["docker", "cp", str(self.layout), cid + ":" + croot + "/oci"])
        self.check(["docker", "cp", str(staged), cid + ":" + croot + "/context"])
        # Independent round trip supports the same file modes/safe symlinks as
        # the shared materializer; the original scientific context is untouched.
        returned = self.root / "copied-context-readback"
        self.check(["docker", "cp", cid + ":" + croot + "/context", str(returned)])
        a.require(a.shared.context_manifest(returned) == expected_manifest, "copied context/modes/symlinks drift")
        self.runner.verify_container_layout(cid, croot + "/oci", self.binding)
        argv = native_argv(self.binding, croot, tag, self.compiled)
        solve = self.invoke(["docker", "exec", cid] + argv, timeout=timeout)
        self.runner.persist("native_build_log", solve.stdout + solve.stderr)
        if solve.returncode:
            return subprocess.CompletedProcess(args, solve.returncode, solve.stdout + solve.stderr)
        self.runner.require_no_registry_request(cid, solve)
        digest_result = self.check(["docker", "exec", cid, "sha256sum", croot + "/output.docker.tar"])
        expected_sha = digest_result.stdout.decode().split()[0]
        artifact = self.root / "output.docker.tar"
        self.check(["docker", "cp", cid + ":" + croot + "/output.docker.tar", str(artifact)])
        a.require(file_sha(artifact) == expected_sha, "Docker exporter copy drift")
        loaded = self.check(["docker", "load", "-i", str(artifact)])
        inspected = self.check(["docker", "image", "inspect", tag])
        image = a.loads(inspected.stdout)[0]
        a.require(tag in image["RepoTags"] and (image["Os"], image["Architecture"]) == ("linux", "amd64"), "output not inspectable")
        diffids = self.binding["ordered_rootfs_diff_ids"]
        a.require(image["RootFS"]["Layers"][:len(diffids)] == diffids, "output rootfs drift")
        self.runner.persist("native_transport_receipt", a.canonical({"artifact_sha256": expected_sha,
            "image_id": image["Id"], "RootFS": image["RootFS"], "scientific_base": self.compiled["scientific_base_authority"],
            "base_attempt_id": self.compiled["base_attempt_id"], "execution_dockerfile_sha256": a.sha(self.compiled["execution_dockerfile"]),
            "docker_load": True, "same_daemon": True, "attempt_identity_regenerated": False}))
        return subprocess.CompletedProcess(args, 0, solve.stdout + solve.stderr + loaded.stdout)


def shared_engine(transport):
    """Clone shared functions into a private namespace; bind build transport."""
    a.require(isinstance(transport, NativeDockerTransport), "unbound transport")
    bound = dict(a.shared.__dict__)
    for name, value in a.shared.__dict__.items():
        if isinstance(value, types.FunctionType) and value.__globals__ is a.shared.__dict__:
            clone = types.FunctionType(value.__code__, bound, value.__name__, value.__defaults__, value.__closure__)
            clone.__kwdefaults__ = value.__kwdefaults__
            bound[name] = clone
    def docker(args, *, timeout=600):
        args = list(args)
        if args[:1] == ["build"]:
            return transport.build(args, timeout=timeout)
        a.require(args and args[0] in {"image", "run"}, "Docker acquisition/global operation denied")
        if args[0] == "image":
            a.require(args[1:2] == ["inspect"], "image operation denied")
        else:
            a.require([x for x in args if x.startswith("--network")] == ["--network=none"], "probe network must be NONE")
            a.require(not any(x.startswith("--pull=") and x != "--pull=never" for x in args), "pull denied")
            if "--pull=never" not in args:
                args.insert(1, "--pull=never")
        return transport.invoke(["docker"] + args, timeout=timeout)
    def observation(args, *, timeout=600):
        return docker(args, timeout=timeout)
    bound["docker"], bound["docker_observation"] = docker, observation
    materialize = bound["_materialize_checked"]
    def qualification_only(fixture, *, output, input_root, synthetic_only, single_identity=False):
        a.require(synthetic_only is True and output.is_relative_to(a.OUTPUT_ROOT / "qualification"), "real materializer entry denied")
        return materialize(fixture, output=output, input_root=input_root, synthetic_only=True, single_identity=single_identity)
    bound["_materialize_checked"] = qualification_only
    bound["shared_materializer_code_object"] = materialize.__code__
    bound["shared_identity_code_object"] = bound["identity"].__code__
    return types.SimpleNamespace(**bound)


ONCE_ONLY = {"population": legacy.POPULATION_SHA, "claim_model": "UNCHANGED_ACCEPTED_LEDGER",
    "base_attempt_ID": "EXISTING_ITEM_ONLY", "exclusive_claim": True, "fsync": True,
    "one_terminal": True, "terminal_after_complete_observation": True, "overwrite": False,
    "retry": False, "crash_orphan": "FAIL_CLOSED", "real_dispatch": "REJECT"}

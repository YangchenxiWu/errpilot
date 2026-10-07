"""Fail-closed qualification and successor transport invariants."""
from __future__ import annotations

import re

ALLOWLIST = ["files.pythonhosted.org", "pypi.org"]


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def command(argv):
    require(bool(argv), "empty command")
    if argv[0] == "docker":
        require("pull" not in argv and "--use" not in argv and "--network=host" not in argv, "pull/global/host mode")
        if argv[1:2] == ["buildx"]:
            require(argv[2:3] in (["create"], ["inspect"], ["rm"]), "Buildx solve prohibited")
        require(argv[1] not in {"build", "builder", "system"}, "non-native/global build prohibited")
    if argv[0] == "git":
        require(argv[1] in {"rev-parse", "branch", "diff", "ls-files", "ls-remote"}, "Git mutation prohibited")
    require("oci-layout:///" not in " ".join(argv), "old Buildx OCI path syntax")


def native_command(argv, expected):
    require(argv == expected, "wrong exact native client/daemon/store/exporter binding")
    require(argv[0] == "/usr/bin/buildctl" and argv[1] == "--addr=unix:///run/buildkit/buildkitd.sock", "wrong native binary/daemon")
    require("--oci-layout" in argv and "--frontend=dockerfile.v0" in argv, "wrong frontend/session")
    require("oci-layout:///" not in " ".join(argv) and "buildx" not in argv and "network=host" not in " ".join(argv), "forbidden source/client/network")


def network_binding(*, required, options, build_args, proxy_url, receipt):
    if required:
        require(receipt is not None, "missing restricted enforcement receipt")
        require(options == [], "DEFAULT changed")
        require(build_args == {"HTTP_PROXY": proxy_url, "HTTPS_PROXY": proxy_url,
            "PIP_INDEX_URL": "https://pypi.org/simple"}, "wrong proxy/index/TLS transport")
    else:
        require(receipt is None, "enforcement receipt on NONE item")
        require(options == ["force-network-mode=none"] and build_args == {}, "NONE proxy/network binding incomplete")


def execution_dockerfile(original, *, frozen_base, restricted):
    require(isinstance(original, bytes) and original.endswith(b"\n"), "ambiguous Dockerfile bytes")
    source = ("FROM --platform=linux/amd64 " + frozen_base + "\n").encode()
    require(original.startswith(source) and original.count(source) == 1, "changed frozen authority/FROM")
    require(not re.search(rb"^RUN\s+--network=", original, re.M), "unexpected network directive")
    result = b"FROM --platform=linux/amd64 errpilot_frozen_base\n"
    if restricted:
        result += b"ARG PIP_INDEX_URL\n"
    result += original[len(source):]
    before = [x for x in original.splitlines(keepends=True) if x.startswith(b"RUN ")]
    after = [x for x in result.splitlines(keepends=True) if x.startswith(b"RUN ")]
    require(before == after, "RUN bytes/order changed")
    return result


def qualification_facts(facts):
    expected = {
        "total": 641, "restricted": 583, "none": 58,
        "same_daemon": True, "daemon_count": 1, "native_binary_exact": True,
        "base_mapping_exact": True, "frozen_base_authority_unchanged": True, "config_diffids_exact": True,
        "registry_fallback": False, "image_pull_fallback": False,
        "docker_exporter": True, "docker_load": True, "output_inspectable": True,
        "network_none_no_proxy": True, "none_all_RUNs_bound": True,
        "allowlist": ALLOWLIST, "pip_index": "https://pypi.org/simple", "TLS_verification": True,
        "trusted_host": False, "direct_external_path": False, "blocker_dispatch": False,
        "automatic_retry": False, "attempt_identity_regeneration": False,
        "source_acquisition": False, "oracle_execution": False, "event_3": False,
        "canonical_mutation": False, "production_client_switch_effectivity_claim": False,
    }
    for key, value in expected.items():
        require(type(facts.get(key)) is type(value) and facts.get(key) == value, "qualification fact rejected: " + key)
    return True

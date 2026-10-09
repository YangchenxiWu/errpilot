"""Pure qualification seam. This module has no provider/controller/receipt authority."""
from __future__ import annotations

import copy
from pathlib import Path

from . import corrected_production_provider_candidate as p

QUALIFICATION = Path(__file__).resolve().parent / "qualification/synthetic_identity_v1"
NAMESPACE = "SYNTHETIC_IMAGE_IDENTITY_OBSERVATION_ONLY_V1"


def observe_fixture(fixture, expected=None):
    """Exercise the candidate's content verifier and topology normalizer on local fixtures."""
    p.a.require(fixture.get("namespace") == NAMESPACE and fixture.get("runtime_authority") is False,
                "candidate-only fixture has no production authority")
    objects = copy.deepcopy(fixture["objects"])
    for role in ("daemon", "proxy"):
        data = fixture["identities"][role]
        identity = p.verify_image_identity(
            objects[role], data["store"], data["selected"],
            data["index_raw"].encode(), data["manifest_raw"].encode(), data["config_raw"].encode(),
            p.image_identity_pins(fixture["config"], role))
        objects[role]["image_config_digest"] = identity["OCI_CONFIG_DIGEST"]
    value = p.normalize_topology(objects, fixture["proxy_source"].encode(),
                                 fixture["policy_raw"].encode(), fixture["config"])
    if expected is not None:
        p.a.require(p.a.canonical(value) == p.a.canonical(expected), "stale or mismatched live topology")
    return value


def read_fixture(path):
    """Only this new qualification child is accepted; no authority object is created."""
    p.ledger.safe_path(path)
    p.a.require(path.is_relative_to(QUALIFICATION), "fixture outside exclusive candidate qualification")
    return p.exact_json(path)

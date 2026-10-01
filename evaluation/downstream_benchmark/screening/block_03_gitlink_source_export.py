"""Scoped Block-03 source representation; never acquire submodule contents.

The sibling sidecar is outside subject source. Its canonical record enters the
existing snapshot identity, separately from ordinary V2 file/symlink entries.
Only the four Human-PI-governed cookiecutter revisions are supported.
"""

from __future__ import annotations

import configparser
import json
import os
import stat
from pathlib import Path
from typing import Any


SCHEMA = "BLOCK_03_GITLINK_PROVENANCE_V1"
PATH = "docs/HelloCookieCutter1"
OBJECT = "239ea692896301eaa280dd407fdd4d5c55cf6998"
URL = "https://github.com/BruceEckel/HelloCookieCutter1"
REVISIONS = {
    ("cookiecutter::2", "BUGGY"): "d7e7b28811e474e14d1bed747115e47dcdd15ba3",
    ("cookiecutter::2", "FIXED"): "90434ff4ea4477941444f1e83313beb414838535",
    ("cookiecutter::1", "BUGGY"): "c15633745df6abdb24e02746b82aadb20b8cdf8c",
    ("cookiecutter::1", "FIXED"): "7f6804c4953a18386809f11faf4d86898570debc",
}


def _block(message: str) -> None:
    from .materializer import Blocked

    raise Blocked("BLOCKED_INPUT_IDENTITY", f"Block 03 gitlink: {message}")


def _mapping(content: bytes | None) -> None:
    if content is None:
        _block("missing .gitmodules")
    parser = configparser.RawConfigParser(strict=True, empty_lines_in_values=False)
    try:
        parser.read_string(content.decode("utf-8", errors="strict"))
    except (configparser.Error, UnicodeError) as exc:
        _block(f"malformed or conflicting .gitmodules ({type(exc).__name__})")
    section = f'submodule "{PATH}"'
    if parser.defaults() or parser.sections() != [section]:
        _block("missing, conflicting, or unsupported nested mapping")
    if set(parser[section]) != {"path", "url"} or parser[section]["path"] != PATH:
        _block("declared path mismatch or unsupported submodule options")
    if parser[section]["url"] != URL:
        _block("declared URL mismatch or unsupported relative URL")


def provenance(revision: str) -> dict[str, Any]:
    if revision not in REVISIONS.values():
        _block("revision outside adopted scope")
    return {"schema": SCHEMA, "gitlinks": [{
        "superproject_revision": revision, "path": PATH, "mode": "160000",
        "object": OBJECT, "declared_url": URL,
    }]}


def derive(recipe: dict[str, Any], label: str, revision: str,
           links: list[tuple[bytes, bytes, bytes, bytes]],
           modules: bytes | None) -> dict[str, Any] | None:
    expected = REVISIONS.get((recipe.get("canonical_case_id"), label))
    governed = recipe.get("expansion_block") == 3 and expected is not None
    if not links and not governed:
        return None
    if (not governed or type(recipe.get("expansion_block")) is not int
            or revision != expected):
        _block("gitlink outside adopted case/revision scope")
    if links != [(PATH.encode(), b"160000", b"commit", OBJECT.encode())]:
        _block("missing, transformed, nested, or unexpected gitlink identity")
    _mapping(modules)
    return provenance(revision)


def sidecar_path(source: Path) -> Path:
    return source.with_name(source.name + ".gitlinks.json")


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _block("duplicate provenance field")
        result[key] = value
    return result


def _read_at(directory: int, name: str) -> bytes:
    descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
    with os.fdopen(descriptor, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            _block("provenance/.gitmodules must be a regular file")
        return stream.read()


def read(source: Path) -> dict[str, Any] | None:
    """Verify sidecar and empty placeholder with no-follow directory traversal."""
    from .materializer import Blocked, canonical_json

    sidecar = sidecar_path(source)
    if not sidecar.exists() and not sidecar.is_symlink():
        return None
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    try:
        parent = os.open(source.parent, flags)
        try:
            data = _read_at(parent, sidecar.name)
        finally:
            os.close(parent)
        value = json.loads(data, object_pairs_hook=_unique)
        revision = value["gitlinks"][0]["superproject_revision"]
        if value != provenance(revision) or data != canonical_json(value):
            _block("noncanonical or mismatched provenance")
        root = os.open(source, flags)
        try:
            _mapping(_read_at(root, ".gitmodules"))
            docs = os.open("docs", flags, dir_fd=root)
            try:
                placeholder = os.open("HelloCookieCutter1", flags, dir_fd=docs)
                try:
                    if os.listdir(placeholder):
                        _block("populated submodule contents refused")
                finally:
                    os.close(placeholder)
            finally:
                os.close(docs)
        finally:
            os.close(root)
        return value
    except Blocked:
        raise
    except (OSError, KeyError, IndexError, TypeError, ValueError, RecursionError) as exc:
        _block(f"unrepresentable provenance/placeholder ({type(exc).__name__})")

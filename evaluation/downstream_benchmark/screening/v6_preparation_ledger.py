"""Durable once-only records; incomplete/orphan records fail closed.

Claim creation is exclusive and precedes work. Terminal publication uses a
fully fsynced temporary inode and an exclusive hard link, never replacement.
Crashes retain claims, writer locks and partial files for separate adjudication.
"""
from __future__ import annotations

import base64
import os
import re
import uuid
from pathlib import Path

from . import v6_preparation_adapter as a

SYNTHETIC = "SYNTHETIC_QUALIFICATION_ONLY"
REAL = "V6_REAL_PREPARATION"
SUCCESS = (
    "dockerfile", "build_context", "source_snapshot_or_absence", "raw_build_log",
    "image_inspection", "python_probe", "installed_distributions", "environment_identity",
)


def safe_path(path: Path) -> None:
    a.require(path.is_absolute(), "absolute persistent path required")
    a.require(all(not p.is_symlink() for p in (path, *path.parents)), "symlink ledger path")


def fsync_dir(path: Path) -> None:
    safe_path(path)
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def mkdir_durable(path: Path) -> None:
    safe_path(path)
    if path.exists():
        a.require(path.is_dir(), "persistent directory required")
        return
    mkdir_durable(path.parent)
    path.mkdir(mode=0o700)
    fsync_dir(path.parent)


def exclusive_write(path: Path, raw: bytes) -> None:
    safe_path(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        view = memoryview(raw)
        while view:
            n = os.write(fd, view)
            a.require(n > 0, "short persistent write")
            view = view[n:]
        os.fsync(fd)
    finally:
        os.close(fd)
    fsync_dir(path.parent)


def atomic_publish(path: Path, raw: bytes) -> None:
    """A same-filesystem hard link is atomic and fails if final name exists."""
    safe_path(path)
    partial = path.with_name(path.name + ".partial." + uuid.uuid4().hex)
    exclusive_write(partial, raw)
    os.link(partial, path, follow_symlinks=False)
    fsync_dir(path.parent)
    partial.unlink()
    fsync_dir(path.parent)


def persist_tree(root: Path) -> dict[str, str]:
    """Fsync evidence files/directories before binding a terminal census."""
    safe_path(root)
    hashes = {}
    paths = sorted(root.rglob("*"))
    for path in paths:
        if path.is_symlink():
            target = os.fsencode(os.readlink(path))
            relative = path.relative_to(root)
            a.shared._safe_link_target(tuple(os.fsencode(p) for p in relative.parts[:-1]), target)
            hashes[str(relative)] = a.identity({"entry_type": "symlink",
                "target_b64": base64.b64encode(target).decode("ascii")})
        elif path.is_file():
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
            hashes[str(path.relative_to(root))] = a.sha(path.read_bytes())
        else:
            a.require(path.is_dir(), "evidence special file refused")
    for path in reversed(paths):
        if path.is_dir() and not path.is_symlink():
            fsync_dir(path)
    fsync_dir(root)
    return hashes


class Ledger:
    def __init__(self, root: Path, *, namespace: str, real_ids=()):
        safe_path(root)
        a.require(namespace in (SYNTHETIC, REAL), "ledger namespace")
        if namespace == SYNTHETIC:
            a.require(root.is_relative_to(a.OUTPUT_ROOT / "qualification"),
                      "synthetic ledger outside qualification subtree")
        else:
            a.require(root == a.OUTPUT_ROOT, "wrong real output root")
        self.root, self.namespace = root, namespace
        self.real_ids = frozenset(real_ids)

    def initialize(self):
        for name in ("claims", "terminals", "locks"):
            mkdir_durable(self.root / "ledger" / name)

    def _path(self, name, attempt):
        a.require(isinstance(attempt, str) and re.fullmatch(r"[A-Za-z0-9_-]+", attempt),
                  "unsafe attempt ID")
        if self.namespace == SYNTHETIC:
            a.require(attempt.startswith("SYNTHETIC_QUALIFICATION_")
                      and attempt not in self.real_ids, "real identity in synthetic ledger")
        else:
            a.require(attempt in self.real_ids, "unknown real attempt identity")
        path = self.root / "ledger" / name / (attempt + ".json")
        safe_path(path)
        return path

    def _read(self, path):
        safe_path(path)
        a.require(path.is_file(), "missing claim/terminal")
        record = a.loads(path.read_bytes())
        a.require(record["namespace"] == self.namespace, "record namespace mismatch")
        return record

    def state(self, attempt):
        claim = self._path("claims", attempt)
        terminal = self._path("terminals", attempt)
        lock = self._path("locks", attempt)
        partial = list(terminal.parent.glob(terminal.name + ".partial.*"))
        a.require(not partial, "orphan/partial terminal blocks")
        if terminal.exists():
            c, t = self._read(claim), self._read(terminal)
            a.require(t["claim_sha256"] == a.identity(c), "terminal claim binding")
            return t["state"]
        if claim.exists():
            self._read(claim)
            return "CLAIMED_NO_TERMINAL"
        a.require(not lock.exists(), "orphan writer lock blocks")
        return "UNSTARTED"

    def claim(self, attempt, binding, *, permit=None):
        if self.namespace == REAL:
            from .v6_preparation_runtime import Admission
            a.require(isinstance(permit, Admission) and permit.item["base_attempt_id"] == attempt
                      and permit.binding == binding, "real claim requires admission")
            permit.revalidate()
        a.require(self.state(attempt) == "UNSTARTED", "duplicate claim/no automatic retry")
        owner = uuid.uuid4().hex
        lock = self._path("locks", attempt)
        body = {"namespace": self.namespace, "attempt_id": attempt, "owner": owner}
        exclusive_write(lock, a.canonical(body))
        # Lock is retained on any later failure. There is no reclaim/retry path.
        a.require(not self._path("terminals", attempt).exists(), "terminal before claim")
        record = {**body, "operation": "CLAIM", "input_runtime_binding": binding,
                  "state": "CLAIMED_NO_TERMINAL", "attempt_consumed": True}
        exclusive_write(self._path("claims", attempt), a.canonical(record))
        return record

    def terminal(self, claim, *, state, evidence, reason=""):
        attempt = claim["attempt_id"]
        a.require(self._read(self._path("claims", attempt)) == claim, "claim identity mismatch")
        lock = self._path("locks", attempt)
        a.require(self._read(lock) == {k: claim[k] for k in ("namespace", "attempt_id", "owner")},
                  "writer ownership mismatch")
        a.require(self.state(attempt) == "CLAIMED_NO_TERMINAL", "duplicate/overwrite terminal")
        a.require(state in ("MATERIALIZED", "BUILD_FAILED", "INTERRUPTED")
                  or isinstance(state, str) and re.fullmatch(r"BLOCKED_[A-Z0-9_]+", state),
                  "terminal state")
        a.require(isinstance(evidence, dict) and bool(evidence), "terminal evidence required")
        if state == "MATERIALIZED":
            a.require(set(SUCCESS) <= set(evidence), "success observations missing")
            a.require(all(isinstance(evidence[k], str) and a.shared.HEX64.fullmatch(evidence[k])
                          for k in SUCCESS), "success evidence digest missing")
        else:
            a.require(isinstance(reason, str) and bool(reason), "failure/interruption reason")
        record = {"namespace": self.namespace, "operation": "TERMINAL", "attempt_id": attempt,
                  "claim_sha256": a.identity(claim), "state": state,
                  "evidence": evidence, "reason": reason}
        atomic_publish(self._path("terminals", attempt), a.canonical(record))
        # Only the current verified owner after durable terminal publication releases.
        a.require(self._read(lock)["owner"] == claim["owner"], "lock owner changed")
        lock.unlink()
        fsync_dir(lock.parent)
        return record

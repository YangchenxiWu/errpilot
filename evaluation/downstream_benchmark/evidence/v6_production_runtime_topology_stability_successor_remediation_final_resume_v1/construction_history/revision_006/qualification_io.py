"""Candidate-only descriptor-relative qualification I/O; frozen modules untouched."""
from __future__ import annotations

import errno
import fnmatch
import fcntl
import os
import stat
import sys
import threading
import uuid
from pathlib import Path, PosixPath

from evaluation.downstream_benchmark.screening import v6_preparation_adapter as a

SOURCE = a.ROOT / ('evaluation/downstream_benchmark/evidence/'
                   'v6_production_runtime_topology_stability_successor_remediation_final_resume_v1/qualification_io.py')
ROOT = a.OUTPUT_ROOT / 'qualification/production_runtime_topology_stability_successor_remediation_final_resume_v1'
FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


def checked(value):
    spelling = os.fspath(value)
    a.require(isinstance(spelling, str) and spelling.startswith('/')
              and all(part not in {'.', '..', ''} for part in spelling.split('/')[1:]),
              'F01 absolute canonical spelling required; traversal/alias rejected')
    path = Path(spelling)
    a.require(path == ROOT or path.is_relative_to(ROOT), 'F01 outside exact qualification root')
    a.require(spelling == str(path), 'F01 path spelling alias rejected')
    return path


class QualificationIO:
    """Every operation walks actual parent components with O_NOFOLLOW.

    Directory capabilities are held through each syscall, including both sides
    of terminal hard-link publication. This proves no symlink traversal during
    an operation; it does not promise protection against a privileged actor
    moving an already-open directory outside the authorized filesystem tree.
    """
    def __init__(self, scope=ROOT):
        a.require(Path(__file__).resolve() == SOURCE, 'F01 copied I/O helper forbidden')
        self.scope = checked(scope)
        self.anchor = None

    def bind(self):
        fd = self.directory(self.scope)
        try:
            info = os.fstat(fd)
            self.anchor = (info.st_dev, info.st_ino)
        finally:
            os.close(fd)
        return self

    def path(self, value):
        path = checked(value)
        a.require(path == self.scope or path.is_relative_to(self.scope), 'F01 cross-namespace path')
        # Resolution is an additional check, not the syscall confinement mechanism.
        a.require(path.resolve(strict=False) == path, 'F01 symlink/resolved alias rejected')
        return path

    def verify_descriptor(self, fd, expected):
        """macOS F_GETPATH verifies the current name of the held capability.

        O_NOFOLLOW remains the open-time mechanism. This additional syscall rejects
        replacement/relocation observed before relevant I/O; it is not a claim of
        immunity to a privileged concurrent rename after the last verification.
        """
        a.require(sys.platform == 'darwin' and hasattr(fcntl, 'F_GETPATH'),
                  'F01 macOS descriptor-path primitive unavailable')
        raw = fcntl.fcntl(fd, fcntl.F_GETPATH, bytes(1024)).split(b'\0', 1)[0]
        a.require(raw.decode('utf-8') == str(expected),
                  'F01 descriptor path replaced or relocated')

    def directory(self, value, *, create=False, exclusive=False, mode=0o700):
        path = self.path(value)
        fd = os.open('/', FLAGS)
        try:
            parts = path.parts[1:]
            for number, component in enumerate(parts):
                final = number == len(parts) - 1
                try:
                    child = os.open(component, FLAGS, dir_fd=fd)
                except FileNotFoundError:
                    if not create:
                        raise
                    os.mkdir(component, mode if final else 0o700, dir_fd=fd)
                    os.fsync(fd)
                    child = os.open(component, FLAGS, dir_fd=fd)
                except OSError as exc:
                    if exc.errno in {errno.ELOOP, errno.ENOTDIR}:
                        raise a.Rejected('F01 no-follow component refused: ' + component) from exc
                    raise
                else:
                    if final and exclusive:
                        os.close(child)
                        raise FileExistsError(str(path))
                try:
                    self.verify_descriptor(child, Path('/').joinpath(*parts[:number + 1]))
                except BaseException:
                    os.close(child)
                    raise
                if number == len(self.scope.parts) - 2 and self.anchor is not None:
                    info = os.fstat(child)
                    if (info.st_dev, info.st_ino) != self.anchor:
                        os.close(child)
                        raise a.Rejected('F01 qualification namespace replaced')
                os.close(fd)
                fd = child
            return fd
        except BaseException:
            os.close(fd)
            raise

    def mkdir(self, path, *, parents=True, exist_ok=True, mode=0o700):
        path = self.path(path)
        if not parents:
            parent = self.directory(path.parent)
            try:
                try:
                    os.mkdir(path.name, mode, dir_fd=parent)
                    os.fsync(parent)
                except FileExistsError:
                    if not exist_ok:
                        raise
                    fd = os.open(path.name, FLAGS, dir_fd=parent)
                    os.close(fd)
            finally:
                os.close(parent)
            return
        fd = self.directory(path, create=True, exclusive=not exist_ok, mode=mode)
        os.close(fd)

    def mkdir_durable(self, value):
        return self.mkdir(value, parents=True, exist_ok=True)

    def read(self, value):
        path = self.path(value)
        parent = self.directory(path.parent)
        try:
            self.verify_descriptor(parent, path.parent)
            fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
            with os.fdopen(fd, 'rb') as stream:
                self.verify_descriptor(stream.fileno(), path)
                a.require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), 'F01 regular file required')
                return stream.read()
        finally:
            os.close(parent)

    def exclusive_write(self, value, raw, *, mode=0o600):
        path = self.path(value)
        parent = self.directory(path.parent)
        try:
            self.verify_descriptor(parent, path.parent)
            fd = os.open(path.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                         mode, dir_fd=parent)
            try:
                view = memoryview(raw)
                while view:
                    self.verify_descriptor(fd, path)
                    count = os.write(fd, view)
                    a.require(count > 0, 'short persistent write')
                    view = view[count:]
                os.fsync(fd)
            finally:
                os.close(fd)
            os.fsync(parent)
        finally:
            os.close(parent)

    def atomic_publish(self, value, raw):
        path = self.path(value)
        partial = path.with_name(path.name + '.partial.' + uuid.uuid4().hex)
        self.exclusive_write(partial, raw)
        parent = self.directory(path.parent)
        try:
            self.verify_descriptor(parent, path.parent)
            os.link(partial.name, path.name, src_dir_fd=parent, dst_dir_fd=parent,
                    follow_symlinks=False)
            os.fsync(parent)
            os.unlink(partial.name, dir_fd=parent)
            os.fsync(parent)
        finally:
            os.close(parent)

    def unlink(self, value):
        path = self.path(value)
        parent = self.directory(path.parent)
        try:
            self.verify_descriptor(parent, path.parent)
            os.unlink(path.name, dir_fd=parent)
            os.fsync(parent)
        finally:
            os.close(parent)

    def fsync_dir(self, value):
        fd = self.directory(value)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def names(self, value):
        fd = self.directory(value)
        try:
            return sorted(os.listdir(fd))
        finally:
            os.close(fd)

    def info(self, value):
        path = self.path(value)
        if path == self.scope:
            fd = self.directory(path)
            try:
                return os.fstat(fd)
            finally:
                os.close(fd)
        parent = self.directory(path.parent)
        try:
            info = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
            a.require(not stat.S_ISLNK(info.st_mode), 'F01 symlink leaf rejected')
            return info
        finally:
            os.close(parent)

    def persist_tree(self, value):
        root = self.path(value)
        hashes = {}
        def visit(path):
            for name in self.names(path):
                child = path / name
                info = self.info(child)
                if stat.S_ISDIR(info.st_mode):
                    visit(child)
                else:
                    a.require(stat.S_ISREG(info.st_mode), 'F01 special evidence file rejected')
                    hashes[str(child.relative_to(root))] = a.sha(self.read(child))
                    parent = self.directory(child.parent)
                    try:
                        fd = os.open(child.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
                        try:
                            os.fsync(fd)
                        finally:
                            os.close(fd)
                    finally:
                        os.close(parent)
            self.fsync_dir(path)
        visit(root)
        return hashes


class ConfinedPath(PosixPath):
    """Path interface supplied only to the unchanged scientific code object.

    Writes remain exclusive even though the original code calls write_bytes.
    Native os.open calls are handled by the descriptor-anchored manifest adapter.
    """
    def __init__(self, *segments, io=None):
        super().__init__(*segments)
        self.io = io if io is not None else QualificationIO().bind()

    def with_segments(self, *segments):
        return type(self)(*segments, io=self.io)

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        self.io.mkdir(self, mode=mode, parents=parents, exist_ok=exist_ok)

    def write_bytes(self, raw):
        self.io.exclusive_write(self, raw, mode=0o666)
        return len(raw)

    def read_bytes(self):
        return self.io.read(self)

    def resolve(self, strict=False):
        path = self.io.path(self)
        if strict:
            self.io.info(path)
        return ConfinedPath(path, io=self.io)

    def exists(self, *, follow_symlinks=True):
        try:
            self.io.info(self)
            return True
        except FileNotFoundError:
            return False

    def is_file(self, *, follow_symlinks=True):
        try:
            return stat.S_ISREG(self.io.info(self).st_mode)
        except FileNotFoundError:
            return False

    def is_dir(self, *, follow_symlinks=True):
        try:
            return stat.S_ISDIR(self.io.info(self).st_mode)
        except FileNotFoundError:
            return False

    def glob(self, pattern, *, case_sensitive=None, recurse_symlinks=False):
        a.require('/' not in pattern and '**' not in pattern, 'F01 bounded glob only')
        return (self / name for name in self.io.names(self)
                if fnmatch.fnmatchcase(name, pattern))


def anchored_manifest_entries(path):
    """Invoke the exact frozen walker from a pinned directory cwd in one thread.

    No frozen global or code object is replaced. All manifest bytes are still
    computed by the original walker; cwd is restored through its saved fd.
    """
    a.require(threading.active_count() == 1, 'F01 anchored walker requires single thread')
    a.require(type(path) is ConfinedPath, 'F01 confined manifest path required')
    fd = path.io.directory(path)
    old = os.open('.', FLAGS)
    try:
        os.fchdir(fd)
        return a.shared._manifest_entries(Path('.'))
    finally:
        os.fchdir(old)
        os.close(old)
        os.close(fd)

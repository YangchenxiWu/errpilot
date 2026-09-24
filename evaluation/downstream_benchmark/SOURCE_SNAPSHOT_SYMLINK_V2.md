# BugsInPy source snapshot symlink representation V2

Status candidate: `SOURCE_SNAPSHOT_SYMLINK_V2_FROZEN`. This amendment changes
future source snapshot and build context representation only. A separate
Human-PI transaction is required before any Batch-02 materialization attempt.

## A. Trigger and contradiction

The preceding Batch-02 transaction stopped as
`BLOCKED_BEFORE_BUILD_DUE_TO_SOURCE_SNAPSHOT_SYMLINK_REPRESENTATION`: zero build
attempts, zero Batch-02 identities, and no subject test or oracle. The frozen
`black::17` and `ansible::15` revisions contain tracked Git symlinks. The V1
materializer rejected every symlink, so it could not represent those exact
revisions. Omitting a link, replacing it with target contents, or rewriting its
target would change the revision representation.

## B. Source snapshot manifest

`SOURCE_SNAPSHOT_MANIFEST_V2` has an `entries` array sorted by relative POSIX
path. A regular file entry has `path`, `entry_type: "file"`,
`content_sha256` over exact file bytes, and recorded permission `mode`. A
symlink entry has `path`, `entry_type: "symlink"`, `target_b64` over the exact
target byte sequence, and `target_sha256` over those same bytes. Directory
entries are omitted. The benchmark `canonical_json` serializer produces
sorted-key, compact UTF-8 JSON with one final LF; its SHA-256 is the source
snapshot identity. V2 does not reinterpret any historical V1 identity.

The materializer reads symlinks with `os.readlink` on a bytes name. It never
opens a target to determine link identity, decodes/re-encodes target bytes, or
requires a target to exist. File and directory traversal uses directory file
descriptors, `stat(..., follow_symlinks=False)`, and `O_NOFOLLOW`; a symlink
directory is an entry and is never traversed. Special filesystem entries are
rejected. Paths that cannot be represented as UTF-8 POSIX paths are blocked
rather than silently renamed.

## C. Lexical safety gate

The snapshot root must be a real directory, and every visited link path is
inside it. A link target must be nonempty and relative. Starting at the link's
parent, process `.` and `..` components lexically; any step above the snapshot
root gives `BLOCKED_UNSAFE_SYMLINK`. Absolute targets, malformed targets, and
targets naming or resolving through forbidden metadata also give that status.
The forbidden names remain `.git`, `bug_patch.txt`, `screening_evidence`,
`bug.info`, and `project.info`. This check does not follow the link or require
the target to exist. An unsafe revision must not be rewritten or materialized;
Human-PI adjudication requires a separate transaction.

## D. Context and Docker copy

`shutil.copytree(..., symlinks=True)` preserves the source links in the build
context. `BUILD_CONTEXT_MANIFEST_V2` uses the same explicit file and symlink
entries, deterministic order, canonical serialization, no-follow traversal,
and special-file rejection. File bytes are hashed; symlink target bytes are
base64-encoded and hashed. Packaging metadata identity is derived from these
no-follow context entries, including when a packaging file is a symlink.
The Dockerfile retains `COPY source/ /subject/`; the synthetic `linux/amd64`,
`--network=none` image test checks `lstat` and exact `readlink` target bytes
inside the resulting image. It does not use subject code or install packages.

## E. Read-only four-revision metadata audit

The audit read only tracked tree paths, Git modes/types, and symlink blob
bytes. It did not inspect patches, revision diffs, logs, tests, or oracles.

| Case | Revision | Tracked symlinks | Safe relative | Absolute | Lexical escape | Malformed/unrepresentable |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `black::17` | BUGGY | 12 | 12 | 0 | 0 | 0 |
| `black::17` | FIXED | 12 | 12 | 0 | 0 | 0 |
| `ansible::15` | BUGGY | 354 | 354 | 0 | 0 | 0 |
| `ansible::15` | FIXED | 354 | 354 | 0 | 0 | 0 |

No audited symlink path or resolved target used a forbidden name. Classification:
`REAL_REVISION_SYMLINK_AUDIT_PASS` under the stated lexical rule. This is a
metadata-only observation, not a materialization, eligibility, or runtime result.

## F. Historical evidence and authority

Completed Batch-01 `SOURCE_SNAPSHOT_MANIFEST_V1` and
`BUILD_CONTEXT_MANIFEST_V1` files remain historical evidence and are not
rewritten. No Batch-01 rebuild is authorized. The V2 code applies only to
future materialization attempts. This transaction performs zero real subject
builds, dependency installations, setup actions, subject imports, subject
tests, oracles, repairs, and model/API calls. Batch-02 remains unattempted;
even after V2 freezes, a new explicit Human-PI authority gate is required for
the named cases, exact revisions, recipes, output paths, and any build network
policy before materialization can begin.

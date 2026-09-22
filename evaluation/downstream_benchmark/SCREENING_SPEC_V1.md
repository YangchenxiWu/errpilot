# ErrPilot BugsInPy Candidate Screening Specification v1

- Specification ID: `EP-BIPS-1`
- Status: screening procedure and initial metadata candidate set frozen; eligibility
  execution not performed and not authorized
- Authority: human-PI transaction instruction dated 2026-09-22
- Controlling protocol: `EP-DBP-1` (`PROTOCOL.md`)
- Controlling run specification: `EP-DBRS-1` (`RUN_SPEC_V1.md`)
- Sampling seed: `20260922`

Normative terms `MUST`, `MUST NOT`, `REQUIRED`, and `BLOCK` are hard gates. This
specification does not amend `PROTOCOL.md` or `RUN_SPEC_V1.md`. A contradiction
between controlling artifacts MUST BLOCK and be returned to the human PI.

## A. Authority and scope

This version authorizes and records only:

1. acquisition of the pinned BugsInPy metadata/framework;
2. a metadata-only census;
3. deterministic construction of the initial candidate set; and
4. freezing the procedure for a separately authorized future eligibility screen.

It does not authorize subject-project acquisition, environment construction,
`run_test.sh` execution, buggy/fixed eligibility execution, pilot selection or
execution, repair execution, ErrPilot invocation, or model/API invocation. It does
not establish that any candidate is eligible.

## B. Pinned BugsInPy identity

The only BugsInPy source identity for this specification is:

- repository: `https://github.com/soarsmu/BugsInPy.git`;
- commit: `11c5f1eea954a42132cfd06bf257766a7963e0fd`;
- tree: `d00ce0495ba73abe50317599f48bced3c9afe4b3`;
- external clone: `/Users/wuyangchenxi/errpilot-benchmark-work/bugsinpy`;
- checkout mode: detached `HEAD`.

Every use MUST verify the exact commit before reading metadata. The acquisition and
framework hashes are recorded in `BUGSINPY_ACQUISITION.md`. Upstream branch movement
MUST NOT silently change the experiment identity.

## C. Metadata census rules

The census unit is each directory matching
`projects/<project>/bugs/<bug_id>/` at the pinned BugsInPy tree. The parser MUST be
inert: it may parse literal scalar assignments but MUST NOT source or execute an
info file.

Permitted case-selection inputs are only:

- project name, normalized `status`, and source URL from `project.info`;
- BugsInPy bug ID;
- Python version, buggy commit ID, fixed commit ID, and declared test file from
  `bug.info`;
- existence and non-empty size of `run_test.sh`; and
- existence of `setup.sh` and `requirements.txt`.

A case is metadata-eligible exactly when:

1. `project.info` exists and is syntactically parseable;
2. normalized project status is exactly `OK`;
3. `bug.info` exists, is syntactically parseable, and provides non-empty Python
   version, buggy commit ID, fixed commit ID, and declared test file;
4. each commit ID is a 7-to-40-character hexadecimal Git identifier;
5. buggy and fixed identifiers are distinct; and
6. `run_test.sh` exists and is non-empty.

An abbreviated commit identifier is acceptable only at this metadata stage. A
future acquisition gate MUST resolve and freeze the full immutable object identity
before any execution. Missing `setup.sh` or `requirements.txt` is recorded but is
not a metadata exclusion criterion. Difficulty, project size, dependency burden,
patch characteristics, test convenience, or predicted environment failure MUST NOT
affect metadata selection.

The frozen census contains 501 cases across 17 projects: 500 metadata-eligible and
1 metadata-excluded. The sole exclusion is `keras::12` with reason
`BUGGY_FIXED_COMMIT_IDS_IDENTICAL`. Metadata exclusions are recorded only in
`screening_metadata_exclusions.csv`; `cases_manifest.csv` and `exclusions.csv`
remain reserved for executed eligibility evidence.

The metadata exclusion reason vocabulary is:

- `PROJECT_INFO_MISSING`;
- `PROJECT_INFO_UNPARSEABLE`;
- `PROJECT_STATUS_NOT_OK`;
- `BUG_INFO_MISSING`;
- `BUG_INFO_UNPARSEABLE`;
- `PYTHON_VERSION_MISSING`;
- `BUGGY_COMMIT_ID_MISSING`;
- `BUGGY_COMMIT_ID_INVALID`;
- `FIXED_COMMIT_ID_MISSING`;
- `FIXED_COMMIT_ID_INVALID`;
- `DECLARED_TEST_FILE_MISSING`;
- `RUN_TEST_MISSING`;
- `RUN_TEST_EMPTY`; and
- `BUGGY_FIXED_COMMIT_IDS_IDENTICAL`.

## D. Candidate-selection algorithm and frozen initial set

For every metadata-eligible case, the canonical identity is the exact UTF-8 string
`<project>::<bug_id>`. Its rank digest is lowercase hexadecimal SHA-256 of:

```text
20260922|candidate|<project>::<bug_id>
```

Candidates are sorted ascending by this digest, with canonical identity as the
deterministic collision tie-breaker. Traverse that order and admit a case unless
its project already has four admitted cases. Stop after 40 admissions. If the
first pass represented fewer than 10 projects while at least 10 eligible projects
existed, rank projects by lowercase hexadecimal SHA-256 of
`20260922|project|<project>`, admit the highest-ranked case from each of the first
10 project ranks, then fill from the global candidate order without exceeding four
per project. If 40 cases, 10 projects, and the cap cannot all be satisfied, BLOCK
for human-PI adjudication; do not invent a replacement rule.

The diversity pass was not needed. The frozen initial set has 40 candidates across
15 projects and no project contributes more than four. In selection order it is:

1. `pandas::102`
2. `pandas::78`
3. `pandas::4`
4. `pandas::45`
5. `scrapy::4`
6. `keras::9`
7. `matplotlib::17`
8. `keras::18`
9. `matplotlib::11`
10. `keras::28`
11. `luigi::31`
12. `youtube-dl::7`
13. `scrapy::19`
14. `scrapy::15`
15. `keras::15`
16. `black::17`
17. `scrapy::14`
18. `thefuck::9`
19. `httpie::1`
20. `ansible::15`
21. `tornado::6`
22. `luigi::4`
23. `fastapi::2`
24. `youtube-dl::37`
25. `youtube-dl::18`
26. `spacy::4`
27. `ansible::2`
28. `sanic::1`
29. `thefuck::26`
30. `thefuck::28`
31. `fastapi::13`
32. `ansible::4`
33. `black::16`
34. `spacy::1`
35. `httpie::3`
36. `matplotlib::29`
37. `tqdm::3`
38. `fastapi::11`
39. `ansible::16`
40. `httpie::4`

`candidate_universe.csv` is the authoritative row-level census, rank digest, and
selection record. Its SHA-256 at freeze is
`78208adf610a50542be6dfbd03a9b25960ba0b5cfc80768b08ffe7a4c78f3b8c`.
`initial_selection_order` preserves admission order; `candidate_rank` preserves
global digest rank. The set MUST NOT be altered after observing screening results.

## E. Fix-leakage prohibition

Candidate selection and all later repair-agent preparation MUST NOT read, expose,
copy, summarize, hash into agent-visible material, or otherwise use:

- `bug_patch.txt` contents or any official repair patch;
- source diffs between buggy and fixed revisions;
- commit messages whose purpose is to reveal the repair;
- human-written fix explanations; or
- patch size, location, simplicity, or perceived repair difficulty.

Fixed revision identifiers may be recorded and a fixed revision may later be
executed by the runner-controlled eligibility gate. Its content is not a selection
input and MUST remain inaccessible to any repair agent.

## F. External workspace layout

All large repositories, subject checkouts, environments, dependency caches, and
execution evidence MUST remain outside the ErrPilot Git repository under:

```text
/Users/wuyangchenxi/errpilot-benchmark-work/
  bugsinpy/
  screening_workspaces/
  screening_evidence/
  caches/
```

This is runner-owned research state. Only frozen specifications, metadata ledgers,
and bounded reproducibility helpers may be committed under
`evaluation/downstream_benchmark/`.

## G. Future subject-repository acquisition boundary

Subject repositories MUST NOT be acquired until a separate human authorization.
When authorized, the runner alone MUST acquire them into the external workspace,
resolve both declared revisions to exact full commit identities, record canonical
source URLs and acquisition evidence, and preserve an immutable metadata-to-object
mapping. Acquisition failure is evidence; it MUST NOT cause candidate replacement
or a change to the ranking.

The acquisition process MUST NOT expose fixed contents, official patches, repair
history, or selection-independent fix clues to the future repair workspace.

## H. Future environment construction identity requirements

Before a candidate may execute, the runner MUST freeze all identities required by
section H of `RUN_SPEC_V1.md`, including exact source revisions, immutable
environment/container digest, exact Python version, complete dependency and build
identity, relevant system dependency identity, oracle and protected-manifest
digests, and the controlling benchmark digests. A matching interpreter version or
mutable image tag alone is insufficient. Missing, ambiguous, or mutable-only
identity MUST produce `UNSUPPORTED_ENVIRONMENT` or the more specific applicable
infrastructure reason and MUST NOT be retried into eligibility.

## I. Future 3/3 buggy/fixed eligibility gate

Under a separately authorized screening transaction, a candidate is eligible if
and only if the exact preregistered oracle produces:

```text
BUGGY = FAIL / FAIL / FAIL
FIXED = PASS / PASS / PASS
```

All six independent executions are mandatory. Each starts from a freshly restored
candidate state with declared ephemeral state cleared and may share only read-only,
content-addressed dependencies. No desired first outcome permits early stopping.
Any inconsistent, invalid, skipped, or missing execution makes the candidate
ineligible under `RUN_SPEC_V1.md`. Setup or infrastructure failure MUST NOT be
silently retried until a desired sequence appears.

## J. Exact execution ordering

For each candidate, future screening MUST perform these steps in order:

1. prepare the runner-controlled environment;
2. establish exact buggy and fixed subject commit identities;
3. establish and freeze the oracle command from BugsInPy metadata/framework;
4. prepare and freeze the protected-test manifest;
5. run the buggy oracle exactly three independent times;
6. run the fixed oracle exactly three independent times;
7. preserve every required artifact before classification; and
8. classify the candidate once, without an unrecorded rerun.

Candidate order is the frozen `initial_selection_order` in
`candidate_universe.csv`, followed only by a separately triggered expansion under
section M. Execution scheduling MUST NOT change selection or eligibility rules.

## K. Evidence capture requirements

For all six future executions, preserve separately:

- canonical case ID and exact full revision;
- immutable environment and dependency identity;
- exact command bytes and working directory;
- start and end timestamps;
- exit status;
- raw stdout and stderr bytes plus SHA-256 identities;
- expected-test-observed evidence;
- freshly restored state and ephemeral-state evidence; and
- protected-manifest identity and integrity evidence.

Raw evidence is immutable and resides in `screening_evidence/`. Derived ledgers
refer to it by path and digest. Missing evidence is not a pass. Eligibility results
must later populate the existing `cases_manifest.csv` and `exclusions.csv` without
rewriting this metadata census.

## L. Exclusion taxonomy

Future executed screening uses specific reasons and MUST NOT overload one category
to conceal distinct failures:

- `METADATA_INCOMPLETE`
- `PROJECT_STATUS_NOT_OK`
- `SOURCE_ACQUISITION_FAILURE`
- `UNSUPPORTED_ENVIRONMENT`
- `DEPENDENCY_SETUP_FAILURE`
- `ORACLE_COMMAND_INVALID`
- `BUGGY_NOT_3_OF_3_FAIL`
- `FIXED_NOT_3_OF_3_PASS`
- `NONDETERMINISTIC_ORACLE`
- `EXTERNAL_SERVICE_REQUIRED`
- `GUI_INTERACTION_REQUIRED`
- `OUTSIDE_ERRPILOT_SCOPE`
- `PROTECTED_MANIFEST_UNRESOLVED`
- `OTHER_INFRASTRUCTURE_FAILURE`

When more than one failure applies, preserve each orthogonally with its evidence;
do not choose a vague reason merely to shorten the record.

## M. Future expansion rule

Do not execute expansion under this transaction. If completed 3/3 screening of the
initial 40 yields too few eligible cases to reserve four permanently separate pilot
cases and select 24 final cases across at least six projects with no more than four
final cases per project, expansion MUST use the next cases in the already frozen
global candidate ranking.

Expansion occurs in blocks of 10 admissions. The cursor begins after the final
global rank examined to create the current candidate set; previously skipped cases
remain skipped. Traverse forward, admit only metadata-eligible cases not already in
the candidate set, and maintain the cumulative four-candidate-per-project cap. A
block and its identities MUST be frozen before any outcome is observed from that
block. If a full block cannot be formed under the cap or the ranking is exhausted,
BLOCK for human-PI adjudication rather than hand-picking, changing the seed, reusing
an earlier skipped case, or weakening the cap. Pilot and final selection remain
governed by `PROTOCOL.md` and `RUN_SPEC_V1.md`; screening results cannot alter the
candidate ranking.

## N. Prohibition on repair-agent invocation

Screening is runner-controlled reproducibility work, not repair work. No Codex,
ErrPilot repair mode, other model, or repair agent may be invoked to acquire,
select, prepare, execute, diagnose, or classify a candidate. No model/API call is
authorized by this specification.

## O. Separation of screening evidence and repair workspaces

Runner screening evidence and future repair workspaces MUST be physically and
permission-separated. A repair workspace MUST be constructed from a buggy source
snapshot without accessible official-fix history and MUST NOT expose:

- BugsInPy metadata directories;
- `bug_patch.txt` or any official patch;
- fixed revision contents;
- Git history capable of recovering the official fix;
- screening commands, outputs, classifications, or evidence;
- paired-condition, prior-repetition, or pilot artifacts; or
- another case or condition's files or writable caches.

The runner may retain fixed and screening materials only outside the agent's
read/write boundary. Creating the live repair workspace is not authorized here.

## P. No eligibility execution has occurred

At this freeze boundary:

- no subject repository has been cloned or checked out;
- no subject dependency or environment has been installed or constructed;
- no `run_test.sh` or subject oracle has been executed;
- no buggy or fixed 3/3 outcome exists;
- no protected-test manifest has been constructed for a real case;
- no pilot, repair, ErrPilot, Codex, or model/API run has occurred; and
- `cases_manifest.csv` and `exclusions.csv` remain header-only.

Therefore the only permitted success label for this transaction is
`BUGSINPY_SCREENING_SPEC_V1_FROZEN`. It does not mean that any case is eligible,
that BugsInPy execution is validated, that a pilot or repair has run, or that
ErrPilot effectiveness has been measured.

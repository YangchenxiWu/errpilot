# BugsInPy Acquisition Record

- Record status: acquisition complete; metadata-only use
- Acquisition timestamp (UTC): `2026-09-22T15:48:19Z`
- Canonical repository: `https://github.com/soarsmu/BugsInPy.git`
- Local clone path: `/Users/wuyangchenxi/errpilot-benchmark-work/bugsinpy`
- Pinned commit: `11c5f1eea954a42132cfd06bf257766a7963e0fd`
- Pinned tree: `d00ce0495ba73abe50317599f48bced3c9afe4b3`
- Checkout state: detached `HEAD`
- Checkout status after acquisition: clean

The external clone is runner-owned research state. It is not part of the ErrPilot
repository and MUST NOT be modified. A moving upstream branch is not an experiment
identity; every metadata operation governed by `SCREENING_SPEC_V1.md` MUST first
verify the exact pinned commit above.

## Framework identity

The repository commit and tree above are the controlling BugsInPy framework
identity. The SHA-256 identities of the framework entrypoints at that commit are:

| Relative path | SHA-256 |
| --- | --- |
| `framework/bin/bugsinpy-checkout` | `36d1f5b8fbef2fbd2b6d4dc0c9d95089c5e82d9fe222dfa96392ab175ee1b1e1` |
| `framework/bin/bugsinpy-compile` | `faf0fd1c427721c00884872c3effe78ede5eff0c0c19ee169cafcad720eeccab` |
| `framework/bin/bugsinpy-coverage` | `955c1ef549509b69194b4bfe1a7db05e6930fab6318508042d294a063e8191ac` |
| `framework/bin/bugsinpy-fuzz` | `bf7ff17cab8070bcbb79d7c02940a045f2dd5f45fce11d0286ab28e043904c79` |
| `framework/bin/bugsinpy-info` | `afb272ebba4cdfe7dc593309976960d0041172dffd4b79f979a9e3692da75232` |
| `framework/bin/bugsinpy-mutation` | `69aa664674f7da4ef33d9be3ca65666e7e7f603be209e343d82f83f32c8eae21` |
| `framework/bin/bugsinpy-test` | `439edaa83ee1f518d70d7c5f195568e0217860e7be38a062188b5cf991078696` |

These hashes identify files only. No BugsInPy framework command or subject-project
test command was executed during this transaction.

## Acquisition and census evidence

- The pinned commit was verified as a Git commit before checkout.
- `HEAD` and `HEAD^{tree}` were verified after checkout.
- The checkout was verified detached and clean.
- The metadata census opened only `project.info` and `bug.info` as text.
- File-system metadata only was inspected for `run_test.sh`, `setup.sh`, and
  `requirements.txt`; no subject script was executed.
- Census cases: 501 across 17 projects.
- Metadata-eligible cases: 500 across 17 projects.
- Metadata-stage exclusions: 1 (`keras::12`, because the declared buggy and fixed
  commit IDs are identical).
- Initial candidates: 40 across 15 projects, maximum 4 per project.
- `candidate_universe.csv` SHA-256:
  `78208adf610a50542be6dfbd03a9b25960ba0b5cfc80768b08ffe7a4c78f3b8c`.
- `screening_metadata_exclusions.csv` SHA-256:
  `7fe72f7aedfe8c4538a1ac984903269d2c3bebebc6d0940e44aeb797554212c7`.

The controlling benchmark files remained:

- `PROTOCOL.md` SHA-256:
  `34e014a07821dc9dca52178874eef0b847aee7f048071fb4920864ae5d3bee93`;
- `RUN_SPEC_V1.md` SHA-256:
  `29ab6f78739d0eeea1c2a774e62e2d133f173e160c3d247407970a80726f4406`.

## Prohibited observations and actions

No `bug_patch.txt` content, official repair patch, buggy-to-fixed source diff,
repair-revealing subject commit message, or human fix explanation was read or
persisted. No subject repository was cloned or checked out. No dependency was
installed, no eligibility oracle was run, no ErrPilot or repair agent was invoked,
and no model/API request was made.

The presence of fixed revision identifiers in the census is identity metadata only.
It does not establish eligibility and does not authorize inspection of fixed content.

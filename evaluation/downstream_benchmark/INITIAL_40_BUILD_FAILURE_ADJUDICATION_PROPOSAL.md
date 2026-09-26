# Initial-40 build-failure adjudication proposal

Status: `INITIAL_40_BUILD_FAILURE_ADJUDICATION_PROPOSAL_READY_FOR_HUMAN_PI` (proposal only, **not accepted or frozen**). Date: 2026-09-25. **MATERIALIZED != ELIGIBLE.** No build, retry, subject test, oracle, eligibility run, repair, model/API call, candidate expansion, exclusion, commit, or push is part of this transaction.

## A. Entry and authority

The repository root was `/Users/wuyangchenxi/errpilot`; branch `main`, local `HEAD`, live `origin/main`, and local tracking `origin/main` were all `93e173172e88ecca0f4222a21893dd8f6ed217c6`. Ahead/behind was `0/0`; worktree and index were clean before the two proposal files were written. No `.airos/current_state.md` or repository Research Contract was present. The controlling SHA-256 values matched the frozen build specification and Batch-04 report: `PROTOCOL.md` `34e014a07821dc9dca52178874eef0b847aee7f048071fb4920864ae5d3bee93`, `RUN_SPEC_V1.md` `29ab6f78739d0eeea1c2a774e62e2d133f173e160c3d247407970a80726f4406`, and `environment_build_recipes.csv` `2addaf1830e61350e46583ec27b1403b43ffb0f8475b48e4bfc7d62b068b663e`. `SCREENING_SPEC_V1.md`, all four ledgers and reports, and the Batch-01 identity-completion supplement were tracked and clean against `HEAD`; their current SHA-256 values are recorded by the transaction's verification output, not changed here.

Authority is the Human-PI request for a read-only evidence adjudication and two local proposal artifacts. The existing protocol, run specification, screening specification, and frozen environment build specification remain controlling. This document does not amend them or classify any case as excluded or eligible.

## B. Reconciliation and evidence method

The four batch ledgers contain exactly 54 required identities for 40 frozen cases. Applying the Batch-01 `keras::28` identity-completion supplement yields 25 `MATERIALIZED`, 29 `BUILD_FAILED`, and zero unresolved identities. At case level, 19 have every required identity materialized and 21 lack a complete environment because of a build failure. The companion CSV contains those 21 cases exactly once; no environment-ready case appears in it. All 29 failed `build.log` bytes matched their ledger SHA-256, and each had an `attempt.json` with the ledger's attempt ID. For the eight failed revision-specific cases, BUGGY and FIXED each failed under the same observed immediate cause. This establishes matching *first blockers* only; later build stages did not run.

Evidence was limited to the frozen recipes, dependency-only inputs, setup-action records, the four batch ledgers/reports, the Batch-01 supplement, and preserved raw failed-build logs under `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_0[1-4]/`. Per-identity paths and log hashes are in the CSV. `bug_patch.txt`, buggy/fixed diffs, repair-revealing history, fix explanations, and oracle outcomes were not inspected. A `No matching distribution` log proves unavailability from the source and resolver used in that attempt; it does **not** prove that the version never existed elsewhere. An unexecuted later action is an unknown blocker, not an observed second failure.

## C. Case-level proposals

| Order | Case | Failed identities | First observed cause | Failure family | Proposal |
| ---: | --- | ---: | --- | --- | --- |
| 5 | `scrapy::4` | 1 | `pywin32==227` on `linux/amd64` | `FROZEN_PLATFORM_INCOMPATIBLE_DEPENDENCY` | `EXCLUDE_UNSUPPORTED_ENVIRONMENT` |
| 6 | `keras::9` | 1 | `numpy==1.19.0rc2` unavailable | `FROZEN_ARTIFACT_UNAVAILABLE` | `EXCLUDE_DEPENDENCY_SETUP_FAILURE` |
| 8 | `keras::18` | 1 | same exact NumPy pin unavailable | `FROZEN_ARTIFACT_UNAVAILABLE` | `EXCLUDE_DEPENDENCY_SETUP_FAILURE` |
| 11 | `luigi::31` | 1 | `mysql-connector-python==8.0.20` unavailable | `FROZEN_ARTIFACT_UNAVAILABLE` | `EXCLUDE_DEPENDENCY_SETUP_FAILURE` |
| 13 | `scrapy::19` | 1 | `pywin32==227` on `linux/amd64` | `FROZEN_PLATFORM_INCOMPATIBLE_DEPENDENCY` | `EXCLUDE_UNSUPPORTED_ENVIRONMENT` |
| 14 | `scrapy::15` | 1 | same exact pywin32 pin | `FROZEN_PLATFORM_INCOMPATIBLE_DEPENDENCY` | `EXCLUDE_UNSUPPORTED_ENVIRONMENT` |
| 15 | `keras::15` | 1 | same exact NumPy pin | `FROZEN_ARTIFACT_UNAVAILABLE` | `EXCLUDE_DEPENDENCY_SETUP_FAILURE` |
| 17 | `scrapy::14` | 1 | same exact pywin32 pin | `FROZEN_PLATFORM_INCOMPATIBLE_DEPENDENCY` | `EXCLUDE_UNSUPPORTED_ENVIRONMENT` |
| 18 | `thefuck::9` | 1 | base pip 18.1 `TomlError` on transitive `cryptography` source metadata | `HISTORICAL_BUILD_TOOLCHAIN_DRIFT` | `NEEDS_HUMAN_PI_ADJUDICATION` |
| 20 | `ansible::15` | 2 | BUGGY/FIXED: `ansible-base==2.10.0.dev0` unavailable | `FROZEN_ARTIFACT_UNAVAILABLE` | `EXCLUDE_DEPENDENCY_SETUP_FAILURE` |
| 21 | `tornado::6` | 1 | frozen setup action `pip install unittest` has no distribution | `FROZEN_ARTIFACT_UNAVAILABLE` | `EXCLUDE_DEPENDENCY_SETUP_FAILURE` |
| 22 | `luigi::4` | 1 | `pywin32==227` on `linux/amd64` | `FROZEN_PLATFORM_INCOMPATIBLE_DEPENDENCY` | `EXCLUDE_UNSUPPORTED_ENVIRONMENT` |
| 26 | `spacy::4` | 2 | BUGGY/FIXED: source Cython compile rejects `cpdef readonly` | `SUBJECT_SOURCE_BUILD_FAILURE` | `NEEDS_HUMAN_PI_ADJUDICATION` |
| 27 | `ansible::2` | 2 | BUGGY/FIXED: same exact `ansible-base` pin | `FROZEN_ARTIFACT_UNAVAILABLE` | `EXCLUDE_DEPENDENCY_SETUP_FAILURE` |
| 28 | `sanic::1` | 2 | BUGGY/FIXED: `pywin32==227` on `linux/amd64` | `FROZEN_PLATFORM_INCOMPATIBLE_DEPENDENCY` | `EXCLUDE_UNSUPPORTED_ENVIRONMENT` |
| 29 | `thefuck::26` | 1 | same pip 18.1 `TomlError` | `HISTORICAL_BUILD_TOOLCHAIN_DRIFT` | `NEEDS_HUMAN_PI_ADJUDICATION` |
| 30 | `thefuck::28` | 1 | same pip 18.1 `TomlError` | `HISTORICAL_BUILD_TOOLCHAIN_DRIFT` | `NEEDS_HUMAN_PI_ADJUDICATION` |
| 32 | `ansible::4` | 2 | BUGGY/FIXED: same exact `ansible-base` pin | `FROZEN_ARTIFACT_UNAVAILABLE` | `EXCLUDE_DEPENDENCY_SETUP_FAILURE` |
| 34 | `spacy::1` | 2 | BUGGY/FIXED: transitive build isolation requests `cython>=3.1`, unavailable on Python 3.7.7 | `HISTORICAL_BUILD_TOOLCHAIN_DRIFT` | `EXCLUDE_DEPENDENCY_SETUP_FAILURE` |
| 37 | `tqdm::3` | 2 | BUGGY/FIXED: `pkg-resources==0.0.0` unavailable | `FROZEN_ARTIFACT_UNAVAILABLE` | `EXCLUDE_DEPENDENCY_SETUP_FAILURE` |
| 39 | `ansible::16` | 2 | BUGGY/FIXED: same exact `ansible-base` pin | `FROZEN_ARTIFACT_UNAVAILABLE` | `EXCLUDE_DEPENDENCY_SETUP_FAILURE` |

`luigi::31` also has `pywin32==227` in its frozen dependency-only input. Its build stopped at the MySQL pin, so the pywin32 issue is a **latent, unobserved** blocker in this case. It is not counted as a second observed cause. The two spaCy cases are distinct: `spacy::4` completed dependency installation and failed while compiling its own source with observed Cython 3.2.9; `spacy::1` stopped earlier in a transitive dependency's isolated build, before subject source compilation. Neither is labeled a benchmark infrastructure defect. The already corrected Python metadata probe and symlink representation leave no unresolved failed case here.

## D. Aggregates and systemic findings

| Failure family | Cases |
| --- | ---: |
| `FROZEN_PLATFORM_INCOMPATIBLE_DEPENDENCY` | 6 |
| `FROZEN_ARTIFACT_UNAVAILABLE` | 10 |
| `HISTORICAL_BUILD_TOOLCHAIN_DRIFT` | 4 |
| `SUBJECT_SOURCE_BUILD_FAILURE` | 1 |
| `BENCHMARK_INFRASTRUCTURE_DEFECT`, `MULTIPLE_CAUSES`, `AMBIGUOUS_REQUIRES_PI` | 0 |
| **Total** | **21** |

| Proposed disposition | Cases |
| --- | ---: |
| `RETRY_CANDIDATE_SYSTEMIC_AMENDMENT` | 0 |
| `EXCLUDE_DEPENDENCY_SETUP_FAILURE` | 11 |
| `EXCLUDE_UNSUPPORTED_ENVIRONMENT` | 6 |
| `NEEDS_HUMAN_PI_ADJUDICATION` | 4 |
| **Total** | **21** |

| Repeated symptom group | Cases | Systemic retry rule proposed | Potentially recoverable under a proposed rule |
| --- | ---: | --- | ---: |
| Frozen `pywin32==227` on Linux | 6 | None; removal/marker or platform change alters the frozen declaration/platform | 0 |
| Frozen `numpy==1.19.0rc2` unavailable | 3 | None; no verified exact artifact source | 0 |
| Frozen `ansible-base==2.10.0.dev0` unavailable | 4 | None; no verified exact artifact source | 0 |
| Frozen `mysql-connector-python==8.0.20` unavailable | 1 | None; case also contains latent pywin32 pin | 0 |
| Frozen `pip install unittest` | 1 | None; changing this setup action changes a frozen input | 0 |
| Frozen `pkg-resources==0.0.0` unavailable | 1 | None; removing a declaration changes a frozen input | 0 |
| Base pip 18.1 / `cryptography` TOML parse | 3 | None; no exact, evidenced replacement toolchain is specified | 0 |
| `spacy::4` source Cython compile | 1 | None; no proven general version rule, and source-vs-toolchain effects are unresolved | 0 |
| `spacy::1` transitive Cython/Python conflict | 1 | None; transitive resolution or Python identity would change | 0 |
| **Total** | **21** | **0 rule IDs** | **0** |

Repeated errors are systematic *observations*, not automatically valid systemic amendments. No candidate rule here satisfies all required conditions: a mechanically fixed trigger, an exact transformation grounded in preserved evidence, full initial-40/prospective-expansion applicability, and demonstrated compatibility with the frozen benchmark semantics. Accordingly every CSV `proposed_systemic_rule_id` is `NA`. There is no before-retry rule to enact. Any future proposed rule must be specified and versioned **before** a separately authorized retry; original first-pass evidence remains immutable. This proposal does not use desired oracle or repair outcomes.

## E. Recovery-change and protocol-compatibility analysis

The CSV records the exact *types of change that could make a new attempt different*, not permission to make them and not proof they would succeed. `|` separates possible alternative changes; it does not imply all are jointly required. The direct responses are:

- **Platform pin cases (6):** install the Windows-only package by changing the frozen Linux platform/Python identity, or omit/marker-gate that declared dependency. A platform switch conflicts with the frozen `linux/amd64` benchmark identity; dependency membership change requires a new general methodology and frozen-input amendment. Neither is an observational materializer correction.
- **Exact unavailable pins (NumPy 3, Ansible 4, MySQL 1):** an independently identified immutable source for the *same* artifact might preserve the exact version, but none is in the evidence. Substituting a version changes a frozen dependency. `luigi::31` has a further latent pywin32 constraint. The CSV marks compatibility `AMBIGUOUS_REQUIRES_PI` because source-only and version-changing routes have different methodological effects.
- **Frozen setup/declaration failures (`tornado::6`, `tqdm::3`):** omitting `pip install unittest` or `pkg-resources==0.0.0` changes frozen membership/action bytes. Those are substantive input amendments, not infrastructure defect fixes. The present proposal favors dependency/setup failure exclusion.
- **`thefuck` trio:** pip 18.1 parsed a downloaded `cryptography-45.0.7` source `pyproject.toml` and raised `TomlError`. A pinned build-tool change *might* avoid that parser failure, or a dependency constraint might change the selected cryptography artifact. Neither exact version nor subsequent build success is supported by the frozen evidence. An alternative package source alone does not establish a compatible artifact. A general rule, if ever proposed, would need to apply to all initial-40 and future cases meeting an objective toolchain trigger, including successful cases if they meet it, and would need a versioned build recipe/toolchain identity and a prospective expansion rule.
- **`spacy::4`:** observed Cython 3.2.9 accepted the unbounded `cython>=0.25` declaration but rejected a `cpdef readonly` source declaration in both revisions. A different Cython pin changes the resolved build dependency/toolchain; source edits change subject build logic. Neither is an observation-only correction. Whether a general, prospective Cython rule can preserve the benchmark meaning is unresolved.
- **`spacy::1`:** a transitive `murmurhash` build selected by the frozen constraints requested `cython>=3.1` in isolation; that had no matching distribution for frozen Python 3.7.7. Constraining transitive versions or changing Python/platform would alter the environment identity. The latter conflicts with the frozen runtime; the former needs an amended dependency-resolution policy and new identity.

`COMPATIBLE_WITH_EXISTING_AUTHORITY_IF_SEPARATELY_AUTHORIZED` is assigned to no proposed recovery. Separate permission alone cannot legalize a silent change to a frozen recipe. `REQUIRES_PROTOCOL_AMENDMENT` means at least a Human-PI approved, versioned normative change to the affected environment specification/recipe and, where `RUN_SPEC_V1.md` section Q applies to semantic identity or eligibility, a new run-spec/protocol version and revalidation. `AMBIGUOUS_REQUIRES_PI` means the available evidence does not select a unique source/toolchain/version route. None of these labels authorizes a build.

## F. The 28-case requirement and expansion consequence

`PROTOCOL.md` requires 24 final eligible cases and four permanently separate pilot cases. Thus **at least 28 eligible cases** are needed before allocation, subject also to the six-project and four-final-cases-per-project limits. Only 19 initial cases currently have complete environments, and even those are **not yet eligible**. With zero failed cases recovered, the initial set can contribute at most 19 eligible cases, so expansion is mathematically unavoidable once the frozen screening rule is applied. With all **proposed** systemic retry candidates recovered, the count is still 19 because this proposal has no qualifying systemic retry rule. With partial recovery of `r` failed cases, the environment-ready ceiling is `19 + r`: expansion is unavoidable for `r <= 8`; for `r >= 9`, the count alone no longer proves expansion necessary, but 3/3 eligibility and project allocation can still require it. Even recovery of all 21 would establish at most 40 environment-ready cases, not 28 eligible cases. No expansion or selection of a next block is authorized here.

## G. Questions for the Human PI

1. Accept, revise, or reject each proposed exclusion or `NEEDS_HUMAN_PI_ADJUDICATION` row; no disposition is enacted by this file.
2. For unavailable exact pins, is there a provenance-verified immutable artifact source for the *same bytes/version*, and what versioned source policy would govern **every** matching case? If none, are the proposed dependency/setup exclusions accepted?
3. Is a prospective, exact pip/toolchain rule justified for all cases with the same mechanical trigger (including any already materialized cases), and which pinned tool version and normative artifact would it amend? No version has been selected here.
4. Is a general source-build/Cython policy possible for the two distinct spaCy failures without case-specific rescue or changing frozen subject source? If not, should `spacy::4` move from PI adjudication to a documented exclusion?
5. Should the six platform-incompatible cases be excluded under the frozen `linux/amd64` identity, and should `luigi::31`'s latent pywin32 declaration affect its final adjudication?
6. After adjudication and separately authorized eligibility screening, apply `SCREENING_SPEC_V1.md` section M exactly if the completed initial-40 eligible pool cannot support the required final and pilot allocations. No next ten are selected here.

The companion CSV is an adjudication proposal, not `cases_manifest.csv` or `exclusions.csv`. Historical batch evidence and failed attempts remain unchanged.

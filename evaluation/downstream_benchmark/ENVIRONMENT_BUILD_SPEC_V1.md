# BugsInPy environment build recipes v1

- Status: `ENVIRONMENT_BUILD_RECIPES_V1_FROZEN`.
- Authority: Human PI environment-input normalization and build-recipe transaction, 2026-09-22.
- Scope: the frozen initial 40, in their existing selection order, for both frozen source revisions.
- Controlling identities: `PROTOCOL.md` SHA-256 `34e014a07821dc9dca52178874eef0b847aee7f048071fb4920864ae5d3bee93`; `RUN_SPEC_V1.md` SHA-256 `29ab6f78739d0eeea1c2a774e62e2d133f173e160c3d247407970a80726f4406`; pinned BugsInPy commit `11c5f1eea954a42132cfd06bf257766a7963e0fd`, tree `d00ce0495ba73abe50317599f48bced3c9afe4b3`.

## A. Authority and execution boundary

This supplement freezes data-only construction recipes. It does not amend candidate membership, oracle membership/order, eligibility rules, or the frozen timeout values. No subject dependency installation, setup execution, project build/install, subject import, subject test, oracle, pilot, repair, ErrPilot run, or model/API invocation is authorized here. A recipe status describes **readiness to attempt a future build**, not a materialized environment or a screening outcome. `cases_manifest.csv` and `exclusions.csv` remain header-only. The existing execution gate remains closed.

## B. Exact base-runtime probe

For each of seven declared patch versions, `runtime_base_images.csv` fixes the official `docker.io/library/python` `linux/amd64` image digest. Pull by that digest and platform, then run only a container with no subject mount, network disabled, and `python -c` that reports `sys.version`, the exact `major.minor.micro`, `platform.machine()`, `sys.executable`, and SHA-256 of the executable's bytes. Store the multiline `sys.version` as a JSON-escaped CSV field. Record exit code and SHA-256 of exact stdout and stderr bytes. Accept only exit code zero, exact declared patch version, `x86_64`, an absolute executable path, and a nonempty 64-character executable SHA-256. The previously recorded digest and source reference must not be replaced on contradiction. A failed probe blocks all affected cases. Nearby patch versions and native macOS are not substitutes.

## C. Requirements normalization

Read exact raw `requirements.txt` bytes from the pinned BugsInPy checkout and verify their frozen raw hash. Keep those bytes untouched. Detect UTF-16 only from a valid LE or BE BOM; decode that with strict BOM-directed UTF-16. Otherwise decode strict UTF-8. Any decode error blocks the case; replacement characters are never used. In decoded text, replace CRLF with LF and bare CR with LF. Preserve all other characters, line order, comments, blank lines, whitespace, and presence or absence of the final line terminator. Do not interpret markers or resolve dependencies. Encode UTF-8 without BOM. Run normalization twice and require byte-identical output. Record raw and normalized SHA-256 in `requirements_normalization.csv`; the actual derived bytes are in `derived_inputs/<project>__<bug_id>/requirements.normalized.txt`.

## D. Self-reference source selection

The BUGGY workspace always uses the frozen buggy SHA and the FIXED workspace always uses the frozen fixed SHA from `screening_execution_plan.csv`. A requirement is a subject self-reference only when its distribution name exactly equals the frozen project name after standard `[-_.]` normalization, or when both its VCS repository and egg name match the frozen project source URL and name. An apparent match that cannot be established mechanically blocks the case. In particular, similarly named packages remain dependencies. The same transformation applies to BUGGY and FIXED; the only permitted source distinction is their frozen revision SHA. This rule resolves the prior `SELF_VCS_REQUIREMENT_REVISION_RULE_REQUIRED` and `SELF_PACKAGE_PIN_SOURCE_SELECTION_UNRESOLVED` questions without changing historical raw evidence.

## E. Dependency-only input and ledger

From normalized text, remove the complete lines of only proven self-references. Preserve every other line byte-for-byte from the normalized form. Record each removal in `self_reference_ledger.csv` with case ID, one-based original line ordinal, exact line text, `SELF_PACKAGE_PIN` or `SELF_VCS_REFERENCE`, proof, and SHA-256 of the UTF-8 line text without its terminator. Hash the canonical JSON list of each case's removal entries, including `[]` for no removals. Record the derived input hash and materialize `derived_inputs/<project>__<bug_id>/requirements.dependencies.txt`. The source project is supplied separately from its exact frozen workspace. A self-reference omitted from dependencies must never import or install the opposite revision.

## F. Setup representation and order

Read `setup.sh` as inert strict UTF-8 text; never run it. Skip comments and blank lines as nonactions. Reclassify each substantive line and compare ordinal, exact text, and category with the frozen audit ledger. Every action records one-based source line ordinal, exact text, category, whether it consumes subject source, requires network, mutates the source workspace, dependency-input binding, and future phase. Allowed categories are `DEPENDENCY_INSTALL`, `PROJECT_INSTALL_OR_BUILD`, `ENVIRONMENT_CONFIGURATION`, and `FILESYSTEM_PREPARATION`. Discovery of `TEST_INVOCATION`, `NETWORK_OR_EXTERNAL_SERVICE`, or `UNSUPPORTED_OR_AMBIGUOUS` blocks that case. A setup line explicitly installing `-r requirements.txt` is bound to the derived dependency-only input in the future controlled builder, while its original text and place in setup order remain evidence. No setup line executes in this transaction.

## G. Controlled future build sequence

Phase 1 materializes the exact base runtime. Phase 2 installs the dependency-only requirements once. Phase 3 schedules the substantive setup actions in original ordinal order. Phase 4 is the source-consuming project build/install action at its original position within that scheduler; it does not sort project actions to the end or duplicate them. Phase 5 records the resulting environment identity. Explicit dependency-install setup actions remain in their original order even when their packages overlap Phase 2. The historical second automatic requirements install in `bugsinpy-compile` is excluded. A future builder must preserve action order and record all inputs and outputs; this specification authorizes no build.

## H. Environment mode v2

`SOURCE_INDEPENDENT_ENVIRONMENT` means the dependency/runtime layer can be built without consuming subject source; the frozen source is supplied as the future fresh execution workspace, with recorded cwd and Python path semantics. `REVISION_SPECIFIC_BUILD_REQUIRED` means an allowed setup action consumes, builds, installs, or mutates that exact source revision. `UNRESOLVED` means required semantics remain unsupported or nonunique. Self-reference omission alone does not force revision-specific mode. This rule supersedes only the older self-reference-related mode classification in `SCREENING_RUNTIME_V1.md`; it does not weaken any other requirement.

## I. Recipe identity

Each row of `environment_build_recipes.csv` contains the complete canonical JSON recipe and its SHA-256. Canonical JSON is UTF-8, keys sorted, compact separators, Unicode preserved, and one LF terminator for hashing. The recipe binds case/order, both frozen source SHAs, declared Python patch version, immutable `linux/amd64` image digest, observed patch version and executable hash, raw/normalized/dependency-only requirements hashes, removal ledger hash, raw setup hash or `ABSENT`, ordered setup actions and ledger hash, Python path metadata, environment mode, system-package status, future network policies, committed execution-plan row hash, `SCREENING_RUNTIME_V1.md` hash, and schema `ENVIRONMENT_BUILD_RECIPE_V1`. Timestamps are excluded from the recipe hash. `materialization_identity` is `UNBUILT`; no image/rootfs, installed-distribution, or environment artifact identity is fabricated.

## J. Network policy

Future **build** network use requires separate Human PI authority, exact source/artifact identification, and recorded immutable hashes. The policy value is `DECLARED_DEPENDENCY_SOURCES_ONLY_SEPARATE_AUTHORITY_REQUIRED`. Future **execution** network policy is `NONE`, mechanically enforced at each trial. Pulls and identity probes in this transaction are limited to the seven recorded base images. A networked build never authorizes networked execution.

## K. System dependencies

Record an explicit system-package declaration only when statically present in frozen inputs. Otherwise record `UNKNOWN`; absence of an explicit declaration is not proof that none will be needed. No `apt` or other subject system dependency installation, build failure experiment, or inferred package repair is part of this transaction.

## L. Readiness and blockers

`BUILD_RECIPE_READY` requires an exact successful base probe, resolved normalization, mechanically proven self-reference transformation, resolved ordered setup representation, unique environment mode, and deterministic recipe hash. Any missing item yields `BUILD_RECIPE_BLOCKED` and an explicit reason. Readiness does not imply that packages can be installed or that a build will succeed. `UNBUILT` continues to apply to every environment identity.

## M. Fix-leakage boundary

The recipe contains the two already-frozen full source SHAs solely to identify future workspaces. No patch file, fixed-vs-buggy diff, repair-revealing history, test outcome, or protected oracle result is used. BUGGY and FIXED transformations are algorithmically identical and cannot select the BUGGY self dependency for FIXED. Future execution must use fresh, isolated workspaces; screening images and evidence must never be handed to a repair agent.

## N. Future authority

A separate Human PI transaction must authorize materialization and a controlled builder before any subject dependency install, setup action, or project build. A later separate transaction must authorize real 3/3 oracle execution. Neither a ready recipe nor an execution token by itself grants either authority.

## Frozen v1 audit result

The seven recorded `linux/amd64` base-image probes passed with their exact declared patch versions and `x86_64` observations. All 40 raw requirements inputs normalize twice to identical bytes: 28 UTF-8 and 12 UTF-16 with BOM. The self-reference ledger contains 25 proven omissions across the 40 cases: 11 VCS and 14 package pins. All other normalized dependency lines remain in their original order and text. The 40 recipes are `BUILD_RECIPE_READY`, with 26 `SOURCE_INDEPENDENT_ENVIRONMENT` and 14 `REVISION_SPECIFIC_BUILD_REQUIRED`; none is `UNRESOLVED`. These are data-only readiness classifications. All 40 materialization identities remain `UNBUILT`.

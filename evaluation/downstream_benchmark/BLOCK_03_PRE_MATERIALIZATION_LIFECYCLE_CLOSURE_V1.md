# Block-03 pre-materialization lifecycle closure V1

Transaction: `BLOCK_03_PRE_MATERIALIZATION_LIFECYCLE_CLOSURE`.
Baseline identity: `BLOCK_03_PRE_MATERIALIZATION_RUNTIME_BASELINE_V1`.
Freeze declaration: `FROZEN`.

## Human-PI authority and accepted components

The Human PI's explicit closure instruction accepts the complete Block-03
preparation, PREPARATION_COMPATIBILITY_BRIDGE_V1, and
BLOCK_03_MATERIALIZER_AUTHORITY_BRIDGE_V1. It authorizes this closure record,
local persistence of the exact accepted artifacts, explicit staging of the
inventory below, exactly one local commit, and post-commit read-only verification.

```text
BLOCK_03_PREPARATION = HUMAN_PI_ACCEPTED
PREPARATION_COMPATIBILITY_BRIDGE_V1 = HUMAN_PI_ACCEPTED
MATERIALIZER_AUTHORITY_BRIDGE_V1 = HUMAN_PI_ACCEPTED
```

The original preparation report records historical 5 PREPARED / 2 blocker.
The accepted compatibility bridge records the final 7 PREPARED / 0 blocker.
Both historical reports and all accepted implementation/input artifacts retain
exact accepted bytes. This record supplies the current lifecycle declaration;
it does not rewrite historical report statuses or the accepted input authority's
serialized `bridge_lifecycle=CANDIDATE_ONLY` field, which remains part of the
accepted hash-bound validator contract. Human-PI acceptance and baseline freeze
are distinct from runtime execution authority and scientific outcomes.

## Entry gate and expected enclosing commit

Canonical cwd/root: `/Users/wuyangchenxi/errpilot`; branch: `main`.
Expected parent: `7b612f96a6715bb8b109d1152b2b1ac5e4b1bcf7`.
Configured origin: `https://github.com/YangchenxiWu/errpilot.git`.
Entry: exactly 35 attributable untracked files, the sole tracked modification
`evaluation/downstream_benchmark/screening/materializer.py`, and no staged diff.
Entry index SHA-256:
`9bf7f257264382f687c2b58e46747825685774cc5c633e69a00211ecbb2cd9c4`.
All 416 other tracked files match parent bytes and prior accepted disk mode/type.
All 209 original Block-01/02/03 external preparation files remain unchanged.
No repository-local AGENTS.md or `.airos/current_state.md`/contract was present.

The enclosing closure commit identity will be established by Git after this
record is written and staged. Its exact authorized message is:

```text
benchmark: freeze Block-03 pre-materialization baseline
```

No closure commit SHA is embedded in its own contents. The inventory excludes
this record's own SHA-256 explicitly, avoiding self-referential hashing. Git
binds this record and all 36 other inventory files in the enclosing tree.
No separate repository manifest or persistent run report is added.
The final chat Run Report supplies the actual commit identity and the record's
post-write SHA-256, without changing committed bytes.

## Controlling identities

Pinned BugsInPy commit: `11c5f1eea954a42132cfd06bf257766a7963e0fd`.
Pinned BugsInPy tree: `d00ce0495ba73abe50317599f48bced3c9afe4b3`.
Sampling seed: `20260922`.
Candidate universe SHA-256:
`78208adf610a50542be6dfbd03a9b25960ba0b5cfc80768b08ffe7a4c78f3b8c`.
Canonical Block-03 identity SHA-256:
`883628cb72d4ddf56fdfd4a28c4b3c0752b429acf1b6c0abe382bbf7d666e780`.

The inventory below binds all three accepted reports, the input authority,
materializer, both adapters, preparation controller, tests, ledgers, derived
inputs, and accepted compatibility evidence to exact final accepted hashes.
Additional inherited controls remain in the expected parent and enclosing tree;
they are read-only inputs, excluded from the changed-path inventory:

| Inherited control relative to `evaluation/downstream_benchmark/` | SHA-256 |
| --- | --- |
| `EXPANSION_BLOCK_01_PREPARATION_V1.md` | `c951cb1993a9dfb5b3ec3598c570d86cfb949022cd0a2e1cebb9e407a9ed3533` |
| `EXPANSION_BLOCK_02_PREPARATION_V1.md` | `82c3fe89c9bf954502eeaa9b134a9c95371e4d815546af0cc83d3df3bee797c8` |
| `EXPANSION_BLOCK_03.md` | `46929b793f456ab18a7d55c425727bb65978c9758f4bec23fb2e1d56d642776b` |
| `EXPANSION_BLOCK_03_TRIGGER_V1.md` | `9106a9475da1231577b68fdf7ab92087c537a97e709a8c096a4a2833789330e2` |
| `ORACLE_REPRESENTATION_V1.md` | `625b656495b5f1174ea1f4a07f872a42112a0be839b47c3db884dcd103a87f52` |
| `PRE_ELIGIBILITY_EXCLUSIONS_LEDGER_STATE_V4.md` | `540572c9f81385bd425ebe4c69e31b7a049614ef7be8b76bd0909b8e9b754e6a` |
| `PROTOCOL.md` | `34e014a07821dc9dca52178874eef0b847aee7f048071fb4920864ae5d3bee93` |
| `RUN_SPEC_V1.md` | `29ab6f78739d0eeea1c2a774e62e2d133f173e160c3d247407970a80726f4406` |
| `SCREENING_RUNTIME_V1.md` | `235b404dd32da91f28c303922ce7acfc8f58611cd78f3c365d583cb2572bb41f` |
| `SCREENING_SPEC_V1.md` | `a7f3cd5e73d6c733f560456d9f3949be18deca9b295ffb4ef2ae087af7e89db3` |
| `SECTION_M_TERMINAL_EXHAUSTION_ADJUDICATION_V1.md` | `bd3d95f56d9aa6332363216b04b91123ac4c0a284076b26504efb399e1daf059` |
| `candidate_universe.csv` | `78208adf610a50542be6dfbd03a9b25960ba0b5cfc80768b08ffe7a4c78f3b8c` |
| `cases_manifest.csv` | `c7d423696616ffb7d5dc79fa5bf56294044b3d66c247c744d575617dbb89dac9` |
| `environment_build_recipes.csv` | `2addaf1830e61350e46583ec27b1403b43ffb0f8475b48e4bfc7d62b068b663e` |
| `environment_requirements.csv` | `9607c48fb02ba0b5a77be01dc2201e0d3eec7b83ea1ff4e13925b8068353e912` |
| `exclusions.csv` | `e13187b561745222873f6533d7883556b786fcab7f455b5035e664f558654f45` |
| `expansion_block_02.csv` | `b1d4cc0a8c863535ef881d4c25b4ddd469ab5925cedc36a6e5783c20d01cd6a7` |
| `expansion_block_02_traversal.csv` | `985de4e8e751400144c5143f0eb7e581b6bcf3e122dd8314592f0f5714acddc9` |
| `expansion_block_03.csv` | `50231362538d477ab262a783da904b51552652dd490267c1c4c84a59db3fcc8b` |
| `expansion_block_03_traversal.csv` | `ac46a4c73bdef279d615f2eaf706598f2f64e24c68e78b6625b8178307e25968` |
| `requirements_normalization.csv` | `86d67df884cf5d46c2e5421bfe477cd3b8c632ba444230f07370f1e415a2af81` |
| `runtime_base_images.csv` | `abbbe6aef3fafcc5ad62bcb67274ad392f1b3d31d04dc009251f0150495f9e1f` |
| `screening/audit_environment.py` | `b7694e6d798fa1911d6e04a0135e70ab8ce629b75066b7a628bd0f8350a1c5fb` |
| `screening/build_recipes.py` | `96fd5f432474c76c25aaccc5cce5ac588d76cdaace269a7b9c7fd9356c3b2aba` |
| `screening/executor.py` | `e16a4e71880ac08e607b2ce43519d7565482c3d3c358ae18c187230a45f5d305` |
| `screening/prepare_expansion_block_02.py` | `9065bfb89973e8e706e0bb70541e14598f765b06b9127409e2c353d544493c0c` |
| `screening_execution_plan.csv` | `95874a88a7ad54a976ef70db1e4cebc2fe8f9be7f72c7551ce8c00dfa17d25ea` |
| `self_reference_ledger.csv` | `8fefc975111f6ab60db2175c39d6ff8c9b2e7027eb1de7b90209143f24bc615d` |

The input authority additionally binds the exact 56 original external Block-03
evidence files at
`/Users/wuyangchenxi/errpilot-benchmark-work/expansion_block_03_preparation/`.
They were hash-verified but are not committed by this transaction. Original
Block-01/02 evidence and the four reused subject-mirror ref inventories are
preserved. No scratch file or external evidence path belongs to the commit set.

## Exact immutable membership and accepted preparation

| Candidate rank | Case | Accepted recipe SHA-256 |
| ---: | --- | --- |
| 259 | `tqdm::6` | `f285092228ac7f1a42a063e9f9cf8d4f1cbc99f22f6f99db2934084cb8637741` |
| 369 | `PySnooper::3` | `c6339567664f2a3d15f68faa461b970b35885a94fe6b1cd0c7fa775bb7cd35eb` |
| 380 | `sanic::3` | `0bf2cdac179ea42ae5533b43159c6c30fe51e79301d0b41c50d95e5d09c0303e` |
| 405 | `sanic::5` | `4b8d920d4da8d52429d650d02f8522987bc1d141d1386b5bfe94ab9880959a23` |
| 431 | `PySnooper::2` | `4b881349a551ead87f940c31789ecbab6f97904a5a223fe25560bf87af5ffe5f` |
| 472 | `cookiecutter::2` | `950e2a16b56d137ec5ece6adb1961b2a810e0c01884aae1425770adb055aa795` |
| 485 | `cookiecutter::1` | `3dcd36c4f7bc6db5762e2ba009d8c566f7ec9f18d37d605510a6b1d5d5aa7272` |

```text
7 PREPARED
0 PREPARATION_BLOCKER
BLOCK_03_MATERIALIZER_INPUT_ACCEPTED
RUNTIME_STATE = NOT MATERIALIZED
ELIGIBILITY_STATE = NOT ESTABLISHED
```

Each recipe remains `UNBUILT`. The exact seven ordered cases, source revisions,
raw oracle/setup text and argv, namespaces, ranks, seed, cursor, cap, and prior
skip rules are unchanged. The two cookiecutter representations retain literal
tox selectors and `python setup.py develop`; neither is executed here.

## Exact commit inventory and byte attribution

The approved changed-path set is exactly 37 files: 35 pre-existing untracked
accepted files, one accepted tracked materializer modification, and this single
new lifecycle record. Attribution follows the accepted reports' final inventories.
The four compatibility-modified prior files use their explicitly accepted final
byte identities. No unrelated/historical unchanged path is staged.

| Repository-relative path | Accepted transaction / ownership | Final accepted SHA-256 |
| --- | --- | --- |
| `evaluation/downstream_benchmark/BLOCK_03_MATERIALIZER_AUTHORITY_BRIDGE_V1.md` | MATERIALIZER_AUTHORITY_BRIDGE_V1 | `ebfa53db42d84f0c3b41cd1c49a775343a64b9c72b6c68e1733bd9cf7d8bb65b` |
| `evaluation/downstream_benchmark/BLOCK_03_PREPARATION_COMPATIBILITY_BRIDGE_V1.md` | PREPARATION_COMPATIBILITY_BRIDGE_V1 | `8e7d2131e45df8207b8ebe042119da63ca58020fee3fbdd2db380cd1292ab194` |
| `evaluation/downstream_benchmark/BLOCK_03_PRE_MATERIALIZATION_LIFECYCLE_CLOSURE_V1.md` | THIS_LIFECYCLE_CLOSURE | SELF_HASH_EXCLUDED |
| `evaluation/downstream_benchmark/EXPANSION_BLOCK_03_PREPARATION_V1.md` | ORIGINAL_PREPARATION | `e797ff2ac48b4ac379fb15c25fe805ce1077a06b56a5603082aba48dbcbda829` |
| `evaluation/downstream_benchmark/block_03_materializer_input_authority_v1.json` | MATERIALIZER_AUTHORITY_BRIDGE_V1 | `8844f3b9a00e9c8a8d10c32112291d8f68ac883f5cc775425afbc559358b6a9e` |
| `evaluation/downstream_benchmark/derived_inputs/expansion_block_03/PySnooper__2/requirements.dependencies.txt` | ORIGINAL_PREPARATION | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `evaluation/downstream_benchmark/derived_inputs/expansion_block_03/PySnooper__2/requirements.normalized.txt` | ORIGINAL_PREPARATION | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `evaluation/downstream_benchmark/derived_inputs/expansion_block_03/PySnooper__3/requirements.dependencies.txt` | ORIGINAL_PREPARATION | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `evaluation/downstream_benchmark/derived_inputs/expansion_block_03/PySnooper__3/requirements.normalized.txt` | ORIGINAL_PREPARATION | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `evaluation/downstream_benchmark/derived_inputs/expansion_block_03/cookiecutter__1/requirements.dependencies.txt` | ORIGINAL_PREPARATION | `912c20a655df19ca7b4a37a17d8d0903ca5731ff2e537bb80f86f4456b2e6c06` |
| `evaluation/downstream_benchmark/derived_inputs/expansion_block_03/cookiecutter__1/requirements.normalized.txt` | ORIGINAL_PREPARATION | `b409989277d9e8b688314e1cdf1c7a9d560d403ce4b8de32bef7382ace51182f` |
| `evaluation/downstream_benchmark/derived_inputs/expansion_block_03/cookiecutter__2/requirements.dependencies.txt` | ORIGINAL_PREPARATION | `912c20a655df19ca7b4a37a17d8d0903ca5731ff2e537bb80f86f4456b2e6c06` |
| `evaluation/downstream_benchmark/derived_inputs/expansion_block_03/cookiecutter__2/requirements.normalized.txt` | ORIGINAL_PREPARATION | `86172d5a86e333c634803243dbc77c0ee5136709db67d4b336b3ddf9ddc42999` |
| `evaluation/downstream_benchmark/derived_inputs/expansion_block_03/sanic__3/requirements.dependencies.txt` | ORIGINAL_PREPARATION | `3129e6f687cdcdf0318e690170dcf5dc10892005a32cc863dfa4ed7bbfc18698` |
| `evaluation/downstream_benchmark/derived_inputs/expansion_block_03/sanic__3/requirements.normalized.txt` | ORIGINAL_PREPARATION | `cec425ea12c8f8c2b213cf132a18df36ec1f035db7c03478bed109e6ba7f813d` |
| `evaluation/downstream_benchmark/derived_inputs/expansion_block_03/sanic__5/requirements.dependencies.txt` | ORIGINAL_PREPARATION | `9aca8a4f848d7d8eac180b034d0c1f152be13d32942a13c5c35a9e6c79522c24` |
| `evaluation/downstream_benchmark/derived_inputs/expansion_block_03/sanic__5/requirements.normalized.txt` | ORIGINAL_PREPARATION | `55624dcc53174a46c31985863a75422085fc71201b916c7d8385929e9dcd203d` |
| `evaluation/downstream_benchmark/derived_inputs/expansion_block_03/tqdm__6/requirements.dependencies.txt` | ORIGINAL_PREPARATION | `f6b306808661d5e2b3cef1e372b5e91f253fc554ed43600aad50c26a9244ca74` |
| `evaluation/downstream_benchmark/derived_inputs/expansion_block_03/tqdm__6/requirements.normalized.txt` | ORIGINAL_PREPARATION | `351870f5066dc3de10d7b3b6ba01b8677d948fedc0d2165eb665a03b1426c22b` |
| `evaluation/downstream_benchmark/evidence/block_03_preparation_compatibility_bridge_v1/cookiecutter__1/environment_inputs.json` | PREPARATION_COMPATIBILITY_BRIDGE_V1 | `5a6328ea7947eb791f0da23cc5c48401d0fe19db5b789c0f07b853cf60a159ab` |
| `evaluation/downstream_benchmark/evidence/block_03_preparation_compatibility_bridge_v1/cookiecutter__1/oracle_representation.json` | PREPARATION_COMPATIBILITY_BRIDGE_V1 | `8a36b3472b16dba4dfdd7cc6517e6e4936683cc2a428853d18d88d9ee6c3853f` |
| `evaluation/downstream_benchmark/evidence/block_03_preparation_compatibility_bridge_v1/cookiecutter__1/preparation_plan.json` | PREPARATION_COMPATIBILITY_BRIDGE_V1 | `9a1bdb8708b466454c30357a4a11dec0aa043092f64f944da7fd3f02cc200b63` |
| `evaluation/downstream_benchmark/evidence/block_03_preparation_compatibility_bridge_v1/cookiecutter__2/environment_inputs.json` | PREPARATION_COMPATIBILITY_BRIDGE_V1 | `42cebdef33d85a2a75a67191e75aa786bdd2db0c2831f6a934d12f6e82bb205f` |
| `evaluation/downstream_benchmark/evidence/block_03_preparation_compatibility_bridge_v1/cookiecutter__2/oracle_representation.json` | PREPARATION_COMPATIBILITY_BRIDGE_V1 | `0918e8fa00cbc3dfb0a4d8647ed459d53cce2c767584d2952c9eff6442878a26` |
| `evaluation/downstream_benchmark/evidence/block_03_preparation_compatibility_bridge_v1/cookiecutter__2/preparation_plan.json` | PREPARATION_COMPATIBILITY_BRIDGE_V1 | `6b32ba4c5ba51347ce54eedf01bb4d5e102271ca28a0ff4daa8d860c8082f725` |
| `evaluation/downstream_benchmark/expansion_block_03_environment_build_recipes.csv` | ORIGINAL_PREPARATION; FINAL_BYTES_ACCEPTED_COMPATIBILITY_BRIDGE_V1 | `1c958036b76abc5152a6dfdcb3a82e0f509d54a53e788d53f7b099202b12f72b` |
| `evaluation/downstream_benchmark/expansion_block_03_environment_requirements.csv` | ORIGINAL_PREPARATION; FINAL_BYTES_ACCEPTED_COMPATIBILITY_BRIDGE_V1 | `843f707f414a393f5e98327c5759183057b0bfa3aaff60bb04af6716475bc4c2` |
| `evaluation/downstream_benchmark/expansion_block_03_execution_plan.csv` | ORIGINAL_PREPARATION; FINAL_BYTES_ACCEPTED_COMPATIBILITY_BRIDGE_V1 | `6a15f01c08cf68d1703eb06dfabb8a8c966100d31e6299a09241322c64240607` |
| `evaluation/downstream_benchmark/expansion_block_03_requirements_normalization.csv` | ORIGINAL_PREPARATION | `a693547e4d61311b3593cd670f177cfd9dee97ccf19872564b5a0ca30cf83c34` |
| `evaluation/downstream_benchmark/expansion_block_03_self_reference_ledger.csv` | ORIGINAL_PREPARATION | `e2b93b5a814db86c2297cccd4b4eab69a7a38eb9d602c407cad18a88a4c6c15e` |
| `evaluation/downstream_benchmark/screening/block_03_materializer_bridge.py` | MATERIALIZER_AUTHORITY_BRIDGE_V1 | `c6212e90ad92fb0be439426549f2f94e6a9790580c6615a2475b7fa95f4f73a5` |
| `evaluation/downstream_benchmark/screening/block_03_preparation_compatibility.py` | PREPARATION_COMPATIBILITY_BRIDGE_V1 | `475f67220bf16183af4154d126559b07f8cda06fb1a50822e020d056870383bf` |
| `evaluation/downstream_benchmark/screening/materializer.py` | MATERIALIZER_AUTHORITY_BRIDGE_V1 | `a2ae7b9595f78afa91763e3537f61bdb5fd114e71135e9ecbb130b8709c5896e` |
| `evaluation/downstream_benchmark/screening/prepare_expansion_block_03.py` | ORIGINAL_PREPARATION; FINAL_BYTES_ACCEPTED_COMPATIBILITY_BRIDGE_V1 | `bc3eb4885b0d2dc439953cc72d4ab1e210a5f08ac741e9d0f38b47c0c6f895aa` |
| `evaluation/downstream_benchmark/tests/test_block_03_materializer_bridge.py` | MATERIALIZER_AUTHORITY_BRIDGE_V1 | `f00c1e3e8051b25831c19c77a9336214db2bd6933134965218b5599fb4a8ff8f` |
| `evaluation/downstream_benchmark/tests/test_block_03_preparation_compatibility.py` | PREPARATION_COMPATIBILITY_BRIDGE_V1 | `b7c2483214c6e0e28fcdce427110be8510a99f851d3c6e242de4fb3be0fb5cb4` |
| `evaluation/downstream_benchmark/tests/test_expansion_block_03_preparation.py` | ORIGINAL_PREPARATION | `658f21877985169153885845a6add2ad38829dc5d16bce598259dc6c583d9413` |

## Bounded pre-commit validation

All required bounded validations passed before staging. Exact commands from
`/Users/wuyangchenxi/errpilot`:

```text
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/errpilot-block03-closure-v1-6_uq7cmc/verify_preparations.py
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/errpilot-block03-closure-v1-6_uq7cmc/run_guarded_tests.py
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/errpilot-block03-closure-v1-6_uq7cmc/dry_consumption.py
PYTHONDONTWRITEBYTECODE=1 python3 -m ruff check --no-cache evaluation/downstream_benchmark/screening/materializer.py evaluation/downstream_benchmark/screening/prepare_expansion_block_03.py evaluation/downstream_benchmark/screening/block_03_preparation_compatibility.py evaluation/downstream_benchmark/screening/block_03_materializer_bridge.py evaluation/downstream_benchmark/tests/test_expansion_block_03_preparation.py evaluation/downstream_benchmark/tests/test_block_03_preparation_compatibility.py evaluation/downstream_benchmark/tests/test_block_03_materializer_bridge.py
git diff --check
```

The preparation wrapper runs each module's `verify` mode under read-only Git
and forbidden-runtime guards:

```text
python3 -m evaluation.downstream_benchmark.screening.block_03_preparation_compatibility verify
python3 -m evaluation.downstream_benchmark.screening.prepare_expansion_block_01 verify
python3 -m evaluation.downstream_benchmark.screening.prepare_expansion_block_02 verify
```

Results: Block-03 7 ready / 0 blocked, Block-01 10 ready / 0 blocked,
Block-02 8 ready / 2 historical blockers. The 438 permitted read-only Git calls
created no subject environment or execution outcome. Historical Block-02
acquisition flags are saved provenance, not new acquisition in this closure.

The test wrapper calls `pytest.main` with this exact merged set of accepted
bridge regression targets:

```text
evaluation/downstream_benchmark/tests/test_block_03_materializer_bridge.py
evaluation/downstream_benchmark/tests/test_environment_build_recipes.py
evaluation/downstream_benchmark/tests/test_screening_environment_audit.py
evaluation/downstream_benchmark/tests/test_environment_materializer.py
evaluation/downstream_benchmark/tests/test_expansion_block_02_batch.py
evaluation/downstream_benchmark/tests/test_block_03_preparation_compatibility.py
evaluation/downstream_benchmark/tests/test_expansion_block_03_preparation.py
evaluation/downstream_benchmark/tests/test_expansion_block_01_preparation.py
evaluation/downstream_benchmark/tests/test_expansion_block_02_preparation.py
evaluation/downstream_benchmark/tests/test_screening_executor.py::ScreeningExecutorTests::test_committed_pre_eligibility_ledgers_pass_controlling_validation
-k 'not test_a_b_f_and_repeat_a and not test_read_only_revision_hash_matches_staged_snapshot'
-q -p no:cacheprovider --tb=short
```

Result: **186 passed, 0 failed, 2 deselected, 76 subtests passed**.
The union reruns all compatibility and materializer bridge bounded targets
without duplicate collection. Ruff passed for all seven accepted Python sources;
`git diff --check` passed. Full repository pytest and the two prohibited runtime
regressions were not run.

The dry wrapper invokes the real CLI function's `validate-expansion-03` and
`plan-expansion-03` modes under guards. Both accept exactly seven cases and
report `materialization_authorized=false`; the plan lists fourteen inert future
BUGGY/FIXED identities, zero attempts. The process logs contain only read-only
Git calls and zero Docker/non-Git runtime process calls. Scratch evidence and
complete accepted-file preimages remain under the named `/private/tmp` root;
none is staged.

An initial entry helper asserted a generic disk-permission mapping from Git
`100644`, failing on the pre-existing `0600` screening execution plan. Comparison
with the accepted previous transaction snapshot confirmed that permission was
unchanged. The valid check preserves actual accepted disk modes/types; no
accepted file or implementation was corrected. The complete entry gate passed
using that evidence.

Required validation comprises the accepted compatibility-aware seven-case
saved-byte verification (the original default controller intentionally retains
the historical 5/2 derivation), both bridge test suites, the accepted bounded
materializer/Block-01/02 regressions, read-only Block-03 input/plan validation,
Block-01/02 preparation `verify`, changed-source Ruff, whitespace checks, and
scientific-state preservation checks. Full repository pytest is not a local
commit gate; no active local Git hook is installed.

The accepted two exclusions from regression collection are preserved:
`test_a_b_f_and_repeat_a` would execute Docker;
`test_read_only_revision_hash_matches_staged_snapshot` would export real subject
source. Neither is invoked. Actual subprocesses during bounded validation are
restricted to read-only Git; dry consumption also forbids Docker wrappers and
the materialization engine. Synthetic fixtures/mocks do not establish any
subject/runtime/oracle result.

## Unchanged scientific state

```text
cumulative metadata admissions = 67
accepted exclusions = 34
UNSUPPORTED_ENVIRONMENT = 9
DEPENDENCY_SETUP_FAILURE = 23
ORACLE_COMMAND_INVALID = 2
environment-ready = 26
required slots = 28
oracle outcomes = 0
cases_manifest.csv = header-only
```

Admissions remain 40 + 10 + 10 + 7. Historical materialization ledgers and the
preserved identity-completion record reproduce 19 + 4 + 3 = 26 ready cases.
Required slots remain 24 final plus four permanently separate pilot cases.
The exact V4 exclusion union and header-only manifest are unchanged. Zero oracle
outcomes is the recorded scientific state; no subject oracle is run to verify it.

## Frozen lifecycle meaning

After all bounded checks passed, the exact 37-path inventory above is declared
`BLOCK_03_PRE_MATERIALIZATION_RUNTIME_BASELINE_V1 = FROZEN`.
The enclosing closure commit fixes its immutable identity. When this record is
read from that authorized commit with the specified parent/message/inventory,
the lifecycle state is:

```text
BLOCK_03_PRE_MATERIALIZATION_RUNTIME_BASELINE_V1 = FROZEN
PERSISTED = YES
COMMITTED = YES
MATERIALIZATION_EXECUTED = NO
ELIGIBILITY_ESTABLISHED = NO
FIRST_PASS_MATERIALIZATION_AUTHORIZED = NO
```

Until the authorized commit exists, the working-tree record alone does not
establish `COMMITTED = YES`. Post-commit parent/message/path/blob, clean-tree/index,
committed membership, disabled-gate and scientific-state checks are required
and are reported in the final chat Run Report. No post-commit self-update,
amendment, second commit or embedded commit-SHA mutation is permitted.

## Runtime firewall and next authority gate

```text
BLOCK_03_REAL_MATERIALIZATION_ENABLED = False
MATERIALIZATION_EXECUTED = NO
ELIGIBILITY_ESTABLISHED = NO
FIRST_PASS_MATERIALIZATION_AUTHORIZED = NO
DOCKER_BUILD_EXECUTED = NO
DOCKER_CONTAINER_EXECUTED = NO
GOVERNED_ENVIRONMENT_MATERIALIZED = NO
SUBJECT_DEPENDENCY_INSTALLATION_EXECUTED = NO
SUBJECT_SETUP_EXECUTED = NO
TOX_SUBJECT_COMMAND_EXECUTED = NO
SETUP_PY_DEVELOP_EXECUTED = NO
BUGGY_ORACLE_EXECUTED = NO
FIXED_ORACLE_EXECUTED = NO
ELIGIBILITY_CLASSIFICATION_PERFORMED = NO
ACCEPTED_EXCLUSION_ADJUDICATION_PERFORMED = NO
ENVIRONMENT_READY_COUNT_CHANGED = NO
PILOT_FINAL_ALLOCATION_PERFORMED = NO
REPAIR_EXECUTION_PERFORMED = NO
BLOCK_03_MEMBERSHIP_CHANGED = NO
PREPARATION_SEMANTICS_CHANGED = NO
RANKING_RULE_CHANGED = NO
PROJECT_CAP_CHANGED = NO
CASES_MANIFEST_POPULATED = NO
GIT_PUSH_PERFORMED = NO
```

No build/run/container, governed environment, installation/setup, tox/develop,
BUGGY/FIXED oracle or 3/3 screening, eligibility/exclusion decision, allocation,
repair, Block-04 construction, ranking/membership/cursor/cap/skip alteration,
unrelated cleanup, tag, release, or push is authorized. This freeze applies
only to the accepted pre-materialization runtime baseline. It establishes no
case eligibility, environment readiness increment, oracle pass, build success,
runtime compatibility, or scientific validation.

```text
NEXT_GATE = HUMAN_PI_REVIEW_OF_COMMITTED_BLOCK_03_RUNTIME_BASELINE
FIRST_PASS_MATERIALIZATION_NOT_AUTHORIZED
GIT_PUSH_NOT_AUTHORIZED
```

Runtime buildability, dependency/system-package requirements and tox/oracle
execution compatibility remain untested. External evidence availability remains
an input dependency of the accepted validator. The enclosing local closure
commit is the immutable starting baseline for any separately authorized later
first-pass materialization; this transaction grants no authority for that step.

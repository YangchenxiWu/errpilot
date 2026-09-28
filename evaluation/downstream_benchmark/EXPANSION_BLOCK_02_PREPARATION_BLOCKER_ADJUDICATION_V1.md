# Expansion Block 02 preparation-blocker adjudication V1

Status: `EXPANSION_BLOCK_02_PREPARATION_BLOCKER_ADJUDICATION_V1_FROZEN`.

## Human-PI authority and frozen inputs

The Human PI accepts `cookiecutter::3` and `cookiecutter::4` as `ACCEPTED_EXCLUSION` with `NON_RETRY` and final reason `ORACLE_COMMAND_INVALID`. This is a normative decision about the frozen oracle representation boundary, not a subject test or eligibility result. Block 02 identity is `6d5a8a713ddcb18ea70b8268c72e7aa2d5e1eb44bace81f1bd485c88907c0b95`. The controlling Block 02 preparation report is `EXPANSION_BLOCK_02_PREPARATION_V1.md`; its committed execution plan records eight `EXPANSION_PREPARATION_READY` cases and exactly these two `EXPANSION_PREPARATION_BLOCKED` cases. No Block 02 environment was built.

| Expansion order | Case | Exact pinned `run_test.sh` command | Script SHA-256 |
| ---: | --- | --- | --- |
| 5 | `cookiecutter::3` | `tox tests/test_read_user_choice.py::test_click_invocation` | `e2d6b23928c772e858658ac76f40fdb0c374d469f56411bb1a5f5e039442fca4` |
| 7 | `cookiecutter::4` | `tox tests/test_hooks.py::TestExternalHooks::test_run_failing_hook` | `b9237865af67323bdf738c16108241b4f88e448db1fab9dddb057ac78630c6b2` |

The preserved `oracle_representation.json` for each case records `COMPOSITE_ORACLE_SEMANTICS_V1`, an empty direct-argv plan, `subcommand 1: unrecognized test command tox`, and `executed: false`. The pinned commands therefore cannot be represented under the frozen direct test-argv model. `ORACLE_COMMAND_INVALID` is independently sufficient as the primary disposition. Neither oracle was executed, and neither case has an eligibility outcome. These are not subject test failures.

The separate preserved setup input for both cases contains `python setup.py develop`. The preparation ledger classifies it as `SETUP_UNRESOLVED:unsupported setup action at line 1: UNSUPPORTED_OR_AMBIGUOUS`. This remains secondary, unresolved setup evidence. It was not executed or observed to fail, and it does not replace the primary oracle disposition. The case-specific references and script hashes are frozen in `expansion_block_02_preparation_blocker_adjudication_v1.csv`.

`NON_RETRY` closes these two cases under the first frozen preparation evidence. It does not authorize another preparation attempt, an oracle run, a build, or an eligibility assignment. No systemic amendment is authorized: `tox` is not added to the oracle executable set or translated to `pytest`; `tox.ini` is not interpreted; tox-managed virtual environments, dependencies, or tests are not inferred; and `python setup.py develop` is not added to the setup taxonomy. The preserved evidence establishes no general, mechanically exact, semantics-preserving transformation. The first preparation artifacts remain unchanged.

## Count and downstream gates

The prior pre-eligibility ledger has 27 exclusions. These two accepted preparation exclusions bring its exact union to 29. Already environment-ready cases number 23; eight Block 02 cases are preparation-ready but unbuilt; two are preparation-excluded. The maximum environment-ready count before Block 02 materialization attrition is 31 against 28 required eligible slots. Block 03 is not mathematically required solely by these two exclusions. Block 02 materialization outcomes are needed for the next capacity decision. Environment-ready does not mean eligible. Block 02 materialization, Block 03 selection, oracle screening, eligibility assignment, repair, and downstream model execution remain under separate authority.

# Expansion Block 02 first-pass batch authority V1

Status: `EXPANSION_BLOCK_02_FIRST_PASS_BATCH_AUTHORITY_V1_FROZEN`.

## Human-PI authority and entry state

The Human PI freezes `BUGSINPY_EXPANSION_BLOCK_02_FIRST_PASS_BATCH_AUTHORIZED_V1` as the exact Controller V2 batch token. This authority-freeze transaction entered on clean `main` at local HEAD and live `origin/main` commit `16c2e2f50bf78913104b7b87097d15a993e0f1ff`, ahead/behind `0/0`. The frozen Block 02 identity is `6d5a8a713ddcb18ea70b8268c72e7aa2d5e1eb44bace81f1bd485c88907c0b95`.

The predecessors are `EXPANSION_BLOCK_02_MATERIALIZER_BRIDGE_V1_FROZEN`, `EXPANSION_BLOCK_02_PRE_DISPATCH_INCIDENT_V1_FROZEN`, `EXPANSION_BLOCK_02_PRODUCTION_CONTROLLER_V2_FROZEN`, and `PRE_ELIGIBILITY_EXCLUSIONS_LEDGER_STATE_V3_VALIDATED`. Controller V2 derives and validates 12/12 requests from the eight ready frozen recipes. The V3 exclusions union contains 29 rows; `cases_manifest.csv` is header-only. There is no repository Block 02 materialization result report or CSV.

## Exact first-pass identities

| Dispatch order | Case | Revision label |
| ---: | --- | --- |
| 1 | `tornado::13` | `SOURCE_INDEPENDENT` |
| 2 | `tornado::4` | `SOURCE_INDEPENDENT` |
| 3 | `spacy::6` | `BUGGY` |
| 4 | `spacy::6` | `FIXED` |
| 5 | `fastapi::12` | `SOURCE_INDEPENDENT` |
| 6 | `tqdm::7` | `BUGGY` |
| 7 | `tqdm::7` | `FIXED` |
| 8 | `spacy::7` | `BUGGY` |
| 9 | `spacy::7` | `FIXED` |
| 10 | `httpie::5` | `SOURCE_INDEPENDENT` |
| 11 | `PySnooper::1` | `BUGGY` |
| 12 | `PySnooper::1` | `FIXED` |

These identities and their order are derived from Controller V2 and the frozen recipe modes. `cookiecutter::3` and `cookiecutter::4` are excluded by their frozen `NON_RETRY` adjudication and receive no build authority. A failed `BUGGY` attempt does not consume or suppress the separately authorized `FIXED` first pass.

## Two-key execution boundary and attempt budget

Real production dispatch requires both independent authority layers:

1. Controller V2 requires the exact outer batch token `BUGSINPY_EXPANSION_BLOCK_02_FIRST_PASS_BATCH_AUTHORIZED_V1` before request derivation or production-root creation.
2. After that gate, the controller supplies the distinct inner materializer token `BUGSINPY_EXPANSION_BLOCK_02_MATERIALIZATION_AUTHORIZED_V1` to the Block 02 materializer, whose request validator and real-materialization gate still apply.

Neither token substitutes for the other. Block 01 tokens are invalid for Block 02. The Human-PI budget is exactly **one governed first-pass build-layer attempt per listed identity**, with **0/12 consumed at this freeze**. No second attempt or other Block 02 identity is implicitly authorized. The future production transaction must be separately invoked against the committed Controller V2 code and pass its live entry, request, and authority gates. This freeze itself invokes no production dispatch.

The historical `tornado::13 / SOURCE_INDEPENDENT` controller invocation remains `CONTROLLER_PRE_DISPATCH_INVALID_REQUEST`, `NON_PRODUCTION_ATTEMPT`, and `ABORTED_BEFORE_FIRST_PRODUCTION_ATTEMPT`. It failed before the governed materializer engine and does not consume that identity's scientific attempt. The sealed historical incident root `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_02` remains read-only; its frozen 10-file summary SHA-256 is `1cea074fbac40c465bff0b3a76f1fbfcca8b79da3e0a14d38af47ad44a6a50bb`. The reserved Controller V2 production root `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_02_v2` remains absent in this transaction. `v2` names the controller transaction, not a second scientific attempt.

**AUTHORITY FROZEN != EXECUTION OCCURRED.** This transaction performs zero real Block 02 production attempts, Docker subject builds, dependency installations, setup actions, subject tests, oracles, eligibility decisions, repairs, or ErrPilot/model/API executions. It creates no production root, attempt ledger, or materialization result artifact. This authority grants no retry, oracle, eligibility, or repair execution.

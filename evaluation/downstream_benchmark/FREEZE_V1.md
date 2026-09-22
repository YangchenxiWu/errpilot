# Downstream Benchmark Harness V1 Freeze Record

Freeze status: `BENCHMARK_HARNESS_SYNTHETICALLY_VALIDATED`

## Human-PI Acceptance Scope

The Human-PI accepts the preceding transaction result only as evidence of
synthetic harness validity. This freeze records that bounded acceptance; it
does not authorize or establish any broader benchmark, production, or
scientific conclusion.

## Explicit Negative Claims and Boundaries

This freeze does **not** establish:

- ErrPilot effectiveness;
- BugsInPy readiness;
- live Codex validity;
- production isolation validity;
- pilot validity;
- benchmark validity; or
- scientific evaluation completion.

No BugsInPy execution occurred. No real BugsInPy case or result exists. No live
Codex or model invocation occurred, and no live Codex adapter exists. No
network-dependent benchmark execution occurred. The validation used only the
local synthetic fixture and synthetic-only harness path.

Future production, candidate-screening, pilot, or final benchmark work requires
separate Human-PI authority. This freeze grants no authority for a subsequent
transaction.

## Authoritative Artifacts

- `PROTOCOL.md` SHA-256:
  `34e014a07821dc9dca52178874eef0b847aee7f048071fb4920864ae5d3bee93`
- `RUN_SPEC_V1.md` SHA-256:
  `29ab6f78739d0eeea1c2a774e62e2d133f173e160c3d247407970a80726f4406`

## Synthetic Validation Evidence

Command:

```text
python3 -B -m unittest discover -s evaluation/downstream_benchmark/tests -v
```

Result: 14 tests passed, 0 failed (`Ran 14 tests`; `OK`).

The already-local `ruff 0.15.6` checks also passed:

```text
ruff check evaluation/downstream_benchmark
ruff format --check evaluation/downstream_benchmark
```

The production/default timeout remains exactly 1200 seconds.
`cases_manifest.csv` remains header-only. `exclusions.csv` remains header-only.

## SHA-256 Inventory

This inventory covers every file under `evaluation/downstream_benchmark/` at
freeze time except this `FREEZE_V1.md` file. Its own hash is intentionally
excluded to avoid recursive identity.

```text
d8abd18bc59bca51edb8fdd28fef484059e1c7ac9a927749a70a77b9c0287a70  evaluation/downstream_benchmark/IMPLEMENTATION_VALIDATION.md
34e014a07821dc9dca52178874eef0b847aee7f048071fb4920864ae5d3bee93  evaluation/downstream_benchmark/PROTOCOL.md
21d2bf42be94762c47c6d97de58846f244cf0530f069856c69eb9bd6fc5a010f  evaluation/downstream_benchmark/README.md
3a66eb4926533c46842e2c7e759500dfc42f08515989170cf49af07dde7b105f  evaluation/downstream_benchmark/RUNNER_DESIGN.md
29ab6f78739d0eeea1c2a774e62e2d133f173e160c3d247407970a80726f4406  evaluation/downstream_benchmark/RUN_SPEC_V1.md
c7d423696616ffb7d5dc79fa5bf56294044b3d66c247c744d575617dbb89dac9  evaluation/downstream_benchmark/cases_manifest.csv
d005a11fcad11ca71f95fd27d772a5d1b5f27caed5c23638b43c5af93cbc6f0e  evaluation/downstream_benchmark/exclusions.csv
e6d59a4af53c4bfdf9a37cb7c8b17411b5d3447746f98cd91bb6632864fa43ce  evaluation/downstream_benchmark/fixtures/synthetic_case/source/oracle.py
6e3ede277d6d74c8df333a50f72a729d3e3d64af8d3fa29cf8d1a40ab64c6f3c  evaluation/downstream_benchmark/fixtures/synthetic_case/source/protected/oracle_data.txt
2ae95b205dcad1605dc99d26053f0f714972176c408140d348bfd1cdf7783717  evaluation/downstream_benchmark/fixtures/synthetic_case/source/subject.py
5301d4cefcb9175e66ad8f02e2436b7a7d0c12eaf01666313dcdd00bd375b056  evaluation/downstream_benchmark/harness/__init__.py
787533fc616c395db2362a0330ded88412588fb40f51cd6212d1e3318761498c  evaluation/downstream_benchmark/harness/adapters.py
f941e562a23cf8b2f8e71a5254a1dbc27082b652c315db1bd48de53107d6b6cb  evaluation/downstream_benchmark/harness/constants.py
8dd85a32317d0625c46ae94060691ddf19905143100a6e5164bd61f40305921e  evaluation/downstream_benchmark/harness/errors.py
6fefcb4ac7a236dad274b1fca9667079c5815942bc24f1906fea505a64b21bc6  evaluation/downstream_benchmark/harness/filesystem.py
8d2045fc896699da160c3e1977247becb16f518c9294244309f3df466a63785b  evaluation/downstream_benchmark/harness/models.py
b3268bdca268c0e9825449c7f30fa9934198adb4df19fd986ae6f9a1d686b9c3  evaluation/downstream_benchmark/harness/payloads.py
abf59685a2fdb6becebec2b01df4f29a40ff02332ecf95c2cfd901bbb7b7923c  evaluation/downstream_benchmark/harness/runner.py
e3cfcbbb0e25ec546f948ce2bcee88fa25f7e037b25bca160836576d18b87875  evaluation/downstream_benchmark/harness/schemas/case_spec.schema.json
3970db708089bc3f66797e31f0b88a8eb09fe99ae2a956eb01e5e4b23459446e  evaluation/downstream_benchmark/harness/schemas/result.schema.json
c80ebd3d156e92d6c098c372c3a2a00227b1929fd073bbd4fff940f8a2de6bd2  evaluation/downstream_benchmark/tests/test_synthetic_harness.py
```

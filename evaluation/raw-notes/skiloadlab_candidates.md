• Candidate Report

  1. gha_provenance_missing_builder

  - Reproduce: gh run view 25018886610 --log-failed
  - Failure type: recent GitHub Actions release/signing failure
  - Deterministic: yes, archived log
  - Expected fields: python_traceback: no, pytest failing_tests: no, source_contexts: .github/workflows/ci.yml, scripts/generate-provenance.py, git state: yes, logs: yes
  - Severity: S2
  - Route: manual_review
  - Privacy/security: CI log includes Actions env and artifact names; summarize only.
  - Useful because ErrPilot must distinguish supply-chain/provenance schema failures from test failures. Core error: cosign attestation rejected provenance because required builder field was missing.

  2. gha_cosign_signing_config_conflict

  - Reproduce: gh run view 25018793061 --log-failed
  - Failure type: recent GitHub Actions CLI/tool config failure
  - Deterministic: yes, archived log
  - Expected fields: python_traceback: no, pytest failing_tests: no, source_contexts: .github/workflows/ci.yml, git state: yes, logs: yes
  - Severity: S2
  - Route: manual_review
  - Privacy/security: CI log contains token-masked GitHub context; do not copy full log.
  - Useful because it tests whether ErrPilot can extract a non-Python root cause from shell logs. Core error: cosign rejected simultaneous service URL options and signing config.

  3. gha_missing_script_generate_provenance

  - Reproduce: gh run view 25018564514 --log-failed
  - Failure type: recent GitHub Actions path/config failure
  - Deterministic: yes, archived log
  - Expected fields: python_traceback: no, pytest failing_tests: no, source_contexts: .github/workflows/ci.yml, scripts/, git state: yes, logs: yes
  - Severity: S3
  - Route: codex_prompt
  - Privacy/security: low; log paths are repo/runner paths only.
  - Useful because ErrPilot should identify missing repository file/path regressions. Core error: .venv/bin/python could not open scripts/generate-provenance.py.

  4. gha_pytest_missing_entrypoints_and_deps

  - Reproduce: gh run view 25017856113 --log-failed
  - Failure type: pytest/import/path/config failure in CI
  - Deterministic: yes, archived log
  - Expected fields: python_traceback: yes, pytest failing_tests: yes, source_contexts: tests/test_alpha_sweep.py, tests/test_combined_load.py, tests/test_make_figures.py, tests/test_robustness_framework.py, pyproject.toml, .github/workflows/ci.yml,
    git state: yes, logs: yes
  - Severity: S3
  - Route: codex_prompt
  - Privacy/security: low; avoid copying full CI log because it includes masked checkout auth metadata.
  - Useful because it has mixed failure modes in one run: missing console scripts such as skiloadlab-combine plus ModuleNotFoundError for dependencies like pandas/numpy.

  5. local_cli_missing_input_files

  - Reproduce:
      - python3 -m skiloadlab.cli.combine --in /tmp/skiloadlab_missing_input.csv --out /tmp/skiloadlab_should_not_exist.csv --report /tmp/skiloadlab_should_not_exist.json --alpha 0.5
      - or python3 -m skiloadlab.cli.make_figures --runs /tmp/skiloadlab_missing_runs.csv --alpha_summary /tmp/skiloadlab_missing_alpha.csv --out_dir /tmp/skiloadlab_figs_should_not_exist
  - Failure type: local CLI input/config failure
  - Deterministic: yes
  - Expected fields: python_traceback: yes, pytest failing_tests: no, source_contexts: skiloadlab/core_model.py or skiloadlab/core_viz.py, git state: yes, logs: yes
  - Severity: S4
  - Route: local_suggestion
  - Privacy/security: low; uses synthetic /tmp missing paths.
  - Useful because it is safe, fast, and offline. It checks whether ErrPilot can extract user-actionable missing-file diagnostics from a Python traceback.



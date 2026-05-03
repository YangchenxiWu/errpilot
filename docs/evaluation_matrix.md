# Evaluation Capability Matrix

ErrPilot's case-study evaluation does not measure bug-fixing success. It
measures whether a wrapped failing command produces a stable failure record,
structured extraction, deterministic local triage, and handoff artifacts that a
human or downstream coding tool can audit.

The executable cases below are intentionally in-repository `pytest examples/`
commands. They provide a reproducible evidence path without depending on
author-specific paths, remote services, external repository state, or external
repair tools. ErrPilot captures and explains the failure; it does not execute
downstream repair tools.

## Executable ErrPilot Cases

| case_id | command | failure type | expected severity | actual severity | route | extracted fields demonstrated | why this case matters |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `errpilot_python_assertion_failure` | `pytest examples/python_assertion_failure` | `pytest_assertion` | `S2` | `S2` | `codex_or_aider_prompt` | `failing_tests=1`; `python_traceback=no`; `source_contexts=1`; `risk_flags=none`; `triage=yes`; `handoff_artifacts=1` | Baseline local assertion failure. Demonstrates that ErrPilot can identify a single failing pytest node, attach bounded source context, assign a low-risk local severity, and create a handoff prompt artifact. |
| `errpilot_pytest_fixture_failure` | `pytest examples/pytest_fixture_failure` | `pytest_fixture_error` | `S4` | `S4` | `manual_plus_agent_investigation` | `failing_tests=1`; `python_traceback=no`; `source_contexts=1`; `risk_flags=none`; `triage=yes`; `handoff_artifacts=1` | Exercises pytest setup/configuration failure handling. The route is compatible with the `manual_or_aider_prompt` expectation because missing fixtures often require project-level test design context. |
| `errpilot_python_import_failure` | `pytest examples/python_import_failure` | `python_import_error` | `S4` | `S4` | `manual_plus_agent_investigation` | `failing_tests=1`; `python_traceback=no`; `source_contexts=1`; `risk_flags=none`; `triage=yes`; `handoff_artifacts=1` | Covers pytest collection-time import failure. This case shows that ErrPilot records failures that happen before normal test execution and routes dependency/path issues toward investigation. |
| `errpilot_pytest_multi_failure` | `pytest examples/pytest_multi_failure` | `pytest_multi_assertion` | `S3` | `S3` | `stronger_coding_agent_prompt` | `failing_tests=2`; `python_traceback=no`; `source_contexts=1`; `risk_flags=none`; `triage=yes`; `handoff_artifacts=1` | Demonstrates multi-failure extraction and escalation above the single-assertion baseline. Multiple failing tests motivate a stronger handoff because the root cause may be broader than one assertion. |
| `errpilot_missing_config_failure` | `pytest examples/missing_config_failure` | `missing_required_config` | `S4` | `S4` | `manual_plus_agent_investigation` | `failing_tests=1`; `python_traceback=no`; `source_contexts=1`; `risk_flags=none`; `triage=yes`; `handoff_artifacts=1` | Represents a missing local configuration/file dependency. This validates that ErrPilot preserves concrete file evidence while routing environment/configuration failures away from simple local edits. |
| `errpilot_python_type_error_failure` | `pytest examples/python_type_error_failure` | `python_type_error` | `S2` | `S2` | `codex_or_aider_prompt` | `failing_tests=1`; `python_traceback=no`; `source_contexts=1`; `risk_flags=none`; `triage=yes`; `handoff_artifacts=1` | Covers a local runtime type error inside pytest. It complements assertion failures by showing that non-assertion Python exceptions still produce structured failing-test evidence and bounded source context. |

Notes:

- `python_traceback=no` means the executable pytest examples exercise the pytest
  failure parser rather than ErrPilot's stderr traceback parser.
- `risk_flags=none` reflects the current executable local examples. External
  documented cases motivate supply-chain and CI risk categories without making
  those repositories part of the default reproducible run.
- Expected routes from `cases.csv` use paper-facing route labels such as
  `codex_prompt` and `manual_or_aider_prompt`; `results.csv` reports the
  concrete local route. The evaluation checks route compatibility.

## Documented-Only External Cases

| case_id | source_project | failure type | why it is documented-only | capability it motivates |
| --- | --- | --- | --- | --- |
| `skiloadlab_gha_missing_script_generate_provenance` | `skiloadlab` | recent GitHub Actions path/config failure | Depends on archived GitHub Actions logs and repository-specific runner paths. The default evaluation does not call GitHub or execute external repositories. | CI log intake with workflow/script source context and handoff for missing generated provenance script paths. |
| `skiloadlab_local_cli_missing_input_files` | `skiloadlab` | local CLI input/config failure | Requires an external project, its dependencies, and its CLI module state. It is kept as metadata rather than executed in ErrPilot's repository. | Local CLI failure capture, traceback extraction, source context around input validation, and local-suggestion triage. |
| `slsa_verifier_missing_cosign_identity_env` | `slsa_verifier` | shell script missing required env config | Requires an external shell script and project layout. It also represents CI/signing configuration that should not be synthesized inside ErrPilot's default run. | Shell stderr intake, missing environment/configuration detection, and risk signaling for absent signing identity. |
| `slsa_verifier_missing_provenance_file` | `slsa_verifier` | missing provenance/SBOM-like file | Requires an external verifier script and supply-chain evidence paths. The synthetic missing file path is documented, not executed, to avoid external repo state. | Missing evidence detection, supply-chain risk flag motivation, and handoff when required provenance is absent. |
| `slsa_verifier_generate_provenance_uninstalled_package` | `slsa_verifier` | Python path/config error | Requires the external package layout and an uninstalled local invocation. Executing it would depend on editable-install state outside ErrPilot. | Python traceback extraction for import/path failures and routing when local invocation differs from CI/package setup. |

Documented-only external cases are paper context, not part of the reproducible
default execution count. They motivate real-world failure categories while
avoiding author-specific paths, private runtime assumptions, network calls, and
external repository mutations.

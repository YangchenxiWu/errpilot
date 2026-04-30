  Candidate 1

  - case_id: missing_cosign_identity_env
  - command: ./scripts/verify_attestation.sh
  - failure type: shell script / missing required env config
  - deterministic: yes
  - expected fields:
      - stderr/log excerpt: ERROR: COSIGN_CERTIFICATE_IDENTITY not set
      - python_traceback: no
      - pytest failing_tests: no
      - source_contexts: scripts/verify_attestation.sh, env var check
      - risk_flags: missing CI signing identity
  - severity: S3
  - route: local_suggestion
  - privacy/security concerns: none
  - useful because: clean single-line shell failure with obvious config root cause.

  Candidate 2

  - case_id: missing_provenance_file
  - command: env COSIGN_CERTIFICATE_IDENTITY=https://example.invalid/identity PROVENANCE_FILE=/tmp/errpilot-missing-provenance.json ./scripts/verify_attestation.sh sbom.json
  - failure type: missing provenance/SBOM-like file
  - deterministic: yes
  - expected fields:
      - stderr/log excerpt: missing provenance file: /tmp/errpilot-missing-provenance.json
      - python_traceback: no
      - pytest failing_tests: no
      - source_contexts: scripts/verify_attestation.sh, PROVENANCE_FILE
      - risk_flags: missing supply-chain evidence
  - severity: S3
  - route: codex_prompt
  - privacy/security concerns: uses only dummy identity and /tmp path
  - useful because: tests artifact verification intake when required evidence is absent.

  Candidate 3

  - case_id: audit_script_python_missing_from_path
  - command: env PATH=/bin bash audit-dependencies.sh
  - failure type: missing dependency / path config error
  - deterministic: yes on environments where python is not in /bin
  - expected fields:
      - stderr/log excerpt: audit-dependencies.sh: line 4: python: command not found
      - python_traceback: no
      - pytest failing_tests: no
      - source_contexts: audit-dependencies.sh
      - risk_flags: toolchain dependency unavailable
  - severity: S4
  - route: local_suggestion
  - privacy/security concerns: none; command fails before creating .venv
  - useful because: simple audit-script failure caused by PATH/runtime assumptions.

  Candidate 4

  - case_id: generate_provenance_uninstalled_package
  - command: python3 ./generate-provenance.py --dist dist --output /tmp/errpilot-provenance.json
  - failure type: Python path/config error
  - deterministic: yes if package is not installed and PYTHONPATH is unset
  - expected fields:
      - stderr/log excerpt: ModuleNotFoundError: No module named 'slsa_verifier'
      - python_traceback: yes
      - pytest failing_tests: no
      - source_contexts: generate-provenance.py, src/slsa_verifier/provenance.py
      - risk_flags: local invocation differs from CI editable install
  - severity: S4
  - route: codex_prompt
  - privacy/security concerns: output target is /tmp; failure occurs before write
  - useful because: validates traceback extraction and import-path diagnosis.

  Candidate 5

  - case_id: gha_cosign_attestation_predicate_schema
  - command: gh run view 25066002519 --log-failed
  - failure type: GitHub Actions workflow / provenance attestation schema
  - deterministic: yes for captured run log; live rerun may differ
  - expected fields:
      - stderr/log excerpt: Error: provenance predicate: required field builder missing and Process completed with exit code 1
      - python_traceback: no
      - pytest failing_tests: no
      - source_contexts: .github/workflows/security.yml, generate-provenance.py
      - risk_flags: supply-chain attestation invalid, signed artifact pipeline blocked
  - severity: S2
  - route: manual_review
  - privacy/security concerns: GitHub log includes masked token lines (token: ***) and public repo/run metadata; avoid storing full logs unnecessarily
  - useful because: realistic CI failure where tool must connect workflow step, cosign command, and provenance schema mismatch.



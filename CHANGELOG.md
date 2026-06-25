# Changelog

## 0.1.0-release-candidate

### Added

- Root project framing for ARA-style artifact to commit-time admissibility interoperability.
- Non-claims boundary for independent exploration.
- ARA-to-standing mapping.
- Glossary for admissibility, standing, authority, delegation, evidence, and commitment-candidate terminology.
- Commitment-candidate JSON Schema.
- Standing-result JSON Schema.
- Example commitment candidates for ALLOW, DENY, and FAIL-CLOSED evaluator behavior.
- Standing-result examples for ALLOW, DENY, and FAIL-CLOSED.
- Negative fixtures for malformed candidate/result validation.
- Minimal deterministic evaluator stub.
- Repo-local validators for schema files, examples, schema-subset validation, negative fixtures, and evaluator fixtures.
- Status generator producing `status/generated-status.json`.
- Validation report generator producing `status/validation-report.md`.
- Validation report interpretation guide.
- Canonical GitHub Actions workflow.
- iOS-safe workflow mirror and manifest.
- GitHub Actions step summary output for validation reports.
- Workflow artifact retention guide as optional future hardening.

### Boundary

This release candidate does not certify external ARA artifacts, assert upstream ARA endorsement, or claim general compatibility. It only establishes an independently maintained interoperability prototype for evaluating ARA-style artifacts as commitment candidates under a commit-time standing model.

### Remaining future hardening

- Optional full JSON Schema validation if dependency policy permits.
- Optional workflow artifact upload for retained generated reports.
- Additional external artifact examples if collaborators provide explicit permission and terminology boundaries.

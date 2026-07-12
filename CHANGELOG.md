# Changelog

## 0.2.0-release-candidate

### Added

- Explicit governed publication manifest for `public_review` and future `canonical` states.
- Dependency-free fail-closed publication gate.
- Negative publication fixtures and executable gate tests.
- GitHub Pages deployment conditioned on the publication gate.
- Hash-bound publication receipt with manifest hash, file inventory, commit, workflow, and deployment identity.
- Publication receipt JSON Schema.
- Human- and machine-readable publication status generation.
- Deployment URL verification and retained deployment evidence.
- Canonical and iOS-safe workflow parity checking.
- Updated docs index, publication-status surface, governed-publication guide, and mirror handoff.

### Boundary

This release candidate automates publication only under the manifest-declared posture. It does not establish upstream ARA endorsement, certification of external artifacts, independent review, canonical doctrine, clinical validity, regulatory authorization, or execution authority.

### Release gate

- Repository-check workflow must pass.
- Pages workflow must pass.
- A deployed publication receipt must contain a verified HTTPS deployment URL.
- Stable tagging remains blocked until those conditions are evidenced.

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
- Additional external artifact examples if collaborators provide explicit permission and terminology boundaries.
- Richer evaluator semantics beyond the current stub.

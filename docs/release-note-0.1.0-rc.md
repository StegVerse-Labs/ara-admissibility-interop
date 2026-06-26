# Release Note: 0.1.0 Release Candidate

## Summary

`0.1.0-release-candidate` establishes the first reviewable ARA admissibility interoperability prototype.

The repository demonstrates how an ARA-style artifact can be presented as a commitment candidate and evaluated through a commit-time standing model that returns:

```text
ALLOW | DENY | FAIL-CLOSED
```

## What this release candidate includes

- Explicit non-claims and boundary language.
- ARA-to-standing mapping.
- Admissibility glossary.
- Commitment-candidate schema.
- Standing-result schema.
- ALLOW, DENY, and FAIL-CLOSED examples.
- Negative fixtures that must be rejected.
- Minimal evaluator stub proving all three outcomes.
- Dependency-free validation tools.
- Machine-readable generated status.
- Human-readable validation report.
- Canonical and iOS-safe GitHub Actions workflow paths.
- Release-readiness checklist.

## Required review command

```bash
python3 tools/generate_validation_report.py
```

Expected generated outputs:

```text
status/generated-status.json
status/validation-report.md
```

## Claims

This release candidate claims only that the repository now contains a coherent, dependency-free prototype for evaluating ARA-style artifacts as commitment candidates under a commit-time standing model.

## Non-claims

This release candidate does not claim:

- endorsement by ARA authors or projects;
- certification of any external artifact;
- production Standing Proof Engine behavior;
- journal, conference, lab, platform, or repository acceptance;
- execution authority for any external system;
- full JSON Schema conformance beyond the documented dependency-free subset.

## Suggested public framing

This repository explores whether agent-native research artifacts can be evaluated as commitment candidates before they are accepted, cited, executed, published, or relied upon downstream.

It does not replace ARA. It tests the standing layer that may be needed at the moment an artifact crosses a governed boundary.

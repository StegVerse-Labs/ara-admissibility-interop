# Release Readiness

## Candidate

Version: `0.1.0-release-candidate`

Release manifest: [`../release-manifest.json`](../release-manifest.json)

Release checklist: [`release-checklist.md`](release-checklist.md)

Release note: [`release-note-0.1.0-rc.md`](release-note-0.1.0-rc.md)

Optional strict validation: [`optional-strict-validation.md`](optional-strict-validation.md)

## Purpose

This release candidate captures the first complete public shape of the ARA admissibility interoperability prototype.

It is intended to be reviewable as a repository artifact without requiring chat history.

## Release candidate criteria

A release candidate is ready when the repository can demonstrate:

| Criterion | Status |
| --- | --- |
| Boundary and non-claims are explicit | Ready |
| ARA-style artifact concepts are mapped to standing concepts | Ready |
| Commitment-candidate schema exists | Ready |
| Standing-result schema exists | Ready |
| ALLOW, DENY, and FAIL-CLOSED examples exist | Ready |
| Invalid fixtures are rejected | Ready |
| Evaluator stub proves all three outcomes | Ready |
| Machine-readable status can be generated | Ready |
| Human-readable validation report can be generated | Ready |
| Canonical workflow runs validation reporting | Ready |
| iOS-safe workflow mirror is aligned | Ready |
| Optional strict JSON Schema validation is visible in generated status | Ready |
| Artifact upload retention exists | Optional future hardening |

## Required release check

Run:

```bash
python3 tools/generate_validation_report.py
```

Expected generated files:

```text
status/generated-status.json
status/validation-report.md
```

Expected state:

```text
self-check-pass
```

## Optional strict check

The optional strict path is:

```bash
python3 tools/validate_with_jsonschema_optional.py
```

This check is optional. If `jsonschema` is absent, it reports `skip` with exit code `0`. If `jsonschema` is installed, it performs stricter schema validation and fails on violations.

## Non-release claims

This release candidate does not claim:

- upstream ARA endorsement;
- certification of external ARA artifacts;
- journal, conference, lab, or platform acceptance;
- production Standing Proof Engine behavior;
- required full JSON Schema conformance when the optional dependency is absent;
- execution authority for any external system.

## Suggested release note

Use [`release-note-0.1.0-rc.md`](release-note-0.1.0-rc.md) for short public or reviewer-facing summaries.

`0.1.0-release-candidate` establishes a dependency-free interoperability prototype for presenting ARA-style artifacts as commitment candidates and evaluating them through ALLOW, DENY, and FAIL-CLOSED standing-result examples.

## Next version candidate

The next candidate after this release should be `0.2.0` if the repository adds one or more of:

- make full JSON Schema validation required if dependency policy changes;
- external example package with explicit permission;
- richer evaluator semantics beyond the current stub;
- artifact upload retention in the live workflow;
- generated docs site integration.

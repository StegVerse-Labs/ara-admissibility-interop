# ARA Admissibility Interop Docs

This documentation index is the static-site entry point for the ARA admissibility interoperability prototype.

## Start here

- [Release readiness](release-readiness.md)
- [Release checklist](release-checklist.md)
- [Release note: 0.1.0 RC](release-note-0.1.0-rc.md)
- [Validation report guide](validation-report-guide.md)

## Governance and boundaries

- [Dependency policy](dependency-policy.md)
- [Optional strict validation](optional-strict-validation.md)
- [Workflow artifact retention](workflow-artifact-retention.md)

## Core repository references

- [Repository README](../README.md)
- [Release manifest](../release-manifest.json)
- [Changelog](../CHANGELOG.md)
- [Version marker](../VERSION)

## Admissibility references

- [Admissibility README](../admissibility/README.md)
- [Non-claims](../admissibility/non-claims.md)
- [Glossary](../admissibility/glossary.md)
- [ARA-to-standing map](../admissibility/ara-to-standing-map.md)
- [Evaluator usage](../admissibility/evaluator-usage.md)

## Validation command

Run from the repository root:

```bash
python3 tools/generate_validation_report.py
```

Expected generated outputs:

```text
status/generated-status.json
status/validation-report.md
```

## Boundary

This repository is an independent interoperability prototype. It does not claim upstream ARA endorsement, certification of external artifacts, production Standing Proof Engine behavior, or execution authority for external systems.

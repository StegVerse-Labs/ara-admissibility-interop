# ARA Admissibility Interop Docs

This documentation index is the static-site entry point for the ARA admissibility interoperability prototype.

## Start here

- [Publication status](publication-status.md)
- [Release readiness](release-readiness.md)
- [Release checklist](release-checklist.md)
- [Release note: 0.2.0 RC](release-note-0.2.0-rc.md)
- [Validation report guide](validation-report-guide.md)
- [Governed publication](governed-publication.md)
- [Independent publication evidence verification](publication-evidence-verification.md)

## Governance and boundaries

- [Dependency policy](dependency-policy.md)
- [Optional strict validation](optional-strict-validation.md)
- [Workflow artifact retention](workflow-artifact-retention.md)
- [Publication manifest](../publication-manifest.json)
- [Publication receipt schema](../publication/publication-receipt.schema.json)

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

## Validation commands

Run from the repository root:

```bash
python3 tools/generate_validation_report.py
python3 tools/check_publication_gate.py
python3 tools/test_publication_gate.py
python3 tools/check_workflow_parity.py
python3 tools/generate_publication_status.py
python3 tools/generate_publication_receipt.py
python3 tools/test_publication_evidence_verifier.py
```

To inspect a retained receipt independently:

```bash
python3 tools/verify_publication_evidence.py status/publication-receipt.json
```

Expected generated outputs:

```text
status/generated-status.json
status/validation-report.md
status/publication-status.json
status/publication-receipt.json
docs/publication-status.md
```

The publication gate must report `PUBLICATION_GATE=ALLOW` before the Pages deployment job can run.

## Publication posture

The current site is published for `public_review`. Canonical status, independent review, clinical validation, regulatory authorization, and execution authority are not implied by deployment.

## Boundary

This repository is an independent interoperability prototype. It does not claim upstream ARA endorsement, certification of external artifacts, production Standing Proof Engine behavior, or execution authority for external systems.

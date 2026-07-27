---
layout: default
title: ARA Admissibility Interop Docs
---

# ARA Admissibility Interop Docs

This documentation site presents an interoperability prototype connecting machine-readable publication, agent-native research artifacts, and commit-time admissibility.

The prototype asks whether content that software can discover and cite can also be converted into an explicit, reviewable request for downstream reliance.

```text
Machine-readable publication
        ↓
Artifact and evidence resolution
        ↓
Requested downstream use
        ↓
Commitment candidate
        ↓
ALLOW | DENY | FAIL-CLOSED
```

## Start here

- [Machine-readable publication bridge](machine-readable-publication-bridge.md)
- [Worked machine-readable citation candidate](../admissibility/examples/machine-readable-publication-citation-candidate.json)
- [ARA-to-standing map](../admissibility/ara-to-standing-map.md)
- [Publication status](publication-status.md)
- [Release readiness](release-readiness.md)
- [Release checklist](release-checklist.md)
- [Release note: 0.2.0 RC](release-note-0.2.0-rc.md)
- [Validation report guide](validation-report-guide.md)
- [Governed publication](governed-publication.md)
- [Independent publication evidence verification](publication-evidence-verification.md)
- [Governed release evidence decision](release-evidence-decision.md)
- [Evidence-bounded release gate promotion](release-gate-promotion.md)
- [Governed deployment email and monitoring](deployment-email-monitoring.md)

## Core distinction

| Layer | Question answered |
| --- | --- |
| Machine-readable publication | What was published, where is it, and how can software resolve it? |
| ARA-style artifact | What logic, code, trace, evidence, and history are preserved? |
| Commitment candidate | What exact citation, publication, integration, execution, or reliance action is requested? |
| Standing determination | Is that requested action admissible for this actor, target, scope, and moment? |

Machine-readable accessibility is necessary for automated use, but it does not itself prove correctness, current validity, authority, or permission to rely on the content.

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
python3 tools/test_release_evidence_evaluator.py
python3 tools/test_evidence_bundle_manifest.py
python3 tools/test_release_gate_promotion.py
python3 tools/test_deployment_notification.py
python3 tools/test_deployment_notification_transport.py
```

To inspect a retained receipt independently:

```bash
python3 tools/verify_publication_evidence.py status/publication-receipt.json
```

To convert verified evidence into bounded public-review and stable-release decisions:

```bash
python3 tools/evaluate_release_evidence.py
```

To generate a non-mutating release-gate promotion proposal:

```bash
python3 tools/promote_release_gates.py
```

To convert a received deployment email into a verification-required next-task candidate:

```bash
python3 tools/ingest_deployment_notification.py
```

Expected generated outputs:

```text
status/generated-status.json
status/validation-report.md
status/publication-status.json
status/publication-receipt.json
status/release-evidence-decision.json
status/release-evidence-decision.md
status/release-manifest.promoted.json
status/release-gate-promotion.json
status/deployment-notification-email.md
status/deployment-notification-envelope.json
status/deployment-notification-delivery.json
status/deployment-next-task-candidate.json
docs/publication-status.md
```

The publication gate must report `PUBLICATION_GATE=ALLOW` before the Pages deployment job can run.

## Publication posture

The current site is published for `public_review`. Canonical status, independent review, scientific validation, regulatory authorization, and execution authority are not implied by deployment.

## Collaboration posture

The central question is not whether this repository replaces machine-readable publishing or ARA. It is whether the mapping from discoverable publication metadata to a bounded commitment candidate usefully supports automated citation and agent-native research.

## Boundary

This repository is an independent interoperability prototype. It does not claim upstream ARA endorsement, certification of external artifacts, production Standing Proof Engine behavior, or execution authority for external systems.
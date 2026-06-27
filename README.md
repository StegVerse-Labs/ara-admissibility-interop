# ARA Admissibility Interop

This repository explores interoperability between Agent-Native Research Artifacts (ARA-style artifacts) and commit-time admissibility evaluation.

The repository does not replace ARA. It asks whether an agent-native research artifact can be evaluated as a commitment candidate before it is accepted, cited, executed, published, or used downstream.

```text
Agent-Native Research Artifact
        ↓
Commitment Candidate
        ↓
Standing Determination
        ↓
ALLOW | DENY | FAIL-CLOSED
```

## Purpose

Agent-native research artifacts improve how research work can be packaged for agents and humans. They can preserve logic, code, traces, evidence, failed branches, and execution history.

Commit-time admissibility addresses a separate question: whether the artifact has standing at the moment it is presented for commitment.

This repository begins with a narrow interoperability hypothesis:

> ARA-style research artifacts can be treated as inputs to a standing and admissibility layer without replacing the ARA artifact model.

## Docs

Static-site documentation starts at [`docs/index.md`](docs/index.md).

## Current goal

Generated docs site integration.

The dependency-free validation path remains the default. Dependency rules are defined in [`docs/dependency-policy.md`](docs/dependency-policy.md). Optional full JSON Schema validation is documented in [`docs/optional-strict-validation.md`](docs/optional-strict-validation.md) and surfaced through [`release-manifest.json`](release-manifest.json).

## Run validation

From the repository root:

```bash
python3 tools/generate_validation_report.py
```

This generates:

```text
status/generated-status.json
status/validation-report.md
```

See [`docs/validation-report-guide.md`](docs/validation-report-guide.md) for how to interpret these outputs.

For optional strict validation with `jsonschema` when installed, run:

```bash
python3 tools/validate_with_jsonschema_optional.py
```

## Layer distinction

| Layer | Primary question |
| --- | --- |
| ARA-style artifact | What was built, tested, traced, evidenced, and reconstructed? |
| Commitment candidate | What action is now being requested based on the artifact? |
| Standing determination | Does the candidate have authority, valid policy, admissible evidence, and commit-time standing now? |

## Repository structure

```text
admissibility/
  README.md
  non-claims.md
  glossary.md
  ara-to-standing-map.md
  commitment-candidate.schema.json
  standing-result.schema.json
  evaluator_stub.py
  evaluator-usage.md
  examples/
    sample-commitment-candidate.json
    deny-execution-candidate.json
    fail-closed-incomplete-boundary-candidate.json
    sample-standing-result-allow.json
    sample-standing-result-deny.json
    sample-standing-result-fail-closed.json
    invalid-missing-claim-boundary.json
    invalid-standing-result-decision.json
docs/
  index.md
  dependency-policy.md
  release-readiness.md
  release-checklist.md
  release-note-0.1.0-rc.md
  optional-strict-validation.md
  validation-report-guide.md
  workflow-artifact-retention.md
tools/
  assess_repo.py
  check_dependency_policy.py
  validate_schema_files.py
  validate_examples.py
  validate_by_schema_subset.py
  validate_with_jsonschema_optional.py
  validate_negative_fixtures.py
  check_evaluator_fixture.py
  generate_status.py
  generate_validation_report.py
status/
  current-status.json
VERSION
CHANGELOG.md
release-manifest.json
```

## Workflow paths

The canonical GitHub Actions workflow path begins with a leading period:

```text
.github/workflows/repo-check.yml
```

For iOS-safe handling, the same workflow is mirrored without the leading period at:

```text
iosnoperiod/github/workflows/repo-check.yml
```

Both workflow paths run:

```bash
python3 tools/generate_validation_report.py
```

Artifact retention is documented in [`docs/workflow-artifact-retention.md`](docs/workflow-artifact-retention.md). The live workflow upload step is optional future hardening.

## Status

Generated docs site integration build in progress.

## Relationship to StegVerse

This repository is part of the StegVerse-Labs exploration of commit-time admissibility, standing proof, and governed transition evaluation.

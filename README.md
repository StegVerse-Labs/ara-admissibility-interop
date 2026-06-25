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

## Current goal

Validation hardening.

For this repository, that means the repo must be able to:

1. describe its own boundary and non-claims;
2. validate commitment-candidate and standing-result examples;
3. reject invalid fixtures for expected reasons;
4. prove evaluator behavior for ALLOW, DENY, and FAIL-CLOSED;
5. generate machine-readable status;
6. generate human-readable validation reporting;
7. keep canonical and iOS-safe workflow paths aligned.

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
  validation-report-guide.md
tools/
  assess_repo.py
  validate_schema_files.py
  validate_examples.py
  validate_by_schema_subset.py
  validate_negative_fixtures.py
  check_evaluator_fixture.py
  generate_status.py
  generate_validation_report.py
status/
  current-status.json
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

## Status

Validation-hardening build in progress.

## Relationship to StegVerse

This repository is part of the StegVerse-Labs exploration of commit-time admissibility, standing proof, and governed transition evaluation.

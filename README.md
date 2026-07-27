# ARA Admissibility Interop

This repository explores interoperability between Agent-Native Research Artifacts (ARA-style artifacts), machine-readable publication, and commit-time admissibility evaluation.

The repository does not replace ARA or prescribe a universal publication format. It asks a downstream question:

> Once research content is machine-readable, discoverable, and citable by software, how should an agent or system determine whether it may rely on that content for a specific action?

```text
Research content
        ↓
Machine-readable publication
        ↓
Agent or robot discovery
        ↓
Commitment Candidate
        ↓
Standing Determination
        ↓
ALLOW | DENY | FAIL-CLOSED
```

## Why this bridge exists

Machine-readable publication helps software answer:

> What was published, where is it, and how can it be cited or inspected?

Commit-time admissibility addresses a separate question:

> May this actor use this artifact for this action, target, scope, and moment?

The second question depends on the first. This repository therefore treats citation metadata, canonical URLs, artifact manifests, evidence links, versions, and content digests as interoperability inputs to a bounded standing decision.

## Purpose

Agent-native research artifacts improve how research work can be packaged for agents and humans. They can preserve logic, code, traces, evidence, failed branches, and execution history.

Machine-readable publication makes those artifacts easier for software to discover, resolve, cite, and inspect.

Commit-time admissibility then evaluates whether a proposed downstream use has valid authority, policy, evidence, scope, timing, and recoverability.

The repository begins with this narrow interoperability hypothesis:

> ARA-style research artifacts and other machine-readable publications can be treated as inputs to a standing and admissibility layer without replacing their publication or artifact models.

## Intended collaboration posture

This is not presented as an upstream replacement or completed answer. It is an invitation to test whether an explicit transition from publication metadata to a reviewable commitment candidate is useful.

The central collaboration question is:

> Does this mapping help support machine-readable publishing, automated citation, and agent-native research by making downstream reliance explicit and governable?

Critique is especially useful where the mapping omits publication fields, imposes unnecessary standing checks, or fails to preserve the original artifact's claims and non-claims.

## Start here

- [Machine-readable publication bridge](docs/machine-readable-publication-bridge.md)
- [Worked citation commitment candidate](admissibility/examples/machine-readable-publication-citation-candidate.json)
- [ARA-to-standing map](admissibility/ara-to-standing-map.md)
- [Static documentation site](docs/index.md)

## Layer distinction

| Layer | Primary question |
| --- | --- |
| Machine-readable publication | What was published, where is it, and how can software resolve it? |
| ARA-style artifact | What was built, tested, traced, evidenced, and reconstructed? |
| Commitment candidate | What action is now being requested based on the artifact? |
| Standing determination | Does the candidate have authority, valid policy, admissible evidence, scope, and commit-time standing now? |

## Example interoperability flow

A publication page may expose a canonical URL, BibTeX, JSON-LD, an artifact manifest, and evidence links. An agent that wants to cite the artifact converts that proposed use into a commitment candidate containing:

- the exact artifact and version;
- the requested action;
- the requesting actor;
- the affected target;
- the permitted scope and claim boundary;
- the relevant policy and delegation;
- the supporting evidence references;
- the current execution context and validity window;
- the recoverability posture.

The evaluator returns `ALLOW`, `DENY`, or `FAIL-CLOSED`. Discoverability alone does not establish truth, authority, or permission to rely on the artifact.

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

The dependency-free validation path remains the default. Dependency rules are defined in [`docs/dependency-policy.md`](docs/dependency-policy.md).

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
    machine-readable-publication-citation-candidate.json
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
  machine-readable-publication-bridge.md
  dependency-policy.md
  release-readiness.md
  release-checklist.md
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

Artifact retention is documented in [`docs/workflow-artifact-retention.md`](docs/workflow-artifact-retention.md).

## Publication and authority boundary

This repository may demonstrate machine-readable publication, evidence resolution, and a governed decision path. It does not imply that:

- publication metadata proves scientific correctness;
- discoverability grants permission to rely on an artifact;
- an upstream ARA project endorses this prototype;
- a public-review deployment grants execution authority;
- an automated citation is independently replicated or verified unless evidence establishes that result.

## Relationship to StegVerse

This repository is part of the StegVerse-Labs exploration of commit-time admissibility, standing proof, and governed transition evaluation. Its intended role is complementary: preserve the machine-readable publication and artifact layer, then make the exact downstream reliance request inspectable before commitment.
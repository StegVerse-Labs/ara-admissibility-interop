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

Continue building without manual actions needed through completion, or until task handoff and task completion can be handled by the ecosystem's own management.

For this repository, that means the repo must become capable of:

1. describing its own boundary and non-claims;
2. validating its commitment-candidate and standing-result examples;
3. running a deterministic evaluator stub;
4. reporting build state in a machine-readable status file;
5. identifying the next handoff target when local repo management is no longer sufficient.

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
    sample-standing-result-allow.json
    sample-standing-result-deny.json
    sample-standing-result-fail-closed.json
management/
  goal-activation.md
  repo-status.json
  assess_repo.py
```

## Build path to goal activation

1. Define non-claims and boundaries. Complete.
2. Map ARA-style artifact components to standing fields. Complete.
3. Define commitment-candidate and standing-result schemas. Complete.
4. Add examples for ALLOW, DENY, and FAIL-CLOSED outcomes. Complete.
5. Add evaluator stub and usage notes. Complete.
6. Add repo management assessment and status reporting. In progress.
7. Add CI or task-runner handoff once repo-local management is stable. Pending.

## Status

Foundation draft with active goal activation path.

## Relationship to StegVerse

This repository is part of the StegVerse-Labs exploration of commit-time admissibility, standing proof, and governed transition evaluation.

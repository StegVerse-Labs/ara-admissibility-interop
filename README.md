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

## Layer distinction

| Layer | Primary question |
| --- | --- |
| ARA-style artifact | What was built, tested, traced, evidenced, and reconstructed? |
| Commitment candidate | What action is now being requested based on the artifact? |
| Standing determination | Does the candidate have authority, valid policy, admissible evidence, and commit-time standing now? |

## Initial build path

1. Define non-claims and boundaries.
2. Map ARA-style artifact components to standing fields.
3. Define a commitment-candidate schema.
4. Define a standing-result schema.
5. Add examples for ALLOW, DENY, and FAIL-CLOSED outcomes.

## Status

Foundation draft. The first files establish scope, non-claims, and the initial admissibility boundary.

## Relationship to StegVerse

This repository is part of the StegVerse-Labs exploration of commit-time admissibility, standing proof, and governed transition evaluation.

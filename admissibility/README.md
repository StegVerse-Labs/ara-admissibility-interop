# Admissibility Layer

This directory defines the first interoperability boundary between ARA-style research artifacts and StegVerse-style commit-time admissibility evaluation.

## Core distinction

ARA-style artifacts can preserve the research process. They may include logic, code, trace data, evidence, failed branches, execution details, and human-readable summaries.

Admissibility evaluation asks whether a proposed use of that artifact has standing now.

```text
Research artifact
      ↓
Proposed use
      ↓
Commitment candidate
      ↓
Standing determination
      ↓
ALLOW | DENY | FAIL-CLOSED
```

## Why this layer exists

Reconstructability is not the same as admissibility.

An artifact may be reproducible and still fail standing if authority, delegation, policy, evidence, timing, scope, or recoverability are invalid at commit time.

This layer therefore separates four questions:

| Question | Layer |
| --- | --- |
| What happened? | Trace and reconstruction |
| What supports the claim? | Evidence |
| What action is being requested? | Commitment candidate |
| May the action cross a governed boundary now? | Standing determination |

## Initial admissibility outcomes

| Outcome | Meaning |
| --- | --- |
| ALLOW | The candidate has sufficient commit-time standing under the applicable policy and evidence boundary. |
| DENY | The candidate was evaluated and does not have sufficient standing. |
| FAIL-CLOSED | The candidate cannot be safely evaluated because a required field, policy, authority, evidence, or context check is missing, corrupt, stale, or indeterminate. |

## Build order

1. Preserve non-claims.
2. Define artifact-to-standing mapping.
3. Define commitment-candidate schema.
4. Define standing-result schema.
5. Add examples and evaluator stubs.

## Boundary statement

This directory does not certify ARA artifacts. It only explores whether ARA-style artifacts can be presented as candidates for commit-time standing evaluation.

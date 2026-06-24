# ARA to Standing Map

This file maps ARA-style artifact concepts to the first StegVerse admissibility concepts used by this repository.

The map is provisional. It is intended to support interoperability discussion, not to redefine ARA or claim upstream acceptance.

## Layer map

| ARA-style layer | Interoperability interpretation | Standing question |
| --- | --- | --- |
| Logic | Claimed reasoning, hypothesis structure, derivation, or argument path | What claim is being presented, and what boundary does it attempt to cross? |
| Code | Executable implementation, scripts, notebooks, tests, or tools | Does the executable path correspond to the claimed transition? |
| Trace | Reconstruction path showing what happened during exploration or execution | Can the claimed path be reconstructed without contradiction? |
| Evidence | Supporting inputs, outputs, observations, datasets, or references | Is the evidence admissible for this requested use? |
| Human-readable summary | Narrative explanation for human review | Does the summary preserve the claim boundary without inflating authority? |
| Agent-readable structure | Machine-oriented representation of artifact state | Can a downstream evaluator consume the artifact without ambiguous authority? |
| Review output | Human or agent evaluation of the artifact | Is this review only historical posture, or does it carry present authority? |
| Artifact package | Bounded research-process package | Can this package be presented as a commitment candidate? |

## Standing bridge

An ARA-style artifact does not automatically become admissible merely because it is complete, executable, or reproducible.

This repository introduces an explicit bridge:

```text
ARA-style artifact
        ↓
requested use
        ↓
commitment candidate
        ↓
standing determination
```

The bridge prevents artifact structure from being silently treated as authority.

## Commitment candidate conversion

A commitment candidate should identify:

| Field | Purpose |
| --- | --- |
| transition_id | Names the proposed boundary crossing. |
| artifact_reference | Points to the ARA-style artifact or package. |
| requested_action | Describes what is being requested now. |
| actor | Identifies who or what is presenting the candidate. |
| target | Identifies what object, system, publication, claim, process, or boundary is affected. |
| scope | Limits where the candidate may apply. |
| claim_boundary | Separates claims from non-claims. |
| policy_reference | Identifies the policy used for standing evaluation. |
| delegation_reference | Identifies any delegated authority. |
| evidence_references | Identifies supporting evidence. |
| execution_context | Captures the context at commit time. |
| validity_window | Limits when the candidate can be evaluated. |
| recoverability_profile | States whether failure or reversal is possible. |

## Standing result interpretation

A standing result evaluates the candidate, not the entire artifact universe.

| Result | Meaning |
| --- | --- |
| ALLOW | The candidate has standing for the requested use under the current policy and evidence boundary. |
| DENY | The candidate was evaluated and failed one or more standing requirements. |
| FAIL-CLOSED | The candidate cannot safely be evaluated because a required part is absent, corrupt, stale, contradictory, or indeterminate. |

## Explicit separations

These separations are central to the interoperability model:

```text
Publication is not authority.
Review is not standing.
Execution is not admissibility.
Reconstruction is not commitment.
Reproducibility is not evidence admissibility.
Artifact completeness is not downstream permission.
```

## Open questions

1. Which ARA fields, if any, should be treated as sufficient artifact references for a commitment candidate?
2. Can an ARA trace provide evidence references directly, or should evidence references be separately canonicalized?
3. Should review outputs be admissible evidence, observer posture, or both?
4. What is the minimum commitment candidate required for citation-only use?
5. What additional fields are required when the requested action touches irreversible execution?

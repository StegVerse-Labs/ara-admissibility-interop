# Glossary

This glossary defines the working terms used by this repository. Definitions are provisional and may be refined as interoperability work develops.

## ARA-style artifact

An agent-native research artifact or artifact package that preserves research work in forms usable by humans and agents. It may include logic, code, trace, evidence, failed branches, execution details, and summaries.

This repository uses `ARA-style artifact` as a broad interoperability phrase and does not claim authority to define ARA itself.

## Admissibility

The property that a claim, artifact, action, evidence item, or transition may be accepted for a specific governed purpose under the applicable boundary conditions.

Admissibility is scoped. An artifact may be admissible for one purpose and inadmissible for another.

## Standing

The present ability of a commitment candidate to cross a governed boundary under current policy, authority, delegation, evidence, timing, scope, and context conditions.

Standing is evaluated at commit time. It is not inherited automatically from prior review, publication, reproduction, or execution.

## Commit time

The moment at which a proposed action, claim, artifact use, publication use, citation use, execution, or downstream reliance is presented for determination.

Commit time is the boundary where historical reconstruction meets present standing.

## Commitment candidate

A structured request that presents an artifact, claim, or action for possible commitment.

A commitment candidate does not approve itself. It only declares what is being requested, by whom, under what scope, with which evidence, policy, delegation, context, validity window, and recoverability profile.

## Standing determination

The result of evaluating a commitment candidate against current standing requirements.

The initial result set used by this repository is:

- `ALLOW`
- `DENY`
- `FAIL-CLOSED`

## ALLOW

The candidate has sufficient standing for the requested use under the applicable policy, authority, delegation, evidence, scope, timing, and context boundary.

`ALLOW` is specific to the evaluated candidate. It is not a universal endorsement of the artifact.

## DENY

The candidate was evaluated and failed one or more standing requirements.

`DENY` means the evaluator had enough information to refuse standing for the requested use.

## FAIL-CLOSED

The candidate cannot safely be evaluated because a required field, policy, authority, delegation, evidence reference, context value, validity condition, or recoverability condition is missing, corrupt, stale, contradictory, or indeterminate.

`FAIL-CLOSED` prevents ambiguity from becoming execution authority.

## Authority

The recognized power to request, approve, deny, delegate, execute, publish, cite, rely upon, or otherwise bind a transition within a defined scope.

Authority must be scoped and current. Historical involvement is not automatically present authority.

## Delegation

A bounded transfer or assignment of authority from one actor or role to another.

Delegation must identify scope, source, recipient, allowed actions, constraints, and validity conditions.

## Evidence

Material offered to support a claim, requested action, or standing determination.

Evidence can support reconstruction without automatically being admissible for a requested commitment.

## Evidence admissibility

The determination that evidence may be used for the requested purpose under the applicable policy, scope, provenance, integrity, timing, and context requirements.

## Claim boundary

The line separating what an artifact or actor claims from what it does not claim.

Claim boundaries prevent interoperability language from becoming endorsement, certification, compatibility, or authority by implication.

## Requested use

The specific action or reliance being proposed for an artifact or claim.

Examples include citation, publication, repository acceptance, execution, downstream integration, policy reliance, or irreversible system action.

## Scope

The defined range within which a candidate, policy, authority, delegation, evidence item, or result applies.

Scope can include actor, artifact, action, time, system, repository, publication, research domain, execution environment, or downstream use.

## Validity window

The time interval during which a candidate, policy, delegation, evidence item, or standing result may be evaluated or relied upon.

## Recoverability profile

A statement of whether the requested action can be reversed, remediated, quarantined, replayed, reconstructed, or safely failed.

Recoverability affects the standing requirements for commitment.

## Reconstruction

The ability to determine what happened from traces, records, evidence, logs, or artifact structure.

Reconstruction is necessary for many evaluations but is not identical to admissibility.

## Reproducibility

The ability to rerun or reproduce a result, output, behavior, experiment, or artifact path.

Reproducibility can strengthen evidence, but it does not automatically create authority or standing.

## Observer posture

A reviewer's or evaluator's stated position about an artifact, claim, or candidate.

Observer posture can become evidence, but it is not automatically execution authority.

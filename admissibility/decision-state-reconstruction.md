# StegGate Decision-State Reconstruction Contract

Status: normative design requirement for the StegGate v4.6 candidate
Owner: `StegVerse-Labs/ara-admissibility-interop`
Runtime consumer: `StegVerse-Labs/StegCore`
Continuity consumer: `StegVerse-Labs/Continuity`

## Principle

Admissibility is not merely a prerequisite to execution. The admissibility determination is itself part of the reconstructable state of the governed system.

A reconstructable system MUST preserve enough information to establish not only what execution occurred, but the complete material admissibility state that caused execution, prevented execution, deferred execution, or failed safely before execution.

The durable record therefore MUST NOT be limited to successful `ALLOW` outcomes.

## Required decision-state surface

For each governed transition attempt, the reconstruction surface MUST preserve directly or by cryptographically bound reference:

- canonical candidate and `candidate_hash`;
- evidence set actually evaluated;
- authority/delegation artifacts and versions;
- policy artifacts and versions;
- applicability determinations;
- freshness, validity, and expiry determinations;
- each material admissibility predicate and its result;
- unknown, unresolved, or unavailable predicate states;
- obligations produced by evaluation;
- terminal disposition and reason codes;
- evaluation time and relevant validity intervals;
- execution topology;
- admission-token and TTL state where applicable;
- approval state, signer binding, and signature references where applicable;
- attempted target/effect;
- whether commit was attempted;
- whether an external effect occurred, did not occur, or remained unknown;
- target-side observation evidence;
- reconciliation result;
- post-execution observations and any divergence from expected state.

## Every terminal disposition is evidence

The admissibility matrix itself is evidence. `ALLOW`, `DENY`, `REVIEW`, and `FAIL_CLOSED` MUST all produce durable decision-state records.

`DENY` is not equivalent to absence of an attempted transition.

`FAIL_CLOSED` is not equivalent to `DENY`. It preserves an epistemically distinct state: execution was prevented because required confidence, evidence, authority, freshness, applicability, or boundary conditions were insufficient or unavailable.

`REVIEW` is not an ALLOW-like pause. A later reviewed or modified candidate is a new transition and MUST NOT retroactively overwrite the original candidate or evaluation.

## State model

A governed transition SHOULD be reconstructable across the following conceptual lifecycle:

```text
PROPOSED
  -> EVALUATED
  -> ALLOW | DENY | REVIEW | FAIL_CLOSED
  -> [if applicable] ADMITTED
  -> COMMIT_ATTEMPTED
  -> COMMITTED | NOT_COMMITTED | COMMIT_UNKNOWN
  -> OBSERVED | NOT_OBSERVED | OBSERVATION_UNKNOWN | DIVERGENT
  -> RECONCILED | UNRESOLVED
```

Not every disposition advances to commit. The absence of a commit after `DENY`, `REVIEW`, or `FAIL_CLOSED` is itself a meaningful governed outcome when bound to the originating transition.

## Three distinct realities

Reconstruction MUST distinguish:

1. **Decision reality** — what StegGate concluded from the admissibility matrix.
2. **Execution reality** — what the target or executor actually did.
3. **Observed reality** — what can later be established from bound observations and reconciliation evidence.

These states MAY disagree and the disagreement MUST remain representable.

Examples:

```text
Decision: ALLOW
Execution: commit accepted
Observed: external effect missing
Reconciliation: DIVERGENT
```

```text
Decision: DENY
Execution: effect nevertheless occurred
Observed: effect confirmed
Reconciliation: GOVERNANCE_BYPASS
```

The second case demonstrates why non-ALLOW decision records are necessary for proving bypass or incomplete gateway coverage.

## Completeness and coverage consequence

A successful `ALLOW` receipt proves only that a particular transition was admitted under a particular evaluation. It does not by itself prove that all relevant mutations passed through the governed boundary.

Coverage evidence therefore SHOULD support the stronger reconstruction claim:

> For the bounded scope and period, known governed transition attempts can be related to their complete admissibility evaluations, dispositions, and observed effects or non-effects.

Target attestations, reconciliation scans, chain checkpoints, or equivalent coverage mechanisms MAY be used, but transport reachability or the existence of a receipt MUST NOT be treated as proof of complete mediation.

## Canonical record shape

Implementations MAY use multiple linked artifacts rather than one monolithic object, but the logical reconstruction surface is equivalent to:

```text
AdmissibilityEvaluation {
  candidate
  evidence_snapshot
  authority_matrix
  policy_matrix
  applicability_matrix
  freshness_matrix
  obligations
  unresolved_conditions
  disposition
  reasons
  temporal_context
  topology
  approval_state
  admission_state
  commit_state
  observation_state
  reconciliation_state
}
```

Cryptographic references MUST preserve exact artifact/version binding so later reconstruction cannot silently substitute current policy, current authority, or current evidence for what was actually evaluated.

## Interoperability ownership

`ara-admissibility-interop` owns the interoperable schema and semantic requirements for representing the decision-state surface.

`StegCore` owns runtime production of decision, commit-attempt, effect, observation, and reconciliation records at governed mutation boundaries.

`Continuity` owns preservation/reconstruction semantics and receipt-chain relationships. Continuity does not grant authority and MUST NOT reinterpret a historical `FAIL_CLOSED` as `DENY`, a `REVIEW` as approval, or non-occurrence as proof that no attempt existed.

## Non-claims

This requirement does not claim that every external effect is observable, that all targets support atomic reconciliation, that all governance bypasses can be detected, or that storage of a record creates authority. Unknown states remain explicit rather than being normalized into success or denial.

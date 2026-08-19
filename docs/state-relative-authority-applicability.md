# State-Relative Authority Applicability and Temporal Non-Causality

Status: implementation requirement transferred from the 2026-08-17 Action-First / Human Continuity session
Canonical semantic owner: `StegVerse-Labs/ara-admissibility-interop`
Runtime consumer: `StegVerse-Labs/StegCore` through its existing governed-execution path
Authority effect: NONE

## Primitive correction

Time indexes governance history. Elapsed time is not itself the governance-changing primitive.

A historically valid decision, authorization, refusal, approval, or other governance basis remains attributable to the operative state in which it was established. Applicability to a materially different successor state must be determined anew.

The governing form is therefore state-relative rather than merely time-relative:

```text
S_i --material transition--> S_j
```

not:

```text
T_i --elapsed time--> T_j
```

Timestamps and chronology remain important for ordering, provenance, freshness inputs, and explicitly declared clock conditions. They do not by themselves create the governance question.

## Normative invariants

### Temporal non-causality

```text
Delta-time -/-> Delta-governance
```

Elapsed time alone must not be treated as proof that authority, applicability, or legitimacy changed.

### State-relative applicability

```text
Valid(R_i, S_i) -/-> Applicable(R_i, S_j)
```

A record may remain historically valid while its applicability to a materially different state requires reassessment.

### No implicit authority inheritance

```text
Authority(S_i) -/-> Authority(S_j)
```

across a governance-material transition.

Continued execution in `S_j` requires either:

1. action-specific governance equivalence between the relevant portions of `S_i` and `S_j`; or
2. renewed or reconstructed authority applicable to `S_j`.

Otherwise the governing profile must resolve to its applicable non-authorizing state such as REVIEW, DENY, or FAIL_CLOSED.

### Current authorization determination

```text
Applicable(R_i, S_j) -/-> Authorized(Action, S_j)
```

without a current authority determination for the requested action.

### Explicit clock-derived state

Expiration, freshness, lease age, review intervals, or other clock-derived conditions may trigger governance reassessment only where the governing policy declares that condition as part of operative state. This prevents elapsed time from being silently reintroduced as the primitive.

## Operative governance fingerprint

A machine implementation should bind the applicability determination to at least:

- state;
- context;
- authority;
- authorization basis;
- evidence;
- policy;
- dependencies.

Governance equivalence must be action-specific. Global state equality is neither required nor sufficient.

## Consequential agency

Recorded human presence or authenticated input is not by itself evidence of governing agency.

A refusal, approval, modification, redirection, or other input is consequential agency with respect to an outcome only where the admissible human response can alter the reachable material consequence set.

If every admissible human response converges on the same authority-dependent downstream state, the system may preserve evidence of participation or intent, but it must not represent that evidence as proof that governing agency over that consequence remained exercisable.

This distinction preserves:

```text
recorded participation != consequential agency
record continuity != authority continuity
authority continuity != consequence continuity
```

## Deterministic acceptance cases

The canonical invariant/schema/profile implementation must include machine-verifiable cases proving:

1. a governance-material state change requires applicability reassessment;
2. an irrelevant state change does not invalidate otherwise applicable authority;
3. passage of time alone, with no declared clock-state transition, does not invalidate authority merely because time elapsed;
4. declared freshness or expiry conditions become explicit operative-state transitions and are enforced;
5. an alternate execution path cannot inherit a prior governance basis after a material transition without governance-equivalence or renewed/reconstructed authority;
6. refusal/choice evidence distinguishes recorded participation from consequential agency;
7. multiple authenticated human inputs that all produce the same material consequence cannot be represented as evidence of consequential choice over that consequence.

## Collision and ownership rule

This document does not create a competing schema/runtime lane.

Active draft `ara-admissibility-interop` PR #1 remains the existing StegGate schema-foundation/invariant integration candidate. Before implementation, its owner must reconcile this requirement against current PR #1, current `main`, and `docs/ARA_ADMISSIBILITY_INTEROP_MIRROR_HANDOFF.md`.

Where runtime enforcement is required, `StegVerse-Labs/StegCore` must consume the canonical ara semantic contract through its existing governed-execution path rather than independently redefining the invariant.

## Completion evidence required

This requirement is not COMPLETE merely because this document exists. Completion requires:

- canonical invariant/schema/profile representation installed;
- deterministic positive and negative fixtures installed;
- validators/tests passing with inspectable evidence;
- StegCore consumer binding validated where required;
- applicable mirror handoff updated with commits, tests, integration state, and propagation obligations;
- no live activation inferred from source merge, CI success, publication, or archival state.

Until those conditions are met, this document is a durable transferred requirement, not implementation-complete evidence.

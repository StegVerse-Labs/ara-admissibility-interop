# State-Relative Applicability at the Authority × Time Governance Coordinate

Status: implementation requirement transferred from the 2026-08-17 Action-First / Human Continuity session and corrected by `StegVerse-Labs/.github#1154` / `ara-admissibility-interop#137`
Canonical semantic owner: `StegVerse-Labs/ara-admissibility-interop`
Runtime consumer: `StegVerse-Labs/StegCore` through its existing governed-execution path
Authority effect: NONE
Canonical governance coordinate: `G = (Authority, Time)`

## Primitive correction

Authority and Time are the coordinates of governance:

```text
G = (A, T)
```

State is evaluated at a governance coordinate; it is not a replacement coordinate. A historically valid decision, authorization, refusal, approval, or other governance basis remains attributable to the Authority and Time at which it was established. Applicability to a materially different successor state must be determined at the applicable later governance coordinate.

A material state transition is represented as context change:

```text
S_i --material transition--> S_j
```

and governance evaluation occurs at:

```text
(A_i, T_i) with S_i
(A_j, T_j) with S_j
```

The fact that `S_i != S_j` may require reevaluation. It does not make State a governance coordinate.

Timestamps, clocks, heartbeat cadence, chronology, freshness observations, and durations are representations or inputs associated with the Time coordinate. They do not manufacture Authority.

## Normative invariants

### Authority × Time governance coordinate

```text
Governance = Authority × Time
G = (A, T)
```

State, context, policy, identity, delegation, evidence, dependencies, scope, recoverability, and other conditions are evaluated at this coordinate.

### Temporal non-causality

```text
Delta-time -/-> Delta-authority
```

Elapsed time alone must not be treated as proof that Authority, applicability, or legitimacy changed. This is a non-causality rule, not a claim that Time lies outside governance.

### State-relative applicability

```text
Valid(R_i, S_i, A_i, T_i) -/-> Applicable(R_i, S_j, A_j, T_j)
```

A record may remain historically valid while its applicability at a later governance coordinate with materially different state requires reassessment.

### No implicit authority inheritance

```text
Authority-at-(A_i,T_i,S_i) -/-> Authority-at-(A_j,T_j,S_j)
```

across a governance-material transition without an applicability determination.

Continued execution with `S_j` requires either:

1. action-specific governance equivalence between the relevant portions of `S_i` and `S_j`, with the applicable Authority resolved at `T_j`; or
2. renewed or reconstructed Authority applicable at `T_j`.

Otherwise the governing profile must resolve to its applicable non-authorizing state such as REVIEW, DENY, or FAIL_CLOSED.

### Current authorization determination

```text
Applicable(R_i, S_j, A_j, T_j) -/-> Authorized(Action, A_j, T_j)
```

without a current authority determination for the requested action at the applicable Time.

### Explicit clock-derived conditions

Expiration, freshness, lease age, review intervals, or other clock-derived conditions may affect governance evaluation where the governing policy declares those conditions relevant. The clock observation is an input associated with Time; it is not itself Authority and does not replace the Time coordinate.

## Operative governance fingerprint

A machine implementation should bind the applicability determination to the governance coordinate plus evaluated context:

```text
governance_coordinate:
  authority
  time

evaluated_context:
  state
  context
  authorization_basis
  evidence
  policy
  dependencies
```

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

None of these relations creates an additional governance coordinate.

## Deterministic acceptance cases

The canonical invariant/schema/profile implementation must include machine-verifiable cases proving:

1. governance is evaluated at an explicit `(Authority, Time)` coordinate;
2. a governance-material state change requires applicability reassessment without promoting State into a governance coordinate;
3. an irrelevant state change does not invalidate otherwise applicable Authority;
4. passage of time alone does not create, destroy, transfer, or renew Authority merely because time elapsed;
5. declared freshness or expiry conditions are evaluated at the relevant Time coordinate and enforced when governing policy requires them;
6. an alternate execution path cannot inherit a prior governance basis after a material transition without governance-equivalence or renewed/reconstructed Authority at the applicable Time;
7. refusal/choice evidence distinguishes recorded participation from consequential agency;
8. multiple authenticated human inputs that all produce the same material consequence cannot be represented as evidence of consequential choice over that consequence.

## Collision and ownership rule

This document does not create a competing schema/runtime lane.

`docs/AUTHORITY_TIME_GOVERNANCE_COORDINATE.md` is the local binding for the corrected primitive. Existing StegGate schema/invariant integration must consume this correction rather than restoring the superseded state-as-coordinate interpretation.

Where runtime enforcement is required, `StegVerse-Labs/StegCore` must consume the canonical ARA semantic contract through its existing governed-execution path rather than independently redefining the invariant.

## Completion evidence required

This requirement is not COMPLETE merely because this document exists. Completion requires:

- canonical invariant/schema/profile representation installed;
- deterministic positive and negative fixtures installed;
- validators/tests passing with inspectable evidence;
- StegCore consumer binding validated where required;
- applicable mirror handoff updated with commits, tests, integration state, and propagation obligations;
- no live activation inferred from source merge, CI success, publication, or archival state.

Until those conditions are met, this document is a durable implementation requirement. The prior statement that governance is state-relative rather than time-relative is superseded.

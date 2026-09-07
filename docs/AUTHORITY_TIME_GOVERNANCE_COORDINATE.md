# Authority × Time Governance Coordinate — ARA Binding

Status: semantic correction coordinated by `StegVerse-Labs/.github#1154` and `StegVerse-Labs/ara-admissibility-interop#137`.

ARA admissibility evaluates applicability and standing at a governance coordinate:

```text
G = (Authority, Time)
```

State is evaluated at that coordinate. A material state transition may require a new applicability determination because the facts relevant to the requested action changed; State is not a replacement governance coordinate.

Temporal non-causality remains required:

```text
Delta-time -/-> Delta-authority
```

Elapsed time alone does not create, revoke, renew, or transfer authority. This invariant does not demote Time from governance. Time locates the authority determination; clocks, timestamps, freshness, expiry, lease age, and review intervals are observations or policy inputs associated with that coordinate.

The canonical distinction is therefore:

```text
Governance coordinate: (Authority, Time)
Evaluated context: state, identity, delegation, policy, evidence, dependencies, scope, recoverability, etc.
```

Any earlier ARA language stating that governance is state-relative rather than time-relative, or that Time only indexes governance history, is superseded where it conflicts with this coordinate model. The useful state-relative applicability rule is retained as a rule requiring reevaluation of context at the applicable Authority × Time coordinate.

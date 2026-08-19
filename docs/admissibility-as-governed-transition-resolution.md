# Admissibility as Governed State-Transition Resolution

Status: research definition / semantic requirement
Canonical semantic owner: `StegVerse-Labs/ara-admissibility-interop`
Authority effect: NONE
Publication posture: public research proposition, not an external standard or certification claim

## Definition

**Admissibility is the governed resolution of a sought or implicated transition against an operative predecessor state into a realized, observable successor-state relation.**

Admissibility is not synonymous with permission, approval, `ALLOW`, truth, correctness, or successful realization of the sought effect.

For predecessor state `S_i`, a sought or implicated transition candidate `P_i`, operative evidence/context `E_i`, and governing conditions `G_i`, the general form is:

```text
A(S_i, P_i, E_i, G_i) -> (R_i, S_j, Q_ij)
```

where:

- `A` is the admissibility resolution;
- `R_i` is the resolution classification;
- `S_j` is the realized successor state;
- `Q_ij` is the set of relations established, confirmed, contradicted, removed, or newly implicated between `S_i`, `S_j`, and any concerned manifolds.

`R_i` may include `ALLOW`, `DENY`, `REVIEW`, `FAIL_CLOSED`, or other governed resolution states defined by an applicable profile. That enumeration does **not** enumerate the possible successor states.

## Core distinction: resolution classification is not successor state

A sought effect may be:

```text
S_i --candidate--> S_x
```

but a governed resolution may realize:

```text
S_i --DENY--> S_j
```

The sought `S_x` did not occur. The `DENY` resolution nevertheless did occur and therefore produced a real successor state `S_j` with evidence about authority, dependency, applicability, reachability, policy, or another relevant relation.

The same applies to `REVIEW`, `FAIL_CLOSED`, and any other non-`ALLOW` outcome.

Therefore:

```text
DENY != absence of transition
REVIEW != absence of transition
FAIL_CLOSED != absence of transition
```

They are governed transition outcomes with successor-state consequences.

## Observed transitions are already downstream of admissibility

An observation of a realized system transition is evidence that the system has entered a successor state through a governed transition path. Observation must not be conflated with a later vote on whether the transition "really counts."

This does **not** mean every sought effect was allowed. It means the resolved transition itself -- including a `DENY`, `REVIEW`, or `FAIL_CLOSED` resolution -- is part of the admitted state history.

A useful separation is:

```text
candidate / sought transition
    !=
resolved admitted transition
    !=
observation of the resulting state relation
```

## Confirmation is a state change

A transition model must not equate `no value difference` with `no state transition`.

If an observation confirms an already represented proposition or invariant, the object-level value may remain equal:

```text
x_j = x_i
```

while total system state still changes because a new evidentiary or relational fact has been established:

```text
confirmation(x_i, x_j) did not exist before the comparison
```

Accordingly:

```text
Delta(value) = 0
```

does not imply:

```text
Delta(system_state) = 0
```

A confirmed invariant, an unobserved value, and a contradicted value are distinct successor-state conditions.

This is also the basis by which continuity can be established: continuity is not merely "nothing changed"; it is a relation established by observing and relating distinguishable states.

## Minimum transition information

A complete governed transition representation should be able to preserve, where applicable:

1. predecessor state;
2. sought or implicated transition candidate;
3. governing evidence/context and authority basis;
4. resolution classification;
5. realized successor state;
6. what materially changed;
7. what was observed and confirmed invariant;
8. what was contradicted;
9. what emerged or disappeared;
10. uncertainty or confidence changes;
11. dependency changes and confirmed dependency states;
12. authority/applicability changes and confirmations;
13. provenance and observation relations;
14. newly established, altered, or removed relations;
15. newly implicated or de-implicated state-transition manifolds.

These categories are representational requirements, not an exhaustive ontology of successor states.

## Singular-to-multi-manifold requirement

The same semantics apply from a singular state variable through coupled multi-manifold systems.

For a singular value, a transition may distinguish:

```text
changed
confirmed unchanged
not observed
contradicted
```

For a multi-manifold system:

```text
M = {M_1, M_2, ..., M_n}
```

a transition in `M_i` may alter `M_i`, confirm parts of `M_i`, change relations `Q(M_i, M_j)`, and implicate or de-implicate additional manifolds. A complete transition model must preserve those coupled consequences rather than collapsing the event to the primary requested effect.

## Observation and recursive transition systems

Observation is caused by realized state-transition consequences, not by the mere existence of a periodic polling interval.

A periodic carrier may provide synchronization, reference coordinates, freshness, liveness, or signal decomposition. It is not the primitive cause of the observation.

The general recursive form is:

```text
candidate / implicated transition
    -> governed admissibility resolution
    -> realized successor state
    -> observation / relation establishment
    -> updated concerned transition manifold
    -> new candidate / implicated transitions
    -> ...
```

Every newly realized transition again produces successor-state evidence, including outcomes that do not realize the originally sought effect.

## Research consequence

Binary permission models answer a comparatively narrow question:

```text
may requested effect X occur?
```

A state-transition admissibility model asks the more general question:

```text
what governed transition actually occurred, what successor state now exists,
what relations were established or confirmed, and what transition space is now implicated?
```

This changes `DENY`, `REVIEW`, `FAIL_CLOSED`, and confirmation from discarded or secondary outputs into first-class evidence about the reachable transition manifold.

## Proposed invariant

```text
Every governed admissibility resolution that becomes part of system history
must be represented as a successor-state transition, including confirmation
and non-ALLOW outcomes; absence of requested-effect realization is not absence
of transition information.
```

## Non-claims

This document does not claim that the current outcome vocabulary is exhaustive, that every transition requires the same schema fields, or that this research definition is already an external standard. It does not grant runtime, publication, release, credential, Master Record, wallet, or execution authority.

## Implementation consequence

Existing schemas, profiles, validators, observation packets, receipts, and transition-manifold analyses should be evaluated for any assumption that:

- `admitted == ALLOW`;
- `DENY/REVIEW/FAIL_CLOSED == no transition`;
- unchanged object value == unchanged system state;
- observation == periodic polling;
- only the requested effect belongs in the successor-state record.

Any such assumption should be treated as a candidate semantic defect and corrected only through the owning repository's governed implementation and validation path.

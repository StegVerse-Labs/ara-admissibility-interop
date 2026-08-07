# StegGate Constraint Composition v1

Status: review-candidate implementation artifact

## Rule

A derived artifact inherits every presentation constraint of every contributing source. The effective presentation envelope is recomputed at decision time using a profile-declared composition operator for each comparable constraint type.

Every normative composition operator MUST be:

- associative;
- commutative;
- idempotent;
- lower-bounding: the composed result MUST NOT be more permissive than any operand.

A profile that declares an operator failing any property is invalid: `COMPOSITION_PROFILE_INVALID`.

If two constraints are not comparable under the declared vocabulary, evaluation MUST fail closed with `COMPOSITION_NOT_COMPARABLE` unless an explicit admitted signed mapping artifact supplies the cross-vocabulary relation.

## v1 operators

| Constraint type | Operator | Least-permissive result |
| --- | --- | --- |
| recipient entitlement set | intersection | recipients admitted by every source |
| classification level | max under declared ordered lattice | highest / most restrictive level |
| compartment requirements | set union of required compartments | all required compartments |
| embargo release time | max timestamp | latest release time |
| permitted jurisdictions | intersection | jurisdictions permitted by every source |
| boolean requirements | logical AND | every required predicate must hold |
| numeric ceiling | min | lowest ceiling |
| numeric floor | max | highest floor |

The phrase "set union" above applies only to *requirements* such as required compartments. It MUST NOT be generalized to presentation envelopes or recipient entitlement sets.

## Decision-time evaluation

The derivation record binds source references, constraint references, provenance state, and a derivation-time audit hash. The derivation-time hash MUST NOT be used as the sole presentation-admission input.

At presentation or retention decision time, current source constraints are resolved and recomposed. If a required source constraint cannot be resolved, return `FAIL_CLOSED / SOURCE_CONSTRAINT_UNRESOLVABLE`.

## Transitive provenance

Completeness order:

`complete > partial > unknown`

A derived artifact's provenance completeness is the minimum completeness across its own derivation record and the transitive closure of all contributing sources. A laundering hop MUST NOT reset `partial` or `unknown` to `complete`.

## Persistence

The artifact carries authority-relevant provenance and constraint references. A store operation recomputes the effective envelope at decision time. Persisting an artifact MUST NOT erase provenance or broaden the reachable recipient set without explicit competent authority.

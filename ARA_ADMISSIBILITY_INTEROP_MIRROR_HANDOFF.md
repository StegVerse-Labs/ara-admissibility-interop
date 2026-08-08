# ARA Admissibility Interop Mirror Handoff

Repository: `StegVerse-Labs/ara-admissibility-interop`

## Source-of-truth rule

Read this file before continuing repository work. The feature branch `feat/steggate-v46-schema-foundation` carries the StegGate v4.6 integration candidate but does **not** authorize release, tag, deployment, publication, evaluator replacement, standards claims, customer-validation claims, or authority expansion.

## Canonical continuation

- Branch: `feat/steggate-v46-schema-foundation`.
- Draft PR: #1, intentionally open/unmerged.
- Session parent #2: COMPLETE / CLOSED.
- Session consolidation #23: COMPLETE / CLOSED.
- Session archive gate #66: COMPLETE / CLOSED.
- Sequencing guard #8: COMPLETE / CLOSED.
- First real boundary #13: implementation COMPLETE; issue remains administratively open only because the attempted issue-close transport was refused by the execution platform.
- Exact real-boundary candidate binding #65: COMPLETE / CLOSED.
- Deterministic execution profile #72: COMPLETE / CLOSED.
- StegCore Goal 0 coordination #54: COMPLETE / CLOSED.
- Canonical machine inventory: `management/steggate-v46-session-inventory.json`.
- Canonical task state: `management/steggate-v46-implementation.json`.
- First-boundary state: `management/first-boundary-activation.json`.
- Runtime adapter/HTTP continuation: `StegVerse-Labs/StegCore#21` and `StegVerse-Labs/StegCore/STEGCORE_MIRROR_HANDOFF.md` on `main`.
- Complete decision-state reconstruction semantics: `admissibility/decision-state-reconstruction.md`, commit `3fbf916f42189ca6c045c6e3220ae3c2ff021a22`.
- Downstream continuity continuation: `StegVerse-Labs/Continuity#5` and `StegVerse-Labs/Continuity/STEGGATE_CONTINUITY_MIRROR_HANDOFF.md`.

## Claim and convergence state

Originating session/integration claim: `MERGED_INTO_CANONICAL_WORKSTREAM`.

Completed finite ara claims include #10, #12, #30, #31, #61, #62, #63, #64, #65, #67, and #72.

The next runtime transport requirement from closed sequencing guard #8 — `HTTP ALLOW-only / bounded runtime transport` — is **not** an ara runtime implementation task. It converges with existing StegCore issue #21, which already owns API/agent/batch/workflow adapters, `governed_execute()` enforcement, raw-executor bypass refusal, and verified receipt-chain pointer preservation.

`MERGED INTO: StegVerse-Labs/StegCore#21#issuecomment-5224430822`

Ara retains the interoperable execution contract; StegCore owns runtime adapters. Do not create competing runtime code in ara while #21 is active.

## Implemented candidate scope

PR #1 contains core/continuity/presentation/StegCore-interop invariants; transition/derivation/receipt/assurance/evidence-pack/execution-request schemas; least-permissive composition vectors; PP-1 and execution fixtures; `stegverse.jcs.v1`; reason registry; achieved-assurance reporting; content-bounded evidence-pack tooling; Python and independent Node offline verifiers; cross-language parity; deterministic fixture Audit Kit package/report generation and verification; first-real-boundary activation/receipt/observation records; REVIEW-not-admission consequence semantics; deterministic execution-profile semantics; and the complete decision-state reconstruction contract.

Execution-profile surfaces:
- `schemas/execution-request.v1.json`
- `profiles/execution-deterministic.v1.yaml`
- `claims/execution-deterministic.yaml`
- `fixtures/execution/execution-profile-cases.json`
- `invariants/profile-execution.yaml`
- `tools/validate_execution_profile.py`
- `reports/execution-profile-validation.json`

The execution profile requires exact candidate and credential binding, exposed-action containment, parameter-bound containment, downstream capability narrowing/no broadening, governed commit preservation, and non-admission for REVIEW/DENY/FAIL_CLOSED. It does not implement or replace StegCore runtime behavior.

## Complete decision-state reconstruction

Normative design requirement: `admissibility/decision-state-reconstruction.md`.

The governing principle is:

> Admissibility is not merely a prerequisite to execution. The admissibility determination is itself part of the reconstructable state of the governed system.

The interoperable reconstruction surface therefore cannot be limited to successful `ALLOW` paths. Every governed transition attempt must preserve directly or by cryptographically bound reference enough material state to reconstruct:

- the exact candidate and candidate hash;
- evidence, authority/delegation, policy, applicability, freshness, validity, and expiry state actually evaluated;
- each material predicate outcome and unresolved/unknown state;
- obligations, disposition, reason codes, temporal context, topology, approval/admission state;
- commit/non-commit state;
- target/executor outcome;
- observation and reconciliation state.

`ALLOW`, `DENY`, `REVIEW`, and `FAIL_CLOSED` are all evidence-bearing terminal dispositions. `FAIL_CLOSED` is epistemically distinct from `DENY`; `REVIEW` does not authorize execution and any reviewed successor candidate is a new transition rather than a retroactive rewrite.

Reconstruction must preserve three independent planes:

1. decision reality — what StegGate concluded;
2. execution reality — what the target/executor actually did;
3. observed reality — what later evidence establishes.

Those planes may diverge. `DENY + observed effect` is a governance-bypass signal; `ALLOW + committed + missing/divergent observed effect` is a reconciliation divergence. An ALLOW receipt alone does not prove complete mediation or coverage.

PR #1 comment `5224765644` records the cross-repository installation. Runtime counterpart: `StegVerse-Labs/StegCore/docs/DECISION_STATE_RECONSTRUCTION.md`, commit `b10ca617d4de3e35d992c9252234f833e54e8655`; StegCore issue #21 durable extension comment `5224765289`. Continuity counterpart: `StegVerse-Labs/Continuity/STEGGATE_CONTINUITY_MIRROR_HANDOFF.md`, `docs/STEGGATE_DECISION_STATE_RECONSTRUCTION.md`, and issue #5.

## StegCore runtime boundary

Live StegCore state supersedes earlier branch-only references:

- PR #18 `Add accountable commit-coherence boundary`: MERGED; merge commit `5f78b489c51a99af7b76b0b9e3979da820c9a296`.
- Dedicated PR #18 acceptance run `29308236624`, job `87006244615`: SUCCESS, 7/7 commit-coherence tests.
- Historical generic repo test run `29308236597`, job `87006323507`: FAILED during collection because `tests/test_stegverse_spec_conformance.py` could not import the `scripts` module. This is not represented as an all-green full-repository state.
- PR #20 `Bind production runtime to commit coherence`: MERGED; merge commit `8d5178507c86efe98c359f957ab20475e55ca9f2`.
- `StegVerse-Labs/StegCore@main:src/stegcore/runtime.py#governed_execute` is the production mutation boundary and invokes an injected executor only after admissibility and commit coherence both permit execution.
- StegCore issue #21 is the canonical owner for reusable governed adapters and the transferred HTTP/API transport requirement plus runtime decision-state production.
- StegCore handoff reconciliation commit: `865e23945060343d8c28f322d315d88d56746dce`.
- Decision-state runtime contract commit: `b10ca617d4de3e35d992c9252234f833e54e8655`.
- StegCore handoff decision-state update: `345a11507783b7614d597ad5f67dad6bb46ba15d`.

## First real-boundary evidence

- candidate: `rb-ara-taskstate-001`
- canonical hash: `sha256:a74ef1ce97953e6661975f68f4a7ae53c1483b4006076279191637800b4326f3`
- admitted consequence: `management/steggate-v46-implementation.json:first_real_boundary_pilot=COMPLETE`
- consequence commit: `48b7c7f68b8dc17dc3b398b682ff4342755ab0da`
- observation: `real-boundary/consequence-observation.json` -> `observation_result=MATCH`, `observed_target_value=COMPLETE`
- post-consequence Schema Foundation `31237866865` / `93053670769`: SUCCESS
- post-consequence Repo Check `31237866861` / `93053670786`: SUCCESS
- exact Python/Node candidate hash agreement: true
- mutated candidate: DENY / `CANDIDATE_BINDING_MISMATCH`
- missing authority: FAIL_CLOSED / `CONSEQUENCE_AUTHORITY_MISSING`
- retry/reconstruction stable: true
- authority effect: false

## Deterministic execution-profile evidence

Validated branch head: `63af5b2568aa206e571f53fb172ab840fe97b7cc`.

- Schema Foundation `31238487769` / `93055293539`: SUCCESS.
- Repo Check `31238487749` / `93055293490`: SUCCESS.
- baseline: 35 invariants, 68 fixture IDs, 74 fixture references, 32 reason codes, 6 schemas — PASS.
- execution cases: 7 total — 1 ALLOW, 5 DENY, 1 FAIL_CLOSED.
- six execution invariants; four execution claims.
- exact candidate binding: true.
- exact credential binding: true.
- capability narrowing: true.
- governed commit required: true.
- real-boundary observation consumed: true.
- StegCore runtime owner preserved: true.
- artifact `steggate-audit-kit-fixture-001`: ID `9016228721`, 7555 bytes, digest `sha256:c2ae3df5efd11cadd707b441bbf522c8a21dbc7f3649f76b62509fbf68fae8a5`.
- receipt commit: `b098448869b7b04ea126a119ae232b9fa489d561`.

The historical hosted-green execution-profile evidence predates the new complete decision-state reconstruction contract. It remains valid for its stated scope but does not by itself validate the newly documented full matrix/effect/reconciliation surface.

## Remaining project work and owners

- HTTP/API and other governed adapters plus runtime decision-state production: StegCore #21. Machine release condition now includes committed adapter code + deterministic dedicated hosted CI proving callback unreachability before admissibility+coherence ALLOW, preservation of bound observation/receipt-pointer fields, and durable decision-state binding across executing and non-executing outcomes.
- Continuity reconstruction schemas/fixtures/verifier: `StegVerse-Labs/Continuity#5` (`STEGGATE-CONT-001`).
- Ara canonical schema evolution for complete matrix/decision/effect/reconciliation fields remains an interop task when field-level schema changes are activated; the current contract is normative documentation and must not be misrepresented as already schema-validated.
- runtime/capability/atomicity/ledgers/payment/conformance: remain under the named ara/StegCore substantive issues recorded in `management/steggate-v46-session-inventory.json`.
- Presentation, continuity, protocol/federation, HIL, portable-node and adapter later lanes: remain under their named issue dependencies.
- Site/Publisher/admissibility-wiki/stegguardian-wiki propagation: not authorized by this PR and must not be implied from source validation.

## Automation and collision controls

`.github/workflows/steggate-schema-foundation.yml` automatically validates invariant/reason/schema/fixture coverage, canonicalization, achieved assurance, Audit Kit reconstruction and Python/Node parity, first-boundary state/observation, REVIEW-not-admission semantics, and deterministic execution-profile semantics.

The newly documented decision-state reconstruction requirement is not yet represented by a dedicated ara schema/fixture validator. Until that implementation exists, documentation installation must not be promoted to schema-level completion.

StegCore issue #21 owns its own required non-interactive adapter CI. Missing adapter evidence remains incomplete rather than being silently promoted from ara tests.

## Session consolidation

All unique StegGate v4.0-v4.6 requirements represented in the originating session plus the complete decision-state reconstruction insight are now implemented where documentation is the correct current artifact, explicitly superseded, or durably assigned to canonical issue/handoff/task-state owners. No continuation requires reconstructing the originating chat.

`MERGED INTO: StegVerse-Labs/ara-admissibility-interop#1; admissibility/decision-state-reconstruction.md; ARA_ADMISSIBILITY_INTEROP_MIRROR_HANDOFF.md; management/steggate-v46-session-inventory.json; management/steggate-v46-implementation.json; management/first-boundary-activation.json; reports/execution-profile-validation.json; StegVerse-Labs/StegCore#21#issuecomment-5224765289; StegVerse-Labs/StegCore/STEGCORE_MIRROR_HANDOFF.md; StegVerse-Labs/StegCore/docs/DECISION_STATE_RECONSTRUCTION.md; StegVerse-Labs/Continuity#5; StegVerse-Labs/Continuity/STEGGATE_CONTINUITY_MIRROR_HANDOFF.md; StegVerse-Labs/Continuity/docs/STEGGATE_DECISION_STATE_RECONSTRUCTION.md.`

## Completion percentages for originating session slice

Denominator = all unique session goals represented in `management/steggate-v46-session-inventory.json`; a goal counts complete for archival when implemented/validated, explicitly superseded, or durably transferred to a named canonical owner with release condition.

- session task/consolidation completion: 9/9 = 100%.
- execution-profile developed-file completion: 8/8 = 100%.
- execution-profile validation: 5/5 = 100%.
- execution-profile integration: 4/4 = 100%.
- originating-session consolidation: 9/9 = 100%.
- decision-state reconstruction documentation/ownership transfer: COMPLETE.
- decision-state field-level schema/runtime/continuity implementation: ACTIVE in the named ara/StegCore/Continuity workstreams; not complete.
- source PR merge/release/publication/deployment: not claimed and not an archival dependency.

## Archive condition

SATISFIED for this insight transfer: deleting or archiving the chat does not remove any unique reconstruction requirement, authority boundary, evidence pointer, claim, next task, or machine release condition. Project work remains active in canonical repository-native workstreams, especially StegCore #21 and Continuity #5, but this session owns no unique information that remains only in chat.

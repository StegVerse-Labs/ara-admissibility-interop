# StegGate Governed Transition Protocol Mirror Handoff

## Authority and relationship to repository handoff

Repository: `StegVerse-Labs/ara-admissibility-interop`
Branch: `feat/steggate-v46-schema-foundation`
Draft PR: `#1`
Goal ID: `STEGGATE-PROTOCOL-001`

`ARA_ADMISSIBILITY_INTEROP_MIRROR_HANDOFF.md` remains the canonical repository-level handoff. This file is the specialized authoritative continuation record for the governed-transition protocol workstream. It does not supersede the root repository handoff and must be read with it.

## Originating session goal

Convert the StegGate product review and the portable StegVerse-node architecture into a durable, implementation-neutral governed-transition protocol while avoiding duplication of the active StegCore runtime-adapter lane.

The session concluded that:

- StegVerse is the user/entity-facing governance ecosystem;
- StegGate is the consequence-adjudication runtime;
- a separate governed-transition protocol is needed for local, organizational, federated, and chained use;
- sender admission never equals receiver admission;
- downstream authority may narrow but never silently broaden;
- human approval must bind to the canonical candidate;
- verification must resolve trust outside the evidence pack;
- coverage/completeness must be evidenced;
- JCS canonicalization must not perform Unicode normalization;
- RFC 9396 supplies fine-grained authorization-detail semantics but is not itself a signed delegation credential;
- independent conformance, not analogy or marketing, is the protocol proof target.

## Authoritative files

- `ARA_ADMISSIBILITY_INTEROP_MIRROR_HANDOFF.md`
- `STEGGATE_PROTOCOL_MIRROR_HANDOFF.md`
- `admissibility/steggate-governed-transition-protocol-v1.md`
- `management/steggate-protocol-session-inventory.json`
- existing v4.6 schema/invariant/runtime-consumer state referenced by the root handoff

## Canonical owner and active claim

Task ID: `STEGGATE-PROTOCOL-001`
Canonical owner: `StegVerse-Labs/ara-admissibility-interop#1`
Role: canonical interop/schema integration only
Claim state: `CLAIMED_FOR_INTEGRATION`
Claim creation time: `2026-08-08T08:43:00-05:00`

Release condition:

> Versioned protocol schemas, RFC 8785/JCS golden vectors, authority-narrowing fixtures, intent-binding fixtures, discovery/trust profiles, independent verifier evidence, and second-implementation conformance are committed and hosted-green, or each remaining item is transferred to a named durable owner with a machine-observable release condition.

Expected evidence:

- schema/profile commits;
- deterministic validator outputs;
- hosted workflow runs/jobs;
- conformance artifacts;
- independent implementation evidence;
- updated task inventory and handoff.

Collision boundaries:

- `StegVerse-Labs/StegCore#21` exclusively owns reusable runtime adapters, HTTP/API bounded transport, runtime receipt-chain binding, and runtime decision-state production while its claim remains active.
- `StegVerse-Labs/Continuity#5` decision-state consumer work is complete and must not be duplicated.
- `StegVerse-Labs/Governance` retains its existing evidence-provider/governance boundary.
- No Site/Publisher/wiki propagation is authorized by this protocol branch.

## Current implementation state

### Already complete before this session

The root handoff records and hosted evidence establish:

- first real bounded consequence;
- exact candidate binding;
- deterministic execution profile;
- REVIEW-not-admission semantics;
- Audit Kit evidence pack and offline verification;
- Python/Node parity for the existing scope;
- complete decision-state reconstruction for ALLOW, DENY, REVIEW, and FAIL_CLOSED;
- StegCore commit-coherence and production governed mutation boundary;
- Continuity decision-state reconstruction consumer.

These remain authoritative for their stated scopes and are not reimplemented here.

### Completed by this session

1. Installed `admissibility/steggate-governed-transition-protocol-v1.md` at commit `f5715e98f6edfa438a3d97456dc47f13e34d1803`.
2. Installed `management/steggate-protocol-session-inventory.json` at commit `3f869c142b2828054d9ce79effa9ab59983030e9`.
3. Transferred all unique product-review / portable-node protocol requirements into repository-native state.
4. Corrected JCS semantics: no Unicode NFC/NFD normalization inside RFC 8785 canonicalization.
5. Corrected RFC 9396 usage: authorization-detail semantics require a separately bound/signed authority proof for portable delegation claims.
6. Added monotonic authority narrowing as a required protocol invariant.
7. Added local, organizational, federated, and chained deployment semantics.
8. Added discovery, trust-profile, protocol-versioning, coverage, idempotency, intent-binding, and independent-conformance requirements.
9. Explicitly bounded the TCP/IP comparison as an interoperability-role analogy rather than a standards claim.

## Incomplete work and exact owners

### Protocol executable delta — ara PR #1

Owner: `StegVerse-Labs/ara-admissibility-interop#1`
State: `CLAIMED_FOR_INTEGRATION`

Required implementation locations, after current files are inspected for reuse:

- `schemas/` — governed-transition, discovery, trust/assurance, multi-gate narrowing structures;
- `profiles/` — JCS/application/authority profiles;
- `fixtures/` — canonicalization, intent-binding, authority-narrowing, protocol-version/trust negative cases;
- `invariants/` — monotonic narrowing and any nonduplicative protocol invariants;
- validators/reports consistent with the existing schema-foundation validation architecture.

Do not add duplicate reason codes or invariants before inspecting the current registry.

### Runtime adapters and bounded HTTP/API transport — StegCore #21

Owner: `StegVerse-Labs/StegCore#21`
State: `MERGED_INTO_CANONICAL_WORKSTREAM / CLAIMED_FOR_IMPLEMENTATION`

Release condition is defined in `StegVerse-Labs/StegCore/STEGCORE_MIRROR_HANDOFF.md` and issue #21. This ara workstream may publish stable protocol inputs for #21 to consume but must not implement a competing runtime lane.

### Second independent implementation

Owner: ara PR #1 until transferred to an exact independent repository.
State: `BLOCKED`
Machine-observable release condition: v1 canonical schemas/golden vectors hosted-green.
Next action after release: assign and install a second implementation that shares vectors but no runtime/canonicalization code.

### Portable StegVerse node integration

Owner: not yet assigned because the canonical portable-node runtime repository must be resolved from its live handoff rather than inferred from the Site presentation branch.
State: `BLOCKED`
Machine-observable release condition: core transition/discovery/trust profiles hosted-green plus canonical portable-node runtime owner resolved from a live handoff.

### Public propagation

Destinations when authorized:

- `StegVerse-Labs/Site`
- `GCAT-BCAT-Engine/Publisher`
- `StegVerse-Labs/admissibility-wiki`
- `stegguardian-wiki` under its live owner

State: `BLOCKED_BY_RELEASE_AUTHORITY`
Release condition: applicable handoffs authorize propagation after implementation and conformance evidence exists.

## Validation commands / paths

Use the repository's existing schema-foundation and repo-check validation architecture. Existing authoritative paths include:

- `.github/workflows/steggate-schema-foundation.yml`
- repo check workflow recorded by the root handoff
- protocol-specific validators added under the existing tool/validator conventions rather than creating an unrelated CI system.

Do not claim hosted validation for new protocol files until workflow runs/jobs are directly inspected.

## Cross-repository dependencies

- `StegVerse-Labs/StegCore#21` — runtime adapters/producer semantics;
- `StegVerse-Labs/Continuity#5` — completed decision-state reconstruction consumer;
- `StegVerse-Labs/Governance` — policy/evidence-source governance boundaries and future regulatory mappings;
- StegID / Continuity contracts — continuity minting/verification, not StegGate authority;
- Master Records — custody only under its own live contracts;
- portable-node runtime repository — to be resolved before node integration;
- Site/Publisher/wikis — release/publication projection only after authorization.

## Automation and machine-owned continuation

Existing ara schema-foundation/repo-check workflows remain the machine validation lane. Do not create a parallel workflow system unless existing dispatchers cannot express the protocol validators.

The protocol inventory persists claim state, release conditions, next executable actions, collision boundaries, and archival dependencies in `management/steggate-protocol-session-inventory.json`.

StegCore issue #23 separately owns the runtime-validation evidence-persistence defect described in the root handoff. It does not transfer StegCore #21 runtime ownership to this protocol session.

## Session consolidation

Session goal denominator: 9 durable goals in `management/steggate-protocol-session-inventory.json`.

Current transfer state:

- session-specific requirements transferred or completed: 9/9;
- chat-only unique requirements remaining: 0;
- runtime adapter goal merged into StegCore #21;
- protocol executable delta retained by ara PR #1;
- portable-node integration blocked with explicit release condition;
- public propagation blocked by release authority.

MERGED INTO: `StegVerse-Labs/ara-admissibility-interop/admissibility/steggate-governed-transition-protocol-v1.md`; `management/steggate-protocol-session-inventory.json`; this handoff; `StegVerse-Labs/StegCore#21` for runtime continuation.

## Completion percentages

These percentages are for `STEGGATE-PROTOCOL-001`, not the already-completed v4.6 decision-state session slice.

- task transfer/completion: 9/9 = 100% durable assignment;
- developed protocol-delta files: 3/12 = 25% after this handoff (requirements, inventory, specialized handoff); existing v4.6 foundation is reusable but not counted as completing unimplemented v3 protocol delta files;
- protocol-delta validation: 0/6 acceptance groups until new-commit hosted runs and future executable fixtures are inspected;
- integration: 2/5 durable owner integrations currently established (ara canonical owner, StegCore runtime owner); Continuity/Governance existing dependencies are recognized but the new node/federated protocol integration is not activated;
- goal activation: 30% review-to-executable protocol activation;
- session consolidation: 9/9 = 100% once this handoff is committed and branch validation state is inspected.

## Archive conditions

The originating chat session becomes archive-safe when:

1. the requirements file, machine inventory, and this specialized handoff are committed;
2. the resulting branch validation state is inspected and any failure caused by these files is either repaired or durably assigned;
3. no unique session requirement remains only in chat;
4. runtime work remains owned by StegCore #21 rather than this session;
5. all unimplemented protocol tasks have durable owners/release conditions in the inventory.

Project incompleteness does not by itself retain the chat once those conditions are satisfied.

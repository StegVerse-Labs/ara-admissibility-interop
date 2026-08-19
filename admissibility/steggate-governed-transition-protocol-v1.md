# StegGate Governed Transition Protocol v1 — Requirements

Status: review-to-implementation requirements
Goal ID: STEGGATE-PROTOCOL-001
Canonical interop owner: StegVerse-Labs/ara-admissibility-interop
Branch: feat/steggate-v46-schema-foundation
Runtime owner: StegVerse-Labs/StegCore#21 for adapters/runtime producer semantics

## Purpose

This document durably transfers the portable-node / StegGate architecture developed during product review into the canonical admissibility interop workstream without duplicating StegCore runtime ownership.

StegVerse is the user/entity-facing governance ecosystem. StegGate is the consequence-adjudication runtime. This protocol defines implementation-neutral governed-transition semantics so local nodes, organizational gateways, and independently operated counterparties can exchange bounded authority, evidence, decisions, and receipts without adopting the same application stack.

This document is not a standards-body claim, release claim, deployment claim, customer-validation claim, legal-compliance claim, or authorization to expand runtime authority.

## Core declaration

Networks already provide transport. StegGate addresses a separate interoperability problem: whether an exact machine-originated transition is admissible before consequence and how that determination can be independently reconstructed afterward.

StegGate is not "the TCP/IP of AI" and must not be presented as an industry standard until independent adoption and external standards processes justify such a claim.

## Canonical layer separation

1. StegVerse Node — user/entity-facing identity, keys, consent, delegations, preferences, evidence, receipts, applications, agents, and gateway configuration.
2. StegGate Governed Transition Protocol — implementation-neutral transition, authority, evidence, admission, commit, coverage, and receipt semantics.
3. StegGate Runtime — authority resolution, policy/evidence evaluation, ALLOW/DENY/REVIEW/FAIL_CLOSED production, commit binding, receipt generation, and reconstruction.
4. Execution/transport — HTTP, MCP, A2A, queues, local IPC, device protocols, and target systems.

Transport reachability, provider output, UI intent, SDK validation, or receipt presence must not independently create execution authority.

## Required deployment modes

### Local

A StegVerse node may invoke a local StegGate without network dependency. The protocol semantics remain identical to remote deployment.

### Organizational

A personal, agent, service, or team node may invoke an organizational StegGate. Effective authority is the intersection of portable node authority, organizational delegation, resource policy, applicable evidence, and transition constraints.

### Federated

A sender-side StegGate may attest to what it admitted, but sender admission never becomes receiver admission. A receiver-side StegGate independently evaluates the transition under its own authority and policy.

### Chained

Multiple independently operated gates may successively constrain a transition. Each boundary must preserve its input authority reference and its effective output authority reference.

## Monotonic authority narrowing invariant

A downstream governance boundary MAY preserve or narrow effective authority. It MUST NOT silently broaden authority beyond the authenticated upstream grant.

For authority sets A0..An, each downstream effective authority must remain a subset of the authenticated authority presented to that boundary.

Permitted narrowing includes lower monetary ceilings, shorter TTL, narrower resources, stronger evidence requirements, added review, or stricter receiver policy.

Examples of prohibited silent broadening:

- $500 ceiling -> $5,000 ceiling
- read -> write
- vendor A -> any vendor
- one resource -> all resources
- one hour -> indefinite

If broader authority is required, a new authority artifact from an entity capable of granting the broader authority is required.

Canonical existing implementation mapping discovered during integration:

- invariant: `SG-CORE-004` in `invariants/core.yaml`;
- broadening reason: `AUTHORITY_BROADENING`;
- incomparability reason: `AUTHORITY_NOT_COMPARABLE`;
- fixtures: `core.allow.authority_narrowing`, `core.deny.authority_broadening`, `core.fail_closed.authority_not_comparable`;
- execution profile also uses `AUTHORITY_BROADENING` for capability broadening.

Do not introduce a duplicate `AUTHORITY_BROADENING_ATTEMPT` reason unless a future version proves materially different semantics and explicitly versions the registry.

## Decision vocabulary

Canonical v1 decision values used by the current decision-state interop are:

- ALLOW
- DENY
- REVIEW
- FAIL_CLOSED

REVIEW is not admission and approval after REVIEW creates a new authority artifact and a new transition.

ADMISSION_LAPSED should be modeled as lifecycle state unless the canonical decision-state owner explicitly decides otherwise.

## Candidate and intent binding

Candidate binding is topology-dependent.

### Inline terminating proxy

Evaluation and target invocation are adjacent. The primary control is structural bypass prevention, preferably credential brokering. Candidate equality alone is not the differentiator.

### Split admission / external commit

The admission token must be single-use, TTL-bound, and cryptographically bound to the candidate hash. The target or receiver-side enforcement component must verify the admission before consequence.

### Deferred human review

The artifact rendered to the human and the artifact hashed for admission must derive from the same canonical candidate. Human approval must cryptographically bind the candidate hash and rendered-form hash. Material fields required by policy must be visible in the deterministic rendering; omission is FAIL_CLOSED.

## Canonicalization correction and existing implementation mapping

Use RFC 8785 JCS-compatible deterministic JSON canonicalization semantics as implemented by the canonical repository profile.

StegGate JCS implementations MUST NOT perform Unicode normalization inside the canonicalizer. RFC 8785 requires parsed string content to be preserved as-is. Any application-level normalization must occur before candidate construction and must be explicitly profiled.

The current repository already enforces this through:

- `SG-CORE-009` in `invariants/core.yaml`;
- `fixtures/canonicalization/vectors.json`, including `canonical.unicode_no_normalization`;
- `tools/canonicalize_steggate.py`;
- `tools/canonicalize_steggate_node.mjs`;
- `tools/validate_canonicalization_vectors.py`;
- `tools/validate_track1b_parity.mjs`.

Required profile properties:

- duplicate object member names rejected;
- JCS-compatible input;
- strings preserved as parsed;
- deterministic property ordering;
- no floating-point representation for money in governed application profiles;
- canonicalization profile recorded in relevant receipts;
- hash algorithm identifier recorded;
- canonicalizer profile/build mismatch at commit fails closed.

Do not create a competing canonicalizer; extend the existing golden vectors when new protocol field classes require coverage.

## Authorization-details correction

RFC 9396 Rich Authorization Requests may be used as the semantic vocabulary for fine-grained authorization_details. RFC 9396 is not itself a signed portable delegation credential.

The v1 ara profile is `profiles/authority-rar-bound.v1.yaml`.

A StegGate authority profile must bind authorization details to independently resolvable authority evidence, for example a signed COSE/JWS authority artifact, an OAuth token with cryptographically bound authorization details, or another approved profile.

The authority proof must establish at minimum:

- grantor identity;
- delegate/actor identity;
- proof the grantor may grant the scope;
- allowed actions/resources/argument constraints;
- validity interval;
- revocation semantics;
- key binding;
- policy reference where required.

## Actor identity

A free-form actor string is not sufficient attribution. Transition requests require a subject identifier plus cryptographic key binding and proof of possession or equivalent attested identity evidence. Accepted profiles may include SPIFFE/SPIRE, OAuth-bound identity, DID-based identity, device-attested keys, or StegID profiles.

StegGate consumes identity evidence; it does not become a universal identity provider.

## Evidence snapshot determinism

Every input that influenced a decision must be included in the evidence pack or hash-referenced to an immutable artifact.

The evaluator must consume a frozen EvidenceSnapshot. External evidence resolution occurs before evaluation and is separately receipted. No un-snapshotted external read may influence a replayable decision.

A missing required snapshot or unresolved required evidence is FAIL_CLOSED.

## Trust anchor and verification

The verifier must be distributed independently of the evidence pack. The pack may state verifier version/digest and trust-anchor references, but must not make a key embedded solely in the pack the root of trust.

Existing ara assurance surfaces already distinguish identity, signatures, trust anchor, source evidence, and capability construction and refuse assurance overclaim. The protocol-specific L0-L3 packaging remains an additive delta and must reuse rather than replace those semantics.

Target assurance profile semantics:

- L0 deployment-signed: deployment key resolved independently;
- L1 timestamped: L0 plus RFC 3161 or equivalent trusted timestamp evidence;
- L2 transparency-anchored: L1 plus independently operated transparency inclusion evidence;
- L3 receiver/witness-attested: L2 plus independently controlled receiver or witness countersignature.

Assurance level strengthens provenance/observation claims. It does not prove truth, legality, policy wisdom, or regulatory compliance.

Use an established signature envelope such as COSE_Sign1 or a separately profiled detached JWS; do not invent a bespoke cryptographic envelope.

## Coverage and completeness

A valid receipt does not by itself prove that all consequential actions were mediated.

Every deployment must declare a coverage mode, such as:

- structural credential-brokered mediation;
- target-side admission verification;
- observational reconciliation against target activity.

Hash-chained decision logs, signed checkpoints, sequence numbers, gap detection, and fork detection are required for audit-grade completeness claims.

A reconciliation delta is a finding and must not be normalized into success.

The existing decision-state reconstruction contract already preserves that an ALLOW receipt alone does not prove complete mediation/coverage; the protocol envelope adds explicit coverage-mode semantics rather than changing that invariant.

## Replay protection and idempotency

Transition replay prevention and consequence idempotency are distinct requirements.

Each admitted transition needs a unique transition/admission identifier. Consequential target calls should carry an idempotency key where the target supports it. If the target does not support idempotency, policy must explicitly classify the retry/double-consequence risk.

## Governed transition envelope — canonical additive schema

`schemas/governed-transition-envelope.v1.json` extends the existing `schemas/transition.v1.json` semantics without replacing it.

The additive envelope represents:

- protocol/schema version;
- existing transition object;
- topology;
- origin context;
- candidate canonicalization/hash binding;
- authority chain;
- evidence snapshot reference;
- requested/achieved assurance;
- coverage mode;
- idempotency posture;
- gate path;
- critical extensions.

Adapter-specific fields must not become required core protocol semantics unless they are consequence-governance primitives.

## Multi-gate receipt semantics

Each gate in a federated/chained path must preserve:

- gateway identity;
- input authority hash/reference;
- effective authority hash/reference;
- whether narrowing occurred;
- which material constraints changed;
- confirmation that no authority broadening occurred;
- decision state;
- candidate hash where applicable;
- prior gate/receipt pointer where applicable.

If effective authority cannot be proven to remain within authenticated input authority, the transition is DENY when broadening is positively established and FAIL_CLOSED when comparability cannot be established, consistent with the existing canonical core fixtures.

## Discovery profile — implemented additive schema

`schemas/gateway-discovery.v1.json` represents:

- gateway identity;
- protocol versions;
- decision states;
- canonicalization profiles;
- identity profiles;
- authority profiles;
- assurance profiles;
- trust-anchor references;
- endpoint or local-runtime bindings;
- optional chain-depth and critical-extension declarations.

A network representation may use a `.well-known` resource, but the core protocol must also support local/offline discovery/configuration.

## Protocol versioning

Every protocol object must identify its major profile/version.

Required behavior:

- unsupported major version -> FAIL_CLOSED;
- unknown required semantics -> FAIL_CLOSED;
- unknown extension may be ignored only when explicitly marked non-critical;
- critical extensions must be understood or the transition fails closed.

`fixtures/protocol/governed-transition-cases.json` and `tools/validate_governed_transition_protocol.py` provide the initial executable unsupported-major refusal case.

## Privacy and selective disclosure

Bare SHA-256 hashing of low-entropy fields is not sufficient privacy protection.

Profiles should use salted commitments and/or Merkleized field commitments so a party can selectively reveal fields while keeping a root commitment bound to the full candidate. Raw PII and large evidence may remain externally referenced where policy permits.

Protocol semantics should distinguish data that is hidden, committed, disclosed, or externally referenced.

This remains an unimplemented additive protocol delta unless an existing canonical privacy/commitment profile is later identified and adopted.

## Availability doctrine

Consequential StegGate boundaries must not silently fail open.

Permitted resilience patterns include:

- HA runtimes;
- pre-resolved evidence snapshots;
- narrow pre-admission envelopes;
- queue-and-hold;
- explicitly declared actions outside this governed boundary.

An explicitly ungoverned non-consequential action class is not the same as fail-open and must not be counted in coverage claims for a governed class.

## Conformance requirement and existing evidence

Protocol credibility requires executable conformance, not prose alone.

Existing hosted-green independent evidence already includes:

- Python and Node canonicalizers sharing vectors but not implementation code;
- independent Python and Node Audit Kit verification;
- Track 1B parity proving identical canonical hashes and verifier decisions for the existing scope.

The new protocol-specific second implementation must extend this independent-conformance property to governed-transition envelope/discovery semantics; existing parity is reused as foundation but not overstated as complete proof of the new envelope.

STEGGATE-PROTOCOL-001 activation target remains:

1. versioned canonical schemas;
2. JCS-correct golden vectors;
3. positive and negative decision vectors;
4. monotonic-authority-narrowing vectors;
5. intent-binding vectors or an explicitly adopted existing equivalent;
6. trust-anchor verification vectors;
7. independent verifier distribution;
8. second implementation for the new protocol semantics without shared runtime/canonicalization code;
9. hosted conformance success.

Independent conformance does not authorize the claim "industry standard".

## Current executable protocol validation

`tools/validate_governed_transition_protocol.py` validates the additive v1 delta and is wired into `.github/workflows/steggate-schema-foundation.yml`.

Hosted evidence at head `5ebeac84bda82b88df7beaa5f3ba680de9d0ebba`:

- StegGate Schema Foundation run `31260489746`: SUCCESS;
- validation job `93110434515`: SUCCESS;
- Repo Check run `31260489761`: SUCCESS.

The same hosted run re-proved the existing JCS vectors, assurance overclaim refusal, Audit Kit verification, Python/Node parity, first real boundary, REVIEW consequence separation, deterministic execution profile, and complete decision-state reconstruction.

## Required public claim discipline

Permitted when directly supported:

- implementation-neutral governed-transition protocol;
- reference implementation;
- independent conformance demonstrated for the explicitly named tested scope;
- portable execution-governance evidence;
- commit-time admissibility;
- local, organizational, and federated deployment profiles as protocol semantics.

Prohibited without independent evidence/authority:

- "the TCP/IP of AI";
- industry standard / universal standard;
- regulator approved;
- AI Act compliant;
- certified;
- guarantees safety;
- proves truth;
- prevents all unauthorized AI action.

## Repository ownership and collision boundaries

Canonical interop/schema requirements: StegVerse-Labs/ara-admissibility-interop.

Policy semantics and regulatory mappings: StegVerse-Labs/Governance where assigned by its handoff.

Runtime adapters, HTTP/API transport, runtime decision-state producer, receipt-chain runtime binding: StegVerse-Labs/StegCore#21. This document MUST NOT create a competing runtime lane.

Continuity minting/verification: StegID / Continuity contracts. StegGate must not silently mint continuity receipts.

Custody: Master Records only under its own live contracts.

Public propagation: Site, Publisher, admissibility-wiki, stegguardian-wiki only after release/publication gates authorize it.

## Session-originating requirements transferred

The following session-specific insights are durable here and in the specialized handoff/inventory:

- StegVerse Node is the user/entity-facing interface to StegGate;
- StegGate may be local, organizational, or federated;
- independent nodes may use the same governed-transition semantics without adopting the same application stack;
- sender admission never equals receiver admission;
- downstream authority may narrow but never silently broaden;
- the TCP/IP comparison is a bounded interoperability-role analogy, not a standards claim;
- JCS must not NFC-normalize strings;
- RFC 9396 supplies authorization-detail semantics but is not standalone signed delegation proof;
- protocol discovery/versioning/trust profiles are required;
- second-implementation conformance is the proof target.

MERGED INTO: StegVerse-Labs/ara-admissibility-interop/admissibility/steggate-governed-transition-protocol-v1.md; STEGGATE_PROTOCOL_MIRROR_HANDOFF.md; management/steggate-protocol-session-inventory.json.

## Activation boundary

Requirements transfer and the current additive protocol slice are implemented and hosted-green for their stated scope. Full STEGGATE-PROTOCOL-001 activation is not claimed.

Remaining activation deltas are durably assigned in `management/steggate-protocol-session-inventory.json`, principally L0-L3 trust-profile completion, protocol-specific second-implementation conformance, portable-node integration after its runtime owner is resolved, and release-gated publication.

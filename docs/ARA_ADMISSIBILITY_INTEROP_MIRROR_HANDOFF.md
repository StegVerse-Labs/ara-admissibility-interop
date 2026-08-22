# ARA Admissibility Interop Mirror Handoff

## Canonical activation state

```text
repository: StegVerse-Labs/ara-admissibility-interop
canonical_branch: main
steggate_integration_merge_commit: 2a0ada472f7a3cc059961cb9af5baadecb5e0c9b
merged_pull_request: #1
validated_integration_head: 523868fae5f5f8584547929284ccb98db1c56e05
activation_manifest: management/activation-surface.json
workflow_governance: management/workflow-governance.json
release_owner_issue: #121
runtime_owner: StegVerse-Labs/StegCore
continuity_owner: StegVerse-Labs/Continuity
credential_authority: TV/TVC
state: INTEGRATED_NOT_RELEASED
```

This file is the heartbeat-target handoff and is activation-authoritative together with `management/activation-surface.json`. Historical feature-branch handoffs, candidate records, receipts, task snapshots, and validation reports remain replay evidence only; they MUST NOT override current `main` state.

## Integrated StegGate state

PR #1 is merged. The conflict-resolved integration head `523868fae5f5f8584547929284ccb98db1c56e05` passed both required activation validators before merge:

```text
Repo Check run 32280935639: SUCCESS
StegGate Schema Foundation run 32280935596: SUCCESS
StegGate integration merge commit: 2a0ada472f7a3cc059961cb9af5baadecb5e0c9b
```

The merged implementation includes the Audit Kit/schema foundation, deterministic execution profile, complete decision-state reconstruction, governed-transition protocol surfaces, candidate/credential/capability binding, first bounded consequence evidence, and independent conformance evidence.

The post-merge activation-surface reconciliation was separately validated with both activation-authoritative workflows before integration. That reconciliation does not alter the historical StegGate integration identity above.

## Runtime and continuity convergence

```text
StegCore issue #21: COMPLETE / CLOSED
StegCore PR #55: MERGED
StegCore governed adapter conformance: SUCCESS
Continuity issue #5: COMPLETE / CLOSED
Continuity Python 3.11 + 3.12 validation: SUCCESS
```

ARA owns interoperable schemas/profiles/semantic fixtures. StegCore owns runtime decisions/adapters/execution reachability. Continuity owns preservation/reconstruction. No ARA state may silently reacquire those transferred authorities.

## Activation surface

The workflow ceiling is enforced by `management/workflow-governance.json` and `tools/check_workflow_governance.py`. The repository baseline is no more than two workflows without discrete exceptions. Repo Check fails if an undeclared workflow appears, an exception disappears, or an exception grants activation/release authority.

The two baseline activation-authoritative workflows are:

```text
.github/workflows/repo-check.yml
.github/workflows/steggate-schema-foundation.yml
```

The three existing service workflows are admitted only through discrete non-authority exceptions:

```text
ARA-WF-EX-001  .github/workflows/docs-pages.yml
ARA-WF-EX-002  .github/workflows/deployment-notification.yml
ARA-WF-EX-003  .github/workflows/deployment-mailbox-monitor.yml
```

These service workflows do not grant or determine StegGate activation or stable-release authority. The working Deployment Mailbox Monitor remains intact; no new workflow surface is introduced by this governance repair.

Heartbeat state is sourced from `management/activation-surface.json`. The heartbeat does not grant execution authority.

## Historical evidence boundary

The following classes remain valid for replay/reconstruction but are non-authoritative for current activation state:

```text
real-boundary/**
reports/*validation*.json
management/first-boundary-*.json
management/steggate-v46-implementation.json
management/steggate-v46-session-inventory.json
management/steggate-decision-state-session-inventory.json
```

Feature-branch identities inside those retained records describe the historical event that produced the evidence. They are not current branch, merge, release, or activation claims.

## Release state

```text
candidate: 0.2.0-release-candidate
release_owner: issue #121
implementation: MERGED_VALIDATED
runtime_transfer: COMPLETE_IN_STEGCORE
continuity_consumer: COMPLETE
stable_tag: NOT_YET_PROVEN
formal_release: NOT_YET_PROVEN
downstream_propagation: NOT_YET_PROVEN
```

Issue #121 owns live release-evidence verification and stable-tag/formal-release activation. It must consume existing Repo Check, Docs Pages, deployed HTTPS receipt, and retained release-evidence surfaces before any stable-release claim. It may not create a duplicate workflow merely to satisfy this gate.

Merge does not itself create release, publication, deployment, evaluator-replacement, standards, credential, or runtime execution authority.

## Current goal

Complete release activation under issue #121 by consuming the existing hosted release-evidence chain and repairing only defects that prevent the existing release machinery from completing.

## Current publication posture

`public_review`. The documentation surface is publishable and independently verifiable, but canonical status, independent review, clinical validation, regulatory authorization, and stable release remain unclaimed unless their separate gates are satisfied.

## Current release gate

The implementation is merged and validated. Docs Pages run `32593976088` successfully deployed and live-verified commit `9ed565df9eff2d03772b766b7fd53c398efbb0e1`, generated a deployment-bound publication receipt, produced `RELEASE_EVIDENCE_DECISION=ALLOW`, and verified evidence bundle `76b43b4fbd0c9dfb9caac86d1cf7d5d78c624c5f3219b115f50bc1907e06d80d`. Stable release remains separate and explicitly governed.

## Boundary

Neither schema validation, Pages deployment, release-evidence ALLOW, notification delivery, mailbox observation, nor merge creates stable-release, canonical-publication, credential, runtime execution, standards, clinical, or regulatory authority. Historical evidence remains replay-only unless admitted by the current activation surface.

## Next tasks

1. Consume the repaired Docs Pages run and retain the `deployed-publication-evidence` artifact.
2. Use issue #121 and the existing release-promotion machinery to reconcile the proven release gates without hand-editing protected authority fields.
3. Create the stable tag/formal release only after explicit stable-release authorization is recorded.
4. After release, activate propagation verification for Site, Publisher, admissibility-wiki, and stegguardian-wiki after reading each destination handoff.

## Remaining activation work

1. Issue #121 verifies the existing release-evidence chain and establishes the stable tag/formal release only when the repository's release policy is satisfied.
2. After release authority exists, issue #121 must activate a distinct propagation-verification task for `StegVerse-Labs/Site`, `GCAT-BCAT-Engine/Publisher`, `StegVerse-Labs/admissibility-wiki`, and `StegVerse-002/stegguardian-wiki` after reading each destination handoff.

No stale or divergent historical record is permitted to participate in current activation decisions. No prior chat context is required to reconstruct this state.

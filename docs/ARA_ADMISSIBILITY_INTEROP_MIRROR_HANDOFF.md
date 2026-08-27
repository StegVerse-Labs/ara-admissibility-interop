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
stable_release_authorization: management/stable-release-authorization.json
runtime_owner: StegVerse-Labs/StegCore
continuity_owner: StegVerse-Labs/Continuity
credential_authority: TV/TVC
state: INTEGRATED_NOT_RELEASED
```

This file is the heartbeat-target handoff and is activation-authoritative together with `management/activation-surface.json`. Historical feature-branch handoffs, candidate records, receipts, task snapshots, and validation reports remain replay evidence only; they MUST NOT override current `main` state.

## Integrated StegGate state

PR #1 is merged. The conflict-resolved integration head `523868fae5f5f8584547929284ccb98db1c56e05` passed both activation validators before merge:

```text
Repo Check run 32280935639: SUCCESS
StegGate Schema Foundation run 32280935596: SUCCESS
StegGate integration merge commit: 2a0ada472f7a3cc059961cb9af5baadecb5e0c9b
```

The merged implementation includes the Audit Kit/schema foundation, deterministic execution profile, complete decision-state reconstruction, governed-transition protocol surfaces, candidate/credential/capability binding, bounded consequence evidence, and independent conformance evidence.

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

The workflow ceiling is enforced by `management/workflow-governance.json` and `tools/check_workflow_governance.py`. The repository baseline is no more than two workflows without discrete exceptions.

Baseline activation-authoritative workflows:

```text
.github/workflows/repo-check.yml
.github/workflows/steggate-schema-foundation.yml
```

Existing service workflows admitted only through discrete non-authority exceptions:

```text
ARA-WF-EX-001  .github/workflows/docs-pages.yml
ARA-WF-EX-002  .github/workflows/deployment-notification.yml
ARA-WF-EX-003  .github/workflows/deployment-mailbox-monitor.yml
```

Repo Check fails if an undeclared workflow appears, an exception disappears, or an exception gains activation/release authority. The working Deployment Mailbox Monitor remains intact. Heartbeat state is sourced from `management/activation-surface.json`; heartbeat does not grant execution authority.

## Historical evidence boundary

The following remain valid for replay/reconstruction but are non-authoritative for current activation state:

```text
real-boundary/**
reports/*validation*.json
management/first-boundary-*.json
management/steggate-v46-implementation.json
management/steggate-v46-session-inventory.json
management/steggate-decision-state-session-inventory.json
```

Feature-branch identities inside retained records describe historical events, not current branch, merge, release, or activation claims.

## Release state

```text
candidate: 0.2.0-release-candidate
release_owner: issue #121
implementation: MERGED_VALIDATED
runtime_transfer: COMPLETE_IN_STEGCORE
continuity_consumer: COMPLETE
stable_release_authorization: RECORDED_CONDITIONAL
stable_release_authorization_pr: #129
stable_release_authorization_merge: 6839fb353c241be86d1e7ad66eb4af8b8b4b2354
stable_tag: NOT_YET_PROVEN
formal_release: NOT_YET_PROVEN
downstream_propagation: NOT_YET_PROVEN
```

PR #129 recorded the explicit maintainer instruction authorizing the `0.2.0` stable tag/formal release after the governed evidence gates are satisfied. `management/stable-release-authorization.json` is the machine-readable authorization receipt. `tools/apply_stable_release_authorization.py` may change only `release_gate.stable_release_authorized`; its regression test is enforced in Repo Check. The authorization does not prove technical release evidence and does not create a tag or release.

## Current goal

Complete release activation under issue #121 by consuming the existing hosted release-evidence chain, applying only evidence-backed gate promotions, and creating the authorized stable tag/formal release only after the final candidate evidence gates are satisfied.

## Current publication posture

`public_review`. The documentation surface is publishable and independently verifiable, but canonical status, independent review, clinical validation, regulatory authorization, and stable release remain unclaimed unless their separate gates are satisfied.

## Current release gate

The implementation is merged and validated. Docs Pages run `32593976088` successfully deployed and live-verified commit `9ed565df9eff2d03772b766b7fd53c398efbb0e1`, generated a deployment-bound publication receipt, produced `RELEASE_EVIDENCE_DECISION=ALLOW`, and verified evidence bundle `76b43b4fbd0c9dfb9caac86d1cf7d5d78c624c5f3219b115f50bc1907e06d80d`. That run is not counted as overall Docs Pages success because a later notification-generation step failed. PRs #123-#128 repaired the notification contract, regression coverage, workflow governance, evidence retention ordering, release-gate proposal retention, and stale release-readiness state. PR #129 separately satisfied the explicit authorization requirement.

The remaining release blocker is therefore technical evidence on the final repaired candidate state: consume an end-to-end successful main-branch Docs Pages run with retained `deployed-publication-evidence`, reconcile the promotable fields and Repo Check evidence for that same candidate state, then create the already-authorized stable tag/formal release.

## Boundary

Neither schema validation, Pages deployment, release-evidence ALLOW, authorization recording, notification delivery, mailbox observation, nor merge creates stable release by itself. None creates canonical-publication, credential, runtime execution, standards, clinical, or regulatory authority. Historical evidence remains replay-only unless admitted by the current activation surface.

## Next tasks

1. Consume the next repaired main-branch Docs Pages run and retain/verify `deployed-publication-evidence` for the exact candidate commit.
2. Reconcile evidence-promotable release gates through `tools/promote_release_gates.py` and separately reconcile Repo Check evidence; do not hand-edit evidence gates.
3. Apply the recorded explicit authorization through `tools/apply_stable_release_authorization.py` when the final release manifest is prepared.
4. Create the `0.2.0` stable tag/formal release only after all required gates agree.
5. After release, read each destination handoff and activate propagation verification for `StegVerse-Labs/Site`, `GCAT-BCAT-Engine/Publisher`, `StegVerse-Labs/admissibility-wiki`, and `StegVerse-002/stegguardian-wiki`.

## Remaining activation work

Issue #121 remains the sole release owner. Completion requires the stable tag/formal release to exist and the activation manifest/handoff to record its exact identity and evidence, followed by activation of the downstream propagation-verification task.

No stale or divergent historical record is permitted to participate in current activation decisions. No prior chat context is required to reconstruct this state.

## TV/TVC mail provider authority reconciliation — 2026-08-27

Live source review found that the two admitted non-activation service workflows were still processing Microsoft Entra application credentials directly inside GitHub-hosted runners.

Observed legacy source path:

.github/workflows/deployment-notification.yml
  -> STEGVERSE_MAIL_CLIENT_SECRET from GitHub Secrets
  -> tools/send_deployment_notification.py
  -> OAuth2 client_credentials
  -> Microsoft Graph sendMail

.github/workflows/deployment-mailbox-monitor.yml
  -> STEGVERSE_MAIL_CLIENT_SECRET from GitHub Secrets
  -> tools/poll_deployment_notification_mailbox.py
  -> OAuth2 client_credentials
  -> Microsoft Graph Mail.ReadWrite

That source contradicted this handoff's existing credential_authority: TV/TVC boundary. The workflow-governance exceptions grant only non-authoritative service transport roles; they do not grant provider credential authority.

Repair on branch fix/ara-tvc-mail-provider-boundary:

ARA direct Entra client-secret processing: RETIRED
ARA direct Microsoft Graph network execution: RETIRED
GitHub Actions mail/provider secrets interpolation: REMOVED
notification generation/evidence binding: PRESERVED
notification replay/attachment processing: PRESERVED
provider execution state: BLOCKED
required state: TVC_ADMITTED_PROVIDER_ROUTE_REQUIRED
credential material read by ARA: FALSE
provider execution performed by ARA: FALSE
release authority effect: NONE

The existing TVC resident mailbox/provider-operation surfaces are the permitted integration direction. This repair intentionally does not invent an ARA-local OAuth broker or claim that the exact ARA Mail.Send or Mail.ReadWrite operations are already admitted in TVC.

State distinction:

source contradiction repair: IMPLEMENTED
hosted validation: VALIDATED
Repo Check: 33070088138 SUCCESS
StegGate Schema Foundation: 33070088132 SUCCESS
merge: MERGED
merge_sha: 53d12e40604f4281688803c485c6fa16f7dcc88b
TVC Graph send operation admitted: NOT PROVEN
TVC ARA mailbox read-write operation admitted: NOT PROVEN
provider runtime activation: NOT OBSERVED
stable release state: unchanged

### ARA mail boundary merge reconciliation

Live repository inspection confirms PR #133 merged the validated source retirement:

PR: #133
validated exact head: 6bd94c0634cf8f2924c14e0487407259385ff6bf
Repo Check 33070088138: SUCCESS
StegGate Schema Foundation 33070088132: SUCCESS
merge: 53d12e40604f4281688803c485c6fa16f7dcc88b

Main-tree verification:

GitHub Actions STEGVERSE_MAIL secret interpolation: ABSENT
STEGVERSE_MAIL_CLIENT_SECRET in active ARA mail source: ABSENT
OAuth2 client_credentials in active ARA mail source: ABSENT
direct graph.microsoft.com execution in active ARA mail source: ABSENT
TVC_ADMITTED_PROVIDER_ROUTE_REQUIRED fail-closed boundary: PRESENT

State:

IMPLEMENTED: YES
VALIDATED: YES
MERGED: YES
DEPLOYED TVC Graph provider operation: NO
ACTIVATED mail provider runtime: NO
OBSERVED Mail.Send operation through TVC: NO
OBSERVED Mail.ReadWrite operation through TVC: NO
RELEASED ARA stable release: NO
COMPLETE ARA release goal: NO

The remaining provider-operation gap is outside ARA credential authority. Future Microsoft Graph execution must use an admitted TV/TVC operation and return only bounded non-secret results/evidence to ARA.

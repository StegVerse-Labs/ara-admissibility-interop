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


### TVC Graph request producer merge reconciliation — 2026-08-27

The ARA outbound deployment-notification producer now emits the exact bounded TVC provider-operation request contract while remaining credential-neutral and fail-closed for actual provider delivery.

```text
TVC source admission:
  PR #176 merge: a03563226740e2e6c7b5ae8ec21b611a15fd5934
  exact operation classes: SEND / FETCH / MARK_READ

TVC resident CLI:
  PR #178 merge: 9332ee37f62c67f5ed478fa28b2749ea510eb4aa
  validation run: 33119425031 SUCCESS

TVC exact request binding:
  PR #181 merge: 5e5813787b749ef7bb0cf81843cbf7dd908b1625
  validation run: 33119847552 SUCCESS

ARA outbound request producer:
  PR #135
  validated head: 002df426cd993055e18ec3d99c6af64c8e9f27fe
  Repo Check: 33120158075 SUCCESS
  merge: a8d5c9c774af9093e90065e6365ce591db68f308
```

Current exact state:
- TVC ARA Graph source admission: IMPLEMENTED / VALIDATED / MERGED
- ARA deployment notification TVC request generation: IMPLEMENTED / VALIDATED / MERGED
- ARA request includes canonical request hash, ARA commit SHA, workflow run ID, and governed evidence attachments
- ARA provider credential handling: NONE
- ARA direct Microsoft Graph execution: NONE
- ARA delivery state without admitted carrier/runtime: BLOCKED
- actual Mail.Send through TVC: NOT OBSERVED
- mailbox fetch through TVC: NOT WIRED IN ARA
- mailbox mark-read through TVC: NOT WIRED IN ARA
- Microsoft Graph Mail.Send/Mail.ReadWrite application permission admission: NOT OBSERVED
- stable release state: unchanged

The next machine-executable provider lane is ARA mailbox request/result integration against the already-merged TVC FETCH and MARK_READ contracts. Transport/runtime admission remains a separate TV/TVC-owned gate.


### ARA TVC mailbox request/result integration branch — 2026-08-27

Branch `ara-tvc-mailbox-requests-136` implements the ARA-side source lifecycle for the already-admitted TVC mailbox operations without creating provider transport or runtime authority.

Implemented source behavior:
- emits exact hash-bound `ARA_DEPLOYMENT_MAILBOX_FETCH` request using non-secret monitor-mailbox runtime policy plus ARA commit/workflow identity;
- validates a supplied TVC secret-free provider result against request hash, operation class, ARA commit SHA, workflow run ID, TV/TVC credential authority, and no-secret/no-token-export predicates;
- consumes only normalized governed-message fields returned by TVC;
- preserves existing deterministic notification validation, replay ledger, candidate creation, and duplicate-noop semantics;
- emits separate hash-bound `ARA_DEPLOYMENT_MAILBOX_MARK_READ` requests only after `candidate_created` or `duplicate_noop`;
- blocked, malformed, conflicting, or incomplete messages produce no mark-read request;
- ARA never mutates the mailbox and performs no Microsoft Graph execution;
- the existing scheduled mailbox workflow only creates/retains non-secret request artifacts; it does not transport them to TVC.

Lifecycle:
- source implementation: IMPLEMENTED
- deterministic regression source: IMPLEMENTED
- workflow primary/iosnoperiod parity: IMPLEMENTED
- hosted validation: PENDING
- merge: NO
- admitted ARA→TVC carrier: NOT IDENTIFIED
- TVC provider result observed: NO
- Mail.ReadWrite permission admission: NOT OBSERVED
- mailbox mutation through TVC: NOT OBSERVED
- stable release effect: NONE

The non-secret mailbox address is intentionally not invented in source. It remains a runtime policy binding and TVC independently enforces that any requested mailbox equals the mailbox in the resident credential package.


### ARA TVC mailbox request integration merge — 2026-08-27

The ARA-side mailbox request/result lifecycle is now merged:

```text
ARA PR #136
validated head: ccffe9a97036fca208a82699818929ee9160e7de
Repo Check 33120648262: SUCCESS
StegGate Schema Foundation 33120648375: SUCCESS
merge: 61c8d1c627148d6caa54c60e8d9525ab5de48c72
```

Merged behavior:
- exact hash-bound `ARA_DEPLOYMENT_MAILBOX_FETCH` request generation;
- TVC result validation against request hash, operation class, ARA commit SHA, workflow run ID, credential authority, and no-secret/no-token-export predicates;
- deterministic governed-message filtering, attachment validation, replay ledger, candidate creation and duplicate-noop preservation;
- separate `ARA_DEPLOYMENT_MAILBOX_MARK_READ` request generation only after `candidate_created` or `duplicate_noop`;
- blocked/malformed/conflicting messages remain without a mark-read request;
- ARA mailbox mutation: NONE;
- ARA Microsoft Graph execution: NONE;
- scheduled workflow retains non-secret FETCH/MARK_READ request artifacts and maintains iosnoperiod parity.

Lifecycle:
- mailbox source integration: IMPLEMENTED / VALIDATED / MERGED
- admitted ARA→TVC request carrier: NOT YET PROVEN
- TVC provider result consumed in live workflow: NOT OBSERVED
- Mail.ReadWrite provider permission admission: NOT OBSERVED
- live mailbox mutation through TVC: NOT OBSERVED
- stable release effect: NONE

The next integration boundary is the existing TVC provider-operation carrier/lease model. Do not create a second carrier if the canonical broker can admit these operation classes.


### TVC resident intake and provider-readiness continuation — 2026-08-27

Downstream TVC source progressed after ARA PR #136:

```text
TVC PR #186 capability lease
  merge: 4e38b6ab02fdefa3201ea2cf8bd13045b5e8c6cb
  validation: 33121349131 SUCCESS

TVC PR #187 resident local intake
  merge: 13f69ac43aa6db073dd8f44cec665a579b4e3777
  validation: 33121667116 SUCCESS

TVC PR #189 provider permission readiness observer
  merge: 42f18a2aaff125459de04a2fdb31889cc94ac307
  validation: 33122004407 SUCCESS
```

TVC production intake remains fail closed because its admitted carrier list is empty. The resident permission observer can evaluate `Mail.Send` and `Mail.ReadWrite` roles without leaking access material or performing mail actions, but no live permission observation has occurred.

ARA source remains credential-neutral and already emits bounded SEND/FETCH/MARK_READ requests. No ARA source work should recreate Microsoft credential handling, direct Graph execution, or transport authority. The next cross-repository gate is a formally admitted provider-neutral ARA→TVC carrier, followed by live TVC permission/policy/runtime receipts.


### TVC repository-native ARA Graph dispatcher — 2026-08-27

TVC PR #192 merged the repository-native dispatcher entrypoints for the existing ARA Graph resident source:

- `tvc.ara_graph.provider_readiness.observe`
- `tvc.ara_graph.resident_intake.process`

Validated head `edf6c4bde440e28e8f97ab5864284a388c742c9c`; consistency run `33135667400` SUCCESS; merge `eeab8fca523a5c9f745f49f193beb46ffef73f79`.

This does not create the missing ARA→TVC carrier. A missing carrier delivery remains a blocked TVC dispatcher result, not successful execution.


### TVC ARA Graph policy-binding readiness — 2026-08-27

TVC PR #193 merged the observation-only mailbox/sender/recipient readiness layer at `45591a24ad39bedb4193e19475f32be5c4a9240b` after consistency run `33135841972` SUCCESS.

The resident task `tvc.ara_graph.policy_bindings.observe` emits only hashes/booleans and performs no Graph action. Actual resident policy values and provider permissions remain unobserved. The unresolved cross-repository gate remains the provider-neutral ARA→TVC carrier.


### TVC provider-neutral KV/InTr carrier — 2026-08-27

TVC PR #195 merged the first admitted ARA→TVC provider-neutral carrier profile:

`tvc-kv-intr-ara-graph-v1`

Validated head `fc29afe38020eb4df8bf80f5d79ffb3a84effc63`; consistency run `33136258675` SUCCESS; merge `1c76cd1f54c53650b160d0929d8c5ec761048d51`.

The carrier is a local KV/InTr handoff only. It validates exact ARA request bytes, request/commit/workflow identity, InTr receipt chaining, root custody, no secret plaintext, and no authority transfer, then places the unchanged request plus TVC carrier receipt into the existing resident inbox. It does not create network transport, credential authority, lease authority, Graph execution authority, runtime activation authority, or ARA release authority.

ARA should not create another provider route or carrier. Remaining gates are live TVC observations and actual bounded provider execution receipts.


### TVC aggregate ARA Graph activation preflight — 2026-08-27

TVC PR #197 merged `tvc.ara_graph.activation_preflight` at `4cee5d5da05b2bbe717d8887a8fdd0b731773517` after validation run `33136427650` SUCCESS.

The preflight requires live provider-role PASS, live policy-binding PASS, and exact verified KV/InTr request delivery before returning `READY_FOR_RESIDENT_INTAKE`. It does not issue the provider-operation lease or invoke Graph. ARA must not treat source validation or preflight source availability as delivery/runtime activation.


### ARA Graph source/control complete; runtime authority handoff — 2026-08-27

TVC PR #201 is merged at `e36dc36f697afc27936403db171f23a6cc45edf3` after exact-head validation run `33137678309` SUCCESS.

The final dispatcher source requires explicit `STEGTV_ARA_GRAPH_RUNTIME_AUTHORITY=TV/TVC`, aggregate preflight `READY_FOR_RESIDENT_INTAKE`, and a post-preflight exact request-hash match before the existing TVC resident intake may execute one bounded Graph operation.

Canonical remaining runtime owner/task:
`StegVerse-Labs/TVC/tasks/TVC-ARA-GRAPH-RUNTIME-EXECUTION-086.json`

ARA must not create another carrier, OAuth broker, provider broker, Graph credential path, or runtime. It consumes only bounded non-secret TVC results/receipts. Live SEND/FETCH/MARK_READ evidence remains NOT OBSERVED and must not be inferred from source validation.


### ARA Graph sovereign resident request bridge — 2026-08-27

StegVerse-Labs/.github PR #353 merged the intent-only resident execution bridge at `ef85edcea0fa40f91ae80399a587898d42e4f176` after heartbeat validation `33141631865` SUCCESS and organization-control validation `33141631864` SUCCESS.

The next eligible sovereign local-source refresh may submit `SHWP-ARA-GRAPH-RUNTIME-086` to the existing WorkerCoordinator. The request grants no authority and ARA still owns no Microsoft credential/provider runtime. Authentic SEND/FETCH/MARK_READ evidence remains NOT OBSERVED.

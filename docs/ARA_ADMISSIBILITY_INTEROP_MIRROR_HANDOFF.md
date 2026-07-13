# ARA Admissibility Interop Mirror Handoff

## Current goal

Complete live verification of the `0.2.0-release-candidate` governed public-review publication path and activate evidence-backed email monitoring for successor orchestration.

## Completed

- Confirmed canonical and iOS-safe workflow mirrors for Repo Check, Docs Pages, Deployment Notification, and Deployment Mailbox Monitor.
- Added dependency-free publication gates, exact-commit Pages verification, retained evidence, independent verification, release decisions, deterministic evidence bundles, and evidence-bounded gate promotion.
- Added handoff-backed deployment notification generation importing `Current goal`, `Current publication posture`, `Current release gate`, `Boundary`, and `Next tasks`.
- Added Microsoft Graph application transport, retained delivery receipts, a post-Pages successor notification workflow, and canonical body, envelope, and bundle attachments.
- Added inbound notification validation, verification-required next-task candidates, durable replay identities, duplicate no-ops, and conflicting-replay rejection.
- Added `tools/poll_deployment_notification_mailbox.py` to retrieve unread governed messages, require all three canonical attachments, process them through the replay ledger, and mark a message read only after `candidate_created` or `duplicate_noop`.
- Added `tools/test_deployment_mailbox_poller.py` covering configuration states, subject filtering, required attachments, duplicate attachments, invalid Base64, unread filtering, and oldest-first ordering.
- Added `.github/workflows/deployment-mailbox-monitor.yml` with hourly and explicit-dispatch triggers.
- The monitor restores the newest non-expired `deployment-mailbox-monitor-state` artifact, runs the poller, and uploads the updated ledger, summary, processing receipts, and task candidates with 90-day retention.
- Extended workflow parity enforcement and Repo Check to include the scheduled monitor and mailbox-poller tests.
- Existing bounded `_site` diagnostics remain in place for the unresolved Pages entry-point layout defect.

## Current publication posture

- publication status: `public_review`
- canonical status: `not_authorized`
- independent review: `not_started`
- clinical status: `not_validated`
- regulatory status: `not_authorized`
- reliance posture: `research_and_review_only`

## Current release gate

- local architecture and checks: built
- canonical/iOS workflow parity: built across four workflow pairs
- exact-commit deployment and evidence verification: built
- release-evidence evaluator and bounded gate promoter: built
- handoff-backed email generation and Graph transport: built
- replay ledger and one-task-per-notification processing: built
- scheduled mailbox polling: built
- durable cross-run ledger restoration and retention: built
- mark-read-after-accepted-processing rule: enforced
- Microsoft Graph application credentials: not configured or not yet observed
- outbound delivery evidence: pending configured successor run
- inbound mailbox-monitor evidence: pending configured scheduled run
- Pages root-entry layout repair: pending observed build diagnostics and successor correction
- deployed publication evidence and bundle inspection: pending
- stable release tag: blocked

## Boundary

A successful Pages deployment means only that documentation was permitted under the declared publication posture. It does not establish upstream endorsement, external certification, independent review, clinical validity, regulatory authorization, canonical status, or execution authority.

Email delivery and mailbox receipt are orchestration signals, not deployment evidence or release authority. The monitor may create a verification-required task only after validating the attached body, envelope, bundle identity, commit, declared handoff sections, and public-review decision.

Replay-ledger continuity prevents duplicate task creation. It cannot promote release gates, establish Repo Check standing, set `stable_release_authorized`, or create a release tag.

## Next tasks

1. Confirm Repo Check passes all publication, evidence, promotion, notification, replay-ledger, and mailbox-poller tests.
2. Inspect the next Docs Pages build inventory and repair only the remaining `_site/index.html` discovery defect.
3. Confirm Docs Pages deploys and retains a valid `deployed-publication-evidence` artifact.
4. Confirm Deployment Notification reverifies that artifact and writes a delivery receipt.
5. Configure narrowly restricted Microsoft Entra `Mail.Send` and `Mail.ReadWrite` application access for the designated sender and monitor mailbox.
6. Configure the six mail and monitor secrets declared by the workflows.
7. Confirm the hourly monitor restores its prior ledger, processes a governed email once, marks it read only after acceptance, and uploads updated monitor state.
8. Independently verify the GitHub deployment artifact before applying any gate-promotion proposal.
9. Set `repo_check_workflow_verified` only from separately observed Repo Check evidence.
10. Create a stable tag only after explicit release authorization.
11. Add optional downstream Site mirroring only after inspecting `StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md`.

No prior chat context is required to continue from this handoff.

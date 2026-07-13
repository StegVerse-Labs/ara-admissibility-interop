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
- Added bounded `_site` diagnostics for the unresolved Pages stamping failure.
- Docs Pages run `29224962832` on commit `ebfbae5d59ceeb38c98d17617ada128aeb91b535` passed the publication gate and Jekyll build but failed again at `Stamp built site with deployment identity`.
- The repeated pattern establishes that the container build completes while the following host-side Python step cannot mutate the generated artifact; the remaining defect is container-owned `_site` permissions rather than publication-gate, Jekyll-rendering, or workflow-parity failure.
- Commit `7400398dacc1d296f83bb5f0b1d83aa92a9e22fa` updated `tools/stamp_built_site.py` to normalize ownership only for `_site` through runner `sudo chown -R`, fail closed if normalization fails, and then preserve the existing deterministic index selection, exact-commit stamping, and inventory diagnostics.
- Repo Check run `29224927109` on commit `8a2dc7d330137243b9803c0dbcbc7db387469dd5` failed at workflow parity during the staged mailbox-monitor updates; later commits completed the canonical/iOS mirror pair, so no duplicate repair was applied.

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
- Pages artifact ownership normalization: installed, successor-run verification pending
- corrected Pages workflow live success: pending successor-run evidence
- deployed publication evidence and bundle inspection: pending
- stable release tag: blocked

## Boundary

A successful Pages deployment means only that documentation was permitted under the declared publication posture. It does not establish upstream endorsement, external certification, independent review, clinical validity, regulatory authorization, canonical status, or execution authority.

Email delivery and mailbox receipt are orchestration signals, not deployment evidence or release authority. The monitor may create a verification-required task only after validating the attached body, envelope, bundle identity, commit, declared handoff sections, and public-review decision.

Replay-ledger continuity prevents duplicate task creation. It cannot promote release gates, establish Repo Check standing, set `stable_release_authorized`, or create a release tag.

Ownership normalization is limited to the generated `_site` artifact inside the GitHub-hosted runner workspace. It does not modify repository ownership, permissions, publication posture, release gates, deployment authority, or external systems.

## Next tasks

1. Confirm Repo Check passes all publication, evidence, promotion, notification, replay-ledger, and mailbox-poller tests after the completed workflow mirror updates.
2. Confirm a successor Docs Pages run executes commit `7400398dacc1d296f83bb5f0b1d83aa92a9e22fa`, normalizes `_site` ownership, stamps deployment identity, and passes the built-site entry verification.
3. Confirm Docs Pages deploys and retains a valid `deployed-publication-evidence` artifact.
4. Inspect that artifact and independently verify the publication receipt and aggregate evidence bundle.
5. Confirm Deployment Notification reverifies that artifact and writes a delivery receipt.
6. Configure narrowly restricted Microsoft Entra `Mail.Send` and `Mail.ReadWrite` application access for the designated sender and monitor mailbox.
7. Configure the six mail and monitor secrets declared by the workflows.
8. Confirm the hourly monitor restores its prior ledger, processes a governed email once, marks it read only after acceptance, and uploads updated monitor state.
9. Independently verify the GitHub deployment artifact before applying any gate-promotion proposal.
10. Set `repo_check_workflow_verified` only from separately observed Repo Check evidence.
11. Create a stable tag only after explicit release authorization.
12. Add optional downstream Site mirroring only after inspecting `StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md`.

No prior chat context is required to continue from this handoff.

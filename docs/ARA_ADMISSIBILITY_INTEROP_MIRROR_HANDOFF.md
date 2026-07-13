# ARA Admissibility Interop Mirror Handoff

## Current goal

Complete live verification of the `0.2.0-release-candidate` governed public-review publication path and activate evidence-backed email monitoring for successor orchestration.

## Completed

- Confirmed canonical and iOS-safe workflow mirrors for Repo Check, Docs Pages, Deployment Notification, and Deployment Mailbox Monitor.
- Added dependency-free publication gates, exact-commit Pages verification, retained evidence, independent verification, release decisions, deterministic evidence bundles, and evidence-bounded gate promotion.
- Added handoff-backed deployment notification generation importing `Current goal`, `Current publication posture`, `Current release gate`, `Boundary`, and `Next tasks`.
- Added Microsoft Graph application transport, retained delivery receipts, a post-Pages successor notification workflow, and canonical body, envelope, and bundle attachments.
- Added inbound notification validation, verification-required next-task candidates, durable replay identities, duplicate no-ops, and conflicting-replay rejection.
- Added scheduled Microsoft Graph mailbox polling, oldest-first unread processing, required attachment validation, mark-read-after-acceptance, and durable cross-run ledger restoration.
- Repeated Pages runs proved the containerized Jekyll action could report build completion without exposing a usable host-side `_site/index.html` to the following governed stamping step.
- Added `tools/build_governed_docs_site.py`, a dependency-free deterministic renderer that converts repository Markdown to static HTML, copies declared supporting assets, and guarantees `_site/index.html` before deployment stamping.
- Replaced `actions/jekyll-build-pages@v1` in both Pages workflow copies with `python3 tools/build_governed_docs_site.py`; the external container build is no longer on the critical publication path.
- Added `tools/test_governed_docs_builder.py` covering heading rendering, Markdown-link conversion, inline-code rendering, code escaping, root entry generation, linked-page generation, and supporting-asset copying.
- Repo Check now runs the deterministic builder regression suite, and canonical/iOS workflow parity was restored after both workflow pairs were updated.
- Existing exact-commit stamping, live HTTP verification, receipt generation, evidence evaluation, bundle verification, notification generation, and retained-artifact boundaries remain unchanged after the builder replacement.

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
- deterministic dependency-free docs builder and tests: built
- exact-commit deployment and evidence verification: built
- release-evidence evaluator and bounded gate promoter: built
- handoff-backed email generation and Graph transport: built
- replay ledger and one-task-per-notification processing: built
- scheduled mailbox polling and durable state restoration: built
- Microsoft Graph application credentials: not configured or not yet observed
- outbound delivery evidence: pending configured successor run
- inbound mailbox-monitor evidence: pending configured scheduled run
- deterministic Pages build execution: pending successor-run evidence
- corrected Pages workflow live success: pending successor-run evidence
- deployed publication evidence and bundle inspection: pending
- stable release tag: blocked

## Boundary

A successful Pages deployment means only that documentation was permitted under the declared publication posture. It does not establish upstream endorsement, external certification, independent review, clinical validity, regulatory authorization, canonical status, or execution authority.

Email delivery and mailbox receipt are orchestration signals, not deployment evidence or release authority. The monitor may create a verification-required task only after validating the attached body, envelope, bundle identity, commit, declared handoff sections, and public-review decision.

Replay-ledger continuity prevents duplicate task creation. It cannot promote release gates, establish Repo Check standing, set `stable_release_authorized`, or create a release tag.

The dependency-free builder controls only the generated `_site` artifact. Replacing Jekyll does not alter publication posture, release authority, canonical status, clinical or regulatory standing, or any external system.

## Next tasks

1. Confirm Repo Check passes the new governed-docs-builder suite together with all publication, evidence, promotion, notification, replay-ledger, and mailbox-poller tests.
2. Confirm the successor Docs Pages run invokes `tools/build_governed_docs_site.py`, produces `_site/index.html`, stamps deployment identity, and passes built-site entry verification.
3. Confirm Docs Pages deploys the exact current commit and retains a valid `deployed-publication-evidence` artifact.
4. Inspect that artifact and independently verify the publication receipt and aggregate evidence bundle.
5. Confirm Deployment Notification reverifies that artifact and writes a delivery receipt.
6. Configure narrowly restricted Microsoft Entra `Mail.Send` and `Mail.ReadWrite` application access for the designated sender and monitor mailbox.
7. Configure the mail and monitor secrets declared by the workflows.
8. Confirm the hourly monitor restores its prior ledger, processes a governed email once, marks it read only after acceptance, and uploads updated monitor state.
9. Apply only evidence-backed technical gate promotion after direct artifact inspection.
10. Set `repo_check_workflow_verified` only from separately observed Repo Check evidence.
11. Create a stable tag only after explicit release authorization.
12. Add optional downstream Site mirroring only after inspecting `StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md`.

No prior chat context is required to continue from this handoff.

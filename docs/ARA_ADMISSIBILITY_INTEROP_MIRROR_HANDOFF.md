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
- Docs Pages run `29225241901` on commit `ec0adaa7a1d9d5b9f926a06ed84c04eb360d7934` passed deterministic build, deployment stamping, built-entry verification, Pages artifact upload, deployment, exact-live-commit verification, and receipt generation.
- That run then failed only at `Evaluate deployed release evidence` because the receipt generator records the live deployment identity hash as `identity_body_sha256` while the independent verifier still read the legacy `identity_sha256` field.
- Commit `92dde057ffeb682e31acc147574e4c19a5f617e3` repaired the verifier to use the canonical `identity_body_sha256` field while accepting the legacy alias for retained-evidence compatibility.
- Repo Check run `29225254890` on commit `e26659d65c0404388c01254c76f570f17dc82658` failed at `Generate validation report` because `tools/check_docs_site.py` still required the removed Jekyll action and pre-renderer workflow structure.
- Commit `698fd40a11f964f2a75ff6aff3c6fff8908cd528` aligned the docs self-check with the deterministic builder, all four workflow mirror pairs, current notification/replay/mailbox tests, and the canonical live identity hash field.
- Existing exact-commit stamping, live HTTP verification, receipt generation, evidence evaluation, bundle verification, notification generation, and retained-artifact boundaries remain unchanged.

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
- exact-commit deployment and live verification: observed through the receipt-generation boundary
- independent evidence verifier canonical identity-hash compatibility: repaired, successor-run verification pending
- docs aggregate self-check alignment: repaired, successor-run verification pending
- release-evidence evaluator and bounded gate promoter: built
- handoff-backed email generation and Graph transport: built
- replay ledger and one-task-per-notification processing: built
- scheduled mailbox polling and durable state restoration: built
- Microsoft Graph application credentials: not configured or not yet observed
- outbound delivery evidence: pending configured successor run
- inbound mailbox-monitor evidence: pending configured scheduled run
- deployed publication evidence and bundle retention: pending successor-run evidence
- stable release tag: blocked

## Boundary

A successful Pages deployment means only that documentation was permitted under the declared publication posture. It does not establish upstream endorsement, external certification, independent review, clinical validity, regulatory authorization, canonical status, or execution authority.

Email delivery and mailbox receipt are orchestration signals, not deployment evidence or release authority. The monitor may create a verification-required task only after validating the attached body, envelope, bundle identity, commit, declared handoff sections, and public-review decision.

Replay-ledger continuity prevents duplicate task creation. It cannot promote release gates, establish Repo Check standing, set `stable_release_authorized`, or create a release tag.

The dependency-free builder controls only the generated `_site` artifact. Identity-hash compatibility and self-check alignment do not change publication posture, release authority, canonical status, clinical or regulatory standing, or any external system.

## Next tasks

1. Confirm Repo Check passes the governed-docs-builder suite together with all publication, evidence, promotion, notification, replay-ledger, and mailbox-poller tests after commit `698fd40a11f964f2a75ff6aff3c6fff8908cd528`.
2. Confirm a successor Docs Pages run passes `Evaluate deployed release evidence` using the canonical `identity_body_sha256` field.
3. Confirm Docs Pages generates and verifies the aggregate evidence bundle, generates the handoff-backed notification, and retains `deployed-publication-evidence`.
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

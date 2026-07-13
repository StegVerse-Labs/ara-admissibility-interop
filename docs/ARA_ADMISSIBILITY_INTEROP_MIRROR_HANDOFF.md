# ARA Admissibility Interop Mirror Handoff

## Current goal

Complete live verification of the `0.2.0-release-candidate` governed public-review publication path and activate evidence-backed email monitoring for successor orchestration.

## Completed

- Confirmed canonical Pages workflow at `.github/workflows/docs-pages.yml` and iOS-safe mirror at `iosnoperiod/github/workflows/docs-pages.yml`.
- Added explicit publication, canonical, independent-review, clinical, regulatory, and reliance states.
- Added dependency-free fail-closed publication gates, positive and negative tests, workflow parity, status generation, receipts, and retained artifacts.
- Replaced raw Markdown deployment with Jekyll-built `_site` deployment and added root-entry, marker, HTTPS, HTTP 200, and exact-current-commit checks.
- Added built-site deployment identity, deterministic artifact-tree hashing, live-root hashing, receipt schema `1.3.0`, independent evidence verification, and tamper tests.
- Added bounded release-evidence decisions with separate public-review and stable-release results.
- Added deterministic deployment-evidence bundle generation, aggregate SHA-256, independent verification, and bundle tamper tests.
- Added evidence-bounded release-gate promotion that cannot set `repo_check_workflow_verified`, cannot set `stable_release_authorized`, and cannot create a tag.
- Added Jekyll front matter to `docs/index.md` after the prior build failed to produce `_site/index.html`.
- Repaired the deployment-notification authority-boundary sentence after its regression test identified the missing exact phrase.
- Added `tools/generate_deployment_notification.py` to import the handoff sections `Current goal`, `Current publication posture`, `Current release gate`, `Boundary`, and `Next tasks` into the email body.
- Added `tools/send_deployment_notification.py`, a dependency-free Microsoft Graph sender that accepts only Microsoft Entra application credentials, rejects partial configuration, and writes a delivery receipt.
- Added `.github/workflows/deployment-notification.yml`, triggered only after a successful `Docs Pages` run or by an explicit source-run dispatch.
- The successor notification workflow checks out the exact deployment commit, downloads `deployed-publication-evidence`, independently reverifies the bundle and publication receipt, regenerates the handoff-backed body, attempts Graph delivery, and retains notification evidence.
- Added `tools/ingest_deployment_notification.py` to verify received notification body hash, subject class, required handoff-section list, commit identity, artifact name, bundle hash, next action, and public-review decision.
- Passing inbound validation creates `status/deployment-next-task-candidate.json` with `task_status: verification_required`; it does not promote gates or authorize release.
- Added `tools/test_deployment_notification_transport.py` covering valid ingestion, body tampering, commit mismatch, bundle mismatch, missing handoff sections, blocked public review, absent configuration, complete configuration, and partial-configuration rejection.
- Added `docs/deployment-email-monitoring.md` and linked it from the documentation index.
- Added canonical and iOS-safe deployment-notification workflow mirrors and extended workflow parity enforcement to include them.
- Repo Check now runs notification generation, Microsoft Graph transport configuration, and monitored-ingestion regression tests.
- Docs Pages run `29224103644` on commit `76173b36746b548ce3b92f39c82b0ae01d36767a` passed the publication gate and Jekyll build but again failed at `Stamp built site with deployment identity` because the built artifact did not expose `_site/index.html` at the expected root.
- Commit `486aedd1f7a9278e567743de05d9d976d87e4c5d` made `tools/stamp_built_site.py` path-robust: it accepts the required root entry point or deterministically copies exactly one nested Jekyll `index.html` to `_site/index.html`; zero or multiple candidates still fail closed with a complete built-file diagnostic.

## Current publication posture

- publication status: `public_review`
- canonical status: `not_authorized`
- independent review: `not_started`
- clinical status: `not_validated`
- regulatory status: `not_authorized`
- reliance posture: `research_and_review_only`

## Current release gate

- local architecture and checks: built
- canonical/iOS workflow parity: built across Repo Check, Docs Pages, and Deployment Notification
- independent evidence verifier and tests: built
- release-evidence evaluator and tests: built
- evidence-bundle generator, verifier, and tests: built
- evidence-bounded release-gate promoter and tests: built
- handoff-backed notification generator and tests: built
- Microsoft Graph outbound transport: built
- post-Pages successor notification workflow: built
- monitored-notification ingestion and next-task candidate generation: built
- Microsoft Graph application credentials: not configured or not yet observed
- governed email delivery: pending configured successor-run evidence
- mailbox monitor retrieval and invocation: pending external mailbox integration
- path-robust built-site entry normalization: installed, successor-run verification pending
- corrected Pages workflow live success: pending successor-run evidence
- rendered current-commit root page: pending successor-run evidence
- deployed publication evidence artifact inspection: pending
- deployed evidence bundle inspection: pending
- stable release tag: blocked

## Boundary

A successful Pages deployment means only that the documentation was permitted under the declared publication posture. It does not establish upstream ARA endorsement, external certification, independent review, clinical validity, regulatory authorization, canonical doctrine status, or execution authority.

A passing evidence verification or evidence-bundle verification proves consistency and integrity of the declared retained evidence. It does not create scientific truth, authority, consent, legality, clinical meaning, canonical status, or standing absent from the underlying evidence and governance state.

An email notification is a signal that a governed verification candidate exists. Email delivery or receipt is not deployment evidence, release-gate authority, Repo Check standing, stable-release authorization, or permission to create a tag.

An `ALLOW` public-review decision and a successful technical-gate promotion do not authorize a stable release. `repo_check_workflow_verified` requires separately observed Repo Check evidence, and `stable_release_authorized` requires explicit maintainer authorization.

## Next tasks

1. Confirm Repo Check passes the notification generation, Graph transport configuration, and monitored-ingestion tests with all prior publication, receipt, decision, bundle, and promotion suites.
2. Confirm a successor Docs Pages run exercises commit `486aedd1f7a9278e567743de05d9d976d87e4c5d`, produces `_site/index.html`, stamps the deployment identity, deploys, verifies the exact current commit, and retains a valid `deployed-publication-evidence` artifact.
3. Inspect the retained artifact and independently verify the publication receipt and aggregate evidence bundle.
4. Confirm Deployment Notification starts from that successful run, downloads and reverifies the artifact, regenerates the current handoff-backed message, and writes `deployment-notification-delivery.json`.
5. Configure the five Microsoft Graph application secrets only after the Entra application has `sendMail` application permission and an appropriately restricted mailbox-access policy.
6. Confirm the sent email contains the required handoff sections and attachments for the notification envelope and evidence-bundle manifest.
7. Connect mailbox monitoring so a received message is passed through `tools/ingest_deployment_notification.py` and produces a verification-required next-task candidate.
8. Retrieve and independently verify the GitHub artifact before producing or applying any gate-promotion proposal.
9. Set `repo_check_workflow_verified` only from separately observed Repo Check evidence.
10. Create a stable tag only after explicit release authorization.
11. Add optional downstream Site mirroring only after inspecting `StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md`.

No prior chat context is required to continue from this handoff.

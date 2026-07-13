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
- The sender now attaches the canonical Markdown email body in addition to the notification envelope and evidence-bundle manifest so mailbox-side verification can reproduce the recorded body SHA-256 exactly.
- Added `.github/workflows/deployment-notification.yml`, triggered only after a successful `Docs Pages` run or by an explicit source-run dispatch.
- The successor notification workflow checks out the exact deployment commit, downloads `deployed-publication-evidence`, independently reverifies the bundle and publication receipt, regenerates the handoff-backed body, attempts Graph delivery, and retains notification evidence.
- Added `tools/ingest_deployment_notification.py` to verify received notification body hash, subject class, required handoff-section list, commit identity, artifact name, bundle hash, next action, and public-review decision.
- Passing inbound validation creates `status/deployment-next-task-candidate.json` with `task_status: verification_required`; it does not promote gates or authorize release.
- Added `tools/process_deployment_notification_once.py` with deterministic notification identities bound to repository, commit, workflow run, bundle SHA-256, and body SHA-256.
- Identical notification replays are idempotent no-ops; conflicting replays for the same repository, commit, and workflow run fail closed without creating a task or mutating the ledger.
- Added `status/deployment-notification-ledger.json` as the durable replay ledger, `status/deployment-notification-processing.json` as the processing receipt, and one-task-per-notification semantics.
- Added `tools/test_deployment_notification_replay_ledger.py` covering deterministic identity, replay conflict detection, distinct-run handling, verification-required task posture, and stable-authority protection.
- Repo Check now runs notification generation, Microsoft Graph transport configuration, monitored-ingestion, and replay-ledger regression tests.
- Added `docs/deployment-email-monitoring.md` and linked it from the documentation index.
- Added canonical and iOS-safe deployment-notification workflow mirrors and extended workflow parity enforcement to include them.
- Docs Pages run `29224103644` on commit `76173b36746b548ce3b92f39c82b0ae01d36767a` passed the publication gate and Jekyll build but again failed at `Stamp built site with deployment identity` because the built artifact did not expose `_site/index.html` at the expected root.
- Commit `486aedd1f7a9278e567743de05d9d976d87e4c5d` made `tools/stamp_built_site.py` path-robust: it accepts the required root entry point or deterministically copies exactly one nested Jekyll `index.html` to `_site/index.html`; zero or multiple candidates still fail closed.
- Docs Pages runs `29224565499` and `29224578601` exercised commits `486aedd1f7a9278e567743de05d9d976d87e4c5d` and `7fbaa99565973376fedacf41123dc6c59fbafb48`; both passed the publication gate and Jekyll build but still failed at the stamping step, and neither produced a retained artifact.
- Repo Check run `29224677219` on commit `b58bdd7287891dbfcc872b3e2ca01e12a5f92a16` failed only at workflow parity after the replay-ledger test was added to the canonical workflow. Commit `26a10d480173eabdf85e64df90ebad4636057d30` immediately synchronized the iOS-safe mirror, so no duplicate parity repair is required.
- Commit `06549b05450ed9110f9a0d9711c73e6fa658b642` added a bounded deterministic `_site` inventory to `tools/stamp_built_site.py` before entry-point resolution. The next Pages run will expose the actual build layout while preserving fail-closed behavior.

## Current publication posture

- publication status: `public_review`
- canonical status: `not_authorized`
- independent review: `not_started`
- clinical status: `not_validated`
- regulatory status: `not_authorized`
- reliance posture: `research_and_review_only`

## Current release gate

- local architecture and checks: built
- canonical/iOS workflow parity: built across Repo Check, Docs Pages, and Deployment Notification; successor verification pending after `26a10d4`
- independent evidence verifier and tests: built
- release-evidence evaluator and tests: built
- evidence-bundle generator, verifier, and tests: built
- evidence-bounded release-gate promoter and tests: built
- handoff-backed notification generator and tests: built
- Microsoft Graph outbound transport: built
- post-Pages successor notification workflow: built
- monitored-notification ingestion and next-task candidate generation: built
- durable replay ledger and one-task-per-notification processing: built
- Microsoft Graph application credentials: not configured or not yet observed
- governed email delivery: pending configured successor-run evidence
- mailbox polling and durable ledger persistence across monitor runs: pending workflow integration
- path-robust built-site entry normalization: installed
- bounded build-layout diagnostics: installed, successor-run evidence pending
- corrected Pages workflow live success: pending successor-run evidence
- rendered current-commit root page: pending successor-run evidence
- deployed publication evidence artifact inspection: pending
- deployed evidence bundle inspection: pending
- stable release tag: blocked

## Boundary

A successful Pages deployment means only that the documentation was permitted under the declared publication posture. It does not establish upstream ARA endorsement, external certification, independent review, clinical validity, regulatory authorization, canonical doctrine status, or execution authority.

A passing evidence verification or evidence-bundle verification proves consistency and integrity of the declared retained evidence. It does not create scientific truth, authority, consent, legality, clinical meaning, canonical status, or standing absent from the underlying evidence and governance state.

An email notification is a signal that a governed verification candidate exists. Email delivery or receipt is not deployment evidence, release-gate authority, Repo Check standing, stable-release authorization, or permission to create a tag.

The replay ledger prevents duplicate task creation and detects conflicting notifications. Ledger continuity does not create evidence or release authority.

An `ALLOW` public-review decision and a successful technical-gate promotion do not authorize a stable release. `repo_check_workflow_verified` requires separately observed Repo Check evidence, and `stable_release_authorized` requires explicit maintainer authorization.

## Next tasks

1. Confirm Repo Check passes after canonical/iOS replay-ledger workflow parity was restored by commit `26a10d480173eabdf85e64df90ebad4636057d30`.
2. Inspect the first successor Docs Pages run containing commit `06549b05450ed9110f9a0d9711c73e6fa658b642`; use its bounded `_site` inventory to identify the exact build layout and repair only the entry-point discovery defect.
3. Confirm Docs Pages produces `_site/index.html`, stamps deployment identity, deploys, verifies the exact current commit, and retains a valid `deployed-publication-evidence` artifact.
4. Inspect the retained artifact and independently verify the publication receipt and aggregate evidence bundle.
5. Confirm Deployment Notification starts from that successful run, downloads and reverifies the artifact, regenerates the current handoff-backed message, and writes `deployment-notification-delivery.json`.
6. Configure the five Microsoft Graph application secrets only after the Entra application has `sendMail` application permission and an appropriately restricted mailbox-access policy.
7. Confirm the sent email contains the canonical Markdown body plus the notification envelope and evidence-bundle attachments.
8. Add scheduled mailbox polling that downloads those three attachments and invokes `tools/process_deployment_notification_once.py` with a ledger restored from durable monitor state.
9. Persist the updated ledger and processing receipt across monitor runs, and create no more than one verification task per deterministic notification identity.
10. Retrieve and independently verify the GitHub artifact before producing or applying any gate-promotion proposal.
11. Set `repo_check_workflow_verified` only from separately observed Repo Check evidence.
12. Create a stable tag only after explicit release authorization.
13. Add optional downstream Site mirroring only after inspecting `StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md`.

No prior chat context is required to continue from this handoff.

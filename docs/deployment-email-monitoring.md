# Governed Deployment Email and Monitoring

The deployment-notification path converts a successfully verified Pages deployment into a monitored continuation signal without granting the email release authority.

## Outbound sequence

1. `Docs Pages` completes successfully and retains `deployed-publication-evidence`.
2. `Deployment Notification` starts from the completed workflow run.
3. The successor workflow checks out the exact deployment commit.
4. It downloads and independently reverifies the retained evidence bundle, publication receipt, built site, deployment identity, and captured live root.
5. It regenerates the email body from the handoff sections at that exact commit.
6. It sends the body through Microsoft Graph when the complete application configuration is present.
7. It retains the generated body, notification envelope, evidence-bundle manifest, and delivery receipt.

## Required Microsoft Graph settings

The outbound workflow reads these GitHub Actions secrets at runtime:

- `STEGVERSE_MAIL_TENANT_ID`
- `STEGVERSE_MAIL_CLIENT_ID`
- `STEGVERSE_MAIL_CLIENT_SECRET`
- `STEGVERSE_MAIL_SENDER`
- `STEGVERSE_MAIL_RECIPIENT`

The scheduled mailbox monitor uses the same tenant, client, and client-secret values plus:

- `STEGVERSE_MONITOR_MAILBOX`

A mailbox password is not accepted. A partial configuration fails closed. When a complete configuration is absent, the workflows record `not_configured` without claiming delivery or mailbox processing.

The Microsoft Entra application requires narrowly restricted application access appropriate to each operation:

- `Mail.Send` for the designated sender mailbox.
- `Mail.ReadWrite` for the designated monitor mailbox because accepted messages are marked read.

Tenant policy must restrict the application to the intended mailbox scope.

## Imported handoff sections

The email body imports:

- Current goal
- Current publication posture
- Current release gate
- Boundary
- Next tasks

The notification envelope records the full handoff SHA-256, body SHA-256, exact commit, workflow run, artifact name, and deployment evidence-bundle SHA-256.

## Scheduled inbound monitoring

`.github/workflows/deployment-mailbox-monitor.yml` runs hourly at minute 17 and also supports explicit dispatch. It restores the newest non-expired `deployment-mailbox-monitor-state` artifact before polling.

The poller retrieves unread governed messages oldest first and requires exactly these canonical attachments:

```text
deployment-notification-email.md
deployment-notification-envelope.json
deployed-evidence-bundle.json
```

Each message is passed through:

```bash
python3 tools/process_deployment_notification_once.py \
  --envelope deployment-notification-envelope.json \
  --body deployment-notification-email.md \
  --bundle deployed-evidence-bundle.json \
  --ledger deployment-notification-ledger.json
```

The processor verifies the body hash, subject class, required handoff-section list, commit identity, artifact name, next action, public-review decision, and bundle hash. It creates at most one verification-required task per deterministic notification identity.

The identity binds:

- Repository
- Commit SHA
- Workflow run ID
- Evidence-bundle SHA-256
- Email-body SHA-256

An identical replay produces `duplicate_noop`. A conflicting replay for the same repository, commit, and workflow run fails closed. A message is marked read only after `candidate_created` or `duplicate_noop`; blocked messages remain unread for investigation.

The monitor retains for 90 days:

```text
deployment-notification-ledger.json
mailbox-poll-summary.json
mailbox-notifications/
```

The retained state provides replay continuity across isolated GitHub-hosted runners. It does not create deployment evidence or release authority.

## Boundary

```text
Email received != deployment verified
Email received = governed verification candidate available
```

Notification delivery, mailbox receipt, replay-ledger continuity, and next-task creation do not establish Repo Check completion, stable-release authorization, canonical status, clinical validity, regulatory authorization, or execution authority.

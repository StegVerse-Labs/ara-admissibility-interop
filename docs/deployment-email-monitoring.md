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

The workflow reads these GitHub Actions secrets at runtime:

- `STEGVERSE_MAIL_TENANT_ID`
- `STEGVERSE_MAIL_CLIENT_ID`
- `STEGVERSE_MAIL_CLIENT_SECRET`
- `STEGVERSE_MAIL_SENDER`
- `STEGVERSE_MAIL_RECIPIENT`

A mailbox password is not accepted. A partial configuration fails closed. When all five values are absent, the workflow records `delivery_status: not_configured` without claiming that email was sent.

The Microsoft Entra application must be separately authorized for the Graph `sendMail` application permission and restricted according to the tenant's mailbox-access policy.

## Imported handoff sections

The email body imports:

- Current goal
- Current publication posture
- Current release gate
- Boundary
- Next tasks

The notification envelope records the full handoff SHA-256, body SHA-256, exact commit, workflow run, artifact name, and deployment evidence-bundle SHA-256.

## Inbound monitoring

A mailbox monitor passes the received body, envelope attachment, and bundle-manifest attachment to:

```bash
python3 tools/ingest_deployment_notification.py \
  --envelope status/deployment-notification-envelope.json \
  --body status/deployment-notification-email.md \
  --bundle status/deployed-evidence-bundle.json
```

The tool verifies the body hash, subject class, required handoff-section list, commit identity, artifact name, next action, public-review decision, and bundle hash. A passing notification creates:

```text
status/deployment-next-task-candidate.json
```

The candidate requires retrieval and independent verification of the GitHub artifact before any release-gate proposal may be created.

## Boundary

```text
Email received != deployment verified
Email received = governed verification candidate available
```

Notification delivery, mailbox receipt, and next-task creation do not establish Repo Check completion, stable-release authorization, canonical status, clinical validity, regulatory authorization, or execution authority.

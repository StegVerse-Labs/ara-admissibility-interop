# Governed Deployment Email and Monitoring

ARA owns deployment-notification generation, deterministic notification identity, replay protection, evidence attachment validation, and next-task-candidate creation.

ARA does not own Microsoft Graph credentials or provider credential execution.

## Current credential boundary

credential authority: TV/TVC
ARA credential custody: NONE
GitHub Actions provider-secret authority: NONE
direct Microsoft Entra client-secret processing in ARA: RETIRED
direct Microsoft Graph execution in ARA: RETIRED
required provider state: TVC_ADMITTED_PROVIDER_ROUTE_REQUIRED

The existing TVC resident mailbox/provider-operation surfaces are the only permitted direction for future Graph execution. This document does not claim that ARA send or Mail.ReadWrite has already been admitted there.

## Outbound sequence

1. Docs Pages completes successfully and retains deployed-publication-evidence.
2. Deployment Notification starts from the completed workflow run.
3. The successor workflow checks out the exact deployment commit.
4. It downloads and independently reverifies the retained evidence bundle and publication evidence.
5. It regenerates the notification body/envelope from the canonical handoff.
6. tools/send_deployment_notification.py validates the body/envelope/bundle relationship.
7. Until a matching TVC provider operation is admitted, it writes a secret-free blocked delivery receipt with TVC_ADMITTED_PROVIDER_ROUTE_REQUIRED.
8. Notification generation and evidence retention remain valid; delivery is not claimed.

## Inbound sequence

The mailbox workflow may preserve durable ledger state and run dependency-free helper tests. tools/poll_deployment_notification_mailbox.py no longer reads provider credentials or contacts Microsoft Graph.

Until an admitted TVC mailbox operation exists for this exact ARA use case it writes a secret-free blocked summary with credential_material_present=false, credential_material_read_by_ara=false, provider_execution_performed=false, mailbox_mutated=false, and authority_effect=false.

The existing deterministic processing helpers remain available for bounded non-secret message objects supplied by an admitted provider operation: governed subject filtering, required attachment decoding/validation, replay-ledger processing, and one-task-per-notification semantics.

## Boundary

notification generated != notification delivered
mailbox processing source present != mailbox observed
workflow success != provider execution
email received != deployment verified
email received = governed verification candidate available

No notification, receipt, mailbox summary, replay ledger, or provider operation grants release authority.

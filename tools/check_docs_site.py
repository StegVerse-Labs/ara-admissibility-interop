#!/usr/bin/env python3
"""Check governed docs, publication, evidence, notification, and monitor invariants."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = {
    "docs-index": ROOT / "docs" / "index.md",
    "docs-config": ROOT / "docs" / "_config.yml",
    "pages-workflow": ROOT / ".github" / "workflows" / "docs-pages.yml",
    "ios-pages-workflow": ROOT / "iosnoperiod" / "github" / "workflows" / "docs-pages.yml",
    "repo-check-workflow": ROOT / ".github" / "workflows" / "repo-check.yml",
    "ios-repo-check-workflow": ROOT / "iosnoperiod" / "github" / "workflows" / "repo-check.yml",
    "notify-workflow": ROOT / ".github" / "workflows" / "deployment-notification.yml",
    "ios-notify-workflow": ROOT / "iosnoperiod" / "github" / "workflows" / "deployment-notification.yml",
    "monitor-workflow": ROOT / ".github" / "workflows" / "deployment-mailbox-monitor.yml",
    "ios-monitor-workflow": ROOT / "iosnoperiod" / "github" / "workflows" / "deployment-mailbox-monitor.yml",
    "builder": ROOT / "tools" / "build_governed_docs_site.py",
    "builder-tests": ROOT / "tools" / "test_governed_docs_builder.py",
    "stamp-tool": ROOT / "tools" / "stamp_built_site.py",
    "evidence-verifier": ROOT / "tools" / "verify_publication_evidence.py",
    "release-evaluator": ROOT / "tools" / "evaluate_release_evidence.py",
    "notification-generator": ROOT / "tools" / "generate_deployment_notification.py",
    "notification-sender": ROOT / "tools" / "send_deployment_notification.py",
    "notification-ingestor": ROOT / "tools" / "ingest_deployment_notification.py",
    "notification-processor": ROOT / "tools" / "process_deployment_notification_once.py",
    "mailbox-poller": ROOT / "tools" / "poll_deployment_notification_mailbox.py",
}

REQUIRED = {
    "docs-index": [
        "release-readiness.md", "release-checklist.md", "dependency-policy.md",
        "optional-strict-validation.md", "publication-evidence-verification.md",
        "release-evidence-decision.md", "release-gate-promotion.md",
        "deployment-email-monitoring.md", "../admissibility/non-claims.md",
    ],
    "docs-config": ["title: ARA Admissibility Interop", "plugins: []", "markdown: kramdown"],
    "pages-workflow": [
        "python3 tools/build_governed_docs_site.py", "python3 tools/stamp_built_site.py",
        "uses: actions/configure-pages@v5", "uses: actions/upload-pages-artifact@v3",
        "uses: actions/deploy-pages@v4", "path: ./_site",
        "Verify live deployed root and commit identity", "PUBLICATION_ARTIFACT_ROOT: _site",
        "PUBLICATION_ARTIFACT_KIND: built_site", "status/deployed-live-root.html",
        "status/deployed-identity.json", "python3 tools/evaluate_release_evidence.py",
        "--require-public-review-allow", "status/deployed-evidence-bundle.json",
    ],
    "ios-pages-workflow": [
        "python3 tools/build_governed_docs_site.py", "python3 tools/stamp_built_site.py",
        "uses: actions/configure-pages@v5", "uses: actions/upload-pages-artifact@v3",
        "uses: actions/deploy-pages@v4", "path: ./_site",
        "Verify live deployed root and commit identity", "PUBLICATION_ARTIFACT_ROOT: _site",
        "PUBLICATION_ARTIFACT_KIND: built_site", "status/deployed-live-root.html",
        "status/deployed-identity.json", "python3 tools/evaluate_release_evidence.py",
        "--require-public-review-allow", "status/deployed-evidence-bundle.json",
    ],
    "repo-check-workflow": [
        "python3 tools/test_governed_docs_builder.py",
        "python3 tools/test_publication_evidence_verifier.py",
        "python3 tools/test_release_evidence_evaluator.py",
        "python3 tools/test_evidence_bundle_manifest.py",
        "python3 tools/test_release_gate_promotion.py",
        "python3 tools/test_deployment_notification.py",
        "python3 tools/test_deployment_notification_transport.py",
        "python3 tools/test_deployment_notification_replay_ledger.py",
        "python3 tools/test_deployment_mailbox_poller.py",
        "name: generated-status", "path: status/generated-status.json",
    ],
    "ios-repo-check-workflow": [
        "python3 tools/test_governed_docs_builder.py",
        "python3 tools/test_publication_evidence_verifier.py",
        "python3 tools/test_release_evidence_evaluator.py",
        "python3 tools/test_evidence_bundle_manifest.py",
        "python3 tools/test_release_gate_promotion.py",
        "python3 tools/test_deployment_notification.py",
        "python3 tools/test_deployment_notification_transport.py",
        "python3 tools/test_deployment_notification_replay_ledger.py",
        "python3 tools/test_deployment_mailbox_poller.py",
        "name: generated-status", "path: status/generated-status.json",
    ],
    "notify-workflow": [
        "name: Deployment Notification", "workflow_run:", "- Docs Pages",
        "github.event.workflow_run.conclusion == 'success'", "gh run download",
        "deployed-publication-evidence", "python3 tools/verify_evidence_bundle_manifest.py",
        "python3 tools/verify_publication_evidence.py", "python3 tools/send_deployment_notification.py",
        "deployment-notification-delivery.json",
    ],
    "ios-notify-workflow": [
        "name: Deployment Notification", "workflow_run:", "- Docs Pages",
        "github.event.workflow_run.conclusion == 'success'", "gh run download",
        "deployed-publication-evidence", "python3 tools/verify_evidence_bundle_manifest.py",
        "python3 tools/verify_publication_evidence.py", "python3 tools/send_deployment_notification.py",
        "deployment-notification-delivery.json",
    ],
    "monitor-workflow": [
        "name: Deployment Mailbox Monitor", "schedule:", "workflow_dispatch:",
        "python3 tools/poll_deployment_notification_mailbox.py",
        "deployment-mailbox-monitor-state", "retention-days: 90",
        "Restore durable notification ledger", "cancel-in-progress: false",
    ],
    "ios-monitor-workflow": [
        "name: Deployment Mailbox Monitor", "schedule:", "workflow_dispatch:",
        "python3 tools/poll_deployment_notification_mailbox.py",
        "deployment-mailbox-monitor-state", "retention-days: 90",
        "Restore durable notification ledger", "cancel-in-progress: false",
    ],
    "builder": [
        "GOVERNED_DOCS_BUILD=PASS", "dependency", "_site", "index.html",
        "markdown_to_html", "ARA Admissibility Interop Docs",
    ],
    "builder-tests": ["build_governed_docs_site", "index.html", "linked-page", "asset-copy"],
    "stamp-tool": ["governed-pages-deployment-identity", "deployment-identity.json", "stegverse-deployment-commit"],
    "evidence-verifier": ["def verify(", "identity_body_sha256", "artifact-tree-mismatch", "live-root-hash-mismatch"],
    "release-evaluator": ["governed-release-evidence-decision", "public_review_decision", "stable_release_automatically_authorized"],
    "notification-generator": ["Current goal", "Current publication posture", "Current release gate", "Boundary", "Next tasks", "body_sha256"],
    "notification-sender": ["microsoft-graph-sendmail", "client_credentials", "sendMail", "delivery_status", "not_configured"],
    "notification-ingestor": ["governed-deployment-evidence-verification-candidate", "verification_required", "bundle-sha256-mismatch"],
    "notification-processor": ["duplicate_noop", "conflicting_replay_blocked", "notification_identity", "stable_release_authorized"],
    "mailbox-poller": [
        "https://graph.microsoft.com/.default", "client_credentials", '"isRead": True',
        "process_deployment_notification_once.py", "deployment-notification-email.md",
        "deployment-notification-envelope.json", "deployed-evidence-bundle.json",
    ],
}


def check_contains(path: Path, phrases: list[str], problems: list[str], label: str) -> None:
    if not path.is_file():
        problems.append(f"missing:{path.relative_to(ROOT)}")
        return
    text = path.read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in text:
            problems.append(f"missing-{label}-phrase:{phrase}")


def main() -> int:
    problems: list[str] = []
    for label, path in FILES.items():
        check_contains(path, REQUIRED[label], problems, label)

    manifest_path = ROOT / "release-manifest.json"
    if not manifest_path.is_file():
        problems.append("missing:release-manifest.json")
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        docs_site = manifest.get("docs_site", {})
        publishing = docs_site.get("publishing", {})
        validation = manifest.get("validation", {})
        retention = validation.get("artifact_retention", {})
        release_evidence = manifest.get("release_evidence", {})
        notification = manifest.get("deployment_notification", {})
        monitor = manifest.get("mailbox_monitor", {})
        workflows = manifest.get("workflows", {})

        if docs_site.get("mode") != "dependency-free-governed-static-html":
            problems.append("manifest-docs-mode")
        if docs_site.get("builder") != "tools/build_governed_docs_site.py":
            problems.append("manifest-docs-builder")
        if docs_site.get("builder_tests") != "tools/test_governed_docs_builder.py":
            problems.append("manifest-docs-builder-tests")
        if docs_site.get("external_site_generator_required") is not False:
            problems.append("manifest-external-site-generator")
        if publishing.get("docs_builder") != "tools/build_governed_docs_site.py":
            problems.append("manifest-publishing-docs-builder")
        if publishing.get("mailbox_poller") != "tools/poll_deployment_notification_mailbox.py":
            problems.append("manifest-publishing-mailbox-poller")
        if retention.get("mailbox_monitor_state_artifact") != "deployment-mailbox-monitor-state":
            problems.append("manifest-monitor-state-artifact")
        if retention.get("mailbox_monitor_retention_days") != 90:
            problems.append("manifest-monitor-retention")
        if release_evidence.get("automatic_stable_authorization") is not False:
            problems.append("manifest-release-evidence-auto-stable")
        if release_evidence.get("public_review_fail_closed") is not True:
            problems.append("manifest-release-evidence-public-review-fail-closed")
        if notification.get("mailbox_password_allowed") is not False:
            problems.append("manifest-notification-mailbox-password")
        if notification.get("email_is_authority") is not False:
            problems.append("manifest-notification-email-authority")
        if notification.get("inbound_result") != "verification-required next-task candidate":
            problems.append("manifest-notification-inbound-result")
        required_attachments = {
            "status/deployment-notification-email.md",
            "status/deployment-notification-envelope.json",
            "status/deployed-evidence-bundle.json",
        }
        if set(notification.get("attachments", [])) != required_attachments:
            problems.append("manifest-notification-attachments")
        if monitor.get("state_artifact") != "deployment-mailbox-monitor-state":
            problems.append("manifest-mailbox-monitor-state")
        if monitor.get("one_task_per_notification_identity") is not True:
            problems.append("manifest-mailbox-monitor-idempotence")
        if monitor.get("automatic_release_authority") is not False:
            problems.append("manifest-mailbox-monitor-authority")
        if workflows.get("workflow_pair_count") != 4:
            problems.append("manifest-workflow-pair-count")
        if workflows.get("mailbox_monitoring") != "scheduled-durable-replay-protected":
            problems.append("manifest-mailbox-monitoring")

    result = {
        "checked": [str(path.relative_to(ROOT)) for path in FILES.values()] + ["release-manifest.json"],
        "problem_count": len(problems),
        "problems": problems,
        "result": "pass" if not problems else "fail",
    }
    print(json.dumps(result, indent=2))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())

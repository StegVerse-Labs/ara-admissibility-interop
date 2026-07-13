#!/usr/bin/env python3
"""Check generated docs site, publishing, evidence, and notification invariants."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS_INDEX = ROOT / "docs" / "index.md"
DOCS_CONFIG = ROOT / "docs" / "_config.yml"
PAGES_WORKFLOW = ROOT / ".github" / "workflows" / "docs-pages.yml"
IOS_PAGES_WORKFLOW = ROOT / "iosnoperiod" / "github" / "workflows" / "docs-pages.yml"
REPO_CHECK_WORKFLOW = ROOT / ".github" / "workflows" / "repo-check.yml"
IOS_REPO_CHECK_WORKFLOW = ROOT / "iosnoperiod" / "github" / "workflows" / "repo-check.yml"
NOTIFY_WORKFLOW = ROOT / ".github" / "workflows" / "deployment-notification.yml"
IOS_NOTIFY_WORKFLOW = ROOT / "iosnoperiod" / "github" / "workflows" / "deployment-notification.yml"
MANIFEST = ROOT / "release-manifest.json"
STAMP_TOOL = ROOT / "tools" / "stamp_built_site.py"
EVIDENCE_VERIFIER = ROOT / "tools" / "verify_publication_evidence.py"
RELEASE_EVALUATOR = ROOT / "tools" / "evaluate_release_evidence.py"
NOTIFICATION_GENERATOR = ROOT / "tools" / "generate_deployment_notification.py"
NOTIFICATION_SENDER = ROOT / "tools" / "send_deployment_notification.py"
NOTIFICATION_INGESTOR = ROOT / "tools" / "ingest_deployment_notification.py"

REQUIRED_INDEX_LINKS = [
    "release-readiness.md",
    "release-checklist.md",
    "dependency-policy.md",
    "optional-strict-validation.md",
    "validation-report-guide.md",
    "publication-evidence-verification.md",
    "release-evidence-decision.md",
    "release-gate-promotion.md",
    "deployment-email-monitoring.md",
    "../admissibility/non-claims.md",
]

REQUIRED_CONFIG_PHRASES = [
    "title: ARA Admissibility Interop",
    "plugins: []",
    "markdown: kramdown",
]

REQUIRED_PAGES_WORKFLOW_PHRASES = [
    "uses: actions/configure-pages@v5",
    "uses: actions/jekyll-build-pages@v1",
    "uses: actions/upload-pages-artifact@v3",
    "uses: actions/deploy-pages@v4",
    'json.load(open("publication-manifest.json"))["publish_root"]',
    "source: ./${{ needs.publication-gate.outputs.publish_root }}",
    "destination: ./_site",
    "path: ./_site",
    "python3 tools/stamp_built_site.py",
    "deployment-identity.json",
    "Verify live deployed root and commit identity",
    "ARA Admissibility Interop Docs",
    "PUBLICATION_ARTIFACT_ROOT: _site",
    "PUBLICATION_ARTIFACT_KIND: built_site",
    "LIVE_ROOT_VERIFICATION=passed",
    "LIVE_ROOT_DEPLOYED_COMMIT_SHA=",
    "status/deployed-live-root.html",
    "status/deployed-identity.json",
    "python3 tools/evaluate_release_evidence.py",
    "--require-public-review-allow",
    "status/release-evidence-decision.json",
    "status/deployed-evidence-bundle.json",
    "status/deployment-notification-email.md",
    "status/deployment-notification-envelope.json",
]

REQUIRED_NOTIFY_WORKFLOW_PHRASES = [
    "name: Deployment Notification",
    "workflow_run:",
    "workflows:",
    "- Docs Pages",
    "github.event.workflow_run.conclusion == 'success'",
    "gh run download",
    "deployed-publication-evidence",
    "python3 tools/verify_evidence_bundle_manifest.py",
    "python3 tools/verify_publication_evidence.py",
    "python3 tools/generate_deployment_notification.py",
    "python3 tools/send_deployment_notification.py",
    "STEGVERSE_MAIL_TENANT_ID",
    "STEGVERSE_MAIL_CLIENT_ID",
    "STEGVERSE_MAIL_CLIENT_SECRET",
    "STEGVERSE_MAIL_SENDER",
    "STEGVERSE_MAIL_RECIPIENT",
    "deployment-notification-delivery.json",
    "name: governed-deployment-notification",
]

REQUIRED_REPO_CHECK_WORKFLOW_PHRASES = [
    "uses: actions/upload-artifact@v4",
    "name: generated-status",
    "path: status/generated-status.json",
    "python3 tools/test_publication_evidence_verifier.py",
    "python3 tools/test_release_evidence_evaluator.py",
    "python3 tools/test_evidence_bundle_manifest.py",
    "python3 tools/test_release_gate_promotion.py",
    "python3 tools/test_deployment_notification.py",
    "python3 tools/test_deployment_notification_transport.py",
]

REQUIRED_STAMP_TOOL_PHRASES = [
    '"identity_type": "governed-pages-deployment-identity"',
    '"commit_sha": commit_sha',
    "deployment-identity.json",
    "stegverse-deployment-commit",
]

REQUIRED_EVIDENCE_VERIFIER_PHRASES = [
    "def verify(",
    "artifact-tree-mismatch",
    "identity-commit-mismatch",
    "live-root-hash-mismatch",
]

REQUIRED_RELEASE_EVALUATOR_PHRASES = [
    "governed-release-evidence-decision",
    "public_review_decision",
    "stable_release_decision",
    "stable_release_automatically_authorized",
    "--artifact-root",
    "--identity-file",
    "--live-root-file",
]

REQUIRED_NOTIFICATION_GENERATOR_PHRASES = [
    "Current goal",
    "Current publication posture",
    "Current release gate",
    "Boundary",
    "Next tasks",
    "handoff_sha256",
    "body_sha256",
]

REQUIRED_NOTIFICATION_SENDER_PHRASES = [
    "microsoft-graph-sendmail",
    "client_credentials",
    "https://graph.microsoft.com/.default",
    "sendMail",
    "partial mail configuration",
    "delivery_status",
    "not_configured",
]

REQUIRED_NOTIFICATION_INGESTOR_PHRASES = [
    "governed-deployment-evidence-verification-candidate",
    "verification_required",
    "body-sha256",
    "bundle-sha256-mismatch",
    "do not set stable_release_authorized",
]


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
    checks = [
        (DOCS_INDEX, REQUIRED_INDEX_LINKS, "docs-index"),
        (DOCS_CONFIG, REQUIRED_CONFIG_PHRASES, "docs-config"),
        (PAGES_WORKFLOW, REQUIRED_PAGES_WORKFLOW_PHRASES, "pages-workflow"),
        (IOS_PAGES_WORKFLOW, REQUIRED_PAGES_WORKFLOW_PHRASES, "ios-pages-workflow"),
        (NOTIFY_WORKFLOW, REQUIRED_NOTIFY_WORKFLOW_PHRASES, "notify-workflow"),
        (IOS_NOTIFY_WORKFLOW, REQUIRED_NOTIFY_WORKFLOW_PHRASES, "ios-notify-workflow"),
        (REPO_CHECK_WORKFLOW, REQUIRED_REPO_CHECK_WORKFLOW_PHRASES, "repo-check-workflow"),
        (IOS_REPO_CHECK_WORKFLOW, REQUIRED_REPO_CHECK_WORKFLOW_PHRASES, "ios-repo-check-workflow"),
        (STAMP_TOOL, REQUIRED_STAMP_TOOL_PHRASES, "stamp-tool"),
        (EVIDENCE_VERIFIER, REQUIRED_EVIDENCE_VERIFIER_PHRASES, "evidence-verifier"),
        (RELEASE_EVALUATOR, REQUIRED_RELEASE_EVALUATOR_PHRASES, "release-evaluator"),
        (NOTIFICATION_GENERATOR, REQUIRED_NOTIFICATION_GENERATOR_PHRASES, "notification-generator"),
        (NOTIFICATION_SENDER, REQUIRED_NOTIFICATION_SENDER_PHRASES, "notification-sender"),
        (NOTIFICATION_INGESTOR, REQUIRED_NOTIFICATION_INGESTOR_PHRASES, "notification-ingestor"),
    ]
    for path, phrases, label in checks:
        check_contains(path, phrases, problems, label)

    if not MANIFEST.is_file():
        problems.append("missing:release-manifest.json")
    else:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        primary_docs = manifest.get("primary_docs", {})
        publishing = manifest.get("docs_site", {}).get("publishing", {})
        validation = manifest.get("validation", {})
        retention = validation.get("artifact_retention", {})
        release_evidence = manifest.get("release_evidence", {})
        notification = manifest.get("deployment_notification", {})
        workflows = manifest.get("workflows", {})

        expected = {
            "primary-docs-email-monitoring": (
                primary_docs.get("deployment_email_monitoring"),
                "docs/deployment-email-monitoring.md",
            ),
            "publishing-notification-sender": (
                publishing.get("notification_sender"),
                "tools/send_deployment_notification.py",
            ),
            "publishing-notification-ingestor": (
                publishing.get("notification_ingestor"),
                "tools/ingest_deployment_notification.py",
            ),
            "retention-notification-delivery": (
                retention.get("deployment_notification_delivery"),
                "status/deployment-notification-delivery.json",
            ),
            "workflow-notification-canonical": (
                workflows.get("deployment_notification_canonical_path"),
                ".github/workflows/deployment-notification.yml",
            ),
            "workflow-notification-ios": (
                workflows.get("deployment_notification_ios_safe_path"),
                "iosnoperiod/github/workflows/deployment-notification.yml",
            ),
        }
        for label, (actual, wanted) in expected.items():
            if actual != wanted:
                problems.append(f"manifest-{label}")

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

    result = {
        "checked": [str(path.relative_to(ROOT)) for path, _, _ in checks] + ["release-manifest.json"],
        "problem_count": len(problems),
        "problems": problems,
        "result": "pass" if not problems else "fail",
    }
    print(json.dumps(result, indent=2))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())

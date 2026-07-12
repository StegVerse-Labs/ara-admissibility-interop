#!/usr/bin/env python3
"""Check generated docs site, publishing, and artifact automation invariants."""

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
MANIFEST = ROOT / "release-manifest.json"
STAMP_TOOL = ROOT / "tools" / "stamp_built_site.py"
EVIDENCE_VERIFIER = ROOT / "tools" / "verify_publication_evidence.py"
RELEASE_EVALUATOR = ROOT / "tools" / "evaluate_release_evidence.py"

REQUIRED_INDEX_LINKS = [
    "release-readiness.md",
    "release-checklist.md",
    "dependency-policy.md",
    "optional-strict-validation.md",
    "validation-report-guide.md",
    "publication-evidence-verification.md",
    "release-evidence-decision.md",
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
    "LIVE_ROOT_VERIFIED_AT=",
    "LIVE_ROOT_HTTP_STATUS=",
    "LIVE_ROOT_FINAL_URL=",
    "LIVE_ROOT_EXPECTED_MARKER=",
    "LIVE_ROOT_MARKER_FOUND=true",
    "LIVE_ROOT_BODY_SHA256=",
    "LIVE_ROOT_BODY_SIZE_BYTES=",
    "LIVE_ROOT_DEPLOYED_COMMIT_SHA=",
    "LIVE_IDENTITY_HTTP_STATUS=",
    "LIVE_IDENTITY_FINAL_URL=",
    "LIVE_IDENTITY_BODY_SHA256=",
    "status/deployed-live-root.html",
    "status/deployed-identity.json",
    "Evaluate deployed release evidence",
    "python3 tools/evaluate_release_evidence.py",
    "--artifact-root _site",
    "--identity-file status/deployed-identity.json",
    "--live-root-file status/deployed-live-root.html",
    "--require-public-review-allow",
    "status/release-evidence-decision.json",
    "status/release-evidence-decision.md",
    "_site",
]

REQUIRED_STAMP_TOOL_PHRASES = [
    '"identity_type": "governed-pages-deployment-identity"',
    '"commit_sha": commit_sha',
    'deployment-identity.json',
    'stegverse-deployment-commit',
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

REQUIRED_REPO_CHECK_WORKFLOW_PHRASES = [
    "uses: actions/upload-artifact@v4",
    "name: generated-status",
    "path: status/generated-status.json",
    "name: validation-report",
    "path: status/validation-report.md",
    "python3 tools/test_publication_evidence_verifier.py",
    "python3 tools/test_release_evidence_evaluator.py",
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

    check_contains(DOCS_INDEX, REQUIRED_INDEX_LINKS, problems, "docs-index")
    check_contains(DOCS_CONFIG, REQUIRED_CONFIG_PHRASES, problems, "docs-config")
    check_contains(PAGES_WORKFLOW, REQUIRED_PAGES_WORKFLOW_PHRASES, problems, "pages-workflow")
    check_contains(IOS_PAGES_WORKFLOW, REQUIRED_PAGES_WORKFLOW_PHRASES, problems, "ios-pages-workflow")
    check_contains(STAMP_TOOL, REQUIRED_STAMP_TOOL_PHRASES, problems, "stamp-tool")
    check_contains(EVIDENCE_VERIFIER, REQUIRED_EVIDENCE_VERIFIER_PHRASES, problems, "evidence-verifier")
    check_contains(RELEASE_EVALUATOR, REQUIRED_RELEASE_EVALUATOR_PHRASES, problems, "release-evaluator")
    check_contains(REPO_CHECK_WORKFLOW, REQUIRED_REPO_CHECK_WORKFLOW_PHRASES, problems, "repo-check-workflow")
    check_contains(IOS_REPO_CHECK_WORKFLOW, REQUIRED_REPO_CHECK_WORKFLOW_PHRASES, problems, "ios-repo-check-workflow")

    if not MANIFEST.is_file():
        problems.append("missing:release-manifest.json")
    else:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        docs_site = manifest.get("docs_site", {})
        primary_docs = manifest.get("primary_docs", {})
        workflows = manifest.get("workflows", {})
        validation = manifest.get("validation", {})
        publishing = docs_site.get("publishing", {})
        retention = validation.get("artifact_retention", {})
        release_evidence = manifest.get("release_evidence", {})
        if docs_site.get("entrypoint") != "docs/index.md":
            problems.append("manifest-docs-entrypoint")
        if docs_site.get("config") != "docs/_config.yml":
            problems.append("manifest-docs-config")
        if primary_docs.get("docs_index") != "docs/index.md":
            problems.append("manifest-primary-docs-index")
        if primary_docs.get("docs_config") != "docs/_config.yml":
            problems.append("manifest-primary-docs-config")
        if publishing.get("canonical_workflow") != ".github/workflows/docs-pages.yml":
            problems.append("manifest-docs-canonical-workflow")
        if publishing.get("ios_safe_workflow") != "iosnoperiod/github/workflows/docs-pages.yml":
            problems.append("manifest-docs-ios-workflow")
        if publishing.get("manual_publish_required") is not False:
            problems.append("manifest-manual-docs-publish-not-false")
        if publishing.get("evidence_verifier") != "tools/verify_publication_evidence.py":
            problems.append("manifest-publishing-evidence-verifier")
        if publishing.get("release_evaluator") != "tools/evaluate_release_evidence.py":
            problems.append("manifest-publishing-release-evaluator")
        if retention.get("canonical_workflow") != ".github/workflows/repo-check.yml":
            problems.append("manifest-retention-canonical-workflow")
        if retention.get("ios_safe_workflow") != "iosnoperiod/github/workflows/repo-check.yml":
            problems.append("manifest-retention-ios-workflow")
        if retention.get("manual_artifact_retention_required") is not False:
            problems.append("manifest-manual-artifact-retention-not-false")
        if retention.get("release_evidence_decision_json") != "status/release-evidence-decision.json":
            problems.append("manifest-release-decision-json")
        if retention.get("release_evidence_decision_markdown") != "status/release-evidence-decision.md":
            problems.append("manifest-release-decision-markdown")
        if workflows.get("docs_pages_canonical_path") != ".github/workflows/docs-pages.yml":
            problems.append("manifest-workflows-docs-canonical-path")
        if workflows.get("docs_pages_ios_safe_path") != "iosnoperiod/github/workflows/docs-pages.yml":
            problems.append("manifest-workflows-docs-ios-path")
        if workflows.get("manual_docs_publish_required") is not False:
            problems.append("manifest-workflows-manual-docs-publish-not-false")
        if workflows.get("manual_artifact_retention_required") is not False:
            problems.append("manifest-workflows-manual-artifact-retention-not-false")
        if workflows.get("artifact_upload") != "automated":
            problems.append("manifest-workflows-artifact-upload-not-automated")
        if workflows.get("deployment_url_verification") != "required":
            problems.append("manifest-workflows-deployment-url-verification")
        if workflows.get("release_evidence_decision") != "required":
            problems.append("manifest-workflows-release-evidence-decision")
        if release_evidence.get("automatic_stable_authorization") is not False:
            problems.append("manifest-release-evidence-auto-stable")
        if release_evidence.get("public_review_fail_closed") is not True:
            problems.append("manifest-release-evidence-public-review-fail-closed")

    result = {
        "checked": [
            "docs/index.md",
            "docs/_config.yml",
            ".github/workflows/docs-pages.yml",
            "iosnoperiod/github/workflows/docs-pages.yml",
            "tools/stamp_built_site.py",
            "tools/verify_publication_evidence.py",
            "tools/evaluate_release_evidence.py",
            ".github/workflows/repo-check.yml",
            "iosnoperiod/github/workflows/repo-check.yml",
            "release-manifest.json",
        ],
        "problem_count": len(problems),
        "problems": problems,
        "result": "pass" if not problems else "fail",
    }
    print(json.dumps(result, indent=2))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())

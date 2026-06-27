#!/usr/bin/env python3
"""Check self-management automation policy invariants."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "automation-policy.json"
MANIFEST = ROOT / "release-manifest.json"


def main() -> int:
    problems: list[str] = []

    if not POLICY.is_file():
        problems.append("missing:automation-policy.json")
        policy = {}
    else:
        policy = json.loads(POLICY.read_text(encoding="utf-8"))

    if policy.get("manual_tasks_allowed") is not False:
        problems.append("policy-manual-tasks-not-false")

    automated_paths = policy.get("automated_paths", {})
    validation = automated_paths.get("validation", {})
    docs_publishing = automated_paths.get("docs_publishing", {})
    dependency_policy = automated_paths.get("dependency_policy", {})
    docs_site_policy = automated_paths.get("docs_site_policy", {})

    if validation.get("command") != "python3 tools/generate_validation_report.py":
        problems.append("policy-validation-command")
    if validation.get("retains_artifacts") is not True:
        problems.append("policy-validation-retains-artifacts-not-true")
    if validation.get("publishes_step_summary") is not True:
        problems.append("policy-validation-step-summary-not-true")
    if docs_publishing.get("manual_publish_required") is not False:
        problems.append("policy-docs-manual-publish-not-false")
    if dependency_policy.get("required_dependencies") != []:
        problems.append("policy-required-dependencies-not-empty")
    if dependency_policy.get("checker") != "tools/check_dependency_policy.py":
        problems.append("policy-dependency-checker")
    if docs_site_policy.get("checker") != "tools/check_docs_site.py":
        problems.append("policy-docs-site-checker")

    completion_rule = policy.get("goal_completion_rule", {})
    if completion_rule.get("when_goal_activation_percent_is") != 100:
        problems.append("policy-goal-completion-threshold")
    if "do not invent manual work" not in completion_rule.get("next_step", ""):
        problems.append("policy-goal-completion-no-manual-work-boundary")

    if not MANIFEST.is_file():
        problems.append("missing:release-manifest.json")
    else:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        workflows = manifest.get("workflows", {})
        if workflows.get("manual_docs_publish_required") is not False:
            problems.append("manifest-manual-docs-publish-not-false")
        if workflows.get("manual_artifact_retention_required") is not False:
            problems.append("manifest-manual-artifact-retention-not-false")
        if workflows.get("artifact_upload") != "automated":
            problems.append("manifest-artifact-upload-not-automated")

    result = {
        "checked": ["automation-policy.json", "release-manifest.json"],
        "problem_count": len(problems),
        "problems": problems,
        "result": "pass" if not problems else "fail",
    }
    print(json.dumps(result, indent=2))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())

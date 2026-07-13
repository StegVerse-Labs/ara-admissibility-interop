#!/usr/bin/env python3
"""Verify a received deployment notification and emit a next-task candidate.

The email is treated only as a signal. The resulting task remains verification-
required and cannot authorize release-gate promotion or stable release.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENVELOPE = ROOT / "status" / "deployment-notification-envelope.json"
DEFAULT_BODY = ROOT / "status" / "deployment-notification-email.md"
DEFAULT_BUNDLE = ROOT / "status" / "deployed-evidence-bundle.json"
DEFAULT_OUTPUT = ROOT / "status" / "deployment-next-task-candidate.json"
REQUIRED_SECTIONS = {
    "Current goal",
    "Current publication posture",
    "Current release gate",
    "Boundary",
    "Next tasks",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(envelope: dict, body: bytes, bundle: dict) -> list[str]:
    problems: list[str] = []
    if envelope.get("notification_type") != "governed-deployment-evidence-available":
        problems.append("notification-type")
    if envelope.get("authority_boundary") != "Email notification is a signal, not release authority.":
        problems.append("authority-boundary")
    if envelope.get("body_sha256") != sha256_bytes(body):
        problems.append("body-sha256")
    if envelope.get("commit_sha") != bundle.get("commit_sha"):
        problems.append("commit-mismatch")
    if envelope.get("bundle_sha256") != bundle.get("bundle_sha256"):
        problems.append("bundle-sha256-mismatch")
    if envelope.get("artifact_name") != "deployed-publication-evidence":
        problems.append("artifact-name")
    if envelope.get("next_action") != "retrieve-and-independently-verify":
        problems.append("next-action")
    included = envelope.get("included_handoff_sections")
    if not isinstance(included, list) or not REQUIRED_SECTIONS.issubset(set(included)):
        problems.append("handoff-sections")
    subject = envelope.get("subject")
    if not isinstance(subject, str) or "[DEPLOYMENT-EVIDENCE]" not in subject:
        problems.append("subject")
    if envelope.get("public_review_decision") != "ALLOW":
        problems.append("public-review-not-allow")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--envelope", type=Path, default=DEFAULT_ENVELOPE)
    parser.add_argument("--body", type=Path, default=DEFAULT_BODY)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        envelope = load_json(args.envelope)
        body = args.body.read_bytes()
        bundle = load_json(args.bundle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"DEPLOYMENT_NOTIFICATION_INGEST=FAIL-CLOSED\nreason={exc}")
        return 1

    problems = validate(envelope, body, bundle)
    candidate = {
        "schema_version": "1.0.0",
        "task_type": "governed-deployment-evidence-verification-candidate",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": envelope.get("repository"),
        "commit_sha": envelope.get("commit_sha"),
        "workflow_run_id": envelope.get("workflow_run_id"),
        "artifact_name": envelope.get("artifact_name"),
        "bundle_sha256": envelope.get("bundle_sha256"),
        "source_notification_subject": envelope.get("subject"),
        "notification_verification": "pass" if not problems else "fail",
        "problems": problems,
        "task_status": "verification_required" if not problems else "blocked",
        "required_actions": [
            "retrieve deployed-publication-evidence artifact from the identified workflow run",
            "verify status/deployed-evidence-bundle.json against the retrieved artifact",
            "verify the publication receipt, built site, captured live root, and deployment identity",
            "evaluate release evidence after independent verification",
            "produce an evidence-bounded gate-promotion proposal",
        ] if not problems else [],
        "prohibited_actions": [
            "do not treat the email as deployment evidence",
            "do not promote release gates before artifact verification",
            "do not set repo_check_workflow_verified from Pages evidence",
            "do not set stable_release_authorized",
            "do not create a stable release tag",
        ],
        "authority_boundary": "The notification creates a verification candidate, not execution or release authority.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")
    print("DEPLOYMENT_NOTIFICATION_INGEST=" + ("CANDIDATE_CREATED" if not problems else "BLOCKED"))
    print(f"output={args.output}")
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())

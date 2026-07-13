#!/usr/bin/env python3
"""Regression tests for governed notification deduplication and replay handling."""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
from pathlib import Path

from ingest_deployment_notification import validate
from process_deployment_notification_once import (
    build_task,
    empty_ledger,
    notification_identity,
    same_transition,
)


def body_bytes() -> bytes:
    return (
        "Subject: [StegVerse][DEPLOYMENT-EVIDENCE][ARA][ALLOW] abcdef123456\n\n"
        "# Governed Deployment Evidence Notification\n\n"
        "## Handoff — Current goal\nGoal\n\n"
        "## Handoff — Current publication posture\nPosture\n\n"
        "## Handoff — Current release gate\nGate\n\n"
        "## Handoff — Boundary\nBoundary\n\n"
        "## Handoff — Next tasks\nTasks\n"
    ).encode("utf-8")


def fixture() -> tuple[dict, bytes, dict]:
    body = body_bytes()
    envelope = {
        "schema_version": "1.0.0",
        "notification_type": "governed-deployment-evidence-available",
        "subject": "[StegVerse][DEPLOYMENT-EVIDENCE][ARA][ALLOW] abcdef123456",
        "repository": "StegVerse-Labs/ara-admissibility-interop",
        "commit_sha": "a" * 40,
        "workflow_run_id": "12345",
        "workflow_run_attempt": "1",
        "artifact_name": "deployed-publication-evidence",
        "bundle_sha256": "b" * 64,
        "body_sha256": hashlib.sha256(body).hexdigest(),
        "public_review_decision": "ALLOW",
        "stable_release_decision": "BLOCK",
        "included_handoff_sections": [
            "Current goal",
            "Current publication posture",
            "Current release gate",
            "Boundary",
            "Next tasks",
        ],
        "next_action": "retrieve-and-independently-verify",
        "authority_boundary": "Email notification is a signal, not release authority.",
    }
    bundle = {
        "bundle_type": "governed-deployment-evidence-bundle",
        "commit_sha": envelope["commit_sha"],
        "bundle_sha256": envelope["bundle_sha256"],
    }
    return envelope, body, bundle


def assert_true(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def main() -> int:
    envelope, body, bundle = fixture()
    assert_true(validate(envelope, body, bundle) == [], "valid fixture")

    identity = notification_identity(envelope)
    assert_true(len(identity) == 64, "identity length")
    assert_true(identity == notification_identity(copy.deepcopy(envelope)), "identity deterministic")

    changed_body = copy.deepcopy(envelope)
    changed_body["body_sha256"] = "c" * 64
    assert_true(notification_identity(changed_body) != identity, "body hash changes identity")
    assert_true(same_transition({
        "repository": envelope["repository"],
        "commit_sha": envelope["commit_sha"],
        "workflow_run_id": envelope["workflow_run_id"],
    }, changed_body), "same transition conflict")

    changed_run = copy.deepcopy(envelope)
    changed_run["workflow_run_id"] = "12346"
    assert_true(not same_transition({
        "repository": envelope["repository"],
        "commit_sha": envelope["commit_sha"],
        "workflow_run_id": envelope["workflow_run_id"],
    }, changed_run), "different run is new transition")

    task = build_task(envelope, identity)
    assert_true(task["notification_identity"] == identity, "task identity")
    assert_true(task["task_status"] == "verification_required", "task requires verification")
    assert_true("do not set stable_release_authorized" in task["prohibited_actions"], "stable authority protected")

    ledger = empty_ledger()
    assert_true(ledger["entry_count"] == 0 and ledger["entries"] == [], "empty ledger")
    assert_true("does not create release authority" in ledger["boundary"], "ledger boundary")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        ledger_path = root / "ledger.json"
        ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
        loaded = json.loads(ledger_path.read_text(encoding="utf-8"))
        assert_true(loaded["ledger_type"] == "governed-deployment-notification-ledger", "ledger persistence")

    print(json.dumps({
        "result": "pass",
        "tests": [
            "valid-notification",
            "deterministic-identity",
            "body-hash-conflict",
            "different-run-new-transition",
            "verification-required-task",
            "stable-authority-protected",
            "empty-ledger-boundary",
        ],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

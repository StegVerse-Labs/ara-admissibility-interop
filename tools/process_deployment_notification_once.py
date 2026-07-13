#!/usr/bin/env python3
"""Process one governed deployment notification with durable deduplication.

The notification remains a signal. This tool validates it through the existing
inbound verifier, then records a deterministic notification identity in a
ledger. Identical replays are idempotent no-ops. Conflicting replays fail
closed. The tool cannot promote release gates or authorize releases.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from ingest_deployment_notification import load_json, validate

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENVELOPE = ROOT / "status" / "deployment-notification-envelope.json"
DEFAULT_BODY = ROOT / "status" / "deployment-notification-email.md"
DEFAULT_BUNDLE = ROOT / "status" / "deployed-evidence-bundle.json"
DEFAULT_LEDGER = ROOT / "status" / "deployment-notification-ledger.json"
DEFAULT_TASK = ROOT / "status" / "deployment-next-task-candidate.json"
DEFAULT_RECEIPT = ROOT / "status" / "deployment-notification-processing.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def notification_identity(envelope: dict) -> str:
    fields = (
        envelope.get("repository"),
        envelope.get("commit_sha"),
        str(envelope.get("workflow_run_id")),
        envelope.get("bundle_sha256"),
        envelope.get("body_sha256"),
    )
    digest = hashlib.sha256()
    for value in fields:
        digest.update(str(value or "").encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def empty_ledger() -> dict:
    return {
        "schema_version": "1.0.0",
        "ledger_type": "governed-deployment-notification-ledger",
        "updated_at": None,
        "entry_count": 0,
        "entries": [],
        "boundary": "Ledger continuity prevents duplicate task creation; it does not create release authority.",
    }


def load_ledger(path: Path) -> dict:
    if not path.exists():
        return empty_ledger()
    ledger = load_json(path)
    if ledger.get("ledger_type") != "governed-deployment-notification-ledger":
        raise ValueError("unexpected ledger type")
    entries = ledger.get("entries")
    if not isinstance(entries, list):
        raise ValueError("ledger entries must be a list")
    return ledger


def same_transition(entry: dict, envelope: dict) -> bool:
    return (
        entry.get("repository") == envelope.get("repository")
        and entry.get("commit_sha") == envelope.get("commit_sha")
        and str(entry.get("workflow_run_id")) == str(envelope.get("workflow_run_id"))
    )


def build_task(envelope: dict, identity: str) -> dict:
    return {
        "schema_version": "1.1.0",
        "task_type": "governed-deployment-evidence-verification-candidate",
        "generated_at": utc_now(),
        "notification_identity": identity,
        "repository": envelope.get("repository"),
        "commit_sha": envelope.get("commit_sha"),
        "workflow_run_id": envelope.get("workflow_run_id"),
        "artifact_name": envelope.get("artifact_name"),
        "bundle_sha256": envelope.get("bundle_sha256"),
        "source_notification_subject": envelope.get("subject"),
        "notification_verification": "pass",
        "task_status": "verification_required",
        "required_actions": [
            "retrieve deployed-publication-evidence artifact from the identified workflow run",
            "verify status/deployed-evidence-bundle.json against the retrieved artifact",
            "verify the publication receipt, built site, captured live root, and deployment identity",
            "evaluate release evidence after independent verification",
            "produce an evidence-bounded gate-promotion proposal",
        ],
        "prohibited_actions": [
            "do not treat the email as deployment evidence",
            "do not promote release gates before artifact verification",
            "do not set repo_check_workflow_verified from Pages evidence",
            "do not set stable_release_authorized",
            "do not create a stable release tag",
        ],
        "authority_boundary": "The notification creates a verification candidate, not execution or release authority.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--envelope", type=Path, default=DEFAULT_ENVELOPE)
    parser.add_argument("--body", type=Path, default=DEFAULT_BODY)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--task", type=Path, default=DEFAULT_TASK)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--max-entries", type=int, default=1000)
    args = parser.parse_args()

    try:
        envelope = load_json(args.envelope)
        body = args.body.read_bytes()
        bundle = load_json(args.bundle)
        ledger = load_ledger(args.ledger)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"DEPLOYMENT_NOTIFICATION_PROCESS=FAIL-CLOSED\nreason={exc}")
        return 1

    problems = validate(envelope, body, bundle)
    if problems:
        result = {
            "schema_version": "1.0.0",
            "processing_result": "blocked",
            "processed_at": utc_now(),
            "problems": problems,
            "authority_boundary": "Blocked notification cannot create a task or alter the replay ledger.",
        }
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print("DEPLOYMENT_NOTIFICATION_PROCESS=BLOCKED")
        return 1

    identity = notification_identity(envelope)
    entries = ledger["entries"]
    exact = next((entry for entry in entries if entry.get("notification_identity") == identity), None)
    conflicts = [
        entry for entry in entries
        if same_transition(entry, envelope)
        and entry.get("notification_identity") != identity
    ]

    if conflicts:
        result = {
            "schema_version": "1.0.0",
            "processing_result": "conflicting_replay_blocked",
            "processed_at": utc_now(),
            "notification_identity": identity,
            "conflicting_identities": [entry.get("notification_identity") for entry in conflicts],
            "authority_boundary": "Conflicting replay cannot create a task or alter release state.",
        }
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print("DEPLOYMENT_NOTIFICATION_PROCESS=CONFLICTING_REPLAY_BLOCKED")
        return 1

    if exact is not None:
        result = {
            "schema_version": "1.0.0",
            "processing_result": "duplicate_noop",
            "processed_at": utc_now(),
            "notification_identity": identity,
            "first_processed_at": exact.get("processed_at"),
            "task_created": False,
            "ledger_changed": False,
            "authority_boundary": "Duplicate notification creates no additional task or authority.",
        }
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print("DEPLOYMENT_NOTIFICATION_PROCESS=DUPLICATE_NOOP")
        return 0

    task = build_task(envelope, identity)
    entry = {
        "notification_identity": identity,
        "processed_at": task["generated_at"],
        "repository": envelope.get("repository"),
        "commit_sha": envelope.get("commit_sha"),
        "workflow_run_id": envelope.get("workflow_run_id"),
        "workflow_run_attempt": envelope.get("workflow_run_attempt"),
        "bundle_sha256": envelope.get("bundle_sha256"),
        "body_sha256": sha256_bytes(body),
        "task_status": task["task_status"],
    }
    entries.append(entry)
    entries.sort(key=lambda item: (str(item.get("repository")), str(item.get("workflow_run_id")), item.get("notification_identity", "")))
    if len(entries) > args.max_entries:
        ledger["entries"] = entries[-args.max_entries:]
    ledger["updated_at"] = utc_now()
    ledger["entry_count"] = len(ledger["entries"])

    args.ledger.parent.mkdir(parents=True, exist_ok=True)
    args.task.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.ledger.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    args.task.write_text(json.dumps(task, indent=2) + "\n", encoding="utf-8")
    result = {
        "schema_version": "1.0.0",
        "processing_result": "candidate_created",
        "processed_at": utc_now(),
        "notification_identity": identity,
        "task_created": True,
        "ledger_changed": True,
        "ledger_entry_count": ledger["entry_count"],
        "authority_boundary": "Processing records continuity and creates a verification task, not release authority.",
    }
    args.receipt.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("DEPLOYMENT_NOTIFICATION_PROCESS=CANDIDATE_CREATED")
    print(f"notification_identity={identity}")
    print(f"ledger={args.ledger}")
    print(f"task={args.task}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

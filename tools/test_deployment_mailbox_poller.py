#!/usr/bin/env python3
"""Regression tests for governed TVC-backed deployment mailbox processing."""
from __future__ import annotations

import base64
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "poll_deployment_notification_mailbox.py"
spec = importlib.util.spec_from_file_location("poller", MODULE_PATH)
assert spec and spec.loader
poller = importlib.util.module_from_spec(spec)
spec.loader.exec_module(poller)


def assert_true(value: bool, label: str) -> None:
    if not value:
        raise AssertionError(label)


def sample_fetch_request() -> dict:
    return poller.build_fetch_request(
        monitor_mailbox="monitor@example.invalid",
        limit=5,
        ara_commit_sha="a" * 40,
        workflow_run_id="33120158075",
    )


def sample_provider_result(fetch_request: dict) -> dict:
    attachments = [
        {
            "name": name,
            "content_base64": base64.b64encode(name.encode("utf-8")).decode("ascii"),
        }
        for name in sorted(poller.REQUIRED_ATTACHMENTS)
    ]
    return {
        "decision": "ALLOW_OPERATION_RESULT",
        "result": {
            "mailbox_observed": True,
            "messages": [
                {
                    "message_id": "message-1",
                    "subject": "[StegVerse][DEPLOYMENT-EVIDENCE][ARA][ALLOW] abc123",
                    "has_attachments": True,
                    "received_timestamp": "2026-08-27T21:00:00Z",
                    "sender": "sender@example.invalid",
                    "attachments": attachments,
                }
            ],
        },
        "receipt": {
            "request_hash": fetch_request["request_hash"],
            "provider_operation_class": poller.FETCH_OPERATION,
            "ara_commit_sha": fetch_request["ara_commit_sha"],
            "workflow_run_id": fetch_request["workflow_run_id"],
            "credential_authority": "TV/TVC",
            "credential_material_exported": False,
            "access_token_exported": False,
            "authority_effect": False,
            "ara_release_authority_effect": "NONE",
            "runtime_activation_claimed": False,
        },
    }


def main() -> int:
    assert_true(
        poller.TVC_PROVIDER_ROUTE_REQUIRED == "TVC_ADMITTED_PROVIDER_ROUTE_REQUIRED",
        "tvc-route-required",
    )

    fetch = sample_fetch_request()
    unhashed = dict(fetch)
    declared = unhashed.pop("request_hash")
    assert_true(declared == poller.canonical_sha256(unhashed), "fetch-request-hash")
    assert_true(fetch["operation_class"] == poller.FETCH_OPERATION, "fetch-operation")
    assert_true(fetch["maximum_messages"] == 5, "fetch-limit")

    provider = sample_provider_result(fetch)
    messages = poller.validate_provider_result(fetch, provider)
    assert_true(len(messages) == 1, "provider-message-count")
    assert_true(poller.governed_message(messages[0]), "governed-message")

    tampered = json.loads(json.dumps(provider))
    tampered["receipt"]["request_hash"] = "0" * 64
    try:
        poller.validate_provider_result(fetch, tampered)
    except ValueError as exc:
        assert_true("request_hash" in str(exc), "provider-hash-mismatch-message")
    else:
        raise AssertionError("provider-hash-mismatch")

    leaked = json.loads(json.dumps(provider))
    leaked["receipt"]["credential_material_exported"] = True
    try:
        poller.validate_provider_result(fetch, leaked)
    except ValueError as exc:
        assert_true("credential" in str(exc), "provider-secret-export-message")
    else:
        raise AssertionError("provider-secret-export")

    mapped = poller.attachment_map(messages[0]["attachments"])
    assert_true(set(mapped) == poller.REQUIRED_ATTACHMENTS, "attachment-map")

    missing = list(messages[0]["attachments"])[:-1]
    try:
        poller.attachment_map(missing)
    except ValueError as exc:
        assert_true("missing required attachments" in str(exc), "missing-attachment-message")
    else:
        raise AssertionError("missing-attachment")

    mark = poller.build_mark_read_request(
        monitor_mailbox="monitor@example.invalid",
        message_id="message-1",
        processing_state="candidate_created",
        ara_commit_sha="a" * 40,
        workflow_run_id="33120158075",
    )
    mark_unhashed = dict(mark)
    mark_declared = mark_unhashed.pop("request_hash")
    assert_true(mark_declared == poller.canonical_sha256(mark_unhashed), "mark-read-request-hash")
    assert_true(mark["operation_class"] == poller.MARK_READ_OPERATION, "mark-read-operation")

    try:
        poller.build_mark_read_request(
            monitor_mailbox="monitor@example.invalid",
            message_id="message-1",
            processing_state="blocked",
            ara_commit_sha="a" * 40,
            workflow_run_id="33120158075",
        )
    except ValueError as exc:
        assert_true("not mark-read eligible" in str(exc), "blocked-mark-read-message")
    else:
        raise AssertionError("blocked-mark-read")

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        provider_path = root / "provider-result.json"
        fetch_path = root / "fetch-request.json"
        summary_path = root / "summary.json"
        ledger_path = root / "ledger.json"
        work_root = root / "work"
        mark_root = root / "mark-read"

        provider_path.write_text(json.dumps(provider), encoding="utf-8")
        original_argv = sys.argv
        original_process = poller.process_message
        try:
            poller.process_message = lambda message, files, work, ledger: ("candidate_created", work / "message-1")
            sys.argv = [
                str(MODULE_PATH),
                "--ledger", str(ledger_path),
                "--work-root", str(work_root),
                "--summary", str(summary_path),
                "--fetch-request", str(fetch_path),
                "--provider-result", str(provider_path),
                "--mark-read-outbox", str(mark_root),
                "--monitor-mailbox", "monitor@example.invalid",
                "--ara-commit-sha", "a" * 40,
                "--workflow-run-id", "33120158075",
                "--limit", "5",
            ]
            code = poller.main()
        finally:
            poller.process_message = original_process
            sys.argv = original_argv

        assert_true(code == 0, "provider-result-main-code")
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        assert_true(summary["provider_result_consumed"] is True, "provider-result-consumed")
        assert_true(summary["candidate_created"] == 1, "candidate-created")
        assert_true(summary["mark_read_requests_generated"] == 1, "mark-read-generated")
        assert_true(summary["mailbox_mutated"] is False, "ara-does-not-mutate-mailbox")
        mark_files = list(mark_root.glob("*.json"))
        assert_true(len(mark_files) == 1, "one-mark-read-file")
        emitted = json.loads(mark_files[0].read_text(encoding="utf-8"))
        assert_true(emitted["processing_state"] == "candidate_created", "mark-read-state")

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        summary_path = root / "summary.json"
        fetch_path = root / "fetch.json"
        original_argv = sys.argv
        try:
            sys.argv = [
                str(MODULE_PATH),
                "--summary", str(summary_path),
                "--fetch-request", str(fetch_path),
                "--monitor-mailbox", "monitor@example.invalid",
                "--ara-commit-sha", "a" * 40,
                "--workflow-run-id", "33120158075",
            ]
            code = poller.main()
        finally:
            sys.argv = original_argv
        assert_true(code == 0, "request-only-code")
        blocked = json.loads(summary_path.read_text(encoding="utf-8"))
        assert_true(blocked["fetch_request_generated"] is True, "request-only-fetch-created")
        assert_true(blocked["provider_result_consumed"] is False, "request-only-no-provider-result")
        assert_true(blocked["mailbox_mutated"] is False, "request-only-no-mutation")

    print("DEPLOYMENT_MAILBOX_POLLER_TESTS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

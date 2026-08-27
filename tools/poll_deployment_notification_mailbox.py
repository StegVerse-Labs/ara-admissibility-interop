#!/usr/bin/env python3
"""Governed ARA deployment mailbox request/result boundary.

ARA may emit bounded, non-secret TVC provider-operation requests and consume
bounded, secret-free TVC results. Credential-bearing Microsoft Graph execution
remains TV/TVC-owned. Fetch and mark-read are separate operations: ARA emits a
mark-read request only after deterministic local processing reaches
candidate_created or duplicate_noop.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SUBJECT_MARKER = "[StegVerse][DEPLOYMENT-EVIDENCE]"
REQUIRED_ATTACHMENTS = {
    "deployment-notification-email.md",
    "deployment-notification-envelope.json",
    "deployed-evidence-bundle.json",
}
TVC_PROVIDER_ROUTE_REQUIRED = "TVC_ADMITTED_PROVIDER_ROUTE_REQUIRED"
TVC_REQUEST_SCHEMA = "stegverse.tvc.ara_graph_operation_request/v1"
TVC_CALLER = "StegVerse-Labs/ara-admissibility-interop"
FETCH_OPERATION = "ARA_DEPLOYMENT_MAILBOX_FETCH"
MARK_READ_OPERATION = "ARA_DEPLOYMENT_MAILBOX_MARK_READ"
MARK_READ_ELIGIBLE = {"candidate_created", "duplicate_noop"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_sha256(value: dict[str, Any]) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _validate_source_identity(ara_commit_sha: str, workflow_run_id: str) -> None:
    if len(ara_commit_sha) not in {40, 64} or any(ch not in "0123456789abcdefABCDEF" for ch in ara_commit_sha):
        raise ValueError("invalid ARA commit SHA")
    if not workflow_run_id.isdigit():
        raise ValueError("invalid workflow run ID")


def _seal_request(payload: dict[str, Any]) -> dict[str, Any]:
    request = dict(payload)
    request["request_hash"] = canonical_sha256(request)
    return request


def build_fetch_request(
    *,
    monitor_mailbox: str,
    limit: int,
    ara_commit_sha: str,
    workflow_run_id: str,
) -> dict[str, Any]:
    mailbox = monitor_mailbox.strip()
    if not mailbox or "@" not in mailbox:
        raise ValueError("monitor mailbox binding is missing or invalid")
    if limit < 1 or limit > 25:
        raise ValueError("mailbox fetch limit out of bounds")
    _validate_source_identity(ara_commit_sha, workflow_run_id)
    return _seal_request({
        "schema": TVC_REQUEST_SCHEMA,
        "caller_repository": TVC_CALLER,
        "operation_class": FETCH_OPERATION,
        "ara_commit_sha": ara_commit_sha,
        "workflow_run_id": workflow_run_id,
        "monitor_mailbox": mailbox,
        "maximum_messages": limit,
    })


def build_mark_read_request(
    *,
    monitor_mailbox: str,
    message_id: str,
    processing_state: str,
    ara_commit_sha: str,
    workflow_run_id: str,
) -> dict[str, Any]:
    mailbox = monitor_mailbox.strip()
    if not mailbox or "@" not in mailbox:
        raise ValueError("monitor mailbox binding is missing or invalid")
    if not isinstance(message_id, str) or not message_id.strip():
        raise ValueError("message ID is missing")
    if processing_state not in MARK_READ_ELIGIBLE:
        raise ValueError("processing state is not mark-read eligible")
    _validate_source_identity(ara_commit_sha, workflow_run_id)
    return _seal_request({
        "schema": TVC_REQUEST_SCHEMA,
        "caller_repository": TVC_CALLER,
        "operation_class": MARK_READ_OPERATION,
        "ara_commit_sha": ara_commit_sha,
        "workflow_run_id": workflow_run_id,
        "monitor_mailbox": mailbox,
        "message_id": message_id,
        "processing_state": processing_state,
    })


def validate_provider_result(fetch_request: dict[str, Any], provider_result: dict[str, Any]) -> list[dict[str, Any]]:
    if provider_result.get("decision") != "ALLOW_OPERATION_RESULT":
        raise ValueError("provider result is not ALLOW_OPERATION_RESULT")
    receipt = provider_result.get("receipt")
    if not isinstance(receipt, dict):
        raise ValueError("provider result receipt is missing")
    expected = {
        "request_hash": fetch_request.get("request_hash"),
        "provider_operation_class": FETCH_OPERATION,
        "ara_commit_sha": fetch_request.get("ara_commit_sha"),
        "workflow_run_id": fetch_request.get("workflow_run_id"),
        "credential_authority": "TV/TVC",
    }
    for key, value in expected.items():
        if str(receipt.get(key)) != str(value):
            raise ValueError(f"provider receipt identity mismatch: {key}")
    if receipt.get("credential_material_exported") is not False:
        raise ValueError("provider result exported credential material")
    if receipt.get("access_token_exported") is not False:
        raise ValueError("provider result exported access-token material")
    if receipt.get("runtime_activation_claimed") is not False:
        raise ValueError("provider result improperly claims runtime activation")
    if receipt.get("ara_release_authority_effect") != "NONE":
        raise ValueError("provider result improperly claims ARA release authority")
    result = provider_result.get("result")
    if not isinstance(result, dict) or result.get("mailbox_observed") is not True:
        raise ValueError("provider mailbox observation result is invalid")
    messages = result.get("messages")
    if not isinstance(messages, list):
        raise ValueError("provider mailbox messages must be a list")
    return messages


def governed_message(message: dict[str, Any]) -> bool:
    return (
        isinstance(message.get("message_id"), str)
        and bool(message.get("message_id"))
        and isinstance(message.get("subject"), str)
        and SUBJECT_MARKER in message["subject"]
        and message.get("has_attachments") is True
    )


def attachment_map(attachments: list[dict[str, Any]]) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    for item in attachments:
        name = item.get("name")
        content = item.get("content_base64")
        if name not in REQUIRED_ATTACHMENTS or not isinstance(content, str):
            continue
        if name in result:
            raise ValueError(f"duplicate required attachment: {name}")
        try:
            result[name] = base64.b64decode(content, validate=True)
        except ValueError as exc:
            raise ValueError(f"invalid base64 attachment: {name}") from exc
    missing = sorted(REQUIRED_ATTACHMENTS - set(result))
    if missing:
        raise ValueError("missing required attachments: " + ", ".join(missing))
    return result


def safe_message_id(message_id: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in message_id)[:120]


def process_message(
    message: dict[str, Any],
    files: dict[str, bytes],
    work_root: Path,
    ledger: Path,
) -> tuple[str, Path]:
    message_id = str(message["message_id"])
    directory = work_root / safe_message_id(message_id)
    directory.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (directory / name).write_bytes(data)
    task = directory / "deployment-next-task-candidate.json"
    receipt = directory / "deployment-notification-processing.json"
    command = [
        sys.executable,
        str(ROOT / "tools" / "process_deployment_notification_once.py"),
        "--envelope", str(directory / "deployment-notification-envelope.json"),
        "--body", str(directory / "deployment-notification-email.md"),
        "--bundle", str(directory / "deployed-evidence-bundle.json"),
        "--ledger", str(ledger),
        "--task", str(task),
        "--receipt", str(receipt),
    ]
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if not receipt.is_file():
        raise RuntimeError(f"notification processor produced no receipt: {completed.stdout} {completed.stderr}")
    result = json.loads(receipt.read_text(encoding="utf-8"))
    status = result.get("processing_result")
    if completed.returncode != 0 or status not in MARK_READ_ELIGIBLE:
        raise RuntimeError(f"notification processing blocked: {status}; {completed.stdout} {completed.stderr}")
    return str(status), directory


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def blocked_summary(reason: str) -> dict[str, Any]:
    return {
        "schema_version": "1.2.0",
        "summary_type": "governed-deployment-mailbox-poll",
        "polled_at": utc_now(),
        "configuration_state": "blocked",
        "result": "blocked",
        "reason": reason,
        "credential_authority": "TV/TVC",
        "credential_material_present": False,
        "credential_material_read_by_ara": False,
        "provider_execution_performed": False,
        "mailbox_mutated": False,
        "fetch_request_generated": False,
        "provider_result_consumed": False,
        "mark_read_requests_generated": 0,
        "matched_messages": 0,
        "candidate_created": 0,
        "duplicate_noop": 0,
        "blocked": 0,
        "processed": [],
        "authority_effect": False,
        "authority_boundary": "Mailbox polling creates verification candidates, not release authority.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, default=ROOT / "status" / "deployment-notification-ledger.json")
    parser.add_argument("--work-root", type=Path, default=ROOT / "status" / "mailbox-notifications")
    parser.add_argument("--summary", type=Path, default=ROOT / "status" / "mailbox-poll-summary.json")
    parser.add_argument("--fetch-request", type=Path, default=ROOT / "status" / "deployment-mailbox-fetch-request.json")
    parser.add_argument("--provider-result", type=Path)
    parser.add_argument("--mark-read-outbox", type=Path, default=ROOT / "status" / "mailbox-mark-read-requests")
    parser.add_argument("--monitor-mailbox", default=os.getenv("STEGVERSE_MONITOR_MAILBOX", ""))
    parser.add_argument("--ara-commit-sha", default=os.getenv("GITHUB_SHA", ""))
    parser.add_argument("--workflow-run-id", default=os.getenv("GITHUB_RUN_ID", ""))
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--require-provider-route", action="store_true")
    args = parser.parse_args()

    summary = blocked_summary(TVC_PROVIDER_ROUTE_REQUIRED)
    try:
        fetch_request = build_fetch_request(
            monitor_mailbox=args.monitor_mailbox,
            limit=args.limit,
            ara_commit_sha=args.ara_commit_sha,
            workflow_run_id=args.workflow_run_id,
        )
        write_json(args.fetch_request, fetch_request)
        summary.update({
            "configuration_state": "request_ready",
            "fetch_request_generated": True,
            "fetch_request_file": args.fetch_request.name,
            "fetch_request_hash": fetch_request["request_hash"],
            "monitor_mailbox": args.monitor_mailbox,
        })
    except (OSError, ValueError) as exc:
        summary["reason"] = str(exc)
        write_json(args.summary, summary)
        print(f"DEPLOYMENT_MAILBOX_POLL=FAIL_CLOSED\nreason={exc}")
        return 1 if args.require_provider_route else 0

    if args.provider_result is None or not args.provider_result.is_file():
        write_json(args.summary, summary)
        print("DEPLOYMENT_MAILBOX_POLL=BLOCKED_TVC_PROVIDER_ROUTE_REQUIRED")
        return 1 if args.require_provider_route else 0

    try:
        provider_result = json.loads(args.provider_result.read_text(encoding="utf-8"))
        messages = validate_provider_result(fetch_request, provider_result)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        summary["reason"] = f"provider_result_invalid:{exc}"
        write_json(args.summary, summary)
        print(f"DEPLOYMENT_MAILBOX_POLL=FAIL_CLOSED\nreason={exc}")
        return 1

    summary.update({
        "configuration_state": "provider_result_validated",
        "result": "processed",
        "reason": None,
        "provider_result_consumed": True,
    })

    args.mark_read_outbox.mkdir(parents=True, exist_ok=True)
    for message in messages:
        if not isinstance(message, dict) or not governed_message(message):
            continue
        summary["matched_messages"] += 1
        message_id = str(message["message_id"])
        item = {
            "message_id": message_id,
            "subject": message.get("subject"),
            "processing_state": "blocked",
            "mark_read_request_generated": False,
        }
        try:
            files = attachment_map(message.get("attachments") or [])
            status, directory = process_message(message, files, args.work_root, args.ledger)
            if status not in MARK_READ_ELIGIBLE:
                raise RuntimeError("processing state is not mark-read eligible")
            mark_request = build_mark_read_request(
                monitor_mailbox=args.monitor_mailbox,
                message_id=message_id,
                processing_state=status,
                ara_commit_sha=args.ara_commit_sha,
                workflow_run_id=args.workflow_run_id,
            )
            mark_path = args.mark_read_outbox / f"{safe_message_id(message_id)}.json"
            write_json(mark_path, mark_request)
            summary[status] += 1
            summary["mark_read_requests_generated"] += 1
            item.update({
                "processing_state": status,
                "work_directory": str(directory),
                "mark_read_request_generated": True,
                "mark_read_request_file": mark_path.name,
                "mark_read_request_hash": mark_request["request_hash"],
            })
        except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
            summary["blocked"] += 1
            item["reason"] = str(exc)
        summary["processed"].append(item)

    write_json(args.summary, summary)
    print("DEPLOYMENT_MAILBOX_POLL=PROVIDER_RESULT_PROCESSED")
    print(f"matched_messages={summary['matched_messages']}")
    print(f"mark_read_requests_generated={summary['mark_read_requests_generated']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

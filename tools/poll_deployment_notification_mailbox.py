#!/usr/bin/env python3
"""Poll Microsoft Graph for governed deployment notifications.

The poller retrieves unread messages with the governed subject marker, requires
three canonical attachments, and processes each notification through the durable
replay ledger. A message is marked read only after processing returns either
candidate_created or duplicate_noop. Email remains a signal, not evidence or
release authority.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBJECT_MARKER = "[StegVerse][DEPLOYMENT-EVIDENCE]"
REQUIRED_ATTACHMENTS = {
    "deployment-notification-email.md",
    "deployment-notification-envelope.json",
    "deployed-evidence-bundle.json",
}
ENV_NAMES = (
    "STEGVERSE_MAIL_TENANT_ID",
    "STEGVERSE_MAIL_CLIENT_ID",
    "STEGVERSE_MAIL_CLIENT_SECRET",
    "STEGVERSE_MONITOR_MAILBOX",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def configuration() -> tuple[dict[str, str], str]:
    values = {name: os.getenv(name, "").strip() for name in ENV_NAMES}
    present = [name for name, value in values.items() if value]
    if not present:
        return values, "not_configured"
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise ValueError("partial mailbox configuration; missing: " + ", ".join(missing))
    return values, "configured"


def request_json(url: str, *, token: str, method: str = "GET", payload: dict | None = None) -> tuple[int, dict]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
            return response.status, json.loads(raw.decode("utf-8")) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Graph HTTP {exc.code}: {raw[:1000]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Graph network error: {exc.reason}") from exc


def get_access_token(config: dict[str, str]) -> str:
    tenant = urllib.parse.quote(config["STEGVERSE_MAIL_TENANT_ID"], safe="")
    url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
    form = urllib.parse.urlencode({
        "client_id": config["STEGVERSE_MAIL_CLIENT_ID"],
        "client_secret": config["STEGVERSE_MAIL_CLIENT_SECRET"],
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials",
    }).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=form,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Microsoft identity HTTP {exc.code}: {raw[:1000]}") from exc
    token = payload.get("access_token")
    if not isinstance(token, str) or not token:
        raise RuntimeError("Microsoft identity response did not contain an access token")
    return token


def message_query_url(mailbox: str, limit: int) -> str:
    encoded_mailbox = urllib.parse.quote(mailbox, safe="@._+-")
    params = urllib.parse.urlencode({
        "$filter": "isRead eq false",
        "$select": "id,subject,receivedDateTime,hasAttachments,internetMessageId",
        "$orderby": "receivedDateTime asc",
        "$top": str(limit),
    })
    return f"https://graph.microsoft.com/v1.0/users/{encoded_mailbox}/mailFolders/inbox/messages?{params}"


def governed_message(message: dict) -> bool:
    return (
        isinstance(message.get("id"), str)
        and isinstance(message.get("subject"), str)
        and SUBJECT_MARKER in message["subject"]
        and message.get("hasAttachments") is True
    )


def attachment_map(attachments: list[dict]) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    for item in attachments:
        name = item.get("name")
        content = item.get("contentBytes")
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


def process_message(message: dict, files: dict[str, bytes], work_root: Path, ledger: Path) -> tuple[str, Path]:
    message_id = message["id"]
    safe_id = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in message_id)[:120]
    directory = work_root / safe_id
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
    if completed.returncode != 0 or status not in {"candidate_created", "duplicate_noop"}:
        raise RuntimeError(f"notification processing blocked: {status}; {completed.stdout} {completed.stderr}")
    return str(status), directory


def mark_read(mailbox: str, message_id: str, token: str) -> None:
    mailbox_part = urllib.parse.quote(mailbox, safe="@._+-")
    message_part = urllib.parse.quote(message_id, safe="")
    url = f"https://graph.microsoft.com/v1.0/users/{mailbox_part}/messages/{message_part}"
    status, _ = request_json(url, token=token, method="PATCH", payload={"isRead": True})
    if status not in (200, 202):
        raise RuntimeError(f"unexpected mark-read status: {status}")


def write_summary(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, default=ROOT / "status" / "deployment-notification-ledger.json")
    parser.add_argument("--work-root", type=Path, default=ROOT / "status" / "mailbox-notifications")
    parser.add_argument("--summary", type=Path, default=ROOT / "status" / "mailbox-poll-summary.json")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--require-config", action="store_true")
    args = parser.parse_args()

    summary = {
        "schema_version": "1.0.0",
        "summary_type": "governed-deployment-mailbox-poll",
        "polled_at": utc_now(),
        "configuration_state": "failed",
        "matched_messages": 0,
        "candidate_created": 0,
        "duplicate_noop": 0,
        "blocked": 0,
        "processed": [],
        "authority_boundary": "Mailbox polling creates verification candidates, not release authority.",
    }
    try:
        config, state = configuration()
        summary["configuration_state"] = state
        if state == "not_configured":
            summary["reason"] = "Microsoft Graph mailbox settings are absent"
            write_summary(args.summary, summary)
            print("DEPLOYMENT_MAILBOX_POLL=NOT_CONFIGURED")
            return 1 if args.require_config else 0

        token = get_access_token(config)
        mailbox = config["STEGVERSE_MONITOR_MAILBOX"]
        status, payload = request_json(message_query_url(mailbox, max(1, min(args.limit, 100))), token=token)
        if status != 200:
            raise RuntimeError(f"unexpected mailbox list status: {status}")
        messages = [item for item in payload.get("value", []) if governed_message(item)]
        summary["matched_messages"] = len(messages)
        mailbox_part = urllib.parse.quote(mailbox, safe="@._+-")

        for message in messages:
            message_id = message["id"]
            message_part = urllib.parse.quote(message_id, safe="")
            attachment_url = f"https://graph.microsoft.com/v1.0/users/{mailbox_part}/messages/{message_part}/attachments"
            try:
                attachment_status, attachment_payload = request_json(attachment_url, token=token)
                if attachment_status != 200:
                    raise RuntimeError(f"unexpected attachment status: {attachment_status}")
                files = attachment_map(attachment_payload.get("value", []))
                result, directory = process_message(message, files, args.work_root, args.ledger)
                mark_read(mailbox, message_id, token)
                summary[result] += 1
                summary["processed"].append({
                    "message_id": message_id,
                    "internet_message_id": message.get("internetMessageId"),
                    "subject": message.get("subject"),
                    "received_at": message.get("receivedDateTime"),
                    "processing_result": result,
                    "message_marked_read": True,
                    "evidence_directory": directory.relative_to(ROOT).as_posix() if directory.is_relative_to(ROOT) else str(directory),
                })
            except (OSError, json.JSONDecodeError, ValueError, RuntimeError) as exc:
                summary["blocked"] += 1
                summary["processed"].append({
                    "message_id": message_id,
                    "subject": message.get("subject"),
                    "processing_result": "blocked",
                    "message_marked_read": False,
                    "reason": str(exc),
                })

        summary["result"] = "pass" if summary["blocked"] == 0 else "partial-failure"
        write_summary(args.summary, summary)
        print("DEPLOYMENT_MAILBOX_POLL=" + ("PASS" if summary["blocked"] == 0 else "PARTIAL_FAILURE"))
        return 0 if summary["blocked"] == 0 else 1
    except (OSError, json.JSONDecodeError, ValueError, RuntimeError) as exc:
        summary["reason"] = str(exc)
        summary["result"] = "fail-closed"
        write_summary(args.summary, summary)
        print(f"DEPLOYMENT_MAILBOX_POLL=FAIL-CLOSED\nreason={exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Governed deployment mailbox processing boundary.

ARA preserves deterministic notification filtering, attachment validation,
replay processing, and durable ledger semantics. Credential-bearing mailbox
access is not authorized in this consumer repository and must occur through an
admitted TV/TVC provider operation.
"""
from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBJECT_MARKER = "[StegVerse][DEPLOYMENT-EVIDENCE]"
REQUIRED_ATTACHMENTS = {
    "deployment-notification-email.md",
    "deployment-notification-envelope.json",
    "deployed-evidence-bundle.json",
}
TVC_PROVIDER_ROUTE_REQUIRED = "TVC_ADMITTED_PROVIDER_ROUTE_REQUIRED"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def write_summary(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, default=ROOT / "status" / "deployment-notification-ledger.json")
    parser.add_argument("--work-root", type=Path, default=ROOT / "status" / "mailbox-notifications")
    parser.add_argument("--summary", type=Path, default=ROOT / "status" / "mailbox-poll-summary.json")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--require-provider-route", action="store_true")
    args = parser.parse_args()

    summary = {
        "schema_version": "1.1.0",
        "summary_type": "governed-deployment-mailbox-poll",
        "polled_at": utc_now(),
        "configuration_state": "blocked",
        "result": "blocked",
        "reason": TVC_PROVIDER_ROUTE_REQUIRED,
        "credential_authority": "TV/TVC",
        "credential_material_present": False,
        "credential_material_read_by_ara": False,
        "provider_execution_performed": False,
        "mailbox_mutated": False,
        "matched_messages": 0,
        "candidate_created": 0,
        "duplicate_noop": 0,
        "blocked": 0,
        "processed": [],
        "authority_effect": False,
        "authority_boundary": "Mailbox polling creates verification candidates, not release authority.",
    }
    write_summary(args.summary, summary)
    print("DEPLOYMENT_MAILBOX_POLL=BLOCKED_TVC_PROVIDER_ROUTE_REQUIRED")
    return 1 if args.require_provider_route else 0


if __name__ == "__main__":
    raise SystemExit(main())

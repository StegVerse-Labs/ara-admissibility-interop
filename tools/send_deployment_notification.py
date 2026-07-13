#!/usr/bin/env python3
"""Send a governed deployment notification through Microsoft Graph.

The sender is dependency-free and uses Microsoft Entra application credentials.
It never accepts a mailbox password. When no mail configuration is present it
records a deterministic not-configured receipt and exits successfully. A
partial configuration fails closed.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BODY = ROOT / "status" / "deployment-notification-email.md"
DEFAULT_ENVELOPE = ROOT / "status" / "deployment-notification-envelope.json"
DEFAULT_BUNDLE = ROOT / "status" / "deployed-evidence-bundle.json"
DEFAULT_RECEIPT = ROOT / "status" / "deployment-notification-delivery.json"
ENV_NAMES = (
    "STEGVERSE_MAIL_TENANT_ID",
    "STEGVERSE_MAIL_CLIENT_ID",
    "STEGVERSE_MAIL_CLIENT_SECRET",
    "STEGVERSE_MAIL_SENDER",
    "STEGVERSE_MAIL_RECIPIENT",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def configuration() -> tuple[dict[str, str], str]:
    values = {name: os.getenv(name, "").strip() for name in ENV_NAMES}
    present = [name for name, value in values.items() if value]
    if not present:
        return values, "not_configured"
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise ValueError("partial mail configuration; missing: " + ", ".join(missing))
    return values, "configured"


def request_json(url: str, *, data: bytes, headers: dict[str, str]) -> tuple[int, dict]:
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
            payload = json.loads(raw.decode("utf-8")) if raw else {}
            return response.status, payload
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {raw[:1000]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"network error: {exc.reason}") from exc


def get_access_token(config: dict[str, str]) -> str:
    tenant = urllib.parse.quote(config["STEGVERSE_MAIL_TENANT_ID"], safe="")
    url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
    form = urllib.parse.urlencode({
        "client_id": config["STEGVERSE_MAIL_CLIENT_ID"],
        "client_secret": config["STEGVERSE_MAIL_CLIENT_SECRET"],
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials",
    }).encode("utf-8")
    status, payload = request_json(
        url,
        data=form,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = payload.get("access_token")
    if status != 200 or not isinstance(token, str) or not token:
        raise RuntimeError("Microsoft identity token response did not contain an access token")
    return token


def attachment(name: str, path: Path, content_type: str) -> dict:
    return {
        "@odata.type": "#microsoft.graph.fileAttachment",
        "name": name,
        "contentType": content_type,
        "contentBytes": base64.b64encode(path.read_bytes()).decode("ascii"),
    }


def send_mail(config: dict[str, str], token: str, subject: str, body: str,
              body_path: Path, envelope_path: Path, bundle_path: Path) -> None:
    sender = urllib.parse.quote(config["STEGVERSE_MAIL_SENDER"], safe="@._+-")
    url = f"https://graph.microsoft.com/v1.0/users/{sender}/sendMail"
    payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "Text", "content": body},
            "toRecipients": [{
                "emailAddress": {"address": config["STEGVERSE_MAIL_RECIPIENT"]}
            }],
            "attachments": [
                attachment(body_path.name, body_path, "text/markdown"),
                attachment(envelope_path.name, envelope_path, "application/json"),
                attachment(bundle_path.name, bundle_path, "application/json"),
            ],
        },
        "saveToSentItems": True,
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status not in (200, 202):
                raise RuntimeError(f"unexpected Graph sendMail status: {response.status}")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Graph sendMail HTTP {exc.code}: {raw[:1000]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Graph sendMail network error: {exc.reason}") from exc


def write_receipt(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--body", type=Path, default=DEFAULT_BODY)
    parser.add_argument("--envelope", type=Path, default=DEFAULT_ENVELOPE)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--require-delivery", action="store_true")
    args = parser.parse_args()

    receipt = {
        "schema_version": "1.1.0",
        "receipt_type": "governed-deployment-notification-delivery",
        "generated_at": utc_now(),
        "transport": "microsoft-graph-sendmail",
        "delivery_status": "failed",
        "attached_files": [args.body.name, args.envelope.name, args.bundle.name],
        "authority_boundary": "Notification delivery is not release authority.",
    }

    try:
        body = args.body.read_text(encoding="utf-8")
        envelope = load_json(args.envelope)
        bundle = load_json(args.bundle)
        if envelope.get("commit_sha") != bundle.get("commit_sha"):
            raise ValueError("notification envelope and bundle commit mismatch")
        if envelope.get("bundle_sha256") != bundle.get("bundle_sha256"):
            raise ValueError("notification envelope and bundle SHA-256 mismatch")
        subject = envelope.get("subject")
        if not isinstance(subject, str) or not subject:
            raise ValueError("notification envelope has no subject")
        config, state = configuration()
        receipt.update({
            "repository": envelope.get("repository"),
            "commit_sha": envelope.get("commit_sha"),
            "workflow_run_id": envelope.get("workflow_run_id"),
            "bundle_sha256": envelope.get("bundle_sha256"),
            "body_sha256": envelope.get("body_sha256"),
            "subject": subject,
            "configuration_state": state,
        })
        if state == "not_configured":
            receipt["delivery_status"] = "not_configured"
            receipt["reason"] = "Microsoft Graph application mail settings are absent"
            write_receipt(args.receipt, receipt)
            print("DEPLOYMENT_NOTIFICATION_DELIVERY=NOT_CONFIGURED")
            return 1 if args.require_delivery else 0

        token = get_access_token(config)
        send_mail(config, token, subject, body, args.body, args.envelope, args.bundle)
        receipt.update({
            "delivery_status": "sent",
            "sent_at": utc_now(),
            "sender": config["STEGVERSE_MAIL_SENDER"],
            "recipient": config["STEGVERSE_MAIL_RECIPIENT"],
        })
        write_receipt(args.receipt, receipt)
        print("DEPLOYMENT_NOTIFICATION_DELIVERY=SENT")
        return 0
    except (OSError, json.JSONDecodeError, ValueError, RuntimeError) as exc:
        receipt["reason"] = str(exc)
        write_receipt(args.receipt, receipt)
        print(f"DEPLOYMENT_NOTIFICATION_DELIVERY=FAIL-CLOSED\nreason={exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

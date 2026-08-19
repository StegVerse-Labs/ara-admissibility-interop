#!/usr/bin/env python3
"""TVC-owned Microsoft Graph GitHub-failure observation processor.

Protected Microsoft Graph configuration may be physically injected by the execution
carrier, but all credential processing occurs in this TVC-owned source. Only a
sanitized JSONL batch and non-secret manifest leave this boundary.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

REQUIRED_ENV = (
    "STEGVERSE_MAIL_TENANT_ID",
    "STEGVERSE_MAIL_CLIENT_ID",
    "STEGVERSE_MAIL_CLIENT_SECRET",
    "STEGVERSE_MONITOR_MAILBOX",
)
SENDER = "notifications@github.com"


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _request_json(url: str, *, token: str = "", data: bytes | None = None, headers: dict[str, str] | None = None) -> dict:
    merged = {"Accept": "application/json"}
    if token:
        merged["Authorization"] = f"Bearer {token}"
    if headers:
        merged.update(headers)
    request = urllib.request.Request(url, data=data, headers=merged)
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
        return json.loads(raw.decode("utf-8")) if raw else {}


def _credential_configuration() -> dict[str, str]:
    values = {name: os.environ.get(name, "").strip() for name in REQUIRED_ENV}
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise RuntimeError("TVC mailbox credential binding incomplete: " + ", ".join(missing))
    return values


def _access_token(config: dict[str, str]) -> str:
    tenant = urllib.parse.quote(config["STEGVERSE_MAIL_TENANT_ID"], safe="")
    token_url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
    form = urllib.parse.urlencode({
        "client_id": config["STEGVERSE_MAIL_CLIENT_ID"],
        "client_secret": config["STEGVERSE_MAIL_CLIENT_SECRET"],
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials",
    }).encode("utf-8")
    payload = _request_json(token_url, data=form, headers={"Content-Type": "application/x-www-form-urlencoded"})
    token = payload.get("access_token")
    if not isinstance(token, str) or not token:
        raise RuntimeError("TVC Microsoft identity response contained no access token")
    return token


def _stable_hash(value: object) -> str:
    return "sha256:" + hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()


def run(*, output_dir: Path, window_minutes: int, lag_minutes: int, maximum_messages: int, carrier: str) -> dict:
    if window_minutes < 1 or window_minutes > 1440:
        raise ValueError("window_minutes outside TVC bounded policy")
    if lag_minutes < 0 or lag_minutes > 60:
        raise ValueError("lag_minutes outside TVC bounded policy")
    if maximum_messages < 1 or maximum_messages > 1000:
        raise ValueError("maximum_messages outside TVC bounded policy")

    config = _credential_configuration()
    token = _access_token(config)
    end = datetime.now(timezone.utc) - timedelta(minutes=lag_minutes)
    start = end - timedelta(minutes=window_minutes)
    params = urllib.parse.urlencode({
        "$filter": f"receivedDateTime ge {_iso(start)} and receivedDateTime le {_iso(end)}",
        "$select": "id,conversationId,internetMessageId,subject,receivedDateTime,bodyPreview,from",
        "$orderby": "receivedDateTime asc",
        "$top": "100",
    })
    mailbox_part = urllib.parse.quote(config["STEGVERSE_MONITOR_MAILBOX"], safe="@._+-")
    url = f"https://graph.microsoft.com/v1.0/users/{mailbox_part}/mailFolders/inbox/messages?{params}"

    rows: list[dict] = []
    source_count = 0
    partial = False
    while url:
        payload = _request_json(url, token=token)
        values = payload.get("value", [])
        if not isinstance(values, list):
            raise RuntimeError("TVC Graph response value is not a list")
        for item in values:
            if not isinstance(item, dict):
                continue
            sender = (((item.get("from") or {}).get("emailAddress") or {}).get("address") or "").lower()
            subject = str(item.get("subject") or "")
            if sender != SENDER or ("Run failed:" not in subject and "PR run failed:" not in subject):
                continue
            source_count += 1
            if len(rows) >= maximum_messages:
                partial = True
                continue
            rows.append({
                "id": _stable_hash(item.get("id")),
                "thread_id": _stable_hash(item.get("conversationId")),
                "internet_message_id": _stable_hash(item.get("internetMessageId")),
                "email_ts": str(item.get("receivedDateTime") or ""),
                "subject": subject,
                "snippet": str(item.get("bodyPreview") or "")[:1000],
            })
        next_link = payload.get("@odata.nextLink")
        url = next_link if isinstance(next_link, str) else ""

    output_dir.mkdir(parents=True, exist_ok=True)
    batch_path = output_dir / "batch.jsonl"
    batch_bytes = b"".join(
        (json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        for row in rows
    )
    batch_path.write_bytes(batch_bytes)
    batch_sha = hashlib.sha256(batch_bytes).hexdigest()
    batch_id = "tvc-graph-failure-" + hashlib.sha256(
        (_iso(start) + "|" + _iso(end) + "|" + batch_sha).encode("utf-8")
    ).hexdigest()[:24]
    manifest = {
        "schema": "stegverse.tvc-mailbox-failure-observation-manifest/v1",
        "batch_id": batch_id,
        "source_count": source_count,
        "materialized_count": len(rows),
        "window_start": _iso(start),
        "window_end": _iso(end),
        "source_ref": "microsoft-graph://notifications@github.com/run-failed",
        "mailbox_mutated": False,
        "credential_authority": "TV/TVC",
        "credential_storage_provider": "GitHub Actions secrets",
        "credential_processed_by": "StegVerse-Labs/TVC",
        "credential_processing_source": "scripts/microsoft_graph_failure_observation.py",
        "execution_carrier": carrier,
        "credential_value_exposed": False,
        "credential_value_persisted": False,
        "consumer_credential_exported": False,
        "provider_message_ids_exported": False,
        "partial_materialization": partial,
        "batch_sha256": batch_sha,
        "authority_effect": False,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if partial:
        raise RuntimeError("TVC mailbox observation exceeded materialization ceiling")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--window-minutes", type=int, default=20)
    parser.add_argument("--lag-minutes", type=int, default=2)
    parser.add_argument("--maximum-messages", type=int, default=1000)
    parser.add_argument("--carrier", default="unspecified")
    args = parser.parse_args()
    manifest = run(
        output_dir=args.output_dir,
        window_minutes=args.window_minutes,
        lag_minutes=args.lag_minutes,
        maximum_messages=args.maximum_messages,
        carrier=args.carrier,
    )
    print(json.dumps({
        "result": "PASS",
        "batch_id": manifest["batch_id"],
        "source_count": manifest["source_count"],
        "materialized_count": manifest["materialized_count"],
        "credential_authority": manifest["credential_authority"],
        "credential_processed_by": manifest["credential_processed_by"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

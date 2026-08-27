#!/usr/bin/env python3
"""Governed deployment-notification delivery boundary.

ARA owns notification generation and evidence binding, but not provider
credentials. Credential-bearing Microsoft Graph execution must occur through an
admitted TV/TVC provider operation. This consumer therefore fails closed
without reading provider secrets or performing network execution.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from build_tvc_notification_request import build_request

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BODY = ROOT / "status" / "deployment-notification-email.md"
DEFAULT_ENVELOPE = ROOT / "status" / "deployment-notification-envelope.json"
DEFAULT_BUNDLE = ROOT / "status" / "deployed-evidence-bundle.json"
DEFAULT_RECEIPT = ROOT / "status" / "deployment-notification-delivery.json"
DEFAULT_PROVIDER_REQUEST = ROOT / "status" / "deployment-notification-provider-request.json"

TVC_PROVIDER_ROUTE_REQUIRED = "TVC_ADMITTED_PROVIDER_ROUTE_REQUIRED"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_receipt(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--body", type=Path, default=DEFAULT_BODY)
    parser.add_argument("--envelope", type=Path, default=DEFAULT_ENVELOPE)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--provider-request", type=Path, default=DEFAULT_PROVIDER_REQUEST)
    parser.add_argument("--require-delivery", action="store_true")
    args = parser.parse_args()

    receipt = {
        "schema_version": "1.2.0",
        "receipt_type": "governed-deployment-notification-delivery",
        "generated_at": utc_now(),
        "transport": "tvc-admitted-provider-operation-required",
        "delivery_status": "blocked",
        "provider": "microsoft-graph",
        "reason": TVC_PROVIDER_ROUTE_REQUIRED,
        "credential_authority": "TV/TVC",
        "credential_material_present": False,
        "credential_material_read_by_ara": False,
        "provider_execution_performed": False,
        "authority_effect": False,
        "authority_boundary": "Notification delivery is not release authority.",
        "attached_files": [args.body.name, args.envelope.name, args.bundle.name],
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
        provider_request = build_request(
            body_path=args.body,
            envelope_path=args.envelope,
            bundle_path=args.bundle,
        )
        args.provider_request.parent.mkdir(parents=True, exist_ok=True)
        args.provider_request.write_text(
            json.dumps(provider_request, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        receipt.update({
            "repository": envelope.get("repository"),
            "commit_sha": envelope.get("commit_sha"),
            "workflow_run_id": envelope.get("workflow_run_id"),
            "bundle_sha256": envelope.get("bundle_sha256"),
            "body_sha256": envelope.get("body_sha256"),
            "subject": subject,
            "body_present": bool(body),
            "provider_request_generated": True,
            "provider_request_file": args.provider_request.name,
            "provider_request_hash": provider_request["request_hash"],
            "provider_request_operation_class": provider_request["operation_class"],
            "provider_request_contains_protected_material": False,
        })
        write_receipt(args.receipt, receipt)
        print("DEPLOYMENT_NOTIFICATION_DELIVERY=BLOCKED_TVC_PROVIDER_ROUTE_REQUIRED")
        return 1 if args.require_delivery else 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        receipt["reason"] = str(exc)
        write_receipt(args.receipt, receipt)
        print(f"DEPLOYMENT_NOTIFICATION_DELIVERY=FAIL_CLOSED\nreason={exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

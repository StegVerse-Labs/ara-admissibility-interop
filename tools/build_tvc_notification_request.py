#!/usr/bin/env python3
"""Build the bounded, non-secret TVC request for one ARA deployment notification."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "stegverse.tvc.ara_graph_operation_request/v1"
CALLER = "StegVerse-Labs/ara-admissibility-interop"
OPERATION = "ARA_DEPLOYMENT_NOTIFICATION_SEND"


def canonical_sha256(value: dict[str, Any]) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def build_request(*, body_path: Path, envelope_path: Path, bundle_path: Path) -> dict[str, Any]:
    body = body_path.read_text(encoding="utf-8")
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    if envelope.get("commit_sha") != bundle.get("commit_sha"):
        raise ValueError("notification envelope and bundle commit mismatch")
    if envelope.get("bundle_sha256") != bundle.get("bundle_sha256"):
        raise ValueError("notification envelope and bundle SHA-256 mismatch")
    commit_sha = str(envelope.get("commit_sha") or "")
    workflow_run_id = str(envelope.get("workflow_run_id") or "")
    subject = str(envelope.get("subject") or "")
    if len(commit_sha) not in {40, 64} or any(ch not in "0123456789abcdefABCDEF" for ch in commit_sha):
        raise ValueError("invalid commit SHA")
    if not workflow_run_id.isdigit():
        raise ValueError("invalid workflow run ID")
    if not subject:
        raise ValueError("missing subject")
    attachments = []
    for path in (body_path, envelope_path, bundle_path):
        attachments.append({
            "name": path.name,
            "content_base64": base64.b64encode(path.read_bytes()).decode("ascii"),
        })
    request = {
        "schema": SCHEMA,
        "caller_repository": CALLER,
        "operation_class": OPERATION,
        "ara_commit_sha": commit_sha,
        "workflow_run_id": workflow_run_id,
        "subject": subject,
        "body": body,
        "attachments": attachments,
    }
    request["request_hash"] = canonical_sha256(request)
    return request


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--body", type=Path, required=True)
    parser.add_argument("--envelope", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        request = build_request(body_path=args.body, envelope_path=args.envelope, bundle_path=args.bundle)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"TVC_NOTIFICATION_REQUEST=FAIL_CLOSED\nreason={exc}")
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(request, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("TVC_NOTIFICATION_REQUEST=CREATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

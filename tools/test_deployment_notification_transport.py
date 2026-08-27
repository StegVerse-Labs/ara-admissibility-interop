#!/usr/bin/env python3
"""Regression tests for governed deployment notification transport and ingestion."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from ingest_deployment_notification import REQUIRED_SECTIONS, sha256_bytes, validate
from build_tvc_notification_request import build_request, canonical_sha256
from send_deployment_notification import TVC_PROVIDER_ROUTE_REQUIRED


def sample() -> tuple[dict, bytes, dict]:
    body = b"Subject: [StegVerse][DEPLOYMENT-EVIDENCE][ARA][ALLOW] abcdef\n\nbody\n"
    bundle = {"commit_sha": "a" * 40, "bundle_sha256": "b" * 64}
    envelope = {
        "notification_type": "governed-deployment-evidence-available",
        "authority_boundary": "Email notification is a signal, not release authority.",
        "body_sha256": sha256_bytes(body),
        "commit_sha": bundle["commit_sha"],
        "bundle_sha256": bundle["bundle_sha256"],
        "artifact_name": "deployed-publication-evidence",
        "next_action": "retrieve-and-independently-verify",
        "included_handoff_sections": sorted(REQUIRED_SECTIONS),
        "subject": "[StegVerse][DEPLOYMENT-EVIDENCE][ARA][ALLOW] aaaaaaaaaaaa",
        "public_review_decision": "ALLOW",
        "workflow_run_id": 33119847552,
    }
    return envelope, body, bundle


def expect(problem: str, envelope: dict, body: bytes, bundle: dict) -> None:
    problems = validate(envelope, body, bundle)
    assert problem in problems, (problem, problems)


def main() -> int:
    envelope, body, bundle = sample()
    assert validate(envelope, body, bundle) == []

    changed = dict(envelope)
    expect("body-sha256", changed, body + b"tampered", bundle)

    changed = dict(envelope)
    changed["commit_sha"] = "c" * 40
    expect("commit-mismatch", changed, body, bundle)

    changed = dict(envelope)
    changed["bundle_sha256"] = "d" * 64
    expect("bundle-sha256-mismatch", changed, body, bundle)

    changed = dict(envelope)
    changed["included_handoff_sections"] = ["Current goal"]
    expect("handoff-sections", changed, body, bundle)

    changed = dict(envelope)
    changed["public_review_decision"] = "BLOCK"
    expect("public-review-not-allow", changed, body, bundle)

    assert TVC_PROVIDER_ROUTE_REQUIRED == "TVC_ADMITTED_PROVIDER_ROUTE_REQUIRED"

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        envelope_path = root / "envelope.json"
        body_path = root / "body.md"
        bundle_path = root / "bundle.json"
        envelope_path.write_text(json.dumps(envelope), encoding="utf-8")
        body_path.write_bytes(body)
        bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
        provider_request = build_request(
            body_path=body_path,
            envelope_path=envelope_path,
            bundle_path=bundle_path,
        )
        declared_hash = provider_request["request_hash"]
        unhashed = dict(provider_request)
        del unhashed["request_hash"]
        assert declared_hash == canonical_sha256(unhashed)
        assert provider_request["schema"] == "stegverse.tvc.ara_graph_operation_request/v1"
        assert provider_request["operation_class"] == "ARA_DEPLOYMENT_NOTIFICATION_SEND"
        assert provider_request["ara_commit_sha"] == bundle["commit_sha"]
        assert provider_request["workflow_run_id"] == "33119847552"
        assert {item["name"] for item in provider_request["attachments"]} == {
            "body.md", "envelope.json", "bundle.json"
        }
        encoded = json.dumps(provider_request)
        for forbidden in ("client_secret", "access_token", "refresh_token", "bearer_token"):
            assert forbidden not in encoded.lower()

    print("DEPLOYMENT_NOTIFICATION_TRANSPORT_TESTS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

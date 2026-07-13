#!/usr/bin/env python3
"""Regression tests for governed deployment notification transport and ingestion."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from ingest_deployment_notification import REQUIRED_SECTIONS, sha256_bytes, validate
from send_deployment_notification import ENV_NAMES, configuration


def sample() -> tuple[dict, bytes, dict]:
    body = b"Subject: [StegVerse][DEPLOYMENT-EVIDENCE][ARA][ALLOW] abcdef\n\nbody\n"
    bundle = {
        "commit_sha": "a" * 40,
        "bundle_sha256": "b" * 64,
    }
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

    empty = {name: "" for name in ENV_NAMES}
    with patch.dict(os.environ, empty, clear=False):
        values, state = configuration()
        assert state == "not_configured"
        assert not any(values.values())

    complete = {
        "STEGVERSE_MAIL_TENANT_ID": "tenant",
        "STEGVERSE_MAIL_CLIENT_ID": "client",
        "STEGVERSE_MAIL_CLIENT_SECRET": "secret",
        "STEGVERSE_MAIL_SENDER": "sender@example.org",
        "STEGVERSE_MAIL_RECIPIENT": "recipient@example.org",
    }
    with patch.dict(os.environ, complete, clear=False):
        values, state = configuration()
        assert state == "configured"
        assert values["STEGVERSE_MAIL_SENDER"] == "sender@example.org"

    partial = dict(empty)
    partial["STEGVERSE_MAIL_TENANT_ID"] = "tenant"
    with patch.dict(os.environ, partial, clear=False):
        try:
            configuration()
        except ValueError as exc:
            assert "partial mail configuration" in str(exc)
        else:
            raise AssertionError("partial mail configuration was accepted")

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "envelope.json").write_text(json.dumps(envelope), encoding="utf-8")
        (root / "body.md").write_bytes(body)
        (root / "bundle.json").write_text(json.dumps(bundle), encoding="utf-8")
        assert (root / "envelope.json").is_file()

    print("DEPLOYMENT_NOTIFICATION_TRANSPORT_TESTS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Regression tests for governed deployment mailbox processing helpers."""
from __future__ import annotations

import base64
import importlib.util
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


def main() -> int:
    assert_true(
        poller.TVC_PROVIDER_ROUTE_REQUIRED == "TVC_ADMITTED_PROVIDER_ROUTE_REQUIRED",
        "tvc-route-required",
    )

    governed = {
        "id": "message-1",
        "subject": "[StegVerse][DEPLOYMENT-EVIDENCE][ARA][ALLOW] abc123",
        "hasAttachments": True,
    }
    assert_true(poller.governed_message(governed), "governed-message")
    assert_true(not poller.governed_message({**governed, "subject": "ordinary"}), "subject-filter")
    assert_true(not poller.governed_message({**governed, "hasAttachments": False}), "attachment-filter")

    attachments = []
    for name in sorted(poller.REQUIRED_ATTACHMENTS):
        attachments.append({"name": name, "contentBytes": base64.b64encode(name.encode()).decode()})
    mapped = poller.attachment_map(attachments)
    assert_true(set(mapped) == poller.REQUIRED_ATTACHMENTS, "attachment-map")

    try:
        poller.attachment_map(attachments[:-1])
    except ValueError as exc:
        assert_true("missing required attachments" in str(exc), "missing-attachment-message")
    else:
        raise AssertionError("missing-attachment")

    duplicate = attachments + [attachments[0]]
    try:
        poller.attachment_map(duplicate)
    except ValueError as exc:
        assert_true("duplicate required attachment" in str(exc), "duplicate-attachment-message")
    else:
        raise AssertionError("duplicate-attachment")

    bad = list(attachments)
    bad[0] = {"name": bad[0]["name"], "contentBytes": "%%%"}
    try:
        poller.attachment_map(bad)
    except ValueError as exc:
        assert_true("invalid base64 attachment" in str(exc), "invalid-base64-message")
    else:
        raise AssertionError("invalid-base64")

    print("DEPLOYMENT_MAILBOX_POLLER_TESTS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

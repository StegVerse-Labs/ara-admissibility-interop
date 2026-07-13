#!/usr/bin/env python3
"""Regression tests for handoff-backed deployment notification generation."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from generate_deployment_notification import REQUIRED_SECTIONS, extract_sections, render, sha256_text


def main() -> int:
    failures: list[str] = []
    handoff = "\n".join(
        ["# Handoff", ""]
        + sum(([f"## {name}", "", f"content for {name}", ""] for name in REQUIRED_SECTIONS), [])
    )
    sections = extract_sections(handoff)
    if set(sections) != set(REQUIRED_SECTIONS):
        failures.append("required-sections")

    try:
        extract_sections("## Current goal\nOnly one section")
    except ValueError:
        pass
    else:
        failures.append("missing-sections-not-rejected")

    envelope = {
        "repository": "StegVerse-Labs/ara-admissibility-interop",
        "commit_sha": "a" * 40,
        "workflow_run_id": "123",
        "bundle_sha256": "b" * 64,
        "public_review_decision": "ALLOW",
        "stable_release_decision": "BLOCK",
    }
    subject = "[StegVerse][DEPLOYMENT-EVIDENCE][ARA][ALLOW] aaaaaaaaaaaa"
    body = render(subject, envelope, sections)
    for name in REQUIRED_SECTIONS:
        if f"## Handoff — {name}" not in body:
            failures.append(f"section-not-rendered:{name}")
    if "signal, not release authority" not in body:
        failures.append("authority-boundary")
    if len(sha256_text(body)) != 64:
        failures.append("body-hash")

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        body_file = root / "notification.md"
        envelope_file = root / "notification.json"
        body_file.write_text(body, encoding="utf-8")
        envelope_payload = dict(envelope, body_sha256=sha256_text(body))
        envelope_file.write_text(json.dumps(envelope_payload), encoding="utf-8")
        loaded = json.loads(envelope_file.read_text(encoding="utf-8"))
        if loaded["body_sha256"] != sha256_text(body_file.read_text(encoding="utf-8")):
            failures.append("body-envelope-mismatch")

    result = {
        "result": "pass" if not failures else "fail",
        "problem_count": len(failures),
        "problems": failures,
        "required_sections": list(REQUIRED_SECTIONS),
    }
    print(json.dumps(result, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

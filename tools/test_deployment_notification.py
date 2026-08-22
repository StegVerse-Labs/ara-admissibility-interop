#!/usr/bin/env python3
"""Regression tests for handoff-backed deployment notification generation."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from generate_deployment_notification import (
    REQUIRED_SECTIONS,
    extract_sections,
    render,
    resolve_handoff_path,
    sha256_text,
)

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_HANDOFF = ROOT / "docs" / "ARA_ADMISSIBILITY_INTEROP_MIRROR_HANDOFF.md"


def main() -> int:
    failures: list[str] = []
    handoff = "\n".join(
        ["# Handoff", ""]
        + sum(([f"## {name}", "", f"content for {name}", ""] for name in REQUIRED_SECTIONS), [])
    )
    sections = extract_sections(handoff)
    if set(sections) != set(REQUIRED_SECTIONS):
        failures.append("required-sections")

    # The publication gate must validate the real canonical handoff, not only a
    # synthetic fixture. This prevents a handoff-heading reconciliation from
    # passing CI while the deployed notification generator fails later.
    try:
        canonical_text = CANONICAL_HANDOFF.read_text(encoding="utf-8")
        canonical_sections = extract_sections(canonical_text)
    except (OSError, ValueError) as exc:
        failures.append(f"canonical-handoff-contract:{exc}")
    else:
        if set(canonical_sections) != set(REQUIRED_SECTIONS):
            failures.append("canonical-handoff-required-sections")
        for name in REQUIRED_SECTIONS:
            if not canonical_sections.get(name, "").strip():
                failures.append(f"canonical-handoff-empty-section:{name}")

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
        docs = root / "docs"
        docs.mkdir()
        canonical = docs / "ARA_ADMISSIBILITY_INTEROP_MIRROR_HANDOFF.md"
        redirect = root / "ARA_ADMISSIBILITY_INTEROP_MIRROR_HANDOFF.md"
        competing = docs / "COMPETING_MIRROR_HANDOFF.md"
        canonical.write_text(handoff, encoding="utf-8")
        redirect.write_text(
            "# Redirect\n\nStatus: superseded redirect\n\n"
            "`docs/ARA_ADMISSIBILITY_INTEROP_MIRROR_HANDOFF.md`\n",
            encoding="utf-8",
        )
        competing.write_text(handoff, encoding="utf-8")

        if resolve_handoff_path(canonical, root=root, canonical=canonical, redirect=redirect) != canonical.resolve():
            failures.append("canonical-not-selected")
        if resolve_handoff_path(redirect, root=root, canonical=canonical, redirect=redirect) != canonical.resolve():
            failures.append("redirect-not-resolved-to-canonical")
        try:
            resolve_handoff_path(competing, root=root, canonical=canonical, redirect=redirect)
        except ValueError as exc:
            if "competing mirror handoff rejected" not in str(exc):
                failures.append("competing-handoff-wrong-error")
        else:
            failures.append("competing-handoff-not-rejected")

        redirect.write_text("# stale alternate handoff\n", encoding="utf-8")
        try:
            resolve_handoff_path(redirect, root=root, canonical=canonical, redirect=redirect)
        except ValueError:
            pass
        else:
            failures.append("invalid-redirect-not-rejected")

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
        "canonical_handoff_checked": str(CANONICAL_HANDOFF.relative_to(ROOT)),
    }
    print(json.dumps(result, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Apply explicit stable-release authorization without promoting evidence gates.

This tool is deliberately separate from ``promote_release_gates.py``. It may set
only ``release_gate.stable_release_authorized`` after validating a machine-readable
maintainer authorization receipt for the same repository and candidate. It never
creates a tag or release and never changes technical-evidence gates.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "release-manifest.json"
DEFAULT_AUTHORIZATION = ROOT / "management" / "stable-release-authorization.json"
DEFAULT_PROPOSED = ROOT / "status" / "release-manifest.authorized.json"
DEFAULT_RECEIPT = ROOT / "status" / "stable-release-authorization-application.json"

EXPECTED_SCHEMA = "stegverse.stable-release-authorization/v1"
EXPECTED_SCOPE = "stable-tag-and-formal-release-after-evidence-gates"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(manifest: dict, authorization: dict) -> list[str]:
    problems: list[str] = []
    if authorization.get("schema") != EXPECTED_SCHEMA:
        problems.append("authorization-schema-mismatch")
    if authorization.get("repository") != manifest.get("repository"):
        problems.append("repository-mismatch")
    if authorization.get("candidate") != manifest.get("candidate"):
        problems.append("candidate-mismatch")
    if authorization.get("authorized") is not True:
        problems.append("authorization-not-true")
    if authorization.get("authorization_scope") != EXPECTED_SCOPE:
        problems.append("authorization-scope-mismatch")
    record = authorization.get("authorization_record")
    if not isinstance(record, dict):
        problems.append("authorization-record-missing")
    else:
        if record.get("type") != "explicit-maintainer-instruction":
            problems.append("authorization-record-type-invalid")
        if not isinstance(record.get("issue"), int):
            problems.append("authorization-issue-missing")
        if not isinstance(record.get("issue_comment_id"), int):
            problems.append("authorization-comment-id-missing")
    effective_when = authorization.get("effective_when")
    if not isinstance(effective_when, list) or not effective_when:
        problems.append("effective-when-missing")
    return problems


def apply(manifest: dict) -> dict:
    proposed = copy.deepcopy(manifest)
    gate = proposed.setdefault("release_gate", {})
    before = copy.deepcopy(gate)
    gate["stable_release_authorized"] = True
    for key, value in before.items():
        if key == "stable_release_authorized":
            continue
        if gate.get(key) != value:
            raise RuntimeError(f"non-authorization gate changed: {key}")
    return proposed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--authorization", type=Path, default=DEFAULT_AUTHORIZATION)
    parser.add_argument("--proposed-output", type=Path, default=DEFAULT_PROPOSED)
    parser.add_argument("--application-receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--write-manifest", action="store_true")
    args = parser.parse_args()

    try:
        manifest = load_json(args.manifest)
        authorization = load_json(args.authorization)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"STABLE_RELEASE_AUTHORIZATION=FAIL-CLOSED\nreason={exc}")
        return 1

    problems = validate(manifest, authorization)
    proposed = copy.deepcopy(manifest) if problems else apply(manifest)
    result = "ALLOW" if not problems else "BLOCK"

    args.proposed_output.parent.mkdir(parents=True, exist_ok=True)
    args.proposed_output.write_text(json.dumps(proposed, indent=2) + "\n", encoding="utf-8")

    receipt = {
        "schema_version": "1.0.0",
        "application_type": "explicit-stable-release-authorization",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "result": result,
        "repository": manifest.get("repository"),
        "candidate": manifest.get("candidate"),
        "authorization_sha256": sha256_file(args.authorization) if args.authorization.exists() else None,
        "manifest_before_sha256": sha256_file(args.manifest) if args.manifest.exists() else None,
        "changed_field": "stable_release_authorized" if not problems else None,
        "manifest_written": bool(args.write_manifest and not problems),
        "problems": problems,
        "boundary": (
            "Authorization application does not prove technical release gates, create a tag, "
            "create a release, or grant any non-release authority."
        ),
    }
    args.application_receipt.parent.mkdir(parents=True, exist_ok=True)
    args.application_receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    if args.write_manifest and not problems:
        args.manifest.write_text(json.dumps(proposed, indent=2) + "\n", encoding="utf-8")

    print(f"STABLE_RELEASE_AUTHORIZATION={result}")
    print(f"manifest_written={receipt['manifest_written']}")
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())

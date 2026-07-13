#!/usr/bin/env python3
"""Promote only evidence-backed release gates from a verified deployment bundle.

This tool never sets ``stable_release_authorized`` and never creates a tag. By
default it writes a proposed manifest and a promotion receipt. Replacing the
input manifest requires the explicit ``--write-manifest`` flag.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from verify_evidence_bundle_manifest import verify as verify_bundle

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "release-manifest.json"
DEFAULT_RECEIPT = ROOT / "status" / "publication-receipt.json"
DEFAULT_DECISION = ROOT / "status" / "release-evidence-decision.json"
DEFAULT_BUNDLE = ROOT / "status" / "deployed-evidence-bundle.json"
DEFAULT_PROPOSED = ROOT / "status" / "release-manifest.promoted.json"
DEFAULT_PROMOTION_RECEIPT = ROOT / "status" / "release-gate-promotion.json"

PROMOTABLE_FIELDS = (
    "pages_workflow_verified",
    "https_deployment_url_verified",
    "built_entrypoint_verified",
    "live_root_page_verified",
    "deployed_publication_receipt_verified",
    "deployed_evidence_bundle_verified",
)
PROTECTED_FIELDS = ("repo_check_workflow_verified", "stable_release_authorized")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def assess(manifest: dict, receipt: dict, decision: dict, bundle: dict,
           bundle_problems: list[str]) -> tuple[dict, list[str], list[str]]:
    blockers: list[str] = []
    commit = receipt.get("commit_sha")
    live = receipt.get("live_root_verification", {})

    if bundle_problems:
        blockers.extend(f"bundle:{item}" for item in bundle_problems)
    if decision.get("public_review_decision") != "ALLOW":
        blockers.append("public-review-decision-not-allow")
    if decision.get("evidence_verification") != "pass":
        blockers.append("evidence-verification-not-pass")
    if live.get("result") != "passed":
        blockers.append("live-root-not-passed")
    if live.get("http_status") != 200:
        blockers.append("live-root-http-not-200")
    if live.get("identity_http_status") != 200:
        blockers.append("identity-http-not-200")
    if live.get("deployed_commit_sha") != commit:
        blockers.append("receipt-deployed-commit-mismatch")
    for label, value in (
        ("decision", decision.get("commit_sha")),
        ("bundle", bundle.get("commit_sha")),
    ):
        if value != commit:
            blockers.append(f"{label}-commit-mismatch")
    if bundle.get("public_review_decision") != "ALLOW":
        blockers.append("bundle-public-review-not-allow")
    if receipt.get("publication_status") != "public_review":
        blockers.append("publication-status-not-public-review")
    if receipt.get("canonical_status") != "not_authorized":
        blockers.append("canonical-status-unexpected")
    if receipt.get("reliance_posture") != "research_and_review_only":
        blockers.append("reliance-posture-unexpected")

    proposed = copy.deepcopy(manifest)
    gate = proposed.setdefault("release_gate", {})
    changed: list[str] = []
    if not blockers:
        for field in PROMOTABLE_FIELDS:
            if gate.get(field) is not True:
                gate[field] = True
                changed.append(field)

    # Explicitly preserve authority-bearing and independently sourced gates.
    original_gate = manifest.get("release_gate", {})
    for field in PROTECTED_FIELDS:
        if field in original_gate:
            gate[field] = original_gate[field]
        else:
            gate[field] = False
    return proposed, changed, blockers


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--decision", type=Path, default=DEFAULT_DECISION)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--bundle-root", type=Path, default=ROOT)
    parser.add_argument("--proposed-output", type=Path, default=DEFAULT_PROPOSED)
    parser.add_argument("--promotion-receipt", type=Path, default=DEFAULT_PROMOTION_RECEIPT)
    parser.add_argument("--write-manifest", action="store_true")
    args = parser.parse_args()

    try:
        manifest = load_json(args.manifest)
        receipt = load_json(args.receipt)
        decision = load_json(args.decision)
        bundle = load_json(args.bundle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"RELEASE_GATE_PROMOTION=FAIL-CLOSED\nreason={exc}")
        return 1

    bundle_problems = verify_bundle(bundle, args.bundle_root)
    proposed, changed, blockers = assess(
        manifest, receipt, decision, bundle, bundle_problems
    )
    result = "ALLOW" if not blockers else "BLOCK"

    args.proposed_output.parent.mkdir(parents=True, exist_ok=True)
    args.proposed_output.write_text(json.dumps(proposed, indent=2) + "\n", encoding="utf-8")

    promotion = {
        "schema_version": "1.0.0",
        "promotion_type": "evidence-bounded-release-gate-promotion",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "result": result,
        "commit_sha": receipt.get("commit_sha"),
        "bundle_sha256": bundle.get("bundle_sha256"),
        "changed_fields": changed,
        "protected_fields": list(PROTECTED_FIELDS),
        "blockers": blockers,
        "manifest_before_sha256": sha256_file(args.manifest),
        "manifest_written": bool(args.write_manifest and not blockers),
        "boundary": (
            "Evidence-backed promotion cannot set stable_release_authorized, "
            "prove Repo Check completion, or create a release tag."
        ),
    }
    args.promotion_receipt.parent.mkdir(parents=True, exist_ok=True)
    args.promotion_receipt.write_text(json.dumps(promotion, indent=2) + "\n", encoding="utf-8")

    if args.write_manifest and not blockers:
        args.manifest.write_text(json.dumps(proposed, indent=2) + "\n", encoding="utf-8")

    print(f"RELEASE_GATE_PROMOTION={result}")
    print(f"changed_fields={','.join(changed) if changed else 'none'}")
    print(f"manifest_written={promotion['manifest_written']}")
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())

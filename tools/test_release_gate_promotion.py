#!/usr/bin/env python3
"""Regression tests for evidence-bounded release-gate promotion."""

from __future__ import annotations

import copy

from promote_release_gates import PROMOTABLE_FIELDS, assess

COMMIT = "a" * 40


def base_manifest() -> dict:
    return {
        "release_gate": {
            "repo_check_workflow_verified": False,
            "pages_workflow_verified": False,
            "https_deployment_url_verified": False,
            "built_entrypoint_verified": False,
            "live_root_page_verified": False,
            "deployed_publication_receipt_verified": False,
            "deployed_evidence_bundle_verified": False,
            "stable_release_authorized": False,
        }
    }


def valid_receipt() -> dict:
    return {
        "commit_sha": COMMIT,
        "publication_status": "public_review",
        "canonical_status": "not_authorized",
        "reliance_posture": "research_and_review_only",
        "live_root_verification": {
            "result": "passed",
            "http_status": 200,
            "identity_http_status": 200,
            "deployed_commit_sha": COMMIT,
        },
    }


def valid_decision() -> dict:
    return {
        "commit_sha": COMMIT,
        "evidence_verification": "pass",
        "public_review_decision": "ALLOW",
    }


def valid_bundle() -> dict:
    return {
        "commit_sha": COMMIT,
        "public_review_decision": "ALLOW",
        "bundle_sha256": "b" * 64,
    }


def expect(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def main() -> int:
    manifest = base_manifest()
    proposed, changed, blockers = assess(
        manifest, valid_receipt(), valid_decision(), valid_bundle(), []
    )
    expect(not blockers, "valid evidence should not be blocked")
    expect(set(changed) == set(PROMOTABLE_FIELDS), "all evidence-backed gates should promote")
    expect(proposed["release_gate"]["repo_check_workflow_verified"] is False,
           "repo check gate must remain protected")
    expect(proposed["release_gate"]["stable_release_authorized"] is False,
           "stable authorization must remain protected")
    expect(manifest["release_gate"]["pages_workflow_verified"] is False,
           "input manifest must not mutate")

    stale = valid_receipt()
    stale["live_root_verification"]["deployed_commit_sha"] = "c" * 40
    proposed, changed, blockers = assess(
        base_manifest(), stale, valid_decision(), valid_bundle(), []
    )
    expect("receipt-deployed-commit-mismatch" in blockers, "stale deployment must block")
    expect(not changed, "blocked evidence must not promote fields")

    decision = valid_decision()
    decision["public_review_decision"] = "BLOCK"
    _, changed, blockers = assess(
        base_manifest(), valid_receipt(), decision, valid_bundle(), []
    )
    expect("public-review-decision-not-allow" in blockers, "blocked decision must block")
    expect(not changed, "blocked decision must not promote")

    _, changed, blockers = assess(
        base_manifest(), valid_receipt(), valid_decision(), valid_bundle(), ["file-hash-mismatch:x"]
    )
    expect("bundle:file-hash-mismatch:x" in blockers, "bundle tamper must block")
    expect(not changed, "tampered bundle must not promote")

    authorized = base_manifest()
    authorized["release_gate"]["stable_release_authorized"] = True
    proposed, _, blockers = assess(
        authorized, valid_receipt(), valid_decision(), valid_bundle(), []
    )
    expect(not blockers, "valid evidence should remain valid")
    expect(proposed["release_gate"]["stable_release_authorized"] is True,
           "existing explicit authorization must be preserved, not generated")

    mismatch = valid_bundle()
    mismatch["commit_sha"] = "d" * 40
    _, changed, blockers = assess(
        base_manifest(), valid_receipt(), valid_decision(), mismatch, []
    )
    expect("bundle-commit-mismatch" in blockers, "bundle commit mismatch must block")
    expect(not changed, "mismatched bundle must not promote")

    print("RELEASE_GATE_PROMOTION_TESTS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

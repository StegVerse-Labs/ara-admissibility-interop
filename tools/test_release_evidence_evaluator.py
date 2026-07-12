#!/usr/bin/env python3
"""Dependency-free tests for the governed release-evidence evaluator."""

from __future__ import annotations

import copy

from evaluate_release_evidence import evaluate

HEX = "a" * 64
COMMIT = "b" * 40


def receipt() -> dict:
    return {
        "schema_version": "1.3.0",
        "receipt_type": "governed-publication-receipt",
        "repository": "StegVerse-Labs/ara-admissibility-interop",
        "commit_sha": COMMIT,
        "publication_status": "public_review",
        "canonical_status": "not_authorized",
        "independent_review_status": "not_started",
        "reliance_posture": "research_and_review_only",
        "publish_target": "github_pages",
        "publish_root": "docs",
        "artifact_root": "_site",
        "artifact_kind": "built_site",
        "artifact_tree_sha256": HEX,
        "manifest_sha256": HEX,
        "file_count": 1,
        "files": [{"path": "index.html", "sha256": HEX, "size_bytes": 10}],
        "gate_result": "ALLOW",
        "deployment_url": "https://example.test/",
        "live_root_verification": {
            "result": "passed",
            "verified_at": "2026-07-12T00:00:00Z",
            "requested_url": "https://example.test/",
            "final_url": "https://example.test/",
            "http_status": 200,
            "expected_marker": "ARA Admissibility Interop Docs",
            "marker_found": True,
            "body_sha256": HEX,
            "body_size_bytes": 10,
            "deployed_commit_sha": COMMIT,
            "identity_url": "https://example.test/deployment-identity.json",
            "identity_http_status": 200,
            "identity_sha256": HEX,
        },
    }


def manifest() -> dict:
    return {
        "candidate": "0.2.0-release-candidate",
        "release_gate": {
            "repo_check_workflow_verified": False,
            "pages_workflow_verified": False,
            "https_deployment_url_verified": True,
            "built_entrypoint_verified": False,
            "live_root_page_verified": False,
            "deployed_publication_receipt_verified": False,
            "stable_release_authorized": False,
        },
    }


def expect(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)
    print(f"PASS {name}")


def main() -> int:
    base = evaluate(receipt(), manifest())
    expect("verified public review allowed", base["public_review_decision"] == "ALLOW")
    expect("stable release remains blocked", base["stable_release_decision"] == "BLOCK")
    expect("no automatic stable authorization", base["stable_release_automatically_authorized"] is False)

    stale = receipt()
    stale["live_root_verification"]["deployed_commit_sha"] = "c" * 40
    decision = evaluate(stale, manifest())
    expect("stale commit blocks public review", decision["public_review_decision"] == "BLOCK")

    wrong_posture = receipt()
    wrong_posture["reliance_posture"] = "clinical"
    decision = evaluate(wrong_posture, manifest())
    expect("unexpected reliance posture blocked", decision["public_review_decision"] == "BLOCK")

    fully_verified = manifest()
    for key in fully_verified["release_gate"]:
        fully_verified["release_gate"][key] = True
    decision = evaluate(receipt(), fully_verified)
    expect("stable release allowed only with all explicit gates", decision["stable_release_decision"] == "ALLOW")
    expect("evaluator still does not auto-authorize", decision["stable_release_automatically_authorized"] is False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

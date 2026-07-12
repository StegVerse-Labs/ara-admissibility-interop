#!/usr/bin/env python3
"""Test the independent publication evidence verifier without external dependencies."""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

from verify_publication_evidence import artifact_inventory, sha256_file, verify

COMMIT = "a" * 40


def build_fixture(root: Path) -> tuple[dict, Path, Path, Path]:
    site = root / "site"
    site.mkdir()
    index = site / "index.html"
    identity = site / "deployment-identity.json"
    index.write_text(f"<html><head><meta name='stegverse-deployment-commit' content='{COMMIT}'></head><body>ARA Admissibility Interop Docs</body></html>\n", encoding="utf-8")
    identity.write_text(json.dumps({"commit_sha": COMMIT}, sort_keys=True) + "\n", encoding="utf-8")
    files, tree_hash = artifact_inventory(site)
    receipt = {
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
        "artifact_tree_sha256": tree_hash,
        "manifest_sha256": "b" * 64,
        "file_count": len(files),
        "files": files,
        "gate_result": "ALLOW",
        "deployment_url": "https://example.invalid/site/",
        "live_root_verification": {
            "result": "passed",
            "verified_at": "2026-07-12T00:00:00Z",
            "requested_url": "https://example.invalid/site/",
            "final_url": "https://example.invalid/site/",
            "http_status": 200,
            "expected_marker": "ARA Admissibility Interop Docs",
            "marker_found": True,
            "body_sha256": sha256_file(index),
            "body_size_bytes": index.stat().st_size,
            "deployed_commit_sha": COMMIT,
            "identity_http_status": 200,
            "identity_final_url": "https://example.invalid/site/deployment-identity.json",
            "identity_sha256": sha256_file(identity),
        },
    }
    receipt_path = root / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt, site, identity, index


def main() -> int:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        receipt, site, identity, index = build_fixture(root)

        assert verify(receipt, site, identity, index) == []

        stale = json.loads(json.dumps(receipt))
        stale["live_root_verification"]["deployed_commit_sha"] = "c" * 40
        assert "live-commit-mismatch" in verify(stale)

        tampered = json.loads(json.dumps(receipt))
        tampered["artifact_tree_sha256"] = "d" * 64
        assert "artifact-tree-mismatch" in verify(tampered, site)

        index.write_text("tampered\n", encoding="utf-8")
        problems = verify(receipt, site, identity, index)
        assert "artifact-inventory-mismatch" in problems
        assert "artifact-tree-mismatch" in problems
        assert "live-root-hash-mismatch" in problems

    print("PUBLICATION_EVIDENCE_VERIFIER_TESTS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

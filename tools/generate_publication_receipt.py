#!/usr/bin/env python3
"""Generate a hash-bound receipt for the governed publication package."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from check_publication_gate import ROOT, load_manifest, validate

OUTPUT = ROOT / "status" / "publication-receipt.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    manifest = load_manifest()
    errors = validate(manifest)
    if errors:
        print("PUBLICATION_RECEIPT=FAIL-CLOSED")
        print("reason=" + "; ".join(errors))
        return 1

    publish_root = (ROOT / manifest["publish_root"]).resolve()
    files = []
    for path in sorted(p for p in publish_root.rglob("*") if p.is_file()):
        files.append({
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        })

    receipt = {
        "schema_version": "1.0.0",
        "receipt_type": "governed-publication-receipt",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": os.getenv("GITHUB_REPOSITORY", "StegVerse-Labs/ara-admissibility-interop"),
        "commit_sha": os.getenv("GITHUB_SHA", "local"),
        "workflow_run_id": os.getenv("GITHUB_RUN_ID", "local"),
        "workflow_run_attempt": os.getenv("GITHUB_RUN_ATTEMPT", "local"),
        "publication_status": manifest["publication_status"],
        "canonical_status": manifest["canonical_status"],
        "independent_review_status": manifest["independent_review_status"],
        "clinical_status": manifest["clinical_status"],
        "regulatory_status": manifest["regulatory_status"],
        "reliance_posture": manifest["reliance_posture"],
        "publish_target": manifest["publish_target"],
        "publish_root": manifest["publish_root"],
        "manifest_sha256": sha256_file(ROOT / "publication-manifest.json"),
        "file_count": len(files),
        "files": files,
        "gate_result": "ALLOW",
        "deployment_url": os.getenv("PAGES_DEPLOYMENT_URL", "pending"),
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print("PUBLICATION_RECEIPT=CREATED")
    print(f"output={OUTPUT.relative_to(ROOT)}")
    print(f"file_count={len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

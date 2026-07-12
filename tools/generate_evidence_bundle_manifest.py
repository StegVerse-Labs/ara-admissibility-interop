#!/usr/bin/env python3
"""Generate a deterministic manifest for the retained deployment evidence bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "status" / "deployed-evidence-bundle.json"
DEFAULT_PATHS = [
    "status/publication-status.json",
    "status/publication-receipt.json",
    "status/release-evidence-decision.json",
    "status/release-evidence-decision.md",
    "status/deployed-live-root.html",
    "status/deployed-identity.json",
    "docs/publication-status.md",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bundle_digest(entries: list[dict]) -> str:
    digest = hashlib.sha256()
    for entry in entries:
        digest.update(entry["path"].encode("utf-8"))
        digest.update(b"\0")
        digest.update(entry["sha256"].encode("ascii"))
        digest.update(b"\0")
        digest.update(str(entry["size_bytes"]).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("paths", nargs="*", default=DEFAULT_PATHS)
    args = parser.parse_args()

    entries: list[dict] = []
    for relative in sorted(set(args.paths)):
        path = (ROOT / relative).resolve()
        try:
            path.relative_to(ROOT.resolve())
        except ValueError:
            print(f"EVIDENCE_BUNDLE=FAIL-CLOSED\nreason=path escapes repository: {relative}")
            return 1
        if not path.is_file():
            print(f"EVIDENCE_BUNDLE=FAIL-CLOSED\nreason=missing evidence file: {relative}")
            return 1
        entries.append({
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        })

    receipt = json.loads((ROOT / "status" / "publication-receipt.json").read_text(encoding="utf-8"))
    decision = json.loads((ROOT / "status" / "release-evidence-decision.json").read_text(encoding="utf-8"))
    commit_sha = receipt.get("commit_sha")
    if decision.get("commit_sha") != commit_sha:
        print("EVIDENCE_BUNDLE=FAIL-CLOSED\nreason=decision and receipt commit mismatch")
        return 1

    manifest = {
        "schema_version": "1.0.0",
        "bundle_type": "governed-deployment-evidence-bundle",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": os.getenv("GITHUB_REPOSITORY", receipt.get("repository")),
        "commit_sha": commit_sha,
        "workflow_run_id": os.getenv("GITHUB_RUN_ID", receipt.get("workflow_run_id", "local")),
        "workflow_run_attempt": os.getenv("GITHUB_RUN_ATTEMPT", receipt.get("workflow_run_attempt", "local")),
        "public_review_decision": decision.get("public_review_decision"),
        "stable_release_decision": decision.get("stable_release_decision"),
        "file_count": len(entries),
        "files": entries,
        "bundle_sha256": bundle_digest(entries),
        "boundary": "Bundle integrity does not create canonical, clinical, regulatory, or execution authority.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("EVIDENCE_BUNDLE=CREATED")
    print(f"output={args.output}")
    print(f"bundle_sha256={manifest['bundle_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

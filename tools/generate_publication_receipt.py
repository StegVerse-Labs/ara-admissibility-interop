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


def resolve_artifact_root(manifest: dict) -> tuple[Path, str, str]:
    configured = os.getenv("PUBLICATION_ARTIFACT_ROOT", manifest["publish_root"])
    artifact_kind = os.getenv("PUBLICATION_ARTIFACT_KIND", "source_tree")
    artifact_root = (ROOT / configured).resolve()
    try:
        artifact_root.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError("publication artifact root escapes repository root") from exc
    if not artifact_root.is_dir():
        raise ValueError(f"publication artifact root does not exist: {configured}")
    if artifact_kind == "built_site" and not (artifact_root / "index.html").is_file():
        raise ValueError("built publication artifact has no index.html")
    return artifact_root, configured, artifact_kind


def inventory(artifact_root: Path) -> tuple[list[dict], str]:
    files = []
    tree_digest = hashlib.sha256()
    for path in sorted(p for p in artifact_root.rglob("*") if p.is_file()):
        relative_path = path.relative_to(artifact_root).as_posix()
        file_hash = sha256_file(path)
        size = path.stat().st_size
        files.append({
            "path": relative_path,
            "sha256": file_hash,
            "size_bytes": size,
        })
        tree_digest.update(relative_path.encode("utf-8"))
        tree_digest.update(b"\0")
        tree_digest.update(file_hash.encode("ascii"))
        tree_digest.update(b"\0")
        tree_digest.update(str(size).encode("ascii"))
        tree_digest.update(b"\n")
    return files, tree_digest.hexdigest()


def main() -> int:
    manifest = load_manifest()
    errors = validate(manifest)
    if errors:
        print("PUBLICATION_RECEIPT=FAIL-CLOSED")
        print("reason=" + "; ".join(errors))
        return 1

    try:
        artifact_root, configured_root, artifact_kind = resolve_artifact_root(manifest)
    except ValueError as exc:
        print("PUBLICATION_RECEIPT=FAIL-CLOSED")
        print(f"reason={exc}")
        return 1

    files, artifact_tree_sha256 = inventory(artifact_root)
    if not files:
        print("PUBLICATION_RECEIPT=FAIL-CLOSED")
        print("reason=publication artifact contains no files")
        return 1

    receipt = {
        "schema_version": "1.1.0",
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
        "artifact_root": configured_root,
        "artifact_kind": artifact_kind,
        "artifact_tree_sha256": artifact_tree_sha256,
        "manifest_sha256": sha256_file(ROOT / "publication-manifest.json"),
        "file_count": len(files),
        "files": files,
        "gate_result": "ALLOW",
        "deployment_url": os.getenv("PAGES_DEPLOYMENT_URL", "pending"),
        "live_root_verification": os.getenv("LIVE_ROOT_VERIFICATION", "not_run"),
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print("PUBLICATION_RECEIPT=CREATED")
    print(f"output={OUTPUT.relative_to(ROOT)}")
    print(f"artifact_kind={artifact_kind}")
    print(f"artifact_root={configured_root}")
    print(f"artifact_tree_sha256={artifact_tree_sha256}")
    print(f"file_count={len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

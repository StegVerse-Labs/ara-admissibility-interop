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
    if artifact_kind == "built_site":
        if not (artifact_root / "index.html").is_file():
            raise ValueError("built publication artifact has no index.html")
        if not (artifact_root / "deployment-identity.json").is_file():
            raise ValueError("built publication artifact has no deployment identity")
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


def optional_int(name: str) -> int | None:
    raw = os.getenv(name, "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc


def live_verification_record(expected_commit: str) -> dict:
    result = os.getenv("LIVE_ROOT_VERIFICATION", "not_run")
    record = {
        "result": result,
        "verified_at": os.getenv("LIVE_ROOT_VERIFIED_AT", ""),
        "requested_url": os.getenv("PAGES_DEPLOYMENT_URL", "pending"),
        "final_url": os.getenv("LIVE_ROOT_FINAL_URL", ""),
        "http_status": optional_int("LIVE_ROOT_HTTP_STATUS"),
        "expected_marker": os.getenv("LIVE_ROOT_EXPECTED_MARKER", ""),
        "marker_found": os.getenv("LIVE_ROOT_MARKER_FOUND", "false").lower() == "true",
        "body_sha256": os.getenv("LIVE_ROOT_BODY_SHA256", ""),
        "body_size_bytes": optional_int("LIVE_ROOT_BODY_SIZE_BYTES"),
        "deployed_commit_sha": os.getenv("LIVE_ROOT_DEPLOYED_COMMIT_SHA", ""),
        "identity_http_status": optional_int("LIVE_IDENTITY_HTTP_STATUS"),
        "identity_final_url": os.getenv("LIVE_IDENTITY_FINAL_URL", ""),
        "identity_body_sha256": os.getenv("LIVE_IDENTITY_BODY_SHA256", ""),
    }
    if result == "passed":
        if record["http_status"] != 200:
            raise ValueError("passed live-root verification requires HTTP 200")
        if not record["final_url"].startswith("https://"):
            raise ValueError("passed live-root verification requires an HTTPS final URL")
        if not record["marker_found"] or not record["expected_marker"]:
            raise ValueError("passed live-root verification requires the expected marker")
        if len(record["body_sha256"]) != 64:
            raise ValueError("passed live-root verification requires a SHA-256 body hash")
        if not record["verified_at"]:
            raise ValueError("passed live-root verification requires a timestamp")
        if record["deployed_commit_sha"] != expected_commit:
            raise ValueError("passed live-root verification requires the current commit identity")
        if record["identity_http_status"] != 200:
            raise ValueError("passed live-root verification requires HTTP 200 for deployment identity")
        if not record["identity_final_url"].startswith("https://"):
            raise ValueError("passed live-root verification requires an HTTPS identity URL")
        if len(record["identity_body_sha256"]) != 64:
            raise ValueError("passed live-root verification requires a SHA-256 identity hash")
    return record


def main() -> int:
    manifest = load_manifest()
    errors = validate(manifest)
    if errors:
        print("PUBLICATION_RECEIPT=FAIL-CLOSED")
        print("reason=" + "; ".join(errors))
        return 1

    commit_sha = os.getenv("GITHUB_SHA", "local")
    try:
        artifact_root, configured_root, artifact_kind = resolve_artifact_root(manifest)
        live_root = live_verification_record(commit_sha)
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
        "schema_version": "1.3.0",
        "receipt_type": "governed-publication-receipt",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": os.getenv("GITHUB_REPOSITORY", "StegVerse-Labs/ara-admissibility-interop"),
        "commit_sha": commit_sha,
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
        "live_root_verification": live_root,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print("PUBLICATION_RECEIPT=CREATED")
    print(f"output={OUTPUT.relative_to(ROOT)}")
    print(f"artifact_kind={artifact_kind}")
    print(f"artifact_root={configured_root}")
    print(f"artifact_tree_sha256={artifact_tree_sha256}")
    print(f"live_root_verification={live_root['result']}")
    print(f"deployed_commit_sha={live_root['deployed_commit_sha']}")
    print(f"file_count={len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

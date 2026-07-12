#!/usr/bin/env python3
"""Independently verify a governed publication receipt and optional evidence files."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HEX64 = set("0123456789abcdef")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def valid_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value) <= HEX64


def artifact_inventory(root: Path) -> tuple[list[dict], str]:
    files: list[dict] = []
    tree_digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        relative = path.relative_to(root).as_posix()
        digest = sha256_file(path)
        size = path.stat().st_size
        files.append({"path": relative, "sha256": digest, "size_bytes": size})
        tree_digest.update(relative.encode("utf-8"))
        tree_digest.update(b"\0")
        tree_digest.update(digest.encode("ascii"))
        tree_digest.update(b"\0")
        tree_digest.update(str(size).encode("ascii"))
        tree_digest.update(b"\n")
    return files, tree_digest.hexdigest()


def verify(receipt: dict, artifact_root: Path | None = None,
           identity_file: Path | None = None, live_root_file: Path | None = None) -> list[str]:
    problems: list[str] = []
    required = {
        "schema_version", "receipt_type", "repository", "commit_sha",
        "publication_status", "canonical_status", "independent_review_status",
        "reliance_posture", "publish_target", "publish_root", "artifact_root",
        "artifact_kind", "artifact_tree_sha256", "manifest_sha256", "file_count",
        "files", "gate_result", "deployment_url", "live_root_verification",
    }
    missing = sorted(required - set(receipt))
    problems.extend(f"missing:{name}" for name in missing)
    if missing:
        return problems

    if receipt.get("receipt_type") != "governed-publication-receipt":
        problems.append("receipt-type")
    if receipt.get("gate_result") != "ALLOW":
        problems.append("gate-result")
    if not valid_sha256(receipt.get("artifact_tree_sha256")):
        problems.append("artifact-tree-sha256")
    if not valid_sha256(receipt.get("manifest_sha256")):
        problems.append("manifest-sha256")

    files = receipt.get("files")
    if not isinstance(files, list) or not files:
        problems.append("files-empty")
    elif receipt.get("file_count") != len(files):
        problems.append("file-count")
    else:
        seen: set[str] = set()
        for entry in files:
            if not isinstance(entry, dict):
                problems.append("file-entry-type")
                continue
            path = entry.get("path")
            if not isinstance(path, str) or not path or path.startswith("/") or ".." in Path(path).parts:
                problems.append(f"file-path:{path}")
            elif path in seen:
                problems.append(f"duplicate-file:{path}")
            else:
                seen.add(path)
            if not valid_sha256(entry.get("sha256")):
                problems.append(f"file-sha256:{path}")
            if not isinstance(entry.get("size_bytes"), int) or entry["size_bytes"] < 0:
                problems.append(f"file-size:{path}")

    live = receipt.get("live_root_verification")
    if not isinstance(live, dict):
        problems.append("live-verification-type")
    elif live.get("result") == "passed":
        if live.get("http_status") != 200:
            problems.append("live-http-status")
        if not str(live.get("final_url", "")).startswith("https://"):
            problems.append("live-final-url")
        if not live.get("marker_found") or not live.get("expected_marker"):
            problems.append("live-marker")
        if not valid_sha256(live.get("body_sha256")):
            problems.append("live-body-sha256")
        if live.get("deployed_commit_sha") != receipt.get("commit_sha"):
            problems.append("live-commit-mismatch")
        if not valid_sha256(live.get("identity_sha256")):
            problems.append("identity-sha256")

    if artifact_root is not None:
        if not artifact_root.is_dir():
            problems.append("artifact-root-missing")
        else:
            actual_files, actual_tree = artifact_inventory(artifact_root)
            expected = sorted(files or [], key=lambda item: item.get("path", ""))
            if actual_files != expected:
                problems.append("artifact-inventory-mismatch")
            if actual_tree != receipt.get("artifact_tree_sha256"):
                problems.append("artifact-tree-mismatch")

    if identity_file is not None:
        if not identity_file.is_file():
            problems.append("identity-file-missing")
        else:
            if sha256_file(identity_file) != live.get("identity_sha256"):
                problems.append("identity-file-hash-mismatch")
            try:
                identity = json.loads(identity_file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                problems.append("identity-file-invalid")
            else:
                if identity.get("commit_sha") != receipt.get("commit_sha"):
                    problems.append("identity-commit-mismatch")

    if live_root_file is not None:
        if not live_root_file.is_file():
            problems.append("live-root-file-missing")
        elif sha256_file(live_root_file) != live.get("body_sha256"):
            problems.append("live-root-hash-mismatch")

    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--artifact-root", type=Path)
    parser.add_argument("--identity-file", type=Path)
    parser.add_argument("--live-root-file", type=Path)
    args = parser.parse_args()

    try:
        receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"PUBLICATION_EVIDENCE=FAIL\nreason={exc}")
        return 1

    problems = verify(receipt, args.artifact_root, args.identity_file, args.live_root_file)
    result = {
        "result": "pass" if not problems else "fail",
        "problem_count": len(problems),
        "problems": problems,
        "commit_sha": receipt.get("commit_sha"),
        "artifact_tree_sha256": receipt.get("artifact_tree_sha256"),
    }
    print(json.dumps(result, indent=2))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())

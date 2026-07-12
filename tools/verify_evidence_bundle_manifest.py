#!/usr/bin/env python3
"""Verify a governed deployment evidence bundle manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HEX = set("0123456789abcdef")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def valid_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value) <= HEX


def bundle_digest(entries: list[dict]) -> str:
    digest = hashlib.sha256()
    for entry in sorted(entries, key=lambda item: item["path"]):
        digest.update(entry["path"].encode("utf-8"))
        digest.update(b"\0")
        digest.update(entry["sha256"].encode("ascii"))
        digest.update(b"\0")
        digest.update(str(entry["size_bytes"]).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def verify(manifest: dict, root: Path) -> list[str]:
    problems: list[str] = []
    required = {"schema_version", "bundle_type", "commit_sha", "file_count", "files", "bundle_sha256"}
    for field in sorted(required - set(manifest)):
        problems.append(f"missing:{field}")
    if problems:
        return problems
    if manifest.get("bundle_type") != "governed-deployment-evidence-bundle":
        problems.append("bundle-type")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        problems.append("files-empty")
        return problems
    if manifest.get("file_count") != len(files):
        problems.append("file-count")
    seen: set[str] = set()
    normalized: list[dict] = []
    for entry in files:
        if not isinstance(entry, dict):
            problems.append("file-entry-type")
            continue
        relative = entry.get("path")
        digest = entry.get("sha256")
        size = entry.get("size_bytes")
        if not isinstance(relative, str) or not relative or relative.startswith("/") or ".." in Path(relative).parts:
            problems.append(f"file-path:{relative}")
            continue
        if relative in seen:
            problems.append(f"duplicate-file:{relative}")
            continue
        seen.add(relative)
        if not valid_sha256(digest):
            problems.append(f"file-sha256:{relative}")
            continue
        if not isinstance(size, int) or size < 0:
            problems.append(f"file-size:{relative}")
            continue
        path = (root / relative).resolve()
        try:
            path.relative_to(root.resolve())
        except ValueError:
            problems.append(f"file-escape:{relative}")
            continue
        if not path.is_file():
            problems.append(f"file-missing:{relative}")
            continue
        if path.stat().st_size != size:
            problems.append(f"file-size-mismatch:{relative}")
        if sha256_file(path) != digest:
            problems.append(f"file-hash-mismatch:{relative}")
        normalized.append({"path": relative, "sha256": digest, "size_bytes": size})
    if valid_sha256(manifest.get("bundle_sha256")):
        if bundle_digest(normalized) != manifest.get("bundle_sha256"):
            problems.append("bundle-sha256-mismatch")
    else:
        problems.append("bundle-sha256")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"EVIDENCE_BUNDLE_VERIFY=FAIL\nreason={exc}")
        return 1
    problems = verify(manifest, args.root)
    print(json.dumps({
        "result": "pass" if not problems else "fail",
        "problem_count": len(problems),
        "problems": problems,
        "commit_sha": manifest.get("commit_sha"),
        "bundle_sha256": manifest.get("bundle_sha256"),
    }, indent=2))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())

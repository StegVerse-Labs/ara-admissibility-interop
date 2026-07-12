#!/usr/bin/env python3
"""Exercise positive and negative evidence-bundle verification cases."""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
from pathlib import Path

from verify_evidence_bundle_manifest import bundle_digest, verify


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_manifest(root: Path) -> dict:
    files = []
    for relative, content in (
        ("status/publication-receipt.json", "{}\n"),
        ("status/release-evidence-decision.json", '{"public_review_decision":"ALLOW"}\n'),
    ):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        files.append({
            "path": relative,
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        })
    files.sort(key=lambda item: item["path"])
    return {
        "schema_version": "1.0.0",
        "bundle_type": "governed-deployment-evidence-bundle",
        "commit_sha": "a" * 40,
        "file_count": len(files),
        "files": files,
        "bundle_sha256": bundle_digest(files),
    }


def require_problem(manifest: dict, root: Path, expected: str) -> None:
    problems = verify(manifest, root)
    if not any(problem == expected or problem.startswith(expected) for problem in problems):
        raise AssertionError(f"expected {expected!r}, got {problems!r}")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        valid = make_manifest(root)
        assert verify(valid, root) == []

        tampered_file = copy.deepcopy(valid)
        (root / tampered_file["files"][0]["path"]).write_text("tampered\n", encoding="utf-8")
        require_problem(tampered_file, root, "file-size-mismatch:")
        require_problem(tampered_file, root, "file-hash-mismatch:")
        valid = make_manifest(root)

        missing = copy.deepcopy(valid)
        (root / missing["files"][0]["path"]).unlink()
        require_problem(missing, root, "file-missing:")
        valid = make_manifest(root)

        duplicate = copy.deepcopy(valid)
        duplicate["files"].append(copy.deepcopy(duplicate["files"][0]))
        duplicate["file_count"] = len(duplicate["files"])
        require_problem(duplicate, root, "duplicate-file:")

        escaping = copy.deepcopy(valid)
        escaping["files"][0]["path"] = "../outside.json"
        require_problem(escaping, root, "file-path:")

        bad_digest = copy.deepcopy(valid)
        bad_digest["bundle_sha256"] = "0" * 64
        require_problem(bad_digest, root, "bundle-sha256-mismatch")

        bad_count = copy.deepcopy(valid)
        bad_count["file_count"] = 999
        require_problem(bad_count, root, "file-count")

        malformed_hash = copy.deepcopy(valid)
        malformed_hash["files"][0]["sha256"] = "not-a-hash"
        require_problem(malformed_hash, root, "file-sha256:")

    print(json.dumps({
        "result": "pass",
        "tested": [
            "valid-bundle",
            "tampered-file",
            "missing-file",
            "duplicate-entry",
            "escaping-path",
            "aggregate-hash-mismatch",
            "file-count-mismatch",
            "malformed-file-hash",
        ],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

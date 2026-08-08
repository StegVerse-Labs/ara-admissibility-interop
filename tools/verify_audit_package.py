#!/usr/bin/env python3
"""Verify generated StegGate fixture Audit Kit package integrity and reconstruction agreement."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from build_audit_package import build

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE = ROOT / "reports" / "audit-kit-fixture-001"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def run_json(command: list[str]) -> dict[str, Any]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise ValueError(f"command failed ({' '.join(command)}): {result.stderr.strip()}")
    value = json.loads(result.stdout)
    if not isinstance(value, dict):
        raise ValueError(f"command did not return JSON object: {' '.join(command)}")
    return value


def verify_integrity(package: Path) -> dict[str, Any]:
    manifest_path = package / "package-manifest.json"
    manifest = load(manifest_path)
    if manifest.get("schema_version") != "steggate.audit-package-manifest.v1":
        raise ValueError("audit package manifest schema mismatch")
    if manifest.get("classification") != "fixture_only_not_customer_validation":
        raise ValueError("fixture audit package classification mismatch")
    if manifest.get("authority_effect") is not False:
        raise ValueError("audit package authority_effect must remain false")

    expected_objects = manifest.get("objects")
    if not isinstance(expected_objects, dict) or not expected_objects:
        raise ValueError("audit package object map missing")
    observed_paths = {
        str(path.relative_to(package))
        for path in package.rglob("*")
        if path.is_file() and path.name != "package-manifest.json"
    }
    if observed_paths != set(expected_objects):
        raise ValueError(f"audit package object set mismatch: observed={sorted(observed_paths)} expected={sorted(expected_objects)}")
    for rel, expected_hash in expected_objects.items():
        path = package / rel
        if not path.is_file():
            raise FileNotFoundError(f"missing audit package object: {rel}")
        observed_hash = sha(path)
        if observed_hash != expected_hash:
            raise ValueError(f"audit package hash mismatch for {rel}: {observed_hash} != {expected_hash}")

    bindings = manifest.get("source_bindings")
    if not isinstance(bindings, dict) or not bindings:
        raise ValueError("audit package source bindings missing")
    for rel, expected_hash in bindings.items():
        path = ROOT / rel
        if not path.is_file():
            raise FileNotFoundError(f"missing bound source: {rel}")
        observed_hash = sha(path)
        if observed_hash != expected_hash:
            raise ValueError(f"bound source changed without package regeneration: {rel}")

    report = load(package / "audit-report.json")
    if report.get("schema_version") != "steggate.audit-report.v1":
        raise ValueError("audit report schema mismatch")
    if report.get("classification") != "fixture_only_not_customer_validation":
        raise ValueError("audit report classification mismatch")
    non_claims = set(report.get("non_claims", []))
    required_non_claims = {"not customer validation", "not a real consequential-boundary observation", "not execution authority", "not release approval", "not publication authority"}
    if not required_non_claims.issubset(non_claims):
        raise ValueError("audit report required non-claims missing")
    if report.get("receipt", {}).get("authority_effect") is not False:
        raise ValueError("audit report receipt authority_effect must remain false")

    evidence_manifest = package / "evidence-pack" / "manifest.json"
    py = run_json(["python", "tools/verify_audit_kit.py", "--manifest", str(evidence_manifest)])
    js = run_json(["node", "tools/verify_audit_kit_node.mjs", "--manifest", str(evidence_manifest)])
    agreement_keys = ["status", "pack_id", "candidate_id", "decision", "reason_code", "canonical_hashes", "achieved_assurance_profile", "authority_effect"]
    for key in agreement_keys:
        if py.get(key) != js.get(key):
            raise ValueError(f"Python/Node audit package reconstruction disagreement at {key}")
    if py.get("status") != "PASS" or py.get("authority_effect") is not False:
        raise ValueError("audit package reconstruction did not fail-safe to PASS/non-authority posture")
    if report["candidate"]["candidate_id"] != py["candidate_id"] or report["candidate"]["canonical_hash"] != py["canonical_hashes"]["candidate"]:
        raise ValueError("audit report candidate reconstruction mismatch")
    if report["decision"]["value"] != py["decision"] or report["decision"]["reason_code"] != py["reason_code"]:
        raise ValueError("audit report decision reconstruction mismatch")
    if report["receipt"]["canonical_hash"] != py["canonical_hashes"]["receipt"]:
        raise ValueError("audit report receipt reconstruction mismatch")

    with tempfile.TemporaryDirectory(prefix="steggate-audit-package-freshness-") as tmp:
        rebuilt = Path(tmp) / "rebuilt"
        build(rebuilt)
        for rel in sorted(list(expected_objects) + ["package-manifest.json"]):
            original = package / rel
            fresh = rebuilt / rel
            if not fresh.is_file() or original.read_bytes() != fresh.read_bytes():
                raise ValueError(f"audit package is stale or nondeterministic: {rel}")

    return {
        "status": "PASS",
        "package_id": manifest["package_id"],
        "objects": len(expected_objects),
        "python_node_agreement": True,
        "deterministic_rebuild": True,
        "authority_effect": False,
    }


def self_test(package: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="steggate-audit-package-tamper-") as tmp:
        copied = Path(tmp) / "package"
        shutil.copytree(package, copied)
        report = copied / "audit-report.json"
        report.write_bytes(report.read_bytes() + b" ")
        try:
            verify_integrity(copied)
        except ValueError as exc:
            if "hash mismatch" not in str(exc):
                raise
        else:
            raise AssertionError("tampered audit report was accepted")
    with tempfile.TemporaryDirectory(prefix="steggate-audit-package-missing-") as tmp:
        copied = Path(tmp) / "package"
        shutil.copytree(package, copied)
        missing = copied / "evidence-pack" / "source" / "receipt.json"
        missing.unlink()
        try:
            verify_integrity(copied)
        except (ValueError, FileNotFoundError):
            pass
        else:
            raise AssertionError("audit package with missing evidence was accepted")
    return {"tamper_refused": True, "missing_refused": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path, nargs="?", default=DEFAULT_PACKAGE)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    result = verify_integrity(args.package)
    if args.self_test:
        result.update(self_test(args.package))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

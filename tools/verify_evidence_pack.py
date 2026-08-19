#!/usr/bin/env python3
"""Offline content-bounded verifier for StegGate evidence-pack manifests."""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "fixtures" / "evidence-pack" / "manifest.json"
REQUIRED_ROLES = {"candidate","policy_authority_evidence","decision","receipt","coverage","verifier_inputs"}
FORBIDDEN_KEYS = {"credential","credentials","password","private_prompt","provider_response","secret","token"}


def sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def scan_forbidden(value, *, path="$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower() in FORBIDDEN_KEYS:
                raise ValueError(f"forbidden embedded field at {path}.{key}")
            scan_forbidden(item, path=f"{path}.{key}")
    elif isinstance(value, list):
        for i, item in enumerate(value):
            scan_forbidden(item, path=f"{path}[{i}]")


def verify(manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "steggate.evidence-pack-manifest.v1":
        raise ValueError("manifest schema_version mismatch")
    if manifest.get("canonicalization_profile") != "stegverse.jcs.v1":
        raise ValueError("canonicalization profile mismatch")
    if not manifest.get("trust_assumptions") or not manifest.get("non_claims"):
        raise ValueError("trust assumptions and non-claims are required")
    assurance = manifest.get("achieved_assurance")
    if not isinstance(assurance, dict) or assurance.get("profile_ref") != "steggate.assurance-profile.v1":
        raise ValueError("achieved assurance report missing or unbound")
    entries = manifest.get("objects")
    if not isinstance(entries, list):
        raise ValueError("manifest objects missing")
    roles = [entry.get("role") for entry in entries]
    if set(roles) != REQUIRED_ROLES or len(roles) != len(REQUIRED_ROLES):
        raise ValueError(f"evidence-pack roles mismatch: {roles}")
    base = manifest_path.parent
    checked = 0
    for entry in entries:
        rel = Path(entry["path"])
        if rel.is_absolute() or ".." in rel.parts:
            raise ValueError(f"unsafe evidence path: {rel}")
        source = base / rel
        if not source.is_file():
            raise FileNotFoundError(f"missing evidence object: {rel}")
        expected = entry.get("sha256")
        observed = sha(source)
        if expected != observed:
            raise ValueError(f"hash mismatch for {rel}: {observed} != {expected}")
        data = json.loads(source.read_text(encoding="utf-8"))
        scan_forbidden(data)
        if entry["role"] == "policy_authority_evidence":
            if entry.get("sensitive_handling") != "commitment_and_refs_only":
                raise ValueError("policy/authority evidence must be commitment_and_refs_only")
            if data.get("content_included") is not False or data.get("commitment_only") is not True:
                raise ValueError("policy/authority fixture improperly embeds sensitive content")
        checked += 1
    return {"status":"PASS","pack_id":manifest["pack_id"],"objects":checked,"authority_effect":False}


def self_test(manifest_path: Path) -> dict:
    source_root = manifest_path.parent
    with tempfile.TemporaryDirectory() as tmp:
        copied = Path(tmp) / "pack"
        shutil.copytree(source_root, copied)
        copied_manifest = copied / manifest_path.name
        verify(copied_manifest)
        candidate = copied / "source" / "candidate.json"
        candidate.write_bytes(candidate.read_bytes() + b" ")
        try:
            verify(copied_manifest)
        except ValueError as exc:
            if "hash mismatch" not in str(exc):
                raise
        else:
            raise AssertionError("tampered evidence object was accepted")
    with tempfile.TemporaryDirectory() as tmp:
        copied = Path(tmp) / "pack"
        shutil.copytree(source_root, copied)
        copied_manifest = copied / manifest_path.name
        (copied / "source" / "receipt.json").unlink()
        try:
            verify(copied_manifest)
        except FileNotFoundError:
            pass
        else:
            raise AssertionError("missing evidence object was accepted")
    return {"status":"PASS","tamper_refused":True,"missing_refused":True}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path, nargs="?", default=DEFAULT_MANIFEST)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    result = verify(args.manifest)
    if args.self_test:
        result.update(self_test(args.manifest))
    print(json.dumps(result, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

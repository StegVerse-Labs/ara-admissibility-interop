#!/usr/bin/env python3
"""Build or check a content-bounded StegGate evidence-pack manifest."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPEC = ROOT / "fixtures" / "evidence-pack" / "pack-spec.json"
DEFAULT_MANIFEST = ROOT / "fixtures" / "evidence-pack" / "manifest.json"


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def build(spec_path: Path) -> dict:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if spec.get("schema_version") != "steggate.evidence-pack-spec.v1":
        raise ValueError("unsupported evidence-pack spec")
    base = spec_path.parent
    objects = []
    for entry in spec.get("objects", []):
        rel = Path(entry["path"])
        if rel.is_absolute() or ".." in rel.parts:
            raise ValueError(f"unsafe evidence path: {rel}")
        source = base / rel
        if not source.is_file():
            raise FileNotFoundError(f"missing evidence object: {rel}")
        objects.append({**entry, "sha256": digest(source)})
    manifest = {
        "pack_id": spec["pack_id"],
        "canonicalization_profile": spec["canonicalization_profile"],
        "objects": objects,
        "achieved_assurance": spec["achieved_assurance"],
        "trust_assumptions": spec["trust_assumptions"],
        "non_claims": spec["non_claims"],
        "schema_version": "steggate.evidence-pack-manifest.v1",
    }
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--output", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    built = build(args.spec)
    if args.check:
        current = json.loads(args.output.read_text(encoding="utf-8"))
        if current != built:
            raise SystemExit("evidence-pack manifest is stale or inconsistent with source objects")
        print(json.dumps({"status":"PASS","objects":len(built["objects"]),"pack_id":built["pack_id"]}, sort_keys=True))
        return 0
    args.output.write_text(json.dumps(built, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.output)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

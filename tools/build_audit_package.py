#!/usr/bin/env python3
"""Build the deterministic fixture-backed StegGate Audit Kit package."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from verify_audit_kit import verify_semantics

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PACK = ROOT / "fixtures" / "evidence-pack"
DEFAULT_OUTPUT = ROOT / "reports" / "audit-kit-fixture-001"
TEMPLATE = ROOT / "audit-kit" / "AUDIT_REPORT_TEMPLATE.md"
REASON_REGISTRY = ROOT / "reasons" / "registry.v1.json"
TOOL_BINDINGS = [
    "tools/canonicalize_steggate.py",
    "tools/verify_evidence_pack.py",
    "tools/verify_audit_kit.py",
    "tools/canonicalize_steggate_node.mjs",
    "tools/verify_audit_kit_node.mjs",
    "tools/validate_track1b_parity.mjs",
]


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def reason_description(code: str) -> str:
    registry = load(REASON_REGISTRY)
    for entry in registry.get("reasons", []):
        if entry.get("code") == code:
            return str(entry.get("description", ""))
    raise ValueError(f"reason code absent from registry: {code}")


def render_markdown(report: dict[str, Any]) -> str:
    assurance = report["achieved_assurance"]
    coverage = report["coverage"]
    lines = [
        "# StegGate Fixture Boundary Audit — audit-kit-fixture-001",
        "",
        "> **Fixture evidence only. This is not customer validation or execution/release/publication authority.**",
        "",
        "## Audit identity",
        "",
        f"- Package: `{report['package_id']}`",
        f"- Classification: `{report['classification']}`",
        f"- Canonicalization profile: `{report['canonicalization_profile']}`",
        "",
        "## Candidate binding",
        "",
        f"- Candidate id: `{report['candidate']['candidate_id']}`",
        f"- Candidate canonical id: `{report['candidate']['canonical_hash']}`",
        f"- Action: `{report['candidate']['action']}`",
        "",
        "## Decision reconstruction",
        "",
        f"- Decision: `{report['decision']['value']}`",
        f"- Reason: `{report['decision']['reason_code']}` — {report['decision']['reason_description']}",
        "",
        "## Receipt reconstruction",
        "",
        f"- Receipt id: `{report['receipt']['receipt_id']}`",
        f"- Receipt canonical id: `{report['receipt']['canonical_hash']}`",
        f"- Authority effect: `{str(report['receipt']['authority_effect']).lower()}`",
        "",
        "## Evidence pack",
        "",
        f"- Evidence pack id: `{report['evidence_pack']['pack_id']}`",
        f"- Bound objects: `{report['evidence_pack']['objects']}`",
        "- Policy/authority content posture: `commitment_and_refs_only`",
        "",
        "## Achieved assurance",
        "",
    ]
    for key in ("identity", "signatures", "trust_anchor", "source_evidence", "capability_construction"):
        lines.append(f"- {key}: `{assurance[key]}`")
    lines.extend(["", "## Coverage", "", f"```json\n{json.dumps(coverage, sort_keys=True)}\n```", "", "## Independent verification", ""])
    for command in report["independent_verification"]["commands"]:
        lines.append(f"- `{command}`")
    lines.extend(["", "## Trust assumptions", ""])
    lines.extend(f"- {item}" for item in report["trust_assumptions"])
    lines.extend(["", "## Non-claims", ""])
    lines.extend(f"- {item}" for item in report["non_claims"])
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.append("")
    return "\n".join(lines)


def build(output: Path) -> dict[str, Any]:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    evidence_copy = output / "evidence-pack"
    shutil.copytree(SOURCE_PACK, evidence_copy)

    source_manifest = SOURCE_PACK / "manifest.json"
    verification = verify_semantics(source_manifest)
    manifest = load(source_manifest)
    objects = {entry["role"]: entry for entry in manifest["objects"]}
    candidate = load(SOURCE_PACK / objects["candidate"]["path"])
    receipt = load(SOURCE_PACK / objects["receipt"]["path"])
    coverage = load(SOURCE_PACK / objects["coverage"]["path"])

    report = {
        "schema_version": "steggate.audit-report.v1",
        "package_id": "audit-kit-fixture-001",
        "classification": "fixture_only_not_customer_validation",
        "canonicalization_profile": "stegverse.jcs.v1",
        "candidate": {
            "candidate_id": verification["candidate_id"],
            "canonical_hash": verification["canonical_hashes"]["candidate"],
            "action": candidate.get("action"),
        },
        "decision": {
            "value": verification["decision"],
            "reason_code": verification["reason_code"],
            "reason_description": reason_description(verification["reason_code"]),
            "canonical_hash": verification["canonical_hashes"]["decision"],
        },
        "receipt": {
            "receipt_id": receipt.get("receipt_id"),
            "canonical_hash": verification["canonical_hashes"]["receipt"],
            "authority_effect": False,
        },
        "evidence_pack": {
            "pack_id": manifest["pack_id"],
            "manifest_sha256": sha(source_manifest),
            "objects": len(manifest["objects"]),
            "object_commitments": {entry["role"]: entry["sha256"] for entry in manifest["objects"]},
        },
        "achieved_assurance": manifest["achieved_assurance"],
        "coverage": coverage,
        "independent_verification": {
            "commands": [
                "python tools/verify_audit_kit.py --manifest reports/audit-kit-fixture-001/evidence-pack/manifest.json",
                "node tools/verify_audit_kit_node.mjs --manifest reports/audit-kit-fixture-001/evidence-pack/manifest.json",
                "node tools/validate_track1b_parity.mjs",
            ],
            "required_agreement": "python_and_node",
            "authority_effect": False,
        },
        "trust_assumptions": manifest["trust_assumptions"],
        "non_claims": manifest["non_claims"] + ["not customer validation", "not a real consequential-boundary observation"],
        "limitations": verification["limitations"],
    }
    write_json(output / "audit-report.json", report)
    (output / "AUDIT_REPORT.md").write_text(render_markdown(report), encoding="utf-8")

    package_objects: dict[str, str] = {}
    for path in sorted(output.rglob("*")):
        if path.is_file() and path.name != "package-manifest.json":
            package_objects[str(path.relative_to(output))] = sha(path)
    source_bindings = {"audit-kit/AUDIT_REPORT_TEMPLATE.md": sha(TEMPLATE)}
    for rel in TOOL_BINDINGS:
        source_bindings[rel] = sha(ROOT / rel)
    package_manifest = {
        "schema_version": "steggate.audit-package-manifest.v1",
        "package_id": report["package_id"],
        "classification": report["classification"],
        "objects": package_objects,
        "source_bindings": source_bindings,
        "verification": {
            "python": "tools/verify_audit_kit.py",
            "node": "tools/verify_audit_kit_node.mjs",
            "cross_language_parity": "tools/validate_track1b_parity.mjs",
        },
        "authority_effect": False,
    }
    write_json(output / "package-manifest.json", package_manifest)
    return {"status": "PASS", "package_id": report["package_id"], "objects": len(package_objects), "authority_effect": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(build(args.output), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

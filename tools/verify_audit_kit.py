#!/usr/bin/env python3
"""Offline StegGate Audit Kit verifier and reconstruction command.

The verifier is intentionally independent from consequence execution. It verifies
content-bounded pack integrity, canonical candidate/receipt bytes, reason/decision
coherence, achieved-assurance binding, and retained Goal 0 compatibility fixtures.
It grants no execution, release, publication, deployment, or standards authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from canonicalize_steggate import canonicalize
from verify_evidence_pack import verify as verify_evidence_pack

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "fixtures" / "verifier" / "cases.json"
REASON_REGISTRY = ROOT / "reasons" / "registry.v1.json"
ALLOWED_DECISIONS = {"ALLOW", "DENY", "REVIEW", "FAIL_CLOSED"}
ASSURANCE_DIMENSIONS = {
    "identity",
    "signatures",
    "trust_anchor",
    "source_evidence",
    "capability_construction",
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def canonical_id(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonicalize(value)).hexdigest()


def raw_id(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def write_canonical(path: Path, value: Any) -> None:
    path.write_bytes(canonicalize(value))


def reason_codes() -> set[str]:
    registry = load(REASON_REGISTRY)
    if registry.get("schema_version") != "steggate.reason-registry.v1":
        raise ValueError("reason registry schema mismatch")
    if registry.get("authority_effect") is not False:
        raise ValueError("reason registry must have authority_effect=false")
    return {item["code"] for item in registry.get("reasons", [])}


def object_index(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {entry["role"]: entry for entry in manifest.get("objects", [])}


def verify_canonical_object(base: Path, entry: dict[str, Any]) -> str:
    path = base / entry["path"]
    value = load(path)
    canonical_hash = canonical_id(value)
    if canonical_hash != entry.get("sha256"):
        raise ValueError(
            f"{entry['role']} canonical hash mismatch: {canonical_hash} != {entry.get('sha256')}"
        )
    if raw_id(path) != canonical_hash:
        raise ValueError(f"{entry['role']} bytes are not canonical stegverse.jcs.v1 bytes")
    return canonical_hash


def verify_semantics(manifest_path: Path) -> dict[str, Any]:
    pack_result = verify_evidence_pack(manifest_path)
    manifest = load(manifest_path)
    base = manifest_path.parent
    objects = object_index(manifest)
    for role in ("candidate", "decision", "receipt", "verifier_inputs"):
        if role not in objects:
            raise ValueError(f"missing required role: {role}")

    candidate = load(base / objects["candidate"]["path"])
    decision = load(base / objects["decision"]["path"])
    receipt = load(base / objects["receipt"]["path"])
    verifier_inputs = load(base / objects["verifier_inputs"]["path"])

    candidate_hash = verify_canonical_object(base, objects["candidate"])
    decision_hash = verify_canonical_object(base, objects["decision"])
    receipt_hash = verify_canonical_object(base, objects["receipt"])
    verify_canonical_object(base, objects["verifier_inputs"])

    candidate_id = candidate.get("candidate_id")
    if not candidate_id or decision.get("candidate_id") != candidate_id or receipt.get("candidate_id") != candidate_id:
        raise ValueError("candidate_id binding mismatch across candidate/decision/receipt")

    decision_value = decision.get("decision")
    if decision_value not in ALLOWED_DECISIONS:
        raise ValueError(f"unsupported decision: {decision_value}")
    if receipt.get("decision") != decision_value:
        raise ValueError("receipt decision does not match reconstructed decision")

    code = decision.get("reason_code")
    if code not in reason_codes():
        raise ValueError(f"unregistered reason_code: {code}")
    if receipt.get("authority_effect") is not False:
        raise ValueError("receipt authority_effect must remain false")

    if verifier_inputs.get("canonicalization_profile") != "stegverse.jcs.v1":
        raise ValueError("verifier input canonicalization profile mismatch")
    if verifier_inputs.get("reason_registry") != "reasons/registry.v1.json":
        raise ValueError("verifier input reason registry mismatch")

    assurance = manifest.get("achieved_assurance")
    if not isinstance(assurance, dict) or assurance.get("profile_ref") != "steggate.assurance-profile.v1":
        raise ValueError("achieved assurance is missing or unbound")
    missing_dimensions = sorted(ASSURANCE_DIMENSIONS - assurance.keys())
    if missing_dimensions:
        raise ValueError(f"achieved assurance dimensions missing: {missing_dimensions}")

    return {
        "status": "PASS",
        "pack_id": pack_result["pack_id"],
        "candidate_id": candidate_id,
        "decision": decision_value,
        "reason_code": code,
        "canonical_hashes": {
            "candidate": candidate_hash,
            "decision": decision_hash,
            "receipt": receipt_hash,
        },
        "achieved_assurance_profile": assurance["profile_ref"],
        "authority_effect": False,
        "limitations": [
            "content integrity does not prove truth of policy or authority assertions",
            "offline verification does not grant consequence execution authority",
            "external identity, signature, and trust-anchor claims remain limited to achieved assurance",
        ],
    }


def prepare_case(source_manifest: Path, decision_value: str, reason_code: str) -> Path:
    source_root = source_manifest.parent
    temp_root = Path(tempfile.mkdtemp(prefix="steggate-verifier-")) / "pack"
    shutil.copytree(source_root, temp_root)
    manifest_path = temp_root / source_manifest.name
    manifest = load(manifest_path)
    objects = object_index(manifest)

    decision_path = temp_root / objects["decision"]["path"]
    receipt_path = temp_root / objects["receipt"]["path"]
    decision = load(decision_path)
    receipt = load(receipt_path)
    decision["decision"] = decision_value
    decision["reason_code"] = reason_code
    receipt["decision"] = decision_value
    receipt["authority_effect"] = False
    write_canonical(decision_path, decision)
    write_canonical(receipt_path, receipt)
    objects["decision"]["sha256"] = raw_id(decision_path)
    objects["receipt"]["sha256"] = raw_id(receipt_path)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def mutate_case(manifest_path: Path, operation: str) -> None:
    manifest = load(manifest_path)
    objects = object_index(manifest)
    base = manifest_path.parent
    if operation == "receipt_decision_mismatch":
        path = base / objects["receipt"]["path"]
        value = load(path)
        value["decision"] = "DENY" if value.get("decision") != "DENY" else "ALLOW"
        write_canonical(path, value)
        objects["receipt"]["sha256"] = raw_id(path)
    elif operation == "candidate_content_without_manifest_update":
        path = base / objects["candidate"]["path"]
        path.write_bytes(path.read_bytes() + b" ")
        return
    elif operation == "unregistered_reason":
        path = base / objects["decision"]["path"]
        value = load(path)
        value["reason_code"] = "UNREGISTERED_TEST_REASON"
        write_canonical(path, value)
        objects["decision"]["sha256"] = raw_id(path)
    elif operation == "receipt_authority_effect_true":
        path = base / objects["receipt"]["path"]
        value = load(path)
        value["authority_effect"] = True
        write_canonical(path, value)
        objects["receipt"]["sha256"] = raw_id(path)
    else:
        raise ValueError(f"unknown tamper operation: {operation}")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def verify_legacy_fixture(path: Path) -> dict[str, Any]:
    payload = load(path)
    checked = 0
    for fixture in payload.get("fixtures", []):
        fixture_id = fixture.get("fixture_id", "")
        source = fixture.get("input", {})
        expected = fixture.get("expected", {})
        if "stegcore_decision" in source:
            actual = {"allow": "ALLOW", "deny": "DENY", "defer": "REVIEW"}[source["stegcore_decision"]]
            if actual != expected.get("steggate_decision"):
                raise ValueError(f"legacy mapping mismatch: {fixture_id}")
            if source["stegcore_decision"] == "defer" and expected.get("not") == actual:
                raise ValueError(f"defer incorrectly mapped to forbidden outcome: {fixture_id}")
        elif "legacy_decision" in source:
            actual = "FAIL_CLOSED" if source["legacy_decision"] == "FAIL-CLOSED" else source["legacy_decision"]
            if actual != expected.get("steggate_decision"):
                raise ValueError(f"legacy spelling mismatch: {fixture_id}")
        elif "admitted_candidate_hash" in source:
            same = source["admitted_candidate_hash"] == source["consequence_candidate_hash"]
            actual_decision = "ALLOW" if same else "DENY"
            if actual_decision != expected.get("decision"):
                raise ValueError(f"candidate binding mismatch: {fixture_id}")
            if not same and expected.get("reason_code") != "CANDIDATE_BINDING_MISMATCH":
                raise ValueError(f"candidate mismatch reason missing: {fixture_id}")
        else:
            raise ValueError(f"unsupported legacy fixture: {fixture_id}")
        checked += 1
    return {"status": "PASS", "fixtures": checked}


def run_cases(cases_path: Path) -> dict[str, Any]:
    cases = load(cases_path)
    if cases.get("schema_version") != "steggate.offline-verifier-cases.v1":
        raise ValueError("verifier cases schema mismatch")
    base_manifest = ROOT / cases["base_manifest"]
    results: list[dict[str, Any]] = []

    for case in cases.get("decision_cases", []):
        manifest_path = prepare_case(base_manifest, case["decision"], case["reason_code"])
        try:
            result = verify_semantics(manifest_path)
            results.append({"case_id": case["case_id"], "result": result["status"], "decision": result["decision"]})
        finally:
            shutil.rmtree(manifest_path.parent.parent, ignore_errors=True)

    for case in cases.get("tamper_cases", []):
        manifest_path = prepare_case(base_manifest, "ALLOW", "DECISION_REQUIRED")
        try:
            mutate_case(manifest_path, case["operation"])
            try:
                verify_semantics(manifest_path)
            except (ValueError, FileNotFoundError) as exc:
                results.append({"case_id": case["case_id"], "result": "REJECT", "reason": str(exc)})
            else:
                raise AssertionError(f"tamper case accepted: {case['case_id']}")
        finally:
            shutil.rmtree(manifest_path.parent.parent, ignore_errors=True)

    legacy = verify_legacy_fixture(ROOT / cases["legacy_fixture"])
    return {
        "status": "PASS",
        "cases": len(results),
        "decision_cases": len(cases.get("decision_cases", [])),
        "tamper_cases": len(cases.get("tamper_cases", [])),
        "legacy_fixtures": legacy["fixtures"],
        "results": results,
        "authority_effect": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, help="verify one evidence-pack manifest")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES, help="run fixture-backed verifier cases")
    args = parser.parse_args()
    result = verify_semantics(args.manifest) if args.manifest else run_cases(args.cases)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

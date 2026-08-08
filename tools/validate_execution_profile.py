#!/usr/bin/env python3
"""Validate the deterministic StegGate execution profile without duplicating StegCore runtime ownership."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles" / "execution-deterministic.v1.yaml"
SCHEMA = ROOT / "schemas" / "execution-request.v1.json"
FIXTURES = ROOT / "fixtures" / "execution" / "execution-profile-cases.json"
INVARIANTS = ROOT / "invariants" / "profile-execution.yaml"
CLAIMS = ROOT / "claims" / "execution-deterministic.yaml"
REASONS = ROOT / "reasons" / "registry.v1.json"
OBSERVATION = ROOT / "real-boundary" / "consequence-observation.json"


def load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"invalid JSON/YAML-subset file {path.relative_to(ROOT)}: {exc}")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate(case: dict[str, Any]) -> tuple[str, str | None]:
    if not case.get("candidate_binding_match"):
        return "DENY", "CANDIDATE_BINDING_MISMATCH"
    if not case.get("credential_binding_match"):
        return "DENY", "CREDENTIAL_BINDING_MISMATCH"
    if not case.get("action_exposed"):
        return "DENY", "CAPABILITY_ACTION_NOT_EXPOSED"
    if not case.get("parameters_within_bounds"):
        return "DENY", "PARAMETER_OUT_OF_BOUNDS"
    if not case.get("downstream_capability_narrows_or_equals_upstream"):
        return "DENY", "AUTHORITY_BROADENING"
    if not case.get("requires_governed_commit"):
        return "FAIL_CLOSED", "GOVERNED_COMMIT_REQUIRED"
    return "ALLOW", None


def main() -> int:
    profile = load(PROFILE)
    schema = load(SCHEMA)
    fixtures = load(FIXTURES)
    invariants = load(INVARIANTS)
    claims = load(CLAIMS)
    reasons = load(REASONS)
    observation = load(OBSERVATION)

    require(profile.get("profile_id") == "SG-EXECUTION-DETERMINISTIC-v1", "execution profile id mismatch")
    require(profile.get("consequence_class") == "execution", "execution consequence class mismatch")
    require(profile.get("authority_effect") is False, "execution profile authority_effect must remain false")
    require(profile.get("runtime_owner") == "StegVerse-Labs/StegCore@feat/commit-coherence-boundary:src/stegcore/commit_governance.py", "StegCore runtime owner reference mismatch")
    require(profile.get("request_schema") == "schemas/execution-request.v1.json", "execution schema reference mismatch")
    require(profile.get("capability_constraints", {}).get("downstream_may_only_narrow") is True, "capability narrowing not required")
    require(profile.get("capability_constraints", {}).get("requires_governed_commit") is True, "governed commit not required")

    require(schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", "execution schema draft mismatch")
    required = set(schema.get("required", []))
    for field in ("execution_id", "candidate_id", "candidate_hash", "credential_binding", "action", "capability_surface", "authority_ref", "profile_ref"):
        require(field in required, f"execution schema missing required field {field}")
    require(schema.get("properties", {}).get("profile_ref", {}).get("const") == "SG-EXECUTION-DETERMINISTIC-v1", "schema profile binding mismatch")
    require(schema.get("properties", {}).get("capability_surface", {}).get("properties", {}).get("requires_governed_commit", {}).get("const") is True, "schema must require governed commit")

    registered = {item.get("code") for item in reasons.get("reasons", [])}
    expected_reasons = {
        "CANDIDATE_BINDING_MISMATCH",
        "CREDENTIAL_BINDING_MISMATCH",
        "CAPABILITY_ACTION_NOT_EXPOSED",
        "PARAMETER_OUT_OF_BOUNDS",
        "AUTHORITY_BROADENING",
        "GOVERNED_COMMIT_REQUIRED",
    }
    require(expected_reasons <= registered, f"execution reasons missing: {sorted(expected_reasons - registered)}")

    cases = fixtures.get("fixtures", [])
    require(len(cases) == 7, "execution fixture count must be 7")
    results = []
    for case in cases:
        decision, reason = evaluate(case)
        expected = case.get("expected", {})
        require(decision == expected.get("decision"), f"fixture {case.get('fixture_id')} decision mismatch")
        require(reason == expected.get("reason_code"), f"fixture {case.get('fixture_id')} reason mismatch")
        results.append({"fixture_id": case.get("fixture_id"), "decision": decision, "reason_code": reason})

    invariant_ids = {item.get("invariant_id") for item in invariants.get("invariants", [])}
    require(invariant_ids == {f"SG-EXEC-{n:03d}" for n in range(1, 7)}, "execution invariant set mismatch")
    claim_ids = {item.get("claim_id") for item in claims.get("claims", [])}
    require(claim_ids == {f"SG-EXEC-{n:03d}" for n in range(1, 5)}, "execution claim set mismatch")
    require(claims.get("authority_effect") is False, "execution claims authority_effect must remain false")

    require(observation.get("task_id") == "STEGGATE-FIRST-BOUNDARY-001", "real-boundary observation task mismatch")
    require(observation.get("candidate_id") == "rb-ara-taskstate-001", "real-boundary candidate mismatch")
    require(observation.get("candidate_hash") == "sha256:a74ef1ce97953e6661975f68f4a7ae53c1483b4006076279191637800b4326f3", "real-boundary hash mismatch")
    require(observation.get("observed_value") == "COMPLETE", "real-boundary consequence not observed complete")
    require(observation.get("authority_effect") is False, "real-boundary observation authority_effect must remain false")

    print(json.dumps({
        "status": "PASS",
        "profile_id": profile["profile_id"],
        "fixtures": len(cases),
        "allows": sum(1 for item in results if item["decision"] == "ALLOW"),
        "denies": sum(1 for item in results if item["decision"] == "DENY"),
        "fail_closed": sum(1 for item in results if item["decision"] == "FAIL_CLOSED"),
        "invariants": len(invariant_ids),
        "claims": len(claim_ids),
        "exact_candidate_binding": True,
        "exact_credential_binding": True,
        "capability_narrowing": True,
        "governed_commit_required": True,
        "real_boundary_observed": True,
        "stegcore_runtime_owner_preserved": True,
        "authority_effect": False,
        "input_hashes": {
            "schema": sha256(SCHEMA),
            "profile": sha256(PROFILE),
            "fixtures": sha256(FIXTURES),
            "invariants": sha256(INVARIANTS),
            "claims": sha256(CLAIMS),
            "observation": sha256(OBSERVATION),
        },
        "results": results,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

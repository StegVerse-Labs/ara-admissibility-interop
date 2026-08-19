#!/usr/bin/env python3
"""Validate additive StegGate governed-transition protocol fixtures.

This validator is intentionally stdlib-only and does not implement StegCore runtime
semantics. It validates the interop/profile invariants owned by ara:
- gateway discovery completeness;
- monotonic authority narrowing across gate paths;
- unsupported major-version fail-closed posture;
- RFC 9396 authorization-details never standing alone as portable authority proof.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "protocol" / "governed-transition-cases.json"
DISCOVERY_SCHEMA = ROOT / "schemas" / "gateway-discovery.v1.json"
ENVELOPE_SCHEMA = ROOT / "schemas" / "governed-transition-envelope.v1.json"
AUTH_PROFILE = ROOT / "profiles" / "authority-rar-bound.v1.yaml"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_discovery(value: dict) -> bool:
    required = {
        "gateway_id",
        "protocol_versions",
        "decision_states",
        "canonicalization_profiles",
        "identity_profiles",
        "authority_profiles",
        "assurance_profiles",
        "trust_anchor_refs",
        "bindings",
    }
    if not required.issubset(value):
        return False
    return set(value["decision_states"]) == {"ALLOW", "DENY", "REVIEW", "FAIL_CLOSED"}


def monotonic_gate_path(gates: list[dict]) -> tuple[bool, str | None]:
    for gate in gates:
        upstream = set(gate.get("input_scope", []))
        effective = set(gate.get("effective_scope", []))
        if gate.get("broadened") is True or not effective.issubset(upstream):
            return False, "AUTHORITY_BROADENING"
    return True, None


def main() -> int:
    # Structural presence / parse checks for new protocol assets.
    discovery_schema = load(DISCOVERY_SCHEMA)
    envelope_schema = load(ENVELOPE_SCHEMA)
    authority_profile = load(AUTH_PROFILE)
    if discovery_schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise SystemExit("gateway discovery schema draft mismatch")
    if envelope_schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise SystemExit("governed transition envelope schema draft mismatch")
    if authority_profile.get("semantic_substrate") != "RFC 9396 authorization_details":
        raise SystemExit("authority profile must preserve RFC 9396 semantic substrate")
    if authority_profile.get("required_binding", {}).get("portable_authority_proof_required") is not True:
        raise SystemExit("RAR authority profile must require separately bound portable authority proof")
    if authority_profile.get("authority_effect") is not False:
        raise SystemExit("authority profile must remain authority_effect=false")

    fixtures = load(FIXTURES).get("fixtures", [])
    results = []
    for case in fixtures:
        fid = case["fixture_id"]
        inp = case["input"]
        expected = case["expected"]
        actual: dict[str, object]

        if fid == "protocol.allow.local_discovery":
            actual = {"valid": validate_discovery(inp)}
        elif fid in {
            "protocol.allow.authority_narrows_across_gates",
            "protocol.deny.authority_broadens_across_gates",
        }:
            valid, reason = monotonic_gate_path(inp["gate_path"])
            actual = {"valid": valid, "monotonic_authority": valid}
            if not valid:
                actual.update({"decision": "DENY", "reason_code": reason})
        elif fid == "protocol.fail_closed.unsupported_major_version":
            supported = set(inp.get("supported", []))
            valid = inp.get("protocol_version") in supported
            actual = {"valid": valid}
            if not valid:
                actual["decision"] = "FAIL_CLOSED"
        elif fid in {
            "protocol.fail_closed.rar_without_bound_authority_proof",
            "protocol.allow.rar_with_bound_authority_proof",
        }:
            valid = bool(
                inp.get("authorization_details_present")
                and inp.get("portable_authority_proof_present")
            )
            actual = {"valid": valid}
            if not valid:
                actual["decision"] = "FAIL_CLOSED"
        else:
            raise SystemExit(f"unknown protocol fixture {fid}")

        for key, expected_value in expected.items():
            if actual.get(key) != expected_value:
                raise SystemExit(
                    f"{fid}: {key} mismatch: {actual.get(key)!r} != {expected_value!r}"
                )
        results.append({"fixture_id": fid, "result": "PASS", **actual})

    print(json.dumps({
        "status": "PASS",
        "profile": "steggate.governed-transition-protocol.v1",
        "fixtures": len(results),
        "monotonic_authority_enforced": True,
        "rar_requires_bound_authority_proof": True,
        "unsupported_major_fails_closed": True,
        "discovery_profile_validated": True,
        "runtime_authority_effect": False,
        "results": results,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Validate achieved-assurance ordering and fail-closed overclaim behavior."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = json.loads((ROOT / "assurance" / "profile.v1.json").read_text(encoding="utf-8"))
FIXTURES = json.loads((ROOT / "fixtures" / "assurance" / "cases.json").read_text(encoding="utf-8"))

VERIFICATION = {value: index for index, value in enumerate(PROFILE["verification_order"])}
CAPABILITY = {value: index for index, value in enumerate(PROFILE["capability_order"])}
DIMENSIONS = tuple(PROFILE["dimensions"])


def evaluate(claimed: dict, observed: dict) -> tuple[str, str | None]:
    for dimension in DIMENSIONS:
        if claimed.get(dimension) not in VERIFICATION or observed.get(dimension) not in VERIFICATION:
            return "FAIL_CLOSED", "ASSURANCE_OVERCLAIMED"
        if VERIFICATION[claimed[dimension]] > VERIFICATION[observed[dimension]]:
            return "FAIL_CLOSED", "ASSURANCE_OVERCLAIMED"
    if claimed.get("capability_construction") not in CAPABILITY or observed.get("capability_construction") not in CAPABILITY:
        return "FAIL_CLOSED", "ASSURANCE_OVERCLAIMED"
    if CAPABILITY[claimed["capability_construction"]] > CAPABILITY[observed["capability_construction"]]:
        return "FAIL_CLOSED", "ASSURANCE_OVERCLAIMED"
    return "ALLOW", None


def main() -> int:
    if PROFILE.get("authority_effect") is not False:
        raise SystemExit("assurance profile must remain authority_effect=false")
    fixtures = FIXTURES.get("fixtures", [])
    if len(fixtures) < 4:
        raise SystemExit("insufficient assurance fixtures")
    seen: set[str] = set()
    passed = 0
    for fixture in fixtures:
        fid = fixture.get("fixture_id")
        if not fid or fid in seen:
            raise SystemExit(f"missing/duplicate assurance fixture id: {fid!r}")
        seen.add(fid)
        observed = evaluate(fixture["claimed"], fixture["observed"])
        expected = fixture["expected"]
        if observed != (expected["decision"], expected.get("reason_code")):
            raise SystemExit(f"{fid}: {observed!r} != {(expected['decision'], expected.get('reason_code'))!r}")
        passed += 1
    print(json.dumps({"status":"PASS","fixtures":passed,"authority_effect":False,"overclaim_reason":"ASSURANCE_OVERCLAIMED"}, sort_keys=True))
    return 0

if __name__ == "__main__":
    sys.exit(main())

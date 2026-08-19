#!/usr/bin/env python3
"""Validate L0-L3 achieved trust level semantics without authority expansion."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = json.loads((ROOT / "assurance" / "trust-levels.v1.json").read_text(encoding="utf-8"))
FIXTURES = json.loads((ROOT / "fixtures" / "assurance" / "trust-level-cases.json").read_text(encoding="utf-8"))
ORDER = {level: index for index, level in enumerate(PROFILE["ordering"])}


def achieved(inp: dict) -> str:
    crypto = inp.get("cryptographic_binding") is True
    domains = {d for d in inp.get("external_anchor_domains", []) if isinstance(d, str) and d}
    observed = inp.get("independent_observation") is True
    if crypto and observed and len(domains) >= 2:
        return "L3"
    if crypto and len(domains) >= 1:
        return "L2"
    if crypto:
        return "L1"
    return "L0"


def evaluate(inp: dict) -> tuple[str, str, str | None]:
    actual = achieved(inp)
    reported = inp.get("reported_level")
    if reported not in ORDER:
        return actual, "FAIL_CLOSED", "ASSURANCE_OVERCLAIMED"
    if ORDER[reported] > ORDER[actual]:
        return actual, "FAIL_CLOSED", "ASSURANCE_OVERCLAIMED"
    return actual, "ALLOW", None


def main() -> int:
    if PROFILE.get("authority_effect") is not False:
        raise SystemExit("trust-level profile must remain authority_effect=false")
    if PROFILE.get("ordering") != ["L0", "L1", "L2", "L3"]:
        raise SystemExit("unexpected trust-level ordering")
    levels = PROFILE.get("levels", {})
    if levels.get("L2", {}).get("independent_administrative_domain_required") is not True:
        raise SystemExit("L2 must require an independent administrative domain")
    if levels.get("L3", {}).get("independent_observation_required") is not True:
        raise SystemExit("L3 must require independent observation")

    fixtures = FIXTURES.get("fixtures", [])
    if len(fixtures) < 8:
        raise SystemExit("insufficient trust-level fixtures")
    results = []
    seen: set[str] = set()
    for fixture in fixtures:
        fid = fixture.get("fixture_id")
        if not fid or fid in seen:
            raise SystemExit(f"missing/duplicate trust fixture id: {fid!r}")
        seen.add(fid)
        actual_level, decision, reason = evaluate(fixture["input"])
        expected = fixture["expected"]
        actual = {"achieved_level": actual_level, "decision": decision, "reason_code": reason}
        if actual != expected:
            raise SystemExit(f"{fid}: {actual!r} != {expected!r}")
        results.append({"fixture_id": fid, **actual})

    print(json.dumps({
        "status": "PASS",
        "profile": "steggate.trust-levels.v1",
        "fixtures": len(results),
        "levels": ["L0", "L1", "L2", "L3"],
        "external_anchor_semantics": True,
        "independent_observation_semantics": True,
        "authority_effect": False,
        "results": results,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

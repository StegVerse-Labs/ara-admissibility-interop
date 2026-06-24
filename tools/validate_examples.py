#!/usr/bin/env python3
"""Validate example JSON files for the ARA admissibility interop repo."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_DIR = ROOT / "admissibility" / "examples"

EXPECTED = {
    "sample-commitment-candidate.json": [
        "schema_version",
        "candidate_id",
        "transition_id",
        "artifact_reference",
        "requested_action",
        "actor",
        "target",
        "scope",
        "claim_boundary",
        "policy_reference",
        "evidence_references",
        "execution_context",
        "validity_window",
        "recoverability_profile",
    ],
    "sample-standing-result-allow.json": ["schema_version", "result_id", "candidate_id", "decision", "standing_valid", "checks", "commit_time", "reasons"],
    "sample-standing-result-deny.json": ["schema_version", "result_id", "candidate_id", "decision", "standing_valid", "checks", "commit_time", "reasons"],
    "sample-standing-result-fail-closed.json": ["schema_version", "result_id", "candidate_id", "decision", "standing_valid", "checks", "commit_time", "reasons"],
}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def main() -> int:
    problems: list[str] = []

    for filename, required_fields in EXPECTED.items():
        path = EXAMPLE_DIR / filename
        if not path.is_file():
            problems.append(f"missing:{filename}")
            continue
        try:
            value = load_json(path)
        except Exception as exc:
            problems.append(f"invalid-json:{filename}:{exc}")
            continue
        for field in required_fields:
            if field not in value:
                problems.append(f"missing-field:{filename}:{field}")

    result = {
        "checked": sorted(EXPECTED),
        "problem_count": len(problems),
        "problems": problems,
        "result": "pass" if not problems else "fail",
    }
    print(json.dumps(result, indent=2))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())

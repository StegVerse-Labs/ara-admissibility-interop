#!/usr/bin/env python3
"""
Minimal ARA admissibility evaluator stub.

This file is intentionally small. It does not implement the full Standing Proof
Engine. It demonstrates how a commitment candidate can be read and reduced to
one of three standing outcomes: ALLOW, DENY, or FAIL-CLOSED.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = [
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
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("candidate must be a JSON object")
    return value


def result(candidate_id: str, decision: str, checks: dict[str, bool | None], reasons: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "result_id": f"standing-result-{candidate_id}",
        "candidate_id": candidate_id,
        "decision": decision,
        "standing_valid": decision == "ALLOW",
        "checks": checks,
        "commit_time": now_iso(),
        "reasons": reasons,
    }


def evaluate(candidate: dict[str, Any]) -> dict[str, Any]:
    candidate_id = str(candidate.get("candidate_id", "unknown-candidate"))
    missing = [field for field in REQUIRED_FIELDS if field not in candidate]

    if missing:
        return result(
            candidate_id,
            "FAIL-CLOSED",
            {
                "authority_valid": None,
                "policy_valid": None,
                "delegation_valid": None,
                "evidence_admissible": None,
                "scope_valid": None,
                "context_valid": None,
                "recoverability_valid": None,
            },
            [
                {
                    "code": "FAIL_CLOSED_REQUIRED_FIELD_MISSING",
                    "message": "One or more required commitment-candidate fields are missing.",
                    "field": ",".join(missing),
                }
            ],
        )

    requested_action = candidate.get("requested_action", {})
    action_type = requested_action.get("action_type") if isinstance(requested_action, dict) else None
    scope = candidate.get("scope", {})
    limitations = scope.get("limitations", []) if isinstance(scope, dict) else []
    non_claims = candidate.get("claim_boundary", {}).get("non_claims", [])

    if action_type in {"execute", "integrate", "rely-upon"}:
        return result(
            candidate_id,
            "DENY",
            {
                "authority_valid": False,
                "policy_valid": True,
                "delegation_valid": False,
                "evidence_admissible": True,
                "scope_valid": False,
                "context_valid": True,
                "recoverability_valid": True,
            },
            [
                {
                    "code": "DENY_EXECUTION_SCOPE_NOT_SUPPORTED_BY_STUB",
                    "message": "This evaluator stub only supports citation-style examples. Execution, integration, or reliance requires a stronger evaluator.",
                    "field": "requested_action.action_type",
                }
            ],
        )

    has_boundary = bool(limitations) and bool(non_claims)
    if not has_boundary:
        return result(
            candidate_id,
            "FAIL-CLOSED",
            {
                "authority_valid": None,
                "policy_valid": True,
                "delegation_valid": None,
                "evidence_admissible": None,
                "scope_valid": False,
                "context_valid": True,
                "recoverability_valid": True,
            },
            [
                {
                    "code": "FAIL_CLOSED_CLAIM_BOUNDARY_INCOMPLETE",
                    "message": "Citation-style candidates require explicit limitations and non-claims.",
                    "field": "claim_boundary",
                }
            ],
        )

    return result(
        candidate_id,
        "ALLOW",
        {
            "authority_valid": True,
            "policy_valid": True,
            "delegation_valid": True,
            "evidence_admissible": True,
            "scope_valid": True,
            "context_valid": True,
            "recoverability_valid": True,
        },
        [
            {
                "code": "ALLOW_CITATION_STYLE_CANDIDATE",
                "message": "The candidate includes explicit scope limitations and non-claims, and requests no execution authority.",
            }
        ],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate a commitment candidate with a minimal admissibility stub.")
    parser.add_argument("candidate", type=Path, help="Path to a commitment-candidate JSON file")
    args = parser.parse_args()

    candidate = load_json(args.candidate)
    print(json.dumps(evaluate(candidate), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

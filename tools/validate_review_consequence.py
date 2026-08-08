#!/usr/bin/env python3
"""Prove bounded StegGate REVIEW consequence semantics from fixture cases.

This validator models permission to reach a consequence boundary; it does not execute
any real consequence and grants no authority. REVIEW is never direct admission. A
REVIEW candidate can become consequence-permitted only through a distinct ALLOW
admission transition with independently verified authority and exact candidate binding.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "fixtures" / "consequence" / "review-transition-cases.json"
ALLOWED_INITIAL = {"ALLOW", "DENY", "REVIEW", "FAIL_CLOSED"}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("fixture root must be an object")
    return value


def evaluate(case: dict[str, Any]) -> tuple[bool, str]:
    initial = case.get("initial_decision")
    if initial not in ALLOWED_INITIAL:
        raise ValueError(f"unsupported initial decision: {initial}")

    if initial == "ALLOW":
        return True, "INITIAL_ALLOW_ADMISSION"
    if initial == "DENY":
        return False, "DENY_NOT_ADMISSION"
    if initial == "FAIL_CLOSED":
        return False, "FAIL_CLOSED_NOT_ADMISSION"

    # REVIEW is explicitly not admission. Only a separate transition can admit it.
    transition = case.get("admission_transition")
    if transition is None:
        return False, "REVIEW_REQUIRES_SEPARATE_ADMISSION"
    if not isinstance(transition, dict):
        raise ValueError("admission_transition must be object or null")
    if not transition.get("transition_id"):
        return False, "SEPARATE_ADMISSION_TRANSITION_MISSING"
    if transition.get("decision") != "ALLOW":
        return False, "SEPARATE_ADMISSION_NOT_ALLOW"
    if transition.get("authority_verified") is not True:
        return False, "SEPARATE_ADMISSION_AUTHORITY_UNVERIFIED"
    if (
        transition.get("candidate_id") != case.get("candidate_id")
        or transition.get("candidate_hash") != case.get("candidate_hash")
    ):
        return False, "CANDIDATE_BINDING_MISMATCH"
    return True, "SEPARATE_ADMISSION_ESTABLISHED"


def main() -> int:
    payload = load(CASES)
    if payload.get("schema_version") != "steggate.review-consequence-cases.v1":
        raise ValueError("fixture schema mismatch")
    if payload.get("authority_effect") is not False:
        raise ValueError("fixture authority_effect must remain false")

    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("fixture cases missing")

    results: list[dict[str, Any]] = []
    review_cases = 0
    direct_review_refusals = 0
    separate_admission_successes = 0
    for case in cases:
        permitted, reason = evaluate(case)
        expected_permitted = case.get("expect_consequence_permitted")
        expected_reason = case.get("expect_reason")
        if permitted is not expected_permitted or reason != expected_reason:
            raise AssertionError(
                f"{case.get('case_id')}: observed {(permitted, reason)} != expected "
                f"{(expected_permitted, expected_reason)}"
            )
        if case.get("initial_decision") == "REVIEW":
            review_cases += 1
            if case.get("admission_transition") is None and not permitted:
                direct_review_refusals += 1
            if permitted and reason == "SEPARATE_ADMISSION_ESTABLISHED":
                separate_admission_successes += 1
        results.append(
            {
                "case_id": case.get("case_id"),
                "consequence_permitted": permitted,
                "reason": reason,
            }
        )

    if direct_review_refusals < 1:
        raise AssertionError("no direct REVIEW refusal was proven")
    if separate_admission_successes != 1:
        raise AssertionError("expected exactly one separately authorized REVIEW admission proof")

    print(
        json.dumps(
            {
                "status": "PASS",
                "cases": len(results),
                "review_cases": review_cases,
                "direct_review_refusals": direct_review_refusals,
                "separate_admission_successes": separate_admission_successes,
                "review_is_admission": False,
                "authority_effect": False,
                "results": results,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

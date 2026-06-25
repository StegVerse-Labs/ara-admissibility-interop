#!/usr/bin/env python3
"""Check evaluator output against expected ALLOW, DENY, and FAIL-CLOSED fixtures."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = ROOT / "admissibility" / "evaluator_stub.py"
CASES = [
    {
        "candidate": ROOT / "admissibility" / "examples" / "sample-commitment-candidate.json",
        "expected": ROOT / "admissibility" / "examples" / "expected-evaluator-result.json",
    },
    {
        "candidate": ROOT / "admissibility" / "examples" / "deny-execution-candidate.json",
        "expected": ROOT / "admissibility" / "examples" / "expected-evaluator-result-deny.json",
    },
    {
        "candidate": ROOT / "admissibility" / "examples" / "fail-closed-incomplete-boundary-candidate.json",
        "expected": ROOT / "admissibility" / "examples" / "expected-evaluator-result-fail-closed.json",
    },
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def load_evaluator():
    spec = importlib.util.spec_from_file_location("evaluator_stub", EVALUATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load evaluator stub")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_case(evaluator: Any, candidate_path: Path, expected_path: Path) -> list[str]:
    candidate = load_json(candidate_path)
    expected = load_json(expected_path)
    actual = evaluator.evaluate(candidate)
    problems: list[str] = []

    if actual.get("decision") != expected.get("decision"):
        problems.append("decision")
    if actual.get("standing_valid") != expected.get("standing_valid"):
        problems.append("standing_valid")

    actual_checks = actual.get("checks", {})
    for key, value in expected.get("required_checks", {}).items():
        if actual_checks.get(key) != value:
            problems.append(f"checks.{key}")

    reason_codes = {reason.get("code") for reason in actual.get("reasons", []) if isinstance(reason, dict)}
    if expected.get("required_reason_code") not in reason_codes:
        problems.append("required_reason_code")

    return [f"{candidate_path.relative_to(ROOT)}:{problem}" for problem in problems]


def main() -> int:
    evaluator = load_evaluator()
    problems: list[str] = []
    checked: list[str] = []

    for case in CASES:
        candidate_path = case["candidate"]
        expected_path = case["expected"]
        checked.append(str(candidate_path.relative_to(ROOT)))
        problems.extend(check_case(evaluator, candidate_path, expected_path))

    result = {
        "checked": checked,
        "problem_count": len(problems),
        "problems": problems,
        "result": "pass" if not problems else "fail",
    }
    print(json.dumps(result, indent=2))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())

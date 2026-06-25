#!/usr/bin/env python3
"""Check evaluator output against the expected fixture."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "admissibility" / "examples" / "sample-commitment-candidate.json"
EXPECTED = ROOT / "admissibility" / "examples" / "expected-evaluator-result.json"
EVALUATOR = ROOT / "admissibility" / "evaluator_stub.py"


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


def main() -> int:
    evaluator = load_evaluator()
    candidate = load_json(CANDIDATE)
    expected = load_json(EXPECTED)
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

    result = {
        "fixture": str(EXPECTED.relative_to(ROOT)),
        "candidate": str(CANDIDATE.relative_to(ROOT)),
        "problem_count": len(problems),
        "problems": problems,
        "result": "pass" if not problems else "fail",
    }
    print(json.dumps(result, indent=2))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())

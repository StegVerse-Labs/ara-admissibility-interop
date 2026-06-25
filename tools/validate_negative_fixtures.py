#!/usr/bin/env python3
"""Verify invalid fixtures are rejected by the schema-subset validator."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate_by_schema_subset.py"
CASES = [
    {
        "schema": ROOT / "admissibility" / "commitment-candidate.schema.json",
        "fixture": ROOT / "admissibility" / "examples" / "invalid-missing-claim-boundary.json",
        "expected_problem_prefix": "required:",
    },
    {
        "schema": ROOT / "admissibility" / "standing-result.schema.json",
        "fixture": ROOT / "admissibility" / "examples" / "invalid-standing-result-decision.json",
        "expected_problem_prefix": "enum:",
    },
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_by_schema_subset", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load schema-subset validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    validator = load_validator()
    problems: list[str] = []
    checked: list[str] = []

    for case in CASES:
        schema = load_json(case["schema"])
        fixture = load_json(case["fixture"])
        fixture_name = str(case["fixture"].relative_to(ROOT))
        checked.append(fixture_name)
        found = validator.validate(schema, fixture, fixture_name)
        prefix = case["expected_problem_prefix"]
        if not any(problem.startswith(prefix) for problem in found):
            problems.append(f"not-rejected-as-expected:{fixture_name}:{prefix}")

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

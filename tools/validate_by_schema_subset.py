#!/usr/bin/env python3
"""Validate repository examples against a supported JSON Schema subset.

This is dependency-free by design. It intentionally supports only the schema
features used by the repository examples: required fields, object properties,
arrays, strings, booleans, nulls, const, and enum.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
COMMITMENT_SCHEMA = ROOT / "admissibility" / "commitment-candidate.schema.json"
STANDING_SCHEMA = ROOT / "admissibility" / "standing-result.schema.json"
EXAMPLES = ROOT / "admissibility" / "examples"

PAIRS = [
    (COMMITMENT_SCHEMA, EXAMPLES / "sample-commitment-candidate.json"),
    (COMMITMENT_SCHEMA, EXAMPLES / "deny-execution-candidate.json"),
    (COMMITMENT_SCHEMA, EXAMPLES / "fail-closed-incomplete-boundary-candidate.json"),
    (STANDING_SCHEMA, EXAMPLES / "sample-standing-result-allow.json"),
    (STANDING_SCHEMA, EXAMPLES / "sample-standing-result-deny.json"),
    (STANDING_SCHEMA, EXAMPLES / "sample-standing-result-fail-closed.json"),
]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def type_matches(expected: Any, value: Any) -> bool:
    expected_types = expected if isinstance(expected, list) else [expected]
    for expected_type in expected_types:
        if expected_type == "object" and isinstance(value, dict):
            return True
        if expected_type == "array" and isinstance(value, list):
            return True
        if expected_type == "string" and isinstance(value, str):
            return True
        if expected_type == "boolean" and isinstance(value, bool):
            return True
        if expected_type == "null" and value is None:
            return True
    return False


def validate(schema: dict[str, Any], value: Any, path: str) -> list[str]:
    problems: list[str] = []

    if "type" in schema and not type_matches(schema["type"], value):
        return [f"type:{path}"]

    if "const" in schema and value != schema["const"]:
        problems.append(f"const:{path}")

    if "enum" in schema and value not in schema["enum"]:
        problems.append(f"enum:{path}")

    if isinstance(value, dict):
        for field in schema.get("required", []):
            if field not in value:
                problems.append(f"required:{path}.{field}")
        properties = schema.get("properties", {})
        if isinstance(properties, dict):
            for field, child_schema in properties.items():
                if field in value and isinstance(child_schema, dict):
                    problems.extend(validate(child_schema, value[field], f"{path}.{field}"))

    if isinstance(value, list):
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                problems.extend(validate(item_schema, item, f"{path}[{index}]"))

    return problems


def main() -> int:
    problems: list[str] = []
    checked: list[str] = []

    for schema_path, example_path in PAIRS:
        checked.append(str(example_path.relative_to(ROOT)))
        schema = load(schema_path)
        example = load(example_path)
        if not isinstance(schema, dict):
            problems.append(f"schema-not-object:{schema_path.relative_to(ROOT)}")
            continue
        problems.extend(validate(schema, example, str(example_path.relative_to(ROOT))))

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

#!/usr/bin/env python3
"""Validate repository JSON schema files without external dependencies."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = [
    ROOT / "admissibility" / "commitment-candidate.schema.json",
    ROOT / "admissibility" / "standing-result.schema.json",
]
REQUIRED_TOP_LEVEL = ["$schema", "title", "type", "properties", "required"]


def main() -> int:
    problems: list[str] = []

    for path in SCHEMAS:
        if not path.is_file():
            problems.append(f"missing:{path.relative_to(ROOT)}")
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            problems.append(f"invalid-json:{path.relative_to(ROOT)}:{exc}")
            continue
        if not isinstance(value, dict):
            problems.append(f"not-object:{path.relative_to(ROOT)}")
            continue
        for field in REQUIRED_TOP_LEVEL:
            if field not in value:
                problems.append(f"missing-top-level:{path.relative_to(ROOT)}:{field}")
        if value.get("type") != "object":
            problems.append(f"schema-type-not-object:{path.relative_to(ROOT)}")
        if not isinstance(value.get("properties"), dict):
            problems.append(f"properties-not-object:{path.relative_to(ROOT)}")
        if not isinstance(value.get("required"), list):
            problems.append(f"required-not-list:{path.relative_to(ROOT)}")

    result = {
        "checked": [str(path.relative_to(ROOT)) for path in SCHEMAS],
        "problem_count": len(problems),
        "problems": problems,
        "result": "pass" if not problems else "fail",
    }
    print(json.dumps(result, indent=2))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())

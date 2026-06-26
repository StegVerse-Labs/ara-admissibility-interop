#!/usr/bin/env python3
"""Optionally validate examples with the jsonschema package.

This tool preserves the repository's dependency-free default posture. If the
`jsonschema` package is not installed, the tool reports a clean skip. If it is
installed, the tool performs stricter schema validation and fails on violations.
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


def main() -> int:
    try:
        import jsonschema  # type: ignore[import-not-found]
    except ImportError:
        print(json.dumps({
            "result": "skip",
            "reason": "jsonschema package is not installed",
            "checked": [],
            "problem_count": 0,
            "problems": []
        }, indent=2))
        return 0

    problems: list[str] = []
    checked: list[str] = []

    for schema_path, example_path in PAIRS:
        checked.append(str(example_path.relative_to(ROOT)))
        schema = load(schema_path)
        example = load(example_path)
        try:
            jsonschema.validate(instance=example, schema=schema)
        except jsonschema.ValidationError as exc:
            problems.append(f"{example_path.relative_to(ROOT)}:{exc.message}")

    result = {
        "result": "pass" if not problems else "fail",
        "checked": checked,
        "problem_count": len(problems),
        "problems": problems,
    }
    print(json.dumps(result, indent=2))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())

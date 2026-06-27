#!/usr/bin/env python3
"""Check repository dependency policy invariants."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "docs" / "dependency-policy.md"
MANIFEST = ROOT / "release-manifest.json"

REQUIRED_POLICY_PHRASES = [
    "dependency-free validation",
    "Required dependency",
    "Optional dependency",
    "Prohibited dependency",
    "jsonschema",
    "skip",
    "exit code `0`",
]


def main() -> int:
    problems: list[str] = []

    if not POLICY.is_file():
        problems.append("missing:docs/dependency-policy.md")
        policy_text = ""
    else:
        policy_text = POLICY.read_text(encoding="utf-8")
        for phrase in REQUIRED_POLICY_PHRASES:
            if phrase not in policy_text:
                problems.append(f"missing-policy-phrase:{phrase}")

    if not MANIFEST.is_file():
        problems.append("missing:release-manifest.json")
    else:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        dependency_policy = manifest.get("dependency_policy", {})
        if dependency_policy.get("baseline") != "dependency-free":
            problems.append("manifest-baseline-not-dependency-free")
        if dependency_policy.get("required_dependencies") != []:
            problems.append("manifest-required-dependencies-not-empty")
        optional_dependencies = dependency_policy.get("optional_dependencies", [])
        if not any(item.get("name") == "jsonschema" for item in optional_dependencies if isinstance(item, dict)):
            problems.append("manifest-jsonschema-not-optional")

    result = {
        "checked": ["docs/dependency-policy.md", "release-manifest.json"],
        "problem_count": len(problems),
        "problems": problems,
        "result": "pass" if not problems else "fail",
    }
    print(json.dumps(result, indent=2))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Assess repository build completeness for ARA admissibility interop."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md",
    "LICENSE",
    "admissibility/README.md",
    "admissibility/non-claims.md",
    "admissibility/glossary.md",
    "admissibility/ara-to-standing-map.md",
    "admissibility/commitment-candidate.schema.json",
    "admissibility/standing-result.schema.json",
    "admissibility/examples/sample-commitment-candidate.json",
    "admissibility/examples/sample-standing-result-allow.json",
    "admissibility/examples/sample-standing-result-deny.json",
    "admissibility/examples/sample-standing-result-fail-closed.json",
    "admissibility/evaluator_stub.py",
    "admissibility/evaluator-usage.md",
    "management/goal-activation.md",
    "tools/assess_repo.py",
]


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    present = len(REQUIRED) - len(missing)
    percent = round((present / len(REQUIRED)) * 100, 2)
    status = {
        "repo": "StegVerse-Labs/ara-admissibility-interop",
        "assessment_version": "0.1.0",
        "present": present,
        "required": len(REQUIRED),
        "percent": percent,
        "missing": missing,
        "result": "pass" if not missing else "incomplete",
    }
    print(json.dumps(status, indent=2))
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())

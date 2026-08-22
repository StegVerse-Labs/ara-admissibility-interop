#!/usr/bin/env python3
"""Fail closed when ARA workflow count exceeds its baseline without explicit exceptions."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "management" / "workflow-governance.json"
WORKFLOW_DIR = ROOT / ".github" / "workflows"


def main() -> int:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    failures: list[str] = []

    baseline_max = policy.get("baseline_max_workflows")
    baseline = policy.get("baseline_workflows", [])
    exceptions = policy.get("discrete_exceptions", [])
    invariants = policy.get("invariants", {})

    if not isinstance(baseline_max, int) or baseline_max < 0:
        failures.append("invalid-baseline-max")
        baseline_max = 0
    if len(baseline) > baseline_max:
        failures.append("baseline-exceeds-max")

    declared_paths: list[str] = []
    for item in baseline:
        path = item.get("path")
        if not path:
            failures.append("baseline-missing-path")
            continue
        declared_paths.append(path)
        if item.get("activation_authoritative") is not True:
            failures.append(f"baseline-not-activation-authoritative:{path}")

    exception_ids: set[str] = set()
    for item in exceptions:
        exception_id = item.get("exception_id")
        path = item.get("path")
        reason = item.get("reason")
        if not exception_id:
            failures.append(f"exception-missing-id:{path or 'unknown'}")
        elif exception_id in exception_ids:
            failures.append(f"duplicate-exception-id:{exception_id}")
        else:
            exception_ids.add(exception_id)
        if not path:
            failures.append(f"exception-missing-path:{exception_id or 'unknown'}")
            continue
        declared_paths.append(path)
        if not isinstance(reason, str) or not reason.strip():
            failures.append(f"exception-missing-reason:{path}")
        if item.get("activation_authoritative") is not False:
            failures.append(f"exception-grants-activation-authority:{path}")
        if item.get("release_authority") is not False:
            failures.append(f"exception-grants-release-authority:{path}")
        if item.get("may_create_additional_workflows") is not False:
            failures.append(f"exception-may-create-workflows:{path}")

    if len(set(declared_paths)) != len(declared_paths):
        failures.append("duplicate-declared-workflow-path")

    actual_paths = sorted(
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in WORKFLOW_DIR.iterdir()
        if path.is_file() and path.suffix in {".yml", ".yaml"}
    )
    declared_sorted = sorted(declared_paths)

    undeclared = sorted(set(actual_paths) - set(declared_sorted))
    missing = sorted(set(declared_sorted) - set(actual_paths))
    for path in undeclared:
        failures.append(f"undeclared-workflow:{path}")
    for path in missing:
        failures.append(f"declared-workflow-missing:{path}")

    expected_count = invariants.get("workflow_count_expected")
    if expected_count != len(actual_paths):
        failures.append(
            f"workflow-count-mismatch:expected={expected_count}:actual={len(actual_paths)}"
        )

    result = {
        "result": "pass" if not failures else "fail",
        "baseline_max_workflows": baseline_max,
        "baseline_workflow_count": len(baseline),
        "discrete_exception_count": len(exceptions),
        "actual_workflow_count": len(actual_paths),
        "actual_workflows": actual_paths,
        "undeclared_workflows": undeclared,
        "missing_declared_workflows": missing,
        "problems": failures,
    }
    print(json.dumps(result, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Generate a human-readable validation report from repo self-checks."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATUS_TOOL = ROOT / "tools" / "generate_status.py"
REPORT = ROOT / "status" / "validation-report.md"


def load_status_tool():
    spec = importlib.util.spec_from_file_location("generate_status", STATUS_TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load status generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_status() -> dict[str, Any]:
    status_path = ROOT / "status" / "generated-status.json"
    value = json.loads(status_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("generated status must be a JSON object")
    return value


def render(status: dict[str, Any]) -> str:
    lines = [
        "# Validation Report",
        "",
        f"Repository: `{status.get('repo', 'unknown')}`",
        "",
        f"State: `{status.get('state', 'unknown')}`",
        f"Goal activation: `{status.get('goal_activation_percent', 'unknown')}%`",
        f"Full build: `{status.get('full_build_percent', 'unknown')}%`",
        f"Handoff ready: `{status.get('handoff_ready', False)}`",
        "",
        "## Checks",
        "",
        "| Check | Result | Problems |",
        "| --- | --- | ---: |",
    ]

    for check in status.get("checks", []):
        if not isinstance(check, dict):
            continue
        command = check.get("command", "unknown")
        passed = "pass" if check.get("passed") else "fail"
        stdout_json = check.get("stdout_json") if isinstance(check.get("stdout_json"), dict) else {}
        problems = stdout_json.get("problem_count", 0)
        lines.append(f"| `{command}` | `{passed}` | {problems} |")

    remaining = status.get("remaining", [])
    if remaining:
        lines.extend(["", "## Remaining", ""])
        for item in remaining:
            lines.append(f"- {item}")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    status_tool = load_status_tool()
    status_code = status_tool.main()
    status = read_status()
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(render(status), encoding="utf-8")
    print(str(REPORT.relative_to(ROOT)))
    return status_code


if __name__ == "__main__":
    raise SystemExit(main())

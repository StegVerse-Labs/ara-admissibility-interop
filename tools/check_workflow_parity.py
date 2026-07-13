#!/usr/bin/env python3
"""Verify canonical workflows and iOS-safe mirrors remain byte-for-byte aligned."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    (ROOT / ".github/workflows/repo-check.yml", ROOT / "iosnoperiod/github/workflows/repo-check.yml"),
    (ROOT / ".github/workflows/docs-pages.yml", ROOT / "iosnoperiod/github/workflows/docs-pages.yml"),
    (
        ROOT / ".github/workflows/deployment-notification.yml",
        ROOT / "iosnoperiod/github/workflows/deployment-notification.yml",
    ),
    (
        ROOT / ".github/workflows/deployment-mailbox-monitor.yml",
        ROOT / "iosnoperiod/github/workflows/deployment-mailbox-monitor.yml",
    ),
]


def main() -> int:
    failures = []
    for canonical, mirror in PAIRS:
        if not canonical.is_file():
            failures.append(f"missing canonical workflow: {canonical.relative_to(ROOT)}")
            continue
        if not mirror.is_file():
            failures.append(f"missing iOS-safe mirror: {mirror.relative_to(ROOT)}")
            continue
        if canonical.read_bytes() != mirror.read_bytes():
            failures.append(
                f"workflow mismatch: {canonical.relative_to(ROOT)} != {mirror.relative_to(ROOT)}"
            )
        else:
            print(f"PARITY=PASS {canonical.relative_to(ROOT)}")

    if failures:
        print("WORKFLOW_PARITY=FAIL")
        for failure in failures:
            print(f"reason={failure}")
        return 1

    print("WORKFLOW_PARITY=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

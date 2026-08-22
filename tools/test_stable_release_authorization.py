#!/usr/bin/env python3
"""Regression tests for explicit stable-release authorization application."""

from __future__ import annotations

import copy

from apply_stable_release_authorization import apply, validate


def sample_manifest() -> dict:
    return {
        "repository": "StegVerse-Labs/ara-admissibility-interop",
        "candidate": "0.2.0-release-candidate",
        "release_gate": {
            "repo_check_workflow_verified": False,
            "pages_workflow_verified": True,
            "https_deployment_url_verified": True,
            "built_entrypoint_verified": True,
            "live_root_page_verified": True,
            "deployed_publication_receipt_verified": True,
            "deployed_evidence_bundle_verified": True,
            "stable_release_authorized": False,
        },
    }


def sample_authorization() -> dict:
    return {
        "schema": "stegverse.stable-release-authorization/v1",
        "repository": "StegVerse-Labs/ara-admissibility-interop",
        "candidate": "0.2.0-release-candidate",
        "authorized": True,
        "authorization_scope": "stable-tag-and-formal-release-after-evidence-gates",
        "authorization_record": {
            "type": "explicit-maintainer-instruction",
            "issue": 121,
            "issue_comment_id": 5383053369,
        },
        "effective_when": ["repo_check_workflow_verified", "pages_workflow_verified"],
    }


def main() -> int:
    failures: list[str] = []
    manifest = sample_manifest()
    authorization = sample_authorization()

    if validate(manifest, authorization):
        failures.append("valid-authorization-rejected")

    proposed = apply(manifest)
    if proposed["release_gate"].get("stable_release_authorized") is not True:
        failures.append("authorization-not-applied")

    before = manifest["release_gate"]
    after = proposed["release_gate"]
    for key, value in before.items():
        if key == "stable_release_authorized":
            continue
        if after.get(key) != value:
            failures.append(f"non-authorization-gate-changed:{key}")

    if manifest["release_gate"]["stable_release_authorized"] is not False:
        failures.append("input-manifest-mutated")

    cases = {
        "repository-mismatch": ("repository", "other/repo"),
        "candidate-mismatch": ("candidate", "9.9.9"),
        "authorization-not-true": ("authorized", False),
        "scope-mismatch": ("authorization_scope", "unbounded"),
    }
    for label, (key, value) in cases.items():
        bad = copy.deepcopy(authorization)
        bad[key] = value
        if not validate(manifest, bad):
            failures.append(f"{label}-not-rejected")

    missing_record = copy.deepcopy(authorization)
    missing_record.pop("authorization_record")
    if not validate(manifest, missing_record):
        failures.append("missing-record-not-rejected")

    missing_effective = copy.deepcopy(authorization)
    missing_effective["effective_when"] = []
    if not validate(manifest, missing_effective):
        failures.append("missing-effective-when-not-rejected")

    print("stable release authorization tests:", "PASS" if not failures else "FAIL")
    for failure in failures:
        print(f"- {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

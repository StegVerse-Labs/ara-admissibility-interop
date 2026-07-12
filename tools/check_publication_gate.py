#!/usr/bin/env python3
"""Validate the governed documentation publication boundary.

Dependency-free by design. The gate fails closed when the publication manifest
is missing, malformed, internally inconsistent, or points to a missing publish
root.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "publication-manifest.json"
REQUIRED_FIELDS = {
    "schema_version",
    "artifact_class",
    "publication_status",
    "canonical_status",
    "independent_review_status",
    "clinical_status",
    "regulatory_status",
    "reliance_posture",
    "publish_target",
    "publish_root",
    "allowed_publication_statuses",
    "required_non_claims",
    "gate_policy",
}


def fail(message: str) -> int:
    print(f"PUBLICATION_GATE=FAIL-CLOSED\nreason={message}")
    return 1


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"publication manifest is missing: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"publication manifest cannot be read: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("publication manifest must be a JSON object")
    return data


def validate(data: dict[str, Any], root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_FIELDS - data.keys())
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")
        return errors

    allowed = data.get("allowed_publication_statuses")
    if not isinstance(allowed, list) or not allowed:
        errors.append("allowed_publication_statuses must be a non-empty list")
    elif data.get("publication_status") not in allowed:
        errors.append("publication_status is not allowed by this manifest")

    publish_root = data.get("publish_root")
    if not isinstance(publish_root, str) or not publish_root.strip():
        errors.append("publish_root must be a non-empty relative path")
    else:
        repository_root = root.resolve()
        root_path = (repository_root / publish_root).resolve()
        try:
            root_path.relative_to(repository_root)
        except ValueError:
            errors.append("publish_root escapes repository root")
        else:
            if not root_path.is_dir():
                errors.append(f"publish_root does not exist: {publish_root}")
            elif not (root_path / "index.md").is_file() and not (root_path / "index.html").is_file():
                errors.append("publish_root has no index.md or index.html")

    non_claims = data.get("required_non_claims")
    if not isinstance(non_claims, list) or not non_claims or not all(
        isinstance(x, str) and x.strip() for x in non_claims
    ):
        errors.append("required_non_claims must be a non-empty string list")

    policy = data.get("gate_policy")
    if not isinstance(policy, dict):
        errors.append("gate_policy must be an object")
        return errors

    if (
        policy.get("block_canonical_without_independent_review", True)
        and data.get("canonical_status") == "authorized"
        and data.get("independent_review_status") != "complete"
    ):
        errors.append("canonical publication requires complete independent review")

    if (
        policy.get("block_clinical_claims_without_validation", True)
        and data.get("clinical_status") == "validated"
        and data.get("regulatory_status") == "not_authorized"
        and data.get("reliance_posture") not in {"research_and_review_only", "non_clinical"}
    ):
        errors.append("clinical reliance is inconsistent with regulatory status")

    if data.get("publication_status") == "canonical" and data.get("canonical_status") != "authorized":
        errors.append("publication_status canonical requires canonical_status authorized")

    if data.get("publish_target") != "github_pages":
        errors.append("this workflow currently supports publish_target github_pages only")

    return errors


def main() -> int:
    try:
        manifest = load_manifest()
    except ValueError as exc:
        return fail(str(exc))

    errors = validate(manifest)
    if errors:
        return fail("; ".join(errors))

    print("PUBLICATION_GATE=ALLOW")
    print(f"publication_status={manifest['publication_status']}")
    print(f"canonical_status={manifest['canonical_status']}")
    print(f"reliance_posture={manifest['reliance_posture']}")
    print(f"publish_root={manifest['publish_root']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

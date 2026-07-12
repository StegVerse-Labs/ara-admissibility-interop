#!/usr/bin/env python3
"""Generate human- and machine-readable governed publication status."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from check_publication_gate import ROOT, load_manifest, validate

JSON_OUTPUT = ROOT / "status" / "publication-status.json"
DOC_OUTPUT = ROOT / "docs" / "publication-status.md"


def main() -> int:
    manifest = load_manifest()
    errors = validate(manifest)
    gate_result = "ALLOW" if not errors else "FAIL-CLOSED"
    generated_at = datetime.now(timezone.utc).isoformat()

    status = {
        "schema_version": "1.0.0",
        "status_type": "governed-publication-status",
        "generated_at": generated_at,
        "repository": os.getenv("GITHUB_REPOSITORY", "StegVerse-Labs/ara-admissibility-interop"),
        "commit_sha": os.getenv("GITHUB_SHA", "local"),
        "publication_status": manifest.get("publication_status", "unknown"),
        "canonical_status": manifest.get("canonical_status", "unknown"),
        "independent_review_status": manifest.get("independent_review_status", "unknown"),
        "clinical_status": manifest.get("clinical_status", "unknown"),
        "regulatory_status": manifest.get("regulatory_status", "unknown"),
        "reliance_posture": manifest.get("reliance_posture", "unknown"),
        "publish_target": manifest.get("publish_target", "unknown"),
        "publish_root": manifest.get("publish_root", "unknown"),
        "gate_result": gate_result,
        "gate_errors": errors,
        "deployment_url": os.getenv("PAGES_DEPLOYMENT_URL", "pending"),
    }

    JSON_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUTPUT.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    error_lines = "\n".join(f"- {error}" for error in errors) if errors else "- None"
    markdown = f"""# Publication status

This page is generated from `publication-manifest.json` and the fail-closed publication gate.

| Field | Current state |
| --- | --- |
| Gate result | `{gate_result}` |
| Publication status | `{status['publication_status']}` |
| Canonical status | `{status['canonical_status']}` |
| Independent review | `{status['independent_review_status']}` |
| Clinical status | `{status['clinical_status']}` |
| Regulatory status | `{status['regulatory_status']}` |
| Reliance posture | `{status['reliance_posture']}` |
| Publish target | `{status['publish_target']}` |
| Publish root | `{status['publish_root']}` |
| Commit | `{status['commit_sha']}` |
| Generated at | `{generated_at}` |
| Deployment URL | `{status['deployment_url']}` |

## Gate errors

{error_lines}

## Reliance boundary

An `ALLOW` result means the declared artifact may be published under its current posture. It does not establish canonical doctrine, independent validation, clinical validity, regulatory authorization, external endorsement, or execution authority.
"""
    DOC_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUTPUT.write_text(markdown, encoding="utf-8")

    print(f"PUBLICATION_STATUS={gate_result}")
    print(f"json_output={JSON_OUTPUT.relative_to(ROOT)}")
    print(f"docs_output={DOC_OUTPUT.relative_to(ROOT)}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

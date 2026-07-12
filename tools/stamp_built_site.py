#!/usr/bin/env python3
"""Embed the current workflow identity into the built Pages artifact."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
OUTPUT = SITE / "deployment-identity.json"


def main() -> int:
    index = SITE / "index.html"
    if not index.is_file():
        print("DEPLOYMENT_IDENTITY=FAIL-CLOSED")
        print("reason=_site/index.html is missing")
        return 1

    commit_sha = os.getenv("GITHUB_SHA", "local")
    workflow_run_id = os.getenv("GITHUB_RUN_ID", "local")
    workflow_run_attempt = os.getenv("GITHUB_RUN_ATTEMPT", "local")

    identity = {
        "schema_version": "1.0.0",
        "identity_type": "governed-pages-deployment-identity",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": os.getenv(
            "GITHUB_REPOSITORY", "StegVerse-Labs/ara-admissibility-interop"
        ),
        "commit_sha": commit_sha,
        "workflow_run_id": workflow_run_id,
        "workflow_run_attempt": workflow_run_attempt,
        "publication_status": "public_review",
        "canonical_status": "not_authorized",
    }
    OUTPUT.write_text(json.dumps(identity, indent=2) + "\n", encoding="utf-8")

    marker = f'<meta name="stegverse-deployment-commit" content="{commit_sha}">'
    html = index.read_text(encoding="utf-8")
    if marker not in html:
        if "</head>" in html:
            html = html.replace("</head>", f"  {marker}\n</head>", 1)
        else:
            html = marker + "\n" + html
        index.write_text(html, encoding="utf-8")

    print("DEPLOYMENT_IDENTITY=CREATED")
    print(f"commit_sha={commit_sha}")
    print(f"output={OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

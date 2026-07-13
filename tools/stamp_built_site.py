#!/usr/bin/env python3
"""Embed the current workflow identity into the built Pages artifact."""

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
OUTPUT = SITE / "deployment-identity.json"


def emit_site_inventory() -> None:
    """Emit a bounded, deterministic inventory for successor-run diagnosis."""
    print(f"workspace_root={ROOT}")
    print(f"site_root={SITE}")
    print(f"site_exists={SITE.exists()}")
    print(f"site_is_dir={SITE.is_dir()}")
    if not SITE.is_dir():
        return

    built_files = sorted(path for path in SITE.rglob("*") if path.is_file())
    print(f"built_file_count={len(built_files)}")
    for built_file in built_files:
        print(f"built_file={built_file.relative_to(ROOT)}")


def resolve_index() -> Path | None:
    """Return a deterministic Pages entry point, normalizing one nested index."""
    root_index = SITE / "index.html"
    if root_index.is_file():
        print(f"resolved_index={root_index.relative_to(ROOT)}")
        return root_index

    candidates = sorted(
        path for path in SITE.rglob("index.html") if path.is_file()
    )
    if len(candidates) != 1:
        print("DEPLOYMENT_IDENTITY=FAIL-CLOSED")
        print("reason=_site/index.html is missing and nested index selection is ambiguous")
        print(f"nested_index_candidates={len(candidates)}")
        for candidate in candidates:
            print(f"candidate={candidate.relative_to(ROOT)}")
        return None

    source = candidates[0]
    SITE.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, root_index)
    print(f"normalized_index_source={source.relative_to(ROOT)}")
    print(f"normalized_index_target={root_index.relative_to(ROOT)}")
    return root_index


def main() -> int:
    emit_site_inventory()
    index = resolve_index()
    if index is None:
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

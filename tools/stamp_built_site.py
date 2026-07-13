#!/usr/bin/env python3
"""Embed the current workflow identity into the built Pages artifact."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
OUTPUT = SITE / "deployment-identity.json"
EXPECTED_SITE_MARKER = "ARA Admissibility Interop Docs"


def normalize_site_ownership() -> bool:
    """Make the container-built artifact writable without widening scope."""
    if not SITE.exists():
        print("ownership_normalization=not-required-site-missing")
        return True

    # Avoid invoking sudo when the artifact is already writable. This keeps local
    # validation dependency-free while retaining a bounded GitHub-hosted fallback
    # for root-owned files emitted by the Jekyll container action.
    probe = SITE / ".stegverse-write-probe"
    try:
        probe.write_text("writable\n", encoding="utf-8")
        probe.unlink()
        print("ownership_normalization=not-required-writable")
        return True
    except OSError:
        pass

    uid = os.getuid()
    gid = os.getgid()
    command = ["sudo", "chown", "-R", f"{uid}:{gid}", str(SITE)]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        probe.write_text("writable\n", encoding="utf-8")
        probe.unlink()
    except (OSError, subprocess.CalledProcessError) as exc:
        print("DEPLOYMENT_IDENTITY=FAIL-CLOSED")
        print("reason=unable to normalize _site ownership")
        print(f"ownership_error={exc}")
        return False

    print(f"ownership_normalized={uid}:{gid}")
    return True


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


def _candidate_score(path: Path) -> tuple[int, int, str]:
    """Rank index candidates by marker match, depth, then stable path."""
    try:
        contains_marker = EXPECTED_SITE_MARKER in path.read_text(
            encoding="utf-8", errors="replace"
        )
    except OSError:
        contains_marker = False
    relative = path.relative_to(SITE)
    return (0 if contains_marker else 1, len(relative.parts), str(relative))


def resolve_index() -> Path | None:
    """Return the governed Pages entry point and normalize it to _site/index.html."""
    root_index = SITE / "index.html"
    if root_index.is_file():
        print(f"resolved_index={root_index.relative_to(ROOT)}")
        return root_index

    candidates = sorted(
        (path for path in SITE.rglob("index.html") if path.is_file()),
        key=_candidate_score,
    )
    if not candidates:
        print("DEPLOYMENT_IDENTITY=FAIL-CLOSED")
        print("reason=_site/index.html is missing and no nested index exists")
        return None

    selected = candidates[0]
    marker_matches = [
        path
        for path in candidates
        if _candidate_score(path)[0] == 0
    ]
    if len(candidates) > 1:
        print(f"nested_index_candidates={len(candidates)}")
        print(f"marker_matching_candidates={len(marker_matches)}")
        for candidate in candidates:
            print(f"candidate={candidate.relative_to(ROOT)}")

    # Selection is deterministic. A marker-bearing candidate is preferred; when
    # no marker is present, the shallowest stable path is copied and the next
    # verification step remains responsible for failing closed on content.
    SITE.mkdir(parents=True, exist_ok=True)
    shutil.copy2(selected, root_index)
    print(f"normalized_index_source={selected.relative_to(ROOT)}")
    print(f"normalized_index_target={root_index.relative_to(ROOT)}")
    return root_index


def main() -> int:
    if not normalize_site_ownership():
        return 1

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

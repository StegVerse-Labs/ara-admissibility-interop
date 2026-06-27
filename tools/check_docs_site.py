#!/usr/bin/env python3
"""Check generated docs site integration invariants."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS_INDEX = ROOT / "docs" / "index.md"
DOCS_CONFIG = ROOT / "docs" / "_config.yml"
MANIFEST = ROOT / "release-manifest.json"

REQUIRED_INDEX_LINKS = [
    "release-readiness.md",
    "release-checklist.md",
    "dependency-policy.md",
    "optional-strict-validation.md",
    "validation-report-guide.md",
    "../admissibility/non-claims.md",
]

REQUIRED_CONFIG_PHRASES = [
    "title: ARA Admissibility Interop",
    "plugins: []",
    "markdown: kramdown",
]


def main() -> int:
    problems: list[str] = []

    if not DOCS_INDEX.is_file():
        problems.append("missing:docs/index.md")
        index_text = ""
    else:
        index_text = DOCS_INDEX.read_text(encoding="utf-8")
        for link in REQUIRED_INDEX_LINKS:
            if link not in index_text:
                problems.append(f"missing-docs-index-link:{link}")

    if not DOCS_CONFIG.is_file():
        problems.append("missing:docs/_config.yml")
        config_text = ""
    else:
        config_text = DOCS_CONFIG.read_text(encoding="utf-8")
        for phrase in REQUIRED_CONFIG_PHRASES:
            if phrase not in config_text:
                problems.append(f"missing-docs-config-phrase:{phrase}")

    if not MANIFEST.is_file():
        problems.append("missing:release-manifest.json")
    else:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        docs_site = manifest.get("docs_site", {})
        primary_docs = manifest.get("primary_docs", {})
        if docs_site.get("entrypoint") != "docs/index.md":
            problems.append("manifest-docs-entrypoint")
        if docs_site.get("config") != "docs/_config.yml":
            problems.append("manifest-docs-config")
        if primary_docs.get("docs_index") != "docs/index.md":
            problems.append("manifest-primary-docs-index")
        if primary_docs.get("docs_config") != "docs/_config.yml":
            problems.append("manifest-primary-docs-config")

    result = {
        "checked": ["docs/index.md", "docs/_config.yml", "release-manifest.json"],
        "problem_count": len(problems),
        "problems": problems,
        "result": "pass" if not problems else "fail",
    }
    print(json.dumps(result, indent=2))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Regression tests for the dependency-free governed documentation builder."""

from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("build_governed_docs_site.py")
spec = importlib.util.spec_from_file_location("build_governed_docs_site", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def require(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def main() -> int:
    rendered = module.markdown_to_html(
        "# Test Site\n\n- [Guide](guide.md)\n\n`bounded`\n\n```\n<unsafe>\n```\n",
        "Test Site",
    )
    require("<h1>Test Site</h1>" in rendered, "heading")
    require('href="guide.html"' in rendered, "markdown-link-conversion")
    require("<code>bounded</code>" in rendered, "inline-code")
    require("&lt;unsafe&gt;" in rendered, "code-escaping")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / "docs"
        destination = root / "_site"
        source.mkdir()
        (source / "index.md").write_text(
            "# ARA Admissibility Interop Docs\n\n- [Guide](guide.md)\n",
            encoding="utf-8",
        )
        (source / "guide.md").write_text("# Guide\n\nGoverned content.\n", encoding="utf-8")
        (source / "record.json").write_text('{"ok":true}\n', encoding="utf-8")

        original_root = module.ROOT
        original_source = module.SOURCE
        original_destination = module.DESTINATION
        try:
            module.ROOT = root
            module.SOURCE = source
            module.DESTINATION = destination
            require(module.main() == 0, "builder-main")
        finally:
            module.ROOT = original_root
            module.SOURCE = original_source
            module.DESTINATION = original_destination

        require((destination / "index.html").is_file(), "root-index")
        require((destination / "guide.html").is_file(), "guide-html")
        require((destination / "record.json").read_text(encoding="utf-8") == '{"ok":true}\n', "asset-copy")
        require("guide.html" in (destination / "index.html").read_text(encoding="utf-8"), "rendered-link")

    print("GOVERNED_DOCS_BUILDER_TESTS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

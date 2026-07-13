#!/usr/bin/env python3
"""Build the governed documentation site without external runtime dependencies.

The builder converts the repository's Markdown documentation into a bounded
static HTML tree, copies declared JSON/text artifacts, and guarantees a root
_site/index.html before deployment identity stamping.
"""

from __future__ import annotations

import html
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs"
DESTINATION = ROOT / "_site"

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
CODE_RE = re.compile(r"`([^`]+)`")


def inline_markup(text: str) -> str:
    escaped = html.escape(text, quote=False)
    escaped = CODE_RE.sub(lambda match: f"<code>{html.escape(match.group(1))}</code>", escaped)

    def link(match: re.Match[str]) -> str:
        label = html.escape(match.group(1), quote=False)
        target = match.group(2)
        if target.endswith(".md"):
            target = target[:-3] + ".html"
        return f'<a href="{html.escape(target, quote=True)}">{label}</a>'

    return LINK_RE.sub(link, escaped)


def markdown_to_html(markdown: str, title: str) -> str:
    lines = markdown.splitlines()
    body: list[str] = []
    in_code = False
    code_lines: list[str] = []
    in_list = False
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            body.append(f"<p>{inline_markup(' '.join(paragraph))}</p>")
            paragraph.clear()

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            body.append("</ul>")
            in_list = False

    for line in lines:
        if line.strip() == "---" and not body and not paragraph:
            continue
        if line.startswith(("layout:", "title:")) and not body and not paragraph:
            continue
        if line.startswith("```"):
            flush_paragraph()
            close_list()
            if in_code:
                body.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
                code_lines.clear()
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            close_list()
            continue
        if stripped.startswith("#"):
            flush_paragraph()
            close_list()
            level = min(len(stripped) - len(stripped.lstrip("#")), 6)
            content = stripped[level:].strip()
            body.append(f"<h{level}>{inline_markup(content)}</h{level}>")
            continue
        if stripped.startswith("- "):
            flush_paragraph()
            if not in_list:
                body.append("<ul>")
                in_list = True
            body.append(f"<li>{inline_markup(stripped[2:])}</li>")
            continue
        paragraph.append(stripped)

    flush_paragraph()
    close_list()
    if in_code:
        body.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")

    return "\n".join([
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '  <meta charset="utf-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1">',
        f"  <title>{html.escape(title)}</title>",
        "  <style>body{font-family:system-ui,-apple-system,sans-serif;max-width:880px;margin:2rem auto;padding:0 1rem;line-height:1.55}code,pre{background:#f4f4f4}pre{padding:1rem;overflow:auto}a{word-break:break-word}</style>",
        "</head>",
        "<body>",
        *body,
        "</body>",
        "</html>",
        "",
    ])


def document_title(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def main() -> int:
    if not SOURCE.is_dir():
        print("GOVERNED_DOCS_BUILD=FAIL-CLOSED")
        print("reason=docs source directory missing")
        return 1
    index_source = SOURCE / "index.md"
    if not index_source.is_file():
        print("GOVERNED_DOCS_BUILD=FAIL-CLOSED")
        print("reason=docs/index.md missing")
        return 1

    if DESTINATION.exists():
        shutil.rmtree(DESTINATION)
    DESTINATION.mkdir(parents=True)

    built = 0
    for source in sorted(path for path in SOURCE.rglob("*") if path.is_file()):
        relative = source.relative_to(SOURCE)
        if source.suffix.lower() == ".md":
            markdown = source.read_text(encoding="utf-8")
            target = (DESTINATION / relative).with_suffix(".html")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                markdown_to_html(markdown, document_title(markdown, source.stem)),
                encoding="utf-8",
            )
        elif source.name != "_config.yml":
            target = DESTINATION / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        built += 1

    root_index = DESTINATION / "index.html"
    if not root_index.is_file():
        print("GOVERNED_DOCS_BUILD=FAIL-CLOSED")
        print("reason=builder did not produce _site/index.html")
        return 1
    rendered = root_index.read_text(encoding="utf-8")
    if "ARA Admissibility Interop Docs" not in rendered:
        print("GOVERNED_DOCS_BUILD=FAIL-CLOSED")
        print("reason=root entry point lacks expected marker")
        return 1

    print("GOVERNED_DOCS_BUILD=PASS")
    print(f"source={SOURCE.relative_to(ROOT)}")
    print(f"destination={DESTINATION.relative_to(ROOT)}")
    print(f"source_file_count={built}")
    print(f"root_entry={root_index.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

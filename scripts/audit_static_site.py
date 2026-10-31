#!/usr/bin/env python3
"""Dependency-light release audit for a static GitHub Pages storefront."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

REQUIRED = [
    "index.html", "styles.css", "app.js", "404.html", "robots.txt",
    "sitemap.xml", "favicon.svg", ".nojekyll", "data/products.json",
]

class MarkupAudit(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.refs: list[tuple[str, str]] = []
        self.buttons: list[dict[str, str]] = []
        self.h1 = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        values = dict(attrs)
        if "id" in values:
            self.ids.append(values["id"])
        for key in ("href", "src"):
            if key in values:
                self.refs.append((key, values[key]))
        if tag == "button":
            self.buttons.append(values)
        if tag == "h1":
            self.h1 += 1


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def audit(root: Path) -> None:
    if not root.is_dir():
        fail(f"not a directory: {root}")
    for relative in REQUIRED:
        path = root / relative
        if not path.is_file() or (path.stat().st_size == 0 and relative != ".nojekyll"):
            fail(f"missing or empty: {relative}")

    try:
        products = json.loads((root / "data/products.json").read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid data/products.json: {exc}")
    if not isinstance(products, list):
        fail("data/products.json must contain an array")

    app = root / "app.js"
    node = subprocess.run(["node", "--check", str(app)], capture_output=True, text=True)
    if node.returncode:
        fail(f"JavaScript syntax error:\n{node.stderr.strip()}")

    html_path = root / "index.html"
    html = html_path.read_text(encoding="utf-8")
    parser = MarkupAudit()
    parser.feed(html)
    if parser.h1 != 1:
        fail(f"index.html must contain exactly one h1; found {parser.h1}")
    if len(parser.ids) != len(set(parser.ids)):
        fail("index.html contains duplicate id attributes")
    if '<meta name="viewport"' not in html:
        fail("index.html is missing viewport metadata")
    if "<title>" not in html or '<meta name="description"' not in html:
        fail("index.html is missing title or description")
    if not any("favicon.svg" in value for _, value in parser.refs):
        fail("index.html does not reference favicon.svg")
    if any(button.get("type") != "button" for button in parser.buttons):
        fail("every button in index.html must declare type=button")

    for kind, reference in parser.refs:
        if not reference or reference.startswith(("#", "https://", "http://", "mailto:", "tel:")):
            continue
        local = reference.split("#", 1)[0].split("?", 1)[0]
        if local in ("", "./"):
            continue
        if not (root / local).is_file():
            fail(f"broken local {kind}: {reference}")

    print(f"PASS: {root} ({len(products)} catalog records, {len(parser.refs)} references)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="repository root")
    args = parser.parse_args()
    audit(args.root.resolve())

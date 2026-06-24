#!/usr/bin/env python3
"""Website QA Auditor — a zero-dependency static-site/page health checker.

Audits a URL (or a local HTML file) for common SEO, accessibility, social-share,
and mobile issues, prints a scored report, and can write a client-ready Markdown
report. Pure Python standard library — no pip install required.

Examples:
    python auditor.py https://example.com
    python auditor.py --file sample.html --out report.md
    python auditor.py https://example.com --links        # also HEAD-check links
    python auditor.py https://example.com --ai           # add an AI summary (needs ANTHROPIC_API_KEY)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from html.parser import HTMLParser

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"
MARK = {PASS: "[PASS]", WARN: "[WARN]", FAIL: "[FAIL]"}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self._in_title = False
        self.metas: dict[str, str] = {}
        self.has_viewport = False
        self.html_lang: str | None = None
        self.rels: set[str] = set()
        self.imgs: list[bool] = []          # True == has usable alt
        self.links: list[str] = []
        self.headings: dict[int, int] = {i: 0 for i in range(1, 7)}
        self.mixed = 0                       # http:// resources on the page

    def handle_starttag(self, tag, attrs):
        d = {k.lower(): (v or "") for k, v in attrs}
        for v in d.values():
            if v.startswith("http://"):
                self.mixed += 1
        if tag == "html":
            self.html_lang = d.get("lang") or None
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            key = (d.get("name") or d.get("property") or "").lower()
            if key:
                self.metas[key] = d.get("content", "")
            if d.get("name", "").lower() == "viewport":
                self.has_viewport = True
        elif tag == "link":
            if d.get("rel"):
                self.rels.add(d["rel"].lower())
        elif tag == "img":
            self.imgs.append("alt" in d and bool(d["alt"].strip()))
        elif tag == "a":
            self.links.append(d.get("href", ""))
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings[int(tag[1])] += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def fetch(target: str) -> tuple[str, int]:
    """Return (html, size_bytes). Accepts a URL or a local file path."""
    if os.path.isfile(target):
        raw = open(target, "rb").read()
        return raw.decode("utf-8", "replace"), len(raw)
    req = urllib.request.Request(target, headers={"User-Agent": "Website-QA-Auditor/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        raw = r.read()
    return raw.decode("utf-8", "replace"), len(raw)


def audit(p: PageParser, size_bytes: int) -> list[tuple[str, str, str]]:
    """Return a list of (severity, check, detail)."""
    rows: list[tuple[str, str, str]] = []
    title = " ".join(p.title.split())

    # SEO
    if not title:
        rows.append((FAIL, "Page title", "Missing <title> — critical for SEO + browser tabs."))
    elif not 20 <= len(title) <= 65:
        rows.append((WARN, "Page title", f"{len(title)} chars (aim 20–65): '{title[:60]}'"))
    else:
        rows.append((PASS, "Page title", f"'{title}'"))

    desc = p.metas.get("description", "")
    if not desc:
        rows.append((FAIL, "Meta description", "Missing — hurts search snippets + click-through."))
    elif not 50 <= len(desc) <= 165:
        rows.append((WARN, "Meta description", f"{len(desc)} chars (aim 50–160)."))
    else:
        rows.append((PASS, "Meta description", f"{len(desc)} chars."))

    # Mobile + a11y
    rows.append((PASS, "Mobile viewport", "Present.") if p.has_viewport
                else (FAIL, "Mobile viewport", "No <meta viewport> — site won't scale on phones."))
    rows.append((PASS, "Language attribute", f"lang='{p.html_lang}'") if p.html_lang
                else (WARN, "Language attribute", "No <html lang> — screen readers can't pick a voice."))

    h1 = p.headings[1]
    if h1 == 1:
        rows.append((PASS, "Heading structure", "Exactly one <h1>."))
    elif h1 == 0:
        rows.append((FAIL, "Heading structure", "No <h1> — weak structure for SEO + a11y."))
    else:
        rows.append((WARN, "Heading structure", f"{h1} <h1> tags (should be 1)."))

    total_img = len(p.imgs)
    no_alt = total_img - sum(p.imgs)
    if total_img == 0:
        rows.append((PASS, "Image alt text", "No images."))
    elif no_alt == 0:
        rows.append((PASS, "Image alt text", f"All {total_img} images have alt text."))
    else:
        sev = FAIL if no_alt > total_img / 2 else WARN
        rows.append((sev, "Image alt text", f"{no_alt}/{total_img} images missing alt text."))

    # Social share
    og = [k for k in ("og:title", "og:description", "og:image") if p.metas.get(k)]
    if len(og) == 3:
        rows.append((PASS, "Social share (OG)", "og:title, description, image all set."))
    elif og:
        rows.append((WARN, "Social share (OG)", f"Only {', '.join(og)} set — links preview poorly."))
    else:
        rows.append((WARN, "Social share (OG)", "No Open Graph tags — shared links show a blank preview."))

    rows.append((PASS, "Favicon", "Declared.") if any("icon" in r for r in p.rels)
                else (WARN, "Favicon", "No favicon link — looks unfinished in tabs/bookmarks."))

    # Hygiene
    empty = sum(1 for h in p.links if h.strip() in ("", "#"))
    if empty:
        rows.append((WARN, "Links", f"{empty} empty/placeholder link(s) (href='' or '#')."))
    else:
        rows.append((PASS, "Links", f"{len(p.links)} links, none empty."))

    if p.mixed:
        rows.append((WARN, "Mixed content", f"{p.mixed} resource(s) loaded over http:// (use https)."))
    else:
        rows.append((PASS, "Mixed content", "No insecure http:// resources."))

    kb = size_bytes / 1024
    rows.append((PASS, "Page weight", f"{kb:.0f} KB.") if kb < 250
                else (WARN, "Page weight", f"{kb:.0f} KB HTML (heavy — consider trimming)."))
    return rows


def check_links(links: list[str], base: str, cap: int = 20) -> list[tuple[str, str, str]]:
    out = []
    seen = set()
    for href in links:
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        url = href if href.startswith("http") else urllib.parse.urljoin(base, href)
        if url in seen:
            continue
        seen.add(url)
        if len(seen) > cap:
            break
        try:
            req = urllib.request.Request(url, method="HEAD",
                                         headers={"User-Agent": "Website-QA-Auditor/1.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                if r.status >= 400:
                    out.append((FAIL, "Broken link", f"{r.status} {url}"))
        except Exception as e:  # noqa
            out.append((FAIL, "Broken link", f"{type(e).__name__} {url}"))
    if not out:
        out.append((PASS, "Link check", f"Checked {len(seen)} links — none broken."))
    return out


def grade(rows):
    score = sum(1 for s, *_ in rows if s == PASS) + 0.5 * sum(1 for s, *_ in rows if s == WARN)
    pct = round(score / len(rows) * 100)
    letter = "A" if pct >= 90 else "B" if pct >= 80 else "C" if pct >= 70 else "D" if pct >= 55 else "F"
    return pct, letter


def render_terminal(target, rows, pct, letter):
    print("=" * 60)
    print(f"  Website QA Audit — {target}")
    print(f"  Score: {pct}%  (grade {letter})")
    print("=" * 60)
    for sev, check, detail in rows:
        print(f"  {MARK[sev]} {check}: {detail}")
    fails = sum(1 for s, *_ in rows if s == FAIL)
    warns = sum(1 for s, *_ in rows if s == WARN)
    print("-" * 60)
    print(f"  {fails} fail, {warns} warn, {len(rows)-fails-warns} pass")


def render_markdown(target, rows, pct, letter):
    icon = {PASS: "✅", WARN: "⚠️", FAIL: "❌"}
    out = [f"# Website QA Report — {target}", "", f"**Score: {pct}% (grade {letter})**", "",
           "| Result | Check | Detail |", "|---|---|---|"]
    for sev, check, detail in rows:
        out.append(f"| {icon[sev]} | {check} | {detail} |")
    out += ["", "_Generated by Website-QA-Auditor. Each item is a real, fixable issue._"]
    return "\n".join(out)


def ai_summary(target, rows):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return "\n(For an AI-written client summary, set ANTHROPIC_API_KEY and re-run with --ai.)"
    findings = "\n".join(f"{s}: {c} — {d}" for s, c, d in rows)
    body = json.dumps({
        "model": "claude-opus-4-8",
        "max_tokens": 400,
        "messages": [{"role": "user", "content":
                      f"Write a short, friendly client summary of this website audit for {target}, "
                      f"then the top 3 fixes in priority order. Findings:\n{findings}"}],
    }).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body,
                                 headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                                          "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
        return "\n## AI summary\n" + data["content"][0]["text"]
    except Exception as e:  # noqa
        return f"\n(AI summary failed: {e})"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Audit a web page for SEO / a11y / mobile / social issues.")
    ap.add_argument("target", nargs="?", help="URL to audit")
    ap.add_argument("--file", help="audit a local HTML file instead of a URL")
    ap.add_argument("--out", help="write a Markdown report to this path")
    ap.add_argument("--links", action="store_true", help="also HEAD-check links (network, capped at 20)")
    ap.add_argument("--ai", action="store_true", help="append an AI-written client summary")
    args = ap.parse_args(argv)

    try:  # clean unicode (em-dashes etc.) in the Windows console too
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa
        pass

    target = args.file or args.target
    if not target:
        ap.error("give a URL or --file <path>")

    try:
        html, size = fetch(target)
    except Exception as e:  # noqa
        print(f"Could not fetch '{target}': {e}", file=sys.stderr)
        return 2

    p = PageParser()
    p.feed(html)
    rows = audit(p, size)
    if args.links and not args.file:
        import urllib.parse  # noqa
        rows += check_links(p.links, args.target)
    pct, letter = grade(rows)

    render_terminal(target, rows, pct, letter)
    md = render_markdown(target, rows, pct, letter)
    if args.ai:
        md += "\n" + ai_summary(target, rows)
        print(ai_summary(target, rows))
    if args.out:
        open(args.out, "w", encoding="utf-8").write(md)
        print(f"\nMarkdown report written to {args.out}")
    return 1 if any(s == FAIL for s, *_ in rows) else 0


if __name__ == "__main__":
    sys.exit(main())

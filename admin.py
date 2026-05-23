#!/usr/bin/env python3
"""Admin CLI for konoerik.github.io

Commands:
  build              Build src/ -> site/
  new-post <title>   Scaffold a new blog post
"""
import argparse
import re
import shutil
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

import markdown as md_lib
import yaml

SRC = Path("src")
SITE = Path("site")


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------

def parse_frontmatter(text):
    if text.startswith("---"):
        _, fm, body = text.split("---", 2)
        meta = yaml.safe_load(fm) or {}
        return meta, body.strip()
    return {}, text.strip()


def render(template, meta, content, root):
    out = template
    out = out.replace("{{ title }}", str(meta.get("title", "")))
    out = out.replace("{{ description }}", str(meta.get("description", "") or ""))
    out = out.replace("{{ content }}", content)
    out = out.replace("{{ root }}", root)
    return out


def build_page(src, dest, template):
    text = src.read_text()
    meta, body = parse_frontmatter(text)
    content = md_lib.markdown(body)
    depth = len(dest.relative_to(SITE).parts) - 1
    root = "../" * depth
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render(template, meta, content, root))
    print(f"  built  {dest}")


def build_blog_index(posts, template):
    dest = SITE / "blog" / "index.html"
    root = "../"

    items = []
    for post_date, slug, title, description in sorted(posts, reverse=True):
        href = f"posts/{post_date}-{slug}.html"
        desc_line = f"<p>{description}</p>" if description else ""
        items.append(
            f"<article>\n"
            f"  <time datetime=\"{post_date}\">{post_date}</time>\n"
            f"  <h2><a href=\"{href}\">{title}</a></h2>\n"
            f"  {desc_line}\n"
            f"</article>"
        )

    content = "<h1>Blog</h1>\n" + (
        "\n".join(items) if items else "<p>No posts yet.</p>"
    )
    meta = {"title": "Blog", "description": "Writing"}
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render(template, meta, content, root))
    print(f"  built  {dest}")


def cmd_build(_args):
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()

    template = (SRC / "_templates" / "base.html").read_text()

    assets = SRC / "assets"
    if assets.exists():
        shutil.copytree(assets, SITE / "assets")
        print(f"  copied {SITE / 'assets'}")

    posts = []
    for src in sorted(SRC.rglob("*.md")):
        rel = src.relative_to(SRC)
        dest = SITE / rel.with_suffix(".html")
        build_page(src, dest, template)

        parts = rel.parts
        if len(parts) == 3 and parts[:2] == ("blog", "posts"):
            m = re.match(r"^(\d{4}-\d{2}-\d{2})-(.+)$", src.stem)
            if m:
                meta, _ = parse_frontmatter(src.read_text())
                posts.append((m.group(1), m.group(2), meta.get("title", src.stem), meta.get("description", "")))

    build_blog_index(posts, template)
    print("done")


# ---------------------------------------------------------------------------
# new-post
# ---------------------------------------------------------------------------

def slugify(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def cmd_new_post(args):
    title = " ".join(args.title)
    slug = slugify(title)
    today = date.today().isoformat()
    dest = SRC / "blog" / "posts" / f"{today}-{slug}.md"

    if dest.exists():
        print(f"Already exists: {dest}")
        raise SystemExit(1)

    dest.write_text(
        f"---\n"
        f"title: {title}\n"
        f"description:\n"
        f"date: {today}\n"
        f"tags:\n"
        f"---\n\n"
        f"# {title}\n\n"
        f"Write your post here.\n"
    )
    print(f"Created: {dest}")


# ---------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------

_VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


class _TagChecker(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in _VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in _VOID:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        else:
            expected = self.stack[-1] if self.stack else "none"
            self.errors.append(f"unexpected </{tag}>, expected </{expected}>")


class _LinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a":
            url = attrs.get("href")
        elif tag in ("img", "script"):
            url = attrs.get("src")
        elif tag == "link":
            url = attrs.get("href")
        else:
            return
        if url:
            self.links.append(url)


def _resolve(base_file, url, site_root):
    parsed = urlparse(url)
    if parsed.scheme or url.startswith("//") or not parsed.path:
        return None
    path = parsed.path
    target = (site_root / path.lstrip("/")) if path.startswith("/") else (base_file.parent / path)
    target = target.resolve()
    if target.is_dir():
        target = target / "index.html"
    return target


def cmd_check(_args):
    issues = []

    # 1. Frontmatter: title required in every source file
    for src in sorted(SRC.rglob("*.md")):
        meta, _ = parse_frontmatter(src.read_text())
        if not meta.get("title"):
            issues.append(f"[frontmatter] missing title: {src.relative_to(SRC)}")

    if not SITE.exists():
        print("site/ not found — run 'make build' first")
        raise SystemExit(1)

    site_root = SITE.resolve()
    pages = sorted(SITE.rglob("*.html"))

    for html_file in pages:
        rel = html_file.relative_to(SITE)
        text = html_file.read_text()

        # 2. Tag balance
        checker = _TagChecker()
        checker.feed(text)
        for err in checker.errors:
            issues.append(f"[html] {rel}: {err}")
        for tag in checker.stack:
            issues.append(f"[html] {rel}: unclosed <{tag}>")

        # 3. Internal link integrity
        extractor = _LinkExtractor()
        extractor.feed(text)
        for url in extractor.links:
            target = _resolve(html_file, url, site_root)
            if target and not target.exists():
                issues.append(f"[links] {rel}: broken → '{url}'")

    if issues:
        for issue in issues:
            print(issue)
        raise SystemExit(1)

    print(f"ok — {len(pages)} pages, no issues")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Admin CLI for konoerik.github.io",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("build", help="Build src/ -> site/")
    sub.add_parser("check", help="Check built site for broken links, tag balance, and missing frontmatter")

    p_post = sub.add_parser("new-post", help="Scaffold a new blog post")
    p_post.add_argument("title", nargs="+", help="Post title (no quotes needed)")

    args = parser.parse_args()

    dispatch = {
        "build": cmd_build,
        "check": cmd_check,
        "new-post": cmd_new_post,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()

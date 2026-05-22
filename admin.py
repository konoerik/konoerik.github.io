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
from pathlib import Path

SRC = Path("src")
SITE = Path("site")


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------

def parse_meta(text):
    meta = {}
    m = re.match(r"<!--\s*\n(.*?)\n-->", text, re.DOTALL)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                meta[k.strip()] = v.strip()
    return meta


def body_content(html):
    m = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL)
    return m.group(1).strip() if m else html.strip()


def render(template, meta, content, root):
    out = template
    out = out.replace("{{ title }}", meta.get("title", ""))
    out = out.replace("{{ description }}", meta.get("description", ""))
    out = out.replace("{{ content }}", content)
    out = out.replace("{{ root }}", root)
    return out


def build_page(src, dest, template):
    text = src.read_text()
    meta = parse_meta(text)
    content = body_content(text)
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
    for src in sorted(SRC.rglob("*.html")):
        rel = src.relative_to(SRC)
        if rel.parts[0] == "_templates":
            continue

        dest = SITE / rel
        build_page(src, dest, template)

        parts = rel.parts
        if len(parts) == 3 and parts[:2] == ("blog", "posts"):
            m = re.match(r"^(\d{4}-\d{2}-\d{2})-(.+)$", src.stem)
            if m:
                meta = parse_meta(src.read_text())
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
    dest = SRC / "blog" / "posts" / f"{today}-{slug}.html"

    if dest.exists():
        print(f"Already exists: {dest}")
        raise SystemExit(1)

    dest.write_text(
        f"""<!--
title: {title}
description:
date: {today}
tags:
-->
<!DOCTYPE html>
<html lang="en">
<head><title>{title}</title></head>
<body>
<h1>{title}</h1>

<p>Write your post here.</p>
</body>
</html>
"""
    )
    print(f"Created: {dest}")


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

    p_post = sub.add_parser("new-post", help="Scaffold a new blog post")
    p_post.add_argument("title", nargs="+", help="Post title (no quotes needed)")

    args = parser.parse_args()

    dispatch = {
        "build": cmd_build,
        "new-post": cmd_new_post,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()

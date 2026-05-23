# konoerik.github.io

Personal site. Markdown source with YAML frontmatter, a lightweight Python build step, and plain HTML/CSS output. No frameworks.

## Setup

```bash
make install   # create .venv and install dependencies (first time only)
```

## Develop

```bash
make build                        # build src/ → site/
make serve                        # build and serve at localhost:8000
make new-post TITLE="Post Title"  # scaffold a new blog post
make clean                        # wipe site/
make help                         # list all targets
```

Deploy is automatic via GitHub Actions on every push to `main`.

> **First deploy:** go to Settings → Pages → Source and select **GitHub Actions**.

## How it works

Source files live in `src/` as Markdown with YAML frontmatter. The build script (`admin.py`) converts them to HTML using the base template at `src/_templates/base.html`, writing output to `site/`.

**Page frontmatter:**

```markdown
---
title: My Page
description: A short description
---

# My Page

Content goes here.
```

**Blog posts** go in `src/blog/posts/YYYY-MM-DD-slug.md`. The blog index is auto-generated from all posts on each build. Use `make new-post` to scaffold one.

**Blog post frontmatter:**

```markdown
---
title: My Post
description: A short description
date: 2026-05-22
tags:
---
```

## Reference

### Images

Place images in `src/assets/images/`. They are copied to `site/assets/images/` on each build.

Reference them in any Markdown file using `{{ root }}` to get a path relative to the site root — this works correctly regardless of how deep the page is nested:

```markdown
![Alt text]({{ root }}assets/images/photo.jpg)
```

### Template placeholders

These can be used in `base.html` and also within Markdown page content:

| Placeholder | Value |
|---|---|
| `{{ title }}` | Page title from frontmatter |
| `{{ description }}` | Page description from frontmatter |
| `{{ content }}` | Rendered page body |
| `{{ root }}` | Relative path back to site root (e.g. `../../` for a nested page) |

### Adding a new page

Create `src/your-page/index.md` with frontmatter and content. It will be built to `site/your-page/index.html` automatically.

### Dependencies

Managed with `uv` in a local `.venv`. To add a new dependency:

```bash
uv pip install <package>
# then add it to requirements.txt
```

# Plan

## Active


## Backlog
- Style blockquotes in markdown-to-HTML: add left-side ribbon (border-left) and/or subtle background; apply globally to all markdown content
- Consider draft mechanism for blog posts (frontmatter `draft: true` skipped at build time, like Hugo/Jekyll)
- Add RSS feed: generate `site/blog/feed.xml` in `admin.py build`, add feed icon to footer
- Add contact page: evaluate form solution (e.g. Formspree) so email never appears in HTML
- Tagging system for blog posts: tag frontmatter, tag index pages, filter by tag
- Review blog post page layout: date placement, blog header size, back link to blog index


## Done
- Repo scaffolding: src/ structure, templates, assets
- admin.py CLI (build, new-post)
- Makefile
- GitHub Actions deploy workflow
- Migrate src/ to Markdown + YAML frontmatter (python-markdown, pyyaml, uv/.venv)
- Makefile: add install and help targets
- README: update for markdown workflow, add reference section

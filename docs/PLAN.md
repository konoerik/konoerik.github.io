# Plan

## Active


## Backlog
- Consider draft mechanism for blog posts (frontmatter `draft: true` skipped at build time, like Hugo/Jekyll)
- Add RSS feed: generate `site/blog/feed.xml` in `admin.py build`, add feed icon to footer
- Add contact page: evaluate form solution (e.g. Formspree) so email never appears in HTML


## Done
- Repo scaffolding: src/ structure, templates, assets
- admin.py CLI (build, new-post)
- Makefile
- GitHub Actions deploy workflow
- Migrate src/ to Markdown + YAML frontmatter (python-markdown, pyyaml, uv/.venv)
- Makefile: add install and help targets
- README: update for markdown workflow, add reference section

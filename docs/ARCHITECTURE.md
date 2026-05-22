# Architecture

## Quick Reference

**Stack:** HTML/CSS, Python 3 (stdlib only), GitHub Actions
**Entry points:** `src/index.html` (landing), `admin.py` (build CLI)
**Key constraints:** no frameworks, no pip dependencies, stdlib-only build scripts
**Patterns:** source in `src/`, output to `site/` (git-ignored); page metadata via HTML comment frontmatter; blog index auto-generated from `src/blog/posts/YYYY-MM-DD-slug.html`


## Decisions (ADRs)

### ADR-1: No static site generator — 2026-05-22
**Context:** Personal site needing static pages and a blog.
**Decision:** Raw HTML/CSS with a small Python build script (`admin.py`) instead of Jekyll, Hugo, or similar.
**Consequences:** Full control, zero dependency rot, slightly more manual work when adding new page types.

### ADR-2: GitHub Actions + `site/` output over gh-pages branch — 2026-05-22
**Context:** GitHub Pages supports root, `/docs` folder, or a separate branch as source. `/docs` conflicts with project documentation folder installed by claudify.
**Decision:** GitHub Actions deploys `site/` directory; Pages source set to "GitHub Actions" in repo settings.
**Consequences:** Clean source/output separation; deploy is fully automatic on push to main; custom output folder name is free.


## Detail
<!-- Load on demand. Diagrams, module breakdowns, etc. -->

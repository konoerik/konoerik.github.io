# Architecture

## Quick Reference

**Stack:** HTML/CSS, Python 3 (minimal deps: `markdown`, `pyyaml`, `pillow`), GitHub Actions
**Entry points:** `src/index.md` (landing), `admin.py` (build CLI)
**Key constraints:** no frameworks, minimal pip dependencies, keep `admin.py` readable top to bottom
**Patterns:** source in `src/` as Markdown with YAML frontmatter, output to `site/` (git-ignored); blog index auto-generated from `src/blog/posts/YYYY-MM-DD-slug.md`
**Tools:** `tools/flac-checker/` — standalone FLAC integrity checker with its own isolated uv env (deps: `soundfile`, `numpy`, `mutagen`); not part of the site build


## Decisions (ADRs)

### ADR-1: No static site generator — 2026-05-22
**Context:** Personal site needing static pages and a blog.
**Decision:** Raw HTML/CSS with a small Python build script (`admin.py`) instead of Jekyll, Hugo, or similar.
**Consequences:** Full control, zero dependency rot, slightly more manual work when adding new page types.

### ADR-2: GitHub Actions + `site/` output over gh-pages branch — 2026-05-22
**Context:** GitHub Pages supports root, `/docs` folder, or a separate branch as source. `/docs` conflicts with project documentation folder installed by claudify.
**Decision:** GitHub Actions deploys `site/` directory; Pages source set to "GitHub Actions" in repo settings.
**Consequences:** Clean source/output separation; deploy is fully automatic on push to main; custom output folder name is free.


### ADR-3: flac-checker as isolated tool under tools/ — 2026-05-28
**Context:** Needed a FLAC integrity checker (stream properties, metadata, frequency cutoff via STFT) for verifying music purchases. Its deps (soundfile, numpy, mutagen) have nothing to do with the site build.
**Decision:** Placed under `tools/flac-checker/` with its own `pyproject.toml` and `uv.lock`, completely separate from the site's uv environment.
**Consequences:** Site build stays clean; tool is still version-controlled with the repo; running `uv run check.py` from the tool directory is self-contained.


## Detail
<!-- Load on demand. Diagrams, module breakdowns, etc. -->

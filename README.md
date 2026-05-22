# konoerik.github.io

Personal site. Static HTML/CSS with a lightweight Python build step. No frameworks.

## Develop

```bash
make build                      # build src/ → site/
make serve                      # build and serve at localhost:8000
make new-post TITLE=Post Title  # scaffold a new blog post
make clean                      # wipe site/
```

Deploy is automatic via GitHub Actions on every push to `main`.

> **First deploy:** go to Settings → Pages → Source and select **GitHub Actions**.

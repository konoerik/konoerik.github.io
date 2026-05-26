.PHONY: build serve clean new-post new-page optimize-image install help check test

PYTHON := .venv/bin/python3

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "  install          Create .venv and install dependencies"
	@echo "  build            Build src/ -> site/"
	@echo "  check            Check built site for broken links, tag balance, missing frontmatter"
	@echo "  serve            Build then serve at localhost:8000"
	@echo "  new-post         Scaffold a post: make new-post TITLE='My Title'"
	@echo "  new-page         Scaffold a page: make new-page PATH=projects/my-project TITLE='My Title'"
	@echo "  optimize-image   Convert image to WebP: make optimize-image IMG=src/assets/images/foo.png"
	@echo "  clean            Remove site/"

install:
	uv venv .venv
	uv pip install -r requirements.txt

build: .venv
	$(PYTHON) admin.py build

serve: build
	$(PYTHON) -m http.server 8000 --directory site/

check: build
	$(PYTHON) admin.py check

test: check

clean:
	rm -rf site/

new-post: .venv
	$(PYTHON) admin.py new-post $(TITLE)

new-page: .venv
	$(PYTHON) admin.py new-page $(PATH) $(TITLE)

optimize-image: .venv
	$(PYTHON) admin.py optimize-image $(IMG)

.venv:
	uv venv .venv
	uv pip install -r requirements.txt

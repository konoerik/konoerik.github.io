.PHONY: build serve clean new-post install help check

PYTHON := .venv/bin/python3

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "  install          Create .venv and install dependencies"
	@echo "  build            Build src/ -> site/"
	@echo "  check            Check built site for broken links, tag balance, missing frontmatter"
	@echo "  serve            Build then serve at localhost:8000"
	@echo "  new-post         Scaffold a post: make new-post TITLE='My Title'"
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

clean:
	rm -rf site/

new-post: .venv
	$(PYTHON) admin.py new-post $(TITLE)

.venv:
	uv venv .venv
	uv pip install -r requirements.txt

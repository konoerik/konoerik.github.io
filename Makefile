.PHONY: build serve clean new-post

build:
	python3 admin.py build

serve: build
	python3 -m http.server 8000 --directory site/

clean:
	rm -rf site/

new-post:
	python3 admin.py new-post $(TITLE)

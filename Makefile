SHELL := /bin/bash
.ONESHELL:

.PHONY: venv
venv: .venv
	source .venv/bin/activate

.venv:
	python3 -m venv .venv

.PHONY: requirements
requirements: requirements.txt venv
	python3 -m pip install --upgrade -r requirements.txt

steins.db: venv
	python3 aux/init_feeds.py

.PHONY: test
test: venv
	python3 -m pytest tests

.PHONY: debug
debug: venv
	env FLASK_ENV=development python3 -m flask run

.PHONY: foo
foo: venv
	make distclean
	python3 foo.py
	make debug

README.pdf: README.md
	pandoc -o README.pdf README.md

.PHONY: clean
clean:
	-rm README.pdf
	-rm -r __pycache__/
	-rm *.pyc

.PHONY: distclean
distclean:
	make clean
	-rm steins.db
	-rm steins.db.?
	-rm steins.db-journal
	-rm steins.log
	-rm steins.log.?
	-rm steins_feed.log
	-rm steins_magic.log

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

.PHONY: create
create: venv
	python3 -c "from model.schema import create_schema; create_schema()"

.PHONY: update
update: venv
	python3 -c "from model.feeds import read_feeds; read_feeds()"

.PHONY: debug
debug: venv
	env FLASK_ENV=development python3 -m flask run

.PHONY: prod
prod: venv
	python3 -m flask run

.PHONY: test
test: venv
	make distclean
	make create
	python3 -m pytest tests

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

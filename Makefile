README.pdf: README.md
	pandoc -o README.pdf README.md

.PHONY: requirements
requirements: requirements.txt
	python3 -m pip install --upgrade -r requirements.txt

.PHONY: create
create:
	python3 -c "from model.schema import create_schema; create_schema()"

.PHONY: update
update:
	python3 -c "from model.feeds import read_feeds; read_feeds()"

.PHONY: debug
debug:
	env FLASK_ENV=development python3 -m flask run

.PHONY: prod
prod:
	python3 -m flask run

.PHONY: test
test:
	make distclean
	make create
	python3 -m pytest tests

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

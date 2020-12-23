.PHONY: run
run: steins.db
	cd ..; php -S localhost:8000

steins.db:
	python3 aux/init_db.py
	php -f aux/init_feeds.php
	python3 aux/update_db.py

README.pdf: README.md
	pandoc -o README.pdf README.md

.PHONY: clean
clean:
	-rm cachegrind.out
	-rm README.pdf
	-rm steins-*.html
	-rm tmp_feeds.xml
	-rm -r __pycache__/
	-rm *.pyc
	-rm [0-9]*

.PHONY: distclean
distclean:
	make clean
	-rm steins.db
	-rm steins.db.?
	-rm steins.db-journal
	-rm steins.log
	-rm steins_feed.log
	-rm steins_magic.log
	-rm -r .venv/


.venv:
	python3 -m venv .venv

.PHONY: venv
venv: .venv
	. .venv/bin/activate

.PHONY: requirements
requirements: requirements.txt venv
	python3 -m pip install --upgrade -r requirements.txt

.PHONY: test
test: venv
	python3 -m pytest tests

.PHONY: run
run: steins.db
	python3 aux/init_feeds.py
	python3 aux/update_db.py
	python3 aux/run_server.py

steins.db:
	python3 aux/init_db.py

.PHONY: test
test:
	make distclean
	make

README.pdf: README.md
	pandoc -o README.pdf README.md

.PHONY: clean
clean:
	-rm README.pdf
	-rm steins-*.html
	-rm tmp_feeds.xml
	-rm -r __pycache__/
	-rm *.pyc
	-find . -name "*.pickle" -print0 | xargs -0 rm

.PHONY: distclean
distclean:
	make clean
	-rm steins.db
	-rm steins.db-journal
	-rm steins.log
	-rm steins_feed.log
	-rm steins_magic.log

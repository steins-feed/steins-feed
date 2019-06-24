.PHONY: run
run:
	python3 main.py

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
	-rm steins.db.0
	-rm steins.db.1
	-rm steins.db-journal
	-rm steins.log
	-rm steins_feed.log
	-rm steins_magic.log

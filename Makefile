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
	-rm *.log
	-rm *.pyc

.PHONY: distclean
distclean:
	make clean
	-rm steins.db

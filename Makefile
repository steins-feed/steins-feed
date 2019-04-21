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
	-rm steins-*.html
	-rm README.pdf
	-rm -r __pycache__/
	-rm *.log
	-rm *.pyc

.PHONY: distclean
distclean:
	make clean
	-rm steins.db

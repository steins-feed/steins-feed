.PHONY: stein
stein:
	python3 main.py --no-write

.PHONY: readme
readme: README.pdf
README.pdf: README.md
	pandoc -o README.pdf README.md

.PHONY: test
test:
	make distclean
	make

.PHONY: clean
clean:
	-rm geckodriver.log
	-rm steins-*.html
	-rm README.pdf
	-rm -r __pycache__/
	-rm *.pyc

.PHONY: distclean
distclean:
	make clean
	-rm steins.db

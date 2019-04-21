.PHONY: stein
stein:
	python3 main.py

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
	-rm steins-*.html
	-rm README.pdf
	-rm -r __pycache__/
	-rm *.log
	-rm *.pyc

.PHONY: distclean
distclean:
	make clean
	-rm steins.db

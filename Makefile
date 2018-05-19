.PHONY: stein
stein:
	python3 main.py

.PHONY: readme
readme: README.pdf
README.pdf: README.md
	pandoc -o README.pdf README.md

.PHONY: clean
clean:
	-rm *.html
	-rm README.pdf
	-rm -r __pycache__/

.PHONY: distclean
distclean:
	make clean
	-rm *.db

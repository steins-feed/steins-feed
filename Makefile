.PHONY: clean
clean:
	-rm *.html
	-rm -r __pycache__/

.PHONY: distclean
distclean:
	make clean
	-rm *.db

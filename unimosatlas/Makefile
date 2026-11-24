# Makefile for Unimosatlas: The Atlas of Hexadecagonal Compositions

BOOK_TEX = unimosatlas.tex
BOOK_PDF = unimosatlas.pdf
BOOK_BASE = unimosatlas

SECS = $(wildcard sec/*.tex)
TKZS = $(wildcard tkz/*.tkz)
PREAMBLE = mosaic_tikz_preamble.tex

.PHONY: all book force clean distclean

all: $(BOOK_PDF)

book: $(BOOK_PDF)

$(BOOK_PDF): $(BOOK_TEX) $(SECS) $(TKZS) $(PREAMBLE)
	pdflatex -interaction=nonstopmode $(BOOK_TEX)
	pdflatex -interaction=nonstopmode $(BOOK_TEX)
	@echo "✓ Successfully compiled Coffee Table Book: $(BOOK_PDF)"

clean:
	rm -f $(BOOK_BASE).aux $(BOOK_BASE).log $(BOOK_BASE).out $(BOOK_BASE).bbl $(BOOK_BASE).blg $(BOOK_BASE).toc $(BOOK_BASE).fls $(BOOK_BASE).fdb_latexmk
	@echo "✓ Cleaned intermediate LaTeX build files."

distclean: clean
	rm -f $(BOOK_PDF)
	@echo "✓ Removed $(BOOK_PDF)."

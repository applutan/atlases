# Makefile for Hexadecality Coffee Table Book & Technical Meta-Paper

BOOK_TEX = hexadecality.tex
BOOK_PDF = hexadecality.pdf
BOOK_BASE = hexadecality

META_TEX = hexadecality_meta.tex
META_PDF = hexadecality_meta.pdf
META_BASE = hexadecality_meta

SECS = $(wildcard sec/*.tex)
TKZS = $(wildcard tkz/*.tkz)
PREAMBLE = mosaic_tikz_preamble.tex

.PHONY: all book meta force clean distclean

all: $(BOOK_PDF) $(META_PDF)

book: $(BOOK_PDF)

meta: $(META_PDF)

$(BOOK_PDF): $(BOOK_TEX) $(SECS) $(TKZS) $(PREAMBLE)
	pdflatex -interaction=nonstopmode $(BOOK_TEX)
	bibtex $(BOOK_BASE)
	pdflatex -interaction=nonstopmode $(BOOK_TEX)
	pdflatex -interaction=nonstopmode $(BOOK_TEX)
	@echo "✓ Successfully compiled Coffee Table Book: $(BOOK_PDF)"

$(META_PDF): $(META_TEX) $(SECS) $(TKZS) $(PREAMBLE)
	pdflatex -interaction=nonstopmode $(META_TEX)
	bibtex $(META_BASE)
	pdflatex -interaction=nonstopmode $(META_TEX)
	pdflatex -interaction=nonstopmode $(META_TEX)
	@echo "✓ Successfully compiled Technical Meta-Paper: $(META_PDF)"

clean:
	rm -f $(BOOK_BASE).aux $(BOOK_BASE).log $(BOOK_BASE).out $(BOOK_BASE).bbl $(BOOK_BASE).blg $(BOOK_BASE).toc $(BOOK_BASE).fls $(BOOK_BASE).fdb_latexmk
	rm -f $(META_BASE).aux $(META_BASE).log $(META_BASE).out $(META_BASE).bbl $(META_BASE).blg $(META_BASE).toc $(META_BASE).fls $(META_BASE).fdb_latexmk
	@echo "✓ Cleaned intermediate LaTeX build files."

distclean: clean
	rm -f $(BOOK_PDF) $(META_PDF)
	@echo "✓ Removed $(BOOK_PDF) and $(META_PDF)."

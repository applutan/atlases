# Makefile for An Atlas of Composition Mosaics (Z_1..Z_8)

MAIN = allmosatlas
PDF = allmosatlas.pdf
PLATES = plates/plates_z1_z8.pdf

.PHONY: all plates pdf clean distclean

all: $(PDF)

plates: $(PLATES)

$(PLATES): plates/plates_z1_z8.tex
	cd plates && pdflatex -interaction=batchmode plates_z1_z8.tex

$(PDF): $(MAIN).tex $(PLATES) sec/*.tex gen/*.tex
	latexmk -pdf -interaction=nonstopmode $(MAIN).tex
	@echo "✓ Successfully compiled $(PDF)"

clean:
	rm -f $(MAIN).aux $(MAIN).log $(MAIN).out $(MAIN).toc $(MAIN).bbl $(MAIN).blg $(MAIN).fls $(MAIN).fdb_latexmk
	cd plates && rm -f plates_z1_z8.aux plates_z1_z8.log plates_z1_z8.out

distclean: clean
	rm -f $(PDF) $(PLATES)

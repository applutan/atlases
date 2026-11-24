all: pdf

pdf:
	latexmk -pdf -interaction=nonstopmode polyatlas.tex

clean:
	latexmk -C polyatlas.tex
	rm -f gen/*.aux gen/*.log

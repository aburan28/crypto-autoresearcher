# Shared build rules for every paper under papers/.  A paper's Makefile sets
#   TEX      := main.tex            (the root document)
#   SECTIONS := sec-a.tex sec-b.tex (files \input by the root; may be empty)
#   BIB      := refs.bib            (bibliography; leave empty when there is none)
#   ASSETS   := figures/a.pdf       (optional: figures, generated tables, .cls/.sty
#                                    and anything else the build reads; paths may
#                                    be in subdirectories and keep them in bundles)
# and then `include ../paper.mk`.
#
# Targets:
#   make             — build the PDF (pdflatex, bibtex when BIB is set, two more passes)
#   make check       — rebuild from scratch, then fail on LaTeX errors, unresolved
#                      references or citations, and overfull boxes
#   make arxiv       — arxiv-submission.tar.gz (sources only; arXiv compiles server-side)
#   make eprint      — eprint-submission.zip (PDF plus sources)
#   make deanonymize — restore the author block from an untracked AUTHORS file
#   make clean       — remove build artefacts (keeps the committed PDF)

PDF      := $(TEX:.tex=.pdf)
STEM     := $(TEX:.tex=)
LOG      := $(STEM).log
AUX      := $(STEM).aux $(STEM).log $(STEM).out $(STEM).toc $(STEM).bbl $(STEM).blg \
            $(STEM).lof $(STEM).lot $(STEM).fls $(STEM).fdb_latexmk $(STEM).synctex.gz
ARXIV_TARBALL := arxiv-submission.tar.gz
EPRINT_ZIP    := eprint-submission.zip
EXTRA    ?= abstract.txt README.md Makefile
ASSETS   ?=

# Copy the given files into a staging directory, keeping their relative
# paths, so \input{sections/a.tex} and figures/a.pdf still resolve there.
copy_tree = tar cf - $(1) | (cd $(2) && tar xf -)
SOURCES  = $(TEX) $(SECTIONS) $(BIB) $(ASSETS)

.PHONY: all clean arxiv eprint deanonymize check

all: $(PDF)

$(PDF): $(TEX) $(SECTIONS) $(BIB) $(ASSETS)
	pdflatex -interaction=nonstopmode $(TEX) || true
	$(if $(BIB),bibtex $(STEM),@true)
	pdflatex -interaction=nonstopmode $(TEX) || true
	pdflatex -interaction=nonstopmode $(TEX)

clean:
	rm -f $(AUX)
	rm -f $(ARXIV_TARBALL) $(EPRINT_ZIP)
	rm -rf submission-staging/

arxiv: $(TEX) $(SECTIONS) $(BIB) $(ASSETS)
	mkdir -p submission-staging/arxiv
	$(call copy_tree,$(SOURCES) $(EXTRA),submission-staging/arxiv)
	cp ../paper.mk submission-staging/arxiv/
	cd submission-staging/arxiv && tar czf ../../$(ARXIV_TARBALL) *
	rm -rf submission-staging/arxiv
	@echo "arXiv submission bundle ready: $(ARXIV_TARBALL)"

eprint: $(PDF)
	mkdir -p submission-staging/eprint
	$(call copy_tree,$(PDF) $(SOURCES) $(EXTRA),submission-staging/eprint)
	cp ../paper.mk submission-staging/eprint/
	cd submission-staging/eprint && zip -qr ../../$(EPRINT_ZIP) *
	rm -rf submission-staging/eprint
	@echo "IACR ePrint submission bundle ready: $(EPRINT_ZIP)"

deanonymize: $(TEX)
	@if [ ! -f AUTHORS ]; then \
	  echo "ERROR: AUTHORS file missing; copy ../AUTHORS.example to AUTHORS and edit it"; exit 1; fi
	@cp $(TEX) $(TEX).anon-backup
	@python3 -c 'import re; \
tex = open("$(TEX)").read(); \
authors = open("AUTHORS").read().strip(); \
tex = re.sub(r"\\author\{Anonymous\}\s*\\date\{[^}]*\}", authors + "\n", tex, count=1); \
open("$(TEX)", "w").write(tex); \
print("De-anonymized $(TEX); backup saved as $(TEX).anon-backup")'

# A committed PDF can look up to date on a fresh checkout while its log is
# absent (logs are ignored), so check always rebuilds and refuses to judge a
# missing log.
check:
	$(MAKE) --no-print-directory --always-make $(PDF)
	@echo "Checking $(PDF)..."
	@if [ ! -s $(LOG) ]; then echo "FAIL: no LaTeX log $(LOG); the build did not run"; exit 1; fi
	@if grep -q '^!' $(LOG); then echo "FAIL: LaTeX errors"; grep -A3 '^!' $(LOG) | head -20; exit 1; fi
	@if grep -q 'LaTeX Warning: There were undefined references' $(LOG); then \
	  echo "FAIL: unresolved references"; grep 'LaTeX Warning: Reference' $(LOG) || true; exit 1; \
	else echo "All references resolved."; fi
	@if grep -qE '(LaTeX|Package natbib) Warning: There were undefined citations' $(LOG); then \
	  echo "FAIL: unresolved citations"; exit 1; fi
	@if grep -E 'Overfull \\[hv]box' $(LOG); then echo "FAIL: overfull boxes"; exit 1; \
	else echo "No overfull boxes."; fi
	@echo "Page count:"; pdfinfo $(PDF) | grep -i pages; ls -lh $(PDF)

# SRC-DCP-SIMON-2026 — frozen external source

Daniel R. Simon, *A Polynomial-Time Quantum Algorithm for the Dihedral Coset
Problem* **[Preliminary Draft]**, IACR ePrint 2026/1591.
Draft dated 2026-07-31; received 2026-08-03; approved 2026-08-06.

- `source_record.yaml` — provenance, hashes, extraction defects, scope of assessment.
- `paper_extracted_text.txt` — automated text extraction of the 16-page PDF.

## Read this before quoting the text file

The extraction is **lossy for mathematics**. `pypdfium2` linearises
superscripts, subscripts and display equations, so `2^{n+1}`, `z*_h`, and
`\sum_{i} y_i(x_i + b_i d)` are all broken across lines in ways that change
what they appear to say. The file is committed so the claim text is
*archived and greppable*, not so formulas can be lifted from it.

**Any formula, exponent, or complexity bound taken from this file must be
re-read against the source PDF** (sha256 `e62fad01…1dbd7b`, re-fetchable from
`https://eprint.iacr.org/2026/1591.pdf`) before it enters an argument.

## What this record does and does not assert

It asserts that these are the bytes Simon published, and that the metadata in
`source_record.yaml` matches the eprint landing page as of 2026-08-06.

It asserts **nothing about whether the algorithm works.** The draft is days
old, its four substantive lemmas are labelled "(Sketch)", and no independent
verification existed when this was frozen. The corpus's assessment lives in
`knowledge/literature/KN-LIT-e204ab.md`; the specific things that would have
to be checked live in `knowledge/open-problems/KN-OPEN-8a5965.md`.

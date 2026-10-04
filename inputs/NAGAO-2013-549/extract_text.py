#!/usr/bin/env python3
"""Regenerate paper_fulltext.md from the frozen PDF in this directory.

Same extractor and LAParams as `inputs/NAGAO-2015-984/extract_text.py` and
`inputs/SEMAEV-2015-310/extract_text.py`, on purpose: this paper is the source of
Lemma 3 and Lemma 5 of Nagao 2015/984, the three texts are read side by side, and
a difference between two of them should mean a difference between the papers
rather than between two extractors.

Usage: python3 extract_text.py  (writes paper_fulltext.md next to the PDF)
Requires: pdfminer.six
"""

from __future__ import annotations

import pathlib

from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams

HERE = pathlib.Path(__file__).resolve().parent
PDF = HERE / "eprint-2013-549.pdf"
OUT = HERE / "paper_fulltext.md"

LAPARAMS = dict(line_margin=0.3, char_margin=2.0, boxes_flow=0.5,
                detect_vertical=False)

HEADER = """<!--
Extracted from inputs/NAGAO-2013-549/eprint-2013-549.pdf (sha256 in the .sha256
sidecar) on 2026-09-13 by this directory's extract_text.py, using pdfminer.six
with LAParams(line_margin=0.3, char_margin=2.0, boxes_flow=0.5). Derivative text
extraction, vendored under the paper's CC BY license
(https://creativecommons.org/licenses/by/4.0/) with attribution to Koh-ichi
Nagao.

NOT hand-cleaned, and the extraction of THIS paper is materially worse than the
2015/984 one: the manuscript is a draft that typesets vectors as overset arrows,
so pdfminer emits the arrow accents as separate lines and the displayed formulas
in Sections 2-3 interleave with them. Read the PDF alongside this file for any
formula that matters; this text is a searchable index of the paper, not a
substitute for it. Ligature and math artifacts are left as produced.

WHY THIS PAPER IS FROZEN. Nagao 2015/984 -- whose Theorem 1 claims ECDLP over
F_{2^n} in O(n^{8w+1}) and which GOAL-SEMBIN-fcb7a2 audits -- cites this paper as
[11] for Lemma 3, and declines to reproduce its proof: "Proof of this Lemma is
complicated and not constructive". Lemma 3 is what licenses replacing the true
first fall degree d_F by the FAKE one d'_F taken modulo the field equations, and
the fake one is the only quantity a Macaulay-rank instrument can compute. So the
instrument EXP-SEMBIN-4fa22c builds rests on a lemma proved here and nowhere the
program had read. IDEA-20260913-352163 recorded that as a disclosed limitation
with the pointer unread; this freeze is the step that converts the pointer into a
source an agent has actually opened.

Landing-page metadata, transcribed 2026-09-13 (see provenance.json):
  title      Equations System coming from Weil descent and subexponential attack
             for algebraic curve cryptosystem
  category   Foundations;  Publication info: Preprint. MINOR revision.
  keywords   Decomposition Attack, ECDLP, first fall degree
  history    2013-11-05: last of 2 revisions;  2013-09-04: received
  licence    CC BY;  short URL https://ia.cr/2013/549

The served PDF is the LAST of two revisions. The abstract's own revision note
records that the first version's Section 3 estimate was wrong for the stated aim
and had to be repaired by replacing a monomial by a polynomial in (X_i - tau);
that note is reproduced in the text below and is a fact about this source, not a
judgement of it.
-->

"""


def main() -> None:
    text = extract_text(str(PDF), laparams=LAParams(**LAPARAMS))
    OUT.write_text(HEADER + text, encoding="utf-8")
    print(f"wrote {OUT} ({len(text)} extracted chars)")


if __name__ == "__main__":
    main()

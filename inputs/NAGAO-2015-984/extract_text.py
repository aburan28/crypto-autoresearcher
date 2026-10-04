#!/usr/bin/env python3
"""Regenerate paper_fulltext.md from the frozen PDF in this directory.

Same extractor and LAParams as `inputs/SEMAEV-2015-310/extract_text.py`, on
purpose: this paper is a commentary on that one, the two are read side by side,
and a difference between the two texts should mean a difference between the two
papers rather than a difference between two extractors.

Usage: python3 extract_text.py  (writes paper_fulltext.md next to the PDF)
Requires: pdfminer.six
"""

from __future__ import annotations

import pathlib

from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams

HERE = pathlib.Path(__file__).resolve().parent
PDF = HERE / "eprint-2015-984.pdf"
OUT = HERE / "paper_fulltext.md"

LAPARAMS = dict(line_margin=0.3, char_margin=2.0, boxes_flow=0.5,
                detect_vertical=False)

HEADER = """<!--
Extracted from inputs/NAGAO-2015-984/eprint-2015-984.pdf (sha256 in the .sha256
sidecar) on 2026-09-13 by this directory's extract_text.py, using pdfminer.six
with LAParams(line_margin=0.3, char_margin=2.0, boxes_flow=0.5). Derivative text
extraction, vendored under the paper's CC BY license
(https://creativecommons.org/licenses/by/4.0/) with attribution to Koh-ichi
Nagao.

NOT hand-cleaned. Ligature and math artifacts from the PDF's fonts are left as
the extractor produced them: `fi`/`ff`/`fl` ligatures, `Gr¨obner`, `⁄=` for the
non-equality sign in Definition 5, and superscripts and summation limits
flattened onto the baseline (so displayed formulas break across lines).

Section, equation, definition, lemma, proposition and theorem numbers below are
the paper's own and are the citable anchors. The load-bearing ones for this
program:

  Definition 2  EQS1(m,R) -- Semaev's chained S_3 system, m-1 links
  Definition 4  EQS2(m,R) -- its Weil descent, n(m-1) variables
  Definition 5  first fall degree d_F, the TRUE definition
  Definition 6  FAKE first fall degree d'_F, reduced mod the field equations
  Assumption 1  degree in the F4 computation is <= d_F  (Nagao's numbering)
  Lemma 3/4     d_F <= d'_F, so the fake version is a safe upper bound
  Lemma 6       first fall degree of a Weil descent is <= (p-1)n + deg F
  Prop. 2       d_F(EQS2) <= 4 (p = 2), <= 3p+1 (p >= 3)
  Section 7     DISJOINT (coset) factor base: Fb_i = {P : x(P) in V + v_i}
  Definition 7  EQS3(m,R) -- the chained system over disjoint cosets
  Definition 8  EQS4(m,R) -- its Weil descent
  Prop. 5       d_F(EQS4) <= 4 (p = 2), <= 3p+1 (p >= 3), stated with the
                proof OMITTED ("the situation is the same as the Semaev's
                case"). This is the paper's load-bearing unproven step.
  Theorem 1     under the first fall degree assumption, ECDLP over F_{p^n}
                costs O(n^{8w+1}) for p = 2 and O(n^{(6p+2)w+1}) for p >= 3

Reference [14] of this paper is Semaev ePrint 2015/310, frozen at
inputs/SEMAEV-2015-310/. Reference [5] is Galbraith-Gebregiyorgis ePrint
2014/806. Section 7's opening sentence credits the disjoint factor base to the
author's own [10] (ePrint 2013/548) and says [5] re-discovered it.
-->

"""


def main() -> None:
    text = extract_text(str(PDF), laparams=LAParams(**LAPARAMS))
    OUT.write_text(HEADER + text, encoding="utf-8")
    print(f"wrote {OUT} ({len(text)} extracted chars)")


if __name__ == "__main__":
    main()

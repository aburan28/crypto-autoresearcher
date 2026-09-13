#!/usr/bin/env python3
"""Regenerate paper_fulltext.md from the frozen PDF in this directory.

Same extractor and LAParams as `inputs/NAGAO-2015-984/extract_text.py` and
`inputs/SEMAEV-2015-310/extract_text.py`, on purpose: 2015/984 credits this paper
with the disjoint factor base, the two are read side by side, and a difference
between the texts should mean a difference between the papers rather than between
two extractors.

Usage: python3 extract_text.py  (writes paper_fulltext.md next to the PDF)
Requires: pdfminer.six
"""

from __future__ import annotations

import pathlib

from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams

HERE = pathlib.Path(__file__).resolve().parent
PDF = HERE / "eprint-2013-548.pdf"
OUT = HERE / "paper_fulltext.md"

LAPARAMS = dict(line_margin=0.3, char_margin=2.0, boxes_flow=0.5,
                detect_vertical=False)

HEADER = """<!--
Extracted from inputs/NAGAO-2013-548/eprint-2013-548.pdf (sha256 in the .sha256
sidecar) on 2026-09-13 by this directory's extract_text.py, using pdfminer.six
with LAParams(line_margin=0.3, char_margin=2.0, boxes_flow=0.5). Derivative text
extraction, vendored under the paper's CC BY license
(https://creativecommons.org/licenses/by/4.0/) with attribution to Koh-ichi
Nagao. NOT hand-cleaned; arrow accents and displayed formulas break across lines
as the extractor produced them.

WHY THIS PAPER IS FROZEN, AND THE ONE QUESTION IT IS FROZEN TO ANSWER. Section 7
of Nagao 2015/984 opens by crediting the DISJOINT (coset) factor base to this
paper -- its reference [10] -- and says Galbraith and Gebregiyorgis ePrint
2014/806 "recently re-discovered" it. This program's own mechanism-lane
hypothesis H-SEMBIN-c59e50 was built on 2014/806, so the priority sentence bears
directly on what that lane may claim as new. IDEA-20260913-352163 recorded the
priority question as NOT settled by 2015/984 asserting it, and left the pointer
unread. This freeze is the step that lets an agent check the sentence against the
cited text rather than against the citing author's summary of it.

Read the priority question against what this paper is actually about: its own
title and abstract are a decomposition formula for the Jacobian group of a plane
curve, and its revision note records that Proposition 3 of the first version "is
not true and this technique can not be used", forcing Section 4 to be rewritten.
Whether a disjoint/coset factor base for the elliptic case appears here at all,
and if so where, is the reading task -- not something this header decides.

Landing-page metadata, transcribed 2026-09-13 (see provenance.json):
  title      Decomposition formula of the Jacobian group of plane curve
  category   Foundations;  Publication info: Preprint. MINOR revision.
  keywords   Decomposition Attack, ECDLP
  history    2013-12-13: last of 3 revisions;  2013-09-04: received
  licence    CC BY;  short URL https://ia.cr/2013/548

The served PDF is the LAST of three revisions, so it is not necessarily the text
2015/984 read in 2015; the versions ePrint retains are listed on the landing page
and none of the earlier ones is frozen here.
-->

"""


def main() -> None:
    text = extract_text(str(PDF), laparams=LAParams(**LAPARAMS))
    OUT.write_text(HEADER + text, encoding="utf-8")
    print(f"wrote {OUT} ({len(text)} extracted chars)")


if __name__ == "__main__":
    main()

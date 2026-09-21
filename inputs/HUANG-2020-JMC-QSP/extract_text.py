#!/usr/bin/env python3
"""Regenerate paper_fulltext.md from the frozen PDF in this directory.

Same extractor and LAParams as inputs/SEMAEV-2015-310/ and inputs/NAGAO-2015-984/,
on purpose: the quasi-subfield papers are read against the Semaev/Nagao lane's
frozen sources, and a textual difference between files should mean a difference
between papers rather than between extractors.

Usage: python3 extract_text.py  (writes paper_fulltext.md next to the PDF)
Requires: pdfminer.six
"""

from __future__ import annotations

import hashlib
import pathlib

from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams

HERE = pathlib.Path(__file__).resolve().parent
PDF = HERE / "huang-et-al-jmc-2020-qsp.pdf"
OUT = HERE / "paper_fulltext.md"

LAPARAMS = dict(line_margin=0.3, char_margin=2.0, boxes_flow=0.5,
                detect_vertical=False)

HEADER = """<!--
Extracted from inputs/HUANG-2020-JMC-QSP/huang-et-al-jmc-2020-qsp.pdf (sha256 in the .sha256
sidecar) on 2026-09-16 by this directory's extract_text.py, using pdfminer.six
with LAParams(line_margin=0.3, char_margin=2.0, boxes_flow=0.5,
detect_vertical=False). Derivative text extraction vendored under
the paper's CC BY 4.0 licence (https://creativecommons.org/licenses/by/4.0/), stated on the publisher's first page and on the Birmingham repository cover sheet,
with attribution to Ming-Deh Huang, Michiel Kosters, Christophe Petit, Sze Ling Yeo and Yang Yun.

NOT hand-cleaned. Ligatures, superscripts flattened onto the baseline, displayed
formulas broken across lines, and (cid:NN) glyph placeholders are left exactly as
the extractor produced them. Section, lemma, proposition, theorem and remark
numbers are the paper's own and are the citable anchors.
-->

"""


def main() -> None:
    text = extract_text(str(PDF), laparams=LAParams(**LAPARAMS))
    OUT.write_text(HEADER + text, encoding="utf-8")
    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    (HERE / "paper_fulltext.md.sha256").write_text(f"{digest}  paper_fulltext.md\n")
    print(f"wrote {OUT} ({len(text)} chars) sha256 {digest}")


if __name__ == "__main__":
    main()

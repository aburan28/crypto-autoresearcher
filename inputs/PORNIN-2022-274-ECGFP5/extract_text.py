#!/usr/bin/env python3
"""Regenerate paper_fulltext.md from the frozen PDF in this directory."""

from __future__ import annotations

import hashlib
import pathlib

from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams

HERE = pathlib.Path(__file__).resolve().parent
PDF = HERE / "eprint-2022-274.pdf"
OUT = HERE / "paper_fulltext.md"

LAPARAMS = dict(line_margin=0.3, char_margin=2.0, boxes_flow=0.5,
                detect_vertical=False)

HEADER = """<!--
Extracted from inputs/PORNIN-2022-274-ECGFP5/eprint-2022-274.pdf (sha256 in the
.sha256 sidecar) on 2026-09-20 by this directory's extract_text.py, using
pdfminer.six with LAParams(line_margin=0.3, char_margin=2.0, boxes_flow=0.5,
detect_vertical=False). Derivative text extraction vendored under ePrint
terms with attribution to Thomas Pornin, EcGFp5: a Specialized Elliptic Curve,
IACR ePrint 2022/274.

NOT hand-cleaned. Ligatures, superscripts flattened onto the baseline, displayed
formulas broken across lines, and (cid:NN) glyph placeholders are left exactly as
the extractor produced them. Section numbers are the paper's own and are the
citable anchors.
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

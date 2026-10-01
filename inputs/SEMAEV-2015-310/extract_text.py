#!/usr/bin/env python3
"""Regenerate paper_fulltext.md from the frozen PDF in this directory.

`pdftotext -layout` -- the extractor used for the other frozen sources in
`inputs/` -- was unavailable in the session that froze this package (no
poppler-utils package on the image), so extraction uses pdfminer.six instead.
The two are not byte-identical: pdfminer reflows some multi-column table bodies
into per-column runs, which is why Tables 1-3 are additionally transcribed
row-wise into `tables.yaml`.

Usage: python3 extract_text.py  (writes paper_fulltext.md next to the PDF)
Requires: pdfminer.six
"""

from __future__ import annotations

import pathlib

from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams

HERE = pathlib.Path(__file__).resolve().parent
PDF = HERE / "eprint-2015-310.pdf"
OUT = HERE / "paper_fulltext.md"

# Recorded so a later re-extraction is comparable rather than merely similar.
LAPARAMS = dict(line_margin=0.3, char_margin=2.0, boxes_flow=0.5, detect_vertical=False)

HEADER = """<!--
Extracted from inputs/SEMAEV-2015-310/eprint-2015-310.pdf (sha256 in the
.sha256 sidecar) on 2026-09-13 by this directory's extract_text.py, using
pdfminer.six with LAParams(line_margin=0.3, char_margin=2.0, boxes_flow=0.5).
Derivative text extraction, vendored under the paper's CC BY 4.0 license
(https://creativecommons.org/licenses/by/4.0/) with attribution to Igor Semaev.

NOT hand-cleaned. Ligature and math artifacts from the PDF's Type-1 fonts are
left as the extractor produced them: `ﬁ`/`ﬀ`/`ﬂ` ligatures, `(cid:100)x(cid:101)`
for the ceiling brackets in k = ceil(n/m), `Gr¨obner`, and superscripts flattened
onto the baseline (so "2 c sqrt(n ln n)" appears broken across lines in the
abstract). Tables 1-3 are reflowed by column rather than by row; use
`tables.yaml` in this directory for the row-wise transcription.

Section and equation numbers below are the paper's own and are the citable
anchors: Assumption 1 (Section 4.5, d_F4 <= 4), Assumption 2 (Section 4.6,
d_F4 = o(sqrt(n/ln n))), the success-probability model (Section 4.3, eq. 11),
the chained S_3 system (eq. 5), and the two-stage cost balance (eqs. 15-17).
-->

"""


def main() -> None:
    text = extract_text(str(PDF), laparams=LAParams(**LAPARAMS))
    OUT.write_text(HEADER + text, encoding="utf-8")
    print(f"wrote {OUT} ({len(text)} extracted chars)")


if __name__ == "__main__":
    main()

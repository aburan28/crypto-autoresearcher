"""Derive paper_fulltext.md from the frozen PDF with pypdf (page text only; display
equations are typeset as separate glyph runs in this 1996 FrameMaker PDF and come out
as fragments after the paragraph that references them -- read the prose and the
equation numbers, and re-derive formulas from the prose where the fragments are
ambiguous)."""
import hashlib, sys
from pypdf import PdfReader
src = 'vow-pcs-1996.pdf'
r = PdfReader(src)
parts = []
for i, p in enumerate(r.pages, 1):
    parts.append(f"\n\n<!-- page {i} -->\n\n" + (p.extract_text() or ''))
head = ("# Parallel Collision Search with Cryptanalytic Applications\n\n"
        "Paul C. van Oorschot and Michael J. Wiener, 1996-09-23 preprint (author-posted; published "
        "J. Cryptology 12(1):1-28, 1999, doi:10.1007/PL00003816).\n\n"
        f"Derived text of inputs/VOW-1996-PCS/{src} (sha256 {hashlib.sha256(open(src,'rb').read()).hexdigest()}) "
        f"via pypdf {__import__('pypdf').__version__}. Equations are fragmentary; see extract_text.py.\n")
open('paper_fulltext.md', 'w').write(head + ''.join(parts) + '\n')
print('pages', len(r.pages))

"""Derive paper_fulltext.md from the frozen arXiv v1 PDF with pypdf (page text only).

TASK-20261003-a19c53. Display equations and inline mathematics are typeset by LaTeX
as separate glyph runs and may come out as glyph fragments, split across lines, or
with symbols dropped/replaced. Quote the prose; never reconstruct a formula from the
fragments without marking it as a reconstruction.

Run from this directory: python extract_text.py
Environment that produced the frozen paper_fulltext.md: a scratch venv (the system
Python had no pypdf) with pypdf==6.19.0 and fonttools==4.66.1. fontTools changes
the CFF font decoding: without it the output differs (sha256 12cbc0c2...dcb1,
mostly in large-delimiter glyphs and inter-word spacing around math), so pin both.
"""
import hashlib
import pypdf
from pypdf import PdfReader

src = 'hhan-2024-2402.11269v1.pdf'
r = PdfReader(src)
parts = []
for i, p in enumerate(r.pages, 1):
    parts.append(f"\n\n<!-- page {i} -->\n\n" + (p.extract_text() or ''))
head = ("# A New Approach to Generic Lower Bounds: Classical/Quantum MDL, Quantum Factoring, and More\n\n"
        "Minki Hhan, arXiv:2402.11269v1 (submitted 2024-02-17; CC BY 4.0).\n\n"
        f"Derived text of inputs/HHAN-2024-2402.11269/{src} (sha256 "
        f"{hashlib.sha256(open(src, 'rb').read()).hexdigest()}) via pypdf {pypdf.__version__}. "
        "Equations are fragmentary; see extract_text.py.\n")
with open('paper_fulltext.md', 'w', encoding='utf-8') as f:
    f.write(head + ''.join(parts) + '\n')
print('pages', len(r.pages))

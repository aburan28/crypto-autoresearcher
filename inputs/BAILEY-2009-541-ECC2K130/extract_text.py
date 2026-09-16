"""Derive page text from the three frozen PDFs (PyMuPDF page text only).

Produces paper_fulltext.md, talk-ecc2010_text.md and talk-35minutes_text.md next to
the PDFs. Display math in the paper (2^60.9, 2^25.27, sums over sigma^i) comes out
with superscripts flattened ("260.9"), so read exponents from the prose context.
The two talk decks are Beamer overlays: every incremental build of a slide is a
separate page, so slide text repeats; the "Reports so far" tallies are the last
overlay of that slide in each deck.
"""
import hashlib
import pymupdf

SOURCES = [
    ("ecc2k130-2009-541.pdf", "paper_fulltext.md",
     "Breaking ECC2K-130 (Bailey et al.), IACR ePrint 2009/541, PDF as served 2026-09-16"),
    ("lange-ecc2010-talk.pdf", "talk-ecc2010_text.md",
     "Tanja Lange, 'Breaking ECC2K-130' talk deck (server tallies dated 2010.10.22)"),
    ("lange-35minutes-talk.pdf", "talk-35minutes_text.md",
     "Tanja Lange, 'Attacking Elliptic Curve Challenges' 35-minute deck (server tallies dated 2010.09.07)"),
]
for src, out, title in SOURCES:
    doc = pymupdf.open(src)
    sha = hashlib.sha256(open(src, "rb").read()).hexdigest()
    parts = [f"# {title}\n\nDerived text of inputs/BAILEY-2009-541-ECC2K130/{src} (sha256 {sha}) "
             f"via PyMuPDF {pymupdf.version[0]}; {len(doc)} pages. See extract_text.py.\n"]
    for i, page in enumerate(doc, 1):
        parts.append(f"\n\n<!-- page {i} -->\n\n" + page.get_text())
    open(out, "w").write("".join(parts) + "\n")
    print(out, len(doc), "pages")

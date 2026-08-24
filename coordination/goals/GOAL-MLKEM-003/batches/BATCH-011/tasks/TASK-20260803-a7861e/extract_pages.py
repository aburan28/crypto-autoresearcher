#!/usr/bin/env python3
"""TASK-20260803-a7861e / BATCH-011 / GOAL-MLKEM-003.

Read-only text extraction from the vendored Carrier et al. PDF, for the single
purpose of settling validator defect D7: where does the source place the d_lsc
integral relative to min(1,.), and are Phi_{d_lsc} and alpha defined anywhere in
the document?

ZERO NEW SAMPLING, NO NETWORK. The only input is the immutable vendored PDF
under experiments/EXP-MLKEM-010/vendor-lock/, which this script opens READ-ONLY
and never writes to. By default the script writes NOTHING to disk: it prints the
extracted text to stdout. `--outdir DIR` optionally dumps per-page text files
(used here only into a scratch directory outside the repository).

Two independent pypdf extraction modes are printed for every page:
  * "plain"  - pypdf's default extract_text(); preserves the PDF's text-object
               order, so a display formula comes out as one token per line.
  * "layout" - pypdf's extraction_mode="layout"; preserves horizontal position,
               so the nesting of a display formula is visible in 2D.
Agreement between the two modes is what makes a nesting claim (e.g. "the min's
argument closes before the Gaussian factor") checkable rather than asserted.

C0 control bytes (0x00-0x1f) appear in the plain-mode text wherever a math-font
glyph carries no Unicode mapping (in this document these sit at the scaled
delimiters of display formulas). They are NOT stripped: they are rendered as
<U+00XX> so that the printed text is a faithful, reversible transcription.

Usage:
    python3 extract_pages.py                       # print everything to stdout
    python3 extract_pages.py --outdir /some/scratch # also dump per-page files
    python3 extract_pages.py --pages 23 25          # restrict the page set
"""

import argparse
import hashlib
import os
import platform
import re
import subprocess
import sys
import datetime

PDF_REPO_PATH = "experiments/EXP-MLKEM-010/vendor-lock/Carrier-2022-1750-hal-05406481.pdf"
EXPECTED_SHA256 = "083b142256eecaebfa72dfccf847151b2175666a3979cef4e7383376757b8005"

# 1-based PDF page indices. The document's printed page number is the PDF index
# minus one throughout (verified by the trailing folio on every page; see the
# FOLIO CHECK section of the output).
PAGES_OF_INTEREST = {
    9: "Definition 2.3 (Centered Binomial Distribution) - candidate locus for alpha",
    20: "Approximation 4.6 = (4.9); (4.10) defines Phi_{d_lsc}; (4.11) defines Upsilon_n",
    23: "(4.17), Model 4.7 = (4.18) defining D, Approximation 4.8 = (4.19)-(4.20), "
        "Approximation 4.9 = (4.21)-(4.22), (4.23) E(T-t), (4.24) lambda/mu  <-- D7 page",
    24: "Justification of Approximation 4.8; alpha enters via sqrt(alpha/2) chi",
    25: "Justification of Approximation 4.9 = (4.26)-(4.29) and the closing "
        "P(D>T) = INT psi_lsc(d) P(D>T|d) dd display",
    26: "Figure 4.1 caption - parameters of the two archived toy runs",
    28: "Table 5.1 - numeric alpha per Kyber parameter set",
    36: "Appendix B - restates alpha as the centered-binomial parameter",
}


def escape_c0(s: str) -> str:
    """Render C0 control bytes visibly and reversibly; leave all else alone."""
    return re.sub(r"[\x00-\x08\x0b-\x1f]", lambda m: "<U+%04X>" % ord(m.group()), s)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", default=None, help="path to the vendored PDF")
    ap.add_argument("--pages", nargs="*", type=int, default=None,
                    help="1-based PDF page indices (default: the D7 page set)")
    ap.add_argument("--outdir", default=None,
                    help="optional directory for per-page dumps; nothing is "
                         "written to disk when omitted")
    args = ap.parse_args()

    # this file lives at
    # <root>/coordination/goals/<GOAL>/batches/<BATCH>/tasks/<TASK>/extract_pages.py
    # so the repository root is seven levels up from the script's directory.
    repo_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                             *([".."] * 7)))
    pdf_path = args.pdf or os.path.join(repo_root, PDF_REPO_PATH)

    import pypdf  # imported after arg parsing so --help works without it

    print("=" * 78)
    print("TASK-20260803-a7861e  extract_pages.py")
    print("generated_at_utc :", datetime.datetime.now(datetime.timezone.utc)
          .strftime("%Y-%m-%dT%H:%M:%SZ"))
    print("python           :", sys.version.replace("\n", " "))
    print("platform         :", platform.platform())
    print("pypdf            :", pypdf.__version__)
    try:
        commit = subprocess.run(["git", "-C", repo_root, "rev-parse", "HEAD"],
                                capture_output=True, text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", repo_root, "status", "--porcelain"],
                               capture_output=True, text=True, check=True).stdout
        print("git_commit       :", commit)
        print("dirty_tree       :", "yes" if dirty.strip() else "no")
        if dirty.strip():
            print("dirty_paths      :", " ".join(sorted(
                l[3:] for l in dirty.splitlines())))
    except Exception as exc:                       # pragma: no cover
        print("git_commit       : UNAVAILABLE (%s)" % exc)

    with open(pdf_path, "rb") as fh:
        blob = fh.read()
    digest = hashlib.sha256(blob).hexdigest()
    print("pdf_path         :", os.path.relpath(pdf_path, repo_root))
    print("pdf_sha256       :", digest)
    print("pdf_sha256_match :", digest == EXPECTED_SHA256)
    if digest != EXPECTED_SHA256:
        print("REFUSING: vendored PDF does not match the expected immutable hash.")
        return 2

    reader = pypdf.PdfReader(pdf_path)
    n_pages = len(reader.pages)
    print("pdf_pages        :", n_pages)

    plain = [(reader.pages[i].extract_text() or "") for i in range(n_pages)]
    layout = [(reader.pages[i].extract_text(extraction_mode="layout") or "")
              for i in range(n_pages)]

    # ---- FOLIO CHECK: printed page number vs 1-based PDF index -------------
    print()
    print("=" * 78)
    print("FOLIO CHECK (last non-blank line of each page = printed folio)")
    for i in range(n_pages):
        tail = [l for l in plain[i].split("\n") if l.strip()]
        print("  pdf page %2d -> last line %r" % (i + 1, tail[-1] if tail else ""))

    # ---- DOCUMENT-WIDE SYMBOL SCAN ----------------------------------------
    print()
    print("=" * 78)
    print("DOCUMENT-WIDE SYMBOL SCAN (plain mode)")
    for sym, label in (("Φ", "Phi (U+03A6)"), ("α", "alpha (U+03B1)")):
        hits = [(i + 1, plain[i].count(sym)) for i in range(n_pages) if sym in plain[i]]
        print("  %-14s pages: %s" % (label, hits))
    min_hits = [(i + 1, ln) for i in range(n_pages)
                for ln, line in enumerate(plain[i].split("\n"), 1)
                if re.search(r"\bmin\b", line)]
    print("  standalone 'min' at (pdf_page, line): %s" % (min_hits,))

    # ---- PER-PAGE EXTRACTS -------------------------------------------------
    pages = args.pages if args.pages else sorted(PAGES_OF_INTEREST)
    if args.outdir:
        os.makedirs(args.outdir, exist_ok=True)
    for p in pages:
        why = PAGES_OF_INTEREST.get(p, "(page requested on the command line)")
        for mode, texts in (("plain", plain), ("layout", layout)):
            body = escape_c0(texts[p - 1])
            print()
            print("=" * 78)
            print("PDF PAGE %d (printed folio %d) | mode=%s" % (p, p - 1, mode))
            print("why: %s" % why)
            print("-" * 78)
            for ln, line in enumerate(body.split("\n"), 1):
                print("%4d| %s" % (ln, line.rstrip()))
            if args.outdir:
                out = os.path.join(args.outdir, "page%03d_%s.txt" % (p, mode))
                with open(out, "w", encoding="utf-8") as fh:
                    fh.write(texts[p - 1])
    if args.outdir:
        print()
        print("per-page dumps written to %s" % args.outdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

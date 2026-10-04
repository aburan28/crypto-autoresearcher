#!/usr/bin/env python3
"""Audit a frozen paper_fulltext.md against a fresh extraction of its own PDF.

WHY
---
`inputs/NAGAO-2013-549/paper_fulltext.md` renders the hypothesis of Lemma 2's
proof as

    Proof. Fix some monomial order > satisfying
    fi. For a local
    ...
    i when
    i >
    ei >
    X ei
    X fi

The PDF says

    Proof. Fix some monomial order > satisfying  Prod X^{e_i}_i > Prod X^{f_i}_i
    when Sum e_i > Sum f_i.

which is a GRADED order. The extraction did not drop the operators -- the `Prod`
and `Sum` glyphs are in the file -- it DETACHED them from their operands and
scattered them across lines. What survives reads as a per-variable comparison,
which is a different and much weaker hypothesis, and a reader working from the
markdown alone sees a proof resting on nothing.

That is worse than a lost formula. A gap announces itself; a formula that
silently re-reads as a weaker statement does not, and the reader cannot tell the
difference without the PDF.

WHAT THIS TOOL DOES
-------------------
Extracts the PDF again with pymupdf and reports, per display-math region, where
the frozen markdown has separated a large operator from its operands. It is a
DETECTOR and a magnitude estimate, not a repair: the frozen file is immutable and
is never edited. Findings go in an additive errata file beside it.

    python3 tools/audit_frozen_extraction.py inputs/NAGAO-2013-549
    python3 tools/audit_frozen_extraction.py inputs/NAGAO-2013-549 --json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

# Large operators and the relation symbols whose scope they take. When one of
# these ends up alone on a line, its operand is somewhere else in the file.
BIG_OPERATORS = "∑∏∫⋂⋃⨁⨂"
ORPHAN_LINE = re.compile(rf"^\s*[{BIG_OPERATORS}]\s*$")
MATH_SYMBOL = re.compile(r"[0-9=<>+\-•¡¢∑∏^_(){}\[\]/|∈≤≥≠∪∩·′]")
FRAGMENT_MAX_LEN = 18


def looks_like_math_fragment(line: str) -> bool:
    """Is this short line a piece of a shredded formula rather than prose?

    The discriminator matters more than it looks. A plain "short line" rule
    counts ordinary words -- "prose", "Then we have" -- and inflates the run
    count with English, which is how the first version of this tool reported 38
    runs where an honest count is far smaller. A number that cannot be trusted
    is worse than no number, so this deliberately UNDERCOUNTS: a purely
    alphabetic fragment like "Gnew" is missed rather than risk counting words.

    A line qualifies when it is short AND at least one of:
      * it is at most two characters ("i", "d", "N");
      * it contains a digit or a math symbol ("ei >", "i=1", "I1");
      * it contains a single-character alphabetic token, i.e. a bare variable
        ("X ei", "F :=").
    """
    stripped = line.strip()
    if not stripped or len(stripped) > FRAGMENT_MAX_LEN:
        return False
    if len(stripped) <= 2:
        return True
    if MATH_SYMBOL.search(stripped):
        return True
    return any(len(token) == 1 and token.isalpha() for token in stripped.split())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_pdf(pdf: Path) -> str:
    try:
        import pymupdf
    except ImportError:
        try:
            import fitz as pymupdf  # noqa: N813  (older name)
        except ImportError:
            raise SystemExit(
                "pymupdf is required: pip install pymupdf. Note that this "
                "environment has neither pdftotext nor mutool, which is itself "
                "worth recording in an input package's provenance."
            ) from None
    doc = pymupdf.open(pdf)
    return "\n".join(page.get_text() for page in doc)


def orphaned_operators(markdown: str) -> list[dict]:
    """Lines holding a large operator alone, with the context around them."""
    lines = markdown.split("\n")
    found = []
    for i, line in enumerate(lines):
        if ORPHAN_LINE.match(line):
            found.append({
                "line": i + 1,
                "operator": line.strip(),
                "before": [l for l in lines[max(0, i - 3):i] if l.strip()][-2:],
                "after": [l for l in lines[i + 1:i + 4] if l.strip()][:2],
            })
    return found


def fragment_runs(markdown: str, minimum: int = 4) -> list[dict]:
    """Runs of consecutive tiny fragment lines -- a shredded display formula."""
    lines = markdown.split("\n")
    runs, current = [], []
    for i, line in enumerate(lines):
        stripped = line.strip()
        # A BLANK LINE DOES NOT END A RUN. The shredding interleaves blanks
        # between fragments -- lines 685-736 of NAGAO-2013-549 are one formula
        # with a blank line after almost every piece -- so treating a blank as a
        # boundary hides exactly the regions this is looking for.
        if not stripped:
            continue
        if looks_like_math_fragment(line) or stripped in BIG_OPERATORS:
            current.append((i + 1, stripped))
        else:
            if len(current) >= minimum:
                runs.append({
                    "start_line": current[0][0],
                    "end_line": current[-1][0],
                    "length": len(current),
                    "fragments": [f for _, f in current],
                })
            current = []
    if len(current) >= minimum:
        runs.append({
            "start_line": current[0][0],
            "end_line": current[-1][0],
            "length": len(current),
            "fragments": [f for _, f in current],
        })
    return runs


def operator_counts(text: str) -> dict[str, int]:
    return {op: text.count(op) for op in BIG_OPERATORS if text.count(op)}


def audit(package: Path) -> dict:
    md_candidates = list(package.glob("paper_fulltext.md"))
    pdf_candidates = list(package.glob("*.pdf"))
    if not md_candidates or not pdf_candidates:
        raise SystemExit(f"{package} needs paper_fulltext.md and a .pdf")
    md_path, pdf_path = md_candidates[0], pdf_candidates[0]
    markdown = md_path.read_text(errors="replace")
    fresh = extract_pdf(pdf_path)

    orphans = orphaned_operators(markdown)
    runs = fragment_runs(markdown)
    return {
        "package": str(package),
        "frozen_markdown": str(md_path),
        "frozen_markdown_sha256": sha256(md_path),
        "pdf": str(pdf_path),
        "pdf_sha256": sha256(pdf_path),
        "frozen_lines": markdown.count("\n") + 1,
        "fresh_extraction_lines": fresh.count("\n") + 1,
        "large_operators_in_frozen": operator_counts(markdown),
        "large_operators_in_fresh": operator_counts(fresh),
        "orphaned_operator_lines": len(orphans),
        "orphaned_operators": orphans,
        "shredded_formula_runs": len(runs),
        "shredded_formula_lines": sum(r["length"] for r in runs),
        "longest_runs": sorted(runs, key=lambda r: -r["length"])[:5],
        "what_this_measures": (
            "Lines where a large operator stands alone, and runs of tiny fragment "
            "lines. Both are signatures of a display formula whose operands were "
            "separated from their operators. This is a DETECTOR: a flagged region "
            "is not necessarily misleading, and an unflagged region is not "
            "necessarily faithful. It bounds where to look, nothing more."
        ),
        "what_this_does_not_do": (
            "It does not repair the frozen file, which is immutable and hash-pinned, "
            "and it does not decide whether a given mangled hypothesis changes a "
            "proof's meaning. That is a reading task."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("package", type=Path, help="an inputs/<PAPER>/ directory")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = audit(args.package)
    if args.json:
        print(json.dumps(result, indent=1, ensure_ascii=False))
        return 0

    print(f"package: {result['package']}")
    print(f"  frozen markdown: {result['frozen_lines']} lines, "
          f"sha256 {result['frozen_markdown_sha256'][:12]}")
    print(f"  fresh extraction: {result['fresh_extraction_lines']} lines")
    print(f"\n  large operators, frozen: {result['large_operators_in_frozen']}")
    print(f"  large operators, fresh:  {result['large_operators_in_fresh']}")
    print(f"\n  ORPHANED OPERATOR LINES: {result['orphaned_operator_lines']}")
    print(f"  SHREDDED FORMULA RUNS:   {result['shredded_formula_runs']} "
          f"({result['shredded_formula_lines']} lines)")
    if result["longest_runs"]:
        print("\n  worst regions:")
        for run in result["longest_runs"]:
            joined = " | ".join(run["fragments"][:10])
            print(f"    lines {run['start_line']}-{run['end_line']} "
                  f"({run['length']} fragments): {joined}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

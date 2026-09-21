"""Parse-quality checks aimed at mathematical PDFs.

These are heuristics, and they are reported as warnings rather than used to
reject documents: a false positive that blocks a paper is worse than one that
annotates it. They exist because a silently mangled conversion -- a truncated
equation, a two-column page read across the gutter -- produces chunks that
retrieve well and mean nothing, which is the failure mode hardest to notice
downstream. Warnings ride on the manifest so `crypto-kb doctor` can list the
documents a human should look at.
"""

from __future__ import annotations

import re
from collections import Counter

from crypto_kb.models import ParsedDocument

REPLACEMENT_CHAR = "�"

#: Unicode ranges that mark real mathematical content, used to decide whether
#: a document was expected to contain equations at all.
_MATH_HINT = re.compile(r"[∀-⋿Α-ω℀-⅏]|\$[^$\n]{2,}\$|\\\[|\\begin\{")
# `.*?` rather than `.+?`: a display equation whose content was dropped in
# conversion leaves `$$$$`, which is the case this check most needs to catch.
_DISPLAY_MATH = re.compile(r"\$\$(.*?)\$\$|\\\[(.*?)\\\]", re.DOTALL)
_INLINE_MATH = re.compile(r"(?<!\$)\$([^$\n]+)\$(?!\$)")
_HEADING = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
_TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")
_REFERENCE_MARK = re.compile(r"\[(\d{1,3})\]")
_SECTION_NUMBER = re.compile(r"^\s*(\d+(?:\.\d+)*)\s+\S")

#: A markdown line longer than this in a paper is usually a paragraph that
#: swallowed a heading, or two columns joined.
_LONG_LINE = 2000


def validate_parse(document: ParsedDocument, key: str) -> list[str]:
    """Return human-readable warnings about a conversion."""
    text = document.markdown
    warnings: list[str] = []

    warnings.extend(_check_replacement_chars(text))
    warnings.extend(_check_equations(text))
    warnings.extend(_check_merged_headings(text))
    warnings.extend(_check_reading_order(text))
    warnings.extend(_check_tables(text))
    warnings.extend(_check_repeated_lines(text))
    warnings.extend(_check_references(text))

    if not text.strip():
        warnings.append("conversion produced no text")
    return [f"{key}: {w}" for w in warnings]


def _check_replacement_chars(text: str) -> list[str]:
    count = text.count(REPLACEMENT_CHAR)
    if not count:
        return []
    ratio = count / max(len(text), 1)
    return [
        f"{count} Unicode replacement characters ({ratio:.2%} of text); "
        "the source encoding or font mapping is probably lost"
    ]


def _check_equations(text: str) -> list[str]:
    warnings: list[str] = []
    if not _MATH_HINT.search(text):
        return warnings

    # Unbalanced delimiters are the usual signature of a truncated equation.
    if text.count("$$") % 2:
        warnings.append("odd number of '$$' delimiters; a display equation is unterminated")
    if (text.count("\\[") - text.count("\\]")) != 0:
        warnings.append("unbalanced '\\[' / '\\]'; a display equation is unterminated")
    if (text.count("\\begin{") - text.count("\\end{")) != 0:
        warnings.append("unbalanced LaTeX begin/end environments")

    empty = [m for m in _DISPLAY_MATH.finditer(text) if not (m.group(1) or m.group(2) or "").strip()]
    if empty:
        warnings.append(f"{len(empty)} empty display equations; content was dropped in conversion")

    stubs = [m for m in _INLINE_MATH.finditer(text) if len((m.group(1) or "").strip()) <= 1]
    if len(stubs) > 5:
        warnings.append(
            f"{len(stubs)} single-character inline math spans; equations may have been "
            "split into fragments"
        )
    return warnings


def _check_merged_headings(text: str) -> list[str]:
    warnings: list[str] = []
    long_lines = [line for line in text.splitlines() if len(line) > _LONG_LINE]
    if long_lines:
        warnings.append(
            f"{len(long_lines)} lines over {_LONG_LINE} characters; headings or columns "
            "may have been merged into paragraphs"
        )
    # A numbered section title sitting mid-paragraph rather than as a heading.
    inline_sections = re.findall(r"[a-z]\.\s+\d+\.\d+\s+[A-Z]", text)
    if len(inline_sections) > 3:
        warnings.append(
            f"{len(inline_sections)} numbered section titles appear inside paragraphs; "
            "heading detection likely failed"
        )
    if not _HEADING.search(text) and len(text) > 8000:
        warnings.append("no markdown headings in a long document; document structure was lost")
    return warnings


def _check_reading_order(text: str) -> list[str]:
    """Detect out-of-order numbered sections, the usual two-column symptom."""
    numbers: list[tuple[int, ...]] = []
    for match in _HEADING.finditer(text):
        section = _SECTION_NUMBER.match(match.group(2))
        if section:
            numbers.append(tuple(int(p) for p in section.group(1).split(".")))
    if len(numbers) < 3:
        return []
    inversions = sum(1 for a, b in zip(numbers, numbers[1:]) if b < a)
    if inversions > max(1, len(numbers) // 10):
        return [
            f"{inversions} out-of-order numbered sections across {len(numbers)}; "
            "two-column reading order is probably wrong"
        ]
    return []


def _check_tables(text: str) -> list[str]:
    rows = [line for line in text.splitlines() if _TABLE_ROW.match(line)]
    if not rows:
        return []
    widths = Counter(line.count("|") for line in rows)
    if len(widths) > 1:
        dominant, dominant_count = widths.most_common(1)[0]
        ragged = len(rows) - dominant_count
        if ragged > max(2, len(rows) // 5):
            return [
                f"{ragged} of {len(rows)} table rows have a column count other than "
                f"{dominant - 1}; table structure is malformed"
            ]
    return []


def _check_repeated_lines(text: str) -> list[str]:
    """Running headers and footers repeated on every page."""
    lines = [line.strip() for line in text.splitlines() if 8 < len(line.strip()) < 120]
    if len(lines) < 40:
        return []
    counts = Counter(lines)
    repeated = [(line, n) for line, n in counts.items() if n >= 5 and not line.startswith(("#", "|", "-", "*"))]
    if not repeated:
        return []
    worst = max(repeated, key=lambda item: item[1])
    return [
        f"{len(repeated)} lines repeat 5+ times (e.g. {worst[0][:60]!r} x{worst[1]}); "
        "running headers/footers were not stripped"
    ]


def _check_references(text: str) -> list[str]:
    marks = {int(m.group(1)) for m in _REFERENCE_MARK.finditer(text)}
    if len(marks) < 5:
        return []
    lower = text.lower()
    has_bibliography = any(
        heading in lower for heading in ("\n# references", "\n## references", "\nreferences\n", "bibliography")
    )
    if not has_bibliography:
        return [
            f"{len(marks)} citation markers but no references section; "
            "the bibliography was dropped or misplaced"
        ]
    return []

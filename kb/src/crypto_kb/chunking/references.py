"""Bibliography handling.

A reference list is high-similarity, low-information text: sliced into
retrieval-sized chunks it produces passages that match almost any query
mentioning an author and answer nothing. It is separated out, kept whole as a
single unit, and left retrievable for the one query it does answer -- "what is
reference [14]".
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_BIB_HEADING = re.compile(
    r"^#{1,6}\s*(?:\d+\.?\s*)?(references|bibliography|works cited|literature cited)\s*$",
    re.I | re.MULTILINE,
)
_NEXT_HEADING = re.compile(r"^#{1,6}\s+\S", re.MULTILINE)
_ENTRY = re.compile(r"^\s*(?:\[(\d{1,3})\]|(\d{1,3})\.)\s+(.+)$", re.MULTILINE)
_CITATION = re.compile(r"\[(\d{1,3}(?:\s*,\s*\d{1,3})*)\]")


@dataclass(frozen=True)
class Bibliography:
    text: str
    section_path: tuple[str, ...]
    line_start: int
    line_end: int
    entry_count: int


def split_bibliography(markdown: str) -> tuple[str, Bibliography | None]:
    """Return (body, bibliography). The bibliography is None when absent.

    Only a *trailing* references section is split off: some papers cite a
    "References" heading inside an appendix, and cutting the document at the
    first match would drop the appendices that follow it.
    """
    matches = list(_BIB_HEADING.finditer(markdown))
    if not matches:
        return markdown, None

    match = matches[-1]
    tail = markdown[match.end() :]
    next_heading = _NEXT_HEADING.search(tail)
    end = match.end() + next_heading.start() if next_heading else len(markdown)

    section_text = markdown[match.start() : end].strip()
    entries = len(_ENTRY.findall(section_text))
    if entries < 3:
        # Not really a reference list -- a "References" line with prose under
        # it, or a stub. Leave it in the body.
        return markdown, None

    line_start = markdown[: match.start()].count("\n")
    line_end = markdown[:end].count("\n")
    body = markdown[: match.start()] + markdown[end:]
    return body, Bibliography(
        text=section_text,
        section_path=("References",),
        line_start=line_start,
        line_end=line_end,
        entry_count=entries,
    )


def extract_citations(text: str) -> list[int]:
    """Numeric citation markers appearing in ``text``, deduplicated and sorted."""
    found: set[int] = set()
    for match in _CITATION.finditer(text):
        for part in match.group(1).split(","):
            part = part.strip()
            if part.isdigit():
                found.add(int(part))
    return sorted(found)

"""Parsers: source bytes in, normalized markdown out.

Dispatch is by extension. Clean markdown and plaintext get native parsers --
routing them through Docling would add a model-inference dependency and a
conversion step to content that is already in the target format, and would
lose the YAML frontmatter this repository's records carry.
"""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Protocol, runtime_checkable

from crypto_kb.models import ParsedDocument
from crypto_kb.parsing.markdown_parser import MarkdownParser
from crypto_kb.parsing.plaintext_parser import PlaintextParser, StructuredRecordParser

#: Extensions Docling owns. Everything else has a native parser or is rejected.
DOCLING_EXTENSIONS = frozenset(
    {".pdf", ".docx", ".pptx", ".xlsx", ".html", ".htm", ".png", ".jpg", ".jpeg", ".tiff"}
)


@runtime_checkable
class Parser(Protocol):
    name: str
    version: str

    def supports(self, key: str) -> bool: ...

    def parse(self, data: bytes, key: str) -> ParsedDocument: ...


class UnsupportedSource(ValueError):
    """No parser claims this key. The object is rejected, never guessed at."""


def native_parsers() -> list[Parser]:
    return [MarkdownParser(), StructuredRecordParser(), PlaintextParser()]


def select_parser(key: str) -> Parser:
    """Pick a parser for ``key``, importing Docling only when it is needed."""
    suffix = PurePosixPath(key).suffix.lower()
    if suffix in DOCLING_EXTENSIONS:
        from crypto_kb.parsing.docling_parser import DoclingParser

        return DoclingParser()
    for parser in native_parsers():
        if parser.supports(key):
            return parser
    raise UnsupportedSource(f"no parser for {key!r} (suffix {suffix!r})")


def parse(data: bytes, key: str) -> ParsedDocument:
    """Parse ``data`` and attach parse-quality warnings."""
    from crypto_kb.parsing.validation import validate_parse

    document = select_parser(key).parse(data, key)
    document.warnings.extend(validate_parse(document, key))
    return document


__all__ = [
    "Parser",
    "UnsupportedSource",
    "DOCLING_EXTENSIONS",
    "select_parser",
    "parse",
    "native_parsers",
    "MarkdownParser",
    "PlaintextParser",
    "StructuredRecordParser",
]

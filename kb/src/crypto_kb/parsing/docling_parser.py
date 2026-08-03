"""Docling adapter for PDF, DOCX, PPTX, HTML and images.

Imported lazily by ``parsing.select_parser`` so a local-corpus install does
not need the (large) docling stack. Both outputs are kept: markdown for
chunking and retrieval, the structured export for page provenance and later
re-chunking without a re-parse.
"""

from __future__ import annotations

import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

from crypto_kb.models import ParsedDocument


class DoclingUnavailable(RuntimeError):
    """Docling is not installed. Install the `docling` extra."""


class DoclingParser:
    name = "docling"

    def __init__(self, converter: Any | None = None) -> None:
        self._converter = converter
        self._version: str | None = None

    @property
    def version(self) -> str:
        if self._version is None:
            self._version = f"docling-{_docling_version()}"
        return self._version

    def supports(self, key: str) -> bool:
        from crypto_kb.parsing import DOCLING_EXTENSIONS

        return PurePosixPath(key).suffix.lower() in DOCLING_EXTENSIONS

    @property
    def converter(self) -> Any:
        if self._converter is None:
            try:
                from docling.document_converter import DocumentConverter
            except ImportError as exc:  # pragma: no cover - depends on install
                raise DoclingUnavailable(
                    "docling is required to parse PDF/DOCX/PPTX/HTML/images; "
                    "install with `pip install 'crypto-kb[docling]'`"
                ) from exc
            self._converter = DocumentConverter()
        return self._converter

    def parse(self, data: bytes, key: str) -> ParsedDocument:
        suffix = PurePosixPath(key).suffix.lower() or ".bin"
        # Docling converts from a path; the object may only exist in the store.
        with tempfile.TemporaryDirectory(prefix="crypto-kb-docling-") as tmpdir:
            path = Path(tmpdir) / (PurePosixPath(key).stem + suffix)
            path.write_bytes(data)
            result = self.converter.convert(str(path))

        document = result.document
        structured = _export_dict(document)
        return ParsedDocument(
            markdown=document.export_to_markdown(),
            structured=structured,
            parser=self.name,
            parser_version=self.version,
            page_count=_page_count(document, structured),
        )


def _export_dict(document: Any) -> dict[str, Any] | None:
    for attribute in ("export_to_dict", "model_dump"):
        exporter = getattr(document, attribute, None)
        if callable(exporter):
            try:
                exported = exporter()
            except Exception:  # pragma: no cover - version drift in docling
                continue
            if isinstance(exported, dict):
                return exported
    return None


def _page_count(document: Any, structured: dict[str, Any] | None) -> int | None:
    pages = getattr(document, "pages", None)
    if pages is not None:
        try:
            return len(pages)
        except TypeError:  # pragma: no cover
            pass
    if structured and isinstance(structured.get("pages"), (list, dict)):
        return len(structured["pages"])
    return None


def _docling_version() -> str:
    from importlib import metadata

    try:
        return metadata.version("docling")
    except metadata.PackageNotFoundError:  # pragma: no cover
        return "unknown"

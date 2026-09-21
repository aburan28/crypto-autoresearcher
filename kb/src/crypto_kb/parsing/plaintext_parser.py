"""Plaintext and structured-record parsers.

``StructuredRecordParser`` exists because a large part of this corpus is YAML
and JSON records (evidence, hypotheses, decisions, run manifests). Indexing
them as a raw code block would make them nearly unretrievable -- the text an
agent searches for is inside the values. They are rendered into headed
markdown sections instead, so section paths mirror the record structure and a
match points at the field it came from.
"""

from __future__ import annotations

from typing import Any

from crypto_kb.models import ParsedDocument

PLAINTEXT_VERSION = "native-plaintext-v1"
RECORD_VERSION = "native-record-v1"

#: Beyond this depth, nested structure is emitted inline rather than as
#: further headings; deeper headings fragment chunks without helping recall.
_MAX_HEADING_DEPTH = 3


def render_record(value: Any) -> str:
    """Render a nested record into headed markdown.

    Public because ``MarkdownParser`` needs exactly this for a note whose whole
    content is YAML frontmatter with no body: without it such a note produces
    no chunks and is silently unretrievable. Sharing one renderer keeps the
    section paths of a frontmatter-only note identical in shape to those of a
    ``.yaml`` record, so a match points at the field it came from either way.
    """
    lines: list[str] = []
    _render(value, lines, depth=1)
    return "\n".join(lines).strip()


class PlaintextParser:
    name = "native-plaintext"
    version = PLAINTEXT_VERSION

    def supports(self, key: str) -> bool:
        return key.lower().endswith((".txt", ".text", ".log", ".rst", ".tex", ".csv"))

    def parse(self, data: bytes, key: str) -> ParsedDocument:
        text = data.decode("utf-8", errors="replace")
        return ParsedDocument(
            markdown=text.strip() + "\n",
            structured={"format": "plaintext"},
            parser=self.name,
            parser_version=self.version,
        )


class StructuredRecordParser:
    name = "native-record"
    version = RECORD_VERSION

    def supports(self, key: str) -> bool:
        return key.lower().endswith((".yaml", ".yml", ".json"))

    def parse(self, data: bytes, key: str) -> ParsedDocument:
        text = data.decode("utf-8", errors="replace")
        loaded = _load(text, key)
        if loaded is None:
            # Unparseable: index the literal text rather than nothing, and let
            # validation flag it. Silently skipping would hide a corrupt record.
            return ParsedDocument(
                markdown=text.strip() + "\n",
                structured={"format": "unparsed-record"},
                parser=self.name,
                parser_version=self.version,
                warnings=[f"{key}: could not parse as YAML/JSON; indexed as plain text"],
            )
        lines: list[str] = []
        _render(loaded, lines, depth=1)
        return ParsedDocument(
            markdown="\n".join(lines).strip() + "\n",
            structured={"format": "record", "record": loaded},
            parser=self.name,
            parser_version=self.version,
        )


def _load(text: str, key: str) -> Any:
    import json

    if key.lower().endswith(".json"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None
    try:
        import yaml

        return yaml.safe_load(text)
    except Exception:
        return None


def _render(value: Any, out: list[str], depth: int, label: str | None = None) -> None:
    """Render a nested record into markdown with headings for its structure."""
    if label is not None and depth <= _MAX_HEADING_DEPTH and isinstance(value, (dict, list)):
        out.append(f"\n{'#' * min(depth, 6)} {label}\n")

    if isinstance(value, dict):
        # Scalars first, then nested structures. Emitting them in source order
        # would leave a scalar field printed *after* a subsection heading,
        # where it reads as belonging to that subsection.
        nested: list[tuple[str, Any]] = []
        for name, child in value.items():
            key = str(name)
            if isinstance(child, (dict, list)) and child and depth < _MAX_HEADING_DEPTH:
                nested.append((key, child))
            else:
                out.append(f"- **{key}**: {_inline(child)}")
        for key, child in nested:
            _render(child, out, depth + 1, label=key)
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                out.append("")
                _render(item, out, depth + 1)
            else:
                out.append(f"- {_inline(item)}")
    else:
        out.append(_inline(value))


def _inline(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float, str)):
        return str(value).strip()
    if isinstance(value, list):
        return ", ".join(_inline(v) for v in value)
    if isinstance(value, dict):
        return "; ".join(f"{k}: {_inline(v)}" for k, v in value.items())
    return str(value)

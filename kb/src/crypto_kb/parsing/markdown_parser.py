"""Native markdown parser.

Markdown is already the normalized form, so parsing is mostly about separating
YAML frontmatter from body text. The frontmatter is preserved in
``structured`` -- this repository's knowledge entries carry their identity
(id, tags, confidence, superseded_by) there, and dropping it would discard
exactly the fields retrieval filters on.

A note with frontmatter and NO body is a real shape in this corpus, not a
defect: some literature notes put their whole substance in frontmatter keys
(``key_claim``, ``relevance_to_*``). Those are rendered through the same
record renderer ``.yaml`` records use, because parsing them to an empty
document made ingestion reject them -- staged, counted, and silently
unsearchable.
"""

from __future__ import annotations

import re
from typing import Any

from crypto_kb.models import ParsedDocument
from crypto_kb.parsing.plaintext_parser import render_record

# v2: a note whose entire content is frontmatter (no body) now renders that
# frontmatter as its markdown instead of producing nothing. Bumping the version
# is what forces those documents to be re-parsed -- document_fingerprint covers
# parser_version, so without the bump an already-manifested note keeps its old
# empty rendering forever.
VERSION = "native-markdown-v2"

_FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)


def split_frontmatter(text: str) -> tuple[dict[str, Any] | None, str]:
    """Return (frontmatter, body). Unparseable frontmatter is left in the body.

    Frontmatter that does not parse is a signal about the document, not a
    reason to drop content: it stays visible in the body where a human reading
    a search result can see it is malformed.
    """
    match = _FRONTMATTER.match(text)
    if not match:
        return None, text
    try:
        import yaml

        loaded = yaml.safe_load(match.group(1))
    except Exception:
        return None, text
    if not isinstance(loaded, dict):
        return None, text
    return loaded, text[match.end() :]


class MarkdownParser:
    name = "native-markdown"
    version = VERSION

    def supports(self, key: str) -> bool:
        return key.lower().endswith((".md", ".markdown", ".mdx"))

    def parse(self, data: bytes, key: str) -> ParsedDocument:
        text = data.decode("utf-8", errors="replace")
        frontmatter, body = split_frontmatter(text)
        structured: dict[str, Any] = {"format": "markdown"}
        if frontmatter is not None:
            structured["frontmatter"] = frontmatter

        rendered = body.strip()
        warnings: list[str] = []
        if not rendered and frontmatter:
            # Frontmatter-only note. Several literature notes carry their whole
            # substance in frontmatter keys (key_claim, relevance_to_*) and have
            # no body at all; parsing those to an empty document made them
            # produce no chunks, so ingestion REJECTED them and they were
            # unreachable by search while still counting as staged. Render the
            # frontmatter as the body instead. This applies ONLY when there is
            # no body: a note that has one keeps its current rendering exactly,
            # and frontmatter stays in `structured` either way, so the fields
            # retrieval filters on are unaffected.
            rendered = render_record(frontmatter)
            structured["body_source"] = "frontmatter"
            if not rendered:
                warnings.append(f"{key}: empty body and empty frontmatter; nothing to index")

        return ParsedDocument(
            markdown=rendered + "\n",
            structured=structured,
            parser=self.name,
            parser_version=self.version,
            warnings=warnings,
        )

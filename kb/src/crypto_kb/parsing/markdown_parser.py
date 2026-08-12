"""Native markdown parser.

Markdown is already the normalized form, so parsing is mostly about separating
YAML frontmatter from body text. The frontmatter is preserved in
``structured`` -- this repository's knowledge entries carry their identity
(id, tags, confidence, superseded_by) there, and dropping it would discard
exactly the fields retrieval filters on.
"""

from __future__ import annotations

import re
from typing import Any

from crypto_kb.models import ParsedDocument

VERSION = "native-markdown-v1"

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
        return ParsedDocument(
            markdown=body.strip() + "\n",
            structured=structured,
            parser=self.name,
            parser_version=self.version,
        )

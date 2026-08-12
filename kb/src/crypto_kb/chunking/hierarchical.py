"""Hierarchy-first chunking.

Order of operations, per the plan: document -> section -> subsection ->
paragraph group -> token-size enforcement. Token limits are the *last* thing
consulted, never the first, and they never override an atomic unit.

Two levels are emitted:

* child chunks (~500-800 tokens) -- what retrieval scores against;
* parent chunks (~2,000-4,000 tokens) -- what ``get_context`` expands into.

Parents are indexed as points too, but flagged ``is_parent`` and excluded from
search by default, so context expansion needs no second store.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from crypto_kb.chunking.equations import (
    Block,
    BlockKind,
    Group,
    group_blocks,
    heading_atomic_label,
)
from crypto_kb.chunking.references import split_bibliography
from crypto_kb.hashing import chunk_id as make_chunk_id
from crypto_kb.hashing import sha256_text
from crypto_kb.models import Chunk
from crypto_kb.text import count_tokens, split_sentences, tail_tokens

_HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
_FENCE = re.compile(r"^\s*(```|~~~)")
_TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")
_LIST_ITEM = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)")
_QUOTE = re.compile(r"^\s*>")
_DISPLAY_OPEN = re.compile(r"^\s*(\$\$|\\\[|\\begin\{(?:equation|align|gather|multline)\*?\})")
_DISPLAY_CLOSE = re.compile(r"(\$\$|\\\]|\\end\{(?:equation|align|gather|multline)\*?\})\s*$")


@dataclass(frozen=True)
class ChunkingConfig:
    target_tokens: int = 640
    max_tokens: int = 1200
    min_tokens: int = 120
    overlap_tokens: int = 100
    parent_target_tokens: int = 3000
    parent_max_tokens: int = 4000

    @classmethod
    def from_settings(cls, settings) -> "ChunkingConfig":
        return cls(
            target_tokens=settings.chunk_target_tokens,
            max_tokens=settings.chunk_max_tokens,
            min_tokens=settings.chunk_min_tokens,
            overlap_tokens=settings.chunk_overlap_tokens,
            parent_target_tokens=settings.parent_target_tokens,
            parent_max_tokens=settings.parent_max_tokens,
        )


class HierarchicalChunker:
    def __init__(self, config: ChunkingConfig | None = None) -> None:
        self.config = config or ChunkingConfig()

    # -- public API --------------------------------------------------------

    def chunk(
        self,
        markdown: str,
        source_id: str,
        page_map: dict[int, int] | None = None,
    ) -> list[Chunk]:
        """Return parent chunks followed by child chunks, all indexed in order.

        ``page_map`` maps a 0-based line number to a page number. It is only
        supplied when the parser could establish it (Docling); otherwise page
        fields stay ``None`` rather than being guessed.
        """
        body, bibliography = split_bibliography(markdown)
        blocks = parse_blocks(body)
        groups = group_blocks(blocks, max_group_tokens=self.config.max_tokens * 2)
        packed = self._pack(groups)
        if bibliography is not None:
            # The reference list is one unit: useful for "which paper is [14]"
            # and actively harmful when sliced into scoring-sized fragments.
            packed.append(
                _Packed(
                    text=bibliography.text,
                    section_path=bibliography.section_path,
                    labels=("references",),
                    line_start=bibliography.line_start,
                    line_end=bibliography.line_end,
                    headings=_heading_tuple(bibliography.section_path),
                )
            )
        return self._materialize(packed, source_id, page_map)

    # -- packing -----------------------------------------------------------

    def _pack(self, groups: list[Group]) -> list["_Packed"]:
        config = self.config
        packed: list[_Packed] = []
        buffer: list[Group] = []
        buffer_tokens = 0

        def flush() -> None:
            nonlocal buffer, buffer_tokens
            if not buffer:
                return
            packed.append(_from_groups(buffer))
            buffer = []
            buffer_tokens = 0

        for group in groups:
            tokens = count_tokens(group.text)

            # A section change ends the chunk -- unless what we have so far is
            # too small to stand alone. A corpus of short subsections (this
            # program's own notes) would otherwise chunk into dozens of
            # 40-token fragments, each scoring on its heading and answering
            # nothing. When sections are merged the chunk's section_path
            # becomes their common ancestor, so it never claims to be from a
            # section it only partly covers.
            if (
                buffer
                and group.section_path != buffer[-1].section_path
                and buffer_tokens >= config.min_tokens
            ):
                flush()

            if tokens > config.max_tokens:
                flush()
                if group.splittable:
                    for piece in self._split_prose(group):
                        packed.append(piece)
                else:
                    # Oversized atomic unit: emitted whole, on purpose.
                    packed.append(_from_groups([group]))
                continue

            if buffer_tokens + tokens > config.target_tokens and buffer_tokens >= config.min_tokens:
                flush()

            buffer.append(group)
            buffer_tokens += tokens

            if buffer_tokens >= config.target_tokens:
                flush()

        flush()
        return self._merge_undersized(packed)

    def _split_prose(self, group: Group) -> list["_Packed"]:
        """Split an oversized prose group on sentence boundaries."""
        sentences = split_sentences(group.text)
        pieces: list[_Packed] = []
        current: list[str] = []
        tokens = 0
        for sentence in sentences:
            sentence_tokens = count_tokens(sentence)
            if current and tokens + sentence_tokens > self.config.target_tokens:
                pieces.append(
                    _Packed(
                        text=" ".join(current),
                        section_path=group.section_path,
                        labels=(),
                        line_start=group.line_start,
                        line_end=group.line_end,
                        headings=_heading_tuple(group.section_path),
                    )
                )
                current, tokens = [], 0
            current.append(sentence)
            tokens += sentence_tokens
        if current:
            pieces.append(
                _Packed(
                    text=" ".join(current),
                    section_path=group.section_path,
                    labels=(),
                    line_start=group.line_start,
                    line_end=group.line_end,
                    headings=_heading_tuple(group.section_path),
                )
            )
        return pieces

    def _merge_undersized(self, packed: list["_Packed"]) -> list["_Packed"]:
        """Fold chunks below the minimum into a same-section neighbour.

        A 20-token orphan ("4.2 Relation Generation") scores well on the query
        that names it and carries no answer. Merging costs nothing; the only
        chunks left below the minimum are documents that are simply that short.
        """
        merged: list[_Packed] = []
        for piece in packed:
            previous = merged[-1] if merged else None
            if (
                previous is not None
                and count_tokens(piece.text) < self.config.min_tokens
                and _related_sections(previous.section_path, piece.section_path)
                and count_tokens(previous.text) + count_tokens(piece.text)
                <= self.config.max_tokens
            ):
                merged[-1] = merged[-1].joined(piece)
                continue
            merged.append(piece)
        return merged

    # -- materialisation ---------------------------------------------------

    def _materialize(
        self,
        packed: list["_Packed"],
        source_id: str,
        page_map: dict[int, int] | None,
    ) -> list[Chunk]:
        parents = self._build_parents(packed)

        chunks: list[Chunk] = []
        index = 0
        parent_ids: list[str] = []

        for parent in parents:
            parent_chunk_id = make_chunk_id(source_id, index, parent.text)
            parent_ids.append(parent_chunk_id)
            chunks.append(
                Chunk(
                    chunk_id=parent_chunk_id,
                    source_id=source_id,
                    chunk_index=index,
                    text=parent.text,
                    content_hash=sha256_text(parent.text),
                    section_path=list(parent.section_path),
                    section_headings=list(parent.headings),
                    parent_id=None,
                    is_parent=True,
                    token_count=count_tokens(parent.text),
                    page_start=_page_of(page_map, parent.line_start),
                    page_end=_page_of(page_map, parent.line_end),
                    atomic_blocks=list(parent.labels),
                )
            )
            index += 1

        previous_text: str | None = None
        previous_section: tuple[str, ...] | None = None
        for parent_position, piece in _with_parent_positions(packed, parents):
            text = piece.text
            if (
                self.config.overlap_tokens
                and previous_text is not None
                and previous_section == piece.section_path
                and not piece.labels
            ):
                # Overlap only into prose. Prefixing a theorem with the tail of
                # the previous paragraph would corrupt an atomic unit's text.
                overlap = tail_tokens(previous_text, self.config.overlap_tokens)
                if overlap:
                    text = f"{overlap}\n\n{piece.text}"

            chunks.append(
                Chunk(
                    chunk_id=make_chunk_id(source_id, index, text),
                    source_id=source_id,
                    chunk_index=index,
                    text=text,
                    content_hash=sha256_text(text),
                    section_path=list(piece.section_path),
                    section_headings=list(piece.headings),
                    parent_id=parent_ids[parent_position] if parent_ids else None,
                    is_parent=False,
                    token_count=count_tokens(text),
                    page_start=_page_of(page_map, piece.line_start),
                    page_end=_page_of(page_map, piece.line_end),
                    atomic_blocks=list(piece.labels),
                )
            )
            previous_text = piece.text
            previous_section = piece.section_path
            index += 1

        return chunks

    def _build_parents(self, packed: list["_Packed"]) -> list["_Packed"]:
        """Group child pieces into parent sections of ~2,000-4,000 tokens."""
        parents: list[_Packed] = []
        buffer: list[_Packed] = []
        tokens = 0

        def flush() -> None:
            nonlocal buffer, tokens
            if not buffer:
                return
            combined = buffer[0]
            for piece in buffer[1:]:
                combined = combined.joined(piece)
            parents.append(combined)
            buffer, tokens = [], 0

        for piece in packed:
            piece_tokens = count_tokens(piece.text)
            top_section = piece.section_path[:1]
            if buffer and (
                buffer[-1].section_path[:1] != top_section
                or tokens + piece_tokens > self.config.parent_max_tokens
            ):
                flush()
            buffer.append(piece)
            tokens += piece_tokens
            if tokens >= self.config.parent_target_tokens:
                flush()
        flush()
        return parents


# --------------------------------------------------------------------------
# Block parsing
# --------------------------------------------------------------------------


def parse_blocks(markdown: str) -> list[Block]:
    """Split markdown into structural blocks, carrying the heading path."""
    lines = markdown.splitlines()
    blocks: list[Block] = []
    section: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]

        if not line.strip():
            index += 1
            continue

        heading = _HEADING.match(line)
        if heading:
            level = len(heading.group(1))
            title = heading.group(2).strip()
            del section[level - 1 :]
            while len(section) < level - 1:
                section.append("")
            section.append(title)
            index += 1
            continue

        path = tuple(s for s in section if s)
        section_label = heading_atomic_label(path[-1]) if path else None

        if _FENCE.match(line):
            fence = _FENCE.match(line).group(1)
            start = index
            index += 1
            while index < len(lines) and not lines[index].strip().startswith(fence):
                index += 1
            index = min(index + 1, len(lines))
            blocks.append(_block(BlockKind.CODE, lines[start:index], path, start, index, section_label))
            continue

        if _DISPLAY_OPEN.match(line):
            start = index
            # A one-line `$$ x $$` closes immediately; otherwise scan forward.
            if not (_DISPLAY_CLOSE.search(line) and len(line.strip()) > 4):
                index += 1
                while index < len(lines) and not _DISPLAY_CLOSE.search(lines[index]):
                    index += 1
            index = min(index + 1, len(lines))
            blocks.append(
                _block(BlockKind.DISPLAY_MATH, lines[start:index], path, start, index, section_label)
            )
            continue

        if _TABLE_ROW.match(line):
            start = index
            while index < len(lines) and _TABLE_ROW.match(lines[index]):
                index += 1
            blocks.append(_block(BlockKind.TABLE, lines[start:index], path, start, index, section_label))
            continue

        if _LIST_ITEM.match(line) or _QUOTE.match(line):
            kind = BlockKind.QUOTE if _QUOTE.match(line) else BlockKind.LIST
            start = index
            while index < len(lines) and lines[index].strip():
                if _HEADING.match(lines[index]) or _TABLE_ROW.match(lines[index]):
                    break
                index += 1
            blocks.append(_block(kind, lines[start:index], path, start, index, section_label))
            continue

        start = index
        while index < len(lines) and lines[index].strip():
            nxt = lines[index]
            if index > start and (
                _HEADING.match(nxt)
                or _TABLE_ROW.match(nxt)
                or _FENCE.match(nxt)
                or _DISPLAY_OPEN.match(nxt)
                or _LIST_ITEM.match(nxt)
            ):
                break
            index += 1
        blocks.append(_block(BlockKind.PARAGRAPH, lines[start:index], path, start, index, section_label))

    return blocks


def _block(
    kind: BlockKind,
    lines: list[str],
    path: tuple[str, ...],
    start: int,
    end: int,
    section_label: str | None,
) -> Block:
    labels: tuple[str, ...] = (section_label,) if section_label else ()
    return Block(
        kind=kind,
        text="\n".join(lines).strip("\n"),
        section_path=path,
        line_start=start,
        line_end=end,
        atomic_labels=labels,
    )


# --------------------------------------------------------------------------
# Packed pieces
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class _Packed:
    text: str
    section_path: tuple[str, ...]
    labels: tuple[str, ...]
    line_start: int
    line_end: int
    #: Every heading path covered, in document order.
    headings: tuple[str, ...] = ()

    def joined(self, other: "_Packed") -> "_Packed":
        return _Packed(
            text=f"{self.text}\n\n{other.text}",
            # The merged chunk spans both sections, so it is attributed to
            # their common ancestor rather than to whichever came first.
            section_path=_common_prefix(self.section_path, other.section_path),
            labels=tuple(dict.fromkeys(self.labels + other.labels)),
            line_start=min(self.line_start, other.line_start),
            line_end=max(self.line_end, other.line_end),
            headings=tuple(dict.fromkeys(self.headings + other.headings)),
        )


def _from_groups(groups: list[Group]) -> _Packed:
    labels: tuple[str, ...] = ()
    for group in groups:
        labels = tuple(dict.fromkeys(labels + group.labels))

    # Each distinct heading path is written into the text as it is reached, so
    # a retrieved passage carries its own address rather than only carrying it
    # in metadata: agents cite what they can see.
    parts: list[str] = []
    headings: list[str] = []
    current: tuple[str, ...] | None = None
    for group in groups:
        if group.section_path != current:
            heading = " > ".join(group.section_path)
            if heading:
                parts.append(f"[{heading}]")
                if heading not in headings:
                    headings.append(heading)
            current = group.section_path
        parts.append(group.text)

    section_path = groups[0].section_path
    for group in groups[1:]:
        section_path = _common_prefix(section_path, group.section_path)

    return _Packed(
        text="\n\n".join(parts),
        section_path=section_path,
        labels=labels,
        line_start=groups[0].line_start,
        line_end=groups[-1].line_end,
        headings=tuple(headings),
    )


def _heading_tuple(path: tuple[str, ...]) -> tuple[str, ...]:
    joined = " > ".join(path)
    return (joined,) if joined else ()


def _common_prefix(left: tuple[str, ...], right: tuple[str, ...]) -> tuple[str, ...]:
    shared: list[str] = []
    for a, b in zip(left, right):
        if a != b:
            break
        shared.append(a)
    return tuple(shared)


def _related_sections(left: tuple[str, ...], right: tuple[str, ...]) -> bool:
    """True when two section paths sit under a shared heading (or none at all)."""
    if not left or not right:
        return True
    return left[0] == right[0]


def _with_parent_positions(
    packed: list[_Packed], parents: list[_Packed]
) -> list[tuple[int, _Packed]]:
    """Assign each child piece to the parent whose text contains it."""
    assignments: list[tuple[int, _Packed]] = []
    parent_index = 0
    for piece in packed:
        while (
            parent_index + 1 < len(parents)
            and piece.line_start > parents[parent_index].line_end
        ):
            parent_index += 1
        assignments.append((min(parent_index, max(len(parents) - 1, 0)), piece))
    return assignments


def _page_of(page_map: dict[int, int] | None, line: int) -> int | None:
    if not page_map:
        return None
    for candidate in range(line, -1, -1):
        if candidate in page_map:
            return page_map[candidate]
    return None


def chunk_document(
    markdown: str,
    source_id: str,
    config: ChunkingConfig | None = None,
    page_map: dict[int, int] | None = None,
) -> list[Chunk]:
    return HierarchicalChunker(config).chunk(markdown, source_id, page_map)

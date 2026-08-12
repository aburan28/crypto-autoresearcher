"""Block classification and the atomic-unit rules.

The plan lists the things a chunk boundary must never fall inside: a theorem
and its proof, a definition, an algorithm, a complexity derivation, an
experiment result table, an equation and its explanation, a negative-result
conclusion, an assumptions list. This module is where those units are
recognised; ``hierarchical.py`` packs them without ever cutting one open.

The cost of the rule is bounded and deliberate: an atomic unit longer than the
maximum chunk size is emitted oversized rather than split, and the chunk
records which unit forced it. A 1,400-token theorem retrieved whole is useful;
the same theorem cut at token 1,200, mid-statement, is not.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class BlockKind(str, Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    DISPLAY_MATH = "display-math"
    CODE = "code"
    TABLE = "table"
    LIST = "list"
    QUOTE = "quote"


#: Openers of an atomic unit. The value is the label recorded on the chunk.
_ATOMIC_OPENERS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"^\**\s*(theorem|lemma|proposition|corollary|claim|fact)\b", re.I), "theorem"),
    (re.compile(r"^\**\s*(definition|notation|convention)\b", re.I), "definition"),
    (re.compile(r"^\**\s*(proof|sketch of proof)\b", re.I), "proof"),
    (re.compile(r"^\**\s*(algorithm|procedure|protocol|construction)\b", re.I), "algorithm"),
    (re.compile(r"^\**\s*(assumption|heuristic|hypothesis)s?\b", re.I), "assumptions"),
    (re.compile(r"^\**\s*(remark|observation)\b", re.I), "remark"),
    (re.compile(r"^\**\s*(table|figure)\s*\d", re.I), "table"),
    (re.compile(r"^\**\s*(complexity|cost)\s+(analysis|derivation|model)\b", re.I), "complexity"),
    (re.compile(r"^\**\s*(negative result|non-result|what (did|does) not work)\b", re.I), "negative-result"),
)

#: Headings that make an entire section an atomic unit worth keeping together
#: when it fits: conclusions and boundaries are exactly the passages this
#: program must never retrieve half of.
_ATOMIC_HEADINGS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\b(assumptions?|heuristics?)\b", re.I), "assumptions"),
    (re.compile(r"\b(boundaries|scope|limitations)\b", re.I), "boundaries"),
    (re.compile(r"\b(negative results?|falsification)\b", re.I), "negative-result"),
    (re.compile(r"\b(complexity|cost model)\b", re.I), "complexity"),
)

#: Continuation openers: a paragraph starting this way explains the block
#: before it and must stay attached to it.
_CONTINUATION = re.compile(
    r"^\s*(where|here|with|in which|such that|and\b|for which|note that|equivalently|"
    r"that is|i\.e\.|e\.g\.|thus|hence|therefore|so that)\b",
    re.I,
)

_CAPTION = re.compile(r"^\**\s*(table|figure|fig\.|alg(?:orithm)?\.?)\s*\d+", re.I)

_ENUMERATED_ASSUMPTION = re.compile(r"^\s*(?:\(?[HhAa]?\d+\)?[.)]|\d+[.)])\s+\S")


@dataclass
class Block:
    """One structural unit of a document, before packing."""

    kind: BlockKind
    text: str
    section_path: tuple[str, ...] = ()
    line_start: int = 0
    line_end: int = 0
    #: Non-empty when this block opens or belongs to an atomic unit.
    atomic_labels: tuple[str, ...] = ()

    @property
    def is_atomic(self) -> bool:
        return bool(self.atomic_labels)


@dataclass
class Group:
    """One or more blocks that must be emitted together."""

    blocks: list[Block] = field(default_factory=list)
    labels: tuple[str, ...] = ()

    @property
    def section_path(self) -> tuple[str, ...]:
        return self.blocks[0].section_path if self.blocks else ()

    @property
    def text(self) -> str:
        return "\n\n".join(b.text for b in self.blocks)

    @property
    def line_start(self) -> int:
        return self.blocks[0].line_start if self.blocks else 0

    @property
    def line_end(self) -> int:
        return self.blocks[-1].line_end if self.blocks else 0

    @property
    def is_atomic(self) -> bool:
        return bool(self.labels)

    @property
    def splittable(self) -> bool:
        """Prose-only groups may be split on sentence bounds if oversized."""
        return not self.labels and all(b.kind == BlockKind.PARAGRAPH for b in self.blocks)


def atomic_label(block: Block) -> str | None:
    """The atomic-unit label this block opens, if any."""
    first_line = block.text.lstrip().splitlines()[0] if block.text.strip() else ""
    if block.kind == BlockKind.TABLE:
        return "table"
    if block.kind == BlockKind.DISPLAY_MATH:
        return "equation"
    if block.kind == BlockKind.CODE:
        return "algorithm"
    for pattern, label in _ATOMIC_OPENERS:
        if pattern.match(first_line):
            return label
    if block.kind == BlockKind.LIST and _looks_like_assumption_list(block.text):
        return "assumptions"
    return None


def heading_atomic_label(heading: str) -> str | None:
    for pattern, label in _ATOMIC_HEADINGS:
        if pattern.search(heading):
            return label
    return None


def continues_previous(block: Block) -> bool:
    """True when ``block`` is the explanation of the block before it."""
    if block.kind in {BlockKind.DISPLAY_MATH, BlockKind.TABLE, BlockKind.CODE}:
        return False
    text = block.text.lstrip()
    if _CONTINUATION.match(text):
        return True
    # A paragraph opening in lower case is a continuation of the sentence that
    # the display block interrupted.
    return bool(text[:1].islower())


def is_caption(block: Block) -> bool:
    return block.kind == BlockKind.PARAGRAPH and bool(_CAPTION.match(block.text.lstrip()))


def group_blocks(blocks: list[Block], max_group_tokens: int) -> list[Group]:
    """Merge blocks into atomic groups.

    ``max_group_tokens`` bounds the damage from a runaway match: a "Proof"
    that absorbs the rest of a chapter helps nobody, so absorption stops once
    the group is that large, even mid-unit. When that happens the group is
    still labelled, so the truncation is visible downstream.
    """
    from crypto_kb.text import count_tokens

    groups: list[Group] = []
    index = 0
    while index < len(blocks):
        block = blocks[index]
        label = atomic_label(block)
        current = Group(blocks=[block], labels=(label,) if label else ())
        tokens = count_tokens(block.text)
        index += 1

        # A caption immediately followed by its table/figure joins it.
        if is_caption(block) and index < len(blocks) and blocks[index].kind == BlockKind.TABLE:
            current.blocks.append(blocks[index])
            current.labels = tuple(dict.fromkeys(current.labels + ("table",)))
            tokens += count_tokens(blocks[index].text)
            index += 1

        # Only an atomic group absorbs. Plain prose groups stay one block each
        # and are merged later by the packer's token budget, which keeps the
        # absorption rules from quietly welding a whole section together.
        while current.labels and index < len(blocks) and tokens < max_group_tokens:
            candidate = blocks[index]
            if candidate.section_path != current.section_path:
                break
            next_label = atomic_label(candidate)

            if next_label == "proof" and "theorem" in current.labels:
                pass  # theorem and proof are one unit, by the plan's rule
            elif next_label is None and continues_previous(candidate):
                pass  # the explanation of the block above it
            else:
                break

            current.blocks.append(candidate)
            if next_label:
                current.labels = tuple(dict.fromkeys(current.labels + (next_label,)))
            tokens += count_tokens(candidate.text)
            index += 1

        groups.append(current)

    return _attach_leadins(groups)


def _attach_leadins(groups: list[Group]) -> list[Group]:
    """Pull a display equation's lead-in sentence into its group.

    ``... satisfies:`` followed by a display equation is one thought. Splitting
    there is the single most common way an equation ends up in the index with
    nothing to say what it is.
    """
    merged: list[Group] = []
    for group in groups:
        if (
            merged
            and "equation" in group.labels
            and merged[-1].splittable
            and merged[-1].section_path == group.section_path
            and merged[-1].text.rstrip().endswith((":", "by", "as", "is"))
        ):
            previous = merged.pop()
            group = Group(blocks=previous.blocks + group.blocks, labels=group.labels)
        merged.append(group)
    return merged


def _looks_like_assumption_list(text: str) -> bool:
    lines = [line for line in text.splitlines() if line.strip()]
    enumerated = sum(1 for line in lines if _ENUMERATED_ASSUMPTION.match(line))
    if enumerated < 2:
        return False
    lowered = text.lower()
    return any(word in lowered for word in ("assum", "heuristic", "conjectur", "suppose", "we posit"))

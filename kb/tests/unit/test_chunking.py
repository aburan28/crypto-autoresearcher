"""The chunker's promises: hierarchy first, atomic units never split."""

from __future__ import annotations

import pytest

from crypto_kb.chunking import ChunkingConfig, chunk_document
from crypto_kb.chunking.equations import Block, BlockKind, atomic_label
from crypto_kb.chunking.hierarchical import parse_blocks
from crypto_kb.chunking.references import extract_citations, split_bibliography
from crypto_kb.text import count_tokens


def children(chunks):
    return [c for c in chunks if not c.is_parent]


def parents(chunks):
    return [c for c in chunks if c.is_parent]


def test_theorem_and_proof_stay_in_one_chunk(sample_markdown):
    chunks = children(chunk_document(sample_markdown, "paper:test"))
    holding_theorem = [c for c in chunks if "Theorem 4.3." in c.text]
    assert holding_theorem, "the theorem statement vanished"
    assert any("*Proof.*" in c.text for c in holding_theorem), (
        "theorem and proof were split across chunks"
    )


def test_table_stays_with_its_caption(sample_markdown):
    chunks = children(chunk_document(sample_markdown, "paper:test"))
    with_table = [c for c in chunks if "| P-256 | 10000" in c.text]
    assert len(with_table) == 1
    assert "Table 3" in with_table[0].text


def test_bibliography_is_one_chunk_and_not_interleaved(sample_markdown):
    chunks = children(chunk_document(sample_markdown, "paper:test"))
    reference_chunks = [c for c in chunks if "references" in c.atomic_blocks]
    assert len(reference_chunks) == 1
    assert "Semaev, Summation polynomials" in reference_chunks[0].text
    assert "Faugere, F4" in reference_chunks[0].text


def test_section_path_is_recorded(sample_markdown):
    chunks = children(chunk_document(sample_markdown, "paper:test"))
    paths = {tuple(c.section_path) for c in chunks}
    assert any("Relation generation" in path for path in paths if path)


def test_parents_cover_children(sample_markdown):
    chunks = chunk_document(sample_markdown, "paper:test")
    assert parents(chunks), "no parent chunks were produced"
    parent_ids = {c.chunk_id for c in parents(chunks)}
    for child in children(chunks):
        assert child.parent_id in parent_ids


def test_chunk_indexes_are_unique_and_dense(sample_markdown):
    chunks = chunk_document(sample_markdown, "paper:test")
    indexes = [c.chunk_index for c in chunks]
    assert indexes == list(range(len(chunks)))


def test_oversized_atomic_unit_is_kept_whole_and_labelled():
    long_proof = " ".join(f"step {i} of the argument follows." for i in range(600))
    text = f"# Section\n\n**Theorem 1.** A statement.\n\n*Proof.* {long_proof}\n"
    config = ChunkingConfig(target_tokens=100, max_tokens=200, min_tokens=20, overlap_tokens=0)
    chunks = children(chunk_document(text, "paper:test", config))
    theorem_chunks = [c for c in chunks if "Theorem 1." in c.text]
    assert len(theorem_chunks) == 1
    assert count_tokens(theorem_chunks[0].text) > config.max_tokens
    assert "theorem" in theorem_chunks[0].atomic_blocks


def test_prose_over_the_maximum_is_split():
    prose = " ".join(f"Sentence number {i} carries no special structure." for i in range(400))
    config = ChunkingConfig(target_tokens=100, max_tokens=150, min_tokens=20, overlap_tokens=0)
    chunks = children(chunk_document(f"# S\n\n{prose}\n", "paper:test", config))
    assert len(chunks) > 1


def test_display_equation_keeps_its_explanation():
    text = (
        "# Cost\n\n"
        "The relation probability satisfies:\n\n"
        "$$P(m) = \\frac{1}{m!}\\left(1 - \\epsilon\\right)$$\n\n"
        "where m is the decomposition arity and epsilon the correction term.\n"
    )
    chunks = children(chunk_document(text, "paper:test"))
    holding = [c for c in chunks if "P(m)" in c.text]
    assert len(holding) == 1
    assert "where m is the decomposition arity" in holding[0].text
    assert "satisfies:" in holding[0].text


def test_undersized_fragments_are_merged():
    text = "\n\n".join(f"## Section {i}\n\nA short line about topic {i}." for i in range(8))
    chunks = children(chunk_document(text, "paper:test"))
    assert len(chunks) < 8, "each tiny section became its own chunk"


def test_overlap_is_not_applied_across_atomic_units(sample_markdown):
    chunks = children(chunk_document(sample_markdown, "paper:test"))
    for chunk in chunks:
        if chunk.atomic_blocks and "references" not in chunk.atomic_blocks:
            assert not chunk.text.startswith("The decomposition succeeds")


def test_page_map_assigns_pages():
    text = "# A\n\nFirst paragraph.\n\n# B\n\nSecond paragraph.\n"
    chunks = children(chunk_document(text, "paper:test", page_map={0: 1, 4: 2}))
    assert {c.page_start for c in chunks} <= {1, 2}


def test_page_fields_stay_none_without_a_page_map(sample_markdown):
    chunks = chunk_document(sample_markdown, "paper:test")
    assert all(c.page_start is None and c.page_end is None for c in chunks)


@pytest.mark.parametrize(
    "line,expected",
    [
        ("**Theorem 4.3.** Let E be", "theorem"),
        ("Definition 2 (factor base).", "definition"),
        ("*Proof.* By induction", "proof"),
        ("Algorithm 1: relation search", "algorithm"),
        ("Assumption 3. The curve is generic.", "assumptions"),
        ("Table 2: yields", "table"),
        ("Ordinary prose about curves.", None),
    ],
)
def test_atomic_openers(line, expected):
    block = Block(kind=BlockKind.PARAGRAPH, text=line)
    assert atomic_label(block) == expected


def test_parse_blocks_tracks_heading_depth():
    text = "# One\n\npara\n\n## Two\n\npara\n\n# Three\n\npara\n"
    blocks = parse_blocks(text)
    assert [b.section_path for b in blocks] == [("One",), ("One", "Two"), ("Three",)]


def test_split_bibliography_uses_the_trailing_section():
    text = (
        "# Body\n\ntext\n\n# References\n\n[1] A\n[2] B\n[3] C\n\n"
        "# Appendix\n\nmore text\n"
    )
    body, bibliography = split_bibliography(text)
    assert bibliography is not None
    assert "Appendix" in body and "more text" in body
    assert bibliography.entry_count == 3


def test_split_bibliography_ignores_a_stub():
    body, bibliography = split_bibliography("# Body\n\ntext\n\n# References\n\nSee the arXiv page.\n")
    assert bibliography is None
    assert "References" in body


def test_extract_citations():
    assert extract_citations("as shown in [3] and [7, 12]") == [3, 7, 12]

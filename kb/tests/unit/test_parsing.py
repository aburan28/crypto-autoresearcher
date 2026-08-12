"""Parser dispatch, record rendering, and the math-quality checks."""

from __future__ import annotations

import pytest

from crypto_kb.models import ParsedDocument
from crypto_kb.parsing import UnsupportedSource, parse, select_parser
from crypto_kb.parsing.markdown_parser import split_frontmatter
from crypto_kb.parsing.validation import validate_parse


def test_markdown_frontmatter_is_separated(sample_document):
    document = parse(sample_document.encode("utf-8"), "knowledge/source/papers/x.md")
    assert document.parser == "native-markdown"
    assert not document.markdown.lstrip().startswith("---")
    assert document.structured["frontmatter"]["id"] == "KN-TEST-001"


def test_unparseable_frontmatter_stays_in_the_body():
    text = "---\nnot: [valid: yaml\n---\n\nbody\n"
    frontmatter, body = split_frontmatter(text)
    assert frontmatter is None
    assert body == text


def test_yaml_record_renders_as_headed_markdown():
    record = b"evidence:\n  id: EV-1\n  strength: single-run\n  observations:\n    - first\n    - second\n"
    document = parse(record, "knowledge/source/ledgers/EV-1.yaml")
    assert document.parser == "native-record"
    assert "## evidence" in document.markdown
    assert "**id**: EV-1" in document.markdown
    assert "- first" in document.markdown


def test_scalars_precede_subsections_in_a_record():
    record = b"evidence:\n  runs:\n    - a\n    - b\n  strength: single-run\n"
    markdown = parse(record, "knowledge/source/ledgers/EV-2.yaml").markdown
    assert markdown.index("**strength**") < markdown.index("### runs")


def test_unparseable_record_is_indexed_as_text_with_a_warning():
    document = parse(b"key: [unclosed\n  bad: indent\n", "knowledge/source/ledgers/broken.yaml")
    assert "unclosed" in document.markdown
    assert any("could not parse" in w for w in document.warnings)


def test_parser_dispatch_by_extension():
    assert select_parser("a/b.md").name == "native-markdown"
    assert select_parser("a/b.yaml").name == "native-record"
    assert select_parser("a/b.txt").name == "native-plaintext"
    assert select_parser("a/b.pdf").name == "docling"


def test_unknown_extension_is_rejected():
    with pytest.raises(UnsupportedSource):
        select_parser("a/b.parquet")


def _document(markdown: str) -> ParsedDocument:
    return ParsedDocument(markdown=markdown, parser="t", parser_version="t")


def test_replacement_characters_are_reported():
    warnings = validate_parse(_document("The curve E over �_p is generic."), "x.pdf")
    assert any("replacement characters" in w for w in warnings)


def test_unterminated_display_equation_is_reported():
    warnings = validate_parse(_document("Then $$P(m) = 1/m!\n\nmore text ∀"), "x.pdf")
    assert any("unterminated" in w for w in warnings)


def test_empty_display_equation_is_reported():
    warnings = validate_parse(_document("Then $$$$ holds for all ∀ x."), "x.pdf")
    assert any("empty display equations" in w for w in warnings)


def test_running_headers_are_reported():
    body = "\n".join(["Proceedings of the Conference on Curves"] + [f"line {i} of body text here" for i in range(60)])
    body = "\n".join([body] + ["Proceedings of the Conference on Curves"] * 6)
    warnings = validate_parse(_document(body), "x.pdf")
    assert any("running headers" in w for w in warnings)


def test_out_of_order_sections_are_reported():
    text = "\n".join(f"# {n} Section\n\nbody\n" for n in ["1", "5", "2", "6", "3", "7", "4"])
    warnings = validate_parse(_document(text), "x.pdf")
    assert any("reading order" in w for w in warnings)


def test_ragged_tables_are_reported():
    rows = ["| a | b | c |"] * 6 + ["| a | b |"] * 5
    warnings = validate_parse(_document("\n".join(rows)), "x.pdf")
    assert any("table structure is malformed" in w for w in warnings)


def test_citations_without_a_bibliography_are_reported():
    text = "See [1], [2], [3], [4], [5], [6] for details."
    warnings = validate_parse(_document(text), "x.pdf")
    assert any("no references section" in w for w in warnings)


def test_clean_document_produces_no_warnings(sample_document):
    document = parse(sample_document.encode("utf-8"), "knowledge/source/papers/x.md")
    assert document.warnings == []

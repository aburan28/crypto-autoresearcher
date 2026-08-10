#!/usr/bin/env python3
"""Regression tests for tools/claim_class_audit.py.

Runs the new frontmatter-parsing audit against the five evasion forms
recorded in VAL-20260808-71bdb1 control_checks C-4 (reconstructed verbatim
in tools/fixtures/claim_class_evasions/, per
coordination/goals/GOAL-MCE-001/batches/BATCH-a68f79/reviews/TASK-20260808-ea7bed/validation_report.yaml
lines 614-657) and asserts B2, B3, B4 and B5 are now caught -- the exact
four forms that defeated AUDIT-1 and AUDIT-2
(knowledge/TAG-CLAIM-CLASS.md sections 2-3; ledger/evidence/EV-MCE-3d6e9a.yaml
observation O-5b).

B1 is asserted NOT caught, and that is the CORRECT, expected result, not a
gap: B1 nests `tags` one level under a `meta:` mapping key
(`{'meta': {'tags': ['distinguisher', 'key-recovery']}}`), so there is no
TOP-LEVEL `tags` key for `frontmatter.get('tags')` to find. The control
check's own note calls B1 "weakest of the five... this entry would likely
be rejected elsewhere" (by the index builder, which also only reads a
top-level `tags`), and lists it "for completeness, not relied on." Asserting
B1 is NOT flagged pins that this script tests the R-CC-1 vocabulary's actual
contract -- a top-level `tags` list -- rather than any string anywhere in
the document that happens to be nested inside something called `tags`.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import claim_class_audit as cca

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "claim_class_evasions"


class FixtureDirectoryTests(unittest.TestCase):
    """Sanity: the fixture directory this test depends on actually exists
    and holds exactly the five files the task card names, byte-for-byte
    under the exact filenames the dispatch queue declared."""

    def test_fixture_directory_exists(self) -> None:
        self.assertTrue(FIXTURES.is_dir(), f"missing fixture directory: {FIXTURES}")

    def test_exact_five_fixture_filenames(self) -> None:
        expected = {
            "b1_nested_flow.md",
            "b2_multiline_flow.md",
            "b3_quoted_flow.md",
            "b4_block_trailing_comment.md",
            "b5_block_quoted.md",
        }
        actual = {p.name for p in FIXTURES.glob("*.md")}
        self.assertEqual(actual, expected)


class EvasionFormsAreCaughtTests(unittest.TestCase):
    """B2-B5: each was a MISS for both AUDIT-1 and AUDIT-2 in
    VAL-20260808-71bdb1 C-4. Each must be a HIT for the new script."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.hits, cls.skipped = cca.scan(str(FIXTURES))

    def test_no_files_were_skipped(self) -> None:
        """All five fixtures are syntactically valid YAML frontmatter; none
        should hit the skip/error path. A skip here would mean a fixture
        was miscopied from the specification, not that the audit works."""
        self.assertEqual(self.skipped, [], f"unexpected skips: {self.skipped}")

    def test_b2_multiline_flow_sequence_is_caught(self) -> None:
        self.assertTrue(
            any(h.endswith("b2_multiline_flow.md") for h in self.hits),
            "B2 (multi-line flow sequence) was not caught -- AUDIT-1 needed "
            "'key-recovery' on a line literally starting 'tags:'; it is on "
            "the continuation line instead.",
        )

    def test_b3_quoted_flow_items_are_caught(self) -> None:
        self.assertTrue(
            any(h.endswith("b3_quoted_flow.md") for h in self.hits),
            "B3 (quoted flow items) was not caught -- AUDIT-1's regex needs "
            "the bare token immediately after the delimiter; a quote breaks it.",
        )

    def test_b4_block_trailing_comment_is_caught(self) -> None:
        self.assertTrue(
            any(h.endswith("b4_block_trailing_comment.md") for h in self.hits),
            "B4 (block item with a trailing comment) was not caught -- "
            "AUDIT-2 anchors with [[:space:]]*$, which a trailing comment breaks.",
        )

    def test_b5_block_quoted_items_are_caught(self) -> None:
        self.assertTrue(
            any(h.endswith("b5_block_quoted.md") for h in self.hits),
            "B5 (block item, quoted) was not caught -- AUDIT-2 matches the "
            "bare token only; a quote character breaks it.",
        )

    def test_b1_nested_under_mapping_is_correctly_not_caught(self) -> None:
        """NOT a gap. See the module docstring and the task's own note: B1
        has no top-level `tags` key, so frontmatter.get('tags') is None and
        {'distinguisher','key-recovery'} cannot be a subset of the empty
        set. This is the R-CC-1 contract working as specified, not a miss."""
        self.assertFalse(
            any(h.endswith("b1_nested_flow.md") for h in self.hits),
            "B1 was flagged, but it should not be: it carries no top-level "
            "`tags` key (tags lives under `meta:`), so this would be a false "
            "positive against the documented contract, not a caught evasion.",
        )

    def test_exactly_four_hits_from_the_fixture_directory(self) -> None:
        """Positive control, restated as a count so a future fixture drift
        (e.g. someone editing b1 to also carry a top-level tags key) fails
        loudly rather than the individual endswith() checks quietly staying
        green for the wrong reason."""
        self.assertEqual(len(self.hits), 4, f"got hits: {self.hits}")


class PositiveControlTests(unittest.TestCase):
    """GATE-A(ii): 'it prints nothing' is never a result by itself. Prove
    the check can fire at all by pointing it at a directory built to
    contain nothing BUT the caught forms, and confirm it is non-empty."""

    def test_audit_fires_on_a_directory_containing_only_caught_evasions(self) -> None:
        hits, _skipped = cca.scan(str(FIXTURES))
        self.assertGreater(
            len(hits), 0,
            "the audit produced zero hits against a fixture directory built "
            "to contain four should-be-caught evasions -- either the check "
            "is dead or the fixtures regressed; this must never be silently green",
        )


class TagSetUnitTests(unittest.TestCase):
    """Direct unit coverage of tag_set(), independent of the fixture files,
    exercising the GATE-A adversarial cases recorded in the execution
    report (string tags, YAML !!set, mapping-shaped tags, non-string list
    members)."""

    def test_missing_tags_key_is_empty(self) -> None:
        self.assertEqual(cca.tag_set({}), set())

    def test_null_tags_is_empty(self) -> None:
        self.assertEqual(cca.tag_set({"tags": None}), set())

    def test_bare_string_tag_is_one_tag_not_exploded_into_characters(self) -> None:
        """GATE-A case: tags as a single string, not a list. set('distinguisher')
        would otherwise silently iterate letters; that must not happen."""
        result = cca.tag_set({"tags": "distinguisher"})
        self.assertEqual(result, {"distinguisher"})
        self.assertNotIn("d", result)

    def test_string_containing_both_tokens_as_substrings_is_not_a_violation(self) -> None:
        """A single string is one tag, however it reads, not two."""
        result = cca.tag_set({"tags": "distinguisher, key-recovery"})
        self.assertFalse(cca.BANNED_PAIR <= result)

    def test_list_with_both_tokens_is_caught(self) -> None:
        result = cca.tag_set({"tags": ["distinguisher", "key-recovery"]})
        self.assertTrue(cca.BANNED_PAIR <= result)

    def test_yaml_set_with_both_tokens_is_caught(self) -> None:
        """GATE-A case G11 (see execution report): a real Python `set`,
        which PyYAML's safe constructor produces for a YAML !!set node, is
        not a list or tuple. tag_set() must accept it explicitly."""
        result = cca.tag_set({"tags": {"distinguisher", "key-recovery"}})
        self.assertTrue(cca.BANNED_PAIR <= result)

    def test_non_string_list_members_do_not_crash_and_are_ignored(self) -> None:
        result = cca.tag_set(
            {"tags": ["distinguisher", 42, {"nested": "mapping"}, "key-recovery", True]}
        )
        self.assertEqual(result, {"distinguisher", "key-recovery"})

    def test_mapping_shaped_tags_is_a_disclosed_non_catch(self) -> None:
        """GATE-A case G12: tags as a mapping keyed by the tokens is a
        DIFFERENT shape from the documented tags-list contract and is
        deliberately not treated as equivalent -- see tag_set()'s
        docstring and knowledge/TAG-CLAIM-CLASS-v2.md. Pinned here so this
        boundary stays a documented decision, not a silent regression
        target if someone tries to 'fix' it without the same reasoning."""
        result = cca.tag_set({"tags": {"distinguisher": True, "key-recovery": True}})
        self.assertEqual(result, set())


class ExtractFrontmatterTests(unittest.TestCase):
    """Direct unit coverage of extract_frontmatter()."""

    def test_no_leading_delimiter_is_not_an_error(self) -> None:
        fm, err = cca.extract_frontmatter("# just a markdown file\n\nbody text\n")
        self.assertIsNone(fm)
        self.assertIsNone(err)

    def test_unterminated_frontmatter_is_reported_not_raised(self) -> None:
        fm, err = cca.extract_frontmatter("---\ntags: [distinguisher]\n\nno closing delimiter\n")
        self.assertIsNone(fm)
        self.assertIsNotNone(err)
        self.assertIn("no closing", err)

    def test_empty_frontmatter_block_is_valid(self) -> None:
        fm, err = cca.extract_frontmatter("---\n---\n\nbody\n")
        self.assertEqual(fm, {})
        self.assertIsNone(err)

    def test_only_the_first_of_two_frontmatter_like_blocks_is_read(self) -> None:
        """GATE-A case: two '---'-delimited blocks in one file. Only the
        first is frontmatter; the rest is body, however it looks."""
        text = (
            "---\ntags: [something-else]\n---\n"
            "---\ntags: [distinguisher, key-recovery]\n---\n"
        )
        fm, err = cca.extract_frontmatter(text)
        self.assertIsNone(err)
        self.assertEqual(fm, {"tags": ["something-else"]})

    def test_non_mapping_frontmatter_block_is_reported_not_raised(self) -> None:
        """GATE-A case: the block between the delimiters is a bare YAML
        list, not a mapping. frontmatter.get('tags') would crash on a list;
        this must be caught and reported instead."""
        fm, err = cca.extract_frontmatter("---\n- distinguisher\n- key-recovery\n---\nbody\n")
        self.assertIsNone(fm)
        self.assertIsNotNone(err)
        self.assertIn("mapping", err)

    def test_invalid_yaml_is_reported_not_raised(self) -> None:
        fm, err = cca.extract_frontmatter("---\ntags: [unterminated flow list\n---\nbody\n")
        self.assertIsNone(fm)
        self.assertIsNotNone(err)
        self.assertIn("YAML parse error", err)

    def test_unsafe_python_tag_is_refused_not_executed(self) -> None:
        """GATE-A case G13: yaml.safe_load must refuse to construct an
        arbitrary Python object even when a file tries to ask for one."""
        fm, err = cca.extract_frontmatter(
            "---\ntags: !!python/tuple [distinguisher, key-recovery]\n---\nbody\n"
        )
        self.assertIsNone(fm)
        self.assertIsNotNone(err)
        self.assertIn("YAML parse error", err)


class ScanRobustnessTests(unittest.TestCase):
    """GATE-A: a scan must never crash on a bad file, and must report the
    bad file rather than silently treating it as clean."""

    def test_scan_survives_a_mixed_directory_without_raising(self) -> None:
        # The fixture directory alone already exercises five real files;
        # this asserts scan() completes and returns the expected shape.
        hits, skipped = cca.scan(str(FIXTURES))
        self.assertIsInstance(hits, list)
        self.assertIsInstance(skipped, list)

    def test_nonexistent_root_yields_no_hits_no_crash(self) -> None:
        hits, skipped = cca.scan(str(FIXTURES / "does-not-exist"))
        self.assertEqual(hits, [])
        self.assertEqual(skipped, [])


if __name__ == "__main__":
    unittest.main()

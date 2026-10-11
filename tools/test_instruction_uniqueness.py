"""Tests for tools/instruction_uniqueness.py.

They use the dependency-free `lexical` backend, so they run anywhere; the
semantic backends (`bge`, `model2vec`) are measured by hand, see the tool.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import instruction_uniqueness as iu  # noqa: E402


class SegmentationTests(unittest.TestCase):
    def test_code_blocks_and_headings_are_not_statements(self):
        text = (
            "# Title\n\n"
            "```sh\npython3 do_not_count_this_command --at all\n```\n\n"
            "## Section\n\nOne rule says exactly this thing. A second rule says another.\n"
        )
        got = [s.text for s in iu.segment("X.md", text)]
        self.assertEqual(got, ["One rule says exactly this thing.",
                               "A second rule says another."])

    def test_sentence_split_never_cuts_inside_inline_code(self):
        text = "Run `tools/a.py --x. Then` before you merge it. Next sentence here now.\n"
        got = [s.text for s in iu.segment("X.md", text)]
        self.assertEqual(got[0], "Run `tools/a.py --x. Then` before you merge it.")

    def test_list_items_are_separate_statements_with_their_section(self):
        text = "## Rules\n\n- first item has enough words\n  wrapped onto two lines\n- second item has enough words too\n"
        got = iu.segment("X.md", text)
        self.assertEqual([s.text for s in got],
                         ["first item has enough words wrapped onto two lines",
                          "second item has enough words too"])
        self.assertEqual({s.section for s in got}, {"Rules"})

    def test_table_header_and_separator_are_skipped_rows_kept(self):
        text = ("| role | owns | policy |\n| --- | --- | --- |\n"
                "| Coordinator | owns the whole queue | `policy-a` |\n"
                "| Executor | runs approved experiments | `policy-b` |\n")
        got = iu.segment("X.md", text)
        self.assertEqual(len(got), 2)
        self.assertEqual(got[0].table, got[1].table)
        self.assertTrue(got[0].text.startswith("Coordinator"))


class MeasureTests(unittest.TestCase):
    def test_a_restated_rule_is_flagged(self):
        report = iu.measure({"A.md": (
            "## One\n\nNever merge a pull request while any required check is red.\n\n"
            "## Two\n\nNever merge a pull request while any required check is red.\n\n"
            "## Three\n\nEvery record id carries a random six hex suffix from the allocator.\n"
        )}, "lexical")
        self.assertEqual(len(report["near_duplicates"]), 1)
        self.assertEqual(report["statements"], 3)

    def test_rows_of_one_table_are_never_duplicates_of_each_other(self):
        report = iu.measure({"A.md": (
            "| a | b |\n| --- | --- |\n"
            "| Reviewer | review-adversarial xhigh independent session |\n"
            "| Validator | review-adversarial xhigh independent session |\n"
        )}, "lexical")
        self.assertEqual(report["near_duplicates"], [])

    def test_intentional_repeats_are_reported_apart(self):
        phrase = "never dispatch a task you cannot rank ahead of doing nothing"
        report = iu.measure({"A.md": f"## One\n\nSo {phrase}.\n\n## Two\n\nThus {phrase}.\n"},
                            "lexical")
        self.assertEqual(report["near_duplicates"], [])
        self.assertEqual(len(report["intentional_repeats"]), 1)

    def test_effective_rank_counts_distinct_directions(self):
        self.assertAlmostEqual(iu.effective_rank(np.eye(5)), 5.0, places=6)
        same = np.tile(np.array([[1.0, 0.0, 0.0]]), (4, 1))
        self.assertAlmostEqual(iu.effective_rank(same), 1.0, places=6)


class ContractTests(unittest.TestCase):
    """The always-loaded contract states each rule once."""

    def test_no_rule_is_restated_word_for_word(self):
        report = iu.measure(iu.read_worktree(), "lexical")
        self.assertEqual(
            report["near_duplicates"], [],
            "AGENTS.md/CLAUDE.md restate a statement; point at it instead "
            "(python3 tools/instruction_uniqueness.py names the pair)")


if __name__ == "__main__":
    unittest.main()

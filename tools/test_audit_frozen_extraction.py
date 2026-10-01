"""Tests for tools/audit_frozen_extraction.py.

The load-bearing assertion is the NAGAO-2013-549 regression: that package's
frozen markdown detaches 63 of its 73 large operators from their operands, which
makes Lemma 2's graded monomial-order hypothesis read as a vacuous per-variable
one. If that stops being detected, the detector has broken.
"""

import tempfile
import unittest
from pathlib import Path

import audit_frozen_extraction as audit

REPO = Path(__file__).resolve().parent.parent


class TestDetectors(unittest.TestCase):
    def test_orphaned_operator_is_found_with_its_context(self):
        md = "some prose\n∑\nmore prose\n"
        found = audit.orphaned_operators(md)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["operator"], "∑")
        self.assertEqual(found[0]["line"], 2)
        self.assertEqual(found[0]["before"], ["some prose"])

    def test_an_operator_inside_a_line_is_not_orphaned(self):
        """Only a BARE operator line signals detachment."""
        self.assertEqual(audit.orphaned_operators("F := ∑ G_i (X^p - X)\n"), [])

    def test_blank_lines_do_not_end_a_shredded_run(self):
        """The regression that hid 37 of 38 runs on the first attempt.

        The shredding interleaves blank lines between fragments, so treating a
        blank as a run boundary hides exactly what is being looked for.
        """
        md = "prose here\n\ni\n\nei >\n\nX ei\n\nX fi\n\nprose again\n"
        runs = audit.fragment_runs(md, minimum=4)
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0]["length"], 4)
        self.assertEqual(runs[0]["fragments"], ["i", "ei >", "X ei", "X fi"])

    def test_a_run_shorter_than_the_minimum_is_not_reported(self):
        self.assertEqual(audit.fragment_runs("prose\n\ni\n\nj\n\nprose\n", minimum=4), [])

    def test_ordinary_prose_produces_no_findings(self):
        md = ("This is an ordinary paragraph of running text that says nothing\n"
              "mathematical at all and should be flagged by neither detector.\n")
        self.assertEqual(audit.orphaned_operators(md), [])
        self.assertEqual(audit.fragment_runs(md), [])

    def test_operator_counts_ignore_absent_operators(self):
        self.assertEqual(audit.operator_counts("a ∑ b ∑ c"), {"∑": 2})
        self.assertEqual(audit.operator_counts("no operators here"), {})


class TestPackageAudit(unittest.TestCase):
    def test_refuses_a_directory_without_the_two_required_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(SystemExit):
                audit.audit(Path(tmp))


class TestNagao2013549Regression(unittest.TestCase):
    """The confirmed defect, pinned. See inputs/NAGAO-2013-549/errata-extraction-20260921.md."""

    @classmethod
    def setUpClass(cls):
        package = REPO / "inputs" / "NAGAO-2013-549"
        if not (package / "paper_fulltext.md").exists():
            raise unittest.SkipTest("NAGAO-2013-549 package absent")
        try:
            cls.result = audit.audit(package)
        except SystemExit as exc:
            raise unittest.SkipTest(str(exc)) from exc

    def test_nothing_was_dropped_only_detached(self):
        """Frozen and fresh hold the SAME operator counts.

        This is the distinction the errata turns on: a dropped formula announces
        itself, a detached one silently re-reads as something weaker.
        """
        self.assertEqual(
            self.result["large_operators_in_frozen"],
            self.result["large_operators_in_fresh"],
        )

    def test_most_operators_are_orphaned(self):
        total = sum(self.result["large_operators_in_frozen"].values())
        self.assertGreaterEqual(total, 70)
        # A floor, not an exact count: the assertion is that the great majority
        # are detached, which is what makes the package unsafe to read at a
        # formula. Pinning 63 exactly would pin the detector's line-splitting.
        self.assertGreater(self.result["orphaned_operator_lines"], total * 0.8)

    def test_the_frozen_markdown_is_far_longer_than_a_clean_extraction(self):
        self.assertGreater(
            self.result["frozen_lines"], 2 * self.result["fresh_extraction_lines"]
        )

    def test_the_lemma_2_region_is_shredded_into_many_separate_runs(self):
        """Lines 685-945 carry Lemma 2's statement and proof.

        Asserted as "many runs in the region" rather than "the single worst run
        in the paper", which is what an earlier, over-sensitive version of the
        detector appeared to show. Sections 3-4 are in fact worse. The claim that
        survives is that this region is shredded throughout, which is what makes
        it unsafe to read from the markdown alone.
        """
        import audit_frozen_extraction as module
        frozen = (REPO / "inputs" / "NAGAO-2013-549" / "paper_fulltext.md").read_text(
            errors="replace"
        )
        runs = module.fragment_runs(frozen)
        in_region = [r for r in runs if r["start_line"] <= 945 and r["end_line"] >= 685]
        self.assertGreaterEqual(len(in_region), 6, in_region)
        self.assertGreaterEqual(sum(r["length"] for r in in_region), 50)

    def test_the_graded_order_hypothesis_is_unreadable_in_the_frozen_text(self):
        """The specific passage the errata is about."""
        frozen = (REPO / "inputs" / "NAGAO-2013-549" / "paper_fulltext.md").read_text(
            errors="replace"
        )
        index = frozen.index("Fix some monomial order")
        window = frozen[index:index + 200]
        # The graded condition requires a product and a sum next to their
        # operands; in the frozen text the line ends right after "satisfying".
        self.assertIn("satisfying", window)
        first_line = window.split("\n")[0]
        self.assertTrue(
            first_line.rstrip().endswith("satisfying"),
            f"the passage no longer breaks after 'satisfying': {first_line!r}",
        )

    def test_the_supplementary_extraction_carries_the_passage_intact(self):
        clean = REPO / "inputs" / "NAGAO-2013-549" / "paper_fulltext.pymupdf.txt"
        if not clean.exists():
            self.skipTest("supplementary extraction absent")
        text = clean.read_text(errors="replace")
        index = text.index("Fix some monomial order")
        window = text[index:index + 120]
        self.assertIn("∏", window)
        self.assertIn("∑", window)
        # both sums of the graded condition, on the same short window
        self.assertIn("when ∑ei > ∑fi", window.replace("\n", ""))


if __name__ == "__main__":
    unittest.main(verbosity=2)

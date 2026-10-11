"""The instruction word budgets (review item P1.6) hold on the live tree and fail
loudly on a synthetic tree that overruns them."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_instruction_budget as cib  # noqa: E402


class LiveTree(unittest.TestCase):
    def test_always_loaded_and_every_wake_are_within_budget(self):
        report = cib.measure()
        self.assertEqual(cib.failures(report), [])
        self.assertLessEqual(report["always_loaded_total"], cib.ALWAYS_LOADED_BUDGET)
        self.assertTrue(report["wakes"], "no skills or agents measured")

    def test_claude_md_is_a_pointer(self):
        # The sibling cairn repository's pattern: one normative file, not two
        # that drift. A CLAUDE.md past this size has started carrying rules.
        self.assertLess(report_words("CLAUDE.md"), 600)


def report_words(name: str) -> int:
    return cib.words(cib.REPO / name)


class SyntheticTree(unittest.TestCase):
    def test_overruns_name_the_file_and_the_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("word " * (cib.ALWAYS_LOADED_BUDGET - 10))
            (root / "CLAUDE.md").write_text("word " * 20)
            skill = root / ".claude/skills/big/SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("word " * 3_200)
            small = root / ".claude/skills/small/SKILL.md"
            small.parent.mkdir(parents=True)
            small.write_text("word " * 10)
            report = cib.measure(root)
            bad = cib.failures(report)
        self.assertEqual(len(bad), 2, bad)
        self.assertIn(
            f"always-loaded instruction is {cib.ALWAYS_LOADED_BUDGET + 10} words", bad[0])
        self.assertIn(".claude/skills/big/SKILL.md", bad[1])
        self.assertNotIn("small", "\n".join(bad))

    def test_main_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("fine\n")
            (root / "CLAUDE.md").write_text("fine\n")
            self.assertEqual(cib.main(["--repo-root", str(root)]), 0)
            (root / "AGENTS.md").write_text("word " * (cib.ALWAYS_LOADED_BUDGET + 1))
            self.assertEqual(cib.main(["--repo-root", str(root)]), 1)


if __name__ == "__main__":
    unittest.main()

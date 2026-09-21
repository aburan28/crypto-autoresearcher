"""Pins the blind-history check added for CORR-20260905-547849.

WHY THIS EXISTS. `blind_from` is a list of FILES, so every independence check
this program had could only see declared FILE reads. A commit message is not a
file: on 2026-09-05 a reverted commit's message still stated a blind phase's
protected verdict, and `git log --oneline` -- a routine orientation command in
nobody's blind list -- displayed it twice on the branch the blind agent was to
run in. Reverting restored the files and could not retract the message.

The load-bearing test here is `test_it_catches_a_real_leak_and_clears_a_clean_ref`:
a checker that never fires is not a check, and one that always fires is not one
either. Both directions are exercised on real git history built in the test.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_review_independence as CRI  # noqa: E402


def _git(repo, *args):
    out = subprocess.run(["git", "-C", str(repo), *args],
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    return out.stdout


def _hashes(*values):
    return {hashlib.sha256(v.encode()).hexdigest(): f"label for {i}"
            for i, v in enumerate(values)}


class DeclarationTests(unittest.TestCase):
    def test_absent_declaration_is_uncheckable_never_a_pass(self):
        # Silence must not read as a guarantee. This is the whole reason the
        # original rule failed: it was declared and never enforced.
        problems = CRI.check_blind_history("HEAD", {})
        self.assertTrue(problems)
        self.assertIn("UNCHECKABLE", problems[0])

    def test_declaration_accepts_list_or_mapping(self):
        digest = hashlib.sha256(b"7.5").hexdigest()
        as_list = {"batch": {"blind_phase_hygiene": {
            "protected_sha256": [digest]}}}
        as_map = {"batch": {"blind_phase_hygiene": {
            "protected_sha256": {digest: "the crossover"}}}}
        self.assertEqual(set(CRI.protected_hashes(as_list)), {digest})
        self.assertEqual(CRI.protected_hashes(as_map)[digest], "the crossover")

    def test_missing_or_malformed_blocks_yield_nothing(self):
        for doc in ({}, {"batch": {}}, {"batch": {"blind_phase_hygiene": None}},
                    {"batch": {"blind_phase_hygiene": {"protected_sha256": 7}}}):
            self.assertEqual(CRI.protected_hashes(doc), {})


class TokenHashTests(unittest.TestCase):
    def test_numbers_and_words_are_both_recognised(self):
        found = CRI._token_hashes("verdict literals_faithful at 2^106.5 bits")
        self.assertIn(hashlib.sha256(b"106.5").hexdigest(), found)
        self.assertIn(hashlib.sha256(b"literals_faithful").hexdigest(), found)

    def test_a_value_at_different_precision_is_NOT_caught(self):
        # Stated as a limitation in the module docstring, and pinned here so a
        # future reader does not mistake this check for something stronger.
        found = CRI._token_hashes("the figure is 106.50 bits")
        self.assertNotIn(hashlib.sha256(b"106.5").hexdigest(), found)


class RealHistoryTests(unittest.TestCase):
    def test_it_catches_a_real_leak_and_clears_a_clean_ref(self):
        """Both directions, on real commits, in a throwaway repo."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _git(repo, "init", "-q", "-b", "main")
            _git(repo, "config", "user.email", "t@example.test")
            _git(repo, "config", "user.name", "t")
            (repo / "a.txt").write_text("x\n")
            _git(repo, "add", "a.txt")
            _git(repo, "commit", "-q", "-m", "clean: a commit naming no value")
            clean = _git(repo, "rev-parse", "HEAD").strip()

            # The leak, in the shape that actually happened: a summary commit
            # message stating the protected verdict and a protected figure.
            (repo / "b.txt").write_text("y\n")
            _git(repo, "add", "b.txt")
            _git(repo, "commit", "-q", "-m",
                 "snapshot: verdict literals_faithful, 256 -> 2^106.5")
            leaky = _git(repo, "rev-parse", "HEAD").strip()

            hashes = _hashes("literals_faithful", "106.5")

            problems = CRI.check_blind_history(leaky, hashes, repo=str(repo))
            self.assertTrue(problems, "a checker that never fires is not a check")
            self.assertTrue(any(leaky[:9] in p for p in problems))

            self.assertEqual(
                CRI.check_blind_history(clean, hashes, repo=str(repo)), [],
                "a checker that always fires is not a check either")

    def test_reverting_the_files_does_not_clear_the_message(self):
        """The exact mechanism of CORR-20260905-547849."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _git(repo, "init", "-q", "-b", "main")
            _git(repo, "config", "user.email", "t@example.test")
            _git(repo, "config", "user.name", "t")
            (repo / "seed.txt").write_text("s\n")
            _git(repo, "add", "seed.txt")
            _git(repo, "commit", "-q", "-m", "seed")
            (repo / "leak.txt").write_text("z\n")
            _git(repo, "add", "leak.txt")
            _git(repo, "commit", "-q", "-m", "snapshot: verdict literals_faithful")
            _git(repo, "revert", "--no-edit", "HEAD")

            hashes = _hashes("literals_faithful")
            problems = CRI.check_blind_history("HEAD", hashes, repo=str(repo))
            self.assertTrue(
                problems,
                "the revert restores the files and cannot retract the message")

    def test_the_reported_problem_never_prints_the_protected_value(self):
        # The output is read by the same people the blind phase protects.
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _git(repo, "init", "-q", "-b", "main")
            _git(repo, "config", "user.email", "t@example.test")
            _git(repo, "config", "user.name", "t")
            (repo / "a").write_text("a\n")
            _git(repo, "add", "a")
            _git(repo, "commit", "-q", "-m", "snapshot: 2^106.5 bits")
            digest = hashlib.sha256(b"106.5").hexdigest()
            problems = CRI.check_blind_history(
                "HEAD", {digest: "a bits-256 figure"}, repo=str(repo))
            self.assertTrue(problems)
            for problem in problems:
                self.assertNotIn("106.5", problem)


if __name__ == "__main__":
    unittest.main(verbosity=2)

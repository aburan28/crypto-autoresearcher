#!/usr/bin/env python3
"""Tests for the merge-hygiene gate.

Every test here replays a defect that actually reached main in the PR #55/#58
window. If one regresses, this tool is decorative:

  - `test_catches_the_markers_that_shipped` — nine files, including two
    coordinator decisions and the technique abstract `CLAUDE.md` names, were
    merged holding literal `<<<<<<< HEAD` lines. Nothing looked for them.
  - `test_catches_a_record_this_branch_broke` — a record that does not parse
    cannot be schema-checked, so breaking one REMOVES validator errors. Under
    a relative gate that reads as an improvement.
  - `test_baseline_does_not_excuse_a_newly_broken_record` — the baseline exists
    only so the gate could be switched on over a corpus with 19 pre-existing
    failures. It must never absorb a new one.
  - `test_catches_the_id_allocated_twice` — `DEC-20260728-004` was spent on two
    unrelated decisions by two branches, each of which had correctly grepped
    its own tree. Only a comparison against the remote can see it.
  - `test_setext_heading_is_not_a_conflict_marker` — a bare `=======` rule is
    legal Markdown and appears throughout `knowledge/`. Matching it would make
    the gate fire on the corpus it protects.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_merge_hygiene as mh


def git(cwd, *args):
    return subprocess.run(("git",) + args, cwd=cwd, capture_output=True,
                          text=True, check=True)


class _Repo:
    """A throwaway git repo with `mh` pointed at it."""

    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = self.tmp.name
        git(self.path, "init", "-q", "-b", "main")
        git(self.path, "config", "user.email", "t@example.com")
        git(self.path, "config", "user.name", "t")
        self._saved = mh.REPO
        mh.REPO = self.path
        return self

    def __exit__(self, *exc):
        mh.REPO = self._saved
        self.tmp.cleanup()

    def write(self, rel, text):
        full = os.path.join(self.path, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as fh:
            fh.write(text)

    def commit(self, msg="c"):
        git(self.path, "add", "-A")
        git(self.path, "commit", "-q", "-m", msg)


# The exact shape that shipped: a record whose two sides were left in place.
#
# Assembled from pieces rather than written literally, because a test file
# containing a real marker at the start of a line would be caught by the very
# gate it tests -- and the honest fix is to not put one there, not to carve an
# exception into the gate. (The first draft of this file did exactly that, and
# the gate rejected it.)
_OPEN = "<" * 7
_MID = "=" * 7
_CLOSE = ">" * 7

CONFLICTED = (
    "coordinator_decision:\n"
    "  id: DEC-20260728-004\n"
    f"{_OPEN} HEAD\n"
    "  decision: revise\n"
    f"{_MID}\n"
    "  decision: support\n"
    f"{_CLOSE} origin/main\n"
)


class MarkerTests(unittest.TestCase):
    def test_catches_the_markers_that_shipped(self) -> None:
        with _Repo() as r:
            r.write("ledger/decisions/DEC-20260728-004.yaml", CONFLICTED)
            r.commit()
            bad = mh.check_markers(mh.tracked_files())
            self.assertEqual(len(bad), 1, bad)
            self.assertIn("unresolved conflict marker", bad[0])

    def test_setext_heading_is_not_a_conflict_marker(self) -> None:
        with _Repo() as r:
            r.write("knowledge/techniques/KN-TECH-056.md",
                    "Heading\n=======\n\nbody\n")
            r.commit()
            self.assertEqual(mh.check_markers(mh.tracked_files()), [])

    def test_clean_tree_passes(self) -> None:
        with _Repo() as r:
            r.write("ledger/decisions/DEC-1.yaml", "coordinator_decision:\n  id: x\n")
            r.commit()
            self.assertEqual(mh.check_markers(mh.tracked_files()), [])


class ParseTests(unittest.TestCase):
    def test_catches_a_record_this_branch_broke(self) -> None:
        with _Repo() as r:
            # Unquoted ": " inside a plain scalar — the defect that made
            # DEC-20260727-010 unreadable.
            r.write("ledger/decisions/DEC-20260727-010.yaml",
                    "coordinator_decision:\n"
                    "  scope:\n"
                    "    added: 4 (two per file); removed: 0\n")
            r.commit()
            bad = mh.check_parses(mh.tracked_files())
            self.assertEqual(len(bad), 1, bad)
            self.assertIn("does not parse", bad[0])

    def test_baseline_does_not_excuse_a_newly_broken_record(self) -> None:
        with _Repo() as r:
            r.write("ledger/a.yaml", "x: [unterminated\n")
            r.write("ledger/b.yaml", "y: [also broken\n")
            # Only the first is grandfathered.
            r.write("tools/merge_hygiene_baseline.txt",
                    mh.BASELINE_HEADER + "ledger/a.yaml\n")
            r.commit()
            mh.BASELINE = os.path.join(r.path, "tools",
                                       "merge_hygiene_baseline.txt")
            try:
                bad = mh.check_parses(mh.tracked_files())
            finally:
                mh.BASELINE = os.path.join(mh.REPO, "tools",
                                           "merge_hygiene_baseline.txt")
            self.assertEqual(len(bad), 1, bad)
            self.assertIn("ledger/b.yaml", bad[0])

    def test_malformed_json_queue_is_caught(self) -> None:
        with _Repo() as r:
            r.write("coordination/goals/G/batches/B/dispatch_queue.json",
                    '{"tasks": [ }')
            r.commit()
            bad = mh.check_parses(mh.tracked_files())
            self.assertEqual(len(bad), 1, bad)


class CollisionTests(unittest.TestCase):
    def test_catches_the_id_allocated_twice(self) -> None:
        """Both branches grepped their own tree correctly. Both got 004."""
        with _Repo() as r:
            r.write("README.md", "base\n")
            r.commit("base")
            git(r.path, "branch", "-q", "other")

            # main spends DEC-20260728-004 on the BATCH-003 support ruling.
            git(r.path, "checkout", "-q", "other")
            r.write("ledger/decisions/DEC-20260728-004.yaml",
                    "coordinator_decision:\n  id: DEC-20260728-004\n"
                    "  decision: support\n")
            r.commit("other allocates 004")

            # The branch spends it on an unrelated BATCH-002 close-out.
            git(r.path, "checkout", "-q", "main")
            r.write("ledger/decisions/DEC-20260728-004.yaml",
                    "coordinator_decision:\n  id: DEC-20260728-004\n"
                    "  decision: revise\n")
            r.commit("branch allocates 004")

            bad = mh.check_collisions("other")
            self.assertEqual(len(bad), 1, bad)
            self.assertIn("already published", bad[0])
            self.assertIn("Do not resolve this by choosing a side", bad[0])

    def test_identical_content_is_not_a_collision(self) -> None:
        with _Repo() as r:
            r.write("README.md", "base\n")
            r.commit("base")
            git(r.path, "branch", "-q", "other")
            same = "coordinator_decision:\n  id: DEC-1\n"
            git(r.path, "checkout", "-q", "other")
            r.write("ledger/decisions/DEC-1.yaml", same)
            r.commit("other")
            git(r.path, "checkout", "-q", "main")
            r.write("ledger/decisions/DEC-1.yaml", same)
            r.commit("branch")
            self.assertEqual(mh.check_collisions("other"), [])

    def test_missing_ref_is_reported_not_crashed(self) -> None:
        with _Repo() as r:
            r.write("README.md", "x\n")
            r.commit()
            out = mh.check_collisions("origin/nonexistent")
            self.assertTrue(out and out[0].startswith("SKIPPED:"), out)


if __name__ == "__main__":
    unittest.main()

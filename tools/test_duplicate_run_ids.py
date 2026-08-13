#!/usr/bin/env python3
"""The colliding-run-ID map may shrink, never grow.

`tools/duplicate_run_ids.yaml` freezes the run IDs that already occur under
more than one experiment. Those collisions cannot be repaired -- renumbering
rewrites committed run manifests and `tools/check_run_immutability.py` refuses
that -- so they are disclosed instead, and their validator errors are
grandfathered.

That disclosure is only honest while the set cannot grow. A NEW collision is a
new defect with a live consequence (see the module docstring of
`tools/build_duplicate_run_ids.py`), and the remedy for it is to give the run a
distinct ID before committing it, not to regenerate this map. These tests are
what make "we know about exactly these" checkable rather than asserted.

Modelled on the PRE_QUORUM_GOAL_IDS pattern in tools/validate_ledger.py: a
bounded, enumerated exemption that a later record cannot quietly join.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_duplicate_run_ids as builder


REPO = Path(__file__).resolve().parents[1]
MAP_PATH = REPO / "tools" / "duplicate_run_ids.yaml"


class DuplicateRunIdMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frozen = yaml.safe_load(MAP_PATH.read_text(encoding="utf-8"))
        cls.current = builder.document()

    def test_map_is_present_and_well_formed(self) -> None:
        self.assertEqual(self.frozen["schema"], builder.SCHEMA)
        if not self.frozen["records"]:
            self.assertEqual(self.frozen.get("collision_count", 0), 0)
            return
        for rec_id, entry in self.frozen["records"].items():
            self.assertTrue(rec_id.startswith("RUN-"), rec_id)
            self.assertGreaterEqual(len(entry["occurrences"]), 2, rec_id)
            for occurrence in entry["occurrences"]:
                self.assertTrue((REPO / occurrence["path"]).is_file(),
                                occurrence["path"])

    def test_no_new_collision_may_be_introduced(self) -> None:
        """The load-bearing one. Growth is a defect, not a map update."""
        added = sorted(set(self.current["records"]) - set(self.frozen["records"]))
        self.assertEqual(
            added, [],
            f"{len(added)} run id(s) newly collide across experiments. Give the "
            f"new run a distinct id; do NOT regenerate tools/duplicate_run_ids.yaml "
            f"to absorb it: {added[:10]}")

    def test_frozen_occurrences_still_describe_the_tree(self) -> None:
        """A collision may retire, but a recorded one must not be misdescribed."""
        for rec_id, entry in self.frozen["records"].items():
            if rec_id not in self.current["records"]:
                continue                     # retired; --check reports it as prunable
            self.assertEqual(
                entry["occurrences"],
                self.current["records"][rec_id]["occurrences"],
                f"{rec_id}: frozen occurrences no longer match the tree")

    def test_no_collision_is_tier_divergent(self) -> None:
        """The reason these are tolerable at all.

        `ctx.run_params` keeps the LAST manifest globbed for a colliding id
        while `ctx.ids` keeps the FIRST, so scale metadata is evaluated
        against an arbitrarily selected manifest. That is only harmless while
        every manifest sharing an id agrees on its scale metadata. The moment
        one does not, an evidence record can carry metadata that was checked
        against a run it never cited, so this fails loudly rather than waiting
        to be noticed.
        """
        divergent = sorted(k for k, v in self.current["records"].items()
                           if v["tier_divergent"])
        self.assertEqual(
            divergent, [],
            f"colliding run ids whose manifests disagree on scale metadata: "
            f"{divergent}. Scale metadata is ambiguous for any evidence "
            f"record citing them.")

    def test_check_mode_passes_on_the_committed_tree(self) -> None:
        result = subprocess.run(
            [sys.executable, str(REPO / "tools" / "build_duplicate_run_ids.py"),
             "--check"],
            cwd=REPO, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()

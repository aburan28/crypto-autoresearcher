#!/usr/bin/env python3
"""Prospective random-suffix GOAL identifier merge-hygiene tests."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_merge_hygiene as hygiene


class ProspectiveGoalIdentifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.git("init", "-q")
        self.git("config", "user.email", "tests@example.invalid")
        self.git("config", "user.name", "Goal Identifier Tests")
        self._write_goal("GOAL-BASE-001", sharded=False)
        self.git("add", ".")
        self.git("commit", "-qm", "base")
        self.git("tag", "base-tree")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def git(self, *arguments: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(self.root), *arguments],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def _write_goal(self, goal_id: str, *, sharded: bool) -> Path:
        path = (self.root / "ledger/goals" / goal_id / "goal.yaml"
                if sharded
                else self.root / "ledger/goals" / f"{goal_id}.yaml")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"research_goal:\n  id: {goal_id}\n  status: active\n",
            encoding="utf-8",
        )
        return path

    def _problems(self) -> list[str]:
        with mock.patch.object(hygiene, "REPO", str(self.root)):
            return hygiene.check_prospective_goal_ids("base-tree")

    def test_flat_to_sharded_legacy_migration_is_not_new_minting(self) -> None:
        (self.root / "ledger/goals/GOAL-BASE-001.yaml").unlink()
        self._write_goal("GOAL-BASE-001", sharded=True)
        self.git("add", "-A")
        self.assertEqual(self._problems(), [])

    def test_new_legacy_flat_goal_is_rejected_from_staged_worktree(self) -> None:
        self._write_goal("GOAL-NEW-002", sharded=False)
        self.git("add", "ledger/goals/GOAL-NEW-002.yaml")
        problems = self._problems()
        self.assertEqual(len(problems), 1)
        self.assertIn("GOAL-NEW-002", problems[0])

    def test_new_legacy_sharded_goal_is_rejected_after_commit(self) -> None:
        self._write_goal("GOAL-NEW-003", sharded=True)
        self.git("add", ".")
        self.git("commit", "-qm", "new legacy shard")
        problems = self._problems()
        self.assertEqual(len(problems), 1)
        self.assertIn("GOAL-NEW-003", problems[0])

    def test_new_random_flat_and_sharded_goals_are_allowed(self) -> None:
        self._write_goal("GOAL-NEW-a1b2c3", sharded=False)
        self._write_goal("GOAL-NEW-deadbe", sharded=True)
        self.git("add", ".")
        self.assertEqual(self._problems(), [])

    def test_noncanonical_new_goal_is_rejected_prospectively(self) -> None:
        self._write_goal("GOAL-NEW-abcd", sharded=False)
        self.git("add", ".")
        problems = self._problems()
        self.assertEqual(len(problems), 1)
        self.assertIn("GOAL-NEW-abcd", problems[0])

    def test_only_flat_and_sharded_heads_define_semantic_goals(self) -> None:
        paths = [
            "ledger/goals/GOAL-X-a1b2c3.yaml",
            "ledger/goals/GOAL-Y-deadbe/goal.yaml",
            "ledger/goals/GOAL-Z-001/checkpoints/BATCH-001.yaml",
        ]
        self.assertEqual(
            hygiene.goal_ids_from_paths(paths),
            {"GOAL-X-a1b2c3", "GOAL-Y-deadbe"},
        )


if __name__ == "__main__":
    unittest.main()

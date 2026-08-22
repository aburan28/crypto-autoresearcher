#!/usr/bin/env python3
"""Prospective random-suffix GOAL identifier merge-hygiene tests."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_merge_hygiene as hygiene
import validate_ledger as vl


class ProspectiveGoalIdentifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.external_temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.external_root = Path(self.external_temporary.name)
        self.git("init", "-q")
        self.git("config", "user.email", "tests@example.invalid")
        self.git("config", "user.name", "Goal Identifier Tests")
        self._write_goal("GOAL-BASE-001", sharded=False)
        self.git("add", ".")
        self.git("commit", "-qm", "base")
        self.git("tag", "base-tree")

    def tearDown(self) -> None:
        self.external_temporary.cleanup()
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

    @staticmethod
    def _goal_document(goal_id: str) -> str:
        return f"""research_goal:
  id: {goal_id}
  title: symlink fixture
  objective: prove goal targets are not followed
  question_ids: []
  status: active
  completion_criteria: [done]
  pause_conditions: [stop]
  next_action: retain the fixture boundary
  owner: coordinator
"""

    def _problems(self) -> list[str]:
        with mock.patch.object(hygiene, "REPO", str(self.root)):
            return hygiene.check_prospective_goal_ids("base-tree")

    def _symlink_problems(self) -> list[str]:
        with mock.patch.object(hygiene, "REPO", str(self.root)):
            return hygiene.check_goal_symlinks(hygiene.tracked_files())

    def _validator_context(self) -> vl.Ctx:
        context = vl.Ctx(set())
        with mock.patch.object(vl, "REPO", str(self.root)):
            vl.check_goals(context)
        return context

    def _assert_merge_hygiene_rejects(self) -> None:
        output = StringIO()
        error = StringIO()
        with (mock.patch.object(hygiene, "REPO", str(self.root)),
              mock.patch.object(hygiene, "BASELINE",
                                str(self.root / "missing-baseline.txt")),
              mock.patch.object(sys, "argv", ["check_merge_hygiene.py", "--absolute"]),
              redirect_stdout(output), redirect_stderr(error)):
            status = hygiene.main()
        self.assertEqual(status, 1)
        self.assertIn("symlinked goal paths", error.getvalue())

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

    def test_tracked_sharded_directory_symlink_is_rejected_without_follow(self) -> None:
        target = self.external_root / "valid-goal-target"
        target.mkdir()
        (target / "goal.yaml").write_text(
            self._goal_document("GOAL-TARGET-a1b2c3"), encoding="utf-8"
        )
        link = self.root / "ledger/goals/GOAL-BYPASS-002"
        link.symlink_to(target, target_is_directory=True)
        self.git("add", "ledger/goals/GOAL-BYPASS-002")

        problems = self._symlink_problems()
        self.assertTrue(any("GOAL-BYPASS-002" in problem for problem in problems))
        self._assert_merge_hygiene_rejects()
        context = self._validator_context()
        self.assertTrue(any("goal path may not be a symlink" in error
                            for error in context.errors), context.errors)
        self.assertNotIn("GOAL-TARGET-a1b2c3", context.ids)
        self.assertNotIn("GOAL-BYPASS-002", context.ids)

    def test_dangling_sharded_directory_symlink_is_rejected(self) -> None:
        link = self.root / "ledger/goals/GOAL-DANGLING-003"
        link.symlink_to(self.external_root / "missing", target_is_directory=True)
        self.git("add", "ledger/goals/GOAL-DANGLING-003")

        self.assertTrue(self._symlink_problems())
        self._assert_merge_hygiene_rejects()
        context = self._validator_context()
        self.assertTrue(any("GOAL-DANGLING-003" in error
                            and "target was not read" in error
                            for error in context.errors), context.errors)

    def test_flat_goal_record_symlink_is_rejected_without_follow(self) -> None:
        target = self.external_root / "flat-target.yaml"
        target.write_text(self._goal_document("GOAL-TARGET-deadbe"), encoding="utf-8")
        link = self.root / "ledger/goals/GOAL-FLAT-a1b2c3.yaml"
        link.symlink_to(target)
        self.git("add", "ledger/goals/GOAL-FLAT-a1b2c3.yaml")

        self.assertTrue(self._symlink_problems())
        self._assert_merge_hygiene_rejects()
        context = self._validator_context()
        self.assertNotIn("GOAL-TARGET-deadbe", context.ids)
        self.assertNotIn("GOAL-FLAT-a1b2c3", context.ids)

    def test_nested_sharded_goal_head_symlink_is_rejected_without_follow(self) -> None:
        target = self.external_root / "nested-target.yaml"
        target.write_text(self._goal_document("GOAL-TARGET-c0ffee"), encoding="utf-8")
        link = self.root / "ledger/goals/GOAL-NESTED-a1b2c3/goal.yaml"
        link.parent.mkdir(parents=True)
        link.symlink_to(target)
        self.git("add", "ledger/goals/GOAL-NESTED-a1b2c3/goal.yaml")

        self.assertTrue(self._symlink_problems())
        self._assert_merge_hygiene_rejects()
        context = self._validator_context()
        self.assertNotIn("GOAL-TARGET-c0ffee", context.ids)
        self.assertNotIn("GOAL-NESTED-a1b2c3", context.ids)

    def test_symlinked_checkpoint_directory_is_rejected_without_follow(self) -> None:
        goal_id = "GOAL-CHECKPOINT-a1b2c3"
        head = self.root / "ledger/goals" / goal_id / "goal.yaml"
        head.parent.mkdir(parents=True)
        head.write_text(self._goal_document(goal_id), encoding="utf-8")
        target = self.external_root / "checkpoint-target"
        target.mkdir()
        (target / "BATCH-a1b2c3.yaml").write_text(
            "batch_checkpoint:\n  batch_id: BATCH-a1b2c3\n  sentinel: followed\n",
            encoding="utf-8",
        )
        checkpoints = head.parent / "checkpoints"
        checkpoints.symlink_to(target, target_is_directory=True)
        self.git("add", str(head.relative_to(self.root)),
                 str(checkpoints.relative_to(self.root)))

        self.assertTrue(self._symlink_problems())
        self._assert_merge_hygiene_rejects()
        context = self._validator_context()
        self.assertIn(goal_id, context.ids)
        self.assertNotIn("batch_checkpoints", context.records[goal_id])
        self.assertTrue(any("checkpoints" in error and "target was not read" in error
                            for error in context.errors), context.errors)

    def test_ordinary_sharded_directory_remains_valid(self) -> None:
        goal_id = "GOAL-ORDINARY-a1b2c3"
        path = self.root / "ledger/goals" / goal_id / "goal.yaml"
        path.parent.mkdir(parents=True)
        path.write_text(self._goal_document(goal_id), encoding="utf-8")
        self.git("add", str(path.relative_to(self.root)))

        self.assertEqual(self._symlink_problems(), [])
        context = self._validator_context()
        self.assertIn(goal_id, context.ids)
        self.assertFalse(any("symlink" in error for error in context.errors),
                         context.errors)


if __name__ == "__main__":
    unittest.main()

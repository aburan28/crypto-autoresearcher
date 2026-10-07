#!/usr/bin/env python3
"""Tests for tools/build_ledger_index.py and tools/portfolio_health_cache.py."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_ledger_index as bli  # noqa: E402
import portfolio_health_cache as phc  # noqa: E402


def _write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class LedgerIndexTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        _write(self.root, "ledger/proposals/IDEA-20261007-aaaaaa.yaml", (
            "idea:\n  id: IDEA-20261007-aaaaaa\n  question_id: RQ-FROB-7d8dd4\n"
            "  status: proposed\n  class: measurement\n  title: Short title\n"
            "  claim: " + "x" * 400 + "\n  mechanism: Depends on H-FROB-000001 and EXP-FROB-123456.\n"
            "  novelty_status: unverified\n  added: '2026-10-07'\n"))
        _write(self.root, "ledger/hypotheses/H-FROB-000001.yaml", (
            "hypothesis:\n  id: H-FROB-000001\n  question_id: RQ-FROB-7d8dd4\n  status: specified\n"
            "  statement: A statement.\n  mechanism: A mechanism.\n  proposal_id: IDEA-20261007-aaaaaa\n"))
        _write(self.root, "experiments/EXP-FROB-123456/specification.yaml", (
            "experiment:\n  id: EXP-FROB-123456\n  goal_id: GOAL-FROB-000001\n  status: approved\n"
            "  hypothesis_id: H-FROB-000001\n  approved_by: coordinator\n  designed_at: '2026-10-07'\n"
            "  success_criterion: ratio < 0.9\n"))
        _write(self.root, "ledger/proposals/IDEA-20261007-bbbbbb.yaml", "idea: [unclosed\n")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_rows_carry_excerpts_refs_and_area(self) -> None:
        out = self.root / "ledger" / ".index"
        summary = bli.build(self.root, out)
        rows = [json.loads(line) for line in (out / "proposals.jsonl").read_text().splitlines()]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["id"], "IDEA-20261007-aaaaaa")
        self.assertEqual(row["kind"], "proposal")
        self.assertEqual(row["status"], "proposed")
        self.assertEqual(row["date"], "2026-10-07")
        self.assertLessEqual(len(row["claim"]), bli.EXCERPT_CHARS)
        self.assertTrue(row["claim"].endswith("…"))
        self.assertIn("H-FROB-000001", row["refs"])
        self.assertIn("EXP-FROB-123456", row["refs"])
        self.assertIn("RQ-FROB-7d8dd4", row["refs"])
        self.assertNotIn("IDEA-20261007-aaaaaa", row["refs"])
        hyp = [json.loads(l) for l in (out / "hypotheses.jsonl").read_text().splitlines()]
        self.assertEqual(hyp[0]["area"], "FROB")
        self.assertEqual(hyp[0]["proposal_id"], "IDEA-20261007-aaaaaa")
        exp = [json.loads(l) for l in (out / "experiments.jsonl").read_text().splitlines()]
        self.assertEqual(exp[0]["goal_id"], "GOAL-FROB-000001")
        self.assertEqual(exp[0]["approved_by"], "coordinator")
        self.assertEqual(exp[0]["path"], "experiments/EXP-FROB-123456/specification.yaml")
        self.assertEqual(summary["kinds"]["proposals"]["rows"], 1)

    def test_unreadable_records_are_reported_not_indexed(self) -> None:
        out = self.root / "ledger" / ".index"
        summary = bli.build(self.root, out)
        self.assertEqual([u["path"] for u in summary["unreadable"]],
                         ["ledger/proposals/IDEA-20261007-bbbbbb.yaml"])
        self.assertIn("unparseable", summary["unreadable"][0]["problem"])

    def test_excerpt_collapses_whitespace_and_handles_non_strings(self) -> None:
        self.assertEqual(bli.excerpt("a\n  b\tc"), "a b c")
        self.assertIsNone(bli.excerpt(None))
        self.assertEqual(bli.excerpt({"k": 1}, 50), '{"k": 1}')


class PortfolioHealthCacheTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "ledger" / "goals").mkdir(parents=True)
        (self.root / "ledger" / "handoffs").mkdir(parents=True)
        (self.root / "experiments").mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_build_buckets_goals_and_truncates_next_action(self) -> None:
        goals = [
            {"id": "GOAL-B-000001", "bucket": "blocked", "current_batch_id": "BATCH-1",
             "ready_task_ids": [], "next_action": "y" * 1000},
            {"id": "GOAL-A-000001", "bucket": "ready", "current_batch_id": "BATCH-2",
             "ready_task_ids": ["TASK-20261007-aaaaaa"], "next_action": "short"},
        ]
        now = datetime(2026, 10, 7, 12, 0, tzinfo=timezone.utc)
        cache = phc.build(self.root, now=now, goals=goals)
        self.assertEqual(cache["generated_at"], "2026-10-07T12:00:00+00:00")
        self.assertEqual(cache["buckets"]["ready"], ["GOAL-A-000001"])
        self.assertEqual(cache["buckets"]["blocked"], ["GOAL-B-000001"])
        self.assertEqual(cache["goals"][0]["id"], "GOAL-A-000001")  # ready sorts first
        blocked = cache["goals"][1]
        self.assertLessEqual(len(blocked["next_action_excerpt"]), phc.NEXT_ACTION_EXCERPT + 2)
        self.assertTrue(blocked["next_action_excerpt"].endswith("…"))
        self.assertIn("kpis", cache)
        self.assertIn("aged_open_handoffs", cache["kpis"])

    def test_age_and_render(self) -> None:
        cache = {"generated_at": "2026-10-07T00:00:00+00:00", "commit": "abcdef1234567890",
                 "buckets": {"ready": ["GOAL-A-000001"]}, "goals": [
                     {"id": "GOAL-A-000001", "bucket": "ready", "current_batch_id": "B",
                      "ready_task_ids": ["TASK-20261007-aaaaaa"]}]}
        now = datetime(2026, 10, 7, 6, 30, tzinfo=timezone.utc)
        self.assertEqual(phc.age_hours(cache, now=now), 6.5)
        text = phc.render(cache, now=now)
        self.assertIn("age 6.5 h", text)
        self.assertIn("ready 1", text)
        self.assertIn("TASK-20261007-aaaaaa", text)
        self.assertIsNone(phc.age_hours({}))

    def test_show_without_cache_exits_2(self) -> None:
        self.assertEqual(phc.main(["--repo-root", str(self.root), "--show"]), 2)


if __name__ == "__main__":
    unittest.main()

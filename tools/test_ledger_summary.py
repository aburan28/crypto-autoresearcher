#!/usr/bin/env python3
"""Tests for the ledger census (tools/ledger_summary.py).

The census replaces a literal 18M-token "scan the ledger" instruction, so the
properties that matter are that it counts what is really there, that it does
not hide records it failed to read, and that its output stays small.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ledger_summary as ls  # noqa: E402

TOOL = Path(__file__).resolve().parent / "ledger_summary.py"


def write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, default_flow_style=False, sort_keys=False))


class LedgerSummaryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        r = self.root

        for i, status in enumerate(["proposed", "proposed", "approved", "analyzed"]):
            write(r / f"ledger/hypotheses/H-T-{i:06d}.yaml",
                  {"hypothesis": {"id": f"H-T-{i:06d}", "status": status}})
        write(r / "ledger/questions/RQ-T-000001.yaml",
              {"research_question": {"id": "RQ-T-000001", "status": "active"}})

        write(r / "ledger/decisions/DEC-20260101-aaaaaa.yaml", {"coordinator_decision": {
            "id": "DEC-20260101-aaaaaa", "recorded_at": "2026-01-01", "decision": "expand",
            "target_ids": ["H-T-000000"], "next_actions": ["older action"]}})
        write(r / "ledger/decisions/DEC-20260202-bbbbbb.yaml", {"coordinator_decision": {
            "id": "DEC-20260202-bbbbbb", "recorded_at": "2026-02-02", "decision": "support",
            "target_ids": ["H-T-000002"],
            "next_actions": [f"action {i}" for i in range(6)]}})

        # One handoff returned (archived_by set), one still open.
        write(r / "ledger/handoffs/TASK-20260101-aaaaaa.yaml", {"handoff": {
            "id": "TASK-20260101-aaaaaa", "to": "executor", "objective": "done work",
            "archived_by": "TASK-20260101-bbbbbb"}})
        write(r / "ledger/handoffs/TASK-20260101-cccccc.yaml", {"handoff": {
            "id": "TASK-20260101-cccccc", "to": "validator", "objective": "open work"}})

        # An unparseable record must be counted and named, never dropped.
        bad = r / "ledger/evidence/EV-T-000001.yaml"
        bad.parent.mkdir(parents=True, exist_ok=True)
        bad.write_text("evidence: {id: [unclosed\n")

        # EXP-T-A is approved with a run; EXP-T-B approved with none (in flight).
        write(r / "experiments/EXP-T-A/specification.yaml", {"experiment": {
            "id": "EXP-T-A", "status": "approved", "hypothesis_id": "H-T-000002"}})
        manifest = r / "experiments/EXP-T-A/runs/RUN-T-A-1/manifest.json"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps({"run": {
            "id": "RUN-T-A-1", "experiment_id": "EXP-T-A", "status": "completed_valid"}}))
        write(r / "experiments/EXP-T-B/specification.yaml", {"experiment": {
            "id": "EXP-T-B", "status": "approved", "hypothesis_id": "H-T-000003"}})
        write(r / "experiments/EXP-T-C/specification.yaml", {"experiment": {
            "id": "EXP-T-C", "status": "draft"}})

    def run_tool(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(TOOL), "--repo-root", str(self.root), *args],
                              capture_output=True, text=True)

    def report(self) -> dict:
        return json.loads(self.run_tool("--json").stdout)

    def test_counts_records_by_status(self) -> None:
        areas = self.report()["areas"]
        self.assertEqual(areas["hypotheses"]["files"], 4)
        self.assertEqual(areas["hypotheses"]["statuses"]["proposed"], 2)
        self.assertEqual(areas["hypotheses"]["statuses"]["approved"], 1)
        self.assertEqual(areas["questions"]["statuses"]["active"], 1)

    def test_unparseable_records_are_named_not_silently_dropped(self) -> None:
        evidence = self.report()["areas"]["evidence"]
        self.assertEqual(evidence["files"], 1)
        self.assertEqual(len(evidence["unparseable"]), 1)
        self.assertIn("EV-T-000001", evidence["unparseable"][0])
        self.assertIn("EV-T-000001", self.run_tool().stdout)

    def test_open_handoffs_are_those_without_archived_by(self) -> None:
        openh = self.report()["open_handoffs"]
        self.assertEqual([h["id"] for h in openh], ["TASK-20260101-cccccc"])

    def test_in_flight_is_approved_with_no_run(self) -> None:
        exp = self.report()["experiments"]
        self.assertEqual([e["id"] for e in exp["in_flight"]], ["EXP-T-B"])
        self.assertEqual(exp["specifications"]["approved"], 2)
        self.assertEqual(exp["specifications"]["draft"], 1)
        self.assertEqual(exp["runs"]["completed_valid"], 1)

    def test_decisions_are_ordered_most_recent_first(self) -> None:
        rows = self.report()["recent_decisions"]
        self.assertEqual([r["id"] for r in rows],
                         ["DEC-20260202-bbbbbb", "DEC-20260101-aaaaaa"])

    def test_long_next_action_lists_are_capped_but_the_total_is_reported(self) -> None:
        row = self.report()["recent_decisions"][0]
        self.assertEqual(len(row["next_actions"]), 3)
        self.assertEqual(row["next_actions_total"], 6)
        self.assertIn("+3 more next_actions", self.run_tool().stdout)

    def test_report_stays_small(self) -> None:
        # The census exists to be cheap; a report that grows with the corpus
        # would reintroduce the problem it was written to remove.
        self.assertLess(len(self.run_tool().stdout), 8000)

    def test_defers_integrity_to_validate_ledger(self) -> None:
        # Reimplementing step 3 here would drift from the real checker and
        # quietly disagree with it, so the census must point at it instead.
        self.assertIn("tools/validate_ledger.py", self.run_tool().stdout)

    def test_missing_ledger_exits_nonzero(self) -> None:
        with tempfile.TemporaryDirectory() as empty:
            result = subprocess.run(
                [sys.executable, str(TOOL), "--repo-root", empty],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("no ledger/", result.stderr)

    def test_one_line_collapses_whitespace(self) -> None:
        self.assertEqual(ls._one_line("a\n  b\tc"), "a b c")
        self.assertTrue(ls._one_line("x" * 400).endswith("…"))


if __name__ == "__main__":
    unittest.main()

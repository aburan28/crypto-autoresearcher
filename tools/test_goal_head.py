#!/usr/bin/env python3
"""Tests for the goal head projection (tools/goal_head.py).

The property under test throughout is HONEST COMPACTION: the projection must
be small, and everything it leaves out must be visibly marked with the command
that returns it. A silent omission would let an agent believe it had read a
whole record, which is the one failure mode worse than the bloat this tool
exists to remove.
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
import goal_head as gh  # noqa: E402

TOOL = Path(__file__).resolve().parent / "goal_head.py"


def write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, default_flow_style=False, sort_keys=False))


class GoalHeadTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

        # A flat goal carrying both declared fields and ad-hoc narrative, in the
        # shapes really seen on these records: a long next_action, a mapping
        # append-log (campaign_budget) and a list append-log.
        flat = {
            "id": "GOAL-T-00aa01",
            "status": "active",
            "title": "flat goal",
            "current_batch_id": "BATCH-00aaaa",
            "dispatch_queue_path": "coordination/goals/GOAL-T-00aa01/q.json",
            "next_action": "N" * 4000,
            "campaign_budget": {f"k{i}": "v" * 200 for i in range(20)},
            "completion_criteria": [f"criterion {i}" for i in range(5)],
            "pause_conditions": ["budget exhausted", "user requests pause"],
            "question_ids": ["RQ-T-000001"],
            "owner": "coordinator",
        }
        for i in range(30):  # ad-hoc narrative keys
            flat[f"status_note_amendment_2026080{i % 10}_batch{i:03d}"] = "X" * 900
        write(self.root / "ledger/goals/GOAL-T-00aa01.yaml", {"research_goal": flat})

        # A sharded goal: id comes from the directory, checkpoints sit alongside.
        write(self.root / "ledger/goals/GOAL-T-00bb02/goal.yaml", {"research_goal": {
            "id": "GOAL-T-00bb02", "status": "paused", "title": "sharded goal",
            "completion_criteria": ["only criterion"],
        }})
        for name in ("BATCH-001", "BATCH-002"):
            write(self.root / f"ledger/goals/GOAL-T-00bb02/checkpoints/{name}.yaml",
                  {"batch_checkpoint": {"batch_id": name, "body": "Z" * 5000}})

        # An unparseable record must be reported, never crash a listing.
        bad = self.root / "ledger/goals/GOAL-T-00cc03.yaml"
        bad.parent.mkdir(parents=True, exist_ok=True)
        bad.write_text("research_goal: {id: [unclosed\n")

    def run_tool(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(TOOL), "--repo-root", str(self.root), *args],
                              capture_output=True, text=True)

    # -- discovery -------------------------------------------------------

    def test_discovers_both_layouts(self) -> None:
        ids = {e["id"] for e in (gh.load_goal(p) for p in gh.goal_paths(self.root))}
        self.assertEqual(ids, {"GOAL-T-00aa01", "GOAL-T-00bb02", "GOAL-T-00cc03"})

    def test_unparseable_record_is_reported_not_raised(self) -> None:
        entry = gh.load_goal(self.root / "ledger/goals/GOAL-T-00cc03.yaml")
        self.assertEqual(entry["status"], "unparseable")
        result = self.run_tool("list")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("GOAL-T-00cc03", result.stdout)

    # -- honest compaction ------------------------------------------------

    def test_projection_is_far_smaller_than_the_record(self) -> None:
        raw = (self.root / "ledger/goals/GOAL-T-00aa01.yaml").stat().st_size
        out = self.run_tool("show", "GOAL-T-00aa01").stdout
        self.assertLess(len(out) * 8, raw,
                        "projection must be far smaller than the record it replaces")

    def test_ad_hoc_keys_are_dropped_but_their_count_is_disclosed(self) -> None:
        out = self.run_tool("show", "GOAL-T-00aa01").stdout
        self.assertNotIn("status_note_amendment", out)
        self.assertIn("30 undeclared top-level keys", out)
        self.assertIn("goal_head.py audit GOAL-T-00aa01", out)

    def test_clipped_text_names_the_command_that_returns_it(self) -> None:
        out = self.run_tool("show", "GOAL-T-00aa01").stdout
        self.assertIn("truncated, 4000 chars total", out)
        self.assertIn("--field next_action", out)

    def test_append_log_mapping_is_tailed_with_a_disclosed_count(self) -> None:
        # campaign_budget is a MAPPING on the real records, not a list; the
        # tailing has to be shape-agnostic or it silently misses this one.
        projection = gh.project(gh.load_goal(self.root / "ledger/goals/GOAL-T-00aa01.yaml"),
                                full=False, tail=2, text_chars=600)
        budget = projection["campaign_budget"]
        self.assertIn("_omitted", budget)
        self.assertIn("+18 earlier keys", budget["_omitted"])

    def test_completion_criteria_are_never_thinned(self) -> None:
        # A closure judgement rests on the full criterion set; showing 2 of 5
        # would invite a wrong call, so entries here are protected from tailing.
        projection = gh.project(gh.load_goal(self.root / "ledger/goals/GOAL-T-00aa01.yaml"),
                                full=False, tail=2, text_chars=600)
        self.assertEqual(len(projection["completion_criteria"]), 5)
        self.assertEqual(len(projection["pause_conditions"]), 2)

    def test_checkpoint_shards_are_named_never_inlined(self) -> None:
        out = self.run_tool("show", "GOAL-T-00bb02").stdout
        self.assertIn("2 shard(s), latest BATCH-002", out)
        self.assertNotIn("ZZZZ", out)

    def test_field_returns_the_whole_untruncated_value(self) -> None:
        out = self.run_tool("show", "GOAL-T-00aa01", "--field", "next_action").stdout
        self.assertIn("N" * 500, out)
        self.assertNotIn("truncated", out)

    def test_full_keeps_every_entry(self) -> None:
        projection = gh.project(gh.load_goal(self.root / "ledger/goals/GOAL-T-00aa01.yaml"),
                                full=True, tail=2, text_chars=600)
        self.assertEqual(len(projection["campaign_budget"]), 20)

    # -- CLI surface ------------------------------------------------------

    def test_bare_invocation_lists(self) -> None:
        # Regression: the no-subcommand path used to hand-patch the namespace
        # and crashed with AttributeError on every option `list` gained.
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("GOAL-T-00aa01", result.stdout)

    def test_status_filter_and_brief(self) -> None:
        out = self.run_tool("list", "--status", "active", "--brief").stdout
        self.assertIn("GOAL-T-00aa01", out)
        self.assertNotIn("GOAL-T-00bb02", out)
        self.assertNotIn("next:", out)

    def test_json_outputs_are_valid(self) -> None:
        for args in (["--json", "list"], ["--json", "show", "GOAL-T-00aa01"],
                     ["--json", "audit"]):
            with self.subTest(args=args):
                result = self.run_tool(*args)
                self.assertEqual(result.returncode, 0, result.stderr)
                json.loads(result.stdout)

    def test_unknown_goal_exits_nonzero(self) -> None:
        result = self.run_tool("show", "GOAL-T-nope99")
        self.assertEqual(result.returncode, 2)
        self.assertIn("no goal record", result.stderr)

    def test_unknown_field_error_does_not_dump_ad_hoc_keys(self) -> None:
        # The error path must not reintroduce the bloat: naming 600 ad-hoc keys
        # to say one is missing costs more than the answer is worth.
        result = self.run_tool("show", "GOAL-T-00aa01", "--field", "nope")
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("status_note_amendment", result.stderr)
        self.assertIn("30 ad-hoc key(s)", result.stderr)

    # -- history: the appended narrative stays reachable ------------------

    def test_every_adhoc_key_is_reachable_and_unchanged(self) -> None:
        # The load-bearing property of the whole design: `show` omits the
        # ad-hoc keys, so if `history` could not reach every one of them
        # byte-for-byte, compaction would be data loss by another name.
        entry = gh.load_goal(self.root / "ledger/goals/GOAL-T-00aa01.yaml")
        rows = gh.history_rows(entry)
        self.assertEqual(len(rows), 30)
        for row in rows:
            self.assertEqual(row["_value"], entry["_record"][row["key"]])

    def test_history_lists_names_without_their_content(self) -> None:
        out = self.run_tool("history", "GOAL-T-00aa01").stdout
        self.assertIn("status_note_amendment", out)
        self.assertNotIn("X" * 100, out)  # names and dates, not the prose
        self.assertIn("30 ad-hoc key(s)", out)

    def test_history_key_prints_the_whole_value(self) -> None:
        key = "status_note_amendment_20260800_batch000"
        out = self.run_tool("history", "GOAL-T-00aa01", "--key", key).stdout
        self.assertIn("X" * 900, out)
        self.assertNotIn("truncated", out)

    def test_history_grep_names_the_key_that_owns_each_hit(self) -> None:
        # Plain grep on a 972 KB single-file record returns a line with no
        # indication of which of 634 keys owns it; naming the key is the
        # entire reason this exists.
        write(self.root / "ledger/goals/GOAL-T-00dd04.yaml", {"research_goal": {
            "id": "GOAL-T-00dd04", "status": "paused",
            "terminal_note_20260815": "the telescoping construction was refuted here",
        }})
        result = self.run_tool("history", "--grep", "telescoping")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("terminal_note_20260815", result.stdout)
        self.assertIn("2026-08-15", result.stdout)
        self.assertIn("--key terminal_note_20260815", result.stdout)

    def test_history_grep_searches_nested_values(self) -> None:
        write(self.root / "ledger/goals/GOAL-T-00ee05.yaml", {"research_goal": {
            "id": "GOAL-T-00ee05", "status": "paused",
            "integrity_notes": [{"note": "the isogeny ladder claim was withdrawn"}],
        }})
        out = self.run_tool("history", "--grep", "isogeny ladder").stdout
        self.assertIn("integrity_notes", out)

    def test_history_dates_come_from_key_names(self) -> None:
        self.assertEqual(gh.key_date("x_terminal_note_20260830"), "2026-08-30")
        self.assertEqual(gh.key_date("note_2026_07_28_batch010"), "2026-07-28")
        self.assertIsNone(gh.key_date("prior_last_amended_by_task"))

    def test_history_date_filters(self) -> None:
        out = self.run_tool("history", "GOAL-T-00aa01", "--since", "2026-08-05").stdout
        self.assertIn("2026-08-05", out)
        self.assertNotIn("2026-08-01 ", out)

    def test_history_unknown_key_points_at_the_listing(self) -> None:
        result = self.run_tool("history", "GOAL-T-00aa01", "--key", "nope")
        self.assertEqual(result.returncode, 2)
        self.assertIn("lists them", result.stderr)

    def test_history_bad_regex_is_reported_not_raised(self) -> None:
        result = self.run_tool("history", "--grep", "([unclosed")
        self.assertEqual(result.returncode, 2)
        self.assertIn("bad --grep pattern", result.stderr)

    def test_audit_reports_adhoc_share(self) -> None:
        report = json.loads(self.run_tool("--json", "audit").stdout)
        row = next(r for r in report["goals"] if r["id"] == "GOAL-T-00aa01")
        self.assertGreater(row["adhoc_bytes"], row["declared_bytes"])
        self.assertEqual(row["keys"], 41)  # 11 declared + 30 ad-hoc


if __name__ == "__main__":
    unittest.main()

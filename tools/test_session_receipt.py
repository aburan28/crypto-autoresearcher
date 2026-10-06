#!/usr/bin/env python3
"""Tests for tools/session_receipt.py."""

from __future__ import annotations

import argparse
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import session_receipt as sr  # noqa: E402


def _args(**over) -> argparse.Namespace:
    base = dict(skill="design-experiment", role="coordinator", mode=None, outcome="approved",
                created="EXP-FROB-123456,H-FROB-000001,TASK-20261007-aaaaaa,weird",
                files_read=12, started=None, runtime=None, model=None, policy=None,
                usage_json=None, usage_source=None, goal="GOAL-FROB-000001", notes=None,
                supersedes=None)
    base.update(over)
    return argparse.Namespace(**base)


class ReceiptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.now = datetime(2026, 10, 7, 9, 30, tzinfo=timezone.utc)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_receipt_groups_created_ids_and_never_estimates_usage(self) -> None:
        rec = sr.receipt(_args(), repo_root=self.root, now=self.now, env={})
        self.assertEqual(rec["schema"], sr.SCHEMA)
        self.assertTrue(rec["id"].startswith("SR-20261007-"))
        self.assertEqual(rec["records_created"],
                         {"EXP": ["EXP-FROB-123456"], "H": ["H-FROB-000001"],
                          "TASK": ["TASK-20261007-aaaaaa"], "other": ["weird"]})
        self.assertEqual(rec["records_created_count"], 4)
        self.assertIsNone(rec["usage"])
        self.assertIsNone(rec["usage_source"])
        self.assertIsNone(rec["runtime"])
        self.assertIsNone(rec["model"])
        self.assertIsNone(rec["started_at"])
        self.assertEqual(rec["ended_at"], "2026-10-07T09:30:00+00:00")

    def test_runtime_detection_uses_only_runtime_markers(self) -> None:
        self.assertEqual(sr.detect_runtime({"CURSOR_AGENT": "1", "CURSOR_WORKLOAD_CGROUP": "x"}), "cursor_cloud")
        self.assertEqual(sr.detect_runtime({"CLAUDECODE": "1"}), "claude_code")
        self.assertEqual(sr.detect_runtime({"AUTORESEARCH_RUNTIME": "api_direct"}), "api_direct")
        self.assertIsNone(sr.detect_runtime({"HOME": "/x"}))
        self.assertEqual(sr.detect_model({"AUTORESEARCH_RESOLVED_MODEL": "m-1"}), "m-1")
        self.assertIsNone(sr.detect_model({}))

    def test_usage_json_must_be_an_object(self) -> None:
        with self.assertRaises(ValueError):
            sr.receipt(_args(usage_json="[1,2]"), repo_root=self.root, now=self.now, env={})
        rec = sr.receipt(_args(usage_json='{"input_tokens": 10}', usage_source="test"),
                         repo_root=self.root, now=self.now, env={})
        self.assertEqual(rec["usage"], {"input_tokens": 10})
        self.assertEqual(rec["usage_source"], "test")

    def test_started_falls_back_to_environment(self) -> None:
        rec = sr.receipt(_args(), repo_root=self.root, now=self.now,
                         env={"SESSION_RECEIPT_STARTED": "2026-10-07T09:00:00+00:00"})
        self.assertEqual(rec["started_at"], "2026-10-07T09:00:00+00:00")

    def test_write_is_write_once_and_summary_aggregates(self) -> None:
        rec = sr.receipt(_args(), repo_root=self.root, now=self.now, env={})
        path = sr.write(rec, self.root)
        self.assertEqual(path.parent.name, "20261007")
        with self.assertRaises(FileExistsError):
            sr.write(rec, self.root)
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertEqual(loaded["skill"], "design-experiment")
        rec2 = sr.receipt(_args(skill="run", outcome="nothing_executable", created=""),
                          repo_root=self.root, now=self.now, env={})
        sr.write(rec2, self.root)
        s = sr.summary(sr.load_all(self.root))
        self.assertEqual(s["receipts"], 2)
        self.assertEqual(s["usage_known"], 0)
        self.assertEqual(s["by_skill"]["run"], {"nothing_executable": 1})
        self.assertEqual(s["records_created_by_skill"]["design-experiment"], 4)
        text = sr.render_summary(s)
        self.assertIn("session receipts: 2", text)
        self.assertIn("design-experiment: 1 (approved 1); records created 4", text)
        self.assertIn("none yet", sr.render_summary(sr.summary([])))

    def test_cli_requires_skill_and_outcome(self) -> None:
        with self.assertRaises(SystemExit):
            sr.main(["--repo-root", str(self.root)])
        self.assertEqual(sr.main(["--repo-root", str(self.root), "--skill", "run",
                                  "--outcome", "ran"]), 0)
        self.assertEqual(len(sr.load_all(self.root)), 1)
        self.assertEqual(sr.main(["--repo-root", str(self.root), "summary"]), 0)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Tests for tools/resumable_grid.py (no solver needed)."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import resumable_grid as rg  # noqa: E402


def fake_instance(job: dict) -> dict:
    """Arm A times out from L = 4 on; arm B always finishes."""
    res = {"A": {"status": "timeout" if job["L"] >= 4 else "ok"}, "B": {"status": "ok"}}
    res = {k: v for k, v in res.items() if k in job["arms"]}
    return dict(job, results=res)


def wrong_seed_instance(job: dict) -> dict:
    return dict(job, seed=job["seed"] + 1, results={a: {"status": "ok"} for a in job["arms"]})


def missing_arm_instance(job: dict) -> dict:
    return dict(job, results={job["arms"][0]: {"status": "ok"}})


def bad_status_instance(job: dict) -> dict:
    return dict(job, results={a: {"status": 3} for a in job["arms"]})


def wrong_inst_instance(job: dict) -> dict:
    return dict(job, inst=job["inst"] + 100, results={a: {"status": "ok"} for a in job["arms"]})


def _never_called(job: dict) -> dict:
    raise AssertionError("the callback must not run on a rejected checkpoint")


PLAN = {"seed": "s", "timeout_s": 5, "planted_per_cell": 2, "random_per_cell": 1,
        "arms": ["A", "B"], "L_by_m": {"3": [3, 4, 5]}}


def _rows(path):
    return [json.loads(l) for l in open(path) if l.strip()]   # raises if any line is corrupt, by design


class ResumableGrid(unittest.TestCase):
    def test_seed_matches_the_frozen_launchers(self):
        want = int(hashlib.sha256(b"EXP-ECDLP-f49f75/v1|3|4|2").hexdigest()[:12], 16)
        self.assertEqual(rg.instance_seed("EXP-ECDLP-f49f75/v1", 3, 4, 2), want)

    def test_full_run_applies_the_stopping_rule(self):
        with tempfile.TemporaryDirectory() as d:
            out = str(Path(d) / "r.jsonl")
            log = []
            counts = rg.run_grid(PLAN, fake_instance, out, workers=2, log=log.append)
            rows = _rows(out)
            self.assertEqual(counts, {"executed": 9, "skipped": 0})
            by_L = {L: [r for r in rows if r["L"] == L] for L in (3, 4, 5)}
            self.assertTrue(all("A" in r["results"] for r in by_L[3] + by_L[4]))
            self.assertTrue(all("A" not in r["results"] for r in by_L[5]))   # retired after L = 4
            self.assertTrue(any("retired at m=3 L=4" in l for l in log))

    def test_resume_skips_recorded_instances_and_matches_an_uninterrupted_run(self):
        with tempfile.TemporaryDirectory() as d:
            full = str(Path(d) / "full.jsonl")
            rg.run_grid(PLAN, fake_instance, full, workers=2, log=lambda s: None)
            part = str(Path(d) / "part.jsonl")
            first = _rows(full)[:4]                      # pretend the process died after four instances
            Path(part).write_text("".join(json.dumps(r) + "\n" for r in first))
            counts = rg.run_grid(PLAN, fake_instance, part, workers=2, log=lambda s: None)
            self.assertEqual(counts["skipped"], 4)
            self.assertEqual(counts["executed"], 5)
            key = lambda r: (r["m"], r["L"], r["inst"])  # noqa: E731
            self.assertEqual(sorted(map(key, _rows(part))), sorted(map(key, _rows(full))))
            self.assertEqual(sorted(json.dumps(r, sort_keys=True) for r in _rows(part)),
                             sorted(json.dumps(r, sort_keys=True) for r in _rows(full)))

    def test_truncated_last_line_is_ignored_and_rerun(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "t.jsonl"
            rg.run_grid(PLAN, fake_instance, str(out), workers=2, log=lambda s: None)
            text = out.read_text().rstrip("\n").split("\n")
            out.write_text("\n".join(text[:-1]) + "\n" + text[-1][:20])    # last line cut mid-write
            counts = rg.run_grid(PLAN, fake_instance, str(out), workers=2, log=lambda s: None)
            self.assertEqual(counts["executed"], 1)
            self.assertEqual(len(_rows(str(out))), 9)

    def test_retirement_is_rebuilt_on_resume(self):
        # Cells L = 3 and 4 are complete on disk; the resumed run must not run arm A at L = 5.
        with tempfile.TemporaryDirectory() as d:
            out = str(Path(d) / "x.jsonl")
            rg.run_grid(dict(PLAN, L_by_m={"3": [3, 4]}), fake_instance, out, workers=2, log=lambda s: None)
            rg.run_grid(PLAN, fake_instance, out, workers=2, log=lambda s: None)
            l5 = [r for r in _rows(out) if r["L"] == 5]
            self.assertEqual(len(l5), 3)
            self.assertTrue(all(set(r["results"]) == {"B"} for r in l5))


class CheckpointValidation(unittest.TestCase):
    """The helper must never skip, truncate or append on a checkpoint it cannot trust."""

    OLD = {"seed": "old-seed", "timeout_s": 5, "planted_per_cell": 2, "random_per_cell": 1,
           "arms": ["A", "B"], "L_by_m": {"3": [3, 4]}}

    def _make(self, d, plan=None):
        out = Path(d) / "ck.jsonl"
        rg.run_grid(plan or self.OLD, fake_instance, str(out), workers=2, log=lambda s: None)
        return out

    def _rejects(self, out, plan, fn=fake_instance):
        before = out.read_bytes() if out.exists() else None
        with self.assertRaises(rg.CheckpointError):
            rg.run_grid(plan, fn, str(out), workers=2, log=lambda s: None)
        after = out.read_bytes() if out.exists() else None
        self.assertEqual(before, after, "a rejected checkpoint must be left byte-for-byte unchanged")

    def test_different_seed_and_timeout_are_rejected_not_skipped(self):
        # The reviewer's fixture: a complete row from seed "old-seed", timeout 5 was accepted as done under
        # another seed and timeout 99 (executed=0, skipped=1).
        with tempfile.TemporaryDirectory() as d:
            out = self._make(d)
            self._rejects(out, dict(self.OLD, seed="new-seed", timeout_s=99))
            self._rejects(out, dict(self.OLD, seed="new-seed"))
            self._rejects(out, dict(self.OLD, timeout_s=99))

    def test_changed_instance_counts_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            out = self._make(d)
            self._rejects(out, dict(self.OLD, planted_per_cell=1, random_per_cell=1))   # row inst 2 now out of grid

    def test_corrupt_complete_record_is_rejected_and_nothing_after_it_is_discarded(self):
        # The reviewer's second fixture: a newline-terminated malformed record before valid rows made the
        # valid rows look like a discardable tail and truncated them.
        with tempfile.TemporaryDirectory() as d:
            out = self._make(d)
            lines = out.read_text().splitlines(True)
            out.write_text("".join(lines[:2]) + "{not json}\n" + "".join(lines[2:]))
            self._rejects(out, self.OLD)

    def test_only_an_incomplete_final_line_is_recoverable(self):
        with tempfile.TemporaryDirectory() as d:
            out = self._make(d)
            text = out.read_text()
            out.write_text(text[:-10])                      # last line cut: no trailing newline
            counts = rg.run_grid(self.OLD, fake_instance, str(out), workers=2, log=lambda s: None)
            self.assertEqual(counts["executed"], 1)
            self.assertEqual(len(_rows(str(out))), 6)

    def test_duplicate_identity_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            out = self._make(d)
            lines = out.read_text().splitlines(True)
            out.write_text("".join(lines) + lines[0])
            self._rejects(out, self.OLD)

    def test_row_outside_the_grid_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            out = self._make(d)
            row = _rows(str(out))[0]
            with out.open("a") as fh:
                fh.write(json.dumps(dict(row, L=9)) + "\n")
            self._rejects(out, self.OLD)

    def test_results_not_matching_the_scheduled_arms_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            out = self._make(d)
            rows = _rows(str(out))
            rows[0]["results"] = {"A": rows[0]["results"]["A"]}            # arm B missing
            out.write_text("".join(json.dumps(r) + "\n" for r in rows))
            self._rejects(out, self.OLD)
            rows[0]["results"] = {"A": {"status": 1}, "B": {"status": "ok"}}  # non-string status
            out.write_text("".join(json.dumps(r) + "\n" for r in rows))
            self._rejects(out, self.OLD)

    def test_arm_that_should_have_been_retired_is_rejected(self):
        # A times out from L = 4 on, so a stored L = 5 row that still carries arm A contradicts the stopping rule.
        with tempfile.TemporaryDirectory() as d:
            plan = dict(PLAN, seed="s")
            out = Path(d) / "x.jsonl"
            rg.run_grid(plan, fake_instance, str(out), workers=2, log=lambda s: None)
            rows = _rows(str(out))
            for r in rows:
                if r["L"] == 5:
                    r["arms"] = ["A", "B"]
                    r["results"] = {"A": {"status": "timeout"}, "B": {"status": "ok"}}
            out.write_text("".join(json.dumps(r) + "\n" for r in rows))
            self._rejects(out, plan)

    def test_row_after_an_incomplete_cell_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            out = self._make(d)
            rows = _rows(str(out))
            keep = [r for r in rows if not (r["L"] == 3 and r["inst"] == 0)]    # L = 3 now incomplete, L = 4 present
            out.write_text("".join(json.dumps(r) + "\n" for r in keep))
            self._rejects(out, self.OLD)

    def test_invalid_callback_rows_are_never_appended(self):
        for bad in (wrong_seed_instance, missing_arm_instance, bad_status_instance, wrong_inst_instance):
            with tempfile.TemporaryDirectory() as d:
                out = Path(d) / "cb.jsonl"
                with self.assertRaises(rg.CheckpointError):
                    rg.run_grid(self.OLD, bad, str(out), workers=2, log=lambda s: None)
                self.assertFalse(out.exists() and out.read_text(), f"{bad.__name__} wrote a row")

    def test_validation_happens_before_the_executor_is_created(self):
        # A mismatching checkpoint must not even start work: the callback would raise if it were called.
        with tempfile.TemporaryDirectory() as d:
            out = self._make(d)
            with self.assertRaises(rg.CheckpointError):
                rg.run_grid(dict(self.OLD, seed="other"), _never_called, str(out), workers=2, log=lambda s: None)


if __name__ == "__main__":
    unittest.main()

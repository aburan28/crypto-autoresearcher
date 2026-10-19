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


if __name__ == "__main__":
    unittest.main()

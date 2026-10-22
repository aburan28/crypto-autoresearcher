"""Tests for tools/self_improve.py against fixture ledgers and fixture git repos."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import self_improve as si

AREAS = ["ALPHA", "BRAVO", "CHARLIE", "DELTA", "ECHO", "FOXTROT"]


def _write(root: Path, rel: str, doc: dict | str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(doc if isinstance(doc, str) else yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout


class BootstrapTests(unittest.TestCase):
    def test_seeded_and_signed(self) -> None:
        pre = [(a, 0.0) for a in AREAS]
        post = [(a, 2.0) for a in AREAS]
        one = si.bootstrap_diff(post, pre)
        self.assertEqual(one, si.bootstrap_diff(post, pre))
        self.assertEqual(one["estimate"], 2.0)
        self.assertEqual(si.verdict(one["ci95"]), "improved")
        self.assertEqual(si.verdict(si.bootstrap_diff(pre, post)["ci95"]), "regressed")
        self.assertEqual(si.verdict([-0.5, 0.5]), "no_change_detectable")

    def test_resamples_clusters_not_items(self) -> None:
        # Twenty items in one cluster are one observation: the interval of a
        # difference built on it must be as wide as the clusters say.
        pre = [("A", 0.0)] * 20 + [("B", 2.0)] * 20
        post = [("A", 2.0)] * 20 + [("B", 0.0)] * 20
        out = si.bootstrap_diff(post, pre)
        self.assertEqual(out["clusters"], [2, 2])
        self.assertLessEqual(out["ci95"][0], 0.0)
        self.assertGreaterEqual(out["ci95"][1], 0.0)

    def test_difference_in_differences_removes_shared_drift(self) -> None:
        pre = [(a, 0.0) for a in AREAS]
        post = [(a, 2.0) for a in AREAS]
        out = si.bootstrap_diff(post, pre, ctrl_post=post, ctrl_pre=pre)
        self.assertEqual(out["estimate"], 0.0)
        self.assertEqual(si.verdict(out["ci95"]), "no_change_detectable")


class LedgerFixture(unittest.TestCase):
    """design-experiment items before and after a round applied 2026-09-01."""

    APPLIED = date(2026, 9, 1)
    TODAY = date(2026, 10, 31)   # span 60 days: horizon 30, windows of 30 days

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        n = 0
        for offset, strength in ((-20, "inconclusive"), (10, "strong")):
            for i, area in enumerate(AREAS):
                n += 1
                designed = self.APPLIED + timedelta(days=offset + i % 3)
                exp = f"EXP-{area}-{n:06d}"
                _write(self.root, f"experiments/{exp}/specification.yaml",
                       {"experiment": {"id": exp, "status": "completed", "area": area,
                                       "designed_at": designed.isoformat()}})
                _write(self.root, f"ledger/evidence/EV-{area}-{n:06d}.yaml",
                       {"evidence": {"id": f"EV-{area}-{n:06d}", "experiment_ids": [exp],
                                     "strength": strength, "direction": "neutral",
                                     "recorded_at": (designed + timedelta(days=5)).isoformat()}})
        # Evidence for a pre-window item that arrived after the horizon: a
        # cohort that merely had longer to mature must not be scored on it.
        late = f"EXP-ALPHA-{n + 1:06d}"
        _write(self.root, f"experiments/{late}/specification.yaml",
               {"experiment": {"id": late, "status": "completed", "area": "ALPHA",
                               "designed_at": (self.APPLIED - timedelta(days=10)).isoformat()}})
        _write(self.root, "ledger/evidence/EV-ALPHA-999999.yaml",
               {"evidence": {"id": "EV-ALPHA-999999", "experiment_ids": [late], "strength": "strong",
                             "recorded_at": (self.APPLIED + timedelta(days=40)).isoformat()}})
        (self.root / "ledger" / "hypotheses").mkdir(parents=True, exist_ok=True)
        (self.root / "ledger" / "proposals").mkdir(parents=True, exist_ok=True)
        (self.root / "ledger" / "decisions").mkdir(parents=True, exist_ok=True)
        import build_ledger_index
        build_ledger_index.build(self.root)
        self.round = {"id": "round-aaaaaa", "decision": "proposed", "files_changed": ["x"],
                      "applied_at": self.APPLIED.isoformat(), "decided_at": "2026-08-30T00:00:00+00:00",
                      "batch_window": {"until": "2026-08-30"}}
        _write(self.root, "coordination/skill-tuning/design-experiment/round-aaaaaa.yaml", {"round": self.round})

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_measure_improved_at_equal_horizon(self) -> None:
        rnd = si.load_records(self.root, "design-experiment", "round")[0]
        m = si.measure(self.root, "design-experiment", rnd, self.TODAY)
        self.assertEqual((m["horizon_days"], m["window_days"]), (30, 30))
        self.assertEqual(m["pre"]["scored"], 6)      # the late-evidence item is not scored
        self.assertEqual(m["pre"]["items"], 7)
        self.assertEqual(m["post"]["scored"], 6)
        self.assertEqual(m["raw"]["verdict"], "improved")
        self.assertEqual(m["verdict"], "improved")    # control (propose-ideas) is empty: raw verdict
        self.assertTrue(any("drift" in c for c in m["caveats"]))

    def test_too_young_is_insufficient_and_not_written(self) -> None:
        rnd = si.load_records(self.root, "design-experiment", "round")[0]
        m = si.measure(self.root, "design-experiment", rnd, self.APPLIED + timedelta(days=10))
        self.assertEqual(m["verdict"], "insufficient_data")
        self.assertFalse(m["censored"])
        rc = si.main(["--repo-root", str(self.root), "--today", (self.APPLIED + timedelta(days=10)).isoformat(),
                      "measure", "round-aaaaaa", "--write"])
        self.assertEqual(rc, 1)
        self.assertEqual(si.load_records(self.root, "design-experiment", "outcome"), [])

    def test_outcome_written_once_then_plan_moves_on(self) -> None:
        argv = ["--repo-root", str(self.root), "--today", self.TODAY.isoformat()]
        self.assertEqual(si.main(argv + ["measure", "round-aaaaaa", "--write"]), 0)
        outs = si.load_records(self.root, "design-experiment", "outcome")
        self.assertEqual([o["verdict"] for o in outs], ["improved"])
        self.assertNotIn("rewards", outs[0]["pre"])
        self.assertEqual(si.main(argv + ["measure", "round-aaaaaa", "--write"]), 2)   # immutable
        # The tuner's batch is the outcome record; its reward follows the verdict.
        meta = si.meta_items(self.root)
        self.assertEqual([(m["id"], m["reward"], m["date"]) for m in meta],
                         [("round-aaaaaa", 2, "2026-08-30")])

    def test_regressed_outcome_plans_a_revert_first(self) -> None:
        _write(self.root, "coordination/skill-tuning/design-experiment/outcome-bbbbbb.yaml",
               {"outcome": {"id": "outcome-bbbbbb", "round_id": "round-aaaaaa", "verdict": "regressed"}})
        states = si.plan(self.root, self.TODAY)
        self.assertEqual((states[0]["action"], states[0]["skill"]), ("revert", "design-experiment"))
        self.assertEqual(states[0]["round"], "round-aaaaaa")

    def test_unmeasured_round_plans_measure(self) -> None:
        states = {s["skill"]: s for s in si.plan(self.root, self.TODAY)}
        self.assertEqual(states["design-experiment"]["action"], "measure")
        self.assertEqual(states["design-experiment"]["preview"], "improved")
        self.assertEqual(states["tune-skill"]["action"], "idle")

    def test_placebo_reports_every_date(self) -> None:
        out = si.placebo(self.root, "design-experiment", date(2026, 8, 25), date(2026, 9, 8), 7, self.TODAY)
        self.assertEqual(out["dates"], 3)
        self.assertEqual(len(out["rows"]), 3)


FROZEN_SKILL = """# Tune skill

intro

<!-- frozen:reward -->
| strength | reward |
| strong | +2 |
<!-- /frozen:reward -->

tail
"""


class GuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        _git(self.root, "init", "-q", "-b", "main")
        _git(self.root, "config", "user.email", "t@example.invalid")
        _git(self.root, "config", "user.name", "t")
        _write(self.root, ".claude/skills/tune-skill/SKILL.md", FROZEN_SKILL)
        _write(self.root, "tools/tune_skill_batch.py", "REWARD = {}\n")
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-qm", "base")
        _git(self.root, "checkout", "-qb", "skill-tuning/tune-skill-round-cccccc")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _commit(self) -> dict:
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-qm", "round-cccccc")
        return si.guard(self.root, "tune-skill", "main")

    def test_edit_outside_frozen_region_and_new_round_record_pass(self) -> None:
        _write(self.root, ".claude/skills/tune-skill/SKILL.md", FROZEN_SKILL.replace("tail", "tail, clarified"))
        _write(self.root, "coordination/skill-tuning/tune-skill/round-cccccc.yaml", {"round": {}})
        g = self._commit()
        self.assertTrue(g["ok"], g["violations"])
        self.assertEqual(g["changed_lines"], 2)

    def test_frozen_region_edit_is_refused(self) -> None:
        _write(self.root, ".claude/skills/tune-skill/SKILL.md", FROZEN_SKILL.replace("+2", "+3"))
        g = self._commit()
        self.assertFalse(g["ok"])
        self.assertIn("frozen region 'reward' changed", g["violations"][0])

    def test_removing_the_frozen_markers_is_refused(self) -> None:
        _write(self.root, ".claude/skills/tune-skill/SKILL.md", "# Tune skill\n\nrewritten\n")
        self.assertFalse(self._commit()["ok"])

    def test_scorer_is_outside_every_write_scope(self) -> None:
        _write(self.root, "tools/tune_skill_batch.py", "REWARD = {'n/a': 2}\n")
        g = self._commit()
        self.assertFalse(g["ok"])
        self.assertIn("tools/tune_skill_batch.py", g["violations"][0])

    def test_large_diff_is_not_minimal(self) -> None:
        body = FROZEN_SKILL + "".join(f"line {i}\n" for i in range(si.MAX_DIFF_LINES + 1))
        _write(self.root, ".claude/skills/tune-skill/SKILL.md", body)
        g = self._commit()
        self.assertFalse(g["ok"])
        self.assertIn("not a minimal diff", g["violations"][-1])


if __name__ == "__main__":
    unittest.main()

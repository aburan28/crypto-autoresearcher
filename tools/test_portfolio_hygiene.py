"""Pins for the portfolio hygiene rules (docs/track-record-review-20261006.md).

P0.1  approval capacity: a post-cutoff approval is refused while the goal's
      approved-unrun backlog is at cap; pre-cutoff decisions never are;
      retiring contracts in the same decision releases capacity.
P0.5  pre-written outcomes: a post-cutoff specification needs a
      decision_impact block whose branches differ, must not carry an outcome,
      and must not have identical success/falsification text. Pre-cutoff
      specifications are untouched.
P1.7/P1.10/P3.17 advisories never fail: they land in ctx.advisories only.
"""
from __future__ import annotations

import datetime as dt
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import portfolio_kpis  # noqa: E402
import validate_ledger as vl  # noqa: E402


def _ctx() -> vl.Ctx:
    return vl.Ctx(set())


def _spec(exp_id: str, goal: str = "GOAL-T-000001", **over) -> dict:
    body = {"id": exp_id, "status": "approved", "goal_id": goal,
            "approved_by": "coordinator"}
    body.update(over)
    return body


def _register_experiment(ctx: vl.Ctx, root: Path, exp_id: str, *, with_run: bool,
                         **over) -> None:
    exp_dir = root / "experiments" / exp_id
    runs = exp_dir / "runs"
    runs.mkdir(parents=True)
    (runs / ".gitkeep").write_text("")
    if with_run:
        (runs / "RUN-1").mkdir()
    path = exp_dir / "specification.yaml"
    path.write_text("experiment: {}\n")
    ctx.register(exp_id, str(path), _spec(exp_id, **over), "experiment")


def _register_decision(ctx: vl.Ctx, root: Path, dec_id: str, targets: list[str],
                       **over) -> None:
    body = {"id": dec_id, "decision": "approve", "target_ids": targets}
    body.update(over)
    path = root / "ledger" / "decisions" / f"{dec_id}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("coordinator_decision: {}\n")
    ctx.register(dec_id, str(path), body, "coordinator_decision")


class ApprovalCapacity(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.cap = portfolio_kpis.APPROVAL_CAPACITY_CAP

    def tearDown(self):
        self.tmp.cleanup()

    def _fill_backlog(self, ctx, n):
        for i in range(n):
            _register_experiment(ctx, self.root, f"EXP-T-00000{i}", with_run=False)

    def test_new_approval_refused_at_cap(self):
        ctx = _ctx()
        self._fill_backlog(ctx, self.cap)
        _register_experiment(ctx, self.root, "EXP-T-aaaaaa", with_run=False)
        _register_decision(ctx, self.root, "DEC-20261101-aaaaaa", ["EXP-T-aaaaaa"])
        vl.check_approval_capacity(ctx)
        self.assertEqual(len(ctx.errors), 1, ctx.errors)
        self.assertIn("approval capacity", ctx.errors[0])
        self.assertIn("EXP-T-aaaaaa", ctx.errors[0])

    def test_below_cap_is_accepted(self):
        ctx = _ctx()
        self._fill_backlog(ctx, self.cap - 1)
        _register_experiment(ctx, self.root, "EXP-T-aaaaaa", with_run=False)
        _register_decision(ctx, self.root, "DEC-20261101-aaaaaa", ["EXP-T-aaaaaa"])
        vl.check_approval_capacity(ctx)
        self.assertEqual(ctx.errors, [])

    def test_experiments_with_runs_do_not_count(self):
        ctx = _ctx()
        for i in range(self.cap + 2):
            _register_experiment(ctx, self.root, f"EXP-T-00000{i}", with_run=True)
        _register_experiment(ctx, self.root, "EXP-T-aaaaaa", with_run=False)
        _register_decision(ctx, self.root, "DEC-20261101-aaaaaa", ["EXP-T-aaaaaa"])
        vl.check_approval_capacity(ctx)
        self.assertEqual(ctx.errors, [])

    def test_pre_cutoff_decisions_are_never_refused(self):
        ctx = _ctx()
        self._fill_backlog(ctx, self.cap + 5)
        _register_experiment(ctx, self.root, "EXP-T-aaaaaa", with_run=False)
        _register_decision(ctx, self.root, "DEC-20261005-aaaaaa", ["EXP-T-aaaaaa"])
        vl.check_approval_capacity(ctx)
        self.assertEqual(ctx.errors, [])

    def test_retiring_contracts_in_the_decision_releases_capacity(self):
        ctx = _ctx()
        self._fill_backlog(ctx, self.cap)
        _register_experiment(ctx, self.root, "EXP-T-aaaaaa", with_run=False)
        _register_decision(ctx, self.root, "DEC-20261101-aaaaaa", ["EXP-T-aaaaaa"],
                           supersedes_experiments=["EXP-T-000000"])
        vl.check_approval_capacity(ctx)
        self.assertEqual(ctx.errors, [])

    def test_other_goals_backlog_is_irrelevant(self):
        ctx = _ctx()
        for i in range(self.cap + 3):
            _register_experiment(ctx, self.root, f"EXP-T-00000{i}", with_run=False,
                                 goal_id="GOAL-OTHER-000001")
        _register_experiment(ctx, self.root, "EXP-T-aaaaaa", with_run=False)
        _register_decision(ctx, self.root, "DEC-20261101-aaaaaa", ["EXP-T-aaaaaa"])
        vl.check_approval_capacity(ctx)
        self.assertEqual(ctx.errors, [])

    def test_non_approval_decisions_are_ignored(self):
        ctx = _ctx()
        self._fill_backlog(ctx, self.cap)
        _register_experiment(ctx, self.root, "EXP-T-aaaaaa", with_run=False)
        _register_decision(ctx, self.root, "DEC-20261101-aaaaaa", ["EXP-T-aaaaaa"],
                           decision="replicate")
        vl.check_approval_capacity(ctx)
        self.assertEqual(ctx.errors, [])


class PrewrittenOutcome(unittest.TestCase):
    def _run(self, **spec) -> list[str]:
        ctx = _ctx()
        body = {"id": "EXP-T-aaaaaa", "status": "approved",
                "success_criterion": "yield exceeds 0.5",
                "falsification_criterion": "yield below 0.1 on every seed",
                "decision_impact": {"on_positive": "design the n=11 ladder",
                                    "on_negative": "retire H-T-aaaaaa"}}
        body.update(spec)
        vl.check_outcome_not_prewritten("/x/specification.yaml", body, ctx)
        return ctx.errors

    def test_pre_cutoff_spec_is_untouched(self):
        self.assertEqual(self._run(designed_at="2026-09-30", outcome="won"), [])

    def test_undated_spec_is_untouched(self):
        self.assertEqual(self._run(outcome="won"), [])

    def test_complete_new_spec_passes(self):
        self.assertEqual(self._run(designed_at="2026-10-07"), [])

    def test_missing_decision_impact(self):
        errors = self._run(designed_at="2026-10-08T00:00:00Z", decision_impact=None)
        self.assertEqual(len(errors), 1)
        self.assertIn("decision_impact", errors[0])

    def test_identical_branches(self):
        errors = self._run(designed_at="2026-10-08",
                           decision_impact={"on_positive": "x", "on_negative": "X"})
        self.assertTrue(any("equals on_negative" in e for e in errors), errors)

    def test_prewritten_outcome_refused(self):
        errors = self._run(designed_at="2026-10-08", outcome="hypothesis supported")
        self.assertTrue(any("'outcome' before any run" in e for e in errors), errors)

    def test_identical_criteria_refused(self):
        errors = self._run(designed_at="2026-10-08",
                           falsification_criterion="Yield exceeds 0.5")
        self.assertTrue(any("same text" in e for e in errors), errors)


class Advisories(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_oversized_goal_head_and_next_action_advise_only(self):
        ctx = _ctx()
        path = self.root / "goal.yaml"
        path.write_bytes(b"x" * (vl.GOAL_HEAD_CAP_BYTES + 1))
        ctx.register("GOAL-T-000001", str(path),
                     {"id": "GOAL-T-000001",
                      "next_action": "y" * (vl.NEXT_ACTION_CAP_CHARS + 1)},
                     "research_goal")
        vl.check_record_sizes(ctx)
        self.assertEqual(ctx.errors, [])
        self.assertEqual(len(ctx.advisories), 2)
        self.assertTrue(any("goal head" in a for a in ctx.advisories))
        self.assertTrue(any("next_action" in a for a in ctx.advisories))

    def test_large_old_idea_is_silent_large_new_idea_advises(self):
        ctx = _ctx()
        for rec_id in ("IDEA-20260901-aaaaaa", "IDEA-20261010-bbbbbb"):
            path = self.root / f"{rec_id}.yaml"
            path.write_bytes(b"x" * (vl.IDEA_CAP_BYTES + 1))
            ctx.register(rec_id, str(path), {"id": rec_id}, "idea")
        vl.check_record_sizes(ctx)
        self.assertEqual(ctx.errors, [])
        self.assertEqual(len(ctx.advisories), 1)
        self.assertIn("IDEA-20261010-bbbbbb", ctx.advisories[0])

    def test_aged_open_handoff_advises(self):
        ctx = _ctx()
        for rec_id, archived in (("TASK-20260901-aaaaaa", None),
                                 ("TASK-20260901-bbbbbb", "TASK-20260902-cccccc"),
                                 ("TASK-20261001-dddddd", None)):
            path = self.root / f"{rec_id}.yaml"
            path.write_text("")
            ctx.register(rec_id, str(path), {"id": rec_id, "archived_by": archived},
                         "handoff")
        vl.check_aged_handoffs(ctx, today="20261006")
        self.assertEqual(ctx.errors, [])
        self.assertEqual(len(ctx.advisories), 1)
        self.assertIn("TASK-20260901-aaaaaa", ctx.advisories[0])

    def test_ceremony_is_advised_on_new_records_only(self):
        ctx = _ctx()
        old = {"id": "TASK-20260901-aaaaaa", "budget": {"memory_gb": None},
               "amazon_bedrock": "NOT SELECTED, NOT USED."}
        new = {"id": "TASK-20261010-bbbbbb",
               "budget": {"wall_clock_seconds": None, "memory_gb": None},
               "amazon_bedrock_selected_configured_probed_contacted_or_used": False}
        fine = {"id": "TASK-20261010-cccccc", "budget": {"memory_gb": 4}}
        for body in (old, new, fine):
            path = self.root / f"{body['id']}.yaml"
            path.write_text("")
            ctx.register(body["id"], str(path), body, "handoff")
        dec = {"id": "DEC-20261010-dddddd", "amazon_bedrock": "not used"}
        dpath = self.root / f"{dec['id']}.yaml"
        dpath.write_text("")
        ctx.register(dec["id"], str(dpath), dec, "coordinator_decision")
        vl.check_ceremony(ctx)
        self.assertEqual(ctx.errors, [])
        joined = "\n".join(ctx.advisories)
        self.assertNotIn("TASK-20260901-aaaaaa", joined)
        self.assertNotIn("TASK-20261010-cccccc", joined)
        self.assertEqual(joined.count("TASK-20261010-bbbbbb"), 2)
        self.assertIn("DEC-20261010-dddddd", joined)
        self.assertIn("budget holds only null placeholders", joined)

    def test_shouted_next_action_advises(self):
        ctx = _ctx()
        quiet = {"id": "GOAL-T-000001",
                 "next_action": "Run EXP-FROB-123456 via TASK-20261007-aaaaaa; "
                                "see DEC-20261007-bbbbbb."}
        loud = {"id": "GOAL-T-000002",
                "next_action": "DO NOT DISPATCH. READ THIS FIRST. EVERY "
                               "SESSION MUST CHECK THE QUEUE BEFORE ANYTHING."}
        for body in (quiet, loud):
            path = self.root / f"{body['id']}.yaml"
            path.write_text("")
            ctx.register(body["id"], str(path), body, "research_goal")
        vl.check_ceremony(ctx)
        self.assertEqual(ctx.errors, [])
        self.assertEqual(len(ctx.advisories), 1)
        self.assertIn("GOAL-T-000002", ctx.advisories[0])
        self.assertIn("all-caps", ctx.advisories[0])


class KpiModule(unittest.TestCase):
    def test_runs_present_ignores_placeholders(self):
        with tempfile.TemporaryDirectory() as tmp:
            exp = Path(tmp) / "EXP-T-aaaaaa"
            (exp / "runs").mkdir(parents=True)
            (exp / "runs" / ".gitkeep").write_text("")
            self.assertFalse(portfolio_kpis.runs_present(exp))
            (exp / "runs" / "RUN-1").mkdir()
            self.assertTrue(portfolio_kpis.runs_present(exp))

    def test_approved_unrun_groups_by_goal_then_area(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for exp_id, goal, run in (("EXP-A-000001", "GOAL-A-000001", False),
                                      ("EXP-A-000002", None, False),
                                      ("EXP-A-000003", "GOAL-A-000001", True)):
                d = root / "experiments" / exp_id / "runs"
                d.mkdir(parents=True)
                if run:
                    (d / "RUN-1").mkdir()
                spec = {"id": exp_id, "status": "approved"}
                if goal:
                    spec["goal_id"] = goal
                (root / "experiments" / exp_id / "specification.yaml").write_text(
                    "experiment:\n" + "".join(f"  {k}: {v}\n" for k, v in spec.items()))
            backlog = portfolio_kpis.approved_unrun(root)
            self.assertEqual(backlog, {"GOAL-A-000001": ["EXP-A-000001"],
                                       "area:A": ["EXP-A-000002"]})

    def test_aged_handoffs_use_id_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            h = root / "ledger" / "handoffs"
            h.mkdir(parents=True)
            (h / "TASK-20260901-aaaaaa.yaml").write_text(
                "handoff:\n  id: TASK-20260901-aaaaaa\n  to: executor\n")
            (h / "TASK-20261005-bbbbbb.yaml").write_text(
                "handoff:\n  id: TASK-20261005-bbbbbb\n  to: executor\n")
            aged = portfolio_kpis.aged_open_handoffs(root, today=dt.date(2026, 10, 6))
            self.assertEqual([r["id"] for r in aged], ["TASK-20260901-aaaaaa"])


if __name__ == "__main__":
    unittest.main()

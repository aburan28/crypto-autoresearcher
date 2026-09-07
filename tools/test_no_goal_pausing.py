"""Pins CLAUDE.md rule 10 / AGENTS.md "Goals are never paused".

A goal may not take `status: paused` or `status: blocked`. Both were removed
from the permitted set on user instruction (2026-09-04).

`blocked` is pinned alongside `paused` deliberately: it is the same idling
under another name, and a rule that refused only `paused` would be cosmetic —
the next session wanting to stop a goal would simply write `blocked`.

The tests below also pin the three things the rule does NOT relax, because the
danger of "never pause" is that it reads as permission to close, to promote a
claim whose review tier cannot be served, or to spend past a budget. Those
guarantees live in prose, so what is pinned here is that the prose is present
and says so — a doc test, and deliberately shallow about it.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import validate_ledger as V  # noqa: E402

try:
    import yaml
except ImportError:                                          # pragma: no cover
    yaml = None


class GoalStatusEnumTests(unittest.TestCase):
    def test_paused_and_blocked_are_not_permitted_statuses(self):
        self.assertNotIn("paused", V.GOAL_STATUSES)
        self.assertNotIn("blocked", V.GOAL_STATUSES)

    def test_the_working_statuses_survive(self):
        for s in ("draft", "active", "completed", "cancelled",
                  "closed_at_budget"):
            self.assertIn(s, V.GOAL_STATUSES, s)

    def test_refusal_table_covers_exactly_the_removed_statuses(self):
        self.assertEqual(set(V.GOAL_STATUSES_REFUSED), {"paused", "blocked"})

    def test_each_refusal_names_the_remedy(self):
        # A refusal that does not say what to do instead just gets worked
        # around, so the message must name both the replacement status and
        # the field that carries the reason.
        for status, msg in V.GOAL_STATUSES_REFUSED.items():
            self.assertIn("active", msg, status)
            self.assertIn("impediments", msg, status)

    def test_refused_statuses_are_disjoint_from_permitted(self):
        self.assertFalse(set(V.GOAL_STATUSES_REFUSED) & V.GOAL_STATUSES)


class NoGoalRecordIsPausedTests(unittest.TestCase):
    """The committed corpus must satisfy the rule, not merely the validator."""

    def _goal_files(self):
        return sorted(
            list((ROOT / "ledger" / "goals").glob("*.yaml"))
            + list((ROOT / "ledger" / "goals").glob("*/goal.yaml"))
        )

    @unittest.skipIf(yaml is None, "PyYAML unavailable")
    def test_no_committed_goal_is_paused_or_blocked(self):
        offenders = []
        for p in self._goal_files():
            try:
                doc = yaml.safe_load(p.read_text())
            except Exception:
                continue                    # parseability is a separate check
            goal = (doc or {}).get("research_goal") or doc or {}
            if not isinstance(goal, dict):
                continue
            if goal.get("status") in V.GOAL_STATUSES_REFUSED:
                offenders.append((goal.get("id"), goal.get("status")))
        self.assertEqual(offenders, [], f"goals must never be parked: {offenders}")

    @unittest.skipIf(yaml is None, "PyYAML unavailable")
    def test_migrated_goals_kept_a_checkable_impediment(self):
        # The four records migrated on 2026-09-04. Going active is only honest
        # if the reason survived the migration, so each must still carry an
        # impediment naming what is blocked and what would clear it.
        migrated = {"GOAL-MONO-001", "GOAL-ECRANK-002",
                    "GOAL-ECQ-e72c0b", "GOAL-ECQ-2298dc"}
        seen = {}
        for p in self._goal_files():
            try:
                doc = yaml.safe_load(p.read_text())
            except Exception:
                continue
            goal = (doc or {}).get("research_goal") or doc or {}
            if isinstance(goal, dict) and goal.get("id") in migrated:
                seen[goal["id"]] = goal
        self.assertEqual(set(seen), migrated, "a migrated goal record vanished")
        for gid, goal in sorted(seen.items()):
            self.assertEqual(goal.get("status"), "active", gid)
            imps = goal.get("impediments")
            self.assertTrue(isinstance(imps, list) and imps, f"{gid}: no impediments")
            for e in imps:
                for field in ("what_is_blocked", "clears_when", "recheck"):
                    self.assertTrue(str(e.get(field, "")).strip(),
                                    f"{gid}: impediment missing {field}")


class TheRuleDoesNotRelaxAnythingTests(unittest.TestCase):
    """"Never pause" must not read as permission to close, promote, or spend."""

    def setUp(self):
        self.agents = (ROOT / "AGENTS.md").read_text()
        self.claude = (ROOT / "CLAUDE.md").read_text()

    def test_agents_md_carries_the_rule(self):
        self.assertIn("Goals are never paused", self.agents)

    def test_claude_md_carries_the_rule(self):
        self.assertIn("Goals are never paused", self.claude)

    def test_the_three_preserved_guarantees_are_stated(self):
        section = self.agents.split("## Goals are never paused", 1)
        self.assertEqual(len(section), 2, "AGENTS.md section missing")
        body = section[1].split("\n## ", 1)[0]
        # 1: an impediment is not evidence. Match the negation bound to the
        # phrase, not one particular adverb — the claim is what matters, and a
        # bare "negative mathematical evidence" would pass while asserting the
        # opposite.
        self.assertRegex(
            body, r"(?:not|never)[^.]{0,60}negative\s+mathematical\s+evidence")
        # 2: an unservable review tier is not downgradable
        self.assertIn("degradable: false", body)
        self.assertRegex(body, r"un-?promoted")
        # 3: ordinary estimates no longer block progress; exceptional caps are separate
        self.assertRegex(body, r"budget")
        self.assertIn("Routine estimates do not stop research", body)
        self.assertIn("stagnation", body)

    def test_make_work_is_still_forbidden(self):
        body = self.agents.split("## Goals are never paused", 1)[1]
        body = body.split("\n## ", 1)[0]
        self.assertRegex(body, r"rank\s+ahead\s+of\s+doing\s+nothing")

    def test_harness_skill_does_not_instruct_pausing(self):
        skill = (ROOT / ".claude" / "skills" / "launch-research-harness"
                 / "SKILL.md").read_text()
        # Any surviving mention must be part of the prohibition, never an
        # instruction to do it.
        for m in re.finditer(r"^.*\bmark\b[^\n]*`paused`.*$", skill,
                             re.MULTILINE | re.IGNORECASE):
            self.fail(f"harness skill still instructs pausing: {m.group(0)!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)

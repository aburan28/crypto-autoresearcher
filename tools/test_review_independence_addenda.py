#!/usr/bin/env python3
"""Tests for addendum composition in check_review_independence.

WHY THESE EXIST. A review plan is immutable once committed, and the base plan
cannot name the addenda that will later extend it, so the only honest way to add
a joint or move one between reviewers is a companion file. Before composition
existed, the checker held every reviewer to the pre-addendum assignment: on
2026-09-15 it reported that TASK-20260913-6c5729 failed to claim joint V2 and
carried no V2 verdict, when a committed addendum had reassigned V2 to another
task. The only way to make that check pass was for the reviewer to claim an
ownership the addendum had removed and invent a verdict on a joint it could not
evaluate -- which is the exact fabrication the checker exists to catch. So the
regression pinned below is not "the tool is convenient now"; it is "the tool no
longer rewards lying to it".

The other half of the contract matters just as much: an addendum may ADD a joint,
REASSIGN one, and ADD a control. It may not remove a joint, drop a control, or
narrow a blind_from -- otherwise "addendum" becomes a way to quietly shrink a
declared review after the fact, and a green check would mean less than no check.
"""

from __future__ import annotations

import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_review_independence as cri


BASE_PLAN = """
review_plan:
  id: REVIEW-TEST-001
  coordinator_prior: I expect J1 to hold and J2 to break.
  joints:
    - joint: 'J1 -- THE FIRST THING. That the arithmetic recomputes.'
      assigned_to: TASK-A
      attack_plan: recompute it from the primary inputs
    - joint: 'J2 -- THE SECOND THING. That the rows reproduce.'
      assigned_to: TASK-A
      attack_plan: re-run the four rows the contract names
  blindness:
    mutual: true
  proves_too_much:
    objects:
      - a curve for which the conclusion is known false
    failure_signature: the argument still goes through
  blind_rederivation:
    required: false
"""

ATTESTATION_A = """
review_attestation:
  task_id: TASK-A
  role: validator
  joints_owned: [J1]
  verdicts:
    J1: holds
  read_sibling_reports: false
  sources_read: []
"""

ATTESTATION_B = """
review_attestation:
  task_id: TASK-B
  role: validator
  joints_owned: [J2]
  verdicts:
    J2: breaks
  read_sibling_reports: false
  sources_read: []
"""


def _addendum(written_at: str, body: str) -> str:
    """A one-addendum document. `body` is dedented and indented under the block.

    Built by concatenation rather than by an f-string inside dedent(): mixing
    the two makes the injected body part of the common-prefix calculation, which
    silently produced a document whose root key was indented and whose body was
    not -- parsed, but not the structure any test meant.
    """
    header = ("review_plan_addendum:\n"
              "  id: REVIEW-TEST-001-ADD\n"
              "  extends: review-plan.yaml\n"
              f"  written_at: '{written_at}'\n")
    return header + textwrap.indent(textwrap.dedent(body).strip("\n"), "  ") + "\n"


class AddendumComposition(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = Path(tempfile.mkdtemp())
        self.plan_path = self.dir / "review-plan.yaml"
        self.plan_path.write_text(BASE_PLAN, encoding="utf-8")
        (self.dir / "TASK-A").mkdir()
        (self.dir / "TASK-A" / "attestation.yaml").write_text(
            ATTESTATION_A, encoding="utf-8")

    def plan(self) -> dict:
        return cri._plan_of(cri._load(str(self.plan_path)))

    def write_addendum(self, name: str, written_at: str, body: str) -> Path:
        path = self.dir / name
        path.write_text(_addendum(written_at, body), encoding="utf-8")
        return path

    def composed(self) -> tuple[dict, list[str]]:
        return cri.compose_plan(self.plan(), cri.find_addenda(str(self.plan_path)))

    # --- discovery ---------------------------------------------------------
    def test_addendum_extending_another_plan_is_ignored(self):
        path = self.dir / "unrelated.yaml"
        path.write_text(textwrap.dedent("""
            review_plan_addendum:
              id: OTHER
              extends: some/other/review-plan-for-a-different-round.yaml
              written_at: '2026-01-01T00:00Z'
              joints_added:
                - joint: 'JX -- NOT OURS.'
                  assigned_to: TASK-Z
                  attack_plan: nothing
        """), encoding="utf-8")
        self.assertEqual(cri.find_addenda(str(self.plan_path)), [])
        composed, notes = self.composed()
        self.assertEqual(len(composed["joints"]), 2)
        self.assertEqual(notes, [])

    def test_the_plan_itself_is_never_its_own_addendum(self):
        self.assertNotIn(str(self.plan_path),
                         [p for p, _ in cri.find_addenda(str(self.plan_path))])

    def test_also_extends_is_followed(self):
        self.write_addendum("a-second.yaml", "2026-01-02T00:00Z", """
            also_extends: review-plan.yaml
            joints_added:
              - joint: 'J3 -- A THIRD THING.'
                assigned_to: TASK-A
                attack_plan: check it
        """)
        # `extends` on this file points at the plan too (the helper writes it),
        # so assert the composed result rather than the discovery mechanism.
        composed, _ = self.composed()
        self.assertIn("J3", [cri._joint_label(j["joint"]) for j in composed["joints"]])

    # --- what an addendum may do -----------------------------------------
    def test_joints_added_are_appended(self):
        self.write_addendum("add.yaml", "2026-01-02T00:00Z", """
            joints_added:
              - joint: 'J3 -- THE BASELINE COLUMN.'
                assigned_to: TASK-A
                attack_plan: derive it from the source record
        """)
        composed, notes = self.composed()
        labels = [cri._joint_label(j["joint"]) for j in composed["joints"]]
        self.assertEqual(labels, ["J1", "J2", "J3"])
        self.assertTrue(any("added joint 'J3'" in n for n in notes))

    def test_owner_reassignment_is_applied_and_reported(self):
        self.write_addendum("split.yaml", "2026-01-03T00:00Z", """
            what_changes:
              owners:
                J1: TASK-A
                J2: TASK-B
        """)
        composed, notes = self.composed()
        owners = {cri._joint_label(j["joint"]): j["assigned_to"]
                  for j in composed["joints"]}
        self.assertEqual(owners, {"J1": "TASK-A", "J2": "TASK-B"})
        self.assertTrue(any("reassigned TASK-A -> TASK-B" in n for n in notes))
        # An unchanged owner is not reported as a change: a composition note
        # that fires on every joint tells a reader nothing.
        self.assertEqual(sum("J1" in n for n in notes), 0)

    def test_owner_reassignment_applies_to_id_owner_spelling(self):
        """A plan naming joints `id:`/`owner:` (the SEMBIN rounds) is reassigned too.

        Matching only `joint`/`assigned_to` made the SEMBIN addendum a no-op:
        composition printed 'no joint added or reassigned' and the re-deriver
        kept the run-reading joints the addendum had moved away from it.
        """
        self.plan_path.write_text(textwrap.dedent("""
            review_plan:
              id: REVIEW-TEST-002
              coordinator_prior: I expect J1 to hold.
              joints:
                - id: J1
                  name: THE FIRST THING
                  owner: TASK-A
                  attack_plan: recompute it
                - id: J2
                  name: THE SECOND THING
                  owner: TASK-A
                  attack_plan: re-run it
              proves_too_much:
                objects: [a known-false object]
                failure_signature: the argument still goes through
        """), encoding="utf-8")
        self.write_addendum("split.yaml", "2026-01-03T00:00Z", """
            what_changes:
              owners:
                J2: TASK-B
        """)
        composed, notes = self.composed()
        owners = {j["id"]: j["owner"] for j in composed["joints"]}
        self.assertEqual(owners, {"J1": "TASK-A", "J2": "TASK-B"})
        self.assertNotIn("assigned_to", composed["joints"][1])
        self.assertTrue(any("'J2' reassigned TASK-A -> TASK-B" in n for n in notes))
        problems = cri.check(composed, cri._collect_reports([str(self.dir)]))
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("TASK-B", problems[0])

    def test_later_addendum_wins_over_earlier(self):
        self.write_addendum("first.yaml", "2026-01-02T00:00Z", """
            what_changes:
              owners:
                J2: TASK-B
        """)
        self.write_addendum("second.yaml", "2026-01-04T00:00Z", """
            what_changes:
              owners:
                J2: TASK-C
        """)
        composed, _ = self.composed()
        owners = {cri._joint_label(j["joint"]): j["assigned_to"]
                  for j in composed["joints"]}
        self.assertEqual(owners["J2"], "TASK-C")

    def test_ordering_is_by_written_at_not_filename(self):
        # Alphabetically 'aaa' precedes 'zzz', but 'zzz' was written first.
        self.write_addendum("zzz.yaml", "2026-01-02T00:00Z", """
            what_changes:
              owners:
                J2: TASK-EARLY
        """)
        self.write_addendum("aaa.yaml", "2026-01-09T00:00Z", """
            what_changes:
              owners:
                J2: TASK-LATE
        """)
        composed, _ = self.composed()
        owners = {cri._joint_label(j["joint"]): j["assigned_to"]
                  for j in composed["joints"]}
        self.assertEqual(owners["J2"], "TASK-LATE")

    def test_proves_too_much_objects_are_added_never_replaced(self):
        self.write_addendum("control.yaml", "2026-01-02T00:00Z", """
            proves_too_much_objects_added:
              - a second known-false object
        """)
        composed, notes = self.composed()
        self.assertEqual(len(composed["proves_too_much"]["objects"]), 2)
        self.assertEqual(composed["proves_too_much"]["failure_signature"],
                         "the argument still goes through")
        self.assertTrue(any("proves-too-much object" in n for n in notes))

    # --- what an addendum may NOT do -------------------------------------
    # --- blind_from widening ------------------------------------------------
    # These pin the one composition step that was declared in committed addenda
    # and enforced nowhere: `blind_from_additions` was an unknown key, so
    # compose_plan left it alone and the leak check below always ran against the
    # parent plan's list. A protection cited in a receipt as in force and applied
    # to nothing is worse than an absent one, which is why these are tests and
    # not a comment.
    def test_blind_from_additions_widen_the_composed_list(self):
        self.write_addendum("a-widen.yaml", "2026-01-02T00:00Z", """
            what_changes:
              blind_from_additions:
                - experiments/EXP-X/runs/
                - coordination/review/r/prior.yaml
        """)
        composed, notes = self.composed()
        self.assertEqual(
            composed["blind_rederivation"]["blind_from"],
            ["experiments/EXP-X/runs/", "coordination/review/r/prior.yaml"])
        self.assertTrue(any("widened blind_from by 2 path(s)" in n for n in notes))

    def test_blind_from_additions_accepted_at_top_level_too(self):
        self.write_addendum("a-widen-flat.yaml", "2026-01-02T00:00Z", """
            blind_from_additions:
              - experiments/EXP-Y/code/
        """)
        composed, _ = self.composed()
        self.assertEqual(composed["blind_rederivation"]["blind_from"],
                         ["experiments/EXP-Y/code/"])

    def test_blind_from_widening_appends_and_never_replaces(self):
        plan = self.plan()
        plan["blind_rederivation"] = {"required": True,
                                      "blind_from": ["already/there/"]}
        self.write_addendum("a-widen2.yaml", "2026-01-02T00:00Z", """
            what_changes:
              blind_from_additions: [newly/added/]
        """)
        composed, _ = cri.compose_plan(plan, cri.find_addenda(str(self.plan_path)))
        self.assertEqual(composed["blind_rederivation"]["blind_from"],
                         ["already/there/", "newly/added/"])

    def test_blind_from_widening_is_idempotent(self):
        """Two addenda naming the same path must not double it: a duplicated
        blind_from entry would report the same leak twice and read as two."""
        plan = self.plan()
        plan["blind_rederivation"] = {"required": True, "blind_from": ["dup/"]}
        self.write_addendum("a-dup.yaml", "2026-01-02T00:00Z", """
            what_changes:
              blind_from_additions: [dup/, fresh/]
        """)
        composed, _ = cri.compose_plan(plan, cri.find_addenda(str(self.plan_path)))
        self.assertEqual(composed["blind_rederivation"]["blind_from"],
                         ["dup/", "fresh/"])

    def test_a_widened_blind_from_actually_catches_a_leak(self):
        """The point of the fix. Composition alone proves nothing; what matters
        is that check_plan now FINDS a read it previously could not see."""
        plan = self.plan()
        plan["blind_rederivation"] = {
            "required": True, "quantity": "d", "assigned_to": "TASK-A",
            "blind_from": ["unrelated/"]}
        addenda = [("a.yaml", {"what_changes":
                               {"blind_from_additions": ["experiments/EXP-X/runs/"]}})]
        composed, _ = cri.compose_plan(plan, addenda)
        attestation = {"task_id": "TASK-A", "role": "validator",
                       "joints_owned": ["J1"], "blind_from_respected": True,
                       "sources_read": ["experiments/EXP-X/runs/RUN-1/manifest.yaml"]}
        reports = [("a/att.yaml", attestation)]
        problems = cri.check(composed, reports)
        self.assertTrue(
            any("experiments/EXP-X/runs/" in p and "not independent" in p
                for p in problems),
            f"the widened path did not produce a leak finding: {problems}")

        uncomposed = cri.check(plan, reports)
        self.assertFalse(
            any("experiments/EXP-X/runs/" in p for p in uncomposed),
            "without composition the same read must go unnoticed -- that is the "
            "defect these tests pin")

    def test_an_addendum_cannot_remove_a_joint(self):
        self.write_addendum("shrink.yaml", "2026-01-02T00:00Z", """
            joints_removed:
              - J2
            what_changes:
              joints_dropped: [J2]
        """)
        composed, _ = self.composed()
        self.assertEqual(len(composed["joints"]), 2,
                         "a joint may not be dropped by an addendum")

    def test_an_addendum_cannot_drop_a_control_or_weaken_blindness(self):
        self.write_addendum("weaken.yaml", "2026-01-02T00:00Z", """
            proves_too_much:
              objects: []
            blindness:
              mutual: false
            blind_rederivation:
              required: false
              blind_from: []
        """)
        composed, _ = self.composed()
        self.assertEqual(len(composed["proves_too_much"]["objects"]), 1)
        self.assertIs(composed["blindness"]["mutual"], True)

    def test_composition_does_not_mutate_the_loaded_plan(self):
        self.write_addendum("add.yaml", "2026-01-02T00:00Z", """
            joints_added:
              - joint: 'J3 -- ANOTHER.'
                assigned_to: TASK-A
                attack_plan: check it
        """)
        original = self.plan()
        composed, _ = cri.compose_plan(
            original, cri.find_addenda(str(self.plan_path)))
        self.assertEqual(len(original["joints"]), 2)
        self.assertEqual(len(composed["joints"]), 3)


class TheRegressionThatMotivatedThis(unittest.TestCase):
    """A reassigned joint must not be reported against its former owner.

    This is the 2026-09-15 ICPERF case in miniature: J2 is moved to TASK-B by a
    committed addendum, TASK-A reports only on J1, and TASK-B has not run yet.
    Composed, the only problem is the true one -- J2's owner has not attested.
    Uncomposed, TASK-A is accused of two things that are not its fault, and the
    only way to clear them is to fabricate.
    """

    def setUp(self) -> None:
        self.dir = Path(tempfile.mkdtemp())
        self.plan_path = self.dir / "review-plan.yaml"
        self.plan_path.write_text(BASE_PLAN, encoding="utf-8")
        (self.dir / "split.yaml").write_text(_addendum("2026-01-03T00:00Z", """
            what_changes:
              owners:
                J2: TASK-B
        """), encoding="utf-8")
        (self.dir / "TASK-A").mkdir()
        (self.dir / "TASK-A" / "attestation.yaml").write_text(
            ATTESTATION_A, encoding="utf-8")

    def _problems(self, *, composed: bool):
        plan = cri._plan_of(cri._load(str(self.plan_path)))
        if composed:
            plan, _ = cri.compose_plan(plan, cri.find_addenda(str(self.plan_path)))
        return cri.check(plan, cri._collect_reports([str(self.dir)]))

    def test_uncomposed_blames_the_former_owner(self):
        problems = self._problems(composed=False)
        self.assertTrue(any("does not claim joint 'J2'" in p for p in problems))
        self.assertTrue(any("no entry for 'J2'" in p for p in problems))

    def test_composed_reports_only_the_missing_reviewer(self):
        problems = self._problems(composed=True)
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("TASK-B", problems[0])
        self.assertIn("filed no review_attestation", problems[0])

    def test_composed_passes_once_the_new_owner_reports(self):
        (self.dir / "TASK-B").mkdir()
        (self.dir / "TASK-B" / "attestation.yaml").write_text(
            ATTESTATION_B, encoding="utf-8")
        self.assertEqual(self._problems(composed=True), [])
        # And the reassignment is still load-bearing: without composition the
        # same two reports fail, because each reports on the joint it owns.
        self.assertTrue(self._problems(composed=False))

    def test_a_second_owner_on_one_joint_is_still_refused(self):
        """Composition must not become a way to double-assign a joint."""
        (self.dir / "double.yaml").write_text(_addendum("2026-01-05T00:00Z", """
            joints_added:
              - joint: 'J1 -- THE FIRST THING, AGAIN.'
                assigned_to: TASK-B
                attack_plan: check it again
        """), encoding="utf-8")
        (self.dir / "TASK-B").mkdir()
        (self.dir / "TASK-B" / "attestation.yaml").write_text(
            ATTESTATION_B, encoding="utf-8")
        problems = self._problems(composed=True)
        self.assertTrue(any("does not claim joint 'J1'" in p for p in problems),
                        problems)


if __name__ == "__main__":
    unittest.main()

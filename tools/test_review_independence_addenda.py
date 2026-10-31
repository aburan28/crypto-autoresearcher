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
import copy
import io
import os
import subprocess
import tempfile
import textwrap
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import yaml

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


class DeclaredBlindPhaseComposition(unittest.TestCase):
    """Synthetic phase/source bindings, not attestations about an actual review."""
    FULL = "TASK-20261015-ef06c6"
    BLIND = "TASK-20261015-5fd82c"
    OTHER = "TASK-20261015-c102ab"
    UNKNOWN = "TASK-20261015-123abc"

    def setUp(self):
        prefix = "research/synthetic/coordinator/"+self.BLIND+"/"
        self.allowed = [prefix+name for name in ("independent_enumerator.py", "predicted-counts.json", "report.md",
                                                "diagram.svg", "report.pdf", "visual-inspection.json", "read-attestation.yaml")]
        self.base = {
            "coordinator_prior": "Synthetic prior, no scientific prediction.",
            "joints": [{"joint": "J1 -- Synthetic integrity joint", "assigned_to": self.OTHER, "attack_plan": "check synthetic inputs"},
                       {"joint": "J2 -- Synthetic full group comparison", "assigned_to": self.FULL, "attack_plan": "compare after independent derivation"}],
            "blindness": {"mutual": True, "lifted_for": [self.OTHER], "rationale": "Original deliberate legacy lift."},
            "proves_too_much": {"objects": ["synthetic known-false object"], "failure_signature": "must reject the false object"},
            "blind_rederivation": {"required": True, "quantity": "synthetic statement-derived quantity", "parameters": {"fixture": "synthetic"},
                                     "assigned_to": self.FULL, "blind_from": ["tools/producer.py", "observations/"]}}
        self.addendum = {
            "extends": "review-plan.yaml", "written_at": "2026-10-15T00:00:00Z",
            "what_changes": {"blind_rederivation_assigned_to": self.BLIND, "blind_from_additions": ["notes/producer-prior.md"]},
            "joints_added": [{"joint": "JB -- Synthetic blind independent derivation", "assigned_to": self.BLIND,
                              "attack_plan": "derive from the statement alone"}],
            "blindness_lifted_for_additions": [self.FULL],
            "blindness_lift_rationale": "Same Reviewer may deliberately compare its exact prior blind artifacts after the external archive/unblind gate.",
            "lift_read_allowlist": list(self.allowed)}
        self.reports = [
            (f"reviews/{self.OTHER}/attestation.yaml", {"task_id": self.OTHER, "joints_owned": ["J1"], "verdict": "holds",
                                                       "sources_read": [], "read_sibling_reports": False}),
            (f"reviews/{self.FULL}/attestation.yaml", {"task_id": self.FULL, "joints_owned": ["J2"], "verdict": "inconclusive",
                                                      "sources_read": ["tools/producer.py", self.allowed[2]], "read_sibling_reports": True,
                                                      "blind_from_respected": False}),
            (f"reviews/{self.BLIND}/attestation.yaml", {"task_id": self.BLIND, "joints_owned": ["JB"], "verdict": "inconclusive",
                                                       "sources_read": ["statement.md", "fixtures.json"], "read_sibling_reports": False,
                                                       "blind_from_respected": True})]

    def compose(self, addendum=None, base=None):
        return cri.compose_plan(self.base if base is None else base,
                                [("synthetic-phase-addendum.yaml", self.addendum if addendum is None else addendum)])

    def _problems(self, reports=None, plan=None):
        if plan is None:
            plan, _ = self.compose()
        return cri.check(plan, self.reports if reports is None else reports)

    def test_exact_named_split_preserves_full_joint_owner_and_protections(self):
        original, directive = copy.deepcopy(self.base), copy.deepcopy(self.addendum)
        composed, notes = self.compose()
        self.assertEqual(cri._joint_owner(composed["joints"][1]), self.FULL)
        self.assertEqual(composed["blind_rederivation"]["assigned_to"], self.BLIND)
        for field in ("required", "quantity", "parameters"):
            self.assertEqual(composed["blind_rederivation"][field], original["blind_rederivation"][field])
        self.assertEqual(composed["blind_rederivation"]["blind_from"], ["tools/producer.py", "observations/", "notes/producer-prior.md"])
        self.assertIs(composed["blindness"]["mutual"], True)
        self.assertEqual(composed["blindness"]["lifted_for"], [self.OTHER])
        self.assertNotIn(self.FULL, composed["blindness"]["lifted_for"])
        self.assertEqual(composed["blindness"]["scoped_lifts"][self.FULL]["read_allowlist"], self.allowed)
        self.assertTrue(any(self.FULL+" -> "+self.BLIND in note for note in notes))
        self.assertEqual(self.base, original)
        self.assertEqual(self.addendum, directive)
        self.assertEqual(self._problems(plan=composed), [])
        self.assertTrue(cri.check(self.base, self.reports), "unsplit blind owner cannot truthfully read producer inputs")

    def test_blind_task_still_rejects_every_original_and_added_source(self):
        for source in ("tools/producer.py", "observations/result.json", "notes/producer-prior.md",
                       "tools/../tools/producer.py", str(Path(cri.REPO)/"tools/producer.py"), "./"):
            with self.subTest(source=source):
                reports = copy.deepcopy(self.reports)
                reports[2][1]["sources_read"].append(source)
                problems = self._problems(reports)
                self.assertTrue(any("blind_from path(s)" in item for item in problems), problems)

    def test_scoped_full_comparison_accepts_only_its_declared_prior_blind_files(self):
        reports = copy.deepcopy(self.reports)
        reports[1][1]["sources_read"] = ["tools/producer.py", "observations/public-result.json"]+self.allowed
        self.assertEqual(self._problems(reports), [])
        for unexpected in (f"reviews/{self.OTHER}/report.md", f"reviews/{self.UNKNOWN}/report.md",
                           self.allowed[0].rsplit("/", 1)[0]+"/unexpected.md", self.allowed[0].rsplit("/", 1)[0]+"/"):
            for flag in (True, False):
                with self.subTest(source=unexpected, declared_flag=flag):
                    wrong = copy.deepcopy(reports)
                    wrong[1][1]["sources_read"].append(unexpected)
                    wrong[1][1]["read_sibling_reports"] = flag
                    self.assertTrue(any("outside scoped" in item for item in self._problems(wrong)))

    def test_scoped_lift_checks_actual_sibling_attestation_path_without_task_directory(self):
        reports = copy.deepcopy(self.reports)
        reports[0] = ("reviews/sibling-unnamed.yaml", reports[0][1])
        reports[1][1]["sources_read"].append("reviews/sibling-unnamed.yaml")
        self.assertTrue(any("outside scoped" in item for item in self._problems(reports)))

    def test_scoped_lift_never_accepts_an_omitted_or_malformed_read_scope(self):
        for reads in ([], None, "report.md", [None]):
            with self.subTest(reads=reads):
                reports = copy.deepcopy(self.reports)
                reports[1][1]["sources_read"] = reads
                self.assertTrue(self._problems(reports))
        reports = copy.deepcopy(self.reports)
        reports[1][1].pop("read_sibling_reports")
        self.assertTrue(any("explicit read_sibling_reports" in item for item in self._problems(reports)))

    def test_blind_task_cannot_hide_sibling_read_with_a_false_flag(self):
        reports = copy.deepcopy(self.reports)
        reports[2][1]["sources_read"].append(f"reviews/{self.FULL}/report.md")
        self.assertTrue(any("without an authorized blindness lift" in item for item in self._problems(reports)))

    def test_missing_malformed_or_unowned_blind_owner_is_rejected(self):
        for owner in (None, "", [], {}, 7, "TASK-A", "not-a-task", self.UNKNOWN):
            with self.subTest(owner=owner):
                addon = copy.deepcopy(self.addendum)
                addon["what_changes"]["blind_rederivation_assigned_to"] = owner
                with self.assertRaises(ValueError):
                    self.compose(addon)
        addon = copy.deepcopy(self.addendum)
        addon["joints_added"] = []
        with self.assertRaisesRegex(ValueError, "explicitly declared joint"):
            self.compose(addon)

    def test_full_joint_reassignment_is_not_hidden_by_a_phase_split(self):
        addon = copy.deepcopy(self.addendum)
        addon["what_changes"]["owners"] = {"J2": self.OTHER}
        with self.assertRaisesRegex(ValueError, "must remain assigned"):
            self.compose(addon)
        composed, _ = self.compose()
        with self.assertRaisesRegex(ValueError, "must remain assigned"):
            cri.compose_plan(composed, [("later.yaml", {"what_changes": {"owners": {"J2": self.OTHER}}})])

    def test_unknown_joint_or_malformed_owner_reassignment_is_refused(self):
        for owners in ({"ABSENT": self.FULL}, {"J1": None}, {"J1": "nobody"}, [self.FULL]):
            with self.subTest(owners=owners):
                with self.assertRaises(ValueError):
                    cri.compose_plan(self.base, [("bad.yaml", {"what_changes": {"owners": owners}})])

    def test_missing_lift_rationale_allowlist_or_named_full_owner_is_refused(self):
        for field, value in (("blindness_lift_rationale", None), ("blindness_lift_rationale", " "),
                             ("lift_read_allowlist", None), ("lift_read_allowlist", []), ("lift_read_allowlist", "report.md"),
                             ("blindness_lifted_for_additions", []), ("blindness_lifted_for_additions", [None]),
                             ("blindness_lifted_for_additions", [self.UNKNOWN]), ("blindness_lifted_for_additions", [self.BLIND]),
                             ("blindness_lifted_for_additions", [self.FULL, self.FULL])):
            with self.subTest(field=field, value=value):
                addon = copy.deepcopy(self.addendum)
                addon[field] = value
                with self.assertRaises(ValueError):
                    self.compose(addon)

    def test_invalid_broad_or_other_reviewer_allowlist_paths_are_refused(self):
        prefix = self.allowed[0].rsplit("/", 1)[0]
        for path in (prefix+"/", prefix, prefix+"/*", prefix+"/../"+self.OTHER+"/report.md",
                     f"reviews/{self.OTHER}/report.md", "/absolute/"+self.BLIND+"/report.md", "report.md", " " ,
                     prefix+"/sub/../../report.md"):
            with self.subTest(path=path):
                addon = copy.deepcopy(self.addendum)
                addon["lift_read_allowlist"] = [path]
                with self.assertRaises(ValueError):
                    self.compose(addon)
        addon = copy.deepcopy(self.addendum)
        addon["lift_read_allowlist"].append(addon["lift_read_allowlist"][0])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.compose(addon)

    def test_allowlist_symlink_or_existing_directory_cannot_authorize_other_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            blind_dir, other_dir = root/"reviews"/self.BLIND, root/"reviews"/self.OTHER
            blind_dir.mkdir(parents=True)
            other_dir.mkdir(parents=True)
            other_report = other_dir/"report.md"
            other_report.write_text("Synthetic other review artifact.\n", encoding="utf-8")
            (blind_dir/"report.md").symlink_to(other_report)
            (blind_dir/"artifacts").mkdir()
            with patch.object(cri, "REPO", str(root)):
                for path in (f"reviews/{self.BLIND}/report.md", f"reviews/{self.BLIND}/artifacts"):
                    addon = copy.deepcopy(self.addendum)
                    addon["lift_read_allowlist"] = [path]
                    with self.assertRaisesRegex(ValueError, "directory or resolves outside"):
                        self.compose(addon)

    def test_explicit_source_addition_containers_are_checked_and_both_spellings_preserved(self):
        for value in (None, "producer.py", [None], [""]):
            addon = copy.deepcopy(self.addendum)
            addon["what_changes"]["blind_from_additions"] = value
            with self.assertRaisesRegex(ValueError, "blind_from_additions"):
                self.compose(addon)
        addon = copy.deepcopy(self.addendum)
        addon["blind_from_additions"] = ["notes/extra-producer.md"]
        composed, _ = self.compose(addon)
        self.assertIn("notes/producer-prior.md", composed["blind_rederivation"]["blind_from"])
        self.assertIn("notes/extra-producer.md", composed["blind_rederivation"]["blind_from"])
        addon = copy.deepcopy(self.addendum)
        addon["joints_added"] = "not an explicit joint list"
        with self.assertRaisesRegex(ValueError, "joints_added"):
            self.compose(addon)

    def test_attempted_blind_from_narrowing_is_an_enforced_audit_failure(self):
        for replacement in ({"blind_from": []}, {"required": False}, {"quantity": "different"}, {"parameters": {}}):
            with self.subTest(replacement=replacement):
                addon = copy.deepcopy(self.addendum)
                addon["blind_rederivation"] = replacement
                composed, notes = self.compose(addon)
                self.assertEqual(composed["blind_rederivation"], self.base["blind_rederivation"])
                self.assertTrue(any("REFUSED" in note for note in notes))
                self.assertTrue(any("REFUSED" in problem for problem in self._problems(plan=composed)))

    def test_mutual_false_or_original_lift_removal_is_never_applied(self):
        for replacement in ({"mutual": False}, {"lifted_for": []}):
            addon = copy.deepcopy(self.addendum)
            addon["blindness"] = replacement
            composed, _ = self.compose(addon)
            self.assertEqual(composed["blindness"], self.base["blindness"])
            self.assertTrue(any("REFUSED" in problem for problem in self._problems(plan=composed)))

    def test_legacy_lift_remains_broad_and_explicit_new_scope_can_narrow_it(self):
        reports = copy.deepcopy(self.reports)
        reports[0][1]["read_sibling_reports"] = True
        reports[0][1]["sources_read"] = [f"reviews/{self.FULL}/report.md"]
        self.assertEqual(self._problems(reports), [])
        base = copy.deepcopy(self.base)
        base["blindness"]["lifted_for"].append(self.FULL)
        composed, _ = self.compose(base=base)
        reports[1][1]["sources_read"].append(f"reviews/{self.OTHER}/report.md")
        self.assertTrue(any("outside scoped" in item for item in self._problems(reports, composed)))

    def test_new_scoped_addendum_preserves_prior_exact_grants(self):
        composed, _ = self.compose()
        new_path = self.allowed[0].rsplit("/", 1)[0]+"/additional-proof.txt"
        later = {"blindness_lifted_for_additions": [self.FULL], "blindness_lift_rationale": "Explicit additional own-blind artifact.",
                 "lift_read_allowlist": [new_path]}
        extended, _ = cri.compose_plan(composed, [("later.yaml", later)])
        self.assertEqual(extended["blindness"]["scoped_lifts"][self.FULL]["read_allowlist"], self.allowed+[new_path])
        self.assertEqual(extended["blindness"]["lifted_for"], [self.OTHER])

    def test_duplicate_attestation_unknown_task_or_absent_required_joint_never_passes(self):
        duplicate = self.reports+[copy.deepcopy(self.reports[-1])]
        self.assertTrue(any("duplicate attestation" in problem for problem in self._problems(duplicate)))
        unknown = copy.deepcopy(self.reports)
        unknown.append(("unknown.yaml", {"task_id": self.UNKNOWN, "joints_owned": [], "sources_read": [], "read_sibling_reports": False}))
        self.assertTrue(any("unowned attestation" in problem for problem in self._problems(unknown)))
        for owner in (self.FULL, self.BLIND):
            composed, _ = self.compose()
            composed["joints"] = [entry for entry in composed["joints"] if cri._joint_owner(entry) != owner]
            self.assertTrue(self._problems(plan=composed))
        missing = self.reports[:-1]
        self.assertTrue(any("filed no review_attestation" in problem for problem in self._problems(missing)))

    def test_composed_binding_and_attestation_owner_tampering_are_rejected(self):
        composed, _ = self.compose()
        for bad_value in (None, [], "ignored"):
            tampered = copy.deepcopy(composed)
            tampered["blindness"]["scoped_lifts"] = bad_value
            self.assertTrue(any("scoped_lifts" in problem for problem in self._problems(plan=tampered)))
        for field, value in (("required", False), ("assigned_to", self.OTHER), ("blind_from", "tools/producer.py")):
            tampered = copy.deepcopy(composed)
            tampered["blind_rederivation"][field] = value
            self.assertTrue(self._problems(plan=tampered))
        reports = copy.deepcopy(self.reports)
        reports[1][1]["joints_owned"].append("J1")
        self.assertTrue(any("unassigned joint" in problem for problem in self._problems(reports)))
        tampered = copy.deepcopy(composed)
        tampered["joints"][0]["assigned_to"] = 17
        self.assertTrue(any("invalid TASK owner" in problem for problem in self._problems(plan=tampered)))

    def test_explicit_directives_at_wrong_locations_are_not_silently_ignored(self):
        for addon in ({"blind_rederivation_assigned_to": self.BLIND},
                      {"what_changes": {"blindness_lifted_for_additions": [self.FULL]}},
                      {"blindness_lift_rationale": "missing owners"},
                      {"lift_read_allowlist": self.allowed}):
            with self.subTest(addon=addon):
                with self.assertRaises(ValueError):
                    self.compose(addon)

    def _native(self, addon, reports):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = root/"review-plan.yaml"
            plan.write_text(yaml.safe_dump({"review_plan": self.base}), encoding="utf-8")
            (root/"phase-addendum.yaml").write_text(yaml.safe_dump({"review_plan_addendum": addon}), encoding="utf-8")
            paths = []
            for i, (_, attestation) in enumerate(reports):
                path = root/f"report-{i}.yaml"
                path.write_text(yaml.safe_dump({"review_attestation": attestation}), encoding="utf-8")
                paths.append(str(path))
            output, errors = io.StringIO(), io.StringIO()
            with patch.object(sys, "argv", ["check_review_independence.py", "--plan", str(plan), "--reports", *paths]):
                with redirect_stdout(output), redirect_stderr(errors):
                    code = cri.main()
            return code, output.getvalue()+errors.getvalue()

    def test_native_cli_accepts_only_the_complete_synthetic_declared_phase(self):
        code, output = self._native(self.addendum, self.reports)
        self.assertEqual(code, 0, output)
        self.assertIn("scoped blindness lift", output)
        reports = copy.deepcopy(self.reports)
        reports[2][1]["sources_read"].append("tools/producer.py")
        code, output = self._native(self.addendum, reports)
        self.assertEqual(code, 1, output)
        self.assertNotIn("PASS:", output)
        addon = copy.deepcopy(self.addendum)
        addon["what_changes"]["blind_rederivation_assigned_to"] = self.UNKNOWN
        code, output = self._native(addon, self.reports)
        self.assertEqual(code, 2, output)
        self.assertIn("invalid review-plan addendum", output)
        self.assertNotIn("PASS:", output)


class DeclaredBlindPhaseReplacement(unittest.TestCase):
    """Lost-session maintenance using only invented declarations and temp files.

    A synthetic PASS is no receipt for an actual identity, archive or science.
    """
    FULL = DeclaredBlindPhaseComposition.FULL
    BLIND = DeclaredBlindPhaseComposition.BLIND
    OTHER = DeclaredBlindPhaseComposition.OTHER
    UNKNOWN = DeclaredBlindPhaseComposition.UNKNOWN
    NEW = "TASK-20261015-49d9e0"

    def setUp(self):
        DeclaredBlindPhaseComposition.setUp(self)
        self.initial, _ = cri.compose_plan(self.base, [("initial.yaml", self.addendum)])
        self.new_allowed = [path.replace(self.BLIND, self.NEW) for path in self.allowed]
        self.replacement = {
            "extends": "review-plan.yaml", "written_at": "2026-10-15T01:00:00Z",
            "blind_phase_replacement": {
                "full_task": self.FULL, "replaces_blind_task": self.BLIND,
                "replacement_blind_task": self.NEW, "reason": "Synthetic lost session; no continuity asserted.",
                "retained_blind_archive": {"task": self.BLIND, "commit_sha": "a"*40,
                                           "verification": "synthetic/archive-verification.json"},
                "prior_artifacts_remain_required": True},
            "joints_added": [{"joint": "JN -- Synthetic fresh blind derivation", "assigned_to": self.NEW,
                              "attack_plan": "derive independently without the prior Reviewer outputs"}],
            "what_changes": {"blind_from_additions": ["notes/fresh-producer.md"]},
            "blindness_lifted_for_additions": [self.FULL],
            "blindness_lift_rationale": "Same fresh Reviewer may read its own seven exact artifacts only after external archive gate.",
            "lift_read_allowlist": self.new_allowed}
        self.reports[1][1]["sources_read"] = ["tools/producer.py"]+self.new_allowed
        self.reports.append((f"reviews/{self.NEW}/attestation.yaml", {
            "task_id": self.NEW, "joints_owned": ["JN"], "verdict": "inconclusive",
            "sources_read": ["statement.md", "fixtures.json"], "read_sibling_reports": False,
            "blind_from_respected": True}))

    def compose(self, addon=None, base=None):
        return cri.compose_plan(self.initial if base is None else base,
                                [("replacement.yaml", self.replacement if addon is None else addon)])

    def test_valid_replacement_preserves_owners_history_and_original_inputs(self):
        before = copy.deepcopy((self.base, self.initial, self.replacement))
        plan, notes = self.compose()
        self.assertEqual(cri.check(plan, self.reports), [])
        self.assertEqual((self.base, self.initial, self.replacement), before)
        for joint in self.initial["joints"]:
            self.assertIn(joint, plan["joints"])
        for field in ("required", "quantity", "parameters"):
            self.assertEqual(plan["blind_rederivation"][field], self.initial["blind_rederivation"][field])
        self.assertTrue(set(self.initial["blind_rederivation"]["blind_from"]).issubset(plan["blind_rederivation"]["blind_from"]))
        self.assertTrue(set(self.allowed).issubset(plan["blind_rederivation"]["blind_from"]))
        self.assertIn("notes/fresh-producer.md", plan["blind_rederivation"]["blind_from"])
        self.assertEqual(plan["blind_rederivation"]["assigned_to"], self.NEW)
        self.assertEqual(plan["blindness"]["scoped_lifts"][self.FULL]["read_allowlist"], self.new_allowed)
        self.assertEqual(plan["blindness"]["lifted_for"], [self.OTHER])
        self.assertIs(plan["blindness"]["mutual"], True)
        self.assertEqual(plan["proves_too_much"], self.initial["proves_too_much"])
        history = plan["_blind_phase_history"]
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["phase_assignment"], self.initial["_blind_phase_assignments"][self.FULL])
        self.assertEqual(history[0]["scoped_lift"], self.initial["blindness"]["scoped_lifts"][self.FULL])
        self.assertEqual(history[0]["retained_blind_archive"], self.replacement["blind_phase_replacement"]["retained_blind_archive"])
        self.assertTrue(any("old phase and grant retained" in note for note in notes))

    def test_every_old_new_and_full_attestation_remains_load_bearing(self):
        plan, _ = self.compose()
        for owner in (self.BLIND, self.NEW, self.FULL, self.OTHER):
            with self.subTest(owner=owner):
                missing = [report for report in self.reports if report[1]["task_id"] != owner]
                problems = cri.check(plan, missing)
                self.assertTrue(any(owner in p and "filed no review_attestation" in p for p in problems), problems)

    def test_old_and_new_blind_producer_reads_are_still_detected(self):
        plan, _ = self.compose()
        for index in (2, 3):
            for source in ("tools/producer.py", "observations/retained-result.json", "notes/producer-prior.md", "./"):
                with self.subTest(index=index, source=source):
                    reports = copy.deepcopy(self.reports)
                    reports[index][1]["sources_read"].append(source)
                    problems = cri.check(plan, reports)
                    self.assertTrue(any(reports[index][1]["task_id"] in p and "blind_from path(s)" in p for p in problems), problems)
        reports = copy.deepcopy(self.reports)
        reports[3][1]["sources_read"].append("notes/fresh-producer.md")
        self.assertTrue(any("blind_from path(s)" in p for p in cri.check(plan, reports)))

    def test_new_blind_and_full_owner_cannot_read_the_old_reviewers_artifacts(self):
        plan, _ = self.compose()
        for index in (1, 3):
            for source in (self.allowed[2], self.allowed[0], self.allowed[0].rsplit("/", 1)[0]+"/"):
                for flag in (True, False):
                    with self.subTest(index=index, source=source, flag=flag):
                        reports = copy.deepcopy(self.reports)
                        reports[index][1]["sources_read"].append(source)
                        reports[index][1]["read_sibling_reports"] = flag
                        self.assertTrue(cri.check(plan, reports))
        # An immutable old attestation may honestly name its own code; the new
        # protection against old-review reads does not rewrite that old phase.
        reports = copy.deepcopy(self.reports)
        reports[2][1]["sources_read"].append(self.allowed[0])
        self.assertEqual(cri.check(plan, reports), [])

    def test_stale_unknown_duplicate_replayed_or_plain_repeated_split_is_refused(self):
        for field, task in (("full_task", self.UNKNOWN), ("replaces_blind_task", self.UNKNOWN),
                            ("replacement_blind_task", self.BLIND), ("replacement_blind_task", self.OTHER)):
            with self.subTest(field=field, task=task):
                addon = copy.deepcopy(self.replacement)
                addon["blind_phase_replacement"][field] = task
                with self.assertRaises(ValueError):
                    self.compose(addon)
        plan, _ = self.compose()
        with self.assertRaises(ValueError):
            self.compose(base=plan)
        with self.assertRaises(ValueError):
            cri.compose_plan(self.initial, [("a.yaml", self.replacement), ("b.yaml", self.replacement)])
        plain = copy.deepcopy(self.replacement)
        del plain["blind_phase_replacement"]
        plain["what_changes"]["blind_rederivation_assigned_to"] = self.NEW
        with self.assertRaises(ValueError):
            self.compose(plain)

    def test_unowned_replacement_and_full_owner_or_old_joint_changes_are_refused(self):
        addon = copy.deepcopy(self.replacement)
        addon["joints_added"] = []
        with self.assertRaisesRegex(ValueError, "newly explicit joint"):
            self.compose(addon)
        for joint in ("J2", "JB", "J1"):
            addon = copy.deepcopy(self.replacement)
            addon["what_changes"]["owners"] = {joint: self.NEW}
            with self.assertRaises(ValueError):
                self.compose(addon)
        plan, _ = self.compose()
        for joint in ("J2", "JB", "J1"):
            with self.assertRaises(ValueError):
                cri.compose_plan(plan, [("later.yaml", {"what_changes": {"owners": {joint: self.NEW}}})])

    def test_directive_schema_ids_reason_and_archive_binding_are_strict(self):
        for value in (None, [], "replacement", {}, [{"full_task": self.FULL}]):
            addon = copy.deepcopy(self.replacement)
            addon["blind_phase_replacement"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.compose(addon)
        mutations = [("reason", None), ("reason", " "), ("prior_artifacts_remain_required", False),
                     ("prior_artifacts_remain_required", 1), ("unknown", True)]
        mutations += [(field, value) for field in ("full_task", "replaces_blind_task", "replacement_blind_task")
                      for value in (None, [], 5, "TASK-A", self.FULL)]
        for field, value in mutations:
            if field == "full_task" and value == self.FULL:
                continue
            addon = copy.deepcopy(self.replacement)
            addon["blind_phase_replacement"][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                self.compose(addon)
        for field, value in (("task", self.NEW), ("commit_sha", "a"*39), ("commit_sha", []),
                             ("verification", "../outside.json"), ("verification", "synthetic/"),
                             ("verification", "synthetic/*"), ("verification", None), ("extra", True)):
            addon = copy.deepcopy(self.replacement)
            addon["blind_phase_replacement"]["retained_blind_archive"][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                self.compose(addon)

    def test_misplaced_unknown_and_conflicting_directives_fail_closed(self):
        directive = self.replacement["blind_phase_replacement"]
        for addon in ({"what_changes": {"blind_phase_replacement": directive}},
                      {"procedure_deviations": [{"blind_phase_replacement": directive}]},
                      {"blind_phase_replacements": directive}):
            with self.subTest(addon=addon), self.assertRaises(ValueError):
                self.compose(addon)
        for document in ({"blind_phase_replacement": directive},
                         {"read_plan_addendum": self.replacement},
                         {"handoff": {"review_plan_addendum": self.replacement}}):
            with self.subTest(document=document), self.assertRaises(ValueError):
                cri._addendum_of(document)
        addon = copy.deepcopy(self.replacement)
        addon["what_changes"]["blind_rederivation_assigned_to"] = self.NEW
        with self.assertRaises(ValueError):
            self.compose(addon)

    def test_replacement_grant_requires_exact_new_own_seven_and_rationale(self):
        for value in (None, " "):
            addon = copy.deepcopy(self.replacement)
            addon["blindness_lift_rationale"] = value
            with self.assertRaises(ValueError):
                self.compose(addon)
        for tasks in ([self.OTHER], [self.NEW], [self.FULL, self.OTHER], [], None):
            addon = copy.deepcopy(self.replacement)
            addon["blindness_lifted_for_additions"] = tasks
            with self.subTest(tasks=tasks), self.assertRaises(ValueError):
                self.compose(addon)
        for paths in (self.allowed, self.allowed+self.new_allowed, self.new_allowed[:-1],
                      self.new_allowed+[self.new_allowed[0]], [self.new_allowed[0].rsplit("/", 1)[0]+"/"],
                      [path.replace("report.md", "*") for path in self.new_allowed],
                      [path.replace("report.md", "unapproved.txt") for path in self.new_allowed],
                      [self.new_allowed[0].replace(self.NEW, self.OTHER)]+self.new_allowed[1:]):
            addon = copy.deepcopy(self.replacement)
            addon["lift_read_allowlist"] = paths
            with self.subTest(paths=paths), self.assertRaises(ValueError):
                self.compose(addon)

    def test_symlink_escape_and_existing_directory_in_exact_seven_are_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for directory_target in (False, True):
                with self.subTest(directory_target=directory_target):
                    target = root/self.new_allowed[2]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if directory_target:
                        target.mkdir()
                    else:
                        target.symlink_to(root/"outside.md")
                    with patch.object(cri, "REPO", str(root)), self.assertRaises(ValueError):
                        self.compose()
                    target.rmdir() if directory_target else target.unlink()

    def test_protection_narrowing_controls_or_broad_lifts_cannot_pass(self):
        for field, value in (("blind_rederivation", {"blind_from": []}),
                             ("blind_rederivation", {"required": False}),
                             ("blind_rederivation", {"quantity": "changed"}),
                             ("blind_rederivation", {"parameters": {}}),
                             ("blindness", {"mutual": False}),
                             ("blindness", {"lifted_for": [self.OTHER, self.FULL]}),
                             ("proves_too_much", {"objects": []}), ("joints_removed", ["JB"])):
            addon = copy.deepcopy(self.replacement)
            addon[field] = value
            with self.subTest(field=field, value=value):
                plan, _ = self.compose(addon)
                self.assertTrue(any("REFUSED" in p for p in cri.check(plan, self.reports)))
        base = copy.deepcopy(self.initial)
        base["blindness"]["lifted_for"].append(self.FULL)
        with self.assertRaisesRegex(ValueError, "broad blindness lift"):
            self.compose(base=base)

    def test_later_scoped_lift_cannot_union_old_or_extra_artifacts(self):
        plan, _ = self.compose()
        for paths in (self.allowed, [self.new_allowed[0].replace("independent_enumerator.py", "extra.txt")]):
            addon = {"blindness_lifted_for_additions": [self.FULL],
                     "blindness_lift_rationale": "Attempted later extension", "lift_read_allowlist": paths}
            with self.subTest(paths=paths), self.assertRaises(ValueError):
                cri.compose_plan(plan, [("later.yaml", addon)])

    def test_second_explicit_replacement_keeps_every_retained_blind_owner_protected(self):
        plan, _ = self.compose()
        next_task = "TASK-20261015-abcdef"
        addon = copy.deepcopy(self.replacement)
        directive = addon["blind_phase_replacement"]
        directive["replaces_blind_task"] = self.NEW
        directive["replacement_blind_task"] = next_task
        directive["retained_blind_archive"]["task"] = self.NEW
        addon["joints_added"][0]["joint"] = "JK -- Another synthetic replacement derivation"
        addon["joints_added"][0]["assigned_to"] = next_task
        addon["lift_read_allowlist"] = [path.replace(self.NEW, next_task) for path in self.new_allowed]
        later, _ = self.compose(addon, plan)
        reports = copy.deepcopy(self.reports)
        reports[1][1]["sources_read"] = ["tools/producer.py"]+addon["lift_read_allowlist"]
        reports.append((f"reviews/{next_task}/attestation.yaml", {
            "task_id": next_task, "joints_owned": ["JK"], "verdict": "inconclusive",
            "sources_read": ["statement.md"], "read_sibling_reports": False, "blind_from_respected": True}))
        self.assertEqual(cri.check(later, reports), [])
        self.assertEqual(len(later["_blind_phase_history"]), 2)
        self.assertEqual(later["_blind_phase_history"][0], plan["_blind_phase_history"][0])
        for index in (2, 3, 4):
            bad = copy.deepcopy(reports)
            bad[index][1]["sources_read"].append("tools/producer.py")
            self.assertTrue(any(bad[index][1]["task_id"] in p and "blind_from path(s)" in p
                                for p in cri.check(later, bad)))
        for path in self.allowed+self.new_allowed:
            bad = copy.deepcopy(reports)
            bad[1][1]["sources_read"].append(path)
            self.assertTrue(any("outside scoped" in p for p in cri.check(later, bad)))

    def test_malformed_or_missing_prior_phase_and_scope_cannot_be_replaced(self):
        for field, value in (("_blind_phase_assignments", []), ("_blind_phase_assignments", {}),
                             ("blindness", None), ("blindness", "bad"),
                             ("blindness", {"mutual": True, "scoped_lifts": []}),
                             ("_blind_phase_history", [None])):
            base = copy.deepcopy(self.initial)
            base[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                self.compose(base=base)
        for field, value in (("quantity", " "), ("blind_from", None), ("blind_from", []),
                             ("blind_from", [None]), ("assigned_to", self.UNKNOWN)):
            base = copy.deepcopy(self.initial)
            base["blind_rederivation"][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                self.compose(base=base)

    def _native(self, reports=None, replacement=None, raw=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = root/"review-plan.yaml"
            plan.write_text(yaml.safe_dump({"review_plan": self.base}), encoding="utf-8")
            (root/"initial.yaml").write_text(yaml.safe_dump({"review_plan_addendum": self.addendum}), encoding="utf-8")
            (root/"replacement.yaml").write_text(raw if raw is not None else yaml.safe_dump({
                "review_plan_addendum": self.replacement if replacement is None else replacement}), encoding="utf-8")
            paths = []
            for index, (_, attestation) in enumerate(self.reports if reports is None else reports):
                path = root/f"report-{index}.yaml"
                path.write_text(yaml.safe_dump({"review_attestation": attestation}), encoding="utf-8")
                paths.append(str(path))
            result = subprocess.run([sys.executable, str(Path(cri.__file__)), "--plan", str(plan), "--reports", *paths],
                                    capture_output=True, text=True,
                                    env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
            return result.returncode, result.stdout+result.stderr

    def test_actual_cli_composes_and_requires_old_new_and_all_full_attestations(self):
        code, output = self._native()
        self.assertEqual(code, 0, output)
        self.assertIn("explicit blind-phase replacement", output)
        self.assertIn("PASS: 4 report(s)", output)
        for owner in (self.BLIND, self.NEW, self.FULL, self.OTHER):
            with self.subTest(owner=owner):
                code, output = self._native([report for report in self.reports if report[1]["task_id"] != owner])
                self.assertEqual(code, 1, output)
                self.assertNotIn("PASS:", output)
        reports = copy.deepcopy(self.reports)
        reports[2][1]["sources_read"].append("tools/producer.py")
        code, output = self._native(reports)
        self.assertEqual(code, 1, output)
        self.assertNotIn("PASS:", output)

    def test_cli_rejects_misplaced_duplicate_and_stale_replacement(self):
        addon = copy.deepcopy(self.replacement)
        addon["blind_phase_replacement"]["replaces_blind_task"] = self.UNKNOWN
        code, output = self._native(replacement=addon)
        self.assertEqual(code, 2, output)
        self.assertNotIn("PASS:", output)
        for raw in (yaml.safe_dump({"review_plan_addendum": {
                "extends": "review-plan.yaml", "what_changes": {"blind_phase_replacement": {}}}}),
                    "review_plan_addendum:\n  extends: review-plan.yaml\n  blind_phase_replacement: {}\n  blind_phase_replacement: {}\n",
                    "review_plan_addendum:\n  extends: review-plan.yaml\n  blind_phase_replacement:\n    reason: a\n    reason: b\n",
                    "review_plan_addendum:\n  blind_phase_replacement: {}\nreview_plan_addendum:\n  extends: review-plan.yaml\n",
                    'review_plan_addendum:\n  extends: review-plan.yaml\n  "blind_phase_replacemen\\u0074": {}\n  "blind_phase_replacemen\\u0074": {}\n'):
            with self.subTest(raw=raw):
                code, output = self._native(raw=raw)
                self.assertEqual(code, 2, output)
                self.assertIn("invalid review-plan addendum", output)
                self.assertNotIn("PASS:", output)


class GitSourceIdentity(unittest.TestCase):
    """Archived citations obey the same positive AND negative read scopes."""

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.repo = Path(cls.directory.name)
        def git(*args):
            return subprocess.check_output(["git", "-C", str(cls.repo), *args], text=True).strip()
        git("init", "-q")
        (cls.repo/"fixture.txt").write_text("scope fixture\n")
        git("add", "fixture.txt")
        git("-c", "user.name=Scope Test", "-c", "user.email=scope@example.invalid",
            "-c", "commit.gpgSign=false", "-c", "core.hooksPath=/dev/null", "commit", "-qm", "fixture")
        cls.commit = git("rev-parse", "HEAD")
        cls.blob = git("rev-parse", "HEAD:fixture.txt")

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def setUp(self):
        self.case = DeclaredBlindPhaseComposition()
        self.case.setUp()
        self.repo_patch = patch.object(cri, "REPO", str(self.repo))
        self.repo_patch.start()
        self.addCleanup(self.repo_patch.stop)
        cri._git_source_commit.cache_clear()

    def alias(self, path, revision=None):
        return "git:"+(revision or self.commit)+":"+path

    def test_exact_full_and_unambiguous_short_aliases_are_allowed(self):
        for revision in (self.commit, self.commit[:10]):
            with self.subTest(revision=revision):
                reports = copy.deepcopy(self.case.reports)
                reports[1][1]["sources_read"] = [self.alias(p, revision) for p in self.case.allowed]
                self.assertEqual(self.case._problems(reports=reports), [])
                self.assertEqual(cri._read_path(self.alias(self.case.allowed[0], revision)),
                                 cri._read_path(self.case.allowed[0]))

    def test_alias_cannot_hide_a_protected_producer_read(self):
        for revision in (self.commit, self.commit[:10]):
            reports = copy.deepcopy(self.case.reports)
            reports[2][1]["sources_read"].append(self.alias("tools/producer.py", revision))
            self.assertTrue(any("blind_from path(s)" in p for p in self.case._problems(reports=reports)))

    def test_alias_cannot_read_an_unauthorized_sibling(self):
        for revision in (self.commit, self.commit[:10]):
            for path in (f"reviews/{self.case.OTHER}/report.md", self.case.allowed[0]+".extra"):
                reports = copy.deepcopy(self.case.reports)
                reports[1][1]["sources_read"].append(self.alias(path, revision))
                self.assertTrue(any("outside scoped lift_read_allowlist" in p
                                    for p in self.case._problems(reports=reports)))

    def test_blind_task_cannot_hide_sibling_read_with_false_flag(self):
        reports = copy.deepcopy(self.case.reports)
        reports[2][1]["sources_read"].append(self.alias(f"reviews/{self.case.FULL}/report.md"))
        self.assertTrue(any("without an authorized blindness lift" in p
                            for p in self.case._problems(reports=reports)))

    def test_malformed_unknown_symbolic_and_noncommit_aliases_fail_closed(self):
        bad = ["git:HEAD:fixture.txt", "git:main:fixture.txt", "git:123:fixture.txt",
               self.alias("fixture.txt", "0"*40), self.alias("fixture.txt", self.blob),
               self.alias("/absolute"), self.alias("../escape"), self.alias("a/../b"),
               self.alias("a/./b"), self.alias("a//b"), self.alias("a/"),
               self.alias("a\\b"), self.alias("a:b"), self.alias("a*"), self.alias("a?"),
               self.alias("a[b]"), self.alias("a\nb"), " "+self.alias("fixture.txt"),
               self.alias("fixture.txt")+" ", self.alias(""), "GIT:"+self.commit+":fixture.txt"]
        for source in bad:
            with self.subTest(source=source):
                reports = copy.deepcopy(self.case.reports)
                # Even a legacy broadly lifted reviewer must declare valid identities.
                reports[0][1]["sources_read"] = [source]
                self.assertTrue(any("invalid Git source identity" in p
                                    for p in self.case._problems(reports=reports)))

    def test_ambiguous_object_prefix_is_rejected(self):
        response = subprocess.CompletedProcess([], 0, "abcdef0"+"1"*33+"\nabcdef0"+"2"*33+"\n", "")
        with patch.object(cri.subprocess, "run", return_value=response):
            with self.assertRaisesRegex(cri.InvalidGitSource, "ambiguous"):
                cri._read_path(self.alias("fixture.txt", "abcdef0"))

    def test_git_failure_is_a_finding_instead_of_a_pass_or_crash(self):
        reports = copy.deepcopy(self.case.reports)
        reports[1][1]["sources_read"].append(self.alias("fixture.txt"))
        with patch.object(cri.subprocess, "run", side_effect=subprocess.TimeoutExpired("git", 10)):
            self.assertTrue(any("cannot resolve Git commit" in p
                                for p in self.case._problems(reports=reports)))

    def test_symlink_escape_cannot_acquire_authorized_path_identity(self):
        with tempfile.TemporaryDirectory() as external:
            link = self.repo/"escape"
            link.symlink_to(external, target_is_directory=True)
            try:
                with self.assertRaisesRegex(cri.InvalidGitSource, "escapes repository"):
                    cri._read_path(self.alias("escape/report.md"))
            finally:
                link.unlink()

    def test_plain_absolute_relative_and_public_url_behavior_is_preserved(self):
        for source in ("fixture.txt", str(self.repo/"fixture.txt"), "https://example.invalid/paper"):
            self.assertEqual(cri._read_path(source), os.path.realpath(os.path.join(str(self.repo), source)))


if __name__ == "__main__":
    unittest.main()

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


if __name__ == "__main__":
    unittest.main()

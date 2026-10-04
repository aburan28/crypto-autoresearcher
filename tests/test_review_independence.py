"""Referee architecture: review plans and the independence they claim.

Independence is invisible in the output -- concurring reports look the same
whether reviewers worked blind on separate joints or all read each other and
converged on the most legible step. These tests pin the two halves that make
the difference recoverable: the plan is well-formed and written in advance
(validate_ledger), and the reviewers' attestations are consistent with it
(check_review_independence).
"""

from __future__ import annotations

import copy
import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

import check_review_independence as independence     # noqa: E402
import validate_ledger                               # noqa: E402


PLAN = {
    "claim_under_review": "the descent certificate is negative on every "
                          "off-line configuration in the tested window",
    "coordinator_prior": "I expect this to be wrong at the localisation step; "
                         "a configuration outside the window may still "
                         "contribute a positive square",
    "joints": [
        {"joint": "localisation",
         "assigned_to": "TASK-20260815-aaaaaa",
         "attack_plan": "crowd synthetic off-line configurations at the "
                        "window edge and show the certificate stays negative",
         "breaking_artifact": "one configuration with a positive certificate"},
        {"joint": "prime-side evaluation",
         "assigned_to": "TASK-20260815-bbbbbb",
         "attack_plan": "reduce the double sum by hand and check no "
                        "RH-strength input enters",
         "breaking_artifact": "a step requiring an unproved bound"},
    ],
    "blindness": {"mutual": True, "lifted_for": [], "rationale": None},
    "proves_too_much": {
        "objects": ["an anomalous curve where the conclusion is known false"],
        "failure_signature": "the certificate must go positive",
        "assigned_to": "TASK-20260815-cccccc",
    },
    "blind_rederivation": {
        "required": True,
        "quantity": "the trace of the compressed form over the window",
        "parameters": "X = 10^4, T = [50, 1000]",
        "blind_from": ["experiments/EXP-X/impl", "experiments/EXP-X/report.md"],
        "assigned_to": "TASK-20260815-dddddd",
    },
    "procedure_deviations": [],
}


def _attestation(task_id, joints, **kwargs):
    base = {
        "task_id": task_id,
        "joints_owned": joints,
        "sources_read": ["experiments/EXP-X/statement.md"],
        "read_sibling_reports": False,
        "blind_from_respected": None,
        "verdict": "holds",
    }
    base.update(kwargs)
    return base


def _reports(**overrides):
    made = {
        "TASK-20260815-aaaaaa": _attestation("TASK-20260815-aaaaaa",
                                             ["localisation"]),
        "TASK-20260815-bbbbbb": _attestation("TASK-20260815-bbbbbb",
                                             ["prime-side evaluation"]),
        "TASK-20260815-dddddd": _attestation("TASK-20260815-dddddd", [],
                                             blind_from_respected=True),
    }
    made.update(overrides)
    return [(f"/tmp/{k}.yaml", v) for k, v in made.items()]


class PlanSchemaTests(unittest.TestCase):
    """validate_ledger checks the plan's internal consistency."""

    def _errors(self, plan) -> list[str]:
        ctx = validate_ledger.Ctx(legacy_paths=set())
        validate_ledger.check_review_plan(
            "h.yaml", {"id": "TASK-20260815-000000", "review_plan": plan}, ctx)
        return ctx.errors

    def test_absent_plan_is_silent(self) -> None:
        ctx = validate_ledger.Ctx(legacy_paths=set())
        validate_ledger.check_review_plan("h.yaml", {"id": "x"}, ctx)
        self.assertEqual(ctx.errors, [])

    def test_complete_plan_passes(self) -> None:
        self.assertEqual(self._errors(copy.deepcopy(PLAN)), [])

    def test_missing_prior_is_rejected(self) -> None:
        plan = copy.deepcopy(PLAN)
        plan["coordinator_prior"] = None
        self.assertTrue(any("coordinator_prior" in e
                            for e in self._errors(plan)))

    def test_unowned_joint_is_rejected(self) -> None:
        plan = copy.deepcopy(PLAN)
        plan["joints"][0]["assigned_to"] = None
        self.assertTrue(any("assigned_to" in e for e in self._errors(plan)))

    def test_joint_without_worked_attack_is_rejected(self) -> None:
        plan = copy.deepcopy(PLAN)
        plan["joints"][1]["attack_plan"] = ""
        self.assertTrue(any("attack_plan" in e for e in self._errors(plan)))

    def test_duplicate_joint_is_rejected(self) -> None:
        plan = copy.deepcopy(PLAN)
        plan["joints"].append(dict(plan["joints"][0]))
        self.assertTrue(any("one joint, one owner" in e
                            for e in self._errors(plan)))

    def test_missing_proves_too_much_is_rejected(self) -> None:
        plan = copy.deepcopy(PLAN)
        plan["proves_too_much"]["objects"] = []
        self.assertTrue(any("proves_too_much" in e for e in self._errors(plan)))

    def test_lifted_blindness_needs_a_rationale(self) -> None:
        plan = copy.deepcopy(PLAN)
        plan["blindness"]["lifted_for"] = ["TASK-20260815-aaaaaa"]
        self.assertTrue(any("rationale" in e for e in self._errors(plan)))

    def test_rederivation_without_blind_from_is_rejected(self) -> None:
        plan = copy.deepcopy(PLAN)
        plan["blind_rederivation"]["blind_from"] = []
        self.assertTrue(any("blind_from" in e for e in self._errors(plan)))


class IndependenceTests(unittest.TestCase):
    """check_review_independence cross-checks the plan against attestations."""

    def test_consistent_round_passes(self) -> None:
        self.assertEqual(independence.check(copy.deepcopy(PLAN), _reports()), [])

    def test_unattested_owner_is_caught(self) -> None:
        reports = [r for r in _reports()
                   if r[1]["task_id"] != "TASK-20260815-bbbbbb"]
        problems = independence.check(copy.deepcopy(PLAN), reports)
        self.assertTrue(any("filed no review_attestation" in p
                            for p in problems))

    def test_reviewer_not_claiming_its_joint_is_caught(self) -> None:
        reports = _reports(**{"TASK-20260815-aaaaaa": _attestation(
            "TASK-20260815-aaaaaa", ["something else"])})
        problems = independence.check(copy.deepcopy(PLAN), reports)
        self.assertTrue(any("joints_owned" in p for p in problems))

    def test_undeclared_sibling_read_is_caught(self) -> None:
        reports = _reports(**{"TASK-20260815-aaaaaa": _attestation(
            "TASK-20260815-aaaaaa", ["localisation"],
            read_sibling_reports=True)})
        problems = independence.check(copy.deepcopy(PLAN), reports)
        self.assertTrue(any("not independent" in p for p in problems))

    def test_declared_sibling_read_is_allowed(self) -> None:
        plan = copy.deepcopy(PLAN)
        plan["blindness"]["lifted_for"] = ["TASK-20260815-aaaaaa"]
        plan["blindness"]["rationale"] = "hardening round; sees prior verdicts"
        reports = _reports(**{"TASK-20260815-aaaaaa": _attestation(
            "TASK-20260815-aaaaaa", ["localisation"],
            read_sibling_reports=True)})
        self.assertEqual(independence.check(plan, reports), [])

    def test_rederiver_reading_a_blind_from_path_is_caught(self) -> None:
        reports = _reports(**{"TASK-20260815-dddddd": _attestation(
            "TASK-20260815-dddddd", [], blind_from_respected=True,
            sources_read=["experiments/EXP-X/impl"])})
        problems = independence.check(copy.deepcopy(PLAN), reports)
        self.assertTrue(any("not independent of the implementation" in p
                            for p in problems))

    def test_rederiver_reading_under_a_blind_from_directory_is_caught(self) -> None:
        """A prefix match counts: blind_from names directories, not just files."""
        reports = _reports(**{"TASK-20260815-dddddd": _attestation(
            "TASK-20260815-dddddd", [], blind_from_respected=True,
            sources_read=["experiments/EXP-X/impl/solver.py"])})
        problems = independence.check(copy.deepcopy(PLAN), reports)
        self.assertTrue(any("not independent of the implementation" in p
                            for p in problems))

    def test_sibling_path_is_not_a_false_positive(self) -> None:
        """`impl-notes` must not match the `impl` prefix."""
        reports = _reports(**{"TASK-20260815-dddddd": _attestation(
            "TASK-20260815-dddddd", [], blind_from_respected=True,
            sources_read=["experiments/EXP-X/impl-notes.md"])})
        self.assertEqual(independence.check(copy.deepcopy(PLAN), reports), [])

    def test_rederiver_must_affirm_blind_from_respected(self) -> None:
        reports = _reports(**{"TASK-20260815-dddddd": _attestation(
            "TASK-20260815-dddddd", [], blind_from_respected=None)})
        problems = independence.check(copy.deepcopy(PLAN), reports)
        self.assertTrue(any("blind_from_respected" in p for p in problems))

    def test_missing_verdict_is_caught(self) -> None:
        reports = _reports(**{"TASK-20260815-aaaaaa": _attestation(
            "TASK-20260815-aaaaaa", ["localisation"], verdict=None)})
        problems = independence.check(copy.deepcopy(PLAN), reports)
        self.assertTrue(any("verdict" in p for p in problems))

    def test_two_owners_on_one_joint_is_caught(self) -> None:
        plan = copy.deepcopy(PLAN)
        plan["joints"][1]["joint"] = "localisation"
        problems = independence.check(plan, _reports())
        self.assertTrue(any("owners" in p for p in problems))


class MultiJointReviewerTests(unittest.TestCase):
    """A reviewer owning several joints reports one verdict PER JOINT.

    The contract is explicit that a blinded reviewer's whole-claim verdict is
    an opinion formed from a fraction of the evidence, so the compliant shape
    for a multi-joint reviewer is a mapping keyed by joint label. Every one of
    these shapes was produced by a real round; the checker used to raise
    TypeError on the mapping and so could not run on the round at all, which
    is worse than a wrong answer -- an unrunnable checker reads as a checker
    nobody needed (CORR-20260913-bfb071).
    """

    LABELLED = [
        {"joint": "J1 -- SEMAEV'S MEMORY MODEL. That peak memory is max(...)",
         "assigned_to": "TASK-20260913-da3982",
         "attack_plan": "rebuild the accounting from the frozen text",
         "breaking_artifact": "an accounting differing by more than 5 bits"},
        {"joint": "J4 -- THE MECHANISM. That yield loss is exponential in n",
         "assigned_to": "TASK-20260913-da3982",
         "attack_plan": "re-derive the yield law and vary t",
         "breaking_artifact": "a polynomial yield loss"},
    ]

    def _plan(self):
        plan = copy.deepcopy(PLAN)
        plan["joints"] = copy.deepcopy(self.LABELLED)
        plan["blind_rederivation"]["required"] = False
        plan["blind_rederivation"]["blind_from"] = []
        return plan

    def _round(self, **kwargs):
        return [("/tmp/a.yaml", _attestation("TASK-20260913-da3982",
                                             ["J1", "J4"], **kwargs))]

    def test_per_joint_mapping_under_verdict_is_read(self) -> None:
        problems = independence.check(
            self._plan(), self._round(verdict={"J1": "holds",
                                               "J4": "breaks"}))
        self.assertEqual(problems, [])

    def test_per_joint_mapping_under_verdicts_is_read(self) -> None:
        """The plural key, which one real attestation used."""
        problems = independence.check(
            self._plan(), self._round(verdict=None,
                                      verdicts={"J1": "holds",
                                                "J4": "inconclusive"}))
        self.assertEqual(problems, [])

    def test_mapping_missing_an_owned_joint_is_caught(self) -> None:
        problems = independence.check(self._plan(),
                                      self._round(verdict={"J1": "holds"}))
        self.assertTrue(any("J4" in p for p in problems), problems)

    def test_unrecognised_verdict_word_in_a_mapping_is_caught(self) -> None:
        problems = independence.check(
            self._plan(), self._round(verdict={"J1": "mostly fine",
                                               "J4": "holds"}))
        self.assertTrue(any("mostly fine" in p for p in problems), problems)

    def test_a_verdict_of_the_wrong_type_fails_rather_than_raises(self) -> None:
        problems = independence.check(self._plan(),
                                      self._round(verdict=["holds", "holds"]))
        self.assertTrue(any("mapping" in p for p in problems), problems)

    def test_paraphrased_joints_owned_is_matched_by_label(self) -> None:
        """Reviewers restate the joint; the label is what identifies it."""
        reports = [("/tmp/a.yaml", _attestation(
            "TASK-20260913-da3982",
            ["J1 -- Semaev's memory model (peak as max of store and working "
             "set; dense versus sparse; the variable count N)",
             "J4: the exponential-versus-polynomial mechanism"],
            verdict={"J1": "holds", "J4": "holds"}))]
        self.assertEqual(independence.check(self._plan(), reports), [])

    def test_an_unclaimed_joint_is_still_caught(self) -> None:
        reports = [("/tmp/a.yaml", _attestation(
            "TASK-20260913-da3982", ["J1"],
            verdict={"J1": "holds", "J4": "holds"}))]
        problems = independence.check(self._plan(), reports)
        self.assertTrue(any("joints_owned" in p for p in problems), problems)

    def test_scalar_verdict_still_works(self) -> None:
        self.assertEqual(independence.check(self._plan(),
                                           self._round(verdict="holds")), [])

    def test_label_extraction(self) -> None:
        for name, label in (
                ("J1 -- SEMAEV'S MEMORY MODEL. That peak memory is ...", "J1"),
                ("J4: the mechanism", "J4"),
                ("J6-BLIND -- the crossover n", "J6-BLIND"),
                ("localisation", "localisation"),
                ("prime-side evaluation", "prime-side evaluation")):
            self.assertEqual(independence._joint_label(name), label)


if __name__ == "__main__":
    unittest.main()

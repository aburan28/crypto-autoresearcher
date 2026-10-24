"""Pins the plan-key alias, and what the alias must NOT be used to do.

A round's plan is spelled `review_plan` by `templates/research-records.md` and
`read_plan` by zero-compute rounds whose joints are readings of external sources.
`coordination/review/sembin-20260916-e0a0c1/read-plan.yaml` is the second kind,
and before the alias the checker answered "no review_plan block" and exited 2 --
finding nothing at all, on a round that had six real problems in it. A committed
plan is immutable, so that round could not be brought into line by renaming its
key, and a checker that cannot read a plan is not a lenient checker but a silent
one.

The second class below is the more important one. An alias that let a round pass
by reading fewer of its fields would be worse than the refusal it replaced, so
the tests assert that the same plan is held to the same requirements under
either spelling.
"""

import copy
import hashlib
import io
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import yaml

import check_review_independence as C


def plan_body(prior="the Coordinator expects J-1 to confirm"):
    return textwrap.dedent(f"""
      id: REVIEW-TEST-000000
      coordinator_prior: {prior}
      joints:
        - id: J-1
          owner: TASK-20000101-000001
    """)


class TestThePlanKeyAlias(unittest.TestCase):
    def test_review_plan_is_read(self):
        doc = {"review_plan": {"id": "R", "joints": []}}
        self.assertEqual(C._plan_of(doc)["id"], "R")

    def test_read_plan_is_read(self):
        doc = {"read_plan": {"id": "R", "joints": []}}
        self.assertEqual(C._plan_of(doc)["id"], "R")

    def test_either_spelling_is_found_under_a_handoff(self):
        for key in C.PLAN_KEYS:
            doc = {"handoff": {key: {"id": "R", "joints": []}}}
            self.assertEqual(C._plan_of(doc)["id"], "R", msg=f"under {key}")

    def test_a_document_with_neither_key_is_still_refused(self):
        """The alias widens the spelling, not the requirement that a plan exist."""
        for doc in ({}, {"plan": {"id": "R"}}, {"review_plan": "not a mapping"}, None, []):
            self.assertIsNone(C._plan_of(doc))

    def test_review_plan_wins_when_both_are_present(self):
        """Deterministic, so a file carrying both cannot be read two ways.

        `review_plan` is the template's spelling and so is the one a reader would
        assume is authoritative.
        """
        doc = {"read_plan": {"id": "second"}, "review_plan": {"id": "first"}}
        self.assertEqual(C._plan_of(doc)["id"], "first")


class TestTheAddendumKeyAlias(unittest.TestCase):
    def test_both_spellings_are_read(self):
        for key in C.ADDENDUM_KEYS:
            doc = {key: {"extends": "p.yaml"}}
            self.assertEqual(C._addendum_of(doc)["extends"], "p.yaml", msg=key)

    def test_a_plan_is_not_mistaken_for_an_addendum(self):
        self.assertIsNone(C._addendum_of({"read_plan": {"id": "R"}}))
        self.assertIsNone(C._addendum_of({"review_plan": {"id": "R"}}))


class TestTheAliasDoesNotWeakenTheCheck(unittest.TestCase):
    """The same plan must be held to the same requirements under either key.

    This is the class that matters. The alias was added while unblocking a round
    the Coordinator itself was running, which is the exact circumstance in which
    a checker gets quietly loosened instead of read.
    """

    def test_an_empty_prior_is_refused_under_both_spellings(self):
        import yaml
        for key in C.PLAN_KEYS:
            plan = C._plan_of({key: yaml.safe_load(plan_body(prior="''"))})
            problems = C.check(plan, [])
            self.assertTrue(
                any("coordinator_prior" in p for p in problems),
                msg=f"an empty prior passed under {key}",
            )

    def test_an_unattested_joint_is_refused_under_both_spellings(self):
        import yaml
        for key in C.PLAN_KEYS:
            plan = C._plan_of({key: yaml.safe_load(plan_body())})
            problems = C.check(plan, [])
            self.assertTrue(problems, msg=f"an unattested joint passed under {key}")


class TestExplicitJointIdsDoNotWeakenTheCheck(unittest.TestCase):
    blind_task = "TASK-20000101-000001"
    peer_task = "TASK-20000101-000002"
    protected = "research/producer-only.json"

    def fixture(self):
        owners = [self.blind_task, self.blind_task, self.peer_task, self.peer_task]
        joints = [
            {"id": f"P{index}", "joint": f"P{index} -- Full statement for joint {index}.",
             "assigned_to": owner, "attack_plan": "Test the stated joint independently."}
            for index, owner in enumerate(owners, 1)
        ]
        plan = {
            "coordinator_prior": "The fixed controls should reject false conclusions.",
            "joints": joints,
            "blindness": {"mutual": True, "lifted_for": []},
            "proves_too_much": {
                "objects": [{"id": "known_false"}],
                "failure_signature": "Accepting the known-false object fails the review.",
            },
            "blind_rederivation": {
                "required": True, "assigned_to": self.blind_task,
                "quantity": "Exact public inventory", "blind_from": [self.protected],
            },
        }
        reports = [
            ("coordination/review/test/validator.yaml", {
                "task_id": self.blind_task, "joints_owned": ["P1", "P2"],
                "verdict": {"P1": "holds", "P2": "holds"},
                "sources_read": ["research/public.json"],
                "read_sibling_reports": False, "blind_from_respected": True,
            }),
            ("coordination/review/test/red-team.yaml", {
                "task_id": self.peer_task, "joints_owned": ["P3", "P4"],
                "verdict": {"P3": "holds", "P4": "inconclusive"},
                "sources_read": ["research/public.json"],
                "read_sibling_reports": False,
            }),
        ]
        return plan, reports

    def test_explicit_ids_match_attestations_while_statements_remain(self):
        plan, reports = self.fixture()
        self.assertEqual(C.check(plan, reports), [])
        self.assertTrue(all("Full statement" in joint["joint"] for joint in plan["joints"]))

    def test_legacy_joint_only_labels_still_match(self):
        plan, reports = self.fixture()
        for joint in plan["joints"]:
            del joint["id"]
        self.assertEqual(C.check(plan, reports), [])

    def test_wrong_explicit_id_cannot_fall_back_to_matching_statement(self):
        plan, reports = self.fixture()
        plan["joints"][2]["id"] = "P9"  # statement still starts with P3
        problems = C.check(plan, reports)
        self.assertTrue(any("P9" in problem and "does not claim" in problem
                            for problem in problems), problems)
        self.assertTrue(any("unassigned joint 'P3'" in problem for problem in problems), problems)

    def test_duplicate_explicit_id_is_rejected(self):
        plan, reports = self.fixture()
        plan["joints"][3]["id"] = "P3"
        self.assertTrue(any("has 2 owners" in problem for problem in C.check(plan, reports)))

    def test_present_but_empty_or_non_string_id_is_rejected(self):
        for malformed in ("", "   ", 3, None):
            with self.subTest(malformed=malformed):
                plan, reports = self.fixture()
                plan["joints"][0]["id"] = malformed
                self.assertTrue(any("joints[0].id must be a nonempty string" in problem
                                    for problem in C.check(plan, reports)))

    def test_wrong_owner_and_missing_attestation_still_fail(self):
        plan, reports = self.fixture()
        plan["joints"][3]["assigned_to"] = self.blind_task
        problems = C.check(plan, reports)
        self.assertTrue(any("does not claim joint 'P4'" in problem for problem in problems),
                        problems)
        self.assertTrue(any("claims unassigned joint 'P4'" in problem for problem in problems),
                        problems)
        plan, reports = self.fixture()
        self.assertTrue(any("filed no review_attestation" in problem
                            for problem in C.check(plan, reports[:1])))

    def test_bad_verdict_sibling_read_and_blind_leak_still_fail(self):
        plan, reports = self.fixture()
        reports[1][1]["verdict"]["P3"] = "pass"
        self.assertTrue(any("must be" in problem and "pass" in problem
                            for problem in C.check(plan, reports)))

        plan, reports = self.fixture()
        reports[0][1]["sources_read"] = [
            f"coordination/review/test/{self.peer_task}/report.md"]
        self.assertTrue(any("sibling artifact" in problem for problem in C.check(plan, reports)))

        plan, reports = self.fixture()
        reports[0][1]["sources_read"] = [self.protected]
        self.assertTrue(any("blind_from path" in problem for problem in C.check(plan, reports)))

    def test_multi_joint_scalar_verdict_is_rejected(self):
        plan, reports = self.fixture()
        reports[1][1]["verdict"] = "holds"
        self.assertTrue(any("per-joint verdict mapping" in problem
                            for problem in C.check(plan, reports)))

    def test_explicit_id_requires_nonempty_statement(self):
        for statement in ("", "   ", "P3", None):
            with self.subTest(statement=statement):
                plan, reports = self.fixture()
                plan["joints"][2]["joint"] = statement
                self.assertTrue(any("full statement" in problem
                                    for problem in C.check(plan, reports)))

    def test_single_joint_scalar_verdict_still_passes(self):
        plan, reports = self.fixture()
        plan["joints"] = plan["joints"][:1]
        reports = reports[:1]
        reports[0][1]["joints_owned"] = ["P1"]
        reports[0][1]["verdict"] = "holds"
        self.assertEqual(C.check(plan, reports), [])

    def test_cli_requires_external_plan_pin_and_rejects_statement_swap(self):
        plan, reports = self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan_path = root / "plan.yaml"
            report_paths = []
            for index, (_, attestation) in enumerate(reports):
                path = root / f"report-{index}.yaml"
                path.write_text(yaml.safe_dump({"review_attestation": attestation}), encoding="utf-8")
                report_paths.append(str(path))

            def run_with_pin(expected=None):
                argv = ["check_review_independence.py", "--plan", str(plan_path),
                        "--reports", *report_paths]
                if expected:
                    argv.extend(["--expected-plan-sha256", expected])
                output, errors = io.StringIO(), io.StringIO()
                with patch.object(sys, "argv", argv), redirect_stdout(output), redirect_stderr(errors):
                    result = C.main()
                return result, output.getvalue() + errors.getvalue()

            plan_path.write_text(yaml.safe_dump({"review_plan": plan}), encoding="utf-8")
            original_digest = hashlib.sha256(plan_path.read_bytes()).hexdigest()
            code, output = run_with_pin()
            self.assertEqual(code, 2, output)
            self.assertIn("expected-plan-sha256", output)
            code, output = run_with_pin(original_digest)
            self.assertEqual(code, 0, output)

            swapped = copy.deepcopy(plan)
            swapped["joints"][2]["joint"], swapped["joints"][3]["joint"] = (
                swapped["joints"][3]["joint"], swapped["joints"][2]["joint"])
            plan_path.write_text(yaml.safe_dump({"review_plan": swapped}), encoding="utf-8")
            code, output = run_with_pin(original_digest)
            self.assertEqual(code, 2, output)
            self.assertIn("SHA-256 mismatch", output)

    def test_top_level_sealed_validator_schema_is_not_inferred(self):
        self.assertIsNone(C._attestation_of({
            "schema": "crypto.autoresearch.independent_blind_review_attestation.v1",
            "task_id": self.blind_task,
            "review_scope": {"joints": ["P1", "P2"]},
            "verdicts": {"P1": "original_raw_archive_inventory_independently_derived"},
        }))


if __name__ == "__main__":
    unittest.main(verbosity=2)

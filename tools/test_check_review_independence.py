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

import textwrap
import unittest

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


if __name__ == "__main__":
    unittest.main(verbosity=2)

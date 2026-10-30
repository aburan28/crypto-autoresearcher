"""Keep independent blind-quantity scopes intact during plan validation."""
import copy
from pathlib import Path
import unittest

from tools import validate_ledger as ledger


class BlindQuantityScopeTests(unittest.TestCase):
    def plan(self):
        return {
            "claim_under_review": "A fixed archived claim",
            "coordinator_prior": "Recorded before the review",
            "joints": [{"joint": "J1", "assigned_to": "original-reviewer",
                        "attack_plan": "Recompute the stated quantity"}],
            "proves_too_much": {"objects": ["Known-false control"],
                                "failure_signature": "Acceptance of that control"},
            "blind_rederivation": {"required": True, "quantities": [
                {"quantity": "First quantity", "assigned_to": "first-reviewer",
                 "blind_from": ["producer/first.py", "first-result.json"]},
                {"quantity": "Second quantity", "assigned_to": "second-reviewer",
                 "blind_from": ["producer/second.py"]},
            ]},
        }

    def errors(self, plan):
        ctx = ledger.Ctx(set())
        ledger.check_review_plan(str(Path(ledger.REPO) / "scope-control.yaml"),
                                 {"review_plan": plan}, ctx)
        return ctx.errors

    def test_distinct_quantity_scopes_are_valid_without_mutation(self):
        plan = self.plan()
        original = copy.deepcopy(plan)
        self.assertEqual(self.errors(plan), [])
        self.assertEqual(plan, original)
        self.assertNotIn("first-result.json",
                         plan["blind_rederivation"]["quantities"][1]["blind_from"])

    def test_any_unowned_quantity_is_rejected(self):
        plan = self.plan()
        del plan["blind_rederivation"]["quantities"][1]["assigned_to"]
        self.assertTrue(any("quantities[1].assigned_to" in e for e in self.errors(plan)))

    def test_parent_fields_do_not_mask_a_missing_scoped_restriction(self):
        plan = self.plan()
        plan["blind_rederivation"].update(quantity="parent", assigned_to="parent",
                                            blind_from=["parent-source.py"])
        del plan["blind_rederivation"]["quantities"][1]["blind_from"]
        self.assertTrue(any("quantities[1].blind_from" in e for e in self.errors(plan)))

    def test_empty_or_nonmapping_quantity_lists_are_rejected(self):
        for quantities in ([], ["unstructured quantity"]):
            with self.subTest(quantities=quantities):
                plan = self.plan()
                plan["blind_rederivation"]["quantities"] = quantities
                self.assertTrue(self.errors(plan))

    def test_original_single_quantity_requirements_still_apply(self):
        plan = self.plan()
        plan["blind_rederivation"] = {"required": True, "quantity": "one"}
        errors = self.errors(plan)
        self.assertTrue(any("blind_rederivation.assigned_to" in e for e in errors))
        self.assertTrue(any("blind_rederivation.blind_from" in e for e in errors))


if __name__ == "__main__":
    unittest.main()

"""Keep independent blind-quantity scopes intact during plan validation."""
import copy
from pathlib import Path
import unittest

import yaml

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

    def named_plan(self):
        plan = self.plan()
        plan["blind_rederivation"] = {
            "required": True, "quantity": "Both named quantities",
            "assigned_to": "shared-reviewer", "blind_from": ["producer/"],
            "quantities": [
                {"name": "first", "statement": "First stated quantity",
                 "blind_from": ["producer/first-result.json"]},
                {"name": "second", "statement": "Second stated quantity",
                 "blind_from": ["producer/second-result.json"]},
            ],
        }
        return plan

    def test_named_details_share_one_explicit_parent_assignment(self):
        plan = self.named_plan()
        original = copy.deepcopy(plan)
        self.assertEqual(self.errors(plan), [])
        self.assertEqual(plan, original)

    def test_named_details_still_require_the_complete_parent_contract(self):
        for field in ("quantity", "assigned_to", "blind_from"):
            with self.subTest(field=field):
                plan = self.named_plan()
                del plan["blind_rederivation"][field]
                self.assertTrue(any(f"blind_rederivation.{field}" in e
                                    for e in self.errors(plan)))

    def test_named_detail_cannot_borrow_parent_blind_from(self):
        plan = self.named_plan()
        del plan["blind_rederivation"]["quantities"][1]["blind_from"]
        self.assertTrue(any("quantities[1].blind_from" in e for e in self.errors(plan)))

    def test_named_details_require_nonempty_names_and_statements(self):
        for field in ("name", "statement"):
            with self.subTest(field=field):
                plan = self.named_plan()
                plan["blind_rederivation"]["quantities"][1][field] = " "
                self.assertTrue(any(f"quantities[1].{field}" in e for e in self.errors(plan)))

    def test_independent_rows_cannot_hide_in_a_shared_detail_list(self):
        plan = self.named_plan()
        plan["blind_rederivation"]["quantities"][1]["assigned_to"] = "other-reviewer"
        self.assertTrue(self.errors(plan))

    def test_three_archived_shared_assignment_plans_pass_without_mutation(self):
        for experiment in ("842864", "ef7fa4", "f14cbb"):
            relative = f"experiments/EXP-BINSTD-{experiment}/review/review-plan.yaml"
            with self.subTest(path=relative):
                doc = yaml.safe_load((Path(ledger.REPO) / relative).read_bytes())
                plan = doc.get("review_plan", doc)
                original = copy.deepcopy(plan)
                self.assertEqual(self.errors(plan), [])
                self.assertEqual(plan, original)


if __name__ == "__main__":
    unittest.main()

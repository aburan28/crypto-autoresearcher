"""Design-contract regressions, not elliptic-curve performance experiments."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("volcano_design_check", HERE / "check_plan.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plan = json.loads((HERE / "campaign.json").read_text(encoding="utf-8"))

    def rejected(self) -> None:
        self.assertTrue(MODULE.validate(self.plan))

    def test_current_plan(self) -> None:
        self.assertEqual(MODULE.validate(self.plan), [])

    def test_ten_distinct_designs(self) -> None:
        self.assertEqual(len({x["key"] for x in self.plan["experiments"]}), 10)

    def test_no_dispatch(self) -> None:
        self.plan["dispatchable"] = True
        self.rejected()

    def test_no_fabricated_approval(self) -> None:
        self.plan["experiments"][0]["approved_by"] = "coordinator"
        self.rejected()

    def test_no_completed_claim(self) -> None:
        self.plan["status"] = "completed"
        self.rejected()

    def test_repository_identity(self) -> None:
        self.plan["repository"] = "aburan28/crypto"
        self.rejected()

    def test_no_fixed_research_cap(self) -> None:
        self.plan["budget"]["maximum_batches"] = 1
        self.rejected()

    def test_machine_guard_required(self) -> None:
        self.plan["budget"]["maximum_workers"] = 0
        self.rejected()

    def test_watchdog_not_evidence(self) -> None:
        del self.plan["budget"]["watchdog_semantics"]
        self.rejected()

    def test_no_degree_conflation(self) -> None:
        self.plan["metrics"]["degree_fields"].remove("max_processed_degree")
        self.rejected()

    def test_no_final_basis_substitution(self) -> None:
        self.plan["metrics"]["degree_fields"].remove("certified_solving_degree")
        self.rejected()

    def test_search_cost_not_free(self) -> None:
        self.plan["metrics"]["cost_components"].remove("candidate_search")
        self.rejected()

    def test_failed_targets_not_free(self) -> None:
        self.plan["metrics"]["cost_components"].remove("solve_all_attempts")
        self.rejected()

    def test_rank_coefficient_field_required(self) -> None:
        del self.plan["metrics"]["rank_field"]
        self.rejected()

    def test_censoring_required(self) -> None:
        self.plan["outcomes"].remove("right_censored")
        self.rejected()

    def test_denominator_policy_required(self) -> None:
        del self.plan["shared_protocol"]["denominators"]
        self.rejected()

    def test_uniform_target_policy_required(self) -> None:
        del self.plan["shared_protocol"]["targets"]
        self.rejected()

    def test_holdout_policy_required(self) -> None:
        del self.plan["shared_protocol"]["holdout"]
        self.rejected()

    def test_no_closed_screen_replay(self) -> None:
        self.plan["profiles"]["smoke"]["decomposition_lengths"] = [3]
        self.rejected()

    def test_toy_scope(self) -> None:
        self.plan["profiles"]["paired"]["binary_degrees"] = [131]
        self.rejected()

    def test_class_replication(self) -> None:
        self.plan["profiles"]["paired"]["classes_per_field"] = 2
        self.rejected()

    def test_unknown_dependency(self) -> None:
        self.plan["experiments"][0]["depends_on"] = ["missing"]
        self.rejected()

    def test_cycle(self) -> None:
        self.plan["experiments"][0]["depends_on"] = ["transport"]
        self.rejected()

    def test_duplicate_key(self) -> None:
        self.plan["experiments"].append(copy.deepcopy(self.plan["experiments"][0]))
        self.rejected()

    def test_falsifier_required(self) -> None:
        self.plan["experiments"][0]["falsifier"] = ""
        self.rejected()

    def test_controls_required(self) -> None:
        self.plan["experiments"][0]["controls"] = []
        self.rejected()

    def test_input_not_mutated(self) -> None:
        before = copy.deepcopy(self.plan)
        MODULE.validate(self.plan)
        self.assertEqual(self.plan, before)


if __name__ == "__main__":
    unittest.main()

"""Local design-contract tests, not point-decomposition benchmarks."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("pair_reuse_check", HERE / "check_plan.py")
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class PlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plan = json.loads((HERE / "campaign.json").read_text(encoding="utf-8"))

    def assert_rejected(self) -> None:
        self.assertTrue(CHECK.validate(self.plan))

    def test_current_plan_passes(self) -> None:
        self.assertEqual(CHECK.validate(self.plan), [])

    def test_non_dispatchable(self) -> None:
        self.plan["dispatchable"] = True
        self.assert_rejected()

    def test_prerequisite_cannot_be_removed(self) -> None:
        self.plan["prerequisite"]["pull_request"] = 0
        self.assert_rejected()

    def test_supersession_checks_must_not_be_waived(self) -> None:
        self.plan["prerequisite"]["required_disposition"] = "Repair validation."
        self.assert_rejected()

    def test_all_three_arms_are_required(self) -> None:
        del self.plan["arms"]["expanded_rebuilt"]
        self.assert_rejected()

    def test_primary_comparator_is_expanded_reuse(self) -> None:
        self.plan["arms"]["expanded_reused"] = "secondary"
        self.assert_rejected()

    def test_query_workload_is_frozen(self) -> None:
        self.plan["workloads"]["query_counts"] = [1, 512]
        self.assert_rejected()

    def test_target_sidecar_is_withheld(self) -> None:
        self.plan["workloads"]["target_rule"] = "Targets selected by outcome."
        self.assert_rejected()

    def test_table_construction_is_charged(self) -> None:
        self.plan["cost_components"].remove("table_construction")
        self.assert_rejected()

    def test_witness_verification_is_required(self) -> None:
        self.plan["controls"].remove(
            "Every returned witness replays by exact group addition to its original target and every summand is in the admitted base."
        )
        self.assert_rejected()

    def test_zero_leakage_control_is_required(self) -> None:
        self.plan["controls"].remove(
            "Fresh process per job; no hidden target joins, previous table, point-to-log table, full-group catalog, or witness cache."
        )
        self.assert_rejected()

    def test_uncertainty_threshold_is_required(self) -> None:
        self.plan["analysis"]["promotion_gate"] = "Median ratio below one."
        self.assert_rejected()

    def test_censored_queries_are_not_unsat(self) -> None:
        self.plan["analysis"]["censoring"] = "Drop timeout cells."
        self.assert_rejected()

    def test_no_fabricated_result_or_id(self) -> None:
        self.plan["run_id"] = "RUN-KIC-000000"
        self.assert_rejected()

    def test_validator_does_not_mutate_input(self) -> None:
        before = copy.deepcopy(self.plan)
        CHECK.validate(self.plan)
        self.assertEqual(self.plan, before)


if __name__ == "__main__":
    unittest.main()

import unittest
from research.code.koblitz_followthrough.frobenius_metrics import FrobeniusMetrics
from research.code.koblitz_followthrough.likelihood import brier_score, log_loss, calibration_error, threshold_accounting


class FollowthroughMetricsTest(unittest.TestCase):
    def test_frobenius_accounting(self):
        m = FrobeniusMetrics(
            raw_factor_base_points=120,
            effective_factor_base_columns=10,
            baseline_solver_work=40,
            candidate_solver_work=20,
            baseline_relation_work=30,
            candidate_relation_work=10,
            baseline_la_dimension=100,
            candidate_la_dimension=20,
        ).to_dict()
        self.assertEqual(m["orbit_column_reduction"], 12)
        self.assertEqual(m["solver_work_reduction"], 2)
        self.assertEqual(m["relation_work_reduction"], 3)
        self.assertEqual(m["linear_algebra_dimension_reduction"], 5)

    def test_likelihood_metrics(self):
        y = [0, 0, 1, 1]
        p = [0.1, 0.2, 0.8, 0.9]
        self.assertLess(brier_score(y, p), 0.05)
        self.assertLess(log_loss(y, p), 0.3)
        self.assertGreaterEqual(calibration_error(y, p, bins=2), 0)
        safe = threshold_accounting(y, p, 0.5)
        self.assertEqual(safe["false_negatives"], 0)
        self.assertTrue(safe["hard_rejection_gate_passed"])

    def test_unsafe_threshold_is_visible(self):
        result = threshold_accounting([1, 0], [0.1, 0.9], 0.5)
        self.assertEqual(result["false_negatives"], 1)
        self.assertFalse(result["hard_rejection_gate_passed"])


if __name__ == "__main__":
    unittest.main()

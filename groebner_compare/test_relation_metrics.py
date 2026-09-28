import unittest

from .relation_metrics import RelationRank, comparison_gate


class RelationMetricsTests(unittest.TestCase):
    def test_rank_is_not_row_count(self):
        rank = RelationRank(29, 3)
        self.assertEqual(rank.add([1, 2, 0]), "independent")
        self.assertEqual(rank.add([-1, -2, 0]), "duplicate")
        self.assertEqual(rank.add([0, 1, 1]), "independent")
        self.assertEqual(rank.add([1, 3, 1]), "dependent")
        self.assertEqual(rank.rank, 2)
        self.assertEqual(rank.add([0, 0, 0]), "dependent")
        with self.assertRaises(ValueError):
            rank.add([1])
        self.assertEqual(rank.rank, 2)

    def runs(self):
        return [{"backend": b, "seed": seed, "status": "complete", "rank": 8,
                 "verification_replayed": True, "workload_sha256": str(seed),
                 "base_sha256": "same", "accounting": "full", "charged_wall_seconds": cost}
                for seed in range(5) for b, cost in [("direct", 10), ("sat", 12), ("new", 4)]]

    def test_gate_and_fail_closed(self):
        runs = self.runs()
        self.assertEqual(comparison_gate(runs, ["direct", "sat"], "new")["status"], "pass")
        runs[-1]["rank"] = 0
        self.assertEqual(comparison_gate(runs, ["direct", "sat"], "new")["status"], "insufficient_evidence")
        runs = self.runs()
        runs[0]["workload_sha256"] = "different"
        with self.assertRaises(ValueError):
            comparison_gate(runs, ["direct", "sat"], "new")
        runs = self.runs()
        runs[-1]["charged_wall_seconds"] = 20
        self.assertEqual(comparison_gate(runs, ["direct", "sat"], "new")["status"], "not_met")


if __name__ == "__main__":
    unittest.main()

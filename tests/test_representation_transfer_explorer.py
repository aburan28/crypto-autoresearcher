"""Correctness controls for the offline toy transfer explorer."""
import importlib.util
from pathlib import Path
import sys
import unittest

PATH = Path(__file__).resolve().parents[1] / "tools" / "representation_transfer_explorer.py"
spec = importlib.util.spec_from_file_location("transfer_explorer", PATH)
lab = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = lab
spec.loader.exec_module(lab)


class TransferTests(unittest.TestCase):
    def setUp(self):
        self.curve = lab.Curve(11, 1, 1)
        self.generator = (0, 1)

    def test_group_law(self):
        points = self.curve.points()
        for a in points:
            for b in points:
                self.assertTrue(self.curve.contains(self.curve.add(a, b)))
                self.assertEqual(self.curve.add(a, b), self.curve.add(b, a))
                for c in points:
                    self.assertEqual(self.curve.add(self.curve.add(a, b), c),
                                     self.curve.add(a, self.curve.add(b, c)))

    def test_identity_and_zero_control(self):
        identity = lab.check_map(self.curve, self.curve, self.generator, lambda p: p)
        self.assertEqual(identity["status"], "verified_toy_subgroup")
        zero = lab.check_map(self.curve, self.curve, self.generator, lambda p: None)
        self.assertTrue(zero["checks"]["scalar"])
        self.assertFalse(zero["checks"]["injective"])
        self.assertEqual(zero["status"], "rejected")

    def test_nonhomomorphic_permutation_rejected(self):
        points = self.curve.subgroup(self.generator)
        swap = {points[2]: points[3], points[3]: points[2]}
        result = lab.check_map(self.curve, self.curve, self.generator, lambda p: swap.get(p, p))
        self.assertTrue(result["checks"]["on_curve"])
        self.assertTrue(result["checks"]["injective"])
        self.assertFalse(result["checks"]["scalar"])
        self.assertEqual(result["status"], "rejected")

    def test_cover_formula_and_degenerate_control(self):
        cert = lab.cover_check(self.curve)
        self.assertEqual(cert["genus"], 2)
        self.assertEqual(cert["status"], "formula_checked")
        self.assertTrue(all(cert["checks"].values()))
        # E remains nonsingular while this particular degree-six C is singular.
        self.assertEqual(lab.cover_check(lab.Curve(11, 1, 0))["status"], "rejected")

    def test_demo_maintains_evidence_boundary(self):
        result = lab.demo()
        self.assertFalse(result["summary"]["demonstrated_speedup"])
        self.assertGreater(result["summary"]["verified_toy_chains"], 0)
        covers = [e for e in result["edges"] if e["family"] == "cover-pullback"]
        self.assertGreater(len(covers), 0)
        self.assertTrue(all(e["status"] == "unimplemented" for e in covers))
        edge_by_id = {e["uid"]: e for e in result["edges"]}
        for path in result["search"]["paths"]:
            self.assertIsNone(path["advantage"])
            if any(edge_by_id[e]["family"] == "cover-pullback" for e in path["edges"]):
                self.assertEqual(path["status"], "obligation_chain")
            nodes = [result["source"]] + [edge_by_id[e]["target"] for e in path["edges"]]
            self.assertEqual(len(nodes), len(set(nodes)))

    def test_chain_search_retains_distinct_routes(self):
        graph = lab.Explorer()
        nodes = [graph.add_node("toy", {"name": name}, {}) for name in "ABCD"]
        for source, target in [(0, 1), (0, 2), (1, 3), (2, 3), (3, 0)]:
            graph.add_edge(nodes[source], nodes[target], "candidate", "unimplemented", {})
        paths = graph.search(nodes[0])["paths"]
        self.assertEqual(sum(p["destination"] == nodes[3] for p in paths), 2)
        self.assertEqual(graph.search(nodes[0], include_obligations=False)["paths"], [])
        limited = graph.search(nodes[0], max_paths=1)
        self.assertTrue(limited["truncated"])
        self.assertEqual(len(limited["paths"]), 1)
        for limit in [0, 9]:
            with self.assertRaises(ValueError):
                graph.search(nodes[0], max_depth=limit)

    def test_path_cost_units_and_unknowns(self):
        edge = lambda unit, evaluation: lab.Edge("x", "a", "b", "f", "unimplemented", {},
            {"unit": unit, "construction": 2, "evaluation": evaluation, "memory": 3}, [])
        cost = lab.Explorer.path_cost([edge("ops", 1), edge("ops", 2)])
        self.assertEqual(cost["evaluation"], 3)
        self.assertEqual(cost["construction"], 4)
        self.assertEqual(cost["memory"], 3)
        self.assertIsNone(lab.Explorer.path_cost([edge("ops", None)])["evaluation"])
        self.assertEqual(lab.Explorer.path_cost([edge("ops", 1), edge("seconds", 1)])["unit"], "incomparable")

    def test_cost_charges_setup_verification_and_workload(self):
        record = {"unit": "group-ops", "workload": "fixed-toy", "setup": 20,
                  "online": 10, "verification": 2, "memory": 5}
        transfer = dict(record, setup=4, online=1, verification=1)
        dest = dict(record, setup=0, online=3, verification=1)
        score = lab.cost_assessment(record, dest, transfer, targets=2)
        self.assertEqual(score["baseline_total"], 44)
        self.assertEqual(score["transferred_total"], 16)
        self.assertEqual(score["status"], "model_estimate")
        self.assertEqual(lab.cost_assessment(record, dest, dict(transfer, workload="other"))["status"], "incomparable")
        self.assertEqual(lab.cost_assessment(record, dest, dict(transfer, unit="seconds"))["status"], "incomparable")
        self.assertEqual(lab.cost_assessment(record, None, transfer)["status"], "unknown")
        with self.assertRaises(ValueError):
            lab.cost_assessment(dict(record, online=-1), dest, transfer)

    def test_field_restrictions_and_singular_curve(self):
        for p in [4, 9, 103]:
            with self.assertRaises(ValueError):
                lab.Curve(p, 1, 1)
        with self.assertRaises(ValueError):
            lab.Curve(11, 0, 0)

    def test_verified_label_cannot_use_empty_certificate(self):
        graph = lab.Explorer()
        node = graph.add_node("toy", {}, {})
        with self.assertRaises(ValueError):
            graph.add_edge(node, node, "bad", "verified_toy_subgroup", {})

    def test_certificate_is_bound_to_endpoints(self):
        graph = lab.Explorer()
        cert = lab.check_map(self.curve, self.curve, self.generator, lambda p: p)
        order = len(self.curve.subgroup(self.generator))
        source = graph.add_node("elliptic", lab.identity(self.curve, self.generator, order, 1), {})
        other_generator = self.curve.mul(2, self.generator)
        target = graph.add_node("elliptic", lab.identity(self.curve, other_generator, order, 1), {})
        with self.assertRaises(ValueError):
            graph.add_edge(source, target, "wrong-binding", "verified_toy_subgroup", cert)


if __name__ == "__main__":
    unittest.main()

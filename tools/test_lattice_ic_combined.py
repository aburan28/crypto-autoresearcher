"""Software checks only: explicit p5/p7/p11, never the frozen F97 study."""
import copy
from itertools import product
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/"tools"))
import lattice_ic_combined as driver
Curve, Field, encode_point = driver.Curve, driver.Field, driver.encode_point
select_prime_subgroup = driver.poly.select_prime_subgroup


class Fixture(unittest.TestCase):
    def setUp(self):
        self.curve = Curve(Field(5), 2, 1)
        self.subgroup = select_prime_subgroup(self.curve)
        self.group = sorted(self.subgroup["G"], key=driver.fb._key)
        self.G = [encode_point(self.curve, point) for point in self.group]
        self.P = encode_point(self.curve, self.subgroup["P"])
        self.base = [encode_point(self.curve, self.subgroup["P"]),
                     encode_point(self.curve, self.curve.neg(self.subgroup["P"]))]


class HeightTests(Fixture):
    def test_complete_catalog_height_and_fullfield_retention(self):
        for p, coefficients in ((5, (2, 1)), (7, (0, 2)), (11, (0, 2))):
            catalog = driver.fb.auxiliary_catalog(p, (0, 1, 2, 3), target_coefficients=coefficients)
            driver.fb.check_catalog(catalog)
            for entry in catalog["entries"]:
                for fiber in entry["finite_fibers"]:
                    previous = set()
                    for W in (1, 2, p):
                        height = driver.height_cell(p, fiber, W)
                        retained = driver._check_height(height, p, fiber, W)
                        labels = {driver.fb._label(point) for point in retained}
                        self.assertLessEqual(previous, labels)
                        previous = labels
                        self.assertEqual(height, json.loads(json.dumps(height)))
                        if W == p:
                            self.assertEqual(retained, fiber["bases"]["list"])
                            self.assertTrue(height["fullfield_baseline"])

    def test_height_tamper_rejected_and_poles_retained(self):
        catalog = driver.fb.auxiliary_catalog(5, (0, 1), target_coefficients=(2, 1))
        entry = catalog["entries"][1]
        self.assertTrue(any(driver._chain_record(5, row)["pole_indices"] for row in entry["pole_paths"]))
        fiber = catalog["entries"][0]["finite_fibers"][0]
        height = driver.height_cell(5, fiber, 2)
        height["source_chains"][0]["centered_x"][0] += 1
        with self.assertRaisesRegex(ValueError, "centered chain"):
            driver._check_height(height, 5, fiber, 2)


class DensityTreeTests(Fixture):
    def test_m2_m3_m5_all_target_counts_against_ordered_tuples(self):
        suite = driver.density_suite(5, (2, 1), self.G, self.base)
        driver._check_suite(suite, 5, (2, 1), self.G, self.base)
        actual_base = [driver._point(self.curve, point) for point in self.base]
        for record in suite["density"]:
            counts = {point: 0 for point in self.group}
            for points in product(actual_base, repeat=record["m"]):
                counts[driver.poly._sum(self.curve, points)] += 1
            self.assertEqual(record["histogram"], [counts[point] for point in self.group])
        for record in suite["trees"]:
            for node_i, node in enumerate(record["nodes"]):
                counts = {}
                for points in product(actual_base, repeat=record["m"]):
                    witness = driver._tree_witness(self.curve, points)
                    value = witness["nodes"][node_i]["centered_x"]
                    counts[value] = counts.get(value, 0)+1
                self.assertEqual(dict(node["full_tuple_height_counts"]), counts)
            self.assertTrue(any(height is None for node in record["nodes"] for height, _ in node["full_tuple_height_counts"]))

    def test_tree_and_density_mutations_empty_bases_and_control_seeds(self):
        suite = driver.density_suite(5, (2, 1), self.G, [])
        driver._check_suite(suite, 5, (2, 1), self.G, [])
        self.assertTrue(all(sum(row["histogram"]) == 0 for row in suite["density"]))
        self.assertTrue(all(row["planted"]["tree"] is None for row in suite["trees"]))
        suite = driver.density_suite(5, (2, 1), self.G, self.base)
        bad = copy.deepcopy(suite)
        bad["trees"][0]["uniform_targets"][0]["count"] += 1
        with self.assertRaises(ValueError):
            driver._check_suite(bad, 5, (2, 1), self.G, self.base)
        bad = copy.deepcopy(suite)
        bad["density"][0]["histogram"][0] += 1
        with self.assertRaises(ValueError):
            driver._check_suite(bad, 5, (2, 1), self.G, self.base)
        controls = driver._controls(1729, 5, (2, 1), self.G, self.base, "softwarecheck", (2, 3, 5))
        driver._check_controls(controls, 1729, 5, (2, 1), self.G, self.base, "softwarecheck")
        controls["coordinate_relabel"]["permutation"].reverse()
        with self.assertRaises(ValueError):
            driver._check_controls(controls, 1729, 5, (2, 1), self.G, self.base, "softwarecheck")


class LatticeTests(Fixture):
    def test_actual_no_chain_lll_signed_boxes_and_checker(self):
        cell = driver.reduction_cell(5, (2, 1), self.G, self.P, 7, self.base, 0, None, self.P, 2, "no_chain_list", multiplier=1)
        driver.check_cell(cell, 5, (2, 1), self.G, self.P, 7, self.base, 0, None, self.P, 2, "no_chain_list", multiplier=1)
        self.assertEqual(cell["boxes"], [[-1, 0, 1], [-1, 0, 1]])
        self.assertEqual(cell["lattice"]["weight_bounds"], [2, 2])
        self.assertEqual(cell["reduction"]["cost"]["counter"]["operations"]["lll.fpylll_call"], 1)
        self.assertGreater(cell["setup_cost"]["resource"]["peak_rss_bytes"], 0)
        self.assertEqual(cell, json.loads(json.dumps(cell)))
        for field in ("boxes", "norm", "row", "rank"):
            bad = copy.deepcopy(cell)
            if field == "boxes":
                bad["boxes"][0] = [0, 1]
            elif field == "norm":
                bad["reduction"]["vectors"][0]["strict_margin"] += 1
            elif field == "row":
                bad["lattice"]["weighted_rows"][0][0] += 1
            else:
                bad["candidate_rank"]["marginal_new_rank"] += 1
            with self.assertRaises(ValueError):
                driver.check_cell(bad, 5, (2, 1), self.G, self.P, 7, self.base, 0, None, self.P, 2, "no_chain_list", multiplier=1)

    def test_actual_chain_lll_uses_all_equations_and_same_final_base(self):
        catalog = driver.fb.auxiliary_catalog(5, (0, 1), target_coefficients=(2, 1))
        count = 0
        for entry in catalog["entries"]:
            for fiber in entry["finite_fibers"]:
                height = driver.height_cell(5, fiber, 5)
                base = height["base_after"]
                if not base:
                    continue
                cells = [driver.reduction_cell(5, (2, 1), self.G, self.P, 7, base, entry["d"], fiber["B"], self.P, 5, arm, multiplier=1) for arm in driver.ARMS]
                for arm, cell in zip(driver.ARMS, cells):
                    driver.check_cell(cell, 5, (2, 1), self.G, self.P, 7, base, entry["d"], fiber["B"], self.P, 5, arm, multiplier=1)
                    self.assertEqual(cell["context"]["allowed_base"], base)
                    self.assertEqual(cell["boxes"], [list(range(-4, 5))]*len(cell["variables"]))
                self.assertEqual(len(cells[0]["source_equations"]), 1+2*(entry["d"]+1))
                self.assertEqual(len(cells[0]["variables"]), 2*(entry["d"]+1))
                self.assertEqual(len(cells[1]["variables"]), 2)
                count += 1
        self.assertGreater(count, 0)

    def test_positive_dimension_and_cap_refusal_without_fallback(self):
        control = driver.positive_dimension_control(5, (2, 1), self.G, self.P)
        driver._check_positive(control, 5, (2, 1), self.G, self.P)
        self.assertEqual(control["original_ideal"]["dimension"], 1)
        self.assertFalse(control["extraction"]["finite_system_success"])
        sp, _ = driver.poly.dependencies()
        x = sp.Symbol("x")
        lattice = driver.poly.build_shift_lattice([x], (x,), 5, (2**17000,), 1, 0, "dense")
        reduced = driver.poly.reduce_and_certify(lattice)
        driver.poly.check_lattice(lattice)
        driver.poly.check_reduction(lattice, reduced)
        self.assertEqual(reduced["status"], "bounded_instrument_stop")
        self.assertNotIn("lll.fpylll_call", reduced["cost"]["counter"]["operations"])
        self.assertGreater(len(str(lattice["gram_determinant"])), 4300)
        self.assertEqual(lattice, json.loads(json.dumps(lattice, sort_keys=True)))

    def test_genuine_extraction_auxiliary_rational_chain_and_wrong_sign_rejection(self):
        # Supply invented integer equations to exercise verification itself,
        # without calling these planted equations an LLL-produced relation.
        sp, _ = driver.poly.dependencies()
        catalog = driver.fb.auxiliary_catalog(5, (0, 1), target_coefficients=(2, 1))
        witnessed = 0
        for entry in catalog["entries"]:
            for fiber in entry["finite_fibers"]:
                base_encoded = fiber["bases"]["list"]
                if not base_encoded:
                    continue
                left = driver._point(self.curve, base_encoded[0])
                target = self.curve.add(left, left)
                if target is None:
                    continue
                target_encoded = encode_point(self.curve, target)
                variables, original, first, chains = driver.build_system(5, (2, 1), entry["d"], fiber["B"], target_encoded, base_encoded, 5, "chain")
                path = next(row for row in fiber["membership_paths"] if row["target"] == base_encoded[0])
                root = [driver._center(x[0], 5) for x in path["x"]]*2
                context = {"curve": self.curve, "G": self.group, "target": target,
                           "allowed_base": [driver._point(self.curve, point) for point in base_encoded],
                           "source_equations": original, "coordinate_sources": first, "auxiliary_chains": chains}
                equations = [x-value for x, value in zip(variables, root)]
                extracted = driver.poly.extract_and_verify(equations, variables, [list(range(-4, 5))]*len(variables), context)
                driver.poly.check_extraction(extracted, equations, variables, [list(range(-4, 5))]*len(variables), context)
                self.assertEqual(extracted["valid_root_count"], 1)
                wrong = dict(context, allowed_base=[])
                refused = driver.poly.verify_root(root, variables, [list(range(-4, 5))]*len(variables), wrong)
                self.assertFalse(refused["accepted"])
                wrong_chains = copy.deepcopy(chains)
                wrong_chains[0]["image_point"] = None
                refused = driver.poly.verify_root(root, variables, [list(range(-4, 5))]*len(variables), dict(context, auxiliary_chains=wrong_chains))
                self.assertFalse(refused["accepted"])
                witnessed += 1
        self.assertGreater(witnessed, 0)

    def test_public_known_affine_rank_no_hidden_logs(self):
        # Base P,2P,3P in the software order7 group; only ±P is public for
        # identity action. P+P=2P gives one independent affine relation.
        P = self.subgroup["P"]
        Q = self.curve.mul(2, P)
        base = [self.P, encode_point(self.curve, Q)]
        target = encode_point(self.curve, Q)
        decompositions = [[self.P, self.P]]
        rank = driver._public_rank(5, (2, 1), self.G, base, target, decompositions, self.P, 7, 1)
        driver._check_public_rank(rank, 5, (2, 1), self.G, base, target, decompositions, self.P, 7, 1)
        self.assertEqual(rank["marginal_new_rank"], 1)
        self.assertTrue(rank["target_base_alias"])
        self.assertEqual(rank["known_rank"], 1)
        zero = driver._public_rank(5, (2, 1), self.G, self.base, None, [self.base], self.P, 7, 1)
        driver._check_public_rank(zero, 5, (2, 1), self.G, self.base, None, [self.base], self.P, 7, 1)
        self.assertEqual(zero["marginal_new_rank"], 0)
        bad = copy.deepcopy(rank)
        bad["public_known"]["points"][1]["scalar"] = 2
        with self.assertRaises(ValueError):
            driver._check_public_rank(bad, 5, (2, 1), self.G, base, target, decompositions, self.P, 7, 1)

    def test_result_checker_and_cli_do_not_launch_study(self):
        with self.assertRaises(ValueError):
            driver.check_result({})
        fake = {key: None for key in ("schema_version", "direction", "seed", "parameters", "cases", "checks", "limitations", "work_accounting", "instrument_scope", "selections")}
        fake.update(schema_version=driver.SCHEMA, direction="combined", parameters={"target": [5, 2, 1]})
        with self.assertRaisesRegex(ValueError, "frozen combined"):
            driver.check_result(fake)
        result = subprocess.run([sys.executable, str(ROOT/"tools/lattice_ic_combined.py"), "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--check", result.stdout)


if __name__ == "__main__":
    unittest.main()

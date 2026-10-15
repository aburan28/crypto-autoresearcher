"""Non-study p5/p7/p11 software fixtures; never call the frozen study runner."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"tools"))
import lattice_ic_factorbase as driver
from lattice_ic_core import Counter, Curve, Field, encode_point, select_prime_subgroup
from src.crypto_autoresearcher.index_calculus.curve import Curve as OracleCurve


class MapCatalogTests(unittest.TestCase):
    def test_expanded_map_independent_rational_formula(self):
        for p in (5, 7, 11):
            field = Field(p)
            for depth in range(4):
                mapping = driver.expanded_map(p, depth)
                self.assertEqual(mapping["degree"], 2**depth)
                for x in range(p):
                    current = x
                    for j in range(depth):
                        current = None if current is None or current == 0 else (
                            current+pow(-4, j, p)*pow(current, -1, p)) % p
                    denominator = driver._eval(field, mapping["denominator"], (x,))[0]
                    actual = None if denominator == 0 else driver._eval(
                        field, mapping["numerator"], (x,))[0]*pow(denominator, -1, p) % p
                    self.assertEqual(actual, current)

    def test_catalog_partition_poles_first_slice_and_empty_bases(self):
        catalog = driver.auxiliary_catalog(5, (0, 1, 2, 3), target_coefficients=(2, 1))
        self.assertGreater(driver.check_catalog(catalog), 0)
        self.assertTrue(catalog["target"]["admission"]["admitted"])
        entries = catalog["entries"]
        self.assertEqual([entry["d"] for entry in entries], [0, 1, 2, 3])
        self.assertTrue(any(not entry["complete_kernel"] for entry in entries))
        self.assertTrue(any(not fiber["bases"]["list"] for entry in entries for fiber in entry["finite_fibers"]))
        for entry in entries:
            self.assertEqual(entry["finite_fiber_denominator"], len(entry["finite_fibers"]))
            self.assertEqual(sum(entry["duplicate_actual_base_histogram"].values()), len(entry["finite_fibers"]))
            self.assertEqual(len(entry["kernel"])+sum(len(fiber["points"]) for fiber in entry["finite_fibers"]), entry["source_point_count"])
            self.assertEqual(entry["pole_paths"][0]["points"], [None]*(entry["d"]+1))
            for fiber in entry["finite_fibers"]:
                self.assertEqual(fiber["bases"]["list"], fiber["bases"]["expanded"])
                self.assertEqual(fiber["bases"]["list"], fiber["bases"]["chain"])
                for arm in ("list", "expanded", "chain", "p1_only"):
                    self.assertGreater(fiber["work"][arm]["operations"].get("field.mul", 0), 0)
        self.assertGreater(driver.check_catalog(json.loads(json.dumps(catalog))), 0)

    def test_independent_prime_curve_point_and_map_oracle(self):
        for p in (5, 7, 11):
            field = Field(p)
            source = Curve(field, 1, 0)
            oracle = OracleCurve(p, 1, 0)
            expected = [None]+[((x,), (y,)) for x in range(p) for y in range(p)
                               if oracle.is_on_curve((x, y))]
            self.assertEqual(source.points(), expected)
            for depth in range(4):
                target_oracle = OracleCurve(p, pow(-4, depth, p), 0)
                for point in expected:
                    chain = driver._chain(field, point, depth)
                    endpoint = chain[-1]
                    self.assertTrue(target_oracle.is_on_curve(None if endpoint is None else (endpoint[0][0], endpoint[1][0])))
                    self.assertEqual(driver._expanded_point(field, point, driver.expanded_map(p, depth)), endpoint)

    def test_catalog_tampering_and_missing_fiber_rejected(self):
        original = driver.auxiliary_catalog(5, (0, 1), target_coefficients=(2, 1))
        bad = copy.deepcopy(original)
        bad["entries"][0]["finite_fibers"].pop()
        with self.assertRaises(ValueError):
            driver.check_catalog(bad)
        bad = copy.deepcopy(original)
        bad["entries"][1]["pole_paths"].pop()
        with self.assertRaises(ValueError):
            driver.check_catalog(bad)
        bad = copy.deepcopy(original)
        bad["entries"][1]["complete_kernel"] = not bad["entries"][1]["complete_kernel"]
        with self.assertRaises(ValueError):
            driver.check_catalog(bad)
        bad = copy.deepcopy(original)
        bad["entries"][0]["finite_fibers"][0]["bases"]["chain"] = [None]
        with self.assertRaises(ValueError):
            driver.check_catalog(bad)

    def test_incomplete_kernel_census_retained_and_no_target_admission(self):
        catalog = driver.auxiliary_catalog(7, (0, 1, 2, 3))
        driver.check_catalog(catalog)
        self.assertTrue(any(not entry["complete_kernel"] and entry["finite_fibers"]
                            for entry in catalog["entries"]))
        for entry in catalog["entries"]:
            for fiber in entry["finite_fibers"]:
                self.assertEqual(fiber["complete_kernel_admitted"], entry["complete_kernel"])
        catalog11 = driver.auxiliary_catalog(11, (0, 1))
        driver.check_catalog(catalog11)
        self.assertFalse(catalog11["target"]["admission"]["admitted"])
        self.assertTrue(all(fiber["bases"]["list"] == [] for entry in catalog11["entries"] for fiber in entry["finite_fibers"]))


class RankAndControlTests(unittest.TestCase):
    def setUp(self):
        self.curve = Curve(Field(5), 2, 1)
        self.subgroup = select_prime_subgroup(self.curve)
        self.group = sorted(self.subgroup["G"], key=driver._key)
        self.group_encoded = [encode_point(self.curve, point) for point in self.group]
        self.generator = self.subgroup["P"]

    def test_identity_action_complete_census_and_target_column_merge(self):
        base = [encode_point(self.curve, self.generator), encode_point(self.curve, self.curve.neg(self.generator))]
        analysis = driver.analyze_base(5, (2, 1), self.group_encoded, base, 7, 1, 1)
        self.assertGreater(driver.check_analysis(analysis, 5, (2, 1), self.group_encoded, 7, 1, 1, (2, 3)), 0)
        for panel in analysis["census"]:
            self.assertEqual(sum(row["count"] for row in panel["targets"]), len(base)**panel["m"])
            self.assertEqual(len(panel["targets"]), 7)
            for target in panel["targets"]:
                if target["R"] in base:
                    self.assertTrue(target["target_merged"])
                    self.assertEqual(target["dimensions"][1]-1, target["dimensions"][3])

    def test_nontrivial_scalar_family_invented_multiplication_endomorphism(self):
        # Invented software fixture alpha=[2] on the order7 group, rather than
        # the study's coordinate automorphism. Its nonzero orbits have length3.
        def scalar_action(curve, point, ignored):
            return curve.mul(2, point)
        base = [encode_point(self.curve, self.generator)]
        with patch.object(driver, "_alpha", scalar_action):
            analysis = driver.analyze_base(5, (2, 1), self.group_encoded, base, 7, 1, 2)
            driver.check_analysis(analysis, 5, (2, 1), self.group_encoded, 7, 1, 2, (2, 3))
            self.assertEqual((analysis["M"], analysis["U"]), (3, 1))
            for panel in analysis["census"]:
                for target in panel["targets"]:
                    # Signed alpha=[2] orbit of public P covers this invented
                    # order7 group. Formal dimensions are already public.
                    self.assertEqual(target["marginal_new_rank"], 0)
                    self.assertTrue(all(value == 0 for value in target["new_constraint_rank_increments"]))
                    for family in target["transformed_families"]:
                        self.assertEqual(len(family["legs"]), 3)
                        self.assertLessEqual(family["ranks"][1], 1)
                        self.assertLessEqual(family["ranks"][3], 1)
                        self.assertEqual(family["marginal_new_rank"], 0)
            self.assertTrue(any(target["ranks"][3] > 0 for panel in analysis["census"] for target in panel["targets"]))
            bad = copy.deepcopy(analysis)
            target = next(row for panel in bad["census"] for row in panel["targets"] if row["count"])
            target["rows"][1][0][-1] = (target["rows"][1][0][-1]+1) % 7
            with self.assertRaises(ValueError):
                driver.check_analysis(bad, 5, (2, 1), self.group_encoded, 7, 1, 2, (2, 3))
            bad = copy.deepcopy(analysis)
            bad["public_known"]["points"][1]["scalar"] = 3
            with self.assertRaisesRegex(ValueError, "public known-log"):
                driver.check_analysis(bad, 5, (2, 1), self.group_encoded, 7, 1, 2, (2, 3))
            bad = copy.deepcopy(analysis)
            target = next(row for panel in bad["census"] for row in panel["targets"] if row["count"])
            target["public_normalized_rows"][0][-1] = 1
            with self.assertRaises(ValueError):
                driver.check_analysis(bad, 5, (2, 1), self.group_encoded, 7, 1, 2, (2, 3))

    def test_affine_known_span_zero_independent_row_one_and_inconsistency(self):
        # Invented linear equations over F7: x=1 is public, y unknown.
        # This is a software linear-algebra control, not a planted curve log.
        variables = ["public-x", "unknown-y"]
        known = {"public-x": 1}
        K = driver._known_affine_constraints(variables, known, 7)
        self.assertEqual(K, [[1, 0, 6]])
        counter = driver.Counter()
        with counter.phase("rank_softwarecheck"):
            known_rank = driver._rank(K, 7, counter)
            self.assertEqual(driver._rank(K+K, 7, counter)-known_rank, 0)
            self.assertEqual(driver._rank(K+[[0, 1, 5]], 7, counter)-known_rank, 1)
        for rows in (K, K+K, K+[[0, 1, 5]], [[1, 1, 0], [2, 2, 0]]):
            self.assertEqual(driver._rank(rows, 7, counter), driver._independent_rank(rows, 7))
        normalized, unknown = driver._normalized_rows([[1, 0], [0, 1]], variables, known, 7)
        self.assertEqual((normalized, unknown), ([[0, 1], [1, 0]], [1]))
        # First row 0+1=0 would be invalid affine evidence, not useful rank.
        self.assertGreater(driver._independent_rank([normalized[0]], 7),
                           driver._independent_rank([normalized[0][:-1]], 7))
        snapshot = counter.snapshot()
        self.assertGreater(snapshot["process_peak_rss_bytes"], 0)
        self.assertGreater(snapshot["phase_rss"]["rank_softwarecheck"]["process_highwater_end_bytes"], 0)
        self.assertGreater(snapshot["operations"]["rank.modular_inverse"], 0)

    def test_nonstudy_quadratic_control_is_json_stable(self):
        # Different curve/ell than the frozen rank2 panel, not that study cell.
        control = driver.torsion_line_control(5, (1, 1), 1, 1, 2, 1)
        self.assertEqual(control, json.loads(json.dumps(control)))
        driver._check_lines(control)

    def test_empty_base_all_zero_cells_and_no_phantom_rank(self):
        result = driver.analyze_base(5, (2, 1), self.group_encoded, [], 7, 1, 1)
        driver.check_analysis(result, 5, (2, 1), self.group_encoded, 7, 1, 1, (2, 3))
        self.assertEqual((result["M"], result["U"]), (0, 0))
        for panel in result["census"]:
            self.assertEqual(panel["completed_tuple_total"], 0)
            self.assertEqual(len(panel["targets"]), 7)
            self.assertTrue(all(row["count"] == 0 and row["ranks"] == [0, 0, 0, 0] for row in panel["targets"]))

    def test_subgroup_action_and_invented_nonstable_two_torsion_lines(self):
        certificate = driver.action_certificate(self.curve, self.group, 7, self.generator, 1)
        self.assertTrue(certificate["admitted"])
        self.assertEqual(certificate["lambda"], 1)
        # Non-study prime5, y²=x³+x, alpha=(-x,2y), order2 lines; not the F25 panel.
        lines = driver.torsion_line_control(5, None, 1, 0, 2, -1, y_multiplier=2)
        self.assertEqual(len(lines["lines"]), 3)
        self.assertTrue(any(not line["stable"] for line in lines["lines"]))
        driver._check_lines(lines)
        bad = copy.deepcopy(lines)
        moved = next(line for line in bad["lines"] if not line["stable"])
        moved["lambda"] = 1
        with self.assertRaises(ValueError):
            driver._check_lines(bad)

    def test_opaque_generic_control_and_tamper(self):
        base = self.group_encoded[1:3]
        control = driver._generic_control(5, (2, 1), self.group_encoded, base, 23, (2, 3))
        driver._check_generic(control, 5, (2, 1), self.group_encoded, base, (2, 3))
        self.assertEqual(len(control["addition_table"]), 49)
        self.assertEqual(control["work"]["operations"]["generic.tuple_attempt"], 2**2+2**3)
        bad = copy.deepcopy(control)
        bad["addition_table"][0][2] = (bad["addition_table"][0][2]+1) % 7
        with self.assertRaises(ValueError):
            driver._check_generic(bad, 5, (2, 1), self.group_encoded, base, (2, 3))

    def test_coverage_checker_rejects_empty_or_changed_study_without_running_it(self):
        with self.assertRaises(ValueError):
            driver.check_result({})
        fake = {key: None for key in ("schema_version", "direction", "seed", "parameters", "cases",
                                    "checks", "limitations", "work_accounting", "instrument_scope")}
        fake.update(schema_version=driver.SCHEMA, direction="factorbase", parameters={"target": [5, 2, 1]})
        with self.assertRaisesRegex(ValueError, "frozen parameters"):
            driver.check_result(fake)

    def test_cli_help_has_no_study_execution(self):
        result = subprocess.run([sys.executable, str(ROOT/"tools/lattice_ic_factorbase.py"), "--help"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--check", result.stdout)


if __name__ == "__main__":
    unittest.main()

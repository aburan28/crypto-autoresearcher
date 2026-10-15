"""Non-study software checks only: p5/p7/p11 and invented polynomials."""
import copy
import io
import json
import sys
from contextlib import redirect_stdout
from itertools import product
from pathlib import Path
import unittest
from unittest.mock import patch

import sympy as sp

from tools import lattice_ic_polynomial as m


class IntegerLatticeSoftwareTests(unittest.TestCase):
    def setUp(self):
        self.x, self.y = sp.symbols("x y")

    def test_exact_dependencies(self):
        sympy, fpylll = m.dependencies()
        self.assertEqual(sympy.__version__, "1.14.0")
        self.assertEqual(fpylll.__version__, "0.6.4")
        with patch.object(sympy, "__version__", "invented-wrong-version"):
            with self.assertRaises(m.InstrumentStop):
                m.dependencies()

    def test_nonprimitive_dependent_rows_keep_full_integer_span(self):
        H, to_original, from_original = m._integer_row_hnf([[2, 0], [3, 0]], m.Counter())
        self.assertEqual(H, [[1, 0]])
        self.assertEqual(m._matmul(to_original, [[2, 0], [3, 0]]), H)
        self.assertEqual(m._matmul(from_original, H), [[2, 0], [3, 0]])

    def test_weighted_dense_system_and_two_way_hnf(self):
        lattice = m.build_shift_lattice([self.x-self.y, self.x+self.y-1], (self.x, self.y), 7, (2, 3), 1, 1, "dense")
        self.assertEqual(len(lattice["shifts"]), 9)
        self.assertEqual(m._matmul(lattice["membership"]["basis_from_rows"], lattice["weighted_rows"]), lattice["weighted_basis"])
        self.assertEqual(m._matmul(lattice["membership"]["rows_from_basis"], lattice["weighted_basis"]), lattice["weighted_rows"])
        self.assertGreater(lattice["gram_determinant"], 0)
        m.check_lattice(lattice)

    def test_sparse_finite_union_uses_actual_cancelled_support(self):
        lattice = m.build_shift_lattice([self.x-self.y], (self.x, self.y), 7, (2, 2), 2, 0, "sparse")
        self.assertEqual({tuple(e) for e in lattice["target_support_K"]}, {(0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2)})
        K = {tuple(e) for e in lattice["target_support_K"]}
        for row in lattice["shifts"]:
            power = sp.Poly((self.x-self.y)**row["b"][0], self.x, self.y)
            self.assertTrue(all(tuple(a+b for a, b in zip(row["a"], e)) in K for e, c in power.terms() if c))
        self.assertEqual(lattice["dimensions"]["n"], lattice["dimensions"]["D"])
        m.check_lattice(lattice)
        reduced = m.reduce_and_certify(lattice)
        m.check_reduction(lattice, reduced)

    def test_actual_lll_unimodularity_and_strict_certificate(self):
        lattice = m.build_shift_lattice([self.x-1], (self.x,), 11, (2,), 1, 1, "dense")
        reduced = m.reduce_and_certify(lattice)
        self.assertIn(reduced["status"], ("measured", "zero_yield"))
        self.assertEqual(abs(reduced["transform_determinant"]), 1)
        self.assertEqual(m._matmul(reduced["transform"], lattice["weighted_basis"]), reduced["reduced_basis"])
        for vector in reduced["vectors"]:
            self.assertEqual(vector["strict"], lattice["dimensions"]["D"]*vector["norm_squared"] < 11**2)
        self.assertTrue(reduced["certified_equations"])
        m.check_lattice(lattice)
        with patch.object(m.dependencies()[1].LLL, "reduction", side_effect=AssertionError("checker must not rerun LLL")):
            m.check_reduction(lattice, reduced)
        for key in ("strict_margin", "norm_squared"):
            bad = copy.deepcopy(reduced)
            bad["vectors"][0][key] += 1
            with self.assertRaises(ValueError):
                m.check_reduction(lattice, bad)

    def test_checker_rejects_integer_membership_and_shift_tampering(self):
        lattice = m.build_shift_lattice([self.x-self.y], (self.x, self.y), 7, (2, 2), 1, 1, "dense")
        bad = copy.deepcopy(lattice)
        bad["membership"]["basis_from_rows"][0][0] += 1
        with self.assertRaisesRegex(ValueError, "both directions"):
            m.check_lattice(bad)
        bad = copy.deepcopy(lattice)
        bad["shifts"].pop()
        with self.assertRaisesRegex(ValueError, "shift generator"):
            m.check_lattice(bad)

    def test_equal_norm_bound_is_not_strict_success(self):
        lattice = m.build_shift_lattice([sp.Integer(5)], (self.x,), 5, (1,), 1, 0, "dense")
        reduced = m.reduce_and_certify(lattice)
        self.assertEqual(reduced["vectors"][0]["strict_margin"], 0)
        self.assertFalse(reduced["vectors"][0]["strict"])
        self.assertEqual(reduced["certified_equations"], [])

    def test_actual_reducer_exception_is_instrument_stop_without_fallback(self):
        lattice = m.build_shift_lattice([self.x-1], (self.x,), 7, (2,), 1, 0, "dense")
        with patch.object(m.dependencies()[1].LLL, "reduction", side_effect=RuntimeError("invented software failure")) as reducer:
            reduced = m.reduce_and_certify(lattice)
        self.assertEqual(reducer.call_count, 1)
        self.assertEqual(reduced["status"], "bounded_instrument_stop")
        self.assertIn("invented software failure", reduced["reason"])
        m.check_reduction(lattice, reduced)
        self.assertGreater(reduced["cost"]["counter"]["phases"]["lll"]["wall_seconds"], 0)

    def test_derived_cap_records_actual_dimensions_and_gram(self):
        with patch.dict(m.CAPS, {"n": 1}):
            lattice = m.build_shift_lattice([self.x-self.y], (self.x, self.y), 7, (2, 2), 1, 1, "dense")
            self.assertIn("n", lattice["cap_exceeded"])
            self.assertGreater(lattice["gram_determinant"], 0)
            with patch.object(m.dependencies()[1].LLL, "reduction", side_effect=AssertionError("must not reduce capped input")):
                reduced = m.reduce_and_certify(lattice)
            self.assertEqual(reduced["status"], "bounded_instrument_stop")

    def test_large_exact_coefficient_cap_serializes_without_losing_certificate(self):
        lattice = m.build_shift_lattice([sp.Integer(1 << 15000)], (self.x,), 5, (1,), 1, 0, "dense")
        self.assertIn("coefficient_bits", lattice["cap_exceeded"])
        self.assertEqual(lattice["dimensions"]["candidate_coefficient_bits"], 15001)
        restored = json.loads(json.dumps(lattice))
        m.check_lattice(restored)
        self.assertEqual(m.reduce_and_certify(restored)["status"], "bounded_instrument_stop")
        large_gram = m.build_shift_lattice([self.x], (self.x,), 5, (1 << 10000,), 1, 0, "dense")
        self.assertEqual(large_gram["gram_determinant"], 25*(1 << 20000))
        self.assertGreater(len(str(large_gram["gram_determinant"])), 4300)
        m.check_lattice(json.loads(json.dumps(large_gram)))


class ExtractionSoftwareTests(unittest.TestCase):
    def setUp(self):
        self.x, self.y = sp.symbols("x y")
        self.curve = m.Curve(m.Field(7), 1, 1)
        self.point = next(point for point in self.curve.points() if point is not None)
        self.context = {"curve": self.curve, "G": self.curve.points(), "target": self.point,
                        "source_equations": [self.x-self.point[0][0]]}

    def test_exact_dimension_rejects_coefficient_independence(self):
        equations = [self.x-self.y, self.x*(self.x-self.y)]
        cert = m.ideal_certificate(equations, (self.x, self.y))
        self.assertEqual(cert["dimension"], 1)
        result = m.extract_and_verify(equations, (self.x, self.y), [range(2), range(2)], self.context)
        self.assertEqual(result["status"], "zero_yield")
        self.assertEqual(result["extracted_roots"], [])

    def test_triangular_integer_roots_no_box_fallback(self):
        roots, trace = m._triangular_integer_roots([self.x**2-1, self.y-self.x], (self.x, self.y), [[-1, 0, 1], [-1, 0, 1]], m.Counter())
        self.assertEqual(roots, [[-1, -1], [1, 1]])
        self.assertTrue(trace)
        roots, trace = m._triangular_integer_roots([2*self.x-1], (self.x,), [range(-2, 3)], m.Counter())
        self.assertEqual(roots, [])
        self.assertEqual(trace[0]["rational_roots"], [["1/2", 1]])
        roots, _ = m._triangular_integer_roots([self.x**2-2], (self.x,), [range(-2, 3)], m.Counter())
        self.assertEqual(roots, [])

    def test_zero_dimensional_extraction_checks_original_point(self):
        target_x = self.point[0][0]
        result = m.extract_and_verify([self.x-target_x], (self.x,), [range(7)], self.context)
        self.assertTrue(result["ideal"]["zero_dimensional"])
        self.assertTrue(result["finite_system_success"])
        self.assertEqual(result["valid_root_count"], 1)
        self.assertEqual(result["verification"][0]["witnesses"][0]["points"], [m.encode_point(self.curve, self.point)])
        m.check_extraction(result, [self.x-target_x], (self.x,), [range(7)], self.context)
        bad = copy.deepcopy(result)
        bad["verification"][0]["witnesses"][0]["points"][0][1][0] += 1
        with self.assertRaises(ValueError):
            m.check_extraction(bad, [self.x-target_x], (self.x,), [range(7)], self.context)

    def test_nonrational_y_and_actual_base_rejections(self):
        bad_x = next(x for x in range(7) if not any(point is not None and point[0] == (x,) for point in self.curve.points()))
        context = dict(self.context, source_equations=[])
        result = m.verify_root([bad_x], (self.x,), [range(7)], context)
        self.assertFalse(result["accepted"])
        self.assertEqual(result["reason"], "no_rational_y")
        context = dict(self.context, allowed_base=[])
        result = m.verify_root([self.point[0][0]], (self.x,), [range(7)], context)
        self.assertEqual(result["reason"], "outside_actual_base")

    def test_separate_box_oracle_and_signed_integer_boxes(self):
        roots, _ = m._triangular_integer_roots([self.x+1], (self.x,), [range(-2, 3)], m.Counter())
        self.assertEqual(roots, [[-1]])
        oracle = m.exhaustive_box_oracle(self.context["source_equations"], (self.x,), [range(7)], self.context)
        self.assertEqual(oracle["tested"], 7)
        self.assertEqual(oracle["valid_root_count"], 1)
        self.assertIn("not_lattice_extraction", oracle["role"])

    def test_actual_auxiliary_y_chain_and_wrong_terminal_rejection(self):
        curve = m.Curve(m.Field(7), 1, 0)
        point = ((1,), (3,))
        self.assertTrue(curve.is_on_curve(point))
        context = {"curve": curve, "G": curve.points(), "target": point,
                   "source_equations": [self.x*self.y-self.x**2-1], "coordinate_sources": [0],
                   "auxiliary_chains": [{"A": 1, "x_indices": [0, 1], "image_point": [[2], [0]]}]}
        result = m.verify_root([1, 2], (self.x, self.y), [range(3), range(3)], context)
        self.assertTrue(result["accepted"])
        self.assertEqual(len(result["witnesses"][0]["auxiliary_paths"][0]), 2)
        context["auxiliary_chains"][0]["image_point"] = [[3], [0]]
        result = m.verify_root([1, 2], (self.x, self.y), [range(3), range(3)], context)
        self.assertEqual(result["reason"], "no_auxiliary_rational_chain")


class GroupAndCellSoftwareTests(unittest.TestCase):
    def setUp(self):
        self.curve = m.Curve(m.Field(7), 1, 1)
        self.admitted = m.select_prime_subgroup(self.curve)
        self.assertTrue(self.admitted["admitted"])

    def test_s3_and_resultant_s4_follow_actual_point_sum(self):
        base = [point for point in self.admitted["G"] if point is not None]
        for length in (2, 3):
            variables = sp.symbols("x1:"+str(length+1))
            polynomials = {}
            for points in product(base, repeat=length):
                target = m._sum(self.curve, points)
                if target is None:
                    continue
                X = target[0][0]
                if X not in polynomials:
                    polynomials[X] = m.summation_polynomial(length, variables, X, 1, 1, 7)
                self.assertEqual(int(polynomials[X].subs(dict(zip(variables, [point[0][0] for point in points])))) % 7, 0)

    def test_generic_coordinate_and_adverse_controls_use_actual_witnesses(self):
        group = self.admitted["G"]
        base = m._window(self.admitted, 2)
        generic = m._generic_density(self.curve, group, base, 3, 1729)
        density = m.group_density(self.curve, group, base, 3)
        self.assertEqual(generic["histogram_in_point_order"], density["histogram"])
        labels = m._coordinate_compatibility(7, 1, 1, [m.encode_point(self.curve, point) for point in base], [1, 2, 3, 4, 5, 6, 0])
        self.assertEqual(labels["affine_trials"]+labels["identity_target_branches"], len(base)**2)
        adverse = m._adverse_lifts(7, 1, 1, m.encode_point(self.curve, self.admitted["P"]), [m.encode_point(self.curve, point) for point in group])
        for witness in adverse["repeated_nonrational_roots"]:
            self.assertEqual(pow(witness["rhs"], 3, 7), 6)
            self.assertEqual(witness["residual"], 0)
        for witness in adverse["outside_G_roots"]:
            self.assertEqual(witness["residual"], 0)

    def test_all_target_dp_matches_exhaustive_point_tuples_and_tree(self):
        base = m._window(self.admitted, 2)
        group = self.admitted["G"]
        for length in (2, 3, 5):
            density = m.group_density(self.curve, group, base, length)
            truth = [0]*len(group)
            for points in product(base, repeat=length):
                truth[group.index(m._sum(self.curve, points))] += 1
            self.assertEqual(density["histogram"], truth)
            self.assertEqual(sum(truth), len(base)**length)
            m._check_cost(density["cost"])
            if length == 5:
                for target, witness in zip(density["targets"], density["witnesses"]):
                    if witness is not None:
                        points = [m._decode_point(self.curve, point) for point in witness]
                        tree = m.addition_tree(self.curve, points)
                        self.assertEqual(tree["sum"], target)
                        self.assertEqual(len(tree["nodes"]), 4)

    def test_public_span_zero_and_independent_fixed_target_rank_one(self):
        P, r = self.admitted["P"], self.admitted["r"]
        base = [point for point in self.admitted["G"] if point is not None]
        zero = m.relation_rank(self.curve, base, None, [(P, self.curve.neg(P))], P, r)
        self.assertEqual(zero["formal_raw_rank"], 1)
        self.assertEqual(zero["marginal_new_rank"], 0)
        Q = self.curve.mul(2, P)
        one = m.relation_rank(self.curve, base, Q, [(P, P), (P, P)], P, r)
        self.assertEqual(one["marginal_new_rank"], 1)
        self.assertTrue(one["target_base_alias"])
        self.assertEqual(one["dimensions"]["raw_unknowns"], len(base))
        self.assertTrue(one["affine_consistent"])
        self.assertEqual(len(one["public_known_witnesses"]), 1)

    def test_cold_nonstudy_cell_and_checker_no_lll_replay(self):
        Q = self.curve.mul(2, self.admitted["P"])
        inputs = {"p": 7, "A": 1, "B": 1, "W": 2, "m": 2, "target": m.encode_point(self.curve, Q),
                  "t": 1, "L": 0, "arm": "dense", "slice_x2": None}
        cell = m.reduction_cell(7, 1, 1, 2, 2, inputs["target"], 1, 0, "dense")
        cell = json.loads(json.dumps(cell))
        self.assertGreater(cell["oracle"]["valid_root_count"], 0)
        self.assertEqual(cell["extraction"]["valid_root_count"], 0)
        self.assertEqual(m._cell_status(cell), "zero_yield")
        with patch.object(m.dependencies()[1].LLL, "reduction", side_effect=AssertionError("no checker LLL replay")):
            m.check_cell(cell, inputs)
        bad = copy.deepcopy(cell)
        bad["candidate_rank"]["marginal_new_rank"] += 1
        with self.assertRaises(ValueError):
            m.check_cell(bad, inputs)

    def test_univariate_slice_and_positive_dimension_controls(self):
        Q = self.curve.mul(2, self.admitted["P"])
        target = m.encode_point(self.curve, Q)
        cell = m.reduction_cell(7, 1, 1, 2, 2, target, 1, 0, "dense", 0)
        inputs = {"p": 7, "A": 1, "B": 1, "W": 2, "m": 2, "target": target,
                  "t": 1, "L": 0, "arm": "dense", "slice_x2": 0}
        m.check_cell(cell, inputs)
        self.assertIsNotNone(cell["univariate"])
        control = m._positive_dimension_control(7)
        self.assertEqual(control["ideal"]["dimension"], 1)
        self.assertFalse(control["finite_system_success"])
        m.check_lattice(control["lattice"])
        m.check_reduction(control["lattice"], control["reduction"])


class EnvelopeSoftwareTests(unittest.TestCase):
    def test_shared_status_and_actual_rss(self):
        for status in m.STATUSES:
            self.assertEqual(m._case("toy", "toy", {}, {}, {}, {}, status=status)["status"], status)
        with self.assertRaises(ValueError):
            m._case("toy", "toy", {}, {}, {}, {}, status="incomplete_rank")
        record = m.rss("software fixture")
        m._check_rss(record)
        bad = dict(record, peak_rss_bytes=record["peak_rss_bytes"]+1)
        with self.assertRaises(ValueError):
            m._check_rss(bad)

    def test_deleted_controls_rejected_before_study_arithmetic(self):
        scope = {"protocol": "prospective-protocols.json/polynomial", "controls": list(m.CONTROL_NAMES),
                 "expanded_reduction_m": [2, 3], "density_m": [2, 3, 5], "expanded_m5": False,
                 "scientific_claim": False, "checker_is_independent_review": False}
        payload = {"schema_version": 1, "direction": "polynomial", "parameters": m.FIXTURE,
                   "instrument_scope": scope, "cases": [m._case("controls", "controls", {}, {}, {}, {})]}
        with patch.object(m, "Field", side_effect=AssertionError("no study field")):
            with self.assertRaisesRegex(ValueError, "controls"):
                m.check_result(payload)

    def test_cli_mocked_writer_and_separate_checker_cost(self):
        sentinel = {"softwarecheck_only": True}
        with patch.object(m, "run_experiment", return_value=sentinel) as experiment:
            with patch.object(m, "write_artifacts") as writer:
                self.assertEqual(m.main(["--seed", "9", "--output-dir", "/tmp/polynomial-mocked-no-write"]), 0)
        experiment.assert_called_once_with(9)
        self.assertEqual(writer.call_args.args[:3], (sentinel, Path("/tmp/polynomial-mocked-no-write"), 9))
        output = io.StringIO()
        with patch.object(Path, "read_text", return_value="{}"):
            with patch.object(m, "check_result", return_value=True):
                with patch.object(m, "run_experiment", side_effect=AssertionError("no study launch")):
                    with redirect_stdout(output):
                        self.assertEqual(m.main(["--check", "/tmp/polynomial-mocked-no-read"]), 0)
        record = json.loads(output.getvalue())
        self.assertFalse(record["lll_rerun"])
        m._check_rss(record["resource"])

    def test_cli_exact_integer_gate_precedes_json_parsing(self):
        large = 1 << 15000
        prior_limit = sys.get_int_max_str_digits()
        try:
            sys.set_int_max_str_digits(0)
            raw = json.dumps({"softwarecheck_large_integer": large})
            sys.set_int_max_str_digits(640)
            with patch.object(Path, "read_text", return_value=raw):
                with patch.object(m, "check_result", return_value=True) as checker:
                    with redirect_stdout(io.StringIO()):
                        self.assertEqual(m.main(["--check", "/tmp/polynomial-mocked-no-read"]), 0)
            self.assertEqual(checker.call_args.args[0]["softwarecheck_large_integer"], large)
        finally:
            sys.set_int_max_str_digits(prior_limit)


if __name__ == "__main__":
    unittest.main()

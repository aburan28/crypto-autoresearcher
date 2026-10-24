"""Mathematical cross-checks and regressions for the research controls."""

from dataclasses import fields
from random import Random
import unittest

from crypto_autoresearcher.index_calculus.representation_arithmetic import (Curve, IDENTITY, Lift, ordinary_curve, solve_mod)
from crypto_autoresearcher.index_calculus.representation_controls import (
    PublicInstance, audit_additive_map, benchmark_one_model, bsgs, check_dependencies, check_map,
    cm_traces_j1728, collect_relations, constraint_benchmark, factor_base,
    recover_by_digit, residual_experiment,
)


class ArithmeticTests(unittest.TestCase):
    def test_projective_against_independent_affine_for_every_small_pair(self):
        # Exhausts identity, inverse, doubling and distinct-point cases, using
        # an independently implemented affine group law as the reference.
        for curve in (ordinary_curve(11), Curve(11, 1, 5)):
            lift = Lift(curve, 3)
            for left in curve.points:
                for right in curve.points:
                    total = lift.add(lift.point(left), lift.point(right))
                    self.assertEqual(lift.reduce(total), curve.add(left, right))

    def test_lift_associativity_including_kernel_points(self):
        rng = Random(11)
        curve = ordinary_curve(37)
        for precision in (2, 3, 4):
            lift = Lift(curve, precision, curve_shift=2, x_shift=1)
            point = lift.point(curve.generator)
            for _ in range(16):
                left, middle, right = [lift.mul(rng.randrange(10000), point)
                                       for _ in range(3)]
                self.assertTrue(lift.equal(
                    lift.add(lift.add(left, middle), right),
                    lift.add(left, lift.add(middle, right))))
                self.assertTrue(lift.equal(lift.add(left, lift.neg(left)), IDENTITY))

    def test_precision_is_nested_for_points_and_group_operations(self):
        curve = ordinary_curve(37)
        for scalar in (0, 1, 12, curve.order, curve.order+3):
            low, high = Lift(curve, 2, 1, 3), Lift(curve, 4, 1, 3)
            low_result = low.mul(scalar, low.point(curve.generator))
            high_result = high.mul(scalar, high.point(curve.generator))
            self.assertTrue(low.equal(low_result, tuple(v % low.modulus for v in high_result)))

    def test_formal_log_additivity_at_all_supported_precisions(self):
        curve = ordinary_curve(37)
        for precision in (2, 3, 4):
            lift = Lift(curve, precision)
            kernel = lift.mul(curve.order, lift.point(curve.generator))
            for a, b in ((1, 2), (-3, 9), (37, 42)):
                left, right = lift.mul(a, kernel), lift.mul(b, kernel)
                self.assertEqual(lift.formal_log(lift.add(left, right)),
                                 (lift.formal_log(left)+lift.formal_log(right)) % lift.modulus)

    def test_public_torsion_split_preserves_group_and_erases_signal(self):
        curve = ordinary_curve(11)
        lift = Lift(curve, 4)
        for left in curve.points:
            split = lift.torsion_point(left)
            self.assertEqual(lift.reduce(split), left)
            self.assertTrue(lift.equal(lift.mul(curve.order, split), IDENTITY))
            self.assertEqual(lift.first_digit(left, torsion=True), 0)
            for right in curve.points:
                self.assertTrue(lift.equal(lift.torsion_point(curve.add(left, right)),
                                           lift.add(split, lift.torsion_point(right))))

    def test_invalid_domains_fail_explicitly(self):
        with self.assertRaises(ValueError):
            Curve(15, 2, 3)
        with self.assertRaises(ValueError):
            Curve(11, 0, 0)
        with self.assertRaises(ValueError):
            Lift(ordinary_curve(11), 5)
        lift = Lift(ordinary_curve(11))
        with self.assertRaises(ArithmeticError):
            lift.equal((0, 0, 0), (0, 0, 0))
        with self.assertRaises(ValueError):
            lift.formal_log(lift.point(lift.curve.generator))

    def test_elimination_rank_inconsistency_and_free_variables(self):
        answer, rank = solve_mod([[1, 2], [3, 4]], [5, 6], 11)
        self.assertEqual(rank, 2)
        self.assertEqual([(answer[0]+2*answer[1]) % 11,
                          (3*answer[0]+4*answer[1]) % 11], [5, 6])
        self.assertEqual(solve_mod([[1, 2], [2, 4]], [5, 0], 11), (None, 1))
        answer, rank = solve_mod([[1, 2]], [5], 11)
        self.assertEqual((answer, rank), ([5, 0], 1))


class ResearchControlTests(unittest.TestCase):
    def test_existing_index_calculus_arithmetic_agrees_on_every_small_pair(self):
        from crypto_autoresearcher.index_calculus.curve import Curve as IndexCurve

        for curve in (ordinary_curve(11), ordinary_curve(37)):
            reference = IndexCurve(curve.p, curve.a, curve.b, curve.order)
            for left in curve.points:
                self.assertEqual(curve.mul(12, left), reference.mul(12, left))
                for right in curve.points:
                    self.assertEqual(curve.add(left, right), reference.add(left, right))

    def test_supplied_maps_distinguish_zero_signal_from_bad_algebra(self):
        curve = ordinary_curve()
        zero = audit_additive_map(curve, lambda point: 0, samples=4)
        self.assertTrue(zero["sampled_algebra_passes"])
        self.assertFalse(zero["nonzero_image_observed"])
        bad = audit_additive_map(curve, lambda point: point[0] if point else 0, samples=4)
        self.assertGreater(bad["map_scalar_failures"], 0)
        self.assertTrue(bad["nonzero_additive_map_structurally_impossible"])
        self.assertFalse(bad["construction_cost_verified"])
        self.assertFalse(bad["secret_independence_verified"])
        values = iter([0, 1]*1000)
        unstable = audit_additive_map(curve, lambda point: next(values), samples=4)
        self.assertGreater(unstable["map_repeated_value_failures"], 0)
        self.assertFalse(unstable["sampled_algebra_passes"])
        with self.assertRaises(TypeError):
            audit_additive_map(curve, lambda point: "not a field element", samples=1)

    def test_candidate_api_has_no_hidden_label(self):
        self.assertEqual([field.name for field in fields(PublicInstance)],
                         ["curve", "base", "target", "order"])
        self.assertFalse(check_dependencies(("unknown_scalar",))["passed"])
        self.assertTrue(check_dependencies(("public_curve", "public_points"))["passed"])
        curve = ordinary_curve(11)
        with self.assertRaises(ValueError):
            PublicInstance(curve, curve.generator, None, curve.order+1)
        with self.assertRaises(ValueError):
            PublicInstance(curve, None, curve.generator, curve.order)

    def test_anomalous_positive_and_ordinary_structural_negative(self):
        anomalous = Curve(1019, 373, 837)
        ordinary = ordinary_curve()
        for curve in (anomalous, ordinary):
            diagnostic = check_map(curve, Lift(curve), False, Random(3), 12)
            if curve is anomalous:
                self.assertEqual(diagnostic["map_addition_failures"], 0)
                self.assertEqual(diagnostic["map_scalar_failures"], 0)
                for scalar in (1, 12, curve.order-1):
                    public = PublicInstance(curve, curve.generator,
                                            curve.mul(scalar, curve.generator), curve.order)
                    self.assertEqual(recover_by_digit(public), scalar)
            else:
                self.assertTrue(diagnostic["nonzero_additive_map_structurally_impossible"])
                self.assertNotEqual(diagnostic["r_times_base_image_mod_p"], 0)
                self.assertGreater(diagnostic["map_scalar_failures"], 0)

    def test_generic_baseline_for_all_small_scalars(self):
        curve = ordinary_curve(37)
        for scalar in range(curve.order):
            public = PublicInstance(curve, curve.generator,
                                    curve.mul(scalar, curve.generator), curve.order)
            self.assertEqual(bsgs(public), scalar)

    def test_isomorphisms_preserve_addition_and_invert(self):
        curve = ordinary_curve(37)
        for u in (1, 2, 3, 5):
            model = curve.scaled(u)
            inv = pow(u, -1, curve.p)
            for left in curve.points:
                right = curve.mul(7, left)
                self.assertEqual(model.transport(curve.transport(left, u), inv), left)
                self.assertEqual(curve.transport(curve.add(left, right), u),
                                 model.add(curve.transport(left, u), curve.transport(right, u)))

    def test_transport_benchmark_identical_relations(self):
        curve = ordinary_curve(101)
        rng = Random(5)
        attempts = [(rng.randrange(curve.order), rng.randrange(curve.order)) for _ in range(1500)]
        target = curve.mul(12, curve.generator)
        runs = [benchmark_one_model(curve, u, "transported", 6, 7, attempts,
                                    curve.generator, target) for u in (1, 2, 3)]
        self.assertEqual(len({run["relation_transcript_sha256"] for run in runs}), 1)
        self.assertTrue(all(run["recovery_verified_in_original_group"] for run in runs))
        self.assertTrue(all(run["recovered_scalar"] == 12 for run in runs))

    def test_collected_relations_use_public_group_arithmetic(self):
        curve = ordinary_curve(101)
        p, q = curve.generator, curve.mul(12, curve.generator)
        base = factor_base(curve, 8, "low_degree", 1)
        relations, _ = collect_relations(curve, p, q, base, 4, 24)
        self.assertEqual(len(relations), len(set(relations)))
        for a, b, i, j in relations:
            self.assertEqual(curve.add(curve.mul(a, p), curve.mul(b, q)),
                             curve.add(base[i], base[j]))

    def test_residual_per_point_fit_is_not_marked_as_attack(self):
        report = residual_experiment(seed=17, size=8, train_count=32, heldout_count=12)
        for run in report["runs"]:
            analytic = run["analytic_per_point_correction"]
            self.assertEqual(analytic["matching_residuals"], run["relations"])
            self.assertTrue(analytic["all_split_torsion_formal_signals_zero"])
            linear = run["models"][1]
            self.assertEqual(linear["heldout_accuracy"], 1.0)
            self.assertIn("not demonstrated", run["end_to_end_improvement"])
            self.assertEqual(run["precision_control"]["matching_relations"], 8)

    def test_cm_filter_retains_all_enumerated_positive_controls(self):
        for p in (101, 103, 107, 109, 127, 131):
            for a in range(1, 21):
                curve = Curve(p, a, 0)
                self.assertIn(p+1-curve.order, cm_traces_j1728(p))
        report = constraint_benchmark()
        self.assertTrue(report["positive_control_sets_identical"])
        self.assertEqual(report["lost_positive_controls"], 0)
        self.assertLess(report["filtered"]["point_counts"], report["unfiltered"]["point_counts"])


if __name__ == "__main__":
    unittest.main()

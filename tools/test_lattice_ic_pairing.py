"""Software checks only: p5/p7/p11 and invented integer-ring identities.

No call to run_experiment and no enumeration/arithmetic on study fields.
"""
import copy
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import unittest
from unittest.mock import patch

from tools import lattice_ic_pairing as m


class PairingSoftwareTests(unittest.TestCase):
    def setUp(self):
        self.f = m.Field(11, (1, 0))
        self.c = m.Curve(self.f, 1, 0)
        prime = m.Curve(m.Field(11), 1, 0)
        subgroup = m.select_prime_subgroup(prime, r=3, min_prime=2)
        self.assertTrue(subgroup["admitted"])
        self.p = tuple(self.f.coerce(x[0]) for x in subgroup["P"])
        self.s = (self.f.neg(self.p[0]), self.f.mul((0, 1), self.p[1]))

    def test_weil_order_bilinearity_and_alternation(self):
        g, cert = m.weil_pairing(self.c, self.p, self.s, 3)
        self.assertNotEqual(g, self.f.one)
        self.assertEqual(self.f.pow(g, 3), self.f.one)
        m.verify_weil(self.c, self.p, self.s, 3, g, cert)
        for a in range(3):
            for b in range(3):
                h, hc = m.weil_pairing(self.c, self.c.mul(a, self.p), self.c.mul(b, self.s), 3)
                self.assertEqual(h, self.f.pow(g, a*b))
                m.verify_weil(self.c, self.c.mul(a, self.p), self.c.mul(b, self.s), 3, h, hc)
        reverse, _ = m.weil_pairing(self.c, self.s, self.p, 3)
        diagonal, _ = m.weil_pairing(self.c, self.p, self.p, 3)
        self.assertEqual(reverse, self.f.inv(g))
        self.assertEqual(diagonal, self.f.one)

    def test_miller_r3_independent_tangent_formula(self):
        # Since 2P=-P, f3 is precisely the tangent line at P.
        x, y = self.p
        slope = self.f.mul(self.f.add(self.f.mul(3, self.f.mul(x, x)), 1),
                           self.f.inv(self.f.mul(2, y)))
        checked = 0
        for at in self.c.points():
            if at is None or at[0] == x:
                continue
            expected = self.f.sub(self.f.sub(at[1], y), self.f.mul(slope, self.f.sub(at[0], x)))
            self.assertEqual(m.miller(self.c, self.p, 3, at), expected)
            checked += 1
        self.assertGreater(checked, 0)

    def test_pole_search_prefix_and_tampering(self):
        g, cert = m.weil_pairing(self.c, self.p, self.s, 3)
        self.assertIn("pole", cert["attempts"][0])
        self.assertIsNone(cert["attempts"][0]["T"])
        for mutate in (lambda c: c["attempts"].pop(0),
                       lambda c: c["attempts"][-1]["values"].__setitem__(0, [0, 0])):
            broken = copy.deepcopy(cert)
            mutate(broken)
            with self.assertRaises(ValueError):
                m.verify_weil(self.c, self.p, self.s, 3, g, broken)
        with self.assertRaises(ValueError):
            m.verify_weil(self.c, self.p, self.s, 3, self.f.one, cert)

    def test_identity_and_torsion_rejection(self):
        value, cert = m.weil_pairing(self.c, None, self.s, 3)
        self.assertEqual(value, self.f.one)
        m.verify_weil(self.c, None, self.s, 3, value, cert)
        with self.assertRaises(ValueError):
            m.weil_pairing(self.c, self.p, self.s, 2)

    def test_degree_two_covariance_and_all_pair_map(self):
        target = m.Curve(self.f, -4, 0)
        g, _ = m.weil_pairing(self.c, self.p, self.s, 3)
        pp, sp = m.isogeny(self.c, target, self.p), m.isogeny(self.c, target, self.s)
        transported, tc = m.weil_pairing(target, pp, sp, 3)
        self.assertEqual(transported, self.f.pow(g, 2))
        m.verify_weil(target, pp, sp, 3, transported, tc)
        prime = m.Curve(m.Field(7), 1, 0)
        dest = m.Curve(prime.field, -4, 0)
        pts = prime.points()
        self.assertIsNone(m.isogeny(prime, dest, None))
        self.assertIsNone(m.isogeny(prime, dest, ((0,), (0,))))
        for left in pts:
            for right in pts:
                self.assertEqual(m.isogeny(prime, dest, prime.add(left, right)),
                                 dest.add(m.isogeny(prime, dest, left), m.isogeny(prime, dest, right)))

    def test_basis_isomorphism_and_pairing(self):
        f = m.Field(7, (1, 0))
        v = m.Field(7, (2, -2))
        elements = list(f.elements())
        convert = lambda x: m.convert_basis(x, f, v)
        for x in elements:
            self.assertEqual(m.convert_basis(convert(x), v, f, "v_to_u"), x)
            for y in elements:
                self.assertEqual(convert(f.add(x, y)), v.add(convert(x), convert(y)))
                self.assertEqual(convert(f.mul(x, y)), v.mul(convert(x), convert(y)))
        vf = m.Field(11, (2, -2))
        vc = m.Curve(vf, 1, 0)
        convert11 = lambda x: m.convert_basis(x, self.f, vf)
        vp, vs = [tuple(convert11(x) for x in p) for p in (self.p, self.s)]
        g, _ = m.weil_pairing(self.c, self.p, self.s, 3)
        vg, cert = m.weil_pairing(vc, vp, vs, 3)
        self.assertEqual(vg, convert11(g))
        m.verify_weil(vc, vp, vs, 3, vg, cert)

    def test_dlp_baselines_all_tiny_targets(self):
        g, _ = m.weil_pairing(self.c, self.p, self.s, 3)
        for a in range(3):
            target = self.f.pow(g, a)
            self.assertEqual(m.exhaustive_dlp(self.f, g, target, 3), [a])
            self.assertEqual(m.bsgs_dlp(self.f, g, target, 3)[0], [a])
        self.assertEqual(m.exhaustive_dlp(self.f, self.f.one, self.f.one, 3), [0, 1, 2])

    def test_fresh_arms_charge_direct_dependency_and_cold_cache(self):
        created, real_counter = [], m.Counter
        def new_counter():
            counter = real_counter()
            created.append(counter)
            return counter
        P, S = m.encode_point(self.c, self.p), m.encode_point(self.c, self.s)
        with patch.object(m, "Counter", side_effect=new_counter):
            arms = {name: m.pairing_arm(11, (1, 0), 1, 0, 3, P, S, name)
                    for name in ("direct", "transported", "reused_power")}
        self.assertEqual(len(created), 3)
        self.assertEqual(len({id(x) for x in created}), 3)
        for arm in arms.values():
            m.verify_pairing_arm(arm, 11, (1, 0), 1, 0, 3, P, S)
            self.assertEqual(arm["cost"]["counter"]["operations"]["curve.enumeration"], 1)
        self.assertEqual(arms["transported"]["images"], arms["reused_power"]["images"])
        direct_count = arms["direct"]["cost"]["counter"]["operations"]["miller.call"]
        self.assertGreater(direct_count, 0)
        self.assertEqual(direct_count, arms["reused_power"]["cost"]["counter"]["operations"]["miller.call"])
        self.assertEqual(arms["direct"]["images"], arms["reused_power"]["direct_dependency"]["images"])
        broken = copy.deepcopy(arms["reused_power"])
        broken["direct_dependency"] = None
        with self.assertRaisesRegex(ValueError, "direct power dependency"):
            m.verify_pairing_arm(broken, 11, (1, 0), 1, 0, 3, P, S)
        broken = copy.deepcopy(arms["direct"])
        broken["cost"]["counter"]["phases"]["target_pairings"]["operations"]["miller.call"] += 1
        with self.assertRaisesRegex(ValueError, "leaf allocated"):
            m.verify_pairing_arm(broken, 11, (1, 0), 1, 0, 3, P, S)

    def test_baseline_basis_and_method_arms_have_isolated_counters(self):
        g, _ = m.weil_pairing(self.c, self.p, self.s, 3)
        vf = m.Field(11, (2, -2))
        created, real_counter = [], m.Counter
        def new_counter():
            counter = real_counter()
            created.append(counter)
            return counter
        arms = []
        for quadratic, f, base in (((1, 0), self.f, g),
                                   ((2, -2), vf, m.convert_basis(g, self.f, vf))):
            images = [f.pow(base, a) for a in range(3)]
            for method in ("exhaustive", "bsgs"):
                with patch.object(m, "Counter", side_effect=new_counter):
                    arm = m.baseline_arm(11, quadratic, base, images, 3, method)
                m.verify_baseline_arm(arm, 11, quadratic, base, images, 3)
                self.assertEqual([x["logs"] for x in arm["records"]], [[0], [1], [2]])
                arms.append(arm)
        self.assertEqual(len({id(x) for x in created}), 4)
        for arm in arms:
            self.assertEqual(set(arm["cost"]["counter"]["phases"]), {"setup", "solve"})
            self.assertNotIn("miller.call", arm["cost"]["counter"]["operations"])

    def test_basis_conversion_cost_is_separate_leaf_component(self):
        counter = m.Counter()
        f, vf = m.Field(7, (1, 0), counter=counter), m.Field(7, (2, -2), counter=counter)
        with counter.phase("basis_conversion"):
            for element in f.elements():
                m.convert_basis(element, f, vf)
        snapshot = counter.snapshot()
        self.assertEqual(snapshot["operations"]["basis.conversion"], 49)
        self.assertEqual(snapshot["phases"]["basis_conversion"]["operations"], {"basis.conversion": 49})


class RingSoftwareTests(unittest.TestCase):
    def setUp(self):
        self.gaussian = m.QuadraticRing(1, 0, "invented Gaussian test")
        self.other = m.QuadraticRing(3, -1, "invented quadratic test")
        self.units1 = [[1, 0], [-1, 0], [0, 1], [0, -1]]
        self.units2 = [[1, 0], [-1, 0]]

    def test_integer_ring_norm_and_exact_division(self):
        for ring in (self.gaussian, self.other):
            for x in ((2, 3), (-4, 1), (1, -2)):
                for y in ((3, -1), (-2, 2), (1, 1)):
                    value = ring.mul(x, y)
                    self.assertEqual(ring.norm(value), ring.norm(x)*ring.norm(y))
                    self.assertEqual(ring.divide(value, y), x)
        self.assertIsNone(self.gaussian.divide((1, 0), (2, 0)))
        with self.assertRaises(ZeroDivisionError):
            self.gaussian.divide((1, 0), (0, 0))

    def test_prime_generator_bounds_and_inert_primes(self):
        gs, inert = m.prime_generators(self.gaussian, 7, 7)
        self.assertEqual(inert, [3, 7])
        self.assertIn({"element": [3, 0], "norm": 9, "rational_prime": 3, "type": "inert_integer"}, gs)
        self.assertIn({"element": [1, 2], "norm": 5, "rational_prime": 5, "type": "norm_prime"}, gs)
        self.assertEqual(gs, sorted(gs, key=lambda g: (g["norm"], g["element"])))
        other, inert2 = m.prime_generators(self.other, 7, 8)
        self.assertEqual(inert2, [2, 7])
        self.assertTrue(any(g["norm"] == 3 for g in other))

    def test_factorization_exact_identity_and_unit(self):
        for ring, units in ((self.gaussian, self.units1), (self.other, self.units2)):
            generators, _ = m.prime_generators(ring, 7, 8)
            for element in ((-1, 0), (3, 0), (0, 3), (4, 2), (6, -2)):
                cert = m.factor_element(ring, element, generators, units)
                self.assertTrue(m.verify_factorization(ring, cert, generators, units))
                if cert["accepted"]:
                    broken = copy.deepcopy(cert)
                    broken["unit"] = None
                    with self.assertRaises(ValueError):
                        m.verify_factorization(ring, broken, generators, units)
        with self.assertRaises(ValueError):
            m.factor_element(self.gaussian, (0, 0), [], self.units1)

    def test_smooth_norm_never_substitutes_for_element_identity(self):
        generators, _ = m.prime_generators(self.gaussian, 5, 5)
        fake = {"element": [3, 4], "norm": 25, "factors": [], "remainder": [1, 0],
                "unit": [1, 0], "accepted": True}
        with self.assertRaisesRegex(ValueError, "ELEMENT identity"):
            m.verify_factorization(self.gaussian, fake, generators, self.units1)

    def test_projected_element_identity_and_bad_factor(self):
        f, root, exponent = m.Field(7, (1, 0)), (0, 1), 16
        generators, _ = m.prime_generators(self.gaussian, 5, 5)
        for gen in generators:
            gen["projected"] = list(f.pow(self.gaussian.evaluate(gen["element"], f, root), exponent))
        cert = m.factor_element(self.gaussian, (3, 4), generators, self.units1)
        self.assertTrue(cert["accepted"])
        m._project_factorization(self.gaussian, cert, generators, self.units1, f, root, exponent)
        for mutate in (lambda c: c.__setitem__("element", [4, 3]),
                       lambda c: c.__setitem__("projected", [0, 0]),
                       lambda c: c["factors"][0].__setitem__(1, c["factors"][0][1]+1)):
            bad = copy.deepcopy(cert)
            mutate(bad)
            with self.assertRaises(ValueError):
                m.verify_factorization(self.gaussian, bad, generators, self.units1, f, root, exponent)
        bad_generators = copy.deepcopy(generators)
        index = cert["factors"][0][0]
        bad_generators[index]["projected"] = [0, 0]
        with self.assertRaisesRegex(ValueError, "bad projected factor"):
            m.verify_factorization(self.gaussian, cert, bad_generators, self.units1, f, root, exponent)

    def test_modular_solve_uses_only_rows_and_preserves_rank(self):
        unique = m.solve_relative([[2, -1], [4, -2]], 2, 7)
        self.assertEqual(unique["solution"], [1, 2])
        self.assertEqual(unique["rank"], 1)
        self.assertTrue(unique["unique"])
        incomplete = m.solve_relative([[2, -1, 0]], 3, 7)
        self.assertFalse(incomplete["unique"])
        self.assertIsNone(incomplete["solution"])
        inconsistent = m.solve_relative([[1, 0]], 2, 7)
        self.assertFalse(inconsistent["consistent"])
        self.assertIsNone(inconsistent["solution"])
        self.assertIsNone(m.solve_relative([], 0, 7)["solution"])

    def test_special_ideal_small_invented_box(self):
        result = m.special_ideal(2, m.Counter())
        self.assertEqual(result["determinant"], 5)
        self.assertEqual(len(result["cells"]), 25)
        for cell in result["cells"]:
            a, b = cell["ab"]
            self.assertEqual(cell["member"], (a-2*b) % 5 == 0)
            if cell["member"]:
                self.assertEqual(self.gaussian.mul(cell["element_quotient"], (2, -1)), (a, -b))

    def test_descent_missing_rank_cannot_consume_truth(self):
        # Invented tiny identity records, deliberately no solvable log matrix.
        f = m.Field(7, (1, 0))
        g = next(f.pow(x, 16) for x in f.elements() if x != f.zero and f.pow(x, 16) != f.one)
        relations = {"solve": {"solution": None}, "columns": [],
                     "fields": [{"root": [0, 1], "generators": []}],
                     "pairs": [{"factorizations": [{"accepted": True, "projected": list(g),
                                                     "unit": [1, 0], "factors": []}]}],
                     "projection_exponent": 16}
        result = m.individual_descent(f, 3, relations, g, [f.one, g])
        self.assertEqual(result["recovered"][0]["scalar"], 0)
        self.assertIsNone(result["recovered"][1]["scalar"])
        self.assertEqual(result["descents"][0]["candidates_tested"], 1)
        self.assertFalse(result["truth_log_input"])


class EnvelopeSoftwareTests(unittest.TestCase):
    def test_shared_status_schema_preserves_incompleteness_in_observables(self):
        for status in m.CASE_STATUSES:
            self.assertEqual(m._case("invented", {"completeness": "incomplete_rank"}, {}, status=status)["status"], status)
        for custom in ("incomplete_rank", "incomplete_coverage", "invalid_control"):
            with self.assertRaisesRegex(ValueError, "shared schema"):
                m._case("invented", {}, {}, status=custom)

    def test_actual_rss_shape_units_and_tampering(self):
        record = m.resource_usage("software fixture")
        m._check_resource_usage(record)
        self.assertGreater(record["peak_rss_bytes"], 0)
        broken = copy.deepcopy(record)
        broken["peak_rss_bytes"] += 1
        with self.assertRaisesRegex(ValueError, "resource measurement"):
            m._check_resource_usage(broken)

    def test_checker_rejects_source_or_coverage_before_study_work(self):
        with patch.object(m, "Field", side_effect=AssertionError("study field must not run")):
            with self.assertRaises(ValueError):
                m.check_result({"schema_version": 1, "direction": "pairing", "parameters": {}})
            with self.assertRaises(ValueError):
                m.check_result({"schema_version": 1, "direction": "pairing", "parameters": m.FIXTURE, "cases": []})
            payload = {"schema_version": 1, "direction": "pairing", "parameters": m.FIXTURE,
                       "cases": [m._case(name, {}, {}) for name in m.PANELS],
                       "instrument_scope": {"full_panels": list(m.PANELS), "scientific_claim": False}}
            with self.assertRaisesRegex(ValueError, "controls"):
                m.check_result(payload)

    def test_cli_help_cannot_launch_experiment(self):
        with patch.object(m, "run_experiment", side_effect=AssertionError("no study launch")):
            with redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit) as exit_info:
                    m.main(["--help"])
            self.assertEqual(exit_info.exception.code, 0)

    def test_cli_routes_seed_and_output_to_canonical_writer_without_execution(self):
        # Mocks only: no scientific execution and no output directory creation.
        sentinel = {"softwarecheck_only": True}
        with patch.object(m, "run_experiment", return_value=sentinel) as experiment:
            with patch.object(m, "write_artifacts") as writer:
                self.assertEqual(m.main(["--seed", "9", "--output-dir", "/tmp/pairing-mocked-no-write"]), 0)
        experiment.assert_called_once_with(9)
        self.assertEqual(writer.call_args.args[:3], (sentinel, Path("/tmp/pairing-mocked-no-write"), 9))

    def test_cli_check_has_separate_measured_cost_and_no_trial_launch(self):
        captured = io.StringIO()
        with patch.object(Path, "read_text", return_value="{}"):
            with patch.object(m, "check_result", return_value=True) as checker:
                with patch.object(m, "run_experiment", side_effect=AssertionError("no study launch")):
                    with redirect_stdout(captured):
                        self.assertEqual(m.main(["--check", "/tmp/pairing-mocked-no-read"]), 0)
        checker.assert_called_once_with({})
        record = json.loads(captured.getvalue())
        self.assertTrue(record["certificate_valid"])
        self.assertFalse(record["independent_review"])
        self.assertGreaterEqual(record["checker_wall_seconds"], 0)
        self.assertGreaterEqual(record["checker_cpu_seconds"], 0)
        m._check_resource_usage(record["resource"])
        self.assertIn("separate checker", record["resource"]["scope"])


if __name__ == "__main__":
    unittest.main()

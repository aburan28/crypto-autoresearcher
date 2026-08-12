from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1] / "src" / "coordinate_expansion.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "coordinate_expansion_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load coordinate expansion module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class CoordinateExpansionTests(unittest.TestCase):
    def test_exact_integer_validation_rejects_bool(self) -> None:
        with self.assertRaises(ValueError):
            MODULE.exact_int(True, "value")

    def test_signed_formal_class_count_matches_small_cases(self) -> None:
        self.assertEqual(MODULE.signed_formal_class_count(1, 1), 2)
        self.assertEqual(MODULE.signed_formal_class_count(1, 2), 3)
        self.assertEqual(MODULE.signed_formal_class_count(1, 3), 4)
        self.assertEqual(MODULE.signed_formal_class_count(2, 3), 16)

    def test_symmetry_specific_factor_base_sizing(self) -> None:
        q = 101
        canonical = MODULE.choose_factor_base_size(
            q, 5, 0.5, "sign_canonical"
        )
        complete = MODULE.choose_factor_base_size(
            q, 5, 0.5, "sign_complete"
        )
        self.assertGreaterEqual(
            MODULE.formal_class_count(canonical, 5, "sign_canonical") / q,
            0.5,
        )
        self.assertGreaterEqual(
            MODULE.formal_class_count(complete, 5, "sign_complete") / q,
            0.5,
        )

    def test_canonical_support_and_point_support_agree(self) -> None:
        curve = MODULE.Curve(17, 2, 2)
        generator = (5, 1)
        points = [curve.mul(scalar, generator) for scalar in (1, 2, 3)]
        levels = MODULE.build_point_levels(curve, points, 5)
        audit = MODULE.audit_scalar_geometry(
            [1, 2, 3], 19, "sign_canonical", levels
        )
        for depth, profile in enumerate(audit["profiles"], 1):
            self.assertEqual(
                profile["support_size"], len(levels["levels"][depth])
            )
            self.assertGreaterEqual(
                profile["canonical_formal_defect"], 0
            )
        self.assertTrue(audit["d5_new"].isdisjoint(audit["d1"]))
        self.assertTrue(audit["d5_new"].isdisjoint(audit["d3"]))
        self.assertEqual(set(audit["split_hits"]), audit["d5"])

    def test_sign_complete_cancellation_canonical_support(self) -> None:
        curve = MODULE.Curve(17, 2, 2)
        generator = (5, 1)
        points = [
            generator,
            curve.neg(generator),
            curve.mul(2, generator),
            curve.neg(curve.mul(2, generator)),
        ]
        levels = MODULE.build_point_levels(curve, points, 5)
        audit = MODULE.audit_scalar_geometry(
            [1, 18, 2, 17], 19, "sign_complete", levels
        )
        self.assertEqual(
            audit["profiles"][4]["canonical_formal_class_total"],
            MODULE.signed_formal_class_count(2, 5),
        )
        self.assertEqual(set(audit["split_hits"]), audit["d5"])

    def test_point_only_query_recovers_witnesses(self) -> None:
        curve = MODULE.Curve(17, 2, 2)
        generator = (5, 1)
        points = [curve.mul(scalar, generator) for scalar in (1, 2, 3)]
        levels = MODULE.build_point_levels(curve, points, 3)
        targets = [curve.mul(scalar, generator) for scalar in range(19)]
        query = MODULE.point_only_query(
            curve,
            points,
            levels["levels"][2],
            levels["levels"][3],
            targets,
            12345,
        )
        self.assertEqual(
            query["api_boundary"], "TARGET_POINTS_AND_POINT_ADVICE_ONLY"
        )
        expected_successes = len(
            MODULE.build_point_levels(curve, points, 5)["levels"][5]
        )
        for order in query["scan_orders"].values():
            self.assertEqual(
                order["successful_targets"], expected_successes
            )
        self.assertIsNotNone(query["first_witness"])

    def test_tiny_generated_smoke_run(self) -> None:
        result = MODULE.run_experiment(
            bit_sizes=[8],
            seeds=[271828],
            null_draws=1,
            targets=8,
            rho_trials=1,
            occupancy_lambda=0.5,
        )
        self.assertTrue(result["valid"])
        self.assertFalse(result["interpretation_eligible"])
        self.assertEqual(result["summary"]["instances_completed"], 1)
        self.assertFalse(result["summary"]["breakthrough_claim"])
        instance = result["instances"][0]
        self.assertEqual(instance["curve"]["cofactor"], 1)
        self.assertNotIn(instance["curve"]["trace"], (0, 1))
        self.assertNotIn(
            instance["curve"]["j_invariant"],
            (0, 1728 % instance["curve"]["p"]),
        )
        self.assertEqual(
            instance["factor_base_digest_set_before_audit"],
            instance["factor_base_digest_set_after_audit"],
        )
        self.assertTrue(
            all(
                record["query"]["api_boundary"]
                == "TARGET_POINTS_AND_POINT_ADVICE_ONLY"
                for record in instance["configurations"]
            )
        )


if __name__ == "__main__":
    unittest.main()

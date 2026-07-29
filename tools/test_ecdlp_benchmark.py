#!/usr/bin/env python3
"""Tests for the ECDLP breakthrough benchmark.

The three that matter most are `test_refuses_an_exponent_it_cannot_resolve`,
`test_recovers_a_known_square_root_exponent` and
`test_falling_ratio_alone_is_not_a_breakthrough_signal`. A benchmark checked
against only one direction is uncalibrated; a benchmark that reports a
plausible-looking exponent from a ladder too short to carry one is worse than
no benchmark, because it launders noise into a claim.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from harness.ecdlp_benchmark import (  # noqa: E402
    COST_STAGES, HardInstance, Measurement, compare, fit_exponent,
    generate_hard_instance,
)


def ladder(exponent: float, constant: float, coeff: float,
           ns=(10**4, 10**5, 10**6, 10**7, 10**8, 10**9)):
    return [(n, int(constant + coeff * (n ** exponent))) for n in ns]


class ResolvabilityTests(unittest.TestCase):
    def test_refuses_an_exponent_it_cannot_resolve(self) -> None:
        """A short ladder dominated by the setup constant yields NO exponent."""
        short = ladder(0.5, constant=1400.0, coeff=4.3,
                       ns=(5_513, 23_117, 58_472, 188_132, 1_400_911))
        fit = fit_exponent(short)
        self.assertFalse(fit["ladder_resolves_an_exponent"])
        self.assertGreater(fit["setup_constant_share_at_ladder_top"], 0.10)

    def test_recovers_a_known_square_root_exponent(self) -> None:
        fit = fit_exponent(ladder(0.5, constant=10.0, coeff=5.0))
        self.assertTrue(fit["ladder_resolves_an_exponent"])
        self.assertAlmostEqual(fit["raw_slope"], 0.5, delta=0.02)

    def test_recovers_a_known_sub_square_root_exponent(self) -> None:
        fit = fit_exponent(ladder(0.33, constant=10.0, coeff=5.0))
        self.assertTrue(fit["ladder_resolves_an_exponent"])
        self.assertAlmostEqual(fit["raw_slope"], 0.33, delta=0.02)

    def test_a_ladder_with_too_few_rungs_is_unresolvable(self) -> None:
        fit = fit_exponent(ladder(0.5, 1.0, 5.0, ns=(10**6, 10**7, 10**8)))
        self.assertFalse(fit["ladder_resolves_an_exponent"])

    def test_falling_ratio_alone_is_not_a_breakthrough_signal(self) -> None:
        """The trap: ops/sqrt(n) falls for rho itself, because C is amortised.

        Scoring a falling ratio as sub-square-root would pass rho as a break of
        rho. The ratio must CONVERGE to a positive constant for square-root and
        keep decaying for genuinely sub-square-root.
        """
        sqrt_fit = fit_exponent(ladder(0.5, constant=1400.0, coeff=4.3))
        sqrt_trend = sqrt_fit["ratio_trend"]
        self.assertGreater(sqrt_trend[0], sqrt_trend[-1],
                           "rho's own ratio falls -- that is the trap")
        # ...yet it CONVERGES to the positive coefficient rather than to zero.
        self.assertAlmostEqual(sqrt_trend[-1], 4.3, delta=0.5)

        sub_fit = fit_exponent(ladder(0.33, constant=10.0, coeff=5.0))
        sub_trend = sub_fit["ratio_trend"]

        # The discriminator is CONVERGENCE vs CONTINUED DECAY, not the absolute
        # value. Consecutive-ratio-of-ratios goes to 1 for square-root and stays
        # well below 1 for genuinely sub-square-root, at every rung.
        sqrt_settling = sqrt_trend[-1] / sqrt_trend[-2]
        sub_settling = sub_trend[-1] / sub_trend[-2]
        self.assertGreater(sqrt_settling, 0.9,
                           "square-root should have essentially converged")
        self.assertLess(sub_settling, 0.8,
                        "sub-square-root should still be decaying at the top")
        self.assertLess(sub_settling, sqrt_settling)

    def test_two_points_cannot_produce_an_exponent_claim(self) -> None:
        fit = fit_exponent([(10**6, 5000), (10**8, 50000)])
        self.assertFalse(fit["ladder_resolves_an_exponent"])


class InstanceQualityTests(unittest.TestCase):
    def test_cofactor_is_bounded_so_the_advertised_size_is_honest(self) -> None:
        inst = generate_hard_instance(seed=3, field_bits=16, max_cofactor=8)
        self.assertLessEqual(inst.cofactor, 8)
        self.assertGreater(inst.n_over_p, 0.05)

    def test_work_bits_not_field_bits_is_the_real_difficulty(self) -> None:
        inst = generate_hard_instance(seed=3, field_bits=16)
        self.assertAlmostEqual(inst.work_bits, inst.n.bit_length() / 2, delta=1.0)

    def test_public_view_never_leaks_the_scalar(self) -> None:
        inst = generate_hard_instance(seed=3, field_bits=16)
        self.assertIsNotNone(inst.k)
        self.assertNotIn("k", inst.public())

    def test_the_old_generator_produced_degenerate_instances(self) -> None:
        """Pins the defect this replaces, so a regression is visible."""
        from harness.toycurve import EllipticCurve, generate_instance
        old = generate_instance(seed=3, field_bits=20)
        cofactor = EllipticCurve(old.p, old.a, old.b).order() // old.n
        self.assertGreater(cofactor, 8,
                           "the old generator is expected to be degenerate here")
        new = generate_hard_instance(seed=3, field_bits=20)
        self.assertGreater(new.n, old.n * 100)


class ScoringTests(unittest.TestCase):
    def _m(self, seed, bits, n, ops, charged=COST_STAGES, valid=True):
        return Measurement(instance_seed=seed, field_bits=bits, n=n,
                           work_bits=0.0, solved=True, certificate_valid=valid,
                           group_operations=ops, wall_seconds=0.0,
                           stages_charged=tuple(charged))

    def test_an_uncharged_stage_makes_the_cost_incomparable(self) -> None:
        partial = [self._m(1, 16, 10**6, 100, charged=("relation_collection",))]
        out = compare(partial, partial)
        self.assertFalse(out["cost_accounting_complete"])
        self.assertIn("linear_algebra", out["stages_never_charged"])

    def test_an_invalid_certificate_yields_no_speedup(self) -> None:
        bad = [self._m(1, 16, 10**6, 10, valid=False)]
        base = [self._m(1, 16, 10**6, 1000)]
        self.assertIsNone(compare(bad, base)["rows"][0]["speedup_vs_rho"])

    def test_speedup_is_measured_against_the_same_instance(self) -> None:
        ch = [self._m(1, 16, 10**6, 500)]
        base = [self._m(1, 16, 10**6, 1000)]
        self.assertAlmostEqual(compare(ch, base)["rows"][0]["speedup_vs_rho"], 2.0)

    def test_scorer_contains_no_threshold(self) -> None:
        """D4: a scorer that knows the passing value is how a gate stops failing."""
        src = (REPO / "harness" / "ecdlp_benchmark.py").read_text(encoding="utf-8")
        code = "\n".join(l for l in src.splitlines()
                         if not l.strip().startswith("#"))
        code = code.split('"""')[0] + "".join(code.split('"""')[2::2])
        for banned in ("verdict", "PASS", "breakthrough_detected"):
            self.assertNotIn(f"return {banned}", code)


if __name__ == "__main__":
    unittest.main()

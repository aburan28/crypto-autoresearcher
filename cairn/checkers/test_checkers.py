"""Tests for the Stage 0 cairn checkers.

These call `check()` directly -- the exact function cairn's sandboxed
verifier calls, byte for byte -- so a pass here means what cairn would
compute, without needing the Rust binary at test time. Every case was also
run once against a real `cairn-mcp` `score_candidate` call before this file
was written (docs/cairn-integration-plan.md Stage 0 exit criterion); this
file is what keeps that agreement from silently drifting.

Fixtures below are real certificates already in `experiments/`, not
invented ones: `RUN-STR-rho-b8-s1/raw-result.json` (discrete_log) and
`RUN-STR-004-EP-A13M3/raw-result.json` `raw.certificates[0]` (decomposition).
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import discrete_log
import decomposition


class DiscreteLogCheckerTests(unittest.TestCase):
    CURVE = {"p": 223, "a": 0, "b": 171}

    def test_real_certificate_accepts(self) -> None:
        ok, detail = discrete_log.check(
            {"curve": self.CURVE, "P": [105, 42], "Q": [81, 42], "k": 2}
        )
        self.assertTrue(ok, detail)
        self.assertIn("2*P = Q", detail)

    def test_wrong_scalar_rejects(self) -> None:
        ok, detail = discrete_log.check(
            {"curve": self.CURVE, "P": [105, 42], "Q": [81, 42], "k": 3}
        )
        self.assertFalse(ok)
        self.assertIn("does not equal Q", detail)

    def test_point_not_on_curve_rejects(self) -> None:
        ok, detail = discrete_log.check(
            {"curve": self.CURVE, "P": [1, 1], "Q": [81, 42], "k": 2}
        )
        self.assertFalse(ok)
        self.assertIn("P is not on the curve", detail)

    def test_singular_curve_rejects(self) -> None:
        # 4a^3 + 27b^2 = 0 mod p -- a=0, b=0 is the trivial singular case.
        ok, detail = discrete_log.check(
            {"curve": {"p": 223, "a": 0, "b": 0}, "P": [0, 0], "Q": [0, 0], "k": 1}
        )
        self.assertFalse(ok)
        self.assertIn("singular", detail)

    def test_malformed_artifact_rejects_without_raising(self) -> None:
        for bad in (
            {},
            {"curve": self.CURVE, "P": [105, 42], "Q": [81, 42]},  # no k
            {"curve": self.CURVE, "P": "not-a-point", "Q": [81, 42], "k": 2},
            "not-a-dict",
        ):
            ok, detail = discrete_log.check(bad)
            self.assertFalse(ok, detail)

    def test_negative_p_does_not_crash_the_checker(self) -> None:
        # A checker that raises on hostile input is UNAVAILABLE, not a
        # rejection (docs/cairn-integration-plan.md invariant b) -- so
        # malformed and adversarial input alike must return, never throw.
        ok, detail = discrete_log.check(
            {"curve": {"p": -1, "a": 0, "b": 1}, "P": [0, 1], "Q": [0, 1], "k": 1}
        )
        self.assertFalse(ok, detail)


class DecompositionCheckerTests(unittest.TestCase):
    CURVE = {"p": 2293, "a": 0, "b": 417}
    TARGET = [1534, 1689]
    SUMMANDS = [[1023, 84], [1583, 354], [877, 988]]

    def test_real_certificate_accepts(self) -> None:
        ok, detail = decomposition.check(
            {"curve": self.CURVE, "target": self.TARGET, "summands": self.SUMMANDS}
        )
        self.assertTrue(ok, detail)
        self.assertIn("3 summand(s)", detail)

    def test_off_curve_summand_rejects(self) -> None:
        bad = [self.SUMMANDS[0], [1583, 355], self.SUMMANDS[2]]
        ok, detail = decomposition.check(
            {"curve": self.CURVE, "target": self.TARGET, "summands": bad}
        )
        self.assertFalse(ok)
        self.assertIn("not on the curve", detail)

    def test_on_curve_but_wrong_sum_rejects(self) -> None:
        # Negating one real summand keeps every point on the curve, so this
        # exercises the sum check specifically rather than curve membership.
        bad = [self.SUMMANDS[0], [1583, (2293 - 354) % 2293], self.SUMMANDS[2]]
        ok, detail = decomposition.check(
            {"curve": self.CURVE, "target": self.TARGET, "summands": bad}
        )
        self.assertFalse(ok)
        self.assertIn("do not sum to target", detail)

    def test_empty_summands_rejects_rather_than_trivially_accepting(self) -> None:
        ok, detail = decomposition.check(
            {"curve": self.CURVE, "target": self.TARGET, "summands": []}
        )
        self.assertFalse(ok, detail)

    def test_malformed_artifact_rejects_without_raising(self) -> None:
        for bad in (
            {},
            {"curve": self.CURVE, "target": self.TARGET},  # no summands
            {"curve": self.CURVE, "target": self.TARGET, "summands": "nope"},
            None,
        ):
            ok, detail = decomposition.check(bad)
            self.assertFalse(ok, detail)


if __name__ == "__main__":
    unittest.main()

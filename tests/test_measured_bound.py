"""Schema checks for the `measured_bound` block on evidence records.

Optional-when-absent by construction (the validator baseline is prune-only,
so nothing new can be required of immutable records); a record that carries
the block must complete it and must respect the four rules that make a bound
safe to carry: the tier is the record's tier, the unit is counted and never
clocked, an exponent needs sizes, and an inadmissible verdict is never
negative evidence (docs/bounds-and-frontiers.md).
"""

from __future__ import annotations

import copy
import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

import validate_ledger  # noqa: E402


def _errors(body: dict) -> list[str]:
    ctx = validate_ledger.Ctx(legacy_paths=set())
    validate_ledger.check_measured_bound("r.yaml", body, ctx)
    return ctx.errors


BOUND = {
    "bound_id": "ECBND1h7b69b9787056",
    "repository": "aburan28/crypto",
    "commit": None,
    "record_path": "docs/bounds/records/prime-rho-neg.json",
    "domain_id": "ECDOM1ha1f283af3a5d",
    "domain": {
        "problem": "ecdlp.single_target",
        "family": "prime",
        "target_kind": "planted",
        "unit": "ecbench.gae",
        "tier": "toy",
    },
    "method_id": "ECM1hefea4e0ebe79",
    "method": "rho.negation",
    "level": "exponent",
    "ops_ratio_to_floor": {"value": 1.466, "ci95": [1.278, 1.653]},
    "alpha": {"value": 0.454, "ci95": [0.273, 0.607], "declared": 0.5,
              "scaling_claim": True},
    "sizes_log2_r": [17.7, 19.1, 21.2, 24.0],
    "verified_runs": 96,
    "bounded": True,
}

VERDICT = {
    "verdict_id": "ECVD1h9c8f1f49a76c",
    "challenge_id": "ECCH1h9b3b00f6ac6e",
    "epoch": 1,
    "outcome": "trade",
    "advances_on": ["ops"],
    "regresses_on": ["memory"],
    "level_moved": None,
    "improves_on": ["ECBND1hcf67af806cc5"],
}


def body(**overrides) -> dict:
    base = {
        "id": "EV-RHO-000001",
        "claim_tier": "toy",
        "direction": "supports",
        "strength": "preliminary",
        "measured_bound": copy.deepcopy(BOUND),
    }
    base.update(overrides)
    return base


class MeasuredBoundTests(unittest.TestCase):
    def test_absent_block_is_silent(self) -> None:
        self.assertEqual(_errors({"id": "EV-X-000000"}), [])

    def test_complete_block_passes(self) -> None:
        self.assertEqual(_errors(body()), [])

    def test_complete_block_with_verdict_passes(self) -> None:
        b = body()
        b["measured_bound"]["verdict"] = copy.deepcopy(VERDICT)
        self.assertEqual(_errors(b), [])

    def test_missing_fields_are_named(self) -> None:
        b = body()
        for field in ("bound_id", "repository", "domain", "method", "level",
                      "ops_ratio_to_floor", "verified_runs"):
            del b["measured_bound"][field]
        errors = " ".join(_errors(b))
        for field in ("bound_id", "repository", "domain", "method", "level",
                      "ops_ratio_to_floor", "verified_runs"):
            self.assertIn(field, errors)

    def test_tier_must_equal_claim_tier(self) -> None:
        b = body(claim_tier="medium")
        self.assertTrue(any("claim_tier" in e for e in _errors(b)))
        b = body()
        b["measured_bound"]["domain"]["tier"] = "crypto"
        self.assertTrue(any("claim_tier" in e for e in _errors(b)))

    def test_a_clocked_unit_is_refused(self) -> None:
        for unit in ("wall_seconds", "online_wall_ns", "time_ms"):
            b = body()
            b["measured_bound"]["domain"]["unit"] = unit
            self.assertTrue(any("wall-clock" in e for e in _errors(b)), unit)

    def test_an_exponent_needs_four_sizes_and_a_scaling_claim(self) -> None:
        b = body()
        b["measured_bound"]["sizes_log2_r"] = [17.7, 19.1, 21.2]
        self.assertTrue(any("four sizes" in e for e in _errors(b)))
        b = body()
        b["measured_bound"]["alpha"]["scaling_claim"] = False
        self.assertTrue(any("scaling_claim" in e for e in _errors(b)))
        b = body()
        b["measured_bound"]["level"] = "constant"
        b["measured_bound"]["alpha"]["scaling_claim"] = False
        b["measured_bound"]["sizes_log2_r"] = [17.7, 19.1]
        self.assertEqual(_errors(b), [])

    def test_malformed_ids_are_refused(self) -> None:
        b = body()
        b["measured_bound"]["bound_id"] = "ECBND1h7b69"
        self.assertTrue(any("bound_id" in e for e in _errors(b)))
        b = body()
        b["measured_bound"]["verdict"] = dict(VERDICT, verdict_id="V-1")
        self.assertTrue(any("verdict_id" in e for e in _errors(b)))
        b = body()
        b["measured_bound"]["verdict"] = dict(VERDICT, improves_on=["nope"])
        self.assertTrue(any("improves_on" in e for e in _errors(b)))

    def test_interval_must_bracket_the_value(self) -> None:
        b = body()
        b["measured_bound"]["ops_ratio_to_floor"] = {"value": 2.0,
                                                    "ci95": [1.278, 1.653]}
        self.assertTrue(any("ci95" in e for e in _errors(b)))

    def test_an_inadmissible_verdict_is_never_negative_evidence(self) -> None:
        for direction in ("weakens", "contradicts", "supports"):
            b = body(direction=direction)
            b["measured_bound"]["verdict"] = dict(VERDICT, outcome="inadmissible",
                                                  advances_on=[], regresses_on=[])
            errors = _errors(b)
            self.assertTrue(any("neutral" in e for e in errors), direction)
        b = body(direction="neutral", strength="inconclusive")
        b["measured_bound"]["verdict"] = dict(VERDICT, outcome="inadmissible",
                                              advances_on=[], regresses_on=[])
        self.assertEqual(_errors(b), [])

    def test_a_level_is_a_statement_about_operations(self) -> None:
        b = body()
        b["measured_bound"]["verdict"] = dict(VERDICT, outcome="advances",
                                              advances_on=["memory"],
                                              regresses_on=[],
                                              level_moved="constant")
        self.assertTrue(any("level_moved" in e for e in _errors(b)))
        b = body()
        b["measured_bound"]["verdict"] = dict(VERDICT, outcome="advances",
                                              advances_on=["ops"],
                                              regresses_on=[],
                                              level_moved="exponent")
        self.assertEqual(_errors(b), [])
        b = body()
        b["measured_bound"]["alpha"]["scaling_claim"] = False
        b["measured_bound"]["level"] = "constant"
        b["measured_bound"]["verdict"] = dict(VERDICT, outcome="advances",
                                              advances_on=["ops"],
                                              regresses_on=[],
                                              level_moved="exponent")
        self.assertTrue(any("exponent" in e for e in _errors(b)))

    def test_unknown_outcome_is_refused(self) -> None:
        b = body()
        b["measured_bound"]["verdict"] = dict(VERDICT, outcome="wins")
        self.assertTrue(any("outcome" in e for e in _errors(b)))


if __name__ == "__main__":
    unittest.main()

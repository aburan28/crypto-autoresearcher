"""Guard the scope error: a favorable idealized floor is not an algorithm."""
import math

import pytest

from tools.check_icperf_orbit_floor import (
    ORBIT_SIZE, SUBGROUP_ORDER, approximate_minimum_bits, minimum_bits, report,
)


def test_archived_models_have_different_comparisons_with_rho():
    result = report()
    rows = result["rows"]
    assert [row["cost_bits"] for row in rows] == pytest.approx(
        [68.5849625010, 67.5849625010, 58.0348279985], abs=1e-7)
    assert result["rho_bits"] == pytest.approx(60.8090365640, abs=1e-7)
    assert [row["relative_to_rho"] for row in rows] == ["above", "above", "below"]
    assert result["demonstrated_algorithmic_speedup"] is False


@pytest.mark.parametrize("ambient", [SUBGROUP_ORDER, 4 * SUBGROUP_ORDER])
def test_numerical_minimum_agrees_with_independent_am_gm_balance(ambient):
    for orbit in (1, ORBIT_SIZE):
        assert minimum_bits(ambient, orbit) == pytest.approx(
            approximate_minimum_bits(ambient, orbit), abs=1e-7)
    # Both the relation count and the quadratic algebra term change.
    shift = minimum_bits(ambient, 1) - minimum_bits(ambient, ORBIT_SIZE)
    assert shift == pytest.approx(1.5 * math.log2(ORBIT_SIZE), abs=1e-7)


def test_no_collapse_control_cannot_be_reported_as_a_crossover():
    result = report()
    assert minimum_bits(4 * SUBGROUP_ORDER, 1) > result["rho_bits"]
    assert approximate_minimum_bits(4 * SUBGROUP_ORDER, 1) > result["rho_bits"]

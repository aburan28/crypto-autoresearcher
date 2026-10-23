"""Exact arithmetic controls for the prepared prime-field coset input."""

from __future__ import annotations

from crypto_autoresearcher.index_calculus.curve import Curve
from crypto_autoresearcher.index_calculus.factor_base import FactorBase
from crypto_autoresearcher.index_calculus.msolve import evaluate
from tools.icperf_prime_coset_quadratic import binary_chain, build_record, lift_system


def test_chain_is_an_exact_power_identity_on_all_small_field_inputs():
    E = Curve(101, 6, 9, 83)
    fb = FactorBase.subgroup(E, 10, seed=7, divisor=20)
    chain = binary_chain(20)
    assert chain[-1][0] == 20
    target = E.add(fb.points[0], fb.points[1])
    lifted, direct, _, indices = lift_system(E, fb, target[0], 2, 9)
    for x in range(E.p):
        values = [0] * len(lifted.names)
        values[0] = x
        for out, left, right in chain:
            values[indices[0][out]] = (values[indices[0][left]]
                                       * values[indices[0][right]]) % E.p
        assert all(evaluate(poly, values, E.p) == 0 for poly in lifted.polys[:len(chain)])
        direct_member = evaluate(direct.polys[0], values[:len(direct.names)], E.p) == 0
        lifted_member = evaluate(lifted.polys[len(chain)], values, E.p) == 0
        assert direct_member == lifted_member


def test_archived_63bit_m8_planted_input_and_negative_controls():
    record = build_record(8, 20261017)
    assert record["factor_base_size"] == 380
    assert record["coset_order"] == 788
    assert record["nonliftable_coset_x_count"] == 408
    assert len(record["addition_chain"]) == 12
    assert all(record["controls"].values())
    assert record["direct"]["max_total_degree"] == 788
    assert record["lifted"]["max_total_degree"] <= 4
    assert record["lifted"]["variable_count"] == 111


def test_chain_rejects_bad_exponents():
    for bad in (0, 1, -3):
        try:
            binary_chain(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"accepted exponent {bad}")

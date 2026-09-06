"""Correctness tests for the FactorBaseLab experimental instrumentation."""
from __future__ import annotations

import pytest

from harness.factor_base_lab import (
    FactorBaseSpec,
    build_factor_base,
    compare_with_matched_random,
    exact_two_sum,
    matched_random_control,
    rank_mod_prime,
    signed_points,
    verify_two_sum_result,
)
from harness.toycurve import ECDLPInstance, EllipticCurve, generate_instance


def textbook_instance() -> ECDLPInstance:
    E = EllipticCurve(17, 2, 2)
    P = (5, 1)
    k = 7
    return ECDLPInstance(
        p=17,
        a=2,
        b=2,
        P=P,
        Q=E.mul(k, P),
        n=19,
        k=k,
        field_bits=5,
        seed=1,
    )


def test_exact_two_sum_finds_known_textbook_decomposition():
    E = EllipticCurve(17, 2, 2)
    B = (5, 1)
    C = (6, 3)
    R = E.add(B, C)
    assert R == (10, 6)

    result = exact_two_sum(E, [5, 6], R)
    assert result.found
    assert result.multiplicity >= 1
    assert set(result.summand_x) == {5, 6}
    assert verify_two_sum_result(result)


def test_exact_two_sum_is_independent_of_semaev_existence_logic():
    E = EllipticCurve(17, 2, 2)
    R = (10, 6)
    result = exact_two_sum(E, [0], R)
    assert not result.found
    assert result.multiplicity == 0
    assert result.certificate is None
    assert verify_two_sum_result(result)


def test_signed_points_contains_both_lifts_without_duplicates():
    E = EllipticCurve(17, 2, 2)
    pts = signed_points(E, [5])
    assert set(pts) == {(5, 1), (5, 16)}


@pytest.mark.parametrize(
    "family",
    [
        "interval",
        "centered_interval",
        "qr_window",
        "sparse_polynomial_predicate",
        "random_matched",
    ],
)
def test_factor_base_families_realize_exact_cardinality(family):
    inst = generate_instance(seed=5, field_bits=8)
    spec = FactorBaseSpec(family=family, requested_size=6, seed=17)
    base = build_factor_base(inst, spec)
    assert base.realized_size == 6
    assert len(set(base.xs)) == 6
    assert len(base.factor_base_hash) == 64
    E = inst.curve()
    assert all(E.lift_x(x) is not None for x in base.xs)


def test_multiplicative_coset_is_supported_when_enough_points_lift():
    inst = generate_instance(seed=9, field_bits=10)
    spec = FactorBaseSpec(
        family="multiplicative_coset",
        requested_size=3,
        seed=4,
    )
    base = build_factor_base(inst, spec)
    assert base.realized_size == 3
    assert all(x != 0 for x in base.xs)


def test_matched_random_control_matches_realized_size_and_scope():
    inst = generate_instance(seed=7, field_bits=8)
    base = build_factor_base(
        inst,
        FactorBaseSpec("interval", requested_size=5, seed=1),
    )
    control = matched_random_control(inst, base, seed=99)
    assert control.realized_size == base.realized_size
    assert control.spec.scope == base.spec.scope
    assert control.spec.family == "random_matched"


def test_target_subgroup_scope_rejects_oversized_base():
    inst = generate_instance(seed=1, field_bits=6)
    with pytest.raises(ValueError):
        build_factor_base(
            inst,
            FactorBaseSpec(
                "interval",
                requested_size=(inst.n - 1) // 2 + 1,
                scope="target_subgroup",
            ),
        )


def test_target_subgroup_membership_is_verified():
    inst = generate_instance(seed=1, field_bits=6)
    size = min(3, (inst.n - 1) // 2)
    base = build_factor_base(
        inst,
        FactorBaseSpec("interval", requested_size=size, scope="target_subgroup"),
    )
    E = inst.curve()
    for x in base.xs:
        P = E.lift_x(x)
        assert P is not None
        assert E.mul(inst.n, P) is None


def test_rank_mod_prime_tracks_incremental_independence():
    assert rank_mod_prime([], 19) == 0
    assert rank_mod_prime([[1, 0, 0], [0, 1, 0]], 19) == 2
    assert rank_mod_prime([[1, 0], [2, 0], [0, 1]], 19) == 2
    with pytest.raises(ValueError):
        rank_mod_prime([[1, 2], [3]], 19)


def test_matched_comparison_uses_same_targets_and_cardinality():
    inst = textbook_instance()
    result = compare_with_matched_random(
        inst,
        FactorBaseSpec("interval", requested_size=4, seed=3),
        control_seed=77,
        target_count=8,
        target_seed=123,
        run_groebner=False,
    )
    assert result.structured.realized_size == result.random_control.realized_size == 4
    assert result.structured.targets == result.random_control.targets == 8
    assert 0.0 <= result.structured.decomposition_yield <= 1.0
    assert 0.0 <= result.random_control.decomposition_yield <= 1.0


def test_groebner_smoke_agrees_with_exact_oracle():
    inst = textbook_instance()
    result = compare_with_matched_random(
        inst,
        FactorBaseSpec("interval", requested_size=3, seed=2),
        control_seed=11,
        target_count=2,
        target_seed=29,
        run_groebner=True,
        groebner_target_limit=1,
    )
    assert result.structured.solver_targets == 1
    assert result.random_control.solver_targets == 1
    assert result.structured.groebner_seconds >= 0.0
    assert result.random_control.groebner_seconds >= 0.0

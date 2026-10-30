"""Exact finite-field correctness controls; these are not performance trials."""
from itertools import product

import pytest

from crypto_autoresearcher.index_calculus.curve import Curve
from crypto_autoresearcher.index_calculus.quality_cli import analyze
from crypto_autoresearcher.index_calculus.relation_quality import (
    AffineRelations, cancel_outside, rank_per_cost, recover_target)


def solutions(system):
    return [z for z in product(range(system.modulus), repeat=system.columns)
            if all(sum(x*y for x, y in zip(row, z)) % system.modulus == rhs
                   for row, rhs in zip(system.rows, system.rhs))]


@pytest.mark.parametrize('p', [2, 5, 7])
def test_identifiability_matches_all_solutions(p):
    system = AffineRelations(p, 3)
    system.add([1, 2, 1], 3)
    system.add([0, 1, 1], 2)
    candidates = solutions(system)
    assert len(candidates) == p
    for v in product(range(p), repeat=3):
        result = system.identify(v)
        values = {sum(x*y for x, y in zip(v, z)) % p for z in candidates}
        assert result.identifiable == (len(values) == 1)
        assert result.identifiable == (not any(result.syndrome))
        if result.identifiable:
            assert result.value == next(iter(values))
            assert [sum(w*row[j] for w, row in zip(result.row_weights, system.rows)) % p
                    for j in range(3)] == list(v)
            assert sum(w*b for w, b in zip(result.row_weights, system.rhs)) % p == result.value


def test_inconsistency_is_atomic_and_affine_dedup_includes_rhs():
    system = AffineRelations(7, 2)
    assert system.add([1, 1], 2)
    assert not system.add([2, 2], 4)
    assert system.summary()['unique_affine_equations'] == 1
    assert system.duplicates == 1
    with pytest.raises(ValueError, match='inconsistent'):
        system.add([2, 2], 5)
    assert len(system.rows) == 2
    assert system.identify([1, 1]).value == 2


@pytest.mark.parametrize('U', [[[1], [1]], [[1, 0], [0, 1]], [[], []]])
def test_partial_cancellation_rank_formula_and_witness(U):
    base = AffineRelations(7, 2)
    base.add([1, 0], 3)
    B, rhs = [[0, 1], [1, 1]], [4, 0]
    result = cancel_outside(base, B, U, rhs)
    full = AffineRelations(7, 2+len(U[0]))
    full.add([1, 0]+[0]*len(U[0]), 3)
    for b, u, value in zip(B, U, rhs):
        full.add(b+u, value)
    assert result['rank_gain'] == full.rank-result['outside_rank']-base.rank
    assert result['rank_gain'] == (0 if len(U[0]) else 1)
    for record in result['cancellations']:
        w = record['partial_row_weights']
        assert all(sum(w[i]*U[i][j] for i in range(2)) % 7 == 0 for j in range(len(U[0])))
        assert record['rhs'] == sum(w[i]*rhs[i] for i in range(2)) % 7


def test_outside_cycle_adds_base_information():
    base = AffineRelations(7, 2)
    result = cancel_outside(base, [[1, 0], [0, 1]], [[1], [-1]], [3, 4])
    assert result['outside_rank'] == 1 and result['rank_gain'] == 1
    assert base.rank == 0


def test_empty_zero_columns_and_invalid_shapes():
    empty = AffineRelations(7, 0)
    assert not empty.add([], 0)
    assert empty.identify([]).value == 0 and empty.kernel() == []
    assert cancel_outside(empty, [], [], [])['rank_gain'] == 0
    for modulus in [1, 4, 9]:
        with pytest.raises(ValueError):
            AffineRelations(modulus, 2)
    with pytest.raises(ValueError):
        AffineRelations(7, 2).add([1], 0)
    with pytest.raises(ValueError):
        cancel_outside(AffineRelations(7, 2), [[1, 2]], [], [0])
    assert rank_per_cost(0, 0) is None
    assert rank_per_cost(0, 2) == 0
    assert rank_per_cost(2, 4) == rank_per_cost(1, 2)


def test_target_recovery_without_individual_logs():
    curve = Curve(101, 2, 21, 107)
    P = curve.lift_x(0)
    # This fixture's order is independently recounted here, not assumed.
    order = 1+sum(1 if curve.rhs(x) == 0 else 2 if curve.lift_x(x) else 0 for x in range(101))
    system = AffineRelations(order, 2)
    system.add([1, 1], 12)
    assert not system.identify([1, 0]).identifiable
    Q = curve.mul(12, P)
    assert recover_target(curve, P, Q, system, [1, 1])['scalar'] == 12
    assert recover_target(curve, P, Q, system, [1, 0]) is None
    with pytest.raises(ValueError, match='verification'):
        recover_target(curve, P, curve.mul(13, P), system, [1, 1])
    with pytest.raises(ValueError, match='zero target'):
        recover_target(curve, P, Q, system, [1, 1], target_coefficient=order)


def test_retained_matrix_cli():
    result = analyze(dict(modulus=7, columns=2, rows=[[1, 1]], rhs=[3],
                          targets=[[1, 1], [1, 0]]))
    assert result['nullity'] == 1
    assert result['targets'][0]['value'] == 3
    assert result['targets'][1]['value'] is None

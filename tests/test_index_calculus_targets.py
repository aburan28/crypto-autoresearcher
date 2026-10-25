"""Exact workload and cost-accounting controls for repeated-base IC targets."""

import random

import pytest

from crypto_autoresearcher.index_calculus import Curve, generate_prime_order_curve
from crypto_autoresearcher.index_calculus import solver
from crypto_autoresearcher.index_calculus.targets import FixedBaseMultiplier


@pytest.fixture(scope="module")
def instance():
    E, P = generate_prime_order_curve(10, seed=4)
    return E.p, E.a, E.b, E.order, P


@pytest.mark.parametrize("window", [1, 2, 4, 8])
def test_every_scalar_and_partial_leading_window(instance, window):
    p, a, b, order, P = instance
    E = Curve(p, a, b, order)
    # A non-power-of-two bound above N tests exact scalar handling rather
    # than an implicit scalar reduction or a truncated leading digit.
    limit = order + 7
    table = FixedBaseMultiplier(E, P, limit, window)
    for scalar in range(limit):
        assert table.mul(scalar) == E.mul(scalar, P)
    for invalid in [-1, limit, limit + 1, True, 1.5]:
        with pytest.raises(ValueError, match="range"):
            table.mul(invalid)


def test_identity_and_zero_only_tables(instance):
    p, a, b, order, P = instance
    E = Curve(p, a, b, order)
    table = FixedBaseMultiplier(E, None, order)
    assert all(table.mul(k) is None for k in [0, 1, order - 1])
    assert table.coordinate_bytes == 0
    empty = FixedBaseMultiplier(E, P, 1)
    assert empty.mul(0) is None
    assert empty.entries == 0


@pytest.mark.parametrize("window", [0, 9, True, 2.5])
def test_window_is_bounded(instance, window):
    p, a, b, order, P = instance
    with pytest.raises(ValueError, match="window"):
        FixedBaseMultiplier(Curve(p, a, b, order), P, order, window)


@pytest.mark.parametrize("m,engine,harvest", [(2, "enumerate", "off"),
                                             (3, "mitm", "off"),
                                             (3, "mitm", "census"),
                                             (3, "mitm", "on")])
def test_identical_targets_relations_and_solution(instance, monkeypatch, m, engine, harvest):
    p, a, b, order, P = instance
    reference_decompose = solver.decompose
    traces = []

    def recording(E, fb, target, *args, **kwargs):
        relation = reference_decompose(E, fb, target, *args, **kwargs)
        traces[-1].append((target, relation))
        return relation

    monkeypatch.setattr(solver, "decompose", recording)
    results = []
    for target_engine in ("reference", "fixed_window"):
        E = Curve(p, a, b, order)
        k = random.Random("ic fixed target control").randrange(1, order)
        Q = E.mul(k, P)
        traces.append([])
        result = solver.solve_index_calculus(
            E, P, Q, m=m, engine=engine, seed=7, harvest=harvest,
            table_arity=2 if m == 3 else None, accelerate=False,
            target_engine=target_engine, max_attempts=10 * order)
        assert result.verified and result.k == k and E.mul(result.k, P) == Q
        results.append(result)
    old, new = results
    assert traces[0] == traces[1]
    for field in ("k", "factor_base", "relations", "rank", "attempts",
                  "s3_solves", "membership_tests", "la_ops", "table_entries"):
        assert getattr(old, field) == getattr(new, field)
    assert old.group_ops - old.target_ops == new.group_ops - new.target_ops
    if new.attempts:
        setup_curve = Curve(p, a, b, order)
        tables = [FixedBaseMultiplier(setup_curve, point, order) for point in (P, Q)]
        assert new.target_setup_ops == setup_curve.ops.group_ops
        assert new.target_table_entries == sum(t.entries for t in tables)
        assert new.target_table_coordinate_bytes == sum(t.coordinate_bytes for t in tables)
        assert new.target_ops >= new.target_setup_ops > 0
    assert old.target_setup_ops == old.target_table_entries == 0


def test_table_only_does_not_allocate_target_tables(instance):
    p, a, b, order, P = instance
    E = Curve(p, a, b, order)
    result = solver.solve_index_calculus(
        E, P, E.mul(9, P), m=3, engine="mitm", table_arity=2,
        harvest="table", accelerate=False, target_engine="fixed_window")
    assert result.attempts == result.target_ops == result.target_setup_ops == 0
    assert result.target_table_entries == result.target_table_coordinate_bytes == 0
    assert result.seconds_target_setup == 0


@pytest.mark.parametrize("kwargs", [{"target_engine": "unknown"}, {"target_window": 9}])
def test_solver_rejects_invalid_target_configuration(instance, kwargs):
    p, a, b, order, P = instance
    with pytest.raises(ValueError, match="target"):
        solver.solve_index_calculus(Curve(p, a, b, order), P, P, **kwargs)

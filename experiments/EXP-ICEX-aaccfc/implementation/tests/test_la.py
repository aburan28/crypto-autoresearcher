"""Stage-3 LA correctness on small planted systems over Z/q."""

import random

import pytest

import audit
import la
from arith import Cost

Q = 60821  # the b16-s21 group order (prime)


def planted(nrows, ncols, q, density, seed, dense_last=True):
    rnd = random.Random(seed)
    x = [rnd.randrange(q) for _ in range(ncols)]
    rows, rhs = [], []
    for _ in range(nrows):
        row = {}
        for j in range(ncols):
            if rnd.random() < density or (dense_last and j == ncols - 1):
                row[j] = rnd.randrange(1, q)
        if not row:
            row[rnd.randrange(ncols)] = 1
        rows.append(row)
        rhs.append(sum(c * x[j] for j, c in row.items()) % q)
    return rows, rhs, x


def dl(t, i):
    return 1 + (1000003 * (t + 1) + 7919 * i) % (Q - 1)


def _check_log(log, cost):
    em = sum(audit.la_step_expected(s)[0] for s in log)
    ei = sum(audit.la_step_expected(s)[1] for s in log)
    assert all(audit.la_step_expected(s) == (s["la_mul"], s["la_inv"]) for s in log)
    assert (em, ei) == (cost.la_mul, cost.la_inv)


@pytest.mark.parametrize("seed", range(6))
def test_planted_solution_recovered(seed):
    rows, rhs, x = planted(18, 8, Q, 0.35, seed)
    ref = la.gauss_reference(rows, rhs, 8, Q)
    if ref is None:
        pytest.skip("random system not full rank")
    cost, log = Cost(), []
    sol, info = la.solve(rows, rhs, 8, Q, cost, log, dl)
    assert sol == x == ref
    _check_log(log, cost)


def test_sge_singleton_and_merge_paths_exercised():
    # column 0 only in row 0 (singleton); column 1 in exactly two rows (merge);
    # columns 2..5 dense enough to leave a Lanczos core.
    x = [11, 22, 33, 44, 55, 66]
    rows = [{0: 3, 2: 1, 3: 5}, {1: 2, 2: 7, 4: 1}, {1: 9, 3: 4, 5: 2},
            {2: 1, 3: 1, 4: 1, 5: 1}, {2: 5, 3: 2, 4: 7, 5: 3}, {2: 8, 3: 3, 4: 1, 5: 9},
            {2: 2, 3: 9, 4: 4, 5: 5}, {2: 6, 3: 6, 4: 3, 5: 1}]
    rhs = [sum(c * x[j] for j, c in r.items()) % Q for r in rows]
    cost, log = Cost(), []
    sol, info = la.solve(rows, rhs, 6, Q, cost, log, dl)
    steps = [s["step"] for s in log]
    assert "sge_singleton" in steps and "sge_merge" in steps and "lanczos_iter" in steps and "backsub" in steps
    assert sol == x
    _check_log(log, cost)


def test_inconsistent_system_fails():
    rows, rhs, x = planted(14, 6, Q, 0.5, 99)
    rhs[3] = (rhs[3] + 1) % Q
    with pytest.raises(la.LAFailure):
        la.solve(rows, rhs, 6, Q, Cost(), [], dl)


def test_rank_tracker_counts_and_rank():
    cost, log = Cost(), []
    rt = la.RankTracker(4, Q, cost, log)
    assert rt.add({0: 1, 1: 2})
    assert not rt.add({0: 2, 1: 4})
    assert rt.add({2: 5, 3: 1})
    assert rt.add({0: 1, 3: 7})
    assert rt.add({1: 1})
    assert rt.rank == 4
    assert not rt.add({0: 3, 1: 1, 2: 4, 3: 1})
    _check_log(log, cost)


def test_lanczos_breakdown_retries_small_field():
    q = 7
    rows, rhs, x = planted(12, 5, q, 0.6, 3)
    if la.gauss_reference(rows, rhs, 5, q) is None:
        pytest.skip("not full rank")
    cost, log = Cost(), []

    def d(t, i):
        return 1 + (3 * t + 5 * i) % (q - 1)
    try:
        sol, info = la.solve(rows, rhs, 5, q, cost, log, d, max_tries=32)
        assert sol == x
    except la.LAFailure:
        pass  # a failure is reported, never a wrong answer
    _check_log(log, cost)

"""Tests for crypto_autoresearcher.index_calculus (ECDLP index calculus over F_p)."""

from __future__ import annotations

import itertools
import json
import math
import random
import statistics

import pytest

from crypto_autoresearcher.index_calculus import (
    FactorBase,
    TailTable,
    default_table_arity,
    generate_prime_order_curve,
    pollard_rho,
    solve_index_calculus,
)
from crypto_autoresearcher.index_calculus import msolve as ms
from crypto_autoresearcher.index_calculus import polyfp
from crypto_autoresearcher.index_calculus.__main__ import main
from crypto_autoresearcher.index_calculus.curve import (
    divisors,
    factorize,
    is_probable_prime,
    primitive_root,
    sqrt_mod,
)
from crypto_autoresearcher.index_calculus.decompose import (
    DecompStats,
    canonical,
    decompose,
    decompose_all,
)
from crypto_autoresearcher.index_calculus.factor_base import (
    build_factor_base,
    default_fb_size,
    subgroup_prime_filter,
)
from crypto_autoresearcher.index_calculus.linalg import EliminationState
from crypto_autoresearcher.index_calculus.semaev import s3, s3_roots
from crypto_autoresearcher.index_calculus.stats import bootstrap_slope

KINDS = ("small_x", "random", "subgroup")


@pytest.fixture(scope="module")
def curve14():
    return generate_prime_order_curve(14, seed=3)


@pytest.fixture(scope="module")
def curve10():
    return generate_prime_order_curve(10, seed=1, p_filter=subgroup_prime_filter([], sizes=[8]))


def _planted(E, fb, m, rng):
    R = None
    for _ in range(m):
        F = rng.choice(fb.points)
        R = E.add(R, F if rng.random() < 0.5 else E.neg(F))
    return R


def _hard_targets(E, fb, m, count, seed):
    """Random points, planted sums of m base points, points of +/-F, and sums
    of m - 1 and m - 2 base points (whose decompositions contain F - F)."""
    rng = random.Random(seed)
    out = []
    while len(out) < count:
        kind = len(out) % 5
        if kind == 0:
            R = E.random_point(rng)
        else:
            R = None
            for _ in range(max(1, (m, 1, m - 1, m - 2)[kind - 1])):
                F = rng.choice(fb.points)
                R = E.add(R, F if rng.random() < 0.5 else E.neg(F))
        if R is not None:
            out.append(R)
    return out


def _targets(E, fb, m, count, seed):
    """Half planted sums of m base points, half random points; none in +/-F."""
    rng = random.Random(seed)
    xs = {Q[0] for Q in fb.points}
    out = []
    while len(out) < count:
        R = _planted(E, fb, m, rng) if len(out) % 2 else E.random_point(rng)
        if R is not None and R[0] not in xs:
            out.append(R)
    return out


# -- arithmetic ---------------------------------------------------------------------

def test_curve_order_is_certified_prime(curve14):
    E, P = curve14
    assert is_probable_prime(E.order)
    assert E.order != E.p
    assert E.a % E.p and E.b % E.p
    assert E.is_on_curve(P)
    assert E.mul(E.order, P) is None


def test_generation_is_deterministic():
    E1, P1 = generate_prime_order_curve(12, seed=7)
    E2, P2 = generate_prime_order_curve(12, seed=7)
    assert (E1.p, E1.a, E1.b, E1.order, P1) == (E2.p, E2.a, E2.b, E2.order, P2)


def test_sqrt_mod_both_residue_classes():
    for p in (10007, 10009, 65537):  # p = 3 mod 4 and p = 1 mod 4
        for n in range(1, 200):
            r = sqrt_mod(n, p)
            if r is not None:
                assert r * r % p == n


def test_factorize_divisors_primitive_root():
    for n in (2, 12, 97, 360, 65520, 2**16 + 1, 999_983 * 12):
        f = factorize(n)
        assert math.prod(q**e for q, e in f.items()) == n
        assert all(is_probable_prime(q) for q in f)
        if n < 10**5:
            assert divisors(n) == [d for d in range(1, n + 1) if n % d == 0]
    for p in (101, 10007, 65521):
        g = primitive_root(p)
        assert len({pow(g, k, p) for k in range(p - 1)}) == p - 1


def test_s3_vanishes_on_sums_and_roots_recover_them(curve14):
    E, _ = curve14
    rng = random.Random(1)
    for _ in range(200):
        A, B = E.random_point(rng), E.random_point(rng)
        C = E.add(A, B)
        if C is None:
            continue
        assert s3(E, A[0], B[0], C[0]) == 0
        assert C[0] in s3_roots(E, A[0], B[0])


def test_s3_nonzero_on_random_triples(curve14):
    E, _ = curve14
    rng = random.Random(2)
    hits = sum(s3(E, rng.randrange(E.p), rng.randrange(E.p), rng.randrange(E.p)) == 0
               for _ in range(500))
    assert hits < 10


def test_polyfp_roots():
    p = 10007
    rng = random.Random(3)
    irreducible = next([c, 0, 1] for c in range(1, p) if sqrt_mod(-c, p) is None)
    for _ in range(40):
        rs = sorted({rng.randrange(p) for _ in range(rng.randrange(0, 9))})
        f = polyfp.mul(polyfp.from_roots(rs, p), irreducible, p)
        f = polyfp.mul(f, polyfp.from_roots(rs[:2], p), p)  # repeated roots too
        assert polyfp.roots(f, p) == rs


# -- factor bases -------------------------------------------------------------------

@pytest.mark.parametrize("kind", KINDS)
def test_factor_base_points_on_curve_one_per_pair(curve14, kind):
    E, _ = curve14
    fb = build_factor_base(E, kind, 30)
    assert len(fb) > 0 and fb.p == E.p
    xs = [P[0] for P in fb.points]
    assert len(set(xs)) == len(xs)
    assert all(E.is_on_curve(P) for P in fb.points)
    if kind == "subgroup":
        d, g = fb.params["d"], fb.params["coset"]
        assert (E.p - 1) % d == 0
        assert all(pow(x, d, E.p) == pow(g, d, E.p) for x in xs)


@pytest.mark.parametrize("kind", KINDS)
def test_membership_poly_vanishes_on_the_base(curve14, kind):
    E, _ = curve14
    fb = build_factor_base(E, kind, 20)
    f = fb.membership_poly()
    dense = [f.get(e, 0) for e in range(max(f) + 1)]
    assert all(polyfp.evaluate(dense, P[0], E.p) == 0 for P in fb.points)
    if kind == "subgroup":
        assert len(f) == 2 and max(f) == fb.params["d"]
    else:
        assert max(f) == len(fb)


def test_subgroup_prime_filter_makes_the_base_fair():
    pf = subgroup_prime_filter([2, 3], tolerance=0.15)
    E, _ = generate_prime_order_curve(18, seed=4, p_filter=pf)
    assert pf(E.p)
    E2, _ = generate_prime_order_curve(18, seed=4, p_filter=pf)
    assert (E.p, E.a, E.b) == (E2.p, E2.a, E2.b)
    for m in (2, 3):
        target = default_fb_size(E.order, m)
        d = build_factor_base(E, "subgroup", target).params["d"]
        assert abs(d - 2 * target) <= 0.15 * 2 * target + 2


# -- decomposition ------------------------------------------------------------------

@pytest.mark.parametrize("m", [2, 3])
def test_decomposition_is_verified_sum(curve14, m):
    E, _ = curve14
    fb = FactorBase.small_x(E, 40)
    rng = random.Random(m)
    found = 0
    for _ in range(60):
        R = E.random_point(rng)
        rel = decompose(E, fb, R, m)
        if rel is None:
            continue
        found += 1
        S = None
        for i, s in rel:
            S = E.add(S, fb.points[i] if s > 0 else E.neg(fb.points[i]))
        assert S == R and len(rel) == m
    assert found > 0


@pytest.mark.parametrize("m", [2, 3])
@pytest.mark.parametrize("kind", KINDS)
def test_decompose_all_matches_brute_force(curve10, kind, m):
    E, _ = curve10
    fb = build_factor_base(E, kind, 8)
    signed = [(i, s) for i in range(len(fb)) for s in (1, -1)]
    for R in _targets(E, fb, m, 12, seed=m):
        brute = set()
        for combo in itertools.combinations_with_replacement(signed, m):
            S = None
            for i, s in combo:
                S = E.add(S, fb.points[i] if s > 0 else E.neg(fb.points[i]))
            if S == R:
                brute.add(canonical(list(combo)))
        assert decompose_all(E, fb, R, m, accelerate=False) == sorted(brute)


def test_elimination_recovers_known_k():
    N, k = 101, 37
    rng = random.Random(0)
    logs = [rng.randrange(N) for _ in range(5)]
    la = EliminationState(N)
    got = None
    while got is None:
        i, j = rng.sample(range(5), 2)
        b = rng.randrange(1, N)
        a = (logs[i] + logs[j] - b * k) % N
        got = la.add_row({i: 1, j: 1}, -b, a)
    assert got == k


# -- meet in the middle: tables of tails ----------------------------------------------

def _tail_sum(E, fb, tail):
    S = None
    for i, s in tail:
        S = E.add(S, fb.points[i] if s > 0 else E.neg(fb.points[i]))
    return S


@pytest.mark.parametrize("h", [2, 3])
def test_tail_table_holds_exactly_the_reachable_tails(curve10, h):
    E, _ = curve10
    fb = build_factor_base(E, "random", 8)
    n = len(fb)
    tab = TailTable(E, fb, h, accelerate=False)
    got = set()
    for x, c in tab._map.items():
        for code in ([c] if type(c) is int else c):
            y = E.lift_x(x)[1]
            tail = tab.orient(code, y)
            assert _tail_sum(E, fb, tail) == (x, y)
            assert tail[0][1] == 1 or tab.orient(code, E.p - y)[0][1] == 1
            got.add(tuple(tab.orient(code, y)))
    # every ordering with non-decreasing indices whose suffixes all have a
    # non-zero sum, one of each +/- pair
    signed = [(i, s) for i in range(n) for s in (1, -1)]
    want = set()
    for tail in itertools.product(signed, repeat=h):
        if any(tail[k][0] > tail[k + 1][0] for k in range(h - 1)) or tail[0][1] < 0:
            continue
        sums = [_tail_sum(E, fb, tail[k:]) for k in range(h)]
        if all(S is not None for S in sums):
            want.add(tuple(tail) if sums[0][1] == E.lift_x(sums[0][0])[1]
                     else tuple((i, -s) for i, s in tail))
    assert got == want and tab.entries == len(want)
    if h == 2:
        assert tab.entries == n * n and tab.s3_solves == n * (n + 1) // 2


@pytest.mark.parametrize("h", [2, 3])
def test_tail_table_numpy_build_is_identical(h):
    pytest.importorskip("numpy")
    E, _ = generate_prime_order_curve(20, 5)
    fb = build_factor_base(E, "small_x", 40)
    a, b = TailTable(E, fb, h, accelerate=False), TailTable(E, fb, h, accelerate=True)
    assert a._map == b._map
    assert (a.entries, a.s3_solves) == (b.entries, b.s3_solves)


def _reachable(E, fb, m):
    """sum -> the decompositions the search reaches, by brute force.

    The search visits orderings with non-decreasing indices and abandons one
    whose remainder is the point at infinity, so a decomposition is reached
    when some such ordering has a non-zero sum on every suffix of length
    2 .. m - 1.  Off the sums of fewer than m base points that is every
    decomposition; on them it leaves out orders that cancel F - F last.
    """
    signed = [(i, s) for i in range(len(fb)) for s in (1, -1)]
    out: dict = {}
    for combo in itertools.product(signed, repeat=m):
        if any(combo[k][0] > combo[k + 1][0] for k in range(m - 1)):
            continue
        sums = [_tail_sum(E, fb, combo[k:]) for k in range(m - 1)]
        if all(S is not None for S in sums):
            out.setdefault(sums[0], set()).add(canonical(list(combo)))
    return out


@pytest.mark.parametrize("m", [3, 4])
@pytest.mark.parametrize("kind", KINDS)
def test_table_search_matches_brute_force(curve10, kind, m):
    E, _ = curve10
    fb = build_factor_base(E, kind, 8)
    reach = _reachable(E, fb, m)
    tables = [None] + [TailTable(E, fb, h) for h in range(2, m)]
    for R in _hard_targets(E, fb, m, 20, seed=10 + m):
        for tab in tables:
            assert decompose_all(E, fb, R, m, table=tab) == sorted(reach.get(R, ()))


@pytest.mark.parametrize("m", [3, 4, 5])
@pytest.mark.parametrize("kind", KINDS)
def test_table_search_finds_what_enumeration_finds(curve10, kind, m):
    """Same relation first, same set in all, on every kind of target -- including
    the ones on the base and the sums of fewer points, whose decompositions
    contain cancelling pairs and are reached only in some orders."""
    E, _ = curve10
    fb = build_factor_base(E, kind, 8)
    tables = [TailTable(E, fb, h) for h in range(2, m)]
    for R in _hard_targets(E, fb, m, 20, seed=m):
        one = decompose(E, fb, R, m, accelerate=False)
        every = decompose_all(E, fb, R, m, accelerate=False)
        for tab in tables:
            st = DecompStats()
            assert decompose(E, fb, R, m, st, accelerate=False, table=tab) == one
            assert decompose_all(E, fb, R, m, accelerate=False, table=tab) == every
            assert st.successes == (one is not None)


@pytest.mark.parametrize("m,h,size", [(3, 2, 90), (4, 2, 60), (5, 3, 50)])
def test_table_search_accelerated_is_identical(m, h, size):
    """The numpy scan with a table (the m = h + 1 level and the m = h + 2 block
    pass) changes nothing: relations, S_3 solves, lookups and group ops."""
    pytest.importorskip("numpy")
    E, _ = generate_prime_order_curve(20, 5, p_filter=subgroup_prime_filter([], sizes=[size]))
    fb = build_factor_base(E, "small_x", size)
    tab = TailTable(E, fb, h)
    for t, R in enumerate(_hard_targets(E, fb, m, 10, seed=size)):
        results = []
        for accelerate in (False, True):
            for fn in (decompose, decompose_all) if t < 3 else (decompose,):
                stats = DecompStats()
                E.ops.group_ops = 0
                rel = fn(E, fb, R, m, stats, accelerate=accelerate, table=tab)
                results.append((rel, stats, E.ops.group_ops))
        half = len(results) // 2
        assert results[:half] == results[half:]
    if m == 3:  # and against the exhaustive search, which is affordable here
        for R in _hard_targets(E, fb, m, 5, seed=1):
            assert decompose(E, fb, R, m, table=tab) == decompose(E, fb, R, m)


def test_table_arguments_are_checked(curve10):
    E, _ = curve10
    fb = build_factor_base(E, "small_x", 8)
    R = E.random_point(random.Random(0))
    with pytest.raises(ValueError, match="needs m > 3"):
        decompose(E, fb, R, 3, table=TailTable(E, fb, 3))
    other = build_factor_base(E, "random", 8)
    with pytest.raises(ValueError, match="different factor base"):
        decompose(E, fb, R, 3, table=TailTable(E, other, 2))
    # arity 1 is the factor base itself: the exhaustive search, nothing built
    one = TailTable(E, fb, 1)
    assert one.entries == len(fb) and one.s3_solves == 0
    assert decompose_all(E, fb, R, 3, table=one) == decompose_all(E, fb, R, 3)
    assert [default_table_arity(m) for m in range(2, 8)] == [1, 2, 2, 3, 3, 4]


@pytest.mark.parametrize("m,kind", [(3, "small_x"), (3, "subgroup"), (4, "random")])
def test_mitm_engine_makes_the_same_run_for_less(curve14, m, kind):
    E, P = curve14
    k = 4242 % E.order
    Q = E.mul(k, P)
    runs = {eng: solve_index_calculus(E, P, Q, m=m, fb_kind=kind, seed=1, engine=eng)
            for eng in ("enumerate", "mitm")}
    a, b = runs["enumerate"], runs["mitm"]
    assert a.verified and b.verified and b.k == k
    same = ("k", "relations", "attempts", "rank", "target_ops", "la_ops", "factor_base")
    assert all(getattr(a, f) == getattr(b, f) for f in same)
    assert (a.table_arity, a.table_s3_solves) == (1, 0)
    assert b.table_arity == default_table_arity(m) and b.table_s3_solves > 0
    assert b.table_s3_solves < b.s3_solves < a.s3_solves  # the table is charged
    with pytest.raises(ValueError, match="mitm engine"):
        solve_index_calculus(E, P, Q, m=m, engine="enumerate", table_arity=2)
    with pytest.raises(ValueError, match="table_arity must be"):
        solve_index_calculus(E, P, Q, m=m, engine="mitm", table_arity=m)


# -- the vectorised scan --------------------------------------------------------------

def test_batch_inverse():
    np = pytest.importorskip("numpy")
    from crypto_autoresearcher.index_calculus._accel import batch_inverse

    for p in (10007, 4294967291):
        rng = random.Random(p)
        for n in (1, 2, 3, 7, 64, 1001):
            v = np.array([rng.randrange(1, p) for _ in range(n)], dtype=np.uint64)
            inv = batch_inverse(v, np.uint64(p))
            assert all(int(a) * int(b) % p == 1 for a, b in zip(v, inv))


@pytest.mark.parametrize("m,size", [(2, 300), (3, 90)])
@pytest.mark.parametrize("kind", KINDS)
def test_accelerated_path_is_identical(kind, m, size):
    pytest.importorskip("numpy")
    E, _ = generate_prime_order_curve(20, 5, p_filter=subgroup_prime_filter([], sizes=[size]))
    fb = build_factor_base(E, kind, size)
    for t, R in enumerate(_targets(E, fb, m, 16, seed=size)):
        results = []
        for accelerate in (False, True):
            stats = DecompStats()
            E.ops.group_ops = 0
            rel = decompose(E, fb, R, m, stats, accelerate=accelerate)
            results.append((rel, stats, E.ops.group_ops))
        assert results[0] == results[1]
        if t < 4:
            alls = []
            for accelerate in (False, True):
                stats = DecompStats()
                E.ops.group_ops = 0
                alls.append((decompose_all(E, fb, R, m, stats, accelerate=accelerate),
                             stats, E.ops.group_ops))
            assert alls[0] == alls[1]


# -- msolve -----------------------------------------------------------------------------

T2 = """[0, [101,
3,
3,
['x1', 'x2', 'x3'],
[0, 0, 1],
[1,
[[3,
[95, 11, 95, 1]],
[0,
[1]],
[
[[2,
[0, 0, 100]]],
[[1,
[100, 98]]]
]]]]]:"""


def test_msolve_parse_output():
    # x3 in {1, 2, 3}, x1 = x3^2, x2 = 3 x3 + 1 over F_101
    run = ms.parse_output(T2, ["x1", "x2", "x3"], 101)
    assert run.status == "ok" and run.degree == 3
    assert sorted(run.solutions) == [[1, 4], [4, 7], [9, 10]]
    assert ms.parse_output("[-1]:", ["x1", "z"], 101).status == "no_solution"
    assert ms.parse_output("[1, 2, -1, []]:", ["x1", "z"], 101).status == \
        "positive_dimensional"
    assert ms.parse_output("", ["x1", "z"], 101).status == "failed"
    # a parametrization in anything but the last variable is not trusted
    assert ms.parse_output(T2.replace("[0, 0, 1]", "[1, 0, 1]"),
                           ["x1", "x2", "x3"], 101).status == "unexpected"


@pytest.mark.parametrize("m", [2, 3, 4])
def test_msolve_system_vanishes_at_a_planted_decomposition(curve14, m):
    E, _ = curve14
    fb = build_factor_base(E, "small_x", 12)
    rng = random.Random(m)
    idx = [rng.randrange(len(fb)) for _ in range(m)]
    pts = [fb.points[i] if rng.random() < 0.5 else E.neg(fb.points[i]) for i in idx]
    partial, us = pts[0], []
    for Q in pts[1:-1]:
        partial = E.add(partial, Q)
        us.append(partial[0])
    R = E.add(partial, pts[-1])
    system = ms.decomposition_system(E, fb, R[0], m, random.Random(0))
    values = [P[0] for P in pts] + us
    form = system.polys[-1]
    z = (-sum(c * values[exps.index(1)] for exps, c in form.items() if exps[-1] == 0)) % E.p
    for poly in system.polys:
        assert ms.evaluate(poly, values + [z], E.p) == 0
    assert "(" not in system.render() and "^0" not in system.render()


needs_msolve = pytest.mark.skipif(not ms.available(), reason="msolve not installed")


@needs_msolve
@pytest.mark.parametrize("m", [2, 3])
@pytest.mark.parametrize("kind", KINDS)
def test_msolve_engine_agrees_with_enumeration(kind, m):
    E, _ = generate_prime_order_curve(14, 2, p_filter=subgroup_prime_filter([], sizes=[8]))
    fb = build_factor_base(E, kind, 8)
    agreed = 0
    for R in _targets(E, fb, m, 8, seed=m):
        out = ms.decompose_msolve(E, fb, R, m, timeout=120)
        assert out.status in ("ok", "no_solution"), out
        assert out.relations == decompose_all(E, fb, R, m)
        agreed += bool(out.relations)
    assert agreed > 0  # the planted targets exercise non-empty answers


@needs_msolve
def test_msolve_refuses_large_primes(curve14):
    E, _ = generate_prime_order_curve(18, 0)
    fb = build_factor_base(E, "small_x", 6)
    with pytest.raises(ValueError, match="msolve bound"):
        ms.decompose_msolve(E, fb, E.random_point(random.Random(0)), 2)


@needs_msolve
def test_index_calculus_with_the_msolve_engine():
    E, P = generate_prime_order_curve(12, 1)
    Q = E.mul(777, P)
    res = solve_index_calculus(E, P, Q, m=2, fb_kind="small_x", engine="msolve", seed=1)
    assert res.verified and res.k == 777 % E.order
    assert res.msolve_calls >= res.attempts - res.censored_attempts


# -- end to end ---------------------------------------------------------------------

@pytest.mark.parametrize("m,fb", [(2, "small_x"), (2, "subgroup"), (2, "random"),
                                  (3, "small_x")])
def test_index_calculus_solves_and_verifies(curve14, m, fb):
    E, P = curve14
    k = 4242 % E.order
    Q = E.mul(k, P)
    res = solve_index_calculus(E, P, Q, m=m, fb_kind=fb, seed=1)
    assert res.verified and res.k == k
    assert res.relations >= 1 and res.s3_solves > 0
    assert 0 < res.target_ops <= res.group_ops


def test_rho_solves_and_separates_setup(curve14):
    E, P = curve14
    Q = E.mul(1234, P)
    rr = pollard_rho(E, P, Q, seed=1)
    assert rr.verified and rr.k == 1234 % E.order
    assert rr.group_ops == rr.walk_ops + rr.setup_ops and rr.walk_ops > 0


def test_rho_walk_is_square_root_sized():
    E, P = generate_prime_order_curve(20, 3)
    walks = []
    for seed in range(12):
        rr = pollard_rho(E, P, E.mul(1000 + seed, P), seed=seed)
        assert rr.verified
        walks.append(rr.walk_ops)
    ratio = statistics.mean(walks) / math.sqrt(math.pi * E.order / 2)
    assert 0.4 < ratio < 2.5


def test_bootstrap_slope_of_an_exact_line():
    xs = [10, 10, 12, 12, 14, 14]
    fit = bootstrap_slope(xs, [0.5 * x + 3 for x in xs], reps=200)
    assert fit["slope"] == pytest.approx(0.5)
    assert fit["lo"] == pytest.approx(0.5) and fit["hi"] == pytest.approx(0.5)


# -- command line ---------------------------------------------------------------------

def _without_times(rows):
    return sorted((json.dumps({k: v for k, v in r.items() if k != "seconds"}, sort_keys=True)
                   for r in rows))


def test_cli_sweep_is_deterministic_across_workers(tmp_path, capsys):
    outs = []
    for workers in (1, 2):
        out = tmp_path / f"w{workers}.jsonl"
        assert main(["sweep", "--bits", "10", "12", "--curves", "1", "--rho-curves", "2",
                     "--m", "2", "--fb", "small_x", "subgroup", "--workers", str(workers),
                     "--out", str(out), "--quiet", "--reps", "50"]) == 0
        outs.append([json.loads(line) for line in out.read_text().splitlines()])
    assert _without_times(outs[0]) == _without_times(outs[1])
    assert {r["method"] for r in outs[0]} == {"rho", "ic_m2"}
    # all bases in a cell share the subgroup base's size
    ic = [r for r in outs[0] if r["method"] == "ic_m2"]
    for bits in (10, 12):
        assert len({r["fb_size"] for r in ic if r["bits"] == bits}) == 1


def test_cli_sweep_runs_both_engines(tmp_path, capsys):
    out = tmp_path / "rows.jsonl"
    assert main(["sweep", "--bits", "12", "14", "--curves", "1", "--m", "3",
                 "--engine", "enumerate", "mitm", "--m-max-bits", "enumerate:3=12",
                 "--out", str(out), "--quiet", "--reps", "50", "--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    rows = [json.loads(line) for line in out.read_text().splitlines()]
    ic = {(r["bits"], r["engine"]): r for r in rows if r["method"] == "ic_m3"}
    assert set(ic) == {(12, "enumerate"), (12, "mitm"), (14, "mitm")}  # the cap
    a, b = ic[12, "enumerate"], ic[12, "mitm"]
    assert (a["attempts"], a["relations"], a["la_ops"]) == \
        (b["attempts"], b["relations"], b["la_ops"])
    assert b["table_arity"] == 2 and 0 < b["table_s3_solves"] < b["s3_solves"] < a["s3_solves"]
    assert {"ic_m3:small_x", "ic_m3:small_x:mitm"} <= set(report["fits"])


def test_cli_analyze_reports_fits(tmp_path, capsys):
    out = tmp_path / "rows.jsonl"
    assert main(["sweep", "--bits", "10", "12", "14", "--curves", "1", "--out", str(out),
                 "--quiet", "--reps", "50"]) == 0
    capsys.readouterr()
    assert main(["analyze", str(out), "--json", "--reps", "50"]) == 0
    report = json.loads(capsys.readouterr().out)
    fits = report["sweep"]["fits"]
    assert fits["rho"]["walk_ops"]["slope"] is not None
    assert fits["ic_m2:small_x"]["s3_solves"]["slope"] is not None


@needs_msolve
def test_cli_engines_smoke(tmp_path, capsys):
    out = tmp_path / "eng.jsonl"
    assert main(["engines", "--bits", "12", "--m", "2", "--fb", "small_x", "--sizes", "4", "6",
                 "--targets", "2", "--out", str(out), "--quiet", "--reps", "50"]) == 0
    rows = [json.loads(line) for line in out.read_text().splitlines()]
    assert rows and all(r["agree"] for r in rows)

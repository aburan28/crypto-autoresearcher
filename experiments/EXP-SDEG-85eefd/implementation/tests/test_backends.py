"""Backends, decks, oracle, Semaev identities, rho on the L=8 seed-1 fixture with
'smoke' labels only (implementation tests, not measurements)."""

import pytest

import backends
import decks
import fixtures
import labels
import rho
import semaev
from fparith import Curve, Fp, OpCounter
from oracle import A5Oracle
from verify import O, VCurve

NS = labels.SMOKE_NS


@pytest.fixture(scope="module")
def env():
    fx = fixtures.fixture(8, 1)
    sem = semaev.SemaevFp(fx["p"], fx["a"], fx["b"])
    dks = decks.build_all(fx, NS)
    return fx, sem, dks


def test_semaev_degrees_and_symmetry():
    t = semaev.load_terms()
    assert t["degrees"]["S4"] == [4, 4, 4, 4] and t["degrees"]["S5"] == [8, 8, 8, 8, 8]


def test_s3_formula_matches_file(env):
    fx, sem, _ = env
    t = semaev.load_terms()
    p, a, b = fx["p"], fx["a"], fx["b"]
    for (x1, x2, x3) in [(1, 2, 3), (100, 7, 32000), (5, 5, 9)]:
        v = sum(c * a ** ea * b ** eb * x1 ** e1 * x2 ** e2 * x3 ** e3
                for ea, eb, e1, e2, e3, c in t["S3"]) % p
        assert v == semaev.s3_value(p, a, b, x1, x2, x3) == \
            semaev.s3_value_charged(Fp(p), a, b, x1, x2, x3)


def test_identity_small(env):
    fx, sem, _ = env
    r = semaev.identity_check(fx, sem, NS + "|unit", 40)
    assert r["passed"], r["failure_examples"]


def test_decks(env):
    fx, _, dks = env
    vc = VCurve(fx["p"], fx["a"], fx["b"])
    assert dks["interval_x"].size == 8 and dks["random_x"].size == 8 and dks["progression"].size == 8
    assert dks["subgroup_x"].size <= 8
    for d in dks.values():
        assert d.V == sorted(set(d.V))
        assert all(vc.liftable(x) and vc.on_curve(P) for x, P in zip(d.V, d.points))
        assert d.construction_ops["W"] > 0
    for x in dks["subgroup_x"].V:
        assert pow(x, 8, fx["p"]) == 1
    iv = dks["interval_x"].V
    assert all(not vc.liftable(x) for x in range(iv[-1]) if x not in iv)


def test_backends_agree_and_b2_matches_candidates(env):
    fx, sem, dks = env
    for name in ("interval_x", "random_x"):
        deck = dks[name]
        table = backends.ForwardTable(fx, deck, build_poly=True)
        assert table.has_inf and table.ops["mul"] > table.ops_points["mul"]
        orc = A5Oracle(fx, deck)
        for q in decks.targets(fx, deck, NS + "|unit", 2, 2):
            R = q["R"]
            r0 = backends.b0_query(fx, deck, table, R, keep_log=True)
            r1 = backends.b1_query(fx, deck, table, sem, R, keep_log=True)
            assert r0["member"] == r1["member"] == orc.member(R)
            assert sorted(r0["hit_triples"]) == sorted(r1["hit_triples"])
            assert sum(e[1] + e[2] + e[3] + e[4] for e in r1["op_log"]) == r1["W_query"]
            for h in r1["hits"]:
                assert backends.extract_and_verify(fx, deck, table, sem, R, h["triple"], h)["verified"]
            b2 = backends.b2_query(fx, deck, R)
            assert 0 < b2["elim_degree"] <= 8 * backends.n_triples(deck.size)


def test_three_sum_target_uses_infinity(env):
    """R = P0 + P1 + P2 is a member only through the forward O = P - P."""
    fx, sem, dks = env
    deck = dks["interval_x"]
    vc = VCurve(fx["p"], fx["a"], fx["b"])
    R = vc.sum_signed([(deck.points[0], 1), (deck.points[1], 1), (deck.points[2], 1)])
    table = backends.ForwardTable(fx, deck, build_poly=True)
    r0 = backends.b0_query(fx, deck, table, R)
    r1 = backends.b1_query(fx, deck, table, sem, R)
    assert r0["member"] and r1["member"] and A5Oracle(fx, deck).member(R)
    assert (0, 1, 2) in r0["hit_triples"] and (0, 1, 2) in r1["hit_triples"]
    h = [h for h in r1["hits"] if tuple(h["triple"]) == (0, 1, 2)][0]
    assert h["inf_root"]
    assert backends.extract_and_verify(fx, deck, table, sem, R, (0, 1, 2), h)["verified"]


def test_target_at_infinity(env):
    fx, sem, dks = env
    deck = dks["interval_x"]
    table = backends.ForwardTable(fx, deck, build_poly=True)
    r0 = backends.b0_query(fx, deck, table, O)
    r1 = backends.b1_query(fx, deck, table, sem, O)
    assert r0["member"] == r1["member"] == A5Oracle(fx, deck).member(O)
    assert sorted(r0["hit_triples"]) == sorted(r1["hit_triples"])


def test_rho_solves(env):
    fx, _, _ = env
    vc = VCurve(fx["p"], fx["a"], fx["b"])
    for t in range(3):
        k = labels.h(labels.cell_lab(NS + "|unit", "rho", 8, 1, t)) % fx["N"]
        out = rho.solve(fx, vc.mul(k, tuple(fx["G"])), t, NS + "|unit")
        assert out["solved"] and out["k"] == k


def test_oracle_counts(env):
    fx, _, dks = env
    orc = A5Oracle(fx, dks["interval_x"])
    assert orc.enumerated == 15504  # C(2*8 + 4, 5)

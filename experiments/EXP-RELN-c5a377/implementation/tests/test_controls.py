import math

import pytest

import fixtures
import labels
import lpgraph
import nulls
import recovery
import rho
from relgen import Generator, relations_of

NS = labels.SMOKE_NS + "|test"


@pytest.fixture(scope="module")
def observed():
    fx = fixtures.fixture(16, 11)
    gen = Generator(fx, fixtures.params(fx), NS)
    recs = [gen.attempt(j) for j in range(751)]
    rels = relations_of(recs)
    return gen, rels, lpgraph.build(rels, gen.B)


def test_rewire_preserves_degrees_and_counts(observed):
    _, _, g = observed
    deg = nulls.degree_sequence(g)
    outs = [nulls.rewire(g, NS, i, "t") for i in range(32)]
    for gr in outs:
        assert gr["n"] == g["n"] and len(gr["edges"]) == len(g["edges"])
        assert nulls.degree_sequence(gr) == deg
    assert len({tuple(sorted(gr["edges"])) for gr in outs}) > 1
    assert nulls.rewire(g, NS, 3, "t") == outs[3]  # deterministic


def test_er_has_identical_V_E_and_is_simple(observed):
    _, _, g = observed
    for i in range(32):
        ge = nulls.erdos_renyi(g["n"], len(g["edges"]), NS, i, "t")
        assert ge["n"] == g["n"] and len(ge["edges"]) == len(g["edges"])
        assert all(u != v for u, v in ge["edges"])
        assert len(set(ge["edges"])) == len(ge["edges"])
    assert nulls.erdos_renyi(3, 4, NS, 0, "t") is None


@pytest.mark.parametrize("n", [2, 5, 18, 40])
def test_planted_dense_known_positive(n):
    gp = nulls.planted_dense(n, NS, "t")
    m = lpgraph.metrics(gp, 5)
    assert m["cycle_rank"] == math.ceil(n ** 1.5) == gp["planted_cycle_rank"]
    assert m["components"] == 1


def test_planted_dense_passes_gate_on_observed(observed):
    gen, _, g = observed
    gp = nulls.planted_dense(g["n"], NS, "t")
    assert lpgraph.metrics(gp, gen.L)["delta_proof"] > 0.25


def test_treatment_recovery_verifies(observed):
    gen, rels, _ = observed
    res = recovery.recover_and_verify(rels, gen.fb_x, gen.B, gen.fx, gen.Q)
    assert res["verification_passed"] and res["inconsistent_rows"] == 0
    assert res["nontrivial_determined"] > 0


def test_scramble_is_derangement(observed):
    _, rels, _ = observed
    s = recovery.scramble(rels, NS, "t")
    assert [r["rel"] for r in s] == [r["rel"] for r in rels]
    assert sorted((r["a"], r["b"]) for r in s) == sorted((r["a"], r["b"]) for r in rels)
    assert all((x["a"], x["b"]) != (y["a"], y["b"]) for x, y in zip(s, rels))


def test_scrambled_known_false_fails_verification(observed):
    gen, rels, _ = observed
    s = recovery.scramble(rels, NS, "t")
    res = recovery.recover_and_verify(s, gen.fb_x, gen.B, gen.fx, gen.Q)
    assert recovery.known_false_outcome(res) == "fails_verification"


def test_known_false_outcome_classes():
    base = {"inconsistent_rows": 0, "verification_failures": 0, "nontrivial_determined": 0}
    assert recovery.known_false_outcome(base) == "not_exercised"
    assert recovery.known_false_outcome({**base, "nontrivial_determined": 3}) == "passes_verification"
    assert recovery.known_false_outcome({**base, "inconsistent_rows": 1}) == "fails_verification"


def test_rho_baseline_solves_and_verifies():
    fx = fixtures.fixture(16, 11)
    rs = [rho.solve(fx, t, NS) for t in range(3)]
    assert all(r["solved"] and r["k_matches_label"] for r in rs)
    s = rho.summary(rs, fx["N"])
    assert s["n_solved"] == 3 and s["mean_walk_ops_over_sqrt_q"] > 0


def test_smoke_namespace_never_frozen():
    assert labels.is_smoke_ns(NS) and not labels.is_smoke_ns(labels.FROZEN_NS)
    assert labels.target_label(labels.SMOKE_NS, 16, 11) != labels.target_label(labels.FROZEN_NS, 16, 11)

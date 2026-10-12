import copy
import random

import pytest

import audit
import fixtures
import labels
from ecarith import Curve, Fp, OpCounter, scalar_mul_charge
from relgen import Generator
from vcurve import VCurve

NS = labels.SMOKE_NS + "|test"


@pytest.fixture(scope="module")
def run():
    fx = fixtures.fixture(16, 11)
    gen = Generator(fx, fixtures.params(fx), NS)
    recs = [gen.attempt(j) for j in range(300)]
    return gen, recs


def test_scalar_mul_charge_formula():
    fx = fixtures.fixture(16, 11)
    rnd = random.Random(1)
    for _ in range(50):
        k = rnd.randrange(1, fx["N"])
        c = OpCounter()
        E = Curve(Fp(fx["p"], c), fx["a"], fx["b"])
        R = E.mul(k, tuple(fx["G"]))
        assert c.group_ops == scalar_mul_charge(k)
        assert R == VCurve(fx["p"], fx["a"], fx["b"]).mul(k, tuple(fx["G"]))


def test_every_attempt_charged_by_formula(run):
    gen, recs = run
    for r in recs:
        exp = gen.expected_attempt_group_ops(r["a"], r["b"], r["outcome"] == "R_is_O")
        assert r["group_ops"] == exp
        assert r["group_ops"] >= len(gen.S)  # the full scan is charged, hits and misses alike
        assert r["W_field"] > 0


def test_totals_are_sum_of_parts(run):
    gen, recs = run
    assert gen.counter.group_ops == gen.setup_ops["group_ops"] + sum(r["group_ops"] for r in recs)
    assert gen.counter.W_field() == gen.setup_ops["W_field"] + sum(r["W_field"] for r in recs)
    assert gen.setup_ops["W_field"] > 0  # FB/LP enumeration is charged


def test_failed_attempts_recorded(run):
    _, recs = run
    assert [r["j"] for r in recs] == list(range(300))
    assert sum(r["outcome"] == "miss" for r in recs) > 0


def test_generator_agrees_with_independent_replay(run):
    gen, recs = run
    total = gen.setup_ops["group_ops"] + sum(r["group_ops"] for r in recs)
    res = audit.audit(gen.header(), recs, len(recs), total, NS, replay_all=True)
    assert res["accepted"], res["reasons"]
    assert res["n_replayed"] == len(recs)


def test_audit_selection_is_about_ten_percent(run):
    gen, recs = run
    total = gen.setup_ops["group_ops"] + sum(r["group_ops"] for r in recs)
    res = audit.audit(gen.header(), recs, len(recs), total, NS)
    assert res["accepted"]
    assert 0.03 < res["replay_fraction"] < 0.2


def _total(gen, recs):
    return gen.setup_ops["group_ops"] + sum(r["group_ops"] for r in recs)


def test_audit_rejects_omitted_failed_attempts(run):
    gen, recs = run
    kept = [r for r in recs if r["outcome"] != "miss"]
    res = audit.audit(gen.header(), kept, len(recs), _total(gen, kept), NS)
    assert not res["accepted"]
    assert any("missing" in s for s in res["reasons"])


def test_audit_rejects_zeroed_failed_attempts(run):
    gen, recs = run
    bad = copy.deepcopy(recs)
    for r in bad:
        if r["outcome"] == "miss":
            r["group_ops"] = 0
    res = audit.audit(gen.header(), bad, len(bad), _total(gen, bad), NS)
    assert not res["accepted"]
    assert any("charged differently" in s for s in res["reasons"])


def test_audit_rejects_inflated_total_and_bad_certificate(run):
    gen, recs = run
    res = audit.audit(gen.header(), recs, len(recs), _total(gen, recs) + 1, NS)
    assert not res["accepted"]
    bad = copy.deepcopy(recs)
    hit = next(r for r in bad if r["rel"])
    hit["rel"][1] = -hit["rel"][1]
    res = audit.audit(gen.header(), bad, len(bad), _total(gen, bad), NS)
    assert not res["accepted"]
    assert res["certificate_failures"] >= 1

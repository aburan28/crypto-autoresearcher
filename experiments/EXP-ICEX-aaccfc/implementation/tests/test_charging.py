"""Charging completeness (C-3, C-5, C-6 accounting audit) and B0 fidelity."""

import json
import os
import subprocess
import sys
from math import comb

import pytest

import audit
import b0
import common
from arith import Cost, Curve, Fp
from oracle import MembershipOracle
from verify import O, VCurve

FX = common.fixture(16, 21)
FX22 = common.fixture(16, 22)


def test_c3_units():
    c = Cost()
    F = Fp(FX["p"], c)
    E = Curve(F, FX["a"], FX["b"])
    G = tuple(FX["G"])
    P2 = E.add(G, G)
    assert c.units() == 13 and c.pt_dbl == 1
    E.add(G, P2)
    assert c.units() == 26 and c.pt_add == 1
    E.add(G, E.neg(G))  # result O: still an affine addition, charged
    assert c.units() == 39
    E.add(None, G)  # identity: free
    assert c.units() == 39
    F.mul(3, 4)
    F.inv(5)
    F.probe()
    assert c.units() == 39 + 1 + 10 + 1
    assert c.pmul == 3 + 4 and c.pinv == 2  # internal field ops tallied, not charged


def test_scalar_mult_counts_match_independent_formula():
    vc = VCurve(FX["p"], FX["a"], FX["b"])
    G = tuple(FX["G"])
    for k in (1, 2, 3, 12345, FX["N"] - 1, 2 ** 15 + 7):
        c = Cost()
        E = Curve(Fp(FX["p"], c), FX["a"], FX["b"])
        R = E.mul(k, G)
        R2, ops = audit.scalar_ops(vc, k, G)
        assert R == R2 == vc.mul(k, G)
        assert c.pt_add + c.pt_dbl == ops


@pytest.mark.parametrize("fx", [FX, FX22])
@pytest.mark.parametrize("m", [5, 6, 8])
def test_b0_charges_every_probe_and_op_and_agrees_with_oracle(fx, m):
    fb = b0.interval_fb(fx, m)
    if fb.L == 0:
        pytest.skip("empty factor base")
    table = b0.ForwardTable(fx, fb)
    n = fb.L
    assert table.cost["pt_add"] + table.cost["pt_dbl"] == n * (n + 1)
    assert table.cost["probes"] == n * (n + 1)
    vc = VCurve(fx["p"], fx["a"], fx["b"])
    orc = MembershipOracle(fx, fb.points, m)
    G = tuple(fx["G"])
    members = 0
    targets = [O] + [vc.mul(common.uniform(common.lab("test", "b0", i), fx["N"]), G) for i in range(60)]
    # add planted members
    for i in range(20):
        terms = [(common.uniform(common.lab("test", "pl", i, t), n), 1 - 2 * (common.h(common.lab("test", "s", i, t)) & 1))
                 for t in range(m)]
        targets.append(vc.sum_signed([(fb.points[j], s) for j, s in terms]))
    for R in targets:
        c = Cost()
        res = b0.b0_query(fx, fb, table, R, m, c)
        ops, probes = audit.b0_expected(vc, fb.points, R, m)
        assert c.probes == probes == (2 ** (m - 2)) * comb(n + m - 3, m - 2)
        assert c.pt_add + c.pt_dbl == ops
        assert c.mul == c.inv == 0
        assert res["member"] == orc.member(R)
        if res["member"]:
            members += 1
            terms = b0.extract_relation(fx, fb, table, res["first"], c)
            assert b0.verify_relation(fx, fb, R, terms, m)
    assert members >= 20


def test_b0_m5_matches_sdeg_b0_query():
    """Stage 1 reuses B0 by reference: our generalized scan must reproduce the
    audited EXP-SDEG-85eefd b0_query (member, first hit triple, hit count, probes)."""
    fx = FX22
    fb = b0.interval_fb(fx, 5)
    table = b0.ForwardTable(fx, fb)
    vc = VCurve(fx["p"], fx["a"], fx["b"])
    G = tuple(fx["G"])
    Rs = [vc.mul(common.uniform(common.lab("test", "sdeg", i), fx["N"]), G) for i in range(30)]
    Rs += [vc.sum_signed([(fb.points[i % fb.L], 1), (fb.points[(i + 1) % fb.L], -1), (fb.points[0], 1),
                          (fb.points[(2 * i) % fb.L], 1), (fb.points[(3 * i) % fb.L], -1)]) for i in range(10)]
    script = r"""
import json, sys
sys.dont_write_bytecode = True
sys.path.insert(0, '.')
import backends
from verify import O
d = json.load(sys.stdin)
class Deck: pass
deck = Deck(); deck.points = [tuple(p) for p in d['points']]; deck.V = [p[0] for p in d['points']]
fx = d['fx']
table = backends.ForwardTable(fx, deck, build_poly=False)
out = []
for R in d['Rs']:
    R = O if R is None else tuple(R)
    r = backends.b0_query(fx, deck, table, R)
    out.append({'member': r['member'], 'first': list(r['hit_triples'][0]) if r['hit_triples'] else None,
                'n_hits': sum(len(h['hits']) for h in r['hits']), 'probes': r['ops']['probes']})
print(json.dumps(out))
"""
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    inp = json.dumps({"fx": fx, "points": [list(p) for p in fb.points],
                      "Rs": [None if R is O else list(R) for R in Rs]})
    res = subprocess.run([sys.executable, "-c", script], cwd=str(common.SDEG_DIR / "implementation"),
                         input=inp, capture_output=True, text=True, env=env)
    assert res.returncode == 0, res.stderr
    sdeg = json.loads(res.stdout)
    for R, s in zip(Rs, sdeg):
        c = Cost()
        r = b0.b0_query(fx, fb, table, R, 5, c)
        assert r["member"] == s["member"]
        assert (list(r["first"]["idx"]) if r["first"] else None) == s["first"]
        assert r["n_hits"] == s["n_hits"]
        assert c.probes == s["probes"]


def test_complete_cost_components_and_audit_accepts(smoke_primary):
    r = smoke_primary
    s1 = r["stage1"]
    assert s1["n_failed_attempts"] > 0
    log = s1["attempt_log"]
    assert 13 * sum(log["pt_ops"]) + len(log["member_bits"]) * log["probes_each"] == s1["cost"]["attempts"]["units"]
    assert len(log["member_bits"]) == s1["n_attempts"] and log["member_bits"].count("0") == s1["n_failed_attempts"]
    assert s1["units"] == (s1["cost"]["fb_construction"]["units"] + s1["cost"]["forward_table"]["units"]
                           + s1["cost"]["attempts"]["units"])
    assert r["complete_units"] == r["stage1"]["units"] + r["stage3"]["units"] + r["descents"]["units"]
    assert r["stage3"]["rank_tracking_cost"]["la_mul"] > 0 and r["stage3"]["la_cost"]["la_mul"] > 0
    for key in ("peak_rss_bytes",):
        assert r[key] > 0 and s1[key] > 0 and r["stage3"][key] > 0 and r["descents"][key] > 0
    receipt = json.loads(json.dumps({"status": "ok", "peak_rss_bytes": r["peak_rss_bytes"], "result": r}))
    a = audit.audit_cell(receipt)
    assert a["accepted"], a["failures"]
    assert a["stats"]["attempts_replayed"] > 0
    assert a["stats"]["la_steps_checked"] == len(r["stage3"]["rank_log"]) + len(r["stage3"]["la_log"])


def _receipt(r):
    return json.loads(json.dumps({"status": "ok", "peak_rss_bytes": r["peak_rss_bytes"], "result": r}))


def test_audit_rejects_omitted_failed_attempt(smoke_primary):
    rc = _receipt(smoke_primary)
    s1 = rc["result"]["stage1"]
    log = s1["attempt_log"]
    idx = log["member_bits"].index("0")
    log["member_bits"] = log["member_bits"][:idx] + log["member_bits"][idx + 1:]
    ops = log["pt_ops"].pop(idx)
    s1["cost"]["attempts"]["pt_add"] -= ops
    s1["cost"]["attempts"]["probes"] -= log["probes_each"]
    s1["cost"]["attempts"]["units"] -= 13 * ops + log["probes_each"]
    s1["n_attempts"] -= 1
    s1["n_failed_attempts"] -= 1
    assert not audit.audit_cell(rc)["accepted"]


def test_audit_rejects_zeroed_table_build(smoke_primary):
    rc = _receipt(smoke_primary)
    for k in ("pt_add", "pt_dbl", "probes", "units"):
        rc["result"]["forward_table"]["cost"][k] = 0
    assert not audit.audit_cell(rc)["accepted"]


def test_audit_rejects_missing_memory(smoke_primary):
    rc = _receipt(smoke_primary)
    rc["result"]["stage3"]["peak_rss_bytes"] = 0
    assert not audit.audit_cell(rc)["accepted"]
    rc = _receipt(smoke_primary)
    rc["peak_rss_bytes"] = None
    assert not audit.audit_cell(rc)["accepted"]


def test_audit_rejects_undercounted_la_step(smoke_primary):
    rc = _receipt(smoke_primary)
    rc["result"]["stage3"]["la_log"][1]["la_mul"] -= 1
    assert not audit.audit_cell(rc)["accepted"]


def test_audit_rejects_undercounted_attempt(smoke_primary):
    rc = _receipt(smoke_primary)
    res = rc["result"]
    log = res["stage1"]["attempt_log"]
    j = next(j for j in range(len(log["pt_ops"])) if audit.audit_selected(res["namespace"], FX, j))
    log["pt_ops"][j] -= 1
    res["stage1"]["cost"]["attempts"]["pt_add"] -= 1
    res["stage1"]["cost"]["attempts"]["units"] -= 13
    res["stage1"]["units"] -= 13
    res["complete_units_components"]["stage1"] -= 13
    res["complete_units"] -= 13
    fails = audit.audit_cell(rc)["failures"]
    assert fails and all("attempt" in f for f in fails)


def test_audit_rejects_undercounted_descent(smoke_primary):
    rc = _receipt(smoke_primary)
    res = rc["result"]
    t = res["descents"]["targets"][0]
    t["attempt_log"]["pt_ops"][0] -= 1
    t["units"] -= 13
    res["descents"]["units"] -= 13
    res["descents"]["cost"]["units"] -= 13
    res["complete_units_components"]["descents"] -= 13
    res["complete_units"] -= 13
    assert not audit.audit_cell(rc)["accepted"]


def test_audit_rejects_zeroed_probe_scan(smoke_primary):
    rc = _receipt(smoke_primary)
    s1 = rc["result"]["stage1"]
    n = s1["n_attempts"]
    pe = s1["attempt_log"]["probes_each"]
    s1["attempt_log"]["probes_each"] = 0
    s1["cost"]["attempts"]["probes"] -= n * pe
    s1["cost"]["attempts"]["units"] -= n * pe
    assert not audit.audit_cell(rc)["accepted"]

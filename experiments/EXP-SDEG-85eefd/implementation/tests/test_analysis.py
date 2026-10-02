"""C-6 metrics / C-7 mapping on SYNTHETIC data only (no experiment data)."""

import math

import numpy as np

import analysis
import audit

QS = {8: [32479, 33053, 32797], 16: [1047539, 1047701, 1047883], 32: [33563891, 33564343, 33557327]}


def synth(beta_by_backend_deck, noise=0.05, n=32, member_frac=0.5, elim_beta=None,
          sub_beta=None, seed=0, member_stop_frac=0.5):
    """Per-triple work W_triple = scale * q^beta * lognormal noise; B1 adds a
    per-query fixed term. W_full = W_triple + fixed; the primary (decision)
    W is W_full * member_stop_frac for members, W_full for non-members.
    A spec value is beta or a dict {beta, scale, fixed}. elim/sub degrees
    likewise."""
    rng = np.random.default_rng(seed)
    recs = []
    elim_beta = elim_beta or {}
    for (be, deck), spec in beta_by_backend_deck.items():
        spec = spec if isinstance(spec, dict) else {"beta": spec}
        bt, scale, fixed = spec["beta"], spec.get("scale", 1.0), spec.get("fixed", 0.0)
        for L, qs in QS.items():
            for s, q in enumerate(qs, 1):
                for j in range(n):
                    member = j < n * member_frac
                    per_triple = scale * q ** bt * math.exp(rng.normal(0, noise))
                    W_full = per_triple + fixed
                    W = W_full * member_stop_frac if member else W_full
                    recs.append(dict(fixture=f"L{L}-s{s}", L=L, seed=s, q=q, deck=deck,
                                     query_id=f"{L}-{s}-{deck}-{j}", backend=be, member=member,
                                     status="ok", W=W, W_full=W_full, W_triple=W - fixed,
                                     sub_degree=(q ** sub_beta if sub_beta is not None else 0)
                                     if be == "B1" else None))
    for deck, eb in elim_beta.items():
        for L, qs in QS.items():
            for s, q in enumerate(qs, 1):
                for j in range(n):
                    recs.append(dict(fixture=f"L{L}-s{s}", L=L, seed=s, q=q, deck=deck,
                                     query_id=f"{L}-{s}-{deck}-{j}", backend="B2", member=None,
                                     status="ok", W=None, W_full=None, W_triple=None,
                                     elim_degree=q ** eb * math.exp(rng.normal(0, 0.02))))
    return recs


def test_slope_recovery():
    recs = synth({("B1", "interval_x"): 0.6}, noise=0.01, member_stop_frac=1.0)
    b = analysis.beta(recs, "W", "median", "B1", "interval_x", "all", n_boot=200)
    assert abs(b["point"] - 0.6) < 0.01
    lo, hi = b["ci95"]
    assert lo <= b["point"] <= hi and hi - lo < 0.05


def test_bootstrap_deterministic():
    recs = synth({("B1", "interval_x"): 0.4}, noise=0.3)
    b1 = analysis.beta(recs, "W", "worst", "B1", "interval_x", "all", n_boot=100)
    b2 = analysis.beta(recs, "W", "worst", "B1", "interval_x", "all", n_boot=100)
    assert b1["ci95"] == b2["ci95"]


def test_class_filters_and_lower_bounds():
    recs = synth({("B1", "interval_x"): 0.5}, noise=0.01)
    recs[0]["status"] = "watchdog_stop"
    recs[0]["member"] = None
    s = analysis.beta(recs, "W", "median", "B1", "interval_x", "successful", n_boot=0)
    a = analysis.beta(recs, "W", "median", "B1", "interval_x", "all", n_boot=0)
    assert s["per_L"]["8"]["n"] == 3 * 16 - 1 and a["per_L"]["8"]["n"] == 96
    assert a["contains_lower_bounds"] and not s["contains_lower_bounds"]


def _full(b1_int, b1_rand, b0, elim_prog=0.2, noise=0.02, sub_beta=None):
    decks = ("interval_x", "subgroup_x", "random_x")
    spec = {}
    for d in decks:
        spec[("B0", d)] = b0
        spec[("B1", d)] = b1_int if d == "interval_x" else b1_rand
    recs = synth(spec, noise=noise, elim_beta={d: 0.6 for d in decks} | {"progression": elim_prog},
                 sub_beta=sub_beta)
    return analysis.compute_metrics(recs, n_boot=200)


def test_outcome_B_scoped_close():
    m = _full(b1_int=1.0, b1_rand=1.0, b0=0.6)
    o = analysis.outcome(m, 1.0, True)
    assert o["outcome"] == "B", o


def test_outcome_A_requires_flat_medians_and_null_gap():
    # beta < 0 gives non-increasing medians; random_x deck higher
    m = _full(b1_int=-0.05, b1_rand=0.5, b0=0.6)
    o = analysis.outcome(m, 1.0, True)
    assert o["outcome"] == "A", o
    # v3 (OQ-9): a constant per-size beta of 0.1 is "flat" within 0.02 -> A
    m = _full(b1_int=0.1, b1_rand=0.5, b0=0.6)
    o = analysis.outcome(m, 1.0, True)
    assert o["outcome"] == "A", o
    assert o["conditions_A"]["B1_medians_nonincreasing_in_L"] is True


def test_per_size_beta_rising_more_than_tolerance_is_not_flat():
    # W = e^-2 q^0.2: per-size log W / log q = 0.2 - 2/log q rises by ~0.05 and
    # ~0.03 per size (> 0.02) while the slope stays 0.2 < 0.30.
    m = _full(b1_int={"beta": 0.2, "scale": math.exp(-2)}, b1_rand=0.5, b0=0.6)
    per = m["beta_work"]["B1"]["interval_x"]["all"]["median"]["per_L"]
    vals = [per[k]["median_logW_over_logq"] for k in ("8", "16", "32")]
    assert vals[1] - vals[0] > 0.02 and vals[2] - vals[1] > 0.02
    o = analysis.outcome(m, 1.0, True)
    assert o["conditions_A"]["B1_all_worst_upper_ci_lt_gate"] is True
    assert o["conditions_A"]["B1_medians_nonincreasing_in_L"] is False
    assert o["outcome"] == "inconclusive"


def test_flat_tolerance_boundary():
    e = {"per_L": {"8": {"median_logW_over_logq": 0.10}, "16": {"median_logW_over_logq": 0.119},
                   "32": {"median_logW_over_logq": 0.138}}}
    assert analysis._medians_nonincreasing(e) is True
    e["per_L"]["32"]["median_logW_over_logq"] = 0.1405
    assert analysis._medians_nonincreasing(e) is False


def test_outcome_A_also_requires_triple_slope():
    # A large per-query fixed term flattens total W (slope ~0) while the
    # per-triple component grows as q^0.6: total passes, W_triple fails -> not A.
    m = _full(b1_int={"beta": 0.6, "fixed": 1e7}, b1_rand=0.5, b0=0.6)
    o = analysis.outcome(m, 1.0, True)
    assert o["conditions_A"]["B1_all_worst_upper_ci_lt_gate"] is True
    assert o["conditions_A"]["B1_triple_all_worst_upper_ci_lt_gate"] is False
    assert o["B1_all_worst_beta_total"] < 0.05 and abs(o["B1_all_worst_beta_triple"] - 0.6) < 0.05
    assert o["outcome"] == "inconclusive"


def test_primary_is_decision_cost_full_is_secondary():
    m = _full(b1_int=0.5, b1_rand=0.5, b0=0.6)
    prim = m["beta_work"]["B1"]["interval_x"]["successful"]["median"]["per_L"]["8"]["value"]
    full = m["beta_work_full"]["B1"]["interval_x"]["successful"]["median"]["per_L"]["8"]["value"]
    assert abs(prim / full - 0.5) < 1e-9
    # all-queries worst is governed by non-members, which pay full enumeration
    w = m["beta_work"]["B1"]["interval_x"]["all"]["worst"]["per_L"]["8"]["value"]
    wf = m["beta_work_full"]["B1"]["interval_x"]["all"]["worst"]["per_L"]["8"]["value"]
    assert w == wf
    assert m["work_quantities"]["primary"] == "W"


def test_calibration_failure_is_inconclusive():
    m = _full(b1_int=1.0, b1_rand=1.0, b0=0.9)
    o = analysis.outcome(m, 1.0, True)
    assert o["outcome"] == "inconclusive" and o["conditions_B"]["B0_calibration_in_range"] is False


def test_procedure_defects():
    m = _full(b1_int=1.0, b1_rand=1.0, b0=0.6)
    assert analysis.outcome(m, 0.99, True)["outcome"] == "procedure_defect"
    assert analysis.outcome(m, 1.0, False)["outcome"] == "procedure_defect"
    m2 = _full(b1_int=1.0, b1_rand=1.0, b0=0.6, elim_prog=0.6)
    assert analysis.outcome(m2, 1.0, True)["outcome"] == "procedure_defect"


def test_known_false_gate_trips_when_B0_looks_sub_gate():
    m = _full(b1_int=1.0, b1_rand=1.0, b0=-0.05)
    o = analysis.outcome(m, 1.0, True)
    assert o["known_false_B0_passes_A"] and o["outcome"] == "procedure_defect"


def test_forbidden_reading_low_beta_sub_is_not_A():
    m = _full(b1_int=1.0, b1_rand=1.0, b0=0.6, sub_beta=0.01)
    assert m["beta_sub"]["interval_x"]["all"]["point"] < 0.3
    assert analysis.outcome(m, 1.0, True)["outcome"] != "A"


def test_rho_c_and_cells():
    recs = synth({("B1", "interval_x"): 0.5}, noise=0.01)
    cells = analysis.per_cell(recs, "B1")
    assert len(cells) == 9 and all(abs(c["P_success"] - 0.5) < 1e-9 for c in cells)
    # rho_c on the primary (decision) W: members stop at the first hit
    assert all(0.3 < c["rho_c"] < 0.8 for c in cells)
    assert all(c["median_W_full_all"] >= c["median_W_all"] for c in cells)


def test_zero_degree_statistic_is_undefined_not_zero():
    recs = synth({("B1", "interval_x"): 0.5}, sub_beta=None)
    b = analysis.beta(recs, "sub_degree", "median", "B1", "interval_x", "all", n_boot=10)
    assert b["point"] is None and "non-positive" in b["undefined_reason"]


def test_audit_rejects_zeroed_work():
    good = {"query_id": "x", "backend": "B0", "W_query": 16, "n_triples": 2, "n_queries_in_cell": 4,
            "op_log": [["0,0,0", 3, 1, 4, 0], ["0,0,1", 0, 0, 0, 8]],
            "table_ops": {"W": 40, "probes": 4, "mul": 10}, "deck_construction_ops": {"W": 0}}
    good["W"] = 16 + 40 / 4
    r = audit.check_receipt(good)
    assert not r["accepted"]  # first triple has 0 probes, second has zero mults but 8 probes
    ok = dict(good, op_log=[["0,0,0", 3, 1, 4, 8], ["0,0,1", 0, 0, 0, 8]], W_query=24, W=24 + 10)
    assert audit.check_receipt(ok)["accepted"]
    zt = dict(ok, table_ops={"W": 0, "probes": 0})
    assert not audit.check_receipt(zt)["accepted"]
    drop = dict(ok, op_log=ok["op_log"][:1])
    assert not audit.check_receipt(drop)["accepted"]


def test_audit_v3_decision_full_and_triple():
    base = {"query_id": "x", "backend": "B1", "n_triples": 2, "n_queries_in_cell": 4,
            "op_log": [["specialize_R", 100, 0, 0, 0], ["0,0,0", 30, 1, 5, 0], ["0,0,1", 30, 1, 7, 0]],
            "table_ops": {"W": 40, "probes": 4, "mul": 10}, "deck_construction_ops": {"W": 0},
            "W_query": 174, "hit_triples": [[0, 0, 0]], "W_fixed_xR": 100}
    good = dict(base, W=136 + 10, W_full=174 + 10, W_triple=136 + 10 - 100)
    assert audit.check_receipt(good)["accepted"], audit.check_receipt(good)
    # a receipt that reports full enumeration as the decision cost is rejected
    assert not audit.check_receipt(dict(good, W=184))["accepted"]
    # a W_triple that also drops per-triple specialization is rejected
    assert not audit.check_receipt(dict(good, W_triple=10))["accepted"]
    # non-member: decision cost is full enumeration
    nm = dict(base, hit_triples=[], W=184, W_full=184, W_triple=84)
    assert audit.check_receipt(nm)["accepted"]


def test_audit_selection_is_ten_percent_and_deterministic():
    ids = [f"q{i}" for i in range(864)]
    s1 = audit.select(ids, "smoke|EXP-SDEG-85eefd/v2")
    assert len(s1) == 87 and s1 == audit.select(ids, "smoke|EXP-SDEG-85eefd/v2")

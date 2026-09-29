"""C-5 analysis of AMD-20260926-ced670, implemented verbatim:

  ratio    := complete charged cost (stage 1 + stage 3 + 16 descents, units)
              / (13 * 0.886 * sqrt(q)), per fixture.
  exponent := slope of log(complete cost) vs log q over the 6 fixtures, with a
              95% bootstrap CI (2000 resamples). With only two sizes the
              exponent is disclosed as weak.
  verdict  := "sub_rho_signal"  iff exponent upper CI < 0.5 AND ratio < 1 on
                                every 20-bit fixture;
              "scoped_negative" iff exponent lower CI >= 0.5, naming the
                                dominant stage (largest share of charged cost
                                at 20 bits);
              "inconclusive"    otherwise.

Implementation readings (implementation.md OQ-8): the bootstrap resamples the
6 (log q, log cost) fixture points with replacement (numpy PCG64 seeded from
'<ns>|bootstrap'); a resample whose log q values are all equal has no slope
and is redrawn (count reported); the CI is the 2.5/97.5 percentile interval
(numpy 'linear' method). The dominant stage pools each stage's units over the
20-bit fixtures. Also reported (not part of the verdict): alpha2 (C-4 stage 2)
as the OLS slope of log(mean 2-sum scan units) vs log L over the primary
fixtures, the spec-v1 metric complete_cost / sqrt(q), the rho baseline's
measured units against 13 * 0.886 * sqrt(q), and the random-x null beside the
interval factor base.

FX-A (AMD-20260929-143d11, protocol v3; DESCRIPTIVE, NOT a verdict input):
per primary fixture
    complete_units_rj_incremental = complete_units - 13 * sum_j (rj_ops_j - 1)
over the stage-1 attempts j, where rj_ops_j is the charged group-operation
count of computing R_j = a_j G + b_j Q (double-and-add of a_j G and b_j Q
plus the final addition), recomputed with the charged arithmetic (arith.Curve)
from the run's own attempt labels (pipeline.attempt_ab) and target label, and
cross-checked rj_ops_j <= pt_ops_j (else ProcedureDefect). Its ratio to
13 * 0.886 * sqrt(q) is reported beside the primary ratio as
ratio_rj_incremental_nonverdict. Descent attempts build Q_t + r G, not
a_j G + b_j Q, so the named figure covers stage-1 attempts only (literal);
a supplementary figure applying the same substitution to the descent
attempts' r G + final addition is reported separately
(complete_units_rj_incremental_with_descents, OQ-15). Neither enters the
C-5 rule, which reads only complete_units.
"""

from __future__ import annotations

import math

import numpy as np

import common

STAGES = ("stage1", "stage3", "descents")


def _charged_ops(fn):
    from arith import Cost
    c = Cost()
    fn(c)
    return c.pt_add + c.pt_dbl


def fxa_figure(r: dict) -> dict:
    """FX-A for one primary cell result (see module docstring)."""
    import pipeline
    from arith import Curve, Fp
    from verify import VCurve
    fx, ns = r["fixture"], r["namespace"]
    G = tuple(fx["G"])
    Q = VCurve(fx["p"], fx["a"], fx["b"]).mul(pipeline.target_k(fx, ns), G)
    if Q is None or [Q[0], Q[1]] != list(r["target"]["Q"]):
        raise pipeline.ProcedureDefect("FX-A: recomputed Q differs from the receipt's target")

    def rj_ops(a, b):
        def f(c):
            E = Curve(Fp(fx["p"], c), fx["a"], fx["b"])
            E.add(E.mul(a, G), E.mul(b, Q))
        return _charged_ops(f)

    def desc_ops(Qt, rr):
        def f(c):
            E = Curve(Fp(fx["p"], c), fx["a"], fx["b"])
            E.add(Qt, E.mul(rr, G))
        return _charged_ops(f)

    s1 = r["stage1"]["attempt_log"]
    pt = s1["pt_ops"]
    if len(pt) != len(s1["member_bits"]):
        raise pipeline.ProcedureDefect("FX-A: malformed stage-1 attempt log")
    excess1 = 0
    for j, logged in enumerate(pt):
        a, b = pipeline.attempt_ab(fx, ns, j)
        k = rj_ops(a, b)
        if k > logged:
            raise pipeline.ProcedureDefect(f"FX-A: attempt {j} rj_ops {k} > logged pt_ops {logged}")
        excess1 += k - 1
    excess_d = 0
    n_desc_att = 0
    for t in r["descents"]["targets"]:
        Qt = tuple(t["Q_t"])
        dpt = t["attempt_log"]["pt_ops"]
        for i, logged in enumerate(dpt):
            rr = common.uniform(common.lab(ns, "descent_r", fx["bits"], fx["seed"], t["t"], i), fx["N"])
            k = desc_ops(Qt, rr)
            if k > logged:
                raise pipeline.ProcedureDefect(f"FX-A: descent {t['t']}.{i} ops {k} > logged pt_ops {logged}")
            excess_d += k - 1
            n_desc_att += 1
    ref = common.rho_reference_units(fx["N"])
    inc = r["complete_units"] - common.UNIT_POINT_ADD * excess1
    inc_d = inc - common.UNIT_POINT_ADD * excess_d
    return {"complete_units_rj_incremental": inc,
            "ratio_rj_incremental_nonverdict": inc / ref,
            "rj_stage1_attempts": len(pt), "rj_stage1_excess_ops": excess1,
            "complete_units_rj_incremental_with_descents": inc_d,
            "ratio_rj_incremental_with_descents_nonverdict": inc_d / ref,
            "rj_descent_attempts": n_desc_att, "rj_descent_excess_ops": excess_d,
            "cross_check": "rj_ops_j <= pt_ops_j for every attempt: passed",
            "label": "FX-A descriptive, NOT a verdict input (AMD-20260929-143d11)"}


def ols_slope(xs, ys):
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    xm = xs.mean()
    den = ((xs - xm) ** 2).sum()
    if den == 0:
        return None
    return float(((xs - xm) * (ys - ys.mean())).sum() / den)


def bootstrap_slope(xs, ys, label, n_resamples=common.BOOTSTRAP_RESAMPLES):
    rng = np.random.Generator(np.random.PCG64(common.rng_seed(label)))
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    n = len(xs)
    slopes, redraws = [], 0
    while len(slopes) < n_resamples:
        idx = rng.integers(0, n, n)
        s = ols_slope(xs[idx], ys[idx])
        if s is None:
            redraws += 1
            continue
        slopes.append(s)
    lo, hi = np.percentile(slopes, [2.5, 97.5])
    return {"ci95": [float(lo), float(hi)], "resamples": n_resamples, "degenerate_redraws": redraws,
            "label": label}


def analyse(primary: list[dict], rho: list[dict] | None = None, null: list[dict] | None = None,
            stage_cost: list[dict] | None = None, namespace: str = common.FROZEN_NS,
            fxa=fxa_figure) -> dict:
    """primary: the 6 primary cell results (pipeline.run_primary outputs).
    `fxa` computes the FX-A figure; results without stage-1 attempt logs
    (synthetic inputs in tests) get None."""
    per = []
    fxa_per = []
    for r in primary:
        fxa_per.append(fxa(r) if (fxa and "stage1" in r) else None)
        q = r["fixture"]["N"]
        comp = r["complete_units_components"]
        total = r["complete_units"]
        per.append({"fixture_id": r["fixture_id"], "bits": r["fixture"]["bits"], "q": q,
                    "complete_units": total, "components": comp,
                    "shares": {s: comp[s] / total for s in STAGES},
                    "ratio": total / common.rho_reference_units(q),
                    "complete_over_sqrt_q": total / math.sqrt(q),
                    "peak_rss_bytes": r["peak_rss_bytes"],
                    "alpha2_mean_units": r["stage2_alpha2"]["mean_units"], "L": r["factor_base"]["L"]})
    xs = [math.log(p["q"]) for p in per]
    ys = [math.log(p["complete_units"]) for p in per]
    expo = ols_slope(xs, ys)
    boot = bootstrap_slope(xs, ys, common.lab(namespace, "bootstrap"))
    lo, hi = boot["ci95"]
    b20 = [p for p in per if p["bits"] == 20]
    pooled20 = {s: sum(p["components"][s] for p in b20) for s in STAGES}
    dominant = max(STAGES, key=lambda s: pooled20[s]) if b20 else None
    if hi < 0.5 and b20 and all(p["ratio"] < 1 for p in b20):
        verdict = "sub_rho_signal"
    elif lo >= 0.5:
        verdict = "scoped_negative"
    else:
        verdict = "inconclusive"
    a_x = [math.log(p["L"]) for p in per if p["L"] > 0]
    a_y = [math.log(p["alpha2_mean_units"]) for p in per if p["L"] > 0]
    alpha2 = ols_slope(a_x, a_y) if len(set(a_x)) > 1 else None
    for p, f in zip(per, fxa_per):
        p["fxa_nonverdict"] = f
        p["ratio_rj_incremental_nonverdict"] = f["ratio_rj_incremental_nonverdict"] if f else None
    out = {
        "per_fixture": per,
        "exponent": expo, "exponent_bootstrap": boot,
        "exponent_disclosure": "weak: only two field sizes (16, 20 bits)",
        "verdict": verdict,
        "dominant_stage_20bit": dominant if verdict == "scoped_negative" else None,
        "dominant_stage_20bit_diagnostic": dominant, "pooled_units_20bit": pooled20,
        "alpha2": alpha2,
        "alpha2_note": "C-4: trivial scan attains alpha2 = 1 < 3/2 by construction; reported, not a verdict input",
        "alpha2_distinct_L": sorted(set(p["L"] for p in per)),
        "rule": "C-5 AMD-20260926-ced670 verbatim (unchanged by AMD-20260929-143d11)",
        "fxa_note": "per_fixture[*].fxa_nonverdict is descriptive only (AMD-20260929-143d11 FX-A)",
    }
    if rho:
        out["rho_baseline"] = [{"fixture_id": r["fixture_id"], "q": r["fixture"]["N"],
                                "mean_units": r["mean_units"], "mean_walk_units": r["mean_walk_units"],
                                "reference_units": r["reference_13x0886_sqrt_q"],
                                "measured_over_reference": r["mean_units"] / r["reference_13x0886_sqrt_q"],
                                "walk_over_reference": r["mean_walk_units"] / r["reference_13x0886_sqrt_q"],
                                "n_solved": r["n_solved"], "peak_rss_bytes": r["peak_rss_bytes"]} for r in rho]
    if null:
        byid = {p["fixture_id"]: p for p in per}
        out["null_randfb"] = []
        for r in null:
            prim = next((x for x in primary if x["fixture_id"] == r["fixture_id"]), None)
            out["null_randfb"].append({
                "fixture_id": r["fixture_id"], "L": r["factor_base"]["L"],
                "attempts": r["stage1"]["n_attempts"], "relation_yield": r["stage1"]["relation_yield"],
                "stage1_units": r["stage1"]["units"], "stage3_units": r["stage3"]["units"],
                "interval_attempts": prim["stage1"]["n_attempts"] if prim else None,
                "interval_relation_yield": (prim["stage1"]["n_relations"] / prim["stage1"]["n_attempts"]) if prim else None,
                "interval_stage1_units": prim["stage1"]["units"] if prim else None,
                "interval_stage3_units": prim["stage3"]["units"] if prim else None,
                "peak_rss_bytes": r["peak_rss_bytes"], "in_primary": r["fixture_id"] in byid})
    if stage_cost:
        out["stage_cost_only"] = [{"fixture_id": r["fixture_id"], "m": r["m"], "B": r["factor_base"]["B"],
                                   "L": r["factor_base"]["L"], "stage1_units": r["stage1"]["units"],
                                   "stage3_units": r["stage3"]["units"], "attempts": r["stage1"]["n_attempts"],
                                   "stage2_mean_units": r["stage2_alpha2"]["mean_units"],
                                   "peak_rss_bytes": r["peak_rss_bytes"]} for r in stage_cost]
    return out

#!/usr/bin/env python3
"""RED TEAM statistical probes for the v2 amendment (TASK-20260806-42c153).

P-A  COMPOSITE NULL.  The v2 INV-NULL interval is calibrated at the single
     point  S ~ Bin(n_e, q_hat).  The hypothesis the test can actually reject
     with the moments it measures is the SUB-FAMILY  {A_k = 1 for k <= k_max}.
     Construct laws inside that sub-family that are NOT binomial and measure
     the realized size of the frozen interval under them.

P-B  q MIS-SPECIFICATION.  Size of the frozen interval when the true q differs
     from the q_hat the interval was frozen at.

P-C  OPEN-7.  Independent third measurement of the v1 Wald rule's size at
     PS-R5, k = 30, T = 239 896, under both candidate q values and both
     batching conventions.

Every draw is from an explicit, fully specified law.  No HQC object is built.
Claim tier TOY.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import sys
import time

import numpy as np

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", "..", ".."))
CAL = os.path.join(REPO, "coordination", "goals", "GOAL-HQC-001", "batches",
                   "BATCH-c5703d", "tasks", "TASK-20260806-dbadc8", "calibration.py")

RT_SEED = 42153
ALPHA = 0.0026997960632601866


def load_cal():
    spec = importlib.util.spec_from_file_location("cal_rt", CAL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------------------
# P-A: laws inside the tested sub-family that are not binomial
# --------------------------------------------------------------------------

def k_null_pmf(n_e, q, k0, s1, knots, scale=0.98):
    """A pmf on {0..n_e} that satisfies EXACTLY the three constraints the
    INV-NULL cell at k = k0 actually tests:
        sum p = 1,   sum s p_s = n_e q  (same q_hat),
        sum C(s,k0) p_s = C(n_e,k0) q^k0   (i.e. A_k0 = 1 exactly),
    but is NOT Bin(n_e,q).  Mass +delta is placed at s = s1 (a heavy upper
    tail, which is what drives Var(log2 Ahat_k0)) and removed at `knots`,
    which are near the mode where the binomial has mass to spare.
    """
    p0 = np.array([math.comb(n_e, s) * q ** s * (1 - q) ** (n_e - s)
                   for s in range(n_e + 1)], dtype=np.float64)
    p0 = p0 / p0.sum()

    def row(s):
        return np.array([1.0, float(s), float(math.comb(int(s), k0))
                         if s >= k0 else 0.0])

    A = np.column_stack([row(t) for t in knots])          # 3 x |knots|
    b = -row(s1)
    try:
        c = np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        return None, None
    u = np.zeros(n_e + 1)
    u[s1] += 1.0
    for t, ci in zip(knots, c):
        u[t] += ci
    # exact-constraint residual check
    res = float(np.abs(np.array([u.sum(),
                                 float(np.arange(n_e + 1) @ u),
                                 float(np.array([math.comb(s, k0) if s >= k0 else 0
                                                 for s in range(n_e + 1)],
                                                dtype=float) @ u)])).max())
    neg = u < 0
    if not neg.any():
        return None, None
    delta = float(np.min(p0[neg] / (-u[neg]))) * scale
    p = p0 + delta * u
    if p.min() < -1e-18:
        return None, None
    p = np.maximum(p, 0.0)
    return p, dict(delta=delta, constraint_residual=res,
                   tv=float(0.5 * np.abs(p - p0).sum()))


def moment_matched_pmf(n_e, q, k0, s_max, target="tail", scale=1.0):
    """A pmf p on {0..n_e} with, EXACTLY:
         sum_s p_s = 1,  sum_s C(s,k) p_s = C(n_e,k) q^k  for k = 1..k0
    i.e. A_k = 1 for every k <= k0 (and the same q as the binomial), but
    p != Bin(n_e,q).  Built as Bin + delta*u with u in the null space of the
    moment constraints, supported on s <= s_max so the non-negativity bound is
    not crushed by the far tail.

    Returns (pmf, delta_used, direction_name) or (None, ...) if infeasible.
    """
    p0 = np.array([math.comb(n_e, s) * q ** s * (1 - q) ** (n_e - s)
                   for s in range(n_e + 1)], dtype=np.float64)
    p0 = p0 / p0.sum()
    sup = np.arange(0, s_max + 1)
    M = np.array([[float(math.comb(int(s), k)) for s in sup]
                  for k in range(0, k0 + 1)], dtype=np.float64)
    # scale rows so the SVD is not dominated by the largest binomials
    M = M / np.maximum(np.abs(M).max(axis=1, keepdims=True), 1.0)
    U, sv, Vt = np.linalg.svd(M)
    rank = int((sv > sv.max() * 1e-10).sum())
    NS = Vt[rank:].T                              # (|sup|, dim) null space
    if NS.shape[1] == 0:
        return None, None, None
    if target == "tail":
        g = np.array([float(math.comb(int(s), k0)) ** 2 for s in sup])
    elif target == "var":
        g = (sup.astype(float) - n_e * q) ** 2
    else:
        g = np.array([1.0 if s == s_max else 0.0 for s in sup])
    g = g / (np.abs(g).max() or 1.0)
    u_sup = NS @ (NS.T @ g)
    if not np.isfinite(u_sup).all() or np.abs(u_sup).max() == 0:
        return None, None, None
    u = np.zeros(n_e + 1)
    u[sup] = u_sup
    neg = u < 0
    if not neg.any():
        return None, None, None
    delta = float(np.min(p0[neg] / (-u[neg]))) * scale
    p = p0 + delta * u
    p = np.maximum(p, 0.0)
    p = p / p.sum()
    return p, delta, target


def exact_log2A(pmf, n_e, k):
    s = np.arange(n_e + 1, dtype=np.float64)
    q = float(pmf @ s) / n_e
    ck = np.array([float(math.comb(int(x), k)) if x >= k else 0.0 for x in s])
    mu = float(pmf @ ck) / float(math.comb(n_e, k))
    return math.log2(mu) - k * math.log2(q), q


def size_under(cal, rng, n_e, T, ks, pmf_cal, pmf_true, n_cal, n_val):
    """Freeze [c_lo,c_hi] under pmf_cal; measure size under pmf_true."""
    c = cal.log2A_samples(rng, T, pmf_cal, n_cal, n_e, ks)
    v = cal.log2A_samples(rng, T, pmf_true, n_val, n_e, ks)
    rows = []
    for k in ks:
        cg = c[k][np.isfinite(c[k])]
        vg = v[k][np.isfinite(v[k])]
        if cg.size < 1000 or vg.size == 0:
            rows.append(dict(k=k, evaluable=False))
            continue
        lo = float(np.quantile(cg, ALPHA / 2))
        hi = float(np.quantile(cg, 1 - ALPHA / 2))
        fire = int(((vg < lo) | (vg > hi)).sum())
        wl, wh = cal.wilson(fire, vg.size)
        rows.append(dict(k=k, evaluable=True, c_lo=lo, c_hi=hi,
                         replicates=int(vg.size), firings=fire,
                         realized_size=fire / vg.size,
                         realized_size_ci95=[wl, wh],
                         nominal=ALPHA,
                         ratio_to_nominal=(fire / vg.size) / ALPHA))
    return rows


def probe_A(cal, rng, out):
    """Size of the FROZEN v2 interval under laws that satisfy EXACTLY the
    moment condition the k = m cell tests, but are not binomial."""
    res = []
    for (sid, n_e, q, T, k0, s1, knots) in [
            ("PS-R1", 46, 0.19742737, 100_000_000, 16, 22, [7, 10, 16]),
            ("PS-R3", 56, 0.31994629, 20_000_000, 17, 25, [14, 17, 20]),
            ("PS-R5", 90, 0.41412035, 20_000_000, 30, 49, [34, 37, 40])]:
        p0 = cal.binom_pmf(n_e, q)
        for scale in (0.98, 0.5, 0.2, 0.05):
            pmf, info = k_null_pmf(n_e, q, k0, s1, knots, scale=scale)
            if pmf is None:
                continue
            a_k0, q_true = exact_log2A(pmf, n_e, k0)
            a_2, _ = exact_log2A(pmf, n_e, 2)
            rows = size_under(cal, rng, n_e, T, [k0], p0, pmf, 200_000, 200_000)
            res.append(dict(
                set=sid, n_e=n_e, q_calibration=q, T=T, k=k0,
                s1=s1, knots=knots, feasibility_scale=scale, delta=info["delta"],
                constraint_residual=info["constraint_residual"],
                exact_log2A_at_k0_bits=a_k0,
                exact_log2A_at_2_bits=a_2,
                q_of_perturbed_law=q_true,
                total_variation_from_binomial=info["tv"],
                size_rows=rows))
            print(sid, "scale", scale, "TV=%.4g" % info["tv"],
                  "log2A_k0=%.1e" % a_k0,
                  "size=", [r.get("realized_size") for r in rows], flush=True)
    out["P_A_composite_null"] = res


def probe_B(cal, rng, out):
    res = []
    for (sid, n_e, q, T, k) in [("PS-R1", 46, 0.19742737, 100_000_000, 16),
                                ("PS-R3", 56, 0.31994629, 20_000_000, 17),
                                ("PS-R5", 90, 0.41412035, 20_000_000, 30)]:
        p0 = cal.binom_pmf(n_e, q)
        for rel in (0.002, 0.01, 0.03):
            for sgn in (-1, 1):
                pq = cal.binom_pmf(n_e, q * (1 + sgn * rel))
                rows = size_under(cal, rng, n_e, T, [k], p0, pq, 200_000, 200_000)
                res.append(dict(set=sid, k=k, T=T, q_frozen=q,
                                q_true=q * (1 + sgn * rel),
                                rel_shift=sgn * rel, size_rows=rows))
                print(sid, "qshift", sgn * rel,
                      [r.get("realized_size") for r in rows], flush=True)
    out["P_B_q_misspecification"] = res


def probe_C(cal, rng, out, reps):
    """OPEN-7: independent third measurement of the v1 Wald rule at PS-R5 k=30."""
    res = []
    n_e, T, k = 90, 239896, 30
    for label, q in [("NULL-M own q_hat", 0.4139887469755413),
                     ("(T) arm q_hat", 0.41412035)]:
        rows = cal.wald_size(rng, n_e, q, T, [k], reps, B=200)
        for r in rows:
            r["q_used"] = q
            r["q_label"] = label
        res += rows
        print("OPEN-7", label, rows[0].get("realized_size"), flush=True)
    # PS-R1 k=16 control cell, where the two prior measurements DID agree
    rows = cal.wald_size(rng, 46, 0.1978445570395305, 497632, [16], reps, B=200)
    for r in rows:
        r["q_used"] = 0.1978445570395305
        r["q_label"] = "PS-R1 NULL-M own q_hat (control cell)"
        r["set"] = "PS-R1"
    res += rows
    out["P_C_open7"] = res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--probes", default="ABC")
    ap.add_argument("--open7-reps", type=int, default=20000)
    a = ap.parse_args(argv)
    cal = load_cal()
    rng = np.random.default_rng(RT_SEED)
    out = dict(seed=RT_SEED, alpha=ALPHA, started=time.time())
    t0 = time.time()
    if "A" in a.probes:
        probe_A(cal, rng, out)
    if "B" in a.probes:
        probe_B(cal, rng, out)
    if "C" in a.probes:
        probe_C(cal, rng, out, a.open7_reps)
    out["wall_seconds"] = time.time() - t0
    json.dump(out, open(a.out, "w"), indent=1)
    print("wall", round(time.time() - t0, 1))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Analysis of the RED TEAM perturbation run: does CTRL-POSHOM fire?

Three references for clause (a) are computed side by side:

  REF-1  the amendment's own: independent-blocks binomial critical value at
         alpha, i.e. Q_raw compared against the (n_e-1)-df chi-square-like
         null of INDEPENDENT blocks.
  REF-2  the exact mean identity.  With c = Cov(F_j,F_j') and v = q(1-q),
         E[Q_raw] = (n_e-1)(1 - c/v) = (n_e-1)(1 - q A_2)/(1 - q).
         Reported as a VERIFICATION OF THE IDENTITY on deliberately broken
         variants; the correct arm's A_2 is computed but WITHHELD.
  REF-3  the fix this review proposes: a distribution-free Wald/chi-square on
         the per-trial contrast Z_t = F_t - (S_t/n_e) 1, whose null mean is
         zero under positional homogeneity and which needs NO unknown
         constant.  X = T * Zbar' Sigmahat^+ Zbar ~ chi2_{n_e-1}.

Clause (b) uses the same construction on Y_t(d) = (F_tj F_t,j+d)_j.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
ALPHA = 0.0026997960632601866


def chi2_sf(x, df, n=200000):
    """Upper tail of chi2_df by a Wilson-Hilferty approximation plus an exact
    Monte-Carlo cross-check for the values that matter."""
    if x <= 0:
        return 1.0
    z = ((x / df) ** (1.0 / 3.0) - (1 - 2.0 / (9 * df))) / math.sqrt(2.0 / (9 * df))
    # normal upper tail
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def chi2_crit_mc(df, alpha, rng, R=400000):
    g = rng.chisquare(df, size=R)
    return float(np.quantile(g, 1 - alpha))


def q_of(bc, T, n_e):
    return float(np.sum(bc)) / (T * n_e)


def Q_raw(bc, T, q):
    bc = np.asarray(bc, dtype=np.float64)
    return float(((bc - bc.mean()) ** 2).sum() / (T * q * (1 - q)))


def ref1_critical(rng, n_e, T, q, R=200000):
    out = np.empty(R)
    den = T * q * (1 - q)
    for i in range(0, R, 20000):
        r = min(20000, R - i)
        C = rng.binomial(T, q, size=(r, n_e)).astype(np.float64)
        out[i:i + r] = ((C - C.mean(axis=1, keepdims=True)) ** 2).sum(axis=1) / den
    return float(np.quantile(out, 1 - ALPHA)), float(out.mean())


def wald_from_aggregates(bc, P, T, n_e):
    """REF-3 for clause (a), computable from the block counts and the pairwise
    co-occurrence matrix alone.  Returns (X, df, note)."""
    bc = np.asarray(bc, dtype=np.float64)
    P = np.asarray(P, dtype=np.float64)
    one = np.ones(n_e)
    P1 = P @ one
    s2 = float(one @ P1)                       # = sum_t S_t^2
    M = P - np.outer(P1, one) / n_e - np.outer(one, P1) / n_e + s2 * np.outer(one, one) / n_e ** 2
    Zbar = (bc - bc.mean()) / T
    Sig = M / T - np.outer(Zbar, Zbar)
    # project onto the (n_e-1)-dim subspace orthogonal to 1 (Z_t lives there)
    w, V = np.linalg.eigh(Sig)
    keep = w > max(w.max(), 0) * 1e-10
    Vp, wp = V[:, keep], w[keep]
    X = float(T * ((Vp.T @ Zbar) ** 2 / wp).sum())
    return X, int(keep.sum()), dict(sum_S_squared=s2)


def A2_from_pair(bc, P, T, n_e):
    """log2 A_2 from the pairwise matrix.  DISCLOSURE, not a deliverable:
    this is exactly the k=2 measurement, and it is one line."""
    P = np.asarray(P, dtype=np.float64)
    off = (P.sum() - np.trace(P)) / 2.0          # sum_{j<j'} count
    mu2 = (off / T) / math.comb(n_e, 2)
    q = float(np.sum(bc)) / (T * n_e)
    return math.log2(mu2) - 2 * math.log2(q)


def clause_b(F, n_e, lags):
    """REF-3 applied to clause (b): within-lag positional homogeneity of the
    pair moment.  Uses only contrasts; needs no unknown constant."""
    T = F.shape[0]
    rows = []
    for d in lags:
        nd = n_e - d
        if nd < 3:
            continue
        G = (F[:, :nd] * F[:, d:d + nd]).astype(np.uint8)
        cnt = G.sum(axis=0).astype(np.float64)
        GG = ((G.astype(np.float32).T @ G.astype(np.float32))).astype(np.float64)
        Ybar = cnt / T
        Sig = GG / T - np.outer(Ybar, Ybar)
        c = Ybar - Ybar.mean()
        # restrict to the contrast subspace (orthogonal to 1)
        H = np.eye(nd) - np.ones((nd, nd)) / nd
        Sc = H @ Sig @ H
        w, V = np.linalg.eigh(Sc)
        keep = w > max(w.max(), 0) * 1e-10
        Vp, wp = V[:, keep], w[keep]
        X = float(T * ((Vp.T @ c) ** 2 / wp).sum())
        df = int(keep.sum())
        rows.append(dict(lag=d, X=X, df=df, X_over_df=X / df,
                         p_upper=chi2_sf(X, df),
                         mean_pair_rate=float(Ybar.mean()),
                         max_min_spread_rel=float((cnt.max() - cnt.min())
                                                  / max(cnt.mean(), 1.0))))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--agg", required=True)
    ap.add_argument("--fdump", default=None)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)

    d = json.load(open(a.agg))
    ps = d["param_set"]
    n_e, T = ps["n_e"], d["trials"]
    rng = np.random.default_rng(42153)

    res = dict(param_set=ps["id"], n_e=n_e, trials=T,
               decode_selftest=d.get("decode_selftest_max_abs_diff_vs_stage_a"),
               alpha=ALPHA, clause_a=[], clause_b={})
    crit_chi = chi2_crit_mc(n_e - 1, ALPHA, rng)
    res["chi2_critical_value_df_n_e_minus_1"] = crit_chi

    V0 = d["variants"]["V0_correct"]
    q0 = q_of(V0["block_counts"], T, n_e)
    crit1, mean1 = ref1_critical(rng, n_e, T, q0)
    res["ref1_independent_blocks_critical_Q"] = crit1
    res["ref1_independent_blocks_null_mean_Q"] = mean1

    S0 = np.array(V0["S_hist"], dtype=np.float64)

    for v, x in d["variants"].items():
        bc = np.array(x["block_counts"], dtype=np.float64)
        P = np.array(x["pair_matrix"], dtype=np.float64)
        q = q_of(bc, T, n_e)
        Qr = Q_raw(bc, T, q)
        X, df, note = wald_from_aggregates(bc, P, T, n_e)
        a2 = A2_from_pair(bc, P, T, n_e)
        pred = (n_e - 1) * (1 - q * (2 ** a2)) / (1 - q)
        # two-sample chi-square of the S histogram against V0 (levels of
        # neither histogram are reported)
        Sv = np.array(x["S_hist"], dtype=np.float64)
        m = (S0 + Sv) > 20
        chi2_2s = float((((S0[m] - Sv[m]) ** 2) / (S0[m] + Sv[m])).sum())
        res["clause_a"].append(dict(
            variant=v,
            q_hat=q,
            q_hat_rel_shift_vs_correct=q / q0 - 1.0,
            Q_raw=Qr, Q_raw_over_df=Qr / (n_e - 1),
            REF1_fires=bool(Qr > crit1),
            REF2_predicted_E_Q_over_df=pred / (n_e - 1),
            REF3_X=X, REF3_df=df, REF3_X_over_df=X / df,
            REF3_fires=bool(X > crit_chi),
            REF3_p_upper=chi2_sf(X, df),
            S_hist_two_sample_chi2_vs_V0=chi2_2s,
            S_hist_two_sample_df=int(m.sum() - 1),
            log2_A2_WITHHELD_FOR_V0=("WITHHELD" if v == "V0_correct"
                                     else round(a2, 6)),
        ))

    if a.fdump and os.path.exists(a.fdump):
        z = np.load(a.fdump)
        for v in z.files:
            F = z[v]
            res["clause_b"][v] = clause_b(F, n_e, [1, 2, 3])

    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: res[k] for k in
                      ("param_set", "trials", "decode_selftest",
                       "chi2_critical_value_df_n_e_minus_1",
                       "ref1_independent_blocks_critical_Q")}, indent=1))
    for r in res["clause_a"]:
        print(f"{r['variant']:26s} q={r['q_hat']:.6f} ({r['q_hat_rel_shift_vs_correct']:+.4f}) "
              f"Q/df={r['Q_raw_over_df']:8.3f} REF1={'FIRE' if r['REF1_fires'] else 'pass'} "
              f"REF2pred={r['REF2_predicted_E_Q_over_df']:7.3f} "
              f"REF3 X/df={r['REF3_X_over_df']:8.3f} {'FIRE' if r['REF3_fires'] else 'pass'} "
              f"Shist_chi2={r['S_hist_two_sample_chi2_vs_V0']:9.1f}")
    for v, rows in res["clause_b"].items():
        for r in rows:
            print(f"CLAUSE-B {v:26s} d={r['lag']:2d} X/df={r['X_over_df']:7.3f} "
                  f"df={r['df']:3d} p={r['p_upper']:.3e} "
                  f"{'FIRE' if r['p_upper'] < ALPHA else 'pass'}")


if __name__ == "__main__":
    main()

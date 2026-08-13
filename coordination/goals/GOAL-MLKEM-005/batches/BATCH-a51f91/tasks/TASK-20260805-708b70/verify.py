#!/usr/bin/env python3
"""
Independent re-verification of TASK-20260805-708b70's headline numbers.

Deliberately does NOT reuse measure.py's code paths for the load-bearing steps:

  V1  R recomputed by an EXPLICIT Gram-Schmidt loop driven by fpylll's own
      mu / r coefficients (no numpy QR), on a freshly regenerated basis, and
      compared against measure.py's numpy-QR path.
  V2  Beta quantiles recomputed by bisection on scipy.stats.beta.cdf
      (not scipy.special.betaincinv) and cross-checked against results.json.
  V3  the forced value E[R] = beta/d re-derived numerically for a FIXED
      projector and iid equal-variance coordinates, plus the identity
      E[R] = tr(P Sigma)/tr(Sigma) for the anisotropic demonstration arm.
  V4  the (b) quantile ratios and the (c) variance decomposition recomputed
      from an independently regenerated R sample for one basis of one cell.
  V5  arithmetic self-consistency of results.json: the pooled/per-draw
      relationships, the 4s adjudication, and the P1/P2 verdicts recomputed
      from the raw fields.

This run type is a pure measurement: certificate.kind = none (there is no
discrete-log solve and no factor-base relation to certify).  V1-V5 are the
independent-recomputation checks that stand in its place.
"""
import json
import os
import sys

import numpy as np
from scipy.stats import beta as beta_dist

TASK_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TASK_DIR)
import measure as M  # noqa: E402

Q_MOD, ETA = 3329, 2
OUT = {}


def bisect_ppf(a, b, p, lo=0.0, hi=1.0, iters=200):
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if beta_dist.cdf(mid, a, b) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def main():
    res = json.load(open(os.path.join(TASK_DIR, "results.json")))
    d, bt, i0 = 100, 30, 0
    key, tag = f"d{d}_b{bt}", f"d{d}_b{bt}_i{i0}"

    # ---------------- V1: explicit Gram-Schmidt from fpylll mu/r, no numpy QR
    from fpylll import IntegerMatrix, LLL, BKZ, GSO, FPLLL
    from fpylll.fplll.bkz_param import Strategy
    from fpylll.algorithms.bkz2 import BKZReduction
    FPLLL.set_random_seed(M.seed_basis(d, bt, i0))
    A = IntegerMatrix.random(d, "qary", k=d // 2, q=Q_MOD)
    LLL.reduction(A)
    BKZReduction(A)(BKZ.Param(block_size=bt,
                              strategies=[Strategy(x) for x in range(bt + 1)],
                              max_loops=2, flags=BKZ.MAX_LOOPS))
    B = np.array([[A[r, c] for c in range(d)] for r in range(d)], dtype=np.float64)
    G = GSO.Mat(A, float_type="d")
    G.update_gso()
    # b*_i = b_i - sum_{j<i} mu_ij b*_j   (mu from fpylll, not from numpy)
    Bs = np.zeros((d, d))
    for i in range(d):
        v = B[i].copy()
        for j in range(i):
            v -= G.get_mu(i, j) * Bs[j]
        Bs[i] = v
    rr = np.array([G.get_r(i, i) for i in range(d)])
    gs_norm = np.sqrt(rr)
    recon = float(np.max(np.abs(np.linalg.norm(Bs, axis=1) - gs_norm) / gs_norm))
    Q_gs = (Bs[d - bt:] / np.linalg.norm(Bs[d - bt:], axis=1)[:, None]).T  # d x beta

    Q_qr = np.linalg.qr(B.T)[0][:, d - bt:]
    # subspace agreement: principal angles via singular values of Q_gs^T Q_qr
    sv = np.linalg.svd(Q_gs.T @ Q_qr, compute_uv=False)
    subspace_dev = float(np.max(np.abs(sv - 1.0)))

    rng = np.random.default_rng(M.seed_error(d))
    n = 1 << 15
    E = M.cbd_eta2(rng, n, d).astype(np.float64)
    n2 = (E ** 2).sum(1)
    R_gs = ((E @ Q_gs) ** 2).sum(1) / n2
    R_qr = ((E @ Q_qr) ** 2).sum(1) / n2
    OUT["V1_gram_schmidt_vs_numpy_qr"] = {
        "basis": tag,
        "fpylll_mu_reconstruction_max_rel_err": recon,
        "tail_subspace_principal_angle_max_dev_from_1": subspace_dev,
        "R_max_abs_diff_over_%d_errors" % n: float(np.max(np.abs(R_gs - R_qr))),
        "R_mean_gram_schmidt": float(R_gs.mean()),
        "R_mean_numpy_qr": float(R_qr.mean()),
        "verdict": "PASS" if (subspace_dev < 1e-8
                              and np.max(np.abs(R_gs - R_qr)) < 1e-9) else "FAIL",
    }

    # ---------------- V2: Beta quantiles by bisection on beta.cdf
    v2 = {}
    for ck, cell in res["cells"].items():
        a, b = cell["forced_values"]["beta_params"]["a"], cell["forced_values"]["beta_params"]["b"]
        for lvl, p in (("p2em10", 2.0 ** -10), ("p2em16", 2.0 ** -16)):
            got = cell["forced_values"]["beta_quantiles"][lvl]
            ref = bisect_ppf(a, b, p)
            v2[f"{ck}_{lvl}"] = {"results_json": got, "bisection": ref,
                                 "rel_diff": abs(got - ref) / ref}
    v2["verdict"] = "PASS" if all(x["rel_diff"] < 1e-9 for k, x in v2.items()
                                  if k != "verdict") else "FAIL"
    OUT["V2_beta_quantiles_independent"] = v2

    # ---------------- V3: forced values, numerically
    rng3 = np.random.default_rng(4242)
    P = np.linalg.qr(rng3.standard_normal((d, bt)))[0]
    e = M.cbd_eta2(rng3, 1 << 18, d).astype(np.float64)
    Rf = ((e @ P) ** 2).sum(1) / (e ** 2).sum(1)
    h = d // 2
    sc = np.empty(d); sc[:h] = M.C1; sc[h:] = M.C2
    ea = e * sc
    Ra = ((ea @ P) ** 2).sum(1) / (ea ** 2).sum(1)
    Sig = np.diag(sc ** 2)
    trPS = float(np.trace(P.T @ Sig @ P))
    OUT["V3_forced_values"] = {
        "E_R_measured_fixed_haar_projector_isotropic": float(Rf.mean()),
        "E_R_forced_beta_over_d": bt / d,
        "abs_diff": abs(float(Rf.mean()) - bt / d),
        "note_isotropic": ("E[R] = beta/d is FORCED for ANY fixed rank-beta "
                           "projector and iid equal-variance coordinates. It "
                           "carries zero information about the basis."),
        "E_R_measured_anisotropic": float(Ra.mean()),
        "E_R_closed_form_tr_P_Sigma_over_tr_Sigma": trPS / float(np.trace(Sig)),
        "abs_diff_aniso": abs(float(Ra.mean()) - trPS / float(np.trace(Sig))),
        "aniso_scales_c1_c2": [M.C1, M.C2],
        "matched_total_variance_check_(c1^2+c2^2)/2": (M.C1 ** 2 + M.C2 ** 2) / 2,
        "sd_ratio_c1_over_c2": M.C1 / M.C2,
        "effective_dimension_ratio_d_over_deff": float(
            (np.trace(Sig) ** 2 / np.trace(Sig @ Sig)) ** -1 * d),
    }

    # ---------------- V4: (b) and (c) recomputed for one cell from scratch
    Qs = []
    for i in range(8):
        FPLLL.set_random_seed(M.seed_basis(d, bt, i))
        Ai = IntegerMatrix.random(d, "qary", k=d // 2, q=Q_MOD)
        LLL.reduction(Ai)
        BKZReduction(Ai)(BKZ.Param(block_size=bt,
                                   strategies=[Strategy(x) for x in range(bt + 1)],
                                   max_loops=2, flags=BKZ.MAX_LOOPS))
        Bi = np.array([[Ai[r, c] for c in range(d)] for r in range(d)],
                      dtype=np.float64)
        Qs.append(np.linalg.qr(Bi.T)[0][:, d - bt:])
    rng4 = np.random.default_rng(M.seed_error(d))
    N = 1 << 20
    Rall = np.empty((N, 8))
    n2f = np.empty(N)
    step = 1 << 16
    for s0 in range(0, N, step):
        Ec = M.cbd_eta2(rng4, step, d).astype(np.float64)
        nn = (Ec ** 2).sum(1)
        n2f[s0:s0 + step] = nn
        for i in range(8):
            Rall[s0:s0 + step, i] = ((Ec @ Qs[i]) ** 2).sum(1) / nn
    a, b = bt / 2.0, (d - bt) / 2.0
    flat = np.sort(Rall.reshape(-1))
    q10 = flat[int(round(2.0 ** -10 * flat.size)) - 1]
    q16 = flat[int(round(2.0 ** -16 * flat.size)) - 1]
    means = Rall.mean(axis=0)
    within = float(np.mean(Rall.var(axis=0, ddof=1)))
    between = float(means.var(ddof=1))
    got = res["cells"][key]["arms"]["real"]
    OUT["V4_independent_recomputation_of_cell"] = {
        "cell": key,
        "ratio_2em10_pooled_recomputed": float(q10 / bisect_ppf(a, b, 2.0 ** -10)),
        "ratio_2em10_pooled_results_json": got["pooled"]["p2em10"]["ratio"],
        "ratio_2em16_pooled_recomputed": float(q16 / bisect_ppf(a, b, 2.0 ** -16)),
        "ratio_2em16_pooled_results_json": got["pooled"]["p2em16"]["ratio"],
        "between_fraction_recomputed": between / (between + within),
        "between_fraction_results_json":
            got["variance_decomposition"]["between_fraction_raw"],
        "note": ("float64 throughout; measure.py uses float32 for the projection "
                 "matmul, so small differences are expected and their size is the "
                 "point of this check."),
    }

    # ---------------- V5: arithmetic self-consistency of results.json
    v5 = {}
    for ck, cell in res["cells"].items():
        s = cell["sensitivity_demonstration"]
        hn = cell["arms"]["haar_null"]["ratio_2em10_over_draws"]
        dm = cell["arms"]["demo_anisotropic"]["ratio_2em10_over_draws"]
        recomputed_met = bool(abs(dm["mean"] - hn["mean"]) >= 4 * hn["sd"])
        r = cell["arms"]["real"]
        p1 = (abs(r["pooled"]["p2em10"]["ratio"] - 1) <= 0.05
              and abs(r["pooled"]["p2em16"]["ratio"] - 1) <= 0.10)
        p2 = r["variance_decomposition"]["between_fraction_raw"] <= 0.20
        v5[ck] = {
            "sensitivity_met_recomputed": recomputed_met,
            "sensitivity_met_in_results": s["met"],
            "sensitivity_agrees": recomputed_met == s["met"],
            "P1_recomputed": p1,
            "P1_in_results": cell["verdict_on_the_real_arm"]["P1"]["pass"],
            "P2_recomputed": p2,
            "P2_in_results": cell["verdict_on_the_real_arm"]["P2"]["pass"],
            "E_R_real_measured": r["pooled"]["mean"],
            "E_R_forced": cell["forced_values"]["E_R_forced"],
            "E_R_abs_dev_FORCED_ZERO_INFORMATION":
                abs(r["pooled"]["mean"] - cell["forced_values"]["E_R_forced"]),
        }
    v5["verdict"] = "PASS" if all(
        v["sensitivity_agrees"] and v["P1_recomputed"] == v["P1_in_results"]
        and v["P2_recomputed"] == v["P2_in_results"]
        for k, v in v5.items() if k != "verdict") else "FAIL"
    OUT["V5_results_json_self_consistency"] = v5

    # ---------------- V6: WHY the 4s sensitivity gate failed.
    # Claim (derived AFTER the run, recorded as a post-hoc instrument
    # diagnosis, NOT as an adjustment to the frozen threshold):
    #   for a Haar-random rank-beta projector P INDEPENDENT of e, the law of
    #   R = ||Pe||^2/||e||^2 is EXACTLY Beta(beta/2,(d-beta)/2) for EVERY fixed
    #   e != 0, by rotation invariance.  Hence the MARGINAL law of R on the
    #   demonstration arm is Beta for ANY error law, isotropic or not, and the
    #   declared demonstration statistic -- the mean over Haar draws of the
    #   2^-10 quantile ratio -- has expectation 1 on BOTH arms.  Its expected
    #   contrast is therefore EXACTLY ZERO: KN-TECH-1a5b7e mode 1, applied to
    #   the sensitivity demonstration rather than to the null.
    dv, bv, NB = 100, 30, 1 << 18
    av, bb = bv / 2.0, (dv - bv) / 2.0
    # (a) exact invariance: the single most anisotropic vector there is
    g6 = np.random.default_rng(777)
    e1 = np.zeros(dv); e1[0] = 1.0
    # R for e1 equals the squared norm of row 0 of the Haar orthonormal frame
    K = 1 << 14
    Rr1 = np.empty(K)
    for t in range(K):
        Qh = np.linalg.qr(g6.standard_normal((dv, bv)))[0]
        Rr1[t] = float((Qh[0] ** 2).sum())
    from scipy.stats import kstest
    ks1 = kstest(Rr1, "beta", args=(av, bb))
    OUT["V6a_haar_invariance_exact_for_any_fixed_e"] = {
        "fixed_e": "e = (1,0,...,0), the most anisotropic unit vector possible",
        "n_haar_draws": K, "d": dv, "beta": bv,
        "ks_statistic_vs_Beta": float(ks1.statistic),
        "ks_pvalue": float(ks1.pvalue),
        "mean": float(Rr1.mean()), "beta_over_d": bv / dv,
        "reading": ("R ~ Beta(beta/2,(d-beta)/2) exactly, for a vector with no "
                    "isotropy whatsoever. The error law is invisible to the "
                    "MARGINAL law of R when the projector is Haar."),
    }

    # (b) does the DECLARED statistic move, at 8x more projector draws?
    NE, NP = 1 << 18, 64
    g6b = np.random.default_rng(1234)
    Ez = M.cbd_eta2(g6b, NE, dv).astype(np.float64)
    n2z = (Ez ** 2).sum(1)
    h = dv // 2
    scv = np.empty(dv); scv[:h] = M.C1; scv[h:] = M.C2
    Ea = Ez * scv
    n2a = (Ea ** 2).sum(1)
    qref = bisect_ppf(av, bb, 2.0 ** -10)
    kq = int(round(2.0 ** -10 * NE))
    riso, rani, condmean_iso, condmean_ani = [], [], [], []
    for t in range(NP):
        Qh = np.linalg.qr(np.random.default_rng(5000 + t)
                          .standard_normal((dv, bv)))[0]
        Ri = ((Ez @ Qh) ** 2).sum(1) / n2z
        Ra2 = ((Ea @ Qh) ** 2).sum(1) / n2a
        riso.append(np.sort(Ri)[kq - 1] / qref)
        rani.append(np.sort(Ra2)[kq - 1] / qref)
        condmean_iso.append(Ri.mean())
        condmean_ani.append(Ra2.mean())
    riso, rani = np.array(riso), np.array(rani)
    cmi, cma = np.array(condmean_iso), np.array(condmean_ani)
    Sig = np.diag(scv ** 2)
    varP = 2 * bv * (dv - bv) / (dv ** 2 * (dv + 2))
    closed = (varP * (dv / (dv - 1.0))
              * (float(np.sum(scv ** 4)) - float(np.sum(scv ** 2)) ** 2 / dv)
              / float(np.sum(scv ** 2)) ** 2)
    OUT["V6b_declared_statistic_is_forced_to_zero_contrast"] = {
        "d": dv, "beta": bv, "n_errors": NE, "n_projector_draws": NP,
        "isotropic_mean_ratio_2em10": float(riso.mean()),
        "isotropic_sd": float(riso.std(ddof=1)),
        "isotropic_sem": float(riso.std(ddof=1) / np.sqrt(NP)),
        "anisotropic_mean_ratio_2em10": float(rani.mean()),
        "anisotropic_sd": float(rani.std(ddof=1)),
        "anisotropic_sem": float(rani.std(ddof=1) / np.sqrt(NP)),
        "shift": float(rani.mean() - riso.mean()),
        "shift_in_sem_units": float((rani.mean() - riso.mean())
                                    / np.sqrt(riso.var(ddof=1) / NP
                                              + rani.var(ddof=1) / NP)),
        "reading": ("At 8x the declared number of projector draws the DECLARED "
                    "statistic still does not separate the two error laws. The "
                    "demonstration was not underpowered by sample size; its "
                    "expected contrast is zero."),
    }
    OUT["V6c_where_the_anisotropy_IS_visible"] = {
        "var_of_conditional_mean_E[R|P]_isotropic": float(cmi.var(ddof=1)),
        "var_of_conditional_mean_E[R|P]_anisotropic": float(cma.var(ddof=1)),
        "ratio": float(cma.var(ddof=1) / cmi.var(ddof=1)),
        "closed_form_first_order_anisotropic":
            "Var_P(tr(P Sigma)/tr Sigma) = Var_Beta * (d/(d-1)) * "
            "(sum s_i^4 - (sum s_i^2)^2/d) / (sum s_i^2)^2",
        "closed_form_value": float(closed),
        "reading": ("The anisotropy is loud in the BETWEEN-PROJECTOR-DRAW "
                    "variance and silent in the marginal quantile. The declared "
                    "demonstration statistic reads the marginal."),
    }

    # ---------------- V7: numerical accuracy of the tail frame
    resid = float(np.linalg.norm(B.T - np.linalg.qr(B.T)[0] @ np.linalg.qr(B.T)[1])
                  / np.linalg.norm(B))
    Qq = np.linalg.qr(B.T)[0]
    orth = float(np.max(np.abs(Qq.T @ Qq - np.eye(d))))
    alt = {}
    for ft in ("ld", "dd", "mpfr"):
        try:
            Gm = GSO.Mat(A, float_type=ft)
            Gm.update_gso()
            gs2 = np.sqrt(np.array([Gm.get_r(i, i) for i in range(d)]))
            alt[ft] = float(np.max(np.abs(np.abs(np.diag(np.linalg.qr(B.T)[1]))
                                          - gs2) / gs2))
        except Exception as ex:
            alt[ft] = f"unavailable: {type(ex).__name__}"
    OUT["V7_tail_frame_numerics"] = {
        "basis": tag,
        "numpy_qr_backward_residual_||B^T-QR||/||B||": resid,
        "numpy_qr_orthonormality_max_abs_dev": orth,
        "max_rel_disagreement_with_fpylll_GSO_by_float_type": alt,
        "reading": ("The disagreement recorded in results.json "
                    "(instrument_checks.qr_vs_fpylll_gso_max_rel_err, up to "
                    "7.6e-7 at d=140) is fpylll's double-precision GSO, not the "
                    "numpy Householder QR that measure.py actually projects "
                    "with; the QR residual and orthonormality figures above "
                    "bound the error in the frame that was used."),
    }

    json.dump(OUT, open(os.path.join(TASK_DIR, "verification.json"), "w"), indent=1)
    print(json.dumps(OUT, indent=1))


if __name__ == "__main__":
    main()

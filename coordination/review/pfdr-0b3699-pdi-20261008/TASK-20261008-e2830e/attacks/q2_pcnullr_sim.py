"""TASK-20261008-e2830e Q2: discriminating power of PC-NULL-R criteria (i) and (ii) of
EXP-PFDR-0b3699, PRE-DATA, ON SYNTHETIC DRAWS ONLY.

Reads no data file of any experiment. Every number below that comes from the frozen
specification (experiments/EXP-PFDR-0b3699/specification.yaml) is a planning figure the
specification itself quotes; the per-curve heterogeneity is a modelling choice stated in
PARAMS["heterogeneity"]. This is not a run of any experiment.

Frozen definitions implemented (specification analysis.statistic, analysis.PC-NULL-R_rule,
analysis.calibration_G-NB-R, controls RANDOM-AS-STRUCTURED NULL PSEUDO-CELLS):
  four null arms per curve: r0, r1, r2, kn (known_null_sub), each NB(mean m_j, variance D_b m_j)
  (Poisson when D_b <= 1) independently, under G-NB-R;
  null pseudo-cell e in {r0, r1, r2, kn}: arm e scored by CC-8 against the triple of the other
  three: C_X = sum_j x_{e,j}; C_R = (1/3) sum_j sum_{a != e} x_{a,j};
  s_j^2 = ddof-1 variance of the triple on curve j; V = max(sum_j s_j^2, C_R);
  SD = sqrt(4 V / 3); z_e = (C_X - C_R) / SD; pooled over both rungs (CC-10).
  t_A = 0.99 quantile of the single-cell pooled z (kn scored against r0..r2), quantiles averaged
  over seed families as the specification averages them; synthetic t_dec = t_A (no real-data
  permutation null exists on synthetic data; t_perm on G-NB-R draws estimates the same quantile).
  (i) passes iff P(K_null >= K) >= 0.01, K = #{e : z_e > t_dec}, K_null from the simulated joint law.
  (ii) passes iff mean_e z_e lies inside the simulated 99% interval [q0.005, q0.995] of that mean.

Usage: python -I q2_pcnullr_sim.py OUT_JSON N_B [N_B ...] [--reps-cal R] [--reps-eval R] [--fam F]
"""
from __future__ import annotations

import json
import sys
import time

import numpy as np

TOKEN = 0xE2830E          # this task's token; seeds: SeedSequence([TOKEN, n_b, scenario_index, family])
CHUNK = 200

PARAMS = {
    "rung_mean_per_curve": {
        "30": 521.3333333333334 / 2000,   # spec p0_inputs: smallx-tt4-localise.json ["small_x|30"].C_R, 2000 curves
        "32": 513.6666666666666 / 2000,   # ["small_x|32"].C_R, 2000 curves
    },
    "rung_D": {
        "30": 1.0044757033248082,          # spec p0_inputs: calibration.json G-NB-R (SUB, TT, 4, 30).D
        "32": 1.0233614536015576,          # (SUB, TT, 4, 32).D
    },
    "heterogeneity": ("per-curve mean m_j = rung mean x w_j, w_j = u_j^4 / mean(u^4), u_j ~ U(0.85, 1.15) "
                      "drawn once per n_b (seed SeedSequence([TOKEN, n_b, 999])): mu_model is proportional to "
                      "s_sub^4 / N (PDI-1, L1/L2), default_fb_size makes s^4 proportional to N, and "
                      "subgroup_prime_filter tolerance 0.15 keeps |F_sub| within about +-15% of it"),
    "declared_n_b": 3400,
    "ladder": [1.0, 1.25, 1.5, 2.0],
}

# scenarios: (name, kappa per arm [r0, r1, r2, kn], dispersion override per arm or None)
SCENARIOS = [
    ("null", [1.0, 1.0, 1.0, 1.0], [None, None, None, None]),
    ("D1_kn_kappa1.10", [1.0, 1.0, 1.0, 1.10], [None, None, None, None]),
    ("D1_kn_kappa1.15", [1.0, 1.0, 1.0, 1.15], [None, None, None, None]),
    ("D2_kn_dispersion1.3", [1.0, 1.0, 1.0, 1.0], [None, None, None, 1.3]),
    ("D3_all_kappa1.10", [1.10, 1.10, 1.10, 1.10], [None, None, None, None]),
    ("D3_all_kappa1.15", [1.15, 1.15, 1.15, 1.15], [None, None, None, None]),
]


def curve_means(n_b: int):
    rng = np.random.default_rng(np.random.SeedSequence([TOKEN, n_b, 999]))
    m, D, rung = [], [], []
    for b in ("30", "32"):
        u = rng.uniform(0.85, 1.15, size=n_b)
        w = u ** 4
        w = w / w.mean()
        m.append(PARAMS["rung_mean_per_curve"][b] * w)
        D.append(np.full(n_b, PARAMS["rung_D"][b]))
        rung.append(np.full(n_b, int(b)))
    return np.concatenate(m), np.concatenate(D), np.concatenate(rung)


def draw(rng, mean: np.ndarray, D: np.ndarray, B: int) -> np.ndarray:
    """B x n counts, NB with per-curve mean and index of dispersion D (Poisson where D <= 1)."""
    out = np.empty((B, mean.size), dtype=np.int64)
    pois = D <= 1.0 + 1e-12
    if pois.any():
        out[:, pois] = rng.poisson(np.broadcast_to(mean[pois], (B, int(pois.sum()))))
    nb = ~pois
    if nb.any():
        mm, dd = mean[nb], D[nb]
        out[:, nb] = rng.negative_binomial(np.broadcast_to(mm / (dd - 1.0), (B, int(nb.sum()))),
                                           np.broadcast_to(1.0 / dd, (B, int(nb.sum()))))
    return out


def pseudo_cells(X: np.ndarray):
    """X: B x n x 4 (r0, r1, r2, kn). Returns z (B x 4), numerators (B x 4), V (B x 4)."""
    Xf = X.astype(float)
    tot = Xf.sum(axis=2)                 # B x n
    sq = (Xf * Xf).sum(axis=2)           # B x n
    Ttot = tot.sum(axis=1)               # B
    Z = np.empty((X.shape[0], 4))
    NUM = np.empty((X.shape[0], 4))
    VV = np.empty((X.shape[0], 4))
    for e in range(4):
        y = Xf[:, :, e]
        six = 3.0 * (sq - y * y) - (tot - y) ** 2   # 6 x ddof-1 variance of the triple, per curve
        S2 = six.sum(axis=1) / 6.0
        CX = y.sum(axis=1)
        CR = (Ttot - CX) / 3.0
        V = np.maximum(S2, CR)
        NUM[:, e] = CX - CR
        Z[:, e] = (CX - CR) / np.sqrt(4.0 * V / 3.0)
        VV[:, e] = V
    return Z, NUM, VV


def simulate(n_b: int, scen_idx: int, R: int, fam: int, m, D):
    name, kap, dov = SCENARIOS[scen_idx]
    rng = np.random.default_rng(np.random.SeedSequence([TOKEN, n_b, scen_idx, fam]))
    Zs, max_abs_numsum = [], 0.0
    for c0 in range(0, R, CHUNK):
        B = min(CHUNK, R - c0)
        X = np.empty((B, m.size, 4), dtype=np.int64)
        for a in range(4):
            Da = D if dov[a] is None else np.full_like(D, dov[a])
            X[:, :, a] = draw(rng, m * kap[a], Da, B)
        Z, NUM, _ = pseudo_cells(X)
        max_abs_numsum = max(max_abs_numsum, float(np.abs(NUM.sum(axis=1)).max()))
        Zs.append(Z)
    return np.concatenate(Zs), max_abs_numsum


def main(argv):
    out_path = argv[1]
    rest = argv[2:]
    nbs, reps_cal, reps_eval, fams = [], 20000, 10000, 2
    i = 0
    while i < len(rest):
        if rest[i] == "--reps-cal":
            reps_cal = int(rest[i + 1]); i += 2
        elif rest[i] == "--reps-eval":
            reps_eval = int(rest[i + 1]); i += 2
        elif rest[i] == "--fam":
            fams = int(rest[i + 1]); i += 2
        else:
            nbs.append(int(rest[i])); i += 1
    t_start = time.time()
    results = {"what": "TASK-20261008-e2830e Q2 synthetic PC-NULL-R power study (no data read)",
               "params": PARAMS, "scenarios": [s[0] for s in SCENARIOS],
               "reps_cal_per_family": reps_cal, "families_cal": fams, "reps_eval": reps_eval,
               "seed_rule": ("calibration: SeedSequence([0xE2830E, n_b, 0, family]) for family in "
                             "range(families_cal) (scenario 0 = null); evaluation: SeedSequence([0xE2830E, n_b, "
                             "scenario_index, 1000]) (independent of calibration); curve means: "
                             "SeedSequence([0xE2830E, n_b, 999])"),
               "by_n_b": {}}
    for n_b in nbs:
        m, D, rung = curve_means(n_b)
        # --- calibration: the simulated joint law under the null (families averaged as the spec does)
        tA_f, lo_f, hi_f, Kdist, cal_numsum = [], [], [], [], 0.0
        Zcal_all = []
        for f in range(fams):
            Z, ns = simulate(n_b, 0, reps_cal, f, m, D)
            cal_numsum = max(cal_numsum, ns)
            Zcal_all.append(Z)
            tA_f.append(float(np.quantile(Z[:, 3], 0.99)))   # single cell: kn against r0..r2
        t_dec = float(np.mean(tA_f))
        for Z in Zcal_all:
            mz = Z.mean(axis=1)
            lo_f.append(float(np.quantile(mz, 0.005)))
            hi_f.append(float(np.quantile(mz, 0.995)))
        lo, hi = float(np.mean(lo_f)), float(np.mean(hi_f))
        Zc = np.concatenate(Zcal_all)
        Kc = (Zc > t_dec).sum(axis=1)
        PKge = {k: float(np.mean(Kc >= k)) for k in range(5)}
        mz_c = Zc.mean(axis=1)
        cal = {"pooled_curves": int(m.size), "sum_mean_per_arm": float(m.sum()),
               "t_dec_synthetic(=t_A)": t_dec, "t_A_per_family": tA_f,
               "mean_z_interval_99": [lo, hi], "mean_z_interval_per_family": [lo_f, hi_f],
               "mean_z_null_mean": float(mz_c.mean()), "mean_z_null_sd": float(mz_c.std(ddof=1)),
               "single_z_null_sd": float(Zc[:, 3].std(ddof=1)),
               "P_K_null_ge_k": PKge,
               "max_abs_sum_of_four_numerators": cal_numsum}
        # --- evaluation of each scenario on independent seeds
        ev = {}
        for s_idx, (name, kap, dov) in enumerate(SCENARIOS):
            Z, ns = simulate(n_b, s_idx, reps_eval, 1000, m, D)
            K = (Z > t_dec).sum(axis=1)
            pk = np.array([PKge[int(k)] for k in K])
            fail_i = pk < 0.01
            mz = Z.mean(axis=1)
            fail_ii = (mz < lo) | (mz > hi)
            ev[name] = {
                "P_fail_i": float(fail_i.mean()), "P_fail_ii": float(fail_ii.mean()),
                "P_fail_PC_NULL_R": float((fail_i | fail_ii).mean()),
                "P_K_ge_1": float((K >= 1).mean()), "P_K_ge_2": float((K >= 2).mean()),
                "P_kn_z_gt_t_dec": float((Z[:, 3] > t_dec).mean()),
                "mean_of_mean_z": float(mz.mean()), "sd_of_mean_z": float(mz.std(ddof=1)),
                "mean_z_shift_over_null_sd": float((mz.mean() - mz_c.mean()) / mz_c.std(ddof=1)),
                "mean_z_by_arm": [float(v) for v in Z.mean(axis=0)],
                "max_abs_sum_of_four_numerators": ns,
                "mc_se_of_P_fail_at_0.01": float(np.sqrt(0.01 * 0.99 / reps_eval)),
            }
        results["by_n_b"][str(n_b)] = {"multiplier": n_b / PARAMS["declared_n_b"], "calibration": cal,
                                       "scenarios": ev}
        print(json.dumps({"n_b": n_b, "t_dec": t_dec, "interval": [lo, hi],
                          "fail": {k: [v["P_fail_i"], v["P_fail_ii"]] for k, v in ev.items()},
                          "elapsed_s": round(time.time() - t_start, 1)}), flush=True)
    results["elapsed_seconds"] = round(time.time() - t_start, 1)
    with open(out_path, "w") as fh:
        json.dump(results, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

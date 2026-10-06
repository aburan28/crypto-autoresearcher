"""J4 (c)-(f): PC-R and PC-1 from the archived counts; the dispersion model (structured and
known-null arms against the randoms); A-INT (q, upper bound), achieved X_rel (Poisson,
compound and clustered planted excess) and interval coverage at the realised n; the SS m = 4
power/transfer comparison. Own code (j4lib), own seeds:
  X_rel / q:      SeedSequence([0x87ffc4, 30, f]), f = 0..4 (4000 reps per family for X_rel,
                  20000 for q -- the producer's counts)
  coverage:       SeedSequence([0x87ffc4, 31]) (4000 synthetic designs per kappa)
  dispersion CI:  SeedSequence([0x87ffc4, 40, i]), i = cell index in (class, m) x arm order
                  (2000 curve-cluster bootstrap replicates)
  t*_adj:         SeedSequence([0x87ffc4, 41, f]) (4000 reps per family)
Command: nice -n 19 $PY attacks/j4/j4_aint.py --out attacks/j4/out/aint.json
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import j4lib as L  # noqa: E402

T_PROD = 2.848862284470068
TC_PROD = 2.306890430176141


def cell_groups(groups, arm, cls, m, rungs):
    fam = L.FAM_OF[arm]
    return [groups[(fam, cls, m, b)] for b in rungs]


def sim_cell(rng, gl, reps, arm_D_factor=1.0):
    CR = np.zeros(reps)
    Q = np.zeros(reps)
    A = np.zeros(reps)
    for g in gl:
        cr, q, a = L.sim_group(rng, g, reps, arm_D=max(g.D * arm_D_factor, 1.0), n_arms=1)
        CR += cr
        Q += q
        A += a[:, 0]
    return CR, Q, A


def excess(rng, gl, kappa, kind, reps):
    ex = np.zeros(reps)
    for g in gl:
        mu = (kappa - 1.0) * g.M
        if mu <= 0:
            continue
        if kind == "poisson" or (kind == "compound" and g.D <= 1.0):
            ex += rng.poisson(mu, size=reps)
        elif kind == "compound":
            ex += rng.negative_binomial(mu / (g.D - 1.0), 1.0 / g.D, size=reps)
        elif kind == "clustered3":
            ex += 3 * rng.poisson(mu / 3.0, size=reps)
    return ex


def xrel(gl, t, reps=4000, fams=5, seed_tag=30, kinds=("poisson", "compound", "clustered3"),
         arm_D_factor=1.0):
    pw = {k: np.zeros(len(L.GRID)) for k in kinds}
    for f in range(fams):
        rng = np.random.default_rng(np.random.SeedSequence([0x87FFC4, seed_tag, f]))
        CR, Q, A0 = sim_cell(rng, gl, reps, arm_D_factor)
        for k in kinds:
            for gi, kap in enumerate(L.GRID):
                z = L.zvec(A0 + excess(rng, gl, kap, k, reps), CR, Q)
                pw[k][gi] += float(np.mean(z > t)) / fams
    out = {}
    for k in kinds:
        hit = [kap for kap, p in zip(L.GRID, pw[k]) if p >= 0.5]
        out[k] = hit[0] if hit else None
        out["power_at_1.15_" + k] = float(pw[k][L.GRID.index(1.15)])
        out["power_at_1.50_" + k] = float(pw[k][L.GRID.index(1.5)])
    out["X_rel_frozen"] = None if (out["poisson"] is None or out["compound"] is None) else max(out["poisson"], out["compound"])
    return out


def aint_q(gl, kap, reps=20000, fams=5, seed_tag=30):
    q2, q1, q1s = [], [], []
    for f in range(fams):
        rng = np.random.default_rng(np.random.SeedSequence([0x87FFC4, seed_tag, 100 + f]))
        CR, Q, A0 = sim_cell(rng, gl, reps)
        if kap >= 1:
            A = A0 + excess(rng, gl, kap, "poisson", reps)
        else:
            A = rng.binomial(A0.astype(np.int64), kap)
        V = np.maximum(Q, CR)
        SE = np.sqrt(V * 4 / 3) / CR
        with np.errstate(divide="ignore", invalid="ignore"):
            dev = (A / CR - kap) / SE
        dev = dev[np.isfinite(dev)]
        q2.append(float(np.quantile(np.abs(dev), 0.975)))
        q1.append(float(np.quantile(np.abs(dev), 0.95)))
        q1s.append(float(np.quantile(-dev, 0.95)))  # one-sided: kappa - kappa_hat <= q SE
    return {"q2_abs_0975": float(np.mean(q2)), "q1_abs_095": float(np.mean(q1)),
            "q1_onesided_095": float(np.mean(q1s)), "per_family_q2": q2}


def coverage(gl, kappas=(1.0, 1.15), designs=4000):
    rng = np.random.default_rng(np.random.SeedSequence([0x87FFC4, 31]))
    grid = [round(0.70 + 0.05 * i, 2) for i in range(17)]
    qtab = {g: aint_q(gl, g, reps=4000, fams=1, seed_tag=32) for g in grid}
    gq2 = np.array([qtab[g]["q2_abs_0975"] for g in grid])
    gq1 = np.array([qtab[g]["q1_abs_095"] for g in grid])
    out = {}
    for kap in kappas:
        CR, Q, A0 = sim_cell(rng, gl, designs)
        A = A0 + (excess(rng, gl, kap, "poisson", designs) if kap > 1 else 0)
        V = np.maximum(Q, CR)
        SE = np.sqrt(V * 4 / 3) / CR
        kh = A / CR
        q2 = np.interp(kh, grid, gq2)
        q1 = np.interp(kh, grid, gq1)
        ok = np.isfinite(kh) & (CR > 0)
        two = np.abs(kh - kap) <= q2 * SE
        one = kap <= kh + q1 * SE
        out[str(kap)] = {"designs": int(ok.sum()), "two_sided_coverage": float(np.mean(two[ok])),
                         "one_sided_upper_coverage": float(np.mean(one[ok])),
                         "mc_se": float(math.sqrt(0.95 * 0.05 / max(1, ok.sum())))}
    return out


def dispersion_ratio(rows, groups, arm, cls, m, rungs, boot=2000, seed_index=0):
    fam = L.FAM_OF[arm]
    Aj, Rj, rung_of = [], [], []
    for b in rungs:
        g = groups[(fam, cls, m, b)]
        A = L.arm_counts(rows, g, arm, cls, m, b)
        Aj.append(A)
        Rj.append(g.randoms)
        rung_of += [b] * len(A)
    A = np.concatenate(Aj)
    R = np.vstack(Rj)
    rung_of = np.array(rung_of)

    def stat(idx):
        a, r = A[idx], R[idx]
        nb = r.mean(axis=1)
        s2 = r.var(axis=1, ddof=1)
        if nb.sum() <= 0:
            return float("nan"), float("nan"), float("nan")
        kap = a.sum() / nb.sum()
        d = a - nb - (kap - 1) * nb
        DA = (np.sum(d * d) - s2.sum() / 3.0) / nb.sum()
        DR = s2.sum() / nb.sum()
        return DA, DR, DA / DR if DR > 0 else float("nan")

    DA, DR, rho = stat(np.arange(len(A)))
    rng = np.random.default_rng(np.random.SeedSequence([0x87FFC4, 40, seed_index]))
    bs = []
    for _ in range(boot):
        idx = np.concatenate([rng.choice(np.flatnonzero(rung_of == b), size=int(np.sum(rung_of == b)))
                              for b in rungs])
        bs.append(stat(idx)[2])
    bs = np.array(bs)
    bs = bs[np.isfinite(bs)]
    return {"D_A_hat": DA, "D_R_hat": DR, "rho_A_over_R": rho,
            "ci95": [float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))] if len(bs) else None,
            "curves": int(len(A))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--tstar-own", type=float, default=None)
    a = ap.parse_args()
    t0 = time.time()
    design = L.load_design()
    rows = L.load_extract()
    groups, rho1, drops = L.build_groups(rows, design, rho1_mode="per_family")
    res = {"task": "TASK-20261002-87ffc4", "joint": "J4", "t_star_producer": T_PROD, "t_carry_producer": TC_PROD,
           "t_star_own": a.tstar_own}
    # ---- PC-R (i), (ii) from counts
    pcr = {}
    for cls in ("TT", "TB"):
        o = L.observed_cell(rows, groups, "planted_sub", cls, 3, L.BAND)
        declared = 0
        for b in L.BAND:
            for c in groups[("SUB", cls, 3, b)].curves:
                r = rows[(b, c, 3, "planted_sub", "table")]
                if cls == "TT":
                    declared += max(1, round(r["s"] ** 4 / (6 * r["N"])))
                else:
                    declared += 1
        exc = o["C_A"] - o["C_R"]
        pcr[cls] = {"z": o["z"], "kappa_rel_planted": o["kappa_rel"], "excess": exc,
                    "declared_planted_total_from_rule": declared, "SD_null": o["SD_null"],
                    "i_z_gt_t_star": o["z"] > T_PROD,
                    "ii_within_4SD": abs(exc - declared) <= 4 * o["SD_null"],
                    "ii_window_as_fraction_of_declared": 4 * o["SD_null"] / declared,
                    "planted_kappa_vs_target": {"planted_kappa": o["kappa_rel"],
                                                "target": L.TARGET[(cls, 3)]}}
    res["PC_R_from_counts"] = pcr
    # ---- PC-1 from counts
    raw_kl = {"TT": 0, "TB": 0}
    raw_rs = {"TT": 0.0, "TB": 0.0}
    bad = []
    for b in (20, 24):
        for c in range(10, 20):
            r = rows.get((b, c, 3, "known_log", "table"))
            if r is None or r["status"] != "completed_valid":
                bad.append([b, c, "missing"])
                continue
            for cls in ("TT", "TB"):
                raw_kl[cls] += r[cls]["raw"]
                if r[cls]["n"] != 0 or r[cls]["irank"] != 0:
                    bad.append([b, c, cls, r[cls]["n"], r[cls]["irank"]])
                raw_rs[cls] += float(np.mean([rows[(b, c, 3, x, "table")][cls]["raw"] for x in L.RANDOMS["SUB"]]))
    res["PC_1_from_counts"] = {"raw_known_log": raw_kl, "raw_random_sub_mean": raw_rs,
                               "ratio_TT_TB_combined": sum(raw_kl.values()) / sum(raw_rs.values()),
                               "ratio_per_class": {k: raw_kl[k] / raw_rs[k] if raw_rs[k] else None for k in raw_kl},
                               "instances_with_nonformal_or_rank": bad}
    print("PC", json.dumps({"PC_R": pcr, "PC_1": res["PC_1_from_counts"]}, default=str)[:1500], flush=True)
    # ---- dispersion model
    disp = {}
    si = 0
    for (cls, m) in L.FAM1_CM:
        for arm in L.FAM1_ARMS + ("known_null_sub", "known_null_dick"):
            disp[f"{arm}|{cls}{m}|band"] = dispersion_ratio(rows, groups, arm, cls, m, L.BAND, seed_index=si)
            si += 1
    res["dispersion_model_band"] = disp
    print("disp done", round(time.time() - t0), flush=True)
    # ---- A-INT, X_rel, coverage per FAM-1 band cell and CARRY-1
    cells = [(arm, cls, m, L.BAND) for (cls, m) in L.FAM1_CM for arm in L.FAM1_ARMS] + [("subgroup", "TT", 3, (28,))]
    aint = {}
    for (arm, cls, m, rungs) in cells:
        cid = f"{arm}|{cls}{m}|" + ("band" if rungs == L.BAND else "28")
        is_carry = rungs != L.BAND
        gl = cell_groups(groups, arm, cls, m, rungs)
        o = L.observed_cell(rows, groups, arm, cls, m, rungs)
        kh = o["kappa_rel"]
        SE = o["SD_null"] / o["C_R"]
        q = aint_q(gl, kh)
        t = TC_PROD if is_carry else T_PROD
        xr = xrel(gl, t)
        ent = {"kappa_rel": kh, "z": o["z"], "SE": SE, "q": q,
               "ci95": [kh - q["q2_abs_0975"] * SE, kh + q["q2_abs_0975"] * SE],
               "upper95_abs_reading": kh + q["q1_abs_095"] * SE,
               "upper95_onesided_reading": kh + q["q1_onesided_095"] * SE,
               "X_rel_own": xr, "target": L.TARGET[(cls, m)]}
        if a.tstar_own and not is_carry:
            ent["X_rel_own_at_own_tstar"] = xrel(gl, a.tstar_own, kinds=("poisson", "compound"))["X_rel_frozen"]
        ent["coverage"] = coverage(gl)
        d = disp.get(f"{arm}|{cls}{m}|band")
        if d and d["ci95"] and not is_carry:
            hi = max(d["ci95"][1], 1.0)
            ent["dispersion_sensitivity"] = {
                "rho_upper95": d["ci95"][1],
                "z_adj_at_rho_hat": o["z"] / math.sqrt((max(d["rho_A_over_R"], 0) + 1 / 3) / (4 / 3)) if d["rho_A_over_R"] > 0 else None,
                "z_adj_at_rho_upper": o["z"] / math.sqrt((hi + 1 / 3) / (4 / 3)),
                "X_rel_at_rho_upper": xrel(gl, T_PROD, kinds=("poisson", "compound"), arm_D_factor=hi)["X_rel_frozen"]
                if hi > 1.0 else ent["X_rel_own"]["X_rel_frozen"]}
        if (cls, m) == ("SS", 4):
            ent["label"] = L.TA1_LABEL
        aint[cid] = ent
        print(cid, json.dumps({k: v for k, v in ent.items() if k in ("kappa_rel", "z", "upper95_abs_reading",
                                                                      "upper95_onesided_reading")}),
              ent["X_rel_own"]["X_rel_frozen"], ent["coverage"], round(time.time() - t0), flush=True)
    res["A_INT_own"] = aint
    # ---- SS m = 4 transfer (DEC-20261002-1efb1f NA-5)
    est = design["estimates"]["SS4"]
    ss4 = {"label": L.TA1_LABEL, "P0_inputs_22_24_bits": {k: est[k] for k in ("rho1", "D_R_hat", "D_R_ub95", "Mbar")},
           "P0_design_D": max(est["D_R_ub95"], 1) * 1.5,
           "P0_predicted_X_rel": design["cells"]["subgroup|SS4|band"]["X_rel"],
           "P0_predicted_power_at_1.15": design["cells"]["subgroup|SS4|band"]["power_governing"],
           "final_n_per_rung": design["final_n"]["search"]["4"]["30"], "declared_n": design["declared_n"]["search"]["4"]["30"]}
    real = {}
    for fam in ("SUB", "DICK"):
        for b in L.BAND:
            g = groups[(fam, "SS", 4, b)]
            pairs = rel = 0
            for c in g.curves:
                for x in L.RANDOMS[fam]:
                    r = rows[(b, c, 4, x, "search")]
                    pairs += r["SSx"]["pairs"]
                    rel += r["SSx"]["raw"]
            real[f"{fam}|{b}"] = {"D_hat": g.D_hat, "mean_relations_per_instance": float(g.randoms.mean()),
                                  "Mbar_pairs_per_relation": pairs / rel if rel else None}
    ss4["realised_30_32_X_fix"] = real
    ss4["realised_X_rel_own"] = {k: v["X_rel_own"]["X_rel_frozen"] for k, v in aint.items() if "|SS4|" in k}
    ss4["realised_power_at_1.15_own"] = {k: v["X_rel_own"]["power_at_1.15_poisson"] for k, v in aint.items() if "|SS4|" in k}
    res["SS4_transfer"] = ss4
    res["seconds"] = time.time() - t0
    L.jdump(a.out, res)
    print("done", round(time.time() - t0))


if __name__ == "__main__":
    main()

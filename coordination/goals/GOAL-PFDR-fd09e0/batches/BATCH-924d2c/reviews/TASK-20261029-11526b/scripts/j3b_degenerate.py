"""J3b item (3): near-degenerate ok jobs and the degenerate jobs.

(a) Per (bits, r) and per cell: gap_C / mean(null_C) and standardized residuals for ok jobs in the top decile of
    gap_meta.duplicate_skips against the rest; also duplicate_skips > 0 against = 0.
(b) Exact group model of the duplicate mechanism (no curve, no label set, no coincidence count): x(Q) = x(Q') iff
    Q = +-Q', so with P_i = lambda_i G for uniform lambda in Z_N^r the half-box label sequence is determined by
    min(c.lambda mod N, N - c.lambda mod N); duplicate_skips, infinity_skips and degeneracy follow exactly. Monte
    Carlo with the recorded N of each curve of the cell gives the expected number of degenerate curves and the
    distribution of duplicate_skips under independent uniform base points, compared with the records.
Writes outputs/near-degenerate.json.
"""
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import math  # noqa: E402

import numpy as np  # noqa: E402

import common as C  # noqa: E402


def half_box(r, T):
    out = []
    for v in itertools.product(range(-T, T + 1), repeat=r):
        for e in v:
            if e != 0:
                if e > 0:
                    out.append(v)
                break
    return np.array(out, dtype=np.int64)


def need(n):
    return -(-102 * n // 100) + 8


def T_of(r, n):
    T = 1
    while ((2 * T + 1) ** r - 1) // 2 < need(n):
        T += 1
    return T


def sim_dup(V, n, N, lam):
    """duplicate_skips, infinity_skips, degenerate for one lambda vector (exact group model)."""
    vals = (V @ lam) % N
    fold = np.minimum(vals, N - vals)
    nz = fold != 0
    u, first = np.unique(fold[nz], return_index=True)
    pos_nz = np.flatnonzero(nz)
    firsts = np.sort(pos_nz[first])
    if len(firsts) < n:
        return None, None, True
    pn = firsts[n - 1]
    inf = int((~nz[:pn + 1]).sum())
    dup = int(pn + 1 - n - inf)
    return dup, inf, False


def main():
    recs = C.load_jobs()
    design = {d["cell"]: d for d in C.load_design()["toy_cells"]}
    allrec = {}
    for r in recs:
        allrec.setdefault(r["cell"], []).append(r)
    # (a) near-degenerate comparison
    def grp_stats(rs):
        if not rs:
            return None
        g = np.array([r["gap_C"] for r in rs], float)
        nul = np.array([r["null_C"] for r in rs], float)
        m, s2 = nul.mean(axis=1), nul.var(axis=1, ddof=1)
        k = g.sum() / m.sum()
        sk = math.sqrt(1.05 * s2.sum()) / m.sum()
        res = (g - m) / np.sqrt(1.05 * np.where(s2 > 0, s2, np.nan))
        return {"jobs": len(rs), "kappa": float(k), "sigma_kappa": float(sk),
                "mean_ratio": float((g / m).mean()), "mean_std_resid": float(np.nanmean(res)),
                "se_mean_std_resid": float(1 / math.sqrt(len(rs)))}

    def compare(a, b):
        if not a or not b:
            return None
        return {"top": a, "rest": b,
                "z_kappa_diff": (a["kappa"] - b["kappa"]) / math.sqrt(a["sigma_kappa"] ** 2 + b["sigma_kappa"] ** 2),
                "z_resid_diff": (a["mean_std_resid"] - b["mean_std_resid"]) / math.sqrt(a["se_mean_std_resid"] ** 2 + b["se_mean_std_resid"] ** 2)}

    strata_plan, strata_within, strata_pos = {}, {}, {}
    per_cell = {}
    for bits in (20, 24, 28):
        for r_ in (2, 3):
            ok = [x for c, v in allrec.items() for x in v
                  if x["status"] == "ok" and x["bits"] == bits and x["r"] == r_
                  and len([y for y in allrec[c] if y["status"] == "ok"]) >= design[c]["n_curves"]]
            if not ok:
                continue
            dups = np.array([x["gap_meta"]["duplicate_skips"] for x in ok])
            q90 = float(np.quantile(dups, 0.9))
            top = [x for x in ok if x["gap_meta"]["duplicate_skips"] >= q90 and x["gap_meta"]["duplicate_skips"] > 0]
            rest = [x for x in ok if x not in top]
            strata_plan[f"bits={bits},r={r_}"] = {"q90_duplicate_skips": q90, "jobs_dup_gt_0": int((dups > 0).sum()),
                                                 "jobs": len(ok), **(compare(grp_stats(top), grp_stats(rest)) or {"note": "no job with duplicate_skips > 0 at or above the 90th percentile"})}
            pos = [x for x in ok if x["gap_meta"]["duplicate_skips"] > 0]
            zero = [x for x in ok if x["gap_meta"]["duplicate_skips"] == 0]
            strata_pos[f"bits={bits},r={r_}"] = compare(grp_stats(pos), grp_stats(zero)) or {"note": "no job with duplicate_skips > 0"}
            # within-cell deciles pooled over the stratum
            tops, rests = [], []
            for c, v in allrec.items():
                v_ok = [x for x in v if x["status"] == "ok"]
                d = design[c]
                if d["bits"] != bits or d["r"] != r_ or len(v_ok) < d["n_curves"]:
                    continue
                dd = np.array([x["gap_meta"]["duplicate_skips"] for x in v_ok])
                qc = float(np.quantile(dd, 0.9))
                t_ = [x for x in v_ok if x["gap_meta"]["duplicate_skips"] >= qc and x["gap_meta"]["duplicate_skips"] > 0]
                tops += t_
                rests += [x for x in v_ok if x not in t_]
                per_cell[c] = {"jobs": len(v_ok), "dup_gt_0": int((dd > 0).sum()), "max_dup": int(dd.max()),
                               "mean_dup": float(dd.mean()),
                               "top_vs_rest": compare(grp_stats(t_), grp_stats([x for x in v_ok if x not in t_]))}
            strata_within[f"bits={bits},r={r_}"] = compare(grp_stats(tops), grp_stats(rests)) or {"note": "none"}
    # (b) exact group model of duplicates
    model = {}
    rng = C.review_np_rng("dup-model")
    for c, d in design.items():
        if d["r"] == 1:
            continue
        if d["bits"] != 20 and not (d["bits"] == 24 and d["r"] == 3):
            continue
        r_, n = d["r"], d["n"]
        T = T_of(r_, n)
        V = half_box(r_, T)
        Ns = [x["N"] for x in allrec[c]]
        draws = 400 if len(V) > 2000 else 1000
        degen = 0
        dsum = 0
        dpos = 0
        tot = 0
        dlist = []
        for Nv in Ns:
            for _ in range(draws):
                lam = rng.integers(1, Nv, size=r_)
                dup, inf, dg = sim_dup(V, n, Nv, lam)
                tot += 1
                if dg:
                    degen += 1
                else:
                    dsum += dup
                    dpos += dup > 0
                    dlist.append(dup)
        obs = allrec[c]
        obs_dup = [x["gap_meta"]["duplicate_skips"] for x in obs if x["status"] == "ok"]
        obs_deg = sum(1 for x in obs if x["status"] == "degenerate")
        p_deg = degen / tot
        lam_ = p_deg * len(Ns)
        p_ge = 1 - sum(math.exp(-lam_) * lam_ ** k / math.factorial(k) for k in range(obs_deg)) if obs_deg > 0 else 1.0
        model[c] = {"T": T, "half_box": int(len(V)), "curves": len(Ns), "draws_per_curve": draws,
                    "model_p_degenerate_per_curve": p_deg, "model_expected_degenerate_curves": lam_,
                    "observed_degenerate_curves": obs_deg, "poisson_p_ge_observed": p_ge,
                    "model_frac_dup_gt_0": dpos / max(1, tot - degen), "observed_frac_dup_gt_0": float(np.mean(np.array(obs_dup) > 0)),
                    "model_mean_dup_ok": dsum / max(1, tot - degen), "observed_mean_dup_ok": float(np.mean(obs_dup)),
                    "model_q99_dup_ok": float(np.quantile(dlist, 0.99)) if dlist else None,
                    "observed_max_dup_ok": int(max(obs_dup))}
    degen_jobs = [{k: x[k] for k in ("cell", "c", "p", "N", "status")} | {"gap_meta": x["gap_meta"]}
                  for v in allrec.values() for x in v if x["status"] != "ok"]
    C.write_json("near-degenerate.json", {
        "task": "TASK-20261029-11526b", "joint": "J3b item (3)",
        "inputs": [C.rel(C.JOBS), C.rel(C.DESIGN)],
        "method": __doc__.strip(),
        "degenerate_jobs": degen_jobs,
        "top_decile_vs_rest_plan_literal_by_bits_r": strata_plan,
        "top_decile_within_cell_pooled_by_bits_r": strata_within,
        "dup_gt_0_vs_eq_0_by_bits_r": strata_pos,
        "per_cell": per_cell,
        "duplicate_model": model,
    }, sig=6)
    for k, v in strata_plan.items():
        print("plan", k, {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items() if kk not in ("top", "rest")},
              v.get("top", {}).get("jobs"), v.get("top", {}).get("kappa"), v.get("rest", {}).get("kappa"))
    for k, v in strata_pos.items():
        print("pos", k, v.get("z_kappa_diff"), v.get("z_resid_diff"), v.get("top", {}).get("jobs"), v.get("top", {}).get("kappa"), v.get("rest", {}).get("kappa"))
    for k, v in model.items():
        print("model", k, {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()})


if __name__ == "__main__":
    main()

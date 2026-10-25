"""Red-team check H (TASK-20261023-326d39): the numbers an obstruction record would carry.

Collates, from the runs and from rt_d / rt_e / rt_f outputs:
  Q1  N_E(H) / (V_r (log H)^{r/2} / sqrt(Reg)) on the grid H in [1000, hmax] of the replication run,
      Reg = det of the verified Mordell-Weil Gram matrix in PARI normalization (rt_e). This is the
      volume form of the Neron / Lang counting law with its constant, not only its exponent.
  Q2  grid-free H_half slopes (rt_d) against 2/r.
  Q3  kernel floor lambda1^2(ker red_p) - 2 log p (rt_f), by rank.
  Q4  pigeonhole lower bound log H_half >= (sqrt(Reg) N_p / (2 V_r))^{2/r} at p = 2^256 for the
      ladder's rank-7 curve, and the rank r*(p) = 2 log p / log(2 log p) where the kernel floor
      2 log p meets the Minkowski scale of an index-p sublattice (constants dropped).
  Q5  log H_half / log p at every resolved prime (the measured regime).
"""
from __future__ import annotations

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
OUT = os.path.join(HERE, "rt_h_obstruction_numbers_output.json")


def V(r):
    return math.pi ** (r / 2) / math.gamma(r / 2 + 1)


def main():
    raw = json.load(open(os.path.join(ROOT, "experiments", "EXP-CZLIFT-a255fc", "runs", "RUN-CZLIFT-490b33", "raw-result.json")))
    curves = {cv["label"]: cv for cv in raw["raw"]["curves"]}
    e = json.load(open(os.path.join(HERE, "rt_e_mw_coordinate_null_output_H30000.json")))
    d = json.load(open(os.path.join(HERE, "rt_d_hhalf_slopes_and_definitions_output.json")))
    f = json.load(open(os.path.join(HERE, "rt_f_kernel_minimum_output.json")))
    out = {"Q1_count_over_volume_law": {}, "Q2_grid_free_hhalf_slopes": {}, "Q3_kernel_floor": {}, "Q4": {}, "Q5": {}}
    for lab, info in e["curves"].items():
        cv = curves[lab]
        r = cv["rank_recalled"]
        reg = info["regulator_det"]
        c = V(r) / math.sqrt(reg)
        ratios = {H: cv["counts"][str(H)] / (c * math.log(H) ** (r / 2)) for H in (1000, 3000, 10000, 30000, 100000, 300000)}
        out["Q1_count_over_volume_law"][lab] = {"rank": r, "Reg_PARI": round(reg, 4), "c_E": round(c, 4),
                                                "ratio_by_H": {str(k): round(v, 3) for k, v in ratios.items()},
                                                "range": [round(min(ratios.values()), 3), round(max(ratios.values()), 3)]}
        for run, blk in d.items():
            ent = blk["curves"].get(lab, {})
            if "interp_slope_uniform_Np_ln2" in ent:
                s = ent["interp_slope_uniform_Np_ln2"]
                out["Q2_grid_free_hhalf_slopes"].setdefault(lab, {})[run] = {
                    "slope": round(s["slope"], 3), "se": round(s["se"], 3), "primes": s["primes"],
                    "two_over_r": round(2 / r, 3), "grid_slope": round(ent.get("grid_slope", float("nan")), 3) if "grid_slope" in ent else None,
                    "grid_se": round(ent["grid_slope_se"], 3) if ent.get("grid_slope_se") else None}
        rows = f["curves"].get(lab, {}).get("rows", [])
        if rows:
            gaps = [x["lambda1sq_minus_2logp"] for x in rows]
            small = [x for x in rows if x["p"] <= 1200]
            out["Q3_kernel_floor"][lab] = {"rank": r, "cyclic_primes": len(rows), "min_gap": min(gaps),
                                           "gap_range_p_le_1200": [min(x["lambda1sq_minus_2logp"] for x in small), max(x["lambda1sq_minus_2logp"] for x in small)] if small else None,
                                           "median_percentile_vs_random": f["curves"][lab]["median_percentile"]}
        hh = {int(p): h for p, h in cv["h_half"].items()}
        if hh:
            out["Q5"][lab] = {str(p): round(math.log(h) / math.log(p), 3) for p, h in sorted(hh.items())}
    reg7 = e["curves"]["382623908456a1"]["regulator_det"]
    p = 2.0 ** 256
    out["Q4"] = {
        "rank7_log_H_half_lower_bound_at_2^256": (math.sqrt(reg7) * p / (2 * V(7))) ** (2 / 7),
        "illustrative_rank29_Reg1": (p / (2 * V(29))) ** (2 / 29),
        "illustrative_rank60_Reg1": (p / (2 * V(60))) ** (2 / 60),
        "r_star": {str(q): round(2 * math.log(q) / math.log(2 * math.log(q)), 1) for q in (103, 1193, 2417)} |
                  {f"2^{k}": round(2 * k * math.log(2) / math.log(2 * k * math.log(2)), 1) for k in (128, 256)},
        "pigeonhole_cap_at_half_coverage": {"N_needed_perfect_spread_over_Np": 0.5, "N_needed_uniform_over_Np": math.log(2),
                                            "delta_loglogH_max_by_rank": {str(r): round((2 / r) * math.log(2 * math.log(2)), 3) for r in range(2, 8)}},
    }
    json.dump(out, open(OUT, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()

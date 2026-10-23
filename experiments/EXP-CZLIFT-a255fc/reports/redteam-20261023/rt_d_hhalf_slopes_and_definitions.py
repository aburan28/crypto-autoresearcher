"""Red-team check D (TASK-20261023-326d39, joint R2): H_half scaling fits, their resolution, and the
definition discrepancies (prime range, cell domain, twist cells).

Reads raw-result.json by key; no producer code.
 * Per curve: resolved primes and grid H_half; OLS slope of log log H_half on log p with its
   standard error and a leave-one-out range; the log p span of the fit.
 * Grid-free H_half: interpolate log N_E(H) linearly in log log H between grid points and solve
   N_E(H*) = N*, for N* = N_p ln 2 (uniform model reaches coverage 1/2) and N* = N_p / 2
   (perfect spread, the pigeonhole floor). Slopes of log log H* on log p over all 16 primes where
   H* <= hmax, and over the grid-resolved primes only.
 * The slope implied by the growth law alone: 1 / (measured growth slope).
 * Extrapolation to log p = 256 log 2: predicted log log H_half and its spread from the slope SE.
 * Definitions: frozen cells under 'model <= 0.9 N_p' versus 'N <= 0.9 N_p'; primes inside the
   frozen range 101..20000 only; twist rows with any twist point other than O, and the twist
   median with O counted once.
"""
from __future__ import annotations

import json
import math
import os
import statistics

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
RUNS = ["RUN-CZLIFT-74f172", "RUN-CZLIFT-490b33"]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rt_d_hhalf_slopes_and_definitions_output.json")


def ols(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    if n > 2:
        s2 = sum((y - a - b * x) ** 2 for x, y in zip(xs, ys)) / (n - 2)
        se = math.sqrt(s2 / sxx)
    else:
        se = None
    return b, a, se


def loo(xs, ys):
    out = []
    for i in range(len(xs)):
        x2 = xs[:i] + xs[i + 1:]
        y2 = ys[:i] + ys[i + 1:]
        if len(x2) >= 2 and len(set(x2)) > 1:
            out.append(ols(x2, y2)[0])
    return [min(out), max(out)] if out else None


def interp_H(counts, target):
    """Solve N_E(H) = target with log N linear in log log H between grid points; None if beyond grid."""
    grid = sorted((int(h), n) for h, n in counts.items() if int(h) >= 10)
    for (h0, n0), (h1, n1) in zip(grid, grid[1:]):
        if n0 <= target <= n1 and n1 > n0:
            u0, u1 = math.log(math.log(h0)), math.log(math.log(h1))
            t = (math.log(target) - math.log(n0)) / (math.log(n1) - math.log(n0))
            return math.exp(math.exp(u0 + t * (u1 - u0)))
    return None


def frozen_a(c):
    return c["n_points"] >= 30 and c["model_distinct"] <= 0.9 * c["N_p"]


def upper_median(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else None


def main():
    out = {}
    LOGP_CRYPTO = 256 * math.log(2)
    for run in RUNS:
        raw = json.load(open(os.path.join(ROOT, "experiments", "EXP-CZLIFT-a255fc", "runs", run, "raw-result.json")))
        curves = raw["raw"]["curves"]
        hmax = raw["metrics"]["hmax"]
        block = {"hmax": hmax, "curves": {}}
        for cv in curves:
            r = cv["rank_recalled"]
            if r < 1:
                block["curves"][cv["label"]] = {"rank": 0, "h_half_recorded": cv["h_half"],
                                                "note": "no prime resolved; growth slope 0; 2/r undefined"}
                continue
            Np = {c["p"]: c["N_p"] for c in cv["coverage"]}
            res = sorted((int(p), h) for p, h in cv["h_half"].items())
            xs = [math.log(p) for p, _ in res]
            ys = [math.log(math.log(h)) for _, h in res]
            entry = {"rank": r, "predicted_2_over_r": 2 / r, "resolved": res,
                     "log_p_span": [round(min(xs), 3), round(max(xs), 3)] if xs else None,
                     "growth_slope": cv["growth_slope"],
                     "implied_by_growth_1_over_slope": 1 / cv["growth_slope"] if cv["growth_slope"] else None}
            if len(res) >= 3:
                b, a, se = ols(xs, ys)
                entry.update({"grid_slope": b, "grid_slope_se": se, "grid_slope_loo_range": loo(xs, ys),
                              "distinct_log_log_H_values": len(set(ys)),
                              "grid_slope_over_2_over_r": b / (2 / r)})
                entry["extrapolated_loglogHhalf_at_p_2^256"] = {
                    "with_fitted_slope": a + b * LOGP_CRYPTO,
                    "pm_1se": (se * (LOGP_CRYPTO - statistics.fmean(xs))) if se else None,
                    "with_2_over_r_through_fit_centroid": statistics.fmean(ys) + (2 / r) * (LOGP_CRYPTO - statistics.fmean(xs)),
                    "extrapolation_factor_in_log_p": LOGP_CRYPTO / max(xs)}
            # grid-free versions
            for tag, frac in (("uniform_Np_ln2", math.log(2)), ("perfect_spread_Np_over_2", 0.5)):
                pts = []
                for p in cv["primes"]:
                    H = interp_H(cv["counts"], frac * Np[p])
                    if H is not None:
                        pts.append((math.log(p), math.log(math.log(H))))
                if len(pts) >= 3:
                    b, a, se = ols([u for u, _ in pts], [v for _, v in pts])
                    entry[f"interp_slope_{tag}"] = {"slope": b, "se": se, "primes": len(pts),
                                                    "over_2_over_r": b / (2 / r)}
            block["curves"][cv["label"]] = entry
        # definitions
        cells_a = [c for cv in curves for c in cv["coverage"] if frozen_a(c)]
        cells_b = [c for cv in curves for c in cv["coverage"] if c["n_points"] >= 30 and c["n_points"] <= 0.9 * c["N_p"]]
        cells_c = [c for c in cells_a if 101 <= c["p"] <= 20000]
        block["definitions"] = {
            "frozen_model_le_0p9": {"cells": len(cells_a), "median": upper_median([c["ratio_to_model"] for c in cells_a]),
                                    "max_N_over_Np": max(c["n_points"] / c["N_p"] for c in cells_a)},
            "heuristic_N_le_0p9_Np": {"cells": len(cells_b), "median": upper_median([c["ratio_to_model"] for c in cells_b])},
            "primes_in_101_20000_only": {"cells": len(cells_c), "median": upper_median([c["ratio_to_model"] for c in cells_c]),
                                         "primes_used": sorted({c["p"] for c in cells_a})},
        }
        tw = [t for cv in curves for t in cv["twists"]]
        if tw:
            with_pts = [t for t in tw if t["n_twist_points"] > 1]
            per_twist = {}
            for cv in curves:
                for t in cv["twists"]:
                    per_twist.setdefault(f'{cv["label"]} D={t["D"]}', t["n_twist_points"])

            def mdl(Np, n):
                return Np * (1 - (1 - 1 / Np) ** n)

            once = [t for t in tw if t["n_base_points"] + t["n_twist_points"] - 1 >= 30
                    and mdl(t["N_p"], t["n_base_points"] + t["n_twist_points"] - 1) <= 0.9 * t["N_p"]]
            frozen_tw = [t for t in tw if t["n_base_points"] + t["n_twist_points"] >= 30 and t["model_union"] <= 0.9 * t["N_p"]]
            block["twists"] = {
                "rows": len(tw), "rows_with_a_twist_point_besides_O": len(with_pts),
                "twist_point_counts_by_curve_and_D": per_twist,
                "frozen_twist_cells": len(frozen_tw),
                "frozen_twist_cells_with_a_twist_point_besides_O": sum(1 for t in frozen_tw if t["n_twist_points"] > 1),
                "frozen_twist_median": upper_median([t["ratio_union_to_model"] for t in frozen_tw]),
                "O_counted_once": {"cells": len(once), "median": upper_median(
                    [t["distinct_union"] / mdl(t["N_p"], t["n_base_points"] + t["n_twist_points"] - 1) for t in once])},
                "gain_over_base_max": max(t["gain_over_base"] for t in tw),
            }
        out[run] = block
    json.dump(out, open(OUT, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()

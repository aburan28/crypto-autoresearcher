#!/usr/bin/env python3
"""POST-REVEAL comparison for TASK-20261001-f39c27. Written AFTER
pre_reveal_hashes.txt was sealed; reads the producer's committed
raw-result.json (RUN-SEMBIN-be48b7) and this task's blind output.

Checks
  K1  Pointwise objective agreement: evaluate the BLIND objective
      (blind_rederive.components/total, unmodified) at every producer argmin
      row whose model is covered by the task statement (ENUM, MITM,
      MITM_CAPPED; FREE is a control with oracle cost 1 and is outside the
      statement), and compare TPR, CALLS, PROBE, FILL, LA, TOTAL.
  K2  Grid reproduction: minimise the BLIND objective on the producer's
      declared domain (d in 1.0 .. n step 0.25, CALLS >= 0, s in
      0..floor(m/2)) and compare with the producer's per-degree primary
      minimum.
  K3  Localisation: grid minimum minus real-d minimum, per degree and per
      (degree, m), against the producer's reported difference from E-2.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import blind_rederive as B  # noqa: E402  (the sealed blind implementation)
import mpmath as mp  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
RAW = os.path.join(REPO, "experiments/EXP-SEMBIN-04ec3c/runs/RUN-SEMBIN-be48b7/raw-result.json")


def flt_total(lN, m, s, d):
    L = math.log2(math.factorial(m)) + lN
    xs = (L + (1 - s) * d, s * d, 2 * d)
    mx = max(xs)
    return mx + math.log2(sum(2.0 ** (x - mx) for x in xs)), L - (m - 1) * d


def main():
    prod = json.load(open(RAW))
    blind = json.load(open(os.path.join(HERE, "blind_rederive_output.json")))
    out = {"raw_result": os.path.relpath(RAW, REPO)}

    # ---- K1
    k1 = {"rows_compared": 0, "max_abs_diff": {}, "worst_row": {}, "skipped_models": {}}
    fields = ("TPR", "CALLS", "PROBE", "FILL", "LA", "TOTAL")
    for f in fields:
        k1["max_abs_diff"][f] = 0.0
    for r in prod["argmin_rows"]:
        if r["model"] == "FREE":
            k1["skipped_models"]["FREE"] = k1["skipped_models"].get("FREE", 0) + 1
            continue
        n, m, s, d = r["n"], r["m"], r["s"], mp.mpf(r["d"])
        c = B.components(n, m, s, d)
        mine = {
            "TPR": c["log2_trials_per_relation"],
            "CALLS": c["log2_total_trials"],
            "PROBE": c["probe"],
            "FILL": c["fill"],
            "LA": c["la"],
            "TOTAL": B.total(n, m, s, d),
        }
        k1["rows_compared"] += 1
        for f in fields:
            if r[f] is None:
                continue
            diff = abs(float(mine[f]) - float(r[f]))
            if diff > k1["max_abs_diff"][f]:
                k1["max_abs_diff"][f] = diff
                k1["worst_row"][f] = {"n": n, "model": r["model"], "B": r["B"], "m": m,
                                      "s": s, "d": r["d"], "producer": r[f],
                                      "blind": float(mine[f])}
    out["K1_pointwise"] = k1

    # ---- K2 + K3
    k2 = {}
    for n in B.DEGREES:
        lN = float(B.log2N(n))
        best = None
        per_m = {}
        for m in B.M_VALUES:
            for s in range(0, m // 2 + 1):
                k = 0
                while True:
                    d = 1.0 + 0.25 * k
                    if d > n + 1e-9:
                        break
                    tot, calls = flt_total(lN, m, s, d)
                    k += 1
                    if calls < 0:
                        continue
                    if best is None or tot < best[0]:
                        best = (tot, m, s, d)
                    if m not in per_m or tot < per_m[m][0]:
                        per_m[m] = (tot, s, d)
        pm = prod["per_degree_minimum"][str(n)]["n"]["primary_min"]
        e2 = prod["per_degree_minimum"][str(n)]["n"].get("E2_expectation_margin_vs_VOW")
        real = blind["degrees"][str(n)]["optimum"]["C1"]
        real_per_m = blind["degrees"][str(n)]["C1_best_per_m"]
        grid_excess_per_m = {m: round(per_m[m][0] - float(real_per_m[str(m)]["TOTAL_bits"]), 4)
                             for m in per_m if m >= 4 and m % 2 == 0}
        k2[str(n)] = {
            "blind_on_producer_grid": {"TOTAL": best[0], "m": best[1], "s": best[2], "d": best[3]},
            "producer_primary_min": {"TOTAL": pm["TOTAL"], "m": pm["m"], "s": pm["s"], "d": pm["d"],
                                     "model": pm["model"], "B": pm["B"]},
            "grid_reproduction_abs_diff": abs(best[0] - pm["TOTAL"]),
            "grid_argmin_identical": (best[1], best[2], best[3]) == (pm["m"], pm["s"], pm["d"]),
            "blind_real_d": {"TOTAL": float(real["TOTAL_bits"]), "m": real["m"], "s": real["s"],
                             "d": float(real["d"]), "margin": float(real["margin_bits"])},
            "producer_margin_vs_VOW": pm["margin_vs_VOW_bits"],
            "producer_minus_blind_real_bits": pm["TOTAL"] - float(real["TOTAL_bits"]),
            "E2": e2,
            "blind_real_minus_E2_bits": (float(real["margin_bits"]) - e2) if e2 is not None else None,
            "grid_excess_even_m_s_eq_m_over_2": grid_excess_per_m,
            "real_d_distance_below_CALLS0_boundary": float(
                (B.L_of(n, real["m"]) / (real["m"] - 1)) - mp.mpf(real["d"])),
        }
    out["K2_K3"] = k2
    json.dump(out, sys.stdout, indent=1, default=str)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()

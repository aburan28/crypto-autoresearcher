#!/usr/bin/env python3
"""N2: derive the vOW Pareto minimum under each committed metric myself, then
check (a) the run's baseline charge at every cell, (b) the convention applied to
the Nagao side at every cell, (c) the committed time-only figures, (d) O-6's
exactly-29.0-bit overcharge, (e) the AT counterfactual with processor area.

Committed definitions used (quoted in the report):
  EXP-SEMBIN-f4a17b/specification.yaml cost_metrics (the four names) and
  COST-SEMBIN-8d123b metrics_defined (the four definitions).
  vOW curve from EV-SEMBIN-71e5cd O-6: T = W(1/M + 1/w), Mem = 3n max(w, M),
  W = 0.886 * 2^{n/2}.
"""
import json
import math
from math import log2

RUN = "/workspace/experiments/EXP-SEMBIN-db9bc3/runs/RUN-SEMBIN-251fd3/"
LABELS = [163, 233, 283, 409, 571]
COMMITTED_VOW_TIME = {163: 81.3254, 233: 116.3254, 283: 141.3254,
                      409: 204.3254, 571: 285.3254}  # COST-SEMBIN-8d123b parameter_sets


def log2W(n):
    return log2(0.886) + n / 2.0


# ---- my own derivations, symbolic then numeric -----------------------------
def vow_time_only_log2(n):
    """M = 1, w -> inf  =>  T = W(1/1 + 0) = W = total sequential work."""
    return log2W(n)


def vow_product_log2(n):
    """T*Mem = 3nW(max(w,M)/M + max(w,M)/w).
    w >= M: = 3nW(w/M + 1) >= 6nW ; M >= w: = 3nW(1 + M/w) >= 6nW.
    Minimum 6nW, attained anywhere on w = M."""
    return log2(6.0 * n) + log2W(n)


def vow_equal_rate_log2(n):
    """min over (w,M) of max(T, Mem).  For a memory ceiling S = max(w,M) the
    best time is w = M = S giving T = 2W/S, so minimise max(2W/S, 3nS):
    balanced at 3nS = 2W/S => S = sqrt(2W/(3n)), value 3nS = sqrt(6nW)."""
    return 0.5 * (log2(6.0 * n) + log2W(n))


def vow_at_with_processor_area_log2(n, area_per_processor_bits):
    """counterfactual: A = 3n*max(w,M) + c*M (processors carry area).
    minimise A*T numerically over a (log2 w, log2 M) grid, then report the
    offset from 6nW."""
    best = None
    for lw in range(0, 401):
        for lM in range(0, 401):
            w, M = 2.0 ** lw, 2.0 ** lM
            # log2 of A and T computed in the log domain to avoid overflow
            logA = log2(3.0 * n * max(w, M) + area_per_processor_bits * M)
            logT = log2W(n) + log2(1.0 / M + 1.0 / w)
            v = logA + logT
            if best is None or v < best[0]:
                best = (v, lw, lM)
    return best


def main():
    out = {"derived_pareto_minima": {}, "committed_time_only_check": {},
           "o6_overcharge": {}, "at_counterfactual": {}}

    print("=== my derived vOW Pareto minima (log2) ===")
    print(f"{'n':>5} {'time_only=W':>12} {'product=6nW':>12} {'equal=sqrt(6nW)':>16} {'AT(committed)':>14}")
    for n in LABELS:
        t, pr, eq = vow_time_only_log2(n), vow_product_log2(n), vow_equal_rate_log2(n)
        out["derived_pareto_minima"][n] = {"time_only": t, "time_memory_product": pr,
                                          "equal_rate_max": eq, "area_time_AT": pr}
        print(f"{n:>5} {t:>12.4f} {pr:>12.4f} {eq:>16.4f} {pr:>14.4f}")

    print("\n=== (c) time-only charge vs COST-SEMBIN-8d123b vow_time_log2 ===")
    for n in LABELS:
        mine, comm = vow_time_only_log2(n), COMMITTED_VOW_TIME[n]
        out["committed_time_only_check"][n] = {"mine": mine, "committed": comm,
                                               "abs_diff": abs(mine - comm)}
        print(f" n={n:>3}  mine {mine:.6f}  committed {comm}  |diff| {abs(mine - comm):.2e}")

    print("\n=== (d) O-6: charging memory of a 2^30 store and time of ONE processor ===")
    print(" charged T x Mem = W * 3n * 2^30 ; Pareto min = 6nW ;")
    print(" ratio = (3n * 2^30 * W) / (6nW) = 2^30/2 = 2^29  -- n and W cancel")
    for n in [283, 310, 409, 571]:
        charged = log2W(n) + log2(3.0 * n) + 30.0
        pmin = vow_product_log2(n)
        out["o6_overcharge"][n] = charged - pmin
        print(f" n={n:>3}  charged {charged:.4f}  min {pmin:.4f}  overcharge {charged - pmin:.6f} bits")

    print("\n=== (e) AT counterfactual: processors carry area of c bits each ===")
    for n in [571]:
        for c_label, c in [("c = 3n (one point of state)", 3 * n),
                           ("c = 10n", 10 * n), ("c = 100n", 100 * n),
                           ("c = 3n*2^10", 3 * n * 1024)]:
            v, lw, lM = vow_at_with_processor_area_log2(n, c)
            off = v - vow_product_log2(n)
            out["at_counterfactual"][f"n={n},{c_label}"] = {
                "AT_min_log2": v, "offset_from_6nW_bits": off,
                "argmin_log2_w": lw, "argmin_log2_M": lM,
                "closed_form_offset_log2_1_plus_c_over_3n": log2(1 + c / (3.0 * n))}
            print(f" n={n} {c_label:<28} AT_min {v:.4f}  offset {off:+.4f} bits "
                  f"(closed form {log2(1 + c / (3.0 * n)):+.4f}), argmin (log2 w, log2 M) = ({lw},{lM})")

    # ---- (a)+(b) every cell, every margin key ------------------------------
    d = json.load(open(RUN + "cost-surface.json"))
    bad_vow, bad_nagao, conv = [], [], {}
    for c in d["cells"]:
        n = c["n"]
        time = c["time_log2_total"]
        t5f = c["T5_memory_log2_frozen_width"]
        t5d = c["T5_memory_log2_dense_width_squared"]
        for key, mg in c["margins"].items():
            metric, memr = mg["metric"], mg["memory_reading"]
            t5 = t5f if memr == "frozen_width_C_N_plus_4_4" else t5d
            expect_vow = {"time_only": vow_time_only_log2(n),
                          "time_memory_product": vow_product_log2(n),
                          "area_time_AT": vow_product_log2(n),
                          "equal_rate_max": vow_equal_rate_log2(n)}[metric]
            expect_nag = {"time_only": time,
                          "time_memory_product": time + t5,
                          "area_time_AT": time + t5,
                          "equal_rate_max": max(time, t5)}[metric]
            dv = abs(mg["vow_pareto_minimum_log2"] - expect_vow)
            dn = abs(mg["nagao_metric_log2"] - expect_nag)
            if dv > 1e-9:
                bad_vow.append((n, c["omega"], c["C_0"], key, mg["vow_pareto_minimum_log2"], expect_vow))
            if dn > 1e-9:
                bad_nagao.append((n, c["omega"], c["C_0"], c["monomial_count_reading"], key,
                                  mg["nagao_metric_log2"], expect_nag))
            # margin self-consistency
            if abs(mg["margin_bits_nagao_minus_vow"]
                   - (mg["nagao_metric_log2"] - mg["vow_pareto_minimum_log2"])) > 1e-9:
                bad_nagao.append(("MARGIN", n, key))
            if mg["nagao_ahead"] != (mg["margin_bits_nagao_minus_vow"] < 0):
                bad_nagao.append(("AHEAD_FLAG", n, key))
            conv.setdefault(metric, set()).add(mg["vow_operating_point"])
    print(f"\n=== (a) baseline charge: {len(d['cells'])} cells x 8 margin keys "
          f"= {len(d['cells']) * 8} checks ===")
    print(f" vOW charge mismatches (>1e-9): {len(bad_vow)}")
    print(f" Nagao-side convention mismatches / margin or flag inconsistencies: {len(bad_nagao)}")
    for m, s in conv.items():
        print(f"  {m}: operating point(s) declared = {sorted(s)}")
    # AT vs TxM offset across every cell
    offs = []
    for c in d["cells"]:
        for memr in ["frozen_width_C_N_plus_4_4", "dense_width_squared"]:
            a = c["margins"][f"area_time_AT|{memr}"]
            t = c["margins"][f"time_memory_product|{memr}"]
            offs.append(a["margin_bits_nagao_minus_vow"] - t["margin_bits_nagao_minus_vow"])
    print(f"\n AT minus TxM margin over all {len(offs)} (cell, memory reading) pairs: "
          f"max |offset| = {max(abs(x) for x in offs):.3e} bits")
    out["checks"] = {"cells": len(d["cells"]), "margin_checks": len(d["cells"]) * 8,
                     "vow_mismatches": len(bad_vow), "nagao_mismatches": len(bad_nagao),
                     "AT_minus_TxM_max_abs_bits": max(abs(x) for x in offs)}
    json.dump(out, open("own_vow.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()

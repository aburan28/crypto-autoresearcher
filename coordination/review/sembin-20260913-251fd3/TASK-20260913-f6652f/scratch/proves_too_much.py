"""TASK-20260913-f6652f -- the plan's proves-too-much object.

THIS FILE IMPORTS THE PRODUCER'S CODE (experiments/EXP-SEMBIN-db9bc3/code/nagao_cost.py and
its imports) AS-IS, by the review plan's own instruction: the object IS the producer's
charging evaluated at C_0 = ceil(n/3) (m = 3) and C_0 = ceil(n/2) (m = 2) at n = 571, where
'Nagao ahead' is known false by counting (#Fb ~ 2 x 2^{n/2} relations must be collected at
m = 2).  Every metric x memory reading x monomial reading is reported with nagao_ahead,
and the margin WITHOUT the T6 term is reported beside it so the plan's 'by more than the
T6 term can explain' clause can be read off.  A C_0 sweep at n = 571 is added so the
C_0-window of the model's flags is visible.  Writes proves_too_much.json."""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = "/workspace/experiments/EXP-SEMBIN-db9bc3/code"
sys.path.insert(0, CODE)

import nagao_cost as NC          # noqa: E402  (producer's code, imported deliberately)
import semaev_repro as R         # noqa: E402

N = 571
P = 2
OBJECTS = {"m=3 (C_0 = ceil(n/3))": math.ceil(N / 3), "m=2 (C_0 = ceil(n/2))": math.ceil(N / 2)}


def margin_without_T6(cell, metric, memory_reading):
    mem = (cell["T5_memory_log2_frozen_width"] if memory_reading.startswith("frozen")
           else cell["T5_memory_log2_dense_width_squared"])
    t = cell["sum_T1_to_T4_time_decompose_log2"]
    if metric == "time_only":
        nag = t
    elif metric in ("time_memory_product", "area_time_AT"):
        nag = t + mem
    else:
        nag = max(t, mem)
    return nag - R.vow_pareto_minimum(cell["n"], metric)["metric_log2"]


def main():
    out = {"n": N, "objects": {}, "sweep_n571": []}
    for label, c0 in OBJECTS.items():
        rows = []
        any_ahead = False
        for omega in NC.OMEGA_SET:
            for reading in NC.READINGS:
                cell = NC.nagao_cell(N, P, c0, omega, reading)
                for metric in NC.METRICS:
                    for memr in NC.MEMORY_READINGS:
                        mg = NC.margin(cell, metric, memr)
                        row = {"C_0": c0, "m": cell["m"], "N_frozen": cell["N_frozen"], "omega": omega,
                               "reading": reading, "metric": metric, "memory_reading": memr,
                               "T1": cell["T1_monomial_count_log2"], "T3": cell["T3_coset_constant_log2"],
                               "T4": cell["T4_inverse_yield_log2"], "T5": (cell["T5_memory_log2_frozen_width"]
                                                                          if memr.startswith("frozen") else
                                                                          cell["T5_memory_log2_dense_width_squared"]),
                               "T6": cell["T6_index_calculus_linalg_log2"],
                               "time_total": cell["time_log2_total"],
                               "time_without_T6": cell["sum_T1_to_T4_time_decompose_log2"],
                               "nagao_metric_log2": mg["nagao_metric_log2"],
                               "vow_pareto_minimum_log2": mg["vow_pareto_minimum_log2"],
                               "margin_bits": mg["margin_bits_nagao_minus_vow"],
                               "margin_bits_without_T6": margin_without_T6(cell, metric, memr),
                               "nagao_ahead": mg["nagao_ahead"],
                               "nagao_ahead_without_T6": margin_without_T6(cell, metric, memr) < 0.0,
                               "bound_B_ok": cell["C_0_satisfies_ARM_C_bound_B_1bit"]}
                        any_ahead = any_ahead or mg["nagao_ahead"]
                        rows.append(row)
        out["objects"][label] = {"C_0": c0, "any_nagao_ahead": any_ahead,
                                 "any_nagao_ahead_without_T6": any(r["nagao_ahead_without_T6"] for r in rows),
                                 "min_margin_bits": min(r["margin_bits"] for r in rows),
                                 "min_margin_bits_without_T6": min(r["margin_bits_without_T6"] for r in rows),
                                 "rows": rows}
    # C_0 sweep, binomial reading, omega = 2.807, T x M dense and frozen, time-only
    for c0 in [4, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64, 96, 128, 143, 191, 286]:
        cell = NC.nagao_cell(N, P, c0, 2.807, "binomial_C_N_plus_d_choose_d")
        out["sweep_n571"].append({
            "C_0": c0, "m": cell["m"], "T1": cell["T1_monomial_count_log2"], "T3": cell["T3_coset_constant_log2"],
            "T4": cell["T4_inverse_yield_log2"], "T6": cell["T6_index_calculus_linalg_log2"],
            "time": cell["time_log2_total"],
            "margin_time_only": NC.margin(cell, "time_only")["margin_bits_nagao_minus_vow"],
            "margin_TxM_frozen": NC.margin(cell, "time_memory_product", "frozen_width_C_N_plus_4_4")["margin_bits_nagao_minus_vow"],
            "margin_TxM_dense": NC.margin(cell, "time_memory_product", "dense_width_squared")["margin_bits_nagao_minus_vow"],
            "margin_equal_rate_frozen": NC.margin(cell, "equal_rate_max", "frozen_width_C_N_plus_4_4")["margin_bits_nagao_minus_vow"],
        })
    json.dump(out, open(os.path.join(HERE, "proves_too_much.json"), "w"), indent=1)
    for label, o in out["objects"].items():
        print(label, "C_0 =", o["C_0"], "any_nagao_ahead:", o["any_nagao_ahead"],
              "min margin:", round(o["min_margin_bits"], 2),
              "| without T6: any_ahead:", o["any_nagao_ahead_without_T6"], "min:", round(o["min_margin_bits_without_T6"], 2))
        for r in o["rows"]:
            if r["omega"] == 2.807 and r["reading"].startswith("binomial"):
                print("   ", r["metric"], r["memory_reading"], "T1", round(r["T1"], 1), "T3", round(r["T3"], 1),
                      "T6", round(r["T6"], 1), "time", round(r["time_total"], 1), "T5", round(r["T5"], 1),
                      "nagao", round(r["nagao_metric_log2"], 1), "vow", round(r["vow_pareto_minimum_log2"], 1),
                      "margin", round(r["margin_bits"], 1), "no-T6 margin", round(r["margin_bits_without_T6"], 1))
    print("sweep (omega 2.807, binomial):")
    for s in out["sweep_n571"]:
        print("   ", {k: (round(v, 1) if isinstance(v, float) else v) for k, v in s.items()})


if __name__ == "__main__":
    main()

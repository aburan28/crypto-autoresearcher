"""J2 scratch: best-case B0 complete cost over all factor-base sizes L (model only,
calibrated on RUN-ICEX-0ad4d8 per-attempt and yield measurements). No run, no draws."""
import json
import math
import sys
from math import comb

CAL = 1.708  # mean complete/model from j2_analysis_output.json fit_complete_vs_b0_model
YIELD_FRAC = 0.66  # mean pooled_yield / C(2L+4,5)/q observed in the run (0.52-0.75)


def scan_23(L):  # frozen B0: 2-sum table, backward 3-sum per attempt
    return comb(L + 2, 3) * 112 + comb(L + 1, 2) * 52 + 26 * L, 13 * L * (L + 1)


def scan_32(L):  # alternative split: 3-sum table once, backward 2-sum per attempt
    return comb(L + 1, 2) * 4 * 14 + L * 2 * 13, 13 * 8 * comb(L + 2, 3)


def total(q, L, scan):
    per, table = scan(L)
    y = min(1.0, YIELD_FRAC * comb(2 * L + 4, 5) / q)
    succ = L + 1 + 10 + 16
    return succ / y * per + table


out = {}
for q in (47059, 60821, 562333, 909289, 2 ** 24, 2 ** 32, 2 ** 64):
    ref = 13 * 0.886 * math.sqrt(q)
    row = {}
    for name, sc in (("frozen_2plus3", scan_23), ("table3_plus2", scan_32)):
        best = min(range(1, 20000 if q > 2 ** 40 else 3000), key=lambda L: total(q, L, sc))
        c = total(q, best, sc)
        row[name] = dict(best_L=best, model_units=c, ratio_to_rho_ref=c / ref,
                         table_points=sc(best)[1] // 13)
    out[str(q)] = row
print(json.dumps(out, indent=1))
json.dump(out, open(sys.argv[1], "w"), indent=1)

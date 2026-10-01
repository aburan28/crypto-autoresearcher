#!/usr/bin/env python3
"""Method-ceiling audit for the EXP-ICEX-153c34 design (arithmetic only).

Reads the committed red-team table of RUN-ICEX-0ad4d8 per-fixture quantities
(TASK-20261001-d367dd/j2_analysis_output.json) and computes, per v4 fixture:
  T          = 13*0.886*sqrt(q)/(L+27)   units per success at which the
               membership share alone equals one frozen rho reference
  T_literal  = sqrt(q)/(L+27)            EV-ICEX-16e3ec wording read literally
  B0         = EV-ICEX-16e3ec units per successful membership
  A          = attempts per success = 1/pooled yield (backend-independent:
               every exact backend decides the same predicate on the same stream)
  grid floor = A * L^5         one unit per point of the grid quotient ring
  sym floor  = A * C(L+4,5)    one unit per point of the symmetric quotient
  Rj floors  = collector R_j units per success (literal and incremental)
It also tabulates the frozen-L panel and the bit size where the incremental
R_j floor alone drops below one rho reference along L = B/2.
No run, no label, no randomness. Run: python3 ceiling_audit.py
"""
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[7]
J2 = REPO / "coordination/goals/GOAL-ICEX-001/batches/BATCH-227e0d/tasks/TASK-20261001-d367dd/j2_analysis_output.json"


def rho_ref(q):
    return 13 * 0.886 * math.sqrt(q)


def b_star(bits):
    target = 2 ** (bits - 0.5)
    b = int(target ** 0.2)
    while b ** 5 < target:
        b += 1
    return b


def main():
    rows = json.loads(J2.read_text())["per_fixture"]
    out = {"source": str(J2.relative_to(REPO)), "v4_fixtures": [], "frozen_L_panel": [], "asymptotic_floor": []}
    for r in rows:
        q, L = r["q"], r["L"]
        A = 1.0 / r["yield_pooled"]
        T = rho_ref(q) / (L + 27)
        rj_lit = r["units_per_attempt_stage1"] - r["predicted_scan_units_excl_Rj"]
        grid = A * L ** 5
        sym = A * math.comb(L + 4, 5)
        out["v4_fixtures"].append({
            "fixture_id": r["fixture_id"], "q": q, "L": L,
            "attempts_per_success": round(A, 2),
            "threshold_T_units_per_success": round(T, 2),
            "threshold_T_literal_units_per_success": round(math.sqrt(q) / (L + 27), 3),
            "b0_units_per_success_EV": r["units_per_successful_membership"],
            "b0_over_T": round(r["units_per_successful_membership"] / T, 1),
            "grid_floor_units_per_success": round(grid),
            "grid_floor_over_T": round(grid / T, 1),
            "grid_floor_over_b0": round(grid / r["units_per_successful_membership"], 3),
            "sym_floor_units_per_success": round(sym),
            "sym_floor_over_T": round(sym / T, 1),
            "rj_literal_units_per_attempt": round(rj_lit, 1),
            "rj_literal_floor_complete_over_rho_ref": round((L + 27) * A * rj_lit / rho_ref(q), 1),
            "rj_incremental_floor_complete_over_rho_ref": round((L + 27) * A * 13 / rho_ref(q), 2),
        })
    for bits in (16, 18, 20, 22, 24):
        B = b_star(bits)
        L = (B + 1) // 2
        lo, hi = max((B - 1) ** 5 + 1, 2 ** (bits - 1)), min(B ** 5, 2 ** bits - 1)
        q = math.sqrt(lo * hi)
        A = q / (0.65 * math.comb(2 * L + 4, 5))
        T = rho_ref(q) / (L + 27)
        out["frozen_L_panel"].append({
            "bits": bits, "B_star": B, "L_star": L, "p_window": [lo, hi], "q_geometric_mid": round(q),
            "attempts_per_success_at_yield_factor_0.65": round(A, 1),
            "threshold_T": round(T, 1), "grid_dim_L5": L ** 5, "sym_dim": math.comb(L + 4, 5),
            "grid_floor_over_T": round(A * L ** 5 / T, 1), "sym_floor_over_T": round(A * math.comb(L + 4, 5) / T, 1),
        })
    first_rj = None
    for bits in range(16, 65, 2):
        q = 2.0 ** bits
        B = math.ceil(q ** 0.2)
        L = max(1, B // 2)
        A = q / (0.65 * math.comb(2 * L + 4, 5))
        rj = (L + 27) * A * 13 / rho_ref(q)
        sym = (L + 27) * A * math.comb(L + 4, 5) / rho_ref(q)
        out["asymptotic_floor"].append({"bits": bits, "L": L, "rj_incremental_floor_over_rho": round(rj, 3),
                                        "sym_floor_over_rho": round(sym, 1)})
        if first_rj is None and rj < 1:
            first_rj = bits
    out["first_even_bits_where_incremental_rj_floor_below_rho"] = first_rj
    json.dump(out, sys.stdout, indent=1)
    print()


if __name__ == "__main__":
    main()

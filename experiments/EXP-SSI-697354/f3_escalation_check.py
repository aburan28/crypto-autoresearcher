#!/usr/bin/env python3
"""
Post-run escalation audit for EXP-SSI-697354 (specification.yaml
escalation_rules, and H-SSI-7fe2bf predictions.preregistered_locus_lower_bound).

This is a SEPARATE PASS over the artifacts RUN-SSI-697354-a already emitted.
It performs no new modelling: it reads p_star_table.json and asks, of every
emitted cell, whether it reports BOTH a numeric p* <= 512 AND memory
feasibility log2 w >= L_mem(p*) at log2 w <= 40.  L_mem is the same
piecewise-linear interpolation of the committed T2 column used by the run
(imported from crossover.py, not re-derived).

It also records, per log2 w, whether the pre-registered bound is satisfied
substantively or VACUOUSLY SATISFIED (satisfied only because the assessed
method is memory-infeasible at that w).

Reports observations only.  No claim, no verdict on any falsifier.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crossover  # noqa: E402

RUN = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "runs", "RUN-SSI-697354-a")


def main():
    crossover.COEF = crossover.fit_laws()
    table = json.load(open(os.path.join(RUN, "p_star_table.json")))
    rows = table["rows"]

    candidates = []
    per_w = {}
    for r in rows:
        w = r["log2_w"]
        b = per_w.setdefault(repr(w), {
            "log2_w": w, "n_cells": 0, "n_numeric": 0,
            "n_numeric_p_star_le_512": 0,
            "n_numeric_p_star_le_512_and_memory_feasible": 0,
            "n_memory_infeasible_cells": 0,
            "L_mem_at_256": crossover.L_mem(256.0)})
        b["n_cells"] += 1
        if r["outcome"] == "INFEASIBLE_AT_MEMORY":
            b["n_memory_infeasible_cells"] += 1
        if r["outcome"] != "NUMERIC":
            continue
        b["n_numeric"] += 1
        ps = r["p_star"]
        lm = crossover.L_mem(ps)
        feasible = (w >= lm)
        if ps <= 512.0:
            b["n_numeric_p_star_le_512"] += 1
            if feasible:
                b["n_numeric_p_star_le_512_and_memory_feasible"] += 1
                if w <= 40.0:
                    candidates.append({
                        "law": r["law"], "S": r["S"], "A": r["A"], "c": r["c"],
                        "MC": r["MC"], "log2_w": w, "p_star": ps,
                        "L_mem_at_p_star": lm})

    for k, b in per_w.items():
        w = b["log2_w"]
        if w > 40.0:
            b["bound_scope"] = "outside the pre-registered log2 w <= 40 range"
            continue
        if b["n_numeric_p_star_le_512_and_memory_feasible"] == 0:
            if b["n_numeric_p_star_le_512"] > 0:
                b["bound_status"] = (
                    "VACUOUSLY SATISFIED: %d cells report a numeric p* <= 512 at "
                    "this memory budget, but at each of them the assessed method "
                    "needs 2^{L_mem(p*)} table entries, which exceeds log2 w = %g, "
                    "so the method is memory-infeasible there."
                    % (b["n_numeric_p_star_le_512"], w))
            elif b["n_memory_infeasible_cells"] == b["n_cells"]:
                b["bound_status"] = (
                    "VACUOUSLY SATISFIED: every cell at this memory budget is "
                    "INFEASIBLE_AT_MEMORY.")
            else:
                b["bound_status"] = (
                    "satisfied with no numeric p* <= 512 at this memory budget.")
        else:
            b["bound_status"] = "F3 CANDIDATE PRESENT -- see candidates."

    out = {
        "audit": "F3 escalation check + vacuous-satisfaction disclosure",
        "source_artifact": "runs/RUN-SSI-697354-a/p_star_table.json",
        "n_cells_examined": len(rows),
        "criterion": ("a cell reporting BOTH a numeric p* <= 512 AND "
                      "log2 w >= L_mem(p*), at log2 w <= 40"),
        "n_F3_candidates": len(candidates),
        "F3_candidates": candidates,
        "design_time_note": ("L_mem(256) = 92.5 > 40, so no cell at log2 w <= 40 "
                             "can satisfy the feasibility half; if one did, the "
                             "implementation would be wrong before the world is."),
        "L_mem_at_256": crossover.L_mem(256.0),
        "per_log2_w": per_w,
        "interpretation": ("observations only; no security claim, no falsifier "
                           "verdict, no hypothesis status change"),
    }
    with open(os.path.join(RUN, "f3_escalation_check.json"), "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
    print(json.dumps({"n_F3_candidates": len(candidates),
                      "n_cells_examined": len(rows)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

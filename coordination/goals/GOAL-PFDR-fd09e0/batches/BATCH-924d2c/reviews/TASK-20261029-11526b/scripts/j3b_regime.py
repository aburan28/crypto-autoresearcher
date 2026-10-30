"""J3b item (1): regime of every cell. Per cell from the job records: mean p, n^2/p, E[C] per set
(formula 3 binom(n,4)/p averaged over curves, and the measured null mean per set), n/sqrt(p), and the absolute
per-set coincidence excess the reading bounds (95% curve-cluster bootstrap of (S - M)/curves, from
power-table.json). Adds the cryptographic reference row p = 2^256, n = 4096 (no computation on any real curve:
closed-form random-set mean only). Writes outputs/regime-table.json.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402


def main():
    recs = C.load_jobs()
    pt = {c["cell"]: c for c in json.load(open(os.path.join(C.OUT, "power-table.json")))["cells"]}
    rows = []
    for d in C.load_design()["toy_cells"]:
        rs = [r for r in recs if r["cell"] == d["cell"] and r["status"] == "ok"]
        ps = [r["p"] for r in rs]
        n = d["n"]
        pm = sum(ps) / len(ps)
        ec = sum(3 * math.comb(n, 4) / p for p in ps) / len(ps)
        row = {"cell": d["cell"], "bits": d["bits"], "r": d["r"], "n": n, "curves_ok": len(rs),
               "mean_p": pm, "n2_over_p": n * n / pm, "EC_formula_per_set": ec,
               "n_over_sqrt_p": n / math.sqrt(pm), "above_sqrt_p": n > math.sqrt(pm)}
        P = pt[d["cell"]]
        if P.get("assessable"):
            row.update({"EC_measured_per_set": P["mean_null_count_per_set"],
                        "excess_per_set": P["excess_coincidences_per_set"],
                        "excess_per_set_ci95": P["excess_per_set_ci95"],
                        "abs_excess_per_set_bound_95": max(abs(x) for x in P["excess_per_set_ci95"]),
                        "relative_bound_95": P["equivalence_bound_recorded_ci"]})
        else:
            row["note"] = "invalid cell: not assessable"
        rows.append(row)
    crypto = {"cell": "reference: p = 2^256, n = 4096 (not tested)", "n": 4096, "mean_p": 2.0 ** 256,
              "n2_over_p": 4096 ** 2 / 2.0 ** 256, "EC_formula_per_set": 3 * math.comb(4096, 4) / 2.0 ** 256,
              "log2_EC": math.log2(3 * math.comb(4096, 4)) - 256, "n_over_sqrt_p": 4096 / 2.0 ** 128}
    ass = [r for r in rows if "excess_per_set" in r]
    C.write_json("regime-table.json", {
        "task": "TASK-20261029-11526b", "joint": "J3b item (1)", "inputs": [C.rel(C.JOBS), "outputs/power-table.json"],
        "method": __doc__.strip(), "cells": rows, "cryptographic_reference": crypto,
        "summary": {"EC_per_set_range_tested": [min(r["EC_formula_per_set"] for r in rows), max(r["EC_formula_per_set"] for r in rows)],
                    "n_over_sqrt_p_range": [min(r["n_over_sqrt_p"] for r in rows), max(r["n_over_sqrt_p"] for r in rows)],
                    "cells_above_sqrt_p": [r["cell"] for r in rows if r["above_sqrt_p"]],
                    "smallest_abs_excess_bound_per_set": min(ass, key=lambda r: r["abs_excess_per_set_bound_95"])["cell"],
                    "abs_excess_bound_per_set_at_n256_bits28": {r["cell"]: r["abs_excess_per_set_bound_95"] for r in ass if r["bits"] == 28 and r["n"] == 256}}}, sig=6)
    for r in rows:
        print(r["cell"], "%.3g" % r["n2_over_p"], "%.3g" % r["EC_formula_per_set"], "%.3g" % r["n_over_sqrt_p"], r.get("abs_excess_per_set_bound_95"))
    print(crypto)


if __name__ == "__main__":
    main()

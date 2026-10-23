#!/usr/bin/env python3
"""Supplementary blind analysis of blind_output.json (still before opening any blind_from path).

For each lift class and section: count of cells, cells with v_z >= 2 on both P and Q
(ratio readable at the next digit), hits ratio == d, and the 1/p reference with a
binomial z-score  z = (hits - sum 1/p) / sqrt(sum (1/p)(1-1/p)).
"""
import json
import math
import sys


def main(path):
    data = json.load(open(path))
    out = {}
    for lname in ["canonical", "isomorphic", "a6+p", "a4+p", "a6+p2", "a4+p2"]:
        per = {}
        for sec in ["int", "randx", "teich", "ALL"]:
            n = hits = 0
            ref = var = 0.0
            nreadable = 0
            vP_ge2 = 0
            vP_eq1 = 0
            hits_v1 = 0
            for r in data["curves"]:
                p = r["p"]
                for c in r["lifts"][lname]["cells"]:
                    if sec != "ALL" and c["section"] != sec:
                        continue
                    n += 1
                    if c["v_z_pP"] == 1:
                        vP_eq1 += 1
                        hits_v1 += int(bool(c["ratio_equals_d"]))
                    if c["v_z_pP"] >= 2:
                        vP_ge2 += 1
                        if c["ratio_leading_digit"] is not None:
                            nreadable += 1
                            ref += 1.0 / p
                            var += (1.0 / p) * (1 - 1.0 / p)
                            hits += int(bool(c["ratio_equals_d"]))
            z = (hits - ref) / math.sqrt(var) if var > 0 else None
            per[sec] = {
                "cells": n, "v1_cells": vP_eq1, "v1_smart_hits": hits_v1,
                "v_ge2_cells": vP_ge2, "v_ge2_readable_same_valuation": nreadable,
                "v_ge2_hits": hits, "ref_sum_inv_p": round(ref, 4),
                "z": None if z is None else round(z, 3),
            }
        out[lname] = per
    # list the degenerate hits on the canonical class
    hitlist = []
    for r in data["curves"]:
        for c in r["lifts"]["canonical"]["cells"]:
            if c["v_z_pP"] >= 2 and c["ratio_equals_d"]:
                hitlist.append({"D": r["D"], "p": r["p"], "P": c["P"], "d": c["d"],
                                "section": c["section"], "vP": c["v_z_pP"], "vQ": c["v_z_pQ"]})
    out["canonical_degenerate_hits"] = hitlist
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])

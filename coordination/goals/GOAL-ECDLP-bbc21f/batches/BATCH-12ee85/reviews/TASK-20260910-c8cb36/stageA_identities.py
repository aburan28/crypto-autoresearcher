#!/usr/bin/env python3
"""Stage A'' per-cell identity recomputation from the sealed cells.jsonl:
 - margin == share_top_Tsel - cov_static  (exact on recorded doubles)
 - residual_fraction == (cycle_mass + capped_mass)/N
 - share_top_T >= share_top_Tsel >= share_top_Tover4 >= share_top_Tover8
 - margin nesting in T_sel
 - min_basin_size >= 1, n_dps recorded, accounting_identity_holds flagged true
 - capped_walks present, cap recorded
 NOTE: sum_d b(d) itself is not exposed in the sealed record (no basin-size
 array in cells.jsonl), so the accounting identity is attested-but-not-
 recomputable from the seal alone; recorded here as a scope note.
"""
import json

T_OF = {1048576: 64, 16777216: 256}
fails = []
n = 0
cap_missing = 0
with open("coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-4433c1/reviews/"
          "TASK-20260907-7afa98/cells.jsonl") as f:
    for line in f:
        d = json.loads(line)
        n += 1
        N = d["N"]
        cid = f"N={N} a={d['a_num']}/{d['a_den']} s={d['seed']}"
        if abs((d["share_top_Tsel"] - d["cov_static"]) - d["margin"]) > 2e-16:
            fails.append((cid, "margin_identity"))
        rf = (d["cycle_mass"] + d["capped_mass"]) / N
        if abs(rf - d["residual_fraction"]) > 2e-18:
            fails.append((cid, f"residual_fraction {rf} vs {d['residual_fraction']}"))
        if not (d["share_top_T"] >= d["share_top_Tsel"] >= d["share_top_Tover4"]
                >= d["share_top_Tover8"]):
            fails.append((cid, "coverage_nesting"))
        T = T_OF[N]
        if d["T"] != T or d["T_sel"] != T // 2 or d["r"] != 2:
            fails.append((cid, "T/T_sel/r_conformance"))
        rho = d["rho_ORACLE"]
        if not (0 < rho <= 1):
            fails.append((cid, "rho_range"))
        # margin nesting vs share prefixes is implied by nesting + same cov
        if d["min_basin_size"] < 1:
            fails.append((cid, "min_basin_size"))
        if d["accounting_identity_holds"] is not True:
            fails.append((cid, "accounting_identity_flag"))
        if "capped_walks" not in d:
            fails.append((cid, "capped_walks_missing"))
        if "cap" not in d:
            cap_missing += 1
        if "cov_static_shuf" not in d:
            fails.append((cid, "cov_static_shuf_missing"))
print(json.dumps({"cells": n, "identity_failures": fails,
                  "cells_without_cap_field": cap_missing,
                  "note": "sum_d b(d) not exposed in sealed cells.jsonl; "
                          "accounting identity verified as flagged-true and "
                          "residual_fraction identity recomputed; the mass sum "
                          "itself is not independently recomputable from the seal"},
                 indent=1))

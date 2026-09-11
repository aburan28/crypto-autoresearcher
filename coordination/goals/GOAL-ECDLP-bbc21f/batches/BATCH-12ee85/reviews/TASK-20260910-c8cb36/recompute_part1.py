#!/usr/bin/env python3
"""J2: Stage B'' 200-cell grid -- identities, residual accounting, per-cell field
recomputation from raw basin data, params conformance, per-(N,a) aggregates,
and bootstrap CI reproduction from the recorded bootstrap seeds.

Deterministic recomputation of every recorded summary field is done from the
raw basin-size / DP arrays in raw-result.json, never copied from summary.json.
"""
import json
import math
import numpy as np
from fractions import Fraction

RUNS = {}
for nbits in (20, 24):
    for s in range(1, 26):
        rid = f"RUN-ECDLP-6ac801-v3-n{nbits}-s{s:02d}"
        RUNS[(nbits, s)] = f"experiments/EXP-ECDLP-6ac801/runs/{rid}"

A_GRID = [Fraction(1, 16), Fraction(1, 8), Fraction(3, 16), Fraction(1, 4)]
T_OF_NBITS = {20: 64, 24: 256}
N_OF_NBITS = {20: 1 << 20, 24: 1 << 24}
CAP_MULT = 8

FIELD_RES = {}   # (nbits,seed,a) -> dict of recomputed values
RAW_ID = {}      # identity re-verification counts
errors = []

for (nbits, seed), path in sorted(RUNS.items()):
    raw = json.load(open(f"{path}/raw-result.json"))
    summ = json.load(open(f"{path}/summary.json"))
    p = raw["params"]
    N = N_OF_NBITS[nbits]
    T = T_OF_NBITS[nbits]
    T_sel = T // 2
    T4, T8 = T // 4, T // 8
    # params conformance (v3 stage plan STAGE B'')
    pc = {
        "n_bits": p["n_bits"] == nbits,
        "N": p["N"] == N,
        "T": p["T"] == T,
        "T_sel": p["T_sel"] == T_sel,
        "T4": p.get("T4") == T4,
        "T8": p.get("T8") == T8,
        "r": p["r"] == 2,
        "seed": p["seed"] == seed,
        "a_grid": sorted(p["a_grid"]) == sorted(float(a) for a in A_GRID),
        "kind": p.get("kind") == "stageBpp_exact_ceiling_v3",
        "walk_key_seed": p.get("seeds", {}).get("walk_key_seed") == seed,
    }
    if not all(pc.values()):
        errors.append({"run": path, "params_conformance_failures":
                       [k for k, v in pc.items() if not v]})
    for a in A_GRID:
        key = f"a={float(a):.6f}"
        cell = raw["cells"][key]
        # ---- residual / accounting identity from raw masses
        sizes = cell["basin_sizes"]
        cm, capm = cell["cycle_mass"], cell["capped_mass"]
        N_rec = cell["N"]
        sum_b = int(sum(sizes))
        acct_exact = (sum_b + cm + capm == N_rec) and (N_rec == N)
        resfrac = Fraction(cm + capm, N)
        # ---- per-field recomputation from raw arrays
        sizes_sorted = np.sort(np.asarray(sizes, dtype=np.int64))[::-1]
        # dp array gives pool ids; pools handled below via raw pool data if present
        share_top_Tsel = Fraction(int(sizes_sorted[:T_sel].sum()), N)
        share_top_T = Fraction(int(sizes_sorted[:T].sum()), N)
        share_top_T4 = Fraction(int(sizes_sorted[:T4].sum()), N)
        share_top_T8 = Fraction(int(sizes_sorted[:T8].sum()), N)
        # cap check from formula
        W = math.sqrt(a * N / T)
        cap_formula = math.ceil(CAP_MULT * W)
        # margin vs static coverage recomputed below (needs pool weights)
        rec = {
            "n_dps": len(sizes),
            "n_basins": len(sizes),
            "sum_b": sum_b,
            "cycle_mass": cm,
            "capped_mass": capm,
            "capped_walks": cell.get("capped_walks"),
            "accounting_identity_exact": acct_exact,
            "residual_fraction": resfrac,
            "min_basin_size": int(sizes_sorted[-1]),
            "cap_formula": cap_formula,
            "cap_recorded": cell.get("cap"),
            "W_formula": W,
            "share_top_Tsel": share_top_Tsel,
            "share_top_T": share_top_T,
            "share_top_T4": share_top_T4,
            "share_top_T8": share_top_T8,
        }
        FIELD_RES[(nbits, seed, a)] = {"rec": rec, "cell": cell, "raw": raw,
                                       "summ_cell": summ["cells"].get(key)}

# Save intermediate state for part 2 (cov_static recompute needs pool data).
import pickle
with open("coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-12ee85/reviews/"
          "TASK-20260910-c8cb36/part1_state.pkl", "wb") as f:
    pickle.dump({"FIELD_RES_KEYS": list(FIELD_RES.keys())}, f)

# ---- quick identity tallies over what we have so far
tally = {
    "cells_seen": len(FIELD_RES),
    "accounting_identity_exact_all": all(
        v["rec"]["accounting_identity_exact"] for v in FIELD_RES.values()),
    "residual_fraction_matches_recorded_all": all(
        v["rec"]["residual_fraction"] == Fraction(
            str(round(v["cell"]["residual_fraction"], 15)))
        or abs(float(v["rec"]["residual_fraction"]) - v["cell"]["residual_fraction"]) < 1e-15
        for v in FIELD_RES.values()),
    "cap_matches_formula_all": all(
        v["rec"]["cap_formula"] == v["rec"]["cap_recorded"]
        for v in FIELD_RES.values()),
    "min_basin_size_ge_1_all": all(
        v["rec"]["min_basin_size"] >= 1 for v in FIELD_RES.values()),
    "share_top_Tsel_matches_recorded_all": all(
        abs(float(v["rec"]["share_top_Tsel"]) - v["cell"]["exact_top_T_sel_share"]) < 5e-16
        for v in FIELD_RES.values()),
    "share_top_T_matches_recorded_all": all(
        abs(float(v["rec"]["share_top_T"]) - v["cell"]["exact_top_T_share"]) < 5e-16
        for v in FIELD_RES.values()),
    "share_top_T4_matches_recorded_all": all(
        abs(float(v["rec"]["share_top_T4"]) - v["cell"]["exact_top_T4_share"]) < 5e-16
        for v in FIELD_RES.values()),
    "share_top_T8_matches_recorded_all": all(
        abs(float(v["rec"]["share_top_T8"]) - v["cell"]["exact_top_T8_share"]) < 5e-16
        for v in FIELD_RES.values()),
}
print(json.dumps({"tally": tally, "params_errors": errors}, indent=1))

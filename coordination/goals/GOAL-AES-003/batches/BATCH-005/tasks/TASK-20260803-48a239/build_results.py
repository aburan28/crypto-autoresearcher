#!/usr/bin/env python3
"""TASK-20260803-48a239 -- assemble RESULTS.json from the run artifacts.

Reads only files under this task directory. Every number in RESULTS.json that
is a MEASUREMENT is copied from a runs/*.json emitted by the binary; every
number that is DERIVED is computed here from those counts by stats_lib.py.
"""
import json
import os
import subprocess
import sys

import stats_lib as S

D = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(D, "runs")


def load(name):
    p = os.path.join(R, name + ".json")
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p))
    except Exception as e:
        return {"PARSE_ERROR": str(e)}


def timing():
    t = {}
    p = os.path.join(R, "timing.txt")
    if os.path.exists(p):
        for ln in open(p):
            parts = ln.split()
            if len(parts) == 3 and parts[1].startswith("exit="):
                t[parts[0]] = {"exit": int(parts[1][5:]),
                               "wall_seconds": float(parts[2][5:])}
    return t


def arm_record(name, role, note):
    d = load(name)
    tm = timing().get(name)
    if d is None:
        return {"arm": name, "role": role, "note": note,
                "status": "NOT_RUN", "MEASURED_W_ge1": None}
    if "W_ge1_nontrivial" not in d:
        return {"arm": name, "role": role, "note": note,
                "status": "INCOMPLETE_OR_IN_PROGRESS", "MEASURED_W_ge1": None,
                "raw": d}
    keep = ["arm", "sbox_spec", "sbox_seed", "sbox_first8", "rounds", "amask",
            "smask", "trials", "nontrivial_trials", "trivial_swaps_excluded",
            "seed", "arm_id", "threads", "key_hex", "thread_seeds",
            "W_ge1_by_word", "whist", "null_expectation_analytic"]
    out = {k: d.get(k) for k in keep}
    out["role"] = role
    out["note"] = note
    out["status"] = "COMPLETED"
    out["sbox_bijective_verified_before_measuring"] = d.get("sbox_bijective")
    w = d["W_ge1_nontrivial"]
    nul = d["null_expectation_analytic"]
    out["MEASURED_W_ge1"] = w
    out["NULL_EXPECTATION_analytic"] = nul
    out["EXCESS_FACTOR"] = round(w / nul, 4) if nul else None
    out["poisson_p_ge_measured_given_null"] = 1.0 - S.pois_cdf_le(w - 1, nul) if w > 0 else 1.0
    out["frozen_T5_verdict"] = "ALIVE" if (nul and w / nul >= 5.0) else "DEAD"
    out["timing"] = tm
    return out


ITEM1 = []
for k, seed in [("K1", 531001), ("K2", 531002), ("K3", 531003), ("K4", 531004)]:
    for tag, spec in [("AES", "aes"), ("R1", "rand:20260803001"), ("R2", "rand:20260803002")]:
        ITEM1.append((f"D-{tag}-{k}", tag, k, seed, spec))

SD = [("SD31-AES", "AES"), ("SD31-R1", "R1"), ("SD31-R2", "R2")]


def main():
    arms = {}
    for name, tag, blk, seed, spec in ITEM1:
        arms[name] = arm_record(
            name, "item1_deconfound_main",
            f"S-box {tag}, seed block {blk} (seed {seed}, armid {blk[1]}), r=5, A={{0}}, S={{0}}, 2^30")
    completed_blocks = []
    for blk in ["K1", "K2", "K3", "K4"]:
        names = [f"D-{t}-{blk}" for t in ("AES", "R1", "R2")]
        if all(arms[n]["status"] == "COMPLETED" for n in names):
            completed_blocks.append(blk)

    # --- design audit: is the pairing real? ---
    pairing = []
    for blk in completed_blocks:
        keys = {t: arms[f"D-{t}-{blk}"]["key_hex"] for t in ("AES", "R1", "R2")}
        seeds = {t: arms[f"D-{t}-{blk}"]["thread_seeds"] for t in ("AES", "R1", "R2")}
        pairing.append({
            "block": blk,
            "key_hex_per_sbox": keys,
            "key_identical_across_sboxes": len(set(keys.values())) == 1,
            "thread_seeds_identical_across_sboxes":
                seeds["AES"] == seeds["R1"] == seeds["R2"],
            "thread_seeds": seeds["AES"],
        })
    pairing_holds = bool(pairing) and all(
        p["key_identical_across_sboxes"] and p["thread_seeds_identical_across_sboxes"]
        for p in pairing)

    # --- T1..T5 ---
    per_sbox = {t: [arms[f"D-{t}-{b}"]["MEASURED_W_ge1"] for b in completed_blocks]
                for t in ("AES", "R1", "R2")}
    pooled_sbox = {t: sum(v) for t, v in per_sbox.items()}
    per_block = {b: sum(arms[f"D-{t}-{b}"]["MEASURED_W_ge1"] for t in ("AES", "R1", "R2"))
                 for b in completed_blocks}
    cells = [arms[f"D-{t}-{b}"]["MEASURED_W_ge1"]
             for t in ("AES", "R1", "R2") for b in completed_blocks]

    nblk = len(completed_blocks)
    exposure_per_arm = 2 ** 30
    null_per_arm = 1.0

    g1, df1, p1 = S.g2_equal_exposure([pooled_sbox[t] for t in ("AES", "R1", "R2")])
    g2, df2, p2 = S.g2_equal_exposure([per_block[b] for b in completed_blocks]) if nblk > 1 else (None, None, None)
    g3, df3, p3 = S.g2_equal_exposure(cells)
    t4 = S.exact_binom_two_sided_half(pooled_sbox["R1"], pooled_sbox["R1"] + pooled_sbox["R2"])

    tests = {
        "T1_sbox_main_effect": {
            "what": "Poisson likelihood-ratio G^2 for equality of rate across the 3 S-boxes, pooled over the completed seed blocks. Equal exposure, so raw counts.",
            "pooled_counts": pooled_sbox,
            "exposure_per_sbox_trials": exposure_per_arm * nblk,
            "null_expectation_per_sbox": null_per_arm * nblk,
            "G2": g1, "df": df1, "p_value": p1,
            "prereg_alpha": 0.05,
            "significant_at_prereg_alpha": (p1 < 0.05),
        },
        "T2_key_main_effect": {
            "what": "Same statistic pooling by seed block instead of by S-box.",
            "pooled_counts": per_block,
            "G2": g2, "df": df2, "p_value": p2,
            "significant_at_prereg_alpha": (p2 < 0.05) if p2 is not None else None,
        },
        "T3_full_cell_homogeneity": {
            "what": "G^2 over all 3 x %d cells; detects overdispersion of any origin." % nblk,
            "cells_row_major_AES_R1_R2_by_block": {
                t: dict(zip(completed_blocks, per_sbox[t])) for t in ("AES", "R1", "R2")},
            "G2": g3, "df": df3, "p_value": p3,
            "significant_at_prereg_alpha": (p3 < 0.05),
        },
        "T4_BATCH004_R1_vs_R2_contrast_retested": {
            "what": "Exact conditional binomial test at p=1/2 on pooled R1 vs pooled R2, the direct re-test of BATCH-004's two-sided p = 0.023.",
            "R1_pooled": pooled_sbox["R1"], "R2_pooled": pooled_sbox["R2"],
            "p_value_two_sided_exact": t4,
            "BATCH004_reference_p": 0.02257497267325731,
            "BATCH004_reference_counts": {"R1": 22, "R2": 41},
            "BATCH004_sign": "R2 > R1",
            "this_task_sign": ("R2 > R1" if pooled_sbox["R2"] > pooled_sbox["R1"]
                              else ("R1 > R2" if pooled_sbox["R1"] > pooled_sbox["R2"] else "tie")),
            "significant_at_prereg_alpha": (t4 < 0.05) if t4 is not None else None,
        },
        "T5_per_arm_liveness": {
            "what": "BATCH-004's frozen rule: excess factor >= 5x is ALIVE. At 2^30 the null is 1.0, so ALIVE means >= 5 hits.",
            "verdicts": {n: arms[n]["frozen_T5_verdict"] for n, *_ in
                         [(a[0],) for a in ITEM1] if arms[n]["status"] == "COMPLETED"},
        },
    }
    # fix T5 dict build
    tests["T5_per_arm_liveness"]["verdicts"] = {
        a[0]: arms[a[0]]["frozen_T5_verdict"] for a in ITEM1
        if arms[a[0]]["status"] == "COMPLETED"}

    # --- ITEM 2 ---
    b4sd = {"Y-AES-sd": {"trials": 2**30, "hits": 2, "null": 1.0, "excess": 2.0},
            "Y-R1-sd": {"trials": 2**30, "hits": 0, "null": 1.0, "excess": 0.0},
            "Y-R2-sd": {"trials": 2**30, "hits": 4, "null": 1.0, "excess": 4.0}}
    sd_arms = {}
    for name, tag in SD:
        sd_arms[name] = arm_record(
            name, "item2_structure_destroyed_control_raised",
            f"S-box {tag}, r=5, A={{0,1,2,3}} (all four plaintext words active), S={{0}}, 2^31, seed 531001 armid 1 -- same master key as the K1 main arms, amask the only difference")
    sd_side_by_side = []
    for name, tag in SD:
        new = sd_arms[name]
        old = b4sd["Y-%s-sd" % tag]
        row = {
            "sbox": tag,
            "BATCH_004_at_2p30": {"arm": "Y-%s-sd" % tag, "trials": old["trials"],
                                  "hits": old["hits"], "null": old["null"],
                                  "excess_factor": old["excess"],
                                  "within_prereg_band_2.5x": old["excess"] <= 2.5},
            "THIS_TASK_at_2p31": None,
        }
        if new["status"] == "COMPLETED":
            row["THIS_TASK_at_2p31"] = {
                "arm": name, "trials": new["trials"], "hits": new["MEASURED_W_ge1"],
                "null": new["NULL_EXPECTATION_analytic"],
                "excess_factor": new["EXCESS_FACTOR"],
                "within_prereg_band_2.5x": new["EXCESS_FACTOR"] <= 2.5,
                "exceeds_P5_falsifier_5x": new["EXCESS_FACTOR"] >= 5.0,
                "exact_upper_tail_P_ge_hits_given_null":
                    (1.0 - S.pois_cdf_le(new["MEASURED_W_ge1"] - 1, 2.0))
                    if new["MEASURED_W_ge1"] > 0 else 1.0,
            }
            ph = old["hits"] + new["MEASURED_W_ge1"]
            row["POOLED_2p30_plus_2p31"] = {
                "trials": old["trials"] + new["trials"], "hits": ph, "null": 3.0,
                "excess_factor": round(ph / 3.0, 4),
                "within_prereg_band_2.5x": (ph / 3.0) <= 2.5,
                "exact_upper_tail_P_ge_hits_given_null":
                    (1.0 - S.pois_cdf_le(ph - 1, 3.0)) if ph > 0 else 1.0,
            }
        sd_side_by_side.append(row)

    out = {
        "task_id": "TASK-20260803-48a239",
        "goal_id": "GOAL-AES-003",
        "batch": "BATCH-005",
        "role": "executor",
        "task_kind": "CONTROL TASK -- repairs two named weaknesses in an existing effect; not a search for a new one",
        "claim_tier": "toy",
        "claim_tier_basis": "r=5 of a reduced-round AES-128 permutation at 2^30-2^31 trials on one machine, under the real AES S-box and two random bijective S-boxes drawn in BATCH-004. Nothing about full-round or deployed AES; no comparison to published cryptanalysis in either direction.",
        "certificate": {"kind": "none",
                        "why": "pure measurement -- no discrete-log solve and no factor-base relation is claimed"},
        "preregistration": "PREREGISTRATION.md in this directory, written and frozen before any measurement arm was launched",
        "arms": arms,
        "sd_arms": sd_arms,
        "item_1_deconfound": {
            "design_audit": {"per_block": pairing, "PAIRING_HOLDS": pairing_holds},
            "completed_blocks": completed_blocks,
            "per_sbox_counts_by_block": {t: dict(zip(completed_blocks, per_sbox[t]))
                                         for t in ("AES", "R1", "R2")},
            "pooled_by_sbox": pooled_sbox,
            "pooled_by_key_block": per_block,
            "tests": tests,
        },
        "item_2_structure_destroyed_raised": {
            "side_by_side": sd_side_by_side,
        },
    }
    json.dump(out, open(os.path.join(D, "results_core.json"), "w"), indent=1)
    print(json.dumps({"completed_blocks": completed_blocks,
                      "pooled_by_sbox": pooled_sbox,
                      "pooled_by_key": per_block,
                      "pairing_holds": pairing_holds,
                      "T1_p": p1, "T2_p": p2, "T3_p": p3, "T4_p": t4,
                      "sd": [(r["sbox"], r["THIS_TASK_at_2p31"]) for r in sd_side_by_side]},
                     indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

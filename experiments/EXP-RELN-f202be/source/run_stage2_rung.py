#!/usr/bin/env python3
"""Stage 2-3 combined (per rung): curve-arm E enumeration (direct, point
arithmetic) + spectral cross-check for every cell, object arms, NULL-A,
NULL-B(points), NULL-B(Z/N mirrored on E), Z/N-interval E small-multiples
mirror, Bose-Chowla E mirror, predicate T_S sums. Writes
RUN-RELN-f202be-N<rung>.

Usage: python3 run_stage2_rung.py <rung_k>
"""
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import zn_integer_arms as zn
import e_arms
import direct_enumerator as de
import spectral_crosscheck as sc
import analysis as an
import runutil as ru

from harness.toycurve import EllipticCurve  # noqa: E402

RUNS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runs"))
STAGE0_DIR = os.path.join(RUNS_DIR, "RUN-RELN-f202be-stage0")
STAGE1_DIR = os.path.join(RUNS_DIR, "RUN-RELN-f202be-stage1")

MASTER_SEED = 20260906
N_NULL_DRAWS = 100

PREDICATES = e_arms.PREDICATES


def load_curves():
    with open(os.path.join(STAGE0_DIR, "curves.json")) as f:
        return json.load(f)


def load_forced_table():
    with open(os.path.join(STAGE0_DIR, "forced-value-table.json")) as f:
        return json.load(f)


def load_null_b_zn_bases():
    with open(os.path.join(STAGE1_DIR, "null_b_zn_bases.json")) as f:
        return json.load(f)


def target_array_from_counter(counter: dict, N: int, log_table: dict) -> "np.ndarray":
    import numpy as np
    arr = np.zeros(N, dtype=np.int64)
    for key, cnt in counter.items():
        idx = log_table[key if key == "O" else tuple(key) if isinstance(key, list) else key]
        arr[idx] = cnt
    return arr


def indices_of_points(points, log_table) -> list[int]:
    return [log_table[e_arms.point_key(pt)] for pt in points]


def predicate_sums(counter: dict, log_table: dict, N: int, p: int) -> dict:
    """T_S for each predicate + anchor, over an E-arm count dict keyed by
    point identity ('O' or (x,y))."""
    sums = {pr["id"]: 0 for pr in PREDICATES}
    sums["ANCHOR-LOG"] = 0
    coverage_ge1 = {pr["id"]: 0 for pr in PREDICATES}
    coverage_ge1["ANCHOR-LOG"] = 0
    total_coverage_ge1 = 0
    for key, cnt in counter.items():
        if key == "O":
            continue
        x = key[0]
        if cnt >= 1:
            total_coverage_ge1 += 1
        for pr in PREDICATES:
            if pr["fn"](x, p, N):
                sums[pr["id"]] += cnt
                if cnt >= 1:
                    coverage_ge1[pr["id"]] += 1
        if e_arms.anchor_predicate(key, log_table, N):
            sums["ANCHOR-LOG"] += cnt
            if cnt >= 1:
                coverage_ge1["ANCHOR-LOG"] += 1
    return {"T_S": sums, "coverage_ge1": coverage_ge1, "total_coverage_ge1": total_coverage_ge1}


def process_curve(rung, cinfo, frow, null_b_zn_bases, run_dir, log):
    import numpy as np

    seed = cinfo["seed"]
    p = cinfo["p"]
    a = cinfo["a"]
    b = cinfo["b"]
    N = cinfo["N"]
    curve = EllipticCurve(p, a, b)
    P = (cinfo["generator_x"], cinfo["generator_y"])

    t0 = time.time()
    log_table = e_arms.build_log_table(curve, P, N)
    log(f"  seed{seed}: log table built ({len(log_table)} entries) in {time.time()-t0:.2f}s")

    B1e = frow["B1_even"]
    B1u = frow["B1_unrounded"]
    B2 = frow["B2"]
    B2e = B2 + (B2 % 2) if B2 is not None else None
    M1 = frow["M"]
    M1_red = frow["M_red"]
    M1u = frow["M_unrounded_plain"]
    M2 = frow.get("M2")

    curve_dir = os.path.join(run_dir, "cells", f"seed{seed}")
    os.makedirs(curve_dir, exist_ok=True)
    cell_records = []
    accounting = []

    def save_cell(name, direct_counter_unred, direct_counter_red, N_, log_table_, is_negclosed,
                   base_indices):
        cdir = os.path.join(curve_dir, name)
        os.makedirs(cdir, exist_ok=True)
        arr_unred = target_array_from_counter(direct_counter_unred, N_, log_table_)
        spectral = sc.spectral_multiset_counts(base_indices, N_)
        spec_arr = spectral["c_multiset"]
        disagree = int((arr_unred != spec_arr).sum())
        np.save(os.path.join(cdir, "count-vector.npy"), arr_unred)
        with open(os.path.join(cdir, "count-vector.sha256"), "w") as f:
            f.write(ru.sha256_bytes(arr_unred.tobytes()))
        hist = {}
        for v in arr_unred:
            hist[str(int(v))] = hist.get(str(int(v)), 0) + 1
        ru.write_json(os.path.join(cdir, "histogram.json"), hist)
        rec = {
            "E3_direct_unreduced": de.sum_of_squares(direct_counter_unred),
            "INV1_unreduced": de.sum_of_counts(direct_counter_unred),
            "E3_spectral": spectral["E3"], "E3_ord": spectral["E3_ord"],
            "parseval_relative_residual": spectral["parseval_relative_residual"],
            "spectral_disagreements": disagree,
        }
        if is_negclosed and direct_counter_red is not None:
            rec["E3_direct_reduced"] = de.sum_of_squares(direct_counter_red)
            rec["INV1_reduced"] = de.sum_of_counts(direct_counter_red)
        ru.write_json(os.path.join(cdir, "spectral.json"), spectral_summary(spectral))
        return rec

    def spectral_summary(spectral):
        return {k: v for k, v in spectral.items() if k not in ("c_multiset", "c_ord")}

    results = {"seed": seed, "N": N, "B1_even": B1e, "B1_unrounded": B1u, "B2": B2, "B2_even": B2e}

    # -------------------- Object arms --------------------
    object_builders = {
        "x_interval_low": e_arms.build_x_interval_low,
        "x_interval_mid": e_arms.build_x_interval_mid,
        "qr_class": e_arms.build_qr_class,
    }
    object_results = {}
    convs = ["B1"] + (["B2"] if B2e else [])
    for arm_name, builder in object_builders.items():
        for conv in convs:
            try:
                if conv == "B1":
                    W, xs = builder(curve, B1e // 2)
                    Bsz = B1e
                    Mv = M1
                    Mred_v = M1_red
                else:
                    W, xs = builder(curve, B2e // 2)
                    Bsz = B2e
                    from math import comb
                    Mv = comb(Bsz + 2, 3)
                    Mred_v = Mv - (Bsz ** 2) // 2
            except RuntimeError as e:
                log(f"  seed{seed} {arm_name} {conv}: SKIPPED ({e})")
                continue
            t1 = time.time()
            direct = e_arms.enumerate_e(curve, W, negation_closed=True)
            base_idx = indices_of_points(W, log_table)
            rec = save_cell(f"{arm_name}_{conv}", direct["unreduced"], direct["reduced"], N, log_table, True, base_idx)
            delta_unred = an.delta_of(rec["E3_direct_unreduced"], Mv, N)
            delta_red = an.delta_of(rec["E3_direct_reduced"], Mred_v, N)
            preds_unred = predicate_sums(direct["unreduced"], log_table, N, p)
            preds_red = predicate_sums(direct["reduced"], log_table, N, p)
            forced_gap_direct = delta_unred - delta_red
            forced_gap_expected = (Bsz ** 3) / (4.0 * Mv)
            rec.update({
                "arm": arm_name, "B_conv": conv, "B": Bsz, "M": Mv, "M_red": Mred_v,
                "delta_unreduced": delta_unred, "delta_reduced": delta_red,
                "forced_negation_gap_measured": forced_gap_direct,
                "forced_negation_gap_expected": forced_gap_expected,
                "forced_gap_within_0.1": abs(forced_gap_direct - forced_gap_expected) <= 0.1,
                "predicate_T_S_unreduced": preds_unred["T_S"],
                "predicate_T_S_reduced": preds_red["T_S"],
                "INV1_ok": rec["INV1_unreduced"] == Mv and rec.get("INV1_reduced") == Mred_v,
                "INV2_ok": rec["spectral_disagreements"] == 0,
                "wall_seconds": time.time() - t1,
            })
            object_results[f"{arm_name}_{conv}"] = rec
            log(f"  seed{seed} {arm_name} {conv}: Delta_red={delta_red:.4f} gap_meas={forced_gap_direct:.3f} "
                f"gap_exp={forced_gap_expected:.3f} INV1={rec['INV1_ok']} INV2={rec['INV2_ok']} "
                f"({rec['wall_seconds']:.2f}s)")
            accounting.append({"cell": f"{arm_name}_{conv}", **{k: rec[k] for k in
                                ("INV1_ok", "INV2_ok", "forced_gap_within_0.1")}})
    results["object_arms"] = object_results

    # -------------------- NULL-A (100 draws), B1 and B2 --------------------
    null_a_results = {}
    for conv, Bhalf, Mval, Mred_val in [("B1", B1e // 2, M1, M1_red)] + (
            [("B2", B2e // 2, None, None)] if B2e else []):
        if conv == "B2":
            from math import comb
            Bsz = B2e
            Mval = comb(Bsz + 2, 3)
            Mred_val = Mval - (Bsz ** 2) // 2
        else:
            Bsz = B1e
        deltas_unred, deltas_red = [], []
        pred_z_accum = {pr["id"]: [] for pr in PREDICATES}
        pred_z_accum["ANCHOR-LOG"] = []
        max_disagree = 0
        t1 = time.time()
        for i in range(N_NULL_DRAWS):
            seed64 = zn.seed_draw_int(MASTER_SEED, rung, seed, "NULL_A", conv, i)
            W, xs = e_arms.null_a_random_x_classes(curve, Bhalf, seed64)
            direct = e_arms.enumerate_e(curve, W, negation_closed=True)
            E3u = de.sum_of_squares(direct["unreduced"])
            E3r = de.sum_of_squares(direct["reduced"])
            deltas_unred.append(an.delta_of(E3u, Mval, N))
            deltas_red.append(an.delta_of(E3r, Mred_val, N))
            base_idx = indices_of_points(W, log_table)
            arr_unred = target_array_from_counter(direct["unreduced"], N, log_table)
            spectral = sc.spectral_multiset_counts(base_idx, N)
            disagree = int((arr_unred != spectral["c_multiset"]).sum())
            max_disagree = max(max_disagree, disagree)
            if i < 5 or disagree != 0:
                # store a modest number of full artifacts (sha+hist) per draw
                cdir = os.path.join(curve_dir, f"NULL_A_{conv}", f"draw{i:03d}")
                os.makedirs(cdir, exist_ok=True)
                with open(os.path.join(cdir, "count-vector.sha256"), "w") as f:
                    f.write(ru.sha256_bytes(arr_unred.tobytes()))
                hist = {}
                for v in arr_unred:
                    hist[str(int(v))] = hist.get(str(int(v)), 0) + 1
                ru.write_json(os.path.join(cdir, "histogram.json"), hist)
                ru.write_json(os.path.join(cdir, "spectral.json"),
                              {k: v for k, v in spectral.items() if k not in ("c_multiset", "c_ord")})
                ru.write_json(os.path.join(cdir, "disagreements.json"), {"disagreements": disagree})
        band_unred = an.null_band(deltas_unred)
        band_red = an.null_band(deltas_red)
        null_a_results[conv] = {
            "B": Bsz, "M": Mval, "M_red": Mred_val,
            "band_unreduced": band_unred, "band_reduced": band_red,
            "max_spectral_disagreement_over_draws": max_disagree,
            "n_draws": N_NULL_DRAWS,
            "wall_seconds": time.time() - t1,
        }
        log(f"  seed{seed} NULL_A {conv}: band_red mean={band_red['mean']:.5f} sd={band_red['sd']:.5f} "
            f"max_spectral_disagree={max_disagree} ({time.time()-t1:.2f}s)")
    results["NULL_A"] = null_a_results

    # -------------------- NULL-B points (100 draws), B1(unrounded)+B2(raw) --------------------
    null_b_results = {}
    for conv, Bsz, Mval in [("B1", B1u, M1u)] + ([("B2", B2, None)] if B2 else []):
        if conv == "B2":
            from math import comb
            Mval = comb(B2 + 2, 3)
            Bsz = B2
        deltas = []
        flagged_pairs = 0
        max_disagree = 0
        t1 = time.time()
        for i in range(N_NULL_DRAWS):
            seed64 = zn.seed_draw_int(MASTER_SEED, rung, seed, "NULL_B_points", conv, i)
            pts, flagged = e_arms.null_b_random_points(curve, Bsz, seed64)
            if flagged:
                flagged_pairs += 1
            direct = e_arms.enumerate_e(curve, pts, negation_closed=False)
            E3 = de.sum_of_squares(direct["unreduced"])
            deltas.append(an.delta_of(E3, Mval, N))
            if i < 5:
                base_idx = indices_of_points(pts, log_table)
                arr = target_array_from_counter(direct["unreduced"], N, log_table)
                spectral = sc.spectral_multiset_counts(base_idx, N)
                disagree = int((arr != spectral["c_multiset"]).sum())
                max_disagree = max(max_disagree, disagree)
        band = an.null_band(deltas)
        null_b_results[conv] = {
            "B": Bsz, "M": Mval, "band": band, "flagged_negation_pair_draws": flagged_pairs,
            "n_draws": N_NULL_DRAWS, "spectral_disagreement_sampled_max": max_disagree,
            "wall_seconds": time.time() - t1,
        }
        log(f"  seed{seed} NULL_B_points {conv}: band mean={band['mean']:.5f} sd={band['sd']:.5f} "
            f"flagged_pairs={flagged_pairs} ({time.time()-t1:.2f}s)")
    results["NULL_B_points"] = null_b_results

    # -------------------- ZN interval + E small-multiples mirror --------------------
    t1 = time.time()
    zn_base = zn.zn_interval_base(B1u)
    e_small_mult = e_arms.scalar_mirror_points(curve, P, zn_base)
    direct_e = e_arms.enumerate_e(curve, e_small_mult, negation_closed=False)
    zn_direct = zn.enumerate_zn(zn_base, N, negation_closed=False)
    e_arr = target_array_from_counter(direct_e["unreduced"], N, log_table)
    zn_arr = ru.counter_to_zn_array(zn_direct["unreduced"], N, lambda k: int(k))
    mirror_identical = bool((e_arr == zn_arr).all())
    results["ZN_interval_E_mirror"] = {
        "B": B1u, "M": M1u, "mirror_bit_identical": mirror_identical,
        "E3_E": de.sum_of_squares(direct_e["unreduced"]), "E3_ZN": de.sum_of_squares(zn_direct["unreduced"]),
        "wall_seconds": time.time() - t1,
    }
    log(f"  seed{seed} ZN_interval/E_small_multiples mirror identical: {mirror_identical} ({time.time()-t1:.2f}s)")

    # -------------------- Bose-Chowla E mirror (if constructible) --------------------
    bc_e = None
    if B2 is not None:
        try:
            inds, order = zn.bose_chowla_set(B2)
            lifted = [i % N for i in inds]
            e_pts = e_arms.scalar_mirror_points(curve, P, lifted)
            direct_e_bc = e_arms.enumerate_e(curve, e_pts, negation_closed=False)
            zn_direct_bc = zn.enumerate_zn(lifted, N, negation_closed=False)
            e_arr_bc = target_array_from_counter(direct_e_bc["unreduced"], N, log_table)
            zn_arr_bc = ru.counter_to_zn_array(zn_direct_bc["unreduced"], N, lambda k: int(k))
            bc_e = {"mirror_bit_identical": bool((e_arr_bc == zn_arr_bc).all()),
                    "E3": de.sum_of_squares(direct_e_bc["unreduced"])}
            log(f"  seed{seed} Bose-Chowla E mirror identical: {bc_e['mirror_bit_identical']}")
        except NotImplementedError as e:
            bc_e = {"skipped": True, "reason": str(e)}
    results["bose_chowla_E_mirror"] = bc_e

    # -------------------- NULL-B Z/N mirrored on E (reuse stage1 bases) --------------------
    nbzn_results = {}
    for conv, Bsz, Mval in [("B1", B1u, M1u)] + ([("B2", B2, None)] if B2 else []):
        if conv == "B2":
            from math import comb
            Mval = comb(B2 + 2, 3)
        deltas_e = []
        mismatches = 0
        t1 = time.time()
        for i in range(N_NULL_DRAWS):
            key = f"{rung}|{seed}|NULL_B_ZN|{i}"
            if conv == "B1" and key in null_b_zn_bases:
                rbase = null_b_zn_bases[key]
            else:
                seed64 = zn.seed_draw_int(MASTER_SEED, rung, seed, "NULL_B_ZN", conv, i)
                rbase = zn.zn_random_subset(N, Bsz, seed64)
            e_pts = e_arms.scalar_mirror_points(curve, P, rbase)
            direct_e = e_arms.enumerate_e(curve, e_pts, negation_closed=False)
            zn_direct = zn.enumerate_zn(rbase, N, negation_closed=False)
            E3e = de.sum_of_squares(direct_e["unreduced"])
            deltas_e.append(an.delta_of(E3e, Mval, N))
            if i < 5:
                e_arr = target_array_from_counter(direct_e["unreduced"], N, log_table)
                zn_arr = ru.counter_to_zn_array(zn_direct["unreduced"], N, lambda k: int(k))
                if not (e_arr == zn_arr).all():
                    mismatches += 1
        band_e = an.null_band(deltas_e)
        nbzn_results[conv] = {"band_E_mirror": band_e, "sampled_mismatches": mismatches,
                               "n_draws": N_NULL_DRAWS, "wall_seconds": time.time() - t1}
        log(f"  seed{seed} NULL_B_ZN E-mirror {conv}: band mean={band_e['mean']:.5f} sd={band_e['sd']:.5f} "
            f"sampled_mismatches={mismatches} ({time.time()-t1:.2f}s)")
    results["NULL_B_ZN_E_mirror"] = nbzn_results

    return results, accounting


def main(rung):
    t_start = time.time()
    RUN_ID = f"RUN-RELN-f202be-N{rung}"
    run_dir = os.path.join(RUNS_DIR, RUN_ID)
    os.makedirs(run_dir, exist_ok=True)
    stdout_lines = []

    def log(msg):
        print(msg)
        stdout_lines.append(msg)

    log(f"stage2/3 rung={rung} start {ru.now_iso()}")

    curves_json = load_curves()
    if str(rung) not in curves_json:
        log(f"FATAL: rung {rung} not present in stage0 curves.json")
        sys.exit(1)
    res = curves_json[str(rung)]
    if not res["sufficient"]:
        log(f"rung {rung} not_run: insufficient curves in stage0")
        ru.write_json(os.path.join(run_dir, "manifest.json"),
                      {"run": {"id": RUN_ID, "status": "not_run", "reason": "insufficient curves"}})
        sys.exit(0)

    forced_rows = {(r["rung"], r["seed"]): r for r in load_forced_table()["rows"]}
    null_b_zn_bases = load_null_b_zn_bases()

    all_curve_results = {}
    all_accounting = []
    for c in res["accepted"]:
        frow = forced_rows[(rung, c["seed"])]
        rr, acc = process_curve(rung, c, frow, null_b_zn_bases, run_dir, log)
        all_curve_results[c["seed"]] = rr
        all_accounting.extend(acc)

    ru.write_json(os.path.join(run_dir, "curve_results.json"), all_curve_results)
    ru.write_json(os.path.join(run_dir, "accounting.json"), {"rows": all_accounting})

    manifest = {
        "run": {
            "id": RUN_ID, "experiment_id": "EXP-RELN-f202be",
            "stage": "stage2_curve_enumeration_and_stage3_spectral", "rung": rung,
            "status": "completed_valid",
            "code": {"commit": ru.git_commit(), "dirty": ru.git_dirty(),
                     "command": f"python3 source/run_stage2_rung.py {rung}"},
            "environment": ru.environment_info(),
            "timing": {"started_at_epoch": t_start, "finished_at_epoch": time.time(),
                       "wall_seconds": time.time() - t_start},
            "seeds": {"null_draw_master_seed": MASTER_SEED, "null_draws": N_NULL_DRAWS},
            "curves": [c["seed"] for c in res["accepted"]],
        }
    }
    ru.write_json(os.path.join(run_dir, "manifest.json"), manifest)
    with open(os.path.join(run_dir, "command.txt"), "w") as f:
        f.write(f"python3 source/run_stage2_rung.py {rung}\n")
    with open(os.path.join(run_dir, "environment.json"), "w") as f:
        json.dump(ru.environment_info(), f, indent=2)
    with open(os.path.join(run_dir, "stdout.log"), "w") as f:
        f.write("\n".join(stdout_lines))
    with open(os.path.join(run_dir, "stderr.log"), "w") as f:
        f.write("")
    log(f"rung {rung} done, wall={time.time()-t_start:.2f}s")


if __name__ == "__main__":
    rung = int(sys.argv[1])
    main(rung)

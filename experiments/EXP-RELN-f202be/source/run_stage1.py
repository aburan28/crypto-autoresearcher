#!/usr/bin/env python3
"""Stage 1: Z/N integer arms for all four rungs -- Z/N interval, Z/N random
(100 draws, base saved for the stage-2 E mirror check), Bose-Chowla (with
B_3 pre-check), q-decay ladder. Integer arithmetic only. Writes
RUN-RELN-f202be-stage1."""
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import zn_integer_arms as zn
import direct_enumerator as de
import spectral_crosscheck as sc
import analysis as an
import runutil as ru

RUNS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runs"))
STAGE0_DIR = os.path.join(RUNS_DIR, "RUN-RELN-f202be-stage0")
RUN_ID = "RUN-RELN-f202be-stage1"
RUN_DIR = os.path.join(RUNS_DIR, RUN_ID)

MASTER_SEED = 20260906
Q_DECAY_SEED = 20260908
N_NULL_DRAWS = 100
Q_LEVELS = [0, 0.25, 0.5, 0.75, 1.0]
Q_DRAWS = 10


def load_curves():
    with open(os.path.join(STAGE0_DIR, "curves.json")) as f:
        return json.load(f)


def load_forced_table():
    with open(os.path.join(STAGE0_DIR, "forced-value-table.json")) as f:
        return json.load(f)


def cell_dir(*parts):
    return os.path.join(RUN_DIR, "cells", *parts)


def enumerate_and_check(base, N, negation_closed=False):
    direct = zn.enumerate_zn(base, N, negation_closed=negation_closed)
    spectral = sc.spectral_multiset_counts(sorted(set(v % N for v in base)), N)
    # map direct unreduced counter to Z/N array for comparison
    unreduced_arr = ru.counter_to_zn_array(direct["unreduced"], N, lambda k: int(k))
    spectral_arr = spectral["c_multiset"]
    disagreements = int((unreduced_arr != spectral_arr).sum())
    return direct, spectral, disagreements, unreduced_arr


def main():
    t_start = time.time()
    os.makedirs(RUN_DIR, exist_ok=True)
    stdout_lines = []

    def log(msg):
        print(msg)
        stdout_lines.append(msg)

    log(f"stage1 start {ru.now_iso()}")
    curves_json = load_curves()
    forced_rows = {(r["rung"], r["seed"]): r for r in load_forced_table()["rows"]}

    accounting = []
    summary_rows = []
    null_draw_bases = {}  # for stage2 E-mirror reuse: (rung, seed, "NULL_B_ZN", i) -> list

    for rung_str, res in curves_json.items():
        rung = int(rung_str)
        if not res["sufficient"]:
            log(f"rung {rung}: not_run (insufficient curves), skipping stage1")
            continue
        for c in res["accepted"]:
            seed = c["seed"]
            N = c["N"]
            frow = forced_rows[(rung, seed)]
            B1u = frow["B1_unrounded"]
            M1 = frow["M_unrounded_plain"]
            mu1 = frow["mu_unrounded_plain"]

            # --- ZN interval + forced negation gap uses B1_even elsewhere;
            # the interval control itself is PLAIN, unrounded B1.
            base = zn.zn_interval_base(B1u)
            direct, spectral, disagree, arr = enumerate_and_check(base, N, negation_closed=False)
            E3 = de.sum_of_squares(direct["unreduced"])
            inv1 = de.sum_of_counts(direct["unreduced"])
            delta = an.delta_of(E3, M1, N)
            threshold = 0.05 * (B1u ** 2)
            cdir = cell_dir(f"rung{rung}_seed{seed}", "ZN_interval")
            os.makedirs(cdir, exist_ok=True)
            ru.write_array(os.path.join(cdir, "count-vector.npy"), arr)
            hist = {}
            for v in arr:
                hist[str(int(v))] = hist.get(str(int(v)), 0) + 1
            ru.write_json(os.path.join(cdir, "histogram.json"), hist)
            ru.write_json(os.path.join(cdir, "spectral.json"), {
                "E3_spectral": spectral["E3"], "E3_ord": spectral["E3_ord"],
                "parseval_relative_residual": spectral["parseval_relative_residual"],
                "disagreements_vs_direct": disagree,
            })
            with open(os.path.join(cdir, "count-vector.sha256"), "w") as f:
                f.write(ru.sha256_bytes(arr.tobytes()))
            verdict = {
                "cell": "ZN_interval", "rung": rung, "seed": seed, "N": N, "B": B1u, "M": M1,
                "E3": E3, "delta": delta, "threshold_0.05B2": threshold,
                "pass_threshold": delta >= threshold, "INV1_ok": inv1 == M1,
                "spectral_disagreements": disagree, "INV2_ok": disagree == 0,
            }
            accounting.append(verdict)
            log(f"rung{rung} seed{seed} ZN_interval: Delta={delta:.3f} thr={threshold:.3f} "
                f"pass={verdict['pass_threshold']} INV1_ok={verdict['INV1_ok']} INV2_ok={verdict['INV2_ok']}")

            # --- ZN random (100 draws), base saved for stage2 E mirror
            deltas = []
            for i in range(N_NULL_DRAWS):
                seed64 = zn.seed_draw_int(MASTER_SEED, rung, seed, "NULL_B_ZN", "B1", i)
                rbase = zn.zn_random_subset(N, B1u, seed64)
                null_draw_bases[(rung, seed, "NULL_B_ZN", i)] = rbase
                direct_r = zn.enumerate_zn(rbase, N, negation_closed=False)
                E3r = de.sum_of_squares(direct_r["unreduced"])
                deltas.append(an.delta_of(E3r, M1, N))
            band = an.null_band(deltas)
            summary_rows.append({"rung": rung, "seed": seed, "arm": "NULL_B_ZN", "B_conv": "B1",
                                  "band": band, "design_mean": frow["random_base_mean_1_minus_1_over_N"],
                                  "design_sd": frow["design_sd_delta_random"]})
            log(f"rung{rung} seed{seed} NULL_B_ZN band: mean={band['mean']:.5f} sd={band['sd']:.5f} "
                f"design_mean={frow['random_base_mean_1_minus_1_over_N']:.5f} design_sd={frow['design_sd_delta_random']:.5f}")

            # --- Bose-Chowla (q prime only; else deviation recorded)
            q = frow.get("B2")
            bc_result = None
            if q is not None:
                try:
                    inds, order = zn.bose_chowla_set(q)
                    b3check = zn.verify_B3_property(inds, order)
                    # lift to integers in [0, q^3-2): inds already in that range mod order
                    lifted = [i % N for i in inds]  # order = q^3-1 <= N by construction (3(q^3-1)<N)
                    direct_bc = zn.enumerate_zn(lifted, N, negation_closed=False)
                    E3_bc = de.sum_of_squares(direct_bc["unreduced"])
                    M2 = frow["M2"]
                    delta_bc = an.delta_of(E3_bc, M2, N)
                    bc_result = {
                        "q": q, "order": order, "b3_property_verified": b3check["is_B3"],
                        "duplicate_sum_events": b3check["duplicate_sum_events"],
                        "E3_measured": E3_bc, "M2_expected": M2, "E3_equals_M2": E3_bc == M2,
                        "delta_measured": delta_bc, "delta_expected": frow["bose_chowla_forced_delta"],
                    }
                    log(f"rung{rung} seed{seed} Bose-Chowla q={q}: E3={E3_bc} M2={M2} "
                        f"E3==M2:{E3_bc==M2} B3_ok={b3check['is_B3']}")
                except NotImplementedError as e:
                    bc_result = {"q": q, "skipped": True, "reason": str(e)}
                    log(f"rung{rung} seed{seed} Bose-Chowla SKIPPED (deviation): {e}")
            accounting.append({"cell": "bose_chowla", "rung": rung, "seed": seed, **({} if bc_result is None else bc_result)})

            # --- q-decay ladder
            qdecay_deltas = {}
            for qf in Q_LEVELS:
                if qf == 0:
                    dvals = []
                    dbase = zn.zn_interval_base(B1u)
                    direct_q = zn.enumerate_zn(dbase, N, negation_closed=False)
                    E3q = de.sum_of_squares(direct_q["unreduced"])
                    dvals.append(an.delta_of(E3q, M1, N))
                    qdecay_deltas["0"] = dvals
                    continue
                dvals = []
                for i in range(Q_DRAWS):
                    seed64 = zn.seed_draw_int(Q_DECAY_SEED, rung, seed, "q_decay", f"q{qf}", i)
                    qbase = zn.q_decay_base(N, B1u, qf, seed64)
                    direct_q = zn.enumerate_zn(qbase, N, negation_closed=False)
                    E3q = de.sum_of_squares(direct_q["unreduced"])
                    dvals.append(an.delta_of(E3q, M1, N))
                qdecay_deltas[str(qf)] = dvals
            means = {k: (sum(v) / len(v)) for k, v in qdecay_deltas.items()}
            qs_sorted = sorted(means.keys(), key=float)
            monotone = all(means[qs_sorted[i]] >= means[qs_sorted[i + 1]] - 1e-9 for i in range(len(qs_sorted) - 1))
            accounting.append({"cell": "q_decay_ladder", "rung": rung, "seed": seed,
                                "means_by_q": means, "monotone_decreasing": monotone,
                                "null_band_mean_at_q1": band["mean"]})
            log(f"rung{rung} seed{seed} q_decay means: {means} monotone={monotone}")

    ru.write_json(os.path.join(RUN_DIR, "accounting.json"), {"rows": accounting})
    ru.write_json(os.path.join(RUN_DIR, "metrics.json"), {"null_bands": summary_rows})

    # Save the exact random Z/N bases used, so stage2 can mirror them onto E
    # with the SAME base sets (not merely the same seed function -- this
    # file IS the reproducibility artifact for the bit-identical mirror
    # check).
    serializable = {f"{k[0]}|{k[1]}|{k[2]}|{k[3]}": v for k, v in null_draw_bases.items()}
    ru.write_json(os.path.join(RUN_DIR, "null_b_zn_bases.json"), serializable)

    manifest = {
        "run": {
            "id": RUN_ID, "experiment_id": "EXP-RELN-f202be",
            "stage": "stage1_ZN_integer_arms",
            "status": "completed_valid",
            "code": {"commit": ru.git_commit(), "dirty": ru.git_dirty(),
                     "command": "python3 source/run_stage1.py"},
            "environment": ru.environment_info(),
            "timing": {"started_at_epoch": t_start, "finished_at_epoch": time.time(),
                       "wall_seconds": time.time() - t_start},
            "seeds": {"null_draw_master_seed": MASTER_SEED, "q_decay_master_seed": Q_DECAY_SEED,
                      "null_draws": N_NULL_DRAWS, "q_decay_draws_per_q": Q_DRAWS},
        }
    }
    ru.write_json(os.path.join(RUN_DIR, "manifest.json"), manifest)
    with open(os.path.join(RUN_DIR, "command.txt"), "w") as f:
        f.write("python3 source/run_stage1.py\n")
    with open(os.path.join(RUN_DIR, "environment.json"), "w") as f:
        json.dump(ru.environment_info(), f, indent=2)
    with open(os.path.join(RUN_DIR, "stdout.log"), "w") as f:
        f.write("\n".join(stdout_lines))
    with open(os.path.join(RUN_DIR, "stderr.log"), "w") as f:
        f.write("")
    log(f"stage1 done, wall={time.time()-t_start:.2f}s")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Stage 1: toy n in {17,19} V/V_C / parity / Z/(4l) replica census."""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from coset import (
    build_curve,
    build_windows,
    classify_window_points,
    coset_fractions_x,
    count_decomps_m2,
    count_decomps_m3,
    replica_census,
    sample_class2_mirrors,
    sample_subgroup_targets,
    verify_order,
)
from runpack import EXP_ROOT, dump_yaml, utc_now, write_run_package


def ratio_stats(num_means, den_means, modeled):
    ratios = []
    for a, b in zip(num_means, den_means):
        if b == 0:
            ratios.append(None)
        else:
            ratios.append(a / b)
    valid = [r for r in ratios if r is not None]
    mean_r = sum(valid) / len(valid) if valid else None
    extreme = None
    if valid:
        # most extreme vs modeled
        extreme = max(valid, key=lambda r: abs(r / modeled - 1.0) if modeled else abs(r))
    band = None
    if mean_r is not None and modeled:
        band = (0.5 * modeled) <= mean_r <= (2.0 * modeled)
    return {
        "per_target_ratios": ratios,
        "mean_ratio_measured": mean_r,
        "modeled_comparator": modeled,
        "within_half_to_double_of_modeled": band,
        "most_extreme_ratio_measured": extreme,
    }


def run_curve_cell(cell_name: str, seed: int, n_C: int = 40, n_mirror: int = 20,
                   m_list=(2, 3), instrument_ceiling: int = 5_000_000):
    F, E, cell = build_curve(cell_name)
    order_info = verify_order(E, cell)
    if not order_info["pass"]:
        raise RuntimeError(f"order verification failed: {order_info}")
    h = cell["expected_h"]
    l = cell["expected_l"]
    windows = build_windows(E, cell, seed, deg_dim=10)
    rng = random.Random(seed)
    targets = sample_subgroup_targets(E, h, n_C, rng)
    mirrors = sample_class2_mirrors(E, l, n_mirror, rng) if h == 4 else []
    fracs = coset_fractions_x(windows["V"], h)

    yields = {}
    mirror_vc = {}
    class_sum_violations = 0
    termination = "completed"
    for m in m_list:
        yields[m] = {}
        for name in ("V", "V_C", "V0", "random"):
            recs = windows[name]
            if m == 2:
                res = count_decomps_m2(E, recs, targets, l, h)
            else:
                res = count_decomps_m3(E, recs, targets, l, h, instrument_ceiling=instrument_ceiling)
                if res.get("termination_reason") == "instrument_ceiling":
                    termination = "instrument_ceiling"
            class_sum_violations += res["class_sum_violations"]
            yields[m][name] = res
        if h == 4 and mirrors:
            if m == 2:
                mirror_vc[m] = count_decomps_m2(E, windows["V_C"], mirrors, l, h)
            else:
                mirror_vc[m] = count_decomps_m3(
                    E, windows["V_C"], mirrors, l, h, instrument_ceiling=instrument_ceiling
                )
            class_sum_violations += mirror_vc[m]["class_sum_violations"]

    # V/V_C and parity ratios
    ratio_tables = {}
    for m in m_list:
        modeled_base = 4 ** (m - 1)
        v_means = yields[m]["V"]["per_target_counts"]
        vc_means = yields[m]["V_C"]["per_target_counts"]
        # align lengths if instrument_ceiling truncated
        n = min(len(v_means), len(vc_means))
        ratio_tables[m] = {
            "V_over_V_C": ratio_stats(
                [yields[m]["V"]["mean"]] * max(n, 1),
                [yields[m]["V_C"]["mean"]] * max(n, 1),
                modeled_base,
            ),
            # also per-target where both complete
            "V_over_V_C_per_target": ratio_stats(v_means[:n], vc_means[:n], modeled_base),
            "parity_V0_over_random": ratio_stats(
                [yields[m]["V0"]["mean"]],
                [yields[m]["random"]["mean"]],
                2.0,
            ),
            "modeled_base_size_4_to_m_minus_1": modeled_base,
            "modeled_parity": 2.0,
        }

    return {
        "cell": cell,
        "order_info": order_info,
        "window_meta": windows["meta"],
        "coset_fractions": fracs,
        "n_targets_C": len(targets),
        "n_mirrors": len(mirrors),
        "yields": {
            m: {k: {kk: vv for kk, vv in res.items() if kk != "per_target_counts"}
                | {"per_target_counts": res["per_target_counts"]}
                for k, res in yields[m].items()}
            for m in m_list
        },
        "mirror_VC": {
            m: {kk: vv for kk, vv in mirror_vc[m].items()} for m in mirror_vc
        },
        "ratios": ratio_tables,
        "class_sum_violations": class_sum_violations,
        "termination_reason": termination,
        "h1_null_absent": True,
    }


def summarize_for_stage_artifacts(curve_results: list, replica_results: dict):
    """Aggregate Stage 1 YAML artifacts from per-run curve cells + replica."""
    coset = {
        "experiment_id": "EXP-BINSTD-58758f",
        "label": "measured",
        "cells": [],
        "modeled_comparator": {"class0": 0.25, "class2": 0.25, "class_1_or_3": 0.5},
    }
    yield_curve = {
        "experiment_id": "EXP-BINSTD-58758f",
        "label": "measured",
        "modeled_V_over_V_C": {2: 4, 3: 16},
        "modeled_parity": 2,
        "matched_rho_baseline": {"label": "modeled", "note": "matched rho ~2^60.9 comparator only; not mixed into yield columns"},
        "cells": [],
    }
    class_sum = {
        "experiment_id": "EXP-BINSTD-58758f",
        "violations": 0,
        "cells": [],
        "hard_halt_if_nonzero": True,
    }
    for r in curve_results:
        coset["cells"].append(
            {
                "curve_id": r["cell"]["curve_id"],
                "seed": r["seed"],
                "fractions": r["coset_fractions"],
                "window_meta": r["window_meta"],
            }
        )
        yield_curve["cells"].append(
            {
                "curve_id": r["cell"]["curve_id"],
                "seed": r["seed"],
                "ratios": r["ratios"],
                "yield_means": {
                    m: {w: r["yields"][m][w]["mean"] for w in r["yields"][m]}
                    for m in r["yields"]
                },
                "mirror_VC_totals": {
                    m: r["mirror_VC"][m]["total"] for m in r.get("mirror_VC", {})
                },
                "termination_reason": r["termination_reason"],
            }
        )
        class_sum["violations"] += r["class_sum_violations"]
        class_sum["cells"].append(
            {
                "curve_id": r["cell"]["curve_id"],
                "seed": r["seed"],
                "violations": r["class_sum_violations"],
                "mirror_VC_zero_check": {
                    m: r["mirror_VC"][m]["total"] == 0 for m in r.get("mirror_VC", {})
                },
            }
        )

    yield_replica = {
        "experiment_id": "EXP-BINSTD-58758f",
        "label": "measured_on_Z_4l_replica",
        "modeled_V_over_V_C": {2: 4, 3: 16},
        "modeled_parity": 2,
        "replica": replica_results,
    }

    # HEUR verdict — primary statistic is mean_V / mean_V_C (equiv. total ratio).
    # Per-target ratios omit zeros in the denominator and are reported as a tail check only.
    heur_rows = []
    for r in curve_results:
        for m, tab in r["ratios"].items():
            primary = tab["V_over_V_C"]
            tail = tab["V_over_V_C_per_target"]
            heur_rows.append(
                {
                    "curve_id": r["cell"]["curve_id"],
                    "seed": r["seed"],
                    "m": int(m) if not isinstance(m, int) else m,
                    "mean_ratio_measured": primary["mean_ratio_measured"],
                    "modeled": primary["modeled_comparator"],
                    "within_band": primary["within_half_to_double_of_modeled"],
                    "most_extreme_per_target_ratio_measured": tail["most_extreme_ratio_measured"],
                    "parity_ratio_measured": tab["parity_V0_over_random"]["mean_ratio_measured"],
                    "parity_modeled": 2.0,
                    "parity_within_band": tab["parity_V0_over_random"][
                        "within_half_to_double_of_modeled"
                    ],
                }
            )
    # replica band
    rep_band = {}
    for m in (2, 3):
        y = replica_results["yields"][m] if m in replica_results["yields"] else replica_results["yields"][str(m)]
        mv = y["V"]["mean"]
        mvc = y["V_C"]["mean"]
        ratio = (mv / mvc) if mvc else None
        modeled = 4 ** (m - 1)
        rep_band[m] = {
            "mean_ratio_measured": ratio,
            "modeled": modeled,
            "within_band": (0.5 * modeled <= ratio <= 2.0 * modeled) if ratio else False,
        }

    curve_ok = all(row["within_band"] for row in heur_rows if row["mean_ratio_measured"] is not None)
    replica_ok = all(rep_band[m]["within_band"] for m in rep_band)
    # DO mapping (observation only — not a status edit)
    if class_sum["violations"] > 0:
        decision_obs = "HARD_HALT_class_sum"
    elif curve_ok and replica_ok:
        decision_obs = "DO-1-consistent_base_size_holds_at_tested_scope"
    elif (not curve_ok) and replica_ok:
        decision_obs = "DO-3-curve_deviates_replica_ok"
    elif (not curve_ok) and (not replica_ok):
        decision_obs = "DO-artifact_or_window_size_arithmetic_both_deviate"
    else:
        decision_obs = "DO-other_or_underpowered"

    heur = {
        "experiment_id": "EXP-BINSTD-58758f",
        "heuristic_id": "HEUR-BINSTD-a45444-H1",
        "statement": "mean V/V_C = 4^{m-1} within [0.5,2]x on curve and Z/(4l) replica at m in {2,3}",
        "curve_rows": heur_rows,
        "replica_rows": rep_band,
        "curve_all_within_band": curve_ok,
        "replica_all_within_band": replica_ok,
        "class_sum_violations": class_sum["violations"],
        "decision_observation_only": decision_obs,
        "no_deployed_break_claim": True,
        "no_free_cofactor_framing": True,
        "note": (
            "Executor records comparison vs frozen prediction only; "
            "does not declare heuristic supported/refuted as a ledger status."
        ),
    }
    return coset, yield_curve, yield_replica, class_sum, heur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--arm", required=True, choices=["n19", "n17", "replica", "finalize"])
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--cell", default=None)
    ap.add_argument("--finalize", action="store_true")
    args = ap.parse_args()

    stage0 = EXP_ROOT / "stage0"
    if not stage0.exists():
        raise SystemExit("Stage 1 refused: stage0/ does not exist")

    started = utc_now()
    t0 = time.time()
    logs = []

    if args.arm in ("n19", "n17"):
        cell = args.cell or ("n19_koblitz_h4" if args.arm == "n19" else "n17_rc1_h4")
        seed = args.seed
        if seed is None:
            raise SystemExit("--seed required for curve arms")
        result = run_curve_cell(cell, seed)
        result["seed"] = seed
        # stash intermediate JSON for finalize (under implementation/, still in write_scope)
        stash = EXP_ROOT / "implementation" / f"_stash_{args.run_id}.json"
        stash.write_text(json.dumps(result, default=str), encoding="utf-8")
        logs.append(f"cell={cell} seed={seed} violations={result['class_sum_violations']}")
        logs.append(f"fractions={result['coset_fractions']}")
        for m, tab in result["ratios"].items():
            logs.append(
                f"m={m} V/V_C mean={tab['V_over_V_C']['mean_ratio_measured']} "
                f"modeled={tab['modeled_base_size_4_to_m_minus_1']} "
                f"band={tab['V_over_V_C']['within_half_to_double_of_modeled']} "
                f"extreme_per_target={tab['V_over_V_C_per_target']['most_extreme_ratio_measured']}"
            )
            logs.append(
                f"m={m} parity={tab['parity_V0_over_random']['mean_ratio_measured']} modeled=2"
            )
        if result["class_sum_violations"] > 0:
            raise SystemExit("HARD HALT: class-sum violations > 0")
        metrics = {
            "class_sum_violations": result["class_sum_violations"],
            "n_targets": result["n_targets_C"],
            "termination_reason": result["termination_reason"],
            "ratios": {
                m: {
                    "V_over_V_C_mean": tab["V_over_V_C"]["mean_ratio_measured"],
                    "V_over_V_C_extreme_per_target": tab["V_over_V_C_per_target"][
                        "most_extreme_ratio_measured"
                    ],
                    "parity_mean": tab["parity_V0_over_random"]["mean_ratio_measured"],
                    "modeled_base": tab["modeled_base_size_4_to_m_minus_1"],
                }
                for m, tab in result["ratios"].items()
            },
        }
        arm = f"{args.arm}-seed{seed}"
        params = {"curve_id": result["cell"]["curve_id"], "seed": seed, "cell": cell}
        term = result["termination_reason"]
    elif args.arm == "replica":
        # Use n19 sizes from a reference build
        seed = args.seed or 20261001
        F, E, cell = build_curve("n19_koblitz_h4")
        verify_order(E, cell)
        windows = build_windows(E, cell, seed, deg_dim=10)
        meta = windows["meta"]
        N = cell["expected_E"]
        rep = replica_census(
            N=N,
            window_size=meta["n_V_pts"],
            vc_size=meta["n_VC_pts"],
            v0_size=meta["n_V0_pts"],
            rand_size=meta["n_random_pts"],
            targets_C=40,
            mirrors=20,
            m_list=[2, 3],
            seed=seed,
        )
        stash = EXP_ROOT / "implementation" / f"_stash_{args.run_id}.json"
        stash.write_text(json.dumps({"kind": "replica", "seed": seed, "replica": rep}, default=str), encoding="utf-8")
        logs.append(f"replica seed={seed} windows={rep['windows']}")
        for m in (2, 3):
            mv = rep["yields"][m]["V"]["mean"]
            mvc = rep["yields"][m]["V_C"]["mean"]
            logs.append(f"replica m={m} V/V_C={None if not mvc else mv/mvc} modeled={4**(m-1)}")
        metrics = {"replica_windows": rep["windows"], "seed": seed}
        arm = "z4l-replica"
        params = {"curve_id": "Z/(4l)-replica", "seed": seed, "N": N}
        term = "completed"
        result = {"class_sum_violations": sum(
            rep["yields"][m][w]["class_sum_violations"]
            for m in rep["yields"] for w in rep["yields"][m]
        )}
        if result["class_sum_violations"] > 0:
            raise SystemExit("HARD HALT: replica class-sum violations > 0")
    else:
        raise SystemExit(f"unknown arm {args.arm}")

    finished = utc_now()
    wall = time.time() - t0
    write_run_package(
        args.run_id,
        stage=1,
        arm=arm,
        seed=params.get("seed"),
        command=(
            f"python3 experiments/EXP-BINSTD-58758f/implementation/stage1_run.py "
            f"--run-id {args.run_id} --arm {args.arm} --seed {params.get('seed')}"
        ),
        parameters=params,
        metrics=metrics,
        valid=True,
        invalid_reason=None,
        termination_reason=term,
        stdout_text="\n".join(logs) + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate_note=(
            "Stage 1 toy yield/coset measurement; counted relations re-verified by curve "
            "group law in the census; certificate.kind=none (measurement run)"
        ),
    )
    print("\n".join(logs))


def finalize_stage1(curve_run_ids: list[str], replica_run_id: str):
    curve_results = []
    for rid in curve_run_ids:
        stash = EXP_ROOT / "implementation" / f"_stash_{rid}.json"
        curve_results.append(json.loads(stash.read_text(encoding="utf-8")))
    rep_stash = json.loads((EXP_ROOT / "implementation" / f"_stash_{replica_run_id}.json").read_text())
    coset, ycurve, yrep, csum, heur = summarize_for_stage_artifacts(curve_results, rep_stash["replica"])
    if csum["violations"] > 0:
        raise SystemExit("HARD HALT: class-sum violations > 0 at finalize")
    stage1 = EXP_ROOT / "stage1"
    dump_yaml(stage1 / "coset-fractions.yaml", coset)
    dump_yaml(stage1 / "yield-ratios-curve.yaml", ycurve)
    dump_yaml(stage1 / "yield-ratios-replica.yaml", yrep)
    dump_yaml(stage1 / "class-sum-report.yaml", csum)
    dump_yaml(stage1 / "heur-h1-verdict.yaml", heur)
    print("wrote stage1 artifacts")


if __name__ == "__main__":
    # Allow: python stage1_run.py finalize --curves id1,id2,id3 --replica id4
    if len(sys.argv) > 1 and sys.argv[1] == "finalize":
        ap = argparse.ArgumentParser()
        ap.add_argument("finalize")
        ap.add_argument("--curves", required=True)
        ap.add_argument("--replica", required=True)
        args = ap.parse_args()
        finalize_stage1(args.curves.split(","), args.replica)
    else:
        main()

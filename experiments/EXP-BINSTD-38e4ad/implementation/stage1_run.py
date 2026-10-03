#!/usr/bin/env python3
"""Stage 1: n=17 m=2 l=8 exhaustive Frobenius orbit soundness census."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runpack import EXP_ROOT, dump_yaml, peak_rss_bytes, utc_now, write_run_package
from soundness import (
    L_ORDER_EXPECTED,
    N,
    build_factor_base,
    build_koblitz_curve,
    census_metrics,
    find_generator,
    random_targets,
    select_V_f1,
    verify_group_order,
)

# seed -> run id (minted via allocate_id --next/--check)
SEED_RUNS = {
    2026100117: "RUN-BINSTD-b50f23",
    2026100118: "RUN-BINSTD-099730",
    2026100119: "RUN-BINSTD-1d2240",
    2026100120: "RUN-BINSTD-06a5e0",
}
N_TARGETS = 200
M = 2
L = 8


def ensure_stage0() -> None:
    if not (EXP_ROOT / "stage0").is_dir():
        raise SystemExit("REFUSE: stage0/ missing; Stage 1 gated on Stage 0")


def run_one(seed: int) -> dict:
    ensure_stage0()
    if N in (29, 37, 163):
        raise SystemExit("REFUSE: forbidden measurement n")
    run_id = SEED_RUNS[seed]
    started = utc_now()
    t0 = time.time()
    stdout_lines = []

    F, E = build_koblitz_curve()
    g, V, vmeta = select_V_f1(F)
    stab = vmeta["tau_stability"]
    stdout_lines.append(f"V card={len(V)} dim={stab['dim_V']} tau_pass={stab['pass']}")
    stdout_lines.append(f"factorisation_ok={vmeta['factorisation_matches_frozen']}")

    # Write tau-stability once (first seed only); later seeds reuse
    stage1 = EXP_ROOT / "stage1"
    stage1.mkdir(parents=True, exist_ok=True)
    tau_path = stage1 / "tau-stability-check.yaml"
    if not tau_path.exists():
        dump_yaml(
            tau_path,
            {
                "experiment_id": "EXP-BINSTD-38e4ad",
                "stage": 1,
                "n": N,
                "m": M,
                "l": L,
                "chosen_g": vmeta["chosen_g"],
                "phi17": vmeta,
                "pass": stab["pass"],
                "dim_V": stab["dim_V"],
                "card_V": stab["card_V"],
                "leave_count": stab["leave_count"],
                "label": "MEASURED",
            },
        )

    if not stab["pass"] or stab["dim_V"] != L:
        finished = utc_now()
        wall = time.time() - t0
        metrics = {
            "tau_stability_pass": stab["pass"],
            "dim_V": stab["dim_V"],
            "termination_reason": "instrument_halt",
            "peak_rss_bytes": peak_rss_bytes(),
            "wall_s": wall,
        }
        write_run_package(
            run_id,
            stage=1,
            arm="soundness_census",
            seed=seed,
            command=f"python3 experiments/EXP-BINSTD-38e4ad/implementation/stage1_run.py --seed {seed}",
            parameters={"curve_id": "RC1-n17-a1b1", "n": N, "m": M, "l": L, "n_targets": N_TARGETS},
            metrics=metrics,
            valid=False,
            invalid_reason="tau-stability failure or dim!=8",
            termination_reason="instrument_halt",
            stdout_text="\n".join(stdout_lines) + "\n",
            started_at=started,
            finished_at=finished,
            wall_seconds=wall,
            certificate_note="Measurement only; certificate.kind=none",
        )
        return metrics

    gord = verify_group_order(E)
    stdout_lines.append(f"group_order={gord}")
    if not (gord["matches_frozen"] and gord["l_order_prime"]):
        finished = utc_now()
        wall = time.time() - t0
        metrics = {
            "group_order": gord,
            "termination_reason": "instrument_halt",
            "peak_rss_bytes": peak_rss_bytes(),
            "wall_s": wall,
        }
        write_run_package(
            run_id,
            stage=1,
            arm="soundness_census",
            seed=seed,
            command=f"python3 experiments/EXP-BINSTD-38e4ad/implementation/stage1_run.py --seed {seed}",
            parameters={"curve_id": "RC1-n17-a1b1", "n": N, "m": M, "l": L},
            metrics=metrics,
            valid=False,
            invalid_reason="group order / primality check failed",
            termination_reason="instrument_halt",
            stdout_text="\n".join(stdout_lines) + "\n",
            started_at=started,
            finished_at=finished,
            wall_seconds=wall,
            certificate_note="Measurement only; certificate.kind=none",
        )
        return metrics

    G = find_generator(E, gord["l_order"], seed)
    targets = random_targets(E, G, gord["l_order"], N_TARGETS, seed)
    fb = build_factor_base(E, V)
    stdout_lines.append(f"fb n_x={fb['n_x']} n_points={fb['n_points']}")

    census = census_metrics(E, targets, fb)
    stdout_lines.append(json.dumps({k: census[k] for k in census if k != "a2_alarms"}, sort_keys=True))

    finished = utc_now()
    wall = time.time() - t0
    termination = "A2_alarm" if census["A2_alarm"] else "completed"
    # equivariance < 1 on V is instrument fail
    eq = census["equivariance_agreement"]
    instrument_fail = eq is not None and eq < 1.0 - 1e-15
    if instrument_fail:
        termination = "instrument_halt"

    metrics = {
        "n": N,
        "m": M,
        "l": L,
        "seed": seed,
        "group_order_E": gord["group_order_E"],
        "l_order": gord["l_order"],
        "l_order_prime": gord["l_order_prime"],
        "cofactor_h": gord["cofactor_h"],
        "fb_n_x": fb["n_x"],
        "fb_n_points": fb["n_points"],
        "closure_fraction": census["closure_fraction"],
        "conjugate_overlap": census["conjugate_overlap"],
        "equivariance_agreement": census["equivariance_agreement"],
        "n_targets_eligible": census["n_targets_eligible"],
        "n_targets_sigma_pm_R": census["n_targets_sigma_pm_R"],
        "n_targets_empty_S": census["n_targets_empty_S"],
        "A2_alarm": census["A2_alarm"],
        "a2_alarms": census["a2_alarms"],
        "peak_rss_bytes": peak_rss_bytes(),
        "wall_s": wall,
        "termination_reason": termination,
        "prior_KN_FIND_47da4e_ratio_band": {
            "label": "MODELED/PRIOR",
            "band": [1.00, 1.47],
            "note": "Stage 1 does not re-run WDSat; band is background only",
        },
        "no_deployed_curve_break_claimed": True,
        "no_fixed_target_satisfiability_claim": True,
        "label": "MEASURED",
    }

    write_run_package(
        run_id,
        stage=1,
        arm="soundness_census",
        seed=seed,
        command=f"python3 experiments/EXP-BINSTD-38e4ad/implementation/stage1_run.py --seed {seed}",
        parameters={
            "curve_id": "RC1-n17-a1b1",
            "n": N,
            "m": M,
            "l": L,
            "n_targets": N_TARGETS,
            "field_poly": "t^17+t^3+1",
            "curve": "y^2+xy=x^3+x^2+1",
            "V": "ker f1(tau)",
        },
        metrics=metrics,
        valid=not instrument_fail,
        invalid_reason="equivariance_agreement < 1 on tau-stable V" if instrument_fail else None,
        termination_reason=termination,
        stdout_text="\n".join(stdout_lines) + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate_note="Exhaustive soundness census; certificate.kind=none",
    )
    # stash per-seed census for aggregate writer
    stash = stage1 / f"_census_seed_{seed}.json"
    if stash.exists():
        raise FileExistsError(stash)
    stash.write_text(json.dumps({"seed": seed, "run_id": run_id, "census": census, "metrics": metrics}, indent=2) + "\n")
    return metrics


def write_aggregate() -> None:
    stage1 = EXP_ROOT / "stage1"
    stashes = sorted(stage1.glob("_census_seed_*.json"))
    if len(stashes) != 4:
        print(f"aggregate deferred: have {len(stashes)}/4 seed stashes")
        return
    per = [json.loads(p.read_text()) for p in stashes]
    # Aggregate: report per-seed and pooled eligible metrics
    closures = [p["census"]["closure_fraction"] for p in per]
    overlaps = [p["census"]["conjugate_overlap"] for p in per]
    eqs = [p["census"]["equivariance_agreement"] for p in per]
    any_a2 = any(p["census"]["A2_alarm"] for p in per)
    # pooled: sum closed / sum eligible
    sum_closed = sum(p["census"]["n_targets_closed_nonempty"] for p in per)
    sum_elig = sum(p["census"]["n_targets_eligible"] for p in per)
    sum_overlap = sum(p["census"]["conjugate_overlap"] for p in per)
    sum_sq = sum(p["census"]["n_squared_tuples"] for p in per)
    sum_sq_sig = sum(p["census"]["n_squared_in_S_sigma"] for p in per)
    pooled_closure = sum_closed / sum_elig if sum_elig else None
    pooled_eq = sum_sq_sig / sum_sq if sum_sq else None

    heur_h1_holds = (
        pooled_closure == 0
        and sum_overlap == 0
        and pooled_eq == 1.0
        and not any_a2
    )
    if any_a2:
        outcome = "DO-2-A2-failure"
    elif pooled_eq is not None and pooled_eq < 1.0:
        outcome = "DO-3-instrument-fail"
    elif heur_h1_holds:
        outcome = "DO-1-null-confirms-HOLD-S"
    else:
        outcome = "DO-3-instrument-fail"

    census_doc = {
        "experiment_id": "EXP-BINSTD-38e4ad",
        "stage": 1,
        "n": N,
        "m": M,
        "l": L,
        "n_targets_per_seed": N_TARGETS,
        "seeds": [p["seed"] for p in per],
        "run_ids": [p["run_id"] for p in per],
        "per_seed": [
            {
                "seed": p["seed"],
                "run_id": p["run_id"],
                "closure_fraction": p["census"]["closure_fraction"],
                "conjugate_overlap": p["census"]["conjugate_overlap"],
                "equivariance_agreement": p["census"]["equivariance_agreement"],
                "n_targets_eligible": p["census"]["n_targets_eligible"],
                "n_targets_sigma_pm_R": p["census"]["n_targets_sigma_pm_R"],
                "A2_alarm": p["census"]["A2_alarm"],
                "label": "MEASURED",
            }
            for p in per
        ],
        "pooled": {
            "closure_fraction": pooled_closure,
            "conjugate_overlap": sum_overlap,
            "equivariance_agreement": pooled_eq,
            "n_targets_eligible": sum_elig,
            "n_targets_closed_nonempty": sum_closed,
            "label": "MEASURED",
        },
        "frozen_prediction_reference": {
            "closure_fraction": 0,
            "conjugate_overlap": 0,
            "equivariance_agreement": 1,
            "source": "HEUR-BINSTD-c3d68f-H1 / preregistered_prediction",
        },
        "tail_checks": {
            "any_A2_alarm": any_a2,
            "sigma_pm_R_counts_per_seed": [p["census"]["n_targets_sigma_pm_R"] for p in per],
        },
        "no_deployed_curve_break_claimed": True,
        "no_fixed_target_satisfiability_claim": True,
    }
    dump_yaml(stage1 / "soundness-census.yaml", census_doc)

    verdict = {
        "experiment_id": "EXP-BINSTD-38e4ad",
        "heuristic_id": "HEUR-BINSTD-c3d68f-H1",
        "stage": 1,
        "HEUR_H1_holds": heur_h1_holds,
        "distinguishable_outcome_id": outcome,
        "comparison_to_frozen_prediction": {
            "closure_fraction_pooled": pooled_closure,
            "conjugate_overlap_pooled": sum_overlap,
            "equivariance_agreement_pooled": pooled_eq,
            "predicted": {"closure_fraction": 0, "conjugate_overlap": 0, "equivariance_agreement": 1},
        },
        "interpretation_boundary": (
            "Observations only. Executor does not declare hypothesis supported/"
            "refuted. No fixed-target orbit clauses claimed satisfiability-preserving. "
            "No deployed-curve break claimed. Scoped to n=17 m=2 l=8."
        ),
        "run_ids": [p["run_id"] for p in per],
        "label": "MEASURED",
    }
    dump_yaml(stage1 / "heur-h1-verdict.yaml", verdict)
    print(json.dumps({"aggregate": True, "outcome": outcome, "HEUR_H1_holds": heur_h1_holds}, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, choices=sorted(SEED_RUNS), required=False)
    ap.add_argument("--aggregate-only", action="store_true")
    args = ap.parse_args()
    if args.aggregate_only:
        write_aggregate()
        return
    if args.seed is None:
        for s in sorted(SEED_RUNS):
            print(f"=== seed {s} ===")
            run_one(s)
        write_aggregate()
    else:
        run_one(args.seed)
        write_aggregate()


if __name__ == "__main__":
    main()

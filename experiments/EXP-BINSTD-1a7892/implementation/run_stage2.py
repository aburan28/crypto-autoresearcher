#!/usr/bin/env python3
"""Stage 2 toy T_k per-trial cost vs g for EXP-BINSTD-1a7892."""
from __future__ import annotations

import json
import math
import statistics
import sys
import time
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if sys.path[:1] != [str(_IMPL)]:
    sys.path.insert(0, str(_IMPL))

from common import (
    EXP_DIR,
    SEEDS,
    dump_yaml,
    git_state,
    utc_now,
    write_run_package,
)
from stage2_tk import measure_non_tk, measure_null_no_subfield, measure_tk_trial

TOYS = [
    {"d": 4, "k_prime": 3, "g": 2, "dk": 12},
    {"d": 4, "k_prime": 5, "g": 4, "dk": 20},
    {"d": 4, "k_prime": 7, "g": 6, "dk": 28},
    {"d": 4, "k_prime": 9, "g": 8, "dk": 36},
]

# Pre-minted RUN ids (checked free). Stage 0/1 used e10267, e3a2f8.
TK_RUN_IDS = {
    # (g, seed) -> run_id
    (2, 20261001): "RUN-BINSTD-4a9a7e",
    (2, 20261002): "RUN-BINSTD-ebfe72",
    (2, 20261003): "RUN-BINSTD-38037e",
    (2, 20261004): "RUN-BINSTD-647377",
    (2, 20261005): "RUN-BINSTD-a0b9b3",
    (4, 20261001): "RUN-BINSTD-8eab5c",
    (4, 20261002): "RUN-BINSTD-939239",
    (4, 20261003): "RUN-BINSTD-76759a",
    (4, 20261004): "RUN-BINSTD-71cc2a",
    (4, 20261005): "RUN-BINSTD-e88197",
    (6, 20261001): "RUN-BINSTD-29db46",
    (6, 20261002): "RUN-BINSTD-f2582d",
    (6, 20261003): "RUN-BINSTD-867603",
    (6, 20261004): "RUN-BINSTD-690858",
    (6, 20261005): "RUN-BINSTD-aa2c56",
    (8, 20261001): "RUN-BINSTD-e43859",
    (8, 20261002): "RUN-BINSTD-3e4798",
    (8, 20261003): "RUN-BINSTD-fd8c4c",
    (8, 20261004): "RUN-BINSTD-1c2973",
    (8, 20261005): "RUN-BINSTD-2fc132",
}
NULL_RUN_IDS = {
    20261001: "RUN-BINSTD-3b6731",
    20261002: "RUN-BINSTD-c9b410",
    20261003: "RUN-BINSTD-3b72d9",
    20261004: "RUN-BINSTD-87b1a8",
    20261005: "RUN-BINSTD-47cc28",
}
NONTK_RUN_IDS = {
    2: "RUN-BINSTD-b34615",
    4: "RUN-BINSTD-a3c77c",
    6: "RUN-BINSTD-5618cb",
    8: "RUN-BINSTD-a17647",
}


def _cost_value(trial: dict):
    pc = trial.get("per_trial_cost") or {}
    if pc.get("status") == "instrument_ceiling":
        return None
    return pc.get("xor_word_ops")


def fit_growth_law(points):
    """Fit log2(cost) ≈ a + b*g on measured points with cost>0."""
    usable = [(g, c) for g, c in points if c is not None and c > 0]
    if len(usable) < 2:
        return {
            "form": "log2(cost) = a + b*g",
            "fitted": False,
            "reason": "fewer than 2 positive measured points",
            "points": points,
            "label": "modeled",
        }
    gs = [g for g, _ in usable]
    ys = [math.log2(c) for _, c in usable]
    n = len(gs)
    mean_g = sum(gs) / n
    mean_y = sum(ys) / n
    var_g = sum((g - mean_g) ** 2 for g in gs)
    if var_g == 0:
        return {"fitted": False, "reason": "zero variance in g", "label": "modeled"}
    b = sum((g - mean_g) * (y - mean_y) for g, y in zip(gs, ys)) / var_g
    a = mean_y - b * mean_g
    resid = [y - (a + b * g) for g, y in zip(gs, ys)]
    return {
        "form": "log2(xor_word_ops) = a + b*g",
        "a": a,
        "b": b,
        "fitted": True,
        "n_points": n,
        "g_values": gs,
        "rmse_log2": math.sqrt(sum(r * r for r in resid) / n),
        "optimistic_assumptions": [
            "Truncated Macaulay instrument understates true Groebner degree/cost.",
            "Extrapolation g<=8 -> g=22 assumes smooth cost law (likely false near phase transitions).",
            "Random dense GE proxy is arity-driven, not T_k-polynomial-specific.",
        ],
        "label": "modeled",
        "measured_input_label": "measured xor_word_ops medians",
    }


def run_stage2() -> dict:
    # Gate: Stage 0 and Stage 1 dirs must exist
    s0 = EXP_DIR / "stage0"
    s1 = EXP_DIR / "stage1"
    if not s0.is_dir() or not s1.is_dir():
        raise SystemExit("Stage 2 refused: stage0/ or stage1/ missing")
    required0 = [
        "naive-cost-table.yaml",
        "rho-reg-table.yaml",
        "dual-rho-margins.yaml",
        "reachability-table-cell.yaml",
        "corpus-arity-ge4-recheck.yaml",
        "ecc2k130-null-note.md",
    ]
    required1 = ["gorla-massierer-extraction.yaml", "calibration-ratio.yaml"]
    for name in required0:
        if not (s0 / name).exists():
            raise SystemExit(f"Stage 2 refused: missing stage0/{name}")
    for name in required1:
        if not (s1 / name).exists():
            raise SystemExit(f"Stage 2 refused: missing stage1/{name}")

    cert_dir = EXP_DIR / "stage2/certified-decompositions"
    cert_dir.mkdir(parents=True, exist_ok=True)

    tk_by_g = {t["g"]: [] for t in TOYS}
    run_ids = []
    logs = []

    for toy in TOYS:
        for seed in SEEDS:
            g = toy["g"]
            run_id = TK_RUN_IDS[(g, seed)]
            started = utc_now()
            t0 = time.perf_counter()
            trial = measure_tk_trial(toy["d"], toy["k_prime"], seed)
            wall = time.perf_counter() - t0
            finished = utc_now()
            term = trial.get("termination_reason", "completed")
            cert = trial.get("certificate") or {"kind": "none", "verified": None}
            if cert.get("kind") == "decomposition":
                dump_yaml(
                    cert_dir / f"{run_id}.yaml",
                    {
                        "run_id": run_id,
                        "g": g,
                        "seed": seed,
                        "certificate": cert,
                        "curve": trial.get("curve"),
                    },
                )
            valid = bool(trial.get("ok", True)) and (
                cert.get("verified") in (True, None)
            )
            if cert.get("kind") == "decomposition" and cert.get("verified") is not True:
                valid = False
            metrics = {
                "g": g,
                "d": toy["d"],
                "k_prime": toy["k_prime"],
                "per_trial_xor_word_ops": _cost_value(trial),
                "per_trial_wall_s": (trial.get("per_trial_cost") or {}).get("wall_s"),
                "termination_reason": term,
                "certificate_verified": cert.get("verified"),
                "instrument_ceiling": term == "instrument_ceiling",
            }
            stdout = json.dumps({k: trial.get(k) for k in (
                "g", "d", "k_prime", "termination_reason", "per_trial_cost",
                "factor_base_size", "macaulay_instrument", "certificate",
            )}, indent=2)
            write_run_package(
                run_id,
                stage=2,
                command=(
                    "python3 -I experiments/EXP-BINSTD-1a7892/implementation/run_stage2.py "
                    f"--tk g={g} seed={seed}"
                ),
                seed=seed,
                parameters={**toy, "construction": "Tk"},
                metrics=metrics,
                valid=valid,
                invalid_reason=None if valid else "certificate failed or trial not ok",
                termination_reason=term,
                certificate=cert,
                stdout_text=stdout + "\n",
                started_at=started,
                finished_at=finished,
                wall_seconds=wall,
                status="completed_valid" if valid and term == "completed" else (
                    "completed_valid" if term == "instrument_ceiling" else "invalid_measurement"
                ),
            )
            tk_by_g[g].append(trial)
            run_ids.append(run_id)
            logs.append(f"Tk g={g} seed={seed} term={term} cost={_cost_value(trial)}")

    # NULL control
    null_trials = []
    for seed in SEEDS:
        run_id = NULL_RUN_IDS[seed]
        started = utc_now()
        t0 = time.perf_counter()
        null = measure_null_no_subfield(seed)
        wall = time.perf_counter() - t0
        finished = utc_now()
        ok = bool(null.get("reports_no_Tk_construction"))
        write_run_package(
            run_id,
            stage=2,
            command=(
                "python3 -I experiments/EXP-BINSTD-1a7892/implementation/run_stage2.py "
                f"--null seed={seed}"
            ),
            seed=seed,
            parameters={"construction": "null_no_subfield", "field_n": 5},
            metrics={
                "null_reports_no_construction": ok,
                "Tk_construction_possible": null.get("Tk_construction_possible"),
                "Tk_finite_cost": null.get("Tk_finite_cost"),
            },
            valid=ok,
            invalid_reason=None if ok else "null reported a T_k construction",
            termination_reason=null.get("termination_reason", "completed"),
            certificate={"kind": "none", "verified": None},
            stdout_text=json.dumps(null, indent=2) + "\n",
            started_at=started,
            finished_at=finished,
            wall_seconds=wall,
            status="completed_valid" if ok else "invalid_measurement",
        )
        null_trials.append(null)
        run_ids.append(run_id)
        logs.append(f"NULL seed={seed} no_Tk={ok}")

    # non-T_k same-arity controls (1 seed per g; seed=20261001)
    nontk = {}
    for g in [2, 4, 6, 8]:
        run_id = NONTK_RUN_IDS[g]
        seed = 20261001
        started = utc_now()
        t0 = time.perf_counter()
        trial = measure_non_tk(g, seed)
        wall = time.perf_counter() - t0
        finished = utc_now()
        term = trial.get("termination_reason", "completed")
        write_run_package(
            run_id,
            stage=2,
            command=(
                "python3 -I experiments/EXP-BINSTD-1a7892/implementation/run_stage2.py "
                f"--nontk g={g}"
            ),
            seed=seed,
            parameters={"construction": "non_Tk_same_arity", "g": g},
            metrics={
                "g": g,
                "per_trial_xor_word_ops": _cost_value(trial),
                "per_trial_wall_s": (trial.get("per_trial_cost") or {}).get("wall_s"),
                "termination_reason": term,
            },
            valid=True,
            invalid_reason=None,
            termination_reason=term,
            certificate={"kind": "none", "verified": None},
            stdout_text=json.dumps(trial, indent=2) + "\n",
            started_at=started,
            finished_at=finished,
            wall_seconds=wall,
            status="completed_valid",
        )
        nontk[g] = trial
        run_ids.append(run_id)
        logs.append(f"nonTk g={g} term={term} cost={_cost_value(trial)}")

    # Aggregate cost-vs-g table
    rows = []
    med_points = []
    for toy in TOYS:
        g = toy["g"]
        costs = [_cost_value(t) for t in tk_by_g[g]]
        walls = [
            (t.get("per_trial_cost") or {}).get("wall_s")
            for t in tk_by_g[g]
        ]
        measured_costs = [c for c in costs if c is not None]
        ceiling = any(
            t.get("termination_reason") == "instrument_ceiling" for t in tk_by_g[g]
        )
        cert_rate = sum(
            1
            for t in tk_by_g[g]
            if (t.get("certificate") or {}).get("verified") is True
        ) / max(len(tk_by_g[g]), 1)
        med = statistics.median(measured_costs) if measured_costs else None
        mx = max(measured_costs) if measured_costs else None
        med_wall = statistics.median([w for w in walls if w is not None]) if any(
            w is not None for w in walls
        ) else None
        max_wall = max([w for w in walls if w is not None]) if any(
            w is not None for w in walls
        ) else None
        rows.append(
            {
                "d": toy["d"],
                "k_prime": toy["k_prime"],
                "g": g,
                "dk": toy["dk"],
                "n_seeds": len(tk_by_g[g]),
                "median_xor_word_ops": med,
                "max_xor_word_ops": mx,
                "median_wall_s": med_wall,
                "max_wall_s": max_wall,
                "certificate_pass_rate": cert_rate,
                "instrument_ceiling": ceiling,
                "cost_label": "measured" if measured_costs else "instrument_ceiling",
                "per_seed_xor_word_ops": costs,
                "run_ids": [TK_RUN_IDS[(g, s)] for s in SEEDS],
            }
        )
        med_points.append((g, med))

    dump_yaml(
        EXP_DIR / "stage2/cost-vs-g-table.yaml",
        {
            "experiment_id": "EXP-BINSTD-1a7892",
            "stage": 2,
            "metric": "per_trial_decomposition_cost_vs_g",
            "cost_proxy": (
                "Dense F2 Gaussian-elimination xor-word ops on a truncated Macaulay "
                "matrix whose shape matches the Gorla–Massierer T_n (n=g+1) variable/"
                "equation counts at a memory-feasible degree D. Forward decompositions "
                "are certificate-verified on E(F_2^4). NOT a deployed attack cost."
            ),
            "tail_check": "max reported alongside median per g",
            "rows": rows,
            "DEFINED_deployed_attack_cost_filed": False,
            "break_claim_filed": False,
        },
    )

    law = fit_growth_law(med_points)
    max_g_measured = max(
        (r["g"] for r in rows if r["median_xor_word_ops"] is not None), default=None
    )
    extrap = {
        "extrapolation_distance_to_g22": (
            None if max_g_measured is None else 22 - max_g_measured
        ),
        "max_g_measured": max_g_measured,
        "target_g": 22,
        "label": "modeled",
        "warning": (
            "Any cost extrapolated to g=22 is MODELED with stated distance; must not "
            "be filed as a deployed DEFINED cost. DO-3-shaped surviving margin would "
            "require break_adjacent_halt + review-breakthrough — not claimed here."
        ),
    }
    if law.get("fitted") and max_g_measured is not None:
        pred_log2 = law["a"] + law["b"] * 22
        extrap["modeled_log2_xor_word_ops_at_g22"] = pred_log2
        extrap["modeled_xor_word_ops_at_g22"] = 2 ** pred_log2
        extrap["modeled_not_DEFINED"] = True

    # Analytic Macaulay memory note per g
    mem_notes = []
    for toy in TOYS:
        g = toy["g"]
        t0 = tk_by_g[g][0] if tk_by_g[g] else {}
        mi = t0.get("macaulay_instrument") or {}
        mem_notes.append(
            {
                "g": g,
                "macaulay_rows": mi.get("n_rows"),
                "macaulay_cols": mi.get("n_cols"),
                "entries": mi.get("entries"),
                "full_total_degree": mi.get("full_total_degree"),
                "truncation_note": mi.get("truncation_note"),
            }
        )

    dump_yaml(
        EXP_DIR / "stage2/fitted-growth-law.yaml",
        {
            "experiment_id": "EXP-BINSTD-1a7892",
            "stage": 2,
            "fitted_growth_law": law,
            "extrapolation": extrap,
            "memory_accounting_analytic": mem_notes,
            "median_points_used": med_points,
            "DEFINED_deployed_attack_cost_filed": False,
            "break_claim_filed": False,
            "DO3_surviving_margin_claimed": False,
        },
    )

    dump_yaml(
        EXP_DIR / "stage2/controls-report.yaml",
        {
            "experiment_id": "EXP-BINSTD-1a7892",
            "stage": 2,
            "null_no_subfield": {
                "n_seeds": len(null_trials),
                "all_report_no_Tk_construction": all(
                    t.get("reports_no_Tk_construction") for t in null_trials
                ),
                "any_finite_Tk_cost": any(t.get("Tk_finite_cost") for t in null_trials),
                "pass": all(t.get("reports_no_Tk_construction") for t in null_trials)
                and not any(t.get("Tk_finite_cost") for t in null_trials),
                "run_ids": [NULL_RUN_IDS[s] for s in SEEDS],
                "field_n": 5,
                "note": null_trials[0].get("note") if null_trials else None,
            },
            "non_Tk_same_arity": {
                "by_g": {
                    str(g): {
                        "xor_word_ops": _cost_value(nontk[g]),
                        "wall_s": (nontk[g].get("per_trial_cost") or {}).get("wall_s"),
                        "termination_reason": nontk[g].get("termination_reason"),
                        "run_id": NONTK_RUN_IDS[g],
                    }
                    for g in nontk
                },
                "note": (
                    "Compare growth of non-Tk random matrices to Tk-shaped instrument; "
                    "both reported separately (measured)."
                ),
            },
            "certificate_oracle": {
                "Tk_certificate_pass_rate_by_g": {
                    str(r["g"]): r["certificate_pass_rate"] for r in rows
                },
                "require_pass_rate_1": True,
                "pass": all(r["certificate_pass_rate"] == 1.0 for r in rows),
            },
            "small_g_sanity_slice": {
                "g2_finite_measured_cost": any(
                    _cost_value(t) is not None for t in tk_by_g[2]
                ),
                "pass": any(_cost_value(t) is not None for t in tk_by_g[2]),
            },
        },
    )

    (EXP_DIR / "stage2/stage2-stdout-summary.log").write_text("\n".join(logs) + "\n")
    return {
        "run_ids": run_ids,
        "n_runs": len(run_ids),
        "git": git_state(),
        "max_g_measured": max_g_measured,
    }


if __name__ == "__main__":
    print(json.dumps(run_stage2(), indent=2))

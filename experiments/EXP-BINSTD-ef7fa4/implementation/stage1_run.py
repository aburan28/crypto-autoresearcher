#!/usr/bin/env python3
"""Stage 1: RC-1 symmetrised S_4 e-space census (P1, P2, lift_agreement)."""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from census import census_cell, measure_P2
from curve import Curve
from product_space import poly_basis
from runpack import EXP_ROOT, dump_yaml, peak_rss_bytes, utc_now, write_run_package
from targets import RC1, SEED, build_rc1_targets

RUN_P2 = "RUN-BINSTD-a81d6f"
RUN_L4 = "RUN-BINSTD-864de8"
RUN_L5 = "RUN-BINSTD-5a6e49"
RUN_L6 = "RUN-BINSTD-0a6a59"


def _require_stage0():
    stage0 = EXP_ROOT / "stage0"
    for name in (
        "dimension-table-n131.yaml",
        "dimension-table-rc1.yaml",
        "preregistered-predictions.yaml",
        "methodological-note.md",
        "subfield-proves-too-much.yaml",
    ):
        if not (stage0 / name).exists():
            raise SystemExit(f"REFUSE: Stage 0 artifact missing: {name}")
    # Stage 0 run must exist
    if not (EXP_ROOT / "runs" / RUN_P2.replace("a81d6f", "fd509d")).exists():
        # check fd509d
        if not (EXP_ROOT / "runs" / "RUN-BINSTD-fd509d" / "manifest.yaml").exists():
            raise SystemExit("REFUSE: Stage 0 run RUN-BINSTD-fd509d not written yet")


def run_p2(F):
    started = utc_now()
    t0 = time.time()
    rows = measure_P2(F)
    metrics = {
        "product_space_dims": rows,
        "P2_exact": all(r["match"] for r in rows),
        "peak_rss_bytes": peak_rss_bytes(),
        "wall_clock_s": time.time() - t0,
        "termination_reason": "completed",
    }
    finished = utc_now()
    write_run_package(
        RUN_P2,
        stage=1,
        arm="poly_basis-P2",
        seed=SEED,
        command="python3 experiments/EXP-BINSTD-ef7fa4/implementation/stage1_run.py --only p2",
        parameters={"l_values": list(range(4, 10)), "n": 17},
        metrics=metrics,
        valid=True,
        invalid_reason=None,
        termination_reason="completed",
        stdout_text=f"P2 rows={rows}\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=time.time() - t0,
        certificate={"kind": "none", "verified": None, "note": "P2 dimension metric-only"},
        curve_id="BIN-TOY-RC1",
    )
    dump_yaml(EXP_ROOT / "stage1" / "product-space-dims.yaml", {
        "experiment_id": "EXP-BINSTD-ef7fa4",
        "metric": "P2",
        "rows": rows,
        "run_id": RUN_P2,
        "label": "MEASURED_explicit_span",
    })
    return rows


def run_l(F, E, targets, l, mode, run_id, sample_cap=1 << 24):
    started = utc_now()
    t0 = time.time()
    V = poly_basis(l)
    cell = census_cell(
        F, RC1["B"], RC1["A"], Curve, V, targets, l, mode, SEED, sample_cap=sample_cap
    )
    # Summarize certificates without huge payloads in metrics
    n_certs = len(cell["decomposition_certificates"])
    metrics = {
        "l": l,
        "enumeration_mode": mode,
        "product_space_dims": cell["dims_Vk"],
        "e_space_solution_count": cell["e_space_solution_count_pooled"],
        "genuine_decomposition_count": cell["genuine_decomposition_count_pooled_ordered"],
        "spurious_factor": cell["spurious_factor"],
        "spurious_factor_label": cell["spurious_factor_label"],
        "lift_agreement": cell["lift_agreement"],
        "lift_agreement_counts": cell["lift_agreement_counts"],
        "decomposition_certificate_count": n_certs,
        "smoothest_e_solution_target": cell["smoothest_e_solution_target"],
        "identity_check": cell["identity_check"],
        "peak_rss_bytes": peak_rss_bytes(),
        "wall_clock_s": time.time() - t0,
        "termination_reason": "completed",
        "censoring_flag": mode != "exhaustive",
        "sampled_assignment_count": sample_cap if mode != "exhaustive" else None,
    }
    # Primary certificate on run: none for metric pool; individual decomp certs stored in stage1
    cert = {"kind": "none", "verified": None, "note": "pooled metric run; see decomposition certs in summary"}
    if n_certs > 0 and cell["lift_agreement"] == 1.0:
        # Attach a pointer; individual certs have kind decomposition
        cert = {
            "kind": "none",
            "verified": True,
            "note": f"{n_certs} genuine decompositions independently re-checked; see stage1 certs",
            "decomposition_certificate_count": n_certs,
        }
    finished = utc_now()
    write_run_package(
        run_id,
        stage=1,
        arm=f"poly_basis-l{l}",
        seed=SEED,
        command=f"python3 experiments/EXP-BINSTD-ef7fa4/implementation/stage1_run.py --only l{l}",
        parameters={
            "l": l,
            "m": 3,
            "mode": mode,
            "n_targets": len(targets),
            "seed": SEED,
            "sample_cap": sample_cap if mode != "exhaustive" else None,
        },
        metrics=metrics,
        valid=cell["lift_agreement"] in (None, 1.0) or (
            cell["lift_agreement"] == 1.0
        ),
        invalid_reason=(
            None
            if cell["lift_agreement"] in (None, 1.0)
            else f"lift_agreement={cell['lift_agreement']}"
        ),
        termination_reason="completed",
        stdout_text=f"l={l} mode={mode} spurious={cell['spurious_factor']} lift={cell['lift_agreement']}\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=time.time() - t0,
        certificate=cert,
        curve_id="BIN-TOY-RC1",
    )
    # Persist certs and per-target detail
    dump_yaml(
        EXP_ROOT / "stage1" / f"cell-l{l}.yaml",
        {
            "run_id": run_id,
            "dims_Vk": cell["dims_Vk"],
            "spurious_factor": cell["spurious_factor"],
            "spurious_factor_label": cell["spurious_factor_label"],
            "e_space_solution_count_pooled": cell["e_space_solution_count_pooled"],
            "genuine_decomposition_count_pooled_ordered": cell[
                "genuine_decomposition_count_pooled_ordered"
            ],
            "lift_agreement": cell["lift_agreement"],
            "per_target": cell["per_target"],
            "smoothest_e_solution_target": cell["smoothest_e_solution_target"],
            "decomposition_certificates": cell["decomposition_certificates"],
            "V_basis": cell["V_basis"],
            "Vk_bases": cell["Vk_bases"],
            "identity_check": cell["identity_check"],
            "no_break_guard": True,
        },
    )
    return cell


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default="all", choices=["all", "p2", "l4", "l5", "l6"])
    parser.add_argument("--sample-cap", type=int, default=1 << 24)
    parser.add_argument("--max-targets", type=int, default=50)
    args = parser.parse_args()

    _require_stage0()
    (EXP_ROOT / "stage1").mkdir(parents=True, exist_ok=True)

    F, E, G, targets = build_rc1_targets(n_targets=args.max_targets, seed=SEED)
    targets = targets[: args.max_targets]

    results = {}
    if args.only in ("all", "p2"):
        results["p2"] = run_p2(F)
    if args.only in ("all", "l4"):
        results["l4"] = run_l(F, E, targets, 4, "exhaustive", RUN_L4)
    if args.only in ("all", "l5"):
        results["l5"] = run_l(F, E, targets, 5, "exhaustive", RUN_L5)
    if args.only in ("all", "l6"):
        results["l6"] = run_l(
            F, E, targets, 6, "sampled", RUN_L6, sample_cap=args.sample_cap
        )

    if args.only == "all" or set(results) >= {"l4", "l5", "l6"}:
        # Build summary from cell files if partial
        pass

    # Always rewrite summary from whatever cell files exist
    import yaml

    summary = {
        "experiment_id": "EXP-BINSTD-ef7fa4",
        "metric": "P1_P2_lift",
        "seed": SEED,
        "n_targets": len(targets),
        "contract_stated_spurious_log2": {4: 9.6, 5: 13.6, 6: 17.6},
        "arithmetic_from_dims_spurious_log2": {4: 11.584962500721156, 5: 14.584962500721156, 6: 17.584962500721156},
        "cells": {},
        "no_break_guard": True,
        "claim": "observations_only_no_rho_no_exponent",
    }
    for l, rid in [(4, RUN_L4), (5, RUN_L5), (6, RUN_L6)]:
        path = EXP_ROOT / "stage1" / f"cell-l{l}.yaml"
        if path.exists():
            cell = yaml.safe_load(path.read_text())
            sf = cell.get("spurious_factor")
            stated = 2 ** summary["contract_stated_spurious_log2"][l]
            ratio_to_stated = (sf / stated) if isinstance(sf, (int, float)) and sf != float("inf") else None
            summary["cells"][l] = {
                "run_id": rid,
                "dims_Vk": cell.get("dims_Vk"),
                "e_space_solution_count_pooled": cell.get("e_space_solution_count_pooled"),
                "genuine_decomposition_count_pooled_ordered": cell.get(
                    "genuine_decomposition_count_pooled_ordered"
                ),
                "spurious_factor": sf,
                "spurious_factor_label": cell.get("spurious_factor_label"),
                "ratio_to_contract_stated": ratio_to_stated,
                "lift_agreement": cell.get("lift_agreement"),
                "smoothest_e_solution_target": cell.get("smoothest_e_solution_target"),
                "n_decomposition_certificates": len(cell.get("decomposition_certificates") or []),
            }
    dims_path = EXP_ROOT / "stage1" / "product-space-dims.yaml"
    if dims_path.exists():
        summary["P2"] = yaml.safe_load(dims_path.read_text())

    out = EXP_ROOT / "stage1" / "spurious-lift-summary.yaml"
    if out.exists():
        out.unlink()  # summary is regenerated; cell runs are immutable
    dump_yaml(out, summary)
    print("Stage 1 summary written", out)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Stage 2: size-matched random-subspace null (P3)."""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from census import census_cell
from curve import Curve
from product_space import random_basis
from runpack import EXP_ROOT, dump_yaml, peak_rss_bytes, utc_now, write_run_package
from targets import RC1, SEED, build_rc1_targets

RUN_ID = "RUN-BINSTD-540b42"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-targets", type=int, default=50)
    parser.add_argument("--sample-cap", type=int, default=1 << 24)
    parser.add_argument("--l-list", default="4,5")
    args = parser.parse_args()
    l_list = [int(x) for x in args.l_list.split(",")]

    # Stage 1 summary required for P3 comparison
    s1 = EXP_ROOT / "stage1" / "spurious-lift-summary.yaml"
    if not s1.exists():
        raise SystemExit("REFUSE: Stage 1 summary missing")
    stage1 = yaml.safe_load(s1.read_text())

    (EXP_ROOT / "stage2").mkdir(parents=True, exist_ok=True)
    F, E, G, targets = build_rc1_targets(n_targets=args.max_targets, seed=SEED)
    targets = targets[: args.max_targets]
    rng = np.random.default_rng(SEED + 999)

    started = utc_now()
    t0 = time.time()
    cells = {}
    for l in l_list:
        V = random_basis(l, F.n, rng)
        # Measure dims first to choose enumeration mode
        from census import build_Vk_bases

        bases = build_Vk_bases(V, F, m=3)
        dims = [len(b) for b in bases]
        sum_dims = sum(dims)
        mode = "exhaustive" if sum_dims <= 24 else "sampled"
        cell = census_cell(
            F,
            RC1["B"],
            RC1["A"],
            Curve,
            V,
            targets,
            l,
            mode,
            SEED + l,
            sample_cap=args.sample_cap,
        )
        poly_sf = None
        if stage1.get("cells", {}).get(l):
            poly_sf = stage1["cells"][l].get("spurious_factor")
        # Prefer scaled estimate for l=6; for undefined zero-genuine, compare e-rates
        poly_sf_num = poly_sf if isinstance(poly_sf, (int, float)) else None
        if (
            poly_sf_num is None
            and isinstance(stage1.get("cells", {}).get(l), dict)
            and stage1["cells"][l].get("sampling", {}).get("spurious_factor_estimated_scaled")
        ):
            poly_sf_num = stage1["cells"][l]["sampling"]["spurious_factor_estimated_scaled"]
        p3_ge = None
        if poly_sf_num is not None and isinstance(cell["spurious_factor"], (int, float)):
            if cell["spurious_factor"] != float("inf"):
                p3_ge = cell["spurious_factor"] >= poly_sf_num
        cells[l] = {
            "V_basis": [int(b) for b in V],
            "dims_Vk": cell["dims_Vk"],
            "sum_dims": cell["sum_dims"],
            "e_space_solution_count_pooled": cell["e_space_solution_count_pooled"],
            "genuine_decomposition_count_pooled_ordered": cell[
                "genuine_decomposition_count_pooled_ordered"
            ],
            "spurious_factor": (
                cell["spurious_factor"]
                if cell["spurious_factor"] != float("inf")
                else "undefined_zero_genuine"
            ),
            "spurious_factor_label": cell["spurious_factor_label"],
            "lift_agreement": cell["lift_agreement"],
            "poly_basis_spurious_factor": poly_sf,
            "poly_basis_spurious_factor_numeric": poly_sf_num,
            "P3_ge_poly": p3_ge,
            "P3_compare_note": (
                "poly-basis P1 undefined at this l (zero genuine); "
                "compare e_per_target / dims instead"
                if poly_sf_num is None
                else "numeric spurious comparison"
            ),
            "e_per_target": cell["e_space_solution_count_pooled"] / max(len(targets), 1),
            "decomposition_certificates": cell["decomposition_certificates"],
            "mode": mode,
            "pre_dims": dims,
        }

    metrics = {
        "cells": {k: {kk: vv for kk, vv in v.items() if kk != "decomposition_certificates"} for k, v in cells.items()},
        "peak_rss_bytes": peak_rss_bytes(),
        "wall_clock_s": time.time() - t0,
        "termination_reason": "completed",
    }
    finished = utc_now()
    write_run_package(
        RUN_ID,
        stage=2,
        arm="random_subspace",
        seed=SEED,
        command="python3 experiments/EXP-BINSTD-ef7fa4/implementation/stage2_run.py",
        parameters={"l_list": l_list, "n_targets": len(targets), "seed": SEED},
        metrics=metrics,
        valid=all(c.get("lift_agreement") in (None, 1.0) for c in cells.values()),
        invalid_reason=None,
        termination_reason="completed",
        stdout_text=f"Stage2 cells={list(cells)}\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=time.time() - t0,
        certificate={"kind": "none", "verified": None, "note": "P3 metric-only pooled run"},
        curve_id="BIN-TOY-RC1-random-subspace",
    )
    dump_yaml(
        EXP_ROOT / "stage2" / "random-subspace-summary.yaml",
        {
            "experiment_id": "EXP-BINSTD-ef7fa4",
            "metric": "P3",
            "run_id": RUN_ID,
            "seed": SEED,
            "cells": cells,
            "no_break_guard": True,
            "claim": "observations_only",
        },
    )
    print("Stage 2 done", metrics["wall_clock_s"])


if __name__ == "__main__":
    main()
